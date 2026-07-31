#!/usr/bin/env python3
"""Emit a stable hash manifest for source immutability checks."""

from __future__ import annotations

import argparse
import hashlib
import json
import pathlib


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("source_dir", type=pathlib.Path)
    args = parser.parse_args()
    source_dir = args.source_dir.resolve()
    files = []
    if source_dir.is_dir():
        for path in sorted(
            p for p in source_dir.rglob("*") if p.is_file() and p.suffix in {".c", ".h"}
        ):
            files.append(
                {
                    "path": path.relative_to(source_dir).as_posix(),
                    "sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
                }
            )
    print(json.dumps(files, sort_keys=True, separators=(",", ":")))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
