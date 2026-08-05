import json
import pathlib
import tempfile
import unittest

from tools.encode_frontier import (
    attach_integration_receipt,
    c_orchestration_boundary,
    discover,
    render_report,
    scan_provisional,
)


def _function(
    name,
    *,
    callees=(),
    usr=None,
    source_file="codec.c",
    line=10,
    loop_count=0,
    effects=None,
    fields_write=None,
    pointer_parameters=None,
):
    return {
        "clang_usr": usr or f"c:@F@{name}",
        "name": name,
        "source_file": source_file,
        "line": line,
        "end_line": line + 2,
        "callees": [{"name": callee} for callee in callees],
        "loop_count": loop_count,
        "effects": effects or {},
        "fields_write": fields_write or [],
        "globals_write": [],
        "pointer_parameters": pointer_parameters or [],
    }


def _candidate(name, *, direct_effects=None, bounded=True):
    return {
        "clang_usr": f"c:@F@{name}",
        "name": name,
        "role": "DUT",
        "eligible": False,
        "bounded_computation": bounded,
        "direct_effects": direct_effects or {},
        "purity": "IMPURE" if direct_effects else "PURE",
        "timing": "UNKNOWN",
    }


def _coverage(*names, static=()):
    records = [
        {
            "clang_usr": f"c:@F@{name}",
            "name": name,
            "coverage_status": "EXECUTED",
            "coverage": {"execution_count": index + 1},
        }
        for index, name in enumerate(names)
    ]
    records.extend(
        {
            "clang_usr": f"c:@F@{name}",
            "name": name,
            "coverage_status": "STATIC_BUT_UNCOVERED",
            "coverage": {"execution_count": 0},
        }
        for name in static
    )
    return {
        "status": "PASS",
        "coverage_phases": "encode",
        "functions": records,
        "encode_runs": [{"status": "PASS"}],
    }


def _synthetic_inputs():
    functions = [
        _function("DSC_Encode", callees=("DSC_Algorithm",), line=1),
        _function(
            "DSC_Algorithm",
            callees=("StableLeaf", "ProvisionalLeaf", "ZeroLeaf", "VLCUnit", "InitializeDSCState", "fifo_init", "fifo_free"),
            line=20,
            loop_count=2,
            effects={"file_io": True, "malloc": True},
            fields_write=[{"record": "dsc_state_t", "name": "state", "type": "int"}],
        ),
        _function("StableLeaf", line=100),
        _function("ProvisionalLeaf", line=110, fields_write=[{"record": "dsc_state_t", "name": "value", "type": "int"}]),
        _function("ZeroLeaf", line=120, loop_count=1),
        _function(
            "VLCUnit",
            callees=("StableLeaf",),
            line=130,
            loop_count=9,
            effects={"file_io": True},
            fields_write=[{"record": "dsc_state_t", "name": "syntax", "type": "int"}],
        ),
        _function("InitializeDSCState", line=140, effects={"malloc": True}),
        _function("fifo_init", line=150, effects={"malloc": True}),
        _function("fifo_free", line=160, effects={"malloc": True}),
        _function("UnrelatedDecode", line=200),
    ]
    candidates = [
        _candidate("DSC_Encode"),
        _candidate(
            "DSC_Algorithm",
            direct_effects={"allocation": True, "io": True, "state_write": True},
            bounded=False,
        ),
        _candidate("StableLeaf"),
        _candidate("ProvisionalLeaf", direct_effects={"state_write": True}),
        _candidate("ZeroLeaf", bounded=False),
        _candidate(
            "VLCUnit",
            direct_effects={"io": True, "state_write": True},
            bounded=False,
        ),
        _candidate("InitializeDSCState", direct_effects={"allocation": True}),
        _candidate("fifo_init", direct_effects={"allocation": True}),
        _candidate("fifo_free", direct_effects={"allocation": True}),
        _candidate("UnrelatedDecode"),
    ]
    manifest = {
        "components": [{
            "function": "StableLeaf",
            "contract_id": "stable_leaf",
            "contract_file": "library/contracts/stable_leaf.json",
            "verification_file": "library/verification/stable_leaf.json",
            "status": "PASS",
        }]
    }
    return functions, candidates, manifest


class EncodeFrontierTests(unittest.TestCase):
    def test_c_shell_classifier_does_not_turn_vlcunit_fprintf_into_orchestration(self):
        self.assertEqual(
            c_orchestration_boundary(
                {"callees": [{"name": "Child"}], "loop_count": 0},
                {"direct_effects": {}},
            ),
            "THIN_CALL_WRAPPER",
        )
        self.assertEqual(
            c_orchestration_boundary(
                {"callees": [], "loop_count": 0},
                {"direct_effects": {"allocation": True}},
            ),
            "MEMORY_LIFECYCLE",
        )
        self.assertEqual(
            c_orchestration_boundary(
                {"callees": [], "loop_count": 0},
                {"direct_effects": {"io": True}},
            ),
            "FRAME_IO_ORCHESTRATION",
        )
        self.assertIsNone(
            c_orchestration_boundary(
                {
                    "callees": [{"name": "Child"}],
                    "loop_count": 9,
                    "fields_write": [{"record": "dsc_state_t", "name": "x"}],
                    "effects": {"file_io": True},
                },
                {"direct_effects": {"io": True, "state_write": True}},
            )
        )

    def test_scan_provisional_requires_positive_encode_rtl_return_invocations(self):
        with tempfile.TemporaryDirectory() as directory:
            root = pathlib.Path(directory)
            for name, invocations, encode_status in (
                ("zero", 0, "PASS"),
                ("positive", 17, "PASS"),
                ("failed_encode", 23, "FAIL"),
            ):
                candidate_dir = root / name
                candidate_dir.mkdir()
                (candidate_dir / "candidate_01.sv").write_text("module candidate; endmodule\n")
                (candidate_dir / "provisional-contract.json").write_text(
                    json.dumps({
                        "contract_id": f"{name}_contract",
                        "function": {
                            "name": f"Function_{name}",
                            "clang_usr": f"c:@F@Function_{name}",
                        },
                        "semantics": {"kind": "state_transition"},
                    }),
                    encoding="utf-8",
                )
                (candidate_dir / "verification-receipt.json").write_text(
                    json.dumps({
                        "status": "PASS",
                        "matrix_scope": "all",
                        "decode": {"rtl_return_invocations": 99, "status": "PASS"},
                        "encode": {
                            "rtl_return_invocations": invocations,
                            "status": encode_status,
                        },
                    }),
                    encoding="utf-8",
                )
            scanned = scan_provisional(root)

        self.assertEqual(set(scanned), {"Function_positive"})
        self.assertEqual(scanned["Function_positive"]["encode_rtl_return_invocations"], 17)
        self.assertEqual(scanned["Function_positive"]["encode_status"], "PASS")
        self.assertIsNotNone(scanned["Function_positive"]["verification_receipt_sha256"])

    def test_scan_supports_nested_rtl_return_mode_receipt(self):
        with tempfile.TemporaryDirectory() as directory:
            root = pathlib.Path(directory)
            candidate_dir = root / "nested"
            candidate_dir.mkdir()
            (candidate_dir / "provisional-contract.json").write_text(
                json.dumps({
                    "contract_id": "nested_contract",
                    "function": {"name": "NestedFunction"},
                    "semantics": {},
                }),
                encoding="utf-8",
            )
            (candidate_dir / "verification-receipt.json").write_text(
                json.dumps({
                    "status": "PASS",
                    "matrix_scope": "all",
                    "encode": {
                        "status": "PASS",
                        "modes": {"RTL_RETURN": {"status": "PASS", "total_rtl_invocations": 3}},
                    },
                }),
                encoding="utf-8",
            )
            scanned = scan_provisional(root)
        self.assertEqual(scanned["NestedFunction"]["encode_rtl_return_invocations"], 3)

    def test_discover_is_rooted_at_encode_and_separates_frontier_classes(self):
        functions, candidates, manifest = _synthetic_inputs()
        coverage = _coverage(
            "DSC_Encode",
            "DSC_Algorithm",
            "StableLeaf",
            "ProvisionalLeaf",
            "ZeroLeaf",
            "VLCUnit",
            "InitializeDSCState",
            "fifo_init",
            "fifo_free",
            "UnrelatedDecode",
            static=("StaticDecode",),
        )
        with tempfile.TemporaryDirectory() as directory:
            source_dir = pathlib.Path(directory)
            (source_dir / "codec.c").write_text("int source_marker;\n", encoding="utf-8")
            frontier = discover(
                coverage,
                {"functions": functions},
                {"functions": candidates},
                manifest,
                source_dir,
                {
                    "ProvisionalLeaf": {
                        "contract_id": "provisional_leaf",
                        "encode_status": "PASS",
                        "encode_rtl_return_invocations": 7,
                        "verification_receipt": "/receipts/provisional.json",
                    }
                },
                traceability={"inputs": {"facts": source_dir / "facts.json"}},
            )

        names = {item["name"] for item in frontier["reached"]}
        self.assertNotIn("UnrelatedDecode", names)
        self.assertNotIn("StaticDecode", names)
        self.assertEqual(frontier["summary"]["reached"], 9)
        self.assertEqual(frontier["summary"]["rtl"], 2)
        self.assertEqual(frontier["summary"]["stable_rtl"], 1)
        self.assertEqual(frontier["summary"]["provisional_rtl"], 1)
        self.assertEqual(frontier["summary"]["c_shell"], 5)
        self.assertEqual(frontier["summary"]["compute_gap"], 2)
        self.assertEqual(
            {item["name"] for item in frontier["c_shell"]},
            {"DSC_Encode", "DSC_Algorithm", "InitializeDSCState", "fifo_init", "fifo_free"},
        )
        self.assertIn("VLCUnit", {item["name"] for item in frontier["compute_gap"]})
        vlc = next(item for item in frontier["reached"] if item["name"] == "VLCUnit")
        self.assertEqual(vlc["rtl_status"], "COMPUTE_GAP")
        self.assertNotEqual(vlc["c_boundary_class"], "FRAME_IO_ORCHESTRATION")
        self.assertEqual(frontier["traceability"]["root_function"], "DSC_Encode")
        self.assertTrue(frontier["traceability"]["inputs"]["facts"]["path"].endswith("facts.json"))

    def test_zero_encode_invocation_is_compute_gap_even_if_receipt_is_pass(self):
        functions, candidates, manifest = _synthetic_inputs()
        coverage = _coverage("DSC_Encode", "DSC_Algorithm", "ProvisionalLeaf")
        with tempfile.TemporaryDirectory() as directory:
            frontier = discover(
                coverage,
                {"functions": functions},
                {"functions": candidates},
                manifest,
                pathlib.Path(directory),
                {
                    "ProvisionalLeaf": {
                        "contract_id": "decode_only_contract",
                        "encode_status": "PASS",
                        "encode_rtl_return_invocations": 0,
                    }
                },
            )
        row = next(item for item in frontier["reached"] if item["name"] == "ProvisionalLeaf")
        self.assertEqual(row["rtl_status"], "COMPUTE_GAP")
        self.assertEqual(frontier["summary"]["provisional_rtl"], 0)

    def test_positive_encode_receipt_is_retained_in_row_traceability(self):
        functions, candidates, manifest = _synthetic_inputs()
        coverage = _coverage("DSC_Encode", "DSC_Algorithm", "ProvisionalLeaf")
        with tempfile.TemporaryDirectory() as directory:
            source_dir = pathlib.Path(directory)
            source = source_dir / "codec.c"
            source.write_text("int source_marker;\n", encoding="utf-8")
            frontier = discover(
                coverage,
                {"functions": functions},
                {"functions": candidates},
                manifest,
                source_dir,
                {
                    "ProvisionalLeaf": {
                        "contract_id": "encode_contract",
                        "encode_status": "PASS",
                        "encode_rtl_return_invocations": 11,
                        "verification_receipt": "/receipts/encode.json",
                        "verification_receipt_sha256": "receipt-hash",
                        "contract_file": "/receipts/provisional-contract.json",
                        "contract_sha256": "contract-hash",
                    }
                },
            )
        row = next(item for item in frontier["reached"] if item["name"] == "ProvisionalLeaf")
        self.assertEqual(row["rtl_status"], "PROVISIONAL_RTL_PASS")
        self.assertEqual(
            row["traceability"]["receipt"]["encode_rtl_return_invocations"],
            11,
        )
        self.assertEqual(row["traceability"]["receipt"]["verification_receipt_sha256"], "receipt-hash")
        self.assertEqual(row["traceability"]["source"]["sha256"], __import__("hashlib").sha256(b"int source_marker;\n").hexdigest())

    def test_attach_integration_receipt_reads_encode_phase(self):
        with tempfile.TemporaryDirectory() as directory:
            path = pathlib.Path(directory) / "matrix.json"
            path.write_text(json.dumps({
                "status": "PASS",
                "encode": {
                    "status": "PASS",
                    "matrix_scope": "all",
                    "profiles": 22,
                    "candidate_count": 27,
                    "modes": {
                        "C_ONLY": {"status": "PASS", "total_rtl_invocations": 0},
                        "SHADOW": {"status": "PASS", "total_rtl_invocations": 4},
                        "RTL_RETURN": {"status": "PASS", "total_rtl_invocations": 4},
                    },
                },
            }), encoding="utf-8")
            frontier = {"traceability": {}}
            attach_integration_receipt(frontier, path)
        self.assertEqual(frontier["multi_rtl_integration"]["phase"], "encode")
        self.assertEqual(frontier["multi_rtl_integration"]["candidate_count"], 27)
        self.assertEqual(
            frontier["multi_rtl_integration"]["modes"]["RTL_RETURN"]["total_rtl_invocations"],
            4,
        )
        self.assertIsNotNone(frontier["traceability"]["integration_receipt"]["sha256"])

    def test_report_has_reached_rtl_c_shell_and_compute_gap_sections(self):
        functions, candidates, manifest = _synthetic_inputs()
        frontier = discover(
            _coverage("DSC_Encode", "DSC_Algorithm", "StableLeaf"),
            {"functions": functions},
            {"functions": candidates},
            manifest,
            pathlib.Path("/tmp/nonexistent-source"),
        )
        report = render_report(frontier)
        self.assertIn("# Encode RTL frontier", report)
        self.assertIn("## Reached Encode functions", report)
        self.assertIn("## RTL reached", report)
        self.assertIn("## C shells", report)
        self.assertIn("## Compute gaps", report)
        self.assertIn("DSC_Encode", report)

    @unittest.skipUnless(
        pathlib.Path(__file__).resolve().parents[1].joinpath(
            "coverage/coverage.json"
        ).is_file()
        and pathlib.Path(__file__).resolve().parents[1].joinpath(
            "facts/functions.json"
        ).is_file()
        and pathlib.Path(__file__).resolve().parents[1].joinpath(
            "rtl/decode-candidates"
        ).is_dir(),
        "generated Encode frontier inputs are not present",
    )
    def test_repository_encode_frontier_has_phase_aware_counts(self):
        repo_root = pathlib.Path(__file__).resolve().parents[1]
        frontier = discover(
            json.loads((repo_root / "coverage/coverage.json").read_text()),
            json.loads((repo_root / "facts/functions.json").read_text()),
            json.loads((repo_root / "facts/candidates.json").read_text()),
            json.loads((repo_root / "library/manifest.json").read_text()),
            repo_root,
            scan_provisional(repo_root / "rtl/decode-candidates"),
            traceability={
                "repo_root": repo_root,
                "inputs": {
                    "coverage": repo_root / "coverage/coverage.json",
                    "functions": repo_root / "facts/functions.json",
                    "candidates": repo_root / "facts/candidates.json",
                    "manifest": repo_root / "library/manifest.json",
                },
            },
        )
        self.assertEqual(frontier["summary"]["reached"], 44)
        self.assertEqual(frontier["summary"]["encode_profiles"], 22)
        self.assertEqual(frontier["summary"]["encode_profiles_passed"], 22)
        self.assertEqual(frontier["summary"]["rtl"], 27)
        self.assertEqual(frontier["summary"]["c_shell"], 5)
        self.assertEqual(frontier["summary"]["compute_gap"], 12)
        self.assertNotIn("DSC_Decode", {item["name"] for item in frontier["reached"]})
        self.assertIn("VLCUnit", {item["name"] for item in frontier["compute_gap"]})
        self.assertNotIn("VLCUnit", {item["name"] for item in frontier["c_shell"]})
        self.assertNotIn(
            "PredictionLoop",
            {item["name"] for item in frontier["rtl"]},
        )
        self.assertNotIn(
            "RateControl",
            {item["name"] for item in frontier["rtl"]},
        )


if __name__ == "__main__":
    unittest.main()
