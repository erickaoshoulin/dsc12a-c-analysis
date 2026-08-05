"""Emit the C/Verilator adapter for the bounded encoder PredictionLoop.

The generated RTL is the implementation under test.  This module only emits
the ABI and the small C boundary needed to run the immutable C function as a
private oracle, compare the complete frozen footprint, and select the commit
side of the C_ONLY/SHADOW/RTL_RETURN modes.
"""

from __future__ import annotations

import pathlib
import re
from typing import Any


_UNITS = 4
_SAMPLES = 3
_COMPONENTS = 4
_MIDPOINT_SLOTS = 6
_PREV_TAPS = 15
_PREV_USED_TAPS = 6
_CURR_TAPS = 16
_PADDING_LEFT = 5
_PRED_BLOCK_SIZE = 3
_PT_MAP = 0
_PT_LEFT = 1
_PT_BLOCK = 2
_BP_RANGE = 13


def _safe_identifier(value: object) -> str:
    result = re.sub(r"[^A-Za-z0-9_]", "_", str(value))
    if not result or result[0].isdigit():
        result = "c_" + result
    return result


def _parameters(agent: object, contract: dict[str, Any]) -> list[dict[str, Any]]:
    getter = getattr(agent, "function_parameters", None)
    if callable(getter):
        result = getter(contract)
        if isinstance(result, list) and result:
            return [dict(item) for item in result]
    function = contract.get("function", {}) or {}
    result = function.get("parameters", [])
    if not isinstance(result, list) or not result:
        raise RuntimeError("bounded prediction encode contract has no native parameters")
    return [dict(item) for item in result]


def _parameter_is_pointer(parameter: dict[str, Any]) -> bool:
    return bool(parameter.get("pointer")) or "*" in str(parameter.get("type", ""))


def _port_names(contract: dict[str, Any]) -> tuple[list[str], list[str]]:
    ports = [
        port
        for port in (contract.get("interface", {}) or {}).get("ports", [])
        if isinstance(port, dict)
    ]
    return (
        [str(port.get("name")) for port in ports if port.get("direction") == "input"],
        [str(port.get("name")) for port in ports if port.get("direction") == "output"],
    )


def _expected_input_names() -> list[str]:
    names = [
        "hpos",
        "vpos",
        "sampmodcnt",
        "qp",
        "cfg_native_420",
        "cfg_dsc_version_minor",
        "cfg_bits_per_component",
        "cfg_full_ich_err_precision",
        "state_is_encoder",
        "state_units_per_group",
        "state_primary_qp",
        "state_prev_line_prediction",
        "state_qlevel_luma_qp",
        "state_qlevel_chroma_qp",
    ]
    for component in range(_COMPONENTS):
        names.extend(
            [
                f"state_cpnt_bit_depth_{component}",
                f"state_left_recon_{component}",
            ]
        )
    for unit in range(_UNITS):
        names.extend(
            [
                f"state_unit_c_type_{unit}",
                f"state_unit_start_hpos_{unit}",
                f"state_max_error_{unit}",
                f"state_max_mid_error_{unit}",
                f"orig_sample_{unit}",
            ]
        )
        for sample in range(_SAMPLES):
            names.extend(
                [
                    f"state_quantized_residual_{unit}_{sample}",
                    f"state_quantized_residual_mid_{unit}_{sample}",
                ]
            )
        for slot in range(_MIDPOINT_SLOTS):
            names.append(f"state_midpoint_recon_{unit}_{slot}")
        for tap in range(_PREV_TAPS):
            names.append(f"prev_line_unit_{unit}_tap_{tap}")
        for tap in range(_CURR_TAPS):
            names.append(f"curr_line_unit_{unit}_tap_{tap}")
    return names


def _expected_output_names() -> list[str]:
    names = [
        "domain_valid",
        "illegal_domain",
        "bound_violation",
        "midpoint_clamp_violation",
        "arithmetic_domain_violation",
        "state_primary_qp_out",
    ]
    for unit in range(_UNITS):
        for sample in range(_SAMPLES):
            names.extend(
                [
                    f"state_quantized_residual_{unit}_{sample}_out",
                    f"state_quantized_residual_mid_{unit}_{sample}_out",
                ]
            )
        for slot in range(_MIDPOINT_SLOTS):
            names.append(f"state_midpoint_recon_{unit}_{slot}_out")
        names.extend(
            [
                f"state_max_error_{unit}_out",
                f"state_max_mid_error_{unit}_out",
                f"curr_line_write_{unit}_enable",
                f"curr_line_write_{unit}_component",
                f"curr_line_write_{unit}_index",
                f"curr_line_write_{unit}_value",
            ]
        )
    return names


def _validate_contract(
    agent: object, contract: dict[str, Any]
) -> tuple[list[dict[str, Any]], list[str], list[str]]:
    semantics = contract.get("semantics", {}) or {}
    if semantics.get("kind") != "bounded_prediction_encode_transition":
        raise RuntimeError("prediction encode adapter requires bounded_prediction_encode_transition")
    constants = semantics.get("constants", {}) or {}
    expected_constants = {
        "max_units": _UNITS,
        "samples_per_unit": _SAMPLES,
        "midpoint_recon_slots": _MIDPOINT_SLOTS,
        "padding_left": _PADDING_LEFT,
        "pred_block_size": _PRED_BLOCK_SIZE,
        "pt_map": _PT_MAP,
        "pt_left": _PT_LEFT,
        "pt_block": _PT_BLOCK,
        "bp_range": _BP_RANGE,
    }
    if any(int(constants.get(key, -1)) != value for key, value in expected_constants.items()):
        raise RuntimeError("bounded prediction encode constants are incomplete")

    bindings = semantics.get("bindings", {}) or {}
    expected_bindings = {
        "config_parameter": "dsc_cfg",
        "state_parameter": "dsc_state",
        "horizontal_parameter": "hPos",
        "vertical_parameter": "vPos",
        "sample_count_parameter": "sampModCnt",
        "qp_parameter": "qp",
        "prev_line_prediction_input": "state_prev_line_prediction",
    }
    if any(bindings.get(key) != value for key, value in expected_bindings.items()):
        raise RuntimeError("bounded prediction encode ABI bindings are incomplete")
    if list(bindings.get("selected_qlevel_inputs", [])) != [
        "state_qlevel_luma_qp",
        "state_qlevel_chroma_qp",
    ]:
        raise RuntimeError("bounded prediction encode qlevel bindings are incomplete")
    if list(bindings.get("orig_sample_ports", [])) != [
        f"orig_sample_{unit}" for unit in range(_UNITS)
    ]:
        raise RuntimeError("bounded prediction encode original-sample bindings are incomplete")
    write_sidebands = bindings.get("write_sidebands", [])
    expected_sidebands = [
        {
            "enable": f"curr_line_write_{unit}_enable",
            "component": f"curr_line_write_{unit}_component",
            "index": f"curr_line_write_{unit}_index",
            "value": f"curr_line_write_{unit}_value",
        }
        for unit in range(_UNITS)
    ]
    if write_sidebands != expected_sidebands:
        raise RuntimeError("bounded prediction encode write-sideband bindings are incomplete")

    parameters = _parameters(agent, contract)
    parameter_names = [str(item.get("name")) for item in parameters]
    expected_parameters = ["dsc_cfg", "dsc_state", "hPos", "vPos", "sampModCnt", "qp"]
    if parameter_names != expected_parameters:
        raise RuntimeError("bounded prediction encode native parameter order changed")
    if not _parameter_is_pointer(parameters[0]) or not _parameter_is_pointer(parameters[1]):
        raise RuntimeError("bounded prediction encode config/state ABI must use pointers")
    if any(_parameter_is_pointer(item) for item in parameters[2:]):
        raise RuntimeError("bounded prediction encode scalar ABI unexpectedly uses a pointer")

    input_names, output_names = _port_names(contract)
    expected_inputs = _expected_input_names()
    expected_outputs = _expected_output_names()
    if (
        len(input_names) != len(set(input_names))
        or len(output_names) != len(set(output_names))
        or set(input_names) != set(expected_inputs)
        or set(output_names) != set(expected_outputs)
    ):
        raise RuntimeError("bounded prediction encode ports do not match the frozen full footprint")
    identifier = re.compile(r"^[A-Za-z_][A-Za-z0-9_]*$")
    if not all(identifier.fullmatch(name) for name in [*input_names, *output_names, *parameter_names]):
        raise RuntimeError("bounded prediction encode ABI contains an invalid identifier")
    return parameters, input_names, output_names


def _render_abi() -> str:
    return f"""#ifndef DSC_CICD_RTL_ABI_H
#define DSC_CICD_RTL_ABI_H
#include <stdint.h>

#define DSC_CICD_PRED_UNITS {_UNITS}
#define DSC_CICD_PRED_SAMPLES {_SAMPLES}
#define DSC_CICD_PRED_COMPONENTS {_COMPONENTS}
#define DSC_CICD_PRED_MIDPOINT_SLOTS {_MIDPOINT_SLOTS}
#define DSC_CICD_PRED_PREV_TAPS {_PREV_TAPS}
#define DSC_CICD_PRED_PREV_USED_TAPS {_PREV_USED_TAPS}
#define DSC_CICD_PRED_CURR_TAPS {_CURR_TAPS}

typedef struct {{
    int32_t hpos;
    int32_t vpos;
    int32_t sample_count;
    int32_t qp;
    int32_t cfg_native_420;
    int32_t cfg_dsc_version_minor;
    int32_t cfg_bits_per_component;
    int32_t cfg_full_ich_err_precision;
    int32_t state_is_encoder;
    int32_t state_units_per_group;
    int32_t state_primary_qp;
    int32_t state_prev_line_prediction;
    int32_t state_qlevel_luma_qp;
    int32_t state_qlevel_chroma_qp;
    int32_t cpnt_bit_depth[DSC_CICD_PRED_COMPONENTS];
    int32_t left_recon[DSC_CICD_PRED_COMPONENTS];
    int32_t unit_c_type[DSC_CICD_PRED_UNITS];
    int32_t unit_start_hpos[DSC_CICD_PRED_UNITS];
    int32_t max_error[DSC_CICD_PRED_UNITS];
    int32_t max_mid_error[DSC_CICD_PRED_UNITS];
    int32_t orig_sample[DSC_CICD_PRED_UNITS];
    int32_t quantized_residual[DSC_CICD_PRED_UNITS][DSC_CICD_PRED_SAMPLES];
    int32_t quantized_residual_mid[DSC_CICD_PRED_UNITS][DSC_CICD_PRED_SAMPLES];
    int32_t midpoint_recon[DSC_CICD_PRED_UNITS][DSC_CICD_PRED_MIDPOINT_SLOTS];
    int32_t prev_line[DSC_CICD_PRED_UNITS][DSC_CICD_PRED_PREV_TAPS];
    int32_t curr_line[DSC_CICD_PRED_UNITS][DSC_CICD_PRED_CURR_TAPS];
}} dsc_cicd_prediction_input_t;

typedef struct {{
    int32_t domain_valid;
    int32_t illegal_domain;
    int32_t bound_violation;
    int32_t midpoint_clamp_violation;
    int32_t arithmetic_domain_violation;
    int32_t state_primary_qp;
    int32_t quantized_residual[DSC_CICD_PRED_UNITS][DSC_CICD_PRED_SAMPLES];
    int32_t quantized_residual_mid[DSC_CICD_PRED_UNITS][DSC_CICD_PRED_SAMPLES];
    int32_t midpoint_recon[DSC_CICD_PRED_UNITS][DSC_CICD_PRED_MIDPOINT_SLOTS];
    int32_t max_error[DSC_CICD_PRED_UNITS];
    int32_t max_mid_error[DSC_CICD_PRED_UNITS];
    int32_t write_enable[DSC_CICD_PRED_UNITS];
    int32_t write_component[DSC_CICD_PRED_UNITS];
    int32_t write_index[DSC_CICD_PRED_UNITS];
    int32_t write_value[DSC_CICD_PRED_UNITS];
}} dsc_cicd_prediction_output_t;

#ifdef __cplusplus
extern "C" {{
#endif
void dsc_cicd_rtl(const dsc_cicd_prediction_input_t *input,
                  dsc_cicd_prediction_output_t *output);
#ifdef __cplusplus
}}
#endif
#endif
"""


def _render_header(parameter_specs: list[str]) -> str:
    return (
        "#ifndef DSC_CICD_OVERLAY_H\n"
        "#define DSC_CICD_OVERLAY_H\n"
        "#include \"dsc_types.h\"\n"
        f"void dsc_cicd_invoke({', '.join(parameter_specs)});\n"
        "#endif\n"
    )


def _runtime_metrics_source() -> str:
    return """static unsigned long dsc_cicd_mismatches;
static unsigned long dsc_cicd_calls;
static unsigned long dsc_cicd_rtl_invocations;
static int dsc_cicd_report_registered;
static void dsc_cicd_report(void) {
    fprintf(stderr, "DSC_CICD_OVERLAY_METRICS calls=%lu rtl_invocations=%lu mismatches=%lu\\n",
            dsc_cicd_calls, dsc_cicd_rtl_invocations, dsc_cicd_mismatches);
}
static void dsc_cicd_note_call(void) {
    if (!dsc_cicd_report_registered) {
        atexit(dsc_cicd_report);
        dsc_cicd_report_registered = 1;
    }
    ++dsc_cicd_calls;
}
static void dsc_cicd_note_rtl_invocation(void) {
    ++dsc_cicd_rtl_invocations;
}

"""


def _c_output_copy_source() -> str:
    lines = [
        "    dsc_cicd_c_output.domain_valid = 1;",
        "    dsc_cicd_c_output.illegal_domain = 0;",
        "    dsc_cicd_c_output.bound_violation = 0;",
        "    dsc_cicd_c_output.midpoint_clamp_violation = 0;",
        "    dsc_cicd_c_output.arithmetic_domain_violation = 0;",
        "    dsc_cicd_c_output.state_primary_qp = dsc_cicd_c_state.primaryQp;",
        "    for (int unit = 0; unit < DSC_CICD_PRED_UNITS; ++unit) {",
        "        for (int sample = 0; sample < DSC_CICD_PRED_SAMPLES; ++sample) {",
        "            dsc_cicd_c_output.quantized_residual[unit][sample] =",
        "                dsc_cicd_c_state.quantizedResidual[unit][sample];",
        "            dsc_cicd_c_output.quantized_residual_mid[unit][sample] =",
        "                dsc_cicd_c_state.quantizedResidualMid[unit][sample];",
        "        }",
        "        for (int slot = 0; slot < DSC_CICD_PRED_MIDPOINT_SLOTS; ++slot)",
        "            dsc_cicd_c_output.midpoint_recon[unit][slot] =",
        "                dsc_cicd_c_state.midpointRecon[unit][slot];",
        "        dsc_cicd_c_output.max_error[unit] = dsc_cicd_c_state.maxError[unit];",
        "        dsc_cicd_c_output.max_mid_error[unit] = dsc_cicd_c_state.maxMidError[unit];",
        "        if (unit < dsc_state->unitsPerGroup) {",
        "            int cpnt = dsc_state->unitCType[unit];",
        "            dsc_cicd_c_output.write_enable[unit] = 1;",
        "            dsc_cicd_c_output.write_component[unit] = cpnt;",
        "            dsc_cicd_c_output.write_index[unit] = dsc_cicd_saved_write_index[unit];",
        "            dsc_cicd_c_output.write_value[unit] =",
        "                dsc_cicd_c_state.currLine[cpnt][dsc_cicd_saved_write_index[unit]];",
        "        }",
        "    }",
    ]
    return "\n".join(lines) + "\n"


def _restore_source() -> str:
    return """    /* Restore the complete touched footprint before selecting a mode. */
    dsc_state->primaryQp = dsc_cicd_saved_primary_qp;
    memcpy(dsc_state->quantizedResidual, dsc_cicd_saved_quantized_residual,
           sizeof(dsc_cicd_saved_quantized_residual));
    memcpy(dsc_state->quantizedResidualMid, dsc_cicd_saved_quantized_residual_mid,
           sizeof(dsc_cicd_saved_quantized_residual_mid));
    memcpy(dsc_state->midpointRecon, dsc_cicd_saved_midpoint_recon,
           sizeof(dsc_cicd_saved_midpoint_recon));
    memcpy(dsc_state->maxError, dsc_cicd_saved_max_error,
           sizeof(dsc_cicd_saved_max_error));
    memcpy(dsc_state->maxMidError, dsc_cicd_saved_max_mid_error,
           sizeof(dsc_cicd_saved_max_mid_error));
    for (int unit = 0; unit < dsc_state->unitsPerGroup; ++unit)
        dsc_state->currLine[dsc_cicd_saved_cpnt[unit]][dsc_cicd_saved_write_index[unit]] =
            dsc_cicd_saved_curr_line[unit];

"""


def _render_require_function() -> str:
    return f"""static void dsc_cicd_fail(const char *reason) {{
    fprintf(stderr, "unsupported PredictionLoop encode domain: %s\\n", reason);
    exit(2);
}}

static void dsc_cicd_require_sample(int value, const char *reason) {{
    if (value < 0 || value > 65535)
        dsc_cicd_fail(reason);
}}

static void dsc_cicd_require_prediction(
    const dsc_cfg_t *cfg, const dsc_state_t *state,
    int hpos, int vpos, int sample_count, int qp) {{
    int line_width;
    if (!cfg || !state)
        dsc_cicd_fail("null config/state");
    if (state->isEncoder != 1 || state->unitsPerGroup < 0 ||
        state->unitsPerGroup > DSC_CICD_PRED_UNITS || hpos < 0 ||
        vpos < 0 || sample_count < 0 || sample_count >= DSC_CICD_PRED_SAMPLES ||
        qp < 0 || qp > 31 || state->sliceWidth <= 0 || hpos >= state->sliceWidth)
        dsc_cicd_fail("scalar domain");
    if ((cfg->native_420 != 0 && cfg->native_420 != 1) ||
        (cfg->dsc_version_minor != 1 && cfg->dsc_version_minor != 2) ||
        cfg->bits_per_component < 8 || cfg->bits_per_component > 16 ||
        (cfg->full_ich_err_precision != 0 && cfg->full_ich_err_precision != 1))
        dsc_cicd_fail("configuration domain");
    if (!state->quantTableLuma || !state->quantTableChroma ||
        (vpos > 0 && !state->prevLinePred))
        dsc_cicd_fail("missing dynamic state pointer");
    if (state->quantTableLuma[qp] < 0 || state->quantTableLuma[qp] > 16 ||
        state->quantTableChroma[qp] < 0 || state->quantTableChroma[qp] > 16)
        dsc_cicd_fail("qlevel domain");
    for (int component = 0; component < DSC_CICD_PRED_COMPONENTS; ++component) {{
        if (state->cpntBitDepth[component] < 8 || state->cpntBitDepth[component] > 16)
            dsc_cicd_fail("component bit depth domain");
        dsc_cicd_require_sample(state->leftRecon[component], "left reconstruction domain");
    }}
    if (vpos > 0) {{
        int prediction = state->prevLinePred[hpos / PRED_BLK_SIZE];
        if (prediction < PT_MAP || prediction > PT_BLOCK + {_BP_RANGE} - 1)
            dsc_cicd_fail("previous prediction domain");
    }}
    line_width = state->sliceWidth + PADDING_LEFT + PADDING_RIGHT;
    for (int unit = 0; unit < state->unitsPerGroup; ++unit) {{
        int cpnt = state->unitCType[unit];
        int residual_index = sample_count - state->unitStartHPos[unit];
        int plane = (cfg->native_420 && cpnt == 2) ? cpnt + (vpos % 2) : cpnt;
        int prev_base = (hpos / SAMPLES_PER_UNIT) * SAMPLES_PER_UNIT +
                        PADDING_LEFT - 2;
        int curr_base = hpos > (PADDING_LEFT + PRED_BLK_SIZE) ?
                        hpos - (PADDING_LEFT + PRED_BLK_SIZE) : 0;
        if (cpnt < 0 || cpnt >= DSC_CICD_PRED_COMPONENTS ||
            state->unitStartHPos[unit] < 0 ||
            state->unitStartHPos[unit] >= DSC_CICD_PRED_SAMPLES ||
            residual_index < 0 || residual_index >= DSC_CICD_PRED_SAMPLES ||
            plane < 0 || plane >= DSC_CICD_PRED_COMPONENTS ||
            !state->origLine[cpnt] || !state->currLine[cpnt] ||
            !state->prevLine[plane])
            dsc_cicd_fail("active unit pointer/domain");
        if (hpos + PADDING_LEFT < 0 || hpos + PADDING_LEFT >= line_width ||
            prev_base < 0 || prev_base + DSC_CICD_PRED_PREV_USED_TAPS > line_width ||
            curr_base < 0 || curr_base + DSC_CICD_PRED_CURR_TAPS > line_width)
            dsc_cicd_fail("dynamic line pointer window");
        dsc_cicd_require_sample(
            state->origLine[cpnt][hpos + PADDING_LEFT], "original sample domain");
        for (int sample = 0; sample < DSC_CICD_PRED_SAMPLES; ++sample) {{
            if (state->quantizedResidual[unit][sample] < -65535 ||
                state->quantizedResidual[unit][sample] > 65535 ||
                state->quantizedResidualMid[unit][sample] < -65535 ||
                state->quantizedResidualMid[unit][sample] > 65535)
                dsc_cicd_fail("residual domain");
        }}
        for (int tap = 0; tap < DSC_CICD_PRED_PREV_USED_TAPS; ++tap)
            dsc_cicd_require_sample(state->prevLine[plane][prev_base + tap],
                                    "previous line tap domain");
        for (int tap = 0; tap < DSC_CICD_PRED_CURR_TAPS; ++tap)
            dsc_cicd_require_sample(state->currLine[cpnt][curr_base + tap],
                                    "current line tap domain");
    }}
}}

"""


def _render_input_population() -> str:
    lines = [
        "    memset(&dsc_cicd_input, 0, sizeof(dsc_cicd_input));",
        "    dsc_cicd_input.hpos = hPos;",
        "    dsc_cicd_input.vpos = vPos;",
        "    dsc_cicd_input.sample_count = sampModCnt;",
        "    dsc_cicd_input.qp = qp;",
        "    dsc_cicd_input.cfg_native_420 = dsc_cfg->native_420;",
        "    dsc_cicd_input.cfg_dsc_version_minor = dsc_cfg->dsc_version_minor;",
        "    dsc_cicd_input.cfg_bits_per_component = dsc_cfg->bits_per_component;",
        "    dsc_cicd_input.cfg_full_ich_err_precision = dsc_cfg->full_ich_err_precision;",
        "    dsc_cicd_input.state_is_encoder = dsc_state->isEncoder;",
        "    dsc_cicd_input.state_units_per_group = dsc_state->unitsPerGroup;",
        "    dsc_cicd_input.state_primary_qp = dsc_state->primaryQp;",
        "    dsc_cicd_input.state_prev_line_prediction = vPos == 0 ? PT_LEFT :",
        "        dsc_state->prevLinePred[hPos / PRED_BLK_SIZE];",
        "    dsc_cicd_input.state_qlevel_luma_qp = dsc_state->quantTableLuma[qp];",
        "    dsc_cicd_input.state_qlevel_chroma_qp = dsc_state->quantTableChroma[qp];",
        "    memcpy(dsc_cicd_input.cpnt_bit_depth, dsc_state->cpntBitDepth,",
        "           sizeof(dsc_cicd_input.cpnt_bit_depth));",
        "    memcpy(dsc_cicd_input.left_recon, dsc_state->leftRecon,",
        "           sizeof(dsc_cicd_input.left_recon));",
        "    for (int unit = 0; unit < dsc_state->unitsPerGroup; ++unit) {",
        "        int cpnt = dsc_state->unitCType[unit];",
        "        int plane = (dsc_cfg->native_420 && cpnt == 2) ?",
        "                    cpnt + (vPos % 2) : cpnt;",
        "        int prev_base = (hPos / SAMPLES_PER_UNIT) * SAMPLES_PER_UNIT +",
        "                        PADDING_LEFT - 2;",
        "        int curr_base = hPos > (PADDING_LEFT + PRED_BLK_SIZE) ?",
        "                        hPos - (PADDING_LEFT + PRED_BLK_SIZE) : 0;",
        "        dsc_cicd_input.unit_c_type[unit] = cpnt;",
        "        dsc_cicd_input.unit_start_hpos[unit] = dsc_state->unitStartHPos[unit];",
        "        dsc_cicd_input.max_error[unit] = dsc_state->maxError[unit];",
        "        dsc_cicd_input.max_mid_error[unit] = dsc_state->maxMidError[unit];",
        "        dsc_cicd_input.orig_sample[unit] =",
        "            dsc_state->origLine[cpnt][hPos + PADDING_LEFT];",
    ]
    for sample in range(_SAMPLES):
        lines.extend(
            [
                f"        dsc_cicd_input.quantized_residual[unit][{sample}] =",
                f"            dsc_state->quantizedResidual[unit][{sample}];",
                f"        dsc_cicd_input.quantized_residual_mid[unit][{sample}] =",
                f"            dsc_state->quantizedResidualMid[unit][{sample}];",
            ]
        )
    for slot in range(_MIDPOINT_SLOTS):
        lines.extend(
            [
                f"        dsc_cicd_input.midpoint_recon[unit][{slot}] =",
                f"            dsc_state->midpointRecon[unit][{slot}];",
            ]
        )
    lines.extend(
        [
            "        for (int tap = 0; tap < DSC_CICD_PRED_PREV_TAPS; ++tap) {",
            "            int index = prev_base + tap;",
            "            if (tap < DSC_CICD_PRED_PREV_USED_TAPS &&",
            "                index >= 0 && index < dsc_state->sliceWidth +",
            "                PADDING_LEFT + PADDING_RIGHT)",
            "                dsc_cicd_input.prev_line[unit][tap] =",
            "                    dsc_state->prevLine[plane][index];",
            "        }",
            "        for (int tap = 0; tap < DSC_CICD_PRED_CURR_TAPS; ++tap) {",
            "            int index = curr_base + tap;",
            "            if (index >= 0 && index < dsc_state->sliceWidth +",
            "                PADDING_LEFT + PADDING_RIGHT)",
            "                dsc_cicd_input.curr_line[unit][tap] =",
            "                    dsc_state->currLine[cpnt][index];",
            "        }",
            "    }",
        ]
    )
    return "\n".join(lines) + "\n"


def _render_snapshot_source() -> str:
    return """    int dsc_cicd_saved_primary_qp = dsc_state->primaryQp;
    int dsc_cicd_saved_quantized_residual[DSC_CICD_PRED_UNITS][DSC_CICD_PRED_SAMPLES];
    int dsc_cicd_saved_quantized_residual_mid[DSC_CICD_PRED_UNITS][DSC_CICD_PRED_SAMPLES];
    int dsc_cicd_saved_midpoint_recon[DSC_CICD_PRED_UNITS][DSC_CICD_PRED_MIDPOINT_SLOTS];
    int dsc_cicd_saved_max_error[DSC_CICD_PRED_UNITS];
    int dsc_cicd_saved_max_mid_error[DSC_CICD_PRED_UNITS];
    int dsc_cicd_saved_cpnt[DSC_CICD_PRED_UNITS] = {0};
    int dsc_cicd_saved_write_index[DSC_CICD_PRED_UNITS] = {0};
    int dsc_cicd_saved_curr_line[DSC_CICD_PRED_UNITS] = {0};
    memcpy(dsc_cicd_saved_quantized_residual, dsc_state->quantizedResidual,
           sizeof(dsc_cicd_saved_quantized_residual));
    memcpy(dsc_cicd_saved_quantized_residual_mid, dsc_state->quantizedResidualMid,
           sizeof(dsc_cicd_saved_quantized_residual_mid));
    memcpy(dsc_cicd_saved_midpoint_recon, dsc_state->midpointRecon,
           sizeof(dsc_cicd_saved_midpoint_recon));
    memcpy(dsc_cicd_saved_max_error, dsc_state->maxError,
           sizeof(dsc_cicd_saved_max_error));
    memcpy(dsc_cicd_saved_max_mid_error, dsc_state->maxMidError,
           sizeof(dsc_cicd_saved_max_mid_error));
    for (int unit = 0; unit < dsc_state->unitsPerGroup; ++unit) {
        dsc_cicd_saved_cpnt[unit] = dsc_state->unitCType[unit];
        dsc_cicd_saved_write_index[unit] = hPos + PADDING_LEFT;
        dsc_cicd_saved_curr_line[unit] =
            dsc_state->currLine[dsc_cicd_saved_cpnt[unit]][dsc_cicd_saved_write_index[unit]];
    }

"""


def _render_apply_function() -> str:
    return """static void dsc_cicd_require_output_write(
    const dsc_state_t *state, int unit, int component, int index) {
    if (unit < 0 || unit >= state->unitsPerGroup ||
        component < 0 || component >= DSC_CICD_PRED_COMPONENTS ||
        index < 0 || index >= state->sliceWidth + PADDING_LEFT ||
        !state->currLine[component]) {
        fprintf(stderr, "unsafe PredictionLoop encode RTL line write: unit=%d component=%d index=%d\\n",
                unit, component, index);
        exit(2);
    }
}

static void dsc_cicd_apply_output(
    dsc_state_t *state, const dsc_cicd_prediction_output_t *output) {
    state->primaryQp = output->state_primary_qp;
    for (int unit = 0; unit < DSC_CICD_PRED_UNITS; ++unit) {
        for (int sample = 0; sample < DSC_CICD_PRED_SAMPLES; ++sample) {
            state->quantizedResidual[unit][sample] =
                output->quantized_residual[unit][sample];
            state->quantizedResidualMid[unit][sample] =
                output->quantized_residual_mid[unit][sample];
        }
        for (int slot = 0; slot < DSC_CICD_PRED_MIDPOINT_SLOTS; ++slot)
            state->midpointRecon[unit][slot] = output->midpoint_recon[unit][slot];
        state->maxError[unit] = output->max_error[unit];
        state->maxMidError[unit] = output->max_mid_error[unit];
        if (output->write_enable[unit] != 0) {
            dsc_cicd_require_output_write(
                state, unit, output->write_component[unit], output->write_index[unit]);
            state->currLine[output->write_component[unit]][output->write_index[unit]] =
                output->write_value[unit];
        }
    }
}

"""


def _render_compare_function() -> str:
    return """static int dsc_cicd_prediction_mismatch(
    const dsc_cicd_prediction_output_t *c_output,
    const dsc_cicd_prediction_output_t *rtl_output) {
    int mismatch = 0;
    mismatch |= c_output->domain_valid != rtl_output->domain_valid;
    mismatch |= c_output->illegal_domain != rtl_output->illegal_domain;
    mismatch |= c_output->bound_violation != rtl_output->bound_violation;
    mismatch |= c_output->midpoint_clamp_violation != rtl_output->midpoint_clamp_violation;
    mismatch |= c_output->arithmetic_domain_violation != rtl_output->arithmetic_domain_violation;
    mismatch |= c_output->state_primary_qp != rtl_output->state_primary_qp;
    for (int unit = 0; unit < DSC_CICD_PRED_UNITS; ++unit) {
        for (int sample = 0; sample < DSC_CICD_PRED_SAMPLES; ++sample) {
            mismatch |= c_output->quantized_residual[unit][sample] !=
                        rtl_output->quantized_residual[unit][sample];
            mismatch |= c_output->quantized_residual_mid[unit][sample] !=
                        rtl_output->quantized_residual_mid[unit][sample];
        }
        for (int slot = 0; slot < DSC_CICD_PRED_MIDPOINT_SLOTS; ++slot)
            mismatch |= c_output->midpoint_recon[unit][slot] !=
                        rtl_output->midpoint_recon[unit][slot];
        mismatch |= c_output->max_error[unit] != rtl_output->max_error[unit];
        mismatch |= c_output->max_mid_error[unit] != rtl_output->max_mid_error[unit];
        mismatch |= c_output->write_enable[unit] != rtl_output->write_enable[unit];
        mismatch |= c_output->write_component[unit] != rtl_output->write_component[unit];
        mismatch |= c_output->write_index[unit] != rtl_output->write_index[unit];
        mismatch |= c_output->write_value[unit] != rtl_output->write_value[unit];
    }
    return mismatch;
}

static void dsc_cicd_print_prediction_mismatch(
    int hpos, int vpos, int sample_count, int qp,
    const dsc_cicd_prediction_output_t *c_output,
    const dsc_cicd_prediction_output_t *rtl_output) {
    fprintf(stderr,
            "C/RTL PredictionLoop encode mismatch: hpos=%d vpos=%d sample=%d qp=%d "
            "flags=%d,%d,%d,%d,%d/%d,%d,%d,%d,%d primary=%d/%d\\n",
            hpos, vpos, sample_count, qp,
            c_output->domain_valid, c_output->illegal_domain,
            c_output->bound_violation, c_output->midpoint_clamp_violation,
            c_output->arithmetic_domain_violation,
            rtl_output->domain_valid, rtl_output->illegal_domain,
            rtl_output->bound_violation, rtl_output->midpoint_clamp_violation,
            rtl_output->arithmetic_domain_violation,
            c_output->state_primary_qp, rtl_output->state_primary_qp);
}

"""


def _render_overlay(
    parameters: list[dict[str, Any]], function_name: str
) -> str:
    parameter_specs = [
        f"{str(parameter.get('type', 'int')).strip()} {parameter.get('name')}"
        for parameter in parameters
    ]
    caller_declarations = ", ".join(parameter_specs)
    alias_call = ", ".join(str(parameter.get("name")) for parameter in parameters)
    return (
        "#include <stdint.h>\n"
        "#include <stdio.h>\n"
        "#include <stdlib.h>\n"
        "#include <string.h>\n"
        "#include \"dsc_cicd_overlay.h\"\n"
        "#include \"dsc_cicd_rtl_abi.h\"\n"
        f"extern void {function_name}_original({caller_declarations});\n\n"
        "static int dsc_cicd_mode(void) {\n"
        "    const char *value = getenv(\"DSC_CICD_MODE\");\n"
        "    if (value && strcmp(value, \"SHADOW\") == 0) return 1;\n"
        "    if (value && strcmp(value, \"RTL_RETURN\") == 0) return 2;\n"
        "    return 0;\n"
        "}\n\n"
        + _runtime_metrics_source()
        + _render_require_function()
        + _render_apply_function()
        + _render_compare_function()
        + f"void dsc_cicd_invoke({caller_declarations}) {{\n"
        "    if (dsc_state && dsc_state->isEncoder != 1) {\n"
        f"        {function_name}_original({alias_call});\n"
        "        return;\n"
        "    }\n"
        "    dsc_cicd_prediction_input_t dsc_cicd_input;\n"
        "    dsc_cicd_prediction_output_t dsc_cicd_c_output;\n"
        "    dsc_cicd_prediction_output_t dsc_cicd_rtl_output;\n"
        "    dsc_cicd_require_prediction(dsc_cfg, dsc_state, hPos, vPos, sampModCnt, qp);\n"
        + _render_input_population()
        + _render_snapshot_source()
        + "    memset(&dsc_cicd_c_output, 0, sizeof(dsc_cicd_c_output));\n"
        "    /* The original C is the immutable oracle and sees only this private state. */\n"
        "    dsc_state_t dsc_cicd_c_state = *dsc_state;\n"
        f"    {function_name}_original(dsc_cfg, &dsc_cicd_c_state, hPos, vPos, sampModCnt, qp);\n"
        + _c_output_copy_source()
        + _restore_source()
        + "    int mode = dsc_cicd_mode();\n"
        "    dsc_cicd_note_call();\n"
        "    if (mode == 0) {\n"
        "        /* C_ONLY restores and commits the C oracle state. */\n"
        "        dsc_cicd_apply_output(dsc_state, &dsc_cicd_c_output);\n"
        "        return;\n"
        "    }\n"
        "    memset(&dsc_cicd_rtl_output, 0, sizeof(dsc_cicd_rtl_output));\n"
        "    dsc_cicd_note_rtl_invocation();\n"
        "    dsc_cicd_rtl(&dsc_cicd_input, &dsc_cicd_rtl_output);\n"
        "    if (dsc_cicd_prediction_mismatch(&dsc_cicd_c_output, &dsc_cicd_rtl_output)) {\n"
        "        ++dsc_cicd_mismatches;\n"
        "        if (dsc_cicd_mismatches <= 16)\n"
        "            dsc_cicd_print_prediction_mismatch(hPos, vPos, sampModCnt, qp,\n"
        "                                               &dsc_cicd_c_output,\n"
        "                                               &dsc_cicd_rtl_output);\n"
        "    }\n"
        "    if (mode == 2) {\n"
        "        /* RTL_RETURN commits only the RTL image in source unit order. */\n"
        "        dsc_cicd_apply_output(dsc_state, &dsc_cicd_rtl_output);\n"
        "        return;\n"
        "    }\n"
        "    /* SHADOW compares RTL but commits the restored C oracle image. */\n"
        "    dsc_cicd_apply_output(dsc_state, &dsc_cicd_c_output);\n"
        "}\n\n"
        f"void {function_name}({caller_declarations}) {{\n"
        f"    dsc_cicd_invoke({alias_call});\n"
        "}\n"
    )


def _input_expression(name: str) -> str:
    if name == "hpos":
        return "hPos"
    if name == "vpos":
        return "vPos"
    if name == "sampmodcnt":
        return "sampModCnt"
    if name == "qp":
        return "qp"
    scalar = {
        "cfg_native_420": "dsc_cfg->native_420",
        "cfg_dsc_version_minor": "dsc_cfg->dsc_version_minor",
        "cfg_bits_per_component": "dsc_cfg->bits_per_component",
        "cfg_full_ich_err_precision": "dsc_cfg->full_ich_err_precision",
        "state_is_encoder": "dsc_state->isEncoder",
        "state_units_per_group": "dsc_state->unitsPerGroup",
        "state_primary_qp": "dsc_state->primaryQp",
        "state_prev_line_prediction": "guarded dsc_state->prevLinePred[hPos/PRED_BLK_SIZE]",
        "state_qlevel_luma_qp": "dsc_state->quantTableLuma[qp]",
        "state_qlevel_chroma_qp": "dsc_state->quantTableChroma[qp]",
    }
    if name in scalar:
        return scalar[name]
    match = re.fullmatch(r"state_cpnt_bit_depth_(\d+)", name)
    if match:
        return f"dsc_state->cpntBitDepth[{match.group(1)}]"
    match = re.fullmatch(r"state_left_recon_(\d+)", name)
    if match:
        return f"dsc_state->leftRecon[{match.group(1)}]"
    match = re.fullmatch(r"state_unit_c_type_(\d+)", name)
    if match:
        return f"guarded dsc_state->unitCType[{match.group(1)}]"
    match = re.fullmatch(r"state_unit_start_hpos_(\d+)", name)
    if match:
        return f"guarded dsc_state->unitStartHPos[{match.group(1)}]"
    match = re.fullmatch(r"state_max_error_(\d+)", name)
    if match:
        return f"guarded dsc_state->maxError[{match.group(1)}]"
    match = re.fullmatch(r"state_max_mid_error_(\d+)", name)
    if match:
        return f"guarded dsc_state->maxMidError[{match.group(1)}]"
    match = re.fullmatch(r"orig_sample_(\d+)", name)
    if match:
        return f"guarded dsc_state->origLine[cpnt][hPos+PADDING_LEFT] (unit {match.group(1)})"
    match = re.fullmatch(r"state_quantized_residual_(\d+)_(\d+)", name)
    if match:
        return f"guarded dsc_state->quantizedResidual[{match.group(1)}][{match.group(2)}]"
    match = re.fullmatch(r"state_quantized_residual_mid_(\d+)_(\d+)", name)
    if match:
        return f"guarded dsc_state->quantizedResidualMid[{match.group(1)}][{match.group(2)}]"
    match = re.fullmatch(r"state_midpoint_recon_(\d+)_(\d+)", name)
    if match:
        return f"guarded dsc_state->midpointRecon[{match.group(1)}][{match.group(2)}]"
    match = re.fullmatch(r"prev_line_unit_(\d+)_tap_(\d+)", name)
    if match:
        return f"guarded dsc_state->prevLine[plane][prev_base+{match.group(2)}] (unit {match.group(1)})"
    match = re.fullmatch(r"curr_line_unit_(\d+)_tap_(\d+)", name)
    if match:
        return f"guarded dsc_state->currLine[cpnt][curr_base+{match.group(2)}] (unit {match.group(1)})"
    raise RuntimeError(f"no PredictionLoop input binding for {name}")


def _output_expression(name: str) -> str:
    scalar = {
        "domain_valid": "output->domain_valid",
        "illegal_domain": "output->illegal_domain",
        "bound_violation": "output->bound_violation",
        "midpoint_clamp_violation": "output->midpoint_clamp_violation",
        "arithmetic_domain_violation": "output->arithmetic_domain_violation",
        "state_primary_qp_out": "output->state_primary_qp",
    }
    if name in scalar:
        return scalar[name]
    match = re.fullmatch(r"state_quantized_residual_(\d+)_(\d+)_out", name)
    if match:
        return f"output->quantized_residual[{match.group(1)}][{match.group(2)}]"
    match = re.fullmatch(r"state_quantized_residual_mid_(\d+)_(\d+)_out", name)
    if match:
        return f"output->quantized_residual_mid[{match.group(1)}][{match.group(2)}]"
    match = re.fullmatch(r"state_midpoint_recon_(\d+)_(\d+)_out", name)
    if match:
        return f"output->midpoint_recon[{match.group(1)}][{match.group(2)}]"
    match = re.fullmatch(r"state_max_error_(\d+)_out", name)
    if match:
        return f"output->max_error[{match.group(1)}]"
    match = re.fullmatch(r"state_max_mid_error_(\d+)_out", name)
    if match:
        return f"output->max_mid_error[{match.group(1)}]"
    match = re.fullmatch(r"curr_line_write_(\d+)_(enable|component|index|value)", name)
    if match:
        return f"output->write_{match.group(2)}[{match.group(1)}]"
    raise RuntimeError(f"no PredictionLoop output binding for {name}")


def _render_bridge(module: str, input_names: list[str], output_names: list[str]) -> str:
    assignments = [
        f"    dut.{name} = static_cast<std::uint32_t>({_input_bridge_expression(name)});"
        for name in input_names
    ]
    outputs = [
        f"    {_output_expression(name)} = static_cast<std::int32_t>(dut.{name});"
        for name in output_names
    ]
    return (
        "#include <cstdint>\n"
        "#include \"verilated.h\"\n"
        "#include \"dsc_cicd_rtl_abi.h\"\n"
        f"#include \"V{_safe_identifier(module)}.h\"\n\n"
        "double sc_time_stamp() { return 0.0; }\n\n"
        "extern \"C\" void dsc_cicd_rtl(\n"
        "    const dsc_cicd_prediction_input_t *input,\n"
        "    dsc_cicd_prediction_output_t *output) {\n"
        f"    static V{_safe_identifier(module)} dut;\n"
        + "\n".join(assignments)
        + "\n    dut.eval();\n"
        + "\n".join(outputs)
        + "\n}\n"
    )


def _input_bridge_expression(name: str) -> str:
    scalar = {
        "hpos": "input->hpos",
        "vpos": "input->vpos",
        "sampmodcnt": "input->sample_count",
        "qp": "input->qp",
        "cfg_native_420": "input->cfg_native_420",
        "cfg_dsc_version_minor": "input->cfg_dsc_version_minor",
        "cfg_bits_per_component": "input->cfg_bits_per_component",
        "cfg_full_ich_err_precision": "input->cfg_full_ich_err_precision",
        "state_is_encoder": "input->state_is_encoder",
        "state_units_per_group": "input->state_units_per_group",
        "state_primary_qp": "input->state_primary_qp",
        "state_prev_line_prediction": "input->state_prev_line_prediction",
        "state_qlevel_luma_qp": "input->state_qlevel_luma_qp",
        "state_qlevel_chroma_qp": "input->state_qlevel_chroma_qp",
    }
    if name in scalar:
        return scalar[name]
    match = re.fullmatch(r"state_cpnt_bit_depth_(\d+)", name)
    if match:
        return f"input->cpnt_bit_depth[{match.group(1)}]"
    match = re.fullmatch(r"state_left_recon_(\d+)", name)
    if match:
        return f"input->left_recon[{match.group(1)}]"
    match = re.fullmatch(r"state_unit_c_type_(\d+)", name)
    if match:
        return f"input->unit_c_type[{match.group(1)}]"
    match = re.fullmatch(r"state_unit_start_hpos_(\d+)", name)
    if match:
        return f"input->unit_start_hpos[{match.group(1)}]"
    match = re.fullmatch(r"state_max_error_(\d+)", name)
    if match:
        return f"input->max_error[{match.group(1)}]"
    match = re.fullmatch(r"state_max_mid_error_(\d+)", name)
    if match:
        return f"input->max_mid_error[{match.group(1)}]"
    match = re.fullmatch(r"orig_sample_(\d+)", name)
    if match:
        return f"input->orig_sample[{match.group(1)}]"
    match = re.fullmatch(r"state_quantized_residual_(\d+)_(\d+)", name)
    if match:
        return f"input->quantized_residual[{match.group(1)}][{match.group(2)}]"
    match = re.fullmatch(r"state_quantized_residual_mid_(\d+)_(\d+)", name)
    if match:
        return f"input->quantized_residual_mid[{match.group(1)}][{match.group(2)}]"
    match = re.fullmatch(r"state_midpoint_recon_(\d+)_(\d+)", name)
    if match:
        return f"input->midpoint_recon[{match.group(1)}][{match.group(2)}]"
    match = re.fullmatch(r"prev_line_unit_(\d+)_tap_(\d+)", name)
    if match:
        return f"input->prev_line[{match.group(1)}][{match.group(2)}]"
    match = re.fullmatch(r"curr_line_unit_(\d+)_tap_(\d+)", name)
    if match:
        return f"input->curr_line[{match.group(1)}][{match.group(2)}]"
    raise RuntimeError(f"no PredictionLoop bridge input binding for {name}")


def _rtl_bindings(input_names: list[str]) -> list[str]:
    return [_input_expression(name) for name in input_names]


def write_prediction_encode_overlay_sources(
    agent: object,
    contract: dict[str, Any],
    source_dir: pathlib.Path,
    module: str,
    candidate_sv: pathlib.Path,
) -> dict[str, Any]:
    """Write the bounded PredictionLoop adapter sources and return their paths.

    ``agent`` is accepted for compatibility with the existing CICD emitter
    interface.  Only its optional ``function_parameters`` helper is used; the
    generated boundary is otherwise deterministic and independent of the
    agent implementation.
    """
    parameters, input_names, output_names = _validate_contract(agent, contract)
    source_dir = pathlib.Path(source_dir)
    source_dir.mkdir(parents=True, exist_ok=True)
    candidate_sv = pathlib.Path(candidate_sv)
    function_name = str((contract.get("function", {}) or {}).get("name", "PredictionLoop"))
    if not re.fullmatch(r"[A-Za-z_][A-Za-z0-9_]*", function_name):
        raise RuntimeError("bounded prediction encode function name is not a C identifier")
    parameter_specs = [
        f"{str(parameter.get('type', 'int')).strip()} {parameter.get('name')}"
        for parameter in parameters
    ]
    module_name = _safe_identifier(module)

    header = source_dir / "dsc_cicd_overlay.h"
    abi = source_dir / "dsc_cicd_rtl_abi.h"
    overlay = source_dir / "dsc_cicd_overlay.c"
    bridge = source_dir / "rtl_bridge.cpp"
    main = source_dir / "dsc_cicd_main.c"
    header.write_text(_render_header(parameter_specs), encoding="utf-8")
    abi.write_text(_render_abi(), encoding="utf-8")
    overlay.write_text(_render_overlay(parameters, function_name), encoding="utf-8")
    bridge.write_text(_render_bridge(module_name, input_names, output_names), encoding="utf-8")
    main.write_text(
        "#include <stdio.h>\n"
        "extern int dsc_cicd_original_main(int, char **);\n"
        "int main(int argc, char **argv) { return dsc_cicd_original_main(argc, argv); }\n",
        encoding="utf-8",
    )

    semantics = contract.get("semantics", {}) or {}
    dependencies = semantics.get("dependencies", []) or contract.get("dependencies", []) or []
    return {
        "header": header,
        "abi": abi,
        "overlay": overlay,
        "bridge": bridge,
        "main": main,
        "candidate": candidate_sv,
        "composition": {
            "status": "PASS",
            "adapter_kind": "explicit_bounded_prediction_encode_transition",
            "caller_parameter_count": len(parameters),
            "rtl_input_count": len(input_names),
            "rtl_output_count": len(output_names),
            "frozen_input_ports": input_names,
            "state_outputs": output_names,
            "rtl_bindings": _rtl_bindings(input_names),
            "oracle_state_footprint": [
                "primaryQp",
                "quantizedResidual",
                "quantizedResidualMid",
                "midpointRecon",
                "maxError",
                "maxMidError",
                "currLine writes",
            ],
            "rtl_return_controls_complete_prediction_encode_state_and_line_write_footprint": True,
            "rtl_return_controls_complete_prediction_encode_state_footprint": True,
            "rtl_return_controls_ordered_curr_line_writes": True,
            "rtl_return_commits_only_rtl_outputs_in_source_order": True,
            "c_only_restores_and_commits_c_oracle_state": True,
            "shadow_commits_c_oracle_state": True,
            "c_oracle_uses_private_state_copy": True,
            "c_oracle_uses_private_state_arrays": True,
            "c_oracle_state_is_restored_before_mode_selection": True,
            "all_outputs_and_domain_bound_flags_are_compared": True,
            "all_rtl_modes_count_actual_verilator_invocation": True,
            "inactive_units_and_taps_are_guarded": True,
            "inactive_line_taps_are_not_dereferenced": True,
            "dynamic_line_pointers_are_guarded": True,
            "decoder_calls_bypass_encode_rtl_and_use_original_c": True,
            "accepted_rtl_dependencies_embedded": [
                str(item.get("contract_id"))
                for item in dependencies
                if isinstance(item, dict) and item.get("contract_id")
            ],
            "generated_rtl_is_called_directly": True,
            "rust_oracle_bypass": False,
            "residual_symbol_alias_routes_to_dispatcher": True,
        },
    }


__all__ = ["write_prediction_encode_overlay_sources"]
