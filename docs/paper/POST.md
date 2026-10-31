# Public post — aura-learn / "Escalation as Supervision"

Three versions: LinkedIn (main), X/Twitter (short), Hacker News / Reddit (technical).

---

## LinkedIn (main post)

Every AI assistant you use is frozen. It helps you all day, every day — and learns nothing from it.

That never sat right with me. A human assistant who worked with you for a year would know your codebase, your naming habits, your preferences, the mistakes you already corrected twice. Current AI knows none of it tomorrow. Same mistakes, every session, forever.

So we're building something new with aura-learn: a model that trains itself **while it works**. No retraining cycle, no data collection phase, no fine-tuning weekends. The work IS the training.

The idea came out of running a two-model agent every day. The small local model handles most tasks. When it fails, the task escalates to the big model, which fixes it. One day the obvious clicked: every escalation is a free, verified training example. The task, the failed attempt, the accepted fix. A teacher signal that already exists inside the normal workflow — we were throwing it away.

The loop looks like this:

1. During the day, the agent works. Successes and escalation fixes are logged automatically.
2. At night, it "sleeps": new corrections are mixed with older ones and anchor data, and the model's LoRA adapter gets a small, careful update — like sleep consolidation in humans.
3. A guard runs the model against benchmarks before and after. If it didn't get better at the user's work, or forgot things it used to know, the update is rejected. Rollback is one command.
4. Next morning, the agent wakes up slightly better at YOUR work than yesterday.

The goal is not a model that's generally smarter. It's an agent that becomes specific to one person. Escalations should get rarer over time; cost per task should fall; the mistakes you corrected should stop coming back.

We're writing this up properly as a position paper: "Escalation as Supervision: Continual On-the-Job Learning for Personal Coding Agents." The claim: a deployed agent that routes tasks small-model-first already produces a stream of free, verified corrections every time it escalates — and that stream is enough to drive safe, daily weight updates.

This is the same philosophy behind everything I build with Aura: AI as an extension of the person, not a copy of everyone. A model that learns its human while working beside them is the most literal version of that so far.

Humans and AI are a team. Teams that learn each other get better every day. That's the future I'm building for.

---

## X / Twitter (short)

Every AI you use is frozen — it works with you all day and learns nothing.

We built a model that trains itself while it works. When the small model fails and the big model fixes it, that fix becomes free, verified training data. At night the model "sleeps": small LoRA update, replay buffer, benchmark guard, promote or rollback. Wakes up better at YOUR work.

Not generally smarter. Specific to you.

Paper: "Escalation as Supervision: Continual On-the-Job Learning for Personal Coding Agents"

---

## Hacker News / Reddit r/MachineLearning (technical)

**Escalation as Supervision: training a personal coding agent's model while it works**

Position paper + open system. The setup: a two-model coding agent (small local model first, escalation to a large model on failure) already generates a stream of free, verified correction triplets — (task, small-model attempt, accepted fix) — every single day. We treat that stream as the only training signal and drive daily weight updates from it. No separate training phase.

Mechanics: triplet capture from session episodes → quality filter → nightly replay buffer (new corrections / older corrections / anchor data, ~50/30/20) → incremental LoRA update per user → guard (personal benchmark + forgetting benchmark; reject and keep yesterday's adapter on regression) → adapter registry with one-command rollback. Two-speed memory: in-session fast weights reset at session end, consolidated adapter persists overnight.

The evaluation protocol we propose: time-split personal benchmark, forgetting benchmark, escalation-rate curve over simulated days (replay historical episodes day-by-day to get a 60-day learning curve without waiting 60 real days).

Interesting failure modes we're explicitly designing against: knowledge-editing-style drift/collapse, catastrophic forgetting of general skills, data poisoning through accepted-but-wrong fixes, and evaluation leakage (the model has already seen today's mistakes — benchmarks must be time-split).

We think this generalizes beyond coding agents: any deployed system with a fallback-and-fix pattern (routing, approval queues, human-in-the-loop corrections) is already producing supervision for free. The paper steelmans the strongest objection — "RAG and longer context already solve this" — and argues why weights matter: latency, cost, and generalization on the user's distribution rather than retrieval of it.

Working title: "Escalation as Supervision: Continual On-the-Job Learning for Personal Coding Agents." Built on the open-source aura-code agent (Archimedes routing, episode schema). Zenodo DOI + arXiv when it's ready.
