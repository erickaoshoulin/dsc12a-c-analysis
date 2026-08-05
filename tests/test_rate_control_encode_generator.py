import copy
import json
import pathlib
import shutil
import subprocess
import tempfile
import unittest

from tools.generate_rate_control_encode import (
    build_rate_control_encode_contract,
    discover_rate_control_encode_candidates,
    file_hash,
    read_json,
    render_rate_control_encode_rtl,
)


REPO_ROOT = pathlib.Path(__file__).resolve().parents[1]
SOURCE_CANDIDATES = (
    pathlib.Path(
        "/Users/snow/Desktop/Display Stream Compression (DSC)/DSC 1.2a"
        "/DSC_model_20210623/source"
    ),
    REPO_ROOT / "DSC_model_20210623" / "source",
)


def immutable_source_dir() -> pathlib.Path:
    for path in SOURCE_CANDIDATES:
        if (path / "dsc_codec.c").is_file():
            return path
    raise AssertionError("immutable DSC C source directory is not available")


class RateControlEncodeGeneratorTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.source_dir = immutable_source_dir()
        cls.functions = read_json(REPO_ROOT / "facts" / "functions.json")
        cls.candidates = read_json(REPO_ROOT / "facts" / "candidates.json")
        cls.coverage = read_json(REPO_ROOT / "coverage" / "coverage.json")
        cls.discovered = discover_rate_control_encode_candidates(
            cls.functions,
            cls.candidates,
            cls.coverage,
            cls.source_dir,
            REPO_ROOT,
        )
        cls.function = next(
            row
            for row in cls.functions["functions"]
            if row["clang_usr"] == cls.discovered[0]["clang_usr"]
        )
        cls.contract = build_rate_control_encode_contract(
            cls.discovered[0], cls.function, cls.source_dir, REPO_ROOT
        )

    def test_real_facts_and_coverage_discover_one_structural_encode_candidate(self):
        self.assertEqual(len(self.discovered), 1)
        selected = self.discovered[0]
        self.assertEqual(selected["semantics_kind"], "bounded_rate_control_encode_transition")
        self.assertGreater(selected["execution_count"], 0)
        self.assertEqual(selected["literal_size_bound"]["group_size"], [1, 3])
        self.assertEqual(selected["literal_size_bound"]["max_remove_stages"], 3)
        self.assertEqual(
            selected["structural_evidence"]["scalar_parameter_types"],
            ["int", "int", "int", "int", "int"],
        )
        source_lines = (self.source_dir / self.function["source_file"]).read_text(
            encoding="utf-8", errors="replace"
        ).splitlines()
        source_body = "\n".join(
            source_lines[
                self.function["line"] - 1 : self.function["end_line"]
            ]
        )
        self.assertIn("midpointSelected", source_body)

    def test_discovery_does_not_depend_on_function_name(self):
        functions = copy.deepcopy(self.functions)
        candidates = copy.deepcopy(self.candidates)
        target_usr = self.discovered[0]["clang_usr"]
        renamed = "StructurallyRenamedController"
        for row in functions["functions"]:
            if row.get("clang_usr") == target_usr:
                row["name"] = renamed
                row["qualified_name"] = renamed
        for row in candidates["functions"]:
            if row.get("clang_usr") == target_usr:
                row["name"] = renamed
                row["qualified_name"] = renamed
        discovered = discover_rate_control_encode_candidates(
            functions, candidates, self.coverage, self.source_dir, REPO_ROOT
        )
        self.assertEqual(len(discovered), 1)
        self.assertEqual(discovered[0]["name"], renamed)

    def test_contract_has_midpoint_inputs_fourteen_scalar_outputs_and_three_events(self):
        contract = self.contract
        ports = {port["name"]: port for port in contract["interface"]["ports"]}
        semantics = contract["semantics"]
        bindings = semantics["bindings"]
        self.assertEqual(semantics["specialization"]["is_encoder"], 1)
        self.assertEqual(semantics["specialization"]["midpoint_source"], "midpointSelected")
        self.assertEqual(len(bindings["midpoint_ports"]), 4)
        self.assertTrue(all(name in ports for name in bindings["midpoint_ports"]))
        self.assertFalse(any("use_midpoint" in name for name in ports))
        self.assertEqual(len(bindings["state_output_ports"]), 14)
        self.assertTrue(all(name in ports for name in bindings["state_output_ports"].values()))
        self.assertEqual(len(bindings["chunk_event_ports"]), 3)
        for event in bindings["chunk_event_ports"]:
            self.assertTrue(all(name in ports for name in event.values()))
        self.assertEqual(
            {port["name"] for port in ports.values() if port["direction"] == "output"}
            - set(bindings["state_output_ports"].values())
            - {"domain_valid", "fatal_error", "fatal_error_code"}
            - {
                name
                for event in bindings["chunk_event_ports"]
                for name in event.values()
            },
            set(),
        )
        self.assertEqual(contract["dependencies"][0]["role"], "remove_one_pixel_bits")
        self.assertGreater(contract["dependencies"][0]["rtl_return_invocations"], 0)

    def test_rendered_rtl_contains_exact_encoder_priority_and_lints(self):
        rtl = render_rate_control_encode_rtl(self.contract)
        self.assertIn("state_midpoint_selected_0", rtl)
        self.assertNotIn("state_use_midpoint", rtl)
        self.assertIn("remove_stage_0_i", rtl)
        self.assertIn("remove_stage_1_i", rtl)
        self.assertIn("remove_stage_2_i", rtl)
        self.assertIn("fatal_error_code", rtl)
        self.assertIn(">>> 3", rtl)
        self.assertIn("else if (state_bitsavemode_out != 32'sd0)", rtl)
        self.assertIn("else if (rc_size_group_i == state_unitspergroup)", rtl)
        self.assertIn("current_qp_i < cfg_rc_quant_incr_limit0", rtl)
        self.assertIn("chunk_write_enable_2", rtl)

        verilator = shutil.which("verilator")
        if not verilator:
            self.skipTest("Verilator is not installed")
        with tempfile.TemporaryDirectory() as directory:
            candidate = pathlib.Path(directory) / "rate_control_encode.sv"
            candidate.write_text(rtl, encoding="utf-8")
            result = subprocess.run(
                [
                    verilator,
                    "--lint-only",
                    "--Wno-fatal",
                    "--top-module",
                    self.contract["contract_id"],
                    str(candidate),
                ],
                cwd=directory,
                text=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                check=False,
            )
            self.assertEqual(result.returncode, 0, result.stdout)

    def test_child_hashes_are_bound_to_the_existing_proven_transition(self):
        dependency = self.contract["dependencies"][0]
        contract_path = REPO_ROOT / dependency["contract_file"]
        module_path = REPO_ROOT / dependency["module_file"]
        self.assertEqual(file_hash(contract_path), dependency["contract_sha256"])
        self.assertEqual(file_hash(module_path), dependency["module_sha256"])
        child_contract = json.loads(contract_path.read_text(encoding="utf-8"))
        self.assertEqual(child_contract["semantics"]["kind"], "scalar_record_memory_transition")
        self.assertIn("chunk_write_enable", {p["name"] for p in child_contract["interface"]["ports"]})


if __name__ == "__main__":
    unittest.main()
