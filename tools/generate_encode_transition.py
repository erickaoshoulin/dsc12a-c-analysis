#!/usr/bin/env python3
"""Discover and generate provisional encoder state-transition RTL.

The target function is selected from Clang facts, candidate effects, and
runtime coverage.  Function names are outputs of discovery, never configured
as an allowlist.  Generated contracts remain simulation-only until the
separate human promotion gate is performed.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import math
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


def safe_identifier(value: str) -> str:
    result = re.sub(r"[^A-Za-z0-9_]", "_", value).lower()
    return ("c_" + result) if result[:1].isdigit() else result


def integer_define(source_dir: pathlib.Path, name: str) -> int:
    pattern = re.compile(
        r"^[ \t]*#[ \t]*define[ \t]+"
        + re.escape(name)
        + r"[ \t]+([0-9]+)\b",
        re.MULTILINE,
    )
    values: set[int] = set()
    for header in sorted(source_dir.glob("*.h")):
        match = pattern.search(
            header.read_text(encoding="utf-8", errors="replace")
        )
        if match:
            values.add(int(match.group(1)))
    if len(values) != 1:
        raise RuntimeError(
            f"expected one integer definition for {name}, got {sorted(values)}"
        )
    return next(iter(values))


def source_range_upper_bound(source_dir: pathlib.Path, field: str) -> int:
    """Extract a finite source range used to bound a generated transaction.

    PopulateOrigLine consumes the state slice width rather than a fixed
    preprocessor maximum.  The immutable C model validates the corresponding
    PPS field with RANGE_CHECK; use that source fact instead of inventing a
    function-specific hardware limit.
    """
    pattern = re.compile(
        r'RANGE_CHECK\s*\(\s*["\']'
        + re.escape(field)
        + r'["\']\s*,\s*[^,\n]+\s*,\s*[^,\n]+\s*,\s*([0-9]+)\s*\)'
    )
    values: set[int] = set()
    for source in sorted(source_dir.glob("*.c")):
        text = source.read_text(encoding="utf-8", errors="replace")
        values.update(int(match.group(1)) for match in pattern.finditer(text))
    if len(values) != 1:
        raise RuntimeError(
            f"expected one source RANGE_CHECK upper bound for {field}, "
            f"got {sorted(values)}"
        )
    return next(iter(values))


def source_body(
    function: dict[str, Any], source_dir: pathlib.Path
) -> tuple[pathlib.Path, int, int, str]:
    source = source_dir / str(function["source_file"])
    lines = source.read_text(encoding="utf-8", errors="replace").splitlines()
    start = int(function.get("line", 1))
    end = int(function.get("end_line", start))
    return source, start, end, "\n".join(lines[start - 1 : end])


def rows(document: dict[str, Any], key: str) -> list[dict[str, Any]]:
    value = document.get(key, []) or []
    return [item for item in value if isinstance(item, dict)]


def discover_bitstream_write_candidates(
    functions_document: dict[str, Any],
    candidates_document: dict[str, Any],
    coverage_document: dict[str, Any],
    source_dir: pathlib.Path,
) -> list[dict[str, Any]]:
    """Find bounded scalar-to-byte-buffer writers without naming one."""
    candidate_by_usr = {
        str(item.get("clang_usr")): item
        for item in rows(candidates_document, "functions")
        if item.get("clang_usr")
    }
    coverage_by_usr = {
        str(item.get("clang_usr")): item
        for item in rows(coverage_document, "functions")
        if item.get("clang_usr")
    }
    matches: list[dict[str, Any]] = []
    for function in rows(functions_document, "functions"):
        usr = str(function.get("clang_usr", ""))
        candidate = candidate_by_usr.get(usr, {})
        coverage_row = coverage_by_usr.get(usr, {})
        coverage = coverage_row.get("coverage", {}) or {}
        if not coverage.get("covered") or int(coverage.get("execution_count", 0)) <= 0:
            continue
        if function.get("return_type") != "void":
            continue
        parameters = function.get("parameters", []) or []
        scalar_parameters = [
            item
            for item in parameters
            if not item.get("pointer") and str(item.get("type")) == "int"
        ]
        pointer_parameters = function.get("pointer_parameters", []) or []
        byte_buffers = [
            item
            for item in pointer_parameters
            if item.get("mode") == "WRITES_THROUGH"
            and str(item.get("type", "")).strip() == "unsigned char *"
        ]
        cursors = [
            item
            for item in pointer_parameters
            if item.get("mode") == "WRITES_THROUGH"
            and str(item.get("type", "")).strip() == "int *"
        ]
        direct = candidate.get("direct_effects", {}) or {}
        loops = function.get("loops", []) or []
        if not (
            len(parameters) == 4
            and len(scalar_parameters) == 2
            and len(byte_buffers) == 1
            and len(cursors) == 1
            and int(function.get("loop_count", 0) or 0) == 1
            and len(loops) == 1
            and not function.get("fields_read")
            and not function.get("fields_write")
            and not function.get("globals_write")
            and candidate.get("contributes_to_observable_output")
            and not any(
                direct.get(key)
                for key in ("allocation", "assertion", "indirect_call", "io")
            )
        ):
            continue

        _, start, end, body = source_body(function, source_dir)
        scalar_names = [str(item.get("name")) for item in scalar_parameters]
        size_names = [
            name
            for name in scalar_names
            if re.search(
                r"\bfor\s*\([^;]*=\s*"
                + re.escape(name)
                + r"\s*-\s*1\s*;",
                body,
            )
        ]
        if len(size_names) != 1:
            continue
        size_name = size_names[0]
        value_names = [name for name in scalar_names if name != size_name]
        guard = re.search(
            r"\bif\s*\(\s*"
            + re.escape(size_name)
            + r"\s*>\s*([0-9]+)\s*\)",
            body,
        )
        if len(value_names) != 1 or not guard:
            continue
        maximum = int(guard.group(1))
        if maximum <= 0 or maximum > 64:
            continue
        value_name = value_names[0]
        buffer_name = str(byte_buffers[0].get("name"))
        cursor_name = str(cursors[0].get("name"))
        if not (
            re.search(
                r"\b" + re.escape(value_name) + r"\s*>>", body
            )
            and re.search(
                re.escape(buffer_name) + r"\s*\[", body
            )
            and re.search(
                r"\*\s*" + re.escape(cursor_name), body
            )
        ):
            continue
        window_bytes = math.ceil((7 + maximum) / 8)
        matches.append(
            {
                "name": function.get("name"),
                "clang_usr": usr,
                "function": function,
                "execution_count": int(coverage.get("execution_count", 0)),
                "coverage": coverage,
                "semantics_kind": "bitstream_write_transition",
                "value_parameter": value_name,
                "size_parameter": size_name,
                "buffer_parameter": buffer_name,
                "cursor_parameter": cursor_name,
                "max_bits": maximum,
                "window_bytes": window_bytes,
                "source_span": {"start_line": start, "end_line": end},
                "selection_basis": [
                    "Encode runtime coverage reached the function",
                    "Clang found two scalar int inputs and exactly one write-through byte buffer",
                    "Clang found exactly one write-through integer cursor",
                    "the sole loop is bounded by a scalar size parameter",
                    "the source guard supplies a finite legal maximum",
                    "candidate effects contain no allocation, assertion, indirect call, or file I/O",
                ],
            }
        )
    return sorted(
        matches,
        key=lambda item: (-int(item["execution_count"]), str(item["name"])),
    )


def scan_phase_verified_contracts(
    provisional_root: pathlib.Path, phase: str
) -> dict[str, dict[str, Any]]:
    """Index all-scope contracts that actually invoked RTL in one phase."""
    result: dict[str, dict[str, Any]] = {}
    if not provisional_root.is_dir():
        return result
    phase_key = phase.lower()
    for receipt_path in sorted(
        provisional_root.rglob("verification-receipt.json")
    ):
        receipt = read_json(receipt_path)
        phase_receipt = receipt.get(phase_key, {}) or {}
        if (
            receipt.get("status") != "PASS"
            or receipt.get("matrix_scope") != "all"
            or int(phase_receipt.get("rtl_return_invocations", 0) or 0) <= 0
        ):
            continue
        contract_path = receipt_path.parent / "provisional-contract.json"
        candidate_path = receipt_path.parent / "candidate_01.sv"
        if not contract_path.is_file() or not candidate_path.is_file():
            continue
        contract = read_json(contract_path)
        function_name = str(
            (contract.get("function", {}) or {}).get("name", "")
        )
        if function_name:
            result[function_name] = {
                "contract": contract,
                "contract_path": contract_path,
                "contract_sha256": hashlib.sha256(
                    contract_path.read_bytes()
                ).hexdigest(),
                "candidate_path": candidate_path,
                "candidate_sha256": hashlib.sha256(
                    candidate_path.read_bytes()
                ).hexdigest(),
                "verification_path": receipt_path,
                "rtl_return_invocations": int(
                    phase_receipt.get("rtl_return_invocations", 0)
                ),
            }
    return result


def scan_stable_contracts(
    manifest: dict[str, Any], repo_root: pathlib.Path
) -> dict[str, dict[str, Any]]:
    """Load hash-traceable accepted contracts by source function."""
    result: dict[str, dict[str, Any]] = {}
    for component in manifest.get("components", []) or []:
        if (
            not isinstance(component, dict)
            or component.get("status") != "PASS"
            or not component.get("function")
            or not component.get("contract_file")
            or not component.get("module_file")
        ):
            continue
        contract_path = repo_root / "library" / str(
            component["contract_file"]
        )
        module_path = repo_root / "library" / str(
            component["module_file"]
        )
        if not contract_path.is_file() or not module_path.is_file():
            continue
        expected_module_hash = component.get("module_sha256")
        actual_module_hash = hashlib.sha256(
            module_path.read_bytes()
        ).hexdigest()
        if (
            expected_module_hash
            and str(expected_module_hash) != actual_module_hash
        ):
            continue
        contract = read_json(contract_path)
        result[str(component["function"])] = {
            "component": component,
            "contract": contract,
            "contract_path": contract_path,
            "contract_sha256": hashlib.sha256(
                contract_path.read_bytes()
            ).hexdigest(),
            "module_path": module_path,
            "module_sha256": actual_module_hash,
        }
    return result


def discover_fifo_write_accounting_candidates(
    functions_document: dict[str, Any],
    candidates_document: dict[str, Any],
    coverage_document: dict[str, Any],
    source_dir: pathlib.Path,
    verified_contracts: dict[str, dict[str, Any]],
) -> list[dict[str, Any]]:
    """Find loop-free state callers around a verified FIFO write transition."""
    candidate_by_usr = {
        str(item.get("clang_usr")): item
        for item in rows(candidates_document, "functions")
        if item.get("clang_usr")
    }
    coverage_by_usr = {
        str(item.get("clang_usr")): item
        for item in rows(coverage_document, "functions")
        if item.get("clang_usr")
    }
    matches: list[dict[str, Any]] = []
    for function in rows(functions_document, "functions"):
        usr = str(function.get("clang_usr", ""))
        candidate = candidate_by_usr.get(usr, {})
        coverage = (
            coverage_by_usr.get(usr, {}).get("coverage", {}) or {}
        )
        if not coverage.get("covered") or int(
            coverage.get("execution_count", 0)
        ) <= 0:
            continue
        callees = [
            str(item.get("name"))
            for item in function.get("callees", [])
            if item.get("name")
        ]
        if len(callees) != 1:
            continue
        dependency = verified_contracts.get(callees[0])
        if not dependency:
            continue
        dependency_contract = dependency["contract"]
        dependency_semantics = (
            dependency_contract.get("semantics", {}) or {}
        )
        if dependency_semantics.get("kind") != "fifo_write_transition":
            continue
        parameters = function.get("parameters", []) or []
        scalar_parameters = [
            item
            for item in parameters
            if not item.get("pointer") and str(item.get("type")) == "int"
        ]
        state_parameters = [
            item
            for item in function.get("pointer_parameters", [])
            if item.get("mode") == "WRITES_THROUGH"
            and "dsc_state_t *" in str(item.get("type"))
        ]
        config_parameters = [
            item
            for item in function.get("pointer_parameters", [])
            if item.get("mode") == "READ_ONLY"
            and "dsc_cfg_t *" in str(item.get("type"))
        ]
        fifo_arrays = [
            item
            for item in function.get("fields_read", [])
            if item.get("record") == "dsc_state_t"
            and str(item.get("type", "")).startswith("fifo_t[")
        ]
        counters = [
            item
            for item in function.get("fields_write", [])
            if item.get("record") == "dsc_state_t"
            and item.get("type") == "int"
        ]
        direct = candidate.get("direct_effects", {}) or {}
        if not (
            function.get("return_type") == "void"
            and len(parameters) == 5
            and len(scalar_parameters) == 3
            and len(state_parameters) == 1
            and len(config_parameters) == 1
            and int(function.get("loop_count", 0) or 0) == 0
            and len(fifo_arrays) == 1
            and len(counters) == 1
            and not function.get("globals_write")
            and candidate.get("contributes_to_observable_output")
            and not any(
                direct.get(key)
                for key in (
                    "allocation",
                    "assertion",
                    "indirect_call",
                    "io",
                    "logging",
                )
            )
        ):
            continue
        _, start, end, body = source_body(function, source_dir)
        state_name = str(state_parameters[0]["name"])
        fifo_array = str(fifo_arrays[0]["name"])
        callee_name = callees[0]
        call = re.search(
            re.escape(callee_name)
            + r"\s*\(\s*&\s*\(?\s*"
            + re.escape(state_name)
            + r"\s*->\s*"
            + re.escape(fifo_array)
            + r"\s*\[\s*([A-Za-z_]\w*)\s*\]\s*\)?\s*,\s*"
            + r"([A-Za-z_]\w*)\s*,\s*([A-Za-z_]\w*)\s*\)",
            body,
        )
        counter_name = str(counters[0]["name"])
        counter_update = re.search(
            re.escape(state_name)
            + r"\s*->\s*"
            + re.escape(counter_name)
            + r"\s*\+=\s*([A-Za-z_]\w*)",
            body,
        )
        if not call or not counter_update:
            continue
        index_name, data_name, nbits_name = call.groups()
        if (
            {index_name, data_name, nbits_name}
            != {str(item["name"]) for item in scalar_parameters}
            or counter_update.group(1) != nbits_name
        ):
            continue
        dependency_bindings = dependency_semantics.get("bindings", {}) or {}
        required_dependency_bindings = {
            "data_field",
            "fullness_field",
            "write_ptr_field",
            "size_field",
            "max_fullness_field",
            "byte_ports",
            "byte_output_ports",
        }
        if not required_dependency_bindings.issubset(dependency_bindings):
            continue
        matches.append(
            {
                "name": function.get("name"),
                "clang_usr": usr,
                "function": function,
                "execution_count": int(coverage.get("execution_count", 0)),
                "coverage": coverage,
                "semantics_kind": "fifo_write_accounting_transition",
                "state_parameter": state_name,
                "config_parameter": str(config_parameters[0]["name"]),
                "fifo_index_parameter": index_name,
                "data_parameter": data_name,
                "nbits_parameter": nbits_name,
                "state_counter_field": counter_name,
                "fifo_array_field": fifo_array,
                "max_bits": int(dependency_semantics["max_bits"]),
                "window_bytes": int(dependency_semantics["window_bytes"]),
                "dependency": dependency,
                "source_span": {"start_line": start, "end_line": end},
                "selection_basis": [
                    "Encode runtime coverage reached the function",
                    "Clang found one loop-free mutable DSC state parameter",
                    "the only callee has all-scope Encode RTL_RETURN evidence",
                    "the callee contract is an explicit FIFO write transition",
                    "AST fields expose one indexed FIFO array and one scalar bit counter",
                    "source binding maps the FIFO index, payload, and size without a function allowlist",
                ],
            }
        )
    return sorted(
        matches,
        key=lambda item: (-int(item["execution_count"]), str(item["name"])),
    )


def discover_midpoint_line_write_candidates(
    functions_document: dict[str, Any],
    candidates_document: dict[str, Any],
    coverage_document: dict[str, Any],
    source_dir: pathlib.Path,
) -> list[dict[str, Any]]:
    """Find bounded state-to-reconstructed-line conditional scatters."""
    candidate_by_usr = {
        str(item.get("clang_usr")): item
        for item in rows(candidates_document, "functions")
        if item.get("clang_usr")
    }
    coverage_by_usr = {
        str(item.get("clang_usr")): item
        for item in rows(coverage_document, "functions")
        if item.get("clang_usr")
    }
    max_units = integer_define(source_dir, "MAX_UNITS_PER_GROUP")
    samples_per_unit = integer_define(source_dir, "SAMPLES_PER_UNIT")
    padding_left = integer_define(source_dir, "PADDING_LEFT")
    matches: list[dict[str, Any]] = []
    for function in rows(functions_document, "functions"):
        usr = str(function.get("clang_usr", ""))
        candidate = candidate_by_usr.get(usr, {})
        coverage = (
            coverage_by_usr.get(usr, {}).get("coverage", {}) or {}
        )
        if not coverage.get("covered") or int(
            coverage.get("execution_count", 0)
        ) <= 0:
            continue
        parameters = function.get("parameters", []) or []
        scalar_parameters = [
            item
            for item in parameters
            if not item.get("pointer") and str(item.get("type")) == "int"
        ]
        config_parameters = [
            item
            for item in function.get("pointer_parameters", [])
            if "dsc_cfg_t *" in str(item.get("type"))
        ]
        state_parameters = [
            item
            for item in function.get("pointer_parameters", [])
            if "dsc_state_t *" in str(item.get("type"))
        ]
        line_parameters = [
            item
            for item in function.get("pointer_parameters", [])
            if item.get("mode") == "WRITES_THROUGH"
            and str(item.get("type", "")).strip() == "int **"
        ]
        state_fields = [
            item
            for item in function.get("fields_read", [])
            if item.get("record") == "dsc_state_t"
        ]
        scalar_fields = {
            str(item.get("name"))
            for item in state_fields
            if item.get("type") == "int"
        }
        vector_fields = {
            str(item.get("name"))
            for item in state_fields
            if str(item.get("type", "")).startswith(
                f"int[{max_units}]"
            )
            and str(item.get("type", "")).count("[") == 1
        }
        matrix_fields = {
            str(item.get("name"))
            for item in state_fields
            if str(item.get("type", "")).startswith(
                f"int[{max_units}]["
            )
        }
        direct = candidate.get("direct_effects", {}) or {}
        if not (
            function.get("return_type") == "void"
            and len(parameters) == 4
            and len(scalar_parameters) == 1
            and len(config_parameters) == 1
            and len(state_parameters) == 1
            and len(line_parameters) == 1
            and int(function.get("loop_count", 0) or 0) == 2
            and not function.get("callees")
            and not function.get("fields_write")
            and not function.get("globals_write")
            and len(scalar_fields) == 3
            and len(vector_fields) == 3
            and len(matrix_fields) == 1
            and candidate.get("contributes_to_observable_output")
            and not any(
                direct.get(key)
                for key in (
                    "allocation",
                    "assertion",
                    "indirect_call",
                    "io",
                    "logging",
                )
            )
        ):
            continue
        _, start, end, body = source_body(function, source_dir)
        state_name = str(state_parameters[0]["name"])
        line_name = str(line_parameters[0]["name"])
        hpos_name = str(scalar_parameters[0]["name"])
        state_ref = re.escape(state_name) + r"\s*->\s*"
        modulo = re.search(
            re.escape(hpos_name)
            + r"\s*%\s*"
            + state_ref
            + r"([A-Za-z_]\w*)",
            body,
        )
        unit_loop = re.search(
            r"for\s*\(\s*([A-Za-z_]\w*)\s*=\s*0\s*;\s*\1\s*<\s*"
            + state_ref
            + r"([A-Za-z_]\w*)",
            body,
        )
        slice_guard = re.search(
            re.escape(hpos_name)
            + r"\s*\+\s*[A-Za-z_]\w*\s*>=\s*"
            + state_ref
            + r"([A-Za-z_]\w*)",
            body,
        )
        if not modulo or not unit_loop or not slice_guard:
            continue
        unit_variable = unit_loop.group(1)
        pixels_field = modulo.group(1)
        units_field = unit_loop.group(2)
        slice_field = slice_guard.group(1)
        if {pixels_field, units_field, slice_field} != scalar_fields:
            continue
        selected_field = next(
            (
                field
                for field in vector_fields
                if re.search(
                    r"if\s*\(\s*"
                    + state_ref
                    + re.escape(field)
                    + r"\s*\[\s*"
                    + re.escape(unit_variable)
                    + r"\s*\]\s*\)",
                    body,
                )
            ),
            None,
        )
        component_field = next(
            (
                field
                for field in vector_fields
                if re.search(
                    r"=\s*"
                    + state_ref
                    + re.escape(field)
                    + r"\s*\[\s*"
                    + re.escape(unit_variable)
                    + r"\s*\]\s*;",
                    body,
                )
                and field != selected_field
            ),
            None,
        )
        address_field = next(
            (
                field
                for field in vector_fields
                if field not in {selected_field, component_field}
                and re.search(
                    re.escape(line_name)
                    + r"\s*\[[^\]]+\]\s*\[[^\]]*"
                    + state_ref
                    + re.escape(field)
                    + r"\s*\[\s*"
                    + re.escape(unit_variable)
                    + r"\s*\]",
                    body,
                )
            ),
            None,
        )
        if not selected_field or not component_field or not address_field:
            continue
        recon_field = next(iter(matrix_fields))
        if not re.search(
            state_ref
            + re.escape(recon_field)
            + r"\s*\[\s*"
            + re.escape(unit_variable)
            + r"\s*\]",
            body,
        ):
            continue
        matches.append(
            {
                "name": function.get("name"),
                "clang_usr": usr,
                "function": function,
                "execution_count": int(coverage.get("execution_count", 0)),
                "coverage": coverage,
                "semantics_kind": "bounded_midpoint_line_write_transition",
                "config_parameter": str(config_parameters[0]["name"]),
                "state_parameter": state_name,
                "line_parameter": line_name,
                "hpos_parameter": hpos_name,
                "pixels_per_group_field": pixels_field,
                "units_per_group_field": units_field,
                "slice_width_field": slice_field,
                "selected_field": selected_field,
                "component_field": component_field,
                "unit_start_field": address_field,
                "reconstruction_field": recon_field,
                "max_units": max_units,
                "samples_per_unit": samples_per_unit,
                "padding_left": padding_left,
                "source_span": {"start_line": start, "end_line": end},
                "selection_basis": [
                    "Encode runtime coverage reached the function",
                    "Clang found one scalar position and one write-through reconstructed-line parameter",
                    "AST found a fixed sample loop and a state-bounded unit loop",
                    "AST/source bindings derive all scalar, vector, matrix, component, address, and write-enable roles",
                    "header constants bound the complete write-sideband set",
                    "no function-name allowlist is used",
                ],
            }
        )
    return sorted(
        matches,
        key=lambda item: (-int(item["execution_count"]), str(item["name"])),
    )


def discover_populate_orig_line_candidates(
    functions_document: dict[str, Any],
    candidates_document: dict[str, Any],
    coverage_document: dict[str, Any],
    source_dir: pathlib.Path,
) -> list[dict[str, Any]]:
    """Find a bounded picture-memory-to-original-line transaction.

    This matcher deliberately identifies the effect/loop shape from Clang
    facts, the source body, and Encode coverage.  The selected C function is
    never named here: its identity is an output of structural discovery.
    """
    candidate_by_usr = {
        str(item.get("clang_usr")): item
        for item in rows(candidates_document, "functions")
        if item.get("clang_usr")
    }
    coverage_by_usr = {
        str(item.get("clang_usr")): item
        for item in rows(coverage_document, "functions")
        if item.get("clang_usr")
    }
    component_count = integer_define(source_dir, "NUM_COMPONENTS")
    padding_left = integer_define(source_dir, "PADDING_LEFT")
    padding_right = integer_define(source_dir, "PADDING_RIGHT")
    max_slice_width = source_range_upper_bound(source_dir, "slice_width")
    max_slice_height = source_range_upper_bound(source_dir, "slice_height")
    matches: list[dict[str, Any]] = []
    for function in rows(functions_document, "functions"):
        usr = str(function.get("clang_usr", ""))
        candidate = candidate_by_usr.get(usr, {})
        coverage = coverage_by_usr.get(usr, {}).get("coverage", {}) or {}
        if not coverage.get("covered") or int(coverage.get("execution_count", 0)) <= 0:
            continue

        parameters = function.get("parameters", []) or []
        pointer_parameters = function.get("pointer_parameters", []) or []
        config_parameters = [
            item for item in pointer_parameters
            if item.get("mode") == "READ_ONLY"
            and str(item.get("type", "")).strip() == "dsc_cfg_t *"
        ]
        state_parameters = [
            item for item in pointer_parameters
            if item.get("mode") == "WRITES_THROUGH"
            and str(item.get("type", "")).strip() == "dsc_state_t *"
        ]
        picture_parameters = [
            item for item in pointer_parameters
            if item.get("mode") == "READ_ONLY"
            and str(item.get("type", "")).strip() == "pic_t *"
        ]
        scalar_parameters = [
            item for item in parameters
            if not item.get("pointer") and str(item.get("type", "")).strip() == "int"
        ]
        fields_read = rows({"fields": function.get("fields_read", [])}, "fields")
        state_reads = {
            str(item.get("name"))
            for item in fields_read
            if item.get("record") == "dsc_state_t"
        }
        config_reads = {
            str(item.get("name"))
            for item in fields_read
            if item.get("record") == "dsc_cfg_t"
        }
        picture_reads = {
            str(item.get("name"))
            for item in fields_read
            if item.get("record") == "pic_s"
        }
        plane_reads = {
            str(item.get("name"))
            for item in fields_read
            if item.get("record") == "yuv_s"
        }
        fields_write = {
            str(item.get("name")) for item in function.get("fields_write", [])
        }
        direct = candidate.get("direct_effects", {}) or {}
        if not (
            function.get("return_type") == "void"
            and len(parameters) == 4
            and len(config_parameters) == 1
            and len(state_parameters) == 1
            and len(picture_parameters) == 1
            and len(scalar_parameters) == 1
            and int(function.get("loop_count", 0) or 0) == 2
            and not function.get("callees")
            and fields_write == {"origLine"}
            and {"cpntBitDepth", "numComponents", "sliceWidth"}.issubset(state_reads)
            and {"native_420", "native_422", "xstart", "ystart"}.issubset(config_reads)
            and {"data", "w", "h"}.issubset(picture_reads)
            and {"y", "u", "v"}.issubset(plane_reads)
            and candidate.get("contributes_to_observable_output")
            and not function.get("globals_write")
            and not any(
                direct.get(key)
                for key in ("allocation", "assertion", "indirect_call", "io", "logging")
            )
        ):
            continue

        _, start, end, body = source_body(function, source_dir)
        config_name = str(config_parameters[0].get("name"))
        state_name = str(state_parameters[0].get("name"))
        picture_name = str(picture_parameters[0].get("name"))
        vpos_name = str(scalar_parameters[0].get("name"))
        state_ref = re.escape(state_name) + r"\s*->\s*"
        config_ref = re.escape(config_name) + r"\s*->\s*"
        picture_ref = re.escape(picture_name) + r"\s*->\s*"
        if not (
            re.search(
                r"\b" + re.escape(vpos_name) + r"\b",
                body,
            )
            and re.search(
                r"\b" + config_ref + r"xstart\s*>>\s*\(",
                body,
            )
            and re.search(
                r"for\s*\([^)]*<\s*" + state_ref + r"numComponents",
                body,
            )
            and re.search(
                r"for\s*\([^)]*<\s*" + state_ref + r"sliceWidth\s*\+\s*PADDING_RIGHT",
                body,
            )
            and re.search(r"\bMIN\s*\(", body)
            and re.search(picture_ref + r"w\b", body)
            and re.search(picture_ref + r"h\b", body)
            and re.search(r"\bPADDING_LEFT\b", body)
            and re.search(
                state_ref + r"origLine\s*\[[^\]]+\]\s*\[[^\]]+\s*\+\s*PADDING_LEFT\]",
                body,
            )
            and re.search(r"1\s*<<\s*\(\s*" + state_ref + r"cpntBitDepth\s*\[", body)
            and re.search(r"\bswitch\s*\(\s*cpnt\s*\)", body)
            and all(re.search(r"\bcase\s+" + str(case) + r"\s*:", body) for case in range(4))
        ):
            continue

        matches.append(
            {
                "name": function.get("name"),
                "clang_usr": usr,
                "function": function,
                "execution_count": int(coverage.get("execution_count", 0)),
                "coverage": coverage,
                "semantics_kind": "populate_orig_line_memory_transition",
                "config_parameter": config_name,
                "state_parameter": state_name,
                "picture_parameter": picture_name,
                "vpos_parameter": vpos_name,
                "component_count": component_count,
                "padding_left": padding_left,
                "padding_right": padding_right,
                "max_slice_width": max_slice_width,
                "max_slice_height": max_slice_height,
                "source_span": {"start_line": start, "end_line": end},
                "selection_basis": [
                    "Encode runtime coverage reached the function",
                    "Clang found read-only config/picture pointers, one mutable state pointer, and one scalar vertical position",
                    "Clang effects found only the indexed original-line output field and no callee/allocation/I/O effects",
                    "Clang fields expose component depth, component count, slice width, picture dimensions, and Y/U/V planes",
                    "source loops and MIN/PADDING/switch facts preserve the complete native-422 mapping and clamp order",
                    "the finite slice-width and slice-height bounds are extracted from immutable source RANGE_CHECK facts",
                    "no function-name allowlist is used",
                ],
            }
        )
    return sorted(
        matches,
        key=lambda item: (-int(item["execution_count"]), str(item["name"])),
    )


def discover_ich_decision_candidates(
    functions_document: dict[str, Any],
    candidates_document: dict[str, Any],
    coverage_document: dict[str, Any],
    source_dir: pathlib.Path,
    stable_contracts: dict[str, dict[str, Any]],
) -> list[dict[str, Any]]:
    """Find bounded read-only decisions composed from accepted pure callees."""
    candidate_by_usr = {
        str(item.get("clang_usr")): item
        for item in rows(candidates_document, "functions")
        if item.get("clang_usr")
    }
    coverage_by_usr = {
        str(item.get("clang_usr")): item
        for item in rows(coverage_document, "functions")
        if item.get("clang_usr")
    }
    max_units = integer_define(source_dir, "MAX_UNITS_PER_GROUP")
    ich_bits = integer_define(source_dir, "ICH_BITS")
    ich_lambda = integer_define(source_dir, "ICH_LAMBDA")
    matches: list[dict[str, Any]] = []
    for function in rows(functions_document, "functions"):
        usr = str(function.get("clang_usr", ""))
        candidate = candidate_by_usr.get(usr, {})
        coverage = (
            coverage_by_usr.get(usr, {}).get("coverage", {}) or {}
        )
        if not coverage.get("covered") or int(
            coverage.get("execution_count", 0)
        ) <= 0:
            continue
        callee_names = [
            str(item.get("name"))
            for item in function.get("callees", [])
            if item.get("name")
        ]
        if len(callee_names) != 4 or any(
            name not in stable_contracts for name in callee_names
        ):
            continue
        by_arity: dict[int, list[str]] = {}
        for name in callee_names:
            dependency_function = (
                stable_contracts[name]["contract"].get("function", {}) or {}
            )
            arity = len(dependency_function.get("parameters", []) or [])
            by_arity.setdefault(arity, []).append(name)
        if not all(
            len(by_arity.get(arity, [])) == 1
            for arity in (1, 2, 3, 4)
        ):
            continue
        log_callee = by_arity[1][0]
        estimate_callee = by_arity[2][0]
        flat_callee = by_arity[3][0]
        midpoint_callee = by_arity[4][0]
        parameters = function.get("parameters", []) or []
        scalar_parameters = [
            item
            for item in parameters
            if not item.get("pointer") and str(item.get("type")) == "int"
        ]
        config_parameters = [
            item
            for item in function.get("pointer_parameters", [])
            if "dsc_cfg_t *" in str(item.get("type"))
        ]
        state_parameters = [
            item
            for item in function.get("pointer_parameters", [])
            if "dsc_state_t *" in str(item.get("type"))
        ]
        state_fields = [
            item
            for item in function.get("fields_read", [])
            if item.get("record") == "dsc_state_t"
        ]
        scalar_state_fields = {
            str(item.get("name"))
            for item in state_fields
            if item.get("type") == "int"
        }
        vector_state_fields = {
            str(item.get("name"))
            for item in state_fields
            if str(item.get("type", "")) == f"int[{max_units}]"
        }
        config_fields = {
            str(item.get("name"))
            for item in function.get("fields_read", [])
            if item.get("record") == "dsc_cfg_t"
            and item.get("type") == "int"
        }
        direct = candidate.get("direct_effects", {}) or {}
        if not (
            function.get("return_type") == "int"
            and len(parameters) == 5
            and len(scalar_parameters) == 3
            and len(config_parameters) == 1
            and len(state_parameters) == 1
            and int(function.get("loop_count", 0) or 0) == 3
            and not function.get("fields_write")
            and not function.get("globals_write")
            and len(scalar_state_fields) == 4
            and len(vector_state_fields) == 4
            and len(config_fields) == 1
            and candidate.get("contributes_to_observable_output")
            and not any(
                direct.get(key)
                for key in (
                    "allocation",
                    "assertion",
                    "indirect_call",
                    "io",
                )
            )
        ):
            continue
        _, start, end, body = source_body(function, source_dir)
        config_name = str(config_parameters[0]["name"])
        state_name = str(state_parameters[0]["name"])
        config_ref = re.escape(config_name) + r"\s*->\s*"
        state_ref = re.escape(state_name) + r"\s*->\s*"
        midpoint_call = re.search(
            re.escape(midpoint_callee)
            + r"\s*\(\s*"
            + re.escape(config_name)
            + r"\s*,\s*"
            + re.escape(state_name)
            + r"\s*,\s*([A-Za-z_]\w*)\s*,\s*"
            + state_ref
            + r"([A-Za-z_]\w*)\s*\[\s*\1\s*\]\s*\)",
            body,
        )
        max_pair = re.search(
            r"if\s*\(\s*"
            + re.escape(midpoint_callee)
            + r"\s*\([^;]+?\)\s*\)\s*"
            + r"[A-Za-z_]\w*\s*\[[^\]]+\]\s*=\s*"
            + r"MAX\s*\([^,]+,\s*"
            + state_ref
            + r"([A-Za-z_]\w*)\s*\[[^\]]+\]\s*\)\s*;\s*"
            + r"else\s*[A-Za-z_]\w*\s*\[[^\]]+\]\s*=\s*"
            + r"MAX\s*\([^,]+,\s*"
            + state_ref
            + r"([A-Za-z_]\w*)\s*\[[^\]]+\]",
            body,
            re.DOTALL,
        )
        max_ich = re.search(
            re.escape(log_callee)
            + r"\s*\(\s*"
            + state_ref
            + r"([A-Za-z_]\w*)\s*\[[^\]]+\]\s*\)",
            body,
        )
        loop_bound = re.search(
            r"for\s*\([^;]+;[^;]*<\s*"
            + state_ref
            + r"([A-Za-z_]\w*)",
            body,
        )
        previous = re.search(
            r"if\s*\(\s*"
            + state_ref
            + r"([A-Za-z_]\w*)\s*\)\s*"
            + r"[A-Za-z_]\w*\s*=\s*1",
            body,
        )
        indices = re.search(
            r"\bICH_BITS\s*\*\s*"
            + state_ref
            + r"([A-Za-z_]\w*)",
            body,
        )
        flat_call = re.search(
            re.escape(flat_callee)
            + r"\s*\(\s*"
            + re.escape(config_name)
            + r"\s*,\s*"
            + re.escape(state_name)
            + r"\s*,\s*"
            + state_ref
            + r"([A-Za-z_]\w*)\s*\)",
            body,
        )
        version_matches = re.findall(
            config_ref + r"([A-Za-z_]\w*)\s*==\s*[12]",
            body,
        )
        bit_difference = re.search(
            r"bits_ich_mode\s*=\s*([A-Za-z_]\w*)\s*-\s*"
            r"([A-Za-z_]\w*)",
            body,
        )
        if not all(
            (
                midpoint_call,
                max_pair,
                max_ich,
                loop_bound,
                previous,
                indices,
                flat_call,
                bit_difference,
            )
        ):
            continue
        unit_type_field = midpoint_call.group(2)
        max_mid_field, max_error_field = max_pair.groups()
        max_ich_field = max_ich.group(1)
        units_field = loop_bound.group(1)
        previous_field = previous.group(1)
        indices_field = indices.group(1)
        hpos_field = flat_call.group(1)
        version_fields = set(version_matches)
        if (
            {
                unit_type_field,
                max_mid_field,
                max_error_field,
                max_ich_field,
            }
            != vector_state_fields
            or {units_field, previous_field, indices_field, hpos_field}
            != scalar_state_fields
            or version_fields != config_fields
        ):
            continue
        alt_size_name, adjusted_name = bit_difference.groups()
        scalar_names = {str(item["name"]) for item in scalar_parameters}
        if not {alt_size_name, adjusted_name}.issubset(scalar_names):
            continue
        unused_names = sorted(
            scalar_names - {alt_size_name, adjusted_name}
        )
        if len(unused_names) != 1:
            continue
        matches.append(
            {
                "name": function.get("name"),
                "clang_usr": usr,
                "function": function,
                "execution_count": int(coverage.get("execution_count", 0)),
                "coverage": coverage,
                "semantics_kind": "bounded_ich_decision_transition",
                "config_parameter": config_name,
                "state_parameter": state_name,
                "adjusted_size_parameter": adjusted_name,
                "alternate_prefix_parameter": unused_names[0],
                "alternate_size_parameter": alt_size_name,
                "version_field": next(iter(version_fields)),
                "units_field": units_field,
                "previous_ich_field": previous_field,
                "ich_indices_field": indices_field,
                "hpos_field": hpos_field,
                "unit_type_field": unit_type_field,
                "max_mid_error_field": max_mid_field,
                "max_error_field": max_error_field,
                "max_ich_error_field": max_ich_field,
                "midpoint_callee": midpoint_callee,
                "estimate_callee": estimate_callee,
                "flat_callee": flat_callee,
                "log_callee": log_callee,
                "dependencies": {
                    name: stable_contracts[name] for name in callee_names
                },
                "max_units": max_units,
                "ich_bits": ich_bits,
                "ich_lambda": ich_lambda,
                "source_span": {"start_line": start, "end_line": end},
                "selection_basis": [
                    "Encode runtime coverage reached the read-only decision",
                    "all four direct callees are hash-checked stable RTL components",
                    "callee ABI arities derive midpoint, estimate, flat-index, and logarithm roles",
                    "AST/source bindings derive every scalar and fixed four-lane error vector",
                    "three state-bounded loops are capped by the header maximum",
                    "no function-name allowlist is used",
                ],
            }
        )
    return sorted(
        matches,
        key=lambda item: (-int(item["execution_count"]), str(item["name"])),
    )


def build_bitstream_write_contract(
    selected: dict[str, Any], source_dir: pathlib.Path
) -> dict[str, Any]:
    function = selected["function"]
    name = str(function["name"])
    contract_id = safe_identifier(name) + "_encode_transition"
    maximum = int(selected["max_bits"])
    window_bytes = int(selected["window_bytes"])
    size_width = max(1, maximum.bit_length())
    byte_ports = [f"byte_{index}" for index in range(window_bytes)]
    byte_outputs = [
        f"byte_{index}_out" for index in range(window_bytes)
    ]
    _, start, end, body = source_body(function, source_dir)
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
            "source_body_sha256": hashlib.sha256(
                body.encode("utf-8")
            ).hexdigest(),
            "parameters": function.get("parameters", []),
            "return_type": function.get("return_type"),
        },
        "interface": {
            "ports": [
                {
                    "name": "value",
                    "direction": "input",
                    "width": 32,
                    "signed": False,
                },
                {
                    "name": "size",
                    "direction": "input",
                    "width": size_width,
                    "signed": False,
                },
                *[
                    {
                        "name": port,
                        "direction": "input",
                        "width": 8,
                        "signed": False,
                    }
                    for port in byte_ports
                ],
                {
                    "name": "bit_count",
                    "direction": "input",
                    "width": 32,
                    "signed": False,
                },
                *[
                    {
                        "name": port,
                        "direction": "output",
                        "width": 8,
                        "signed": False,
                    }
                    for port in byte_outputs
                ],
                {
                    "name": "bit_count_out",
                    "direction": "output",
                    "width": 32,
                    "signed": False,
                },
            ]
        },
        "semantics": {
            "kind": "bitstream_write_transition",
            "max_bits": maximum,
            "legal_size_values": list(range(maximum + 1)),
            "window_bytes": window_bytes,
            "bindings": {
                "value_parameter": selected["value_parameter"],
                "size_parameter": selected["size_parameter"],
                "buffer_parameter": selected["buffer_parameter"],
                "cursor_parameter": selected["cursor_parameter"],
                "value_port": "value",
                "size_port": "size",
                "byte_ports": byte_ports,
                "cursor_port": "bit_count",
                "byte_output_ports": byte_outputs,
                "cursor_output_port": "bit_count_out",
            },
            "state_transition": (
                "write size bits MSB-first into a bounded output-byte image "
                "and advance the explicit bit cursor"
            ),
            "legal_domain": {
                "size_minimum": 0,
                "size_maximum": maximum,
                "runtime_error_logging_branch_excluded": True,
            },
        },
        "selection": {
            "basis": selected["selection_basis"],
            "encode_execution_count": selected["execution_count"],
            "window_bytes": window_bytes,
        },
        "obligations": [
            "full-frame Encode C_ONLY/SHADOW/RTL_RETURN comparison",
            "all selected Encode profiles must exercise RTL in SHADOW and RTL_RETURN",
            "human review of output-memory and cursor contract before promotion",
        ],
        "promotion": {
            "status": "BLOCKED_PENDING_HUMAN_CONTRACT_REVIEW",
            "simulation_may_proceed": True,
        },
    }


def render_bitstream_write_rtl(contract: dict[str, Any]) -> str:
    semantics = contract["semantics"]
    bindings = semantics["bindings"]
    module = safe_identifier(str(contract["contract_id"]))
    maximum = int(semantics["max_bits"])
    window_bytes = int(semantics["window_bytes"])
    ports = contract["interface"]["ports"]
    declarations = []
    for port in ports:
        direction = str(port["direction"])
        width = int(port["width"])
        declarations.append(
            f"    {direction} logic"
            + (f" [{width - 1}:0]" if width > 1 else "")
            + f" {port['name']}"
        )
    byte_ports = list(bindings["byte_ports"])
    byte_outputs = list(bindings["byte_output_ports"])
    size_width = next(
        int(port["width"]) for port in ports if port["name"] == "size"
    )
    body = [
        f"module {module} (",
        ",\n".join(declarations),
        ");",
        "",
        "  integer k;",
        "  integer logical_bit;",
        "  integer slot;",
        "  integer source_bit;",
        *[
            f"  logic [7:0] work_{index};"
            for index in range(window_bytes)
        ],
        "",
        "  always_comb begin",
    ]
    body.extend(
        f"    work_{index} = {port};"
        for index, port in enumerate(byte_ports)
    )
    body.extend(
        [
            "    logical_bit = 0;",
            "    slot = 0;",
            "    source_bit = 0;",
            "    bit_count_out = bit_count + "
            f"{{{{{32 - size_width}{{1'b0}}}}, size}};",
            f"    for (k = 0; k < {maximum}; k = k + 1) begin",
            "      if (k < int'(size)) begin",
            "        logical_bit = int'(bit_count[2:0]) + k;",
            "        slot = logical_bit >> 3;",
            "        source_bit = int'(size) - 1 - k;",
            "        case (slot)",
        ]
    )
    for index in range(window_bytes):
        body.extend(
            [
                f"          {index}: begin",
                "            if ((logical_bit & 7) == 0)",
                f"              work_{index} = 8'h00;",
                "            if (value[source_bit])",
                f"              work_{index} = work_{index} "
                "| (8'h80 >> (logical_bit & 7));",
                "          end",
            ]
        )
    body.extend(
        [
            "          default: begin end",
            "        endcase",
            "      end",
            "    end",
        ]
    )
    body.extend(
        f"    {port} = work_{index};"
        for index, port in enumerate(byte_outputs)
    )
    body.extend(["  end", "", "endmodule", ""])
    return "\n".join(body)


def build_fifo_write_accounting_contract(
    selected: dict[str, Any], source_dir: pathlib.Path
) -> dict[str, Any]:
    function = selected["function"]
    name = str(function["name"])
    contract_id = safe_identifier(name) + "_encode_transition"
    maximum = int(selected["max_bits"])
    window_bytes = int(selected["window_bytes"])
    nbits_width = max(1, maximum.bit_length())
    dependency = selected["dependency"]
    dependency_contract = dependency["contract"]
    child_bindings = (
        (dependency_contract.get("semantics", {}) or {}).get(
            "bindings", {}
        )
        or {}
    )
    byte_ports = [f"byte_{index}" for index in range(window_bytes)]
    byte_outputs = [
        f"byte_{index}_out" for index in range(window_bytes)
    ]
    _, start, end, body = source_body(function, source_dir)
    ports = [
        {
            "name": "data",
            "direction": "input",
            "width": 32,
            "signed": False,
        },
        {
            "name": "nbits",
            "direction": "input",
            "width": nbits_width,
            "signed": False,
        },
        *[
            {
                "name": port,
                "direction": "input",
                "width": 8,
                "signed": False,
            }
            for port in byte_ports
        ],
        {
            "name": "num_bits",
            "direction": "input",
            "width": 32,
            "signed": True,
        },
        {
            "name": "fullness",
            "direction": "input",
            "width": 32,
            "signed": False,
        },
        {
            "name": "write_ptr",
            "direction": "input",
            "width": 32,
            "signed": False,
        },
        {
            "name": "fifo_size",
            "direction": "input",
            "width": 32,
            "signed": False,
        },
        {
            "name": "max_fullness",
            "direction": "input",
            "width": 32,
            "signed": False,
        },
        *[
            {
                "name": port,
                "direction": "output",
                "width": 8,
                "signed": False,
            }
            for port in byte_outputs
        ],
        {
            "name": "num_bits_out",
            "direction": "output",
            "width": 32,
            "signed": True,
        },
        {
            "name": "fullness_out",
            "direction": "output",
            "width": 32,
            "signed": False,
        },
        {
            "name": "write_ptr_out",
            "direction": "output",
            "width": 32,
            "signed": False,
        },
        {
            "name": "max_fullness_out",
            "direction": "output",
            "width": 32,
            "signed": False,
        },
    ]
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
            "source_body_sha256": hashlib.sha256(
                body.encode("utf-8")
            ).hexdigest(),
            "parameters": function.get("parameters", []),
            "return_type": function.get("return_type"),
        },
        "interface": {"ports": ports},
        "semantics": {
            "kind": "fifo_write_accounting_transition",
            "max_bits": maximum,
            "window_bytes": window_bytes,
            "legal_domain": {
                "nbits": [0, maximum],
                "fifo_index_nonnegative_and_in_range": True,
                "free_space_at_least_nbits": True,
                "fifo_size_positive_multiple_of_8": True,
            },
            "bindings": {
                "state_parameter": selected["state_parameter"],
                "config_parameter": selected["config_parameter"],
                "fifo_index_parameter": selected[
                    "fifo_index_parameter"
                ],
                "data_parameter": selected["data_parameter"],
                "nbits_parameter": selected["nbits_parameter"],
                "state_counter_field": selected[
                    "state_counter_field"
                ],
                "fifo_array_field": selected["fifo_array_field"],
                "data_field": child_bindings["data_field"],
                "fullness_field": child_bindings["fullness_field"],
                "write_ptr_field": child_bindings[
                    "write_ptr_field"
                ],
                "size_field": child_bindings["size_field"],
                "max_fullness_field": child_bindings[
                    "max_fullness_field"
                ],
                "data_port": "data",
                "nbits_port": "nbits",
                "byte_ports": byte_ports,
                "num_bits_port": "num_bits",
                "fullness_port": "fullness",
                "write_ptr_port": "write_ptr",
                "fifo_size_port": "fifo_size",
                "max_fullness_port": "max_fullness",
                "byte_output_ports": byte_outputs,
                "num_bits_output_port": "num_bits_out",
                "fullness_output_port": "fullness_out",
                "write_ptr_output_port": "write_ptr_out",
                "max_fullness_output_port": "max_fullness_out",
            },
            "state_transition": (
                "write n payload bits into one selected encoder FIFO, "
                "advance its memory/scalar state, and increment the "
                "explicit encoded-bit counter"
            ),
        },
        "composition": {
            "callee_function": (
                dependency_contract.get("function", {}) or {}
            ).get("name"),
            "callee_contract_id": dependency_contract.get(
                "contract_id"
            ),
            "callee_contract_sha256": dependency[
                "contract_sha256"
            ],
            "callee_candidate_sha256": dependency[
                "candidate_sha256"
            ],
            "callee_encode_rtl_return_invocations": dependency[
                "rtl_return_invocations"
            ],
            "implementation": (
                "verified FIFO-write transition inlined before scalar "
                "counter update in exact C source order"
            ),
        },
        "selection": {
            "basis": selected["selection_basis"],
            "encode_execution_count": selected["execution_count"],
        },
        "obligations": [
            "full-frame Encode C_ONLY/SHADOW/RTL_RETURN comparison",
            "all selected Encode profiles must exercise RTL in SHADOW and RTL_RETURN",
            "human review of composed FIFO memory and bit-counter contract before promotion",
        ],
        "promotion": {
            "status": "BLOCKED_PENDING_HUMAN_CONTRACT_REVIEW",
            "simulation_may_proceed": True,
        },
    }


def render_fifo_write_accounting_rtl(
    contract: dict[str, Any]
) -> str:
    semantics = contract["semantics"]
    bindings = semantics["bindings"]
    byte_ports = list(bindings["byte_ports"])
    byte_outputs = list(bindings["byte_output_ports"])
    module = safe_identifier(str(contract["contract_id"]))
    maximum = int(semantics["max_bits"])
    nbits_width = next(
        int(port["width"])
        for port in contract["interface"]["ports"]
        if port["name"] == bindings["nbits_port"]
    )
    window_width = len(byte_ports) * 8
    port_lines = [
        "    input  logic [31:0] data",
        f"    input  logic [{nbits_width - 1}:0] nbits",
        *[f"    input  logic [7:0] {name}" for name in byte_ports],
        "    input  logic signed [31:0] num_bits",
        "    input  logic [31:0] fullness",
        "    input  logic [31:0] write_ptr",
        "    input  logic [31:0] fifo_size",
        "    input  logic [31:0] max_fullness",
        *[
            f"    output logic [7:0] {name}"
            for name in byte_outputs
        ],
        "    output logic signed [31:0] num_bits_out",
        "    output logic [31:0] fullness_out",
        "    output logic [31:0] write_ptr_out",
        "    output logic [31:0] max_fullness_out",
    ]
    concatenation = ", ".join(byte_ports)
    byte_assignments = "".join(
        f"        {output} = "
        f"window_out_i[{window_width - 1 - index * 8} -: 8];\n"
        for index, output in enumerate(byte_outputs)
    )
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
        "            if (i < int'(nbits))\n"
        f"                window_out_i[{window_width - 1} - "
        "int'(write_ptr[2:0]) - i] = "
        "data[int'(nbits) - 1 - i];\n"
        "        end\n"
        + byte_assignments
        + f"        num_bits_out = num_bits + "
        f"{{{{{32 - nbits_width}{{1'b0}}}}, nbits}};\n"
        f"        fullness_out = fullness + "
        f"{{{{{32 - nbits_width}{{1'b0}}}}, nbits}};\n"
        f"        write_sum_i = {{1'b0, write_ptr}} + "
        f"{{{{{33 - nbits_width}{{1'b0}}}}, nbits}};\n"
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


def build_midpoint_line_write_contract(
    selected: dict[str, Any], source_dir: pathlib.Path
) -> dict[str, Any]:
    function = selected["function"]
    name = str(function["name"])
    contract_id = safe_identifier(name) + "_encode_transition"
    max_units = int(selected["max_units"])
    samples_per_unit = int(selected["samples_per_unit"])
    write_slots = max_units * samples_per_unit
    _, start, end, body = source_body(function, source_dir)
    scalar_input_names = [
        "hpos",
        "pixels_per_group",
        "units_per_group",
        "slice_width",
    ]
    vector_roles = (
        "unit_selected",
        "unit_component",
        "unit_start",
    )
    ports: list[dict[str, Any]] = [
        {
            "name": port,
            "direction": "input",
            "width": 32,
            "signed": True,
        }
        for port in scalar_input_names
    ]
    for role in vector_roles:
        ports.extend(
            {
                "name": f"{role}_{unit}",
                "direction": "input",
                "width": 32,
                "signed": True,
            }
            for unit in range(max_units)
        )
    ports.extend(
        {
            "name": f"reconstruction_{unit}_{sample}",
            "direction": "input",
            "width": 32,
            "signed": True,
        }
        for unit in range(max_units)
        for sample in range(samples_per_unit)
    )
    sidebands: list[dict[str, str]] = []
    for slot in range(write_slots):
        names = {
            "enable": f"write_enable_{slot}",
            "component": f"write_component_{slot}",
            "address": f"write_address_{slot}",
            "value": f"write_value_{slot}",
        }
        sidebands.append(names)
        ports.extend(
            [
                {
                    "name": names["enable"],
                    "direction": "output",
                    "width": 1,
                    "signed": False,
                },
                {
                    "name": names["component"],
                    "direction": "output",
                    "width": 2,
                    "signed": False,
                },
                {
                    "name": names["address"],
                    "direction": "output",
                    "width": 32,
                    "signed": True,
                },
                {
                    "name": names["value"],
                    "direction": "output",
                    "width": 32,
                    "signed": True,
                },
            ]
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
            "source_body_sha256": hashlib.sha256(
                body.encode("utf-8")
            ).hexdigest(),
            "parameters": function.get("parameters", []),
            "return_type": function.get("return_type"),
        },
        "interface": {"ports": ports},
        "semantics": {
            "kind": "bounded_midpoint_line_write_transition",
            "max_units": max_units,
            "samples_per_unit": samples_per_unit,
            "write_slots": write_slots,
            "padding_left": int(selected["padding_left"]),
            "legal_domain": {
                "hpos_nonnegative": True,
                "pixels_per_group_positive": True,
                "units_per_group": [0, max_units],
                "unit_component": [0, 3],
                "all_enabled_addresses_reference_allocated_padded_lines": True,
            },
            "bindings": {
                "config_parameter": selected["config_parameter"],
                "state_parameter": selected["state_parameter"],
                "line_parameter": selected["line_parameter"],
                "hpos_parameter": selected["hpos_parameter"],
                "pixels_per_group_field": selected[
                    "pixels_per_group_field"
                ],
                "units_per_group_field": selected[
                    "units_per_group_field"
                ],
                "slice_width_field": selected["slice_width_field"],
                "selected_field": selected["selected_field"],
                "component_field": selected["component_field"],
                "unit_start_field": selected["unit_start_field"],
                "reconstruction_field": selected[
                    "reconstruction_field"
                ],
                "hpos_port": "hpos",
                "pixels_per_group_port": "pixels_per_group",
                "units_per_group_port": "units_per_group",
                "slice_width_port": "slice_width",
                "selected_ports": [
                    f"unit_selected_{unit}"
                    for unit in range(max_units)
                ],
                "component_ports": [
                    f"unit_component_{unit}"
                    for unit in range(max_units)
                ],
                "unit_start_ports": [
                    f"unit_start_{unit}" for unit in range(max_units)
                ],
                "reconstruction_ports": [
                    [
                        f"reconstruction_{unit}_{sample}"
                        for sample in range(samples_per_unit)
                    ]
                    for unit in range(max_units)
                ],
                "write_sidebands": sidebands,
            },
            "state_transition": (
                "emit every conditional reconstructed-line write in exact "
                "sample-major then unit-major C source order"
            ),
        },
        "selection": {
            "basis": selected["selection_basis"],
            "encode_execution_count": selected["execution_count"],
        },
        "obligations": [
            "full-frame Encode C_ONLY/SHADOW/RTL_RETURN comparison",
            "enabled write metadata and final aliased line image must match original C",
            "human review of bounded reconstructed-line write sidebands before promotion",
        ],
        "promotion": {
            "status": "BLOCKED_PENDING_HUMAN_CONTRACT_REVIEW",
            "simulation_may_proceed": True,
        },
    }


def render_midpoint_line_write_rtl(
    contract: dict[str, Any]
) -> str:
    semantics = contract["semantics"]
    bindings = semantics["bindings"]
    module = safe_identifier(str(contract["contract_id"]))
    max_units = int(semantics["max_units"])
    samples_per_unit = int(semantics["samples_per_unit"])
    padding_left = int(semantics["padding_left"])
    port_lines: list[str] = []
    for port in contract["interface"]["ports"]:
        direction = str(port["direction"])
        width = int(port["width"])
        signed = " signed" if port.get("signed") else ""
        width_text = f" [{width - 1}:0]" if width > 1 else ""
        port_lines.append(
            f"    {direction} logic{signed}{width_text} {port['name']}"
        )
    lines = [
        f"module {module}(",
        ",\n".join(port_lines),
        ");",
        "",
        "    logic signed [31:0] start_hpos;",
        "",
        "    always_comb begin",
        "        start_hpos = hpos - (hpos % pixels_per_group);",
    ]
    sidebands = bindings["write_sidebands"]
    selected_ports = bindings["selected_ports"]
    component_ports = bindings["component_ports"]
    unit_start_ports = bindings["unit_start_ports"]
    reconstruction_ports = bindings["reconstruction_ports"]
    for sample in range(samples_per_unit):
        active = (
            "1'b1"
            if sample == 0
            else f"((hpos + 32'sd{sample - 1}) < slice_width)"
        )
        for unit in range(max_units):
            slot = sample * max_units + unit
            names = sidebands[slot]
            lines.extend(
                [
                    f"        {names['enable']} = "
                    f"(units_per_group > 32'sd{unit}) && "
                    f"({selected_ports[unit]} != 0) && {active};",
                    f"        {names['component']} = "
                    f"{component_ports[unit]}[1:0];",
                    f"        {names['address']} = start_hpos + "
                    f"32'sd{padding_left} + {unit_start_ports[unit]} + "
                    f"32'sd{sample};",
                    f"        {names['value']} = "
                    f"{reconstruction_ports[unit][sample]};",
                ]
            )
    lines.extend(["    end", "endmodule", ""])
    return "\n".join(lines)


def build_populate_orig_line_contract(
    selected: dict[str, Any], source_dir: pathlib.Path
) -> dict[str, Any]:
    """Freeze one memory-request transaction from the discovered C leaf."""
    function = selected["function"]
    name = str(function["name"])
    contract_id = safe_identifier(name) + "_encode_transition"
    component_count = int(selected["component_count"])
    padding_left = int(selected["padding_left"])
    padding_right = int(selected["padding_right"])
    max_slice_width = int(selected["max_slice_width"])
    max_slice_height = int(selected["max_slice_height"])
    _, start, end, body = source_body(function, source_dir)

    def input_port(
        port_name: str,
        lower: int,
        upper: int,
    ) -> dict[str, Any]:
        return {
            "name": port_name,
            "direction": "input",
            "width": 32,
            "signed": True,
            "legal_domain": {"range": [int(lower), int(upper)]},
        }

    ports: list[dict[str, Any]] = [
        input_port("native_420", 0, 1),
        input_port("native_422", 0, 1),
        input_port("xstart", 0, max_slice_width),
        input_port("ystart", 0, max_slice_height),
        input_port("num_components", 1, component_count),
        input_port("slice_width", 1, max_slice_width),
        input_port("pic_width", 1, max_slice_width),
        input_port("pic_height", 1, max_slice_height),
        input_port("vpos", 0, max_slice_height),
        input_port("component", 0, component_count - 1),
        input_port("sample_index", 0, max_slice_width + padding_right - 1),
        input_port("component_bit_depth", 1, 30),
        input_port("pixel_data", 0, (1 << 16) - 1),
        {
            "name": "read_enable",
            "direction": "output",
            "width": 1,
            "signed": False,
        },
        {
            "name": "read_plane",
            "direction": "output",
            "width": 2,
            "signed": False,
        },
        {
            "name": "read_y",
            "direction": "output",
            "width": 32,
            "signed": True,
        },
        {
            "name": "read_x",
            "direction": "output",
            "width": 32,
            "signed": True,
        },
        {
            "name": "write_enable",
            "direction": "output",
            "width": 1,
            "signed": False,
        },
        {
            "name": "write_component",
            "direction": "output",
            "width": 2,
            "signed": False,
        },
        {
            "name": "write_address",
            "direction": "output",
            "width": 32,
            "signed": True,
        },
        {
            "name": "write_value",
            "direction": "output",
            "width": 32,
            "signed": True,
        },
        {
            "name": "illegal_domain",
            "direction": "output",
            "width": 1,
            "signed": False,
        },
    ]
    input_names = [
        str(port["name"])
        for port in ports
        if port["direction"] == "input"
    ]
    output_names = [
        str(port["name"])
        for port in ports
        if port["direction"] == "output"
    ]
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
            "source_body_sha256": hashlib.sha256(
                body.encode("utf-8")
            ).hexdigest(),
            "parameters": function.get("parameters", []),
            "return_type": function.get("return_type"),
        },
        "interface": {"ports": ports},
        "semantics": {
            "kind": "populate_orig_line_memory_transition",
            "transactional": True,
            "component_count": component_count,
            "padding_left": padding_left,
            "padding_right": padding_right,
            "max_slice_width": max_slice_width,
            "max_slice_height": max_slice_height,
            "legal_domain": {
                "native_flags_are_binary_and_mutually_exclusive": True,
                "num_components": [1, component_count],
                "component_is_less_than_num_components": True,
                "slice_width": [1, max_slice_width],
                "sample_index": [0, max_slice_width + padding_right - 1],
                "picture_dimensions_positive": True,
                "component_bit_depth": [1, 30],
                "source_plane_memory_is_read_only_and_row_addressable": True,
                "orig_line_storage_covers_padding_left_and_right": True,
            },
            "bindings": {
                "config_parameter": selected["config_parameter"],
                "state_parameter": selected["state_parameter"],
                "picture_parameter": selected["picture_parameter"],
                "vpos_parameter": selected["vpos_parameter"],
                "native_420_field": "native_420",
                "native_422_field": "native_422",
                "xstart_field": "xstart",
                "ystart_field": "ystart",
                "num_components_field": "numComponents",
                "slice_width_field": "sliceWidth",
                "component_depth_field": "cpntBitDepth",
                "picture_width_field": "w",
                "picture_height_field": "h",
                "native_420_port": "native_420",
                "native_422_port": "native_422",
                "xstart_port": "xstart",
                "ystart_port": "ystart",
                "num_components_port": "num_components",
                "slice_width_port": "slice_width",
                "picture_width_port": "pic_width",
                "picture_height_port": "pic_height",
                "vpos_port": "vpos",
                "component_port": "component",
                "sample_index_port": "sample_index",
                "component_depth_port": "component_bit_depth",
                "pixel_data_port": "pixel_data",
                "read_enable_port": "read_enable",
                "read_plane_port": "read_plane",
                "read_y_port": "read_y",
                "read_x_port": "read_x",
                "write_enable_port": "write_enable",
                "write_component_port": "write_component",
                "write_address_port": "write_address",
                "write_value_port": "write_value",
                "illegal_domain_port": "illegal_domain",
                "input_ports": input_names,
                "output_ports": output_names,
            },
            "state_transition": (
                "produce one source-plane/y/x read request and, after the "
                "returned pixel is supplied, the exact origLine component, "
                "PADDING_LEFT address, and value"
            ),
            "external_memory": {
                "record": "pic_t",
                "read_only": True,
                "request_fields": ["read_enable", "read_plane", "read_y", "read_x"],
                "response_field": "pixel_data",
                "adapter_must_service_request": True,
            },
            "legal_vector_strategy": {
                "kind": "populate_orig_line",
                "exhaustive": False,
                "formal_required": False,
                "coverage_mode": (
                    "native-422-plane-map-plus-x-clamp-bottom-padding-"
                    "and-write-address-boundaries"
                ),
            },
        },
        "selection": {
            "basis": selected["selection_basis"],
            "encode_execution_count": selected["execution_count"],
        },
        "obligations": [
            "full-frame Encode C_ONLY/SHADOW/RTL_RETURN comparison",
            "the adapter must compare every touched origLine element and request metadata",
            "RTL_RETURN must commit the RTL-produced line image without C fallback",
            "human review of external picture-memory and address contract before promotion",
        ],
        "promotion": {
            "status": "BLOCKED_PENDING_HUMAN_CONTRACT_REVIEW",
            "simulation_may_proceed": True,
        },
    }


def render_populate_orig_line_rtl(contract: dict[str, Any]) -> str:
    """Render a single-cycle transaction over an external read-only picture."""
    semantics = contract["semantics"]
    module = safe_identifier(str(contract["contract_id"]))
    component_count = int(semantics["component_count"])
    padding_left = int(semantics["padding_left"])
    padding_right = int(semantics["padding_right"])
    max_slice_width = int(semantics["max_slice_width"])
    max_slice_height = int(semantics["max_slice_height"])
    ports = contract["interface"]["ports"]
    port_lines: list[str] = []
    for port in ports:
        direction = str(port["direction"])
        width = int(port["width"])
        signed = " signed" if port.get("signed") else ""
        width_text = f" [{width - 1}:0]" if width > 1 else ""
        port_lines.append(
            f"    {direction} logic{signed}{width_text} {port['name']}"
        )
    lines = [
        f"module {module}(",
        ",\n".join(port_lines),
        ");",
        "",
        "    integer xstart_i;",
        "    integer picture_width_i;",
        "    integer last_position_i;",
        "    integer y_raw_i;",
        "    integer y_index_i;",
        "    integer x_index_i;",
        "    logic legal_i;",
        "",
        "    always_comb begin",
        "        read_enable = 1'b0;",
        "        read_plane = 2'd0;",
        "        read_y = 32'sd0;",
        "        read_x = 32'sd0;",
        "        write_enable = 1'b0;",
        "        write_component = 2'd0;",
        "        write_address = 32'sd0;",
        "        write_value = 32'sd0;",
        "        illegal_domain = 1'b0;",
        "        xstart_i = 0;",
        "        picture_width_i = 0;",
        "        last_position_i = 0;",
        "        y_raw_i = 0;",
        "        y_index_i = 0;",
        "        x_index_i = 0;",
        "        legal_i = 1'b1;",
        f"        if (native_420 != 0 && native_422 != 0) legal_i = 1'b0;",
        f"        if (native_420 != 0 && native_420 != 1) legal_i = 1'b0;",
        f"        if (native_422 != 0 && native_422 != 1) legal_i = 1'b0;",
        f"        if (num_components < 1 || num_components > {component_count}) legal_i = 1'b0;",
        "        if (component < 0 || component >= num_components) legal_i = 1'b0;",
        f"        if (xstart < 0 || xstart > {max_slice_width}) legal_i = 1'b0;",
        f"        if (ystart < 0 || ystart > {max_slice_height}) legal_i = 1'b0;",
        f"        if (slice_width < 1 || slice_width > {max_slice_width}) legal_i = 1'b0;",
        f"        if (sample_index < 0 || sample_index >= slice_width + {padding_right}) legal_i = 1'b0;",
        f"        if (pic_width < 1 || pic_width > {max_slice_width}) legal_i = 1'b0;",
        f"        if (pic_height < 1 || pic_height > {max_slice_height}) legal_i = 1'b0;",
        f"        if (vpos < 0 || vpos > {max_slice_height}) legal_i = 1'b0;",
        "        if (component_bit_depth < 1 || component_bit_depth > 30) legal_i = 1'b0;",
        "        if (pixel_data < 0 || pixel_data > 65535) legal_i = 1'b0;",
        "        if (native_422 != 0 && pic_width < 2) legal_i = 1'b0;",
        "        if (native_422 == 0 && num_components > 3) legal_i = 1'b0;",
        "        if (native_422 != 0 && component >= 4) legal_i = 1'b0;",
        "        if (legal_i) begin",
        "            xstart_i = xstart;",
        "            if (native_420 != 0 || native_422 != 0)",
        "                xstart_i = xstart >>> 1;",
        "            picture_width_i = pic_width;",
        "            if (native_422 != 0 && component >= 1 && component <= 2)",
        "                picture_width_i = pic_width >>> 1;",
            "            y_raw_i = ystart + vpos;",
        "            if (y_raw_i < pic_height)",
        "                y_index_i = y_raw_i;",
        "            else",
        "                y_index_i = pic_height - 1;",
        "            if (native_422 != 0 && (component == 0 || component == 3)) begin",
        "                if (picture_width_i < (xstart_i + slice_width) * 2)",
                "                    last_position_i = picture_width_i - 1;",
                "                else",
                "                    last_position_i = (xstart_i + slice_width) * 2 - 1;",
                "            end else begin",
                "                if (picture_width_i < xstart_i + slice_width)",
                "                    last_position_i = picture_width_i - 1;",
                "                else",
                "                    last_position_i = xstart_i + slice_width - 1;",
                "            end",
                "            if (native_422 != 0 && component == 0) begin",
                "                read_plane = 2'd0;",
                "                x_index_i = (xstart_i + sample_index) * 2;",
                "            end else if (native_422 != 0 && component == 1) begin",
                "                read_plane = 2'd1;",
                "                x_index_i = xstart_i + sample_index;",
                "            end else if (native_422 != 0 && component == 2) begin",
                "                read_plane = 2'd2;",
                "                x_index_i = xstart_i + sample_index;",
                "            end else if (native_422 != 0 && component == 3) begin",
                "                read_plane = 2'd0;",
                "                x_index_i = (xstart_i + sample_index) * 2 + 1;",
                "            end else if (component == 0) begin",
                "                read_plane = 2'd0;",
                "                x_index_i = xstart_i + sample_index;",
                "            end else if (component == 1) begin",
                "                read_plane = 2'd1;",
                "                x_index_i = xstart_i + sample_index;",
                "            end else begin",
                "                read_plane = 2'd2;",
                "                x_index_i = xstart_i + sample_index;",
                "            end",
                "            if (x_index_i > last_position_i)",
                "                x_index_i = last_position_i;",
                "            read_enable = (y_raw_i < pic_height);",
                "            read_y = y_index_i;",
                "            read_x = x_index_i;",
                "            write_enable = 1'b1;",
                "            write_component = component[1:0];",
                f"            write_address = sample_index + 32'sd{padding_left};",
                "            if (read_enable)",
                "                write_value = pixel_data;",
                "            else",
                "                write_value = 32'sd1 <<< (component_bit_depth - 1);",
                "        end else begin",
                "            illegal_domain = 1'b1;",
                "        end",
                "    end",
                "endmodule",
                "",
            ]
    return "\n".join(lines)


def build_ich_decision_contract(
    selected: dict[str, Any], source_dir: pathlib.Path
) -> dict[str, Any]:
    function = selected["function"]
    name = str(function["name"])
    contract_id = safe_identifier(name) + "_encode_transition"
    max_units = int(selected["max_units"])
    _, start, end, body = source_body(function, source_dir)
    ports: list[dict[str, Any]] = [
        {
            "name": name,
            "direction": "input",
            "width": 32,
            "signed": True,
        }
        for name in (
            "adjusted_predicted_size",
            "alternate_prefix",
            "alternate_size",
            "version_minor",
            "units_per_group",
            "previous_ich_selected",
            "ich_indices_in_group",
        )
    ]
    for role in (
        "max_mid_error",
        "max_error",
        "max_ich_error",
        "using_midpoint",
    ):
        ports.extend(
            {
                "name": f"{role}_{unit}",
                "direction": "input",
                "width": 32,
                "signed": True,
            }
            for unit in range(max_units)
        )
    ports.extend(
        [
            {
                "name": "estimated_p_mode_bits",
                "direction": "input",
                "width": 32,
                "signed": True,
            },
            {
                "name": "original_flat_index",
                "direction": "input",
                "width": 32,
                "signed": True,
            },
            {
                "name": "return_value",
                "direction": "output",
                "width": 1,
                "signed": False,
            },
        ]
    )
    dependencies = []
    for dependency_name, dependency in sorted(
        selected["dependencies"].items()
    ):
        dependency_contract = dependency["contract"]
        dependencies.append(
            {
                "function": dependency_name,
                "contract_id": dependency_contract.get("contract_id"),
                "contract_sha256": dependency["contract_sha256"],
                "module_sha256": dependency["module_sha256"],
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
            "source_body_sha256": hashlib.sha256(
                body.encode("utf-8")
            ).hexdigest(),
            "parameters": function.get("parameters", []),
            "return_type": function.get("return_type"),
        },
        "interface": {"ports": ports},
        "semantics": {
            "kind": "bounded_ich_decision_transition",
            "max_units": max_units,
            "ich_bits": int(selected["ich_bits"]),
            "ich_lambda": int(selected["ich_lambda"]),
            "legal_domain": {
                "units_per_group": [0, max_units],
                "error_magnitudes_nonnegative": True,
                "version_minor_values": [1, 2],
                "child_calls_within_their_accepted_domains": True,
            },
            "bindings": {
                "config_parameter": selected["config_parameter"],
                "state_parameter": selected["state_parameter"],
                "adjusted_size_parameter": selected[
                    "adjusted_size_parameter"
                ],
                "alternate_prefix_parameter": selected[
                    "alternate_prefix_parameter"
                ],
                "alternate_size_parameter": selected[
                    "alternate_size_parameter"
                ],
                "version_field": selected["version_field"],
                "units_field": selected["units_field"],
                "previous_ich_field": selected[
                    "previous_ich_field"
                ],
                "ich_indices_field": selected["ich_indices_field"],
                "hpos_field": selected["hpos_field"],
                "unit_type_field": selected["unit_type_field"],
                "max_mid_error_field": selected[
                    "max_mid_error_field"
                ],
                "max_error_field": selected["max_error_field"],
                "max_ich_error_field": selected[
                    "max_ich_error_field"
                ],
                "midpoint_callee": selected["midpoint_callee"],
                "estimate_callee": selected["estimate_callee"],
                "flat_callee": selected["flat_callee"],
                "log_callee": selected["log_callee"],
                "adjusted_size_port": "adjusted_predicted_size",
                "alternate_prefix_port": "alternate_prefix",
                "alternate_size_port": "alternate_size",
                "version_port": "version_minor",
                "units_port": "units_per_group",
                "previous_ich_port": "previous_ich_selected",
                "ich_indices_port": "ich_indices_in_group",
                "max_mid_error_ports": [
                    f"max_mid_error_{unit}"
                    for unit in range(max_units)
                ],
                "max_error_ports": [
                    f"max_error_{unit}" for unit in range(max_units)
                ],
                "max_ich_error_ports": [
                    f"max_ich_error_{unit}"
                    for unit in range(max_units)
                ],
                "using_midpoint_ports": [
                    f"using_midpoint_{unit}"
                    for unit in range(max_units)
                ],
                "estimated_bits_port": "estimated_p_mode_bits",
                "flat_index_port": "original_flat_index",
                "return_port": "return_value",
            },
            "state_transition": (
                "select predictive or ICH mode from child RTL results and "
                "fixed-lane error-cost reduction with exact DSC 1.1/1.2 branches"
            ),
        },
        "composition": {
            "dependencies": dependencies,
            "child_results": (
                "accepted midpoint, P-mode bit estimate, and flat-index "
                "functions are invoked by the adapter and become RTL calls "
                "in the simultaneous replacement executable"
            ),
            "logarithm_helper": (
                "accepted scalar helper semantics are inlined exactly in "
                "the generated parent RTL"
            ),
        },
        "selection": {
            "basis": selected["selection_basis"],
            "encode_execution_count": selected["execution_count"],
        },
        "obligations": [
            "full-frame Encode C_ONLY/SHADOW/RTL_RETURN comparison",
            "simultaneous all-RTL integration must replace every composed child",
            "human review of composed child-result boundary before promotion",
        ],
        "promotion": {
            "status": "BLOCKED_PENDING_HUMAN_CONTRACT_REVIEW",
            "simulation_may_proceed": True,
        },
    }


def render_ich_decision_rtl(contract: dict[str, Any]) -> str:
    semantics = contract["semantics"]
    bindings = semantics["bindings"]
    module = safe_identifier(str(contract["contract_id"]))
    max_units = int(semantics["max_units"])
    ich_bits = int(semantics["ich_bits"])
    ich_lambda = int(semantics["ich_lambda"])
    ports = contract["interface"]["ports"]
    port_lines: list[str] = []
    for port in ports:
        direction = str(port["direction"])
        width = int(port["width"])
        signed = " signed" if port.get("signed") else ""
        width_text = f" [{width - 1}:0]" if width > 1 else ""
        port_lines.append(
            f"    {direction} logic{signed}{width_text} {port['name']}"
        )
    max_mid_ports = bindings["max_mid_error_ports"]
    max_error_ports = bindings["max_error_ports"]
    max_ich_ports = bindings["max_ich_error_ports"]
    using_ports = bindings["using_midpoint_ports"]
    lines = [
        f"module {module}(",
        ",\n".join(port_lines),
        ");",
        "",
        "    logic signed [31:0] log_error_p_mode;",
        "    logic signed [31:0] log_error_ich_mode;",
        "    logic signed [31:0] bits_ich_mode;",
        "    logic signed [31:0] p_mode_cost;",
        "    logic signed [31:0] ich_mode_cost;",
        "",
        "    function automatic signed [31:0] c_ceil_log2(",
        "        input logic signed [31:0] value",
        "    );",
        "        logic [31:0] x;",
        "        integer bit_index;",
        "        begin",
        "            x = value[31:0];",
        "            c_ceil_log2 = 32'sd0;",
        "            for (bit_index = 0; bit_index < 32; "
        "bit_index = bit_index + 1) begin",
        "                if (x != 0) begin",
        "                    c_ceil_log2 = c_ceil_log2 + 32'sd1;",
        "                    x = x >> 1;",
        "                end",
        "            end",
        "        end",
        "    endfunction",
        "",
        "    always_comb begin",
        "        if (previous_ich_selected != 0)",
        "            bits_ich_mode = 32'sd1;",
        "        else",
        "            bits_ich_mode = alternate_size "
        "- adjusted_predicted_size;",
        f"        bits_ich_mode = bits_ich_mode + "
        f"(32'sd{ich_bits} * ich_indices_in_group) "
        "+ (alternate_prefix & 32'sd0);",
        "        log_error_p_mode = 32'sd0;",
        "        log_error_ich_mode = 32'sd0;",
    ]
    for unit in range(max_units):
        lines.extend(
            [
                f"        if (units_per_group > 32'sd{unit}) begin",
                f"            if ({using_ports[unit]} != 0)",
                "                log_error_p_mode = log_error_p_mode + "
                f"c_ceil_log2({max_mid_ports[unit]});",
                "            else",
                "                log_error_p_mode = log_error_p_mode + "
                f"c_ceil_log2({max_error_ports[unit]});",
                "            log_error_ich_mode = log_error_ich_mode + "
                f"c_ceil_log2({max_ich_ports[unit]});",
            ]
        )
        if unit == 0:
            lines.extend(
                [
                    "            if (version_minor == 32'sd1) begin",
                    "                log_error_p_mode = "
                    "log_error_p_mode * 32'sd2;",
                    "                log_error_ich_mode = "
                    "log_error_ich_mode * 32'sd2;",
                    "            end",
                ]
            )
        lines.append("        end")
    lines.extend(
        [
            f"        p_mode_cost = estimated_p_mode_bits + "
            f"(32'sd{ich_lambda} * log_error_p_mode);",
            f"        ich_mode_cost = bits_ich_mode + "
            f"(32'sd{ich_lambda} * log_error_ich_mode);",
            "        if (version_minor == 32'sd2) begin",
            "            if (original_flat_index == 32'sd2)",
            "                return_value = "
            "(log_error_ich_mode <= log_error_p_mode) && "
            "(ich_mode_cost < p_mode_cost);",
            "            else",
            "                return_value = ich_mode_cost < p_mode_cost;",
            "        end else begin",
            "            return_value = "
            "(log_error_ich_mode <= log_error_p_mode) && "
            "(ich_mode_cost < p_mode_cost);",
            "        end",
            "    end",
            "endmodule",
            "",
        ]
    )
    return "\n".join(lines)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--semantics",
        choices=(
            "bitstream-write",
            "fifo-write-accounting",
            "midpoint-line-write",
            "populate-orig-line",
            "ich-decision",
        ),
        default="bitstream-write",
    )
    parser.add_argument("--functions", type=pathlib.Path, required=True)
    parser.add_argument("--candidates", type=pathlib.Path, required=True)
    parser.add_argument("--coverage", type=pathlib.Path, required=True)
    parser.add_argument("--source-dir", type=pathlib.Path, required=True)
    parser.add_argument("--provisional-root", type=pathlib.Path)
    parser.add_argument("--manifest", type=pathlib.Path)
    parser.add_argument("--output-dir", type=pathlib.Path, required=True)
    return parser.parse_args()


def match_receipt(item: dict[str, Any]) -> dict[str, Any]:
    result = {
        key: value
        for key, value in item.items()
        if key not in {"function", "dependency", "dependencies"}
    }
    dependency = item.get("dependency")
    if isinstance(dependency, dict):
        contract = dependency.get("contract", {}) or {}
        result["dependency"] = {
            "contract_id": contract.get("contract_id"),
            "function": (
                contract.get("function", {}) or {}
            ).get("name"),
            "contract_sha256": dependency.get(
                "contract_sha256"
            ),
            "candidate_sha256": dependency.get(
                "candidate_sha256"
            ),
            "encode_rtl_return_invocations": dependency.get(
                "rtl_return_invocations"
            ),
        }
    dependencies = item.get("dependencies")
    if isinstance(dependencies, dict):
        result["dependencies"] = [
            {
                "function": name,
                "contract_id": (
                    value.get("contract", {}) or {}
                ).get("contract_id"),
                "contract_sha256": value.get("contract_sha256"),
                "module_sha256": value.get("module_sha256"),
            }
            for name, value in sorted(dependencies.items())
            if isinstance(value, dict)
        ]
    return result


def main() -> int:
    args = parse_args()
    source_dir = args.source_dir.resolve()
    functions_document = read_json(args.functions)
    candidates_document = read_json(args.candidates)
    coverage_document = read_json(args.coverage)
    if args.semantics == "bitstream-write":
        matches = discover_bitstream_write_candidates(
            functions_document,
            candidates_document,
            coverage_document,
            source_dir,
        )
        description = "bounded bitstream-write"
        contract_builder = build_bitstream_write_contract
        rtl_renderer = render_bitstream_write_rtl
    elif args.semantics == "fifo-write-accounting":
        if args.provisional_root is None:
            raise SystemExit(
                "--provisional-root is required for composed FIFO accounting"
            )
        verified = scan_phase_verified_contracts(
            args.provisional_root.resolve(), "encode"
        )
        matches = discover_fifo_write_accounting_candidates(
            functions_document,
            candidates_document,
            coverage_document,
            source_dir,
            verified,
        )
        description = "composed FIFO-write accounting"
        contract_builder = build_fifo_write_accounting_contract
        rtl_renderer = render_fifo_write_accounting_rtl
    elif args.semantics == "midpoint-line-write":
        matches = discover_midpoint_line_write_candidates(
            functions_document,
            candidates_document,
            coverage_document,
            source_dir,
        )
        description = "bounded midpoint reconstructed-line write"
        contract_builder = build_midpoint_line_write_contract
        rtl_renderer = render_midpoint_line_write_rtl
    elif args.semantics == "populate-orig-line":
        matches = discover_populate_orig_line_candidates(
            functions_document,
            candidates_document,
            coverage_document,
            source_dir,
        )
        description = "bounded picture-memory original-line transaction"
        contract_builder = build_populate_orig_line_contract
        rtl_renderer = render_populate_orig_line_rtl
    else:
        if args.manifest is None:
            raise SystemExit(
                "--manifest is required for composed ICH decision"
            )
        manifest_path = args.manifest.resolve()
        stable = scan_stable_contracts(
            read_json(manifest_path), manifest_path.parent.parent
        )
        matches = discover_ich_decision_candidates(
            functions_document,
            candidates_document,
            coverage_document,
            source_dir,
            stable,
        )
        description = "bounded composed ICH decision"
        contract_builder = build_ich_decision_contract
        rtl_renderer = render_ich_decision_rtl
    if not matches:
        raise SystemExit(
            f"no covered {description} transition was tool-discovered"
        )
    selected = matches[0]
    contract = contract_builder(selected, source_dir)
    output = args.output_dir.resolve()
    write_json(output / "provisional-contract.json", contract)
    (output / "candidate_01.sv").parent.mkdir(parents=True, exist_ok=True)
    (output / "candidate_01.sv").write_text(
        rtl_renderer(contract), encoding="utf-8"
    )
    write_json(
        output / "generation-receipt.json",
        {
            "schema_version": 1,
            "status": "PASS",
            "selection_policy": (
                "highest Encode execution count among structural bounded "
                f"{description} matches; no function-name allowlist"
            ),
            "match_count": len(matches),
            "matches": [match_receipt(item) for item in matches],
            "selected_function": selected["name"],
            "selected_clang_usr": selected["clang_usr"],
            "contract_id": contract["contract_id"],
            "candidate": "candidate_01.sv",
            "promotion_status": "BLOCKED_PENDING_HUMAN_CONTRACT_REVIEW",
        },
    )
    print(
        "generated provisional Encode transition: "
        f"{contract['contract_id']} ({selected['execution_count']} calls)"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
