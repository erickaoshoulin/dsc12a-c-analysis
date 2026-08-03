#!/usr/bin/env python3
"""Detect generated or transient material that must stay off the handoff repo.

The repository is the compact contract/report handoff.  Candidate RTL, C
oracles, harnesses, vectors, and build logs belong in the durable regression
root instead.  This module is deliberately path-based: it never selects a
function or infers a verification result from a filename.
"""

from __future__ import annotations

import argparse
import json
import subprocess
from pathlib import Path, PurePosixPath
from typing import Any, Iterable


GENERATED_ARTIFACT_DIRECTORIES = frozenset(
    {
        "candidate-build",
        "generated",
        "harness",
        "rtl",
    }
)
GENERATED_ARTIFACT_FILES = frozenset(
    {
        "oracle.c",
        "shadow_replacement_wrapper.c",
        "vector_generator.py",
    }
)
TRANSIENT_SUFFIXES = frozenset(
    {
        ".fst",
        ".log",
        ".vcd",
        ".wlf",
    }
)


def classify_path(raw_path: str | Path) -> str | None:
    """Return a stable rule id when a tracked path violates handoff policy."""

    path = PurePosixPath(str(raw_path).replace("\\", "/"))
    parts = path.parts
    if not parts:
        return None
    if "obj_dir" in parts:
        return "obj_dir"
    if "vectors" in parts:
        return "vectors"
    if path.suffix.lower() in TRANSIENT_SUFFIXES:
        return "transient_log_or_waveform"
    if parts[0] != "artifacts":
        return None
    if any(directory in parts[1:-1] for directory in GENERATED_ARTIFACT_DIRECTORIES):
        return "generated_candidate_material"
    if path.name in GENERATED_ARTIFACT_FILES:
        return "generated_candidate_material"
    return None


def scan_paths(paths: Iterable[str | Path]) -> list[dict[str, str]]:
    findings = []
    for raw_path in sorted((str(path) for path in paths)):
        rule = classify_path(raw_path)
        if rule:
            findings.append({"path": raw_path, "rule": rule})
    return findings


def tracked_paths(repo: Path) -> tuple[list[str], str | None]:
    try:
        result = subprocess.run(
            ["git", "-C", str(repo), "ls-files", "-z"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=False,
        )
    except OSError as error:
        return [], str(error)
    if result.returncode != 0:
        message = result.stderr.decode("utf-8", errors="replace").strip()
        return [], message or f"git ls-files exited {result.returncode}"
    return [item for item in result.stdout.decode("utf-8", errors="replace").split("\0") if item], None


def check_repo(repo: Path) -> dict[str, Any]:
    repo = repo.resolve()
    paths, error = tracked_paths(repo)
    if error:
        return {
            "schema_version": 1,
            "status": "NOT_A_GIT_REPO",
            "repo": str(repo),
            "tracked_count": 0,
            "forbidden_count": 0,
            "forbidden": [],
            "error": error,
        }
    findings = scan_paths(paths)
    return {
        "schema_version": 1,
        "status": "PASS" if not findings else "FAIL",
        "repo": str(repo),
        "tracked_count": len(paths),
        "forbidden_count": len(findings),
        "forbidden": findings,
        "rules": {
            "generated_candidate_material": "artifacts generated candidates, RTL, oracles, harnesses, and vector generators",
            "transient_log_or_waveform": "tracked logs and simulator waveforms",
            "obj_dir": "simulator build directories",
            "vectors": "tracked vector directories",
        },
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers(dest="command", required=True)
    check = subparsers.add_parser("check")
    check.add_argument("--repo", type=Path, default=Path.cwd())
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    if args.command != "check":
        raise ValueError(args.command)
    result = check_repo(args.repo)
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0 if result["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
