import json
import pathlib
import subprocess
import sys
import tempfile
import unittest
from unittest import mock

from tools import analysis_preflight


ROOT = pathlib.Path(__file__).resolve().parents[1]


class AnalysisPreflightTests(unittest.TestCase):
    def test_homebrew_fallback_is_used_for_bare_llvm_tool(self):
        with tempfile.TemporaryDirectory() as directory:
            candidate = pathlib.Path(directory) / "llvm-config"
            candidate.write_text("#!/bin/sh\nprintf 'test llvm\\n'\n", encoding="utf-8")
            candidate.chmod(0o755)
            with mock.patch.dict(
                analysis_preflight.HOMEBREW_TOOL_PATHS,
                {"llvm-config": (str(candidate),)},
                clear=True,
            ):
                resolved, resolution = analysis_preflight.resolve_executable("llvm-config", "llvm-config")
        self.assertEqual(resolved, str(candidate.resolve()))
        self.assertEqual(resolution, "homebrew")

    def test_missing_tool_is_recorded_before_analysis(self):
        with tempfile.TemporaryDirectory() as directory:
            output = pathlib.Path(directory) / "analysis-preflight.json"
            command = [
                sys.executable,
                str(ROOT / "tools" / "analysis_preflight.py"),
                "--output", str(output),
                "--python", sys.executable,
                "--clang", sys.executable,
                "--clang++", sys.executable,
                "--frama-c", str(pathlib.Path(directory) / "missing-frama-c"),
                "--llvm-config", sys.executable,
                "--cmake", sys.executable,
            ]
            result = subprocess.run(command, cwd=ROOT, text=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, check=False)
            self.assertEqual(result.returncode, 1)
            receipt = json.loads(output.read_text(encoding="utf-8"))
        self.assertEqual(receipt["status"], "INFRASTRUCTURE_FAILURE")
        self.assertEqual(receipt["missing_tools"], ["frama-c"])
        self.assertEqual(receipt["tools"]["python"]["status"], "PASS")

    def test_all_executables_pass_without_function_selection_inputs(self):
        with tempfile.TemporaryDirectory() as directory:
            output = pathlib.Path(directory) / "analysis-preflight.json"
            command = [
                sys.executable,
                str(ROOT / "tools" / "analysis_preflight.py"),
                "--output", str(output),
                *sum(([f"--{name}", sys.executable] for name in ("python", "clang", "clang++", "frama-c", "llvm-config", "cmake")), []),
            ]
            result = subprocess.run(command, cwd=ROOT, text=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, check=False)
            self.assertEqual(result.returncode, 0)
            receipt = json.loads(output.read_text(encoding="utf-8"))
        self.assertEqual(receipt["status"], "PASS")
        self.assertEqual(receipt["missing_tools"], [])
        self.assertEqual(receipt["tools"]["llvm-config"]["resolution"], "configured")


if __name__ == "__main__":
    unittest.main()
