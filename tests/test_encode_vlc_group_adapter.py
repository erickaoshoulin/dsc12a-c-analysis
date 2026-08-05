import copy
import hashlib
import json
import pathlib
import shutil
import subprocess
import tempfile
import unittest

from tools.encode_vlc_group_adapter import (
    write_vlc_group_encode_overlay_sources,
)
from tools.verify_decode_integration import route_adapter_child_dispatchers


ROOT = pathlib.Path(__file__).resolve().parents[1]
ARTIFACT = ROOT / "rtl/encode-candidates/selected-vlc-group-encode-transition"
SOURCE_CANDIDATES = (
    pathlib.Path(
        "/Users/snow/Desktop/Display Stream Compression (DSC)/DSC 1.2a/"
        "DSC_model_20210623/source"
    ),
    ROOT / "DSC_model_20210623/source",
)


class _AdapterAgent:
    root = ROOT

    @staticmethod
    def overlay_runtime_metrics_source() -> str:
        return (
            "static unsigned long dsc_cicd_mismatches;\n"
            "static unsigned long dsc_cicd_calls;\n"
            "static void dsc_cicd_note_call(int mode) {\n"
            "    ++dsc_cicd_calls; (void)mode;\n"
            "}\n"
        )


def _source_dir() -> pathlib.Path | None:
    for candidate in SOURCE_CANDIDATES:
        if (candidate / "dsc_types.h").is_file() and (candidate / "fifo.h").is_file():
            return candidate
    return None


class EncodeVlcGroupAdapterTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.contract = json.loads(
            (ARTIFACT / "provisional-contract.json").read_text(encoding="utf-8")
        )
        cls.candidate = ARTIFACT / "candidate_01.sv"

    def _emit(self, directory: pathlib.Path, contract=None):
        return write_vlc_group_encode_overlay_sources(
            _AdapterAgent(),
            copy.deepcopy(contract or self.contract),
            directory,
            self.contract["rtl"]["module"],
            self.candidate,
        )

    def test_real_contract_emits_standard_composition_and_complete_frozen_inputs(self):
        self.assertEqual(
            self.contract["semantics"]["kind"], "vlc_group_encode_fsm"
        )
        with tempfile.TemporaryDirectory() as directory:
            paths = self._emit(pathlib.Path(directory))
            composition = paths["composition"]
            frozen_inputs = [
                item["name"]
                for item in self.contract["interface"]["ports"]
                if item["direction"] == "input"
            ]
            self.assertEqual(composition["status"], "PASS")
            self.assertEqual(composition["composition_status"], "EXTERNALIZED_CHILD_BOUNDARY")
            self.assertEqual(composition["frozen_input_ports"], frozen_inputs)
            self.assertEqual(len(composition["rtl_bindings"]), len(frozen_inputs))
            self.assertEqual(composition["caller_parameter_count"], 4)
            self.assertEqual(composition["rtl_input_count"], len(frozen_inputs))
            self.assertTrue(composition["se_size_fifo_events_in_source_order"])
            self.assertTrue(composition["simultaneous_child_dispatchers_required"])
            self.assertTrue(composition["c_oracle_uses_deep_private_state_snapshots"])
            self.assertTrue(composition["c_oracle_state_is_restored_before_rtl"])
            self.assertTrue(
                composition[
                    "rtl_return_commits_only_parent_outputs_and_hash_pinned_child_results"
                ]
            )
            self.assertTrue(composition["all_child_event_metadata_compared"])
            self.assertTrue(composition["byte_out_pointer_cursor_compared"])
            self.assertEqual(
                [child["role"] for child in composition["child_roles"]],
                ["vlc_unit", "process_group"],
            )
            for key in ("header", "abi", "overlay", "bridge", "main"):
                self.assertTrue(paths[key].is_file(), key)
            self.assertEqual(paths["candidate"], self.candidate)
            self.assertEqual(
                hashlib.sha256(self.candidate.read_bytes()).hexdigest(),
                self.contract["rtl"]["candidate_sha256"],
            )

    def test_generated_overlay_preserves_semantic_child_calls_and_restore_boundary(self):
        with tempfile.TemporaryDirectory() as directory:
            paths = self._emit(pathlib.Path(directory))
            overlay = paths["overlay"].read_text(encoding="utf-8")
            bridge = paths["bridge"].read_text(encoding="utf-8")
            self.assertIn("VLCUnit(", overlay)
            self.assertIn("ProcessGroupEnc(", overlay)
            self.assertIn("VLCGroup_original(", overlay)
            self.assertIn("dsc_cicd_snapshot_clone", overlay)
            self.assertIn("dsc_cicd_restore_snapshot", overlay)
            self.assertIn(
                "size_t frame_bytes = (size_t)dsc_cfg->chunk_size *",
                overlay,
            )
            self.assertIn(
                "memcpy(oracle.external_base, oracle.frame_data",
                overlay,
            )
            self.assertIn("dsc_cicd_compare_code", overlay)
            self.assertIn("dsc_cicd_vlc_group_service_vlc_unit", overlay)
            self.assertIn("dsc_cicd_vlc_group_service_process_group", overlay)
            self.assertIn("dsc_cicd_compare_state", overlay)
            self.assertIn("event_kind", overlay)
            self.assertIn("frame_write_events", overlay)
            self.assertIn("byte_cursor", overlay)
            self.assertIn("se_size_mem_write_req", bridge)
            self.assertIn("frame_mem_write_bit_mask", bridge)
            self.assertIn("context->state->forceMpp = dut.force_mpp_out", bridge)
            self.assertIn("dut.midpoint_selected_out[lane]", bridge)
            self.assertIn("service_low_phase", bridge)
            self.assertIn("DSC_CICD_VLC_GROUP_MAX_CYCLES", bridge)
            self.assertIn("double sc_time_stamp()", bridge)
            self.assertIn("while (!dut.done", bridge)
            self.assertNotIn("rust", (overlay + bridge).lower())
            self.assertNotIn("VLCGroup(", bridge)

            routed, receipts = route_adapter_child_dispatchers(
                overlay,
                own_function="VLCGroup",
                candidates=[
                    {"function": "VLCGroup", "slug": "vlc_group"},
                    {"function": "VLCUnit", "slug": "vlc_unit"},
                    {"function": "ProcessGroupEnc", "slug": "process_group"},
                ],
            )
            self.assertIn("dsc_cicd_vlc_unit_invoke", routed)
            self.assertIn("dsc_cicd_process_group_invoke", routed)
            self.assertNotIn("VLCUnit(", routed)
            self.assertNotIn("ProcessGroupEnc(", routed)
            self.assertEqual(
                {item["function"] for item in receipts},
                {"VLCUnit", "ProcessGroupEnc"},
            )

    def test_function_spelling_is_not_an_admission_predicate(self):
        contract = copy.deepcopy(self.contract)
        contract["function"]["name"] = "renamed_group_entry"
        with tempfile.TemporaryDirectory() as directory:
            paths = self._emit(pathlib.Path(directory), contract)
            overlay = paths["overlay"].read_text(encoding="utf-8")
            self.assertIn("renamed_group_entry_original", overlay)
            self.assertNotIn("VLCGroup_original", overlay)

    def test_real_candidate_lints_with_verilator(self):
        rtl = self.candidate.read_text(encoding="utf-8")
        self.assertIn("active_max_se_size", rtl)
        self.assertIn("$signed({1'b0, units_per_group})", rtl)
        self.assertNotIn(
            "se_size_byte_ctr_r[ssp_index_r] <= "
            "se_size_byte_ctr_r[ssp_index_r] + 32'd1",
            rtl,
        )
        verilator = shutil.which("verilator")
        if not verilator:
            self.skipTest("verilator is unavailable")
        result = subprocess.run(
            [
                verilator,
                "--lint-only",
                "--Wno-fatal",
                "--language",
                "1800-2012",
                "--top-module",
                self.contract["rtl"]["module"],
                str(self.candidate),
            ],
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            check=False,
        )
        self.assertEqual(result.returncode, 0, result.stdout)

    def test_generated_c_and_cpp_sources_compile_where_toolchains_are_available(self):
        source = _source_dir()
        clang = shutil.which("clang")
        clangxx = shutil.which("clang++")
        verilator = shutil.which("verilator")
        if not source or not clang or not clangxx or not verilator:
            self.skipTest("immutable C headers or compiler toolchain is unavailable")
        with tempfile.TemporaryDirectory() as directory:
            root = pathlib.Path(directory)
            paths = self._emit(root)
            c_result = subprocess.run(
                [
                    clang,
                    "-std=gnu99",
                    "-Wall",
                    "-Wextra",
                    "-Werror",
                    "-fsyntax-only",
                    "-I",
                    str(root),
                    "-I",
                    str(source),
                    str(paths["overlay"]),
                ],
                text=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                check=False,
            )
            self.assertEqual(c_result.returncode, 0, c_result.stdout)

            obj = root / "verilator-obj"
            lint = subprocess.run(
                [
                    verilator,
                    "--cc",
                    "--Wno-fatal",
                    "--Mdir",
                    str(obj),
                    "--language",
                    "1800-2012",
                    "--top-module",
                    self.contract["rtl"]["module"],
                    str(self.candidate),
                ],
                text=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                check=False,
            )
            self.assertEqual(lint.returncode, 0, lint.stdout)
            verilator_include = (
                pathlib.Path(verilator).resolve().parent.parent
                / "share/verilator/include"
            )
            cpp_result = subprocess.run(
                [
                    clangxx,
                    "-std=c++17",
                    "-fsyntax-only",
                    "-I",
                    str(obj),
                    "-I",
                    str(verilator_include),
                    "-I",
                    str(root),
                    "-I",
                    str(source),
                    str(paths["bridge"]),
                ],
                text=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                check=False,
            )
            self.assertEqual(cpp_result.returncode, 0, cpp_result.stdout)


if __name__ == "__main__":
    unittest.main()
