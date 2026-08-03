import json
import pathlib
import subprocess
import sys
import tempfile
import unittest


ROOT = pathlib.Path(__file__).resolve().parents[1]


class AnalysisPreflightTests(unittest.TestCase):
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


if __name__ == "__main__":
    unittest.main()
