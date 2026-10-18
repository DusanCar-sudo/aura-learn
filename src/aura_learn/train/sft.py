"""QLoRA SFT on correction JSONL — Phase 3 groundwork (HANDOFF task T3).

Design constraints (see configs/base.yaml and docs/PLAN.md):
- Never modify the base model in place: output is a PEFT adapter directory.
- Heavy libraries are imported lazily; importing this module without the
  ``train`` extra installed must not fail.
- Same code runs on CPU (0.5B smoke test) and on a Kaggle T4 (7B) — the
  only difference is the ``--model`` flag. 4-bit quantization is enabled
  only when CUDA is present; CPU runs plain LoRA (bitsandbytes needs GPU).
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

DEFAULT_MODEL = "Qwen/Qwen2.5-Coder-7B-Instruct"


def load_config(path: Path) -> dict:
    import yaml

    with open(path, encoding="utf-8") as f:
        return yaml.safe_load(f) or {}


def build_dataset(data_path: Path) -> list[dict]:
    """Load the correction JSONL into prompt/completion rows."""
    rows = []
    with open(data_path, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            row = json.loads(line)
            prompt = row["instruction"]
            if row.get("input"):
                prompt += f"\n\n{row['input']}"
            rows.append({"prompt": prompt, "completion": row["output"]})
    if not rows:
        raise SystemExit(f"no training rows in {data_path}")
    return rows


def run_sft(
    model_name: str,
    data_path: Path,
    output_dir: Path,
    max_steps: int,
    learning_rate: float,
    lora_r: int,
    lora_alpha: int,
    batch_size: int = 1,
) -> Path:
    """Train one LoRA adapter. Returns the adapter directory (never the base)."""
    import torch
    from datasets import Dataset
    from peft import LoraConfig
    from transformers import AutoModelForCausalLM, AutoTokenizer
    from trl import SFTConfig, SFTTrainer

    use_qlora = torch.cuda.is_available()
    kwargs: dict = {}
    if use_qlora:
        from transformers import BitsAndBytesConfig

        kwargs["quantization_config"] = BitsAndBytesConfig(
            load_in_4bit=True, bnb_4bit_compute_dtype=torch.bfloat16, bnb_4bit_quant_type="nf4",
        )
        kwargs["dtype"] = torch.bfloat16
    else:
        kwargs["dtype"] = torch.float32

    tokenizer = AutoTokenizer.from_pretrained(model_name)
    if tokenizer.pad_token is None:
        tokenizer.pad_token = tokenizer.eos_token
    model = AutoModelForCausalLM.from_pretrained(model_name, **kwargs)
    model.config.use_cache = False

    peft_config = LoraConfig(
        r=lora_r,
        lora_alpha=lora_alpha,
        lora_dropout=0.05,
        task_type="CAUSAL_LM",
        target_modules=["q_proj", "k_proj", "v_proj", "o_proj"],
    )

    dataset = Dataset.from_list(build_dataset(data_path))
    config = SFTConfig(
        output_dir=str(output_dir),
        max_steps=max_steps,
        learning_rate=learning_rate,
        per_device_train_batch_size=batch_size,
        gradient_accumulation_steps=4,
        logging_steps=1,
        save_strategy="no",
        report_to=[],
        max_length=2048,
        packing=False,
        completion_only_loss=True,
        bf16=use_qlora,  # bf16 needs CUDA/TPU; CPU smoke runs must not set it
    )
    trainer = SFTTrainer(
        model=model,
        args=config,
        train_dataset=dataset,
        processing_class=tokenizer,
        peft_config=peft_config,
    )
    trainer.train()
    trainer.save_model(str(output_dir))
    return output_dir


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="aura-learn-train")
    parser.add_argument("--model", default=DEFAULT_MODEL, help="base model id (HF hub or local path)")
    parser.add_argument("--config", default="configs/base.yaml")
    parser.add_argument("--data", required=True, help="correction JSONL from `aura-learn export`")
    parser.add_argument("--out", default="experiments/adapter", help="adapter output directory")
    parser.add_argument("--steps", type=int, default=None, help="override max_steps_per_night")
    parser.add_argument("--lr", type=float, default=None, help="override learning rate")
    args = parser.parse_args(argv)

    cfg = load_config(Path(args.config))
    out = run_sft(
        model_name=args.model,
        data_path=Path(args.data),
        output_dir=Path(args.out),
        max_steps=args.steps if args.steps is not None else int(cfg.get("lora", {}).get("max_steps_per_night", 300)),
        learning_rate=args.lr if args.lr is not None else float(cfg.get("lora", {}).get("learning_rate", 5e-5)),
        lora_r=int(cfg.get("lora", {}).get("r", 16)),
        lora_alpha=int(cfg.get("lora", {}).get("alpha", 32)),
    )
    print(f"adapter saved to {out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
