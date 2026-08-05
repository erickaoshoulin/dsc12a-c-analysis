import json
import pathlib
import shutil
import subprocess
import tempfile
import unittest

from tools.cicd_agent import Agent
from tools.encode_rate_control_adapter import (
    write_rate_control_encode_overlay_sources,
)


ROOT = pathlib.Path(__file__).resolve().parents[1]
CONTRACT_PATH = ROOT / "rtl/encode-candidates/selected-rate-control-encode-transition/provisional-contract.json"
CANDIDATE_PATH = ROOT / "rtl/encode-candidates/selected-rate-control-encode-transition/candidate_01.sv"


class EncodeRateControlAdapterTests(unittest.TestCase):
    def test_real_contract_emits_complete_adapter_and_compiles(self):
        contract = json.loads(CONTRACT_PATH.read_text(encoding="utf-8"))
        manifest = json.loads((ROOT / "spec/manifest.json").read_text(encoding="utf-8"))
        source_dir = pathlib.Path(manifest["source"]["source_dir"])

        with tempfile.TemporaryDirectory() as directory:
            generated = pathlib.Path(directory)
            for name in ("dsc_types.h", "fifo.h"):
                shutil.copy2(source_dir / name, generated / name)

            paths = write_rate_control_encode_overlay_sources(
                Agent(ROOT, "test"),
                contract,
                generated,
                contract["contract_id"],
                CANDIDATE_PATH,
            )

            self.assertEqual(
                set(paths),
                {"header", "abi", "overlay", "bridge", "main", "candidate", "composition"},
            )
            composition = paths["composition"]
            self.assertEqual(
                composition["adapter_kind"],
                "explicit_bounded_rate_control_encode_transition",
            )
            self.assertEqual(composition["rtl_input_count"], 114)
            self.assertEqual(len(composition["rtl_bindings"]), 114)
            self.assertEqual(
                len(composition["rtl_bindings"]),
                len(composition["frozen_input_ports"]),
            )
            self.assertEqual(composition["state_output_count"], 14)
            self.assertEqual(len(composition["chunk_write_events"]), 3)
            self.assertTrue(composition["c_snapshot_restores_every_touched_scalar_before_mode_selection"])
            self.assertTrue(composition["c_snapshot_restores_every_touched_chunk_byte_before_mode_selection"])
            self.assertTrue(composition["rtl_return_commits_only_rtl"])

            abi = paths["abi"].read_text(encoding="utf-8")
            overlay = paths["overlay"].read_text(encoding="utf-8")
            bridge = paths["bridge"].read_text(encoding="utf-8")
            generated_text = "\n".join((abi, overlay, bridge))

            for field in (
                "cfg_bits_per_component",
                "cfg_bits_per_pixel",
                "cfg_rc_buf_thresh_13",
                "cfg_range_min_qp_14",
                "cfg_range_max_qp_14",
                "cfg_range_bpg_offset_14",
                "state_codedgroupsize",
                "state_midpoint_selected_3",
                "state_rc_size_unit_3",
                "state_vpos",
            ):
                self.assertIn(field, generated_text)
            for field in (
                "state_bitsavemode_out",
                "state_bufferfullness_out",
                "state_prevrange_out",
                "state_stqp_out",
                "fatal_error",
                "fatal_error_code",
                "chunk_write_enable[2]",
                "chunk_write_index[2]",
                "chunk_write_value[2]",
            ):
                self.assertIn(field, generated_text)

            self.assertIn("extern void RateControl_original", overlay)
            self.assertIn("dsc_state->isEncoder != 1", overlay)
            self.assertIn("RateControl_original(dsc_cfg, dsc_state", overlay)
            self.assertIn(
                "(state->chunkPixelTimes + group_size) / state->sliceWidth",
                overlay,
            )
            self.assertIn("stage < 3 && stage < group_size", overlay)
            self.assertIn("output->chunk_write_enable[stage] = 1", overlay)
            self.assertIn("int expected_chunk_index = base", overlay)
            self.assertIn(
                "dsc_cicd_chunk_base + event < dsc_cicd_chunk_capacity",
                overlay,
            )
            self.assertIn("dsc_state_t private_state = *state", overlay)
            self.assertIn("private_state.chunkSizes = shadow", overlay)
            self.assertIn("dsc_cicd_snapshot_rate_control", overlay)
            self.assertIn("dsc_cicd_restore_rate_control", overlay)
            self.assertIn("++dsc_cicd_rtl_invocations", overlay)
            self.assertIn("return 0; /* C_ONLY", overlay)
            self.assertNotIn("useMidpoint", generated_text)
            self.assertNotIn("use_midpoint", generated_text)

            restore = overlay.index("dsc_cicd_restore_rate_control")
            mode = overlay.index("int mode = dsc_cicd_mode()")
            self.assertLess(restore, mode)
            self.assertIn("dsc_cicd_output_mismatch", overlay)
            self.assertIn("chunk_write_index", overlay)
            self.assertIn("dsc_cicd_rtl_output", overlay)
            self.assertNotIn("dsc_cicd_rtl_output = dsc_cicd_c_output", overlay)

            clang = shutil.which("clang")
            if clang:
                result = subprocess.run(
                    [
                        clang,
                        "-std=gnu99",
                        "-Wall",
                        "-Wextra",
                        "-Werror",
                        "-fsyntax-only",
                        "-I",
                        str(generated),
                        str(paths["overlay"]),
                    ],
                    cwd=ROOT,
                    text=True,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.STDOUT,
                    check=False,
                )
                self.assertEqual(result.returncode, 0, result.stdout)

            verilator = shutil.which("verilator")
            if verilator:
                lint = subprocess.run(
                    [
                        verilator,
                        "--lint-only",
                        "--Wno-fatal",
                        "--top-module",
                        contract["contract_id"],
                        str(CANDIDATE_PATH),
                    ],
                    cwd=ROOT,
                    text=True,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.STDOUT,
                    check=False,
                )
                self.assertEqual(lint.returncode, 0, lint.stdout)

                clangxx = shutil.which("clang++")
                if clangxx:
                    verilated = generated / "verilated"
                    compile_rtl = subprocess.run(
                        [
                            verilator,
                            "--cc",
                            "--Mdir",
                            str(verilated),
                            "--top-module",
                            contract["contract_id"],
                            str(CANDIDATE_PATH),
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
                            str(generated),
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
