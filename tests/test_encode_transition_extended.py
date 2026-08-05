import hashlib
import pathlib
import shutil
import subprocess
import tempfile
import unittest

from tools.cicd_agent import Agent
from tools.generate_encode_transition import (
    build_ich_decision_contract,
    build_midpoint_line_write_contract,
    discover_ich_decision_candidates,
    discover_midpoint_line_write_candidates,
    render_ich_decision_rtl,
    render_midpoint_line_write_rtl,
)


def _source_span(source: str) -> tuple[int, int]:
    return 1, len(source.splitlines())


def _candidate_fact(usr: str, name: str) -> dict:
    return {
        "clang_usr": usr,
        "name": name,
        "contributes_to_observable_output": True,
        "direct_effects": {
            "allocation": False,
            "assertion": False,
            "indirect_call": False,
            "io": False,
            "logging": False,
        },
    }


def _coverage_fact(usr: str, name: str) -> dict:
    return {
        "clang_usr": usr,
        "name": name,
        "coverage": {"covered": True, "execution_count": 17},
    }


def _write_encode_constants(root: pathlib.Path) -> None:
    (root / "synthetic_constants.h").write_text(
        "#define MAX_UNITS_PER_GROUP 2\n"
        "#define SAMPLES_PER_UNIT 2\n"
        "#define PADDING_LEFT 1\n"
        "#define ICH_BITS 2\n"
        "#define ICH_LAMBDA 3\n",
        encoding="utf-8",
    )


def _midpoint_fixture() -> tuple[str, dict, dict, dict]:
    source = """void RenamedLineEmitter(dsc_cfg_t *cfg, dsc_state_t *state, int hpos, int **line)
{
  int sample, unit, component;
  int start = hpos % state->pixels_per_group;
  for (sample = 0; sample < SAMPLES_PER_UNIT; ++sample) {
    for (unit = 0; unit < state->units_per_group; ++unit) {
      if (state->unit_selected[unit]) {
        component = state->unit_component[unit];
        line[component][start + state->unit_start[unit] + sample] =
            state->reconstruction[unit][sample];
      }
      if (hpos + sample >= state->slice_width)
        break;
    }
  }
}
"""
    start, end = _source_span(source)
    usr = "c:@F@RenamedLineEmitter"
    function = {
        "name": "RenamedLineEmitter",
        "clang_usr": usr,
        "source_file": "midpoint.c",
        "line": start,
        "end_line": end,
        "return_type": "void",
        "parameters": [
            {"name": "cfg", "type": "dsc_cfg_t *", "pointer": True},
            {"name": "state", "type": "dsc_state_t *", "pointer": True},
            {"name": "hpos", "type": "int", "pointer": False},
            {"name": "line", "type": "int **", "pointer": True},
        ],
        "pointer_parameters": [
            {"name": "cfg", "type": "dsc_cfg_t *", "mode": "READ_ONLY"},
            {"name": "state", "type": "dsc_state_t *", "mode": "READ_ONLY"},
            {"name": "line", "type": "int **", "mode": "WRITES_THROUGH"},
        ],
        "loop_count": 2,
        "callees": [],
        "fields_read": [
            {"record": "dsc_state_t", "name": "pixels_per_group", "type": "int"},
            {"record": "dsc_state_t", "name": "units_per_group", "type": "int"},
            {"record": "dsc_state_t", "name": "slice_width", "type": "int"},
            {"record": "dsc_state_t", "name": "unit_selected", "type": "int[2]"},
            {"record": "dsc_state_t", "name": "unit_component", "type": "int[2]"},
            {"record": "dsc_state_t", "name": "unit_start", "type": "int[2]"},
            {"record": "dsc_state_t", "name": "reconstruction", "type": "int[2][2]"},
        ],
        "fields_write": [],
        "globals_write": [],
    }
    return (
        source,
        {"functions": [function]},
        {"functions": [_candidate_fact(usr, function["name"])]},
        {"functions": [_coverage_fact(usr, function["name"])]},
    )


def _ich_fixture() -> tuple[str, dict, dict, dict, dict]:
    source = """int RenamedCostSelector(dsc_cfg_t *cfg, dsc_state_t *state, int alternate_size, int adjusted_size, int unused_prefix)
{
  int unit, prior = 0;
  int max_error[2];
  int bits_ich_mode = alternate_size - adjusted_size;
  if (cfg->version == 1)
    prior += 1;
  if (cfg->version == 2)
    prior += 1;
  if (state->previous_ich)
    prior = 1;
  ICH_BITS * state->ich_indices[0];
  for (unit = 0; unit < state->units_per_group; ++unit) {
    if (OddQuad(cfg, state, unit, state->unit_type[unit]))
      max_error[unit] = MAX(0, state->max_mid_error[unit]);
    else
      max_error[unit] = MAX(0, state->max_error[unit]);
    prior += OneArg(state->max_ich_error[unit]);
  }
  for (unit = 0; unit < 0; ++unit)
    prior += 0;
  for (unit = 0; unit < 0; ++unit)
    prior += 0;
  bits_ich_mode = alternate_size - adjusted_size;
  return bits_ich_mode + TwoArg(cfg, state) +
      ThreeArg(cfg, state, state->hpos);
}
"""
    start, end = _source_span(source)
    usr = "c:@F@RenamedCostSelector"
    callee_names = ["OddQuad", "OneArg", "TwoArg", "ThreeArg"]
    function = {
        "name": "RenamedCostSelector",
        "clang_usr": usr,
        "source_file": "ich.c",
        "line": start,
        "end_line": end,
        "return_type": "int",
        "parameters": [
            {"name": "cfg", "type": "dsc_cfg_t *", "pointer": True},
            {"name": "state", "type": "dsc_state_t *", "pointer": True},
            {"name": "alternate_size", "type": "int", "pointer": False},
            {"name": "adjusted_size", "type": "int", "pointer": False},
            {"name": "unused_prefix", "type": "int", "pointer": False},
        ],
        "pointer_parameters": [
            {"name": "cfg", "type": "dsc_cfg_t *", "mode": "READ_ONLY"},
            {"name": "state", "type": "dsc_state_t *", "mode": "READ_ONLY"},
        ],
        "loop_count": 3,
        "callees": [{"name": name} for name in callee_names],
        "fields_read": [
            {"record": "dsc_state_t", "name": "units_per_group", "type": "int"},
            {"record": "dsc_state_t", "name": "previous_ich", "type": "int"},
            {"record": "dsc_state_t", "name": "ich_indices", "type": "int"},
            {"record": "dsc_state_t", "name": "hpos", "type": "int"},
            {"record": "dsc_state_t", "name": "unit_type", "type": "int[2]"},
            {"record": "dsc_state_t", "name": "max_mid_error", "type": "int[2]"},
            {"record": "dsc_state_t", "name": "max_error", "type": "int[2]"},
            {"record": "dsc_state_t", "name": "max_ich_error", "type": "int[2]"},
            {"record": "dsc_cfg_t", "name": "version", "type": "int"},
        ],
        "fields_write": [],
        "globals_write": [],
    }
    arities = {"OddQuad": 4, "OneArg": 1, "TwoArg": 2, "ThreeArg": 3}
    stable_contracts = {}
    for name, arity in arities.items():
        parameters = [
            {"name": f"p{index}", "type": "int", "pointer": False}
            for index in range(arity)
        ]
        child_contract = {
            "contract_id": f"stable_{name.lower()}",
            "status": "PASS",
            "function": {"name": name, "parameters": parameters},
        }
        stable_contracts[name] = {
            "component": {"status": "PASS", "function": name},
            "contract": child_contract,
            "contract_sha256": hashlib.sha256(
                f"contract:{name}".encode("utf-8")
            ).hexdigest(),
            "module_sha256": hashlib.sha256(
                f"module:{name}".encode("utf-8")
            ).hexdigest(),
        }
    return (
        source,
        {"functions": [function]},
        {"functions": [_candidate_fact(usr, function["name"])]},
        {"functions": [_coverage_fact(usr, function["name"])]},
        stable_contracts,
    )


def _assert_optional_tool_checks(
    testcase: unittest.TestCase,
    root: pathlib.Path,
    paths: dict,
    contract: dict,
) -> None:
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
        testcase.assertEqual(syntax.returncode, 0, syntax.stdout)

    verilator = shutil.which("verilator")
    if verilator:
        lint = subprocess.run(
            [
                verilator,
                "--lint-only",
                "--Wno-fatal",
                "--top-module",
                contract["contract_id"],
                str(paths["candidate"]),
            ],
            cwd=root,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            check=False,
        )
        testcase.assertEqual(lint.returncode, 0, lint.stdout)


class EncodeTransitionExtendedTests(unittest.TestCase):
    def test_midpoint_discover_build_render_and_adapter(self):
        source, functions, candidates, coverage = _midpoint_fixture()
        with tempfile.TemporaryDirectory() as directory:
            root = pathlib.Path(directory)
            _write_encode_constants(root)
            (root / "midpoint.c").write_text(source, encoding="utf-8")
            (root / "dsc_types.h").write_text(
                "typedef struct dsc_cfg_s { int unused; } dsc_cfg_t;\n"
                "typedef struct dsc_state_s {\n"
                "  int pixels_per_group; int units_per_group; int slice_width;\n"
                "  int unit_selected[2]; int unit_component[2]; int unit_start[2];\n"
                "  int reconstruction[2][2];\n"
                "} dsc_state_t;\n",
                encoding="utf-8",
            )
            selected = discover_midpoint_line_write_candidates(
                functions, candidates, coverage, root
            )
            self.assertEqual(len(selected), 1)
            self.assertEqual(selected[0]["name"], "RenamedLineEmitter")
            self.assertEqual(
                selected[0]["semantics_kind"],
                "bounded_midpoint_line_write_transition",
            )
            self.assertIn(
                "no function-name allowlist is used",
                selected[0]["selection_basis"],
            )

            contract = build_midpoint_line_write_contract(selected[0], root)
            self.assertEqual(
                contract["semantics"]["write_slots"],
                contract["semantics"]["max_units"]
                * contract["semantics"]["samples_per_unit"],
            )
            rtl = render_midpoint_line_write_rtl(contract)
            candidate = root / "midpoint_candidate.sv"
            candidate.write_text(rtl, encoding="utf-8")
            paths = Agent(root, "test").write_overlay_sources(
                contract, root, contract["contract_id"], candidate
            )
            composition = paths["composition"]
            self.assertEqual(
                composition["adapter_kind"],
                "explicit_bounded_midpoint_line_write_transition",
            )
            self.assertTrue(
                composition["rtl_return_controls_all_enabled_line_writes"]
            )
            self.assertTrue(composition["final_aliased_line_image_compared"])
            self.assertTrue(
                composition["residual_symbol_alias_routes_to_dispatcher"]
            )
            overlay = paths["overlay"].read_text(encoding="utf-8")
            self.assertIn("dsc_cicd_expected_enable", overlay)
            self.assertIn("dsc_cicd_merged", overlay)
            self.assertIn("dsc_cicd_rtl", overlay)
            self.assertIn("write_value_0", rtl)
            _assert_optional_tool_checks(self, root, paths, contract)

    def test_ich_discover_build_render_and_adapter_composes_stable_children(self):
        source, functions, candidates, coverage, stable_contracts = _ich_fixture()
        with tempfile.TemporaryDirectory() as directory:
            root = pathlib.Path(directory)
            _write_encode_constants(root)
            (root / "ich.c").write_text(source, encoding="utf-8")
            (root / "dsc_types.h").write_text(
                "typedef struct dsc_cfg_s { int version; } dsc_cfg_t;\n"
                "typedef struct dsc_state_s {\n"
                "  int units_per_group; int previous_ich; int ich_indices; int hpos;\n"
                "  int unit_type[2]; int max_mid_error[2]; int max_error[2];\n"
                "  int max_ich_error[2];\n"
                "} dsc_state_t;\n",
                encoding="utf-8",
            )
            selected = discover_ich_decision_candidates(
                functions,
                candidates,
                coverage,
                root,
                stable_contracts,
            )
            self.assertEqual(len(selected), 1)
            self.assertEqual(selected[0]["name"], "RenamedCostSelector")
            self.assertEqual(selected[0]["midpoint_callee"], "OddQuad")
            self.assertEqual(selected[0]["estimate_callee"], "TwoArg")
            self.assertEqual(selected[0]["flat_callee"], "ThreeArg")
            self.assertEqual(selected[0]["log_callee"], "OneArg")
            self.assertIn(
                "no function-name allowlist is used",
                selected[0]["selection_basis"],
            )

            contract = build_ich_decision_contract(selected[0], root)
            dependencies = contract["composition"]["dependencies"]
            self.assertEqual(
                {item["function"] for item in dependencies},
                set(stable_contracts),
            )
            self.assertTrue(
                all(len(item["contract_sha256"]) == 64 for item in dependencies)
            )
            rtl = render_ich_decision_rtl(contract)
            candidate = root / "ich_candidate.sv"
            candidate.write_text(rtl, encoding="utf-8")
            paths = Agent(root, "test").write_overlay_sources(
                contract, root, contract["contract_id"], candidate
            )
            composition = paths["composition"]
            self.assertEqual(
                composition["adapter_kind"],
                "explicit_bounded_ich_decision_transition",
            )
            self.assertTrue(composition["rtl_return_controls_decision"])
            self.assertTrue(
                composition["accepted_child_results_are_explicit_inputs"]
            )
            self.assertTrue(
                composition["simultaneous_rewrite_routes_child_calls_to_rtl"]
            )
            self.assertTrue(
                composition["residual_symbol_alias_routes_to_dispatcher"]
            )
            overlay = paths["overlay"].read_text(encoding="utf-8")
            self.assertIn("extern int OddQuad", overlay)
            self.assertIn("extern int TwoArg", overlay)
            self.assertIn("dsc_cicd_estimated_bits", overlay)
            self.assertIn("dsc_cicd_flat_index", overlay)
            self.assertIn("dsc_cicd_rtl", overlay)
            self.assertIn("c_ceil_log2", rtl)
            _assert_optional_tool_checks(self, root, paths, contract)


if __name__ == "__main__":
    unittest.main()
