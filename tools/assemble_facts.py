#!/usr/bin/env python3
"""Assemble Clang, Eva, and From outputs into deterministic facts/reports.

This module only consumes JSON emitted by the LibTooling executable and text
emitted by Frama-C. It intentionally contains no C lexer/parser and does not
infer a fact from a function name.
"""

from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import json
import pathlib
import re
import subprocess
import sys
from collections import defaultdict
from typing import Any

CHECK_PATTERNS = {
    "array_index_bounds": re.compile(
        r"out of bounds|array.*bound|index.*bound|invalid.*index", re.I
    ),
    "invalid_shifts": re.compile(
        r"invalid.*shift|shift.*negative|shift.*too large|left shift|right shift", re.I
    ),
    "signed_overflow": re.compile(r"signed overflow|integer overflow", re.I),
    "pointer_validity": re.compile(
        r"invalid.*(pointer|dereference)|dangling|pointer.*valid", re.I
    ),
    "unreachable_branches": re.compile(r"unreachable|dead branch", re.I),
}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--raw", required=True, type=pathlib.Path)
    parser.add_argument("--source-dir", required=True, type=pathlib.Path)
    parser.add_argument("--output-dir", required=True, type=pathlib.Path)
    parser.add_argument("--source-revision", required=True)
    parser.add_argument("--clang-version", required=True)
    parser.add_argument("--frama-c-version", required=True)
    parser.add_argument("--compile-commands", required=True, type=pathlib.Path)
    parser.add_argument("--compile-check", required=True, type=pathlib.Path)
    parser.add_argument("--input-manifest", required=True, type=pathlib.Path)
    parser.add_argument("--build-receipt", required=True, type=pathlib.Path)
    parser.add_argument("--candidates", required=True, type=pathlib.Path)
    parser.add_argument("--traceability", required=True, type=pathlib.Path)
    parser.add_argument("--analysis-command", action="append", default=[])
    parser.add_argument("--frama-output-dir", required=True, type=pathlib.Path)
    return parser.parse_args()


def canonical_json(value: Any) -> bytes:
    return json.dumps(
        value, ensure_ascii=False, sort_keys=True, separators=(",", ":")
    ).encode("utf-8")


def write_json(path: pathlib.Path, value: Any) -> None:
    path.write_text(
        json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )


def source_hashes(source_dir: pathlib.Path) -> list[dict[str, str]]:
    result = []
    for path in sorted(
        p for p in source_dir.rglob("*") if p.is_file() and p.suffix in {".c", ".h"}
    ):
        result.append(
            {
                "path": path.relative_to(source_dir).as_posix(),
                "sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
            }
        )
    return result


def file_sha256(path: pathlib.Path) -> str:
    if not path.is_file():
        return "UNKNOWN"
    return hashlib.sha256(path.read_bytes()).hexdigest()


def first_line(value: str) -> str:
    return value.splitlines()[0].strip() if value.splitlines() else value.strip()


def location_key(location: dict[str, Any]) -> tuple[Any, ...]:
    return (
        location.get("file", ""),
        location.get("line", 0),
        location.get("column", 0),
    )


def unique_sorted(values: list[Any], key=None) -> list[Any]:
    if key is None:
        key = lambda value: json.dumps(value, sort_keys=True)
    result = {}
    for value in values:
        result[key(value)] = value
    return [result[item] for item in sorted(result)]


def parse_eva(path: pathlib.Path, function_name: str) -> dict[str, Any]:
    if not path.exists():
        return {
            "status": "UNKNOWN",
            "warnings": [],
            "values": {},
            "parameter_ranges": {},
            "return_range": "UNKNOWN",
            "checks": {name: "UNKNOWN" for name in CHECK_PATTERNS},
            "raw_log": path.name,
        }
    lines = path.read_text(encoding="utf-8", errors="replace").splitlines()
    warnings = []
    values: dict[str, str] = {}
    active = False
    current_warning = None

    def flush_warning() -> None:
        nonlocal current_warning
        if current_warning is not None:
            warnings.append(current_warning)
            current_warning = None

    range_pattern = re.compile(
        r"^\s+(?P<name>\\?[_A-Za-z][\w$]*(?:\[[^\]]+\])?)\s*(?:∈|in)\s+(?P<range>.+)$"
    )
    for number, line in enumerate(lines, start=1):
        if current_warning is not None and line.startswith("["):
            flush_warning()
        if re.search(
            rf"\[eva:final-states\]\s+Values at end of function\s+{re.escape(function_name)}\b",
            line,
            re.I,
        ):
            active = True
        elif re.search(r"\[eva:final-states\]\s+Values at end of function\s+\w+", line, re.I):
            active = False
        elif re.match(r"\[eva:summary\]", line):
            active = False
        match = range_pattern.search(line)
        if active and match:
            values[match.group("name")] = match.group("range").strip()
        if re.search(r"\[eva(?::[^\]]+)?\].*(warning|alarm|error)", line, re.I):
            flush_warning()
            current_warning = {"line": number, "text": line.strip()}
        elif current_warning is not None and line.strip():
            current_warning["text"] += " " + line.strip()
    flush_warning()
    warnings = unique_sorted(warnings, key=lambda value: (value["line"], value["text"]))
    parameter_ranges = {
        name: value for name, value in values.items() if not name.startswith("\\")
    }
    return_range = "UNKNOWN"
    for candidate in ("__retres", "\\result", "result"):
        if candidate in values:
            return_range = values[candidate]
            break
    checks = {}
    for name, pattern in CHECK_PATTERNS.items():
        matching = [warning for warning in warnings if pattern.search(warning["text"])]
        checks[name] = "WARNING" if matching else "NO_ALARM_OBSERVED_NOT_PROOF"
    return {
        "status": "COMPLETED",
        "warnings": warnings,
        "values": dict(sorted(values.items())),
        "parameter_ranges": dict(sorted(parameter_ranges.items())),
        "return_range": return_range,
        "checks": checks,
        "raw_log": path.name,
    }


def dependency_tokens(value: str) -> list[str]:
    if not value.strip():
        return []
    # Frama-C prints source strings in some dependency expressions. They are
    # not memory dependencies and must not contribute words to the fact.
    value = re.sub(r'"(?:\\.|[^"\\])*"', " ", value)
    tokens = re.findall(
        r"(?:\\result|\\nothing|\\all|\*?[A-Za-z_][A-Za-z0-9_]*"
        r"(?:\[(?:[0-9]+)(?:\.\.[0-9]+)?\])?)",
        value,
    )
    return unique_sorted(token for token in tokens if token not in {"and", "or"})


def parse_from(path: pathlib.Path, function_name: str) -> dict[str, Any]:
    if not path.exists():
        return {
            "status": "UNKNOWN",
            "return_dependencies": [],
            "modified_memory_dependencies": [],
            "warnings": [],
            "raw_log": path.name,
        }
    lines = path.read_text(encoding="utf-8", errors="replace").splitlines()
    return_deps: list[str] = []
    modified_deps: list[str] = []
    warnings = []
    active = False
    block_seen = False
    dependency_line_seen = False
    current_kind = None
    for number, line in enumerate(lines, start=1):
        if line.startswith(f"[from] Function {function_name}:"):
            active = True
            block_seen = True
            continue
        if active and line.startswith("[from] ====== END OF DEPENDENCIES ======"):
            active = False
            continue
        if re.search(r"\[from\].*(warning|error)", line, re.I):
            warnings.append({"line": number, "text": line.strip()})
        if not active:
            continue
        if "FROM" in line:
            dependency_line_seen = True
            left, right = line.split("FROM", 1)
            current_kind = "return" if re.search(r"\\result|return|retres", left, re.I) else "modified"
            deps = dependency_tokens(right)
        else:
            # Continuation lines belong to the preceding dependency clause.
            deps = dependency_tokens(line)
        if current_kind == "return":
            return_deps.extend(deps)
        elif current_kind == "modified":
            modified_deps.extend(deps)
    return {
        "status": "COMPLETED" if block_seen and (return_deps or modified_deps or dependency_line_seen) else "UNKNOWN",
        "return_dependencies": unique_sorted(return_deps),
        "modified_memory_dependencies": unique_sorted(modified_deps),
        "warnings": unique_sorted(warnings, key=lambda value: (value["line"], value["text"])),
        "raw_log": path.name,
    }


def access_name(access: dict[str, Any]) -> str:
    if access.get("record"):
        return f"{access['record']}.{access['name']}"
    return access.get("name", "UNKNOWN")


def all_writes(function: dict[str, Any]) -> list[str]:
    return [
        *[access_name(item) for item in function.get("globals_write", [])],
        *[access_name(item) for item in function.get("fields_write", [])],
        *function.get("static_mutable_state", []),
        *[
            item["name"]
            for item in function.get("pointer_parameters", [])
            if item.get("mode") == "WRITES_THROUGH"
        ],
    ]


def direct_global_is_const(function: dict[str, Any], raw_globals: dict[str, Any]) -> bool:
    reads = function.get("globals_read", [])
    if not reads:
        return True
    by_name = {item.get("name"): item for item in raw_globals.values()}
    return all(by_name.get(item.get("name"), {}).get("const", False) for item in reads)


def classify(function: dict[str, Any], raw_globals: dict[str, Any]) -> dict[str, Any]:
    effects = function.get("effects", {})
    writes = all_writes(function)
    pointer_modes = [item.get("mode", "UNKNOWN") for item in function.get("pointer_parameters", [])]
    direct_calls = function.get("calls", [])
    unknown_call = bool(effects.get("indirect_call"))
    evidence = []
    if writes:
        evidence.append(f"AST observed writes or mutable-state effects: {sorted(set(writes))}")
    else:
        evidence.append("AST observed no global/field/pointee writes")
    if pointer_modes:
        evidence.append(f"AST pointer modes: {sorted(pointer_modes)}")
    if function.get("globals_read"):
        evidence.append(
            "AST observed global reads: "
            + ", ".join(sorted(access_name(item) for item in function["globals_read"]))
        )
    if function.get("fields_read"):
        evidence.append(
            "AST observed field reads: "
            + ", ".join(sorted(access_name(item) for item in function["fields_read"]))
        )
    if function.get("loops"):
        evidence.append(f"AST loop count is {len(function['loops'])}; trip proofs are retained per loop")
    else:
        evidence.append("AST observed no loop")
    if effects.get("file_io") or effects.get("logging") or effects.get("malloc"):
        category = "IO_OR_DEBUG"
    elif effects.get("assert"):
        category = "TEST_OR_CHECKER"
    elif unknown_call:
        category = "UNRESOLVED"
    elif writes:
        category = "STATEFUL"
    elif any(item.get("record") == "dsc_cfg_t" for item in function.get("fields_read", [])):
        category = "CONFIG_HELPER"
    elif not direct_calls and direct_global_is_const(function, raw_globals):
        category = "PURE_COMB_CANDIDATE"
    elif not direct_calls or all(item.get("category") == "other" for item in direct_calls):
        category = "COMPOSITE_COMB_CANDIDATE"
    else:
        category = "UNRESOLVED"
    if category == "PURE_COMB_CANDIDATE":
        evidence.append("No direct calls and no non-const global read were observed")
    if category == "CONFIG_HELPER":
        evidence.append("The proposal is per-field input use; the containing struct is not classified as static configuration")
    if category == "UNRESOLVED":
        evidence.append("At least one dependency or side effect could not be proven by the selected analyses")
    pure = category == "PURE_COMB_CANDIDATE"
    combinational = category in {
        "PURE_COMB_CANDIDATE",
        "COMPOSITE_COMB_CANDIDATE",
        "CONFIG_HELPER",
    }
    return {
        "category_proposal": category,
        "purity_candidate": pure,
        "combinational_candidate": combinational,
        "classification_evidence": evidence,
        "pointer_modes": pointer_modes,
    }


def normalize_function(
    function: dict[str, Any],
    eva: dict[str, Any],
    from_facts: dict[str, Any],
    raw_globals: dict[str, Any],
) -> dict[str, Any]:
    result = dict(function)
    result["analysis"] = {
        "eva": eva,
        "from": from_facts,
        "warnings": unique_sorted(
            [*eva.get("warnings", []), *from_facts.get("warnings", [])],
            key=lambda value: (value.get("line", 0), value.get("text", "")),
        ),
    }
    result["proposal"] = classify(result, raw_globals)
    unknown = set(result.get("unknown_facts", []))
    if eva.get("status") != "COMPLETED":
        unknown.add("Eva result unavailable")
    if from_facts.get("status") != "COMPLETED":
        unknown.add("From result unavailable")
    if any(not loop.get("has_fixed_trip_count") for loop in result.get("loops", [])):
        unknown.add("at least one loop trip count is not proven fixed")
    if any(loop.get("iteration_dependency", "").startswith("POTENTIAL") for loop in result.get("loops", [])):
        unknown.add("loop has a potential read/write dependency across iterations")
    result["unknown_facts"] = sorted(unknown)
    return result


def build_field_facts(
    functions: list[dict[str, Any]], production_usrs: set[str]
) -> list[dict[str, Any]]:
    fields: dict[tuple[str, str], dict[str, Any]] = {}
    for function in functions:
        for direction in ("read", "write"):
            for access in function.get(f"fields_{direction}", []):
                key = (access.get("record", "UNKNOWN"), access.get("name", "UNKNOWN"))
                item = fields.setdefault(
                    key,
                    {
                        "record": key[0],
                        "field": key[1],
                        "type": access.get("type", "UNKNOWN"),
                        "read_by": [],
                        "written_by": [],
                        "evidence": [],
                    },
                )
                consumer = {
                    "function": function["name"],
                    "clang_usr": function["clang_usr"],
                    "location": access.get("location", {}),
                    "context": access.get("context", "UNKNOWN"),
                }
                destination = item["read_by"] if direction == "read" else item["written_by"]
                destination.append(consumer)
    result = []
    for key in sorted(fields):
        item = fields[key]
        item["read_by"] = unique_sorted(item["read_by"], key=lambda value: (value["function"], location_key(value["location"])))
        item["written_by"] = unique_sorted(item["written_by"], key=lambda value: (value["function"], location_key(value["location"])))
        if item["record"] == "dsc_cfg_t":
            if item["written_by"]:
                role = "MUTATED_CONFIGURATION_FIELD"
            else:
                role = "FUNCTION_INPUT_CONFIGURATION_FIELD"
            item["role_proposal"] = role
            item["evidence"].append("Role is derived from this field's individual read/write sites")
        elif item["record"] == "dsc_state_t":
            target_access = any(
                consumer["clang_usr"] in production_usrs
                for consumer in [*item["read_by"], *item["written_by"]]
            )
            if target_access:
                item["role_proposal"] = "RUNTIME_STATE_INPUT_CANDIDATE"
                item["evidence"].append(
                    "Field is accessed by a production-reachable function; this is a dataflow role proposal, not a sequential-hardware claim"
                )
            else:
                item["role_proposal"] = "MODEL_ONLY_OR_RUNTIME_UNKNOWN"
                item["evidence"].append(
                    "Field is outside the production-reachable access path; AST alone does not prove model-only versus runtime state"
                )
        else:
            item["role_proposal"] = "UNKNOWN"
            item["evidence"].append("No role taxonomy proof was available")
        result.append(item)
    return result


def component_loop_evidence(functions: list[dict[str, Any]]) -> list[dict[str, Any]]:
    result = []
    for function in functions:
        for loop in function.get("loops", []):
            condition = loop.get("condition", "")
            cases = loop.get("trip_count_cases", [])
            counts = [case.get("count") for case in cases]
            if not (
                any(count in {3, 4} for count in counts)
                or "numComponents" in condition
                or "native_422" in condition
            ):
                continue
            result.append(
                {
                    "function": function["name"],
                    "source_file": loop.get("location", {}).get("file", "UNKNOWN"),
                    "line": loop.get("location", {}).get("line", 0),
                    "condition": condition,
                    "fixed_trip_count": loop.get("fixed_trip_count"),
                    "trip_count_cases": cases,
                    "iteration_dependency": loop.get("iteration_dependency", "UNKNOWN"),
                    "dependency_locations": loop.get("dependency_locations", []),
                    "evidence": "Clang AST loop bounds; conditional 3/4 cases remain conditional",
                }
            )
    return sorted(result, key=lambda value: (value["function"], value["line"], value["condition"]))


def table_ranges(raw_globals: dict[str, Any]) -> list[dict[str, Any]]:
    result = []
    for item in raw_globals.values():
        values = item.get("constant_values", [])
        if not item.get("is_array", item.get("array_size") is not None) or not values:
            continue
        result.append(
            {
                "table": item["name"],
                "source_file": item.get("source_file", "UNKNOWN"),
                "line": item.get("line", 0),
                "array_size": item.get("array_size"),
                "value_range": [min(values), max(values)] if values else "UNKNOWN",
                "evidence": "Clang evaluated the constant initializer list for an array global",
            }
        )
    return sorted(result, key=lambda value: value["table"])


def range_facts(
    functions: list[dict[str, Any]],
    raw_globals: dict[str, Any],
) -> list[dict[str, Any]]:
    tables = table_ranges(raw_globals)
    table_names = {item["table"] for item in tables}
    result = []
    for function in functions:
        eva = function.get("analysis", {}).get("eva", {})
        parameters = []
        for param in function.get("parameters", []):
            name = param.get("name", "UNKNOWN")
            parameters.append(
                {
                    "name": name,
                    "eva_range": eva.get("parameter_ranges", {}).get(name, "UNKNOWN"),
                    "status": "EVA_RANGE" if name in eva.get("parameter_ranges", {}) else "UNKNOWN",
                }
            )
        used_tables = sorted(
            {
                access.get("name", "")
                for access in function.get("globals_read", [])
                if access.get("name", "") in table_names
            }
        )
        item = {
            "function": function["name"],
            "clang_usr": function["clang_usr"],
            "parameters": parameters,
            "return": eva.get("return_range", "UNKNOWN"),
            "eva_values": eva.get("values", {}),
            "eva_checks": eva.get("checks", {name: "UNKNOWN" for name in CHECK_PATTERNS}),
            "table_ranges": [table for table in tables if table["table"] in used_tables],
            "proposals": [],
        }
        if used_tables:
            item["table_use"] = {
                "tables": used_tables,
                "status": "CLANG_GLOBAL_READ",
                "evidence": "The function reads a constant-initializer array global",
            }
        result.append(item)
    return result


def dependency_facts(functions: list[dict[str, Any]]) -> list[dict[str, Any]]:
    result = []
    for function in functions:
        from_facts = function.get("analysis", {}).get("from", {})
        ast_deps = function.get("return_dependencies", [])
        result.append(
            {
                "function": function["name"],
                "clang_usr": function["clang_usr"],
                "ast_return_dependencies": ast_deps,
                "from_return_dependencies": from_facts.get("return_dependencies", []),
                "from_modified_memory_dependencies": from_facts.get(
                    "modified_memory_dependencies", []
                ),
                "status": from_facts.get("status", "UNKNOWN"),
                "unknown": (
                    []
                    if from_facts.get("status") == "COMPLETED"
                    else ["From did not emit a parseable dependency result"]
                ),
            }
        )
    return result


def usage_paths(functions: list[dict[str, Any]], target: str) -> list[list[str]]:
    by_name = {item["name"]: item for item in functions}
    reverse: dict[str, list[str]] = defaultdict(list)
    for item in functions:
        for caller in item.get("callers", []):
            reverse[item["name"]].append(caller["name"])
    paths = []
    queue = [([target], target)]
    while queue:
        path, node = queue.pop(0)
        parents = sorted(set(reverse.get(node, [])))
        if not parents:
            paths.append(list(reversed(path)))
            continue
        for parent in parents:
            if parent in path or len(path) >= 5:
                paths.append(list(reversed(path + [parent])))
            else:
                queue.append((path + [parent], parent))
    if not paths:
        return [[target]]
    return unique_sorted(paths)


def markdown_function_summary(functions: list[dict[str, Any]]) -> str:
    lines = [
        "# Function summary",
        "",
        "Facts are from Clang LibTooling/AST Matchers and Frama-C runs selected by the auto-ranked candidate receipt.",
        "A proposal is not a hardware equivalence claim.",
        "",
    ]
    for function in sorted(functions, key=lambda value: (value["name"], value["source_file"], value["line"])):
        proposal = function["proposal"]
        pointer_modes = ", ".join(
            f"{param['name']}={param['mode']}"
            for param in function.get("pointer_parameters", [])
        ) or "NONE"
        parameter_text = ", ".join(
            f"`{param['name']}: {param['type']}`"
            for param in function.get("parameters", [])
        ) or "NONE"
        fixed_counts = [
            str(loop.get("fixed_trip_count"))
            for loop in function.get("loops", [])
            if loop.get("has_fixed_trip_count")
        ]
        lines.extend(
            [
                f"## `{function['name']}`",
                "",
                f"- Source: `{function['source_file']}:{function['line']}`",
                f"- Clang USR: `{function['clang_usr']}`",
                f"- Return: `{function['return_type']}`; parameters: {parameter_text}",
                f"- Callers: {', '.join(item['name'] for item in function.get('callers', [])) or 'NONE'}",
                f"- Callees: {', '.join(item['name'] for item in function.get('callees', [])) or 'NONE'}",
                f"- Global read/write: {len(function.get('globals_read', []))}/{len(function.get('globals_write', []))}; "
                f"field read/write: {len(function.get('fields_read', []))}/{len(function.get('fields_write', []))}",
                f"- Pointer modes: {pointer_modes}",
                f"- Loops: {len(function.get('loops', []))}; fixed counts: "
                + (", ".join(fixed_counts) if fixed_counts else "UNKNOWN"),
                f"- Effects: `{json.dumps(function.get('effects', {}), sort_keys=True)}`",
                f"- Proposal: **{proposal['category_proposal']}**; purity={proposal['purity_candidate']}; combinational={proposal['combinational_candidate']}",
                "- Classification evidence:",
            ]
        )
        lines.extend(f"  - {evidence}" for evidence in proposal["classification_evidence"])
        lines.append("")
    lines.extend(
        [
            "## Component-loop evidence",
            "",
            "Conditional component bounds are retained as AST facts; no fixed 3/4 simplification is made without proof.",
            "",
        ]
    )
    for function in functions:
        for loop in function.get("loops", []):
            condition = loop.get("condition", "")
            if "native_422" in condition or "numComponents" in condition:
                lines.append(
                    f"- `{function['name']}` line {loop.get('location', {}).get('line', 0)}: `{condition}`; "
                    f"cases={loop.get('trip_count_cases', [])}; dependency={loop.get('iteration_dependency', 'UNKNOWN')}"
                )
    return "\n".join(lines).rstrip() + "\n"


def markdown_field_summary(fields: list[dict[str, Any]], functions: list[dict[str, Any]]) -> str:
    lines = [
        "# Field summary",
        "",
        "Roles are per-field proposals. No complete `dsc_cfg_t` or `dsc_state_t` is treated as static configuration.",
        "",
    ]
    for field in fields:
        lines.extend(
            [
                f"## `{field['record']}.{field['field']}`",
                "",
                f"- Type: `{field['type']}`",
                f"- Role proposal: **{field['role_proposal']}**",
                f"- Read by: {', '.join(item['function'] for item in field['read_by']) or 'NONE'}",
                f"- Written by: {', '.join(item['function'] for item in field['written_by']) or 'NONE'}",
                "- Evidence:",
            ]
        )
        lines.extend(f"  - {evidence}" for evidence in field["evidence"])
        lines.append("")
    lines.extend(
        [
            "## dsc_state_t role split",
            "",
            "- Constant-initializer array globals and their pointer uses are recorded in `value-ranges.json` and field facts.",
            "- Production-reachable state fields: runtime-state input candidate based on observed access sites; fields outside that path remain model-only-or-runtime UNKNOWN.",
            "- This report does not infer sequential hardware from state access.",
            "",
            "## Quant table initialization and use",
            "",
            "- Constant-initializer table declarations, observed readers, and value ranges are emitted without a function-name allowlist.",
            "",
        ]
    )
    return "\n".join(lines)


def markdown_candidates(functions: list[dict[str, Any]]) -> str:
    candidates = [
        function
        for function in functions
        if function.get("proposal", {}).get("combinational_candidate")
    ]
    lines = [
        "# Candidate functions",
        "",
        "These are proposal labels supported by recorded AST/Frama evidence; they are not RTL generation decisions.",
        "",
    ]
    for function in sorted(candidates, key=lambda value: value["name"]):
        proposal = function["proposal"]
        lines.extend(
            [
                f"## `{function['name']}` — {proposal['category_proposal']}",
                "",
                f"- Pure candidate: `{proposal['purity_candidate']}`",
                f"- Combinational candidate: `{proposal['combinational_candidate']}`",
                f"- Evidence: {'; '.join(proposal['classification_evidence'])}",
                "",
            ]
        )
    if len(candidates) < 5:
        lines.extend(
            [
                "## Gate",
                "",
                f"Only {len(candidates)} candidate(s) were proven by the available facts; the five-candidate success gate is UNKNOWN.",
                "",
            ]
        )
    return "\n".join(lines)


def markdown_unresolved(functions: list[dict[str, Any]], metadata: dict[str, Any]) -> str:
    lines = [
        "# Unresolved facts and limitations",
        "",
        "Unknown means the selected tools did not prove the property; it is not a negative fact.",
        "",
    ]
    for function in sorted(functions, key=lambda value: value["name"]):
        unknown = function.get("unknown_facts", [])
        if unknown:
            lines.append(f"- `{function['name']}`: " + "; ".join(unknown))
    lines.extend(
        [
            "",
            "- Eva checks report `NO_ALARM_OBSERVED_NOT_PROOF` when no matching alarm was emitted.",
            "- Direct entry-point ranges for pointer/struct parameters may remain UNKNOWN without an ACSL contract.",
            "- Modulo behavior is retained; no simplification is proposed without a caller-specific range proof.",
            "- From text is retained as raw log names and only normalized when a dependency line is emitted.",
            "- This experiment does not analyze sequential hardware or call an LLM.",
        ]
    )
    return "\n".join(lines) + "\n"


def main() -> int:
    args = parse_args()
    try:
        raw = json.loads(args.raw.resolve().read_text(encoding="utf-8"))
        compile_check = json.loads(args.compile_check.resolve().read_text(encoding="utf-8"))
        input_manifest = json.loads(args.input_manifest.resolve().read_text(encoding="utf-8"))
        build_receipt = json.loads(args.build_receipt.resolve().read_text(encoding="utf-8"))
        candidate_payload = json.loads(args.candidates.resolve().read_text(encoding="utf-8"))
        traceability_payload = json.loads(args.traceability.resolve().read_text(encoding="utf-8"))
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        print(f"could not load analysis inputs: {exc}", file=sys.stderr)
        return 2
    if compile_check.get("status") != "PASS":
        print("C compiler front-end receipt is not PASS", file=sys.stderr)
        return 2
    if build_receipt.get("status") != "PASS":
        print("C model build receipt is not PASS", file=sys.stderr)
        return 2

    source_dir = args.source_dir.resolve()
    output_dir = args.output_dir.resolve()
    facts_dir = output_dir / "facts"
    reports_dir = output_dir / "reports"
    facts_dir.mkdir(parents=True, exist_ok=True)
    reports_dir.mkdir(parents=True, exist_ok=True)

    raw_globals = raw.get("global_declarations", [])
    globals_by_usr = {item.get("clang_usr", "UNKNOWN"): item for item in raw_globals}
    source_functions = unique_sorted(
        [
            function
            for function in raw.get("functions", [])
            if function.get("source_file")
            and not function.get("source_file", "").startswith("<external>/")
        ],
        key=lambda item: (
            item.get("clang_usr", ""),
            item.get("source_file", ""),
            item.get("line", 0),
        ),
    )
    frama_manifest_path = args.frama_output_dir / "manifest.json"
    frama_manifest = (
        json.loads(frama_manifest_path.read_text(encoding="utf-8"))
        if frama_manifest_path.is_file()
        else {}
    )
    analysis_targets = list(frama_manifest.get("targets", []))
    eva_by_function = {
        target: parse_eva(args.frama_output_dir / f"{target}.eva.log", target)
        for target in analysis_targets
    }
    from_by_function = {
        target: parse_from(args.frama_output_dir / f"{target}.from.log", target)
        for target in analysis_targets
    }
    normalized = []
    for function in source_functions:
        name = function.get("name")
        normalized.append(
            normalize_function(
                function,
                eva_by_function.get(name, {"status": "UNKNOWN", "values": {}}),
                from_by_function.get(name, {"status": "UNKNOWN"}),
                globals_by_usr,
            )
        )
    normalized.sort(key=lambda item: (item["name"], item["source_file"], item["line"], item["clang_usr"]))

    candidate_records = candidate_payload.get("functions", [])
    production_usrs = {
        item.get("clang_usr")
        for item in candidate_records
        if item.get("production_reachable")
    }
    fields = build_field_facts(normalized, production_usrs)
    ranges = range_facts(normalized, globals_by_usr)
    dependencies = dependency_facts(normalized)
    edges = unique_sorted(
        raw.get("edges", []),
        key=lambda item: (
            item.get("caller_usr", ""),
            item.get("callee_usr", ""),
            location_key(item.get("location", {})),
        ),
    )
    call_nodes = [
        {
            "clang_usr": function["clang_usr"],
            "name": function["name"],
            "source_file": function["source_file"],
            "line": function["line"],
            "end_line": function.get("end_line", function["line"]),
        }
        for function in normalized
    ]
    discovered_inventory = [
        {
            "clang_usr": function.get("clang_usr", "UNKNOWN"),
            "name": function.get("name", "UNKNOWN"),
            "qualified_name": function.get("qualified_name", function.get("name", "UNKNOWN")),
            "source_file": function.get("source_file", "UNKNOWN"),
            "line": function.get("line", 0),
            "column": function.get("column", 0),
            "end_line": function.get("end_line", function.get("line", 0)),
            "end_column": function.get("end_column", function.get("column", 0)),
        }
        for function in source_functions
    ]
    discovered_inventory.sort(
        key=lambda item: (
            item["name"],
            item["source_file"],
            item["line"],
            item["column"],
            item["clang_usr"],
        )
    )
    trace_counts = traceability_payload.get("counts", {})
    source_manifest = input_manifest.get("source", {})
    metadata = {
        "schema_version": 2,
        "status": "OK",
        "do_not_edit": True,
        "dsc_source_revision": args.source_revision,
        "source_git": source_manifest.get("git", {}),
        "source_file_hashes": source_hashes(source_dir),
        "source_hashes_sha256": source_manifest.get("source_hashes_sha256", "UNKNOWN"),
        "spec_pdf_sha256": input_manifest.get("spec", {}).get("sha256", "UNKNOWN"),
        "input_manifest_sha256": file_sha256(args.input_manifest.resolve()),
        "build_receipt_sha256": file_sha256(args.build_receipt.resolve()),
        "compile_commands_sha256": file_sha256(args.compile_commands.resolve()),
        "compile_check_sha256": file_sha256(args.compile_check.resolve()),
        "compile_check_status": compile_check.get("status", "UNKNOWN"),
        "compiler_command_count": compile_check.get("compiler_command_count", 0),
        "candidate_receipt_sha256": file_sha256(args.candidates.resolve()),
        "traceability_sha256": file_sha256(args.traceability.resolve()),
        "build_status": build_receipt.get("status", "UNKNOWN"),
        "binary_sha256": build_receipt.get("binary", {}).get("sha256", "UNKNOWN"),
        "frama_targets": analysis_targets,
        "frama_excluded_sources": frama_manifest.get("excluded_sources", []),
        "discovered_function_count": len(discovered_inventory),
        "function_discovery": {
            "source": "Clang AST functionDecl(isDefinition())",
            "count": len(discovered_inventory),
        },
        "candidate_selection": candidate_payload.get("selection", {}),
        "traceability_counts": trace_counts,
        "clang_version": args.clang_version,
        "frama_c_version": args.frama_c_version,
        "analysis_command": sorted(args.analysis_command),
        "generated_timestamp": dt.datetime.now(dt.timezone.utc).isoformat(),
    }

    comparison = {}
    comparison_names = unique_sorted(candidate_payload.get("selected_for_frama", [])[:2])
    for name in comparison_names:
        function = next((item for item in normalized if item["name"] == name), None)
        if function:
            comparison[name] = {
                "callers": function.get("callers", []),
                "callees": function.get("callees", []),
                "usage_paths": usage_paths(normalized, name),
                "fields_read": function.get("fields_read", []),
                "globals_read": function.get("globals_read", []),
                "return_dependencies": function.get("return_dependencies", []),
            }
    artifact_payload = {
        "functions": normalized,
        "discovered_functions": discovered_inventory,
        "compile_check": compile_check,
        "build_receipt": build_receipt,
        "candidates": candidate_payload,
        "traceability": traceability_payload,
        "callgraph": {"nodes": call_nodes, "edges": edges},
        "field_access": {"fields": fields},
        "loops": {
            "functions": [
                {
                    "function": item["name"],
                    "clang_usr": item["clang_usr"],
                    "loop_count": item.get("loop_count", len(item.get("loops", []))),
                    "loops": item.get("loops", []),
                }
                for item in normalized
            ]
        },
        "value_ranges": {"functions": ranges},
        "dependencies": {"functions": dependencies},
        "reports": {
            "candidate_count": candidate_payload.get("counts", {}).get("eligible_candidates", 0),
            "production_reachable_count": candidate_payload.get("counts", {}).get("production_reachable", 0),
            "output_contributing_count": candidate_payload.get("counts", {}).get("output_contributing", 0),
            "comparison": comparison,
            "table_ranges": table_ranges(globals_by_usr),
            "component_loop_evidence": component_loop_evidence(normalized),
        },
    }
    semantic_input = {
        "metadata": {key: value for key, value in metadata.items() if key != "generated_timestamp"},
        "artifacts": artifact_payload,
    }
    metadata["semantic_hash"] = hashlib.sha256(canonical_json(semantic_input)).hexdigest()

    def with_metadata(payload: Any) -> dict[str, Any]:
        return {"metadata": metadata, **payload}

    write_json(facts_dir / "functions.json", with_metadata({"functions": normalized}))
    write_json(facts_dir / "discovered-functions.json", with_metadata({"functions": discovered_inventory}))
    write_json(facts_dir / "compile-check.json", with_metadata(compile_check))
    write_json(facts_dir / "build-receipt.json", with_metadata(build_receipt))
    write_json(facts_dir / "candidates.json", with_metadata(candidate_payload))
    write_json(facts_dir / "callgraph.json", with_metadata({"nodes": call_nodes, "edges": edges}))
    write_json(facts_dir / "field-access.json", with_metadata({"fields": fields}))
    write_json(facts_dir / "loops.json", with_metadata(artifact_payload["loops"]))
    write_json(facts_dir / "value-ranges.json", with_metadata(artifact_payload["value_ranges"]))
    write_json(facts_dir / "dependencies.json", with_metadata(artifact_payload["dependencies"]))

    reports_dir.joinpath("function-summary.md").write_text(markdown_function_summary(normalized), encoding="utf-8")
    reports_dir.joinpath("field-summary.md").write_text(markdown_field_summary(fields, normalized), encoding="utf-8")
    reports_dir.joinpath("candidate-functions.md").write_text(markdown_candidates(normalized), encoding="utf-8")
    reports_dir.joinpath("unresolved.md").write_text(markdown_unresolved(normalized, metadata), encoding="utf-8")

    summary = with_metadata(
        {
            "facts": {
                "function_count": len(normalized),
                "callgraph_node_count": len(call_nodes),
                "callgraph_edge_count": len(edges),
                "field_count": len(fields),
                "loop_count": sum(len(item.get("loops", [])) for item in normalized),
                "candidate_count": artifact_payload["reports"]["candidate_count"],
                "production_reachable_count": artifact_payload["reports"]["production_reachable_count"],
                "output_contributing_count": artifact_payload["reports"]["output_contributing_count"],
                "frama_targets": analysis_targets,
                "discovered_function_count": len(discovered_inventory),
                "compile_check_status": compile_check.get("status", "UNKNOWN"),
                "compiler_command_count": compile_check.get("compiler_command_count", 0),
            },
            "comparisons": comparison,
            "candidate_summary": candidate_payload.get("counts", {}),
            "traceability_summary": trace_counts,
            "quantization_tables": table_ranges(globals_by_usr),
            "component_loop_evidence": component_loop_evidence(normalized),
            "limitations": [
                "Eva no-alarm observations are not substituted for proof.",
                "Direct parameter ranges can remain UNKNOWN without contracts.",
                "Candidate links and non-exact spec links remain visibly proposed or orphaned until review.",
                "No LLM calls or RTL generation are used by this pipeline.",
            ],
        }
    )
    write_json(output_dir / "summary.json", summary)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
