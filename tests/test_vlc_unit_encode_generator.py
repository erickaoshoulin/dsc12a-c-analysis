import copy
import pathlib
import shutil
import subprocess
import tempfile
import unittest

from tools.generate_vlc_unit_encode import (
    build_vlc_unit_encode_contract,
    discover_vlc_unit_encode_candidates,
    file_hash,
    read_json,
    render_vlc_unit_encode_rtl,
    verify_dependency_pins,
)


REPO_ROOT = pathlib.Path(__file__).resolve().parents[1]
SOURCE_CANDIDATES = (
    pathlib.Path(
        "/Users/snow/Desktop/Display Stream Compression (DSC)/DSC 1.2a/"
        "DSC_model_20210623/source"
    ),
    REPO_ROOT / "DSC_model_20210623" / "source",
)


def immutable_source_dir() -> pathlib.Path:
    for path in SOURCE_CANDIDATES:
        if (path / "dsc_codec.c").is_file() and (path / "multiplex.c").is_file():
            return path
    raise unittest.SkipTest("immutable DSC model source directory is unavailable")


class VlcUnitEncodeGeneratorTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.source_dir = immutable_source_dir()
        cls.functions = read_json(REPO_ROOT / "facts" / "functions.json")
        cls.candidates = read_json(REPO_ROOT / "facts" / "candidates.json")
        cls.coverage = read_json(REPO_ROOT / "coverage" / "coverage.json")
        cls.discovered = discover_vlc_unit_encode_candidates(
            cls.functions,
            cls.candidates,
            cls.coverage,
            cls.source_dir,
            REPO_ROOT,
        )
        if not cls.discovered:
            raise unittest.SkipTest("the current facts do not expose the VLC-unit boundary")
        cls.selected = cls.discovered[0]
        cls.function = next(
            row
            for row in cls.functions["functions"]
            if row.get("clang_usr") == cls.selected["clang_usr"]
        )
        cls.contract = build_vlc_unit_encode_contract(
            cls.selected,
            cls.function,
            cls.source_dir,
            REPO_ROOT,
        )

    def test_discovery_is_coverage_and_structural_signature_driven(self):
        self.assertEqual(len(self.discovered), 1)
        self.assertEqual(
            self.selected["semantics_kind"], "bounded_vlc_unit_encode_transition"
        )
        self.assertGreater(self.selected["execution_count"], 0)
        evidence = self.selected["structural_evidence"]
        self.assertEqual(evidence["max_addbits_commands"], 9)
        self.assertEqual(evidence["dynamic_ich_bound"], 6)
        self.assertEqual(evidence["bounded_ich_loop_count"], 4)
        self.assertIn("fixed sample/unit loops", " ".join(self.selected["selection_basis"]))
        self.assertTrue(evidence["source_ordered"])
        self.assertTrue(evidence["fatal_side_effects_separated"])

    def test_discovery_does_not_use_function_name_allowlist(self):
        functions = copy.deepcopy(self.functions)
        candidates = copy.deepcopy(self.candidates)
        renamed = "StructurallyRenamedEncodeBoundary"
        for row in functions["functions"]:
            if row.get("clang_usr") == self.selected["clang_usr"]:
                row["name"] = renamed
                row["qualified_name"] = renamed
        for row in candidates["functions"]:
            if row.get("clang_usr") == self.selected["clang_usr"]:
                row["name"] = renamed
                row["qualified_name"] = renamed
        discovered = discover_vlc_unit_encode_candidates(
            functions,
            candidates,
            self.coverage,
            self.source_dir,
            REPO_ROOT,
        )
        self.assertEqual(len(discovered), 1)
        self.assertEqual(discovered[0]["name"], renamed)

    def test_discovery_rejects_uncovered_boundary(self):
        coverage = copy.deepcopy(self.coverage)
        row = next(
            item
            for item in coverage["functions"]
            if item.get("clang_usr") == self.selected["clang_usr"]
        )
        row["coverage"]["covered"] = False
        row["coverage"]["execution_count"] = 0
        self.assertEqual(
            discover_vlc_unit_encode_candidates(
                self.functions,
                self.candidates,
                coverage,
                self.source_dir,
                REPO_ROOT,
            ),
            [],
        )

    def test_addbits_dependency_contract_module_and_source_body_are_pinned(self):
        dependency = self.contract["dependencies"][0]
        self.assertEqual(dependency["role"], "addbits_command_sink")
        self.assertEqual(
            file_hash(REPO_ROOT / dependency["contract_file"]),
            dependency["contract_sha256"],
        )
        self.assertEqual(
            file_hash(REPO_ROOT / dependency["module_file"]),
            dependency["module_sha256"],
        )
        child = verify_dependency_pins(self.contract, REPO_ROOT, self.source_dir)
        self.assertEqual(child[0]["semantics"]["kind"], "fifo_write_accounting_transition")
        self.assertTrue(dependency["source_body_sha256"])
        self.assertTrue(dependency["source_file_sha256"])

    def test_hash_drift_is_rejected_without_touching_repository_artifacts(self):
        dependency = self.contract["dependencies"][0]
        with tempfile.TemporaryDirectory() as directory:
            root = pathlib.Path(directory)
            for key in (
                "contract_file",
                "module_file",
                "matrix_receipt_file",
                "rtl_return_receipt_file",
            ):
                source = REPO_ROOT / dependency[key]
                target = root / dependency[key]
                target.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(source, target)
            copied_contract = copy.deepcopy(self.contract)
            copied_dependency = copied_contract["dependencies"][0]
            module = root / copied_dependency["module_file"]
            module.write_text(module.read_text(encoding="utf-8") + "\n// drift\n", encoding="utf-8")
            with self.assertRaisesRegex(RuntimeError, "module hash drift"):
                verify_dependency_pins(copied_contract, root, self.source_dir)

        with tempfile.TemporaryDirectory() as directory:
            source_root = pathlib.Path(directory)
            source_root.mkdir(parents=True, exist_ok=True)
            source = self.source_dir / dependency["source_file"]
            modified = source_root / dependency["source_file"]
            modified.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(source, modified)
            modified.write_bytes(modified.read_bytes().replace(b"void AddBits", b"void DriftBits", 1))
            copied_contract = copy.deepcopy(self.contract)
            copied_contract["dependencies"][0]["source_root"] = str(source_root)
            with self.assertRaisesRegex(RuntimeError, "source body hash drift"):
                verify_dependency_pins(copied_contract, REPO_ROOT, source_root)

    def test_contract_exposes_complete_state_outputs_and_ordered_nine_slot_stream(self):
        semantics = self.contract["semantics"]
        bindings = semantics["bindings"]
        ports = {item["name"]: item for item in self.contract["interface"]["ports"]}
        command_ports = bindings["command_ports"]
        self.assertEqual(len(command_ports), 9)
        self.assertEqual(semantics["command_stream"]["max_commands"], 9)
        self.assertTrue(semantics["command_stream"]["bounded"])
        self.assertTrue(semantics["command_stream"]["ordered"])
        for command in command_ports:
            self.assertTrue(all(name in ports for name in command.values()))
        for field in ("flatnessType", "ichSelected", "prevIchSelected", "midpointSelected", "predictedSize", "rcSizeUnit"):
            value = bindings["state_output_ports"][field]
            values = value if isinstance(value, list) else [value]
            self.assertTrue(all(name in ports for name in values))
        self.assertIn("state_num_bits_output", bindings)
        self.assertIn("num_bits_delta_port", bindings)
        self.assertEqual(
            [item["stage"] for item in semantics["command_stream"]["source_order"]],
            [
                "flatness_flag",
                "first_flat",
                "early_ich_indices",
                "ich_prefix",
                "ich_indices",
                "residual_prefix",
                "sample_deltas",
            ],
        )
        self.assertTrue(self.contract["selection"]["no_function_name_allowlist"])

    def test_rendered_rtl_keeps_source_order_and_lints_with_verilator(self):
        rtl = render_vlc_unit_encode_rtl(self.contract, REPO_ROOT, self.source_dir)
        self.assertIn("module addbits_encode_transition", rtl)
        self.assertIn("module vlcunit_encode_transition", rtl)
        self.assertIn("emit_addbits", rtl)
        self.assertIn("addbits_cmd_valid_8", rtl)
        self.assertIn("fatal_error_code", rtl)
        self.assertIn("bounded_loop_violation", rtl)
        self.assertLess(rtl.index("source line 1535"), rtl.index("source line 1548"))
        self.assertLess(rtl.index("source line 1548"), rtl.index("source line 1633"))
        self.assertLess(rtl.index("source line 1633"), rtl.index("source line 1673"))
        self.assertLess(rtl.index("source line 1673"), rtl.index("source line 1682"))

        verilator = shutil.which("verilator")
        if not verilator:
            self.skipTest("Verilator is not installed")
        with tempfile.TemporaryDirectory() as directory:
            candidate = pathlib.Path(directory) / "vlc_unit_encode.sv"
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


if __name__ == "__main__":
    unittest.main()
