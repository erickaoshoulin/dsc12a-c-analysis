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
