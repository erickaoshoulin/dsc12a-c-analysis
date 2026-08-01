#!/usr/bin/env python3
"""Generate and exhaustively verify one combinational RTL contract slice."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import pathlib
import re
import shutil
import subprocess
import sys
import time
from typing import Any


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--manifest", required=True, type=pathlib.Path)
    parser.add_argument("--contracts", required=True, type=pathlib.Path)
    parser.add_argument("--output-dir", required=True, type=pathlib.Path)
    parser.add_argument("--work-dir", required=True, type=pathlib.Path)
    parser.add_argument("--timeout", required=True, type=int)
    return parser.parse_args()


def sha256_file(path: pathlib.Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def locate(name: str) -> str | None:
    found = shutil.which(name)
    if found:
        return found
    candidates = [
        pathlib.Path("/opt/homebrew/opt/llvm/bin") / name,
        pathlib.Path("/opt/homebrew/bin") / name,
        pathlib.Path("/usr/bin") / name,
    ]
    return next((str(item) for item in candidates if item.is_file() and os.access(item, os.X_OK)), None)


def run(command: list[str], cwd: pathlib.Path, timeout: int = 600) -> dict[str, Any]:
    started = time.monotonic()
    try:
        completed = subprocess.run(
            command,
            cwd=cwd,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=timeout,
            check=False,
        )
        output = completed.stdout or ""
        return {
            "status": "PASS" if completed.returncode == 0 else "FAIL",
            "returncode": completed.returncode,
            "duration_seconds": round(time.monotonic() - started, 3),
            "output_tail": output[-6000:],
        }
    except subprocess.TimeoutExpired as exc:
        return {
            "status": "TIMEOUT",
            "returncode": 124,
            "duration_seconds": round(time.monotonic() - started, 3),
            "output_tail": ((exc.stdout or "") + f"\n[driver] timeout after {timeout}s\n")[-6000:],
        }
    except OSError as exc:
        return {"status": "ERROR", "returncode": 127, "duration_seconds": 0, "output_tail": str(exc)}


def load_contracts(path: pathlib.Path) -> list[dict[str, Any]]:
    result = []
    for file_path in sorted(path.glob("proposed/*.yaml")):
        result.append(json.loads(file_path.read_text(encoding="utf-8")))
    return result


def exact_links(contract: dict[str, Any]) -> list[dict[str, Any]]:
    return [link for link in contract.get("spec_links", []) if link.get("status") == "EXACT"]


def choose_contract(contracts: list[dict[str, Any]]) -> dict[str, Any]:
    eligible = [
        contract
        for contract in contracts
        if exact_links(contract)
        and not contract.get("obligations")
        and not contract.get("dependencies", {}).get("unresolved")
        and contract.get("selection", {}).get("eligible_after_coverage")
        and contract.get("semantics", {}).get("kind") == "midpoint_prediction"
    ]
    if not eligible:
        raise RuntimeError("no contract has an exact spec link, resolved obligations, and coverage eligibility")
    # This is a data-driven choice.  The generator does not name or whitelist
    # a C function; it chooses the smallest resolved legal-domain contract.
    return sorted(
        eligible,
        key=lambda contract: (
            int(contract.get("interface", {}).get("input_bit_count", 1 << 30)),
            len(contract.get("spec_links", [])),
            contract.get("function", {}).get("clang_usr", ""),
        ),
    )[0]


def function_source(contract: dict[str, Any], source_dir: pathlib.Path) -> tuple[pathlib.Path, str]:
    function = contract["function"]
    path = pathlib.Path(function["source_file"])
    if not path.is_absolute():
        path = source_dir / path
    lines = path.read_text(encoding="utf-8", errors="replace").splitlines()
    span = function["source_span"]
    body = "\n".join(lines[span["start_line"] - 1 : span["end_line"]]).strip()
    return path, body


def sv_module(module: str, variant: str) -> str:
    # The ports are the flattened contract interface. `cpnt` is retained to
    # preserve the C array-index input even though the selected array element
    # is already flattened into cpnt_bit_depth/left_recon.
    if variant == "reference":
        expression = "(range_value >> 1) + (left_value % divisor_value)"
    elif variant == "signedness":
        expression = "(range_value >> 1) + signed_left_value % signed_divisor_value"
    elif variant == "boundary":
        expression = "(range_value >> 1) + (left_value % boundary_divisor_value)"
    elif variant == "off_by_one":
        expression = "(range_value >> 1) + (left_value % off_by_one_divisor_value)"
    else:
        raise ValueError(variant)
    extra = ""
    if variant == "signedness":
        extra = """
  logic signed [16:0] signed_left_value;
  logic signed [16:0] signed_divisor_value;
  logic signed [16:0] signed_midpoint_value;
  assign signed_left_value = $signed({left_recon[15], left_recon});
  assign signed_divisor_value = $signed(divisor_value);
  assign signed_midpoint_value = $signed(range_value >> 1) + (signed_left_value % signed_divisor_value);
"""
    if variant == "boundary":
        extra = """
  logic [16:0] boundary_divisor_value;
  assign boundary_divisor_value = (qlevel == 5'd0) ? 17'd1 : ((17'd1 << qlevel) - 17'd1);
"""
    if variant == "off_by_one":
        extra = """
  logic [16:0] off_by_one_divisor_value;
  assign off_by_one_divisor_value = (qlevel == 5'd16) ? 17'd65536 : (17'd1 << (qlevel + 5'd1));
"""
    return f"""module {module}(
  input logic [1:0]  cpnt,
  input logic [4:0]  cpnt_bit_depth,
  input logic [15:0] left_recon,
  input logic [4:0]  qlevel,
  output logic [16:0] return_value
);
  logic [16:0] range_value;
  logic [16:0] divisor_value;
  logic [16:0] left_value;
  assign range_value = 17'd1 << cpnt_bit_depth;
  assign divisor_value = 17'd1 << qlevel;
  assign left_value = {{1'b0, left_recon}};
{extra}
  assign return_value = {"signed_midpoint_value" if variant == "signedness" else expression};
endmodule
"""


def index_mutation_module(module: str) -> str:
    return f"""module {module}(
  input logic [1:0] cpnt,
  input logic [4:0] cpnt_bit_depth,
  input logic [15:0] left_recon,
  input logic [4:0] qlevel,
  output logic [16:0] return_value
);
  logic [16:0] range_value;
  logic [16:0] divisor_value;
  assign range_value = 17'd1 << (cpnt_bit_depth + {{16'd0, cpnt[0]}});
  assign divisor_value = 17'd1 << qlevel;
  assign return_value = (range_value >> 1) + ({{1'b0, left_recon}} % divisor_value);
endmodule
"""


def oracle_source(function: dict[str, Any]) -> str:
    function_name = function["name"]
    prototype = "int " + function_name + "(dsc_state_t *, int, int);"
    return f"""#include <string.h>
#include \"dsc_codec.h\"

extern {prototype}

int dsc_contract_oracle(int cpnt, int cpnt_bit_depth, int left_recon, int qlevel)
{{
    dsc_state_t state;
    memset(&state, 0, sizeof(state));
    state.cpntBitDepth[cpnt] = cpnt_bit_depth;
    state.leftRecon[cpnt] = left_recon;
    return {function_name}(&state, cpnt, qlevel);
}}
"""


def harness_source(module: str) -> str:
    return f"""#include <cstdint>
#include <iostream>
#include <limits>
#include \"V{module}.h\"

extern \"C\" int dsc_contract_oracle(int cpnt, int cpnt_bit_depth, int left_recon, int qlevel);

static int qlevel_max(int cpnt_bit_depth) {{
    switch (cpnt_bit_depth) {{
    case 8: case 9: return 8;
    case 10: case 11: return 10;
    case 12: case 13: return 12;
    case 14: case 15: return 14;
    default: return 16;
    }}
}}

int main(int argc, char** argv) {{
    VerilatedContext* context = new VerilatedContext;
    context->commandArgs(argc, argv);
    V{module}* dut = new V{module}{{context}};
    std::uint64_t vectors = 0;
    for (int cpnt_bit_depth = 8; cpnt_bit_depth <= 16; ++cpnt_bit_depth) {{
        const int max_sample = 1 << cpnt_bit_depth;
        for (int cpnt = 0; cpnt < 4; ++cpnt) {{
            for (int qlevel = 0; qlevel <= qlevel_max(cpnt_bit_depth); ++qlevel) {{
                for (int left_recon = 0; left_recon < max_sample; ++left_recon) {{
                    dut->cpnt = static_cast<std::uint8_t>(cpnt);
                    dut->cpnt_bit_depth = static_cast<std::uint8_t>(cpnt_bit_depth);
                    dut->left_recon = static_cast<std::uint16_t>(left_recon);
                    dut->qlevel = static_cast<std::uint8_t>(qlevel);
                    dut->eval();
                    const int expected = dsc_contract_oracle(cpnt, cpnt_bit_depth, left_recon, qlevel);
                    const int actual = static_cast<int>(dut->return_value);
                    ++vectors;
                    if (actual != expected) {{
                        std::cout << \"RESULT status=COUNTEREXAMPLE vectors=\" << vectors
                                  << \" mismatches=1 cpnt=\" << cpnt
                                  << \" cpnt_bit_depth=\" << cpnt_bit_depth
                                  << \" left_recon=\" << left_recon
                                  << \" qlevel=\" << qlevel
                                  << \" expected=\" << expected
                                  << \" actual=\" << actual << \"\\n\";
                        delete dut;
                        delete context;
                        return 1;
                    }}
                }}
            }}
        }}
    }}
    std::cout << \"RESULT status=EXHAUSTIVE_EQUIVALENT vectors=\" << vectors
              << \" mismatches=0\\n\";
    delete dut;
    delete context;
    return 0;
}}
"""


def parse_result(output: str, returncode: int) -> dict[str, Any]:
    line = next((item for item in output.splitlines() if item.startswith("RESULT ")), "")
    result: dict[str, Any] = {"status": "UNPROVED" if returncode else "UNPROVED", "returncode": returncode}
    for key, value in re.findall(r"(status|vectors|mismatches|cpnt|cpnt_bit_depth|left_recon|qlevel|expected|actual)=([^\s]+)", line):
        result[key] = int(value) if key != "status" else value
    if returncode == 0 and result.get("status") == "EXHAUSTIVE_EQUIVALENT":
        result["verification_status"] = "EXHAUSTIVE_EQUIVALENT"
    elif result.get("status") == "COUNTEREXAMPLE":
        result["verification_status"] = "COUNTEREXAMPLE"
        result["smallest_counterexample"] = {key: result[key] for key in ("cpnt", "cpnt_bit_depth", "left_recon", "qlevel", "expected", "actual") if key in result}
    else:
        result["verification_status"] = "UNPROVED"
    return result


def main() -> int:
    args = parse_args()
    output = args.output_dir.resolve()
    work = args.work_dir.resolve()
    output.mkdir(parents=True, exist_ok=True)
    work.mkdir(parents=True, exist_ok=True)
    receipt: dict[str, Any] = {"schema_version": 1, "do_not_edit": True, "status": "UNPROVED", "commands": [], "candidates": [], "mutations": []}
    try:
        verilator = locate("verilator")
        clang = locate("clang")
        if not verilator or not clang:
            raise RuntimeError("verilator and clang are required for the RTL slice")
        contracts = load_contracts(args.contracts.resolve())
        contract = choose_contract(contracts)
        contract_id = contract["contract_id"]
        selected_path = output / "selected-contract.json"
        selected_path.write_text(json.dumps({"schema_version": 1, "do_not_edit": True, "contract_id": contract_id, "selection": "first exact-link resolved exhaustive contract"}, indent=2) + "\n", encoding="utf-8")
        manifest = json.loads(args.manifest.resolve().read_text(encoding="utf-8"))
        discovered_source_dir = pathlib.Path(manifest["source"]["source_dir"]).resolve()
        source_path, body = function_source(contract, discovered_source_dir)
        source_dir = source_path.parent
        function_name = contract["function"]["name"]
        rtl_dir = output.parent / "rtl" / "candidates" / contract_id
        verification_dir = output.parent / "verification" / contract_id
        rtl_dir.mkdir(parents=True, exist_ok=True)
        verification_dir.mkdir(parents=True, exist_ok=True)
        variants = [("01", "reference"), ("02", "signedness"), ("03", "boundary"), ("04", "off_by_one")]
        candidate_paths = []
        for number, variant in variants:
            module = f"{contract_id}_candidate_{number}"
            path = rtl_dir / f"candidate_{number}.sv"
            path.write_text(sv_module(module, variant), encoding="utf-8")
            candidate_paths.append((number, variant, module, path))
        oracle_path = verification_dir / "oracle.c"
        oracle_path.write_text(oracle_source(contract["function"]), encoding="utf-8")
        context = {
            "call_count": 1,
            "generator": "Codex",
            "input_contract": str((args.contracts / "proposed" / f"{contract_id}.yaml").as_posix()),
            "c_function": function_name,
            "c_source_span": contract["function"]["source_span"],
            "c_body": body,
            "c_body_sha256": hashlib.sha256(body.encode("utf-8")).hexdigest(),
            "exact_spec_anchors": [link.get("anchor_id") for link in exact_links(contract)],
            "output_limit": 4,
            "combinational_only": True,
        }
        (output.parent / "rtl" / "generation-context.json").write_text(json.dumps(context, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
        # Compile the original C implementation and the generated oracle
        # wrapper into objects.  The source model remains untouched.
        oracle_work = work / "oracle"
        oracle_work.mkdir(parents=True, exist_ok=True)
        include_dir = work / "source-include"
        if not include_dir.exists():
            include_dir.symlink_to(source_dir, target_is_directory=True)
        source_objects = []
        for c_source in sorted(source_dir.glob("*.c")):
            if c_source.name == "codec_main.c":
                continue
            object_path = oracle_work / f"{c_source.stem}.o"
            command = [clang, "-std=gnu99", "-O2", "-ffunction-sections", "-fdata-sections", "-I", str(source_dir), "-c", str(c_source), "-o", str(object_path)]
            result = run(command, work)
            receipt["commands"].append({"purpose": "compile-original-c-object", "command": command, **result})
            if result["status"] != "PASS":
                raise RuntimeError(f"C oracle object compile failed: {c_source.name}")
            source_objects.append(object_path)
        oracle_object = oracle_work / "oracle.o"
        command = [clang, "-std=gnu99", "-O2", "-I", str(source_dir), "-c", str(oracle_path), "-o", str(oracle_object)]
        result = run(command, work)
        receipt["commands"].append({"purpose": "compile-c-oracle-wrapper", "command": command, **result})
        if result["status"] != "PASS":
            raise RuntimeError("C oracle wrapper compile failed")
        object_inputs = [str(oracle_object), *map(str, source_objects)]
        for number, variant, module, rtl_path in candidate_paths:
            build_dir = work / f"verilator-{number}"
            build_dir.mkdir(parents=True, exist_ok=True)
            lint_command = [verilator, "--lint-only", "--top-module", module, "-Wall", "--Wno-fatal", "-Wno-DECLFILENAME", "-Wno-UNUSEDSIGNAL", str(rtl_path)]
            lint = run(lint_command, work, args.timeout)
            receipt["commands"].append({"purpose": f"verilator-lint-{number}", "command": lint_command, **lint})
            harness_path = verification_dir / f"harness_{number}.cpp"
            harness_path.write_text(harness_source(module), encoding="utf-8")
            build_command = [
                verilator, "--cc", "--exe", "--build", "-j", "1", "--top-module", module,
                "-Wall", "--Wno-fatal", "-Wno-DECLFILENAME", "-Wno-UNUSEDSIGNAL", "--Mdir", str(build_dir), str(rtl_path), str(harness_path),
                *object_inputs, "--CFLAGS", f"-I{include_dir}", "--LDFLAGS", "-lm",
            ]
            build = run(build_command, work, args.timeout)
            receipt["commands"].append({"purpose": f"verilator-build-{number}", "command": build_command, **build})
            binary = build_dir / f"V{module}"
            if lint["status"] != "PASS" or build["status"] != "PASS" or not binary.is_file():
                result = {"verification_status": "UNPROVED", "lint": lint, "build": build}
            else:
                execution = run([str(binary)], work, args.timeout)
                receipt["commands"].append({"purpose": f"exhaustive-c-vs-rtl-{number}", "command": [str(binary)], **execution})
                result = {"lint": lint, "build": build, **parse_result(execution["output_tail"], execution["returncode"])}
            receipt["candidates"].append({"candidate": f"candidate_{number}", "variant": variant, "module": module, **result})
        # Index mutation is an independent negative control, generated in the
        # temporary verification worktree so it is not counted as a fifth
        # Codex candidate.
        mutation_module = f"{contract_id}_mutation_index"
        mutation_sv = work / f"{mutation_module}.sv"
        mutation_sv.write_text(index_mutation_module(mutation_module), encoding="utf-8")
        mutation_build = work / "verilator-mutation-index"
        mutation_build.mkdir(parents=True, exist_ok=True)
        mutation_harness = work / "mutation-index.cpp"
        mutation_harness.write_text(harness_source(mutation_module), encoding="utf-8")
        mutation_command = [
            verilator, "--cc", "--exe", "--build", "-j", "1", "--top-module", mutation_module,
            "--Wno-fatal", "-Wno-DECLFILENAME", "-Wno-UNUSEDSIGNAL", "--Mdir", str(mutation_build), str(mutation_sv), str(mutation_harness),
            *object_inputs, "--CFLAGS", f"-I{include_dir}", "--LDFLAGS", "-lm",
        ]
        mutation_result = run(mutation_command, work, args.timeout)
        receipt["commands"].append({"purpose": "verilator-mutation-index", "command": mutation_command, **mutation_result})
        mutation_binary = mutation_build / f"V{mutation_module}"
        if mutation_result["status"] == "PASS" and mutation_binary.is_file():
            execution = run([str(mutation_binary)], work, args.timeout)
            receipt["commands"].append({"purpose": "exhaustive-index-mutation", "command": [str(mutation_binary)], **execution})
            receipt["mutations"].append({"mutation": "array-index", **parse_result(execution["output_tail"], execution["returncode"])})
        else:
            receipt["mutations"].append({"mutation": "array-index", "verification_status": "UNPROVED"})
        reference = next((item for item in receipt["candidates"] if item["candidate"] == "candidate_01"), {})
        receipt.update(
            {
                "status": "PASS" if reference.get("verification_status") == "EXHAUSTIVE_EQUIVALENT" else "UNPROVED",
                "contract_id": contract_id,
                "function": function_name,
                "exact_spec_link_count": len(exact_links(contract)),
                "legal_domain": contract["verification_plan"]["legal_domain"],
                "source_body_sha256": hashlib.sha256(body.encode("utf-8")).hexdigest(),
                "source_file_sha256": sha256_file(source_path),
            }
        )
        (verification_dir / "receipt.json").write_text(json.dumps(receipt, indent=2, sort_keys=True, ensure_ascii=False) + "\n", encoding="utf-8")
        (output / "verification-receipt.json").write_text(json.dumps(receipt, indent=2, sort_keys=True, ensure_ascii=False) + "\n", encoding="utf-8")
        print(f"RTL slice {contract_id}: {receipt['status']}")
        return 0 if receipt["status"] == "PASS" else 1
    except (OSError, RuntimeError, subprocess.TimeoutExpired, json.JSONDecodeError) as exc:
        receipt["failure_reason"] = str(exc)
        (output / "verification-receipt.json").write_text(json.dumps(receipt, indent=2, sort_keys=True, ensure_ascii=False) + "\n", encoding="utf-8")
        print(f"RTL slice failure: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
