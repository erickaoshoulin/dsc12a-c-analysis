#!/usr/bin/env python3
"""Discover the phase-aware Encode RTL frontier.

The Encode frontier is the part of the generated C source model that is
reachable from ``DSC_Encode`` during the Encode coverage phase.  It joins the
source/facts graph, Encode coverage, the stable manifest, and provisional
verification receipts.  A provisional contract is usable here only when its
Encode ``RTL_RETURN`` receipt reports a positive invocation count.

This module intentionally reports the frontier; it does not promote
contracts, edit the original C source, or infer orchestration from an error
path such as ``fprintf`` inside a datapath function.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import pathlib
from collections import deque
from typing import Any


ROOT_FUNCTION = "DSC_Encode"
SCHEMA_VERSION = 1


def read_json(path: pathlib.Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: pathlib.Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(value, indent=2, sort_keys=True, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )


def file_hash(path: pathlib.Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def _path_trace(path: pathlib.Path | str | None) -> dict[str, Any]:
    if path is None:
        return {"path": None, "sha256": None, "exists": False}
    value = pathlib.Path(path)
    result: dict[str, Any] = {
        "path": str(value),
        "sha256": None,
        "exists": value.exists(),
        "kind": "file" if value.is_file() else "directory" if value.is_dir() else "missing",
    }
    if value.is_file():
        result["sha256"] = file_hash(value)
    return result


def _as_int(value: Any, default: int = 0) -> int:
    try:
        if isinstance(value, bool):
            return int(value)
        return int(value)
    except (TypeError, ValueError):
        return default


def _optional_int(value: Any) -> int | None:
    try:
        if isinstance(value, bool):
            return int(value)
        return int(value)
    except (TypeError, ValueError):
        return None


def _callee_name(item: Any) -> str:
    if isinstance(item, str):
        return item
    if isinstance(item, dict):
        return str(item.get("name", ""))
    return ""


def _effect_summary(
    function: dict[str, Any], candidate: dict[str, Any]
) -> dict[str, bool]:
    """Normalize candidate and Clang effect spelling into direct effects."""

    candidate_effects = candidate.get("direct_effects", {}) or {}
    function_effects = function.get("effects", {}) or {}
    fields_write = function.get("fields_write", []) or []
    pointer_parameters = function.get("pointer_parameters", []) or []
    return {
        "allocation": bool(
            candidate_effects.get("allocation") or function_effects.get("malloc")
        ),
        "assertion": bool(
            candidate_effects.get("assertion") or function_effects.get("assert")
        ),
        "indirect_call": bool(
            candidate_effects.get("indirect_call")
            or function_effects.get("indirect_call")
        ),
        "io": bool(
            candidate_effects.get("io") or function_effects.get("file_io")
        ),
        "logging": bool(
            candidate_effects.get("logging") or function_effects.get("logging")
        ),
        "state_write": bool(
            candidate_effects.get("state_write")
            or fields_write
            or any(item.get("mode") == "WRITES_THROUGH" for item in pointer_parameters)
        ),
    }


def c_orchestration_boundary(
    function: dict[str, Any], candidate: dict[str, Any]
) -> str | None:
    """Classify intentional C shells using effects and shape.

    ``fprintf``/logging alone is deliberately insufficient.  Datapath
    functions often carry error reporting on an invalid input path; treating
    that as frame orchestration would hide a compute gap.  Allocation plus
    frame I/O identifies the frame controller, allocation without it
    identifies lifecycle/reset code, and a side-effect-free one-call wrapper
    identifies a thin API shell.
    """

    effects = _effect_summary(function, candidate)
    callees = function.get("callees", []) or []
    loop_count = _as_int(function.get("loop_count", 0))
    fields_write = function.get("fields_write", []) or []
    globals_write = function.get("globals_write", []) or []

    if effects["allocation"] and effects["io"]:
        return "FRAME_IO_ORCHESTRATION"
    if effects["allocation"]:
        return "MEMORY_LIFECYCLE"

    # A small I/O-only wrapper can still be a frame shell, but an I/O-bearing
    # stateful loop is a compute boundary.  This is the distinction that keeps
    # VLCUnit's fprintf error path out of the C-shell bucket.
    if (
        effects["io"]
        and not effects["state_write"]
        and loop_count == 0
    ):
        return "FRAME_IO_ORCHESTRATION"

    direct_effect_free = not any(effects.values())
    if (
        direct_effect_free
        and len(callees) == 1
        and loop_count == 0
        and not fields_write
        and not globals_write
    ):
        return "THIN_CALL_WRAPPER"
    return None


def _reachable_names(
    functions: list[dict[str, Any]], root_name: str
) -> tuple[set[str], list[str]]:
    by_name = {
        str(item.get("name")): item
        for item in functions
        if item.get("name")
    }
    if root_name not in by_name:
        return set(), []

    reachable: set[str] = set()
    order: list[str] = []
    pending: deque[str] = deque([root_name])
    while pending:
        name = pending.popleft()
        if name in reachable:
            continue
        function = by_name.get(name)
        if function is None:
            continue
        reachable.add(name)
        order.append(name)
        for callee in function.get("callees", []) or []:
            child = _callee_name(callee)
            if child in by_name and child not in reachable:
                pending.append(child)
    return reachable, order


def _encode_rtl_return_invocations(verification: dict[str, Any]) -> int:
    """Read the Encode RTL_RETURN invocation count across receipt variants."""

    encode = verification.get("encode")
    if not isinstance(encode, dict):
        encode = {}

    direct_keys = (
        "rtl_return_invocations",
        "rtl_return_rtl_invocations",
        "total_rtl_invocations",
    )
    for key in direct_keys:
        value = _optional_int(encode.get(key))
        if value is not None:
            return value

    modes = encode.get("modes")
    if isinstance(modes, dict):
        rtl_return = modes.get("RTL_RETURN") or modes.get("rtl_return")
        if isinstance(rtl_return, dict):
            for key in direct_keys:
                value = _optional_int(rtl_return.get(key))
                if value is not None:
                    return value

    replacement = verification.get("replacement_coverage")
    if isinstance(replacement, dict):
        for key in (
            "encode_rtl_return_invocations",
            "encode_rtl_return_rtl_invocations",
        ):
            value = _optional_int(replacement.get(key))
            if value is not None:
                return value
    return 0


def _encode_status(verification: dict[str, Any]) -> str | None:
    encode = verification.get("encode")
    if not isinstance(encode, dict):
        return None
    status = encode.get("status")
    if status is not None:
        return str(status)
    modes = encode.get("modes")
    if isinstance(modes, dict):
        rtl_return = modes.get("RTL_RETURN") or modes.get("rtl_return")
        if isinstance(rtl_return, dict) and rtl_return.get("status") is not None:
            return str(rtl_return.get("status"))
    return None


def _provisional_is_encode_usable(record: dict[str, Any]) -> bool:
    """Require positive Encode RTL_RETURN evidence, even for supplied maps."""

    invocations = record.get("encode_rtl_return_invocations")
    if invocations is None:
        verification = record.get("verification")
        if isinstance(verification, dict):
            invocations = _encode_rtl_return_invocations(verification)
    if _as_int(invocations) <= 0:
        return False
    status = record.get("encode_status")
    return status in (None, "PASS")


def _provisional_receipt_trace(record: dict[str, Any]) -> dict[str, Any]:
    return {
        "kind": "provisional_verification",
        "contract_id": record.get("contract_id"),
        "contract_file": record.get("contract_file"),
        "contract_sha256": record.get("contract_sha256"),
        "candidate_file": record.get("candidate_file"),
        "candidate_sha256": record.get("candidate_sha256"),
        "verification_receipt": record.get("verification_receipt"),
        "verification_receipt_sha256": record.get("verification_receipt_sha256"),
        "matrix_scope": record.get("matrix_scope"),
        "encode_status": record.get("encode_status"),
        "encode_rtl_return_invocations": record.get(
            "encode_rtl_return_invocations", 0
        ),
    }


def _stable_receipt_trace(
    record: dict[str, Any], repo_root: pathlib.Path | None
) -> dict[str, Any]:
    result: dict[str, Any] = {
        "kind": "stable_manifest",
        "contract_id": record.get("contract_id"),
        "status": record.get("status"),
        "contract_file": record.get("contract_file"),
        "verification_file": record.get("verification_file"),
    }
    if repo_root is not None:
        for key in ("contract_file", "verification_file"):
            value = record.get(key)
            if not value:
                continue
            path = repo_root / str(value)
            result[f"{key}_trace"] = _path_trace(path)
    return result


def _source_trace(
    function: dict[str, Any], source_dir: pathlib.Path
) -> dict[str, Any]:
    source_file = function.get("source_file")
    source_path: pathlib.Path | None = None
    if source_file:
        source_path = pathlib.Path(str(source_file))
        if not source_path.is_absolute():
            source_path = source_dir / source_path
    return {
        "file": source_file,
        "line": function.get("line"),
        "end_line": function.get("end_line"),
        "path": str(source_path) if source_path is not None else None,
        "sha256": file_hash(source_path) if source_path and source_path.is_file() else None,
    }


def _coverage_count(runtime: dict[str, Any]) -> int:
    coverage = runtime.get("coverage")
    if isinstance(coverage, dict):
        return _as_int(coverage.get("execution_count"))
    return _as_int(runtime.get("execution_count"))


def _encode_profile_counts(coverage: dict[str, Any]) -> tuple[int, int]:
    runs = coverage.get("encode_runs", []) or []
    if runs:
        return len(runs), sum(item.get("status") == "PASS" for item in runs)
    artifacts = coverage.get("profile_artifacts", {}) or {}
    count = _as_int(artifacts.get("profraw_count"))
    if count:
        # The Encode coverage receipt predates the explicit encode_runs list;
        # a PASS aggregate with a profraw count is the equivalent evidence.
        return count, count if coverage.get("status") == "PASS" else 0
    return 0, 0


def _runtime_name(
    runtime: dict[str, Any], function_by_usr: dict[str, dict[str, Any]]
) -> str:
    usr = str(runtime.get("clang_usr", ""))
    function = function_by_usr.get(usr, {})
    return str(runtime.get("name") or function.get("name") or "")


def _traceability_inputs(
    traceability: dict[str, Any] | None,
) -> dict[str, Any]:
    if not traceability:
        return {}
    inputs = traceability.get("inputs", traceability)
    result: dict[str, Any] = {}
    if isinstance(inputs, dict):
        for key, value in inputs.items():
            if isinstance(value, (str, pathlib.Path)):
                result[str(key)] = _path_trace(value)
            else:
                result[str(key)] = value
    return result


def discover(
    coverage: dict[str, Any],
    functions: dict[str, Any],
    candidates: dict[str, Any],
    manifest: dict[str, Any],
    source_dir: pathlib.Path,
    provisional_verified: dict[str, dict[str, Any]] | None = None,
    *,
    traceability: dict[str, Any] | None = None,
    root_name: str = ROOT_FUNCTION,
) -> dict[str, Any]:
    """Return the Encode runtime frontier rooted at ``DSC_Encode``."""

    source_dir = pathlib.Path(source_dir)
    provisional_verified = provisional_verified or {}
    function_records = [
        item for item in functions.get("functions", [])
        if isinstance(item, dict)
    ]
    candidate_records = [
        item for item in candidates.get("functions", [])
        if isinstance(item, dict)
    ]
    function_by_usr = {
        str(item.get("clang_usr")): item
        for item in function_records
        if item.get("clang_usr")
    }
    function_by_name = {
        str(item.get("name")): item
        for item in function_records
        if item.get("name")
    }
    candidate_by_usr = {
        str(item.get("clang_usr")): item
        for item in candidate_records
        if item.get("clang_usr")
    }
    candidate_by_name = {
        str(item.get("name")): item
        for item in candidate_records
        if item.get("name")
    }
    accepted_by_name = {
        str(item.get("function")): item
        for item in manifest.get("components", [])
        if isinstance(item, dict)
        and item.get("status") == "PASS"
        and item.get("function")
    }
    reachable_names, traversal_order = _reachable_names(function_records, root_name)
    reachable_order = set(reachable_names)

    # An Encode frontier must never inherit a Decode-only provisional pass.
    encode_provisional = {
        name: record
        for name, record in provisional_verified.items()
        if _provisional_is_encode_usable(record)
    }
    available_rtl_names = set(accepted_by_name) | set(encode_provisional)

    runtime_records = [
        item for item in coverage.get("functions", [])
        if isinstance(item, dict)
        and item.get("coverage_status") == "EXECUTED"
        and _runtime_name(item, function_by_usr) in reachable_order
    ]
    # Keep one deterministic runtime row per phase function.  Coverage facts
    # normally contain one row; choosing the largest count is safer for merged
    # receipts and keeps the graph trace stable.
    runtime_by_name: dict[str, dict[str, Any]] = {}
    for runtime in runtime_records:
        name = _runtime_name(runtime, function_by_usr)
        prior = runtime_by_name.get(name)
        if prior is None or _coverage_count(runtime) > _coverage_count(prior):
            runtime_by_name[name] = runtime

    rows: list[dict[str, Any]] = []
    repo_root_value = (traceability or {}).get("repo_root") if traceability else None
    repo_root = pathlib.Path(repo_root_value) if repo_root_value else None
    for name in sorted(runtime_by_name):
        runtime = runtime_by_name[name]
        usr = str(runtime.get("clang_usr", ""))
        function = function_by_usr.get(usr) or function_by_name.get(name, {})
        if not usr:
            usr = str(function.get("clang_usr", ""))
        candidate = candidate_by_usr.get(usr) or candidate_by_name.get(name, {})
        if candidate and candidate.get("role") not in (None, "DUT"):
            continue

        accepted = accepted_by_name.get(name)
        provisional = encode_provisional.get(name)
        internal_callees = sorted({
            child
            for child in (
                _callee_name(item) for item in function.get("callees", []) or []
            )
            if child in reachable_order and child != name
        })
        missing_internal_callees = [
            child
            for child in internal_callees
            if child not in available_rtl_names
        ]
        pointer_modes = sorted({
            str(item.get("mode"))
            for item in function.get("pointer_parameters", []) or []
            if item.get("mode")
        })
        effects = _effect_summary(function, candidate)
        c_boundary = c_orchestration_boundary(function, candidate)
        blockers: list[str] = []
        if effects["state_write"]:
            blockers.append("EXPLICIT_STATE_OUTPUT_CONTRACT_REQUIRED")
        if "WRITES_THROUGH" in pointer_modes:
            blockers.append("POINTER_OUTPUT_CONTRACT_REQUIRED")
        if not candidate.get("bounded_computation", False):
            blockers.append("LOOP_BOUND_OR_DECOMPOSITION_REQUIRED")
        if missing_internal_callees:
            blockers.append("MISSING_CALLEE_RTL")
        if (effects["io"] or effects["logging"] or effects["assertion"]) and not c_boundary:
            blockers.append("ERROR_PATH_SIDE_EFFECTS_REQUIRE_LEGAL_DOMAIN_SEPARATION")

        if accepted:
            rtl_status = "STABLE_RTL"
            frontier_class = "RTL"
        elif provisional:
            rtl_status = "PROVISIONAL_RTL_PASS"
            frontier_class = "RTL"
        elif c_boundary:
            rtl_status = "C_ORCHESTRATION_BOUNDARY"
            frontier_class = "C_SHELL"
        else:
            rtl_status = "COMPUTE_GAP"
            frontier_class = "COMPUTE_GAP"

        receipt_trace: dict[str, Any]
        if accepted:
            receipt_trace = _stable_receipt_trace(accepted, repo_root)
        elif provisional:
            receipt_trace = _provisional_receipt_trace(provisional)
        else:
            receipt_trace = {"kind": None}

        row = {
            "clang_usr": usr,
            "name": name,
            "source_file": function.get("source_file"),
            "line": function.get("line"),
            "end_line": function.get("end_line"),
            "execution_count": _coverage_count(runtime),
            "runtime_status": runtime.get("coverage_status"),
            "rtl_status": rtl_status,
            "frontier_class": frontier_class,
            "accepted_contract_id": accepted.get("contract_id") if accepted else None,
            "provisional_contract_id": provisional.get("contract_id") if provisional else None,
            "provisional_encode_rtl_return_invocations": (
                provisional.get("encode_rtl_return_invocations", 0)
                if provisional else 0
            ),
            "auto_eligible": bool(candidate.get("eligible")),
            "purity": candidate.get("purity"),
            "timing": candidate.get("timing"),
            "bounded_computation": bool(candidate.get("bounded_computation")),
            "pointer_modes": pointer_modes,
            "direct_effects": effects,
            "internal_callees": internal_callees,
            "missing_internal_callees": missing_internal_callees,
            "leaf_at_current_rtl_frontier": not missing_internal_callees,
            "blockers": blockers,
            "c_boundary_class": c_boundary,
            "traceability": {
                "source": _source_trace(function, source_dir),
                "facts": {
                    "clang_usr": usr,
                    "functions_record_present": bool(function),
                    "candidate_record_present": bool(candidate),
                },
                "coverage": {
                    "phase": "encode",
                    "coverage_status": runtime.get("coverage_status"),
                    "execution_count": _coverage_count(runtime),
                },
                "receipt": receipt_trace,
            },
        }
        rows.append(row)

    stable_runtime = [item for item in rows if item["rtl_status"] == "STABLE_RTL"]
    provisional_runtime = [
        item for item in rows if item["rtl_status"] == "PROVISIONAL_RTL_PASS"
    ]
    c_shell_runtime = [
        item for item in rows if item["rtl_status"] == "C_ORCHESTRATION_BOUNDARY"
    ]
    compute_gaps = [item for item in rows if item["rtl_status"] == "COMPUTE_GAP"]
    reached_names = {item["name"] for item in rows}

    # Keep static-but-uncovered functions in a separate traceable bucket.  They
    # are not Encode compute gaps until the Encode coverage phase reaches them.
    coverage_by_name = {
        _runtime_name(item, function_by_usr): item
        for item in coverage.get("functions", [])
        if isinstance(item, dict)
    }
    unreached_root_functions: list[dict[str, Any]] = []
    for name in sorted(reachable_names - reached_names):
        function = function_by_name.get(name, {})
        runtime = coverage_by_name.get(name, {})
        candidate = candidate_by_usr.get(str(function.get("clang_usr"))) or candidate_by_name.get(name, {})
        unreached_root_functions.append({
            "clang_usr": function.get("clang_usr"),
            "name": name,
            "source_file": function.get("source_file"),
            "line": function.get("line"),
            "end_line": function.get("end_line"),
            "runtime_status": runtime.get("coverage_status", "NOT_REACHED"),
            "execution_count": _coverage_count(runtime),
            "reason": "NOT_EXECUTED_IN_ENCODE_COVERAGE",
            "traceability": {
                "source": _source_trace(function, source_dir),
                "facts": {
                    "clang_usr": function.get("clang_usr"),
                    "functions_record_present": bool(function),
                    "candidate_record_present": bool(candidate),
                },
                "coverage": {
                    "phase": "encode",
                    "coverage_status": runtime.get("coverage_status", "NOT_REACHED"),
                    "execution_count": _coverage_count(runtime),
                },
                "receipt": {"kind": None},
            },
        })

    input_trace = _traceability_inputs(traceability)
    encode_profiles, encode_profiles_passed = _encode_profile_counts(coverage)
    traceability_output = {
        "root_function": root_name,
        "root_graph": {
            "reachable_function_count": len(reachable_names),
            "reachable_function_names": sorted(reachable_names),
            "traversal_order": traversal_order,
        },
        "encode_profiles": encode_profiles,
        "encode_profiles_passed": encode_profiles_passed,
        "inputs": input_trace,
        "source_dir": str(source_dir),
        "policy": (
            "Encode phase only; stable manifest PASS plus provisional verification "
            "with positive Encode RTL_RETURN invocation count; no function allowlist"
        ),
    }

    summary = {
        "root_function": root_name,
        "root_graph_functions": len(reachable_names),
        "phase_reached_functions": len(rows),
        "phase_unreached_root_functions": len(unreached_root_functions),
        "encode_profiles": encode_profiles,
        "encode_profiles_passed": encode_profiles_passed,
        "reached": len(rows),
        "rtl": len(stable_runtime) + len(provisional_runtime),
        "stable_rtl": len(stable_runtime),
        "provisional_rtl": len(provisional_runtime),
        "c_shell": len(c_shell_runtime),
        "compute_gap": len(compute_gaps),
        # Decode-frontier-compatible names make the two reports easy to join.
        "runtime_source_functions": len(coverage.get("functions", []) or []),
        "runtime_dut_functions": len(rows),
        "runtime_dut_with_stable_rtl": len(stable_runtime),
        "runtime_dut_with_provisional_rtl": len(provisional_runtime),
        "runtime_dut_c_orchestration_boundaries": len(c_shell_runtime),
        "runtime_dut_without_any_rtl": len(c_shell_runtime) + len(compute_gaps),
        "runtime_compute_functions_without_any_rtl": len(compute_gaps),
    }

    return {
        "schema_version": SCHEMA_VERSION,
        "status": "PASS",
        "root_function": root_name,
        "discovery_policy": (
            "Encode-only root graph from DSC_Encode; no function-name allowlist; "
            "provisional RTL requires positive Encode RTL_RETURN evidence"
        ),
        "coverage_phase": "encode",
        "coverage_phases": coverage.get("coverage_phases", "encode"),
        "summary": summary,
        "reached": rows,
        "rtl": stable_runtime + provisional_runtime,
        "stable_runtime_functions": stable_runtime,
        "provisional_runtime_functions": provisional_runtime,
        "c_shell": c_shell_runtime,
        "c_shell_runtime_functions": c_shell_runtime,
        "c_orchestration_runtime_functions": c_shell_runtime,
        "compute_gap": compute_gaps,
        "compute_gap_runtime_functions": compute_gaps,
        "missing_runtime_functions": compute_gaps,
        "unreached_root_functions": unreached_root_functions,
        "provisional_transition_candidates": [],
        "traceability": traceability_output,
    }


def _phase_matrix_receipt(receipt: dict[str, Any]) -> dict[str, Any]:
    encode = receipt.get("encode")
    if isinstance(encode, dict) and (
        "modes" in encode or "candidate_count" in encode or "profiles" in encode
    ):
        return encode
    return receipt


def attach_integration_receipt(
    frontier: dict[str, Any], receipt_path: pathlib.Path | None
) -> None:
    if receipt_path is None or not receipt_path.is_file():
        frontier["multi_rtl_integration"] = {"status": "NOT_RUN", "phase": "encode"}
        return
    receipt = read_json(receipt_path)
    phase_receipt = _phase_matrix_receipt(receipt)
    modes = phase_receipt.get("modes", {}) or {}
    frontier["multi_rtl_integration"] = {
        "phase": "encode",
        "status": phase_receipt.get("status", receipt.get("status")),
        "receipt": str(receipt_path),
        "receipt_sha256": file_hash(receipt_path),
        "matrix_scope": phase_receipt.get("matrix_scope", receipt.get("matrix_scope")),
        "profiles": phase_receipt.get("profiles", receipt.get("profiles")),
        "candidate_count": phase_receipt.get(
            "candidate_count", receipt.get("candidate_count")
        ),
        "comparison": phase_receipt.get("comparison", receipt.get("comparison")),
        "modes": {
            mode: {
                "status": (modes.get(mode, {}) or {}).get("status"),
                "total_rtl_invocations": (
                    modes.get(mode, {}) or {}
                ).get("total_rtl_invocations", 0),
                "all_candidates_reached": (
                    modes.get(mode, {}) or {}
                ).get("all_candidates_reached"),
            }
            for mode in ("C_ONLY", "SHADOW", "RTL_RETURN")
        },
    }
    traceability = frontier.setdefault("traceability", {})
    traceability["integration_receipt"] = _path_trace(receipt_path)


def scan_provisional(root: pathlib.Path | None) -> dict[str, dict[str, Any]]:
    """Scan only full-matrix provisional receipts usable by Encode."""

    if root is None or not root.is_dir():
        return {}
    result: dict[str, dict[str, Any]] = {}
    for verification_path in sorted(root.rglob("verification-receipt.json")):
        verification = read_json(verification_path)
        if (
            verification.get("status") != "PASS"
            or verification.get("matrix_scope") != "all"
        ):
            continue
        encode_invocations = _encode_rtl_return_invocations(verification)
        encode_status = _encode_status(verification)
        if encode_invocations <= 0 or encode_status not in (None, "PASS"):
            continue
        contract_path = verification_path.parent / "provisional-contract.json"
        if not contract_path.is_file():
            continue
        contract = read_json(contract_path)
        function = contract.get("function", {}) or {}
        name = str(function.get("name", ""))
        if not name:
            continue
        candidate_path = verification_path.parent / "candidate_01.sv"
        record = {
            "contract_id": contract.get("contract_id"),
            "verification_receipt": str(verification_path),
            "verification_receipt_sha256": file_hash(verification_path),
            "contract_file": str(contract_path),
            "contract_sha256": file_hash(contract_path),
            "candidate_file": str(candidate_path) if candidate_path.is_file() else None,
            "candidate_sha256": file_hash(candidate_path) if candidate_path.is_file() else None,
            "matrix_scope": verification.get("matrix_scope"),
            "status": verification.get("status"),
            "encode_status": encode_status,
            "encode_rtl_return_invocations": encode_invocations,
            "semantics_kind": (contract.get("semantics", {}) or {}).get("kind"),
            "max_bits": (contract.get("semantics", {}) or {}).get("max_bits"),
            "window_bytes": (contract.get("semantics", {}) or {}).get("window_bytes"),
            "function": {
                "clang_usr": function.get("clang_usr"),
                "name": name,
                "source_file": function.get("source_file"),
                "source_span": function.get("source_span"),
            },
        }
        previous = result.get(name)
        if previous is None or (
            encode_invocations,
            str(verification_path),
        ) > (
            _as_int(previous.get("encode_rtl_return_invocations")),
            str(previous.get("verification_receipt", "")),
        ):
            result[name] = record
    return result


def render_report(frontier: dict[str, Any]) -> str:
    summary = frontier.get("summary", {})
    integration = frontier.get("multi_rtl_integration", {}) or {}
    traceability = frontier.get("traceability", {}) or {}
    lines = [
        "# Encode RTL frontier",
        "",
        "Generated from the DSC_Encode root graph, Encode coverage, Clang facts, the stable RTL manifest, and phase-specific provisional receipts.",
        "No function-name allowlist is used.",
        "",
        f"- root: `{frontier.get('root_function', ROOT_FUNCTION)}`",
        f"- reached Encode functions: {summary.get('reached', 0)}",
        f"- RTL reached: {summary.get('rtl', 0)} ({summary.get('stable_rtl', 0)} stable, {summary.get('provisional_rtl', 0)} provisional)",
        f"- C shells: {summary.get('c_shell', 0)}",
        f"- compute gaps: {summary.get('compute_gap', 0)}",
        f"- root functions not executed in Encode coverage: {summary.get('phase_unreached_root_functions', 0)}",
        f"- simultaneous Encode multi-RTL integration: {integration.get('status', 'NOT_RUN')}",
        "",
        "## Traceability inputs",
        "",
        f"- source directory: `{traceability.get('source_dir', '')}`",
    ]
    for key, item in sorted((traceability.get("inputs", {}) or {}).items()):
        if isinstance(item, dict):
            lines.append(
                f"- {key}: `{item.get('path')}` ({item.get('sha256') or 'unhashed/unavailable'})"
            )
    lines.extend([
        "",
        "## Reached Encode functions",
        "",
        "| Function | Class | Calls | Source | Receipt |",
        "|---|---|---:|---|---|",
    ])
    for item in frontier.get("reached", []):
        receipt = item.get("provisional_contract_id") or item.get("accepted_contract_id") or "C/source"
        source = f"{item.get('source_file')}:{item.get('line')}"
        lines.append(
            f"| {item.get('name')} | {item.get('frontier_class')} | {item.get('execution_count', 0)} | {source} | {receipt} |"
        )
    if not frontier.get("reached"):
        lines.append("| none | none | 0 | none | none |")

    lines.extend([
        "",
        "## RTL reached",
        "",
        "| Function | Calls | Contract | Encode RTL_RETURN invocations |",
        "|---|---:|---|---:|",
    ])
    for item in frontier.get("rtl", []):
        lines.append(
            f"| {item.get('name')} | {item.get('execution_count', 0)} | "
            f"{item.get('accepted_contract_id') or item.get('provisional_contract_id')} | "
            f"{item.get('provisional_encode_rtl_return_invocations', 0)} |"
        )
    if not frontier.get("rtl"):
        lines.append("| none | 0 | none | 0 |")

    lines.extend([
        "",
        "## C shells",
        "",
        "| Function | Calls | Boundary | Source |",
        "|---|---:|---|---|",
    ])
    for item in frontier.get("c_shell", []):
        lines.append(
            f"| {item.get('name')} | {item.get('execution_count', 0)} | "
            f"{item.get('c_boundary_class')} | {item.get('source_file')}:{item.get('line')} |"
        )
    if not frontier.get("c_shell"):
        lines.append("| none | 0 | none | none |")

    lines.extend([
        "",
        "## Compute gaps",
        "",
        "| Function | Calls | Frontier | Required work | Source |",
        "|---|---:|---|---|---|",
    ])
    for item in frontier.get("compute_gap", []):
        blockers = ", ".join(item.get("blockers", [])) or "RTL contract required"
        lines.append(
            f"| {item.get('name')} | {item.get('execution_count', 0)} | "
            f"{'leaf' if item.get('leaf_at_current_rtl_frontier') else 'composite'} | "
            f"{blockers} | {item.get('source_file')}:{item.get('line')} |"
        )
    if not frontier.get("compute_gap"):
        lines.append("| none | 0 | complete | none | none |")

    lines.extend([
        "",
        "## Root functions not reached by Encode coverage",
        "",
        "| Function | Source | Reason |",
        "|---|---|---|",
    ])
    for item in frontier.get("unreached_root_functions", []):
        lines.append(
            f"| {item.get('name')} | {item.get('source_file')}:{item.get('line')} | {item.get('reason')} |"
        )
    if not frontier.get("unreached_root_functions"):
        lines.append("| none | none | none |")
    return "\n".join(lines) + "\n"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--coverage", type=pathlib.Path, required=True)
    parser.add_argument("--functions", type=pathlib.Path, required=True)
    parser.add_argument("--candidates", type=pathlib.Path, required=True)
    parser.add_argument("--manifest", type=pathlib.Path, required=True)
    parser.add_argument("--source-dir", type=pathlib.Path, required=True)
    parser.add_argument("--provisional-root", type=pathlib.Path)
    parser.add_argument("--integration-receipt", type=pathlib.Path)
    parser.add_argument("--output", type=pathlib.Path, required=True)
    parser.add_argument("--report", type=pathlib.Path, required=True)
    parser.add_argument("--root", default=ROOT_FUNCTION)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    input_paths = {
        "coverage": args.coverage.resolve(),
        "functions": args.functions.resolve(),
        "candidates": args.candidates.resolve(),
        "manifest": args.manifest.resolve(),
        "provisional_root": args.provisional_root.resolve()
        if args.provisional_root else None,
    }
    frontier = discover(
        read_json(args.coverage),
        read_json(args.functions),
        read_json(args.candidates),
        read_json(args.manifest),
        args.source_dir.resolve(),
        scan_provisional(args.provisional_root.resolve() if args.provisional_root else None),
        traceability={
            "repo_root": args.manifest.resolve().parent.parent,
            "inputs": input_paths,
        },
        root_name=args.root,
    )
    attach_integration_receipt(
        frontier,
        args.integration_receipt.resolve() if args.integration_receipt else None,
    )
    write_json(args.output, frontier)
    args.report.parent.mkdir(parents=True, exist_ok=True)
    args.report.write_text(render_report(frontier), encoding="utf-8")
    print(
        "encode frontier: "
        f"{frontier['summary']['rtl']} RTL-reached, "
        f"{frontier['summary']['compute_gap']} compute gaps"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
