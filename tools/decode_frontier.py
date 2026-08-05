#!/usr/bin/env python3
"""Discover the runtime decoder-to-RTL frontier from generated tool facts.

The selector is deliberately data-driven: no DSC function name is configured.
It joins decoder-only LLVM coverage, Clang function/effect facts, candidate
classification, and the accepted RTL manifest.  The result distinguishes
already replaced leaves from state-transition/composite boundaries and emits
the next provisional bit-reader transition candidate when that shape exists.
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


def file_hash(path: pathlib.Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def c_orchestration_boundary(
    function: dict[str, Any], candidate: dict[str, Any]
) -> str | None:
    """Classify executed C shells that are not meaningful RTL DUTs.

    This is intentionally effect/signature driven.  Function names and source
    filenames are not part of the decision.
    """
    direct = candidate.get("direct_effects", {}) or {}
    callees = function.get("callees", []) or []
    if direct.get("io"):
        return "FRAME_IO_ORCHESTRATION"
    if direct.get("allocation"):
        return "MEMORY_LIFECYCLE"
    direct_effect_free = not any(
        direct.get(key)
        for key in ("allocation", "assertion", "indirect_call", "io", "logging", "state_write")
    )
    if (
        direct_effect_free
        and len(callees) == 1
        and int(function.get("loop_count", 0) or 0) == 0
        and not function.get("fields_write")
        and not function.get("globals_write")
    ):
        return "THIN_CALL_WRAPPER"
    return None


def transition_shape(function: dict[str, Any], candidate: dict[str, Any]) -> bool:
    pointers = function.get("pointer_parameters", []) or []
    write_pointers = [
        item for item in pointers
        if item.get("mode") == "WRITES_THROUGH" and "int *" in str(item.get("type"))
    ]
    byte_buffers = [
        item for item in pointers
        if item.get("mode") == "READ_ONLY"
        and "unsigned char *" in str(item.get("type"))
    ]
    effects = candidate.get("direct_effects", {}) or {}
    forbidden_effect = any(
        effects.get(key)
        for key in ("allocation", "assertion", "indirect_call", "io", "logging")
    )
    return bool(
        function.get("return_type") == "int"
        and len(write_pointers) == 1
        and len(byte_buffers) == 1
        and not function.get("callees")
        and int(function.get("loop_count", 0) or 0) == 1
        and not forbidden_effect
    )


def fifo_read_transition_shape(
    function: dict[str, Any], candidate: dict[str, Any]
) -> bool:
    pointers = function.get("pointer_parameters", []) or []
    fifo_pointers = [
        item for item in pointers
        if item.get("mode") == "WRITES_THROUGH"
        and "fifo_t *" in str(item.get("type"))
    ]
    scalar_parameters = [
        item for item in function.get("parameters", []) if not item.get("pointer")
    ]
    return bool(
        function.get("return_type") == "int"
        and len(fifo_pointers) == 1
        and len(scalar_parameters) == 2
        and int(function.get("loop_count", 0) or 0) == 1
        and not function.get("fields_write") == []
        and not (candidate.get("direct_effects", {}) or {}).get("allocation")
    )


def fifo_read_accounting_shape(
    function: dict[str, Any], provisional_verified: dict[str, dict[str, Any]]
) -> bool:
    callee_names = [str(item.get("name")) for item in function.get("callees", [])]
    fifo_callees = [
        name for name in callee_names
        if (provisional_verified.get(name, {}) or {}).get("semantics_kind")
        == "fifo_read_transition"
    ]
    state_pointers = [
        item for item in function.get("pointer_parameters", [])
        if "dsc_state_t *" in str(item.get("type"))
    ]
    scalar_parameters = [
        item for item in function.get("parameters", []) if not item.get("pointer")
    ]
    state_writes = [
        item for item in function.get("fields_write", [])
        if item.get("record") == "dsc_state_t" and item.get("type") == "int"
    ]
    fifo_arrays = [
        item for item in function.get("fields_read", [])
        if item.get("record") == "dsc_state_t"
        and str(item.get("type", "")).startswith("fifo_t[")
    ]
    effects = function.get("effects", {}) or {}
    return bool(
        function.get("return_type") == "int"
        and len(fifo_callees) == 1
        and len(callee_names) == 1
        and len(state_pointers) == 1
        and len(scalar_parameters) == 3
        and int(function.get("loop_count", 0) or 0) == 0
        and len(state_writes) == 1
        and len(fifo_arrays) == 1
        and not any(
            effects.get(key)
            for key in ("assert", "file_io", "indirect_call", "logging", "malloc")
        )
    )


def fifo_write_transition_shape(
    function: dict[str, Any], candidate: dict[str, Any]
) -> bool:
    pointers = function.get("pointer_parameters", []) or []
    fifo_pointers = [
        item for item in pointers
        if item.get("mode") == "WRITES_THROUGH"
        and "fifo_t *" in str(item.get("type"))
    ]
    scalar_parameters = [
        item for item in function.get("parameters", []) if not item.get("pointer")
    ]
    field_writes = function.get("fields_write", []) or []
    pointer_data_writes = [
        item for item in field_writes
        if item.get("record") == "fifo_s"
        and "unsigned char *" in str(item.get("type"))
    ]
    scalar_state_writes = [
        item for item in field_writes
        if item.get("record") == "fifo_s" and item.get("type") == "int"
    ]
    return bool(
        function.get("return_type") == "void"
        and len(fifo_pointers) == 1
        and len(scalar_parameters) == 2
        and str(scalar_parameters[0].get("type")) == "unsigned int"
        and str(scalar_parameters[1].get("type")) == "int"
        and int(function.get("loop_count", 0) or 0) == 1
        and len(pointer_data_writes) >= 1
        and len({str(item.get("name")) for item in scalar_state_writes}) == 3
        and not (candidate.get("direct_effects", {}) or {}).get("allocation")
    )


def scalar_record_next_state_shape(
    function: dict[str, Any], candidate: dict[str, Any]
) -> bool:
    pointers = function.get("pointer_parameters", []) or []
    config_pointers = [
        item for item in pointers
        if item.get("mode") == "READ_ONLY"
        and "dsc_cfg_t *" in str(item.get("type"))
    ]
    state_pointers = [
        item for item in pointers
        if item.get("mode") == "WRITES_THROUGH"
        and "dsc_state_t *" in str(item.get("type"))
    ]
    scalar_outputs = [
        item for item in pointers
        if item.get("mode") == "WRITES_THROUGH"
        and str(item.get("type", "")).strip() == "int *"
    ]
    scalar_inputs = [
        item for item in function.get("parameters", []) if not item.get("pointer")
    ]
    field_reads = function.get("fields_read", []) or []
    field_writes = function.get("fields_write", []) or []
    effects = function.get("effects", {}) or {}
    return bool(
        function.get("return_type") == "void"
        and len(config_pointers) == 1
        and len(state_pointers) == 1
        and len(scalar_outputs) == 2
        and len(scalar_inputs) == 2
        and all(str(item.get("type")) == "int" for item in scalar_inputs)
        and int(function.get("loop_count", 0) or 0) == 0
        and not function.get("callees")
        and len({str(item.get("name")) for item in field_writes}) >= 5
        and all(
            item.get("record") == "dsc_state_t" and item.get("type") == "int"
            for item in field_writes
        )
        and all(
            item.get("record") in {"dsc_cfg_t", "dsc_state_t"}
            and item.get("type") == "int"
            for item in field_reads
        )
        and not any(
            effects.get(key)
            for key in ("assert", "file_io", "indirect_call", "logging", "malloc")
        )
        and not (candidate.get("direct_effects", {}) or {}).get("allocation")
    )


def sampled_lookup_transition_shape(
    function: dict[str, Any], candidate: dict[str, Any]
) -> bool:
    pointers = function.get("pointer_parameters", []) or []
    read_records = [
        item for item in pointers
        if item.get("mode") == "READ_ONLY"
        and any(
            record in str(item.get("type"))
            for record in ("dsc_cfg_t *", "dsc_state_t *")
        )
    ]
    word_outputs = [
        item for item in pointers
        if item.get("mode") == "WRITES_THROUGH"
        and "unsigned int *" in str(item.get("type"))
    ]
    scalar_inputs = [
        item for item in function.get("parameters", []) if not item.get("pointer")
    ]
    field_reads = function.get("fields_read", []) or []
    effects = function.get("effects", {}) or {}
    callees = [str(item.get("name")) for item in function.get("callees", [])]
    return bool(
        function.get("return_type") == "void"
        and len(read_records) == 2
        and len(word_outputs) == 1
        and len(scalar_inputs) == 4
        and all(str(item.get("type")) == "int" for item in scalar_inputs)
        and int(function.get("loop_count", 0) or 0) == 1
        and not function.get("fields_write")
        and not function.get("globals_write")
        and all(name.startswith("__builtin_") for name in callees)
        and sum(
            item.get("record") == "dsc_cfg_t" and item.get("type") == "int"
            for item in field_reads
        ) >= 2
        and any(
            item.get("record") == "dsc_state_t"
            and str(item.get("type", "")).startswith("int *[")
            for item in field_reads
        )
        and any(
            item.get("record") == "dsc_history_t"
            and "unsigned int *[" in str(item.get("type", ""))
            for item in field_reads
        )
        and not any(
            effects.get(key)
            for key in ("assert", "file_io", "indirect_call", "logging", "malloc")
        )
        and not (candidate.get("direct_effects", {}) or {}).get("allocation")
    )


def scalar_record_memory_transition_shape(
    function: dict[str, Any], candidate: dict[str, Any]
) -> bool:
    pointers = function.get("pointer_parameters", []) or []
    config_pointers = [
        item for item in pointers
        if item.get("mode") == "READ_ONLY"
        and "dsc_cfg_t *" in str(item.get("type"))
    ]
    state_pointers = [
        item for item in pointers
        if item.get("mode") == "WRITES_THROUGH"
        and "dsc_state_t *" in str(item.get("type"))
    ]
    field_reads = function.get("fields_read", []) or []
    field_writes = function.get("fields_write", []) or []
    scalar_writes = [
        item for item in field_writes
        if item.get("record") == "dsc_state_t" and item.get("type") == "int"
    ]
    memory_writes = [
        item for item in field_writes
        if item.get("record") == "dsc_state_t"
        and str(item.get("type", "")).strip() == "int *"
    ]
    effects = function.get("effects", {}) or {}
    return bool(
        function.get("return_type") == "void"
        and len(function.get("parameters", []) or []) == 2
        and len(config_pointers) == 1
        and len(state_pointers) == 1
        and int(function.get("loop_count", 0) or 0) == 0
        and not function.get("callees")
        and len({str(item.get("name")) for item in scalar_writes}) >= 5
        and len({str(item.get("name")) for item in memory_writes}) == 1
        and all(
            item.get("record") in {"dsc_cfg_t", "dsc_state_t"}
            and item.get("type") == "int"
            for item in field_reads
        )
        and not any(
            effects.get(key)
            for key in ("assert", "file_io", "indirect_call", "logging", "malloc")
        )
        and not (candidate.get("direct_effects", {}) or {}).get("allocation")
    )


def bounded_mux_refill_transition_shape(
    function: dict[str, Any],
    provisional_verified: dict[str, dict[str, Any]],
) -> bool:
    """Match a bounded multi-lane byte refill composed from verified leaves."""
    parameters = function.get("parameters", []) or []
    pointers = function.get("pointer_parameters", []) or []
    config_pointers = [
        item for item in pointers if "dsc_cfg_t *" in str(item.get("type"))
    ]
    state_pointers = [
        item for item in pointers if "dsc_state_t *" in str(item.get("type"))
    ]
    byte_buffers = [
        item for item in pointers
        if "unsigned char *" in str(item.get("type"))
        and "**" not in str(item.get("type"))
    ]
    callee_kinds = sorted(
        str(
            (provisional_verified.get(str(item.get("name")), {}) or {}).get(
                "semantics_kind"
            )
            or ""
        )
        for item in function.get("callees", [])
    )
    field_reads = function.get("fields_read", []) or []
    config_fields = {
        (str(item.get("name")), str(item.get("type")))
        for item in field_reads if item.get("record") == "dsc_cfg_t"
    }
    state_fields = {
        (str(item.get("name")), str(item.get("type")))
        for item in field_reads if item.get("record") == "dsc_state_t"
    }
    fifo_fields = {
        (str(item.get("name")), str(item.get("type")))
        for item in field_reads if item.get("record") == "fifo_s"
    }
    effects = function.get("effects", {}) or {}
    return bool(
        function.get("return_type") == "void"
        and len(parameters) == 3
        and len(config_pointers) == 1
        and len(state_pointers) == 1
        and len(byte_buffers) == 1
        and not [item for item in parameters if not item.get("pointer")]
        and int(function.get("loop_count", 0) or 0) == 2
        and not function.get("fields_write")
        and callee_kinds == ["bitstream_read_transition", "fifo_write_transition"]
        and config_fields == {("mux_word_size", "int")}
        and state_fields == {
            ("maxSeSize", "int[4]"),
            ("numSsps", "int"),
            ("postMuxNumBits", "int"),
            ("shifter", "fifo_t[4]"),
        }
        and fifo_fields == {("fullness", "int")}
        and not any(
            effects.get(key)
            for key in ("assert", "file_io", "indirect_call", "logging", "malloc")
        )
    )


def bounded_flatness_state_transition_shape(
    function: dict[str, Any], candidate: dict[str, Any]
) -> bool:
    """Match fixed four-stage flatness control around accepted pure callees."""
    parameters = function.get("parameters", []) or []
    pointers = function.get("pointer_parameters", []) or []
    scalar_parameters = [item for item in parameters if not item.get("pointer")]
    config_pointers = [
        item for item in pointers if "dsc_cfg_t *" in str(item.get("type"))
    ]
    state_pointers = [
        item for item in pointers
        if item.get("mode") == "WRITES_THROUGH"
        and "dsc_state_t *" in str(item.get("type"))
    ]
    field_reads = function.get("fields_read", []) or []
    field_writes = function.get("fields_write", []) or []
    config_fields = {
        (str(item.get("name")), str(item.get("type")))
        for item in field_reads if item.get("record") == "dsc_cfg_t"
    }
    state_fields = {
        (str(item.get("name")), str(item.get("type")))
        for item in field_reads if item.get("record") == "dsc_state_t"
    }
    state_outputs = {
        str(item.get("name")) for item in field_writes
        if item.get("record") == "dsc_state_t" and item.get("type") == "int"
    }
    range_fields = {
        (str(item.get("name")), str(item.get("type")))
        for item in field_reads if item.get("record") == "dsc_range_cfg_t"
    }
    loops = function.get("loops", []) or []
    effects = function.get("effects", {}) or {}
    return bool(
        function.get("return_type") == "void"
        and len(parameters) == 5
        and len(config_pointers) == 1
        and len(state_pointers) == 1
        and len(scalar_parameters) == 3
        and all(str(item.get("type")) == "int" for item in scalar_parameters)
        and len(function.get("callees", []) or []) == 2
        and int(function.get("loop_count", 0) or 0) == 1
        and len(loops) == 1
        and "FIXED_TRIP_COUNT" in str(loops[0].get("proof", ""))
        and config_fields == {
            ("dsc_version_minor", "int"),
            ("rc_range_parameters", "dsc_range_cfg_t[15]"),
            ("somewhat_flat_qp_delta", "int"),
            ("somewhat_flat_qp_thresh", "int"),
            ("very_flat_qp", "int"),
        }
        and state_fields == {
            ("firstFlat", "int"), ("flatnessType", "int"),
            ("groupCount", "int"), ("isEncoder", "int"),
            ("origIsFlat", "int"), ("pixelsInGroup", "int"),
            ("prevFirstFlat", "int"), ("prevFlatnessType", "int"),
            ("prevIsFlat", "int"), ("prevQp", "int"),
            ("primaryQp", "int"), ("sliceWidth", "int"),
            ("stQp", "int"),
        }
        and state_outputs == {
            "firstFlat", "flatnessType", "origIsFlat", "prevFirstFlat",
            "prevFlatnessType", "prevIsFlat", "prevQp", "stQp",
        }
        and range_fields == {("range_max_qp", "int")}
        and not any(
            effects.get(key)
            for key in ("assert", "file_io", "indirect_call", "logging", "malloc")
        )
        and not (candidate.get("direct_effects", {}) or {}).get("allocation")
    )


def bounded_line_write_transition_shape(
    function: dict[str, Any], candidate: dict[str, Any]
) -> bool:
    """Match a fixed-extent state-to-line-buffer scatter transition."""
    parameters = function.get("parameters", []) or []
    pointers = function.get("pointer_parameters", []) or []
    config_pointers = [
        item for item in pointers if "dsc_cfg_t *" in str(item.get("type"))
    ]
    state_pointers = [
        item for item in pointers if "dsc_state_t *" in str(item.get("type"))
    ]
    line_outputs = [
        item for item in pointers
        if item.get("mode") == "WRITES_THROUGH"
        and "int **" in str(item.get("type"))
    ]
    state_fields = {
        (str(item.get("name")), str(item.get("type")))
        for item in function.get("fields_read", [])
        if item.get("record") == "dsc_state_t"
    }
    effects = function.get("effects", {}) or {}
    callees = {str(item.get("name")) for item in function.get("callees", [])}
    return bool(
        function.get("return_type") == "void"
        and len(parameters) == 3
        and len(config_pointers) == 1
        and len(state_pointers) == 1
        and len(line_outputs) == 1
        and not [item for item in parameters if not item.get("pointer")]
        and int(function.get("loop_count", 0) or 0) == 2
        and not function.get("fields_write")
        and not function.get("globals_write")
        and callees == {"printf"}
        and state_fields == {
            ("hPos", "int"), ("ichIndicesInGroup", "int"),
            ("ichLookup", "int[6]"), ("ichPixels", "unsigned int[6][4]"),
            ("ichSelected", "int"), ("numComponents", "int"),
            ("pixelsInGroup", "int"),
        }
        and not any(
            effects.get(key)
            for key in ("assert", "file_io", "indirect_call", "malloc")
        )
        and bool(effects.get("logging"))
        and not (candidate.get("direct_effects", {}) or {}).get("allocation")
    )


def bounded_history_update_transition_shape(
    function: dict[str, Any],
    candidate: dict[str, Any],
    provisional_verified: dict[str, dict[str, Any]],
) -> bool:
    """Match a bounded MRU history shift around a verified lookup leaf."""
    parameters = function.get("parameters", []) or []
    pointers = function.get("pointer_parameters", []) or []
    config_pointers = [
        item for item in pointers if "dsc_cfg_t *" in str(item.get("type"))
    ]
    state_pointers = [
        item for item in pointers
        if item.get("mode") == "WRITES_THROUGH"
        and "dsc_state_t *" in str(item.get("type"))
    ]
    word_inputs = [
        item for item in pointers
        if item.get("mode") == "READ_ONLY"
        and "unsigned int *" in str(item.get("type"))
    ]
    callee_kinds = [
        str(
            (provisional_verified.get(str(item.get("name")), {}) or {}).get(
                "semantics_kind"
            )
            or ""
        )
        for item in function.get("callees", [])
    ]
    field_reads = function.get("fields_read", []) or []
    field_writes = function.get("fields_write", []) or []
    config_fields = {
        (str(item.get("name")), str(item.get("type")))
        for item in field_reads if item.get("record") == "dsc_cfg_t"
    }
    state_fields = {
        (str(item.get("name")), str(item.get("type")))
        for item in field_reads if item.get("record") == "dsc_state_t"
    }
    history_read_fields = {
        (str(item.get("name")), str(item.get("type")))
        for item in field_reads if item.get("record") == "dsc_history_t"
    }
    state_write_fields = {
        (str(item.get("name")), str(item.get("type")))
        for item in field_writes if item.get("record") == "dsc_state_t"
    }
    history_write_fields = {
        (str(item.get("name")), str(item.get("type")))
        for item in field_writes if item.get("record") == "dsc_history_t"
    }
    effects = function.get("effects", {}) or {}
    return bool(
        function.get("return_type") == "void"
        and len(parameters) == 3
        and len(config_pointers) == 1
        and len(state_pointers) == 1
        and len(word_inputs) == 1
        and not [item for item in parameters if not item.get("pointer")]
        and int(function.get("loop_count", 0) or 0) == 4
        and callee_kinds == ["sampled_lookup_transition"]
        and config_fields == {("native_420", "int")}
        and state_fields == {
            ("hPos", "int"), ("history", "dsc_history_t"),
            ("ichSelected", "int"), ("isEncoder", "int"),
            ("numComponents", "int"), ("prevIchSelected", "int"),
            ("vPos", "int"),
        }
        and history_read_fields == {
            ("pixels", "unsigned int *[4]"), ("valid", "int *")
        }
        and state_write_fields == {("history", "dsc_history_t")}
        and history_write_fields == {
            ("pixels", "unsigned int *[4]"), ("valid", "int *")
        }
        and not function.get("globals_write")
        and not any(
            effects.get(key)
            for key in ("assert", "file_io", "indirect_call", "logging", "malloc")
        )
        and not (candidate.get("direct_effects", {}) or {}).get("allocation")
    )


def bounded_history_caller_transition_shape(
    function: dict[str, Any],
    candidate: dict[str, Any],
    provisional_verified: dict[str, dict[str, Any]],
) -> bool:
    """Match a bounded line-sample/history-clear caller around verified ICH RTL."""
    parameters = function.get("parameters", []) or []
    pointers = function.get("pointer_parameters", []) or []
    scalar_parameters = [item for item in parameters if not item.get("pointer")]
    config_pointers = [
        item for item in pointers if "dsc_cfg_t *" in str(item.get("type"))
    ]
    state_pointers = [
        item for item in pointers if "dsc_state_t *" in str(item.get("type"))
    ]
    line_inputs = [
        item for item in pointers
        if item.get("mode") == "READ_ONLY" and "int **" in str(item.get("type"))
    ]
    callee_kinds = [
        str(
            (provisional_verified.get(str(item.get("name")), {}) or {}).get(
                "semantics_kind"
            )
            or ""
        )
        for item in function.get("callees", [])
    ]
    field_reads = function.get("fields_read", []) or []
    field_writes = function.get("fields_write", []) or []
    config_fields = {
        (str(item.get("name")), str(item.get("type")))
        for item in field_reads if item.get("record") == "dsc_cfg_t"
    }
    state_fields = {
        (str(item.get("name")), str(item.get("type")))
        for item in field_reads if item.get("record") == "dsc_state_t"
    }
    state_write_fields = {
        (str(item.get("name")), str(item.get("type")))
        for item in field_writes if item.get("record") == "dsc_state_t"
    }
    history_write_fields = {
        (str(item.get("name")), str(item.get("type")))
        for item in field_writes if item.get("record") == "dsc_history_t"
    }
    loops = function.get("loops", []) or []
    effects = function.get("effects", {}) or {}
    return bool(
        function.get("return_type") == "void"
        and len(parameters) == 5
        and len(config_pointers) == 1
        and len(state_pointers) == 1
        and len(line_inputs) == 1
        and len(scalar_parameters) == 2
        and all(str(item.get("type")) == "int" for item in scalar_parameters)
        and int(function.get("loop_count", 0) or 0) == 3
        and len(loops) == 3
        and sum(int(loop.get("fixed_trip_count", 0) or 0) == 32 for loop in loops) == 2
        and callee_kinds == ["bounded_history_update_transition"]
        and config_fields == {("pic_width", "int"), ("slice_width", "int")}
        and state_fields == {
            ("numComponents", "int"), ("pixelsInGroup", "int")
        }
        and state_write_fields == {("history", "dsc_history_t")}
        and history_write_fields == {("valid", "int *")}
        and not function.get("globals_write")
        and not any(
            effects.get(key)
            for key in ("assert", "file_io", "indirect_call", "logging", "malloc")
        )
        and not (candidate.get("direct_effects", {}) or {}).get("allocation")
    )


def bounded_vld_unit_transition_shape(
    function: dict[str, Any],
    candidate: dict[str, Any],
    provisional_verified: dict[str, dict[str, Any]],
) -> bool:
    """Match one bounded decoder syntax unit around verified pure/read leaves."""
    parameters = function.get("parameters", []) or []
    pointers = function.get("pointer_parameters", []) or []
    scalar_parameters = [item for item in parameters if not item.get("pointer")]
    config_pointers = [
        item for item in pointers if "dsc_cfg_t *" in str(item.get("type"))
    ]
    state_pointers = [
        item for item in pointers
        if item.get("mode") == "WRITES_THROUGH"
        and "dsc_state_t *" in str(item.get("type"))
    ]
    residual_pointers = [
        item for item in pointers if str(item.get("type", "")).strip() == "int *"
    ]
    byte_pointer_pointers = [
        item for item in pointers if "unsigned char **" in str(item.get("type"))
    ]
    callee_names = [str(item.get("name")) for item in function.get("callees", [])]
    provisional_callee_kinds = [
        str(
            (provisional_verified.get(name, {}) or {}).get("semantics_kind") or ""
        )
        for name in callee_names
        if name in provisional_verified
    ]
    field_reads = function.get("fields_read", []) or []
    field_writes = function.get("fields_write", []) or []
    config_fields = {
        (str(item.get("name")), str(item.get("type")))
        for item in field_reads if item.get("record") == "dsc_cfg_t"
    }
    state_fields = {
        (str(item.get("name")), str(item.get("type")))
        for item in field_reads if item.get("record") == "dsc_state_t"
    }
    state_write_fields = {
        (str(item.get("name")), str(item.get("type")))
        for item in field_writes if item.get("record") == "dsc_state_t"
    }
    loops = function.get("loops", []) or []
    globals_read = function.get("globals_read", []) or []
    effects = function.get("effects", {}) or {}
    return bool(
        function.get("return_type") == "void"
        and len(parameters) == 5
        and len(config_pointers) == 1
        and len(state_pointers) == 1
        and len(residual_pointers) == 1
        and len(byte_pointer_pointers) == 1
        and len(scalar_parameters) == 1
        and str(scalar_parameters[0].get("type")) == "int"
        and int(function.get("loop_count", 0) or 0) == 9
        and len(loops) == 9
        and sum(int(loop.get("fixed_trip_count", 0) or 0) == 3 for loop in loops) == 2
        and len(callee_names) == 9
        and provisional_callee_kinds == ["fifo_read_accounting_transition"]
        and config_fields == {
            ("bits_per_component", "int"),
            ("somewhat_flat_qp_thresh", "int"),
        }
        and state_fields == {
            ("cpntBitDepth", "int[4]"), ("firstFlat", "int"),
            ("flatnessType", "int"), ("groupCount", "int"),
            ("ichIndexUnitMap", "int[6]"), ("ichIndicesInGroup", "int"),
            ("ichLookup", "int[6]"), ("ichSelected", "int"),
            ("prevFirstFlat", "int"), ("prevIchSelected", "int"),
            ("primaryQp", "int"), ("unitCType", "int[4]"),
            ("unitSspMap", "int[4]"), ("unitsPerGroup", "int"),
        }
        and state_write_fields == {
            ("firstFlat", "int"), ("flatnessType", "int"),
            ("ichLookup", "int[6]"), ("ichSelected", "int"),
            ("predictedSize", "int[4]"), ("prevFirstFlat", "int"),
            ("prevIchSelected", "int"), ("rcSizeUnit", "int[4]"),
            ("useMidpoint", "int[4]"),
        }
        and not function.get("globals_write")
        and globals_read
        and all(str(item.get("type")) == "FILE *" for item in globals_read)
        and bool(effects.get("file_io"))
        and not any(
            effects.get(key)
            for key in ("assert", "indirect_call", "logging", "malloc")
        )
        and not (candidate.get("direct_effects", {}) or {}).get("allocation")
    )


def bounded_vld_group_transition_shape(
    function: dict[str, Any],
    candidate: dict[str, Any],
    provisional_verified: dict[str, dict[str, Any]],
) -> bool:
    """Match the bounded decoder group around mux refill and syntax units."""
    parameters = function.get("parameters", []) or []
    pointers = function.get("pointer_parameters", []) or []
    config_pointers = [
        item for item in pointers if "dsc_cfg_t *" in str(item.get("type"))
    ]
    state_pointers = [
        item for item in pointers
        if item.get("mode") == "WRITES_THROUGH"
        and "dsc_state_t *" in str(item.get("type"))
    ]
    byte_pointer_pointers = [
        item for item in pointers if "unsigned char **" in str(item.get("type"))
    ]
    callee_names = [str(item.get("name")) for item in function.get("callees", [])]
    provisional_kinds = {
        str((provisional_verified.get(name, {}) or {}).get("semantics_kind") or "")
        for name in callee_names if name in provisional_verified
    }
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
    state_writes = {
        (str(item.get("name")), str(item.get("type")))
        for item in function.get("fields_write", [])
        if item.get("record") == "dsc_state_t"
    }
    effects = function.get("effects", {}) or {}
    return bool(
        function.get("return_type") == "void"
        and len(parameters) == 3
        and len(config_pointers) == 1
        and len(state_pointers) == 1
        and len(byte_pointer_pointers) == 1
        and int(function.get("loop_count", 0) or 0) == 3
        and set(callee_names) == {"ProcessGroupDec", "VLDUnit", "printf"}
        and provisional_kinds == {
            "bounded_mux_refill_transition", "bounded_vld_unit_transition"
        }
        and config_fields == {("rcb_bits", "int")}
        and state_fields == {
            ("bufferFullness", "int"), ("codedGroupSize", "int"),
            ("firstFlat", "int"), ("groupCount", "int"),
            ("numBits", "int"), ("primaryQp", "int"),
            ("quantizedResidual", "int[4][3]"),
            ("unitsPerGroup", "int"),
        }
        and state_writes == {
            ("bufferFullness", "int"), ("codedGroupSize", "int"),
            ("errorOccurred", "int"), ("groupCountLine", "int"),
            ("origIsFlat", "int"), ("prevPrimaryQp", "int"),
        }
        and not function.get("globals_read")
        and not function.get("globals_write")
        and bool(effects.get("logging"))
        and not any(
            effects.get(key)
            for key in ("assert", "file_io", "indirect_call", "malloc")
        )
        and not (candidate.get("direct_effects", {}) or {}).get("allocation")
    )


def raster_color_transform_direction(function: dict[str, Any]) -> str | None:
    """Infer RGB<->YCoCg direction from typed plane reads/writes, not names."""
    read_records = {
        str(item.get("record")) for item in function.get("fields_read", [])
    }
    write_records = {
        str(item.get("record")) for item in function.get("fields_write", [])
    }
    if "rgb_s" in read_records and "yuv_s" in write_records:
        return "rgb_to_ycocg"
    if "yuv_s" in read_records and "rgb_s" in write_records:
        return "ycocg_to_rgb"
    return None


def raster_color_transform_shape(
    function: dict[str, Any], candidate: dict[str, Any]
) -> bool:
    """Match a raster loop whose independent pixel transform is bounded."""
    parameters = function.get("parameters", []) or []
    pointers = function.get("pointer_parameters", []) or []
    pointer_modes = sorted(str(item.get("mode")) for item in pointers)
    callee_names = {str(item.get("name")) for item in function.get("callees", [])}
    config_fields = {
        (str(item.get("name")), str(item.get("type")))
        for item in function.get("fields_read", [])
        if item.get("record") == "dsc_cfg_t"
    }
    picture_fields = {
        str(item.get("name")) for item in function.get("fields_read", [])
        if item.get("record") == "pic_s"
    }
    globals_read = function.get("globals_read", []) or []
    effects = function.get("effects", {}) or {}
    return bool(
        function.get("return_type") == "void"
        and len(parameters) == 3
        and len(pointers) == 3
        and pointer_modes == ["READ_ONLY", "READ_ONLY", "WRITES_THROUGH"]
        and int(function.get("loop_count", 0) or 0) == 2
        and raster_color_transform_direction(function) is not None
        and callee_names == {"exit", "fprintf"}
        and config_fields == {
            ("slice_height", "int"), ("slice_width", "int"),
            ("xstart", "int"), ("ystart", "int"),
        }
        and {"bits", "chroma", "color", "data", "h", "w"} <= picture_fields
        and globals_read
        and all(str(item.get("type")) == "FILE *" for item in globals_read)
        and not function.get("globals_write")
        and bool(effects.get("file_io"))
        and not any(
            effects.get(key) for key in ("assert", "indirect_call", "logging", "malloc")
        )
        and not (candidate.get("direct_effects", {}) or {}).get("allocation")
    )


def bounded_block_pred_search_transition_shape(
    function: dict[str, Any], candidate: dict[str, Any]
) -> bool:
    """Match the fixed DSC block-predictor search and explicit line decision write."""
    parameters = function.get("parameters", []) or []
    pointers = function.get("pointer_parameters", []) or []
    scalar_parameters = [item for item in parameters if not item.get("pointer")]
    config_pointers = [
        item for item in pointers
        if item.get("mode") == "READ_ONLY"
        and "dsc_cfg_t *" in str(item.get("type"))
    ]
    state_pointers = [
        item for item in pointers
        if item.get("mode") == "WRITES_THROUGH"
        and "dsc_state_t *" in str(item.get("type"))
    ]
    line_pointers = [
        item for item in pointers if "int **" in str(item.get("type"))
    ]
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
    loops = function.get("loops", []) or []
    effects = function.get("effects", {}) or {}
    return bool(
        function.get("return_type") == "void"
        and len(parameters) == 5
        and len(config_pointers) == 1
        and len(state_pointers) == 1
        and len(line_pointers) == 1
        and len(scalar_parameters) == 2
        and all(str(item.get("type")) == "int" for item in scalar_parameters)
        and len(function.get("callees", []) or []) == 1
        and int(function.get("loop_count", 0) or 0) == 9
        and len(loops) == 9
        and sum(int(loop.get("fixed_trip_count", 0) or 0) == 13 for loop in loops) == 4
        and sum(int(loop.get("fixed_trip_count", 0) or 0) == 3 for loop in loops) == 2
        and config_fields == {
            ("bits_per_component", "int"),
            ("block_pred_enable", "int"),
            ("native_420", "int"),
        }
        and state_fields == {
            ("bpCount", "int"), ("cpntBitDepth", "int[4]"),
            ("edgeDetected", "int"), ("lastEdgeCount", "int"),
            ("lastErr", "int[4][3][13]"), ("numComponents", "int"),
            ("predErr", "int[4][13]"),
        }
        and state_write_fields == {
            ("bpCount", "int"), ("edgeDetected", "int"),
            ("lastEdgeCount", "int"), ("lastErr", "int[4][3][13]"),
            ("predErr", "int[4][13]"), ("prevLinePred", "PRED_TYPE *"),
        }
        and not function.get("globals_read")
        and not function.get("globals_write")
        and not any(
            effects.get(key)
            for key in ("assert", "file_io", "indirect_call", "logging", "malloc")
        )
        and not (candidate.get("direct_effects", {}) or {}).get("allocation")
    )


def bounded_prediction_decode_transition_shape(
    function: dict[str, Any], candidate: dict[str, Any]
) -> bool:
    """Match the fixed-unit decoder reconstruction loop around accepted leaves."""
    parameters = function.get("parameters", []) or []
    pointers = function.get("pointer_parameters", []) or []
    scalar_parameters = [item for item in parameters if not item.get("pointer")]
    config_pointers = [
        item for item in pointers if "dsc_cfg_t *" in str(item.get("type"))
    ]
    state_pointers = [
        item for item in pointers
        if item.get("mode") == "WRITES_THROUGH"
        and "dsc_state_t *" in str(item.get("type"))
    ]
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
    callees = function.get("callees", []) or []
    internal_callees = [
        item for item in callees
        if str(item.get("name")) not in {
            "__assert_rtn", "__builtin_expect", "abs", "printf"
        }
    ]
    loops = function.get("loops", []) or []
    globals_read = function.get("globals_read", []) or []
    effects = function.get("effects", {}) or {}
    return bool(
        function.get("return_type") == "void"
        and len(parameters) == 6
        and len(config_pointers) == 1
        and len(state_pointers) == 1
        and len(scalar_parameters) == 4
        and all(str(item.get("type")) == "int" for item in scalar_parameters)
        and int(function.get("loop_count", 0) or 0) == 3
        and len(loops) == 3
        and sum(str(loop.get("kind")) == "while" for loop in loops) == 2
        and len(internal_callees) == 6
        and config_fields == {
            ("bits_per_component", "int"),
            ("full_ich_err_precision", "int"),
            ("native_420", "int"),
        }
        and state_fields == {
            ("cpntBitDepth", "int[4]"), ("currLine", "int *[4]"),
            ("isEncoder", "int"), ("maxError", "int[4]"),
            ("maxMidError", "int[4]"), ("midpointRecon", "int[4][6]"),
            ("origLine", "int *[4]"), ("prevLine", "int *[5]"),
            ("prevLinePred", "PRED_TYPE *"),
            ("quantizedResidual", "int[4][3]"),
            ("quantizedResidualMid", "int[4][3]"),
            ("unitCType", "int[4]"), ("unitStartHPos", "int[4]"),
            ("unitsPerGroup", "int"), ("useMidpoint", "int[4]"),
        }
        and state_write_fields == {
            ("currLine", "int *[4]"), ("maxError", "int[4]"),
            ("maxMidError", "int[4]"), ("midpointRecon", "int[4][6]"),
            ("primaryQp", "int"), ("quantizedResidual", "int[4][3]"),
            ("quantizedResidualMid", "int[4][3]"),
        }
        and len(globals_read) == 3
        and {str(item.get("type")) for item in globals_read} == {"int"}
        and not function.get("globals_write")
        and bool(effects.get("assert"))
        and bool(effects.get("logging"))
        and not any(
            effects.get(key) for key in ("file_io", "indirect_call", "malloc")
        )
        and not (candidate.get("direct_effects", {}) or {}).get("allocation")
    )


def bounded_rate_control_decode_transition_shape(
    function: dict[str, Any],
    candidate: dict[str, Any],
    provisional_verified: dict[str, dict[str, Any]],
) -> bool:
    """Match decoder rate control around one verified scalar-memory child."""
    parameters = function.get("parameters", []) or []
    pointers = function.get("pointer_parameters", []) or []
    scalar_parameters = [item for item in parameters if not item.get("pointer")]
    config_pointers = [
        item for item in pointers if "dsc_cfg_t *" in str(item.get("type"))
    ]
    state_pointers = [
        item for item in pointers
        if item.get("mode") == "WRITES_THROUGH"
        and "dsc_state_t *" in str(item.get("type"))
    ]
    callee_names = [str(item.get("name")) for item in function.get("callees", [])]
    provisional_kinds = [
        str((provisional_verified.get(name, {}) or {}).get("semantics_kind") or "")
        for name in callee_names if name in provisional_verified
    ]
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
    state_writes = {
        (str(item.get("name")), str(item.get("type")))
        for item in function.get("fields_write", [])
        if item.get("record") == "dsc_state_t"
    }
    globals_read = function.get("globals_read", []) or []
    effects = function.get("effects", {}) or {}
    return bool(
        function.get("return_type") == "void"
        and len(parameters) == 7
        and len(config_pointers) == 1
        and len(state_pointers) == 1
        and len(scalar_parameters) == 5
        and all(str(item.get("type")) == "int" for item in scalar_parameters)
        and int(function.get("loop_count", 0) or 0) == 3
        and provisional_kinds == ["scalar_record_memory_transition"]
        and config_fields == {
            ("bits_per_component", "int"), ("bits_per_pixel", "int"),
            ("dsc_version_minor", "int"), ("initial_xmit_delay", "int"),
            ("native_420", "int"), ("native_422", "int"),
            ("rc_buf_thresh", "int[14]"), ("rc_edge_factor", "int"),
            ("rc_model_size", "int"), ("rc_quant_incr_limit0", "int"),
            ("rc_quant_incr_limit1", "int"),
            ("rc_range_parameters", "dsc_range_cfg_t[15]"),
            ("rc_tgt_offset_hi", "int"), ("rc_tgt_offset_lo", "int"),
            ("rcb_bits", "int"),
        }
        and range_fields == {
            ("range_bpg_offset", "int"), ("range_max_qp", "int"),
            ("range_min_qp", "int"),
        }
        and state_fields == {
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
        }
        and state_writes == {
            ("bitSaveMode", "int"), ("errorOccurred", "int"),
            ("mppState", "int"), ("pixelCount", "int"),
            ("prevQp", "int"), ("prevRange", "int"),
            ("rcSizeGroup", "int"), ("stQp", "int"),
        }
        and len(globals_read) == 6
        and {str(item.get("type")) for item in globals_read} == {"FILE *"}
        and not function.get("globals_write")
        and bool(effects.get("file_io"))
        and bool(effects.get("logging"))
        and not any(effects.get(key) for key in ("assert", "indirect_call", "malloc"))
        and not (candidate.get("direct_effects", {}) or {}).get("allocation")
    )


def call_arguments(text: str, name: str) -> list[list[str]]:
    results: list[list[str]] = []
    for match in re.finditer(r"\b" + re.escape(name) + r"\s*\(", text):
        start = text.find("(", match.start())
        depth = 0
        end = None
        for index in range(start, len(text)):
            char = text[index]
            if char == "(":
                depth += 1
            elif char == ")":
                depth -= 1
                if depth == 0:
                    end = index
                    break
        if end is None:
            continue
        raw = text[start + 1:end]
        arguments: list[str] = []
        argument_start = 0
        nested = 0
        for index, char in enumerate(raw):
            if char in "([{":
                nested += 1
            elif char in ")]}":
                nested -= 1
            elif char == "," and nested == 0:
                arguments.append(raw[argument_start:index].strip())
                argument_start = index + 1
        arguments.append(raw[argument_start:].strip())
        results.append(arguments)
    return results


def literal_argument_bound(
    function: dict[str, Any], source_dir: pathlib.Path, argument_index: int
) -> dict[str, Any]:
    name = str(function.get("name", ""))
    values: list[int] = []
    visible_calls = 0
    nonliteral_calls = 0
    for source in sorted(source_dir.glob("*.c")):
        text = source.read_text(encoding="utf-8", errors="replace")
        for arguments in call_arguments(text, name):
            if argument_index >= len(arguments):
                continue
            # Exclude the function declaration/definition, whose selected
            # argument is an identifier rather than an integer literal.
            argument = arguments[argument_index]
            if re.fullmatch(r"\d+", argument):
                values.append(int(argument))
                visible_calls += 1
            elif arguments and not re.search(r"\bint\b|\bvoid\b", arguments[0]):
                visible_calls += 1
                nonliteral_calls += 1
    unique = sorted(set(values))
    maximum = max(unique) if unique else None
    return {
        "evidence": "integer literals at directly visible C callsites",
        "argument_index": argument_index,
        "values": unique,
        "maximum": maximum,
        "visible_calls": visible_calls,
        "nonliteral_calls": nonliteral_calls,
        "complete_for_visible_literal_calls": bool(unique) and nonliteral_calls == 0,
    }


def discover(
    coverage: dict[str, Any],
    functions: dict[str, Any],
    candidates: dict[str, Any],
    manifest: dict[str, Any],
    source_dir: pathlib.Path,
    provisional_verified: dict[str, dict[str, Any]] | None = None,
) -> dict[str, Any]:
    provisional_verified = provisional_verified or {}
    function_by_usr = {
        str(item.get("clang_usr")): item
        for item in functions.get("functions", [])
    }
    candidate_by_usr = {
        str(item.get("clang_usr")): item
        for item in candidates.get("functions", [])
    }
    accepted_by_name = {
        str(item.get("function")): item
        for item in manifest.get("components", [])
        if item.get("status") == "PASS" and item.get("function")
    }
    internal_names = {
        str(item.get("name")) for item in functions.get("functions", [])
    }
    runtime_records = [
        item for item in coverage.get("functions", [])
        if item.get("coverage_status") == "EXECUTED"
    ]
    rows: list[dict[str, Any]] = []
    for runtime in runtime_records:
        usr = str(runtime.get("clang_usr", ""))
        function = function_by_usr.get(usr, {})
        candidate = candidate_by_usr.get(usr, {})
        if candidate.get("role") != "DUT":
            continue
        name = str(runtime.get("name", function.get("name", "")))
        accepted = accepted_by_name.get(name)
        provisional = provisional_verified.get(name)
        internal_callees = sorted(
            str(item.get("name"))
            for item in function.get("callees", [])
            if item.get("name") in internal_names
        )
        missing_internal_callees = [
            callee for callee in internal_callees
            if callee not in accepted_by_name and callee not in provisional_verified
        ]
        pointer_modes = sorted({
            str(item.get("mode"))
            for item in function.get("pointer_parameters", [])
            if item.get("mode")
        })
        blockers = []
        if (candidate.get("direct_effects", {}) or {}).get("state_write"):
            blockers.append("EXPLICIT_STATE_OUTPUT_CONTRACT_REQUIRED")
        if "WRITES_THROUGH" in pointer_modes:
            blockers.append("POINTER_OUTPUT_CONTRACT_REQUIRED")
        if not candidate.get("bounded_computation"):
            blockers.append("LOOP_BOUND_OR_DECOMPOSITION_REQUIRED")
        if missing_internal_callees:
            blockers.append("MISSING_CALLEE_RTL")
        c_boundary = c_orchestration_boundary(function, candidate)
        status = (
            "STABLE_RTL"
            if accepted
            else "PROVISIONAL_RTL_PASS"
            if provisional
            else "C_ORCHESTRATION_BOUNDARY"
            if c_boundary
            else "AUTO_GENERATION_READY"
            if candidate.get("eligible")
            else "TRANSITION_CONTRACT_REQUIRED"
        )
        row = {
            "clang_usr": usr,
            "name": name,
            "source_file": function.get("source_file"),
            "line": function.get("line"),
            "end_line": function.get("end_line"),
            "execution_count": (runtime.get("coverage", {}) or {}).get("execution_count", 0),
            "runtime_status": runtime.get("coverage_status"),
            "rtl_status": status,
            "accepted_contract_id": accepted.get("contract_id") if accepted else None,
            "provisional_contract_id": provisional.get("contract_id") if provisional else None,
            "auto_eligible": bool(candidate.get("eligible")),
            "purity": candidate.get("purity"),
            "timing": candidate.get("timing"),
            "bounded_computation": bool(candidate.get("bounded_computation")),
            "pointer_modes": pointer_modes,
            "internal_callees": internal_callees,
            "missing_internal_callees": missing_internal_callees,
            "leaf_at_current_rtl_frontier": not missing_internal_callees,
            "blockers": blockers,
            "c_boundary_class": c_boundary,
        }
        row["provisional_transition_shape"] = bool(
            not accepted and not provisional and transition_shape(function, candidate)
        )
        row["provisional_fifo_read_shape"] = bool(
            not accepted and not provisional
            and not missing_internal_callees
            and fifo_read_transition_shape(function, candidate)
        )
        row["provisional_fifo_accounting_shape"] = bool(
            not accepted and not provisional
            and not missing_internal_callees
            and fifo_read_accounting_shape(function, provisional_verified)
        )
        row["provisional_fifo_write_shape"] = bool(
            not accepted and not provisional
            and not missing_internal_callees
            and fifo_write_transition_shape(function, candidate)
        )
        row["provisional_scalar_record_shape"] = bool(
            not accepted and not provisional
            and not missing_internal_callees
            and scalar_record_next_state_shape(function, candidate)
        )
        row["provisional_sampled_lookup_shape"] = bool(
            not accepted and not provisional
            and not missing_internal_callees
            and sampled_lookup_transition_shape(function, candidate)
        )
        row["provisional_scalar_memory_shape"] = bool(
            not accepted and not provisional
            and not missing_internal_callees
            and scalar_record_memory_transition_shape(function, candidate)
        )
        row["provisional_mux_refill_shape"] = bool(
            not accepted and not provisional
            and not missing_internal_callees
            and bounded_mux_refill_transition_shape(function, provisional_verified)
        )
        row["provisional_flatness_state_shape"] = bool(
            not accepted and not provisional
            and not missing_internal_callees
            and bounded_flatness_state_transition_shape(function, candidate)
        )
        row["provisional_line_write_shape"] = bool(
            not accepted and not provisional
            and not missing_internal_callees
            and bounded_line_write_transition_shape(function, candidate)
        )
        row["provisional_history_update_shape"] = bool(
            not accepted and not provisional
            and not missing_internal_callees
            and bounded_history_update_transition_shape(
                function, candidate, provisional_verified
            )
        )
        row["provisional_history_caller_shape"] = bool(
            not accepted and not provisional
            and not missing_internal_callees
            and bounded_history_caller_transition_shape(
                function, candidate, provisional_verified
            )
        )
        row["provisional_vld_unit_shape"] = bool(
            not accepted and not provisional
            and not missing_internal_callees
            and bounded_vld_unit_transition_shape(
                function, candidate, provisional_verified
            )
        )
        row["provisional_vld_group_shape"] = bool(
            not accepted and not provisional
            and not missing_internal_callees
            and bounded_vld_group_transition_shape(
                function, candidate, provisional_verified
            )
        )
        row["provisional_raster_color_transform_shape"] = bool(
            not accepted and not provisional
            and not missing_internal_callees
            and raster_color_transform_shape(function, candidate)
        )
        row["provisional_block_pred_search_shape"] = bool(
            not accepted and not provisional
            and not missing_internal_callees
            and bounded_block_pred_search_transition_shape(function, candidate)
        )
        row["provisional_prediction_decode_shape"] = bool(
            not accepted and not provisional
            and not missing_internal_callees
            and bounded_prediction_decode_transition_shape(function, candidate)
        )
        row["provisional_rate_control_decode_shape"] = bool(
            not accepted and not provisional
            and not missing_internal_callees
            and bounded_rate_control_decode_transition_shape(
                function, candidate, provisional_verified
            )
        )
        rows.append(row)

    rows.sort(key=lambda item: str(item["name"]))
    stable_runtime = [item for item in rows if item["rtl_status"] == "STABLE_RTL"]
    provisional_runtime = [
        item for item in rows if item["rtl_status"] == "PROVISIONAL_RTL_PASS"
    ]
    c_boundaries = [
        item for item in rows if item["rtl_status"] == "C_ORCHESTRATION_BOUNDARY"
    ]
    missing_stable = [item for item in rows if item["rtl_status"] != "STABLE_RTL"]
    missing = [
        item for item in rows
        if item["rtl_status"] not in {
            "STABLE_RTL", "PROVISIONAL_RTL_PASS", "C_ORCHESTRATION_BOUNDARY"
        }
    ]
    auto_ready = [item for item in missing if item["rtl_status"] == "AUTO_GENERATION_READY"]
    transition = [
        (item, "bitstream_read_transition", 0)
        for item in missing if item["provisional_transition_shape"]
    ]
    transition.extend(
        (item, "fifo_read_transition", 1)
        for item in missing if item["provisional_fifo_read_shape"]
    )
    transition.extend(
        (item, "fifo_read_accounting_transition", 2)
        for item in missing if item["provisional_fifo_accounting_shape"]
    )
    transition.extend(
        (item, "fifo_write_transition", 2)
        for item in missing if item["provisional_fifo_write_shape"]
    )
    transition.extend(
        (item, "scalar_record_next_state", 3)
        for item in missing if item["provisional_scalar_record_shape"]
    )
    transition.extend(
        (item, "sampled_lookup_transition", 4)
        for item in missing if item["provisional_sampled_lookup_shape"]
    )
    transition.extend(
        (item, "scalar_record_memory_transition", 5)
        for item in missing if item["provisional_scalar_memory_shape"]
    )
    transition.extend(
        (item, "bounded_mux_refill_transition", 6)
        for item in missing if item["provisional_mux_refill_shape"]
    )
    transition.extend(
        (item, "bounded_flatness_state_transition", 7)
        for item in missing if item["provisional_flatness_state_shape"]
    )
    transition.extend(
        (item, "bounded_line_write_transition", 8)
        for item in missing if item["provisional_line_write_shape"]
    )
    transition.extend(
        (item, "bounded_history_update_transition", 9)
        for item in missing if item["provisional_history_update_shape"]
    )
    transition.extend(
        (item, "bounded_history_caller_transition", 10)
        for item in missing if item["provisional_history_caller_shape"]
    )
    transition.extend(
        (item, "bounded_vld_unit_transition", 11)
        for item in missing if item["provisional_vld_unit_shape"]
    )
    transition.extend(
        (item, "bounded_block_pred_search_transition", 12)
        for item in missing if item["provisional_block_pred_search_shape"]
    )
    transition.extend(
        (item, "bounded_prediction_decode_transition", 13)
        for item in missing if item["provisional_prediction_decode_shape"]
    )
    transition.extend(
        (item, "bounded_rate_control_decode_transition", 14)
        for item in missing if item["provisional_rate_control_decode_shape"]
    )
    transition.extend(
        (item, "bounded_vld_group_decode_transition", 15)
        for item in missing if item["provisional_vld_group_shape"]
    )
    transition.extend(
        (item, "raster_color_transform_transition", 16)
        for item in missing if item["provisional_raster_color_transform_shape"]
    )
    transition.sort(
        key=lambda value: (value[2], -int(value[0]["execution_count"]), str(value[0]["name"]))
    )
    provisional = []
    for item, semantics_kind, argument_index in transition:
        function = function_by_usr[item["clang_usr"]]
        if semantics_kind == "fifo_read_accounting_transition":
            callee_name = next(
                str(value.get("name"))
                for value in function.get("callees", [])
                if (provisional_verified.get(str(value.get("name")), {}) or {}).get("semantics_kind")
                == "fifo_read_transition"
            )
            callee = provisional_verified[callee_name]
            maximum = int(callee.get("max_bits", 0) or 0)
            bound = {
                "evidence": "verified provisional FIFO-read callee contract",
                "callee": callee_name,
                "callee_contract_id": callee.get("contract_id"),
                "maximum": maximum,
                "values": [],
                "complete_for_visible_literal_calls": False,
            }
        elif semantics_kind == "bounded_history_update_transition":
            callee_name = next(
                str(value.get("name"))
                for value in function.get("callees", [])
                if (provisional_verified.get(str(value.get("name")), {}) or {}).get(
                    "semantics_kind"
                ) == "sampled_lookup_transition"
            )
            callee = provisional_verified[callee_name]
            bound = {
                "evidence": (
                    "bounded MRU history update composed from a verified sampled "
                    "lookup transition"
                ),
                "callee": callee_name,
                "callee_contract_id": callee.get("contract_id"),
                "callee_contract_file": callee.get("contract_file"),
                "callee_contract_sha256": callee.get("contract_sha256"),
                "callee_candidate_file": callee.get("candidate_file"),
                "callee_candidate_sha256": callee.get("candidate_sha256"),
                "maximum": None,
                "values": [],
                "complete_for_visible_literal_calls": False,
            }
            maximum = None
        elif semantics_kind == "bounded_history_caller_transition":
            callee_name = next(
                str(value.get("name"))
                for value in function.get("callees", [])
                if (provisional_verified.get(str(value.get("name")), {}) or {}).get(
                    "semantics_kind"
                ) == "bounded_history_update_transition"
            )
            callee = provisional_verified[callee_name]
            bound = {
                "evidence": (
                    "bounded line-sample/history-clear caller composed from a "
                    "verified complete-history transition"
                ),
                "callee": callee_name,
                "callee_contract_id": callee.get("contract_id"),
                "callee_contract_file": callee.get("contract_file"),
                "callee_contract_sha256": callee.get("contract_sha256"),
                "callee_candidate_file": callee.get("candidate_file"),
                "callee_candidate_sha256": callee.get("candidate_sha256"),
                "maximum": None,
                "values": [],
                "complete_for_visible_literal_calls": False,
            }
            maximum = None
        elif semantics_kind == "bounded_vld_unit_transition":
            callee_name = next(
                str(value.get("name"))
                for value in function.get("callees", [])
                if (provisional_verified.get(str(value.get("name")), {}) or {}).get(
                    "semantics_kind"
                ) == "fifo_read_accounting_transition"
            )
            callee = provisional_verified[callee_name]
            bound = {
                "evidence": (
                    "bounded decoder syntax-unit transition composed from accepted "
                    "pure leaves and a verified FIFO accounting transition"
                ),
                "callee": callee_name,
                "callee_contract_id": callee.get("contract_id"),
                "callee_contract_file": callee.get("contract_file"),
                "callee_contract_sha256": callee.get("contract_sha256"),
                "callee_candidate_file": callee.get("candidate_file"),
                "callee_candidate_sha256": callee.get("candidate_sha256"),
                "maximum": None,
                "values": [],
                "complete_for_visible_literal_calls": False,
            }
            maximum = None
        elif semantics_kind == "bounded_block_pred_search_transition":
            callee_name = next(
                str(value.get("name"))
                for value in function.get("callees", [])
                if str(value.get("name")) in accepted_by_name
            )
            callee = accepted_by_name[callee_name]
            library_root = pathlib.Path(__file__).resolve().parent.parent / "library"
            callee_contract_path = library_root / str(callee.get("contract_file"))
            callee_candidate_path = library_root / str(callee.get("module_file"))
            bound = {
                "evidence": (
                    "fixed BP_RANGE/BP_SIZE predictor search composed from a "
                    "hash-bound accepted sample predictor"
                ),
                "callee": callee_name,
                "callee_contract_id": callee.get("contract_id"),
                "callee_contract_file": str(callee_contract_path),
                "callee_contract_sha256": file_hash(callee_contract_path),
                "callee_candidate_file": str(callee_candidate_path),
                "callee_candidate_sha256": file_hash(callee_candidate_path),
                "maximum": None,
                "values": [],
                "complete_for_visible_literal_calls": False,
            }
            maximum = None
        elif semantics_kind == "bounded_prediction_decode_transition":
            accepted_callees = [
                accepted_by_name[str(value.get("name"))]
                for value in function.get("callees", [])
                if str(value.get("name")) in accepted_by_name
            ]
            library_root = pathlib.Path(__file__).resolve().parent.parent / "library"
            dependencies = []
            for callee in sorted(
                accepted_callees, key=lambda value: str(value.get("contract_id"))
            ):
                contract_path = library_root / str(callee.get("contract_file"))
                candidate_path = library_root / str(callee.get("module_file"))
                dependencies.append({
                    "function": callee.get("function"),
                    "contract_id": callee.get("contract_id"),
                    "contract_file": str(contract_path),
                    "contract_sha256": file_hash(contract_path),
                    "candidate_file": str(candidate_path),
                    "candidate_sha256": file_hash(candidate_path),
                })
            bound = {
                "evidence": (
                    "fixed MAX_UNITS_PER_GROUP decoder reconstruction composed "
                    "from hash-bound accepted pure leaves; encoder-only branches "
                    "are outside this specialization"
                ),
                "accepted_dependencies": dependencies,
                "maximum": None,
                "values": [],
                "complete_for_visible_literal_calls": False,
            }
            maximum = None
        elif semantics_kind == "bounded_rate_control_decode_transition":
            callee_name = next(
                str(value.get("name"))
                for value in function.get("callees", [])
                if (provisional_verified.get(str(value.get("name")), {}) or {}).get(
                    "semantics_kind"
                ) == "scalar_record_memory_transition"
            )
            callee = provisional_verified[callee_name]
            bound = {
                "evidence": (
                    "bounded three-pixel decoder rate-control transition composed "
                    "from a hash-bound scalar-memory buffer-removal transition"
                ),
                "callee": callee_name,
                "callee_contract_id": callee.get("contract_id"),
                "callee_contract_file": callee.get("contract_file"),
                "callee_contract_sha256": callee.get("contract_sha256"),
                "callee_candidate_file": callee.get("candidate_file"),
                "callee_candidate_sha256": callee.get("candidate_sha256"),
                "maximum": None,
                "values": [],
                "complete_for_visible_literal_calls": False,
            }
            maximum = None
        elif semantics_kind == "bounded_vld_group_decode_transition":
            dependencies = []
            for callee_name in ("ProcessGroupDec", "VLDUnit"):
                callee = provisional_verified[callee_name]
                dependencies.append({
                    "function": callee_name,
                    "contract_id": callee.get("contract_id"),
                    "semantics_kind": callee.get("semantics_kind"),
                    "contract_file": callee.get("contract_file"),
                    "contract_sha256": callee.get("contract_sha256"),
                    "candidate_file": callee.get("candidate_file"),
                    "candidate_sha256": callee.get("candidate_sha256"),
                })
            bound = {
                "evidence": (
                    "bounded decoder group transition composed in source order "
                    "from hash-bound mux-refill and VLD-unit transitions"
                ),
                "dependencies": dependencies,
                "maximum": None,
                "values": [],
                "complete_for_visible_literal_calls": False,
            }
            maximum = None
        elif semantics_kind == "raster_color_transform_transition":
            direction = raster_color_transform_direction(function)
            if direction is None:
                continue
            bound = {
                "evidence": (
                    "typed RGB/YUV plane read-write direction plus a bounded "
                    "independent per-pixel arithmetic kernel"
                ),
                "direction": direction,
                "maximum": None,
                "values": [],
                "complete_for_visible_literal_calls": False,
            }
            maximum = None
        elif semantics_kind in {
            "scalar_record_next_state", "sampled_lookup_transition",
            "scalar_record_memory_transition", "bounded_mux_refill_transition",
            "bounded_flatness_state_transition",
            "bounded_line_write_transition",
        }:
            bound = {
                "evidence": (
                    "loop-free scalar record transition from Clang facts"
                    if semantics_kind == "scalar_record_next_state"
                    else "fixed-extent sampled lookup transition from Clang facts"
                    if semantics_kind == "sampled_lookup_transition"
                    else "loop-free scalar record plus one memory write from Clang facts"
                    if semantics_kind == "scalar_record_memory_transition"
                    else "bounded multi-lane refill composed from verified transition callees"
                    if semantics_kind == "bounded_mux_refill_transition"
                    else "fixed four-stage scalar state transition around accepted pure callees"
                    if semantics_kind == "bounded_flatness_state_transition"
                    else "fixed-extent state-to-line-buffer scatter transition"
                ),
                "maximum": None,
                "values": [],
                "complete_for_visible_literal_calls": False,
            }
            maximum = None
        else:
            bound = literal_argument_bound(function, source_dir, argument_index)
            maximum = bound.get("maximum")
        if semantics_kind == "fifo_read_transition" and isinstance(maximum, int):
            # The DSC state initializer admits 64-bit syntax-element FIFOs.
            # Keep the literal callsite evidence intact while using a
            # conservative transition-class cap for variable-width reads.
            maximum = max(maximum, 64)
        if semantics_kind == "fifo_write_transition" and isinstance(maximum, int):
            # The payload parameter is a 32-bit C unsigned int. Variable-width
            # writes are therefore frozen to that type-derived useful domain.
            maximum = max(maximum, 32)
        if (
            semantics_kind not in {
                "scalar_record_next_state", "sampled_lookup_transition",
                "scalar_record_memory_transition", "bounded_mux_refill_transition",
                "bounded_flatness_state_transition",
                "bounded_line_write_transition", "bounded_history_update_transition",
                "bounded_history_caller_transition",
                "bounded_vld_unit_transition",
                "bounded_block_pred_search_transition",
                "bounded_prediction_decode_transition",
                "bounded_rate_control_decode_transition",
                "bounded_vld_group_decode_transition",
                "raster_color_transform_transition",
            }
            and (not isinstance(maximum, int) or maximum <= 0 or maximum > 32)
        ):
            if semantics_kind not in {
                "fifo_read_transition", "fifo_read_accounting_transition"
            } or maximum > 64:
                continue
        provisional.append({
            "clang_usr": item["clang_usr"],
            "name": item["name"],
            "execution_count": item["execution_count"],
            "selection_basis": (
                "decoder runtime execution + no accepted/provisional RTL + "
                "tool-matched explicit state-transition shape"
            ),
            "semantics_kind": semantics_kind,
            "literal_size_bound": bound,
            "provisional_max_bits": maximum,
            "window_bytes": (
                math.ceil((maximum + 7) / 8)
                if isinstance(maximum, int) else 0
            ),
            "callee_contract_id": bound.get("callee_contract_id"),
            "human_review_required_before_promotion": True,
        })

    decode_runs = coverage.get("decode_runs", []) or []
    return {
        "schema_version": 1,
        "status": "PASS",
        "discovery_policy": "tool facts and decoder-only execution; no function allowlist",
        "coverage_phases": coverage.get("coverage_phases"),
        "decode_profiles": len(decode_runs),
        "decode_profiles_passed": sum(item.get("status") == "PASS" for item in decode_runs),
        "summary": {
            "runtime_source_functions": len(runtime_records),
            "runtime_dut_functions": len(rows),
            "runtime_dut_with_stable_rtl": len(stable_runtime),
            "runtime_dut_with_provisional_rtl": len(provisional_runtime),
            "runtime_dut_c_orchestration_boundaries": len(c_boundaries),
            "runtime_dut_missing_stable_rtl": len(missing_stable),
            "runtime_dut_without_any_rtl": len(c_boundaries) + len(missing),
            "runtime_compute_functions_without_any_rtl": len(missing),
            "auto_generation_ready_missing": len(auto_ready),
            "provisional_transition_candidates": len(provisional),
        },
        "stable_runtime_functions": stable_runtime,
        "provisional_runtime_functions": provisional_runtime,
        "c_orchestration_runtime_functions": c_boundaries,
        "missing_runtime_functions": missing,
        "auto_generation_ready": auto_ready,
        "provisional_transition_candidates": provisional,
    }


def render_report(frontier: dict[str, Any]) -> str:
    summary = frontier["summary"]
    integration = frontier.get("multi_rtl_integration", {}) or {}
    lines = [
        "# Decode RTL frontier",
        "",
        "Generated from decoder-only LLVM coverage, Clang facts, candidate effects, and the stable RTL manifest.",
        "No function-name allowlist is used.",
        "",
        f"- decode profiles: {frontier['decode_profiles_passed']}/{frontier['decode_profiles']} PASS",
        f"- runtime source functions: {summary['runtime_source_functions']}",
        f"- runtime DUT functions: {summary['runtime_dut_functions']}",
        f"- runtime DUT functions with stable RTL: {summary['runtime_dut_with_stable_rtl']}",
        f"- runtime DUT functions with provisional RTL PASS: {summary['runtime_dut_with_provisional_rtl']}",
        f"- runtime C orchestration/lifecycle boundaries: {summary['runtime_dut_c_orchestration_boundaries']}",
        f"- runtime DUT functions missing stable RTL: {summary['runtime_dut_missing_stable_rtl']}",
        f"- runtime DUT functions without any RTL: {summary['runtime_dut_without_any_rtl']}",
        f"- unresolved runtime compute functions without RTL: {summary['runtime_compute_functions_without_any_rtl']}",
        f"- existing auto-generation-ready gaps: {summary['auto_generation_ready_missing']}",
        f"- provisional state-transition candidates: {summary['provisional_transition_candidates']}",
        f"- simultaneous multi-RTL integration: {integration.get('status', 'NOT_RUN')}",
        f"- integration profiles/candidates: {integration.get('profiles', 0)}/{integration.get('candidate_count', 0)}",
        "",
        "## Stable RTL reached by Decode",
        "",
        "| Function | Calls | Contract |",
        "|---|---:|---|",
    ]
    for item in frontier["stable_runtime_functions"]:
        lines.append(
            f"| {item['name']} | {item['execution_count']} | {item['accepted_contract_id']} |"
        )
    lines.extend([
        "",
        "## Provisional RTL passed full-frame regression",
        "",
        "| Function | Calls | Contract |",
        "|---|---:|---|",
    ])
    if not frontier["provisional_runtime_functions"]:
        lines.append("| none | 0 | none |")
    for item in frontier["provisional_runtime_functions"]:
        lines.append(
            f"| {item['name']} | {item['execution_count']} | {item['provisional_contract_id']} |"
        )
    lines.extend([
        "",
        "## Intentional C orchestration and lifecycle boundaries",
        "",
        "| Function | Calls | Boundary class |",
        "|---|---:|---|",
    ])
    if not frontier["c_orchestration_runtime_functions"]:
        lines.append("| none | 0 | none |")
    for item in frontier["c_orchestration_runtime_functions"]:
        lines.append(
            f"| {item['name']} | {item['execution_count']} | {item['c_boundary_class']} |"
        )
    lines.extend([
        "",
        "## Unresolved runtime compute functions",
        "",
        "| Function | Calls | Frontier | Required work |",
        "|---|---:|---|---|",
    ])
    if not frontier["missing_runtime_functions"]:
        lines.append("| none | 0 | complete at current compute boundaries |")
    for item in frontier["missing_runtime_functions"]:
        blockers = ", ".join(item["blockers"]) or "contract/generation"
        lines.append(
            f"| {item['name']} | {item['execution_count']} | "
            f"{'leaf' if item['leaf_at_current_rtl_frontier'] else 'composite'} | {blockers} |"
        )
    lines.extend([
        "",
        "## Tool-selected provisional transition candidates",
        "",
    ])
    if not frontier["provisional_transition_candidates"]:
        lines.append("None.")
    for item in frontier["provisional_transition_candidates"]:
        bound = item["literal_size_bound"]
        lines.append(
            f"- {item['name']}: `{item['semantics_kind']}`, literal size values "
            f"{bound['values']}, {item['window_bytes']} input bytes; promotion remains human-gated."
        )
    return "\n".join(lines) + "\n"


def attach_integration_receipt(
    frontier: dict[str, Any], receipt_path: pathlib.Path | None
) -> None:
    if receipt_path is None or not receipt_path.is_file():
        frontier["multi_rtl_integration"] = {"status": "NOT_RUN"}
        return
    receipt = read_json(receipt_path)
    modes = receipt.get("modes", {}) or {}
    frontier["multi_rtl_integration"] = {
        "status": receipt.get("status"),
        "receipt": str(receipt_path),
        "receipt_sha256": file_hash(receipt_path),
        "matrix_scope": receipt.get("matrix_scope"),
        "profiles": receipt.get("profiles"),
        "candidate_count": receipt.get("candidate_count"),
        "comparison": receipt.get("comparison"),
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


def scan_provisional(root: pathlib.Path | None) -> dict[str, dict[str, Any]]:
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
        contract_path = verification_path.parent / "provisional-contract.json"
        if not contract_path.is_file():
            continue
        contract = read_json(contract_path)
        function = contract.get("function", {}) or {}
        name = str(function.get("name", ""))
        if name:
            candidate_path = verification_path.parent / "candidate_01.sv"
            result[name] = {
                "contract_id": contract.get("contract_id"),
                "verification_receipt": str(verification_path),
                "contract_file": str(contract_path),
                "contract_sha256": hashlib.sha256(contract_path.read_bytes()).hexdigest(),
                "candidate_file": str(candidate_path) if candidate_path.is_file() else None,
                "candidate_sha256": (
                    hashlib.sha256(candidate_path.read_bytes()).hexdigest()
                    if candidate_path.is_file() else None
                ),
                "matrix_scope": verification.get("matrix_scope"),
                "semantics_kind": (contract.get("semantics", {}) or {}).get("kind"),
                "max_bits": (contract.get("semantics", {}) or {}).get("max_bits"),
                "window_bytes": (contract.get("semantics", {}) or {}).get("window_bytes"),
            }
    return result


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
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    frontier = discover(
        read_json(args.coverage),
        read_json(args.functions),
        read_json(args.candidates),
        read_json(args.manifest),
        args.source_dir.resolve(),
        scan_provisional(args.provisional_root.resolve() if args.provisional_root else None),
    )
    attach_integration_receipt(
        frontier,
        args.integration_receipt.resolve() if args.integration_receipt else None,
    )
    write_json(args.output, frontier)
    args.report.parent.mkdir(parents=True, exist_ok=True)
    args.report.write_text(render_report(frontier), encoding="utf-8")
    print(
        "decode frontier: "
        f"{frontier['summary']['runtime_dut_with_stable_rtl']} RTL-covered, "
        f"{frontier['summary']['runtime_compute_functions_without_any_rtl']} "
        "unresolved compute functions"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
