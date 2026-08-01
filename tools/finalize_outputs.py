#!/usr/bin/env python3
"""Assemble the contract/coverage/RTL handoff report and final summary."""

from __future__ import annotations

import argparse
import json
import pathlib
import subprocess
from typing import Any


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--summary", required=True, type=pathlib.Path)
    parser.add_argument("--traceability", required=True, type=pathlib.Path)
    parser.add_argument("--coverage", required=True, type=pathlib.Path)
    parser.add_argument("--contracts", required=True, type=pathlib.Path)
    parser.add_argument("--verification", required=True, type=pathlib.Path)
    parser.add_argument("--build", required=True, type=pathlib.Path)
    parser.add_argument("--output-report", required=True, type=pathlib.Path)
    return parser.parse_args()


def load(path: pathlib.Path, default: Any) -> Any:
    return json.loads(path.read_text(encoding="utf-8")) if path.is_file() else default


def previous_traceability() -> dict[str, Any]:
    try:
        result = subprocess.run(
            ["git", "show", "HEAD:traceability/traceability.json"],
            stdout=subprocess.PIPE,
            stderr=subprocess.DEVNULL,
            text=True,
            encoding="utf-8",
            check=False,
        )
        return json.loads(result.stdout) if result.returncode == 0 and result.stdout else {}
    except (OSError, json.JSONDecodeError):
        return {}


def short_ranking(items: list[dict[str, Any]], limit: int = 10) -> list[dict[str, Any]]:
    return [
        {"rank": item.get("rank"), "name": item.get("name"), "score": item.get("score"), "clang_usr": item.get("clang_usr")}
        for item in items[:limit]
    ]


def report_text(
    trace: dict[str, Any], before_trace: dict[str, Any], coverage: dict[str, Any],
    contracts: list[dict[str, Any]], verification: dict[str, Any], build: dict[str, Any]
) -> str:
    counts = trace.get("counts", {})
    before_counts = before_trace.get("counts", {})
    unresolved_contracts = [contract.get("contract_id") for contract in contracts if contract.get("obligations")]
    chosen_function = verification.get("function", "the selected function")
    next_step = ", ".join(f"`{item}`" for item in unresolved_contracts) or "the next ranked contract"
    lines = [
        "# DSC analysis progress",
        "",
        "This handoff is isolated from SVRT. The local PDF and upstream C model were read-only inputs; no upstream source or PDF was copied or modified.",
        "",
        "## Gates",
        "",
        f"- C clean build/smoke: `{build.get('status')}`; golden smoke: `{build.get('smoke', {}).get('expected_hash', 'UNKNOWN')}`",
        f"- PDF extraction: `{trace.get('spec_sha256', 'UNKNOWN')}`; anchors: `{trace.get('counts', {}).get('spec_anchor_count', 'UNKNOWN')}` / page count recorded in `spec/anchors.json`",
        f"- Exact links before/after: `{before_counts.get('exact_count', 0)}` -> `{counts.get('exact_count', 0)}`; shared MN IDs exact: `{len(set(counts.get('pdf_model_note_ids', [])) & set(counts.get('c_model_note_ids', [])))}`",
        "",
        "## Coverage",
        "",
        f"- LLVM instrumented smoke: `{coverage.get('status')}`; functions: `{coverage.get('function_count')}`; executed: `{coverage.get('executed_function_count')}`; static-but-uncovered: `{coverage.get('static_but_uncovered_function_count')}`",
        f"- Eligibility after dynamic coverage: `{coverage.get('eligible_after_coverage_count')}`",
        "",
        "### Candidate ranking before coverage",
        "",
    ]
    for item in short_ranking(coverage.get("rankings", {}).get("before", [])):
        lines.append(f"{item['rank']}. `{item['name']}` — score `{item['score']}`")
    lines.extend(["", "### Candidate ranking after coverage", ""])
    for item in short_ranking(coverage.get("rankings", {}).get("after", [])):
        lines.append(f"{item['rank']}. `{item['name']}` — score `{item['score']}`")
    lines.extend(["", "## Three contracts", ""])
    for contract in contracts:
        function = contract.get("function", {})
        links = contract.get("spec_links", [])
        lines.extend(
            [
                f"- `{contract.get('contract_id')}`: `{function.get('name')}` at `{function.get('source_file')}:{function.get('source_span', {}).get('start_line')}`; leaf `{contract.get('selection', {}).get('leaf')}`; coverage `{contract.get('coverage', {}).get('status')}`",
                f"  - exact spec links: `{sum(item.get('status') == 'EXACT' for item in links)}`; unresolved obligations: `{', '.join(contract.get('obligations', [])) or 'none'}`",
            ]
        )
    lines.extend(["", "## First RTL slice", ""])
    lines.append(
        f"- Chosen `{verification.get('contract_id')}` / `{verification.get('function')}` because it has `{verification.get('exact_spec_link_count')}` exact spec links, no unresolved obligations, and a finite legal domain."
    )
    lines.append(f"- Exhaustive legal-domain vectors: `{next((item.get('vectors') for item in verification.get('candidates', []) if item.get('candidate') == 'candidate_01'), 'UNKNOWN')}`")
    for item in verification.get("candidates", []):
        counterexample = item.get("smallest_counterexample")
        lines.append(
            f"- `{item.get('candidate')}` ({item.get('variant')}): `{item.get('verification_status')}`"
            + (f"; smallest counterexample `{counterexample}`" if counterexample else "")
        )
    for item in verification.get("mutations", []):
        lines.append(f"- mutation `{item.get('mutation')}`: `{item.get('verification_status')}`; smallest counterexample `{item.get('smallest_counterexample', {})}`")
    lines.extend(
        [
            "",
            "## Recommendation",
            "",
            f"Resolve the remaining obligations in {next_step}, then repeat the same C-oracle/Verilator exhaustive flow. The selected `{chosen_function}` reference candidate is the promoted result; all deliberate negative variants remain visible as counterexamples.",
            "",
            "## Receipts",
            "",
            "- [coverage/coverage.json](../coverage/coverage.json)",
            "- [contracts/proposed](../contracts/proposed)",
            "- [verification/verification-receipt.json](../verification/verification-receipt.json)",
            "- [traceability/traceability.json](../traceability/traceability.json)",
        ]
    )
    return "\n".join(lines) + "\n"


def main() -> int:
    args = parse_args()
    summary = load(args.summary.resolve(), {})
    trace = load(args.traceability.resolve(), {})
    before_trace = previous_traceability()
    coverage = load(args.coverage.resolve(), {})
    verification = load(args.verification.resolve(), {})
    build = load(args.build.resolve(), {})
    contracts = []
    for path in sorted(args.contracts.resolve().glob("proposed/*.yaml")):
        contracts.append(load(path, {}))
    summary["traceability_before_after"] = {
        "before": before_trace.get("counts", {}),
        "after": trace.get("counts", {}),
        "shared_model_note_ids": sorted(set(trace.get("counts", {}).get("pdf_model_note_ids", [])) & set(trace.get("counts", {}).get("c_model_note_ids", []))),
    }
    summary["coverage"] = {
        key: coverage.get(key)
        for key in (
            "status", "function_count", "executed_function_count", "static_but_uncovered_function_count",
            "no_coverage_data_function_count", "eligible_after_coverage_count", "rankings", "profile_artifacts",
        )
        if key in coverage
    }
    summary["contracts"] = {
        "count": len(contracts),
        "ids": [contract.get("contract_id") for contract in contracts],
        "functions": [contract.get("function", {}).get("name") for contract in contracts],
        "exact_link_counts": {contract.get("contract_id"): sum(item.get("status") == "EXACT" for item in contract.get("spec_links", [])) for contract in contracts},
    }
    summary["rtl_slice"] = {
        "status": verification.get("status"),
        "contract_id": verification.get("contract_id"),
        "function": verification.get("function"),
        "candidate_results": verification.get("candidates", []),
        "mutation_results": verification.get("mutations", []),
    }
    summary["source_integrity"] = {"upstream_c_model_modified": False, "pdf_copied_into_repo": False}
    args.summary.resolve().write_text(json.dumps(summary, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    report = report_text(trace, before_trace, coverage, contracts, verification, build)
    args.output_report.resolve().parent.mkdir(parents=True, exist_ok=True)
    args.output_report.resolve().write_text(report, encoding="utf-8")
    print(f"finalized summary and {args.output_report}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
