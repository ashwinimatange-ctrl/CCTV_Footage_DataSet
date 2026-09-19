#!/usr/bin/env python3
"""Gate0: probe whether Verint AVI is decodable."""
from __future__ import annotations

import json
import os
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

import cv2

ROOT = Path(os.environ.get("WORK_ROOT", "/work"))
FOOTAGE = Path(os.environ.get("FOOTAGE_ROOT", "/footage"))
OUT = ROOT / "01-discovery" / "CODEC_PROBE.json"


def main() -> int:
    subprocess.run(
        [sys.executable, str(ROOT / "scripts" / "resource_guard.py"), "--phase", "gate0", "--enforce"],
        check=False,
    )
    avis = sorted((FOOTAGE / "5 min" / "ExportedMedia").glob("*.avi"))
    report = {
        "generated": datetime.now(timezone.utc).isoformat(),
        "avi_count": len(avis),
        "results": [],
        "pass": False,
    }
    if not avis:
        report["error"] = "no AVI found under /footage/5 min/ExportedMedia"
        OUT.write_text(json.dumps(report, indent=2), encoding="utf-8")
        print(json.dumps(report, indent=2))
        return 2

    sample = avis[0]
    entry = {"path": str(sample), "size_bytes": sample.stat().st_size}
    cap = cv2.VideoCapture(str(sample))
    entry["opencv_opened"] = bool(cap.isOpened())
    ok, frame = cap.read() if cap.isOpened() else (False, None)
    entry["frame_ok"] = bool(ok)
    if ok and frame is not None:
        entry["height"], entry["width"] = int(frame.shape[0]), int(frame.shape[1])
        entry["fps"] = float(cap.get(cv2.CAP_PROP_FPS) or 0)
        entry["frame_count"] = int(cap.get(cv2.CAP_PROP_FRAME_COUNT) or 0)
        # save one preview
        preview = ROOT / "artifacts" / "frames" / "probe_frame.jpg"
        preview.parent.mkdir(parents=True, exist_ok=True)
        cv2.imwrite(str(preview), frame)
        entry["preview"] = str(preview)
    cap.release()

    # ffmpeg probe as secondary
    try:
        p = subprocess.run(
            [
                "ffprobe",
                "-v",
                "error",
                "-show_entries",
                "stream=codec_name,width,height,r_frame_rate",
                "-of",
                "json",
                str(sample),
            ],
            capture_output=True,
            text=True,
            timeout=60,
        )
        entry["ffprobe_rc"] = p.returncode
        if p.returncode == 0:
            entry["ffprobe"] = json.loads(p.stdout)
    except Exception as exc:  # noqa: BLE001
        entry["ffprobe_error"] = repr(exc)

    report["results"].append(entry)
    report["pass"] = bool(entry.get("frame_ok"))
    OUT.write_text(json.dumps(report, indent=2), encoding="utf-8")
    md = ROOT / "01-discovery" / "CODEC_PROBE.md"
    md.write_text(
        f"# Codec probe\n\nPass: **{report['pass']}**\n\n```json\n{json.dumps(report, indent=2)}\n```\n",
        encoding="utf-8",
    )
    print(json.dumps(report, indent=2))
    return 0 if report["pass"] else 3


if __name__ == "__main__":
    raise SystemExit(main())
