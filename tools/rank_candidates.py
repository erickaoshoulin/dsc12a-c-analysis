#!/usr/bin/env python3
"""Infer production reachability and rank combinational DUT candidates.

Selection is derived from the linked executable's entry symbol, the Clang call
graph, parameter/dataflow shape, effects, and loop proofs.  No source function
name is an allowlist or a selection input.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import pathlib
import re
from collections import defaultdict, deque
from typing import Any


OUTPUT_CALLS = {"fwrite", "fputc", "fputs", "putc", "putchar", "write", "send"}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--raw", required=True, type=pathlib.Path)
    parser.add_argument("--build-receipt", required=True, type=pathlib.Path)
    parser.add_argument("--output", required=True, type=pathlib.Path)
    parser.add_argument("--report", required=True, type=pathlib.Path)
    parser.add_argument("--top-n", type=int, default=10)
    return parser.parse_args()


def sha256_file(path: pathlib.Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def is_source_function(function: dict[str, Any]) -> bool:
    source_file = function.get("source_file", "")
    return bool(source_file and not source_file.startswith("<external>/"))


def function_graph(functions: list[dict[str, Any]]) -> tuple[dict[str, dict], dict[str, set[str]], dict[str, set[str]]]:
    source = {item.get("clang_usr", "UNKNOWN"): item for item in functions if is_source_function(item)}
    forward: dict[str, set[str]] = {usr: set() for usr in source}
    reverse: dict[str, set[str]] = {usr: set() for usr in source}
    for usr, function in source.items():
        for callee in function.get("callees", []):
            callee_usr = callee.get("clang_usr", "UNKNOWN")
            if callee_usr in source:
                forward[usr].add(callee_usr)
                reverse[callee_usr].add(usr)
    return source, forward, reverse


def reachable(roots: set[str], forward: dict[str, set[str]]) -> set[str]:
    seen: set[str] = set()
    queue = deque(sorted(roots))
    while queue:
        node = queue.popleft()
        if node in seen:
            continue
        seen.add(node)
        queue.extend(sorted(forward.get(node, set()) - seen))
    return seen


def ancestors(nodes: set[str], reverse: dict[str, set[str]]) -> set[str]:
    seen = set(nodes)
    queue = deque(sorted(nodes))
    while queue:
        node = queue.popleft()
        for parent in sorted(reverse.get(node, set())):
            if parent not in seen:
                seen.add(parent)
                queue.append(parent)
    return seen


def has_output_call(function: dict[str, Any]) -> bool:
    return any(
        call.get("category") == "file_io"
        and call.get("name", "").split("::")[-1].lower() in OUTPUT_CALLS
        for call in function.get("calls", [])
    )


def boundary_shape(function: dict[str, Any]) -> bool:
    types = [param.get("type", "").lower() for param in function.get("parameters", [])]
    has_config = any("dsc_cfg_t" in value for value in types)
    has_picture = any("pic_t" in value for value in types)
    has_bitstream = any("unsigned char" in value or "char *" in value for value in types)
    return has_config and has_picture and has_bitstream


def direct_effects(function: dict[str, Any]) -> dict[str, Any]:
    effects = function.get("effects", {})
    state_write = bool(
        function.get("globals_write")
        or function.get("fields_write")
        or function.get("static_mutable_state")
        or any(param.get("mode") == "WRITES_THROUGH" for param in function.get("pointer_parameters", []))
    )
    external_categories = {call.get("category") for call in function.get("calls", [])}
    return {
        "state_write": state_write,
        "io": bool(effects.get("file_io") or "file_io" in external_categories),
        "allocation": bool(effects.get("malloc") or "malloc" in external_categories),
        "logging": bool(effects.get("logging") or "logging" in external_categories),
        "assertion": bool(effects.get("assert") or "assert" in external_categories),
        "indirect_call": bool(effects.get("indirect_call")),
        "unknown_facts": list(function.get("unknown_facts", [])),
    }


def transitive_effects(
    source: dict[str, dict[str, Any]], forward: dict[str, set[str]]
) -> dict[str, dict[str, Any]]:
    result = {usr: direct_effects(function) for usr, function in source.items()}
    changed = True
    while changed:
        changed = False
        for usr in sorted(source):
            combined = dict(result[usr])
            unknown = set(combined.get("unknown_facts", []))
            for callee in sorted(forward.get(usr, set())):
                child = result[callee]
                for key in ("state_write", "io", "allocation", "logging", "assertion", "indirect_call"):
                    combined[key] = bool(combined[key] or child[key])
                unknown.update(child.get("unknown_facts", []))
            combined["unknown_facts"] = sorted(unknown)
            if combined != result[usr]:
                result[usr] = combined
                changed = True
    return result


def transitive_bounded(usr: str, source: dict[str, dict[str, Any]], forward: dict[str, set[str]]) -> bool:
    seen: set[str] = set()
    queue = [usr]
    while queue:
        current = queue.pop()
        if current in seen:
            continue
        seen.add(current)
        function = source[current]
        if any(not loop.get("has_fixed_trip_count") for loop in function.get("loops", [])):
            return False
        queue.extend(forward.get(current, set()))
    return True


def normalize_tokens(value: str) -> set[str]:
    value = re.sub(r"([a-z0-9])([A-Z])", r"\1 \2", value)
    return {
        token.lower()
        for token in re.findall(r"[A-Za-z][A-Za-z0-9]+", value)
        if token.lower() not in {"the", "and", "source", "model"}
    }


def classification(
    function: dict[str, Any],
    usr: str,
    source: dict[str, dict[str, Any]],
    effects: dict[str, dict[str, Any]],
    production: set[str],
    output_contributing: set[str],
    bounded: bool,
) -> dict[str, Any]:
    direct = direct_effects(function)
    transitive = effects[usr]
    production_reachable = usr in production
    contributes = usr in output_contributing
    purity = "UNKNOWN" if transitive["indirect_call"] or transitive["unknown_facts"] else (
        "IMPURE"
        if any(transitive[key] for key in ("state_write", "io", "allocation", "logging", "assertion"))
        else "PURE"
    )
    timing = (
        "UNKNOWN"
        if purity == "UNKNOWN" or not bounded
        else "STATEFUL"
        if transitive["state_write"]
        else "COMBINATIONAL"
    )
    config_access = any(
        access.get("record") == "dsc_cfg_t"
        for access in [*function.get("fields_read", []), *function.get("fields_write", [])]
    )
    source_file = function.get("source_file", "")
    if production_reachable and contributes:
        role = "DUT"
    elif config_access:
        role = "CONFIG"
    elif transitive["assertion"]:
        role = "CHECKER"
    elif transitive["io"] or transitive["allocation"] or transitive["logging"]:
        role = "HOST_IO"
    elif "test" in source_file.lower():
        role = "TEST"
    else:
        role = "UNRESOLVED"

    criteria = {
        "production_reachable": production_reachable,
        "contributes_to_observable_output": contributes,
        "no_direct_or_transitive_state_write": not transitive["state_write"],
        "no_io_allocation_or_logging": not any(
            transitive[key] for key in ("io", "allocation", "logging")
        ),
        "bounded_computation": bounded,
    }
    eligible = all(criteria.values())
    evidence = [
        "production reachability is a graph traversal from linked executable entry symbols",
        "observable output is inferred from output file calls and codec boundary dataflow shape",
        f"direct effects: {json.dumps(direct, sort_keys=True)}",
        f"transitive effects: {json.dumps(transitive, sort_keys=True)}",
        "all reachable loops have fixed AST bounds" if bounded else "at least one reachable loop has UNKNOWN bounds",
    ]
    score = 0.0
    score += 30.0 if production_reachable else 0.0
    score += 30.0 if contributes else 0.0
    score += 20.0 if purity == "PURE" else 0.0
    score += 15.0 if timing == "COMBINATIONAL" else 0.0
    score += 5.0 if bounded else 0.0
    score -= min(len(function.get("callees", [])), 20) * 0.05
    confidence = 0.95 if eligible else 0.75 if production_reachable and contributes else 0.55
    return {
        "clang_usr": usr,
        "name": function.get("name", "UNKNOWN"),
        "qualified_name": function.get("qualified_name", function.get("name", "UNKNOWN")),
        "source_file": source_file,
        "line": function.get("line", 0),
        "column": function.get("column", 0),
        "purity": purity,
        "timing": timing,
        "role": role,
        "production_reachable": production_reachable,
        "contributes_to_observable_output": contributes,
        "bounded_computation": bounded,
        "direct_effects": direct,
        "transitive_effects": transitive,
        "criteria": criteria,
        "eligible": eligible,
        "score": round(score, 3),
        "confidence": confidence,
        "evidence": evidence,
    }


def render_report(payload: dict[str, Any]) -> str:
    lines = [
        "# Auto-discovered DUT candidates",
        "",
        "Candidate selection is derived from the linked executable entry symbol, Clang call/dataflow facts, effects, and loop proofs. No source function-name allowlist is used.",
        "",
        f"- Source functions: {payload['counts']['source_functions']}",
        f"- Production reachable: {payload['counts']['production_reachable']}",
        f"- Output contributing: {payload['counts']['output_contributing']}",
        f"- Eligible candidates: {payload['counts']['eligible_candidates']}",
        f"- Selected for Eva/From: {len(payload['selected_for_frama'])}",
        "",
        "## Ranked candidates",
        "",
    ]
    for index, item in enumerate(payload["ranked_candidates"], start=1):
        lines.extend(
            [
                f"### {index}. `{item['name']}`",
                "",
                f"- Score: `{item['score']}`; confidence: `{item['confidence']}`; role: `{item['role']}`",
                f"- Purity: `{item['purity']}`; timing: `{item['timing']}`; bounded: `{item['bounded_computation']}`",
                f"- Production reachable: `{item['production_reachable']}`; output contributing: `{item['contributes_to_observable_output']}`",
                f"- Source: `{item['source_file']}:{item['line']}`",
                f"- Eligible: `{item['eligible']}`",
                "- Evidence:",
            ]
        )
        lines.extend(f"  - {evidence}" for evidence in item["evidence"])
        lines.append("")
    return "\n".join(lines).rstrip() + "\n"


def main() -> int:
    args = parse_args()
    raw = json.loads(args.raw.resolve().read_text(encoding="utf-8"))
    build = json.loads(args.build_receipt.resolve().read_text(encoding="utf-8"))
    functions = raw.get("functions", [])
    source, forward, reverse = function_graph(functions)

    entry_symbols = build.get("binary", {}).get("symbols", {}).get("entry_symbols", [])
    roots = {
        usr
        for usr, function in source.items()
        if function.get("name") in set(entry_symbols)
    }
    root_method = "linked_executable_entry_symbols"
    if not roots:
        roots = {
            usr
            for usr, function in source.items()
            if not function.get("callers") and not function.get("is_static")
        }
        root_method = "source_functions_without_callers_fallback"
    production = reachable(roots, forward)
    sink_nodes = {usr for usr, function in source.items() if has_output_call(function)}
    sink_ancestors = ancestors(sink_nodes, reverse)
    boundary_roots = {usr for usr in production if boundary_shape(source[usr])}
    boundary_descendants = reachable(boundary_roots, forward)
    output_contributing = (sink_ancestors | boundary_descendants) & production
    effects = transitive_effects(source, forward)

    records = []
    for usr in sorted(source):
        records.append(
            classification(
                source[usr],
                usr,
                source,
                effects,
                production,
                output_contributing,
                transitive_bounded(usr, source, forward),
            )
        )
    ranked = sorted(
        records,
        key=lambda item: (
            not item["eligible"],
            -item["score"],
            item["name"],
            item["source_file"],
            item["line"],
            item["clang_usr"],
        ),
    )
    eligible = [item for item in ranked if item["eligible"]]
    selected = eligible[: max(0, args.top_n)]
    selected_names = []
    seen_names: set[str] = set()
    for item in selected:
        if item["name"] not in seen_names:
            selected_names.append(item["name"])
            seen_names.add(item["name"])
    payload = {
        "schema_version": 2,
        "status": "OK",
        "do_not_edit": True,
        "raw_sha256": sha256_file(args.raw.resolve()),
        "build_receipt_sha256": sha256_file(args.build_receipt.resolve()),
        "selection": {
            "method": root_method,
            "top_n": args.top_n,
            "entry_symbols": sorted(entry_symbols),
            "root_usrs": sorted(roots),
            "output_sink_usrs": sorted(sink_nodes),
            "boundary_root_usrs": sorted(boundary_roots),
            "criteria": [
                "production_reachable",
                "contributes_to_observable_output",
                "no_direct_or_transitive_state_write",
                "no_io_allocation_or_logging",
                "bounded_computation",
            ],
        },
        "counts": {
            "source_functions": len(source),
            "production_reachable": len(production),
            "output_contributing": len(output_contributing),
            "eligible_candidates": len(eligible),
        },
        "selected_for_frama": selected_names,
        "ranked_candidates": ranked,
        "functions": records,
    }
    args.output.resolve().parent.mkdir(parents=True, exist_ok=True)
    args.output.resolve().write_text(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    args.report.resolve().parent.mkdir(parents=True, exist_ok=True)
    args.report.resolve().write_text(render_report(payload), encoding="utf-8")
    print(f"auto-discovered {len(eligible)} eligible candidates; selected {len(selected_names)} for Frama-C")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
