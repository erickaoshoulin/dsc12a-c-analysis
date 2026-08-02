import json
import os
import pathlib
import re
import tempfile
import unittest
from concurrent.futures import ThreadPoolExecutor
from unittest import mock

from tools.regression import (
    DurableStore,
    LocalContext,
    ModelRouter,
    RegressionService,
    append_jsonl,
    compact_frames,
    read_json,
    summarize_candidates,
)


ROOT = pathlib.Path(__file__).resolve().parents[1]


class RegressionServiceTests(unittest.TestCase):
    def test_concurrent_jsonl_appends_preserve_every_record(self):
        with tempfile.TemporaryDirectory() as directory:
            path = pathlib.Path(directory) / "strategy.jsonl"
            records = [{"event": "worker", "sequence": index} for index in range(32)]
            with ThreadPoolExecutor(max_workers=8) as executor:
                list(executor.map(lambda record: append_jsonl(path, record), records))
            actual = [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines()]
            self.assertEqual({item["sequence"] for item in actual}, set(range(32)))

    def test_queue_claim_finish_and_stale_recovery_are_durable(self):
        with tempfile.TemporaryDirectory() as directory:
            root = pathlib.Path(directory)
            store = DurableStore(root, validate=False)
            store.ensure_layout()
            run_dir = store.run_dir("run-a")
            (run_dir / "functions").mkdir(parents=True)
            (run_dir / "run.json").write_text(json.dumps({"run_id": "run-a"}), encoding="utf-8")

            store.enqueue({"job_id": "job-a", "run_id": "run-a", "contract_id": "contract-a", "function": "discovered_a"})
            running = store.claim_one()
            self.assertIsNotNone(running)
            assert running is not None
            heartbeat = read_json(running / "heartbeat.json", {})
            self.assertIn("host", heartbeat)
            self.assertIn("pid", heartbeat)
            self.assertIn("stage", heartbeat)
            self.assertIn("progress", heartbeat)
            self.assertIn("elapsed_seconds", heartbeat)
            self.assertIn("last_error", heartbeat)
            done = store.finish(running, "done", stage="complete")
            self.assertTrue(done.is_dir())

            store.enqueue({"job_id": "job-b", "run_id": "run-a", "contract_id": "contract-b", "function": "discovered_b"})
            stale = store.claim_one()
            assert stale is not None
            old = read_json(stale / "heartbeat.json", {})
            old["updated_at"] = "1970-01-01T00:00:00Z"
            from tools import regression

            regression.atomic_write_json(stale / "heartbeat.json", old)
            recovered = store.recover_stale(stale_seconds=1)
            self.assertEqual([item["job_id"] for item in recovered], ["job-b"])
            pending = store.job_dir("pending", "job-b")
            self.assertTrue(pending.is_dir())
            self.assertEqual(read_json(pending / "job.json", {})["attempt"], 1)
            strategy = (run_dir / "strategy.jsonl").read_text(encoding="utf-8").splitlines()
            self.assertTrue(any(json.loads(line).get("event") == "stale_recovery" for line in strategy))

    def test_run_status_is_reconciled_from_receipts(self):
        with tempfile.TemporaryDirectory() as directory:
            root = pathlib.Path(directory)
            store = DurableStore(root, validate=False)
            store.ensure_layout()
            run_dir = store.run_dir("run-a")
            function_dir = run_dir / "functions" / "contract-a"
            function_dir.mkdir(parents=True)
            (run_dir / "run.json").write_text(
                json.dumps({"run_id": "run-a", "status": "QUEUED"}),
                encoding="utf-8",
            )
            (function_dir / "receipt.json").write_text(
                json.dumps({"run_id": "run-a", "contract_id": "contract-a", "status": "PASS"}),
                encoding="utf-8",
            )

            service = RegressionService(store, ROOT)
            refreshed = service.refresh_run_status("run-a")

            self.assertEqual(refreshed["status"], "COMPLETED")
            self.assertIn("completed_at", refreshed)
            self.assertEqual(read_json(run_dir / "run.json", {})["status"], "COMPLETED")

    def test_source_gate_and_function_selection_use_current_facts(self):
        context = LocalContext(ROOT)
        gate = context.source_gate()
        self.assertEqual(gate["status"], "PASS")
        self.assertEqual(gate["pdf"]["pages"], 145)
        self.assertEqual(gate["compile_check"]["translation_units"], 11)
        self.assertEqual(gate["build"]["status"], "PASS")
        pilot = context.pilot_functions(ModelRouter(ROOT / "model-policy.yaml"))
        plan_ids = {str(item.get("contract_id")) for item in context.plan.get("contracts", [])}
        self.assertTrue(pilot)
        self.assertTrue({item["contract_id"] for item in pilot} <= plan_ids)
        self.assertTrue(any(item["kind"] == "arithmetic" for item in pilot))
        scale = context.scale_plan(ModelRouter(ROOT / "model-policy.yaml"))
        verified_ids = {
            str(item.get("contract_id"))
            for item in json.loads((ROOT / "library" / "manifest.json").read_text(encoding="utf-8")).get("components", [])
            if item.get("status") == "PASS" and item.get("contract_id")
        }
        scale_ids = {str(item.get("contract_id")) for item in scale.get("functions", [])}
        self.assertTrue(verified_ids <= scale_ids)
        service_source = (ROOT / "tools" / "regression.py").read_text(encoding="utf-8").lower()
        for item in context.plan.get("contracts", []):
            self.assertNotIn(str(item.get("contract_id", "")).lower(), service_source)

    def test_c_type_fallback_and_ai_proposed_authority_block_generation(self):
        context = LocalContext(ROOT)
        blocked_ids = [item.get("contract_id") for item in context.plan.get("contracts", []) if not item.get("ready")]
        if blocked_ids:
            self.assertEqual(context.width_spec_gate(str(blocked_ids[0]))["status"], "BLOCKED")
        else:
            self.assertEqual(context.width_spec_gate("mapqptoqlevel")["status"], "PASS")
        with tempfile.TemporaryDirectory() as directory:
            contract = {
                "contract_id": "synthetic",
                "function": {"name": "synthetic"},
                "interface": {"ports": [{"name": "value", "width": 8, "signed": False, "legal_domain": {"kind": "unresolved"}}]},
                "spec_links": [{"status": "EXACT", "page": 1}],
            }
            fake = pathlib.Path(directory)
            (fake / "spec").mkdir()
            (fake / "spec" / "manifest.json").write_text(json.dumps({}), encoding="utf-8")
            (fake / "contracts" / "locked").mkdir(parents=True)
            (fake / "contracts" / "locked" / "synthetic.json").write_text(json.dumps(contract), encoding="utf-8")
            (fake / "ci").mkdir()
            for name, value in (("plan.json", {"contracts": []}), ("state.json", {}), ("cache-index.json", {})):
                (fake / "ci" / name).write_text(json.dumps(value), encoding="utf-8")
            self.assertEqual(LocalContext(fake).width_spec_gate("synthetic")["status"], "BLOCKED")

    def test_candidate_summary_requires_compile_evidence_and_keeps_bad_rtl(self):
        generation = {"candidates": [{"candidate": "candidate_01"}, {"candidate": "candidate_02"}]}
        unit = {
            "promoted_candidate": "candidate_01",
            "compile_once": [{"candidate": "candidate_01", "binary": "rtl-01"}, {"candidate": "candidate_02", "binary": "rtl-02"}],
            "candidates": [
                {"candidate": "candidate_01", "verification_status": "EXHAUSTIVE_EQUIVALENT", "vectors_executed": 10},
                {"candidate": "candidate_02", "verification_status": "COUNTEREXAMPLE", "smallest_counterexample": {"x": 0}},
            ],
        }
        summary = summarize_candidates(generation, unit, 2)
        self.assertEqual([item["compile_status"] for item in summary], ["PASS", "PASS"])
        self.assertEqual(summary[1]["verification_status"], "COUNTEREXAMPLE")
        self.assertEqual(summary[1]["smallest_counterexample"], {"x": 0})

    def test_old_and_current_frame_receipt_shapes_are_normalized(self):
        context = LocalContext(ROOT)
        selected = context.frame_matrix()
        old = {
            "modes": [
                {"mode": "C_ONLY", "status": "PASS", "sha256": "x", "expected_sha256": "x", "byte_for_byte_equal": True},
                {"mode": "SHADOW", "status": "PASS", "sha256": "x", "expected_sha256": "x", "byte_for_byte_equal": True},
            ]
        }
        compact = compact_frames(old, selected)
        self.assertEqual(compact[0]["modes"][0]["status"], "PASS")
        self.assertEqual(compact[1]["modes"][0]["status"], "MISSING")

    def test_model_routing_is_env_only_and_dashboard_has_no_external_assets(self):
        with mock.patch.dict(os.environ, {"DSC_REGRESSION_CHEAP_MODEL": "cheap-test", "DSC_REGRESSION_STRONG_MODEL": "strong-test"}, clear=False):
            router = ModelRouter(ROOT / "model-policy.yaml")
            cheap = router.route("arithmetic")
            strong = router.route("table_config")
            self.assertEqual(cheap["model"], "cheap-test")
            self.assertEqual(strong["model"], "strong-test")
            self.assertEqual(router.route("arithmetic", cached=True)["initial_calls_allowed"], 0)
        with tempfile.TemporaryDirectory() as directory:
            store = DurableStore(pathlib.Path(directory), validate=False)
            service = RegressionService(store, ROOT)
            service.init()
            html = (store.dashboard / "index.html").read_text(encoding="utf-8")
            self.assertNotRegex(html, r"<link[^>]+href=\"https?://|<script[^>]+src=\"https?://")
            first = read_json(store.dashboard / "latest.json", {})
            second = service.refresh_dashboard()
            self.assertEqual(first["counts"], second["counts"])

    def test_library_promotion_requires_pass_and_preserves_traceability(self):
        with tempfile.TemporaryDirectory() as directory:
            root = pathlib.Path(directory)
            store = DurableStore(root / "state", validate=False)
            service = RegressionService(store, root)
            rtl = root / "accepted.sv"
            rtl.write_text(
                "module synthetic_candidate_01(input logic [7:0] value, output logic [7:0] return_value);\n"
                "assign return_value = value + 8'd1;\nendmodule\n",
                encoding="utf-8",
            )
            run = store.run_dir("run-a")
            function = run / "functions" / "synthetic"
            function.mkdir(parents=True)
            (run / "run.json").write_text(json.dumps({"run_id": "run-a", "profile": "scale"}), encoding="utf-8")
            receipt = {
                "status": "PASS",
                "run_id": "run-a",
                "contract_id": "synthetic",
                "function": "Synthetic",
                "kind": "arithmetic",
                "execution_status": "EXECUTED_NOW",
                "accepted_rtl": str(rtl),
                "contract_hash": "contract-hash",
                "candidate_pass_rate": "1/2",
                "frame_pass_rate": "3/3",
                "source_gate": {"status": "PASS"},
                "traceability": {
                    "authority": "EXACT_SPEC",
                    "review_status": "REVIEWED",
                    "source_file": "model.c",
                    "c_span": {"start_line": 1, "end_line": 1},
                    "spec_links": [{"status": "EXACT", "page": 1, "section": "1"}],
                    "ports": [{"name": "value", "authority": "EXACT_SPEC"}, {"name": "return_value", "authority": "EXACT_SPEC"}],
                },
                "stages": {stage: {"status": "PASS"} for stage in ("width_spec_gate", "generator_cache", "verilator_lint_build", "shards_mutations", "dependency_composition", "model_matrix", "frame_compare")},
            }
            (function / "receipt.json").write_text(json.dumps(receipt), encoding="utf-8")
            result = service.promote_library("run-a")
            self.assertEqual(result["status"], "PASS")
            manifest = read_json(root / "library" / "manifest.json", {})
            self.assertEqual(manifest["components"][0]["contract_id"], "synthetic")
            self.assertEqual(manifest["components"][0]["module"], "synthetic")
            self.assertTrue((root / "library" / "rtl" / "synthetic.sv").is_file())
            self.assertIn("module synthetic(", (root / "library" / "rtl" / "synthetic.sv").read_text(encoding="utf-8"))
            self.assertTrue((root / "library" / "verification" / "synthetic.json").is_file())


if __name__ == "__main__":
    unittest.main()
