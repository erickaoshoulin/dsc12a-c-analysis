#!/usr/bin/env python3
"""Forward the durable service's one-shot poll command."""

from __future__ import annotations

import pathlib
import subprocess
import sys


ROOT = pathlib.Path(__file__).resolve().parents[3]
raise SystemExit(subprocess.call([sys.executable, str(ROOT / "tools" / "regression.py"), "poll", "--once"]))
