import json
import pathlib
import tempfile
import threading
import time
import unittest
from unittest import mock

from tools.cicd_agent import Agent, STATE_ORDER, contract_exact_links, digest, safe_identifier
from tools.generator_fixture import generic_body


class CicdAgentUnitTests(unittest.TestCase):
    def test_state_machine_is_monotonic_and_complete(self):
        self.assertEqual(STATE_ORDER[0], "DISCOVERED")
        self.assertEqual(STATE_ORDER[-1], "PROMOTED")
        self.assertEqual(len(STATE_ORDER), 9)

    def test_contract_selection_uses_contract_facts(self):
        contract = {
            "contract_id": "unit_alpha",
            "status": "LOCKED",
            "spec_links": [{"status": "EXACT", "anchor_id": "pdf:section:unit"}],
            "obligations": [],
            "dependencies": {"unresolved": []},
            "interface": {"inputs": [{"name": "value", "unresolved": False}], "flattened_pointer_dependencies": [], "output": {"unresolved": False}},
            "semantics": {"kind": "pure_expression"},
        }
        with tempfile.TemporaryDirectory() as directory:
            root = pathlib.Path(directory)
            (root / "contracts" / "locked").mkdir(parents=True)
            (root / "contracts" / "locked" / "unit_alpha.json").write_text(json.dumps(contract), encoding="utf-8")
            agent = Agent(root, "plan")
            agent.contracts = [contract]
            agent.dependency_info = {"cycles": [], "adjacency": {"unit_alpha": []}}
            ready, reasons = agent.ready(contract)
        self.assertTrue(ready)
        self.assertEqual(reasons, [])
        self.assertEqual(contract_exact_links(contract)[0]["status"], "EXACT")

    def test_cache_key_changes_when_dependency_hash_changes(self):
        contract = {"contract_id": "unit_beta", "function": {"name": "f_beta"}}
        with tempfile.TemporaryDirectory() as directory:
            agent = Agent(pathlib.Path(directory), "plan")
            agent.input_facts = {"source_hash": "s", "spec_hash": "p", "tool_versions": {"clang": "v"}}
            agent.dependency_info = {"dependency_hashes": {"unit_beta": "d1"}}
            first, _ = agent.cache_key(contract)
            agent.dependency_info["dependency_hashes"]["unit_beta"] = "d2"
            second, _ = agent.cache_key(contract)
        self.assertNotEqual(first, second)

    def test_cycle_detection_is_data_driven(self):
        with tempfile.TemporaryDirectory() as directory:
            root = pathlib.Path(directory)
            (root / "facts").mkdir()
            (root / "facts" / "callgraph.json").write_text(json.dumps({"edges": [
                {"caller_usr": "u_a", "callee_usr": "u_b", "caller_name": "f_a", "callee_name": "f_b", "location": {"line": 1}},
                {"caller_usr": "u_b", "callee_usr": "u_a", "caller_name": "f_b", "callee_name": "f_a", "location": {"line": 2}},
            ]}), encoding="utf-8")
            agent = Agent(root, "plan")
            agent.contracts = [
                {"contract_id": "a", "function": {"clang_usr": "u_a", "name": "f_a"}},
                {"contract_id": "b", "function": {"clang_usr": "u_b", "name": "f_b"}},
            ]
            graph = agent.dependency_graph()
        self.assertTrue(graph["cycles"])
        self.assertIn(["a", "b", "a"], graph["cycles"])

    def test_generated_identifiers_are_safe(self):
        self.assertEqual(safe_identifier("a.b-c"), "a_b_c")
        self.assertEqual(len(digest({"a": 1})), 64)

    def test_freeze_ports_deduplicates_flattened_pointer_fields(self):
        agent = Agent(pathlib.Path(tempfile.mkdtemp()), "test")
        ports = agent.freeze_ports({
            "inputs": [{"name": "value", "logical_width": 8, "signed": False}],
            "flattened_pointer_dependencies": [{
                "field": "value",
                "port_name": "value",
                "logical_width": 8,
                "signed": False,
            }],
            "output": {"name": "return_value", "logical_width": 8, "signed": False},
        })
        self.assertEqual([port["name"] for port in ports], ["value", "return_value"])

    def test_promoted_manifest_resolves_dynamic_contract_usr_from_tool_facts(self):
        with tempfile.TemporaryDirectory() as directory:
            root = pathlib.Path(directory)
            (root / "library").mkdir()
            (root / "library" / "manifest.json").write_text(json.dumps({
                "components": [{
                    "contract_id": "promoted_composite",
                    "function": "PromotedComposite",
                    "status": "PASS",
                }],
            }), encoding="utf-8")
            (root / "facts").mkdir()
            (root / "facts" / "functions.json").write_text(json.dumps({
                "functions": [{
                    "name": "PromotedComposite",
                    "clang_usr": "c:@F@PromotedComposite",
                }],
            }), encoding="utf-8")
            agent = Agent(root, "plan")
            promoted = agent.promoted_contract_usrs([])
        self.assertEqual(promoted, {"c:@F@PromotedComposite"})

    def test_reviewed_bounded_domain_admission_only_discharge_loop_bound(self):
        candidate = {
            "clang_usr": "c:@F@BoundedLeaf",
            "name": "BoundedLeaf",
            "eligible": False,
            "criteria": {
                "production_reachable": True,
                "contributes_to_observable_output": True,
                "no_direct_or_transitive_state_write": True,
                "no_io_allocation_or_logging": True,
                "bounded_computation": False,
            },
        }
        coverage = {"coverage_status": "EXECUTED", "covered": True}
        override = {
            "review_status": "REVIEWED",
            "spec_links": [{"anchor_id": "pdf:section:bounded", "status": "EXACT"}],
            "interface": {
                "inputs": [{
                    "name": "value",
                    "legal_domain": {"kind": "range", "range": [0, 255]},
                    "unresolved": False,
                }],
                "output": {"name": "return_value", "legal_range": [0, 8], "unresolved": False},
            },
            "semantics": {"kind": "pure_expression", "expression": "value"},
            "tool_admission": {
                "kind": "BOUNDED_DOMAIN",
                "status": "PASS",
                "loop": "while (value) value >>= 1",
                "max_iterations": 8,
            },
        }
        self.assertTrue(Agent.reviewed_bounded_domain_admission(candidate, coverage, override))

        bad = dict(override)
        bad["tool_admission"] = dict(override["tool_admission"])
        bad["tool_admission"]["max_iterations"] = 0
        self.assertFalse(Agent.reviewed_bounded_domain_admission(candidate, coverage, bad))

    def test_reviewed_combined_domain_admission_requires_one_proof_per_failed_fact(self):
        candidate = {
            "clang_usr": "c:@F@CompositeLeaf",
            "name": "CompositeLeaf",
            "eligible": False,
            "criteria": {
                "production_reachable": True,
                "contributes_to_observable_output": True,
                "no_direct_or_transitive_state_write": True,
                "no_io_allocation_or_logging": False,
                "bounded_computation": False,
            },
        }
        coverage = {"coverage_status": "EXECUTED", "covered": True}
        override = {
            "review_status": "REVIEWED",
            "spec_links": [{"anchor_id": "pdf:section:composite", "status": "EXACT"}],
            "interface": {
                "inputs": [{
                    "name": "value",
                    "legal_domain": {"kind": "range", "range": [-8, 8]},
                    "unresolved": False,
                }],
                "output": {"name": "return_value", "legal_range": [0, 32], "unresolved": False},
            },
            "semantics": {"kind": "composite_comb"},
            "tool_admissions": [
                {
                    "kind": "BOUNDED_DOMAIN",
                    "status": "PASS",
                    "loop": "for (i = 0; i < 4; ++i)",
                    "max_iterations": 4,
                },
                {
                    "kind": "DOMAIN_EFFECT",
                    "status": "PASS",
                    "discharged_effects": ["logging"],
                    "unreachable_condition": "value < -100 || value > 100",
                },
            ],
        }
        admission = Agent.reviewed_domain_admission(candidate, coverage, override)
        self.assertEqual(admission["kind"], "COMBINED_DOMAIN")
        self.assertEqual(admission["criteria_discharged"], ["bounded_computation", "no_io_allocation_or_logging"])

        missing = dict(override)
        missing["tool_admissions"] = [override["tool_admissions"][0]]
        self.assertIsNone(Agent.reviewed_domain_admission(candidate, coverage, missing))

        stateful = dict(candidate)
        stateful["criteria"] = dict(candidate["criteria"])
        stateful["criteria"]["no_direct_or_transitive_state_write"] = False
        self.assertIsNone(Agent.reviewed_domain_admission(stateful, coverage, override))

    def test_tool_candidate_facts_accepts_reviewed_bounded_domain_without_name_queue(self):
        candidate = {
            "clang_usr": "c:@F@BoundedLeaf",
            "name": "BoundedLeaf",
            "eligible": False,
            "score": 80.0,
            "criteria": {
                "production_reachable": True,
                "contributes_to_observable_output": True,
                "no_direct_or_transitive_state_write": True,
                "no_io_allocation_or_logging": True,
                "bounded_computation": False,
            },
        }
        override = {
            "match": {"clang_usr": "c:@F@BoundedLeaf", "spec_anchor_id": "pdf:section:bounded"},
            "review_status": "REVIEWED",
            "spec_links": [{"anchor_id": "pdf:section:bounded", "status": "EXACT"}],
            "interface": {
                "inputs": [{"name": "value", "legal_domain": {"kind": "range", "range": [0, 255]}, "unresolved": False}],
                "output": {"name": "return_value", "legal_range": [0, 8], "unresolved": False},
            },
            "semantics": {"kind": "pure_expression", "expression": "value"},
            "tool_admission": {"kind": "BOUNDED_DOMAIN", "status": "PASS", "loop": "while (value)", "max_iterations": 8},
        }
        with tempfile.TemporaryDirectory() as directory:
            root = pathlib.Path(directory)
            (root / "facts").mkdir()
            (root / "coverage").mkdir()
            (root / "contracts").mkdir()
            (root / "facts" / "candidates.json").write_text(json.dumps({"ranked_candidates": [candidate]}), encoding="utf-8")
            (root / "coverage" / "coverage.json").write_text(json.dumps({"functions": [{
                "clang_usr": "c:@F@BoundedLeaf",
                "coverage_status": "EXECUTED",
                "covered": True,
            }]}), encoding="utf-8")
            (root / "contracts" / "reviewed-overrides.json").write_text(json.dumps({"overrides": [override]}), encoding="utf-8")
            facts = Agent(root, "plan").tool_candidate_facts()
        self.assertIn("c:@F@BoundedLeaf", facts)
        self.assertEqual(facts["c:@F@BoundedLeaf"]["coverage_basis"], "reviewed_bounded_domain")

    def test_reviewed_domain_effect_only_discharges_out_of_domain_logging(self):
        candidate = {
            "clang_usr": "c:@F@DiagnosticLeaf",
            "name": "DiagnosticLeaf",
            "eligible": False,
            "criteria": {
                "production_reachable": True,
                "contributes_to_observable_output": True,
                "no_direct_or_transitive_state_write": True,
                "no_io_allocation_or_logging": False,
                "bounded_computation": True,
            },
        }
        coverage = {"coverage_status": "EXECUTED", "coverage": {"covered": True}}
        override = {
            "review_status": "REVIEWED",
            "spec_links": [{"anchor_id": "pdf:section:diagnostic", "status": "EXACT"}],
            "interface": {
                "inputs": [{
                    "name": "value",
                    "legal_domain": {"kind": "range", "range": [-4, 4]},
                    "unresolved": False,
                }],
                "output": {"name": "return_value", "legal_range": [0, 3], "unresolved": False},
            },
            "semantics": {"kind": "domain_effect"},
            "tool_admission": {
                "kind": "DOMAIN_EFFECT",
                "status": "PASS",
                "discharged_effects": ["logging"],
                "unreachable_condition": "value < -10 || value > 10",
            },
        }
        admission = Agent.reviewed_domain_admission(candidate, coverage, override)
        self.assertEqual(admission["kind"], "DOMAIN_EFFECT")

        bad = dict(override)
        bad["tool_admission"] = dict(override["tool_admission"])
        bad["tool_admission"]["discharged_effects"] = ["logging", "allocation"]
        self.assertIsNone(Agent.reviewed_domain_admission(candidate, coverage, bad))

        missing_output_domain = dict(override)
        missing_output_domain["interface"] = dict(override["interface"])
        missing_output_domain["interface"]["output"] = {"name": "return_value", "unresolved": False}
        self.assertIsNone(Agent.reviewed_domain_admission(candidate, coverage, missing_output_domain))

    def test_reviewed_config_library_admission_keeps_non_dut_boundary(self):
        candidate = {
            "clang_usr": "c:@F@ConfigLeaf",
            "name": "ConfigLeaf",
            "role": "CONFIG",
            "eligible": False,
            "criteria": {
                "production_reachable": True,
                "contributes_to_observable_output": False,
                "no_direct_or_transitive_state_write": True,
                "no_io_allocation_or_logging": True,
                "bounded_computation": True,
            },
        }
        coverage = {"coverage_status": "EXECUTED", "covered": True}
        override = {
            "review_status": "REVIEWED",
            "spec_links": [{"anchor_id": "pdf:table:config", "status": "EXACT"}],
            "interface": {
                "inputs": [{
                    "name": "mode",
                    "legal_domain": {"values": [0, 1]},
                    "unresolved": False,
                }],
                "output": {"name": "return_value", "legal_range": [0, 3], "unresolved": False},
            },
            "semantics": {"kind": "table_lookup"},
            "tool_admission": {
                "kind": "CONFIG_LIBRARY",
                "status": "PASS",
                "role": "CONFIG_HELPER",
                "non_dut_boundary": True,
            },
        }
        admission = Agent.reviewed_domain_admission(candidate, coverage, override)
        self.assertEqual(admission["kind"], "CONFIG_LIBRARY")

        bad_boundary = dict(override)
        bad_boundary["tool_admission"] = dict(override["tool_admission"])
        bad_boundary["tool_admission"]["non_dut_boundary"] = False
        self.assertIsNone(Agent.reviewed_domain_admission(candidate, coverage, bad_boundary))

        bad_criteria = dict(candidate)
        bad_criteria["criteria"] = dict(candidate["criteria"])
        bad_criteria["criteria"]["no_io_allocation_or_logging"] = False
        self.assertIsNone(Agent.reviewed_domain_admission(bad_criteria, coverage, override))

    def test_queue_target_selects_one_discovered_contract_and_refreshes_cache(self):
        contract = {
            "contract_id": "unit_target",
            "status": "LOCKED",
            "function": {"name": "TargetLeaf", "clang_usr": "c:@F@TargetLeaf"},
            "spec_links": [{"status": "EXACT", "anchor_id": "pdf:section:unit"}],
            "obligations": [],
            "dependencies": {"unresolved": []},
            "interface": {"ports": [
                {"name": "value", "direction": "input", "width": 8, "signed": False},
                {"name": "return_value", "direction": "output", "width": 8, "signed": False},
            ]},
            "semantics": {"kind": "pure_expression"},
        }
        with tempfile.TemporaryDirectory() as directory:
            root = pathlib.Path(directory)
            agent = Agent(root, "plan")
            agent.contracts = [contract]
            agent.dependency_info = {"cycles": [], "adjacency": {"unit_target": []}, "call_sites": [], "all_call_sites": [], "dependency_hashes": {}}
            with mock.patch.dict("os.environ", {"DSC_CICD_TARGET_CONTRACT": "unit_target", "DSC_CICD_FORCE_REGENERATE": "1"}, clear=False):
                plan = agent.build_plan()
        self.assertEqual(plan["selected_contracts"], ["unit_target"])
        self.assertEqual(plan["target_contract"], "unit_target")
        self.assertTrue(plan["force_regenerate"])
        self.assertTrue(plan["contracts"][0]["targeted"])
        self.assertTrue(plan["contracts"][0]["force_regenerate"])

    def test_refresh_stable_selects_tool_ready_manifest_frontier_in_parallel_batch(self):
        def contract(contract_id):
            return {
                "contract_id": contract_id,
                "status": "LOCKED",
                "function": {"name": contract_id, "clang_usr": f"c:@F@{contract_id}"},
                "spec_links": [{"status": "EXACT", "anchor_id": f"pdf:section:{contract_id}"}],
                "obligations": [],
                "dependencies": {"unresolved": []},
                "interface": {"ports": [
                    {"name": "value", "direction": "input", "width": 8, "signed": False},
                    {"name": "return_value", "direction": "output", "width": 8, "signed": False},
                ]},
                "semantics": {"kind": "pure_expression"},
            }

        with tempfile.TemporaryDirectory() as directory:
            root = pathlib.Path(directory)
            (root / "library").mkdir()
            (root / "library" / "manifest.json").write_text(json.dumps({
                "components": [
                    {"contract_id": "unit_alpha", "status": "PASS"},
                    {"contract_id": "unit_beta", "status": "PASS"},
                ],
            }), encoding="utf-8")
            agent = Agent(root, "plan")
            agent.contracts = [contract("unit_alpha"), contract("unit_beta")]
            agent.dependency_info = {
                "cycles": [],
                "adjacency": {"unit_alpha": [], "unit_beta": []},
                "call_sites": [],
                "all_call_sites": [],
                "dependency_hashes": {},
            }
            with mock.patch.dict("os.environ", {
                "DSC_CICD_TARGET_CONTRACT": "",
                "DSC_CICD_REFRESH_STABLE": "1",
                "DSC_CICD_MAX_NEW": "2",
            }, clear=False):
                plan = agent.build_plan()
        self.assertEqual(plan["selected_contracts"], ["unit_alpha", "unit_beta"])
        self.assertTrue(plan["refresh_stable"])
        self.assertTrue(plan["force_regenerate"])
        self.assertTrue(all(item["force_regenerate"] for item in plan["contracts"]))

    def test_promoted_candidate_materializes_stable_library_and_archives_replacement(self):
        contract = {
            "contract_id": "fixture_leaf",
            "status": "LOCKED",
            "function": {
                "name": "FixtureLeaf",
                "clang_usr": "c:@F@FixtureLeaf",
                "source_file": "dsc_codec.c",
                "source_span": {"start_line": 10, "end_line": 12},
            },
            "interface": {"ports": [
                {"name": "value", "direction": "input", "width": 8, "signed": False},
                {"name": "return_value", "direction": "output", "width": 8, "signed": False},
            ]},
            "semantics": {"kind": "pure_expression"},
            "obligations": [],
            "dependencies": {"unresolved": []},
            "spec_links": [{"status": "EXACT", "anchor_id": "pdf:section:fixture"}],
        }
        with tempfile.TemporaryDirectory() as directory:
            root = pathlib.Path(directory).resolve()
            artifact = root / "artifacts" / "fixture-hash"
            (artifact / "generated").mkdir(parents=True)
            (artifact / "generated" / "candidate_01.sv").write_text(
                "module fixture_leaf_candidate_01(input logic [7:0] value, output logic [7:0] return_value);\n"
                "  assign return_value = value;\n"
                "endmodule\n",
                encoding="utf-8",
            )
            (root / "library" / "rtl").mkdir(parents=True)
            (root / "library" / "rtl" / "fixture_leaf.sv").write_text(
                "module fixture_leaf(input logic [7:0] value, output logic [7:0] return_value); assign return_value = 0; endmodule\n",
                encoding="utf-8",
            )
            (root / "library" / "manifest.json").write_text(json.dumps({"components": []}), encoding="utf-8")
            agent = Agent(root, "run")
            agent.input_facts = {"spec_hash": "pdf-hash", "source_hash": "source-hash", "baseline_hash": "baseline-hash"}
            result = {
                "status": "PROMOTED",
                "execution_status": "EXECUTED_NOW",
                "generation": {"status": "PASS"},
                "unit": {
                    "promoted_candidate": "candidate_01",
                    "verification_status": "EXHAUSTIVE_EQUIVALENT",
                    "domain": {"total_vectors": 4},
                    "candidates": [{"candidate": "candidate_01", "formal_proof": {"status": "NOT_APPLICABLE"}}],
                },
                "dependency": {"status": "PASS"},
                "matrix": {"status": "PASS", "modes": {"C_ONLY": {"status": "PASS"}, "SHADOW": {"status": "PASS"}, "RTL_RETURN": {"status": "PASS"}}},
            }
            promotion = agent.promote_library_component(
                contract,
                {"contract_id": "fixture_leaf", "contract_hash": "fixture-hash"},
                artifact,
                result,
            )
            stable = (root / "library" / "rtl" / "fixture_leaf.sv").read_text(encoding="utf-8")
            manifest = json.loads((root / "library" / "manifest.json").read_text(encoding="utf-8"))
            verification = json.loads((root / "library" / "verification" / "fixture_leaf.json").read_text(encoding="utf-8"))
            promoted_contract = json.loads((root / "library" / "contracts" / "fixture_leaf.json").read_text(encoding="utf-8"))
        self.assertEqual(promotion["status"], "PASS")
        self.assertIn("module fixture_leaf(", stable)
        self.assertNotIn("candidate_01", stable)
        self.assertTrue(promotion["archived_previous"])
        self.assertEqual(manifest["components"][0]["status"], "PASS")
        self.assertEqual(manifest["components"][0]["module_sha256"], promotion["rtl_sha256"])
        self.assertEqual(verification["status"], "PASS")
        self.assertTrue(promoted_contract["do_not_edit"])

    def test_independent_selected_contracts_run_in_parallel_batches(self):
        with tempfile.TemporaryDirectory() as directory:
            agent = Agent(pathlib.Path(directory), "run")
            agent.plan = {
                "contracts": [
                    {"contract_id": "alpha", "selected": True},
                    {"contract_id": "beta", "selected": True},
                ]
            }
            agent.dependency_info = {"adjacency": {"alpha": [], "beta": []}}
            active = 0
            peak = 0
            guard = threading.Lock()

            def fake_run(item):
                nonlocal active, peak
                with guard:
                    active += 1
                    peak = max(peak, active)
                time.sleep(0.03)
                with guard:
                    active -= 1
                result = {"contract_id": item["contract_id"], "status": "PROMOTED"}
                agent.append_result(result)
                return result

            with mock.patch.object(agent, "run_contract", side_effect=fake_run):
                with mock.patch.dict("os.environ", {"DSC_CICD_CONTRACT_WORKERS": "2"}, clear=False):
                    agent.run_selected_batches()
        self.assertEqual(peak, 2)
        self.assertEqual([item["contract_id"] for item in agent.run_results], ["alpha", "beta"])

    def test_selected_callee_finishes_before_selected_caller(self):
        with tempfile.TemporaryDirectory() as directory:
            agent = Agent(pathlib.Path(directory), "run")
            agent.plan = {
                "contracts": [
                    {"contract_id": "caller", "selected": True},
                    {"contract_id": "callee", "selected": True},
                ]
            }
            agent.dependency_info = {"adjacency": {"caller": ["callee"], "callee": []}}
            order = []

            def fake_run(item):
                order.append(item["contract_id"])
                result = {"contract_id": item["contract_id"], "status": "PROMOTED"}
                agent.append_result(result)
                return result

            with mock.patch.object(agent, "run_contract", side_effect=fake_run):
                agent.run_selected_batches()
        self.assertEqual(order, ["callee", "caller"])

    def test_reviewed_override_resolves_locked_leaf_without_editing_lock(self):
        contract = {
            "contract_id": "locked_leaf",
            "status": "LOCKED",
            "function": {"name": "LockedLeaf", "clang_usr": "c:@F@LockedLeaf"},
            "interface": {"inputs": [], "output": {"unresolved": True}},
            "dependencies": {"unresolved": ["field:unknown"]},
        }
        override = {
            "match": {"clang_usr": "c:@F@LockedLeaf", "spec_anchor_id": "pdf:section:test"},
            "review_status": "REVIEWED",
            "interface": {
                "inputs": [{"name": "value", "logical_width": 4, "unresolved": False}],
                "output": {"name": "return_value", "logical_width": 1, "unresolved": False},
            },
            "semantics": {"expression": "value >= 3"},
            "spec_links": [{"anchor_id": "pdf:section:test", "status": "EXACT"}],
        }
        with tempfile.TemporaryDirectory() as directory:
            root = pathlib.Path(directory)
            (root / "contracts").mkdir()
            (root / "contracts" / "reviewed-overrides.json").write_text(
                json.dumps({"overrides": [override]}), encoding="utf-8"
            )
            agent = Agent(root, "plan")
            agent.locked_contracts = [contract]
            effective = agent.apply_reviewed_overrides()
            self.assertEqual(effective[0]["origin"], "tool_discovered_reviewed_override")
            self.assertEqual(effective[0]["spec_links"][0]["status"], "EXACT")
            self.assertEqual(effective[0]["semantics"]["expression"], "value >= 3")
            self.assertEqual(effective[0]["dependencies"]["unresolved"], [])
            self.assertTrue((root / "ci" / "reviewed-contracts" / "locked_leaf.json").is_file())

    def test_materialize_new_contract_uses_reviewed_exact_anchor_not_target_name(self):
        with tempfile.TemporaryDirectory() as directory:
            root = pathlib.Path(directory)
            source_dir = root / "source"
            source_dir.mkdir(parents=True)
            (source_dir / "dsc_codec.c").write_text(
                "int ToolDiscoveredLeaf(int value) { return value; }\n", encoding="utf-8"
            )
            (root / "facts").mkdir()
            (root / "facts" / "functions.json").write_text(json.dumps({
                "functions": [{
                    "clang_usr": "c:@F@ToolDiscoveredLeaf",
                    "name": "ToolDiscoveredLeaf",
                    "source_file": "dsc_codec.c",
                    "line": 1,
                    "return_type": "int",
                    "parameters": [{"name": "value", "pointer": False, "type": "int"}],
                    "callees": [],
                    "proposal": {"combinational_candidate": True},
                }],
            }), encoding="utf-8")
            (root / "facts" / "candidates.json").write_text(json.dumps({
                "ranked_candidates": [{
                    "clang_usr": "c:@F@ToolDiscoveredLeaf",
                    "eligible": True,
                    "score": 100.0,
                }],
            }), encoding="utf-8")
            (root / "coverage").mkdir()
            (root / "coverage" / "coverage.json").write_text(json.dumps({
                "functions": [{
                    "clang_usr": "c:@F@ToolDiscoveredLeaf",
                    "eligible_after_coverage": True,
                }],
            }), encoding="utf-8")
            (root / "traceability" ).mkdir()
            (root / "traceability" / "traceability.json").write_text(json.dumps({"links": [{
                "clang_usr": "c:@F@ToolDiscoveredLeaf",
                "spec_anchor_id": "pdf:section:test",
                "spec_page": 1,
                "spec_section": "test",
                "status": "EXACT",
            }]}), encoding="utf-8")
            (root / "contracts").mkdir()
            (root / "contracts" / "reviewed-overrides.json").write_text(json.dumps({"overrides": [{
                "match": {"exact_anchor_id": "pdf:section:test"},
                "review_status": "REVIEWED",
                "interface": {
                    "inputs": [{
                        "name": "value",
                        "logical_width": 4,
                        "signed": False,
                        "legal_domain": {"kind": "range", "range": [0, 15]},
                        "unresolved": False,
                    }],
                    "output": {
                        "name": "return_value",
                        "logical_width": 4,
                        "signed": False,
                        "legal_range": [0, 15],
                        "unresolved": False,
                    },
                },
                "semantics": {"kind": "pure_expression", "expression": "value"},
                "spec_links": [{"anchor_id": "pdf:section:test", "status": "EXACT"}],
            }]}), encoding="utf-8")
            agent = Agent(root, "plan")
            agent.input_facts = {"errors": [], "source_dir": str(source_dir)}
            discovered = agent.materialize_new_contracts()
            self.assertEqual([item["contract_id"] for item in discovered], ["tooldiscoveredleaf"])
            self.assertEqual(discovered[0]["spec_links"][0]["status"], "EXACT")
            self.assertTrue((root / "ci" / "discovered-contracts" / "tooldiscoveredleaf.json").is_file())

    def test_oracle_supports_multiple_flattened_record_dependencies(self):
        contract = {
            "contract_id": "multi_record_leaf",
            "function": {
                "name": "MultiRecordLeaf",
                "parameters": [
                    {"name": "dsc_cfg", "pointer": True, "type": "dsc_cfg_t *"},
                    {"name": "dsc_state", "pointer": True, "type": "dsc_state_t *"},
                    {"name": "x", "pointer": False, "type": "int"},
                    {"name": "cpnt", "pointer": False, "type": "int"},
                ],
            },
            "interface": {
                "ports": [
                    {"name": "x", "direction": "input", "width": 16, "signed": False},
                    {"name": "cpnt", "direction": "input", "width": 2, "signed": False},
                    {"name": "cpntBitDepth", "direction": "input", "width": 5, "signed": False},
                    {"name": "linebuf_depth", "direction": "input", "width": 4, "signed": False},
                    {"name": "return_value", "direction": "output", "width": 16, "signed": False},
                ],
                "flattened_pointer_dependencies": [
                    {"record": "dsc_state_t", "field": "cpntBitDepth", "c_type": "int[4]"},
                    {"record": "dsc_cfg_t", "field": "linebuf_depth", "c_type": "int"},
                ],
            },
        }
        oracle = Agent(pathlib.Path(tempfile.mkdtemp()), "test").render_oracle(contract)
        self.assertIn("extern int MultiRecordLeaf(dsc_cfg_t * dsc_cfg, dsc_state_t * dsc_state, int x, int cpnt);", oracle)
        self.assertIn("dsc_cfg.linebuf_depth = linebuf_depth;", oracle)
        self.assertIn("dsc_state.cpntBitDepth[i] = cpntBitDepth;", oracle)
        self.assertIn("MultiRecordLeaf(&dsc_cfg, &dsc_state, x, cpnt)", oracle)

    def test_oracle_supports_flattened_pointer_array_and_unused_pointer(self):
        contract = {
            "contract_id": "predict_size",
            "function": {
                "name": "PredictSize",
                "parameters": [
                    {"name": "dsc_cfg", "pointer": True, "type": "dsc_cfg_t *"},
                    {"name": "req_size", "pointer": True, "type": "int *"},
                ],
            },
            "interface": {
                "ports": [
                    {"name": "req_size_0", "direction": "input", "width": 5, "signed": False},
                    {"name": "req_size_1", "direction": "input", "width": 5, "signed": False},
                    {"name": "req_size_2", "direction": "input", "width": 5, "signed": False},
                    {"name": "return_value", "direction": "output", "width": 5, "signed": False},
                ],
                "flattened_pointer_dependencies": [
                    {"parameter": "req_size", "field": "req_size[0]", "port_name": "req_size_0", "index": 0, "c_type": "int *"},
                    {"parameter": "req_size", "field": "req_size[1]", "port_name": "req_size_1", "index": 1, "c_type": "int *"},
                    {"parameter": "req_size", "field": "req_size[2]", "port_name": "req_size_2", "index": 2, "c_type": "int *"},
                ],
                "ignored_pointer_dependencies": [
                    {"parameter": "dsc_cfg", "c_type": "dsc_cfg_t *", "role": "UNUSED_DEPENDENCY"},
                ],
            },
        }
        oracle = Agent(pathlib.Path(tempfile.mkdtemp()), "test").render_oracle(contract)
        self.assertIn("extern int PredictSize(dsc_cfg_t * dsc_cfg, int * req_size);", oracle)
        self.assertIn("int req_size[3] = {0};", oracle)
        self.assertIn("req_size[2] = req_size_2;", oracle)
        self.assertIn("dsc_cfg_t dsc_cfg = {0};", oracle)
        self.assertIn("PredictSize(&dsc_cfg, req_size)", oracle)

    def test_oracle_and_overlay_support_dynamic_struct_table_entries(self):
        contract = {
            "contract_id": "map_qp_to_qlevel",
            "function": {
                "name": "MapQpToQlevel",
                "parameters": [
                    {"name": "dsc_cfg", "pointer": True, "type": "dsc_cfg_t *"},
                    {"name": "dsc_state", "pointer": True, "type": "dsc_state_t *"},
                    {"name": "qp", "pointer": False, "type": "int"},
                    {"name": "cpnt", "pointer": False, "type": "int"},
                ],
            },
            "interface": {
                "inputs": [
                    {"name": "cpnt", "logical_width": 2, "signed": False},
                    {"name": "qp", "logical_width": 5, "signed": False},
                ],
                "flattened_pointer_dependencies": [
                    {"record": "dsc_cfg_t", "field": "dsc_version_minor", "port_name": "dsc_version_minor", "c_type": "int"},
                    {"record": "dsc_state_t", "field": "cpntBitDepth", "port_name": "cpntBitDepth_0", "index": 0, "c_type": "int[4]"},
                    {"record": "dsc_state_t", "field": "quantTableLuma", "port_name": "qlevel_luma", "index_name": "qp", "array_length": 32, "c_type": "int *"},
                ],
                "output": {"name": "return_value", "logical_width": 5, "signed": False},
            },
        }
        with tempfile.TemporaryDirectory() as directory:
            root = pathlib.Path(directory)
            agent = Agent(root, "test")
            agent.input_facts = {"source_dir": str(root)}
            contract["interface"]["ports"] = agent.freeze_ports(contract["interface"])
            oracle = agent.render_oracle(contract)
            self.assertIn("quantTableLuma_oracle_storage[qp] = qlevel_luma;", oracle)
            self.assertIn("dsc_state.quantTableLuma = quantTableLuma_oracle_storage;", oracle)
            self.assertIn("dsc_state.cpntBitDepth[0] = cpntBitDepth_0;", oracle)
            agent.write_overlay_sources(contract, root, "map_qp_to_qlevel", root / "candidate.sv")
            overlay = (root / "dsc_cicd_overlay.c").read_text(encoding="utf-8")
            self.assertIn("dsc_cfg->dsc_version_minor", overlay)
            self.assertIn("dsc_state->quantTableLuma[qp]", overlay)
            self.assertIn("dsc_state->cpntBitDepth[0]", overlay)

    def test_oracle_supports_dynamic_index_into_fixed_struct_array(self):
        contract = {
            "contract_id": "selected_component",
            "function": {
                "name": "SelectedComponent",
                "parameters": [
                    {"name": "dsc_cfg", "pointer": True, "type": "dsc_cfg_t *"},
                    {"name": "dsc_state", "pointer": True, "type": "dsc_state_t *"},
                    {"name": "cpnt", "pointer": False, "type": "int"},
                ],
            },
            "interface": {
                "inputs": [{"name": "cpnt", "logical_width": 2, "signed": False}],
                "flattened_pointer_dependencies": [
                    {
                        "record": "dsc_cfg_t",
                        "field": "native_420",
                        "port_name": "native_420",
                        "c_type": "int",
                    },
                    {
                        "record": "dsc_state_t",
                        "field": "cpntBitDepth",
                        "index_name": "cpnt",
                        "port_name": "cpntBitDepth_selected",
                        "c_type": "int[4]",
                    },
                ],
                "output": {"name": "return_value", "logical_width": 5, "signed": False},
            },
        }
        agent = Agent(pathlib.Path(tempfile.mkdtemp()), "test")
        contract["interface"]["ports"] = agent.freeze_ports(contract["interface"])
        oracle = agent.render_oracle(contract)
        self.assertIn("dsc_state.cpntBitDepth[cpnt] = cpntBitDepth_selected;", oracle)
        self.assertNotIn("cpntBitDepth_oracle_storage", oracle)

    def test_oracle_supports_nested_state_array_indices(self):
        contract = {
            "contract_id": "nested_state_array",
            "function": {
                "name": "NestedStateArray",
                "parameters": [
                    {"name": "dsc_state", "pointer": True, "type": "dsc_state_t *"},
                    {"name": "unit", "pointer": False, "type": "int"},
                ],
            },
            "interface": {
                "inputs": [{"name": "unit", "logical_width": 2, "signed": False}],
                "flattened_pointer_dependencies": [
                    {
                        "record": "dsc_state_t",
                        "field": "quantizedResidual",
                        "index_names": ["unit", 0],
                        "port_name": "quantized_residual_0",
                        "c_type": "int[4][3]",
                    },
                    {
                        "record": "dsc_state_t",
                        "field": "quantizedResidual",
                        "index_names": ["unit", 1],
                        "port_name": "quantized_residual_1",
                        "c_type": "int[4][3]",
                    },
                ],
                "output": {"name": "return_value", "logical_width": 1, "signed": False},
            },
        }
        agent = Agent(pathlib.Path(tempfile.mkdtemp()), "test")
        contract["interface"]["ports"] = agent.freeze_ports(contract["interface"])
        oracle = agent.render_oracle(contract)
        self.assertIn("dsc_state.quantizedResidual[unit][0] = quantized_residual_0;", oracle)
        self.assertIn("dsc_state.quantizedResidual[unit][1] = quantized_residual_1;", oracle)

    def test_oracle_resolves_camel_case_state_index_to_frozen_port(self):
        contract = {
            "contract_id": "state_table_alias",
            "function": {
                "name": "StateTableAlias",
                "parameters": [
                    {"name": "dsc_state", "pointer": True, "type": "dsc_state_t *"},
                    {"name": "unit", "pointer": False, "type": "int"},
                ],
            },
            "interface": {
                "inputs": [{"name": "unit", "logical_width": 2, "signed": False}],
                "flattened_pointer_dependencies": [
                    {
                        "record": "dsc_state_t",
                        "field": "primaryQp",
                        "port_name": "primary_qp",
                        "c_type": "int",
                    },
                    {
                        "record": "dsc_state_t",
                        "field": "quantTableLuma",
                        "port_name": "qlevel_luma",
                        "index_name": "primaryQp",
                        "array_length": 32,
                        "c_type": "int *",
                    },
                ],
                "output": {"name": "return_value", "logical_width": 5, "signed": False},
            },
        }
        agent = Agent(pathlib.Path(tempfile.mkdtemp()), "test")
        contract["interface"]["ports"] = agent.freeze_ports(contract["interface"])
        oracle = agent.render_oracle(contract)
        self.assertIn("dsc_state.primaryQp = primary_qp;", oracle)
        self.assertIn("quantTableLuma_oracle_storage[primary_qp] = qlevel_luma;", oracle)

    def test_flattened_state_oracle_and_conditional_domain(self):
        contract = {
            "contract_id": "state_leaf",
            "status": "LOCKED",
            "function": {"name": "StateLeaf"},
            "spec_links": [{"status": "EXACT", "anchor_id": "pdf:section:unit"}],
            "interface": {
                "flattened_pointer_dependencies": [
                    {"record": "dsc_state_t", "field": "cpntBitDepth", "c_type": "int[4]"},
                    {"record": "dsc_state_t", "field": "leftRecon", "c_type": "int[4]"},
                ],
                "ports": [
                    {"name": "cpnt", "direction": "input", "width": 1, "signed": False, "legal_domain": {"range": [0, 0]}},
                    {"name": "qlevel", "direction": "input", "width": 2, "signed": False, "legal_domain": {"range": [0, 3]}},
                    {"name": "cpntBitDepth", "direction": "input", "width": 2, "signed": False, "legal_domain": {"values": [2, 3]}},
                    {"name": "leftRecon", "direction": "input", "width": 3, "signed": False, "legal_domain": {"range": [0, 7]}},
                    {"name": "return_value", "direction": "output", "width": 4, "signed": False},
                ],
            },
            "semantics": {"qlevel_max_by_cpnt_bit_depth": {"2": 1, "3": 2}},
        }
        agent = Agent(pathlib.Path(tempfile.mkdtemp()), "test")
        oracle = agent.render_oracle(contract)
        self.assertIn("dsc_state_t *dsc_state", oracle)
        self.assertIn("dsc_state.cpntBitDepth[i] = cpntBitDepth", oracle)
        self.assertIn("StateLeaf(&dsc_state, cpnt, qlevel)", oracle)
        with tempfile.TemporaryDirectory() as directory:
            artifact = pathlib.Path(directory) / "artifact"
            result = agent.make_shards(contract, artifact)
            self.assertEqual(result["total_vectors"], 32)
            self.assertEqual(result["vector_strategy"]["kind"], "conditional")

    def test_table_lookup_domain_derives_selected_values_from_qp(self):
        contract = {
            "contract_id": "table_relation",
            "interface": {
                "ports": [
                    {"name": "unit", "direction": "input", "legal_domain": {"values": [0, 1]}},
                    {"name": "cpntBitDepth_0", "direction": "input", "legal_domain": {"values": [8, 10]}},
                    {"name": "cpntBitDepth_1", "direction": "input", "legal_domain": {"values": [8, 9, 10, 11]}},
                    {"name": "cpntBitDepth_2", "direction": "input", "legal_domain": {"values": [8, 9, 10, 11]}},
                    {"name": "cpntBitDepth_3", "direction": "input", "legal_domain": {"values": [8, 10]}},
                    {"name": "unit_c_type_selected", "direction": "input", "legal_domain": {"values": [0, 1]}},
                    {"name": "predicted_size_selected", "direction": "input", "legal_domain": {"values": [0, 1]}},
                    {"name": "primary_qp", "direction": "input", "legal_domain": {"range": [0, 31]}},
                    {"name": "prev_primary_qp", "direction": "input", "legal_domain": {"range": [0, 31]}},
                    {"name": "qlevel_luma_new", "direction": "input", "legal_domain": {"range": [0, 16]}},
                    {"name": "qlevel_chroma_new", "direction": "input", "legal_domain": {"range": [0, 16]}},
                    {"name": "qlevel_luma_old", "direction": "input", "legal_domain": {"range": [0, 16]}},
                    {"name": "qlevel_chroma_old", "direction": "input", "legal_domain": {"range": [0, 16]}},
                    {"name": "return_value", "direction": "output"},
                ]
            },
            "semantics": {
                "legal_vector_strategy": {
                    "kind": "table_lookup",
                    "base_bit_depth_port": "cpntBitDepth_0",
                    "bit_depth_ports": {
                        "cpntBitDepth_1": {"values_by_base": {"8": [8, 9], "10": [10]}},
                        "cpntBitDepth_2": {"values_by_base": {"8": [8], "10": [10]}},
                        "cpntBitDepth_3": {"values_by_base": {"8": [8], "10": [10]}},
                    },
                    "table_bindings": {
                        "qlevel_luma_new": {"table": "luma", "qp_port": "primary_qp"},
                        "qlevel_chroma_new": {"table": "chroma", "qp_port": "primary_qp"},
                        "qlevel_luma_old": {"table": "luma", "qp_port": "prev_primary_qp"},
                        "qlevel_chroma_old": {"table": "chroma", "qp_port": "prev_primary_qp"},
                    },
                    "tables": {
                        "luma": {"8": [0, 1], "10": [2, 3, 4]},
                        "chroma": {"8": [5, 6], "10": [7, 8, 9]},
                    },
                }
            },
        }
        agent = Agent(pathlib.Path(tempfile.mkdtemp()), "test")
        with tempfile.TemporaryDirectory() as directory:
            result = agent.make_shards(contract, pathlib.Path(directory) / "artifact")
        self.assertEqual(result["vector_strategy"]["kind"], "table_lookup")
        self.assertEqual(result["total_vectors"], 136)
        shard_lines = []
        with tempfile.TemporaryDirectory() as directory:
            artifact = pathlib.Path(directory) / "artifact"
            result = agent.make_shards(contract, artifact)
            for path in sorted((artifact / "shards").glob("*.vectors")):
                shard_lines.extend(path.read_text(encoding="utf-8").splitlines())
        rows = [[int(value) for value in line.split()] for line in shard_lines]
        matching = [row for row in rows if row[1] == 8 and row[7] == 0 and row[8] == 0]
        self.assertTrue(matching)
        self.assertTrue(all(row[9:13] == [0, 5, 0, 5] for row in matching))

    def test_qp_table_domain_keeps_qp_within_selected_table_row(self):
        contract = {
            "contract_id": "qp_table_relation",
            "interface": {
                "ports": [
                    {"name": "bits_per_component", "direction": "input", "legal_domain": {"values": [8, 10]}},
                    {"name": "qp", "direction": "input", "legal_domain": {"range": [0, 31]}},
                    {"name": "cpnt", "direction": "input", "legal_domain": {"values": [0, 1]}},
                    {"name": "return_value", "direction": "output"},
                ]
            },
            "semantics": {
                "legal_vector_strategy": {
                    "kind": "qp_table",
                    "base_bit_depth_port": "bits_per_component",
                    "qp_port": "qp",
                },
                "tables": {
                    "luma": {"8": [0, 1], "10": [0, 1, 2]},
                    "chroma": {"8": [0, 1], "10": [0, 1, 2]},
                },
            },
        }
        agent = Agent(pathlib.Path(tempfile.mkdtemp()), "test")
        with tempfile.TemporaryDirectory() as directory:
            artifact = pathlib.Path(directory) / "artifact"
            result = agent.make_shards(contract, artifact)
            rows = [
                [int(value) for value in line.split()]
                for path in sorted((artifact / "shards").glob("*.vectors"))
                for line in path.read_text(encoding="utf-8").splitlines()
            ]
        self.assertEqual(result["vector_strategy"]["kind"], "qp_table")
        self.assertEqual(result["total_vectors"], 10)
        self.assertEqual(max(row[1] for row in rows if row[0] == 8), 1)
        self.assertEqual(max(row[1] for row in rows if row[0] == 10), 2)

    def test_flatness_window_strategy_is_data_driven_and_bounded(self):
        root = pathlib.Path(__file__).resolve().parents[1]
        contract = json.loads(
            (root / "library" / "contracts" / "isorigflathindex.json").read_text(encoding="utf-8")
        )
        agent = Agent(root, "test")
        ports = contract["interface"]["ports"]
        input_ports = [port for port in ports if port.get("direction") == "input"]
        values = [agent.port_domain(port) for port in input_ports]
        vectors, receipt = agent.legal_vector_iterator(contract, input_ports, values)
        first = next(iter(vectors))
        self.assertEqual(len(first), len(input_ports))
        self.assertFalse(receipt["exhaustive"])
        self.assertEqual(receipt["kind"], "flatness_window")
        self.assertEqual(receipt["coverage_mode"], "STRUCTURAL_PLUS_BOUNDARY_AND_PAIRWISE_FLATNESS_TAPS")
        self.assertEqual(len(receipt["sample_ports_by_component"]), 4)
        self.assertGreater(receipt["structural_cases"], 0)

    def test_generator_maps_c_style_semantic_identifiers_to_frozen_ports(self):
        interface = {
            "ports": [
                {"name": "cpntBitDepth", "role": "cpntBitDepth", "direction": "input"},
                {"name": "leftRecon", "role": "leftRecon", "direction": "input"},
                {"name": "qlevel", "role": "qlevel", "direction": "input"},
                {"name": "return_value", "role": "return_value", "direction": "output"},
            ]
        }
        body = generic_body(interface, {"expression": "(1 << (cpnt_bit_depth - 1)) + (left_recon % (1 << qlevel))"}, False)
        self.assertIn("cpntBitDepth", body)
        self.assertIn("leftRecon", body)
        self.assertIn("qlevel", body)
        self.assertNotIn("cpnt_bit_depth", body)


if __name__ == "__main__":
    unittest.main()
