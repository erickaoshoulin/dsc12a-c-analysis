#!/usr/bin/env python3
"""Create a deterministic compile_commands.json for the public DSC C model.

This is intentionally a build-database generator, not a C parser.  The
analysis tools consume the resulting compilation database and never infer
source structure from text.
"""

from __future__ import annotations

import argparse
import json
import os
import pathlib
import shutil
import subprocess
import sys
import tempfile


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--source-dir", required=True, type=pathlib.Path)
    parser.add_argument("--output", required=True, type=pathlib.Path)
    parser.add_argument("--compiler", default=None)
    parser.add_argument("--sysroot", default=None)
    parser.add_argument("--resource-dir", default=None)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    source_dir = args.source_dir.resolve()
    output = args.output.resolve()
    if not source_dir.is_dir():
        print(f"source directory does not exist: {source_dir}", file=sys.stderr)
        return 2

    compiler = args.compiler or os.environ.get("CLANG", "") or shutil.which("clang")
    if not compiler:
        print("clang is not installed", file=sys.stderr)
        return 3
    compiler = str(pathlib.Path(compiler).resolve())

    sysroot = args.sysroot or os.environ.get("DSC_SYSROOT", "")
    if sysroot:
        sysroot = str(pathlib.Path(sysroot).resolve())
        if not pathlib.Path(sysroot).is_dir():
            print(f"sysroot does not exist: {sysroot}", file=sys.stderr)
            return 5

    resource_dir = args.resource_dir or os.environ.get("DSC_RESOURCE_DIR", "")
    if not resource_dir:
        try:
            resource_dir = subprocess.run(
                [compiler, "-print-resource-dir"],
                check=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
            ).stdout.strip()
        except (OSError, subprocess.CalledProcessError):
            resource_dir = ""
    if resource_dir:
        resource_dir = str(pathlib.Path(resource_dir).resolve())
        if not pathlib.Path(resource_dir).is_dir():
            print(f"resource directory does not exist: {resource_dir}", file=sys.stderr)
            return 6

    platform_defines = ["-D__GNUC__=4"]
    if sys.platform == "darwin":
        platform_defines.append("-D__APPLE__")
    elif sys.platform.startswith("linux"):
        platform_defines.append("-D__linux__")

    source_files = sorted(
        path for path in source_dir.rglob("*.c") if path.is_file()
    )
    if not source_files:
        print(f"no C source files under {source_dir}", file=sys.stderr)
        return 4

    entries = []
    for source_file in source_files:
        arguments = [
            compiler,
            "-std=gnu99",
            "-O3",
            "-Wall",
            "-D_FILE_OFFSET_BITS=64",
            "-I",
            str(source_dir),
            *platform_defines,
        ]
        if sysroot:
            arguments.extend(["-isysroot", sysroot])
        if resource_dir:
            arguments.extend(["-resource-dir", resource_dir])
            resource_include = pathlib.Path(resource_dir) / "include"
            if resource_include.is_dir():
                arguments.extend(["-isystem", str(resource_include)])
        if sysroot:
            sdk_include = pathlib.Path(sysroot) / "usr" / "include"
            if sdk_include.is_dir():
                arguments.extend(["-isystem", str(sdk_include)])
        arguments.extend(
            [
                "-fsyntax-only",
                str(source_file.resolve()),
            ]
        )
        entries.append(
            {
                "directory": str(source_dir),
                "file": str(source_file.resolve()),
                "arguments": arguments,
            }
        )

    payload = {
        "schema_version": 1,
        "generator": "tools/generate_compile_commands.py",
        "entries": entries,
    }

    output.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.NamedTemporaryFile(
        "w", encoding="utf-8", dir=output.parent, delete=False
    ) as handle:
        json.dump(payload["entries"], handle, indent=2, sort_keys=True)
        handle.write("\n")
        temporary = pathlib.Path(handle.name)
    temporary.replace(output)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
