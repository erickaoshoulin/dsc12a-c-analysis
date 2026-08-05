#!/usr/bin/env python3
"""Tests for the isolated encoder ProcessGroup generator and RTL artifact."""

from __future__ import annotations

import copy
import hashlib
import json
import pathlib
import shutil
import subprocess
import tempfile
import unittest

from tools import generate_process_group_encode as generator


ROOT = pathlib.Path(__file__).resolve().parents[1]


class ProcessGroupEncodeGeneratorTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.source_dir = generator._default_source_dir(ROOT)
        cls.functions = generator._read_json(ROOT / "facts" / "functions.json")
        cls.coverage = generator._read_json(ROOT / "coverage" / "coverage.json")
        cls.frontier = generator._read_json(ROOT / "coverage" / "encode" / "frontier.json")
        cls.candidate = generator.discover_process_group_candidate(
            cls.functions,
            cls.coverage,
            cls.source_dir,
            encode_frontier_document=cls.frontier,
        )
        cls.pins = generator.discover_dependency_pins(ROOT, cls.source_dir)

    def test_discovery_is_encode_coverage_and_structural_not_name_allowlist(self) -> None:
        renamed = copy.deepcopy(self.functions)
        renamed_target = None
        for row in renamed["functions"]:
            if (
                row.get("source_file") == self.candidate["source_file"]
                and row.get("line") == self.candidate["source_span"]["start_line"]
                and row.get("loop_count") == 2
            ):
                row["name"] = "renamed_structural_mux_target"
                renamed_target = row
                break
        self.assertIsNotNone(renamed_target)
        selected = generator.discover_process_group_candidate(
            renamed,
            self.coverage,
            self.source_dir,
            encode_frontier_document=self.frontier,
        )
        self.assertEqual(selected["name"], "renamed_structural_mux_target")
        self.assertGreater(selected["execution_count"], 0)
        self.assertIn("ssp-loop-bound", selected["structural_evidence"])
        self.assertIn("mux-byte-loop-bound", selected["structural_evidence"])

        uncovered = copy.deepcopy(self.coverage)
        for row in uncovered["functions"]:
            if row.get("clang_usr") == self.candidate["clang_usr"]:
                row["coverage"]["covered"] = False
                row["coverage"]["execution_count"] = 0
        with self.assertRaises(generator.DiscoveryError):
            generator.discover_process_group_candidate(
                renamed,
                uncovered,
                self.source_dir,
            )

    def test_dependency_contracts_are_semantically_selected_and_hash_pinned(self) -> None:
        self.assertEqual(
            set(self.pins),
            {
                "fifo_read_transition",
                "fifo_write_transition",
                "bitstream_write_transition",
            },
        )
        for kind, pin in self.pins.items():
            self.assertEqual(len(pin.contract_sha256), 64, kind)
            self.assertEqual(len(pin.module_sha256), 64, kind)
            self.assertEqual(len(pin.source_body_sha256), 64, kind)
            self.assertEqual(len(pin.source_file_sha256), 64, kind)

        with tempfile.TemporaryDirectory(prefix="dsc-process-group-deps-") as temp:
            temp_path = pathlib.Path(temp) / "tampered.json"
            tampered = json.loads(pathlib.Path(self.pins["fifo_read_transition"].contract_path).read_text())
            tampered["function"]["source_body_sha256"] = "0" * 64
            temp_path.write_text(json.dumps(tampered), encoding="utf-8")
            paths = [
                temp_path,
                pathlib.Path(self.pins["fifo_write_transition"].contract_path),
                pathlib.Path(self.pins["bitstream_write_transition"].contract_path),
            ]
            with self.assertRaises(generator.DiscoveryError):
                generator.discover_dependency_pins(
                    ROOT,
                    self.source_dir,
                    contract_paths=paths,
                )

    def test_contract_generation_captures_full_state_and_memory_interface(self) -> None:
        contract = generator.build_contract(self.candidate, self.pins)
        self.assertEqual(
            contract["semantics"]["kind"],
            "bounded_process_group_encode_transition",
        )
        self.assertEqual(len(contract["composition"]["dependencies"]), 3)
        self.assertTrue(all(
            len(item["module_sha256"]) == 64
            for item in contract["composition"]["dependencies"]
        ))
        self.assertEqual(contract["domain"]["num_ssps"], [3, 4])
        self.assertEqual(contract["domain"]["mux_word_size"], [48, 64])
        self.assertEqual(contract["domain"]["is_encoder"], 1)
        self.assertTrue(contract["domain"]["frame_write_mask_is_read_modify_write"])
        self.assertEqual(
            set(contract["flags"]),
            {
                "illegal_domain",
                "fifo_underflow",
                "fifo_overflow",
                "frame_overflow",
                "se_size_overflow",
            },
        )
        ports = {item["name"]: item for item in contract["interface"]["ports"]}
        for prefix in ("enc_balance", "shifter", "se_size"):
            for field in (
                "size_bits",
                "fullness",
                "read_ptr",
                "write_ptr",
                "max_fullness",
                "byte_ctr",
            ):
                self.assertIn(f"{prefix}_{field}_in", ports)
                self.assertIn(f"{prefix}_{field}_out", ports)
            self.assertIn(f"{prefix}_mem_read_req", ports)
            self.assertIn(f"{prefix}_mem_read_valid", ports)
            self.assertIn(f"{prefix}_mem_write_req", ports)
            self.assertIn(f"{prefix}_mem_write_ready", ports)
        self.assertIn("frame_mem_write_req", ports)
        self.assertIn("frame_mem_write_bit_mask", ports)
        self.assertIn("post_mux_num_bits_out", ports)

    def test_generation_writes_only_candidate_and_contract_and_preserves_order(self) -> None:
        with tempfile.TemporaryDirectory(prefix="dsc-process-group-artifact-") as temp:
            output = pathlib.Path(temp) / "candidate"
            artifact = generator.generate_artifact(ROOT, output)
            self.assertEqual(
                {path.name for path in output.iterdir()},
                {"candidate_01.sv", "provisional-contract.json"},
            )
            rtl = artifact["rtl"]
            contract = json.loads((output / "provisional-contract.json").read_text())
            self.assertEqual(
                contract["rtl"]["candidate_sha256"],
                hashlib.sha256(rtl.encode()).hexdigest(),
            )
            self.assertEqual(rtl.count("module process_group_encode_fsm"), 1)
            order = [
                "ST_CHECK_SSP",
                "ST_PREP_ENC_BIT",
                "ST_ENC_READ",
                "ST_FRAME_WRITE",
                "ST_PREP_SHIFTER_WRITE",
                "ST_SHIFTER_WRITE",
                "ST_PREP_SE_SIZE",
                "ST_SE_SIZE_READ",
                "ST_PREP_SHIFTER_DISCARD",
                "ST_SHIFTER_DISCARD",
            ]
            positions = [rtl.index(item) for item in order]
            self.assertEqual(positions, sorted(positions))
            self.assertIn("enc_balance_mem_read_req", rtl)
            self.assertIn("shifter_mem_write_bit_mask", rtl)
            self.assertIn(
                "one_hot_bit(3'd7 - shifter_write_ptr_r[ssp_index_r][2:0])",
                rtl,
            )
            self.assertIn("se_size_mem_read_valid", rtl)
            self.assertIn("frame_mem_write_bit_mask", rtl)
            self.assertNotIn("getbits(", rtl)

    def test_generated_rtl_passes_verilator_lint(self) -> None:
        verilator = shutil.which("verilator")
        if verilator is None:
            self.skipTest("Verilator is not installed")
        rtl = generator.render_rtl(self.candidate, self.pins)
        with tempfile.TemporaryDirectory(prefix="dsc-process-group-lint-") as temp:
            source = pathlib.Path(temp) / "process_group_encode_fsm.sv"
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
                    "process_group_encode_fsm",
                    str(source),
                ],
                capture_output=True,
                text=True,
                check=False,
            )
            self.assertEqual(
                result.returncode,
                0,
                msg=f"Verilator lint failed:\n{result.stdout}\n{result.stderr}",
            )


if __name__ == "__main__":
    unittest.main()
