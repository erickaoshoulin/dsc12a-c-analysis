#!/usr/bin/env python3
"""Verilator/C adapter emitter for the bounded Encode ProcessGroup FSM."""

from __future__ import annotations

import hashlib
import pathlib
import re
from typing import Any


_PG_SSPS = 4
_PG_MIN_SSPS = 3
_PG_MUX_WORD_SIZES = (48, 64)
_PG_MAX_SE_SIZE = 68
_PG_MAX_CYCLES = 10000


def _identifier(value: str) -> str:
    return re.sub(r"[^A-Za-z0-9_]", "_", value)


def _sha256(path: pathlib.Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def write_process_group_encode_overlay_sources(
    agent: Any,
    contract: dict[str, Any],
    source_dir: pathlib.Path,
    module: str,
    candidate_sv: pathlib.Path,
) -> dict[str, Any]:
    """Emit a deep-snapshot oracle and cycle-accurate external-memory bridge."""

    source_dir = pathlib.Path(source_dir)
    source_dir.mkdir(parents=True, exist_ok=True)
    candidate_sv = pathlib.Path(candidate_sv)

    semantics = contract.get("semantics", {}) or {}
    if semantics.get("kind") != "bounded_process_group_encode_transition":
        raise RuntimeError("unsupported ProcessGroup Encode semantic kind")
    constants = semantics.get("constants", {}) or {}
    if (
        int(constants.get("max_ssps", 0)) != _PG_SSPS
        or int(constants.get("min_ssps", 0)) != _PG_MIN_SSPS
        or tuple(constants.get("mux_word_sizes", [])) != _PG_MUX_WORD_SIZES
        or int(constants.get("max_se_size", 0)) != _PG_MAX_SE_SIZE
    ):
        raise RuntimeError("ProcessGroup Encode bounds changed")

    function = contract.get("function", {}) or {}
    parameters = list(function.get("parameters", []) or [])
    expected_parameters = [
        ("dsc_cfg", "dsc_cfg_t *"),
        ("dsc_state", "dsc_state_t *"),
        ("buf", "unsigned char *"),
    ]
    if function.get("name") != "ProcessGroupEnc":
        raise RuntimeError("ProcessGroup Encode function identity changed")
    if len(parameters) != len(expected_parameters) or any(
        not isinstance(item, dict)
        or item.get("name") != name
        or str(item.get("type", "")).strip() != type_name
        or item.get("pointer") is not True
        for item, (name, type_name) in zip(parameters, expected_parameters)
    ):
        raise RuntimeError("ProcessGroup Encode native ABI changed")
    parameter_names = [str(item.get("name", "")) for item in parameters]
    if not all(re.fullmatch(r"[A-Za-z_][A-Za-z0-9_]*", item) for item in parameter_names):
        raise RuntimeError("ProcessGroup Encode parameter name is invalid")
    parameter_specs = [
        f"{str(item.get('type', 'int')).strip()} {item.get('name')}"
        for item in parameters
    ]
    caller_declarations = ", ".join(parameter_specs)
    alias_call = ", ".join(parameter_names)
    config_parameter, state_parameter, buffer_parameter = parameter_names
    function_name = str(function.get("name", ""))
    original = function_name + "_original"
    if not function_name:
        raise RuntimeError("ProcessGroup Encode function identity is missing")

    rtl = contract.get("rtl", {}) or {}
    expected_module = str(rtl.get("module", ""))
    if (
        not re.fullmatch(r"[A-Za-z_][A-Za-z0-9_]*", module)
        or module != expected_module
        or not candidate_sv.is_file()
    ):
        raise RuntimeError("ProcessGroup Encode RTL module identity is invalid")
    expected_candidate_hash = str(rtl.get("candidate_sha256", "")).lower()
    if not re.fullmatch(r"[0-9a-f]{64}", expected_candidate_hash):
        raise RuntimeError("ProcessGroup Encode candidate hash is missing")
    if _sha256(candidate_sv) != expected_candidate_hash:
        raise RuntimeError("ProcessGroup Encode selected candidate bytes changed")
    candidate_text = candidate_sv.read_text(encoding="utf-8", errors="replace")
    module_match = re.search(
        r"\bmodule\s+([A-Za-z_][A-Za-z0-9_]*)\s*(?:#\s*\(|\()",
        candidate_text,
    )
    if not module_match or module_match.group(1) != module:
        raise RuntimeError("ProcessGroup Encode candidate module name changed")

    ports = list((contract.get("interface", {}) or {}).get("ports", []) or [])
    if any(not isinstance(item, dict) for item in ports):
        raise RuntimeError("ProcessGroup Encode port metadata is invalid")

    expected_ports: dict[str, tuple[str, str, str]] = {}

    def add_port(name: str, direction: str, width: int, unpacked: str = "") -> None:
        expected_ports[name] = (direction, str(width), unpacked)

    for name, direction, width in (
        ("clk", "input", 1),
        ("rst_n", "input", 1),
        ("start", "input", 1),
        ("is_encoder", "input", 1),
        ("num_ssps", "input", 3),
        ("mux_word_size", "input", 7),
        ("frame_capacity_bits", "input", 32),
        ("busy", "output", 1),
        ("done", "output", 1),
        ("illegal_domain", "output", 1),
        ("fifo_underflow", "output", 1),
        ("fifo_overflow", "output", 1),
        ("frame_overflow", "output", 1),
        ("se_size_overflow", "output", 1),
        ("post_mux_num_bits_in", "input", 32),
        ("post_mux_num_bits_out", "output", 32),
    ):
        add_port(name, direction, width)
    add_port("max_se_size", "input", 7, "[0:3]")
    for prefix in ("enc_balance", "shifter", "se_size"):
        for field in (
            "size_bits", "fullness", "read_ptr", "write_ptr",
            "max_fullness", "byte_ctr",
        ):
            add_port(f"{prefix}_{field}_in", "input", 32, "[0:3]")
            add_port(f"{prefix}_{field}_out", "output", 32, "[0:3]")
        for suffix in (
            "mem_read_req", "mem_read_addr", "mem_read_valid", "mem_read_data",
            "mem_write_req", "mem_write_addr", "mem_write_ready",
            "mem_write_data", "mem_write_bit_mask",
        ):
            if suffix in {"mem_read_req", "mem_write_req"}:
                add_port(f"{prefix}_{suffix}", "output", 4)
            elif suffix in {"mem_read_valid", "mem_write_ready"}:
                add_port(f"{prefix}_{suffix}", "input", 4)
            elif suffix.endswith("_addr"):
                add_port(f"{prefix}_{suffix}", "output", 16, "[0:3]")
            elif suffix == "mem_read_data":
                add_port(f"{prefix}_{suffix}", "input", 8, "[0:3]")
            else:
                add_port(f"{prefix}_{suffix}", "output", 8, "[0:3]")
    add_port("frame_mem_write_req", "output", 1)
    add_port("frame_mem_write_addr", "output", 32)
    add_port("frame_mem_write_ready", "input", 1)
    add_port("frame_mem_write_data", "output", 8)
    add_port("frame_mem_write_bit_mask", "output", 8)

    port_by_name = {
        str(item.get("name")): item
        for item in ports
    }
    if len(port_by_name) != len(ports) or set(port_by_name) != set(expected_ports):
        missing = sorted(set(expected_ports) - set(port_by_name))
        extra = sorted(set(port_by_name) - set(expected_ports))
        raise RuntimeError(
            f"ProcessGroup Encode frozen ports changed: missing={missing} extra={extra}"
        )
    for name, (direction, width, unpacked) in expected_ports.items():
        port = port_by_name[name]
        if (
            str(port.get("direction")) != direction
            or str(port.get("width")) != width
            or str(port.get("unpacked", "")) != unpacked
        ):
            raise RuntimeError(f"ProcessGroup Encode port ABI changed: {name}")

    abi = source_dir / "dsc_cicd_rtl_abi.h"
    abi.write_text(
        """#ifndef DSC_CICD_RTL_ABI_H
#define DSC_CICD_RTL_ABI_H
#include <stdint.h>
#define DSC_CICD_PG_SSPS 4
#define DSC_CICD_PG_MIN_SSPS 3
#define DSC_CICD_PG_MAX_MUX_WORD_SIZE 64
#define DSC_CICD_PG_MAX_SE_SIZE 68
#define DSC_CICD_PG_MAX_CYCLES 10000u
typedef struct {
    uint8_t *data;
    uint32_t size_bits;
    uint32_t fullness;
    uint32_t read_ptr;
    uint32_t write_ptr;
    uint32_t max_fullness;
    uint32_t byte_ctr;
} dsc_cicd_pg_fifo_t;
typedef struct {
    int32_t is_encoder;
    uint32_t num_ssps;
    uint32_t mux_word_size;
    uint32_t max_se_size[DSC_CICD_PG_SSPS];
    uint32_t post_mux_num_bits;
    uint32_t frame_capacity_bits;
    uint8_t *frame_data;
    dsc_cicd_pg_fifo_t enc_balance[DSC_CICD_PG_SSPS];
    dsc_cicd_pg_fifo_t shifter[DSC_CICD_PG_SSPS];
    dsc_cicd_pg_fifo_t se_size[DSC_CICD_PG_SSPS];
} dsc_cicd_pg_input_t;
typedef struct {
    uint32_t post_mux_num_bits;
    dsc_cicd_pg_fifo_t enc_balance[DSC_CICD_PG_SSPS];
    dsc_cicd_pg_fifo_t shifter[DSC_CICD_PG_SSPS];
    dsc_cicd_pg_fifo_t se_size[DSC_CICD_PG_SSPS];
    int32_t illegal_domain;
    int32_t fifo_underflow;
    int32_t fifo_overflow;
    int32_t frame_overflow;
    int32_t se_size_overflow;
    int32_t bridge_error;
    uint32_t cycles;
} dsc_cicd_pg_output_t;
#ifdef __cplusplus
extern "C" {
#endif
void dsc_cicd_rtl(dsc_cicd_pg_input_t *input, dsc_cicd_pg_output_t *output);
#ifdef __cplusplus
}
#endif
#endif
""",
        encoding="utf-8",
    )

    header = source_dir / "dsc_cicd_overlay.h"
    header.write_text(
        "#ifndef DSC_CICD_OVERLAY_H\n#define DSC_CICD_OVERLAY_H\n"
        "#include \"dsc_types.h\"\n"
        f"void dsc_cicd_invoke({caller_declarations});\n#endif\n",
        encoding="utf-8",
    )

    overlay_template = r'''#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <limits.h>
#include "dsc_cicd_overlay.h"
#include "dsc_cicd_rtl_abi.h"
extern void __ORIGINAL__(__CALLER_DECLARATIONS__);

static int dsc_cicd_mode(void) {
    const char *value = getenv("DSC_CICD_MODE");
    if (value && strcmp(value, "SHADOW") == 0) return 1;
    if (value && strcmp(value, "RTL_RETURN") == 0) return 2;
    return 0;
}
__METRICS__
static void dsc_cicd_fail(const char *message) {
    fprintf(stderr, "unsupported ProcessGroupEnc bridge domain: %s\n", message);
    exit(2);
}

static int dsc_cicd_fifo_domain_is_valid(const fifo_t *fifo) {
    return fifo && fifo->data && fifo->size > 0 && !(fifo->size & 7) &&
        fifo->fullness >= 0 && fifo->fullness <= fifo->size &&
        fifo->read_ptr >= 0 && fifo->read_ptr < fifo->size &&
        fifo->write_ptr >= 0 && fifo->write_ptr < fifo->size &&
        fifo->max_fullness >= 0 && fifo->max_fullness <= fifo->size;
}

static unsigned int dsc_cicd_peek_fifo_bits(const fifo_t *fifo, int nbits) {
    unsigned int value = 0;
    int pointer = fifo->read_ptr;
    for (int index = 0; index < nbits; ++index) {
        value = (value << 1) |
            ((fifo->data[pointer / 8] >> (7 - (pointer % 8))) & 1u);
        if (++pointer >= fifo->size)
            pointer = 0;
    }
    return value;
}

static void dsc_cicd_validate_bridge_domain(
    const dsc_cfg_t *cfg, const dsc_state_t *state, const unsigned char *buffer
) {
    if (!cfg || !state || !buffer || state->isEncoder != 1 ||
        state->numSsps < DSC_CICD_PG_MIN_SSPS ||
        state->numSsps > DSC_CICD_PG_SSPS ||
        (cfg->mux_word_size != 48 && cfg->mux_word_size != 64))
        dsc_cicd_fail("top-level bounds");
    if (state->postMuxNumBits < 0)
        dsc_cicd_fail("negative frame cursor");

    uint64_t max_output_bits = (uint64_t)state->numSsps *
        (uint64_t)cfg->mux_word_size;
    uint64_t frame_capacity_bits = (uint64_t)state->postMuxNumBits +
        max_output_bits + 8u;
    if (max_output_bits > (uint64_t)INT_MAX - (uint64_t)state->postMuxNumBits ||
        frame_capacity_bits > UINT32_MAX)
        dsc_cicd_fail("frame cursor or capacity overflow");

    for (int lane = 0; lane < state->numSsps; ++lane) {
        if (state->maxSeSize[lane] <= 0 ||
            state->maxSeSize[lane] > DSC_CICD_PG_MAX_SE_SIZE ||
            !dsc_cicd_fifo_domain_is_valid(&state->encBalanceFifo[lane]) ||
            !dsc_cicd_fifo_domain_is_valid(&state->shifter[lane]) ||
            !dsc_cicd_fifo_domain_is_valid(&state->seSizeFifo[lane]))
            dsc_cicd_fail("active FIFO or SE-size bounds");
        uint64_t refill_bits = state->shifter[lane].fullness <
            state->maxSeSize[lane] ? (uint64_t)cfg->mux_word_size : 0u;
        if (state->seSizeFifo[lane].fullness < 8)
            dsc_cicd_fail("syntax-element size FIFO underflow");
        unsigned int se_size = dsc_cicd_peek_fifo_bits(&state->seSizeFifo[lane], 8);
        if ((uint64_t)state->shifter[lane].fullness + refill_bits >
                (uint64_t)state->shifter[lane].size ||
            se_size > DSC_CICD_PG_MAX_SE_SIZE ||
            (uint64_t)state->shifter[lane].fullness + refill_bits < se_size)
            dsc_cicd_fail("ProcessGroupEnc FIFO operation bounds");
    }
}

typedef struct {
    fifo_t scalar;
    unsigned char *bytes;
    size_t byte_count;
} dsc_cicd_fifo_snapshot_t;

static void dsc_cicd_snapshot_fifo(
    const fifo_t *fifo, dsc_cicd_fifo_snapshot_t *snapshot
) {
    if (!dsc_cicd_fifo_domain_is_valid(fifo) || !snapshot)
        dsc_cicd_fail("FIFO snapshot");
    snapshot->scalar = *fifo;
    snapshot->byte_count = (size_t)fifo->size / 8u;
    snapshot->bytes = (unsigned char *)malloc(snapshot->byte_count);
    if (!snapshot->bytes) exit(2);
    memcpy(snapshot->bytes, fifo->data, snapshot->byte_count);
}

static void dsc_cicd_snapshot_inactive_fifo(
    const fifo_t *fifo, dsc_cicd_fifo_snapshot_t *snapshot
) {
    if (!fifo || !snapshot)
        dsc_cicd_fail("inactive FIFO snapshot");
    snapshot->scalar = *fifo;
    snapshot->bytes = NULL;
    snapshot->byte_count = 0;
    /* Inactive storage is never dereferenced; its scalar image is passthrough. */
}

static void dsc_cicd_restore_fifo(
    fifo_t *fifo, const dsc_cicd_fifo_snapshot_t *snapshot
) {
    if (!fifo || !snapshot ||
        (snapshot->bytes && fifo->data != snapshot->scalar.data))
        dsc_cicd_fail("FIFO restore ownership");
    *fifo = snapshot->scalar;
    if (snapshot->bytes)
        memcpy(fifo->data, snapshot->bytes, snapshot->byte_count);
}

static int dsc_cicd_fifo_matches(
    const fifo_t *fifo, const dsc_cicd_fifo_snapshot_t *snapshot
) {
    return fifo && snapshot &&
        fifo->data == snapshot->scalar.data &&
        fifo->size == snapshot->scalar.size &&
        fifo->fullness == snapshot->scalar.fullness &&
        fifo->read_ptr == snapshot->scalar.read_ptr &&
        fifo->write_ptr == snapshot->scalar.write_ptr &&
        fifo->max_fullness == snapshot->scalar.max_fullness &&
        fifo->byte_ctr == snapshot->scalar.byte_ctr &&
        (!snapshot->bytes || memcmp(fifo->data, snapshot->bytes,
                                     snapshot->byte_count) == 0);
}

static void dsc_cicd_free_fifo_snapshot(dsc_cicd_fifo_snapshot_t *snapshot) {
    free(snapshot->bytes);
    snapshot->bytes = NULL;
}

static void dsc_cicd_fill_fifo(
    dsc_cicd_pg_fifo_t *target, fifo_t *source
) {
    target->data = source->data;
    target->size_bits = (uint32_t)source->size;
    target->fullness = (uint32_t)source->fullness;
    target->read_ptr = (uint32_t)source->read_ptr;
    target->write_ptr = (uint32_t)source->write_ptr;
    target->max_fullness = (uint32_t)source->max_fullness;
    target->byte_ctr = (uint32_t)source->byte_ctr;
}

static void dsc_cicd_apply_fifo_scalars(
    fifo_t *target, const dsc_cicd_pg_fifo_t *source
) {
    target->size = (int)source->size_bits;
    target->fullness = (int)source->fullness;
    target->read_ptr = (int)source->read_ptr;
    target->write_ptr = (int)source->write_ptr;
    target->max_fullness = (int)source->max_fullness;
    target->byte_ctr = (int)source->byte_ctr;
}

void dsc_cicd_invoke(__CALLER_DECLARATIONS__) {
    int mode = dsc_cicd_mode();
    dsc_cicd_note_call(mode);
    if (mode == 0) {
        __ORIGINAL__(__ALIAS_CALL__);
        return;
    }
    dsc_cicd_validate_bridge_domain(__CFG__, __STATE__, __BUFFER__);

    fifo_t *banks[3] = {
        __STATE__->encBalanceFifo, __STATE__->shifter, __STATE__->seSizeFifo
    };
    dsc_cicd_fifo_snapshot_t pre[3][DSC_CICD_PG_SSPS] = {{{0}}};
    dsc_cicd_fifo_snapshot_t oracle[3][DSC_CICD_PG_SSPS] = {{{0}}};
    for (int bank = 0; bank < 3; ++bank)
        for (int lane = 0; lane < DSC_CICD_PG_SSPS; ++lane)
            if (lane < __STATE__->numSsps)
                dsc_cicd_snapshot_fifo(&banks[bank][lane], &pre[bank][lane]);
            else
                dsc_cicd_snapshot_inactive_fifo(&banks[bank][lane], &pre[bank][lane]);

    int pre_post_mux = __STATE__->postMuxNumBits;
    size_t frame_start = (size_t)pre_post_mux / 8u;
    size_t frame_span = (size_t)(__STATE__->numSsps * (__CFG__->mux_word_size / 8)) + 2u;
    if (frame_start > (size_t)-1 - frame_span)
        dsc_cicd_fail("frame snapshot address overflow");
    unsigned char *pre_frame = (unsigned char *)malloc(frame_span);
    unsigned char *oracle_frame = (unsigned char *)malloc(frame_span);
    if (!pre_frame || !oracle_frame) exit(2);
    memcpy(pre_frame, __BUFFER__ + frame_start, frame_span);

    __ORIGINAL__(__ALIAS_CALL__);
    int oracle_post_mux = __STATE__->postMuxNumBits;
    for (int bank = 0; bank < 3; ++bank)
        for (int lane = 0; lane < DSC_CICD_PG_SSPS; ++lane)
            if (lane < __STATE__->numSsps)
                dsc_cicd_snapshot_fifo(&banks[bank][lane], &oracle[bank][lane]);
            else
                dsc_cicd_snapshot_inactive_fifo(&banks[bank][lane], &oracle[bank][lane]);
    memcpy(oracle_frame, __BUFFER__ + frame_start, frame_span);

    __STATE__->postMuxNumBits = pre_post_mux;
    for (int bank = 0; bank < 3; ++bank)
        for (int lane = 0; lane < DSC_CICD_PG_SSPS; ++lane)
            dsc_cicd_restore_fifo(&banks[bank][lane], &pre[bank][lane]);
    memcpy(__BUFFER__ + frame_start, pre_frame, frame_span);

    dsc_cicd_pg_input_t input;
    dsc_cicd_pg_output_t output;
    memset(&input, 0, sizeof(input));
    memset(&output, 0, sizeof(output));
    input.is_encoder = __STATE__->isEncoder;
    input.num_ssps = (uint32_t)__STATE__->numSsps;
    input.mux_word_size = (uint32_t)__CFG__->mux_word_size;
    input.post_mux_num_bits = (uint32_t)__STATE__->postMuxNumBits;
    input.frame_capacity_bits = (uint32_t)((uint64_t)pre_post_mux +
        (uint64_t)__STATE__->numSsps * (uint64_t)__CFG__->mux_word_size + 8u);
    input.frame_data = __BUFFER__;
    for (int lane = 0; lane < DSC_CICD_PG_SSPS; ++lane) {
        input.max_se_size[lane] = (uint32_t)__STATE__->maxSeSize[lane];
        dsc_cicd_fill_fifo(&input.enc_balance[lane], &__STATE__->encBalanceFifo[lane]);
        dsc_cicd_fill_fifo(&input.shifter[lane], &__STATE__->shifter[lane]);
        dsc_cicd_fill_fifo(&input.se_size[lane], &__STATE__->seSizeFifo[lane]);
    }
    dsc_cicd_rtl(&input, &output);
    __STATE__->postMuxNumBits = (int)output.post_mux_num_bits;
    for (int lane = 0; lane < __STATE__->numSsps; ++lane) {
        dsc_cicd_apply_fifo_scalars(&__STATE__->encBalanceFifo[lane], &output.enc_balance[lane]);
        dsc_cicd_apply_fifo_scalars(&__STATE__->shifter[lane], &output.shifter[lane]);
        dsc_cicd_apply_fifo_scalars(&__STATE__->seSizeFifo[lane], &output.se_size[lane]);
    }

    int mismatch = output.bridge_error || output.illegal_domain ||
        output.fifo_underflow || output.fifo_overflow || output.frame_overflow ||
        output.se_size_overflow || __STATE__->postMuxNumBits != oracle_post_mux ||
        memcmp(__BUFFER__ + frame_start, oracle_frame, frame_span) != 0;
    for (int bank = 0; bank < 3; ++bank)
        for (int lane = 0; lane < DSC_CICD_PG_SSPS; ++lane)
            mismatch |= !dsc_cicd_fifo_matches(&banks[bank][lane], &oracle[bank][lane]);
    if (mismatch) {
        ++dsc_cicd_mismatches;
        fprintf(stderr, "C/RTL ProcessGroupEnc mismatch: cycles=%u flags=%d/%d/%d/%d/%d bridge=%d\n",
            output.cycles, output.illegal_domain, output.fifo_underflow,
            output.fifo_overflow, output.frame_overflow, output.se_size_overflow,
            output.bridge_error);
    }

    if (mode == 1) {
        __STATE__->postMuxNumBits = oracle_post_mux;
        for (int bank = 0; bank < 3; ++bank)
            for (int lane = 0; lane < DSC_CICD_PG_SSPS; ++lane)
                dsc_cicd_restore_fifo(&banks[bank][lane], &oracle[bank][lane]);
        memcpy(__BUFFER__ + frame_start, oracle_frame, frame_span);
    } else if (mode == 2) {
        /* RTL_RETURN commits active RTL state; inactive lanes are passthrough. */
        for (int bank = 0; bank < 3; ++bank)
            for (int lane = __STATE__->numSsps; lane < DSC_CICD_PG_SSPS; ++lane)
                dsc_cicd_restore_fifo(&banks[bank][lane], &pre[bank][lane]);
    }
    for (int bank = 0; bank < 3; ++bank)
        for (int lane = 0; lane < DSC_CICD_PG_SSPS; ++lane) {
            dsc_cicd_free_fifo_snapshot(&pre[bank][lane]);
            dsc_cicd_free_fifo_snapshot(&oracle[bank][lane]);
        }
    free(pre_frame);
    free(oracle_frame);
}

void __FUNCTION__(__CALLER_DECLARATIONS__) {
    dsc_cicd_invoke(__ALIAS_CALL__);
}
'''
    overlay_text = (
        overlay_template
        .replace("__ORIGINAL__", original)
        .replace("__FUNCTION__", function_name)
        .replace("__CALLER_DECLARATIONS__", caller_declarations)
        .replace("__ALIAS_CALL__", alias_call)
        .replace("__CFG__", config_parameter)
        .replace("__STATE__", state_parameter)
        .replace("__BUFFER__", buffer_parameter)
        .replace("__METRICS__", agent.overlay_runtime_metrics_source())
    )
    overlay = source_dir / "dsc_cicd_overlay.c"
    overlay.write_text(overlay_text, encoding="utf-8")

    bridge_template = r'''#include <cstdint>
#include <cstring>
#include "verilated.h"
#include "dsc_cicd_rtl_abi.h"
#include "V__MODULE__.h"
double sc_time_stamp() { return 0.0; }

extern "C" void dsc_cicd_rtl(
    dsc_cicd_pg_input_t *input, dsc_cicd_pg_output_t *output
) {
    V__MODULE__ dut;
    std::memset(output, 0, sizeof(*output));
    dut.clk = 0;
    dut.rst_n = 0;
    dut.start = 0;
    dut.is_encoder = input->is_encoder;
    dut.num_ssps = input->num_ssps;
    dut.mux_word_size = input->mux_word_size;
    dut.frame_capacity_bits = input->frame_capacity_bits;
    dut.post_mux_num_bits_in = input->post_mux_num_bits;
    for (int lane = 0; lane < DSC_CICD_PG_SSPS; ++lane) {
        dut.max_se_size[lane] = input->max_se_size[lane];
#define DSC_CICD_SET_FIFO(prefix, member) \
        dut.prefix##_size_bits_in[lane] = input->member[lane].size_bits; \
        dut.prefix##_fullness_in[lane] = input->member[lane].fullness; \
        dut.prefix##_read_ptr_in[lane] = input->member[lane].read_ptr; \
        dut.prefix##_write_ptr_in[lane] = input->member[lane].write_ptr; \
        dut.prefix##_max_fullness_in[lane] = input->member[lane].max_fullness; \
        dut.prefix##_byte_ctr_in[lane] = input->member[lane].byte_ctr
        DSC_CICD_SET_FIFO(enc_balance, enc_balance);
        DSC_CICD_SET_FIFO(shifter, shifter);
        DSC_CICD_SET_FIFO(se_size, se_size);
#undef DSC_CICD_SET_FIFO
    }
    dut.enc_balance_mem_read_valid = 0;
    dut.shifter_mem_read_valid = 0;
    dut.se_size_mem_read_valid = 0;
    dut.enc_balance_mem_write_ready = 0;
    dut.shifter_mem_write_ready = 0;
    dut.se_size_mem_write_ready = 0;
    dut.frame_mem_write_ready = 0;
    for (int lane = 0; lane < DSC_CICD_PG_SSPS; ++lane) {
        dut.enc_balance_mem_read_data[lane] = 0;
        dut.shifter_mem_read_data[lane] = 0;
        dut.se_size_mem_read_data[lane] = 0;
    }
    dut.eval();
    dut.clk = 1;
    dut.eval();
    dut.clk = 0;
    dut.rst_n = 1;
    dut.eval();

    auto service_low_phase = [&]() {
        dut.clk = 0;
        dut.enc_balance_mem_read_valid = 0;
        dut.shifter_mem_read_valid = 0;
        dut.se_size_mem_read_valid = 0;
        dut.enc_balance_mem_write_ready = 0;
        dut.shifter_mem_write_ready = 0;
        dut.se_size_mem_write_ready = 0;
        dut.frame_mem_write_ready = 0;
        dut.eval();
        uint8_t enc_read_valid = 0;
        uint8_t shifter_read_valid = 0;
        uint8_t se_read_valid = 0;
        uint8_t enc_write_ready = 0;
        uint8_t shifter_write_ready = 0;
        uint8_t se_write_ready = 0;
        for (int lane = 0; lane < DSC_CICD_PG_SSPS; ++lane) {
            auto service_read = [&](uint32_t requests, auto &addresses, auto &read_data,
                                    dsc_cicd_pg_fifo_t &fifo, uint8_t &valid) {
                if (!(requests & (1u << lane))) return;
                if (lane >= static_cast<int>(input->num_ssps)) {
                    ++output->bridge_error;
                    valid |= static_cast<uint8_t>(1u << lane);
                    read_data[lane] = 0;
                    return;
                }
                uint32_t address = static_cast<uint32_t>(addresses[lane]);
                uint64_t bytes = static_cast<uint64_t>(fifo.size_bits) / 8u;
                if (!fifo.data || address >= bytes) {
                    ++output->bridge_error;
                    read_data[lane] = 0;
                } else {
                    read_data[lane] = fifo.data[address];
                }
                valid |= static_cast<uint8_t>(1u << lane);
            };
            service_read(dut.enc_balance_mem_read_req, dut.enc_balance_mem_read_addr,
                         dut.enc_balance_mem_read_data, input->enc_balance[lane], enc_read_valid);
            service_read(dut.shifter_mem_read_req, dut.shifter_mem_read_addr,
                         dut.shifter_mem_read_data, input->shifter[lane], shifter_read_valid);
            service_read(dut.se_size_mem_read_req, dut.se_size_mem_read_addr,
                         dut.se_size_mem_read_data, input->se_size[lane], se_read_valid);

            auto service_write = [&](uint32_t requests, auto &addresses, auto &write_data,
                                     auto &write_mask, dsc_cicd_pg_fifo_t &fifo,
                                     uint8_t &ready) {
                if (!(requests & (1u << lane))) return;
                if (lane >= static_cast<int>(input->num_ssps)) {
                    ++output->bridge_error;
                    ready |= static_cast<uint8_t>(1u << lane);
                    return;
                }
                uint32_t address = static_cast<uint32_t>(addresses[lane]);
                uint64_t bytes = static_cast<uint64_t>(fifo.size_bits) / 8u;
                if (!fifo.data || address >= bytes) {
                    ++output->bridge_error;
                } else {
                    uint8_t mask = static_cast<uint8_t>(write_mask[lane]);
                    uint8_t value = static_cast<uint8_t>(write_data[lane]);
                    fifo.data[address] = static_cast<uint8_t>(
                        (fifo.data[address] & static_cast<uint8_t>(~mask)) |
                        (value & mask));
                }
                ready |= static_cast<uint8_t>(1u << lane);
            };
            service_write(dut.enc_balance_mem_write_req, dut.enc_balance_mem_write_addr,
                          dut.enc_balance_mem_write_data, dut.enc_balance_mem_write_bit_mask,
                          input->enc_balance[lane], enc_write_ready);
            service_write(dut.shifter_mem_write_req, dut.shifter_mem_write_addr,
                          dut.shifter_mem_write_data, dut.shifter_mem_write_bit_mask,
                          input->shifter[lane], shifter_write_ready);
            service_write(dut.se_size_mem_write_req, dut.se_size_mem_write_addr,
                          dut.se_size_mem_write_data, dut.se_size_mem_write_bit_mask,
                          input->se_size[lane], se_write_ready);
        }
        if (dut.frame_mem_write_req) {
            uint64_t address = static_cast<uint64_t>(dut.frame_mem_write_addr);
            uint64_t bytes = (static_cast<uint64_t>(input->frame_capacity_bits) + 7u) / 8u;
            if (!input->frame_data || address >= bytes) {
                ++output->bridge_error;
            } else {
                uint8_t mask = static_cast<uint8_t>(dut.frame_mem_write_bit_mask);
                uint8_t value = static_cast<uint8_t>(dut.frame_mem_write_data);
                /*
                 * putbits() clears a byte only when it starts that byte.  For
                 * a partial-byte write, a zero source bit is a no-op; it does
                 * not clear a pre-existing destination bit.  FIFO writes are
                 * different and retain the per-bit RMW below.
                 */
                if (mask == 0xffu)
                    input->frame_data[address] = static_cast<uint8_t>(value & mask);
                else if (value & mask)
                    input->frame_data[address] = static_cast<uint8_t>(
                        input->frame_data[address] | (value & mask));
            }
            dut.frame_mem_write_ready = 1;
        }
        dut.enc_balance_mem_read_valid = enc_read_valid;
        dut.shifter_mem_read_valid = shifter_read_valid;
        dut.se_size_mem_read_valid = se_read_valid;
        dut.enc_balance_mem_write_ready = enc_write_ready;
        dut.shifter_mem_write_ready = shifter_write_ready;
        dut.se_size_mem_write_ready = se_write_ready;
        dut.eval();
    };

    auto tick = [&]() {
        service_low_phase();
        dut.clk = 1;
        dut.eval();
        ++output->cycles;
    };
    dut.start = 1;
    tick();
    dut.start = 0;
    for (uint32_t cycle = 0; cycle < DSC_CICD_PG_MAX_CYCLES && !dut.done; ++cycle)
        tick();
    if (!dut.done) ++output->bridge_error;

    output->post_mux_num_bits = dut.post_mux_num_bits_out;
    output->illegal_domain = dut.illegal_domain;
    output->fifo_underflow = dut.fifo_underflow;
    output->fifo_overflow = dut.fifo_overflow;
    output->frame_overflow = dut.frame_overflow;
    output->se_size_overflow = dut.se_size_overflow;
    for (int lane = 0; lane < DSC_CICD_PG_SSPS; ++lane) {
#define DSC_CICD_GET_FIFO(prefix, member) \
        output->member[lane].data = input->member[lane].data; \
        output->member[lane].size_bits = dut.prefix##_size_bits_out[lane]; \
        output->member[lane].fullness = dut.prefix##_fullness_out[lane]; \
        output->member[lane].read_ptr = dut.prefix##_read_ptr_out[lane]; \
        output->member[lane].write_ptr = dut.prefix##_write_ptr_out[lane]; \
        output->member[lane].max_fullness = dut.prefix##_max_fullness_out[lane]; \
        output->member[lane].byte_ctr = dut.prefix##_byte_ctr_out[lane]
        DSC_CICD_GET_FIFO(enc_balance, enc_balance);
        DSC_CICD_GET_FIFO(shifter, shifter);
        DSC_CICD_GET_FIFO(se_size, se_size);
#undef DSC_CICD_GET_FIFO
    }
}
'''
    safe_module = _identifier(module)
    bridge = source_dir / "rtl_bridge.cpp"
    bridge.write_text(
        bridge_template.replace("__MODULE__", safe_module), encoding="utf-8"
    )

    main = source_dir / "dsc_cicd_main.c"
    main.write_text(
        "#include <stdio.h>\nextern int dsc_cicd_original_main(int, char **);\n"
        "int main(int argc, char **argv) { return dsc_cicd_original_main(argc, argv); }\n",
        encoding="utf-8",
    )
    input_port_names = [
        str(item.get("name")) for item in ports
        if item.get("direction") == "input"
    ]

    def input_binding(name: str) -> str:
        if name in {"clk", "rst_n", "start"}:
            return f"Verilator bridge control::{name}"
        if name == "is_encoder":
            return f"{state_parameter}->isEncoder"
        if name == "num_ssps":
            return f"{state_parameter}->numSsps"
        if name == "mux_word_size":
            return f"{config_parameter}->mux_word_size"
        if name == "max_se_size":
            return f"{state_parameter}->maxSeSize[0..3]"
        if name == "frame_capacity_bits":
            return "bounded frame cursor plus maximum mux output"
        if name == "post_mux_num_bits_in":
            return f"{state_parameter}->postMuxNumBits"
        for prefix, field in (
            ("enc_balance_", "encBalanceFifo"),
            ("shifter_", "shifter"),
            ("se_size_", "seSizeFifo"),
        ):
            if name.startswith(prefix):
                if "_mem_" in name:
                    return f"bridge services {state_parameter}->{field}[0..3]::{name}"
                return f"{state_parameter}->{field}[0..3]::{name}"
        if name.startswith("frame_mem_"):
            return f"bridge services {buffer_parameter}::{name}"
        return f"frozen contract binding::{name}"

    return {
        "header": header,
        "abi": abi,
        "overlay": overlay,
        "bridge": bridge,
        "main": main,
        "candidate": candidate_sv,
        "composition": {
            "status": "PASS",
            "adapter_kind": "explicit_bounded_process_group_encode_transition",
            "caller_parameter_count": len(parameters),
            "rtl_input_count": len(input_port_names),
            "frozen_input_ports": input_port_names,
            "rtl_bindings": [input_binding(name) for name in input_port_names],
            "state_outputs": sorted(
                str(item.get("name")) for item in ports
                if item.get("direction") == "output"
            ),
            "c_oracle_uses_deep_fifo_and_frame_snapshots": True,
            "c_oracle_state_is_restored_before_rtl": True,
            "rtl_services_external_fifo_and_frame_memory_requests": True,
            "rtl_return_commits_only_rtl_fifo_frame_and_cursor_state": True,
            "all_fifo_scalar_and_active_memory_bytes_compared": True,
            "inactive_ssp_scalar_state_is_passthrough_checked": True,
            "inactive_ssp_memory_requests_are_guarded": True,
            "frame_zero_bits_match_putbits_partial_byte_semantics": True,
            "candidate_hash_and_module_are_pinned": True,
            "rtl_port_shapes_are_pinned_for_verilator_arrays": True,
            "bridge_cycle_bound": _PG_MAX_CYCLES,
            "source_order_is_clocked_and_bounded": True,
            "residual_symbol_alias_routes_to_dispatcher": True,
        },
    }
