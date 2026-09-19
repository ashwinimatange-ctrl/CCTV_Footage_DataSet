#!/usr/bin/env python3
"""Resume incomplete short-bucket pipeline (skips finished buckets)."""
from __future__ import annotations

import os
import sys
from pathlib import Path

os.environ["RUN_REMAINING"] = "1"
sys.path.insert(0, str(Path(__file__).resolve().parent))

from run_pipeline import main

if __name__ == "__main__":
    raise SystemExit(main())
