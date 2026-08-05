#!/usr/bin/env python3
"""Focused tests for the generator-only VLCGroup Encode parent boundary."""

from __future__ import annotations

import copy
import hashlib
import json
import pathlib
import shutil
import subprocess
import tempfile
import unittest

from tools import generate_process_group_encode
from tools import generate_vlc_group_encode as generator


ROOT = pathlib.Path(__file__).resolve().parents[1]
SOURCE = generator._default_source_dir(ROOT)


class VLCGroupEncodeGeneratorTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.functions = generator._read_json(ROOT / "facts" / "functions.json")
        cls.coverage = generator._read_json(ROOT / "coverage" / "coverage.json")
        cls.frontier = generator._read_json(ROOT / "coverage" / "encode" / "frontier.json")
        cls.candidate = generator.discover_vlc_group_candidate(
            cls.functions,
            cls.coverage,
            SOURCE,
            encode_frontier_document=cls.frontier,
        )

    @staticmethod
    def _write_vlc_unit_artifact(directory: pathlib.Path) -> pathlib.Path:
        directory.mkdir(parents=True, exist_ok=True)
        module = directory / "candidate_01.sv"
        module.write_text(
            "module vlc_unit_encode_child;\nendmodule\n",
            encoding="utf-8",
        )
        source_function = next(
            row for row in generator._rows(generator._read_json(ROOT / "facts" / "functions.json"), "functions")
            if row.get("clang_usr") == "c:@F@VLCUnit"
        )
        function = copy.deepcopy(source_function)
        function["source_span"] = {
            "start_line": int(source_function["line"]),
            "end_line": int(source_function["end_line"]),
        }
        function["source_body_sha256"] = generator.source_body_sha256(SOURCE, function)
        contract = {
            "schema_version": 1,
            "contract_id": "vlc_unit_encode_child_v1",
            "status": "PROVISIONAL_SIMULATION_ONLY",
            "origin": "tool_discovered_encoder_runtime_transition",
            "function": function,
            "semantics": {
                "kind": "bounded_vlc_unit_encode_transition",
                "legal_domain": {"unit": [0, 3]},
            },
            "interface": {
                "module": "vlc_unit_encode_child",
                "ports": [
                    {"name": "domain_valid", "direction": "output", "width": 1},
                    {"name": "num_bits_out", "direction": "output", "width": 32},
                ],
            },
            "rtl": {
                "module": "vlc_unit_encode_child",
                "candidate_sha256": hashlib.sha256(module.read_bytes()).hexdigest(),
            },
        }
        (directory / "provisional-contract.json").write_text(
            json.dumps(contract, indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
        )
        return directory

    @staticmethod
    def _write_process_group_artifact(directory: pathlib.Path) -> pathlib.Path:
        generate_process_group_encode.generate_artifact(ROOT, directory)
        return directory

    def _pins(self, temporary: pathlib.Path) -> dict[str, generator.ChildPin]:
        vlc = self._write_vlc_unit_artifact(temporary / "vlc-unit")
        process = self._write_process_group_artifact(temporary / "process-group")
        return generator.discover_dependency_pins(
            ROOT,
            SOURCE,
            vlc_unit_artifact=vlc,
            process_group_artifact=process,
        )

    def test_discovery_uses_encode_coverage_and_structure_not_function_name(self) -> None:
        renamed = copy.deepcopy(self.functions)
        for row in renamed["functions"]:
            if row.get("clang_usr") == self.candidate["clang_usr"]:
                row["name"] = "renamed_ordered_encode_group"
        selected = generator.discover_vlc_group_candidate(
            renamed,
            self.coverage,
            SOURCE,
            encode_frontier_document=self.frontier,
        )
        self.assertEqual(selected["name"], "renamed_ordered_encode_group")
        self.assertGreater(selected["execution_count"], 0)
        self.assertIn(
            "source-order-unit-then-se-size-fifo-then-process-group",
            selected["structural_evidence"],
        )
        self.assertEqual(
            selected["source_order_evidence"]["vlc_unit"],
            [1754, 1774],
        )

        uncovered = copy.deepcopy(self.coverage)
        for row in uncovered["functions"]:
            if row.get("clang_usr") == self.candidate["clang_usr"]:
                row["coverage"]["covered"] = False
                row["coverage"]["execution_count"] = 0
        with self.assertRaises(generator.DiscoveryError):
            generator.discover_vlc_group_candidate(renamed, uncovered, SOURCE)

    def test_child_resolution_requires_explicit_missing_artifact_and_pins_all_bytes(self) -> None:
        with tempfile.TemporaryDirectory(prefix="dsc-vlc-group-child-") as temporary:
            temporary_path = pathlib.Path(temporary)
            process = self._write_process_group_artifact(temporary_path / "process-group")
            with self.assertRaisesRegex(generator.DiscoveryError, "does not exist"):
                generator.discover_dependency_pins(
                    ROOT,
                    SOURCE,
                    vlc_unit_artifact=temporary_path / "missing-vlc-unit",
                    process_group_artifact=process,
                )
            pins = self._pins(temporary_path / "valid")
            self.assertEqual(set(pins), {"vlc_unit", "process_group"})
            for role, pin in pins.items():
                self.assertEqual(len(pin.contract_sha256), 64, role)
                self.assertEqual(len(pin.module_sha256), 64, role)
                self.assertEqual(len(pin.function["source_body_sha256"]), 64, role)
                self.assertEqual(len(pin.source_file_sha256 or ""), 64, role)

    def test_contract_records_externalized_ordered_composition_and_sidebands(self) -> None:
        with tempfile.TemporaryDirectory(prefix="dsc-vlc-group-contract-") as temporary:
            pins = self._pins(pathlib.Path(temporary))
            contract = generator.build_contract(self.candidate, pins)
        self.assertEqual(contract["semantics"]["kind"], "vlc_group_encode_fsm")
        self.assertEqual(contract["domain"]["units_per_group"], [3, 4])
        self.assertEqual(contract["domain"]["num_ssps"], [3, 4])
        self.assertEqual(contract["composition"]["status"], "EXTERNALIZED_CHILD_BOUNDARY")
        self.assertFalse(contract["composition"]["child_modules_instantiated"])
        self.assertEqual(
            [item["role"] for item in contract["dependencies"]],
            ["vlc_unit", "process_group"],
        )
        ports = {item["name"]: item for item in contract["interface"]["ports"]}
        for name in (
            "domain_valid",
            "illegal_domain",
            "fatal_error",
            "bound_violation",
            "done",
            "vlc_unit_start",
            "process_group_start",
            "se_size_mem_write_req",
            "frame_mem_write_req",
        ):
            self.assertIn(name, ports)
        order = contract["source_order"]
        self.assertLess(order.index("for unit=0..unitsPerGroup-1: call VLCUnit and commit its state snapshot"), order.index("for ssp=0..numSsps-1: fifo_put_bits(seSizeFifo, encBalance delta, 8)"))
        self.assertLess(
            order.index(
                "for ssp=0..numSsps-1: fifo_put_bits(seSizeFifo, encBalance delta, 8)"
            ),
            order.index(
                "if groupCount > mux_word_size + "
                "(4 * bits_per_component + 4) - 3: call ProcessGroupEnc"
            ),
        )

    def test_generation_is_private_and_rtl_preserves_parent_state_order(self) -> None:
        with tempfile.TemporaryDirectory(prefix="dsc-vlc-group-artifact-") as temporary:
            temporary_path = pathlib.Path(temporary)
            vlc = self._write_vlc_unit_artifact(temporary_path / "vlc-unit")
            process = self._write_process_group_artifact(temporary_path / "process-group")
            output = temporary_path / "parent"
            artifact = generator.generate_artifact(
                ROOT,
                output,
                source_dir=SOURCE,
                vlc_unit_artifact=vlc,
                process_group_artifact=process,
            )
            self.assertEqual(
                {path.name for path in output.iterdir()},
                {"candidate_01.sv", "provisional-contract.json"},
            )
            contract = json.loads((output / "provisional-contract.json").read_text(encoding="utf-8"))
            rtl = artifact["rtl"]
            self.assertEqual(contract["rtl"]["candidate_sha256"], hashlib.sha256(rtl.encode()).hexdigest())
            self.assertEqual(rtl.count("module vlc_group_encode_fsm"), 1)
            order = [
                "ST_VLC_START",
                "ST_VLC_WAIT",
                "ST_SE_PREP",
                "ST_SE_WRITE",
                "ST_PROCESS_CHECK",
                "ST_PROCESS_START",
                "ST_PROCESS_WAIT",
                "ST_ACCOUNT",
            ]
            self.assertEqual([rtl.index(item) for item in order], sorted(rtl.index(item) for item in order))
            for marker in (
                "vlc_unit_start",
                "se_size_mem_write_req",
                "process_group_start",
                "frame_mem_write_req",
                "fatal_error",
                "MAX_CYCLES",
            ):
                self.assertIn(marker, rtl)
            self.assertNotIn("VLCUnit(", rtl)
            self.assertNotIn("ProcessGroupEnc(", rtl)

    def test_render_rejects_tampered_child_module_hash(self) -> None:
        with tempfile.TemporaryDirectory(prefix="dsc-vlc-group-tamper-") as temporary:
            pins = self._pins(pathlib.Path(temporary))
            tampered = copy.copy(pins["vlc_unit"])
            object.__setattr__(tampered, "module_sha256", "0" * 64)
            pins["vlc_unit"] = tampered
            with self.assertRaisesRegex(generator.DiscoveryError, "pinned child module changed"):
                generator.render_rtl(self.candidate, pins, root=ROOT)

    def test_generated_rtl_passes_verilator_lint(self) -> None:
        verilator = shutil.which("verilator")
        if verilator is None:
            self.skipTest("Verilator is not installed")
        with tempfile.TemporaryDirectory(prefix="dsc-vlc-group-lint-") as temporary:
            pins = self._pins(pathlib.Path(temporary))
            rtl = generator.render_rtl(self.candidate, pins, root=ROOT)
            source = pathlib.Path(temporary) / "vlc_group_encode_fsm.sv"
            source.write_text(rtl, encoding="utf-8")
            result = subprocess.run(
                [
                    verilator,
                    "--lint-only",
                    "--language",
                    "1800-2012",
                    "-Wall",
                    "--Wno-fatal",
                    "--top-module",
                    "vlc_group_encode_fsm",
                    str(source),
                ],
                capture_output=True,
                text=True,
                check=False,
            )
            self.assertEqual(result.returncode, 0, f"Verilator lint failed:\n{result.stdout}\n{result.stderr}")


if __name__ == "__main__":
    unittest.main()
