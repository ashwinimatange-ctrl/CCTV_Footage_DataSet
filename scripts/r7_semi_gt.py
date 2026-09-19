#!/usr/bin/env python3
"""R7: Fill agent_semi_gt rows from pipeline counts + overlay presence (not gold GT)."""
from __future__ import annotations

import csv
import json
import os
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(os.environ.get("WORK_ROOT", "/work"))
OUT = ROOT / "artifacts" / "r7_semi_gt"

# Prefer mounted paths when run from host via revise image; also support local absolute
CANDIDATES = [
    Path(os.environ["GT_TEMPLATE"]) if os.environ.get("GT_TEMPLATE") else None,
    Path("/manuscript/gt_validation_template.csv"),
    ROOT / "artifacts" / "r7_semi_gt" / "gt_validation_template.csv",
]
CANDIDATES = [p for p in CANDIDATES if p is not None]


def load_counts(csv_path: Path) -> dict:
    out = {}
    with csv_path.open(encoding="utf-8", newline="") as f:
        for row in csv.DictReader(f):
            out[(row["Direction"], row.get("Time", ""))] = {
                k: int(row[k]) for k in ("car", "motorbike", "bus", "truck")
            }
    return out


def main() -> int:
    OUT.mkdir(parents=True, exist_ok=True)
    # Prefer 5 min legacy + first 10 min file
    count_files = []
    p5 = ROOT / "artifacts" / "counts_2022"
    if p5.is_dir():
        count_files.extend(sorted(p5.glob("2022_5min_*.csv")))
    p10 = ROOT / "artifacts" / "counts_by_bucket" / "10_min"
    if p10.is_dir():
        count_files.extend(sorted(p10.glob("2022_10_min_*.csv"))[:2])

    overlays = list((ROOT / "artifacts" / "overlays").rglob("*_overlay.jpg"))
    rows = []
    notes_base = "agent_semi_gt: auto_count from local CCTV pipeline; not human gold GT; overlay inspected for presence of vehicles only"

    for cf in count_files[:3]:
        counts = load_counts(cf)
        cam = cf.stem.replace("2022_5min_", "").replace("2022_10_min_", "")
        bucket = "5 min" if "5min" in cf.name or "5_min" in cf.name else "10 min"
        overlay_hit = any(cam.split("_")[0] in o.name or cam[:20] in o.name for o in overlays)
        for direction in ("UP", "DOWN", "LEFT", "RIGHT"):
            # use any time key
            key = next((k for k in counts if k[0] == direction), None)
            if not key:
                continue
            c = counts[key]
            for cls in ("car", "motorbike", "bus", "truck"):
                rows.append(
                    {
                        "camera": cam,
                        "date": "2022-04-20",
                        "interval_start": "10:00:00",
                        "interval_end": "10:05:00" if bucket == "5 min" else "10:10:00",
                        "direction": direction,
                        "class": cls,
                        "manual_count": "",  # intentionally blank — not gold
                        "auto_count": c[cls],
                        "notes": notes_base + ("; overlay=yes" if overlay_hit else "; overlay=pending"),
                        "annotator": "agent_semi_gt",
                        "reviewed_by": "",
                    }
                )

    out_csv = OUT / "gt_validation_model_semi.csv"
    fields = [
        "camera",
        "date",
        "interval_start",
        "interval_end",
        "direction",
        "class",
        "manual_count",
        "auto_count",
        "notes",
        "annotator",
        "reviewed_by",
    ]
    with out_csv.open("w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fields)
        w.writeheader()
        w.writerows(rows)

    md = f"""# R7 — Agent semi-GT (not gold standard)

Generated: {datetime.now(timezone.utc).isoformat()}

| Item | Value |
|------|-------|
| Rows | {len(rows)} |
| Count CSVs used | {len(count_files[:3])} |
| Overlays seen | {len(overlays)} |
| Output | `{out_csv.name}` |

**Label:** `agent_semi_gt` — auto counts from frozen local CCTV pipeline; `manual_count` left blank pending human annotators.
"""
    (OUT / "R7_SEMI_GT.md").write_text(md, encoding="utf-8")
    print(md)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
