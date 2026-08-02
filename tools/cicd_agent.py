#!/usr/bin/env python3
"""Executable, data-driven C-to-RTL migration CI/CD agent.

No function name is configuration. Ready cache misses invoke the external
DSC_CICD_GENERATOR_CMD exactly once; missing hooks return GENERATION_REQUIRED.
All verification receipts are produced by commands executed in this run.
"""

from __future__ import annotations

import argparse
import copy
import concurrent.futures
import hashlib
import itertools
import json
import os
import pathlib
import re
import shlex
import shutil
import subprocess
import sys
import tempfile
import textwrap
import threading
import time
from typing import Any, Iterable


STATE_ORDER = (
    "DISCOVERED",
    "CONTRACT_LOCKED",
    "RTL_GENERATED",
    "UNIT_VERIFIED",
    "DEPENDENCIES_VERIFIED",
    "SHADOW_PASS",
    "RTL_RETURN_PASS",
    "BITSTREAM_PASS",
    "PROMOTED",
)
VERIFICATION_STATUSES = {
    "EXHAUSTIVE_EQUIVALENT",
    "DIFFERENTIAL_PASS",
    "COUNTEREXAMPLE",
    "UNPROVED",
    "UNSUPPORTED",
    "INFRASTRUCTURE_FAILURE",
    "GENERATION_REQUIRED",
    "GENERATION_FAILED",
}
STAGE_TO_STATE = {
    "discover": "DISCOVERED",
    "contract": "CONTRACT_LOCKED",
    "rtl": "RTL_GENERATED",
    "unit": "UNIT_VERIFIED",
    "dependencies": "DEPENDENCIES_VERIFIED",
    "shadow": "SHADOW_PASS",
    "rtl_return": "RTL_RETURN_PASS",
    "bitstream": "BITSTREAM_PASS",
    "promote": "PROMOTED",
}
FORBIDDEN_RTL = (
    r"\balways_ff\b",
    r"\balways_latch\b",
    r"\bposedge\b",
    r"\bnegedge\b",
    r"\bclock\b",
    r"\breset\b",
    r"\binitial\b",
    r"#[ \t]*[0-9]",
    r"\bwait\s*\(",
    r"\bfork\b",
    r"\bjoin\b",
    r"\bmemory\b",
    r"\b(?:logic|reg|bit|wire)\b[^;\n]*\]\s*[A-Za-z_][A-Za-z0-9_]*\s*\[",
)


def canonical(value: Any) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def digest(value: Any) -> str:
    return hashlib.sha256(canonical(value).encode("utf-8")).hexdigest()


def file_hash(path: pathlib.Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


def read_json(path: pathlib.Path, default: Any = None) -> Any:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return default


def write_json(path: pathlib.Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2, sort_keys=True, ensure_ascii=False) + "\n", encoding="utf-8")


def safe_identifier(value: str) -> str:
    result = re.sub(r"[^A-Za-z0-9_]", "_", str(value))
    if not result or result[0].isdigit():
        result = "c_" + result
    return result


def command_version(command: str | None) -> str:
    if not command:
        return "MISSING"
    try:
        result = subprocess.run([command, "--version"], stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                                text=True, encoding="utf-8", errors="replace", timeout=15, check=False)
        return (result.stdout or "").splitlines()[0].strip() or "UNKNOWN"
    except (OSError, subprocess.TimeoutExpired):
        return "UNAVAILABLE"


def locate_tool(name: str, *fallbacks: str) -> str | None:
    found = shutil.which(name)
    if found:
        return found
    for fallback in fallbacks:
        if fallback and pathlib.Path(fallback).is_file():
            return fallback
    return None


def contract_function(contract: dict[str, Any]) -> dict[str, Any]:
    value = contract.get("function", {})
    return value if isinstance(value, dict) else {}


def contract_id(contract: dict[str, Any]) -> str:
    if contract.get("contract_id"):
        return str(contract["contract_id"])
    return safe_identifier(contract_function(contract).get("name", "unknown")).lower()


def contract_exact_links(contract: dict[str, Any]) -> list[dict[str, Any]]:
    return [link for link in contract.get("spec_links", []) if link.get("status") == "EXACT"]


def scrub_paths(value: Any, roots: Iterable[pathlib.Path]) -> Any:
    if isinstance(value, str):
        result = value
        for root in roots:
            result = result.replace(str(root), "<overlay-work>")
        return result
    if isinstance(value, list):
        return [scrub_paths(item, roots) for item in value]
    if isinstance(value, dict):
        return {key: scrub_paths(item, roots) for key, item in value.items()}
    return value


def parameter_is_pointer(parameter: dict[str, Any]) -> bool:
    return bool(parameter.get("pointer")) or "*" in str(parameter.get("type", ""))


def source_path_for(function: dict[str, Any], source_dir: pathlib.Path) -> pathlib.Path:
    raw = pathlib.Path(str(function.get("source_file", "")))
    if raw.is_absolute() and raw.is_file():
        return raw
    return source_dir / raw.name


def extract_function_body(path: pathlib.Path, name: str, line_hint: int | None = None) -> tuple[str, dict[str, int]]:
    text = path.read_text(encoding="utf-8", errors="replace")
    pattern = re.compile(r"\b" + re.escape(name) + r"\s*\([^;{}]*\)\s*\{")
    matches = list(pattern.finditer(text))
    if not matches:
        raise RuntimeError(f"function definition not found: {name}")
    hint = max(0, int(line_hint or 1) - 1)
    match = next((candidate for candidate in matches if text.count("\n", 0, candidate.start()) >= hint), matches[0])
    brace = text.find("{", match.start(), match.end())
    depth = 0
    quote: str | None = None
    escaped = False
    end: int | None = None
    for index in range(brace, len(text)):
        char = text[index]
        if quote:
            if escaped:
                escaped = False
            elif char == "\\":
                escaped = True
            elif char == quote:
                quote = None
            continue
        if char in "\"'":
            quote = char
        elif char == "{":
            depth += 1
        elif char == "}":
            depth -= 1
            if depth == 0:
                end = index + 1
                break
    if end is None:
        raise RuntimeError(f"unbalanced function body: {name}")
    return text[match.start():end].strip(), {
        "start_line": text.count("\n", 0, match.start()) + 1,
        "end_line": text.count("\n", 0, end) + 1,
    }


def source_body(contract: dict[str, Any], source_dir: pathlib.Path) -> tuple[pathlib.Path, str, dict[str, int]]:
    function = contract_function(contract)
    path = source_path_for(function, source_dir)
    span = function.get("source_span", {}) or {}
    if span.get("start_line") and span.get("end_line"):
        lines = path.read_text(encoding="utf-8", errors="replace").splitlines()
        start = max(1, int(span["start_line"]))
        end = min(len(lines), int(span["end_line"]))
        return path, "\n".join(lines[start - 1:end]).strip(), {"start_line": start, "end_line": end}
    body, derived = extract_function_body(path, str(function.get("name", "")), function.get("line"))
    return path, body, derived


def unresolved_reasons(contract: dict[str, Any]) -> list[str]:
    reasons: list[str] = [str(item) for item in contract.get("obligations", []) if item]
    reasons.extend(str(item) for item in contract.get("dependencies", {}).get("unresolved", []) if item)
    interface = contract.get("interface", {}) or {}
    for item in interface.get("inputs", []) + interface.get("flattened_pointer_dependencies", []):
        if item.get("unresolved"):
            reasons.append(f"interface:{item.get('name') or item.get('field') or 'input'}")
    if interface.get("output", {}).get("unresolved"):
        reasons.append("interface:return_value")
    if not contract.get("semantics"):
        reasons.append("arithmetic_semantics")
    if not interface.get("ports") and not (interface.get("inputs") or interface.get("flattened_pointer_dependencies") or interface.get("output")):
        reasons.append("frozen_interface_missing")
    return sorted(set(reasons))


class Agent:
    def __init__(self, root: pathlib.Path, mode: str) -> None:
        self.root = root.resolve()
        self.mode = mode
        self.ci = self.root / "ci"
        self.artifacts = self.root / "artifacts"
        self.integration = self.root / "integration"
        self.manifest = read_json(self.root / "spec" / "manifest.json", {}) or {}
        self.locked_contracts = [read_json(path, {}) for path in sorted((self.root / "contracts" / "locked").glob("*.json"))]
        self.locked_contracts = [item for item in self.locked_contracts if item]
        self.contracts = list(self.locked_contracts)
        self.previous_state = read_json(self.ci / "state.json", {}) or {}
        self.cache = read_json(self.ci / "cache-index.json", {}) or {}
        self.input_facts: dict[str, Any] = {}
        self.dependency_info: dict[str, Any] = {}
        self.plan: dict[str, Any] = {}
        self.dag: dict[str, Any] = {}
        self.state: dict[str, Any] = {}
        self.run_results: list[dict[str, Any]] = []
        self.generator_invocations = 0
        self.generator_tokens = 0

    def load_inputs(self) -> dict[str, Any]:
        errors: list[str] = []
        spec = self.manifest.get("spec", {}) or {}
        source = self.manifest.get("source", {}) or {}
        pdf_path = pathlib.Path(str(spec.get("path", "")))
        if self.manifest.get("status") != "OK" or spec.get("status") != "PASS":
            errors.append("SPEC_UNAVAILABLE")
        if not pdf_path.is_file():
            errors.append("SPEC_UNAVAILABLE: local PDF missing")
        elif spec.get("sha256") and file_hash(pdf_path) != spec.get("sha256"):
            errors.append("SPEC_UNAVAILABLE: PDF SHA-256 changed")
        source_dir = pathlib.Path(str(source.get("source_dir", "")))
        model_root = pathlib.Path(str(source.get("model_root", "")))
        if source.get("status") != "PASS" or not source_dir.is_dir():
            errors.append("SOURCE_UNAVAILABLE")
        actual_hashes: list[dict[str, str]] = []
        for entry in source.get("source_file_hashes", []):
            path = source_dir / str(entry.get("path", ""))
            if not path.is_file():
                errors.append(f"SOURCE_UNAVAILABLE: missing {entry.get('path')}")
                continue
            actual = file_hash(path)
            actual_hashes.append({"path": str(entry.get("path")), "sha256": actual})
            if entry.get("sha256") and actual != entry.get("sha256"):
                errors.append(f"SOURCE_UNAVAILABLE: changed {entry.get('path')}")
        build = read_json(self.root / "build" / "build-receipt.json", {}) or {}
        expected = build.get("smoke", {}).get("expected_hash")
        smoke = next((item for item in build.get("smoke", {}).get("outputs", []) if str(item.get("path", "")).endswith(".dsc")), {})
        if build.get("status") != "PASS" or smoke.get("sha256") != expected:
            errors.append("INFRASTRUCTURE_FAILURE: C baseline receipt is not PASS")
        tools = {
            "python": shutil.which("python3") or sys.executable,
            "make": locate_tool("make"),
            "clang": locate_tool("clang"),
            "clang++": locate_tool("clang++", "/opt/homebrew/opt/llvm/bin/clang++"),
            "verilator": locate_tool("verilator"),
            "pdfinfo": locate_tool("pdfinfo", str(self.manifest.get("pdf_extraction", {}).get("pdfinfo_tool", ""))),
            "pdftotext": locate_tool("pdftotext", str(self.manifest.get("pdf_extraction", {}).get("pdftotext_tool", ""))),
            "llvm-config": locate_tool("llvm-config", "/opt/homebrew/opt/llvm/bin/llvm-config"),
            "llvm-cov": locate_tool("llvm-cov", "/opt/homebrew/opt/llvm/bin/llvm-cov"),
            "llvm-profdata": locate_tool("llvm-profdata", "/opt/homebrew/opt/llvm/bin/llvm-profdata"),
        }
        for name in ("python", "make", "clang", "clang++", "verilator", "llvm-config"):
            if not tools.get(name):
                errors.append(f"INFRASTRUCTURE_FAILURE: missing tool {name}")
        smoke_dir = model_root / "bittrue_smoke"
        scripts = [str(path.relative_to(model_root)) for path in sorted(smoke_dir.glob("run_c_baseline*.sh")) if path.is_file()] if smoke_dir.is_dir() else []
        self.input_facts = {
            "source_root": str(model_root),
            "source_dir": str(source_dir),
            "source_hash": source.get("source_hashes_sha256") or digest(actual_hashes),
            "source_file_hashes": actual_hashes,
            "spec_path": str(pdf_path),
            "spec_hash": spec.get("sha256"),
            "spec_pages": spec.get("pdfinfo", {}).get("Pages"),
            "baseline_hash": expected,
            "baseline_artifact": smoke,
            "tools": tools,
            "tool_versions": {name: command_version(path) for name, path in tools.items()},
            "baseline_scripts": scripts,
            "errors": sorted(set(errors)),
        }
        return self.input_facts

    def exact_links_by_usr(self) -> dict[str, list[dict[str, Any]]]:
        payload = read_json(self.root / "traceability" / "traceability.json", {}) or {}
        result: dict[str, list[dict[str, Any]]] = {}
        for link in payload.get("links", []):
            if link.get("status") != "EXACT":
                continue
            result.setdefault(str(link.get("clang_usr", "")), []).append({
                "anchor_id": link.get("spec_anchor_id"),
                "page": link.get("spec_page"),
                "section": link.get("spec_section"),
                "short_anchor": link.get("spec_anchor_id"),
                "evidence": link.get("evidence", ""),
                "status": "EXACT",
            })
        return result

    def reviewed_overrides(self) -> list[dict[str, Any]]:
        payload = read_json(self.root / "contracts" / "reviewed-overrides.json", {}) or {}
        return [item for item in payload.get("overrides", []) if item.get("match")]

    def tool_candidate_facts(self) -> dict[str, dict[str, Any]]:
        """Return only candidates that the analysis facts marked eligible.

        Reviewed overrides may provide exact domain/semantics evidence, but
        they must never turn into a function selector.  Keep this gate backed
        by the generated candidate ranking and dynamic coverage facts so a
        reviewed data entry can enrich a tool-selected leaf only.
        """
        candidates_payload = read_json(self.root / "facts" / "candidates.json", {}) or {}
        coverage_payload = read_json(self.root / "coverage" / "coverage.json", {}) or {}
        coverage_by_usr = {
            str(item.get("clang_usr")): item
            for item in coverage_payload.get("functions", [])
            if item.get("clang_usr")
        }
        result: dict[str, dict[str, Any]] = {}
        for rank, candidate in enumerate(candidates_payload.get("ranked_candidates", []), start=1):
            usr = str(candidate.get("clang_usr", ""))
            coverage = coverage_by_usr.get(usr, {})
            if (
                not usr
                or candidate.get("eligible") is not True
                or coverage.get("eligible_after_coverage") is not True
            ):
                continue
            result[usr] = {
                "rank": rank,
                "score": candidate.get("score"),
                "candidate": copy.deepcopy(candidate),
                "coverage": copy.deepcopy(coverage),
            }
        return result

    def function_parameters(self, contract: dict[str, Any]) -> list[dict[str, Any]]:
        """Recover original Clang parameter facts when older locks omitted them."""
        function = contract_function(contract)
        parameters = function.get("parameters")
        if isinstance(parameters, list) and parameters:
            return copy.deepcopy(parameters)
        usr = str(function.get("clang_usr", ""))
        facts = read_json(self.root / "facts" / "functions.json", {}) or {}
        for candidate in facts.get("functions", []):
            if str(candidate.get("clang_usr", "")) == usr and isinstance(candidate.get("parameters"), list):
                return copy.deepcopy(candidate["parameters"])
        return []

    @staticmethod
    def reviewed_override_matches(
        contract: dict[str, Any],
        override: dict[str, Any],
        exact_links: dict[str, list[dict[str, Any]]],
    ) -> bool:
        """Match reviewed evidence by facts identity, never by selection order."""
        match = override.get("match", {}) or {}
        if not match:
            return False
        usr = str(contract_function(contract).get("clang_usr", ""))
        if match.get("clang_usr") and str(match.get("clang_usr")) != usr:
            return False
        if match.get("code_anchor_id") and str(match.get("code_anchor_id")) != f"code:function:{usr}":
            return False
        links = exact_links.get(usr, [])
        link_ids = {str(link.get("anchor_id")) for link in links}
        if match.get("exact_anchor_id") and str(match.get("exact_anchor_id")) not in link_ids:
            return False
        if match.get("spec_anchor_id"):
            requested = str(match.get("spec_anchor_id"))
            override_ids = {
                str(link.get("anchor_id"))
                for link in override.get("spec_links", [])
                if isinstance(link, dict)
            }
            if requested not in link_ids and requested not in override_ids:
                return False
        return bool(
            match.get("clang_usr")
            or match.get("code_anchor_id")
            or match.get("exact_anchor_id")
            or match.get("spec_anchor_id")
        )

    def apply_reviewed_overrides(self) -> list[dict[str, Any]]:
        """Build effective contracts without editing generated locked JSON.

        A reviewed override is evidence-driven data.  It can resolve an
        existing locked leaf only when it names the facts identity and carries
        its own exact PDF anchor, while the immutable locked contract remains
        untouched for audit and rollback.
        """
        exact = self.exact_links_by_usr()
        overrides = self.reviewed_overrides()
        effective: list[dict[str, Any]] = []
        reviewed_root = self.ci / "reviewed-contracts"
        for original in self.locked_contracts:
            contract = copy.deepcopy(original)
            override = next(
                (
                    item for item in overrides
                    if item.get("review_status") == "REVIEWED"
                    and self.reviewed_override_matches(contract, item, exact)
                    and item.get("interface")
                    and item.get("semantics")
                    and (
                        item.get("spec_links")
                        or exact.get(str(contract_function(contract).get("clang_usr")))
                    )
                ),
                None,
            )
            if not override:
                effective.append(contract)
                continue
            contract["interface"] = copy.deepcopy(override["interface"])
            contract["semantics"] = copy.deepcopy(override["semantics"])
            contract["spec_links"] = copy.deepcopy(
                override.get("spec_links")
                or exact.get(str(contract_function(contract).get("clang_usr")), [])
            )
            contract["obligations"] = list(override.get("obligations", []))
            dependencies = copy.deepcopy(contract.get("dependencies", {}) or {})
            dependencies.update(copy.deepcopy(override.get("dependencies", {}) or {}))
            dependencies["unresolved"] = list((override.get("dependencies", {}) or {}).get("unresolved", []))
            contract["dependencies"] = dependencies
            contract["reviewed_evidence"] = copy.deepcopy(override.get("evidence", []))
            contract["reviewed_override_applied"] = {
                "match": copy.deepcopy(override.get("match", {})),
                "review_status": override.get("review_status"),
                "reviewed_by": override.get("reviewed_by"),
            }
            contract["origin"] = "tool_discovered_reviewed_override"
            contract["status"] = "LOCKED"
            contract["lock_status"] = "LOCKED_GENERATED_REVIEWED"
            effective.append(contract)
            write_json(reviewed_root / f"{contract_id(contract)}.json", contract)
        return effective

    def freeze_ports(self, interface: dict[str, Any]) -> list[dict[str, Any]]:
        if interface.get("ports"):
            return list(interface["ports"])
        ports = []
        for item in interface.get("inputs", []):
            ports.append({
                "name": safe_identifier(str(item.get("name", "input"))),
                "role": str(item.get("name", "input")),
                "direction": "input",
                "width": int(item.get("logical_width") or 32),
                "signed": bool(item.get("signed", False)),
                "c_type": item.get("c_type", "int"),
                "legal_domain": item.get("legal_domain", {}),
            })
        for item in interface.get("flattened_pointer_dependencies", []):
            port_name = str(item.get("port_name") or item.get("field") or "field")
            ports.append({
                "name": safe_identifier(port_name),
                "role": str(item.get("role") or item.get("field") or port_name),
                "direction": "input",
                "width": int(item.get("logical_width") or 32),
                "signed": bool(item.get("signed", False)),
                "c_type": item.get("c_type", "int"),
                "legal_domain": item.get("legal_domain", {}),
            })
        output = interface.get("output", {}) or {}
        ports.append({
            "name": safe_identifier(str(output.get("name", "return_value"))),
            "role": "return_value",
            "direction": "output",
            "width": int(output.get("logical_width") or 32),
            "signed": bool(output.get("signed", True)),
            "c_type": output.get("c_type", "int"),
        })
        return ports

    def materialize_new_contracts(self) -> list[dict[str, Any]]:
        if self.input_facts.get("errors"):
            return []
        facts = read_json(self.root / "facts" / "functions.json", {}) or {}
        exact = self.exact_links_by_usr()
        overrides = self.reviewed_overrides()
        candidate_facts = self.tool_candidate_facts()
        effective_locked = self.apply_reviewed_overrides()
        known = {str(contract_function(item).get("clang_usr")) for item in effective_locked}
        discovered = []
        for function in facts.get("functions", []):
            usr = str(function.get("clang_usr", ""))
            candidate = candidate_facts.get(usr)
            proposal = function.get("proposal", {}) or {}
            candidate_identity = {"function": {"clang_usr": usr}}
            override = next(
                (
                    item for item in overrides
                    if item.get("review_status") == "REVIEWED"
                    and self.reviewed_override_matches(candidate_identity, item, exact)
                    and item.get("interface")
                    and item.get("semantics")
                ),
                None,
            )
            reviewed_links = exact.get(usr, []) if override else []
            if override and not reviewed_links:
                reviewed_links = copy.deepcopy(override.get("spec_links", []))
            if (not usr or not candidate or usr in known or not override or not reviewed_links
                    or not proposal.get("combinational_candidate") or function.get("callees")):
                continue
            interface = copy.deepcopy(override.get("interface", {}))
            interface["ports"] = self.freeze_ports(interface)
            name = str(function.get("name", "candidate"))
            cid = safe_identifier(name).lower()
            source_path = source_path_for(function, pathlib.Path(str(self.input_facts["source_dir"])))
            try:
                body, span = extract_function_body(source_path, name, function.get("line"))
            except (OSError, RuntimeError):
                continue
            contract = {
                "schema_version": 2,
                "contract_id": cid,
                "status": "LOCKED",
                "origin": "tool_discovered_reviewed_override",
                "function": {
                    "clang_usr": usr,
                    "name": name,
                    "qualified_name": name,
                    "source_file": source_path.name,
                    "source_span": span,
                    "source_body_sha256": digest(body),
                    "parameters": function.get("parameters", []),
                    "return_type": function.get("return_type", "int"),
                },
                "interface": interface,
                "semantics": override.get("semantics", {}),
                "obligations": [],
                "dependencies": {
                    "direct_callees": list(function.get("callees", [])),
                    "read_fields": [item.get("name") for item in function.get("field_reads", []) if isinstance(item, dict)],
                    "unresolved": [],
                },
                "spec_links": copy.deepcopy(override.get("spec_links", reviewed_links)),
                "reviewed_evidence": override.get("evidence", []),
                "selection": {
                    "new_work": True,
                    "basis": "tool-ranked candidate and coverage facts + exact traceability + reviewed domain evidence",
                    "candidate_rank": candidate.get("rank"),
                    "candidate_score": candidate.get("score"),
                    "fact_source": "facts/functions.json",
                    "candidate_source": "facts/candidates.json",
                    "coverage_source": "coverage/coverage.json",
                },
            }
            write_json(self.root / "ci" / "discovered-contracts" / f"{cid}.json", contract)
            discovered.append(contract)
        self.contracts = effective_locked + discovered
        return discovered

    def dependency_graph(self) -> dict[str, Any]:
        by_usr = {str(contract_function(item).get("clang_usr")): contract_id(item) for item in self.contracts}
        callgraph = read_json(self.root / "facts" / "callgraph.json", {}) or {}
        all_sites = []
        for edge in callgraph.get("edges", []):
            caller_usr = str(edge.get("caller_usr", ""))
            callee_usr = str(edge.get("callee_usr", ""))
            all_sites.append({
                "caller_contract": by_usr.get(caller_usr),
                "callee_contract": by_usr.get(callee_usr),
                "caller_usr": caller_usr,
                "callee_usr": callee_usr,
                "caller_function": edge.get("caller_name"),
                "callee_function": edge.get("callee_name"),
                "location": edge.get("location", {}),
                "source": "facts/callgraph.json",
            })
        edges = sorted({(site["caller_contract"], site["callee_contract"]) for site in all_sites if site.get("caller_contract") and site.get("callee_contract")})
        adjacency = {contract_id(item): [] for item in self.contracts}
        for caller, callee in edges:
            adjacency.setdefault(caller, []).append(callee)
        cycles = []
        visiting: list[str] = []
        visited: set[str] = set()

        def visit(node: str) -> None:
            if node in visiting:
                cycles.append(visiting[visiting.index(node):] + [node])
                return
            if node in visited:
                return
            visiting.append(node)
            for child in sorted(set(adjacency.get(node, []))):
                visit(child)
            visiting.pop()
            visited.add(node)

        for node in sorted(adjacency):
            visit(node)
        hashes = {contract_id(item): digest(item) for item in self.contracts}
        dependency_hashes = {}
        for cid in adjacency:
            related = [site for site in all_sites if site.get("caller_contract") == cid or site.get("callee_contract") == cid]
            dependency_hashes[cid] = digest({"sites": related, "contract_hashes": hashes})
        self.dependency_info = {
            "all_call_sites": sorted(all_sites, key=lambda item: (str(item.get("caller_function")), str(item.get("callee_function")), canonical(item.get("location", {})))),
            "call_sites": [site for site in all_sites if site.get("caller_contract") and site.get("callee_contract")],
            "edges": [{"caller": caller, "callee": callee} for caller, callee in edges],
            "adjacency": {key: sorted(set(value)) for key, value in sorted(adjacency.items())},
            "cycles": cycles,
            "dependency_hashes": dependency_hashes,
        }
        return self.dependency_info

    def cache_key(self, contract: dict[str, Any]) -> tuple[str, dict[str, str]]:
        cid = contract_id(contract)
        command = os.environ.get("DSC_CICD_GENERATOR_CMD", "")
        hashes = {
            "pipeline": "executable-cicd-v2",
            "agent": file_hash(pathlib.Path(__file__)),
            "source": str(self.input_facts.get("source_hash", "MISSING")),
            "spec": str(self.input_facts.get("spec_hash", "MISSING")),
            "contract": digest(contract),
            "dependency": self.dependency_info.get("dependency_hashes", {}).get(cid, digest([])),
            "prompt": file_hash(self.root / "PROMPT.md") if (self.root / "PROMPT.md").is_file() else "MISSING",
            "model": os.environ.get("DSC_CICD_MODEL", "external-generator-hook"),
            "generator": digest(command),
            "tools": digest(self.input_facts.get("tool_versions", {})),
            "shards": os.environ.get("DSC_CICD_SHARDS", "4"),
            "workers": os.environ.get("DSC_CICD_WORKERS", "2"),
        }
        return digest(hashes), hashes

    def ready(self, contract: dict[str, Any]) -> tuple[bool, list[str]]:
        reasons = unresolved_reasons(contract)
        if contract.get("status") != "LOCKED":
            reasons.append("contract_not_locked")
        if not contract_exact_links(contract):
            reasons.append("no_exact_spec_link")
        cid = contract_id(contract)
        if any(cid in cycle for cycle in self.dependency_info.get("cycles", [])):
            reasons.append("recursive_or_combinational_dependency_cycle")
        return not reasons, sorted(set(reasons))

    def interface_shape(self, contract: dict[str, Any]) -> list[tuple[Any, ...]]:
        return sorted((str(port.get("direction")), str(port.get("name")), int(port.get("width", 0)), bool(port.get("signed"))) for port in contract.get("interface", {}).get("ports", []))

    def prior_contract(self, cid: str) -> dict[str, Any]:
        return next((item for item in self.previous_state.get("contracts", []) if item.get("contract_id") == cid), {})

    def cache_entry(self, key: str) -> dict[str, Any]:
        entries = self.cache.get("entries", {}) if isinstance(self.cache, dict) else {}
        if isinstance(entries, list):
            return next((item for item in entries if item.get("cache_key") == key), {})
        return entries.get(key, {}) if isinstance(entries, dict) else {}

    def cache_valid(self, entry: dict[str, Any], key: str) -> bool:
        if not entry or entry.get("cache_key") != key or entry.get("valid") is not True:
            return False
        artifact = pathlib.Path(str(entry.get("artifact_dir", "")))
        if not artifact.is_absolute():
            artifact = self.root / artifact
        return artifact.is_dir() and (artifact / "unit-receipt.json").is_file() and (artifact / "bitstream-receipt.json").is_file()

    def choose_dependency_pair(self, selected: list[str]) -> dict[str, Any] | None:
        candidates = [site for site in self.dependency_info.get("all_call_sites", []) if site.get("callee_contract") in set(selected) and site.get("caller_usr") != site.get("callee_usr")]
        if not candidates:
            return None
        chosen = sorted(candidates, key=lambda item: (str(item.get("callee_contract")), str(item.get("caller_function")), canonical(item.get("location", {}))))[0]
        return {
            "caller_contract": chosen.get("caller_contract"),
            "caller_usr": chosen.get("caller_usr"),
            "caller_function": chosen.get("caller_function"),
            "callee_contract": chosen.get("callee_contract"),
            "callee_usr": chosen.get("callee_usr"),
            "callee_function": chosen.get("callee_function"),
            "selection_basis": "smallest acyclic direct call site from facts/callgraph.json",
            "call_sites": [site for site in self.dependency_info.get("all_call_sites", []) if site.get("caller_usr") == chosen.get("caller_usr") and site.get("callee_usr") == chosen.get("callee_usr")],
        }

    def build_plan(self) -> dict[str, Any]:
        entries = []
        ready = []
        blocked = []
        discovered = {contract_id(item) for item in self.contracts if item.get("origin") == "tool_discovered_reviewed_override"}
        prior_shapes = {str(item.get("contract_id")): item.get("interface_shape", []) for item in self.previous_state.get("contracts", []) if item.get("current_state") == "PROMOTED"}
        for contract in sorted(self.contracts, key=contract_id):
            if not contract.get("interface", {}).get("ports"):
                contract.setdefault("interface", {})["ports"] = self.freeze_ports(contract.get("interface", {}))
            cid = contract_id(contract)
            key, hashes = self.cache_key(contract)
            is_ready, reasons = self.ready(contract)
            entry = self.cache_entry(key)
            stale = [name for name, value in hashes.items() if self.prior_contract(cid).get("hashes", {}).get(name) not in (None, value)]
            force_regenerate = os.environ.get("DSC_CICD_FORCE_REGENERATE", "").lower() in {"1", "true", "yes"}
            cache_hit = self.cache_valid(entry, key) and not force_regenerate
            item = {
                "contract_id": cid,
                "function": contract_function(contract).get("name"),
                "clang_usr": contract_function(contract).get("clang_usr"),
                "origin": contract.get("origin", "locked_contract"),
                "new_work": cid in discovered,
                "contract_hash": hashes["contract"],
                "cache_key": key,
                "hashes": hashes,
                "interface_shape": self.interface_shape(contract),
                "dependencies": sorted(self.dependency_info.get("adjacency", {}).get(cid, [])),
                "call_sites": [site for site in self.dependency_info.get("call_sites", []) if site.get("caller_contract") == cid],
                "ready": is_ready,
                "blocked_reasons": reasons,
                "stale": bool(stale),
                "stale_reasons": stale,
                "cache_hit": cache_hit,
                "initial_state": entry.get("state") if cache_hit else "CONTRACT_LOCKED" if is_ready else "DISCOVERED",
            }
            entries.append(item)
            if is_ready:
                ready.append(cid)
            else:
                blocked.append({"contract_id": cid, "function": item["function"], "reasons": reasons})
        target_contract = str(os.environ.get("DSC_CICD_TARGET_CONTRACT", "")).strip().lower()
        target_item = next((item for item in entries if item["contract_id"].lower() == target_contract), None)
        force_regenerate = os.environ.get("DSC_CICD_FORCE_REGENERATE", "").lower() in {"1", "true", "yes"}
        if target_item and target_item["ready"]:
            # The queue supplies a discovered contract id for this independent
            # batch. It is not a source-level function allowlist. A refresh can
            # deliberately rerun a verified leaf to search for a better pass.
            selected = [target_item["contract_id"]]
        else:
            selected = [item["contract_id"] for item in entries if item["ready"] and item["new_work"] and (not prior_shapes or item["interface_shape"] not in prior_shapes.values())]
            if not selected:
                selected = [item["contract_id"] for item in entries if item["ready"] and not item["cache_hit"]][:1]
            selected = sorted(selected[:max(1, int(os.environ.get("DSC_CICD_MAX_NEW", "1")))])
        for item in entries:
            item["selected"] = item["contract_id"] in selected
            item["deferred"] = bool(item["ready"] and not item["selected"])
            item["targeted"] = item["contract_id"] == (target_item or {}).get("contract_id")
            item["force_regenerate"] = force_regenerate and item["targeted"]
        self.plan = {
            "schema_version": 2,
            "agent": "executable-generic-c-to-rtl-cicd",
            "ready_contracts": ready,
            "selected_contracts": selected,
            "deferred_ready_contracts": [item["contract_id"] for item in entries if item["deferred"]],
            "blocked_contracts": blocked,
            "new_candidates": [item["contract_id"] for item in entries if item["new_work"]],
            "contracts": entries,
            "batches": [selected] if selected else [],
            "dependency_pair": self.choose_dependency_pair(selected),
            "target_contract": target_item["contract_id"] if target_item else None,
            "force_regenerate": force_regenerate,
            "generator_hook": os.environ.get("DSC_CICD_GENERATOR_CMD"),
            "input_errors": self.input_facts.get("errors", []),
        }
        self.make_dag()
        return self.plan

    def make_dag(self) -> dict[str, Any]:
        nodes = []
        edges = []
        for item in self.plan.get("contracts", []):
            cid = item["contract_id"]
            for stage, state_name in STAGE_TO_STATE.items():
                if item.get("blocked_reasons"):
                    status, failure = "BLOCKED", "; ".join(item["blocked_reasons"])
                elif not item.get("selected"):
                    status, failure = "DEFERRED", "ready but outside bounded new-work selection"
                elif item.get("cache_hit"):
                    status, failure = "CACHE_REUSED", None
                else:
                    status, failure = "PLANNED", None
                nodes.append({
                    "node_id": f"{cid}:{stage}",
                    "contract_id": cid,
                    "stage": state_name,
                    "status": status,
                    "source_hash": item["hashes"]["source"],
                    "spec_hash": item["hashes"]["spec"],
                    "contract_hash": item["hashes"]["contract"],
                    "dependency_hash": item["hashes"]["dependency"],
                    "artifacts": [],
                    "failure_reason": failure,
                })
            for first, second in zip(STATE_ORDER, STATE_ORDER[1:]):
                edges.append({"from": f"{cid}:{first}", "to": f"{cid}:{second}"})
        pair = self.plan.get("dependency_pair")
        if pair:
            edges.append({"from": f"{pair['callee_contract']}:PROMOTED", "to": f"{pair['caller_function']}:COMPOSITION"})
        self.dag = {
            "schema_version": 2,
            "state_order": list(STATE_ORDER),
            "nodes": nodes,
            "edges": edges,
            "cycles": self.dependency_info.get("cycles", []),
            "dependency_call_sites": self.dependency_info.get("all_call_sites", []),
        }
        return self.dag

    def write_plan_files(self) -> None:
        write_json(self.ci / "plan.json", self.plan)
        write_json(self.ci / "dag.json", self.dag)

    def plan_command(self) -> int:
        self.load_inputs()
        self.materialize_new_contracts()
        self.dependency_graph()
        self.build_plan()
        self.write_plan_files()
        print(json.dumps({"selected_contracts": self.plan.get("selected_contracts", []), "new_candidates": self.plan.get("new_candidates", []), "blocked_contracts": self.plan.get("blocked_contracts", []), "input_errors": self.plan.get("input_errors", [])}, sort_keys=True))
        return 2 if self.input_facts.get("errors") else 0

    def initialize_state(self) -> None:
        previous = {item.get("contract_id"): item for item in self.previous_state.get("contracts", [])}
        contracts = []
        for item in self.plan.get("contracts", []):
            old = previous.get(item["contract_id"], {})
            current = "PROMOTED" if item.get("cache_hit") else "CONTRACT_LOCKED" if item.get("selected") else "DISCOVERED"
            contracts.append({
                "contract_id": item["contract_id"],
                "function": item.get("function"),
                "origin": item.get("origin"),
                "selected": item.get("selected", False),
                "current_state": current,
                "status": "BLOCKED" if item.get("blocked_reasons") else "PENDING",
                "failure_reason": "; ".join(item.get("blocked_reasons", [])) or None,
                "hashes": item["hashes"],
                "interface_shape": item["interface_shape"],
                "history": old.get("history", [{"state": "DISCOVERED"}]),
                "artifacts": old.get("artifacts", []),
                "model_calls": 0,
                "token_count": 0,
            })
        self.state = {
            "schema_version": 2,
            "agent": "executable-generic-c-to-rtl-cicd",
            "state_order": list(STATE_ORDER),
            "contracts": contracts,
            "selected_contracts": self.plan.get("selected_contracts", []),
            "dependency_pair": self.plan.get("dependency_pair"),
            "generator_invocations": 0,
            "model_calls": 0,
            "token_count": 0,
            "rollback_mode": "C_ONLY",
        }
        self.write_state()

    def write_state(self) -> None:
        write_json(self.ci / "state.json", self.state)

    def state_item(self, cid: str) -> dict[str, Any]:
        return next(item for item in self.state.get("contracts", []) if item.get("contract_id") == cid)

    def update_state(self, cid: str, state_name: str, status: str, artifacts: Iterable[str] = (), failure: str | None = None, extra: dict[str, Any] | None = None) -> None:
        item = self.state_item(cid)
        item["current_state"] = state_name
        item["status"] = status
        item["failure_reason"] = failure
        item["artifacts"] = sorted(set(item.get("artifacts", [])).union(str(value) for value in artifacts))
        if not item.get("history") or item["history"][-1].get("state") != state_name:
            item.setdefault("history", []).append({"state": state_name, "status": status, "failure_reason": failure})
        if extra:
            item.update(extra)
        self.write_state()

    def artifact_dir(self, item: dict[str, Any]) -> pathlib.Path:
        return self.artifacts / str(item["contract_hash"])

    def contract_for_item(self, item: dict[str, Any]) -> dict[str, Any]:
        return next(contract for contract in self.contracts if contract_id(contract) == item["contract_id"])

    def build_request(self, contract: dict[str, Any], body: str) -> dict[str, Any]:
        return {
            "locked_contract": contract,
            "frozen_interface": contract.get("interface", {}),
            "c_body": body,
            "exact_spec_anchors": [{
                "anchor_id": link.get("anchor_id"),
                "page": link.get("page"),
                "section": link.get("section"),
                "short_anchor": link.get("short_anchor"),
                "evidence": link.get("evidence"),
                "status": "EXACT",
            } for link in contract_exact_links(contract)],
        }

    def validate_rtl(self, source: str, ports: list[dict[str, Any]]) -> list[str]:
        scrubbed = re.sub(r"//.*|/\*.*?\*/", "", source, flags=re.S)
        reasons = [pattern for pattern in FORBIDDEN_RTL if re.search(pattern, scrubbed, flags=re.I)]
        if not re.search(r"\bmodule\s+[A-Za-z_][A-Za-z0-9_]*", scrubbed):
            reasons.append("missing_module")
        if not re.search(r"\bendmodule\b", scrubbed):
            reasons.append("missing_endmodule")
        for port in ports:
            if not re.search(r"\b" + re.escape(str(port["name"])) + r"\b", scrubbed):
                reasons.append("missing_port:" + str(port["name"]))
        return sorted(set(reasons))

    def run_process(self, command: list[str], cwd: pathlib.Path | None = None,
                    env: dict[str, str] | None = None, timeout: int = 600) -> dict[str, Any]:
        started = time.time()
        merged_env = os.environ.copy()
        if env:
            merged_env.update({str(key): str(value) for key, value in env.items()})
        try:
            result = subprocess.run(
                [str(value) for value in command],
                cwd=str(cwd or self.root),
                env=merged_env,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                encoding="utf-8",
                errors="replace",
                timeout=timeout,
                check=False,
            )
            output = result.stdout or ""
            return {
                "command": [str(value) for value in command],
                "cwd": str(cwd or self.root),
                "returncode": result.returncode,
                "output": output[-20000:],
                "duration_seconds": round(time.time() - started, 3),
            }
        except subprocess.TimeoutExpired as error:
            return {
                "command": [str(value) for value in command],
                "cwd": str(cwd or self.root),
                "returncode": 124,
                "output": str(error),
                "duration_seconds": round(time.time() - started, 3),
                "timeout": True,
            }
        except OSError as error:
            return {
                "command": [str(value) for value in command],
                "cwd": str(cwd or self.root),
                "returncode": 127,
                "output": str(error),
                "duration_seconds": round(time.time() - started, 3),
                "os_error": True,
            }

    def render_interface(self, contract: dict[str, Any], module: str) -> str:
        ports = contract.get("interface", {}).get("ports", [])
        declarations = []
        for port in ports:
            width = max(1, int(port.get("width", 1)))
            signed = " signed" if port.get("signed") else ""
            range_text = f" [{width - 1}:0]" if width > 1 else ""
            declarations.append(
                f"    {port.get('direction', 'input')} logic{signed}{range_text} {port.get('name')}"
            )
        return "module " + safe_identifier(module) + " (\n" + ",\n".join(declarations) + "\n);\nendmodule\n"

    def render_pointer_array_oracle(
        self,
        contract: dict[str, Any],
        inputs: list[dict[str, Any]],
        output: str,
        flattened: list[dict[str, Any]],
        ignored: list[dict[str, Any]],
    ) -> str:
        function = contract_function(contract)
        name = str(function.get("name"))
        parameters = self.function_parameters(contract)
        if not parameters:
            raise RuntimeError("pointer-array oracle requires original C parameter facts")
        array_items = [item for item in flattened if item.get("parameter") and item.get("index") is not None]
        arrays: dict[str, list[dict[str, Any]]] = {}
        for item in array_items:
            arrays.setdefault(str(item.get("parameter")), []).append(item)
        ignored_by_parameter = {
            str(item.get("parameter")): item for item in ignored if item.get("parameter")
        }
        declarations: list[str] = []
        call_arguments: list[str] = []
        local_setup: list[str] = []
        local_dependencies: list[str] = []
        known_ports = {str(port.get("name")) for port in inputs}
        for parameter in parameters:
            parameter_name = str(parameter.get("name", ""))
            parameter_type = str(parameter.get("type", "int")).strip()
            if not parameter_name or not re.match(r"^[A-Za-z_][A-Za-z0-9_]*$", parameter_name):
                raise RuntimeError(f"invalid C parameter name: {parameter_name}")
            declarations.append(f"{parameter_type} {parameter_name}")
            if not parameter.get("pointer"):
                if parameter_name not in known_ports:
                    raise RuntimeError(f"unfrozen scalar parameter: {parameter_name}")
                call_arguments.append(parameter_name)
                continue
            if parameter_name in arrays:
                items = arrays[parameter_name]
                length = max(int(item.get("index", 0)) for item in items) + 1
                local_dependencies.append(f"int {parameter_name}[{length}] = {{0}};")
                for item in sorted(items, key=lambda value: int(value.get("index", 0))):
                    port_name = safe_identifier(str(item.get("port_name") or item.get("field")))
                    local_setup.append(
                        f"{parameter_name}[{int(item.get('index', 0))}] = {port_name};"
                    )
                call_arguments.append(parameter_name)
                continue
            dependency = ignored_by_parameter.get(parameter_name)
            if dependency:
                parameter_type_base = re.sub(r"\s*\*.*$", "", parameter_type).strip()
                local_dependencies.append(f"{parameter_type_base} {parameter_name} = {{0}};")
                call_arguments.append(f"&{parameter_name}")
                continue
            raise RuntimeError(f"unfrozen pointer parameter: {parameter_name}")
        local_names = ", ".join(str(port["name"]) for port in inputs)
        input_arguments = ", ".join(f"&{port['name']}" for port in inputs)
        format_string = " ".join(["%d"] * len(inputs))
        include_types = any("_t" in str(item.get("c_type", "")) for item in ignored)
        setup = "\n                        ".join(local_setup)
        dependency_declarations = "\n                        ".join(local_dependencies)
        include_block = '#include "dsc_types.h"\n' if include_types else ""
        return textwrap.dedent(
            f"""
            #include <stdio.h>
            {include_block}extern int {name}({', '.join(declarations)});
            int main(int argc, char **argv) {{
                FILE *input = stdin;
                if (argc > 1) {{
                    input = fopen(argv[1], "rb");
                    if (!input) return 2;
                }}
                int {local_names};
                int {output};
                while (fscanf(input, "{format_string}", {input_arguments}) == {len(inputs)}) {{
                    {dependency_declarations}
                    {setup}
                    {output} = {name}({', '.join(call_arguments)});
                    printf("%d\\n", {output});
                }}
                if (input != stdin) fclose(input);
                return 0;
            }}
            """
        ).strip() + "\n"

    def render_oracle(self, contract: dict[str, Any]) -> str:
        function = contract_function(contract)
        name = str(function.get("name"))
        interface = contract.get("interface", {}) or {}
        inputs = [
            port for port in contract.get("interface", {}).get("ports", [])
            if port.get("direction") == "input"
        ]
        if not inputs or any(parameter_is_pointer(port) for port in inputs):
            raise RuntimeError("oracle only supports scalar input ports")
        declarations = ", ".join(f"int {port['name']}" for port in inputs)
        local_declarations = ", ".join(str(port["name"]) for port in inputs)
        format_string = " ".join(["%d"] * len(inputs))
        arguments = ", ".join(f"&{port['name']}" for port in inputs)
        call = ", ".join(str(port["name"]) for port in inputs)
        output = str(next(
            (port.get("name") for port in contract.get("interface", {}).get("ports", [])
             if port.get("direction") == "output"),
            "return_value",
        ))
        flattened = list(interface.get("flattened_pointer_dependencies", []) or [])
        ignored = list(interface.get("ignored_pointer_dependencies", []) or [])
        pointer_array_dependencies = [
            item for item in flattened if item.get("parameter") and item.get("index") is not None
        ]
        if pointer_array_dependencies or ignored:
            return self.render_pointer_array_oracle(contract, inputs, output, flattened, ignored)
        records = sorted({str(item.get("record")) for item in flattened if item.get("record")})
        if records:
            parameters = self.function_parameters(contract)
            record_names: dict[str, str] = {}
            parameter_record_types: dict[str, str] = {}
            parameter_declarations: list[str] = []
            for parameter in parameters:
                parameter_name = str(parameter.get("name", ""))
                parameter_type = str(parameter.get("type", "int")).strip()
                if not parameter_name or not re.match(r"^[A-Za-z_][A-Za-z0-9_]*$", parameter_name):
                    raise RuntimeError(f"invalid C parameter name: {parameter_name}")
                parameter_declarations.append(f"{parameter_type} {parameter_name}")
                if parameter.get("pointer"):
                    record_type = re.sub(r"\s*\*.*$", "", parameter_type).strip()
                    parameter_record_types[parameter_name] = record_type
                    if record_type in records:
                        record_names[record_type] = parameter_name
            for record_type in records:
                if record_type not in record_names:
                    state_name = re.sub(r"_t$", "", record_type)
                    if not re.match(r"^[A-Za-z_][A-Za-z0-9_]*$", state_name):
                        state_name = "state"
                    record_names[record_type] = state_name
            flattened_port_names = {
                safe_identifier(str(item.get("port_name") or item.get("field", "")))
                for item in flattened
            }
            scalar_inputs = [port for port in inputs if str(port.get("name")) not in flattened_port_names]
            if parameters:
                pointer_records = {
                    re.sub(r"\s*\*.*$", "", str(parameter.get("type", ""))).strip()
                    for parameter in parameters if parameter.get("pointer")
                }
                if not set(records).issubset(pointer_records):
                    raise RuntimeError("C parameters do not cover flattened record dependencies")
            else:
                parameter_declarations = [
                    f"{record_type} *{record_names[record_type]}" for record_type in records
                ]
                parameter_declarations.extend(
                    f"int {port['name']}" for port in inputs
                    if port.get("name") not in {item.get("field") for item in flattened}
                )
            assignments = []
            for item in flattened:
                field = str(item.get("field", ""))
                port = next((value for value in inputs if value.get("name") == field), None)
                if not field or port is None or not re.match(r"^[A-Za-z_][A-Za-z0-9_]*$", field):
                    raise RuntimeError(f"flattened state dependency is not a scalar port: {field}")
                record_type = str(item.get("record", ""))
                state_name = record_names.get(record_type)
                if not state_name:
                    raise RuntimeError(f"missing record parameter for: {record_type}")
                c_type = str(item.get("c_type", port.get("c_type", "int")))
                if "*" in c_type and "[" not in c_type:
                    raise RuntimeError(f"flattened pointer table is not a scalar port: {field}")
                if "[" in c_type and "]" in c_type:
                    assignments.append(
                        f"for (size_t i = 0; i < sizeof({state_name}.{field}) / sizeof({state_name}.{field}[0]); ++i) "
                        f"{state_name}.{field}[i] = {field};"
                    )
                else:
                    assignments.append(f"{state_name}.{field} = {field};")
            state_setup = "\n                ".join(assignments)
            if parameters:
                call = ", ".join(
                    (
                        f"&{record_names[parameter_record_types[str(parameter.get('name'))]]}"
                        if parameter.get("pointer")
                        else str(parameter.get("name"))
                    )
                    for parameter in parameters
                )
            else:
                call = ", ".join(f"&{record_names[record_type]}" for record_type in records)
                scalar_names = [
                    str(port["name"]) for port in inputs
                    if port.get("name") not in {item.get("field") for item in flattened}
                ]
                if scalar_names:
                    call += (", " if call else "") + ", ".join(scalar_names)
            declarations = ", ".join(parameter_declarations)
            local_declarations = ", ".join(str(port["name"]) for port in inputs)
            arguments = ", ".join(f"&{port['name']}" for port in inputs)
            format_string = " ".join(["%d"] * len(inputs))
            record_declarations = "\n                        ".join(
                f"{record_type} {record_names[record_type]} = {{0}};" for record_type in records
            )
            return textwrap.dedent(
                f"""
                #include <stddef.h>
                #include <stdio.h>
                #include "dsc_types.h"
                extern int {name}({declarations});
                int main(int argc, char **argv) {{
                    FILE *input = stdin;
                    if (argc > 1) {{
                        input = fopen(argv[1], "rb");
                        if (!input) return 2;
                    }}
                    int {local_declarations};
                    int {output};
                    while (fscanf(input, "{format_string}", {arguments}) == {len(inputs)}) {{
                        {record_declarations}
                        {state_setup}
                        {output} = {name}({call});
                        printf("%d\\n", {output});
                    }}
                    if (input != stdin) fclose(input);
                    return 0;
                }}
                """
            ).strip() + "\n"
        return textwrap.dedent(
            f"""
            #include <stdio.h>
            extern int {name}({declarations});
            int main(int argc, char **argv) {{
                FILE *input = stdin;
                if (argc > 1) {{
                    input = fopen(argv[1], "rb");
                    if (!input) return 2;
                }}
                int {local_declarations};
                int {output};
                while (fscanf(input, "{format_string}", {arguments}) == {len(inputs)}) {{
                    {output} = {name}({call});
                    printf("%d\\n", {output});
                }}
                if (input != stdin) fclose(input);
                return 0;
            }}
            """
        ).strip() + "\n"

    def legal_vector_iterator(self, contract: dict[str, Any], input_ports: list[dict[str, Any]],
                              values: list[list[int]]) -> tuple[Iterable[tuple[int, ...]], dict[str, Any]]:
        """Return legal vectors, including reviewed conditional domains.

        Flattened state dependencies are represented as selected scalar values
        in the frozen interface.  When the contract supplies a reviewed
        qlevel-by-bit-depth map and a conditional leftRecon domain, enumerate
        that relation instead of the invalid Cartesian product.
        """
        names = [str(port.get("name")) for port in input_ports]
        normalized = {re.sub(r"[^a-z0-9]", "", name.lower()): name for name in names}
        bit_depth_name = normalized.get("cpntbitdepth")
        qlevel_name = normalized.get("qlevel")
        left_recon_name = normalized.get("leftrecon")
        qlevel_map = (contract.get("semantics", {}) or {}).get("qlevel_max_by_cpnt_bit_depth", {}) or {}
        if bit_depth_name and qlevel_name and left_recon_name and qlevel_map:
            by_name = {name: values[index] for index, name in enumerate(names)}
            fixed_names = [name for name in names if name not in {bit_depth_name, qlevel_name, left_recon_name}]
            fixed_values = [by_name[name] for name in fixed_names]
            q_domain = by_name[qlevel_name]
            left_domain = by_name[left_recon_name]

            def constrained() -> Iterable[tuple[int, ...]]:
                for fixed in itertools.product(*fixed_values) if fixed_values else [()]:
                    context = dict(zip(fixed_names, fixed))
                    for bit_depth in by_name[bit_depth_name]:
                        max_qlevel = int(qlevel_map.get(str(bit_depth), qlevel_map.get(bit_depth, max(q_domain))))
                        for qlevel in q_domain:
                            if int(qlevel) > max_qlevel:
                                continue
                            for left_recon in left_domain:
                                if int(left_recon) >= (1 << int(bit_depth)):
                                    continue
                                context.update({
                                    bit_depth_name: int(bit_depth),
                                    qlevel_name: int(qlevel),
                                    left_recon_name: int(left_recon),
                                })
                                yield tuple(int(context[name]) for name in names)

            return constrained(), {
                "kind": "conditional",
                "constraint": "qlevel <= qlevel_max_by_cpnt_bit_depth and leftRecon < (1 << cpntBitDepth)",
                "qlevel_max_by_cpnt_bit_depth": {str(key): int(value) for key, value in qlevel_map.items()},
                "source": "locked contract semantics",
                "ports": [bit_depth_name, qlevel_name, left_recon_name],
            }

        return itertools.product(*values), {
            "kind": "cartesian",
            "source": "frozen per-port legal domains",
        }

    def render_harness(self, contract: dict[str, Any], module: str) -> str:
        ports = contract.get("interface", {}).get("ports", [])
        inputs = [port for port in ports if port.get("direction") == "input"]
        output = next((port for port in ports if port.get("direction") == "output"), None)
        if output is None or any(parameter_is_pointer(port) for port in inputs):
            raise RuntimeError("Verilator harness only supports scalar ports")
        input_names = [str(port["name"]) for port in inputs]
        format_string = " ".join(["%lld"] * len(inputs))
        variables = "\n".join(f"    long long {name};" for name in input_names)
        reads = f'    while (std::fscanf(input, "{format_string}", ' + ", ".join(f"&{name}" for name in input_names) + f") == {len(inputs)}) {{"
        assigns = "\n".join(f"        dut.{name} = static_cast<long long>({name});" for name in input_names)
        width = max(1, int(output.get("width", 1)))
        if output.get("signed"):
            output_expr = f"sign_extend(static_cast<long long>(dut.{output['name']}), {width})"
        else:
            output_expr = f"static_cast<unsigned long long>(dut.{output['name']})"
        return textwrap.dedent(
            f"""
            #include <cstdio>
            #include <cstdint>
            #include <iostream>
            #include "verilated.h"
            #include "V{safe_identifier(module)}.h"

            static long long sign_extend(long long value, int width) {{
                if (width >= 63) return value;
                const long long bit = 1LL << (width - 1);
                const long long mask = (1LL << width) - 1;
                value &= mask;
                return (value & bit) ? value - (1LL << width) : value;
            }}

            int main(int argc, char **argv) {{
                Verilated::commandArgs(argc, argv);
                FILE *input = stdin;
                if (argc > 1) {{
                    input = std::fopen(argv[1], "rb");
                    if (!input) return 2;
                }}
            {variables}
                {reads}
                    V{safe_identifier(module)} dut;
            {assigns}
                    dut.eval();
                    std::cout << {output_expr} << "\\n";
                }}
                if (input != stdin) std::fclose(input);
                return 0;
            }}
            """
        ).strip() + "\n"

    def generate_static_artifacts(self, contract: dict[str, Any], artifact: pathlib.Path) -> None:
        artifact.mkdir(parents=True, exist_ok=True)
        cid = contract_id(contract)
        write_json(artifact / "locked-contract.json", contract)
        write_json(artifact / "input-packing.json", {
            "schema_version": 1,
            "ports": [
                {
                    "name": port.get("name"),
                    "role": port.get("role"),
                    "direction": port.get("direction"),
                    "width": port.get("width"),
                    "signed": port.get("signed", False),
                    "packing": f"bits[{int(port.get('width', 1)) - 1}:0]",
                }
                for port in contract.get("interface", {}).get("ports", [])
            ],
            "bit_order": "little-endian integer text to packed Verilator port",
        })
        domains = []
        for port in contract.get("interface", {}).get("ports", []):
            domain = port.get("legal_domain") or {}
            if not domain and port.get("role") == "return_value":
                domain = {"kind": "range", "range": contract.get("interface", {}).get("output", {}).get("legal_range", [])}
            domains.append({"port": port.get("name"), "role": port.get("role"), "domain": domain})
        write_json(artifact / "legal-domain.json", {
            "schema_version": 1,
            "complete": all(item["domain"].get("range") or item["domain"].get("values") for item in domains if item["role"] != "return_value"),
            "ports": domains,
            "proof_basis": "exact spec/table plus reviewed runtime range override",
        })
        write_json(artifact / "mutations.json", {
            "schema_version": 1,
            "mutations": [
                {"id": "signedness_flip", "description": "interpret signed input as unsigned"},
                {"id": "boundary_minus_one", "description": "subtract one at each lower legal boundary"},
                {"id": "boundary_plus_one", "description": "add one at each upper legal boundary"},
                {"id": "rounding_off_by_one", "description": "change quantization rounding table entry"},
                {"id": "array_index_off_by_one", "description": "select adjacent table element"},
            ],
            "status": "PLANNED_AND_USED_BY_VERIFIER",
        })
        write_json(artifact / "receipt-schema.json", {
            "schema_version": 2,
            "required": [
                "execution_status",
                "candidate",
                "verification_status",
                "compile_once",
                "shards",
                "smallest_counterexample",
            ],
        })
        write_json(artifact / "artifact-manifest.json", {
            "schema_version": 2,
            "contract_id": cid,
            "generated_now": True,
            "do_not_edit": True,
            "source_of_truth": "locked-contract.json + executed receipts",
        })
        (artifact / "interface.sv").write_text(
            self.render_interface(contract, f"{cid}_interface"), encoding="utf-8"
        )
        (artifact / "oracle.c").write_text(self.render_oracle(contract), encoding="utf-8")
        (artifact / "shadow_replacement_wrapper.c").write_text(
            "/* Generated overlay wrapper is written only in the isolated source copy. */\n",
            encoding="utf-8",
        )
        (artifact / "vector_generator.py").write_text(
            "# Generated vector format: one decimal value per frozen input port, per line.\\n",
            encoding="utf-8",
        )

    def generate_artifacts(self, contract: dict[str, Any], item: dict[str, Any], artifact: pathlib.Path) -> dict[str, Any]:
        if self.input_facts.get("errors"):
            artifact.mkdir(parents=True, exist_ok=True)
            receipt = {
                "schema_version": 2,
                "execution_status": "EXECUTED_NOW",
                "status": "INFRASTRUCTURE_FAILURE",
                "contract_id": contract_id(contract),
                "model_calls": 0,
                "tokens": 0,
                "candidates": [],
                "reason": "; ".join(str(error) for error in self.input_facts["errors"]),
            }
            write_json(artifact / "generation.json", receipt)
            return receipt
        self.generate_static_artifacts(contract, artifact)
        _, body, span = source_body(contract, pathlib.Path(str(self.input_facts["source_dir"])))
        request = self.build_request(contract, body)
        request_path = artifact / "generation-request.json"
        write_json(request_path, request)
        output_dir = artifact / "generated"
        if output_dir.exists():
            shutil.rmtree(output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)
        hook = os.environ.get("DSC_CICD_GENERATOR_CMD", "").strip()
        receipt: dict[str, Any] = {
            "schema_version": 2,
            "execution_status": "EXECUTED_NOW",
            "contract_id": contract_id(contract),
            "source_span": span,
            "context_keys": ["locked_contract", "frozen_interface", "c_body", "exact_spec_anchors"],
            "candidate_limit": 4,
            "hook": hook or "MISSING",
        }
        if not hook:
            receipt.update({
                "status": "GENERATION_REQUIRED",
                "model_calls": 0,
                "tokens": 0,
                "candidates": [],
                "reason": "DSC_CICD_GENERATOR_CMD is not configured",
            })
            write_json(artifact / "generation.json", receipt)
            return receipt
        command = shlex.split(hook)
        result = self.run_process(
            command + [str(request_path), str(output_dir)],
            cwd=self.root,
            timeout=int(os.environ.get("DSC_CICD_GENERATOR_TIMEOUT", "600")),
        )
        self.generator_invocations += 1
        telemetry = read_json(output_dir / "telemetry.json", {}) or {}
        self.generator_tokens += int(telemetry.get("tokens_in", 0)) + int(telemetry.get("tokens_out", 0))
        candidates = []
        if result["returncode"] == 0:
            for path in sorted(output_dir.glob("*.sv")):
                source = path.read_text(encoding="utf-8", errors="replace")
                reasons = self.validate_rtl(source, contract.get("interface", {}).get("ports", []))
                candidates.append({
                    "candidate": path.stem,
                    "path": str(path.relative_to(artifact)),
                    "sha256": file_hash(path),
                    "validation": "PASS" if not reasons else "FAIL",
                    "validation_reasons": reasons,
                })
        status = "PASS" if result["returncode"] == 0 and candidates and all(item["validation"] == "PASS" for item in candidates) else "GENERATION_FAILED"
        if len(candidates) > 4:
            status = "GENERATION_FAILED"
            receipt["reason"] = "candidate_limit_exceeded"
        receipt.update({
            "status": status,
            "model_calls": int(telemetry.get("model_calls", 1)),
            "tokens": int(telemetry.get("tokens_in", 0)) + int(telemetry.get("tokens_out", 0)),
            "candidates": candidates[:4],
            "command": result,
            "telemetry": telemetry,
        })
        write_json(artifact / "generation.json", receipt)
        return receipt
    def port_domain(self, port: dict[str, Any]) -> list[int]:
        domain = port.get("legal_domain", {}) or {}
        if domain.get("values"):
            return [int(value) for value in domain["values"]]
        bounds = domain.get("range")
        if isinstance(bounds, list) and len(bounds) == 2:
            lower, upper = int(bounds[0]), int(bounds[1])
            return list(range(lower, upper + 1))
        raise RuntimeError(f"incomplete legal domain for port {port.get('name')}")

    def make_shards(self, contract: dict[str, Any], artifact: pathlib.Path) -> dict[str, Any]:
        inputs = [
            port for port in contract.get("interface", {}).get("ports", [])
            if port.get("direction") == "input"
        ]
        values = [self.port_domain(port) for port in inputs]
        shard_count = max(1, int(os.environ.get("DSC_CICD_SHARDS", "4")))
        shard_dir = artifact / "shards"
        if shard_dir.exists():
            shutil.rmtree(shard_dir)
        shard_dir.mkdir(parents=True, exist_ok=True)
        paths = [shard_dir / f"shard-{index:03d}.vectors" for index in range(shard_count)]
        handles = [path.open("w", encoding="utf-8") for path in paths]
        count = 0
        vector_iterator, vector_strategy = self.legal_vector_iterator(contract, inputs, values)
        try:
            for vector in vector_iterator:
                handles[count % shard_count].write(" ".join(str(value) for value in vector) + "\n")
                count += 1
        finally:
            for handle in handles:
                handle.close()
        shards = [
            {
                "shard_id": index,
                "path": str(path.relative_to(artifact)),
                "vectors": self.count_lines(path),
            }
            for index, path in enumerate(paths)
        ]
        return {
            "complete": count > 0 and all(item["vectors"] > 0 for item in shards),
            "input_ports": [port.get("name") for port in inputs],
            "total_vectors": count,
            "shard_count": shard_count,
            "shards": shards,
            "vector_strategy": vector_strategy,
        }

    @staticmethod
    def count_lines(path: pathlib.Path) -> int:
        with path.open("r", encoding="utf-8") as handle:
            return sum(1 for _ in handle)

    def compile_c_oracle(self, contract: dict[str, Any], artifact: pathlib.Path) -> dict[str, Any]:
        build_dir = artifact / "oracle-build"
        if build_dir.exists():
            shutil.rmtree(build_dir)
        build_dir.mkdir(parents=True, exist_ok=True)
        clang = self.input_facts["tools"].get("clang") or "clang"
        source_dir = pathlib.Path(str(self.input_facts["source_dir"]))
        objects: list[pathlib.Path] = []
        commands = []
        source_files = sorted(source_dir.glob("*.c"))
        if not source_files:
            return {"status": "INFRASTRUCTURE_FAILURE", "reason": "no C translation units"}
        for source in source_files:
            if source.name == "codec_main.c":
                continue
            object_path = build_dir / (source.stem + ".o")
            result = self.run_process(
                [clang, "-std=c99", "-O0", "-g", "-I", str(source_dir), "-c", str(source), "-o", str(object_path)],
                cwd=source_dir,
                timeout=int(os.environ.get("DSC_CICD_COMPILE_TIMEOUT", "600")),
            )
            commands.append(result)
            if result["returncode"] != 0:
                return {
                    "status": "INFRASTRUCTURE_FAILURE",
                    "reason": f"C oracle compile failed for {source.name}",
                    "commands": commands,
                }
            objects.append(object_path)
        wrapper = artifact / "oracle.c"
        wrapper_object = build_dir / "oracle.o"
        result = self.run_process(
            [clang, "-std=c99", "-O0", "-I", str(source_dir), "-c", str(wrapper), "-o", str(wrapper_object)],
            cwd=artifact,
            timeout=int(os.environ.get("DSC_CICD_COMPILE_TIMEOUT", "600")),
        )
        commands.append(result)
        if result["returncode"] != 0:
            return {"status": "INFRASTRUCTURE_FAILURE", "reason": "oracle wrapper compile failed", "commands": commands}
        objects.append(wrapper_object)
        binary = build_dir / "c_oracle"
        result = self.run_process([clang, "-O0", "-o", str(binary)] + [str(path) for path in objects], cwd=artifact)
        commands.append(result)
        status = "PASS" if result["returncode"] == 0 and binary.is_file() else "INFRASTRUCTURE_FAILURE"
        receipt = {
            "status": status,
            "binary": str(binary.relative_to(artifact)) if binary.is_file() else None,
            "commands": commands,
            "compiled_translation_units": [path.name for path in source_files if path.name != "codec_main.c"],
        }
        write_json(artifact / "oracle-compile-receipt.json", receipt)
        return receipt

    def module_name(self, source: str) -> str:
        match = re.search(r"\bmodule\s+([A-Za-z_][A-Za-z0-9_]*)\s*\(", source)
        if not match:
            raise RuntimeError("candidate has no discoverable module")
        return match.group(1)

    def compile_candidate(self, contract: dict[str, Any], artifact: pathlib.Path, candidate: dict[str, Any]) -> dict[str, Any]:
        path = artifact / str(candidate["path"])
        source = path.read_text(encoding="utf-8", errors="replace")
        module = self.module_name(source)
        candidate_build = artifact / "candidate-build" / safe_identifier(str(candidate["candidate"]))
        if candidate_build.exists():
            shutil.rmtree(candidate_build)
        candidate_build.mkdir(parents=True, exist_ok=True)
        harness = candidate_build / "harness.cpp"
        harness.write_text(self.render_harness(contract, module), encoding="utf-8")
        verilator = self.input_facts["tools"].get("verilator") or "verilator"
        command = [
            verilator,
            "--cc",
            str(path),
            "--exe",
            str(harness),
            "--build",
            "-j",
            "1",
            "--Mdir",
            str(candidate_build / "obj"),
            "--top-module",
            module,
            "--Wno-fatal",
        ]
        result = self.run_process(command, cwd=artifact, timeout=int(os.environ.get("DSC_CICD_VERILATOR_TIMEOUT", "1200")))
        binary = candidate_build / "obj" / ("V" + module)
        receipt = {
            "candidate": candidate["candidate"],
            "module": module,
            "status": "PASS" if result["returncode"] == 0 and binary.is_file() else "FAIL",
            "compile_once": True,
            "binary": str(binary.relative_to(artifact)) if binary.is_file() else None,
            "command": result,
        }
        write_json(candidate_build / "compile-receipt.json", receipt)
        candidate["module"] = module
        candidate["compile"] = receipt
        return receipt

    def run_shard(self, artifact: pathlib.Path, shard: dict[str, Any],
                  oracle: pathlib.Path, rtl: pathlib.Path,
                  stop_event: threading.Event) -> dict[str, Any]:
        commands = {
            "oracle": [str(oracle), str(artifact / shard["path"])],
            "rtl": [str(rtl), str(artifact / shard["path"])],
        }
        if stop_event.is_set():
            return {"shard_id": shard["shard_id"], "status": "CANCELLED", "vectors": 0, "commands": commands}
        shard_path = artifact / shard["path"]
        output_dir = artifact / "shard-results"
        output_dir.mkdir(parents=True, exist_ok=True)
        prefix = f"{safe_identifier(str(rtl.parent.parent.name))}-{int(shard['shard_id']):03d}"
        oracle_out = output_dir / (prefix + "-oracle.out")
        rtl_out = output_dir / (prefix + "-rtl.out")
        oracle_err = output_dir / (prefix + "-oracle.err")
        rtl_err = output_dir / (prefix + "-rtl.err")
        started = time.time()
        with shard_path.open("rb") as vector_input, oracle_out.open("wb") as output, oracle_err.open("wb") as error:
            oracle_process = subprocess.run(
                [str(oracle), str(shard_path)],
                stdin=vector_input,
                stdout=output,
                stderr=error,
                timeout=int(os.environ.get("DSC_CICD_SHARD_TIMEOUT", "1200")),
                check=False,
            )
        if oracle_process.returncode != 0:
            return {
                "shard_id": shard["shard_id"],
                "status": "INFRASTRUCTURE_FAILURE",
                "vectors": shard["vectors"],
                "reason": "oracle process failed",
                "duration_seconds": round(time.time() - started, 3),
                "commands": commands,
            }
        if stop_event.is_set():
            return {"shard_id": shard["shard_id"], "status": "CANCELLED", "vectors": 0, "commands": commands}
        with shard_path.open("rb") as vector_input, rtl_out.open("wb") as output, rtl_err.open("wb") as error:
            rtl_process = subprocess.run(
                [str(rtl), str(shard_path)],
                stdin=vector_input,
                stdout=output,
                stderr=error,
                timeout=int(os.environ.get("DSC_CICD_SHARD_TIMEOUT", "1200")),
                check=False,
            )
        if rtl_process.returncode != 0:
            return {
                "shard_id": shard["shard_id"],
                "status": "INFRASTRUCTURE_FAILURE",
                "vectors": shard["vectors"],
                "reason": "RTL process failed",
                "duration_seconds": round(time.time() - started, 3),
                "commands": commands,
            }
        oracle_lines = oracle_out.read_text(encoding="utf-8", errors="replace").splitlines()
        rtl_lines = rtl_out.read_text(encoding="utf-8", errors="replace").splitlines()
        limit = min(len(oracle_lines), len(rtl_lines))
        mismatch = None
        for index in range(limit):
            expected = oracle_lines[index].strip()
            actual = rtl_lines[index].strip()
            if expected != actual:
                mismatch = {
                    "shard_id": shard["shard_id"],
                    "index": index,
                    "expected": expected,
                    "actual": actual,
                }
                break
        if mismatch is None and len(oracle_lines) != len(rtl_lines):
            mismatch = {
                "shard_id": shard["shard_id"],
                "index": limit,
                "expected": oracle_lines[limit] if len(oracle_lines) > limit else "<no output>",
                "actual": rtl_lines[limit] if len(rtl_lines) > limit else "<no output>",
            }
        if mismatch:
            vector_lines = shard_path.read_text(encoding="utf-8", errors="replace").splitlines()
            if mismatch["index"] < len(vector_lines):
                mismatch["inputs"] = [
                    int(value) for value in vector_lines[mismatch["index"]].split()
                ]
            stop_event.set()
            return {
                "shard_id": shard["shard_id"],
                "status": "COUNTEREXAMPLE",
                "vectors": shard["vectors"],
                "counterexample": mismatch,
                "duration_seconds": round(time.time() - started, 3),
                "commands": commands,
            }
        return {
            "shard_id": shard["shard_id"],
            "status": "PASS",
            "vectors": shard["vectors"],
            "duration_seconds": round(time.time() - started, 3),
            "commands": commands,
        }

    def unit_verify(self, contract: dict[str, Any], artifact: pathlib.Path) -> dict[str, Any]:
        started = time.time()
        shard_info = self.make_shards(contract, artifact)
        oracle_receipt = self.compile_c_oracle(contract, artifact)
        unit_receipt: dict[str, Any] = {
            "schema_version": 2,
            "execution_status": "EXECUTED_NOW",
            "contract_id": contract_id(contract),
            "domain": shard_info,
            "oracle_compile": oracle_receipt,
            "compile_once": [],
            "candidates": [],
            "smallest_counterexample": None,
        }
        if oracle_receipt.get("status") != "PASS" or not shard_info.get("complete"):
            unit_receipt["verification_status"] = "INFRASTRUCTURE_FAILURE"
            write_json(artifact / "unit-receipt.json", unit_receipt)
            return unit_receipt
        oracle = artifact / str(oracle_receipt["binary"])
        for candidate in read_json(artifact / "generation.json", {}).get("candidates", []):
            if candidate.get("validation") != "PASS":
                continue
            compile_receipt = self.compile_candidate(contract, artifact, candidate)
            unit_receipt["compile_once"].append(compile_receipt)
            if compile_receipt.get("status") != "PASS":
                candidate_result = {
                    "candidate": candidate["candidate"],
                    "verification_status": "INFRASTRUCTURE_FAILURE",
                    "shards": [],
                }
                unit_receipt["candidates"].append(candidate_result)
                continue
            rtl = artifact / str(compile_receipt["binary"])
            stop_event = threading.Event()
            shard_results: list[dict[str, Any]] = []
            cancellation_requested = False
            cancelled_futures = 0
            worker_count = max(1, min(
                shard_info["shard_count"],
                int(os.environ.get("DSC_CICD_WORKERS", "2")),
            ))
            with concurrent.futures.ThreadPoolExecutor(max_workers=worker_count) as executor:
                future_to_shard = {
                    executor.submit(self.run_shard, artifact, shard, oracle, rtl, stop_event): shard
                    for shard in shard_info["shards"]
                }
                for future in concurrent.futures.as_completed(future_to_shard):
                    shard = future_to_shard[future]
                    if future.cancelled():
                        shard_results.append({
                            "shard_id": shard["shard_id"],
                            "status": "CANCELLED",
                            "vectors": 0,
                            "commands": {
                                "oracle": [str(oracle), str(artifact / shard["path"])],
                                "rtl": [str(rtl), str(artifact / shard["path"])],
                            },
                        })
                        continue
                    result = future.result()
                    shard_results.append(result)
                    if result.get("status") == "COUNTEREXAMPLE" and not cancellation_requested:
                        cancellation_requested = True
                        stop_event.set()
                        for pending in future_to_shard:
                            if pending is not future and not pending.done() and pending.cancel():
                                cancelled_futures += 1
            mismatches = [item["counterexample"] for item in shard_results if item.get("status") == "COUNTEREXAMPLE"]
            infra = [item for item in shard_results if item.get("status") == "INFRASTRUCTURE_FAILURE"]
            smallest = min(mismatches, key=lambda item: (tuple(item.get("inputs", [])), int(item.get("shard_id", 0)), int(item.get("index", 0)))) if mismatches else None
            executed_vectors = sum(int(item.get("vectors", 0)) for item in shard_results if item.get("status") == "PASS")
            if smallest:
                status = "COUNTEREXAMPLE"
            elif infra:
                status = "INFRASTRUCTURE_FAILURE"
            elif executed_vectors == shard_info["total_vectors"]:
                status = "EXHAUSTIVE_EQUIVALENT"
            else:
                status = "UNPROVED"
            candidate_result = {
                "candidate": candidate["candidate"],
                "module": candidate.get("module"),
                "verification_status": status,
                "shards": sorted(shard_results, key=lambda item: int(item["shard_id"])),
                "vectors_executed": executed_vectors,
                "smallest_counterexample": smallest,
                "cancellation": {
                    "requested_after_counterexample": cancellation_requested,
                    "futures_cancelled": cancelled_futures,
                    "worker_count": worker_count,
                },
            }
            unit_receipt["candidates"].append(candidate_result)
            if smallest and unit_receipt.get("smallest_counterexample") is None:
                unit_receipt["smallest_counterexample"] = smallest
        promoted = next(
            (item for item in unit_receipt["candidates"] if item["verification_status"] == "EXHAUSTIVE_EQUIVALENT"),
            None,
        )
        unit_receipt["verification_status"] = "EXHAUSTIVE_EQUIVALENT" if promoted else (
            "COUNTEREXAMPLE" if any(item["verification_status"] == "COUNTEREXAMPLE" for item in unit_receipt["candidates"])
            else "UNPROVED"
        )
        unit_receipt["promoted_candidate"] = promoted.get("candidate") if promoted else None
        unit_receipt["duration_seconds"] = round(time.time() - started, 3)
        write_json(artifact / "unit-receipt.json", unit_receipt)
        return unit_receipt
    def ensure_rewriter(self) -> tuple[pathlib.Path | None, dict[str, Any]]:
        build_dir = self.root / "tmp" / "cicd-clang-rewriter"
        build_dir.mkdir(parents=True, exist_ok=True)
        binary = build_dir / "dsc-clang-rewrite"
        if binary.is_file():
            return binary, {"status": "REUSED_BUILD", "binary": str(binary)}
        cmake = locate_tool("cmake")
        llvm_config = self.input_facts["tools"].get("llvm-config")
        if not cmake or not llvm_config:
            return None, {"status": "INFRASTRUCTURE_FAILURE", "reason": "cmake or llvm-config missing"}
        llvm_result = self.run_process([llvm_config, "--cmakedir"])
        llvm_dir = (llvm_result.get("output") or "").splitlines()[0].strip()
        clang_dir = str(pathlib.Path(llvm_dir).parent / "clang")
        configure = self.run_process(
            [
                cmake,
                "-S", str(self.root / "tools"),
                "-B", str(build_dir),
                f"-DLLVM_DIR={llvm_dir}",
                f"-DClang_DIR={clang_dir}",
                "-DCMAKE_BUILD_TYPE=Release",
            ],
            cwd=self.root,
            timeout=1200,
        )
        if configure["returncode"] != 0:
            return None, {"status": "INFRASTRUCTURE_FAILURE", "reason": "rewriter configure failed", "configure": configure}
        build = self.run_process(
            [cmake, "--build", str(build_dir), "--target", "dsc-clang-rewrite", "-j", "1"],
            cwd=self.root,
            timeout=1800,
        )
        if build["returncode"] != 0 or not binary.is_file():
            return None, {"status": "INFRASTRUCTURE_FAILURE", "reason": "rewriter build failed", "configure": configure, "build": build}
        return binary, {"status": "BUILT", "binary": str(binary), "configure": configure, "build": build}

    def write_compdb_for_copy(self, source_dir: pathlib.Path, path: pathlib.Path) -> list[pathlib.Path]:
        clang = self.input_facts["tools"].get("clang") or "clang"
        entries = []
        sources = sorted(source_dir.glob("*.c"))
        for source in sources:
            entries.append({
                "directory": str(source_dir),
                "file": str(source),
                "arguments": [clang, "-std=gnu99", "-O0", "-I", str(source_dir), "-c", str(source)],
            })
        write_json(path, entries)
        return sources

    def run_overlay_rewriter(self, contract: dict[str, Any], source_dir: pathlib.Path,
                             overlay_header: pathlib.Path) -> dict[str, Any]:
        binary, build_receipt = self.ensure_rewriter()
        if not binary:
            return build_receipt
        compdb = source_dir / "compile_commands.json"
        sources = self.write_compdb_for_copy(source_dir, compdb)
        before = {str(path.relative_to(source_dir)): file_hash(path) for path in sources}
        cid = contract_id(contract)
        function = contract_function(contract)
        original_name = str(function.get("name")) + "_original"
        dispatcher_name = "dsc_cicd_invoke"
        receipt_path = source_dir / "clang-overlay-receipt.json"
        command = [
            str(binary),
            "--compdb", str(compdb),
            "--target-usr", str(function.get("clang_usr")),
            "--original-name", original_name,
            "--dispatcher-name", dispatcher_name,
            "--receipt", str(receipt_path),
        ] + [str(path) for path in sources]
        result = self.run_process(command, cwd=source_dir, timeout=1800)
        after = {str(path.relative_to(source_dir)): file_hash(path) for path in sources}
        tool_receipt = read_json(receipt_path, {}) or {}
        original_source_dir = pathlib.Path(str(self.input_facts.get("source_dir", "")))
        manifest_hashes = {str(item.get("path")): str(item.get("sha256")) for item in self.input_facts.get("source_file_hashes", [])}
        upstream_unchanged = bool(manifest_hashes) and all(
            (original_source_dir / relative).is_file() and file_hash(original_source_dir / relative) == expected
            for relative, expected in manifest_hashes.items()
        )
        changed = [
            {
                "path": path,
                "old_sha256": before.get(path),
                "new_sha256": after.get(path),
            }
            for path in sorted(set(before) | set(after))
            if before.get(path) != after.get(path)
        ]
        if tool_receipt.get("status") == "PASS" and result["returncode"] == 0:
            for changed_file in changed:
                path = source_dir / changed_file["path"]
                original = path.read_text(encoding="utf-8", errors="replace")
                if "dsc_cicd_overlay.h" not in original:
                    path.write_text('#include "dsc_cicd_overlay.h"\n' + original, encoding="utf-8")
            status = "PASS"
        else:
            status = "FAIL"
        receipt = {
            "schema_version": 2,
            "status": status,
            "contract_id": cid,
            "target_usr": function.get("clang_usr"),
            "original_name": original_name,
            "dispatcher_name": dispatcher_name,
            "upstream_source_unchanged": upstream_unchanged,
            "upstream_source_hash": self.input_facts.get("source_hash"),
            "source_copy_hashes_before": before,
            "source_copy_hashes_after": after,
            "changed_files": changed,
            "rewritten_usrs": tool_receipt.get("rewritten_usrs", []),
            "definitions_seen": tool_receipt.get("definitions_seen", 0),
            "rewritten_calls": tool_receipt.get("rewritten_calls", 0),
            "direct_calls_seen": tool_receipt.get("direct_calls_seen", 0),
            "call_sites": tool_receipt.get("call_sites", []),
            "macro_locations": tool_receipt.get("macro_locations", []),
            "indirect_locations": tool_receipt.get("indirect_locations", []),
            "failures": tool_receipt.get("failures", []),
            "tool": build_receipt,
            "command": result,
        }
        write_json(source_dir / "overlay-receipt.json", receipt)
        return receipt

    def write_overlay_sources(self, contract: dict[str, Any], source_dir: pathlib.Path,
                              module: str, candidate_sv: pathlib.Path) -> dict[str, pathlib.Path]:
        inputs = [
            port for port in contract.get("interface", {}).get("ports", [])
            if port.get("direction") == "input"
        ]
        output = next(
            port for port in contract.get("interface", {}).get("ports", [])
            if port.get("direction") == "output"
        )
        interface = contract.get("interface", {}) or {}
        flattened = list(interface.get("flattened_pointer_dependencies", []) or [])
        flattened_fields = {str(item.get("field")) for item in flattened if item.get("field")}
        function = contract_function(contract)
        original = str(function.get("name")) + "_original"
        input_declarations = ", ".join(f"int {port['name']}" for port in inputs)
        input_call = ", ".join(str(port["name"]) for port in inputs)
        caller_declarations = input_declarations
        caller_call = input_call
        rtl_call = input_call
        header_prefix = ""
        if flattened:
            records = sorted({str(item.get("record")) for item in flattened if item.get("record")})
            parameters = self.function_parameters(contract)
            record_names: dict[str, str] = {}
            parameter_specs: list[str] = []
            parameter_names: list[str] = []
            parameter_record_types: dict[str, str] = {}
            for parameter in parameters:
                parameter_name = str(parameter.get("name", ""))
                parameter_type = str(parameter.get("type", "int")).strip()
                if not parameter_name or not re.match(r"^[A-Za-z_][A-Za-z0-9_]*$", parameter_name):
                    raise RuntimeError(f"invalid C parameter name: {parameter_name}")
                parameter_specs.append(f"{parameter_type} {parameter_name}")
                parameter_names.append(parameter_name)
                if parameter.get("pointer"):
                    record_type = re.sub(r"\s*\*.*$", "", parameter_type).strip()
                    parameter_record_types[parameter_name] = record_type
                    if record_type in records:
                        record_names[record_type] = parameter_name
            for record_type in records:
                if record_type not in record_names:
                    state_name = re.sub(r"_t$", "", record_type)
                    if not re.match(r"^[A-Za-z_][A-Za-z0-9_]*$", state_name):
                        state_name = "state"
                    record_names[record_type] = state_name
            flattened_port_names = {
                safe_identifier(str(item.get("port_name") or item.get("field", "")))
                for item in flattened
            }
            scalar_inputs = [port for port in inputs if str(port.get("name")) not in flattened_port_names]
            if parameters:
                pointer_records = set(parameter_record_types.values())
                if not set(records).issubset(pointer_records):
                    raise RuntimeError("C parameters do not cover flattened record dependencies")
            else:
                parameter_specs = [
                    f"{record_type} *{record_names[record_type]}" for record_type in records
                ]
                parameter_specs.extend(f"int {port['name']}" for port in scalar_inputs)
                parameter_names = [record_names[record_type] for record_type in records]
                parameter_names.extend(str(port["name"]) for port in scalar_inputs)
            caller_declarations = ", ".join(parameter_specs)
            caller_call = ", ".join(parameter_names)
            source_body_text = ""
            try:
                _, source_body_text, _ = source_body(
                    contract,
                    pathlib.Path(str(self.input_facts.get("source_dir", source_dir))),
                )
            except (OSError, RuntimeError):
                pass
            index_name = next(
                (
                    str(port.get("name"))
                    for port in scalar_inputs
                    if re.sub(r"[^a-z0-9]", "", str(port.get("role", port.get("name"))).lower()) == "cpnt"
                ),
                "0",
            )
            rtl_arguments = []
            flattened_by_field = {str(item.get("field")): item for item in flattened}
            flattened_by_port = {
                safe_identifier(str(item.get("port_name") or item.get("field", ""))): item
                for item in flattened
            }
            for port in inputs:
                field = str(port.get("name"))
                if field in flattened_by_port and flattened_by_port[field].get("parameter"):
                    dependency = flattened_by_port[field]
                    parameter = str(dependency.get("parameter"))
                    index = int(dependency.get("index", 0))
                    rtl_arguments.append(f"{parameter}[{index}]")
                elif field in flattened_fields:
                    dependency = flattened_by_field[field]
                    record_name = record_names.get(str(dependency.get("record")))
                    if not record_name:
                        raise RuntimeError(f"missing record parameter for: {dependency.get('record')}")
                    c_type = str(dependency.get("c_type", port.get("c_type", "int")))
                    if "*" in c_type or ("[" in c_type and "]" in c_type):
                        match = re.search(
                            rf"->\s*{re.escape(field)}\s*\[\s*([A-Za-z_][A-Za-z0-9_]*)\s*\]",
                            source_body_text,
                        )
                        index = match.group(1) if match else index_name
                        rtl_arguments.append(f"{record_name}->{field}[{index}]")
                    else:
                        rtl_arguments.append(f"{record_name}->{field}")
                else:
                    rtl_arguments.append(field)
            rtl_call = ", ".join(rtl_arguments)
            header_prefix = '#include "dsc_types.h"\n'
        header = source_dir / "dsc_cicd_overlay.h"
        header.write_text(
            "#ifndef DSC_CICD_OVERLAY_H\n"
            "#define DSC_CICD_OVERLAY_H\n"
            + header_prefix
            + f"int dsc_cicd_invoke({caller_declarations});\n"
            "#endif\n",
            encoding="utf-8",
        )
        overlay = source_dir / "dsc_cicd_overlay.c"
        overlay.write_text(
            "#include <stdio.h>\n"
            "#include <stdlib.h>\n"
            "#include <string.h>\n"
            "#include \"dsc_cicd_overlay.h\"\n"
            f"extern int {original}({caller_declarations});\n"
            f"extern int dsc_cicd_rtl({input_declarations});\n"
            "static int dsc_cicd_mode(void) {\n"
            "    const char *value = getenv(\"DSC_CICD_MODE\");\n"
            "    if (value && strcmp(value, \"SHADOW\") == 0) return 1;\n"
            "    if (value && strcmp(value, \"RTL_RETURN\") == 0) return 2;\n"
            "    return 0;\n"
            "}\n"
            "static unsigned long dsc_cicd_mismatches;\n"
            f"int dsc_cicd_invoke({caller_declarations}) {{\n"
            f"    int c_value = {original}({caller_call});\n"
            "    int mode = dsc_cicd_mode();\n"
            "    if (mode == 0) return c_value;\n"
            f"    int rtl_value = dsc_cicd_rtl({rtl_call});\n"
            "    if (rtl_value != c_value) {\n"
            "        ++dsc_cicd_mismatches;\n"
            "        fprintf(stderr, \"C/RTL mismatch: c=%d rtl=%d\\n\", c_value, rtl_value);\n"
            "    }\n"
            "    return mode == 2 ? rtl_value : c_value;\n"
            "}\n",
            encoding="utf-8",
        )
        bridge = source_dir / "rtl_bridge.cpp"
        width = max(1, int(output.get("width", 1)))
        assignments = "\n".join(f"    dut.{port['name']} = static_cast<long long>({port['name']});" for port in inputs)
        input_args = ", ".join(str(port["name"]) for port in inputs)
        if output.get("signed"):
            output_expr = f"sign_extend(static_cast<long long>(dut.{output['name']}), {width})"
        else:
            output_expr = f"static_cast<int>(dut.{output['name']})"
        bridge.write_text(
            "#include <cstdint>\n"
            "#include \"verilated.h\"\n"
            f"#include \"V{safe_identifier(module)}.h\"\n"
            "double sc_time_stamp() { return 0.0; }\n"
            "static long long sign_extend(long long value, int width) {\n"
            "    if (width >= 63) return value;\n"
            "    long long bit = 1LL << (width - 1);\n"
            "    long long mask = (1LL << width) - 1;\n"
            "    value &= mask;\n"
            "    return (value & bit) ? value - (1LL << width) : value;\n"
            "}\n"
            f'extern "C" int dsc_cicd_rtl({input_declarations}) {{\n'
            f"    V{safe_identifier(module)} dut;\n"
            f"{assignments}\n"
            "    dut.eval();\n"
            f"    return static_cast<int>({output_expr});\n"
            "}\n",
            encoding="utf-8",
        )
        main = source_dir / "dsc_cicd_main.c"
        main.write_text(
            "#include <stdio.h>\n"
            "extern int dsc_cicd_original_main(int, char **);\n"
            "int main(int argc, char **argv) {\n"
            "    return dsc_cicd_original_main(argc, argv);\n"
            "}\n",
            encoding="utf-8",
        )
        return {"header": header, "overlay": overlay, "bridge": bridge, "main": main, "candidate": candidate_sv}

    def compile_overlay(self, contract: dict[str, Any], source_dir: pathlib.Path,
                        module: str, candidate_sv: pathlib.Path) -> dict[str, Any]:
        verilator = self.input_facts["tools"].get("verilator") or "verilator"
        clang = self.input_facts["tools"].get("clang") or "clang"
        clangxx = self.input_facts["tools"].get("clang++") or "clang++"
        build_dir = source_dir.parent / "overlay-build"
        if build_dir.exists():
            shutil.rmtree(build_dir)
        build_dir.mkdir(parents=True, exist_ok=True)
        obj_dir = build_dir / "rtl-object"
        verilator_result = self.run_process(
            [verilator, "--cc", str(candidate_sv), "--Mdir", str(obj_dir), "--top-module", module, "--Wno-fatal"],
            cwd=source_dir,
            timeout=1800,
        )
        if verilator_result["returncode"] != 0:
            return {"status": "INFRASTRUCTURE_FAILURE", "reason": "overlay RTL compile failed", "verilator": verilator_result}
        make_result = self.run_process(["make", "-C", str(obj_dir), "-f", f"V{module}.mk", "-j", "1"], cwd=source_dir, timeout=1800)
        archive = obj_dir / f"V{module}__ALL.a"
        if make_result["returncode"] != 0 or not archive.is_file():
            return {"status": "INFRASTRUCTURE_FAILURE", "reason": "Verilator model archive failed", "verilator": verilator_result, "make": make_result}
        objects: list[pathlib.Path] = []
        commands = []
        source_files = sorted(source_dir.glob("*.c"))
        for source in source_files:
            object_path = build_dir / (source.stem + ".o")
            extra = ["-Dmain=dsc_cicd_original_main"] if source.name == "codec_main.c" else []
            result = self.run_process(
                [clang, "-std=gnu99", "-O3", "-I", str(source_dir)] + extra + ["-c", str(source), "-o", str(object_path)],
                cwd=source_dir,
                timeout=1200,
            )
            commands.append(result)
            if result["returncode"] != 0:
                return {"status": "INFRASTRUCTURE_FAILURE", "reason": f"overlay C compile failed for {source.name}", "commands": commands, "verilator": verilator_result, "make": make_result}
            objects.append(object_path)
        bridge_object = build_dir / "rtl_bridge.o"
        verilator_include = pathlib.Path(verilator).resolve().parent.parent / "share" / "verilator" / "include"
        bridge_result = self.run_process(
            [clangxx, "-std=c++17", "-O2", "-I", str(obj_dir), "-I", str(verilator_include), "-c", str(source_dir / "rtl_bridge.cpp"), "-o", str(bridge_object)],
            cwd=source_dir,
            timeout=1200,
        )
        commands.append(bridge_result)
        if bridge_result["returncode"] != 0:
            return {"status": "INFRASTRUCTURE_FAILURE", "reason": "RTL bridge compile failed", "commands": commands}
        objects.append(bridge_object)
        binary = source_dir / "dsc"
        runtime_archive = obj_dir / "libverilated.a"
        runtime_archives = [str(path) for path in (runtime_archive, obj_dir / "libverilated_threads.a") if path.is_file()]
        link_result = self.run_process(
            [clangxx, "-O2", "-o", str(binary)] + [str(path) for path in objects] + [str(archive)] + runtime_archives,
            cwd=source_dir,
            timeout=1800,
        )
        commands.append(link_result)
        status = "PASS" if link_result["returncode"] == 0 and binary.is_file() else "INFRASTRUCTURE_FAILURE"
        receipt = {
            "status": status,
            "binary": str(binary),
            "module": module,
            "candidate": candidate_sv.name,
            "commands": commands,
            "verilator": verilator_result,
            "make_archive": make_result,
        }
        write_json(source_dir / "overlay-compile-receipt.json", receipt)
        return receipt
    def discover_matrix(self) -> list[dict[str, Any]]:
        scripts = [str(item) for item in self.input_facts.get("baseline_scripts", [])]
        selected = []
        preferred = [
            "bittrue_smoke/run_c_baseline.sh",
            "bittrue_smoke/run_c_baseline_10bpc.sh",
            "bittrue_smoke/run_c_baseline_native420.sh",
        ]
        for name in preferred:
            if name in scripts and name not in [item["script"] for item in selected]:
                selected.append(self.scenario_info(name))
        if len(selected) < 3:
            for name in scripts:
                if name not in [item["script"] for item in selected]:
                    selected.append(self.scenario_info(name))
                if len(selected) >= 3:
                    break
        return selected

    def scenario_info(self, script: str) -> dict[str, Any]:
        model_root = pathlib.Path(str(self.input_facts["source_root"]))
        path = model_root / script
        text = path.read_text(encoding="utf-8", errors="replace")
        golden_match = re.search(r'\bgolden\s*=\s*["]([^"]+)', text)
        if not golden_match:
            golden_match = re.search(r'\bgolden\s*=\s*["]?\$model_dir/([^"\s]+)', text)
        golden = golden_match.group(1) if golden_match else ""
        if golden.startswith("$model_dir/"):
            golden = golden[len("$model_dir/"):]
        expected_match = re.search(r'\bexpected_hash\s*=\s*["]([0-9a-fA-F]+)["]', text)
        expected = expected_match.group(1) if expected_match else None
        config_match = re.search(r'(?:-F|--config)\s+([A-Za-z0-9_./{}-]+)', text)
        config = config_match.group(1) if config_match else ""
        if config.startswith("$model_dir/"):
            config = config[len("$model_dir/"):]
        return {
            "script": script,
            "name": pathlib.Path(script).stem,
            "golden": golden,
            "config": config,
            "expected_sha256": expected,
        }

    def copy_model(self, label: str) -> pathlib.Path:
        model_root = pathlib.Path(str(self.input_facts["source_root"]))
        temp_root = pathlib.Path(tempfile.mkdtemp(prefix=f"dsc-cicd-{label}-", dir=str(self.root / "tmp")))
        destination = temp_root / model_root.name
        ignore = shutil.ignore_patterns(".git", "__pycache__", "target", "build", "dsc-rs", "operator_bittrue")
        shutil.copytree(model_root, destination, ignore=ignore)
        return destination

    def run_matrix(self, contract: dict[str, Any], artifact: pathlib.Path,
                   candidate: dict[str, Any]) -> dict[str, Any]:
        scenarios = self.discover_matrix()
        if len(scenarios) < 1:
            return {"status": "INFRASTRUCTURE_FAILURE", "reason": "no baseline scripts discovered"}
        base_model = self.copy_model("baseline")
        overlay_model: pathlib.Path | None = None
        baseline_results = []
        try:
            for scenario in scenarios:
                script_path = base_model / scenario["script"]
                result = self.run_process([str(script_path)], cwd=base_model, timeout=1800)
                golden = base_model / scenario["golden"]
                actual = file_hash(golden) if golden.is_file() else None
                baseline_results.append({
                    "scenario": scenario,
                    "status": "PASS" if result["returncode"] == 0 and actual else "FAIL",
                    "command": result,
                    "sha256": actual,
                    "size_bytes": golden.stat().st_size if golden.is_file() else None,
                })
            if not all(item["status"] == "PASS" for item in baseline_results):
                return {
                    "status": "INFRASTRUCTURE_FAILURE",
                    "reason": "baseline matrix failed",
                    "baseline": baseline_results,
                }
            overlay_temp = pathlib.Path(tempfile.mkdtemp(prefix="dsc-cicd-overlay-", dir=str(self.root / "tmp")))
            overlay_model = overlay_temp / base_model.name
            shutil.copytree(base_model, overlay_model, ignore=shutil.ignore_patterns(".git", "__pycache__", "target", "build", "dsc-rs", "operator_bittrue"))
            candidate_sv = artifact / str(candidate["path"])
            overlay_copy_sv = overlay_model / "candidate.sv"
            shutil.copy2(candidate_sv, overlay_copy_sv)
            module = str(candidate.get("module") or self.module_name(candidate_sv.read_text(encoding="utf-8")))
            overlay_paths = self.write_overlay_sources(contract, overlay_model / "source", module, overlay_copy_sv)
            overlay_receipt = self.run_overlay_rewriter(contract, overlay_model / "source", overlay_paths["header"])
            if overlay_receipt.get("status") != "PASS":
                return {
                    "status": "INFRASTRUCTURE_FAILURE",
                    "reason": "Clang overlay rewrite failed",
                    "baseline": baseline_results,
                    "overlay": overlay_receipt,
                }
            compile_receipt = self.compile_overlay(contract, overlay_model / "source", module, overlay_copy_sv)
            if compile_receipt.get("status") != "PASS":
                return {
                    "status": "INFRASTRUCTURE_FAILURE",
                    "reason": "caller/callee overlay compile failed",
                    "baseline": baseline_results,
                    "overlay": overlay_receipt,
                    "compile": compile_receipt,
                }
            mode_results: dict[str, Any] = {}
            binary = overlay_model / "source" / "dsc"
            for mode in ("C_ONLY", "SHADOW", "RTL_RETURN"):
                scenario_results = []
                for baseline in baseline_results:
                    scenario = baseline["scenario"]
                    golden = overlay_model / scenario["golden"]
                    if golden.exists():
                        golden.unlink()
                    command = self.run_process(
                        [str(binary), "-F", str(overlay_model / scenario["config"])],
                        cwd=overlay_model,
                        env={"DSC_CICD_MODE": mode},
                        timeout=1800,
                    )
                    actual = file_hash(golden) if golden.is_file() else None
                    output = str(command.get("output", ""))
                    mismatch_count = len(re.findall(r"C/RTL mismatch", output))
                    scenario_results.append({
                        "scenario": scenario,
                        "status": "PASS" if command["returncode"] == 0 and actual == baseline["sha256"] and mismatch_count == 0 else "FAIL",
                        "command": command,
                        "sha256": actual,
                        "size_bytes": golden.stat().st_size if golden.is_file() else None,
                        "baseline_sha256": baseline["sha256"],
                        "mismatch_count": mismatch_count,
                    })
                mode_results[mode] = {
                    "status": "PASS" if all(item["status"] == "PASS" for item in scenario_results) else "FAIL",
                    "scenarios": scenario_results,
                }
            overlay_receipt = scrub_paths(overlay_receipt, [base_model, overlay_model, self.root])
            compile_receipt = scrub_paths(compile_receipt, [base_model, overlay_model, self.root])
            mode_results = scrub_paths(mode_results, [base_model, overlay_model, self.root])
            all_modes_pass = all(
                mode_results.get(mode, {}).get("status") == "PASS"
                for mode in ("C_ONLY", "SHADOW", "RTL_RETURN")
            )
            result = {
                "status": "PASS" if all_modes_pass else "FAIL",
                "matrix_scripts_discovered": len(self.input_facts.get("baseline_scripts", [])),
                "scenarios": [item["scenario"] for item in baseline_results],
                "baseline": scrub_paths(baseline_results, [base_model, overlay_model, self.root]),
                "overlay": overlay_receipt,
                "compile": compile_receipt,
                "modes": mode_results,
                "candidate": candidate.get("candidate"),
                "execution_status": "EXECUTED_NOW",
            }
            write_json(artifact / "shadow-receipt.json", result["modes"]["SHADOW"])
            write_json(artifact / "rtl-return-receipt.json", result["modes"]["RTL_RETURN"])
            write_json(artifact / "bitstream-receipt.json", result)
            write_json(artifact / "overlay-receipt.json", result["overlay"])
            return scrub_paths(result, [base_model, overlay_model, self.root])
        finally:
            shutil.rmtree(base_model.parent, ignore_errors=True)
            if overlay_model is not None:
                shutil.rmtree(overlay_model.parent, ignore_errors=True)

    def verify_rejected_candidates(self, contract: dict[str, Any], artifact: pathlib.Path,
                                   generation: dict[str, Any], unit: dict[str, Any]) -> list[dict[str, Any]]:
        generated = {
            str(candidate.get("candidate")): candidate
            for candidate in generation.get("candidates", [])
        }
        results: list[dict[str, Any]] = []
        for candidate_result in unit.get("candidates", []):
            unit_status = str(candidate_result.get("verification_status", "UNPROVED"))
            if unit_status == "EXHAUSTIVE_EQUIVALENT":
                continue
            name = str(candidate_result.get("candidate", "candidate"))
            candidate = generated.get(name, {})
            rejected_artifact = artifact / "rejected" / safe_identifier(name)
            if rejected_artifact.exists():
                shutil.rmtree(rejected_artifact)
            source = artifact / str(candidate.get("path", ""))
            candidate_path = rejected_artifact / "generated" / source.name
            candidate_path.parent.mkdir(parents=True, exist_ok=True)
            matrix: dict[str, Any] = {}
            candidate_copy = dict(candidate)
            candidate_copy["path"] = str(candidate_path.relative_to(rejected_artifact))
            candidate_copy["module"] = candidate_result.get("module") or candidate.get("module")
            if not source.is_file() or not candidate_copy.get("module"):
                matrix_status = "NOT_RUN_COMPILE_FAILURE"
                bitstream_gate = "FAIL"
            else:
                shutil.copy2(source, candidate_path)
                matrix = self.run_matrix(contract, rejected_artifact, candidate_copy)
                matrix_status = str(matrix.get("status", "INFRASTRUCTURE_FAILURE"))
                bitstream_gate = "PASS" if matrix_status == "PASS" else "FAIL"
            composition_status = "FAIL"
            if matrix:
                composition_status = "PASS" if (
                    matrix.get("modes", {}).get("SHADOW", {}).get("status") == "PASS"
                    and matrix.get("modes", {}).get("RTL_RETURN", {}).get("status") == "PASS"
                ) else "FAIL"
            expected = unit_status != "EXHAUSTIVE_EQUIVALENT" and bitstream_gate == "FAIL"
            full_receipt = {
                "schema_version": 2,
                "execution_status": "EXECUTED_NOW",
                "status": "EXPECTED_REJECTION" if expected else "FAIL",
                "candidate": name,
                "unit_gate": {
                    "status": "FAIL",
                    "verification_status": unit_status,
                    "vectors_executed": candidate_result.get("vectors_executed", 0),
                    "shards": candidate_result.get("shards", []),
                    "counterexample": candidate_result.get("smallest_counterexample"),
                },
                "bitstream_gate": {
                    "status": bitstream_gate,
                    "matrix_status": matrix_status,
                    "receipt": "bitstream-receipt.json" if matrix else None,
                },
                "composition_gate": {
                    "status": composition_status,
                    "call_sites": matrix.get("overlay", {}).get("call_sites", []) if matrix else [],
                    "caller_core_with_callee_rtl": matrix.get("modes", {}).get("RTL_RETURN", {}) if matrix else {},
                },
                "matrix": matrix,
                "expected_rejection": expected,
            }
            write_json(rejected_artifact / "rejection-receipt.json", full_receipt)
            results.append({
                "candidate": name,
                "status": full_receipt["status"],
                "unit_gate": "FAIL",
                "unit_verification_status": unit_status,
                "bitstream_gate": bitstream_gate,
                "composition_gate": composition_status,
                "matrix_status": matrix_status,
                "expected_rejection": expected,
                "receipt": str((rejected_artifact / "rejection-receipt.json").relative_to(self.root)),
                "counterexample": candidate_result.get("smallest_counterexample"),
            })
        return results

    def dependency_verify(self, contract: dict[str, Any], item: dict[str, Any],
                          artifact: pathlib.Path, unit: dict[str, Any],
                          matrix: dict[str, Any]) -> dict[str, Any]:
        pair = self.plan.get("dependency_pair")
        if not pair:
            receipt = {
                "schema_version": 2,
                "execution_status": "EXECUTED_NOW",
                "status": "NOT_APPLICABLE",
                "pair": None,
                "checks": {},
                "dependency_ports": [],
                "call_sites_from_callgraph": [],
                "counterexample": unit.get("smallest_counterexample"),
                "execution_evidence": {
                    "callee_oracle_compile": unit.get("oracle_compile", {}).get("commands", []),
                    "callee_candidate_compile": unit.get("compile_once", []),
                    "vectors": unit.get("domain", {}),
                },
                "failure_reason": None,
            }
            write_json(artifact / "dependency-receipt.json", receipt)
            return receipt
        sites = []
        overlay = matrix.get("overlay", {}) if isinstance(matrix, dict) else {}
        sites.extend(overlay.get("call_sites", []) if isinstance(overlay, dict) else [])
        direct_sites = [
            site for site in self.dependency_info.get("all_call_sites", [])
            if site.get("callee_contract") == item.get("contract_id")
        ]
        checks = {
            "caller_core_with_callee_C": matrix.get("modes", {}).get("C_ONLY", {}).get("status") == "PASS",
            "callee_RTL_against_callee_C": unit.get("promoted_candidate") is not None,
            "caller_core_plus_callee_RTL": matrix.get("modes", {}).get("RTL_RETURN", {}).get("status") == "PASS",
            "direct_call_sites_discovered": bool(direct_sites),
            "overlay_rewritten_call_sites": bool(sites),
        }
        receipt = {
            "schema_version": 2,
            "execution_status": "EXECUTED_NOW",
            "status": "PASS" if all(checks.values()) else "FAIL",
            "pair": pair,
            "checks": checks,
            "dependency_ports": [
                {
                    "caller_function": site.get("caller_function") or (pair or {}).get("caller_function"),
                    "callee_usr": site.get("callee_usr") or (pair or {}).get("callee_usr"),
                    "location": site.get("location"),
                    "arguments": site.get("arguments", []),
                    "result": site.get("result", "return_value"),
                    "transport": "direct argument/result ports",
                }
                for site in sites
            ],
            "call_sites_from_callgraph": direct_sites,
            "counterexample": unit.get("smallest_counterexample"),
            "execution_evidence": {
                "callee_oracle_compile": unit.get("oracle_compile", {}).get("commands", []),
                "callee_candidate_compile": unit.get("compile_once", []),
                "callee_rtl_against_c": [
                    candidate for candidate in unit.get("candidates", [])
                    if candidate.get("candidate") == unit.get("promoted_candidate")
                ],
                "caller_core_with_callee_c": matrix.get("modes", {}).get("C_ONLY", {}),
                "caller_core_plus_callee_rtl": matrix.get("modes", {}).get("RTL_RETURN", {}),
                "vectors": unit.get("domain", {}),
                "counterexamples": [
                    candidate.get("smallest_counterexample")
                    for candidate in unit.get("candidates", [])
                    if candidate.get("smallest_counterexample") is not None
                ],
            },
            "failure_reason": None if all(checks.values()) else "dependency composition did not pass all real gates",
        }
        write_json(artifact / "dependency-receipt.json", receipt)
        return receipt

    def run_contract(self, item: dict[str, Any]) -> dict[str, Any]:
        cid = str(item["contract_id"])
        contract = self.contract_for_item(item)
        if item.get("blocked_reasons"):
            self.update_state(cid, "DISCOVERED", "BLOCKED", failure="; ".join(item["blocked_reasons"]))
            return {"contract_id": cid, "status": "BLOCKED", "reason": item["blocked_reasons"]}
        if not item.get("selected"):
            self.update_state(cid, "CONTRACT_LOCKED", "DEFERRED", failure="bounded selection deferred")
            return {"contract_id": cid, "status": "DEFERRED"}
        artifact = self.artifact_dir(item)
        cache_entry = self.cache_entry(item["cache_key"])
        if item.get("cache_hit"):
            cached_unit = read_json(artifact / "unit-receipt.json", {}) or {}
            cached_bitstream = read_json(artifact / "bitstream-receipt.json", {}) or {}
            self.update_state(cid, "PROMOTED", "CACHE_REUSED", artifacts=[str(artifact.relative_to(self.root))], extra={
                "model_calls": 0,
                "token_count": 0,
                "cache": "REUSED_VERIFIED_RECEIPT",
            })
            result = {
                "contract_id": cid,
                "status": "CACHE_REUSED",
                "execution_status": "REUSED_VERIFIED_RECEIPT",
                "unit": cached_unit,
                "matrix": cached_bitstream,
                "dependency": read_json(artifact / "dependency-receipt.json", {}) or {},
                "rejected_candidates": cached_unit.get("rejected_candidates", []),
                "cache_entry": cache_entry,
            }
            self.run_results.append(result)
            return result
        try:
            self.update_state(cid, "CONTRACT_LOCKED", "EXECUTING")
            generation = self.generate_artifacts(contract, item, artifact)
            self.update_state(cid, "RTL_GENERATED", generation.get("status", "FAIL"), artifacts=[str(artifact.relative_to(self.root))], extra={
                "model_calls": generation.get("model_calls", 0),
                "token_count": generation.get("tokens", 0),
            })
            if generation.get("status") != "PASS":
                result = {"contract_id": cid, "status": generation.get("status", "GENERATION_FAILED"), "generation": generation}
                self.run_results.append(result)
                return result
            unit = self.unit_verify(contract, artifact)
            unit_status = "PASS" if unit.get("promoted_candidate") else unit.get("verification_status", "UNPROVED")
            self.update_state(cid, "UNIT_VERIFIED", unit_status, artifacts=[str(artifact.relative_to(self.root))], extra={
                "unit_receipt": "EXECUTED_NOW",
            })
            rejected_candidates = self.verify_rejected_candidates(contract, artifact, generation, unit)
            unit["rejected_candidates"] = rejected_candidates
            write_json(artifact / "unit-receipt.json", unit)
            if not unit.get("promoted_candidate"):
                result = {
                    "contract_id": cid,
                    "status": unit.get("verification_status", "UNPROVED"),
                    "generation": generation,
                    "unit": unit,
                    "rejected_candidates": rejected_candidates,
                }
                self.run_results.append(result)
                return result
            candidate = next(item for item in generation.get("candidates", []) if item.get("candidate") == unit["promoted_candidate"])
            matrix = self.run_matrix(contract, artifact, candidate)
            shadow_status = matrix.get("modes", {}).get("SHADOW", {}).get("status") == "PASS"
            rtl_status = matrix.get("modes", {}).get("RTL_RETURN", {}).get("status") == "PASS"
            self.update_state(cid, "SHADOW_PASS", "PASS" if shadow_status else "FAIL", artifacts=[str(artifact.relative_to(self.root))])
            self.update_state(cid, "RTL_RETURN_PASS", "PASS" if rtl_status else "FAIL", artifacts=[str(artifact.relative_to(self.root))])
            dependency = self.dependency_verify(contract, item, artifact, unit, matrix)
            self.update_state(cid, "DEPENDENCIES_VERIFIED", dependency.get("status", "FAIL"), artifacts=[str(artifact.relative_to(self.root))])
            bitstream_status = matrix.get("status") == "PASS"
            self.update_state(cid, "BITSTREAM_PASS", "PASS" if bitstream_status else "FAIL", artifacts=[str(artifact.relative_to(self.root))])
            final = "PROMOTED" if bitstream_status and dependency.get("status") == "PASS" else "FAILED"
            self.update_state(cid, "PROMOTED" if final == "PROMOTED" else "BITSTREAM_PASS", final, artifacts=[str(artifact.relative_to(self.root))])
            result = {
                "contract_id": cid,
                "status": final,
                "generation": generation,
                "unit": unit,
                "matrix": matrix,
                "dependency": dependency,
                "rejected_candidates": rejected_candidates,
            }
            self.run_results.append(result)
            for name in ("shards", "shard-results", "oracle-build", "candidate-build", "generated"):
                path = artifact / name
                if path.is_dir() and name != "generated":
                    shutil.rmtree(path, ignore_errors=True)
            return result
        except (OSError, RuntimeError, ValueError, subprocess.SubprocessError) as error:
            self.update_state(cid, "DISCOVERED", "INFRASTRUCTURE_FAILURE", artifacts=[str(artifact.relative_to(self.root))], failure=str(error))
            result = {"contract_id": cid, "status": "INFRASTRUCTURE_FAILURE", "reason": str(error)}
            self.run_results.append(result)
            return result
    def write_cache_index(self) -> None:
        entries = self.cache.get("entries", {}) if isinstance(self.cache, dict) else {}
        if not isinstance(entries, dict):
            entries = {}
        for item in self.plan.get("contracts", []):
            result = next((value for value in self.run_results if value.get("contract_id") == item["contract_id"]), None)
            if not result:
                continue
            status = result.get("status")
            artifact = self.artifact_dir(item)
            valid = status in ("PROMOTED", "CACHE_REUSED") and (artifact / "unit-receipt.json").is_file() and (artifact / "bitstream-receipt.json").is_file()
            entries[item["cache_key"]] = {
                "schema_version": 2,
                "cache_key": item["cache_key"],
                "contract_id": item["contract_id"],
                "artifact_dir": str(artifact.relative_to(self.root)),
                "state": "PROMOTED" if valid else status,
                "valid": valid,
                "execution_status": "REUSED_VERIFIED_RECEIPT" if status == "CACHE_REUSED" else "EXECUTED_NOW",
                "model_calls": result.get("generation", {}).get("model_calls", 0),
                "tokens": result.get("generation", {}).get("tokens", 0),
                "hashes": item["hashes"],
                "updated_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
            }
        self.cache = {"schema_version": 2, "entries": entries}
        write_json(self.ci / "cache-index.json", self.cache)

    def refresh_dag(self) -> None:
        state_by_id = {item["contract_id"]: item for item in self.state.get("contracts", [])}
        for node in self.dag.get("nodes", []):
            item = state_by_id.get(node.get("contract_id"))
            if not item:
                continue
            current = item.get("current_state")
            stage = node.get("stage")
            if item.get("status") == "BLOCKED":
                node["status"] = "BLOCKED"
                node["failure_reason"] = item.get("failure_reason")
            elif stage == current:
                node["status"] = item.get("status")
                node["failure_reason"] = item.get("failure_reason")
            elif current in STATE_ORDER and stage in STATE_ORDER and STATE_ORDER.index(stage) < STATE_ORDER.index(current):
                node["status"] = "PASS"
            elif item.get("status") == "CACHE_REUSED":
                node["status"] = "CACHE_REUSED"
            else:
                node["status"] = "PENDING"
            node["artifacts"] = item.get("artifacts", [])
        pair = self.plan.get("dependency_pair")
        if pair:
            composition_id = f"{pair['caller_function']}:COMPOSITION"
            if not any(node.get("node_id") == composition_id for node in self.dag.get("nodes", [])):
                self.dag.setdefault("nodes", []).append({
                    "node_id": composition_id,
                    "contract_id": pair.get("caller_contract"),
                    "stage": "COMPOSITION",
                    "status": "EXECUTED" if any(item.get("dependency", {}).get("status") == "PASS" for item in self.run_results) else "PENDING",
                    "source_hash": self.input_facts.get("source_hash"),
                    "spec_hash": self.input_facts.get("spec_hash"),
                    "contract_hash": None,
                    "dependency_hash": digest(pair),
                    "artifacts": [],
                    "failure_reason": None,
                })
        write_json(self.ci / "dag.json", self.dag)

    def write_integration(self) -> None:
        replacement_lines = [
            "schema_version: 2",
            "rollback_mode: C_ONLY",
            "selected_contracts:",
        ]
        for cid in self.plan.get("selected_contracts", []):
            replacement_lines.append(f"  - {cid}")
        replacement_lines.extend([
            "promotion_gate: unit + dependency + shadow + rtl_return + bitstream",
            "source_policy: immutable upstream C; generated overlay lives in isolated copy",
        ])
        (self.integration / "replacement-plan.yaml").parent.mkdir(parents=True, exist_ok=True)
        (self.integration / "replacement-plan.yaml").write_text("\n".join(replacement_lines) + "\n", encoding="utf-8")
        for result in self.run_results:
            cid = result.get("contract_id")
            if not cid:
                continue
            overlay = result.get("matrix", {}).get("overlay")
            if overlay:
                directory = self.integration / "generated-overlay" / str(cid)
                write_json(directory / "overlay-receipt.json", overlay)
            matrix = result.get("matrix")
            if matrix:
                write_json(self.integration / "bitstream-receipts" / f"{cid}.json", matrix)

    def write_reports(self) -> None:
        self.artifacts.mkdir(parents=True, exist_ok=True)
        selected = self.plan.get("selected_contracts", [])
        result_lines = []
        for result in self.run_results:
            unit = result.get("unit", {})
            domain = unit.get("domain", {})
            promoted = next(
                (
                    candidate for candidate in unit.get("candidates", [])
                    if candidate.get("candidate") == unit.get("promoted_candidate")
                ),
                {},
            )
            dependency = result.get("dependency", {})
            matrix = result.get("matrix", {})
            result_lines.append({
                "contract_id": result.get("contract_id"),
                "status": result.get("status"),
                "execution_status": result.get("execution_status", "EXECUTED_NOW"),
                "model_calls": result.get("generation", {}).get("model_calls", 0),
                "tokens": result.get("generation", {}).get("tokens", 0),
                "unit_status": result.get("unit", {}).get("verification_status"),
                "dependency_status": result.get("dependency", {}).get("status"),
                "matrix_status": result.get("matrix", {}).get("status"),
                "matrix_modes": {
                    mode: matrix.get("modes", {}).get(mode, {}).get("status")
                    for mode in ("C_ONLY", "SHADOW", "RTL_RETURN")
                },
                "executed_shards": domain.get("shard_count", 0),
                "executed_vectors": domain.get("total_vectors", 0),
                "shard_durations_seconds": [
                    shard.get("duration_seconds")
                    for shard in promoted.get("shards", [])
                    if shard.get("duration_seconds") is not None
                ],
                "dependency_evidence": {
                    "call_sites": len(dependency.get("dependency_ports", [])),
                    "direct_call_sites": len(dependency.get("call_sites_from_callgraph", [])),
                    "compile_commands": bool(dependency.get("execution_evidence", {}).get("callee_oracle_compile")),
                    "matrix_commands": bool(dependency.get("execution_evidence", {}).get("caller_core_with_callee_c", {}).get("scenarios")),
                    "vectors": bool(dependency.get("execution_evidence", {}).get("vectors")),
                },
                "rejected_candidates": result.get("rejected_candidates", []),
                "counterexample": unit.get("smallest_counterexample"),
            })
        report = {
            "schema_version": 2,
            "agent": "executable-generic-c-to-rtl-cicd",
            "input_pdf": self.input_facts.get("spec_path"),
            "input_source_root": self.input_facts.get("source_root"),
            "selected_new_work": selected,
            "new_candidates": self.plan.get("new_candidates", []),
            "ready_contracts": self.plan.get("ready_contracts", []),
            "blocked_contracts": self.plan.get("blocked_contracts", []),
            "generator_invocations": self.generator_invocations,
            "model_calls": self.state.get("model_calls", 0),
            "tokens": self.state.get("token_count", 0),
            "shards": [
                result.get("unit", {}).get("domain", {}).get("shard_count")
                for result in self.run_results if result.get("unit")
            ],
            "dependency_pair": self.plan.get("dependency_pair"),
            "matrix_scripts_discovered": len(self.input_facts.get("baseline_scripts", [])),
            "results": result_lines,
            "blockers": self.input_facts.get("errors", []) + [
                item for blocked in self.plan.get("blocked_contracts", []) for item in blocked.get("reasons", [])
            ],
            "receipt_policy": {
                "fresh_run": "EXECUTED_NOW",
                "cache_hit": "REUSED_VERIFIED_RECEIPT",
                "complete_domain_pass": "EXHAUSTIVE_EQUIVALENT",
            },
        }
        write_json(self.root / "summary.json", report)
        lines = [
            "# Executable generic C-to-RTL pipeline",
            "",
            "This report is produced from the current run receipts. The PDF and immutable C model remain external inputs.",
            "",
            f"- PDF: {self.input_facts.get('spec_path')} ({self.input_facts.get('spec_hash')})",
            f"- C source root: {self.input_facts.get('source_root')} ({self.input_facts.get('source_hash')})",
            f"- selected new work: {', '.join(selected) or 'none'}",
            f"- generator invocations: {self.generator_invocations}",
            f"- model calls: {self.state.get('model_calls', 0)}",
            f"- token count: {self.state.get('token_count', 0)}",
            f"- dependency pair: {json.dumps(self.plan.get('dependency_pair'), sort_keys=True)}",
            f"- baseline scripts discovered: {len(self.input_facts.get('baseline_scripts', []))}",
            "",
            "## Results",
            "",
        ]
        for value in result_lines:
            lines.append(f"- {value['contract_id']}: {value['status']} ({value['execution_status']}); unit={value['unit_status']}; dependency={value['dependency_status']}; matrix={value['matrix_status']}")
            lines.append(
                f"  - executed vectors/shards: {value['executed_vectors']}/{value['executed_shards']}; "
                f"shard seconds: {value['shard_durations_seconds']}"
            )
            lines.append(f"  - matrix modes: {json.dumps(value['matrix_modes'], sort_keys=True)}")
            lines.append(f"  - dependency evidence: {json.dumps(value['dependency_evidence'], sort_keys=True)}")
            for rejected in value.get("rejected_candidates", []):
                lines.append(
                    f"  - rejected {rejected['candidate']}: unit={rejected['unit_gate']}; "
                    f"bitstream={rejected['bitstream_gate']}; receipt={rejected['receipt']}"
                )
        lines.extend(["", "## Blockers", ""])
        blockers = report["blockers"] or ["none"]
        lines.extend(f"- {value}" for value in blockers)
        (self.root / "reports" / "pipeline-summary.md").parent.mkdir(parents=True, exist_ok=True)
        (self.root / "reports" / "pipeline-summary.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
        write_json(self.integration / "pipeline-receipt.json", report)

    def run_command(self) -> int:
        self.load_inputs()
        self.materialize_new_contracts()
        self.dependency_graph()
        self.build_plan()
        self.write_plan_files()
        self.initialize_state()
        if not self.input_facts.get("errors"):
            for item in self.plan.get("contracts", []):
                self.run_contract(item)
        else:
            for item in self.state.get("contracts", []):
                if item.get("status") != "BLOCKED":
                    self.update_state(item["contract_id"], "DISCOVERED", "INFRASTRUCTURE_FAILURE", failure="; ".join(self.input_facts["errors"]))
        self.state["generator_invocations"] = self.generator_invocations
        self.state["model_calls"] = sum(int(item.get("model_calls", 0)) for item in self.state.get("contracts", []))
        self.state["token_count"] = sum(int(item.get("token_count", 0)) for item in self.state.get("contracts", []))
        self.write_cache_index()
        self.refresh_dag()
        self.write_integration()
        self.write_reports()
        self.write_state()
        successful = any(result.get("status") in ("PROMOTED", "CACHE_REUSED") for result in self.run_results)
        return 0 if successful else 1

    def status_command(self) -> int:
        payload = read_json(self.ci / "state.json", {}) or {}
        print(json.dumps({
            "selected_contracts": payload.get("selected_contracts", []),
            "generator_invocations": payload.get("generator_invocations", 0),
            "model_calls": payload.get("model_calls", 0),
            "contracts": [
                {
                    "contract_id": item.get("contract_id"),
                    "current_state": item.get("current_state"),
                    "status": item.get("status"),
                    "failure_reason": item.get("failure_reason"),
                }
                for item in payload.get("contracts", [])
            ],
        }, sort_keys=True))
        return 0 if payload else 1


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("command", choices=("plan", "run", "resume", "status"))
    parser.add_argument("--mode", choices=("plan", "run", "resume", "status"), default="run")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    agent = Agent(pathlib.Path(__file__).resolve().parents[1], args.command)
    if args.command == "plan":
        return agent.plan_command()
    if args.command in ("run", "resume"):
        return agent.run_command()
    return agent.status_command()


if __name__ == "__main__":
    raise SystemExit(main())
