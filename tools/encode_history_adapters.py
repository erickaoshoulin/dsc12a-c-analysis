"""Emit C/Verilator adapters for the Encode history transition contracts.

The history contracts deliberately expose the results of their semantic child
functions as ports.  This module owns the small amount of glue needed to turn
those ports into a normal overlay boundary; it does not implement either
history algorithm in C.  The immutable model function remains the oracle and
the RTL candidate owns the reduction/qerr arithmetic.
"""

from __future__ import annotations

import pathlib
import re
from typing import Any, Iterable


HISTORY_REDUCTION_KIND = "history_reduction_transition"
HISTORY_QERR_KIND = "history_qerr_transition"
HISTORY_ENTRIES = 32
HISTORY_COMPONENTS = 4
QERR_SLOTS = 6

_IDENTIFIER = re.compile(r"^[A-Za-z_][A-Za-z0-9_]*$")


def _safe_identifier(value: object) -> str:
    result = re.sub(r"[^A-Za-z0-9_]", "_", str(value))
    if not result or result[0].isdigit():
        result = "c_" + result
    return result


def _contract_kind(contract: dict[str, Any]) -> str:
    semantics = contract.get("semantics", {}) or {}
    if not isinstance(semantics, dict):
        raise RuntimeError("history adapter contract semantics are not an object")
    kind = str(semantics.get("kind", ""))
    if kind not in {HISTORY_REDUCTION_KIND, HISTORY_QERR_KIND}:
        raise ValueError(f"unsupported Encode history semantics: {kind}")
    return kind


def _ports(contract: dict[str, Any]) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    interface = contract.get("interface", {}) or {}
    if not isinstance(interface, dict):
        raise RuntimeError("history adapter interface is not an object")
    rows = [item for item in interface.get("ports", []) or [] if isinstance(item, dict)]
    if not rows:
        raise RuntimeError("history adapter contract has no interface ports")
    names: set[str] = set()
    for port in rows:
        name = str(port.get("name", ""))
        if not _IDENTIFIER.fullmatch(name) or name in names:
            raise RuntimeError(f"invalid or duplicate history port name: {name}")
        names.add(name)
        width = int(port.get("width", 0) or 0)
        if width < 1 or width > 32:
            raise RuntimeError(f"history port width is outside the 32-bit ABI: {name}")
        array = port.get("array")
        if array is not None:
            if (
                not isinstance(array, list)
                or len(array) != 2
                or int(array[0]) != 0
                or int(array[1]) < 0
            ):
                raise RuntimeError(f"history array port does not start at zero: {name}")
            extent = int(array[1]) + 1
            if extent not in {HISTORY_ENTRIES, HISTORY_COMPONENTS, QERR_SLOTS}:
                raise RuntimeError(
                    f"history array port has an unbounded/non-contract extent: {name}"
                )
        if port.get("direction") not in {"input", "output"}:
            raise RuntimeError(f"history port direction is invalid: {name}")
    return (
        [port for port in rows if port.get("direction") == "input"],
        [port for port in rows if port.get("direction") == "output"],
    )


def _port_by_name(ports: Iterable[dict[str, Any]]) -> dict[str, dict[str, Any]]:
    return {str(port["name"]): port for port in ports}


def _extent(port: dict[str, Any]) -> int | None:
    array = port.get("array")
    if array is None:
        return None
    return int(array[1]) - int(array[0]) + 1


def _require_ports(
    kind: str,
    inputs: list[dict[str, Any]],
    outputs: list[dict[str, Any]],
) -> None:
    input_names = set(_port_by_name(inputs))
    output_names = set(_port_by_name(outputs))
    common_inputs = {
        "cfg_native_420",
        "cfg_native_422",
        "cfg_dsc_version_minor",
        "state_v_pos",
        "state_num_components",
        "state_pixels_in_group",
        "state_slice_width",
        "h_pos",
        "history_valid",
        "history_lookup_0",
        "history_lookup_1",
        "history_lookup_2",
        "history_lookup_3",
        "history_lookup_result_valid",
    }
    common_outputs = {
        "lookup_request_valid",
        "lookup_request_entry",
        "lookup_request_first_line",
        "lookup_request_is_odd_line",
        "lookup_request_h_pos",
        "return_value",
        "illegal_domain",
    }
    if kind == HISTORY_REDUCTION_KIND:
        required_inputs = common_inputs | {"orig_0", "orig_1", "orig_2", "orig_3"}
        required_outputs = common_outputs | {"search_failed"}
    else:
        required_inputs = common_inputs | {
            "cfg_bits_per_component",
            "v_pos",
            "qp",
            "samp_mod_cnt",
            "cpnt_bit_depth_0",
            "cpnt_bit_depth_1",
            "cpnt_bit_depth_2",
            "cpnt_bit_depth_3",
            "orig_within_qerr",
            "orig_line_sample_0",
            "orig_line_sample_1",
            "orig_line_sample_2",
            "orig_line_sample_3",
            "map_qlevel",
        }
        required_outputs = common_outputs | {
            "map_request_valid",
            "map_request_qp",
            "map_request_cpnt",
            "max_qerr",
            "orig_within_qerr_out",
            "history_valid_out",
        }
    missing_inputs = required_inputs - input_names
    missing_outputs = required_outputs - output_names
    extra_inputs = input_names - required_inputs
    extra_outputs = output_names - required_outputs
    if missing_inputs or missing_outputs or extra_inputs or extra_outputs:
        raise RuntimeError(
            "history interface is incomplete: "
            f"missing inputs={sorted(missing_inputs)} outputs={sorted(missing_outputs)} "
            f"extra inputs={sorted(extra_inputs)} outputs={sorted(extra_outputs)}"
        )

    input_map = _port_by_name(inputs)
    output_map = _port_by_name(outputs)
    for name in (
        "history_valid",
        "history_lookup_0",
        "history_lookup_1",
        "history_lookup_2",
        "history_lookup_3",
        "history_lookup_result_valid",
        "lookup_request_valid",
        "lookup_request_entry",
        "lookup_request_first_line",
        "lookup_request_is_odd_line",
        "lookup_request_h_pos",
    ):
        port = input_map.get(name) or output_map.get(name)
        if _extent(port or {}) != HISTORY_ENTRIES:
            raise RuntimeError(f"{name} must have exactly 32 entries")
    if kind == HISTORY_QERR_KIND:
        for name in ("orig_within_qerr", "orig_within_qerr_out"):
            if _extent(input_map.get(name) or output_map.get(name) or {}) != QERR_SLOTS:
                raise RuntimeError(f"{name} must have exactly six entries")
        for name in ("map_qlevel", "map_request_valid", "map_request_cpnt", "max_qerr"):
            if _extent(input_map.get(name) or output_map.get(name) or {}) != HISTORY_COMPONENTS:
                raise RuntimeError(f"{name} must have exactly four component entries")


def _dependency_rows(contract: dict[str, Any]) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for value in (
        contract.get("dependencies", []),
        (contract.get("composition", {}) or {}).get("dependencies", []),
    ):
        if isinstance(value, list):
            rows.extend(item for item in value if isinstance(item, dict))
    return rows


def _child_name(contract: dict[str, Any], role: str) -> str:
    matches = [
        str(item.get("function", ""))
        for item in _dependency_rows(contract)
        if str(item.get("role", "")) == role and item.get("function")
    ]
    unique_matches = sorted(set(matches))
    if len(unique_matches) != 1 or not _IDENTIFIER.fullmatch(unique_matches[0]):
        raise RuntimeError(f"history contract must pin exactly one {role} child")
    return unique_matches[0]


def _function(contract: dict[str, Any]) -> dict[str, Any]:
    function = contract.get("function", {})
    if not isinstance(function, dict):
        raise RuntimeError("history contract function is not an object")
    name = str(function.get("name", ""))
    if not _IDENTIFIER.fullmatch(name):
        raise RuntimeError(f"history function name is not a C identifier: {name}")
    parameters = function.get("parameters", []) or []
    if not isinstance(parameters, list) or not parameters:
        raise RuntimeError("history contract has no native C parameters")
    for parameter in parameters:
        if not isinstance(parameter, dict) or not _IDENTIFIER.fullmatch(
            str(parameter.get("name", ""))
        ):
            raise RuntimeError("history contract contains an invalid C parameter")
    return function


def _c_parameter_declarations(function: dict[str, Any]) -> str:
    return ", ".join(
        f"{str(parameter.get('type', 'int')).strip()} {str(parameter['name'])}"
        for parameter in function.get("parameters", []) or []
    )


def _c_parameter_names(function: dict[str, Any]) -> str:
    return ", ".join(str(parameter["name"]) for parameter in function.get("parameters", []) or [])


def _abi_type(port: dict[str, Any]) -> str:
    return "int32_t" if bool(port.get("signed")) else "uint32_t"


def _abi_field(port: dict[str, Any]) -> str:
    extent = _extent(port)
    return f"{_abi_type(port)} {port['name']}[{extent}];" if extent else f"{_abi_type(port)} {port['name']};"


def _abi_text(
    inputs: list[dict[str, Any]],
    outputs: list[dict[str, Any]],
) -> str:
    input_fields = "\n".join(f"    {_abi_field(port)}" for port in inputs)
    output_fields = "\n".join(f"    {_abi_field(port)}" for port in outputs)
    return (
        "#ifndef DSC_CICD_RTL_ABI_H\n"
        "#define DSC_CICD_RTL_ABI_H\n"
        "#include <stdint.h>\n"
        f"#define DSC_CICD_HISTORY_ENTRIES {HISTORY_ENTRIES}\n"
        f"#define DSC_CICD_HISTORY_COMPONENTS {HISTORY_COMPONENTS}\n"
        f"#define DSC_CICD_HISTORY_QERR_SLOTS {QERR_SLOTS}\n"
        "typedef struct {\n"
        f"{input_fields}\n"
        "} dsc_cicd_history_input_t;\n"
        "typedef struct {\n"
        f"{output_fields}\n"
        "} dsc_cicd_history_output_t;\n"
        "#ifdef __cplusplus\nextern \"C\" {\n#endif\n"
        "void dsc_cicd_rtl(const dsc_cicd_history_input_t *input, "
        "dsc_cicd_history_output_t *output);\n"
        "#ifdef __cplusplus\n}\n#endif\n"
        "#endif\n"
    )


def _bridge_text(
    module: str,
    inputs: list[dict[str, Any]],
    outputs: list[dict[str, Any]],
) -> str:
    module_id = _safe_identifier(module)
    assignments: list[str] = []
    results: list[str] = []
    for port in inputs:
        extent = _extent(port)
        target_type = "std::int32_t" if bool(port.get("signed")) else "std::uint32_t"
        if extent:
            for index in range(extent):
                assignments.append(
                    f"    dut.{port['name']}[{index}] = "
                    f"static_cast<{target_type}>(input->{port['name']}[{index}]);"
                )
        else:
            assignments.append(
                f"    dut.{port['name']} = "
                f"static_cast<{target_type}>(input->{port['name']});"
            )
    for port in outputs:
        extent = _extent(port)
        result_type = "std::int32_t" if bool(port.get("signed")) else "std::uint32_t"
        if extent:
            for index in range(extent):
                results.append(
                    f"    output->{port['name']}[{index}] = "
                    f"static_cast<{result_type}>(dut.{port['name']}[{index}]);"
                )
        else:
            results.append(
                f"    output->{port['name']} = "
                f"static_cast<{result_type}>(dut.{port['name']});"
            )
    return (
        "#include <cstdint>\n"
        "#include \"verilated.h\"\n"
        "#include \"dsc_cicd_rtl_abi.h\"\n"
        f"#include \"V{module_id}.h\"\n"
        "double sc_time_stamp() { return 0.0; }\n"
        "extern \"C\" void dsc_cicd_rtl("
        "const dsc_cicd_history_input_t *input, "
        "dsc_cicd_history_output_t *output) {\n"
        f"    static V{module_id} dut;\n"
        + "\n".join(assignments)
        + "\n    dut.eval();\n"
        + "\n".join(results)
        + "\n}\n"
    )


def _main_text() -> str:
    return (
        "#include <stdio.h>\n"
        "extern int dsc_cicd_original_main(int, char **);\n"
        "int main(int argc, char **argv) {\n"
        "    return dsc_cicd_original_main(argc, argv);\n"
        "}\n"
    )


def _output_compare_text(outputs: list[dict[str, Any]]) -> str:
    lines = [
        "static int dsc_cicd_outputs_mismatch(const dsc_cicd_history_output_t *left,",
        "        const dsc_cicd_history_output_t *right) {",
        "    int mismatch = 0;",
    ]
    for port in outputs:
        extent = _extent(port)
        if extent:
            lines.append(f"    for (int i = 0; i < {extent}; ++i)")
            lines.append(
                f"        mismatch |= left->{port['name']}[i] != right->{port['name']}[i];"
            )
        else:
            lines.append(
                f"    mismatch |= left->{port['name']} != right->{port['name']};"
            )
    lines.extend(["    return mismatch;", "}", ""])
    return "\n".join(lines)


def _capture_common_lines(kind: str) -> list[str]:
    if kind == HISTORY_REDUCTION_KIND:
        signature = (
            "static void dsc_cicd_capture_input("
            "dsc_cicd_history_input_t *input, const dsc_cfg_t *cfg, "
            "const dsc_state_t *state, int h_pos, const unsigned int *orig) {"
        )
    else:
        signature = (
            "static void dsc_cicd_capture_input("
            "dsc_cicd_history_input_t *input, const dsc_cfg_t *cfg, "
            "const dsc_state_t *state, int h_pos, int v_pos, int qp, "
            "int samp_mod_cnt) {"
        )
    lines = [
        signature,
        "    memset(input, 0, sizeof(*input));",
        "    if (!cfg || !state) return;",
        "    input->cfg_native_420 = (uint32_t)cfg->native_420;",
        "    input->cfg_native_422 = (uint32_t)cfg->native_422;",
        "    input->cfg_dsc_version_minor = (uint32_t)cfg->dsc_version_minor;",
        "    input->state_v_pos = (int32_t)state->vPos;",
        "    input->state_num_components = (int32_t)state->numComponents;",
        "    input->state_pixels_in_group = (int32_t)state->pixelsInGroup;",
        "    input->state_slice_width = (int32_t)state->sliceWidth;",
        "    input->h_pos = (int32_t)h_pos;",
        "    if (state->history.valid) {",
        f"        for (int i = 0; i < {HISTORY_ENTRIES}; ++i)",
        "            input->history_valid[i] = (int32_t)state->history.valid[i];",
        "    }",
    ]
    if kind == HISTORY_REDUCTION_KIND:
        lines.extend(
            [
                "    if (orig) {",
                "        input->orig_0 = (uint32_t)orig[0];",
                "        input->orig_1 = (uint32_t)orig[1];",
                "        input->orig_2 = (uint32_t)orig[2];",
                "        input->orig_3 = (uint32_t)orig[3];",
                "    }",
            ]
        )
    else:
        lines.extend(
            [
                "    input->cfg_bits_per_component = (int32_t)cfg->bits_per_component;",
                "    input->v_pos = (int32_t)v_pos;",
                "    input->qp = (int32_t)qp;",
                "    input->samp_mod_cnt = (int32_t)samp_mod_cnt;",
                "    input->cpnt_bit_depth_0 = (int32_t)state->cpntBitDepth[0];",
                "    input->cpnt_bit_depth_1 = (int32_t)state->cpntBitDepth[1];",
                "    input->cpnt_bit_depth_2 = (int32_t)state->cpntBitDepth[2];",
                "    input->cpnt_bit_depth_3 = (int32_t)state->cpntBitDepth[3];",
                "    if (h_pos >= 0 && h_pos < state->sliceWidth) {",
                "        if (state->origLine[0]) input->orig_line_sample_0 = (int32_t)state->origLine[0][h_pos + PADDING_LEFT];",
                "        if (state->origLine[1]) input->orig_line_sample_1 = (int32_t)state->origLine[1][h_pos + PADDING_LEFT];",
                "        if (state->origLine[2]) input->orig_line_sample_2 = (int32_t)state->origLine[2][h_pos + PADDING_LEFT];",
                "        if (state->origLine[3]) input->orig_line_sample_3 = (int32_t)state->origLine[3][h_pos + PADDING_LEFT];",
                "    }",
                f"    for (int i = 0; i < {QERR_SLOTS}; ++i)",
                "        input->orig_within_qerr[i] = (int32_t)state->origWithinQerr[i];",
            ]
        )
    lines.append("}")
    return lines


def _clone_lines() -> list[str]:
    return [
        "static int dsc_cicd_clone_state(const dsc_state_t *source,",
        "        dsc_state_t *copy,",
        f"        unsigned int history_pixels[{HISTORY_COMPONENTS}][{HISTORY_ENTRIES}],",
        f"        int history_valid[{HISTORY_ENTRIES}]) {{",
        "    if (!source || !source->history.valid) return 0;",
        "    *copy = *source;",
        f"    memcpy(history_valid, source->history.valid, sizeof(int) * {HISTORY_ENTRIES});",
        "    copy->history.valid = history_valid;",
        f"    for (int component = 0; component < {HISTORY_COMPONENTS}; ++component) {{",
        "        if (component < source->numComponents) {",
        "            if (!source->history.pixels[component]) return 0;",
        f"            memcpy(history_pixels[component], source->history.pixels[component], "
        f"sizeof(unsigned int) * {HISTORY_ENTRIES});",
        "            copy->history.pixels[component] = history_pixels[component];",
        "        } else {",
        "            copy->history.pixels[component] = source->history.pixels[component];",
        "        }",
        "    }",
        "    return 1;",
        "}",
        "",
    ]


def _domain_lines(kind: str) -> list[str]:
    if kind == HISTORY_REDUCTION_KIND:
        return [
            "static int dsc_cicd_domain_valid(const dsc_cfg_t *cfg,",
            "        const dsc_state_t *state, int h_pos, const unsigned int *orig) {",
            "    if (!cfg || !state || !state->history.valid || !orig) return 0;",
            "    if ((cfg->native_420 && cfg->native_422) ||",
            "        (state->numComponents != 3 && state->numComponents != 4) ||",
            "        (cfg->native_422 && state->numComponents != 4) ||",
            "        (!cfg->native_422 && state->numComponents != 3) ||",
            "        state->pixelsInGroup != 3 || state->vPos < 0 ||",
            "        state->sliceWidth <= 0 ||",
            "        h_pos < 0 || h_pos >= state->sliceWidth) return 0;",
            "    if ((cfg->native_420 || cfg->native_422) ? state->sliceWidth < 5 :",
            "        state->sliceWidth < 7) return 0;",
            f"    for (int component = 0; component < {HISTORY_COMPONENTS}; ++component)",
            "        if (component < state->numComponents && !state->history.pixels[component]) return 0;",
            "    return 1;",
            "}",
            "",
        ]
    return [
        "static int dsc_cicd_domain_valid(const dsc_cfg_t *cfg,",
        "        const dsc_state_t *state, int h_pos, int v_pos, int qp, int samp_mod_cnt) {",
        "    if (!cfg || !state || !state->history.valid) return 0;",
        "    if ((cfg->native_420 && cfg->native_422) ||",
        "        (state->numComponents != 3 && state->numComponents != 4) ||",
        "        (cfg->native_422 && state->numComponents != 4) ||",
        "        (!cfg->native_422 && state->numComponents != 3) ||",
        "        state->pixelsInGroup != 3 || state->vPos < 0 ||",
        "        state->sliceWidth <= 0 || h_pos < 0 || h_pos >= state->sliceWidth ||",
        "        v_pos < 0 || samp_mod_cnt < 0 || samp_mod_cnt >= DSC_CICD_HISTORY_QERR_SLOTS ||",
        "        qp < 0 || qp > 31) return 0;",
        "    if ((cfg->native_420 || cfg->native_422) ? state->sliceWidth < 5 :",
        "        state->sliceWidth < 7) return 0;",
        "    if (cfg->bits_per_component != 8 && cfg->bits_per_component != 10 &&",
        "        cfg->bits_per_component != 12 && cfg->bits_per_component != 14 &&",
        "        cfg->bits_per_component != 16) return 0;",
        f"    for (int component = 0; component < {HISTORY_COMPONENTS}; ++component) {{",
        "        if (component < state->numComponents &&",
        "            (!state->history.pixels[component] || !state->origLine[component])) return 0;",
        "    }",
        "    return 1;",
        "}",
        "",
    ]


def _history_child_declaration(name: str) -> str:
    return f"extern void {name}(dsc_cfg_t *, dsc_state_t *, int, unsigned int *, int, int, int);"


def _map_child_declaration(name: str) -> str:
    return f"extern int {name}(dsc_cfg_t *, dsc_state_t *, int, int);"


def _reduction_child_lines(history_name: str) -> list[str]:
    return [
        "static void dsc_cicd_populate_history_children(",
        "        const dsc_cfg_t *cfg, dsc_state_t *state,",
        "        dsc_cicd_history_input_t *input, int h_pos) {",
        "    int first_line = (state->vPos == 0) ||",
        "        (cfg->native_420 && state->vPos == 1);",
        f"    for (int entry = 0; entry < {HISTORY_ENTRIES}; ++entry) {{",
        "        if (input->history_valid[entry] != 0) {",
        "            unsigned int pixel[4] = {0, 0, 0, 0};",
        f"            {history_name}( (dsc_cfg_t *)cfg, state, entry, pixel, h_pos,",
        "                first_line, state->vPos % 2);",
        "            input->history_lookup_0[entry] = pixel[0];",
        "            input->history_lookup_1[entry] = pixel[1];",
        "            input->history_lookup_2[entry] = pixel[2];",
        "            input->history_lookup_3[entry] = pixel[3];",
        "            input->history_lookup_result_valid[entry] = 1;",
        "        }",
        "    }",
        "}",
        "",
    ]


def _qerr_child_lines(history_name: str, map_name: str) -> list[str]:
    return [
        "static int dsc_cicd_populate_qerr_children(",
        "        const dsc_cfg_t *cfg, dsc_state_t *state,",
        "        dsc_cicd_history_input_t *input, int h_pos, int v_pos, int qp) {",
        "    if ((h_pos == 0) && (v_pos == 0)) return 1;",
        "    int modified_qp = 2 * cfg->bits_per_component - 1;",
        "    if (qp + 2 < modified_qp) modified_qp = qp + 2;",
        f"    for (int component = 0; component < {HISTORY_COMPONENTS}; ++component) {{",
        "        if (component < state->numComponents) {",
        f"            int qlevel = {map_name}((dsc_cfg_t *)cfg, state, modified_qp, component);",
        "            input->map_qlevel[component] = (uint32_t)qlevel;",
        "            if (qlevel < 0 || qlevel > 16) return 0;",
        "        }",
        "    }",
        "    if ((!cfg->native_420 && state->vPos > 0) ||",
        "        (cfg->native_420 && state->vPos > 1)) {",
        "        for (int entry = 25; entry < DSC_CICD_HISTORY_ENTRIES; ++entry)",
        "            state->history.valid[entry] = 1;",
        "    }",
        "    int first_line = (v_pos == 0) || (cfg->native_420 && v_pos == 1);",
        f"    for (int entry = 0; entry < {HISTORY_ENTRIES}; ++entry) {{",
        "        if (state->history.valid[entry] != 0) {",
        "            unsigned int pixel[4] = {0, 0, 0, 0};",
        f"            {history_name}((dsc_cfg_t *)cfg, state, entry, pixel, h_pos,",
        "                first_line, v_pos % 2);",
        "            input->history_lookup_0[entry] = pixel[0];",
        "            input->history_lookup_1[entry] = pixel[1];",
        "            input->history_lookup_2[entry] = pixel[2];",
        "            input->history_lookup_3[entry] = pixel[3];",
        "            input->history_lookup_result_valid[entry] = 1;",
        "        }",
        "    }",
        "    return 1;",
        "}",
        "",
    ]


def _reduction_expected_lines() -> list[str]:
    return [
        "static void dsc_cicd_expected_reduction(",
        "        const dsc_cicd_history_input_t *input,",
        "        dsc_cicd_history_output_t *expected, int legal, int c_value) {",
        "    memset(expected, 0, sizeof(*expected));",
        f"    for (int entry = 0; entry < {HISTORY_ENTRIES}; ++entry) {{",
        "        expected->lookup_request_entry[entry] = (uint32_t)entry;",
        "        expected->lookup_request_h_pos[entry] = input->h_pos;",
        "    }",
        "    expected->return_value = c_value;",
        "    expected->search_failed = (c_value == 99);",
        "    expected->illegal_domain = legal ? 0 : 1;",
        "    if (legal) {",
        "        int first_line = (input->state_v_pos == 0) ||",
        "            (input->cfg_native_420 && input->state_v_pos == 1);",
        f"        for (int entry = 0; entry < {HISTORY_ENTRIES}; ++entry) {{",
        "            expected->lookup_request_valid[entry] =",
        "                input->history_valid[entry] != 0;",
        "            expected->lookup_request_first_line[entry] = first_line;",
        "            expected->lookup_request_is_odd_line[entry] =",
        "                (input->state_v_pos & 1) != 0;",
        "        }",
        "    }",
        "}",
        "",
    ]


def _quant_divisor_lines(contract: dict[str, Any]) -> list[str]:
    constants = (contract.get("semantics", {}) or {}).get("constants", {}) or {}
    table = constants.get("quant_divisor", []) or []
    if len(table) != 17:
        raise RuntimeError("history qerr contract must carry the 17-entry QuantDivisor table")
    cases = [
        f"        case {index}: return {int(value)};"
        for index, value in enumerate(table)
    ]
    return [
        "static int32_t dsc_cicd_quant_divisor(uint32_t qlevel) {",
        "    switch (qlevel) {",
        *cases,
        "        default: return 0;",
        "    }",
        "}",
        "",
    ]


def _qerr_expected_lines(contract: dict[str, Any]) -> list[str]:
    return [
        "static void dsc_cicd_expected_qerr(",
        "        const dsc_cicd_history_input_t *input,",
        "        const dsc_state_t *c_state,",
        "        dsc_cicd_history_output_t *expected, int legal, int c_value) {",
        "    memset(expected, 0, sizeof(*expected));",
        f"    for (int slot = 0; slot < {QERR_SLOTS}; ++slot) {{",
        "        expected->orig_within_qerr_out[slot] = input->orig_within_qerr[slot];",
        "        if (c_state && c_state->history.valid)",
        "            expected->orig_within_qerr_out[slot] = c_state->origWithinQerr[slot];",
        "    }",
        f"    for (int entry = 0; entry < {HISTORY_ENTRIES}; ++entry) {{",
        "        expected->history_valid_out[entry] = input->history_valid[entry];",
        "        if (c_state && c_state->history.valid)",
        "            expected->history_valid_out[entry] = c_state->history.valid[entry];",
        "        expected->lookup_request_entry[entry] = (uint32_t)entry;",
        "        expected->lookup_request_h_pos[entry] = input->h_pos;",
        "    }",
        f"    for (int component = 0; component < {HISTORY_COMPONENTS}; ++component)",
        "        expected->map_request_cpnt[component] = (uint32_t)component;",
        "    if (!legal && input->samp_mod_cnt >= 0 &&",
        f"        input->samp_mod_cnt < {QERR_SLOTS})",
        "        expected->orig_within_qerr_out[input->samp_mod_cnt] = 0;",
        "    expected->return_value = c_value;",
        "    expected->illegal_domain = legal ? 0 : 1;",
        "    if (legal && !(input->h_pos == 0 && input->v_pos == 0)) {",
        "        int modified_qp = 2 * input->cfg_bits_per_component - 1;",
        "        if (input->qp + 2 < modified_qp) modified_qp = input->qp + 2;",
        "        expected->map_request_qp = (uint32_t)modified_qp;",
        f"        for (int component = 0; component < {HISTORY_COMPONENTS}; ++component) {{",
        "            if (component < input->state_num_components) {",
        "                expected->map_request_valid[component] = 1;",
        "                expected->max_qerr[component] =",
        "                    dsc_cicd_quant_divisor(input->map_qlevel[component]) / 2;",
        "            }",
        "        }",
        "        int first_line = (input->v_pos == 0) ||",
        "            (input->cfg_native_420 && input->v_pos == 1);",
        f"        for (int entry = 0; entry < {HISTORY_ENTRIES}; ++entry) {{",
        "            expected->lookup_request_valid[entry] =",
        "                c_state->history.valid[entry] != 0;",
        "            expected->lookup_request_first_line[entry] = first_line;",
        "            expected->lookup_request_is_odd_line[entry] =",
        "                (input->v_pos & 1) != 0;",
        "        }",
        "    }",
        "}",
        "",
    ]


def _qerr_state_lines() -> list[str]:
    return [
        "static void dsc_cicd_restore_qerr_touched(",
        "        dsc_state_t *state, const int *orig_snapshot,",
        "        const int *valid_snapshot) {",
        "    if (!state || !state->history.valid) return;",
        f"    memcpy(state->origWithinQerr, orig_snapshot, sizeof(int) * {QERR_SLOTS});",
        f"    memcpy(state->history.valid, valid_snapshot, sizeof(int) * {HISTORY_ENTRIES});",
        "}",
        "",
        "static void dsc_cicd_commit_qerr_c(",
        "        dsc_state_t *state, const dsc_cicd_history_output_t *output,",
        "        int samp_mod_cnt) {",
        "    if (!state || !state->history.valid) return;",
        f"    if (samp_mod_cnt >= 0 && samp_mod_cnt < {QERR_SLOTS})",
        "        state->origWithinQerr[samp_mod_cnt] =",
        "            output->orig_within_qerr_out[samp_mod_cnt];",
        "    for (int entry = 25; entry < DSC_CICD_HISTORY_ENTRIES; ++entry)",
        "        state->history.valid[entry] = output->history_valid_out[entry];",
        "}",
        "",
        "static void dsc_cicd_commit_qerr_rtl(",
        "        dsc_state_t *state, const dsc_cicd_history_output_t *output,",
        "        int samp_mod_cnt) {",
        "    dsc_cicd_commit_qerr_c(state, output, samp_mod_cnt);",
        "}",
        "",
    ]


def _reduction_overlay_text(
    function: dict[str, Any],
    original: str,
    history_name: str,
    metrics: str,
) -> str:
    declarations = _c_parameter_declarations(function)
    names = _c_parameter_names(function)
    # The new contract is intentionally parameterized by facts, but these
    # semantic ports are bound to the immutable DSC ABI fields.  Keep the
    # native argument names in the generated C call derived from the frozen
    # parameter order rather than admitting a function spelling.
    parameter_names = [str(item["name"]) for item in function.get("parameters", []) or []]
    if len(parameter_names) != 4:
        raise RuntimeError("history reduction native ABI must have four parameters")
    cfg, state, h_pos, orig = parameter_names
    lines: list[str] = [
        "#include <stdint.h>",
        "#include <stdio.h>",
        "#include <stdlib.h>",
        "#include <string.h>",
        '#include "dsc_cicd_overlay.h"',
        '#include "dsc_cicd_rtl_abi.h"',
        f"extern int {original}({declarations});",
        _history_child_declaration(history_name),
        "static int dsc_cicd_mode(void) {",
        '    const char *value = getenv("DSC_CICD_MODE");',
        '    if (value && strcmp(value, "SHADOW") == 0) return 1;',
        '    if (value && strcmp(value, "RTL_RETURN") == 0) return 2;',
        "    return 0;",
        "}",
        metrics.rstrip(),
        *_clone_lines(),
        *_domain_lines(HISTORY_REDUCTION_KIND),
        *_reduction_child_lines(history_name),
        *_capture_common_lines(HISTORY_REDUCTION_KIND),
        *_reduction_expected_lines(),
        _output_compare_text(
            [
                {"name": "lookup_request_valid", "array": [0, 31]},
                {"name": "lookup_request_entry", "array": [0, 31]},
                {"name": "lookup_request_first_line", "array": [0, 31]},
                {"name": "lookup_request_is_odd_line", "array": [0, 31]},
                {"name": "lookup_request_h_pos", "array": [0, 31]},
                {"name": "return_value"},
                {"name": "search_failed"},
                {"name": "illegal_domain"},
            ]
        ),
        f"int dsc_cicd_invoke({declarations}) {{",
        "    dsc_cicd_history_input_t input;",
        "    dsc_cicd_history_output_t c_output;",
        "    dsc_cicd_history_output_t rtl_output;",
        f"    dsc_state_t dsc_cicd_c_state;",
        f"    unsigned int dsc_cicd_history_pixels[{HISTORY_COMPONENTS}][{HISTORY_ENTRIES}];",
        f"    int dsc_cicd_history_valid[{HISTORY_ENTRIES}];",
        f"    dsc_cicd_capture_input(&input, {cfg}, {state}, {h_pos}, {orig});",
        f"    int legal = dsc_cicd_domain_valid({cfg}, {state}, {h_pos}, {orig});",
        f"    if (legal && !dsc_cicd_clone_state({state}, &dsc_cicd_c_state,",
        "        dsc_cicd_history_pixels, dsc_cicd_history_valid)) legal = 0;",
        "    if (legal)",
        f"        dsc_cicd_populate_history_children({cfg}, &dsc_cicd_c_state,",
        f"            &input, {h_pos});",
        f"    int c_value = legal ? {original}({cfg}, &dsc_cicd_c_state, {h_pos}, {orig}) : 99;",
        "    dsc_cicd_expected_reduction(&input, &c_output, legal, c_value);",
        "    int mode = dsc_cicd_mode();",
        "    dsc_cicd_note_call(mode);",
        "    if (mode == 0) return c_value;",
        "    memset(&rtl_output, 0, sizeof(rtl_output));",
        "    dsc_cicd_rtl(&input, &rtl_output);",
        "    if (dsc_cicd_outputs_mismatch(&c_output, &rtl_output)) {",
        "        ++dsc_cicd_mismatches;",
        '        fprintf(stderr, "C/RTL history reduction mismatch\\n");',
        "    }",
        "    return mode == 2 ? (int)rtl_output.return_value : c_value;",
        "}",
        f"int {str(function['name'])}({declarations}) {{",
        f"    return dsc_cicd_invoke({names});",
        "}",
    ]
    return "\n".join(lines) + "\n"


def _qerr_overlay_text(
    contract: dict[str, Any],
    function: dict[str, Any],
    original: str,
    history_name: str,
    map_name: str,
    metrics: str,
) -> str:
    declarations = _c_parameter_declarations(function)
    names = _c_parameter_names(function)
    parameter_names = [str(item["name"]) for item in function.get("parameters", []) or []]
    if len(parameter_names) != 6:
        raise RuntimeError("history qerr native ABI must have six parameters")
    cfg, state, h_pos, v_pos, qp, samp = parameter_names
    compare_ports = [
        {"name": "lookup_request_valid", "array": [0, 31]},
        {"name": "lookup_request_entry", "array": [0, 31]},
        {"name": "lookup_request_first_line", "array": [0, 31]},
        {"name": "lookup_request_is_odd_line", "array": [0, 31]},
        {"name": "lookup_request_h_pos", "array": [0, 31]},
        {"name": "map_request_valid", "array": [0, 3]},
        {"name": "map_request_qp"},
        {"name": "map_request_cpnt", "array": [0, 3]},
        {"name": "max_qerr", "array": [0, 3]},
        {"name": "orig_within_qerr_out", "array": [0, 5]},
        {"name": "history_valid_out", "array": [0, 31]},
        {"name": "return_value"},
        {"name": "illegal_domain"},
    ]
    lines: list[str] = [
        "#include <stdint.h>",
        "#include <stdio.h>",
        "#include <stdlib.h>",
        "#include <string.h>",
        '#include "dsc_cicd_overlay.h"',
        '#include "dsc_cicd_rtl_abi.h"',
        f"extern int {original}({declarations});",
        _history_child_declaration(history_name),
        _map_child_declaration(map_name),
        "static int dsc_cicd_mode(void) {",
        '    const char *value = getenv("DSC_CICD_MODE");',
        '    if (value && strcmp(value, "SHADOW") == 0) return 1;',
        '    if (value && strcmp(value, "RTL_RETURN") == 0) return 2;',
        "    return 0;",
        "}",
        metrics.rstrip(),
        *_clone_lines(),
        *_domain_lines(HISTORY_QERR_KIND),
        *_qerr_child_lines(history_name, map_name),
        *_capture_common_lines(HISTORY_QERR_KIND),
        *_quant_divisor_lines(contract),
        *_qerr_expected_lines(contract),
        *_qerr_state_lines(),
        _output_compare_text(compare_ports),
        f"int dsc_cicd_invoke({declarations}) {{",
        "    dsc_cicd_history_input_t input;",
        "    dsc_cicd_history_output_t c_output;",
        "    dsc_cicd_history_output_t rtl_output;",
        "    dsc_state_t dsc_cicd_c_state;",
        f"    unsigned int dsc_cicd_history_pixels[{HISTORY_COMPONENTS}][{HISTORY_ENTRIES}];",
        f"    int dsc_cicd_history_valid[{HISTORY_ENTRIES}];",
        f"    int dsc_cicd_saved_orig_within_qerr[{QERR_SLOTS}];",
        f"    int dsc_cicd_saved_history_valid[{HISTORY_ENTRIES}];",
        f"    dsc_cicd_capture_input(&input, {cfg}, {state}, {h_pos}, {v_pos}, {qp}, {samp});",
        f"    if ({state} && {state}->history.valid) {{",
        f"        memcpy(dsc_cicd_saved_orig_within_qerr, {state}->origWithinQerr,",
        f"            sizeof(int) * {QERR_SLOTS});",
        f"        memcpy(dsc_cicd_saved_history_valid, {state}->history.valid,",
        f"            sizeof(int) * {HISTORY_ENTRIES});",
        "    } else {",
        f"        memset(dsc_cicd_saved_orig_within_qerr, 0, sizeof(dsc_cicd_saved_orig_within_qerr));",
        f"        memset(dsc_cicd_saved_history_valid, 0, sizeof(dsc_cicd_saved_history_valid));",
        "    }",
        f"    int legal = dsc_cicd_domain_valid({cfg}, {state}, {h_pos}, {v_pos}, {qp}, {samp});",
        f"    if (legal && !dsc_cicd_clone_state({state}, &dsc_cicd_c_state,",
        "        dsc_cicd_history_pixels, dsc_cicd_history_valid)) legal = 0;",
        "    if (legal)",
        f"        legal = dsc_cicd_populate_qerr_children({cfg}, &dsc_cicd_c_state,",
        f"            &input, {h_pos}, {v_pos}, {qp});",
        f"    int c_value = legal ? {original}({cfg}, &dsc_cicd_c_state,",
        f"        {h_pos}, {v_pos}, {qp}, {samp}) : 0;",
        "    if (!legal) {",
        "        memset(&dsc_cicd_c_state, 0, sizeof(dsc_cicd_c_state));",
        f"        if ({state}) dsc_cicd_c_state = *{state};",
        "    }",
        "    dsc_cicd_expected_qerr(&input, &dsc_cicd_c_state, &c_output, legal, c_value);",
        "    int mode = dsc_cicd_mode();",
        "    dsc_cicd_note_call(mode);",
        "    if (mode == 0) {",
        f"        dsc_cicd_restore_qerr_touched({state}, dsc_cicd_saved_orig_within_qerr,",
        "            dsc_cicd_saved_history_valid);",
        f"        dsc_cicd_commit_qerr_c({state}, &c_output, {samp});",
        "        return c_value;",
        "    }",
        "    memset(&rtl_output, 0, sizeof(rtl_output));",
        "    dsc_cicd_rtl(&input, &rtl_output);",
        "    if (dsc_cicd_outputs_mismatch(&c_output, &rtl_output)) {",
        "        ++dsc_cicd_mismatches;",
        '        fprintf(stderr, "C/RTL history qerr mismatch\\n");',
        "    }",
        "    if (mode == 2) {",
        f"        dsc_cicd_restore_qerr_touched({state}, dsc_cicd_saved_orig_within_qerr,",
        "            dsc_cicd_saved_history_valid);",
        f"        dsc_cicd_commit_qerr_rtl({state}, &rtl_output, {samp});",
        "        return (int)rtl_output.return_value;",
        "    }",
        f"    dsc_cicd_restore_qerr_touched({state}, dsc_cicd_saved_orig_within_qerr,",
        "        dsc_cicd_saved_history_valid);",
        f"    dsc_cicd_commit_qerr_c({state}, &c_output, {samp});",
        "    return c_value;",
        "}",
        f"int {str(function['name'])}({declarations}) {{",
        f"    return dsc_cicd_invoke({names});",
        "}",
    ]
    return "\n".join(lines) + "\n"


def _header_text(function: dict[str, Any]) -> str:
    declarations = _c_parameter_declarations(function)
    name = str(function["name"])
    return (
        "#ifndef DSC_CICD_OVERLAY_H\n"
        "#define DSC_CICD_OVERLAY_H\n"
        '#include "dsc_types.h"\n'
        "#ifdef __cplusplus\nextern \"C\" {\n#endif\n"
        f"int dsc_cicd_invoke({declarations});\n"
        f"int {name}({declarations});\n"
        "#ifdef __cplusplus\n}\n#endif\n"
        "#endif\n"
    )


def write_history_encode_overlay_sources(
    agent: Any,
    contract: dict[str, Any],
    source_dir: pathlib.Path,
    module: str,
    candidate_sv: pathlib.Path,
) -> dict[str, Any]:
    """Write the explicit adapter for one Encode history transition.

    ``agent`` is deliberately only used for the repository-wide runtime
    metrics fragment.  Keeping the emitter independent lets the owner of
    ``Agent.write_overlay_sources`` register these two semantic kinds without
    making this module import or mutate the agent implementation.
    """

    kind = _contract_kind(contract)
    inputs, outputs = _ports(contract)
    _require_ports(kind, inputs, outputs)
    function = _function(contract)
    function_name = str(function["name"])
    original = f"{function_name}_original"
    history_name = _child_name(contract, "history_lookup")
    map_name = _child_name(contract, "map_qp_to_qlevel") if kind == HISTORY_QERR_KIND else ""
    metrics = agent.overlay_runtime_metrics_source()
    if not isinstance(metrics, str) or not metrics.strip():
        raise RuntimeError("agent.overlay_runtime_metrics_source() returned no source")

    source_dir = pathlib.Path(source_dir)
    source_dir.mkdir(parents=True, exist_ok=True)
    candidate_sv = pathlib.Path(candidate_sv)
    header = source_dir / "dsc_cicd_overlay.h"
    abi = source_dir / "dsc_cicd_rtl_abi.h"
    overlay = source_dir / "dsc_cicd_overlay.c"
    bridge = source_dir / "rtl_bridge.cpp"
    main = source_dir / "dsc_cicd_main.c"
    header.write_text(_header_text(function), encoding="utf-8")
    abi.write_text(_abi_text(inputs, outputs), encoding="utf-8")
    if kind == HISTORY_REDUCTION_KIND:
        overlay.write_text(
            _reduction_overlay_text(function, original, history_name, metrics),
            encoding="utf-8",
        )
    else:
        overlay.write_text(
            _qerr_overlay_text(contract, function, original, history_name, map_name, metrics),
            encoding="utf-8",
        )
    bridge.write_text(_bridge_text(module, inputs, outputs), encoding="utf-8")
    main.write_text(_main_text(), encoding="utf-8")

    output_names = [str(port["name"]) for port in outputs]
    input_names = [str(port["name"]) for port in inputs]
    child_result_ports = {
        "history_lookup": [
            "history_lookup_0[0..31]",
            "history_lookup_1[0..31]",
            "history_lookup_2[0..31]",
            "history_lookup_3[0..31]",
            "history_lookup_result_valid[0..31]",
        ],
    }
    child_calls: list[dict[str, Any]] = [
        {
            "role": "history_lookup",
            "function": history_name,
            "result_ports": child_result_ports["history_lookup"],
            "request_ports": [
                "lookup_request_valid[0..31]",
                "lookup_request_entry[0..31]",
                "lookup_request_first_line[0..31]",
                "lookup_request_is_odd_line[0..31]",
                "lookup_request_h_pos[0..31]",
            ],
        }
    ]
    if kind == HISTORY_QERR_KIND:
        child_calls.append(
            {
                "role": "map_qp_to_qlevel",
                "function": map_name,
                "result_ports": ["map_qlevel[0..3]"],
                "request_ports": [
                    "map_request_valid[0..3]",
                    "map_request_qp",
                    "map_request_cpnt[0..3]",
                ],
            }
        )
    composition: dict[str, Any] = {
        "status": "PASS",
        "adapter_kind": f"explicit_{kind}",
        "semantic_kind": kind,
        "caller_parameter_count": len(function.get("parameters", []) or []),
        "rtl_input_count": len(inputs),
        "frozen_input_ports": input_names,
        "state_outputs": output_names,
        "rtl_bindings": input_names,
        "output_ports_compared": output_names,
        "legal_domain_port_compared": True,
        "c_only_shadow_rtl_return": True,
        "immutable_original_c_oracle": original,
        "private_c_oracle": True,
        "c_oracle_uses_private_history_arrays": True,
        "c_oracle_uses_private_state_arrays": True,
        "child_result_ports_are_explicit_inputs": True,
        "child_calls_are_semantic_and_routable": True,
        "simultaneous_rewrite_routes_child_calls_to_rtl": True,
        "c_precomputed_sad": False,
        "c_precomputed_qerr": False,
        "history_entry_bound": HISTORY_ENTRIES,
        "component_bound": HISTORY_COMPONENTS,
        "child_calls": child_calls,
        "residual_symbol_alias_routes_to_dispatcher": True,
    }
    if kind == HISTORY_REDUCTION_KIND:
        composition.update(
            {
                "rtl_return_controls_result": True,
                "rtl_return_controls_search_result": True,
                "compare_return_value_search_failed_and_illegal_domain": True,
            }
        )
    else:
        composition.update(
            {
                "qerr_slot_bound": QERR_SLOTS,
                "rtl_return_controls_result": True,
                "rtl_return_controls_state_outputs": True,
                "snapshot_restore_before_rtl_return": True,
                "c_oracle_state_pointers_restored_before_rtl_return": True,
                "snapshot_restore_locations": [
                    "origWithinQerr[0..5]",
                    "history.valid[0..31]",
                ],
                "rtl_return_commits_only_touched_state": True,
                "every_touched_output_element_compared": True,
                "compare_qerr_state_images_and_legal_domain": True,
            }
        )
    return {
        "header": header,
        "abi": abi,
        "overlay": overlay,
        "bridge": bridge,
        "main": main,
        "candidate": candidate_sv,
        "composition": composition,
    }


def write_overlay_sources(
    agent: Any,
    contract: dict[str, Any],
    source_dir: pathlib.Path,
    module: str,
    candidate_sv: pathlib.Path,
) -> dict[str, Any]:
    """Compatibility alias for callers that dispatch emitters by module."""

    return write_history_encode_overlay_sources(
        agent, contract, source_dir, module, candidate_sv
    )


__all__ = [
    "HISTORY_REDUCTION_KIND",
    "HISTORY_QERR_KIND",
    "write_history_encode_overlay_sources",
    "write_overlay_sources",
]
