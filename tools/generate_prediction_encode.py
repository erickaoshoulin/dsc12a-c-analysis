#!/usr/bin/env python3
"""Discover and render the bounded encoder half of PredictionLoop.

This module deliberately stops at the generator/RTL boundary.  It does not
rewrite the C model, create a CI receipt, or perform a promotion.  The target
function is selected from Clang facts, Encode coverage, source shape, and
dataflow.  Its C spelling is never used as an admission predicate.

The generated module is self-contained RTL so that it can be linted in
isolation.  The six pure leaf contracts are still pinned by their manifest
contract/module hashes and their reviewed semantic kinds.  Their semantics
are inlined into private RTL functions; this keeps the generated candidate
portable while preserving the dependency boundary in the contract.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import pathlib
import re
from typing import Any, Iterable


REQUIRED_DEPENDENCY_KINDS: tuple[tuple[str, str], ...] = (
    ("qp_mapping", "map_qp_to_qlevel"),
    ("windowed_sample_predict", "sample_predict"),
    ("quantization", "quantize_residual"),
    ("midpoint_prediction", "find_midpoint"),
    ("residual_size", "find_residual_size"),
    ("max_residual_size", "max_residual_size"),
)

REQUIRED_DEPENDENCY_ROLES = {role for _, role in REQUIRED_DEPENDENCY_KINDS}


def read_json(path: pathlib.Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: pathlib.Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(value, indent=2, sort_keys=True, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )


def file_sha256(path: pathlib.Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def safe_identifier(value: str) -> str:
    result = re.sub(r"[^A-Za-z0-9_]", "_", value).lower()
    return ("c_" + result) if result[:1].isdigit() else result


def rows(document: dict[str, Any], key: str = "functions") -> list[dict[str, Any]]:
    value = document.get(key, []) or []
    return [item for item in value if isinstance(item, dict)]


def integer_define(source_dir: pathlib.Path, name: str) -> int:
    pattern = re.compile(
        r"^[ \t]*#[ \t]*define[ \t]+"
        + re.escape(name)
        + r"[ \t]+([0-9]+)\b",
        re.MULTILINE,
    )
    values: set[int] = set()
    for header in sorted(source_dir.glob("*.h")):
        match = pattern.search(header.read_text(encoding="utf-8", errors="replace"))
        if match:
            values.add(int(match.group(1)))
    if len(values) != 1:
        raise RuntimeError(f"expected one integer definition for {name}, got {sorted(values)}")
    return next(iter(values))


def source_span(
    function: dict[str, Any], source_dir: pathlib.Path
) -> tuple[pathlib.Path, int, int, str]:
    source = source_dir / str(function["source_file"])
    lines = source.read_text(encoding="utf-8", errors="replace").splitlines()
    start = int(function.get("line", 1))
    end = int(function.get("end_line", start))
    return source, start, end, "\n".join(lines[start - 1 : end])


def _coverage_row(
    coverage_document: dict[str, Any], usr: str
) -> dict[str, Any]:
    candidates: list[dict[str, Any]] = []
    candidates.extend(rows(coverage_document))
    for key in ("coverage", "functions", "encode"):
        value = coverage_document.get(key)
        if isinstance(value, dict):
            row = value.get(usr)
            if isinstance(row, dict):
                candidates.append(row)
            candidates.extend(item for item in value.values() if isinstance(item, dict))
        elif isinstance(value, list):
            candidates.extend(item for item in value if isinstance(item, dict))
    for row in candidates:
        if str(row.get("clang_usr", "")) == usr:
            return row
    return {}


def _encode_coverage(row: dict[str, Any]) -> tuple[bool, int]:
    value = row.get("coverage", row)
    if not isinstance(value, dict):
        return False, 0
    encode = value.get("encode")
    if isinstance(encode, dict):
        covered = bool(encode.get("covered"))
        count = int(encode.get("execution_count", encode.get("count", 0)) or 0)
        return covered and count > 0, count
    count = int(
        value.get(
            "encode_execution_count",
            value.get("execution_count", value.get("count", 0)),
        )
        or 0
    )
    covered = value.get("covered", count > 0)
    return bool(covered) and count > 0, count


def _direct_effects(candidate: dict[str, Any]) -> dict[str, Any]:
    return candidate.get("direct_effects", {}) or {}


def _field_names(function: dict[str, Any], key: str, record: str | None = None) -> set[str]:
    result: set[str] = set()
    for item in function.get(key, []) or []:
        if not isinstance(item, dict):
            continue
        if record is not None and item.get("record") != record:
            continue
        name = item.get("name")
        if name:
            result.add(str(name))
    return result


def _semantic_kind(record: dict[str, Any]) -> str:
    contract = record.get("contract", record)
    return str((contract.get("semantics", {}) or {}).get("kind", ""))


def _normalise_dependency_records(
    dependencies: dict[str, Any] | Iterable[dict[str, Any]]
) -> dict[str, dict[str, Any]]:
    """Return lookup entries by role, function name, and clang USR.

    The role lookup is the structural path used by discovery.  Name/USR keys
    are only join keys after a semantic role has been established.
    """
    if isinstance(dependencies, dict):
        values = list(dependencies.values())
    else:
        values = list(dependencies)
    result: dict[str, dict[str, Any]] = {}
    for record in values:
        if not isinstance(record, dict):
            continue
        contract = record.get("contract", record)
        kind = _semantic_kind(record)
        role = str(record.get("role", ""))
        if not role:
            role = dict(REQUIRED_DEPENDENCY_KINDS).get(kind, "")
        if not role:
            continue
        item = dict(record)
        item["role"] = role
        item["contract"] = contract
        function = contract.get("function", {}) or {}
        if function.get("name"):
            result[str(function["name"])] = item
        if function.get("clang_usr"):
            result[str(function["clang_usr"])] = item
        result[role] = item
    return result


def load_pinned_dependencies(
    repo_root: pathlib.Path,
    *,
    manifest_path: pathlib.Path | None = None,
) -> dict[str, dict[str, Any]]:
    """Load the six accepted leaves and verify every recorded hash.

    ``manifest.contract_hash`` is the repository's artifact/content pin; the
    actual contract-file SHA is recorded separately because it is the byte
    identity consumed by this generator.  Both pins are checked where the
    manifest provides them, along with the module SHA and promotion metadata.
    """
    root = repo_root.resolve()
    manifest_file = manifest_path or root / "library" / "manifest.json"
    manifest = read_json(manifest_file)
    by_kind: dict[str, dict[str, Any]] = {}
    for component in manifest.get("components", []) or []:
        if not isinstance(component, dict) or component.get("status") != "PASS":
            continue
        if not component.get("contract_file") or not component.get("module_file"):
            continue
        contract_path = root / "library" / str(component["contract_file"])
        module_path = root / "library" / str(component["module_file"])
        if not contract_path.is_file() or not module_path.is_file():
            continue
        contract = read_json(contract_path)
        kind = _semantic_kind(contract)
        role = dict(REQUIRED_DEPENDENCY_KINDS).get(kind)
        if not role or kind in by_kind:
            continue
        actual_contract_hash = file_sha256(contract_path)
        actual_module_hash = file_sha256(module_path)
        promotion = contract.get("library_promotion", {}) or {}
        expected_module_hashes = {
            str(component.get("module_sha256", "")),
            str(promotion.get("rtl_sha256", "")),
        }
        expected_module_hashes.discard("")
        if expected_module_hashes and actual_module_hash not in expected_module_hashes:
            raise RuntimeError(
                f"dependency module hash mismatch for semantic kind {kind}: "
                f"{actual_module_hash} not in {sorted(expected_module_hashes)}"
            )
        if promotion.get("status") not in (None, "PASS"):
            raise RuntimeError(f"dependency promotion is not PASS for {kind}")
        manifest_pin = str(component.get("contract_hash", ""))
        artifact_dir = str(promotion.get("artifact_dir", ""))
        if manifest_pin and artifact_dir:
            artifact_pin = pathlib.Path(artifact_dir).name
            if manifest_pin != artifact_pin:
                raise RuntimeError(f"dependency artifact pin mismatch for {kind}")
        function = contract.get("function", {}) or {}
        if component.get("function") and function.get("name") != component.get("function"):
            raise RuntimeError(f"dependency function identity mismatch for {kind}")
        by_kind[kind] = {
            "role": role,
            "function": function.get("name"),
            "clang_usr": function.get("clang_usr"),
            "contract": contract,
            "contract_id": contract.get("contract_id"),
            "contract_file": str(contract_path.relative_to(root)),
            "contract_sha256": actual_contract_hash,
            "manifest_contract_hash": manifest_pin,
            "module_file": str(module_path.relative_to(root)),
            "module_sha256": actual_module_hash,
            "manifest_module_sha256": component.get("module_sha256"),
            "source_body_sha256": function.get("source_body_sha256"),
        }
    missing = [kind for kind, _ in REQUIRED_DEPENDENCY_KINDS if kind not in by_kind]
    if missing:
        raise RuntimeError("missing pinned PredictionLoop dependencies: " + ", ".join(missing))
    result: dict[str, dict[str, Any]] = {}
    for record in by_kind.values():
        result[record["role"]] = record
        if record.get("function"):
            result[str(record["function"])] = record
        if record.get("clang_usr"):
            result[str(record["clang_usr"])] = record
    return result


def _dependency_for_callee(
    callee: dict[str, Any], dependency_records: dict[str, dict[str, Any]]
) -> dict[str, Any] | None:
    for key in (str(callee.get("clang_usr", "")), str(callee.get("name", ""))):
        if key and key in dependency_records:
            return dependency_records[key]
    return None


def _structural_prediction_match(
    function: dict[str, Any],
    candidate: dict[str, Any],
    body: str,
    dependency_records: dict[str, dict[str, Any]],
) -> tuple[bool, dict[str, dict[str, Any]], list[str]]:
    parameters = function.get("parameters", []) or []
    pointers = function.get("pointer_parameters", []) or []
    scalar_ints = [item for item in parameters if not item.get("pointer") and item.get("type") == "int"]
    config_ptrs = [item for item in pointers if "dsc_cfg_t *" in str(item.get("type"))]
    state_ptrs = [item for item in pointers if "dsc_state_t *" in str(item.get("type"))]
    if function.get("return_type") != "void" or len(parameters) != 6:
        return False, {}, ["native ABI is not six-parameter void state transition"]
    if len(scalar_ints) != 4 or len(config_ptrs) != 1 or len(state_ptrs) != 1:
        return False, {}, ["signature does not contain one config/state pointer and four int arguments"]
    effects = _direct_effects(candidate)
    if effects.get("allocation") or effects.get("io") or effects.get("indirect_call"):
        return False, {}, ["allocation, I/O, or indirect call is in the direct effect set"]
    if not candidate.get("contributes_to_observable_output"):
        return False, {}, ["function does not contribute to an observable Encode output"]
    if int(function.get("loop_count", 0) or 0) < 3:
        return False, {}, ["bounded encoder shape requires one unit loop and two source while loops"]
    if len(re.findall(r"\bwhile\s*\(", body)) < 2:
        return False, {}, ["source does not expose both midpoint correction loops"]
    if not re.search(r"\bfor\s*\([^;]+;[^;]*unitsPerGroup", body):
        return False, {}, ["source has no unit loop bounded by state unitsPerGroup"]
    if not re.search(r"\bisEncoder\b", body):
        return False, {}, ["source has no encoder specialization predicate"]
    read_fields = _field_names(function, "fields_read", "dsc_state_t")
    config_read_fields = _field_names(function, "fields_read", "dsc_cfg_t")
    write_fields = _field_names(function, "fields_write", "dsc_state_t")
    required_reads = {
        "cpntBitDepth", "currLine", "maxError", "maxMidError",
        "origLine", "prevLine", "prevLinePred", "quantizedResidual",
        "quantizedResidualMid", "unitCType", "unitStartHPos", "unitsPerGroup",
    }
    required_writes = {
        "currLine", "maxError", "maxMidError", "midpointRecon", "primaryQp",
        "quantizedResidual", "quantizedResidualMid",
    }
    if (
        not required_reads.issubset(read_fields)
        or "native_420" not in config_read_fields
        or "full_ich_err_precision" not in config_read_fields
        or "bits_per_component" not in config_read_fields
        or not required_writes.issubset(write_fields)
    ):
        return False, {}, ["Clang field read/write footprint is not the complete encoder footprint"]
    callee_rows = [item for item in function.get("callees", []) or [] if isinstance(item, dict)]
    matched: dict[str, dict[str, Any]] = {}
    for callee in callee_rows:
        record = _dependency_for_callee(callee, dependency_records)
        if record:
            kind = _semantic_kind(record)
            role = dict(REQUIRED_DEPENDENCY_KINDS).get(kind, "")
            if role:
                matched[role] = record
    missing_roles = REQUIRED_DEPENDENCY_ROLES - set(matched)
    if missing_roles:
        return False, {}, ["semantic dependency set is incomplete: " + ", ".join(sorted(missing_roles))]
    evidence = [
        "Encode coverage is positive",
        "six-parameter void config/state transition signature matched structurally",
        "unit loop is bounded by the state unitsPerGroup field",
        "two midpoint while-loop source spans were identified for finite replacement",
        "complete encoder state write footprint matched Clang field facts",
        "all six dependencies joined by semantic kind and pinned contract identity",
        "function name is not an admission predicate",
    ]
    return True, matched, evidence


def discover_prediction_encode_candidates(
    functions_document: dict[str, Any],
    candidates_document: dict[str, Any],
    coverage_document: dict[str, Any],
    source_dir: pathlib.Path,
    dependency_records: dict[str, Any] | Iterable[dict[str, Any]],
) -> list[dict[str, Any]]:
    """Discover Encode prediction-loop candidates without a name allowlist."""
    dependency_index = _normalise_dependency_records(dependency_records)
    candidate_by_usr = {
        str(item.get("clang_usr")): item
        for item in rows(candidates_document)
        if item.get("clang_usr")
    }
    matches: list[dict[str, Any]] = []
    for function in rows(functions_document):
        usr = str(function.get("clang_usr", ""))
        covered, execution_count = _encode_coverage(_coverage_row(coverage_document, usr))
        if not covered:
            continue
        candidate = candidate_by_usr.get(usr, {})
        try:
            _, start, end, body = source_span(function, source_dir)
        except (KeyError, OSError):
            continue
        accepted, matched, evidence = _structural_prediction_match(
            function, candidate, body, dependency_index
        )
        if not accepted:
            continue
        matches.append(
            {
                "name": function.get("name"),
                "clang_usr": usr,
                "function": function,
                "execution_count": execution_count,
                "coverage": _coverage_row(coverage_document, usr),
                "semantics_kind": "bounded_prediction_encode_transition",
                "dependencies": matched,
                "source_span": {"start_line": start, "end_line": end},
                "selection_basis": evidence,
            }
        )
    return sorted(matches, key=lambda item: (-int(item["execution_count"]), str(item.get("clang_usr", ""))))


def _active_mse_definition(source_dir: pathlib.Path) -> bool:
    pattern = re.compile(r"^[ \t]*#[ \t]*define[ \t]+USE_MSE_FOR_ICH(?:[ \t]+|$)", re.MULTILINE)
    undef = re.compile(r"^[ \t]*//[ \t]*#define[ \t]+USE_MSE_FOR_ICH", re.MULTILINE)
    for source in sorted(source_dir.glob("*.c")):
        text = source.read_text(encoding="utf-8", errors="replace")
        if pattern.search(text) and not undef.search(text):
            return True
    return False


def _port(name: str, direction: str, *, signed: bool = True, width: int = 32) -> dict[str, Any]:
    return {"name": name, "direction": direction, "width": width, "signed": signed}


def _make_prediction_ports(max_units: int, samples: int, midpoint_slots: int) -> list[dict[str, Any]]:
    ports: list[dict[str, Any]] = []
    ports.extend(_port(name, "input") for name in ("hpos", "vpos", "sampmodcnt", "qp"))
    ports.extend(
        _port(name, "input")
        for name in (
            "cfg_native_420", "cfg_dsc_version_minor", "cfg_bits_per_component",
            "cfg_full_ich_err_precision", "state_is_encoder", "state_units_per_group",
            "state_primary_qp", "state_prev_line_prediction", "state_qlevel_luma_qp",
            "state_qlevel_chroma_qp",
        )
    )
    for index in range(4):
        ports.append(_port(f"state_cpnt_bit_depth_{index}", "input"))
        ports.append(_port(f"state_left_recon_{index}", "input"))
    for unit in range(max_units):
        for prefix in ("state_unit_c_type", "state_unit_start_hpos", "state_max_error", "state_max_mid_error", "orig_sample"):
            ports.append(_port(f"{prefix}_{unit}", "input"))
        for sample in range(samples):
            ports.append(_port(f"state_quantized_residual_{unit}_{sample}", "input"))
            ports.append(_port(f"state_quantized_residual_mid_{unit}_{sample}", "input"))
        for slot in range(midpoint_slots):
            ports.append(_port(f"state_midpoint_recon_{unit}_{slot}", "input"))
        for tap in range(15):
            ports.append(_port(f"prev_line_unit_{unit}_tap_{tap}", "input"))
        for tap in range(16):
            ports.append(_port(f"curr_line_unit_{unit}_tap_{tap}", "input"))
    for name in (
        "domain_valid", "illegal_domain", "bound_violation",
        "midpoint_clamp_violation", "arithmetic_domain_violation",
    ):
        ports.append(_port(name, "output", signed=False, width=1))
    ports.append(_port("state_primary_qp_out", "output"))
    for unit in range(max_units):
        for sample in range(samples):
            ports.append(_port(f"state_quantized_residual_{unit}_{sample}_out", "output"))
            ports.append(_port(f"state_quantized_residual_mid_{unit}_{sample}_out", "output"))
        for slot in range(midpoint_slots):
            ports.append(_port(f"state_midpoint_recon_{unit}_{slot}_out", "output"))
        ports.append(_port(f"state_max_error_{unit}_out", "output"))
        ports.append(_port(f"state_max_mid_error_{unit}_out", "output"))
        ports.append(_port(f"curr_line_write_{unit}_enable", "output", signed=False, width=1))
        ports.append(_port(f"curr_line_write_{unit}_component", "output"))
        ports.append(_port(f"curr_line_write_{unit}_index", "output"))
        ports.append(_port(f"curr_line_write_{unit}_value", "output"))
    return ports


def build_prediction_encode_contract(
    selected: dict[str, Any],
    source_dir: pathlib.Path,
    dependency_records: dict[str, Any] | Iterable[dict[str, Any]] | None = None,
) -> dict[str, Any]:
    """Build a hash-pinned, simulation-only Encode contract."""
    function = selected["function"]
    name = str(function["name"])
    _, start, end, body = source_span(function, source_dir)
    max_units = integer_define(source_dir, "MAX_UNITS_PER_GROUP")
    samples = integer_define(source_dir, "SAMPLES_PER_UNIT")
    padding = integer_define(source_dir, "PADDING_LEFT")
    pred_block_size = integer_define(source_dir, "PRED_BLK_SIZE")
    bp_range = integer_define(source_dir, "BP_RANGE")
    try:
        midpoint_slots = integer_define(source_dir, "MAX_PIXELS_PER_GROUP")
    except RuntimeError:
        midpoint_slots = samples * 2
    if (
        max_units > 4
        or samples != 3
        or padding != 5
        or pred_block_size != 3
        or bp_range != 13
        or midpoint_slots != 6
    ):
        raise RuntimeError("PredictionLoop generator requires the DSC 1.2a bounded shape")
    dependencies = selected.get("dependencies") if dependency_records is None else dependency_records
    if dependencies is None:
        raise RuntimeError("PredictionLoop contract requires pinned dependencies")
    dependency_index = _normalise_dependency_records(dependencies)
    by_role: dict[str, dict[str, Any]] = {}
    for _, role in REQUIRED_DEPENDENCY_KINDS:
        record = dependency_index.get(role)
        if not record:
            raise RuntimeError(f"missing pinned dependency role {role}")
        by_role[role] = record
    contract_id = safe_identifier(name) + "_encode_transition"
    dependency_manifest = []
    for kind, role in REQUIRED_DEPENDENCY_KINDS:
        record = by_role[role]
        contract = record.get("contract", {}) or {}
        if _semantic_kind(record) != kind:
            raise RuntimeError(f"dependency role {role} has wrong semantic kind")
        dependency_manifest.append(
            {
                "role": role,
                "semantic_kind": kind,
                "function": record.get("function") or (contract.get("function", {}) or {}).get("name"),
                "clang_usr": record.get("clang_usr") or (contract.get("function", {}) or {}).get("clang_usr"),
                "contract_id": record.get("contract_id") or contract.get("contract_id"),
                "contract_file": record.get("contract_file"),
                "contract_sha256": record.get("contract_sha256"),
                "manifest_contract_hash": record.get("manifest_contract_hash"),
                "module_file": record.get("module_file"),
                "module_sha256": record.get("module_sha256"),
                "source_body_sha256": record.get("source_body_sha256") or (contract.get("function", {}) or {}).get("source_body_sha256"),
            }
        )
    return {
        "schema_version": 2,
        "contract_id": contract_id,
        "status": "PROVISIONAL_SIMULATION_ONLY",
        "origin": "tool_discovered_encoder_runtime_transition",
        "function": {
            "clang_usr": function.get("clang_usr"),
            "name": name,
            "source_file": function.get("source_file"),
            "source_span": {"start_line": start, "end_line": end},
            "source_body_sha256": hashlib.sha256(body.encode("utf-8")).hexdigest(),
            "parameters": function.get("parameters", []),
            "return_type": function.get("return_type"),
        },
        "interface": {
            "ports": _make_prediction_ports(max_units, samples, midpoint_slots),
        },
        "dependencies": dependency_manifest,
        "semantics": {
            "kind": "bounded_prediction_encode_transition",
            "specialization": "isEncoder == 1",
            "constants": {
                "max_units": max_units,
                "samples_per_unit": samples,
                "midpoint_recon_slots": midpoint_slots,
                "padding_left": padding,
                "pred_block_size": pred_block_size,
                "pt_map": 0,
                "pt_left": 1,
                "pt_block": 2,
                "bp_range": bp_range,
                "max_component_bit_depth": 16,
            },
            "legal_domain": {
                "is_encoder": [1, 1],
                "units_per_group": [0, max_units],
                "component": [0, 3],
                "component_bit_depth": [8, 16],
                "bits_per_component": [8, 16],
                "sample_position": [0, samples - 1],
                "qp": [0, 31],
                "qlevel": [0, 16],
                "version_minor": [1, 2],
                "native_420": [0, 1],
                "full_ich_err_precision": [0, 1],
                "samples": [0, 65535],
                "signed_residual": [-65535, 65535],
                "prev_line_prediction": [0, 14],
                "source_order": "unit ascending, then the immutable C statements within each unit",
            },
            "bindings": {
                "horizontal_parameter": "hPos",
                "vertical_parameter": "vPos",
                "sample_count_parameter": "sampModCnt",
                "qp_parameter": "qp",
                "config_parameter": "dsc_cfg",
                "state_parameter": "dsc_state",
                "selected_qlevel_inputs": ["state_qlevel_luma_qp", "state_qlevel_chroma_qp"],
                "prev_line_prediction_input": "state_prev_line_prediction",
                "orig_sample_ports": [f"orig_sample_{unit}" for unit in range(max_units)],
                "write_sidebands": [
                    {
                        "enable": f"curr_line_write_{unit}_enable",
                        "component": f"curr_line_write_{unit}_component",
                        "index": f"curr_line_write_{unit}_index",
                        "value": f"curr_line_write_{unit}_value",
                    }
                    for unit in range(max_units)
                ],
            },
            "mse_mode": _active_mse_definition(source_dir),
            "midpoint_clamp": {
                "formulation": "exact_threshold_interval_projection",
                "source_loops": 2,
                "finite": True,
                "bound_violation_flag": "midpoint_clamp_violation",
                "proof": (
                    "For signed residual size N, the accepted interval is {-0} for N=0, "
                    "[-1,0] for N=1, and [-2^(N-1), 2^(N-1)-1] for N>=2. "
                    "The C loop moves one step toward that interval, so projection "
                    "has exactly the same terminal value and needs no unbounded loop."
                ),
            },
            "state_transition": (
                "Compute the encoder branch for up to four units and emit complete "
                "next-state arrays plus one ordered currLine write sideband per active unit."
            ),
        },
        "selection": {
            "basis": selected.get("selection_basis", []),
            "encode_execution_count": selected.get("execution_count", 0),
            "structural_discovery": True,
        },
        "obligations": [
            "C_ONLY/SHADOW/RTL_RETURN adapter integration is intentionally outside this generator",
            "full-frame Encode bit-true comparison before any promotion",
            "human review of the composed state/sideband contract before promotion",
        ],
        "promotion": {
            "status": "BLOCKED_PENDING_HUMAN_CONTRACT_REVIEW",
            "simulation_may_proceed": True,
        },
    }


def _port_decl(port: dict[str, Any]) -> str:
    width = int(port["width"])
    width_text = "" if width == 1 else f" [{width - 1}:0]"
    signed = " signed" if port.get("signed") else ""
    return f"    {port['direction']} logic{signed}{width_text} {port['name']}"


def _sv_signed_args(prefix: str, count: int) -> str:
    return ",\n".join(f"        input logic signed [31:0] {prefix}{index}_i" for index in range(count))


def _render_leaf_functions() -> str:
    qoffsets = [0, 0, 1, 3] + [(1 << q) // 2 - 1 for q in range(4, 17)]
    # The first four entries above are [q=0,q=1,q=2,q=3]; the expression for
    # q>=4 is the exact source QuantOffset formula.
    qoffsets = [0, 0, 1, 3, 7, 15, 31, 63, 127, 255, 511, 1023, 2047, 4095, 8191, 16383, 32767]
    current_args = ",\n".join(f"        input logic signed [31:0] curr_{index}_i" for index in range(16))
    prev_args = ",\n".join(f"        input logic signed [31:0] prev_{index}_i" for index in range(15))
    current_cases = "\n".join(
        f"                {index}: dsc_current_at_i = curr_{index}_i;"
        for index in range(16)
    )
    prev_names = [f"prev_{index}_i" for index in range(15)]
    curr_names = [f"curr_{index}_i" for index in range(16)]
    sample_args = ",\n".join(
        [
            "        input logic signed [31:0] hpos_i",
            "        input logic signed [31:0] pred_type_i",
            "        input logic signed [31:0] qlevel_i",
            "        input logic signed [31:0] depth_i",
            "        input logic signed [31:0] qr0_i",
            "        input logic signed [31:0] qr1_i",
            prev_args,
            current_args,
        ]
    )
    sample_call_current = ", ".join(curr_names)
    sample_call_prev = ", ".join(prev_names)
    return f"""
    function automatic signed [31:0] dsc_clamp_i(
        input logic signed [31:0] value_i,
        input logic signed [31:0] lower_i,
        input logic signed [31:0] upper_i);
        begin
            if (value_i < lower_i) dsc_clamp_i = lower_i;
            else if (value_i > upper_i) dsc_clamp_i = upper_i;
            else dsc_clamp_i = value_i;
        end
    endfunction

    function automatic signed [31:0] dsc_min_i(
        input logic signed [31:0] left_i,
        input logic signed [31:0] right_i);
        begin dsc_min_i = (left_i < right_i) ? left_i : right_i; end
    endfunction

    function automatic signed [31:0] dsc_max_i(
        input logic signed [31:0] left_i,
        input logic signed [31:0] right_i);
        begin dsc_max_i = (left_i > right_i) ? left_i : right_i; end
    endfunction

    function automatic signed [31:0] dsc_abs_i(
        input logic signed [31:0] value_i);
        begin dsc_abs_i = (value_i < 0) ? -value_i : value_i; end
    endfunction

    function automatic signed [31:0] dsc_map_qlevel_i(
        input logic signed [31:0] cpnt_i,
        input logic signed [31:0] native_i,
        input logic signed [31:0] version_i,
        input logic signed [31:0] depth0_i,
        input logic signed [31:0] depth1_i,
        input logic signed [31:0] luma_i,
        input logic signed [31:0] chroma_i);
        logic signed [31:0] mapped_i;
        begin
            if ((cpnt_i % 32'sd3) == 0) mapped_i = luma_i;
            else if ((native_i != 0) && (cpnt_i == 32'sd1)) mapped_i = luma_i;
            else begin
                mapped_i = chroma_i;
                if ((version_i == 32'sd2) && (depth0_i == depth1_i) && (mapped_i > 0))
                    mapped_i = mapped_i - 32'sd1;
            end
            dsc_map_qlevel_i = mapped_i;
        end
    endfunction

    function automatic signed [31:0] dsc_quantize_i(
        input logic signed [31:0] error_i,
        input logic signed [31:0] qlevel_i);
        logic signed [31:0] offset_i;
        begin
            offset_i = 32'sd0;
            case (qlevel_i)
{''.join(f'                {index}: offset_i = 32\'sd{value};\n' for index, value in enumerate(qoffsets))}                default: offset_i = 32'sd0;
            endcase
            if (error_i > 0)
                dsc_quantize_i = (error_i + offset_i) >>> qlevel_i;
            else
                dsc_quantize_i = -((offset_i - error_i) >>> qlevel_i);
        end
    endfunction

    function automatic signed [31:0] dsc_find_residual_size_i(
        input logic signed [31:0] error_i);
        begin
            dsc_find_residual_size_i = 0;
            if (error_i == 0) dsc_find_residual_size_i = 0;
            else if ((error_i >= -1) && (error_i <= 0)) dsc_find_residual_size_i = 1;
            else if ((error_i >= -2) && (error_i <= 1)) dsc_find_residual_size_i = 2;
            else if ((error_i >= -4) && (error_i <= 3)) dsc_find_residual_size_i = 3;
            else if ((error_i >= -8) && (error_i <= 7)) dsc_find_residual_size_i = 4;
            else if ((error_i >= -16) && (error_i <= 15)) dsc_find_residual_size_i = 5;
            else if ((error_i >= -32) && (error_i <= 31)) dsc_find_residual_size_i = 6;
            else if ((error_i >= -64) && (error_i <= 63)) dsc_find_residual_size_i = 7;
            else if ((error_i >= -128) && (error_i <= 127)) dsc_find_residual_size_i = 8;
            else if ((error_i >= -256) && (error_i <= 255)) dsc_find_residual_size_i = 9;
            else if ((error_i >= -512) && (error_i <= 511)) dsc_find_residual_size_i = 10;
            else if ((error_i >= -1024) && (error_i <= 1023)) dsc_find_residual_size_i = 11;
            else if ((error_i >= -2048) && (error_i <= 2047)) dsc_find_residual_size_i = 12;
            else if ((error_i >= -4096) && (error_i <= 4095)) dsc_find_residual_size_i = 13;
            else if ((error_i >= -8192) && (error_i <= 8191)) dsc_find_residual_size_i = 14;
            else if ((error_i >= -16384) && (error_i <= 16383)) dsc_find_residual_size_i = 15;
            else if ((error_i >= -32768) && (error_i <= 32767)) dsc_find_residual_size_i = 16;
            else if ((error_i >= -65536) && (error_i <= 65535)) dsc_find_residual_size_i = 17;
            else if ((error_i >= -131702) && (error_i <= 131701)) dsc_find_residual_size_i = 18;
        end
    endfunction

    function automatic signed [31:0] dsc_max_residual_size_i(
        input logic signed [31:0] cpnt_i,
        input logic signed [31:0] version_i,
        input logic signed [31:0] native_i,
        input logic signed [31:0] depth0_i,
        input logic signed [31:0] depth1_i,
        input logic signed [31:0] selected_depth_i,
        input logic signed [31:0] qlevel_luma_i,
        input logic signed [31:0] qlevel_chroma_i);
        logic signed [31:0] qlevel_i;
        logic signed [31:0] chroma_i;
        begin
            qlevel_i = qlevel_luma_i;
            if ((cpnt_i % 32'sd3) == 0) qlevel_i = qlevel_luma_i;
            else if ((native_i != 0) && (cpnt_i == 32'sd1)) qlevel_i = qlevel_luma_i;
            else begin
                chroma_i = qlevel_chroma_i;
                if ((version_i == 32'sd2) &&
                    (depth0_i == ((cpnt_i == 32'sd1) ? selected_depth_i : depth1_i)) &&
                    (chroma_i > 0)) chroma_i = chroma_i - 32'sd1;
                qlevel_i = (chroma_i < 0) ? 0 : chroma_i;
            end
            dsc_max_residual_size_i = selected_depth_i - qlevel_i;
        end
    endfunction

    function automatic signed [31:0] dsc_find_midpoint_i(
        input logic signed [31:0] depth_i,
        input logic signed [31:0] left_i,
        input logic signed [31:0] qlevel_i);
        begin
            dsc_find_midpoint_i = (32'sd1 <<< (depth_i - 32'sd1))
                + (left_i % (32'sd1 <<< qlevel_i));
        end
    endfunction

    function automatic signed [31:0] dsc_current_at_i(
        input logic signed [31:0] index_i,
{current_args});
        begin
            case (index_i)
{current_cases}
                default: dsc_current_at_i = 0;
            endcase
        end
    endfunction

    function automatic signed [31:0] dsc_sample_predict_i(
{sample_args});
        logic signed [31:0] a_i;
        logic signed [31:0] b_i;
        logic signed [31:0] c_i;
        logic signed [31:0] d_i;
        logic signed [31:0] e_i;
        logic signed [31:0] filt_b_i;
        logic signed [31:0] filt_c_i;
        logic signed [31:0] filt_d_i;
        logic signed [31:0] filt_e_i;
        logic signed [31:0] blend_b_i;
        logic signed [31:0] blend_c_i;
        logic signed [31:0] blend_d_i;
        logic signed [31:0] blend_e_i;
        logic signed [31:0] diff_i;
        logic signed [31:0] qdiv_i;
        logic signed [31:0] qhalf_i;
        logic signed [31:0] max_i;
        logic signed [31:0] window_start_i;
        logic signed [31:0] group_a_index_i;
        logic signed [31:0] block_global_index_i;
        logic signed [31:0] block_window_index_i;
        logic signed [31:0] block_i;
        logic signed [31:0] result_i;
        begin
            window_start_i = (hpos_i > 32'sd8) ? (hpos_i - 32'sd8) : 32'sd0;
            group_a_index_i = ((hpos_i / 32'sd3) * 32'sd3) + 32'sd4 - window_start_i;
            a_i = dsc_current_at_i(group_a_index_i, {sample_call_current});
            c_i = prev_1_i;
            b_i = prev_2_i;
            d_i = prev_3_i;
            e_i = prev_4_i;
            filt_c_i = (prev_0_i + (32'sd2 * prev_1_i) + prev_2_i + 32'sd2) >>> 2;
            filt_b_i = (prev_1_i + (32'sd2 * prev_2_i) + prev_3_i + 32'sd2) >>> 2;
            filt_d_i = (prev_2_i + (32'sd2 * prev_3_i) + prev_4_i + 32'sd2) >>> 2;
            filt_e_i = (prev_3_i + (32'sd2 * prev_4_i) + prev_5_i + 32'sd2) >>> 2;
            qdiv_i = 32'sd1 <<< qlevel_i;
            qhalf_i = qdiv_i / 32'sd2;
            max_i = (32'sd1 <<< depth_i) - 32'sd1;
            diff_i = dsc_clamp_i(filt_c_i - c_i, -qhalf_i, qhalf_i);
            blend_c_i = c_i + diff_i;
            diff_i = dsc_clamp_i(filt_b_i - b_i, -qhalf_i, qhalf_i);
            blend_b_i = b_i + diff_i;
            diff_i = dsc_clamp_i(filt_d_i - d_i, -qhalf_i, qhalf_i);
            blend_d_i = d_i + diff_i;
            diff_i = dsc_clamp_i(filt_e_i - e_i, -qhalf_i, qhalf_i);
            blend_e_i = e_i + diff_i;
            block_global_index_i = hpos_i + 32'sd5 - 32'sd1 - (pred_type_i - 32'sd2);
            if (block_global_index_i < 0) block_global_index_i = 0;
            block_window_index_i = block_global_index_i - window_start_i;
            block_i = dsc_current_at_i(block_window_index_i, {sample_call_current});
            result_i = 0;
            if ((hpos_i / 32'sd3) == 0) blend_c_i = a_i;
            if (pred_type_i == 32'sd0) begin
                if ((hpos_i % 32'sd3) == 0)
                    result_i = dsc_clamp_i(a_i + blend_b_i - blend_c_i,
                        dsc_min_i(a_i, blend_b_i), dsc_max_i(a_i, blend_b_i));
                else if ((hpos_i % 32'sd3) == 1)
                    result_i = dsc_clamp_i(a_i + blend_d_i - blend_c_i + (qr0_i * qdiv_i),
                        dsc_min_i(dsc_min_i(a_i, blend_b_i), blend_d_i),
                        dsc_max_i(dsc_max_i(a_i, blend_b_i), blend_d_i));
                else
                    result_i = dsc_clamp_i(a_i + blend_e_i - blend_c_i
                        + ((qr0_i + qr1_i) * qdiv_i),
                        dsc_min_i(dsc_min_i(a_i, blend_b_i), dsc_min_i(blend_d_i, blend_e_i)),
                        dsc_max_i(dsc_max_i(a_i, blend_b_i), dsc_max_i(blend_d_i, blend_e_i)));
            end else if (pred_type_i == 32'sd1) begin
                result_i = a_i;
                if ((hpos_i % 32'sd3) == 1)
                    result_i = dsc_clamp_i(a_i + (qr0_i * qdiv_i), 0, max_i);
                else if ((hpos_i % 32'sd3) == 2)
                    result_i = dsc_clamp_i(a_i + ((qr0_i + qr1_i) * qdiv_i), 0, max_i);
            end else result_i = block_i;
            dsc_sample_predict_i = result_i;
        end
    endfunction

    function automatic signed [31:0] dsc_lower_for_size_i(
        input logic signed [31:0] size_i);
        begin
            if (size_i <= 0) dsc_lower_for_size_i = 0;
            else if (size_i == 1) dsc_lower_for_size_i = -1;
            else dsc_lower_for_size_i = -(32'sd1 <<< (size_i - 1));
        end
    endfunction

    function automatic signed [31:0] dsc_upper_for_size_i(
        input logic signed [31:0] size_i);
        begin
            if (size_i <= 1) dsc_upper_for_size_i = 0;
            else dsc_upper_for_size_i = (32'sd1 <<< (size_i - 1)) - 32'sd1;
        end
    endfunction

    function automatic signed [31:0] dsc_project_midpoint_i(
        input logic signed [31:0] value_i,
        input logic signed [31:0] max_size_i);
        logic signed [31:0] lower_i;
        logic signed [31:0] upper_i;
        begin
            lower_i = dsc_lower_for_size_i(max_size_i);
            upper_i = dsc_upper_for_size_i(max_size_i);
            dsc_project_midpoint_i = dsc_clamp_i(value_i, lower_i, upper_i);
        end
    endfunction
""".strip("\n")


def render_prediction_encode_rtl(contract: dict[str, Any]) -> str:
    """Render a self-contained synthesizable SystemVerilog candidate."""
    semantics = contract.get("semantics", {}) or {}
    constants = semantics.get("constants", {}) or {}
    max_units = int(constants.get("max_units", 4))
    samples = int(constants.get("samples_per_unit", 3))
    midpoint_slots = int(constants.get("midpoint_recon_slots", 6))
    pt_block = int(constants.get("pt_block", 2))
    bp_range = int(constants.get("bp_range", 13))
    if max_units > 4 or samples != 3 or midpoint_slots != 6:
        raise RuntimeError("unsupported PredictionLoop RTL shape")
    _verify_render_dependency_hashes(contract)
    module = safe_identifier(str(contract["contract_id"]))
    port_lines = [_port_decl(port) for port in contract["interface"]["ports"]]
    declarations: list[str] = []
    for unit in range(max_units):
        declarations.extend(
            [
                f"    logic signed [31:0] cpnt_{unit}_i;",
                f"    logic signed [31:0] depth_{unit}_i;",
                f"    logic signed [31:0] qlevel_{unit}_i;",
                f"    logic signed [31:0] pred_type_{unit}_i;",
                f"    logic signed [31:0] pred_{unit}_i;",
                f"    logic signed [31:0] actual_{unit}_i;",
                f"    logic signed [31:0] err_raw_{unit}_i;",
                f"    logic signed [31:0] err_q_{unit}_i;",
                f"    logic signed [31:0] qmid_initial_{unit}_i;",
                f"    logic signed [31:0] qmid_{unit}_i;",
                f"    logic signed [31:0] max_size_{unit}_i;",
                f"    logic signed [31:0] max_value_{unit}_i;",
                f"    logic signed [31:0] recon_{unit}_i;",
                f"    logic signed [31:0] midpoint_pred_{unit}_i;",
                f"    logic signed [31:0] midpoint_recon_{unit}_i;",
                f"    logic signed [31:0] abs_error_{unit}_i;",
                f"    logic signed [31:0] abs_mid_error_{unit}_i;",
                f"    logic signed [31:0] residual_index_{unit}_i;",
                f"    logic signed [31:0] find_size_{unit}_i;",
            ]
        )
    functions = _render_leaf_functions()
    lines: list[str] = [
        f"module {module}(",
        ",\n".join(port_lines),
        ");",
        "",
        "    // Child contract pins are recorded in provisional-contract.json.",
        "    // Their pure semantics are inlined here to keep this candidate standalone.",
        *declarations,
        "",
        functions,
        "",
        "    always_comb begin",
        "        domain_valid = 1'b1;",
        "        illegal_domain = 1'b0;",
        "        bound_violation = 1'b0;",
        "        midpoint_clamp_violation = 1'b0;",
        "        arithmetic_domain_violation = 1'b0;",
        "        state_primary_qp_out = state_primary_qp;",
    ]
    for unit in range(max_units):
        for sample in range(samples):
            lines.extend(
                [
                    f"        state_quantized_residual_{unit}_{sample}_out = state_quantized_residual_{unit}_{sample};",
                    f"        state_quantized_residual_mid_{unit}_{sample}_out = state_quantized_residual_mid_{unit}_{sample};",
                ]
            )
        for slot in range(midpoint_slots):
            lines.append(
                f"        state_midpoint_recon_{unit}_{slot}_out = state_midpoint_recon_{unit}_{slot};"
            )
        lines.extend(
            [
                f"        state_max_error_{unit}_out = state_max_error_{unit};",
                f"        state_max_mid_error_{unit}_out = state_max_mid_error_{unit};",
                f"        curr_line_write_{unit}_enable = 1'b0;",
                f"        curr_line_write_{unit}_component = 32'sd0;",
                f"        curr_line_write_{unit}_index = 32'sd0;",
                f"        curr_line_write_{unit}_value = 32'sd0;",
            ]
        )
        for local in (
            "cpnt", "depth", "qlevel", "pred_type", "pred", "actual", "err_raw",
            "err_q", "qmid_initial", "qmid", "max_size", "max_value", "recon",
            "midpoint_pred", "midpoint_recon", "abs_error", "abs_mid_error",
            "residual_index", "find_size",
        ):
            lines.append(f"        {local}_{unit}_i = 32'sd0;")
    lines.extend(
        [
            "",
            "        if ((state_is_encoder != 32'sd1) ||",
            f"            (state_units_per_group < 0) || (state_units_per_group > 32'sd{max_units}) ||",
            "            (hpos < 0) || (vpos < 0) ||",
            f"            (sampmodcnt < 0) || (sampmodcnt >= 32'sd{samples}) ||",
            "            (qp < 0) || (qp > 32'sd31) ||",
            "            ((cfg_native_420 != 0) && (cfg_native_420 != 1)) ||",
            "            ((cfg_dsc_version_minor != 32'sd1) && (cfg_dsc_version_minor != 32'sd2)) ||",
            "            (cfg_bits_per_component < 32'sd8) || (cfg_bits_per_component > 32'sd16) ||",
            "            ((cfg_full_ich_err_precision != 0) && (cfg_full_ich_err_precision != 1)) ||",
            "            (state_qlevel_luma_qp < 0) || (state_qlevel_luma_qp > 32'sd16) ||",
            "            (state_qlevel_chroma_qp < 0) || (state_qlevel_chroma_qp > 32'sd16) ||",
            f"            (state_prev_line_prediction < 0) || (state_prev_line_prediction > 32'sd{pt_block + bp_range - 1})) begin",
            "            domain_valid = 1'b0;",
            "            illegal_domain = 1'b1;",
            "        end",
        ]
    )
    for unit in range(max_units):
        depth_expr = "((cpnt_%d_i == 32'sd0) ? state_cpnt_bit_depth_0 : ((cpnt_%d_i == 32'sd1) ? state_cpnt_bit_depth_1 : ((cpnt_%d_i == 32'sd2) ? state_cpnt_bit_depth_2 : state_cpnt_bit_depth_3)))" % (unit, unit, unit)
        left_expr = "((cpnt_%d_i == 32'sd0) ? state_left_recon_0 : ((cpnt_%d_i == 32'sd1) ? state_left_recon_1 : ((cpnt_%d_i == 32'sd2) ? state_left_recon_2 : state_left_recon_3)))" % (unit, unit, unit)
        prev_args = ", ".join(f"prev_line_unit_{unit}_tap_{tap}" for tap in range(15))
        curr_args = ", ".join(f"curr_line_unit_{unit}_tap_{tap}" for tap in range(16))
        lines.extend(
            [
                f"        cpnt_{unit}_i = state_unit_c_type_{unit};",
                f"        depth_{unit}_i = {depth_expr};",
                f"        qlevel_{unit}_i = dsc_map_qlevel_i(cpnt_{unit}_i, cfg_native_420, cfg_dsc_version_minor, state_cpnt_bit_depth_0, state_cpnt_bit_depth_1, state_qlevel_luma_qp, state_qlevel_chroma_qp);",
                f"        residual_index_{unit}_i = sampmodcnt - state_unit_start_hpos_{unit};",
                f"        pred_type_{unit}_i = (vpos == 0) ? 32'sd1 : state_prev_line_prediction;",
                f"        if ((cfg_native_420 != 0) && (cpnt_{unit}_i == 32'sd2))",
                f"            pred_type_{unit}_i = (vpos <= 32'sd1) ? 32'sd1 : 32'sd0;",
                f"        pred_{unit}_i = dsc_sample_predict_i(hpos, pred_type_{unit}_i, qlevel_{unit}_i, depth_{unit}_i, state_quantized_residual_{unit}_0, state_quantized_residual_{unit}_1, {prev_args}, {curr_args});",
                f"        actual_{unit}_i = orig_sample_{unit};",
                f"        err_raw_{unit}_i = actual_{unit}_i - pred_{unit}_i;",
                f"        qlevel_{unit}_i = dsc_map_qlevel_i(cpnt_{unit}_i, cfg_native_420, cfg_dsc_version_minor, state_cpnt_bit_depth_0, state_cpnt_bit_depth_1, state_qlevel_luma_qp, state_qlevel_chroma_qp);",
                f"        err_q_{unit}_i = dsc_quantize_i(err_raw_{unit}_i, qlevel_{unit}_i);",
                f"        midpoint_pred_{unit}_i = dsc_find_midpoint_i(depth_{unit}_i, {left_expr}, qlevel_{unit}_i);",
                f"        err_raw_{unit}_i = actual_{unit}_i - midpoint_pred_{unit}_i;",
                f"        qmid_initial_{unit}_i = dsc_quantize_i(err_raw_{unit}_i, qlevel_{unit}_i);",
                f"        max_size_{unit}_i = dsc_max_residual_size_i(cpnt_{unit}_i, cfg_dsc_version_minor, cfg_native_420, state_cpnt_bit_depth_0, state_cpnt_bit_depth_1, depth_{unit}_i, state_qlevel_luma_qp, state_qlevel_chroma_qp);",
                f"        find_size_{unit}_i = dsc_find_residual_size_i(qmid_initial_{unit}_i);",
                f"        qmid_{unit}_i = dsc_project_midpoint_i(qmid_initial_{unit}_i, max_size_{unit}_i);",
            ]
        )
        lines.extend(
            [
                f"        if (state_units_per_group > 32'sd{unit}) begin",
                f"            if ((cpnt_{unit}_i < 0) || (cpnt_{unit}_i > 32'sd3) || (depth_{unit}_i < 32'sd8) || (depth_{unit}_i > 32'sd16) || (qlevel_{unit}_i < 0) || (qlevel_{unit}_i > depth_{unit}_i) || (state_unit_start_hpos_{unit} < 0) || (state_unit_start_hpos_{unit} >= 32'sd{samples}) || (residual_index_{unit}_i < 0) || (residual_index_{unit}_i >= 32'sd{samples})) begin",
                "                domain_valid = 1'b0;",
                "                illegal_domain = 1'b1;",
                "            end",
                f"            if ((orig_sample_{unit} < 0) || (orig_sample_{unit} > 32'sd65535) || (state_left_recon_{unit} < 0) || (state_left_recon_{unit} > 32'sd65535)) begin",
                "                domain_valid = 1'b0;",
                "                arithmetic_domain_violation = 1'b1;",
                "            end",
                f"            if (dsc_find_residual_size_i(qmid_{unit}_i) > max_size_{unit}_i)",
                "                midpoint_clamp_violation = 1'b1;",
                "            if (sampmodcnt == 0) state_primary_qp_out = qp;",
                f"            if ((residual_index_{unit}_i >= 0) && (residual_index_{unit}_i < 32'sd{samples})) begin",
            ]
        )
        for sample in range(samples):
            lines.extend(
                [
                    f"                if (residual_index_{unit}_i == 32'sd{sample}) begin",
                    f"                    state_quantized_residual_{unit}_{sample}_out = err_q_{unit}_i;",
                    f"                    state_quantized_residual_mid_{unit}_{sample}_out = qmid_{unit}_i;",
                    "                end",
                ]
            )
        lines.extend(
            [
                "            end",
                f"            max_value_{unit}_i = (32'sd1 <<< depth_{unit}_i) - 32'sd1;",
                f"            recon_{unit}_i = dsc_clamp_i(pred_{unit}_i + (err_q_{unit}_i <<< qlevel_{unit}_i), 0, max_value_{unit}_i);",
                f"            abs_error_{unit}_i = dsc_abs_i(actual_{unit}_i - recon_{unit}_i);",
                f"            if (cfg_full_ich_err_precision == 0)",
                f"                abs_error_{unit}_i = abs_error_{unit}_i >>> (cfg_bits_per_component - 32'sd8);",
            ]
        )
        if bool(semantics.get("mse_mode")):
            lines.extend(
                [
                    f"            state_max_error_{unit}_out = state_max_error_{unit} + (abs_error_{unit}_i * abs_error_{unit}_i);",
                ]
            )
        else:
            lines.extend(
                [
                    f"            state_max_error_{unit}_out = dsc_max_i(state_max_error_{unit}, abs_error_{unit}_i);",
                ]
            )
        lines.extend(
            [
                f"            midpoint_pred_{unit}_i = dsc_find_midpoint_i(depth_{unit}_i, {left_expr}, qlevel_{unit}_i);",
                f"            midpoint_recon_{unit}_i = midpoint_pred_{unit}_i + (qmid_{unit}_i <<< qlevel_{unit}_i);",
                f"            midpoint_recon_{unit}_i = dsc_clamp_i(midpoint_recon_{unit}_i, 0, max_value_{unit}_i);",
            ]
        )
        for sample in range(samples):
            lines.extend(
                [
                    f"            if (residual_index_{unit}_i == 32'sd{sample})",
                    f"                state_midpoint_recon_{unit}_{sample}_out = midpoint_recon_{unit}_i;",
                ]
            )
        lines.extend(
            [
                f"            abs_mid_error_{unit}_i = dsc_abs_i(actual_{unit}_i - midpoint_recon_{unit}_i);",
                f"            if (cfg_full_ich_err_precision == 0)",
                f"                abs_mid_error_{unit}_i = abs_mid_error_{unit}_i >>> (cfg_bits_per_component - 32'sd8);",
            ]
        )
        if bool(semantics.get("mse_mode")):
            lines.extend(
                [
                    f"            state_max_mid_error_{unit}_out = state_max_mid_error_{unit} + (abs_mid_error_{unit}_i * abs_mid_error_{unit}_i);",
                ]
            )
        else:
            lines.extend(
                [
                    f"            state_max_mid_error_{unit}_out = dsc_max_i(state_max_mid_error_{unit}, abs_mid_error_{unit}_i);",
                ]
            )
        lines.extend(
            [
                f"            curr_line_write_{unit}_enable = 1'b1;",
                f"            curr_line_write_{unit}_component = cpnt_{unit}_i;",
                f"            curr_line_write_{unit}_index = hpos + 32'sd{int(constants.get('padding_left', 5))};",
                f"            curr_line_write_{unit}_value = recon_{unit}_i;",
                "        end",
            ]
        )
    lines.extend(
        [
            "        if (midpoint_clamp_violation != 0) bound_violation = 1'b1;",
            "        if (illegal_domain != 0) domain_valid = 1'b0;",
            "        if (bound_violation != 0) domain_valid = 1'b0;",
            "    end",
            "endmodule",
            "",
        ]
    )
    return "\n".join(lines)


def _verify_render_dependency_hashes(contract: dict[str, Any]) -> None:
    repo_root = pathlib.Path(__file__).resolve().parent.parent
    roles: set[str] = set()
    for dependency in contract.get("dependencies", []) or []:
        role = str(dependency.get("role", ""))
        if role:
            roles.add(role)
        for key, digest_key in (("contract_file", "contract_sha256"), ("module_file", "module_sha256")):
            raw = dependency.get(key)
            expected = str(dependency.get(digest_key, ""))
            if not raw or not expected:
                raise RuntimeError(f"missing hash pin for dependency {role}")
            path = pathlib.Path(str(raw))
            if not path.is_absolute():
                path = repo_root / path
            if not path.is_file():
                raise RuntimeError(f"pinned dependency file is missing: {path}")
            actual = file_sha256(path)
            if actual != expected:
                raise RuntimeError(f"pinned dependency changed: {path}")
    if roles != REQUIRED_DEPENDENCY_ROLES:
        raise RuntimeError(
            "PredictionLoop RTL requires exactly the six pinned dependency roles; "
            f"got {sorted(roles)}"
        )


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=pathlib.Path, default=pathlib.Path.cwd())
    parser.add_argument("--source-dir", type=pathlib.Path, required=True)
    parser.add_argument("--functions", type=pathlib.Path, default=None)
    parser.add_argument("--candidates", type=pathlib.Path, default=None)
    parser.add_argument("--coverage", type=pathlib.Path, default=None)
    parser.add_argument("--output", type=pathlib.Path, required=True)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    root = args.root.resolve()
    functions = read_json(args.functions or root / "facts" / "functions.json")
    candidates = read_json(args.candidates or root / "facts" / "candidates.json")
    coverage = read_json(args.coverage or root / "coverage" / "coverage.json")
    dependencies = load_pinned_dependencies(root)
    matches = discover_prediction_encode_candidates(
        functions, candidates, coverage, args.source_dir.resolve(), dependencies
    )
    if not matches:
        raise SystemExit("DISCOVERY_INCOMPLETE: no structurally admitted Encode prediction candidate")
    selected = matches[0]
    contract = build_prediction_encode_contract(selected, args.source_dir.resolve(), dependencies)
    args.output.mkdir(parents=True, exist_ok=True)
    write_json(args.output / "provisional-contract.json", contract)
    (args.output / "candidate_01.sv").write_text(
        render_prediction_encode_rtl(contract), encoding="utf-8"
    )
    print(f"generated {contract['contract_id']} ({selected['execution_count']} Encode calls)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
