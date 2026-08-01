import json
import pathlib
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
        reasons = agent.validate_rtl("module bad(input logic [7:0] value); always_ff @(posedge clk) value <= value; endmodule", ports)
        self.assertIn(r"\balways_ff\b", reasons)
        self.assertIn(r"\bposedge\b", reasons)

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


if __name__ == "__main__":
    unittest.main()
