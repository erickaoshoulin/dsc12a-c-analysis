import copy
import json
import pathlib
import re
import shutil
import subprocess
import tempfile
import unittest

from tools.generate_history_encode import (
    HISTORY_QERR_ROLE,
    HISTORY_REDUCTION_ROLE,
    build_history_encode_contract,
    discover_history_encode_candidates,
    find_dependency_pins,
    read_json,
    render_history_encode_rtl,
    verify_dependency_pins,
)


REPO_ROOT = pathlib.Path(__file__).resolve().parents[1]
SOURCE_DIR = pathlib.Path(
    "/Users/snow/Desktop/Display Stream Compression (DSC)/DSC 1.2a/"
    "DSC_model_20210623/source"
)


def _real_documents():
    return (
        read_json(REPO_ROOT / "facts" / "functions.json"),
        read_json(REPO_ROOT / "facts" / "candidates.json"),
        read_json(REPO_ROOT / "coverage" / "coverage.json"),
    )


def _function_row(functions, name):
    return copy.deepcopy(
        next(item for item in functions["functions"] if item.get("name") == name)
    )


def _renamed_fixture(name: str, renamed: str):
    functions, candidates, coverage = _real_documents()
    function = _function_row(functions, name)
    source = SOURCE_DIR / function["source_file"]
    lines = source.read_text(encoding="utf-8", errors="replace").splitlines()
    start = int(function["line"])
    end = int(function["end_line"])
    body = "\n".join(lines[start - 1 : end])
    body = re.sub(rf"\b{re.escape(name)}\b", renamed, body, count=1)
    function["name"] = renamed
    function["qualified_name"] = renamed
    function["source_file"] = "renamed_transition.c"
    function["line"] = 1
    function["end_line"] = len(body.splitlines())
    functions["functions"] = [function]

    candidate = copy.deepcopy(
        next(item for item in candidates["functions"] if item.get("clang_usr") == function["clang_usr"])
    )
    candidate["name"] = renamed
    candidates["functions"] = [candidate]
    runtime = copy.deepcopy(
        next(item for item in coverage["functions"] if item.get("clang_usr") == function["clang_usr"])
    )
    runtime["name"] = renamed
    coverage["functions"] = [runtime]
    return body, functions, candidates, coverage


class HistoryEncodeGeneratorTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        if not SOURCE_DIR.is_dir():
            raise unittest.SkipTest(f"immutable model source is unavailable: {SOURCE_DIR}")

    def test_discovery_is_structural_and_coverage_driven(self):
        functions, candidates, coverage = _real_documents()
        dependencies = find_dependency_pins(REPO_ROOT)
        matches = discover_history_encode_candidates(
            functions, candidates, coverage, SOURCE_DIR, dependencies
        )
        roles = {item["role"]: item for item in matches}
        self.assertEqual(set(roles), {HISTORY_REDUCTION_ROLE, HISTORY_QERR_ROLE})
        self.assertGreater(roles[HISTORY_REDUCTION_ROLE]["execution_count"], 0)
        self.assertGreater(roles[HISTORY_QERR_ROLE]["execution_count"], 0)
        for item in roles.values():
            self.assertIn("role was selected by loop/call/field/effect fingerprint", " ".join(item["selection_basis"]))

        body, renamed_functions, renamed_candidates, renamed_coverage = _renamed_fixture(
            "PickBestHistoryValue", "RenamedHistoryReducer"
        )
        with tempfile.TemporaryDirectory() as directory:
            source_root = pathlib.Path(directory)
            (source_root / "renamed_transition.c").write_text(body, encoding="utf-8")
            renamed_matches = discover_history_encode_candidates(
                renamed_functions,
                renamed_candidates,
                renamed_coverage,
                source_root,
                dependencies,
            )
        self.assertEqual(len(renamed_matches), 1)
        self.assertEqual(renamed_matches[0]["role"], HISTORY_REDUCTION_ROLE)
        self.assertEqual(renamed_matches[0]["name"], "RenamedHistoryReducer")

        qerr_body, qerr_functions, qerr_candidates, qerr_coverage = _renamed_fixture(
            "IsOrigWithinQerr", "RenamedHistoryQerr"
        )
        with tempfile.TemporaryDirectory() as directory:
            source_root = pathlib.Path(directory)
            (source_root / "renamed_transition.c").write_text(qerr_body, encoding="utf-8")
            qerr_matches = discover_history_encode_candidates(
                qerr_functions,
                qerr_candidates,
                qerr_coverage,
                source_root,
                dependencies,
            )
        self.assertEqual(len(qerr_matches), 1)
        self.assertEqual(qerr_matches[0]["role"], HISTORY_QERR_ROLE)
        self.assertEqual(qerr_matches[0]["name"], "RenamedHistoryQerr")

        uncovered_coverage = copy.deepcopy(qerr_coverage)
        uncovered_coverage["functions"][0]["coverage"]["execution_count"] = 0
        uncovered_coverage["functions"][0]["coverage"]["covered"] = False
        with tempfile.TemporaryDirectory() as directory:
            source_root = pathlib.Path(directory)
            (source_root / "renamed_transition.c").write_text(qerr_body, encoding="utf-8")
            self.assertEqual(
                discover_history_encode_candidates(
                    qerr_functions,
                    qerr_candidates,
                    uncovered_coverage,
                    source_root,
                    dependencies,
                ),
                [],
            )

    def test_contracts_bind_and_recheck_existing_dependencies(self):
        functions, candidates, coverage = _real_documents()
        dependencies = find_dependency_pins(REPO_ROOT)
        self.assertEqual(
            set(dependencies), {"history_lookup", "map_qp_to_qlevel"}
        )
        for dependency in dependencies.values():
            self.assertTrue(dependency["contract_sha256"])
            self.assertTrue(dependency["module_sha256"])
            self.assertTrue(dependency["function_usr"])

        matches = discover_history_encode_candidates(
            functions, candidates, coverage, SOURCE_DIR, dependencies
        )
        for match in matches:
            contract = build_history_encode_contract(
                match, REPO_ROOT, SOURCE_DIR, dependencies
            )
            verify_dependency_pins(contract, REPO_ROOT)
            roles = {item["role"] for item in contract["dependencies"]}
            self.assertIn("history_lookup", roles)
            if match["role"] == HISTORY_QERR_ROLE:
                self.assertIn("map_qp_to_qlevel", roles)
                self.assertEqual(
                    contract["semantics"]["algorithm"]["threshold"],
                    "inclusive; reject only when absdiff > max_qerr",
                )
            else:
                self.assertEqual(
                    contract["semantics"]["algorithm"]["tie_rule"],
                    "strict lowest_sad > weighted_sad; first entry wins ties",
                )

    def test_hash_drift_is_rejected_without_touching_repository_artifacts(self):
        functions, candidates, coverage = _real_documents()
        dependencies = find_dependency_pins(REPO_ROOT)
        match = next(
            item
            for item in discover_history_encode_candidates(
                functions, candidates, coverage, SOURCE_DIR, dependencies
            )
            if item["role"] == HISTORY_QERR_ROLE
        )
        contract = build_history_encode_contract(
            match, REPO_ROOT, SOURCE_DIR, dependencies
        )
        with tempfile.TemporaryDirectory() as directory:
            temp_root = pathlib.Path(directory)
            for dependency in contract["dependencies"]:
                for key in ("contract_file", "module_file"):
                    relative = pathlib.Path(dependency[key])
                    target = temp_root / relative
                    target.parent.mkdir(parents=True, exist_ok=True)
                    shutil.copy2(REPO_ROOT / relative, target)
            verify_dependency_pins(contract, temp_root)
            history = next(
                item
                for item in contract["dependencies"]
                if item["role"] == "history_lookup"
            )
            module = temp_root / history["module_file"]
            module.write_text(module.read_text(encoding="utf-8") + "\n// drift\n", encoding="utf-8")
            with self.assertRaisesRegex(RuntimeError, "module hash drift"):
                verify_dependency_pins(contract, temp_root)

    def test_generated_rtl_exposes_child_results_and_lints(self):
        functions, candidates, coverage = _real_documents()
        dependencies = find_dependency_pins(REPO_ROOT)
        matches = discover_history_encode_candidates(
            functions, candidates, coverage, SOURCE_DIR, dependencies
        )
        verilator = shutil.which("verilator")
        with tempfile.TemporaryDirectory() as directory:
            output = pathlib.Path(directory)
            for match in matches:
                contract = build_history_encode_contract(
                    match, REPO_ROOT, SOURCE_DIR, dependencies
                )
                rtl = render_history_encode_rtl(contract)
                candidate = output / f"{contract['contract_id']}.sv"
                candidate.write_text(rtl, encoding="utf-8")
                self.assertIn("history_lookup_result_valid", rtl)
                self.assertIn("lookup_request_valid", rtl)
                self.assertIn("illegal_domain", rtl)
                if match["role"] == HISTORY_REDUCTION_ROLE:
                    self.assertIn("weighted_sad_i", rtl)
                    self.assertIn("lowest_sad_i > weighted_sad_i", rtl)
                    self.assertIn("64'sd2 * abs_i33(diff0_i)", rtl)
                    self.assertIn("search_failed", rtl)
                else:
                    self.assertIn("map_qlevel", rtl)
                    self.assertIn("history_valid_next[i] = 32'sd1", rtl)
                    self.assertIn("absdiff_i > max_qerr_i[i]", rtl)
                    self.assertIn("orig_within_qerr_out", rtl)
                if verilator:
                    result = subprocess.run(
                        [
                            verilator,
                            "--lint-only",
                            "--Wno-fatal",
                            "--top-module",
                            contract["contract_id"],
                            str(candidate),
                        ],
                        cwd=REPO_ROOT,
                        text=True,
                        stdout=subprocess.PIPE,
                        stderr=subprocess.STDOUT,
                        check=False,
                    )
                    self.assertEqual(result.returncode, 0, result.stdout)


if __name__ == "__main__":
    unittest.main()
