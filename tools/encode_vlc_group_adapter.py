"""Adapter emitter for the externally composed Encode ``VLCGroup`` FSM.

The parent candidate deliberately stops at the VLCUnit and ProcessGroupEnc
boundaries.  This emitter keeps those boundaries semantic: the generated C
overlay calls the pinned C symbols and the integration rewriter can route
those calls through the selected child dispatchers.  The C implementation is
also the oracle.  It is run against a private deep copy, the caller is
restored, and only then is the sequential Verilator model run.

This module is intentionally independent of the large CI/CD agent dispatch
table.  It is imported directly by source-generation tests and by callers
which already know that the contract is the VLCGroup candidate.
"""

from __future__ import annotations

import hashlib
import pathlib
import re
from typing import Any


_IDENTIFIER = re.compile(r"^[A-Za-z_][A-Za-z0-9_]*$")
_HASH = re.compile(r"^[0-9a-fA-F]{64}$")
_MAX_SSPS = 4
_MAX_UNITS = 4
_MAX_SE_SIZE = 68
_MAX_CYCLES = 4096
_BANKS = ("enc_balance", "shifter", "se_size")
_FIFO_FIELDS = (
    "size_bits",
    "fullness",
    "read_ptr",
    "write_ptr",
    "max_fullness",
    "byte_ctr",
)


def _safe_identifier(value: str) -> str:
    result = re.sub(r"[^A-Za-z0-9_]", "_", str(value))
    if not result or result[0].isdigit():
        result = "c_" + result
    return result


def _path_hash(path: pathlib.Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def _resolve_reference(agent: Any, root: pathlib.Path, value: str) -> pathlib.Path:
    resolver = getattr(agent, "resolve_artifact_reference", None)
    if callable(resolver):
        return pathlib.Path(resolver(value))
    path = pathlib.Path(value)
    return path if path.is_absolute() else root / path


def _parameters(agent: Any, contract: dict[str, Any]) -> list[dict[str, Any]]:
    direct = (contract.get("function", {}) or {}).get("parameters")
    if isinstance(direct, list) and direct:
        return [dict(item) for item in direct]
    getter = getattr(agent, "function_parameters", None)
    if callable(getter):
        value = getter(contract)
        if isinstance(value, list):
            return [dict(item) for item in value]
    return []


def _parameter_declaration(parameter: dict[str, Any]) -> str:
    return (
        f"{str(parameter.get('type', 'int')).strip()} "
        f"{str(parameter.get('name', '')).strip()}"
    )


def _validate_dependency(
    agent: Any,
    dependency: dict[str, Any],
    source_dir: pathlib.Path,
    expected_role: str,
    expected_kind: str,
) -> dict[str, Any]:
    if dependency.get("role") != expected_role:
        raise RuntimeError(f"VLCGroup child role {expected_role} is not pinned")
    if dependency.get("semantic_kind") != expected_kind:
        raise RuntimeError(f"VLCGroup {expected_role} semantic kind changed")
    child_composition = dependency.get("composition", {}) or {}
    if (
        child_composition.get("status") != "EXTERNALIZED_CHILD_BOUNDARY"
        or child_composition.get("module_embedded_in_parent") is not False
        or child_composition.get("state_and_memory_adapter_required") is not True
    ):
        raise RuntimeError(f"VLCGroup {expected_role} boundary is not externalized")
    for key in ("contract_sha256", "module_sha256"):
        if not _HASH.fullmatch(str(dependency.get(key, ""))):
            raise RuntimeError(f"VLCGroup child {key} is not hash pinned")
    function = dependency.get("function", {}) or {}
    if isinstance(function, str):
        function_name = function
        child_parameters: list[dict[str, Any]] = []
        return_type = "void"
    else:
        function_name = str(function.get("name", ""))
        child_parameters = [dict(item) for item in function.get("parameters", [])]
        return_type = str(function.get("return_type", "void"))
    if not _IDENTIFIER.fullmatch(function_name):
        raise RuntimeError(f"VLCGroup {expected_role} function identity is invalid")
    module = str(dependency.get("module", ""))
    if not _IDENTIFIER.fullmatch(module):
        raise RuntimeError(f"VLCGroup {expected_role} module identity is invalid")
    if not child_parameters:
        raise RuntimeError(f"VLCGroup {expected_role} parameter ABI is missing")

    root_value = getattr(agent, "root", None)
    root = pathlib.Path(root_value) if root_value else source_dir.parent
    contract_path = _resolve_reference(
        agent, root, str(dependency.get("contract_file", ""))
    )
    module_path = _resolve_reference(
        agent, root, str(dependency.get("module_file", ""))
    )
    # A contract may pin an artifact outside a source-generation fixture.  A
    # present artifact is checked; the 64-byte pin remains mandatory either
    # way.
    if contract_path.is_file() and _path_hash(contract_path) != str(
        dependency["contract_sha256"]
    ).lower():
        raise RuntimeError(f"VLCGroup {expected_role} contract hash changed")
    if module_path.is_file():
        if _path_hash(module_path) != str(dependency["module_sha256"]).lower():
            raise RuntimeError(f"VLCGroup {expected_role} module hash changed")
        module_text = module_path.read_text(encoding="utf-8", errors="replace")
        if not re.search(rf"\bmodule\s+{re.escape(module)}\b", module_text):
            raise RuntimeError(f"VLCGroup {expected_role} module identity changed")
    return {
        "role": expected_role,
        "function": function_name,
        "return_type": return_type,
        "parameters": child_parameters,
        "module": module,
        "contract_id": str(dependency.get("contract_id", "")),
        "contract_sha256": str(dependency["contract_sha256"]).lower(),
        "module_sha256": str(dependency["module_sha256"]).lower(),
    }


def _required_ports() -> set[str]:
    required = {
        "clk",
        "rst_n",
        "start",
        "is_encoder",
        "units_per_group",
        "num_ssps",
        "mux_word_size",
        "bits_per_pixel",
        "bits_per_component",
        "chunk_size",
        "initial_xmit_delay",
        "vbr_enable",
        "rcb_bits",
        "frame_capacity_bits",
        "max_se_size",
        "busy",
        "done",
        "domain_valid",
        "illegal_domain",
        "fatal_error",
        "bound_violation",
        "child_error",
        "fifo_underflow",
        "fifo_overflow",
        "se_size_overflow",
        "buffer_overflow",
        "post_mux_num_bits_in",
        "post_mux_num_bits_out",
    }
    parent_scalars = (
        "num_bits",
        "buffer_fullness",
        "num_bits_chunk",
        "pixels_in_group",
        "slice_width",
        "pixel_count",
        "group_count",
        "primary_qp",
        "prev_primary_qp",
        "prev_num_bits",
        "coded_group_size",
        "group_count_line",
        "force_mpp",
    )
    for name in parent_scalars:
        required.update({f"{name}_in", f"{name}_out"})
    required.update(
        {
            "midpoint_selected_in",
            "midpoint_selected_out",
            "quantized_residual_in",
            "quantized_residual_out",
            "quantized_residual_mid_in",
            "quantized_residual_mid_out",
        }
    )
    for prefix in _BANKS:
        for field in _FIFO_FIELDS:
            required.update({f"{prefix}_{field}_in", f"{prefix}_{field}_out"})
        required.update(
            {
                f"{prefix}_mem_read_req",
                f"{prefix}_mem_read_addr",
                f"{prefix}_mem_read_valid",
                f"{prefix}_mem_read_data",
                f"{prefix}_mem_write_req",
                f"{prefix}_mem_write_addr",
                f"{prefix}_mem_write_ready",
                f"{prefix}_mem_write_data",
                f"{prefix}_mem_write_bit_mask",
            }
        )
    required.update(
        {
            "vlc_unit_start",
            "vlc_unit_ready",
            "vlc_unit_done",
            "vlc_unit_domain_valid",
            "vlc_unit_fatal_error",
            "vlc_unit_index",
            "vlc_unit_force_p1_ich2",
            "vlc_unit_num_bits_in",
            "vlc_unit_num_bits_out",
            "vlc_unit_primary_qp_in",
            "vlc_unit_primary_qp_out",
        }
    )
    for field in _FIFO_FIELDS:
        required.update(
            {
                f"vlc_unit_enc_balance_{field}_in",
                f"vlc_unit_enc_balance_{field}_out",
            }
        )
    for prefix in ("vlc_unit_shifter", "vlc_unit_se_size"):
        for field in _FIFO_FIELDS:
            required.add(f"{prefix}_{field}_in")
    for prefix in _BANKS:
        for suffix in (
            "mem_read_req",
            "mem_read_addr",
            "mem_read_valid",
            "mem_read_data",
            "mem_write_req",
            "mem_write_addr",
            "mem_write_ready",
            "mem_write_data",
            "mem_write_bit_mask",
        ):
            required.add(f"vlc_unit_{prefix}_{suffix}")
    required.update(
        {
            "process_group_start",
            "process_group_ready",
            "process_group_done",
            "process_group_domain_valid",
            "process_group_fatal_error",
            "process_group_is_encoder",
            "process_group_num_ssps",
            "process_group_mux_word_size",
            "process_group_frame_capacity_bits",
            "process_group_post_mux_num_bits_in",
            "process_group_post_mux_num_bits_out",
            "frame_mem_write_req",
            "frame_mem_write_addr",
            "frame_mem_write_ready",
            "frame_mem_write_data",
            "frame_mem_write_bit_mask",
        }
    )
    for prefix in _BANKS:
        for field in _FIFO_FIELDS:
            required.update(
                {
                    f"process_group_{prefix}_{field}_in",
                    f"process_group_{prefix}_{field}_out",
                }
            )
        required.update(
            {
                f"process_group_{prefix}_mem_read_req",
                f"process_group_{prefix}_mem_read_addr",
                f"process_group_{prefix}_mem_read_valid",
                f"process_group_{prefix}_mem_read_data",
                f"process_group_{prefix}_mem_write_req",
                f"process_group_{prefix}_mem_write_addr",
                f"process_group_{prefix}_mem_write_ready",
                f"process_group_{prefix}_mem_write_data",
                f"process_group_{prefix}_mem_write_bit_mask",
            }
        )
    return required


def _child_declaration(child: dict[str, Any]) -> str:
    parameters = ", ".join(_parameter_declaration(item) for item in child["parameters"])
    return f"extern {child['return_type']} {child['function']}({parameters});"


def _metrics_source(agent: Any) -> str:
    getter = getattr(agent, "overlay_runtime_metrics_source", None)
    if callable(getter):
        return str(getter())
    return """\
static unsigned long dsc_cicd_mismatches;
static unsigned long dsc_cicd_calls;
static unsigned long dsc_cicd_rtl_invocations;
static int dsc_cicd_report_registered;
static void dsc_cicd_report(void) {
    fprintf(stderr, "DSC_CICD_OVERLAY_METRICS calls=%lu rtl_invocations=%lu mismatches=%lu\\n",
            dsc_cicd_calls, dsc_cicd_rtl_invocations, dsc_cicd_mismatches);
}
static void dsc_cicd_note_call(int mode) {
    if (!dsc_cicd_report_registered) {
        atexit(dsc_cicd_report);
        dsc_cicd_report_registered = 1;
    }
    ++dsc_cicd_calls;
    if (mode != 0) ++dsc_cicd_rtl_invocations;
}
"""


def _abi_source() -> str:
    return r'''#ifndef DSC_CICD_RTL_ABI_H
#define DSC_CICD_RTL_ABI_H
#include <stdint.h>
#include "dsc_types.h"

#define DSC_CICD_VLC_GROUP_MAX_SSPS 4
#define DSC_CICD_VLC_GROUP_MAX_UNITS 4
#define DSC_CICD_VLC_GROUP_MAX_SE_SIZE 68
#define DSC_CICD_VLC_GROUP_MAX_EVENTS 256
#define DSC_CICD_VLC_GROUP_MAX_CYCLES 4096

typedef struct {
    uint8_t *data;
    uint32_t size_bits;
    uint32_t fullness;
    uint32_t read_ptr;
    uint32_t write_ptr;
    uint32_t max_fullness;
    uint32_t byte_ctr;
} dsc_cicd_vlc_group_fifo_t;

typedef struct {
    dsc_cfg_t *cfg;
    dsc_state_t *state;
    unsigned char **byte_out_p;
    int32_t force_p1_ich2;
    uint32_t vlc_unit_calls;
    uint32_t process_group_calls;
    uint32_t se_size_write_events;
    uint32_t frame_write_events;
    uint32_t event_count;
    uint8_t event_kind[DSC_CICD_VLC_GROUP_MAX_EVENTS];
    uint32_t event_arg[DSC_CICD_VLC_GROUP_MAX_EVENTS];
    uint32_t event_addr[DSC_CICD_VLC_GROUP_MAX_EVENTS];
    uint32_t event_data[DSC_CICD_VLC_GROUP_MAX_EVENTS];
    uint32_t event_mask[DSC_CICD_VLC_GROUP_MAX_EVENTS];
    uint8_t *frame_observe;
    uint32_t frame_observe_bytes;
    int32_t force_metadata_mismatch;
    int32_t child_domain_valid;
    int32_t child_fatal_error;
} dsc_cicd_vlc_group_context_t;

typedef struct {
    int32_t is_encoder;
    uint32_t units_per_group;
    uint32_t num_ssps;
    uint32_t mux_word_size;
    int32_t bits_per_pixel;
    int32_t bits_per_component;
    int32_t chunk_size;
    int32_t initial_xmit_delay;
    int32_t vbr_enable;
    int32_t rcb_bits;
    uint32_t frame_capacity_bits;
    uint32_t max_se_size[DSC_CICD_VLC_GROUP_MAX_SSPS];
    uint32_t post_mux_num_bits;
    int32_t num_bits;
    int32_t buffer_fullness;
    int32_t num_bits_chunk;
    int32_t pixels_in_group;
    int32_t slice_width;
    int32_t pixel_count;
    int32_t group_count;
    int32_t primary_qp;
    int32_t prev_primary_qp;
    int32_t prev_num_bits;
    int32_t coded_group_size;
    int32_t group_count_line;
    int32_t force_mpp;
    int32_t midpoint_selected[DSC_CICD_VLC_GROUP_MAX_UNITS];
    int32_t quantized_residual[DSC_CICD_VLC_GROUP_MAX_UNITS][3];
    int32_t quantized_residual_mid[DSC_CICD_VLC_GROUP_MAX_UNITS][3];
    dsc_cicd_vlc_group_fifo_t enc_balance[DSC_CICD_VLC_GROUP_MAX_SSPS];
    dsc_cicd_vlc_group_fifo_t shifter[DSC_CICD_VLC_GROUP_MAX_SSPS];
    dsc_cicd_vlc_group_fifo_t se_size[DSC_CICD_VLC_GROUP_MAX_SSPS];
    uint8_t *frame_data;
} dsc_cicd_vlc_group_input_t;

typedef struct {
    uint32_t post_mux_num_bits;
    int32_t num_bits;
    int32_t buffer_fullness;
    int32_t num_bits_chunk;
    int32_t pixels_in_group;
    int32_t slice_width;
    int32_t pixel_count;
    int32_t group_count;
    int32_t primary_qp;
    int32_t prev_primary_qp;
    int32_t prev_num_bits;
    int32_t coded_group_size;
    int32_t group_count_line;
    int32_t force_mpp;
    int32_t midpoint_selected[DSC_CICD_VLC_GROUP_MAX_UNITS];
    int32_t quantized_residual[DSC_CICD_VLC_GROUP_MAX_UNITS][3];
    int32_t quantized_residual_mid[DSC_CICD_VLC_GROUP_MAX_UNITS][3];
    dsc_cicd_vlc_group_fifo_t enc_balance[DSC_CICD_VLC_GROUP_MAX_SSPS];
    dsc_cicd_vlc_group_fifo_t shifter[DSC_CICD_VLC_GROUP_MAX_SSPS];
    dsc_cicd_vlc_group_fifo_t se_size[DSC_CICD_VLC_GROUP_MAX_SSPS];
    int32_t busy;
    int32_t done;
    int32_t domain_valid;
    int32_t illegal_domain;
    int32_t fatal_error;
    int32_t bound_violation;
    int32_t child_error;
    int32_t fifo_underflow;
    int32_t fifo_overflow;
    int32_t se_size_overflow;
    int32_t buffer_overflow;
    uint32_t cycles;
    uint32_t vlc_unit_calls;
    uint32_t process_group_calls;
    uint32_t se_size_write_events;
    uint32_t frame_write_events;
    uint32_t event_count;
    uint8_t event_kind[DSC_CICD_VLC_GROUP_MAX_EVENTS];
    uint32_t event_arg[DSC_CICD_VLC_GROUP_MAX_EVENTS];
    uint32_t event_addr[DSC_CICD_VLC_GROUP_MAX_EVENTS];
    uint32_t event_data[DSC_CICD_VLC_GROUP_MAX_EVENTS];
    uint32_t event_mask[DSC_CICD_VLC_GROUP_MAX_EVENTS];
} dsc_cicd_vlc_group_output_t;

#ifdef __cplusplus
extern "C" {
#endif
void dsc_cicd_vlc_group_service_vlc_unit(
    dsc_cicd_vlc_group_context_t *context, int unit, int force_p1_ich2);
void dsc_cicd_vlc_group_service_process_group(
    dsc_cicd_vlc_group_context_t *context);
void dsc_cicd_rtl(
    dsc_cicd_vlc_group_input_t *input,
    dsc_cicd_vlc_group_output_t *output,
    dsc_cicd_vlc_group_context_t *context);
#ifdef __cplusplus
}
#endif
#endif
'''


def _header_source(caller_declarations: str) -> str:
    return (
        "#ifndef DSC_CICD_OVERLAY_H\n"
        "#define DSC_CICD_OVERLAY_H\n"
        "#include \"dsc_types.h\"\n"
        "#include \"dsc_cicd_rtl_abi.h\"\n"
        "#ifdef __cplusplus\nextern \"C\" {\n#endif\n"
        f"void dsc_cicd_invoke({caller_declarations});\n"
        "#ifdef __cplusplus\n}\n#endif\n"
        "#endif\n"
    )


def _overlay_source(
    *,
    original: str,
    caller_declarations: str,
    alias_call: str,
    cfg_name: str,
    state_name: str,
    byte_name: str,
    force_name: str,
    children: dict[str, dict[str, Any]],
    metrics: str,
) -> str:
    vlc = children["vlc_unit"]
    process = children["process_group"]
    vlc_args = ", ".join(
        [
            "context->cfg",
            "context->state",
            "unit",
            "context->state->quantizedResidual[unit]",
            "force_p1_ich2",
        ]
    )
    process_args = "context->cfg, context->state, *context->byte_out_p"
    return f'''#include <stdint.h>
#include <stddef.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include "dsc_cicd_overlay.h"

extern void {original}({caller_declarations});
{_child_declaration(vlc)}
{_child_declaration(process)}

static int dsc_cicd_mode(void) {{
    const char *value = getenv("DSC_CICD_MODE");
    if (value && strcmp(value, "SHADOW") == 0) return 1;
    if (value && strcmp(value, "RTL_RETURN") == 0) return 2;
    return 0;
}}
{metrics}

/* The parent child boundary is semantic and intentionally remains visible to
 * the source rewriter.  A composed run replaces these two calls with the
 * selected child dispatchers; a private C oracle runs them in C_ONLY scope. */
void dsc_cicd_vlc_group_service_vlc_unit(
    dsc_cicd_vlc_group_context_t *context, int unit, int force_p1_ich2) {{
    if (!context || !context->cfg || !context->state ||
        unit < 0 || unit >= DSC_CICD_VLC_GROUP_MAX_UNITS) {{
        if (context) context->child_fatal_error = 1;
        return;
    }}
    VLCUnit({vlc_args});
    ++context->vlc_unit_calls;
    if (context->event_count < DSC_CICD_VLC_GROUP_MAX_EVENTS) {{
        uint32_t index = context->event_count++;
        context->event_kind[index] = 0;
        context->event_arg[index] = (uint32_t)unit;
        context->event_addr[index] = 0;
        context->event_data[index] = (uint32_t)force_p1_ich2;
        context->event_mask[index] = 0;
    }}
}}

void dsc_cicd_vlc_group_service_process_group(
    dsc_cicd_vlc_group_context_t *context) {{
    if (!context || !context->cfg || !context->state ||
        !context->byte_out_p || !*context->byte_out_p) {{
        if (context) context->child_fatal_error = 1;
        return;
    }}
    ProcessGroupEnc({process_args});
    ++context->process_group_calls;
    if (context->event_count < DSC_CICD_VLC_GROUP_MAX_EVENTS) {{
        uint32_t index = context->event_count++;
        context->event_kind[index] = 2;
        context->event_arg[index] = 0;
        context->event_addr[index] = 0;
        context->event_data[index] = 0;
        context->event_mask[index] = 0;
    }}
}}

typedef struct {{
    dsc_state_t state;
    unsigned char *fifo_bytes[3][DSC_CICD_VLC_GROUP_MAX_SSPS];
    PRED_TYPE *prev_line_pred;
    int *prev_line[NUM_COMPONENTS + 1];
    int *curr_line[NUM_COMPONENTS];
    int *orig_line[NUM_COMPONENTS];
    unsigned int *history_pixels[NUM_COMPONENTS];
    int *history_valid;
    int *chunk_sizes;
    unsigned char *frame_data;
    unsigned char *external_base;
    unsigned char *byte_cursor;
    size_t frame_bytes;
    size_t chunk_bytes;
}} dsc_cicd_vlc_group_snapshot_t;

static void *dsc_cicd_alloc_copy(const void *source, size_t bytes) {{
    if (!source || !bytes) return NULL;
    void *copy = malloc(bytes);
    if (!copy) {{ fprintf(stderr, "VLCGroup snapshot allocation failed\\n"); exit(2); }}
    memcpy(copy, source, bytes);
    return copy;
}}

static size_t dsc_cicd_line_count(const dsc_state_t *state) {{
    return state && state->sliceWidth > 0
        ? (size_t)state->sliceWidth + PADDING_LEFT + PADDING_RIGHT : 1u;
}}

static size_t dsc_cicd_pred_count(const dsc_state_t *state) {{
    return state && state->sliceWidth > 0
        ? ((size_t)state->sliceWidth + PRED_BLK_SIZE - 1u) / PRED_BLK_SIZE : 1u;
}}

static void dsc_cicd_snapshot_destroy(dsc_cicd_vlc_group_snapshot_t *snapshot) {{
    if (!snapshot) return;
    for (int bank = 0; bank < 3; ++bank)
        for (int lane = 0; lane < DSC_CICD_VLC_GROUP_MAX_SSPS; ++lane)
            free(snapshot->fifo_bytes[bank][lane]);
    free(snapshot->prev_line_pred);
    for (int lane = 0; lane < NUM_COMPONENTS + 1; ++lane) free(snapshot->prev_line[lane]);
    for (int lane = 0; lane < NUM_COMPONENTS; ++lane) {{
        free(snapshot->curr_line[lane]);
        free(snapshot->orig_line[lane]);
        free(snapshot->history_pixels[lane]);
    }}
    free(snapshot->history_valid);
    free(snapshot->chunk_sizes);
    free(snapshot->frame_data);
    memset(snapshot, 0, sizeof(*snapshot));
}}

static int dsc_cicd_snapshot_capture(
    dsc_cicd_vlc_group_snapshot_t *snapshot,
    const dsc_state_t *source,
    unsigned char *external_base,
    size_t frame_bytes,
    const dsc_cfg_t *cfg) {{
    memset(snapshot, 0, sizeof(*snapshot));
    if (!source || !external_base || !frame_bytes) return 0;
    snapshot->state = *source;
    snapshot->external_base = external_base;
    snapshot->frame_bytes = frame_bytes;
    snapshot->chunk_bytes = cfg && cfg->slice_height > 0
        ? (size_t)cfg->slice_height * sizeof(int) : 0u;
    snapshot->frame_data = (unsigned char *)dsc_cicd_alloc_copy(
        external_base, frame_bytes);
    snapshot->byte_cursor = snapshot->frame_data;
    fifo_t *banks[3] = {{
        snapshot->state.encBalanceFifo,
        snapshot->state.shifter,
        snapshot->state.seSizeFifo
    }};
    const fifo_t *source_banks[3] = {{
        source->encBalanceFifo, source->shifter, source->seSizeFifo
    }};
    for (int bank = 0; bank < 3; ++bank) {{
        for (int lane = 0; lane < DSC_CICD_VLC_GROUP_MAX_SSPS; ++lane) {{
            if (!source_banks[bank][lane].data || source_banks[bank][lane].size <= 0 ||
                (source_banks[bank][lane].size & 7)) return 0;
            size_t bytes = (size_t)source_banks[bank][lane].size / 8u;
            snapshot->fifo_bytes[bank][lane] = (unsigned char *)dsc_cicd_alloc_copy(
                source_banks[bank][lane].data, bytes);
            banks[bank][lane].data = snapshot->fifo_bytes[bank][lane];
        }}
    }}
    if (source->prevLinePred) {{
        snapshot->prev_line_pred = (PRED_TYPE *)dsc_cicd_alloc_copy(
            source->prevLinePred, dsc_cicd_pred_count(source) * sizeof(PRED_TYPE));
        snapshot->state.prevLinePred = snapshot->prev_line_pred;
    }}
    size_t line_bytes = dsc_cicd_line_count(source) * sizeof(int);
    for (int lane = 0; lane < NUM_COMPONENTS + 1; ++lane) {{
        if (source->prevLine[lane]) {{
            snapshot->prev_line[lane] = (int *)dsc_cicd_alloc_copy(
                source->prevLine[lane], line_bytes);
            snapshot->state.prevLine[lane] = snapshot->prev_line[lane];
        }}
    }}
    for (int lane = 0; lane < NUM_COMPONENTS; ++lane) {{
        if (source->currLine[lane]) {{
            snapshot->curr_line[lane] = (int *)dsc_cicd_alloc_copy(
                source->currLine[lane], line_bytes);
            snapshot->state.currLine[lane] = snapshot->curr_line[lane];
        }}
        if (source->origLine[lane]) {{
            snapshot->orig_line[lane] = (int *)dsc_cicd_alloc_copy(
                source->origLine[lane], line_bytes);
            snapshot->state.origLine[lane] = snapshot->orig_line[lane];
        }}
        if (source->history.pixels[lane]) {{
            snapshot->history_pixels[lane] = (unsigned int *)dsc_cicd_alloc_copy(
                source->history.pixels[lane], ICH_SIZE * sizeof(unsigned int));
            snapshot->state.history.pixels[lane] = snapshot->history_pixels[lane];
        }}
    }}
    if (source->history.valid) {{
        snapshot->history_valid = (int *)dsc_cicd_alloc_copy(
            source->history.valid, ICH_SIZE * sizeof(int));
        snapshot->state.history.valid = snapshot->history_valid;
    }}
    if (source->chunkSizes && cfg && cfg->slice_height > 0) {{
        snapshot->chunk_sizes = (int *)dsc_cicd_alloc_copy(
            source->chunkSizes, (size_t)cfg->slice_height * sizeof(int));
        snapshot->state.chunkSizes = snapshot->chunk_sizes;
    }}
    return 1;
}}

static size_t dsc_cicd_cursor_offset(
    const dsc_cicd_vlc_group_snapshot_t *snapshot) {{
    if (!snapshot || !snapshot->frame_data || !snapshot->byte_cursor ||
        snapshot->byte_cursor < snapshot->frame_data ||
        snapshot->byte_cursor > snapshot->frame_data + snapshot->frame_bytes)
        return 0;
    return (size_t)(snapshot->byte_cursor - snapshot->frame_data);
}}

static int dsc_cicd_snapshot_clone(
    dsc_cicd_vlc_group_snapshot_t *destination,
    const dsc_cicd_vlc_group_snapshot_t *source,
    const dsc_cfg_t *cfg) {{
    size_t cursor = dsc_cicd_cursor_offset(source);
    if (!dsc_cicd_snapshot_capture(
            destination, &source->state, source->frame_data,
            source->frame_bytes, cfg)) return 0;
    destination->external_base = source->external_base;
    destination->byte_cursor = destination->frame_data +
        (cursor <= destination->frame_bytes ? cursor : 0u);
    return 1;
}}

static void dsc_cicd_restore_snapshot(
    dsc_state_t *target,
    unsigned char **byte_out_p,
    const dsc_cicd_vlc_group_snapshot_t *snapshot) {{
    dsc_state_t desired = snapshot->state;
    unsigned char *fifo_data[3][DSC_CICD_VLC_GROUP_MAX_SSPS];
    fifo_t *target_banks[3] = {{
        target->encBalanceFifo, target->shifter, target->seSizeFifo
    }};
    fifo_t *desired_banks[3] = {{
        desired.encBalanceFifo, desired.shifter, desired.seSizeFifo
    }};
    for (int bank = 0; bank < 3; ++bank)
        for (int lane = 0; lane < DSC_CICD_VLC_GROUP_MAX_SSPS; ++lane) {{
            fifo_data[bank][lane] = target_banks[bank][lane].data;
            desired_banks[bank][lane].data = fifo_data[bank][lane];
        }}
    PRED_TYPE *prev_line_pred = target->prevLinePred;
    int *prev_line[NUM_COMPONENTS + 1];
    int *curr_line[NUM_COMPONENTS];
    int *orig_line[NUM_COMPONENTS];
    unsigned int *history_pixels[NUM_COMPONENTS];
    for (int lane = 0; lane < NUM_COMPONENTS + 1; ++lane)
        prev_line[lane] = target->prevLine[lane];
    for (int lane = 0; lane < NUM_COMPONENTS; ++lane) {{
        curr_line[lane] = target->currLine[lane];
        orig_line[lane] = target->origLine[lane];
        history_pixels[lane] = target->history.pixels[lane];
    }}
    int *history_valid = target->history.valid;
    int *chunk_sizes = target->chunkSizes;
    desired.prevLinePred = prev_line_pred;
    desired.history.valid = history_valid;
    desired.chunkSizes = chunk_sizes;
    for (int lane = 0; lane < NUM_COMPONENTS + 1; ++lane)
        desired.prevLine[lane] = prev_line[lane];
    for (int lane = 0; lane < NUM_COMPONENTS; ++lane) {{
        desired.currLine[lane] = curr_line[lane];
        desired.origLine[lane] = orig_line[lane];
        desired.history.pixels[lane] = history_pixels[lane];
    }}
    *target = desired;
    for (int bank = 0; bank < 3; ++bank)
        for (int lane = 0; lane < DSC_CICD_VLC_GROUP_MAX_SSPS; ++lane) {{
            size_t bytes = (size_t)target_banks[bank][lane].size / 8u;
            memcpy(fifo_data[bank][lane], snapshot->fifo_bytes[bank][lane], bytes);
        }}
    if (prev_line_pred && snapshot->prev_line_pred)
        memcpy(prev_line_pred, snapshot->prev_line_pred,
               dsc_cicd_pred_count(target) * sizeof(PRED_TYPE));
    size_t line_bytes = dsc_cicd_line_count(target) * sizeof(int);
    for (int lane = 0; lane < NUM_COMPONENTS + 1; ++lane)
        if (prev_line[lane] && snapshot->prev_line[lane])
            memcpy(prev_line[lane], snapshot->prev_line[lane], line_bytes);
    for (int lane = 0; lane < NUM_COMPONENTS; ++lane) {{
        if (curr_line[lane] && snapshot->curr_line[lane])
            memcpy(curr_line[lane], snapshot->curr_line[lane], line_bytes);
        if (orig_line[lane] && snapshot->orig_line[lane])
            memcpy(orig_line[lane], snapshot->orig_line[lane], line_bytes);
        if (history_pixels[lane] && snapshot->history_pixels[lane])
            memcpy(history_pixels[lane], snapshot->history_pixels[lane],
                   ICH_SIZE * sizeof(unsigned int));
    }}
    if (history_valid && snapshot->history_valid)
        memcpy(history_valid, snapshot->history_valid, ICH_SIZE * sizeof(int));
    if (chunk_sizes && snapshot->chunk_sizes)
        memcpy(chunk_sizes, snapshot->chunk_sizes, snapshot->chunk_bytes);
    if (byte_out_p && snapshot->external_base)
        *byte_out_p = snapshot->external_base + dsc_cicd_cursor_offset(snapshot);
}}

static void dsc_cicd_null_state_pointers(dsc_state_t *state) {{
    state->prevLinePred = NULL;
    for (int lane = 0; lane < NUM_COMPONENTS + 1; ++lane) state->prevLine[lane] = NULL;
    for (int lane = 0; lane < NUM_COMPONENTS; ++lane) {{
        state->currLine[lane] = NULL;
        state->origLine[lane] = NULL;
        state->history.pixels[lane] = NULL;
    }}
    state->history.valid = NULL;
    state->chunkSizes = NULL;
    state->quantTableLuma = NULL;
    state->quantTableChroma = NULL;
    for (int bank = 0; bank < 3; ++bank) {{
        fifo_t *banks[3] = {{ state->encBalanceFifo, state->shifter, state->seSizeFifo }};
        for (int lane = 0; lane < DSC_CICD_VLC_GROUP_MAX_SSPS; ++lane)
            banks[bank][lane].data = NULL;
    }}
}}

static int dsc_cicd_compare_state(
    const dsc_state_t *left, const dsc_state_t *right,
    const dsc_cfg_t *cfg) {{
    dsc_state_t a = *left;
    dsc_state_t b = *right;
    int pointer_shape = 1;
    pointer_shape &= (!!left->prevLinePred == !!right->prevLinePred);
    pointer_shape &= (!!left->history.valid == !!right->history.valid);
    pointer_shape &= (!!left->chunkSizes == !!right->chunkSizes);
    for (int lane = 0; lane < NUM_COMPONENTS + 1; ++lane)
        pointer_shape &= (!!left->prevLine[lane] == !!right->prevLine[lane]);
    for (int lane = 0; lane < NUM_COMPONENTS; ++lane)
        pointer_shape &= (!!left->currLine[lane] == !!right->currLine[lane]) &&
            (!!left->origLine[lane] == !!right->origLine[lane]) &&
            (!!left->history.pixels[lane] == !!right->history.pixels[lane]);
    if (!pointer_shape) return 0;
    dsc_cicd_null_state_pointers(&a);
    dsc_cicd_null_state_pointers(&b);
    if (memcmp(&a, &b, sizeof(a)) != 0) return 0;
    size_t line_bytes = dsc_cicd_line_count(left) * sizeof(int);
    size_t pred_bytes = dsc_cicd_pred_count(left) * sizeof(PRED_TYPE);
    if (left->prevLinePred && memcmp(left->prevLinePred, right->prevLinePred, pred_bytes)) return 0;
    for (int lane = 0; lane < NUM_COMPONENTS + 1; ++lane)
        if (left->prevLine[lane] && memcmp(left->prevLine[lane], right->prevLine[lane], line_bytes)) return 0;
    for (int lane = 0; lane < NUM_COMPONENTS; ++lane) {{
        if (left->currLine[lane] && memcmp(left->currLine[lane], right->currLine[lane], line_bytes)) return 0;
        if (left->origLine[lane] && memcmp(left->origLine[lane], right->origLine[lane], line_bytes)) return 0;
        if (left->history.pixels[lane] && memcmp(left->history.pixels[lane], right->history.pixels[lane], ICH_SIZE * sizeof(unsigned int))) return 0;
    }}
    if (left->history.valid && memcmp(left->history.valid, right->history.valid, ICH_SIZE * sizeof(int))) return 0;
    if (left->chunkSizes && cfg && cfg->slice_height > 0 && memcmp(left->chunkSizes, right->chunkSizes, (size_t)cfg->slice_height * sizeof(int))) return 0;
    const fifo_t *left_banks[3] = {{ left->encBalanceFifo, left->shifter, left->seSizeFifo }};
    const fifo_t *right_banks[3] = {{ right->encBalanceFifo, right->shifter, right->seSizeFifo }};
    for (int bank = 0; bank < 3; ++bank) for (int lane = 0; lane < DSC_CICD_VLC_GROUP_MAX_SSPS; ++lane) {{
        const fifo_t *lf = &left_banks[bank][lane];
        const fifo_t *rf = &right_banks[bank][lane];
        if (lf->size != rf->size || lf->fullness != rf->fullness ||
            lf->read_ptr != rf->read_ptr || lf->write_ptr != rf->write_ptr ||
            lf->max_fullness != rf->max_fullness || lf->byte_ctr != rf->byte_ctr)
            return 0;
        if (lf->data && memcmp(lf->data, rf->data, (size_t)lf->size / 8u)) return 0;
    }}
    return 1;
}}

static void dsc_cicd_report_state_difference(
    const dsc_state_t *oracle, const dsc_state_t *rtl) {{
    static int reports;
    if (reports++ >= 16) return;
    dsc_state_t oracle_image = *oracle;
    dsc_state_t rtl_image = *rtl;
    dsc_cicd_null_state_pointers(&oracle_image);
    dsc_cicd_null_state_pointers(&rtl_image);
    for (size_t byte = 0; byte < sizeof(oracle_image); ++byte) {{
        const unsigned char c = ((const unsigned char *)&oracle_image)[byte];
        const unsigned char r = ((const unsigned char *)&rtl_image)[byte];
        if (c != r) {{
            fprintf(stderr, "  first state byte[%zu] C=0x%02x RTL=0x%02x\\n",
                    byte, (unsigned)c, (unsigned)r);
            break;
        }}
    }}
#define DSC_CICD_REPORT_FIELD(field) \
    if (oracle->field != rtl->field) \
        fprintf(stderr, "  state %s C=%d RTL=%d\\n", #field, oracle->field, rtl->field)
    DSC_CICD_REPORT_FIELD(numBits);
    DSC_CICD_REPORT_FIELD(prevNumBits);
    DSC_CICD_REPORT_FIELD(postMuxNumBits);
    DSC_CICD_REPORT_FIELD(bufferFullness);
    DSC_CICD_REPORT_FIELD(codedGroupSize);
    DSC_CICD_REPORT_FIELD(primaryQp);
    DSC_CICD_REPORT_FIELD(prevPrimaryQp);
    DSC_CICD_REPORT_FIELD(ichSelected);
    DSC_CICD_REPORT_FIELD(prevIchSelected);
    DSC_CICD_REPORT_FIELD(flatnessType);
    DSC_CICD_REPORT_FIELD(groupCount);
    DSC_CICD_REPORT_FIELD(groupCountLine);
    DSC_CICD_REPORT_FIELD(forceMpp);
    DSC_CICD_REPORT_FIELD(numBitsChunk);
    DSC_CICD_REPORT_FIELD(pixelCount);
    DSC_CICD_REPORT_FIELD(pixelsInGroup);
#undef DSC_CICD_REPORT_FIELD
    for (int unit = 0; unit < DSC_CICD_VLC_GROUP_MAX_UNITS; ++unit) {{
        if (oracle->midpointSelected[unit] != rtl->midpointSelected[unit])
            fprintf(stderr, "  midpoint[%d] C=%d RTL=%d\\n", unit,
                    oracle->midpointSelected[unit], rtl->midpointSelected[unit]);
        if (oracle->predictedSize[unit] != rtl->predictedSize[unit])
            fprintf(stderr, "  predicted[%d] C=%d RTL=%d\\n", unit,
                    oracle->predictedSize[unit], rtl->predictedSize[unit]);
        if (oracle->rcSizeUnit[unit] != rtl->rcSizeUnit[unit])
            fprintf(stderr, "  rcSize[%d] C=%d RTL=%d\\n", unit,
                    oracle->rcSizeUnit[unit], rtl->rcSizeUnit[unit]);
    }}
    const fifo_t *c_banks[3] = {{ oracle->encBalanceFifo, oracle->shifter, oracle->seSizeFifo }};
    const fifo_t *r_banks[3] = {{ rtl->encBalanceFifo, rtl->shifter, rtl->seSizeFifo }};
    for (int bank = 0; bank < 3; ++bank) for (int lane = 0; lane < DSC_CICD_VLC_GROUP_MAX_SSPS; ++lane) {{
        if (c_banks[bank][lane].fullness != r_banks[bank][lane].fullness ||
            c_banks[bank][lane].read_ptr != r_banks[bank][lane].read_ptr ||
            c_banks[bank][lane].write_ptr != r_banks[bank][lane].write_ptr)
            fprintf(stderr,
                    "  fifo[%d][%d] fullness=%d/%d read=%d/%d write=%d/%d\\n",
                    bank, lane, c_banks[bank][lane].fullness,
                    r_banks[bank][lane].fullness, c_banks[bank][lane].read_ptr,
                    r_banks[bank][lane].read_ptr, c_banks[bank][lane].write_ptr,
                    r_banks[bank][lane].write_ptr);
    }}
}}

static int dsc_cicd_compare_snapshot(
    const dsc_cicd_vlc_group_snapshot_t *pre,
    const dsc_cicd_vlc_group_snapshot_t *oracle,
    const dsc_cicd_vlc_group_snapshot_t *rtl,
    const dsc_cfg_t *cfg,
    const dsc_cicd_vlc_group_context_t *context,
    const dsc_cicd_vlc_group_output_t *output,
    int expected_units, int expected_ssps, int expected_process,
    uint32_t expected_frame_writes) {{
    if (!dsc_cicd_compare_state(&oracle->state, &rtl->state, cfg)) {{
        dsc_cicd_report_state_difference(&oracle->state, &rtl->state);
        return -1;
    }}
    if (oracle->frame_bytes != rtl->frame_bytes ||
        memcmp(oracle->frame_data, rtl->frame_data, oracle->frame_bytes) != 0 ||
        dsc_cicd_cursor_offset(oracle) != dsc_cicd_cursor_offset(rtl)) {{
        static int frame_reports;
        if (frame_reports++ < 16) {{
            fprintf(stderr,
                    "  frame bytes=%zu/%zu cursor=%zu/%zu\\n",
                    oracle->frame_bytes, rtl->frame_bytes,
                    dsc_cicd_cursor_offset(oracle),
                    dsc_cicd_cursor_offset(rtl));
            size_t common = oracle->frame_bytes < rtl->frame_bytes
                ? oracle->frame_bytes : rtl->frame_bytes;
            for (size_t byte = 0; byte < common; ++byte)
                if (oracle->frame_data[byte] != rtl->frame_data[byte]) {{
                    fprintf(stderr,
                            "  first frame byte[%zu] C=0x%02x RTL=0x%02x\\n",
                            byte, (unsigned)oracle->frame_data[byte],
                            (unsigned)rtl->frame_data[byte]);
                    break;
                }}
        }}
        return -2;
    }}
    if (context->vlc_unit_calls != (uint32_t)expected_units ||
        context->se_size_write_events != (uint32_t)expected_ssps ||
        context->process_group_calls != (uint32_t)expected_process ||
        context->frame_write_events != expected_frame_writes ||
        context->child_fatal_error || context->force_metadata_mismatch ||
        !context->child_domain_valid)
        return -3;
    if (output->vlc_unit_calls != context->vlc_unit_calls ||
        output->se_size_write_events != context->se_size_write_events ||
        output->process_group_calls != context->process_group_calls ||
        output->frame_write_events != context->frame_write_events)
        return -4;
    uint32_t event = 0;
    for (int unit = 0; unit < expected_units; ++unit, ++event)
        if (event >= context->event_count || context->event_kind[event] != 0 ||
            context->event_arg[event] != (uint32_t)unit ||
            context->event_addr[event] != 0 ||
            context->event_data[event] != (uint32_t)context->force_p1_ich2 ||
            context->event_mask[event] != 0) return -5;
    for (int lane = 0; lane < expected_ssps; ++lane, ++event) {{
        uint32_t expected_address = (uint32_t)pre->state.seSizeFifo[lane].write_ptr / 8u;
        if (event >= context->event_count || context->event_kind[event] != 1 ||
            context->event_arg[event] != (uint32_t)lane ||
            context->event_addr[event] != expected_address ||
            context->event_data[event] > DSC_CICD_VLC_GROUP_MAX_SE_SIZE ||
            context->event_mask[event] != 0xffu ||
            context->event_data[event] != oracle->state.seSizeFifo[lane].data[expected_address])
            return -6;
    }}
    if (expected_process) {{
        if (event >= context->event_count || context->event_kind[event] != 2 ||
            context->event_arg[event] != 0 || context->event_addr[event] != 0 ||
            context->event_data[event] != 0 || context->event_mask[event] != 0)
            return -7;
        ++event;
    }}
    for (; event < context->event_count; ++event)
        if (context->event_kind[event] != 3 || context->event_mask[event] == 0 ||
            context->event_addr[event] >= oracle->frame_bytes ||
            (oracle->frame_data[context->event_addr[event]] & context->event_mask[event]) !=
                (context->event_data[event] & context->event_mask[event]))
            return -8;
    if (context->event_count != (uint32_t)(expected_units + expected_ssps + expected_process) +
            context->frame_write_events)
        return -9;
    if (output->event_count != context->event_count ||
        memcmp(output->event_kind, context->event_kind, sizeof(output->event_kind)) != 0 ||
        memcmp(output->event_arg, context->event_arg, sizeof(output->event_arg)) != 0 ||
        memcmp(output->event_addr, context->event_addr, sizeof(output->event_addr)) != 0 ||
        memcmp(output->event_data, context->event_data, sizeof(output->event_data)) != 0 ||
        memcmp(output->event_mask, context->event_mask, sizeof(output->event_mask)) != 0)
        return -10;
    return 1;
}}

static int dsc_cicd_native_domain_valid(
    const dsc_cfg_t *cfg, const dsc_state_t *state,
    unsigned char **byte_out_p, int force_p1_ich2) {{
    if (!cfg || !state || !byte_out_p || !*byte_out_p || state->isEncoder != 1) return 0;
    if (state->unitsPerGroup < 3 || state->unitsPerGroup > DSC_CICD_VLC_GROUP_MAX_UNITS ||
        state->numSsps < 3 || state->numSsps > DSC_CICD_VLC_GROUP_MAX_SSPS ||
        (cfg->mux_word_size != 48 && cfg->mux_word_size != 64) ||
        cfg->bits_per_component < 8 || cfg->bits_per_component > 16 ||
        cfg->bits_per_pixel < 0 || cfg->chunk_size <= 0 || cfg->slice_height <= 0 ||
        (uint64_t)(uint32_t)cfg->chunk_size * (uint32_t)cfg->slice_height >
            (uint64_t)UINT32_MAX / 8u || cfg->rcb_bits <= 0 ||
        state->sliceWidth <= 0 || state->pixelsInGroup <= 0 ||
        force_p1_ich2 < 0 || force_p1_ich2 > 2)
        return 0;
    const fifo_t *banks[3] = {{ state->encBalanceFifo, state->shifter, state->seSizeFifo }};
    for (int bank = 0; bank < 3; ++bank) for (int lane = 0; lane < DSC_CICD_VLC_GROUP_MAX_SSPS; ++lane) {{
        const fifo_t *fifo = &banks[bank][lane];
        if (!fifo->data || fifo->size <= 0 || (fifo->size & 7) || fifo->fullness < 0 ||
            fifo->fullness > fifo->size || fifo->read_ptr < 0 || fifo->read_ptr >= fifo->size ||
            fifo->write_ptr < 0 || fifo->write_ptr >= fifo->size || fifo->max_fullness < 0 ||
            fifo->max_fullness > fifo->size) return 0;
    }}
    return 1;
}}

static void dsc_cicd_fill_fifo(
    dsc_cicd_vlc_group_fifo_t *target, const fifo_t *source) {{
    target->data = source->data;
    target->size_bits = (uint32_t)source->size;
    target->fullness = (uint32_t)source->fullness;
    target->read_ptr = (uint32_t)source->read_ptr;
    target->write_ptr = (uint32_t)source->write_ptr;
    target->max_fullness = (uint32_t)source->max_fullness;
    target->byte_ctr = (uint32_t)source->byte_ctr;
}}

static void dsc_cicd_fill_input(
    dsc_cicd_vlc_group_input_t *input, dsc_cfg_t *cfg,
    dsc_state_t *state, unsigned char **byte_out_p, int force_p1_ich2,
    size_t frame_bytes) {{
    memset(input, 0, sizeof(*input));
    input->is_encoder = state->isEncoder;
    input->units_per_group = (uint32_t)state->unitsPerGroup;
    input->num_ssps = (uint32_t)state->numSsps;
    input->mux_word_size = (uint32_t)cfg->mux_word_size;
    input->bits_per_pixel = cfg->bits_per_pixel;
    input->bits_per_component = cfg->bits_per_component;
    input->chunk_size = cfg->chunk_size;
    input->initial_xmit_delay = cfg->initial_xmit_delay;
    input->vbr_enable = cfg->vbr_enable;
    input->rcb_bits = cfg->rcb_bits;
    input->frame_capacity_bits = (uint32_t)(frame_bytes * 8u);
    input->post_mux_num_bits = (uint32_t)state->postMuxNumBits;
    input->num_bits = state->numBits;
    input->buffer_fullness = state->bufferFullness;
    input->num_bits_chunk = state->numBitsChunk;
    input->pixels_in_group = state->pixelsInGroup;
    input->slice_width = state->sliceWidth;
    input->pixel_count = state->pixelCount;
    input->group_count = state->groupCount;
    input->primary_qp = state->primaryQp;
    input->prev_primary_qp = state->prevPrimaryQp;
    input->prev_num_bits = state->prevNumBits;
    input->coded_group_size = state->codedGroupSize;
    input->group_count_line = state->groupCountLine;
    input->force_mpp = state->forceMpp;
    input->frame_data = *byte_out_p;
    for (int lane = 0; lane < DSC_CICD_VLC_GROUP_MAX_SSPS; ++lane) {{
        input->max_se_size[lane] = (uint32_t)state->maxSeSize[lane];
        input->midpoint_selected[lane] = state->midpointSelected[lane];
        for (int sample = 0; sample < 3; ++sample) {{
            input->quantized_residual[lane][sample] = state->quantizedResidual[lane][sample];
            input->quantized_residual_mid[lane][sample] = state->quantizedResidualMid[lane][sample];
        }}
        dsc_cicd_fill_fifo(&input->enc_balance[lane], &state->encBalanceFifo[lane]);
        dsc_cicd_fill_fifo(&input->shifter[lane], &state->shifter[lane]);
        dsc_cicd_fill_fifo(&input->se_size[lane], &state->seSizeFifo[lane]);
    }}
    (void)force_p1_ich2;
}}

static void dsc_cicd_copy_fifo_result(fifo_t *target, const fifo_t *source) {{
    unsigned char *data = target->data;
    int size = target->size;
    *target = *source;
    target->data = data;
    target->size = size;
    if (data && source->data && size > 0) memcpy(data, source->data, (size_t)size / 8u);
}}

static void dsc_cicd_apply_rtl_outputs(
    dsc_state_t *target, unsigned char **byte_out_p,
    const dsc_cicd_vlc_group_snapshot_t *rtl) {{
    const dsc_state_t *source = &rtl->state;
    /* Parent outputs.  No complete dsc_state_t assignment is allowed here. */
    target->postMuxNumBits = source->postMuxNumBits;
    target->numBits = source->numBits;
    target->bufferFullness = source->bufferFullness;
    target->numBitsChunk = source->numBitsChunk;
    target->pixelsInGroup = source->pixelsInGroup;
    target->sliceWidth = source->sliceWidth;
    target->pixelCount = source->pixelCount;
    target->groupCount = source->groupCount;
    target->primaryQp = source->primaryQp;
    target->prevPrimaryQp = source->prevPrimaryQp;
    target->prevNumBits = source->prevNumBits;
    target->codedGroupSize = source->codedGroupSize;
    target->groupCountLine = source->groupCountLine;
    target->forceMpp = source->forceMpp;
    for (int unit = 0; unit < DSC_CICD_VLC_GROUP_MAX_UNITS; ++unit) {{
        target->midpointSelected[unit] = source->midpointSelected[unit];
        target->predictedSize[unit] = source->predictedSize[unit];
        target->rcSizeUnit[unit] = source->rcSizeUnit[unit];
        for (int sample = 0; sample < 3; ++sample) {{
            target->quantizedResidual[unit][sample] = source->quantizedResidual[unit][sample];
            target->quantizedResidualMid[unit][sample] = source->quantizedResidualMid[unit][sample];
        }}
    }}
    /* Hash-pinned child result footprint: VLCUnit's scalar decision results
     * and the three FIFO banks; ProcessGroupEnc's post-mux/FIFO/frame result
     * is represented by the same explicit parent memory outputs. */
    target->ichSelected = source->ichSelected;
    target->prevIchSelected = source->prevIchSelected;
    target->flatnessType = source->flatnessType;
    for (int bank = 0; bank < 3; ++bank) {{
        fifo_t *target_banks[3] = {{ target->encBalanceFifo, target->shifter, target->seSizeFifo }};
        const fifo_t *source_banks[3] = {{ source->encBalanceFifo, source->shifter, source->seSizeFifo }};
        for (int lane = 0; lane < DSC_CICD_VLC_GROUP_MAX_SSPS; ++lane)
            dsc_cicd_copy_fifo_result(&target_banks[bank][lane], &source_banks[bank][lane]);
    }}
    if (byte_out_p && *byte_out_p && rtl->frame_data)
        memcpy(*byte_out_p, rtl->frame_data, rtl->frame_bytes);
    if (byte_out_p && rtl->external_base)
        *byte_out_p = rtl->external_base + dsc_cicd_cursor_offset(rtl);
}}

void dsc_cicd_invoke({caller_declarations}) {{
    int mode = dsc_cicd_mode();
    dsc_cicd_note_call(mode);
    if (mode == 0) {{
        {original}({alias_call});
        return;
    }}
    if (!dsc_cicd_native_domain_valid(
            {cfg_name}, {state_name}, {byte_name}, {force_name})) {{
        fprintf(stderr, "unsupported VLCGroup native domain\\n");
        exit(2);
    }}
    size_t frame_bytes = (size_t){cfg_name}->chunk_size *
        (size_t){cfg_name}->slice_height;
    dsc_cicd_vlc_group_snapshot_t pre, oracle, rtl;
    if (!dsc_cicd_snapshot_capture(
            &pre, {state_name}, *{byte_name}, frame_bytes, {cfg_name}) ||
        !dsc_cicd_snapshot_clone(&oracle, &pre, {cfg_name}) ||
        !dsc_cicd_snapshot_clone(&rtl, &pre, {cfg_name})) {{
        fprintf(stderr, "VLCGroup private snapshot failed\\n");
        exit(2);
    }}
    /* The oracle is immutable with respect to the caller.  Restore the
     * original snapshot before the RTL bridge, even though capture itself
     * never called C on the original object. */
    dsc_cicd_restore_snapshot({state_name}, {byte_name}, &pre);
    {original}({cfg_name}, &oracle.state, &oracle.byte_cursor, {force_name});
    dsc_cicd_restore_snapshot({state_name}, {byte_name}, &pre);

    dsc_cicd_vlc_group_context_t context;
    dsc_cicd_vlc_group_input_t input;
    dsc_cicd_vlc_group_output_t output;
    memset(&context, 0, sizeof(context));
    memset(&output, 0, sizeof(output));
    context.cfg = {cfg_name};
    context.state = &rtl.state;
    context.byte_out_p = &rtl.byte_cursor;
    context.force_p1_ich2 = {force_name};
    context.frame_observe = rtl.frame_data;
    context.frame_observe_bytes = (uint32_t)frame_bytes;
    context.child_domain_valid = 1;
    dsc_cicd_fill_input(
        &input, {cfg_name}, &rtl.state, &rtl.byte_cursor,
        {force_name}, frame_bytes);
    dsc_cicd_rtl(&input, &output, &context);
    rtl.byte_cursor = context.byte_out_p ? *context.byte_out_p : rtl.byte_cursor;
    int expected_process = {state_name}->groupCount >
        {cfg_name}->mux_word_size +
        (4 * {cfg_name}->bits_per_component + 4) - 3;
    uint32_t expected_frame_writes = 0;
    size_t expected_frame_offset = (size_t)pre.state.postMuxNumBits / 8u;
    size_t expected_frame_bytes = expected_process
        ? (size_t)pre.state.numSsps * (size_t){cfg_name}->mux_word_size / 8u
        : 0u;
    if (expected_frame_offset >= pre.frame_bytes) expected_frame_bytes = 0;
    else if (expected_frame_bytes > pre.frame_bytes - expected_frame_offset)
        expected_frame_bytes = pre.frame_bytes - expected_frame_offset;
    for (size_t frame_index = 0; frame_index < expected_frame_bytes; ++frame_index)
        if (pre.frame_data[expected_frame_offset + frame_index] !=
            oracle.frame_data[expected_frame_offset + frame_index])
            ++expected_frame_writes;
    int dsc_cicd_compare_code = dsc_cicd_compare_snapshot(
        &pre, &oracle, &rtl, {cfg_name}, &context, &output,
        {state_name}->unitsPerGroup, {state_name}->numSsps, expected_process,
        expected_frame_writes);
    if (!output.done || output.bound_violation || output.fatal_error ||
        output.illegal_domain || output.child_error ||
        dsc_cicd_compare_code != 1) {{
        ++dsc_cicd_mismatches;
        if (dsc_cicd_mismatches <= 16) {{
            if (oracle.state.forceMpp != rtl.state.forceMpp)
                fprintf(stderr,
                        "  forceMpp inputs bpp=%d pixels=%d numBitsChunk=%d "
                        "chunkBits=%d fullness=%d units=%d pixelCount=%d "
                        "initialDelay=%d sliceWidth=%d vbr=%d\\n",
                        {cfg_name}->bits_per_pixel, pre.state.pixelsInGroup,
                        pre.state.numBitsChunk, {cfg_name}->chunk_size * 8,
                        pre.state.bufferFullness, pre.state.unitsPerGroup,
                        pre.state.pixelCount, {cfg_name}->initial_xmit_delay,
                        pre.state.sliceWidth, {cfg_name}->vbr_enable);
            fprintf(stderr,
                    "VLCGroup C/RTL mismatch: code=%d flags=%d/%d/%d/%d "
                    "events=%u units=%u se=%u process=%u frame=%u "
                    "expected=%d/%d/%d/%u gc=%d threshold=%d\\n",
                    dsc_cicd_compare_code, output.done, output.bound_violation,
                    output.fatal_error, output.child_error, context.event_count,
                    context.vlc_unit_calls, context.se_size_write_events,
                    context.process_group_calls, context.frame_write_events,
                    {state_name}->unitsPerGroup, {state_name}->numSsps,
                    expected_process, expected_frame_writes,
                    {state_name}->groupCount,
                    {cfg_name}->mux_word_size +
                        (4 * {cfg_name}->bits_per_component + 4) - 3);
        }}
    }}

    /* Both C_ONLY and SHADOW commit the C oracle.  RTL_RETURN starts from the
     * restored pre-state and copies only explicit parent outputs plus the
     * hash-pinned child result/memory footprint. */
    dsc_cicd_restore_snapshot({state_name}, {byte_name}, &pre);
    if (mode == 1) {{
        dsc_cicd_restore_snapshot({state_name}, {byte_name}, &oracle);
        if (oracle.external_base && oracle.frame_data && oracle.frame_bytes)
            memcpy(oracle.external_base, oracle.frame_data, oracle.frame_bytes);
    }} else dsc_cicd_apply_rtl_outputs({state_name}, {byte_name}, &rtl);
    dsc_cicd_snapshot_destroy(&rtl);
    dsc_cicd_snapshot_destroy(&oracle);
    dsc_cicd_snapshot_destroy(&pre);
}}
'''


def _bridge_source(module: str) -> str:
    return rf'''#include <stdint.h>
#include <string.h>
#include "dsc_cicd_rtl_abi.h"
#include "V{module}.h"

double sc_time_stamp() {{ return 0.0; }}

static uint8_t dsc_cicd_read_byte(const fifo_t *fifo, uint32_t address) {{
    if (!fifo || !fifo->data || fifo->size <= 0 || address >= (uint32_t)fifo->size / 8u)
        return 0;
    return fifo->data[address];
}}

static void dsc_cicd_write_byte(
    fifo_t *fifo, uint32_t address, uint8_t data, uint8_t mask) {{
    if (!fifo || !fifo->data || fifo->size <= 0 || address >= (uint32_t)fifo->size / 8u)
        return;
    uint8_t old = fifo->data[address];
    fifo->data[address] = (uint8_t)((old & (uint8_t)~mask) | (data & mask));
}}

static void dsc_cicd_record_event(
    dsc_cicd_vlc_group_context_t *context, uint8_t kind, uint32_t arg,
    uint32_t address, uint32_t data, uint32_t mask) {{
    if (context->event_count >= DSC_CICD_VLC_GROUP_MAX_EVENTS) return;
    uint32_t index = context->event_count++;
    context->event_kind[index] = kind;
    context->event_arg[index] = arg;
    context->event_addr[index] = address;
    context->event_data[index] = data;
    context->event_mask[index] = mask;
    if (kind == 1) ++context->se_size_write_events;
    if (kind == 3) ++context->frame_write_events;
}}

static void dsc_cicd_set_parent_inputs(
    V{module} &dut, const dsc_cicd_vlc_group_input_t *input) {{
    dut.is_encoder = input->is_encoder;
    dut.units_per_group = input->units_per_group;
    dut.num_ssps = input->num_ssps;
    dut.mux_word_size = input->mux_word_size;
    dut.bits_per_pixel = input->bits_per_pixel;
    dut.bits_per_component = input->bits_per_component;
    dut.chunk_size = input->chunk_size;
    dut.initial_xmit_delay = input->initial_xmit_delay;
    dut.vbr_enable = input->vbr_enable;
    dut.rcb_bits = input->rcb_bits;
    dut.frame_capacity_bits = input->frame_capacity_bits;
    dut.post_mux_num_bits_in = input->post_mux_num_bits;
    dut.num_bits_in = input->num_bits;
    dut.buffer_fullness_in = input->buffer_fullness;
    dut.num_bits_chunk_in = input->num_bits_chunk;
    dut.pixels_in_group_in = input->pixels_in_group;
    dut.slice_width_in = input->slice_width;
    dut.pixel_count_in = input->pixel_count;
    dut.group_count_in = input->group_count;
    dut.primary_qp_in = input->primary_qp;
    dut.prev_primary_qp_in = input->prev_primary_qp;
    dut.prev_num_bits_in = input->prev_num_bits;
    dut.coded_group_size_in = input->coded_group_size;
    dut.group_count_line_in = input->group_count_line;
    dut.force_mpp_in = input->force_mpp;
    for (int lane = 0; lane < DSC_CICD_VLC_GROUP_MAX_SSPS; ++lane) {{
        dut.max_se_size[lane] = input->max_se_size[lane];
        dut.midpoint_selected_in[lane] = input->midpoint_selected[lane];
        for (int sample = 0; sample < 3; ++sample) {{
            dut.quantized_residual_in[lane][sample] = input->quantized_residual[lane][sample];
            dut.quantized_residual_mid_in[lane][sample] = input->quantized_residual_mid[lane][sample];
        }}
#define DSC_CICD_SET_FIFO(prefix, bank) \
        dut.prefix##_size_bits_in[lane] = input->bank[lane].size_bits; \
        dut.prefix##_fullness_in[lane] = input->bank[lane].fullness; \
        dut.prefix##_read_ptr_in[lane] = input->bank[lane].read_ptr; \
        dut.prefix##_write_ptr_in[lane] = input->bank[lane].write_ptr; \
        dut.prefix##_max_fullness_in[lane] = input->bank[lane].max_fullness; \
        dut.prefix##_byte_ctr_in[lane] = input->bank[lane].byte_ctr
        DSC_CICD_SET_FIFO(enc_balance, enc_balance);
        DSC_CICD_SET_FIFO(shifter, shifter);
        DSC_CICD_SET_FIFO(se_size, se_size);
#undef DSC_CICD_SET_FIFO
    }}
}}

static void dsc_cicd_set_vlc_child_inputs(
    V{module} &dut, const dsc_cicd_vlc_group_context_t *context) {{
    const dsc_state_t *state = context->state;
    dut.vlc_unit_num_bits_out = state->numBits;
    dut.vlc_unit_primary_qp_out = state->primaryQp;
    dut.vlc_unit_domain_valid = context->child_domain_valid;
    dut.vlc_unit_fatal_error = context->child_fatal_error;
    for (int lane = 0; lane < DSC_CICD_VLC_GROUP_MAX_SSPS; ++lane) {{
        dut.vlc_unit_enc_balance_size_bits_out[lane] = state->encBalanceFifo[lane].size;
        dut.vlc_unit_enc_balance_fullness_out[lane] = state->encBalanceFifo[lane].fullness;
        dut.vlc_unit_enc_balance_read_ptr_out[lane] = state->encBalanceFifo[lane].read_ptr;
        dut.vlc_unit_enc_balance_write_ptr_out[lane] = state->encBalanceFifo[lane].write_ptr;
        dut.vlc_unit_enc_balance_max_fullness_out[lane] = state->encBalanceFifo[lane].max_fullness;
        dut.vlc_unit_enc_balance_byte_ctr_out[lane] = state->encBalanceFifo[lane].byte_ctr;
    }}
}}

static void dsc_cicd_set_process_child_inputs(
    V{module} &dut, const dsc_cicd_vlc_group_context_t *context) {{
    const dsc_state_t *state = context->state;
    dut.process_group_post_mux_num_bits_out = state->postMuxNumBits;
    dut.process_group_domain_valid = context->child_domain_valid;
    dut.process_group_fatal_error = context->child_fatal_error;
    for (int lane = 0; lane < DSC_CICD_VLC_GROUP_MAX_SSPS; ++lane) {{
#define DSC_CICD_SET_CHILD_FIFO(prefix, bank) \
        dut.process_group_##prefix##_size_bits_out[lane] = state->bank[lane].size; \
        dut.process_group_##prefix##_fullness_out[lane] = state->bank[lane].fullness; \
        dut.process_group_##prefix##_read_ptr_out[lane] = state->bank[lane].read_ptr; \
        dut.process_group_##prefix##_write_ptr_out[lane] = state->bank[lane].write_ptr; \
        dut.process_group_##prefix##_max_fullness_out[lane] = state->bank[lane].max_fullness; \
        dut.process_group_##prefix##_byte_ctr_out[lane] = state->bank[lane].byte_ctr
        DSC_CICD_SET_CHILD_FIFO(enc_balance, encBalanceFifo);
        DSC_CICD_SET_CHILD_FIFO(shifter, shifter);
        DSC_CICD_SET_CHILD_FIFO(se_size, seSizeFifo);
#undef DSC_CICD_SET_CHILD_FIFO
    }}
}}

static void dsc_cicd_apply_parent_outputs(
    V{module} &dut, dsc_state_t *state) {{
    state->postMuxNumBits = dut.post_mux_num_bits_out;
    state->numBits = dut.num_bits_out;
    state->bufferFullness = dut.buffer_fullness_out;
    state->numBitsChunk = dut.num_bits_chunk_out;
    state->pixelsInGroup = dut.pixels_in_group_out;
    state->sliceWidth = dut.slice_width_out;
    state->pixelCount = dut.pixel_count_out;
    state->groupCount = dut.group_count_out;
    state->primaryQp = dut.primary_qp_out;
    state->prevPrimaryQp = dut.prev_primary_qp_out;
    state->prevNumBits = dut.prev_num_bits_out;
    state->codedGroupSize = dut.coded_group_size_out;
    state->groupCountLine = dut.group_count_line_out;
    state->forceMpp = dut.force_mpp_out;
    for (int lane = 0; lane < DSC_CICD_VLC_GROUP_MAX_UNITS; ++lane) {{
        /* midpointSelected is a VLCUnit child result.  The parent register only
         * models VLCGroup's pre-child clear, so committing it here would erase
         * the hash-pinned child's final decision. */
        for (int sample = 0; sample < 3; ++sample) {{
            state->quantizedResidual[lane][sample] = dut.quantized_residual_out[lane][sample];
            state->quantizedResidualMid[lane][sample] = dut.quantized_residual_mid_out[lane][sample];
        }}
    }}
#define DSC_CICD_APPLY_FIFO(prefix, bank) \
    state->bank[lane].size = dut.prefix##_size_bits_out[lane]; \
    state->bank[lane].fullness = dut.prefix##_fullness_out[lane]; \
    state->bank[lane].read_ptr = dut.prefix##_read_ptr_out[lane]; \
    state->bank[lane].write_ptr = dut.prefix##_write_ptr_out[lane]; \
    state->bank[lane].max_fullness = dut.prefix##_max_fullness_out[lane]; \
    state->bank[lane].byte_ctr = dut.prefix##_byte_ctr_out[lane]
    for (int lane = 0; lane < DSC_CICD_VLC_GROUP_MAX_SSPS; ++lane) {{
        DSC_CICD_APPLY_FIFO(enc_balance, encBalanceFifo);
        DSC_CICD_APPLY_FIFO(shifter, shifter);
        DSC_CICD_APPLY_FIFO(se_size, seSizeFifo);
    }}
#undef DSC_CICD_APPLY_FIFO
}}

template <
    typename TReadAddr, typename TReadValid, typename TReadData,
    typename TWriteAddr, typename TWriteReady, typename TWriteData,
    typename TWriteMask>
static void dsc_cicd_service_fifo_bank(
    V{module} &dut, dsc_cicd_vlc_group_context_t *context,
    uint32_t read_req, const TReadAddr &read_addr,
    TReadValid &read_valid, TReadData &read_data,
    uint32_t write_req, const TWriteAddr &write_addr,
    TWriteReady &write_ready, const TWriteData &write_data,
    const TWriteMask &write_mask, fifo_t *bank, int bank_number) {{
    (void)dut;
    *read_valid = 0;
    *write_ready = 0;
    for (int lane = 0; lane < DSC_CICD_VLC_GROUP_MAX_SSPS; ++lane) {{
        if (read_req & (1u << lane)) {{
            read_data[lane] = dsc_cicd_read_byte(&bank[lane], read_addr[lane]);
            read_valid[lane] = 1;
        }}
        if (write_req & (1u << lane)) {{
            dsc_cicd_write_byte(&bank[lane], write_addr[lane], write_data[lane], write_mask[lane]);
            write_ready[lane] = 1;
            if (bank_number == 2)
                dsc_cicd_record_event(context, 1, (uint32_t)lane, write_addr[lane], write_data[lane], write_mask[lane]);
        }}
    }}
}}

void dsc_cicd_rtl(
    dsc_cicd_vlc_group_input_t *input,
    dsc_cicd_vlc_group_output_t *output,
    dsc_cicd_vlc_group_context_t *context) {{
    V{module} dut;
    memset(output, 0, sizeof(*output));
    dut.clk = 0;
    dut.rst_n = 0;
    dut.start = 0;
    dsc_cicd_set_parent_inputs(dut, input);
    for (int lane = 0; lane < DSC_CICD_VLC_GROUP_MAX_UNITS; ++lane) for (int sample = 0; sample < 3; ++sample) {{
        dut.vlc_unit_enc_balance_mem_read_data[lane] = 0;
        dut.vlc_unit_shifter_mem_read_data[lane] = 0;
        dut.vlc_unit_se_size_mem_read_data[lane] = 0;
    }}
    dut.eval();
    dut.rst_n = 1;
    dut.eval();
    bool vlc_result_pending = false;
    bool process_result_pending = false;
    uint32_t cycles = 0;
    auto reset_memory_inputs = [&]() {{
        dut.enc_balance_mem_read_valid = 0; dut.enc_balance_mem_write_ready = 0;
        dut.shifter_mem_read_valid = 0; dut.shifter_mem_write_ready = 0;
        dut.se_size_mem_read_valid = 0; dut.se_size_mem_write_ready = 0;
        dut.frame_mem_write_ready = 0;
        dut.vlc_unit_ready = 0; dut.vlc_unit_done = 0;
        dut.vlc_unit_domain_valid = context->child_domain_valid;
        dut.vlc_unit_fatal_error = context->child_fatal_error;
        dut.process_group_ready = 0; dut.process_group_done = 0;
        dut.process_group_domain_valid = context->child_domain_valid;
        dut.process_group_fatal_error = context->child_fatal_error;
        dut.vlc_unit_enc_balance_mem_read_req = 0;
        dut.vlc_unit_enc_balance_mem_write_req = 0;
        dut.vlc_unit_shifter_mem_read_req = 0;
        dut.vlc_unit_shifter_mem_write_req = 0;
        dut.vlc_unit_se_size_mem_read_req = 0;
        dut.vlc_unit_se_size_mem_write_req = 0;
        dut.process_group_enc_balance_mem_read_req = 0;
        dut.process_group_enc_balance_mem_write_req = 0;
        dut.process_group_shifter_mem_read_req = 0;
        dut.process_group_shifter_mem_write_req = 0;
        dut.process_group_se_size_mem_read_req = 0;
        dut.process_group_se_size_mem_write_req = 0;
        dut.process_group_frame_mem_write_req = 0;
        for (int lane = 0; lane < DSC_CICD_VLC_GROUP_MAX_SSPS; ++lane) {{
            dut.vlc_unit_enc_balance_mem_read_addr[lane] = 0;
            dut.vlc_unit_enc_balance_mem_write_addr[lane] = 0;
            dut.vlc_unit_enc_balance_mem_write_data[lane] = 0;
            dut.vlc_unit_enc_balance_mem_write_bit_mask[lane] = 0;
            dut.vlc_unit_shifter_mem_read_addr[lane] = 0;
            dut.vlc_unit_shifter_mem_write_addr[lane] = 0;
            dut.vlc_unit_shifter_mem_write_data[lane] = 0;
            dut.vlc_unit_shifter_mem_write_bit_mask[lane] = 0;
            dut.vlc_unit_se_size_mem_read_addr[lane] = 0;
            dut.vlc_unit_se_size_mem_write_addr[lane] = 0;
            dut.vlc_unit_se_size_mem_write_data[lane] = 0;
            dut.vlc_unit_se_size_mem_write_bit_mask[lane] = 0;
            dut.process_group_enc_balance_mem_read_addr[lane] = 0;
            dut.process_group_enc_balance_mem_write_addr[lane] = 0;
            dut.process_group_enc_balance_mem_write_data[lane] = 0;
            dut.process_group_enc_balance_mem_write_bit_mask[lane] = 0;
            dut.process_group_shifter_mem_read_addr[lane] = 0;
            dut.process_group_shifter_mem_write_addr[lane] = 0;
            dut.process_group_shifter_mem_write_data[lane] = 0;
            dut.process_group_shifter_mem_write_bit_mask[lane] = 0;
            dut.process_group_se_size_mem_read_addr[lane] = 0;
            dut.process_group_se_size_mem_write_addr[lane] = 0;
            dut.process_group_se_size_mem_write_data[lane] = 0;
            dut.process_group_se_size_mem_write_bit_mask[lane] = 0;
        }}
        dut.process_group_frame_mem_write_addr = 0;
        dut.process_group_frame_mem_write_data = 0;
        dut.process_group_frame_mem_write_bit_mask = 0;
    }};
    auto service_low_phase = [&]() {{
        dut.clk = 0;
        reset_memory_inputs();
        dsc_cicd_set_vlc_child_inputs(dut, context);
        dsc_cicd_set_process_child_inputs(dut, context);
        dut.eval();
        if (dut.vlc_unit_start) {{
            if (dut.vlc_unit_force_p1_ich2 != context->force_p1_ich2)
                context->force_metadata_mismatch = 1;
            /* VLCGroup owns these pre-child updates in the source order.
             * The semantic child must observe the newly computed forceMpp,
             * not the previous group's state image. */
            context->state->forceMpp = dut.force_mpp_out;
            if (dut.vlc_unit_index == 0)
                for (int lane = 0; lane < context->state->unitsPerGroup; ++lane)
                    context->state->midpointSelected[lane] =
                        dut.midpoint_selected_out[lane];
            context->state->numBits = dut.vlc_unit_num_bits_in;
            context->state->primaryQp = dut.vlc_unit_primary_qp_in;
            for (int lane = 0; lane < DSC_CICD_VLC_GROUP_MAX_SSPS; ++lane) {{
                context->state->encBalanceFifo[lane].size = dut.vlc_unit_enc_balance_size_bits_in[lane];
                context->state->encBalanceFifo[lane].fullness = dut.vlc_unit_enc_balance_fullness_in[lane];
                context->state->encBalanceFifo[lane].read_ptr = dut.vlc_unit_enc_balance_read_ptr_in[lane];
                context->state->encBalanceFifo[lane].write_ptr = dut.vlc_unit_enc_balance_write_ptr_in[lane];
                context->state->encBalanceFifo[lane].max_fullness = dut.vlc_unit_enc_balance_max_fullness_in[lane];
                context->state->encBalanceFifo[lane].byte_ctr = dut.vlc_unit_enc_balance_byte_ctr_in[lane];
            }}
            dsc_cicd_vlc_group_service_vlc_unit(
                context, (int)dut.vlc_unit_index, context->force_p1_ich2);
            vlc_result_pending = true;
            dut.vlc_unit_ready = 1;
        }} else if (vlc_result_pending) {{
            dsc_cicd_set_vlc_child_inputs(dut, context);
            dut.vlc_unit_done = 1;
        }}
        if (dut.process_group_start) {{
            uint8_t frame_before[DSC_CICD_VLC_GROUP_MAX_SSPS * 8u] = {{0}};
            uint32_t frame_offset = dut.process_group_post_mux_num_bits_in / 8u;
            uint32_t frame_bytes = context->cfg
                ? (uint32_t)context->state->numSsps *
                    (uint32_t)context->cfg->mux_word_size / 8u
                : 0u;
            if (frame_bytes > sizeof(frame_before)) frame_bytes = sizeof(frame_before);
            if (frame_offset >= context->frame_observe_bytes) frame_bytes = 0;
            else if (frame_bytes > context->frame_observe_bytes - frame_offset)
                frame_bytes = context->frame_observe_bytes - frame_offset;
            if (context->frame_observe && frame_bytes)
                memcpy(frame_before, context->frame_observe + frame_offset, frame_bytes);
            context->state->postMuxNumBits = dut.process_group_post_mux_num_bits_in;
            for (int lane = 0; lane < DSC_CICD_VLC_GROUP_MAX_SSPS; ++lane) {{
                context->state->encBalanceFifo[lane].size = dut.process_group_enc_balance_size_bits_in[lane];
                context->state->encBalanceFifo[lane].fullness = dut.process_group_enc_balance_fullness_in[lane];
                context->state->encBalanceFifo[lane].read_ptr = dut.process_group_enc_balance_read_ptr_in[lane];
                context->state->encBalanceFifo[lane].write_ptr = dut.process_group_enc_balance_write_ptr_in[lane];
                context->state->encBalanceFifo[lane].max_fullness = dut.process_group_enc_balance_max_fullness_in[lane];
                context->state->encBalanceFifo[lane].byte_ctr = dut.process_group_enc_balance_byte_ctr_in[lane];
                context->state->shifter[lane].size = dut.process_group_shifter_size_bits_in[lane];
                context->state->shifter[lane].fullness = dut.process_group_shifter_fullness_in[lane];
                context->state->shifter[lane].read_ptr = dut.process_group_shifter_read_ptr_in[lane];
                context->state->shifter[lane].write_ptr = dut.process_group_shifter_write_ptr_in[lane];
                context->state->shifter[lane].max_fullness = dut.process_group_shifter_max_fullness_in[lane];
                context->state->shifter[lane].byte_ctr = dut.process_group_shifter_byte_ctr_in[lane];
                context->state->seSizeFifo[lane].size = dut.process_group_se_size_size_bits_in[lane];
                context->state->seSizeFifo[lane].fullness = dut.process_group_se_size_fullness_in[lane];
                context->state->seSizeFifo[lane].read_ptr = dut.process_group_se_size_read_ptr_in[lane];
                context->state->seSizeFifo[lane].write_ptr = dut.process_group_se_size_write_ptr_in[lane];
                context->state->seSizeFifo[lane].max_fullness = dut.process_group_se_size_max_fullness_in[lane];
                context->state->seSizeFifo[lane].byte_ctr = dut.process_group_se_size_byte_ctr_in[lane];
            }}
            dsc_cicd_vlc_group_service_process_group(context);
            for (uint32_t frame_index = 0; frame_index < frame_bytes; ++frame_index)
                if (context->frame_observe &&
                    frame_before[frame_index] !=
                        context->frame_observe[frame_offset + frame_index]) {{
                    dsc_cicd_record_event(
                        context, 3, 0, frame_offset + frame_index,
                        context->frame_observe[frame_offset + frame_index], 0xffu);
                }}
            process_result_pending = true;
            dut.process_group_ready = 1;
        }} else if (process_result_pending) {{
            dsc_cicd_set_process_child_inputs(dut, context);
            dut.process_group_done = 1;
        }}
        uint8_t read_valid[DSC_CICD_VLC_GROUP_MAX_SSPS] = {{0}};
        uint8_t read_data[DSC_CICD_VLC_GROUP_MAX_SSPS] = {{0}};
        uint8_t write_ready[DSC_CICD_VLC_GROUP_MAX_SSPS] = {{0}};
#define DSC_CICD_SERVICE_BANK(prefix, bank, number) \
        dsc_cicd_service_fifo_bank(dut, context, dut.prefix##_mem_read_req, dut.prefix##_mem_read_addr, \
            read_valid, read_data, dut.prefix##_mem_write_req, dut.prefix##_mem_write_addr, \
            write_ready, dut.prefix##_mem_write_data, dut.prefix##_mem_write_bit_mask, bank, number); \
        dut.prefix##_mem_read_valid = 0; dut.prefix##_mem_write_ready = 0; \
        for (int lane = 0; lane < DSC_CICD_VLC_GROUP_MAX_SSPS; ++lane) {{ \
            dut.prefix##_mem_read_valid |= ((uint32_t)read_valid[lane] << lane); \
            dut.prefix##_mem_write_ready |= ((uint32_t)write_ready[lane] << lane); \
            dut.prefix##_mem_read_data[lane] = read_data[lane]; \
        }}
        DSC_CICD_SERVICE_BANK(enc_balance, context->state->encBalanceFifo, 0);
        DSC_CICD_SERVICE_BANK(shifter, context->state->shifter, 1);
        DSC_CICD_SERVICE_BANK(se_size, context->state->seSizeFifo, 2);
#undef DSC_CICD_SERVICE_BANK
        if (dut.frame_mem_write_req) {{
            uint32_t address = dut.frame_mem_write_addr;
            if (context->byte_out_p && *context->byte_out_p &&
                address < context->frame_observe_bytes) {{
                uint8_t *location = *context->byte_out_p + address;
                *location = (uint8_t)((*location & (uint8_t)~dut.frame_mem_write_bit_mask) |
                    (dut.frame_mem_write_data & dut.frame_mem_write_bit_mask));
                dut.frame_mem_write_ready = 1;
                dsc_cicd_record_event(context, 3, 0, address,
                    dut.frame_mem_write_data, dut.frame_mem_write_bit_mask);
            }}
        }}
        dut.eval();
    }};
    dut.start = 1;
    service_low_phase();
    dut.clk = 1; dut.eval(); ++cycles;
    dut.start = 0;
    while (!dut.done && cycles < DSC_CICD_VLC_GROUP_MAX_CYCLES) {{
        service_low_phase();
        dut.clk = 1; dut.eval(); ++cycles;
    }}
    output->cycles = cycles;
    output->busy = dut.busy;
    output->done = dut.done;
    output->domain_valid = dut.domain_valid;
    output->illegal_domain = dut.illegal_domain;
    output->fatal_error = dut.fatal_error;
    output->bound_violation = dut.bound_violation;
    output->child_error = dut.child_error;
    output->fifo_underflow = dut.fifo_underflow;
    output->fifo_overflow = dut.fifo_overflow;
    output->se_size_overflow = dut.se_size_overflow;
    output->buffer_overflow = dut.buffer_overflow;
    if (!dut.done) {{ output->bound_violation = 1; output->fatal_error = 1; }}
    dsc_cicd_apply_parent_outputs(dut, context->state);
    output->post_mux_num_bits = context->state->postMuxNumBits;
    output->num_bits = context->state->numBits;
    output->buffer_fullness = context->state->bufferFullness;
    output->num_bits_chunk = context->state->numBitsChunk;
    output->pixels_in_group = context->state->pixelsInGroup;
    output->slice_width = context->state->sliceWidth;
    output->pixel_count = context->state->pixelCount;
    output->group_count = context->state->groupCount;
    output->primary_qp = context->state->primaryQp;
    output->prev_primary_qp = context->state->prevPrimaryQp;
    output->prev_num_bits = context->state->prevNumBits;
    output->coded_group_size = context->state->codedGroupSize;
    output->group_count_line = context->state->groupCountLine;
    output->force_mpp = context->state->forceMpp;
    for (int lane = 0; lane < DSC_CICD_VLC_GROUP_MAX_UNITS; ++lane) {{
        output->midpoint_selected[lane] = context->state->midpointSelected[lane];
        for (int sample = 0; sample < 3; ++sample) {{
            output->quantized_residual[lane][sample] = context->state->quantizedResidual[lane][sample];
            output->quantized_residual_mid[lane][sample] = context->state->quantizedResidualMid[lane][sample];
        }}
    }}
    for (int lane = 0; lane < DSC_CICD_VLC_GROUP_MAX_SSPS; ++lane) {{
#define DSC_CICD_GET_FIFO(prefix, out_bank, state_bank) \
        output->out_bank[lane].data = context->state->state_bank[lane].data; \
        output->out_bank[lane].size_bits = dut.prefix##_size_bits_out[lane]; \
        output->out_bank[lane].fullness = dut.prefix##_fullness_out[lane]; \
        output->out_bank[lane].read_ptr = dut.prefix##_read_ptr_out[lane]; \
        output->out_bank[lane].write_ptr = dut.prefix##_write_ptr_out[lane]; \
        output->out_bank[lane].max_fullness = dut.prefix##_max_fullness_out[lane]; \
        output->out_bank[lane].byte_ctr = dut.prefix##_byte_ctr_out[lane]
        DSC_CICD_GET_FIFO(enc_balance, enc_balance, encBalanceFifo);
        DSC_CICD_GET_FIFO(shifter, shifter, shifter);
        DSC_CICD_GET_FIFO(se_size, se_size, seSizeFifo);
#undef DSC_CICD_GET_FIFO
    }}
    output->vlc_unit_calls = context->vlc_unit_calls;
    output->process_group_calls = context->process_group_calls;
    output->se_size_write_events = context->se_size_write_events;
    output->frame_write_events = context->frame_write_events;
    output->event_count = context->event_count;
    memcpy(output->event_kind, context->event_kind, sizeof(output->event_kind));
    memcpy(output->event_arg, context->event_arg, sizeof(output->event_arg));
    memcpy(output->event_addr, context->event_addr, sizeof(output->event_addr));
    memcpy(output->event_data, context->event_data, sizeof(output->event_data));
    memcpy(output->event_mask, context->event_mask, sizeof(output->event_mask));
}}
'''


def write_vlc_group_encode_overlay_sources(
    agent: Any,
    contract: dict[str, Any],
    source_dir: pathlib.Path,
    module: str,
    candidate_sv: pathlib.Path,
) -> dict[str, Any]:
    """Emit the bounded VLCGroup C/oracle and sequential Verilator adapter."""

    semantics = contract.get("semantics", {}) or {}
    if semantics.get("kind") != "vlc_group_encode_fsm":
        raise RuntimeError("contract is not the VLCGroup Encode FSM")
    finite = semantics.get("finite_bounds", {}) or {}
    if {
        "max_units": int(finite.get("max_units", 0)),
        "max_ssps": int(finite.get("max_ssps", 0)),
        "max_se_size": int(finite.get("max_se_size", 0)),
        "max_cycles": int(finite.get("max_cycles", 0)),
    } != {
        "max_units": _MAX_UNITS,
        "max_ssps": _MAX_SSPS,
        "max_se_size": _MAX_SE_SIZE,
        "max_cycles": _MAX_CYCLES,
    }:
        raise RuntimeError("VLCGroup finite bounds changed")
    legal = semantics.get("legal_domain", {}) or {}
    if legal.get("units_per_group") != [3, 4] or legal.get("num_ssps") != [3, 4]:
        raise RuntimeError("VLCGroup child cardinality domain changed")
    if legal.get("mux_word_size") != [48, 64] or legal.get("child_domain_valid_required") is not True:
        raise RuntimeError("VLCGroup mux/child domain contract changed")
    composition = contract.get("composition", {}) or {}
    if (
        composition.get("status") != "EXTERNALIZED_CHILD_BOUNDARY"
        or composition.get("absorption") != "NONE"
        or composition.get("child_modules_instantiated") is not False
        or composition.get("child_source_embedded") is not False
        or composition.get("memory_events_externalized")
        != ["enc_balance", "shifter", "se_size", "frame"]
        or composition.get("ordered_child_sequence")
        != [
            "vlc_unit[0..units_per_group-1]",
            "se_size_fifo_put[0..num_ssps-1]",
            "process_group_enc[conditional]",
        ]
    ):
        raise RuntimeError("VLCGroup externalized-child composition changed")
    bindings = semantics.get("bindings", {}) or {}
    if bindings != {
        "unit_child_role": "vlc_unit",
        "process_child_role": "process_group",
        "se_size_fifo_write": "se_size_mem_write_req",
        "frame_write_event": "frame_mem_write_req",
        "completion": "done",
    }:
        raise RuntimeError("VLCGroup externalized boundary bindings changed")
    function = contract.get("function", {}) or {}
    parameters = _parameters(agent, contract)
    if len(parameters) != 4:
        raise RuntimeError("VLCGroup native ABI must have four parameters")
    parameter_names = [str(item.get("name", "")) for item in parameters]
    if not all(_IDENTIFIER.fullmatch(name) for name in parameter_names):
        raise RuntimeError("VLCGroup parameter name is invalid")
    if not parameters[0].get("pointer") or not parameters[1].get("pointer"):
        raise RuntimeError("VLCGroup config/state parameters must be pointers")
    if str(parameters[2].get("type", "")).strip() != "unsigned char **" or not parameters[2].get("pointer"):
        raise RuntimeError("VLCGroup byte output pointer ABI changed")
    if parameters[3].get("pointer"):
        raise RuntimeError("VLCGroup force_p1_ich2 must remain scalar")
    rtl = contract.get("rtl", {}) or {}
    expected_module = str(rtl.get("module", ""))
    if (
        not _IDENTIFIER.fullmatch(module)
        or module != expected_module
        or not pathlib.Path(candidate_sv).is_file()
    ):
        raise RuntimeError("VLCGroup RTL module identity is invalid")
    expected_candidate_hash = str(rtl.get("candidate_sha256", "")).lower()
    if not _HASH.fullmatch(expected_candidate_hash):
        raise RuntimeError("VLCGroup candidate hash is missing")
    if _path_hash(pathlib.Path(candidate_sv)) != expected_candidate_hash:
        raise RuntimeError("VLCGroup selected candidate bytes changed")
    candidate_text = pathlib.Path(candidate_sv).read_text(
        encoding="utf-8", errors="replace"
    )
    module_match = re.search(
        r"\bmodule\s+([A-Za-z_][A-Za-z0-9_]*)\s*(?:#\s*\(|\()",
        candidate_text,
    )
    if not module_match or module_match.group(1) != module:
        raise RuntimeError("VLCGroup candidate module name changed")
    function_name = str(function.get("name", ""))
    if not _IDENTIFIER.fullmatch(function_name):
        # The spelling is traceability only.  It must be a valid C identifier
        # so the generated declaration can be compiled, but is not admitted by
        # comparing it to a hard-coded function name.
        raise RuntimeError("VLCGroup function identity is invalid")
    caller_declarations = ", ".join(_parameter_declaration(item) for item in parameters)
    alias_call = ", ".join(parameter_names)
    children_by_role: dict[str, dict[str, Any]] = {}
    dependencies = contract.get("dependencies", []) or []
    for dependency in dependencies:
        if not isinstance(dependency, dict):
            raise RuntimeError("VLCGroup dependency record is invalid")
        role = str(dependency.get("role", ""))
        if role == "vlc_unit":
            children_by_role[role] = _validate_dependency(
                agent, dependency, source_dir, role, "bounded_vlc_unit_encode_transition"
            )
        elif role == "process_group":
            children_by_role[role] = _validate_dependency(
                agent, dependency, source_dir, role, "bounded_process_group_encode_transition"
            )
    if set(children_by_role) != {"vlc_unit", "process_group"}:
        raise RuntimeError("VLCGroup requires exactly the pinned VLCUnit and ProcessGroupEnc children")
    ports = list((contract.get("interface", {}) or {}).get("ports", []) or [])
    if not ports:
        raise RuntimeError("VLCGroup RTL interface is missing")
    port_names = [str(item.get("name", "")) for item in ports if isinstance(item, dict)]
    if len(port_names) != len(set(port_names)) or not all(_IDENTIFIER.fullmatch(name) for name in port_names):
        raise RuntimeError("VLCGroup RTL port names are invalid")
    missing = sorted(_required_ports() - set(port_names))
    if missing:
        raise RuntimeError(f"VLCGroup frozen ports are incomplete: {missing}")
    input_port_names = [
        str(item.get("name")) for item in ports if item.get("direction") == "input"
    ]
    output_port_names = [
        str(item.get("name")) for item in ports if item.get("direction") == "output"
    ]
    source_dir.mkdir(parents=True, exist_ok=True)
    safe_module = _safe_identifier(module)
    original = f"{function_name}_original"
    cfg_name, state_name, byte_name, force_name = parameter_names
    paths = {
        "header": source_dir / "dsc_cicd_overlay.h",
        "abi": source_dir / "dsc_cicd_rtl_abi.h",
        "overlay": source_dir / "dsc_cicd_overlay.c",
        "bridge": source_dir / "rtl_bridge.cpp",
        "main": source_dir / "dsc_cicd_main.c",
    }
    paths["abi"].write_text(_abi_source(), encoding="utf-8")
    paths["header"].write_text(_header_source(caller_declarations), encoding="utf-8")
    paths["overlay"].write_text(
        _overlay_source(
            original=original,
            caller_declarations=caller_declarations,
            alias_call=alias_call,
            cfg_name=cfg_name,
            state_name=state_name,
            byte_name=byte_name,
            force_name=force_name,
            children=children_by_role,
            metrics=_metrics_source(agent),
        ),
        encoding="utf-8",
    )
    paths["bridge"].write_text(_bridge_source(safe_module), encoding="utf-8")
    paths["main"].write_text(
        "#include <stdio.h>\n"
        "extern int dsc_cicd_original_main(int, char **);\n"
        "int main(int argc, char **argv) { return dsc_cicd_original_main(argc, argv); }\n",
        encoding="utf-8",
    )

    child_composition = [
        {
            "role": child["role"],
            "function": child["function"],
            "module": child["module"],
            "contract_id": child["contract_id"],
            "contract_sha256": child["contract_sha256"],
            "module_sha256": child["module_sha256"],
        }
        for child in (children_by_role["vlc_unit"], children_by_role["process_group"])
    ]

    def input_binding(name: str) -> str:
        if name in {"clk", "rst_n", "start"}:
            return f"sequential Verilator control::{name}"
        if name.startswith("vlc_unit_") or name.startswith("process_group_"):
            return f"externalized child transaction::{name}"
        if "mem_" in name or name == "frame_mem_write_ready":
            return f"ordered bounded memory service::{name}"
        return f"contract input::{name}"

    return {
        **paths,
        "candidate": pathlib.Path(candidate_sv),
        "composition": {
            "status": "PASS",
            "adapter_kind": "explicit_vlc_group_encode_fsm",
            "caller_parameter_count": len(parameters),
            "rtl_input_count": len(input_port_names),
            "frozen_input_ports": input_port_names,
            "rtl_bindings": [input_binding(name) for name in input_port_names],
            "state_outputs": sorted(output_port_names),
            "child_roles": child_composition,
            "composition_status": "EXTERNALIZED_CHILD_BOUNDARY",
            "ordered_child_sequence": composition["ordered_child_sequence"],
            "se_size_fifo_events_in_source_order": True,
            "child_calls_are_semantic_and_routable": True,
            "simultaneous_child_dispatchers_required": True,
            "c_oracle_uses_deep_private_state_snapshots": True,
            "c_oracle_uses_deep_fifo_frame_and_pointer_snapshots": True,
            "c_oracle_state_is_restored_before_rtl": True,
            "rtl_services_external_fifo_and_frame_memory_requests": True,
            "rtl_runs_sequential_fsm_to_done_with_finite_bound": True,
            "rtl_finite_cycle_bound": _MAX_CYCLES,
            "rtl_legal_and_fatal_flags_compared": True,
            "rtl_return_commits_only_parent_outputs_and_hash_pinned_child_results": True,
            "all_child_event_metadata_compared": True,
            "force_p1_ich2_child_metadata_compared": True,
            "all_fifo_scalar_and_active_memory_bytes_compared": True,
            "byte_out_pointer_cursor_compared": True,
            "source_order_is_clocked_and_bounded": True,
            "residual_symbol_alias_routes_to_dispatcher": True,
            "no_parent_c_output_bypass": True,
            "no_function_name_admission": True,
        },
    }


__all__ = ["write_vlc_group_encode_overlay_sources"]
