#!/usr/bin/env python3
"""Run every compiler-front-end command in a compilation database.

This is a compiler check, not a C parser. The command lines are consumed
exactly as emitted in compile_commands.json, with only the working directory
selected from the database entry.
"""

from __future__ import annotations

import argparse
import json
import pathlib
import shlex
import subprocess
import sys
from typing import Any


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--compile-commands", required=True, type=pathlib.Path)
    parser.add_argument("--output", required=True, type=pathlib.Path)
    parser.add_argument("--timeout", required=True, type=int)
    return parser.parse_args()


def command_for(entry: dict[str, Any]) -> list[str]:
    if "arguments" in entry:
        return list(entry["arguments"])
    return shlex.split(entry.get("command", ""))


def write_receipt(path: pathlib.Path, receipt: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(receipt, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )


def main() -> int:
    args = parse_args()
    entries = json.loads(args.compile_commands.resolve().read_text(encoding="utf-8"))
    entries = sorted(entries, key=lambda entry: str(pathlib.Path(entry["file"]).resolve()))
    results = []
    for entry in entries:
        source = pathlib.Path(entry["file"]).resolve()
        directory = pathlib.Path(entry.get("directory", source.parent)).resolve()
        command = command_for(entry)
        result: dict[str, Any] = {
            "file": str(source),
            "directory": str(directory),
            "command": command,
        }
        try:
            completed = subprocess.run(
                command,
                cwd=directory,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                encoding="utf-8",
                errors="replace",
                timeout=args.timeout,
                check=False,
            )
        except subprocess.TimeoutExpired as exc:
            result.update(
                {
                    "status": "TIMEOUT",
                    "returncode": 124,
                    "output": exc.stdout or "",
                }
            )
        except OSError as exc:
            result.update(
                {
                    "status": "ERROR",
                    "returncode": 127,
                    "output": str(exc),
                }
            )
        else:
            result["status"] = "PASS" if completed.returncode == 0 else "FAIL"
            result["returncode"] = completed.returncode
            if completed.stdout:
                result["output"] = completed.stdout
        results.append(result)

    failed = [item for item in results if item["status"] != "PASS"]
    receipt = {
        "schema_version": 1,
        "status": "PASS" if not failed else "FAIL",
        "compiler_command_count": len(results),
        "results": results,
    }
    write_receipt(args.output.resolve(), receipt)
    if failed:
        for item in failed:
            print(f"C compiler check failed for {item['file']}: {item['status']}", file=sys.stderr)
        return 1
    print(f"C compiler check passed for {len(results)} translation units")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
