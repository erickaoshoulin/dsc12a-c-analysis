#!/usr/bin/env python3
"""Clean-build and smoke-test a copied DSC C model.

The original model is treated as read-only.  Large derived sibling trees are
excluded from the temporary copy because they are not required by source/ or
bittrue_smoke/ and can be tens of gigabytes.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import pathlib
import re
import shutil
import subprocess
import sys
import time
from typing import Any


COPY_EXCLUDES = {
    ".git",
    "dsc-rs",
    "operator_bittrue",
    "target",
    "build",
    "out",
    "__pycache__",
}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--model-root", required=True, type=pathlib.Path)
    parser.add_argument("--output-dir", required=True, type=pathlib.Path)
    parser.add_argument("--work-dir", required=True, type=pathlib.Path)
    parser.add_argument("--timeout", required=True, type=int)
    return parser.parse_args()


def sha256_file(path: pathlib.Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def command_text(command: list[str], copy_root: pathlib.Path) -> list[str]:
    return [item.replace(str(copy_root), "<build-copy>") for item in command]


def run_command(
    command: list[str], cwd: pathlib.Path, log_path: pathlib.Path, timeout: int
) -> dict[str, Any]:
    started = time.monotonic()
    try:
        completed = subprocess.run(
            command,
            cwd=cwd,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=timeout,
            check=False,
        )
        output = completed.stdout or ""
        result = {
            "status": "PASS" if completed.returncode == 0 else "FAIL",
            "returncode": completed.returncode,
            "duration_seconds": round(time.monotonic() - started, 3),
            "output": output,
        }
    except subprocess.TimeoutExpired as exc:
        output = (exc.stdout or "") + f"\n[driver] timeout after {timeout}s\n"
        result = {
            "status": "TIMEOUT",
            "returncode": 124,
            "duration_seconds": round(time.monotonic() - started, 3),
            "output": output,
        }
    except OSError as exc:
        result = {
            "status": "ERROR",
            "returncode": 127,
            "duration_seconds": round(time.monotonic() - started, 3),
            "output": str(exc),
        }
    log_path.write_text(result["output"], encoding="utf-8")
    result.pop("output")
    return result


def copy_model(model_root: pathlib.Path, copy_root: pathlib.Path) -> list[str]:
    excluded: list[str] = []

    def ignore(current: str, names: list[str]) -> set[str]:
        ignored = {name for name in names if name in COPY_EXCLUDES}
        excluded.extend(
            str(pathlib.Path(current, name).relative_to(model_root)) for name in sorted(ignored)
        )
        return ignored

    shutil.copytree(model_root, copy_root, symlinks=True, ignore=ignore)
    (copy_root / "bittrue_smoke" / "out").mkdir(parents=True, exist_ok=True)
    return sorted(set(excluded))


def tool_version(command: str) -> str:
    path = shutil.which(command) or command
    try:
        completed = subprocess.run(
            [path, "--version"],
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=20,
            check=False,
        )
        return (completed.stdout or "").splitlines()[0].strip()
    except (OSError, subprocess.TimeoutExpired):
        return "UNKNOWN"


def warning_lines(log_path: pathlib.Path) -> list[str]:
    if not log_path.is_file():
        return []
    return [
        line.strip()
        for line in log_path.read_text(encoding="utf-8", errors="replace").splitlines()
        if re.search(r"\bwarning\b", line, re.I)
    ]


def expected_smoke_hash(script: pathlib.Path) -> str:
    text = script.read_text(encoding="utf-8", errors="replace")
    match = re.search(r'expected_hash="([0-9a-f]{64})"', text)
    return match.group(1) if match else "UNKNOWN"


def smoke_outputs(copy_root: pathlib.Path) -> list[dict[str, Any]]:
    result = []
    output_dir = copy_root / "bittrue_smoke" / "out"
    for path in sorted(output_dir.glob("*")):
        if not path.is_file():
            continue
        result.append(
            {
                "path": path.relative_to(copy_root).as_posix(),
                "size_bytes": path.stat().st_size,
                "sha256": sha256_file(path),
            }
        )
    return result


def binary_symbols(binary: pathlib.Path) -> dict[str, Any]:
    nm = shutil.which("nm")
    if not nm or not binary.is_file():
        return {"status": "UNKNOWN", "entry_symbols": [], "raw": ""}
    try:
        completed = subprocess.run(
            [nm, "-g", str(binary)],
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=30,
            check=False,
        )
    except (OSError, subprocess.TimeoutExpired) as exc:
        return {"status": "ERROR", "entry_symbols": [], "raw": str(exc)}
    symbols = []
    for line in completed.stdout.splitlines():
        fields = line.split()
        if fields and fields[-1].lstrip("_") == "main":
            symbols.append("main")
    return {
        "status": "PASS" if completed.returncode == 0 else "FAIL",
        "entry_symbols": sorted(set(symbols)),
        "raw": completed.stdout,
    }


def main() -> int:
    args = parse_args()
    model_root = args.model_root.resolve()
    output_dir = args.output_dir.resolve()
    work_dir = args.work_dir.resolve()
    output_dir.mkdir(parents=True, exist_ok=True)
    work_dir.mkdir(parents=True, exist_ok=True)
    copy_root = work_dir / "model"
    receipt: dict[str, Any] = {
        "schema_version": 2,
        "status": "INFRASTRUCTURE_FAILURE",
        "do_not_edit": True,
        "model_root": str(model_root),
        "copy_excludes": sorted(COPY_EXCLUDES),
        "commands": [],
        "warnings": [],
        "tool_versions": {
            "make": tool_version("make"),
            "cc": tool_version(os.environ.get("CC", "cc")),
            "nm": tool_version("nm"),
        },
    }
    receipt_path = output_dir / "build-receipt.json"

    try:
        if not model_root.is_dir():
            raise RuntimeError(f"model root does not exist: {model_root}")
        excluded = copy_model(model_root, copy_root)
        receipt["copy_excluded_paths"] = excluded
        source_dir = copy_root / "source"
        binary = source_dir / "dsc"
        clean_command = ["make", "-j1", "-C", str(source_dir), "clean"]
        clean_result = run_command(clean_command, copy_root, output_dir / "make-clean.log", args.timeout)
        receipt["commands"].append(
            {"command": command_text(clean_command, copy_root), **clean_result, "log": "make-clean.log"}
        )
        if clean_result["status"] != "PASS":
            receipt["failure_reason"] = "clean build command failed"
            return write_receipt(receipt_path, receipt)

        build_command = ["make", "-j1", "-C", str(source_dir)]
        build_result = run_command(build_command, copy_root, output_dir / "make-build.log", args.timeout)
        receipt["commands"].append(
            {"command": command_text(build_command, copy_root), **build_result, "log": "make-build.log"}
        )
        receipt["warnings"] = warning_lines(output_dir / "make-build.log")
        if build_result["status"] != "PASS" or not binary.is_file():
            receipt["failure_reason"] = "C build failed or source/dsc was not produced"
            return write_receipt(receipt_path, receipt)

        smoke_script = copy_root / "bittrue_smoke" / "run_c_baseline.sh"
        if smoke_script.is_file():
            smoke_command = [str(smoke_script)]
            smoke_result = run_command(smoke_command, copy_root, output_dir / "smoke.log", args.timeout)
            receipt["commands"].append(
                {"command": ["<build-copy>/bittrue_smoke/run_c_baseline.sh"], **smoke_result, "log": "smoke.log"}
            )
            receipt["smoke"] = {
                "mode": "bittrue_smoke/run_c_baseline.sh",
                "expected_hash": expected_smoke_hash(smoke_script),
                "outputs": smoke_outputs(copy_root),
            }
            if smoke_result["status"] != "PASS":
                receipt["failure_reason"] = "bittrue C smoke script failed or golden hash mismatched"
                return write_receipt(receipt_path, receipt)
        else:
            help_command = [str(binary), "-help"]
            help_result = run_command(help_command, copy_root, output_dir / "smoke.log", args.timeout)
            receipt["commands"].append(
                {"command": ["<build-copy>/source/dsc", "-help"], **help_result, "log": "smoke.log"}
            )
            receipt["smoke"] = {"mode": "source/dsc -help", "outputs": []}
            if help_result["status"] != "PASS":
                receipt["failure_reason"] = "safe C help smoke command failed"
                return write_receipt(receipt_path, receipt)

        symbols = binary_symbols(binary)
        receipt["binary"] = {
            "path": "source/dsc",
            "size_bytes": binary.stat().st_size,
            "sha256": sha256_file(binary),
            "symbols": symbols,
        }
        receipt["status"] = "PASS"
        return write_receipt(receipt_path, receipt)
    except (OSError, RuntimeError, shutil.Error) as exc:
        receipt["failure_reason"] = str(exc)
        return write_receipt(receipt_path, receipt)


def write_receipt(path: pathlib.Path, receipt: dict[str, Any]) -> int:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(receipt, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    if receipt["status"] != "PASS":
        print(receipt.get("failure_reason", "build failed"), file=sys.stderr)
        return 1
    print("C model clean build and smoke PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
