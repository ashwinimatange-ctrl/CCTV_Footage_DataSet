#!/usr/bin/env python3
"""Run YOLOv8n + ByteTrack on local CCTV AVIs; emit count CSVs per duration bucket.

Env:
  BUCKET — e.g. \"10 min\", \"1 Hours\" (default \"5 min\")
  Or set RUN_ALL_SHORT=1 to process 10 min → 1 Hours sequentially.
"""
from __future__ import annotations

import csv
import hashlib
import json
import os
import re
import subprocess
import sys
import time
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path

import cv2
import yaml

ROOT = Path(os.environ.get("WORK_ROOT", "/work"))
FOOTAGE = Path(os.environ.get("FOOTAGE_ROOT", "/footage"))
CFG_PATH = ROOT / "config" / "config.yaml"
CLASS_MAP = {2: "car", 3: "motorbike", 5: "bus", 7: "truck"}

SHORT_BUCKETS = [
    "10 min",
    "15 min",
    "20 min",
    "25 min",
    "30 min",
    "45 min",
    "1 Hours",
]

REMAINING_DEFAULT = [
    "25 min",
    "30 min",
    "45 min",
    "1 Hours",
]


def bucket_complete(bucket: str) -> bool:
    """True if RUN_SUMMARY exists with >=5 successful file entries (no error)."""
    slug = bucket_slug(bucket)
    if bucket == "5 min":
        summary_path = ROOT / "artifacts" / "counts_2022" / "RUN_SUMMARY.json"
    else:
        summary_path = ROOT / "artifacts" / "counts_by_bucket" / slug / "RUN_SUMMARY.json"
    if not summary_path.is_file():
        return False
    try:
        data = json.loads(summary_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return False
    files = data.get("files") or []
    ok = [f for f in files if not f.get("error")]
    return len(ok) >= 5


def bucket_slug(bucket: str) -> str:
    return re.sub(r"[^\w]+", "_", bucket.strip()).strip("_")


def guard(phase: str, notes: str = "") -> int:
    cmd = [
        sys.executable,
        str(ROOT / "scripts" / "resource_guard.py"),
        "--phase",
        phase,
        "--enforce",
        "--notes",
        notes,
    ]
    return subprocess.run(cmd, check=False).returncode


def sha256_file(p: Path) -> str:
    h = hashlib.sha256()
    with p.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def direction_from_delta(dx: float, dy: float, min_disp: float) -> str | None:
    if (dx * dx + dy * dy) ** 0.5 < min_disp:
        return None
    if abs(dx) >= abs(dy):
        return "RIGHT" if dx > 0 else "LEFT"
    return "DOWN" if dy > 0 else "UP"


def process_avi(path: Path, cfg: dict, model, out_dir: Path, overlay_dir: Path, bucket: str) -> dict:
    stride = int(cfg["temporal"]["frame_stride"])
    imgsz = int(cfg["detector"]["imgsz"])
    conf = float(cfg["detector"]["conf"])
    iou = float(cfg["detector"]["iou"])
    min_disp = float(cfg["direction"]["min_track_displacement_px"])

    name = path.stem
    cam = name
    if name.startswith("Export__"):
        for day in ("Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"):
            if f"_{day}" in name:
                cam = name[len("Export__") :].split(f"_{day}")[0]
                break

    cap = cv2.VideoCapture(str(path))
    if not cap.isOpened():
        return {"path": str(path), "error": "cannot_open", "camera": cam, "bucket": bucket}

    fps = float(cap.get(cv2.CAP_PROP_FPS) or 25.0)
    nframes = int(cap.get(cv2.CAP_PROP_FRAME_COUNT) or 0)
    tracks: dict[int, dict] = {}
    frame_idx = 0
    processed = 0
    detections = 0
    overlay_saved = False
    t0 = time.time()

    while True:
        ok, frame = cap.read()
        if not ok:
            break
        if frame_idx % stride != 0:
            frame_idx += 1
            continue
        try:
            results = model.track(
                frame,
                persist=True,
                conf=conf,
                iou=iou,
                imgsz=imgsz,
                device="cpu",
                verbose=False,
                classes=list(CLASS_MAP.keys()),
            )
        except Exception as exc:  # noqa: BLE001 — ByteTrack Kalman can fail on some frames
            print(f"  track skip frame {frame_idx}: {type(exc).__name__}: {exc}", flush=True)
            try:
                model.predictor = None
            except Exception:  # noqa: BLE001
                pass
            frame_idx += 1
            continue
        processed += 1
        r0 = results[0]
        if r0.boxes is not None and r0.boxes.id is not None:
            ids = r0.boxes.id.cpu().numpy().astype(int)
            clss = r0.boxes.cls.cpu().numpy().astype(int)
            xyxy = r0.boxes.xyxy.cpu().numpy()
            detections += len(ids)
            for tid, cls, box in zip(ids, clss, xyxy):
                if int(cls) not in CLASS_MAP:
                    continue
                cx = float((box[0] + box[2]) / 2)
                cy = float((box[1] + box[3]) / 2)
                label = CLASS_MAP[int(cls)]
                if tid not in tracks:
                    tracks[tid] = {"cls": label, "x0": cx, "y0": cy, "x1": cx, "y1": cy}
                else:
                    tracks[tid]["x1"] = cx
                    tracks[tid]["y1"] = cy
                    tracks[tid]["cls"] = label
            if not overlay_saved:
                plotted = r0.plot()
                overlay_dir.mkdir(parents=True, exist_ok=True)
                cv2.imwrite(str(overlay_dir / f"{path.stem}_overlay.jpg"), plotted)
                overlay_saved = True
        frame_idx += 1

    cap.release()
    try:
        model.predictor = None
    except Exception:  # noqa: BLE001
        pass

    start_label = "10:00:00"
    counts = defaultdict(lambda: {"car": 0, "motorbike": 0, "bus": 0, "truck": 0})
    for tr in tracks.values():
        d = direction_from_delta(tr["x1"] - tr["x0"], tr["y1"] - tr["y0"], min_disp)
        if d is None:
            continue
        counts[d][tr["cls"]] += 1

    out_dir.mkdir(parents=True, exist_ok=True)
    safe = "".join(c if c.isalnum() or c in "-_" else "_" for c in cam)
    slug = bucket_slug(bucket)
    csv_path = out_dir / f"2022_{slug}_{safe}.csv"
    with csv_path.open("w", encoding="utf-8", newline="") as f:
        w = csv.writer(f)
        w.writerow(["Time", "Direction", "car", "motorbike", "bus", "truck"])
        for d in ["UP", "DOWN", "LEFT", "RIGHT"]:
            c = counts[d]
            w.writerow([start_label, d, c["car"], c["motorbike"], c["bus"], c["truck"]])

    return {
        "path": str(path),
        "bucket": bucket,
        "camera": cam,
        "csv": str(csv_path),
        "fps": fps,
        "frame_count": nframes,
        "frames_processed": processed,
        "raw_detections": detections,
        "tracks_kept": sum(
            1
            for tr in tracks.values()
            if direction_from_delta(tr["x1"] - tr["x0"], tr["y1"] - tr["y0"], min_disp)
        ),
        "wall_seconds": round(time.time() - t0, 1),
        "counts": {d: dict(counts[d]) for d in ["UP", "DOWN", "LEFT", "RIGHT"]},
    }


def resolve_weights(cfg: dict) -> str:
    raw = cfg["detector"]["weights"]
    for candidate in (ROOT / raw, ROOT / "weights" / "yolov8n.pt", Path(raw)):
        if candidate.is_file():
            return str(candidate)
    return raw


def run_bucket(bucket: str, cfg: dict, digest: str) -> dict:
    from ultralytics import YOLO

    slug = bucket_slug(bucket)
    out_dir = ROOT / "artifacts" / "counts_by_bucket" / slug
    overlay_dir = ROOT / "artifacts" / "overlays" / slug
    # Preserve legacy 5 min location
    if bucket == "5 min":
        out_dir = ROOT / "artifacts" / "counts_2022"
        overlay_dir = ROOT / "artifacts" / "overlays"

    media = FOOTAGE / bucket / "ExportedMedia"
    avis = sorted(media.glob("*.avi")) if media.is_dir() else []
    summary = {
        "generated": datetime.now(timezone.utc).isoformat(),
        "bucket": bucket,
        "config_sha256": digest,
        "n_avis": len(avis),
        "files": [],
    }
    if not avis:
        summary["error"] = f"no avis under {media}"
        out_dir.mkdir(parents=True, exist_ok=True)
        (out_dir / "RUN_SUMMARY.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")
        return summary

    weights = resolve_weights(cfg)
    model = YOLO(weights)
    for i, avi in enumerate(avis):
        # Skip if CSV already written for this camera in this bucket
        cam_guess = avi.stem
        if cam_guess.startswith("Export__"):
            for day in ("Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"):
                if f"_{day}" in cam_guess:
                    cam_guess = cam_guess[len("Export__") :].split(f"_{day}")[0]
                    break
        safe = "".join(c if c.isalnum() or c in "-_" else "_" for c in cam_guess)
        existing = out_dir / f"2022_{slug}_{safe}.csv"
        if existing.is_file() and existing.stat().st_size > 50:
            print(f"[{bucket}] Skip existing {existing.name}", flush=True)
            summary["files"].append(
                {
                    "path": str(avi),
                    "bucket": bucket,
                    "camera": cam_guess,
                    "csv": str(existing),
                    "skipped": True,
                }
            )
            continue
        if guard(f"4-{slug}-avi-{i}", notes=avi.name) == 90:
            summary["stopped"] = avi.name
            break
        print(f"[{bucket}] Processing {avi.name} ...", flush=True)
        meta = process_avi(avi, cfg, model, out_dir, overlay_dir, bucket)
        summary["files"].append(meta)
        time.sleep(2)
        model = YOLO(weights)

    walls = [f.get("wall_seconds", 0) for f in summary["files"] if "wall_seconds" in f]
    summary["wall_seconds_total"] = round(sum(walls), 1)
    summary["wall_seconds_avg"] = round(sum(walls) / len(walls), 1) if walls else 0
    out_dir.mkdir(parents=True, exist_ok=True)
    (out_dir / "RUN_SUMMARY.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")
    print(json.dumps({"bucket": bucket, "files": len(summary["files"]), "wall_total": summary["wall_seconds_total"]}, indent=2))
    return summary


def main() -> int:
    if guard("4-pipeline-start") == 90:
        return 90
    cfg = yaml.safe_load(CFG_PATH.read_text(encoding="utf-8"))
    digest = sha256_file(CFG_PATH)
    (ROOT / "config" / "config.yaml.sha256").write_text(digest + "\n", encoding="utf-8")

    run_all = os.environ.get("RUN_ALL_SHORT", "").strip() in ("1", "true", "yes")
    run_remaining = os.environ.get("RUN_REMAINING", "").strip() in ("1", "true", "yes")
    if run_remaining:
        buckets = [b for b in SHORT_BUCKETS if not bucket_complete(b)]
        print(f"RUN_REMAINING: will process {buckets}", flush=True)
    elif run_all:
        buckets = list(SHORT_BUCKETS)
    else:
        buckets = [os.environ.get("BUCKET", "5 min").strip() or "5 min"]

    if not buckets:
        print("Nothing to do — all target buckets complete.", flush=True)
        master = {
            "generated": datetime.now(timezone.utc).isoformat(),
            "config_sha256": digest,
            "buckets": [],
            "note": "all_complete",
        }
        for b in SHORT_BUCKETS:
            slug = bucket_slug(b)
            sp = ROOT / "artifacts" / "counts_by_bucket" / slug / "RUN_SUMMARY.json"
            if sp.is_file():
                master["buckets"].append(json.loads(sp.read_text(encoding="utf-8")))
        out = ROOT / "artifacts" / "counts_by_bucket" / "MULTI_BUCKET_SUMMARY.json"
        out.write_text(json.dumps(master, indent=2), encoding="utf-8")
        return 0

    master = {
        "generated": datetime.now(timezone.utc).isoformat(),
        "config_sha256": digest,
        "buckets": [],
    }
    t0 = time.time()
    for b in buckets:
        if guard(f"4-bucket-{bucket_slug(b)}", notes=b) == 90:
            master["stopped_before"] = b
            break
        master["buckets"].append(run_bucket(b, cfg, digest))

    master["wall_seconds_total"] = round(time.time() - t0, 1)
    out = ROOT / "artifacts" / "counts_by_bucket" / "MULTI_BUCKET_SUMMARY.json"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(master, indent=2), encoding="utf-8")
    print(json.dumps({"done_buckets": len(master["buckets"]), "wall_total": master["wall_seconds_total"]}, indent=2))
    guard("4-pipeline-end")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
