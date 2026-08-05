#!/usr/bin/env python3
"""Build the discovered C model with LLVM source-based coverage enabled.

The upstream model is copied to a temporary directory.  Coverage is collected
from the existing bit-true smoke flow, then joined to the Clang-discovered
function inventory.  No source file in the discovered model is edited.
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

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from build_model import COPY_EXCLUDES, copy_model, expected_smoke_hash, smoke_outputs  # noqa: E402


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--model-root", required=True, type=pathlib.Path)
    parser.add_argument("--output-dir", required=True, type=pathlib.Path)
    parser.add_argument("--work-dir", required=True, type=pathlib.Path)
    parser.add_argument("--timeout", required=True, type=int)
    parser.add_argument("--functions", required=True, type=pathlib.Path)
    parser.add_argument("--candidates", required=True, type=pathlib.Path)
    parser.add_argument("--build-receipt", required=True, type=pathlib.Path)
    parser.add_argument(
        "--coverage-scripts",
        choices=("default", "all"),
        default=os.environ.get("DSC_COVERAGE_SCRIPTS", "all"),
        help="profile the default smoke script or every discovered run_c_baseline*.sh script",
    )
    parser.add_argument(
        "--coverage-phases",
        choices=("encode", "decode", "both"),
        default=os.environ.get("DSC_COVERAGE_PHASES", "encode"),
        help=(
            "collect encoder execution, decoder execution, or both; decoder mode "
            "uses encoded bitstreams only as fixtures and excludes their profiles"
        ),
    )
    return parser.parse_args()


def sha256_file(path: pathlib.Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def locate(name: str) -> str | None:
    found = shutil.which(name)
    if found:
        return found
    candidates = [
        pathlib.Path("/opt/homebrew/opt/llvm/bin") / name,
        pathlib.Path("/opt/homebrew/bin") / name,
        pathlib.Path("/opt/homebrew/Cellar/llvm/22.1.8/bin") / name,
    ]
    return next((str(item) for item in candidates if item.is_file() and os.access(item, os.X_OK)), None)


def run(command: list[str], cwd: pathlib.Path, env: dict[str, str], timeout: int) -> dict[str, Any]:
    started = time.monotonic()
    try:
        completed = subprocess.run(
            command,
            cwd=cwd,
            env=env,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=timeout,
            check=False,
        )
        output = completed.stdout or ""
        return {
            "status": "PASS" if completed.returncode == 0 else "FAIL",
            "returncode": completed.returncode,
            "duration_seconds": round(time.monotonic() - started, 3),
            "output_tail": output[-4000:],
        }
    except subprocess.TimeoutExpired as exc:
        return {
            "status": "TIMEOUT",
            "returncode": 124,
            "duration_seconds": round(time.monotonic() - started, 3),
            "output_tail": ((exc.stdout or "") + f"\n[driver] timeout after {timeout}s\n")[-4000:],
        }
    except OSError as exc:
        return {"status": "ERROR", "returncode": 127, "duration_seconds": 0, "output_tail": str(exc)}


def compact_command(command: list[str], copy_root: pathlib.Path) -> list[str]:
    return [item.replace(str(copy_root), "<coverage-copy>") for item in command]


def discover_coverage_scripts(copy_root: pathlib.Path, mode: str = "all") -> list[pathlib.Path]:
    """Discover the existing smoke profiles without a function-name allowlist."""
    smoke_dir = copy_root / "bittrue_smoke"
    if mode == "default":
        scripts = [smoke_dir / "run_c_baseline.sh"]
    else:
        scripts = sorted(smoke_dir.glob("run_c_baseline*.sh"))
    return [script for script in scripts if script.is_file()]


def baseline_scenario(script: pathlib.Path, copy_root: pathlib.Path) -> dict[str, Any]:
    """Derive a decode fixture from the existing data-driven baseline script."""
    text = script.read_text(encoding="utf-8", errors="replace")
    golden_match = re.search(r'\bgolden\s*=\s*["\']([^"\']+)', text)
    golden = golden_match.group(1) if golden_match else ""
    if golden.startswith("$model_dir/"):
        golden = golden[len("$model_dir/"):]
    config_match = re.search(r'(?:-F|--config)\s+([A-Za-z0-9_./{}-]+)', text)
    config = config_match.group(1) if config_match else ""
    if config.startswith("$model_dir/"):
        config = config[len("$model_dir/"):]
    list_file = str(pathlib.Path(config).with_suffix(".list")) if config else ""
    return {
        "script": script.relative_to(copy_root).as_posix(),
        "golden": golden,
        "config": config,
        "list": list_file,
        "status": (
            "PASS"
            if golden
            and config
            and (copy_root / config).is_file()
            and (copy_root / list_file).is_file()
            else "FAIL"
        ),
    }


def run_decode_fixture(
    copy_root: pathlib.Path,
    binary: pathlib.Path,
    scenario: dict[str, Any],
    output_dir: pathlib.Path,
    env: dict[str, str],
    timeout: int,
) -> dict[str, Any]:
    if output_dir.exists():
        shutil.rmtree(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    golden = copy_root / str(scenario.get("golden", ""))
    if scenario.get("status") != "PASS" or not golden.is_file():
        return {
            "status": "FAIL",
            "returncode": 2,
            "failure_reason": "decode fixture metadata or bitstream is missing",
            "scenario": scenario,
        }
    bitstream = output_dir / golden.name
    shutil.copy2(golden, bitstream)
    command = [
        str(binary),
        "-F", str(scenario["config"]),
        "-do", "2",
        "-ppm", "1",
        "-O", f"LOG_FILENAME {output_dir / 'decode.log'}",
        str(scenario["list"]),
        str(output_dir),
    ]
    result = run(command, copy_root, env, timeout)
    outputs = sorted(output_dir.glob("*.out.ppm"))
    output = outputs[0] if len(outputs) == 1 else None
    status = "PASS" if result.get("status") == "PASS" and output else "FAIL"
    return {
        "status": status,
        "scenario": scenario,
        "command": compact_command(command, copy_root),
        "result": result,
        "input_bitstream_sha256": sha256_file(bitstream),
        "output_count": len(outputs),
        "decoded_frame": output.name if output else None,
        "decoded_frame_sha256": sha256_file(output) if output else None,
        "decoded_frame_size_bytes": output.stat().st_size if output else None,
    }


def function_key(value: dict[str, Any]) -> tuple[str, int, str]:
    source = pathlib.Path(value.get("source_file", value.get("filename", ""))).name
    line = int(value.get("line", value.get("start_line", 0)) or 0)
    return source, line, value.get("name", "")


def cov_function_key(value: dict[str, Any]) -> tuple[str, int, str]:
    filenames = value.get("filenames", [])
    source = pathlib.Path(filenames[0] if filenames else value.get("filename", "")).name
    regions = value.get("regions", [])
    line = int(regions[0][0] if regions else value.get("line", 0))
    return source, line, value.get("name", "")


def percent(summary: dict[str, Any], key: str) -> float | None:
    value = summary.get(key)
    if not isinstance(value, dict):
        return None
    if isinstance(value.get("percent"), (int, float)):
        return float(value["percent"])
    count = value.get("count")
    covered = value.get("covered")
    if isinstance(count, (int, float)) and count:
        return round(float(covered or 0) * 100.0 / float(count), 3)
    return None


def coverage_function_record(value: dict[str, Any], file_summary: dict[str, Any]) -> dict[str, Any]:
    execution_count = int(value.get("count", value.get("execution_count", 0)) or 0)
    regions = value.get("regions", [])
    primary_regions = [
        region for region in regions
        if len(region) > 5 and isinstance(region[5], int) and region[5] == 0
    ] or regions
    region_counts = [int(region[4]) for region in regions if len(region) > 4 and isinstance(region[4], int)]
    covered = execution_count > 0 or any(count > 0 for count in region_counts)
    line_regions = {(int(region[0]), int(region[2])) for region in regions if len(region) > 4}
    covered_line_regions = {
        (int(region[0]), int(region[2]))
        for region in regions
        if len(region) > 4 and isinstance(region[4], int) and region[4] > 0
    }
    branch_values = [
        count
        for branch in value.get("branches", [])
        for count in branch[4:6]
        if isinstance(count, int)
    ]
    branch_total = len(branch_values)
    branch_covered = sum(count > 0 for count in branch_values)
    return {
        "name": value.get("name", ""),
        "source_file": pathlib.Path((value.get("filenames") or [""])[0]).name,
        "start_line": min(int(region[0]) for region in primary_regions) if primary_regions else None,
        "end_line": max(int(region[2]) for region in primary_regions) if primary_regions else None,
        "execution_count": execution_count,
        "line_coverage_percent": round(len(covered_line_regions) * 100.0 / len(line_regions), 3) if line_regions else 0.0,
        "branch_coverage_percent": round(branch_covered * 100.0 / branch_total, 3) if branch_total else 100.0,
        "region_coverage_percent": round(len(covered_line_regions) * 100.0 / len(line_regions), 3) if line_regions else 0.0,
        "covered": covered,
        "raw_summary": {
            "function_count": 1,
            "function_covered": int(covered),
            "line_region_count": len(line_regions),
            "covered_line_region_count": len(covered_line_regions),
            "branch_arm_count": branch_total,
            "covered_branch_arm_count": branch_covered,
        },
    }


def join_coverage(
    exported: dict[str, Any], functions: dict[str, Any], candidates: dict[str, Any],
    profile_tools: dict[str, str], commands: list[dict[str, Any]], build_receipt: dict[str, Any]
) -> dict[str, Any]:
    coverage_by_key: dict[tuple[str, int, str], dict[str, Any]] = {}
    data = exported.get("data", [{}])[0]
    file_summaries = {pathlib.Path(item.get("filename", "")).name: item.get("summary", {}) for item in data.get("files", [])}
    for value in data.get("functions", []):
        filenames = value.get("filenames", [])
        source = pathlib.Path(filenames[0] if filenames else "").name
        coverage_by_key[cov_function_key(value)] = coverage_function_record(value, file_summaries.get(source, {}))
    candidate_by_usr = {item.get("clang_usr"): item for item in candidates.get("functions", [])}
    records = []
    for function in functions.get("functions", []):
        source = pathlib.Path(function.get("source_file", "")).name
        key = source, int(function.get("line", 0) or 0), function.get("name", "")
        cov = coverage_by_key.get(key)
        if cov is None:
            # LLVM may report the first executable body line instead of the
            # declaration line recorded by Clang.  C has no overloaded
            # functions, so source plus name is a deterministic fallback even
            # when the span begins more than a few lines apart.
            matches = [
                item for item in coverage_by_key.values()
                if item.get("source_file") == source
                and item.get("name") == function.get("name")
                and item.get("start_line") is not None
            ]
            cov = sorted(matches, key=lambda item: (abs(int(item["start_line"]) - int(function.get("line", 0))), item["start_line"]))[0] if matches else None
        candidate = candidate_by_usr.get(function.get("clang_usr"), {})
        status = "EXECUTED" if cov and cov.get("covered") else "STATIC_BUT_UNCOVERED" if cov else "NO_COVERAGE_DATA"
        static_eligible = bool(candidate.get("eligible"))
        eligible_after = static_eligible and status in {"EXECUTED", "STATIC_BUT_UNCOVERED"}
        records.append(
            {
                "clang_usr": function.get("clang_usr"),
                "name": function.get("name"),
                "source_file": function.get("source_file"),
                "line": function.get("line"),
                "end_line": function.get("end_line"),
                "production_reachable": bool(candidate.get("production_reachable", False)),
                "contributes_to_observable_output": bool(candidate.get("contributes_to_observable_output", False)),
                "purity": candidate.get("purity", "UNKNOWN"),
                "timing": candidate.get("timing", "UNKNOWN"),
                "role": candidate.get("role", "UNRESOLVED"),
                "static_eligible": static_eligible,
                "coverage_status": status,
                "eligible_after_coverage": eligible_after,
                "direct_effects": candidate.get("direct_effects", {}),
                "transitive_effects": candidate.get("transitive_effects", {}),
                "coverage": cov or {
                    "execution_count": 0,
                    "line_coverage_percent": None,
                    "branch_coverage_percent": None,
                    "region_coverage_percent": None,
                    "covered": False,
                },
            }
        )
    before = [
        {"rank": index, "name": item.get("name"), "score": item.get("score"), "clang_usr": item.get("clang_usr")}
        for index, item in enumerate(candidates.get("ranked_candidates", []), start=1)
    ]
    after_items = [
        item for item in candidates.get("ranked_candidates", [])
        if next((record for record in records if record["clang_usr"] == item.get("clang_usr")), {}).get("eligible_after_coverage")
    ]
    after = [
        {"rank": index, "name": item.get("name"), "score": item.get("score"), "clang_usr": item.get("clang_usr")}
        for index, item in enumerate(after_items, start=1)
    ]
    return {
        "schema_version": 1,
        "do_not_edit": True,
        "status": "PASS",
        "coverage_tools": profile_tools,
        "commands": commands,
        "build_receipt_sha256": sha256_file(pathlib.Path(build_receipt["path"])) if pathlib.Path(build_receipt["path"]).is_file() else "UNKNOWN",
        "profile": exported.get("type", "llvm-source-based"),
        "function_count": len(records),
        "executed_function_count": sum(record["coverage_status"] == "EXECUTED" for record in records),
        "static_but_uncovered_function_count": sum(record["coverage_status"] == "STATIC_BUT_UNCOVERED" for record in records),
        "no_coverage_data_function_count": sum(record["coverage_status"] == "NO_COVERAGE_DATA" for record in records),
        "eligible_after_coverage_count": sum(record["eligible_after_coverage"] for record in records),
        "rankings": {"before": before, "after": after},
        "functions": records,
    }


def main() -> int:
    args = parse_args()
    output_dir = args.output_dir.resolve()
    work_dir = args.work_dir.resolve()
    output_dir.mkdir(parents=True, exist_ok=True)
    work_dir.mkdir(parents=True, exist_ok=True)
    receipt: dict[str, Any] = {
        "schema_version": 1,
        "do_not_edit": True,
        "status": "INFRASTRUCTURE_FAILURE",
        "model_root": str(args.model_root.resolve()),
        "copy_excludes": sorted(COPY_EXCLUDES),
        "commands": [],
    }
    receipt_path = output_dir / "coverage-receipt.json"
    try:
        clang = locate("clang")
        llvm_profdata = locate("llvm-profdata")
        llvm_cov = locate("llvm-cov")
        if not clang or not llvm_profdata or not llvm_cov:
            raise RuntimeError("clang, llvm-profdata, and llvm-cov are required for dynamic coverage")
        copy_root = work_dir / "model"
        copy_model(args.model_root.resolve(), copy_root)
        source_dir = copy_root / "source"
        binary = source_dir / "dsc"
        profile_dir = copy_root / "coverage-profiles"
        profile_dir.mkdir(parents=True, exist_ok=True)
        profile_pattern = str(profile_dir / "%p.profraw")
        env = os.environ.copy()
        env.update(
            {
                "CC": f"{clang} -fprofile-instr-generate",
                "JFLAGS": "-std=gnu99 -O1 -gline-tables-only -fprofile-instr-generate -fcoverage-mapping",
                "LLVM_PROFILE_FILE": profile_pattern,
                # The public Makefile uses `=` assignments.  -e makes the
                # temporary instrumentation variables win without editing
                # that upstream file, including inside the smoke script.
                "MAKEFLAGS": "-e",
            }
        )
        for command in (
            ["make", "-j1", "-C", str(source_dir), "clean"],
            ["make", "-j1", "-C", str(source_dir)],
        ):
            result = run(command, copy_root, env, args.timeout)
            receipt["commands"].append({"command": compact_command(command, copy_root), **result})
            if result["status"] != "PASS":
                receipt["failure_reason"] = "instrumented C build failed"
                receipt_path.write_text(json.dumps(receipt, indent=2, sort_keys=True) + "\n", encoding="utf-8")
                return 1
        coverage_scripts = discover_coverage_scripts(copy_root, args.coverage_scripts)
        if not coverage_scripts:
            raise RuntimeError(
                f"no coverage scripts discovered in {copy_root / 'bittrue_smoke'}"
            )
        receipt["coverage_script_mode"] = args.coverage_scripts
        receipt["coverage_phases"] = args.coverage_phases
        receipt["coverage_scripts"] = []
        receipt["decode_runs"] = []
        for index, smoke_script in enumerate(coverage_scripts, start=1):
            # Give every profile a unique prefix.  Several scripts rebuild the
            # same binary and the operating system may reuse a PID between
            # sequential runs; a per-script prefix prevents profile overwrite.
            script_env = env.copy()
            fixture_phase = (
                "encode"
                if args.coverage_phases in {"encode", "both"}
                else "fixture"
            )
            fixture_prefix = f"{index:02d}-{fixture_phase}-{smoke_script.stem}"
            script_env["LLVM_PROFILE_FILE"] = str(
                profile_dir / f"{fixture_prefix}-%p.profraw"
            )
            command = ["bash", str(smoke_script)]
            result = run(command, copy_root, script_env, args.timeout)
            command_record = {
                "command": compact_command(command, copy_root),
                **result,
            }
            receipt["commands"].append(command_record)
            script_record = {
                "script": smoke_script.relative_to(copy_root).as_posix(),
                "expected_hash": expected_smoke_hash(smoke_script),
                "result": result,
                "outputs": smoke_outputs(copy_root),
            }
            receipt["coverage_scripts"].append(script_record)
            # Keep the historical single-smoke field as a compatibility alias
            # for consumers that only understand the original receipt schema.
            if smoke_script.name == "run_c_baseline.sh":
                receipt["smoke"] = {
                    "mode": smoke_script.relative_to(copy_root).as_posix(),
                    "expected_hash": expected_smoke_hash(smoke_script),
                    "outputs": smoke_outputs(copy_root),
                    "result": result,
                }
            if result["status"] != "PASS":
                receipt["failure_reason"] = (
                    f"instrumented C coverage script failed: "
                    f"{smoke_script.relative_to(copy_root).as_posix()}"
                )
                receipt_path.write_text(json.dumps(receipt, indent=2, sort_keys=True) + "\n", encoding="utf-8")
                return 1
            if args.coverage_phases in {"decode", "both"}:
                # In decoder-only mode the baseline script is fixture
                # preparation, not runtime evidence.  Delete only that
                # script's uniquely prefixed encoder profiles before decode.
                if args.coverage_phases == "decode":
                    for fixture_profile in profile_dir.glob(f"{fixture_prefix}-*.profraw"):
                        fixture_profile.unlink()
                scenario = baseline_scenario(smoke_script, copy_root)
                decode_env = env.copy()
                decode_env["LLVM_PROFILE_FILE"] = str(
                    profile_dir / f"{index:02d}-decode-{smoke_script.stem}-%p.profraw"
                )
                decode = run_decode_fixture(
                    copy_root,
                    binary,
                    scenario,
                    copy_root / "coverage-decode-output" / smoke_script.stem,
                    decode_env,
                    args.timeout,
                )
                receipt["decode_runs"].append(decode)
                if decode.get("command") and isinstance(decode.get("result"), dict):
                    receipt["commands"].append({
                        "command": decode["command"],
                        **decode["result"],
                    })
                if decode.get("status") != "PASS":
                    receipt["failure_reason"] = (
                        f"instrumented C decode failed: "
                        f"{smoke_script.relative_to(copy_root).as_posix()}"
                    )
                    receipt_path.write_text(
                        json.dumps(receipt, indent=2, sort_keys=True) + "\n",
                        encoding="utf-8",
                    )
                    return 1
        if not binary.is_file():
            raise RuntimeError("instrumented source/dsc was not produced")
        profraw = sorted(profile_dir.glob("*.profraw"))
        if not profraw:
            raise RuntimeError("LLVM_PROFILE_FILE produced no profraw data")
        profdata = work_dir / "merged.profdata"
        merge_command = [llvm_profdata, "merge", "-sparse", *map(str, profraw), "-o", str(profdata)]
        result = run(merge_command, work_dir, env, args.timeout)
        receipt["commands"].append({"command": compact_command(merge_command, copy_root), **result})
        if result["status"] != "PASS":
            raise RuntimeError("llvm-profdata merge failed")
        # LLVM 22 emits the machine-readable JSON document under the `text`
        # export format; older LLVM releases accepted `json` as an alias.
        export_command = [llvm_cov, "export", "-format=text", "-instr-profile", str(profdata), str(binary)]
        export = subprocess.run(
            export_command,
            cwd=work_dir,
            env=env,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=args.timeout,
            check=False,
        )
        receipt["commands"].append(
            {
                "command": compact_command(export_command, copy_root),
                "status": "PASS" if export.returncode == 0 else "FAIL",
                "returncode": export.returncode,
                "output_tail": (export.stdout or "")[-4000:],
            }
        )
        if export.returncode != 0:
            raise RuntimeError("llvm-cov export failed")
        exported = json.loads(export.stdout)
        functions = json.loads(args.functions.resolve().read_text(encoding="utf-8"))
        candidates = json.loads(args.candidates.resolve().read_text(encoding="utf-8"))
        build_receipt = {"path": str(args.build_receipt.resolve())}
        coverage = join_coverage(
            exported,
            functions,
            candidates,
            {"clang": clang, "llvm-profdata": llvm_profdata, "llvm-cov": llvm_cov},
            receipt["commands"],
            build_receipt,
        )
        coverage["profile_artifacts"] = {
            "profraw_count": len(profraw),
            "profdata_sha256": sha256_file(profdata),
            "instrumented_binary_sha256": sha256_file(binary),
        }
        coverage["coverage_script_mode"] = args.coverage_scripts
        coverage["coverage_phases"] = args.coverage_phases
        coverage["coverage_scripts"] = receipt["coverage_scripts"]
        coverage["decode_runs"] = receipt["decode_runs"]
        (output_dir / "coverage.json").write_text(json.dumps(coverage, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        receipt.update(
            {
                "status": "PASS",
                "profile_artifacts": coverage["profile_artifacts"],
                "instrumented_binary_sha256": sha256_file(binary),
                "profraw_count": len(profraw),
            }
        )
        receipt_path.write_text(json.dumps(receipt, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        print(
            f"coverage PASS: {coverage['executed_function_count']} executed, "
            f"{coverage['eligible_after_coverage_count']} eligible after coverage"
        )
        return 0
    except (OSError, RuntimeError, subprocess.TimeoutExpired, json.JSONDecodeError) as exc:
        receipt["failure_reason"] = str(exc)
        receipt_path.write_text(json.dumps(receipt, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        print(f"coverage failure: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
