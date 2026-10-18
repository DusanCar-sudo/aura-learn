# Research notes

Reading list and what we take from each. Checked October 2026.

## Use

- **In-Place Test-Time Training** — Feng et al., ByteDance Seed / PKU, ICLR 2026 oral. arXiv:2604.06169. Uses the final MLP projection as fast weights; drop-in, open code. → Phase 5 base method.
- **Agentic Test-Time Training (aTTT)** — arXiv:2607.03441, Jul 2026. Continuous TTT across multi-turn agent episodes. → Phase 5 design for agent sessions.
- **Learning to Discover at Test Time (TTT-Discover)** — Yuksekgonul et al., arXiv:2601.16175. Test-time RL, a few hundred dollars per problem via Tinker. → Proof that experiments are affordable.
- **When Does Continual Learning Require Learning** — arXiv:2607.07847. Mechanism-agnostic CL evaluation; self-distillation (SDFT) accumulated knowledge stably. → Phase 2 eval design, Phase 4 distillation term.
- **Just-In-Time RL (JitRL)** — arXiv:2601.18510. Test-time policy improvement without gradients (logit adjustment). → Cheap baseline worth comparing against.

## Avoid as a primary method

- **ROME / MEMIT direct editing** — Gupta et al., arXiv:2401.07453. Gradual then catastrophic forgetting after a few hundred sequential edits. Not viable for daily learning.
- **WikiBigEdit** — arXiv:2503.05683. Local editing methods drop to near zero within ~250 updates; LoRA-FT and RAG hold up better.

## Watch

- **MEMOIR** (NeurIPS 2025) — sparse residual memory for lifelong editing with minimal overwrite.
- **NeurIPS 2026 Workshop: Test-Time Continual Learning Agents (TTCL)** — target venue for Phase 7.
