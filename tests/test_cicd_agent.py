import json
import pathlib
import tempfile
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
