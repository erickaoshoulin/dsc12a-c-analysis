import json
import pathlib
import shutil
import subprocess
import tempfile
import unittest

from tools.cicd_agent import Agent
from tools.generate_encode_transition import (
    build_populate_orig_line_contract,
    discover_populate_orig_line_candidates,
    render_populate_orig_line_rtl,
)


WORKTREE = pathlib.Path(__file__).resolve().parents[1]
SOURCE_DIR = pathlib.Path(
    "/Users/snow/Desktop/Display Stream Compression (DSC)/DSC 1.2a/"
    "DSC_model_20210623/source"
)


def real_candidate():
    functions = json.loads((WORKTREE / "facts/functions.json").read_text())
    candidates = json.loads((WORKTREE / "facts/candidates.json").read_text())
    coverage = json.loads((WORKTREE / "coverage/coverage.json").read_text())
    matches = discover_populate_orig_line_candidates(
        functions,
        candidates,
        coverage,
        SOURCE_DIR,
    )
    return matches


def write_fixture_header(root: pathlib.Path) -> None:
    (root / "dsc_types.h").write_text(
        """#define NUM_COMPONENTS 4
#define PADDING_LEFT 5
#define PADDING_RIGHT 10
typedef struct { int **y; int **u; int **v; int **a; } yuv_t;
typedef union { yuv_t yuv; } data_u;
typedef struct { int w; int h; data_u data; } pic_t;
typedef struct { int native_420; int native_422; int xstart; int ystart; } dsc_cfg_t;
typedef struct {
    int numComponents;
    int sliceWidth;
    int cpntBitDepth[4];
    int *origLine[4];
} dsc_state_t;
""",
        encoding="utf-8",
    )
    # The real model owns pic_t in vdo.h; this fixture defines it above to
    # keep the adapter syntax test minimal while preserving the include ABI.
    (root / "vdo.h").write_text("", encoding="utf-8")


class PopulateOrigLineTransitionTests(unittest.TestCase):
    def test_structural_discovery_and_contract_are_source_driven(self):
        if not SOURCE_DIR.is_dir():
            self.skipTest("immutable local DSC C source is unavailable")
        matches = real_candidate()
        self.assertEqual(len(matches), 1)
        selected = matches[0]
        self.assertEqual(selected["semantics_kind"], "populate_orig_line_memory_transition")
        self.assertEqual(selected["execution_count"], 2592)
        self.assertEqual(selected["max_slice_width"], 65535)
        self.assertEqual(selected["max_slice_height"], 65535)
        contract = build_populate_orig_line_contract(selected, SOURCE_DIR)
        self.assertEqual(
            contract["semantics"]["external_memory"]["request_fields"],
            ["read_enable", "read_plane", "read_y", "read_x"],
        )
        self.assertTrue(contract["semantics"]["external_memory"]["read_only"])
        self.assertEqual(
            contract["semantics"]["bindings"]["write_address_port"],
            "write_address",
        )
        self.assertEqual(
            contract["semantics"]["legal_vector_strategy"]["kind"],
            "populate_orig_line",
        )

    def test_adapter_keeps_pic_external_and_restores_private_c_oracle(self):
        if not SOURCE_DIR.is_dir():
            self.skipTest("immutable local DSC C source is unavailable")
        selected = real_candidate()[0]
        contract = build_populate_orig_line_contract(selected, SOURCE_DIR)
        with tempfile.TemporaryDirectory() as directory:
            root = pathlib.Path(directory)
            write_fixture_header(root)
            candidate = root / "candidate.sv"
            candidate.write_text(render_populate_orig_line_rtl(contract), encoding="utf-8")
            agent = Agent(root, "populate-orig-line-test")
            paths = agent.write_overlay_sources(
                contract,
                root,
                contract["contract_id"],
                candidate,
            )
            composition = paths["composition"]
            self.assertTrue(composition["external_pic_memory_is_read_only"])
            self.assertTrue(composition["rtl_produces_plane_y_x_request"])
            self.assertTrue(composition["adapter_services_rtl_memory_request"])
            self.assertTrue(composition["c_oracle_state_pointers_restored_before_rtl"])
            self.assertTrue(composition["rtl_return_commits_rtl_line_image_without_c_fallback"])
            self.assertTrue(composition["every_touched_output_element_compared"])
            overlay = paths["overlay"].read_text(encoding="utf-8")
            self.assertIn("dsc_cicd_read_pixel", overlay)
            self.assertIn("dsc_cicd_request_plane", overlay)
            self.assertIn("dsc_cicd_request_y", overlay)
            self.assertIn("dsc_cicd_request_x", overlay)
            self.assertIn("dsc_cicd_private_line", overlay)
            self.assertIn("dsc_cicd_rtl_line", overlay)
            self.assertIn("dsc_cicd_rtl(", overlay)
            self.assertNotIn("PopulateOrigLine", overlay.split("static int dsc_cicd_read_pixel", 1)[-1].split("void dsc_cicd_invoke", 1)[0])

            clang = shutil.which("clang")
            if clang:
                for source in (paths["overlay"],):
                    result = subprocess.run(
                        [clang, "-std=gnu99", "-fsyntax-only", "-I", str(root), str(source)],
                        cwd=root,
                        text=True,
                        stdout=subprocess.PIPE,
                        stderr=subprocess.STDOUT,
                        check=False,
                    )
                    self.assertEqual(result.returncode, 0, result.stdout)

    def test_rtl_preserves_native_422_mapping_clamps_midpoint_and_address(self):
        verilator = shutil.which("verilator")
        if not verilator:
            self.skipTest("Verilator is unavailable")
        if not SOURCE_DIR.is_dir():
            self.skipTest("immutable local DSC C source is unavailable")
        contract = build_populate_orig_line_contract(real_candidate()[0], SOURCE_DIR)
        module = contract["contract_id"]
        with tempfile.TemporaryDirectory() as directory:
            root = pathlib.Path(directory)
            candidate = root / "candidate.sv"
            candidate.write_text(render_populate_orig_line_rtl(contract), encoding="utf-8")
            harness = root / "harness.cpp"
            harness.write_text(
                f'''#include "V{module}.h"
#include "verilated.h"
#include <cstdlib>

static void drive(
    V{module}& dut, int native420, int native422, int xstart, int ystart,
    int components, int slice, int width, int height, int vpos,
    int component, int sample, int depth, int pixel,
    int read_enable, int read_plane, int read_y, int read_x,
    int write_address, int write_value) {{
    dut.native_420 = native420; dut.native_422 = native422;
    dut.xstart = xstart; dut.ystart = ystart;
    dut.num_components = components; dut.slice_width = slice;
    dut.pic_width = width; dut.pic_height = height; dut.vpos = vpos;
    dut.component = component; dut.sample_index = sample;
    dut.component_bit_depth = depth; dut.pixel_data = pixel;
    dut.eval();
    if (dut.illegal_domain || dut.read_enable != read_enable ||
        dut.read_plane != read_plane || dut.read_y != read_y ||
        dut.read_x != read_x || !dut.write_enable ||
        dut.write_component != component || dut.write_address != write_address ||
        dut.write_value != write_value) std::abort();
}}

int main() {{
    V{module} dut;
    drive(dut, 0, 1, 2, 1, 4, 3, 8, 4, 0, 0, 1, 10, 77,
          1, 0, 1, 4, 6, 77);
    drive(dut, 0, 1, 2, 1, 4, 3, 8, 4, 0, 1, 12, 10, 91,
          1, 1, 1, 3, 17, 91);
    drive(dut, 0, 1, 2, 1, 4, 3, 8, 4, 0, 3, 0, 10, 33,
          1, 0, 1, 3, 5, 33);
    drive(dut, 0, 1, 2, 1, 4, 3, 8, 4, 3, 0, 0, 10, 33,
          0, 0, 3, 2, 5, 512);
    drive(dut, 0, 0, 1, 0, 3, 3, 4, 4, 0, 2, 7, 8, 44,
          1, 2, 0, 3, 12, 44);
    return 0;
}}
''',
                encoding="utf-8",
            )
            build = subprocess.run(
                [
                    verilator,
                    "--cc",
                    "--exe",
                    "--build",
                    "--Wno-fatal",
                    "--top-module",
                    module,
                    str(candidate),
                    str(harness),
                    "--Mdir",
                    str(root / "obj"),
                ],
                cwd=root,
                text=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                check=False,
            )
            self.assertEqual(build.returncode, 0, build.stdout)
            binary = root / "obj" / f"V{module}"
            run = subprocess.run(
                [str(binary)],
                cwd=root,
                text=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                check=False,
            )
            self.assertEqual(run.returncode, 0, run.stdout)


if __name__ == "__main__":
    unittest.main()
