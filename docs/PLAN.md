# aura-learn — Project Plan

**Goal:** an agent whose model weights keep learning from daily work — no classical retraining cycle — and measurably gets better at *your* code without forgetting what it already knew.

**Thesis in one line:** Archimedes escalations are a free, high-quality teacher signal. Turn them into weight updates on a small local model, safely, every day.

**Owner:** Dušan Milosavljević · **Start:** after plan review · **Horizon:** ~13 weeks to a publishable result

---

## Success criteria (what "it works" means)

The whole project is judged by one chart: **task success on held-out tasks from your own repos, over time.**

| Metric | Target by week 13 |
|---|---|
| Personal-repo task success (adapted vs frozen base) | **+15 points absolute** or better |
| Escalation rate (small model → large model) | **−30% relative** |
| Forgetting: general coding benchmark score | **no more than −2 points** vs base |
| Update cost | nightly consolidation **< 1 GPU-hour** on a 7B model |
| Safety | **0** regressions shipped — every bad adapter caught by the guard and rolled back |

If the curve goes up and forgetting stays flat, that is the paper and the pitch.

---

## Phase 0 — Foundations (week 1)

**Steps**
1. Create the `aura-learn` repo (this scaffold), push to GitHub under DusanCar-sudo.
2. Python env: Python 3.11, PyTorch, transformers, peft, trl, datasets, vllm or llama.cpp for serving.
3. Freeze the **data contract** with aura-code: the episode JSON schema (`src/archimedes/types.ts → Episode`) is the interface. aura-learn reads `~/.aura/episodes/` read-only.
4. Compute — zero-cost ladder (local machine can't run 7B; the GCP free trial blocks GPUs):
   - **Develop at 0.5B–1.5B** (Qwen2.5-Coder-0.5B/1.5B) on CPU — every pipeline piece (export, replay, guard, eval) is proven small first.
   - **Train 7B on Kaggle** — free T4 GPUs, 12 h sessions, ~30 h/week. 7B QLoRA fits a 16 GB T4; nightly consolidation is well under the weekly quota. Colab free T4 as backup.
   - **Apply now:** TPU Research Cloud (free TPUs, expects published research — matches the paper track), Modal academic grant (up to $10k), AWS Activate Founders (up to $5k, self-serve), Google for Startups Start tier (up to $2k).
   - Paid GCP only after credits land.
5. Experiment tracking: plain JSONL run logs + one results table in `experiments/` (no SaaS dependency).

**Exit:** `aura-learn export` turns real episodes into a training JSONL. ✅ already implemented in this scaffold.

---

## Phase 1 — Close the loop in aura-code (weeks 1–2)

Correction pairs already exist (`src/mining/corrections.ts`, Path B, behind `:mine`). What's missing:

**Steps**
1. **Full-fidelity capture.** `alternator.ts` saves episodes; make sure `archimedesOutput` and `largeModelOutput` are stored untruncated. Truncate only at export time (aura-learn decides).
2. **Richer triplets.** Add to `Episode`: files touched, the diff applied, test result (pass/fail/none), reviewer verdict reason. These become reward signal and eval labels.
3. **Quality filter.** Only escalations where the large-model answer was *accepted* (reviewer approved, or tests passed) become training rows. Rejected ones become eval negatives.
4. **Auto-export.** Optional nightly export of new episodes; the manual `:mine` gate stays as the default.
5. **Privacy switch.** A per-project flag to exclude a repo from learning entirely.

**Exit:** 2 weeks of normal aura-code use produces ≥ 200 accepted correction triplets.

---

## Phase 2 — Evaluation harness (weeks 2–4)

Nothing gets trained before this exists. The harness is the product.

**Steps**
1. **Personal benchmark.** Build tasks from your own repos (aura-code, aura-droid, aura-pulse, jewel3): real past commits → "reproduce this change" tasks with the repo's tests as the judge. Time-split: train on tasks before date T, test on tasks after T.
2. **Forgetting benchmark.** A fixed general coding set (e.g. a HumanEval+/MBPP+ subset) run after every update.
3. **Agent metrics.** Escalation rate, tokens, latency, cost per task — read from aura-code's cost log.
4. **Replace the rotted tiered benchmark** in aura-code with this harness (it references pre-rename symbols).
5. One command: `aura-learn eval --adapter <id>` → one row in `experiments/results.jsonl`.

**Exit:** frozen base model scored on both benchmarks, 3 repeated runs, variance known.

---

## Phase 3 — Baselines (weeks 4–6)

Every new idea must beat these honestly.

| Baseline | What it is |
|---|---|
| **B0 Frozen** | Qwen2.5-Coder-7B-Instruct, no changes |
| **B1 RAG** | Frozen + retrieval over past episodes and repo |
| **B2 Batch LoRA** | One QLoRA SFT run on all correction pairs (your existing Vertex pipeline) |

**Exit:** a results table B0/B1/B2 on personal + forgetting benchmarks.

---

## Phase 4 — Sleep consolidation (weeks 6–9)

The core system. Daily, small, safe weight updates.

**Steps**
1. **Replay buffer.** Each night: new correction pairs + a sampled mix of older pairs + general "anchor" data. Starting ratio to tune: 50 / 30 / 20.
2. **Per-user LoRA adapter**, updated incrementally (continue from yesterday's adapter, low learning rate) — not retrained from scratch.
3. **Optional self-distillation term** against the base model on anchor data to limit drift.
4. **Guard.** After each update run both benchmarks. If personal score doesn't improve or forgetting exceeds threshold → reject, keep yesterday's adapter.
5. **Adapter registry.** Versioned adapters with their scores; rollback is one command.
6. **Simulated time.** Replay your historical episodes day by day to get a 30–60 day learning curve without waiting 60 real days.

**Exit:** learning curve over simulated days beats B2 with forgetting inside the limit.

---

## Phase 5 — Fast weights / in-session learning (weeks 8–12)

Adapt *during* a session, not just overnight.

**Steps**
1. Reproduce **In-Place TTT** (ByteDance, ICLR 2026, open code) on Qwen2.5-Coder-7B. Match their reported numbers on one of their tasks first.
2. Apply it to agent sessions: fast weights update from the session's own context (files read, errors seen).
3. Fast weights reset at session end; anything worth keeping goes to the replay buffer → consolidated at night. (Fast = short-term memory, LoRA = long-term memory.)
4. Measure: within-session success on long tasks vs B0 and vs Phase 4 alone.

**Exit:** in-session adaptation shows a measurable gain on long multi-step tasks, or a documented negative result (also publishable).

---

## Phase 6 — Integrate into aura-code (weeks 12–13)

**Steps**
1. Serving: base model + current adapter via llama.cpp (local, quantized) or vLLM (remote) with LoRA hot-swap.
2. Archimedes loads the latest **guard-passed** adapter at startup; `aura doctor` shows adapter version and its scores.
3. `aura learn status | rollback | pause` commands.

**Exit:** you use aura-code daily on the adapting model for one week, no regressions shipped.

---

## Phase 7 — Publish & pitch (week 13+)

1. Technical report: method, learning curve, forgetting, ablations (correction vs mined data, replay ratios, TTT on/off). arXiv + GitHub.
2. Submit to a relevant workshop (e.g. test-time / continual learning agents).
3. Investor memo + 2-minute demo video: "same model, day 1 vs day 30, on my repo."
4. Apply to compute-credit programs (Google, AWS) and accelerators with the result in hand.

---

## Parallel track — Papers (see docs/paper/OUTLINE.md)

| When | Paper | Needs |
|---|---|---|
| Weeks 1–4 | **Position paper:** *Escalation as Supervision* — thesis, cross-examination of prior work, framework, evaluation protocol | Literature deep-dive + aura-code system description + episode stats |
| Week 13 | **Results paper** — learning curves, forgetting, ablations | Phases 2–5 |

Published on Zenodo (DOI) and arXiv, linked to ORCID.

---

## Risks and how we handle them

| Risk | Mitigation |
|---|---|
| Too little data from one user | Simulated replay of history; mine all own repos' commit history as extra tasks |
| Catastrophic forgetting | Replay + anchors + guard + rollback; direct weight editing (ROME/MEMIT) is excluded — it collapses at scale |
| Benchmark leakage (testing on what we trained on) | Strict time-split; tasks after date T are never trained on |
| Compute cost | 7B QLoRA nightly fits one spot GPU; budget cap set in Decision D3 |
| Big labs publish the same thing | Our edge is applied: agent escalation signal + personal repos + working product. Publish early. |
| Result is negative | Still publishable and still a credible research track record |

---

## Decisions needed from you before we start

- **D1 Name:** `aura-learn` (working name) — keep or rename?
- **D2 Base model:** Qwen2.5-Coder-7B-Instruct (recommended: TTT + LoRA tooling is mature) vs Granite 4.1 3B (cheaper, weaker).
- **D3 Compute budget:** $0 to start (Kaggle + small models); set a paid cap only once grant credits arrive or Kaggle quota becomes the bottleneck.
- **D4 Visibility:** public from day 1 (credibility, community) or private until Phase 7 (protect the idea)?
- **D5 License:** MIT like aura-code, or Apache-2.0 (patent grant, preferred by companies)?
