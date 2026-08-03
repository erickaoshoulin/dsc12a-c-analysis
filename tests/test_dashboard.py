#!/usr/bin/env python3
import json
import tempfile
import unittest
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "tools"))
import dashboard


class DashboardFixtureTests(unittest.TestCase):
    def make_fixture(self, *, failed=False, pdf_available=True):
        temp = tempfile.TemporaryDirectory()
        root = Path(temp.name)
        repo = root / "repo"
        regression = root / "regression"
        source = root / "external-source"
        source.mkdir(parents=True)
        for directory in (
            repo / "spec",
            repo / "library" / "contracts",
            repo / "library" / "verification",
            repo / "library" / "rtl",
            repo / "artifacts" / "fixture-hash",
            regression / "runs" / "fixture-run" / "functions" / "fixture_leaf",
        ):
            directory.mkdir(parents=True)
        pdf = root / "missing-spec.pdf"
        if pdf_available:
            pdf.write_bytes(b"fixture pdf")
        contract = {
            "schema_version": 1,
            "contract_id": "fixture_leaf",
            "function": {
                "name": "FixtureLeaf",
                "source_file": "fixture.c",
                "source_span": {"start_line": 10, "end_line": 20},
                "permalink": "https://github.com/example/repo/blob/0123456789abcdef0123456789abcdef01234567/fixture.c#L10-L20",
            },
            "interface": {
                "ports": [
                    {
                        "name": "input_value",
                        "direction": "input",
                        "width": 8,
                        "signed": False,
                        "role": "RUNTIME_INPUT",
                        "legal_domain": {
                            "kind": "range",
                            "range": [0, 255],
                            "basis": "8-bit fixture input",
                        },
                    },
                    {
                        "name": "return_value",
                        "direction": "output",
                        "width": 9,
                        "signed": False,
                        "role": "return_value",
                        "legal_domain": {
                            "kind": "range",
                            "range": [0, 256],
                            "basis": "derived output range",
                        },
                    },
                ],
                "inputs": [
                    {
                        "name": "input_value",
                        "logical_width": 8,
                        "width_source": "EXACT_SPEC",
                        "legal_domain": {"range": [0, 255], "basis": "8-bit fixture input"},
                    }
                ],
                "output": {
                    "name": "return_value",
                    "logical_width": 9,
                    "range_formula": "(input_value + 1)",
                    "width_source": "DERIVED_SPEC_DOMAIN",
                },
            },
            "spec_links": [
                {
                    "anchor_id": "pdf:table:fixture-1",
                    "page": 7,
                    "section": "fixture",
                    "status": "EXACT",
                }
            ],
            "lock": {"contract_sha256": "fixture-hash"},
        }
        dashboard.write_json(repo / "library" / "contracts" / "fixture_leaf.json", contract)
        (repo / "library" / "rtl" / "fixture_leaf.sv").write_text(
            "module fixture_leaf; endmodule\n", encoding="utf-8"
        )
        dashboard.write_json(repo / "library" / "verification" / "fixture_leaf.json", {
            "status": "PASS",
            "contract_id": "fixture_leaf",
            "candidate_pass_rate": "1/2",
            "frame_pass_rate": "2/2",
        })
        (repo / "artifacts" / "fixture-hash" / "mutations.json").write_text(
            '{"mutations":[{"id":"boundary"}]}\n', encoding="utf-8"
        )
        dashboard.write_json(repo / "library" / "manifest.json", {
            "schema_version": 2,
            "library": "fixture-library",
            "source_hash": "source-hash",
            "spec_hash": "spec-hash",
            "components": [{
                "contract_id": "fixture_leaf",
                "function": "FixtureLeaf",
                "contract_hash": "fixture-hash",
                "artifact_dir": "artifacts/fixture-hash",
                "module": "fixture_leaf",
                "module_file": "rtl/fixture_leaf.sv",
                "module_sha256": "rtl-hash",
                "verification_file": "verification/fixture_leaf.json",
                "status": "PASS",
                "promoted_at": "2026-01-01T00:00:00Z",
                "last_verified_run_id": "fixture-run",
            }],
        })
        dashboard.write_json(repo / "spec" / "manifest.json", {
            "status": "OK",
            "spec": {
                "path": str(pdf),
                "sha256": "spec-hash",
                "status": "OK",
            },
            "source": {
                "status": "PASS",
                "source_dir": str(source),
                "source_hashes_sha256": "source-hash",
            },
        })
        receipt_status = "FAIL" if failed else "PASS"
        stage_status = "FAIL" if failed else "PASS"
        receipt = {
            "schema_version": 1,
            "contract_id": "fixture_leaf",
            "function": "FixtureLeaf",
            "status": receipt_status,
            "contract_hash": "fixture-hash",
            "candidate_pass_rate": "1/2",
            "frame_pass_rate": "2/2",
            "blockers": ["fixture stage failed"] if failed else [],
            "source_gate": {
                "status": "PASS",
                "pdf": {"path": str(pdf), "sha256": "spec-hash"},
                "source": {"sha256": "source-hash"},
            },
            "traceability": {
                "authority": "EXACT_SPEC",
                "review_status": "REVIEWED",
                "source_root": str(source),
                "source_file": "fixture.c",
                "c_span": {"start_line": 10, "end_line": 20},
                "spec_pdf": str(pdf),
                "spec_links": [{
                    "anchor_id": "pdf:table:fixture-1",
                    "page": 7,
                    "section": "fixture",
                    "status": "EXACT",
                }],
                "ports": contract["interface"]["ports"],
            },
            "stages": {
                "width_spec_gate": {"status": "PASS"},
                "generator_cache": {
                    "status": stage_status,
                    "execution_status": "EXECUTED_NOW",
                    "candidates": [
                        {
                            "candidate": "candidate_01",
                            "accepted": not failed,
                            "compile_status": "PASS",
                            "validation": "PASS",
                            "verification_status": "EXHAUSTIVE_EQUIVALENT",
                            "vectors_executed": 256,
                            "smallest_counterexample": None,
                        },
                        {
                            "candidate": "candidate_02",
                            "accepted": False,
                            "compile_status": "PASS",
                            "validation": "PASS",
                            "verification_status": "COUNTEREXAMPLE",
                            "vectors_executed": 0,
                            "smallest_counterexample": {
                                "expected": "1",
                                "actual": "2",
                                "inputs": [255],
                                "index": 0,
                            },
                        },
                    ],
                    "route": {"tier": "cheap", "model_env": "FIXTURE_MODEL"},
                },
                "verilator_lint_build": {"status": stage_status},
                "shards_mutations": {
                    "status": stage_status,
                    "vectors": 256,
                    "verification_status": "EXHAUSTIVE_EQUIVALENT",
                    "shards": [{"shard_id": 0, "vectors": 256}],
                    "candidates": [],
                },
                "model_matrix": {
                    "status": stage_status,
                    "authority_modes": {
                        "C_ONLY": "PASS",
                        "SHADOW": "PASS",
                        "RTL_RETURN": "PASS",
                    },
                },
                "frame_compare": {
                    "status": stage_status,
                    "frames": [
                        {"name": "fixture", "status": stage_status},
                        {"name": "fixture-alt", "status": stage_status},
                    ],
                },
            },
        }
        if failed:
            receipt["stages"]["shards_mutations"]["counterexample"] = {
                "expected": "1",
                "actual": "2",
                "inputs": [255],
                "index": 0,
            }
        dashboard.write_json(
            regression / "runs" / "fixture-run" / "run.json",
            {
                "run_id": "fixture-run",
                "profile": "fixture",
                "status": "FAILED" if failed else "COMPLETED",
                "created_at": "2026-01-01T00:00:00Z",
                "updated_at": "2026-01-01T00:00:00Z",
                "source_hash": "source-hash",
                "spec_hash": "spec-hash",
            },
        )
        dashboard.write_json(
            regression / "runs" / "fixture-run" / "functions" / "fixture_leaf" / "receipt.json",
            receipt,
        )
        return temp, repo, regression, pdf

    def test_accepted_fixture_has_traceability_and_width_derivation(self):
        temp, repo, regression, _ = self.make_fixture()
        self.addCleanup(temp.cleanup)
        site = repo / "dashboard"
        dataset, _ = dashboard.build(repo, str(regression), "latest", output=site, mirror_external=False)
        self.assertEqual(dataset.functions[0]["status"], "PASS")
        model = dashboard.read_json(site / "data" / "functions" / "fixture_leaf.json")
        self.assertEqual(model["traceability"]["spec"]["status"], "AVAILABLE")
        self.assertEqual(model["traceability"]["ports"][1]["width"], 9)
        self.assertEqual(
            model["traceability"]["ports"][1]["width_derivation"]["formula"],
            "(input_value + 1)",
        )
        self.assertEqual(
            [item["status"] for item in model["matrix"]["modes"].values()],
            ["PASS", "PASS", "PASS", "PASS"],
        )
        ok, errors = dashboard.check_site(repo, site)
        self.assertTrue(ok, errors)

    def test_failed_fixture_is_red_with_cause_and_counterexample(self):
        temp, repo, regression, _ = self.make_fixture(failed=True)
        self.addCleanup(temp.cleanup)
        site = repo / "dashboard"
        dataset, _ = dashboard.build(repo, str(regression), "latest", output=site, mirror_external=False)
        model = dashboard.read_json(site / "data" / "functions" / "fixture_leaf.json")
        self.assertEqual(model["status"], "FAIL")
        self.assertIn("fixture stage failed", model["blockers"])
        self.assertEqual(model["mutations"]["smallest_counterexample"]["expected"], "1")
        report = (repo / "reports" / "functions" / "fixture_leaf.md").read_text()
        self.assertIn("FAIL", report)
        self.assertIn("expected", report)
        self.assertIn("actual", report)
        self.assertIn("Next action", report)
        self.assertIn("FAIL", (site / "functions" / "fixture_leaf.html").read_text())

    def test_missing_pdf_and_smb_fallback_are_visible(self):
        temp, repo, regression, _ = self.make_fixture(pdf_available=False)
        self.addCleanup(temp.cleanup)
        missing = regression.parent / "not-mounted"
        resolution = dashboard.resolve_storage(repo, str(missing))
        self.assertTrue(resolution.fallback)
        self.assertIn("does not exist", resolution.fallback_reason)
        site = repo / "dashboard"
        dataset, _ = dashboard.build(repo, str(missing), "latest", output=site, mirror_external=False)
        self.assertEqual(dataset.overview["storage"]["mode"], "LOCAL_REPOSITORY")
        self.assertTrue(dataset.overview["storage"]["fallback"])
        self.assertEqual(dataset.functions[0]["traceability"]["spec"]["status"], "SPEC_UNAVAILABLE")
        summary = (repo / "reports" / "regression-summary.md").read_text()
        self.assertIn("SPEC_UNAVAILABLE", summary)
        self.assertIn("SMB fallback", summary)

    def test_rebuild_is_deterministic_and_links_resolve(self):
        temp, repo, regression, _ = self.make_fixture()
        self.addCleanup(temp.cleanup)
        site = repo / "dashboard"
        dashboard.build(repo, str(regression), "latest", output=site, mirror_external=False)
        tracked = [
            site / "index.html",
            site / "history.html",
            site / "traceability.html",
            site / "data" / "functions" / "fixture_leaf.json",
            repo / "reports" / "regression-summary.md",
            repo / "reports" / "functions" / "fixture_leaf.md",
            repo / "library" / "index.json",
            repo / "path-map.json",
            repo / "DIRECTORY_LAYOUT.md",
        ]
        first = {str(path.relative_to(repo)): path.read_bytes() for path in tracked}
        dashboard.build(repo, str(regression), "latest", output=site, mirror_external=False)
        second = {str(path.relative_to(repo)): path.read_bytes() for path in tracked}
        self.assertEqual(first, second)
        ok, errors = dashboard.check_site(repo, site)
        self.assertTrue(ok, errors)
        self.assertNotIn("receipt.json", (repo / "reports" / "regression-summary.md").read_text())


if __name__ == "__main__":
    unittest.main()
