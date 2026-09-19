#!/usr/bin/env python3
"""Task 18: event-level auto/e-rickshaw confusion audit from spotcheck flags.

Among is_rickshaw=yes, scores P(Model class == car) under rickshaw → car taxonomy.

Env:
  SPOTCHECK_CSV — default data/event_spotcheck_23_18_9.csv
  OUT_DIR — default artifacts/eval
"""
from __future__ import annotations

import csv
import json
import os
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
OUT = Path(os.environ.get("OUT_DIR", str(REPO / "artifacts" / "eval")))
SRC = Path(
    os.environ.get(
        "SPOTCHECK_CSV",
        str(REPO / "data" / "event_spotcheck_23_18_9.csv"),
    )
)
CLASSES = ("car", "motorbike", "bus", "truck")


def yn(v: str) -> bool:
    return (v or "").strip().lower() in {"yes", "y", "true", "t", "1"}


def pct(n: int, d: int) -> float:
    return round(100.0 * n / d, 2) if d else 0.0


def main() -> int:
    if not SRC.is_file():
        raise SystemExit(
            f"Missing {SRC}. Place the spotcheck CSV under data/ or set SPOTCHECK_CSV."
        )
    OUT.mkdir(parents=True, exist_ok=True)

    total = 0
    rickshaw = 0
    model_on_rickshaw: Counter[str] = Counter()
    green_on_rickshaw = 0
    yellow_on_rickshaw = 0
    by_camera: Counter[str] = Counter()
    human_car = 0
    human_car_rickshaw = 0
    model_car = 0
    model_car_rickshaw = 0

    with SRC.open(encoding="utf-8", errors="replace", newline="") as f:
        for row in csv.DictReader(f):
            total += 1
            model = (row.get("Model class") or row.get("model_class") or "").strip().lower()
            raw_hc = (row.get("human_class") or "").strip().lower()
            is_r = yn(row.get("is_rickshaw") or "")
            gre = yn(row.get("green_plate") or "")
            yel = yn(row.get("yellow_plate") or "")
            cam = (row.get("camera") or "").strip() or "(unknown)"

            if raw_hc == "car":
                human_car += 1
                if is_r:
                    human_car_rickshaw += 1
            if model == "car":
                model_car += 1
                if is_r:
                    model_car_rickshaw += 1

            if not is_r:
                continue
            rickshaw += 1
            model_on_rickshaw[model if model in CLASSES else (model or "(blank)")] += 1
            if gre:
                green_on_rickshaw += 1
            if yel:
                yellow_on_rickshaw += 1
            by_camera[cam] += 1

    hit = model_on_rickshaw.get("car", 0)
    miss = rickshaw - hit
    confusion = {
        c: {
            "n": model_on_rickshaw.get(c, 0),
            "pct_of_rickshaw": pct(model_on_rickshaw.get(c, 0), rickshaw),
        }
        for c in CLASSES
    }
    other = {k: v for k, v in model_on_rickshaw.items() if k not in CLASSES}

    generated = datetime.now(timezone.utc).isoformat()
    payload = {
        "generated_utc": generated,
        "source": SRC.name,
        "definition": (
            "Among is_rickshaw=yes, taxonomy_hit = (Model class == car). "
            "Does not use swapped human_class/human_agree for the hit rate."
        ),
        "limitation": (
            "Event-level audit on pipeline-detected tracks humans tagged as "
            "rickshaw. Does not estimate rickshaws missed entirely by the detector."
        ),
        "n_events": total,
        "n_rickshaw": rickshaw,
        "rickshaw_share_pct": pct(rickshaw, total),
        "taxonomy_hit_n": hit,
        "taxonomy_hit_pct": pct(hit, rickshaw),
        "taxonomy_miss_n": miss,
        "taxonomy_miss_pct": pct(miss, rickshaw),
        "confusion_model_class": confusion,
        "other_model_class": other,
        "plates_among_rickshaw": {
            "green_yes": green_on_rickshaw,
            "green_pct": pct(green_on_rickshaw, rickshaw),
            "yellow_yes": yellow_on_rickshaw,
            "yellow_pct": pct(yellow_on_rickshaw, rickshaw),
        },
        "by_camera": dict(by_camera.most_common()),
        "share_of_human_class_car_pct": pct(human_car_rickshaw, human_car),
        "n_human_class_car": human_car,
        "n_human_class_car_rickshaw": human_car_rickshaw,
        "share_of_model_car_pct": pct(model_car_rickshaw, model_car),
        "n_model_car": model_car,
        "n_model_car_rickshaw": model_car_rickshaw,
    }

    json_path = OUT / "rickshaw_confusion_audit.json"
    json_path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")

    lines = [
        "# Rickshaw confusion audit (Task 18)",
        "",
        f"Generated: {generated}",
        f"Source: `{SRC.name}`",
        "",
        "## Results",
        "",
        f"| Events audited | {total:,} |",
        f"| Rickshaw-tagged | **{rickshaw:,}** ({pct(rickshaw, total):.2f}%) |",
        f"| Taxonomy hit (`model=car`) | **{hit:,} / {rickshaw:,} ({pct(hit, rickshaw):.2f}%)** |",
        "",
        "Limitation: does not measure rickshaws missed entirely by the detector.",
        "",
    ]
    md_path = OUT / "RICKSHAW_CONFUSION_AUDIT.md"
    md_path.write_text("\n".join(lines), encoding="utf-8")
    print(f"Wrote {json_path}")
    print(f"Wrote {md_path}")
    print(f"rickshaw={rickshaw}/{total} hit={hit} ({pct(hit, rickshaw):.2f}%)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
