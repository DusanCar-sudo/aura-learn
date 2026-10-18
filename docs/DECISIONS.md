# Decision log

One entry per decision. Newest first.

## 2026-10-18 — Project direction

**Decision:** Pursue continual on-the-job learning for a personal coding agent instead of training a frontier model.
**Why:** Frontier pretraining costs are out of reach; continual learning is an open research frontier where an applied, agent-specific result on small models is achievable solo and fundable.
**Consequences:** Small base models (3B–7B), daily LoRA consolidation, test-time fast weights; success measured on personal-repo learning curves.

## 2026-10-18 — Exclude direct weight editing

**Decision:** ROME/MEMIT-style editing is not a primary method.
**Why:** Published results show collapse after a few hundred sequential edits.

## Open

- D1 name · D2 base model · D3 compute budget · D4 visibility · D5 license — see PLAN.md.
