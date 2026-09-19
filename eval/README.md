# Evaluation scripts

| Script | Role |
|--------|------|
| `audit_rickshaw_confusion.py` | Task 18 rickshaw→car taxonomy hit rate |
| `compute_human_gt_metrics.py` | Human gold MAE/RMSE/MAPE (refuses empty labels) |

```bat
python eval\audit_rickshaw_confusion.py
```

Requires [`data/event_spotcheck_23_18_9.csv`](../data/event_spotcheck_23_18_9.csv) (spotcheck events; not raw video).

For human GT metrics, place filled aggregate CSV under `data/human_gt/` or set `HUMAN_GT_DIR`.
