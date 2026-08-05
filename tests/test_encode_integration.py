import hashlib
import json
import pathlib
import tempfile
import unittest

from tools.verify_encode_integration import (
    absorbed_rtl_dependencies,
    compare_dsc_frame,
    discover_encode_candidates,
    encode_frontier,
    namespace_adapter_text,
    parse_overlay_metrics,
    source_order_encode_candidates,
)
from tools.verify_decode_integration import (
    active_absorbed_rtl_dependencies,
    render_private_oracle_wrapper,
    route_adapter_child_dispatchers,
)


class EncodeIntegrationTests(unittest.TestCase):
    def test_hash_pinned_absorption_propagates_through_parent_rtl(self):
        totals = {
            "top": {"rtl_invocations": 5},
            "middle": {"rtl_invocations": 0},
            "leaf": {"rtl_invocations": 0},
        }
        dependencies = {
            "middle": [{
                "parent_slug": "top",
                "contract_hash_match": True,
                "candidate_hash_match": True,
            }],
            "leaf": [{
                "parent_slug": "middle",
                "contract_hash_match": True,
                "candidate_hash_match": True,
            }],
        }
        active = active_absorbed_rtl_dependencies(totals, dependencies)
        self.assertEqual(
            active["middle"][0]["parent_execution_class"], "DIRECT_RTL"
        )
        self.assertEqual(
            active["leaf"][0]["parent_execution_class"],
            "ABSORBED_BY_PARENT_RTL",
        )

    def test_hash_pinned_unrouted_child_is_absorbed_by_parent_rtl(self):
        child = {
            "function": "ChildFn",
            "slug": "child_transition",
            "contract_sha256": "a" * 64,
            "candidate_sha256": "b" * 64,
            "contract": {"function": {"name": "ChildFn"}},
            "composition": {"simultaneous_child_dispatchers": []},
        }
        parent = {
            "function": "ParentFn",
            "slug": "parent_transition",
            "contract_sha256": "c" * 64,
            "candidate_sha256": "d" * 64,
            "contract": {
                "function": {"name": "ParentFn"},
                "dependencies": [
                    {
                        "function": "ChildFn",
                        "contract_sha256": "a" * 64,
                        "module_sha256": "b" * 64,
                    }
                ],
            },
            "composition": {"simultaneous_child_dispatchers": []},
        }
        absorbed = absorbed_rtl_dependencies([parent, child])
        self.assertEqual(
            absorbed["child_transition"][0]["parent_slug"],
            "parent_transition",
        )
        parent["composition"]["simultaneous_child_dispatchers"] = [
            {
                "function": "ChildFn",
                "dispatcher": "dsc_cicd_child_transition_invoke",
                "replacements": "2",
            }
        ]
        self.assertEqual(absorbed_rtl_dependencies([parent, child]), {})

    def test_frozen_callee_evidence_is_hash_bound_at_integration(self):
        child = {
            "function": "ChildFn",
            "slug": "child_transition",
            "contract_sha256": "a" * 64,
            "candidate_sha256": "b" * 64,
            "contract": {
                "contract_id": "child_contract",
                "function": {"name": "ChildFn"},
            },
            "composition": {"simultaneous_child_dispatchers": []},
        }
        parent = {
            "function": "ParentFn",
            "slug": "parent_transition",
            "contract_sha256": "c" * 64,
            "candidate_sha256": "d" * 64,
            "contract": {
                "contract_id": "parent_contract",
                "function": {"name": "ParentFn"},
                "selection": {"callee_names": ["ChildFn"]},
            },
            "composition": {"simultaneous_child_dispatchers": []},
        }
        row = absorbed_rtl_dependencies([parent, child])["child_transition"][0]
        self.assertEqual(
            row["pin_origin"],
            "INTEGRATION_HASH_BINDING_OVER_FROZEN_CALLEE_EVIDENCE",
        )
        self.assertEqual(row["parent_contract_sha256"], "c" * 64)
        self.assertEqual(row["dependency_candidate_sha256"], "b" * 64)

    def test_composed_adapter_calls_selected_child_dispatcher(self):
        source = """\
extern int ChildFn(int value);
extern int ParentFn_original_parent_transition(int value);
int dsc_cicd_parent_transition_invoke(int value) {
    int oracle = ParentFn_original_parent_transition(value);
    return ChildFn(value) + oracle;
}
int ParentFn(int value) {
    return dsc_cicd_parent_transition_invoke(value);
}
"""
        routed, receipts = route_adapter_child_dispatchers(
            source,
            own_function="ParentFn",
            candidates=[
                {"function": "ParentFn", "slug": "parent_transition"},
                {"function": "ChildFn", "slug": "child_transition"},
            ],
        )
        self.assertIn(
            "extern int dsc_cicd_child_transition_invoke(int value);",
            routed,
        )
        self.assertIn(
            "return dsc_cicd_child_transition_invoke(value) + oracle;",
            routed,
        )
        self.assertIn("int ParentFn(int value)", routed)
        self.assertIn("ParentFn_original_parent_transition", routed)
        self.assertEqual(
            receipts,
            [
                {
                    "function": "ChildFn",
                    "dispatcher": "dsc_cicd_child_transition_invoke",
                    "replacements": "2",
                }
            ],
        )

    def test_private_oracle_wrapper_forces_nested_children_to_c_only(self):
        candidate = {
            "contract": {
                "function": {
                    "name": "ParentFn",
                    "return_type": "int",
                    "parameters": [
                        {"name": "value", "type": "int"},
                        {"name": "state", "type": "void *"},
                    ],
                }
            },
            "original_name": "ParentFn_original_parent_transition",
            "original_impl_name": (
                "ParentFn_original_impl_parent_transition"
            ),
        }
        wrapper = render_private_oracle_wrapper(candidate)
        self.assertIn("++dsc_cicd_multi_oracle_depth", wrapper)
        self.assertIn("--dsc_cicd_multi_oracle_depth", wrapper)
        self.assertIn(
            "ParentFn_original_impl_parent_transition(value, state)",
            wrapper,
        )
        self.assertIn("return result", wrapper)

        namespaced = namespace_adapter_text(
            "static int dsc_cicd_mode(void) {\n    return 2;\n}\n",
            slug="parent_transition",
            function_name="ParentFn",
        )
        self.assertIn(
            "if (dsc_cicd_multi_oracle_depth > 0) return 0;",
            namespaced,
        )

    @staticmethod
    def _write_json(path: pathlib.Path, value: object) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(value), encoding="utf-8")

    def test_provisional_requires_encode_rtl_return_invocation(self):
        with tempfile.TemporaryDirectory() as directory:
            root = pathlib.Path(directory)
            good = root / "rtl" / "encode-candidates" / "good"
            bad = root / "rtl" / "decode-candidates" / "bad"
            for path, name, count in ((good, "Good", 7), (bad, "Bad", 0)):
                path.mkdir(parents=True)
                self._write_json(path / "provisional-contract.json", {
                    "contract_id": name.lower(),
                    "function": {"name": name, "clang_usr": f"c:@F@{name}"},
                    "rtl": {"module": f"{name.lower()}_rtl"},
                })
                (path / "candidate_01.sv").write_text(
                    f"module {name.lower()}; endmodule\n", encoding="utf-8"
                )
                self._write_json(path / "matrix-receipt.json", {
                    "status": "PASS",
                    "encode": {"modes": {
                        "SHADOW": {"status": "PASS", "total_rtl_invocations": count},
                        "RTL_RETURN": {"status": "PASS", "total_rtl_invocations": count},
                    }},
                })
            selected, report = discover_encode_candidates(root, return_report=True)
        self.assertEqual([item["function"] for item in selected], ["Good"])
        self.assertEqual(selected[0]["module"], "good_rtl")
        self.assertEqual(report["candidate_count"], 1)
        self.assertTrue(any(
            item["function"] == "Bad"
            and "encode_rtl_return_invocations_not_positive" in item["reason"]
            for item in report["exclusions"]
        ))

    def test_stable_manifest_is_hash_checked_and_encode_reachable(self):
        with tempfile.TemporaryDirectory() as directory:
            root = pathlib.Path(directory)
            contract_dir = root / "library" / "contracts"
            rtl_dir = root / "library" / "rtl"
            contract_dir.mkdir(parents=True)
            rtl_dir.mkdir(parents=True)
            rtl = rtl_dir / "leaf.sv"
            rtl.write_text("module leaf; endmodule\n", encoding="utf-8")
            contract = {
                "contract_id": "leaf",
                "function": {"name": "Leaf", "clang_usr": "c:@F@Leaf"},
            }
            contract_path = contract_dir / "leaf.json"
            self._write_json(contract_path, contract)
            self._write_json(root / "coverage" / "coverage.json", {
                "functions": [{
                    "name": "Leaf",
                    "clang_usr": "c:@F@Leaf",
                    "coverage_status": "EXECUTED",
                }],
            })
            self._write_json(root / "facts" / "functions.json", {
                "functions": [{"name": "DSC_Encode", "callees": [{"name": "Leaf"}]},
                               {"name": "Leaf", "callees": []}],
            })
            self._write_json(root / "library" / "manifest.json", {
                "components": [{
                    "status": "PASS",
                    "contract_id": "leaf",
                    "contract_file": "contracts/leaf.json",
                    "module_file": "rtl/leaf.sv",
                    "module": "leaf",
                    "module_sha256": hashlib.sha256(rtl.read_bytes()).hexdigest(),
                }],
            })
            selected = discover_encode_candidates(root)
        self.assertEqual([item["function"] for item in selected], ["Leaf"])
        self.assertEqual(selected[0]["rtl_tier"], "STABLE_RTL")

    def test_frontier_reports_compute_gap_but_keeps_lifecycle_c_in_shell(self):
        with tempfile.TemporaryDirectory() as directory:
            root = pathlib.Path(directory)
            self._write_json(root / "facts" / "functions.json", {
                "functions": [
                    {"name": "DSC_Encode", "loop_count": 0, "effects": {},
                     "callees": [{"name": "DSC_Algorithm"}]},
                    {"name": "DSC_Algorithm", "loop_count": 2,
                     "effects": {"malloc": True},
                     "callees": [{"name": "Compute"}, {"name": "fifo_init"}]},
                    {"name": "fifo_init", "loop_count": 0,
                     "effects": {"malloc": True}, "callees": []},
                    {"name": "Compute", "loop_count": 3,
                     "effects": {"malloc": False}, "callees": []},
                ],
            })
            self._write_json(root / "coverage" / "coverage.json", {
                "functions": [
                    {"name": name, "clang_usr": f"c:@F@{name}",
                     "coverage_status": "EXECUTED"}
                    for name in ("DSC_Encode", "DSC_Algorithm", "fifo_init", "Compute")
                ],
            })
            frontier = encode_frontier(root, [])
        self.assertEqual(frontier["status"], "INCOMPLETE")
        self.assertEqual([item["function"] for item in frontier["compute_gaps"]], ["Compute"])
        self.assertEqual(
            [item["function"] for item in frontier["orchestration_boundaries"]],
            ["DSC_Algorithm", "DSC_Encode", "fifo_init"],
        )

    def test_callers_are_ordered_before_callees(self):
        ordered = source_order_encode_candidates(
            [{"function": "Leaf"}, {"function": "Parent"}, {"function": "Peer"}],
            {"functions": [
                {"name": "Parent", "callees": [{"name": "Leaf"}]},
                {"name": "Leaf", "callees": []},
                {"name": "Peer", "callees": []},
            ]},
        )
        names = [item["function"] for item in ordered]
        self.assertLess(names.index("Parent"), names.index("Leaf"))

    def test_named_metrics_and_full_frame_comparison(self):
        metrics = parse_overlay_metrics(
            "DSC_CICD_OVERLAY_METRICS candidate=parent calls=4 "
            "rtl_invocations=4 mismatches=0\n"
            "DSC_CICD_OVERLAY_METRICS candidate=leaf calls=8 "
            "rtl_invocations=8 mismatches=0\n"
        )
        self.assertEqual(metrics["candidates"]["parent"]["rtl_invocations"], 4)
        with tempfile.TemporaryDirectory() as directory:
            root = pathlib.Path(directory)
            oracle = root / "oracle.dsc"
            actual = root / "actual.dsc"
            oracle.write_bytes(b"frame\x00\xff")
            actual.write_bytes(b"frame\x00\xff")
            result = compare_dsc_frame(actual, oracle)
        self.assertEqual(result["status"], "PASS")
        self.assertTrue(result["byte_for_byte_match"])
        self.assertTrue(result["sha256_match"])

    def test_namespace_keeps_shared_mode_and_unique_symbols(self):
        source = (
            'const char *mode = getenv("DSC_CICD_MODE");\n'
            'void dsc_cicd_invoke(void);\n'
            'void Encode_original(void);\n'
            'const char *metric = "DSC_CICD_OVERLAY_METRICS calls=";\n'
            'double sc_time_stamp() { return 0.0; }\n'
        )
        namespaced = namespace_adapter_text(
            source, slug="encode_leaf", function_name="Encode"
        )
        self.assertIn('getenv("DSC_CICD_MODE")', namespaced)
        self.assertIn("dsc_cicd_encode_leaf_invoke", namespaced)
        self.assertIn("Encode_original_encode_leaf", namespaced)
        self.assertIn(
            "DSC_CICD_OVERLAY_METRICS candidate=encode_leaf calls=", namespaced
        )
        self.assertNotIn("double sc_time_stamp()", namespaced)


if __name__ == "__main__":
    unittest.main()
