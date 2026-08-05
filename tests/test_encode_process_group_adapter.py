import json
import pathlib
import shutil
import subprocess
import tempfile
import unittest

from tools.cicd_agent import Agent


ROOT = pathlib.Path(__file__).resolve().parents[1]
SOURCE = pathlib.Path(
    "/Users/snow/Desktop/Display Stream Compression (DSC)/DSC 1.2a/"
    "DSC_model_20210623/source"
)
ARTIFACT = ROOT / "rtl/encode-candidates/selected-process-group-encode-transition"


class EncodeProcessGroupAdapterTests(unittest.TestCase):
    def test_real_contract_emits_deep_snapshot_and_clocked_memory_adapter(self):
        contract = json.loads((ARTIFACT / "provisional-contract.json").read_text())
        self.assertEqual(
            contract["semantics"]["kind"],
            "bounded_process_group_encode_transition",
        )
        with tempfile.TemporaryDirectory() as directory:
            root = pathlib.Path(directory)
            candidate = root / "candidate_01.sv"
            candidate.write_bytes((ARTIFACT / "candidate_01.sv").read_bytes())
            paths = Agent(root, "process-group-adapter-test").write_overlay_sources(
                contract,
                root,
                contract["rtl"]["module"],
                candidate,
            )
            composition = paths["composition"]
            frozen_inputs = [
                item["name"] for item in contract["interface"]["ports"]
                if item["direction"] == "input"
            ]
            self.assertEqual(composition["frozen_input_ports"], frozen_inputs)
            self.assertEqual(len(composition["rtl_bindings"]), len(frozen_inputs))
            self.assertTrue(composition["c_oracle_uses_deep_fifo_and_frame_snapshots"])
            self.assertTrue(composition["c_oracle_state_is_restored_before_rtl"])
            self.assertTrue(composition["rtl_services_external_fifo_and_frame_memory_requests"])
            self.assertTrue(composition["rtl_return_commits_only_rtl_fifo_frame_and_cursor_state"])
            self.assertTrue(composition["inactive_ssp_scalar_state_is_passthrough_checked"])
            self.assertTrue(composition["inactive_ssp_memory_requests_are_guarded"])
            self.assertTrue(composition["frame_zero_bits_match_putbits_partial_byte_semantics"])
            self.assertTrue(composition["candidate_hash_and_module_are_pinned"])
            self.assertTrue(composition["rtl_port_shapes_are_pinned_for_verilator_arrays"])
            self.assertEqual(composition["bridge_cycle_bound"], 10000)
            overlay = paths["overlay"].read_text()
            bridge = paths["bridge"].read_text()
            c_only = overlay.split("if (mode == 0)", 1)[1].split("}", 1)[0]
            self.assertIn("ProcessGroupEnc_original", c_only)
            self.assertNotIn("dsc_cicd_rtl", c_only)
            self.assertIn("dsc_cicd_restore_fifo", overlay)
            self.assertIn("memcmp", overlay)
            self.assertIn("dsc_cicd_snapshot_inactive_fifo", overlay)
            self.assertIn("dsc_cicd_validate_bridge_domain", overlay)
            self.assertIn("service_low_phase", bridge)
            self.assertIn("frame_mem_write_bit_mask", bridge)
            self.assertIn("DSC_CICD_PG_MAX_CYCLES", bridge)
            self.assertIn("putbits() clears a byte only when it starts that byte", bridge)
            self.assertIn("if (mask == 0xffu)", bridge)

    def test_contract_rejects_changed_candidate_and_verilator_port_shape(self):
        contract = json.loads((ARTIFACT / "provisional-contract.json").read_text())
        with tempfile.TemporaryDirectory() as directory:
            root = pathlib.Path(directory)
            candidate = root / "candidate_01.sv"
            candidate.write_bytes((ARTIFACT / "candidate_01.sv").read_bytes())
            bad_candidate = root / "bad_candidate.sv"
            bad_candidate.write_bytes(candidate.read_bytes() + b"\n")
            with self.assertRaisesRegex(RuntimeError, "candidate bytes changed"):
                Agent(root, "process-group-adapter-bad-candidate").write_overlay_sources(
                    contract, root, contract["rtl"]["module"], bad_candidate
                )

            bad_contract = json.loads(json.dumps(contract))
            for port in bad_contract["interface"]["ports"]:
                if port["name"] == "enc_balance_mem_read_addr":
                    port["width"] = "32"
                    break
            with self.assertRaisesRegex(RuntimeError, "port ABI changed"):
                Agent(root, "process-group-adapter-bad-port").write_overlay_sources(
                    bad_contract, root, contract["rtl"]["module"], candidate
                )

    def test_verilator_bridge_runs_clocked_bit_order_and_inactive_passthrough(self):
        verilator = shutil.which("verilator")
        if not verilator:
            self.skipTest("Verilator is unavailable")
        contract = json.loads((ARTIFACT / "provisional-contract.json").read_text())
        with tempfile.TemporaryDirectory() as directory:
            root = pathlib.Path(directory)
            candidate = root / "candidate_01.sv"
            candidate.write_bytes((ARTIFACT / "candidate_01.sv").read_bytes())
            paths = Agent(root, "process-group-adapter-runtime").write_overlay_sources(
                contract, root, contract["rtl"]["module"], candidate
            )
            harness = root / "bridge_harness.cpp"
            harness.write_text(
                r'''
#include <cstdint>
#include <cstdio>
#include <cstring>
#include "dsc_cicd_rtl_abi.h"

static bool same_fifo(const dsc_cicd_pg_fifo_t &left,
                      const dsc_cicd_pg_fifo_t &right) {
    return left.data == right.data && left.size_bits == right.size_bits &&
        left.fullness == right.fullness && left.read_ptr == right.read_ptr &&
        left.write_ptr == right.write_ptr &&
        left.max_fullness == right.max_fullness &&
        left.byte_ctr == right.byte_ctr;
}

int main() {
    uint8_t enc[4][8] = {
        {0xa5, 0x3c}, {0x5a, 0xc3}, {0x96, 0x69}, {0xf0, 0x0f}
    };
    uint8_t shifter[4][32] = {};
    uint8_t se_size[4][8] = {};
    uint8_t frame[64];
    std::memset(frame, 0xa6, sizeof(frame));

    dsc_cicd_pg_input_t input{};
    input.is_encoder = 1;
    input.num_ssps = 3;
    input.mux_word_size = 48;
    input.post_mux_num_bits = 3;
    input.frame_capacity_bits = 155;
    input.frame_data = frame;
    for (int lane = 0; lane < 4; ++lane) {
        input.max_se_size[lane] = 68;
        input.enc_balance[lane] = {enc[lane], 64, 16, 0, 16, 16, 9};
        input.shifter[lane] = {shifter[lane], 256, 0, 0, 0, 0, 10};
        input.se_size[lane] = {se_size[lane], 64, 8, 0, 8, 8, 11};
    }
    const dsc_cicd_pg_fifo_t inactive_enc = input.enc_balance[3];
    const dsc_cicd_pg_fifo_t inactive_shifter = input.shifter[3];
    const dsc_cicd_pg_fifo_t inactive_se_size = input.se_size[3];

    dsc_cicd_pg_output_t output{};
    dsc_cicd_rtl(&input, &output);
    if (output.bridge_error || output.illegal_domain || output.fifo_underflow ||
        output.fifo_overflow || output.frame_overflow || output.se_size_overflow)
        return 1;
    if (output.post_mux_num_bits != 147 || output.cycles != 408)
        return 2;
    const uint8_t expected[] = {
        0xb6, 0xa7, 0x80, 0x00, 0x00, 0x00,
        0x0b, 0x58, 0x60, 0x00, 0x00, 0x00,
        0x12, 0xcd, 0x20, 0x00, 0x00, 0x00, 0x00
    };
    if (std::memcmp(frame, expected, sizeof(expected)) != 0)
        return 3;
    if (!same_fifo(input.enc_balance[3], inactive_enc) ||
        !same_fifo(input.shifter[3], inactive_shifter) ||
        !same_fifo(input.se_size[3], inactive_se_size))
        return 4;
    return 0;
}
''',
                encoding="utf-8",
            )
            verilated = root / "verilated"
            build = subprocess.run(
                [
                    verilator,
                    "--cc",
                    "--exe",
                    "--build",
                    "--Wno-fatal",
                    "--Mdir",
                    str(verilated),
                    "--top-module",
                    contract["rtl"]["module"],
                    str(candidate),
                    str(paths["bridge"]),
                    str(harness),
                ],
                cwd=ROOT,
                text=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                check=False,
            )
            self.assertEqual(build.returncode, 0, build.stdout)
            executable = verilated / f"V{contract['rtl']['module']}"
            run = subprocess.run(
                [str(executable)],
                text=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                check=False,
            )
            self.assertEqual(run.returncode, 0, run.stdout)

    def test_generated_overlay_is_valid_c_against_original_headers(self):
        if not SOURCE.is_dir():
            self.skipTest("immutable DSC source is unavailable")
        clang = shutil.which("clang")
        if not clang:
            self.skipTest("clang is unavailable")
        contract = json.loads((ARTIFACT / "provisional-contract.json").read_text())
        with tempfile.TemporaryDirectory() as directory:
            root = pathlib.Path(directory)
            for name in ("dsc_types.h", "fifo.h"):
                shutil.copy2(SOURCE / name, root / name)
            candidate = root / "candidate_01.sv"
            candidate.write_bytes((ARTIFACT / "candidate_01.sv").read_bytes())
            paths = Agent(root, "process-group-adapter-compile").write_overlay_sources(
                contract, root, contract["rtl"]["module"], candidate
            )
            result = subprocess.run(
                [
                    clang,
                    "-std=gnu99",
                    "-Wall",
                    "-Wextra",
                    "-Werror",
                    "-fsyntax-only",
                    "-I",
                    str(root),
                    str(paths["overlay"]),
                ],
                text=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                check=False,
            )
            self.assertEqual(result.returncode, 0, result.stdout)

            verilator = shutil.which("verilator")
            clangxx = shutil.which("clang++")
            if not verilator or not clangxx:
                self.skipTest("Verilator/clang++ is unavailable")
            verilated = root / "verilated"
            compile_rtl = subprocess.run(
                [
                    verilator,
                    "--cc",
                    "--Wno-fatal",
                    "--Mdir",
                    str(verilated),
                    "--top-module",
                    contract["rtl"]["module"],
                    str(candidate),
                ],
                cwd=ROOT,
                text=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                check=False,
            )
            self.assertEqual(compile_rtl.returncode, 0, compile_rtl.stdout)
            verilator_root = subprocess.check_output(
                [verilator, "--getenv", "VERILATOR_ROOT"],
                cwd=ROOT,
                text=True,
            ).strip()
            bridge_compile = subprocess.run(
                [
                    clangxx,
                    "-std=c++17",
                    "-w",
                    "-fsyntax-only",
                    "-I",
                    str(root),
                    "-I",
                    str(verilated),
                    "-I",
                    str(pathlib.Path(verilator_root) / "include"),
                    str(paths["bridge"]),
                ],
                cwd=ROOT,
                text=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                check=False,
            )
            self.assertEqual(bridge_compile.returncode, 0, bridge_compile.stdout)


if __name__ == "__main__":
    unittest.main()
