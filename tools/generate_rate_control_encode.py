#!/usr/bin/env python3
"""Discover and render the Encode-specialized rate-control transition.

This module deliberately stops at contract/RTL generation.  It does not
modify the immutable C model, write a promotion receipt, or update the
existing CI/CD adapter.  Candidate selection is based on Clang facts,
coverage, source shape, and a hash-verified state-memory child transition.
Names are retained as metadata, but are never used as a selection allowlist.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import pathlib
import re
from typing import Any, Iterable


REQUIRED_CONFIG_FIELDS = {
    ("bits_per_component", "int"),
    ("bits_per_pixel", "int"),
    ("dsc_version_minor", "int"),
    ("initial_xmit_delay", "int"),
    ("native_420", "int"),
    ("native_422", "int"),
    ("rc_buf_thresh", "int[14]"),
    ("rc_edge_factor", "int"),
    ("rc_model_size", "int"),
    ("rc_quant_incr_limit0", "int"),
    ("rc_quant_incr_limit1", "int"),
    ("rc_range_parameters", "dsc_range_cfg_t[15]"),
    ("rc_tgt_offset_hi", "int"),
    ("rc_tgt_offset_lo", "int"),
    ("rcb_bits", "int"),
}

REQUIRED_RANGE_FIELDS = {
    ("range_bpg_offset", "int"),
    ("range_max_qp", "int"),
    ("range_min_qp", "int"),
}

REQUIRED_STATE_READ_FIELDS = {
    ("bitSaveMode", "int"),
    ("bufferFullness", "int"),
    ("codedGroupSize", "int"),
    ("cpntBitDepth", "int[4]"),
    ("firstFlat", "int"),
    ("ichSelected", "int"),
    ("isEncoder", "int"),
    ("midpointSelected", "int[4]"),
    ("mppState", "int"),
    ("pixelCount", "int"),
    ("predictedSize", "int[4]"),
    ("prevQp", "int"),
    ("prevRange", "int"),
    ("rcSizeGroup", "int"),
    ("rcSizeUnit", "int[4]"),
    ("stQp", "int"),
    ("unitsPerGroup", "int"),
    ("useMidpoint", "int[4]"),
    ("vPos", "int"),
}

REQUIRED_STATE_WRITE_FIELDS = {
    ("bitSaveMode", "int"),
    ("errorOccurred", "int"),
    ("mppState", "int"),
    ("pixelCount", "int"),
    ("prevQp", "int"),
    ("prevRange", "int"),
    ("rcSizeGroup", "int"),
    ("stQp", "int"),
}

CHILD_INPUTS = {
    "cfg_bits_per_pixel",
    "cfg_chunk_size",
    "cfg_vbr_enable",
    "state_bitsclamped",
    "state_bpgfracaccum",
    "state_bufferfullness",
    "state_chunkcount",
    "state_chunkpixeltimes",
    "state_isencoder",
    "state_numbitschunk",
    "state_slicewidth",
}

CHILD_OUTPUTS = {
    "state_bitsclamped_out",
    "state_bpgfracaccum_out",
    "state_bufferfullness_out",
    "state_chunkcount_out",
    "state_chunkpixeltimes_out",
    "state_numbitschunk_out",
    "chunk_write_enable",
    "chunk_write_index",
    "chunk_write_value",
}


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


def safe_identifier(value: str) -> str:
    result = re.sub(r"[^A-Za-z0-9_]", "_", value).lower()
    return ("c_" + result) if result[:1].isdigit() else result


def integer_define(source_dir: pathlib.Path, name: str) -> int:
    pattern = re.compile(
        r"^[ \t]*#[ \t]*define[ \t]+" + re.escape(name) + r"[ \t]+([0-9]+)\b",
        re.MULTILINE,
    )
    matches: set[int] = set()
    for source in sorted((*source_dir.glob("*.h"), *source_dir.glob("*.c"))):
        match = pattern.search(source.read_text(encoding="utf-8", errors="replace"))
        if match:
            matches.add(int(match.group(1)))
    if len(matches) != 1:
        raise RuntimeError(f"expected one integer definition for {name}, got {sorted(matches)}")
    return next(iter(matches))


def _document_rows(document: dict[str, Any] | list[dict[str, Any]]) -> list[dict[str, Any]]:
    if isinstance(document, list):
        return document
    rows = document.get("functions", [])
    if not isinstance(rows, list):
        raise RuntimeError("facts document has no function list")
    return rows


def _by_usr(document: dict[str, Any] | list[dict[str, Any]]) -> dict[str, dict[str, Any]]:
    return {
        str(row.get("clang_usr")): row
        for row in _document_rows(document)
        if row.get("clang_usr")
    }


def _body(function: dict[str, Any], source_dir: pathlib.Path) -> str:
    source = source_dir / str(function.get("source_file", ""))
    if not source.is_file():
        raise RuntimeError(f"source file is missing: {source}")
    lines = source.read_text(encoding="utf-8", errors="replace").splitlines()
    start = int(function.get("line", 1))
    end = int(function.get("end_line", start))
    if start < 1 or end < start or end > len(lines):
        raise RuntimeError(f"invalid source span for {function.get('name')}")
    return "\n".join(lines[start - 1 : end])


def _field_set(function: dict[str, Any], key: str, record: str) -> set[tuple[str, str]]:
    return {
        (str(item.get("name")), str(item.get("type")))
        for item in function.get(key, []) or []
        if item.get("record") == record
    }


def _scalar_parameters(function: dict[str, Any]) -> list[dict[str, Any]]:
    return [item for item in function.get("parameters", []) or [] if not item.get("pointer")]


def _has_rate_control_loops(function: dict[str, Any], source_text: str) -> bool:
    loops = function.get("loops", []) or []
    conditions = {str(loop.get("condition", "")).replace(" ", "") for loop in loops}
    structural_loop_shape = (
        any("<group_size" in condition for condition in conditions)
        and any("<dsc_state->unitsPerGroup" in condition for condition in conditions)
        and any(condition == "i>0" for condition in conditions)
    )
    source_shape = (
        re.search(r"for\s*\([^;]*<\s*group_size", source_text) is not None
        and re.search(r"for\s*\([^;]*<\s*dsc_state->unitsPerGroup", source_text) is not None
        and re.search(r"for\s*\([^;]*i\s*>\s*0", source_text) is not None
    )
    return structural_loop_shape or source_shape


def _is_state_memory_child(function: dict[str, Any], source_dir: pathlib.Path) -> bool:
    parameters = function.get("parameters", []) or []
    pointers = function.get("pointer_parameters", []) or []
    pointer_types = {str(item.get("type")) for item in pointers}
    if (
        str(function.get("return_type")) != "void"
        or len(parameters) != 2
        or pointer_types != {"dsc_cfg_t *", "dsc_state_t *"}
    ):
        return False
    state_writes = _field_set(function, "fields_write", "dsc_state_t")
    state_reads = _field_set(function, "fields_read", "dsc_state_t")
    required_writes = {
        ("bitsClamped", "int"),
        ("bpgFracAccum", "int"),
        ("bufferFullness", "int"),
        ("chunkCount", "int"),
        ("chunkPixelTimes", "int"),
        ("chunkSizes", "int *"),
        ("numBitsChunk", "int"),
    }
    required_reads = {
        ("bitsClamped", "int"),
        ("bpgFracAccum", "int"),
        ("chunkPixelTimes", "int"),
        ("isEncoder", "int"),
        ("numBitsChunk", "int"),
        ("sliceWidth", "int"),
    }
    if not required_writes.issubset(state_writes) or not required_reads.issubset(state_reads):
        return False
    text = _body(function, source_dir)
    return (
        "vbr_enable" in text
        and "chunkSizes" in text
        and "sliceWidth" in text
        and "bpgFracAccum" in text
    )


def _contract_has_proven_child_shape(contract: dict[str, Any]) -> bool:
    if (contract.get("semantics", {}) or {}).get("kind") != "scalar_record_memory_transition":
        return False
    ports = {
        str(port.get("name")): port
        for port in (contract.get("interface", {}) or {}).get("ports", []) or []
    }
    return CHILD_INPUTS.issubset(ports) and CHILD_OUTPUTS.issubset(ports)


def _repo_relative(path: pathlib.Path, repo_root: pathlib.Path) -> str:
    try:
        return str(path.resolve().relative_to(repo_root.resolve()))
    except ValueError:
        return str(path.resolve())


def _resolve_repo_path(value: str | pathlib.Path, repo_root: pathlib.Path) -> pathlib.Path:
    path = pathlib.Path(str(value))
    return path if path.is_absolute() else repo_root / path


def _proven_dependency(
    callee: dict[str, Any], repo_root: pathlib.Path
) -> dict[str, Any] | None:
    """Find a PASSed, RTL-exercised child by facts/contract shape and hashes."""
    callee_usr = str(callee.get("clang_usr", ""))
    candidates_root = repo_root / "rtl"
    matches: list[dict[str, Any]] = []
    if not candidates_root.is_dir():
        return None
    for contract_path in sorted(candidates_root.rglob("provisional-contract.json")):
        try:
            contract = read_json(contract_path)
        except (OSError, ValueError, TypeError):
            continue
        function_meta = contract.get("function", {}) or {}
        if str(function_meta.get("clang_usr", "")) != callee_usr:
            continue
        if not _contract_has_proven_child_shape(contract):
            continue
        artifact_dir = contract_path.parent
        matrix_path = artifact_dir / "matrix-receipt.json"
        rtl_return_path = artifact_dir / "rtl-return-receipt.json"
        candidate_path = artifact_dir / "candidate_01.sv"
        if not (matrix_path.is_file() and rtl_return_path.is_file() and candidate_path.is_file()):
            continue
        try:
            matrix = read_json(matrix_path)
            rtl_return = read_json(rtl_return_path)
        except (OSError, ValueError, TypeError):
            continue
        if matrix.get("status") != "PASS" or matrix.get("matrix_scope") != "all":
            continue
        if rtl_return.get("status") != "PASS":
            continue
        invocations = int(rtl_return.get("total_rtl_invocations", 0) or 0)
        if invocations <= 0:
            continue
        module = safe_identifier(str(contract.get("contract_id", "")))
        if not re.search(rf"\bmodule\s+{re.escape(module)}\s*\(", candidate_path.read_text(encoding="utf-8")):
            continue
        matches.append(
            {
                "role": "remove_one_pixel_bits",
                "function": function_meta.get("name"),
                "clang_usr": callee_usr,
                "contract_id": contract.get("contract_id"),
                "module": module,
                "contract_file": _repo_relative(contract_path, repo_root),
                "contract_sha256": file_hash(contract_path),
                "module_file": _repo_relative(candidate_path, repo_root),
                "module_sha256": file_hash(candidate_path),
                "matrix_receipt_file": _repo_relative(matrix_path, repo_root),
                "rtl_return_receipt_file": _repo_relative(rtl_return_path, repo_root),
                "rtl_return_invocations": invocations,
            }
        )
    if not matches:
        return None
    matches.sort(key=lambda row: (-int(row["rtl_return_invocations"]), str(row["contract_file"])))
    return matches[0]


def _rate_control_shape(
    function: dict[str, Any],
    candidate: dict[str, Any] | None,
    coverage: dict[str, Any] | None,
    source_dir: pathlib.Path,
    facts_by_usr: dict[str, dict[str, Any]],
) -> tuple[bool, dict[str, Any] | None, str]:
    parameters = function.get("parameters", []) or []
    pointers = function.get("pointer_parameters", []) or []
    pointer_types = {str(item.get("type")) for item in pointers}
    scalars = _scalar_parameters(function)
    source_text = _body(function, source_dir)
    covered = bool((coverage or {}).get("coverage", {}).get("covered"))
    execution_count = int((coverage or {}).get("coverage", {}).get("execution_count", 0) or 0)
    structural = (
        str(function.get("return_type")) == "void"
        and len(parameters) == 7
        and pointer_types == {"dsc_cfg_t *", "dsc_state_t *"}
        and len(scalars) == 5
        and all(str(item.get("type")) == "int" for item in scalars)
        and REQUIRED_CONFIG_FIELDS.issubset(_field_set(function, "fields_read", "dsc_cfg_t"))
        and REQUIRED_RANGE_FIELDS.issubset(_field_set(function, "fields_read", "dsc_range_cfg_t"))
        and REQUIRED_STATE_READ_FIELDS.issubset(_field_set(function, "fields_read", "dsc_state_t"))
        and REQUIRED_STATE_WRITE_FIELDS.issubset(_field_set(function, "fields_write", "dsc_state_t"))
        and "isEncoder" in source_text
        and "midpointSelected" in source_text
        and "useMidpoint" in source_text
        and "rc_model_size" in source_text
        and "rc_buf_thresh" in source_text
        and "rc_range_parameters" in source_text
        and _has_rate_control_loops(function, source_text)
    )
    if not structural:
        return False, None, "rate-control source/fact shape is incomplete"
    if not bool((candidate or {}).get("production_reachable", False)):
        return False, None, "candidate is not production reachable"
    if not covered or execution_count <= 0:
        return False, None, "coverage is not executed"
    child_fact: dict[str, Any] | None = None
    for callee in function.get("callees", []) or []:
        callee_fact = facts_by_usr.get(str(callee.get("clang_usr", "")))
        if callee_fact and _is_state_memory_child(callee_fact, source_dir):
            child_fact = callee_fact
            break
    if child_fact is None:
        return False, None, "no structural state-memory child callee"
    return True, child_fact, "covered encoder RC state transition with bounded child composition"


def discover_rate_control_encode_candidates(
    functions: dict[str, Any] | list[dict[str, Any]],
    candidates: dict[str, Any] | list[dict[str, Any]],
    coverage: dict[str, Any] | list[dict[str, Any]],
    source_dir: pathlib.Path,
    repo_root: pathlib.Path | None = None,
) -> list[dict[str, Any]]:
    """Discover all structural/covered Encode RC candidates.

    The returned rows are deterministic and contain dependency evidence, but
    no function-name-based filtering is performed.
    """
    source_dir = pathlib.Path(source_dir)
    repo_root = pathlib.Path(repo_root or pathlib.Path(__file__).resolve().parent.parent)
    function_rows = _document_rows(functions)
    candidate_by_usr = _by_usr(candidates)
    coverage_by_usr = _by_usr(coverage)
    facts_by_usr = _by_usr(functions)
    discovered: list[dict[str, Any]] = []
    for function in function_rows:
        usr = str(function.get("clang_usr", ""))
        candidate = candidate_by_usr.get(usr)
        coverage_row = coverage_by_usr.get(usr)
        try:
            matches, child_fact, reason = _rate_control_shape(
                function, candidate, coverage_row, source_dir, facts_by_usr
            )
        except (OSError, RuntimeError, ValueError):
            continue
        if not matches or child_fact is None:
            continue
        dependency = _proven_dependency(child_fact, repo_root)
        if dependency is None:
            continue
        discovered.append(
            {
                "name": function.get("name"),
                "qualified_name": function.get("qualified_name", function.get("name")),
                "clang_usr": usr,
                "source_file": function.get("source_file"),
                "line": function.get("line"),
                "end_line": function.get("end_line"),
                "source_body_sha256": hashlib.sha256(
                    _body(function, source_dir).encode("utf-8")
                ).hexdigest(),
                "semantics_kind": "bounded_rate_control_encode_transition",
                "execution_count": int(
                    (coverage_row or {}).get("coverage", {}).get("execution_count", 0) or 0
                ),
                "selection_basis": reason,
                "structural_evidence": {
                    "pointer_types": sorted(
                        str(item.get("type"))
                        for item in function.get("pointer_parameters", []) or []
                    ),
                    "scalar_parameter_types": [
                        str(item.get("type")) for item in _scalar_parameters(function)
                    ],
                    "loop_conditions": [
                        item.get("condition") for item in function.get("loops", []) or []
                    ],
                    "direct_state_writes": sorted(
                        name for name, _ in _field_set(function, "fields_write", "dsc_state_t")
                    ),
                    "child_clang_usr": child_fact.get("clang_usr"),
                },
                "literal_size_bound": {
                    "group_size": [1, 3],
                    "max_remove_stages": 3,
                    "child_callee": child_fact.get("name"),
                    "child_clang_usr": child_fact.get("clang_usr"),
                    "dependency": dependency,
                },
            }
        )
    discovered.sort(
        key=lambda row: (-int(row.get("execution_count", 0)), int(row.get("line", 0) or 0), str(row.get("name")))
    )
    return discovered


def select_candidate(candidates: Iterable[dict[str, Any]]) -> dict[str, Any]:
    rows = list(candidates)
    if not rows:
        raise RuntimeError("no covered structural Encode rate-control candidate")
    return sorted(
        rows,
        key=lambda row: (-int(row.get("execution_count", 0)), int(row.get("line", 0) or 0), str(row.get("name"))),
    )[0]


def _port(name: str, direction: str, width: int = 32, signed: bool = True) -> dict[str, Any]:
    return {"name": name, "direction": direction, "width": width, "signed": signed}


def _state_port_map(fields: Iterable[str]) -> dict[str, str]:
    return {field: f"state_{safe_identifier(field)}" for field in fields}


def _verify_dependency(
    dependency: dict[str, Any], repo_root: pathlib.Path
) -> tuple[dict[str, Any], pathlib.Path, pathlib.Path]:
    contract_path = _resolve_repo_path(dependency["contract_file"], repo_root)
    module_path = _resolve_repo_path(dependency["module_file"], repo_root)
    if not contract_path.is_file() or not module_path.is_file():
        raise RuntimeError("rate-control child artifact is missing")
    if file_hash(contract_path) != str(dependency.get("contract_sha256")):
        raise RuntimeError("rate-control child contract hash changed")
    if file_hash(module_path) != str(dependency.get("module_sha256")):
        raise RuntimeError("rate-control child module hash changed")
    child_contract = read_json(contract_path)
    if (
        child_contract.get("contract_id") != dependency.get("contract_id")
        or safe_identifier(str(child_contract.get("contract_id"))) != dependency.get("module")
        or not _contract_has_proven_child_shape(child_contract)
    ):
        raise RuntimeError("rate-control child contract shape changed")
    matrix_path = _resolve_repo_path(dependency.get("matrix_receipt_file", ""), repo_root)
    rtl_return_path = _resolve_repo_path(dependency.get("rtl_return_receipt_file", ""), repo_root)
    if not matrix_path.is_file() or not rtl_return_path.is_file():
        raise RuntimeError("rate-control child proof receipts are missing")
    matrix = read_json(matrix_path)
    if matrix.get("status") != "PASS" or matrix.get("matrix_scope") != "all":
        raise RuntimeError("rate-control child matrix is not a full PASS")
    rtl_return = read_json(rtl_return_path)
    if rtl_return.get("status") != "PASS" or int(rtl_return.get("total_rtl_invocations", 0) or 0) <= 0:
        raise RuntimeError("rate-control child has no RTL_RETURN proof")
    return child_contract, contract_path, module_path


def build_rate_control_encode_contract(
    selected: dict[str, Any],
    function: dict[str, Any],
    source_dir: pathlib.Path,
    repo_root: pathlib.Path | None = None,
) -> dict[str, Any]:
    """Build the bounded Encode contract from a structural discovery row."""
    repo_root = pathlib.Path(repo_root or pathlib.Path(__file__).resolve().parent.parent)
    if selected.get("semantics_kind") != "bounded_rate_control_encode_transition":
        raise RuntimeError("selection is not an Encode rate-control transition")
    source_text = _body(function, pathlib.Path(source_dir))
    selected_hash = selected.get("source_body_sha256")
    if selected_hash and hashlib.sha256(source_text.encode("utf-8")).hexdigest() != str(selected_hash):
        raise RuntimeError("immutable Encode rate-control source span changed")
    evidence = selected.get("literal_size_bound", {}) or {}
    dependency = dict(evidence.get("dependency", {}) or selected.get("dependency", {}) or {})
    if not dependency:
        raise RuntimeError("structural discovery did not provide a child dependency")
    child_contract, _, _ = _verify_dependency(dependency, repo_root)
    child_function_usr = str(child_contract.get("function", {}).get("clang_usr", ""))
    if child_function_usr and child_function_usr != str(evidence.get("child_clang_usr", child_function_usr)):
        raise RuntimeError("child dependency does not match discovered callee")

    ranges = integer_define(pathlib.Path(source_dir), "NUM_BUF_RANGES")
    units = integer_define(pathlib.Path(source_dir), "MAX_UNITS_PER_GROUP")
    samples = integer_define(pathlib.Path(source_dir), "SAMPLES_PER_UNIT")
    scale_point = integer_define(pathlib.Path(source_dir), "RC_SCALE_BINARY_POINT")
    print_debug = integer_define(pathlib.Path(source_dir), "PRINT_DEBUG_RC")
    if (ranges, units, samples, scale_point, print_debug) != (15, 4, 3, 3, 0):
        raise RuntimeError("source constants changed from the bounded Encode RC shape")
    if not re.search(
        r"#[ \t]*define[ \t]+OVERFLOW_AVOID_THRESHOLD[ \t]+"
        r"\(dsc_cfg->native_422[ \t]*\?[ \t]*-224[ \t]*:[ \t]*-172\)",
        "\n".join(
            path.read_text(encoding="utf-8", errors="replace")
            for path in sorted((*pathlib.Path(source_dir).glob("*.h"), *pathlib.Path(source_dir).glob("*.c")))
        ),
    ):
        raise RuntimeError("overflow-avoid source macro changed")

    parameters = function.get("parameters", []) or []
    pointers = [item for item in parameters if item.get("pointer")]
    scalars = _scalar_parameters(function)
    cfg_parameter = next(item for item in pointers if "dsc_cfg_t *" in str(item.get("type")))
    state_parameter = next(item for item in pointers if "dsc_state_t *" in str(item.get("type")))
    argument_ports = {str(item["name"]): safe_identifier(str(item["name"])) for item in scalars}
    config_fields = (
        "bits_per_component", "bits_per_pixel", "chunk_size", "dsc_version_minor",
        "initial_xmit_delay", "native_420", "native_422", "rc_edge_factor",
        "rc_model_size", "rc_quant_incr_limit0", "rc_quant_incr_limit1",
        "rc_tgt_offset_hi", "rc_tgt_offset_lo", "rcb_bits", "vbr_enable",
    )
    config_ports = {field: f"cfg_{safe_identifier(field)}" for field in config_fields}
    state_fields = (
        "bitSaveMode", "bitsClamped", "bpgFracAccum", "bufferFullness", "chunkCount",
        "chunkPixelTimes", "codedGroupSize", "errorOccurred", "firstFlat", "ichSelected",
        "isEncoder", "mppState", "numBitsChunk", "pixelCount", "prevQp", "prevRange",
        "rcSizeGroup", "sliceWidth", "stQp", "unitsPerGroup", "vPos",
    )
    state_ports = _state_port_map(state_fields)
    midpoint_ports = [f"state_midpoint_selected_{index}" for index in range(units)]
    depth_ports = [f"state_cpnt_bit_depth_{index}" for index in range(2)]
    predicted_ports = [f"state_predicted_size_{index}" for index in range(units)]
    rc_size_ports = [f"state_rc_size_unit_{index}" for index in range(units)]
    threshold_ports = [f"cfg_rc_buf_thresh_{index}" for index in range(ranges - 1)]
    range_ports = {
        field: [f"cfg_{safe_identifier(field)}_{index}" for index in range(ranges)]
        for field in ("range_min_qp", "range_max_qp", "range_bpg_offset")
    }
    state_output_fields = (
        "bitSaveMode", "bitsClamped", "bpgFracAccum", "bufferFullness", "chunkCount",
        "chunkPixelTimes", "errorOccurred", "mppState", "numBitsChunk", "pixelCount",
        "prevQp", "prevRange", "rcSizeGroup", "stQp",
    )
    state_output_ports = {field: f"state_{safe_identifier(field)}_out" for field in state_output_fields}
    chunk_event_ports = [
        {
            "enable": f"chunk_write_enable_{stage}",
            "index": f"chunk_write_index_{stage}",
            "value": f"chunk_write_value_{stage}",
        }
        for stage in range(samples)
    ]
    fatal_ports = {
        "domain_valid": "domain_valid",
        "fatal_error": "fatal_error",
        "fatal_error_code": "fatal_error_code",
    }
    input_names = [
        *argument_ports.values(), *config_ports.values(), *state_ports.values(),
        *midpoint_ports, *depth_ports, *predicted_ports, *rc_size_ports,
        *threshold_ports, *[port for row in range_ports.values() for port in row],
    ]
    ports = [_port(name, "input") for name in input_names]
    ports.extend([
        _port(fatal_ports["domain_valid"], "output", 1, False),
        _port(fatal_ports["fatal_error"], "output", 1, False),
        _port(fatal_ports["fatal_error_code"], "output", 3, False),
        *[_port(name, "output") for name in state_output_ports.values()],
    ])
    for event in chunk_event_ports:
        ports.extend([
            _port(event["enable"], "output", 1, False),
            _port(event["index"], "output"),
            _port(event["value"], "output"),
        ])
    body_hash = hashlib.sha256(source_text.encode("utf-8")).hexdigest()
    return {
        "schema_version": 2,
        "contract_id": safe_identifier(str(function.get("name"))) + "_encode_transition",
        "status": "PROVISIONAL_SIMULATION_ONLY",
        "origin": "tool_discovered_encode_rate_control_transition",
        "function": {
            "clang_usr": function.get("clang_usr"),
            "name": function.get("name"),
            "source_file": function.get("source_file"),
            "source_span": {"start_line": int(function.get("line", 1)), "end_line": int(function.get("end_line", 1))},
            "source_body_sha256": body_hash,
            "parameters": parameters,
            "return_type": function.get("return_type"),
        },
        "interface": {"ports": ports},
        "dependencies": [dependency],
        "semantics": {
            "kind": "bounded_rate_control_encode_transition",
            "specialization": {
                "is_encoder": 1,
                "midpoint_source": "midpointSelected",
                "decoder_use_midpoint_is_not_an_input": True,
            },
            "constants": {
                "num_buf_ranges": ranges,
                "max_units": units,
                "samples_per_unit": samples,
                "rc_scale_binary_point": scale_point,
                "max_remove_stages": samples,
                "print_debug_rc": print_debug,
                "overflow_avoid_native_422": -224,
                "overflow_avoid_other": -172,
            },
            "bindings": {
                "config_parameter": cfg_parameter["name"],
                "state_parameter": state_parameter["name"],
                "argument_ports": argument_ports,
                "config_ports": config_ports,
                "state_ports": state_ports,
                "midpoint_ports": midpoint_ports,
                "depth_ports": depth_ports,
                "predicted_ports": predicted_ports,
                "rc_size_ports": rc_size_ports,
                "threshold_ports": threshold_ports,
                "range_ports": range_ports,
                "state_output_ports": state_output_ports,
                "fatal_ports": fatal_ports,
                "chunk_event_ports": chunk_event_ports,
                "range_parameter_field": "rc_range_parameters",
                "threshold_field": "rc_buf_thresh",
            },
            "legal_domain": {
                "encoder_only": True,
                "is_encoder": [1, 1],
                "group_size": [1, samples],
                "units_per_group": [3, units],
                "previous_range": [0, ranges - 1],
                "dsc_version_minor": [1, 2],
                "component_bit_depth": [8, 16],
                "slice_width_positive": True,
                "chunk_pixel_times_before_slice_width": True,
                "native_modes_boolean_and_mutually_exclusive": True,
                "vbr_boolean": True,
                "signed_arithmetic": "32-bit C int; widened checks reject overflow before commit",
                "fatal_paths": {
                    "rc_model_overflow": "fatal_error_code=2",
                    "rcb_overflow": "fatal_error_code=3",
                },
                "invalid_domain_code": 1,
                "arithmetic_domain_code": 4,
            },
            "state_transition": (
                "remove one pixel worth of encoder-buffer bits for each group pixel, "
                "sum rcSizeUnit, select the delayed RC range, update bit-save/MPP state "
                "and apply the source-priority QP ladder"
            ),
            "chunk_events": (
                "ordered child events 0..2 correspond to source-order RemoveBits calls; "
                "each event carries enable/index/value and is suppressed on fatal/no-commit paths"
            ),
            "composition_reduction": (
                "instantiate the hash-verified state-memory child in a three-stage source-order "
                "chain; child chunk writes remain visible as ordered sidebands"
            ),
        },
        "selection": {
            "basis": selected.get("selection_basis"),
            "encode_execution_count": selected.get("execution_count"),
            "structural_evidence": selected.get("structural_evidence", {}),
        },
        "obligations": [
            "full-frame Encode C_ONLY/SHADOW/RTL_RETURN comparison",
            "compare all 14 scalar state outputs and all ordered chunk events",
            "human review of signed RC arithmetic, fatal sidebands, and QP priority before promotion",
        ],
        "promotion": {
            "status": "BLOCKED_PENDING_HUMAN_CONTRACT_REVIEW",
            "simulation_may_proceed": True,
        },
    }


def _select_expression(values: list[str], selector: str) -> str:
    expression = values[-1]
    for index in reversed(range(len(values) - 1)):
        expression = f"(({selector} == 32'sd{index}) ? {values[index]} : {expression})"
    return expression


def _port_lines(contract: dict[str, Any]) -> list[str]:
    lines: list[str] = []
    for port in contract["interface"]["ports"]:
        width = int(port["width"])
        width_text = "" if width == 1 else f" [{width - 1}:0]"
        signed = " signed" if port.get("signed") else ""
        lines.append(f"    {port['direction']} logic{signed}{width_text} {port['name']}")
    return lines


def render_rate_control_encode_rtl(
    contract: dict[str, Any], repo_root: pathlib.Path | None = None
) -> str:
    """Render a combinational, synthesizable SV composition of the child and RC."""
    semantics = contract.get("semantics", {})
    if semantics.get("kind") != "bounded_rate_control_encode_transition":
        raise RuntimeError("contract is not an Encode rate-control contract")
    constants = semantics["constants"]
    ranges = int(constants["num_buf_ranges"])
    units = int(constants["max_units"])
    samples = int(constants["samples_per_unit"])
    scale_point = int(constants["rc_scale_binary_point"])
    if (ranges, units, samples, scale_point) != (15, 4, 3, 3):
        raise RuntimeError("unsupported DSC Encode rate-control constants")
    dependencies = contract.get("dependencies", []) or []
    if len(dependencies) != 1 or dependencies[0].get("role") != "remove_one_pixel_bits":
        raise RuntimeError("Encode rate-control child dependency is incomplete")
    repo_root = pathlib.Path(repo_root or pathlib.Path(__file__).resolve().parent.parent)
    dependency = dependencies[0]
    child_contract, _, child_module_path = _verify_dependency(dependency, repo_root)
    child_module = safe_identifier(str(child_contract["contract_id"]))
    dependency_source = child_module_path.read_text(encoding="utf-8").rstrip()
    bindings = semantics["bindings"]
    arguments = {str(key): str(value) for key, value in bindings["argument_ports"].items()}
    config = {str(key): str(value) for key, value in bindings["config_ports"].items()}
    state = {str(key): str(value) for key, value in bindings["state_ports"].items()}
    midpoint = [str(value) for value in bindings["midpoint_ports"]]
    depth = [str(value) for value in bindings["depth_ports"]]
    predicted = [str(value) for value in bindings["predicted_ports"]]
    rc_size = [str(value) for value in bindings["rc_size_ports"]]
    thresholds = [str(value) for value in bindings["threshold_ports"]]
    range_ports = {str(key): [str(value) for value in row] for key, row in bindings["range_ports"].items()}
    outputs = {str(key): str(value) for key, value in bindings["state_output_ports"].items()}
    fatal = {str(key): str(value) for key, value in bindings["fatal_ports"].items()}
    events = [{str(key): str(value) for key, value in row.items()} for row in bindings["chunk_event_ports"]]
    if len(midpoint) != units or len(depth) != 2 or len(predicted) != units or len(rc_size) != units:
        raise RuntimeError("Encode rate-control array bindings are incomplete")
    if len(thresholds) != ranges - 1 or any(len(row) != ranges for row in range_ports.values()):
        raise RuntimeError("Encode rate-control range bindings are incomplete")
    if len(events) != samples:
        raise RuntimeError("Encode rate-control event bindings are incomplete")

    def sext32(expression: str) -> str:
        return f"$signed({{{{32{{{expression}[31]}}}}, {expression}}})"

    # The child is the already-proven state-memory transition.  Its output
    # sideband is deliberately retained per stage so event ordering cannot be
    # reconstructed from a collapsed count later.
    child_state_fields = (
        "bitsclamped", "bpgfracaccum", "bufferfullness", "chunkcount",
        "chunkpixeltimes", "numbitschunk",
    )
    declarations: list[str] = []
    for stage in range(samples + 1):
        declarations.append(f"    logic signed [31:0] pixelcount_stage_{stage}_i;")
        declarations.extend(
            f"    logic signed [31:0] {field}_stage_{stage}_i;"
            for field in child_state_fields
        )
    for stage in range(samples):
        declarations.extend([
            f"    logic signed [31:0] pixelcount_after_{stage}_i;",
            f"    logic remove_stage_{stage}_i;",
            *[f"    logic signed [31:0] {field}_child_{stage}_i;" for field in child_state_fields],
            f"    logic chunk_write_enable_child_{stage}_i;",
            f"    logic signed [31:0] chunk_write_index_child_{stage}_i;",
            f"    logic signed [31:0] chunk_write_value_child_{stage}_i;",
        ])
    declarations.extend([
        "    logic signed [31:0] throttle_i;",
        "    logic signed [31:0] rc_model_fullness_i;",
        "    logic signed [31:0] selected_range_i;",
        "    logic signed [31:0] next_range_i;",
        "    logic signed [31:0] rc_size_group_i;",
        "    logic signed [31:0] rc_target_i;",
        "    logic signed [31:0] min_qp_i;",
        "    logic signed [31:0] max_qp_i;",
        "    logic signed [31:0] target_minus_i;",
        "    logic signed [31:0] target_plus_i;",
        "    logic signed [31:0] increment_i;",
        "    logic signed [31:0] bpg_i;",
        "    logic signed [31:0] mpsel_i;",
        "    logic signed [31:0] pred_activity_i;",
        "    logic signed [31:0] bit_save_thresh_i;",
        "    logic signed [31:0] previous_qp_i;",
        "    logic signed [31:0] previous2_qp_i;",
        "    logic signed [31:0] current_qp_i;",
        "    logic signed [31:0] new_qp_i;",
        "    logic overflow_avoid_i;",
        "    logic range_found_i;",
        "    logic arithmetic_invalid_i;",
        "    logic signed [63:0] fullness_throttle_wide_i;",
        "    logic signed [63:0] model_product_wide_i;",
        "    logic signed [63:0] model_shift_wide_i;",
        "    logic signed [63:0] bpg_product_wide_i;",
        "    logic signed [63:0] bpg_shift_wide_i;",
        "    logic signed [63:0] rc_size_group_wide_i;",
        "    logic signed [63:0] increment_wide_i;",
    ])

    stage_wiring = [
        f"    assign pixelcount_stage_0_i = {state['pixelCount']};",
        f"    assign bitsclamped_stage_0_i = {state['bitsClamped']};",
        f"    assign bpgfracaccum_stage_0_i = {state['bpgFracAccum']};",
        f"    assign bufferfullness_stage_0_i = {state['bufferFullness']};",
        f"    assign chunkcount_stage_0_i = {state['chunkCount']};",
        f"    assign chunkpixeltimes_stage_0_i = {state['chunkPixelTimes']};",
        f"    assign numbitschunk_stage_0_i = {state['numBitsChunk']};",
    ]
    child_instances: list[str] = []
    for stage in range(samples):
        stage_wiring.extend([
            f"    assign pixelcount_after_{stage}_i = pixelcount_stage_{stage}_i "
            f"+ (({arguments['group_size']} > 32'sd{stage}) ? 32'sd1 : 32'sd0);",
            f"    assign remove_stage_{stage}_i = ({arguments['group_size']} > 32'sd{stage}) "
            f"&& (pixelcount_after_{stage}_i >= {config['initial_xmit_delay']});",
            f"    assign pixelcount_stage_{stage + 1}_i = pixelcount_after_{stage}_i;",
        ])
        for field in child_state_fields:
            stage_wiring.append(
                f"    assign {field}_stage_{stage + 1}_i = remove_stage_{stage}_i "
                f"? {field}_child_{stage}_i : {field}_stage_{stage}_i;"
            )
        child_instances.append(
            f"    {child_module} remove_stage_{stage}(\n"
            f"        .cfg_bits_per_pixel({config['bits_per_pixel']}),\n"
            f"        .cfg_chunk_size({config['chunk_size']}),\n"
            f"        .cfg_vbr_enable({config['vbr_enable']}),\n"
            f"        .state_bitsclamped(bitsclamped_stage_{stage}_i),\n"
            f"        .state_bpgfracaccum(bpgfracaccum_stage_{stage}_i),\n"
            f"        .state_bufferfullness(bufferfullness_stage_{stage}_i),\n"
            f"        .state_chunkcount(chunkcount_stage_{stage}_i),\n"
            f"        .state_chunkpixeltimes(chunkpixeltimes_stage_{stage}_i),\n"
            f"        .state_isencoder({state['isEncoder']}),\n"
            f"        .state_numbitschunk(numbitschunk_stage_{stage}_i),\n"
            f"        .state_slicewidth({state['sliceWidth']}),\n"
            f"        .state_bitsclamped_out(bitsclamped_child_{stage}_i),\n"
            f"        .state_bpgfracaccum_out(bpgfracaccum_child_{stage}_i),\n"
            f"        .state_bufferfullness_out(bufferfullness_child_{stage}_i),\n"
            f"        .state_chunkcount_out(chunkcount_child_{stage}_i),\n"
            f"        .state_chunkpixeltimes_out(chunkpixeltimes_child_{stage}_i),\n"
            f"        .state_numbitschunk_out(numbitschunk_child_{stage}_i),\n"
            f"        .chunk_write_enable(chunk_write_enable_child_{stage}_i),\n"
            f"        .chunk_write_index(chunk_write_index_child_{stage}_i),\n"
            f"        .chunk_write_value(chunk_write_value_child_{stage}_i)\n"
            "    );"
        )

    functions = """
    function automatic signed [31:0] dsc_cicd_min(
        input logic signed [31:0] left_i,
        input logic signed [31:0] right_i);
        begin dsc_cicd_min = (left_i < right_i) ? left_i : right_i; end
    endfunction

    function automatic signed [31:0] dsc_cicd_max(
        input logic signed [31:0] left_i,
        input logic signed [31:0] right_i);
        begin dsc_cicd_max = (left_i > right_i) ? left_i : right_i; end
    endfunction

    function automatic signed [31:0] dsc_cicd_clamp(
        input logic signed [31:0] value_i,
        input logic signed [31:0] lower_i,
        input logic signed [31:0] upper_i);
        begin
            if (value_i < lower_i) dsc_cicd_clamp = lower_i;
            else if (value_i > upper_i) dsc_cicd_clamp = upper_i;
            else dsc_cicd_clamp = value_i;
        end
    endfunction
""".strip("\n")

    body: list[str] = [
        f"        {fatal['domain_valid']} = 1'b1;",
        f"        {fatal['fatal_error']} = 1'b0;",
        f"        {fatal['fatal_error_code']} = 3'd0;",
    ]
    # Defaults are the no-commit values.  This also makes the fatal/domain
    # behavior explicit: an encoder C exit path never commits a partial state.
    for field, port in outputs.items():
        body.append(f"        {port} = {state[field]};")
    for event in events:
        body.extend([
            f"        {event['enable']} = 1'b0;",
            f"        {event['index']} = 32'sd0;",
            f"        {event['value']} = 32'sd0;",
        ])
    body.extend([
        "        arithmetic_invalid_i = 1'b0;",
        "        fullness_throttle_wide_i = 64'sd0;",
        "        model_product_wide_i = 64'sd0;",
        "        model_shift_wide_i = 64'sd0;",
        "        bpg_product_wide_i = 64'sd0;",
        "        bpg_shift_wide_i = 64'sd0;",
        "        rc_size_group_wide_i = 64'sd0;",
        "        increment_wide_i = 64'sd0;",
        "        rc_size_group_i = 32'sd0;",
        "        throttle_i = 32'sd0;",
        "        rc_model_fullness_i = 32'sd0;",
        "        selected_range_i = 32'sd0;",
        "        next_range_i = 32'sd0;",
        "        rc_target_i = 32'sd0;",
        "        min_qp_i = 32'sd0;",
        "        max_qp_i = 32'sd0;",
        "        target_minus_i = 32'sd0;",
        "        target_plus_i = 32'sd0;",
        "        increment_i = 32'sd0;",
        "        bpg_i = 32'sd0;",
        "        mpsel_i = 32'sd0;",
        "        pred_activity_i = 32'sd0;",
        "        bit_save_thresh_i = 32'sd0;",
        f"        previous_qp_i = {state['stQp']};",
        f"        previous2_qp_i = {state['prevQp']};",
        "        current_qp_i = 32'sd0;",
        f"        new_qp_i = {state['stQp']};",
        "        overflow_avoid_i = 1'b0;",
        "        range_found_i = 1'b0;",
        f"        rc_size_group_wide_i = 64'sd0;",
    ])
    for index in range(units):
        body.append(
        f"        if ({state['unitsPerGroup']} > 32'sd{index}) "
            f"rc_size_group_wide_i = rc_size_group_wide_i + {sext32(rc_size[index])};"
        )
    body.extend([
        "        rc_size_group_i = rc_size_group_wide_i[31:0];",
        f"        throttle_i = {arguments['throttle_offset']} - {config['rc_model_size']};",
        f"        fullness_throttle_wide_i = {sext32(f'bufferfullness_stage_{samples}_i')} + {sext32('throttle_i')};",
        f"        model_product_wide_i = {sext32(arguments['scale'])} * fullness_throttle_wide_i;",
        f"        model_shift_wide_i = model_product_wide_i >>> {scale_point};",
        "        rc_model_fullness_i = model_shift_wide_i[31:0];",
        f"        bpg_product_wide_i = {sext32(config['bits_per_pixel'])} * {sext32(arguments['group_size'])};",
        "        bpg_shift_wide_i = (bpg_product_wide_i + 64'sd8) >>> 4;",
        "        bpg_i = bpg_shift_wide_i[31:0];",
        f"        selected_range_i = {state['prevRange']};",
        "        next_range_i = 32'sd0;",
        "        range_found_i = 1'b0;",
    ])
    for index in reversed(range(1, ranges)):
        body.append(
            f"        if (!range_found_i && (rc_model_fullness_i > "
            f"({thresholds[index - 1]} - {config['rc_model_size']}))) begin"
        )
        body.extend([f"            next_range_i = 32'sd{index};", "            range_found_i = 1'b1;", "        end"])
    body.extend([
        f"        overflow_avoid_i = (fullness_throttle_wide_i > "
        f"(({config['native_422']} != 0) ? -64'sd224 : -64'sd172));",
        f"        rc_target_i = dsc_cicd_max(32'sd0, bpg_i + "
        f"{_select_expression(range_ports['range_bpg_offset'], 'selected_range_i')} + {arguments['bpg_offset']});",
        f"        min_qp_i = {_select_expression(range_ports['range_min_qp'], 'selected_range_i')};",
        f"        max_qp_i = {_select_expression(range_ports['range_max_qp'], 'selected_range_i')};",
        f"        target_minus_i = dsc_cicd_max(32'sd0, rc_target_i - {config['rc_tgt_offset_lo']});",
        f"        target_plus_i = dsc_cicd_max(32'sd0, rc_target_i + {config['rc_tgt_offset_hi']});",
        f"        increment_wide_i = ({sext32(state['codedGroupSize'])} - {sext32('rc_target_i')}) >>> 1;",
        "        increment_i = increment_wide_i[31:0];",
        f"        mpsel_i = {midpoint[0]} + {midpoint[1]} + {midpoint[2]} + {midpoint[3]};",
        f"        if ({config['native_420']} != 0) pred_activity_i = {state['prevQp']} + "
        f"dsc_cicd_max({predicted[0]}, {predicted[1]}) + {predicted[2]};",
        f"        else if ({config['native_422']} == 0) pred_activity_i = {state['prevQp']} + "
        f"{predicted[0]} + dsc_cicd_max({predicted[1]}, {predicted[2]});",
        f"        else pred_activity_i = {state['prevQp']} + (({predicted[0]} + {predicted[3]} + "
        f"{predicted[1]} + {predicted[2]}) >>> 1);",
        f"        bit_save_thresh_i = {depth[0]} + {depth[1]} - 32'sd2;",
        f"        if (({config['dsc_version_minor']} == 32'sd2) && ({state['vPos']} > 32'sd0) "
        f"&& ({state['firstFlat']} == -32'sd1)) begin",
        f"            if (({state['ichSelected']} == 32'sd0) && (mpsel_i >= 32'sd3)) begin",
        f"                {outputs['mppState']} = {state['mppState']} + 32'sd1;",
        f"                if ({outputs['mppState']} >= 32'sd2) {outputs['bitSaveMode']} = 32'sd2;",
        "            end",
        f"            else if (({state['ichSelected']} == 32'sd0) && "
        f"(pred_activity_i >= bit_save_thresh_i)) begin end",
        f"            else if ({state['ichSelected']} != 32'sd0) "
        f"{outputs['bitSaveMode']} = dsc_cicd_max(32'sd1, {outputs['bitSaveMode']});",
        "            else begin",
        f"                {outputs['mppState']} = 32'sd0;",
        f"                {outputs['bitSaveMode']} = 32'sd0;",
        "            end",
        "        end else begin",
        f"            {outputs['bitSaveMode']} = 32'sd0;",
        f"            {outputs['mppState']} = 32'sd0;",
        "        end",
        f"        if (({config['dsc_version_minor']} == 32'sd2) && "
        f"(bufferfullness_stage_{samples}_i < 32'sd192)) new_qp_i = min_qp_i;",
        f"        else if ({outputs['bitSaveMode']} != 32'sd0) begin",
        f"            max_qp_i = dsc_cicd_min(({config['bits_per_component']} * 32'sd2) - 32'sd1, max_qp_i + 32'sd1);",
        f"            if ({outputs['bitSaveMode']} == 32'sd1) new_qp_i = previous_qp_i;",
        "            else new_qp_i = previous_qp_i + 32'sd2;",
        f"        end else if (rc_size_group_i == {state['unitsPerGroup']}) begin",
        f"            if ({config['dsc_version_minor']} == 32'sd2) begin",
        "                min_qp_i = dsc_cicd_max(min_qp_i - 32'sd4, 32'sd0);",
        "                new_qp_i = previous_qp_i - 32'sd1;",
        "            end else new_qp_i = dsc_cicd_max(min_qp_i / 32'sd2, previous_qp_i - 32'sd1);",
        "        end",
        f"        else if ((({config['dsc_version_minor']} == 32'sd1) && "
        f"({state['codedGroupSize']} < target_minus_i) && (rc_size_group_i < target_minus_i)) ||",
        f"                 (({config['dsc_version_minor']} == 32'sd2) && (rc_size_group_i < target_minus_i))) begin",
        f"            if ({config['dsc_version_minor']} == 32'sd2) new_qp_i = previous_qp_i - 32'sd1;",
        "            else new_qp_i = dsc_cicd_max(min_qp_i, previous_qp_i - 32'sd1);",
        "        end",
        f"        else if ((bufferfullness_stage_{samples}_i >= 32'sd64) && "
        f"({state['codedGroupSize']} > target_plus_i)) begin",
        "            current_qp_i = dsc_cicd_max(previous_qp_i, min_qp_i);",
        f"            if (previous2_qp_i == current_qp_i) begin",
        f"                if ((rc_size_group_i * 32'sd2) < ({state['rcSizeGroup']} * {config['rc_edge_factor']})) begin",
        f"                    if ({config['dsc_version_minor']} == 32'sd2) new_qp_i = current_qp_i + increment_i;",
        "                    else new_qp_i = dsc_cicd_min(max_qp_i, current_qp_i + increment_i);",
        "                end else new_qp_i = current_qp_i;",
        "            end else if (previous2_qp_i < current_qp_i) begin",
        f"                if (((rc_size_group_i * 32'sd2) < ({state['rcSizeGroup']} * {config['rc_edge_factor']})) "
        f"&& (current_qp_i < {config['rc_quant_incr_limit0']})) begin",
        f"                    if ({config['dsc_version_minor']} == 32'sd2) new_qp_i = current_qp_i + increment_i;",
        "                    else new_qp_i = dsc_cicd_min(max_qp_i, current_qp_i + increment_i);",
        "                end else new_qp_i = current_qp_i;",
        f"            end else if (current_qp_i < {config['rc_quant_incr_limit1']}) begin",
        f"                if ({config['dsc_version_minor']} == 32'sd2) new_qp_i = current_qp_i + increment_i;",
        "                else new_qp_i = dsc_cicd_min(max_qp_i, current_qp_i + increment_i);",
        "            end else new_qp_i = current_qp_i;",
        "        end else new_qp_i = previous_qp_i;",
        f"        if ({config['dsc_version_minor']} == 32'sd2) new_qp_i = dsc_cicd_clamp(new_qp_i, min_qp_i, max_qp_i);",
        f"        if (overflow_avoid_i) new_qp_i = {range_ports['range_max_qp'][-1]};",
        f"        {outputs['bitSaveMode']} = {outputs['bitSaveMode']};",
        f"        {outputs['errorOccurred']} = {state['errorOccurred']};",
        f"        {outputs['prevQp']} = previous_qp_i;",
        f"        {outputs['prevRange']} = next_range_i;",
        f"        {outputs['rcSizeGroup']} = rc_size_group_i;",
        f"        {outputs['stQp']} = new_qp_i;",
    ])
    # Reject overflows that would make a 64-bit widened implementation differ
    # from the source's defined 32-bit legal domain.  The actual C fatal paths
    # are represented separately below.
    body.extend([
        "        if ((rc_size_group_wide_i > 64'sd2147483647) || (rc_size_group_wide_i < -64'sd2147483648) ||",
        "            (fullness_throttle_wide_i > 64'sd2147483647) || (fullness_throttle_wide_i < -64'sd2147483648) ||",
        "            (model_shift_wide_i > 64'sd2147483647) || (model_shift_wide_i < -64'sd2147483648) ||",
        "            (bpg_shift_wide_i > 64'sd2147483647) || (bpg_shift_wide_i < -64'sd2147483648) ||",
        "            (increment_wide_i > 64'sd2147483647) || (increment_wide_i < -64'sd2147483648))",
        "            arithmetic_invalid_i = 1'b1;",
        f"        if (({state['isEncoder']} != 32'sd1) || ({arguments['group_size']} < 32'sd1) || "
        f"({arguments['group_size']} > 32'sd{samples}) || ({state['unitsPerGroup']} < 32'sd3) || "
        f"({state['unitsPerGroup']} > 32'sd{units}) || ({state['prevRange']} < 32'sd0) || "
        f"({state['prevRange']} >= 32'sd{ranges}) || ({state['sliceWidth']} <= 32'sd0) || "
        f"({state['chunkPixelTimes']} < 32'sd0) || ({state['chunkPixelTimes']} >= {state['sliceWidth']}) || "
        f"({config['dsc_version_minor']} < 32'sd1) || ({config['dsc_version_minor']} > 32'sd2) || "
        f"(({config['native_420']} != 32'sd0) && ({config['native_420']} != 32'sd1)) || "
        f"(({config['native_422']} != 32'sd0) && ({config['native_422']} != 32'sd1)) || "
        f"(({config['native_420']} != 32'sd0) && ({config['native_422']} != 32'sd0)) || "
        f"({config['vbr_enable']} < 32'sd0) || ({config['vbr_enable']} > 32'sd1) || "
        f"({config['initial_xmit_delay']} < 32'sd0) || ({depth[0]} < 32'sd8) || ({depth[0]} > 32'sd16) || "
        f"({depth[1]} < 32'sd8) || ({depth[1]} > 32'sd16)) begin",
        f"            {fatal['domain_valid']} = 1'b0;",
        f"            {fatal['fatal_error']} = 1'b1;",
        f"            {fatal['fatal_error_code']} = 3'd1;",
        "        end",
        "        if (arithmetic_invalid_i && (domain_valid != 1'b0)) begin",
        f"            {fatal['fatal_error']} = 1'b1;",
        f"            {fatal['fatal_error_code']} = 3'd4;",
        "        end",
        f"        if (({fatal['domain_valid']} != 1'b0) && !arithmetic_invalid_i && (rc_model_fullness_i > 32'sd0)) begin",
        f"            {fatal['fatal_error']} = 1'b1;",
        f"            {fatal['fatal_error_code']} = 3'd2;",
        "        end",
        f"        else if (({fatal['domain_valid']} != 1'b0) && !arithmetic_invalid_i && "
        f"(bufferfullness_stage_{samples}_i > {config['rcb_bits']})) begin",
        f"            {fatal['fatal_error']} = 1'b1;",
        f"            {fatal['fatal_error_code']} = 3'd3;",
        "        end",
    ])
    # The outputs were initialized to no-commit values.  Commit the child
    # state, scalar state and ordered events only on a legal, non-fatal path.
    body.extend([
        f"        if (({fatal['domain_valid']} != 1'b0) && ({fatal['fatal_error']} == 1'b0)) begin",
    ])
    for field, port in outputs.items():
        if field == "pixelCount":
            expression = f"pixelcount_stage_{samples}_i"
        elif field == "bitsClamped":
            expression = f"bitsclamped_stage_{samples}_i"
        elif field == "bpgFracAccum":
            expression = f"bpgfracaccum_stage_{samples}_i"
        elif field == "bufferFullness":
            expression = f"bufferfullness_stage_{samples}_i"
        elif field == "chunkCount":
            expression = f"chunkcount_stage_{samples}_i"
        elif field == "chunkPixelTimes":
            expression = f"chunkpixeltimes_stage_{samples}_i"
        elif field == "numBitsChunk":
            expression = f"numbitschunk_stage_{samples}_i"
        else:
            expression = port
        if field in {"bitSaveMode", "mppState", "prevQp", "prevRange", "rcSizeGroup", "stQp", "errorOccurred"}:
            # These were computed in the preceding source-order block; leave
            # their already-assigned values in place.
            continue
        body.append(f"            {port} = {expression};")
    for stage, event in enumerate(events):
        body.extend([
            f"            {event['enable']} = remove_stage_{stage}_i && chunk_write_enable_child_{stage}_i;",
            f"            {event['index']} = chunk_write_index_child_{stage}_i;",
            f"            {event['value']} = chunk_write_value_child_{stage}_i;",
        ])
    body.append("        end")
    # On invalid/fatal paths, the scalar/direct outputs must remain the
    # no-commit defaults established at the top of the block.
    body.extend([
        f"        if (({fatal['domain_valid']} == 1'b0) || ({fatal['fatal_error']} != 1'b0)) begin",
    ])
    for field, port in outputs.items():
        body.append(f"            {port} = {state[field]};")
    for event in events:
        body.extend([
            f"            {event['enable']} = 1'b0;",
            f"            {event['index']} = 32'sd0;",
            f"            {event['value']} = 32'sd0;",
        ])
    body.append("        end")

    module = safe_identifier(str(contract["contract_id"]))
    top = (
        f"module {module}(\n" + ",\n".join(_port_lines(contract)) + "\n);\n"
        + "\n".join(declarations) + "\n\n"
        + functions + "\n\n"
        + "\n".join(stage_wiring) + "\n\n"
        + "\n\n".join(child_instances) + "\n\n"
        + "    always_comb begin\n" + "\n".join(body)
        + "\n    end\nendmodule\n"
    )
    return dependency_source + "\n\n" + top


def build_contract_from_documents(
    functions_path: pathlib.Path,
    candidates_path: pathlib.Path,
    coverage_path: pathlib.Path,
    source_dir: pathlib.Path,
    repo_root: pathlib.Path,
) -> dict[str, Any]:
    discovered = discover_rate_control_encode_candidates(
        read_json(functions_path),
        read_json(candidates_path),
        read_json(coverage_path),
        source_dir,
        repo_root,
    )
    selected = select_candidate(discovered)
    function = next(
        row for row in _document_rows(read_json(functions_path))
        if str(row.get("clang_usr")) == str(selected.get("clang_usr"))
    )
    return build_rate_control_encode_contract(selected, function, source_dir, repo_root)


# Small compatibility surface for callers that use the same generator
# protocol as the existing transition generators.  These are aliases over the
# explicit Encode-rate-control API above; discovery remains structural.
def discover_candidates(
    functions: dict[str, Any] | list[dict[str, Any]],
    candidates: dict[str, Any] | list[dict[str, Any]],
    coverage: dict[str, Any] | list[dict[str, Any]],
    source_dir: pathlib.Path,
    repo_root: pathlib.Path | None = None,
) -> list[dict[str, Any]]:
    return discover_rate_control_encode_candidates(
        functions, candidates, coverage, source_dir, repo_root
    )


def build_contract(
    selected: dict[str, Any],
    function: dict[str, Any],
    source_dir: pathlib.Path,
    repo_root: pathlib.Path | None = None,
) -> dict[str, Any]:
    return build_rate_control_encode_contract(selected, function, source_dir, repo_root)


def render_rtl(
    contract: dict[str, Any], repo_root: pathlib.Path | None = None
) -> str:
    return render_rate_control_encode_rtl(contract, repo_root)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo-root", type=pathlib.Path, default=pathlib.Path(__file__).resolve().parent.parent)
    parser.add_argument("--source-dir", type=pathlib.Path, required=True)
    parser.add_argument("--functions", type=pathlib.Path, required=True)
    parser.add_argument("--candidates", type=pathlib.Path, required=True)
    parser.add_argument("--coverage", type=pathlib.Path, required=True)
    parser.add_argument("--contract-out", type=pathlib.Path)
    parser.add_argument("--rtl-out", type=pathlib.Path)
    args = parser.parse_args(argv)
    contract = build_contract_from_documents(
        args.functions, args.candidates, args.coverage, args.source_dir, args.repo_root
    )
    rtl = render_rate_control_encode_rtl(contract, args.repo_root)
    if args.contract_out:
        write_json(args.contract_out, contract)
    else:
        print(json.dumps(contract, indent=2, sort_keys=True, ensure_ascii=False))
    if args.rtl_out:
        args.rtl_out.parent.mkdir(parents=True, exist_ok=True)
        args.rtl_out.write_text(rtl, encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
