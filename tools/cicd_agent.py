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
    "FORMAL_EQUIVALENT",
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
        # Contract-level batches can run concurrently.  Keep durable state and
        # generator telemetry serialized while allowing each contract to use
        # its own isolated artifact directory and Verilator build.
        self.state_lock = threading.RLock()
        # Promotion updates a shared designer library while contract jobs run
        # in parallel.  Keep the stable manifest and archive writes atomic at
        # the agent level without serializing generation or verification.
        self.library_lock = threading.RLock()

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

    def discover_inputs(self) -> dict[str, Any]:
        """Compatibility entry point for the tool-driven input discovery gate."""
        return self.load_inputs()

    def exact_links_by_usr(self) -> dict[str, list[dict[str, Any]]]:
        payload = read_json(self.root / "traceability" / "traceability.json", {}) or {}
        result: dict[str, list[dict[str, Any]]] = {}
        for link in payload.get("links", []):
            # A human-reviewed link is an exact authority only after the
            # traceability tool validated its PDF/source hashes.  Normalize
            # the status in this facts view so downstream contract matching
            # never depends on whether the link came from an MN comment or a
            # reviewed exact section reference.
            if link.get("status") not in {"EXACT", "REVIEWED"}:
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

    @staticmethod
    def reviewed_domain_admission(
        candidate: dict[str, Any],
        coverage: dict[str, Any],
        override: dict[str, Any] | None,
    ) -> dict[str, Any] | None:
        """Return a narrowly-scoped reviewed admission for a tool candidate.

        The candidate remains selected by generated Clang/coverage facts.  A
        reviewed override may discharge either one bounded-loop fact or one
        out-of-domain diagnostic effect.  It must carry a complete finite
        legal domain and exact PDF authority.  This is deliberately generic:
        no function name or source file is consulted here.
        """
        if not override or override.get("review_status") != "REVIEWED":
            return None
        criteria = candidate.get("criteria", {}) or {}
        failed = sorted(str(key) for key, value in criteria.items() if value is not True)
        allowed_failures = {
            "bounded_computation",
            "no_io_allocation_or_logging",
            "contributes_to_observable_output",
        }
        if not failed or any(item not in allowed_failures for item in failed):
            return None
        covered = coverage.get("covered") is True or (coverage.get("coverage", {}) or {}).get("covered") is True
        if coverage.get("coverage_status") != "EXECUTED" or not covered:
            return None
        interface = override.get("interface", {}) or {}
        inputs = interface.get("inputs", []) or []
        output = interface.get("output", {}) or {}
        if not inputs or not output or any(item.get("unresolved") for item in inputs):
            return None
        for item in inputs:
            domain = item.get("legal_domain", {}) or {}
            values = domain.get("values")
            bounds = domain.get("range")
            if not (isinstance(values, list) and values) and not (
                isinstance(bounds, list) and len(bounds) == 2 and all(isinstance(value, int) for value in bounds)
            ):
                return None
        if output.get("unresolved"):
            return None
        output_domain = output.get("legal_domain", {}) or {}
        output_values = output.get("legal_values") or output.get("values") or output_domain.get("values")
        output_bounds = output.get("legal_range") or output.get("range") or output_domain.get("range")
        if not (isinstance(output_values, list) and output_values) and not (
            isinstance(output_bounds, list)
            and len(output_bounds) == 2
            and all(isinstance(value, int) for value in output_bounds)
        ):
            return None
        raw_proofs = override.get("tool_admissions")
        if raw_proofs is None:
            raw_proofs = [override.get("tool_admission", {}) or {}]
        if not isinstance(raw_proofs, list) or len(raw_proofs) != len(failed):
            return None
        proofs = [copy.deepcopy(item) for item in raw_proofs if isinstance(item, dict)]
        if len(proofs) != len(raw_proofs) or any(item.get("status") != "PASS" for item in proofs):
            return None

        expected_kinds = {
            "bounded_computation": "BOUNDED_DOMAIN",
            "no_io_allocation_or_logging": "DOMAIN_EFFECT",
            "contributes_to_observable_output": "CONFIG_LIBRARY",
        }
        if sorted(str(item.get("kind")) for item in proofs) != sorted(expected_kinds[item] for item in failed):
            return None
        by_kind = {str(item.get("kind")): item for item in proofs}
        bounded = by_kind.get("BOUNDED_DOMAIN")
        if bounded is not None and (
            not bounded.get("loop")
            or not isinstance(bounded.get("max_iterations"), int)
            or bounded.get("max_iterations") <= 0
        ):
            return None
        domain_effect = by_kind.get("DOMAIN_EFFECT")
        if domain_effect is not None:
            discharged = sorted(str(item) for item in domain_effect.get("discharged_effects", []))
            if discharged != ["logging"] or not domain_effect.get("unreachable_condition"):
                return None
        config = by_kind.get("CONFIG_LIBRARY")
        if config is not None:
            # A CONFIG_LIBRARY is deliberately outside the production-output
            # DUT set. It is valid only when output contribution is the sole
            # failed criterion; it cannot be combined with any other waiver.
            if len(failed) != 1 or config.get("role") != "CONFIG_HELPER" or not config.get("non_dut_boundary"):
                return None
        spec_links = override.get("spec_links", []) or []
        if not spec_links or not all(link.get("status") == "EXACT" for link in spec_links):
            return None
        if len(proofs) == 1:
            return proofs[0]
        discharged_effects = sorted({
            str(effect)
            for proof in proofs
            for effect in proof.get("discharged_effects", [])
        })
        return {
            "kind": "COMBINED_DOMAIN",
            "status": "PASS",
            "criteria_discharged": failed,
            "admissions": proofs,
            "discharged_effects": discharged_effects,
            "bounded_loops": [
                {
                    "loop": proof.get("loop"),
                    "max_iterations": proof.get("max_iterations"),
                }
                for proof in proofs
                if proof.get("kind") == "BOUNDED_DOMAIN"
            ],
        }

    @staticmethod
    def reviewed_bounded_domain_admission(
        candidate: dict[str, Any],
        coverage: dict[str, Any],
        override: dict[str, Any] | None,
    ) -> bool:
        """Compatibility predicate for the bounded-domain unit tests."""
        admission = Agent.reviewed_domain_admission(candidate, coverage, override)
        return bool(
            admission
            and (
                admission.get("kind") == "BOUNDED_DOMAIN"
                or any(
                    item.get("kind") == "BOUNDED_DOMAIN"
                    for item in admission.get("admissions", [])
                    if isinstance(item, dict)
                )
            )
        )

    def reviewed_overrides(self) -> list[dict[str, Any]]:
        payload = read_json(self.root / "contracts" / "reviewed-overrides.json", {}) or {}
        return [item for item in payload.get("overrides", []) if item.get("match")]

    def promoted_contract_usrs(self, contracts: list[dict[str, Any]]) -> set[str]:
        """Return facts identities whose RTL is already in the stable library.

        Composite candidates are allowed to materialize only after every direct
        callee has a PASS library entry.  This keeps the dependency boundary
        data-driven while preventing an unproven C call chain from becoming a
        generation target merely because a reviewed override exists.
        """
        manifest = read_json(self.root / "library" / "manifest.json", {}) or {}
        promoted_ids = {
            str(item.get("contract_id"))
            for item in manifest.get("components", [])
            if item.get("status") == "PASS" and item.get("contract_id")
        }
        promoted_usrs = {
            str(contract_function(contract).get("clang_usr"))
            for contract in contracts
            if contract_id(contract) in promoted_ids and contract_function(contract).get("clang_usr")
        }
        # Promoted composites are intentionally not copied into contracts/locked;
        # their durable identity lives in the library manifest.  Resolve the
        # manifest function name back through tool facts so a newly promoted
        # dynamic contract can unlock the next tool-discovered composite.
        facts = read_json(self.root / "facts" / "functions.json", {}) or {}
        facts_by_name = {
            str(item.get("name")): str(item.get("clang_usr"))
            for item in facts.get("functions", [])
            if item.get("name") and item.get("clang_usr")
        }
        for item in manifest.get("components", []):
            if item.get("status") != "PASS":
                continue
            if item.get("clang_usr"):
                promoted_usrs.add(str(item["clang_usr"]))
            function_name = str(item.get("function") or "")
            if function_name in facts_by_name:
                promoted_usrs.add(facts_by_name[function_name])
        return promoted_usrs

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
        overrides = self.reviewed_overrides()
        exact = self.exact_links_by_usr()
        result: dict[str, dict[str, Any]] = {}
        for rank, candidate in enumerate(candidates_payload.get("ranked_candidates", []), start=1):
            usr = str(candidate.get("clang_usr", ""))
            coverage = coverage_by_usr.get(usr, {})
            if not usr:
                continue
            domain_override = None
            domain_admission = None
            for item in overrides:
                if (
                    item.get("review_status") == "REVIEWED"
                    and self.reviewed_override_matches(
                        {"function": {"clang_usr": usr}}, item, exact
                    )
                    and item.get("interface")
                    and item.get("semantics")
                ):
                    admission = self.reviewed_domain_admission(candidate, coverage, item)
                    if admission:
                        domain_override = item
                        domain_admission = admission
                        break
            if candidate.get("eligible") is not True and domain_override is None:
                continue
            coverage_override = next(
                (
                    item for item in overrides
                    if item.get("review_status") == "REVIEWED"
                    and self.reviewed_override_matches(
                        {"function": {"clang_usr": usr}}, item, exact
                    )
                    and str((item.get("coverage") or {}).get("status", ""))
                    == "STATIC_BUT_UNCOVERED"
                    and item.get("interface")
                    and item.get("semantics")
                ),
                None,
            )
            dynamically_eligible = coverage.get("eligible_after_coverage") is True
            reviewed_static_eligible = bool(
                coverage_override
                and coverage.get("static_eligible") is True
                and coverage.get("coverage_status") in {"STATIC_BUT_UNCOVERED", "NO_COVERAGE_DATA"}
            )
            if not dynamically_eligible and not reviewed_static_eligible:
                if domain_override is None:
                    continue
            result[usr] = {
                "rank": rank,
                "score": candidate.get("score"),
                "candidate": copy.deepcopy(candidate),
                "coverage": copy.deepcopy(coverage),
                "coverage_override": copy.deepcopy(coverage_override) if coverage_override else None,
                "domain_admission": copy.deepcopy(domain_admission) if domain_admission else None,
                "coverage_basis": (
                    "reviewed_bounded_domain"
                    if domain_admission and domain_admission.get("kind") == "BOUNDED_DOMAIN"
                    and candidate.get("eligible") is not True
                    else "reviewed_domain_effect"
                    if domain_admission and candidate.get("eligible") is not True
                    and domain_admission.get("kind") == "DOMAIN_EFFECT"
                    else "reviewed_config_library"
                    if domain_admission and candidate.get("eligible") is not True
                    and domain_admission.get("kind") == "CONFIG_LIBRARY"
                    else "reviewed_combined_domain"
                    if domain_admission and candidate.get("eligible") is not True
                    and domain_admission.get("kind") == "COMBINED_DOMAIN"
                    else "reviewed_static_but_uncovered"
                    if reviewed_static_eligible
                    else "dynamic_execution"
                ),
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
        port_names: set[str] = set()

        def add_port(port: dict[str, Any]) -> None:
            name = str(port.get("name", ""))
            if name in port_names:
                return
            port_names.add(name)
            ports.append(port)

        for item in interface.get("inputs", []):
            add_port({
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
            add_port({
                "name": safe_identifier(port_name),
                "role": str(item.get("role") or item.get("field") or port_name),
                "direction": "input",
                "width": int(item.get("logical_width") or 32),
                "signed": bool(item.get("signed", False)),
                "c_type": item.get("c_type", "int"),
                "legal_domain": item.get("legal_domain", {}),
            })
        output = interface.get("output", {}) or {}
        add_port({
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
        promoted_usrs = self.promoted_contract_usrs(effective_locked)
        source_usrs = {
            str(item.get("clang_usr"))
            for item in facts.get("functions", [])
            if item.get("clang_usr")
        }
        target_contract = safe_identifier(os.environ.get("DSC_CICD_TARGET_CONTRACT", "")).lower()
        refresh_stable = os.environ.get("DSC_CICD_REFRESH_STABLE", "").lower() in {"1", "true", "yes"}
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
            callee_usrs = {
                str(item.get("clang_usr"))
                for item in function.get("callees", [])
                if isinstance(item, dict)
                and item.get("clang_usr")
                and str(item.get("clang_usr")) in source_usrs
            }
            # A reviewed override supplies semantics/domain evidence only.  A
            # composite is eligible when tool facts selected it and every
            # direct callee is already a PASS component in library/manifest.
            # The callee gate is intentionally not a function-name selector.
            dependencies_ready = callee_usrs.issubset(promoted_usrs)
            admission = (candidate.get("domain_admission") or {}) if candidate else {}
            admission_allows_combinational = (
                admission.get("kind") == "DOMAIN_EFFECT"
                and sorted(str(item) for item in admission.get("discharged_effects", [])) == ["logging"]
            )
            if admission.get("kind") == "COMBINED_DOMAIN":
                combined_kinds = {
                    str(item.get("kind"))
                    for item in admission.get("admissions", [])
                    if isinstance(item, dict)
                }
                admission_allows_combinational = (
                    combined_kinds.issubset({"BOUNDED_DOMAIN", "DOMAIN_EFFECT"})
                    and "BOUNDED_DOMAIN" in combined_kinds
                    and "DOMAIN_EFFECT" in combined_kinds
                    and sorted(str(item) for item in admission.get("discharged_effects", [])) == ["logging"]
                )
            if (not usr or not candidate or usr in known or not override or not reviewed_links
                    or not (proposal.get("combinational_candidate") or admission_allows_combinational)
                    or not dependencies_ready):
                continue
            interface = copy.deepcopy(override.get("interface", {}))
            interface["ports"] = self.freeze_ports(interface)
            name = str(function.get("name", "candidate"))
            cid = safe_identifier(name).lower()
            # A promoted composite is not new work.  It is materialized only
            # when the durable queue explicitly asks for that contract (for a
            # refresh or a dependency composition run); ordinary planning must
            # not regenerate the stable library forever.
            promoted_existing = usr in promoted_usrs
            if promoted_existing and cid != target_contract and not refresh_stable:
                continue
            targeted_refresh = cid == target_contract
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
                    "promotion_gate": "all direct callees PASS in library/manifest.json" if callee_usrs else None,
                },
                "spec_links": copy.deepcopy(override.get("spec_links", reviewed_links)),
                "reviewed_evidence": override.get("evidence", []),
                "selection": {
                    "new_work": (not promoted_existing) or targeted_refresh,
                    "basis": "tool-ranked candidate and coverage facts + exact traceability + reviewed domain evidence",
                    "candidate_rank": candidate.get("rank"),
                    "candidate_score": candidate.get("score"),
                    "fact_source": "facts/functions.json",
                    "candidate_source": "facts/candidates.json",
                    "coverage_source": "coverage/coverage.json",
                    "coverage_basis": candidate.get("coverage_basis"),
                    "domain_admission": copy.deepcopy(candidate.get("domain_admission")),
                    "promoted_existing": promoted_existing,
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
        manifest = read_json(self.root / "library" / "manifest.json", {}) or {}
        stable_ids = {
            str(value.get("contract_id"))
            for value in manifest.get("components", [])
            if value.get("status") == "PASS" and value.get("contract_id")
        }
        refresh_stable = os.environ.get("DSC_CICD_REFRESH_STABLE", "").lower() in {"1", "true", "yes"}
        force_regenerate = (
            os.environ.get("DSC_CICD_FORCE_REGENERATE", "").lower() in {"1", "true", "yes"}
            or refresh_stable
        )
        prior_shapes = {str(item.get("contract_id")): item.get("interface_shape", []) for item in self.previous_state.get("contracts", []) if item.get("current_state") == "PROMOTED"}
        for contract in sorted(self.contracts, key=contract_id):
            if not contract.get("interface", {}).get("ports"):
                contract.setdefault("interface", {})["ports"] = self.freeze_ports(contract.get("interface", {}))
            cid = contract_id(contract)
            key, hashes = self.cache_key(contract)
            is_ready, reasons = self.ready(contract)
            entry = self.cache_entry(key)
            stale = [name for name, value in hashes.items() if self.prior_contract(cid).get("hashes", {}).get(name) not in (None, value)]
            cache_hit = self.cache_valid(entry, key) and not force_regenerate
            item = {
                "contract_id": cid,
                "function": contract_function(contract).get("name"),
                "clang_usr": contract_function(contract).get("clang_usr"),
                "origin": contract.get("origin", "locked_contract"),
                "new_work": bool(
                    (contract.get("selection") or {}).get(
                        "new_work", cid in discovered and cid not in stable_ids
                    )
                ),
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
        if target_item and target_item["ready"]:
            # The queue supplies a discovered contract id for this independent
            # batch. It is not a source-level function allowlist. A refresh can
            # deliberately rerun a verified leaf to search for a better pass.
            selected = [target_item["contract_id"]]
        elif refresh_stable:
            # A scale refresh rechecks the current reviewed stable frontier. The
            # manifest contributes only promotion state; the actual contracts
            # still come from the current tool/spec-ready plan. This is routing
            # metadata, not a source-level function selector.
            selected = [
                item["contract_id"]
                for item in entries
                if item["ready"] and (item["contract_id"] in stable_ids or item["new_work"])
            ]
            selected = sorted(selected[:max(1, int(os.environ.get("DSC_CICD_MAX_NEW", "1")))])
        else:
            selected = [item["contract_id"] for item in entries if item["ready"] and item["new_work"] and (not prior_shapes or item["interface_shape"] not in prior_shapes.values())]
            if not selected:
                selected = [
                    item["contract_id"]
                    for item in entries
                    if item["ready"] and not item["cache_hit"] and item["contract_id"] not in stable_ids
                ][:1]
            selected = sorted(selected[:max(1, int(os.environ.get("DSC_CICD_MAX_NEW", "1")))])
        for item in entries:
            item["selected"] = item["contract_id"] in selected
            item["deferred"] = bool(item["ready"] and not item["selected"])
            item["targeted"] = item["contract_id"] == (target_item or {}).get("contract_id")
            item["force_regenerate"] = force_regenerate and item["selected"]
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
            "refresh_stable": refresh_stable,
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
        with self.state_lock:
            write_json(self.ci / "state.json", self.state)

    def state_item(self, cid: str) -> dict[str, Any]:
        return next(item for item in self.state.get("contracts", []) if item.get("contract_id") == cid)

    def update_state(self, cid: str, state_name: str, status: str, artifacts: Iterable[str] = (), failure: str | None = None, extra: dict[str, Any] | None = None) -> None:
        with self.state_lock:
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

    def append_result(self, result: dict[str, Any]) -> None:
        with self.state_lock:
            self.run_results.append(result)

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

    def promote_library_component(
        self,
        contract: dict[str, Any],
        item: dict[str, Any],
        artifact: pathlib.Path,
        result: dict[str, Any],
    ) -> dict[str, Any]:
        """Materialize one fully verified leaf into the stable RTL library.

        The C oracle and receipts are the authority for a promotion.  This
        method only runs after the unit, dependency, shadow, RTL_RETURN, and
        frame gates pass; it rechecks exact links and the RTL boundary before
        writing.  A lock protects the shared manifest while independent
        contract jobs retain parallel generation and verification.
        """
        cid = contract_id(contract)
        if result.get("status") not in {"PROMOTED", "CACHE_REUSED"}:
            raise RuntimeError(f"library promotion requires PROMOTED result: {cid}")
        if not contract_exact_links(contract):
            raise RuntimeError(f"library promotion requires exact PDF links: {cid}")
        unit = result.get("unit", {}) or {}
        matrix = result.get("matrix", {}) or {}
        dependency = result.get("dependency", {}) or {}
        if not unit.get("promoted_candidate"):
            raise RuntimeError(f"library promotion missing accepted candidate: {cid}")
        if dependency.get("status") != "PASS" or matrix.get("status") != "PASS":
            raise RuntimeError(f"library promotion gates are not PASS: {cid}")
        required_modes = ("C_ONLY", "SHADOW", "RTL_RETURN")
        if any((matrix.get("modes", {}).get(mode, {}) or {}).get("status") != "PASS" for mode in required_modes):
            raise RuntimeError(f"library promotion matrix modes are not PASS: {cid}")
        candidate_name = str(unit["promoted_candidate"])
        candidate_path = artifact / "generated" / f"{candidate_name}.sv"
        if not candidate_path.is_file():
            raise RuntimeError(f"library promotion candidate missing: {candidate_path}")
        source = candidate_path.read_text(encoding="utf-8", errors="replace")
        scrubbed = re.sub(r"//.*|/\*.*?\*/", "", source, flags=re.S)
        modules = list(re.finditer(r"\bmodule\s+([A-Za-z_][A-Za-z0-9_]*)", scrubbed))
        if len(modules) != 1 or len(re.findall(r"\bendmodule\b", scrubbed)) != 1:
            raise RuntimeError(f"library promotion requires one RTL module: {cid}")
        ports = self.freeze_ports(contract.get("interface", {}) or {})
        rtl_blockers = self.validate_rtl(source, ports)
        if rtl_blockers:
            raise RuntimeError(f"library promotion RTL boundary failed for {cid}: {rtl_blockers}")
        module_name = safe_identifier(cid).lower()
        match = re.search(r"\bmodule\s+([A-Za-z_][A-Za-z0-9_]*)", source)
        if not match:
            raise RuntimeError(f"library promotion module name missing: {cid}")
        canonical_source = source[:match.start(1)] + module_name + source[match.end(1):]
        if not canonical_source.endswith("\n"):
            canonical_source += "\n"
        canonical_bytes = canonical_source.encode("utf-8")
        rtl_sha256 = hashlib.sha256(canonical_bytes).hexdigest()
        contract_hash = str(item.get("contract_hash") or artifact.name)
        artifact_relative = str(artifact.relative_to(self.root))
        promoted_at = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
        library = self.root / "library"
        rtl_root = library / "rtl"
        verification_root = library / "verification"
        contract_root = library / "contracts"
        archive_root = library / "archive" / safe_identifier(cid).lower()
        with self.library_lock:
            for directory in (rtl_root, verification_root, contract_root, archive_root):
                directory.mkdir(parents=True, exist_ok=True)
            destination = rtl_root / f"{safe_identifier(cid).lower()}.sv"
            archived = None
            if destination.is_file():
                old_hash = file_hash(destination)
                if old_hash != rtl_sha256:
                    archive_path = archive_root / f"{artifact.name}.sv"
                    if not archive_path.exists():
                        archive_path.write_bytes(destination.read_bytes())
                    archived = str(archive_path.relative_to(library))
            destination.write_bytes(canonical_bytes)

            formal_candidate = next(
                (
                    candidate for candidate in unit.get("candidates", [])
                    if candidate.get("candidate") == candidate_name
                ),
                {},
            )
            formal = formal_candidate.get("formal_proof", {}) or {}
            formal_receipt = read_json(artifact / str(formal.get("receipt", "")), {}) or {}
            source_gate = {
                "status": "PASS",
                "pdf_sha256": self.input_facts.get("spec_hash"),
                "source_sha256": self.input_facts.get("source_hash"),
                "baseline_sha256": self.input_facts.get("baseline_hash"),
            }
            verification_path = verification_root / f"{safe_identifier(cid).lower()}.json"
            prior_verification = read_json(verification_path, {}) or {}
            verification = {
                "schema_version": 2,
                "contract_id": cid,
                "function": contract_function(contract).get("name"),
                "kind": (contract.get("semantics", {}) or {}).get("kind"),
                "status": "PASS",
                "execution_status": result.get("execution_status", "EXECUTED_NOW"),
                "candidate": candidate_name,
                "module": module_name,
                "rtl_sha256": rtl_sha256,
                "contract_hash": contract_hash,
                "artifact_dir": artifact_relative,
                "source_gate": source_gate,
                "traceability": {
                    "authority": "EXACT_SPEC",
                    "review_status": "REVIEWED",
                    "source_file": contract_function(contract).get("source_file"),
                    "c_span": contract_function(contract).get("source_span"),
                    "spec_links": contract_exact_links(contract),
                },
                "stages": {
                    "generator": (result.get("generation", {}) or {}).get("status", "PASS"),
                    "verilator_lint_build": "PASS",
                    "unit_equivalence": unit.get("verification_status"),
                    "formal": formal.get("status", "NOT_APPLICABLE"),
                    "formal_rtl_equivalence": formal.get("status", "NOT_APPLICABLE"),
                    "formal_partitions": formal_receipt.get("partition_count"),
                    "shards_mutations": "PASS" if unit.get("promoted_candidate") else "FAIL",
                    "width_spec_gate": "PASS",
                    "dependency_composition": dependency.get("status"),
                    "model_matrix": matrix.get("status"),
                    "frame_compare": matrix.get("status"),
                },
                "unit_vectors": (unit.get("domain", {}) or {}).get("total_vectors", 0),
                "formal_proof": formal,
                "formal_partitions": formal_receipt.get("partition_count"),
                "dependency": {
                    "status": dependency.get("status"),
                    "call_sites": len(dependency.get("call_sites_from_callgraph", [])),
                    "dependency_ports": len(dependency.get("dependency_ports", [])),
                    "vectors": (dependency.get("execution_evidence", {}) or {}).get("vectors", {}).get("total_vectors", 0),
                },
                "matrix": {
                    "status": matrix.get("status"),
                    "modes": {
                        mode: (matrix.get("modes", {}).get(mode, {}) or {}).get("status")
                        for mode in ("C_ONLY", "SHADOW", "RTL_RETURN")
                    },
                    "scripts_discovered": matrix.get("matrix_scripts_discovered"),
                },
                "promoted_at": promoted_at,
            }
            # Preserve reviewed window metadata only when it still describes
            # the exact same canonical RTL bytes; never carry stale proof data
            # across a changed candidate.
            if prior_verification.get("rtl_sha256") == rtl_sha256:
                for key in ("profile", "window", "formal_partitions"):
                    if key in prior_verification and not verification.get(key):
                        verification[key] = prior_verification[key]
            write_json(verification_path, verification)

            contract_path = contract_root / f"{safe_identifier(cid).lower()}.json"
            library_contract = copy.deepcopy(contract)
            library_contract["do_not_edit"] = True
            library_contract["library_promotion"] = {
                "status": "PASS",
                "artifact_dir": artifact_relative,
                "module": module_name,
                "rtl_sha256": rtl_sha256,
                "promoted_at": promoted_at,
            }
            write_json(contract_path, library_contract)

            manifest = read_json(library / "manifest.json", {}) or {}
            components = {
                str(value.get("contract_id")): value
                for value in manifest.get("components", [])
                if value.get("contract_id")
            }
            function = contract_function(contract)
            components[cid] = {
                "contract_id": cid,
                "function": function.get("name"),
                "module": module_name,
                "module_file": str(destination.relative_to(library)),
                "module_sha256": rtl_sha256,
                "verification_file": str(verification_path.relative_to(library)),
                "contract_file": str(contract_path.relative_to(library)),
                "contract_hash": contract_hash,
                "source_file": function.get("source_file"),
                "c_span": function.get("source_span"),
                "spec_links": contract_exact_links(contract),
                "authority": "EXACT_SPEC",
                "boundary": "verified combinational leaf; C_ONLY remains rollback/reference",
                "artifact_dir": artifact_relative,
                "status": "PASS",
                "promoted_at": promoted_at,
            }
            manifest.update({
                "schema_version": max(2, int(manifest.get("schema_version", 1))),
                "library": manifest.get("library", "dsc-verilog-library"),
                "policy": manifest.get("policy", "Only spec-traceable PASS leaf RTL is canonical; stateful callers remain C until separately contracted and verified."),
                "source_policy": manifest.get("source_policy", "immutable external C model and local DSC 1.2a PDF; no SVRT"),
                "spec_hash": self.input_facts.get("spec_hash") or manifest.get("spec_hash"),
                "source_hash": self.input_facts.get("source_hash") or manifest.get("source_hash"),
                "updated_at": promoted_at,
                "components": sorted(components.values(), key=lambda value: str(value.get("contract_id"))),
            })
            write_json(library / "manifest.json", manifest)
        return {
            "status": "PASS",
            "contract_id": cid,
            "module": module_name,
            "module_file": str(destination.relative_to(self.root)),
            "verification_file": str(verification_path.relative_to(self.root)),
            "contract_file": str(contract_path.relative_to(self.root)),
            "artifact_dir": artifact_relative,
            "rtl_sha256": rtl_sha256,
            "contract_hash": contract_hash,
            "archived_previous": archived,
        }

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
        record_parameters: dict[str, str] = {}
        for parameter in parameters:
            if not parameter.get("pointer"):
                continue
            parameter_name = str(parameter.get("name", ""))
            record_type = re.sub(r"\s*\*.*$", "", str(parameter.get("type", ""))).strip()
            if parameter_name and record_type:
                record_parameters[record_type] = parameter_name
        declarations: list[str] = []
        call_arguments: list[str] = []
        local_setup: list[str] = []
        local_dependencies: list[str] = []
        state_setup: list[str] = []
        known_ports = {str(port.get("name")) for port in inputs}

        def resolve_index(raw_index: object) -> str:
            raw = str(raw_index)
            if re.fullmatch(r"-?\d+", raw):
                return raw
            if raw in known_ports:
                return raw
            normalized_raw = re.sub(r"[^a-z0-9]", "", raw.lower())
            for port in inputs:
                for candidate in (port.get("name"), port.get("role")):
                    if re.sub(r"[^a-z0-9]", "", str(candidate).lower()) == normalized_raw:
                        return str(port.get("name"))
            raise RuntimeError(f"dynamic array index is not an input port or literal: {raw}")

        # A pointer-array contract may freeze both pointer-array taps and
        # selected fields of a pointed-to state record.  Keep the adapter
        # data-driven: the contract supplies the field/index binding and the
        # original Clang facts supply the record parameter.
        for item in flattened:
            record_type = str(item.get("record", ""))
            field = str(item.get("field", ""))
            if not record_type or not field:
                continue
            state_name = record_parameters.get(record_type)
            if not state_name or not re.match(r"^[A-Za-z_][A-Za-z0-9_]*$", field):
                raise RuntimeError(f"missing state record binding for flattened field: {field}")
            port_name = safe_identifier(str(item.get("port_name") or field))
            if port_name not in known_ports:
                raise RuntimeError(f"flattened state field is not an input port: {port_name}")
            indices: list[object] = []
            if item.get("index_names") is not None:
                raw_indices = item.get("index_names")
                if not isinstance(raw_indices, list) or not raw_indices:
                    raise RuntimeError(f"invalid index_names for flattened field: {field}")
                indices.extend(raw_indices)
            elif item.get("index_name") is not None:
                indices.append(item.get("index_name"))
            elif item.get("index") is not None:
                indices.append(item.get("index"))
            if not indices and "[" in str(item.get("c_type", "")):
                raise RuntimeError(f"array state field requires a frozen index: {field}")
            lhs = f"{state_name}.{field}"
            for index in indices:
                lhs += f"[{resolve_index(index)}]"
            state_setup.append(f"{lhs} = {port_name};")
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
        include_types = bool(record_parameters) or any("_t" in str(item.get("c_type", "")) for item in ignored)
        setup = "\n                        ".join(local_setup + state_setup)
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
        dynamic_window = ((contract.get("semantics", {}) or {}).get("window_spec", {}) or {}).get(
            "dynamic_line_window"
        )
        if (contract.get("semantics", {}) or {}).get("kind") == "flatness_window":
            return self.render_flatness_window_oracle(contract, inputs, output)
        if (contract.get("semantics", {}) or {}).get("kind") == "ich_decision":
            return self.render_ich_decision_oracle(contract, inputs, output)
        if isinstance(dynamic_window, dict) and dynamic_window:
            return self.render_dynamic_window_oracle(
                contract,
                inputs,
                output,
                dynamic_window,
            )
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
            storage_declarations: list[str] = []
            storage_names: set[str] = set()
            input_names = {str(value.get("name")) for value in inputs}

            def resolve_input_index(raw_index: object) -> str:
                raw = str(raw_index)
                if re.fullmatch(r"-?\d+", raw):
                    return raw
                safe_raw = safe_identifier(raw)
                if safe_raw in input_names:
                    return safe_raw
                normalized_raw = re.sub(r"[^a-z0-9]", "", raw.lower())
                for value in inputs:
                    for candidate in (value.get("name"), value.get("role")):
                        if re.sub(r"[^a-z0-9]", "", str(candidate).lower()) == normalized_raw:
                            return str(value.get("name"))
                raise RuntimeError(f"dynamic array index is not an input port: {safe_raw}")

            for item in flattened:
                field = str(item.get("field", ""))
                port_name = safe_identifier(str(item.get("port_name") or field))
                port = next((value for value in inputs if value.get("name") == port_name), None)
                if not field or port is None or not re.match(r"^[A-Za-z_][A-Za-z0-9_]*$", field):
                    raise RuntimeError(f"flattened state dependency is not a scalar port: {field}")
                record_type = str(item.get("record", ""))
                state_name = record_names.get(record_type)
                if not state_name:
                    raise RuntimeError(f"missing record parameter for: {record_type}")
                c_type = str(item.get("c_type", port.get("c_type", "int")))
                if item.get("index_names") is not None:
                    raw_indices = item.get("index_names")
                    if not isinstance(raw_indices, list) or not raw_indices:
                        raise RuntimeError(f"invalid nested array indices for: {field}")
                    lhs = f"{state_name}.{field}"
                    for raw_index in raw_indices:
                        lhs += f"[{resolve_input_index(raw_index)}]"
                    assignments.append(f"{lhs} = {port_name};")
                elif "*" in c_type and item.get("index_name"):
                    index_name = resolve_input_index(item.get("index_name"))
                    array_length = int(item.get("array_length", 32))
                    storage_name = f"{safe_identifier(field)}_oracle_storage"
                    if storage_name not in storage_names:
                        storage_declarations.append(f"int {storage_name}[{array_length}] = {{0}};")
                        storage_names.add(storage_name)
                    assignments.append(f"{storage_name}[{index_name}] = {port_name};")
                    assignments.append(f"{state_name}.{field} = {storage_name};")
                elif "*" in c_type and "[" not in c_type:
                    raise RuntimeError(f"flattened pointer table is not a scalar port: {field}")
                elif "[" in c_type and "]" in c_type and item.get("index_name"):
                    index_name = resolve_input_index(item.get("index_name"))
                    assignments.append(f"{state_name}.{field}[{index_name}] = {port_name};")
                elif "[" in c_type and "]" in c_type:
                    if item.get("index") is not None:
                        assignments.append(f"{state_name}.{field}[{int(item.get('index'))}] = {port_name};")
                    else:
                        assignments.append(
                            f"for (size_t i = 0; i < sizeof({state_name}.{field}) / sizeof({state_name}.{field}[0]); ++i) "
                            f"{state_name}.{field}[i] = {port_name};"
                        )
                elif "*" not in c_type or not item.get("index_name"):
                    assignments.append(f"{state_name}.{field} = {port_name};")
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
            if storage_declarations:
                record_declarations += "\n                        " + "\n                        ".join(storage_declarations)
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

    def render_flatness_window_oracle(
        self,
        contract: dict[str, Any],
        inputs: list[dict[str, Any]],
        output: str,
    ) -> str:
        """Render an oracle for a reviewed original-pixel flatness window.

        The immutable C function keeps its native ``dsc_cfg_t`` and
        ``dsc_state_t`` parameters.  This adapter initializes only the
        read-only configuration/state fields named by the contract, selects
        the immutable Table 6-2 rows, and places the seven relative original
        pixel taps into the model's padded line storage.  No line storage or
        caller state is moved into the generated RTL.
        """
        function = contract_function(contract)
        name = str(function.get("name"))
        parameters = self.function_parameters(contract)
        if not parameters:
            raise RuntimeError("flatness-window oracle requires original C parameter facts")

        semantics = contract.get("semantics", {}) or {}
        bindings = semantics.get("bindings", {}) or {}
        window = semantics.get("window_spec", {}) or {}
        input_names = {str(port.get("name")) for port in inputs}

        def binding(key: str, fallback: str) -> str:
            value = bindings.get(key, fallback)
            if value not in input_names:
                raise RuntimeError(f"flatness-window binding is not an input port: {value}")
            return str(value)

        hpos_name = binding("hpos_port", "hPos")
        bpc_name = binding("bits_per_component_port", "bits_per_component")
        primary_qp_name = binding("primary_qp_port", "primary_qp")
        num_components_name = binding("num_components_port", "num_components")
        slice_width_name = binding("slice_width_port", "slice_width")
        flatness_thresh_name = binding("flatness_det_thresh_port", "flatness_det_thresh")
        flatness_delta_name = binding("somewhat_flat_qp_delta_port", "somewhat_flat_qp_delta")
        native420_name = binding("native_420_port", "native_420")
        version_name = binding("dsc_version_minor_port", "dsc_version_minor")
        cpnt0_name = binding("cpnt_bit_depth_0_port", "cpnt_bit_depth_0")
        cpnt1_name = binding("cpnt_bit_depth_1_port", "cpnt_bit_depth_1")

        sample_ports_by_component = window.get("sample_ports_by_component", {})
        if not isinstance(sample_ports_by_component, dict):
            raise RuntimeError("flatness-window oracle is missing sample_ports_by_component")
        sample_names: dict[int, list[str]] = {}
        for component in range(4):
            raw = sample_ports_by_component.get(str(component), sample_ports_by_component.get(component, []))
            values = [str(value) for value in raw]
            if len(values) != 7 or any(value not in input_names for value in values):
                raise RuntimeError(f"flatness-window oracle has incomplete component {component} taps")
            sample_names[component] = values

        record_parameters: dict[str, str] = {}
        parameter_declarations: list[str] = []
        call_arguments: list[str] = []
        for parameter in parameters:
            parameter_name = str(parameter.get("name", ""))
            parameter_type = str(parameter.get("type", "int")).strip()
            if not parameter_name or not re.match(r"^[A-Za-z_][A-Za-z0-9_]*$", parameter_name):
                raise RuntimeError(f"invalid C parameter name: {parameter_name}")
            parameter_declarations.append(f"{parameter_type} {parameter_name}")
            if parameter.get("pointer"):
                record_type = re.sub(r"\s*\*.*$", "", parameter_type).strip()
                record_parameters[record_type] = parameter_name
                call_arguments.append(f"&{parameter_name}")
            else:
                if parameter_name not in input_names:
                    raise RuntimeError(f"flatness-window scalar parameter is not an input port: {parameter_name}")
                call_arguments.append(parameter_name)

        config_name = record_parameters.get("dsc_cfg_t")
        state_name = record_parameters.get("dsc_state_t")
        if not config_name or not state_name:
            raise RuntimeError("flatness-window oracle requires dsc_cfg_t and dsc_state_t parameters")

        tables = semantics.get("tables", {}) or {}
        luma_tables = tables.get("luma", {}) or {}
        chroma_tables = tables.get("chroma", {}) or {}
        if not luma_tables or not chroma_tables:
            raise RuntimeError("flatness-window oracle requires Table 6-2 rows")

        table_declarations: list[str] = []
        table_selection: list[str] = ["switch (bits_per_component) {"]
        for raw_bpc in sorted(luma_tables, key=lambda value: int(value)):
            bpc = int(raw_bpc)
            luma_values = [int(value) for value in luma_tables[raw_bpc]]
            chroma_values = [int(value) for value in chroma_tables[raw_bpc]]
            luma_values.extend([0] * (32 - len(luma_values)))
            chroma_values.extend([0] * (32 - len(chroma_values)))
            table_declarations.extend([
                f"static int flat_luma_{bpc}[32] = {{{', '.join(str(value) for value in luma_values)}}};",
                f"static int flat_chroma_{bpc}[32] = {{{', '.join(str(value) for value in chroma_values)}}};",
            ])
            table_selection.extend([
                f"case {bpc}: {state_name}.quantTableLuma = flat_luma_{bpc}; {state_name}.quantTableChroma = flat_chroma_{bpc}; break;",
            ])
        default_bpc = int(sorted(luma_tables, key=lambda value: int(value))[0])
        table_selection.extend([
            f"default: {state_name}.quantTableLuma = flat_luma_{default_bpc}; {state_name}.quantTableChroma = flat_chroma_{default_bpc}; break;",
            "}",
        ])

        hpos_port = next(port for port in inputs if str(port.get("name")) == hpos_name)
        hpos_domain = hpos_port.get("legal_domain", {}) or {}
        hpos_values = hpos_domain.get("values")
        hpos_bounds = hpos_domain.get("range")
        if isinstance(hpos_values, list) and hpos_values:
            hpos_max = max(int(value) for value in hpos_values)
        elif isinstance(hpos_bounds, list) and len(hpos_bounds) == 2:
            hpos_max = int(hpos_bounds[1])
        else:
            raise RuntimeError("flatness-window oracle needs a finite hPos upper bound")
        padding_left = int(window.get("padding_left", 5))
        max_offset = max(int(value) for value in window.get("sample_offsets", [0, 1, 2, 3, 4, 5, 6]))
        line_capacity = max(1, hpos_max + padding_left + max_offset + 2)
        storage_declarations = [
            f"static int orig_line_{component}[{line_capacity}] = {{0}};"
            for component in range(4)
        ]

        state_setup = [
            f"{config_name}.bits_per_component = {bpc_name};",
            f"{config_name}.flatness_det_thresh = {flatness_thresh_name};",
            f"{config_name}.somewhat_flat_qp_delta = {flatness_delta_name};",
            f"{config_name}.native_420 = {native420_name};",
            f"{config_name}.dsc_version_minor = {version_name};",
            f"{state_name}.numComponents = {num_components_name};",
            f"{state_name}.sliceWidth = {slice_width_name};",
            f"{state_name}.primaryQp = {primary_qp_name};",
            f"{state_name}.cpntBitDepth[0] = {cpnt0_name};",
            f"{state_name}.cpntBitDepth[1] = {cpnt1_name};",
        ]
        state_setup.extend(
            f"{state_name}.origLine[{component}] = orig_line_{component};"
            for component in range(4)
        )
        state_setup.extend(table_selection)
        for component in range(4):
            for offset, port_name in enumerate(sample_names[component]):
                state_setup.append(
                    f"orig_line_{component}[PADDING_LEFT + {hpos_name} + {offset}] = {port_name};"
                )

        input_declarations = ", ".join(str(port["name"]) for port in inputs)
        input_arguments = ", ".join(f"&{port['name']}" for port in inputs)
        format_string = " ".join(["%d"] * len(inputs))
        setup = "\n                        ".join(state_setup)
        return textwrap.dedent(
            f"""
            #include <stdio.h>
            #include "dsc_types.h"
            extern int {name}({', '.join(parameter_declarations)});
            {' '.join(table_declarations)}
            int main(int argc, char **argv) {{
                FILE *input = stdin;
                if (argc > 1) {{
                    input = fopen(argv[1], "rb");
                    if (!input) return 2;
                }}
                int {input_declarations};
                static int orig_line_0[{line_capacity}] = {{0}};
                static int orig_line_1[{line_capacity}] = {{0}};
                static int orig_line_2[{line_capacity}] = {{0}};
                static int orig_line_3[{line_capacity}] = {{0}};
                while (fscanf(input, "{format_string}", {input_arguments}) == {len(inputs)}) {{
                    dsc_cfg_t {config_name} = {{0}};
                    dsc_state_t {state_name} = {{0}};
                    {setup}
                    int {output} = {name}({', '.join(call_arguments)});
                    printf("%d\\n", {output});
                }}
                if (input != stdin) fclose(input);
                return 0;
            }}
            """
        ).strip() + "\n"

    def render_ich_decision_oracle(
        self,
        contract: dict[str, Any],
        inputs: list[dict[str, Any]],
        output: str,
    ) -> str:
        """Freeze the read-only DSC state projection for IchDecision.

        The C function itself remains the oracle.  This adapter supplies only
        scalar state/config fields and the original-pixel taps it reads
        transitively through IsOrigFlatHIndex.  The qLevel ports are frozen
        outputs of the already-promoted MapQpToQlevel component; placing them
        into the C model's lookup tables keeps this composite check modular
        without copying the table implementation into the adapter.
        """
        function = contract_function(contract)
        name = str(function.get("name"))
        parameters = self.function_parameters(contract)
        if not parameters:
            raise RuntimeError("ich-decision oracle requires original C parameter facts")
        semantics = contract.get("semantics", {}) or {}
        strategy = semantics.get("legal_vector_strategy", {}) or {}
        input_names = {str(port.get("name")) for port in inputs}

        def require(key: str, fallback: str) -> str:
            value = str(strategy.get(key, fallback))
            if value not in input_names:
                raise RuntimeError(f"ich-decision binding is not an input port: {value}")
            return value

        cfg_fields = {
            "dsc_version_minor": require("version_port", "dsc_version_minor"),
            "native_420": require("native_420_port", "native_420"),
            "flatness_det_thresh": require("flatness_det_thresh_port", "flatness_det_thresh"),
            "somewhat_flat_qp_delta": require("somewhat_flat_qp_delta_port", "somewhat_flat_qp_delta"),
        }
        state_fields = {
            "unitsPerGroup": require("units_per_group_port", "units_per_group"),
            "pixelsInGroup": require("pixels_in_group_port", "pixels_in_group"),
            "hPos": require("hpos_port", "hPos"),
            "sliceWidth": require("slice_width_port", "slice_width"),
            "prevIchSelected": require("prev_ich_selected_port", "prev_ich_selected"),
            "primaryQp": require("primary_qp_port", "primary_qp"),
            "prevPrimaryQp": require("prev_primary_qp_port", "prev_primary_qp"),
            "ichIndicesInGroup": require("ich_indices_in_group_port", "ich_indices_in_group"),
            "numComponents": require("num_components_port", "num_components"),
        }

        def require_group(key: str, length: int) -> list[str]:
            values = strategy.get(key, [])
            if not isinstance(values, list) or len(values) != length:
                raise RuntimeError(f"ich-decision binding requires {length} ports for {key}")
            result = [str(value) for value in values]
            if any(value not in input_names for value in result):
                raise RuntimeError(f"ich-decision binding has a missing port for {key}")
            return result

        depth_ports = require_group("component_depth_ports", 4)
        ctype_ports = require_group("unit_component_ports", 4)
        start_ports = require_group("unit_start_hpos_ports", 4)
        predicted_ports = require_group("predicted_size_ports", 4)
        max_error_ports = require_group("max_error_ports", 4)
        max_mid_error_ports = require_group("max_mid_error_ports", 4)
        max_ich_error_ports = require_group("max_ich_error_ports", 4)
        residual_ports = require_group("residual_ports", 12)
        qlevel_ports = strategy.get("qlevel_ports", {}) or {}
        qlevel_names = {
            key: str(qlevel_ports.get(key, ""))
            for key in ("luma_primary", "chroma_primary", "luma_previous",
                        "chroma_previous", "luma_flat", "chroma_flat")
        }
        if any(value not in input_names for value in qlevel_names.values()):
            raise RuntimeError("ich-decision oracle is missing a qLevel port")
        orig_ports = strategy.get("orig_ports_by_component", {}) or {}
        if not isinstance(orig_ports, dict):
            raise RuntimeError("ich-decision oracle is missing original-pixel bindings")
        orig_names: dict[int, list[str]] = {}
        for component in range(4):
            raw = orig_ports.get(str(component), orig_ports.get(component, []))
            if not isinstance(raw, list) or len(raw) != 7:
                raise RuntimeError("ich-decision oracle requires seven original taps per component")
            values = [str(value) for value in raw]
            if any(value not in input_names for value in values):
                raise RuntimeError("ich-decision oracle has a missing original tap")
            orig_names[component] = values

        input_declarations = ", ".join(f"int {port['name']}" for port in inputs)
        local_declarations = ", ".join(str(port["name"]) for port in inputs)
        arguments = ", ".join(f"&{port['name']}" for port in inputs)
        format_string = " ".join(["%d"] * len(inputs))
        call_arguments = ", ".join([
            "&dsc_cfg",
            "&dsc_state",
            str(strategy.get("adj_predicted_size_port", "adj_predicted_size")),
            str(strategy.get("alt_pfx_port", "alt_pfx")),
            str(strategy.get("alt_size_to_generate_port", "alt_size_to_generate")),
        ])
        assignments = [
            f"dsc_cfg.{field} = {port};" for field, port in cfg_fields.items()
        ]
        assignments.extend([
            f"dsc_state.{field} = {port};" for field, port in state_fields.items()
        ])
        assignments.extend([
            f"dsc_state.cpntBitDepth[{index}] = {port};"
            for index, port in enumerate(depth_ports)
        ])
        assignments.extend([
            f"dsc_state.unitCType[{index}] = {port};"
            for index, port in enumerate(ctype_ports)
        ])
        assignments.extend([
            f"dsc_state.unitStartHPos[{index}] = {port};"
            for index, port in enumerate(start_ports)
        ])
        assignments.extend([
            f"dsc_state.predictedSize[{index}] = {port};"
            for index, port in enumerate(predicted_ports)
        ])
        assignments.extend([
            f"dsc_state.maxError[{index}] = {port};"
            for index, port in enumerate(max_error_ports)
        ])
        assignments.extend([
            f"dsc_state.maxMidError[{index}] = {port};"
            for index, port in enumerate(max_mid_error_ports)
        ])
        assignments.extend([
            f"dsc_state.maxIchError[{index}] = {port};"
            for index, port in enumerate(max_ich_error_ports)
        ])
        assignments.extend([
            f"dsc_state.quantizedResidual[{unit}][{sample}] = {residual_ports[unit * 3 + sample]};"
            for unit in range(4) for sample in range(3)
        ])
        assignments.extend([
            f"orig_line[{component}][PADDING_LEFT + {state_fields['hPos']} + {offset}] = {port};"
            for component in range(4)
            for offset, port in enumerate(orig_names[component])
        ])
        qlevel_primary_luma = qlevel_names["luma_primary"]
        qlevel_primary_chroma = qlevel_names["chroma_primary"]
        qlevel_previous_luma = qlevel_names["luma_previous"]
        qlevel_previous_chroma = qlevel_names["chroma_previous"]
        qlevel_flat_luma = qlevel_names["luma_flat"]
        qlevel_flat_chroma = qlevel_names["chroma_flat"]
        assignments.extend([
            f"quant_luma[{state_fields['primaryQp']}] = {qlevel_primary_luma};",
            f"quant_chroma[{state_fields['primaryQp']}] = {qlevel_primary_chroma};",
            f"quant_luma[{state_fields['prevPrimaryQp']}] = {qlevel_previous_luma};",
            f"quant_chroma[{state_fields['prevPrimaryQp']}] = {qlevel_previous_chroma};",
            f"quant_luma[flat_qp] = {qlevel_flat_luma};",
            f"quant_chroma[flat_qp] = {qlevel_flat_chroma};",
        ])
        setup = "\n                        ".join(assignments)
        record_declarations = "\n                        ".join([
            "dsc_cfg_t dsc_cfg = {0};",
            "dsc_state_t dsc_state = {0};",
            "int quant_luma[32] = {0};",
            "int quant_chroma[32] = {0};",
            "static int orig_line[NUM_COMPONENTS][PADDING_LEFT + 65535 + 8];",
            "int flat_qp = dsc_state.primaryQp - dsc_cfg.somewhat_flat_qp_delta;",
            "if (flat_qp < 0) flat_qp = 0;",
            "dsc_state.quantTableLuma = quant_luma;",
            "dsc_state.quantTableChroma = quant_chroma;",
        ])
        # Recompute flat_qp after the input assignments; the declaration above
        # intentionally stays scalar, while the assignment is written after
        # cfg/state binding in the generated loop.
        record_declarations = "\n                        ".join([
            "dsc_cfg_t dsc_cfg = {0};",
            "dsc_state_t dsc_state = {0};",
            "int quant_luma[32] = {0};",
            "int quant_chroma[32] = {0};",
            "static int orig_line[NUM_COMPONENTS][PADDING_LEFT + 65535 + 8];",
        ])
        setup = "\n                        ".join([
            *[f"{field}" for field in assignments[:len(cfg_fields) + len(state_fields) + len(depth_ports) + len(ctype_ports) + len(start_ports) + len(predicted_ports) + len(max_error_ports) + len(max_mid_error_ports) + len(max_ich_error_ports) + len(residual_ports)]],
            "dsc_state.quantTableLuma = quant_luma;",
            "dsc_state.quantTableChroma = quant_chroma;",
            "for (int table_i = 0; table_i < 32; ++table_i) { quant_luma[table_i] = 0; quant_chroma[table_i] = 0; }",
            f"quant_luma[{state_fields['primaryQp']}] = {qlevel_primary_luma};",
            f"quant_chroma[{state_fields['primaryQp']}] = {qlevel_primary_chroma};",
            f"quant_luma[{state_fields['prevPrimaryQp']}] = {qlevel_previous_luma};",
            f"quant_chroma[{state_fields['prevPrimaryQp']}] = {qlevel_previous_chroma};",
            f"int flat_qp = {state_fields['primaryQp']} - {cfg_fields['somewhat_flat_qp_delta']};",
            "if (flat_qp < 0) flat_qp = 0;",
            f"quant_luma[flat_qp] = {qlevel_flat_luma};",
            f"quant_chroma[flat_qp] = {qlevel_flat_chroma};",
            *[f"dsc_state.origLine[{component}] = orig_line[{component}];" for component in range(4)],
            *[f"orig_line[{component}][PADDING_LEFT + {state_fields['hPos']} + {offset}] = {port};"
              for component in range(4)
              for offset, port in enumerate(orig_names[component])],
            *[f"dsc_state.quantizedResidual[{unit}][{sample}] = {residual_ports[unit * 3 + sample]};"
              for unit in range(4) for sample in range(3)],
        ])
        return textwrap.dedent(
            f"""
            #include <stdio.h>
            #include <string.h>
            #include "dsc_types.h"
            extern int {name}(dsc_cfg_t *, dsc_state_t *, int, int, int);
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
                    {setup}
                    {output} = {name}({call_arguments});
                    printf("%d\\n", {output});
                }}
                if (input != stdin) fclose(input);
                return 0;
            }}
            """
        ).strip() + "\n"

    def render_dynamic_window_oracle(
        self,
        contract: dict[str, Any],
        inputs: list[dict[str, Any]],
        output: str,
        dynamic_window: dict[str, Any],
    ) -> str:
        """Render a C adapter for a reviewed relative line-buffer window.

        The frozen RTL interface carries only the relative taps required by
        the reviewed function.  The immutable C function still receives its
        native line-buffer pointers, so this adapter reconstructs those
        physical offsets for each vector.  It is driven by window metadata,
        not by a function-name allowlist.
        """
        function = contract_function(contract)
        name = str(function.get("name"))
        parameters = self.function_parameters(contract)
        if not parameters:
            raise RuntimeError("dynamic-window oracle requires original C parameter facts")

        input_names = {str(port.get("name")) for port in inputs}
        prev_parameter = str(dynamic_window.get("prev_parameter", ""))
        curr_parameter = str(dynamic_window.get("curr_parameter", ""))
        hpos_parameter = str(dynamic_window.get("hpos_parameter", ""))
        prev_ports = [str(value) for value in dynamic_window.get("prev_window_ports", [])]
        curr_ports = [str(value) for value in dynamic_window.get("curr_window_ports", [])]
        if not prev_parameter or not curr_parameter or not hpos_parameter:
            raise RuntimeError("dynamic-window oracle is missing pointer/position bindings")
        if hpos_parameter not in input_names:
            raise RuntimeError(f"dynamic-window hPos binding is not an input port: {hpos_parameter}")
        if not prev_ports or not curr_ports or any(
            port not in input_names for port in prev_ports + curr_ports
        ):
            raise RuntimeError("dynamic-window oracle references missing frozen tap ports")

        def index_expression(raw_index: object) -> str:
            raw = str(raw_index)
            if re.fullmatch(r"-?\d+", raw):
                return raw
            if raw in input_names:
                return raw
            normalized = re.sub(r"[^a-z0-9]", "", raw.lower())
            for port in inputs:
                for candidate in (port.get("name"), port.get("role")):
                    if re.sub(r"[^a-z0-9]", "", str(candidate).lower()) == normalized:
                        return str(port.get("name"))
            raise RuntimeError(f"dynamic-window state index is not an input port or literal: {raw}")

        parameter_declarations: list[str] = []
        call_arguments: list[str] = []
        state_name = ""
        state_type = ""
        for parameter in parameters:
            parameter_name = str(parameter.get("name", ""))
            parameter_type = str(parameter.get("type", "int")).strip()
            if not parameter_name or not re.match(r"^[A-Za-z_][A-Za-z0-9_]*$", parameter_name):
                raise RuntimeError(f"invalid C parameter name: {parameter_name}")
            parameter_declarations.append(f"{parameter_type} {parameter_name}")
            if not parameter.get("pointer"):
                if parameter_name not in input_names:
                    raise RuntimeError(f"dynamic-window scalar parameter is not an input port: {parameter_name}")
                call_arguments.append(parameter_name)
                continue
            if parameter_name in {prev_parameter, curr_parameter}:
                call_arguments.append(parameter_name)
                continue
            if state_name:
                raise RuntimeError("dynamic-window oracle has multiple non-line-buffer pointer parameters")
            state_type = re.sub(r"\s*\*.*$", "", parameter_type).strip()
            state_name = parameter_name
            call_arguments.append(f"&{state_name}")
        if not state_name or not state_type:
            raise RuntimeError("dynamic-window oracle has no state record pointer")

        flattened = list((contract.get("interface", {}) or {}).get("flattened_pointer_dependencies", []) or [])
        state_setup: list[str] = []
        for item in flattened:
            if str(item.get("parameter", "")) != state_name:
                continue
            field = str(item.get("field", ""))
            port_name = safe_identifier(str(item.get("port_name") or ""))
            if not field or port_name not in input_names:
                continue
            field_name = field.split("[", 1)[0]
            if not re.match(r"^[A-Za-z_][A-Za-z0-9_]*$", field_name):
                continue
            indices: list[object] = []
            if isinstance(item.get("index_names"), list):
                indices.extend(item.get("index_names") or [])
            elif item.get("index_name") is not None:
                indices.append(item.get("index_name"))
            elif item.get("index") is not None:
                indices.append(item.get("index"))
            lhs = f"{state_name}.{field_name}"
            for index in indices:
                lhs += f"[{index_expression(index)}]"
            state_setup.append(f"{lhs} = {port_name};")

        def hpos_upper_bound() -> int:
            hpos_port = next(port for port in inputs if str(port.get("name")) == hpos_parameter)
            domain = hpos_port.get("legal_domain", {}) or {}
            values = domain.get("values")
            if isinstance(values, list) and values:
                return max(int(value) for value in values)
            bounds = domain.get("range")
            if isinstance(bounds, list) and len(bounds) == 2:
                return int(bounds[1])
            raise RuntimeError("dynamic-window oracle needs a finite hPos upper bound")

        samples_per_unit = int(dynamic_window.get("samples_per_unit", 3))
        padding_left = int(dynamic_window.get("padding_left", 5))
        prev_first_offset = int(dynamic_window.get("prev_window_first_offset", 0))
        current_window_left = int(dynamic_window.get("current_window_left", 0))
        hpos_max = hpos_upper_bound()
        prev_last = (
            (hpos_max // samples_per_unit) * samples_per_unit
            + padding_left
            + prev_first_offset
            + len(prev_ports)
            - 1
        )
        curr_last = max(hpos_max - current_window_left, 0) + len(curr_ports) - 1
        line_capacity = max(1, prev_last + 1, curr_last + 1)
        prev_window_base = (
            f"(({hpos_parameter} / {samples_per_unit}) * {samples_per_unit}"
            f" + {padding_left} + {prev_first_offset})"
        )
        curr_window_base = (
            f"(({hpos_parameter} > {current_window_left})"
            f" ? ({hpos_parameter} - {current_window_left}) : 0)"
        )
        prev_assignments = "\n                        ".join(
            f"prevLine[{prev_window_base} + {index}] = {port};"
            for index, port in enumerate(prev_ports)
        )
        curr_assignments = "\n                        ".join(
            f"currLine[{curr_window_base} + {index}] = {port};"
            for index, port in enumerate(curr_ports)
        )
        input_declarations = ", ".join(str(port["name"]) for port in inputs)
        input_arguments = ", ".join(f"&{port['name']}" for port in inputs)
        format_string = " ".join(["%d"] * len(inputs))
        setup = "\n                        ".join(
            state_setup + [prev_assignments, curr_assignments]
        )
        return textwrap.dedent(
            f"""
            #include <stdio.h>
            #include "dsc_types.h"
            extern int {name}({', '.join(parameter_declarations)});
            int main(int argc, char **argv) {{
                FILE *input = stdin;
                if (argc > 1) {{
                    input = fopen(argv[1], "rb");
                    if (!input) return 2;
                }}
                int {input_declarations};
                static int prevLine[{line_capacity}] = {{0}};
                static int currLine[{line_capacity}] = {{0}};
                while (fscanf(input, "{format_string}", {input_arguments}) == {len(inputs)}) {{
                    {state_type} {state_name} = {{0}};
                    {setup}
                    int {output} = {name}({', '.join(call_arguments)});
                    printf("%d\\n", {output});
                }}
                if (input != stdin) fclose(input);
                return 0;
            }}
            """
        ).strip() + "\n"

    def table_lookup_vector_iterator(
        self,
        contract: dict[str, Any],
        input_ports: list[dict[str, Any]],
        values: list[list[int]],
        strategy: dict[str, Any],
    ) -> tuple[Iterable[tuple[int, ...]], dict[str, Any]]:
        """Enumerate reviewed table/state relations without a false Cartesian product.

        A flattened table lookup port is a selected value, not an independent
        free variable.  The relation below keeps the frozen scalar interface
        while deriving the selected qlevel ports from the QP and the reviewed
        source table for the selected base bit depth.  This is deliberately
        contract data driven: no function name or hard-coded contract id is
        consulted here.
        """
        names = [str(port.get("name")) for port in input_ports]
        positions = {name: index for index, name in enumerate(names)}
        base_port = str(strategy.get("base_bit_depth_port", ""))
        table_bindings = strategy.get("table_bindings", {}) or {}
        tables = strategy.get("tables", {}) or (contract.get("semantics", {}) or {}).get("tables", {}) or {}
        related_specs = strategy.get("bit_depth_ports", {}) or {}
        if base_port not in positions or not table_bindings or not tables:
            raise RuntimeError("incomplete reviewed table-lookup vector strategy")

        qp_ports: set[str] = set()
        table_ports: set[str] = set()
        for table_port, binding in table_bindings.items():
            if table_port not in positions:
                raise RuntimeError(f"table binding port is not an input port: {table_port}")
            qp_port = str((binding or {}).get("qp_port", ""))
            if qp_port not in positions:
                raise RuntimeError(f"table binding QP is not an input port: {qp_port}")
            table_kind = str((binding or {}).get("table", ""))
            if table_kind not in tables:
                raise RuntimeError(f"table binding references unknown table: {table_kind}")
            qp_ports.add(qp_port)
            table_ports.add(table_port)

        related_ports = set(related_specs)
        if base_port in related_ports or not related_ports.issubset(positions):
            raise RuntimeError("invalid related bit-depth ports in table-lookup strategy")

        by_name = {name: values[index] for index, name in enumerate(names)}
        varying_names = {base_port, *related_ports, *qp_ports, *table_ports}
        fixed_names = [name for name in names if name not in varying_names]
        fixed_values = [by_name[name] for name in fixed_names]
        base_values = by_name[base_port]

        def table_for(table_kind: str, bit_depth: int) -> list[int]:
            table = tables.get(table_kind, {}) or {}
            raw = table.get(str(bit_depth), table.get(bit_depth))
            if not isinstance(raw, list) or not raw:
                raise RuntimeError(
                    f"reviewed table {table_kind} has no entries for bit depth {bit_depth}"
                )
            return [int(value) for value in raw]

        def related_values(port_name: str, bit_depth: int) -> list[int]:
            spec = related_specs.get(port_name, {}) or {}
            values_by_base = spec.get("values_by_base")
            if values_by_base is not None:
                raw = values_by_base.get(str(bit_depth), values_by_base.get(bit_depth))
                if raw is None:
                    raise RuntimeError(
                        f"related bit-depth port {port_name} has no value for {bit_depth}"
                    )
                return [int(value) for value in raw]
            offsets = spec.get("offsets")
            if offsets is not None:
                return [int(bit_depth) + int(offset) for offset in offsets]
            raise RuntimeError(f"related bit-depth port has no rule: {port_name}")

        def constrained() -> Iterable[tuple[int, ...]]:
            for fixed in itertools.product(*fixed_values) if fixed_values else [()]:
                context = dict(zip(fixed_names, fixed))
                for bit_depth in base_values:
                    bit_depth = int(bit_depth)
                    selected_tables = {
                        kind: table_for(kind, bit_depth) for kind in tables
                    }
                    max_qp = min(len(table) for table in selected_tables.values()) - 1
                    qp_domains = {
                        qp_port: [int(qp) for qp in by_name[qp_port] if int(qp) <= max_qp]
                        for qp_port in qp_ports
                    }
                    if any(not domain for domain in qp_domains.values()):
                        continue
                    related_names = sorted(related_specs)
                    related_domains = [
                        related_values(port_name, bit_depth) for port_name in related_names
                    ]
                    for related in itertools.product(*related_domains) if related_domains else [()]:
                        context[base_port] = bit_depth
                        context.update(dict(zip(related_names, related)))
                        qp_names = sorted(qp_ports)
                        qp_domains_ordered = [qp_domains[qp_port] for qp_port in qp_names]
                        for qps in itertools.product(*qp_domains_ordered) if qp_domains_ordered else [()]:
                            context.update(dict(zip(qp_names, qps)))
                            for table_port, binding in table_bindings.items():
                                table_kind = str(binding["table"])
                                qp_port = str(binding["qp_port"])
                                context[table_port] = selected_tables[table_kind][context[qp_port]]
                            yield tuple(int(context[name]) for name in names)

        return constrained(), {
            "kind": "table_lookup",
            "source": "reviewed source table relation",
            "base_bit_depth_port": base_port,
            "related_bit_depth_ports": sorted(related_ports),
            "table_ports": sorted(table_ports),
            "qp_ports": sorted(qp_ports),
        }

    def qp_table_vector_iterator(
        self,
        contract: dict[str, Any],
        input_ports: list[dict[str, Any]],
        values: list[list[int]],
        strategy: dict[str, Any],
    ) -> tuple[Iterable[tuple[int, ...]], dict[str, Any]]:
        """Enumerate a normative QP table with its bit-depth row relation.

        Table 6-2 has a different legal QP extent for each supported bit
        depth.  Keeping that relation here prevents the C oracle from reading
        past the selected immutable table while retaining an exhaustive
        finite domain.  The strategy is data-driven and applies to any
        reviewed configuration lookup with the same table shape.
        """
        names = [str(port.get("name")) for port in input_ports]
        by_name = {name: values[index] for index, name in enumerate(names)}
        base_port = str(strategy.get("base_bit_depth_port", ""))
        qp_port = str(strategy.get("qp_port", ""))
        tables = strategy.get("tables") or (contract.get("semantics", {}) or {}).get("tables", {}) or {}
        if base_port not in by_name or qp_port not in by_name or not tables:
            raise RuntimeError("incomplete reviewed QP-table vector strategy")
        fixed_names = [name for name in names if name not in {base_port, qp_port}]
        fixed_values = [by_name[name] for name in fixed_names]

        def table_length(table_kind: str, bit_depth: int) -> int:
            table = tables.get(table_kind, {}) or {}
            raw = table.get(str(bit_depth), table.get(bit_depth))
            if not isinstance(raw, list) or not raw:
                raise RuntimeError(
                    f"reviewed QP table {table_kind} has no row for {bit_depth}"
                )
            return len(raw)

        def constrained() -> Iterable[tuple[int, ...]]:
            for fixed in itertools.product(*fixed_values) if fixed_values else [()]:
                context = dict(zip(fixed_names, fixed))
                for bit_depth in by_name[base_port]:
                    bit_depth = int(bit_depth)
                    max_qp = min(
                        table_length(str(table_kind), bit_depth)
                        for table_kind in tables
                    ) - 1
                    for qp in by_name[qp_port]:
                        if int(qp) > max_qp:
                            continue
                        context[base_port] = bit_depth
                        context[qp_port] = int(qp)
                        yield tuple(int(context[name]) for name in names)

        return constrained(), {
            "kind": "qp_table",
            "source": "reviewed normative QP table row relation",
            "base_bit_depth_port": base_port,
            "qp_port": qp_port,
            "max_qp_by_bit_depth": {
                str(bit_depth): min(
                    table_length(str(table_kind), int(bit_depth))
                    for table_kind in tables
                ) - 1
                for bit_depth in by_name[base_port]
            },
        }

    def windowed_boundary_vector_iterator(
        self,
        contract: dict[str, Any],
        input_ports: list[dict[str, Any]],
        values: list[list[int]],
        strategy: dict[str, Any],
    ) -> tuple[Iterable[tuple[int, ...]], dict[str, Any]]:
        """Generate a deterministic large differential suite for windowed DUTs.

        A windowed leaf can have a finite scalar interface after pointer
        flattening while still having a huge sample-value domain.  This
        strategy exercises every structural mode, all legal qLevels for the
        selected component class, one-factor boundary probes, and pairwise
        tap interactions.  It is explicitly *not* an exhaustive proof; the
        receipt must remain DIFFERENTIAL_PASS until a separate proof or a
        tractable exact domain exists.
        """
        names = [str(port.get("name")) for port in input_ports]
        by_name = {name: values[index] for index, name in enumerate(names)}
        window = (contract.get("semantics", {}) or {}).get("window_spec", {}) or {}
        dynamic_window = window.get("dynamic_line_window") if isinstance(window, dict) else None
        if dynamic_window and not strategy.get("_dynamic_hpos_probed"):
            hpos_name = str(strategy.get("hpos_port", ""))
            if hpos_name in by_name and len(by_name[hpos_name]) > 64:
                legal_hpos = [int(value) for value in by_name[hpos_name]]
                hpos_min = min(legal_hpos)
                hpos_max = max(legal_hpos)
                raw_probes = dynamic_window.get("hpos_probe_values", []) if isinstance(dynamic_window, dict) else []
                probes = {
                    int(value) for value in raw_probes
                    if int(value) in set(legal_hpos)
                }
                probes.update(
                    value for value in (
                        hpos_min,
                        hpos_min + 1,
                        hpos_min + 2,
                        hpos_min + 3,
                        hpos_min + 4,
                        hpos_min + 8,
                        hpos_min + 9,
                        hpos_min + 10,
                        hpos_min + 11,
                        hpos_min + 12,
                        hpos_min + 13,
                        hpos_min + 14,
                        hpos_min + 15,
                        hpos_max // 2 - 1,
                        hpos_max // 2,
                        hpos_max // 2 + 1,
                        hpos_max - 4,
                        hpos_max - 3,
                        hpos_max - 2,
                        hpos_max - 1,
                        hpos_max,
                    )
                    if hpos_min <= value <= hpos_max
                )
                adjusted_values = [list(value) for value in values]
                hpos_index = names.index(hpos_name)
                adjusted_values[hpos_index] = sorted(probes)
                adjusted_strategy = dict(strategy)
                adjusted_strategy["_dynamic_hpos_probed"] = True
                iterator, details = self.windowed_boundary_vector_iterator(
                    contract,
                    input_ports,
                    adjusted_values,
                    adjusted_strategy,
                )
                details["coverage_mode"] = "DYNAMIC_RELATIVE_WINDOW_PROBES"
                details["hpos_domain"] = [hpos_min, hpos_max]
                details["hpos_probe_values"] = sorted(probes)
                details["formal_required"] = True
                return iterator, details

        def require_port(key: str) -> str:
            name = str(strategy.get(key, ""))
            if name not in by_name:
                raise RuntimeError(f"windowed boundary strategy port is missing: {name}")
            return name

        bit_depth_name = require_port("bit_depth_port")
        component_name = require_port("component_type_port")
        qlevel_name = require_port("qlevel_port")
        unit_name = require_port("unit_port")
        hpos_name = require_port("hpos_port")
        pred_type_name = require_port("pred_type_port")
        sample_ports = [str(name) for name in strategy.get("sample_ports", [])]
        residual_ports = [str(name) for name in strategy.get("residual_ports", [])]
        pairwise_ports = [str(name) for name in strategy.get("pairwise_ports", [])]
        raw_pairwise_groups = strategy.get("pairwise_groups", []) or []
        pairwise_groups: list[list[str]] = []
        if raw_pairwise_groups:
            if not isinstance(raw_pairwise_groups, list):
                raise RuntimeError("windowed boundary pairwise_groups must be a list")
            for raw_group in raw_pairwise_groups:
                if not isinstance(raw_group, list) or len(raw_group) < 2:
                    raise RuntimeError("windowed boundary pairwise group must contain at least two ports")
                pairwise_groups.append([str(name) for name in raw_group])
        elif pairwise_ports:
            pairwise_groups = [pairwise_ports]
        all_pairwise_ports = sorted({name for group in pairwise_groups for name in group})
        for port_name in sample_ports + residual_ports + all_pairwise_ports:
            if port_name not in by_name:
                raise RuntimeError(f"windowed boundary strategy port is missing: {port_name}")

        max_qlevel_by_component = strategy.get("qlevel_max_by_component", {}) or {}
        probe_units = [int(value) for value in strategy.get("probe_units", by_name[unit_name])]
        probe_units = [value for value in probe_units if value in by_name[unit_name]] or list(by_name[unit_name])
        probe_qlevels = str(strategy.get("probe_qlevels", "endpoints"))

        bit_depth_values_by_component = strategy.get("bit_depth_values_by_component", {}) or {}

        def bit_depths_for(component: int) -> list[int]:
            kind = "luma" if int(component) % 3 == 0 else "chroma"
            raw_values = bit_depth_values_by_component.get(kind)
            if raw_values is None:
                return [int(value) for value in by_name[bit_depth_name]]
            allowed = {int(value) for value in by_name[bit_depth_name]}
            values_for_kind = [int(value) for value in raw_values if int(value) in allowed]
            return values_for_kind or [int(value) for value in by_name[bit_depth_name]]

        def unique(values_to_check: Iterable[int]) -> list[int]:
            result: list[int] = []
            seen: set[int] = set()
            for value in values_to_check:
                value = int(value)
                if value not in seen:
                    seen.add(value)
                    result.append(value)
            return result

        def sample_boundaries(bit_depth: int) -> list[int]:
            maximum = (1 << int(bit_depth)) - 1
            midpoint = maximum // 2
            return unique([0, 1, midpoint - 1, midpoint, midpoint + 1, maximum - 1, maximum])

        def residual_boundaries(bit_depth: int, qlevel: int) -> list[int]:
            width = int(bit_depth) - int(qlevel)
            if width <= 0:
                return [0]
            lower = -(1 << (width - 1))
            upper = (1 << (width - 1)) - 1
            return unique([lower, lower + 1, -1, 0, 1, upper - 1, upper])

        def qlevels_for(bit_depth: int, component: int) -> list[int]:
            kind = "luma" if int(component) % 3 == 0 else "chroma"
            raw_max = max_qlevel_by_component.get(kind, {}).get(str(bit_depth))
            max_qlevel = int(raw_max) if raw_max is not None else max(by_name[qlevel_name])
            return [int(value) for value in by_name[qlevel_name] if int(value) <= max_qlevel]

        def baseline(
            bit_depth: int,
            component: int,
            qlevel: int,
            unit: int,
            hpos: int,
            pred_type: int,
        ) -> dict[str, int]:
            context = {
                name: int(domain[len(domain) // 2])
                for name, domain in by_name.items()
                if domain
            }
            context.update({
                bit_depth_name: int(bit_depth),
                component_name: int(component),
                qlevel_name: int(qlevel),
                unit_name: int(unit),
                hpos_name: int(hpos),
                pred_type_name: int(pred_type),
            })
            midpoint = ((1 << int(bit_depth)) - 1) // 2
            for port_name in sample_ports:
                context[port_name] = midpoint
            for port_name in residual_ports:
                context[port_name] = 0
            return context

        def emit(context: dict[str, int]) -> tuple[int, ...]:
            return tuple(int(context[name]) for name in names)

        structural: list[tuple[int, int, int, int, int, int]] = []
        for component in by_name[component_name]:
            for bit_depth in bit_depths_for(int(component)):
                for qlevel in qlevels_for(int(bit_depth), int(component)):
                    for unit in by_name[unit_name]:
                        for hpos in by_name[hpos_name]:
                            for pred_type in by_name[pred_type_name]:
                                structural.append((
                                    int(bit_depth), int(component), int(qlevel),
                                    int(unit), int(hpos), int(pred_type),
                                ))

        def vectors() -> Iterable[tuple[int, ...]]:
            # First cover every legal structural mode with a stable midpoint
            # line and zero residual baseline.
            for bit_depth, component, qlevel, unit, hpos, pred_type in structural:
                yield emit(baseline(bit_depth, component, qlevel, unit, hpos, pred_type))

            # Boundary probes use qLevel endpoints (or all qLevels when the
            # contract asks for it) and both end units to expose index paths.
            for component in by_name[component_name]:
                for bit_depth in bit_depths_for(int(component)):
                    qlevels = qlevels_for(int(bit_depth), int(component))
                    if probe_qlevels == "all":
                        q_probes = qlevels
                    else:
                        q_probes = unique([qlevels[0], qlevels[-1]]) if qlevels else []
                    for qlevel in q_probes:
                        for unit in probe_units:
                            for hpos in by_name[hpos_name]:
                                for pred_type in by_name[pred_type_name]:
                                    base = baseline(int(bit_depth), int(component), qlevel, unit, int(hpos), int(pred_type))
                                    boundaries = sample_boundaries(int(bit_depth))
                                    for port_name in sample_ports:
                                        for value in boundaries:
                                            case = dict(base)
                                            case[port_name] = value
                                            yield emit(case)
                                    residuals = residual_boundaries(int(bit_depth), qlevel)
                                    for port_name in residual_ports:
                                        for value in residuals:
                                            case = dict(base)
                                            case[port_name] = value
                                            yield emit(case)

                                    # Pairwise endpoints cover the principal
                                    # filter/clamp interactions without
                                    # pretending to enumerate every pixel value.
                                    pair_values = [0, (1 << int(bit_depth)) - 1]
                                    for pairwise_group in pairwise_groups:
                                        for first, second in itertools.combinations(pairwise_group, 2):
                                            for first_value in pair_values:
                                                for second_value in pair_values:
                                                    case = dict(base)
                                                    case[first] = first_value
                                                    case[second] = second_value
                                                    yield emit(case)

        return vectors(), {
            "kind": "windowed_boundary",
            "exhaustive": False,
            "coverage_mode": "STRUCTURAL_PLUS_BOUNDARY_AND_PAIRWISE",
            "source": strategy.get("source", "reviewed spec-domain differential plan"),
            "structural_cases": len(structural),
            "sample_ports": sample_ports,
            "residual_ports": residual_ports,
            "pairwise_ports": all_pairwise_ports,
            "pairwise_groups": pairwise_groups,
            "bit_depth_values_by_component": {
                str(kind): [int(value) for value in raw_values]
                for kind, raw_values in bit_depth_values_by_component.items()
            },
            "legal_relation": "qlevel is constrained by Table 6-2 component class and selected bit depth; residuals use signed n-bit decoded-domain boundaries",
        }

    def using_midpoint_vector_iterator(
        self,
        contract: dict[str, Any],
        input_ports: list[dict[str, Any]],
        values: list[list[int]],
        strategy: dict[str, Any],
    ) -> tuple[Iterable[tuple[int, ...]], dict[str, Any]]:
        """Generate a spec-structured suite for the midpoint-selection predicate.

        Selected qLevels and component depth are relations, not independent
        Cartesian inputs.  The concrete suite covers every component/unit
        branch, Table 6-2 row endpoints, version/native-420 branches, depth
        equality, and residual-size threshold boundaries.  The independent
        formal gate covers the full finite scalar domain.
        """
        names = [str(port.get("name")) for port in input_ports]
        by_name = {name: values[index] for index, name in enumerate(names)}
        semantics = contract.get("semantics", {}) or {}

        def require(key: str, fallback: str) -> str:
            name = str(strategy.get(key, fallback))
            if name not in by_name:
                raise RuntimeError(f"using-midpoint strategy port is missing: {name}")
            return name

        unit_name = require("unit_port", "unit")
        cpnt_name = require("component_port", "cpnt")
        version_name = require("version_port", "dsc_version_minor")
        native_name = require("native_420_port", "native_420")
        primary_qp_name = require("primary_qp_port", "primary_qp")
        selected_depth_name = require("selected_depth_port", "cpntBitDepth_selected")
        residual_ports = [str(value) for value in strategy.get("residual_ports", [])]
        if len(residual_ports) != 3 or any(name not in by_name for name in residual_ports):
            raise RuntimeError("using-midpoint strategy requires three residual ports")
        depth_ports = [str(value) for value in strategy.get("component_depth_ports", [])]
        if len(depth_ports) != 4 or any(name not in by_name for name in depth_ports):
            raise RuntimeError("using-midpoint strategy requires four component depth ports")
        table_bindings = strategy.get("table_bindings", {}) or {}
        tables = strategy.get("tables", {}) or semantics.get("tables", {}) or {}
        table_ports: dict[str, str] = {}
        for port_name, binding in table_bindings.items():
            table_kind = str((binding or {}).get("table", ""))
            if table_kind in {"luma", "chroma"}:
                table_ports[table_kind] = str(port_name)
            if str(port_name) not in by_name:
                raise RuntimeError(f"using-midpoint table port is missing: {port_name}")
        if set(table_ports) != {"luma", "chroma"}:
            raise RuntimeError("using-midpoint strategy requires luma and chroma table bindings")

        def unique(raw_values: Iterable[int]) -> list[int]:
            result: list[int] = []
            seen: set[int] = set()
            for raw in raw_values:
                value = int(raw)
                if value not in seen:
                    seen.add(value)
                    result.append(value)
            return result

        def values_for(name: str) -> list[int]:
            result = [int(value) for value in by_name[name]]
            if not result:
                raise RuntimeError(f"using-midpoint strategy has no legal values for {name}")
            return result

        def table_row(kind: str, bit_depth: int) -> list[int]:
            table = tables.get(kind, {}) or {}
            raw = table.get(str(bit_depth), table.get(bit_depth))
            if not isinstance(raw, list) or not raw:
                raise RuntimeError(f"using-midpoint table {kind} has no row for {bit_depth}")
            return [int(value) for value in raw]

        component_values = values_for(cpnt_name)
        unit_values = values_for(unit_name)
        version_values = values_for(version_name)
        native_values = values_for(native_name)
        primary_qp_values = values_for(primary_qp_name)
        depth_values = {name: values_for(name) for name in depth_ports}
        depth_probe_values = {
            name: unique([min(domain), max(domain), domain[len(domain) // 2]])
            for name, domain in depth_values.items()
        }
        # Component 0/1 equality is a semantic branch.  Components 2/3 only
        # select the returned depth, so their boundary probes are sufficient.
        depth_variants = list(itertools.product(
            depth_values[depth_ports[0]],
            depth_values[depth_ports[1]],
            depth_probe_values[depth_ports[2]],
            depth_probe_values[depth_ports[3]],
        ))
        if not depth_variants:
            raise RuntimeError("using-midpoint strategy has no component-depth combinations")

        def valid_qps(bit_depth: int) -> list[int]:
            lengths = [len(table_row(kind, bit_depth)) for kind in ("luma", "chroma")]
            maximum = min(lengths) - 1
            return [value for value in primary_qp_values if value <= maximum]

        def baseline(
            component: int,
            unit: int,
            bit_depths: tuple[int, int, int, int],
            primary_qp: int,
            version: int,
            native420: int,
        ) -> dict[str, int]:
            context = {
                name: int(domain[len(domain) // 2])
                for name, domain in by_name.items()
                if domain
            }
            context.update({
                unit_name: int(unit),
                cpnt_name: int(component),
                version_name: int(version),
                native_name: int(native420),
                primary_qp_name: int(primary_qp),
            })
            for name, value in zip(depth_ports, bit_depths):
                context[name] = int(value)
            context[selected_depth_name] = int(bit_depths[int(component)])
            for kind, port_name in table_ports.items():
                context[port_name] = table_row(kind, int(bit_depths[0]))[int(primary_qp)]
            for port_name in residual_ports:
                context[port_name] = 0
            return context

        def emit(context: dict[str, int]) -> tuple[int, ...]:
            return tuple(int(context[name]) for name in names)

        structural: list[dict[str, int]] = []
        for bit_depth in depth_values[depth_ports[0]]:
            qps = valid_qps(int(bit_depth))
            if not qps:
                continue
            for primary_qp in unique([qps[0], qps[-1]]):
                for version in version_values:
                    for native420 in native_values:
                        for bit_depths in depth_variants:
                            if int(bit_depths[0]) != int(bit_depth):
                                continue
                            for component in component_values:
                                for unit in unit_values:
                                    structural.append(baseline(
                                        int(component), int(unit),
                                        tuple(int(value) for value in bit_depths),
                                        int(primary_qp), int(version), int(native420),
                                    ))

        thresholds = semantics.get("residual_size_thresholds") or semantics.get("thresholds") or []
        residual_probe_values: list[int] = [0, -1, 1]
        for threshold in thresholds:
            if not isinstance(threshold, dict):
                continue
            for key in ("lower", "upper"):
                if threshold.get(key) is not None:
                    residual_probe_values.append(int(threshold[key]))
        residual_probe_values = unique(residual_probe_values)
        legal_residual_sets = [set(values_for(name)) for name in residual_ports]
        residual_probe_values = [
            value for value in residual_probe_values
            if all(value in legal_values for legal_values in legal_residual_sets)
        ]

        probe_depths = list(itertools.product(*(depth_probe_values[name] for name in depth_ports)))
        probe_contexts: list[dict[str, int]] = []
        for bit_depth in unique([
            min(depth_values[depth_ports[0]]),
            max(depth_values[depth_ports[0]]),
        ]):
            qps = valid_qps(int(bit_depth))
            if not qps:
                continue
            for primary_qp in unique([qps[0], qps[-1]]):
                for version in unique([min(version_values), max(version_values)]):
                    for native420 in unique([min(native_values), max(native_values)]):
                        for bit_depths in probe_depths:
                            if int(bit_depths[0]) != int(bit_depth):
                                continue
                            for component in component_values:
                                for unit in unique([min(unit_values), max(unit_values)]):
                                    probe_contexts.append(baseline(
                                        int(component), int(unit),
                                        tuple(int(value) for value in bit_depths),
                                        int(primary_qp), int(version), int(native420),
                                    ))

        def vectors() -> Iterable[tuple[int, ...]]:
            for context in structural:
                yield emit(context)
            for context in probe_contexts:
                for port_name in residual_ports:
                    for value in residual_probe_values:
                        case = dict(context)
                        case[port_name] = int(value)
                        yield emit(case)

        return vectors(), {
            "kind": "using_midpoint",
            "exhaustive": False,
            "formal_required": True,
            "coverage_mode": "STRUCTURAL_COMPONENT_UNIT_TABLE_AND_RESIDUAL_THRESHOLDS",
            "source": strategy.get("source", "DSC 1.2a section 6.4.4.2"),
            "structural_cases": len(structural),
            "probe_contexts": len(probe_contexts),
            "residual_probe_values": residual_probe_values,
            "table_relation": "qLevelY/qLevelC are selected from Table 6-2 by cpntBitDepth[0] and primaryQp",
            "selected_depth_relation": "cpntBitDepth_selected equals cpntBitDepth[cpnt]",
            "residual_relation": "FindResidualSize threshold classes over the reviewed [-65535,65535] residual domain",
        }

    def estimate_bits_vector_iterator(
        self,
        contract: dict[str, Any],
        input_ports: list[dict[str, Any]],
        values: list[list[int]],
        strategy: dict[str, Any],
    ) -> tuple[Iterable[tuple[int, ...]], dict[str, Any]]:
        """Generate a structural/boundary suite for the fixed DSC DSU estimator.

        The source loops are unrolled to four units and three samples, but the
        residual values and state controls remain too large for a Cartesian
        product.  This iterator therefore covers every source/spec branch,
        every residual-size transition, predicted-size clamps, line-end
        conditions, and pairwise max-size interactions.  The independent Z3
        gate proves the complete finite domain before promotion.
        """
        names = [str(port.get("name")) for port in input_ports]
        by_name = {name: values[index] for index, name in enumerate(names)}

        def require(key: str, fallback: str) -> str:
            name = str(strategy.get(key, fallback))
            if name not in by_name:
                raise RuntimeError(f"estimate-bits strategy port is missing: {name}")
            return name

        units_name = require("units_per_group_port", "units_per_group")
        pixels_name = require("pixels_in_group_port", "pixels_in_group")
        hpos_name = require("hpos_port", "hPos")
        slice_name = require("slice_width_port", "slice_width")
        prev_ich_name = require("prev_ich_selected_port", "prev_ich_selected")
        version_name = require("version_port", "dsc_version_minor")
        native_name = require("native_420_port", "native_420")
        primary_name = require("primary_qp_port", "primary_qp")
        previous_name = require("prev_primary_qp_port", "prev_primary_qp")
        depth_ports = [str(value) for value in strategy.get("component_depth_ports", [])]
        ctype_ports = [str(value) for value in strategy.get("unit_component_ports", [])]
        start_ports = [str(value) for value in strategy.get("unit_start_hpos_ports", [])]
        predicted_ports = [str(value) for value in strategy.get("predicted_size_ports", [])]
        residual_ports = [str(value) for value in strategy.get("residual_ports", [])]
        if any(
            len(group) != 4 or any(name not in by_name for name in group)
            for group in (depth_ports, ctype_ports, start_ports, predicted_ports)
        ):
            raise RuntimeError("estimate-bits strategy requires four component/unit port groups")
        if len(residual_ports) != 12 or any(name not in by_name for name in residual_ports):
            raise RuntimeError("estimate-bits strategy requires twelve residual ports")

        table_bindings = strategy.get("table_bindings", {}) or {}
        table_ports: dict[tuple[str, str], str] = {}
        for port_name, binding in table_bindings.items():
            table_kind = str((binding or {}).get("table", ""))
            qp_port = str((binding or {}).get("qp_port", ""))
            if table_kind not in {"luma", "chroma"} or qp_port not in {primary_name, previous_name}:
                raise RuntimeError("estimate-bits strategy has an invalid table binding")
            if str(port_name) not in by_name:
                raise RuntimeError(f"estimate-bits table port is missing: {port_name}")
            table_ports[(table_kind, qp_port)] = str(port_name)
        if len(table_ports) != 4:
            raise RuntimeError("estimate-bits strategy requires four Table 6-2 bindings")
        tables = strategy.get("tables", {}) or (contract.get("semantics", {}) or {}).get("tables", {}) or {}
        if not tables.get("luma") or not tables.get("chroma"):
            raise RuntimeError("estimate-bits strategy is missing Table 6-2 rows")
        base_depth_name = str(strategy.get("base_bit_depth_port", depth_ports[0]))
        if base_depth_name not in by_name:
            raise RuntimeError("estimate-bits strategy base bit depth port is missing")
        related_specs = strategy.get("bit_depth_ports", {}) or {}

        def unique(raw_values: Iterable[int]) -> list[int]:
            result: list[int] = []
            seen: set[int] = set()
            for raw in raw_values:
                value = int(raw)
                if value not in seen:
                    seen.add(value)
                    result.append(value)
            return result

        def legal(name: str) -> list[int]:
            result = [int(value) for value in by_name[name]]
            if not result:
                raise RuntimeError(f"estimate-bits strategy has no legal values for {name}")
            return result

        def table_row(kind: str, bit_depth: int) -> list[int]:
            raw = tables.get(kind, {}).get(str(bit_depth), tables.get(kind, {}).get(bit_depth))
            if not isinstance(raw, list) or not raw:
                raise RuntimeError(f"estimate-bits table {kind} lacks bpc={bit_depth}")
            return [int(value) for value in raw]

        def related_values(port_name: str, bit_depth: int) -> list[int]:
            spec = related_specs.get(port_name, {}) or {}
            values_by_base = spec.get("values_by_base")
            if isinstance(values_by_base, dict):
                raw = values_by_base.get(str(bit_depth), values_by_base.get(bit_depth))
                if raw is None:
                    raise RuntimeError(f"estimate-bits depth relation lacks base={bit_depth}: {port_name}")
                return [int(value) for value in raw]
            offsets = spec.get("offsets")
            if isinstance(offsets, list):
                return [int(bit_depth) + int(offset) for offset in offsets]
            return legal(port_name)

        def table_value(kind: str, bit_depth: int, qp: int) -> int:
            row = table_row(kind, bit_depth)
            if qp < 0 or qp >= len(row):
                raise RuntimeError(f"estimate-bits QP is outside {kind} table: {qp}")
            return int(row[qp])

        def emit(context: dict[str, int]) -> tuple[int, ...]:
            return tuple(int(context[name]) for name in names)

        all_depth_values = legal(base_depth_name)
        units_values = legal(units_name)
        version_values = legal(version_name)
        native_values = legal(native_name)
        prev_ich_values = legal(prev_ich_name)
        primary_values = legal(primary_name)
        previous_values = legal(previous_name)
        hpos_domain = legal(hpos_name)
        slice_domain = legal(slice_name)

        # With unitStartHPos frozen at zero and pixelsInGroup frozen at three,
        # the source's three sample guards have only four legal masks: all
        # samples active, the first two, the first one, or none.  Representatives
        # for those transitions plus the slice endpoints cover the runtime
        # branch structure; the complete hPos/sliceWidth ranges remain in the
        # formal proof and in the C/RTL differential oracle.
        hpos_min, hpos_max = min(hpos_domain), max(hpos_domain)
        slice_min, slice_max = min(slice_domain), max(slice_domain)
        position_representatives: list[tuple[int, int]] = []
        for hpos, slice_width in [
            (hpos_min, slice_min),
            (slice_min, slice_min),
            (slice_min + 1, slice_min),
            (slice_min + 2, slice_min),
            (hpos_min, slice_max),
            (hpos_max, slice_min),
        ]:
            if hpos in hpos_domain and slice_width in slice_domain:
                pair = (int(hpos), int(slice_width))
                if pair not in position_representatives:
                    position_representatives.append(pair)
        qres_domain = set(legal(residual_ports[0]))
        residual_boundaries: list[int] = [0, -1, 1, min(qres_domain), max(qres_domain)]
        for threshold in (contract.get("semantics", {}) or {}).get("thresholds", []):
            if not isinstance(threshold, dict):
                continue
            for key in ("lower", "upper"):
                if threshold.get(key) is None:
                    continue
                value = int(threshold[key])
                residual_boundaries.extend([value - 1, value, value + 1])
        residual_boundaries = [value for value in unique(residual_boundaries) if value in qres_domain]

        unit_patterns = {
            3: [[0, 1, 2], [1, 2, 0], [0, 0, 0]],
            4: [[0, 1, 2, 3], [3, 2, 1, 0], [0, 2, 1, 3]],
        }
        depth_variants: dict[int, list[tuple[int, int, int, int]]] = {}
        for base in all_depth_values:
            related = [related_values(name, int(base)) for name in depth_ports[1:]]
            depth_variants[int(base)] = [
                tuple([int(base), *values])
                for values in itertools.product(*related)
            ]

        def qps_for(kind: str, bit_depth: int, domain: list[int]) -> list[int]:
            maximum = len(table_row(kind, bit_depth)) - 1
            return [value for value in domain if int(value) <= maximum]

        def baseline(
            base_depth: int,
            depths: tuple[int, int, int, int],
            units: int,
            pattern: list[int],
            primary_qp: int,
            previous_qp: int,
            version: int,
            native420: int,
            prev_ich: int,
            hpos: int,
            slice_width: int,
        ) -> dict[str, int]:
            context = {
                name: int(domain[len(domain) // 2])
                for name, domain in by_name.items()
                if domain
            }
            context.update({
                units_name: int(units),
                pixels_name: int(legal(pixels_name)[0]),
                version_name: int(version),
                native_name: int(native420),
                prev_ich_name: int(prev_ich),
                primary_name: int(primary_qp),
                previous_name: int(previous_qp),
                hpos_name: int(hpos),
                slice_name: int(slice_width),
            })
            for name, value in zip(depth_ports, depths):
                context[name] = int(value)
            for name, value in zip(ctype_ports, pattern):
                context[name] = int(value)
            for name in start_ports:
                context[name] = int(legal(name)[0])
            for name in predicted_ports:
                context[name] = 0
            for name in residual_ports:
                context[name] = 0
            for kind in ("luma", "chroma"):
                for qp_name in (primary_name, previous_name):
                    port_name = table_ports[(kind, qp_name)]
                    context[port_name] = table_value(kind, int(base_depth), int(context[qp_name]))
            return context

        structural: list[dict[str, int]] = []
        for base_depth in all_depth_values:
            base_depth = int(base_depth)
            for depths in depth_variants[base_depth]:
                primary_qps = qps_for("luma", base_depth, primary_values)
                previous_qps = qps_for("luma", base_depth, previous_values)
                qp_probes = unique([primary_qps[0], primary_qps[-1], primary_qps[len(primary_qps) // 2]]) if primary_qps else []
                prev_qp_probes = unique([previous_qps[0], previous_qps[-1], previous_qps[len(previous_qps) // 2]]) if previous_qps else []
                for units in units_values:
                    patterns = unit_patterns.get(int(units), [list(range(min(4, int(units))))])
                    for pattern in patterns:
                        for primary_qp in qp_probes:
                            for previous_qp in prev_qp_probes:
                                for version in version_values:
                                    for native420 in native_values:
                                        for prev_ich in prev_ich_values:
                                            for hpos, slice_width in position_representatives:
                                                structural.append(baseline(
                                                    base_depth, depths, int(units), pattern,
                                                    int(primary_qp), int(previous_qp), int(version),
                                                    int(native420), int(prev_ich), int(hpos), int(slice_width),
                                                ))

        selected = structural[: max(64, min(256, len(structural)))]

        def vectors() -> Iterable[tuple[int, ...]]:
            for context in structural:
                yield emit(context)
                for port_name in predicted_ports:
                    for value in unique([0, 1, 15, 16]):
                        if value in by_name[port_name]:
                            case = dict(context)
                            case[port_name] = value
                            yield emit(case)
            for context in selected:
                for port_name in residual_ports:
                    for value in residual_boundaries:
                        case = dict(context)
                        case[port_name] = int(value)
                        yield emit(case)
                endpoints = [residual_boundaries[0], residual_boundaries[-1]]
                for unit in range(4):
                    lane = residual_ports[unit * 3:(unit + 1) * 3]
                    for first, second in itertools.combinations(lane, 2):
                        for first_value in endpoints:
                            for second_value in endpoints:
                                case = dict(context)
                                case[first] = int(first_value)
                                case[second] = int(second_value)
                                yield emit(case)

        return vectors(), {
            "kind": "estimate_bits",
            "exhaustive": False,
            "formal_required": True,
            "coverage_mode": "STRUCTURAL_PLUS_RESIDUAL_THRESHOLD_AND_PREDICTED_SIZE_BOUNDARIES",
            "source": strategy.get("source", "DSC 1.2a sections 6.5.3.2, 6.6.1, and 6.6.4"),
            "structural_cases": len(structural),
            "boundary_contexts": len(selected),
            "residual_probe_values": residual_boundaries,
            "table_relation": "qLevel ports are Table 6-2 rows selected by cpntBitDepth[0] and current/previous primary QP",
            "unit_relation": "unitsPerGroup is the reviewed {3,4} domain; four source lanes are guarded by the runtime bound",
            "formal_relation": "full finite scalar domains plus Table 6-2, component-depth, and residual-size relations are checked symbolically",
        }

    def ich_decision_vector_iterator(
        self,
        contract: dict[str, Any],
        input_ports: list[dict[str, Any]],
        values: list[list[int]],
        strategy: dict[str, Any],
    ) -> tuple[Iterable[tuple[int, ...]], dict[str, Any]]:
        """Generate structural and boundary vectors for the ICH decision.

        The qLevel ports are frozen outputs of MapQpToQlevel, so vectors keep
        equal QP table entries equal while allowing the composite to be
        exercised over the complete scalar qLevel range.  Large residual,
        sample, and horizontal-position ranges are represented by threshold
        and geometry boundaries here; the formal gate retains the full finite
        domains.
        """
        names = [str(port.get("name")) for port in input_ports]
        by_name = {name: values[index] for index, name in enumerate(names)}

        def require(key: str, fallback: str) -> str:
            name = str(strategy.get(key, fallback))
            if name not in by_name:
                raise RuntimeError(f"ich-decision strategy port is missing: {name}")
            return name

        units_name = require("units_per_group_port", "units_per_group")
        pixels_name = require("pixels_in_group_port", "pixels_in_group")
        hpos_name = require("hpos_port", "hPos")
        slice_name = require("slice_width_port", "slice_width")
        version_name = require("version_port", "dsc_version_minor")
        native_name = require("native_420_port", "native_420")
        prev_ich_name = require("prev_ich_selected_port", "prev_ich_selected")
        primary_name = require("primary_qp_port", "primary_qp")
        previous_name = require("prev_primary_qp_port", "prev_primary_qp")
        delta_name = require("somewhat_flat_qp_delta_port", "somewhat_flat_qp_delta")
        flatness_name = require("flatness_det_thresh_port", "flatness_det_thresh")
        adj_name = require("adj_predicted_size_port", "adj_predicted_size")
        alt_pfx_name = require("alt_pfx_port", "alt_pfx")
        alt_size_name = require("alt_size_to_generate_port", "alt_size_to_generate")
        ich_indices_name = require("ich_indices_in_group_port", "ich_indices_in_group")
        num_components_name = require("num_components_port", "num_components")
        depth_ports = [str(value) for value in strategy.get("component_depth_ports", [])]
        ctype_ports = [str(value) for value in strategy.get("unit_component_ports", [])]
        start_ports = [str(value) for value in strategy.get("unit_start_hpos_ports", [])]
        predicted_ports = [str(value) for value in strategy.get("predicted_size_ports", [])]
        max_error_ports = [str(value) for value in strategy.get("max_error_ports", [])]
        max_mid_error_ports = [str(value) for value in strategy.get("max_mid_error_ports", [])]
        max_ich_error_ports = [str(value) for value in strategy.get("max_ich_error_ports", [])]
        residual_ports = [str(value) for value in strategy.get("residual_ports", [])]
        if any(
            len(group) != 4 or any(name not in by_name for name in group)
            for group in (depth_ports, ctype_ports, start_ports, predicted_ports,
                          max_error_ports, max_mid_error_ports, max_ich_error_ports)
        ):
            raise RuntimeError("ich-decision strategy requires four lane groups")
        if len(residual_ports) != 12 or any(name not in by_name for name in residual_ports):
            raise RuntimeError("ich-decision strategy requires twelve residual ports")
        qlevel_ports = strategy.get("qlevel_ports", {}) or {}
        qlevel_names = {
            key: str(qlevel_ports.get(key, ""))
            for key in ("luma_primary", "chroma_primary", "luma_previous",
                        "chroma_previous", "luma_flat", "chroma_flat")
        }
        if any(name not in by_name for name in qlevel_names.values()):
            raise RuntimeError("ich-decision strategy requires six qLevel ports")
        orig_ports = strategy.get("orig_ports_by_component", {}) or {}
        sample_names = {
            component: [str(value) for value in orig_ports.get(str(component), orig_ports.get(component, []))]
            for component in range(4)
        }
        if any(len(group) != 7 or any(name not in by_name for name in group) for group in sample_names.values()):
            raise RuntimeError("ich-decision strategy requires seven taps per component")

        def unique(raw_values: Iterable[int]) -> list[int]:
            result: list[int] = []
            seen: set[int] = set()
            for raw in raw_values:
                value = int(raw)
                if value not in seen:
                    seen.add(value)
                    result.append(value)
            return result

        def domain(name: str) -> list[int]:
            result = [int(value) for value in by_name[name]]
            if not result:
                raise RuntimeError(f"ich-decision strategy has no legal values for {name}")
            return result

        def probes(name: str, preferred: Iterable[int] = ()) -> list[int]:
            legal_values = domain(name)
            legal_set = set(legal_values) if len(legal_values) <= 200000 else None
            raw = [min(legal_values), max(legal_values), legal_values[len(legal_values) // 2], *preferred]
            if len(legal_values) > 2:
                raw.extend([legal_values[1], legal_values[-2]])
            if legal_set is not None:
                return unique(value for value in raw if value in legal_set)
            lower, upper = min(legal_values), max(legal_values)
            return unique(value for value in raw if lower <= value <= upper)

        def set_if_legal(context: dict[str, int], name: str, value: int) -> None:
            legal_values = by_name[name]
            if value in legal_values:
                context[name] = int(value)

        def selected_qlevel(component: int, raw_luma: int, raw_chroma: int,
                            version: int, native420: int, depths: tuple[int, int, int, int]) -> int:
            if component % 3 == 0 or (native420 != 0 and component == 1):
                return int(raw_luma)
            if version == 2 and depths[0] == depths[1] and raw_chroma > 0:
                return int(raw_chroma) - 1
            return int(raw_chroma)

        def qlevels_legal(context: dict[str, int], depths: tuple[int, int, int, int]) -> bool:
            version = int(context[version_name])
            native420 = int(context[native_name])
            for raw_luma, raw_chroma in (
                (context[qlevel_names["luma_primary"]], context[qlevel_names["chroma_primary"]]),
                (context[qlevel_names["luma_previous"]], context[qlevel_names["chroma_previous"]]),
                (context[qlevel_names["luma_flat"]], context[qlevel_names["chroma_flat"]]),
            ):
                for component, depth in enumerate(depths):
                    if selected_qlevel(component, raw_luma, raw_chroma, version, native420, depths) > depth:
                        return False
            return True

        def qps_consistent(context: dict[str, int]) -> bool:
            primary = int(context[primary_name])
            previous = int(context[previous_name])
            delta = int(context[delta_name])
            flat = max(primary - delta, 0)
            pairs = [
                (primary, previous, "primary", "previous"),
                (primary, flat, "primary", "flat"),
                (previous, flat, "previous", "flat"),
            ]
            for left_qp, right_qp, left, right in pairs:
                if left_qp != right_qp:
                    continue
                if context[qlevel_names[f"luma_{left}"]] != context[qlevel_names[f"luma_{right}"]]:
                    return False
                if context[qlevel_names[f"chroma_{left}"]] != context[qlevel_names[f"chroma_{right}"]]:
                    return False
            return True

        def emit(context: dict[str, int]) -> tuple[int, ...]:
            return tuple(int(context[name]) for name in names)

        default_values = {
            name: int(domain(name)[len(domain(name)) // 2])
            for name in names
        }
        for name in start_ports:
            default_values[name] = int(domain(name)[0])
        for name in residual_ports:
            default_values[name] = 0
        for names_group in (max_error_ports, max_mid_error_ports, max_ich_error_ports):
            for name in names_group:
                default_values[name] = 0
        for name in predicted_ports:
            default_values[name] = 0
        for component in range(4):
            for name in sample_names[component]:
                default_values[name] = 0

        depth_variants = [
            tuple(int(value) for value in values)
            for values in (
                (8, 8, 8, 8),
                (10, 11, 10, 10),
                (12, 13, 12, 12),
                (16, 16, 16, 16),
                (16, 17, 16, 17),
            )
            if all(values[index] in by_name[depth_ports[index]] for index in range(4))
        ]
        if not depth_variants:
            depth_variants = [tuple(int(domain(name)[0]) for name in depth_ports)]
        qlevel_profiles = [
            (0, 0, 0, 0, 0, 0),
            (1, 2, 3, 4, 5, 6),
            (8, 8, 8, 8, 8, 8),
            (16, 16, 16, 16, 16, 16),
            (0, 16, 4, 12, 0, 16),
        ]
        qlevel_profiles = [
            profile for profile in qlevel_profiles
            if all(profile[index] in by_name[qlevel_names[key]]
                   for index, key in enumerate(("luma_primary", "chroma_primary",
                                                "luma_previous", "chroma_previous",
                                                "luma_flat", "chroma_flat")))
        ]
        if not qlevel_profiles:
            qlevel_profiles = [tuple(0 for _ in range(6))]

        structural: list[dict[str, int]] = []
        primary_values = unique([min(domain(primary_name)), 0, 16, max(domain(primary_name))])
        previous_values = unique([min(domain(previous_name)), 0, 16, max(domain(previous_name))])
        hpos_values = unique([min(domain(hpos_name)), 0, 1, 2, 5, max(domain(hpos_name))])
        slice_values = unique([min(domain(slice_name)), 1, 2, 3, 8, max(domain(slice_name))])
        flatness_values = probes(flatness_name, [2, 4, 8, 32, 512])
        unit_patterns = {
            3: ((0, 1, 2, 0), (2, 1, 0, 0), (0, 0, 0, 0)),
            4: ((0, 1, 2, 3), (3, 2, 1, 0), (0, 2, 1, 3)),
        }
        for depths in depth_variants:
            for primary in primary_values:
                for previous in previous_values:
                    for version in probes(version_name):
                        for native420 in probes(native_name):
                            for units in probes(units_name):
                                patterns = unit_patterns.get(int(units), ((0, 1, 2, 3),))
                                for pattern in patterns:
                                    if any(pattern[index] not in by_name[ctype_ports[index]] for index in range(4)):
                                        continue
                                    for num_components in probes(num_components_name):
                                        for prev_ich in probes(prev_ich_name):
                                            for hpos in hpos_values:
                                                for slice_width in slice_values:
                                                    for profile in qlevel_profiles:
                                                        if len(structural) >= 12000:
                                                            break
                                                        context = dict(default_values)
                                                        context.update({
                                                            primary_name: int(primary),
                                                            previous_name: int(previous),
                                                            version_name: int(version),
                                                            native_name: int(native420),
                                                            units_name: int(units),
                                                            pixels_name: int(domain(pixels_name)[0]),
                                                            num_components_name: int(num_components),
                                                            prev_ich_name: int(prev_ich),
                                                            hpos_name: int(hpos),
                                                            slice_name: int(slice_width),
                                                            flatness_name: int(flatness_values[0]),
                                                            delta_name: int(domain(delta_name)[0]),
                                                            adj_name: int(probes(adj_name, [0, 1, 8, 16])[0]),
                                                            alt_pfx_name: int(probes(alt_pfx_name, [0, 1, 8])[0]),
                                                            alt_size_name: int(probes(alt_size_name, [1, 8, 17])[0]),
                                                            ich_indices_name: int(probes(ich_indices_name, [0, 1, 3, 6])[0]),
                                                        })
                                                        for qlevel_name, qlevel_value in zip(qlevel_names.values(), profile):
                                                            context[qlevel_name] = int(qlevel_value)
                                                        for index, port in enumerate(ctype_ports):
                                                            context[port] = int(pattern[index])
                                                        if qlevels_legal(context, depths) and qps_consistent(context):
                                                            for index, port in enumerate(depth_ports):
                                                                context[port] = int(depths[index])
                                                            structural.append(context)

        residual_values = [0, -1, 1, -2, 2, -4, 3, -8, 7, -16, 15,
                           -32768, 32767, -65535, 65535]
        for threshold in (contract.get("semantics", {}) or {}).get("thresholds", []):
            if not isinstance(threshold, dict):
                continue
            for key in ("lower", "upper"):
                if threshold.get(key) is not None:
                    residual_values.extend([int(threshold[key]), int(threshold[key]) - 1, int(threshold[key]) + 1])
        residual_values = [value for value in unique(residual_values) if value in set(domain(residual_ports[0]))]
        error_values = [value for value in (0, 1, 2, 16, 255, 65535)
                        if value in by_name[max_error_ports[0]]]
        orig_values = [value for value in (0, 1, 2, 4, 8, 16, 32, 255, 65535)
                       if value in by_name[sample_names[0][0]]]
        structural_probe = structural[: min(len(structural), 128)]

        def vectors() -> Iterable[tuple[int, ...]]:
            seen: set[tuple[int, ...]] = set()

            def yield_case(context: dict[str, int]) -> Iterable[tuple[int, ...]]:
                vector = emit(context)
                if vector not in seen:
                    seen.add(vector)
                    yield vector

            for context in structural:
                yield from yield_case(context)
            for context in structural_probe:
                for port_name in residual_ports:
                    for value in residual_values:
                        case = dict(context)
                        case[port_name] = int(value)
                        yield from yield_case(case)
                for port_name in max_error_ports + max_mid_error_ports + max_ich_error_ports:
                    for value in error_values:
                        case = dict(context)
                        case[port_name] = int(value)
                        yield from yield_case(case)
                for component in range(4):
                    taps = sample_names[component]
                    for offset, port_name in enumerate(taps):
                        for value in orig_values:
                            case = dict(context)
                            case[port_name] = int(value)
                            yield from yield_case(case)
                for threshold in flatness_values:
                    case = dict(context)
                    case[flatness_name] = int(threshold)
                    yield from yield_case(case)

        return vectors(), {
            "kind": "ich_decision",
            "exhaustive": False,
            "formal_required": True,
            "coverage_mode": "STRUCTURAL_PLUS_RESIDUAL_ERROR_AND_ORIGINAL_PIXEL_BOUNDARIES",
            "source": strategy.get("source", "DSC 1.2a section 6.5.3.2 / MN_ENC_ICH_MODE_SELECT"),
            "structural_cases": len(structural),
            "boundary_contexts": len(structural_probe),
            "residual_probe_values": residual_values,
            "error_probe_values": error_values,
            "qlevel_relation": "qLevel ports are frozen MapQpToQlevel outputs; equal QP table indices must carry equal values",
            "unit_relation": "unitsPerGroup is the reviewed {3,4} domain and source loops are unrolled to four lanes",
            "formal_relation": "full finite scalar domains plus qLevel/depth and equal-QP witness relations are checked symbolically",
        }

    def flatness_window_vector_iterator(
        self,
        contract: dict[str, Any],
        input_ports: list[dict[str, Any]],
        values: list[list[int]],
        strategy: dict[str, Any],
    ) -> tuple[Iterable[tuple[int, ...]], dict[str, Any]]:
        """Generate a bounded, spec-structured suite for flatness windows.

        The value space contains up to 28 independent pixel taps and cannot be
        exhaustively enumerated.  This iterator therefore covers every
        structural branch, exact Table 6-2 qLevel relation, line-end cases,
        per-tap boundaries, and pairwise tap interactions.  The independent
        formal gate is required before the result can enter the stable library.
        """
        names = [str(port.get("name")) for port in input_ports]
        by_name = {name: values[index] for index, name in enumerate(names)}
        semantics = contract.get("semantics", {}) or {}
        window = semantics.get("window_spec", {}) or {}
        bindings = semantics.get("bindings", {}) or {}
        tables = semantics.get("tables", {}) or {}
        luma_tables = tables.get("luma", {}) or {}
        chroma_tables = tables.get("chroma", {}) or {}

        def require_binding(key: str, fallback: str) -> str:
            name = str(bindings.get(key, fallback))
            if name not in by_name:
                raise RuntimeError(f"flatness window strategy port is missing: {name}")
            return name

        hpos_name = require_binding("hpos_port", "hPos")
        bpc_name = require_binding("bits_per_component_port", "bits_per_component")
        primary_qp_name = require_binding("primary_qp_port", "primary_qp")
        num_components_name = require_binding("num_components_port", "num_components")
        slice_width_name = require_binding("slice_width_port", "slice_width")
        flatness_thresh_name = require_binding("flatness_det_thresh_port", "flatness_det_thresh")
        flatness_delta_name = require_binding("somewhat_flat_qp_delta_port", "somewhat_flat_qp_delta")
        native420_name = require_binding("native_420_port", "native_420")
        version_name = require_binding("dsc_version_minor_port", "dsc_version_minor")
        cpnt0_name = require_binding("cpnt_bit_depth_0_port", "cpnt_bit_depth_0")
        cpnt1_name = require_binding("cpnt_bit_depth_1_port", "cpnt_bit_depth_1")

        sample_by_component = window.get("sample_ports_by_component", {})
        if not isinstance(sample_by_component, dict):
            raise RuntimeError("flatness window strategy is missing sample_ports_by_component")
        sample_ports: list[str] = []
        for component in range(4):
            raw = sample_by_component.get(str(component), sample_by_component.get(component, []))
            taps = [str(value) for value in raw]
            if len(taps) != 7 or any(tap not in by_name for tap in taps):
                raise RuntimeError(f"flatness window strategy has incomplete component {component} taps")
            sample_ports.extend(taps)

        def unique(raw_values: Iterable[int]) -> list[int]:
            result: list[int] = []
            seen: set[int] = set()
            for raw in raw_values:
                value = int(raw)
                if value not in seen:
                    seen.add(value)
                    result.append(value)
            return result

        def probes(port_name: str, explicit_key: str, fallback: list[int]) -> list[int]:
            legal = [int(value) for value in by_name[port_name]]
            if len(legal) <= 64:
                return legal
            requested = [int(value) for value in strategy.get(explicit_key, [])]
            legal_set = set(legal)
            values_for_probe = [value for value in requested if value in legal_set]
            lower, upper = min(legal), max(legal)
            values_for_probe.extend(value for value in fallback if lower <= value <= upper)
            values_for_probe.extend([lower, lower + 1, upper - 1, upper])
            return sorted(set(value for value in values_for_probe if value in legal_set))

        hpos_values = probes(
            hpos_name,
            "hpos_probe_values",
            [0, 1, 2, 3, 4, 5, 6, 8, 16, 31, 63, 127, 255, 1023, 4095, 65534],
        )
        slice_width_values = probes(
            slice_width_name,
            "slice_width_probe_values",
            [1, 2, 3, 4, 5, 6, 7, 8, 16, 31, 63, 127, 255, 1024, 4096, 65535],
        )
        bpc_values = [int(value) for value in by_name[bpc_name]]
        num_components_values = [int(value) for value in by_name[num_components_name]]
        native_values = [int(value) for value in by_name[native420_name]]
        version_values = [int(value) for value in by_name[version_name]]
        delta_values = [int(value) for value in by_name[flatness_delta_name]]
        if not delta_values:
            raise RuntimeError("flatness window strategy has no qP-delta values")

        def table_value(table: dict[str, Any], bit_depth: int, qp: int) -> int:
            row = table.get(str(bit_depth), table.get(bit_depth))
            if not isinstance(row, list) or not 0 <= qp < len(row):
                raise RuntimeError(f"flatness window table lacks bpc={bit_depth}, qp={qp}")
            return int(row[qp])

        def adjusted_qp(primary_qp: int, delta: int) -> int:
            return max(int(primary_qp) - int(delta), 0)

        def valid_primary_qps(bit_depth: int) -> list[int]:
            luma_row = luma_tables.get(str(bit_depth), luma_tables.get(bit_depth, []))
            chroma_row = chroma_tables.get(str(bit_depth), chroma_tables.get(bit_depth, []))
            max_adjusted = min(len(luma_row), len(chroma_row)) - 1
            if max_adjusted < 0:
                raise RuntimeError(f"flatness window table lacks bpc={bit_depth}")
            return [
                int(primary)
                for primary in by_name[primary_qp_name]
                if any(adjusted_qp(int(primary), delta) <= max_adjusted for delta in delta_values)
            ]

        depth_legal = [int(value) for value in by_name[cpnt0_name]]
        depth_legal_1 = [int(value) for value in by_name[cpnt1_name]]
        depth_probes = unique(
            [min(depth_legal), max(depth_legal), 8, 10, 12, 14, 16]
        )
        depth_probes_1 = unique(
            [min(depth_legal_1), max(depth_legal_1), 8, 10, 12, 14, 16]
        )
        depth_probes = [value for value in depth_probes if value in set(depth_legal)]
        depth_probes_1 = [value for value in depth_probes_1 if value in set(depth_legal_1)]

        # The structural suite is deliberately a covering array, not the
        # Cartesian product of every legal scalar probe.  The full scalar
        # domains are still enforced by the independent formal proof; the
        # concrete suite needs only representative values for every branch,
        # line-end class, qLevel table edge, and bit-depth equality relation.
        def structural_probes(port_values: list[int], requested: Iterable[int]) -> list[int]:
            legal = set(int(value) for value in port_values)
            return unique(value for value in requested if int(value) in legal)

        structural_hpos_values = structural_probes(
            hpos_values,
            [min(hpos_values), 0, 1, 2, 3, 6, max(hpos_values)],
        )
        structural_slice_width_values = structural_probes(
            slice_width_values,
            [min(slice_width_values), 1, 2, 3, 4, 7, max(slice_width_values)],
        )
        structural_depth_probes = structural_probes(
            depth_legal,
            [min(depth_legal), 8, 10, 12, 14, 16, max(depth_legal)],
        )
        structural_depth_probes_1 = structural_probes(
            depth_legal_1,
            [min(depth_legal_1), 8, 9, 10, 11, 16, 17, max(depth_legal_1)],
        )

        def sample_boundaries(bit_depth: int) -> list[int]:
            maximum = (1 << int(bit_depth)) - 1
            midpoint = maximum // 2
            return unique([0, 1, midpoint - 1, midpoint, midpoint + 1, maximum - 1, maximum])

        def baseline(
            bit_depth: int,
            primary_qp: int,
            delta: int,
            native420: int,
            version: int,
            cpnt0: int,
            cpnt1: int,
            num_components: int,
            hpos: int,
            slice_width: int,
        ) -> dict[str, int]:
            context = {
                name: int(domain[len(domain) // 2])
                for name, domain in by_name.items()
                if domain
            }
            context.update({
                bpc_name: int(bit_depth),
                primary_qp_name: int(primary_qp),
                flatness_delta_name: int(delta),
                native420_name: int(native420),
                version_name: int(version),
                cpnt0_name: int(cpnt0),
                cpnt1_name: int(cpnt1),
                num_components_name: int(num_components),
                hpos_name: int(hpos),
                slice_width_name: int(slice_width),
                flatness_thresh_name: 2 << (int(bit_depth) - 8),
            })
            maximum = (1 << int(bit_depth)) - 1
            for tap in sample_ports:
                context[tap] = maximum // 2
            return context

        def emit(context: dict[str, int]) -> tuple[int, ...]:
            return tuple(int(context[name]) for name in names)

        structural: list[dict[str, int]] = []
        for bit_depth in bpc_values:
            qps = valid_primary_qps(bit_depth)
            primary_qp_probes = unique(
                qps[index]
                for index in [0, min(4, len(qps) - 1), max(0, len(qps) - 2), len(qps) - 1]
            )
            for primary_qp in primary_qp_probes:
                for delta in delta_values:
                    if adjusted_qp(primary_qp, delta) > min(
                        len(luma_tables.get(str(bit_depth), [])),
                        len(chroma_tables.get(str(bit_depth), [])),
                    ) - 1:
                        continue
                    for native420 in native_values:
                        for version in version_values:
                            for cpnt0 in structural_depth_probes:
                                for cpnt1 in structural_depth_probes_1:
                                    for num_components in num_components_values:
                                        for hpos in structural_hpos_values:
                                            for slice_width in structural_slice_width_values:
                                                structural.append(baseline(
                                                    bit_depth, primary_qp, delta, native420, version,
                                                    cpnt0, cpnt1, num_components, hpos, slice_width,
                                                ))

        def vectors() -> Iterable[tuple[int, ...]]:
            for context in structural:
                yield emit(context)

            selected_contexts: list[dict[str, int]] = []
            for bit_depth in bpc_values:
                qps = valid_primary_qps(bit_depth)
                if not qps:
                    continue
                for primary_qp in unique([qps[0], qps[-1]]):
                    for delta in delta_values:
                        if adjusted_qp(primary_qp, delta) >= len(luma_tables.get(str(bit_depth), [])):
                            continue
                        for native420 in unique([min(native_values), max(native_values)]):
                            for version in unique([min(version_values), max(version_values)]):
                                for num_components in unique([min(num_components_values), max(num_components_values)]):
                                    for hpos in unique([min(hpos_values), max(hpos_values), 0, 1, 2, 3]):
                                        for slice_width in unique([min(slice_width_values), max(slice_width_values), 1, 2, 3, 4]):
                                            selected_contexts.append(baseline(
                                                bit_depth, primary_qp, delta, native420, version,
                                    structural_depth_probes[0], structural_depth_probes_1[-1], num_components,
                                                hpos, slice_width,
                                            ))

            for context in selected_contexts:
                bit_depth = int(context[bpc_name])
                for tap in sample_ports:
                    for value in sample_boundaries(bit_depth):
                        case = dict(context)
                        case[tap] = int(value)
                        yield emit(case)

            pair_contexts = selected_contexts[: max(1, min(32, len(selected_contexts)))]
            for context in pair_contexts:
                bit_depth = int(context[bpc_name])
                endpoint_values = sample_boundaries(bit_depth)
                endpoints = [endpoint_values[0], endpoint_values[-1]]
                for component in range(4):
                    taps = [str(value) for value in sample_by_component[str(component)]]
                    for first, second in itertools.combinations(taps, 2):
                        for first_value in endpoints:
                            for second_value in endpoints:
                                case = dict(context)
                                case[first] = first_value
                                case[second] = second_value
                                yield emit(case)

        return vectors(), {
            "kind": "flatness_window",
            "exhaustive": False,
            "formal_required": True,
            "coverage_mode": "STRUCTURAL_PLUS_BOUNDARY_AND_PAIRWISE_FLATNESS_TAPS",
            "source": strategy.get("source", "DSC 1.2a section 6.8.5.1 and Figure 6-19"),
            "structural_cases": len(structural),
            "sample_ports": sample_ports,
            "sample_ports_by_component": {
                str(component): [str(value) for value in sample_by_component[str(component)]]
                for component in range(4)
            },
            "hpos_probe_values": hpos_values,
            "slice_width_probe_values": slice_width_values,
            "table_relation": "primary_qp - somewhat_flat_qp_delta indexes the normative Table 6-2 row",
            "legal_relation": "flatness_det_thresh = 2 << (bits_per_component - 8); taps are bounded original samples",
        }

    def legal_vector_iterator(self, contract: dict[str, Any], input_ports: list[dict[str, Any]],
                              values: list[list[int]]) -> tuple[Iterable[tuple[int, ...]], dict[str, Any]]:
        """Return legal vectors, including reviewed conditional domains.

        Flattened state dependencies are represented as selected scalar values
        in the frozen interface.  When the contract supplies a reviewed
        qlevel-by-bit-depth map and a conditional leftRecon domain, enumerate
        that relation instead of the invalid Cartesian product.
        """
        names = [str(port.get("name")) for port in input_ports]
        semantics = contract.get("semantics", {}) or {}
        table_strategy = semantics.get("legal_vector_strategy") or semantics.get("vector_strategy")
        if isinstance(table_strategy, dict) and table_strategy.get("kind") == "qp_table":
            return self.qp_table_vector_iterator(contract, input_ports, values, table_strategy)
        if isinstance(table_strategy, dict) and table_strategy.get("kind") == "table_lookup":
            return self.table_lookup_vector_iterator(contract, input_ports, values, table_strategy)
        if isinstance(table_strategy, dict) and table_strategy.get("kind") == "windowed_boundary":
            return self.windowed_boundary_vector_iterator(contract, input_ports, values, table_strategy)
        if isinstance(table_strategy, dict) and table_strategy.get("kind") == "flatness_window":
            return self.flatness_window_vector_iterator(contract, input_ports, values, table_strategy)
        if isinstance(table_strategy, dict) and table_strategy.get("kind") == "using_midpoint":
            return self.using_midpoint_vector_iterator(contract, input_ports, values, table_strategy)
        if isinstance(table_strategy, dict) and table_strategy.get("kind") == "estimate_bits":
            return self.estimate_bits_vector_iterator(contract, input_ports, values, table_strategy)
        if isinstance(table_strategy, dict) and table_strategy.get("kind") == "ich_decision":
            return self.ich_decision_vector_iterator(contract, input_ports, values, table_strategy)
        normalized = {re.sub(r"[^a-z0-9]", "", name.lower()): name for name in names}
        bit_depth_name = normalized.get("cpntbitdepth")
        qlevel_name = normalized.get("qlevel")
        left_recon_name = normalized.get("leftrecon")
        qlevel_map = semantics.get("qlevel_max_by_cpnt_bit_depth", {}) or {}
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
        vector_strategy = (contract.get("semantics", {}) or {}).get("legal_vector_strategy") or (contract.get("semantics", {}) or {}).get("vector_strategy") or {}
        write_json(artifact / "legal-domain.json", {
            "schema_version": 1,
            "complete": bool(vector_strategy.get("exhaustive", True)) and all(
                item["domain"].get("range") or item["domain"].get("values")
                for item in domains if item["role"] != "return_value"
            ),
            "ports": domains,
            "proof_basis": "exact spec/table plus reviewed runtime range override" if vector_strategy.get("exhaustive", True) else "reviewed spec-domain differential strategy; not a legal-domain proof",
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
                "formal_proofs",
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
        with self.state_lock:
            self.generator_invocations += 1
        telemetry = read_json(output_dir / "telemetry.json", {}) or {}
        with self.state_lock:
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
            "proof_complete": bool(vector_strategy.get("exhaustive", True)),
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

    def reuse_existing_shards(
        self,
        contract: dict[str, Any],
        artifact: pathlib.Path,
    ) -> dict[str, Any] | None:
        """Reuse a verified vector partition during proof-only iterations.

        This is opt-in because a normal run should materialize its own
        vectors.  When enabled, the prior domain receipt, input-port order,
        strategy, and every shard line count must match the current contract
        before any C/RTL process consumes the files.
        """
        enabled = os.environ.get("DSC_CICD_REUSE_SHARDS", "").lower() in {"1", "true", "yes"}
        if not enabled:
            return None
        prior = read_json(artifact / "unit-receipt.json", {}) or {}
        domain = prior.get("domain") if isinstance(prior, dict) else None
        if not isinstance(domain, dict) or not domain.get("shards"):
            return None
        inputs = [
            port for port in contract.get("interface", {}).get("ports", [])
            if port.get("direction") == "input"
        ]
        input_names = [str(port.get("name")) for port in inputs]
        if domain.get("input_ports") != input_names:
            return None
        values = [self.port_domain(port) for port in inputs]
        _, current_strategy = self.legal_vector_iterator(contract, inputs, values)
        if canonical(domain.get("vector_strategy", {})) != canonical(current_strategy):
            return None
        shards: list[dict[str, Any]] = []
        total = 0
        for prior_shard in domain.get("shards", []):
            path = artifact / str(prior_shard.get("path", ""))
            if not path.is_file():
                return None
            count = self.count_lines(path)
            if count <= 0 or count != int(prior_shard.get("vectors", -1)):
                return None
            shard = copy.deepcopy(prior_shard)
            shard["vectors"] = count
            shards.append(shard)
            total += count
        if total != int(domain.get("total_vectors", -1)):
            return None
        reused = copy.deepcopy(domain)
        reused["shards"] = shards
        reused["total_vectors"] = total
        reused["execution_status"] = "REUSED_VERIFIED_SHARDS"
        return reused

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
            object_path = build_dir / (source.stem + ".o")
            extra = ["-Dmain=dsc_cicd_original_main"] if source.name == "codec_main.c" else []
            result = self.run_process(
                [clang, "-std=c99", "-O0", "-g", "-I", str(source_dir)]
                + extra
                + ["-c", str(source), "-o", str(object_path)],
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
            "compiled_translation_units": [path.name for path in source_files],
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

    def formal_verify(self, contract: dict[str, Any], artifact: pathlib.Path,
                      candidate: dict[str, Any]) -> dict[str, Any]:
        """Run the independent AST/Z3 proof for a reviewed bounded window.

        Concrete window coverage remains intentionally bounded.  The formal
        helper is invoked only for contracts that explicitly declare the
        reviewed semantic adapter; other contracts retain their normal
        exhaustive-differential path.
        """
        semantics = contract.get("semantics", {}) or {}
        strategy = semantics.get("legal_vector_strategy") or {}
        if strategy.get("kind") not in {"windowed_boundary", "flatness_window", "using_midpoint", "estimate_bits", "ich_decision"}:
            return {
                "schema_version": 1,
                "status": "NOT_APPLICABLE",
                "proof_complete": False,
                "reason": "formal AST proof is only enabled for reviewed windowed_boundary, flatness_window, using_midpoint, estimate_bits, or ich_decision contracts",
            }
        helper = self.root / "tools" / "formal_rtl.py"
        if not helper.is_file():
            return {
                "schema_version": 1,
                "status": "INFRASTRUCTURE_FAILURE",
                "proof_complete": False,
                "error": "formal_rtl.py is missing",
            }
        candidate_path = artifact / str(candidate["path"])
        output = artifact / "formal" / f"{safe_identifier(str(candidate['candidate']))}.json"
        timeout_ms = int(os.environ.get("DSC_CICD_FORMAL_TIMEOUT_MS", "180000"))
        verilator = self.input_facts["tools"].get("verilator") or "verilator"
        command = [
            sys.executable,
            str(helper),
            "--contract",
            str(artifact / "locked-contract.json"),
            "--candidate",
            str(candidate_path),
            "--output",
            str(output),
            "--verilator",
            str(verilator),
            "--timeout-ms",
            str(timeout_ms),
        ]
        process = self.run_process(
            command,
            cwd=artifact,
            timeout=max(60, int(timeout_ms / 1000) + 30),
        )
        receipt = read_json(output, {}) or {}
        if not isinstance(receipt, dict):
            receipt = {}
        receipt["execution_status"] = "EXECUTED_NOW"
        receipt["command"] = process
        if process.get("returncode") == 124:
            receipt["status"] = "UNKNOWN"
            receipt["proof_complete"] = False
            receipt.setdefault("reason", "formal proof timed out")
        elif process.get("returncode") != 0 and receipt.get("status") not in {"COUNTEREXAMPLE", "UNKNOWN"}:
            receipt["status"] = "INFRASTRUCTURE_FAILURE"
            receipt["proof_complete"] = False
            receipt.setdefault("error", "formal proof command failed")
        write_json(output, receipt)
        receipt["receipt"] = str(output.relative_to(artifact))
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
        shard_info = self.reuse_existing_shards(contract, artifact) or self.make_shards(contract, artifact)
        oracle_receipt = self.compile_c_oracle(contract, artifact)
        unit_receipt: dict[str, Any] = {
            "schema_version": 2,
            "execution_status": "EXECUTED_NOW",
            "contract_id": contract_id(contract),
            "domain": shard_info,
            "oracle_compile": oracle_receipt,
            "compile_once": [],
            "candidates": [],
            "formal_proofs": [],
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
                status = (
                    "EXHAUSTIVE_EQUIVALENT"
                    if shard_info.get("vector_strategy", {}).get("exhaustive", True)
                    else "DIFFERENTIAL_PASS"
                )
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
            formal = self.formal_verify(contract, artifact, candidate)
            candidate_result["formal_proof"] = {
                "status": formal.get("status"),
                "proof_complete": formal.get("proof_complete", False),
                "receipt": formal.get("receipt"),
                "counterexample": formal.get("counterexample"),
                "reason": formal.get("reason") or formal.get("error"),
            }
            unit_receipt["formal_proofs"].append({
                "candidate": candidate["candidate"],
                "status": formal.get("status"),
                "proof_complete": formal.get("proof_complete", False),
                "receipt": formal.get("receipt"),
            })
            if status == "DIFFERENTIAL_PASS" and formal.get("status") == "PASS":
                status = "FORMAL_EQUIVALENT"
                candidate_result["verification_status"] = status
            elif status == "DIFFERENTIAL_PASS" and formal.get("status") == "COUNTEREXAMPLE":
                status = "COUNTEREXAMPLE"
                candidate_result["verification_status"] = status
                candidate_result["formal_counterexample"] = formal.get("counterexample")
            elif status == "DIFFERENTIAL_PASS" and formal.get("status") in {
                "INFRASTRUCTURE_FAILURE", "UNKNOWN"
            }:
                status = "INFRASTRUCTURE_FAILURE" if formal.get("status") == "INFRASTRUCTURE_FAILURE" else "UNPROVED"
                candidate_result["verification_status"] = status
            unit_receipt["candidates"].append(candidate_result)
            if smallest and unit_receipt.get("smallest_counterexample") is None:
                unit_receipt["smallest_counterexample"] = smallest
        promoted = next(
            (item for item in unit_receipt["candidates"] if item["verification_status"] == "FORMAL_EQUIVALENT"),
            None,
        ) or next(
            (item for item in unit_receipt["candidates"] if item["verification_status"] == "EXHAUSTIVE_EQUIVALENT"),
            None,
        )
        unit_receipt["verification_status"] = (
            "FORMAL_EQUIVALENT" if promoted and promoted["verification_status"] == "FORMAL_EQUIVALENT"
            else "EXHAUSTIVE_EQUIVALENT" if promoted else (
            "COUNTEREXAMPLE" if any(item["verification_status"] == "COUNTEREXAMPLE" for item in unit_receipt["candidates"])
            else "DIFFERENTIAL_PASS" if unit_receipt["candidates"] and all(
                item["verification_status"] == "DIFFERENTIAL_PASS"
                for item in unit_receipt["candidates"]
            )
            else "UNPROVED"
            )
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

    def write_flatness_overlay_sources(
        self,
        contract: dict[str, Any],
        source_dir: pathlib.Path,
        module: str,
        candidate_sv: pathlib.Path,
    ) -> dict[str, pathlib.Path]:
        """Write the caller overlay for a reviewed flatness-window leaf."""
        ports = contract.get("interface", {}).get("ports", [])
        inputs = [port for port in ports if port.get("direction") == "input"]
        output = next(
            port for port in ports if port.get("direction") == "output"
        )
        semantics = contract.get("semantics", {}) or {}
        bindings = semantics.get("bindings", {}) or {}
        window = semantics.get("window_spec", {}) or {}
        parameters = self.function_parameters(contract)
        if not parameters:
            raise RuntimeError("flatness overlay requires original C parameter facts")

        parameter_specs: list[str] = []
        parameter_names: list[str] = []
        records: dict[str, str] = {}
        scalar_parameter = ""
        for parameter in parameters:
            parameter_name = str(parameter.get("name", ""))
            parameter_type = str(parameter.get("type", "int")).strip()
            parameter_specs.append(f"{parameter_type} {parameter_name}")
            parameter_names.append(parameter_name)
            if parameter.get("pointer"):
                records[re.sub(r"\s*\*.*$", "", parameter_type).strip()] = parameter_name
            else:
                scalar_parameter = parameter_name
        config_parameter = records.get("dsc_cfg_t")
        state_parameter = records.get("dsc_state_t")
        if not config_parameter or not state_parameter or not scalar_parameter:
            raise RuntimeError("flatness overlay requires config, state, and hPos parameters")

        hpos_port = str(bindings.get("hpos_port", "hPos"))
        config_fields = bindings.get("config_fields", {}) or {}
        state_fields = bindings.get("state_fields", {}) or {}
        samples = window.get("sample_ports_by_component", {}) or {}
        sample_expressions: dict[str, str] = {}
        padding_left = int(window.get("padding_left", 5))
        for raw_component in range(4):
            taps = samples.get(str(raw_component), samples.get(raw_component, []))
            for offset, tap in enumerate(taps):
                sample_expressions[str(tap)] = (
                    f"(({state_parameter}->numComponents > {raw_component}) ? "
                    f"{state_parameter}->origLine[{raw_component}]"
                    f"[{scalar_parameter} + PADDING_LEFT + {offset}] : 0)"
                )

        rtl_arguments: list[str] = []
        for port in inputs:
            port_name = str(port.get("name"))
            if port_name == hpos_port:
                rtl_arguments.append(scalar_parameter)
                continue
            if port_name in config_fields:
                field = str(config_fields[port_name])
                rtl_arguments.append(f"{config_parameter}->{field}")
                continue
            if port_name in state_fields:
                field = str(state_fields[port_name])
                if field.startswith("cpntBitDepth["):
                    index = field.split("[", 1)[1].split("]", 1)[0]
                    rtl_arguments.append(f"{state_parameter}->cpntBitDepth[{index}]")
                else:
                    rtl_arguments.append(f"{state_parameter}->{field}")
                continue
            if port_name in sample_expressions:
                rtl_arguments.append(sample_expressions[port_name])
                continue
            raise RuntimeError(f"flatness overlay has no source binding for port: {port_name}")

        original = str(contract_function(contract).get("name")) + "_original"
        input_declarations = ", ".join(f"int {port['name']}" for port in inputs)
        caller_declarations = ", ".join(parameter_specs)
        caller_call = ", ".join(parameter_names)
        rtl_call = ", ".join(rtl_arguments)
        header = source_dir / "dsc_cicd_overlay.h"
        header.write_text(
            "#ifndef DSC_CICD_OVERLAY_H\n"
            "#define DSC_CICD_OVERLAY_H\n"
            "#include \"dsc_types.h\"\n"
            f"int dsc_cicd_invoke({caller_declarations});\n"
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
        assignments = "\n".join(
            f"    dut.{port['name']} = static_cast<long long>({port['name']});"
            for port in inputs
        )
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

    def write_overlay_sources(self, contract: dict[str, Any], source_dir: pathlib.Path,
                              module: str, candidate_sv: pathlib.Path) -> dict[str, pathlib.Path]:
        if (contract.get("semantics", {}) or {}).get("kind") == "flatness_window":
            return self.write_flatness_overlay_sources(contract, source_dir, module, candidate_sv)
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
            semantics = contract.get("semantics", {}) or {}
            window_spec = semantics.get("window_spec", {}) if isinstance(semantics, dict) else {}
            dynamic_window = window_spec.get("dynamic_line_window", {}) if isinstance(window_spec, dict) else {}
            if not isinstance(dynamic_window, dict):
                dynamic_window = {}
            dynamic_prev_ports = [
                str(value) for value in dynamic_window.get("prev_window_ports", [])
            ]
            dynamic_curr_ports = [
                str(value) for value in dynamic_window.get("curr_window_ports", [])
            ]
            dynamic_hpos = str(
                dynamic_window.get("hpos_parameter")
                or (semantics.get("legal_vector_strategy", {}) or {}).get("hpos_port", "hPos")
            )
            dynamic_prev_parameter = str(
                dynamic_window.get("prev_parameter")
                or next(
                    (
                        item.get("parameter")
                        for item in flattened
                        if str(item.get("parameter", "")) and str(item.get("parameter", "")).lower().startswith("prev")
                    ),
                    "prevLine",
                )
            )
            dynamic_curr_parameter = str(
                dynamic_window.get("curr_parameter")
                or next(
                    (
                        item.get("parameter")
                        for item in flattened
                        if str(item.get("parameter", "")) and str(item.get("parameter", "")).lower().startswith("curr")
                    ),
                    "currLine",
                )
            )

            def dynamic_line_argument(port_name: str) -> str | None:
                if not dynamic_prev_ports and not dynamic_curr_ports:
                    return None
                if port_name in dynamic_prev_ports:
                    slot = dynamic_prev_ports.index(port_name)
                    samples = int(dynamic_window.get("samples_per_unit", 3))
                    padding = int(dynamic_window.get("padding_left", 5))
                    first_offset = int(dynamic_window.get("prev_window_first_offset", -2))
                    index = (
                        f"((({dynamic_hpos} / {samples}) * {samples}) + "
                        f"{padding} + {first_offset + slot})"
                    )
                    return f"{dynamic_prev_parameter}[{index}]"
                if port_name in dynamic_curr_ports:
                    slot = dynamic_curr_ports.index(port_name)
                    left = int(dynamic_window.get("current_window_left", 8))
                    window_start = (
                        f"(({dynamic_hpos} > {left}) ? "
                        f"({dynamic_hpos} - {left}) : 0)"
                    )
                    return f"{dynamic_curr_parameter}[({window_start}) + {slot}]"
                return None

            def resolve_overlay_index(dependency: dict[str, Any], raw_index: object) -> str:
                raw = str(raw_index)
                if re.fullmatch(r"-?\d+", raw):
                    return raw
                normalized_raw = re.sub(r"[^a-z0-9]", "", raw.lower())
                bound_port = next(
                    (
                        item for item in flattened
                        if any(
                            re.sub(r"[^a-z0-9]", "", str(candidate).lower()) == normalized_raw
                            for candidate in (
                                item.get("port_name"),
                                item.get("role"),
                            )
                            if candidate is not None
                        )
                    ),
                    None,
                )
                if bound_port and bound_port.get("record"):
                    bound_record = record_names.get(str(bound_port.get("record")))
                    bound_field = str(bound_port.get("field"))
                    if bound_record and re.match(r"^[A-Za-z_][A-Za-z0-9_]*$", bound_field):
                        raw_indices: list[object] = []
                        if bound_port.get("index_names") is not None:
                            raw_indices.extend(bound_port.get("index_names") or [])
                        elif bound_port.get("index_name") is not None:
                            raw_indices.append(bound_port.get("index_name"))
                        elif bound_port.get("index") is not None:
                            raw_indices.append(bound_port.get("index"))
                        indices = [resolve_overlay_index(bound_port, value) for value in raw_indices]
                        suffix = "".join(f"[{index}]" for index in indices)
                        return f"{bound_record}->{bound_field}{suffix}"
                indexed_field = next(
                    (
                        item for item in flattened
                        if re.sub(r"[^a-z0-9]", "", str(item.get("field", "")).lower()) == normalized_raw
                        and "[" not in str(item.get("c_type", "int"))
                    ),
                    None,
                )
                if indexed_field:
                    record_name = record_names.get(str(indexed_field.get("record")))
                    field_name = str(indexed_field.get("field"))
                    if record_name and re.match(r"^[A-Za-z_][A-Za-z0-9_]*$", field_name):
                        return f"{record_name}->{field_name}"
                for scalar in scalar_inputs:
                    for candidate in (scalar.get("name"), scalar.get("role")):
                        if re.sub(r"[^a-z0-9]", "", str(candidate).lower()) == normalized_raw:
                            return str(scalar.get("name"))
                return safe_identifier(raw)

            for port in inputs:
                field = str(port.get("name"))
                dynamic_argument = dynamic_line_argument(field)
                if dynamic_argument is not None:
                    rtl_arguments.append(dynamic_argument)
                    continue
                if field in flattened_by_port:
                    dependency = flattened_by_port[field]
                    # A flattened record field also carries its original
                    # parameter name.  It must be emitted as
                    # ``record->field[index]``; only a bare pointer-array tap
                    # uses the ``parameter[index]`` form.
                    if dependency.get("record"):
                        record_name = record_names.get(str(dependency.get("record")))
                        if not record_name:
                            raise RuntimeError(f"missing record parameter for: {dependency.get('record')}")
                        dependency_field = str(dependency.get("field"))
                        c_type = str(dependency.get("c_type", port.get("c_type", "int")))
                        raw_indices: list[object] = []
                        if dependency.get("index_names") is not None:
                            value = dependency.get("index_names")
                            if not isinstance(value, list) or not value:
                                raise RuntimeError(f"invalid record index_names for: {dependency_field}")
                            raw_indices.extend(value)
                        elif dependency.get("index_name") is not None:
                            raw_indices.append(dependency.get("index_name"))
                        elif dependency.get("index") is not None and "[" in c_type:
                            raw_indices.append(dependency.get("index"))
                        if raw_indices:
                            indices = [resolve_overlay_index(dependency, value) for value in raw_indices]
                            rtl_arguments.append(
                                f"{record_name}->{dependency_field}" + "".join(f"[{index}]" for index in indices)
                            )
                        elif "*" in c_type or ("[" in c_type and "]" in c_type):
                            match = re.search(
                                rf"->\s*{re.escape(dependency_field)}\s*\[\s*([A-Za-z_][A-Za-z0-9_]*)\s*\]",
                                source_body_text,
                            )
                            if not match:
                                raise RuntimeError(f"record array field lacks a frozen index: {dependency_field}")
                            rtl_arguments.append(f"{record_name}->{dependency_field}[{match.group(1)}]")
                        else:
                            rtl_arguments.append(f"{record_name}->{dependency_field}")
                    elif dependency.get("parameter"):
                        parameter = str(dependency.get("parameter"))
                        index = int(dependency.get("index", 0))
                        rtl_arguments.append(f"{parameter}[{index}]")
                    else:
                        record_name = record_names.get(str(dependency.get("record")))
                        if not record_name:
                            raise RuntimeError(f"missing record parameter for: {dependency.get('record')}")
                        dependency_field = str(dependency.get("field"))
                        c_type = str(dependency.get("c_type", port.get("c_type", "int")))
                        if dependency.get("index_name"):
                            index = resolve_overlay_index(dependency, dependency.get("index_name"))
                            rtl_arguments.append(f"{record_name}->{dependency_field}[{index}]")
                        elif dependency.get("index") is not None and "[" in c_type:
                            rtl_arguments.append(
                                f"{record_name}->{dependency_field}[{int(dependency.get('index'))}]"
                            )
                        elif "*" in c_type or ("[" in c_type and "]" in c_type):
                            match = re.search(
                                rf"->\s*{re.escape(dependency_field)}\s*\[\s*([A-Za-z_][A-Za-z0-9_]*)\s*\]",
                                source_body_text,
                            )
                            index = match.group(1) if match else index_name
                            rtl_arguments.append(f"{record_name}->{dependency_field}[{index}]")
                        else:
                            rtl_arguments.append(f"{record_name}->{dependency_field}")
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
        temp_parent = self.root / "tmp"
        temp_parent.mkdir(parents=True, exist_ok=True)
        temp_root = pathlib.Path(tempfile.mkdtemp(prefix=f"dsc-cicd-{label}-", dir=str(temp_parent)))
        destination = temp_root / model_root.name
        ignore = shutil.ignore_patterns(".git", "__pycache__", "target", "build", "dsc-rs", "operator_bittrue")
        shutil.copytree(model_root, destination, ignore=ignore)
        return destination

    def run_matrix(self, contract: dict[str, Any], artifact: pathlib.Path,
                   candidate: dict[str, Any]) -> dict[str, Any]:
        scenarios = self.discover_matrix()
        if len(scenarios) < 1:
            result = {"status": "INFRASTRUCTURE_FAILURE", "reason": "no baseline scripts discovered"}
            write_json(artifact / "matrix-receipt.json", result)
            return result
        base_model = self.copy_model("baseline")
        overlay_model: pathlib.Path | None = None

        def persist_matrix_failure(result: dict[str, Any]) -> dict[str, Any]:
            roots: list[pathlib.Path] = [base_model, self.root]
            if overlay_model is not None:
                roots.insert(1, overlay_model)
            scrubbed = scrub_paths(result, roots)
            write_json(artifact / "matrix-receipt.json", scrubbed)
            if isinstance(scrubbed.get("overlay"), dict):
                write_json(artifact / "overlay-receipt.json", scrubbed["overlay"])
            if isinstance(scrubbed.get("compile"), dict):
                write_json(artifact / "overlay-compile-receipt.json", scrubbed["compile"])
            return scrubbed

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
                return persist_matrix_failure({
                    "status": "INFRASTRUCTURE_FAILURE",
                    "reason": "baseline matrix failed",
                    "baseline": baseline_results,
                })
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
                return persist_matrix_failure({
                    "status": "INFRASTRUCTURE_FAILURE",
                    "reason": "Clang overlay rewrite failed",
                    "baseline": baseline_results,
                    "overlay": overlay_receipt,
                })
            frozen_input_count = sum(
                1 for port in contract.get("interface", {}).get("ports", [])
                if port.get("direction") == "input"
            )
            call_sites = [
                site for site in overlay_receipt.get("call_sites", [])
                if isinstance(site, dict)
            ]
            call_site_arities = [len(site.get("arguments", [])) for site in call_sites]
            if call_sites and any(arity != frozen_input_count for arity in call_site_arities):
                # The immutable caller still owns a pointer/state projection
                # that is not represented by the frozen scalar DUT interface.
                # Keep that caller on C_ONLY; never invent a guessed adapter or
                # pass dummy state just to make RTL_RETURN compile.
                return persist_matrix_failure({
                    "status": "COMPOSITION_BLOCKED",
                    "reason": "caller call signature does not provide the frozen DUT interface; retain C boundary",
                    "baseline": baseline_results,
                    "overlay": overlay_receipt,
                    "composition": {
                        "status": "C_BOUNDARY",
                        "frozen_input_count": frozen_input_count,
                        "call_site_argument_counts": call_site_arities,
                        "c_only_status": "PASS",
                        "rtl_modes": "NOT_RUN",
                    },
                    "modes": {
                        "C_ONLY": {
                            "status": "PASS",
                            "execution_status": "BASELINE_ONLY",
                            "scenarios": baseline_results,
                        },
                        "SHADOW": {"status": "NOT_RUN", "scenarios": []},
                        "RTL_RETURN": {"status": "NOT_RUN", "scenarios": []},
                    },
                })
            compile_receipt = self.compile_overlay(contract, overlay_model / "source", module, overlay_copy_sv)
            if compile_receipt.get("status") != "PASS":
                return persist_matrix_failure({
                    "status": "INFRASTRUCTURE_FAILURE",
                    "reason": "caller/callee overlay compile failed",
                    "baseline": baseline_results,
                    "overlay": overlay_receipt,
                    "compile": compile_receipt,
                })
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
            write_json(artifact / "matrix-receipt.json", result)
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
            if unit_status in {"FORMAL_EQUIVALENT", "EXHAUSTIVE_EQUIVALENT", "DIFFERENTIAL_PASS"}:
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
            skip_matrix = unit_status in {"COUNTEREXAMPLE", "INFRASTRUCTURE_FAILURE", "UNPROVED"}
            if skip_matrix:
                matrix_status = "NOT_RUN_UNIT_REJECTED"
                bitstream_gate = "FAIL"
            elif not source.is_file() or not candidate_copy.get("module"):
                matrix_status = "NOT_RUN_COMPILE_FAILURE"
                bitstream_gate = "FAIL"
            else:
                shutil.copy2(source, candidate_path)
                matrix = self.run_matrix(contract, rejected_artifact, candidate_copy)
                matrix_status = str(matrix.get("status", "INFRASTRUCTURE_FAILURE"))
                bitstream_gate = "PASS" if matrix_status == "PASS" else "FAIL"
            composition_status = "NOT_RUN" if skip_matrix else "FAIL"
            if matrix:
                composition_status = "PASS" if (
                    matrix.get("modes", {}).get("SHADOW", {}).get("status") == "PASS"
                    and matrix.get("modes", {}).get("RTL_RETURN", {}).get("status") == "PASS"
                ) else "FAIL"
            expected = unit_status not in {"FORMAL_EQUIVALENT", "EXHAUSTIVE_EQUIVALENT"} and bitstream_gate == "FAIL"
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
                    "reason": "unit rejection is already decisive" if skip_matrix else None,
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
            try:
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
                    "generation": read_json(artifact / "generation.json", {}) or {},
                    "unit": cached_unit,
                    "matrix": cached_bitstream,
                    "dependency": read_json(artifact / "dependency-receipt.json", {}) or {},
                    "rejected_candidates": cached_unit.get("rejected_candidates", []),
                    "cache_entry": cache_entry,
                }
                result["library_promotion"] = self.promote_library_component(contract, item, artifact, result)
                self.append_result(result)
                return result
            except (OSError, RuntimeError, ValueError, subprocess.SubprocessError) as error:
                self.update_state(cid, "DISCOVERED", "INFRASTRUCTURE_FAILURE", artifacts=[str(artifact.relative_to(self.root))], failure=str(error))
                result = {"contract_id": cid, "status": "INFRASTRUCTURE_FAILURE", "reason": str(error)}
                self.append_result(result)
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
                self.append_result(result)
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
                self.append_result(result)
                return result
            candidate = next(item for item in generation.get("candidates", []) if item.get("candidate") == unit["promoted_candidate"])
            matrix = self.run_matrix(contract, artifact, candidate)
            matrix_failure = matrix.get("reason") if matrix.get("status") != "PASS" else None
            shadow_status = matrix.get("modes", {}).get("SHADOW", {}).get("status") == "PASS"
            rtl_status = matrix.get("modes", {}).get("RTL_RETURN", {}).get("status") == "PASS"
            self.update_state(
                cid,
                "SHADOW_PASS",
                "PASS" if shadow_status else "FAIL",
                artifacts=[str(artifact.relative_to(self.root))],
                failure=matrix_failure,
            )
            self.update_state(
                cid,
                "RTL_RETURN_PASS",
                "PASS" if rtl_status else "FAIL",
                artifacts=[str(artifact.relative_to(self.root))],
                failure=matrix_failure,
            )
            dependency = self.dependency_verify(contract, item, artifact, unit, matrix)
            self.update_state(
                cid,
                "DEPENDENCIES_VERIFIED",
                dependency.get("status", "FAIL"),
                artifacts=[str(artifact.relative_to(self.root))],
                failure=dependency.get("failure_reason"),
            )
            bitstream_status = matrix.get("status") == "PASS"
            self.update_state(
                cid,
                "BITSTREAM_PASS",
                "PASS" if bitstream_status else "FAIL",
                artifacts=[str(artifact.relative_to(self.root))],
                failure=matrix_failure,
            )
            final = "PROMOTED" if bitstream_status and dependency.get("status") == "PASS" else "FAILED"
            self.update_state(
                cid,
                "PROMOTED" if final == "PROMOTED" else "BITSTREAM_PASS",
                final,
                artifacts=[str(artifact.relative_to(self.root))],
                failure=None if final == "PROMOTED" else (matrix_failure or dependency.get("failure_reason")),
            )
            result = {
                "contract_id": cid,
                "status": final,
                "generation": generation,
                "unit": unit,
                "matrix": matrix,
                "dependency": dependency,
                "rejected_candidates": rejected_candidates,
            }
            if final == "PROMOTED":
                result["library_promotion"] = self.promote_library_component(contract, item, artifact, result)
            self.append_result(result)
            for name in ("shards", "shard-results", "oracle-build", "candidate-build", "generated"):
                path = artifact / name
                if path.is_dir() and name != "generated":
                    shutil.rmtree(path, ignore_errors=True)
            return result
        except (OSError, RuntimeError, ValueError, subprocess.SubprocessError) as error:
            self.update_state(cid, "DISCOVERED", "INFRASTRUCTURE_FAILURE", artifacts=[str(artifact.relative_to(self.root))], failure=str(error))
            result = {"contract_id": cid, "status": "INFRASTRUCTURE_FAILURE", "reason": str(error)}
            self.append_result(result)
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
                "domain_proof_complete": domain.get("proof_complete", True),
                "vector_strategy": domain.get("vector_strategy", {}).get("kind"),
                "formal_proof_status": promoted.get("formal_proof", {}).get("status"),
                "formal_proof_complete": promoted.get("formal_proof", {}).get("proof_complete", False),
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
                "library_promotion": result.get("library_promotion", {}),
                "rejected_candidates": result.get("rejected_candidates", []),
                "counterexample": unit.get("smallest_counterexample"),
            })
        report = {
            "schema_version": 2,
            "agent": "executable-generic-c-to-rtl-cicd",
            "input_pdf": self.input_facts.get("spec_path"),
            "input_source_root": self.input_facts.get("source_root"),
            "selected_contracts": selected,
            "selected_new_work": [
                item["contract_id"]
                for item in self.plan.get("contracts", [])
                if item.get("selected") and item.get("new_work")
            ],
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
                "formal_window_pass": "FORMAL_EQUIVALENT; requires an independent parsed-RTL proof",
                "bounded_differential_pass": "DIFFERENTIAL_PASS; never a promotion gate",
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
            f"- selected contracts: {', '.join(selected) or 'none'}",
            f"- selected new work: {', '.join(report['selected_new_work']) or 'none'}",
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
            lines.append(f"- {value['contract_id']}: {value['status']} ({value['execution_status']}); unit={value['unit_status']}; dependency={value['dependency_status']}; matrix={value['matrix_status']}; library={value['library_promotion'].get('status', 'NOT_ATTEMPTED')}")
            lines.append(
                f"  - executed vectors/shards: {value['executed_vectors']}/{value['executed_shards']}; "
                f"shard seconds: {value['shard_durations_seconds']}; "
                f"domain_proof_complete={value['domain_proof_complete']}; "
                f"formal={value['formal_proof_status']}/{value['formal_proof_complete']}; "
                f"strategy={value['vector_strategy']}"
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

    def run_selected_batches(self) -> None:
        """Execute independent selected contracts in deterministic batches.

        Each contract owns a unique artifact directory, so generation, C
        oracle compilation, Verilator builds, and shard processes can run in
        parallel.  A selected caller waits for any selected callee; callers
        whose callees are already promoted are independent and can start in
        the same batch.  The function identities come only from the plan and
        callgraph facts.
        """
        selected = [
            item for item in self.plan.get("contracts", []) if item.get("selected")
        ]
        selected_by_id = {str(item["contract_id"]): item for item in selected}
        remaining = set(selected_by_id)
        adjacency = self.dependency_info.get("adjacency", {}) or {}
        contract_workers = max(
            1,
            int(os.environ.get("DSC_CICD_CONTRACT_WORKERS", os.environ.get("DSC_CICD_WORKERS", "2"))),
        )
        while remaining:
            ready_ids = sorted(
                cid for cid in remaining
                if not any(str(dep) in remaining for dep in adjacency.get(cid, []))
            )
            if not ready_ids:
                # The plan normally rejects cycles.  Keep a deterministic
                # fail-closed escape if a malformed external plan slips in.
                ready_ids = [sorted(remaining)[0]]
            batch = [selected_by_id[cid] for cid in ready_ids]
            with concurrent.futures.ThreadPoolExecutor(
                max_workers=min(contract_workers, len(batch)),
                thread_name_prefix="cicd-contract",
            ) as executor:
                futures = [executor.submit(self.run_contract, item) for item in batch]
                # Consume futures in plan order so an exception cannot be
                # silently discarded and receipts remain deterministic.
                for future in futures:
                    future.result()
            remaining.difference_update(ready_ids)
        with self.state_lock:
            self.run_results.sort(key=lambda item: str(item.get("contract_id", "")))

    def run_command(self) -> int:
        self.load_inputs()
        self.materialize_new_contracts()
        self.dependency_graph()
        self.build_plan()
        self.write_plan_files()
        self.initialize_state()
        if not self.input_facts.get("errors"):
            for item in self.plan.get("contracts", []):
                if not item.get("selected"):
                    self.run_contract(item)
            self.run_selected_batches()
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
