# CLAUDE.md — aura-learn

Read `HANDOFF.md` first. It holds the current state and the next tasks. `docs/PLAN.md` is the source of truth for scope.

## What this is
Continual on-the-job learning for aura-code. Archimedes (the small model) escalates to a large model when it fails. Those escalations are turned into safe daily weight updates (LoRA consolidation each night, fast weights during a session), so the agent improves on the owner's own repos without forgetting.

## Owner and working style
- Dušan (Dule) Milosavljević, solo developer.
- Keep responses concise and skip long explanations unless asked.
- Always deliver **complete files**, never snippets or partial diffs.
- He learns by seeing, so show worked demonstrations: real commands and real output.
- Be candid. Flag bad ideas plainly.

## Hard rules
1. Never modify the base model in place.
2. No adapter reaches aura-code without passing the guard (personal and forgetting benchmarks).
3. Strict time-split: no task dated after the split date is ever trained on.
4. Read-only access to `~/.aura/episodes/`. Never write there.
5. Projects listed as excluded produce zero training rows.
6. No ROME/MEMIT-style direct weight editing as a primary method (it collapses at scale; see `docs/RESEARCH.md`).

## Compute reality
- The owner's machine has an AMD 680M iGPU. It **cannot run 7B models** and was unstable for training. Treat it as CPU-only.
- Develop and test every pipeline piece at **Qwen2.5-Coder-0.5B/1.5B on CPU**.
- 7B training runs on **Kaggle** (free T4, 16 GB, 12 h sessions, about 30 h/week). Write training code so it runs unchanged as a Kaggle notebook.
- The GCP free trial does **not** allow GPUs. Don't plan around it.

## Commands
```bash
pip install -e ".[dev]"        # core + pytest (no ML deps)
pip install -e ".[dev,train]"  # + torch/transformers/peft/trl
pytest
aura-learn export --stats
aura-learn export --out data/corrections.jsonl
```

## Conventions
- Python 3.11+, stdlib-first in core (`episodes.py`, `cli.py` have zero dependencies). ML code goes under `src/aura_learn/train/` and imports heavy libraries lazily.
- Every new module gets tests in `tests/` with fixture data. Never use real episodes in tests.
- Each experiment run appends one line to `experiments/results.jsonl` (format in `experiments/README.md`).
- Log decisions in `docs/DECISIONS.md`, newest first.
- End commit messages with a `Co-Authored-By` line when Claude wrote the change.

## Related repo
aura-code: https://github.com/DusanCar-sudo/aura-code (TypeScript). Interface files:
- `src/archimedes/types.ts`: the `Episode` type, which is the data contract
- `src/archimedes/episode-capture.ts`: the episode store at `~/.aura/episodes/{projectHash}/`
- `src/archimedes/alternator.ts` (~line 827): where episodes are saved
- `src/mining/corrections.ts`: existing Path B correction pairs (manual `:mine`, truncates outputs to 1200/2000 chars)
- `src/mining/extract.ts`, `refine.ts`: Path A clustered "mined" lessons
