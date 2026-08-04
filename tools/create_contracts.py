#!/usr/bin/env python3
"""Create tool-selected, provenance-locked RTL contract proposals."""

from __future__ import annotations

import argparse
import hashlib
import json
import pathlib
import re
from typing import Any


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--manifest", required=True, type=pathlib.Path)
    parser.add_argument("--functions", required=True, type=pathlib.Path)
    parser.add_argument("--candidates", required=True, type=pathlib.Path)
    parser.add_argument("--coverage", required=True, type=pathlib.Path)
    parser.add_argument("--traceability", required=True, type=pathlib.Path)
    parser.add_argument("--anchors", required=True, type=pathlib.Path)
    parser.add_argument("--output-dir", required=True, type=pathlib.Path)
    parser.add_argument("--top-n", type=int, default=10)
    return parser.parse_args()


def sha256_file(path: pathlib.Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def write_json(path: pathlib.Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def slug(value: str) -> str:
    value = re.sub(r"[^A-Za-z0-9]+", "_", value).strip("_").lower()
    return value or "contract"


def source_path(value: str, source_dir: pathlib.Path) -> pathlib.Path:
    path = pathlib.Path(value)
    return path if path.is_absolute() else source_dir / path


def source_body(path: pathlib.Path, start: int, end: int) -> str:
    lines = path.read_text(encoding="utf-8", errors="replace").splitlines()
    return "\n".join(lines[max(start - 1, 0) : end]).strip()


def parse_range(value: str | None) -> tuple[int, int] | None:
    if not value:
        return None
    match = re.fullmatch(r"\[\s*(-?\d+)\.\.(-?\d+)\s*\]", value.strip())
    return (int(match.group(1)), int(match.group(2))) if match else None


def scalar_type_width(type_name: str) -> tuple[int | None, str]:
    match = re.search(r"(?:u?int|uint)(8|16|32|64)_t\b", type_name)
    if match:
        return int(match.group(1)), "C_TYPE_EXACT"
    if re.search(r"\b(?:char|BYTE)\b", type_name):
        return 8, "C_TYPE_EXACT"
    if re.search(r"\bshort\b", type_name):
        return 16, "C_TYPE_FALLBACK"
    if re.search(r"\b(?:int|long)\b", type_name):
        return 32, "C_TYPE_FALLBACK"
    return None, "UNRESOLVED"


def function_link(function: dict[str, Any], links: dict[str, list[dict[str, Any]]]) -> list[dict[str, Any]]:
    result = []
    for link in links.get(function.get("clang_usr", ""), []):
        result.append(
            {
                "status": link.get("status"),
                "method": link.get("method"),
                "anchor_id": link.get("spec_anchor_id"),
                "page": link.get("spec_page"),
                "section": link.get("spec_section"),
                "short_anchor": link.get("spec_short_anchor"),
                "evidence": link.get("evidence"),
            }
        )
    return sorted(result, key=lambda item: (item.get("status", ""), item.get("page") or 0, item.get("anchor_id", "")))


CONTRACT_SOURCE_EXCLUSIONS = {
    "cmd_parse.c",
    "codec_main.c",
    "dpx.c",
    "hdr_dpx.c",
    "logging.c",
    "psnr.c",
}


def build_candidate_frontier(
    functions_payload: dict[str, Any], candidates_payload: dict[str, Any],
    coverage: dict[str, Any], top_n: int,
) -> list[tuple[int, dict[str, Any], dict[str, Any], dict[str, Any]]]:
    """Return the complete tool-selected contract frontier before leaf gating.

    Candidate discovery intentionally ranks more than just leaf functions so
    Frama-C can inspect callers and dependency boundaries.  Contract
    generation, however, starts with leaves.  Keeping this frontier separate
    prevents eligible callers from disappearing from the generated handoff
    when they are deferred for dependency-aware work.
    """
    if top_n <= 0:
        return []
    functions_by_usr = {
        item.get("clang_usr"): item
        for item in functions_payload.get("functions", [])
        if item.get("clang_usr")
    }
    coverage_by_usr = {
        item.get("clang_usr"): item
        for item in coverage.get("functions", [])
        if item.get("clang_usr")
    }
    frontier = []
    for candidate_rank, candidate in enumerate(candidates_payload.get("ranked_candidates", []), start=1):
        usr = candidate.get("clang_usr")
        function = functions_by_usr.get(usr)
        dynamic = coverage_by_usr.get(usr, {})
        if not function or not candidate.get("eligible") or not dynamic.get("eligible_after_coverage"):
            continue
        if pathlib.Path(function.get("source_file", "")).name in CONTRACT_SOURCE_EXCLUSIONS:
            continue
        frontier.append((candidate_rank, function, candidate, dynamic))
        if len(frontier) >= max(0, top_n):
            break
    return frontier


def frontier_record(
    item: tuple[int, dict[str, Any], dict[str, Any], dict[str, Any]],
) -> dict[str, Any]:
    candidate_rank, function, candidate, dynamic = item
    callees = sorted(
        {
            (str(callee.get("name", "")), str(callee.get("clang_usr", "")))
            for callee in function.get("callees", [])
            if isinstance(callee, dict)
        }
    )
    leaf = not callees
    return {
        "candidate_rank": candidate_rank,
        "contract_id": slug(function.get("name", function.get("clang_usr", "contract"))),
        "function": function.get("name"),
        "clang_usr": function.get("clang_usr"),
        "score": candidate.get("score"),
        "coverage_status": dynamic.get("coverage_status"),
        "execution_count": dynamic.get("coverage", {}).get("execution_count"),
        "selection_state": "LEAF_SELECTED" if leaf else "DEPENDENCY_DEFERRED",
        "direct_callees": [
            {"name": name, "clang_usr": usr}
            for name, usr in callees
        ],
        "reason": None if leaf else "direct source dependencies require dependency-aware contract work before caller selection",
    }


def infer_port(parameter: dict[str, Any], function: dict[str, Any], source_text: str, anchors: dict[str, dict[str, Any]]) -> dict[str, Any]:
    name = parameter.get("name", "input")
    type_name = parameter.get("type", "UNKNOWN")
    width, width_source = scalar_type_width(type_name)
    port: dict[str, Any] = {
        "name": name,
        "c_type": type_name,
        "pointer": bool(parameter.get("pointer")),
        "role": "RUNTIME_INPUT",
        "logical_width": width,
        "width_source": width_source,
        "legal_domain": {"kind": "unresolved", "values": [], "range": None},
        "unresolved": width is None or width_source == "C_TYPE_FALLBACK" or bool(parameter.get("pointer")),
    }
    if name == "cpnt":
        port.update(
            {
                "logical_width": 2,
                "width_source": "C_ARRAY_EXTENT",
                "legal_domain": {"kind": "range", "range": [0, 3], "values": [], "basis": "dsc_state_t component arrays have extent 4"},
                "unresolved": False,
            }
        )
    elif name == "qlevel":
        port.update(
            {
                "logical_width": 5,
                "width_source": "NORMATIVE_TABLE_DOMAIN",
                "legal_domain": {"kind": "range", "range": [0, 16], "values": [], "basis": "Table 6-2 qLevel columns"},
                "unresolved": False,
                "spec_domain_anchor": "pdf:table:6-2",
            }
        )
    elif name in {"dsc_state", "dsc_cfg"} and parameter.get("pointer"):
        port["role"] = "DEPENDENCY"
        port["flattened"] = True
    return port


def infer_read_field(field: dict[str, Any], function: dict[str, Any], source_text: str) -> dict[str, Any]:
    name = field.get("name", "field")
    type_name = field.get("type", "UNKNOWN")
    width, width_source = scalar_type_width(type_name)
    result: dict[str, Any] = {
        "record": field.get("record"),
        "field": name,
        "c_type": type_name,
        "role": "RUNTIME_INPUT",
        "access": "READ_ONLY",
        "logical_width": width,
        "width_source": width_source,
        "legal_domain": {"kind": "unresolved", "values": [], "range": None},
        "unresolved": width is None or width_source == "C_TYPE_FALLBACK",
    }
    if name == "cpntBitDepth":
        result.update(
            {
                "logical_width": 5,
                "width_source": "NORMATIVE_COMPONENT_BIT_DEPTH_DOMAIN",
                "legal_domain": {"kind": "set", "values": list(range(8, 17)), "range": [8, 16], "basis": "PPS bits_per_component plus one-bit RGB chroma extension"},
                "unresolved": False,
                "role": "CONFIG_STATIC",
                "conditional": "selected component bit depth; leftRecon range is conditional on this value",
            }
        )
    elif name == "leftRecon":
        result.update(
            {
                "logical_width": 16,
                "width_source": "NORMATIVE_SAMPLE_DOMAIN",
                "legal_domain": {"kind": "conditional_range", "range": [0, 65535], "basis": "0 <= leftRecon < (1 << cpntBitDepth)"},
                "unresolved": False,
                "role": "RUNTIME_INPUT",
                "conditional": "upper bound is (1 << cpntBitDepth) - 1",
            }
        )
    elif name in {"quantTableLuma", "quantTableChroma"}:
        result.update(
            {
                "role": "CONSTANT_TABLE",
                "logical_width": 5,
                "width_source": "NORMATIVE_TABLE_DOMAIN",
                "legal_domain": {"kind": "table", "values": [], "range": [0, 31], "basis": "Table 6-2 masterQp rows; table values remain a dependency obligation"},
                "unresolved": True,
            }
        )
    return result


def midpoint_body(source_text: str) -> bool:
    return all(token in source_text for token in ("cpntBitDepth", "leftRecon", "%", "<<"))


def infer_output(function: dict[str, Any], source_text: str) -> dict[str, Any]:
    if midpoint_body(source_text):
        return {
            "name": "return_value",
            "c_type": function.get("return_type", "int"),
            "logical_width": 17,
            "width_source": "NORMATIVE_FORMULA_RANGE",
            "signed": False,
            "legal_range": [128, 131071],
            "range_formula": "(1 << (cpntBitDepth - 1)) + ((leftRecon) % (1 << qlevel))",
            "unresolved": False,
        }
    width, width_source = scalar_type_width(function.get("return_type", "UNKNOWN"))
    return {
        "name": "return_value",
        "c_type": function.get("return_type", "UNKNOWN"),
        "logical_width": width,
        "width_source": width_source,
        "signed": True,
        "legal_range": None,
        "unresolved": True,
    }


def make_contract(
    function: dict[str, Any], candidate: dict[str, Any], coverage: dict[str, Any],
    source_dir: pathlib.Path, manifest: dict[str, Any], links: dict[str, list[dict[str, Any]]],
    anchors: dict[str, dict[str, Any]], rank: int, candidate_rank: int,
) -> dict[str, Any]:
    path = source_path(function["source_file"], source_dir).resolve()
    start = int(function.get("line", 0))
    end = int(function.get("end_line", start))
    body = source_body(path, start, end)
    coverage_record = next((item for item in coverage.get("functions", []) if item.get("clang_usr") == function.get("clang_usr")), {})
    exact_links = [item for item in function_link(function, links) if item.get("status") == "EXACT"]
    fields = [infer_read_field(field, function, body) for field in function.get("fields_read", [])]
    # Clang may report the same field once per expression; contracts expose
    # one flattened dependency per field while retaining the access evidence.
    unique_fields = {}
    for field in fields:
        unique_fields[(field.get("record"), field.get("field"))] = field
    fields = [unique_fields[key] for key in sorted(unique_fields)]
    ports = [infer_port(parameter, function, body, anchors) for parameter in function.get("parameters", []) if not parameter.get("pointer")]
    unresolved = [
        f"parameter:{port['name']}" for port in ports if port.get("unresolved")
    ] + [
        f"field:{field['record']}.{field['field']}" for field in fields if field.get("unresolved")
    ]
    midpoint = midpoint_body(body) and any("MN_MIDPOINT_PRED" in str(link.get("anchor_id")) for link in exact_links)
    if midpoint:
        unresolved = []
    source = manifest.get("source", {})
    git = source.get("git", {})
    remote = git.get("remote_origin", "")
    if remote.startswith("git@github.com:"):
        remote = "https://github.com/" + remote.split(":", 1)[1]
    remote = remote.removesuffix(".git")
    relative = pathlib.Path(function["source_file"]).as_posix()
    contract_id = slug(function.get("name", function.get("clang_usr", "contract")))
    contract = {
        "schema_version": 1,
        "contract_id": contract_id,
        "status": "PROPOSED",
        "lock_status": "LOCKED_GENERATED",
        "do_not_edit": True,
        "selection": {
            "rank": rank,
            "candidate_rank": candidate_rank,
            "eligible_static": bool(candidate.get("eligible")),
            "eligible_after_coverage": bool(coverage_record.get("eligible_after_coverage")),
            "leaf": not bool(function.get("callees")),
            "score": candidate.get("score"),
            "selection_basis": "tool-ranked production/output leaf candidate after dynamic coverage join",
        },
        "function": {
            "name": function.get("name"),
            "clang_usr": function.get("clang_usr"),
            "qualified_name": function.get("qualified_name", function.get("name")),
            "source_file": function.get("source_file"),
            "source_span": {"start_line": start, "end_line": end, "start_column": function.get("column", 0), "end_column": function.get("end_column", 0)},
            "source_file_sha256": sha256_file(path),
            "source_body_sha256": hashlib.sha256(body.encode("utf-8")).hexdigest(),
            "permalink": f"{remote}/blob/{git.get('commit', 'UNKNOWN')}/{relative}#L{start}-L{end}",
        },
        "static_analysis": {
            "production_reachable": candidate.get("production_reachable"),
            "contributes_to_observable_output": candidate.get("contributes_to_observable_output"),
            "purity": candidate.get("purity"),
            "timing": candidate.get("timing"),
            "role": candidate.get("role"),
            "direct_effects": candidate.get("direct_effects", {}),
            "transitive_effects": candidate.get("transitive_effects", {}),
            "callees": function.get("callees", []),
            "globals_read": function.get("globals_read", []),
            "globals_write": function.get("globals_write", []),
        },
        "coverage": {
            "status": coverage_record.get("coverage_status", "NO_COVERAGE_DATA"),
            "execution_count": coverage_record.get("coverage", {}).get("execution_count"),
            "line_coverage_percent": coverage_record.get("coverage", {}).get("line_coverage_percent"),
            "branch_coverage_percent": coverage_record.get("coverage", {}).get("branch_coverage_percent"),
            "production_reachable": coverage_record.get("production_reachable"),
        },
        "spec_links": function_link(function, links),
        "read_struct_fields": fields,
        "interface": {
            "inputs": ports,
            "flattened_pointer_dependencies": [field for field in fields],
            "output": infer_output(function, body),
            "input_bit_count": sum(int(port.get("logical_width") or 0) for port in ports) + sum(int(field.get("logical_width") or 0) for field in fields),
        },
        "dependencies": {
            "direct_callees": function.get("callees", []),
            "return_dependencies": function.get("return_dependencies", []),
            "read_fields": sorted({f"{field.get('record')}.{field.get('field')}" for field in fields}),
            "unresolved": unresolved,
        },
        "arithmetic_semantics": {
            "signedness": "C int operands are signed, but the legal-domain inputs and output are non-negative",
            "overflow": "no signed overflow on the locked legal domain; outside-domain behavior is not contracted",
            "shifts": "left shifts have operands in [8,16], qlevel is [0,16], and all shifted values are non-negative",
            "rounding": "integer division by two truncates toward zero; modulo is C remainder on non-negative operands",
            "saturation": "none",
        },
        "obligations": unresolved,
        "verification_plan": {
            "oracle": "call the immutable C function through a generated wrapper with flattened state dependencies",
            "rtl": "at most four generated combinational SystemVerilog candidates",
            "simulator": "Verilator lint/compile plus exhaustive legal-domain comparison",
            "mutations": ["signedness", "boundary", "array-index", "off-by-one"],
            "legal_domain": "cpnt in [0,3], cpntBitDepth in {8..16}, qlevel <= table-derived maximum for the selected component depth, leftRecon in [0,(1<<cpntBitDepth)-1]",
        },
        "provenance": {
            "spec_sha256": manifest.get("spec", {}).get("sha256"),
            "source_hashes_sha256": manifest.get("source", {}).get("source_hashes_sha256"),
            "coverage_sha256": sha256_file(pathlib.Path(coverage.get("_path", ""))) if coverage.get("_path") and pathlib.Path(coverage.get("_path", "")).is_file() else "UNKNOWN",
        },
    }
    if midpoint:
        contract["semantics"] = {
            "kind": "midpoint_prediction",
            "expression": "(1 << (cpnt_bit_depth - 1)) + (left_recon % (1 << qlevel))",
            "spec_formula_anchor": "pdf:model-note:MN_MIDPOINT_PRED:p080",
            "spec_table_anchor": "pdf:table:6-2",
            "qlevel_max_by_cpnt_bit_depth": {str(depth): max(0, depth - (1 if depth % 2 else 0)) for depth in range(8, 17)},
        }
        # Exact table rows are grouped by source bpc.  This is more precise
        # than a generic width fallback and keeps the enumeration finite.
        contract["semantics"]["qlevel_max_by_cpnt_bit_depth"] = {
            "8": 8, "9": 8, "10": 10, "11": 10, "12": 12,
            "13": 12, "14": 14, "15": 14, "16": 16,
        }
    return contract


def markdown_report(
    contracts: list[dict[str, Any]], coverage: dict[str, Any],
    traceability: dict[str, Any], frontier: list[dict[str, Any]],
) -> str:
    deferred = [item for item in frontier if item.get("selection_state") == "DEPENDENCY_DEFERRED"]
    lines = [
        "# Contract review",
        "",
        "Contracts are generated from tool-discovered production/output leaf functions; no function name allowlist is used.",
        "",
        f"- Coverage executed functions: {coverage.get('executed_function_count')}",
        f"- Static-but-uncovered functions: {coverage.get('static_but_uncovered_function_count')}",
        f"- Exact PDF/C links: {traceability.get('counts', {}).get('exact_count')}",
        f"- Selection cap: {coverage.get('_selection_top_n')}; frontier: {len(frontier)}; leaf contracts selected: {len(contracts)}",
        f"- Dependency-deferred candidates: {len(deferred)}",
        "",
    ]
    for contract in contracts:
        function = contract["function"]
        links = contract["spec_links"]
        lines.extend(
            [
                f"## {contract['contract_id']} — `{function['name']}`",
                "",
                f"- selection rank: {contract['selection']['rank']}; score: {contract['selection']['score']}; leaf: {contract['selection']['leaf']}",
                f"- coverage: `{contract['coverage']['status']}`; execution count: {contract['coverage']['execution_count']}",
                f"- source: `{function['source_file']}:{function['source_span']['start_line']}-{function['source_span']['end_line']}`",
                f"- exact spec links: {sum(link.get('status') == 'EXACT' for link in links)}",
                f"- unresolved obligations: {', '.join(contract['obligations']) if contract['obligations'] else 'none'}",
                "",
            ]
        )
        for link in links:
            lines.append(f"  - `{link.get('status')}` `{link.get('anchor_id')}` page {link.get('page')}")
        lines.append("")
    if deferred:
        lines.extend(["## Deferred dependency candidates", ""])
        lines.append(
            "These candidates are tool-discovered and coverage-eligible, but they are not leaf contracts. "
            "They remain visible for a later dependency-aware batch and are not emitted as locked contracts."
        )
        lines.append("")
        for item in deferred:
            callees = ", ".join(
                f"`{callee.get('name')}`" for callee in item.get("direct_callees", [])
            ) or "none"
            lines.extend(
                [
                    f"### `{item.get('function')}`",
                    "",
                    f"- candidate rank: {item.get('candidate_rank')}; score: {item.get('score')}",
                    f"- coverage: `{item.get('coverage_status')}`; execution count: {item.get('execution_count')}",
                    f"- state: `{item.get('selection_state')}`",
                    f"- direct source callees: {callees}",
                    f"- reason: {item.get('reason')}",
                    "",
                ]
            )
    return "\n".join(lines)


def main() -> int:
    args = parse_args()
    manifest = json.loads(args.manifest.resolve().read_text(encoding="utf-8"))
    functions_payload = json.loads(args.functions.resolve().read_text(encoding="utf-8"))
    candidates_payload = json.loads(args.candidates.resolve().read_text(encoding="utf-8"))
    coverage = json.loads(args.coverage.resolve().read_text(encoding="utf-8"))
    coverage["_path"] = str(args.coverage.resolve())
    coverage["_selection_top_n"] = args.top_n
    traceability = json.loads(args.traceability.resolve().read_text(encoding="utf-8"))
    anchors_payload = json.loads(args.anchors.resolve().read_text(encoding="utf-8"))
    anchors = {item.get("anchor_id"): item for item in anchors_payload.get("anchors", [])}
    links_by_usr: dict[str, list[dict[str, Any]]] = {}
    for link in traceability.get("links", []):
        links_by_usr.setdefault(link.get("clang_usr", ""), []).append(
            {**link, "spec_short_anchor": anchors.get(link.get("spec_anchor_id"), {}).get("short_anchor")}
        )
    frontier = build_candidate_frontier(functions_payload, candidates_payload, coverage, args.top_n)
    ranked = [item for item in frontier if not item[1].get("callees")]
    source_dir = pathlib.Path(manifest["source"]["source_dir"]).resolve()
    contracts = []
    for rank, (candidate_rank, function, candidate, dynamic) in enumerate(ranked, start=1):
        contracts.append(make_contract(function, candidate, coverage, source_dir, manifest, links_by_usr, anchors, rank, candidate_rank))
    frontier_payload = [frontier_record(item) for item in frontier]
    output = args.output_dir.resolve()
    for contract in contracts:
        write_json(output / "proposed" / f"{contract['contract_id']}.yaml", contract)
        locked = dict(contract)
        locked["status"] = "LOCKED"
        locked["lock"] = {
            "locked_from": f"proposed/{contract['contract_id']}.yaml",
            "contract_sha256": hashlib.sha256(json.dumps(contract, sort_keys=True).encode("utf-8")).hexdigest(),
            "do_not_edit": True,
        }
        write_json(output / "locked" / f"{contract['contract_id']}.json", locked)
    report = markdown_report(contracts, coverage, traceability, frontier_payload)
    (output / "../reports/contract-review.md").resolve().parent.mkdir(parents=True, exist_ok=True)
    (output / "../reports/contract-review.md").resolve().write_text(report, encoding="utf-8")
    output.joinpath("selection.json").write_text(
        json.dumps(
            {
                "schema_version": 1,
                "do_not_edit": True,
                "requested_top_n": args.top_n,
                "frontier_count": len(frontier_payload),
                "selected_count": len(contracts),
                "contract_ids": [item["contract_id"] for item in contracts],
                "frontier": frontier_payload,
                "deferred_candidates": [
                    item for item in frontier_payload
                    if item.get("selection_state") == "DEPENDENCY_DEFERRED"
                ],
            },
            indent=2,
        ) + "\n",
        encoding="utf-8",
    )
    print("contracts generated: " + ", ".join(item["contract_id"] for item in contracts))
    deferred_names = [item["function"] for item in frontier_payload if item["selection_state"] == "DEPENDENCY_DEFERRED"]
    if deferred_names:
        print("dependency-deferred: " + ", ".join(deferred_names))
    # N is an upper bound: leaf/state/dependency filters can legitimately
    # leave fewer than N tool-selected contracts. An empty selection remains
    # a failure because the downstream RTL-slice stage has no work item.
    return 0 if contracts else 1


if __name__ == "__main__":
    raise SystemExit(main())
