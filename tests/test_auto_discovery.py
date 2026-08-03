import json
import pathlib
import sys
import tempfile
import unittest
from unittest import mock


ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))

import rank_candidates  # noqa: E402
import traceability  # noqa: E402
import discover_inputs  # noqa: E402


class AutoDiscoveryTests(unittest.TestCase):
    def test_source_discovery_prefers_versioned_model_over_ephemeral_copy(self):
        with tempfile.TemporaryDirectory() as directory:
            root = pathlib.Path(directory)
            repo = root / "workspace" / "repo"
            external = root / "Desktop" / "DSC_model_20210623" / "source"
            ephemeral = root / "workspace" / "tmp-copy" / "DSC_model_20210623" / "source"
            repo.mkdir(parents=True)
            external.mkdir(parents=True)
            ephemeral.mkdir(parents=True)

            def fake_run(command, timeout):
                if command[:4] == ["git", "-C", str(external.parent), "remote"]:
                    return 0, "https://example.invalid/dsc.git\n"
                return 128, "not a git repository\n"

            with mock.patch.object(discover_inputs, "run_command", side_effect=fake_run):
                external_key = discover_inputs.source_candidate_key(external, repo)
                ephemeral_key = discover_inputs.source_candidate_key(ephemeral, repo)

        self.assertLess(external_key, ephemeral_key)

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

    def test_reviewed_exact_link_materializes_when_heuristics_have_no_proposal(self):
        reviewed = [{
            "link_id": "reviewed-one",
            "spec_anchor_id": "pdf:section:1.6.2",
            "code_anchor_id": "code:function:U_leaf",
            "spec_sha256": "pdf",
            "source_hashes_sha256": "src",
            "method": "reviewed_exact_spec",
            "evidence": "normative helper definition",
        }]
        anchors = [{
            "anchor_id": "pdf:section:1.6.2",
            "kind": "section",
            "identifier": "1.6.2",
            "title": "Functions",
            "page": 22,
        }]
        code = [{
            "code_anchor_id": "code:function:U_leaf",
            "clang_usr": "U_leaf",
            "function": "ceil_log2",
            "file": "dsc_utils.c",
            "line": 67,
            "permalink": "https://example.invalid/ceil_log2",
        }]
        result = traceability.apply_reviewed(
            [], reviewed, {"spec": {"sha256": "pdf"}, "source": {"source_hashes_sha256": "src"}}, anchors, code
        )
        self.assertEqual(result[0]["status"], "REVIEWED")
        self.assertEqual(result[0]["function"], "ceil_log2")

    def test_reviewed_exact_link_can_resolve_excluded_function_from_raw_facts(self):
        reviewed = [{
            "link_id": "reviewed-config",
            "spec_anchor_id": "pdf:table:6-2",
            "code_anchor_id": "code:function:U_config",
            "spec_sha256": "pdf",
            "source_hashes_sha256": "src",
            "method": "reviewed_exact_spec",
            "evidence": "normative configuration table",
        }]
        anchors = [{
            "anchor_id": "pdf:table:6-2",
            "kind": "table",
            "identifier": "6-2",
            "title": "qLevel mapping",
            "page": 114,
        }]
        result = traceability.apply_reviewed(
            [],
            reviewed,
            {"spec": {"sha256": "pdf"}, "source": {"source_hashes_sha256": "src"}},
            anchors,
            [],
            [{
                "clang_usr": "U_config",
                "name": "Qp2Qlevel",
                "source_file": "codec_main.c",
                "line": 816,
                "end_line": 844,
            }],
        )
        self.assertEqual(result[0]["status"], "REVIEWED")
        self.assertEqual(result[0]["function"], "Qp2Qlevel")
        self.assertEqual(result[0]["code_file"], "codec_main.c")

    def test_every_shared_model_note_has_an_exact_link(self):
        payload = json.loads((ROOT / "traceability" / "traceability.json").read_text(encoding="utf-8"))
        shared = payload["counts"]["shared_model_note_ids"]
        self.assertEqual(payload["counts"]["shared_model_note_count"], len(shared))
        for model_note in shared:
            exact = [
                link
                for link in payload["links"]
                if link["status"] == "EXACT" and model_note in link.get("evidence", "")
            ]
            self.assertTrue(exact, model_note)

    def test_layout_model_note_attaches_to_same_page_preceding_heading(self):
        anchors = traceability.layout_pdf_anchors(
            ["6.4.3 Midpoint Prediction\n\nmodel note: MN_TEST in dsc_codec.c\n"],
            {"pages": "1"},
            pathlib.Path("synthetic.pdf"),
        )
        note = next(item for item in anchors if item["kind"] == "model_note")
        self.assertEqual(note["section_id"], "6.4.3")
        self.assertEqual(note["section_anchor_id"], "pdf:section:6.4.3")

    def test_heuristic_requires_two_meaningful_tokens(self):
        anchors = [
            {
                "anchor_id": "pdf:section:6.4.3",
                "kind": "section",
                "identifier": "6.4.3",
                "title": "Midpoint Prediction",
                "page": 80,
                "mn_ids": [],
            }
        ]
        comments = {
            "code_anchors": [
                {"code_anchor_id": "code:function:U_one", "clang_usr": "U_one", "function": "Midpoint", "file": "dsc_codec.c", "line": 1, "permalink": "x"},
                {"code_anchor_id": "code:function:U_two", "clang_usr": "U_two", "function": "MidpointPrediction", "file": "dsc_codec.c", "line": 2, "permalink": "x"},
            ],
            "comments": [],
        }
        manifest = {"spec": {"sha256": "pdf"}, "source": {"source_hashes_sha256": "src"}}
        candidates = {
            "ranked_candidates": [
                {"clang_usr": "U_one", "name": "Midpoint", "production_reachable": True},
                {"clang_usr": "U_two", "name": "MidpointPrediction", "production_reachable": True},
            ]
        }
        links = traceability.proposal_links(anchors, comments, candidates, manifest)
        self.assertEqual([link["function"] for link in links], ["MidpointPrediction"])
        self.assertEqual(links[0]["status"], "PROPOSED")


if __name__ == "__main__":
    unittest.main()
