#!/usr/bin/env python3
"""Run one analysis command with a deterministic timeout and log."""

from __future__ import annotations

import argparse
import pathlib
import subprocess
import sys


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--timeout", required=True, type=int)
    parser.add_argument("--log", required=True, type=pathlib.Path)
    parser.add_argument("command", nargs=argparse.REMAINDER)
    args = parser.parse_args()
    command = args.command
    if command and command[0] == "--":
        command = command[1:]
    if not command:
        print("missing command", file=sys.stderr)
        return 2
    try:
        result = subprocess.run(
            command,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=args.timeout,
            check=False,
        )
    except subprocess.TimeoutExpired as exc:
        args.log.write_text(
            (exc.stdout or "") + f"\n[driver] timeout after {args.timeout}s\n",
            encoding="utf-8",
        )
        return 124
    args.log.write_text(result.stdout or "", encoding="utf-8")
    return result.returncode


if __name__ == "__main__":
    raise SystemExit(main())
