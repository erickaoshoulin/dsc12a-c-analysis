import json
import pathlib
import tempfile
import unittest

from tools.cicd_agent import Agent
from tools.decode_frontier import (
    attach_integration_receipt,
    c_orchestration_boundary,
    discover,
    scan_provisional,
)
from tools.generate_decode_transition import build_contract, render_rtl


class DecodeFrontierTests(unittest.TestCase):
    def test_c_orchestration_boundaries_are_effect_and_shape_driven(self):
        self.assertEqual(
            c_orchestration_boundary(
                {"callees": [{"name": "Compute"}], "loop_count": 0},
                {"direct_effects": {}},
            ),
            "THIN_CALL_WRAPPER",
        )
        self.assertEqual(
            c_orchestration_boundary(
                {"callees": [], "loop_count": 0},
                {"direct_effects": {"allocation": True}},
            ),
            "MEMORY_LIFECYCLE",
        )
        self.assertEqual(
            c_orchestration_boundary(
                {"callees": [], "loop_count": 0},
                {"direct_effects": {"io": True}},
            ),
            "FRAME_IO_ORCHESTRATION",
        )

    def test_frontier_attaches_hash_bound_multi_rtl_receipt(self):
        with tempfile.TemporaryDirectory() as directory:
            path = pathlib.Path(directory) / "matrix.json"
            path.write_text(json.dumps({
                "status": "PASS",
                "matrix_scope": "all",
                "profiles": 22,
                "candidate_count": 19,
                "comparison": "FULL_DECODED_FRAME_BYTE_FOR_BYTE_AND_SHA256",
                "modes": {
                    "C_ONLY": {"status": "PASS", "total_rtl_invocations": 0, "all_candidates_reached": True},
                    "SHADOW": {"status": "PASS", "total_rtl_invocations": 10, "all_candidates_reached": True},
                    "RTL_RETURN": {"status": "PASS", "total_rtl_invocations": 10, "all_candidates_reached": True},
                },
            }))
            frontier = {}
            attach_integration_receipt(frontier, path)
        self.assertEqual(frontier["multi_rtl_integration"]["status"], "PASS")
        self.assertEqual(frontier["multi_rtl_integration"]["candidate_count"], 19)
        self.assertEqual(
            frontier["multi_rtl_integration"]["modes"]["RTL_RETURN"]["total_rtl_invocations"],
            10,
        )

    def test_provisional_scan_accepts_only_full_matrix_pass_receipts(self):
        with tempfile.TemporaryDirectory() as directory:
            root = pathlib.Path(directory)
            for name, status, scope in (
                ("full", "PASS", "all"),
                ("smoke", "PASS", "smoke"),
                ("failed", "FAIL", "all"),
            ):
                candidate = root / name
                candidate.mkdir()
                (candidate / "verification-receipt.json").write_text(
                    json.dumps({
                        "status": status,
                        "matrix_scope": scope,
                    }),
                    encoding="utf-8",
                )
                (candidate / "provisional-contract.json").write_text(
                    json.dumps({
                        "contract_id": f"{name}_contract",
                        "function": {"name": f"Function_{name}"},
                        "semantics": {
                            "kind": "scalar_record_next_state",
                            "max_bits": None,
                            "window_bytes": 0,
                        },
                    }),
                    encoding="utf-8",
                )
            scanned = scan_provisional(root)

        self.assertEqual(set(scanned), {"Function_full"})
        self.assertEqual(scanned["Function_full"]["contract_id"], "full_contract")

    def test_runtime_frontier_and_transition_candidate_are_data_driven(self):
        stable_usr = "c:@F@StableLeaf"
        reader_usr = "c:@F@ReadTransition"
        coverage = {
            "coverage_phases": "decode",
            "decode_runs": [{"status": "PASS"}, {"status": "PASS"}],
            "functions": [
                {
                    "clang_usr": stable_usr,
                    "name": "StableLeaf",
                    "coverage_status": "EXECUTED",
                    "coverage": {"execution_count": 11},
                },
                {
                    "clang_usr": reader_usr,
                    "name": "ReadTransition",
                    "coverage_status": "EXECUTED",
                    "coverage": {"execution_count": 37},
                },
            ],
        }
        functions = {
            "functions": [
                {
                    "clang_usr": stable_usr,
                    "name": "StableLeaf",
                    "source_file": "codec.c",
                    "return_type": "int",
                    "pointer_parameters": [],
                    "callees": [],
                    "loop_count": 0,
                },
                {
                    "clang_usr": reader_usr,
                    "name": "ReadTransition",
                    "source_file": "codec.c",
                    "return_type": "int",
                    "pointer_parameters": [
                        {"name": "buf", "type": "unsigned char *", "mode": "READ_ONLY"},
                        {"name": "cursor", "type": "int *", "mode": "WRITES_THROUGH"},
                    ],
                    "callees": [],
                    "loop_count": 1,
                },
            ],
        }
        candidates = {
            "functions": [
                {
                    "clang_usr": stable_usr,
                    "role": "DUT",
                    "eligible": True,
                    "direct_effects": {},
                    "bounded_computation": True,
                },
                {
                    "clang_usr": reader_usr,
                    "role": "DUT",
                    "eligible": False,
                    "direct_effects": {"state_write": True},
                    "bounded_computation": False,
                },
            ],
        }
        manifest = {
            "components": [
                {
                    "function": "StableLeaf",
                    "contract_id": "stableleaf",
                    "status": "PASS",
                }
            ]
        }
        with tempfile.TemporaryDirectory() as directory:
            source_dir = pathlib.Path(directory)
            (source_dir / "codec.c").write_text(
                "int x = ReadTransition(4, buf, &cursor, 0);\n"
                "int y = ReadTransition(16, buf, &cursor, 1);\n",
                encoding="utf-8",
            )
            frontier = discover(
                coverage, functions, candidates, manifest, source_dir
            )

        self.assertEqual(frontier["summary"]["runtime_dut_functions"], 2)
        self.assertEqual(frontier["summary"]["runtime_dut_with_stable_rtl"], 1)
        self.assertEqual(frontier["summary"]["runtime_dut_missing_stable_rtl"], 1)
        selected = frontier["provisional_transition_candidates"]
        self.assertEqual(len(selected), 1)
        self.assertEqual(selected[0]["name"], "ReadTransition")
        self.assertEqual(selected[0]["literal_size_bound"]["maximum"], 16)
        self.assertEqual(selected[0]["window_bytes"], 3)

    def test_provisional_generator_uses_explicit_cursor_state_ports(self):
        selected = {
            "name": "ReadTransition",
            "clang_usr": "c:@F@ReadTransition",
            "selection_basis": "tool-selected shape",
            "execution_count": 37,
            "literal_size_bound": {"maximum": 16, "values": [4, 16]},
            "window_bytes": 3,
        }
        function = {
            "clang_usr": selected["clang_usr"],
            "name": selected["name"],
            "source_file": "codec.c",
            "line": 1,
            "end_line": 3,
            "return_type": "int",
            "parameters": [
                {"name": "width", "type": "int", "pointer": False},
                {"name": "stream", "type": "unsigned char *", "pointer": True},
                {"name": "cursor", "type": "int *", "pointer": True},
                {"name": "signed_mode", "type": "int", "pointer": False},
            ],
            "pointer_parameters": [
                {"name": "stream", "type": "unsigned char *", "mode": "READ_ONLY"},
                {"name": "cursor", "type": "int *", "mode": "WRITES_THROUGH"},
            ],
        }
        with tempfile.TemporaryDirectory() as directory:
            source_dir = pathlib.Path(directory)
            (source_dir / "codec.c").write_text(
                "int ReadTransition(int width, unsigned char *stream, int *cursor, int signed_mode) {\n"
                "  return 0;\n}\n",
                encoding="utf-8",
            )
            contract = build_contract(selected, function, source_dir)
        rtl = render_rtl(contract)
        self.assertEqual(contract["semantics"]["kind"], "bitstream_read_transition")
        self.assertEqual(
            contract["semantics"]["bindings"]["cursor_parameter"], "cursor"
        )
        self.assertIn("input  logic [31:0] bit_count", rtl)
        self.assertIn("output logic [31:0] bit_count_out", rtl)
        self.assertIn("bit_count_out = bit_count + {27'd0, size}", rtl)

    def test_transition_overlay_uses_rtl_cursor_as_real_state_in_rtl_return(self):
        selected = {
            "name": "ReadTransition",
            "clang_usr": "c:@F@ReadTransition",
            "selection_basis": "tool-selected shape",
            "execution_count": 37,
            "literal_size_bound": {"maximum": 16, "values": [4, 16]},
            "window_bytes": 3,
        }
        function = {
            "clang_usr": selected["clang_usr"],
            "name": selected["name"],
            "source_file": "codec.c",
            "line": 1,
            "end_line": 3,
            "return_type": "int",
            "parameters": [
                {"name": "width", "type": "int", "pointer": False},
                {"name": "stream", "type": "unsigned char *", "pointer": True},
                {"name": "cursor", "type": "int *", "pointer": True},
                {"name": "signed_mode", "type": "int", "pointer": False},
            ],
            "pointer_parameters": [
                {"name": "stream", "type": "unsigned char *", "mode": "READ_ONLY"},
                {"name": "cursor", "type": "int *", "mode": "WRITES_THROUGH"},
            ],
        }
        with tempfile.TemporaryDirectory() as directory:
            root = pathlib.Path(directory)
            source_dir = root / "source"
            source_dir.mkdir()
            (source_dir / "codec.c").write_text(
                "int ReadTransition(int width, unsigned char *stream, int *cursor, int signed_mode) {\n"
                "  return 0;\n}\n",
                encoding="utf-8",
            )
            contract = build_contract(selected, function, source_dir)
            paths = Agent(root, "test").write_overlay_sources(
                contract,
                source_dir,
                "readtransition_decode_transition",
                root / "candidate_01.sv",
            )
            overlay = paths["overlay"].read_text(encoding="utf-8")

        self.assertIn("int dsc_cicd_c_cursor = dsc_cicd_cursor_before", overlay)
        self.assertIn("ReadTransition_original(width, stream, &dsc_cicd_c_cursor, signed_mode)", overlay)
        self.assertIn("*cursor = dsc_cicd_rtl_cursor", overlay)
        self.assertIn("DSC_CICD_OVERLAY_METRICS", overlay)
        self.assertTrue(
            paths["composition"]["rtl_return_controls_cursor_in_rtl_return"]
        )

    def test_fifo_transition_generator_exposes_mutated_fifo_state(self):
        selected = {
            "name": "ReadFifo",
            "clang_usr": "c:@F@ReadFifo",
            "selection_basis": "tool-selected FIFO shape",
            "execution_count": 101,
            "semantics_kind": "fifo_read_transition",
            "literal_size_bound": {"maximum": 32, "values": [8, 32]},
            "window_bytes": 5,
        }
        function = {
            "clang_usr": selected["clang_usr"],
            "name": selected["name"],
            "source_file": "fifo.c",
            "line": 1,
            "end_line": 3,
            "return_type": "int",
            "parameters": [
                {"name": "queue", "type": "fifo_t *", "pointer": True},
                {"name": "count", "type": "int", "pointer": False},
                {"name": "signed_mode", "type": "int", "pointer": False},
            ],
            "pointer_parameters": [
                {"name": "queue", "type": "fifo_t *", "mode": "WRITES_THROUGH"},
            ],
        }
        with tempfile.TemporaryDirectory() as directory:
            root = pathlib.Path(directory)
            source_dir = root / "source"
            source_dir.mkdir()
            (source_dir / "fifo.c").write_text(
                "int ReadFifo(fifo_t *queue, int count, int signed_mode) {\n"
                "  return 0;\n}\n",
                encoding="utf-8",
            )
            contract = build_contract(selected, function, source_dir)
            paths = Agent(root, "test").write_overlay_sources(
                contract,
                source_dir,
                "readfifo_decode_transition",
                root / "candidate_01.sv",
            )
            overlay = paths["overlay"].read_text(encoding="utf-8")
        rtl = render_rtl(contract)
        self.assertEqual(contract["semantics"]["kind"], "fifo_read_transition")
        self.assertIn("output logic [31:0] fullness_out", rtl)
        self.assertIn("output logic [31:0] read_ptr_out", rtl)
        self.assertIn("if (nbits >= 32)", rtl)
        self.assertIn("fifo_t dsc_cicd_c_fifo = *queue", overlay)
        self.assertIn("queue->fullness = dsc_cicd_rtl_fullness", overlay)
        self.assertTrue(
            paths["composition"]["rtl_return_controls_fifo_state_in_rtl_return"]
        )

    def test_verified_fifo_callee_unlocks_composed_accounting_transition(self):
        usr = "c:@F@AccountRead"
        coverage = {
            "coverage_phases": "decode",
            "decode_runs": [{"status": "PASS"}],
            "functions": [{
                "clang_usr": usr,
                "name": "AccountRead",
                "coverage_status": "EXECUTED",
                "coverage": {"execution_count": 211},
            }],
        }
        function = {
            "clang_usr": usr,
            "name": "AccountRead",
            "source_file": "mux.c",
            "line": 1,
            "end_line": 4,
            "return_type": "int",
            "parameters": [
                {"name": "cfg", "type": "dsc_cfg_t *", "pointer": True},
                {"name": "state", "type": "dsc_state_t *", "pointer": True},
                {"name": "channel", "type": "int", "pointer": False},
                {"name": "count", "type": "int", "pointer": False},
                {"name": "signed_mode", "type": "int", "pointer": False},
                {"name": "buf", "type": "unsigned char *", "pointer": True},
            ],
            "pointer_parameters": [
                {"name": "cfg", "type": "dsc_cfg_t *", "mode": "READ_ONLY"},
                {"name": "state", "type": "dsc_state_t *", "mode": "UNKNOWN"},
                {"name": "buf", "type": "unsigned char *", "mode": "READ_ONLY"},
            ],
            "callees": [{"name": "QueueRead", "clang_usr": "c:@F@QueueRead"}],
            "loop_count": 0,
            "fields_write": [{
                "record": "dsc_state_t", "name": "bitsSeen", "type": "int",
            }],
            "fields_read": [{
                "record": "dsc_state_t", "name": "queues", "type": "fifo_t[4]",
            }],
            "effects": {
                "assert": False,
                "file_io": False,
                "indirect_call": False,
                "logging": False,
                "malloc": False,
            },
        }
        functions = {"functions": [function]}
        candidates = {"functions": [{
            "clang_usr": usr,
            "role": "DUT",
            "eligible": False,
            "direct_effects": {"state_write": True},
            "bounded_computation": False,
        }]}
        verified = {
            "QueueRead": {
                "contract_id": "queue_read_transition",
                "semantics_kind": "fifo_read_transition",
                "max_bits": 64,
                "window_bytes": 9,
            }
        }
        with tempfile.TemporaryDirectory() as directory:
            root = pathlib.Path(directory)
            source_dir = root / "source"
            source_dir.mkdir()
            (source_dir / "mux.c").write_text(
                "int AccountRead(dsc_cfg_t *cfg, dsc_state_t *state, int channel, "
                "int count, int signed_mode, unsigned char *buf) {\n"
                "  state->bitsSeen += count;\n"
                "  return QueueRead(&state->queues[channel], count, signed_mode);\n"
                "}\n",
                encoding="utf-8",
            )
            frontier = discover(
                coverage, functions, candidates, {"components": []}, source_dir,
                verified,
            )
            selected = frontier["provisional_transition_candidates"]
            self.assertEqual(len(selected), 1)
            self.assertEqual(selected[0]["name"], "AccountRead")
            self.assertEqual(
                selected[0]["semantics_kind"],
                "fifo_read_accounting_transition",
            )
            contract = build_contract(selected[0], function, source_dir)
            paths = Agent(root, "test").write_overlay_sources(
                contract,
                source_dir,
                contract["contract_id"],
                root / "candidate_01.sv",
            )
            overlay = paths["overlay"].read_text(encoding="utf-8")
        rtl = render_rtl(contract)
        self.assertEqual(
            contract["semantics"]["bindings"]["state_counter_field"],
            "bitsSeen",
        )
        self.assertIn("output logic signed [31:0] bit_count_out", rtl)
        self.assertIn("bit_count_out = bit_count +", rtl)
        self.assertIn("dsc_state_t dsc_cicd_c_state = *state", overlay)
        self.assertIn("state->bitsSeen = dsc_cicd_rtl_bit_count", overlay)
        self.assertIn("state->queues[channel]", overlay)
        self.assertTrue(
            paths["composition"][
                "rtl_return_controls_composed_state_in_rtl_return"
            ]
        )

    def test_fifo_write_transition_exposes_memory_window_and_scalar_state(self):
        selected = {
            "name": "QueueWrite",
            "clang_usr": "c:@F@QueueWrite",
            "selection_basis": "tool-selected FIFO write shape",
            "execution_count": 307,
            "semantics_kind": "fifo_write_transition",
            "literal_size_bound": {"maximum": 32, "values": [8, 32]},
            "provisional_max_bits": 32,
            "window_bytes": 5,
        }
        function = {
            "clang_usr": selected["clang_usr"],
            "name": selected["name"],
            "source_file": "fifo.c",
            "line": 1,
            "end_line": 4,
            "return_type": "void",
            "parameters": [
                {"name": "queue", "type": "fifo_t *", "pointer": True},
                {"name": "payload", "type": "unsigned int", "pointer": False},
                {"name": "count", "type": "int", "pointer": False},
            ],
            "pointer_parameters": [{
                "name": "queue", "type": "fifo_t *", "mode": "WRITES_THROUGH",
            }],
            "fields_read": [
                {"record": "fifo_s", "name": "fill", "type": "int", "context": "condition"},
                {"record": "fifo_s", "name": "fill", "type": "int", "context": "condition"},
                {"record": "fifo_s", "name": "fill", "type": "int", "context": "expression"},
                {"record": "fifo_s", "name": "peak", "type": "int", "context": "condition"},
                {"record": "fifo_s", "name": "capacity", "type": "int", "context": "condition"},
                {"record": "fifo_s", "name": "capacity", "type": "int", "context": "condition"},
                {"record": "fifo_s", "name": "cursor", "type": "int", "context": "array_index"},
                {"record": "fifo_s", "name": "cursor", "type": "int", "context": "expression"},
            ],
            "fields_write": [
                {"record": "fifo_s", "name": "bytes", "type": "unsigned char *"},
                {"record": "fifo_s", "name": "bytes", "type": "unsigned char *"},
                {"record": "fifo_s", "name": "fill", "type": "int"},
                {"record": "fifo_s", "name": "cursor", "type": "int"},
                {"record": "fifo_s", "name": "cursor", "type": "int"},
                {"record": "fifo_s", "name": "peak", "type": "int"},
            ],
        }
        with tempfile.TemporaryDirectory() as directory:
            root = pathlib.Path(directory)
            source_dir = root / "source"
            source_dir.mkdir()
            (source_dir / "fifo.c").write_text(
                "void QueueWrite(fifo_t *queue, unsigned int payload, int count) {\n"
                "  queue->fill += count;\n"
                "  queue->cursor += count;\n"
                "}\n",
                encoding="utf-8",
            )
            contract = build_contract(selected, function, source_dir)
            paths = Agent(root, "test").write_overlay_sources(
                contract,
                source_dir,
                contract["contract_id"],
                root / "candidate_01.sv",
            )
            overlay = paths["overlay"].read_text(encoding="utf-8")
        rtl = render_rtl(contract)
        self.assertEqual(contract["semantics"]["kind"], "fifo_write_transition")
        self.assertEqual(
            contract["semantics"]["bindings"]["write_ptr_field"], "cursor"
        )
        self.assertIn("output logic [7:0] byte_4_out", rtl)
        self.assertIn("window_out_i[39 - int'(write_ptr[2:0]) - i]", rtl)
        self.assertIn("unsigned char dsc_cicd_merged[5]", overlay)
        self.assertIn("queue->bytes[dsc_cicd_index[i]] = dsc_cicd_merged[i]", overlay)
        self.assertTrue(
            paths["composition"][
                "rtl_return_controls_fifo_memory_and_state_in_rtl_return"
            ]
        )

    def test_scalar_record_transition_freezes_all_written_state_outputs(self):
        config_fields = [
            "bits_per_pixel", "final_offset", "first_line_bpg_ofs",
            "initial_scale_value", "initial_xmit_delay", "nfl_bpg_offset",
            "nsl_bpg_offset", "scale_decrement_interval",
            "scale_increment_interval", "second_line_bpg_ofs",
            "second_line_ofs_adj", "slice_bpg_offset",
        ]
        state_inputs = [
            "currentScale", "pixelCount", "pixelsInGroup", "prevPixelCount",
            "rcOffsetClampEnable", "rcXformOffset", "scaleAdjustCounter",
            "scaleIncrementStart", "secondOffsetApplied", "throttleFrac",
        ]
        state_outputs = [
            "currentScale", "prevPixelCount", "rcOffsetClampEnable",
            "rcXformOffset", "scaleAdjustCounter", "scaleIncrementStart",
            "secondOffsetApplied", "throttleFrac",
        ]
        selected = {
            "name": "RateStep",
            "clang_usr": "c:@F@RateStep",
            "selection_basis": "tool-selected scalar record shape",
            "execution_count": 73,
            "semantics_kind": "scalar_record_next_state",
            "literal_size_bound": {"evidence": "loop-free", "maximum": None},
            "window_bytes": 0,
        }
        function = {
            "clang_usr": selected["clang_usr"],
            "name": selected["name"],
            "source_file": "rate.c",
            "line": 1,
            "end_line": 3,
            "return_type": "void",
            "parameters": [
                {"name": "cfg", "type": "dsc_cfg_t *", "pointer": True},
                {"name": "state", "type": "dsc_state_t *", "pointer": True},
                {"name": "line", "type": "int", "pointer": False},
                {"name": "group", "type": "int", "pointer": False},
                {"name": "scale", "type": "int *", "pointer": True},
                {"name": "offset", "type": "int *", "pointer": True},
            ],
            "pointer_parameters": [
                {"name": "cfg", "type": "dsc_cfg_t *", "mode": "READ_ONLY"},
                {"name": "state", "type": "dsc_state_t *", "mode": "WRITES_THROUGH"},
                {"name": "scale", "type": "int *", "mode": "WRITES_THROUGH"},
                {"name": "offset", "type": "int *", "mode": "WRITES_THROUGH"},
            ],
            "fields_read": [
                *[
                    {"record": "dsc_cfg_t", "name": field, "type": "int"}
                    for field in config_fields
                ],
                *[
                    {"record": "dsc_state_t", "name": field, "type": "int"}
                    for field in state_inputs
                ],
            ],
            "fields_write": [
                {"record": "dsc_state_t", "name": field, "type": "int"}
                for field in state_outputs
            ],
        }
        with tempfile.TemporaryDirectory() as directory:
            root = pathlib.Path(directory)
            source_dir = root / "source"
            source_dir.mkdir()
            (source_dir / "dsc_types.h").write_text(
                "#define OFFSET_FRACTIONAL_BITS 11\n"
                "#define RC_SCALE_BINARY_POINT 3\n",
                encoding="utf-8",
            )
            (source_dir / "rate.c").write_text(
                "void RateStep(dsc_cfg_t *cfg, dsc_state_t *state, int line, "
                "int group, int *scale, int *offset) {\n"
                "  *scale = state->currentScale;\n"
                "}\n",
                encoding="utf-8",
            )
            contract = build_contract(selected, function, source_dir)
            paths = Agent(root, "test").write_overlay_sources(
                contract,
                source_dir,
                contract["contract_id"],
                root / "candidate_01.sv",
            )
            overlay = paths["overlay"].read_text(encoding="utf-8")
        rtl = render_rtl(contract)
        self.assertEqual(contract["semantics"]["constants"]["offset_fractional_bits"], 11)
        self.assertIn("state_currentscale_out", contract["semantics"]["bindings"]["state_output_ports"].values())
        self.assertIn("increment_i", rtl)
        self.assertIn("state->currentScale = dsc_cicd_rtl_state_currentscale_out", overlay)
        self.assertIn("RateStep_original(cfg, &dsc_cicd_c_state", overlay)
        self.assertTrue(
            paths["composition"][
                "rtl_return_controls_scalar_record_state_in_rtl_return"
            ]
        )

    def test_sampled_lookup_transition_resolves_pointer_taps_in_adapter(self):
        selected = {
            "name": "LookupWords",
            "clang_usr": "c:@F@LookupWords",
            "selection_basis": "tool-selected sampled lookup shape",
            "execution_count": 901,
            "semantics_kind": "sampled_lookup_transition",
            "literal_size_bound": {"evidence": "fixed extent", "maximum": None},
            "window_bytes": 0,
        }
        function = {
            "clang_usr": selected["clang_usr"],
            "name": selected["name"],
            "source_file": "lookup.c",
            "line": 1,
            "end_line": 3,
            "return_type": "void",
            "parameters": [
                {"name": "cfg", "type": "dsc_cfg_t *", "pointer": True},
                {"name": "state", "type": "dsc_state_t *", "pointer": True},
                {"name": "entry_id", "type": "int", "pointer": False},
                {"name": "words", "type": "unsigned int *", "pointer": True},
                {"name": "x", "type": "int", "pointer": False},
                {"name": "first", "type": "int", "pointer": False},
                {"name": "odd", "type": "int", "pointer": False},
            ],
            "pointer_parameters": [
                {"name": "cfg", "type": "dsc_cfg_t *", "mode": "READ_ONLY"},
                {"name": "state", "type": "dsc_state_t *", "mode": "READ_ONLY"},
                {"name": "words", "type": "unsigned int *", "mode": "WRITES_THROUGH"},
            ],
            "fields_read": [
                {"record": "dsc_cfg_t", "name": "native_420", "type": "int"},
                {"record": "dsc_cfg_t", "name": "native_422", "type": "int"},
                {"record": "dsc_state_t", "name": "history", "type": "dsc_history_t"},
                {"record": "dsc_state_t", "name": "numComponents", "type": "int"},
                {"record": "dsc_state_t", "name": "pixelsInGroup", "type": "int"},
                {"record": "dsc_state_t", "name": "prevLine", "type": "int *[5]"},
                {"record": "dsc_state_t", "name": "sliceWidth", "type": "int"},
                {"record": "dsc_history_t", "name": "pixels", "type": "unsigned int *[4]"},
            ],
        }
        with tempfile.TemporaryDirectory() as directory:
            root = pathlib.Path(directory)
            source_dir = root / "source"
            source_dir.mkdir()
            (source_dir / "dsc_types.h").write_text(
                "#define ICH_BITS 5\n"
                "#define ICH_PIXELS_ABOVE 7\n"
                "#define PADDING_LEFT 5\n"
                "#define NUM_COMPONENTS 4\n",
                encoding="utf-8",
            )
            (source_dir / "lookup.c").write_text(
                "void LookupWords(dsc_cfg_t *cfg, dsc_state_t *state, int entry_id, "
                "unsigned int *words, int x, int first, int odd) {\n"
                "  words[0] = 0;\n"
                "}\n",
                encoding="utf-8",
            )
            contract = build_contract(selected, function, source_dir)
            paths = Agent(root, "test").write_overlay_sources(
                contract,
                source_dir,
                contract["contract_id"],
                root / "candidate_01.sv",
            )
            overlay = paths["overlay"].read_text(encoding="utf-8")
            bridge = paths["bridge"].read_text(encoding="utf-8")
        rtl = render_rtl(contract)
        self.assertIn("input logic [4:0] entry", rtl)
        self.assertIn("entry >= 25", rtl)
        self.assertIn("state->history.pixels[i][entry_id]", overlay)
        self.assertIn("state->prevLine[i][dsc_cicd_index + 1]", overlay)
        self.assertIn("static Vlookupwords_decode_transition dut", bridge)
        self.assertTrue(
            paths["composition"][
                "rtl_return_controls_output_buffer_in_rtl_return"
            ]
        )

    def test_scalar_record_memory_transition_replaces_state_and_indexed_write(self):
        usr = "c:@F@RemoveChunkBits"
        config_fields = ["bits_per_pixel", "chunk_size", "vbr_enable"]
        state_read_fields = [
            "bitsClamped", "bpgFracAccum", "chunkPixelTimes", "isEncoder",
            "numBitsChunk", "sliceWidth",
        ]
        state_output_fields = [
            "bitsClamped", "bpgFracAccum", "bufferFullness", "chunkCount",
            "chunkPixelTimes", "numBitsChunk",
        ]
        function = {
            "clang_usr": usr,
            "name": "RemoveChunkBits",
            "source_file": "codec.c",
            "line": 1,
            "end_line": 3,
            "return_type": "void",
            "parameters": [
                {"name": "cfg", "type": "dsc_cfg_t *", "pointer": True},
                {"name": "state", "type": "dsc_state_t *", "pointer": True},
            ],
            "pointer_parameters": [
                {"name": "cfg", "type": "dsc_cfg_t *", "mode": "READ_ONLY"},
                {
                    "name": "state", "type": "dsc_state_t *",
                    "mode": "WRITES_THROUGH",
                },
            ],
            "fields_read": [
                *[
                    {"record": "dsc_cfg_t", "name": field, "type": "int"}
                    for field in config_fields
                ],
                *[
                    {"record": "dsc_state_t", "name": field, "type": "int"}
                    for field in state_read_fields
                ],
            ],
            "fields_write": [
                *[
                    {"record": "dsc_state_t", "name": field, "type": "int"}
                    for field in state_output_fields
                ],
                {
                    "record": "dsc_state_t", "name": "chunkSizes",
                    "type": "int *",
                },
            ],
            "callees": [],
            "loop_count": 0,
            "effects": {},
        }
        coverage = {
            "coverage_phases": "decode",
            "decode_runs": [{"status": "PASS"}],
            "functions": [{
                "clang_usr": usr,
                "name": "RemoveChunkBits",
                "coverage_status": "EXECUTED",
                "coverage": {"execution_count": 386271},
            }],
        }
        candidates = {"functions": [{
            "clang_usr": usr,
            "role": "DUT",
            "eligible": False,
            "direct_effects": {"state_write": True},
            "bounded_computation": True,
        }]}
        with tempfile.TemporaryDirectory() as directory:
            root = pathlib.Path(directory)
            source_dir = root / "source"
            source_dir.mkdir()
            (source_dir / "codec.c").write_text(
                "void RemoveChunkBits(dsc_cfg_t *cfg, dsc_state_t *state) {\n"
                "  state->chunkSizes[state->chunkCount] = 1;\n"
                "}\n",
                encoding="utf-8",
            )
            frontier = discover(
                coverage,
                {"functions": [function]},
                candidates,
                {"components": []},
                source_dir,
            )
            selected = frontier["provisional_transition_candidates"][0]
            contract = build_contract(selected, function, source_dir)
            paths = Agent(root, "test").write_overlay_sources(
                contract,
                source_dir,
                contract["contract_id"],
                root / "candidate_01.sv",
            )
            overlay = paths["overlay"].read_text(encoding="utf-8")
            bridge = paths["bridge"].read_text(encoding="utf-8")

        rtl = render_rtl(contract)
        self.assertEqual(selected["semantics_kind"], "scalar_record_memory_transition")
        self.assertIn("state_bufferfullness", contract["semantics"]["bindings"]["state_input_ports"].values())
        self.assertIn("chunk_write_enable = 1'b1", rtl)
        self.assertIn("removal_bits_i", rtl)
        self.assertIn("RemoveChunkBits_original(cfg, &dsc_cicd_c_state)", overlay)
        self.assertIn("dsc_cicd_prior_write_value", overlay)
        self.assertIn("state->chunkSizes[dsc_cicd_c_write_index]", overlay)
        self.assertIn("static Vremovechunkbits_decode_transition dut", bridge)
        self.assertTrue(
            paths["composition"][
                "rtl_return_controls_scalar_and_indexed_memory_state_in_rtl_return"
            ]
        )

    def test_bounded_mux_refill_transition_uses_private_complete_fifo_images(self):
        usr = "c:@F@RefillMuxGroup"
        function = {
            "clang_usr": usr,
            "name": "RefillMuxGroup",
            "source_file": "multiplex.c",
            "line": 1,
            "end_line": 8,
            "return_type": "void",
            "parameters": [
                {"name": "cfg", "type": "dsc_cfg_t *", "pointer": True},
                {"name": "state", "type": "dsc_state_t *", "pointer": True},
                {"name": "buf", "type": "unsigned char *", "pointer": True},
            ],
            "pointer_parameters": [
                {"name": "cfg", "type": "dsc_cfg_t *", "mode": "READ_ONLY"},
                {"name": "state", "type": "dsc_state_t *", "mode": "UNKNOWN"},
                {"name": "buf", "type": "unsigned char *", "mode": "UNKNOWN"},
            ],
            "fields_read": [
                {"record": "dsc_cfg_t", "name": "mux_word_size", "type": "int"},
                {"record": "dsc_state_t", "name": "maxSeSize", "type": "int[4]"},
                {"record": "dsc_state_t", "name": "numSsps", "type": "int"},
                {"record": "dsc_state_t", "name": "postMuxNumBits", "type": "int"},
                {"record": "dsc_state_t", "name": "shifter", "type": "fifo_t[4]"},
                {"record": "fifo_s", "name": "fullness", "type": "int"},
            ],
            "fields_write": [],
            "callees": [
                {"name": "ReadStreamBits"},
                {"name": "WriteFifoBits"},
            ],
            "loop_count": 2,
            "effects": {},
        }
        coverage = {
            "coverage_phases": "decode",
            "decode_runs": [{"status": "PASS"}],
            "functions": [{
                "clang_usr": usr,
                "name": "RefillMuxGroup",
                "coverage_status": "EXECUTED",
                "coverage": {"execution_count": 131328},
            }],
        }
        candidates = {"functions": [{
            "clang_usr": usr,
            "role": "DUT",
            "eligible": False,
            "direct_effects": {},
            "bounded_computation": False,
        }]}
        provisional = {
            "ReadStreamBits": {"semantics_kind": "bitstream_read_transition"},
            "WriteFifoBits": {"semantics_kind": "fifo_write_transition"},
        }
        with tempfile.TemporaryDirectory() as directory:
            root = pathlib.Path(directory)
            source_dir = root / "source"
            source_dir.mkdir()
            (source_dir / "dsc_types.h").write_text(
                "#define MAX_NUM_SSPS 4\n",
                encoding="utf-8",
            )
            (source_dir / "multiplex.c").write_text(
                "void RefillMuxGroup(dsc_cfg_t *cfg, dsc_state_t *state, "
                "unsigned char *buf) {\n"
                "  for (int i=0;i<state->numSsps;i++) {\n"
                "    for (int j=0;j<cfg->mux_word_size/8;j++) {}\n"
                "  }\n"
                "}\n",
                encoding="utf-8",
            )
            (source_dir / "config.c").write_text(
                "void f(void) { cfg.mux_word_size = 48; cfg.mux_word_size = 64; "
                "cfg.bits_per_component = 16; }\n",
                encoding="utf-8",
            )
            frontier = discover(
                coverage,
                {"functions": [function]},
                candidates,
                {"components": []},
                source_dir,
                provisional,
            )
            selected = frontier["provisional_transition_candidates"][0]
            contract = build_contract(selected, function, source_dir)
            paths = Agent(root, "test").write_overlay_sources(
                contract,
                source_dir,
                contract["contract_id"],
                root / "candidate_01.sv",
            )
            overlay = paths["overlay"].read_text(encoding="utf-8")
            bridge = paths["bridge"].read_text(encoding="utf-8")
            abi = paths["abi"].read_text(encoding="utf-8")

        rtl = render_rtl(contract)
        self.assertEqual(selected["semantics_kind"], "bounded_mux_refill_transition")
        self.assertEqual(contract["semantics"]["constants"]["max_fifo_bytes"], 17)
        self.assertIn("fifo_0_byte_16_out", rtl)
        self.assertIn("domain_valid", rtl)
        self.assertIn("dsc_cicd_c_data", overlay)
        self.assertIn("dsc_cicd_c_state.shifter[lane].data = dsc_cicd_c_data[lane]", overlay)
        self.assertIn("DSC_CICD_FIFO_BYTES 17", abi)
        self.assertIn("dut.fifo_3_byte_16", bridge)
        self.assertTrue(
            paths["composition"][
                "rtl_return_controls_cursor_and_complete_fifo_snapshots"
            ]
        )

    def test_bounded_line_write_transition_reconstructs_rtl_line_writes(self):
        usr = "c:@F@RestoreHistoryPixels"
        function = {
            "clang_usr": usr,
            "name": "RestoreHistoryPixels",
            "source_file": "codec.c",
            "line": 1,
            "end_line": 9,
            "return_type": "void",
            "parameters": [
                {"name": "cfg", "type": "dsc_cfg_t *", "pointer": True},
                {"name": "state", "type": "dsc_state_t *", "pointer": True},
                {"name": "line", "type": "int **", "pointer": True},
            ],
            "pointer_parameters": [
                {"name": "cfg", "type": "dsc_cfg_t *", "mode": "READ_ONLY"},
                {"name": "state", "type": "dsc_state_t *", "mode": "READ_ONLY"},
                {"name": "line", "type": "int **", "mode": "WRITES_THROUGH"},
            ],
            "fields_read": [
                {"record": "dsc_state_t", "name": "hPos", "type": "int"},
                {"record": "dsc_state_t", "name": "ichIndicesInGroup", "type": "int"},
                {"record": "dsc_state_t", "name": "ichLookup", "type": "int[6]"},
                {"record": "dsc_state_t", "name": "ichPixels", "type": "unsigned int[6][4]"},
                {"record": "dsc_state_t", "name": "ichSelected", "type": "int"},
                {"record": "dsc_state_t", "name": "numComponents", "type": "int"},
                {"record": "dsc_state_t", "name": "pixelsInGroup", "type": "int"},
            ],
            "fields_write": [],
            "globals_write": [],
            "callees": [{"name": "printf"}],
            "loop_count": 2,
            "effects": {"logging": True},
        }
        coverage = {
            "coverage_phases": "decode",
            "decode_runs": [{"status": "PASS"}],
            "functions": [{
                "clang_usr": usr,
                "name": "RestoreHistoryPixels",
                "coverage_status": "EXECUTED",
                "coverage": {"execution_count": 11704},
            }],
        }
        candidates = {"functions": [{
            "clang_usr": usr,
            "role": "DUT",
            "eligible": False,
            "direct_effects": {},
            "bounded_computation": False,
        }]}
        with tempfile.TemporaryDirectory() as directory:
            root = pathlib.Path(directory)
            source_dir = root / "source"
            source_dir.mkdir()
            (source_dir / "dsc_types.h").write_text(
                "#define MAX_PIXELS_PER_GROUP 6\n"
                "#define NUM_COMPONENTS 4\n"
                "#define PADDING_LEFT 5\n"
                "#define ICH_BITS 5\n",
                encoding="utf-8",
            )
            (source_dir / "codec.c").write_text(
                "void RestoreHistoryPixels(dsc_cfg_t *cfg, dsc_state_t *state, int **line) {\n"
                "  int start = state->hPos - state->pixelsInGroup + 1;\n"
                "  for (int pixel = 0; pixel < state->ichIndicesInGroup; ++pixel) {\n"
                "    if (state->ichSelected)\n"
                "      for (int component = 0; component < state->numComponents; ++component)\n"
                "        line[component][start + pixel + PADDING_LEFT] =\n"
                "            state->ichPixels[pixel][component];\n"
                "  }\n"
                "}\n",
                encoding="utf-8",
            )
            frontier = discover(
                coverage,
                {"functions": [function]},
                candidates,
                {"components": []},
                source_dir,
            )
            selected = frontier["provisional_transition_candidates"][0]
            contract = build_contract(selected, function, source_dir)
            paths = Agent(root, "test").write_overlay_sources(
                contract,
                source_dir,
                contract["contract_id"],
                root / "candidate_01.sv",
            )
            overlay = paths["overlay"].read_text(encoding="utf-8")
            bridge = paths["bridge"].read_text(encoding="utf-8")

        rtl = render_rtl(contract)
        self.assertEqual(selected["semantics_kind"], "bounded_line_write_transition")
        self.assertEqual(contract["semantics"]["constants"]["max_pixels"], 6)
        self.assertEqual(len(contract["interface"]["ports"]), 83)
        self.assertIn("write_index_5 = state_hpos - state_pixels_in_group + 32'sd11", rtl)
        self.assertIn("write_enable_5_3 = 1'b1", rtl)
        self.assertIn("RestoreHistoryPixels_original(cfg, state, line)", overlay)
        self.assertIn("line[component][dsc_cicd_index[pixel]] = dsc_cicd_prior", overlay)
        self.assertIn("line[component][dsc_cicd_rtl_output.index[pixel]]", overlay)
        self.assertIn("static Vrestorehistorypixels_decode_transition dut", bridge)
        self.assertTrue(
            paths["composition"][
                "rtl_return_controls_all_reconstructed_line_writes"
            ]
        )

    def test_verified_history_transitions_are_deterministic_and_private(self):
        repo_root = pathlib.Path(__file__).resolve().parents[1]
        cases = (
            (
                "selected-history-update-transition",
                "bounded_history_update_transition",
                171,
                "c_oracle_uses_private_history_memory",
                "dsc_cicd_c_state.history.valid = dsc_cicd_c_valid",
            ),
            (
                "selected-history-caller-transition",
                "bounded_history_caller_transition",
                176,
                "line_samples_are_read_only_and_guarded_by_update_condition",
                "if (dsc_cicd_previous_hpos >= 0)",
            ),
        )
        provisional = scan_provisional(repo_root / "rtl" / "decode-candidates")
        self.assertEqual(
            provisional["UpdateHistoryElement"]["semantics_kind"],
            "bounded_history_update_transition",
        )
        self.assertEqual(
            provisional["UpdateICHistory"]["semantics_kind"],
            "bounded_history_caller_transition",
        )

        for directory, semantics_kind, input_count, proof_key, overlay_text in cases:
            with self.subTest(directory=directory):
                artifact = repo_root / "rtl" / "decode-candidates" / directory
                contract = json.loads(
                    (artifact / "provisional-contract.json").read_text(
                        encoding="utf-8"
                    )
                )
                candidate = artifact / "candidate_01.sv"
                self.assertEqual(contract["semantics"]["kind"], semantics_kind)
                self.assertEqual(render_rtl(contract), candidate.read_text(encoding="utf-8"))
                self.assertEqual(
                    sum(
                        port["direction"] == "input"
                        for port in contract["interface"]["ports"]
                    ),
                    input_count,
                )
                self.assertEqual(
                    sum(
                        port["direction"] == "output"
                        for port in contract["interface"]["ports"]
                    ),
                    160,
                )
                with tempfile.TemporaryDirectory() as directory_path:
                    root = pathlib.Path(directory_path)
                    source_dir = root / "source"
                    source_dir.mkdir()
                    paths = Agent(root, "test").write_overlay_sources(
                        contract,
                        source_dir,
                        contract["contract_id"],
                        candidate,
                    )
                    overlay = paths["overlay"].read_text(encoding="utf-8")
                self.assertIn(overlay_text, overlay)
                self.assertIn("numComponents; ++component", overlay)
                self.assertTrue(paths["composition"][proof_key])
                self.assertTrue(
                    paths["composition"][
                        "inactive_component_planes_are_not_dereferenced_or_committed"
                    ]
                )

    def test_verified_vld_unit_is_deterministic_private_and_full_pass(self):
        repo_root = pathlib.Path(__file__).resolve().parents[1]
        artifact = (
            repo_root / "rtl" / "decode-candidates"
            / "selected-vld-unit-transition"
        )
        contract = json.loads(
            (artifact / "provisional-contract.json").read_text(encoding="utf-8")
        )
        candidate = artifact / "candidate_01.sv"
        receipt = json.loads(
            (artifact / "matrix-receipt.json").read_text(encoding="utf-8")
        )
        provisional = scan_provisional(repo_root / "rtl" / "decode-candidates")

        self.assertEqual(
            provisional["VLDUnit"]["semantics_kind"],
            "bounded_vld_unit_transition",
        )
        self.assertEqual(render_rtl(contract), candidate.read_text(encoding="utf-8"))
        self.assertEqual(
            sum(
                port["direction"] == "input"
                for port in contract["interface"]["ports"]
            ),
            81,
        )
        self.assertEqual(
            sum(
                port["direction"] == "output"
                for port in contract["interface"]["ports"]
            ),
            31,
        )
        self.assertEqual(
            {item["role"] for item in contract["dependencies"]},
            {
                "adjusted_prediction", "escape_size", "flatness_sent",
                "get_bits", "max_residual", "predict_size", "qp_mapping",
                "residual_size",
            },
        )

        with tempfile.TemporaryDirectory() as directory_path:
            root = pathlib.Path(directory_path)
            source_dir = root / "source"
            source_dir.mkdir()
            paths = Agent(root, "test").write_overlay_sources(
                contract,
                source_dir,
                contract["contract_id"],
                candidate,
            )
            overlay = paths["overlay"].read_text(encoding="utf-8")

        self.assertIn(
            "dsc_cicd_c_state.shifter[dsc_cicd_lane].data = "
            "dsc_cicd_c_fifo",
            overlay,
        )
        self.assertIn("dsc_cicd_c_residual", overlay)
        self.assertEqual(paths["composition"]["selected_fifo_snapshot_bytes"], 17)
        self.assertEqual(paths["composition"]["prefix_unroll_bound"], 17)
        self.assertEqual(len(paths["composition"]["rtl_bindings"]), 81)
        self.assertTrue(
            paths["composition"][
                "rtl_return_controls_complete_vld_write_footprint"
            ]
        )
        self.assertTrue(
            paths["composition"][
                "c_oracle_uses_private_state_fifo_and_residuals"
            ]
        )

        self.assertEqual(receipt["status"], "PASS")
        self.assertEqual(receipt["matrix_scope"], "all")
        self.assertEqual(receipt["decode"]["status"], "PASS")
        self.assertEqual(
            receipt["replacement_coverage"]["rtl_return_rtl_invocations"],
            404352,
        )
        for mode in ("SHADOW", "RTL_RETURN"):
            phase = receipt["decode"]["modes"][mode]
            self.assertEqual(phase["total_rtl_invocations"], 404352)
            self.assertEqual(
                sum(
                    scenario["overlay_metrics"]["mismatches"]
                    for scenario in phase["scenarios"]
                ),
                0,
            )

    def test_verified_vld_group_is_source_ordered_private_and_full_pass(self):
        repo_root = pathlib.Path(__file__).resolve().parents[1]
        artifact = (
            repo_root / "rtl" / "decode-candidates"
            / "selected-vld-group-transition"
        )
        contract = json.loads(
            (artifact / "provisional-contract.json").read_text(encoding="utf-8")
        )
        candidate = artifact / "candidate_01.sv"
        receipt = json.loads(
            (artifact / "matrix-receipt.json").read_text(encoding="utf-8")
        )
        provisional = scan_provisional(repo_root / "rtl" / "decode-candidates")

        self.assertEqual(
            provisional["VLDGroup"]["semantics_kind"],
            "bounded_vld_group_decode_transition",
        )
        self.assertEqual(render_rtl(contract), candidate.read_text(encoding="utf-8"))
        self.assertEqual(
            sum(
                port["direction"] == "input"
                for port in contract["interface"]["ports"]
            ),
            205,
        )
        self.assertEqual(
            sum(
                port["direction"] == "output"
                for port in contract["interface"]["ports"]
            ),
            136,
        )
        self.assertEqual(
            [item["role"] for item in contract["dependencies"]],
            ["mux_refill", "vld_unit"],
        )

        with tempfile.TemporaryDirectory() as directory_path:
            root = pathlib.Path(directory_path)
            source_dir = root / "source"
            source_dir.mkdir()
            paths = Agent(root, "test").write_overlay_sources(
                contract,
                source_dir,
                contract["contract_id"],
                candidate,
            )
            overlay = paths["overlay"].read_text(encoding="utf-8")

        self.assertIn("dsc_cicd_c_fifo[DSC_CICD_VLD_GROUP_UNITS]", overlay)
        self.assertIn("VLDGroup_original", overlay)
        self.assertEqual(len(paths["composition"]["rtl_bindings"]), 205)
        self.assertEqual(
            paths["composition"]["source_order_child_sequence"],
            [
                "ProcessGroupDec", "VLDUnit[0]", "VLDUnit[1]",
                "VLDUnit[2]", "VLDUnit[3]",
            ],
        )
        self.assertTrue(
            paths["composition"][
                "rtl_return_controls_complete_vld_group_write_footprint"
            ]
        )
        self.assertTrue(
            paths["composition"][
                "c_oracle_uses_private_state_and_four_fifo_images"
            ]
        )

        self.assertEqual(receipt["status"], "PASS")
        self.assertEqual(receipt["matrix_scope"], "all")
        for mode in ("SHADOW", "RTL_RETURN"):
            decode_mode = receipt["decode"]["modes"][mode]
            self.assertEqual(decode_mode["total_rtl_invocations"], 131328)
            self.assertEqual(
                sum(
                    scenario["overlay_metrics"]["mismatches"]
                    for scenario in decode_mode["scenarios"]
                ),
                0,
            )
            self.assertEqual(
                receipt["encode"]["modes"][mode]["total_rtl_invocations"],
                0,
            )

    def test_verified_raster_color_transforms_are_iterated_and_full_pass(self):
        repo_root = pathlib.Path(__file__).resolve().parents[1]
        provisional = scan_provisional(repo_root / "rtl" / "decode-candidates")
        cases = (
            (
                "rgb2ycocg", "rgb_to_ycocg",
                "selected-rgb-to-ycocg-transition",
            ),
            (
                "ycocg2rgb", "ycocg_to_rgb",
                "selected-ycocg-to-rgb-transition",
            ),
        )
        for function, direction, directory in cases:
            with self.subTest(function=function):
                artifact = repo_root / "rtl" / "decode-candidates" / directory
                contract = json.loads(
                    (artifact / "provisional-contract.json").read_text(
                        encoding="utf-8"
                    )
                )
                candidate = artifact / "candidate_01.sv"
                receipt = json.loads(
                    (artifact / "matrix-receipt.json").read_text(encoding="utf-8")
                )
                self.assertEqual(
                    provisional[function]["semantics_kind"],
                    "raster_color_transform_transition",
                )
                self.assertEqual(contract["semantics"]["bindings"]["direction"], direction)
                self.assertEqual(
                    render_rtl(contract), candidate.read_text(encoding="utf-8")
                )
                self.assertEqual(
                    sum(
                        port["direction"] == "input"
                        for port in contract["interface"]["ports"]
                    ),
                    4,
                )
                self.assertEqual(
                    sum(
                        port["direction"] == "output"
                        for port in contract["interface"]["ports"]
                    ),
                    4,
                )
                with tempfile.TemporaryDirectory() as directory_path:
                    root = pathlib.Path(directory_path)
                    source_dir = root / "source"
                    source_dir.mkdir()
                    paths = Agent(root, "test").write_overlay_sources(
                        contract,
                        source_dir,
                        contract["contract_id"],
                        candidate,
                    )
                    overlay = paths["overlay"].read_text(encoding="utf-8")
                self.assertIn("saved[position * 3", overlay)
                self.assertIn("dsc_cicd_rtl_invocations", overlay)
                self.assertEqual(len(paths["composition"]["rtl_bindings"]), 4)
                self.assertTrue(
                    paths["composition"][
                        "iteration_adapter_invokes_rtl_per_active_pixel"
                    ]
                )
                self.assertTrue(
                    paths["composition"][
                        "original_c_writes_are_saved_and_restored_before_commit"
                    ]
                )
                self.assertEqual(receipt["status"], "PASS")
                self.assertEqual(receipt["matrix_scope"], "all")
                for phase in ("decode", "encode"):
                    for mode in ("SHADOW", "RTL_RETURN"):
                        phase_mode = receipt[phase]["modes"][mode]
                        self.assertEqual(
                            phase_mode["total_rtl_invocations"], 269568
                        )
                        self.assertEqual(
                            sum(
                                scenario["overlay_metrics"]["mismatches"]
                                for scenario in phase_mode["scenarios"]
                            ),
                            0,
                        )

    def test_verified_block_predictor_is_deterministic_and_full_pass(self):
        repo_root = pathlib.Path(__file__).resolve().parents[1]
        artifact = (
            repo_root / "rtl" / "decode-candidates"
            / "selected-block-pred-search-transition"
        )
        contract = json.loads(
            (artifact / "provisional-contract.json").read_text(encoding="utf-8")
        )
        candidate = artifact / "candidate_01.sv"
        receipt = json.loads(
            (artifact / "matrix-receipt.json").read_text(encoding="utf-8")
        )
        provisional = scan_provisional(repo_root / "rtl" / "decode-candidates")

        self.assertEqual(
            provisional["BlockPredSearch"]["semantics_kind"],
            "bounded_block_pred_search_transition",
        )
        self.assertEqual(render_rtl(contract), candidate.read_text(encoding="utf-8"))
        self.assertEqual(
            sum(
                port["direction"] == "input"
                for port in contract["interface"]["ports"]
            ),
            235,
        )
        self.assertEqual(
            sum(
                port["direction"] == "output"
                for port in contract["interface"]["ports"]
            ),
            215,
        )
        self.assertEqual(
            contract["dependencies"][0]["role"], "block_sample_predict"
        )

        with tempfile.TemporaryDirectory() as directory_path:
            root = pathlib.Path(directory_path)
            source_dir = root / "source"
            source_dir.mkdir()
            paths = Agent(root, "test").write_overlay_sources(
                contract,
                source_dir,
                contract["contract_id"],
                candidate,
            )
            overlay = paths["overlay"].read_text(encoding="utf-8")

        self.assertIn("dsc_cicd_c_state = *dsc_state", overlay)
        self.assertIn(
            "prevLinePred[dsc_cicd_write_index] = "
            "(PRED_TYPE)dsc_cicd_prior_write",
            overlay,
        )
        self.assertEqual(len(paths["composition"]["rtl_bindings"]), 235)
        self.assertTrue(
            paths["composition"][
                "rtl_return_controls_complete_predictor_accumulators"
            ]
        )
        self.assertTrue(
            paths["composition"][
                "c_oracle_decision_write_is_restored_before_mode_commit"
            ]
        )
        self.assertTrue(
            paths["composition"][
                "inactive_candidate_line_taps_are_not_dereferenced"
            ]
        )

        self.assertEqual(receipt["status"], "PASS")
        self.assertEqual(receipt["matrix_scope"], "all")
        for phase_name in ("decode", "encode"):
            phase = receipt[phase_name]
            self.assertEqual(phase["status"], "PASS")
            for mode in ("SHADOW", "RTL_RETURN"):
                mode_receipt = phase["modes"][mode]
                self.assertEqual(mode_receipt["total_rtl_invocations"], 1213056)
                self.assertEqual(
                    sum(
                        scenario["overlay_metrics"]["mismatches"]
                        for scenario in mode_receipt["scenarios"]
                    ),
                    0,
                )

    def test_verified_prediction_decoder_is_deterministic_and_full_pass(self):
        repo_root = pathlib.Path(__file__).resolve().parents[1]
        artifact = (
            repo_root / "rtl" / "decode-candidates"
            / "selected-prediction-decode-transition"
        )
        contract = json.loads(
            (artifact / "provisional-contract.json").read_text(encoding="utf-8")
        )
        candidate = artifact / "candidate_01.sv"
        receipt = json.loads(
            (artifact / "matrix-receipt.json").read_text(encoding="utf-8")
        )
        provisional = scan_provisional(repo_root / "rtl" / "decode-candidates")

        self.assertEqual(
            provisional["PredictionLoop"]["semantics_kind"],
            "bounded_prediction_decode_transition",
        )
        self.assertEqual(render_rtl(contract), candidate.read_text(encoding="utf-8"))
        self.assertEqual(
            sum(
                port["direction"] == "input"
                for port in contract["interface"]["ports"]
            ),
            75,
        )
        self.assertEqual(
            sum(
                port["direction"] == "output"
                for port in contract["interface"]["ports"]
            ),
            17,
        )
        self.assertEqual(
            {item["role"] for item in contract["dependencies"]},
            {
                "max_residual", "midpoint", "qp_mapping", "quantize",
                "residual_size", "sample_predict",
            },
        )
        self.assertEqual(
            {
                item["role"]
                for item in contract["dependencies"]
                if item["active_in_decode_specialization"]
            },
            {"midpoint", "qp_mapping", "sample_predict"},
        )

        with tempfile.TemporaryDirectory() as directory_path:
            root = pathlib.Path(directory_path)
            source_dir = root / "source"
            source_dir.mkdir()
            paths = Agent(root, "test").write_overlay_sources(
                contract,
                source_dir,
                contract["contract_id"],
                candidate,
            )
            overlay = paths["overlay"].read_text(encoding="utf-8")

        self.assertIn("if (dsc_state->isEncoder != 0)", overlay)
        self.assertIn("PredictionLoop_original", overlay)
        self.assertEqual(len(paths["composition"]["rtl_bindings"]), 75)
        self.assertTrue(
            paths["composition"][
                "rtl_return_controls_complete_decoder_line_write_footprint"
            ]
        )
        self.assertTrue(
            paths["composition"][
                "c_oracle_uses_private_embedded_state_and_restored_line_writes"
            ]
        )
        self.assertTrue(
            paths["composition"]["encoder_calls_bypass_rtl_and_remain_original_c"]
        )

        self.assertEqual(receipt["status"], "PASS")
        self.assertEqual(receipt["matrix_scope"], "all")
        for mode in ("SHADOW", "RTL_RETURN"):
            decode_mode = receipt["decode"]["modes"][mode]
            self.assertEqual(decode_mode["total_rtl_invocations"], 393984)
            self.assertEqual(
                sum(
                    scenario["overlay_metrics"]["mismatches"]
                    for scenario in decode_mode["scenarios"]
                ),
                0,
            )
            self.assertEqual(
                receipt["encode"]["modes"][mode]["total_rtl_invocations"],
                0,
            )

    def test_verified_rate_control_decoder_is_deterministic_and_full_pass(self):
        repo_root = pathlib.Path(__file__).resolve().parents[1]
        artifact = (
            repo_root / "rtl" / "decode-candidates"
            / "selected-rate-control-decode-transition"
        )
        contract = json.loads(
            (artifact / "provisional-contract.json").read_text(encoding="utf-8")
        )
        candidate = artifact / "candidate_01.sv"
        receipt = json.loads(
            (artifact / "matrix-receipt.json").read_text(encoding="utf-8")
        )
        provisional = scan_provisional(repo_root / "rtl" / "decode-candidates")

        self.assertEqual(
            provisional["RateControl"]["semantics_kind"],
            "bounded_rate_control_decode_transition",
        )
        self.assertEqual(render_rtl(contract), candidate.read_text(encoding="utf-8"))
        self.assertEqual(
            sum(
                port["direction"] == "input"
                for port in contract["interface"]["ports"]
            ),
            114,
        )
        self.assertEqual(
            sum(
                port["direction"] == "output"
                for port in contract["interface"]["ports"]
            ),
            15,
        )
        self.assertEqual(contract["dependencies"][0]["role"], "remove_one_pixel_bits")
        self.assertTrue(
            contract["dependencies"][0][
                "memory_write_disabled_by_decoder_specialization"
            ]
        )

        with tempfile.TemporaryDirectory() as directory_path:
            root = pathlib.Path(directory_path)
            source_dir = root / "source"
            source_dir.mkdir()
            paths = Agent(root, "test").write_overlay_sources(
                contract,
                source_dir,
                contract["contract_id"],
                candidate,
            )
            overlay = paths["overlay"].read_text(encoding="utf-8")

        self.assertIn("dsc_state_t dsc_cicd_c_state = *dsc_state", overlay)
        self.assertIn("if (dsc_state->isEncoder != 0)", overlay)
        self.assertEqual(len(paths["composition"]["rtl_bindings"]), 114)
        self.assertTrue(
            paths["composition"][
                "three_remove_bits_stages_are_hash_bound_and_ordered"
            ]
        )
        self.assertTrue(
            paths["composition"][
                "rtl_return_controls_complete_rate_control_scalar_footprint"
            ]
        )
        self.assertTrue(
            paths["composition"]["decoder_specialization_has_no_chunk_memory_write"]
        )

        self.assertEqual(receipt["status"], "PASS")
        self.assertEqual(receipt["matrix_scope"], "all")
        for mode in ("SHADOW", "RTL_RETURN"):
            decode_mode = receipt["decode"]["modes"][mode]
            self.assertEqual(decode_mode["total_rtl_invocations"], 131328)
            self.assertEqual(
                sum(
                    scenario["overlay_metrics"]["mismatches"]
                    for scenario in decode_mode["scenarios"]
                ),
                0,
            )
            self.assertEqual(
                receipt["encode"]["modes"][mode]["total_rtl_invocations"],
                0,
            )


if __name__ == "__main__":
    unittest.main()
