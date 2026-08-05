#!/usr/bin/env python3
"""Generate a provisional combinational RTL state-transition candidate.

Input selection comes from decode_frontier.py's Clang/runtime-fact matchers.
Generated candidates never self-promote; full-frame C/Verilator simulation is
required before human contract review can make one eligible for the stable
library.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import pathlib
import re
from typing import Any


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
    for header in sorted(source_dir.glob("*.h")):
        match = pattern.search(header.read_text(encoding="utf-8", errors="replace"))
        if match:
            matches.add(int(match.group(1)))
    if len(matches) != 1:
        raise RuntimeError(f"expected one integer definition for {name}, got {sorted(matches)}")
    return next(iter(matches))


def integer_field_assignment_values(
    source_dir: pathlib.Path, field: str, *, multiple_of: int = 1
) -> list[int]:
    """Collect plausible integer values from direct field assignments."""
    assignment = re.compile(r"\b" + re.escape(field) + r"\s*=\s*([^;]+);")
    values: set[int] = set()
    for source in sorted(source_dir.glob("*.c")):
        text_value = source.read_text(encoding="utf-8", errors="replace")
        for expression in assignment.findall(text_value):
            for literal in re.findall(r"\b\d+\b", expression):
                value = int(literal)
                if value > 0 and value % multiple_of == 0:
                    values.add(value)
    return sorted(values)


def select(frontier: dict[str, Any]) -> dict[str, Any]:
    candidates = frontier.get("provisional_transition_candidates", []) or []
    if not candidates:
        raise RuntimeError("decode frontier has no provisional transition candidate")
    # decode_frontier already provides a deterministic execution-count/name
    # order; consuming its first row is routing, not a function allowlist.
    return candidates[0]


def build_contract(
    selected: dict[str, Any], function: dict[str, Any], source_dir: pathlib.Path
) -> dict[str, Any]:
    semantics_kind = selected.get("semantics_kind")
    if semantics_kind == "fifo_read_transition":
        return build_fifo_read_contract(selected, function, source_dir)
    if semantics_kind == "fifo_read_accounting_transition":
        return build_fifo_read_accounting_contract(selected, function, source_dir)
    if semantics_kind == "fifo_write_transition":
        return build_fifo_write_contract(selected, function, source_dir)
    if semantics_kind == "scalar_record_next_state":
        return build_scalar_record_next_state_contract(selected, function, source_dir)
    if semantics_kind == "sampled_lookup_transition":
        return build_sampled_lookup_contract(selected, function, source_dir)
    if semantics_kind == "scalar_record_memory_transition":
        return build_scalar_record_memory_contract(selected, function, source_dir)
    if semantics_kind == "bounded_mux_refill_transition":
        return build_bounded_mux_refill_contract(selected, function, source_dir)
    if semantics_kind == "bounded_flatness_state_transition":
        return build_bounded_flatness_state_contract(selected, function, source_dir)
    if semantics_kind == "bounded_line_write_transition":
        return build_bounded_line_write_contract(selected, function, source_dir)
    if semantics_kind == "bounded_history_update_transition":
        return build_bounded_history_update_contract(selected, function, source_dir)
    if semantics_kind == "bounded_history_caller_transition":
        return build_bounded_history_caller_contract(selected, function, source_dir)
    if semantics_kind == "bounded_vld_unit_transition":
        return build_bounded_vld_unit_contract(selected, function, source_dir)
    if semantics_kind == "bounded_block_pred_search_transition":
        return build_bounded_block_pred_search_contract(
            selected, function, source_dir
        )
    if semantics_kind == "bounded_prediction_decode_transition":
        return build_bounded_prediction_decode_contract(
            selected, function, source_dir
        )
    if semantics_kind == "bounded_rate_control_decode_transition":
        return build_bounded_rate_control_decode_contract(
            selected, function, source_dir
        )
    if semantics_kind == "bounded_vld_group_decode_transition":
        return build_bounded_vld_group_decode_contract(
            selected, function, source_dir
        )
    if semantics_kind == "raster_color_transform_transition":
        return build_raster_color_transform_contract(
            selected, function, source_dir
        )
    maximum = int(selected["literal_size_bound"]["maximum"])
    window_bytes = int(selected["window_bytes"])
    name = str(function["name"])
    cid = safe_identifier(name) + "_decode_transition"
    byte_ports = [f"byte_{index}" for index in range(window_bytes)]
    ports = [
        {"name": "size", "direction": "input", "width": 5, "signed": False},
        *[
            {"name": port, "direction": "input", "width": 8, "signed": False}
            for port in byte_ports
        ],
        {"name": "bit_count", "direction": "input", "width": 32, "signed": False},
        {"name": "sign_extend", "direction": "input", "width": 1, "signed": False},
        {"name": "return_value", "direction": "output", "width": 32, "signed": True},
        {"name": "bit_count_out", "direction": "output", "width": 32, "signed": False},
    ]
    source = source_dir / str(function["source_file"])
    lines = source.read_text(encoding="utf-8", errors="replace").splitlines()
    start = int(function.get("line", 1))
    end = int(function.get("end_line", start))
    body = "\n".join(lines[start - 1:end])
    parameters = function.get("parameters", []) or []
    read_buffer = next(
        item for item in function.get("pointer_parameters", [])
        if item.get("mode") == "READ_ONLY" and "unsigned char *" in str(item.get("type"))
    )
    cursor = next(
        item for item in function.get("pointer_parameters", [])
        if item.get("mode") == "WRITES_THROUGH" and "int *" in str(item.get("type"))
    )
    scalar_names = [
        str(item.get("name")) for item in parameters if not item.get("pointer")
    ]
    size_parameter = scalar_names[0]
    sign_parameter = scalar_names[-1]
    return {
        "schema_version": 2,
        "contract_id": cid,
        "status": "PROVISIONAL_SIMULATION_ONLY",
        "origin": "tool_discovered_decoder_runtime_transition",
        "function": {
            "clang_usr": function.get("clang_usr"),
            "name": name,
            "source_file": function.get("source_file"),
            "source_span": {"start_line": start, "end_line": end},
            "source_body_sha256": hashlib.sha256(body.encode("utf-8")).hexdigest(),
            "parameters": parameters,
            "return_type": function.get("return_type"),
        },
        "interface": {"ports": ports},
        "semantics": {
            "kind": "bitstream_read_transition",
            "max_bits": maximum,
            "legal_size_values": selected["literal_size_bound"]["values"],
            "window_bytes": window_bytes,
            "bindings": {
                "size_parameter": size_parameter,
                "buffer_parameter": read_buffer["name"],
                "cursor_parameter": cursor["name"],
                "sign_extend_parameter": sign_parameter,
                "size_port": "size",
                "byte_ports": byte_ports,
                "cursor_port": "bit_count",
                "sign_extend_port": "sign_extend",
                "return_port": "return_value",
                "cursor_output_port": "bit_count_out",
            },
            "state_transition": (
                "return selected MSB-first bits and advance the explicit bit cursor by size"
            ),
        },
        "selection": {
            "basis": selected["selection_basis"],
            "decode_execution_count": selected.get("execution_count"),
            "literal_size_bound": selected["literal_size_bound"],
        },
        "obligations": [
            "full-frame Decode C_ONLY/SHADOW/RTL_RETURN comparison",
            "full-frame Encode C_ONLY/SHADOW/RTL_RETURN comparison",
            "human review of explicit cursor state contract before promotion",
        ],
        "promotion": {
            "status": "BLOCKED_PENDING_HUMAN_CONTRACT_REVIEW",
            "simulation_may_proceed": True,
        },
    }


def build_fifo_read_contract(
    selected: dict[str, Any], function: dict[str, Any], source_dir: pathlib.Path
) -> dict[str, Any]:
    maximum = int(selected.get("provisional_max_bits") or selected["literal_size_bound"]["maximum"])
    window_bytes = int(selected["window_bytes"])
    nbits_width = max(1, maximum.bit_length())
    name = str(function["name"])
    cid = safe_identifier(name) + "_decode_transition"
    byte_ports = [f"byte_{index}" for index in range(window_bytes)]
    ports = [
        {"name": "nbits", "direction": "input", "width": nbits_width, "signed": False},
        *[
            {"name": port, "direction": "input", "width": 8, "signed": False}
            for port in byte_ports
        ],
        {"name": "fullness", "direction": "input", "width": 32, "signed": False},
        {"name": "read_ptr", "direction": "input", "width": 32, "signed": False},
        {"name": "fifo_size", "direction": "input", "width": 32, "signed": False},
        {"name": "sign_extend", "direction": "input", "width": 1, "signed": False},
        {"name": "return_value", "direction": "output", "width": 32, "signed": True},
        {"name": "fullness_out", "direction": "output", "width": 32, "signed": False},
        {"name": "read_ptr_out", "direction": "output", "width": 32, "signed": False},
    ]
    source = source_dir / str(function["source_file"])
    lines = source.read_text(encoding="utf-8", errors="replace").splitlines()
    start = int(function.get("line", 1))
    end = int(function.get("end_line", start))
    body = "\n".join(lines[start - 1:end])
    parameters = function.get("parameters", []) or []
    fifo_parameter = next(
        item for item in function.get("pointer_parameters", [])
        if item.get("mode") == "WRITES_THROUGH" and "fifo_t *" in str(item.get("type"))
    )
    scalars = [item for item in parameters if not item.get("pointer")]
    return {
        "schema_version": 2,
        "contract_id": cid,
        "status": "PROVISIONAL_SIMULATION_ONLY",
        "origin": "tool_discovered_decoder_runtime_transition",
        "function": {
            "clang_usr": function.get("clang_usr"),
            "name": name,
            "source_file": function.get("source_file"),
            "source_span": {"start_line": start, "end_line": end},
            "source_body_sha256": hashlib.sha256(body.encode("utf-8")).hexdigest(),
            "parameters": parameters,
            "return_type": function.get("return_type"),
        },
        "interface": {"ports": ports},
        "semantics": {
            "kind": "fifo_read_transition",
            "max_bits": maximum,
            "window_bytes": window_bytes,
            "legal_domain": {
                "nbits": [0, maximum],
                "fullness_at_least_nbits": True,
                "fifo_size_positive_multiple_of_8": True,
            },
            "bindings": {
                "fifo_parameter": fifo_parameter["name"],
                "nbits_parameter": scalars[0]["name"],
                "sign_extend_parameter": scalars[-1]["name"],
                "nbits_port": "nbits",
                "byte_ports": byte_ports,
                "fullness_port": "fullness",
                "read_ptr_port": "read_ptr",
                "fifo_size_port": "fifo_size",
                "sign_extend_port": "sign_extend",
                "return_port": "return_value",
                "fullness_output_port": "fullness_out",
                "read_ptr_output_port": "read_ptr_out",
            },
            "state_transition": (
                "return n MSB-first FIFO bits, decrement fullness, and advance/wrap read_ptr"
            ),
        },
        "selection": {
            "basis": selected["selection_basis"],
            "decode_execution_count": selected.get("execution_count"),
            "literal_size_bound": selected["literal_size_bound"],
        },
        "obligations": [
            "full-frame Decode C_ONLY/SHADOW/RTL_RETURN comparison",
            "full-frame Encode C_ONLY/SHADOW/RTL_RETURN comparison",
            "human review of FIFO legal-domain and explicit state outputs before promotion",
        ],
        "promotion": {
            "status": "BLOCKED_PENDING_HUMAN_CONTRACT_REVIEW",
            "simulation_may_proceed": True,
        },
    }


def build_fifo_read_accounting_contract(
    selected: dict[str, Any], function: dict[str, Any], source_dir: pathlib.Path
) -> dict[str, Any]:
    """Freeze a caller-visible bit-accounting + FIFO-read next-state boundary."""
    maximum = int(
        selected.get("provisional_max_bits")
        or selected["literal_size_bound"]["maximum"]
    )
    window_bytes = int(selected["window_bytes"])
    nbits_width = max(1, maximum.bit_length())
    name = str(function["name"])
    cid = safe_identifier(name) + "_fifo_accounting_decode_transition"
    byte_ports = [f"byte_{index}" for index in range(window_bytes)]
    ports = [
        {"name": "nbits", "direction": "input", "width": nbits_width, "signed": False},
        *[
            {"name": port, "direction": "input", "width": 8, "signed": False}
            for port in byte_ports
        ],
        {"name": "bit_count", "direction": "input", "width": 32, "signed": True},
        {"name": "fullness", "direction": "input", "width": 32, "signed": False},
        {"name": "read_ptr", "direction": "input", "width": 32, "signed": False},
        {"name": "fifo_size", "direction": "input", "width": 32, "signed": False},
        {"name": "sign_extend", "direction": "input", "width": 1, "signed": False},
        {"name": "return_value", "direction": "output", "width": 32, "signed": True},
        {"name": "bit_count_out", "direction": "output", "width": 32, "signed": True},
        {"name": "fullness_out", "direction": "output", "width": 32, "signed": False},
        {"name": "read_ptr_out", "direction": "output", "width": 32, "signed": False},
    ]
    source = source_dir / str(function["source_file"])
    lines = source.read_text(encoding="utf-8", errors="replace").splitlines()
    start = int(function.get("line", 1))
    end = int(function.get("end_line", start))
    body = "\n".join(lines[start - 1:end])
    parameters = function.get("parameters", []) or []
    state_parameter = next(
        item for item in function.get("pointer_parameters", [])
        if "dsc_state_t *" in str(item.get("type"))
    )
    scalars = [item for item in parameters if not item.get("pointer")]
    state_counter = next(
        item for item in function.get("fields_write", [])
        if item.get("record") == "dsc_state_t" and item.get("type") == "int"
    )
    fifo_array = next(
        item for item in function.get("fields_read", [])
        if item.get("record") == "dsc_state_t"
        and str(item.get("type", "")).startswith("fifo_t[")
    )
    return {
        "schema_version": 2,
        "contract_id": cid,
        "status": "PROVISIONAL_SIMULATION_ONLY",
        "origin": "tool_discovered_decoder_runtime_transition",
        "function": {
            "clang_usr": function.get("clang_usr"),
            "name": name,
            "source_file": function.get("source_file"),
            "source_span": {"start_line": start, "end_line": end},
            "source_body_sha256": hashlib.sha256(body.encode("utf-8")).hexdigest(),
            "parameters": parameters,
            "return_type": function.get("return_type"),
        },
        "interface": {"ports": ports},
        "semantics": {
            "kind": "fifo_read_accounting_transition",
            "max_bits": maximum,
            "window_bytes": window_bytes,
            "legal_domain": {
                "nbits": [0, maximum],
                "fullness_at_least_nbits": True,
                "fifo_size_positive_multiple_of_8": True,
            },
            "bindings": {
                "state_parameter": state_parameter["name"],
                "unit_parameter": scalars[0]["name"],
                "nbits_parameter": scalars[1]["name"],
                "sign_extend_parameter": scalars[2]["name"],
                "state_counter_field": state_counter["name"],
                "fifo_array_field": fifo_array["name"],
                "nbits_port": "nbits",
                "byte_ports": byte_ports,
                "bit_count_port": "bit_count",
                "fullness_port": "fullness",
                "read_ptr_port": "read_ptr",
                "fifo_size_port": "fifo_size",
                "sign_extend_port": "sign_extend",
                "return_port": "return_value",
                "bit_count_output_port": "bit_count_out",
                "fullness_output_port": "fullness_out",
                "read_ptr_output_port": "read_ptr_out",
            },
            "state_transition": (
                "increment the explicit bit counter, return n MSB-first FIFO bits, "
                "decrement fullness, and advance/wrap read_ptr"
            ),
        },
        "selection": {
            "basis": selected["selection_basis"],
            "decode_execution_count": selected.get("execution_count"),
            "callee_contract_id": selected.get("callee_contract_id"),
            "literal_size_bound": selected["literal_size_bound"],
        },
        "obligations": [
            "full-frame Decode C_ONLY/SHADOW/RTL_RETURN comparison",
            "full-frame Encode C_ONLY/SHADOW/RTL_RETURN comparison",
            "human review of composed bit-accounting and FIFO state outputs before promotion",
        ],
        "promotion": {
            "status": "BLOCKED_PENDING_HUMAN_CONTRACT_REVIEW",
            "simulation_may_proceed": True,
        },
    }


def build_fifo_write_contract(
    selected: dict[str, Any], function: dict[str, Any], source_dir: pathlib.Path
) -> dict[str, Any]:
    """Freeze a bounded FIFO memory-window write plus scalar next state."""
    maximum = int(
        selected.get("provisional_max_bits")
        or selected["literal_size_bound"]["maximum"]
    )
    window_bytes = int(selected["window_bytes"])
    nbits_width = max(1, maximum.bit_length())
    name = str(function["name"])
    cid = safe_identifier(name) + "_decode_transition"
    byte_ports = [f"byte_{index}" for index in range(window_bytes)]
    byte_output_ports = [f"{name}_out" for name in byte_ports]
    ports = [
        {"name": "data", "direction": "input", "width": 32, "signed": False},
        {"name": "nbits", "direction": "input", "width": nbits_width, "signed": False},
        *[
            {"name": port, "direction": "input", "width": 8, "signed": False}
            for port in byte_ports
        ],
        {"name": "fullness", "direction": "input", "width": 32, "signed": False},
        {"name": "write_ptr", "direction": "input", "width": 32, "signed": False},
        {"name": "fifo_size", "direction": "input", "width": 32, "signed": False},
        {"name": "max_fullness", "direction": "input", "width": 32, "signed": False},
        *[
            {"name": port, "direction": "output", "width": 8, "signed": False}
            for port in byte_output_ports
        ],
        {"name": "fullness_out", "direction": "output", "width": 32, "signed": False},
        {"name": "write_ptr_out", "direction": "output", "width": 32, "signed": False},
        {"name": "max_fullness_out", "direction": "output", "width": 32, "signed": False},
    ]
    source = source_dir / str(function["source_file"])
    lines = source.read_text(encoding="utf-8", errors="replace").splitlines()
    start = int(function.get("line", 1))
    end = int(function.get("end_line", start))
    body = "\n".join(lines[start - 1:end])
    parameters = function.get("parameters", []) or []
    fifo_parameter = next(
        item for item in function.get("pointer_parameters", [])
        if item.get("mode") == "WRITES_THROUGH"
        and "fifo_t *" in str(item.get("type"))
    )
    scalars = [item for item in parameters if not item.get("pointer")]
    field_reads = function.get("fields_read", []) or []
    field_writes = function.get("fields_write", []) or []
    data_field = next(
        item for item in field_writes
        if item.get("record") == "fifo_s"
        and "unsigned char *" in str(item.get("type"))
    )["name"]
    write_ptr_names = {
        str(item.get("name")) for item in field_reads
        if item.get("record") == "fifo_s" and item.get("context") == "array_index"
    }
    if len(write_ptr_names) != 1:
        raise RuntimeError("FIFO write pointer field could not be derived from array indexing")
    write_ptr_field = next(iter(write_ptr_names))
    scalar_write_names = {
        str(item.get("name")) for item in field_writes
        if item.get("record") == "fifo_s" and item.get("type") == "int"
    }
    remaining_fields = scalar_write_names - {write_ptr_field}
    read_counts = {
        field: sum(
            item.get("record") == "fifo_s" and item.get("name") == field
            for item in field_reads
        )
        for field in remaining_fields
    }
    max_candidates = [field for field, count in read_counts.items() if count == 1]
    if len(max_candidates) != 1 or len(remaining_fields) != 2:
        raise RuntimeError("FIFO fullness fields could not be derived from AST use counts")
    max_fullness_field = max_candidates[0]
    fullness_field = next(iter(remaining_fields - {max_fullness_field}))
    size_fields = {
        str(item.get("name")) for item in field_reads
        if item.get("record") == "fifo_s"
        and item.get("type") == "int"
        and str(item.get("name")) not in scalar_write_names
    }
    if len(size_fields) != 1:
        raise RuntimeError("FIFO size field could not be derived from read-only scalar state")
    size_field = next(iter(size_fields))
    return {
        "schema_version": 2,
        "contract_id": cid,
        "status": "PROVISIONAL_SIMULATION_ONLY",
        "origin": "tool_discovered_decoder_runtime_transition",
        "function": {
            "clang_usr": function.get("clang_usr"),
            "name": name,
            "source_file": function.get("source_file"),
            "source_span": {"start_line": start, "end_line": end},
            "source_body_sha256": hashlib.sha256(body.encode("utf-8")).hexdigest(),
            "parameters": parameters,
            "return_type": function.get("return_type"),
        },
        "interface": {"ports": ports},
        "semantics": {
            "kind": "fifo_write_transition",
            "max_bits": maximum,
            "window_bytes": window_bytes,
            "legal_domain": {
                "nbits": [0, maximum],
                "free_space_at_least_nbits": True,
                "fifo_size_positive_multiple_of_8": True,
            },
            "bindings": {
                "fifo_parameter": fifo_parameter["name"],
                "data_parameter": scalars[0]["name"],
                "nbits_parameter": scalars[1]["name"],
                "data_field": data_field,
                "fullness_field": fullness_field,
                "write_ptr_field": write_ptr_field,
                "size_field": size_field,
                "max_fullness_field": max_fullness_field,
                "data_port": "data",
                "nbits_port": "nbits",
                "byte_ports": byte_ports,
                "fullness_port": "fullness",
                "write_ptr_port": "write_ptr",
                "fifo_size_port": "fifo_size",
                "max_fullness_port": "max_fullness",
                "byte_output_ports": byte_output_ports,
                "fullness_output_port": "fullness_out",
                "write_ptr_output_port": "write_ptr_out",
                "max_fullness_output_port": "max_fullness_out",
            },
            "state_transition": (
                "write n payload bits into a bounded FIFO byte window, increment fullness, "
                "advance/wrap write_ptr, and update max_fullness"
            ),
        },
        "selection": {
            "basis": selected["selection_basis"],
            "decode_execution_count": selected.get("execution_count"),
            "literal_size_bound": selected["literal_size_bound"],
        },
        "obligations": [
            "full-frame Decode C_ONLY/SHADOW/RTL_RETURN comparison",
            "full-frame Encode C_ONLY/SHADOW/RTL_RETURN comparison",
            "human review of FIFO memory-window and scalar state outputs before promotion",
        ],
        "promotion": {
            "status": "BLOCKED_PENDING_HUMAN_CONTRACT_REVIEW",
            "simulation_may_proceed": True,
        },
    }


def build_scalar_record_next_state_contract(
    selected: dict[str, Any], function: dict[str, Any], source_dir: pathlib.Path
) -> dict[str, Any]:
    """Freeze a loop-free DSC config/state scalar next-state boundary."""
    name = str(function["name"])
    cid = safe_identifier(name) + "_decode_transition"
    source = source_dir / str(function["source_file"])
    lines = source.read_text(encoding="utf-8", errors="replace").splitlines()
    start = int(function.get("line", 1))
    end = int(function.get("end_line", start))
    body = "\n".join(lines[start - 1:end])
    parameters = function.get("parameters", []) or []
    pointers = function.get("pointer_parameters", []) or []
    config_parameter = next(
        item for item in pointers if "dsc_cfg_t *" in str(item.get("type"))
    )
    state_parameter = next(
        item for item in pointers if "dsc_state_t *" in str(item.get("type"))
    )
    scalar_inputs = [item for item in parameters if not item.get("pointer")]
    scalar_outputs = [
        item for item in pointers
        if str(item.get("type", "")).strip() == "int *"
    ]
    config_fields = sorted({
        str(item.get("name")) for item in function.get("fields_read", [])
        if item.get("record") == "dsc_cfg_t"
    })
    state_input_fields = sorted({
        str(item.get("name")) for item in function.get("fields_read", [])
        if item.get("record") == "dsc_state_t"
    })
    state_output_fields = sorted({
        str(item.get("name")) for item in function.get("fields_write", [])
        if item.get("record") == "dsc_state_t"
    })
    if not set(state_output_fields).issubset(state_input_fields):
        raise RuntimeError("scalar next-state outputs require their pre-state inputs")
    scalar_input_ports = {
        str(item["name"]): safe_identifier(str(item["name"]))
        for item in scalar_inputs
    }
    config_ports = {field: f"cfg_{safe_identifier(field)}" for field in config_fields}
    state_input_ports = {
        field: f"state_{safe_identifier(field)}" for field in state_input_fields
    }
    scalar_output_ports = {
        str(item["name"]): f"{safe_identifier(str(item['name']))}_out"
        for item in scalar_outputs
    }
    state_output_ports = {
        field: f"state_{safe_identifier(field)}_out"
        for field in state_output_fields
    }
    input_names = [
        *scalar_input_ports.values(),
        *config_ports.values(),
        *state_input_ports.values(),
    ]
    output_names = [
        *scalar_output_ports.values(),
        *state_output_ports.values(),
    ]
    ports = [
        *[
            {"name": port, "direction": "input", "width": 32, "signed": True}
            for port in input_names
        ],
        *[
            {"name": port, "direction": "output", "width": 32, "signed": True}
            for port in output_names
        ],
    ]
    return {
        "schema_version": 2,
        "contract_id": cid,
        "status": "PROVISIONAL_SIMULATION_ONLY",
        "origin": "tool_discovered_decoder_runtime_transition",
        "function": {
            "clang_usr": function.get("clang_usr"),
            "name": name,
            "source_file": function.get("source_file"),
            "source_span": {"start_line": start, "end_line": end},
            "source_body_sha256": hashlib.sha256(body.encode("utf-8")).hexdigest(),
            "parameters": parameters,
            "return_type": function.get("return_type"),
        },
        "interface": {"ports": ports},
        "semantics": {
            "kind": "scalar_record_next_state",
            "constants": {
                "offset_fractional_bits": integer_define(
                    source_dir, "OFFSET_FRACTIONAL_BITS"
                ),
                "rc_scale_binary_point": integer_define(
                    source_dir, "RC_SCALE_BINARY_POINT"
                ),
            },
            "bindings": {
                "config_parameter": config_parameter["name"],
                "state_parameter": state_parameter["name"],
                "vertical_position_parameter": scalar_inputs[0]["name"],
                "group_count_parameter": scalar_inputs[1]["name"],
                "scale_output_parameter": scalar_outputs[0]["name"],
                "bpg_offset_output_parameter": scalar_outputs[1]["name"],
                "scalar_input_ports": scalar_input_ports,
                "config_ports": config_ports,
                "state_input_ports": state_input_ports,
                "scalar_output_ports": scalar_output_ports,
                "state_output_ports": state_output_ports,
            },
            "state_transition": (
                "compute rate-control scale/BPG outputs and all explicitly written "
                "dsc_state scalar next-state fields"
            ),
        },
        "selection": {
            "basis": selected["selection_basis"],
            "decode_execution_count": selected.get("execution_count"),
            "shape_evidence": selected["literal_size_bound"],
        },
        "obligations": [
            "full-frame Decode C_ONLY/SHADOW/RTL_RETURN comparison",
            "full-frame Encode C_ONLY/SHADOW/RTL_RETURN comparison",
            "human review of signed arithmetic and scalar state outputs before promotion",
        ],
        "promotion": {
            "status": "BLOCKED_PENDING_HUMAN_CONTRACT_REVIEW",
            "simulation_may_proceed": True,
        },
    }


def build_scalar_record_memory_contract(
    selected: dict[str, Any], function: dict[str, Any], source_dir: pathlib.Path
) -> dict[str, Any]:
    """Freeze a scalar next-state boundary with one indexed memory write."""
    name = str(function["name"])
    cid = safe_identifier(name) + "_decode_transition"
    source = source_dir / str(function["source_file"])
    lines = source.read_text(encoding="utf-8", errors="replace").splitlines()
    start = int(function.get("line", 1))
    end = int(function.get("end_line", start))
    body = "\n".join(lines[start - 1:end])
    parameters = function.get("parameters", []) or []
    pointers = function.get("pointer_parameters", []) or []
    config_parameter = next(
        item for item in pointers if "dsc_cfg_t *" in str(item.get("type"))
    )
    state_parameter = next(
        item for item in pointers if "dsc_state_t *" in str(item.get("type"))
    )
    field_reads = function.get("fields_read", []) or []
    field_writes = function.get("fields_write", []) or []
    config_fields = sorted({
        str(item.get("name")) for item in field_reads
        if item.get("record") == "dsc_cfg_t" and item.get("type") == "int"
    })
    state_output_fields = sorted({
        str(item.get("name")) for item in field_writes
        if item.get("record") == "dsc_state_t" and item.get("type") == "int"
    })
    # Compound assignments and increments are reported as writes by the Clang
    # fact extractor.  Every scalar output is therefore also an explicit
    # pre-state input, in addition to fields observed in ordinary reads.
    state_input_fields = sorted({
        str(item.get("name")) for item in field_reads
        if item.get("record") == "dsc_state_t" and item.get("type") == "int"
    } | set(state_output_fields))
    memory_fields = sorted({
        str(item.get("name")) for item in field_writes
        if item.get("record") == "dsc_state_t"
        and str(item.get("type", "")).strip() == "int *"
    })
    required_config = {"bits_per_pixel", "chunk_size", "vbr_enable"}
    required_state_inputs = {
        "bitsClamped", "bpgFracAccum", "bufferFullness", "chunkCount",
        "chunkPixelTimes", "isEncoder", "numBitsChunk", "sliceWidth",
    }
    required_state_outputs = {
        "bitsClamped", "bpgFracAccum", "bufferFullness", "chunkCount",
        "chunkPixelTimes", "numBitsChunk",
    }
    if (
        set(config_fields) != required_config
        or set(state_input_fields) != required_state_inputs
        or set(state_output_fields) != required_state_outputs
        or len(memory_fields) != 1
    ):
        raise RuntimeError(
            "scalar record memory fields do not match the frozen chunk transition shape"
        )
    config_ports = {field: f"cfg_{safe_identifier(field)}" for field in config_fields}
    state_input_ports = {
        field: f"state_{safe_identifier(field)}" for field in state_input_fields
    }
    state_output_ports = {
        field: f"state_{safe_identifier(field)}_out"
        for field in state_output_fields
    }
    memory_write_ports = {
        "enable": "chunk_write_enable",
        "index": "chunk_write_index",
        "value": "chunk_write_value",
    }
    ports = [
        *[
            {"name": port, "direction": "input", "width": 32, "signed": True}
            for port in [*config_ports.values(), *state_input_ports.values()]
        ],
        *[
            {"name": port, "direction": "output", "width": 32, "signed": True}
            for port in state_output_ports.values()
        ],
        {
            "name": memory_write_ports["enable"],
            "direction": "output",
            "width": 1,
            "signed": False,
        },
        *[
            {
                "name": memory_write_ports[key],
                "direction": "output",
                "width": 32,
                "signed": True,
            }
            for key in ("index", "value")
        ],
    ]
    return {
        "schema_version": 2,
        "contract_id": cid,
        "status": "PROVISIONAL_SIMULATION_ONLY",
        "origin": "tool_discovered_decoder_runtime_transition",
        "function": {
            "clang_usr": function.get("clang_usr"),
            "name": name,
            "source_file": function.get("source_file"),
            "source_span": {"start_line": start, "end_line": end},
            "source_body_sha256": hashlib.sha256(body.encode("utf-8")).hexdigest(),
            "parameters": parameters,
            "return_type": function.get("return_type"),
        },
        "interface": {"ports": ports},
        "semantics": {
            "kind": "scalar_record_memory_transition",
            "bindings": {
                "config_parameter": config_parameter["name"],
                "state_parameter": state_parameter["name"],
                "config_ports": config_ports,
                "state_input_ports": state_input_ports,
                "state_output_ports": state_output_ports,
                "memory_field": memory_fields[0],
                "memory_write_ports": memory_write_ports,
            },
            "legal_domain": {
                "slice_width_positive": True,
                "chunk_write_index_valid_when_enabled": True,
                "chunk_sizes_storage_required_when_enabled": True,
                "integer_width": 32,
            },
            "state_transition": (
                "remove one pixel allocation from encoder buffer state and emit one "
                "optional indexed chunk-size write as explicit sideband state"
            ),
        },
        "selection": {
            "basis": selected["selection_basis"],
            "decode_execution_count": selected.get("execution_count"),
            "shape_evidence": selected["literal_size_bound"],
        },
        "obligations": [
            "full-frame Decode C_ONLY/SHADOW/RTL_RETURN comparison",
            "full-frame Encode C_ONLY/SHADOW/RTL_RETURN comparison",
            "human review of signed arithmetic, scalar state, and indexed write before promotion",
        ],
        "promotion": {
            "status": "BLOCKED_PENDING_HUMAN_CONTRACT_REVIEW",
            "simulation_may_proceed": True,
        },
    }


def build_bounded_mux_refill_contract(
    selected: dict[str, Any], function: dict[str, Any], source_dir: pathlib.Path
) -> dict[str, Any]:
    """Freeze bounded bitstream-to-multi-FIFO refill state and byte writes."""
    name = str(function["name"])
    cid = safe_identifier(name) + "_decode_transition"
    source = source_dir / str(function["source_file"])
    lines = source.read_text(encoding="utf-8", errors="replace").splitlines()
    start = int(function.get("line", 1))
    end = int(function.get("end_line", start))
    body = "\n".join(lines[start - 1:end])
    parameters = function.get("parameters", []) or []
    pointers = function.get("pointer_parameters", []) or []
    config_parameter = next(
        item for item in pointers if "dsc_cfg_t *" in str(item.get("type"))
    )
    state_parameter = next(
        item for item in pointers if "dsc_state_t *" in str(item.get("type"))
    )
    buffer_parameter = next(
        item for item in pointers
        if "unsigned char *" in str(item.get("type"))
        and "**" not in str(item.get("type"))
    )
    config_fields = {
        str(item.get("name")) for item in function.get("fields_read", [])
        if item.get("record") == "dsc_cfg_t"
    }
    state_fields = {
        str(item.get("name")) for item in function.get("fields_read", [])
        if item.get("record") == "dsc_state_t"
    }
    if config_fields != {"mux_word_size"} or state_fields != {
        "maxSeSize", "numSsps", "postMuxNumBits", "shifter"
    }:
        raise RuntimeError("bounded mux refill fields do not match the frozen shape")
    max_ssps = integer_define(source_dir, "MAX_NUM_SSPS")
    mux_word_values = integer_field_assignment_values(
        source_dir, "mux_word_size", multiple_of=8
    )
    # Ignore unrelated condition literals collected from ternary expressions;
    # DSC mux words are explicitly assigned as 48 or 64 bits in the model.
    mux_word_values = [value for value in mux_word_values if 32 <= value <= 64]
    if max_ssps != 4 or mux_word_values != [48, 64]:
        raise RuntimeError(
            "bounded mux refill requires derived MAX_NUM_SSPS=4 and mux words 48/64"
        )
    max_mux_bytes = max(mux_word_values) // 8
    stream_window_bytes = max_ssps * max_mux_bytes + 1
    bpc_literals = integer_field_assignment_values(source_dir, "bits_per_component")
    max_bits_per_component = max(value for value in bpc_literals if value <= 16)
    max_se_bits = 4 * max_bits_per_component + 4
    max_fifo_bytes = (max(mux_word_values) + max_se_bits + 7) // 8
    if max_bits_per_component != 16 or max_fifo_bytes != 17:
        raise RuntimeError("bounded mux refill could not derive the 17-byte FIFO ceiling")
    max_se_size_ports = [f"max_se_size_{lane}" for lane in range(max_ssps)]
    stream_byte_ports = [
        f"stream_byte_{index}" for index in range(stream_window_bytes)
    ]
    fifo_lanes = []
    for lane in range(max_ssps):
        fifo_lanes.append({
            "data_input_ports": [
                f"fifo_{lane}_byte_{index}"
                for index in range(max_fifo_bytes)
            ],
            "data_output_ports": [
                f"fifo_{lane}_byte_{index}_out"
                for index in range(max_fifo_bytes)
            ],
            "size_port": f"fifo_{lane}_size",
            "fullness_port": f"fifo_{lane}_fullness",
            "read_ptr_port": f"fifo_{lane}_read_ptr",
            "write_ptr_port": f"fifo_{lane}_write_ptr",
            "max_fullness_port": f"fifo_{lane}_max_fullness",
            "byte_ctr_port": f"fifo_{lane}_byte_ctr",
            "size_output_port": f"fifo_{lane}_size_out",
            "fullness_output_port": f"fifo_{lane}_fullness_out",
            "read_ptr_output_port": f"fifo_{lane}_read_ptr_out",
            "write_ptr_output_port": f"fifo_{lane}_write_ptr_out",
            "max_fullness_output_port": f"fifo_{lane}_max_fullness_out",
            "byte_ctr_output_port": f"fifo_{lane}_byte_ctr_out",
        })
    ports = [
        {"name": "mux_word_size", "direction": "input", "width": 7, "signed": False},
        {"name": "num_ssps", "direction": "input", "width": 3, "signed": False},
        {"name": "post_mux_num_bits", "direction": "input", "width": 32, "signed": False},
        *[
            {"name": port, "direction": "input", "width": 7, "signed": False}
            for port in max_se_size_ports
        ],
        *[
            {"name": port, "direction": "input", "width": 8, "signed": False}
            for port in stream_byte_ports
        ],
        *[
            {
                "name": lane[key], "direction": "input", "width": 32,
                "signed": False,
            }
            for lane in fifo_lanes
            for key in (
                "size_port", "fullness_port", "read_ptr_port",
                "write_ptr_port", "max_fullness_port", "byte_ctr_port",
            )
        ],
        *[
            {"name": port, "direction": "input", "width": 8, "signed": False}
            for lane in fifo_lanes for port in lane["data_input_ports"]
        ],
        {"name": "domain_valid", "direction": "output", "width": 1, "signed": False},
        {
            "name": "post_mux_num_bits_out", "direction": "output",
            "width": 32, "signed": False,
        },
        *[
            {"name": port, "direction": "output", "width": 8, "signed": False}
            for lane in fifo_lanes for port in lane["data_output_ports"]
        ],
        *[
            {"name": lane[key], "direction": "output", "width": 32, "signed": False}
            for lane in fifo_lanes
            for key in (
                "size_output_port", "fullness_output_port",
                "read_ptr_output_port", "write_ptr_output_port",
                "max_fullness_output_port", "byte_ctr_output_port",
            )
        ],
    ]
    return {
        "schema_version": 2,
        "contract_id": cid,
        "status": "PROVISIONAL_SIMULATION_ONLY",
        "origin": "tool_discovered_decoder_runtime_transition",
        "function": {
            "clang_usr": function.get("clang_usr"),
            "name": name,
            "source_file": function.get("source_file"),
            "source_span": {"start_line": start, "end_line": end},
            "source_body_sha256": hashlib.sha256(body.encode("utf-8")).hexdigest(),
            "parameters": parameters,
            "return_type": function.get("return_type"),
        },
        "interface": {"ports": ports},
        "semantics": {
            "kind": "bounded_mux_refill_transition",
            "constants": {
                "max_ssps": max_ssps,
                "mux_word_values": mux_word_values,
                "max_mux_bytes": max_mux_bytes,
                "stream_window_bytes": stream_window_bytes,
                "max_bits_per_component": max_bits_per_component,
                "max_fifo_bytes": max_fifo_bytes,
            },
            "bindings": {
                "config_parameter": config_parameter["name"],
                "state_parameter": state_parameter["name"],
                "buffer_parameter": buffer_parameter["name"],
                "mux_word_size_field": "mux_word_size",
                "num_ssps_field": "numSsps",
                "post_mux_num_bits_field": "postMuxNumBits",
                "max_se_size_field": "maxSeSize",
                "shifter_field": "shifter",
                "mux_word_size_port": "mux_word_size",
                "num_ssps_port": "num_ssps",
                "post_mux_num_bits_port": "post_mux_num_bits",
                "post_mux_num_bits_output_port": "post_mux_num_bits_out",
                "max_se_size_ports": max_se_size_ports,
                "stream_byte_ports": stream_byte_ports,
                "fifo_lanes": fifo_lanes,
            },
            "legal_domain": {
                "mux_word_size": mux_word_values,
                "num_ssps": [0, max_ssps],
                "fifo_write_pointer_may_be_unaligned": True,
                "fifo_size_positive_multiple_of_8": True,
                "fifo_size_bytes_at_most": max_fifo_bytes,
                "fifo_free_space_at_least_mux_word": True,
                "input_window_bytes": stream_window_bytes,
            },
            "state_transition": (
                "for each active underfilled SSP, consume one mux word from the "
                "explicit bitstream cursor and append its bytes to that lane FIFO"
            ),
        },
        "selection": {
            "basis": selected["selection_basis"],
            "decode_execution_count": selected.get("execution_count"),
            "shape_evidence": selected["literal_size_bound"],
            "callee_names": sorted(
                str(item.get("name")) for item in function.get("callees", [])
            ),
        },
        "obligations": [
            "full-frame Decode C_ONLY/SHADOW/RTL_RETURN comparison",
            "full-frame Encode C_ONLY/SHADOW/RTL_RETURN comparison",
            "human review of bounded SSP count, bitstream window, and FIFO writes before promotion",
        ],
        "promotion": {
            "status": "BLOCKED_PENDING_HUMAN_CONTRACT_REVIEW",
            "simulation_may_proceed": True,
        },
    }


def build_bounded_flatness_state_contract(
    selected: dict[str, Any], function: dict[str, Any], source_dir: pathlib.Path
) -> dict[str, Any]:
    """Freeze flatness next state while composing accepted pure RTL callees."""
    name = str(function["name"])
    cid = safe_identifier(name) + "_decode_transition"
    source = source_dir / str(function["source_file"])
    lines = source.read_text(encoding="utf-8", errors="replace").splitlines()
    start = int(function.get("line", 1))
    end = int(function.get("end_line", start))
    body = "\n".join(lines[start - 1:end])
    parameters = function.get("parameters", []) or []
    pointers = function.get("pointer_parameters", []) or []
    config_parameter = next(
        item for item in pointers if "dsc_cfg_t *" in str(item.get("type"))
    )
    state_parameter = next(
        item for item in pointers if "dsc_state_t *" in str(item.get("type"))
    )
    scalar_parameters = [item for item in parameters if not item.get("pointer")]
    if len(scalar_parameters) != 3:
        raise RuntimeError("flatness state transition requires three scalar ABI inputs")
    config_fields = {
        str(item.get("name")) for item in function.get("fields_read", [])
        if item.get("record") == "dsc_cfg_t"
    }
    state_input_fields = {
        str(item.get("name")) for item in function.get("fields_read", [])
        if item.get("record") == "dsc_state_t" and item.get("type") == "int"
    }
    state_output_fields = {
        str(item.get("name")) for item in function.get("fields_write", [])
        if item.get("record") == "dsc_state_t" and item.get("type") == "int"
    }
    required_config = {
        "dsc_version_minor", "rc_range_parameters", "somewhat_flat_qp_delta",
        "somewhat_flat_qp_thresh", "very_flat_qp",
    }
    required_state_inputs = {
        "firstFlat", "flatnessType", "groupCount", "isEncoder",
        "origIsFlat", "pixelsInGroup", "prevFirstFlat",
        "prevFlatnessType", "prevIsFlat", "prevQp", "primaryQp",
        "sliceWidth", "stQp",
    }
    required_state_outputs = {
        "firstFlat", "flatnessType", "origIsFlat", "prevFirstFlat",
        "prevFlatnessType", "prevIsFlat", "prevQp", "stQp",
    }
    if (
        config_fields != required_config
        or state_input_fields != required_state_inputs
        or state_output_fields != required_state_outputs
    ):
        raise RuntimeError("flatness state fields do not match the frozen shape")

    repo_root = pathlib.Path(__file__).resolve().parent.parent
    library_root = repo_root / "library"
    manifest = read_json(library_root / "manifest.json")
    callee_names = {str(item.get("name")) for item in function.get("callees", [])}
    dependencies = []
    for entry in manifest.get("components", []):
        if entry.get("status") != "PASS" or entry.get("function") not in callee_names:
            continue
        module_path = library_root / str(entry["module_file"])
        contract_path = library_root / str(entry["contract_file"])
        dependency_contract = read_json(contract_path)
        dependency_ports = {
            str(port.get("name"))
            for port in (dependency_contract.get("interface", {}) or {}).get("ports", [])
        }
        if {"qp", "flatness_min_qp", "flatness_max_qp", "return_value"} == dependency_ports:
            role = "flatness_interval"
        elif {"orig_0_0", "orig_3_6", "return_value"}.issubset(dependency_ports):
            role = "original_window"
        else:
            raise RuntimeError("accepted flatness callee interface is not recognized")
        dependencies.append({
            "role": role,
            "function": entry["function"],
            "contract_id": entry["contract_id"],
            "module": entry["module"],
            "module_file": entry["module_file"],
            "module_sha256": file_hash(module_path),
            "contract_file": entry["contract_file"],
            "contract_sha256": file_hash(contract_path),
        })
    if {item["function"] for item in dependencies} != callee_names or {
        item["role"] for item in dependencies
    } != {"flatness_interval", "original_window"}:
        raise RuntimeError("flatness transition requires both accepted pure RTL callees")

    groups = integer_define(source_dir, "GROUPS_PER_SUPERGROUP")
    ranges = integer_define(source_dir, "NUM_BUF_RANGES")
    components = integer_define(source_dir, "NUM_COMPONENTS")
    padding_left = integer_define(source_dir, "PADDING_LEFT")
    if (groups, ranges, components, padding_left) != (4, 15, 4, 5):
        raise RuntimeError("flatness transition source constants do not match DSC shape")
    calls = groups
    taps_per_component = 7
    scalar_input_ports = {
        str(item["name"]): safe_identifier(str(item["name"]))
        for item in scalar_parameters
    }
    direct_config_fields = sorted(required_config - {"rc_range_parameters"})
    transitive_config_fields = [
        "bits_per_component", "flatness_det_thresh", "flatness_max_qp",
        "flatness_min_qp", "native_420",
    ]
    config_ports = {
        field: f"cfg_{safe_identifier(field)}"
        for field in [*direct_config_fields, *transitive_config_fields]
    }
    config_ports["last_range_max_qp"] = "cfg_last_range_max_qp"
    state_ports = {
        field: f"state_{safe_identifier(field)}"
        for field in sorted(required_state_inputs)
    }
    state_ports.update({
        "numComponents": "state_numcomponents",
        "cpntBitDepth[0]": "state_cpntbitdepth_0",
        "cpntBitDepth[1]": "state_cpntbitdepth_1",
    })
    state_output_ports = {
        field: f"state_{safe_identifier(field)}_out"
        for field in sorted(required_state_outputs)
    }
    tap_ports = [
        f"orig_call_{call}_c{component}_{tap}"
        for call in range(calls)
        for component in range(components)
        for tap in range(taps_per_component)
    ]
    ports = [
        *[
            {"name": port, "direction": "input", "width": 32, "signed": True}
            for port in [
                *scalar_input_ports.values(), *config_ports.values(),
                *state_ports.values(),
            ]
        ],
        *[
            {"name": port, "direction": "input", "width": 16, "signed": False}
            for port in tap_ports
        ],
        *[
            {"name": port, "direction": "output", "width": 32, "signed": True}
            for port in state_output_ports.values()
        ],
    ]
    return {
        "schema_version": 2,
        "contract_id": cid,
        "status": "PROVISIONAL_SIMULATION_ONLY",
        "origin": "tool_discovered_decoder_runtime_transition",
        "function": {
            "clang_usr": function.get("clang_usr"),
            "name": name,
            "source_file": function.get("source_file"),
            "source_span": {"start_line": start, "end_line": end},
            "source_body_sha256": hashlib.sha256(body.encode("utf-8")).hexdigest(),
            "parameters": parameters,
            "return_type": function.get("return_type"),
        },
        "interface": {"ports": ports},
        "dependencies": dependencies,
        "semantics": {
            "kind": "bounded_flatness_state_transition",
            "constants": {
                "groups_per_supergroup": groups,
                "num_buffer_ranges": ranges,
                "last_range_index": ranges - 1,
                "component_count": components,
                "padding_left": padding_left,
                "callee_calls": calls,
                "taps_per_component": taps_per_component,
            },
            "bindings": {
                "config_parameter": config_parameter["name"],
                "state_parameter": state_parameter["name"],
                "horizontal_position_parameter": scalar_parameters[0]["name"],
                "qp_parameter": scalar_parameters[1]["name"],
                "ignored_parameter": scalar_parameters[2]["name"],
                "scalar_input_ports": scalar_input_ports,
                "config_ports": config_ports,
                "state_input_ports": state_ports,
                "state_output_ports": state_output_ports,
                "tap_ports": tap_ports,
            },
            "legal_domain": {
                "group_count_nonnegative": True,
                "pixels_in_group": 3,
                "num_components": [3, 4],
                "first_flat_sentinel": [-1, 3],
                "dsc_version_minor": [1, 2],
            },
            "state_transition": (
                "compose accepted flatness predicate/window RTL with a fixed four-stage "
                "priority recurrence and explicit scalar next-state outputs"
            ),
        },
        "selection": {
            "basis": selected["selection_basis"],
            "decode_execution_count": selected.get("execution_count"),
            "shape_evidence": selected["literal_size_bound"],
        },
        "obligations": [
            "full-frame Decode C_ONLY/SHADOW/RTL_RETURN comparison",
            "full-frame Encode C_ONLY/SHADOW/RTL_RETURN comparison",
            "human review of unrolled priority loop, tap addressing, and scalar next state before promotion",
        ],
        "promotion": {
            "status": "BLOCKED_PENDING_HUMAN_CONTRACT_REVIEW",
            "simulation_may_proceed": True,
        },
    }


def build_bounded_history_update_contract(
    selected: dict[str, Any], function: dict[str, Any], source_dir: pathlib.Path
) -> dict[str, Any]:
    """Freeze the complete bounded ICH memory image around one update."""
    name = str(function["name"])
    cid = safe_identifier(name) + "_decode_transition"
    source = source_dir / str(function["source_file"])
    lines = source.read_text(encoding="utf-8", errors="replace").splitlines()
    start = int(function.get("line", 1))
    end = int(function.get("end_line", start))
    body = "\n".join(lines[start - 1:end])
    parameters = function.get("parameters", []) or []
    pointers = function.get("pointer_parameters", []) or []
    config_parameter = next(
        item for item in pointers if "dsc_cfg_t *" in str(item.get("type"))
    )
    state_parameter = next(
        item for item in pointers if "dsc_state_t *" in str(item.get("type"))
    )
    recon_parameter = next(
        item for item in pointers if "unsigned int *" in str(item.get("type"))
    )
    config_fields = {
        (str(item.get("name")), str(item.get("type")))
        for item in function.get("fields_read", [])
        if item.get("record") == "dsc_cfg_t"
    }
    state_fields = {
        (str(item.get("name")), str(item.get("type")))
        for item in function.get("fields_read", [])
        if item.get("record") == "dsc_state_t"
    }
    history_fields = {
        (str(item.get("name")), str(item.get("type")))
        for item in function.get("fields_read", [])
        if item.get("record") == "dsc_history_t"
    }
    if (
        config_fields != {("native_420", "int")}
        or state_fields != {
            ("hPos", "int"), ("history", "dsc_history_t"),
            ("ichSelected", "int"), ("isEncoder", "int"),
            ("numComponents", "int"), ("prevIchSelected", "int"),
            ("vPos", "int"),
        }
        or history_fields != {
            ("pixels", "unsigned int *[4]"), ("valid", "int *")
        }
    ):
        raise RuntimeError("bounded history update fields do not match the frozen shape")

    ich_bits = integer_define(source_dir, "ICH_BITS")
    pixels_above = integer_define(source_dir, "ICH_PIXELS_ABOVE")
    components = integer_define(source_dir, "NUM_COMPONENTS")
    entries = 1 << ich_bits
    reserved_nonfirst = entries - pixels_above
    if (ich_bits, pixels_above, components, entries, reserved_nonfirst) != (
        5, 7, 4, 32, 25
    ):
        raise RuntimeError("bounded history update constants do not match DSC shape")

    evidence = selected.get("literal_size_bound", {}) or {}
    dependency_contract_path = pathlib.Path(str(evidence.get("callee_contract_file", "")))
    dependency_candidate_path = pathlib.Path(str(evidence.get("callee_candidate_file", "")))
    if not dependency_contract_path.is_file() or not dependency_candidate_path.is_file():
        raise RuntimeError("bounded history update requires its verified lookup dependency")
    if (
        file_hash(dependency_contract_path)
        != str(evidence.get("callee_contract_sha256", ""))
        or file_hash(dependency_candidate_path)
        != str(evidence.get("callee_candidate_sha256", ""))
    ):
        raise RuntimeError("bounded history lookup dependency changed after frontier discovery")
    dependency_contract = read_json(dependency_contract_path)
    dependency_id = str(evidence.get("callee_contract_id", ""))
    if (
        dependency_contract.get("contract_id") != dependency_id
        or (dependency_contract.get("semantics", {}) or {}).get("kind")
        != "sampled_lookup_transition"
    ):
        raise RuntimeError("bounded history dependency contract is not the sampled lookup leaf")
    repo_root = pathlib.Path(__file__).resolve().parent.parent

    def repo_path(path: pathlib.Path) -> str:
        try:
            return str(path.resolve().relative_to(repo_root.resolve()))
        except ValueError:
            return str(path.resolve())

    dependency = {
        "role": "history_lookup_branch_guard",
        "function": str((dependency_contract.get("function", {}) or {}).get("name")),
        "contract_id": dependency_id,
        "module": safe_identifier(dependency_id),
        "contract_file": repo_path(dependency_contract_path),
        "contract_sha256": file_hash(dependency_contract_path),
        "module_file": repo_path(dependency_candidate_path),
        "module_sha256": file_hash(dependency_candidate_path),
    }

    scalar_ports = {
        "cfg_native_420": "cfg_native_420",
        "hPos": "state_hpos",
        "vPos": "state_vpos",
        "numComponents": "state_num_components",
        "isEncoder": "state_is_encoder",
        "ichSelected": "state_ich_selected",
        "prevIchSelected": "state_prev_ich_selected",
    }
    recon_ports = [f"recon_{component}" for component in range(components)]
    valid_input_ports = [f"history_valid_{entry}" for entry in range(entries)]
    pixel_input_ports = [
        [f"history_pixel_{component}_{entry}" for entry in range(entries)]
        for component in range(components)
    ]
    valid_output_ports = [
        f"history_valid_{entry}_out" for entry in range(entries)
    ]
    pixel_output_ports = [
        [f"history_pixel_{component}_{entry}_out" for entry in range(entries)]
        for component in range(components)
    ]
    ports = [
        *[
            {"name": port, "direction": "input", "width": 32, "signed": True}
            for port in scalar_ports.values()
        ],
        *[
            {"name": port, "direction": "input", "width": 32, "signed": False}
            for port in recon_ports
        ],
        *[
            {"name": port, "direction": "input", "width": 32, "signed": True}
            for port in valid_input_ports
        ],
        *[
            {"name": port, "direction": "input", "width": 32, "signed": False}
            for row in pixel_input_ports for port in row
        ],
        *[
            {"name": port, "direction": "output", "width": 32, "signed": True}
            for port in valid_output_ports
        ],
        *[
            {"name": port, "direction": "output", "width": 32, "signed": False}
            for row in pixel_output_ports for port in row
        ],
    ]
    return {
        "schema_version": 2,
        "contract_id": cid,
        "status": "PROVISIONAL_SIMULATION_ONLY",
        "origin": "tool_discovered_decoder_runtime_transition",
        "function": {
            "clang_usr": function.get("clang_usr"),
            "name": name,
            "source_file": function.get("source_file"),
            "source_span": {"start_line": start, "end_line": end},
            "source_body_sha256": hashlib.sha256(body.encode("utf-8")).hexdigest(),
            "parameters": parameters,
            "return_type": function.get("return_type"),
        },
        "interface": {"ports": ports},
        "dependencies": [dependency],
        "semantics": {
            "kind": "bounded_history_update_transition",
            "constants": {
                "ich_bits": ich_bits,
                "ich_entries": entries,
                "ich_pixels_above": pixels_above,
                "reserved_nonfirst": reserved_nonfirst,
                "component_count": components,
            },
            "bindings": {
                "config_parameter": config_parameter["name"],
                "state_parameter": state_parameter["name"],
                "recon_parameter": recon_parameter["name"],
                "native_420_field": "native_420",
                "history_field": "history",
                "history_pixels_field": "pixels",
                "history_valid_field": "valid",
                "scalar_ports": scalar_ports,
                "recon_ports": recon_ports,
                "valid_input_ports": valid_input_ports,
                "pixel_input_ports": pixel_input_ports,
                "valid_output_ports": valid_output_ports,
                "pixel_output_ports": pixel_output_ports,
            },
            "legal_domain": {
                "num_components": [3, components],
                "vpos_nonnegative": True,
                "history_valid_values": [0, 1],
                "history_storage_entries": entries,
                "first_line_reserved_entries": entries,
                "nonfirst_line_reserved_entries": reserved_nonfirst,
                "inactive_component_planes_tied_zero_and_not_dereferenced": True,
            },
            "state_transition": (
                "find the first empty or selected matching entry, shift active "
                "component histories toward LRU, insert recon at MRU, and emit "
                "the complete 4x32 pixel plus 32-valid-bit memory image"
            ),
            "composition_reduction": (
                "the verified lookup dependency can only select history memory: "
                "first-line updates set first_line_flag, while non-first-line "
                "search indices are strictly below ICH_SIZE-ICH_PIXELS_ABOVE"
            ),
        },
        "selection": {
            "basis": selected["selection_basis"],
            "decode_execution_count": selected.get("execution_count"),
            "shape_evidence": evidence,
        },
        "obligations": [
            "full-frame Decode C_ONLY/SHADOW/RTL_RETURN comparison",
            "full-frame Encode C_ONLY/SHADOW/RTL_RETURN comparison",
            "human review of lookup-branch reduction, location priority, and complete history image before promotion",
        ],
        "promotion": {
            "status": "BLOCKED_PENDING_HUMAN_CONTRACT_REVIEW",
            "simulation_may_proceed": True,
        },
    }


def build_bounded_history_caller_contract(
    selected: dict[str, Any], function: dict[str, Any], source_dir: pathlib.Path
) -> dict[str, Any]:
    """Freeze history clear, one reconstructed-line sample, and child update."""
    name = str(function["name"])
    cid = safe_identifier(name) + "_decode_transition"
    source = source_dir / str(function["source_file"])
    lines = source.read_text(encoding="utf-8", errors="replace").splitlines()
    start = int(function.get("line", 1))
    end = int(function.get("end_line", start))
    body = "\n".join(lines[start - 1:end])
    parameters = function.get("parameters", []) or []
    pointers = function.get("pointer_parameters", []) or []
    config_parameter = next(
        item for item in pointers if "dsc_cfg_t *" in str(item.get("type"))
    )
    state_parameter = next(
        item for item in pointers if "dsc_state_t *" in str(item.get("type"))
    )
    line_parameter = next(
        item for item in pointers if "int **" in str(item.get("type"))
    )
    scalar_parameters = [item for item in parameters if not item.get("pointer")]
    if len(scalar_parameters) != 2 or any(
        str(item.get("type")) != "int" for item in scalar_parameters
    ):
        raise RuntimeError("bounded history caller requires two scalar positions")
    config_fields = {
        (str(item.get("name")), str(item.get("type")))
        for item in function.get("fields_read", [])
        if item.get("record") == "dsc_cfg_t"
    }
    state_fields = {
        (str(item.get("name")), str(item.get("type")))
        for item in function.get("fields_read", [])
        if item.get("record") == "dsc_state_t"
    }
    if config_fields != {("pic_width", "int"), ("slice_width", "int")} or state_fields != {
        ("numComponents", "int"), ("pixelsInGroup", "int")
    }:
        raise RuntimeError("bounded history caller direct fields do not match frozen shape")

    ich_bits = integer_define(source_dir, "ICH_BITS")
    components = integer_define(source_dir, "NUM_COMPONENTS")
    padding_left = integer_define(source_dir, "PADDING_LEFT")
    entries = 1 << ich_bits
    if (ich_bits, components, padding_left, entries) != (5, 4, 5, 32):
        raise RuntimeError("bounded history caller constants do not match DSC shape")

    evidence = selected.get("literal_size_bound", {}) or {}
    dependency_contract_path = pathlib.Path(str(evidence.get("callee_contract_file", "")))
    dependency_candidate_path = pathlib.Path(str(evidence.get("callee_candidate_file", "")))
    if not dependency_contract_path.is_file() or not dependency_candidate_path.is_file():
        raise RuntimeError("bounded history caller requires verified child artifacts")
    if (
        file_hash(dependency_contract_path)
        != str(evidence.get("callee_contract_sha256", ""))
        or file_hash(dependency_candidate_path)
        != str(evidence.get("callee_candidate_sha256", ""))
    ):
        raise RuntimeError("bounded history child changed after frontier discovery")
    dependency_contract = read_json(dependency_contract_path)
    dependency_id = str(evidence.get("callee_contract_id", ""))
    if (
        dependency_contract.get("contract_id") != dependency_id
        or (dependency_contract.get("semantics", {}) or {}).get("kind")
        != "bounded_history_update_transition"
    ):
        raise RuntimeError("bounded history caller dependency has wrong semantics")
    repo_root = pathlib.Path(__file__).resolve().parent.parent

    def repo_path(path: pathlib.Path) -> str:
        try:
            return str(path.resolve().relative_to(repo_root.resolve()))
        except ValueError:
            return str(path.resolve())

    dependency = {
        "role": "history_update",
        "function": str((dependency_contract.get("function", {}) or {}).get("name")),
        "contract_id": dependency_id,
        "module": safe_identifier(dependency_id),
        "contract_file": repo_path(dependency_contract_path),
        "contract_sha256": file_hash(dependency_contract_path),
        "module_file": repo_path(dependency_candidate_path),
        "module_sha256": file_hash(dependency_candidate_path),
    }
    argument_ports = {
        str(item["name"]): safe_identifier(str(item["name"]))
        for item in scalar_parameters
    }
    config_ports = {
        "native_420": "cfg_native_420",
        "slice_width": "cfg_slice_width",
        "pic_width": "cfg_pic_width",
    }
    state_ports = {
        "hPos": "state_hpos",
        "vPos": "state_vpos",
        "numComponents": "state_num_components",
        "pixelsInGroup": "state_pixels_in_group",
        "isEncoder": "state_is_encoder",
        "ichSelected": "state_ich_selected",
        "prevIchSelected": "state_prev_ich_selected",
    }
    line_sample_ports = [
        f"line_sample_{component}" for component in range(components)
    ]
    valid_input_ports = [f"history_valid_{entry}" for entry in range(entries)]
    pixel_input_ports = [
        [f"history_pixel_{component}_{entry}" for entry in range(entries)]
        for component in range(components)
    ]
    valid_output_ports = [f"history_valid_{entry}_out" for entry in range(entries)]
    pixel_output_ports = [
        [f"history_pixel_{component}_{entry}_out" for entry in range(entries)]
        for component in range(components)
    ]
    ports = [
        *[
            {"name": port, "direction": "input", "width": 32, "signed": True}
            for port in [
                *argument_ports.values(), *config_ports.values(), *state_ports.values()
            ]
        ],
        *[
            {"name": port, "direction": "input", "width": 32, "signed": False}
            for port in line_sample_ports
        ],
        *[
            {"name": port, "direction": "input", "width": 32, "signed": True}
            for port in valid_input_ports
        ],
        *[
            {"name": port, "direction": "input", "width": 32, "signed": False}
            for row in pixel_input_ports for port in row
        ],
        *[
            {"name": port, "direction": "output", "width": 32, "signed": True}
            for port in valid_output_ports
        ],
        *[
            {"name": port, "direction": "output", "width": 32, "signed": False}
            for row in pixel_output_ports for port in row
        ],
    ]
    return {
        "schema_version": 2,
        "contract_id": cid,
        "status": "PROVISIONAL_SIMULATION_ONLY",
        "origin": "tool_discovered_decoder_runtime_transition",
        "function": {
            "clang_usr": function.get("clang_usr"),
            "name": name,
            "source_file": function.get("source_file"),
            "source_span": {"start_line": start, "end_line": end},
            "source_body_sha256": hashlib.sha256(body.encode("utf-8")).hexdigest(),
            "parameters": parameters,
            "return_type": function.get("return_type"),
        },
        "interface": {"ports": ports},
        "dependencies": [dependency],
        "semantics": {
            "kind": "bounded_history_caller_transition",
            "constants": {
                "ich_bits": ich_bits,
                "ich_entries": entries,
                "component_count": components,
                "padding_left": padding_left,
            },
            "bindings": {
                "config_parameter": config_parameter["name"],
                "state_parameter": state_parameter["name"],
                "line_parameter": line_parameter["name"],
                "horizontal_position_parameter": scalar_parameters[0]["name"],
                "vertical_position_parameter": scalar_parameters[1]["name"],
                "history_field": "history",
                "history_pixels_field": "pixels",
                "history_valid_field": "valid",
                "argument_ports": argument_ports,
                "config_ports": config_ports,
                "state_ports": state_ports,
                "line_sample_ports": line_sample_ports,
                "valid_input_ports": valid_input_ports,
                "pixel_input_ports": pixel_input_ports,
                "valid_output_ports": valid_output_ports,
                "pixel_output_ports": pixel_output_ports,
            },
            "legal_domain": {
                "num_components": [3, components],
                "pixels_in_group_positive": True,
                "line_sample_index": "hPos - pixelsInGroup + PADDING_LEFT",
                "line_samples_only_read_when_hPos_minus_pixelsInGroup_nonnegative": True,
                "inactive_component_planes_tied_zero_and_not_dereferenced": True,
                "history_storage_entries": entries,
            },
            "state_transition": (
                "clear history valid bits at a slice/line boundary, otherwise sample "
                "one reconstructed pixel and compose the verified complete-history update"
            ),
        },
        "selection": {
            "basis": selected["selection_basis"],
            "decode_execution_count": selected.get("execution_count"),
            "shape_evidence": evidence,
        },
        "obligations": [
            "full-frame Decode C_ONLY/SHADOW/RTL_RETURN comparison",
            "full-frame Encode C_ONLY/SHADOW/RTL_RETURN comparison",
            "human review of line sample address, clear priority, and child composition before promotion",
        ],
        "promotion": {
            "status": "BLOCKED_PENDING_HUMAN_CONTRACT_REVIEW",
            "simulation_may_proceed": True,
        },
    }


def build_bounded_vld_unit_contract(
    selected: dict[str, Any], function: dict[str, Any], source_dir: pathlib.Path
) -> dict[str, Any]:
    """Freeze one bounded decoder syntax unit and its selected FIFO state."""
    name = str(function["name"])
    cid = safe_identifier(name) + "_decode_transition"
    source = source_dir / str(function["source_file"])
    source_text = source.read_text(encoding="utf-8", errors="replace")
    lines = source_text.splitlines()
    start = int(function.get("line", 1))
    end = int(function.get("end_line", start))
    body = "\n".join(lines[start - 1:end])
    parameters = function.get("parameters", []) or []
    pointers = function.get("pointer_parameters", []) or []
    config_parameter = next(
        item for item in pointers if "dsc_cfg_t *" in str(item.get("type"))
    )
    state_parameter = next(
        item for item in pointers if "dsc_state_t *" in str(item.get("type"))
    )
    residual_parameter = next(
        item for item in pointers if str(item.get("type", "")).strip() == "int *"
    )
    byte_pointer_parameter = next(
        item for item in pointers if "unsigned char **" in str(item.get("type"))
    )
    scalar_parameters = [item for item in parameters if not item.get("pointer")]
    if len(scalar_parameters) != 1 or str(scalar_parameters[0].get("type")) != "int":
        raise RuntimeError("bounded VLD unit requires one scalar unit index")
    config_fields = {
        (str(item.get("name")), str(item.get("type")))
        for item in function.get("fields_read", [])
        if item.get("record") == "dsc_cfg_t"
    }
    state_fields = {
        (str(item.get("name")), str(item.get("type")))
        for item in function.get("fields_read", [])
        if item.get("record") == "dsc_state_t"
    }
    if config_fields != {
        ("bits_per_component", "int"), ("somewhat_flat_qp_thresh", "int")
    } or state_fields != {
        ("cpntBitDepth", "int[4]"), ("firstFlat", "int"),
        ("flatnessType", "int"), ("groupCount", "int"),
        ("ichIndexUnitMap", "int[6]"), ("ichIndicesInGroup", "int"),
        ("ichLookup", "int[6]"), ("ichSelected", "int"),
        ("prevFirstFlat", "int"), ("prevIchSelected", "int"),
        ("primaryQp", "int"), ("unitCType", "int[4]"),
        ("unitSspMap", "int[4]"), ("unitsPerGroup", "int"),
    }:
        raise RuntimeError("bounded VLD direct fields do not match frozen shape")
    debug_match = re.search(
        r"^[ \t]*#[ \t]*define[ \t]+PRINT_DEBUG_VLC[ \t]+([0-9]+)\b",
        source_text,
        re.MULTILINE,
    )
    if not debug_match or int(debug_match.group(1)) != 0:
        raise RuntimeError("bounded VLD requires compile-time disabled debug file I/O")

    units = integer_define(source_dir, "MAX_UNITS_PER_GROUP")
    samples = integer_define(source_dir, "SAMPLES_PER_UNIT")
    indices = integer_define(source_dir, "MAX_PIXELS_PER_GROUP")
    groups = integer_define(source_dir, "GROUPS_PER_SUPERGROUP")
    ich_bits = integer_define(source_dir, "ICH_BITS")
    fifo_bytes = 17
    max_prefix_bits = 17
    if (units, samples, indices, groups, ich_bits) != (4, 3, 6, 4, 5):
        raise RuntimeError("bounded VLD constants do not match DSC shape")

    repo_root = pathlib.Path(__file__).resolve().parent.parent
    library_root = repo_root / "library"
    manifest = read_json(library_root / "manifest.json")
    callee_names = {
        str(item.get("name")) for item in function.get("callees", [])
        if str(item.get("name")) != "fprintf"
    }
    dependencies = []
    role_signatures = (
        ("escape_size", {"qp", "dsc_version_minor", "native_420", "cpntBitDepth_0", "qlevel_luma", "return_value"}),
        ("residual_size", {"eq", "return_value"}),
        ("adjusted_prediction", {"unit", "dsc_version_minor", "native_420", "unit_c_type_selected", "predicted_size_selected", "primary_qp", "prev_primary_qp", "cpntBitDepth_0", "cpntBitDepth_1", "cpntBitDepth_2", "cpntBitDepth_3", "qlevel_luma_new", "qlevel_chroma_new", "qlevel_luma_old", "qlevel_chroma_old", "return_value"}),
        ("flatness_sent", {"qp", "flatness_min_qp", "flatness_max_qp", "return_value"}),
        ("qp_mapping", {"cpnt", "qp", "dsc_version_minor", "native_420", "cpntBitDepth_0", "cpntBitDepth_1", "qlevel_luma", "qlevel_chroma", "return_value"}),
        ("max_residual", {"cpnt", "qp", "dsc_version_minor", "native_420", "cpntBitDepth_0", "cpntBitDepth_1", "cpntBitDepth_selected", "qlevel_luma", "qlevel_chroma", "return_value"}),
        ("predict_size", {"req_size_0", "req_size_1", "req_size_2", "return_value"}),
    )
    for entry in manifest.get("components", []):
        if entry.get("status") != "PASS" or entry.get("function") not in callee_names:
            continue
        module_path = library_root / str(entry["module_file"])
        contract_path = library_root / str(entry["contract_file"])
        dependency_contract = read_json(contract_path)
        dependency_ports = {
            str(port.get("name"))
            for port in (dependency_contract.get("interface", {}) or {}).get("ports", [])
        }
        matching_roles = [
            role for role, signature in role_signatures
            if signature == dependency_ports
        ]
        if len(matching_roles) != 1:
            raise RuntimeError("accepted VLD callee interface is not uniquely recognized")
        dependencies.append({
            "role": matching_roles[0],
            "function": entry["function"],
            "contract_id": entry["contract_id"],
            "module": entry["module"],
            "module_file": str(pathlib.Path("library") / str(entry["module_file"])),
            "module_sha256": file_hash(module_path),
            "contract_file": str(pathlib.Path("library") / str(entry["contract_file"])),
            "contract_sha256": file_hash(contract_path),
        })
    stable_names = {str(item["function"]) for item in dependencies}
    evidence = selected.get("literal_size_bound", {}) or {}
    getbits_contract_path = pathlib.Path(str(evidence.get("callee_contract_file", "")))
    getbits_candidate_path = pathlib.Path(str(evidence.get("callee_candidate_file", "")))
    if not getbits_contract_path.is_file() or not getbits_candidate_path.is_file():
        raise RuntimeError("bounded VLD requires verified GetBits artifacts")
    if (
        file_hash(getbits_contract_path) != str(evidence.get("callee_contract_sha256", ""))
        or file_hash(getbits_candidate_path) != str(evidence.get("callee_candidate_sha256", ""))
    ):
        raise RuntimeError("bounded VLD GetBits dependency changed after discovery")
    getbits_contract = read_json(getbits_contract_path)
    if (
        getbits_contract.get("contract_id") != evidence.get("callee_contract_id")
        or (getbits_contract.get("semantics", {}) or {}).get("kind")
        != "fifo_read_accounting_transition"
    ):
        raise RuntimeError("bounded VLD GetBits dependency has wrong semantics")
    if stable_names | {str(evidence.get("callee"))} != callee_names:
        raise RuntimeError("bounded VLD dependencies do not cover every internal callee")

    def repo_path(path: pathlib.Path) -> str:
        try:
            return str(path.resolve().relative_to(repo_root.resolve()))
        except ValueError:
            return str(path.resolve())

    dependencies.append({
        "role": "get_bits",
        "function": str(evidence.get("callee")),
        "contract_id": str(evidence.get("callee_contract_id")),
        "module": safe_identifier(str(evidence.get("callee_contract_id"))),
        "contract_file": repo_path(getbits_contract_path),
        "contract_sha256": file_hash(getbits_contract_path),
        "module_file": repo_path(getbits_candidate_path),
        "module_sha256": file_hash(getbits_candidate_path),
    })
    dependencies.sort(key=lambda item: str(item["role"]))

    unit_parameter = str(scalar_parameters[0]["name"])
    config_ports = {
        field: f"cfg_{safe_identifier(field)}" for field in (
            "bits_per_component", "somewhat_flat_qp_thresh",
            "dsc_version_minor", "native_420", "flatness_min_qp",
            "flatness_max_qp",
        )
    }
    scalar_state_fields = (
        "firstFlat", "flatnessType", "groupCount", "ichIndicesInGroup",
        "ichSelected", "prevFirstFlat", "prevIchSelected", "primaryQp",
        "prevPrimaryQp", "unitsPerGroup", "numBits",
    )
    state_ports = {
        field: f"state_{safe_identifier(field)}" for field in scalar_state_fields
    }
    array_sizes = {
        "cpntBitDepth": units,
        "unitCType": units,
        "unitSspMap": units,
        "ichIndexUnitMap": indices,
        "ichLookup": indices,
        "predictedSize": units,
        "rcSizeUnit": units,
        "useMidpoint": units,
    }
    array_input_ports = {
        field: [f"state_{safe_identifier(field)}_{index}" for index in range(size)]
        for field, size in array_sizes.items()
    }
    scalar_output_fields = (
        "firstFlat", "flatnessType", "ichSelected", "prevFirstFlat",
        "prevIchSelected", "numBits",
    )
    state_output_ports = {
        field: f"state_{safe_identifier(field)}_out"
        for field in scalar_output_fields
    }
    array_output_fields = ("ichLookup", "predictedSize", "rcSizeUnit", "useMidpoint")
    array_output_ports = {
        field: [f"state_{safe_identifier(field)}_{index}_out" for index in range(array_sizes[field])]
        for field in array_output_fields
    }
    qlevel_ports = {
        "luma_primary": "qlevel_luma_primary",
        "chroma_primary": "qlevel_chroma_primary",
        "luma_previous": "qlevel_luma_previous",
        "chroma_previous": "qlevel_chroma_previous",
    }
    residual_input_ports = [f"quantized_residual_{index}" for index in range(samples)]
    residual_output_ports = [f"quantized_residual_{index}_out" for index in range(samples)]
    fifo_data_ports = [f"fifo_byte_{index}" for index in range(fifo_bytes)]
    fifo_ports = {
        "size": "fifo_size", "fullness": "fifo_fullness",
        "read_ptr": "fifo_read_ptr",
    }
    fifo_output_ports = {
        "lane": "fifo_lane_out", "fullness": "fifo_fullness_out",
        "read_ptr": "fifo_read_ptr_out",
    }
    ports = [
        {"name": safe_identifier(unit_parameter), "direction": "input", "width": 32, "signed": True},
        *[
            {"name": port, "direction": "input", "width": 32, "signed": True}
            for port in [*config_ports.values(), *state_ports.values()]
        ],
        *[
            {"name": port, "direction": "input", "width": 32, "signed": True}
            for row in array_input_ports.values() for port in row
        ],
        *[
            {"name": port, "direction": "input", "width": 32, "signed": True}
            for port in qlevel_ports.values()
        ],
        *[
            {"name": port, "direction": "input", "width": 32, "signed": True}
            for port in residual_input_ports
        ],
        *[
            {"name": port, "direction": "input", "width": 32, "signed": True}
            for port in fifo_ports.values()
        ],
        *[
            {"name": port, "direction": "input", "width": 8, "signed": False}
            for port in fifo_data_ports
        ],
        {"name": "domain_valid", "direction": "output", "width": 1, "signed": False},
        *[
            {"name": port, "direction": "output", "width": 32, "signed": True}
            for port in state_output_ports.values()
        ],
        *[
            {"name": port, "direction": "output", "width": 32, "signed": True}
            for row in array_output_ports.values() for port in row
        ],
        *[
            {"name": port, "direction": "output", "width": 32, "signed": True}
            for port in residual_output_ports
        ],
        *[
            {"name": port, "direction": "output", "width": 32, "signed": True}
            for port in fifo_output_ports.values()
        ],
    ]
    return {
        "schema_version": 2,
        "contract_id": cid,
        "status": "PROVISIONAL_SIMULATION_ONLY",
        "origin": "tool_discovered_decoder_runtime_transition",
        "function": {
            "clang_usr": function.get("clang_usr"), "name": name,
            "source_file": function.get("source_file"),
            "source_span": {"start_line": start, "end_line": end},
            "source_body_sha256": hashlib.sha256(body.encode("utf-8")).hexdigest(),
            "parameters": parameters, "return_type": function.get("return_type"),
        },
        "interface": {"ports": ports},
        "dependencies": dependencies,
        "semantics": {
            "kind": "bounded_vld_unit_transition",
            "constants": {
                "max_units": units, "samples_per_unit": samples,
                "max_ich_indices": indices, "groups_per_supergroup": groups,
                "ich_bits": ich_bits, "fifo_bytes": fifo_bytes,
                "max_prefix_bits": max_prefix_bits, "print_debug_vlc": 0,
            },
            "bindings": {
                "config_parameter": config_parameter["name"],
                "state_parameter": state_parameter["name"],
                "unit_parameter": unit_parameter,
                "residual_parameter": residual_parameter["name"],
                "byte_pointer_parameter": byte_pointer_parameter["name"],
                "unit_port": safe_identifier(unit_parameter),
                "config_ports": config_ports, "state_ports": state_ports,
                "array_input_ports": array_input_ports,
                "state_output_ports": state_output_ports,
                "array_output_ports": array_output_ports,
                "qlevel_ports": qlevel_ports,
                "residual_input_ports": residual_input_ports,
                "residual_output_ports": residual_output_ports,
                "fifo_ports": fifo_ports, "fifo_data_ports": fifo_data_ports,
                "fifo_output_ports": fifo_output_ports,
                "fifo_array_field": "shifter",
                "quant_table_luma_field": "quantTableLuma",
                "quant_table_chroma_field": "quantTableChroma",
            },
            "legal_domain": {
                "unit": [0, units - 1], "units_per_group": [3, units],
                "num_components": [3, units], "ich_indices": [0, indices],
                "bits_per_component": [8, 16], "primary_qp": [0, 31],
                "previous_qp": [0, 31], "fifo_size_bits_at_most": fifo_bytes * 8,
                "fifo_size_positive_multiple_of_8": True,
                "fifo_fullness_covers_every_requested_bit": True,
                "prefix_unroll_bound": max_prefix_bits,
                "byte_input_pointer_is_semantically_unused": True,
            },
            "state_transition": (
                "decode one syntax unit, consume the selected FIFO, and emit every "
                "written scalar/array plus the three residual outputs"
            ),
            "composition_reduction": (
                "accepted pure leaf RTL supplies mapping/size predicates; the hash-bound "
                "GetBits contract is inlined over a complete selected-FIFO image"
            ),
        },
        "selection": {
            "basis": selected["selection_basis"],
            "decode_execution_count": selected.get("execution_count"),
            "shape_evidence": evidence,
        },
        "obligations": [
            "full-frame Decode C_ONLY/SHADOW/RTL_RETURN comparison",
            "full-frame Encode C_ONLY/SHADOW/RTL_RETURN comparison",
            "human review of prefix bound, FIFO read recurrence, early returns, and complete outputs before promotion",
        ],
        "promotion": {
            "status": "BLOCKED_PENDING_HUMAN_CONTRACT_REVIEW",
            "simulation_may_proceed": True,
        },
    }


def build_bounded_vld_group_decode_contract(
    selected: dict[str, Any], function: dict[str, Any], source_dir: pathlib.Path
) -> dict[str, Any]:
    """Compose one decoder group from the verified mux-refill and VLD-unit RTL."""
    name = str(function["name"])
    cid = safe_identifier(name) + "_decode_transition"
    source = source_dir / str(function["source_file"])
    source_text = source.read_text(encoding="utf-8", errors="replace")
    lines = source_text.splitlines()
    start = int(function.get("line", 1))
    end = int(function.get("end_line", start))
    body = "\n".join(lines[start - 1:end])
    if not re.search(r"\bif\s*\(\s*1\s*\)", body):
        raise RuntimeError("bounded VLD group requires the frozen if(1) source path")

    parameters = function.get("parameters", []) or []
    pointers = function.get("pointer_parameters", []) or []
    config_parameter = next(
        item for item in pointers if "dsc_cfg_t *" in str(item.get("type"))
    )
    state_parameter = next(
        item for item in pointers if "dsc_state_t *" in str(item.get("type"))
    )
    byte_parameter = next(
        item for item in pointers if "unsigned char **" in str(item.get("type"))
    )
    if len(parameters) != 3 or len(pointers) != 3:
        raise RuntimeError("bounded VLD group native ABI changed")

    units = integer_define(source_dir, "MAX_UNITS_PER_GROUP")
    samples = integer_define(source_dir, "SAMPLES_PER_UNIT")
    indices = integer_define(source_dir, "MAX_PIXELS_PER_GROUP")
    groups = integer_define(source_dir, "GROUPS_PER_SUPERGROUP")
    fifo_bytes = 17
    stream_bytes = 33
    if (units, samples, indices, groups) != (4, 3, 6, 4):
        raise RuntimeError("bounded VLD group constants do not match DSC")

    repo_root = pathlib.Path(__file__).resolve().parent.parent

    def repo_path(path: pathlib.Path) -> str:
        try:
            return str(path.resolve().relative_to(repo_root.resolve()))
        except ValueError:
            return str(path.resolve())

    evidence = selected.get("literal_size_bound", {}) or {}
    evidence_dependencies = list(evidence.get("dependencies", []) or [])
    child_by_kind: dict[str, tuple[dict[str, Any], dict[str, Any]]] = {}
    dependencies = []
    expected_kinds = {
        "bounded_mux_refill_transition": "mux_refill",
        "bounded_vld_unit_transition": "vld_unit",
    }
    for item in evidence_dependencies:
        contract_path = pathlib.Path(str(item.get("contract_file", "")))
        candidate_path = pathlib.Path(str(item.get("candidate_file", "")))
        if not contract_path.is_file() or not candidate_path.is_file():
            raise RuntimeError("bounded VLD group dependency artifact is missing")
        if (
            file_hash(contract_path) != str(item.get("contract_sha256", ""))
            or file_hash(candidate_path) != str(item.get("candidate_sha256", ""))
        ):
            raise RuntimeError("bounded VLD group dependency changed after discovery")
        child_contract = read_json(contract_path)
        kind = str((child_contract.get("semantics", {}) or {}).get("kind", ""))
        if kind not in expected_kinds or kind in child_by_kind:
            raise RuntimeError("bounded VLD group child semantics are incomplete")
        if child_contract.get("contract_id") != item.get("contract_id"):
            raise RuntimeError("bounded VLD group child contract id changed")
        role = expected_kinds[kind]
        dependency = {
            "role": role,
            "function": item.get("function"),
            "contract_id": item.get("contract_id"),
            "semantics_kind": kind,
            "module": safe_identifier(str(item.get("contract_id"))),
            "contract_file": repo_path(contract_path),
            "contract_sha256": file_hash(contract_path),
            "module_file": repo_path(candidate_path),
            "module_sha256": file_hash(candidate_path),
        }
        dependencies.append(dependency)
        child_by_kind[kind] = (child_contract, dependency)
    if set(child_by_kind) != set(expected_kinds):
        raise RuntimeError("bounded VLD group requires mux-refill and VLD-unit children")
    dependencies.sort(key=lambda item: str(item["role"]))

    mux_contract = child_by_kind["bounded_mux_refill_transition"][0]
    vld_contract = child_by_kind["bounded_vld_unit_transition"][0]
    mux_semantics = mux_contract.get("semantics", {}) or {}
    vld_semantics = vld_contract.get("semantics", {}) or {}
    mux_bindings = mux_semantics.get("bindings", {}) or {}
    vld_bindings = vld_semantics.get("bindings", {}) or {}
    if (
        int((mux_semantics.get("constants", {}) or {}).get("max_ssps", 0)) != units
        or int((mux_semantics.get("constants", {}) or {}).get("max_fifo_bytes", 0))
        != fifo_bytes
        or int((mux_semantics.get("constants", {}) or {}).get("stream_window_bytes", 0))
        != stream_bytes
        or int((vld_semantics.get("constants", {}) or {}).get("max_units", 0)) != units
        or int((vld_semantics.get("constants", {}) or {}).get("samples_per_unit", 0))
        != samples
        or int((vld_semantics.get("constants", {}) or {}).get("max_ich_indices", 0))
        != indices
        or int((vld_semantics.get("constants", {}) or {}).get("fifo_bytes", 0))
        != fifo_bytes
    ):
        raise RuntimeError("bounded VLD group child constants changed")

    mux_ports = [dict(port) for port in mux_contract["interface"]["ports"]]
    vld_ports = [dict(port) for port in vld_contract["interface"]["ports"]]
    mux_inputs = [port for port in mux_ports if port.get("direction") == "input"]
    mux_outputs = [port for port in mux_ports if port.get("direction") == "output"]
    vld_inputs = [port for port in vld_ports if port.get("direction") == "input"]
    vld_outputs = [port for port in vld_ports if port.get("direction") == "output"]
    vld_excluded_inputs = {
        str(vld_bindings["unit_port"]),
        *[str(value) for value in vld_bindings["residual_input_ports"]],
        *[str(value) for value in vld_bindings["fifo_ports"].values()],
        *[str(value) for value in vld_bindings["fifo_data_ports"]],
    }
    vld_excluded_outputs = {
        "domain_valid",
        *[str(value) for value in vld_bindings["residual_output_ports"]],
        *[str(value) for value in vld_bindings["fifo_output_ports"].values()],
    }
    vld_parent_inputs = [
        port for port in vld_inputs if str(port.get("name")) not in vld_excluded_inputs
    ]
    vld_parent_outputs = [
        port for port in vld_outputs if str(port.get("name")) not in vld_excluded_outputs
    ]
    residual_inputs = [
        [f"state_quantizedresidual_{unit}_{sample}" for sample in range(samples)]
        for unit in range(units)
    ]
    residual_outputs = [
        [f"state_quantizedresidual_{unit}_{sample}_out" for sample in range(samples)]
        for unit in range(units)
    ]
    direct_inputs = {
        "rcb_bits": "cfg_rcb_bits",
        "bufferFullness": "state_bufferfullness",
        "errorOccurred": "state_erroroccurred",
        "groupCountLine": "state_groupcountline",
    }
    direct_outputs = {
        "prevPrimaryQp": "state_prevprimaryqp_out",
        "codedGroupSize": "state_codedgroupsize_out",
        "bufferFullness": "state_bufferfullness_out",
        "errorOccurred": "state_erroroccurred_out",
        "origIsFlat": "state_origisflat_out",
        "groupCountLine": "state_groupcountline_out",
    }
    ports = [
        *mux_inputs,
        *vld_parent_inputs,
        *[
            {"name": port, "direction": "input", "width": 32, "signed": True}
            for row in residual_inputs for port in row
        ],
        *[
            {"name": port, "direction": "input", "width": 32, "signed": True}
            for port in direct_inputs.values()
        ],
        {"name": "domain_valid", "direction": "output", "width": 1, "signed": False},
        *[port for port in mux_outputs if str(port.get("name")) != "domain_valid"],
        *vld_parent_outputs,
        *[
            {"name": port, "direction": "output", "width": 32, "signed": True}
            for row in residual_outputs for port in row
        ],
        *[
            {"name": port, "direction": "output", "width": 32, "signed": True}
            for port in direct_outputs.values()
        ],
    ]
    input_names = [str(port["name"]) for port in ports if port["direction"] == "input"]
    output_names = [str(port["name"]) for port in ports if port["direction"] == "output"]
    if len(input_names) != 205 or len(output_names) != 136:
        raise RuntimeError(
            f"bounded VLD group expected 205/136 ports, got {len(input_names)}/{len(output_names)}"
        )
    if len(set(input_names + output_names)) != len(input_names) + len(output_names):
        raise RuntimeError("bounded VLD group flattened port names collide")

    return {
        "schema_version": 2,
        "contract_id": cid,
        "status": "PROVISIONAL_SIMULATION_ONLY",
        "origin": "tool_discovered_decoder_runtime_transition",
        "function": {
            "clang_usr": function.get("clang_usr"), "name": name,
            "source_file": function.get("source_file"),
            "source_span": {"start_line": start, "end_line": end},
            "source_body_sha256": hashlib.sha256(body.encode("utf-8")).hexdigest(),
            "parameters": parameters, "return_type": function.get("return_type"),
        },
        "interface": {"ports": ports},
        "dependencies": dependencies,
        "semantics": {
            "kind": "bounded_vld_group_decode_transition",
            "constants": {
                "max_units": units, "samples_per_unit": samples,
                "max_ich_indices": indices, "groups_per_supergroup": groups,
                "max_ssps": units, "fifo_bytes": fifo_bytes,
                "stream_window_bytes": stream_bytes,
            },
            "bindings": {
                "config_parameter": config_parameter["name"],
                "state_parameter": state_parameter["name"],
                "byte_pointer_parameter": byte_parameter["name"],
                "mux": mux_bindings,
                "vld": vld_bindings,
                "vld_parent_input_ports": [str(port["name"]) for port in vld_parent_inputs],
                "vld_parent_output_ports": [str(port["name"]) for port in vld_parent_outputs],
                "residual_input_ports": residual_inputs,
                "residual_output_ports": residual_outputs,
                "direct_input_ports": direct_inputs,
                "direct_output_ports": direct_outputs,
                "quant_table_luma_field": "quantTableLuma",
                "quant_table_chroma_field": "quantTableChroma",
            },
            "legal_domain": {
                "units_per_group": [3, units], "num_ssps": [0, units],
                "unit_component_and_ssp_maps": [0, units - 1],
                "ich_indices": [0, indices], "mux_word_size": [48, 64],
                "bits_per_component": [8, 16], "qp": [0, 31],
                "fifo_size_bits_at_most": fifo_bytes * 8,
                "fifo_size_positive_multiple_of_8": True,
                "stream_window_bytes": stream_bytes,
                "active_source_branch": "if(1)",
                "byte_input_pointer_is_read_only": True,
            },
            "state_transition": (
                "execute ProcessGroupDec once, chain VLDUnit for each active unit, "
                "then apply the six VLDGroup tail writes"
            ),
            "composition_reduction": (
                "hash-bound provisional mux-refill and VLD-unit modules are composed "
                "strictly in C source order over complete FIFO and decoder state images"
            ),
        },
        "selection": {
            "basis": selected["selection_basis"],
            "decode_execution_count": selected.get("execution_count"),
            "shape_evidence": evidence,
        },
        "obligations": [
            "full-frame Decode C_ONLY/SHADOW/RTL_RETURN comparison",
            "full-frame Encode C_ONLY/SHADOW/RTL_RETURN non-reachability check",
            "human review of sequential child composition and complete state/FIFO outputs before promotion",
        ],
        "promotion": {
            "status": "BLOCKED_PENDING_HUMAN_CONTRACT_REVIEW",
            "simulation_may_proceed": True,
        },
    }


def build_raster_color_transform_contract(
    selected: dict[str, Any], function: dict[str, Any], source_dir: pathlib.Path
) -> dict[str, Any]:
    """Freeze one independently iterated RGB/YCoCg pixel transform."""
    name = str(function["name"])
    cid = safe_identifier(name) + "_pixel_transition"
    source = source_dir / str(function["source_file"])
    source_text = source.read_text(encoding="utf-8", errors="replace")
    lines = source_text.splitlines()
    start = int(function.get("line", 1))
    end = int(function.get("end_line", start))
    body = "\n".join(lines[start - 1:end])
    direction = str(
        (selected.get("literal_size_bound", {}) or {}).get("direction", "")
    )
    if direction not in {"rgb_to_ycocg", "ycocg_to_rgb"}:
        raise RuntimeError("raster color transform direction is not frozen")
    if not re.search(
        r"^[ \t]*#[ \t]*define[ \t]+REDUCE_CHROMA_16BPC\b",
        source_text,
        re.MULTILINE,
    ):
        raise RuntimeError("raster color transform requires REDUCE_CHROMA_16BPC")

    parameters = function.get("parameters", []) or []
    pointers = function.get("pointer_parameters", []) or []
    input_parameter = next(
        item for item in pointers
        if item.get("mode") == "READ_ONLY" and "pic_t *" in str(item.get("type"))
    )
    output_parameter = next(
        item for item in pointers
        if item.get("mode") == "WRITES_THROUGH" and "pic_t *" in str(item.get("type"))
    )
    config_parameter = next(
        item for item in pointers if "dsc_cfg_t *" in str(item.get("type"))
    )
    input_fields = ["r", "g", "b"] if direction == "rgb_to_ycocg" else ["y", "u", "v"]
    output_fields = ["y", "u", "v"] if direction == "rgb_to_ycocg" else ["r", "g", "b"]
    input_ports = [f"input_channel_{index}" for index in range(3)]
    output_ports = [f"output_channel_{index}" for index in range(3)]
    ports = [
        {"name": "bits", "direction": "input", "width": 32, "signed": True},
        *[
            {"name": port, "direction": "input", "width": 32, "signed": True}
            for port in input_ports
        ],
        {"name": "domain_valid", "direction": "output", "width": 1, "signed": False},
        *[
            {"name": port, "direction": "output", "width": 32, "signed": True}
            for port in output_ports
        ],
    ]
    return {
        "schema_version": 2,
        "contract_id": cid,
        "status": "PROVISIONAL_SIMULATION_ONLY",
        "origin": "tool_discovered_decoder_runtime_transition",
        "function": {
            "clang_usr": function.get("clang_usr"), "name": name,
            "source_file": function.get("source_file"),
            "source_span": {"start_line": start, "end_line": end},
            "source_body_sha256": hashlib.sha256(body.encode("utf-8")).hexdigest(),
            "parameters": parameters, "return_type": function.get("return_type"),
        },
        "interface": {"ports": ports},
        "dependencies": [],
        "semantics": {
            "kind": "raster_color_transform_transition",
            "constants": {
                "channel_count": 3,
                "minimum_bits": 8,
                "maximum_bits": 16,
                "reduce_chroma_16bpc": True,
            },
            "bindings": {
                "input_parameter": input_parameter["name"],
                "output_parameter": output_parameter["name"],
                "config_parameter": config_parameter["name"],
                "direction": direction,
                "bits_port": "bits",
                "input_ports": input_ports,
                "output_ports": output_ports,
                "input_plane_fields": input_fields,
                "output_plane_fields": output_fields,
                "config_fields": ["xstart", "ystart", "slice_width", "slice_height"],
            },
            "legal_domain": {
                "bits": [8, 16],
                "input_and_output_pictures_are_distinct": True,
                "matching_picture_dimensions": True,
                "yuv_chroma": "YUV_444",
                "iteration_region": (
                    "intersection of configured slice rectangle and picture dimensions"
                ),
                "each_pixel_is_independent": True,
            },
            "state_transition": (
                "apply the frozen reversible RGB/YCoCg arithmetic to every active "
                "raster pixel through repeated Verilator invocations"
            ),
            "composition_reduction": (
                "the C adapter retains bounds/error orchestration while every pixel "
                "value written by the source function is returned by RTL"
            ),
        },
        "selection": {
            "basis": selected["selection_basis"],
            "decode_execution_count": selected.get("execution_count"),
            "shape_evidence": selected.get("literal_size_bound"),
        },
        "obligations": [
            "full-frame Decode C_ONLY/SHADOW/RTL_RETURN comparison",
            "full-frame Encode C_ONLY/SHADOW/RTL_RETURN comparison",
            "human review of raster bounds and 16-bpc chroma reduction before promotion",
        ],
        "promotion": {
            "status": "BLOCKED_PENDING_HUMAN_CONTRACT_REVIEW",
            "simulation_may_proceed": True,
        },
    }


def build_bounded_block_pred_search_contract(
    selected: dict[str, Any], function: dict[str, Any], source_dir: pathlib.Path
) -> dict[str, Any]:
    """Freeze the bounded block-predict search and one indexed decision write."""
    name = str(function["name"])
    cid = safe_identifier(name) + "_decode_transition"
    source = source_dir / str(function["source_file"])
    source_text = source.read_text(encoding="utf-8", errors="replace")
    lines = source_text.splitlines()
    start = int(function.get("line", 1))
    end = int(function.get("end_line", start))
    body = "\n".join(lines[start - 1:end])
    parameters = function.get("parameters", []) or []
    pointers = function.get("pointer_parameters", []) or []
    config_parameter = next(
        item for item in pointers if "dsc_cfg_t *" in str(item.get("type"))
    )
    state_parameter = next(
        item for item in pointers if "dsc_state_t *" in str(item.get("type"))
    )
    line_parameter = next(
        item for item in pointers if "int **" in str(item.get("type"))
    )
    scalar_parameters = [item for item in parameters if not item.get("pointer")]
    if (
        len(scalar_parameters) != 2
        or any(str(item.get("type")) != "int" for item in scalar_parameters)
    ):
        raise RuntimeError("bounded block predictor requires two scalar indices")
    cpnt_parameter, hpos_parameter = scalar_parameters
    config_fields = {
        (str(item.get("name")), str(item.get("type")))
        for item in function.get("fields_read", [])
        if item.get("record") == "dsc_cfg_t"
    }
    state_fields = {
        (str(item.get("name")), str(item.get("type")))
        for item in function.get("fields_read", [])
        if item.get("record") == "dsc_state_t"
    }
    state_write_fields = {
        (str(item.get("name")), str(item.get("type")))
        for item in function.get("fields_write", [])
        if item.get("record") == "dsc_state_t"
    }
    if config_fields != {
        ("bits_per_component", "int"), ("block_pred_enable", "int"),
        ("native_420", "int"),
    } or state_fields != {
        ("bpCount", "int"), ("cpntBitDepth", "int[4]"),
        ("edgeDetected", "int"), ("lastEdgeCount", "int"),
        ("lastErr", "int[4][3][13]"), ("numComponents", "int"),
        ("predErr", "int[4][13]"),
    } or state_write_fields != {
        ("bpCount", "int"), ("edgeDetected", "int"),
        ("lastEdgeCount", "int"), ("lastErr", "int[4][3][13]"),
        ("predErr", "int[4][13]"), ("prevLinePred", "PRED_TYPE *"),
    }:
        raise RuntimeError("bounded block predictor fields changed")

    components = integer_define(source_dir, "NUM_COMPONENTS")
    bp_range = integer_define(source_dir, "BP_RANGE")
    bp_size = integer_define(source_dir, "BP_SIZE")
    pred_block_size = integer_define(source_dir, "PRED_BLK_SIZE")
    edge_count = integer_define(source_dir, "BP_EDGE_COUNT")
    edge_strength = integer_define(source_dir, "BP_EDGE_STRENGTH")
    padding_left = integer_define(source_dir, "PADDING_LEFT")
    if (
        components, bp_range, bp_size, pred_block_size,
        edge_count, edge_strength, padding_left
    ) != (4, 13, 3, 3, 3, 32, 5):
        raise RuntimeError("bounded block predictor constants changed")
    enum_match = re.search(
        r"typedef\s+enum\s*\{\s*PT_MAP\s*=\s*0\s*,\s*PT_LEFT\s*,\s*"
        r"PT_BLOCK\s*\}\s*PRED_TYPE\s*;",
        "\n".join(
            path.read_text(encoding="utf-8", errors="replace")
            for path in sorted(source_dir.glob("*.h"))
        ),
        re.MULTILINE,
    )
    if not enum_match:
        raise RuntimeError("bounded block predictor enum changed")

    evidence = selected.get("literal_size_bound", {}) or {}
    dependency_contract_path = pathlib.Path(
        str(evidence.get("callee_contract_file", ""))
    )
    dependency_candidate_path = pathlib.Path(
        str(evidence.get("callee_candidate_file", ""))
    )
    if not dependency_contract_path.is_file() or not dependency_candidate_path.is_file():
        raise RuntimeError("bounded block predictor dependency artifacts are missing")
    if (
        file_hash(dependency_contract_path)
        != str(evidence.get("callee_contract_sha256", ""))
        or file_hash(dependency_candidate_path)
        != str(evidence.get("callee_candidate_sha256", ""))
    ):
        raise RuntimeError("bounded block predictor dependency changed after discovery")
    dependency_contract = read_json(dependency_contract_path)
    dependency_id = str(evidence.get("callee_contract_id", ""))
    callee_names = {
        str(item.get("name")) for item in function.get("callees", [])
    }
    if (
        dependency_contract.get("contract_id") != dependency_id
        or callee_names != {str(evidence.get("callee"))}
        or (dependency_contract.get("semantics", {}) or {}).get("kind")
        != "windowed_sample_predict"
    ):
        raise RuntimeError("bounded block predictor dependency has wrong semantics")
    repo_root = pathlib.Path(__file__).resolve().parent.parent

    def repo_path(path: pathlib.Path) -> str:
        try:
            return str(path.resolve().relative_to(repo_root.resolve()))
        except ValueError:
            return str(path.resolve())

    dependency = {
        "role": "block_sample_predict",
        "function": str(evidence.get("callee")),
        "contract_id": dependency_id,
        "module": safe_identifier(dependency_id),
        "contract_file": repo_path(dependency_contract_path),
        "contract_sha256": file_hash(dependency_contract_path),
        "module_file": repo_path(dependency_candidate_path),
        "module_sha256": file_hash(dependency_candidate_path),
    }
    argument_ports = {
        str(cpnt_parameter["name"]): safe_identifier(str(cpnt_parameter["name"])),
        str(hpos_parameter["name"]): safe_identifier(str(hpos_parameter["name"])),
    }
    config_ports = {
        field: f"cfg_{safe_identifier(field)}" for field in (
            "bits_per_component", "block_pred_enable", "native_420",
        )
    }
    state_ports = {
        field: f"state_{safe_identifier(field)}" for field in (
            "numComponents", "bpCount", "lastEdgeCount", "edgeDetected",
        )
    }
    depth_ports = [f"state_cpnt_bit_depth_{index}" for index in range(components)]
    pred_input_ports = [
        [f"state_pred_err_{component}_{vector}" for vector in range(bp_range)]
        for component in range(components)
    ]
    last_input_ports = [
        [
            [
                f"state_last_err_{component}_{block}_{vector}"
                for vector in range(bp_range)
            ]
            for block in range(bp_size)
        ]
        for component in range(components)
    ]
    line_sample_offsets = list(range(-8, 6))
    line_sample_ports = [
        "line_sample_m" + str(abs(offset)) if offset < 0
        else "line_sample_p" + str(offset)
        for offset in line_sample_offsets
    ]
    state_output_ports = {
        field: f"state_{safe_identifier(field)}_out"
        for field in ("bpCount", "lastEdgeCount", "edgeDetected")
    }
    pred_output_ports = [
        [f"state_pred_err_{component}_{vector}_out" for vector in range(bp_range)]
        for component in range(components)
    ]
    last_output_ports = [
        [
            [
                f"state_last_err_{component}_{block}_{vector}_out"
                for vector in range(bp_range)
            ]
            for block in range(bp_size)
        ]
        for component in range(components)
    ]
    write_ports = {
        "enable": "prev_line_pred_write_enable",
        "index": "prev_line_pred_write_index",
        "value": "prev_line_pred_write_value",
    }
    ports = [
        *[
            {"name": port, "direction": "input", "width": 32, "signed": True}
            for port in [
                *argument_ports.values(), *config_ports.values(), *state_ports.values(),
                *depth_ports,
                *[value for row in pred_input_ports for value in row],
                *[
                    value for component in last_input_ports
                    for block in component for value in block
                ],
                *line_sample_ports,
            ]
        ],
        {"name": "domain_valid", "direction": "output", "width": 1, "signed": False},
        *[
            {"name": port, "direction": "output", "width": 32, "signed": True}
            for port in [
                *state_output_ports.values(),
                *[value for row in pred_output_ports for value in row],
                *[
                    value for component in last_output_ports
                    for block in component for value in block
                ],
            ]
        ],
        {"name": write_ports["enable"], "direction": "output", "width": 1, "signed": False},
        {"name": write_ports["index"], "direction": "output", "width": 32, "signed": True},
        {"name": write_ports["value"], "direction": "output", "width": 32, "signed": True},
    ]
    return {
        "schema_version": 2,
        "contract_id": cid,
        "status": "PROVISIONAL_SIMULATION_ONLY",
        "origin": "tool_discovered_decoder_runtime_transition",
        "function": {
            "clang_usr": function.get("clang_usr"), "name": name,
            "source_file": function.get("source_file"),
            "source_span": {"start_line": start, "end_line": end},
            "source_body_sha256": hashlib.sha256(body.encode("utf-8")).hexdigest(),
            "parameters": parameters, "return_type": function.get("return_type"),
        },
        "interface": {"ports": ports},
        "dependencies": [dependency],
        "semantics": {
            "kind": "bounded_block_pred_search_transition",
            "constants": {
                "component_count": components, "bp_range": bp_range,
                "bp_size": bp_size, "pred_block_size": pred_block_size,
                "edge_count": edge_count, "edge_strength": edge_strength,
                "padding_left": padding_left, "pt_map": 0,
                "pt_left": 1, "pt_block": 2,
            },
            "bindings": {
                "config_parameter": config_parameter["name"],
                "state_parameter": state_parameter["name"],
                "line_parameter": line_parameter["name"],
                "component_parameter": cpnt_parameter["name"],
                "horizontal_parameter": hpos_parameter["name"],
                "argument_ports": argument_ports,
                "config_ports": config_ports, "state_ports": state_ports,
                "depth_ports": depth_ports,
                "pred_input_ports": pred_input_ports,
                "last_input_ports": last_input_ports,
                "line_sample_offsets": line_sample_offsets,
                "line_sample_ports": line_sample_ports,
                "state_output_ports": state_output_ports,
                "pred_output_ports": pred_output_ports,
                "last_output_ports": last_output_ports,
                "write_ports": write_ports,
                "decision_field": "prevLinePred",
            },
            "legal_domain": {
                "component": [0, components - 1],
                "num_components": [3, components],
                "bits_per_component": [8, 16],
                "component_bit_depth": [8, 16],
                "horizontal_position_nonnegative": True,
                "line_samples": (
                    "recon at hPos+PADDING_LEFT and candidate taps at "
                    "hPos+PADDING_LEFT-1-vector only when hPos>vector"
                ),
                "inactive_candidate_taps_tied_zero_and_not_dereferenced": True,
            },
            "state_transition": (
                "update fixed BP accumulators and emit at most one indexed "
                "prevLinePred decision write"
            ),
            "composition_reduction": (
                "the hash-bound sample predictor is specialized to its PT_BLOCK "
                "branch for candidate vectors 0..12"
            ),
        },
        "selection": {
            "basis": selected["selection_basis"],
            "decode_execution_count": selected.get("execution_count"),
            "shape_evidence": evidence,
        },
        "obligations": [
            "full-frame Decode C_ONLY/SHADOW/RTL_RETURN comparison",
            "full-frame Encode C_ONLY/SHADOW/RTL_RETURN comparison",
            "human review of PT_BLOCK specialization, accumulator bounds, and indexed write before promotion",
        ],
        "promotion": {
            "status": "BLOCKED_PENDING_HUMAN_CONTRACT_REVIEW",
            "simulation_may_proceed": True,
        },
    }


def build_bounded_prediction_decode_contract(
    selected: dict[str, Any], function: dict[str, Any], source_dir: pathlib.Path
) -> dict[str, Any]:
    """Freeze the decoder half of the fixed-unit reconstruction loop."""
    name = str(function["name"])
    cid = safe_identifier(name) + "_decode_transition"
    source = source_dir / str(function["source_file"])
    source_text = source.read_text(encoding="utf-8", errors="replace")
    lines = source_text.splitlines()
    start = int(function.get("line", 1))
    end = int(function.get("end_line", start))
    body = "\n".join(lines[start - 1:end])
    parameters = function.get("parameters", []) or []
    pointers = function.get("pointer_parameters", []) or []
    config_parameter = next(
        item for item in pointers if "dsc_cfg_t *" in str(item.get("type"))
    )
    state_parameter = next(
        item for item in pointers if "dsc_state_t *" in str(item.get("type"))
    )
    scalar_parameters = [item for item in parameters if not item.get("pointer")]
    if (
        len(scalar_parameters) != 4
        or any(str(item.get("type")) != "int" for item in scalar_parameters)
    ):
        raise RuntimeError("bounded prediction decoder requires four scalar arguments")
    horizontal, vertical, sample_count, qp_parameter = scalar_parameters
    config_fields = {
        (str(item.get("name")), str(item.get("type")))
        for item in function.get("fields_read", [])
        if item.get("record") == "dsc_cfg_t"
    }
    state_fields = {
        (str(item.get("name")), str(item.get("type")))
        for item in function.get("fields_read", [])
        if item.get("record") == "dsc_state_t"
    }
    state_write_fields = {
        (str(item.get("name")), str(item.get("type")))
        for item in function.get("fields_write", [])
        if item.get("record") == "dsc_state_t"
    }
    if config_fields != {
        ("bits_per_component", "int"), ("full_ich_err_precision", "int"),
        ("native_420", "int"),
    } or state_fields != {
        ("cpntBitDepth", "int[4]"), ("currLine", "int *[4]"),
        ("isEncoder", "int"), ("maxError", "int[4]"),
        ("maxMidError", "int[4]"), ("midpointRecon", "int[4][6]"),
        ("origLine", "int *[4]"), ("prevLine", "int *[5]"),
        ("prevLinePred", "PRED_TYPE *"),
        ("quantizedResidual", "int[4][3]"),
        ("quantizedResidualMid", "int[4][3]"),
        ("unitCType", "int[4]"), ("unitStartHPos", "int[4]"),
        ("unitsPerGroup", "int"), ("useMidpoint", "int[4]"),
    } or state_write_fields != {
        ("currLine", "int *[4]"), ("maxError", "int[4]"),
        ("maxMidError", "int[4]"), ("midpointRecon", "int[4][6]"),
        ("primaryQp", "int"), ("quantizedResidual", "int[4][3]"),
        ("quantizedResidualMid", "int[4][3]"),
    }:
        raise RuntimeError("bounded prediction decoder fields changed")

    units = integer_define(source_dir, "MAX_UNITS_PER_GROUP")
    samples = integer_define(source_dir, "SAMPLES_PER_UNIT")
    components = integer_define(source_dir, "NUM_COMPONENTS")
    padding_left = integer_define(source_dir, "PADDING_LEFT")
    pred_block_size = integer_define(source_dir, "PRED_BLK_SIZE")
    if (units, samples, components, padding_left, pred_block_size) != (4, 3, 4, 5, 3):
        raise RuntimeError("bounded prediction decoder constants changed")
    if not re.search(
        r"typedef\s+enum\s*\{\s*PT_MAP\s*=\s*0\s*,\s*PT_LEFT\s*,\s*"
        r"PT_BLOCK\s*\}\s*PRED_TYPE\s*;",
        "\n".join(
            path.read_text(encoding="utf-8", errors="replace")
            for path in sorted(source_dir.glob("*.h"))
        ),
        re.MULTILINE,
    ):
        raise RuntimeError("bounded prediction decoder predictor enum changed")

    evidence = selected.get("literal_size_bound", {}) or {}
    evidence_dependencies = evidence.get("accepted_dependencies", []) or []
    role_signatures = {
        "qp_mapping": {
            "cpnt", "qp", "dsc_version_minor", "native_420",
            "cpntBitDepth_0", "cpntBitDepth_1", "qlevel_luma",
            "qlevel_chroma", "return_value",
        },
        "sample_predict": {
            "hPos", "predType", "qLevel", "unit", "cpnt_bit_depth",
            "unit_c_type", "quantized_residual_0", "quantized_residual_1",
            *{f"prev_{index}" for index in range(3, 18)},
            *{f"curr_{index}" for index in range(16)}, "return_value",
        },
        "midpoint": {"cpnt", "qlevel", "cpntBitDepth", "leftRecon", "return_value"},
        "quantize": {"e", "qlevel", "return_value"},
        "residual_size": {"eq", "return_value"},
        "max_residual": {
            "cpnt", "qp", "dsc_version_minor", "native_420",
            "cpntBitDepth_0", "cpntBitDepth_1", "cpntBitDepth_selected",
            "qlevel_luma", "qlevel_chroma", "return_value",
        },
    }
    repo_root = pathlib.Path(__file__).resolve().parent.parent

    def repo_path(path: pathlib.Path) -> str:
        try:
            return str(path.resolve().relative_to(repo_root.resolve()))
        except ValueError:
            return str(path.resolve())

    dependencies = []
    for item in evidence_dependencies:
        contract_path = pathlib.Path(str(item.get("contract_file", "")))
        module_path = pathlib.Path(str(item.get("candidate_file", "")))
        if not contract_path.is_file() or not module_path.is_file():
            raise RuntimeError("bounded prediction dependency artifact is missing")
        if (
            file_hash(contract_path) != str(item.get("contract_sha256", ""))
            or file_hash(module_path) != str(item.get("candidate_sha256", ""))
        ):
            raise RuntimeError("bounded prediction dependency changed after discovery")
        dependency_contract = read_json(contract_path)
        ports = {
            str(port.get("name"))
            for port in (dependency_contract.get("interface", {}) or {}).get("ports", [])
        }
        roles = [role for role, signature in role_signatures.items() if signature == ports]
        if len(roles) != 1:
            raise RuntimeError("bounded prediction dependency interface is unrecognized")
        dependencies.append({
            "role": roles[0], "function": item.get("function"),
            "contract_id": item.get("contract_id"),
            "contract_file": repo_path(contract_path),
            "contract_sha256": file_hash(contract_path),
            "module_file": repo_path(module_path),
            "module_sha256": file_hash(module_path),
            "active_in_decode_specialization": roles[0] in {
                "qp_mapping", "sample_predict", "midpoint"
            },
        })
    if {str(item["role"]) for item in dependencies} != set(role_signatures):
        raise RuntimeError("bounded prediction dependencies are incomplete")
    dependency_functions = {str(item["function"]) for item in dependencies}
    source_callees = {
        str(item.get("name")) for item in function.get("callees", [])
        if str(item.get("name")) in dependency_functions
    }
    if source_callees != dependency_functions:
        raise RuntimeError("bounded prediction dependency/source call graph changed")
    dependencies.sort(key=lambda item: str(item["role"]))

    argument_ports = {
        str(item["name"]): safe_identifier(str(item["name"]))
        for item in scalar_parameters
    }
    config_ports = {
        "native_420": "cfg_native_420",
        "dsc_version_minor": "cfg_dsc_version_minor",
    }
    state_ports = {
        "isEncoder": "state_is_encoder",
        "unitsPerGroup": "state_units_per_group",
    }
    depth_ports = [f"state_cpnt_bit_depth_{index}" for index in range(components)]
    unit_type_ports = [f"state_unit_c_type_{index}" for index in range(units)]
    unit_start_ports = [f"state_unit_start_hpos_{index}" for index in range(units)]
    midpoint_ports = [f"state_use_midpoint_{index}" for index in range(units)]
    left_ports = [f"state_left_recon_{index}" for index in range(components)]
    residual_ports = [
        [f"state_quantized_residual_{unit}_{index}" for index in range(samples)]
        for unit in range(units)
    ]
    qlevel_ports = {"luma": "qlevel_luma_qp", "chroma": "qlevel_chroma_qp"}
    prediction_port = "prev_line_prediction"
    previous_line_ports = [
        [f"prev_line_unit_{unit}_tap_{tap}" for tap in range(6)]
        for unit in range(units)
    ]
    current_a_ports = [f"curr_line_unit_{unit}_a" for unit in range(units)]
    current_block_ports = [f"curr_line_unit_{unit}_block" for unit in range(units)]
    write_ports = [
        {
            "enable": f"line_write_{unit}_enable",
            "component": f"line_write_{unit}_component",
            "index": f"line_write_{unit}_index",
            "value": f"line_write_{unit}_value",
        }
        for unit in range(units)
    ]
    scalar_inputs = [
        *argument_ports.values(), *config_ports.values(), *state_ports.values(),
        *depth_ports, *unit_type_ports, *unit_start_ports, *midpoint_ports,
        *left_ports, *[value for row in residual_ports for value in row],
        *qlevel_ports.values(), prediction_port,
        *[value for row in previous_line_ports for value in row],
        *current_a_ports, *current_block_ports,
    ]
    ports = [
        *[
            {"name": port, "direction": "input", "width": 32, "signed": True}
            for port in scalar_inputs
        ],
        {"name": "domain_valid", "direction": "output", "width": 1, "signed": False},
    ]
    for slot in write_ports:
        ports.append({
            "name": slot["enable"], "direction": "output", "width": 1,
            "signed": False,
        })
        ports.extend(
            {"name": slot[key], "direction": "output", "width": 32, "signed": True}
            for key in ("component", "index", "value")
        )
    return {
        "schema_version": 2,
        "contract_id": cid,
        "status": "PROVISIONAL_SIMULATION_ONLY",
        "origin": "tool_discovered_decoder_runtime_transition",
        "function": {
            "clang_usr": function.get("clang_usr"), "name": name,
            "source_file": function.get("source_file"),
            "source_span": {"start_line": start, "end_line": end},
            "source_body_sha256": hashlib.sha256(body.encode("utf-8")).hexdigest(),
            "parameters": parameters, "return_type": function.get("return_type"),
        },
        "interface": {"ports": ports},
        "dependencies": dependencies,
        "semantics": {
            "kind": "bounded_prediction_decode_transition",
            "specialization": {"state_is_encoder": 0},
            "constants": {
                "max_units": units, "samples_per_unit": samples,
                "component_count": components, "padding_left": padding_left,
                "pred_block_size": pred_block_size,
                "pt_map": 0, "pt_left": 1, "pt_block": 2,
            },
            "bindings": {
                "config_parameter": config_parameter["name"],
                "state_parameter": state_parameter["name"],
                "horizontal_parameter": horizontal["name"],
                "vertical_parameter": vertical["name"],
                "sample_count_parameter": sample_count["name"],
                "qp_parameter": qp_parameter["name"],
                "argument_ports": argument_ports, "config_ports": config_ports,
                "state_ports": state_ports, "depth_ports": depth_ports,
                "unit_type_ports": unit_type_ports,
                "unit_start_ports": unit_start_ports,
                "midpoint_ports": midpoint_ports, "left_ports": left_ports,
                "residual_ports": residual_ports, "qlevel_ports": qlevel_ports,
                "prediction_port": prediction_port,
                "previous_line_ports": previous_line_ports,
                "current_a_ports": current_a_ports,
                "current_block_ports": current_block_ports,
                "write_ports": write_ports,
                "quant_table_luma_field": "quantTableLuma",
                "quant_table_chroma_field": "quantTableChroma",
                "previous_line_field": "prevLine",
                "current_line_field": "currLine",
                "prediction_field": "prevLinePred",
            },
            "legal_domain": {
                "decoder_only": True, "units_per_group": [3, units],
                "active_unit_component_indices_are_unique": True,
                "component": [0, components - 1], "component_bit_depth": [8, 16],
                "horizontal_position_nonnegative": True,
                "vertical_position_nonnegative": True,
                "sample_count": [0, samples - 1], "qp": [0, 31],
                "residual_index_per_active_unit": [0, samples - 1],
                "qlevel": [0, 16], "prev_line_prediction": [0, 11],
                "all_active_line_taps_present": True,
            },
            "state_transition": (
                "for decoder state only, reconstruct each active unit and emit "
                "one explicit current-line write slot"
            ),
            "composition_reduction": (
                "hash-bound mapping, sample-predict, and midpoint leaves are "
                "specialized into a fixed four-slot chain; quantization and error "
                "accumulation dependencies are proven inactive by isEncoder==0"
            ),
        },
        "selection": {
            "basis": selected["selection_basis"],
            "decode_execution_count": selected.get("execution_count"),
            "shape_evidence": evidence,
        },
        "obligations": [
            "full-frame Decode C_ONLY/SHADOW/RTL_RETURN comparison",
            "prove encoder calls are bypassed and reported NOT_REACHED",
            "human review of decoder specialization and complete line-write footprint before promotion",
        ],
        "promotion": {
            "status": "BLOCKED_PENDING_HUMAN_CONTRACT_REVIEW",
            "simulation_may_proceed": True,
        },
    }


def build_bounded_rate_control_decode_contract(
    selected: dict[str, Any], function: dict[str, Any], source_dir: pathlib.Path
) -> dict[str, Any]:
    """Freeze decoder rate control and up to three chained bit removals."""
    name = str(function["name"])
    cid = safe_identifier(name) + "_decode_transition"
    source = source_dir / str(function["source_file"])
    source_text = source.read_text(encoding="utf-8", errors="replace")
    lines = source_text.splitlines()
    start = int(function.get("line", 1))
    end = int(function.get("end_line", start))
    body = "\n".join(lines[start - 1:end])
    parameters = function.get("parameters", []) or []
    pointers = function.get("pointer_parameters", []) or []
    config_parameter = next(
        item for item in pointers if "dsc_cfg_t *" in str(item.get("type"))
    )
    state_parameter = next(
        item for item in pointers if "dsc_state_t *" in str(item.get("type"))
    )
    scalar_parameters = [item for item in parameters if not item.get("pointer")]
    if (
        len(scalar_parameters) != 5
        or any(str(item.get("type")) != "int" for item in scalar_parameters)
    ):
        raise RuntimeError("bounded rate control requires five scalar arguments")
    (
        throttle_parameter, bpg_parameter, group_count_parameter,
        scale_parameter, group_size_parameter,
    ) = scalar_parameters
    config_fields = {
        (str(item.get("name")), str(item.get("type")))
        for item in function.get("fields_read", [])
        if item.get("record") == "dsc_cfg_t"
    }
    range_fields = {
        (str(item.get("name")), str(item.get("type")))
        for item in function.get("fields_read", [])
        if item.get("record") == "dsc_range_cfg_t"
    }
    state_fields = {
        (str(item.get("name")), str(item.get("type")))
        for item in function.get("fields_read", [])
        if item.get("record") == "dsc_state_t"
    }
    state_write_fields = {
        (str(item.get("name")), str(item.get("type")))
        for item in function.get("fields_write", [])
        if item.get("record") == "dsc_state_t"
    }
    if config_fields != {
        ("bits_per_component", "int"), ("bits_per_pixel", "int"),
        ("dsc_version_minor", "int"), ("initial_xmit_delay", "int"),
        ("native_420", "int"), ("native_422", "int"),
        ("rc_buf_thresh", "int[14]"), ("rc_edge_factor", "int"),
        ("rc_model_size", "int"), ("rc_quant_incr_limit0", "int"),
        ("rc_quant_incr_limit1", "int"),
        ("rc_range_parameters", "dsc_range_cfg_t[15]"),
        ("rc_tgt_offset_hi", "int"), ("rc_tgt_offset_lo", "int"),
        ("rcb_bits", "int"),
    } or range_fields != {
        ("range_bpg_offset", "int"), ("range_max_qp", "int"),
        ("range_min_qp", "int"),
    } or state_fields != {
        ("bitSaveMode", "int"), ("bufferFullness", "int"),
        ("codedGroupSize", "int"), ("cpntBitDepth", "int[4]"),
        ("firstFlat", "int"), ("ichSelected", "int"),
        ("isEncoder", "int"), ("midpointSelected", "int[4]"),
        ("mppState", "int"), ("pixelCount", "int"),
        ("predictedSize", "int[4]"), ("prevQp", "int"),
        ("prevRange", "int"), ("rcSizeGroup", "int"),
        ("rcSizeUnit", "int[4]"), ("stQp", "int"),
        ("unitsPerGroup", "int"), ("useMidpoint", "int[4]"),
        ("vPos", "int"),
    } or state_write_fields != {
        ("bitSaveMode", "int"), ("errorOccurred", "int"),
        ("mppState", "int"), ("pixelCount", "int"),
        ("prevQp", "int"), ("prevRange", "int"),
        ("rcSizeGroup", "int"), ("stQp", "int"),
    }:
        raise RuntimeError("bounded rate-control direct fields changed")

    ranges = integer_define(source_dir, "NUM_BUF_RANGES")
    units = integer_define(source_dir, "MAX_UNITS_PER_GROUP")
    samples = integer_define(source_dir, "SAMPLES_PER_UNIT")
    scale_binary_point = integer_define(source_dir, "RC_SCALE_BINARY_POINT")
    if (ranges, units, samples, scale_binary_point) != (15, 4, 3, 3):
        raise RuntimeError("bounded rate-control constants changed")
    print_debug = re.search(
        r"^[ \t]*#[ \t]*define[ \t]+PRINT_DEBUG_RC[ \t]+([0-9]+)\b",
        source_text,
        re.MULTILINE,
    )
    overflow_macro = re.search(
        r"^[ \t]*#[ \t]*define[ \t]+OVERFLOW_AVOID_THRESHOLD[ \t]+"
        r"\(dsc_cfg->native_422[ \t]*\?[ \t]*-224[ \t]*:[ \t]*-172\)",
        "\n".join(
            path.read_text(encoding="utf-8", errors="replace")
            for path in sorted(source_dir.glob("*.h"))
        ),
        re.MULTILINE,
    )
    if not print_debug or int(print_debug.group(1)) != 0 or not overflow_macro:
        raise RuntimeError("bounded rate-control compile-time branch changed")

    evidence = selected.get("literal_size_bound", {}) or {}
    dependency_contract_path = pathlib.Path(
        str(evidence.get("callee_contract_file", ""))
    )
    dependency_candidate_path = pathlib.Path(
        str(evidence.get("callee_candidate_file", ""))
    )
    if not dependency_contract_path.is_file() or not dependency_candidate_path.is_file():
        raise RuntimeError("bounded rate-control dependency artifacts are missing")
    if (
        file_hash(dependency_contract_path)
        != str(evidence.get("callee_contract_sha256", ""))
        or file_hash(dependency_candidate_path)
        != str(evidence.get("callee_candidate_sha256", ""))
    ):
        raise RuntimeError("bounded rate-control dependency changed after discovery")
    dependency_contract = read_json(dependency_contract_path)
    if (
        dependency_contract.get("contract_id") != evidence.get("callee_contract_id")
        or (dependency_contract.get("semantics", {}) or {}).get("kind")
        != "scalar_record_memory_transition"
    ):
        raise RuntimeError("bounded rate-control dependency has wrong semantics")
    if {
        str(item.get("name")) for item in function.get("callees", [])
        if str(item.get("name")) == str(evidence.get("callee"))
    } != {str(evidence.get("callee"))}:
        raise RuntimeError("bounded rate-control child call changed")
    repo_root = pathlib.Path(__file__).resolve().parent.parent

    def repo_path(path: pathlib.Path) -> str:
        try:
            return str(path.resolve().relative_to(repo_root.resolve()))
        except ValueError:
            return str(path.resolve())

    dependency = {
        "role": "remove_one_pixel_bits",
        "function": evidence.get("callee"),
        "contract_id": evidence.get("callee_contract_id"),
        "module": safe_identifier(str(evidence.get("callee_contract_id"))),
        "contract_file": repo_path(dependency_contract_path),
        "contract_sha256": file_hash(dependency_contract_path),
        "module_file": repo_path(dependency_candidate_path),
        "module_sha256": file_hash(dependency_candidate_path),
        "memory_write_disabled_by_decoder_specialization": True,
    }

    argument_ports = {
        str(item["name"]): safe_identifier(str(item["name"]))
        for item in scalar_parameters
    }
    config_scalar_fields = (
        "bits_per_component", "bits_per_pixel", "chunk_size",
        "dsc_version_minor", "initial_xmit_delay", "native_420", "native_422",
        "rc_edge_factor", "rc_model_size", "rc_quant_incr_limit0",
        "rc_quant_incr_limit1", "rc_tgt_offset_hi", "rc_tgt_offset_lo",
        "rcb_bits", "vbr_enable",
    )
    config_ports = {
        field: f"cfg_{safe_identifier(field)}" for field in config_scalar_fields
    }
    state_input_fields = (
        "bitSaveMode", "bitsClamped", "bpgFracAccum", "bufferFullness",
        "chunkCount", "chunkPixelTimes", "codedGroupSize", "errorOccurred",
        "firstFlat", "ichSelected", "isEncoder", "mppState", "numBitsChunk",
        "pixelCount", "prevQp", "prevRange", "rcSizeGroup", "sliceWidth",
        "stQp", "unitsPerGroup", "vPos",
    )
    state_ports = {
        field: f"state_{safe_identifier(field)}" for field in state_input_fields
    }
    depth_ports = [f"state_cpnt_bit_depth_{index}" for index in range(2)]
    predicted_ports = [f"state_predicted_size_{index}" for index in range(units)]
    rc_size_ports = [f"state_rc_size_unit_{index}" for index in range(units)]
    use_midpoint_ports = [f"state_use_midpoint_{index}" for index in range(units)]
    threshold_ports = [f"cfg_rc_buf_thresh_{index}" for index in range(ranges - 1)]
    range_ports = {
        field: [f"cfg_{field}_{index}" for index in range(ranges)]
        for field in ("range_min_qp", "range_max_qp", "range_bpg_offset")
    }
    state_output_fields = (
        "bitSaveMode", "bitsClamped", "bpgFracAccum", "bufferFullness",
        "chunkCount", "chunkPixelTimes", "errorOccurred", "mppState",
        "numBitsChunk", "pixelCount", "prevQp", "prevRange",
        "rcSizeGroup", "stQp",
    )
    state_output_ports = {
        field: f"state_{safe_identifier(field)}_out"
        for field in state_output_fields
    }
    input_names = [
        *argument_ports.values(), *config_ports.values(), *state_ports.values(),
        *depth_ports, *predicted_ports, *rc_size_ports,
        *use_midpoint_ports, *threshold_ports,
        *[value for row in range_ports.values() for value in row],
    ]
    ports = [
        *[
            {"name": port, "direction": "input", "width": 32, "signed": True}
            for port in input_names
        ],
        {"name": "domain_valid", "direction": "output", "width": 1, "signed": False},
        *[
            {"name": port, "direction": "output", "width": 32, "signed": True}
            for port in state_output_ports.values()
        ],
    ]
    return {
        "schema_version": 2,
        "contract_id": cid,
        "status": "PROVISIONAL_SIMULATION_ONLY",
        "origin": "tool_discovered_decoder_runtime_transition",
        "function": {
            "clang_usr": function.get("clang_usr"), "name": name,
            "source_file": function.get("source_file"),
            "source_span": {"start_line": start, "end_line": end},
            "source_body_sha256": hashlib.sha256(body.encode("utf-8")).hexdigest(),
            "parameters": parameters, "return_type": function.get("return_type"),
        },
        "interface": {"ports": ports},
        "dependencies": [dependency],
        "semantics": {
            "kind": "bounded_rate_control_decode_transition",
            "specialization": {"state_is_encoder": 0},
            "constants": {
                "num_buf_ranges": ranges, "max_units": units,
                "samples_per_unit": samples,
                "rc_scale_binary_point": scale_binary_point,
                "max_remove_stages": samples, "print_debug_rc": 0,
                "overflow_avoid_native_422": -224,
                "overflow_avoid_other": -172,
            },
            "bindings": {
                "config_parameter": config_parameter["name"],
                "state_parameter": state_parameter["name"],
                "throttle_parameter": throttle_parameter["name"],
                "bpg_parameter": bpg_parameter["name"],
                "group_count_parameter": group_count_parameter["name"],
                "scale_parameter": scale_parameter["name"],
                "group_size_parameter": group_size_parameter["name"],
                "argument_ports": argument_ports, "config_ports": config_ports,
                "state_ports": state_ports, "depth_ports": depth_ports,
                "predicted_ports": predicted_ports,
                "rc_size_ports": rc_size_ports,
                "use_midpoint_ports": use_midpoint_ports,
                "threshold_ports": threshold_ports,
                "range_ports": range_ports,
                "state_output_ports": state_output_ports,
                "range_parameter_field": "rc_range_parameters",
                "threshold_field": "rc_buf_thresh",
                "inactive_encoder_state_fields": ["midpointSelected"],
            },
            "legal_domain": {
                "decoder_only": True, "group_size": [1, samples],
                "units_per_group": [3, units], "previous_range": [0, ranges - 1],
                "dsc_version_minor": [1, 2],
                "native_modes_are_boolean_and_mutually_exclusive": True,
                "slice_width_positive": True,
                "chunk_pixel_times_before_slice_width": True,
                "component_bit_depth": [8, 16],
                "integer_arithmetic": "signed 32-bit C-compatible",
            },
            "state_transition": (
                "chain zero to three pixel-removal stages, choose one of 15 RC "
                "ranges, update bit-save/MPP state, and emit all decoder scalar writes"
            ),
            "composition_reduction": (
                "the hash-bound RemoveBitsEncoderBuffer transition is instantiated "
                "three times; its chunk-memory write is unreachable for isEncoder==0"
            ),
        },
        "selection": {
            "basis": selected["selection_basis"],
            "decode_execution_count": selected.get("execution_count"),
            "shape_evidence": evidence,
        },
        "obligations": [
            "full-frame Decode C_ONLY/SHADOW/RTL_RETURN comparison",
            "prove encoder calls and chunk-memory writes are outside this specialization",
            "human review of signed RC arithmetic, delayed range selection, and QP priority before promotion",
        ],
        "promotion": {
            "status": "BLOCKED_PENDING_HUMAN_CONTRACT_REVIEW",
            "simulation_may_proceed": True,
        },
    }


def build_bounded_line_write_contract(
    selected: dict[str, Any], function: dict[str, Any], source_dir: pathlib.Path
) -> dict[str, Any]:
    """Freeze a fixed-extent reconstructed-line scatter write boundary."""
    name = str(function["name"])
    cid = safe_identifier(name) + "_decode_transition"
    source = source_dir / str(function["source_file"])
    lines = source.read_text(encoding="utf-8", errors="replace").splitlines()
    start = int(function.get("line", 1))
    end = int(function.get("end_line", start))
    body = "\n".join(lines[start - 1:end])
    parameters = function.get("parameters", []) or []
    pointers = function.get("pointer_parameters", []) or []
    config_parameter = next(
        item for item in pointers if "dsc_cfg_t *" in str(item.get("type"))
    )
    state_parameter = next(
        item for item in pointers if "dsc_state_t *" in str(item.get("type"))
    )
    line_parameter = next(
        item for item in pointers if "int **" in str(item.get("type"))
    )
    state_fields = {
        (str(item.get("name")), str(item.get("type")))
        for item in function.get("fields_read", [])
        if item.get("record") == "dsc_state_t"
    }
    required_fields = {
        ("hPos", "int"), ("ichIndicesInGroup", "int"),
        ("ichLookup", "int[6]"), ("ichPixels", "unsigned int[6][4]"),
        ("ichSelected", "int"), ("numComponents", "int"),
        ("pixelsInGroup", "int"),
    }
    if state_fields != required_fields:
        raise RuntimeError("bounded line write fields do not match the frozen shape")
    max_pixels = integer_define(source_dir, "MAX_PIXELS_PER_GROUP")
    components = integer_define(source_dir, "NUM_COMPONENTS")
    padding_left = integer_define(source_dir, "PADDING_LEFT")
    ich_bits = integer_define(source_dir, "ICH_BITS")
    if (max_pixels, components, padding_left, ich_bits) != (6, 4, 5, 5):
        raise RuntimeError("bounded line write constants do not match DSC shape")
    pixel_ports = [
        [f"ich_pixel_{pixel}_{component}" for component in range(components)]
        for pixel in range(max_pixels)
    ]
    write_index_ports = [f"write_index_{pixel}" for pixel in range(max_pixels)]
    write_enable_ports = [
        [f"write_enable_{pixel}_{component}" for component in range(components)]
        for pixel in range(max_pixels)
    ]
    write_value_ports = [
        [f"write_value_{pixel}_{component}" for component in range(components)]
        for pixel in range(max_pixels)
    ]
    ports = [
        {"name": "state_hpos", "direction": "input", "width": 32, "signed": True},
        {"name": "state_pixels_in_group", "direction": "input", "width": 32, "signed": True},
        {"name": "state_ich_indices", "direction": "input", "width": 32, "signed": True},
        {"name": "state_ich_selected", "direction": "input", "width": 32, "signed": True},
        {"name": "state_num_components", "direction": "input", "width": 32, "signed": True},
        *[
            {"name": port, "direction": "input", "width": 32, "signed": False}
            for row in pixel_ports for port in row
        ],
        *[
            {"name": port, "direction": "output", "width": 32, "signed": True}
            for port in write_index_ports
        ],
        *[
            {"name": port, "direction": "output", "width": 1, "signed": False}
            for row in write_enable_ports for port in row
        ],
        *[
            {"name": port, "direction": "output", "width": 32, "signed": True}
            for row in write_value_ports for port in row
        ],
    ]
    return {
        "schema_version": 2,
        "contract_id": cid,
        "status": "PROVISIONAL_SIMULATION_ONLY",
        "origin": "tool_discovered_decoder_runtime_transition",
        "function": {
            "clang_usr": function.get("clang_usr"),
            "name": name,
            "source_file": function.get("source_file"),
            "source_span": {"start_line": start, "end_line": end},
            "source_body_sha256": hashlib.sha256(body.encode("utf-8")).hexdigest(),
            "parameters": parameters,
            "return_type": function.get("return_type"),
        },
        "interface": {"ports": ports},
        "semantics": {
            "kind": "bounded_line_write_transition",
            "constants": {
                "max_pixels": max_pixels,
                "component_count": components,
                "padding_left": padding_left,
                "ich_bits": ich_bits,
            },
            "bindings": {
                "config_parameter": config_parameter["name"],
                "state_parameter": state_parameter["name"],
                "line_parameter": line_parameter["name"],
                "hpos_field": "hPos",
                "pixels_in_group_field": "pixelsInGroup",
                "ich_indices_field": "ichIndicesInGroup",
                "ich_selected_field": "ichSelected",
                "num_components_field": "numComponents",
                "ich_pixels_field": "ichPixels",
                "hpos_port": "state_hpos",
                "pixels_in_group_port": "state_pixels_in_group",
                "ich_indices_port": "state_ich_indices",
                "ich_selected_port": "state_ich_selected",
                "num_components_port": "state_num_components",
                "pixel_ports": pixel_ports,
                "write_index_ports": write_index_ports,
                "write_enable_ports": write_enable_ports,
                "write_value_ports": write_value_ports,
            },
            "legal_domain": {
                "ich_indices": [0, max_pixels],
                "num_components": [3, components],
                "target_line_storage_valid": True,
            },
            "state_transition": (
                "emit up to six by four explicit reconstructed-line writes from stored ICH pixels"
            ),
        },
        "selection": {
            "basis": selected["selection_basis"],
            "decode_execution_count": selected.get("execution_count"),
            "shape_evidence": selected["literal_size_bound"],
        },
        "obligations": [
            "full-frame Decode C_ONLY/SHADOW/RTL_RETURN comparison",
            "full-frame Encode C_ONLY/SHADOW/RTL_RETURN comparison",
            "human review of bounded line-write addresses and values before promotion",
        ],
        "promotion": {
            "status": "BLOCKED_PENDING_HUMAN_CONTRACT_REVIEW",
            "simulation_may_proceed": True,
        },
    }


def build_sampled_lookup_contract(
    selected: dict[str, Any], function: dict[str, Any], source_dir: pathlib.Path
) -> dict[str, Any]:
    """Freeze pointer-rich history lookup as a sampled-tap combinational boundary."""
    name = str(function["name"])
    cid = safe_identifier(name) + "_decode_transition"
    source = source_dir / str(function["source_file"])
    lines = source.read_text(encoding="utf-8", errors="replace").splitlines()
    start = int(function.get("line", 1))
    end = int(function.get("end_line", start))
    body = "\n".join(lines[start - 1:end])
    parameters = function.get("parameters", []) or []
    pointers = function.get("pointer_parameters", []) or []
    config_parameter = next(
        item for item in pointers if "dsc_cfg_t *" in str(item.get("type"))
    )
    state_parameter = next(
        item for item in pointers if "dsc_state_t *" in str(item.get("type"))
    )
    output_parameter = next(
        item for item in pointers
        if item.get("mode") == "WRITES_THROUGH"
        and "unsigned int *" in str(item.get("type"))
    )
    scalars = [item for item in parameters if not item.get("pointer")]
    config_fields = {
        str(item.get("name")) for item in function.get("fields_read", [])
        if item.get("record") == "dsc_cfg_t"
    }
    state_fields = {
        str(item.get("name")) for item in function.get("fields_read", [])
        if item.get("record") == "dsc_state_t"
    }
    history_fields = {
        str(item.get("name")) for item in function.get("fields_read", [])
        if item.get("record") == "dsc_history_t"
    }
    required_config = {"native_420", "native_422"}
    required_state = {
        "history", "numComponents", "pixelsInGroup", "prevLine", "sliceWidth"
    }
    if config_fields != required_config or state_fields != required_state:
        raise RuntimeError("sampled lookup record fields do not match the frozen shape")
    if history_fields != {"pixels"}:
        raise RuntimeError("sampled lookup history storage could not be identified")
    ich_bits = integer_define(source_dir, "ICH_BITS")
    component_count = integer_define(source_dir, "NUM_COMPONENTS")
    history_ports = [f"history_{index}" for index in range(component_count)]
    native_base_ports = [f"native_base_{index}" for index in range(component_count)]
    native_base1_ports = [f"native_base1_{index}" for index in range(component_count)]
    simple_tap_ports = [f"simple_tap_{index}" for index in range(component_count - 1)]
    output_ports = [f"p_{index}_out" for index in range(component_count)]
    ports = [
        {"name": "native_420", "direction": "input", "width": 1, "signed": False},
        {"name": "native_422", "direction": "input", "width": 1, "signed": False},
        {"name": "entry", "direction": "input", "width": ich_bits, "signed": False},
        {"name": "first_line_flag", "direction": "input", "width": 1, "signed": False},
        {"name": "is_odd_line", "direction": "input", "width": 1, "signed": False},
        {"name": "num_components", "direction": "input", "width": 3, "signed": False},
        *[
            {"name": port, "direction": "input", "width": 32, "signed": False}
            for port in [
                *history_ports, *native_base_ports, *native_base1_ports,
                *simple_tap_ports,
            ]
        ],
        *[
            {"name": port, "direction": "output", "width": 32, "signed": False}
            for port in output_ports
        ],
    ]
    return {
        "schema_version": 2,
        "contract_id": cid,
        "status": "PROVISIONAL_SIMULATION_ONLY",
        "origin": "tool_discovered_decoder_runtime_transition",
        "function": {
            "clang_usr": function.get("clang_usr"),
            "name": name,
            "source_file": function.get("source_file"),
            "source_span": {"start_line": start, "end_line": end},
            "source_body_sha256": hashlib.sha256(body.encode("utf-8")).hexdigest(),
            "parameters": parameters,
            "return_type": function.get("return_type"),
        },
        "interface": {"ports": ports},
        "semantics": {
            "kind": "sampled_lookup_transition",
            "constants": {
                "ich_bits": ich_bits,
                "ich_size": 1 << ich_bits,
                "ich_pixels_above": integer_define(source_dir, "ICH_PIXELS_ABOVE"),
                "padding_left": integer_define(source_dir, "PADDING_LEFT"),
                "component_count": component_count,
            },
            "bindings": {
                "config_parameter": config_parameter["name"],
                "state_parameter": state_parameter["name"],
                "output_parameter": output_parameter["name"],
                "entry_parameter": scalars[0]["name"],
                "horizontal_position_parameter": scalars[1]["name"],
                "first_line_parameter": scalars[2]["name"],
                "odd_line_parameter": scalars[3]["name"],
                "native_420_field": "native_420",
                "native_422_field": "native_422",
                "history_field": "history",
                "history_pixels_field": "pixels",
                "num_components_field": "numComponents",
                "pixels_in_group_field": "pixelsInGroup",
                "prev_line_field": "prevLine",
                "slice_width_field": "sliceWidth",
                "history_ports": history_ports,
                "native_base_ports": native_base_ports,
                "native_base1_ports": native_base1_ports,
                "simple_tap_ports": simple_tap_ports,
                "output_ports": output_ports,
            },
            "legal_domain": {
                "entry": [0, (1 << ich_bits) - 1],
                "flags": [0, 1],
                "num_components": [3, component_count],
                "pixels_in_group_positive": True,
                "sample_width": 32,
            },
            "state_transition": (
                "select four output words from sampled history or clamped previous-line taps"
            ),
        },
        "selection": {
            "basis": selected["selection_basis"],
            "decode_execution_count": selected.get("execution_count"),
            "shape_evidence": selected["literal_size_bound"],
        },
        "obligations": [
            "full-frame Decode C_ONLY/SHADOW/RTL_RETURN comparison",
            "full-frame Encode C_ONLY/SHADOW/RTL_RETURN comparison",
            "human review of sampled address adapter and fixed output extent before promotion",
        ],
        "promotion": {
            "status": "BLOCKED_PENDING_HUMAN_CONTRACT_REVIEW",
            "simulation_may_proceed": True,
        },
    }


def render_rtl(contract: dict[str, Any]) -> str:
    semantics_kind = contract.get("semantics", {}).get("kind")
    if semantics_kind == "fifo_read_transition":
        return render_fifo_read_rtl(contract)
    if semantics_kind == "fifo_read_accounting_transition":
        return render_fifo_read_accounting_rtl(contract)
    if semantics_kind == "fifo_write_transition":
        return render_fifo_write_rtl(contract)
    if semantics_kind == "scalar_record_next_state":
        return render_scalar_record_next_state_rtl(contract)
    if semantics_kind == "sampled_lookup_transition":
        return render_sampled_lookup_rtl(contract)
    if semantics_kind == "scalar_record_memory_transition":
        return render_scalar_record_memory_rtl(contract)
    if semantics_kind == "bounded_mux_refill_transition":
        return render_bounded_mux_refill_rtl(contract)
    if semantics_kind == "bounded_flatness_state_transition":
        return render_bounded_flatness_state_rtl(contract)
    if semantics_kind == "bounded_line_write_transition":
        return render_bounded_line_write_rtl(contract)
    if semantics_kind == "bounded_history_update_transition":
        return render_bounded_history_update_rtl(contract)
    if semantics_kind == "bounded_history_caller_transition":
        return render_bounded_history_caller_rtl(contract)
    if semantics_kind == "bounded_vld_unit_transition":
        return render_bounded_vld_unit_rtl(contract)
    if semantics_kind == "bounded_block_pred_search_transition":
        return render_bounded_block_pred_search_rtl(contract)
    if semantics_kind == "bounded_prediction_decode_transition":
        return render_bounded_prediction_decode_rtl(contract)
    if semantics_kind == "bounded_rate_control_decode_transition":
        return render_bounded_rate_control_decode_rtl(contract)
    if semantics_kind == "bounded_vld_group_decode_transition":
        return render_bounded_vld_group_decode_rtl(contract)
    if semantics_kind == "raster_color_transform_transition":
        return render_raster_color_transform_rtl(contract)
    semantics = contract["semantics"]
    bindings = semantics["bindings"]
    byte_ports = list(bindings["byte_ports"])
    module = safe_identifier(contract["contract_id"])
    port_lines = [
        "    input  logic [4:0] size",
        *[f"    input  logic [7:0] {name}" for name in byte_ports],
        "    input  logic [31:0] bit_count",
        "    input  logic sign_extend",
        "    output logic signed [31:0] return_value",
        "    output logic [31:0] bit_count_out",
    ]
    window_width = (len(byte_ports) + 1) * 8
    concatenation = ", ".join([*byte_ports, "8'b0"])
    return (
        f"module {module}(\n"
        + ",\n".join(port_lines)
        + "\n);\n"
        f"    logic [{window_width - 1}:0] window_i;\n"
        f"    logic [{window_width - 1}:0] shifted_i;\n"
        "    logic [31:0] raw_i;\n"
        "    logic [31:0] mask_i;\n"
        "\n"
        "    always_comb begin\n"
        f"        window_i = {{{concatenation}}};\n"
        "        shifted_i = window_i << bit_count[2:0];\n"
        "        bit_count_out = bit_count + {27'd0, size};\n"
        "        raw_i = 32'd0;\n"
        "        mask_i = 32'd0;\n"
        "        return_value = 32'sd0;\n"
        "        if (size != 0) begin\n"
        f"            raw_i = shifted_i >> ({window_width} - size);\n"
        "            mask_i = (32'h00000001 << size) - 1;\n"
        "            raw_i = raw_i & mask_i;\n"
        "            if (sign_extend && raw_i[size - 1])\n"
        "                return_value = $signed(raw_i | ~mask_i);\n"
        "            else\n"
        "                return_value = $signed(raw_i);\n"
        "        end\n"
        "    end\n"
        "endmodule\n"
    )


def render_fifo_read_rtl(contract: dict[str, Any]) -> str:
    bindings = contract["semantics"]["bindings"]
    byte_ports = list(bindings["byte_ports"])
    module = safe_identifier(contract["contract_id"])
    nbits_port = next(
        port for port in contract["interface"]["ports"] if port["name"] == "nbits"
    )
    nbits_width = int(nbits_port["width"])
    port_lines = [
        f"    input  logic [{nbits_width - 1}:0] nbits",
        *[f"    input  logic [7:0] {name}" for name in byte_ports],
        "    input  logic [31:0] fullness",
        "    input  logic [31:0] read_ptr",
        "    input  logic [31:0] fifo_size",
        "    input  logic sign_extend",
        "    output logic signed [31:0] return_value",
        "    output logic [31:0] fullness_out",
        "    output logic [31:0] read_ptr_out",
    ]
    window_width = (len(byte_ports) + 1) * 8
    concatenation = ", ".join([*byte_ports, "8'b0"])
    return (
        f"module {module}(\n"
        + ",\n".join(port_lines)
        + "\n);\n"
        f"    logic [{window_width - 1}:0] window_i;\n"
        f"    logic [{window_width - 1}:0] shifted_i;\n"
        f"    logic [{window_width - 1}:0] extracted_i;\n"
        "    logic [31:0] raw_i;\n"
        "    logic [31:0] mask_i;\n"
        "    logic [32:0] read_sum_i;\n"
        "    logic sign_i;\n"
        "\n"
        "    always_comb begin\n"
        f"        window_i = {{{concatenation}}};\n"
        "        shifted_i = window_i << read_ptr[2:0];\n"
        "        extracted_i = '0;\n"
        f"        fullness_out = fullness - {{{32 - nbits_width}'d0, nbits}};\n"
        f"        read_sum_i = {{1'b0, read_ptr}} + {{{33 - nbits_width}'d0, nbits}};\n"
        "        if (read_sum_i >= {1'b0, fifo_size})\n"
        "            read_ptr_out = read_sum_i[31:0] - fifo_size;\n"
        "        else\n"
        "            read_ptr_out = read_sum_i[31:0];\n"
        "        raw_i = 32'd0;\n"
        "        mask_i = 32'd0;\n"
        "        return_value = 32'sd0;\n"
        f"        sign_i = shifted_i[{window_width - 1}];\n"
        "        if (nbits != 0) begin\n"
        f"            extracted_i = shifted_i >> ({window_width} - nbits);\n"
        "            raw_i = extracted_i[31:0];\n"
        "            if (nbits >= 32) mask_i = 32'hffffffff;\n"
        "            else mask_i = (32'h00000001 << nbits) - 1;\n"
        "            raw_i = raw_i & mask_i;\n"
        "            if (sign_extend && sign_i)\n"
        "                return_value = $signed(raw_i | ~mask_i);\n"
        "            else\n"
        "                return_value = $signed(raw_i);\n"
        "        end\n"
        "    end\n"
        "endmodule\n"
    )


def render_fifo_read_accounting_rtl(contract: dict[str, Any]) -> str:
    bindings = contract["semantics"]["bindings"]
    byte_ports = list(bindings["byte_ports"])
    module = safe_identifier(contract["contract_id"])
    nbits_port = next(
        port for port in contract["interface"]["ports"] if port["name"] == "nbits"
    )
    nbits_width = int(nbits_port["width"])
    port_lines = [
        f"    input  logic [{nbits_width - 1}:0] nbits",
        *[f"    input  logic [7:0] {name}" for name in byte_ports],
        "    input  logic signed [31:0] bit_count",
        "    input  logic [31:0] fullness",
        "    input  logic [31:0] read_ptr",
        "    input  logic [31:0] fifo_size",
        "    input  logic sign_extend",
        "    output logic signed [31:0] return_value",
        "    output logic signed [31:0] bit_count_out",
        "    output logic [31:0] fullness_out",
        "    output logic [31:0] read_ptr_out",
    ]
    window_width = (len(byte_ports) + 1) * 8
    concatenation = ", ".join([*byte_ports, "8'b0"])
    return (
        f"module {module}(\n"
        + ",\n".join(port_lines)
        + "\n);\n"
        f"    logic [{window_width - 1}:0] window_i;\n"
        f"    logic [{window_width - 1}:0] shifted_i;\n"
        f"    logic [{window_width - 1}:0] extracted_i;\n"
        "    logic [31:0] raw_i;\n"
        "    logic [31:0] mask_i;\n"
        "    logic [32:0] read_sum_i;\n"
        "    logic sign_i;\n"
        "\n"
        "    always_comb begin\n"
        f"        window_i = {{{concatenation}}};\n"
        "        shifted_i = window_i << read_ptr[2:0];\n"
        "        extracted_i = '0;\n"
        f"        bit_count_out = bit_count + {{{32 - nbits_width}'d0, nbits}};\n"
        f"        fullness_out = fullness - {{{32 - nbits_width}'d0, nbits}};\n"
        f"        read_sum_i = {{1'b0, read_ptr}} + {{{33 - nbits_width}'d0, nbits}};\n"
        "        if (read_sum_i >= {1'b0, fifo_size})\n"
        "            read_ptr_out = read_sum_i[31:0] - fifo_size;\n"
        "        else\n"
        "            read_ptr_out = read_sum_i[31:0];\n"
        "        raw_i = 32'd0;\n"
        "        mask_i = 32'd0;\n"
        "        return_value = 32'sd0;\n"
        f"        sign_i = shifted_i[{window_width - 1}];\n"
        "        if (nbits != 0) begin\n"
        f"            extracted_i = shifted_i >> ({window_width} - nbits);\n"
        "            raw_i = extracted_i[31:0];\n"
        "            if (nbits >= 32) mask_i = 32'hffffffff;\n"
        "            else mask_i = (32'h00000001 << nbits) - 1;\n"
        "            raw_i = raw_i & mask_i;\n"
        "            if (sign_extend && sign_i)\n"
        "                return_value = $signed(raw_i | ~mask_i);\n"
        "            else\n"
        "                return_value = $signed(raw_i);\n"
        "        end\n"
        "    end\n"
        "endmodule\n"
    )


def render_fifo_write_rtl(contract: dict[str, Any]) -> str:
    bindings = contract["semantics"]["bindings"]
    byte_ports = list(bindings["byte_ports"])
    byte_outputs = list(bindings["byte_output_ports"])
    module = safe_identifier(contract["contract_id"])
    nbits_port = next(
        port for port in contract["interface"]["ports"] if port["name"] == "nbits"
    )
    nbits_width = int(nbits_port["width"])
    port_lines = [
        "    input  logic [31:0] data",
        f"    input  logic [{nbits_width - 1}:0] nbits",
        *[f"    input  logic [7:0] {name}" for name in byte_ports],
        "    input  logic [31:0] fullness",
        "    input  logic [31:0] write_ptr",
        "    input  logic [31:0] fifo_size",
        "    input  logic [31:0] max_fullness",
        *[f"    output logic [7:0] {name}" for name in byte_outputs],
        "    output logic [31:0] fullness_out",
        "    output logic [31:0] write_ptr_out",
        "    output logic [31:0] max_fullness_out",
    ]
    window_width = len(byte_ports) * 8
    concatenation = ", ".join(byte_ports)
    byte_assignments = "".join(
        f"        {output} = window_out_i[{window_width - 1 - index * 8} -: 8];\n"
        for index, output in enumerate(byte_outputs)
    )
    maximum = int(contract["semantics"]["max_bits"])
    return (
        f"module {module}(\n"
        + ",\n".join(port_lines)
        + "\n);\n"
        f"    logic [{window_width - 1}:0] window_i;\n"
        f"    logic [{window_width - 1}:0] window_out_i;\n"
        "    logic [32:0] write_sum_i;\n"
        "    integer i;\n"
        "\n"
        "    always_comb begin\n"
        f"        window_i = {{{concatenation}}};\n"
        "        window_out_i = window_i;\n"
        f"        for (i = 0; i < {maximum}; i = i + 1) begin\n"
        "            if (i < nbits)\n"
        f"                window_out_i[{window_width - 1} - int'(write_ptr[2:0]) - i] = "
        "data[int'(nbits) - 1 - i];\n"
        "        end\n"
        + byte_assignments
        + f"        fullness_out = fullness + {{{32 - nbits_width}'d0, nbits}};\n"
        f"        write_sum_i = {{1'b0, write_ptr}} + {{{33 - nbits_width}'d0, nbits}};\n"
        "        if (write_sum_i >= {1'b0, fifo_size})\n"
        "            write_ptr_out = write_sum_i[31:0] - fifo_size;\n"
        "        else\n"
        "            write_ptr_out = write_sum_i[31:0];\n"
        "        if (fullness_out > max_fullness)\n"
        "            max_fullness_out = fullness_out;\n"
        "        else\n"
        "            max_fullness_out = max_fullness;\n"
        "    end\n"
        "endmodule\n"
    )


def render_scalar_record_next_state_rtl(contract: dict[str, Any]) -> str:
    semantics = contract["semantics"]
    bindings = semantics["bindings"]
    scalar_inputs = bindings["scalar_input_ports"]
    config_ports = bindings["config_ports"]
    state_inputs = bindings["state_input_ports"]
    scalar_outputs = bindings["scalar_output_ports"]
    state_outputs = bindings["state_output_ports"]
    required_config = {
        "bits_per_pixel", "final_offset", "first_line_bpg_ofs",
        "initial_scale_value", "initial_xmit_delay", "nfl_bpg_offset",
        "nsl_bpg_offset", "scale_decrement_interval",
        "scale_increment_interval", "second_line_bpg_ofs",
        "second_line_ofs_adj", "slice_bpg_offset",
    }
    required_state_inputs = {
        "currentScale", "pixelCount", "pixelsInGroup", "prevPixelCount",
        "rcOffsetClampEnable", "rcXformOffset", "scaleAdjustCounter",
        "scaleIncrementStart", "secondOffsetApplied", "throttleFrac",
    }
    required_state_outputs = {
        "currentScale", "prevPixelCount", "rcOffsetClampEnable",
        "rcXformOffset", "scaleAdjustCounter", "scaleIncrementStart",
        "secondOffsetApplied", "throttleFrac",
    }
    if (
        set(config_ports) != required_config
        or set(state_inputs) != required_state_inputs
        or set(state_outputs) != required_state_outputs
    ):
        raise RuntimeError("scalar record transition fields do not match the frozen RC shape")

    vertical_parameter = str(bindings["vertical_position_parameter"])
    group_parameter = str(bindings["group_count_parameter"])
    scale_parameter = str(bindings["scale_output_parameter"])
    bpg_parameter = str(bindings["bpg_offset_output_parameter"])
    vpos = scalar_inputs[vertical_parameter]
    group_count = scalar_inputs[group_parameter]
    scale_result = scalar_outputs[scale_parameter]
    bpg_result = scalar_outputs[bpg_parameter]
    cfg = lambda field: config_ports[field]
    state = lambda field: state_inputs[field]
    nxt = lambda field: state_outputs[field]
    constants = semantics["constants"]
    fractional_bits = int(constants["offset_fractional_bits"])
    scale_binary_point = int(constants["rc_scale_binary_point"])
    unity_scale = 1 << scale_binary_point
    fractional_mask = (1 << fractional_bits) - 1
    port_lines = []
    for port in contract["interface"]["ports"]:
        direction = str(port["direction"])
        signed = " signed" if port.get("signed") else ""
        port_lines.append(
            f"    {direction} logic{signed} [31:0] {port['name']}"
        )
    defaults = "".join(
        f"        {state_outputs[field]} = {state_inputs[field]};\n"
        for field in sorted(state_outputs)
    )
    module = safe_identifier(contract["contract_id"])
    return (
        f"module {module}(\n"
        + ",\n".join(port_lines)
        + "\n);\n"
        "    logic signed [31:0] current_bpg_target_i;\n"
        "    logic signed [31:0] increment_i;\n"
        "    logic signed [31:0] num_pixels_i;\n"
        "\n"
        "    always_comb begin\n"
        + defaults
        + "        current_bpg_target_i = 32'sd0;\n"
        "        increment_i = 32'sd0;\n"
        "        num_pixels_i = 32'sd0;\n"
        f"        if ({group_count} == 0) begin\n"
        f"            {nxt('currentScale')} = {cfg('initial_scale_value')};\n"
        f"            {nxt('scaleAdjustCounter')} = 32'sd1;\n"
        f"        end else if (({vpos} == 0) && "
        f"({state('currentScale')} > 32'sd{unity_scale})) begin\n"
        f"            {nxt('scaleAdjustCounter')} = {state('scaleAdjustCounter')} + 1;\n"
        f"            if ({nxt('scaleAdjustCounter')} >= {cfg('scale_decrement_interval')}) begin\n"
        f"                {nxt('scaleAdjustCounter')} = 0;\n"
        f"                {nxt('currentScale')} = {state('currentScale')} - 1;\n"
        "            end\n"
        f"        end else if ({state('scaleIncrementStart')} != 0) begin\n"
        f"            {nxt('scaleAdjustCounter')} = {state('scaleAdjustCounter')} + 1;\n"
        f"            if ({nxt('scaleAdjustCounter')} >= {cfg('scale_increment_interval')}) begin\n"
        f"                {nxt('scaleAdjustCounter')} = 0;\n"
        f"                {nxt('currentScale')} = {state('currentScale')} + 1;\n"
        "            end\n"
        "        end\n"
        f"        if ({vpos} == 0) begin\n"
        f"            current_bpg_target_i = {cfg('first_line_bpg_ofs')};\n"
        f"            increment_i = -({cfg('first_line_bpg_ofs')} <<< {fractional_bits});\n"
        "        end else begin\n"
        f"            current_bpg_target_i = -({cfg('nfl_bpg_offset')} >>> {fractional_bits});\n"
        f"            increment_i = {cfg('nfl_bpg_offset')};\n"
        "        end\n"
        f"        if ({vpos} == 1) begin\n"
        f"            current_bpg_target_i = current_bpg_target_i + {cfg('second_line_bpg_ofs')};\n"
        f"            increment_i = increment_i - ({cfg('second_line_bpg_ofs')} <<< {fractional_bits});\n"
        f"            if ({state('secondOffsetApplied')} == 0) begin\n"
        f"                {nxt('secondOffsetApplied')} = 1;\n"
        f"                {nxt('rcXformOffset')} = {state('rcXformOffset')} - {cfg('second_line_ofs_adj')};\n"
        "            end\n"
        "        end else begin\n"
        f"            current_bpg_target_i = current_bpg_target_i - ({cfg('nsl_bpg_offset')} >>> {fractional_bits});\n"
        f"            increment_i = increment_i + {cfg('nsl_bpg_offset')};\n"
        "        end\n"
        f"        if ({state('pixelCount')} < {cfg('initial_xmit_delay')}) begin\n"
        f"            if ({state('pixelCount')} == 0)\n"
        f"                num_pixels_i = {state('pixelsInGroup')};\n"
        "            else\n"
        f"                num_pixels_i = {state('pixelCount')} - {state('prevPixelCount')};\n"
        f"            if (({cfg('initial_xmit_delay')} - {state('pixelCount')}) < num_pixels_i)\n"
        f"                num_pixels_i = {cfg('initial_xmit_delay')} - {state('pixelCount')};\n"
        f"            increment_i = increment_i - (({cfg('bits_per_pixel')} * num_pixels_i) <<< {fractional_bits - 4});\n"
        "        end else begin\n"
        f"            if (({cfg('scale_increment_interval')} != 0) && "
        f"({state('scaleIncrementStart')} == 0) && ({vpos} > 0) && "
        f"({state('rcXformOffset')} > 0)) begin\n"
        f"                {nxt('currentScale')} = 9;\n"
        f"                {nxt('scaleAdjustCounter')} = 0;\n"
        f"                {nxt('scaleIncrementStart')} = 1;\n"
        "            end\n"
        "        end\n"
        f"        {nxt('prevPixelCount')} = {state('pixelCount')};\n"
        f"        current_bpg_target_i = current_bpg_target_i - ({cfg('slice_bpg_offset')} >>> {fractional_bits});\n"
        f"        increment_i = increment_i + {cfg('slice_bpg_offset')};\n"
        f"        {nxt('throttleFrac')} = {state('throttleFrac')} + increment_i;\n"
        f"        {nxt('rcXformOffset')} = {nxt('rcXformOffset')} + ({nxt('throttleFrac')} >>> {fractional_bits});\n"
        f"        {nxt('throttleFrac')} = {nxt('throttleFrac')} & 32'h{fractional_mask:08x};\n"
        f"        if ({nxt('rcXformOffset')} < {cfg('final_offset')})\n"
        f"            {nxt('rcOffsetClampEnable')} = 1;\n"
        f"        if (({nxt('rcOffsetClampEnable')} != 0) && ({nxt('rcXformOffset')} > {cfg('final_offset')}))\n"
        f"            {nxt('rcXformOffset')} = {cfg('final_offset')};\n"
        f"        {scale_result} = {nxt('currentScale')};\n"
        f"        {bpg_result} = current_bpg_target_i;\n"
        "    end\n"
        "endmodule\n"
    )


def render_scalar_record_memory_rtl(contract: dict[str, Any]) -> str:
    semantics = contract["semantics"]
    bindings = semantics["bindings"]
    config_ports = bindings["config_ports"]
    state_inputs = bindings["state_input_ports"]
    state_outputs = bindings["state_output_ports"]
    memory_ports = bindings["memory_write_ports"]
    required_config = {"bits_per_pixel", "chunk_size", "vbr_enable"}
    required_state_inputs = {
        "bitsClamped", "bpgFracAccum", "bufferFullness", "chunkCount",
        "chunkPixelTimes", "isEncoder", "numBitsChunk", "sliceWidth",
    }
    required_state_outputs = {
        "bitsClamped", "bpgFracAccum", "bufferFullness", "chunkCount",
        "chunkPixelTimes", "numBitsChunk",
    }
    if (
        set(config_ports) != required_config
        or set(state_inputs) != required_state_inputs
        or set(state_outputs) != required_state_outputs
        or set(memory_ports) != {"enable", "index", "value"}
    ):
        raise RuntimeError(
            "scalar record memory transition fields do not match the frozen chunk shape"
        )
    port_lines = []
    for port in contract["interface"]["ports"]:
        width = int(port["width"])
        width_text = "" if width == 1 else f" [{width - 1}:0]"
        signed = " signed" if port.get("signed") else ""
        port_lines.append(
            f"    {port['direction']} logic{signed}{width_text} {port['name']}"
        )
    cfg = lambda field: config_ports[field]
    state = lambda field: state_inputs[field]
    nxt = lambda field: state_outputs[field]
    write_enable = memory_ports["enable"]
    write_index = memory_ports["index"]
    write_value = memory_ports["value"]
    defaults = "".join(
        f"        {state_outputs[field]} = {state_inputs[field]};\n"
        for field in sorted(state_outputs)
    )
    module = safe_identifier(contract["contract_id"])
    return (
        f"module {module}(\n"
        + ",\n".join(port_lines)
        + "\n);\n"
        "    logic signed [31:0] removal_bits_i;\n"
        "    logic signed [31:0] size_i;\n"
        "    logic signed [31:0] adjustment_bits_i;\n"
        "\n"
        "    always_comb begin\n"
        + defaults
        + f"        {write_enable} = 1'b0;\n"
        + f"        {write_index} = {state('chunkCount')};\n"
        + f"        {write_value} = 32'sd0;\n"
        + "        removal_bits_i = 32'sd0;\n"
        + "        size_i = 32'sd0;\n"
        + "        adjustment_bits_i = 32'sd0;\n"
        + f"        {nxt('bpgFracAccum')} = {state('bpgFracAccum')} + "
        + f"({cfg('bits_per_pixel')} & 32'sd15);\n"
        + f"        removal_bits_i = ({cfg('bits_per_pixel')} >>> 4) + "
        + f"({nxt('bpgFracAccum')} >>> 4);\n"
        + f"        {nxt('bufferFullness')} = {state('bufferFullness')} - removal_bits_i;\n"
        + f"        {nxt('numBitsChunk')} = {state('numBitsChunk')} + removal_bits_i;\n"
        + f"        {nxt('bpgFracAccum')} = {nxt('bpgFracAccum')} & 32'sd15;\n"
        + f"        {nxt('chunkPixelTimes')} = {state('chunkPixelTimes')} + 32'sd1;\n"
        + f"        if ({nxt('chunkPixelTimes')} >= {state('sliceWidth')}) begin\n"
        + f"            if ({cfg('vbr_enable')} != 0) begin\n"
        + f"                size_i = ({nxt('numBitsChunk')} - "
        + f"{state('bitsClamped')} + 32'sd7) / 32'sd8;\n"
        + f"                adjustment_bits_i = size_i * 32'sd8 - "
        + f"({nxt('numBitsChunk')} - {state('bitsClamped')});\n"
        + f"                {nxt('bufferFullness')} = {nxt('bufferFullness')} - adjustment_bits_i;\n"
        + f"                {nxt('bitsClamped')} = 32'sd0;\n"
        + f"                if ({state('isEncoder')} != 0) begin\n"
        + f"                    {write_enable} = 1'b1;\n"
        + f"                    {write_value} = size_i;\n"
        + "                end\n"
        + "            end else begin\n"
        + f"                adjustment_bits_i = {cfg('chunk_size')} * 32'sd8 - "
        + f"{nxt('numBitsChunk')};\n"
        + f"                {nxt('bufferFullness')} = {nxt('bufferFullness')} - adjustment_bits_i;\n"
        + "            end\n"
        + f"            {nxt('bpgFracAccum')} = 32'sd0;\n"
        + f"            {nxt('numBitsChunk')} = 32'sd0;\n"
        + f"            {nxt('chunkCount')} = {state('chunkCount')} + 32'sd1;\n"
        + f"            {nxt('chunkPixelTimes')} = 32'sd0;\n"
        + "        end\n"
        + "    end\n"
        + "endmodule\n"
    )


def render_bounded_mux_refill_rtl(contract: dict[str, Any]) -> str:
    semantics = contract["semantics"]
    constants = semantics["constants"]
    bindings = semantics["bindings"]
    max_ssps = int(constants["max_ssps"])
    max_mux_bytes = int(constants["max_mux_bytes"])
    stream_window_bytes = int(constants["stream_window_bytes"])
    max_fifo_bytes = int(constants["max_fifo_bytes"])
    stream_ports = list(bindings["stream_byte_ports"])
    max_se_ports = list(bindings["max_se_size_ports"])
    lanes = list(bindings["fifo_lanes"])
    if (
        max_ssps != 4
        or max_mux_bytes != 8
        or stream_window_bytes != 33
        or max_fifo_bytes != 17
        or len(stream_ports) != stream_window_bytes
        or len(max_se_ports) != max_ssps
        or len(lanes) != max_ssps
        or list(constants["mux_word_values"]) != [48, 64]
    ):
        raise RuntimeError("bounded mux refill requires the frozen 4-lane 48/64-bit shape")
    port_lines = []
    for port in contract["interface"]["ports"]:
        width = int(port["width"])
        width_text = "" if width == 1 else f" [{width - 1}:0]"
        signed = " signed" if port.get("signed") else ""
        port_lines.append(
            f"    {port['direction']} logic{signed}{width_text} {port['name']}"
        )
    post_in = str(bindings["post_mux_num_bits_port"])
    post_out = str(bindings["post_mux_num_bits_output_port"])
    num_ssps = str(bindings["num_ssps_port"])
    mux_word_size = str(bindings["mux_word_size_port"])
    defaults = [
        "        domain_valid = 1'b1;",
        f"        {post_out} = {post_in};",
    ]
    validation: list[str] = []
    lane_blocks: list[str] = []
    final_assignments: list[str] = []
    declarations: list[str] = []
    for lane_index, lane in enumerate(lanes):
        byte_inputs = list(lane["data_input_ports"])
        byte_outputs = list(lane["data_output_ports"])
        if len(byte_inputs) != max_fifo_bytes or len(byte_outputs) != max_fifo_bytes:
            raise RuntimeError("bounded mux refill lane memory extent is incomplete")
        data_work = f"fifo_{lane_index}_data_work_i"
        fullness_work = f"fifo_{lane_index}_fullness_work_i"
        write_ptr_work = f"fifo_{lane_index}_write_ptr_work_i"
        max_fullness_work = f"fifo_{lane_index}_max_fullness_work_i"
        declarations.extend([
            f"    logic [{max_fifo_bytes * 8 - 1}:0] {data_work};",
            f"    logic [31:0] {fullness_work};",
            f"    logic [31:0] {write_ptr_work};",
            f"    logic [31:0] {max_fullness_work};",
        ])
        defaults.extend([
            f"        {data_work} = {{{', '.join(byte_inputs)}}};",
            f"        {fullness_work} = {lane['fullness_port']};",
            f"        {write_ptr_work} = {lane['write_ptr_port']};",
            f"        {max_fullness_work} = {lane['max_fullness_port']};",
            f"        {lane['size_output_port']} = {lane['size_port']};",
            f"        {lane['fullness_output_port']} = {lane['fullness_port']};",
            f"        {lane['read_ptr_output_port']} = {lane['read_ptr_port']};",
            f"        {lane['write_ptr_output_port']} = {lane['write_ptr_port']};",
            f"        {lane['max_fullness_output_port']} = {lane['max_fullness_port']};",
            f"        {lane['byte_ctr_output_port']} = {lane['byte_ctr_port']};",
            *[f"        {port} = 8'd0;" for port in byte_outputs],
        ])
        validation.extend([
            f"        if (({lane['size_port']} == 0) || "
            f"({lane['size_port']}[2:0] != 0) || "
            f"({lane['size_port']} > 32'd{max_fifo_bytes * 8}) || "
            f"({lane['write_ptr_port']} >= {lane['size_port']}))",
            "            domain_valid = 1'b0;",
            f"        if (({num_ssps} > 3'd{lane_index}) && "
            f"({lane['fullness_port']} < {max_se_ports[lane_index]}) && "
            f"({{1'b0, {lane['fullness_port']}}} + {{26'd0, {mux_word_size}}} > "
            f"{{1'b0, {lane['size_port']}}}))",
            "            domain_valid = 1'b0;",
        ])
        byte_steps = []
        for byte_index, output in enumerate(byte_outputs):
            if byte_index >= max_mux_bytes:
                break
            bit_steps: list[str] = []
            for bit_index in range(8):
                bit_steps.extend([
                    f"                {data_work}[{max_fifo_bytes * 8 - 1} - "
                    f"{write_ptr_work}] = data_byte_i[{7 - bit_index}];",
                    f"                if (({write_ptr_work} + 32'd1) >= "
                    f"{lane['size_port']})",
                    f"                    {write_ptr_work} = 32'd0;",
                    "                else",
                    f"                    {write_ptr_work} = {write_ptr_work} + 32'd1;",
                ])
            byte_steps.extend([
                f"            if (mux_bytes_i > 4'd{byte_index}) begin",
                f"                data_byte_i = aligned_window_i["
                f"{stream_window_bytes * 8 - 1} - (stream_index_i * 8) -: 8];",
                *bit_steps,
                f"                {fullness_work} = {fullness_work} + 32'd8;",
                f"                if ({fullness_work} > {max_fullness_work})",
                f"                    {max_fullness_work} = {fullness_work};",
                "                stream_index_i = stream_index_i + 6'd1;",
                "            end",
            ])
        lane_blocks.extend([
            f"        if (domain_valid && ({num_ssps} > 3'd{lane_index}) && "
            f"({lane['fullness_port']} < {max_se_ports[lane_index]})) begin",
            *byte_steps,
            "        end",
        ])
        final_assignments.extend([
            f"        {lane['fullness_output_port']} = {fullness_work};",
            f"        {lane['write_ptr_output_port']} = {write_ptr_work};",
            f"        {lane['max_fullness_output_port']} = {max_fullness_work};",
            *[
                f"        {output} = {data_work}["
                f"{max_fifo_bytes * 8 - 1 - byte_index * 8} -: 8];"
                for byte_index, output in enumerate(byte_outputs)
            ],
        ])
    window_width = stream_window_bytes * 8
    module = safe_identifier(contract["contract_id"])
    return (
        f"module {module}(\n"
        + ",\n".join(port_lines)
        + "\n);\n"
        + f"    logic [{window_width - 1}:0] stream_window_i;\n"
        + f"    logic [{window_width - 1}:0] aligned_window_i;\n"
        + "    logic [3:0] mux_bytes_i;\n"
        + "    logic [5:0] stream_index_i;\n"
        + "    logic [7:0] data_byte_i;\n"
        + "\n".join(declarations)
        + "\n"
        + "\n"
        + "    always_comb begin\n"
        + f"        stream_window_i = {{{', '.join(stream_ports)}}};\n"
        + f"        aligned_window_i = stream_window_i << {post_in}[2:0];\n"
        + "        mux_bytes_i = 4'd0;\n"
        + f"        if ({mux_word_size} == 7'd48) mux_bytes_i = 4'd6;\n"
        + f"        else if ({mux_word_size} == 7'd64) mux_bytes_i = 4'd8;\n"
        + "        stream_index_i = 6'd0;\n"
        + "        data_byte_i = 8'd0;\n"
        + "\n".join(defaults)
        + "\n"
        + f"        if (({mux_word_size} != 7'd48) && ({mux_word_size} != 7'd64))\n"
        + "            domain_valid = 1'b0;\n"
        + f"        if ({num_ssps} > 3'd{max_ssps}) domain_valid = 1'b0;\n"
        + "\n".join(validation)
        + "\n"
        + "\n".join(lane_blocks)
        + "\n"
        + f"        {post_out} = {post_in} + "
        + "{23'd0, stream_index_i, 3'b000};\n"
        + "\n".join(final_assignments)
        + "\n"
        + "    end\n"
        + "endmodule\n"
    )


def render_bounded_flatness_state_rtl(contract: dict[str, Any]) -> str:
    semantics = contract["semantics"]
    constants = semantics["constants"]
    bindings = semantics["bindings"]
    scalar_ports = bindings["scalar_input_ports"]
    config_ports = bindings["config_ports"]
    state_ports = bindings["state_input_ports"]
    state_outputs = bindings["state_output_ports"]
    groups = int(constants["groups_per_supergroup"])
    components = int(constants["component_count"])
    taps_per_component = int(constants["taps_per_component"])
    if groups != 4 or components != 4 or taps_per_component != 7:
        raise RuntimeError("flatness state transition requires the frozen 4x4x7 shape")
    dependencies = {str(item["role"]): item for item in contract.get("dependencies", [])}
    if set(dependencies) != {"flatness_interval", "original_window"}:
        raise RuntimeError("flatness state transition RTL dependencies are incomplete")
    repo_root = pathlib.Path(__file__).resolve().parent.parent
    dependency_sources = []
    for role in ("flatness_interval", "original_window"):
        item = dependencies[role]
        path = repo_root / "library" / str(item["module_file"])
        if file_hash(path) != str(item["module_sha256"]):
            raise RuntimeError(f"accepted dependency changed before render: {role}")
        dependency_sources.append(path.read_text(encoding="utf-8").rstrip() + "\n")
    interval_module = str(dependencies["flatness_interval"]["module"])
    window_module = str(dependencies["original_window"]["module"])
    hpos = scalar_ports[str(bindings["horizontal_position_parameter"])]
    qp = scalar_ports[str(bindings["qp_parameter"])]
    ignored = scalar_ports[str(bindings["ignored_parameter"])]
    cfg = lambda field: config_ports[field]
    state = lambda field: state_ports[field]
    nxt = lambda field: state_outputs[field]
    tap = lambda call, component, index: (
        f"orig_call_{call}_c{component}_{index}"
    )
    port_lines = []
    for port in contract["interface"]["ports"]:
        width = int(port["width"])
        width_text = "" if width == 1 else f" [{width - 1}:0]"
        signed = " signed" if port.get("signed") else ""
        port_lines.append(
            f"    {port['direction']} logic{signed}{width_text} {port['name']}"
        )
    interval_instance = (
        f"    {interval_module} u_flatness_interval(\n"
        f"        .qp({qp}[4:0]),\n"
        f"        .flatness_min_qp({cfg('flatness_min_qp')}[4:0]),\n"
        f"        .flatness_max_qp({cfg('flatness_max_qp')}[4:0]),\n"
        "        .return_value(flatness_sent_i)\n"
        "    );\n"
    )
    window_instances = []
    for call in range(groups):
        tap_connections = []
        for component in range(components):
            for index in range(taps_per_component):
                tap_connections.append(
                    f"        .orig_{component}_{index}({tap(call, component, index)})"
                )
        connections = [
            f"        .hPos(call_h_{call}_i[15:0])",
            f"        .bits_per_component({cfg('bits_per_component')}[4:0])",
            f"        .primary_qp({state('primaryQp')}[4:0])",
            f"        .num_components({state('numComponents')}[2:0])",
            f"        .slice_width({state('sliceWidth')}[15:0])",
            f"        .flatness_det_thresh({cfg('flatness_det_thresh')}[9:0])",
            f"        .somewhat_flat_qp_delta({cfg('somewhat_flat_qp_delta')}[2:0])",
            f"        .native_420({cfg('native_420')}[0])",
            f"        .dsc_version_minor({cfg('dsc_version_minor')}[1:0])",
            f"        .cpnt_bit_depth_0({state('cpntBitDepth[0]')}[4:0])",
            f"        .cpnt_bit_depth_1({state('cpntBitDepth[1]')}[4:0])",
            *tap_connections,
            f"        .return_value(flatness_raw_{call}_i)",
        ]
        window_instances.append(
            f"    {window_module} u_original_window_{call}(\n"
            + ",\n".join(connections)
            + "\n    );\n"
            + f"    assign call_h_{call}_i = {hpos} + "
            + f"({state('pixelsInGroup')} * 32'sd{call + 1});\n"
            + f"    assign flatness_result_{call}_i = "
            + f"((call_h_{call}_i + 32'sd1) >= {state('sliceWidth')}) "
            + f"? 2'd0 : flatness_raw_{call}_i;\n"
        )
    declarations = [
        "    logic flatness_sent_i;",
        "    logic found_i;",
        "    logic ignored_new_quant_i;",
        *[
            f"    logic signed [31:0] call_h_{call}_i;\n"
            f"    logic [1:0] flatness_raw_{call}_i;\n"
            f"    logic [1:0] flatness_result_{call}_i;"
            for call in range(groups)
        ],
    ]
    defaults = "".join(
        f"        {state_outputs[field]} = {state_ports[field]};\n"
        for field in sorted(state_outputs)
    )
    priority_stages = []
    for call in range(groups):
        priority_stages.extend([
            "                if (!found_i) begin",
            f"                    if (({nxt('prevIsFlat')} == 0) && "
            f"(flatness_result_{call}_i != 0)) begin",
            f"                        {nxt('prevFirstFlat')} = 32'sd{call};",
            f"                        {nxt('prevFlatnessType')} = "
            f"{{30'd0, flatness_result_{call}_i}} - 32'sd1;",
            "                        found_i = 1'b1;",
            "                    end else begin",
            f"                        {nxt('prevIsFlat')} = "
            f"{{30'd0, flatness_result_{call}_i}};",
            "                    end",
            "                end",
        ])
    module = safe_identifier(contract["contract_id"])
    top = (
        f"module {module}(\n"
        + ",\n".join(port_lines)
        + "\n);\n"
        + "\n".join(declarations)
        + "\n\n"
        + interval_instance
        + "\n".join(window_instances)
        + "\n    always_comb begin\n"
        + defaults
        + "        found_i = 1'b0;\n"
        + f"        ignored_new_quant_i = ^{ignored};\n"
        + f"        if ({state('isEncoder')} != 0) begin\n"
        + f"            if (flatness_sent_i && ({state('groupCount')}[1:0] == 2'd3)) begin\n"
        + f"                {nxt('prevIsFlat')} = ({state('firstFlat')} >= 0) ? 32'sd1 : 32'sd0;\n"
        + f"                {nxt('prevFirstFlat')} = -32'sd1;\n"
        + "\n".join(priority_stages)
        + "\n"
        + f"            end else if (!flatness_sent_i && ({state('groupCount')}[1:0] == 2'd3)) begin\n"
        + f"                {nxt('prevFirstFlat')} = -32'sd1;\n"
        + f"            end else if ({state('groupCount')}[1:0] == 2'd0) begin\n"
        + f"                {nxt('firstFlat')} = {state('prevFirstFlat')};\n"
        + f"                {nxt('flatnessType')} = {state('prevFlatnessType')};\n"
        + "            end\n"
        + f"            {nxt('origIsFlat')} = 32'sd0;\n"
        + f"            if (({nxt('firstFlat')} >= 0) && "
        + f"({state('groupCount')}[1:0] == {nxt('firstFlat')}[1:0]))\n"
        + f"                {nxt('origIsFlat')} = 32'sd1;\n"
        + "        end\n"
        + f"        if ({cfg('dsc_version_minor')} == 32'sd1) begin\n"
        + f"            if (({nxt('origIsFlat')} != 0) && "
        + f"({state('primaryQp')} < {cfg('last_range_max_qp')})) begin\n"
        + f"                if (({nxt('flatnessType')} == 0) || "
        + f"({state('primaryQp')} < {cfg('somewhat_flat_qp_thresh')})) begin\n"
        + f"                    if ({state('stQp')} > {cfg('somewhat_flat_qp_delta')})\n"
        + f"                        {nxt('stQp')} = {state('stQp')} - {cfg('somewhat_flat_qp_delta')};\n"
        + f"                    else {nxt('stQp')} = 32'sd0;\n"
        + "                end else begin\n"
        + f"                    {nxt('stQp')} = {cfg('very_flat_qp')};\n"
        + "                end\n"
        + "            end\n"
        + "        end else begin\n"
        + f"            if ({hpos} >= ({state('sliceWidth')} - 32'sd1)) begin\n"
        + f"                {nxt('origIsFlat')} = 32'sd1;\n"
        + f"                {nxt('flatnessType')} = 32'sd1;\n"
        + "            end\n"
        + f"            if (({nxt('origIsFlat')} != 0) && "
        + f"({state('primaryQp')} < {cfg('last_range_max_qp')})) begin\n"
        + f"                if (({nxt('flatnessType')} == 0) || "
        + f"({state('primaryQp')} < {cfg('somewhat_flat_qp_thresh')})) begin\n"
        + f"                    if ({state('stQp')} > {cfg('somewhat_flat_qp_delta')})\n"
        + f"                        {nxt('stQp')} = {state('stQp')} - {cfg('somewhat_flat_qp_delta')};\n"
        + f"                    else {nxt('stQp')} = 32'sd0;\n"
        + f"                    if ({state('prevQp')} > {cfg('somewhat_flat_qp_delta')})\n"
        + f"                        {nxt('prevQp')} = {state('prevQp')} - {cfg('somewhat_flat_qp_delta')};\n"
        + f"                    else {nxt('prevQp')} = 32'sd0;\n"
        + "                end else begin\n"
        + f"                    {nxt('stQp')} = {cfg('very_flat_qp')};\n"
        + f"                    {nxt('prevQp')} = {cfg('very_flat_qp')};\n"
        + "                end\n"
        + "            end\n"
        + "        end\n"
        + "    end\n"
        + "endmodule\n"
    )
    return "\n".join(dependency_sources) + "\n" + top


def render_bounded_line_write_rtl(contract: dict[str, Any]) -> str:
    constants = contract["semantics"]["constants"]
    bindings = contract["semantics"]["bindings"]
    max_pixels = int(constants["max_pixels"])
    components = int(constants["component_count"])
    padding_left = int(constants["padding_left"])
    pixel_ports = bindings["pixel_ports"]
    index_ports = bindings["write_index_ports"]
    enable_ports = bindings["write_enable_ports"]
    value_ports = bindings["write_value_ports"]
    if (
        (max_pixels, components, padding_left) != (6, 4, 5)
        or len(pixel_ports) != max_pixels
        or len(index_ports) != max_pixels
        or len(enable_ports) != max_pixels
        or len(value_ports) != max_pixels
    ):
        raise RuntimeError("bounded line write requires the frozen 6x4 shape")
    port_lines = []
    for port in contract["interface"]["ports"]:
        width = int(port["width"])
        width_text = "" if width == 1 else f" [{width - 1}:0]"
        signed = " signed" if port.get("signed") else ""
        port_lines.append(
            f"    {port['direction']} logic{signed}{width_text} {port['name']}"
        )
    body = [
        f"        {index_ports[pixel]} = state_hpos - state_pixels_in_group + "
        f"32'sd{1 + padding_left + pixel};"
        for pixel in range(max_pixels)
    ]
    for pixel in range(max_pixels):
        for component in range(components):
            body.extend([
                f"        {enable_ports[pixel][component]} = 1'b0;",
                f"        {value_ports[pixel][component]} = 32'sd0;",
                f"        if ((state_ich_selected != 0) && "
                f"(state_ich_indices > 32'sd{pixel}) && "
                f"(state_num_components > 32'sd{component})) begin",
                f"            {enable_ports[pixel][component]} = 1'b1;",
                f"            {value_ports[pixel][component]} = "
                f"$signed({pixel_ports[pixel][component]});",
                "        end",
            ])
    module = safe_identifier(contract["contract_id"])
    return (
        f"module {module}(\n"
        + ",\n".join(port_lines)
        + "\n);\n"
        + "    always_comb begin\n"
        + "\n".join(body)
        + "\n    end\n"
        + "endmodule\n"
    )


def render_bounded_history_update_rtl(contract: dict[str, Any]) -> str:
    semantics = contract["semantics"]
    constants = semantics["constants"]
    bindings = semantics["bindings"]
    entries = int(constants["ich_entries"])
    components = int(constants["component_count"])
    reserved_nonfirst = int(constants["reserved_nonfirst"])
    if (entries, components, reserved_nonfirst) != (32, 4, 25):
        raise RuntimeError("bounded history update requires the frozen 4x32 shape")
    dependencies = {
        str(item["role"]): item for item in contract.get("dependencies", [])
    }
    if set(dependencies) != {"history_lookup_branch_guard"}:
        raise RuntimeError("bounded history update dependency is incomplete")
    dependency = dependencies["history_lookup_branch_guard"]
    repo_root = pathlib.Path(__file__).resolve().parent.parent
    dependency_path = pathlib.Path(str(dependency["module_file"]))
    if not dependency_path.is_absolute():
        dependency_path = repo_root / dependency_path
    if file_hash(dependency_path) != str(dependency["module_sha256"]):
        raise RuntimeError("history lookup dependency changed before render")
    dependency_source = dependency_path.read_text(encoding="utf-8").rstrip() + "\n"
    dependency_module = str(dependency["module"])

    scalar = bindings["scalar_ports"]
    recon_ports = list(bindings["recon_ports"])
    valid_inputs = list(bindings["valid_input_ports"])
    pixel_inputs = [list(row) for row in bindings["pixel_input_ports"]]
    valid_outputs = list(bindings["valid_output_ports"])
    pixel_outputs = [list(row) for row in bindings["pixel_output_ports"]]
    if (
        len(recon_ports) != components
        or len(valid_inputs) != entries
        or len(valid_outputs) != entries
        or any(len(row) != entries for row in pixel_inputs)
        or any(len(row) != entries for row in pixel_outputs)
    ):
        raise RuntimeError("bounded history update port extents are incomplete")
    port_lines = []
    for port in contract["interface"]["ports"]:
        width = int(port["width"])
        width_text = "" if width == 1 else f" [{width - 1}:0]"
        signed = " signed" if port.get("signed") else ""
        port_lines.append(
            f"    {port['direction']} logic{signed}{width_text} {port['name']}"
        )

    lookup_wires = [
        f"    logic [31:0] lookup_{entry}_{component}_i;"
        for entry in range(entries) for component in range(components)
    ]
    lookup_instances = []
    for entry in range(entries):
        connections = [
            f"        .native_420({scalar['cfg_native_420']}[0])",
            "        .native_422(1'b0)",
            f"        .entry(5'd{entry})",
            "        .first_line_flag(first_line_i)",
            f"        .is_odd_line({scalar['vPos']}[0])",
            f"        .num_components({scalar['numComponents']}[2:0])",
            *[
                f"        .history_{component}({pixel_inputs[component][entry]})"
                for component in range(components)
            ],
            *[
                f"        .native_base_{component}(32'd0)"
                for component in range(components)
            ],
            *[
                f"        .native_base1_{component}(32'd0)"
                for component in range(components)
            ],
            *[
                f"        .simple_tap_{component}(32'd0)"
                for component in range(components - 1)
            ],
            *[
                f"        .p_{component}_out(lookup_{entry}_{component}_i)"
                for component in range(components)
            ],
        ]
        lookup_instances.append(
            f"    {dependency_module} u_history_lookup_{entry}(\n"
            + ",\n".join(connections)
            + "\n    );"
        )

    defaults = [
        *[
            f"        {valid_outputs[entry]} = {valid_inputs[entry]};"
            for entry in range(entries)
        ],
        *[
            f"        {pixel_outputs[component][entry]} = "
            f"{pixel_inputs[component][entry]};"
            for component in range(components) for entry in range(entries)
        ],
    ]
    scan_stages = []
    for entry in range(entries):
        matches = " && ".join(
            f"(({scalar['numComponents']} <= 32'sd{component}) || "
            f"(lookup_{entry}_{component}_i == {recon_ports[component]}))"
            for component in range(components)
        )
        scan_stages.extend([
            f"        if (!found_i && (6'd{entry} < reserved_i)) begin",
            f"            if ({valid_inputs[entry]} == 0) begin",
            f"                location_i = 5'd{entry};",
            "                found_i = 1'b1;",
            f"            end else if (active_selection_i && ({matches})) begin",
            f"                location_i = 5'd{entry};",
            "                found_i = 1'b1;",
            "            end",
            "        end",
        ])
    updates = [
        f"        if ({scalar['numComponents']} > 32'sd0) begin",
        f"            {valid_outputs[0]} = 32'sd1;",
    ]
    for entry in range(entries):
        updates.extend([
            f"            if (location_i == 5'd{entry})",
            f"                {valid_outputs[entry]} = 32'sd1;",
        ])
    updates.append("        end")
    for component in range(components):
        updates.extend([
            f"        if ({scalar['numComponents']} > 32'sd{component}) begin",
            f"            {pixel_outputs[component][0]} = {recon_ports[component]};",
        ])
        for entry in range(1, entries):
            updates.extend([
                f"            if (location_i >= 5'd{entry})",
                f"                {pixel_outputs[component][entry]} = "
                f"{pixel_inputs[component][entry - 1]};",
            ])
        updates.append("        end")

    module = safe_identifier(contract["contract_id"])
    top = (
        f"module {module}(\n"
        + ",\n".join(port_lines)
        + "\n);\n"
        + "    logic first_line_i;\n"
        + "    logic active_selection_i;\n"
        + "    logic [5:0] reserved_i;\n"
        + "    logic [4:0] location_i;\n"
        + "    logic found_i;\n"
        + "\n".join(lookup_wires)
        + "\n\n"
        + f"    assign first_line_i = ({scalar['vPos']} == 0) || "
        + f"(({scalar['cfg_native_420']} != 0) && ({scalar['vPos']} == 1));\n"
        + f"    assign active_selection_i = (({scalar['isEncoder']} != 0) && "
        + f"({scalar['ichSelected']} != 0)) || (({scalar['isEncoder']} == 0) && "
        + f"({scalar['prevIchSelected']} != 0));\n"
        + f"    assign reserved_i = first_line_i ? 6'd{entries} : "
        + f"6'd{reserved_nonfirst};\n\n"
        + "\n\n".join(lookup_instances)
        + "\n\n    always_comb begin\n"
        + "\n".join(defaults)
        + "\n        found_i = 1'b0;\n"
        + f"        location_i = first_line_i ? 5'd{entries - 1} : "
        + f"5'd{reserved_nonfirst - 1};\n"
        + "\n".join(scan_stages)
        + "\n"
        + "\n".join(updates)
        + "\n    end\n"
        + "endmodule\n"
    )
    return dependency_source + "\n" + top


def render_bounded_history_caller_rtl(contract: dict[str, Any]) -> str:
    semantics = contract["semantics"]
    constants = semantics["constants"]
    bindings = semantics["bindings"]
    entries = int(constants["ich_entries"])
    components = int(constants["component_count"])
    padding_left = int(constants["padding_left"])
    if (entries, components, padding_left) != (32, 4, 5):
        raise RuntimeError("bounded history caller requires the frozen 4x32 shape")
    dependencies = {
        str(item["role"]): item for item in contract.get("dependencies", [])
    }
    if set(dependencies) != {"history_update"}:
        raise RuntimeError("bounded history caller dependency is incomplete")
    dependency = dependencies["history_update"]
    repo_root = pathlib.Path(__file__).resolve().parent.parent
    module_path = pathlib.Path(str(dependency["module_file"]))
    contract_path = pathlib.Path(str(dependency["contract_file"]))
    if not module_path.is_absolute():
        module_path = repo_root / module_path
    if not contract_path.is_absolute():
        contract_path = repo_root / contract_path
    if (
        file_hash(module_path) != str(dependency["module_sha256"])
        or file_hash(contract_path) != str(dependency["contract_sha256"])
    ):
        raise RuntimeError("bounded history caller dependency changed before render")
    dependency_source = module_path.read_text(encoding="utf-8").rstrip() + "\n"
    dependency_contract = read_json(contract_path)
    child_bindings = dependency_contract["semantics"]["bindings"]
    child_scalar = child_bindings["scalar_ports"]
    child_recon = list(child_bindings["recon_ports"])
    child_valid_inputs = list(child_bindings["valid_input_ports"])
    child_pixel_inputs = [list(row) for row in child_bindings["pixel_input_ports"]]
    child_valid_outputs = list(child_bindings["valid_output_ports"])
    child_pixel_outputs = [list(row) for row in child_bindings["pixel_output_ports"]]
    child_module = str(dependency["module"])

    arguments = bindings["argument_ports"]
    config = bindings["config_ports"]
    state = bindings["state_ports"]
    line_samples = list(bindings["line_sample_ports"])
    valid_inputs = list(bindings["valid_input_ports"])
    pixel_inputs = [list(row) for row in bindings["pixel_input_ports"]]
    valid_outputs = list(bindings["valid_output_ports"])
    pixel_outputs = [list(row) for row in bindings["pixel_output_ports"]]
    hpos = arguments[str(bindings["horizontal_position_parameter"])]
    vpos = arguments[str(bindings["vertical_position_parameter"])]
    if (
        len(line_samples) != components
        or len(valid_inputs) != entries
        or len(valid_outputs) != entries
        or any(len(row) != entries for row in pixel_inputs)
        or any(len(row) != entries for row in pixel_outputs)
        or len(child_valid_inputs) != entries
        or len(child_valid_outputs) != entries
    ):
        raise RuntimeError("bounded history caller port extents are incomplete")
    port_lines = []
    for port in contract["interface"]["ports"]:
        width = int(port["width"])
        width_text = "" if width == 1 else f" [{width - 1}:0]"
        signed = " signed" if port.get("signed") else ""
        port_lines.append(
            f"    {port['direction']} logic{signed}{width_text} {port['name']}"
        )
    child_valid_wires = [f"child_valid_{entry}_i" for entry in range(entries)]
    child_pixel_wires = [
        [f"child_pixel_{component}_{entry}_i" for entry in range(entries)]
        for component in range(components)
    ]
    declarations = [
        "    logic clear_history_i;",
        "    logic update_history_i;",
        "    logic signed [31:0] previous_hpos_i;",
        *[f"    logic signed [31:0] {wire};" for wire in child_valid_wires],
        *[
            f"    logic [31:0] {wire};"
            for row in child_pixel_wires for wire in row
        ],
    ]
    child_connections = [
        f"        .{child_scalar['cfg_native_420']}({config['native_420']})",
        f"        .{child_scalar['hPos']}({state['hPos']})",
        f"        .{child_scalar['vPos']}({state['vPos']})",
        f"        .{child_scalar['numComponents']}({state['numComponents']})",
        f"        .{child_scalar['isEncoder']}({state['isEncoder']})",
        f"        .{child_scalar['ichSelected']}({state['ichSelected']})",
        f"        .{child_scalar['prevIchSelected']}({state['prevIchSelected']})",
        *[
            f"        .{child_recon[component]}({line_samples[component]})"
            for component in range(components)
        ],
        *[
            f"        .{child_valid_inputs[entry]}(clear_history_i ? 32'sd0 : "
            f"{valid_inputs[entry]})"
            for entry in range(entries)
        ],
        *[
            f"        .{child_pixel_inputs[component][entry]}("
            f"{pixel_inputs[component][entry]})"
            for component in range(components) for entry in range(entries)
        ],
        *[
            f"        .{child_valid_outputs[entry]}({child_valid_wires[entry]})"
            for entry in range(entries)
        ],
        *[
            f"        .{child_pixel_outputs[component][entry]}("
            f"{child_pixel_wires[component][entry]})"
            for component in range(components) for entry in range(entries)
        ],
    ]
    defaults = [
        *[
            f"        {valid_outputs[entry]} = {valid_inputs[entry]};"
            for entry in range(entries)
        ],
        *[
            f"        {pixel_outputs[component][entry]} = "
            f"{pixel_inputs[component][entry]};"
            for component in range(components) for entry in range(entries)
        ],
    ]
    clear_outputs = [
        f"            {valid_outputs[entry]} = 32'sd0;"
        for entry in range(entries)
    ]
    update_outputs = [
        *[
            f"            {valid_outputs[entry]} = {child_valid_wires[entry]};"
            for entry in range(entries)
        ],
        *[
            f"            {pixel_outputs[component][entry]} = "
            f"{child_pixel_wires[component][entry]};"
            for component in range(components) for entry in range(entries)
        ],
    ]
    module = safe_identifier(contract["contract_id"])
    top = (
        f"module {module}(\n"
        + ",\n".join(port_lines)
        + "\n);\n"
        + "\n".join(declarations)
        + "\n\n"
        + f"    assign previous_hpos_i = {hpos} - {state['pixelsInGroup']};\n"
        + "    assign update_history_i = previous_hpos_i >= 0;\n"
        + f"    assign clear_history_i = ({hpos} == 0) && (({vpos} == 0) || "
        + f"({config['slice_width']} != {config['pic_width']}));\n\n"
        + f"    {child_module} u_history_update(\n"
        + ",\n".join(child_connections)
        + "\n    );\n\n"
        + "    always_comb begin\n"
        + "\n".join(defaults)
        + "\n        if (clear_history_i) begin\n"
        + "\n".join(clear_outputs)
        + "\n        end\n"
        + "        if (update_history_i) begin\n"
        + "\n".join(update_outputs)
        + "\n        end\n"
        + "    end\nendmodule\n"
    )
    return dependency_source + "\n" + top


def render_bounded_rate_control_decode_rtl(contract: dict[str, Any]) -> str:
    semantics = contract["semantics"]
    constants = semantics["constants"]
    bindings = semantics["bindings"]
    ranges = int(constants["num_buf_ranges"])
    units = int(constants["max_units"])
    samples = int(constants["samples_per_unit"])
    scale_point = int(constants["rc_scale_binary_point"])
    stages = int(constants["max_remove_stages"])
    overflow_422 = int(constants["overflow_avoid_native_422"])
    overflow_other = int(constants["overflow_avoid_other"])
    if (
        ranges, units, samples, scale_point, stages,
        overflow_422, overflow_other
    ) != (15, 4, 3, 3, 3, -224, -172):
        raise RuntimeError("bounded rate-control decoder requires the frozen DSC shape")
    dependencies = contract.get("dependencies", []) or []
    if len(dependencies) != 1 or dependencies[0].get("role") != "remove_one_pixel_bits":
        raise RuntimeError("bounded rate-control dependency is incomplete")
    repo_root = pathlib.Path(__file__).resolve().parent.parent
    dependency = dependencies[0]
    dependency_paths = {}
    for key, hash_key in (
        ("contract_file", "contract_sha256"),
        ("module_file", "module_sha256"),
    ):
        path = pathlib.Path(str(dependency[key]))
        if not path.is_absolute():
            path = repo_root / path
        if file_hash(path) != str(dependency[hash_key]):
            raise RuntimeError("verified rate-control dependency changed before render")
        dependency_paths[key] = path
    dependency_source = dependency_paths["module_file"].read_text(encoding="utf-8").rstrip()
    child_module = str(dependency["module"])

    arguments = {
        str(key): str(value) for key, value in bindings["argument_ports"].items()
    }
    config = {
        str(key): str(value) for key, value in bindings["config_ports"].items()
    }
    state = {
        str(key): str(value) for key, value in bindings["state_ports"].items()
    }
    depth = [str(value) for value in bindings["depth_ports"]]
    predicted = [str(value) for value in bindings["predicted_ports"]]
    rc_size = [str(value) for value in bindings["rc_size_ports"]]
    use_midpoint = [str(value) for value in bindings["use_midpoint_ports"]]
    thresholds = [str(value) for value in bindings["threshold_ports"]]
    range_ports = {
        str(key): [str(value) for value in row]
        for key, row in bindings["range_ports"].items()
    }
    state_outputs = {
        str(key): str(value)
        for key, value in bindings["state_output_ports"].items()
    }
    expected_config = {
        "bits_per_component", "bits_per_pixel", "chunk_size",
        "dsc_version_minor", "initial_xmit_delay", "native_420", "native_422",
        "rc_edge_factor", "rc_model_size", "rc_quant_incr_limit0",
        "rc_quant_incr_limit1", "rc_tgt_offset_hi", "rc_tgt_offset_lo",
        "rcb_bits", "vbr_enable",
    }
    expected_state = {
        "bitSaveMode", "bitsClamped", "bpgFracAccum", "bufferFullness",
        "chunkCount", "chunkPixelTimes", "codedGroupSize", "errorOccurred",
        "firstFlat", "ichSelected", "isEncoder", "mppState", "numBitsChunk",
        "pixelCount", "prevQp", "prevRange", "rcSizeGroup", "sliceWidth",
        "stQp", "unitsPerGroup", "vPos",
    }
    expected_outputs = {
        "bitSaveMode", "bitsClamped", "bpgFracAccum", "bufferFullness",
        "chunkCount", "chunkPixelTimes", "errorOccurred", "mppState",
        "numBitsChunk", "pixelCount", "prevQp", "prevRange",
        "rcSizeGroup", "stQp",
    }
    if (
        len(arguments) != 5 or set(config) != expected_config
        or set(state) != expected_state or set(state_outputs) != expected_outputs
        or len(depth) != 2
        or len(predicted) != units or len(rc_size) != units
        or len(use_midpoint) != units or len(thresholds) != ranges - 1
        or set(range_ports) != {"range_min_qp", "range_max_qp", "range_bpg_offset"}
        or any(len(row) != ranges for row in range_ports.values())
    ):
        raise RuntimeError("bounded rate-control decoder bindings are incomplete")
    throttle = arguments[str(bindings["throttle_parameter"])]
    bpg_offset = arguments[str(bindings["bpg_parameter"])]
    group_count = arguments[str(bindings["group_count_parameter"])]
    scale = arguments[str(bindings["scale_parameter"])]
    group_size = arguments[str(bindings["group_size_parameter"])]

    def select(values: list[str], selector: str) -> str:
        expression = values[-1]
        for index in reversed(range(len(values) - 1)):
            expression = f"(({selector} == 32'sd{index}) ? {values[index]} : {expression})"
        return expression

    port_lines = []
    for port in contract["interface"]["ports"]:
        width = int(port["width"])
        width_text = "" if width == 1 else f" [{width - 1}:0]"
        signed = " signed" if port.get("signed") else ""
        port_lines.append(
            f"    {port['direction']} logic{signed}{width_text} {port['name']}"
        )
    child_state_fields = (
        "bitsclamped", "bpgfracaccum", "bufferfullness", "chunkcount",
        "chunkpixeltimes", "numbitschunk",
    )
    declarations = []
    for stage in range(stages + 1):
        declarations.append(f"    logic signed [31:0] pixelcount_stage_{stage}_i;")
        declarations.extend(
            f"    logic signed [31:0] {field}_stage_{stage}_i;"
            for field in child_state_fields
        )
    for stage in range(stages):
        declarations.extend([
            f"    logic remove_stage_{stage}_i;",
            f"    logic signed [31:0] pixelcount_after_{stage}_i;",
            *[
                f"    logic signed [31:0] {field}_child_{stage}_i;"
                for field in child_state_fields
            ],
            f"    logic chunk_write_enable_{stage}_i;",
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
    child_instances = []
    for stage in range(stages):
        stage_wiring.extend([
            f"    assign pixelcount_after_{stage}_i = pixelcount_stage_{stage}_i "
            f"+ (({group_size} > 32'sd{stage}) ? 32'sd1 : 32'sd0);",
            f"    assign remove_stage_{stage}_i = ({group_size} > 32'sd{stage}) "
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
            f"        .chunk_write_enable(chunk_write_enable_{stage}_i),\n"
            f"        .chunk_write_index(),\n"
            f"        .chunk_write_value()\n"
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
    body = [
        "        domain_valid = 1'b1;",
        f"        {state_outputs['bitsClamped']} = bitsclamped_stage_{stages}_i;",
        f"        {state_outputs['bpgFracAccum']} = bpgfracaccum_stage_{stages}_i;",
        f"        {state_outputs['bufferFullness']} = bufferfullness_stage_{stages}_i;",
        f"        {state_outputs['chunkCount']} = chunkcount_stage_{stages}_i;",
        f"        {state_outputs['chunkPixelTimes']} = chunkpixeltimes_stage_{stages}_i;",
        f"        {state_outputs['numBitsChunk']} = numbitschunk_stage_{stages}_i;",
        f"        {state_outputs['pixelCount']} = pixelcount_stage_{stages}_i;",
        f"        {state_outputs['bitSaveMode']} = {state['bitSaveMode']};",
        f"        {state_outputs['errorOccurred']} = {state['errorOccurred']};",
        f"        {state_outputs['mppState']} = {state['mppState']};",
        f"        {state_outputs['prevQp']} = {state['stQp']};",
        f"        {state_outputs['prevRange']} = 32'sd0;",
        f"        {state_outputs['rcSizeGroup']} = 32'sd0;",
        f"        {state_outputs['stQp']} = {state['stQp']};",
        f"        previous_qp_i = {state['stQp']};",
        f"        previous2_qp_i = {state['prevQp']};",
        "        current_qp_i = 32'sd0;",
        "        overflow_avoid_i = 1'b0;",
        f"        rc_size_group_i = {rc_size[0]} + {rc_size[1]} + {rc_size[2]};",
        f"        if ({state['unitsPerGroup']} > 3) rc_size_group_i = "
        f"rc_size_group_i + {rc_size[3]};",
        f"        throttle_i = {throttle} - {config['rc_model_size']};",
        f"        rc_model_fullness_i = ({scale} * "
        f"(bufferfullness_stage_{stages}_i + throttle_i)) >>> {scale_point};",
        "        next_range_i = 32'sd0;",
    ]
    for index, threshold in enumerate(thresholds):
        body.append(
            f"        if (rc_model_fullness_i > ({threshold} - {config['rc_model_size']})) "
            f"next_range_i = 32'sd{index + 1};"
        )
    body.extend([
        f"        if (rc_model_fullness_i > 0) {state_outputs['errorOccurred']} = 32'sd1;",
        f"        selected_range_i = {state['prevRange']};",
        f"        {state_outputs['prevRange']} = next_range_i;",
        f"        bpg_i = (({config['bits_per_pixel']} * {group_size}) + 32'sd8) >>> 4;",
        f"        rc_target_i = dsc_cicd_max(0, bpg_i + "
        f"{select(range_ports['range_bpg_offset'], 'selected_range_i')} + {bpg_offset});",
        f"        min_qp_i = {select(range_ports['range_min_qp'], 'selected_range_i')};",
        f"        max_qp_i = {select(range_ports['range_max_qp'], 'selected_range_i')};",
        f"        target_minus_i = dsc_cicd_max(0, rc_target_i - {config['rc_tgt_offset_lo']});",
        f"        target_plus_i = dsc_cicd_max(0, rc_target_i + {config['rc_tgt_offset_hi']});",
        f"        increment_i = ({state['codedGroupSize']} - rc_target_i) >>> 1;",
        f"        mpsel_i = {use_midpoint[0]} + {use_midpoint[1]} + "
        f"{use_midpoint[2]} + {use_midpoint[3]};",
        f"        if ({config['native_420']} != 0) pred_activity_i = {state['prevQp']} "
        f"+ dsc_cicd_max({predicted[0]}, {predicted[1]}) + {predicted[2]};",
        f"        else if ({config['native_422']} == 0) pred_activity_i = {state['prevQp']} "
        f"+ {predicted[0]} + dsc_cicd_max({predicted[1]}, {predicted[2]});",
        f"        else pred_activity_i = {state['prevQp']} + (({predicted[0]} + "
        f"{predicted[3]} + {predicted[1]} + {predicted[2]}) >>> 1);",
        f"        bit_save_thresh_i = {depth[0]} + {depth[1]} - 2;",
        f"        if (({config['dsc_version_minor']} == 2) && ({state['vPos']} > 0) "
        f"&& ({state['firstFlat']} == -1)) begin",
        f"            if (({state['ichSelected']} == 0) && (mpsel_i >= 3)) begin",
        f"                {state_outputs['mppState']} = {state_outputs['mppState']} + 1;",
        f"                if ({state_outputs['mppState']} >= 2) "
        f"{state_outputs['bitSaveMode']} = 2;",
        f"            end else if (({state['ichSelected']} == 0) && "
        "(pred_activity_i >= bit_save_thresh_i)) begin end",
        f"            else if ({state['ichSelected']} != 0) "
        f"{state_outputs['bitSaveMode']} = dsc_cicd_max(1, {state_outputs['bitSaveMode']});",
        "            else begin",
        f"                {state_outputs['mppState']} = 0;",
        f"                {state_outputs['bitSaveMode']} = 0;",
        "            end",
        "        end else begin",
        f"            {state_outputs['bitSaveMode']} = 0;",
        f"            {state_outputs['mppState']} = 0;",
        "        end",
        f"        if (({config['dsc_version_minor']} == 2) && "
        f"(bufferfullness_stage_{stages}_i < 192)) new_qp_i = min_qp_i;",
        f"        else if ({state_outputs['bitSaveMode']} != 0) begin",
        f"            max_qp_i = dsc_cicd_min(({config['bits_per_component']} * 2) - 1, "
        "max_qp_i + 1);",
        f"            if ({state_outputs['bitSaveMode']} == 1) new_qp_i = previous_qp_i;",
        "            else new_qp_i = previous_qp_i + 2;",
        "        end",
        f"        else if (rc_size_group_i == {state['unitsPerGroup']}) begin",
        f"            if ({config['dsc_version_minor']} == 2) begin",
        "                min_qp_i = dsc_cicd_max(min_qp_i - 4, 0);",
        "                new_qp_i = previous_qp_i - 1;",
        "            end else new_qp_i = dsc_cicd_max(min_qp_i / 2, previous_qp_i - 1);",
        "        end",
        f"        else if ((({config['dsc_version_minor']} == 1) && "
        f"({state['codedGroupSize']} < target_minus_i) && "
        "(rc_size_group_i < target_minus_i)) ||",
        f"                 (({config['dsc_version_minor']} == 2) && "
        "(rc_size_group_i < target_minus_i))) begin",
        f"            if ({config['dsc_version_minor']} == 2) new_qp_i = previous_qp_i - 1;",
        "            else new_qp_i = dsc_cicd_max(min_qp_i, previous_qp_i - 1);",
        "        end",
        f"        else if ((bufferfullness_stage_{stages}_i >= 64) && "
        f"({state['codedGroupSize']} > target_plus_i)) begin",
        "            current_qp_i = dsc_cicd_max(previous_qp_i, min_qp_i);",
        "            if (previous2_qp_i == current_qp_i) begin",
        f"                if ((rc_size_group_i * 2) < ({state['rcSizeGroup']} * "
        f"{config['rc_edge_factor']})) begin",
        f"                    if ({config['dsc_version_minor']} == 2) "
        "new_qp_i = current_qp_i + increment_i;",
        "                    else new_qp_i = dsc_cicd_min(max_qp_i, current_qp_i + increment_i);",
        "                end else new_qp_i = current_qp_i;",
        "            end else if (previous2_qp_i < current_qp_i) begin",
        f"                if (((rc_size_group_i * 2) < ({state['rcSizeGroup']} * "
        f"{config['rc_edge_factor']})) && (current_qp_i < {config['rc_quant_incr_limit0']})) begin",
        f"                    if ({config['dsc_version_minor']} == 2) "
        "new_qp_i = current_qp_i + increment_i;",
        "                    else new_qp_i = dsc_cicd_min(max_qp_i, current_qp_i + increment_i);",
        "                end else new_qp_i = current_qp_i;",
        f"            end else if (current_qp_i < {config['rc_quant_incr_limit1']}) begin",
        f"                if ({config['dsc_version_minor']} == 2) "
        "new_qp_i = current_qp_i + increment_i;",
        "                else new_qp_i = dsc_cicd_min(max_qp_i, current_qp_i + increment_i);",
        "            end else new_qp_i = current_qp_i;",
        "        end else new_qp_i = previous_qp_i;",
        f"        if ({config['dsc_version_minor']} == 2) "
        "new_qp_i = dsc_cicd_clamp(new_qp_i, min_qp_i, max_qp_i);",
        f"        overflow_avoid_i = (bufferfullness_stage_{stages}_i + throttle_i) > "
        f"(({config['native_422']} != 0) ? {overflow_422} : {overflow_other});",
        f"        if (overflow_avoid_i) new_qp_i = {range_ports['range_max_qp'][-1]};",
        f"        {state_outputs['rcSizeGroup']} = rc_size_group_i;",
        f"        {state_outputs['stQp']} = new_qp_i;",
        f"        if (bufferfullness_stage_{stages}_i > {config['rcb_bits']}) "
        f"{state_outputs['errorOccurred']} = 1;",
        f"        if (({state['isEncoder']} != 0) || ({group_size} < 1) || "
        f"({group_size} > {samples}) || ({state['unitsPerGroup']} < 3) || "
        f"({state['unitsPerGroup']} > {units}) || ({state['prevRange']} < 0) || "
        f"({state['prevRange']} >= {ranges}) || ({state['sliceWidth']} <= 0) || "
        f"({state['chunkPixelTimes']} < 0) || "
        f"({state['chunkPixelTimes']} >= {state['sliceWidth']}) || "
        f"({config['dsc_version_minor']} < 1) || ({config['dsc_version_minor']} > 2) || "
        f"(({config['native_420']} != 0) && ({config['native_420']} != 1)) || "
        f"(({config['native_422']} != 0) && ({config['native_422']} != 1)) || "
        f"(({config['native_420']} != 0) && ({config['native_422']} != 0)) || "
        f"({depth[0]} < 8) || ({depth[0]} > 16) || "
        f"({depth[1]} < 8) || ({depth[1]} > 16) || ({group_count} < 0)) "
        "domain_valid = 1'b0;",
    ])
    for stage in range(stages):
        body.append(
            f"        if (chunk_write_enable_{stage}_i) domain_valid = 1'b0;"
        )
    module = safe_identifier(contract["contract_id"])
    top = (
        f"module {module}(\n" + ",\n".join(port_lines) + "\n);\n"
        + "\n".join(declarations) + "\n\n" + functions + "\n\n"
        + "\n".join(stage_wiring) + "\n\n"
        + "\n\n".join(child_instances) + "\n\n"
        + "    always_comb begin\n" + "\n".join(body)
        + "\n    end\nendmodule\n"
    )
    return dependency_source + "\n\n" + top


def render_bounded_prediction_decode_rtl(contract: dict[str, Any]) -> str:
    semantics = contract["semantics"]
    constants = semantics["constants"]
    bindings = semantics["bindings"]
    units = int(constants["max_units"])
    samples = int(constants["samples_per_unit"])
    components = int(constants["component_count"])
    padding_left = int(constants["padding_left"])
    pred_block_size = int(constants["pred_block_size"])
    pt_map = int(constants["pt_map"])
    pt_left = int(constants["pt_left"])
    pt_block = int(constants["pt_block"])
    if (
        units, samples, components, padding_left, pred_block_size,
        pt_map, pt_left, pt_block
    ) != (4, 3, 4, 5, 3, 0, 1, 2):
        raise RuntimeError("bounded prediction decoder requires the frozen DSC shape")
    repo_root = pathlib.Path(__file__).resolve().parent.parent
    dependencies = contract.get("dependencies", []) or []
    if {str(item.get("role")) for item in dependencies} != {
        "qp_mapping", "sample_predict", "midpoint", "quantize",
        "residual_size", "max_residual",
    }:
        raise RuntimeError("bounded prediction decoder dependencies are incomplete")
    for dependency in dependencies:
        for key, hash_key in (
            ("contract_file", "contract_sha256"),
            ("module_file", "module_sha256"),
        ):
            path = pathlib.Path(str(dependency[key]))
            if not path.is_absolute():
                path = repo_root / path
            if file_hash(path) != str(dependency[hash_key]):
                raise RuntimeError("accepted prediction dependency changed before render")

    arguments = {
        str(key): str(value) for key, value in bindings["argument_ports"].items()
    }
    config = {
        str(key): str(value) for key, value in bindings["config_ports"].items()
    }
    state = {
        str(key): str(value) for key, value in bindings["state_ports"].items()
    }
    depth = [str(value) for value in bindings["depth_ports"]]
    unit_type = [str(value) for value in bindings["unit_type_ports"]]
    unit_start = [str(value) for value in bindings["unit_start_ports"]]
    use_midpoint = [str(value) for value in bindings["midpoint_ports"]]
    left_recon = [str(value) for value in bindings["left_ports"]]
    residual = [
        [str(value) for value in row] for row in bindings["residual_ports"]
    ]
    qlevels = {
        str(key): str(value) for key, value in bindings["qlevel_ports"].items()
    }
    prediction = str(bindings["prediction_port"])
    previous = [
        [str(value) for value in row]
        for row in bindings["previous_line_ports"]
    ]
    current_a = [str(value) for value in bindings["current_a_ports"]]
    current_block = [str(value) for value in bindings["current_block_ports"]]
    writes = [
        {str(key): str(value) for key, value in slot.items()}
        for slot in bindings["write_ports"]
    ]
    if (
        len(arguments) != 4
        or set(config) != {"native_420", "dsc_version_minor"}
        or set(state) != {"isEncoder", "unitsPerGroup"}
        or len(depth) != components
        or len(unit_type) != units
        or len(unit_start) != units
        or len(use_midpoint) != units
        or len(left_recon) != components
        or len(residual) != units
        or any(len(row) != samples for row in residual)
        or set(qlevels) != {"luma", "chroma"}
        or len(previous) != units
        or any(len(row) != 6 for row in previous)
        or len(current_a) != units
        or len(current_block) != units
        or len(writes) != units
        or any(set(slot) != {"enable", "component", "index", "value"} for slot in writes)
    ):
        raise RuntimeError("bounded prediction decoder bindings are incomplete")
    hpos = arguments[str(bindings["horizontal_parameter"])]
    vpos = arguments[str(bindings["vertical_parameter"])]
    sample_count = arguments[str(bindings["sample_count_parameter"])]
    qp = arguments[str(bindings["qp_parameter"])]

    def select(values: list[str], selector: str) -> str:
        expression = values[-1]
        for index in reversed(range(len(values) - 1)):
            expression = f"(({selector} == 32'sd{index}) ? {values[index]} : {expression})"
        return expression

    port_lines = []
    for port in contract["interface"]["ports"]:
        width = int(port["width"])
        width_text = "" if width == 1 else f" [{width - 1}:0]"
        signed = " signed" if port.get("signed") else ""
        port_lines.append(
            f"    {port['direction']} logic{signed}{width_text} {port['name']}"
        )
    declarations = []
    for unit in range(units):
        declarations.extend([
            f"    logic signed [31:0] cpnt_{unit}_i;",
            f"    logic signed [31:0] depth_{unit}_i;",
            f"    logic signed [31:0] qlevel_{unit}_i;",
            f"    logic signed [31:0] pred_type_{unit}_i;",
            f"    logic signed [31:0] pred_{unit}_i;",
            f"    logic signed [31:0] residual_index_{unit}_i;",
            f"    logic signed [31:0] err_{unit}_i;",
            f"    logic signed [31:0] max_value_{unit}_i;",
            f"    logic signed [31:0] recon_{unit}_i;",
        ])
    functions = f"""
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

    function automatic signed [31:0] dsc_cicd_map_qlevel(
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
                    mapped_i = mapped_i - 1;
            end
            dsc_cicd_map_qlevel = mapped_i;
        end
    endfunction

    function automatic signed [31:0] dsc_cicd_midpoint(
        input logic signed [31:0] depth_i,
        input logic signed [31:0] left_i,
        input logic signed [31:0] qlevel_i);
        begin
            dsc_cicd_midpoint = (32'sd1 <<< (depth_i - 1))
                + (left_i % (32'sd1 <<< qlevel_i));
        end
    endfunction

    function automatic signed [31:0] dsc_cicd_predict(
        input logic signed [31:0] hpos_i,
        input logic signed [31:0] pred_type_i,
        input logic signed [31:0] qlevel_i,
        input logic signed [31:0] depth_i,
        input logic signed [31:0] qr0_i,
        input logic signed [31:0] qr1_i,
        input logic signed [31:0] prev0_i,
        input logic signed [31:0] prev1_i,
        input logic signed [31:0] prev2_i,
        input logic signed [31:0] prev3_i,
        input logic signed [31:0] prev4_i,
        input logic signed [31:0] prev5_i,
        input logic signed [31:0] curr_a_i,
        input logic signed [31:0] curr_block_i);
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
        logic signed [31:0] qdiv_i;
        logic signed [31:0] half_i;
        logic signed [31:0] result_i;
        begin
            a_i = curr_a_i;
            c_i = prev1_i; b_i = prev2_i; d_i = prev3_i; e_i = prev4_i;
            filt_c_i = (prev0_i + (32'sd2 * prev1_i) + prev2_i + 2) >>> 2;
            filt_b_i = (prev1_i + (32'sd2 * prev2_i) + prev3_i + 2) >>> 2;
            filt_d_i = (prev2_i + (32'sd2 * prev3_i) + prev4_i + 2) >>> 2;
            filt_e_i = (prev3_i + (32'sd2 * prev4_i) + prev5_i + 2) >>> 2;
            qdiv_i = 32'sd1 <<< qlevel_i;
            half_i = qdiv_i / 2;
            blend_c_i = c_i + dsc_cicd_clamp(filt_c_i - c_i, -half_i, half_i);
            blend_b_i = b_i + dsc_cicd_clamp(filt_b_i - b_i, -half_i, half_i);
            blend_d_i = d_i + dsc_cicd_clamp(filt_d_i - d_i, -half_i, half_i);
            blend_e_i = e_i + dsc_cicd_clamp(filt_e_i - e_i, -half_i, half_i);
            result_i = 0;
            if (pred_type_i == 32'sd{pt_map}) begin
                if ((hpos_i / 32'sd3) == 0) blend_c_i = a_i;
                if ((hpos_i % 32'sd3) == 0)
                    result_i = dsc_cicd_clamp(a_i + blend_b_i - blend_c_i,
                        dsc_cicd_min(a_i, blend_b_i), dsc_cicd_max(a_i, blend_b_i));
                else if ((hpos_i % 32'sd3) == 1)
                    result_i = dsc_cicd_clamp(a_i + blend_d_i - blend_c_i + (qr0_i * qdiv_i),
                        dsc_cicd_min(dsc_cicd_min(a_i, blend_b_i), blend_d_i),
                        dsc_cicd_max(dsc_cicd_max(a_i, blend_b_i), blend_d_i));
                else
                    result_i = dsc_cicd_clamp(a_i + blend_e_i - blend_c_i
                            + ((qr0_i + qr1_i) * qdiv_i),
                        dsc_cicd_min(dsc_cicd_min(a_i, blend_b_i), dsc_cicd_min(blend_d_i, blend_e_i)),
                        dsc_cicd_max(dsc_cicd_max(a_i, blend_b_i), dsc_cicd_max(blend_d_i, blend_e_i)));
            end else if (pred_type_i == 32'sd{pt_left}) begin
                result_i = a_i;
                if ((hpos_i % 32'sd3) == 1)
                    result_i = dsc_cicd_clamp(a_i + (qr0_i * qdiv_i), 0,
                        (32'sd1 <<< depth_i) - 1);
                else if ((hpos_i % 32'sd3) == 2)
                    result_i = dsc_cicd_clamp(a_i + ((qr0_i + qr1_i) * qdiv_i), 0,
                        (32'sd1 <<< depth_i) - 1);
            end else result_i = curr_block_i;
            dsc_cicd_predict = result_i;
        end
    endfunction
""".strip("\n")
    body = [
        "        domain_valid = 1'b1;",
    ]
    for unit, slot in enumerate(writes):
        body.extend([
            f"        {slot['enable']} = 1'b0;",
            f"        {slot['component']} = 32'sd0;",
            f"        {slot['index']} = 32'sd0;",
            f"        {slot['value']} = 32'sd0;",
            f"        cpnt_{unit}_i = {unit_type[unit]};",
            f"        depth_{unit}_i = {select(depth, f'cpnt_{unit}_i')};",
            f"        qlevel_{unit}_i = dsc_cicd_map_qlevel(cpnt_{unit}_i, "
            f"{config['native_420']}, {config['dsc_version_minor']}, "
            f"{depth[0]}, {depth[1]}, {qlevels['luma']}, {qlevels['chroma']});",
            f"        residual_index_{unit}_i = {sample_count} - {unit_start[unit]};",
            f"        pred_type_{unit}_i = ({vpos} == 0) ? 32'sd{pt_left} : {prediction};",
            f"        if (({config['native_420']} != 0) && (cpnt_{unit}_i == 32'sd2))",
            f"            pred_type_{unit}_i = ({vpos} <= 1) ? 32'sd{pt_left} : 32'sd{pt_map};",
            f"        err_{unit}_i = (residual_index_{unit}_i == 0) ? {residual[unit][0]} : "
            f"((residual_index_{unit}_i == 1) ? {residual[unit][1]} : {residual[unit][2]});",
            f"        pred_{unit}_i = dsc_cicd_predict({hpos}, pred_type_{unit}_i, "
            f"qlevel_{unit}_i, depth_{unit}_i, {residual[unit][0]}, "
            f"{residual[unit][1]}, {', '.join(previous[unit])}, "
            f"{current_a[unit]}, {current_block[unit]});",
            f"        if ({use_midpoint[unit]} != 0)",
            f"            pred_{unit}_i = dsc_cicd_midpoint(depth_{unit}_i, "
            f"{select(left_recon, f'cpnt_{unit}_i')}, qlevel_{unit}_i);",
            f"        max_value_{unit}_i = (32'sd1 <<< depth_{unit}_i) - 1;",
            f"        recon_{unit}_i = dsc_cicd_clamp(pred_{unit}_i "
            f"+ (err_{unit}_i <<< qlevel_{unit}_i), 0, max_value_{unit}_i);",
        ])
    body.extend([
        f"        if (({state['isEncoder']} != 0) || "
        f"({state['unitsPerGroup']} < 3) || ({state['unitsPerGroup']} > {units}) || "
        f"({hpos} < 0) || ({vpos} < 0) || ({sample_count} < 0) || "
        f"({sample_count} >= {samples}) || ({qp} < 0) || ({qp} > 31) || "
        f"({qlevels['luma']} < 0) || ({qlevels['luma']} > 16) || "
        f"({qlevels['chroma']} < 0) || ({qlevels['chroma']} > 16) || "
        f"({prediction} < 0) || ({prediction} > 11)) domain_valid = 1'b0;",
    ])
    for unit, slot in enumerate(writes):
        body.extend([
            f"        if ({state['unitsPerGroup']} > {unit}) begin",
            f"            if ((cpnt_{unit}_i < 0) || (cpnt_{unit}_i >= {components}) || "
            f"(depth_{unit}_i < 8) || (depth_{unit}_i > 16) || "
            f"(qlevel_{unit}_i < 0) || (qlevel_{unit}_i > depth_{unit}_i) || "
            f"(residual_index_{unit}_i < 0) || (residual_index_{unit}_i >= {samples})) "
            "domain_valid = 1'b0;",
        ])
        for prior in range(unit):
            body.append(
                f"            if (({state['unitsPerGroup']} > {prior}) && "
                f"(cpnt_{unit}_i == cpnt_{prior}_i)) domain_valid = 1'b0;"
            )
        body.extend([
            f"            {slot['enable']} = 1'b1;",
            f"            {slot['component']} = cpnt_{unit}_i;",
            f"            {slot['index']} = {hpos} + 32'sd{padding_left};",
            f"            {slot['value']} = recon_{unit}_i;",
            "        end",
        ])
    module = safe_identifier(contract["contract_id"])
    return (
        f"module {module}(\n" + ",\n".join(port_lines) + "\n);\n"
        + "\n".join(declarations) + "\n\n" + functions + "\n\n"
        + "    always_comb begin\n" + "\n".join(body)
        + "\n    end\nendmodule\n"
    )


def render_bounded_block_pred_search_rtl(contract: dict[str, Any]) -> str:
    semantics = contract["semantics"]
    constants = semantics["constants"]
    bindings = semantics["bindings"]
    components = int(constants["component_count"])
    bp_range = int(constants["bp_range"])
    bp_size = int(constants["bp_size"])
    pred_block_size = int(constants["pred_block_size"])
    edge_count = int(constants["edge_count"])
    edge_strength = int(constants["edge_strength"])
    padding_left = int(constants["padding_left"])
    pt_map = int(constants["pt_map"])
    pt_block = int(constants["pt_block"])
    if (
        components, bp_range, bp_size, pred_block_size,
        edge_count, edge_strength, padding_left, pt_map, pt_block
    ) != (4, 13, 3, 3, 3, 32, 5, 0, 2):
        raise RuntimeError("bounded block predictor requires the frozen DSC shape")
    dependencies = contract.get("dependencies", []) or []
    if len(dependencies) != 1 or dependencies[0].get("role") != "block_sample_predict":
        raise RuntimeError("bounded block predictor dependency is incomplete")
    repo_root = pathlib.Path(__file__).resolve().parent.parent
    dependency = dependencies[0]
    for key, hash_key in (
        ("contract_file", "contract_sha256"),
        ("module_file", "module_sha256"),
    ):
        path = pathlib.Path(str(dependency[key]))
        if not path.is_absolute():
            path = repo_root / path
        if file_hash(path) != str(dependency[hash_key]):
            raise RuntimeError("accepted block predictor dependency changed before render")

    argument_ports = {
        str(key): str(value)
        for key, value in bindings["argument_ports"].items()
    }
    config = {
        str(key): str(value) for key, value in bindings["config_ports"].items()
    }
    state = {
        str(key): str(value) for key, value in bindings["state_ports"].items()
    }
    depth = [str(value) for value in bindings["depth_ports"]]
    pred_inputs = [
        [str(value) for value in row]
        for row in bindings["pred_input_ports"]
    ]
    last_inputs = [
        [[str(value) for value in block] for block in component]
        for component in bindings["last_input_ports"]
    ]
    line_offsets = [int(value) for value in bindings["line_sample_offsets"]]
    line_ports = [str(value) for value in bindings["line_sample_ports"]]
    state_outputs = {
        str(key): str(value)
        for key, value in bindings["state_output_ports"].items()
    }
    pred_outputs = [
        [str(value) for value in row]
        for row in bindings["pred_output_ports"]
    ]
    last_outputs = [
        [[str(value) for value in block] for block in component]
        for component in bindings["last_output_ports"]
    ]
    write_ports = {
        str(key): str(value) for key, value in bindings["write_ports"].items()
    }
    if (
        len(argument_ports) != 2
        or set(config) != {"bits_per_component", "block_pred_enable", "native_420"}
        or set(state) != {"numComponents", "bpCount", "lastEdgeCount", "edgeDetected"}
        or len(depth) != components
        or len(pred_inputs) != components
        or len(pred_outputs) != components
        or any(len(row) != bp_range for row in pred_inputs + pred_outputs)
        or len(last_inputs) != components
        or len(last_outputs) != components
        or any(len(component) != bp_size for component in last_inputs + last_outputs)
        or any(
            len(block) != bp_range
            for component in last_inputs + last_outputs for block in component
        )
        or line_offsets != list(range(-8, 6))
        or len(line_ports) != len(line_offsets)
        or set(state_outputs) != {"bpCount", "lastEdgeCount", "edgeDetected"}
        or set(write_ports) != {"enable", "index", "value"}
    ):
        raise RuntimeError("bounded block predictor bindings are incomplete")
    cpnt_parameter = str(bindings["component_parameter"])
    hpos_parameter = str(bindings["horizontal_parameter"])
    cpnt_port = argument_ports[cpnt_parameter]
    hpos_port = argument_ports[hpos_parameter]
    line_by_offset = dict(zip(line_offsets, line_ports))

    def select(values: list[str], selector: str) -> str:
        expression = values[-1]
        for index in reversed(range(len(values) - 1)):
            expression = f"(({selector} == 32'sd{index}) ? {values[index]} : {expression})"
        return expression

    port_lines = []
    for port in contract["interface"]["ports"]:
        width = int(port["width"])
        width_text = "" if width == 1 else f" [{width - 1}:0]"
        signed = " signed" if port.get("signed") else ""
        port_lines.append(
            f"    {port['direction']} logic{signed}{width_text} {port['name']}"
        )
    declarations = [
        "    logic signed [31:0] depth_i;",
        "    logic signed [31:0] max_cpnt_i;",
        "    logic signed [31:0] pixel_mod_i;",
        "    logic signed [31:0] cursamp_i;",
        "    logic signed [31:0] recon_i;",
        "    logic signed [31:0] pred_x_i;",
        "    logic signed [31:0] pixdiff_i;",
        "    logic signed [31:0] modified_i;",
        "    logic signed [31:0] sad3_i;",
        "    logic signed [31:0] min_err_i;",
        "    logic signed [31:0] min_pred_i;",
        "    logic done_i;",
        *[
            f"    logic signed [31:0] bp_sad_{vector}_i;"
            for vector in range(bp_range)
        ],
    ]
    body = [
        "        domain_valid = 1'b1;",
        f"        {state_outputs['bpCount']} = {state['bpCount']};",
        f"        {state_outputs['lastEdgeCount']} = {state['lastEdgeCount']};",
        f"        {state_outputs['edgeDetected']} = {state['edgeDetected']};",
    ]
    body.extend(
        f"        {pred_outputs[component][vector]} = "
        f"{pred_inputs[component][vector]};"
        for component in range(components) for vector in range(bp_range)
    )
    body.extend(
        f"        {last_outputs[component][block][vector]} = "
        f"{last_inputs[component][block][vector]};"
        for component in range(components)
        for block in range(bp_size)
        for vector in range(bp_range)
    )
    body.extend([
        f"        {write_ports['enable']} = 1'b0;",
        f"        {write_ports['index']} = {hpos_port} / 32'sd{pred_block_size};",
        f"        {write_ports['value']} = 32'sd0;",
        "        max_cpnt_i = 32'sd0;",
        "        pixel_mod_i = 32'sd0;",
        "        cursamp_i = 32'sd0;",
        "        recon_i = 32'sd0;",
        "        pred_x_i = 32'sd0;",
        "        pixdiff_i = 32'sd0;",
        "        modified_i = 32'sd0;",
        "        sad3_i = 32'sd0;",
        "        min_err_i = 32'sd0;",
        f"        min_pred_i = 32'sd{pt_map};",
        "        done_i = 1'b0;",
    ])
    body.extend(
        f"        bp_sad_{vector}_i = 32'sd0;" for vector in range(bp_range)
    )
    body.extend([
        f"        if (({cpnt_port} < 0) || ({cpnt_port} >= 32'sd{components}) || "
        f"({hpos_port} < 0) || ({state['numComponents']} < 32'sd3) || "
        f"({state['numComponents']} > 32'sd{components}) || "
        f"({config['bits_per_component']} < 32'sd8) || "
        f"({config['bits_per_component']} > 32'sd16) || "
        "(depth_i < 32'sd8) || (depth_i > 32'sd16)) domain_valid = 1'b0;",
        f"        max_cpnt_i = {state['numComponents']} - 1;",
        f"        if ({config['native_420']} != 0) max_cpnt_i = 32'sd1;",
        f"        if (({config['native_420']} != 0) && ({cpnt_port} > 32'sd1)) "
        "done_i = 1'b1;",
        "        if (!done_i) begin",
        f"            if ({hpos_port} == 0) begin",
        f"                {state_outputs['bpCount']} = 32'sd0;",
        f"                {state_outputs['lastEdgeCount']} = 32'sd10;",
    ])
    for component in range(components):
        body.append(
            f"                if ({state['numComponents']} > 32'sd{component}) begin"
        )
        body.extend(
            f"                    {last_outputs[component][block][vector]} = 32'sd0;"
            for block in range(bp_size) for vector in range(bp_range)
        )
        body.append("                end")
    body.extend([
        "            end",
        f"            recon_i = {line_by_offset[5]};",
        f"            if ({hpos_port} > 0) pixdiff_i = recon_i - {line_by_offset[4]};",
        "            else pixdiff_i = recon_i - (32'sd1 <<< (depth_i - 1));",
        "            if (pixdiff_i < 0) pixdiff_i = -pixdiff_i;",
        f"            if ({cpnt_port} == 0) {state_outputs['edgeDetected']} = 32'sd0;",
        f"            if (pixdiff_i > (32'sd{edge_strength} <<< "
        f"({config['bits_per_component']} - 32'sd8)))",
        f"                {state_outputs['edgeDetected']} = 32'sd1;",
        f"            if ({cpnt_port} == max_cpnt_i) begin",
        f"                if ({state_outputs['edgeDetected']} != 0) "
        f"{state_outputs['lastEdgeCount']} = 32'sd0;",
        f"                else {state_outputs['lastEdgeCount']} = "
        f"{state_outputs['lastEdgeCount']} + 1;",
        "            end",
        f"            cursamp_i = (({hpos_port} / 32'sd{pred_block_size}) % "
        f"32'sd{bp_size});",
        f"            pixel_mod_i = {hpos_port} % 32'sd{pred_block_size};",
    ])
    for vector in range(bp_range):
        for component in range(components):
            body.extend([
                f"            if (({cpnt_port} == 32'sd{component}) && "
                "(pixel_mod_i == 0))",
                f"                {pred_outputs[component][vector]} = 32'sd0;",
            ])
        body.extend([
            f"            if ({hpos_port} > 32'sd{vector}) "
            f"pred_x_i = {line_by_offset[4 - vector]};",
            "            else pred_x_i = 32'sd1 <<< (depth_i - 1);",
            "            pixdiff_i = recon_i - pred_x_i;",
            "            if (pixdiff_i < 0) pixdiff_i = -pixdiff_i;",
            "            modified_i = pixdiff_i >>> (depth_i - 32'sd7);",
            "            if (modified_i > 32'sd63) modified_i = 32'sd63;",
        ])
        for component in range(components):
            body.extend([
                f"            if ({cpnt_port} == 32'sd{component})",
                f"                {pred_outputs[component][vector]} = "
                f"{pred_outputs[component][vector]} + modified_i;",
            ])
    body.append("            if (pixel_mod_i == 32'sd2) begin")
    for component in range(components):
        body.append(f"                if ({cpnt_port} == 32'sd{component}) begin")
        for block in range(bp_size):
            body.append(f"                    if (cursamp_i == 32'sd{block}) begin")
            body.extend(
                f"                        {last_outputs[component][block][vector]} = "
                f"{pred_outputs[component][vector]};"
                for vector in range(bp_range)
            )
            body.append("                    end")
        body.append("                end")
    body.append(f"                if ({cpnt_port} >= max_cpnt_i) begin")
    for vector in range(bp_range):
        body.append(f"                    bp_sad_{vector}_i = 32'sd0;")
        for block in range(bp_size):
            body.append("                    sad3_i = 32'sd0;")
            for component in range(components):
                body.extend([
                    f"                    if ({state['numComponents']} > 32'sd{component})",
                    f"                        sad3_i = sad3_i + "
                    f"{last_outputs[component][block][vector]};",
                ])
            body.extend([
                "                    if (sad3_i > 32'sd511) sad3_i = 32'sd511;",
                f"                    bp_sad_{vector}_i = bp_sad_{vector}_i + sad3_i;",
            ])
        body.append(
            f"                    bp_sad_{vector}_i = bp_sad_{vector}_i >>> 3;"
        )
    body.extend([
        "                    min_err_i = bp_sad_0_i;",
        f"                    min_pred_i = 32'sd{pt_map};",
    ])
    for vector in range(2, 10):
        body.extend([
            f"                    if (min_err_i > bp_sad_{vector}_i) begin",
            f"                        min_err_i = bp_sad_{vector}_i;",
            f"                        min_pred_i = 32'sd{vector + pt_block};",
            "                    end",
        ])
    body.extend([
        f"                    if (({config['block_pred_enable']} != 0) && "
        f"({hpos_port} >= 32'sd9)) begin",
        f"                        if (min_pred_i > 32'sd{pt_block}) "
        f"{state_outputs['bpCount']} = {state_outputs['bpCount']} + 1;",
        f"                        else {state_outputs['bpCount']} = 32'sd0;",
        "                    end",
        f"                    {write_ports['enable']} = 1'b1;",
        f"                    if (({state_outputs['bpCount']} >= 32'sd3) && "
        f"({state_outputs['lastEdgeCount']} < 32'sd{edge_count}))",
        f"                        {write_ports['value']} = min_pred_i;",
        f"                    else {write_ports['value']} = 32'sd{pt_map};",
        "                end",
        "            end",
        "        end",
    ])
    module = safe_identifier(contract["contract_id"])
    return (
        f"module {module}(\n"
        + ",\n".join(port_lines)
        + "\n);\n"
        + "\n".join(declarations)
        + "\n\n"
        + f"    assign depth_i = {select(depth, cpnt_port)};\n\n"
        + "    always_comb begin\n"
        + "\n".join(body)
        + "\n    end\nendmodule\n"
    )


def render_bounded_vld_unit_rtl(contract: dict[str, Any]) -> str:
    semantics = contract["semantics"]
    constants = semantics["constants"]
    bindings = semantics["bindings"]
    units = int(constants["max_units"])
    samples = int(constants["samples_per_unit"])
    indices = int(constants["max_ich_indices"])
    fifo_bytes = int(constants["fifo_bytes"])
    prefix_bound = int(constants["max_prefix_bits"])
    ich_bits = int(constants["ich_bits"])
    if (units, samples, indices, fifo_bytes, prefix_bound) != (4, 3, 6, 17, 17):
        raise RuntimeError("bounded VLD unit requires the frozen DSC shape")
    dependencies = {
        str(item["role"]): item for item in contract.get("dependencies", [])
    }
    expected_roles = {
        "escape_size", "residual_size", "adjusted_prediction",
        "flatness_sent", "qp_mapping", "max_residual", "predict_size",
        "get_bits",
    }
    if set(dependencies) != expected_roles:
        raise RuntimeError("bounded VLD dependencies are incomplete")
    repo_root = pathlib.Path(__file__).resolve().parent.parent
    dependency_sources = []
    for role in sorted(expected_roles - {"get_bits"}):
        item = dependencies[role]
        path = pathlib.Path(str(item["module_file"]))
        if not path.is_absolute():
            path = repo_root / path
        if file_hash(path) != str(item["module_sha256"]):
            raise RuntimeError(f"accepted VLD dependency changed before render: {role}")
        dependency_sources.append(path.read_text(encoding="utf-8").rstrip() + "\n")
    get_bits = dependencies["get_bits"]
    get_bits_path = pathlib.Path(str(get_bits["module_file"]))
    if not get_bits_path.is_absolute():
        get_bits_path = repo_root / get_bits_path
    if file_hash(get_bits_path) != str(get_bits["module_sha256"]):
        raise RuntimeError("GetBits dependency changed before VLD render")

    unit_port = str(bindings["unit_port"])
    config = bindings["config_ports"]
    state = bindings["state_ports"]
    arrays = {key: list(value) for key, value in bindings["array_input_ports"].items()}
    state_outputs = bindings["state_output_ports"]
    array_outputs = {
        key: list(value) for key, value in bindings["array_output_ports"].items()
    }
    state_output_order = (
        "firstFlat", "flatnessType", "ichSelected", "prevFirstFlat",
        "prevIchSelected", "numBits",
    )
    array_output_order = (
        "ichLookup", "predictedSize", "rcSizeUnit", "useMidpoint",
    )
    if (
        set(state_outputs) != set(state_output_order)
        or set(array_outputs) != set(array_output_order)
    ):
        raise RuntimeError("bounded VLD output maps changed")
    qlevels = bindings["qlevel_ports"]
    residual_inputs = list(bindings["residual_input_ports"])
    residual_outputs = list(bindings["residual_output_ports"])
    fifo = bindings["fifo_ports"]
    fifo_data = list(bindings["fifo_data_ports"])
    fifo_outputs = bindings["fifo_output_ports"]

    def select(values: list[str], selector: str) -> str:
        expression = values[-1]
        for index in reversed(range(len(values) - 1)):
            expression = f"(({selector} == 32'sd{index}) ? {values[index]} : {expression})"
        return expression

    port_lines = []
    for port in contract["interface"]["ports"]:
        width = int(port["width"])
        width_text = "" if width == 1 else f" [{width - 1}:0]"
        signed = " signed" if port.get("signed") else ""
        port_lines.append(
            f"    {port['direction']} logic{signed}{width_text} {port['name']}"
        )
    module_names = {role: str(item["module"]) for role, item in dependencies.items()}
    cpnt_selected = select(arrays["unitCType"], unit_port)
    ssp_selected = select(arrays["unitSspMap"], unit_port)
    pred_selected = select(arrays["predictedSize"], unit_port)
    depth_selected = select(arrays["cpntBitDepth"], "cpnt_i")
    data_concat = ", ".join(fifo_data)
    declarations = [
        "    logic signed [31:0] cpnt_i;",
        "    logic signed [31:0] ssp_i;",
        "    logic signed [31:0] predicted_selected_i;",
        "    logic signed [31:0] depth_selected_i;",
        "    logic signed [31:0] qlevel_i;",
        "    logic signed [31:0] adj_predicted_i;",
        "    logic signed [31:0] max_prefix_i;",
        "    logic signed [31:0] prefix_limit_i;",
        "    logic signed [31:0] old_max_prefix_i;",
        "    logic signed [31:0] prefix_value_i;",
        "    logic signed [31:0] size_i;",
        "    logic signed [31:0] max_size_i;",
        "    logic signed [31:0] read_value_i;",
        "    logic signed [31:0] req_0_i;",
        "    logic signed [31:0] req_1_i;",
        "    logic signed [31:0] req_2_i;",
        "    logic done_i;",
        "    logic prefix_stop_i;",
        "    logic special_cap_i;",
        "    logic ich_disallow_i;",
        "    logic use_ich_i;",
        "    logic midpoint_i;",
        "    logic [32:0] read_sum_i;",
        f"    logic [{fifo_bytes * 8 - 1}:0] fifo_data_i;",
        "    logic [4:0] qlevel_leaf_i;",
        "    logic signed [4:0] adjusted_leaf_i;",
        "    logic signed [5:0] max_residual_leaf_i;",
        "    logic signed [5:0] escape_leaf_i;",
        "    logic flatness_sent_i;",
        "    logic [4:0] required_0_leaf_i;",
        "    logic [4:0] required_1_leaf_i;",
        "    logic [4:0] required_2_leaf_i;",
        "    logic [4:0] predicted_leaf_i;",
    ]
    leaf_instances = [
        f"    {module_names['qp_mapping']} u_qp_mapping(\n"
        f"        .cpnt(cpnt_i[1:0]), .qp({state['primaryQp']}[4:0]),\n"
        f"        .dsc_version_minor({config['dsc_version_minor']}[1:0]),\n"
        f"        .native_420({config['native_420']}[0]),\n"
        f"        .cpntBitDepth_0({arrays['cpntBitDepth'][0]}[4:0]),\n"
        f"        .cpntBitDepth_1({arrays['cpntBitDepth'][1]}[4:0]),\n"
        f"        .qlevel_luma({qlevels['luma_primary']}[4:0]),\n"
        f"        .qlevel_chroma({qlevels['chroma_primary']}[4:0]),\n"
        "        .return_value(qlevel_leaf_i));",
        f"    {module_names['adjusted_prediction']} u_adjusted_prediction(\n"
        f"        .unit({unit_port}[1:0]), .dsc_version_minor({config['dsc_version_minor']}[1:0]),\n"
        f"        .native_420({config['native_420']}[0]),\n"
        f"        .unit_c_type_selected(cpnt_i[1:0]),\n"
        "        .predicted_size_selected(predicted_selected_i[4:0]),\n"
        f"        .primary_qp({state['primaryQp']}[4:0]),\n"
        f"        .prev_primary_qp({state['prevPrimaryQp']}[4:0]),\n"
        + "\n".join(
            f"        .cpntBitDepth_{index}({arrays['cpntBitDepth'][index]}[4:0]),"
            for index in range(units)
        )
        + "\n"
        f"        .qlevel_luma_new({qlevels['luma_primary']}[4:0]),\n"
        f"        .qlevel_chroma_new({qlevels['chroma_primary']}[4:0]),\n"
        f"        .qlevel_luma_old({qlevels['luma_previous']}[4:0]),\n"
        f"        .qlevel_chroma_old({qlevels['chroma_previous']}[4:0]),\n"
        "        .return_value(adjusted_leaf_i));",
        f"    {module_names['max_residual']} u_max_residual(\n"
        f"        .cpnt(cpnt_i[1:0]), .qp({state['primaryQp']}[4:0]),\n"
        f"        .dsc_version_minor({config['dsc_version_minor']}[1:0]),\n"
        f"        .native_420({config['native_420']}[0]),\n"
        f"        .cpntBitDepth_0({arrays['cpntBitDepth'][0]}[4:0]),\n"
        f"        .cpntBitDepth_1({arrays['cpntBitDepth'][1]}[4:0]),\n"
        "        .cpntBitDepth_selected(depth_selected_i[4:0]),\n"
        f"        .qlevel_luma({qlevels['luma_primary']}[4:0]),\n"
        f"        .qlevel_chroma({qlevels['chroma_primary']}[4:0]),\n"
        "        .return_value(max_residual_leaf_i));",
        f"    {module_names['escape_size']} u_escape_size(\n"
        f"        .qp({state['primaryQp']}[4:0]),\n"
        f"        .dsc_version_minor({config['dsc_version_minor']}[1:0]),\n"
        f"        .native_420({config['native_420']}[0]),\n"
        f"        .cpntBitDepth_0({arrays['cpntBitDepth'][0]}[4:0]),\n"
        f"        .qlevel_luma({qlevels['luma_primary']}[4:0]),\n"
        "        .return_value(escape_leaf_i));",
        f"    {module_names['flatness_sent']} u_flatness_sent(\n"
        f"        .qp({state['primaryQp']}[4:0]),\n"
        f"        .flatness_min_qp({config['flatness_min_qp']}[4:0]),\n"
        f"        .flatness_max_qp({config['flatness_max_qp']}[4:0]),\n"
        "        .return_value(flatness_sent_i));",
        *[
            f"    {module_names['residual_size']} u_residual_size_{index}(\n"
            f"        .eq({residual_outputs[index]}[16:0]),\n"
            f"        .return_value(required_{index}_leaf_i));"
            for index in range(samples)
        ],
        f"    {module_names['predict_size']} u_predict_size(\n"
        "        .req_size_0(req_0_i[4:0]), .req_size_1(req_1_i[4:0]),\n"
        "        .req_size_2(req_2_i[4:0]), .return_value(predicted_leaf_i));",
    ]
    default_lines = [
        *[
            f"        {state_outputs[field]} = {state[field]};"
            for field in state_output_order
        ],
        *[
            f"        {array_outputs[field][index]} = {arrays[field][index]};"
            for field in array_output_order
            for index in range(len(array_outputs[field]))
        ],
        *[
            f"        {residual_outputs[index]} = {residual_inputs[index]};"
            for index in range(samples)
        ],
        f"        {fifo_outputs['lane']} = ssp_i;",
        f"        {fifo_outputs['fullness']} = {fifo['fullness']};",
        f"        {fifo_outputs['read_ptr']} = {fifo['read_ptr']};",
    ]

    def consume(count: str, target: str, sign: str, indent: str = "        ") -> list[str]:
        return [
            f"{indent}if (({count} < 0) || ({count} > 32) || "
            f"({fifo_outputs['fullness']} < {count})) domain_valid = 1'b0;",
            f"{indent}{target} = dsc_cicd_read_bits(fifo_data_i, {fifo['size']}, "
            f"{fifo_outputs['read_ptr']}, {count}, {sign});",
            f"{indent}{state_outputs['numBits']} = {state_outputs['numBits']} + {count};",
            f"{indent}{fifo_outputs['fullness']} = {fifo_outputs['fullness']} - {count};",
            f"{indent}read_sum_i = {{1'b0, {fifo_outputs['read_ptr']}}} + {count};",
            f"{indent}if (read_sum_i >= {{1'b0, {fifo['size']}}})",
            f"{indent}    {fifo_outputs['read_ptr']} = read_sum_i[31:0] - {fifo['size']};",
            f"{indent}else {fifo_outputs['read_ptr']} = read_sum_i[31:0];",
        ]

    body_lines = [
        *default_lines,
        "        domain_valid = 1'b1;",
        "        done_i = 1'b0;",
        "        prefix_stop_i = 1'b0;",
        "        special_cap_i = 1'b0;",
        "        prefix_value_i = 32'sd0;",
        "        prefix_limit_i = 32'sd0;",
        "        old_max_prefix_i = 32'sd0;",
        "        size_i = 32'sd0;",
        "        max_size_i = 32'sd0;",
        "        read_value_i = 32'sd0;",
        "        read_sum_i = 33'd0;",
        "        max_prefix_i = 32'sd0;",
        "        req_0_i = 32'sd0; req_1_i = 32'sd0; req_2_i = 32'sd0;",
        "        use_ich_i = 1'b0; midpoint_i = 1'b0;",
        f"        qlevel_i = $signed({{27'd0, qlevel_leaf_i}});",
        f"        adj_predicted_i = $signed(adjusted_leaf_i);",
        f"        ich_disallow_i = ({config['bits_per_component']} == 32'sd16) && "
        f"({unit_port} == 0) && ((32'sd3 * qlevel_i) <= "
        "(32'sd3 - adj_predicted_i));",
        f"        if (({unit_port} < 0) || ({unit_port} >= 32'sd{units}) || "
        f"(cpnt_i < 0) || (cpnt_i >= 32'sd{units}) || "
        f"(ssp_i < 0) || (ssp_i >= 32'sd{units}) || "
        f"({state['unitsPerGroup']} < 0) || ({state['unitsPerGroup']} > 32'sd{units}) || "
        f"({state['ichIndicesInGroup']} < 0) || ({state['ichIndicesInGroup']} > 32'sd{indices}) || "
        f"({fifo['size']} <= 0) || ({fifo['size']} > 32'sd{fifo_bytes * 8}) || "
        f"(({fifo['size']} & 32'sd7) != 0)) domain_valid = 1'b0;",
        f"        if ({unit_port} == 0) begin",
        f"            {state_outputs['prevIchSelected']} = {state['ichSelected']};",
        f"            {state_outputs['ichSelected']} = 32'sd0;",
        "        end",
        f"        if (({unit_port} == 0) && ({state['groupCount']}[1:0] == 2'd3)) begin",
        "            if (flatness_sent_i) begin",
        *consume("32'sd1", "read_value_i", "1'b0", "                "),
        f"                {state_outputs['prevFirstFlat']} = "
        "(read_value_i != 0) ? 32'sd0 : -32'sd1;",
        f"            end else {state_outputs['prevFirstFlat']} = -32'sd1;",
        "        end",
        f"        if (({unit_port} == 0) && ({state['groupCount']}[1:0] == 2'd0)) begin",
        f"            if ({state_outputs['prevFirstFlat']} >= 0) begin",
        f"                {state_outputs['flatnessType']} = 32'sd0;",
        f"                if ({state['primaryQp']} >= {config['somewhat_flat_qp_thresh']}) begin",
        *consume("32'sd1", "read_value_i", "1'b0", "                    "),
        f"                    {state_outputs['flatnessType']} = read_value_i;",
        "                end",
        *consume("32'sd2", "read_value_i", "1'b0", "                "),
        f"                {state_outputs['firstFlat']} = read_value_i;",
        f"            end else {state_outputs['firstFlat']} = -32'sd1;",
        "        end",
        f"        if ({state_outputs['ichSelected']} != 0) begin",
    ]
    for index in range(indices):
        body_lines.extend([
            f"            if ((32'sd{index} < {state['ichIndicesInGroup']}) && "
            f"({arrays['ichIndexUnitMap'][index]} == {unit_port})) begin",
            *consume(f"32'sd{1 << 0} * 32'sd{5}", "read_value_i", "1'b0", "                "),
            f"                {array_outputs['ichLookup'][index]} = read_value_i;",
            "            end",
        ])
    body_lines.extend([
        "            done_i = 1'b1;",
        "        end",
        "        if (!done_i) begin",
        f"            max_prefix_i = $signed(max_residual_leaf_i) + "
        f"((({unit_port} == 0) && !ich_disallow_i) ? 32'sd1 : 32'sd0) - "
        "adj_predicted_i;",
        "            old_max_prefix_i = max_prefix_i;",
        "            prefix_limit_i = max_prefix_i;",
        f"            if (({config['bits_per_component']} == 32'sd16) && "
        f"({unit_port} == 0) && (qlevel_i == 0) && ich_disallow_i && "
        "((max_prefix_i + 32'sd48) > 32'sd61)) begin",
        "                prefix_limit_i = 32'sd13;",
        "                special_cap_i = 1'b1;",
        "            end",
    ])
    for _ in range(prefix_bound):
        body_lines.extend([
            "            if (!prefix_stop_i && (prefix_value_i < prefix_limit_i)) begin",
            *consume("32'sd1", "read_value_i", "1'b0", "                "),
            "                if (read_value_i == 0) prefix_value_i = prefix_value_i + 1;",
            "                else prefix_stop_i = 1'b1;",
            "            end",
        ])
    body_lines.extend([
        "            if (special_cap_i && (prefix_value_i == prefix_limit_i))",
        "                prefix_value_i = old_max_prefix_i;",
        f"            if (({unit_port} == 0) && "
        f"({state_outputs['prevIchSelected']} != 0) && !ich_disallow_i)",
        "                size_i = adj_predicted_i + prefix_value_i - 1;",
        "            else size_i = adj_predicted_i + prefix_value_i;",
        f"            if ({state_outputs['prevIchSelected']} != 0)",
        "                use_ich_i = !ich_disallow_i && (prefix_value_i == 0);",
        "            else use_ich_i = !ich_disallow_i && "
        "(size_i >= $signed(escape_leaf_i));",
        f"            if (({unit_port} == 0) && use_ich_i) begin",
        f"                {state_outputs['ichSelected']} = 32'sd1;",
        f"                {array_outputs['rcSizeUnit'][0]} = 32'sd1 + "
        f"(32'sd{ich_bits} * {state['ichIndicesInGroup']});",
    ])
    for index in range(1, units):
        body_lines.extend([
            f"                if ({state['unitsPerGroup']} > 32'sd{index})",
            f"                    {array_outputs['rcSizeUnit'][index]} = 32'sd0;",
        ])
    for index in range(indices):
        body_lines.extend([
            f"                if ((32'sd{index} < {state['ichIndicesInGroup']}) && "
            f"({arrays['ichIndexUnitMap'][index]} == {unit_port})) begin",
            *consume(f"32'sd{ich_bits}", "read_value_i", "1'b0", "                    "),
            f"                    {array_outputs['ichLookup'][index]} = read_value_i;",
            "                end",
        ])
    body_lines.extend([
        "                done_i = 1'b1;",
        "            end",
        "        end",
        "        if (!done_i) begin",
        f"            midpoint_i = (size_i == (({depth_selected}) - qlevel_i));",
    ])
    for index in range(units):
        body_lines.extend([
            f"            if ({unit_port} == 32'sd{index})",
            f"                {array_outputs['useMidpoint'][index]} = midpoint_i;",
        ])
    for index in range(samples):
        body_lines.extend(consume("size_i", residual_outputs[index], "1'b1", "            "))
    body_lines.extend([
        "            req_0_i = $signed({27'd0, required_0_leaf_i});",
        "            req_1_i = $signed({27'd0, required_1_leaf_i});",
        "            req_2_i = $signed({27'd0, required_2_leaf_i});",
        "            max_size_i = req_0_i;",
        "            if (req_1_i > max_size_i) max_size_i = req_1_i;",
        "            if (req_2_i > max_size_i) max_size_i = req_2_i;",
        "            if (midpoint_i) begin",
        "                max_size_i = size_i;",
        "                req_0_i = size_i; req_1_i = size_i; req_2_i = size_i;",
        "            end",
    ])
    for index in range(units):
        body_lines.extend([
            f"            if ({unit_port} == 32'sd{index}) begin",
            f"                {array_outputs['rcSizeUnit'][index]} = "
            f"(max_size_i * 32'sd{samples}) + 1;",
            f"                {array_outputs['predictedSize'][index]} = "
            "$signed({27'd0, predicted_leaf_i});",
            "            end",
        ])
    body_lines.extend(["        end"])

    function_text = (
        f"    function automatic signed [31:0] dsc_cicd_read_bits(\n"
        f"        input logic [{fifo_bytes * 8 - 1}:0] data_i,\n"
        "        input logic signed [31:0] size_i,\n"
        "        input logic signed [31:0] pointer_i,\n"
        "        input logic signed [31:0] count_i,\n"
        "        input logic sign_i);\n"
        "        integer bit_i;\n        integer position_i;\n"
        "        logic signed [31:0] value_i;\n"
        "        begin\n            value_i = 32'sd0;\n"
        "            for (bit_i = 0; bit_i < 32; bit_i = bit_i + 1) begin\n"
        "                if (bit_i < count_i) begin\n"
        "                    position_i = pointer_i + bit_i;\n"
        "                    if (position_i >= size_i) position_i = position_i - size_i;\n"
        f"                    if ((position_i >= 0) && (position_i < {fifo_bytes * 8}))\n"
        f"                        value_i = (value_i <<< 1) | data_i[{fifo_bytes * 8 - 1} - position_i];\n"
        "                end\n            end\n"
        "            if (sign_i && (count_i > 0) && value_i[count_i-1])\n"
        "                value_i = value_i | (32'hffffffff << count_i);\n"
        "            dsc_cicd_read_bits = value_i;\n"
        "        end\n    endfunction\n"
    )
    module = safe_identifier(contract["contract_id"])
    top = (
        f"module {module}(\n"
        + ",\n".join(port_lines)
        + "\n);\n"
        + "\n".join(declarations)
        + "\n\n"
        + f"    assign cpnt_i = {cpnt_selected};\n"
        + f"    assign ssp_i = {ssp_selected};\n"
        + f"    assign predicted_selected_i = {pred_selected};\n"
        + f"    assign depth_selected_i = {depth_selected};\n"
        + f"    assign fifo_data_i = {{{data_concat}}};\n\n"
        + "\n\n".join(leaf_instances)
        + "\n\n"
        + function_text
        + "\n    always_comb begin\n"
        + "\n".join(body_lines)
        + "\n    end\nendmodule\n"
    )
    return "\n".join(dependency_sources) + "\n" + top


def render_bounded_vld_group_decode_rtl(contract: dict[str, Any]) -> str:
    """Render the source-ordered mux-refill plus four-stage VLD composition."""
    semantics = contract["semantics"]
    constants = semantics["constants"]
    bindings = semantics["bindings"]
    units = int(constants["max_units"])
    samples = int(constants["samples_per_unit"])
    indices = int(constants["max_ich_indices"])
    fifo_bytes = int(constants["fifo_bytes"])
    stream_bytes = int(constants["stream_window_bytes"])
    if (units, samples, indices, fifo_bytes, stream_bytes) != (4, 3, 6, 17, 33):
        raise RuntimeError("bounded VLD group requires the frozen DSC shape")

    dependencies = {
        str(item["role"]): item for item in contract.get("dependencies", [])
    }
    if set(dependencies) != {"mux_refill", "vld_unit"}:
        raise RuntimeError("bounded VLD group dependencies are incomplete")
    repo_root = pathlib.Path(__file__).resolve().parent.parent
    child_contracts: dict[str, dict[str, Any]] = {}
    dependency_sources = []
    for role in ("mux_refill", "vld_unit"):
        item = dependencies[role]
        contract_path = pathlib.Path(str(item["contract_file"]))
        module_path = pathlib.Path(str(item["module_file"]))
        if not contract_path.is_absolute():
            contract_path = repo_root / contract_path
        if not module_path.is_absolute():
            module_path = repo_root / module_path
        if (
            file_hash(contract_path) != str(item["contract_sha256"])
            or file_hash(module_path) != str(item["module_sha256"])
        ):
            raise RuntimeError(f"bounded VLD group dependency changed: {role}")
        child_contracts[role] = read_json(contract_path)
        dependency_sources.append(module_path.read_text(encoding="utf-8").rstrip())

    mux_contract = child_contracts["mux_refill"]
    vld_contract = child_contracts["vld_unit"]
    mux_ports = [dict(port) for port in mux_contract["interface"]["ports"]]
    vld_ports = [dict(port) for port in vld_contract["interface"]["ports"]]
    mux = bindings["mux"]
    vld = bindings["vld"]
    residual_inputs = [list(row) for row in bindings["residual_input_ports"]]
    residual_outputs = [list(row) for row in bindings["residual_output_ports"]]
    direct_inputs = bindings["direct_input_ports"]
    direct_outputs = bindings["direct_output_ports"]
    lanes = list(mux["fifo_lanes"])
    if (
        len(lanes) != units
        or len(residual_inputs) != units
        or len(residual_outputs) != units
        or any(len(row) != samples for row in residual_inputs + residual_outputs)
    ):
        raise RuntimeError("bounded VLD group array bindings are incomplete")

    def declaration(port: dict[str, Any], name: str | None = None) -> str:
        width = int(port["width"])
        width_text = "" if width == 1 else f" [{width - 1}:0]"
        signed = " signed" if port.get("signed") else ""
        return f"    logic{signed}{width_text} {name or port['name']};"

    port_lines = []
    for port in contract["interface"]["ports"]:
        width = int(port["width"])
        width_text = "" if width == 1 else f" [{width - 1}:0]"
        signed = " signed" if port.get("signed") else ""
        port_lines.append(
            f"    {port['direction']} logic{signed}{width_text} {port['name']}"
        )

    mux_outputs = [port for port in mux_ports if port.get("direction") == "output"]
    mux_internal = {
        str(port["name"]): f"mux_{safe_identifier(str(port['name']))}_i"
        for port in mux_outputs
    }
    declarations = [
        declaration(port, mux_internal[str(port["name"])]) for port in mux_outputs
    ]
    mux_connections = []
    for port in mux_ports:
        name = str(port["name"])
        connection = name if port.get("direction") == "input" else mux_internal[name]
        mux_connections.append(f"        .{name}({connection})")
    instances = [
        f"    {dependencies['mux_refill']['module']} u_mux_refill(\n"
        + ",\n".join(mux_connections)
        + "\n    );"
    ]

    state_inputs = {str(key): str(value) for key, value in vld["state_ports"].items()}
    state_outputs = {
        str(key): str(value) for key, value in vld["state_output_ports"].items()
    }
    array_inputs = {
        str(key): [str(value) for value in values]
        for key, values in vld["array_input_ports"].items()
    }
    array_outputs = {
        str(key): [str(value) for value in values]
        for key, values in vld["array_output_ports"].items()
    }
    evolving_state = tuple(state_outputs)
    evolving_arrays = tuple(array_outputs)
    state_input_by_port = {
        port: field for field, port in state_inputs.items()
    }
    array_input_by_port = {
        port: (field, index)
        for field, ports in array_inputs.items()
        for index, port in enumerate(ports)
    }
    state_output_by_port = {
        port: field for field, port in state_outputs.items()
    }
    array_output_by_port = {
        port: (field, index)
        for field, ports in array_outputs.items()
        for index, port in enumerate(ports)
    }
    residual_input_by_port = {
        str(port): index for index, port in enumerate(vld["residual_input_ports"])
    }
    residual_output_by_port = {
        str(port): index for index, port in enumerate(vld["residual_output_ports"])
    }
    fifo_input_by_port = {
        str(port): field for field, port in vld["fifo_ports"].items()
    }
    fifo_data_by_port = {
        str(port): index for index, port in enumerate(vld["fifo_data_ports"])
    }
    fifo_output_by_port = {
        str(port): field for field, port in vld["fifo_output_ports"].items()
    }

    state_chain: dict[tuple[int, str], str] = {}
    array_chain: dict[tuple[int, str, int], str] = {}
    fifo_full_chain: dict[tuple[int, int], str] = {}
    fifo_read_chain: dict[tuple[int, int], str] = {}
    assignments = []
    for stage in range(units + 1):
        for field in evolving_state:
            name = f"vld_state_{safe_identifier(field)}_s{stage}_i"
            state_chain[(stage, field)] = name
            declarations.append(f"    logic signed [31:0] {name};")
        for field in evolving_arrays:
            for index in range(len(array_outputs[field])):
                name = f"vld_state_{safe_identifier(field)}_{index}_s{stage}_i"
                array_chain[(stage, field, index)] = name
                declarations.append(f"    logic signed [31:0] {name};")
        for lane_index in range(units):
            full_name = f"fifo_{lane_index}_fullness_s{stage}_i"
            read_name = f"fifo_{lane_index}_read_ptr_s{stage}_i"
            fifo_full_chain[(stage, lane_index)] = full_name
            fifo_read_chain[(stage, lane_index)] = read_name
            declarations.extend([
                f"    logic signed [31:0] {full_name};",
                f"    logic signed [31:0] {read_name};",
            ])
    for field in evolving_state:
        assignments.append(
            f"    assign {state_chain[(0, field)]} = {state_inputs[field]};"
        )
    for field in evolving_arrays:
        for index, input_port in enumerate(array_inputs[field]):
            assignments.append(
                f"    assign {array_chain[(0, field, index)]} = {input_port};"
            )
    for lane_index, lane in enumerate(lanes):
        assignments.extend([
            f"    assign {fifo_full_chain[(0, lane_index)]} = "
            f"$signed({mux_internal[str(lane['fullness_output_port'])]});",
            f"    assign {fifo_read_chain[(0, lane_index)]} = "
            f"$signed({mux_internal[str(lane['read_ptr_output_port'])]});",
        ])

    def select(values: list[str], selector: str) -> str:
        expression = values[-1]
        for index in reversed(range(len(values) - 1)):
            expression = f"(({selector} == 32'sd{index}) ? {values[index]} : {expression})"
        return expression

    stage_domains = []
    stage_residuals: dict[tuple[int, int], str] = {}
    for stage in range(units):
        active = f"($signed({state_inputs['unitsPerGroup']}) > 32'sd{stage})"
        selector = array_inputs["unitSspMap"][stage]
        domain_name = f"vld_domain_s{stage}_i"
        lane_name = f"vld_fifo_lane_s{stage}_i"
        full_name = f"vld_fifo_fullness_s{stage}_i"
        read_name = f"vld_fifo_read_ptr_s{stage}_i"
        declarations.extend([
            f"    logic {domain_name};",
            f"    logic signed [31:0] {lane_name};",
            f"    logic signed [31:0] {full_name};",
            f"    logic signed [31:0] {read_name};",
        ])
        raw_state = {}
        raw_arrays = {}
        for field in evolving_state:
            raw = f"vld_{safe_identifier(field)}_s{stage}_raw_i"
            raw_state[field] = raw
            declarations.append(f"    logic signed [31:0] {raw};")
        for field in evolving_arrays:
            for index in range(len(array_outputs[field])):
                raw = f"vld_{safe_identifier(field)}_{index}_s{stage}_raw_i"
                raw_arrays[(field, index)] = raw
                declarations.append(f"    logic signed [31:0] {raw};")
        for sample in range(samples):
            raw = f"vld_residual_{stage}_{sample}_raw_i"
            stage_residuals[(stage, sample)] = raw
            declarations.append(f"    logic signed [31:0] {raw};")

        connections = []
        for port in vld_ports:
            name = str(port["name"])
            if port.get("direction") == "input":
                if name == str(vld["unit_port"]):
                    connection = f"32'sd{stage}"
                elif name in residual_input_by_port:
                    connection = residual_inputs[stage][residual_input_by_port[name]]
                elif name in fifo_input_by_port:
                    field = fifo_input_by_port[name]
                    if field == "size":
                        values = [
                            mux_internal[str(lane["size_output_port"])] for lane in lanes
                        ]
                    elif field == "fullness":
                        values = [fifo_full_chain[(stage, lane)] for lane in range(units)]
                    elif field == "read_ptr":
                        values = [fifo_read_chain[(stage, lane)] for lane in range(units)]
                    else:
                        raise RuntimeError("unexpected VLD FIFO input")
                    connection = select(values, selector)
                elif name in fifo_data_by_port:
                    byte_index = fifo_data_by_port[name]
                    connection = select([
                        mux_internal[str(lane["data_output_ports"][byte_index])]
                        for lane in lanes
                    ], selector)
                elif name in state_input_by_port:
                    field = state_input_by_port[name]
                    connection = (
                        state_chain[(stage, field)]
                        if field in evolving_state else name
                    )
                elif name in array_input_by_port:
                    field, index = array_input_by_port[name]
                    connection = (
                        array_chain[(stage, field, index)]
                        if field in evolving_arrays else name
                    )
                else:
                    connection = name
            else:
                if name == "domain_valid":
                    connection = domain_name
                elif name in state_output_by_port:
                    connection = raw_state[state_output_by_port[name]]
                elif name in array_output_by_port:
                    connection = raw_arrays[array_output_by_port[name]]
                elif name in residual_output_by_port:
                    connection = stage_residuals[(stage, residual_output_by_port[name])]
                elif name in fifo_output_by_port:
                    connection = {
                        "lane": lane_name, "fullness": full_name, "read_ptr": read_name,
                    }[fifo_output_by_port[name]]
                else:
                    raise RuntimeError(f"unrecognized VLD output: {name}")
            connections.append(f"        .{name}({connection})")
        instances.append(
            f"    {dependencies['vld_unit']['module']} u_vld_unit_{stage}(\n"
            + ",\n".join(connections)
            + "\n    );"
        )
        stage_domains.append(f"(!{active} || {domain_name})")
        for field in evolving_state:
            assignments.append(
                f"    assign {state_chain[(stage + 1, field)]} = {active} ? "
                f"{raw_state[field]} : {state_chain[(stage, field)]};"
            )
        for field in evolving_arrays:
            for index in range(len(array_outputs[field])):
                assignments.append(
                    f"    assign {array_chain[(stage + 1, field, index)]} = {active} ? "
                    f"{raw_arrays[(field, index)]} : {array_chain[(stage, field, index)]};"
                )
        for lane_index in range(units):
            lane_hit = f"({lane_name} == 32'sd{lane_index})"
            assignments.extend([
                f"    assign {fifo_full_chain[(stage + 1, lane_index)]} = "
                f"({active} && {lane_hit}) ? {full_name} : "
                f"{fifo_full_chain[(stage, lane_index)]};",
                f"    assign {fifo_read_chain[(stage + 1, lane_index)]} = "
                f"({active} && {lane_hit}) ? {read_name} : "
                f"{fifo_read_chain[(stage, lane_index)]};",
            ])

    mux_post_output = str(mux["post_mux_num_bits_output_port"])
    assignments.append(
        f"    assign {mux_post_output} = {mux_internal[mux_post_output]};"
    )
    for lane_index, lane in enumerate(lanes):
        for key in (
            "size_output_port", "write_ptr_output_port", "max_fullness_output_port",
            "byte_ctr_output_port",
        ):
            output = str(lane[key])
            assignments.append(f"    assign {output} = {mux_internal[output]};")
        assignments.extend([
            f"    assign {lane['fullness_output_port']} = "
            f"{fifo_full_chain[(units, lane_index)]};",
            f"    assign {lane['read_ptr_output_port']} = "
            f"{fifo_read_chain[(units, lane_index)]};",
        ])
        for output in lane["data_output_ports"]:
            assignments.append(f"    assign {output} = {mux_internal[str(output)]};")
    for field, output in state_outputs.items():
        assignments.append(
            f"    assign {output} = {state_chain[(units, field)]};"
        )
    for field, outputs in array_outputs.items():
        for index, output in enumerate(outputs):
            assignments.append(
                f"    assign {output} = {array_chain[(units, field, index)]};"
            )
    for stage in range(units):
        active = f"($signed({state_inputs['unitsPerGroup']}) > 32'sd{stage})"
        for sample in range(samples):
            assignments.append(
                f"    assign {residual_outputs[stage][sample]} = {active} ? "
                f"{stage_residuals[(stage, sample)]} : {residual_inputs[stage][sample]};"
            )

    coded = direct_outputs["codedGroupSize"]
    fullness = direct_outputs["bufferFullness"]
    assignments.extend([
        f"    assign {direct_outputs['prevPrimaryQp']} = {state_inputs['primaryQp']};",
        f"    assign {coded} = {state_chain[(units, 'numBits')]} - {state_inputs['numBits']};",
        f"    assign {fullness} = {direct_inputs['bufferFullness']} + {coded};",
        f"    assign {direct_outputs['errorOccurred']} = "
        f"($signed({fullness}) > $signed({direct_inputs['rcb_bits']})) ? "
        f"32'sd1 : {direct_inputs['errorOccurred']};",
        f"    assign {direct_outputs['origIsFlat']} = "
        f"(($signed({state_inputs['groupCount']}) % 32'sd4) == "
        f"$signed({state_chain[(units, 'firstFlat')]})) ? 32'sd1 : 32'sd0;",
        f"    assign {direct_outputs['groupCountLine']} = "
        f"{direct_inputs['groupCountLine']} + 32'sd1;",
        "    assign domain_valid = "
        f"{mux_internal['domain_valid']} && "
        f"($signed({state_inputs['unitsPerGroup']}) >= 32'sd3) && "
        f"($signed({state_inputs['unitsPerGroup']}) <= 32'sd{units}) && "
        + " && ".join(stage_domains) + ";",
    ])

    module = safe_identifier(contract["contract_id"])
    top = (
        f"module {module}(\n"
        + ",\n".join(port_lines)
        + "\n);\n"
        + "\n".join(declarations)
        + "\n\n"
        + "\n\n".join(instances)
        + "\n\n"
        + "\n".join(assignments)
        + "\nendmodule\n"
    )
    return "\n\n".join(dependency_sources) + "\n\n" + top


def render_raster_color_transform_rtl(contract: dict[str, Any]) -> str:
    semantics = contract["semantics"]
    bindings = semantics["bindings"]
    constants = semantics["constants"]
    direction = str(bindings["direction"])
    inputs = list(bindings["input_ports"])
    outputs = list(bindings["output_ports"])
    bits = str(bindings["bits_port"])
    if (
        direction not in {"rgb_to_ycocg", "ycocg_to_rgb"}
        or len(inputs) != 3
        or len(outputs) != 3
        or int(constants["channel_count"]) != 3
        or not constants.get("reduce_chroma_16bpc")
    ):
        raise RuntimeError("raster color transform bindings changed")
    port_lines = []
    for port in contract["interface"]["ports"]:
        width = int(port["width"])
        width_text = "" if width == 1 else f" [{width - 1}:0]"
        signed = " signed" if port.get("signed") else ""
        port_lines.append(
            f"    {port['direction']} logic{signed}{width_text} {port['name']}"
        )
    body = [
        "        domain_valid = 1'b1;",
        *[f"        {port} = 32'sd0;" for port in outputs],
        "        half_i = 32'sd0; max_i = 32'sd0;",
        "        co_i = 32'sd0; cg_i = 32'sd0; temp_i = 32'sd0;",
        "        r_i = 32'sd0; g_i = 32'sd0; b_i = 32'sd0; y_i = 32'sd0;",
        f"        if (($signed({bits}) < 32'sd{constants['minimum_bits']}) || "
        f"($signed({bits}) > 32'sd{constants['maximum_bits']})) domain_valid = 1'b0;",
        f"        half_i = 32'sd1 <<< ($signed({bits}) - 32'sd1);",
    ]
    if direction == "rgb_to_ycocg":
        body.extend([
            f"        r_i = {inputs[0]}; g_i = {inputs[1]}; b_i = {inputs[2]};",
            "        co_i = r_i - b_i;",
            "        temp_i = b_i + (co_i >>> 1);",
            "        cg_i = g_i - temp_i;",
            "        y_i = temp_i + (cg_i >>> 1);",
            f"        {outputs[0]} = y_i;",
            f"        if ($signed({bits}) == 32'sd16) begin",
            "            temp_i = ((co_i + 32'sd1) >>> 1) + half_i;",
            f"            {outputs[1]} = (temp_i < 32'sd65535) ? temp_i : 32'sd65535;",
            "            temp_i = ((cg_i + 32'sd1) >>> 1) + half_i;",
            f"            {outputs[2]} = (temp_i < 32'sd65535) ? temp_i : 32'sd65535;",
            "        end else begin",
            f"            {outputs[1]} = co_i + (half_i <<< 1);",
            f"            {outputs[2]} = cg_i + (half_i <<< 1);",
            "        end",
        ])
    else:
        body.extend([
            f"        y_i = {inputs[0]};",
            f"        if ($signed({bits}) == 32'sd16) begin",
            f"            co_i = ({inputs[1]} - half_i) <<< 1;",
            f"            cg_i = ({inputs[2]} - half_i) <<< 1;",
            "        end else begin",
            f"            co_i = {inputs[1]} - (half_i <<< 1);",
            f"            cg_i = {inputs[2]} - (half_i <<< 1);",
            "        end",
            "        temp_i = y_i - (cg_i >>> 1);",
            "        g_i = cg_i + temp_i;",
            "        b_i = temp_i - (co_i >>> 1);",
            "        r_i = co_i + b_i;",
            f"        max_i = (32'sd1 <<< $signed({bits})) - 32'sd1;",
            f"        {outputs[0]} = (r_i < 0) ? 0 : ((r_i > max_i) ? max_i : r_i);",
            f"        {outputs[1]} = (g_i < 0) ? 0 : ((g_i > max_i) ? max_i : g_i);",
            f"        {outputs[2]} = (b_i < 0) ? 0 : ((b_i > max_i) ? max_i : b_i);",
        ])
    module = safe_identifier(contract["contract_id"])
    return (
        f"module {module}(\n"
        + ",\n".join(port_lines)
        + "\n);\n"
        "    logic signed [31:0] half_i, max_i;\n"
        "    logic signed [31:0] co_i, cg_i, temp_i;\n"
        "    logic signed [31:0] r_i, g_i, b_i, y_i;\n"
        "    always_comb begin\n"
        + "\n".join(body)
        + "\n    end\nendmodule\n"
    )


def render_sampled_lookup_rtl(contract: dict[str, Any]) -> str:
    semantics = contract["semantics"]
    bindings = semantics["bindings"]
    constants = semantics["constants"]
    history = list(bindings["history_ports"])
    base = list(bindings["native_base_ports"])
    base1 = list(bindings["native_base1_ports"])
    simple = list(bindings["simple_tap_ports"])
    outputs = list(bindings["output_ports"])
    component_count = int(constants["component_count"])
    reserved = int(constants["ich_size"]) - int(constants["ich_pixels_above"])
    if (
        component_count != 4
        or len(history) != 4
        or len(base) != 4
        or len(base1) != 4
        or len(simple) != 3
        or len(outputs) != 4
    ):
        raise RuntimeError("sampled lookup transition requires the fixed four-lane DSC shape")
    port_lines = []
    for port in contract["interface"]["ports"]:
        width = int(port["width"])
        width_text = "" if width == 1 else f" [{width - 1}:0]"
        signed = " signed" if port.get("signed") else ""
        port_lines.append(
            f"    {port['direction']} logic{signed}{width_text} {port['name']}"
        )
    defaults = "".join(f"        {port} = 32'd0;\n" for port in outputs)
    history_assignments = "".join(
        f"            if (num_components > {index}) {outputs[index]} = {history[index]};\n"
        for index in range(component_count)
    )
    module = safe_identifier(contract["contract_id"])
    return (
        f"module {module}(\n"
        + ",\n".join(port_lines)
        + "\n);\n"
        "    always_comb begin\n"
        + defaults
        + f"        if ((first_line_flag == 0) && (entry >= {reserved})) begin\n"
        "            if (native_420 != 0) begin\n"
        f"                if (((entry - {reserved}) & 1) != 0) begin\n"
        f"                    {outputs[0]} = {base[0]};\n"
        f"                    {outputs[1]} = {base[1]};\n"
        f"                    {outputs[2]} = is_odd_line ? {base[3]} : {base[2]};\n"
        "                end else begin\n"
        f"                    {outputs[0]} = {base[1]};\n"
        f"                    {outputs[1]} = {base1[0]};\n"
        f"                    {outputs[2]} = is_odd_line ? {base1[3]} : {base1[2]};\n"
        "                end\n"
        "            end else if (native_422 != 0) begin\n"
        f"                if (((entry - {reserved}) & 1) != 0) begin\n"
        f"                    {outputs[0]} = {base[0]};\n"
        f"                    {outputs[1]} = {base[1]};\n"
        f"                    {outputs[2]} = {base[2]};\n"
        f"                    {outputs[3]} = {base[3]};\n"
        "                end else begin\n"
        f"                    {outputs[0]} = {base[3]};\n"
        f"                    {outputs[1]} = {base1[1]};\n"
        f"                    {outputs[2]} = {base1[2]};\n"
        f"                    {outputs[3]} = {base1[0]};\n"
        "                end\n"
        "            end else begin\n"
        f"                {outputs[0]} = {simple[0]};\n"
        f"                {outputs[1]} = {simple[1]};\n"
        f"                {outputs[2]} = {simple[2]};\n"
        "            end\n"
        "        end else begin\n"
        + history_assignments
        + "        end\n"
        "    end\n"
        "endmodule\n"
    )


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--frontier", type=pathlib.Path, required=True)
    parser.add_argument("--functions", type=pathlib.Path, required=True)
    parser.add_argument("--source-dir", type=pathlib.Path, required=True)
    parser.add_argument("--output-dir", type=pathlib.Path, required=True)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    frontier = read_json(args.frontier)
    selected = select(frontier)
    functions = read_json(args.functions).get("functions", [])
    function = next(
        item for item in functions
        if item.get("clang_usr") == selected.get("clang_usr")
    )
    contract = build_contract(selected, function, args.source_dir.resolve())
    output = args.output_dir.resolve()
    output.mkdir(parents=True, exist_ok=True)
    contract_path = output / "provisional-contract.json"
    rtl_path = output / "candidate_01.sv"
    write_json(contract_path, contract)
    rtl_path.write_text(render_rtl(contract), encoding="utf-8")
    receipt = {
        "schema_version": 1,
        "status": "PASS",
        "selection": selected,
        "contract": contract_path.name,
        "contract_sha256": file_hash(contract_path),
        "candidate": rtl_path.name,
        "candidate_sha256": file_hash(rtl_path),
        "promotion_status": "BLOCKED_PENDING_HUMAN_CONTRACT_REVIEW",
    }
    write_json(output / "generation-receipt.json", receipt)
    print(f"generated provisional decode transition: {contract['contract_id']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
