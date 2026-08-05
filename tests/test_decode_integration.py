import json
import pathlib
import tempfile
import unittest

from tools.verify_decode_integration import (
    discover_decode_candidates,
    namespace_adapter_text,
    source_order_candidates,
)


class DecodeIntegrationTests(unittest.TestCase):
    def test_discovery_uses_executed_decode_receipts(self):
        with tempfile.TemporaryDirectory() as directory:
            root = pathlib.Path(directory)
            artifact = root / "rtl" / "decode-candidates" / "candidate"
            artifact.mkdir(parents=True)
            contract = {
                "contract_id": "foo_transition",
                "function": {"name": "Foo", "clang_usr": "c:@F@Foo"},
            }
            (artifact / "provisional-contract.json").write_text(json.dumps(contract))
            (artifact / "candidate_01.sv").write_text("module foo_transition; endmodule\n")
            receipt = {
                "status": "PASS",
                "decode": {"modes": {
                    "SHADOW": {"status": "PASS", "total_rtl_invocations": 3},
                    "RTL_RETURN": {"status": "PASS", "total_rtl_invocations": 3},
                }},
            }
            (artifact / "matrix-receipt.json").write_text(json.dumps(receipt))
            selected = discover_decode_candidates(root)
        self.assertEqual([item["function"] for item in selected], ["Foo"])

    def test_discovery_includes_hash_checked_stable_decode_rtl(self):
        with tempfile.TemporaryDirectory() as directory:
            root = pathlib.Path(directory)
            (root / "coverage" / "decode").mkdir(parents=True)
            (root / "library" / "contracts").mkdir(parents=True)
            (root / "library" / "rtl").mkdir()
            (root / "library" / "verification").mkdir()
            contract = {
                "contract_id": "stable_leaf",
                "function": {"name": "StableLeaf", "clang_usr": "c:@F@StableLeaf"},
            }
            contract_path = root / "library" / "contracts" / "stable_leaf.json"
            rtl_path = root / "library" / "rtl" / "stable_leaf.sv"
            verification_path = root / "library" / "verification" / "stable_leaf.json"
            contract_path.write_text(json.dumps(contract))
            rtl_path.write_text("module stable_leaf; endmodule\n")
            verification_path.write_text(json.dumps({"status": "PASS"}))
            import hashlib
            rtl_hash = hashlib.sha256(rtl_path.read_bytes()).hexdigest()
            (root / "coverage" / "decode" / "coverage.json").write_text(json.dumps({
                "functions": [{
                    "clang_usr": "c:@F@StableLeaf",
                    "coverage_status": "EXECUTED",
                }],
            }))
            (root / "library" / "manifest.json").write_text(json.dumps({
                "components": [{
                    "status": "PASS",
                    "contract_id": "stable_leaf",
                    "contract_file": "contracts/stable_leaf.json",
                    "module_file": "rtl/stable_leaf.sv",
                    "verification_file": "verification/stable_leaf.json",
                    "module": "stable_leaf",
                    "module_sha256": rtl_hash,
                }],
            }))
            selected = discover_decode_candidates(root)
        self.assertEqual([item["function"] for item in selected], ["StableLeaf"])
        self.assertEqual(selected[0]["rtl_tier"], "STABLE_RTL")

    def test_namespace_preserves_shared_mode_and_tags_metrics(self):
        source = (
            '#define DSC_CICD_FIFO_BYTES 8\n'
            'const char *mode = getenv("DSC_CICD_MODE");\n'
            'void dsc_cicd_invoke(void);\n'
            'void Foo_original(void);\n'
            'const char *metric = "DSC_CICD_OVERLAY_METRICS calls=";\n'
            'double sc_time_stamp() { return 0.0; }\n'
        )
        namespaced = namespace_adapter_text(
            source, slug="foo_transition", function_name="Foo"
        )
        self.assertIn("DSC_CICD_FOO_TRANSITION_FIFO_BYTES", namespaced)
        self.assertIn('getenv("DSC_CICD_MODE")', namespaced)
        self.assertIn("dsc_cicd_foo_transition_invoke", namespaced)
        self.assertIn("Foo_original_foo_transition", namespaced)
        self.assertIn(
            "DSC_CICD_OVERLAY_METRICS candidate=foo_transition calls=",
            namespaced,
        )
        self.assertNotIn("double sc_time_stamp()", namespaced)

    def test_selected_callers_are_rewritten_before_selected_callees(self):
        candidates = [
            {"function": "Leaf"},
            {"function": "Parent"},
            {"function": "Peer"},
        ]
        facts = {"functions": [
            {"name": "Parent", "callees": [{"name": "Leaf"}]},
            {"name": "Leaf", "callees": []},
            {"name": "Peer", "callees": []},
        ]}
        ordered = source_order_candidates(candidates, facts)
        names = [item["function"] for item in ordered]
        self.assertLess(names.index("Parent"), names.index("Leaf"))


if __name__ == "__main__":
    unittest.main()
