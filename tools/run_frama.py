#!/usr/bin/env python3
"""Run focused Eva and From analyses and retain their raw deterministic logs."""

from __future__ import annotations

import argparse
import json
import pathlib
import shlex
import subprocess
import sys


TARGETS = (
    "Qp2Qlevel",
    "MapQpToQlevel",
    "QuantizeResidual",
    "FindResidualSize",
    "SampToLineBuf",
    "MaxResidualSize",
    "GetQpAdjPredSize",
)

# These command-line/platform glue units have host-specific headers or a
# dynamic DPX layout that Frama-C's parser configuration cannot consume, and
# none of the focused targets depends on them.
# Clang still analyzes every compile_commands.json entry for the complete
# structural facts; this exclusion is only for the focused Eva/From scope.
FRAMA_EXCLUDED_SOURCES = {"cmd_parse.c", "dpx.c", "hdr_dpx.c", "logging.c"}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--frama-c", required=True)
    parser.add_argument("--compile-commands", required=True, type=pathlib.Path)
    parser.add_argument("--source-dir", required=True, type=pathlib.Path)
    parser.add_argument("--output-dir", required=True, type=pathlib.Path)
    parser.add_argument("--timeout", required=True, type=int)
    return parser.parse_args()


def command_entries(compdb: pathlib.Path) -> list[dict]:
    entries = json.loads(compdb.read_text(encoding="utf-8"))
    return sorted(entries, key=lambda entry: str(pathlib.Path(entry["file"]).resolve()))


def command_sources(entries: list[dict]) -> list[str]:
    return sorted(
        {
            str(pathlib.Path(entry["file"]).resolve())
            for entry in entries
            if pathlib.Path(entry["file"]).name not in FRAMA_EXCLUDED_SOURCES
        }
    )


def cpp_extra_args(entries: list[dict]) -> str:
    """Reuse preprocessing flags from compile_commands.json for Frama-C."""
    if not entries:
        return ""
    entry = entries[0]
    if "arguments" in entry:
        arguments = list(entry["arguments"])
    else:
        arguments = shlex.split(entry.get("command", ""))
    source = str(pathlib.Path(entry["file"]).resolve())
    flags = []
    skip_next = False
    for index, argument in enumerate(arguments):
        if skip_next:
            skip_next = False
            continue
        if index == 0 or argument in {source, entry.get("file"), "-c", "-fsyntax-only"}:
            continue
        if argument == "-D__APPLE__":
            # Frama-C's bundled libc has malloc.h, but not Darwin's
            # sys/malloc.h. The only source unit needing __APPLE__ here is
            # cmd_parse.c, which is intentionally outside focused scope.
            continue
        if argument in {"-o", "--output", "-resource-dir", "-isysroot", "-isystem"}:
            skip_next = True
            continue
        if argument.startswith("-o") and argument != "-O0":
            continue
        flags.append(argument)
    return shlex.join(flags)


def run_one(command: list[str], output: pathlib.Path, timeout: int) -> int:
    try:
        completed = subprocess.run(
            command,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=timeout,
            check=False,
        )
    except subprocess.TimeoutExpired as exc:
        output.write_text(
            (exc.stdout or "") + f"\n[driver] timeout after {timeout}s\n",
            encoding="utf-8",
        )
        return 124
    output.write_text(completed.stdout or "", encoding="utf-8")
    return completed.returncode


def main() -> int:
    args = parse_args()
    source_dir = args.source_dir.resolve()
    output_dir = args.output_dir.resolve()
    output_dir.mkdir(parents=True, exist_ok=True)
    entries = command_entries(args.compile_commands.resolve())
    sources = command_sources(entries)
    cpp_extra = cpp_extra_args(entries)

    manifest = {
        "targets": list(TARGETS),
        "excluded_sources": sorted(FRAMA_EXCLUDED_SOURCES),
        "eva": {},
        "from": {},
    }
    for target in TARGETS:
        eva_log = output_dir / f"{target}.eva.log"
        eva_command = [
            args.frama_c,
            *sources,
            "-main",
            target,
            "-lib-entry",
            "-eva",
            "-eva-slevel",
            "20",
            "-warn-signed-overflow",
            "-cpp-extra-args=" + cpp_extra,
        ]
        eva_rc = run_one(eva_command, eva_log, args.timeout)
        manifest["eva"][target] = {
            "returncode": eva_rc,
            "log": eva_log.name,
        }
        if eva_rc != 0:
            (output_dir / "manifest.json").write_text(
                json.dumps(manifest, indent=2, sort_keys=True) + "\n",
                encoding="utf-8",
            )
            print(f"Eva failed for {target}; see {eva_log}", file=sys.stderr)
            return eva_rc or 1

        from_log = output_dir / f"{target}.from.log"
        from_command = [
            args.frama_c,
            *sources,
            "-main",
            target,
            "-lib-entry",
            "-deps",
            "-calldeps",
            "-cpp-extra-args=" + cpp_extra,
        ]
        from_rc = run_one(from_command, from_log, args.timeout)
        manifest["from"][target] = {
            "returncode": from_rc,
            "log": from_log.name,
        }
        if from_rc != 0:
            (output_dir / "manifest.json").write_text(
                json.dumps(manifest, indent=2, sort_keys=True) + "\n",
                encoding="utf-8",
            )
            print(f"From failed for {target}; see {from_log}", file=sys.stderr)
            return from_rc or 1

    (output_dir / "manifest.json").write_text(
        json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
