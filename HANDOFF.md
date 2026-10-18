# HANDOFF — 2026-10-18

From a Claude.ai planning session to Claude Code. Read `CLAUDE.md` for the rules, then this file.

## Where we are
- Repo scaffolded with 2 commits on `main`. It is **not yet pushed** to GitHub; the target is `DusanCar-sudo/aura-learn`.
- Working code: `src/aura_learn/episodes.py` and `cli.py`. `aura-learn export` turns aura-code episodes into correction JSONL, with `--stats` and `--exclude-project`. 5 tests pass.
- Docs written:
  - `docs/PLAN.md`: phases 0–7 plus the paper track
  - `docs/ARCHITECTURE.md`
  - `docs/RESEARCH.md`
  - `docs/DECISIONS.md`
  - `docs/paper/OUTLINE.md`
- `configs/base.yaml` holds starting values; anything marked TUNE is not a decision.

## Why this direction
The owner wanted to raise money for a frontier model. That was rejected as unrealistic. The fundable, achievable version is continual learning for a *personal* agent, where the free teacher signal is Archimedes escalations. The plan is to publish a position paper early, then a results paper around week 13, and use both in investor and grant applications.

## Open decisions (ask the owner; don't assume)
| ID | Question | Recommendation |
|---|---|---|
| D1 | Project name | keep `aura-learn` |
| D2 | Base model | Qwen2.5-Coder-7B-Instruct, with 0.5B/1.5B for development |
| D3 | Compute budget | $0 to start (Kaggle) |
| D4 | Public or private repo | owner's call |
| D5 | License | MIT (matches aura-code) or Apache-2.0 |

## Next tasks, in order

### T1 — Push and verify on the owner's machine
- Help him create the GitHub repo and push.
- Run `pytest` and `aura-learn export --stats` against his real `~/.aura/episodes`.
- Record the stats output (episode count, escalation rate per category, usable corrections). The position paper uses these numbers.

### T2 — Close the loop in aura-code (Phase 1)
This happens in the aura-code repo, not here.
1. Make sure `archimedesOutput` and `largeModelOutput` are stored **untruncated** in episodes. Truncation belongs only at export.
2. Add optional fields to `Episode` in `src/archimedes/types.ts`: `filesTouched?: string[]`, `diff?: string`, `testResult?: 'pass' | 'fail' | 'none'`, `reviewerReason?: string`. Populate them in `alternator.ts`.
3. Add a per-project learning opt-out flag in project config.
4. Keep `:mine` as the manual default and add an optional auto-export.
5. Update `src/archimedes/types.ts` and `aura_learn/episodes.py` together, so the contract stays in sync, and add tests on both sides.

### T3 — Dev model loop at 0.5B (Phase 0/3 groundwork)
- Create `src/aura_learn/train/sft.py`: QLoRA SFT on the correction JSONL with peft and trl. Use lazy imports, and read `configs/base.yaml` with a `--model` override.
- Smoke test on CPU with Qwen2.5-Coder-0.5B, 10 steps, using fixture data.
- Write a Kaggle notebook `notebooks/kaggle_sft_7b.ipynb` that runs the same module on a T4 with the 7B model.

### T4 — Eval harness skeleton (Phase 2)
- Personal benchmark: turn past commits from the owner's repos into "reproduce this change" tasks, judged by each repo's tests, with a time-split date in config.
- Forgetting benchmark: a fixed HumanEval+/MBPP+ subset.
- `aura-learn eval --adapter <id>` appends a row to `experiments/results.jsonl`.

### T5 — Position paper literature pass (parallel track)
- Follow `docs/paper/OUTLINE.md`, section 3 (cross-examination).
- Verify every citation in `docs/RESEARCH.md` against the source before anything goes into the paper. Find the strongest objection ("RAG and long context already solve this") and steelman it.
- Publishing targets: Zenodo (DOI) and arXiv, linked to the owner's ORCID.

## Parallel non-code actions for the owner
- Apply to TPU Research Cloud (Express interest form), the Modal academic grant, AWS Activate Founders, and Google for Startups Start tier.
- Set up an ORCID iD, link Zenodo to ORCID and GitHub, and find an arXiv endorser for cs.LG.

## Known facts worth keeping
- Path B correction mining already exists in aura-code, so the loop is half-closed. The remaining gaps are truncation, the manual-only trigger, no consolidation and no eval.
- aura-code's old tiered benchmark is stale (it references pre-rename RubyAlternator symbols). It will be replaced by the T4 harness.
- In-Place TTT (arXiv:2604.06169) has open code and is the Phase 5 base method.
