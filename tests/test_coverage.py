import pathlib
import tempfile
import unittest

from tools.run_coverage import discover_coverage_scripts, join_coverage


class CoverageDiscoveryTests(unittest.TestCase):
    def test_all_mode_discovers_profiles_without_a_name_allowlist(self):
        with tempfile.TemporaryDirectory() as directory:
            root = pathlib.Path(directory)
            smoke = root / "bittrue_smoke"
            smoke.mkdir()
            for name in (
                "run_c_baseline.sh",
                "run_c_baseline_native420.sh",
                "run_c_baseline_vbr_underflow.sh",
            ):
                (smoke / name).write_text("#!/bin/sh\n", encoding="utf-8")
            (smoke / "run_c_baseline_notes.txt").write_text("ignored\n", encoding="utf-8")

            scripts = discover_coverage_scripts(root, "all")

        self.assertEqual(
            [script.name for script in scripts],
            [
                "run_c_baseline.sh",
                "run_c_baseline_native420.sh",
                "run_c_baseline_vbr_underflow.sh",
            ],
        )

    def test_default_mode_is_the_legacy_smoke_profile(self):
        with tempfile.TemporaryDirectory() as directory:
            root = pathlib.Path(directory)
            smoke = root / "bittrue_smoke"
            smoke.mkdir()
            (smoke / "run_c_baseline.sh").write_text("#!/bin/sh\n", encoding="utf-8")
            (smoke / "run_c_baseline_native420.sh").write_text("#!/bin/sh\n", encoding="utf-8")

            scripts = discover_coverage_scripts(root, "default")

        self.assertEqual([script.name for script in scripts], ["run_c_baseline.sh"])

    def test_llvm_body_line_still_joins_to_clang_declaration(self):
        exported = {
            "data": [{
                "files": [],
                "functions": [{
                    "name": "SamplePredict",
                    "filenames": ["/tmp/dsc_codec.c"],
                    "regions": [[316, 1, 383, 2, 17]],
                    "count": 17,
                    "branches": [],
                }],
            }],
        }
        functions = {
            "functions": [{
                "clang_usr": "c:@F@SamplePredict",
                "name": "SamplePredict",
                "source_file": "dsc_codec.c",
                "line": 308,
                "end_line": 383,
            }],
        }
        candidates = {
            "functions": [{"clang_usr": "c:@F@SamplePredict", "eligible": True}],
            "ranked_candidates": [{"clang_usr": "c:@F@SamplePredict", "name": "SamplePredict", "score": 1}],
        }

        coverage = join_coverage(exported, functions, candidates, {}, [], {"path": "/missing/build.json"})

        record = coverage["functions"][0]
        self.assertEqual(record["coverage_status"], "EXECUTED")
        self.assertTrue(record["eligible_after_coverage"])
