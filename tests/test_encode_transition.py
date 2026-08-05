import json
import pathlib
import shutil
import subprocess
import tempfile
import unittest

from tools.cicd_agent import Agent
from tools.generate_encode_transition import (
    build_bitstream_write_contract,
    build_fifo_write_accounting_contract,
    discover_bitstream_write_candidates,
    discover_fifo_write_accounting_candidates,
    render_bitstream_write_rtl,
    render_fifo_write_accounting_rtl,
)


def fixture_documents(source_name: str = "writer.c"):
    parameters = [
        {"name": "payload", "type": "int", "pointer": False},
        {"name": "count", "type": "int", "pointer": False},
        {
            "name": "output",
            "type": "unsigned char *",
            "pointer": True,
        },
        {"name": "cursor", "type": "int *", "pointer": True},
    ]
    function = {
        "name": "EmitWindow",
        "clang_usr": "c:@F@EmitWindow",
        "source_file": source_name,
        "line": 1,
        "end_line": 12,
        "return_type": "void",
        "parameters": parameters,
        "pointer_parameters": [
            {
                "name": "output",
                "type": "unsigned char *",
                "mode": "WRITES_THROUGH",
            },
            {
                "name": "cursor",
                "type": "int *",
                "mode": "WRITES_THROUGH",
            },
        ],
        "loop_count": 1,
        "loops": [{"condition": "i >= 0"}],
        "fields_read": [],
        "fields_write": [],
        "globals_write": [],
    }
    return (
        {"functions": [function]},
        {
            "functions": [
                {
                    "name": "EmitWindow",
                    "clang_usr": "c:@F@EmitWindow",
                    "contributes_to_observable_output": True,
                    "direct_effects": {
                        "allocation": False,
                        "assertion": False,
                        "indirect_call": False,
                        "io": False,
                        "logging": True,
                        "state_write": True,
                    },
                }
            ]
        },
        {
            "functions": [
                {
                    "name": "EmitWindow",
                    "clang_usr": "c:@F@EmitWindow",
                    "coverage": {
                        "covered": True,
                        "execution_count": 123,
                    },
                }
            ]
        },
    )


class EncodeTransitionTests(unittest.TestCase):
    def test_discovers_bounded_writer_without_function_allowlist(self):
        source = """void EmitWindow(int payload, int count, unsigned char *output, int *cursor)
{
  int i, bit, index;
  if (count > 32)
    printf("too large\\n");
  for (i = count - 1; i >= 0; --i) {
    index = (*cursor) >> 3;
    bit = (payload >> i) & 1;
    output[index] |= bit;
    (*cursor)++;
  }
}
"""
        with tempfile.TemporaryDirectory() as directory:
            root = pathlib.Path(directory)
            (root / "writer.c").write_text(source, encoding="utf-8")
            functions, candidates, coverage = fixture_documents()
            matches = discover_bitstream_write_candidates(
                functions, candidates, coverage, root
            )
            self.assertEqual(len(matches), 1)
            selected = matches[0]
            self.assertEqual(selected["name"], "EmitWindow")
            self.assertEqual(selected["semantics_kind"], "bitstream_write_transition")
            self.assertEqual(selected["max_bits"], 32)
            self.assertEqual(selected["window_bytes"], 5)
            contract = build_bitstream_write_contract(selected, root)
        self.assertEqual(
            contract["contract_id"], "emitwindow_encode_transition"
        )
        self.assertEqual(
            contract["selection"]["encode_execution_count"], 123
        )
        self.assertEqual(
            contract["semantics"]["legal_size_values"], list(range(33))
        )

    def test_uncovered_shape_is_not_selected(self):
        source = """void EmitWindow(int payload, int count, unsigned char *output, int *cursor)
{
  int i;
  if (count > 32)
    printf("too large\\n");
  for (i = count - 1; i >= 0; --i) {
    output[(*cursor) >> 3] |= (payload >> i) & 1;
    (*cursor)++;
  }
}
"""
        with tempfile.TemporaryDirectory() as directory:
            root = pathlib.Path(directory)
            (root / "writer.c").write_text(source, encoding="utf-8")
            functions, candidates, coverage = fixture_documents()
            coverage["functions"][0]["coverage"]["covered"] = False
            matches = discover_bitstream_write_candidates(
                functions, candidates, coverage, root
            )
        self.assertEqual(matches, [])

    def test_rendered_rtl_and_adapter_expose_complete_next_state(self):
        source = """void EmitWindow(int payload, int count, unsigned char *output, int *cursor)
{
  int i, bit, index;
  if (count > 32)
    printf("too large\\n");
  for (i = count - 1; i >= 0; --i) {
    index = (*cursor) >> 3;
    bit = (payload >> i) & 1;
    output[index] |= bit;
    (*cursor)++;
  }
}
"""
        with tempfile.TemporaryDirectory() as directory:
            root = pathlib.Path(directory)
            (root / "writer.c").write_text(source, encoding="utf-8")
            functions, candidates, coverage = fixture_documents()
            selected = discover_bitstream_write_candidates(
                functions, candidates, coverage, root
            )[0]
            contract = build_bitstream_write_contract(selected, root)
            rtl = render_bitstream_write_rtl(contract)
            candidate = root / "candidate.sv"
            candidate.write_text(rtl, encoding="utf-8")
            paths = Agent(root, "test").write_overlay_sources(
                contract,
                root,
                contract["contract_id"],
                candidate,
            )
            overlay = paths["overlay"].read_text(encoding="utf-8")
            composition = paths["composition"]
            self.assertEqual(
                composition["adapter_kind"],
                "explicit_bitstream_write_state_transition",
            )
            self.assertTrue(
                composition["rtl_return_controls_output_memory_and_cursor"]
            )
            self.assertTrue(
                composition["c_oracle_uses_private_output_window"]
            )
            self.assertIn("dsc_cicd_c_bytes", overlay)
            self.assertIn("dsc_cicd_rtl_bytes", overlay)
            self.assertIn("*cursor = dsc_cicd_rtl_cursor", overlay)
            self.assertIn("byte_4_out", rtl)
            self.assertIn("bit_count_out", rtl)
            clang = shutil.which("clang")
            if clang:
                syntax = subprocess.run(
                    [
                        clang,
                        "-std=gnu99",
                        "-fsyntax-only",
                        str(paths["overlay"]),
                    ],
                    cwd=root,
                    text=True,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.STDOUT,
                    check=False,
                )
                self.assertEqual(syntax.returncode, 0, syntax.stdout)
            verilator = shutil.which("verilator")
            if verilator:
                lint = subprocess.run(
                    [
                        verilator,
                        "--lint-only",
                        "--Wno-fatal",
                        "--top-module",
                        contract["contract_id"],
                        str(candidate),
                    ],
                    cwd=root,
                    text=True,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.STDOUT,
                    check=False,
                )
                self.assertEqual(lint.returncode, 0, lint.stdout)

    def test_discovers_and_binds_fifo_write_accounting_caller(self):
        source = """void PushCount(dsc_cfg_t *cfg, dsc_state_t *state, int lane, int payload, int count)
{
  WriteFifo(&(state->lanes[lane]), payload, count);
  state->bits += count;
}
"""
        function = {
            "name": "PushCount",
            "clang_usr": "c:@F@PushCount",
            "source_file": "parent.c",
            "line": 1,
            "end_line": 5,
            "return_type": "void",
            "parameters": [
                {"name": "cfg", "type": "dsc_cfg_t *", "pointer": True},
                {
                    "name": "state",
                    "type": "dsc_state_t *",
                    "pointer": True,
                },
                {"name": "lane", "type": "int", "pointer": False},
                {"name": "payload", "type": "int", "pointer": False},
                {"name": "count", "type": "int", "pointer": False},
            ],
            "pointer_parameters": [
                {
                    "name": "cfg",
                    "type": "dsc_cfg_t *",
                    "mode": "READ_ONLY",
                },
                {
                    "name": "state",
                    "type": "dsc_state_t *",
                    "mode": "WRITES_THROUGH",
                },
            ],
            "loop_count": 0,
            "callees": [
                {"name": "WriteFifo", "clang_usr": "c:@F@WriteFifo"}
            ],
            "fields_read": [
                {
                    "record": "dsc_state_t",
                    "name": "lanes",
                    "type": "fifo_t[4]",
                }
            ],
            "fields_write": [
                {
                    "record": "dsc_state_t",
                    "name": "bits",
                    "type": "int",
                }
            ],
            "globals_write": [],
        }
        functions = {"functions": [function]}
        candidates = {
            "functions": [
                {
                    "clang_usr": "c:@F@PushCount",
                    "name": "PushCount",
                    "contributes_to_observable_output": True,
                    "direct_effects": {
                        "allocation": False,
                        "assertion": False,
                        "indirect_call": False,
                        "io": False,
                        "logging": False,
                    },
                }
            ]
        }
        coverage = {
            "functions": [
                {
                    "clang_usr": "c:@F@PushCount",
                    "name": "PushCount",
                    "coverage": {
                        "covered": True,
                        "execution_count": 456,
                    },
                }
            ]
        }
        child_contract = {
            "contract_id": "writefifo_transition",
            "function": {"name": "WriteFifo"},
            "semantics": {
                "kind": "fifo_write_transition",
                "max_bits": 32,
                "window_bytes": 5,
                "bindings": {
                    "data_field": "data",
                    "fullness_field": "fullness",
                    "write_ptr_field": "write_ptr",
                    "size_field": "size",
                    "max_fullness_field": "max_fullness",
                    "byte_ports": [f"byte_{i}" for i in range(5)],
                    "byte_output_ports": [
                        f"byte_{i}_out" for i in range(5)
                    ],
                },
            },
        }
        verified = {
            "WriteFifo": {
                "contract": child_contract,
                "contract_sha256": "a" * 64,
                "candidate_sha256": "b" * 64,
                "rtl_return_invocations": 99,
            }
        }
        with tempfile.TemporaryDirectory() as directory:
            root = pathlib.Path(directory)
            (root / "parent.c").write_text(source, encoding="utf-8")
            matches = discover_fifo_write_accounting_candidates(
                functions,
                candidates,
                coverage,
                root,
                verified,
            )
            self.assertEqual(len(matches), 1)
            contract = build_fifo_write_accounting_contract(
                matches[0], root
            )
            rtl = render_fifo_write_accounting_rtl(contract)
            candidate = root / "candidate.sv"
            candidate.write_text(rtl, encoding="utf-8")
            (root / "dsc_types.h").write_text(
                "typedef struct fifo_s { unsigned char *data; int fullness; "
                "int write_ptr; int size; int max_fullness; } fifo_t;\n"
                "typedef struct { fifo_t lanes[4]; int bits; } dsc_state_t;\n"
                "typedef struct { int unused; } dsc_cfg_t;\n",
                encoding="utf-8",
            )
            paths = Agent(root, "test").write_overlay_sources(
                contract,
                root,
                contract["contract_id"],
                candidate,
            )
            composition = paths["composition"]
            self.assertEqual(
                composition["adapter_kind"],
                "explicit_fifo_write_accounting_state_transition",
            )
            self.assertTrue(
                composition["rtl_return_controls_fifo_memory_and_counter"]
            )
            overlay = paths["overlay"].read_text(encoding="utf-8")
            self.assertIn("state->bits = dsc_cicd_rtl_num_bits", overlay)
            self.assertIn("dsc_cicd_merged", overlay)
            clang = shutil.which("clang")
            if clang:
                syntax = subprocess.run(
                    [
                        clang,
                        "-std=gnu99",
                        "-fsyntax-only",
                        "-I",
                        str(root),
                        str(paths["overlay"]),
                    ],
                    cwd=root,
                    text=True,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.STDOUT,
                    check=False,
                )
                self.assertEqual(syntax.returncode, 0, syntax.stdout)
            verilator = shutil.which("verilator")
            if verilator:
                lint = subprocess.run(
                    [
                        verilator,
                        "--lint-only",
                        "--Wno-fatal",
                        "--top-module",
                        contract["contract_id"],
                        str(candidate),
                    ],
                    cwd=root,
                    text=True,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.STDOUT,
                    check=False,
                )
                self.assertEqual(lint.returncode, 0, lint.stdout)


if __name__ == "__main__":
    unittest.main()
