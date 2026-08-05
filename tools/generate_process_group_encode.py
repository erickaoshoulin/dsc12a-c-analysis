#!/usr/bin/env python3
"""Discover and generate the encoder ProcessGroup transition.

This module deliberately discovers the target from Clang facts, Encode-phase
coverage, loop shape, field effects, and callee roles.  Function names are
reported metadata only; they are not admission predicates.

The generated RTL is a bounded encoder-only sequential FSM.  It inlines the
already pinned bit-level contracts for the FIFO reader, FIFO writer, and
bitstream writer, while exposing their memory effects through external
request/write ports.  The generated artifact is simulation-only until the
normal human contract-review gate is completed.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import pathlib
import re
from dataclasses import dataclass
from typing import Any, Iterable, Mapping, Sequence


MAX_SSPS = 4
MIN_SSPS = 3
MUX_WORD_SIZES = (48, 64)
MAX_SE_SIZE_BOUND = 68  # 4 * max legal DSC bpc (16) + 4
FIFO_ADDR_WIDTH = 16
FRAME_ADDR_WIDTH = 32


class DiscoveryError(RuntimeError):
    """Raised when structural discovery or dependency admission is ambiguous."""


def _read_json(path: pathlib.Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def _write_json(path: pathlib.Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(value, indent=2, sort_keys=True, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )


def _sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def _sha256_text(value: str) -> str:
    return _sha256_bytes(value.encode("utf-8"))


def _rows(document: Any, key: str | None = None) -> list[dict[str, Any]]:
    if isinstance(document, list):
        return [item for item in document if isinstance(item, dict)]
    if not isinstance(document, dict):
        return []
    value = document.get(key, []) if key else document
    if isinstance(value, list):
        return [item for item in value if isinstance(item, dict)]
    return []


def _normal_type(value: Any) -> str:
    return re.sub(r"\s+", " ", str(value or "").strip())


def _parameter_types(function: Mapping[str, Any]) -> list[str]:
    return [_normal_type(item.get("type")) for item in function.get("parameters", []) or []]


def _callee_usrs(function: Mapping[str, Any]) -> set[str]:
    result: set[str] = set()
    for item in function.get("calls", []) or []:
        if isinstance(item, dict) and item.get("clang_usr"):
            result.add(str(item["clang_usr"]))
    for item in function.get("callees", []) or []:
        if isinstance(item, dict) and item.get("clang_usr"):
            result.add(str(item["clang_usr"]))
    return result


def _call_names(function: Mapping[str, Any]) -> set[str]:
    return {
        str(item.get("name"))
        for item in function.get("calls", []) or []
        if isinstance(item, dict) and item.get("name")
    }


def _field_names(function: Mapping[str, Any], key: str) -> set[str]:
    return {
        str(item.get("name"))
        for item in function.get(key, []) or []
        if isinstance(item, dict) and item.get("name")
    }


def _covered_row(row: Mapping[str, Any]) -> tuple[bool, int]:
    coverage = row.get("coverage", {}) or {}
    count = int(coverage.get("execution_count", row.get("execution_count", 0)) or 0)
    covered = bool(coverage.get("covered", row.get("covered", count > 0)))
    return covered and count > 0, count


def _coverage_by_usr(*documents: Any) -> dict[str, tuple[bool, int, dict[str, Any]]]:
    result: dict[str, tuple[bool, int, dict[str, Any]]] = {}
    for document in documents:
        rows = _rows(document, "functions")
        if not rows and isinstance(document, dict):
            for key in ("reached", "rtl", "compute_gap", "c_shell"):
                rows.extend(_rows(document, key))
        for row in rows:
            usr = row.get("clang_usr")
            if not usr:
                continue
            covered, count = _covered_row(row)
            # The first document is authoritative.  The optional frontier is
            # only a fallback for a function absent from the primary Encode
            # coverage export; it must not resurrect a row explicitly marked
            # uncovered in that export.
            if str(usr) not in result:
                result[str(usr)] = (covered, count, row)
    return result


def _loop_conditions(function: Mapping[str, Any]) -> list[str]:
    return [
        str(item.get("condition", ""))
        for item in function.get("loops", []) or []
        if isinstance(item, dict)
    ]


def _has_fifo_read_role(function: Mapping[str, Any]) -> bool:
    if _normal_type(function.get("return_type")) not in {"int", "signed int"}:
        return False
    if _parameter_types(function) != ["fifo_t *", "int", "int"]:
        return False
    reads = _field_names(function, "fields_read")
    writes = _field_names(function, "fields_write")
    return {"data", "fullness", "read_ptr"}.issubset(reads) and {
        "fullness",
        "read_ptr",
    }.issubset(writes)


def _has_fifo_write_role(function: Mapping[str, Any]) -> bool:
    if _normal_type(function.get("return_type")) != "void":
        return False
    if _parameter_types(function) != ["fifo_t *", "unsigned int", "int"]:
        return False
    reads = _field_names(function, "fields_read")
    writes = _field_names(function, "fields_write")
    return {"data", "fullness", "write_ptr", "max_fullness"}.issubset(writes) and {
        "size",
        "fullness",
        "write_ptr",
    }.issubset(reads)


def _has_bitstream_write_role(function: Mapping[str, Any]) -> bool:
    if _normal_type(function.get("return_type")) != "void":
        return False
    if _parameter_types(function) != ["int", "int", "unsigned char *", "int *"]:
        return False
    loops = _loop_conditions(function)
    pointer_modes = {
        str(item.get("name")): str(item.get("mode"))
        for item in function.get("pointer_parameters", []) or []
        if isinstance(item, dict)
    }
    return (
        len(loops) == 1
        and int(function.get("loop_count", 0) or 0) == 1
        and pointer_modes.get("buf") in {"WRITES_THROUGH", "UNKNOWN", ""}
        and pointer_modes.get("bit_count") in {"WRITES_THROUGH", "UNKNOWN", ""}
    )


def _source_text(source_dir: pathlib.Path, function: Mapping[str, Any]) -> str:
    path = source_dir / str(function.get("source_file", ""))
    if not path.is_file():
        raise DiscoveryError(f"source file is missing: {path}")
    lines = path.read_text(encoding="utf-8", errors="replace").splitlines()
    start = int(function.get("line", 0) or 0)
    end = int(function.get("end_line", 0) or 0)
    if start <= 0 or end < start or end > len(lines):
        raise DiscoveryError(
            f"invalid source span for {function.get('clang_usr')}: {start}..{end}"
        )
    return "\n".join(lines[start - 1 : end])


def source_body_sha256(source_dir: pathlib.Path, function: Mapping[str, Any]) -> str:
    return _sha256_text(_source_text(source_dir, function))


def _structural_target_score(
    function: Mapping[str, Any],
    functions_by_usr: Mapping[str, Mapping[str, Any]],
    source_dir: pathlib.Path,
) -> tuple[int, list[str]]:
    reasons: list[str] = []
    score = 0
    if _normal_type(function.get("return_type")) == "void":
        score += 2
        reasons.append("void-return")
    if _parameter_types(function) == ["dsc_cfg_t *", "dsc_state_t *", "unsigned char *"]:
        score += 5
        reasons.append("config-state-frame-pointer-shape")
    else:
        return -1, reasons

    conditions = _loop_conditions(function)
    if len(conditions) == 2:
        score += 2
        reasons.append("two-nested-loop-facts")
    if conditions and "numSsps" in conditions[0] and "<" in conditions[0]:
        score += 4
        reasons.append("ssp-loop-bound")
    if len(conditions) > 1 and "mux_word_size" in conditions[1] and "/ 8" in conditions[1]:
        score += 4
        reasons.append("mux-byte-loop-bound")
    if int(function.get("loop_count", 0) or 0) == 2:
        score += 2
        reasons.append("two-loop-count")

    fields = _field_names(function, "fields_read")
    required_fields = {
        "encBalanceFifo",
        "seSizeFifo",
        "shifter",
        "maxSeSize",
        "numSsps",
        "postMuxNumBits",
        "mux_word_size",
        "isEncoder",
    }
    field_hits = required_fields.intersection(fields)
    score += len(field_hits)
    reasons.extend(f"field:{item}" for item in sorted(field_hits))
    if len(field_hits) >= 7:
        score += 5

    calls = _callee_usrs(function)
    roles = {
        "fifo_read": [usr for usr in calls if _has_fifo_read_role(functions_by_usr.get(usr, {}))],
        "fifo_write": [usr for usr in calls if _has_fifo_write_role(functions_by_usr.get(usr, {}))],
        "bitstream_write": [usr for usr in calls if _has_bitstream_write_role(functions_by_usr.get(usr, {}))],
    }
    for role, matches in roles.items():
        if matches:
            score += 8
            reasons.append(f"callee-role:{role}")
    if all(roles.values()):
        score += 12
        reasons.append("three-pinned-callee-roles")
    else:
        return -1, reasons

    try:
        body = _source_text(source_dir, function)
    except DiscoveryError:
        return -1, reasons
    source_markers = (
        "dsc_state->isEncoder",
        "dsc_state->shifter",
        "dsc_state->maxSeSize",
        "dsc_state->encBalanceFifo",
        "dsc_state->seSizeFifo",
        "dsc_state->postMuxNumBits",
    )
    marker_hits = sum(marker in body for marker in source_markers)
    if marker_hits == len(source_markers):
        score += 12
        reasons.append("source-state-effects")
    else:
        return -1, reasons
    if "fifo_get_bits" in body and "fifo_put_bits" in body and "putbits" in body:
        score += 8
        reasons.append("source-call-order-markers")
    else:
        return -1, reasons
    if "if (dsc_state->isEncoder)" in body:
        score += 3
        reasons.append("encoder-branch")
    return score, reasons


def discover_process_group_candidate(
    functions_document: Any,
    coverage_document: Any,
    source_dir: pathlib.Path,
    *,
    encode_frontier_document: Any | None = None,
) -> dict[str, Any]:
    """Return the unique structural target reached by Encode coverage.

    The function's spelling is never consulted.  A renamed function with the
    same Clang facts and source span remains discoverable, while decoder-only
    mux code does not satisfy the encoder branch/effect fingerprint.
    """

    functions = _rows(functions_document, "functions")
    functions_by_usr = {
        str(item.get("clang_usr")): item
        for item in functions
        if item.get("clang_usr")
    }
    coverage = _coverage_by_usr(coverage_document, encode_frontier_document)
    matches: list[dict[str, Any]] = []
    for function in functions:
        usr = str(function.get("clang_usr", ""))
        covered, count, coverage_row = coverage.get(usr, (False, 0, {}))
        if not covered or count <= 0:
            continue
        score, reasons = _structural_target_score(function, functions_by_usr, source_dir)
        if score >= 0:
            matches.append(
                {
                    "function": function,
                    "coverage": coverage_row,
                    "execution_count": count,
                    "score": score,
                    "reasons": reasons,
                }
            )
    if not matches:
        raise DiscoveryError("Encode coverage contains no structural mux encoder target")
    matches.sort(
        key=lambda item: (
            -int(item["score"]),
            -int(item["execution_count"]),
            str(item["function"].get("clang_usr", "")),
        )
    )
    if len(matches) > 1 and matches[0]["score"] == matches[1]["score"]:
        usrs = [str(item["function"].get("clang_usr")) for item in matches]
        raise DiscoveryError(f"ambiguous structural Encode targets: {usrs}")
    selected = matches[0]
    return {
        "clang_usr": selected["function"].get("clang_usr"),
        "name": selected["function"].get("name"),
        "source_file": selected["function"].get("source_file"),
        "source_span": {
            "start_line": int(selected["function"].get("line", 0)),
            "end_line": int(selected["function"].get("end_line", 0)),
        },
        "source_body_sha256": source_body_sha256(source_dir, selected["function"]),
        "execution_count": selected["execution_count"],
        "structural_score": selected["score"],
        "structural_evidence": selected["reasons"],
        "coverage": selected["coverage"],
        "function": selected["function"],
    }


@dataclass(frozen=True)
class DependencyPin:
    kind: str
    contract_path: str
    contract_sha256: str
    contract_id: str
    clang_usr: str
    function_name: str
    source_file: str
    source_span: dict[str, int]
    source_body_sha256: str
    source_file_sha256: str
    module_path: str
    module_sha256: str
    module: str

    def as_dict(self) -> dict[str, Any]:
        return {
            "kind": self.kind,
            "contract_path": self.contract_path,
            "contract_sha256": self.contract_sha256,
            "contract_id": self.contract_id,
            "clang_usr": self.clang_usr,
            "function_name": self.function_name,
            "source_file": self.source_file,
            "source_span": self.source_span,
            "source_body_sha256": self.source_body_sha256,
            "source_file_sha256": self.source_file_sha256,
            "module_path": self.module_path,
            "module_sha256": self.module_sha256,
            "module": self.module,
        }


def _default_source_dir(root: pathlib.Path) -> pathlib.Path:
    receipt_path = root / "facts" / "build-receipt.json"
    if receipt_path.is_file():
        receipt = _read_json(receipt_path)
        model_root = receipt.get("model_root")
        if model_root:
            candidate = pathlib.Path(str(model_root)) / "source"
            if candidate.is_dir():
                return candidate
    compile_commands = root / "facts" / "compile_commands.json"
    if compile_commands.is_file():
        for row in _read_json(compile_commands):
            directory = row.get("directory")
            if directory and (pathlib.Path(directory) / "multiplex.c").is_file():
                return pathlib.Path(directory)
    raise DiscoveryError("cannot locate immutable DSC source directory")


def _dependency_contract_paths(
    root: pathlib.Path, explicit: Sequence[pathlib.Path] | None
) -> list[pathlib.Path]:
    if explicit:
        return [pathlib.Path(path) for path in explicit]
    return sorted(root.glob("rtl/**/provisional-contract.json"))


def _contract_function(document: Mapping[str, Any]) -> Mapping[str, Any]:
    function = document.get("function")
    if not isinstance(function, dict):
        raise DiscoveryError("dependency contract has no function record")
    span = function.get("source_span", {})
    if not isinstance(span, dict):
        raise DiscoveryError("dependency contract has no source span")
    return function


def _pin_contract(
    path: pathlib.Path,
    source_dir: pathlib.Path,
    expected_kind: str,
) -> DependencyPin:
    raw = path.read_bytes()
    document = json.loads(raw.decode("utf-8"))
    semantics = document.get("semantics", {}) or {}
    if semantics.get("kind") != expected_kind:
        raise DiscoveryError(f"{path} is not a {expected_kind} contract")
    function = _contract_function(document)
    source_file = str(function.get("source_file", ""))
    source_path = source_dir / source_file
    if not source_path.is_file():
        raise DiscoveryError(f"dependency source file is missing: {source_path}")
    span = function["source_span"]
    start = int(span.get("start_line", 0))
    end = int(span.get("end_line", 0))
    lines = source_path.read_text(encoding="utf-8", errors="replace").splitlines()
    if start <= 0 or end < start or end > len(lines):
        raise DiscoveryError(f"invalid dependency source span in {path}: {start}..{end}")
    body_hash = _sha256_text("\n".join(lines[start - 1 : end]))
    expected_body_hash = str(function.get("source_body_sha256", ""))
    if body_hash != expected_body_hash:
        raise DiscoveryError(
            f"dependency source hash mismatch for {path}: "
            f"expected {expected_body_hash}, actual {body_hash}"
        )
    module_path = path.parent / "candidate_01.sv"
    if not module_path.is_file():
        raise DiscoveryError(
            f"dependency RTL candidate is missing beside {path}: {module_path}"
        )
    return DependencyPin(
        kind=expected_kind,
        contract_path=str(path),
        contract_sha256=_sha256_bytes(raw),
        contract_id=str(document.get("contract_id", "")),
        clang_usr=str(function.get("clang_usr", "")),
        function_name=str(function.get("name", "")),
        source_file=source_file,
        source_span={"start_line": start, "end_line": end},
        source_body_sha256=body_hash,
        source_file_sha256=_sha256_bytes(source_path.read_bytes()),
        module_path=str(module_path),
        module_sha256=_sha256_bytes(module_path.read_bytes()),
        module=re.sub(
            r"[^A-Za-z0-9_]", "_", str(document.get("contract_id", ""))
        ),
    )


def discover_dependency_pins(
    root: pathlib.Path,
    source_dir: pathlib.Path | None = None,
    *,
    contract_paths: Sequence[pathlib.Path] | None = None,
) -> dict[str, DependencyPin]:
    """Find dependency contracts by semantic role and verify both hashes."""

    source_dir = source_dir or _default_source_dir(root)
    by_kind: dict[str, list[pathlib.Path]] = {
        "fifo_read_transition": [],
        "fifo_write_transition": [],
        "bitstream_write_transition": [],
    }
    for path in _dependency_contract_paths(root, contract_paths):
        try:
            document = _read_json(path)
        except (OSError, json.JSONDecodeError):
            continue
        kind = (document.get("semantics", {}) or {}).get("kind")
        if kind in by_kind:
            by_kind[str(kind)].append(path)

    pins: dict[str, DependencyPin] = {}
    for kind, paths in by_kind.items():
        if not paths:
            raise DiscoveryError(f"missing pinned dependency contract: {kind}")
        candidates: list[DependencyPin] = []
        errors: list[str] = []
        for path in paths:
            try:
                candidates.append(_pin_contract(path, source_dir, kind))
            except DiscoveryError as exc:
                errors.append(str(exc))
        if not candidates:
            raise DiscoveryError("; ".join(errors))
        source_hashes = {item.source_body_sha256 for item in candidates}
        if len(source_hashes) != 1:
            raise DiscoveryError(f"ambiguous source hashes for dependency kind {kind}")
        candidates.sort(key=lambda item: item.contract_path)
        pins[kind] = candidates[0]
    return pins


def _port(name: str, direction: str, width: str, *, unpacked: str = "") -> dict[str, Any]:
    return {
        "name": name,
        "direction": direction,
        "width": width,
        "unpacked": unpacked,
    }


def contract_interface() -> list[dict[str, Any]]:
    """Return the complete scalar and external-memory interface description."""

    ports = [
        _port("clk", "input", "1"),
        _port("rst_n", "input", "1"),
        _port("start", "input", "1"),
        _port("is_encoder", "input", "1"),
        _port("num_ssps", "input", "3"),
        _port("mux_word_size", "input", "7"),
        _port("max_se_size", "input", "7", unpacked="[0:3]"),
        _port("frame_capacity_bits", "input", "32"),
        _port("busy", "output", "1"),
        _port("done", "output", "1"),
        _port("illegal_domain", "output", "1"),
        _port("fifo_underflow", "output", "1"),
        _port("fifo_overflow", "output", "1"),
        _port("frame_overflow", "output", "1"),
        _port("se_size_overflow", "output", "1"),
        _port("post_mux_num_bits_in", "input", "32"),
        _port("post_mux_num_bits_out", "output", "32"),
    ]
    for prefix in ("enc_balance", "shifter", "se_size"):
        for field in (
            "size_bits",
            "fullness",
            "read_ptr",
            "write_ptr",
            "max_fullness",
            "byte_ctr",
        ):
            ports.append(_port(f"{prefix}_{field}_in", "input", "32", unpacked="[0:3]"))
            ports.append(_port(f"{prefix}_{field}_out", "output", "32", unpacked="[0:3]"))
        ports.extend(
            [
                _port(f"{prefix}_mem_read_req", "output", "4"),
                _port(
                    f"{prefix}_mem_read_addr",
                    "output",
                    f"{FIFO_ADDR_WIDTH}",
                    unpacked="[0:3]",
                ),
                _port(f"{prefix}_mem_read_valid", "input", "4"),
                _port(f"{prefix}_mem_read_data", "input", "8", unpacked="[0:3]"),
                _port(f"{prefix}_mem_write_req", "output", "4"),
                _port(
                    f"{prefix}_mem_write_addr",
                    "output",
                    f"{FIFO_ADDR_WIDTH}",
                    unpacked="[0:3]",
                ),
                _port(f"{prefix}_mem_write_ready", "input", "4"),
                _port(f"{prefix}_mem_write_data", "output", "8", unpacked="[0:3]"),
                _port(f"{prefix}_mem_write_bit_mask", "output", "8", unpacked="[0:3]"),
            ]
        )
    ports.extend(
        [
            _port("frame_mem_write_req", "output", "1"),
            _port("frame_mem_write_addr", "output", str(FRAME_ADDR_WIDTH)),
            _port("frame_mem_write_ready", "input", "1"),
            _port("frame_mem_write_data", "output", "8"),
            _port("frame_mem_write_bit_mask", "output", "8"),
        ]
    )
    return ports


def build_contract(
    candidate: Mapping[str, Any],
    pins: Mapping[str, DependencyPin],
    *,
    rtl_sha256: str | None = None,
) -> dict[str, Any]:
    function = candidate.get("function", {})
    function_record = {
        "clang_usr": candidate.get("clang_usr"),
        "name": candidate.get("name"),
        "parameters": function.get("parameters", []),
        "return_type": function.get("return_type"),
        "source_file": candidate.get("source_file"),
        "source_span": candidate.get("source_span"),
        "source_body_sha256": candidate.get("source_body_sha256"),
    }
    contract: dict[str, Any] = {
        "schema_version": 1,
        "contract_id": "process_group_encode_fsm_v1",
        "status": "PROVISIONAL_SIMULATION_ONLY",
        "promotion": {
            "simulation_may_proceed": True,
            "status": "BLOCKED_PENDING_HUMAN_CONTRACT_REVIEW",
        },
        "origin": "tool_discovered_encode_coverage_structural_fsm",
        "function": function_record,
        "selection": {
            "basis": [
                "Encode-phase positive execution coverage",
                "config/state/frame pointer signature",
                "outer SSP loop and inner mux-byte loop facts",
                "encoder branch and FIFO/bitstream callee roles",
                "source-order memory-effect markers",
            ],
            "execution_count": int(candidate.get("execution_count", 0)),
            "structural_score": int(candidate.get("structural_score", 0)),
            "structural_evidence": candidate.get("structural_evidence", []),
            "callee_names": sorted(pin.function_name for pin in pins.values()),
        },
        "dependencies": {kind: pin.as_dict() for kind, pin in sorted(pins.items())},
        "composition": {
            "dependencies": [
                {
                    "role": kind,
                    "function": pin.function_name,
                    "contract_id": pin.contract_id,
                    "contract_file": pin.contract_path,
                    "contract_sha256": pin.contract_sha256,
                    "module": pin.module,
                    "module_file": pin.module_path,
                    "module_sha256": pin.module_sha256,
                    "composition_mode": "semantics_inlined_into_parent_fsm",
                }
                for kind, pin in sorted(pins.items())
            ]
        },
        "domain": {
            "is_encoder": 1,
            "num_ssps": [MIN_SSPS, MAX_SSPS],
            "mux_word_size": list(MUX_WORD_SIZES),
            "max_ssps": MAX_SSPS,
            "max_se_size_bound": MAX_SE_SIZE_BOUND,
            "fifo_size_bits_positive_multiple_of_8": True,
            "fifo_pointer_is_bit_address": True,
            "se_size_value": [0, MAX_SE_SIZE_BOUND],
            "external_memory_read_handshake": "request-held-until-read-valid",
            "external_memory_write_handshake": "request-held-until-write-ready",
            "frame_write_mask_is_read_modify_write": True,
        },
        "source_order": [
            "for each active SSP in increasing index",
            "capture refill from shifter fullness once per SSP",
            "for each mux byte in increasing index",
            "read encBalanceFifo bits before frame write",
            "write one 8-bit mux byte to frame before shifter FIFO write",
            "write the same mux byte to shifter FIFO",
            "read one 8-bit syntax-element size from seSizeFifo",
            "discard exactly that many bits from shifter FIFO",
        ],
        "state_outputs": {
            "fifo_scalar_fields": [
                "size_bits",
                "fullness",
                "read_ptr",
                "write_ptr",
                "max_fullness",
                "byte_ctr",
            ],
            "post_mux_num_bits": True,
            "inactive_ssp_state_passthrough": True,
        },
        "flags": [
            "illegal_domain",
            "fifo_underflow",
            "fifo_overflow",
            "frame_overflow",
            "se_size_overflow",
        ],
        "interface": {"ports": contract_interface()},
    }
    contract["semantics"] = {
        "kind": "bounded_process_group_encode_transition",
        "constants": {
            "max_ssps": MAX_SSPS,
            "min_ssps": MIN_SSPS,
            "mux_word_sizes": list(MUX_WORD_SIZES),
            "max_se_size": MAX_SE_SIZE_BOUND,
            "fifo_address_width": FIFO_ADDR_WIDTH,
            "frame_address_width": FRAME_ADDR_WIDTH,
        },
        "legal_domain": contract["domain"],
        "bindings": {
            "config_parameter": str(function_record["parameters"][0]["name"]),
            "state_parameter": str(function_record["parameters"][1]["name"]),
            "buffer_parameter": str(function_record["parameters"][2]["name"]),
            "fifo_prefixes": ["enc_balance", "shifter", "se_size"],
            "frame_prefix": "frame",
            "post_mux_num_bits_input": "post_mux_num_bits_in",
            "post_mux_num_bits_output": "post_mux_num_bits_out",
        },
        "state_transition": (
            "bounded source-ordered encoder mux/FIFO/frame FSM with explicit "
            "external memory handshakes"
        ),
    }
    if rtl_sha256 is not None:
        contract["rtl"] = {
            "module": "process_group_encode_fsm",
            "candidate_sha256": rtl_sha256,
        }
    return contract


def _sv_port_declaration(port: Mapping[str, Any]) -> str:
    direction = str(port["direction"])
    width = str(port["width"])
    name = str(port["name"])
    unpacked = str(port.get("unpacked", ""))
    if width == "1":
        packed = "logic"
    else:
        packed = f"logic [{int(width) - 1}:0]"
    return f"    {direction} {packed} {name}{unpacked}"


def render_rtl(
    candidate: Mapping[str, Any],
    pins: Mapping[str, DependencyPin],
    *,
    module_name: str = "process_group_encode_fsm",
) -> str:
    """Render a synthesizable bounded sequential FSM for the encoder path."""

    safe_module = re.sub(r"[^A-Za-z0-9_]", "_", module_name)
    ports = contract_interface()
    declarations = ",\n".join(_sv_port_declaration(port) for port in ports)
    dependency_comment = "\n".join(
        f"// pinned {kind}: contract_sha256={pin.contract_sha256} "
        f"source_body_sha256={pin.source_body_sha256}"
        for kind, pin in sorted(pins.items())
    )
    # A single generate block keeps the emitted port/state mapping readable.
    scalar_assignments_text = "\n".join(
        [
            "  genvar g;",
            "  generate",
            "    for (g = 0; g < MAX_SSPS; g++) begin : gen_scalar_outputs",
        ]
        + [
            f"      assign {prefix}_{field}_out[g] = {prefix}_{field}_r[g];"
            for prefix in ("enc_balance", "shifter", "se_size")
            for field in (
                "size_bits",
                "fullness",
                "read_ptr",
                "write_ptr",
                "max_fullness",
                "byte_ctr",
            )
        ]
        + ["    end", "  endgenerate"]
    )
    template = """// Generated by tools/generate_process_group_encode.py
// Encoder-only bounded FSM; promotion remains human-review gated.
__DEPENDENCY_COMMENT__
module __MODULE__ #(
    parameter integer MAX_SSPS = 4,
    parameter integer FIFO_ADDR_W = __FIFO_ADDR_WIDTH__,
    parameter integer FRAME_ADDR_W = __FRAME_ADDR_WIDTH__,
    parameter integer MAX_SE_SIZE = __MAX_SE_SIZE_BOUND__
) (
__DECLARATIONS__
);

  localparam integer ST_IDLE = 0;
  localparam integer ST_CHECK_SSP = 1;
  localparam integer ST_PREP_ENC_BIT = 2;
  localparam integer ST_ENC_READ = 3;
  localparam integer ST_FRAME_WRITE = 4;
  localparam integer ST_PREP_SHIFTER_WRITE = 5;
  localparam integer ST_SHIFTER_WRITE = 6;
  localparam integer ST_PREP_SE_SIZE = 7;
  localparam integer ST_SE_SIZE_READ = 8;
  localparam integer ST_PREP_SHIFTER_DISCARD = 9;
  localparam integer ST_SHIFTER_DISCARD = 10;
  localparam integer ST_DONE = 11;
  localparam integer ST_ERROR = 12;

  logic [3:0] state_r;
  logic [31:0] enc_balance_size_bits_r [0:3];
  logic [31:0] enc_balance_fullness_r [0:3];
  logic [31:0] enc_balance_read_ptr_r [0:3];
  logic [31:0] enc_balance_write_ptr_r [0:3];
  logic [31:0] enc_balance_max_fullness_r [0:3];
  logic [31:0] enc_balance_byte_ctr_r [0:3];
  logic [31:0] shifter_size_bits_r [0:3];
  logic [31:0] shifter_fullness_r [0:3];
  logic [31:0] shifter_read_ptr_r [0:3];
  logic [31:0] shifter_write_ptr_r [0:3];
  logic [31:0] shifter_max_fullness_r [0:3];
  logic [31:0] shifter_byte_ctr_r [0:3];
  logic [31:0] se_size_size_bits_r [0:3];
  logic [31:0] se_size_fullness_r [0:3];
  logic [31:0] se_size_read_ptr_r [0:3];
  logic [31:0] se_size_write_ptr_r [0:3];
  logic [31:0] se_size_max_fullness_r [0:3];
  logic [31:0] se_size_byte_ctr_r [0:3];
  logic [6:0] max_se_size_r [0:3];
  logic [31:0] frame_capacity_bits_r;
  logic [31:0] post_mux_num_bits_r;
  logic [2:0] ssp_index_r;
  logic [3:0] mux_index_r;
  logic [3:0] enc_bits_total_r;
  logic [3:0] bits_remaining_r;
  logic [7:0] enc_accum_r;
  logic [7:0] mux_byte_r;
  logic [3:0] frame_bit_index_r;
  logic [3:0] shifter_bit_index_r;
  logic [7:0] shifter_bit_data_r;
  logic [3:0] se_bits_remaining_r;
  logic [7:0] se_accum_r;
  logic [7:0] se_size_value_r;
  logic [7:0] discard_remaining_r;
  logic input_legal;
  integer reset_i;

__SCALAR_ASSIGNMENTS__
  assign post_mux_num_bits_out = post_mux_num_bits_r;

  function automatic [31:0] advance_ptr;
    input [31:0] ptr;
    input [31:0] size_bits;
    begin
      if ((size_bits != 0) && ((ptr + 32'd1) >= size_bits))
        advance_ptr = 32'd0;
      else
        advance_ptr = ptr + 32'd1;
    end
  endfunction

  function automatic [7:0] one_hot_bit;
    input [2:0] bit_position;
    begin
      one_hot_bit = (8'h01 << bit_position);
    end
  endfunction

  always_comb begin
    input_legal = 1'b1;
    if (is_encoder !== 1'b1)
      input_legal = 1'b0;
    if ((num_ssps < 3) || (num_ssps > MAX_SSPS))
      input_legal = 1'b0;
    if ((mux_word_size != 7'd48) && (mux_word_size != 7'd64))
      input_legal = 1'b0;
    if (post_mux_num_bits_in > frame_capacity_bits)
      input_legal = 1'b0;
    for (integer k = 0; k < MAX_SSPS; k = k + 1) begin
      if (k < num_ssps) begin
        if ((enc_balance_size_bits_in[k] == 0) ||
            ((enc_balance_size_bits_in[k] % 8) != 0) ||
            (enc_balance_fullness_in[k] > enc_balance_size_bits_in[k]) ||
            (enc_balance_read_ptr_in[k] >= enc_balance_size_bits_in[k]) ||
            (enc_balance_write_ptr_in[k] >= enc_balance_size_bits_in[k]) ||
            (enc_balance_max_fullness_in[k] > enc_balance_size_bits_in[k]))
          input_legal = 1'b0;
        if ((shifter_size_bits_in[k] == 0) ||
            ((shifter_size_bits_in[k] % 8) != 0) ||
            (shifter_fullness_in[k] > shifter_size_bits_in[k]) ||
            (shifter_read_ptr_in[k] >= shifter_size_bits_in[k]) ||
            (shifter_write_ptr_in[k] >= shifter_size_bits_in[k]) ||
            (shifter_max_fullness_in[k] > shifter_size_bits_in[k]))
          input_legal = 1'b0;
        if ((se_size_size_bits_in[k] == 0) ||
            ((se_size_size_bits_in[k] % 8) != 0) ||
            (se_size_fullness_in[k] > se_size_size_bits_in[k]) ||
            (se_size_read_ptr_in[k] >= se_size_size_bits_in[k]) ||
            (se_size_write_ptr_in[k] >= se_size_size_bits_in[k]) ||
            (se_size_max_fullness_in[k] > se_size_size_bits_in[k]))
          input_legal = 1'b0;
        if ((max_se_size[k] == 0) || (max_se_size[k] > MAX_SE_SIZE))
          input_legal = 1'b0;
      end
    end
  end

  always_comb begin
    enc_balance_mem_read_req = 4'b0;
    enc_balance_mem_read_addr = '{default:'0};
    enc_balance_mem_write_req = 4'b0;
    enc_balance_mem_write_addr = '{default:'0};
    enc_balance_mem_write_data = '{default:'0};
    enc_balance_mem_write_bit_mask = '{default:'0};
    shifter_mem_read_req = 4'b0;
    shifter_mem_read_addr = '{default:'0};
    shifter_mem_write_req = 4'b0;
    shifter_mem_write_addr = '{default:'0};
    shifter_mem_write_data = '{default:'0};
    shifter_mem_write_bit_mask = '{default:'0};
    se_size_mem_read_req = 4'b0;
    se_size_mem_read_addr = '{default:'0};
    se_size_mem_write_req = 4'b0;
    se_size_mem_write_addr = '{default:'0};
    se_size_mem_write_data = '{default:'0};
    se_size_mem_write_bit_mask = '{default:'0};
    frame_mem_write_req = 1'b0;
    frame_mem_write_addr = '0;
    frame_mem_write_data = 8'h00;
    frame_mem_write_bit_mask = 8'h00;

    if (busy) begin
      if (state_r == ST_ENC_READ) begin
        enc_balance_mem_read_req[ssp_index_r] = 1'b1;
        enc_balance_mem_read_addr[ssp_index_r] =
            enc_balance_read_ptr_r[ssp_index_r] >> 3;
      end
      else if (state_r == ST_SE_SIZE_READ) begin
        se_size_mem_read_req[ssp_index_r] = 1'b1;
        se_size_mem_read_addr[ssp_index_r] =
            se_size_read_ptr_r[ssp_index_r] >> 3;
      end
      else if (state_r == ST_SHIFTER_DISCARD) begin
        shifter_mem_read_req[ssp_index_r] = 1'b1;
        shifter_mem_read_addr[ssp_index_r] =
            shifter_read_ptr_r[ssp_index_r] >> 3;
      end
      else if (state_r == ST_SHIFTER_WRITE) begin
        shifter_mem_write_req[ssp_index_r] = 1'b1;
        shifter_mem_write_addr[ssp_index_r] =
            shifter_write_ptr_r[ssp_index_r] >> 3;
        shifter_mem_write_bit_mask[ssp_index_r] =
            one_hot_bit(3'd7 - shifter_write_ptr_r[ssp_index_r][2:0]);
        shifter_mem_write_data[ssp_index_r] =
            shifter_bit_data_r[7 - shifter_bit_index_r]
            ? one_hot_bit(3'd7 - shifter_write_ptr_r[ssp_index_r][2:0])
            : 8'h00;
      end
      else if (state_r == ST_FRAME_WRITE) begin
        frame_mem_write_req = 1'b1;
        frame_mem_write_addr = post_mux_num_bits_r >> 3;
        frame_mem_write_bit_mask =
            ((post_mux_num_bits_r[2:0] == 0)
                ? 8'hff
                : one_hot_bit(3'd7 - post_mux_num_bits_r[2:0]));
        frame_mem_write_data =
            mux_byte_r[7 - frame_bit_index_r]
                ? one_hot_bit(3'd7 - post_mux_num_bits_r[2:0])
                : 8'h00;
      end
    end
  end

  always_ff @(posedge clk or negedge rst_n) begin
    if (!rst_n) begin
      state_r <= ST_IDLE;
      busy <= 1'b0;
      done <= 1'b0;
      illegal_domain <= 1'b0;
      fifo_underflow <= 1'b0;
      fifo_overflow <= 1'b0;
      frame_overflow <= 1'b0;
      se_size_overflow <= 1'b0;
      post_mux_num_bits_r <= 32'd0;
      frame_capacity_bits_r <= 32'd0;
      ssp_index_r <= 3'd0;
      mux_index_r <= 4'd0;
      enc_bits_total_r <= 4'd0;
      bits_remaining_r <= 4'd0;
      enc_accum_r <= 8'd0;
      mux_byte_r <= 8'd0;
      frame_bit_index_r <= 4'd0;
      shifter_bit_index_r <= 4'd0;
      shifter_bit_data_r <= 8'd0;
      se_bits_remaining_r <= 4'd0;
      se_accum_r <= 8'd0;
      se_size_value_r <= 8'd0;
      discard_remaining_r <= 8'd0;
      for (reset_i = 0; reset_i < MAX_SSPS; reset_i = reset_i + 1) begin
        enc_balance_size_bits_r[reset_i] <= 32'd0;
        enc_balance_fullness_r[reset_i] <= 32'd0;
        enc_balance_read_ptr_r[reset_i] <= 32'd0;
        enc_balance_write_ptr_r[reset_i] <= 32'd0;
        enc_balance_max_fullness_r[reset_i] <= 32'd0;
        enc_balance_byte_ctr_r[reset_i] <= 32'd0;
        shifter_size_bits_r[reset_i] <= 32'd0;
        shifter_fullness_r[reset_i] <= 32'd0;
        shifter_read_ptr_r[reset_i] <= 32'd0;
        shifter_write_ptr_r[reset_i] <= 32'd0;
        shifter_max_fullness_r[reset_i] <= 32'd0;
        shifter_byte_ctr_r[reset_i] <= 32'd0;
        se_size_size_bits_r[reset_i] <= 32'd0;
        se_size_fullness_r[reset_i] <= 32'd0;
        se_size_read_ptr_r[reset_i] <= 32'd0;
        se_size_write_ptr_r[reset_i] <= 32'd0;
        se_size_max_fullness_r[reset_i] <= 32'd0;
        se_size_byte_ctr_r[reset_i] <= 32'd0;
        max_se_size_r[reset_i] <= 7'd0;
      end
    end
    else begin
      done <= 1'b0;
      case (state_r)
        ST_IDLE: begin
          busy <= 1'b0;
          if (start) begin
            illegal_domain <= 1'b0;
            fifo_underflow <= 1'b0;
            fifo_overflow <= 1'b0;
            frame_overflow <= 1'b0;
            se_size_overflow <= 1'b0;
            post_mux_num_bits_r <= post_mux_num_bits_in;
            frame_capacity_bits_r <= frame_capacity_bits;
            ssp_index_r <= 3'd0;
            mux_index_r <= 4'd0;
            for (reset_i = 0; reset_i < MAX_SSPS; reset_i = reset_i + 1) begin
              enc_balance_size_bits_r[reset_i] <= enc_balance_size_bits_in[reset_i];
              enc_balance_fullness_r[reset_i] <= enc_balance_fullness_in[reset_i];
              enc_balance_read_ptr_r[reset_i] <= enc_balance_read_ptr_in[reset_i];
              enc_balance_write_ptr_r[reset_i] <= enc_balance_write_ptr_in[reset_i];
              enc_balance_max_fullness_r[reset_i] <= enc_balance_max_fullness_in[reset_i];
              enc_balance_byte_ctr_r[reset_i] <= enc_balance_byte_ctr_in[reset_i];
              shifter_size_bits_r[reset_i] <= shifter_size_bits_in[reset_i];
              shifter_fullness_r[reset_i] <= shifter_fullness_in[reset_i];
              shifter_read_ptr_r[reset_i] <= shifter_read_ptr_in[reset_i];
              shifter_write_ptr_r[reset_i] <= shifter_write_ptr_in[reset_i];
              shifter_max_fullness_r[reset_i] <= shifter_max_fullness_in[reset_i];
              shifter_byte_ctr_r[reset_i] <= shifter_byte_ctr_in[reset_i];
              se_size_size_bits_r[reset_i] <= se_size_size_bits_in[reset_i];
              se_size_fullness_r[reset_i] <= se_size_fullness_in[reset_i];
              se_size_read_ptr_r[reset_i] <= se_size_read_ptr_in[reset_i];
              se_size_write_ptr_r[reset_i] <= se_size_write_ptr_in[reset_i];
              se_size_max_fullness_r[reset_i] <= se_size_max_fullness_in[reset_i];
              se_size_byte_ctr_r[reset_i] <= se_size_byte_ctr_in[reset_i];
              max_se_size_r[reset_i] <= max_se_size[reset_i];
            end
            if (!input_legal) begin
              illegal_domain <= 1'b1;
              state_r <= ST_ERROR;
              busy <= 1'b0;
            end
            else begin
              state_r <= ST_CHECK_SSP;
              busy <= 1'b1;
            end
          end
        end

        ST_CHECK_SSP: begin
          if (ssp_index_r >= num_ssps) begin
            state_r <= ST_DONE;
          end
          else if (shifter_fullness_r[ssp_index_r] < max_se_size_r[ssp_index_r]) begin
            mux_index_r <= 4'd0;
            state_r <= ST_PREP_ENC_BIT;
          end
          else begin
            state_r <= ST_PREP_SE_SIZE;
          end
        end

        ST_PREP_ENC_BIT: begin
          if (enc_balance_fullness_r[ssp_index_r] >= 8) begin
            enc_bits_total_r <= 4'd8;
          end
          else begin
            enc_bits_total_r <= enc_balance_fullness_r[ssp_index_r][3:0];
          end
          enc_accum_r <= 8'd0;
          bits_remaining_r <=
              (enc_balance_fullness_r[ssp_index_r] >= 8)
                  ? 4'd8
                  : enc_balance_fullness_r[ssp_index_r][3:0];
          if (enc_balance_fullness_r[ssp_index_r] == 0) begin
            mux_byte_r <= 8'd0;
            frame_bit_index_r <= 4'd0;
            state_r <= ST_FRAME_WRITE;
          end
          else if (enc_balance_fullness_r[ssp_index_r] > enc_balance_size_bits_r[ssp_index_r]) begin
            fifo_underflow <= 1'b1;
            state_r <= ST_ERROR;
          end
          else begin
            state_r <= ST_ENC_READ;
          end
        end

        ST_ENC_READ: begin
          if (enc_balance_mem_read_valid[ssp_index_r]) begin
            enc_accum_r <= {
                enc_accum_r[6:0],
                enc_balance_mem_read_data[ssp_index_r][7 - enc_balance_read_ptr_r[ssp_index_r][2:0]]
            };
            enc_balance_fullness_r[ssp_index_r] <=
                enc_balance_fullness_r[ssp_index_r] - 32'd1;
            enc_balance_read_ptr_r[ssp_index_r] <= advance_ptr(
                enc_balance_read_ptr_r[ssp_index_r],
                enc_balance_size_bits_r[ssp_index_r]
            );
            if (bits_remaining_r == 1) begin
              if (enc_bits_total_r == 8)
                mux_byte_r <= {
                    enc_accum_r[6:0],
                    enc_balance_mem_read_data[ssp_index_r][7 - enc_balance_read_ptr_r[ssp_index_r][2:0]]
                };
              else
                mux_byte_r <= (
                    {
                        enc_accum_r[6:0],
                        enc_balance_mem_read_data[ssp_index_r][7 - enc_balance_read_ptr_r[ssp_index_r][2:0]]
                    } << (8 - enc_bits_total_r)
                );
              frame_bit_index_r <= 4'd0;
              state_r <= ST_FRAME_WRITE;
            end
            else begin
              bits_remaining_r <= bits_remaining_r - 4'd1;
            end
          end
        end

        ST_FRAME_WRITE: begin
          if ((post_mux_num_bits_r + 32'd8) > frame_capacity_bits_r) begin
            frame_overflow <= 1'b1;
            state_r <= ST_ERROR;
          end
          else if (frame_mem_write_ready) begin
            post_mux_num_bits_r <= post_mux_num_bits_r + 32'd1;
            if (frame_bit_index_r == 7) begin
              shifter_bit_data_r <= mux_byte_r;
              shifter_bit_index_r <= 4'd0;
              state_r <= ST_PREP_SHIFTER_WRITE;
            end
            else begin
              frame_bit_index_r <= frame_bit_index_r + 4'd1;
            end
          end
        end

        ST_PREP_SHIFTER_WRITE: begin
          if ((shifter_fullness_r[ssp_index_r] + 32'd8) >
              shifter_size_bits_r[ssp_index_r]) begin
            fifo_overflow <= 1'b1;
            state_r <= ST_ERROR;
          end
          else begin
            shifter_fullness_r[ssp_index_r] <=
                shifter_fullness_r[ssp_index_r] + 32'd8;
            if ((shifter_fullness_r[ssp_index_r] + 32'd8) >
                shifter_max_fullness_r[ssp_index_r])
              shifter_max_fullness_r[ssp_index_r] <=
                  shifter_fullness_r[ssp_index_r] + 32'd8;
            state_r <= ST_SHIFTER_WRITE;
          end
        end

        ST_SHIFTER_WRITE: begin
          if (shifter_mem_write_ready[ssp_index_r]) begin
            shifter_write_ptr_r[ssp_index_r] <= advance_ptr(
                shifter_write_ptr_r[ssp_index_r],
                shifter_size_bits_r[ssp_index_r]
            );
            if (shifter_bit_index_r == 7) begin
              if (mux_index_r + 4'd1 < (mux_word_size / 8)) begin
                mux_index_r <= mux_index_r + 4'd1;
                state_r <= ST_PREP_ENC_BIT;
              end
              else begin
                state_r <= ST_PREP_SE_SIZE;
              end
            end
            else begin
              shifter_bit_index_r <= shifter_bit_index_r + 4'd1;
            end
          end
        end

        ST_PREP_SE_SIZE: begin
          if (se_size_fullness_r[ssp_index_r] < 8) begin
            fifo_underflow <= 1'b1;
            state_r <= ST_ERROR;
          end
          else begin
            se_bits_remaining_r <= 4'd8;
            se_accum_r <= 8'd0;
            state_r <= ST_SE_SIZE_READ;
          end
        end

        ST_SE_SIZE_READ: begin
          if (se_size_mem_read_valid[ssp_index_r]) begin
            se_accum_r <= {
                se_accum_r[6:0],
                se_size_mem_read_data[ssp_index_r][7 - se_size_read_ptr_r[ssp_index_r][2:0]]
            };
            se_size_fullness_r[ssp_index_r] <=
                se_size_fullness_r[ssp_index_r] - 32'd1;
            se_size_read_ptr_r[ssp_index_r] <= advance_ptr(
                se_size_read_ptr_r[ssp_index_r],
                se_size_size_bits_r[ssp_index_r]
            );
            if (se_bits_remaining_r == 1) begin
              se_size_value_r <= {
                  se_accum_r[6:0],
                  se_size_mem_read_data[ssp_index_r][7 - se_size_read_ptr_r[ssp_index_r][2:0]]
              };
              state_r <= ST_PREP_SHIFTER_DISCARD;
            end
            else begin
              se_bits_remaining_r <= se_bits_remaining_r - 4'd1;
            end
          end
        end

        ST_PREP_SHIFTER_DISCARD: begin
          if (se_size_value_r > MAX_SE_SIZE) begin
            se_size_overflow <= 1'b1;
            illegal_domain <= 1'b1;
            state_r <= ST_ERROR;
          end
          else if (shifter_fullness_r[ssp_index_r] < se_size_value_r) begin
            fifo_underflow <= 1'b1;
            state_r <= ST_ERROR;
          end
          else begin
            discard_remaining_r <= se_size_value_r;
            if (se_size_value_r == 0) begin
              if (ssp_index_r + 3'd1 < num_ssps)
                ssp_index_r <= ssp_index_r + 3'd1;
              else
                ssp_index_r <= num_ssps;
              state_r <= ST_CHECK_SSP;
            end
            else begin
              state_r <= ST_SHIFTER_DISCARD;
            end
          end
        end

        ST_SHIFTER_DISCARD: begin
          if (shifter_mem_read_valid[ssp_index_r]) begin
            shifter_fullness_r[ssp_index_r] <=
                shifter_fullness_r[ssp_index_r] - 32'd1;
            shifter_read_ptr_r[ssp_index_r] <= advance_ptr(
                shifter_read_ptr_r[ssp_index_r],
                shifter_size_bits_r[ssp_index_r]
            );
            if (discard_remaining_r == 1) begin
              if (ssp_index_r + 3'd1 < num_ssps)
                ssp_index_r <= ssp_index_r + 3'd1;
              else
                ssp_index_r <= num_ssps;
              state_r <= ST_CHECK_SSP;
            end
            else begin
              discard_remaining_r <= discard_remaining_r - 8'd1;
            end
          end
        end

        ST_DONE: begin
          busy <= 1'b0;
          done <= 1'b1;
          state_r <= ST_IDLE;
        end

        ST_ERROR: begin
          busy <= 1'b0;
          done <= 1'b1;
          state_r <= ST_IDLE;
        end

        default: begin
          illegal_domain <= 1'b1;
          busy <= 1'b0;
          state_r <= ST_ERROR;
        end
      endcase
    end
  end

endmodule
"""
    return (
        template.replace("__DEPENDENCY_COMMENT__", dependency_comment)
        .replace("__MODULE__", safe_module)
        .replace("__FIFO_ADDR_WIDTH__", str(FIFO_ADDR_WIDTH))
        .replace("__FRAME_ADDR_WIDTH__", str(FRAME_ADDR_WIDTH))
        .replace("__MAX_SE_SIZE_BOUND__", str(MAX_SE_SIZE_BOUND))
        .replace("__DECLARATIONS__", declarations)
        .replace("__SCALAR_ASSIGNMENTS__", scalar_assignments_text)
    )


def generate_artifact(
    root: pathlib.Path,
    output_dir: pathlib.Path,
    *,
    source_dir: pathlib.Path | None = None,
    functions_path: pathlib.Path | None = None,
    coverage_path: pathlib.Path | None = None,
    frontier_path: pathlib.Path | None = None,
    contract_paths: Sequence[pathlib.Path] | None = None,
) -> dict[str, Any]:
    """Discover, pin, render, and write only the requested candidate artifact."""

    source_dir = source_dir or _default_source_dir(root)
    functions_document = _read_json(functions_path or root / "facts" / "functions.json")
    coverage_document = _read_json(coverage_path or root / "coverage" / "coverage.json")
    frontier_document = None
    selected_frontier = frontier_path or root / "coverage" / "encode" / "frontier.json"
    if selected_frontier.is_file():
        frontier_document = _read_json(selected_frontier)
    candidate = discover_process_group_candidate(
        functions_document,
        coverage_document,
        source_dir,
        encode_frontier_document=frontier_document,
    )
    pins = discover_dependency_pins(
        root,
        source_dir,
        contract_paths=contract_paths,
    )
    rtl = render_rtl(candidate, pins)
    contract = build_contract(candidate, pins, rtl_sha256=_sha256_text(rtl))
    output_dir.mkdir(parents=True, exist_ok=True)
    (output_dir / "candidate_01.sv").write_text(rtl, encoding="utf-8")
    _write_json(output_dir / "provisional-contract.json", contract)
    return {"candidate": candidate, "pins": pins, "contract": contract, "rtl": rtl}


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=pathlib.Path, default=pathlib.Path("."))
    parser.add_argument("--source-dir", type=pathlib.Path)
    parser.add_argument("--functions", type=pathlib.Path)
    parser.add_argument("--coverage", type=pathlib.Path)
    parser.add_argument("--encode-frontier", type=pathlib.Path)
    parser.add_argument("--output", type=pathlib.Path, required=True)
    parser.add_argument(
        "--dependency-contract",
        type=pathlib.Path,
        action="append",
        dest="dependency_contracts",
        help="explicit dependency contract path; repeat exactly three times",
    )
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    args = _build_parser().parse_args(argv)
    try:
        artifact = generate_artifact(
            args.root,
            args.output,
            source_dir=args.source_dir,
            functions_path=args.functions,
            coverage_path=args.coverage,
            frontier_path=args.encode_frontier,
            contract_paths=args.dependency_contracts,
        )
    except (DiscoveryError, OSError, json.JSONDecodeError) as exc:
        print(f"DISCOVERY_INCOMPLETE: {exc}")
        return 2
    print(
        json.dumps(
            {
                "status": "GENERATED",
                "target": artifact["candidate"]["name"],
                "execution_count": artifact["candidate"]["execution_count"],
                "output": str(args.output),
                "dependencies": sorted(artifact["pins"]),
            },
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
