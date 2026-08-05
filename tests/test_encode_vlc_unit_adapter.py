from __future__ import annotations

import copy
import json
import pathlib
import shutil
import subprocess
import tempfile
import unittest

from tools.cicd_agent import Agent
from tools.encode_vlc_unit_adapter import write_vlc_unit_encode_overlay_sources
from tools.verify_decode_integration import route_adapter_child_dispatchers


ROOT = pathlib.Path(__file__).resolve().parents[1]
CONTRACT_PATH = (
    ROOT
    / "rtl/encode-candidates/selected-vlc-unit-encode-transition/"
    "provisional-contract.json"
)
CANDIDATE_PATH = (
    ROOT
    / "rtl/encode-candidates/selected-vlc-unit-encode-transition/candidate_01.sv"
)
MODEL_SOURCE = pathlib.Path(
    "/Users/snow/Desktop/Display Stream Compression (DSC)/DSC 1.2a/"
    "DSC_model_20210623/source"
)


def _ports(contract: dict, direction: str) -> list[str]:
    return [
        str(port["name"])
        for port in contract["interface"]["ports"]
        if port.get("direction") == direction
    ]


class EncodeVlcUnitAdapterTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        if not MODEL_SOURCE.is_dir():
            raise unittest.SkipTest(f"immutable DSC source is unavailable: {MODEL_SOURCE}")
        if not CONTRACT_PATH.is_file() or not CANDIDATE_PATH.is_file():
            raise unittest.SkipTest("the selected VLCUnit Encode candidate is unavailable")
        cls.contract = json.loads(CONTRACT_PATH.read_text(encoding="utf-8"))

    def _emit(self, directory: pathlib.Path) -> dict:
        return write_vlc_unit_encode_overlay_sources(
            Agent(ROOT, "test"),
            self.contract,
            directory,
            self.contract["contract_id"],
            CANDIDATE_PATH,
        )

    def test_real_contract_emits_the_complete_abi_and_composition(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            paths = self._emit(pathlib.Path(directory))
            self.assertEqual(
                set(paths),
                {"header", "abi", "overlay", "bridge", "main", "candidate", "composition"},
            )
            for key in ("header", "abi", "overlay", "bridge", "main", "candidate"):
                self.assertTrue(paths[key].is_file(), key)

            composition = paths["composition"]
            self.assertEqual(composition["semantic_kind"], "bounded_vlc_unit_encode_transition")
            self.assertEqual(composition["rtl_input_count"], 82)
            self.assertEqual(composition["rtl_output_count"], 62)
            self.assertEqual(composition["frozen_input_ports"], _ports(self.contract, "input"))
            self.assertEqual(composition["state_outputs"], _ports(self.contract, "output"))
            self.assertEqual(len(composition["rtl_bindings"]), 82)
            self.assertEqual(composition["command_stream_bound"], 9)
            self.assertTrue(composition["command_stream_is_bounded_and_source_ordered"])
            self.assertTrue(composition["command_legality_and_order_compared"])
            self.assertTrue(composition["complete_final_state_and_fifo_image_compared"])
            self.assertTrue(composition["c_oracle_uses_deep_private_state"])
            self.assertTrue(composition["c_snapshot_restores_every_directly_written_state_field"])
            self.assertTrue(composition["c_snapshot_restores_all_addbits_fifo_effects"])
            self.assertTrue(composition["all_rtl_modes_count_actual_verilator_invocation"])

            bridge = paths["bridge"].read_text(encoding="utf-8")
            for name in _ports(self.contract, "input") + _ports(self.contract, "output"):
                self.assertIn(f"dut.{name}", bridge)

            abi = paths["abi"].read_text(encoding="utf-8")
            for name in (
                "helper_required_size[DSC_CICD_VLC_SAMPLES]",
                "state_quantized_residual_mid[DSC_CICD_VLC_UNITS][DSC_CICD_VLC_SAMPLES]",
                "state_midpoint_selected[DSC_CICD_VLC_UNITS]",
                "command_valid[DSC_CICD_VLC_MAX_COMMANDS]",
                "command_ctype[DSC_CICD_VLC_MAX_COMMANDS]",
                "command_data[DSC_CICD_VLC_MAX_COMMANDS]",
                "command_nbits[DSC_CICD_VLC_MAX_COMMANDS]",
            ):
                self.assertIn(name, abi)

    def test_overlay_routes_addbits_child_and_enforces_mode_commit_rules(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            paths = self._emit(pathlib.Path(directory))
            overlay = paths["overlay"].read_text(encoding="utf-8")

            routed, receipts = route_adapter_child_dispatchers(
                overlay,
                own_function=self.contract["function"]["name"],
                candidates=[
                    {
                        "function": "AddBits",
                        "slug": "addbits_encode_transition",
                    }
                ],
            )
            self.assertTrue(receipts)
            self.assertIn("dsc_cicd_addbits_encode_transition_invoke", routed)
            self.assertNotIn("extern void AddBits(", routed)
            self.assertNotIn("fifo_put_bits", overlay)
            self.assertIn("extern void AddBits(", overlay)

            self.assertIn("VLCUnit_original", overlay)
            self.assertIn("dsc_state_t dsc_cicd_c_state", overlay)
            self.assertIn("dsc_cicd_clone_fifo", overlay)
            self.assertIn("dsc_cicd_restore_directly_written_state", overlay)
            self.assertIn("dsc_cicd_replay_command_stream", overlay)
            self.assertIn(
                "for (int command = 0; command < output->command_count; ++command)",
                overlay,
            )
            self.assertIn("!output->source_order_valid", overlay)
            self.assertIn("command < count", overlay)
            self.assertIn("dsc_cicd_rtl(&dsc_cicd_input, &dsc_cicd_rtl_output)", overlay)
            self.assertIn("dsc_cicd_note_rtl_invocation();", overlay)
            self.assertNotIn("rust", overlay.lower())

            restore = overlay.index("dsc_cicd_restore_directly_written_state")
            mode = overlay.index("int mode = dsc_cicd_mode()")
            self.assertLess(restore, mode)
            self.assertIn("if (mode == 0)", overlay)
            self.assertIn("if (mode == 2)", overlay)
            self.assertIn(
                "dsc_cicd_commit_c_oracle(dsc_state, &dsc_cicd_rtl_state)",
                overlay,
            )
            self.assertIn(
                "dsc_cicd_commit_c_oracle(dsc_state, &dsc_cicd_c_state)",
                overlay,
            )

    def test_changed_command_footprint_is_rejected(self) -> None:
        contract = copy.deepcopy(self.contract)
        contract["interface"]["ports"] = [
            port
            for port in contract["interface"]["ports"]
            if port["name"] != "addbits_cmd_nbits_8"
        ]
        with tempfile.TemporaryDirectory() as directory:
            with self.assertRaisesRegex(RuntimeError, "frozen full footprint"):
                write_vlc_unit_encode_overlay_sources(
                    Agent(ROOT, "test"),
                    contract,
                    pathlib.Path(directory),
                    contract["contract_id"],
                    CANDIDATE_PATH,
                )

    def test_generated_c_bridge_and_candidate_pass_practical_checks(self) -> None:
        clang = shutil.which("clang")
        verilator = shutil.which("verilator")
        if not clang and not verilator:
            self.skipTest("neither clang nor verilator is installed")

        with tempfile.TemporaryDirectory() as directory:
            generated = pathlib.Path(directory)
            paths = self._emit(generated)

            if clang:
                syntax = subprocess.run(
                    [
                        clang,
                        "-std=gnu99",
                        "-Wall",
                        "-Wextra",
                        "-Werror",
                        "-fsyntax-only",
                        "-I",
                        str(generated),
                        "-I",
                        str(MODEL_SOURCE),
                        str(paths["overlay"]),
                    ],
                    cwd=ROOT,
                    text=True,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.STDOUT,
                    check=False,
                )
                self.assertEqual(syntax.returncode, 0, syntax.stdout)

            if not verilator:
                return

            lint = subprocess.run(
                [
                    verilator,
                    "--lint-only",
                    "--Wno-fatal",
                    "--top-module",
                    self.contract["contract_id"],
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
            if not clangxx:
                return
            verilated = generated / "verilated"
            compile_rtl = subprocess.run(
                [
                    verilator,
                    "--cc",
                    "--Wno-fatal",
                    "--Mdir",
                    str(verilated),
                    "--top-module",
                    self.contract["contract_id"],
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
