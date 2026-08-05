import copy
import json
import pathlib
import shutil
import subprocess
import tempfile
import unittest

from tools.encode_history_adapters import (
    HISTORY_QERR_KIND,
    HISTORY_REDUCTION_KIND,
    write_history_encode_overlay_sources,
)
from tools.verify_decode_integration import route_adapter_child_dispatchers


ROOT = pathlib.Path(__file__).resolve().parents[1]
MODEL_SOURCE = pathlib.Path(
    "/Users/snow/Desktop/Display Stream Compression (DSC)/DSC 1.2a/"
    "DSC_model_20210623/source"
)


class _MetricsAgent:
    calls = 0

    @classmethod
    def overlay_runtime_metrics_source(cls):
        cls.calls += 1
        return (
            "static unsigned long dsc_cicd_mismatches;\n"
            "static unsigned long dsc_cicd_calls;\n"
            "static unsigned long dsc_cicd_rtl_invocations;\n"
            "static int dsc_cicd_report_registered;\n"
            "static void dsc_cicd_report(void) {}\n"
            "static void dsc_cicd_note_call(int mode) {\n"
            "    ++dsc_cicd_calls;\n"
            "    if (mode != 0) ++dsc_cicd_rtl_invocations;\n"
            "}\n"
        )


def _contract(path: pathlib.Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def _real_contracts():
    return [
        (
            _contract(
                ROOT
                / "rtl/encode-candidates/selected-history-reduction-transition/"
                "provisional-contract.json"
            ),
            ROOT
            / "rtl/encode-candidates/selected-history-reduction-transition/"
            "candidate_01.sv",
        ),
        (
            _contract(
                ROOT
                / "rtl/encode-candidates/selected-history-qerr-transition/"
                "provisional-contract.json"
            ),
            ROOT
            / "rtl/encode-candidates/selected-history-qerr-transition/"
            "candidate_01.sv",
        ),
    ]


class EncodeHistoryAdapterTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        if not MODEL_SOURCE.is_dir():
            raise unittest.SkipTest(f"immutable model source is unavailable: {MODEL_SOURCE}")

    def _emit(self, contract, candidate, root):
        for name in ("dsc_types.h", "fifo.h"):
            shutil.copy2(MODEL_SOURCE / name, root / name)
        return write_history_encode_overlay_sources(
            _MetricsAgent,
            contract,
            root,
            contract["contract_id"],
            candidate,
        )

    def test_real_contracts_emit_complete_sources_and_child_result_routing(self):
        for contract, candidate in _real_contracts():
            with self.subTest(kind=contract["semantics"]["kind"]), tempfile.TemporaryDirectory() as directory:
                paths = self._emit(contract, candidate, pathlib.Path(directory))
                self.assertEqual(
                    set(paths), {"header", "abi", "overlay", "bridge", "main", "candidate", "composition"}
                )
                for key in ("header", "abi", "overlay", "bridge", "main"):
                    self.assertTrue(paths[key].is_file(), key)

                composition = paths["composition"]
                self.assertTrue(composition["child_result_ports_are_explicit_inputs"])
                self.assertTrue(composition["child_calls_are_semantic_and_routable"])
                self.assertTrue(composition["simultaneous_rewrite_routes_child_calls_to_rtl"])
                self.assertEqual(composition["history_entry_bound"], 32)
                self.assertEqual(composition["component_bound"], 4)
                if contract["semantics"]["kind"] == HISTORY_QERR_KIND:
                    self.assertEqual(composition["qerr_slot_bound"], 6)

                overlay = paths["overlay"].read_text(encoding="utf-8")
                self.assertIn("dsc_cicd_rtl", overlay)
                self.assertIn("illegal_domain", overlay)
                self.assertIn("dsc_cicd_note_call(mode)", overlay)
                self.assertIn("dsc_cicd_outputs_mismatch", overlay)
                self.assertIn("HistoryLookup(", overlay)
                self.assertNotIn("weighted_sad", overlay)
                self.assertNotIn("absdiff", overlay)
                self.assertNotIn("abs(", overlay)

                if contract["semantics"]["kind"] == HISTORY_REDUCTION_KIND:
                    self.assertIn("PickBestHistoryValue_original", overlay)
                    self.assertIn("search_failed", overlay)
                    self.assertIn("return mode == 2", overlay)
                    child_candidates = [
                        {"function": "PickBestHistoryValue", "slug": "parent"},
                        {"function": "HistoryLookup", "slug": "history_child"},
                    ]
                else:
                    self.assertIn("MapQpToQlevel(", overlay)
                    self.assertIn("IsOrigWithinQerr_original", overlay)
                    self.assertIn("dsc_cicd_saved_orig_within_qerr", overlay)
                    self.assertIn("dsc_cicd_saved_history_valid", overlay)
                    self.assertIn("dsc_cicd_restore_qerr_touched", overlay)
                    self.assertIn("dsc_cicd_commit_qerr_c", overlay)
                    self.assertIn("origWithinQerr", overlay)
                    self.assertIn("history.valid", overlay)
                    child_candidates = [
                        {"function": "IsOrigWithinQerr", "slug": "parent"},
                        {"function": "HistoryLookup", "slug": "history_child"},
                        {"function": "MapQpToQlevel", "slug": "map_child"},
                    ]
                routed, receipts = route_adapter_child_dispatchers(
                    overlay,
                    own_function=contract["function"]["name"],
                    candidates=child_candidates,
                )
                self.assertIn("dsc_cicd_history_child_invoke", routed)
                self.assertNotIn("extern void HistoryLookup(", routed)
                if contract["semantics"]["kind"] == HISTORY_QERR_KIND:
                    self.assertIn("dsc_cicd_map_child_invoke", routed)
                    self.assertNotIn("extern int MapQpToQlevel(", routed)
                self.assertTrue(receipts)

    def test_function_spelling_is_not_an_admission_check(self):
        contract, candidate = _real_contracts()[0]
        renamed = copy.deepcopy(contract)
        renamed["function"]["name"] = "RenamedHistoryReducer"
        renamed["function"]["qualified_name"] = "RenamedHistoryReducer"
        with tempfile.TemporaryDirectory() as directory:
            paths = self._emit(renamed, candidate, pathlib.Path(directory))
            text = paths["overlay"].read_text(encoding="utf-8")
            self.assertIn("RenamedHistoryReducer_original", text)
            self.assertIn("int RenamedHistoryReducer(", text)
            self.assertEqual(paths["composition"]["semantic_kind"], HISTORY_REDUCTION_KIND)

    def test_array_bounds_are_taken_from_the_frozen_contract(self):
        contract, candidate = _real_contracts()[1]
        bad = copy.deepcopy(contract)
        for port in bad["interface"]["ports"]:
            if port["name"] == "orig_within_qerr":
                port["array"] = [0, 4]
                break
        with tempfile.TemporaryDirectory() as directory:
            with self.assertRaisesRegex(RuntimeError, "extent"):
                self._emit(bad, candidate, pathlib.Path(directory))

    def test_generated_c_compiles_and_candidates_lint(self):
        clang = shutil.which("clang")
        verilator = shutil.which("verilator")
        for contract, candidate in _real_contracts():
            with self.subTest(kind=contract["semantics"]["kind"]), tempfile.TemporaryDirectory() as directory:
                root = pathlib.Path(directory)
                paths = self._emit(contract, candidate, root)
                if clang:
                    result = subprocess.run(
                        [
                            clang,
                            "-std=gnu99",
                            "-fsyntax-only",
                            "-I",
                            str(root),
                            str(paths["overlay"]),
                        ],
                        cwd=root,
                        text=True,
                        stdout=subprocess.PIPE,
                        stderr=subprocess.STDOUT,
                        check=False,
                    )
                    self.assertEqual(result.returncode, 0, result.stdout)
                if verilator:
                    result = subprocess.run(
                        [
                            verilator,
                            "--lint-only",
                            "--Wno-fatal",
                            "--top-module",
                            contract["contract_id"],
                            str(candidate),
                        ],
                        cwd=ROOT,
                        text=True,
                        stdout=subprocess.PIPE,
                        stderr=subprocess.STDOUT,
                        check=False,
                    )
                    self.assertEqual(result.returncode, 0, result.stdout)
                    verilator_include = pathlib.Path(verilator).resolve().parent.parent / "share/verilator/include"
                    if shutil.which("clang++") and (verilator_include / "verilated.h").is_file():
                        build = root / "verilated"
                        result = subprocess.run(
                            [
                                verilator,
                                "--cc",
                                "--Wno-fatal",
                                "--Mdir",
                                str(build),
                                "--top-module",
                                contract["contract_id"],
                                str(candidate),
                            ],
                            cwd=root,
                            text=True,
                            stdout=subprocess.PIPE,
                            stderr=subprocess.STDOUT,
                            check=False,
                        )
                        self.assertEqual(result.returncode, 0, result.stdout)
                        result = subprocess.run(
                            [
                                shutil.which("clang++"),
                                "-std=c++17",
                                "-fsyntax-only",
                                "-I",
                                str(build),
                                "-I",
                                str(root),
                                "-I",
                                str(verilator_include),
                                str(paths["bridge"]),
                            ],
                            cwd=root,
                            text=True,
                            stdout=subprocess.PIPE,
                            stderr=subprocess.STDOUT,
                            check=False,
                        )
                        self.assertEqual(result.returncode, 0, result.stdout)


if __name__ == "__main__":
    unittest.main()
