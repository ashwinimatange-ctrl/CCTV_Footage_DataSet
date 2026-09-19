#!/usr/bin/env python3
"""Write the public-dataset comparison table (no fabricated accuracy metrics)."""
from __future__ import annotations

import os
from datetime import datetime, timezone
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
OUT = Path(os.environ.get("OUT_DIR", str(REPO / "artifacts" / "analysis")))

ROWS = [
    {
        "name": "Heterogeneous Traffic Count Dataset, Pune",
        "region": "Pune, India",
        "traffic": "Heterogeneous, weak lane discipline",
        "duration": "Published 2023 (deposit calendar 11–18 Jan); train video 2022 unpublished",
        "classes": "car, motorbike, bus, truck",
        "direction": "UP/DOWN/LEFT/RIGHT",
        "video": "No (counts only)",
        "doi": "https://doi.org/10.17632/xnf2k6n288.1",
    },
    {
        "name": "SUMO (simulator; not a field count corpus)",
        "region": "Synthetic / user scenarios",
        "traffic": "Configurable",
        "duration": "Scenario-dependent",
        "classes": "User-defined",
        "direction": "Network-defined",
        "video": "N/A",
        "doi": "https://doi.org/10.1109/ITSC.2018.8569938",
    },
    {
        "name": "CityFlow",
        "region": "Multiple cities (benchmark)",
        "traffic": "Urban multi-camera",
        "duration": "Benchmark sequences",
        "classes": "Vehicles (tracking-oriented)",
        "direction": "Multi-camera trajectories",
        "video": "Yes (benchmark)",
        "doi": "https://github.com/Zhongdao/CityFlow",
    },
    {
        "name": "UA-DETRAC",
        "region": "Beijing / traffic surveillance",
        "traffic": "Urban road",
        "duration": "Benchmark hours of video",
        "classes": "Vehicle categories",
        "direction": "Not direction-count CSV",
        "video": "Yes",
        "doi": "https://doi.org/10.1016/j.patcog.2020.107130",
    },
    {
        "name": "HighD / naturalistic trajectory class",
        "region": "Germany (highway)",
        "traffic": "Lane-based highway",
        "duration": "Multi-hour recordings",
        "classes": "Car/truck-focused",
        "direction": "Carriageway directions",
        "video": "Derived trajectories",
        "doi": "https://doi.org/10.1038/s41597-018-0001-0",
    },
]


def main() -> int:
    OUT.mkdir(parents=True, exist_ok=True)
    cols = ["name", "region", "traffic", "duration", "classes", "direction", "video", "doi"]
    lines = [
        "# Comparison table (public resources)",
        "",
        f"Generated: {datetime.now(timezone.utc).isoformat()}",
        "",
        "No detector performance superiority is claimed.",
        "",
        "| " + " | ".join(cols) + " |",
        "| " + " | ".join("---" for _ in cols) + " |",
    ]
    for r in ROWS:
        lines.append("| " + " | ".join(str(r[c]) for c in cols) + " |")
    path = OUT / "COMPARISON_TABLE.md"
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"Wrote {path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
