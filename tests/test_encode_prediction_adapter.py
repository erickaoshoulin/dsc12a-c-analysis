"""Focused source and footprint tests for the encoder PredictionLoop adapter."""

from __future__ import annotations

import copy
import json
import pathlib
import shutil
import subprocess
import tempfile
import unittest

from tools.encode_prediction_adapter import write_prediction_encode_overlay_sources
from tools.generate_prediction_encode import (
    build_prediction_encode_contract,
    discover_prediction_encode_candidates,
    load_pinned_dependencies,
    render_prediction_encode_rtl,
)


ROOT = pathlib.Path(__file__).resolve().parents[1]
SOURCE = pathlib.Path(
    "/Users/snow/Desktop/Display Stream Compression (DSC)/DSC 1.2a/"
    "DSC_model_20210623/source"
)


class PredictionEncodeAdapterTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        if not SOURCE.is_dir():
            raise unittest.SkipTest(f"immutable DSC source is unavailable: {SOURCE}")
        cls.contract = cls._build_real_contract()

    @classmethod
    def _build_real_contract(cls) -> dict:
        functions = json.loads((ROOT / "facts/functions.json").read_text(encoding="utf-8"))
        candidates = json.loads((ROOT / "facts/candidates.json").read_text(encoding="utf-8"))
        coverage = json.loads((ROOT / "coverage/coverage.json").read_text(encoding="utf-8"))
        dependencies = load_pinned_dependencies(ROOT)
        matches = discover_prediction_encode_candidates(
            functions, candidates, coverage, SOURCE, dependencies
        )
        if len(matches) != 1:
            raise unittest.SkipTest("the real bounded PredictionLoop contract is unavailable")
        return build_prediction_encode_contract(matches[0], SOURCE, dependencies)

    def _emit(self, directory: pathlib.Path) -> dict:
        candidate = directory / "candidate.sv"
        candidate.write_text(render_prediction_encode_rtl(self.contract), encoding="utf-8")
        return write_prediction_encode_overlay_sources(
            None,
            self.contract,
            directory,
            self.contract["contract_id"],
            candidate,
        )

    def test_emits_complete_real_predictionloop_footprint(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            paths = self._emit(pathlib.Path(directory))
            composition = paths["composition"]
            input_ports = [
                port["name"]
                for port in self.contract["interface"]["ports"]
                if port["direction"] == "input"
            ]
            output_ports = [
                port["name"]
                for port in self.contract["interface"]["ports"]
                if port["direction"] == "output"
            ]
            self.assertEqual(composition["rtl_input_count"], 214)
            self.assertEqual(composition["rtl_output_count"], 78)
            self.assertEqual(composition["frozen_input_ports"], input_ports)
            self.assertEqual(composition["state_outputs"], output_ports)
            self.assertEqual(len(composition["rtl_bindings"]), len(input_ports))
            self.assertEqual(
                set(paths),
                {"header", "abi", "overlay", "bridge", "main", "candidate", "composition"},
            )
            for key in ("header", "abi", "overlay", "bridge", "main", "candidate"):
                self.assertTrue(paths[key].is_file(), key)

            bridge = paths["bridge"].read_text(encoding="utf-8")
            for port in input_ports:
                self.assertIn(f"dut.{port} =", bridge)
            for port in output_ports:
                self.assertIn(f"dut.{port}", bridge)

    def test_source_restores_oracle_and_commits_only_selected_mode(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            paths = self._emit(pathlib.Path(directory))
            overlay = paths["overlay"].read_text(encoding="utf-8")
            abi = paths["abi"].read_text(encoding="utf-8")
            composition = paths["composition"]

            self.assertIn("dsc_state_t dsc_cicd_c_state = *dsc_state;", overlay)
            for field in (
                "primaryQp",
                "quantizedResidual",
                "quantizedResidualMid",
                "midpointRecon",
                "maxError",
                "maxMidError",
                "currLine",
            ):
                self.assertIn(field, overlay)
            for flag in (
                "domain_valid",
                "illegal_domain",
                "bound_violation",
                "midpoint_clamp_violation",
                "arithmetic_domain_violation",
            ):
                self.assertIn(f"c_output->{flag} != rtl_output->{flag}", overlay)
            self.assertIn("dsc_cicd_note_rtl_invocation();", overlay)
            self.assertIn("dsc_cicd_rtl(&dsc_cicd_input, &dsc_cicd_rtl_output);", overlay)
            self.assertIn("if (mode == 0)", overlay)
            self.assertIn("if (mode == 2)", overlay)
            self.assertIn("dsc_state->isEncoder != 1", overlay)
            self.assertIn("SHADOW compares RTL but commits the restored C oracle image", overlay)
            self.assertIn("tap < DSC_CICD_PRED_PREV_USED_TAPS", overlay)
            self.assertIn("unit < dsc_state->unitsPerGroup", overlay)
            self.assertIn("!state->currLine[cpnt]", overlay)
            self.assertIn("int32_t curr_line[DSC_CICD_PRED_UNITS][DSC_CICD_PRED_CURR_TAPS]", abi)
            self.assertNotIn("rust", overlay.lower())
            self.assertTrue(composition["rtl_return_commits_only_rtl_outputs_in_source_order"])
            self.assertTrue(composition["c_only_restores_and_commits_c_oracle_state"])
            self.assertTrue(composition["shadow_commits_c_oracle_state"])
            self.assertTrue(
                composition["decoder_calls_bypass_encode_rtl_and_use_original_c"]
            )

    def test_rejects_a_changed_frozen_footprint(self) -> None:
        contract = copy.deepcopy(self.contract)
        contract["interface"]["ports"] = [
            port
            for port in contract["interface"]["ports"]
            if port["name"] != "state_max_error_3_out"
        ]
        with tempfile.TemporaryDirectory() as directory:
            with self.assertRaisesRegex(RuntimeError, "frozen full footprint"):
                write_prediction_encode_overlay_sources(
                    None,
                    contract,
                    pathlib.Path(directory),
                    contract["contract_id"],
                    pathlib.Path(directory) / "candidate.sv",
                )

    def test_overlay_compiles_and_candidate_lints_when_tools_are_available(self) -> None:
        clang = shutil.which("clang")
        verilator = shutil.which("verilator")
        if not clang and not verilator:
            self.skipTest("neither clang nor verilator is installed")
        with tempfile.TemporaryDirectory() as directory:
            root = pathlib.Path(directory)
            paths = self._emit(root)
            if clang:
                syntax = subprocess.run(
                    [
                        clang,
                        "-std=gnu99",
                        "-fsyntax-only",
                        "-I",
                        str(SOURCE),
                        str(paths["overlay"]),
                    ],
                    cwd=root,
                    text=True,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.STDOUT,
                    check=False,
                )
                self.assertEqual(syntax.returncode, 0, syntax.stdout)
            if verilator:
                lint = subprocess.run(
                    [
                        verilator,
                        "--lint-only",
                        "--Wno-fatal",
                        "--top-module",
                        self.contract["contract_id"],
                        str(paths["candidate"]),
                    ],
                    cwd=root,
                    text=True,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.STDOUT,
                    check=False,
                )
                self.assertEqual(lint.returncode, 0, lint.stdout)


if __name__ == "__main__":
    unittest.main()
