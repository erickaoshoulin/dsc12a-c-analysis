import pathlib
import sys
import unittest


ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))

import create_contracts  # noqa: E402


class ContractSelectionTests(unittest.TestCase):
    def test_frontier_keeps_dependency_candidates_visible_before_leaf_gate(self):
        functions = {
            "functions": [
                {"clang_usr": "U_leaf", "name": "leaf", "source_file": "dsc_codec.c", "callees": []},
                {
                    "clang_usr": "U_caller",
                    "name": "caller",
                    "source_file": "dsc_codec.c",
                    "callees": [{"clang_usr": "U_leaf", "name": "leaf"}],
                },
            ]
        }
        candidates = {
            "ranked_candidates": [
                {"clang_usr": "U_caller", "name": "caller", "eligible": True, "score": 2.0},
                {"clang_usr": "U_leaf", "name": "leaf", "eligible": True, "score": 1.0},
            ]
        }
        coverage = {
            "functions": [
                {"clang_usr": "U_caller", "eligible_after_coverage": True, "coverage_status": "EXECUTED"},
                {"clang_usr": "U_leaf", "eligible_after_coverage": True, "coverage_status": "EXECUTED"},
            ]
        }

        frontier = create_contracts.build_candidate_frontier(functions, candidates, coverage, 2)
        records = [create_contracts.frontier_record(item) for item in frontier]

        self.assertEqual([item[1]["name"] for item in frontier], ["caller", "leaf"])
        self.assertEqual(records[0]["selection_state"], "DEPENDENCY_DEFERRED")
        self.assertEqual(records[0]["direct_callees"][0]["name"], "leaf")
        self.assertEqual(records[1]["selection_state"], "LEAF_SELECTED")


if __name__ == "__main__":
    unittest.main()
