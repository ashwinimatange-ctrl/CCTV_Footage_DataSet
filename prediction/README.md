# Prediction / forecast helpers

| Script | Role |
|--------|------|
| `knn_stratified_eval.py` | Held-out stratified KNN on count `total` (preferred) |
| `KNN_model.py` | Legacy notebook-style in-sample KNN (reference only) |

```bat
set PREDICTION_INPUT=D:\path\to\dataset.csv
python prediction\knn_stratified_eval.py
```

Place a small sample under `prediction/input/dataset.csv` if desired (gitignored except README).
Outputs go to `artifacts/prediction/`.
