import json
import pathlib
import sys
import tempfile
import unittest


ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))

import rank_candidates  # noqa: E402
import traceability  # noqa: E402


class AutoDiscoveryTests(unittest.TestCase):
    def test_generic_boundary_function_is_selected_without_name_allowlist(self):
        raw = {
            "functions": [
                {
                    "clang_usr": "U_main",
                    "name": "entry_alpha",
                    "source_file": "/tmp/entry.c",
                    "callees": [{"clang_usr": "U_core", "name": "core_beta"}],
                    "calls": [{"name": "fputs", "category": "file_io"}],
                    "parameters": [],
                    "loops": [],
                    "effects": {"file_io": True},
                },
                {
                    "clang_usr": "U_core",
                    "name": "core_beta",
                    "source_file": "/tmp/core.c",
                    "callees": [],
                    "calls": [],
                    "parameters": [
                        {"type": "const dsc_cfg_t *"},
                        {"type": "pic_t *"},
                        {"type": "unsigned char *"},
                    ],
                    "loops": [],
                    "effects": {},
                },
            ],
            "edges": [],
        }
        with tempfile.TemporaryDirectory() as directory:
            root = pathlib.Path(directory)
            raw_path = root / "raw.json"
            build_path = root / "build.json"
            output_path = root / "candidates.json"
            report_path = root / "candidates.md"
            raw_path.write_text(json.dumps(raw), encoding="utf-8")
            build_path.write_text(
                json.dumps({"status": "PASS", "binary": {"symbols": {"entry_symbols": ["entry_alpha"]}}}),
                encoding="utf-8",
            )
            args = type(
                "Args",
                (),
                {
                    "raw": raw_path,
                    "build_receipt": build_path,
                    "output": output_path,
                    "report": report_path,
                    "top_n": 10,
                },
            )()
            original = rank_candidates.parse_args
            rank_candidates.parse_args = lambda: args
            try:
                self.assertEqual(rank_candidates.main(), 0)
            finally:
                rank_candidates.parse_args = original
            payload = json.loads(output_path.read_text(encoding="utf-8"))
            self.assertEqual(payload["selected_for_frama"], ["core_beta"])
            selected = payload["ranked_candidates"][0]
            self.assertTrue(selected["eligible"])
            self.assertEqual(selected["role"], "DUT")

    def test_reference_ids_are_structural_and_deterministic(self):
        refs = traceability.ref_ids("Section 4.2 uses Table 4-1 and Figure 2 on spec P17")
        self.assertEqual(refs["sections"], ["4.2"])
        self.assertEqual(refs["pages"], [17])
        self.assertEqual(refs["tables"], ["Table 4-1"])
        self.assertEqual(refs["figures"], ["Figure 2"])
        self.assertEqual(traceability.normalize_pdf_text("Table4-1: values"), "Table 4-1: values")

    def test_reviewed_link_becomes_stale_when_input_hash_changes(self):
        link = {
            "spec_anchor_id": "pdf:section:4.2",
            "code_anchor_id": "code:function:U_core",
            "status": "PROPOSED",
        }
        reviewed = [
            {
                "spec_anchor_id": "pdf:section:4.2",
                "code_anchor_id": "code:function:U_core",
                "spec_sha256": "old-pdf",
                "source_hashes_sha256": "old-source",
            }
        ]
        result = traceability.apply_reviewed(
            [link],
            reviewed,
            {"spec": {"sha256": "new-pdf"}, "source": {"source_hashes_sha256": "new-source"}},
        )
        self.assertEqual(result[0]["status"], "STALE")


if __name__ == "__main__":
    unittest.main()
