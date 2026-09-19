#!/usr/bin/env python3
"""Scan a local Mendeley traffic CSV tree for completeness + time spans.

Expects MENDELEY_CSV root containing junction folders (AlankarChowk / JehangirChowk /
RTOChowk) or a flat `traffic/` tree with `a2_11.csv` style names.

Env:
  MENDELEY_CSV — required input root
  OUT_DIR — default artifacts/analysis
"""
from __future__ import annotations

import csv
import hashlib
import os
import re
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
OUT = Path(os.environ.get("OUT_DIR", str(REPO / "artifacts" / "analysis")))
ROOT = Path(os.environ.get("MENDELEY_CSV", ""))

CAMERAS = ["a2", "a3", "j1", "j2", "j3", "r1", "r2", "r3"]
DAYS = [str(d) for d in range(11, 19)]
NAME_RE = re.compile(r"^(?P<cam>[ajr]\d)_(?P<day>\d+)(?P<one>_one)?\.csv$", re.I)


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def scan_times(path: Path) -> tuple[int, str, str, int]:
    """Return rows, first_time, last_time, unique_times (streaming)."""
    first = last = None
    uniq: set[str] = set()
    rows = 0
    with path.open(encoding="utf-8", errors="replace", newline="") as f:
        reader = csv.DictReader(f)
        for row in reader:
            rows += 1
            t = (row.get("Time") or "").strip()
            if not t:
                continue
            uniq.add(t)
            if first is None or t < first:
                first = t
            if last is None or t > last:
                last = t
    return rows, first or "", last or "", len(uniq)


def main() -> int:
    if not ROOT.is_dir():
        raise SystemExit(
            "Set MENDELEY_CSV to the extracted Mendeley traffic root "
            "(download DOI 10.17632/xnf2k6n288.1 first)."
        )
    OUT.mkdir(parents=True, exist_ok=True)

    files: list[Path] = sorted(ROOT.rglob("*.csv"))
    # Prefer deposit-style names
    named = []
    for p in files:
        m = NAME_RE.match(p.name)
        if m:
            named.append((p, m.group("cam").lower(), m.group("day"), bool(m.group("one"))))

    presence: dict[tuple[str, str], dict] = {
        (c, d): {"primary": False, "one": False} for c in CAMERAS for d in DAYS
    }
    spans = []
    for p, cam, day, is_one in named:
        key = (cam, day)
        if key in presence:
            if is_one:
                presence[key]["one"] = True
            else:
                presence[key]["primary"] = True
        rows, first, last, nuniq = scan_times(p)
        spans.append(
            {
                "path": str(p.relative_to(ROOT)).replace("\\", "/"),
                "camera": cam,
                "day": day,
                "is_one": is_one,
                "bytes": p.stat().st_size,
                "rows": rows,
                "unique_times": nuniq,
                "first_time": first,
                "last_time": last,
                "sha256": sha256_file(p),
            }
        )

    matrix_rows = []
    for c in CAMERAS:
        for d in DAYS:
            prim = presence[(c, d)]["primary"]
            one = presence[(c, d)]["one"]
            if prim and one:
                status = "primary+one"
            elif prim:
                status = "primary_only"
            elif one:
                status = "one_only"
            else:
                status = "MISSING"
            matrix_rows.append(
                {
                    "camera": c,
                    "day": d,
                    "primary_present": prim,
                    "one_present": one,
                    "status": status,
                }
            )

    mat_path = OUT / "COMPLETENESS_MATRIX.csv"
    with mat_path.open("w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(
            f,
            fieldnames=["camera", "day", "primary_present", "one_present", "status"],
        )
        w.writeheader()
        w.writerows(matrix_rows)

    spans_path = OUT / "TIME_SPANS.csv"
    with spans_path.open("w", encoding="utf-8", newline="") as f:
        fields = [
            "path",
            "camera",
            "day",
            "is_one",
            "bytes",
            "rows",
            "unique_times",
            "first_time",
            "last_time",
            "sha256",
        ]
        w = csv.DictWriter(f, fieldnames=fields)
        w.writeheader()
        w.writerows(spans)

    missing = sum(1 for r in matrix_rows if r["status"] == "MISSING")
    primary_only = sum(1 for r in matrix_rows if r["status"] == "primary_only")
    md = f"""# Local completeness scan

Generated: {datetime.now(timezone.utc).isoformat()}
Root: `{ROOT}`

| Metric | Value |
|--------|-------|
| Named CSVs scanned | {len(named)} |
| Missing camera-days | {missing} |
| Primary without `_one` | {primary_only} |
| Outputs | `{mat_path.name}`, `{spans_path.name}` |

Next: `python analysis/hours_covered.py` with `TIME_SPANS_CSV={spans_path}` then
`python analysis/build_table4_coverage.py`.
"""
    (OUT / "COMPLETENESS_SUMMARY.md").write_text(md, encoding="utf-8")
    print(md)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
