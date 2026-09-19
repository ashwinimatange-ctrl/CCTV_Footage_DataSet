#!/usr/bin/env python3
"""Resource guard: soft 85% / hard 90% of cgroup or host."""
from __future__ import annotations

import argparse
import os
import time
from datetime import datetime, timezone
from pathlib import Path

import psutil

ROOT = Path(os.environ.get("WORK_ROOT", "/work"))
LOG = ROOT / "logs" / "resource.log"
MEM_BUDGET_GB = float(os.environ.get("MEM_BUDGET_GB", "40"))


def mem_pct_of_budget() -> float:
    used = psutil.virtual_memory().used / (1024**3)
    return 100.0 * used / MEM_BUDGET_GB


def cpu_pct() -> float:
    return float(psutil.cpu_percent(interval=0.3))


def append(phase: str, cpu: float, ram: float, action: str, notes: str) -> None:
    LOG.parent.mkdir(parents=True, exist_ok=True)
    ts = datetime.now(timezone.utc).isoformat()
    with LOG.open("a", encoding="utf-8") as f:
        f.write(
            f"Timestamp: {ts} | Phase: {phase} | CPU %: {cpu:.1f} | "
            f"RAM % of 40g budget: {ram:.1f} | Action: {action} | Notes: {notes}\n"
        )


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--phase", default="check")
    ap.add_argument("--enforce", action="store_true")
    ap.add_argument("--notes", default="")
    args = ap.parse_args()
    cpu = cpu_pct()
    ram = mem_pct_of_budget()
    action = "none"
    code = 0
    if cpu >= 90 or ram >= 90:
        action = "HARD_STOP"
        code = 90
    elif cpu >= 85 or ram >= 85:
        action = "SOFT_THROTTLE"
        time.sleep(5)
    append(args.phase, cpu, ram, action, args.notes)
    if args.enforce and code == 90:
        return 90
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
