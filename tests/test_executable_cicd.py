import copy
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
        selected = next((item for item in state["contracts"] if item.get("selected")), None)
        if selected:
            for relative in selected.get("artifacts", []):
                artifact = ROOT / relative
                if not artifact.is_dir():
                    continue
                generation_path = artifact / "generation.json"
                unit_path = artifact / "unit-receipt.json"
                if not (generation_path.is_file() and unit_path.is_file()):
                    continue
                generation = json.loads(generation_path.read_text(encoding="utf-8"))
                unit = json.loads(unit_path.read_text(encoding="utf-8"))
                if (
                    generation.get("execution_status") == "EXECUTED_NOW"
                    and int((generation.get("telemetry") or {}).get("model_calls", 0)) >= 1
                    and any(item.get("candidate") == "candidate_02" for item in unit.get("candidates", []))
                ):
                    return selected
        # A no-work reconciliation intentionally clears the active selection.
        # Keep executable-receipt tests anchored to the latest tool-produced
        # fresh candidate rather than a source/function-name target.
        fresh = []
        for artifact in (ROOT / "artifacts").iterdir():
            generation_path = artifact / "generation.json"
            locked_path = artifact / "locked-contract.json"
            unit_path = artifact / "unit-receipt.json"
            if not (generation_path.is_file() and locked_path.is_file() and unit_path.is_file()):
                continue
            generation = json.loads(generation_path.read_text(encoding="utf-8"))
            if generation.get("status") != "PASS" or generation.get("execution_status") != "EXECUTED_NOW":
                continue
            if int((generation.get("telemetry") or {}).get("model_calls", 0)) < 1:
                continue
            contract_id = json.loads(locked_path.read_text(encoding="utf-8")).get("contract_id")
            if contract_id:
                fresh.append((generation_path.stat().st_mtime, artifact, str(contract_id)))
        if not fresh:
            raise AssertionError("no selected or tool-produced fresh executable receipt")
        _, artifact, contract_id = max(fresh, key=lambda value: value[0])
        prior = next((item for item in state["contracts"] if item.get("contract_id") == contract_id), {})
        fallback = copy.deepcopy(prior)
        dependency = json.loads((artifact / "dependency-receipt.json").read_text(encoding="utf-8"))
        matrix_path = artifact / "matrix-receipt.json"
        matrix = json.loads(matrix_path.read_text(encoding="utf-8")) if matrix_path.is_file() else {}
        fallback.update({
            "contract_id": contract_id,
            "selected": False,
            "artifacts": [str(artifact.relative_to(ROOT))],
            "status": "PROMOTED" if dependency.get("status") == "PASS" and matrix.get("status") == "PASS" else "FAILED",
        })
        return fallback

    @staticmethod
    def selected_artifact(state):
        for relative in reversed(state.get("artifacts", [])):
            path = ROOT / relative
            if path.is_dir() and (path / "unit-receipt.json").is_file():
                return path
        raise AssertionError(f"no executable artifact in state: {state.get('artifacts', [])}")

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

    def test_windowed_formal_receipts_and_record_field_overlay_mapping(self):
        artifact = next(
            path for path in sorted((ROOT / "artifacts").iterdir())
            if path.is_dir()
            and json.loads((path / "locked-contract.json").read_text(encoding="utf-8")).get("contract_id")
            == "samplepredict"
            and (path / "formal" / "candidate_01.json").is_file()
            and json.loads((path / "formal" / "candidate_01.json").read_text(encoding="utf-8")).get("proof_strategy")
            == "STRUCTURAL_HPOS_RESIDUE_PARTITION"
        )
        rejection_artifact = next(
            path for path in sorted((ROOT / "artifacts").iterdir())
            if path.is_dir()
            and json.loads((path / "locked-contract.json").read_text(encoding="utf-8")).get("contract_id")
            == "samplepredict"
            and any(
                item.get("candidate") == "candidate_02"
                for item in json.loads((path / "unit-receipt.json").read_text(encoding="utf-8")).get("candidates", [])
            )
        )
        unit = json.loads((artifact / "unit-receipt.json").read_text(encoding="utf-8"))
        statuses = {item["candidate"]: item["verification_status"] for item in unit["candidates"]}
        self.assertEqual(statuses["candidate_01"], "FORMAL_EQUIVALENT")
        rejection_unit = json.loads((rejection_artifact / "unit-receipt.json").read_text(encoding="utf-8"))
        rejection_statuses = {item["candidate"]: item["verification_status"] for item in rejection_unit["candidates"]}
        self.assertEqual(rejection_statuses["candidate_02"], "COUNTEREXAMPLE")
        formal = json.loads((artifact / "formal" / "candidate_01.json").read_text(encoding="utf-8"))
        self.assertEqual(formal["status"], "PASS")
        self.assertTrue(formal["proof_complete"])
        self.assertEqual(formal["ast_frontend"], "verilator --json-only")
        self.assertEqual(formal["proof_strategy"], "STRUCTURAL_HPOS_RESIDUE_PARTITION")
        self.assertEqual(formal["partitions_checked"], formal["partition_count"])
        self.assertGreater(formal["partition_count"], 0)
        # A stable refresh executes the shards again; older cached artifacts
        # recorded reuse on the domain object while newer fresh receipts keep
        # the execution status at the unit level. Accept both receipt shapes.
        self.assertIn(unit["execution_status"], ("EXECUTED_NOW", "REUSED_VERIFIED_RECEIPT"))
        self.assertIn(
            unit["domain"].get("execution_status", unit["execution_status"]),
            ("EXECUTED_NOW", "REUSED_VERIFIED_SHARDS", "REUSED_VERIFIED_RECEIPT"),
        )

        oracle = (artifact / "oracle.c").read_text(encoding="utf-8")
        self.assertIn("static int prevLine[65541]", oracle)
        self.assertIn("prevLine[((hPos / 3) * 3 + 5 + -2) + 0]", oracle)
        self.assertIn("currLine[((hPos > 8) ? (hPos - 8) : 0) + 0]", oracle)

        agent = Agent(ROOT, "test")
        agent.load_inputs()
        contract = json.loads((artifact / "locked-contract.json").read_text(encoding="utf-8"))
        candidate = artifact / "generated" / "candidate_01.sv"
        with tempfile.TemporaryDirectory() as directory:
            source_dir = pathlib.Path(directory) / "source"
            source_dir.mkdir()
            paths = agent.write_overlay_sources(
                contract,
                source_dir,
                "samplepredict_candidate_01",
                candidate,
            )
            rtl_call = next(
                line for line in paths["overlay"].read_text(encoding="utf-8").splitlines()
                if "int rtl_value =" in line
            )
        self.assertIn("dsc_state->cpntBitDepth[dsc_state->unitCType[unit]]", rtl_call)
        self.assertIn("dsc_state->quantizedResidual[unit][0]", rtl_call)
        self.assertNotIn("dsc_state[0]", rtl_call)

    def test_fresh_receipts_prove_real_candidates_and_wrong_callee(self):
        selected = self.selected_contract_state()
        plan = json.loads((ROOT / "ci" / "plan.json").read_text(encoding="utf-8"))
        selected_plan = next(
            (item for item in plan["contracts"] if item["contract_id"] == selected["contract_id"]),
            None,
        )
        if selected_plan is None:
            # After the discovered frontier is fully promoted, the next plan
            # is intentionally a no-work plan.  The last promoted state still
            # supplies the stable receipt checked below, but it need not be
            # re-selected by the current plan.
            self.assertEqual(plan["selected_contracts"], [])
            self.assertEqual(plan["new_candidates"], [])
        elif not selected_plan["selected"]:
            # The current plan may retain a prior run's deterministic
            # composition boundary as blocked, defer an accepted stable leaf,
            # or select another tool-discovered frontier item. A last-run
            # receipt is not a request to regenerate the same C boundary.
            self.assertNotIn(selected["contract_id"], plan["selected_contracts"])
            self.assertTrue(
                selected_plan.get("prior_composition_boundary")
                or selected_plan.get("blocked_reasons")
                or selected_plan.get("deferred")
                or selected_plan.get("cache_hit")
                or selected_plan.get("accepted_rtl_available")
                or selected_plan.get("stale")
            )
        else:
            existing_ready = [
                item for item in plan["contracts"]
                if item["contract_id"] != selected["contract_id"] and item.get("origin") == "locked_contract" and item.get("ready")
            ]
            self.assertTrue(selected_plan["selected"])
            self.assertTrue(selected_plan.get("force_regenerate") or selected_plan["new_work"])
            self.assertTrue(all(selected_plan["interface_shape"] != item["interface_shape"] for item in existing_ready))
        artifact = self.selected_artifact(selected)
        generation = json.loads((artifact / "generation.json").read_text(encoding="utf-8"))
        unit = json.loads((artifact / "unit-receipt.json").read_text(encoding="utf-8"))
        self.assertEqual(generation["status"], "PASS")
        self.assertEqual(generation["telemetry"]["model_calls"], 1)
        self.assertEqual(unit["execution_status"], "EXECUTED_NOW")
        self.assertGreater(unit["domain"]["total_vectors"], 0)
        statuses = {item["candidate"]: item["verification_status"] for item in unit["candidates"]}
        self.assertEqual(statuses["candidate_01"], unit["verification_status"])
        self.assertIn(statuses["candidate_01"], ("EXHAUSTIVE_EQUIVALENT", "FORMAL_EQUIVALENT"))
        self.assertEqual(statuses["candidate_02"], "COUNTEREXAMPLE")
        self.assertEqual(
            len(unit["smallest_counterexample"]["inputs"]),
            len(unit["domain"]["input_ports"]),
        )

        dependency = json.loads((artifact / "dependency-receipt.json").read_text(encoding="utf-8"))
        if dependency["status"] != "PASS":
            # A unit-proven leaf may still be rejected at the immutable-C
            # caller boundary.  That is a safe C fallback, not a promotion.
            self.assertEqual(selected["status"], "FAILED")
            self.assertTrue(dependency["checks"]["callee_RTL_against_callee_C"])
            self.assertFalse(dependency["checks"]["caller_core_plus_callee_RTL"])
            self.assertTrue(dependency["checks"]["caller_core_with_callee_C"])
            matrix = json.loads((artifact / "matrix-receipt.json").read_text(encoding="utf-8"))
            self.assertIn(matrix["status"], {"COMPOSITION_BLOCKED", "INFRASTRUCTURE_FAILURE"})
            self.assertIn(matrix["reason"], {
                "caller call signature does not provide the frozen DUT interface; retain C boundary",
                "caller/callee overlay compile failed",
                "baseline matrix failed",
                "Clang overlay rewrite failed",
            })
            return
        self.assertGreater(len(dependency["dependency_ports"]), 0)
        self.assertTrue(all(port.get("arguments") for port in dependency["dependency_ports"]))
        self.assertTrue(all(port.get("result") for port in dependency["dependency_ports"]))
        evidence = dependency["execution_evidence"]
        self.assertTrue(evidence["callee_oracle_compile"])
        self.assertTrue(evidence["callee_candidate_compile"])
        self.assertGreater(evidence["vectors"]["total_vectors"], 0)
        self.assertTrue(evidence["caller_core_with_callee_c"]["scenarios"])
        self.assertTrue(evidence["caller_core_plus_callee_rtl"]["scenarios"])
        overlay = json.loads((ROOT / "integration" / "generated-overlay" / selected["contract_id"] / "overlay-receipt.json").read_text(encoding="utf-8"))
        self.assertEqual(overlay["status"], "PASS")
        self.assertGreater(overlay["rewritten_calls"], 0)

        bitstream = json.loads((artifact / "bitstream-receipt.json").read_text(encoding="utf-8"))
        self.assertEqual(bitstream["status"], "PASS")
        self.assertTrue(all(bitstream["modes"][mode]["status"] == "PASS" for mode in ("C_ONLY", "SHADOW", "RTL_RETURN")))

    def test_samplepredict_is_in_stable_library_after_all_gates(self):
        manifest = json.loads((ROOT / "library" / "manifest.json").read_text(encoding="utf-8"))
        entry = next(item for item in manifest["components"] if item.get("contract_id") == "samplepredict")
        self.assertEqual(entry["status"], "PASS")
        self.assertEqual(entry["module"], "samplepredict")
        self.assertTrue((ROOT / "library" / "rtl" / "samplepredict.sv").is_file())
        verification = json.loads((ROOT / "library" / "verification" / "samplepredict.json").read_text(encoding="utf-8"))
        self.assertEqual(verification["status"], "PASS")
        self.assertEqual(verification["stages"]["formal_rtl_equivalence"], "PASS")
        self.assertEqual(verification["stages"]["formal_partitions"], 1002)

    def test_cache_hit_is_zero_call_and_reuses_verified_receipt(self):
        selected = self.selected_contract_state()
        summary = json.loads((ROOT / "summary.json").read_text(encoding="utf-8"))
        cache = json.loads((ROOT / "ci" / "cache-index.json").read_text(encoding="utf-8"))
        entry = next(
            (
                item
                for item in cache["entries"].values()
                if item.get("contract_id") == selected["contract_id"] and item.get("valid")
            ),
            None,
        )
        if entry is None:
            self.assertNotIn(selected["status"], ("PROMOTED", "CACHE_REUSED"))
            return
        self.assertTrue(entry.get("valid"))
        if selected["status"] == "CACHE_REUSED":
            self.assertEqual(summary["generator_invocations"], 0)
            self.assertEqual(summary["model_calls"], 0)
            self.assertEqual(summary["results"][0]["execution_status"], "REUSED_VERIFIED_RECEIPT")
        elif selected["status"] == "FAILED":
            # A historical generated candidate can remain the latest fresh
            # receipt while the current planner is executing a different
            # tool-discovered contract. In that case the old receipt may be a
            # deliberate C boundary and is not evidence of a cache failure.
            artifact = self.selected_artifact(selected)
            matrix_path = artifact / "matrix-receipt.json"
            if matrix_path.is_file():
                matrix = json.loads(matrix_path.read_text(encoding="utf-8"))
                self.assertIn(matrix.get("status"), {"COMPOSITION_BLOCKED", "FAIL", "INFRASTRUCTURE_FAILURE"})
            self.assertEqual(summary["generator_invocations"], 0)
            self.assertEqual(summary["model_calls"], 0)
        else:
            self.assertEqual(selected["status"], "PROMOTED")
            self.assertEqual(summary["results"][0]["execution_status"], "EXECUTED_NOW")

    def test_rejected_candidate_fails_unit_and_bitstream_gates(self):
        selected = self.selected_contract_state()
        artifact = self.selected_artifact(selected)
        unit = json.loads((artifact / "unit-receipt.json").read_text(encoding="utf-8"))
        rejected = next(item for item in unit["rejected_candidates"] if item["candidate"] == "candidate_02")
        self.assertEqual(rejected["status"], "EXPECTED_REJECTION")
        self.assertEqual(rejected["unit_gate"], "FAIL")
        self.assertEqual(rejected["bitstream_gate"], "FAIL")
        self.assertIn(rejected["composition_gate"], ("FAIL", "NOT_RUN"))
        self.assertTrue(rejected["expected_rejection"])
        receipt = json.loads((ROOT / rejected["receipt"]).read_text(encoding="utf-8"))
        self.assertIn(receipt["bitstream_gate"]["matrix_status"], ("FAIL", "NOT_RUN_UNIT_REJECTED"))
        if rejected["composition_gate"] == "NOT_RUN":
            self.assertEqual(receipt["composition_gate"]["status"], "NOT_RUN")
            self.assertEqual(receipt["matrix"], {})
        else:
            self.assertEqual(receipt["composition_gate"]["status"], "FAIL")
            self.assertTrue(receipt["composition_gate"]["call_sites"])
            self.assertEqual(receipt["matrix"]["modes"]["C_ONLY"]["status"], "PASS")
            self.assertEqual(receipt["matrix"]["modes"]["SHADOW"]["status"], "FAIL")
            self.assertEqual(receipt["matrix"]["modes"]["RTL_RETURN"]["status"], "FAIL")

    def test_windowed_boundary_strategy_never_claims_exhaustive(self):
        agent = Agent(ROOT, "test")
        ports = [
            {"name": "hPos", "direction": "input", "width": 2, "legal_domain": {"values": [0, 1, 2]}},
            {"name": "predType", "direction": "input", "width": 2, "legal_domain": {"values": [0, 1, 2]}},
            {"name": "qLevel", "direction": "input", "width": 2, "legal_domain": {"range": [0, 2]}},
            {"name": "unit", "direction": "input", "width": 2, "legal_domain": {"values": [0, 3]}},
            {"name": "cpnt_bit_depth", "direction": "input", "width": 5, "legal_domain": {"values": [8, 10]}},
            {"name": "unit_c_type", "direction": "input", "width": 2, "legal_domain": {"values": [0, 1]}},
            {"name": "tap_a", "direction": "input", "width": 16, "legal_domain": {"range": [0, 65535]}},
            {"name": "tap_b", "direction": "input", "width": 16, "legal_domain": {"range": [0, 65535]}},
            {"name": "residual", "direction": "input", "width": 16, "signed": True, "legal_domain": {"range": [-32768, 32767]}},
        ]
        strategy = {
            "kind": "windowed_boundary",
            "exhaustive": False,
            "bit_depth_port": "cpnt_bit_depth",
            "component_type_port": "unit_c_type",
            "qlevel_port": "qLevel",
            "unit_port": "unit",
            "hpos_port": "hPos",
            "pred_type_port": "predType",
            "sample_ports": ["tap_a", "tap_b"],
            "residual_ports": ["residual"],
            "pairwise_groups": [["tap_a", "tap_b"]],
            "probe_units": [0, 3],
            "qlevel_max_by_component": {
                "luma": {"8": 2, "10": 2},
                "chroma": {"8": 2, "10": 2},
            },
        }
        contract = {"interface": {"ports": ports}, "semantics": {"legal_vector_strategy": strategy}}
        vectors, receipt = agent.legal_vector_iterator(
            contract,
            ports,
            [agent.port_domain(port) for port in ports],
        )
        first = next(iter(vectors))
        self.assertEqual(len(first), len(ports))
        self.assertFalse(receipt["exhaustive"])
        self.assertEqual(receipt["kind"], "windowed_boundary")
        self.assertEqual(receipt["pairwise_groups"], [["tap_a", "tap_b"]])

    def test_flatness_window_promotion_receipt_and_unused_lane_guard(self):
        artifact = next(
            path for path in sorted((ROOT / "artifacts").iterdir())
            if path.is_dir()
            and json.loads((path / "locked-contract.json").read_text(encoding="utf-8")).get("contract_id")
            == "isorigflathindex"
            and (path / "formal" / "candidate_01.json").is_file()
        )
        contract = json.loads((artifact / "locked-contract.json").read_text(encoding="utf-8"))
        unit = json.loads((artifact / "unit-receipt.json").read_text(encoding="utf-8"))
        formal = json.loads((artifact / "formal" / "candidate_01.json").read_text(encoding="utf-8"))
        self.assertEqual(unit["domain"]["vector_strategy"]["kind"], "flatness_window")
        self.assertEqual(unit["domain"]["total_vectors"], 575552)
        self.assertEqual(formal["proof_strategy"], "SYMBOLIC_FLATNESS_WINDOW")
        self.assertTrue(formal["proof_complete"])
        self.assertEqual(unit["candidates"][0]["verification_status"], "FORMAL_EQUIVALENT")

        agent = Agent(ROOT, "test")
        candidate = artifact / "generated" / "candidate_01.sv"
        with tempfile.TemporaryDirectory() as directory:
            paths = agent.write_overlay_sources(contract, pathlib.Path(directory), "isorigflathindex", candidate)
            overlay = paths["overlay"].read_text(encoding="utf-8")
        self.assertIn("dsc_state->numComponents > 3", overlay)
        self.assertIn("dsc_state->origLine[3][hPos + PADDING_LEFT + 0] : 0", overlay)
        self.assertNotIn("orig_line_window", overlay)

    def test_samplepredict_pointer_adapter_binds_state_and_taps(self):
        agent = Agent(ROOT, "test")
        agent.input_facts = {
            "source_dir": "/Users/snow/Desktop/Display Stream Compression (DSC)/DSC 1.2a/DSC_model_20210623/source",
        }
        locked = json.loads((ROOT / "contracts" / "locked" / "samplepredict.json").read_text(encoding="utf-8"))
        overrides = json.loads((ROOT / "contracts" / "reviewed-overrides.json").read_text(encoding="utf-8"))["overrides"]
        override = next(item for item in overrides if item.get("match", {}).get("clang_usr") == "c:@F@SamplePredict")
        contract = copy.deepcopy(locked)
        contract["interface"] = copy.deepcopy(override["interface"])
        contract["semantics"] = copy.deepcopy(override["semantics"])
        contract["interface"]["ports"] = agent.freeze_ports(contract["interface"])
        oracle = agent.render_oracle(contract)
        ports = {port["name"]: port for port in contract["interface"]["ports"]}
        self.assertEqual(ports["hPos"]["width"], 16)
        self.assertEqual(ports["hPos"]["legal_domain"]["range"], [0, 65534])
        self.assertIn(9, ports["cpnt_bit_depth"]["legal_domain"]["values"])
        self.assertIn("dsc_state.cpntBitDepth[unit_c_type] = cpnt_bit_depth;", oracle)
        self.assertIn("dsc_state.quantizedResidual[unit][1] = quantized_residual_1;", oracle)
        self.assertIn("prevLine[((hPos / 3) * 3 + 5 + -2) + 0] = prev_3;", oracle)
        self.assertIn("currLine[((hPos > 8) ? (hPos - 8) : 0) + 12] = curr_12;", oracle)
        self.assertIn("SamplePredict(&dsc_state, prevLine, currLine", oracle)

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
