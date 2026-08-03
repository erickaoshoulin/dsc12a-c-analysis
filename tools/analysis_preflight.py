#!/usr/bin/env python3
"""Record the deterministic analysis-tool preflight.

The C build gate is intentionally separate from the static-analysis gate.  A
preflight receipt makes a missing Frama-C/LLVM tool visible to the dashboard
before run.sh clears any derived facts.  This module never selects a function
and never infers verification status from a source name.
"""

from __future__ import annotations

import argparse
import json
import os
import pathlib
import shutil
import subprocess
from typing import Any


REQUIRED_TOOLS = ("python", "clang", "clang++", "frama-c", "llvm-config", "cmake")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", required=True, type=pathlib.Path)
    for name in REQUIRED_TOOLS:
        parser.add_argument(f"--{name}", dest=name.replace("-", "_"), default="")
    return parser.parse_args()


def resolve_executable(raw: str) -> str | None:
    value = str(raw or "").strip()
    if not value:
        return None
    found = shutil.which(value)
    if found:
        return str(pathlib.Path(found).resolve())
    path = pathlib.Path(value).expanduser()
    if path.is_file() and os.access(path, os.X_OK):
        return str(path.resolve())
    return None


def command_version(path: str, tool: str) -> str:
    option = "-version" if tool == "frama-c" else "--version"
    try:
        result = subprocess.run(
            [path, option],
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=15,
            check=False,
        )
    except (OSError, subprocess.TimeoutExpired) as error:
        return f"UNAVAILABLE: {error}"
    return (result.stdout or "").splitlines()[0].strip() or "UNKNOWN"


def build_receipt(args: argparse.Namespace) -> dict[str, Any]:
    tools: dict[str, dict[str, Any]] = {}
    missing: list[str] = []
    for name in REQUIRED_TOOLS:
        requested = str(getattr(args, name.replace("-", "_"), "") or "")
        resolved = resolve_executable(requested)
        entry: dict[str, Any] = {
            "requested": requested or None,
            "resolved": resolved,
            "status": "PASS" if resolved else "MISSING",
        }
        if resolved:
            entry["version"] = command_version(resolved, name)
        else:
            missing.append(name)
        tools[name] = entry
    status = "PASS" if not missing else "INFRASTRUCTURE_FAILURE"
    return {
        "schema_version": 1,
        "do_not_edit": True,
        "status": status,
        "required_tools": list(REQUIRED_TOOLS),
        "missing_tools": missing,
        "blockers": [f"missing tool: {name}" for name in missing],
        "tools": tools,
    }


def main() -> int:
    args = parse_args()
    receipt = build_receipt(args)
    output = args.output.resolve()
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(receipt, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(receipt, ensure_ascii=False, indent=2, sort_keys=True))
    return 0 if receipt["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
