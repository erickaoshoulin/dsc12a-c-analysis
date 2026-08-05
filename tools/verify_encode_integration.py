#!/usr/bin/env python3
"""Verify all discovered Encode RTL boundaries in one full-frame executable.

The original C model is the Encode oracle.  This verifier discovers stable
library components and provisional candidates from receipts, filters the
provisional set by Encode RTL_RETURN execution evidence, rewrites every
selected boundary into one copied C model, and compares the resulting `.dsc`
frame byte-for-byte and by SHA-256 in C_ONLY/SHADOW/RTL_RETURN modes.

The verifier is deliberately conservative.  A missing Encode candidate is a
reported compute gap, not an implicit C fallback that can produce a PASS.  A
dry run can therefore be used to inspect the frontier before spending time on
the simultaneous Verilator build; ``--allow-incomplete`` runs the discovered
subset but records an INCOMPLETE result rather than a PASS.
"""

from __future__ import annotations

import argparse
import json
import os
import pathlib
import shutil
import tempfile
import time
from typing import Any

try:
    from cicd_agent import (
        Agent,
        contract_function,
        file_hash,
        read_json,
        safe_identifier,
        scrub_paths,
        write_json,
    )
    from verify_decode_integration import (
        absorbed_rtl_dependencies,
        compile_multi_overlay,
        namespace_adapter_text,
        namespaced_filename,
        rewrite_multi_overlay,
        source_order_candidates,
        write_multi_overlay_sources,
    )
except ModuleNotFoundError:  # Imported as tools.verify_encode_integration in tests.
    from tools.cicd_agent import (
        Agent,
        contract_function,
        file_hash,
        read_json,
        safe_identifier,
        scrub_paths,
        write_json,
    )
    from tools.verify_decode_integration import (
        absorbed_rtl_dependencies,
        compile_multi_overlay,
        namespace_adapter_text,
        namespaced_filename,
        rewrite_multi_overlay,
        source_order_candidates,
        write_multi_overlay_sources,
    )


PHASE = "encode"
PHASE_LABEL = "ENCODE"
DEFAULT_ROOT_FUNCTION = "DSC_Encode"
REQUIRED_FULL_PROFILE_COUNT = 22
MODES = ("C_ONLY", "SHADOW", "RTL_RETURN")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Run all discovered Encode RTL candidates in one .dsc frame verifier"
    )
    parser.add_argument("--root", type=pathlib.Path, required=True)
    parser.add_argument("--artifact", type=pathlib.Path, required=True)
    parser.add_argument(
        "--scope",
        choices=("smoke", "all"),
        default="all",
        help="all selects every discovered baseline profile; smoke selects the small development set",
    )
    parser.add_argument("--jobs", type=int, default=min(4, os.cpu_count() or 1))
    parser.add_argument(
        "--allow-incomplete",
        action="store_true",
        help="run the discovered subset while preserving an INCOMPLETE result when gaps remain",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="write discovery/frontier receipts without building or simulating",
    )
    return parser.parse_args()


def _int(value: Any, default: int = 0) -> int:
    try:
        return int(value)
    except (TypeError, ValueError):
        return default


def _bool_effect(record: dict[str, Any], *keys: str) -> bool:
    effects = record.get("effects", {}) or {}
    return any(bool(effects.get(key)) for key in keys)


def _facts_by_name(facts: dict[str, Any]) -> dict[str, dict[str, Any]]:
    return {
        str(item.get("name")): item
        for item in facts.get("functions", []) or []
        if item.get("name")
    }


def reachable_encode_functions(
    facts: dict[str, Any], root_function: str = DEFAULT_ROOT_FUNCTION
) -> list[str]:
    """Traverse the generated direct-call facts from the Encode phase root."""
    by_name = _facts_by_name(facts)
    if root_function not in by_name:
        return []
    seen: set[str] = set()
    pending = [root_function]
    while pending:
        name = pending.pop()
        if name in seen:
            continue
        seen.add(name)
        for callee in by_name.get(name, {}).get("callees", []) or []:
            callee_name = str(callee.get("name", ""))
            if callee_name in by_name and callee_name not in seen:
                pending.append(callee_name)
    return sorted(seen)


def classify_non_rtl_boundary(
    function: dict[str, Any], root_function: str = DEFAULT_ROOT_FUNCTION
) -> str | None:
    """Classify only structural C orchestration/lifecycle boundaries.

    This intentionally has no function-name allowlist.  Allocation effects
    identify lifecycle ownership, while the phase wrapper is identified by the
    caller-provided root and its zero-loop shape.  Functions with datapath
    loops, state writes, or only error-path logging remain compute gaps.
    """
    name = str(function.get("name", ""))
    if name == root_function and _int(function.get("loop_count")) == 0:
        return "PHASE_WRAPPER"
    if _bool_effect(function, "malloc", "free", "allocation"):
        return "LIFECYCLE_ORCHESTRATION"
    return None


def _coverage_by_identity(root: pathlib.Path) -> dict[str, dict[str, Any]]:
    coverage = read_json(root / "coverage" / "coverage.json", {}) or {}
    result: dict[str, dict[str, Any]] = {}
    for item in coverage.get("functions", []) or []:
        for key in (item.get("clang_usr"), item.get("name")):
            if key:
                result[str(key)] = item
    return result


def _phase_modes(receipt: dict[str, Any], phase: str = PHASE) -> dict[str, Any]:
    phase_receipt = receipt.get(phase)
    if isinstance(phase_receipt, dict):
        modes = phase_receipt.get("modes")
        if isinstance(modes, dict):
            return modes
    # Individual Encode matrix receipts historically exposed Encode as the
    # top-level `modes` alias.  Keep this fallback receipt-driven.
    modes = receipt.get("modes")
    return modes if isinstance(modes, dict) else {}


def _phase_invocations(
    receipt: dict[str, Any], phase: str = PHASE, mode: str = "RTL_RETURN"
) -> int:
    mode_receipt = _phase_modes(receipt, phase).get(mode, {}) or {}
    return _int(mode_receipt.get("total_rtl_invocations"))


def _phase_mode_status(
    receipt: dict[str, Any], phase: str = PHASE, mode: str = "RTL_RETURN"
) -> str | None:
    mode_receipt = _phase_modes(receipt, phase).get(mode, {}) or {}
    value = mode_receipt.get("status")
    return str(value) if value is not None else None


def _path_value(value: Any, root: pathlib.Path) -> Any:
    if isinstance(value, pathlib.Path):
        try:
            return str(value.relative_to(root))
        except ValueError:
            return str(value)
    return value


def _candidate_summary(candidate: dict[str, Any], root: pathlib.Path) -> dict[str, Any]:
    return {
        key: _path_value(value, root)
        for key, value in candidate.items()
        if key != "contract"
    }


def encode_frontier(
    root: pathlib.Path,
    candidates: list[dict[str, Any]],
    *,
    root_function: str = DEFAULT_ROOT_FUNCTION,
) -> dict[str, Any]:
    """Report reachable Encode RTL coverage and unresolved compute gaps."""
    facts = read_json(root / "facts" / "functions.json", {}) or {}
    by_name = _facts_by_name(facts)
    reachable = reachable_encode_functions(facts, root_function)
    coverage = _coverage_by_identity(root)
    selected_names = {str(item.get("function")) for item in candidates}
    if not by_name or not reachable:
        return {
            "status": "UNAVAILABLE",
            "root_function": root_function,
            "reachable_functions": [],
            "rtl_covered": sorted(selected_names),
            "orchestration_boundaries": [],
            "compute_gaps": [],
            "unexecuted_reachable": [],
            "reason": "facts/functions.json does not contain the Encode root",
        }

    rtl_covered: list[str] = []
    orchestration: list[dict[str, Any]] = []
    compute_gaps: list[dict[str, Any]] = []
    unexecuted: list[dict[str, Any]] = []
    for name in reachable:
        function = by_name[name]
        identity = str(function.get("clang_usr", name))
        coverage_record = coverage.get(identity) or coverage.get(name) or {}
        executed = coverage_record.get("coverage_status") == "EXECUTED"
        if not executed:
            unexecuted.append({
                "function": name,
                "clang_usr": identity,
                "reason": "Encode phase execution evidence is absent",
            })
            continue
        if name in selected_names:
            rtl_covered.append(name)
            continue
        boundary = classify_non_rtl_boundary(function, root_function)
        if boundary:
            orchestration.append({
                "function": name,
                "clang_usr": identity,
                "classification": boundary,
                "source_file": function.get("source_file"),
                "line": function.get("line"),
            })
            continue
        compute_gaps.append({
            "function": name,
            "clang_usr": identity,
            "reason": "Executed Encode datapath has no discovered RTL candidate",
            "source_file": function.get("source_file"),
            "line": function.get("line"),
            "effects": function.get("effects", {}),
            "loop_count": function.get("loop_count"),
        })
    return {
        "status": "PASS" if not compute_gaps else "INCOMPLETE",
        "root_function": root_function,
        "reachable_functions": reachable,
        "rtl_covered": sorted(rtl_covered),
        "orchestration_boundaries": sorted(
            orchestration, key=lambda item: str(item.get("function"))
        ),
        "compute_gaps": sorted(
            compute_gaps, key=lambda item: str(item.get("function"))
        ),
        "unexecuted_reachable": sorted(
            unexecuted, key=lambda item: str(item.get("function"))
        ),
        "counts": {
            "reachable": len(reachable),
            "rtl_covered": len(rtl_covered),
            "orchestration_boundaries": len(orchestration),
            "compute_gaps": len(compute_gaps),
            "unexecuted_reachable": len(unexecuted),
        },
    }


def discover_encode_candidates(
    root: pathlib.Path,
    *,
    root_function: str = DEFAULT_ROOT_FUNCTION,
    return_report: bool = False,
) -> list[dict[str, Any]] | tuple[list[dict[str, Any]], dict[str, Any]]:
    """Discover Encode candidates from the manifest and phase receipts.

    Stable components are hash checked against the library manifest and must
    have Encode coverage.  Provisional components are selected only when the
    receipt says Encode RTL_RETURN actually invoked the candidate at least
    once.  No candidate function names are enumerated here.
    """
    coverage = _coverage_by_identity(root)
    facts = read_json(root / "facts" / "functions.json", {}) or {}
    reachable = set(reachable_encode_functions(facts, root_function))
    selected: list[dict[str, Any]] = []
    errors: list[str] = []
    exclusions: list[dict[str, Any]] = []
    stable_functions: set[str] = set()

    manifest = read_json(root / "library" / "manifest.json", {}) or {}
    components = sorted(
        manifest.get("components", []) or [],
        key=lambda item: str(item.get("contract_id", "")),
    )
    for component in components:
        if component.get("status") != "PASS":
            continue
        contract_path = root / "library" / str(component.get("contract_file", ""))
        candidate_path = root / "library" / str(component.get("module_file", ""))
        if not contract_path.is_file():
            errors.append(f"stable_contract_missing:{component.get('contract_id')}")
            continue
        if not candidate_path.is_file():
            errors.append(f"stable_rtl_missing:{component.get('contract_id')}")
            continue
        contract = read_json(contract_path, {}) or {}
        function = contract_function(contract)
        name = str(function.get("name", ""))
        identity = str(function.get("clang_usr", ""))
        if not name or not identity:
            errors.append(f"stable_function_identity_missing:{component.get('contract_id')}")
            continue
        coverage_record = coverage.get(identity) or coverage.get(name) or {}
        if coverage_record.get("coverage_status") != "EXECUTED":
            exclusions.append({
                "source": "STABLE_MANIFEST",
                "function": name,
                "reason": "Encode coverage does not show execution",
            })
            continue
        if reachable and name not in reachable:
            exclusions.append({
                "source": "STABLE_MANIFEST",
                "function": name,
                "reason": "not in generated DSC_Encode call-graph closure",
            })
            continue
        expected_hash = str(component.get("module_sha256", ""))
        actual_hash = file_hash(candidate_path)
        if expected_hash and expected_hash != actual_hash:
            errors.append(f"stable_rtl_hash_mismatch:{name}")
            continue
        slug = safe_identifier(
            str(component.get("contract_id") or contract.get("contract_id") or name)
        ).lower()
        stable_functions.add(name)
        selected.append({
            "slug": slug,
            "rtl_tier": "STABLE_RTL",
            "source": "STABLE_MANIFEST",
            "artifact": root / "library" / str(component.get("artifact_dir", "")),
            "contract_path": contract_path,
            "contract": contract,
            "candidate_path": candidate_path,
            "module": str(component.get("module") or contract.get("contract_id")),
            "function": name,
            "clang_usr": identity,
            "contract_sha256": file_hash(contract_path),
            "candidate_sha256": actual_hash,
        })

    # Search every generated candidate collection.  This keeps the discovery
    # policy independent of whether a future producer calls the directory
    # `encode-candidates`, `decode-candidates`, or another phase collection.
    provisional_paths = sorted(root.glob("rtl/**/provisional-contract.json"))
    provisional_seen = 0
    for contract_path in provisional_paths:
        parent = contract_path.parent
        contract = read_json(contract_path, {}) or {}
        function = contract_function(contract)
        name = str(function.get("name", ""))
        identity = str(function.get("clang_usr", ""))
        if not name or not identity:
            exclusions.append({
                "source": "PROVISIONAL_RECEIPT",
                "path": str(contract_path),
                "reason": "function identity missing",
            })
            continue
        matrix_path = parent / "matrix-receipt.json"
        matrix = read_json(matrix_path, {}) or {}
        provisional_seen += 1
        encode_return_invocations = _phase_invocations(matrix, PHASE, "RTL_RETURN")
        encode_return_status = _phase_mode_status(matrix, PHASE, "RTL_RETURN")
        candidate_path = next(
            (
                path for path in (
                    parent / "candidate_01.sv",
                    parent / "candidate.sv",
                )
                if path.is_file()
            ),
            None,
        )
        if (
            matrix.get("status") != "PASS"
            or encode_return_status != "PASS"
            or encode_return_invocations <= 0
            or candidate_path is None
        ):
            reasons: list[str] = []
            if matrix.get("status") != "PASS":
                reasons.append("matrix_status_not_pass")
            if encode_return_status != "PASS":
                reasons.append("encode_rtl_return_status_not_pass")
            if encode_return_invocations <= 0:
                reasons.append("encode_rtl_return_invocations_not_positive")
            if candidate_path is None:
                reasons.append("candidate_sv_missing")
            exclusions.append({
                "source": "PROVISIONAL_RECEIPT",
                "function": name,
                "path": str(contract_path),
                "encode_rtl_return_invocations": encode_return_invocations,
                "reason": ",".join(reasons),
            })
            continue
        if name in stable_functions:
            exclusions.append({
                "source": "PROVISIONAL_RECEIPT",
                "function": name,
                "reason": "stable manifest component takes precedence",
            })
            continue
        slug = safe_identifier(str(contract.get("contract_id") or name)).lower()
        selected.append({
            "slug": slug,
            "rtl_tier": "PROVISIONAL_RTL_PASS",
            "source": "PROVISIONAL_RECEIPT",
            "artifact": parent,
            "contract_path": contract_path,
            "contract": contract,
            "candidate_path": candidate_path,
            "module": str(
                (contract.get("rtl", {}) or {}).get("module")
                or contract.get("contract_id")
                or slug
            ),
            "function": name,
            "clang_usr": identity,
            "contract_sha256": file_hash(contract_path),
            "candidate_sha256": file_hash(candidate_path),
            "source_matrix_sha256": file_hash(matrix_path) if matrix_path.is_file() else None,
            "encode_rtl_return_invocations": encode_return_invocations,
        })

    slugs = [str(item.get("slug")) for item in selected]
    if len(slugs) != len(set(slugs)):
        errors.append("discovered_encode_contract_identifiers_not_unique")
    if not selected:
        errors.append("no_encode_rtl_candidates_with_phase_evidence")

    frontier = encode_frontier(root, selected, root_function=root_function)
    report = {
        "schema_version": 1,
        "phase": PHASE_LABEL,
        "root_function": root_function,
        "policy": {
            "stable": "PASS library manifest component with hash-checked RTL and Encode execution evidence",
            "provisional": "matrix PASS plus Encode RTL_RETURN status PASS and invocation count > 0",
            "function_selection": "receipt/facts driven; no function allowlist",
            "incomplete_policy": "compute gaps block PASS unless explicitly run with --allow-incomplete",
        },
        "stable_manifest_components_seen": len(components),
        "provisional_receipts_seen": provisional_seen,
        "selected_candidates": [_candidate_summary(item, root) for item in selected],
        "candidate_count": len(selected),
        "exclusions": exclusions,
        "errors": sorted(set(errors)),
        "frontier": frontier,
    }
    return (selected, report) if return_report else selected


def source_order_encode_candidates(
    candidates: list[dict[str, Any]], facts: dict[str, Any]
) -> list[dict[str, Any]]:
    """Preserve caller-before-callee ordering for nested source rewrites."""
    return source_order_candidates(candidates, facts)


def parse_overlay_metrics(output: str) -> dict[str, Any]:
    """Expose the shared named adapter metric parser for unit tests/tools."""
    return Agent.parse_overlay_metrics(output)


def aggregate_candidate_metrics(scenarios: list[dict[str, Any]]) -> dict[str, Any]:
    totals: dict[str, dict[str, int | bool]] = {}
    for scenario in scenarios:
        candidates = (scenario.get("overlay_metrics", {}) or {}).get("candidates", {}) or {}
        for name, metrics in candidates.items():
            total = totals.setdefault(
                str(name),
                {"calls": 0, "rtl_invocations": 0, "mismatches": 0},
            )
            total["calls"] = int(total["calls"]) + _int(metrics.get("calls"))
            total["rtl_invocations"] = int(total["rtl_invocations"]) + _int(
                metrics.get("rtl_invocations")
            )
            total["mismatches"] = int(total["mismatches"]) + _int(
                metrics.get("mismatches")
            )
    for total in totals.values():
        total["replacement_reached"] = int(total["calls"]) > 0
        total["rtl_exercised"] = int(total["rtl_invocations"]) > 0
    return totals


def compare_dsc_frame(actual: pathlib.Path, oracle: pathlib.Path) -> dict[str, Any]:
    actual_exists = actual.is_file()
    oracle_exists = oracle.is_file()
    actual_hash = file_hash(actual) if actual_exists else None
    oracle_hash = file_hash(oracle) if oracle_exists else None
    byte_equal = Agent.files_byte_equal(actual, oracle)
    return {
        "status": "PASS" if byte_equal and actual_hash == oracle_hash else "FAIL",
        "actual_file": actual,
        "oracle_file": oracle,
        "actual_sha256": actual_hash,
        "oracle_sha256": oracle_hash,
        "sha256_match": bool(actual_hash and oracle_hash and actual_hash == oracle_hash),
        "byte_for_byte_match": byte_equal,
        "actual_size_bytes": actual.stat().st_size if actual_exists else None,
        "oracle_size_bytes": oracle.stat().st_size if oracle_exists else None,
    }


def _run_c_baseline(
    agent: Agent, base_model: pathlib.Path, scenarios: list[dict[str, Any]]
) -> list[dict[str, Any]]:
    results: list[dict[str, Any]] = []
    for scenario in scenarios:
        command = agent.run_process(
            [str(base_model / scenario["script"])],
            cwd=base_model,
            timeout=1800,
        )
        oracle = base_model / scenario["golden"]
        actual_hash = file_hash(oracle) if oracle.is_file() else None
        expected = scenario.get("expected_sha256")
        expected_match = actual_hash == expected if expected else None
        results.append({
            "scenario": scenario,
            "status": (
                "PASS"
                if command.get("returncode") == 0
                and actual_hash is not None
                and expected_match is not False
                else "FAIL"
            ),
            "command": command,
            "oracle_file": oracle,
            "sha256": actual_hash,
            "size_bytes": oracle.stat().st_size if oracle.is_file() else None,
            "expected_sha256": expected,
            "expected_sha256_match": expected_match,
            "oracle": "IMMUTABLE_ORIGINAL_C_SOURCE_COPY",
        })
    return results


def _run_encode_mode(
    agent: Agent,
    overlay_model: pathlib.Path,
    binary: pathlib.Path,
    baseline_results: list[dict[str, Any]],
    mode: str,
    expected_slugs: set[str],
    absorbed_by_parent: dict[str, list[dict[str, Any]]],
) -> dict[str, Any]:
    scenario_results: list[dict[str, Any]] = []
    for baseline in baseline_results:
        scenario = baseline["scenario"]
        golden = overlay_model / scenario["golden"]
        if golden.exists():
            golden.unlink()
        command = agent.run_process(
            [str(binary), "-F", str(overlay_model / scenario["config"])],
            cwd=overlay_model,
            env={"DSC_CICD_MODE": mode},
            timeout=1800,
        )
        metrics = parse_overlay_metrics(str(command.get("output", "")))
        frame = compare_dsc_frame(golden, pathlib.Path(str(baseline["oracle_file"])))
        mismatch_count = _int(metrics.get("mismatches"))
        expected = scenario.get("expected_sha256")
        actual_hash = frame.get("actual_sha256")
        expected_match = actual_hash == expected if expected else None
        scenario_pass = bool(
            command.get("returncode") == 0
            and frame.get("status") == "PASS"
            and expected_match is not False
            and mismatch_count == 0
        )
        scenario_results.append({
            "scenario": scenario,
            "status": "PASS" if scenario_pass else "FAIL",
            "command": command,
            "sha256": actual_hash,
            "size_bytes": golden.stat().st_size if golden.is_file() else None,
            "baseline_sha256": baseline.get("sha256"),
            "baseline_sha256_match": frame.get("sha256_match"),
            "expected_sha256": expected,
            "expected_sha256_match": expected_match,
            "mismatch_count": mismatch_count,
            "overlay_metrics": metrics,
            "frame_compare": frame,
            "replacement_status": (
                "RTL_EXERCISED"
                if metrics.get("rtl_exercised")
                else "C_PATH_REACHED"
                if metrics.get("replacement_reached")
                else "NOT_REACHED"
            ),
        })

    candidate_totals = aggregate_candidate_metrics(scenario_results)
    for slug in expected_slugs:
        total = candidate_totals.setdefault(
            slug,
            {
                "calls": 0,
                "rtl_invocations": 0,
                "mismatches": 0,
                "replacement_reached": False,
                "rtl_exercised": False,
            },
        )
        parents = absorbed_by_parent.get(slug, [])
        active_parents = [
            item
            for item in parents
            if _int(
                candidate_totals.get(
                    str(item.get("parent_slug")), {}
                ).get("rtl_invocations")
            )
            > 0
        ]
        total["absorbed_by_parent_rtl"] = active_parents
        total["execution_class"] = (
            "DIRECT_RTL"
            if _int(total.get("rtl_invocations")) > 0
            else "ABSORBED_BY_PARENT_RTL"
            if active_parents
            else "C_ONLY"
            if mode == "C_ONLY"
            else "NOT_RTL_EXERCISED"
        )

    def reached(slug: str) -> bool:
        total = candidate_totals.get(slug, {})
        if _int(total.get("calls")) > 0:
            return True
        return bool(total.get("absorbed_by_parent_rtl"))

    def rtl_exercised(slug: str) -> bool:
        total = candidate_totals.get(slug, {})
        return bool(
            _int(total.get("rtl_invocations")) > 0
            or total.get("absorbed_by_parent_rtl")
        ) and _int(total.get("mismatches")) == 0

    if mode == "C_ONLY":
        candidates_exercised = all(
            reached(slug)
            and _int(candidate_totals.get(slug, {}).get("rtl_invocations")) == 0
            for slug in expected_slugs
        )
    else:
        candidates_exercised = all(rtl_exercised(slug) for slug in expected_slugs)
    all_candidates_reached = all(reached(slug) for slug in expected_slugs)
    status = bool(
        all(item["status"] == "PASS" for item in scenario_results)
        and all_candidates_reached
        and candidates_exercised
    )
    return {
        "status": "PASS" if status else "FAIL",
        "profiles": len(scenario_results),
        "all_candidates_reached": all_candidates_reached,
        "all_candidates_exercised_as_expected": candidates_exercised,
        "total_calls": sum(_int(item.get("calls")) for item in candidate_totals.values()),
        "total_rtl_invocations": sum(
            _int(item.get("rtl_invocations")) for item in candidate_totals.values()
        ),
        "candidate_metrics": candidate_totals,
        "scenarios": scenario_results,
    }


def _write_discovery_receipts(
    artifact: pathlib.Path, root: pathlib.Path, candidates: list[dict[str, Any]], report: dict[str, Any]
) -> None:
    artifact.mkdir(parents=True, exist_ok=True)
    write_json(artifact / "discovery-receipt.json", report)
    write_json(artifact / "selected-candidates.json", {
        "schema_version": 1,
        "phase": PHASE_LABEL,
        "policy": report.get("policy"),
        "count": len(candidates),
        "candidates": [_candidate_summary(item, root) for item in candidates],
    })


def run_encode_discovery(
    root: pathlib.Path,
    artifact: pathlib.Path,
    *,
    root_function: str = DEFAULT_ROOT_FUNCTION,
) -> dict[str, Any]:
    candidates, report = discover_encode_candidates(
        root, root_function=root_function, return_report=True
    )
    _write_discovery_receipts(artifact, root, candidates, report)
    complete = bool(
        candidates
        and not report.get("errors")
        and (report.get("frontier", {}) or {}).get("status") == "PASS"
        and not (report.get("frontier", {}) or {}).get("compute_gaps")
    )
    result = {
        "schema_version": 1,
        "status": "DISCOVERY_PASS" if complete else "DISCOVERY_INCOMPLETE",
        "phase": PHASE_LABEL,
        "matrix_scope": "all",
        "required_profiles": REQUIRED_FULL_PROFILE_COUNT,
        "candidate_count": len(candidates),
        "discovery": report,
        "promotion_status": "BLOCKED_PENDING_HUMAN_CONTRACT_REVIEW",
    }
    write_json(artifact / "matrix-receipt.json", result)
    return result


def run_encode_integration(
    root: pathlib.Path,
    artifact: pathlib.Path,
    scope: str = "all",
    jobs: int = 1,
    *,
    allow_incomplete: bool = False,
) -> dict[str, Any]:
    started = time.time()
    root = root.resolve()
    artifact = artifact.resolve()
    previous_scope = os.environ.get("DSC_CICD_MATRIX_SCOPE")
    os.environ["DSC_CICD_MATRIX_SCOPE"] = scope
    base_model: pathlib.Path | None = None
    overlay_model: pathlib.Path | None = None
    discovery: dict[str, Any] = {}
    candidates: list[dict[str, Any]] = []

    def write_result(result: dict[str, Any]) -> dict[str, Any]:
        artifact.mkdir(parents=True, exist_ok=True)
        result.setdefault("matrix_scope", scope)
        result["duration_seconds"] = round(time.time() - started, 3)
        write_json(artifact / "matrix-receipt.json", scrub_paths(result, [root]))
        return result

    try:
        candidates, discovery = discover_encode_candidates(root, return_report=True)
        _write_discovery_receipts(artifact, root, candidates, discovery)
        gaps = (discovery.get("frontier", {}) or {}).get("compute_gaps", []) or []
        frontier_status = (discovery.get("frontier", {}) or {}).get("status")
        if discovery.get("errors"):
            return write_result({
                "schema_version": 1,
                "status": "BLOCKED_DISCOVERY",
                "phase": PHASE_LABEL,
                "reason": "Encode candidate discovery has errors",
                "candidate_count": len(candidates),
                "discovery": discovery,
            })
        if frontier_status == "UNAVAILABLE":
            return write_result({
                "schema_version": 1,
                "status": "BLOCKED_DISCOVERY",
                "phase": PHASE_LABEL,
                "reason": "Encode call-graph frontier is unavailable; cannot claim complete coverage",
                "candidate_count": len(candidates),
                "discovery": discovery,
            })
        if not candidates:
            return write_result({
                "schema_version": 1,
                "status": "BLOCKED_INCOMPLETE_CANDIDATES",
                "phase": PHASE_LABEL,
                "reason": "no Encode RTL candidates have valid phase evidence",
                "candidate_count": 0,
                "gaps": gaps,
                "discovery": discovery,
            })
        if gaps and not allow_incomplete:
            return write_result({
                "schema_version": 1,
                "status": "BLOCKED_INCOMPLETE_CANDIDATES",
                "phase": PHASE_LABEL,
                "reason": "executed Encode compute gaps remain; use --dry-run or --allow-incomplete",
                "candidate_count": len(candidates),
                "gaps": gaps,
                "discovery": discovery,
                "promotion_status": "BLOCKED_PENDING_HUMAN_CONTRACT_REVIEW",
            })

        agent = Agent(root, "encode-multi-rtl-integration")
        input_facts = agent.load_inputs()
        if input_facts.get("errors"):
            return write_result({
                "schema_version": 1,
                "status": "INFRASTRUCTURE_FAILURE",
                "phase": PHASE_LABEL,
                "reason": "input gate failed",
                "input_errors": input_facts.get("errors"),
                "candidate_count": len(candidates),
                "discovery": discovery,
            })
        scenarios = agent.discover_matrix()
        if not scenarios or not all(item.get("parse_status") == "PASS" for item in scenarios):
            return write_result({
                "schema_version": 1,
                "status": "INFRASTRUCTURE_FAILURE",
                "phase": PHASE_LABEL,
                "reason": "Encode matrix contains no usable or parseable profiles",
                "profiles": len(scenarios),
                "scenarios": scenarios,
                "candidate_count": len(candidates),
                "discovery": discovery,
            })
        if scope == "all" and len(scenarios) != REQUIRED_FULL_PROFILE_COUNT:
            return write_result({
                "schema_version": 1,
                "status": "BLOCKED_PROFILE_COVERAGE",
                "phase": PHASE_LABEL,
                "reason": f"full Encode scope requires {REQUIRED_FULL_PROFILE_COUNT} profiles",
                "profiles": len(scenarios),
                "required_profiles": REQUIRED_FULL_PROFILE_COUNT,
                "candidate_count": len(candidates),
                "discovery": discovery,
            })

        facts = read_json(root / "facts" / "functions.json", {}) or {}
        candidates = source_order_encode_candidates(candidates, facts)
        base_model = agent.copy_model("encode-integration-baseline")
        baseline_results = _run_c_baseline(agent, base_model, scenarios)
        if not all(item["status"] == "PASS" for item in baseline_results):
            return write_result({
                "schema_version": 1,
                "status": "INFRASTRUCTURE_FAILURE",
                "phase": PHASE_LABEL,
                "reason": "original C Encode baseline failed",
                "profiles": len(scenarios),
                "baseline": baseline_results,
                "candidate_count": len(candidates),
                "discovery": discovery,
            })

        temp_parent = root / "tmp"
        temp_parent.mkdir(parents=True, exist_ok=True)
        overlay_temp = pathlib.Path(
            tempfile.mkdtemp(prefix="dsc-encode-multi-overlay-", dir=str(temp_parent))
        )
        overlay_model = overlay_temp / base_model.name
        shutil.copytree(
            base_model,
            overlay_model,
            ignore=shutil.ignore_patterns(
                ".git", "__pycache__", "target", "build", "dsc-rs", "operator_bittrue"
            ),
        )
        generated = write_multi_overlay_sources(
            agent, overlay_model / "source", candidates
        )
        absorbed_dependencies = absorbed_rtl_dependencies(generated)
        rewrite_receipts = rewrite_multi_overlay(
            agent, overlay_model / "source", generated
        )
        compile_receipt = compile_multi_overlay(
            agent, overlay_model / "source", generated, max(1, jobs)
        )
        if compile_receipt.get("status") != "PASS":
            return write_result({
                "schema_version": 1,
                "status": "INFRASTRUCTURE_FAILURE",
                "phase": PHASE_LABEL,
                "reason": "simultaneous Encode Verilator executable failed to compile",
                "profiles": len(scenarios),
                "baseline": baseline_results,
                "rewrites": rewrite_receipts,
                "compile": compile_receipt,
                "candidate_count": len(candidates),
                "candidate_order": [item["function"] for item in candidates],
                "discovery": discovery,
            })

        expected_slugs = {str(item["slug"]) for item in generated}
        mode_results: dict[str, Any] = {}
        for mode in MODES:
            mode_results[mode] = _run_encode_mode(
                agent,
                overlay_model,
                pathlib.Path(str(compile_receipt["binary"])),
                baseline_results,
                mode,
                expected_slugs,
                absorbed_dependencies,
            )

        matrix_pass = all(
            mode_results.get(mode, {}).get("status") == "PASS" for mode in MODES
        )
        complete = not gaps
        status = (
            "PASS"
            if complete and matrix_pass
            else "INCOMPLETE_PASS"
            if allow_incomplete and matrix_pass
            else "FAIL"
        )
        roots = [root, base_model, base_model.parent, overlay_model, overlay_model.parent]
        result = {
            "schema_version": 1,
            "status": status,
            "matrix_scope": scope,
            "profiles": len(scenarios),
            "required_profiles": REQUIRED_FULL_PROFILE_COUNT if scope == "all" else None,
            "phase_order": [PHASE_LABEL],
            "oracle": "IMMUTABLE_ORIGINAL_C_SOURCE",
            "replacement": "ALL_DISCOVERED_ENCODE_VERILOG_VIA_VERILATOR_CXX_IN_ONE_EXECUTABLE",
            "comparison": "FULL_ENCODED_DSC_FRAME_BYTE_FOR_BYTE_AND_SHA256",
            "candidate_count": len(generated),
            "candidate_order": [item["function"] for item in generated],
            "absorbed_rtl_dependencies": absorbed_dependencies,
            "source_hash": agent.input_facts.get("source_hash"),
            "allow_incomplete": allow_incomplete,
            "incomplete_compute_gaps": gaps,
            "discovery": discovery,
            "baseline": baseline_results,
            "rewrites": rewrite_receipts,
            "compile": compile_receipt,
            "modes": mode_results,
            "promotion_status": "BLOCKED_PENDING_HUMAN_CONTRACT_REVIEW",
        }
        scrubbed = scrub_paths(result, roots)
        artifact.mkdir(parents=True, exist_ok=True)
        write_json(artifact / "matrix-receipt.json", scrubbed)
        write_json(artifact / "compile-receipt.json", scrubbed.get("compile", {}))
        write_json(artifact / "rewrite-receipts.json", scrubbed.get("rewrites", []))
        write_json(artifact / "verification-receipt.json", {
            "schema_version": 1,
            "status": status,
            "phase": PHASE_LABEL,
            "candidate_count": len(generated),
            "matrix_scope": scope,
            "profiles": len(scenarios),
            "c_only": mode_results["C_ONLY"]["status"],
            "shadow": mode_results["SHADOW"]["status"],
            "rtl_return": mode_results["RTL_RETURN"]["status"],
            "comparison": "FULL_ENCODED_DSC_FRAME_BYTE_FOR_BYTE_AND_SHA256",
            "promotion_status": "BLOCKED_PENDING_HUMAN_CONTRACT_REVIEW",
            "matrix_receipt": "matrix-receipt.json",
        })
        return result
    except Exception as error:
        return write_result({
            "schema_version": 1,
            "status": "INFRASTRUCTURE_FAILURE",
            "phase": PHASE_LABEL,
            "reason": str(error),
            "candidate_count": len(candidates),
            "discovery": discovery,
        })
    finally:
        if base_model is not None:
            shutil.rmtree(base_model.parent, ignore_errors=True)
        if overlay_model is not None:
            shutil.rmtree(overlay_model.parent, ignore_errors=True)
        if previous_scope is None:
            os.environ.pop("DSC_CICD_MATRIX_SCOPE", None)
        else:
            os.environ["DSC_CICD_MATRIX_SCOPE"] = previous_scope


def main() -> int:
    args = parse_args()
    root = args.root.resolve()
    artifact = args.artifact.resolve()
    if args.dry_run:
        result = run_encode_discovery(root, artifact)
    else:
        result = run_encode_integration(
            root,
            artifact,
            args.scope,
            max(1, args.jobs),
            allow_incomplete=args.allow_incomplete,
        )
    print(json.dumps({
        "status": result.get("status"),
        "phase": result.get("phase", PHASE_LABEL),
        "matrix_scope": result.get("matrix_scope"),
        "profiles": result.get("profiles"),
        "candidate_count": result.get("candidate_count"),
        "compute_gaps": len(
            result.get("gaps", [])
            or result.get("discovery", {}).get("frontier", {}).get("compute_gaps", [])
            or result.get("incomplete_compute_gaps", [])
        ),
        "reason": result.get("reason"),
        "duration_seconds": result.get("duration_seconds"),
    }, sort_keys=True))
    if args.dry_run:
        return 0
    return 0 if result.get("status") == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
