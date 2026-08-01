import json
import pathlib
import shutil
import subprocess
import sys
import tempfile
import unittest
from unittest import mock

from tools.cicd_agent import Agent


ROOT = pathlib.Path(__file__).resolve().parents[1]


class ExecutableCicdTests(unittest.TestCase):
    @staticmethod
    def selected_contract_state():
        state = json.loads((ROOT / "ci" / "state.json").read_text(encoding="utf-8"))
        return next(item for item in state["contracts"] if item.get("selected"))

    def test_missing_generator_is_required_without_model_call(self):
        with tempfile.TemporaryDirectory() as directory:
            root = pathlib.Path(directory)
            source = root / "source"
            source.mkdir()
            (source / "model.c").write_text("int f(int value) { return value; }\n", encoding="utf-8")
            agent = Agent(root, "run")
            agent.input_facts = {"source_dir": str(source), "tools": {}}
            contract = {
                "contract_id": "fixture_leaf",
                "status": "LOCKED",
                "function": {"name": "f", "source_file": "model.c", "source_span": {"start_line": 1, "end_line": 1}},
                "interface": {"ports": [{"name": "value", "direction": "input", "width": 8, "signed": False}]},
                "spec_links": [{"status": "EXACT", "anchor_id": "pdf:fixture"}],
            }
            with mock.patch.dict("os.environ", {}, clear=False):
                os_value = mock.patch.dict("os.environ", {"DSC_CICD_GENERATOR_CMD": ""}, clear=False)
                with os_value:
                    receipt = agent.generate_artifacts(contract, {"contract_id": "fixture_leaf"}, root / "artifact")
            self.assertEqual(receipt["status"], "GENERATION_REQUIRED")
            self.assertEqual(receipt["model_calls"], 0)

    def test_infrastructure_failure_never_invokes_generator(self):
        with tempfile.TemporaryDirectory() as directory:
            root = pathlib.Path(directory)
            marker = root / "generator-called"
            source = root / "source"
            source.mkdir()
            contract = {
                "contract_id": "fixture_leaf",
                "function": {"name": "f", "source_file": "model.c"},
                "interface": {"ports": []},
            }
            agent = Agent(root, "run")
            agent.input_facts = {"errors": ["PDF input changed"]}
            command = f"{sys.executable} -c 'open({str(marker)!r}, \"w\").write(\"called\")'"
            with mock.patch.dict("os.environ", {"DSC_CICD_GENERATOR_CMD": command}, clear=False):
                receipt = agent.generate_artifacts(contract, {}, root / "artifact")
            self.assertEqual(receipt["status"], "INFRASTRUCTURE_FAILURE")
            self.assertEqual(receipt["model_calls"], 0)
            self.assertFalse(marker.exists())

    def test_generator_hook_emits_multiple_candidates_from_locked_request(self):
        request = {
            "locked_contract": {"contract_id": "fixture_leaf"},
            "frozen_interface": {
                "ports": [
                    {"name": "value", "role": "value", "direction": "input", "width": 8, "signed": False},
                    {"name": "return_value", "role": "return_value", "direction": "output", "width": 8, "signed": False},
                ]
            },
            "c_body": "return value;",
            "exact_spec_anchors": [{"anchor_id": "pdf:section:fixture", "status": "EXACT"}],
        }
        with tempfile.TemporaryDirectory() as directory:
            root = pathlib.Path(directory)
            request_path = root / "request.json"
            output = root / "generated"
            request_path.write_text(json.dumps(request), encoding="utf-8")
            result = subprocess.run(
                [sys.executable, str(ROOT / "tools" / "generator_fixture.py"), str(request_path), str(output)],
                cwd=ROOT,
                text=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                check=False,
            )
            self.assertEqual(result.returncode, 0, result.stdout)
            self.assertEqual(sorted(path.name for path in output.glob("*.sv")), ["candidate_01.sv", "candidate_02.sv"])
            telemetry = json.loads((output / "telemetry.json").read_text(encoding="utf-8"))
            self.assertEqual(telemetry["model_calls"], 1)
            self.assertEqual(sorted(telemetry["request_keys"]), ["c_body", "exact_spec_anchors", "frozen_interface", "locked_contract"])

    def test_rtl_gate_rejects_sequential_constructs(self):
        agent = Agent(pathlib.Path(tempfile.mkdtemp()), "test")
        ports = [{"name": "value", "direction": "input", "width": 8, "signed": False}]
        reasons = agent.validate_rtl(
            "module bad(input logic [7:0] value); always_ff @(posedge clk) value <= value; endmodule",
            ports,
        )
        self.assertIn(r"\balways_ff\b", reasons)
        self.assertIn(r"\bposedge\b", reasons)
        latch_reasons = agent.validate_rtl(
            "module bad(input logic [7:0] value, output logic [7:0] out); always_latch out = value; endmodule",
            ports + [{"name": "out", "direction": "output", "width": 8, "signed": False}],
        )
        self.assertIn(r"\balways_latch\b", latch_reasons)
        memory_reasons = agent.validate_rtl(
            "module bad(input logic [7:0] value); logic [7:0] mem [0:3]; assign value = mem[0]; endmodule",
            ports,
        )
        self.assertTrue(any("logic" in reason for reason in memory_reasons))

    def test_fresh_receipts_prove_real_candidates_and_wrong_callee(self):
        selected = self.selected_contract_state()
        artifact = ROOT / selected["artifacts"][0]
        generation = json.loads((artifact / "generation.json").read_text(encoding="utf-8"))
        unit = json.loads((artifact / "unit-receipt.json").read_text(encoding="utf-8"))
        self.assertEqual(generation["status"], "PASS")
        self.assertEqual(generation["telemetry"]["model_calls"], 1)
        self.assertEqual(unit["execution_status"], "EXECUTED_NOW")
        self.assertEqual(unit["domain"]["total_vectors"], 2228207)
        statuses = {item["candidate"]: item["verification_status"] for item in unit["candidates"]}
        self.assertEqual(statuses["candidate_01"], "EXHAUSTIVE_EQUIVALENT")
        self.assertEqual(statuses["candidate_02"], "COUNTEREXAMPLE")
        self.assertEqual(unit["smallest_counterexample"]["inputs"], [-65535, 0])

        dependency = json.loads((artifact / "dependency-receipt.json").read_text(encoding="utf-8"))
        self.assertEqual(dependency["status"], "PASS")
        self.assertEqual(len(dependency["dependency_ports"]), 3)
        evidence = dependency["execution_evidence"]
        self.assertTrue(evidence["callee_oracle_compile"])
        self.assertTrue(evidence["callee_candidate_compile"])
        self.assertEqual(evidence["vectors"]["total_vectors"], 2228207)
        self.assertTrue(evidence["caller_core_with_callee_c"]["scenarios"])
        self.assertTrue(evidence["caller_core_plus_callee_rtl"]["scenarios"])
        overlay = json.loads((ROOT / "integration" / "generated-overlay" / selected["contract_id"] / "overlay-receipt.json").read_text(encoding="utf-8"))
        self.assertEqual(overlay["status"], "PASS")
        self.assertEqual(overlay["rewritten_calls"], 3)

        bitstream = json.loads((artifact / "bitstream-receipt.json").read_text(encoding="utf-8"))
        self.assertEqual(bitstream["status"], "PASS")
        self.assertTrue(all(bitstream["modes"][mode]["status"] == "PASS" for mode in ("C_ONLY", "SHADOW", "RTL_RETURN")))

    def test_cache_hit_is_zero_call_and_reuses_verified_receipt(self):
        selected = self.selected_contract_state()
        self.assertEqual(selected["status"], "CACHE_REUSED")
        summary = json.loads((ROOT / "summary.json").read_text(encoding="utf-8"))
        self.assertEqual(summary["generator_invocations"], 0)
        self.assertEqual(summary["model_calls"], 0)
        self.assertEqual(summary["results"][0]["execution_status"], "REUSED_VERIFIED_RECEIPT")
        cache = json.loads((ROOT / "ci" / "cache-index.json").read_text(encoding="utf-8"))
        self.assertTrue(any(item.get("contract_id") == selected["contract_id"] and item.get("valid") for item in cache["entries"].values()))

    def test_rejected_candidate_fails_unit_and_bitstream_gates(self):
        selected = self.selected_contract_state()
        artifact = ROOT / selected["artifacts"][0]
        unit = json.loads((artifact / "unit-receipt.json").read_text(encoding="utf-8"))
        rejected = next(item for item in unit["rejected_candidates"] if item["candidate"] == "candidate_02")
        self.assertEqual(rejected["status"], "EXPECTED_REJECTION")
        self.assertEqual(rejected["unit_gate"], "FAIL")
        self.assertEqual(rejected["bitstream_gate"], "FAIL")
        self.assertEqual(rejected["composition_gate"], "FAIL")
        self.assertTrue(rejected["expected_rejection"])
        receipt = json.loads((ROOT / rejected["receipt"]).read_text(encoding="utf-8"))
        self.assertEqual(receipt["bitstream_gate"]["matrix_status"], "FAIL")
        self.assertEqual(receipt["composition_gate"]["status"], "FAIL")
        self.assertTrue(receipt["composition_gate"]["call_sites"])
        self.assertEqual(receipt["matrix"]["modes"]["C_ONLY"]["status"], "PASS")
        self.assertEqual(receipt["matrix"]["modes"]["SHADOW"]["status"], "FAIL")
        self.assertEqual(receipt["matrix"]["modes"]["RTL_RETURN"]["status"], "FAIL")

    def _rewriter_binary(self):
        binary = ROOT / "tmp" / "cicd-clang-rewriter" / "dsc-clang-rewrite"
        if not binary.is_file():
            agent = Agent(ROOT, "test")
            agent.input_facts = agent.discover_inputs()
            binary, build = agent.ensure_rewriter()
            self.assertIsNotNone(binary, build)
        return binary

    def _run_rewriter_fixture(self, root, caller_source):
        clang = shutil.which("clang")
        self.assertIsNotNone(clang)
        header = root / "selected_leaf.h"
        callee = root / "callee.c"
        caller = root / "caller.c"
        header.write_text("int selected_leaf(int value);\n", encoding="utf-8")
        callee.write_text(
            '#include "selected_leaf.h"\n'
            "int selected_leaf(int value) { return value + 1; }\n",
            encoding="utf-8",
        )
        caller.write_text(caller_source, encoding="utf-8")
        compdb = root / "compile_commands.json"
        compdb.write_text(json.dumps([
            {
                "directory": str(root),
                "file": str(path),
                "arguments": [str(clang), "-std=gnu99", "-I", str(root), "-c", str(path)],
            }
            for path in (callee, caller)
        ]), encoding="utf-8")
        receipt = root / "receipt.json"
        command = [
            str(self._rewriter_binary()),
            "--compdb", str(compdb),
            "--target-usr", "c:@F@selected_leaf",
            "--original-name", "selected_leaf_original",
            "--dispatcher-name", "dsc_cicd_invoke",
            "--receipt", str(receipt),
            str(callee), str(caller),
        ]
        result = subprocess.run(command, cwd=root, text=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, check=False)
        return result, receipt, callee, caller

    def test_clang_rewriter_handles_cross_file_multiple_calls(self):
        with tempfile.TemporaryDirectory() as directory:
            result, receipt_path, callee, caller = self._run_rewriter_fixture(
                pathlib.Path(directory),
                '#include "selected_leaf.h"\n'
                "int call_many(int value) { return selected_leaf(value) + selected_leaf(value + 1); }\n",
            )
            receipt = json.loads(receipt_path.read_text(encoding="utf-8"))
            self.assertEqual(result.returncode, 0, result.stdout)
            self.assertEqual(receipt["status"], "PASS")
            self.assertEqual(receipt["definitions_seen"], 1)
            self.assertEqual(receipt["direct_calls_seen"], 2)
            self.assertEqual(receipt["rewritten_calls"], 2)
            self.assertEqual(receipt["changed_files"], [str(callee), str(caller)])
            self.assertIn("selected_leaf_original", callee.read_text(encoding="utf-8"))
            rewritten = caller.read_text(encoding="utf-8")
            self.assertEqual(rewritten.count("dsc_cicd_invoke"), 2)

    def test_clang_rewriter_fails_closed_for_macro_and_indirect_calls(self):
        with tempfile.TemporaryDirectory() as directory:
            result, receipt_path, _, _ = self._run_rewriter_fixture(
                pathlib.Path(directory),
                '#include "selected_leaf.h"\n'
                "#define CALL_SELECTED(value) selected_leaf(value)\n"
                "int (*selected_leaf_pointer)(int) = selected_leaf;\n"
                "int call_bad(int value) { return CALL_SELECTED(value) + selected_leaf_pointer(value); }\n",
            )
            receipt = json.loads(receipt_path.read_text(encoding="utf-8"))
            self.assertNotEqual(result.returncode, 0)
            self.assertEqual(receipt["status"], "FAIL")
            self.assertTrue(receipt["macro_locations"])
            self.assertTrue(receipt["indirect_locations"])


if __name__ == "__main__":
    unittest.main()
