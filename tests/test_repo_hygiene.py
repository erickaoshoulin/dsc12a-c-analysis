import json
import os
import subprocess
import tempfile
import unittest
from pathlib import Path
from unittest import mock

from tools import repo_hygiene
from tools.cicd_agent import Agent


class RepositoryHygieneTests(unittest.TestCase):
    def test_generated_and_transient_paths_are_rejected(self):
        findings = repo_hygiene.scan_paths(
            [
                "artifacts/hash/generated/candidate_01.sv",
                "artifacts/hash/candidate-build/candidate_01/harness.cpp",
                "artifacts/hash/oracle.c",
                "build/make-build.log",
                "sim/obj_dir/Vcandidate.cpp",
                "tests/vectors/fixture.txt",
                "artifacts/hash/unit-receipt.json",
                "library/rtl/leaf.sv",
            ]
        )
        self.assertEqual(
            [(item["path"], item["rule"]) for item in findings],
            [
                ("artifacts/hash/candidate-build/candidate_01/harness.cpp", "generated_candidate_material"),
                ("artifacts/hash/generated/candidate_01.sv", "generated_candidate_material"),
                ("artifacts/hash/oracle.c", "generated_candidate_material"),
                ("build/make-build.log", "transient_log_or_waveform"),
                ("sim/obj_dir/Vcandidate.cpp", "obj_dir"),
                ("tests/vectors/fixture.txt", "vectors"),
            ],
        )

    def test_check_repo_reads_only_tracked_paths(self):
        with tempfile.TemporaryDirectory() as directory:
            repo = Path(directory)
            subprocess.run(["git", "init", "-q", str(repo)], check=True)
            (repo / "build").mkdir()
            (repo / "build" / "make-build.log").write_text("verbose\n", encoding="utf-8")
            (repo / "README.md").write_text("compact\n", encoding="utf-8")
            subprocess.run(["git", "-C", str(repo), "add", "build/make-build.log", "README.md"], check=True)
            result = repo_hygiene.check_repo(repo)
            self.assertEqual(result["status"], "FAIL")
            self.assertEqual(result["forbidden_count"], 1)
            self.assertEqual(result["forbidden"][0]["path"], "build/make-build.log")

            (repo / "build" / "make-build.log").unlink()
            subprocess.run(["git", "-C", str(repo), "rm", "-q", "build/make-build.log"], check=True)
            clean = repo_hygiene.check_repo(repo)
            self.assertEqual(clean["status"], "PASS")
            self.assertEqual(json.loads(json.dumps(clean))["forbidden"], [])

    def test_external_artifact_root_uses_logical_checkout_reference(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory) / "repo"
            external = (Path(directory) / "durable" / "artifacts").resolve()
            root.mkdir()
            with mock.patch.dict(os.environ, {"DSC_CICD_ARTIFACT_ROOT": str(external)}, clear=False):
                agent = Agent(root, "test")
                artifact = agent.artifact_dir({"contract_hash": "fixture-hash"})
                self.assertEqual(artifact, external / "fixture-hash")
                self.assertTrue(agent.external_artifacts)
                self.assertEqual(agent.artifact_reference(artifact), "artifacts/fixture-hash")
                self.assertEqual(
                    agent.resolve_artifact_reference("artifacts/fixture-hash"),
                    external / "fixture-hash",
                )


if __name__ == "__main__":
    unittest.main()
