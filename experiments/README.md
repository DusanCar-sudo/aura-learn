# Experiments

One line per run in `results.jsonl`:

```json
{"run_id": "2026-11-02-b2", "phase": 3, "method": "B2-batch-lora", "adapter": "a003",
 "personal_success": 0.41, "forgetting_score": 0.62, "escalation_rate": 0.38,
 "gpu_hours": 0.7, "notes": "..."}
```

Run folders `runs/<run_id>/` hold the config used and the logs. Nothing in this folder gets edited after a run finishes.
