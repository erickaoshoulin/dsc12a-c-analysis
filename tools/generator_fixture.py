#!/usr/bin/env python3
"""Deterministic external generator hook used for executable CI demonstrations.

The production agent invokes this through DSC_CICD_GENERATOR_CMD exactly like it
would invoke a model-backed generator.  It consumes only the request contract,
frozen interface, C body, and short exact anchors.  It intentionally emits one
correct and one mutated candidate so the real verifier has a failure to
measure, rather than replaying an old receipt.
"""

from __future__ import annotations

import json
import pathlib
import re
import sys


def safe(value: str) -> str:
    value = re.sub(r"[^A-Za-z0-9_]", "_", value)
    return value if value and not value[0].isdigit() else "c_" + value


def normalized_identifier(value: object) -> str:
    return re.sub(r"[^a-z0-9]", "", str(value).lower())


def port_decl(port: dict[str, object]) -> str:
    width = int(port.get("width", 1))
    signed = " signed" if port.get("signed") else ""
    range_text = f" [{width - 1}:0]" if width > 1 else ""
    return f"    {port.get('direction', 'input')} logic{signed}{range_text} {port['name']}"


def quantization_body(interface: dict[str, object], semantics: dict[str, object], bad: bool) -> str:
    ports = interface.get("ports", [])
    names = {str(p.get("role")): str(p.get("name")) for p in ports if isinstance(p, dict)}
    e_name = names.get("e", "e")
    q_name = names.get("qlevel", "qlevel")
    out_name = names.get("return_value", "return_value")
    offsets = [int(x) for x in semantics.get("quant_offset", [])]
    lines = [
        "    integer signed e_i;",
        "    integer signed round_i;",
        "    always_comb begin",
        f"        e_i = $signed({e_name});",
        "        round_i = 0;",
        f"        case ({q_name})",
    ]
    for index, offset in enumerate(offsets):
        lines.append(f"            {index}: round_i = {offset};")
    lines.extend([
        "            default: round_i = 0;",
        "        endcase",
        f"        if (e_i > 0) {out_name} = (e_i + round_i) >>> {q_name};",
        f"        else {out_name} = -((round_i - e_i) >>> {q_name});",
    ])
    if bad:
        lines.append(f"        {out_name} = {out_name} + 1;")
    lines.append("    end")
    return "\n".join(lines)


def line_storage_body(interface: dict[str, object], bad: bool) -> str:
    ports = interface.get("ports", [])
    names = {
        normalized_identifier(str(port.get("role", port.get("name")))): str(port.get("name"))
        for port in ports if isinstance(port, dict)
    }
    x_name = names.get("x", "x")
    bit_depth_name = names.get("cpntbitdepth", "cpntBitDepth")
    linebuf_name = names.get("linebufdepth", "linebuf_depth")
    out_name = names.get("returnvalue", "return_value")
    lines = [
        "    integer signed shift_amount_i;",
        "    integer signed round_i;",
        "    integer signed stored_sample_i;",
        "    always_comb begin",
        f"        shift_amount_i = {bit_depth_name} - {linebuf_name};",
        "        if (shift_amount_i < 0) shift_amount_i = 0;",
        "        round_i = shift_amount_i > 0 ? (1 <<< (shift_amount_i - 1)) : 0;",
        f"        stored_sample_i = ({x_name} + round_i) >>> shift_amount_i;",
        f"        if (stored_sample_i > ((1 <<< {linebuf_name}) - 1)) stored_sample_i = (1 <<< {linebuf_name}) - 1;",
        f"        {out_name} = stored_sample_i <<< shift_amount_i;",
    ]
    if bad:
        lines.append(f"        {out_name} = {out_name} + 1;")
    lines.append("    end")
    return "\n".join(lines)


def qp_mapping_body(interface: dict[str, object], bad: bool) -> str:
    ports = interface.get("ports", [])
    names = {
        normalized_identifier(str(port.get("role", port.get("name")))): str(port.get("name"))
        for port in ports if isinstance(port, dict)
    }
    version_name = names.get("dscversionminor", "dsc_version_minor")
    native_name = names.get("native420", "native_420")
    bit_depth_0_name = names.get("cpntbitdepth0", "cpntBitDepth_0")
    bit_depth_1_name = names.get("cpntbitdepth1", "cpntBitDepth_1")
    luma_name = names.get("tablelookupluma", "qlevel_luma")
    chroma_name = names.get("tablelookupchroma", "qlevel_chroma")
    cpnt_name = names.get("cpnt", "cpnt")
    out_name = names.get("returnvalue", "return_value")
    lines = [
        "    integer signed qlevel_i;",
        "    always_comb begin",
        f"        if (({cpnt_name} % 3) == 0) begin",
        f"            qlevel_i = {luma_name};",
        f"        end else if (({native_name} != 0) && ({cpnt_name} == 1)) begin",
        f"            qlevel_i = {luma_name};",
        "        end else begin",
        f"            qlevel_i = {chroma_name};",
        f"            if (({version_name} == 2) && ({bit_depth_0_name} == {bit_depth_1_name}) && (qlevel_i > 0)) begin",
        "                qlevel_i = qlevel_i - 1;",
        "            end",
        "        end",
        f"        {out_name} = qlevel_i;",
    ]
    if bad:
        lines.append(f"        {out_name} = {out_name} + 1;")
    lines.append("    end")
    return "\n".join(lines)


def max_residual_size_body(interface: dict[str, object], bad: bool) -> str:
    ports = interface.get("ports", [])
    names = {
        normalized_identifier(str(port.get("role", port.get("name")))): str(port.get("name"))
        for port in ports if isinstance(port, dict)
    }
    version_name = names.get("dscversionminor", "dsc_version_minor")
    native_name = names.get("native420", "native_420")
    bit_depth_name = names.get("configselected", "cpntBitDepth_selected")
    bit_depth_0_name = names.get("cpntbitdepth0", "cpntBitDepth_0")
    bit_depth_1_name = names.get("cpntbitdepth1", "cpntBitDepth_1")
    luma_name = names.get("tablelookupluma", "qlevel_luma")
    chroma_name = names.get("tablelookupchroma", "qlevel_chroma")
    cpnt_name = names.get("cpnt", "cpnt")
    out_name = names.get("returnvalue", "return_value")
    lines = [
        "    integer signed qlevel_i;",
        "    integer signed chroma_i;",
        "    integer signed max_size_i;",
        "    always_comb begin",
        f"        max_size_i = {bit_depth_name};",
        f"        if (({cpnt_name} % 3) == 0) begin",
        f"            qlevel_i = {luma_name};",
        f"        end else if (({native_name} != 0) && ({cpnt_name} == 1)) begin",
        f"            qlevel_i = {luma_name};",
        "        end else begin",
        f"            chroma_i = {chroma_name};",
        f"            if (({version_name} == 2) && ({bit_depth_0_name} == (({cpnt_name} == 1) ? {bit_depth_name} : {bit_depth_1_name}))) begin",
        "                chroma_i = chroma_i - 1;",
        "            end",
        "            qlevel_i = chroma_i < 0 ? 0 : chroma_i;",
        "        end",
        f"        max_size_i = max_size_i - qlevel_i;",
        f"        {out_name} = max_size_i;",
    ]
    if bad:
        lines.append(f"        {out_name} = {out_name} + 1;")
    lines.append("    end")
    return "\n".join(lines)


def qp_adjusted_pred_size_body(interface: dict[str, object], bad: bool) -> str:
    ports = interface.get("ports", [])
    names = {
        normalized_identifier(str(port.get("role", port.get("name")))): str(port.get("name"))
        for port in ports if isinstance(port, dict)
    }
    version_name = names.get("dscversionminor", "dsc_version_minor")
    native_name = names.get("native420", "native_420")
    unit_name = names.get("unit", "unit")
    cpnt_name = names.get("stateselected", "unit_c_type_selected")
    pred_size_name = names.get("stateselected", "predicted_size_selected")
    primary_qp_name = names.get("stateruntime", "primary_qp")
    prev_qp_name = names.get("stateruntime", "prev_primary_qp")
    bpc_names = [names.get(f"configstatic", f"cpntBitDepth_{index}") for index in range(4)]
    luma_new_name = "qlevel_luma_new"
    chroma_new_name = "qlevel_chroma_new"
    luma_old_name = "qlevel_luma_old"
    chroma_old_name = "qlevel_chroma_old"
    out_name = names.get("returnvalue", "return_value")
    # Roles are not unique for the four static bit-depth ports and for the two
    # state-runtime QPs, so use their frozen names when selecting those ports.
    port_names = {str(port.get("name")): str(port.get("name")) for port in ports if isinstance(port, dict)}
    cpnt_name = port_names.get("unit_c_type_selected", cpnt_name)
    pred_size_name = port_names.get("predicted_size_selected", pred_size_name)
    primary_qp_name = port_names.get("primary_qp", primary_qp_name)
    prev_qp_name = port_names.get("prev_primary_qp", prev_qp_name)
    bpc_names = [port_names.get(f"cpntBitDepth_{index}", f"cpntBitDepth_{index}") for index in range(4)]
    lines = [
        "    integer signed cpnt_i;",
        "    integer signed bit_depth_i;",
        "    integer signed qlevel_new_i;",
        "    integer signed qlevel_old_i;",
        "    integer signed pred_size_i;",
        "    integer signed max_size_i;",
        "    always_comb begin",
        f"        cpnt_i = {cpnt_name};",
        "        case (cpnt_i)",
    ]
    for index, bpc_name in enumerate(bpc_names):
        lines.append(f"            {index}: bit_depth_i = {bpc_name};")
    lines.extend([
        f"            default: bit_depth_i = {bpc_names[0]};",
        "        endcase",
        f"        if ((cpnt_i % 3) == 0) begin",
        f"            qlevel_new_i = {luma_new_name};",
        f"        end else if (({native_name} != 0) && (cpnt_i == 1)) begin",
        f"            qlevel_new_i = {luma_new_name};",
        "        end else begin",
        f"            qlevel_new_i = {chroma_new_name};",
        f"            if (({version_name} == 2) && ({bpc_names[0]} == {bpc_names[1]}) && (qlevel_new_i > 0)) begin",
        "                qlevel_new_i = qlevel_new_i - 1;",
        "            end",
        "        end",
        f"        if ((cpnt_i % 3) == 0) begin",
        f"            qlevel_old_i = {luma_old_name};",
        f"        end else if (({native_name} != 0) && (cpnt_i == 1)) begin",
        f"            qlevel_old_i = {luma_old_name};",
        "        end else begin",
        f"            qlevel_old_i = {chroma_old_name};",
        f"            if (({version_name} == 2) && ({bpc_names[0]} == {bpc_names[1]}) && (qlevel_old_i > 0)) begin",
        "                qlevel_old_i = qlevel_old_i - 1;",
        "            end",
        "        end",
        f"        pred_size_i = {pred_size_name} + qlevel_old_i - qlevel_new_i;",
        f"        max_size_i = bit_depth_i - qlevel_new_i;",
        "        if (pred_size_i < 0) pred_size_i = 0;",
        "        else if (pred_size_i > (max_size_i - 1)) pred_size_i = max_size_i - 1;",
        f"        {out_name} = pred_size_i;",
    ])
    if bad:
        lines.append(f"        {out_name} = {out_name} + 1;")
    lines.append("    end")
    return "\n".join(lines)


def windowed_sample_predict_body(interface: dict[str, object], bad: bool) -> str:
    """Emit the deterministic fixture candidate for a flattened sample window.

    The production path supplies the same frozen interface to an external
    generator.  This fixture keeps CI executable offline while implementing
    the reviewed DSC MMAP/left/block equations rather than replaying a stored
    candidate.
    """
    ports = interface.get("ports", [])
    names = {str(port.get("name")): str(port.get("name")) for port in ports if isinstance(port, dict)}
    required = [
        "hPos", "predType", "qLevel", "unit", "unit_c_type", "cpnt_bit_depth",
        "quantized_residual_0", "quantized_residual_1",
        "prev_3", "prev_4", "prev_5", "prev_6", "prev_7", "prev_8",
        "curr_0", "curr_1", "curr_2", "curr_3", "curr_4", "curr_5", "curr_6",
        "return_value",
    ]
    missing = [name for name in required if name not in names]
    if missing:
        raise ValueError("windowed sample-predict fixture is missing ports: " + ", ".join(missing))

    lines = [
        "    integer signed a_i;",
        "    integer signed b_i;",
        "    integer signed c_i;",
        "    integer signed d_i;",
        "    integer signed e_i;",
        "    integer signed filt_c_i;",
        "    integer signed filt_b_i;",
        "    integer signed filt_d_i;",
        "    integer signed filt_e_i;",
        "    integer signed blend_b_i;",
        "    integer signed blend_c_i;",
        "    integer signed blend_d_i;",
        "    integer signed blend_e_i;",
        "    integer signed diff_i;",
        "    integer signed qdiv_i;",
        "    integer signed qhalf_i;",
        "    integer signed cpnt_max_i;",
        "    integer signed bp_index_i;",
        "    integer signed result_i;",
        "    integer signed qr0_i;",
        "    integer signed qr1_i;",
        "    integer signed block_value_i;",
        "    function automatic integer clamp_i;",
        "        input integer value;",
        "        input integer lower;",
        "        input integer upper;",
        "        begin",
        "            if (value < lower) clamp_i = lower;",
        "            else if (value > upper) clamp_i = upper;",
        "            else clamp_i = value;",
        "        end",
        "    endfunction",
        "    function automatic integer min_i;",
        "        input integer left;",
        "        input integer right;",
        "        begin min_i = (left < right) ? left : right; end",
        "    endfunction",
        "    function automatic integer max_i;",
        "        input integer left;",
        "        input integer right;",
        "        begin max_i = (left > right) ? left : right; end",
        "    endfunction",
        "    always_comb begin",
        "        a_i = curr_4;",
        "        b_i = prev_5;",
        "        c_i = prev_4;",
        "        d_i = prev_6;",
        "        e_i = prev_7;",
        "        filt_c_i = (prev_3 + (2 * prev_4) + prev_5 + 2) >>> 2;",
        "        filt_b_i = (prev_4 + (2 * prev_5) + prev_6 + 2) >>> 2;",
        "        filt_d_i = (prev_5 + (2 * prev_6) + prev_7 + 2) >>> 2;",
        "        filt_e_i = (prev_6 + (2 * prev_7) + prev_8 + 2) >>> 2;",
        "        qdiv_i = 1 <<< qLevel;",
        "        qhalf_i = qdiv_i / 2;",
        "        cpnt_max_i = (1 <<< cpnt_bit_depth) - 1;",
        "        qr0_i = $signed(quantized_residual_0);",
        "        qr1_i = $signed(quantized_residual_1);",
        "        diff_i = 0;",
        "        blend_b_i = b_i;",
        "        blend_c_i = c_i;",
        "        blend_d_i = d_i;",
        "        blend_e_i = e_i;",
        "        result_i = 0;",
        "        block_value_i = 0;",
        "        bp_index_i = hPos + 4 - (predType - 2);",
        "        if (bp_index_i < 0) bp_index_i = 0;",
        "        case (bp_index_i)",
        "            0: block_value_i = curr_0;",
        "            1: block_value_i = curr_1;",
        "            2: block_value_i = curr_2;",
        "            3: block_value_i = curr_3;",
        "            4: block_value_i = curr_4;",
        "            5: block_value_i = curr_5;",
        "            6: block_value_i = curr_6;",
        "            default: block_value_i = 0;",
        "        endcase",
        "        diff_i = clamp_i(filt_c_i - c_i, -qhalf_i, qhalf_i);",
        "        blend_c_i = c_i + diff_i;",
        "        diff_i = clamp_i(filt_b_i - b_i, -qhalf_i, qhalf_i);",
        "        blend_b_i = b_i + diff_i;",
        "        diff_i = clamp_i(filt_d_i - d_i, -qhalf_i, qhalf_i);",
        "        blend_d_i = d_i + diff_i;",
        "        diff_i = clamp_i(filt_e_i - e_i, -qhalf_i, qhalf_i);",
        "        blend_e_i = e_i + diff_i;",
        "        if ((hPos / 3) == 0) blend_c_i = a_i;",
        "        if (predType == 0) begin",
        "            if ((hPos % 3) == 0)",
        "                result_i = clamp_i(a_i + blend_b_i - blend_c_i, min_i(a_i, blend_b_i), max_i(a_i, blend_b_i));",
        "            else if ((hPos % 3) == 1)",
        "                result_i = clamp_i(a_i + blend_d_i - blend_c_i + (qr0_i * qdiv_i), min_i(a_i, min_i(blend_b_i, blend_d_i)), max_i(a_i, max_i(blend_b_i, blend_d_i)));",
        "            else",
        "                result_i = clamp_i(a_i + blend_e_i - blend_c_i + ((qr0_i + qr1_i) * qdiv_i), min_i(a_i, min_i(blend_b_i, min_i(blend_d_i, blend_e_i))), max_i(a_i, max_i(blend_b_i, max_i(blend_d_i, blend_e_i))));",
        "        end else if (predType == 1) begin",
        "            if ((hPos % 3) == 0) result_i = a_i;",
        "            else if ((hPos % 3) == 1) result_i = clamp_i(a_i + (qr0_i * qdiv_i), 0, cpnt_max_i);",
        "            else result_i = clamp_i(a_i + ((qr0_i + qr1_i) * qdiv_i), 0, cpnt_max_i);",
        "        end else begin",
        "            result_i = block_value_i;",
        "        end",
        "        return_value = result_i;",
    ]
    if bad:
        lines.append("        return_value = return_value + 1;")
    lines.append("    end")
    return "\n".join(lines)


def generic_body(interface: dict[str, object], semantics: dict[str, object], bad: bool) -> str:
    ports = interface.get("ports", [])
    out = next((p for p in ports if isinstance(p, dict) and p.get("role") == "return_value"), None)
    out_name = str(out.get("name", "return_value")) if isinstance(out, dict) else "return_value"
    expression = str(semantics.get("verilog_expression") or semantics.get("expression") or "0")
    identifiers = {}
    for port in ports:
        if not isinstance(port, dict) or port.get("direction") != "input":
            continue
        name = str(port.get("name"))
        identifiers[normalized_identifier(name)] = name
        if port.get("role"):
            identifiers[normalized_identifier(port.get("role"))] = name

    def replace_identifier(match: re.Match[str]) -> str:
        token = match.group(0)
        return identifiers.get(normalized_identifier(token), token)

    # Semantic expressions are authored in a C-style vocabulary (for example
    # left_recon/cpnt_bit_depth). Rewrite only identifiers that are present in
    # the frozen interface; operators and literals remain untouched.
    expression = re.sub(r"[A-Za-z_][A-Za-z0-9_]*", replace_identifier, expression)
    value = f"({expression})"
    if bad:
        value = f"({value}) + 1"
    return f"    assign {out_name} = {value};"


def render_candidate(contract: dict[str, object], interface: dict[str, object], bad: bool) -> str:
    cid = safe(str(contract.get("contract_id", "candidate")))
    module = f"{cid}_candidate_{'02' if bad else '01'}"
    ports = [p for p in interface.get("ports", []) if isinstance(p, dict)]
    declarations = ",\n".join(port_decl(port) for port in ports)
    semantics = contract.get("semantics", {})
    kind = str(semantics.get("kind", "")) if isinstance(semantics, dict) else ""
    if kind == "quantization":
        body = quantization_body(interface, semantics, bad)
    elif kind == "line_storage":
        body = line_storage_body(interface, bad)
    elif kind == "qp_mapping":
        body = qp_mapping_body(interface, bad)
    elif kind == "max_residual_size":
        body = max_residual_size_body(interface, bad)
    elif kind == "qp_adjusted_pred_size":
        body = qp_adjusted_pred_size_body(interface, bad)
    elif kind == "windowed_sample_predict":
        body = windowed_sample_predict_body(interface, bad)
    else:
        body = generic_body(interface, semantics if isinstance(semantics, dict) else {}, bad)
    return "module " + module + " (\n" + declarations + "\n);\n" + body + "\nendmodule\n"


def main() -> int:
    if len(sys.argv) != 3:
        print("usage: generator_fixture.py request.json output_dir", file=sys.stderr)
        return 2
    request_path = pathlib.Path(sys.argv[1])
    output_dir = pathlib.Path(sys.argv[2])
    request = json.loads(request_path.read_text(encoding="utf-8"))
    contract = request["locked_contract"]
    interface = request["frozen_interface"]
    output_dir.mkdir(parents=True, exist_ok=True)
    (output_dir / "candidate_01.sv").write_text(render_candidate(contract, interface, False), encoding="utf-8")
    (output_dir / "candidate_02.sv").write_text(render_candidate(contract, interface, True), encoding="utf-8")
    telemetry = {
        "generator": "deterministic-fixture-hook",
        "model_calls": 1,
        "tokens_in": len(request.get("c_body", "")) // 4 + len(json.dumps(contract, sort_keys=True)) // 4,
        "tokens_out": 0,
        "candidate_count": 2,
        "contract_id": contract.get("contract_id"),
        "request_keys": sorted(request),
    }
    telemetry["tokens_out"] = sum(len((output_dir / name).read_text(encoding="utf-8")) for name in ("candidate_01.sv", "candidate_02.sv")) // 4
    (output_dir / "telemetry.json").write_text(json.dumps(telemetry, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
