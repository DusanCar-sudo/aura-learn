# Paper track

ORCID is the author identifier, not a venue. Publish on **Zenodo** (instant DOI) and **arXiv** (cs.LG / cs.SE; first-time submitters need an endorsement), then add both to the ORCID record.

---

## Paper 1 — Position paper (target: 4 weeks, Zenodo DOI + arXiv)

**Working title:** *Escalation as Supervision: Continual On-the-Job Learning for Personal Coding Agents*

**Claim:** A deployed agent that routes tasks small-model-first already produces a stream of free, verified corrections every time it escalates. That stream is enough to drive safe, daily weight updates, with no separate training phase. The agent becomes specific to one user instead of generally good.

### Sections
1. **Introduction.** Deployed models are frozen after training. Personal agents need to learn the user's code and habits. The cost argument: escalations get rarer over time.
2. **Background.** Test-time training (In-Place TTT, aTTT, TTT-Discover); knowledge editing and why it collapses (ROME/MEMIT at scale); continual learning and forgetting; retrieval as a non-parametric alternative; gradient-free adaptation (JitRL).
3. **Cross-examination.** For each line of work: what it assumes, where it breaks for a personal agent, and what it leaves unanswered. Steelman the strongest objection: "RAG and longer context already solve this."
4. **The escalation-supervision framework.** Router, triplet capture, quality filter, replay buffer, consolidation, guard and rollback, plus a two-speed memory (fast weights in-session, adapter overnight).
5. **Evaluation protocol.** Time-split personal benchmark, forgetting benchmark, escalation-rate curve, simulated-day replay. Proposed as a reusable protocol for others.
6. **Systems view.** Cross-domain parallels from the author's background: Lean/PDCA as the update loop (plan → train → check → act/rollback), 5S as data hygiene, sleep consolidation as replay. Each parallel is used only where it changes a design decision.
7. **Risks and open questions.** Privacy, data poisoning, single-user data scarcity, evaluation leakage, drift in style versus correctness.
8. **Conclusion and roadmap.** Points to Paper 2.

### Evidence we can include without new experiments
- The aura-code system description: Archimedes routing, the episode schema, and the existing Path B correction mining.
- Descriptive statistics from real episodes: escalation rate per task category and triplet counts, via `aura-learn export --stats`.

---

## Paper 2 — Results paper (target: week 13)

**Contents:** B0/B1/B2 baselines vs sleep consolidation vs consolidation plus fast weights. Learning curves over simulated days, forgetting, ablations (correction vs mined rows, replay ratios), cost.

**Venue:** the NeurIPS 2026 TTCL workshop if its deadline is still open; otherwise the next continual-learning or agents workshop. Always arXiv as well.

---

## Author setup checklist
- [ ] ORCID iD created or confirmed; affiliation set to "Independent researcher, Lean Progress IQ"
- [ ] Zenodo account linked to ORCID and GitHub, so GitHub releases get DOIs automatically
- [ ] arXiv account plus an endorser for cs.LG
- [ ] LaTeX template (arXiv-compatible) in `docs/paper/`
