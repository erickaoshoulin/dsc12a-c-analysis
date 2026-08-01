import json
import pathlib
import tempfile
import unittest

from tools.cicd_agent import Agent, STATE_ORDER, contract_exact_links, digest, safe_identifier


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


if __name__ == "__main__":
    unittest.main()
