#!/usr/bin/env python3
"""Compare local CCTV pipeline count CSVs to Mendeley published count dataset.

Framing: train dataset = local CCTV (2022), not published online (privacy).
Published dataset = Mendeley counts (2023), available online via DOI.
Legacy output dir name: artifacts/blackbox_2023.
"""
from __future__ import annotations

import csv
import json
import os
import subprocess
import sys
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
from sklearn.neighbors import KNeighborsRegressor

ROOT = Path(os.environ.get("WORK_ROOT", "/work"))
MENDELEY = Path(os.environ.get("MENDELEY_CSV", "/mendeley_csv"))
COUNTS = ROOT / "artifacts" / "counts_2022"
OUT = ROOT / "artifacts" / "blackbox_2023"


def guard(phase: str) -> None:
    subprocess.run(
        [sys.executable, str(ROOT / "scripts" / "resource_guard.py"), "--phase", phase, "--enforce"],
        check=False,
    )


def load_counts(path: Path) -> dict:
    totals = defaultdict(int)
    rows = 0
    dirs = set()
    with path.open(encoding="utf-8", newline="") as f:
        r = csv.DictReader(f)
        fields = r.fieldnames or []
        for row in r:
            rows += 1
            if "Direction" in row:
                dirs.add(row["Direction"])
            for k in ("car", "motorbike", "bus", "truck"):
                if k in row and row[k] not in (None, ""):
                    try:
                        totals[k] += int(float(row[k]))
                    except ValueError:
                        pass
    return {"rows": rows, "fields": fields, "directions": sorted(dirs), "totals": dict(totals)}


def class_share(totals: dict) -> dict:
    s = sum(totals.values()) or 1
    return {k: round(v / s, 4) for k, v in totals.items()}


def mendeley_sample_stats(path: Path, max_unique_times: int = 500) -> dict:
    """De-dup by taking max per (time, direction) for first N unique times — streaming."""
    best = {}
    uniq_times = []
    prev = None
    with path.open(encoding="utf-8", newline="") as f:
        r = csv.DictReader(f)
        for row in r:
            t = row.get("Time", "").strip()
            if not t:
                continue
            if t != prev:
                if len(uniq_times) >= max_unique_times:
                    break
                uniq_times.append(t)
                prev = t
            d = row.get("Direction", "")
            key = (t, d)
            vals = tuple(int(float(row.get(k, 0) or 0)) for k in ("car", "motorbike", "bus", "truck"))
            if key not in best or sum(vals) > sum(best[key]):
                best[key] = vals
    totals = defaultdict(int)
    for (t, d), vals in best.items():
        for i, k in enumerate(("car", "motorbike", "bus", "truck")):
            totals[k] += vals[i]
    return {
        "path": path.name,
        "unique_times_sampled": len(uniq_times),
        "direction_rows": len(best),
        "totals": dict(totals),
        "share": class_share(dict(totals)),
        "first_time": uniq_times[0] if uniq_times else "",
        "last_time_sampled": uniq_times[-1] if uniq_times else "",
    }


def forecast_test(train_totals_list: list[dict], mend_path: Path) -> dict:
    """Toy black-box: KNN on hour->total from 2022 clip totals vs sample of 2023 series."""
    # 2022 clips are single interval — weak train; use synthetic hour features from shares
    if len(train_totals_list) < 2:
        return {"skipped": True, "reason": "need >=2 train clips"}
    X, y = [], []
    for i, tot in enumerate(train_totals_list):
        total = sum(tot.values())
        X.append([i, tot.get("car", 0), tot.get("motorbike", 0), tot.get("bus", 0), tot.get("truck", 0)])
        y.append(total)
    X = np.array(X, dtype=float)
    y = np.array(y, dtype=float)
    model = KNeighborsRegressor(n_neighbors=min(3, len(X)))
    model.fit(X, y)
    # Build a few points from mendeley sample aggregates by chunking unique times
    stats = mendeley_sample_stats(mend_path, max_unique_times=200)
    # predict using mean feature scaled
    feat = np.array(
        [
            [
                0,
                stats["totals"].get("car", 0) / 50,
                stats["totals"].get("motorbike", 0) / 50,
                stats["totals"].get("bus", 0) / 50,
                stats["totals"].get("truck", 0) / 50,
            ]
        ]
    )
    pred = float(model.predict(feat)[0])
    actual = float(sum(stats["totals"].values()))
    return {
        "skipped": False,
        "note": "Illustrative transfer forecast only; domains differ (site/year).",
        "train_n": len(X),
        "pred_total_like": round(pred, 2),
        "mendeley_sample_total": actual,
        "abs_error": round(abs(pred - actual), 2),
    }


def main() -> int:
    guard("5-blackbox-start")
    OUT.mkdir(parents=True, exist_ok=True)
    schema_expected = ["Time", "Direction", "car", "motorbike", "bus", "truck"]

    train_files = sorted(COUNTS.glob("2022_5min_*.csv"))
    train_stats = []
    for p in train_files:
        st = load_counts(p)
        st["path"] = p.name
        st["share"] = class_share(st["totals"])
        st["schema_ok"] = list(st["fields"]) == schema_expected
        train_stats.append(st)

    mend_file = MENDELEY / "traffic__A__a2__a2_11.csv"
    if not mend_file.exists():
        # try alternate naming
        cands = list(MENDELEY.glob("*a2_11.csv"))
        mend_file = cands[0] if cands else mend_file

    mend_stats = None
    forecast = {"skipped": True, "reason": "mendeley file missing"}
    if mend_file.exists():
        mend_stats = mendeley_sample_stats(mend_file)
        forecast = forecast_test([s["totals"] for s in train_stats], mend_file)

    # Aggregate 2022 shares
    agg = defaultdict(int)
    for s in train_stats:
        for k, v in s["totals"].items():
            agg[k] += v
    report = {
        "generated": datetime.now(timezone.utc).isoformat(),
        "verification_ref": "01-discovery/DATA_VERIFICATION.md",
        "honesty": "Train dataset = local CCTV (2022), not published online (privacy). Published dataset = Mendeley counts (2023), online via DOI. Count-structure compare only; not frame mAP.",
        "train_2022": {
            "n_files": len(train_stats),
            "files": train_stats,
            "aggregate_totals": dict(agg),
            "aggregate_share": class_share(dict(agg)),
            "schema_expected": schema_expected,
        },
        "mendeley_2023_sample": mend_stats,
        "forecast_toy": forecast,
        "comparability": {
            "schema_compatible": bool(mend_stats) and all(
                c in (load_counts(mend_file)["fields"] if mend_file.exists() else [])
                for c in schema_expected
            ),
            "cameras_match": False,
            "dates_match": False,
        },
    }

    (OUT / "BLACKBOX_REPORT.json").write_text(json.dumps(report, indent=2), encoding="utf-8")
    lines = [
        "# Count compare — 2022 train pipeline vs 2023 published Mendeley",
        "",
        f"Generated: {report['generated']}",
        "",
        report["honesty"],
        "",
        "## Train dataset run (2022)",
        f"- Files: {report['train_2022']['n_files']}",
        f"- Aggregate totals: `{report['train_2022']['aggregate_totals']}`",
        f"- Aggregate class share: `{report['train_2022']['aggregate_share']}`",
        "",
        "## Published dataset sample (2023, `a2_11`)",
        f"- `{mend_stats}`" if mend_stats else "- missing",
        "",
        "## Forecast toy",
        f"- `{forecast}`",
        "",
        "## Comparability flags",
        f"- `{report['comparability']}`",
        "",
    ]
    (OUT / "REPORT.md").write_text("\n".join(lines), encoding="utf-8")
    print((OUT / "REPORT.md").read_text(encoding="utf-8"))
    guard("5-blackbox-end")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
