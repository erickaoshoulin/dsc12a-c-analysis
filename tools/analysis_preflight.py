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

# Keep this lookup in the receipt-producing tool as well as in run.sh.  A
# caller that invokes the preflight directly must get the same answer as the
# pipeline wrapper, especially for Homebrew's LLVM tools which are often not
# on PATH on macOS.
HOMEBREW_TOOL_PATHS = {
    "clang++": (
        "/opt/homebrew/opt/llvm/bin/clang++",
        "/usr/local/opt/llvm/bin/clang++",
    ),
    "llvm-config": (
        "/opt/homebrew/opt/llvm/bin/llvm-config",
        "/usr/local/opt/llvm/bin/llvm-config",
    ),
}

OPAM_EXECUTABLE_PATHS = (
    "/opt/homebrew/bin/opam",
    "/usr/local/bin/opam",
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", required=True, type=pathlib.Path)
    for name in REQUIRED_TOOLS:
        parser.add_argument(f"--{name}", dest=name.replace("-", "_"), default="")
    return parser.parse_args()


def _executable_from_output(output: str) -> str | None:
    for line in reversed((output or "").splitlines()):
        candidate = pathlib.Path(line.strip()).expanduser()
        if candidate.is_file() and os.access(candidate, os.X_OK):
            return str(candidate.resolve())
    return None


def resolve_opam_executable(tool: str) -> str | None:
    """Find an Opam-managed executable without changing the active switch."""
    switch_prefix = os.environ.get("OPAM_SWITCH_PREFIX", "").strip()
    prefixes: list[pathlib.Path] = []
    if switch_prefix:
        prefixes.append(pathlib.Path(switch_prefix).expanduser())

    opam_root = pathlib.Path.home() / ".opam"
    default_switch = opam_root / "default"
    prefixes.append(default_switch)
    if opam_root.is_dir():
        prefixes.extend(sorted(path for path in opam_root.iterdir() if path.is_dir()))

    seen: set[pathlib.Path] = set()
    for prefix in prefixes:
        if prefix in seen:
            continue
        seen.add(prefix)
        for candidate in (prefix / "bin" / tool, prefix / "_opam" / "bin" / tool):
            if candidate.is_file() and os.access(candidate, os.X_OK):
                return str(candidate.resolve())

    opam = shutil.which("opam")
    if not opam:
        for candidate in OPAM_EXECUTABLE_PATHS:
            if pathlib.Path(candidate).is_file() and os.access(candidate, os.X_OK):
                opam = candidate
                break
    if not opam:
        return None

    commands = [[opam, "exec", "--", "which", tool]]
    try:
        switches = subprocess.run(
            [opam, "switch", "list", "--short"],
            stdout=subprocess.PIPE,
            stderr=subprocess.DEVNULL,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=15,
            check=False,
        ).stdout
    except (OSError, subprocess.TimeoutExpired):
        switches = ""
    for switch in sorted({line.strip() for line in switches.splitlines() if line.strip()}):
        commands.append([opam, "exec", f"--switch={switch}", "--", "which", tool])

    for command in commands:
        try:
            result = subprocess.run(
                command,
                stdout=subprocess.PIPE,
                stderr=subprocess.DEVNULL,
                text=True,
                encoding="utf-8",
                errors="replace",
                timeout=15,
                check=False,
            )
        except (OSError, subprocess.TimeoutExpired):
            continue
        resolved = _executable_from_output(result.stdout)
        if resolved:
            return resolved
    return None


def resolve_executable(raw: str, tool: str) -> tuple[str | None, str | None]:
    value = str(raw or "").strip()
    if value and ("/" in value or "\\" in value):
        path = pathlib.Path(value).expanduser()
        if path.is_file() and os.access(path, os.X_OK):
            return str(path.resolve()), "configured"
        return None, None

    # Match run.sh: standard Homebrew locations take precedence over PATH for
    # LLVM tools, while an explicitly configured absolute path remains the
    # authority.  The fallback list is data, not a function-selection input.
    if tool in HOMEBREW_TOOL_PATHS and value in {"", tool}:
        for candidate in HOMEBREW_TOOL_PATHS[tool]:
            path = pathlib.Path(candidate)
            if path.is_file() and os.access(path, os.X_OK):
                return str(path.resolve()), "homebrew"

    lookup = value or tool
    found = shutil.which(lookup)
    if found:
        return str(pathlib.Path(found).resolve()), "PATH"
    if tool == "frama-c" and value in {"", tool}:
        found = resolve_opam_executable(tool)
        if found:
            return found, "opam"
    return None, None


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
        resolved, resolution = resolve_executable(requested, name)
        entry: dict[str, Any] = {
            "requested": requested or None,
            "resolved": resolved,
            "status": "PASS" if resolved else "MISSING",
        }
        if resolved:
            entry["resolution"] = resolution
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
