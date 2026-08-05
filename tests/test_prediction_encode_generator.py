"""Unit tests for the generator/RTL half of encoder PredictionLoop.

The tests never write into the worktree's generated-artifact directories.  Any
rendered RTL is placed in a temporary directory and linted there.
"""

from __future__ import annotations

import copy
import json
import pathlib
import shutil
import subprocess
import tempfile
import unittest

from tools.generate_prediction_encode import (
    REQUIRED_DEPENDENCY_ROLES,
    build_prediction_encode_contract,
    discover_prediction_encode_candidates,
    load_pinned_dependencies,
    render_prediction_encode_rtl,
)


ROOT = pathlib.Path(__file__).resolve().parents[1]
SOURCE = pathlib.Path(
    "/Users/snow/Desktop/Display Stream Compression (DSC)/DSC 1.2a/"
    "DSC_model_20210623/source"
)


def _load_facts() -> tuple[dict, dict, dict]:
    return (
        json.loads((ROOT / "facts/functions.json").read_text(encoding="utf-8")),
        json.loads((ROOT / "facts/candidates.json").read_text(encoding="utf-8")),
        json.loads((ROOT / "coverage/coverage.json").read_text(encoding="utf-8")),
    )


class PredictionEncodeGeneratorTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        if not SOURCE.is_dir():
            raise unittest.SkipTest(f"immutable DSC source is unavailable: {SOURCE}")
        cls.dependencies = load_pinned_dependencies(ROOT)
        cls.functions, cls.candidates, cls.coverage = _load_facts()

    def test_all_six_dependencies_are_semantically_pinned(self) -> None:
        roles = {record["role"] for record in self.dependencies.values()}
        self.assertEqual(roles, REQUIRED_DEPENDENCY_ROLES)
        for role in sorted(REQUIRED_DEPENDENCY_ROLES):
            record = self.dependencies[role]
            self.assertTrue(record["contract_sha256"])
            self.assertTrue(record["module_sha256"])
            self.assertEqual(record["contract"]["status"], "LOCKED")

    def test_discovery_uses_structure_and_encode_coverage_not_target_name(self) -> None:
        functions = copy.deepcopy(self.functions)
        candidates = copy.deepcopy(self.candidates)
        coverage = copy.deepcopy(self.coverage)
        target_usr = "c:@F@PredictionLoop"
        for document in (functions, candidates, coverage):
            for row in document["functions"]:
                if row.get("clang_usr") == target_usr:
                    row["name"] = "RenamedEncoderStateKernel"
        matches = discover_prediction_encode_candidates(
            functions, candidates, coverage, SOURCE, self.dependencies
        )
        self.assertEqual(len(matches), 1)
        self.assertEqual(matches[0]["name"], "RenamedEncoderStateKernel")
        self.assertEqual(
            {record["role"] for record in matches[0]["dependencies"].values()},
            REQUIRED_DEPENDENCY_ROLES,
        )
        self.assertTrue(any("function name" in evidence for evidence in matches[0]["selection_basis"]))

    def test_uncovered_structural_candidate_is_rejected(self) -> None:
        functions, candidates, coverage = _load_facts()
        for row in coverage["functions"]:
            if row.get("clang_usr") == "c:@F@PredictionLoop":
                row["coverage"]["covered"] = False
        self.assertEqual(
            discover_prediction_encode_candidates(
                functions, candidates, coverage, SOURCE, self.dependencies
            ),
            [],
        )

    def test_contract_is_complete_and_midpoint_loop_is_finite(self) -> None:
        matches = discover_prediction_encode_candidates(
            self.functions, self.candidates, self.coverage, SOURCE, self.dependencies
        )
        contract = build_prediction_encode_contract(matches[0], SOURCE, self.dependencies)
        semantics = contract["semantics"]
        self.assertEqual(semantics["specialization"], "isEncoder == 1")
        self.assertEqual(semantics["constants"]["max_units"], 4)
        self.assertTrue(semantics["midpoint_clamp"]["finite"])
        self.assertEqual(semantics["midpoint_clamp"]["formulation"], "exact_threshold_interval_projection")
        self.assertEqual(len(contract["dependencies"]), 6)
        output_names = {
            port["name"]
            for port in contract["interface"]["ports"]
            if port["direction"] == "output"
        }
        for name in (
            "state_primary_qp_out",
            "domain_valid",
            "illegal_domain",
            "bound_violation",
            "midpoint_clamp_violation",
            "arithmetic_domain_violation",
        ):
            self.assertIn(name, output_names)
        for unit in range(4):
            self.assertIn(f"state_max_error_{unit}_out", output_names)
            self.assertIn(f"state_max_mid_error_{unit}_out", output_names)
            self.assertIn(f"curr_line_write_{unit}_enable", output_names)
            for sample in range(3):
                self.assertIn(f"state_quantized_residual_{unit}_{sample}_out", output_names)
                self.assertIn(f"state_quantized_residual_mid_{unit}_{sample}_out", output_names)
        rtl = render_prediction_encode_rtl(contract)
        self.assertNotIn("while (", rtl)
        self.assertIn("dsc_project_midpoint_i", rtl)
        self.assertIn("dsc_find_residual_size_i", rtl)
        self.assertIn("dsc_max_residual_size_i", rtl)
        self.assertIn("state_primary_qp_out = qp", rtl)
        self.assertIn("curr_line_write_3_value", rtl)

    def test_render_rejects_changed_dependency_bytes(self) -> None:
        matches = discover_prediction_encode_candidates(
            self.functions, self.candidates, self.coverage, SOURCE, self.dependencies
        )
        contract = build_prediction_encode_contract(matches[0], SOURCE, self.dependencies)
        tampered = copy.deepcopy(contract)
        tampered["dependencies"][0]["module_sha256"] = "0" * 64
        with self.assertRaisesRegex(RuntimeError, "pinned dependency changed"):
            render_prediction_encode_rtl(tampered)

    def test_rendered_rtl_passes_verilator_lint(self) -> None:
        verilator = shutil.which("verilator")
        if not verilator:
            self.skipTest("verilator is not installed")
        matches = discover_prediction_encode_candidates(
            self.functions, self.candidates, self.coverage, SOURCE, self.dependencies
        )
        contract = build_prediction_encode_contract(matches[0], SOURCE, self.dependencies)
        with tempfile.TemporaryDirectory() as directory:
            candidate = pathlib.Path(directory) / "candidate.sv"
            candidate.write_text(render_prediction_encode_rtl(contract), encoding="utf-8")
            result = subprocess.run(
                [
                    verilator,
                    "--lint-only",
                    "--Wno-fatal",
                    "--top-module",
                    contract["contract_id"].lower(),
                    str(candidate),
                ],
                cwd=directory,
                text=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                check=False,
            )
            self.assertEqual(result.returncode, 0, result.stdout)


if __name__ == "__main__":
    unittest.main()
