#!/usr/bin/env python3
"""Write the stable failure receipt used when infrastructure is unavailable."""

from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import json
import pathlib
import subprocess
import sys


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output-dir", required=True, type=pathlib.Path)
    parser.add_argument("--source-dir", required=True, type=pathlib.Path)
    parser.add_argument("--reason", required=True)
    parser.add_argument("--analysis-command", action="append", default=[])
    parser.add_argument("--clang-version", default="UNKNOWN")
    parser.add_argument("--frama-c-version", default="UNKNOWN")
    return parser.parse_args()


def source_revision(source_dir: pathlib.Path) -> str:
    try:
        completed = subprocess.run(
            ["git", "-C", str(source_dir.parent), "rev-parse", "HEAD"],
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.DEVNULL,
            check=False,
        )
        if completed.returncode == 0:
            return completed.stdout.strip()
    except OSError:
        pass
    return "UNKNOWN"


def source_hashes(source_dir: pathlib.Path) -> list[dict[str, str]]:
    result = []
    if not source_dir.is_dir():
        return result
    for path in sorted(
        p for p in source_dir.rglob("*") if p.is_file() and p.suffix in {".c", ".h"}
    ):
        digest = hashlib.sha256(path.read_bytes()).hexdigest()
        result.append({"path": path.relative_to(source_dir).as_posix(), "sha256": digest})
    return result


def main() -> int:
    args = parse_args()
    output_dir = args.output_dir.resolve()
    facts_dir = output_dir / "facts"
    reports_dir = output_dir / "reports"
    facts_dir.mkdir(parents=True, exist_ok=True)
    reports_dir.mkdir(parents=True, exist_ok=True)
    metadata = {
        "schema_version": 1,
        "status": "INFRASTRUCTURE_FAILURE",
        "failure_reason": args.reason,
        "dsc_source_revision": source_revision(args.source_dir.resolve()),
        "source_file_hashes": source_hashes(args.source_dir.resolve()),
        "compile_commands_sha256": "UNKNOWN",
        "clang_version": args.clang_version,
        "frama_c_version": args.frama_c_version,
        "analysis_command": sorted(args.analysis_command),
        "generated_timestamp": dt.datetime.now(dt.timezone.utc).isoformat(),
    }
    semantic = json.dumps(
        {key: value for key, value in metadata.items() if key != "generated_timestamp"},
        sort_keys=True,
        separators=(",", ":"),
    ).encode()
    metadata["semantic_hash"] = hashlib.sha256(semantic).hexdigest()
    summary = {"metadata": metadata, "facts": {}, "limitations": [args.reason]}
    empty_outputs = {
        "functions.json": {"functions": []},
        "callgraph.json": {"nodes": [], "edges": []},
        "field-access.json": {"fields": []},
        "loops.json": {"functions": []},
        "value-ranges.json": {"functions": []},
        "dependencies.json": {"functions": []},
    }
    for filename, payload in empty_outputs.items():
        (facts_dir / filename).write_text(
            json.dumps({"metadata": metadata, **payload}, indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
        )
    (output_dir / "summary.json").write_text(
        json.dumps(summary, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    failure_reports = {
        "function-summary.md": "# Function summary\n\nAnalysis did not run because infrastructure is unavailable.\n",
        "field-summary.md": "# Field summary\n\nAnalysis did not run because infrastructure is unavailable.\n",
        "candidate-functions.md": "# Candidate functions\n\nThe five-candidate gate is UNKNOWN because infrastructure is unavailable.\n",
    }
    for filename, contents in failure_reports.items():
        (reports_dir / filename).write_text(contents, encoding="utf-8")
    (reports_dir / "unresolved.md").write_text(
        "# Unresolved facts\n\n"
        "`INFRASTRUCTURE_FAILURE`\n\n"
        f"- {args.reason}\n"
        "- No LLM, C parser, fallback parser, or regenerated source was used.\n"
        "- The deterministic retry policy stopped after the allowed retry.\n",
        encoding="utf-8",
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
