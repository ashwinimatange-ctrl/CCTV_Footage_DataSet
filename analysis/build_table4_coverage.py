#!/usr/bin/env python3
"""Build Table 4 camera-day coverage from HOURS_COVERED + COMPLETENESS_MATRIX.

Defaults to repo examples/; override with HOURS_CSV / MATRIX_CSV / OUT_DIR env vars.
"""
from __future__ import annotations

import csv
import os
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
EXAMPLES = REPO / "examples"
ARTIFACTS = Path(os.environ.get("OUT_DIR", str(REPO / "artifacts" / "analysis")))
HOURS = Path(os.environ.get("HOURS_CSV", str(EXAMPLES / "HOURS_COVERED.csv")))
MATRIX = Path(os.environ.get("MATRIX_CSV", str(EXAMPLES / "COMPLETENESS_MATRIX.csv")))

EXPECTED_HOURS = 24.0
FIELDNAMES = [
    "Camera",
    "Date",
    "First Time",
    "Last Time",
    "Observed Duration",
    "Expected Duration",
    "Missing Duration",
    "Coverage %",
    "_one Available",
]


def parse_t(t: str):
    t = (t or "").strip()
    if not t:
        return None
    try:
        return datetime.strptime(t, "%H:%M:%S")
    except ValueError:
        return None


def day_to_date(day: str) -> str:
    d = int(str(day).strip())
    return f"2023-01-{d:02d}"


def is_true(v) -> bool:
    return str(v).strip().lower() in ("true", "1", "yes")


def span_hours(first: datetime, last: datetime) -> float:
    sec = (last - first).total_seconds()
    if sec < 0:
        sec += 86400
    return round(sec / 3600.0, 4)


def main() -> int:
    if not HOURS.is_file():
        raise SystemExit(f"Missing {HOURS}")
    if not MATRIX.is_file():
        raise SystemExit(f"Missing {MATRIX}")

    ARTIFACTS.mkdir(parents=True, exist_ok=True)

    by_cd: dict[tuple[str, str], list[dict]] = defaultdict(list)
    n_files = 0
    n_short_files = 0
    with HOURS.open(encoding="utf-8", newline="") as f:
        for row in csv.DictReader(f):
            n_files += 1
            if row.get("flag") in ("very_short", "under_1h", "missing_times"):
                n_short_files += 1
            by_cd[(row["camera"], row["day"])].append(row)

    one_present: dict[tuple[str, str], bool] = {}
    with MATRIX.open(encoding="utf-8", newline="") as f:
        for row in csv.DictReader(f):
            one_present[(row["camera"], row["day"])] = is_true(row.get("one_present"))

    out_rows: list[dict] = []
    for (camera, day), parts in sorted(by_cd.items(), key=lambda x: (x[0][0], int(x[0][1]))):
        times = []
        for r in parts:
            a, b = parse_t(r.get("first_time", "")), parse_t(r.get("last_time", ""))
            if a:
                times.append(a)
            if b:
                times.append(b)
        if not times:
            continue
        first, last = min(times), max(times)
        observed = span_hours(first, last)
        missing = round(max(0.0, EXPECTED_HOURS - observed), 4)
        coverage = round(100.0 * observed / EXPECTED_HOURS, 1)
        has_one = one_present.get((camera, day))
        if has_one is None:
            has_one = any(is_true(r.get("is_one")) for r in parts)
        out_rows.append(
            {
                "Camera": camera,
                "Date": day_to_date(day),
                "First Time": first.strftime("%H:%M:%S"),
                "Last Time": last.strftime("%H:%M:%S"),
                "Observed Duration": observed,
                "Expected Duration": EXPECTED_HOURS,
                "Missing Duration": missing,
                "Coverage %": coverage,
                "_one Available": "Yes" if has_one else "No",
            }
        )

    csv_path = ARTIFACTS / "TABLE4_COVERAGE.csv"
    with csv_path.open("w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=FIELDNAMES)
        w.writeheader()
        w.writerows(out_rows)

    n_cd = len(out_rows)
    n_with_one = sum(1 for r in out_rows if r["_one Available"] == "Yes")
    coverages = [float(r["Coverage %"]) for r in out_rows]
    mean_cov = round(sum(coverages) / len(coverages), 2) if coverages else 0.0

    caption = (
        "Table 4. Per camera-day temporal coverage of the deposited CSVs. "
        "Observed duration is the span between the earliest and latest distinct Time values "
        "across primary and _one files. Expected duration is a full operating day (24 h). "
        f"Fifty-one deposited files are shorter than 1 h under the per-file span metric "
        f"(here: {n_short_files} short/missing of {n_files} files); users should concatenate "
        "primary and _one where both exist."
    )

    md_lines = [
        "# Table 4 — Camera-day coverage",
        "",
        f"Generated: {datetime.now(timezone.utc).isoformat()}",
        "",
        caption,
        "",
        "| " + " | ".join(FIELDNAMES) + " |",
        "| " + " | ".join("---" for _ in FIELDNAMES) + " |",
    ]
    for r in out_rows:
        md_lines.append("| " + " | ".join(str(r[c]) for c in FIELDNAMES) + " |")
    (ARTIFACTS / "TABLE4_COVERAGE.md").write_text("\n".join(md_lines) + "\n", encoding="utf-8")

    summary = (
        f"# Table 4 coverage summary\n\n"
        f"- Camera-days: {n_cd}\n"
        f"- With `_one`: {n_with_one}\n"
        f"- Mean coverage %: {mean_cov}\n"
        f"- Short files (per-file < 1 h): {n_short_files} / {n_files}\n"
        f"- Wrote `{csv_path}`\n"
    )
    (ARTIFACTS / "TABLE4_COVERAGE_SUMMARY.md").write_text(summary, encoding="utf-8")
    print(summary)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
