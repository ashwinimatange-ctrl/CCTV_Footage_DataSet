#!/usr/bin/env python3
"""Stratified train/test KNN evaluation on count totals.

Env:
  PREDICTION_INPUT — CSV with Junction,Date,Time,Direction,car,...,total
  OUT_DIR — output folder (default: artifacts/prediction)
"""
from __future__ import annotations

import json
import math
import os
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from sklearn.model_selection import train_test_split
from sklearn.neighbors import KNeighborsRegressor

REPO = Path(__file__).resolve().parents[1]
HERE = Path(__file__).resolve().parent
ROOT = Path(os.environ.get("PREDICTION_ROOT", str(HERE)))
INPUT = Path(
    os.environ.get(
        "PREDICTION_INPUT",
        str(ROOT / "input" / "dataset.csv"),
    )
)
OUT_DIR = Path(os.environ.get("OUT_DIR", str(REPO / "artifacts" / "prediction")))
REPORT = OUT_DIR / "KNN_STRATIFIED_EVAL.md"
METRICS_JSON = OUT_DIR / "knn_stratified_metrics.json"


def prepare(df: pd.DataFrame) -> pd.DataFrame:
    d = df.dropna().copy()
    d["uniqueDate"] = d["Date"].astype(str).str.replace("-", "", regex=False).astype(int)
    # dataset.csv uses MM-DD-YYYY (e.g. 01-14-2023 = 14 Jan 2023)
    d["Date_dt"] = pd.to_datetime(d["Date"], format="%m-%d-%Y", errors="coerce")
    d["day"] = d["Date_dt"].dt.weekday
    ts = pd.to_datetime(d["Time"], format="%H:%M:%S", errors="coerce")
    d["hour"] = ts.dt.hour
    d["minute"] = ts.dt.minute
    d = d.dropna(subset=["Date_dt", "day", "hour", "minute"]).copy()
    d["Junction"] = d["Junction"].astype(int)
    d["Direction"] = d["Direction"].astype(int)
    d["total"] = d["total"].astype(float)
    # Stratify key: junction × direction × weekday (keep strata large enough)
    d["strata"] = (
        d["Junction"].astype(str)
        + "_"
        + d["Direction"].astype(str)
        + "_"
        + d["day"].astype(str)
    )
    return d


def feature_matrix(d: pd.DataFrame) -> tuple[pd.DataFrame, pd.Series]:
    x = d[["Junction", "Direction", "uniqueDate", "day", "hour", "minute"]].copy()
    y = d["total"]
    return x, y


def metrics_block(y_true, y_pred) -> dict:
    y_true = np.asarray(y_true, dtype=float)
    y_pred = np.asarray(y_pred, dtype=float)
    mae = float(mean_absolute_error(y_true, y_pred))
    mse = float(mean_squared_error(y_true, y_pred))
    rmse = float(math.sqrt(mse))
    r2 = float(r2_score(y_true, y_pred))
    # MAPE skip zeros
    mask = y_true != 0
    mape = float(np.mean(np.abs((y_true[mask] - y_pred[mask]) / y_true[mask])) * 100) if mask.any() else None
    return {"n": int(len(y_true)), "MAE": mae, "RMSE": rmse, "R2": r2, "MAPE_pct": mape}


def main() -> int:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    raw = pd.read_csv(INPUT)
    d = prepare(raw)

    # Drop tiny strata (< 2) so stratified split works
    counts = d["strata"].value_counts()
    keep = counts[counts >= 2].index
    d = d[d["strata"].isin(keep)].copy()

    train_df, test_df = train_test_split(
        d,
        test_size=0.2,
        random_state=42,
        stratify=d["strata"],
    )

    x_train, y_train = feature_matrix(train_df)
    x_test, y_test = feature_matrix(test_df)

    # Prefer k=5 for generalization; also report k=1 for parity with legacy script
    results = {
        "generated": datetime.now(timezone.utc).isoformat(),
        "input": str(INPUT),
        "rows_total_input": int(len(raw)),
        "rows_after_prep": int(len(d)),
        "train_rows": int(len(train_df)),
        "test_rows": int(len(test_df)),
        "test_size": 0.2,
        "stratify_by": "Junction_Direction_weekday",
        "features": list(x_train.columns),
        "models": {},
    }

    best_name = None
    best_rmse = None
    best_pred = None

    for k in (1, 3, 5):
        model = KNeighborsRegressor(n_neighbors=k)
        model.fit(x_train, y_train)
        pred_train = model.predict(x_train)
        pred_test = model.predict(x_test)
        block = {
            "n_neighbors": k,
            "train": metrics_block(y_train, pred_train),
            "test": metrics_block(y_test, pred_test),
        }
        results["models"][f"k{k}"] = block
        if best_rmse is None or block["test"]["RMSE"] < best_rmse:
            best_rmse = block["test"]["RMSE"]
            best_name = f"k{k}"
            best_pred = pred_test

    # Per-junction test metrics for best model
    best_k = results["models"][best_name]["n_neighbors"]
    model = KNeighborsRegressor(n_neighbors=best_k)
    model.fit(x_train, y_train)
    test_pred = model.predict(x_test)
    by_j = {}
    tmp = test_df.copy()
    tmp["y_true"] = y_test.values
    tmp["y_pred"] = test_pred
    for j, g in tmp.groupby("Junction"):
        by_j[str(int(j))] = metrics_block(g["y_true"], g["y_pred"])
    results["best_model"] = best_name
    results["test_by_junction"] = by_j

    # Save stratified split CSVs + predictions
    train_out = train_df[
        ["Junction", "Date", "Time", "Direction", "car", "motorbike", "bus", "truck", "total"]
    ].copy()
    test_out = test_df[
        ["Junction", "Date", "Time", "Direction", "car", "motorbike", "bus", "truck", "total"]
    ].copy()
    test_pred_df = test_out.copy()
    test_pred_df["predicted_total"] = test_pred
    test_pred_df["residual"] = test_pred_df["total"] - test_pred_df["predicted_total"]

    train_path = OUT_DIR / "knn_train_stratified.csv"
    test_path = OUT_DIR / "knn_test_stratified.csv"
    pred_path = OUT_DIR / "knn_test_predictions_stratified.csv"
    train_out.to_csv(train_path, index=False)
    test_out.to_csv(test_path, index=False)
    test_pred_df.to_csv(pred_path, index=False)

    METRICS_JSON.write_text(json.dumps(results, indent=2), encoding="utf-8")

    lines = [
        "# KNN stratified train/test evaluation",
        "",
        f"Generated: {results['generated']}",
        "",
        "## Setup",
        "",
        f"- Input: `{INPUT.name}` ({results['rows_total_input']} rows)",
        f"- After prep / min-strata filter: {results['rows_after_prep']}",
        f"- Stratify by: **{results['stratify_by']}** (Junction × Direction × weekday)",
        f"- Split: train={results['train_rows']} ({100*(1-0.2):.0f}%) / test={results['test_rows']} (20%), `random_state=42`",
        f"- Features: {', '.join(results['features'])}",
        f"- Target: `total`",
        "",
        "## Results (lower RMSE better on test)",
        "",
        "| k | Train MAE | Train RMSE | Train R² | Test MAE | Test RMSE | Test R² | Test MAPE% |",
        "|--:|----------:|-----------:|---------:|---------:|----------:|--------:|-----------:|",
    ]
    for name, block in results["models"].items():
        tr, te = block["train"], block["test"]
        mape = f"{te['MAPE_pct']:.2f}" if te["MAPE_pct"] is not None else "n/a"
        lines.append(
            f"| {block['n_neighbors']} | {tr['MAE']:.3f} | {tr['RMSE']:.3f} | {tr['R2']:.4f} | "
            f"{te['MAE']:.3f} | {te['RMSE']:.3f} | {te['R2']:.4f} | {mape} |"
        )
    lines += [
        "",
        f"**Best by test RMSE:** `{best_name}` (k={best_k})",
        "",
        "## Test metrics by junction (best k)",
        "",
        "| Junction | n | MAE | RMSE | R² |",
        "|---------:|--:|----:|-----:|---:|",
    ]
    for j, m in sorted(by_j.items(), key=lambda kv: int(kv[0])):
        lines.append(f"| {j} | {m['n']} | {m['MAE']:.3f} | {m['RMSE']:.3f} | {m['R2']:.4f} |")

    lines += [
        "",
        "## Outputs",
        "",
        f"- `{train_path.name}` — stratified train split",
        f"- `{test_path.name}` — stratified test split",
        f"- `{pred_path.name}` — test predictions (`predicted_total`, `residual`)",
        f"- `{METRICS_JSON.name}` — full metrics JSON",
        "",
        "## Note",
        "",
        "Legacy `KNN_model.py` fit/predict on the full dataset (in-sample). This run is the "
        "held-out stratified evaluation.",
        "",
    ]
    REPORT.write_text("\n".join(lines), encoding="utf-8")

    print(REPORT.read_text(encoding="utf-8"))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
