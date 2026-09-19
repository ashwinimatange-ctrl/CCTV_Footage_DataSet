#!/usr/bin/env python3
"""Hours covered from TIME_SPANS.csv (first–last Time span per deposited file).

Env:
  TIME_SPANS_CSV — input (default: examples/TIME_SPANS.csv if present)
  OUT_DIR — output directory (default: artifacts/analysis)
"""
from __future__ import annotations

import csv
import os
from datetime import datetime, timezone
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
OUT = Path(os.environ.get("OUT_DIR", str(REPO / "artifacts" / "analysis")))
SPANS = Path(
    os.environ.get(
        "TIME_SPANS_CSV",
        str(REPO / "examples" / "TIME_SPANS.csv"),
    )
)


def parse_t(t: str):
    t = (t or "").strip()
    if not t:
        return None
    try:
        return datetime.strptime(t, "%H:%M:%S")
    except ValueError:
        return None


def main() -> int:
    if not SPANS.is_file():
        raise SystemExit(
            f"Missing {SPANS}. Provide TIME_SPANS.csv "
            "(from a local completeness scan) or set TIME_SPANS_CSV."
        )
    OUT.mkdir(parents=True, exist_ok=True)
    rows_out = []
    with SPANS.open(encoding="utf-8", newline="") as f:
        for row in csv.DictReader(f):
            a, b = parse_t(row.get("first_time", "")), parse_t(row.get("last_time", ""))
            hours = ""
            flag = "ok"
            if a and b:
                sec = (b - a).total_seconds()
                if sec < 0:
                    sec += 86400
                hours = round(sec / 3600.0, 4)
                if hours < 0.05:
                    flag = "very_short"
                elif hours < 1.0:
                    flag = "under_1h"
            else:
                flag = "missing_times"
            rows_out.append(
                {
                    "path": row.get("path", ""),
                    "camera": row.get("camera", ""),
                    "day": row.get("day", ""),
                    "is_one": row.get("is_one", ""),
                    "first_time": row.get("first_time", ""),
                    "last_time": row.get("last_time", ""),
                    "unique_times": row.get("unique_times", ""),
                    "hours_covered": hours,
                    "flag": flag,
                }
            )

    out_csv = OUT / "HOURS_COVERED.csv"
    with out_csv.open("w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(rows_out[0].keys()) if rows_out else ["path"])
        w.writeheader()
        w.writerows(rows_out)

    short = [r for r in rows_out if r["flag"] in ("very_short", "under_1h", "missing_times")]
    md = f"""# Hours covered

Generated: {datetime.now(timezone.utc).isoformat()}

`hours_covered = (last_time - first_time)` in hours (same-day wrap +24h if needed).

| Metric | Value |
|--------|-------|
| Files | {len(rows_out)} |
| Flagged short/missing | {len(short)} |
| Output | `{out_csv.name}` |

This is **span of observed timestamps**, not proof of continuous recording without gaps.
"""
    (OUT / "HOURS_COVERED_SUMMARY.md").write_text(md, encoding="utf-8")
    print(md)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
