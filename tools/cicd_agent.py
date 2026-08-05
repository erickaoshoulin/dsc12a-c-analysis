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
PROMOTION_REVIEW_GATES = (
    "width_spec",
    "unit_equivalence",
    "formal_or_exhaustive",
    "dependency_composition",
    "C_ONLY",
    "SHADOW",
    "RTL_RETURN",
    "frame_compare",
)
# A prior composition boundary is a durable no-repeat guard only while the
# composition implementation and its inputs are unchanged.  Controller,
# pipeline, tool, or prompt changes are legitimate automatic revalidation
# triggers; semantic source/spec/contract/dependency changes already reopen
# work through the ordinary planner.
COMPOSITION_RETRY_HASHES = ("pipeline", "agent", "prompt", "tools")
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
    if isinstance(value, pathlib.Path):
        value = str(value)
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
        configured_artifacts = os.environ.get("DSC_CICD_ARTIFACT_ROOT", "").strip()
        self.artifacts = (
            pathlib.Path(configured_artifacts).expanduser().resolve()
            if configured_artifacts
            else self.root / "artifacts"
        )
        self.external_artifacts = self.artifacts != (self.root / "artifacts").resolve()
        self.integration = self.root / "integration"
        self.manifest = read_json(self.root / "spec" / "manifest.json", {}) or {}
        self.locked_contracts = [read_json(path, {}) for path in sorted((self.root / "contracts" / "locked").glob("*.json"))]
        self.locked_contracts = [item for item in self.locked_contracts if item]
        self.contracts = list(self.locked_contracts)
        self.previous_state = read_json(self.ci / "state.json", {}) or {}
        self.previous_dag = read_json(self.ci / "dag.json", {}) or {}
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

    def artifact_reference(self, path: pathlib.Path) -> str:
        """Return a checkout-portable reference for an artifact path."""
        resolved = path.resolve()
        if self.external_artifacts:
            try:
                return pathlib.PurePosixPath("artifacts", *resolved.relative_to(self.artifacts).parts).as_posix()
            except ValueError:
                pass
        try:
            return resolved.relative_to(self.root).as_posix()
        except ValueError:
            return str(resolved)

    def resolve_artifact_reference(self, raw: str | pathlib.Path) -> pathlib.Path:
        """Resolve local or logical artifact references against the active root."""
        value = str(raw)
        if value.startswith("external://artifacts/"):
            return self.artifacts / pathlib.PurePosixPath(value.removeprefix("external://artifacts/"))
        path = pathlib.Path(value)
        if path.is_absolute():
            return path
        if path.parts and path.parts[0] == "artifacts":
            suffix = pathlib.Path(*path.parts[1:])
            return (self.artifacts if self.external_artifacts else self.root / "artifacts") / suffix
        return self.root / path

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

    def load_accepted_library_contracts(
        self,
        existing: list[dict[str, Any]],
    ) -> list[dict[str, Any]]:
        """Reload accepted dynamic contracts for an ordinary plan.

        ``contracts/locked`` is the small, human-maintained seed set.  Once a
        tool-discovered contract is accepted, its canonical snapshot lives in
        ``library/contracts`` and the manifest records the accepted frontier.
        A normal plan must bring those snapshots back into the in-memory set;
        otherwise it silently degrades the stable DAG to the seed set plus
        whatever happens to be rediscovered in the current pass.
        """
        manifest = read_json(self.root / "library" / "manifest.json", {}) or {}
        accepted_components = {
            str(component.get("contract_id", "")).strip().lower(): component
            for component in manifest.get("components", [])
            if str(component.get("status", "")).upper() == "PASS"
            and str(component.get("contract_id", "")).strip()
        }
        accepted_ids = set(accepted_components)
        known_ids = {
            str(contract_id(item)).strip().lower()
            for item in existing
            if str(contract_id(item)).strip()
        }
        loaded: list[dict[str, Any]] = []
        contracts_dir = self.root / "library" / "contracts"
        if not contracts_dir.is_dir():
            return loaded

        for path in sorted(contracts_dir.glob("*.json")):
            contract = read_json(path, {}) or {}
            cid = str(contract_id(contract)).strip().lower()
            if not cid or cid not in accepted_ids or cid in known_ids:
                continue
            clang_usr = str(contract_function(contract).get("clang_usr", "")).strip()
            if not clang_usr:
                continue
            if not contract_exact_links(contract):
                continue

            # The library contract carries promotion provenance for audit, but
            # the manifest's content-addressed artifact owns the planning
            # identity.  Prefer its immutable locked snapshot so cache and
            # dependency hashes stay equal to the accepted state after a
            # normal plan.  Fall back to a provenance-stripped library copy
            # only when an older artifact predates the snapshot file.
            component = accepted_components[cid]
            expected_hash = str(component.get("contract_hash", ""))
            snapshots = [copy.deepcopy(contract)]
            artifact_raw = str(component.get("artifact_dir", ""))
            artifact_dir = pathlib.Path(artifact_raw)
            if artifact_raw and not artifact_dir.is_absolute() and ".." not in artifact_dir.parts:
                artifact_path = self.resolve_artifact_reference(artifact_dir)
                try:
                    artifact_path.resolve().relative_to(self.artifacts.resolve())
                except ValueError:
                    artifact_path = None
                if artifact_path is not None:
                    locked_snapshot = read_json(artifact_path / "locked-contract.json", {}) or {}
                    if contract_id(locked_snapshot).lower() == cid:
                        snapshots.insert(0, locked_snapshot)
            snapshots.extend(
                [
                    {
                        key: value
                        for key, value in contract.items()
                        if key not in excluded
                    }
                    for excluded in (
                        {"library_promotion"},
                        {"library_promotion", "do_not_edit"},
                    )
                ]
            )
            accepted_snapshot = next(
                (
                    snapshot
                    for snapshot in snapshots
                    if expected_hash and digest(snapshot) == expected_hash
                ),
                snapshots[0],
            )
            accepted_snapshot["status"] = "LOCKED"
            loaded.append(accepted_snapshot)
            known_ids.add(cid)
        return loaded

    def materialize_new_contracts(self) -> list[dict[str, Any]]:
        if self.input_facts.get("errors"):
            return []
        facts = read_json(self.root / "facts" / "functions.json", {}) or {}
        exact = self.exact_links_by_usr()
        overrides = self.reviewed_overrides()
        candidate_facts = self.tool_candidate_facts()
        effective_locked = self.apply_reviewed_overrides()
        target_contract = safe_identifier(os.environ.get("DSC_CICD_TARGET_CONTRACT", "")).lower()
        refresh_stable = os.environ.get("DSC_CICD_REFRESH_STABLE", "").lower() in {"1", "true", "yes"}
        # Stable refreshes must execute against the same canonical accepted
        # snapshots as ordinary plans.  Rebuilding promoted contracts from
        # current tool facts changes their content hash and can accidentally
        # verify a rediscovered contract instead of the accepted RTL.
        effective_locked.extend(
            self.load_accepted_library_contracts(effective_locked)
        )
        known = {str(contract_function(item).get("clang_usr")) for item in effective_locked}
        promoted_usrs = self.promoted_contract_usrs(effective_locked)
        source_usrs = {
            str(item.get("clang_usr"))
            for item in facts.get("functions", [])
            if item.get("clang_usr")
        }
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

    def prior_execution_incomplete(self, cid: str) -> bool:
        """Detect an interrupted executable attempt from durable state history.

        A later no-work plan may append a DEFERRED/BLOCKED event after a
        process died during verification.  Do not lose that work merely
        because the current semantic hashes are unchanged.  Only in-progress
        or successfully-entered execution stages are recoverable here;
        terminal composition boundaries and candidate counterexamples retain
        their existing no-repeat behavior.
        """
        prior = self.prior_contract(cid)
        if prior.get("promotion_status") in {
            "AWAITING_HUMAN_APPROVAL",
            "VERIFIED_REFRESH",
        }:
            return False
        history = prior.get("history", []) or []
        # Older state snapshots did not retain the final refresh promotion
        # status on a deferred contract.  A stable refresh is still complete
        # when its durable accepted-RTL receipt and matrix are both PASS; do
        # not turn a later bounded no-work plan into a false recovery job.
        for raw in prior.get("artifacts", []) or []:
            artifact = pathlib.Path(str(raw))
            if not artifact.is_absolute():
                artifact = self.root / artifact
            generation = read_json(artifact / "generation.json", {}) or {}
            matrix = read_json(artifact / "matrix-receipt.json", {}) or {}
            if (
                generation.get("execution_status") == "REUSED_ACCEPTED_RTL"
                and generation.get("status") == "PASS"
                and matrix.get("status") == "PASS"
            ):
                return False
        execution_states = set(STATE_ORDER[1:-1])
        for event in reversed(history):
            if not isinstance(event, dict):
                continue
            state = str(event.get("state", ""))
            status = str(event.get("status", ""))
            if event.get("promotion_status") in {
                "AWAITING_HUMAN_APPROVAL",
                "VERIFIED_REFRESH",
            }:
                return False
            if state == "PROMOTED":
                return False
            if state in execution_states:
                if status in {"COUNTEREXAMPLE", "FAILED", "FAIL", "UNPROVED", "UNSUPPORTED", "GENERATION_REQUIRED", "GENERATION_FAILED"}:
                    return False
                if status not in {"DEFERRED", "BLOCKED"}:
                    return True
            if state == "CONTRACT_LOCKED" and status == "EXECUTING":
                return True
            if state == "DISCOVERED" and status == "INFRASTRUCTURE_FAILURE":
                return True
            if state in {"CONTRACT_LOCKED", "DISCOVERED"} and status in {"DEFERRED", "BLOCKED"}:
                continue
            if state == "DISCOVERED" and status in {"COUNTEREXAMPLE", "FAILED"}:
                return False
        return False

    def promotion_approval_path(self, cid: str, contract_hash: str) -> pathlib.Path:
        """Return the immutable approval location for one contract identity."""
        return self.ci / "promotion-approvals" / safe_identifier(cid) / f"{safe_identifier(contract_hash)}.json"

    def prior_promotion_review(self, cid: str, contract_hash: str) -> tuple[bool, bool, str | None]:
        """Return pending/ready approval state without selecting by source name.

        The durable state carries the exact RTL hash that was reviewed.  A
        later run may resume that same artifact only when the matching approval
        receipt has appeared; otherwise the planner leaves the job visible and
        does not regenerate it.
        """
        prior = self.prior_contract(cid)
        pending = (
            str(prior.get("promotion_status", "")) == "AWAITING_HUMAN_APPROVAL"
            and str((prior.get("hashes", {}) or {}).get("contract", "")) == str(contract_hash)
        )
        if not pending:
            return False, False, None
        path = self.promotion_approval_path(cid, contract_hash)
        return True, path.is_file(), str(prior.get("pending_rtl_sha256") or "") or None

    def prior_composition_boundary(
        self, cid: str, hashes: dict[str, str]
    ) -> dict[str, Any] | None:
        """Find a durable C-boundary result for the same semantic inputs.

        A caller/callee composition can be blocked for a structural reason
        that the generated adapter cannot safely represent.  Keep that
        receipt visible while the same composition implementation is active;
        a controller/pipeline/tool/prompt change intentionally reopens the
        boundary so a corrected deterministic adapter is exercised.  A
        changed source, spec, contract, or dependency hash also reopens the
        work through the ordinary planner.
        """
        prior = self.prior_contract(cid)
        prior_hashes = prior.get("hashes", {}) or {}
        semantic_keys = ("source", "spec", "contract", "dependency")
        if any(
            not prior_hashes.get(key)
            or str(prior_hashes.get(key)) != str(hashes.get(key))
            for key in semantic_keys
        ):
            return None

        artifact_dirs: list[pathlib.Path] = []
        for raw in prior.get("artifacts", []) or []:
            path = self.resolve_artifact_reference(str(raw))
            if path.is_dir():
                artifact_dirs.append(path)
            elif path.is_file() and path.name in {
                "matrix-receipt.json",
                "dependency-receipt.json",
            }:
                artifact_dirs.append(path.parent)
        for artifact in artifact_dirs:
            matrix = read_json(artifact / "matrix-receipt.json", {}) or {}
            composition = matrix.get("composition", {}) or {}
            if (
                matrix.get("status") == "COMPOSITION_BLOCKED"
                and composition.get("status") == "C_BOUNDARY"
            ):
                try:
                    artifact_ref = self.artifact_reference(artifact)
                except ValueError:
                    artifact_ref = str(artifact)
                return {
                    "status": matrix.get("status"),
                    "composition_status": composition.get("status"),
                    "reason": matrix.get("reason"),
                    "artifact": artifact_ref,
                    "controller_changed": any(
                        prior_hashes.get(key)
                        and str(prior_hashes.get(key)) != str(hashes.get(key))
                        for key in COMPOSITION_RETRY_HASHES
                    ),
                }
        return None

    def cache_entry(self, key: str) -> dict[str, Any]:
        entries = self.cache.get("entries", {}) if isinstance(self.cache, dict) else {}
        if isinstance(entries, list):
            return next((item for item in entries if item.get("cache_key") == key), {})
        return entries.get(key, {}) if isinstance(entries, dict) else {}

    def cache_valid(self, entry: dict[str, Any], key: str) -> bool:
        if not entry or entry.get("cache_key") != key or entry.get("valid") is not True:
            return False
        artifact = self.resolve_artifact_reference(str(entry.get("artifact_dir", "")))
        return artifact.is_dir() and (artifact / "unit-receipt.json").is_file() and (artifact / "bitstream-receipt.json").is_file()

    def accepted_rtl_component(
        self,
        contract_id_value: str,
        contract_hash: str,
        manifest: dict[str, Any] | None = None,
        contract: dict[str, Any] | None = None,
    ) -> dict[str, Any] | None:
        """Resolve one immutable, hash-checked PASS RTL library component.

        A stable refresh may reuse accepted RTL only when the current locked
        contract is exactly the contract that was promoted.  The manifest
        path and bytes are checked here rather than trusting a stale receipt;
        a missing or changed library file is an infrastructure condition and
        must not turn into an implicit generator retry.
        """
        library = self.root / "library"
        payload = manifest if manifest is not None else read_json(library / "manifest.json", {}) or {}
        component = next(
            (
                value for value in payload.get("components", [])
                if str(value.get("contract_id")) == str(contract_id_value)
                and value.get("status") == "PASS"
            ),
            None,
        )
        if not component:
            return None
        manifest_contract_hash = str(component.get("contract_hash"))
        if manifest_contract_hash != str(contract_hash):
            # Selection/ranking metadata is routing provenance, not part of
            # the semantic contract consumed by an already accepted RTL
            # component.  Stable refreshes may rebuild that metadata from the
            # current tool facts, so compare the immutable contract snapshot
            # while ignoring only the transient selection block.  Compact
            # accepted snapshots live in the checkout for portability.  When
            # a fresh external artifact root is selected it is intentionally
            # empty, so fall back to that checkout snapshot instead of
            # treating the accepted RTL as unavailable.
            artifact_raw = str(component.get("artifact_dir", ""))
            artifact_dir = pathlib.Path(artifact_raw)
            if (
                contract is None
                or artifact_dir.is_absolute()
                or ".." in artifact_dir.parts
            ):
                return None
            artifact_paths = [self.resolve_artifact_reference(artifact_dir)]
            if self.external_artifacts and artifact_dir.parts[:1] == ("artifacts",):
                artifact_paths.append(self.root / artifact_dir)
            promoted_contract = None
            for artifact_path in artifact_paths:
                allowed_root = (
                    self.root / "artifacts"
                    if artifact_path == self.root / artifact_dir
                    else self.artifacts
                )
                try:
                    artifact_path.resolve().relative_to(allowed_root.resolve())
                except ValueError:
                    continue
                snapshot = read_json(artifact_path / "locked-contract.json", {}) or {}
                if (
                    snapshot
                    and self.stable_contract_identity(snapshot)
                    == self.stable_contract_identity(contract)
                ):
                    promoted_contract = snapshot
                    break
            if promoted_contract is None:
                return None
        raw_module_file = str(component.get("module_file", ""))
        if not raw_module_file:
            return None
        module_file = pathlib.Path(raw_module_file)
        if module_file.is_absolute() or ".." in module_file.parts:
            return None
        module_path = library / module_file
        try:
            module_path.resolve().relative_to(library.resolve())
        except ValueError:
            return None
        expected_sha256 = str(component.get("module_sha256", ""))
        if not module_path.is_file() or not expected_sha256 or file_hash(module_path) != expected_sha256:
            return None
        return {
            "contract_id": str(component.get("contract_id")),
            "contract_hash": str(component.get("contract_hash")),
            "module": str(component.get("module") or safe_identifier(contract_id_value).lower()),
            "module_file": str(module_path.relative_to(self.root)),
            "module_path": module_path,
            "module_sha256": expected_sha256,
        }

    @staticmethod
    def stable_contract_identity(contract: dict[str, Any]) -> str:
        """Hash semantic contract facts while excluding routing/provenance metadata."""
        normalized = copy.deepcopy(contract)
        for key in (
            "selection",
            "library_promotion",
            "do_not_edit",
            "lock",
            "provenance",
        ):
            normalized.pop(key, None)
        return digest(normalized)

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
        explicit_force_regenerate = os.environ.get("DSC_CICD_FORCE_REGENERATE", "").lower() in {"1", "true", "yes"}
        force_regenerate = explicit_force_regenerate or refresh_stable
        generator_hook = os.environ.get("DSC_CICD_GENERATOR_CMD", "").strip()
        target_contract = str(os.environ.get("DSC_CICD_TARGET_CONTRACT", "")).strip().lower()
        retry_blocked = os.environ.get("DSC_CICD_RETRY_BLOCKED", "").lower() in {"1", "true", "yes"}
        prior_shapes = {str(item.get("contract_id")): item.get("interface_shape", []) for item in self.previous_state.get("contracts", []) if item.get("current_state") == "PROMOTED"}
        for contract in sorted(self.contracts, key=contract_id):
            if not contract.get("interface", {}).get("ports"):
                contract.setdefault("interface", {})["ports"] = self.freeze_ports(contract.get("interface", {}))
            cid = contract_id(contract)
            key, hashes = self.cache_key(contract)
            is_ready, reasons = self.ready(contract)
            prior_boundary = self.prior_composition_boundary(cid, hashes)
            resume_needed = self.prior_execution_incomplete(cid)
            promotion_pending, approval_available, pending_rtl_sha256 = self.prior_promotion_review(cid, hashes["contract"])
            boundary_retry_requested = bool(
                prior_boundary
                and (
                    retry_blocked
                    or force_regenerate
                    or cid == target_contract
                    or prior_boundary.get("controller_changed", False)
                )
            )
            if prior_boundary and not boundary_retry_requested:
                reasons.append("prior_composition_boundary_unresolved")
                reasons = sorted(set(reasons))
                is_ready = False
            if promotion_pending and not approval_available:
                reasons.append("human_promotion_approval_pending")
                reasons = sorted(set(reasons))
                is_ready = False
            entry = self.cache_entry(key)
            stale = [name for name, value in hashes.items() if self.prior_contract(cid).get("hashes", {}).get(name) not in (None, value)]
            cache_hit = self.cache_valid(entry, key) and not force_regenerate
            accepted_rtl = self.accepted_rtl_component(cid, hashes["contract"], manifest, contract)
            new_work = bool(
                (contract.get("selection") or {}).get(
                    "new_work", cid in discovered and cid not in stable_ids
                )
            )
            if (
                cid in stable_ids
                and not explicit_force_regenerate
                and cid != target_contract
            ):
                # Accepted library entries retain their canonical snapshot in
                # an ordinary plan.  Their selection metadata may be from the
                # original discovery batch, but that must not reopen them as
                # new work or collapse the stable frontier to the seed set.
                new_work = False
            stable_refresh_candidate = bool(
                cid in stable_ids
                and (
                    refresh_stable
                    or (stale and not cache_hit)
                    or (resume_needed and not cache_hit)
                )
            )
            if (
                stable_refresh_candidate
                and not accepted_rtl
                and not explicit_force_regenerate
                and cid != target_contract
            ):
                reasons.append("accepted_rtl_unavailable")
                reasons = sorted(set(reasons))
                is_ready = False
            reuses_accepted_rtl = bool(
                accepted_rtl
                and stable_refresh_candidate
                and not explicit_force_regenerate
                and cid != target_contract
            )
            generation_required = bool(
                not cache_hit
                and not promotion_pending
                and not reuses_accepted_rtl
                and (
                    new_work
                    or explicit_force_regenerate
                    or cid == target_contract
                    or cid not in stable_ids
                )
            )
            if is_ready and generation_required and not generator_hook:
                reasons.append(
                    "GENERATION_REQUIRED: DSC_CICD_GENERATOR_CMD is not configured"
                )
                reasons = sorted(set(reasons))
                is_ready = False
            item = {
                "contract_id": cid,
                "function": contract_function(contract).get("name"),
                "clang_usr": contract_function(contract).get("clang_usr"),
                "origin": contract.get("origin", "locked_contract"),
                "new_work": new_work,
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
                "accepted_rtl_available": bool(accepted_rtl),
                "generation_required": generation_required,
                "generator_hook_configured": bool(generator_hook),
                "resume_needed": resume_needed,
                "promotion_pending": promotion_pending,
                "resume_human_approval": bool(promotion_pending and approval_available),
                "pending_rtl_sha256": pending_rtl_sha256,
                "prior_composition_boundary": prior_boundary,
                "boundary_retry_requested": boundary_retry_requested,
                "initial_state": entry.get("state") if cache_hit else "CONTRACT_LOCKED" if is_ready else "DISCOVERED",
            }
            entries.append(item)
            if is_ready:
                ready.append(cid)
            else:
                blocked.append({"contract_id": cid, "function": item["function"], "reasons": reasons})
        target_item = next((item for item in entries if item["contract_id"].lower() == target_contract), None)
        stale_stable = sorted(
            item["contract_id"]
            for item in entries
            if (
                item["ready"]
                and item["contract_id"] in stable_ids
                and item["stale"]
                and not item["cache_hit"]
            )
        )
        recovery_contracts = sorted(
            item["contract_id"]
            for item in entries
            if item["ready"] and item.get("resume_needed") and not item["cache_hit"]
        )
        approval_resume_contracts = sorted(
            item["contract_id"]
            for item in entries
            if item["ready"] and item.get("resume_human_approval") and not item["cache_hit"]
        )
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
            if approval_resume_contracts:
                # Human approval resumes the exact verified candidate already
                # recorded in the artifact; it must not invoke a new model or
                # generator attempt.
                selected = approval_resume_contracts[:max(1, int(os.environ.get("DSC_CICD_MAX_NEW", "1")))]
            elif recovery_contracts:
                # Recover an interrupted executable attempt before opening
                # unrelated new work.  This is state-driven orchestration,
                # not a source-level function selector.
                selected = recovery_contracts[:max(1, int(os.environ.get("DSC_CICD_MAX_NEW", "1")))]
            elif stale_stable:
                # A verified library regression has higher priority than
                # unrelated new RTL generation.  This keeps controller/tool
                # changes from opening a new candidate while an accepted
                # component still needs deterministic revalidation.
                selected = stale_stable[:max(1, int(os.environ.get("DSC_CICD_MAX_NEW", "1")))]
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
            item["auto_refresh"] = item["contract_id"] in stale_stable
            item["recovery"] = item["contract_id"] in recovery_contracts
            item["resume_human_approval"] = bool(
                item["selected"] and item.get("resume_human_approval")
            )
            item["reuse_accepted_rtl"] = bool(
                item["selected"]
                and item.get("accepted_rtl_available")
                and item["contract_id"] in stable_ids
                and (item["auto_refresh"] or item["recovery"] or refresh_stable)
                and not item["targeted"]
                and not explicit_force_regenerate
            )
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
            "auto_refresh_contracts": stale_stable,
            "recovery_contracts": recovery_contracts,
            "approval_resume_contracts": approval_resume_contracts,
            "dependency_pair": self.choose_dependency_pair(selected),
            "target_contract": target_item["contract_id"] if target_item else None,
            "force_regenerate": force_regenerate,
            "explicit_force_regenerate": explicit_force_regenerate,
            "refresh_stable": refresh_stable,
            "retry_blocked": retry_blocked,
            "reuse_accepted_rtl_contracts": [
                item["contract_id"] for item in entries if item.get("reuse_accepted_rtl")
            ],
            "generator_hook": generator_hook or None,
            "generator_hook_configured": bool(generator_hook),
            "input_errors": self.input_facts.get("errors", []),
        }
        self.make_dag()
        self.plan["historical_contracts"] = sorted({
            str(node.get("contract_id"))
            for node in self.dag.get("nodes", [])
            if node.get("contract_id") and node.get("contract_id") not in {item["contract_id"] for item in entries}
        })
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
            stage_names = list(STAGE_TO_STATE)
            for first, second in zip(stage_names, stage_names[1:]):
                edges.append({"from": f"{cid}:{first}", "to": f"{cid}:{second}"})
        pair = self.plan.get("dependency_pair")
        if pair:
            edges.append({"from": f"{pair['callee_contract']}:PROMOTED", "to": f"{pair['caller_function']}:COMPOSITION"})

        # A no-work refresh intentionally removes promoted contracts from the
        # active plan, but it must not erase their prior DAG evidence.  Keep
        # nodes and edges that are absent from the current tool/spec frontier;
        # the current plan remains authoritative for new selection while the
        # previous DAG remains an audit trail for completed promotion gates.
        current_node_ids = {str(node.get("node_id")) for node in nodes}
        historical_nodes = [
            copy.deepcopy(node)
            for node in self.previous_dag.get("nodes", [])
            if str(node.get("node_id")) not in current_node_ids
        ]
        historical_contract_ids = {
            str(node.get("contract_id"))
            for node in historical_nodes
            if node.get("contract_id")
        }
        # A prior plan may already have been refreshed, while ci/state.json
        # still retains the last executed promotion.  Reconstruct missing
        # historical nodes from that durable state so one no-work refresh
        # cannot erase audit evidence even when the previous DAG was compacted.
        state_by_contract = {
            str(item.get("contract_id")): item
            for item in self.previous_state.get("contracts", [])
            if item.get("contract_id")
        }
        state_to_stage = {state: stage for stage, state in STAGE_TO_STATE.items()}
        for cid, item in sorted(state_by_contract.items()):
            if cid in {str(value.get("contract_id")) for value in self.plan.get("contracts", [])} or cid in historical_contract_ids:
                continue
            hashes = item.get("hashes", {}) or {}
            current_state = str(item.get("current_state", "DISCOVERED"))
            current_index = STATE_ORDER.index(current_state) if current_state in STATE_ORDER else -1
            for index, state_name in enumerate(STATE_ORDER):
                if index == current_index:
                    node_status = str(item.get("status") or "PENDING")
                    failure_reason = item.get("failure_reason")
                elif 0 <= index < current_index:
                    node_status = "PASS"
                    failure_reason = None
                else:
                    node_status = "PENDING"
                    failure_reason = None
                historical_nodes.append({
                    "node_id": f"{cid}:{state_to_stage[state_name]}",
                    "contract_id": cid,
                    "stage": state_name,
                    "status": node_status,
                    "source_hash": hashes.get("source"),
                    "spec_hash": hashes.get("spec"),
                    "contract_hash": hashes.get("contract"),
                    "dependency_hash": hashes.get("dependency"),
                    "artifacts": sorted(str(value) for value in item.get("artifacts", [])),
                    "failure_reason": failure_reason,
                })
            for first, second in zip(STATE_ORDER, STATE_ORDER[1:]):
                edges.append({"from": f"{cid}:{state_to_stage[first]}", "to": f"{cid}:{state_to_stage[second]}"})
            historical_contract_ids.add(cid)
        all_nodes = nodes + historical_nodes
        all_node_ids = {str(node.get("node_id")) for node in all_nodes}
        edge_by_key: dict[tuple[str, str], dict[str, str]] = {}
        for edge in list(self.previous_dag.get("edges", [])) + edges:
            source = str(edge.get("from", ""))
            target = str(edge.get("to", ""))
            if source in all_node_ids and target in all_node_ids:
                edge_by_key[(source, target)] = {"from": source, "to": target}
        call_site_by_key: dict[str, dict[str, Any]] = {}
        for site in list(self.previous_dag.get("dependency_call_sites", [])) + self.dependency_info.get("all_call_sites", []):
            call_site_by_key[canonical(site)] = site
        self.dag = {
            "schema_version": 2,
            "state_order": list(STATE_ORDER),
            "nodes": all_nodes,
            "edges": sorted(edge_by_key.values(), key=lambda item: (item["from"], item["to"])),
            "cycles": self.dependency_info.get("cycles", []),
            "dependency_call_sites": sorted(call_site_by_key.values(), key=lambda item: (
                str(item.get("caller_function")),
                str(item.get("callee_function")),
                canonical(item.get("location", {})),
                canonical(item),
            )),
            "historical_node_count": len(historical_nodes),
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
            observed_hashes = item["hashes"]
            if (item.get("deferred") or item.get("blocked_reasons")) and old.get("hashes"):
                # A bounded batch or planner blocker must not acknowledge an
                # unexecuted refresh/new attempt merely because the current
                # controller hash changed. Keep the previous observation until
                # this contract actually runs, so a later hook/tool change can
                # reopen the exact work automatically.
                observed_hashes = old["hashes"]
            contracts.append({
                "contract_id": item["contract_id"],
                "function": item.get("function"),
                "origin": item.get("origin"),
                "selected": item.get("selected", False),
                "current_state": current,
                "status": "BLOCKED" if item.get("blocked_reasons") else "PENDING",
                "failure_reason": "; ".join(item.get("blocked_reasons", [])) or None,
                "hashes": observed_hashes,
                "interface_shape": item["interface_shape"],
                "history": old.get("history", [{"state": "DISCOVERED"}]),
                "artifacts": old.get("artifacts", []),
                "model_calls": 0,
                "token_count": 0,
                "promotion_status": old.get("promotion_status"),
                "pending_rtl_sha256": old.get("pending_rtl_sha256"),
                "promotion_approval_file": old.get("promotion_approval_file"),
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
                event = {"state": state_name, "status": status, "failure_reason": failure}
                item.setdefault("history", []).append(event)
            else:
                event = item["history"][-1]
                event.update({"status": status, "failure_reason": failure})
            if extra:
                item.update(extra)
                event.update(extra)
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

    def canonical_rtl_source(self, cid: str, source: str) -> tuple[str, str]:
        """Canonicalize one candidate and return its immutable content hash."""
        scrubbed = re.sub(r"//.*|/\*.*?\*/", "", source, flags=re.S)
        modules = list(re.finditer(r"\bmodule\s+([A-Za-z_][A-Za-z0-9_]*)", scrubbed))
        if len(modules) != 1 or len(re.findall(r"\bendmodule\b", scrubbed)) != 1:
            raise RuntimeError(f"library promotion requires one RTL module: {cid}")
        match = re.search(r"\bmodule\s+([A-Za-z_][A-Za-z0-9_]*)", source)
        if not match:
            raise RuntimeError(f"library promotion module name missing: {cid}")
        module_name = safe_identifier(cid).lower()
        canonical_source = source[:match.start(1)] + module_name + source[match.end(1):]
        if not canonical_source.endswith("\n"):
            canonical_source += "\n"
        return canonical_source, hashlib.sha256(canonical_source.encode("utf-8")).hexdigest()

    def promotion_approval(
        self,
        contract: dict[str, Any],
        item: dict[str, Any],
        rtl_sha256: str,
    ) -> dict[str, Any]:
        """Validate the human decision for one exact candidate identity."""
        cid = contract_id(contract)
        contract_hash = str(item.get("contract_hash") or digest(contract))
        path = self.promotion_approval_path(cid, contract_hash)
        expected = {
            "contract_id": cid,
            "contract_hash": contract_hash,
            "rtl_sha256": rtl_sha256,
            "source_sha256": str(self.input_facts.get("source_hash") or item.get("hashes", {}).get("source") or ""),
            "spec_sha256": str(self.input_facts.get("spec_hash") or item.get("hashes", {}).get("spec") or ""),
            "interface_sha256": digest(contract.get("interface", {}) or {}),
        }
        approval = read_json(path, None)
        errors: list[str] = []
        if not isinstance(approval, dict):
            errors.append("approval_file_missing" if not path.exists() else "approval_file_invalid_json")
            approval = {}
        for key, value in expected.items():
            if str(approval.get(key, "")) != str(value):
                errors.append(f"approval_{key}_mismatch")
        if approval.get("review_status") != "APPROVED":
            errors.append("approval_review_status_not_approved")
        if approval.get("decision") != "PROMOTE":
            errors.append("approval_decision_not_promote")
        if not str(approval.get("reviewer", "")).strip():
            errors.append("approval_reviewer_missing")
        if not str(approval.get("reviewed_at", "")).strip():
            errors.append("approval_reviewed_at_missing")
        if not str(approval.get("design_intent", "")).strip():
            errors.append("approval_design_intent_missing")
        if not isinstance(approval.get("qor"), dict) or not approval.get("qor"):
            errors.append("approval_qor_review_missing")
        reviewed_gates = {str(value) for value in approval.get("gates_reviewed", []) if value}
        missing_gates = sorted(set(PROMOTION_REVIEW_GATES) - reviewed_gates)
        if missing_gates:
            errors.append("approval_gates_missing:" + ",".join(missing_gates))
        return {
            "status": "APPROVED" if not errors else "INVALID",
            "approval_file": str(path.relative_to(self.root)),
            "expected": expected,
            "errors": sorted(set(errors)),
            "approval_sha256": file_hash(path) if path.is_file() else None,
        }

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
        ports = self.freeze_ports(contract.get("interface", {}) or {})
        rtl_blockers = self.validate_rtl(source, ports)
        if rtl_blockers:
            raise RuntimeError(f"library promotion RTL boundary failed for {cid}: {rtl_blockers}")
        canonical_source, rtl_sha256 = self.canonical_rtl_source(cid, source)
        canonical_bytes = canonical_source.encode("utf-8")
        module_name = safe_identifier(cid).lower()
        contract_hash = str(item.get("contract_hash") or artifact.name)
        artifact_relative = self.artifact_reference(artifact)
        accepted = self.accepted_rtl_component(cid, contract_hash, contract=contract)
        if item.get("reuse_accepted_rtl") and accepted and accepted.get("module_sha256") == rtl_sha256:
            return {
                "status": "VERIFIED_REFRESH",
                "contract_id": cid,
                "module": module_name,
                "module_file": accepted["module_file"],
                "artifact_dir": artifact_relative,
                "rtl_sha256": rtl_sha256,
                "contract_hash": contract_hash,
                "approval": {"status": "NOT_REQUIRED", "reason": "existing_accepted_rtl_unchanged"},
            }
        approval = self.promotion_approval(contract, item, rtl_sha256)
        if approval.get("status") != "APPROVED":
            return {
                "status": "AWAITING_HUMAN_APPROVAL",
                "contract_id": cid,
                "module": module_name,
                "artifact_dir": artifact_relative,
                "rtl_sha256": rtl_sha256,
                "contract_hash": contract_hash,
                "approval": approval,
                "reason": "human promotion approval required for this exact candidate",
            }
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
                    "scope": matrix.get("matrix_scope"),
                    "profiles_selected": matrix.get("matrix_profiles_selected"),
                    "evidence_summary": matrix.get("evidence_summary", {}),
                    "modes": {
                        mode: (matrix.get("modes", {}).get(mode, {}) or {}).get("status")
                        for mode in ("C_ONLY", "SHADOW", "RTL_RETURN")
                    },
                    "scripts_discovered": matrix.get("matrix_scripts_discovered"),
                    "phase_order": matrix.get("phase_order", []),
                    "decode": {
                        "status": (matrix.get("decode", {}) or {}).get("status"),
                        "coverage_status": (matrix.get("decode", {}) or {}).get("coverage_status"),
                        "comparison": (matrix.get("decode", {}) or {}).get("comparison"),
                    },
                    "encode": {
                        "status": (matrix.get("encode", {}) or {}).get("status"),
                        "comparison": (matrix.get("encode", {}) or {}).get("comparison"),
                    },
                    "replacement_coverage": matrix.get("replacement_coverage", {}),
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
                "approval_file": approval.get("approval_file"),
                "approval_sha256": approval.get("approval_sha256"),
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
                "approval_file": approval.get("approval_file"),
                "approval_sha256": approval.get("approval_sha256"),
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

    def render_populate_orig_line_oracle(
        self,
        contract: dict[str, Any],
        inputs: list[dict[str, Any]],
    ) -> str:
        """Render the bounded transaction oracle around the immutable C leaf.

        The source image is deliberately uniform per vector.  That keeps the
        oracle memory finite while still exercising the original function for
        the touched line element; the request metadata is emitted by the
        same source-derived transaction relation frozen in the contract.
        The production overlay remains request-driven and never uses this
        helper to calculate a picture address.
        """
        function = contract_function(contract)
        name = str(function.get("name"))
        parameters = self.function_parameters(contract)
        if len(parameters) != 4:
            raise RuntimeError("PopulateOrigLine oracle requires four C parameters")
        semantics = contract.get("semantics", {}) or {}
        bindings = semantics.get("bindings", {}) or {}
        input_names = [str(port.get("name")) for port in inputs]
        output_names = [
            str(port.get("name"))
            for port in (contract.get("interface", {}) or {}).get("ports", [])
            if port.get("direction") == "output"
        ]
        required_inputs = [
            str(bindings.get(key, ""))
            for key in (
                "native_420_port",
                "native_422_port",
                "xstart_port",
                "ystart_port",
                "num_components_port",
                "slice_width_port",
                "picture_width_port",
                "picture_height_port",
                "vpos_port",
                "component_port",
                "sample_index_port",
                "component_depth_port",
                "pixel_data_port",
            )
        ]
        if required_inputs != input_names:
            raise RuntimeError("PopulateOrigLine oracle input bindings are incomplete")
        if output_names != [
            "read_enable",
            "read_plane",
            "read_y",
            "read_x",
            "write_enable",
            "write_component",
            "write_address",
            "write_value",
            "illegal_domain",
        ]:
            raise RuntimeError("PopulateOrigLine oracle output bindings are incomplete")
        parameter_declarations = ", ".join(
            f"{str(parameter.get('type', 'int')).strip()} {parameter.get('name')}"
            for parameter in parameters
        )
        parameter_names = [str(parameter.get("name")) for parameter in parameters]
        input_declarations = ", ".join(f"int {name}" for name in input_names)
        input_local_declarations = ", ".join(input_names)
        input_variables = ", ".join(f"&{name}" for name in input_names)
        input_format = " ".join(["%d"] * len(input_names))
        cfg_name = str(bindings.get("config_parameter", "dsc_cfg"))
        state_name = str(bindings.get("state_parameter", "dsc_state"))
        picture_name = str(bindings.get("picture_parameter", "ip"))
        vpos_name = str(bindings.get("vpos_parameter", "vPos"))
        vpos_port = str(bindings.get("vpos_port", "vpos"))
        cfg_fields = {
            "native_420": str(bindings.get("native_420_field", "native_420")),
            "native_422": str(bindings.get("native_422_field", "native_422")),
            "xstart": str(bindings.get("xstart_field", "xstart")),
            "ystart": str(bindings.get("ystart_field", "ystart")),
        }
        state_fields = {
            "num_components": str(bindings.get("num_components_field", "numComponents")),
            "slice_width": str(bindings.get("slice_width_field", "sliceWidth")),
            "component_depth": str(bindings.get("component_depth_field", "cpntBitDepth")),
        }
        max_components = int(semantics.get("component_count", 4) or 4)
        padding_left = int(semantics.get("padding_left", 5) or 5)
        padding_right = int(semantics.get("padding_right", 10) or 10)
        output_values = {
            "read_enable": "dsc_cicd_read_enable",
            "read_plane": "dsc_cicd_read_plane",
            "read_y": "dsc_cicd_read_y",
            "read_x": "dsc_cicd_read_x",
            "write_enable": "dsc_cicd_write_enable",
            "write_component": "dsc_cicd_write_component",
            "write_address": "dsc_cicd_write_address",
            "write_value": "dsc_cicd_write_value",
            "illegal_domain": "dsc_cicd_illegal_domain",
        }
        lines = [
            "#include <stdio.h>",
            "#include <stdlib.h>",
            "#include <string.h>",
            "#include \"dsc_types.h\"",
            f"extern void {name}({parameter_declarations});",
            "static int dsc_cicd_min(int left, int right) { return left < right ? left : right; }",
            "static void dsc_cicd_free_rows(int **rows, int height) {",
            "    if (!rows) return;",
            "    for (int row = 0; row < height; ++row) free(rows[row]);",
            "    free(rows);",
            "}",
            "static void dsc_cicd_reference_request(",
            "    int native_420, int native_422, int xstart, int ystart,",
            "    int slice_width, int pic_width, int pic_height, int vpos,",
            "    int component, int sample_index, int component_depth, int pixel_data,",
            "    int *read_enable, int *read_plane, int *read_y, int *read_x,",
            "    int *write_enable, int *write_component, int *write_address,",
            "    int *write_value, int *illegal_domain) {",
            "    int legal = 1;",
            "    if (native_420 && native_422) legal = 0;",
            "    if (component < 0 || component > 3 || sample_index < 0 || slice_width < 1 ||",
            "        sample_index >= slice_width + PADDING_RIGHT || pic_width < 1 || pic_height < 1 ||",
            "        vpos < 0 || component_depth < 1 || component_depth > 30) legal = 0;",
            "    if (!native_422 && component > 2) legal = 0;",
            "    *read_enable = 0; *read_plane = 0; *read_y = 0; *read_x = 0;",
            "    *write_enable = 0; *write_component = 0; *write_address = 0;",
            "    *write_value = 0; *illegal_domain = legal ? 0 : 1;",
            "    if (!legal) return;",
            "    int xstart_i = xstart >> (native_420 || native_422);",
            "    int picture_width_i = pic_width;",
            "    if (native_422 && component >= 1 && component <= 2) picture_width_i >>= 1;",
            "    int last_position_i;",
            "    if (native_422 && (component == 0 || component == 3))",
            "        last_position_i = dsc_cicd_min(picture_width_i, (xstart_i + slice_width) * 2) - 1;",
            "    else",
            "        last_position_i = dsc_cicd_min(picture_width_i, xstart_i + slice_width) - 1;",
            "    int x_index_i;",
            "    if (native_422 && component == 0) { *read_plane = 0; x_index_i = (xstart_i + sample_index) * 2; }",
            "    else if (native_422 && component == 1) { *read_plane = 1; x_index_i = xstart_i + sample_index; }",
            "    else if (native_422 && component == 2) { *read_plane = 2; x_index_i = xstart_i + sample_index; }",
            "    else if (native_422 && component == 3) { *read_plane = 0; x_index_i = (xstart_i + sample_index) * 2 + 1; }",
            "    else if (component == 0) { *read_plane = 0; x_index_i = xstart_i + sample_index; }",
            "    else if (component == 1) { *read_plane = 1; x_index_i = xstart_i + sample_index; }",
            "    else { *read_plane = 2; x_index_i = xstart_i + sample_index; }",
            "    if (x_index_i > last_position_i) x_index_i = last_position_i;",
            "    int y_raw_i = ystart + vpos;",
            "    *read_enable = y_raw_i < pic_height;",
            "    *read_y = y_raw_i < pic_height ? y_raw_i : pic_height - 1;",
            "    *read_x = x_index_i;",
            "    *write_enable = 1; *write_component = component;",
            "    *write_address = sample_index + PADDING_LEFT;",
            "    *write_value = *read_enable ? pixel_data : (1 << (component_depth - 1));",
            "}",
            "int main(int argc, char **argv) {",
            "    FILE *input = stdin;",
            "    if (argc > 1) { input = fopen(argv[1], \"rb\"); if (!input) return 2; }",
            f"    int {input_local_declarations};",
            "    while (fscanf(input, \"" + input_format + "\", " + input_variables + f") == {len(input_names)}) {{",
            f"        dsc_cfg_t {cfg_name} = {{0}};",
            f"        dsc_state_t {state_name} = {{0}};",
            f"        pic_t {picture_name} = {{0}};",
            f"        {cfg_name}.{cfg_fields['native_420']} = native_420;",
            f"        {cfg_name}.{cfg_fields['native_422']} = native_422;",
            f"        {cfg_name}.{cfg_fields['xstart']} = xstart;",
            f"        {cfg_name}.{cfg_fields['ystart']} = ystart;",
            f"        {state_name}.{state_fields['num_components']} = num_components;",
            f"        {state_name}.{state_fields['slice_width']} = slice_width;",
            f"        {picture_name}.w = pic_width; {picture_name}.h = pic_height;",
            f"        int *dsc_cicd_line[{max_components}] = {{0}};",
            "        int **dsc_cicd_y = (int **)calloc((size_t)pic_height, sizeof(int *));",
            "        int **dsc_cicd_u = (int **)calloc((size_t)pic_height, sizeof(int *));",
            "        int **dsc_cicd_v = (int **)calloc((size_t)pic_height, sizeof(int *));",
            "        for (int row = 0; row < pic_height; ++row) {",
            "            dsc_cicd_y[row] = (int *)calloc((size_t)pic_width, sizeof(int));",
            "            dsc_cicd_u[row] = (int *)calloc((size_t)pic_width, sizeof(int));",
            "            dsc_cicd_v[row] = (int *)calloc((size_t)pic_width, sizeof(int));",
            "            for (int col = 0; col < pic_width; ++col) {",
            "                dsc_cicd_y[row][col] = pixel_data; dsc_cicd_u[row][col] = pixel_data; dsc_cicd_v[row][col] = pixel_data;",
            "            }",
            "        }",
            f"        {picture_name}.data.yuv.y = dsc_cicd_y; {picture_name}.data.yuv.u = dsc_cicd_u; {picture_name}.data.yuv.v = dsc_cicd_v;",
            f"        for (int cpnt = 0; cpnt < num_components; ++cpnt) {{ {state_name}.{state_fields['component_depth']}[cpnt] = component_bit_depth; dsc_cicd_line[cpnt] = (int *)calloc((size_t)(slice_width + PADDING_LEFT + PADDING_RIGHT), sizeof(int)); {state_name}.origLine[cpnt] = dsc_cicd_line[cpnt]; }}",
            f"        {name}(&{cfg_name}, &{state_name}, &{picture_name}, {vpos_port});",
            "        int dsc_cicd_read_enable, dsc_cicd_read_plane, dsc_cicd_read_y, dsc_cicd_read_x;",
            "        int dsc_cicd_write_enable, dsc_cicd_write_component, dsc_cicd_write_address, dsc_cicd_write_value, dsc_cicd_illegal_domain;",
            "        dsc_cicd_reference_request(native_420, native_422, xstart, ystart, slice_width, pic_width, pic_height, vpos, component, sample_index, component_bit_depth, pixel_data, &dsc_cicd_read_enable, &dsc_cicd_read_plane, &dsc_cicd_read_y, &dsc_cicd_read_x, &dsc_cicd_write_enable, &dsc_cicd_write_component, &dsc_cicd_write_address, &dsc_cicd_write_value, &dsc_cicd_illegal_domain);",
            "        if (!dsc_cicd_illegal_domain) dsc_cicd_write_value = dsc_cicd_line[component][sample_index + PADDING_LEFT];",
            "        printf(\"%d %d %d %d %d %d %d %d %d\\n\", dsc_cicd_read_enable, dsc_cicd_read_plane, dsc_cicd_read_y, dsc_cicd_read_x, dsc_cicd_write_enable, dsc_cicd_write_component, dsc_cicd_write_address, dsc_cicd_write_value, dsc_cicd_illegal_domain);",
            f"        for (int cpnt = 0; cpnt < num_components; ++cpnt) free(dsc_cicd_line[cpnt]);",
            "        dsc_cicd_free_rows(dsc_cicd_y, pic_height); dsc_cicd_free_rows(dsc_cicd_u, pic_height); dsc_cicd_free_rows(dsc_cicd_v, pic_height);",
            "    }",
            "    if (input != stdin) fclose(input);",
            "    return 0;",
            "}",
        ]
        return "\n".join(lines) + "\n"

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
        if (contract.get("semantics", {}) or {}).get("kind") == "populate_orig_line_memory_transition":
            return self.render_populate_orig_line_oracle(contract, inputs)
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

    def populate_orig_line_vector_iterator(
        self,
        contract: dict[str, Any],
        input_ports: list[dict[str, Any]],
        values: list[list[int]],
        strategy: dict[str, Any],
    ) -> tuple[Iterable[tuple[int, ...]], dict[str, Any]]:
        """Generate bounded request/response cases for the picture leaf."""
        names = [str(port.get("name")) for port in input_ports]
        by_name = {name: [int(value) for value in values[index]] for index, name in enumerate(names)}
        required = {
            "native_420", "native_422", "xstart", "ystart", "num_components",
            "slice_width", "pic_width", "pic_height", "vpos", "component",
            "sample_index", "component_bit_depth", "pixel_data",
        }
        if not required.issubset(by_name):
            raise RuntimeError("PopulateOrigLine vector strategy ports are incomplete")

        def choose(port_name: str, requested: Iterable[int]) -> list[int]:
            legal = set(by_name[port_name])
            return list(dict.fromkeys(int(value) for value in requested if int(value) in legal))

        native_420_values = choose("native_420", [0, 1])
        native_422_values = choose("native_422", [0, 1])
        x_values = choose("xstart", [0, 1, 2, 5, 16])
        ystart_values = choose("ystart", [0, 1, 2, 5])
        width_values = choose("slice_width", [1, 2, 3, 4, 8, 16, 31])
        picture_width_values = choose("pic_width", [1, 2, 3, 4, 8, 16, 31])
        picture_height_values = choose("pic_height", [1, 2, 3, 4, 8, 16])
        depth_values = choose("component_bit_depth", [8, 10, 12, 16])
        pixel_values = choose("pixel_data", [0, 1, 127, 255, 1023, 65535])
        if not all((native_420_values, native_422_values, x_values, ystart_values,
                    width_values, picture_width_values, picture_height_values,
                    depth_values, pixel_values)):
            raise RuntimeError("PopulateOrigLine vector strategy has an empty legal probe")

        def emit(context: dict[str, int]) -> tuple[int, ...]:
            return tuple(int(context[name]) for name in names)

        vectors: list[tuple[int, ...]] = []
        seen: set[tuple[int, ...]] = set()
        for native_420, native_422, component_count, components in (
            (0, 0, 3, (0, 1, 2)),
            (1, 0, 3, (0, 1, 2)),
            (0, 1, 4, (0, 1, 2, 3)),
        ):
            if native_420 not in native_420_values or native_422 not in native_422_values:
                continue
            mode_vector_count = 0
            for slice_width in width_values:
                sample_values = choose(
                    "sample_index",
                    [0, max(0, slice_width - 1), slice_width, slice_width + int(contract["semantics"].get("padding_right", 10)) - 1],
                )
                for pic_width in picture_width_values:
                    if native_422 and pic_width < 2:
                        continue
                    for pic_height in picture_height_values:
                        for vpos in choose("vpos", [0, 1, max(0, pic_height - 1), pic_height]):
                            for component in components:
                                for sample_index in sample_values:
                                    for pixel_data in pixel_values:
                                        context = {
                                            name: int(domain[len(domain) // 2])
                                            for name, domain in by_name.items()
                                            if domain
                                        }
                                        context.update({
                                            "native_420": native_420,
                                            "native_422": native_422,
                                            "xstart": x_values[(slice_width + component) % len(x_values)],
                                            "ystart": ystart_values[(pic_height + component) % len(ystart_values)],
                                            "num_components": component_count,
                                            "slice_width": slice_width,
                                            "pic_width": pic_width,
                                            "pic_height": pic_height,
                                            "vpos": vpos,
                                            "component": component,
                                            "sample_index": sample_index,
                                            "component_bit_depth": depth_values[(component + sample_index) % len(depth_values)],
                                            "pixel_data": pixel_data,
                                        })
                                        vector = emit(context)
                                        if mode_vector_count >= 5000:
                                            continue
                                        if vector in seen:
                                            continue
                                        seen.add(vector)
                                        vectors.append(vector)
                                        mode_vector_count += 1

        return iter(vectors), {
            "kind": "populate_orig_line",
            "exhaustive": False,
            "formal_required": False,
            "coverage_mode": str(strategy.get("coverage_mode", "request-and-write-boundaries")),
            "vectors": len(vectors),
            "source": "tool-driven native plane mapping, clamp, bottom midpoint, and padded-address probes",
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
        if isinstance(table_strategy, dict) and table_strategy.get("kind") == "populate_orig_line":
            return self.populate_orig_line_vector_iterator(contract, input_ports, values, table_strategy)
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

    @staticmethod
    def preserve_generated_history(output_dir: pathlib.Path) -> pathlib.Path | None:
        """Move prior generated candidates aside before a new materialization."""
        if not output_dir.is_dir():
            return None
        prior = [path for path in output_dir.iterdir() if path.name != "history"]
        if not prior:
            return None
        stamp = time.strftime("%Y%m%dT%H%M%SZ", time.gmtime())
        history_root = output_dir / "history" / stamp
        suffix = 1
        while history_root.exists():
            suffix += 1
            history_root = output_dir / "history" / f"{stamp}-{suffix:02d}"
        history_root.mkdir(parents=True, exist_ok=True)
        for path in prior:
            shutil.move(str(path), str(history_root / path.name))
        return history_root

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
        resume_pending = bool(item.get("resume_human_approval"))
        if output_dir.exists() and not resume_pending:
            self.preserve_generated_history(output_dir)
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
        if resume_pending:
            candidate_path = output_dir / "candidate_01.sv"
            expected_sha256 = str(item.get("pending_rtl_sha256") or "")
            reasons = []
            if not candidate_path.is_file():
                reasons.append("pending_approval_candidate_missing")
            if candidate_path.is_file():
                source = candidate_path.read_text(encoding="utf-8", errors="replace")
                reasons.extend(self.validate_rtl(source, contract.get("interface", {}).get("ports", [])))
                try:
                    module = self.module_name(source)
                    _, canonical_sha256 = self.canonical_rtl_source(contract_id(contract), source)
                    if expected_sha256 and canonical_sha256 != expected_sha256:
                        reasons.append("pending_approval_candidate_hash_mismatch")
                except RuntimeError:
                    module = None
                    reasons.append("pending_approval_module_not_discoverable")
            else:
                module = None
            if reasons:
                receipt.update({
                    "execution_status": "REUSED_PENDING_APPROVAL_RTL",
                    "status": "INFRASTRUCTURE_FAILURE",
                    "model_calls": 0,
                    "tokens": 0,
                    "candidates": [],
                    "hook": "NOT_USED",
                    "reason": "; ".join(sorted(set(reasons))),
                })
                write_json(artifact / "generation.json", receipt)
                return receipt
            candidate = {
                "candidate": "candidate_01",
                "path": str(candidate_path.relative_to(artifact)),
                "module": module,
                "sha256": file_hash(candidate_path),
                "validation": "PASS",
                "validation_reasons": [],
            }
            receipt.update({
                "execution_status": "REUSED_PENDING_APPROVAL_RTL",
                "status": "PASS",
                "model_calls": 0,
                "tokens": 0,
                "candidates": [candidate],
                "hook": "NOT_USED",
                "pending_approval": {"reason": "resume_exact_candidate_after_human_review"},
            })
            write_json(artifact / "generation.json", receipt)
            return receipt
        if item.get("reuse_accepted_rtl"):
            component = self.accepted_rtl_component(
                contract_id(contract),
                str(item.get("contract_hash") or digest(contract)),
                contract=contract,
            )
            if not component:
                receipt.update({
                    "execution_status": "REUSED_ACCEPTED_RTL",
                    "status": "INFRASTRUCTURE_FAILURE",
                    "model_calls": 0,
                    "tokens": 0,
                    "candidates": [],
                    "hook": "NOT_USED",
                    "reason": "accepted_rtl_component_unavailable_or_hash_mismatch",
                })
                write_json(artifact / "generation.json", receipt)
                return receipt
            source = component["module_path"].read_text(encoding="utf-8", errors="replace")
            reasons = self.validate_rtl(source, contract.get("interface", {}).get("ports", []))
            scrubbed = re.sub(r"//.*|/\*.*?\*/", "", source, flags=re.S)
            modules = list(re.finditer(r"\bmodule\s+[A-Za-z_][A-Za-z0-9_]*", scrubbed))
            if len(modules) != 1 or len(re.findall(r"\bendmodule\b", scrubbed)) != 1:
                reasons.append("accepted_rtl_must_contain_one_module")
            try:
                module = self.module_name(source)
            except RuntimeError:
                module = None
                reasons.append("accepted_rtl_module_not_discoverable")
            if reasons:
                receipt.update({
                    "execution_status": "REUSED_ACCEPTED_RTL",
                    "status": "INFRASTRUCTURE_FAILURE",
                    "model_calls": 0,
                    "tokens": 0,
                    "candidates": [],
                    "hook": "NOT_USED",
                    "accepted_rtl": {
                        "library_file": component["module_file"],
                        "module_sha256": component["module_sha256"],
                    },
                    "reason": "accepted_rtl_validation_failed: " + "; ".join(sorted(set(reasons))),
                })
                write_json(artifact / "generation.json", receipt)
                return receipt
            candidate_path = output_dir / "candidate_01.sv"
            shutil.copy2(component["module_path"], candidate_path)
            candidate = {
                "candidate": "candidate_01",
                "path": str(candidate_path.relative_to(artifact)),
                "module": module,
                "sha256": file_hash(candidate_path),
                "validation": "PASS",
                "validation_reasons": [],
            }
            receipt.update({
                "execution_status": "REUSED_ACCEPTED_RTL",
                "status": "PASS",
                "model_calls": 0,
                "tokens": 0,
                "candidates": [candidate],
                "hook": "NOT_USED",
                "accepted_rtl": {
                    "library_file": component["module_file"],
                    "module": module,
                    "module_sha256": component["module_sha256"],
                    "contract_hash": component["contract_hash"],
                    "reason": "bounded_stable_refresh",
                },
            })
            write_json(artifact / "generation.json", receipt)
            return receipt
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
        build_inputs = [
            self.root / "tools" / "CMakeLists.txt",
            self.root / "tools" / "clang_rewrite_overlay.cpp",
        ]
        fingerprint = digest([
            {"path": str(path.relative_to(self.root)), "sha256": file_hash(path)}
            for path in build_inputs
        ])
        fingerprint_path = build_dir / "source-fingerprint.txt"
        if (
            binary.is_file()
            and fingerprint_path.is_file()
            and fingerprint_path.read_text(encoding="utf-8").strip() == fingerprint
        ):
            return binary, {
                "status": "REUSED_BUILD",
                "binary": str(binary),
                "source_fingerprint": fingerprint,
            }
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
        fingerprint_path.write_text(fingerprint + "\n", encoding="utf-8")
        return binary, {
            "status": "BUILT",
            "binary": str(binary),
            "source_fingerprint": fingerprint,
            "configure": configure,
            "build": build,
        }

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

    def run_overlay_rewriter(
        self,
        contract: dict[str, Any],
        source_dir: pathlib.Path,
        overlay_header: pathlib.Path,
        allow_residual_symbol_alias: bool = False,
        *,
        original_name: str | None = None,
        dispatcher_name: str = "dsc_cicd_invoke",
        receipt_name: str = "clang-overlay-receipt.json",
    ) -> dict[str, Any]:
        binary, build_receipt = self.ensure_rewriter()
        if not binary:
            return build_receipt
        compdb = source_dir / "compile_commands.json"
        sources = self.write_compdb_for_copy(source_dir, compdb)
        rewrite_sources = [
            path for path in sources if not path.name.startswith("dsc_cicd_")
        ]
        before = {str(path.relative_to(source_dir)): file_hash(path) for path in sources}
        cid = contract_id(contract)
        function = contract_function(contract)
        original_name = original_name or str(function.get("name")) + "_original"
        receipt_path = source_dir / receipt_name
        command = [
            str(binary),
            "--compdb", str(compdb),
            "--target-usr", str(function.get("clang_usr")),
            "--original-name", original_name,
            "--dispatcher-name", dispatcher_name,
            "--receipt", str(receipt_path),
        ] + [str(path) for path in rewrite_sources]
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
        failures = [str(value) for value in tool_receipt.get("failures", [])]
        alias_safe_failure_prefixes = (
            "selected function reference is not a direct call at ",
            "selected function is called indirectly at ",
            "direct target call is inside a macro expansion",
        )
        residual_alias_accepted = bool(
            allow_residual_symbol_alias
            and tool_receipt.get("definitions_seen") == 1
            and tool_receipt.get("rewritten_calls")
            == tool_receipt.get("direct_calls_seen")
            and failures
            and all(
                failure.startswith(alias_safe_failure_prefixes)
                for failure in failures
            )
        )
        if (
            tool_receipt.get("status") == "PASS" and result["returncode"] == 0
        ) or residual_alias_accepted:
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
            "direct_reference_locations": tool_receipt.get(
                "direct_reference_locations", []
            ),
            "pending_reference_locations": tool_receipt.get(
                "pending_reference_locations", []
            ),
            "macro_locations": tool_receipt.get("macro_locations", []),
            "indirect_locations": tool_receipt.get("indirect_locations", []),
            "failures": failures,
            "residual_symbol_alias": {
                "declared_by_adapter": allow_residual_symbol_alias,
                "accepted": residual_alias_accepted,
                "policy": (
                    "definition must be renamed exactly once; every recognized direct call "
                    "must be rewritten; only residual references routed by the generated "
                    "same-name dispatcher alias may remain"
                ),
            },
            "tool": build_receipt,
            "command": result,
        }
        write_json(source_dir / "overlay-receipt.json", receipt)
        return receipt

    @staticmethod
    def overlay_runtime_metrics_source() -> str:
        """Emit one machine-readable invocation summary at normal process exit."""
        return (
            "static unsigned long dsc_cicd_mismatches;\n"
            "static unsigned long dsc_cicd_calls;\n"
            "static unsigned long dsc_cicd_rtl_invocations;\n"
            "static int dsc_cicd_report_registered;\n"
            "static void dsc_cicd_report(void) {\n"
            "    fprintf(stderr, \"DSC_CICD_OVERLAY_METRICS calls=%lu "
            "rtl_invocations=%lu mismatches=%lu\\n\",\n"
            "            dsc_cicd_calls, dsc_cicd_rtl_invocations, "
            "dsc_cicd_mismatches);\n"
            "}\n"
            "static void dsc_cicd_note_call(int mode) {\n"
            "    if (!dsc_cicd_report_registered) {\n"
            "        atexit(dsc_cicd_report);\n"
            "        dsc_cicd_report_registered = 1;\n"
            "    }\n"
            "    ++dsc_cicd_calls;\n"
            "    if (mode != 0) ++dsc_cicd_rtl_invocations;\n"
            "}\n"
        )

    def write_flatness_overlay_sources(
        self,
        contract: dict[str, Any],
        source_dir: pathlib.Path,
        module: str,
        candidate_sv: pathlib.Path,
    ) -> dict[str, Any]:
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
            + self.overlay_runtime_metrics_source()
            + f"int dsc_cicd_invoke({caller_declarations}) {{\n"
            f"    int c_value = {original}({caller_call});\n"
            "    int mode = dsc_cicd_mode();\n"
            "    dsc_cicd_note_call(mode);\n"
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
        return {
            "header": header,
            "overlay": overlay,
            "bridge": bridge,
            "main": main,
            "candidate": candidate_sv,
            "composition": {
                "status": "PASS",
                "adapter_kind": "reviewed_window",
                "caller_parameter_count": len(parameters),
                "rtl_input_count": len(rtl_arguments),
                "frozen_input_ports": [str(port.get("name")) for port in inputs],
                "rtl_bindings": list(rtl_arguments),
            },
        }

    def write_ich_decision_overlay_sources(
        self,
        contract: dict[str, Any],
        source_dir: pathlib.Path,
        module: str,
        candidate_sv: pathlib.Path,
    ) -> dict[str, Any]:
        """Write a caller adapter for a reviewed semantic ICH decision.

        The frozen RTL interface is a scalar projection of the native C
        configuration/state records.  The C callsite must keep its original
        five-argument signature, while the adapter expands those records into
        the scalar DUT ports using the reviewed legal-vector strategy.  This
        binding is contract-driven; it does not identify a function by name or
        guess fields from the generated RTL.
        """
        interface = contract.get("interface", {}) or {}
        ports = [port for port in interface.get("ports", []) if isinstance(port, dict)]
        inputs = [port for port in ports if port.get("direction") == "input"]
        outputs = [port for port in ports if port.get("direction") == "output"]
        if len(outputs) != 1:
            raise RuntimeError("ich-decision overlay requires exactly one output port")
        output = outputs[0]
        semantics = contract.get("semantics", {}) or {}
        strategy = semantics.get("legal_vector_strategy", {}) or {}
        if not isinstance(strategy, dict):
            raise RuntimeError("ich-decision overlay is missing legal vector strategy")
        parameters = self.function_parameters(contract)
        if not parameters:
            raise RuntimeError("ich-decision overlay requires original C parameter facts")

        parameter_specs: list[str] = []
        parameter_names: list[str] = []
        pointer_records: dict[str, str] = {}
        scalar_parameters: set[str] = set()
        for parameter in parameters:
            parameter_name = str(parameter.get("name", ""))
            parameter_type = str(parameter.get("type", "int")).strip()
            if not parameter_name or not re.match(r"^[A-Za-z_][A-Za-z0-9_]*$", parameter_name):
                raise RuntimeError(f"invalid C parameter name: {parameter_name}")
            parameter_specs.append(f"{parameter_type} {parameter_name}")
            parameter_names.append(parameter_name)
            if parameter.get("pointer"):
                record_type = re.sub(r"\s*\*.*$", "", parameter_type).strip()
                pointer_records[record_type] = parameter_name
            else:
                scalar_parameters.add(parameter_name)
        config_parameter = pointer_records.get("dsc_cfg_t")
        state_parameter = pointer_records.get("dsc_state_t")
        if not config_parameter or not state_parameter:
            raise RuntimeError("ich-decision overlay requires dsc_cfg_t and dsc_state_t parameters")

        input_names = {str(port.get("name")) for port in inputs}

        def require_port(key: str, fallback: str) -> str:
            name = str(strategy.get(key, fallback))
            if name not in input_names:
                raise RuntimeError(f"ich-decision binding is not an input port: {name}")
            return name

        def require_scalar_port(key: str, fallback: str) -> str:
            name = require_port(key, fallback)
            if name not in scalar_parameters:
                raise RuntimeError(f"ich-decision scalar binding is not a C parameter: {name}")
            return name

        def require_group(key: str, length: int) -> list[str]:
            values = strategy.get(key, [])
            if not isinstance(values, list) or len(values) != length:
                raise RuntimeError(f"ich-decision binding requires {length} ports for {key}")
            result = [str(value) for value in values]
            if any(value not in input_names for value in result):
                raise RuntimeError(f"ich-decision binding has a missing port for {key}")
            return result

        cfg_fields = {
            require_port("version_port", "dsc_version_minor"): f"{config_parameter}->dsc_version_minor",
            require_port("native_420_port", "native_420"): f"{config_parameter}->native_420",
            require_port("flatness_det_thresh_port", "flatness_det_thresh"):
                f"{config_parameter}->flatness_det_thresh",
            require_port("somewhat_flat_qp_delta_port", "somewhat_flat_qp_delta"):
                f"{config_parameter}->somewhat_flat_qp_delta",
        }
        state_fields = {
            require_port("units_per_group_port", "units_per_group"): f"{state_parameter}->unitsPerGroup",
            require_port("pixels_in_group_port", "pixels_in_group"): f"{state_parameter}->pixelsInGroup",
            require_port("hpos_port", "hPos"): f"{state_parameter}->hPos",
            require_port("slice_width_port", "slice_width"): f"{state_parameter}->sliceWidth",
            require_port("prev_ich_selected_port", "prev_ich_selected"):
                f"{state_parameter}->prevIchSelected",
            require_port("primary_qp_port", "primary_qp"): f"{state_parameter}->primaryQp",
            require_port("prev_primary_qp_port", "prev_primary_qp"):
                f"{state_parameter}->prevPrimaryQp",
            require_port("ich_indices_in_group_port", "ich_indices_in_group"):
                f"{state_parameter}->ichIndicesInGroup",
            require_port("num_components_port", "num_components"): f"{state_parameter}->numComponents",
        }
        depth_ports = require_group("component_depth_ports", 4)
        ctype_ports = require_group("unit_component_ports", 4)
        start_ports = require_group("unit_start_hpos_ports", 4)
        predicted_ports = require_group("predicted_size_ports", 4)
        max_error_ports = require_group("max_error_ports", 4)
        max_mid_error_ports = require_group("max_mid_error_ports", 4)
        max_ich_error_ports = require_group("max_ich_error_ports", 4)
        residual_ports = require_group("residual_ports", 12)
        qlevel_ports = strategy.get("qlevel_ports", {}) or {}
        if not isinstance(qlevel_ports, dict):
            raise RuntimeError("ich-decision overlay is missing qLevel bindings")
        qlevel_names: dict[str, str] = {}
        for key in ("luma_primary", "chroma_primary", "luma_previous",
                    "chroma_previous", "luma_flat", "chroma_flat"):
            if key not in qlevel_ports:
                raise RuntimeError("ich-decision overlay is missing a qLevel port")
            qlevel_names[key] = require_port(key, str(qlevel_ports[key]))
        orig_ports = strategy.get("orig_ports_by_component", {}) or {}
        if not isinstance(orig_ports, dict):
            raise RuntimeError("ich-decision overlay is missing original-pixel bindings")
        orig_names: dict[int, list[str]] = {}
        for component in range(4):
            raw = orig_ports.get(str(component), orig_ports.get(component, []))
            if not isinstance(raw, list) or len(raw) != 7:
                raise RuntimeError("ich-decision overlay requires seven original taps per component")
            values = [str(value) for value in raw]
            if any(value not in input_names for value in values):
                raise RuntimeError("ich-decision overlay has a missing original tap")
            orig_names[component] = values

        scalar_ports = {
            require_scalar_port("adj_predicted_size_port", "adj_predicted_size"),
            require_scalar_port("alt_pfx_port", "alt_pfx"),
            require_scalar_port("alt_size_to_generate_port", "alt_size_to_generate"),
        }
        expressions: dict[str, str] = {}
        expressions.update(cfg_fields)
        expressions.update(state_fields)
        for index, port in enumerate(depth_ports):
            expressions[port] = f"{state_parameter}->cpntBitDepth[{index}]"
        for index, port in enumerate(ctype_ports):
            expressions[port] = f"{state_parameter}->unitCType[{index}]"
        for index, port in enumerate(start_ports):
            expressions[port] = f"{state_parameter}->unitStartHPos[{index}]"
        for index, port in enumerate(predicted_ports):
            expressions[port] = f"{state_parameter}->predictedSize[{index}]"
        for index, port in enumerate(max_error_ports):
            expressions[port] = f"{state_parameter}->maxError[{index}]"
        for index, port in enumerate(max_mid_error_ports):
            expressions[port] = f"{state_parameter}->maxMidError[{index}]"
        for index, port in enumerate(max_ich_error_ports):
            expressions[port] = f"{state_parameter}->maxIchError[{index}]"
        for index, port in enumerate(residual_ports):
            unit, sample = divmod(index, 3)
            expressions[port] = f"{state_parameter}->quantizedResidual[{unit}][{sample}]"
        primary_qp = state_fields[require_port("primary_qp_port", "primary_qp")]
        previous_qp = state_fields[require_port("prev_primary_qp_port", "prev_primary_qp")]
        flat_delta = cfg_fields[require_port("somewhat_flat_qp_delta_port", "somewhat_flat_qp_delta")]
        flat_qp = f"(({primary_qp} > {flat_delta}) ? ({primary_qp} - {flat_delta}) : 0)"
        qlevel_qp = {
            "luma_primary": primary_qp,
            "chroma_primary": primary_qp,
            "luma_previous": previous_qp,
            "chroma_previous": previous_qp,
            "luma_flat": flat_qp,
            "chroma_flat": flat_qp,
        }
        for key, port in qlevel_names.items():
            table = "quantTableLuma" if key.startswith("luma_") else "quantTableChroma"
            expressions[port] = f"{state_parameter}->{table}[{qlevel_qp[key]}]"
        for component, taps in orig_names.items():
            for offset, port in enumerate(taps):
                expressions[port] = (
                    f"(({state_parameter}->numComponents > {component}) ? "
                    f"{state_parameter}->origLine[{component}]"
                    f"[PADDING_LEFT + {state_parameter}->hPos + {offset}] : 0)"
                )
        expressions.update({port: port for port in scalar_ports})
        rtl_arguments = []
        for port in inputs:
            name = str(port.get("name"))
            if name not in expressions:
                raise RuntimeError(f"ich-decision overlay has no source binding for port: {name}")
            rtl_arguments.append(expressions[name])

        function = contract_function(contract)
        original = str(function.get("name")) + "_original"
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
            + self.overlay_runtime_metrics_source()
            + f"int dsc_cicd_invoke({caller_declarations}) {{\n"
            f"    int c_value = {original}({caller_call});\n"
            "    int mode = dsc_cicd_mode();\n"
            "    dsc_cicd_note_call(mode);\n"
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
        return {
            "header": header,
            "overlay": overlay,
            "bridge": bridge,
            "main": main,
            "candidate": candidate_sv,
            "composition": {
                "status": "PASS",
                "adapter_kind": "reviewed_ich_decision",
                "caller_parameter_count": len(parameters),
                "rtl_input_count": len(rtl_arguments),
                "frozen_input_ports": [str(port.get("name")) for port in inputs],
                "rtl_bindings": list(rtl_arguments),
            },
        }

    def write_bitstream_read_transition_overlay_sources(
        self,
        contract: dict[str, Any],
        source_dir: pathlib.Path,
        module: str,
        candidate_sv: pathlib.Path,
    ) -> dict[str, Any]:
        """Bind a read-only byte window plus explicit write-through cursor."""
        semantics = contract.get("semantics", {}) or {}
        bindings = semantics.get("bindings", {}) or {}
        interface = contract.get("interface", {}) or {}
        ports = [
            port for port in interface.get("ports", []) if isinstance(port, dict)
        ]
        inputs = [port for port in ports if port.get("direction") == "input"]
        outputs = [port for port in ports if port.get("direction") == "output"]
        input_names = {str(port.get("name")) for port in inputs}
        output_names = {str(port.get("name")) for port in outputs}
        byte_ports = [str(value) for value in bindings.get("byte_ports", [])]
        size_port = str(bindings.get("size_port", ""))
        cursor_port = str(bindings.get("cursor_port", ""))
        sign_port = str(bindings.get("sign_extend_port", ""))
        return_port = str(bindings.get("return_port", ""))
        cursor_output_port = str(bindings.get("cursor_output_port", ""))
        if (
            not byte_ports
            or {size_port, cursor_port, sign_port, *byte_ports} != input_names
            or {return_port, cursor_output_port} != output_names
        ):
            raise RuntimeError("bitstream transition ports do not match the frozen interface")

        parameters = self.function_parameters(contract)
        parameter_by_name = {
            str(parameter.get("name")): parameter for parameter in parameters
        }
        size_parameter = str(bindings.get("size_parameter", ""))
        buffer_parameter = str(bindings.get("buffer_parameter", ""))
        cursor_parameter = str(bindings.get("cursor_parameter", ""))
        sign_parameter = str(bindings.get("sign_extend_parameter", ""))
        required_parameters = {
            size_parameter, buffer_parameter, cursor_parameter, sign_parameter
        }
        if not required_parameters or not required_parameters.issubset(parameter_by_name):
            raise RuntimeError("bitstream transition parameter bindings are incomplete")
        if not parameter_is_pointer(parameter_by_name[buffer_parameter]):
            raise RuntimeError("bitstream transition buffer must be a pointer")
        if not parameter_is_pointer(parameter_by_name[cursor_parameter]):
            raise RuntimeError("bitstream transition cursor must be a pointer")

        parameter_specs = [
            f"{str(parameter.get('type', 'int')).strip()} {parameter.get('name')}"
            for parameter in parameters
        ]
        parameter_names = [str(parameter.get("name")) for parameter in parameters]
        caller_declarations = ", ".join(parameter_specs)
        function_name = str(contract_function(contract).get("name"))
        original = function_name + "_original"
        alias_call = ", ".join(parameter_names)
        c_call = ", ".join(
            "&dsc_cicd_c_cursor" if name == cursor_parameter else name
            for name in parameter_names
        )
        input_declarations = ", ".join(
            f"int {port['name']}" for port in inputs
        )
        rtl_expressions = {
            size_port: size_parameter,
            cursor_port: "dsc_cicd_cursor_before",
            sign_port: sign_parameter,
        }
        for index, port in enumerate(byte_ports):
            rtl_expressions[port] = f"dsc_cicd_byte_{index}"
        rtl_arguments = [rtl_expressions[str(port["name"])] for port in inputs]
        rtl_call = ", ".join([*rtl_arguments, "&dsc_cicd_rtl_cursor"])

        header = source_dir / "dsc_cicd_overlay.h"
        header.write_text(
            "#ifndef DSC_CICD_OVERLAY_H\n"
            "#define DSC_CICD_OVERLAY_H\n"
            f"int dsc_cicd_invoke({caller_declarations});\n"
            "#endif\n",
            encoding="utf-8",
        )
        byte_loads = []
        for index in range(len(byte_ports)):
            threshold = index * 8
            byte_loads.append(
                f"    int dsc_cicd_byte_{index} = "
                f"(((dsc_cicd_cursor_before & 7) + {size_parameter}) > {threshold}) "
                f"? {buffer_parameter}[(dsc_cicd_cursor_before >> 3) + {index}] : 0;\n"
            )
        overlay = source_dir / "dsc_cicd_overlay.c"
        overlay.write_text(
            "#include <stdio.h>\n"
            "#include <stdlib.h>\n"
            "#include <string.h>\n"
            "#include \"dsc_cicd_overlay.h\"\n"
            f"extern int {original}({caller_declarations});\n"
            f"extern int dsc_cicd_rtl({input_declarations}, int *{cursor_output_port});\n"
            "static int dsc_cicd_mode(void) {\n"
            "    const char *value = getenv(\"DSC_CICD_MODE\");\n"
            "    if (value && strcmp(value, \"SHADOW\") == 0) return 1;\n"
            "    if (value && strcmp(value, \"RTL_RETURN\") == 0) return 2;\n"
            "    return 0;\n"
            "}\n"
            + self.overlay_runtime_metrics_source()
            + f"int dsc_cicd_invoke({caller_declarations}) {{\n"
            f"    int dsc_cicd_cursor_before = *{cursor_parameter};\n"
            "    int dsc_cicd_c_cursor = dsc_cicd_cursor_before;\n"
            f"    int c_value = {original}({c_call});\n"
            "    int mode = dsc_cicd_mode();\n"
            "    dsc_cicd_note_call(mode);\n"
            "    if (mode == 0) {\n"
            f"        *{cursor_parameter} = dsc_cicd_c_cursor;\n"
            "        return c_value;\n"
            "    }\n"
            + "".join(byte_loads)
            + "    int dsc_cicd_rtl_cursor = dsc_cicd_cursor_before;\n"
            f"    int rtl_value = dsc_cicd_rtl({rtl_call});\n"
            "    if (rtl_value != c_value || dsc_cicd_rtl_cursor != dsc_cicd_c_cursor) {\n"
            "        ++dsc_cicd_mismatches;\n"
            "        fprintf(stderr, \"C/RTL mismatch: c=%d rtl=%d c_cursor=%d rtl_cursor=%d\\n\",\n"
            "                c_value, rtl_value, dsc_cicd_c_cursor, dsc_cicd_rtl_cursor);\n"
            "    }\n"
            "    if (mode == 2) {\n"
            f"        *{cursor_parameter} = dsc_cicd_rtl_cursor;\n"
            "        return rtl_value;\n"
            "    }\n"
            f"    *{cursor_parameter} = dsc_cicd_c_cursor;\n"
            "    return c_value;\n"
            "}\n",
            encoding="utf-8",
        )

        return_output = next(port for port in outputs if port["name"] == return_port)
        return_width = int(return_output.get("width", 32))
        assignments = "\n".join(
            f"    dut.{port['name']} = static_cast<unsigned long long>({port['name']});"
            for port in inputs
        )
        bridge = source_dir / "rtl_bridge.cpp"
        bridge.write_text(
            "#include <cstdint>\n"
            "#include \"verilated.h\"\n"
            f"#include \"V{safe_identifier(module)}.h\"\n"
            "double sc_time_stamp() { return 0.0; }\n"
            "static long long dsc_cicd_sign_extend(long long value, int width) {\n"
            "    if (width >= 63) return value;\n"
            "    long long bit = 1LL << (width - 1);\n"
            "    long long mask = (1LL << width) - 1;\n"
            "    value &= mask;\n"
            "    return (value & bit) ? value - (1LL << width) : value;\n"
            "}\n"
            f'extern "C" int dsc_cicd_rtl({input_declarations}, int *{cursor_output_port}) {{\n'
            f"    V{safe_identifier(module)} dut;\n"
            f"{assignments}\n"
            "    dut.eval();\n"
            f"    *{cursor_output_port} = static_cast<int>(dut.{cursor_output_port});\n"
            f"    return static_cast<int>(dsc_cicd_sign_extend(static_cast<long long>(dut.{return_port}), {return_width}));\n"
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
        return {
            "header": header,
            "overlay": overlay,
            "bridge": bridge,
            "main": main,
            "candidate": candidate_sv,
            "composition": {
                "status": "PASS",
                "adapter_kind": "explicit_bitstream_read_state_transition",
                "caller_parameter_count": len(parameters),
                "rtl_input_count": len(inputs),
                "frozen_input_ports": [str(port.get("name")) for port in inputs],
                "rtl_bindings": rtl_arguments,
                "state_outputs": [cursor_output_port],
                "rtl_return_controls_cursor_in_rtl_return": True,
            },
        }

    def write_bitstream_write_transition_overlay_sources(
        self,
        contract: dict[str, Any],
        source_dir: pathlib.Path,
        module: str,
        candidate_sv: pathlib.Path,
    ) -> dict[str, Any]:
        """Bind a bounded output-byte window plus explicit write cursor."""
        semantics = contract.get("semantics", {}) or {}
        bindings = semantics.get("bindings", {}) or {}
        ports = [
            port
            for port in (contract.get("interface", {}) or {}).get("ports", [])
            if isinstance(port, dict)
        ]
        inputs = [port for port in ports if port.get("direction") == "input"]
        outputs = [port for port in ports if port.get("direction") == "output"]
        input_names = {str(port.get("name")) for port in inputs}
        output_names = {str(port.get("name")) for port in outputs}
        byte_ports = [str(value) for value in bindings.get("byte_ports", [])]
        byte_outputs = [
            str(value) for value in bindings.get("byte_output_ports", [])
        ]
        value_port = str(bindings.get("value_port", ""))
        size_port = str(bindings.get("size_port", ""))
        cursor_port = str(bindings.get("cursor_port", ""))
        cursor_output = str(bindings.get("cursor_output_port", ""))
        if (
            not byte_ports
            or len(byte_ports) != len(byte_outputs)
            or {value_port, size_port, cursor_port, *byte_ports} != input_names
            or {cursor_output, *byte_outputs} != output_names
        ):
            raise RuntimeError(
                "bitstream write ports do not match the frozen interface"
            )

        parameters = self.function_parameters(contract)
        parameter_by_name = {
            str(parameter.get("name")): parameter for parameter in parameters
        }
        value_parameter = str(bindings.get("value_parameter", ""))
        size_parameter = str(bindings.get("size_parameter", ""))
        buffer_parameter = str(bindings.get("buffer_parameter", ""))
        cursor_parameter = str(bindings.get("cursor_parameter", ""))
        if not {
            value_parameter,
            size_parameter,
            buffer_parameter,
            cursor_parameter,
        }.issubset(parameter_by_name):
            raise RuntimeError(
                "bitstream write parameter bindings are incomplete"
            )
        if not parameter_is_pointer(parameter_by_name[buffer_parameter]):
            raise RuntimeError("bitstream write buffer must be a pointer")
        if not parameter_is_pointer(parameter_by_name[cursor_parameter]):
            raise RuntimeError("bitstream write cursor must be a pointer")

        maximum = int(semantics.get("max_bits", 0) or 0)
        window_bytes = int(semantics.get("window_bytes", len(byte_ports)) or 0)
        if maximum <= 0 or window_bytes != len(byte_ports):
            raise RuntimeError("bitstream write bounds are incomplete")

        parameter_specs = [
            f"{str(parameter.get('type', 'int')).strip()} {parameter.get('name')}"
            for parameter in parameters
        ]
        parameter_names = [str(parameter.get("name")) for parameter in parameters]
        caller_declarations = ", ".join(parameter_specs)
        alias_call = ", ".join(parameter_names)
        function_name = str(contract_function(contract).get("name"))
        original = function_name + "_original"
        c_call = ", ".join(
            (
                "dsc_cicd_c_bytes"
                if name == buffer_parameter
                else "&dsc_cicd_c_local_cursor"
                if name == cursor_parameter
                else name
            )
            for name in parameter_names
        )
        input_declarations = ", ".join(
            (
                f"unsigned int {port['name']}"
                if str(port.get("name")) == value_port
                else f"int {port['name']}"
            )
            for port in inputs
        )
        rtl_expressions = {
            value_port: value_parameter,
            size_port: size_parameter,
            cursor_port: "dsc_cicd_cursor_before",
        }
        for index, port in enumerate(byte_ports):
            rtl_expressions[port] = f"dsc_cicd_pre[{index}]"
        rtl_arguments = [rtl_expressions[str(port["name"])] for port in inputs]
        rtl_byte_variables = [
            f"dsc_cicd_rtl_byte_{index}" for index in range(window_bytes)
        ]
        rtl_call = ", ".join(
            [
                *rtl_arguments,
                *[f"&{name}" for name in rtl_byte_variables],
                "&dsc_cicd_rtl_cursor",
            ]
        )
        rtl_variable_declarations = "".join(
            f"    int {name} = dsc_cicd_pre[{index}];\n"
            for index, name in enumerate(rtl_byte_variables)
        )
        rtl_raw_initializers = ", ".join(
            f"(unsigned char){name}" for name in rtl_byte_variables
        )

        header = source_dir / "dsc_cicd_overlay.h"
        header.write_text(
            "#ifndef DSC_CICD_OVERLAY_H\n"
            "#define DSC_CICD_OVERLAY_H\n"
            f"void dsc_cicd_invoke({caller_declarations});\n"
            "#endif\n",
            encoding="utf-8",
        )
        overlay = source_dir / "dsc_cicd_overlay.c"
        overlay.write_text(
            "#include <stdio.h>\n"
            "#include <stdlib.h>\n"
            "#include <string.h>\n"
            "#include \"dsc_cicd_overlay.h\"\n"
            f"extern void {original}({caller_declarations});\n"
            f"extern void dsc_cicd_rtl({input_declarations}, "
            + ", ".join(f"int *{name}" for name in byte_outputs)
            + f", int *{cursor_output});\n"
            "static int dsc_cicd_mode(void) {\n"
            "    const char *value = getenv(\"DSC_CICD_MODE\");\n"
            "    if (value && strcmp(value, \"SHADOW\") == 0) return 1;\n"
            "    if (value && strcmp(value, \"RTL_RETURN\") == 0) return 2;\n"
            "    return 0;\n"
            "}\n"
            + self.overlay_runtime_metrics_source()
            + f"void dsc_cicd_invoke({caller_declarations}) {{\n"
            "    int mode = dsc_cicd_mode();\n"
            f"    if ({size_parameter} < 0 || {size_parameter} > {maximum}) {{\n"
            "        dsc_cicd_note_call(0);\n"
            f"        {original}({alias_call});\n"
            "        return;\n"
            "    }\n"
            "    dsc_cicd_note_call(mode);\n"
            "    if (mode == 0) {\n"
            f"        {original}({alias_call});\n"
            "        return;\n"
            "    }\n"
            f"    int dsc_cicd_cursor_before = *{cursor_parameter};\n"
            "    int dsc_cicd_start_byte = dsc_cicd_cursor_before >> 3;\n"
            "    int dsc_cicd_bit_offset = dsc_cicd_cursor_before & 7;\n"
            f"    int dsc_cicd_touched = "
            f"(dsc_cicd_bit_offset + {size_parameter} + 7) >> 3;\n"
            f"    unsigned char dsc_cicd_pre[{window_bytes}] = {{0}};\n"
            f"    for (int i = 0; i < dsc_cicd_touched && i < {window_bytes}; ++i)\n"
            f"        dsc_cicd_pre[i] = {buffer_parameter}[dsc_cicd_start_byte + i];\n"
            f"    unsigned char dsc_cicd_c_bytes[{window_bytes}];\n"
            f"    memcpy(dsc_cicd_c_bytes, dsc_cicd_pre, {window_bytes});\n"
            "    int dsc_cicd_c_local_cursor = dsc_cicd_bit_offset;\n"
            f"    {original}({c_call});\n"
            "    int dsc_cicd_c_cursor = "
            "(dsc_cicd_cursor_before & ~7) + dsc_cicd_c_local_cursor;\n"
            + rtl_variable_declarations
            + "    int dsc_cicd_rtl_cursor = dsc_cicd_cursor_before;\n"
            f"    dsc_cicd_rtl({rtl_call});\n"
            f"    unsigned char dsc_cicd_rtl_bytes[{window_bytes}] = "
            f"{{{rtl_raw_initializers}}};\n"
            "    int dsc_cicd_data_mismatch = 0;\n"
            f"    for (int i = 0; i < dsc_cicd_touched && i < {window_bytes}; ++i)\n"
            "        dsc_cicd_data_mismatch |= "
            "dsc_cicd_c_bytes[i] != dsc_cicd_rtl_bytes[i];\n"
            "    if (dsc_cicd_data_mismatch || "
            "dsc_cicd_c_cursor != dsc_cicd_rtl_cursor) {\n"
            "        ++dsc_cicd_mismatches;\n"
            "        fprintf(stderr, \"C/RTL mismatch: data=%d "
            "c_cursor=%d rtl_cursor=%d size=%d cursor_before=%d\\n\",\n"
            "                dsc_cicd_data_mismatch, dsc_cicd_c_cursor, "
            f"dsc_cicd_rtl_cursor, {size_parameter}, dsc_cicd_cursor_before);\n"
            "    }\n"
            "    if (mode == 2) {\n"
            f"        for (int i = 0; i < dsc_cicd_touched && i < {window_bytes}; ++i)\n"
            f"            {buffer_parameter}[dsc_cicd_start_byte + i] = "
            "dsc_cicd_rtl_bytes[i];\n"
            f"        *{cursor_parameter} = dsc_cicd_rtl_cursor;\n"
            "    } else {\n"
            f"        for (int i = 0; i < dsc_cicd_touched && i < {window_bytes}; ++i)\n"
            f"            {buffer_parameter}[dsc_cicd_start_byte + i] = "
            "dsc_cicd_c_bytes[i];\n"
            f"        *{cursor_parameter} = dsc_cicd_c_cursor;\n"
            "    }\n"
            "}\n"
            + f"void {function_name}({caller_declarations}) {{\n"
            f"    dsc_cicd_invoke({alias_call});\n"
            "}\n",
            encoding="utf-8",
        )

        assignments = "\n".join(
            f"    dut.{port['name']} = "
            f"static_cast<unsigned long long>({port['name']});"
            for port in inputs
        )
        bridge = source_dir / "rtl_bridge.cpp"
        bridge.write_text(
            "#include <cstdint>\n"
            "#include \"verilated.h\"\n"
            f"#include \"V{safe_identifier(module)}.h\"\n"
            "double sc_time_stamp() { return 0.0; }\n"
            f'extern "C" void dsc_cicd_rtl({input_declarations}, '
            + ", ".join(f"int *{name}" for name in byte_outputs)
            + f", int *{cursor_output}) {{\n"
            f"    V{safe_identifier(module)} dut;\n"
            f"{assignments}\n"
            "    dut.eval();\n"
            + "".join(
                f"    *{output} = static_cast<int>(dut.{output});\n"
                for output in byte_outputs
            )
            + f"    *{cursor_output} = "
            f"static_cast<int>(dut.{cursor_output});\n"
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
        return {
            "header": header,
            "overlay": overlay,
            "bridge": bridge,
            "main": main,
            "candidate": candidate_sv,
            "composition": {
                "status": "PASS",
                "adapter_kind": "explicit_bitstream_write_state_transition",
                "caller_parameter_count": len(parameters),
                "rtl_input_count": len(inputs),
                "frozen_input_ports": [
                    str(port.get("name")) for port in inputs
                ],
                "rtl_bindings": rtl_arguments,
                "state_outputs": [*byte_outputs, cursor_output],
                "rtl_return_controls_output_memory_and_cursor": True,
                "c_oracle_uses_private_output_window": True,
                "residual_symbol_alias_routes_to_dispatcher": True,
            },
        }

    def write_fifo_read_transition_overlay_sources(
        self,
        contract: dict[str, Any],
        source_dir: pathlib.Path,
        module: str,
        candidate_sv: pathlib.Path,
    ) -> dict[str, Any]:
        """Bind a FIFO read as an explicit combinational next-state function."""
        semantics = contract.get("semantics", {}) or {}
        bindings = semantics.get("bindings", {}) or {}
        ports = [
            port for port in (contract.get("interface", {}) or {}).get("ports", [])
            if isinstance(port, dict)
        ]
        inputs = [port for port in ports if port.get("direction") == "input"]
        outputs = [port for port in ports if port.get("direction") == "output"]
        input_names = {str(port.get("name")) for port in inputs}
        output_names = {str(port.get("name")) for port in outputs}
        byte_ports = [str(value) for value in bindings.get("byte_ports", [])]
        nbits_port = str(bindings.get("nbits_port", ""))
        fullness_port = str(bindings.get("fullness_port", ""))
        read_ptr_port = str(bindings.get("read_ptr_port", ""))
        fifo_size_port = str(bindings.get("fifo_size_port", ""))
        sign_port = str(bindings.get("sign_extend_port", ""))
        return_port = str(bindings.get("return_port", ""))
        fullness_output = str(bindings.get("fullness_output_port", ""))
        read_ptr_output = str(bindings.get("read_ptr_output_port", ""))
        if (
            not byte_ports
            or {
                nbits_port, fullness_port, read_ptr_port,
                fifo_size_port, sign_port, *byte_ports,
            } != input_names
            or {return_port, fullness_output, read_ptr_output} != output_names
        ):
            raise RuntimeError("FIFO transition ports do not match the frozen interface")

        parameters = self.function_parameters(contract)
        parameter_by_name = {
            str(parameter.get("name")): parameter for parameter in parameters
        }
        fifo_parameter = str(bindings.get("fifo_parameter", ""))
        nbits_parameter = str(bindings.get("nbits_parameter", ""))
        sign_parameter = str(bindings.get("sign_extend_parameter", ""))
        if not {fifo_parameter, nbits_parameter, sign_parameter}.issubset(parameter_by_name):
            raise RuntimeError("FIFO transition parameter bindings are incomplete")
        if not parameter_is_pointer(parameter_by_name[fifo_parameter]):
            raise RuntimeError("FIFO transition state parameter must be a pointer")

        parameter_specs = [
            f"{str(parameter.get('type', 'int')).strip()} {parameter.get('name')}"
            for parameter in parameters
        ]
        parameter_names = [str(parameter.get("name")) for parameter in parameters]
        caller_declarations = ", ".join(parameter_specs)
        function_name = str(contract_function(contract).get("name"))
        original = function_name + "_original"
        alias_call = ", ".join(parameter_names)
        c_call = ", ".join(
            "&dsc_cicd_c_fifo" if name == fifo_parameter else name
            for name in parameter_names
        )
        input_declarations = ", ".join(
            f"int {port['name']}" for port in inputs
        )
        rtl_expressions = {
            nbits_port: nbits_parameter,
            fullness_port: "dsc_cicd_fullness_before",
            read_ptr_port: "dsc_cicd_read_ptr_before",
            fifo_size_port: "dsc_cicd_fifo_size",
            sign_port: sign_parameter,
        }
        for index, port in enumerate(byte_ports):
            rtl_expressions[port] = f"dsc_cicd_byte_{index}"
        rtl_arguments = [rtl_expressions[str(port["name"])] for port in inputs]
        rtl_call = ", ".join([
            *rtl_arguments,
            "&dsc_cicd_rtl_fullness",
            "&dsc_cicd_rtl_read_ptr",
        ])

        header = source_dir / "dsc_cicd_overlay.h"
        header.write_text(
            "#ifndef DSC_CICD_OVERLAY_H\n"
            "#define DSC_CICD_OVERLAY_H\n"
            "#include \"fifo.h\"\n"
            f"int dsc_cicd_invoke({caller_declarations});\n"
            "#endif\n",
            encoding="utf-8",
        )
        byte_loads = []
        for index in range(len(byte_ports)):
            threshold = index * 8
            byte_loads.append(
                f"    int dsc_cicd_byte_{index} = "
                f"(((dsc_cicd_read_ptr_before & 7) + {nbits_parameter}) > {threshold}) "
                f"? {fifo_parameter}->data[(dsc_cicd_start_byte + {index}) "
                f"% dsc_cicd_fifo_bytes] : 0;\n"
            )
        overlay = source_dir / "dsc_cicd_overlay.c"
        overlay.write_text(
            "#include <stdio.h>\n"
            "#include <stdlib.h>\n"
            "#include <string.h>\n"
            "#include \"dsc_cicd_overlay.h\"\n"
            f"extern int {original}({caller_declarations});\n"
            f"extern int dsc_cicd_rtl({input_declarations}, int *{fullness_output}, int *{read_ptr_output});\n"
            "static int dsc_cicd_mode(void) {\n"
            "    const char *value = getenv(\"DSC_CICD_MODE\");\n"
            "    if (value && strcmp(value, \"SHADOW\") == 0) return 1;\n"
            "    if (value && strcmp(value, \"RTL_RETURN\") == 0) return 2;\n"
            "    return 0;\n"
            "}\n"
            + self.overlay_runtime_metrics_source()
            + f"int dsc_cicd_invoke({caller_declarations}) {{\n"
            f"    int dsc_cicd_fullness_before = {fifo_parameter}->fullness;\n"
            f"    int dsc_cicd_read_ptr_before = {fifo_parameter}->read_ptr;\n"
            f"    int dsc_cicd_fifo_size = {fifo_parameter}->size;\n"
            f"    fifo_t dsc_cicd_c_fifo = *{fifo_parameter};\n"
            f"    int c_value = {original}({c_call});\n"
            "    int mode = dsc_cicd_mode();\n"
            "    dsc_cicd_note_call(mode);\n"
            "    if (mode == 0) {\n"
            f"        {fifo_parameter}->fullness = dsc_cicd_c_fifo.fullness;\n"
            f"        {fifo_parameter}->read_ptr = dsc_cicd_c_fifo.read_ptr;\n"
            "        return c_value;\n"
            "    }\n"
            "    int dsc_cicd_fifo_bytes = dsc_cicd_fifo_size >> 3;\n"
            "    int dsc_cicd_start_byte = dsc_cicd_read_ptr_before >> 3;\n"
            + "".join(byte_loads)
            + "    int dsc_cicd_rtl_fullness = dsc_cicd_fullness_before;\n"
            "    int dsc_cicd_rtl_read_ptr = dsc_cicd_read_ptr_before;\n"
            f"    int rtl_value = dsc_cicd_rtl({rtl_call});\n"
            "    if (rtl_value != c_value || "
            "dsc_cicd_rtl_fullness != dsc_cicd_c_fifo.fullness || "
            "dsc_cicd_rtl_read_ptr != dsc_cicd_c_fifo.read_ptr) {\n"
            "        ++dsc_cicd_mismatches;\n"
            "        fprintf(stderr, \"C/RTL mismatch: c=%d rtl=%d c_fullness=%d "
            "rtl_fullness=%d c_read_ptr=%d rtl_read_ptr=%d nbits=%d sign=%d "
            "read_before=%d fifo_size=%d\\n\",\n"
            "                c_value, rtl_value, dsc_cicd_c_fifo.fullness, "
            "dsc_cicd_rtl_fullness, dsc_cicd_c_fifo.read_ptr, dsc_cicd_rtl_read_ptr, "
            f"{nbits_parameter}, {sign_parameter}, dsc_cicd_read_ptr_before, dsc_cicd_fifo_size);\n"
            "    }\n"
            "    if (mode == 2) {\n"
            f"        {fifo_parameter}->fullness = dsc_cicd_rtl_fullness;\n"
            f"        {fifo_parameter}->read_ptr = dsc_cicd_rtl_read_ptr;\n"
            "        return rtl_value;\n"
            "    }\n"
            f"    {fifo_parameter}->fullness = dsc_cicd_c_fifo.fullness;\n"
            f"    {fifo_parameter}->read_ptr = dsc_cicd_c_fifo.read_ptr;\n"
            "    return c_value;\n"
            "}\n"
            + f"int {function_name}({caller_declarations}) {{\n"
            f"    return dsc_cicd_invoke({alias_call});\n"
            "}\n",
            encoding="utf-8",
        )

        return_output = next(port for port in outputs if port["name"] == return_port)
        return_width = int(return_output.get("width", 32))
        assignments = "\n".join(
            f"    dut.{port['name']} = static_cast<unsigned long long>({port['name']});"
            for port in inputs
        )
        bridge = source_dir / "rtl_bridge.cpp"
        bridge.write_text(
            "#include <cstdint>\n"
            "#include \"verilated.h\"\n"
            f"#include \"V{safe_identifier(module)}.h\"\n"
            "double sc_time_stamp() { return 0.0; }\n"
            "static long long dsc_cicd_fifo_sign_extend(long long value, int width) {\n"
            "    if (width >= 63) return value;\n"
            "    long long bit = 1LL << (width - 1);\n"
            "    long long mask = (1LL << width) - 1;\n"
            "    value &= mask;\n"
            "    return (value & bit) ? value - (1LL << width) : value;\n"
            "}\n"
            f'extern "C" int dsc_cicd_rtl({input_declarations}, int *{fullness_output}, int *{read_ptr_output}) {{\n'
            f"    V{safe_identifier(module)} dut;\n"
            f"{assignments}\n"
            "    dut.eval();\n"
            f"    *{fullness_output} = static_cast<int>(dut.{fullness_output});\n"
            f"    *{read_ptr_output} = static_cast<int>(dut.{read_ptr_output});\n"
            f"    return static_cast<int>(dsc_cicd_fifo_sign_extend(static_cast<long long>(dut.{return_port}), {return_width}));\n"
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
        return {
            "header": header,
            "overlay": overlay,
            "bridge": bridge,
            "main": main,
            "candidate": candidate_sv,
            "composition": {
                "status": "PASS",
                "adapter_kind": "explicit_fifo_read_state_transition",
                "caller_parameter_count": len(parameters),
                "rtl_input_count": len(inputs),
                "frozen_input_ports": [str(port.get("name")) for port in inputs],
                "rtl_bindings": rtl_arguments,
                "state_outputs": [fullness_output, read_ptr_output],
                "rtl_return_controls_fifo_state_in_rtl_return": True,
                "residual_symbol_alias_routes_to_dispatcher": True,
            },
        }

    def write_fifo_read_accounting_transition_overlay_sources(
        self,
        contract: dict[str, Any],
        source_dir: pathlib.Path,
        module: str,
        candidate_sv: pathlib.Path,
    ) -> dict[str, Any]:
        """Bind a composed bit-accounting/FIFO read as explicit next state."""
        semantics = contract.get("semantics", {}) or {}
        bindings = semantics.get("bindings", {}) or {}
        ports = [
            port for port in (contract.get("interface", {}) or {}).get("ports", [])
            if isinstance(port, dict)
        ]
        inputs = [port for port in ports if port.get("direction") == "input"]
        outputs = [port for port in ports if port.get("direction") == "output"]
        input_names = {str(port.get("name")) for port in inputs}
        output_names = {str(port.get("name")) for port in outputs}
        byte_ports = [str(value) for value in bindings.get("byte_ports", [])]
        nbits_port = str(bindings.get("nbits_port", ""))
        bit_count_port = str(bindings.get("bit_count_port", ""))
        fullness_port = str(bindings.get("fullness_port", ""))
        read_ptr_port = str(bindings.get("read_ptr_port", ""))
        fifo_size_port = str(bindings.get("fifo_size_port", ""))
        sign_port = str(bindings.get("sign_extend_port", ""))
        return_port = str(bindings.get("return_port", ""))
        bit_count_output = str(bindings.get("bit_count_output_port", ""))
        fullness_output = str(bindings.get("fullness_output_port", ""))
        read_ptr_output = str(bindings.get("read_ptr_output_port", ""))
        if (
            not byte_ports
            or {
                nbits_port, bit_count_port, fullness_port, read_ptr_port,
                fifo_size_port, sign_port, *byte_ports,
            } != input_names
            or {
                return_port, bit_count_output, fullness_output, read_ptr_output,
            } != output_names
        ):
            raise RuntimeError(
                "FIFO accounting transition ports do not match the frozen interface"
            )

        parameters = self.function_parameters(contract)
        parameter_by_name = {
            str(parameter.get("name")): parameter for parameter in parameters
        }
        state_parameter = str(bindings.get("state_parameter", ""))
        unit_parameter = str(bindings.get("unit_parameter", ""))
        nbits_parameter = str(bindings.get("nbits_parameter", ""))
        sign_parameter = str(bindings.get("sign_extend_parameter", ""))
        required_parameters = {
            state_parameter, unit_parameter, nbits_parameter, sign_parameter,
        }
        if not required_parameters.issubset(parameter_by_name):
            raise RuntimeError("FIFO accounting parameter bindings are incomplete")
        if not parameter_is_pointer(parameter_by_name[state_parameter]):
            raise RuntimeError("FIFO accounting state parameter must be a pointer")

        state_counter_field = str(bindings.get("state_counter_field", ""))
        fifo_array_field = str(bindings.get("fifo_array_field", ""))
        identifier = re.compile(r"^[A-Za-z_][A-Za-z0-9_]*$")
        if not identifier.fullmatch(state_counter_field) or not identifier.fullmatch(
            fifo_array_field
        ):
            raise RuntimeError("FIFO accounting state-field bindings are invalid")

        parameter_specs = [
            f"{str(parameter.get('type', 'int')).strip()} {parameter.get('name')}"
            for parameter in parameters
        ]
        parameter_names = [str(parameter.get("name")) for parameter in parameters]
        caller_declarations = ", ".join(parameter_specs)
        function_name = str(contract_function(contract).get("name"))
        original = function_name + "_original"
        alias_call = ", ".join(parameter_names)
        c_call = ", ".join(
            "&dsc_cicd_c_state" if name == state_parameter else name
            for name in parameter_names
        )
        input_declarations = ", ".join(
            f"int {port['name']}" for port in inputs
        )
        rtl_expressions = {
            nbits_port: nbits_parameter,
            bit_count_port: "dsc_cicd_bit_count_before",
            fullness_port: "dsc_cicd_fullness_before",
            read_ptr_port: "dsc_cicd_read_ptr_before",
            fifo_size_port: "dsc_cicd_fifo_size",
            sign_port: sign_parameter,
        }
        for index, port in enumerate(byte_ports):
            rtl_expressions[port] = f"dsc_cicd_byte_{index}"
        rtl_arguments = [rtl_expressions[str(port["name"])] for port in inputs]
        rtl_call = ", ".join([
            *rtl_arguments,
            "&dsc_cicd_rtl_bit_count",
            "&dsc_cicd_rtl_fullness",
            "&dsc_cicd_rtl_read_ptr",
        ])

        header = source_dir / "dsc_cicd_overlay.h"
        header.write_text(
            "#ifndef DSC_CICD_OVERLAY_H\n"
            "#define DSC_CICD_OVERLAY_H\n"
            "#include \"dsc_types.h\"\n"
            f"int dsc_cicd_invoke({caller_declarations});\n"
            "#endif\n",
            encoding="utf-8",
        )
        byte_loads = []
        for index in range(len(byte_ports)):
            threshold = index * 8
            byte_loads.append(
                f"    int dsc_cicd_byte_{index} = "
                f"(((dsc_cicd_read_ptr_before & 7) + {nbits_parameter}) > {threshold}) "
                f"? dsc_cicd_fifo->data[(dsc_cicd_start_byte + {index}) "
                f"% dsc_cicd_fifo_bytes] : 0;\n"
            )
        overlay = source_dir / "dsc_cicd_overlay.c"
        overlay.write_text(
            "#include <stdio.h>\n"
            "#include <stdlib.h>\n"
            "#include <string.h>\n"
            "#include \"dsc_cicd_overlay.h\"\n"
            f"extern int {original}({caller_declarations});\n"
            f"extern int dsc_cicd_rtl({input_declarations}, int *{bit_count_output}, "
            f"int *{fullness_output}, int *{read_ptr_output});\n"
            "static int dsc_cicd_mode(void) {\n"
            "    const char *value = getenv(\"DSC_CICD_MODE\");\n"
            "    if (value && strcmp(value, \"SHADOW\") == 0) return 1;\n"
            "    if (value && strcmp(value, \"RTL_RETURN\") == 0) return 2;\n"
            "    return 0;\n"
            "}\n"
            + self.overlay_runtime_metrics_source()
            + f"int dsc_cicd_invoke({caller_declarations}) {{\n"
            f"    int dsc_cicd_bit_count_before = {state_parameter}->{state_counter_field};\n"
            f"    fifo_t *dsc_cicd_fifo = &({state_parameter}->{fifo_array_field}[{unit_parameter}]);\n"
            "    int dsc_cicd_fullness_before = dsc_cicd_fifo->fullness;\n"
            "    int dsc_cicd_read_ptr_before = dsc_cicd_fifo->read_ptr;\n"
            "    int dsc_cicd_fifo_size = dsc_cicd_fifo->size;\n"
            f"    dsc_state_t dsc_cicd_c_state = *{state_parameter};\n"
            f"    int c_value = {original}({c_call});\n"
            f"    fifo_t *dsc_cicd_c_fifo = &(dsc_cicd_c_state.{fifo_array_field}[{unit_parameter}]);\n"
            "    int mode = dsc_cicd_mode();\n"
            "    dsc_cicd_note_call(mode);\n"
            "    if (mode == 0) {\n"
            f"        {state_parameter}->{state_counter_field} = "
            f"dsc_cicd_c_state.{state_counter_field};\n"
            "        dsc_cicd_fifo->fullness = dsc_cicd_c_fifo->fullness;\n"
            "        dsc_cicd_fifo->read_ptr = dsc_cicd_c_fifo->read_ptr;\n"
            "        return c_value;\n"
            "    }\n"
            "    int dsc_cicd_fifo_bytes = dsc_cicd_fifo_size >> 3;\n"
            "    int dsc_cicd_start_byte = dsc_cicd_read_ptr_before >> 3;\n"
            + "".join(byte_loads)
            + "    int dsc_cicd_rtl_bit_count = dsc_cicd_bit_count_before;\n"
            "    int dsc_cicd_rtl_fullness = dsc_cicd_fullness_before;\n"
            "    int dsc_cicd_rtl_read_ptr = dsc_cicd_read_ptr_before;\n"
            f"    int rtl_value = dsc_cicd_rtl({rtl_call});\n"
            "    if (rtl_value != c_value || "
            f"dsc_cicd_rtl_bit_count != dsc_cicd_c_state.{state_counter_field} || "
            "dsc_cicd_rtl_fullness != dsc_cicd_c_fifo->fullness || "
            "dsc_cicd_rtl_read_ptr != dsc_cicd_c_fifo->read_ptr) {\n"
            "        ++dsc_cicd_mismatches;\n"
            "        fprintf(stderr, \"C/RTL mismatch: c=%d rtl=%d c_bits=%d "
            "rtl_bits=%d c_fullness=%d rtl_fullness=%d c_read_ptr=%d "
            "rtl_read_ptr=%d nbits=%d sign=%d unit=%d read_before=%d "
            "fifo_size=%d\\n\",\n"
            f"                c_value, rtl_value, dsc_cicd_c_state.{state_counter_field}, "
            "dsc_cicd_rtl_bit_count, dsc_cicd_c_fifo->fullness, "
            "dsc_cicd_rtl_fullness, dsc_cicd_c_fifo->read_ptr, "
            f"dsc_cicd_rtl_read_ptr, {nbits_parameter}, {sign_parameter}, "
            f"{unit_parameter}, dsc_cicd_read_ptr_before, dsc_cicd_fifo_size);\n"
            "    }\n"
            "    if (mode == 2) {\n"
            f"        {state_parameter}->{state_counter_field} = dsc_cicd_rtl_bit_count;\n"
            "        dsc_cicd_fifo->fullness = dsc_cicd_rtl_fullness;\n"
            "        dsc_cicd_fifo->read_ptr = dsc_cicd_rtl_read_ptr;\n"
            "        return rtl_value;\n"
            "    }\n"
            f"    {state_parameter}->{state_counter_field} = "
            f"dsc_cicd_c_state.{state_counter_field};\n"
            "    dsc_cicd_fifo->fullness = dsc_cicd_c_fifo->fullness;\n"
            "    dsc_cicd_fifo->read_ptr = dsc_cicd_c_fifo->read_ptr;\n"
            "    return c_value;\n"
            "}\n"
            + f"int {function_name}({caller_declarations}) {{\n"
            f"    return dsc_cicd_invoke({alias_call});\n"
            "}\n",
            encoding="utf-8",
        )

        return_output = next(port for port in outputs if port["name"] == return_port)
        return_width = int(return_output.get("width", 32))
        assignments = "\n".join(
            f"    dut.{port['name']} = static_cast<unsigned long long>({port['name']});"
            for port in inputs
        )
        bridge = source_dir / "rtl_bridge.cpp"
        bridge.write_text(
            "#include <cstdint>\n"
            "#include \"verilated.h\"\n"
            f"#include \"V{safe_identifier(module)}.h\"\n"
            "double sc_time_stamp() { return 0.0; }\n"
            "static long long dsc_cicd_fifo_accounting_sign_extend(long long value, int width) {\n"
            "    if (width >= 63) return value;\n"
            "    long long bit = 1LL << (width - 1);\n"
            "    long long mask = (1LL << width) - 1;\n"
            "    value &= mask;\n"
            "    return (value & bit) ? value - (1LL << width) : value;\n"
            "}\n"
            f'extern "C" int dsc_cicd_rtl({input_declarations}, int *{bit_count_output}, '
            f'int *{fullness_output}, int *{read_ptr_output}) {{\n'
            f"    V{safe_identifier(module)} dut;\n"
            f"{assignments}\n"
            "    dut.eval();\n"
            f"    *{bit_count_output} = static_cast<int>(dut.{bit_count_output});\n"
            f"    *{fullness_output} = static_cast<int>(dut.{fullness_output});\n"
            f"    *{read_ptr_output} = static_cast<int>(dut.{read_ptr_output});\n"
            "    return static_cast<int>(dsc_cicd_fifo_accounting_sign_extend("
            f"static_cast<long long>(dut.{return_port}), {return_width}));\n"
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
        return {
            "header": header,
            "overlay": overlay,
            "bridge": bridge,
            "main": main,
            "candidate": candidate_sv,
            "composition": {
                "status": "PASS",
                "adapter_kind": "explicit_fifo_read_accounting_state_transition",
                "caller_parameter_count": len(parameters),
                "rtl_input_count": len(inputs),
                "frozen_input_ports": [str(port.get("name")) for port in inputs],
                "rtl_bindings": rtl_arguments,
                "state_outputs": [
                    bit_count_output, fullness_output, read_ptr_output,
                ],
                "rtl_return_controls_composed_state_in_rtl_return": True,
                "residual_symbol_alias_routes_to_dispatcher": True,
            },
        }

    def write_fifo_write_transition_overlay_sources(
        self,
        contract: dict[str, Any],
        source_dir: pathlib.Path,
        module: str,
        candidate_sv: pathlib.Path,
    ) -> dict[str, Any]:
        """Bind a bounded FIFO memory-window write as explicit next state."""
        semantics = contract.get("semantics", {}) or {}
        bindings = semantics.get("bindings", {}) or {}
        ports = [
            port for port in (contract.get("interface", {}) or {}).get("ports", [])
            if isinstance(port, dict)
        ]
        inputs = [port for port in ports if port.get("direction") == "input"]
        outputs = [port for port in ports if port.get("direction") == "output"]
        input_names = {str(port.get("name")) for port in inputs}
        output_names = {str(port.get("name")) for port in outputs}
        byte_ports = [str(value) for value in bindings.get("byte_ports", [])]
        byte_outputs = [
            str(value) for value in bindings.get("byte_output_ports", [])
        ]
        data_port = str(bindings.get("data_port", ""))
        nbits_port = str(bindings.get("nbits_port", ""))
        fullness_port = str(bindings.get("fullness_port", ""))
        write_ptr_port = str(bindings.get("write_ptr_port", ""))
        fifo_size_port = str(bindings.get("fifo_size_port", ""))
        max_fullness_port = str(bindings.get("max_fullness_port", ""))
        fullness_output = str(bindings.get("fullness_output_port", ""))
        write_ptr_output = str(bindings.get("write_ptr_output_port", ""))
        max_fullness_output = str(bindings.get("max_fullness_output_port", ""))
        if (
            not byte_ports
            or len(byte_ports) != len(byte_outputs)
            or {
                data_port, nbits_port, fullness_port, write_ptr_port,
                fifo_size_port, max_fullness_port, *byte_ports,
            } != input_names
            or {
                fullness_output, write_ptr_output, max_fullness_output,
                *byte_outputs,
            } != output_names
        ):
            raise RuntimeError("FIFO write ports do not match the frozen interface")

        parameters = self.function_parameters(contract)
        parameter_by_name = {
            str(parameter.get("name")): parameter for parameter in parameters
        }
        fifo_parameter = str(bindings.get("fifo_parameter", ""))
        data_parameter = str(bindings.get("data_parameter", ""))
        nbits_parameter = str(bindings.get("nbits_parameter", ""))
        if not {fifo_parameter, data_parameter, nbits_parameter}.issubset(
            parameter_by_name
        ):
            raise RuntimeError("FIFO write parameter bindings are incomplete")
        if not parameter_is_pointer(parameter_by_name[fifo_parameter]):
            raise RuntimeError("FIFO write state parameter must be a pointer")

        field_keys = [
            "data_field", "fullness_field", "write_ptr_field", "size_field",
            "max_fullness_field",
        ]
        fields = {key: str(bindings.get(key, "")) for key in field_keys}
        identifier = re.compile(r"^[A-Za-z_][A-Za-z0-9_]*$")
        if not all(identifier.fullmatch(value) for value in fields.values()):
            raise RuntimeError("FIFO write state-field bindings are invalid")
        data_field = fields["data_field"]
        fullness_field = fields["fullness_field"]
        write_ptr_field = fields["write_ptr_field"]
        size_field = fields["size_field"]
        max_fullness_field = fields["max_fullness_field"]

        parameter_specs = [
            f"{str(parameter.get('type', 'int')).strip()} {parameter.get('name')}"
            for parameter in parameters
        ]
        parameter_names = [str(parameter.get("name")) for parameter in parameters]
        caller_declarations = ", ".join(parameter_specs)
        function_name = str(contract_function(contract).get("name"))
        original = function_name + "_original"
        alias_call = ", ".join(parameter_names)
        c_call = alias_call
        input_declarations = ", ".join(
            (
                f"unsigned int {port['name']}"
                if str(port.get("name")) == data_port
                else f"int {port['name']}"
            )
            for port in inputs
        )
        rtl_expressions = {
            data_port: data_parameter,
            nbits_port: nbits_parameter,
            fullness_port: "dsc_cicd_fullness_before",
            write_ptr_port: "dsc_cicd_write_ptr_before",
            fifo_size_port: "dsc_cicd_fifo_size",
            max_fullness_port: "dsc_cicd_max_fullness_before",
        }
        for index, port in enumerate(byte_ports):
            rtl_expressions[port] = f"dsc_cicd_pre[{index}]"
        rtl_arguments = [rtl_expressions[str(port["name"])] for port in inputs]
        rtl_byte_variables = [
            f"dsc_cicd_rtl_byte_{index}" for index in range(len(byte_outputs))
        ]
        rtl_call = ", ".join([
            *rtl_arguments,
            *[f"&{value}" for value in rtl_byte_variables],
            "&dsc_cicd_rtl_fullness",
            "&dsc_cicd_rtl_write_ptr",
            "&dsc_cicd_rtl_max_fullness",
        ])
        index_initializers = ", ".join(
            f"(dsc_cicd_start_byte + {index}) % dsc_cicd_fifo_bytes"
            for index in range(len(byte_ports))
        )
        pre_initializers = ", ".join(
            f"{fifo_parameter}->{data_field}[dsc_cicd_index[{index}]]"
            for index in range(len(byte_ports))
        )
        c_initializers = ", ".join(
            f"{fifo_parameter}->{data_field}[dsc_cicd_index[{index}]]"
            for index in range(len(byte_ports))
        )
        rtl_variable_declarations = "".join(
            f"    int {value} = dsc_cicd_pre[{index}];\n"
            for index, value in enumerate(rtl_byte_variables)
        )
        rtl_raw_initializers = ", ".join(
            f"(unsigned char){value}" for value in rtl_byte_variables
        )

        header = source_dir / "dsc_cicd_overlay.h"
        header.write_text(
            "#ifndef DSC_CICD_OVERLAY_H\n"
            "#define DSC_CICD_OVERLAY_H\n"
            "#include \"fifo.h\"\n"
            f"void dsc_cicd_invoke({caller_declarations});\n"
            "#endif\n",
            encoding="utf-8",
        )
        overlay = source_dir / "dsc_cicd_overlay.c"
        overlay.write_text(
            "#include <stdio.h>\n"
            "#include <stdlib.h>\n"
            "#include <string.h>\n"
            "#include \"dsc_cicd_overlay.h\"\n"
            f"extern void {original}({caller_declarations});\n"
            f"extern void dsc_cicd_rtl({input_declarations}, "
            + ", ".join(f"int *{value}" for value in byte_outputs)
            + f", int *{fullness_output}, int *{write_ptr_output}, "
            f"int *{max_fullness_output});\n"
            "static int dsc_cicd_mode(void) {\n"
            "    const char *value = getenv(\"DSC_CICD_MODE\");\n"
            "    if (value && strcmp(value, \"SHADOW\") == 0) return 1;\n"
            "    if (value && strcmp(value, \"RTL_RETURN\") == 0) return 2;\n"
            "    return 0;\n"
            "}\n"
            + self.overlay_runtime_metrics_source()
            + f"void dsc_cicd_invoke({caller_declarations}) {{\n"
            f"    int dsc_cicd_fullness_before = {fifo_parameter}->{fullness_field};\n"
            f"    int dsc_cicd_write_ptr_before = {fifo_parameter}->{write_ptr_field};\n"
            f"    int dsc_cicd_fifo_size = {fifo_parameter}->{size_field};\n"
            f"    int dsc_cicd_max_fullness_before = {fifo_parameter}->{max_fullness_field};\n"
            "    int dsc_cicd_fifo_bytes = dsc_cicd_fifo_size >> 3;\n"
            "    int dsc_cicd_start_byte = dsc_cicd_write_ptr_before >> 3;\n"
            f"    int dsc_cicd_index[{len(byte_ports)}] = {{{index_initializers}}};\n"
            f"    unsigned char dsc_cicd_pre[{len(byte_ports)}] = {{{pre_initializers}}};\n"
            f"    {original}({c_call});\n"
            f"    unsigned char dsc_cicd_c_after[{len(byte_ports)}] = "
            f"{{{c_initializers}}};\n"
            f"    int dsc_cicd_c_fullness = {fifo_parameter}->{fullness_field};\n"
            f"    int dsc_cicd_c_write_ptr = {fifo_parameter}->{write_ptr_field};\n"
            f"    int dsc_cicd_c_max_fullness = {fifo_parameter}->{max_fullness_field};\n"
            "    int mode = dsc_cicd_mode();\n"
            "    dsc_cicd_note_call(mode);\n"
            "    if (mode == 0) return;\n"
            + rtl_variable_declarations
            + "    int dsc_cicd_rtl_fullness = dsc_cicd_fullness_before;\n"
            "    int dsc_cicd_rtl_write_ptr = dsc_cicd_write_ptr_before;\n"
            "    int dsc_cicd_rtl_max_fullness = dsc_cicd_max_fullness_before;\n"
            f"    dsc_cicd_rtl({rtl_call});\n"
            f"    unsigned char dsc_cicd_rtl_raw[{len(byte_ports)}] = "
            f"{{{rtl_raw_initializers}}};\n"
            f"    unsigned char dsc_cicd_mask[{len(byte_ports)}] = {{0}};\n"
            f"    unsigned char dsc_cicd_merged[{len(byte_ports)}];\n"
            f"    for (int i = 0; i < {nbits_parameter}; ++i) {{\n"
            "        int logical_bit = (dsc_cicd_write_ptr_before & 7) + i;\n"
            "        int slot = logical_bit >> 3;\n"
            "        dsc_cicd_mask[slot] |= (unsigned char)(1 << (7 - (logical_bit & 7)));\n"
            "    }\n"
            f"    for (int i = 0; i < {len(byte_ports)}; ++i) "
            "dsc_cicd_merged[i] = dsc_cicd_pre[i];\n"
            f"    for (int slot = 0; slot < {len(byte_ports)}; ++slot) {{\n"
            f"        for (int alias = 0; alias < {len(byte_ports)}; ++alias) {{\n"
            "            if (dsc_cicd_index[alias] == dsc_cicd_index[slot])\n"
            "                dsc_cicd_merged[alias] = "
            "(unsigned char)((dsc_cicd_merged[alias] & ~dsc_cicd_mask[slot]) | "
            "(dsc_cicd_rtl_raw[slot] & dsc_cicd_mask[slot]));\n"
            "        }\n"
            "    }\n"
            "    int dsc_cicd_data_mismatch = 0;\n"
            f"    for (int i = 0; i < {len(byte_ports)}; ++i) "
            "dsc_cicd_data_mismatch |= dsc_cicd_merged[i] != dsc_cicd_c_after[i];\n"
            "    if (dsc_cicd_data_mismatch || "
            "dsc_cicd_rtl_fullness != dsc_cicd_c_fullness || "
            "dsc_cicd_rtl_write_ptr != dsc_cicd_c_write_ptr || "
            "dsc_cicd_rtl_max_fullness != dsc_cicd_c_max_fullness) {\n"
            "        ++dsc_cicd_mismatches;\n"
            "        fprintf(stderr, \"C/RTL mismatch: data=%d c_fullness=%d "
            "rtl_fullness=%d c_write_ptr=%d rtl_write_ptr=%d c_max=%d "
            "rtl_max=%d nbits=%d write_before=%d fifo_size=%d\\n\",\n"
            "                dsc_cicd_data_mismatch, dsc_cicd_c_fullness, "
            "dsc_cicd_rtl_fullness, dsc_cicd_c_write_ptr, dsc_cicd_rtl_write_ptr, "
            "dsc_cicd_c_max_fullness, dsc_cicd_rtl_max_fullness, "
            f"{nbits_parameter}, dsc_cicd_write_ptr_before, dsc_cicd_fifo_size);\n"
            "    }\n"
            "    if (mode == 2) {\n"
            f"        for (int i = 0; i < {len(byte_ports)}; ++i) "
            f"{fifo_parameter}->{data_field}[dsc_cicd_index[i]] = dsc_cicd_merged[i];\n"
            f"        {fifo_parameter}->{fullness_field} = dsc_cicd_rtl_fullness;\n"
            f"        {fifo_parameter}->{write_ptr_field} = dsc_cicd_rtl_write_ptr;\n"
            f"        {fifo_parameter}->{max_fullness_field} = dsc_cicd_rtl_max_fullness;\n"
            "    }\n"
            "}\n"
            + f"void {function_name}({caller_declarations}) {{\n"
            f"    dsc_cicd_invoke({alias_call});\n"
            "}\n",
            encoding="utf-8",
        )

        assignments = "\n".join(
            f"    dut.{port['name']} = static_cast<unsigned long long>({port['name']});"
            for port in inputs
        )
        bridge = source_dir / "rtl_bridge.cpp"
        bridge.write_text(
            "#include <cstdint>\n"
            "#include \"verilated.h\"\n"
            f"#include \"V{safe_identifier(module)}.h\"\n"
            "double sc_time_stamp() { return 0.0; }\n"
            f'extern "C" void dsc_cicd_rtl({input_declarations}, '
            + ", ".join(f"int *{value}" for value in byte_outputs)
            + f", int *{fullness_output}, int *{write_ptr_output}, "
            f"int *{max_fullness_output}) {{\n"
            f"    V{safe_identifier(module)} dut;\n"
            f"{assignments}\n"
            "    dut.eval();\n"
            + "".join(
                f"    *{output} = static_cast<int>(dut.{output});\n"
                for output in byte_outputs
            )
            + f"    *{fullness_output} = static_cast<int>(dut.{fullness_output});\n"
            f"    *{write_ptr_output} = static_cast<int>(dut.{write_ptr_output});\n"
            f"    *{max_fullness_output} = static_cast<int>(dut.{max_fullness_output});\n"
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
        return {
            "header": header,
            "overlay": overlay,
            "bridge": bridge,
            "main": main,
            "candidate": candidate_sv,
            "composition": {
                "status": "PASS",
                "adapter_kind": "explicit_fifo_write_state_transition",
                "caller_parameter_count": len(parameters),
                "rtl_input_count": len(inputs),
                "frozen_input_ports": [str(port.get("name")) for port in inputs],
                "rtl_bindings": rtl_arguments,
                "state_outputs": [
                    *byte_outputs, fullness_output, write_ptr_output,
                    max_fullness_output,
                ],
                "rtl_return_controls_fifo_memory_and_state_in_rtl_return": True,
                "residual_symbol_alias_routes_to_dispatcher": True,
            },
        }

    def write_fifo_write_accounting_transition_overlay_sources(
        self,
        contract: dict[str, Any],
        source_dir: pathlib.Path,
        module: str,
        candidate_sv: pathlib.Path,
    ) -> dict[str, Any]:
        """Bind one indexed FIFO write plus its caller-visible bit counter."""
        semantics = contract.get("semantics", {}) or {}
        bindings = semantics.get("bindings", {}) or {}
        ports = [
            port
            for port in (contract.get("interface", {}) or {}).get("ports", [])
            if isinstance(port, dict)
        ]
        inputs = [port for port in ports if port.get("direction") == "input"]
        outputs = [port for port in ports if port.get("direction") == "output"]
        input_names = {str(port.get("name")) for port in inputs}
        output_names = {str(port.get("name")) for port in outputs}
        byte_ports = [str(value) for value in bindings.get("byte_ports", [])]
        byte_outputs = [
            str(value) for value in bindings.get("byte_output_ports", [])
        ]
        data_port = str(bindings.get("data_port", ""))
        nbits_port = str(bindings.get("nbits_port", ""))
        num_bits_port = str(bindings.get("num_bits_port", ""))
        fullness_port = str(bindings.get("fullness_port", ""))
        write_ptr_port = str(bindings.get("write_ptr_port", ""))
        fifo_size_port = str(bindings.get("fifo_size_port", ""))
        max_fullness_port = str(bindings.get("max_fullness_port", ""))
        num_bits_output = str(
            bindings.get("num_bits_output_port", "")
        )
        fullness_output = str(
            bindings.get("fullness_output_port", "")
        )
        write_ptr_output = str(
            bindings.get("write_ptr_output_port", "")
        )
        max_fullness_output = str(
            bindings.get("max_fullness_output_port", "")
        )
        if (
            not byte_ports
            or len(byte_ports) != len(byte_outputs)
            or {
                data_port,
                nbits_port,
                num_bits_port,
                fullness_port,
                write_ptr_port,
                fifo_size_port,
                max_fullness_port,
                *byte_ports,
            }
            != input_names
            or {
                num_bits_output,
                fullness_output,
                write_ptr_output,
                max_fullness_output,
                *byte_outputs,
            }
            != output_names
        ):
            raise RuntimeError(
                "FIFO write accounting ports do not match the frozen interface"
            )

        parameters = self.function_parameters(contract)
        parameter_by_name = {
            str(parameter.get("name")): parameter for parameter in parameters
        }
        state_parameter = str(bindings.get("state_parameter", ""))
        fifo_index_parameter = str(
            bindings.get("fifo_index_parameter", "")
        )
        data_parameter = str(bindings.get("data_parameter", ""))
        nbits_parameter = str(bindings.get("nbits_parameter", ""))
        required_parameters = {
            state_parameter,
            fifo_index_parameter,
            data_parameter,
            nbits_parameter,
        }
        if not required_parameters.issubset(parameter_by_name):
            raise RuntimeError(
                "FIFO write accounting parameter bindings are incomplete"
            )
        if not parameter_is_pointer(parameter_by_name[state_parameter]):
            raise RuntimeError(
                "FIFO write accounting state parameter must be a pointer"
            )

        field_names = {
            key: str(bindings.get(key, ""))
            for key in (
                "state_counter_field",
                "fifo_array_field",
                "data_field",
                "fullness_field",
                "write_ptr_field",
                "size_field",
                "max_fullness_field",
            )
        }
        identifier = re.compile(r"^[A-Za-z_][A-Za-z0-9_]*$")
        if not all(
            identifier.fullmatch(value) for value in field_names.values()
        ):
            raise RuntimeError(
                "FIFO write accounting state-field bindings are invalid"
            )
        counter_field = field_names["state_counter_field"]
        fifo_array_field = field_names["fifo_array_field"]
        data_field = field_names["data_field"]
        fullness_field = field_names["fullness_field"]
        write_ptr_field = field_names["write_ptr_field"]
        size_field = field_names["size_field"]
        max_fullness_field = field_names["max_fullness_field"]

        parameter_specs = [
            f"{str(parameter.get('type', 'int')).strip()} {parameter.get('name')}"
            for parameter in parameters
        ]
        parameter_names = [str(parameter.get("name")) for parameter in parameters]
        caller_declarations = ", ".join(parameter_specs)
        alias_call = ", ".join(parameter_names)
        function_name = str(contract_function(contract).get("name"))
        original = function_name + "_original"
        input_declarations = ", ".join(
            (
                f"unsigned int {port['name']}"
                if str(port.get("name")) == data_port
                else f"int {port['name']}"
            )
            for port in inputs
        )
        rtl_expressions = {
            data_port: data_parameter,
            nbits_port: nbits_parameter,
            num_bits_port: "dsc_cicd_num_bits_before",
            fullness_port: "dsc_cicd_fullness_before",
            write_ptr_port: "dsc_cicd_write_ptr_before",
            fifo_size_port: "dsc_cicd_fifo_size",
            max_fullness_port: "dsc_cicd_max_fullness_before",
        }
        for index, port in enumerate(byte_ports):
            rtl_expressions[port] = f"dsc_cicd_pre[{index}]"
        rtl_arguments = [rtl_expressions[str(port["name"])] for port in inputs]
        rtl_byte_variables = [
            f"dsc_cicd_rtl_byte_{index}"
            for index in range(len(byte_outputs))
        ]
        rtl_call = ", ".join(
            [
                *rtl_arguments,
                *[f"&{value}" for value in rtl_byte_variables],
                "&dsc_cicd_rtl_num_bits",
                "&dsc_cicd_rtl_fullness",
                "&dsc_cicd_rtl_write_ptr",
                "&dsc_cicd_rtl_max_fullness",
            ]
        )
        index_initializers = ", ".join(
            f"(dsc_cicd_start_byte + {index}) % dsc_cicd_fifo_bytes"
            for index in range(len(byte_ports))
        )
        pre_initializers = ", ".join(
            f"dsc_cicd_fifo->{data_field}[dsc_cicd_index[{index}]]"
            for index in range(len(byte_ports))
        )
        c_initializers = ", ".join(
            f"dsc_cicd_fifo->{data_field}[dsc_cicd_index[{index}]]"
            for index in range(len(byte_ports))
        )
        rtl_variable_declarations = "".join(
            f"    int {value} = dsc_cicd_pre[{index}];\n"
            for index, value in enumerate(rtl_byte_variables)
        )
        rtl_raw_initializers = ", ".join(
            f"(unsigned char){value}" for value in rtl_byte_variables
        )

        header = source_dir / "dsc_cicd_overlay.h"
        header.write_text(
            "#ifndef DSC_CICD_OVERLAY_H\n"
            "#define DSC_CICD_OVERLAY_H\n"
            "#include \"dsc_types.h\"\n"
            f"void dsc_cicd_invoke({caller_declarations});\n"
            "#endif\n",
            encoding="utf-8",
        )
        overlay = source_dir / "dsc_cicd_overlay.c"
        overlay.write_text(
            "#include <stdio.h>\n"
            "#include <stdlib.h>\n"
            "#include <string.h>\n"
            "#include \"dsc_cicd_overlay.h\"\n"
            f"extern void {original}({caller_declarations});\n"
            f"extern void dsc_cicd_rtl({input_declarations}, "
            + ", ".join(f"int *{value}" for value in byte_outputs)
            + f", int *{num_bits_output}, int *{fullness_output}, "
            f"int *{write_ptr_output}, int *{max_fullness_output});\n"
            "static int dsc_cicd_mode(void) {\n"
            "    const char *value = getenv(\"DSC_CICD_MODE\");\n"
            "    if (value && strcmp(value, \"SHADOW\") == 0) return 1;\n"
            "    if (value && strcmp(value, \"RTL_RETURN\") == 0) return 2;\n"
            "    return 0;\n"
            "}\n"
            + self.overlay_runtime_metrics_source()
            + f"void dsc_cicd_invoke({caller_declarations}) {{\n"
            f"    fifo_t *dsc_cicd_fifo = &({state_parameter}->"
            f"{fifo_array_field}[{fifo_index_parameter}]);\n"
            f"    int dsc_cicd_num_bits_before = "
            f"{state_parameter}->{counter_field};\n"
            f"    int dsc_cicd_fullness_before = "
            f"dsc_cicd_fifo->{fullness_field};\n"
            f"    int dsc_cicd_write_ptr_before = "
            f"dsc_cicd_fifo->{write_ptr_field};\n"
            f"    int dsc_cicd_fifo_size = dsc_cicd_fifo->{size_field};\n"
            f"    int dsc_cicd_max_fullness_before = "
            f"dsc_cicd_fifo->{max_fullness_field};\n"
            "    int dsc_cicd_fifo_bytes = dsc_cicd_fifo_size >> 3;\n"
            "    int dsc_cicd_start_byte = dsc_cicd_write_ptr_before >> 3;\n"
            f"    int dsc_cicd_index[{len(byte_ports)}] = "
            f"{{{index_initializers}}};\n"
            f"    unsigned char dsc_cicd_pre[{len(byte_ports)}] = "
            f"{{{pre_initializers}}};\n"
            f"    {original}({alias_call});\n"
            f"    unsigned char dsc_cicd_c_after[{len(byte_ports)}] = "
            f"{{{c_initializers}}};\n"
            f"    int dsc_cicd_c_num_bits = "
            f"{state_parameter}->{counter_field};\n"
            f"    int dsc_cicd_c_fullness = "
            f"dsc_cicd_fifo->{fullness_field};\n"
            f"    int dsc_cicd_c_write_ptr = "
            f"dsc_cicd_fifo->{write_ptr_field};\n"
            f"    int dsc_cicd_c_max_fullness = "
            f"dsc_cicd_fifo->{max_fullness_field};\n"
            "    int mode = dsc_cicd_mode();\n"
            "    dsc_cicd_note_call(mode);\n"
            "    if (mode == 0) return;\n"
            + rtl_variable_declarations
            + "    int dsc_cicd_rtl_num_bits = dsc_cicd_num_bits_before;\n"
            "    int dsc_cicd_rtl_fullness = dsc_cicd_fullness_before;\n"
            "    int dsc_cicd_rtl_write_ptr = dsc_cicd_write_ptr_before;\n"
            "    int dsc_cicd_rtl_max_fullness = "
            "dsc_cicd_max_fullness_before;\n"
            f"    dsc_cicd_rtl({rtl_call});\n"
            f"    unsigned char dsc_cicd_rtl_raw[{len(byte_ports)}] = "
            f"{{{rtl_raw_initializers}}};\n"
            f"    unsigned char dsc_cicd_mask[{len(byte_ports)}] = {{0}};\n"
            f"    unsigned char dsc_cicd_merged[{len(byte_ports)}];\n"
            f"    for (int i = 0; i < {nbits_parameter}; ++i) {{\n"
            "        int logical_bit = "
            "(dsc_cicd_write_ptr_before & 7) + i;\n"
            "        int slot = logical_bit >> 3;\n"
            "        dsc_cicd_mask[slot] |= "
            "(unsigned char)(1 << (7 - (logical_bit & 7)));\n"
            "    }\n"
            f"    for (int i = 0; i < {len(byte_ports)}; ++i) "
            "dsc_cicd_merged[i] = dsc_cicd_pre[i];\n"
            f"    for (int slot = 0; slot < {len(byte_ports)}; ++slot) {{\n"
            f"        for (int alias = 0; alias < {len(byte_ports)}; ++alias) {{\n"
            "            if (dsc_cicd_index[alias] == dsc_cicd_index[slot])\n"
            "                dsc_cicd_merged[alias] = "
            "(unsigned char)((dsc_cicd_merged[alias] & "
            "~dsc_cicd_mask[slot]) | "
            "(dsc_cicd_rtl_raw[slot] & dsc_cicd_mask[slot]));\n"
            "        }\n"
            "    }\n"
            "    int dsc_cicd_data_mismatch = 0;\n"
            f"    for (int i = 0; i < {len(byte_ports)}; ++i) "
            "dsc_cicd_data_mismatch |= "
            "dsc_cicd_merged[i] != dsc_cicd_c_after[i];\n"
            "    if (dsc_cicd_data_mismatch || "
            "dsc_cicd_rtl_num_bits != dsc_cicd_c_num_bits || "
            "dsc_cicd_rtl_fullness != dsc_cicd_c_fullness || "
            "dsc_cicd_rtl_write_ptr != dsc_cicd_c_write_ptr || "
            "dsc_cicd_rtl_max_fullness != dsc_cicd_c_max_fullness) {\n"
            "        ++dsc_cicd_mismatches;\n"
            "        fprintf(stderr, \"C/RTL mismatch: data=%d "
            "c_bits=%d rtl_bits=%d c_fullness=%d rtl_fullness=%d "
            "c_write_ptr=%d rtl_write_ptr=%d c_max=%d rtl_max=%d "
            "nbits=%d write_before=%d fifo_size=%d\\n\",\n"
            "                dsc_cicd_data_mismatch, dsc_cicd_c_num_bits, "
            "dsc_cicd_rtl_num_bits, dsc_cicd_c_fullness, "
            "dsc_cicd_rtl_fullness, dsc_cicd_c_write_ptr, "
            "dsc_cicd_rtl_write_ptr, dsc_cicd_c_max_fullness, "
            "dsc_cicd_rtl_max_fullness, "
            f"{nbits_parameter}, dsc_cicd_write_ptr_before, "
            "dsc_cicd_fifo_size);\n"
            "    }\n"
            "    if (mode == 2) {\n"
            f"        for (int i = 0; i < {len(byte_ports)}; ++i) "
            f"dsc_cicd_fifo->{data_field}[dsc_cicd_index[i]] = "
            "dsc_cicd_merged[i];\n"
            f"        {state_parameter}->{counter_field} = "
            "dsc_cicd_rtl_num_bits;\n"
            f"        dsc_cicd_fifo->{fullness_field} = "
            "dsc_cicd_rtl_fullness;\n"
            f"        dsc_cicd_fifo->{write_ptr_field} = "
            "dsc_cicd_rtl_write_ptr;\n"
            f"        dsc_cicd_fifo->{max_fullness_field} = "
            "dsc_cicd_rtl_max_fullness;\n"
            "    }\n"
            "}\n"
            + f"void {function_name}({caller_declarations}) {{\n"
            f"    dsc_cicd_invoke({alias_call});\n"
            "}\n",
            encoding="utf-8",
        )

        assignments = "\n".join(
            f"    dut.{port['name']} = "
            f"static_cast<unsigned long long>({port['name']});"
            for port in inputs
        )
        bridge = source_dir / "rtl_bridge.cpp"
        bridge.write_text(
            "#include <cstdint>\n"
            "#include \"verilated.h\"\n"
            f"#include \"V{safe_identifier(module)}.h\"\n"
            "double sc_time_stamp() { return 0.0; }\n"
            f'extern "C" void dsc_cicd_rtl({input_declarations}, '
            + ", ".join(f"int *{value}" for value in byte_outputs)
            + f", int *{num_bits_output}, int *{fullness_output}, "
            f"int *{write_ptr_output}, int *{max_fullness_output}) {{\n"
            f"    V{safe_identifier(module)} dut;\n"
            f"{assignments}\n"
            "    dut.eval();\n"
            + "".join(
                f"    *{output} = static_cast<int>(dut.{output});\n"
                for output in byte_outputs
            )
            + f"    *{num_bits_output} = "
            f"static_cast<int>(dut.{num_bits_output});\n"
            f"    *{fullness_output} = "
            f"static_cast<int>(dut.{fullness_output});\n"
            f"    *{write_ptr_output} = "
            f"static_cast<int>(dut.{write_ptr_output});\n"
            f"    *{max_fullness_output} = "
            f"static_cast<int>(dut.{max_fullness_output});\n"
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
        return {
            "header": header,
            "overlay": overlay,
            "bridge": bridge,
            "main": main,
            "candidate": candidate_sv,
            "composition": {
                "status": "PASS",
                "adapter_kind": (
                    "explicit_fifo_write_accounting_state_transition"
                ),
                "caller_parameter_count": len(parameters),
                "rtl_input_count": len(inputs),
                "frozen_input_ports": [
                    str(port.get("name")) for port in inputs
                ],
                "rtl_bindings": rtl_arguments,
                "state_outputs": [
                    *byte_outputs,
                    num_bits_output,
                    fullness_output,
                    write_ptr_output,
                    max_fullness_output,
                ],
                "rtl_return_controls_fifo_memory_and_counter": True,
                "callee_transition_inlined_in_source_order": True,
                "residual_symbol_alias_routes_to_dispatcher": True,
            },
        }

    def write_midpoint_line_write_transition_overlay_sources(
        self,
        contract: dict[str, Any],
        source_dir: pathlib.Path,
        module: str,
        candidate_sv: pathlib.Path,
    ) -> dict[str, Any]:
        """Bind bounded conditional writes into reconstructed line storage."""
        semantics = contract.get("semantics", {}) or {}
        bindings = semantics.get("bindings", {}) or {}
        ports = [
            port
            for port in (contract.get("interface", {}) or {}).get("ports", [])
            if isinstance(port, dict)
        ]
        inputs = [port for port in ports if port.get("direction") == "input"]
        outputs = [port for port in ports if port.get("direction") == "output"]
        input_names = {str(port.get("name")) for port in inputs}
        output_names = {str(port.get("name")) for port in outputs}
        selected_ports = [
            str(value) for value in bindings.get("selected_ports", [])
        ]
        component_ports = [
            str(value) for value in bindings.get("component_ports", [])
        ]
        unit_start_ports = [
            str(value) for value in bindings.get("unit_start_ports", [])
        ]
        reconstruction_ports = [
            [str(value) for value in row]
            for row in bindings.get("reconstruction_ports", [])
        ]
        sidebands = [
            {
                key: str(item.get(key, ""))
                for key in ("enable", "component", "address", "value")
            }
            for item in bindings.get("write_sidebands", [])
            if isinstance(item, dict)
        ]
        max_units = int(semantics.get("max_units", 0) or 0)
        samples_per_unit = int(
            semantics.get("samples_per_unit", 0) or 0
        )
        write_slots = int(semantics.get("write_slots", 0) or 0)
        if (
            max_units <= 0
            or samples_per_unit <= 0
            or write_slots != max_units * samples_per_unit
            or len(selected_ports) != max_units
            or len(component_ports) != max_units
            or len(unit_start_ports) != max_units
            or len(reconstruction_ports) != max_units
            or any(
                len(row) != samples_per_unit
                for row in reconstruction_ports
            )
            or len(sidebands) != write_slots
        ):
            raise RuntimeError(
                "midpoint line-write dimensions are incomplete"
            )
        scalar_port_names = {
            str(bindings.get("hpos_port", "")),
            str(bindings.get("pixels_per_group_port", "")),
            str(bindings.get("units_per_group_port", "")),
            str(bindings.get("slice_width_port", "")),
        }
        expected_inputs = {
            *scalar_port_names,
            *selected_ports,
            *component_ports,
            *unit_start_ports,
            *[
                port
                for row in reconstruction_ports
                for port in row
            ],
        }
        expected_outputs = {
            value for item in sidebands for value in item.values()
        }
        if expected_inputs != input_names or expected_outputs != output_names:
            raise RuntimeError(
                "midpoint line-write ports do not match the frozen interface"
            )

        parameters = self.function_parameters(contract)
        parameter_by_name = {
            str(parameter.get("name")): parameter for parameter in parameters
        }
        config_parameter = str(bindings.get("config_parameter", ""))
        state_parameter = str(bindings.get("state_parameter", ""))
        line_parameter = str(bindings.get("line_parameter", ""))
        hpos_parameter = str(bindings.get("hpos_parameter", ""))
        if not {
            config_parameter,
            state_parameter,
            line_parameter,
            hpos_parameter,
        }.issubset(parameter_by_name):
            raise RuntimeError(
                "midpoint line-write parameter bindings are incomplete"
            )
        if not parameter_is_pointer(parameter_by_name[state_parameter]):
            raise RuntimeError(
                "midpoint line-write state parameter must be a pointer"
            )
        if not parameter_is_pointer(parameter_by_name[line_parameter]):
            raise RuntimeError(
                "midpoint line-write output parameter must be a pointer"
            )

        field_names = {
            key: str(bindings.get(key, ""))
            for key in (
                "pixels_per_group_field",
                "units_per_group_field",
                "slice_width_field",
                "selected_field",
                "component_field",
                "unit_start_field",
                "reconstruction_field",
            )
        }
        identifier = re.compile(r"^[A-Za-z_][A-Za-z0-9_]*$")
        if not all(
            identifier.fullmatch(value) for value in field_names.values()
        ):
            raise RuntimeError(
                "midpoint line-write state-field bindings are invalid"
            )
        pixels_field = field_names["pixels_per_group_field"]
        units_field = field_names["units_per_group_field"]
        slice_field = field_names["slice_width_field"]
        selected_field = field_names["selected_field"]
        component_field = field_names["component_field"]
        unit_start_field = field_names["unit_start_field"]
        reconstruction_field = field_names["reconstruction_field"]

        parameter_specs = [
            f"{str(parameter.get('type', 'int')).strip()} {parameter.get('name')}"
            for parameter in parameters
        ]
        parameter_names = [str(parameter.get("name")) for parameter in parameters]
        caller_declarations = ", ".join(parameter_specs)
        alias_call = ", ".join(parameter_names)
        function_name = str(contract_function(contract).get("name"))
        original = function_name + "_original"
        input_declarations = ", ".join(
            f"int {port['name']}" for port in inputs
        )
        rtl_expressions = {
            str(bindings["hpos_port"]): hpos_parameter,
            str(bindings["pixels_per_group_port"]): (
                f"{state_parameter}->{pixels_field}"
            ),
            str(bindings["units_per_group_port"]): (
                f"{state_parameter}->{units_field}"
            ),
            str(bindings["slice_width_port"]): (
                f"{state_parameter}->{slice_field}"
            ),
        }
        for unit in range(max_units):
            rtl_expressions[selected_ports[unit]] = (
                f"{state_parameter}->{selected_field}[{unit}]"
            )
            rtl_expressions[component_ports[unit]] = (
                f"{state_parameter}->{component_field}[{unit}]"
            )
            rtl_expressions[unit_start_ports[unit]] = (
                f"{state_parameter}->{unit_start_field}[{unit}]"
            )
            for sample in range(samples_per_unit):
                rtl_expressions[reconstruction_ports[unit][sample]] = (
                    f"{state_parameter}->{reconstruction_field}"
                    f"[{unit}][{sample}]"
                )
        rtl_arguments = [rtl_expressions[str(port["name"])] for port in inputs]
        output_port_order = [str(port["name"]) for port in outputs]
        output_variables = {
            name: f"dsc_cicd_rtl_{name}" for name in output_port_order
        }
        rtl_call = ", ".join(
            [
                *rtl_arguments,
                *[
                    f"&{output_variables[name]}"
                    for name in output_port_order
                ],
            ]
        )
        output_declarations = "".join(
            f"    int {output_variables[name]} = 0;\n"
            for name in output_port_order
        )
        enable_initializers = ", ".join(
            output_variables[item["enable"]] for item in sidebands
        )
        component_initializers = ", ".join(
            output_variables[item["component"]] for item in sidebands
        )
        address_initializers = ", ".join(
            output_variables[item["address"]] for item in sidebands
        )
        value_initializers = ", ".join(
            output_variables[item["value"]] for item in sidebands
        )

        header = source_dir / "dsc_cicd_overlay.h"
        header.write_text(
            "#ifndef DSC_CICD_OVERLAY_H\n"
            "#define DSC_CICD_OVERLAY_H\n"
            "#include \"dsc_types.h\"\n"
            f"void dsc_cicd_invoke({caller_declarations});\n"
            "#endif\n",
            encoding="utf-8",
        )
        overlay = source_dir / "dsc_cicd_overlay.c"
        overlay.write_text(
            "#include <stdio.h>\n"
            "#include <stdlib.h>\n"
            "#include <string.h>\n"
            "#include \"dsc_cicd_overlay.h\"\n"
            f"extern void {original}({caller_declarations});\n"
            f"extern void dsc_cicd_rtl({input_declarations}, "
            + ", ".join(f"int *{name}" for name in output_port_order)
            + ");\n"
            "static int dsc_cicd_mode(void) {\n"
            "    const char *value = getenv(\"DSC_CICD_MODE\");\n"
            "    if (value && strcmp(value, \"SHADOW\") == 0) return 1;\n"
            "    if (value && strcmp(value, \"RTL_RETURN\") == 0) return 2;\n"
            "    return 0;\n"
            "}\n"
            + self.overlay_runtime_metrics_source()
            + f"void dsc_cicd_invoke({caller_declarations}) {{\n"
            f"    int dsc_cicd_expected_enable[{write_slots}] = {{0}};\n"
            f"    int dsc_cicd_expected_component[{write_slots}] = {{0}};\n"
            f"    int dsc_cicd_expected_address[{write_slots}] = {{0}};\n"
            f"    int dsc_cicd_pre[{write_slots}] = {{0}};\n"
            f"    int dsc_cicd_start_hpos = {hpos_parameter} - "
            f"({hpos_parameter} % {state_parameter}->{pixels_field});\n"
            f"    for (int sample = 0; sample < {samples_per_unit}; ++sample) {{\n"
            "        int active = sample == 0 || "
            f"({hpos_parameter} + sample - 1 < "
            f"{state_parameter}->{slice_field});\n"
            f"        for (int unit = 0; unit < {max_units}; ++unit) {{\n"
            f"            int slot = sample * {max_units} + unit;\n"
            "            dsc_cicd_expected_enable[slot] = "
            f"unit < {state_parameter}->{units_field} && "
            f"{state_parameter}->{selected_field}[unit] && active;\n"
            "            dsc_cicd_expected_component[slot] = "
            f"{state_parameter}->{component_field}[unit];\n"
            "            dsc_cicd_expected_address[slot] = "
            "dsc_cicd_start_hpos + "
            f"{int(semantics.get('padding_left', 0))} + "
            f"{state_parameter}->{unit_start_field}[unit] + sample;\n"
            "            if (dsc_cicd_expected_enable[slot])\n"
            "                dsc_cicd_pre[slot] = "
            f"{line_parameter}[dsc_cicd_expected_component[slot]]"
            "[dsc_cicd_expected_address[slot]];\n"
            "        }\n"
            "    }\n"
            f"    {original}({alias_call});\n"
            f"    int dsc_cicd_c_after[{write_slots}] = {{0}};\n"
            f"    for (int slot = 0; slot < {write_slots}; ++slot) {{\n"
            "        if (dsc_cicd_expected_enable[slot])\n"
            "            dsc_cicd_c_after[slot] = "
            f"{line_parameter}[dsc_cicd_expected_component[slot]]"
            "[dsc_cicd_expected_address[slot]];\n"
            "    }\n"
            "    int mode = dsc_cicd_mode();\n"
            "    dsc_cicd_note_call(mode);\n"
            "    if (mode == 0) return;\n"
            + output_declarations
            + f"    dsc_cicd_rtl({rtl_call});\n"
            f"    int dsc_cicd_rtl_enable[{write_slots}] = "
            f"{{{enable_initializers}}};\n"
            f"    int dsc_cicd_rtl_component[{write_slots}] = "
            f"{{{component_initializers}}};\n"
            f"    int dsc_cicd_rtl_address[{write_slots}] = "
            f"{{{address_initializers}}};\n"
            f"    int dsc_cicd_rtl_value[{write_slots}] = "
            f"{{{value_initializers}}};\n"
            f"    int dsc_cicd_merged[{write_slots}];\n"
            f"    memcpy(dsc_cicd_merged, dsc_cicd_pre, "
            f"sizeof(dsc_cicd_merged));\n"
            "    int dsc_cicd_sideband_mismatch = 0;\n"
            f"    for (int slot = 0; slot < {write_slots}; ++slot) {{\n"
            "        dsc_cicd_sideband_mismatch |= "
            "dsc_cicd_rtl_enable[slot] != "
            "dsc_cicd_expected_enable[slot];\n"
            "        if (dsc_cicd_expected_enable[slot] || "
            "dsc_cicd_rtl_enable[slot]) {\n"
            "            dsc_cicd_sideband_mismatch |= "
            "dsc_cicd_rtl_component[slot] != "
            "dsc_cicd_expected_component[slot];\n"
            "            dsc_cicd_sideband_mismatch |= "
            "dsc_cicd_rtl_address[slot] != "
            "dsc_cicd_expected_address[slot];\n"
            "        }\n"
            "        if (dsc_cicd_rtl_enable[slot] && "
            "dsc_cicd_rtl_component[slot] == "
            "dsc_cicd_expected_component[slot] && "
            "dsc_cicd_rtl_address[slot] == "
            "dsc_cicd_expected_address[slot]) {\n"
            f"            for (int alias = 0; alias < {write_slots}; ++alias) {{\n"
            "                if (dsc_cicd_expected_enable[alias] && "
            "dsc_cicd_expected_component[alias] == "
            "dsc_cicd_rtl_component[slot] && "
            "dsc_cicd_expected_address[alias] == "
            "dsc_cicd_rtl_address[slot])\n"
            "                    dsc_cicd_merged[alias] = "
            "dsc_cicd_rtl_value[slot];\n"
            "            }\n"
            "        }\n"
            "    }\n"
            "    int dsc_cicd_data_mismatch = 0;\n"
            f"    for (int slot = 0; slot < {write_slots}; ++slot) {{\n"
            "        if (dsc_cicd_expected_enable[slot])\n"
            "            dsc_cicd_data_mismatch |= "
            "dsc_cicd_merged[slot] != dsc_cicd_c_after[slot];\n"
            "    }\n"
            "    if (dsc_cicd_sideband_mismatch || "
            "dsc_cicd_data_mismatch) {\n"
            "        ++dsc_cicd_mismatches;\n"
            "        fprintf(stderr, \"C/RTL mismatch: sideband=%d "
            "data=%d hpos=%d units=%d slice_width=%d\\n\",\n"
            "                dsc_cicd_sideband_mismatch, "
            f"dsc_cicd_data_mismatch, {hpos_parameter}, "
            f"{state_parameter}->{units_field}, "
            f"{state_parameter}->{slice_field});\n"
            "    }\n"
            "    if (mode == 2) {\n"
            f"        for (int slot = 0; slot < {write_slots}; ++slot) {{\n"
            "            if (dsc_cicd_expected_enable[slot])\n"
            f"                {line_parameter}"
            "[dsc_cicd_expected_component[slot]]"
            "[dsc_cicd_expected_address[slot]] = "
            "dsc_cicd_merged[slot];\n"
            "        }\n"
            "    }\n"
            "}\n"
            + f"void {function_name}({caller_declarations}) {{\n"
            f"    dsc_cicd_invoke({alias_call});\n"
            "}\n",
            encoding="utf-8",
        )

        assignments = "\n".join(
            f"    dut.{port['name']} = "
            f"static_cast<unsigned long long>({port['name']});"
            for port in inputs
        )
        bridge = source_dir / "rtl_bridge.cpp"
        bridge.write_text(
            "#include <cstdint>\n"
            "#include \"verilated.h\"\n"
            f"#include \"V{safe_identifier(module)}.h\"\n"
            "double sc_time_stamp() { return 0.0; }\n"
            f'extern "C" void dsc_cicd_rtl({input_declarations}, '
            + ", ".join(f"int *{name}" for name in output_port_order)
            + ") {\n"
            f"    V{safe_identifier(module)} dut;\n"
            f"{assignments}\n"
            "    dut.eval();\n"
            + "".join(
                f"    *{name} = static_cast<int>(dut.{name});\n"
                for name in output_port_order
            )
            + "}\n",
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
        return {
            "header": header,
            "overlay": overlay,
            "bridge": bridge,
            "main": main,
            "candidate": candidate_sv,
            "composition": {
                "status": "PASS",
                "adapter_kind": (
                    "explicit_bounded_midpoint_line_write_transition"
                ),
                "caller_parameter_count": len(parameters),
                "rtl_input_count": len(inputs),
                "frozen_input_ports": [
                    str(port.get("name")) for port in inputs
                ],
                "rtl_bindings": rtl_arguments,
                "state_outputs": output_port_order,
                "rtl_return_controls_all_enabled_line_writes": True,
                "final_aliased_line_image_compared": True,
                "residual_symbol_alias_routes_to_dispatcher": True,
            },
        }

    def write_populate_orig_line_transition_overlay_sources(
        self,
        contract: dict[str, Any],
        source_dir: pathlib.Path,
        module: str,
        candidate_sv: pathlib.Path,
    ) -> dict[str, Any]:
        """Replace a picture-to-origLine leaf with request-driven RTL.

        The immutable C function is called against private line storage and
        its pointers are restored before the generated transaction loop runs.
        RTL owns the source address calculation: the adapter only services
        the plane/y/x request returned by RTL and supplies the returned pixel.
        In RTL_RETURN the final line image is copied from RTL sidebands; the
        C image is used solely as the comparison oracle.
        """
        semantics = contract.get("semantics", {}) or {}
        bindings = semantics.get("bindings", {}) or {}
        ports = [
            port
            for port in (contract.get("interface", {}) or {}).get("ports", [])
            if isinstance(port, dict)
        ]
        inputs = [port for port in ports if port.get("direction") == "input"]
        outputs = [port for port in ports if port.get("direction") == "output"]
        input_names = {str(port.get("name")) for port in inputs}
        output_names = {str(port.get("name")) for port in outputs}
        expected_inputs = {
            str(bindings.get(key, ""))
            for key in (
                "native_420_port",
                "native_422_port",
                "xstart_port",
                "ystart_port",
                "num_components_port",
                "slice_width_port",
                "picture_width_port",
                "picture_height_port",
                "vpos_port",
                "component_port",
                "sample_index_port",
                "component_depth_port",
                "pixel_data_port",
            )
        }
        expected_outputs = {
            str(bindings.get(key, ""))
            for key in (
                "read_enable_port",
                "read_plane_port",
                "read_y_port",
                "read_x_port",
                "write_enable_port",
                "write_component_port",
                "write_address_port",
                "write_value_port",
                "illegal_domain_port",
            )
        }
        if "" in expected_inputs or "" in expected_outputs or expected_inputs != input_names or expected_outputs != output_names:
            raise RuntimeError("PopulateOrigLine ports do not match the frozen interface")

        parameters = self.function_parameters(contract)
        parameter_by_name = {
            str(parameter.get("name")): parameter for parameter in parameters
        }
        config_parameter = str(bindings.get("config_parameter", ""))
        state_parameter = str(bindings.get("state_parameter", ""))
        picture_parameter = str(bindings.get("picture_parameter", ""))
        vpos_parameter = str(bindings.get("vpos_parameter", ""))
        if not {config_parameter, state_parameter, picture_parameter, vpos_parameter}.issubset(parameter_by_name):
            raise RuntimeError("PopulateOrigLine parameter bindings are incomplete")
        for pointer_name in (config_parameter, state_parameter, picture_parameter):
            if not parameter_is_pointer(parameter_by_name[pointer_name]):
                raise RuntimeError(f"PopulateOrigLine parameter is not a pointer: {pointer_name}")

        component_count = int(semantics.get("component_count", 0) or 0)
        padding_left = int(semantics.get("padding_left", 0) or 0)
        padding_right = int(semantics.get("padding_right", 0) or 0)
        max_slice_width = int(semantics.get("max_slice_width", 0) or 0)
        max_slice_height = int(semantics.get("max_slice_height", 0) or 0)
        if component_count <= 0 or padding_left < 0 or padding_right < 0 or max_slice_width <= 0 or max_slice_height <= 0:
            raise RuntimeError("PopulateOrigLine bounds are incomplete")

        parameter_specs = [
            f"{str(parameter.get('type', 'int')).strip()} {parameter.get('name')}"
            for parameter in parameters
        ]
        parameter_names = [str(parameter.get("name")) for parameter in parameters]
        caller_declarations = ", ".join(parameter_specs)
        alias_call = ", ".join(parameter_names)
        function_name = str(contract_function(contract).get("name"))
        original = function_name + "_original"
        input_declarations = ", ".join(f"int {port['name']}" for port in inputs)
        output_declarations = ", ".join(f"int *{port['name']}" for port in outputs)

        def binding_port(key: str) -> str:
            value = str(bindings.get(key, ""))
            if value not in input_names | output_names:
                raise RuntimeError(f"PopulateOrigLine binding is not a frozen port: {value}")
            return value

        native_420_port = binding_port("native_420_port")
        native_422_port = binding_port("native_422_port")
        xstart_port = binding_port("xstart_port")
        ystart_port = binding_port("ystart_port")
        num_components_port = binding_port("num_components_port")
        slice_width_port = binding_port("slice_width_port")
        picture_width_port = binding_port("picture_width_port")
        picture_height_port = binding_port("picture_height_port")
        vpos_port = binding_port("vpos_port")
        component_port = binding_port("component_port")
        sample_index_port = binding_port("sample_index_port")
        component_depth_port = binding_port("component_depth_port")
        pixel_data_port = binding_port("pixel_data_port")
        read_enable_port = binding_port("read_enable_port")
        read_plane_port = binding_port("read_plane_port")
        read_y_port = binding_port("read_y_port")
        read_x_port = binding_port("read_x_port")
        write_enable_port = binding_port("write_enable_port")
        write_component_port = binding_port("write_component_port")
        write_address_port = binding_port("write_address_port")
        write_value_port = binding_port("write_value_port")
        illegal_domain_port = binding_port("illegal_domain_port")

        rtl_expressions = {
            native_420_port: f"{config_parameter}->{str(bindings.get('native_420_field', 'native_420'))}",
            native_422_port: f"{config_parameter}->{str(bindings.get('native_422_field', 'native_422'))}",
            xstart_port: f"{config_parameter}->{str(bindings.get('xstart_field', 'xstart'))}",
            ystart_port: f"{config_parameter}->{str(bindings.get('ystart_field', 'ystart'))}",
            num_components_port: f"{state_parameter}->{str(bindings.get('num_components_field', 'numComponents'))}",
            slice_width_port: f"{state_parameter}->{str(bindings.get('slice_width_field', 'sliceWidth'))}",
            picture_width_port: f"{picture_parameter}->{str(bindings.get('picture_width_field', 'w'))}",
            picture_height_port: f"{picture_parameter}->{str(bindings.get('picture_height_field', 'h'))}",
            vpos_port: vpos_parameter,
            component_port: "dsc_cicd_component",
            sample_index_port: "dsc_cicd_sample",
            component_depth_port: f"{state_parameter}->{str(bindings.get('component_depth_field', 'cpntBitDepth'))}[dsc_cicd_component]",
            pixel_data_port: "dsc_cicd_pixel_data",
        }
        if set(rtl_expressions) != input_names:
            raise RuntimeError("PopulateOrigLine RTL input bindings are incomplete")
        rtl_arguments = [rtl_expressions[str(port["name"])] for port in inputs]
        output_variables = {
            name: f"dsc_cicd_rtl_{name}" for name in output_names
        }
        rtl_call = ", ".join(
            [
                *rtl_arguments,
                *[f"&{output_variables[str(port['name'])]}" for port in outputs],
            ]
        )
        output_declarations_source = "".join(
            f"    int {output_variables[str(port['name'])]} = 0;\n"
            for port in outputs
        )

        header = source_dir / "dsc_cicd_overlay.h"
        header.write_text(
            "#ifndef DSC_CICD_OVERLAY_H\n"
            "#define DSC_CICD_OVERLAY_H\n"
            "#include \"dsc_types.h\"\n"
            "#include \"vdo.h\"\n"
            f"void dsc_cicd_invoke({caller_declarations});\n"
            "#endif\n",
            encoding="utf-8",
        )
        overlay = source_dir / "dsc_cicd_overlay.c"
        overlay.write_text(
            "#include <stdio.h>\n"
            "#include <stdlib.h>\n"
            "#include <string.h>\n"
            "#include \"dsc_cicd_overlay.h\"\n"
            f"extern void {original}({caller_declarations});\n"
            f"extern void dsc_cicd_rtl({input_declarations}, {output_declarations});\n"
            "static int dsc_cicd_mode(void) {\n"
            "    const char *value = getenv(\"DSC_CICD_MODE\");\n"
            "    if (value && strcmp(value, \"SHADOW\") == 0) return 1;\n"
            "    if (value && strcmp(value, \"RTL_RETURN\") == 0) return 2;\n"
            "    return 0;\n"
            "}\n"
            "static int dsc_cicd_read_pixel(pic_t *picture, int plane, int y, int x, int *valid) {\n"
            "    *valid = 0;\n"
            "    if (plane == 0 && picture->data.yuv.y && picture->data.yuv.y[y]) { *valid = 1; return picture->data.yuv.y[y][x]; }\n"
            "    if (plane == 1 && picture->data.yuv.u && picture->data.yuv.u[y]) { *valid = 1; return picture->data.yuv.u[y][x]; }\n"
            "    if (plane == 2 && picture->data.yuv.v && picture->data.yuv.v[y]) { *valid = 1; return picture->data.yuv.v[y][x]; }\n"
            "    return 0;\n"
            "}\n"
            + self.overlay_runtime_metrics_source()
            + f"void dsc_cicd_invoke({caller_declarations}) {{\n"
            "    int mode = dsc_cicd_mode();\n"
            "    dsc_cicd_note_call(mode);\n"
            f"    if (!{config_parameter} || !{state_parameter} || !{picture_parameter} || "
            f"{state_parameter}->numComponents < 1 || {state_parameter}->numComponents > {component_count} || "
            f"{state_parameter}->sliceWidth < 1 || {state_parameter}->sliceWidth > {max_slice_width} || "
            f"{vpos_parameter} < 0 || {vpos_parameter} > {max_slice_height} || "
            f"{config_parameter}->native_420 < 0 || {config_parameter}->native_420 > 1 || "
            f"{config_parameter}->native_422 < 0 || {config_parameter}->native_422 > 1 || "
            f"({config_parameter}->native_420 && {config_parameter}->native_422) || "
            f"{config_parameter}->xstart < 0 || {config_parameter}->xstart > {max_slice_width} || "
            f"{config_parameter}->ystart < 0 || {config_parameter}->ystart > {max_slice_height} || "
            f"{picture_parameter}->w < 1 || {picture_parameter}->w > {max_slice_width} || "
            f"{picture_parameter}->h < 1 || {picture_parameter}->h > {max_slice_height} || "
            f"!{picture_parameter}->data.yuv.y || !{picture_parameter}->data.yuv.u || !{picture_parameter}->data.yuv.v || "
            f"({config_parameter}->native_422 == 0 && {state_parameter}->numComponents > 3) || "
            f"({config_parameter}->native_422 && {picture_parameter}->w < 2)) {{\n"
            "        ++dsc_cicd_mismatches;\n"
            "        return;\n"
            "    }\n"
            f"    int dsc_cicd_line_extent = {state_parameter}->sliceWidth + {padding_left} + {padding_right};\n"
            f"    int *dsc_cicd_saved_line[{component_count}] = {{0}};\n"
            f"    int *dsc_cicd_private_line[{component_count}] = {{0}};\n"
            f"    int *dsc_cicd_rtl_line[{component_count}] = {{0}};\n"
            f"    for (int cpnt = 0; cpnt < {state_parameter}->numComponents; ++cpnt) {{\n"
            f"        if (!{state_parameter}->origLine[cpnt] || {state_parameter}->cpntBitDepth[cpnt] < 1 || {state_parameter}->cpntBitDepth[cpnt] > 30) {{\n"
            "            ++dsc_cicd_mismatches;\n"
            f"            for (int restore_cpnt = 0; restore_cpnt < cpnt; ++restore_cpnt) {state_parameter}->origLine[restore_cpnt] = dsc_cicd_saved_line[restore_cpnt];\n"
            "            return;\n"
            "        }\n"
            "        dsc_cicd_saved_line[cpnt] = "
            f"{state_parameter}->origLine[cpnt];\n"
            "        dsc_cicd_private_line[cpnt] = (int *)calloc((size_t)dsc_cicd_line_extent, sizeof(int));\n"
            "        dsc_cicd_rtl_line[cpnt] = (int *)calloc((size_t)dsc_cicd_line_extent, sizeof(int));\n"
            "        if (!dsc_cicd_private_line[cpnt] || !dsc_cicd_rtl_line[cpnt]) {\n"
            "            ++dsc_cicd_mismatches;\n"
            f"            for (int restore_cpnt = 0; restore_cpnt < cpnt; ++restore_cpnt) {state_parameter}->origLine[restore_cpnt] = dsc_cicd_saved_line[restore_cpnt];\n"
            f"            for (int free_cpnt = 0; free_cpnt <= cpnt; ++free_cpnt) {{ free(dsc_cicd_private_line[free_cpnt]); free(dsc_cicd_rtl_line[free_cpnt]); }}\n"
            "            return;\n"
            "        }\n"
            f"        {state_parameter}->origLine[cpnt] = dsc_cicd_private_line[cpnt];\n"
            "    }\n"
            f"    {original}({alias_call});\n"
            f"    for (int cpnt = 0; cpnt < {state_parameter}->numComponents; ++cpnt)\n"
            f"        {state_parameter}->origLine[cpnt] = dsc_cicd_saved_line[cpnt];\n"
            "    if (mode == 0) {\n"
            f"        for (int cpnt = 0; cpnt < {state_parameter}->numComponents; ++cpnt) {{\n"
            f"            for (int sample = 0; sample < {state_parameter}->sliceWidth + {padding_right}; ++sample) {{\n"
            f"                int address = sample + {padding_left};\n"
            f"                {state_parameter}->origLine[cpnt][address] = dsc_cicd_private_line[cpnt][address];\n"
            "            }\n"
            "            free(dsc_cicd_private_line[cpnt]);\n"
            "            free(dsc_cicd_rtl_line[cpnt]);\n"
            "        }\n"
            "        return;\n"
            "    }\n"
            "    int dsc_cicd_mismatch = 0;\n"
            f"    for (int dsc_cicd_component = 0; dsc_cicd_component < {state_parameter}->numComponents; ++dsc_cicd_component) {{\n"
            f"        for (int dsc_cicd_sample = 0; dsc_cicd_sample < {state_parameter}->sliceWidth + {padding_right}; ++dsc_cicd_sample) {{\n"
            "            int dsc_cicd_pixel_data = 0;\n"
            + output_declarations_source
            + "            dsc_cicd_rtl(" + rtl_call + ");\n"
            + "            int dsc_cicd_request_enable = " + output_variables[read_enable_port] + ";\n"
            + "            int dsc_cicd_request_plane = " + output_variables[read_plane_port] + ";\n"
            + "            int dsc_cicd_request_y = " + output_variables[read_y_port] + ";\n"
            + "            int dsc_cicd_request_x = " + output_variables[read_x_port] + ";\n"
            + "            if (dsc_cicd_request_enable) {\n"
            + "                int dsc_cicd_memory_valid = 0;\n"
            + f"                int dsc_cicd_source_width = {picture_parameter}->w;\n"
            + f"                if ({config_parameter}->native_422 && (dsc_cicd_request_plane == 1 || dsc_cicd_request_plane == 2)) dsc_cicd_source_width >>= 1;\n"
            + f"                if (dsc_cicd_request_plane < 0 || dsc_cicd_request_plane > 2 || dsc_cicd_request_y < 0 || dsc_cicd_request_y >= {picture_parameter}->h || dsc_cicd_request_x < 0 || dsc_cicd_request_x >= dsc_cicd_source_width) dsc_cicd_mismatch = 1;\n"
            + "                else { dsc_cicd_pixel_data = dsc_cicd_read_pixel(" + picture_parameter + ", dsc_cicd_request_plane, dsc_cicd_request_y, dsc_cicd_request_x, &dsc_cicd_memory_valid); dsc_cicd_mismatch |= !dsc_cicd_memory_valid; }\n"
            + "                dsc_cicd_rtl(" + rtl_call + ");\n"
            + "                dsc_cicd_mismatch |= " + output_variables[read_enable_port] + " != dsc_cicd_request_enable;\n"
            + "                dsc_cicd_mismatch |= " + output_variables[read_plane_port] + " != dsc_cicd_request_plane;\n"
            + "                dsc_cicd_mismatch |= " + output_variables[read_y_port] + " != dsc_cicd_request_y;\n"
            + "                dsc_cicd_mismatch |= " + output_variables[read_x_port] + " != dsc_cicd_request_x;\n"
            + "            }\n"
            + "            int dsc_cicd_address = dsc_cicd_sample + " + str(padding_left) + ";\n"
            + "            int dsc_cicd_expected = dsc_cicd_private_line[dsc_cicd_component][dsc_cicd_address];\n"
            + "            dsc_cicd_mismatch |= " + output_variables[illegal_domain_port] + " != 0;\n"
            + "            dsc_cicd_mismatch |= " + output_variables[write_enable_port] + " != 1;\n"
            + "            dsc_cicd_mismatch |= " + output_variables[write_component_port] + " != dsc_cicd_component;\n"
            + "            dsc_cicd_mismatch |= " + output_variables[write_address_port] + " != dsc_cicd_address;\n"
            + "            dsc_cicd_mismatch |= " + output_variables[write_value_port] + " != dsc_cicd_expected;\n"
            + "            dsc_cicd_rtl_line[dsc_cicd_component][dsc_cicd_address] = " + output_variables[write_value_port] + ";\n"
            + "        }\n"
            + "    }\n"
            + "    if (dsc_cicd_mismatch) {\n"
            + "        ++dsc_cicd_mismatches;\n"
            + "        fprintf(stderr, \"C/RTL PopulateOrigLine mismatch: mode=%d\\n\", mode);\n"
            + "    }\n"
            + f"    for (int dsc_cicd_component = 0; dsc_cicd_component < {state_parameter}->numComponents; ++dsc_cicd_component) {{\n"
            + f"        for (int dsc_cicd_sample = 0; dsc_cicd_sample < {state_parameter}->sliceWidth + {padding_right}; ++dsc_cicd_sample) {{\n"
            + "            int dsc_cicd_address = dsc_cicd_sample + " + str(padding_left) + ";\n"
            + "            if (mode == 2) " + state_parameter + "->origLine[dsc_cicd_component][dsc_cicd_address] = dsc_cicd_rtl_line[dsc_cicd_component][dsc_cicd_address];\n"
            + "            else " + state_parameter + "->origLine[dsc_cicd_component][dsc_cicd_address] = dsc_cicd_private_line[dsc_cicd_component][dsc_cicd_address];\n"
            + "        }\n"
            + "        free(dsc_cicd_private_line[dsc_cicd_component]);\n"
            + "        free(dsc_cicd_rtl_line[dsc_cicd_component]);\n"
            + "    }\n"
            + "}\n"
            + f"void {function_name}({caller_declarations}) {{\n"
            + f"    dsc_cicd_invoke({alias_call});\n"
            + "}\n",
            encoding="utf-8",
        )

        assignments = "\n".join(
            f"    dut.{port['name']} = static_cast<long long>({port['name']});"
            for port in inputs
        )
        bridge = source_dir / "rtl_bridge.cpp"
        bridge.write_text(
            "#include <cstdint>\n"
            "#include \"verilated.h\"\n"
            f"#include \"V{safe_identifier(module)}.h\"\n"
            "double sc_time_stamp() { return 0.0; }\n"
            f"extern \"C\" void dsc_cicd_rtl({input_declarations}, {output_declarations}) {{\n"
            f"    V{safe_identifier(module)} dut;\n"
            f"{assignments}\n"
            "    dut.eval();\n"
            + "\n".join(
                f"    *{port['name']} = static_cast<int>(dut.{port['name']});"
                for port in outputs
            )
            + "\n}\n",
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
        return {
            "header": header,
            "overlay": overlay,
            "bridge": bridge,
            "main": main,
            "candidate": candidate_sv,
            "composition": {
                "status": "PASS",
                "adapter_kind": "explicit_populate_orig_line_memory_request_transition",
                "caller_parameter_count": len(parameters),
                "rtl_input_count": len(inputs),
                "frozen_input_ports": [str(port.get("name")) for port in inputs],
                "rtl_bindings": rtl_arguments,
                "state_outputs": [str(port.get("name")) for port in outputs],
                "external_pic_memory_is_read_only": True,
                "rtl_produces_plane_y_x_request": True,
                "adapter_services_rtl_memory_request": True,
                "c_oracle_uses_private_orig_line_storage": True,
                "c_oracle_state_pointers_restored_before_rtl": True,
                "rtl_return_commits_rtl_line_image_without_c_fallback": True,
                "every_touched_output_element_compared": True,
                "residual_symbol_alias_routes_to_dispatcher": True,
            },
        }

    def write_bounded_ich_decision_transition_overlay_sources(
        self,
        contract: dict[str, Any],
        source_dir: pathlib.Path,
        module: str,
        candidate_sv: pathlib.Path,
    ) -> dict[str, Any]:
        """Bind a fixed-lane ICH decision composed from accepted child results."""
        semantics = contract.get("semantics", {}) or {}
        bindings = semantics.get("bindings", {}) or {}
        ports = [
            port
            for port in (contract.get("interface", {}) or {}).get("ports", [])
            if isinstance(port, dict)
        ]
        inputs = [port for port in ports if port.get("direction") == "input"]
        outputs = [port for port in ports if port.get("direction") == "output"]
        if len(outputs) != 1:
            raise RuntimeError(
                "ICH decision must expose exactly one return output"
            )
        input_names = {str(port.get("name")) for port in inputs}
        return_port = str(bindings.get("return_port", ""))
        if {str(port.get("name")) for port in outputs} != {return_port}:
            raise RuntimeError("ICH decision return binding is invalid")
        max_units = int(semantics.get("max_units", 0) or 0)
        max_mid_ports = [
            str(value)
            for value in bindings.get("max_mid_error_ports", [])
        ]
        max_error_ports = [
            str(value) for value in bindings.get("max_error_ports", [])
        ]
        max_ich_ports = [
            str(value)
            for value in bindings.get("max_ich_error_ports", [])
        ]
        using_ports = [
            str(value)
            for value in bindings.get("using_midpoint_ports", [])
        ]
        scalar_ports = {
            str(bindings.get("adjusted_size_port", "")),
            str(bindings.get("alternate_prefix_port", "")),
            str(bindings.get("alternate_size_port", "")),
            str(bindings.get("version_port", "")),
            str(bindings.get("units_port", "")),
            str(bindings.get("previous_ich_port", "")),
            str(bindings.get("ich_indices_port", "")),
            str(bindings.get("estimated_bits_port", "")),
            str(bindings.get("flat_index_port", "")),
        }
        if (
            max_units <= 0
            or len(max_mid_ports) != max_units
            or len(max_error_ports) != max_units
            or len(max_ich_ports) != max_units
            or len(using_ports) != max_units
            or {
                *scalar_ports,
                *max_mid_ports,
                *max_error_ports,
                *max_ich_ports,
                *using_ports,
            }
            != input_names
        ):
            raise RuntimeError(
                "ICH decision ports do not match the frozen interface"
            )

        parameters = self.function_parameters(contract)
        parameter_by_name = {
            str(parameter.get("name")): parameter for parameter in parameters
        }
        config_parameter = str(bindings.get("config_parameter", ""))
        state_parameter = str(bindings.get("state_parameter", ""))
        adjusted_parameter = str(
            bindings.get("adjusted_size_parameter", "")
        )
        alternate_prefix_parameter = str(
            bindings.get("alternate_prefix_parameter", "")
        )
        alternate_size_parameter = str(
            bindings.get("alternate_size_parameter", "")
        )
        if not {
            config_parameter,
            state_parameter,
            adjusted_parameter,
            alternate_prefix_parameter,
            alternate_size_parameter,
        }.issubset(parameter_by_name):
            raise RuntimeError(
                "ICH decision parameter bindings are incomplete"
            )
        if not parameter_is_pointer(parameter_by_name[config_parameter]):
            raise RuntimeError("ICH decision config must be a pointer")
        if not parameter_is_pointer(parameter_by_name[state_parameter]):
            raise RuntimeError("ICH decision state must be a pointer")

        field_names = {
            key: str(bindings.get(key, ""))
            for key in (
                "version_field",
                "units_field",
                "previous_ich_field",
                "ich_indices_field",
                "hpos_field",
                "unit_type_field",
                "max_mid_error_field",
                "max_error_field",
                "max_ich_error_field",
            )
        }
        callee_names = {
            key: str(bindings.get(key, ""))
            for key in (
                "midpoint_callee",
                "estimate_callee",
                "flat_callee",
                "log_callee",
            )
        }
        identifier = re.compile(r"^[A-Za-z_][A-Za-z0-9_]*$")
        if not all(
            identifier.fullmatch(value)
            for value in [*field_names.values(), *callee_names.values()]
        ):
            raise RuntimeError(
                "ICH decision field or callee bindings are invalid"
            )
        version_field = field_names["version_field"]
        units_field = field_names["units_field"]
        previous_ich_field = field_names["previous_ich_field"]
        ich_indices_field = field_names["ich_indices_field"]
        hpos_field = field_names["hpos_field"]
        unit_type_field = field_names["unit_type_field"]
        max_mid_field = field_names["max_mid_error_field"]
        max_error_field = field_names["max_error_field"]
        max_ich_field = field_names["max_ich_error_field"]
        midpoint_callee = callee_names["midpoint_callee"]
        estimate_callee = callee_names["estimate_callee"]
        flat_callee = callee_names["flat_callee"]

        parameter_specs = [
            f"{str(parameter.get('type', 'int')).strip()} {parameter.get('name')}"
            for parameter in parameters
        ]
        parameter_names = [str(parameter.get("name")) for parameter in parameters]
        caller_declarations = ", ".join(parameter_specs)
        caller_call = ", ".join(parameter_names)
        function_name = str(contract_function(contract).get("name"))
        original = function_name + "_original"
        input_declarations = ", ".join(
            f"int {port['name']}" for port in inputs
        )
        rtl_expressions = {
            str(bindings["adjusted_size_port"]): adjusted_parameter,
            str(bindings["alternate_prefix_port"]): (
                alternate_prefix_parameter
            ),
            str(bindings["alternate_size_port"]): alternate_size_parameter,
            str(bindings["version_port"]): (
                f"{config_parameter}->{version_field}"
            ),
            str(bindings["units_port"]): (
                f"{state_parameter}->{units_field}"
            ),
            str(bindings["previous_ich_port"]): (
                f"{state_parameter}->{previous_ich_field}"
            ),
            str(bindings["ich_indices_port"]): (
                f"{state_parameter}->{ich_indices_field}"
            ),
            str(bindings["estimated_bits_port"]): (
                "dsc_cicd_estimated_bits"
            ),
            str(bindings["flat_index_port"]): "dsc_cicd_flat_index",
        }
        using_declarations = []
        for unit in range(max_units):
            using_declarations.append(
                f"    int dsc_cicd_using_{unit} = 0;\n"
                f"    if ({unit} < {state_parameter}->{units_field})\n"
                f"        dsc_cicd_using_{unit} = {midpoint_callee}("
                f"{config_parameter}, {state_parameter}, {unit}, "
                f"{state_parameter}->{unit_type_field}[{unit}]);\n"
            )
            rtl_expressions[using_ports[unit]] = (
                f"dsc_cicd_using_{unit}"
            )
            rtl_expressions[max_mid_ports[unit]] = (
                f"{state_parameter}->{max_mid_field}[{unit}]"
            )
            rtl_expressions[max_error_ports[unit]] = (
                f"{state_parameter}->{max_error_field}[{unit}]"
            )
            rtl_expressions[max_ich_ports[unit]] = (
                f"{state_parameter}->{max_ich_field}[{unit}]"
            )
        rtl_arguments = [rtl_expressions[str(port["name"])] for port in inputs]
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
            f"extern int {midpoint_callee}(dsc_cfg_t *, "
            "dsc_state_t *, int, int);\n"
            f"extern int {estimate_callee}(dsc_cfg_t *, dsc_state_t *);\n"
            f"extern int {flat_callee}(dsc_cfg_t *, dsc_state_t *, int);\n"
            f"extern int dsc_cicd_rtl({input_declarations});\n"
            "static int dsc_cicd_mode(void) {\n"
            "    const char *value = getenv(\"DSC_CICD_MODE\");\n"
            "    if (value && strcmp(value, \"SHADOW\") == 0) return 1;\n"
            "    if (value && strcmp(value, \"RTL_RETURN\") == 0) return 2;\n"
            "    return 0;\n"
            "}\n"
            + self.overlay_runtime_metrics_source()
            + f"int dsc_cicd_invoke({caller_declarations}) {{\n"
            f"    int c_value = {original}({caller_call});\n"
            "    int mode = dsc_cicd_mode();\n"
            "    dsc_cicd_note_call(mode);\n"
            "    if (mode == 0) return c_value;\n"
            + "".join(using_declarations)
            + f"    int dsc_cicd_estimated_bits = {estimate_callee}("
            f"{config_parameter}, {state_parameter});\n"
            "    int dsc_cicd_flat_index = 0;\n"
            f"    if ({config_parameter}->{version_field} == 2)\n"
            f"        dsc_cicd_flat_index = {flat_callee}("
            f"{config_parameter}, {state_parameter}, "
            f"{state_parameter}->{hpos_field});\n"
            f"    int rtl_value = dsc_cicd_rtl({rtl_call});\n"
            "    if (rtl_value != c_value) {\n"
            "        ++dsc_cicd_mismatches;\n"
            "        fprintf(stderr, \"C/RTL mismatch: c=%d rtl=%d "
            "units=%d version=%d\\n\", c_value, rtl_value, "
            f"{state_parameter}->{units_field}, "
            f"{config_parameter}->{version_field});\n"
            "    }\n"
            "    return mode == 2 ? rtl_value : c_value;\n"
            "}\n"
            + f"int {function_name}({caller_declarations}) {{\n"
            f"    return dsc_cicd_invoke({caller_call});\n"
            "}\n",
            encoding="utf-8",
        )

        assignments = "\n".join(
            f"    dut.{port['name']} = "
            f"static_cast<unsigned long long>({port['name']});"
            for port in inputs
        )
        bridge = source_dir / "rtl_bridge.cpp"
        bridge.write_text(
            "#include <cstdint>\n"
            "#include \"verilated.h\"\n"
            f"#include \"V{safe_identifier(module)}.h\"\n"
            "double sc_time_stamp() { return 0.0; }\n"
            f'extern "C" int dsc_cicd_rtl({input_declarations}) {{\n'
            f"    V{safe_identifier(module)} dut;\n"
            f"{assignments}\n"
            "    dut.eval();\n"
            f"    return static_cast<int>(dut.{return_port});\n"
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
        return {
            "header": header,
            "overlay": overlay,
            "bridge": bridge,
            "main": main,
            "candidate": candidate_sv,
            "composition": {
                "status": "PASS",
                "adapter_kind": "explicit_bounded_ich_decision_transition",
                "caller_parameter_count": len(parameters),
                "rtl_input_count": len(inputs),
                "frozen_input_ports": [
                    str(port.get("name")) for port in inputs
                ],
                "rtl_bindings": rtl_arguments,
                "state_outputs": [return_port],
                "rtl_return_controls_decision": True,
                "accepted_child_results_are_explicit_inputs": True,
                "simultaneous_rewrite_routes_child_calls_to_rtl": True,
                "residual_symbol_alias_routes_to_dispatcher": True,
            },
        }

    def write_scalar_record_next_state_overlay_sources(
        self,
        contract: dict[str, Any],
        source_dir: pathlib.Path,
        module: str,
        candidate_sv: pathlib.Path,
    ) -> dict[str, Any]:
        """Bind loop-free config/state scalar arithmetic to explicit outputs."""
        semantics = contract.get("semantics", {}) or {}
        bindings = semantics.get("bindings", {}) or {}
        scalar_input_ports = {
            str(key): str(value)
            for key, value in (bindings.get("scalar_input_ports", {}) or {}).items()
        }
        config_ports = {
            str(key): str(value)
            for key, value in (bindings.get("config_ports", {}) or {}).items()
        }
        state_input_ports = {
            str(key): str(value)
            for key, value in (bindings.get("state_input_ports", {}) or {}).items()
        }
        scalar_output_ports = {
            str(key): str(value)
            for key, value in (bindings.get("scalar_output_ports", {}) or {}).items()
        }
        state_output_ports = {
            str(key): str(value)
            for key, value in (bindings.get("state_output_ports", {}) or {}).items()
        }
        ports = [
            port for port in (contract.get("interface", {}) or {}).get("ports", [])
            if isinstance(port, dict)
        ]
        inputs = [port for port in ports if port.get("direction") == "input"]
        outputs = [port for port in ports if port.get("direction") == "output"]
        if (
            {str(port.get("name")) for port in inputs}
            != {
                *scalar_input_ports.values(), *config_ports.values(),
                *state_input_ports.values(),
            }
            or {str(port.get("name")) for port in outputs}
            != {*scalar_output_ports.values(), *state_output_ports.values()}
        ):
            raise RuntimeError(
                "scalar record transition ports do not match the frozen interface"
            )

        parameters = self.function_parameters(contract)
        parameter_by_name = {
            str(parameter.get("name")): parameter for parameter in parameters
        }
        config_parameter = str(bindings.get("config_parameter", ""))
        state_parameter = str(bindings.get("state_parameter", ""))
        scalar_output_parameters = set(scalar_output_ports)
        required_parameters = {
            config_parameter, state_parameter, *scalar_input_ports,
            *scalar_output_parameters,
        }
        if not required_parameters.issubset(parameter_by_name):
            raise RuntimeError("scalar record parameter bindings are incomplete")
        if not parameter_is_pointer(parameter_by_name[config_parameter]):
            raise RuntimeError("scalar record config parameter must be a pointer")
        if not parameter_is_pointer(parameter_by_name[state_parameter]):
            raise RuntimeError("scalar record state parameter must be a pointer")

        identifier = re.compile(r"^[A-Za-z_][A-Za-z0-9_]*$")
        all_identifiers = {
            config_parameter, state_parameter, *scalar_input_ports,
            *scalar_output_parameters, *config_ports, *state_input_ports,
            *state_output_ports,
        }
        if not all(identifier.fullmatch(value) for value in all_identifiers):
            raise RuntimeError("scalar record bindings contain an invalid identifier")

        parameter_specs = [
            f"{str(parameter.get('type', 'int')).strip()} {parameter.get('name')}"
            for parameter in parameters
        ]
        parameter_names = [str(parameter.get("name")) for parameter in parameters]
        caller_declarations = ", ".join(parameter_specs)
        function_name = str(contract_function(contract).get("name"))
        original = function_name + "_original"
        alias_call = ", ".join(parameter_names)
        c_output_names = {
            parameter: f"dsc_cicd_c_{safe_identifier(parameter)}"
            for parameter in scalar_output_parameters
        }
        c_call = ", ".join(
            "&dsc_cicd_c_state"
            if name == state_parameter
            else f"&{c_output_names[name]}"
            if name in c_output_names
            else name
            for name in parameter_names
        )
        rtl_expressions = {
            port: parameter for parameter, port in scalar_input_ports.items()
        }
        rtl_expressions.update({
            port: f"{config_parameter}->{field}"
            for field, port in config_ports.items()
        })
        rtl_expressions.update({
            port: f"{state_parameter}->{field}"
            for field, port in state_input_ports.items()
        })
        rtl_arguments = [rtl_expressions[str(port["name"])] for port in inputs]
        rtl_variables = {
            str(port["name"]): f"dsc_cicd_rtl_{safe_identifier(str(port['name']))}"
            for port in outputs
        }
        rtl_call = ", ".join([
            *rtl_arguments,
            *[f"&{rtl_variables[str(port['name'])]}" for port in outputs],
        ])
        c_expected = {
            port: c_output_names[parameter]
            for parameter, port in scalar_output_ports.items()
        }
        c_expected.update({
            port: f"dsc_cicd_c_state.{field}"
            for field, port in state_output_ports.items()
        })
        rtl_initializers = {
            port: "0" for port in scalar_output_ports.values()
        }
        rtl_initializers.update({
            port: f"{state_parameter}->{field}"
            for field, port in state_output_ports.items()
        })
        c_output_declarations = "".join(
            f"    int {c_output_names[parameter]} = 0;\n"
            for parameter in sorted(c_output_names)
        )
        rtl_output_declarations = "".join(
            f"    int {rtl_variables[str(port['name'])]} = "
            f"{rtl_initializers[str(port['name'])]};\n"
            for port in outputs
        )
        mismatch_expression = " || ".join(
            f"{rtl_variables[str(port['name'])]} != {c_expected[str(port['name'])]}"
            for port in outputs
        )
        apply_c = "".join(
            f"        *{parameter} = {c_output_names[parameter]};\n"
            for parameter in scalar_output_ports
        ) + "".join(
            f"        {state_parameter}->{field} = dsc_cicd_c_state.{field};\n"
            for field in state_output_ports
        )
        apply_rtl = "".join(
            f"        *{parameter} = {rtl_variables[port]};\n"
            for parameter, port in scalar_output_ports.items()
        ) + "".join(
            f"        {state_parameter}->{field} = {rtl_variables[port]};\n"
            for field, port in state_output_ports.items()
        )
        input_declarations = ", ".join(
            f"int {port['name']}" for port in inputs
        )
        output_pointer_declarations = ", ".join(
            f"int *{port['name']}" for port in outputs
        )

        header = source_dir / "dsc_cicd_overlay.h"
        header.write_text(
            "#ifndef DSC_CICD_OVERLAY_H\n"
            "#define DSC_CICD_OVERLAY_H\n"
            "#include \"dsc_types.h\"\n"
            f"void dsc_cicd_invoke({caller_declarations});\n"
            "#endif\n",
            encoding="utf-8",
        )
        overlay = source_dir / "dsc_cicd_overlay.c"
        overlay.write_text(
            "#include <stdio.h>\n"
            "#include <stdlib.h>\n"
            "#include <string.h>\n"
            "#include \"dsc_cicd_overlay.h\"\n"
            f"extern void {original}({caller_declarations});\n"
            f"extern void dsc_cicd_rtl({input_declarations}, "
            f"{output_pointer_declarations});\n"
            "static int dsc_cicd_mode(void) {\n"
            "    const char *value = getenv(\"DSC_CICD_MODE\");\n"
            "    if (value && strcmp(value, \"SHADOW\") == 0) return 1;\n"
            "    if (value && strcmp(value, \"RTL_RETURN\") == 0) return 2;\n"
            "    return 0;\n"
            "}\n"
            + self.overlay_runtime_metrics_source()
            + f"void dsc_cicd_invoke({caller_declarations}) {{\n"
            f"    dsc_state_t dsc_cicd_c_state = *{state_parameter};\n"
            + c_output_declarations
            + f"    {original}({c_call});\n"
            "    int mode = dsc_cicd_mode();\n"
            "    dsc_cicd_note_call(mode);\n"
            "    if (mode == 0) {\n"
            + apply_c
            + "        return;\n"
            "    }\n"
            + rtl_output_declarations
            + f"    dsc_cicd_rtl({rtl_call});\n"
            f"    if ({mismatch_expression}) {{\n"
            "        ++dsc_cicd_mismatches;\n"
            "        fprintf(stderr, \"C/RTL scalar record mismatch\\n\");\n"
            "    }\n"
            "    if (mode == 2) {\n"
            + apply_rtl
            + "        return;\n"
            "    }\n"
            + apply_c
            + "}\n"
            + f"void {function_name}({caller_declarations}) {{\n"
            f"    dsc_cicd_invoke({alias_call});\n"
            "}\n",
            encoding="utf-8",
        )

        assignments = "\n".join(
            f"    dut.{port['name']} = static_cast<unsigned int>({port['name']});"
            for port in inputs
        )
        bridge = source_dir / "rtl_bridge.cpp"
        bridge.write_text(
            "#include <cstdint>\n"
            "#include \"verilated.h\"\n"
            f"#include \"V{safe_identifier(module)}.h\"\n"
            "double sc_time_stamp() { return 0.0; }\n"
            f'extern "C" void dsc_cicd_rtl({input_declarations}, '
            f"{output_pointer_declarations}) {{\n"
            f"    V{safe_identifier(module)} dut;\n"
            f"{assignments}\n"
            "    dut.eval();\n"
            + "".join(
                f"    *{port['name']} = static_cast<int>(dut.{port['name']});\n"
                for port in outputs
            )
            + "}\n",
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
        return {
            "header": header,
            "overlay": overlay,
            "bridge": bridge,
            "main": main,
            "candidate": candidate_sv,
            "composition": {
                "status": "PASS",
                "adapter_kind": "explicit_scalar_record_next_state",
                "caller_parameter_count": len(parameters),
                "rtl_input_count": len(inputs),
                "frozen_input_ports": [str(port.get("name")) for port in inputs],
                "rtl_bindings": rtl_arguments,
                "state_outputs": [str(port.get("name")) for port in outputs],
                "rtl_return_controls_scalar_record_state_in_rtl_return": True,
                "residual_symbol_alias_routes_to_dispatcher": True,
            },
        }

    def write_sampled_lookup_transition_overlay_sources(
        self,
        contract: dict[str, Any],
        source_dir: pathlib.Path,
        module: str,
        candidate_sv: pathlib.Path,
    ) -> dict[str, Any]:
        """Bind history/line-buffer pointers through a fixed sampled-tap interface."""
        semantics = contract.get("semantics", {}) or {}
        bindings = semantics.get("bindings", {}) or {}
        constants = semantics.get("constants", {}) or {}
        history_ports = [str(value) for value in bindings.get("history_ports", [])]
        base_ports = [str(value) for value in bindings.get("native_base_ports", [])]
        base1_ports = [str(value) for value in bindings.get("native_base1_ports", [])]
        simple_ports = [str(value) for value in bindings.get("simple_tap_ports", [])]
        output_ports = [str(value) for value in bindings.get("output_ports", [])]
        component_count = int(constants.get("component_count", 0) or 0)
        ich_size = int(constants.get("ich_size", 0) or 0)
        pixels_above = int(constants.get("ich_pixels_above", 0) or 0)
        padding_left = int(constants.get("padding_left", 0) or 0)
        if not (
            component_count == 4
            and len(history_ports) == component_count
            and len(base_ports) == component_count
            and len(base1_ports) == component_count
            and len(simple_ports) == component_count - 1
            and len(output_ports) == component_count
            and ich_size > pixels_above > 0
        ):
            raise RuntimeError("sampled lookup fixed extents are incomplete")

        ports = [
            port for port in (contract.get("interface", {}) or {}).get("ports", [])
            if isinstance(port, dict)
        ]
        inputs = [port for port in ports if port.get("direction") == "input"]
        outputs = [port for port in ports if port.get("direction") == "output"]
        fixed_inputs = {
            "native_420", "native_422", "entry", "first_line_flag",
            "is_odd_line", "num_components",
        }
        if (
            {str(port.get("name")) for port in inputs}
            != {
                *fixed_inputs, *history_ports, *base_ports, *base1_ports,
                *simple_ports,
            }
            or {str(port.get("name")) for port in outputs} != set(output_ports)
        ):
            raise RuntimeError("sampled lookup ports do not match the frozen interface")

        parameters = self.function_parameters(contract)
        parameter_by_name = {
            str(parameter.get("name")): parameter for parameter in parameters
        }
        binding_keys = [
            "config_parameter", "state_parameter", "output_parameter",
            "entry_parameter", "horizontal_position_parameter",
            "first_line_parameter", "odd_line_parameter",
        ]
        parameter_bindings = {
            key: str(bindings.get(key, "")) for key in binding_keys
        }
        if not set(parameter_bindings.values()).issubset(parameter_by_name):
            raise RuntimeError("sampled lookup parameter bindings are incomplete")
        config_parameter = parameter_bindings["config_parameter"]
        state_parameter = parameter_bindings["state_parameter"]
        output_parameter = parameter_bindings["output_parameter"]
        entry_parameter = parameter_bindings["entry_parameter"]
        hpos_parameter = parameter_bindings["horizontal_position_parameter"]
        first_line_parameter = parameter_bindings["first_line_parameter"]
        odd_line_parameter = parameter_bindings["odd_line_parameter"]
        if not all(
            parameter_is_pointer(parameter_by_name[name])
            for name in (config_parameter, state_parameter, output_parameter)
        ):
            raise RuntimeError("sampled lookup record/output parameters must be pointers")

        field_keys = [
            "native_420_field", "native_422_field", "history_field",
            "history_pixels_field", "num_components_field",
            "pixels_in_group_field", "prev_line_field", "slice_width_field",
        ]
        fields = {key: str(bindings.get(key, "")) for key in field_keys}
        identifier = re.compile(r"^[A-Za-z_][A-Za-z0-9_]*$")
        if not all(identifier.fullmatch(value) for value in fields.values()):
            raise RuntimeError("sampled lookup field bindings are invalid")

        parameter_specs = [
            f"{str(parameter.get('type', 'int')).strip()} {parameter.get('name')}"
            for parameter in parameters
        ]
        parameter_names = [str(parameter.get("name")) for parameter in parameters]
        caller_declarations = ", ".join(parameter_specs)
        function_name = str(contract_function(contract).get("name"))
        original = function_name + "_original"
        alias_call = ", ".join(parameter_names)
        c_call = ", ".join(
            "dsc_cicd_c_output" if name == output_parameter else name
            for name in parameter_names
        )
        reserved = ich_size - pixels_above
        history_field = fields["history_field"]
        history_pixels_field = fields["history_pixels_field"]
        prev_line_field = fields["prev_line_field"]
        num_components_field = fields["num_components_field"]
        pixels_in_group_field = fields["pixels_in_group_field"]
        slice_width_field = fields["slice_width_field"]
        native_420_field = fields["native_420_field"]
        native_422_field = fields["native_422_field"]

        input_declarations = ", ".join(
            (
                f"unsigned int {port['name']}"
                if int(port.get("width", 1)) == 32 and not port.get("signed")
                else f"int {port['name']}"
            )
            for port in inputs
        )
        output_pointer_declarations = ", ".join(
            f"unsigned int *{port}" for port in output_ports
        )
        rtl_expressions = {
            "native_420": f"{config_parameter}->{native_420_field}",
            "native_422": f"{config_parameter}->{native_422_field}",
            "entry": entry_parameter,
            "first_line_flag": first_line_parameter,
            "is_odd_line": odd_line_parameter,
            "num_components": f"{state_parameter}->{num_components_field}",
        }
        for index, port in enumerate(history_ports):
            rtl_expressions[port] = f"dsc_cicd_history[{index}]"
        for index, port in enumerate(base_ports):
            rtl_expressions[port] = f"dsc_cicd_base[{index}]"
        for index, port in enumerate(base1_ports):
            rtl_expressions[port] = f"dsc_cicd_base1[{index}]"
        for index, port in enumerate(simple_ports):
            rtl_expressions[port] = f"dsc_cicd_simple[{index}]"
        rtl_arguments = [rtl_expressions[str(port["name"])] for port in inputs]
        rtl_output_variables = [
            f"dsc_cicd_rtl_output_{index}" for index in range(component_count)
        ]
        rtl_call = ", ".join([
            *rtl_arguments,
            *[f"&{value}" for value in rtl_output_variables],
        ])
        copy_c = "".join(
            f"        {output_parameter}[{index}] = dsc_cicd_c_output[{index}];\n"
            for index in range(component_count)
        )
        copy_rtl = "".join(
            f"        {output_parameter}[{index}] = {rtl_output_variables[index]};\n"
            for index in range(component_count)
        )
        rtl_output_declarations = "".join(
            f"    unsigned int {value} = 0;\n"
            for value in rtl_output_variables
        )
        mismatch_expression = " || ".join(
            f"{rtl_output_variables[index]} != dsc_cicd_c_output[{index}]"
            for index in range(component_count)
        )

        header = source_dir / "dsc_cicd_overlay.h"
        header.write_text(
            "#ifndef DSC_CICD_OVERLAY_H\n"
            "#define DSC_CICD_OVERLAY_H\n"
            "#include \"dsc_types.h\"\n"
            f"void dsc_cicd_invoke({caller_declarations});\n"
            "#endif\n",
            encoding="utf-8",
        )
        overlay = source_dir / "dsc_cicd_overlay.c"
        overlay.write_text(
            "#include <stdio.h>\n"
            "#include <stdlib.h>\n"
            "#include <string.h>\n"
            "#include \"dsc_cicd_overlay.h\"\n"
            f"extern void {original}({caller_declarations});\n"
            f"extern void dsc_cicd_rtl({input_declarations}, "
            f"{output_pointer_declarations});\n"
            "static int dsc_cicd_mode(void) {\n"
            "    const char *value = getenv(\"DSC_CICD_MODE\");\n"
            "    if (value && strcmp(value, \"SHADOW\") == 0) return 1;\n"
            "    if (value && strcmp(value, \"RTL_RETURN\") == 0) return 2;\n"
            "    return 0;\n"
            "}\n"
            + self.overlay_runtime_metrics_source()
            + f"void dsc_cicd_invoke({caller_declarations}) {{\n"
            f"    unsigned int dsc_cicd_c_output[{component_count}] = {{0}};\n"
            f"    {original}({c_call});\n"
            "    int mode = dsc_cicd_mode();\n"
            "    dsc_cicd_note_call(mode);\n"
            "    if (mode == 0) {\n"
            + copy_c
            + "        return;\n"
            "    }\n"
            f"    unsigned int dsc_cicd_history[{component_count}] = {{0}};\n"
            f"    unsigned int dsc_cicd_base[{component_count}] = {{0}};\n"
            f"    unsigned int dsc_cicd_base1[{component_count}] = {{0}};\n"
            f"    unsigned int dsc_cicd_simple[{component_count - 1}] = {{0}};\n"
            f"    for (int i = 0; i < {component_count}; ++i) {{\n"
            f"        if (i < {state_parameter}->{num_components_field})\n"
            f"            dsc_cicd_history[i] = {state_parameter}->{history_field}."
            f"{history_pixels_field}[i][{entry_parameter}];\n"
            "    }\n"
            f"    int dsc_cicd_center = ({hpos_parameter} / "
            f"{state_parameter}->{pixels_in_group_field}) * "
            f"{state_parameter}->{pixels_in_group_field} + "
            f"({state_parameter}->{pixels_in_group_field} / 2);\n"
            f"    int dsc_cicd_native = {config_parameter}->{native_420_field} || "
            f"{config_parameter}->{native_422_field};\n"
            "    int dsc_cicd_low = dsc_cicd_native ? 2 : "
            f"({pixels_above} / 2);\n"
            f"    int dsc_cicd_high = {state_parameter}->{slice_width_field} - 1 - "
            f"(dsc_cicd_native ? 2 : ({pixels_above} / 2));\n"
            "    if (dsc_cicd_center < dsc_cicd_low) dsc_cicd_center = dsc_cicd_low;\n"
            "    else if (dsc_cicd_center > dsc_cicd_high) dsc_cicd_center = dsc_cicd_high;\n"
            f"    if (!{first_line_parameter} && ({entry_parameter} >= {reserved})) {{\n"
            f"        int dsc_cicd_distance = {entry_parameter} - {reserved};\n"
            "        int dsc_cicd_offset = (dsc_cicd_distance + 1) >> 1;\n"
            f"        if ({config_parameter}->{native_420_field} || "
            f"{config_parameter}->{native_422_field}) {{\n"
            f"            int dsc_cicd_index = dsc_cicd_center + dsc_cicd_offset - 2 + {padding_left};\n"
            f"            for (int i = 0; i < {component_count}; ++i) {{\n"
            f"                dsc_cicd_base[i] = {state_parameter}->{prev_line_field}[i][dsc_cicd_index];\n"
            f"                dsc_cicd_base1[i] = {state_parameter}->{prev_line_field}[i][dsc_cicd_index + 1];\n"
            "            }\n"
            "        } else {\n"
            f"            int dsc_cicd_index = dsc_cicd_center + dsc_cicd_distance - ({pixels_above} / 2) + {padding_left};\n"
            f"            for (int i = 0; i < {component_count - 1}; ++i)\n"
            f"                dsc_cicd_simple[i] = {state_parameter}->{prev_line_field}[i][dsc_cicd_index];\n"
            "        }\n"
            "    }\n"
            + rtl_output_declarations
            + f"    dsc_cicd_rtl({rtl_call});\n"
            f"    if ({mismatch_expression}) {{\n"
            "        ++dsc_cicd_mismatches;\n"
            "        fprintf(stderr, \"C/RTL sampled lookup mismatch: entry=%d first=%d odd=%d\\n\", "
            f"{entry_parameter}, {first_line_parameter}, {odd_line_parameter});\n"
            "    }\n"
            "    if (mode == 2) {\n"
            + copy_rtl
            + "        return;\n"
            "    }\n"
            + copy_c
            + "}\n"
            + f"void {function_name}({caller_declarations}) {{\n"
            f"    dsc_cicd_invoke({alias_call});\n"
            "}\n",
            encoding="utf-8",
        )

        assignments = "\n".join(
            f"    dut.{port['name']} = static_cast<unsigned int>({port['name']});"
            for port in inputs
        )
        bridge = source_dir / "rtl_bridge.cpp"
        bridge.write_text(
            "#include <cstdint>\n"
            "#include \"verilated.h\"\n"
            f"#include \"V{safe_identifier(module)}.h\"\n"
            "double sc_time_stamp() { return 0.0; }\n"
            f'extern "C" void dsc_cicd_rtl({input_declarations}, '
            f"{output_pointer_declarations}) {{\n"
            f"    static V{safe_identifier(module)} dut;\n"
            f"{assignments}\n"
            "    dut.eval();\n"
            + "".join(
                f"    *{port} = static_cast<unsigned int>(dut.{port});\n"
                for port in output_ports
            )
            + "}\n",
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
        return {
            "header": header,
            "overlay": overlay,
            "bridge": bridge,
            "main": main,
            "candidate": candidate_sv,
            "composition": {
                "status": "PASS",
                "adapter_kind": "explicit_sampled_lookup_transition",
                "caller_parameter_count": len(parameters),
                "rtl_input_count": len(inputs),
                "frozen_input_ports": [str(port.get("name")) for port in inputs],
                "rtl_bindings": rtl_arguments,
                "state_outputs": output_ports,
                "rtl_return_controls_output_buffer_in_rtl_return": True,
                "residual_symbol_alias_routes_to_dispatcher": True,
            },
        }

    def write_scalar_record_memory_transition_overlay_sources(
        self,
        contract: dict[str, Any],
        source_dir: pathlib.Path,
        module: str,
        candidate_sv: pathlib.Path,
    ) -> dict[str, Any]:
        """Bind scalar next state plus one indexed memory write sideband."""
        semantics = contract.get("semantics", {}) or {}
        bindings = semantics.get("bindings", {}) or {}
        config_ports = {
            str(key): str(value)
            for key, value in (bindings.get("config_ports", {}) or {}).items()
        }
        state_input_ports = {
            str(key): str(value)
            for key, value in (bindings.get("state_input_ports", {}) or {}).items()
        }
        state_output_ports = {
            str(key): str(value)
            for key, value in (bindings.get("state_output_ports", {}) or {}).items()
        }
        memory_write_ports = {
            str(key): str(value)
            for key, value in (bindings.get("memory_write_ports", {}) or {}).items()
        }
        memory_field = str(bindings.get("memory_field", ""))
        ports = [
            port for port in (contract.get("interface", {}) or {}).get("ports", [])
            if isinstance(port, dict)
        ]
        inputs = [port for port in ports if port.get("direction") == "input"]
        outputs = [port for port in ports if port.get("direction") == "output"]
        if (
            {str(port.get("name")) for port in inputs}
            != {*config_ports.values(), *state_input_ports.values()}
            or {str(port.get("name")) for port in outputs}
            != {*state_output_ports.values(), *memory_write_ports.values()}
            or set(memory_write_ports) != {"enable", "index", "value"}
            or not memory_field
        ):
            raise RuntimeError(
                "scalar record memory ports do not match the frozen interface"
            )

        parameters = self.function_parameters(contract)
        parameter_by_name = {
            str(parameter.get("name")): parameter for parameter in parameters
        }
        config_parameter = str(bindings.get("config_parameter", ""))
        state_parameter = str(bindings.get("state_parameter", ""))
        if set(parameter_by_name) != {config_parameter, state_parameter}:
            raise RuntimeError(
                "scalar record memory transition requires exactly config/state parameters"
            )
        if not parameter_is_pointer(parameter_by_name[config_parameter]):
            raise RuntimeError("scalar record memory config parameter must be a pointer")
        if not parameter_is_pointer(parameter_by_name[state_parameter]):
            raise RuntimeError("scalar record memory state parameter must be a pointer")

        identifier = re.compile(r"^[A-Za-z_][A-Za-z0-9_]*$")
        all_identifiers = {
            config_parameter, state_parameter, memory_field,
            *config_ports, *state_input_ports, *state_output_ports,
            *config_ports.values(), *state_input_ports.values(),
            *state_output_ports.values(), *memory_write_ports.values(),
        }
        if not all(identifier.fullmatch(value) for value in all_identifiers):
            raise RuntimeError("scalar record memory bindings contain an invalid identifier")

        parameter_specs = [
            f"{str(parameter.get('type', 'int')).strip()} {parameter.get('name')}"
            for parameter in parameters
        ]
        parameter_names = [str(parameter.get("name")) for parameter in parameters]
        caller_declarations = ", ".join(parameter_specs)
        function_name = str(contract_function(contract).get("name"))
        original = function_name + "_original"
        alias_call = ", ".join(parameter_names)
        c_call = ", ".join(
            "&dsc_cicd_c_state" if name == state_parameter else name
            for name in parameter_names
        )
        rtl_expressions = {
            port: f"{config_parameter}->{field}"
            for field, port in config_ports.items()
        }
        rtl_expressions.update({
            port: f"{state_parameter}->{field}"
            for field, port in state_input_ports.items()
        })
        rtl_arguments = [rtl_expressions[str(port["name"])] for port in inputs]
        rtl_variables = {
            str(port["name"]): f"dsc_cicd_rtl_{safe_identifier(str(port['name']))}"
            for port in outputs
        }
        rtl_call = ", ".join([
            *rtl_arguments,
            *[f"&{rtl_variables[str(port['name'])]}" for port in outputs],
        ])
        c_expected = {
            port: f"dsc_cicd_c_state.{field}"
            for field, port in state_output_ports.items()
        }
        c_expected.update({
            memory_write_ports["enable"]: "dsc_cicd_c_write_enable",
            memory_write_ports["index"]: "dsc_cicd_c_write_index",
            memory_write_ports["value"]: "dsc_cicd_c_write_value",
        })
        rtl_initializers = {
            port: f"{state_parameter}->{field}"
            for field, port in state_output_ports.items()
        }
        rtl_initializers.update({
            memory_write_ports["enable"]: "0",
            memory_write_ports["index"]: f"{state_parameter}->chunkCount",
            memory_write_ports["value"]: "0",
        })
        rtl_output_declarations = "".join(
            f"    int {rtl_variables[str(port['name'])]} = "
            f"{rtl_initializers[str(port['name'])]};\n"
            for port in outputs
        )
        mismatch_expression = " || ".join(
            f"{rtl_variables[str(port['name'])]} != {c_expected[str(port['name'])]}"
            for port in outputs
        )
        apply_c = "".join(
            f"        {state_parameter}->{field} = dsc_cicd_c_state.{field};\n"
            for field in state_output_ports
        ) + (
            f"        if (dsc_cicd_c_write_enable)\n"
            f"            {state_parameter}->{memory_field}[dsc_cicd_c_write_index] = "
            "dsc_cicd_c_write_value;\n"
        )
        apply_rtl = "".join(
            f"        {state_parameter}->{field} = {rtl_variables[port]};\n"
            for field, port in state_output_ports.items()
        ) + (
            f"        if ({rtl_variables[memory_write_ports['enable']]})\n"
            f"            {state_parameter}->{memory_field}"
            f"[{rtl_variables[memory_write_ports['index']]}] = "
            f"{rtl_variables[memory_write_ports['value']]};\n"
        )
        input_declarations = ", ".join(
            f"int {port['name']}" for port in inputs
        )
        output_pointer_declarations = ", ".join(
            f"int *{port['name']}" for port in outputs
        )

        header = source_dir / "dsc_cicd_overlay.h"
        header.write_text(
            "#ifndef DSC_CICD_OVERLAY_H\n"
            "#define DSC_CICD_OVERLAY_H\n"
            "#include \"dsc_types.h\"\n"
            f"void dsc_cicd_invoke({caller_declarations});\n"
            "#endif\n",
            encoding="utf-8",
        )
        overlay = source_dir / "dsc_cicd_overlay.c"
        overlay.write_text(
            "#include <stdio.h>\n"
            "#include <stdlib.h>\n"
            "#include <string.h>\n"
            "#include \"dsc_cicd_overlay.h\"\n"
            f"extern void {original}({caller_declarations});\n"
            f"extern void dsc_cicd_rtl({input_declarations}, "
            f"{output_pointer_declarations});\n"
            "static int dsc_cicd_mode(void) {\n"
            "    const char *value = getenv(\"DSC_CICD_MODE\");\n"
            "    if (value && strcmp(value, \"SHADOW\") == 0) return 1;\n"
            "    if (value && strcmp(value, \"RTL_RETURN\") == 0) return 2;\n"
            "    return 0;\n"
            "}\n"
            + self.overlay_runtime_metrics_source()
            + f"void dsc_cicd_invoke({caller_declarations}) {{\n"
            f"    dsc_state_t dsc_cicd_c_state = *{state_parameter};\n"
            f"    int dsc_cicd_c_write_enable = "
            f"(({state_parameter}->chunkPixelTimes + 1 >= {state_parameter}->sliceWidth) && "
            f"({config_parameter}->vbr_enable != 0) && ({state_parameter}->isEncoder != 0));\n"
            f"    int dsc_cicd_c_write_index = {state_parameter}->chunkCount;\n"
            "    int dsc_cicd_c_write_value = 0;\n"
            "    int dsc_cicd_prior_write_value = 0;\n"
            f"    if (dsc_cicd_c_write_enable)\n"
            f"        dsc_cicd_prior_write_value = {state_parameter}->{memory_field}"
            "[dsc_cicd_c_write_index];\n"
            f"    {original}({c_call});\n"
            "    if (dsc_cicd_c_write_enable) {\n"
            f"        dsc_cicd_c_write_value = {state_parameter}->{memory_field}"
            "[dsc_cicd_c_write_index];\n"
            f"        {state_parameter}->{memory_field}[dsc_cicd_c_write_index] = "
            "dsc_cicd_prior_write_value;\n"
            "    }\n"
            "    int mode = dsc_cicd_mode();\n"
            "    dsc_cicd_note_call(mode);\n"
            "    if (mode == 0) {\n"
            + apply_c
            + "        return;\n"
            "    }\n"
            + rtl_output_declarations
            + f"    dsc_cicd_rtl({rtl_call});\n"
            f"    if ({mismatch_expression}) {{\n"
            "        ++dsc_cicd_mismatches;\n"
            "        fprintf(stderr, \"C/RTL scalar-memory mismatch: write=%d index=%d value=%d\\n\", "
            f"{rtl_variables[memory_write_ports['enable']]}, "
            f"{rtl_variables[memory_write_ports['index']]}, "
            f"{rtl_variables[memory_write_ports['value']]});\n"
            "    }\n"
            "    if (mode == 2) {\n"
            + apply_rtl
            + "        return;\n"
            "    }\n"
            + apply_c
            + "}\n"
            + f"void {function_name}({caller_declarations}) {{\n"
            f"    dsc_cicd_invoke({alias_call});\n"
            "}\n",
            encoding="utf-8",
        )

        assignments = "\n".join(
            f"    dut.{port['name']} = static_cast<std::uint32_t>({port['name']});"
            for port in inputs
        )
        output_assignments = "".join(
            f"    *{port['name']} = "
            + (
                f"static_cast<std::int32_t>(dut.{port['name']});\n"
                if port.get("signed") and int(port.get("width", 1)) == 32
                else f"static_cast<int>(dut.{port['name']});\n"
            )
            for port in outputs
        )
        bridge = source_dir / "rtl_bridge.cpp"
        bridge.write_text(
            "#include <cstdint>\n"
            "#include \"verilated.h\"\n"
            f"#include \"V{safe_identifier(module)}.h\"\n"
            "double sc_time_stamp() { return 0.0; }\n"
            f'extern "C" void dsc_cicd_rtl({input_declarations}, '
            f"{output_pointer_declarations}) {{\n"
            f"    static V{safe_identifier(module)} dut;\n"
            f"{assignments}\n"
            "    dut.eval();\n"
            + output_assignments
            + "}\n",
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
        return {
            "header": header,
            "overlay": overlay,
            "bridge": bridge,
            "main": main,
            "candidate": candidate_sv,
            "composition": {
                "status": "PASS",
                "adapter_kind": "explicit_scalar_record_memory_transition",
                "caller_parameter_count": len(parameters),
                "rtl_input_count": len(inputs),
                "frozen_input_ports": [str(port.get("name")) for port in inputs],
                "rtl_bindings": rtl_arguments,
                "state_outputs": [str(port.get("name")) for port in outputs],
                "rtl_return_controls_scalar_and_indexed_memory_state_in_rtl_return": True,
                "c_shadow_memory_write_is_restored_before_rtl_return": True,
                "residual_symbol_alias_routes_to_dispatcher": True,
            },
        }

    def write_bounded_mux_refill_transition_overlay_sources(
        self,
        contract: dict[str, Any],
        source_dir: pathlib.Path,
        module: str,
        candidate_sv: pathlib.Path,
    ) -> dict[str, Any]:
        """Bind a bounded stream cursor and four complete FIFO snapshots."""
        semantics = contract.get("semantics", {}) or {}
        constants = semantics.get("constants", {}) or {}
        bindings = semantics.get("bindings", {}) or {}
        max_ssps = int(constants.get("max_ssps", 0))
        stream_window_bytes = int(constants.get("stream_window_bytes", 0))
        max_fifo_bytes = int(constants.get("max_fifo_bytes", 0))
        max_se_ports = [str(value) for value in bindings.get("max_se_size_ports", [])]
        stream_ports = [str(value) for value in bindings.get("stream_byte_ports", [])]
        lanes = [dict(value) for value in bindings.get("fifo_lanes", [])]
        if (
            max_ssps != 4
            or stream_window_bytes != 33
            or max_fifo_bytes != 17
            or len(max_se_ports) != max_ssps
            or len(stream_ports) != stream_window_bytes
            or len(lanes) != max_ssps
        ):
            raise RuntimeError("bounded mux refill constants are incomplete")

        ports = [
            port for port in (contract.get("interface", {}) or {}).get("ports", [])
            if isinstance(port, dict)
        ]
        inputs = [port for port in ports if port.get("direction") == "input"]
        outputs = [port for port in ports if port.get("direction") == "output"]
        input_names = {str(port.get("name")) for port in inputs}
        output_names = {str(port.get("name")) for port in outputs}
        expected_inputs = {
            str(bindings.get("mux_word_size_port")),
            str(bindings.get("num_ssps_port")),
            str(bindings.get("post_mux_num_bits_port")),
            *max_se_ports,
            *stream_ports,
        }
        expected_outputs = {
            "domain_valid",
            str(bindings.get("post_mux_num_bits_output_port")),
        }
        scalar_input_keys = (
            "size_port", "fullness_port", "read_ptr_port", "write_ptr_port",
            "max_fullness_port", "byte_ctr_port",
        )
        scalar_output_keys = (
            "size_output_port", "fullness_output_port", "read_ptr_output_port",
            "write_ptr_output_port", "max_fullness_output_port",
            "byte_ctr_output_port",
        )
        for lane in lanes:
            expected_inputs.update(str(lane[key]) for key in scalar_input_keys)
            expected_inputs.update(str(value) for value in lane["data_input_ports"])
            expected_outputs.update(str(lane[key]) for key in scalar_output_keys)
            expected_outputs.update(str(value) for value in lane["data_output_ports"])
        if input_names != expected_inputs or output_names != expected_outputs:
            raise RuntimeError("bounded mux refill ports do not match the frozen interface")

        parameters = self.function_parameters(contract)
        parameter_by_name = {
            str(parameter.get("name")): parameter for parameter in parameters
        }
        config_parameter = str(bindings.get("config_parameter", ""))
        state_parameter = str(bindings.get("state_parameter", ""))
        buffer_parameter = str(bindings.get("buffer_parameter", ""))
        if set(parameter_by_name) != {
            config_parameter, state_parameter, buffer_parameter
        }:
            raise RuntimeError("bounded mux refill requires config/state/byte-buffer parameters")
        if not all(
            parameter_is_pointer(parameter_by_name[name])
            for name in (config_parameter, state_parameter, buffer_parameter)
        ):
            raise RuntimeError("bounded mux refill native parameters must be pointers")

        identifier = re.compile(r"^[A-Za-z_][A-Za-z0-9_]*$")
        all_identifiers = {
            config_parameter, state_parameter, buffer_parameter,
            str(bindings.get("mux_word_size_field")),
            str(bindings.get("num_ssps_field")),
            str(bindings.get("post_mux_num_bits_field")),
            str(bindings.get("max_se_size_field")),
            str(bindings.get("shifter_field")),
            *input_names, *output_names,
        }
        if not all(identifier.fullmatch(value) for value in all_identifiers):
            raise RuntimeError("bounded mux refill bindings contain an invalid identifier")

        parameter_specs = [
            f"{str(parameter.get('type', 'int')).strip()} {parameter.get('name')}"
            for parameter in parameters
        ]
        parameter_names = [str(parameter.get("name")) for parameter in parameters]
        caller_declarations = ", ".join(parameter_specs)
        alias_call = ", ".join(parameter_names)
        function_name = str(contract_function(contract).get("name"))
        original = function_name + "_original"
        mux_field = str(bindings["mux_word_size_field"])
        num_ssps_field = str(bindings["num_ssps_field"])
        post_field = str(bindings["post_mux_num_bits_field"])
        max_se_field = str(bindings["max_se_size_field"])
        shifter_field = str(bindings["shifter_field"])

        abi = source_dir / "dsc_cicd_rtl_abi.h"
        abi.write_text(
            "#ifndef DSC_CICD_RTL_ABI_H\n"
            "#define DSC_CICD_RTL_ABI_H\n"
            "#include <stdint.h>\n"
            f"#define DSC_CICD_MAX_SSPS {max_ssps}\n"
            f"#define DSC_CICD_STREAM_BYTES {stream_window_bytes}\n"
            f"#define DSC_CICD_FIFO_BYTES {max_fifo_bytes}\n"
            "typedef struct {\n"
            "    uint32_t size;\n"
            "    uint32_t fullness;\n"
            "    uint32_t read_ptr;\n"
            "    uint32_t write_ptr;\n"
            "    uint32_t max_fullness;\n"
            "    uint32_t byte_ctr;\n"
            "    uint8_t data[DSC_CICD_FIFO_BYTES];\n"
            "} dsc_cicd_fifo_snapshot_t;\n"
            "#ifdef __cplusplus\nextern \"C\" {\n#endif\n"
            "void dsc_cicd_rtl(uint32_t mux_word_size, uint32_t num_ssps, "
            "uint32_t post_mux_num_bits, "
            "const uint32_t max_se_size[DSC_CICD_MAX_SSPS], "
            "const uint8_t stream[DSC_CICD_STREAM_BYTES], "
            "const dsc_cicd_fifo_snapshot_t input_fifo[DSC_CICD_MAX_SSPS], "
            "uint32_t *domain_valid, uint32_t *post_mux_num_bits_out, "
            "dsc_cicd_fifo_snapshot_t output_fifo[DSC_CICD_MAX_SSPS]);\n"
            "#ifdef __cplusplus\n}\n#endif\n"
            "#endif\n",
            encoding="utf-8",
        )
        header = source_dir / "dsc_cicd_overlay.h"
        header.write_text(
            "#ifndef DSC_CICD_OVERLAY_H\n"
            "#define DSC_CICD_OVERLAY_H\n"
            "#include \"dsc_types.h\"\n"
            f"void dsc_cicd_invoke({caller_declarations});\n"
            "#endif\n",
            encoding="utf-8",
        )
        overlay = source_dir / "dsc_cicd_overlay.c"
        overlay.write_text(
            "#include <stdint.h>\n"
            "#include <stdio.h>\n"
            "#include <stdlib.h>\n"
            "#include <string.h>\n"
            "#include \"dsc_cicd_overlay.h\"\n"
            "#include \"dsc_cicd_rtl_abi.h\"\n"
            f"extern void {original}({caller_declarations});\n"
            "static int dsc_cicd_mode(void) {\n"
            "    const char *value = getenv(\"DSC_CICD_MODE\");\n"
            "    if (value && strcmp(value, \"SHADOW\") == 0) return 1;\n"
            "    if (value && strcmp(value, \"RTL_RETURN\") == 0) return 2;\n"
            "    return 0;\n"
            "}\n"
            + self.overlay_runtime_metrics_source()
            + "static void dsc_cicd_capture_fifo(const fifo_t *source, "
            "dsc_cicd_fifo_snapshot_t *target) {\n"
            "    memset(target, 0, sizeof(*target));\n"
            "    if (!source->data || source->size <= 0 || (source->size & 7) || "
            "source->size / 8 > DSC_CICD_FIFO_BYTES) {\n"
            "        fprintf(stderr, \"unsupported mux FIFO domain: size=%d\\n\", source->size);\n"
            "        exit(2);\n"
            "    }\n"
            "    target->size = (uint32_t)source->size;\n"
            "    target->fullness = (uint32_t)source->fullness;\n"
            "    target->read_ptr = (uint32_t)source->read_ptr;\n"
            "    target->write_ptr = (uint32_t)source->write_ptr;\n"
            "    target->max_fullness = (uint32_t)source->max_fullness;\n"
            "    target->byte_ctr = (uint32_t)source->byte_ctr;\n"
            "    memcpy(target->data, source->data, (size_t)(source->size / 8));\n"
            "}\n"
            "static void dsc_cicd_apply_fifo(fifo_t *target, "
            "const dsc_cicd_fifo_snapshot_t *source) {\n"
            "    target->size = (int)source->size;\n"
            "    target->fullness = (int)source->fullness;\n"
            "    target->read_ptr = (int)source->read_ptr;\n"
            "    target->write_ptr = (int)source->write_ptr;\n"
            "    target->max_fullness = (int)source->max_fullness;\n"
            "    target->byte_ctr = (int)source->byte_ctr;\n"
            "    memcpy(target->data, source->data, (size_t)(source->size / 8));\n"
            "}\n"
            "static int dsc_cicd_fifo_mismatch(const dsc_cicd_fifo_snapshot_t *left, "
            "const dsc_cicd_fifo_snapshot_t *right) {\n"
            "    if (left->size != right->size || left->fullness != right->fullness || "
            "left->read_ptr != right->read_ptr || left->write_ptr != right->write_ptr || "
            "left->max_fullness != right->max_fullness || "
            "left->byte_ctr != right->byte_ctr) return 1;\n"
            "    return memcmp(left->data, right->data, (size_t)(left->size / 8)) != 0;\n"
            "}\n"
            + f"void dsc_cicd_invoke({caller_declarations}) {{\n"
            f"    dsc_state_t dsc_cicd_c_state = *{state_parameter};\n"
            "    dsc_cicd_fifo_snapshot_t dsc_cicd_input[DSC_CICD_MAX_SSPS];\n"
            "    dsc_cicd_fifo_snapshot_t dsc_cicd_c_output[DSC_CICD_MAX_SSPS];\n"
            "    dsc_cicd_fifo_snapshot_t dsc_cicd_rtl_output[DSC_CICD_MAX_SSPS];\n"
            "    uint8_t dsc_cicd_c_data[DSC_CICD_MAX_SSPS][DSC_CICD_FIFO_BYTES] = {{0}};\n"
            "    uint32_t dsc_cicd_max_se_size[DSC_CICD_MAX_SSPS] = {0};\n"
            "    for (int lane = 0; lane < DSC_CICD_MAX_SSPS; ++lane) {\n"
            f"        dsc_cicd_capture_fifo(&{state_parameter}->{shifter_field}[lane], "
            "&dsc_cicd_input[lane]);\n"
            "        memcpy(dsc_cicd_c_data[lane], dsc_cicd_input[lane].data, "
            "DSC_CICD_FIFO_BYTES);\n"
            f"        dsc_cicd_c_state.{shifter_field}[lane].data = dsc_cicd_c_data[lane];\n"
            f"        dsc_cicd_max_se_size[lane] = (uint32_t){state_parameter}->{max_se_field}[lane];\n"
            "    }\n"
            f"    {original}({config_parameter}, &dsc_cicd_c_state, {buffer_parameter});\n"
            "    for (int lane = 0; lane < DSC_CICD_MAX_SSPS; ++lane)\n"
            f"        dsc_cicd_capture_fifo(&dsc_cicd_c_state.{shifter_field}[lane], "
            "&dsc_cicd_c_output[lane]);\n"
            "    int mode = dsc_cicd_mode();\n"
            "    dsc_cicd_note_call(mode);\n"
            "    if (mode == 0) {\n"
            f"        {state_parameter}->{post_field} = dsc_cicd_c_state.{post_field};\n"
            "        for (int lane = 0; lane < DSC_CICD_MAX_SSPS; ++lane)\n"
            f"            dsc_cicd_apply_fifo(&{state_parameter}->{shifter_field}[lane], "
            "&dsc_cicd_c_output[lane]);\n"
            "        return;\n"
            "    }\n"
            "    uint8_t dsc_cicd_stream[DSC_CICD_STREAM_BYTES] = {0};\n"
            f"    int dsc_cicd_base = {state_parameter}->{post_field} >> 3;\n"
            "    for (int index = 0; index < DSC_CICD_STREAM_BYTES; ++index) {\n"
            f"        if (index + 1 < DSC_CICD_STREAM_BYTES || ({state_parameter}->{post_field} & 7))\n"
            f"            dsc_cicd_stream[index] = {buffer_parameter}[dsc_cicd_base + index];\n"
            "    }\n"
            "    uint32_t dsc_cicd_domain_valid = 0;\n"
            "    uint32_t dsc_cicd_rtl_post = 0;\n"
            f"    dsc_cicd_rtl((uint32_t){config_parameter}->{mux_field}, "
            f"(uint32_t){state_parameter}->{num_ssps_field}, "
            f"(uint32_t){state_parameter}->{post_field}, dsc_cicd_max_se_size, "
            "dsc_cicd_stream, dsc_cicd_input, &dsc_cicd_domain_valid, "
            "&dsc_cicd_rtl_post, dsc_cicd_rtl_output);\n"
            "    int dsc_cicd_mismatch = !dsc_cicd_domain_valid || "
            f"dsc_cicd_rtl_post != (uint32_t)dsc_cicd_c_state.{post_field};\n"
            "    for (int lane = 0; lane < DSC_CICD_MAX_SSPS; ++lane)\n"
            "        dsc_cicd_mismatch |= dsc_cicd_fifo_mismatch("
            "&dsc_cicd_c_output[lane], &dsc_cicd_rtl_output[lane]);\n"
            "    if (dsc_cicd_mismatch) {\n"
            "        ++dsc_cicd_mismatches;\n"
            "        fprintf(stderr, \"C/RTL bounded mux refill mismatch: cursor=%d ssps=%d mux=%d\\n\", "
            f"{state_parameter}->{post_field}, {state_parameter}->{num_ssps_field}, "
            f"{config_parameter}->{mux_field});\n"
            "    }\n"
            "    if (mode == 2) {\n"
            f"        {state_parameter}->{post_field} = (int)dsc_cicd_rtl_post;\n"
            "        for (int lane = 0; lane < DSC_CICD_MAX_SSPS; ++lane)\n"
            f"            dsc_cicd_apply_fifo(&{state_parameter}->{shifter_field}[lane], "
            "&dsc_cicd_rtl_output[lane]);\n"
            "        return;\n"
            "    }\n"
            f"    {state_parameter}->{post_field} = dsc_cicd_c_state.{post_field};\n"
            "    for (int lane = 0; lane < DSC_CICD_MAX_SSPS; ++lane)\n"
            f"        dsc_cicd_apply_fifo(&{state_parameter}->{shifter_field}[lane], "
            "&dsc_cicd_c_output[lane]);\n"
            "}\n"
            + f"void {function_name}({caller_declarations}) {{\n"
            f"    dsc_cicd_invoke({alias_call});\n"
            "}\n",
            encoding="utf-8",
        )

        bridge_assignments = [
            f"    dut.{bindings['mux_word_size_port']} = mux_word_size;",
            f"    dut.{bindings['num_ssps_port']} = num_ssps;",
            f"    dut.{bindings['post_mux_num_bits_port']} = post_mux_num_bits;",
        ]
        bridge_outputs = [
            "    *domain_valid = static_cast<uint32_t>(dut.domain_valid);",
            f"    *post_mux_num_bits_out = static_cast<uint32_t>(dut."
            f"{bindings['post_mux_num_bits_output_port']});",
        ]
        for index, port in enumerate(max_se_ports):
            bridge_assignments.append(f"    dut.{port} = max_se_size[{index}];")
        for index, port in enumerate(stream_ports):
            bridge_assignments.append(f"    dut.{port} = stream[{index}];")
        field_pairs = (
            ("size_port", "size", "size_output_port"),
            ("fullness_port", "fullness", "fullness_output_port"),
            ("read_ptr_port", "read_ptr", "read_ptr_output_port"),
            ("write_ptr_port", "write_ptr", "write_ptr_output_port"),
            ("max_fullness_port", "max_fullness", "max_fullness_output_port"),
            ("byte_ctr_port", "byte_ctr", "byte_ctr_output_port"),
        )
        for lane_index, lane in enumerate(lanes):
            for input_key, field, output_key in field_pairs:
                bridge_assignments.append(
                    f"    dut.{lane[input_key]} = input_fifo[{lane_index}].{field};"
                )
                bridge_outputs.append(
                    f"    output_fifo[{lane_index}].{field} = "
                    f"static_cast<uint32_t>(dut.{lane[output_key]});"
                )
            for byte_index, (input_port, output_port) in enumerate(zip(
                lane["data_input_ports"], lane["data_output_ports"]
            )):
                bridge_assignments.append(
                    f"    dut.{input_port} = input_fifo[{lane_index}].data[{byte_index}];"
                )
                bridge_outputs.append(
                    f"    output_fifo[{lane_index}].data[{byte_index}] = "
                    f"static_cast<uint8_t>(dut.{output_port});"
                )
        bridge = source_dir / "rtl_bridge.cpp"
        bridge.write_text(
            "#include <cstdint>\n"
            "#include \"verilated.h\"\n"
            "#include \"dsc_cicd_rtl_abi.h\"\n"
            f"#include \"V{safe_identifier(module)}.h\"\n"
            "double sc_time_stamp() { return 0.0; }\n"
            "extern \"C\" void dsc_cicd_rtl(uint32_t mux_word_size, "
            "uint32_t num_ssps, uint32_t post_mux_num_bits, "
            "const uint32_t max_se_size[DSC_CICD_MAX_SSPS], "
            "const uint8_t stream[DSC_CICD_STREAM_BYTES], "
            "const dsc_cicd_fifo_snapshot_t input_fifo[DSC_CICD_MAX_SSPS], "
            "uint32_t *domain_valid, uint32_t *post_mux_num_bits_out, "
            "dsc_cicd_fifo_snapshot_t output_fifo[DSC_CICD_MAX_SSPS]) {\n"
            f"    static V{safe_identifier(module)} dut;\n"
            + "\n".join(bridge_assignments)
            + "\n    dut.eval();\n"
            + "\n".join(bridge_outputs)
            + "\n}\n",
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
        rtl_bindings = [
            f"{config_parameter}->{mux_field}",
            f"{state_parameter}->{num_ssps_field}",
            f"{state_parameter}->{post_field}",
            *[f"{state_parameter}->{max_se_field}[{index}]" for index in range(max_ssps)],
            *[f"{buffer_parameter}[base+{index}]" for index in range(stream_window_bytes)],
        ]
        for lane_index in range(max_ssps):
            rtl_bindings.extend(
                f"{state_parameter}->{shifter_field}[{lane_index}].{field}"
                for field in (
                    "size", "fullness", "read_ptr", "write_ptr",
                    "max_fullness", "byte_ctr",
                )
            )
            rtl_bindings.extend(
                f"{state_parameter}->{shifter_field}[{lane_index}].data[{index}]"
                for index in range(max_fifo_bytes)
            )
        return {
            "header": header,
            "abi": abi,
            "overlay": overlay,
            "bridge": bridge,
            "main": main,
            "candidate": candidate_sv,
            "composition": {
                "status": "PASS",
                "adapter_kind": "explicit_bounded_mux_refill_transition",
                "caller_parameter_count": len(parameters),
                "rtl_input_count": len(inputs),
                "frozen_input_ports": [str(port.get("name")) for port in inputs],
                "rtl_bindings": rtl_bindings,
                "state_outputs": [str(port.get("name")) for port in outputs],
                "rtl_return_controls_cursor_and_complete_fifo_snapshots": True,
                "c_oracle_uses_private_fifo_memory": True,
                "residual_symbol_alias_routes_to_dispatcher": True,
            },
        }

    def write_bounded_flatness_state_transition_overlay_sources(
        self,
        contract: dict[str, Any],
        source_dir: pathlib.Path,
        module: str,
        candidate_sv: pathlib.Path,
    ) -> dict[str, Any]:
        """Bind accepted flatness RTL callees plus an explicit scalar next state."""
        semantics = contract.get("semantics", {}) or {}
        constants = semantics.get("constants", {}) or {}
        bindings = semantics.get("bindings", {}) or {}
        calls = int(constants.get("callee_calls", 0))
        components = int(constants.get("component_count", 0))
        taps_per_component = int(constants.get("taps_per_component", 0))
        padding_left = int(constants.get("padding_left", 0))
        last_range_index = int(constants.get("last_range_index", -1))
        if (calls, components, taps_per_component, padding_left, last_range_index) != (
            4, 4, 7, 5, 14
        ):
            raise RuntimeError("bounded flatness constants are incomplete")
        scalar_ports = {
            str(key): str(value)
            for key, value in (bindings.get("scalar_input_ports", {}) or {}).items()
        }
        config_ports = {
            str(key): str(value)
            for key, value in (bindings.get("config_ports", {}) or {}).items()
        }
        state_ports = {
            str(key): str(value)
            for key, value in (bindings.get("state_input_ports", {}) or {}).items()
        }
        state_output_ports = {
            str(key): str(value)
            for key, value in (bindings.get("state_output_ports", {}) or {}).items()
        }
        tap_ports = [str(value) for value in bindings.get("tap_ports", [])]
        ports = [
            port for port in (contract.get("interface", {}) or {}).get("ports", [])
            if isinstance(port, dict)
        ]
        inputs = [port for port in ports if port.get("direction") == "input"]
        outputs = [port for port in ports if port.get("direction") == "output"]
        scalar_input_names = {
            *scalar_ports.values(), *config_ports.values(), *state_ports.values()
        }
        if (
            {str(port.get("name")) for port in inputs}
            != {*scalar_input_names, *tap_ports}
            or {str(port.get("name")) for port in outputs}
            != set(state_output_ports.values())
            or len(tap_ports) != calls * components * taps_per_component
        ):
            raise RuntimeError("bounded flatness ports do not match the frozen interface")

        parameters = self.function_parameters(contract)
        parameter_by_name = {
            str(parameter.get("name")): parameter for parameter in parameters
        }
        config_parameter = str(bindings.get("config_parameter", ""))
        state_parameter = str(bindings.get("state_parameter", ""))
        required_parameters = {config_parameter, state_parameter, *scalar_ports}
        if set(parameter_by_name) != required_parameters:
            raise RuntimeError("bounded flatness native parameter bindings are incomplete")
        if not parameter_is_pointer(parameter_by_name[config_parameter]):
            raise RuntimeError("bounded flatness config parameter must be a pointer")
        if not parameter_is_pointer(parameter_by_name[state_parameter]):
            raise RuntimeError("bounded flatness state parameter must be a pointer")
        identifier = re.compile(r"^[A-Za-z_][A-Za-z0-9_]*$")
        all_identifiers = {
            config_parameter, state_parameter, *scalar_ports, *config_ports,
            *state_output_ports, *scalar_input_names,
            *state_output_ports.values(), *tap_ports,
        }
        if not all(identifier.fullmatch(value) for value in all_identifiers):
            raise RuntimeError("bounded flatness bindings contain an invalid identifier")
        field_expression = re.compile(r"^[A-Za-z_][A-Za-z0-9_]*(?:\[[0-9]+\])?$")
        if not all(field_expression.fullmatch(value) for value in state_ports):
            raise RuntimeError("bounded flatness state field binding is invalid")

        parameter_specs = [
            f"{str(parameter.get('type', 'int')).strip()} {parameter.get('name')}"
            for parameter in parameters
        ]
        parameter_names = [str(parameter.get("name")) for parameter in parameters]
        caller_declarations = ", ".join(parameter_specs)
        alias_call = ", ".join(parameter_names)
        c_call = ", ".join(
            "&dsc_cicd_c_state" if name == state_parameter else name
            for name in parameter_names
        )
        function_name = str(contract_function(contract).get("name"))
        original = function_name + "_original"

        scalar_port_order = [
            str(port["name"]) for port in inputs if str(port["name"]) not in set(tap_ports)
        ]
        output_port_order = [str(port["name"]) for port in outputs]
        abi = source_dir / "dsc_cicd_rtl_abi.h"
        abi.write_text(
            "#ifndef DSC_CICD_RTL_ABI_H\n"
            "#define DSC_CICD_RTL_ABI_H\n"
            "#include <stdint.h>\n"
            f"#define DSC_CICD_FLAT_CALLS {calls}\n"
            f"#define DSC_CICD_FLAT_COMPONENTS {components}\n"
            f"#define DSC_CICD_FLAT_TAPS {taps_per_component}\n"
            "typedef struct {\n"
            + "".join(f"    int32_t {port};\n" for port in scalar_port_order)
            + "    uint16_t taps[DSC_CICD_FLAT_CALLS][DSC_CICD_FLAT_COMPONENTS]"
            "[DSC_CICD_FLAT_TAPS];\n"
            "} dsc_cicd_flatness_input_t;\n"
            "typedef struct {\n"
            + "".join(f"    int32_t {port};\n" for port in output_port_order)
            + "} dsc_cicd_flatness_output_t;\n"
            "#ifdef __cplusplus\nextern \"C\" {\n#endif\n"
            "void dsc_cicd_rtl(const dsc_cicd_flatness_input_t *input, "
            "dsc_cicd_flatness_output_t *output);\n"
            "#ifdef __cplusplus\n}\n#endif\n"
            "#endif\n",
            encoding="utf-8",
        )
        header = source_dir / "dsc_cicd_overlay.h"
        header.write_text(
            "#ifndef DSC_CICD_OVERLAY_H\n"
            "#define DSC_CICD_OVERLAY_H\n"
            "#include \"dsc_types.h\"\n"
            f"void dsc_cicd_invoke({caller_declarations});\n"
            "#endif\n",
            encoding="utf-8",
        )

        scalar_assignments = []
        rtl_bindings = []
        for parameter, port in scalar_ports.items():
            scalar_assignments.append(f"    dsc_cicd_input.{port} = {parameter};")
            rtl_bindings.append(parameter)
        for field, port in config_ports.items():
            expression = (
                f"{config_parameter}->rc_range_parameters[{last_range_index}].range_max_qp"
                if field == "last_range_max_qp"
                else f"{config_parameter}->{field}"
            )
            scalar_assignments.append(f"    dsc_cicd_input.{port} = {expression};")
            rtl_bindings.append(expression)
        for field, port in state_ports.items():
            if field.startswith("cpntBitDepth["):
                expression = f"{state_parameter}->{field}"
            else:
                expression = f"{state_parameter}->{field}"
            scalar_assignments.append(f"    dsc_cicd_input.{port} = {expression};")
            rtl_bindings.append(expression)
        hpos_parameter = str(bindings["horizontal_position_parameter"])
        qp_parameter = str(bindings["qp_parameter"])
        tap_index = 0
        for call in range(calls):
            for component in range(components):
                for tap_index_in_call in range(taps_per_component):
                    expression = (
                        f"{state_parameter}->origLine[{component}]"
                        f"[{padding_left}+{hpos_parameter}"
                        f"+({call + 1}*{state_parameter}->pixelsInGroup)+{tap_index_in_call}]"
                    )
                    rtl_bindings.append(expression)
                    tap_index += 1
        c_expected = {
            port: f"dsc_cicd_c_state.{field}"
            for field, port in state_output_ports.items()
        }
        mismatch_expression = " || ".join(
            f"dsc_cicd_rtl_output.{port} != {c_expected[port]}"
            for port in output_port_order
        )
        apply_c = "".join(
            f"        {state_parameter}->{field} = dsc_cicd_c_state.{field};\n"
            for field in state_output_ports
        )
        apply_rtl = "".join(
            f"        {state_parameter}->{field} = dsc_cicd_rtl_output.{port};\n"
            for field, port in state_output_ports.items()
        )
        overlay = source_dir / "dsc_cicd_overlay.c"
        overlay.write_text(
            "#include <stdint.h>\n"
            "#include <stdio.h>\n"
            "#include <stdlib.h>\n"
            "#include <string.h>\n"
            "#include \"dsc_cicd_overlay.h\"\n"
            "#include \"dsc_cicd_rtl_abi.h\"\n"
            f"extern void {original}({caller_declarations});\n"
            "static int dsc_cicd_mode(void) {\n"
            "    const char *value = getenv(\"DSC_CICD_MODE\");\n"
            "    if (value && strcmp(value, \"SHADOW\") == 0) return 1;\n"
            "    if (value && strcmp(value, \"RTL_RETURN\") == 0) return 2;\n"
            "    return 0;\n"
            "}\n"
            + self.overlay_runtime_metrics_source()
            + f"void dsc_cicd_invoke({caller_declarations}) {{\n"
            f"    dsc_state_t dsc_cicd_c_state = *{state_parameter};\n"
            f"    {original}({c_call});\n"
            "    int mode = dsc_cicd_mode();\n"
            "    dsc_cicd_note_call(mode);\n"
            "    if (mode == 0) {\n"
            + apply_c
            + "        return;\n"
            "    }\n"
            "    dsc_cicd_flatness_input_t dsc_cicd_input;\n"
            "    dsc_cicd_flatness_output_t dsc_cicd_rtl_output;\n"
            "    memset(&dsc_cicd_input, 0, sizeof(dsc_cicd_input));\n"
            "    memset(&dsc_cicd_rtl_output, 0, sizeof(dsc_cicd_rtl_output));\n"
            + "\n".join(scalar_assignments)
            + "\n"
            f"    int dsc_cicd_scan = ({state_parameter}->isEncoder != 0) && "
            f"(({state_parameter}->groupCount & 3) == 3) && "
            f"({qp_parameter} >= {config_parameter}->flatness_min_qp) && "
            f"({qp_parameter} <= {config_parameter}->flatness_max_qp);\n"
            "    if (dsc_cicd_scan) {\n"
            "        for (int call = 0; call < DSC_CICD_FLAT_CALLS; ++call) {\n"
            f"            int flat_h = {hpos_parameter} + (call + 1) * "
            f"{state_parameter}->pixelsInGroup;\n"
            f"            if (flat_h >= 0 && flat_h + 1 < {state_parameter}->sliceWidth) {{\n"
            "                for (int component = 0; component < "
            f"{state_parameter}->numComponents; ++component) {{\n"
            "                    for (int tap = 0; tap < DSC_CICD_FLAT_TAPS; ++tap)\n"
            f"                        dsc_cicd_input.taps[call][component][tap] = "
            f"(uint16_t){state_parameter}->origLine[component]"
            f"[{padding_left} + flat_h + tap];\n"
            "                }\n"
            "            }\n"
            "        }\n"
            "    }\n"
            "    dsc_cicd_rtl(&dsc_cicd_input, &dsc_cicd_rtl_output);\n"
            f"    if ({mismatch_expression}) {{\n"
            "        ++dsc_cicd_mismatches;\n"
            "        fprintf(stderr, \"C/RTL bounded flatness mismatch: h=%d qp=%d group=%d encoder=%d\\n\", "
            f"{hpos_parameter}, {qp_parameter}, {state_parameter}->groupCount, "
            f"{state_parameter}->isEncoder);\n"
            "    }\n"
            "    if (mode == 2) {\n"
            + apply_rtl
            + "        return;\n"
            "    }\n"
            + apply_c
            + "}\n"
            + f"void {function_name}({caller_declarations}) {{\n"
            f"    dsc_cicd_invoke({alias_call});\n"
            "}\n",
            encoding="utf-8",
        )

        bridge_assignments = [
            f"    dut.{port} = static_cast<uint32_t>(input->{port});"
            for port in scalar_port_order
        ]
        tap_index = 0
        for call in range(calls):
            for component in range(components):
                for tap_index_in_call in range(taps_per_component):
                    bridge_assignments.append(
                        f"    dut.{tap_ports[tap_index]} = "
                        f"input->taps[{call}][{component}][{tap_index_in_call}];"
                    )
                    tap_index += 1
        bridge_outputs = [
            f"    output->{port} = static_cast<int32_t>(dut.{port});"
            for port in output_port_order
        ]
        bridge = source_dir / "rtl_bridge.cpp"
        bridge.write_text(
            "#include <cstdint>\n"
            "#include \"verilated.h\"\n"
            "#include \"dsc_cicd_rtl_abi.h\"\n"
            f"#include \"V{safe_identifier(module)}.h\"\n"
            "double sc_time_stamp() { return 0.0; }\n"
            "extern \"C\" void dsc_cicd_rtl("
            "const dsc_cicd_flatness_input_t *input, "
            "dsc_cicd_flatness_output_t *output) {\n"
            f"    static V{safe_identifier(module)} dut;\n"
            + "\n".join(bridge_assignments)
            + "\n    dut.eval();\n"
            + "\n".join(bridge_outputs)
            + "\n}\n",
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
        return {
            "header": header,
            "abi": abi,
            "overlay": overlay,
            "bridge": bridge,
            "main": main,
            "candidate": candidate_sv,
            "composition": {
                "status": "PASS",
                "adapter_kind": "accepted_flatness_rtl_plus_bounded_scalar_state",
                "caller_parameter_count": len(parameters),
                "rtl_input_count": len(inputs),
                "frozen_input_ports": [str(port.get("name")) for port in inputs],
                "rtl_bindings": rtl_bindings,
                "state_outputs": output_port_order,
                "rtl_return_controls_all_written_flatness_state": True,
                "accepted_rtl_dependencies_embedded": [
                    str(item.get("contract_id")) for item in contract.get("dependencies", [])
                ],
                "residual_symbol_alias_routes_to_dispatcher": True,
            },
        }

    def write_bounded_line_write_transition_overlay_sources(
        self,
        contract: dict[str, Any],
        source_dir: pathlib.Path,
        module: str,
        candidate_sv: pathlib.Path,
    ) -> dict[str, Any]:
        """Bind a bounded ICH-to-line scatter as explicit write sidebands."""
        semantics = contract.get("semantics", {}) or {}
        constants = semantics.get("constants", {}) or {}
        bindings = semantics.get("bindings", {}) or {}
        max_pixels = int(constants.get("max_pixels", 0))
        components = int(constants.get("component_count", 0))
        if (max_pixels, components, int(constants.get("padding_left", 0))) != (6, 4, 5):
            raise RuntimeError("bounded line write constants are incomplete")
        pixel_ports = [[str(value) for value in row] for row in bindings.get("pixel_ports", [])]
        index_ports = [str(value) for value in bindings.get("write_index_ports", [])]
        enable_ports = [[str(value) for value in row] for row in bindings.get("write_enable_ports", [])]
        value_ports = [[str(value) for value in row] for row in bindings.get("write_value_ports", [])]
        if not all(len(rows) == max_pixels for rows in (pixel_ports, enable_ports, value_ports)):
            raise RuntimeError("bounded line write row extent is incomplete")
        if any(len(row) != components for rows in (pixel_ports, enable_ports, value_ports) for row in rows):
            raise RuntimeError("bounded line write component extent is incomplete")
        if len(index_ports) != max_pixels:
            raise RuntimeError("bounded line write index extent is incomplete")

        ports = [
            port for port in (contract.get("interface", {}) or {}).get("ports", [])
            if isinstance(port, dict)
        ]
        inputs = [port for port in ports if port.get("direction") == "input"]
        outputs = [port for port in ports if port.get("direction") == "output"]
        base_input_ports = [
            str(bindings[key]) for key in (
                "hpos_port", "pixels_in_group_port", "ich_indices_port",
                "ich_selected_port", "num_components_port",
            )
        ]
        if {str(port["name"]) for port in inputs} != {
            *base_input_ports, *[value for row in pixel_ports for value in row]
        } or {str(port["name"]) for port in outputs} != {
            *index_ports,
            *[value for row in enable_ports for value in row],
            *[value for row in value_ports for value in row],
        }:
            raise RuntimeError("bounded line write ports do not match the frozen interface")

        parameters = self.function_parameters(contract)
        parameter_by_name = {str(item.get("name")): item for item in parameters}
        config_parameter = str(bindings.get("config_parameter", ""))
        state_parameter = str(bindings.get("state_parameter", ""))
        line_parameter = str(bindings.get("line_parameter", ""))
        if set(parameter_by_name) != {config_parameter, state_parameter, line_parameter}:
            raise RuntimeError("bounded line write requires config/state/line parameters")
        if not all(parameter_is_pointer(parameter_by_name[name]) for name in parameter_by_name):
            raise RuntimeError("bounded line write native parameters must be pointers")
        identifier = re.compile(r"^[A-Za-z_][A-Za-z0-9_]*$")
        if not all(identifier.fullmatch(value) for value in {
            config_parameter, state_parameter, line_parameter,
            *base_input_ports, *index_ports,
            *[value for row in pixel_ports for value in row],
            *[value for row in enable_ports for value in row],
            *[value for row in value_ports for value in row],
        }):
            raise RuntimeError("bounded line write bindings contain an invalid identifier")

        parameter_specs = [
            f"{str(item.get('type', 'int')).strip()} {item.get('name')}"
            for item in parameters
        ]
        parameter_names = [str(item.get("name")) for item in parameters]
        caller_declarations = ", ".join(parameter_specs)
        alias_call = ", ".join(parameter_names)
        function_name = str(contract_function(contract).get("name"))
        original = function_name + "_original"
        hpos_field = str(bindings["hpos_field"])
        pixels_in_group_field = str(bindings["pixels_in_group_field"])
        ich_indices_field = str(bindings["ich_indices_field"])
        ich_selected_field = str(bindings["ich_selected_field"])
        num_components_field = str(bindings["num_components_field"])
        ich_pixels_field = str(bindings["ich_pixels_field"])

        abi = source_dir / "dsc_cicd_rtl_abi.h"
        abi.write_text(
            "#ifndef DSC_CICD_RTL_ABI_H\n"
            "#define DSC_CICD_RTL_ABI_H\n"
            "#include <stdint.h>\n"
            f"#define DSC_CICD_LINE_PIXELS {max_pixels}\n"
            f"#define DSC_CICD_LINE_COMPONENTS {components}\n"
            "typedef struct {\n"
            "    int32_t hpos;\n    int32_t pixels_in_group;\n"
            "    int32_t ich_indices;\n    int32_t ich_selected;\n"
            "    int32_t num_components;\n"
            "    uint32_t pixels[DSC_CICD_LINE_PIXELS][DSC_CICD_LINE_COMPONENTS];\n"
            "} dsc_cicd_line_input_t;\n"
            "typedef struct {\n"
            "    int32_t index[DSC_CICD_LINE_PIXELS];\n"
            "    uint8_t enable[DSC_CICD_LINE_PIXELS][DSC_CICD_LINE_COMPONENTS];\n"
            "    int32_t value[DSC_CICD_LINE_PIXELS][DSC_CICD_LINE_COMPONENTS];\n"
            "} dsc_cicd_line_output_t;\n"
            "#ifdef __cplusplus\nextern \"C\" {\n#endif\n"
            "void dsc_cicd_rtl(const dsc_cicd_line_input_t *input, "
            "dsc_cicd_line_output_t *output);\n"
            "#ifdef __cplusplus\n}\n#endif\n"
            "#endif\n",
            encoding="utf-8",
        )
        header = source_dir / "dsc_cicd_overlay.h"
        header.write_text(
            "#ifndef DSC_CICD_OVERLAY_H\n#define DSC_CICD_OVERLAY_H\n"
            "#include \"dsc_types.h\"\n"
            f"void dsc_cicd_invoke({caller_declarations});\n#endif\n",
            encoding="utf-8",
        )
        overlay = source_dir / "dsc_cicd_overlay.c"
        overlay.write_text(
            "#include <stdint.h>\n#include <stdio.h>\n#include <stdlib.h>\n"
            "#include <string.h>\n#include \"dsc_cicd_overlay.h\"\n"
            "#include \"dsc_cicd_rtl_abi.h\"\n"
            f"extern void {original}({caller_declarations});\n"
            "static int dsc_cicd_mode(void) {\n"
            "    const char *value = getenv(\"DSC_CICD_MODE\");\n"
            "    if (value && strcmp(value, \"SHADOW\") == 0) return 1;\n"
            "    if (value && strcmp(value, \"RTL_RETURN\") == 0) return 2;\n"
            "    return 0;\n}\n"
            + self.overlay_runtime_metrics_source()
            + f"void dsc_cicd_invoke({caller_declarations}) {{\n"
            "    int dsc_cicd_index[DSC_CICD_LINE_PIXELS] = {0};\n"
            "    uint8_t dsc_cicd_enable[DSC_CICD_LINE_PIXELS][DSC_CICD_LINE_COMPONENTS] = {{0}};\n"
            "    int dsc_cicd_prior[DSC_CICD_LINE_PIXELS][DSC_CICD_LINE_COMPONENTS] = {{0}};\n"
            "    int dsc_cicd_c_value[DSC_CICD_LINE_PIXELS][DSC_CICD_LINE_COMPONENTS] = {{0}};\n"
            f"    int dsc_cicd_start = {state_parameter}->{hpos_field} - "
            f"{state_parameter}->{pixels_in_group_field} + 1 + 5;\n"
            "    for (int pixel = 0; pixel < DSC_CICD_LINE_PIXELS; ++pixel) {\n"
            "        dsc_cicd_index[pixel] = dsc_cicd_start + pixel;\n"
            "        for (int component = 0; component < DSC_CICD_LINE_COMPONENTS; ++component) {\n"
            f"            dsc_cicd_enable[pixel][component] = ({state_parameter}->{ich_selected_field} != 0) && "
            f"(pixel < {state_parameter}->{ich_indices_field}) && "
            f"(component < {state_parameter}->{num_components_field});\n"
            "            if (dsc_cicd_enable[pixel][component])\n"
            f"                dsc_cicd_prior[pixel][component] = {line_parameter}[component]"
            "[dsc_cicd_index[pixel]];\n"
            "        }\n    }\n"
            f"    {original}({config_parameter}, {state_parameter}, {line_parameter});\n"
            "    for (int pixel = 0; pixel < DSC_CICD_LINE_PIXELS; ++pixel)\n"
            "        for (int component = 0; component < DSC_CICD_LINE_COMPONENTS; ++component)\n"
            "            if (dsc_cicd_enable[pixel][component]) {\n"
            f"                dsc_cicd_c_value[pixel][component] = {line_parameter}[component]"
            "[dsc_cicd_index[pixel]];\n"
            f"                {line_parameter}[component][dsc_cicd_index[pixel]] = "
            "dsc_cicd_prior[pixel][component];\n"
            "            }\n"
            "    int mode = dsc_cicd_mode();\n    dsc_cicd_note_call(mode);\n"
            "    if (mode == 0) {\n"
            "        for (int pixel = 0; pixel < DSC_CICD_LINE_PIXELS; ++pixel)\n"
            "            for (int component = 0; component < DSC_CICD_LINE_COMPONENTS; ++component)\n"
            "                if (dsc_cicd_enable[pixel][component])\n"
            f"                    {line_parameter}[component][dsc_cicd_index[pixel]] = "
            "dsc_cicd_c_value[pixel][component];\n"
            "        return;\n    }\n"
            "    dsc_cicd_line_input_t dsc_cicd_input;\n"
            "    dsc_cicd_line_output_t dsc_cicd_rtl_output;\n"
            "    memset(&dsc_cicd_input, 0, sizeof(dsc_cicd_input));\n"
            "    memset(&dsc_cicd_rtl_output, 0, sizeof(dsc_cicd_rtl_output));\n"
            f"    dsc_cicd_input.hpos = {state_parameter}->{hpos_field};\n"
            f"    dsc_cicd_input.pixels_in_group = {state_parameter}->{pixels_in_group_field};\n"
            f"    dsc_cicd_input.ich_indices = {state_parameter}->{ich_indices_field};\n"
            f"    dsc_cicd_input.ich_selected = {state_parameter}->{ich_selected_field};\n"
            f"    dsc_cicd_input.num_components = {state_parameter}->{num_components_field};\n"
            "    for (int pixel = 0; pixel < DSC_CICD_LINE_PIXELS; ++pixel)\n"
            "        for (int component = 0; component < DSC_CICD_LINE_COMPONENTS; ++component)\n"
            f"            dsc_cicd_input.pixels[pixel][component] = {state_parameter}->"
            f"{ich_pixels_field}[pixel][component];\n"
            "    dsc_cicd_rtl(&dsc_cicd_input, &dsc_cicd_rtl_output);\n"
            "    int dsc_cicd_mismatch = 0;\n"
            "    for (int pixel = 0; pixel < DSC_CICD_LINE_PIXELS; ++pixel) {\n"
            "        dsc_cicd_mismatch |= dsc_cicd_rtl_output.index[pixel] != dsc_cicd_index[pixel];\n"
            "        for (int component = 0; component < DSC_CICD_LINE_COMPONENTS; ++component)\n"
            "            dsc_cicd_mismatch |= "
            "dsc_cicd_rtl_output.enable[pixel][component] != dsc_cicd_enable[pixel][component] || "
            "dsc_cicd_rtl_output.value[pixel][component] != dsc_cicd_c_value[pixel][component];\n"
            "    }\n"
            "    if (dsc_cicd_mismatch) {\n        ++dsc_cicd_mismatches;\n"
            "        fprintf(stderr, \"C/RTL bounded line write mismatch\\n\");\n    }\n"
            "    if (mode == 2) {\n"
            "        for (int pixel = 0; pixel < DSC_CICD_LINE_PIXELS; ++pixel)\n"
            "            for (int component = 0; component < DSC_CICD_LINE_COMPONENTS; ++component)\n"
            "                if (dsc_cicd_rtl_output.enable[pixel][component])\n"
            f"                    {line_parameter}[component][dsc_cicd_rtl_output.index[pixel]] = "
            "dsc_cicd_rtl_output.value[pixel][component];\n"
            "        return;\n    }\n"
            "    for (int pixel = 0; pixel < DSC_CICD_LINE_PIXELS; ++pixel)\n"
            "        for (int component = 0; component < DSC_CICD_LINE_COMPONENTS; ++component)\n"
            "            if (dsc_cicd_enable[pixel][component])\n"
            f"                {line_parameter}[component][dsc_cicd_index[pixel]] = "
            "dsc_cicd_c_value[pixel][component];\n"
            "}\n"
            + f"void {function_name}({caller_declarations}) {{\n"
            f"    dsc_cicd_invoke({alias_call});\n}}\n",
            encoding="utf-8",
        )

        bridge_assignments = [
            f"    dut.{bindings['hpos_port']} = static_cast<uint32_t>(input->hpos);",
            f"    dut.{bindings['pixels_in_group_port']} = static_cast<uint32_t>(input->pixels_in_group);",
            f"    dut.{bindings['ich_indices_port']} = static_cast<uint32_t>(input->ich_indices);",
            f"    dut.{bindings['ich_selected_port']} = static_cast<uint32_t>(input->ich_selected);",
            f"    dut.{bindings['num_components_port']} = static_cast<uint32_t>(input->num_components);",
        ]
        bridge_outputs = []
        for pixel in range(max_pixels):
            bridge_outputs.append(
                f"    output->index[{pixel}] = static_cast<int32_t>(dut.{index_ports[pixel]});"
            )
            for component in range(components):
                bridge_assignments.append(
                    f"    dut.{pixel_ports[pixel][component]} = input->pixels[{pixel}][{component}];"
                )
                bridge_outputs.extend([
                    f"    output->enable[{pixel}][{component}] = "
                    f"static_cast<uint8_t>(dut.{enable_ports[pixel][component]});",
                    f"    output->value[{pixel}][{component}] = "
                    f"static_cast<int32_t>(dut.{value_ports[pixel][component]});",
                ])
        bridge = source_dir / "rtl_bridge.cpp"
        bridge.write_text(
            "#include <cstdint>\n#include \"verilated.h\"\n"
            "#include \"dsc_cicd_rtl_abi.h\"\n"
            f"#include \"V{safe_identifier(module)}.h\"\n"
            "double sc_time_stamp() { return 0.0; }\n"
            "extern \"C\" void dsc_cicd_rtl(const dsc_cicd_line_input_t *input, "
            "dsc_cicd_line_output_t *output) {\n"
            f"    static V{safe_identifier(module)} dut;\n"
            + "\n".join(bridge_assignments)
            + "\n    dut.eval();\n"
            + "\n".join(bridge_outputs)
            + "\n}\n",
            encoding="utf-8",
        )
        main = source_dir / "dsc_cicd_main.c"
        main.write_text(
            "#include <stdio.h>\nextern int dsc_cicd_original_main(int, char **);\n"
            "int main(int argc, char **argv) { return dsc_cicd_original_main(argc, argv); }\n",
            encoding="utf-8",
        )
        rtl_bindings = [
            f"{state_parameter}->{hpos_field}",
            f"{state_parameter}->{pixels_in_group_field}",
            f"{state_parameter}->{ich_indices_field}",
            f"{state_parameter}->{ich_selected_field}",
            f"{state_parameter}->{num_components_field}",
            *[
                f"{state_parameter}->{ich_pixels_field}[{pixel}][{component}]"
                for pixel in range(max_pixels) for component in range(components)
            ],
        ]
        return {
            "header": header,
            "abi": abi,
            "overlay": overlay,
            "bridge": bridge,
            "main": main,
            "candidate": candidate_sv,
            "composition": {
                "status": "PASS",
                "adapter_kind": "explicit_bounded_line_write_transition",
                "caller_parameter_count": len(parameters),
                "rtl_input_count": len(inputs),
                "frozen_input_ports": [str(port.get("name")) for port in inputs],
                "rtl_bindings": rtl_bindings,
                "state_outputs": [str(port.get("name")) for port in outputs],
                "rtl_return_controls_all_reconstructed_line_writes": True,
                "c_shadow_line_writes_restored_before_rtl_return": True,
                "residual_symbol_alias_routes_to_dispatcher": True,
            },
        }

    def write_bounded_history_update_transition_overlay_sources(
        self,
        contract: dict[str, Any],
        source_dir: pathlib.Path,
        module: str,
        candidate_sv: pathlib.Path,
    ) -> dict[str, Any]:
        """Bind a complete bounded ICH memory snapshot to Verilated RTL."""
        semantics = contract.get("semantics", {}) or {}
        constants = semantics.get("constants", {}) or {}
        bindings = semantics.get("bindings", {}) or {}
        entries = int(constants.get("ich_entries", 0))
        components = int(constants.get("component_count", 0))
        if (entries, components, int(constants.get("reserved_nonfirst", 0))) != (
            32, 4, 25
        ):
            raise RuntimeError("bounded history update constants are incomplete")
        scalar_ports = {
            str(key): str(value)
            for key, value in (bindings.get("scalar_ports", {}) or {}).items()
        }
        recon_ports = [str(value) for value in bindings.get("recon_ports", [])]
        valid_inputs = [
            str(value) for value in bindings.get("valid_input_ports", [])
        ]
        pixel_inputs = [
            [str(value) for value in row]
            for row in bindings.get("pixel_input_ports", [])
        ]
        valid_outputs = [
            str(value) for value in bindings.get("valid_output_ports", [])
        ]
        pixel_outputs = [
            [str(value) for value in row]
            for row in bindings.get("pixel_output_ports", [])
        ]
        if (
            set(scalar_ports) != {
                "cfg_native_420", "hPos", "vPos", "numComponents",
                "isEncoder", "ichSelected", "prevIchSelected",
            }
            or len(recon_ports) != components
            or len(valid_inputs) != entries
            or len(valid_outputs) != entries
            or len(pixel_inputs) != components
            or len(pixel_outputs) != components
            or any(len(row) != entries for row in pixel_inputs)
            or any(len(row) != entries for row in pixel_outputs)
        ):
            raise RuntimeError("bounded history update bindings are incomplete")

        ports = [
            port for port in (contract.get("interface", {}) or {}).get("ports", [])
            if isinstance(port, dict)
        ]
        inputs = [port for port in ports if port.get("direction") == "input"]
        outputs = [port for port in ports if port.get("direction") == "output"]
        expected_inputs = {
            *scalar_ports.values(), *recon_ports, *valid_inputs,
            *[value for row in pixel_inputs for value in row],
        }
        expected_outputs = {
            *valid_outputs, *[value for row in pixel_outputs for value in row],
        }
        if (
            {str(port.get("name")) for port in inputs} != expected_inputs
            or {str(port.get("name")) for port in outputs} != expected_outputs
        ):
            raise RuntimeError("bounded history update ports do not match frozen interface")

        parameters = self.function_parameters(contract)
        parameter_by_name = {
            str(parameter.get("name")): parameter for parameter in parameters
        }
        config_parameter = str(bindings.get("config_parameter", ""))
        state_parameter = str(bindings.get("state_parameter", ""))
        recon_parameter = str(bindings.get("recon_parameter", ""))
        if set(parameter_by_name) != {
            config_parameter, state_parameter, recon_parameter
        } or not all(
            parameter_is_pointer(parameter_by_name[name])
            for name in parameter_by_name
        ):
            raise RuntimeError("bounded history update requires config/state/recon pointers")

        native_420_field = str(bindings.get("native_420_field", ""))
        history_field = str(bindings.get("history_field", ""))
        pixels_field = str(bindings.get("history_pixels_field", ""))
        valid_field = str(bindings.get("history_valid_field", ""))
        identifier = re.compile(r"^[A-Za-z_][A-Za-z0-9_]*$")
        identifiers = {
            config_parameter, state_parameter, recon_parameter,
            native_420_field, history_field, pixels_field, valid_field,
            *scalar_ports.values(), *recon_ports, *valid_inputs, *valid_outputs,
            *[value for row in pixel_inputs for value in row],
            *[value for row in pixel_outputs for value in row],
        }
        if not all(identifier.fullmatch(value) for value in identifiers):
            raise RuntimeError("bounded history update bindings contain invalid identifier")

        parameter_specs = [
            f"{str(parameter.get('type', 'int')).strip()} {parameter.get('name')}"
            for parameter in parameters
        ]
        parameter_names = [str(parameter.get("name")) for parameter in parameters]
        caller_declarations = ", ".join(parameter_specs)
        alias_call = ", ".join(parameter_names)
        function_name = str(contract_function(contract).get("name"))
        original = function_name + "_original"

        abi = source_dir / "dsc_cicd_rtl_abi.h"
        abi.write_text(
            "#ifndef DSC_CICD_RTL_ABI_H\n#define DSC_CICD_RTL_ABI_H\n"
            "#include <stdint.h>\n"
            f"#define DSC_CICD_HISTORY_ENTRIES {entries}\n"
            f"#define DSC_CICD_HISTORY_COMPONENTS {components}\n"
            "typedef struct {\n"
            "    int32_t cfg_native_420;\n    int32_t hpos;\n"
            "    int32_t vpos;\n    int32_t num_components;\n"
            "    int32_t is_encoder;\n    int32_t ich_selected;\n"
            "    int32_t prev_ich_selected;\n"
            "    uint32_t recon[DSC_CICD_HISTORY_COMPONENTS];\n"
            "    int32_t valid[DSC_CICD_HISTORY_ENTRIES];\n"
            "    uint32_t pixels[DSC_CICD_HISTORY_COMPONENTS]"
            "[DSC_CICD_HISTORY_ENTRIES];\n"
            "} dsc_cicd_history_input_t;\n"
            "typedef struct {\n"
            "    int32_t valid[DSC_CICD_HISTORY_ENTRIES];\n"
            "    uint32_t pixels[DSC_CICD_HISTORY_COMPONENTS]"
            "[DSC_CICD_HISTORY_ENTRIES];\n"
            "} dsc_cicd_history_output_t;\n"
            "#ifdef __cplusplus\nextern \"C\" {\n#endif\n"
            "void dsc_cicd_rtl(const dsc_cicd_history_input_t *input, "
            "dsc_cicd_history_output_t *output);\n"
            "#ifdef __cplusplus\n}\n#endif\n#endif\n",
            encoding="utf-8",
        )
        header = source_dir / "dsc_cicd_overlay.h"
        header.write_text(
            "#ifndef DSC_CICD_OVERLAY_H\n#define DSC_CICD_OVERLAY_H\n"
            "#include \"dsc_types.h\"\n"
            f"void dsc_cicd_invoke({caller_declarations});\n#endif\n",
            encoding="utf-8",
        )
        overlay = source_dir / "dsc_cicd_overlay.c"
        overlay.write_text(
            "#include <stdint.h>\n#include <stdio.h>\n#include <stdlib.h>\n"
            "#include <string.h>\n#include \"dsc_cicd_overlay.h\"\n"
            "#include \"dsc_cicd_rtl_abi.h\"\n"
            f"extern void {original}({caller_declarations});\n"
            "static int dsc_cicd_mode(void) {\n"
            "    const char *value = getenv(\"DSC_CICD_MODE\");\n"
            "    if (value && strcmp(value, \"SHADOW\") == 0) return 1;\n"
            "    if (value && strcmp(value, \"RTL_RETURN\") == 0) return 2;\n"
            "    return 0;\n}\n"
            + self.overlay_runtime_metrics_source()
            + "static void dsc_cicd_require_history(const dsc_state_t *state) {\n"
            "    if (!state || !state->history.valid || state->numComponents < 3 || "
            "state->numComponents > DSC_CICD_HISTORY_COMPONENTS) {\n"
            "        fprintf(stderr, \"unsupported history domain: components=%d\\n\", "
            "state ? state->numComponents : -1);\n        exit(2);\n    }\n"
            "    for (int component = 0; component < state->numComponents; ++component)\n"
            "        if (!state->history.pixels[component]) {\n"
            "            fprintf(stderr, \"missing active history plane: %d\\n\", component);\n"
            "            exit(2);\n        }\n}\n"
            "static void dsc_cicd_capture_input(const dsc_cfg_t *cfg, "
            "const dsc_state_t *state, const unsigned int *recon, "
            "dsc_cicd_history_input_t *input) {\n"
            "    memset(input, 0, sizeof(*input));\n"
            f"    input->cfg_native_420 = cfg->{native_420_field};\n"
            "    input->hpos = state->hPos;\n    input->vpos = state->vPos;\n"
            "    input->num_components = state->numComponents;\n"
            "    input->is_encoder = state->isEncoder;\n"
            "    input->ich_selected = state->ichSelected;\n"
            "    input->prev_ich_selected = state->prevIchSelected;\n"
            "    memcpy(input->valid, state->history.valid, sizeof(input->valid));\n"
            "    for (int component = 0; component < state->numComponents; ++component) {\n"
            "        input->recon[component] = recon[component];\n"
            "        memcpy(input->pixels[component], state->history.pixels[component], "
            "sizeof(input->pixels[component]));\n    }\n}\n"
            "static void dsc_cicd_apply_history(dsc_state_t *state, "
            "const dsc_cicd_history_output_t *source) {\n"
            "    memcpy(state->history.valid, source->valid, sizeof(source->valid));\n"
            "    for (int component = 0; component < state->numComponents; ++component)\n"
            "        memcpy(state->history.pixels[component], source->pixels[component], "
            "sizeof(source->pixels[component]));\n}\n"
            "static int dsc_cicd_history_mismatch("
            "const dsc_cicd_history_output_t *left, "
            "const dsc_cicd_history_output_t *right, int components) {\n"
            "    if (memcmp(left->valid, right->valid, sizeof(left->valid)) != 0) return 1;\n"
            "    for (int component = 0; component < components; ++component)\n"
            "        if (memcmp(left->pixels[component], right->pixels[component], "
            "sizeof(left->pixels[component])) != 0) return 1;\n"
            "    return 0;\n}\n"
            + f"void dsc_cicd_invoke({caller_declarations}) {{\n"
            f"    dsc_cicd_require_history({state_parameter});\n"
            "    dsc_cicd_history_input_t dsc_cicd_input;\n"
            "    dsc_cicd_history_output_t dsc_cicd_c_output;\n"
            "    dsc_cicd_history_output_t dsc_cicd_rtl_output;\n"
            f"    dsc_cicd_capture_input({config_parameter}, {state_parameter}, "
            f"{recon_parameter}, &dsc_cicd_input);\n"
            f"    dsc_state_t dsc_cicd_c_state = *{state_parameter};\n"
            "    int dsc_cicd_c_valid[DSC_CICD_HISTORY_ENTRIES];\n"
            "    unsigned int dsc_cicd_c_pixels[DSC_CICD_HISTORY_COMPONENTS]"
            "[DSC_CICD_HISTORY_ENTRIES] = {{0}};\n"
            "    unsigned int dsc_cicd_c_recon[DSC_CICD_HISTORY_COMPONENTS] = {0};\n"
            "    memcpy(dsc_cicd_c_valid, dsc_cicd_input.valid, "
            "sizeof(dsc_cicd_c_valid));\n"
            "    for (int component = 0; component < DSC_CICD_HISTORY_COMPONENTS; ++component) {\n"
            "        memcpy(dsc_cicd_c_pixels[component], dsc_cicd_input.pixels[component], "
            "sizeof(dsc_cicd_c_pixels[component]));\n"
            "        dsc_cicd_c_recon[component] = dsc_cicd_input.recon[component];\n"
            "        dsc_cicd_c_state.history.pixels[component] = "
            "dsc_cicd_c_pixels[component];\n    }\n"
            "    dsc_cicd_c_state.history.valid = dsc_cicd_c_valid;\n"
            f"    {original}({config_parameter}, &dsc_cicd_c_state, dsc_cicd_c_recon);\n"
            "    memcpy(dsc_cicd_c_output.valid, dsc_cicd_c_valid, "
            "sizeof(dsc_cicd_c_output.valid));\n"
            "    memcpy(dsc_cicd_c_output.pixels, dsc_cicd_c_pixels, "
            "sizeof(dsc_cicd_c_output.pixels));\n"
            "    int mode = dsc_cicd_mode();\n    dsc_cicd_note_call(mode);\n"
            "    if (mode == 0) {\n"
            f"        dsc_cicd_apply_history({state_parameter}, &dsc_cicd_c_output);\n"
            "        return;\n    }\n"
            "    memset(&dsc_cicd_rtl_output, 0, sizeof(dsc_cicd_rtl_output));\n"
            "    dsc_cicd_rtl(&dsc_cicd_input, &dsc_cicd_rtl_output);\n"
            "    if (dsc_cicd_history_mismatch(&dsc_cicd_c_output, "
            f"&dsc_cicd_rtl_output, {state_parameter}->numComponents)) {{\n"
            "        ++dsc_cicd_mismatches;\n"
            "        fprintf(stderr, \"C/RTL bounded history mismatch: h=%d v=%d components=%d\\n\", "
            f"{state_parameter}->hPos, {state_parameter}->vPos, "
            f"{state_parameter}->numComponents);\n    }}\n"
            "    if (mode == 2) {\n"
            f"        dsc_cicd_apply_history({state_parameter}, &dsc_cicd_rtl_output);\n"
            "        return;\n    }\n"
            f"    dsc_cicd_apply_history({state_parameter}, &dsc_cicd_c_output);\n"
            "}\n"
            + f"void {function_name}({caller_declarations}) {{\n"
            f"    dsc_cicd_invoke({alias_call});\n}}\n",
            encoding="utf-8",
        )

        bridge_assignments = [
            f"    dut.{scalar_ports['cfg_native_420']} = static_cast<std::uint32_t>(input->cfg_native_420);",
            f"    dut.{scalar_ports['hPos']} = static_cast<std::uint32_t>(input->hpos);",
            f"    dut.{scalar_ports['vPos']} = static_cast<std::uint32_t>(input->vpos);",
            f"    dut.{scalar_ports['numComponents']} = static_cast<std::uint32_t>(input->num_components);",
            f"    dut.{scalar_ports['isEncoder']} = static_cast<std::uint32_t>(input->is_encoder);",
            f"    dut.{scalar_ports['ichSelected']} = static_cast<std::uint32_t>(input->ich_selected);",
            f"    dut.{scalar_ports['prevIchSelected']} = static_cast<std::uint32_t>(input->prev_ich_selected);",
        ]
        bridge_outputs = []
        for component in range(components):
            bridge_assignments.append(
                f"    dut.{recon_ports[component]} = input->recon[{component}];"
            )
        for entry in range(entries):
            bridge_assignments.append(
                f"    dut.{valid_inputs[entry]} = "
                f"static_cast<std::uint32_t>(input->valid[{entry}]);"
            )
            bridge_outputs.append(
                f"    output->valid[{entry}] = "
                f"static_cast<std::int32_t>(dut.{valid_outputs[entry]});"
            )
        for component in range(components):
            for entry in range(entries):
                bridge_assignments.append(
                    f"    dut.{pixel_inputs[component][entry]} = "
                    f"input->pixels[{component}][{entry}];"
                )
                bridge_outputs.append(
                    f"    output->pixels[{component}][{entry}] = "
                    f"static_cast<std::uint32_t>(dut.{pixel_outputs[component][entry]});"
                )
        bridge = source_dir / "rtl_bridge.cpp"
        bridge.write_text(
            "#include <cstdint>\n#include \"verilated.h\"\n"
            "#include \"dsc_cicd_rtl_abi.h\"\n"
            f"#include \"V{safe_identifier(module)}.h\"\n"
            "double sc_time_stamp() { return 0.0; }\n"
            "extern \"C\" void dsc_cicd_rtl("
            "const dsc_cicd_history_input_t *input, "
            "dsc_cicd_history_output_t *output) {\n"
            f"    static V{safe_identifier(module)} dut;\n"
            + "\n".join(bridge_assignments)
            + "\n    dut.eval();\n"
            + "\n".join(bridge_outputs)
            + "\n}\n",
            encoding="utf-8",
        )
        main = source_dir / "dsc_cicd_main.c"
        main.write_text(
            "#include <stdio.h>\nextern int dsc_cicd_original_main(int, char **);\n"
            "int main(int argc, char **argv) { return dsc_cicd_original_main(argc, argv); }\n",
            encoding="utf-8",
        )
        rtl_bindings = [
            f"{config_parameter}->{native_420_field}",
            f"{state_parameter}->hPos",
            f"{state_parameter}->vPos",
            f"{state_parameter}->numComponents",
            f"{state_parameter}->isEncoder",
            f"{state_parameter}->ichSelected",
            f"{state_parameter}->prevIchSelected",
            *[f"{recon_parameter}[{component}]" for component in range(components)],
            *[
                f"{state_parameter}->{history_field}.{valid_field}[{entry}]"
                for entry in range(entries)
            ],
            *[
                f"active({component}) ? {state_parameter}->{history_field}."
                f"{pixels_field}[{component}][{entry}] : 0"
                for component in range(components) for entry in range(entries)
            ],
        ]
        return {
            "header": header,
            "abi": abi,
            "overlay": overlay,
            "bridge": bridge,
            "main": main,
            "candidate": candidate_sv,
            "composition": {
                "status": "PASS",
                "adapter_kind": "explicit_bounded_history_update_transition",
                "caller_parameter_count": len(parameters),
                "rtl_input_count": len(inputs),
                "frozen_input_ports": [str(port.get("name")) for port in inputs],
                "rtl_bindings": rtl_bindings,
                "state_outputs": [str(port.get("name")) for port in outputs],
                "rtl_return_controls_complete_active_history_image": True,
                "c_oracle_uses_private_history_memory": True,
                "inactive_component_planes_are_not_dereferenced_or_committed": True,
                "residual_symbol_alias_routes_to_dispatcher": True,
            },
        }

    def write_bounded_history_caller_transition_overlay_sources(
        self,
        contract: dict[str, Any],
        source_dir: pathlib.Path,
        module: str,
        candidate_sv: pathlib.Path,
    ) -> dict[str, Any]:
        """Bind line sampling plus a complete composed ICH output image."""
        semantics = contract.get("semantics", {}) or {}
        constants = semantics.get("constants", {}) or {}
        bindings = semantics.get("bindings", {}) or {}
        entries = int(constants.get("ich_entries", 0))
        components = int(constants.get("component_count", 0))
        padding_left = int(constants.get("padding_left", 0))
        if (entries, components, padding_left) != (32, 4, 5):
            raise RuntimeError("bounded history caller constants are incomplete")
        argument_ports = {
            str(key): str(value)
            for key, value in (bindings.get("argument_ports", {}) or {}).items()
        }
        config_ports = {
            str(key): str(value)
            for key, value in (bindings.get("config_ports", {}) or {}).items()
        }
        state_ports = {
            str(key): str(value)
            for key, value in (bindings.get("state_ports", {}) or {}).items()
        }
        line_ports = [str(value) for value in bindings.get("line_sample_ports", [])]
        valid_inputs = [str(value) for value in bindings.get("valid_input_ports", [])]
        pixel_inputs = [
            [str(value) for value in row]
            for row in bindings.get("pixel_input_ports", [])
        ]
        valid_outputs = [str(value) for value in bindings.get("valid_output_ports", [])]
        pixel_outputs = [
            [str(value) for value in row]
            for row in bindings.get("pixel_output_ports", [])
        ]
        if (
            set(config_ports) != {"native_420", "slice_width", "pic_width"}
            or set(state_ports) != {
                "hPos", "vPos", "numComponents", "pixelsInGroup",
                "isEncoder", "ichSelected", "prevIchSelected",
            }
            or len(argument_ports) != 2
            or len(line_ports) != components
            or len(valid_inputs) != entries
            or len(valid_outputs) != entries
            or len(pixel_inputs) != components
            or len(pixel_outputs) != components
            or any(len(row) != entries for row in pixel_inputs)
            or any(len(row) != entries for row in pixel_outputs)
        ):
            raise RuntimeError("bounded history caller bindings are incomplete")
        horizontal_parameter = str(bindings.get("horizontal_position_parameter", ""))
        vertical_parameter = str(bindings.get("vertical_position_parameter", ""))
        if set(argument_ports) != {horizontal_parameter, vertical_parameter}:
            raise RuntimeError("bounded history caller scalar positions are incomplete")

        ports = [
            port for port in (contract.get("interface", {}) or {}).get("ports", [])
            if isinstance(port, dict)
        ]
        inputs = [port for port in ports if port.get("direction") == "input"]
        outputs = [port for port in ports if port.get("direction") == "output"]
        expected_inputs = {
            *argument_ports.values(), *config_ports.values(), *state_ports.values(),
            *line_ports, *valid_inputs,
            *[value for row in pixel_inputs for value in row],
        }
        expected_outputs = {
            *valid_outputs, *[value for row in pixel_outputs for value in row],
        }
        if (
            {str(port.get("name")) for port in inputs} != expected_inputs
            or {str(port.get("name")) for port in outputs} != expected_outputs
        ):
            raise RuntimeError("bounded history caller ports do not match frozen interface")

        parameters = self.function_parameters(contract)
        parameter_by_name = {
            str(parameter.get("name")): parameter for parameter in parameters
        }
        config_parameter = str(bindings.get("config_parameter", ""))
        state_parameter = str(bindings.get("state_parameter", ""))
        line_parameter = str(bindings.get("line_parameter", ""))
        if set(parameter_by_name) != {
            config_parameter, state_parameter, line_parameter,
            horizontal_parameter, vertical_parameter,
        }:
            raise RuntimeError("bounded history caller native ABI is incomplete")
        if not all(
            parameter_is_pointer(parameter_by_name[name])
            for name in (config_parameter, state_parameter, line_parameter)
        ) or any(
            parameter_is_pointer(parameter_by_name[name])
            for name in (horizontal_parameter, vertical_parameter)
        ):
            raise RuntimeError("bounded history caller pointer/scalar ABI changed")

        history_field = str(bindings.get("history_field", ""))
        pixels_field = str(bindings.get("history_pixels_field", ""))
        valid_field = str(bindings.get("history_valid_field", ""))
        identifier = re.compile(r"^[A-Za-z_][A-Za-z0-9_]*$")
        identifiers = {
            config_parameter, state_parameter, line_parameter,
            horizontal_parameter, vertical_parameter,
            history_field, pixels_field, valid_field,
            *argument_ports.values(), *config_ports.values(), *state_ports.values(),
            *line_ports, *valid_inputs, *valid_outputs,
            *[value for row in pixel_inputs for value in row],
            *[value for row in pixel_outputs for value in row],
        }
        if not all(identifier.fullmatch(value) for value in identifiers):
            raise RuntimeError("bounded history caller bindings contain invalid identifier")

        parameter_specs = [
            f"{str(parameter.get('type', 'int')).strip()} {parameter.get('name')}"
            for parameter in parameters
        ]
        parameter_names = [str(parameter.get("name")) for parameter in parameters]
        caller_declarations = ", ".join(parameter_specs)
        alias_call = ", ".join(parameter_names)
        function_name = str(contract_function(contract).get("name"))
        original = function_name + "_original"

        abi = source_dir / "dsc_cicd_rtl_abi.h"
        abi.write_text(
            "#ifndef DSC_CICD_RTL_ABI_H\n#define DSC_CICD_RTL_ABI_H\n"
            "#include <stdint.h>\n"
            f"#define DSC_CICD_HISTORY_ENTRIES {entries}\n"
            f"#define DSC_CICD_HISTORY_COMPONENTS {components}\n"
            "typedef struct {\n"
            "    int32_t hpos_arg;\n    int32_t vpos_arg;\n"
            "    int32_t cfg_native_420;\n    int32_t cfg_slice_width;\n"
            "    int32_t cfg_pic_width;\n    int32_t state_hpos;\n"
            "    int32_t state_vpos;\n    int32_t num_components;\n"
            "    int32_t pixels_in_group;\n    int32_t is_encoder;\n"
            "    int32_t ich_selected;\n    int32_t prev_ich_selected;\n"
            "    uint32_t line_sample[DSC_CICD_HISTORY_COMPONENTS];\n"
            "    int32_t valid[DSC_CICD_HISTORY_ENTRIES];\n"
            "    uint32_t pixels[DSC_CICD_HISTORY_COMPONENTS]"
            "[DSC_CICD_HISTORY_ENTRIES];\n"
            "} dsc_cicd_history_input_t;\n"
            "typedef struct {\n"
            "    int32_t valid[DSC_CICD_HISTORY_ENTRIES];\n"
            "    uint32_t pixels[DSC_CICD_HISTORY_COMPONENTS]"
            "[DSC_CICD_HISTORY_ENTRIES];\n"
            "} dsc_cicd_history_output_t;\n"
            "#ifdef __cplusplus\nextern \"C\" {\n#endif\n"
            "void dsc_cicd_rtl(const dsc_cicd_history_input_t *input, "
            "dsc_cicd_history_output_t *output);\n"
            "#ifdef __cplusplus\n}\n#endif\n#endif\n",
            encoding="utf-8",
        )
        header = source_dir / "dsc_cicd_overlay.h"
        header.write_text(
            "#ifndef DSC_CICD_OVERLAY_H\n#define DSC_CICD_OVERLAY_H\n"
            "#include \"dsc_types.h\"\n"
            f"void dsc_cicd_invoke({caller_declarations});\n#endif\n",
            encoding="utf-8",
        )
        overlay = source_dir / "dsc_cicd_overlay.c"
        overlay.write_text(
            "#include <stdint.h>\n#include <stdio.h>\n#include <stdlib.h>\n"
            "#include <string.h>\n#include \"dsc_cicd_overlay.h\"\n"
            "#include \"dsc_cicd_rtl_abi.h\"\n"
            f"extern void {original}({caller_declarations});\n"
            "static int dsc_cicd_mode(void) {\n"
            "    const char *value = getenv(\"DSC_CICD_MODE\");\n"
            "    if (value && strcmp(value, \"SHADOW\") == 0) return 1;\n"
            "    if (value && strcmp(value, \"RTL_RETURN\") == 0) return 2;\n"
            "    return 0;\n}\n"
            + self.overlay_runtime_metrics_source()
            + "static void dsc_cicd_require_history(const dsc_state_t *state) {\n"
            "    if (!state || !state->history.valid || state->numComponents < 3 || "
            "state->numComponents > DSC_CICD_HISTORY_COMPONENTS) {\n"
            "        fprintf(stderr, \"unsupported history caller domain: components=%d\\n\", "
            "state ? state->numComponents : -1);\n        exit(2);\n    }\n"
            "    for (int component = 0; component < state->numComponents; ++component)\n"
            "        if (!state->history.pixels[component]) {\n"
            "            fprintf(stderr, \"missing active history plane: %d\\n\", component);\n"
            "            exit(2);\n        }\n}\n"
            "static void dsc_cicd_apply_history(dsc_state_t *state, "
            "const dsc_cicd_history_output_t *source) {\n"
            "    memcpy(state->history.valid, source->valid, sizeof(source->valid));\n"
            "    for (int component = 0; component < state->numComponents; ++component)\n"
            "        memcpy(state->history.pixels[component], source->pixels[component], "
            "sizeof(source->pixels[component]));\n}\n"
            "static int dsc_cicd_history_mismatch("
            "const dsc_cicd_history_output_t *left, "
            "const dsc_cicd_history_output_t *right, int components) {\n"
            "    if (memcmp(left->valid, right->valid, sizeof(left->valid)) != 0) return 1;\n"
            "    for (int component = 0; component < components; ++component)\n"
            "        if (memcmp(left->pixels[component], right->pixels[component], "
            "sizeof(left->pixels[component])) != 0) return 1;\n"
            "    return 0;\n}\n"
            + f"void dsc_cicd_invoke({caller_declarations}) {{\n"
            f"    dsc_cicd_require_history({state_parameter});\n"
            "    dsc_cicd_history_input_t dsc_cicd_input;\n"
            "    dsc_cicd_history_output_t dsc_cicd_c_output;\n"
            "    dsc_cicd_history_output_t dsc_cicd_rtl_output;\n"
            "    memset(&dsc_cicd_input, 0, sizeof(dsc_cicd_input));\n"
            f"    dsc_cicd_input.hpos_arg = {horizontal_parameter};\n"
            f"    dsc_cicd_input.vpos_arg = {vertical_parameter};\n"
            f"    dsc_cicd_input.cfg_native_420 = {config_parameter}->native_420;\n"
            f"    dsc_cicd_input.cfg_slice_width = {config_parameter}->slice_width;\n"
            f"    dsc_cicd_input.cfg_pic_width = {config_parameter}->pic_width;\n"
            f"    dsc_cicd_input.state_hpos = {state_parameter}->hPos;\n"
            f"    dsc_cicd_input.state_vpos = {state_parameter}->vPos;\n"
            f"    dsc_cicd_input.num_components = {state_parameter}->numComponents;\n"
            f"    dsc_cicd_input.pixels_in_group = {state_parameter}->pixelsInGroup;\n"
            f"    dsc_cicd_input.is_encoder = {state_parameter}->isEncoder;\n"
            f"    dsc_cicd_input.ich_selected = {state_parameter}->ichSelected;\n"
            f"    dsc_cicd_input.prev_ich_selected = {state_parameter}->prevIchSelected;\n"
            f"    memcpy(dsc_cicd_input.valid, {state_parameter}->{history_field}."
            f"{valid_field}, sizeof(dsc_cicd_input.valid));\n"
            f"    int dsc_cicd_previous_hpos = {horizontal_parameter} - "
            f"{state_parameter}->pixelsInGroup;\n"
            "    for (int component = 0; component < "
            f"{state_parameter}->numComponents; ++component) {{\n"
            f"        memcpy(dsc_cicd_input.pixels[component], {state_parameter}->"
            f"{history_field}.{pixels_field}[component], "
            "sizeof(dsc_cicd_input.pixels[component]));\n"
            "        if (dsc_cicd_previous_hpos >= 0) {\n"
            f"            if (!{line_parameter} || !{line_parameter}[component]) {{\n"
            "                fprintf(stderr, \"missing active reconstructed line plane\\n\");\n"
            "                exit(2);\n            }\n"
            f"            dsc_cicd_input.line_sample[component] = (uint32_t)"
            f"{line_parameter}[component][dsc_cicd_previous_hpos + {padding_left}];\n"
            "        }\n    }\n"
            f"    dsc_state_t dsc_cicd_c_state = *{state_parameter};\n"
            "    int dsc_cicd_c_valid[DSC_CICD_HISTORY_ENTRIES];\n"
            "    unsigned int dsc_cicd_c_pixels[DSC_CICD_HISTORY_COMPONENTS]"
            "[DSC_CICD_HISTORY_ENTRIES] = {{0}};\n"
            "    memcpy(dsc_cicd_c_valid, dsc_cicd_input.valid, "
            "sizeof(dsc_cicd_c_valid));\n"
            "    for (int component = 0; component < DSC_CICD_HISTORY_COMPONENTS; ++component) {\n"
            "        memcpy(dsc_cicd_c_pixels[component], dsc_cicd_input.pixels[component], "
            "sizeof(dsc_cicd_c_pixels[component]));\n"
            "        dsc_cicd_c_state.history.pixels[component] = "
            "dsc_cicd_c_pixels[component];\n    }\n"
            "    dsc_cicd_c_state.history.valid = dsc_cicd_c_valid;\n"
            f"    {original}({config_parameter}, &dsc_cicd_c_state, {line_parameter}, "
            f"{horizontal_parameter}, {vertical_parameter});\n"
            "    memcpy(dsc_cicd_c_output.valid, dsc_cicd_c_valid, "
            "sizeof(dsc_cicd_c_output.valid));\n"
            "    memcpy(dsc_cicd_c_output.pixels, dsc_cicd_c_pixels, "
            "sizeof(dsc_cicd_c_output.pixels));\n"
            "    int mode = dsc_cicd_mode();\n    dsc_cicd_note_call(mode);\n"
            "    if (mode == 0) {\n"
            f"        dsc_cicd_apply_history({state_parameter}, &dsc_cicd_c_output);\n"
            "        return;\n    }\n"
            "    memset(&dsc_cicd_rtl_output, 0, sizeof(dsc_cicd_rtl_output));\n"
            "    dsc_cicd_rtl(&dsc_cicd_input, &dsc_cicd_rtl_output);\n"
            "    if (dsc_cicd_history_mismatch(&dsc_cicd_c_output, "
            f"&dsc_cicd_rtl_output, {state_parameter}->numComponents)) {{\n"
            "        ++dsc_cicd_mismatches;\n"
            "        fprintf(stderr, \"C/RTL bounded history caller mismatch: h=%d v=%d components=%d\\n\", "
            f"{horizontal_parameter}, {vertical_parameter}, "
            f"{state_parameter}->numComponents);\n    }}\n"
            "    if (mode == 2) {\n"
            f"        dsc_cicd_apply_history({state_parameter}, &dsc_cicd_rtl_output);\n"
            "        return;\n    }\n"
            f"    dsc_cicd_apply_history({state_parameter}, &dsc_cicd_c_output);\n"
            "}\n"
            + f"void {function_name}({caller_declarations}) {{\n"
            f"    dsc_cicd_invoke({alias_call});\n}}\n",
            encoding="utf-8",
        )

        bridge_assignments = [
            f"    dut.{argument_ports[horizontal_parameter]} = static_cast<std::uint32_t>(input->hpos_arg);",
            f"    dut.{argument_ports[vertical_parameter]} = static_cast<std::uint32_t>(input->vpos_arg);",
            f"    dut.{config_ports['native_420']} = static_cast<std::uint32_t>(input->cfg_native_420);",
            f"    dut.{config_ports['slice_width']} = static_cast<std::uint32_t>(input->cfg_slice_width);",
            f"    dut.{config_ports['pic_width']} = static_cast<std::uint32_t>(input->cfg_pic_width);",
            f"    dut.{state_ports['hPos']} = static_cast<std::uint32_t>(input->state_hpos);",
            f"    dut.{state_ports['vPos']} = static_cast<std::uint32_t>(input->state_vpos);",
            f"    dut.{state_ports['numComponents']} = static_cast<std::uint32_t>(input->num_components);",
            f"    dut.{state_ports['pixelsInGroup']} = static_cast<std::uint32_t>(input->pixels_in_group);",
            f"    dut.{state_ports['isEncoder']} = static_cast<std::uint32_t>(input->is_encoder);",
            f"    dut.{state_ports['ichSelected']} = static_cast<std::uint32_t>(input->ich_selected);",
            f"    dut.{state_ports['prevIchSelected']} = static_cast<std::uint32_t>(input->prev_ich_selected);",
        ]
        bridge_outputs = []
        for component in range(components):
            bridge_assignments.append(
                f"    dut.{line_ports[component]} = input->line_sample[{component}];"
            )
        for entry in range(entries):
            bridge_assignments.append(
                f"    dut.{valid_inputs[entry]} = "
                f"static_cast<std::uint32_t>(input->valid[{entry}]);"
            )
            bridge_outputs.append(
                f"    output->valid[{entry}] = "
                f"static_cast<std::int32_t>(dut.{valid_outputs[entry]});"
            )
        for component in range(components):
            for entry in range(entries):
                bridge_assignments.append(
                    f"    dut.{pixel_inputs[component][entry]} = "
                    f"input->pixels[{component}][{entry}];"
                )
                bridge_outputs.append(
                    f"    output->pixels[{component}][{entry}] = "
                    f"static_cast<std::uint32_t>(dut.{pixel_outputs[component][entry]});"
                )
        bridge = source_dir / "rtl_bridge.cpp"
        bridge.write_text(
            "#include <cstdint>\n#include \"verilated.h\"\n"
            "#include \"dsc_cicd_rtl_abi.h\"\n"
            f"#include \"V{safe_identifier(module)}.h\"\n"
            "double sc_time_stamp() { return 0.0; }\n"
            "extern \"C\" void dsc_cicd_rtl("
            "const dsc_cicd_history_input_t *input, "
            "dsc_cicd_history_output_t *output) {\n"
            f"    static V{safe_identifier(module)} dut;\n"
            + "\n".join(bridge_assignments)
            + "\n    dut.eval();\n"
            + "\n".join(bridge_outputs)
            + "\n}\n",
            encoding="utf-8",
        )
        main = source_dir / "dsc_cicd_main.c"
        main.write_text(
            "#include <stdio.h>\nextern int dsc_cicd_original_main(int, char **);\n"
            "int main(int argc, char **argv) { return dsc_cicd_original_main(argc, argv); }\n",
            encoding="utf-8",
        )
        rtl_bindings = [
            horizontal_parameter, vertical_parameter,
            f"{config_parameter}->native_420",
            f"{config_parameter}->slice_width",
            f"{config_parameter}->pic_width",
            f"{state_parameter}->hPos",
            f"{state_parameter}->vPos",
            f"{state_parameter}->numComponents",
            f"{state_parameter}->pixelsInGroup",
            f"{state_parameter}->isEncoder",
            f"{state_parameter}->ichSelected",
            f"{state_parameter}->prevIchSelected",
            *[
                f"update ? {line_parameter}[{component}][hPos-pixelsInGroup+{padding_left}] : 0"
                for component in range(components)
            ],
            *[
                f"{state_parameter}->{history_field}.{valid_field}[{entry}]"
                for entry in range(entries)
            ],
            *[
                f"active({component}) ? {state_parameter}->{history_field}."
                f"{pixels_field}[{component}][{entry}] : 0"
                for component in range(components) for entry in range(entries)
            ],
        ]
        return {
            "header": header,
            "abi": abi,
            "overlay": overlay,
            "bridge": bridge,
            "main": main,
            "candidate": candidate_sv,
            "composition": {
                "status": "PASS",
                "adapter_kind": "explicit_bounded_history_caller_transition",
                "caller_parameter_count": len(parameters),
                "rtl_input_count": len(inputs),
                "frozen_input_ports": [str(port.get("name")) for port in inputs],
                "rtl_bindings": rtl_bindings,
                "state_outputs": [str(port.get("name")) for port in outputs],
                "rtl_return_controls_complete_active_history_image": True,
                "c_oracle_uses_private_history_memory": True,
                "line_samples_are_read_only_and_guarded_by_update_condition": True,
                "inactive_component_planes_are_not_dereferenced_or_committed": True,
                "residual_symbol_alias_routes_to_dispatcher": True,
            },
        }

    def write_bounded_vld_unit_transition_overlay_sources(
        self,
        contract: dict[str, Any],
        source_dir: pathlib.Path,
        module: str,
        candidate_sv: pathlib.Path,
    ) -> dict[str, Any]:
        """Bind one decoder VLD unit to a complete selected-FIFO snapshot."""
        semantics = contract.get("semantics", {}) or {}
        constants = semantics.get("constants", {}) or {}
        bindings = semantics.get("bindings", {}) or {}
        units = int(constants.get("max_units", 0))
        samples = int(constants.get("samples_per_unit", 0))
        indices = int(constants.get("max_ich_indices", 0))
        fifo_bytes = int(constants.get("fifo_bytes", 0))
        prefix_bits = int(constants.get("max_prefix_bits", 0))
        if (units, samples, indices, fifo_bytes, prefix_bits) != (4, 3, 6, 17, 17):
            raise RuntimeError("bounded VLD constants are incomplete")

        config_ports = {
            str(key): str(value)
            for key, value in (bindings.get("config_ports", {}) or {}).items()
        }
        state_ports = {
            str(key): str(value)
            for key, value in (bindings.get("state_ports", {}) or {}).items()
        }
        array_inputs = {
            str(key): [str(value) for value in values]
            for key, values in (bindings.get("array_input_ports", {}) or {}).items()
        }
        state_outputs = {
            str(key): str(value)
            for key, value in (bindings.get("state_output_ports", {}) or {}).items()
        }
        array_outputs = {
            str(key): [str(value) for value in values]
            for key, values in (bindings.get("array_output_ports", {}) or {}).items()
        }
        qlevel_ports = {
            str(key): str(value)
            for key, value in (bindings.get("qlevel_ports", {}) or {}).items()
        }
        residual_inputs = [str(value) for value in bindings.get("residual_input_ports", [])]
        residual_outputs = [str(value) for value in bindings.get("residual_output_ports", [])]
        fifo_ports = {
            str(key): str(value)
            for key, value in (bindings.get("fifo_ports", {}) or {}).items()
        }
        fifo_data_ports = [str(value) for value in bindings.get("fifo_data_ports", [])]
        fifo_outputs = {
            str(key): str(value)
            for key, value in (bindings.get("fifo_output_ports", {}) or {}).items()
        }
        unit_port = str(bindings.get("unit_port", ""))
        expected_array_sizes = {
            "cpntBitDepth": units,
            "unitCType": units,
            "unitSspMap": units,
            "ichIndexUnitMap": indices,
            "ichLookup": indices,
            "predictedSize": units,
            "rcSizeUnit": units,
            "useMidpoint": units,
        }
        if (
            set(config_ports) != {
                "bits_per_component", "somewhat_flat_qp_thresh",
                "dsc_version_minor", "native_420", "flatness_min_qp",
                "flatness_max_qp",
            }
            or set(state_ports) != {
                "firstFlat", "flatnessType", "groupCount", "ichIndicesInGroup",
                "ichSelected", "prevFirstFlat", "prevIchSelected", "primaryQp",
                "prevPrimaryQp", "unitsPerGroup", "numBits",
            }
            or set(array_inputs) != set(expected_array_sizes)
            or any(
                len(array_inputs[field]) != size
                for field, size in expected_array_sizes.items()
            )
            or set(state_outputs) != {
                "firstFlat", "flatnessType", "ichSelected", "prevFirstFlat",
                "prevIchSelected", "numBits",
            }
            or set(array_outputs) != {
                "ichLookup", "predictedSize", "rcSizeUnit", "useMidpoint",
            }
            or any(
                len(array_outputs[field]) != expected_array_sizes[field]
                for field in array_outputs
            )
            or set(qlevel_ports) != {
                "luma_primary", "chroma_primary", "luma_previous",
                "chroma_previous",
            }
            or len(residual_inputs) != samples
            or len(residual_outputs) != samples
            or set(fifo_ports) != {"size", "fullness", "read_ptr"}
            or len(fifo_data_ports) != fifo_bytes
            or set(fifo_outputs) != {"lane", "fullness", "read_ptr"}
            or not unit_port
        ):
            raise RuntimeError("bounded VLD bindings are incomplete")

        ports = [
            port for port in (contract.get("interface", {}) or {}).get("ports", [])
            if isinstance(port, dict)
        ]
        inputs = [port for port in ports if port.get("direction") == "input"]
        outputs = [port for port in ports if port.get("direction") == "output"]
        expected_inputs = {
            unit_port, *config_ports.values(), *state_ports.values(),
            *[value for row in array_inputs.values() for value in row],
            *qlevel_ports.values(), *residual_inputs, *fifo_ports.values(),
            *fifo_data_ports,
        }
        expected_outputs = {
            "domain_valid", *state_outputs.values(),
            *[value for row in array_outputs.values() for value in row],
            *residual_outputs, *fifo_outputs.values(),
        }
        if (
            {str(port.get("name")) for port in inputs} != expected_inputs
            or {str(port.get("name")) for port in outputs} != expected_outputs
        ):
            raise RuntimeError("bounded VLD ports do not match the frozen interface")

        parameters = self.function_parameters(contract)
        parameter_by_name = {
            str(parameter.get("name")): parameter for parameter in parameters
        }
        config_parameter = str(bindings.get("config_parameter", ""))
        state_parameter = str(bindings.get("state_parameter", ""))
        unit_parameter = str(bindings.get("unit_parameter", ""))
        residual_parameter = str(bindings.get("residual_parameter", ""))
        byte_parameter = str(bindings.get("byte_pointer_parameter", ""))
        if set(parameter_by_name) != {
            config_parameter, state_parameter, unit_parameter,
            residual_parameter, byte_parameter,
        }:
            raise RuntimeError("bounded VLD native ABI is incomplete")
        if (
            not parameter_is_pointer(parameter_by_name[config_parameter])
            or not parameter_is_pointer(parameter_by_name[state_parameter])
            or parameter_is_pointer(parameter_by_name[unit_parameter])
            or not parameter_is_pointer(parameter_by_name[residual_parameter])
            or not parameter_is_pointer(parameter_by_name[byte_parameter])
        ):
            raise RuntimeError("bounded VLD pointer/scalar ABI changed")

        identifier = re.compile(r"^[A-Za-z_][A-Za-z0-9_]*$")
        identifiers = {
            config_parameter, state_parameter, unit_parameter,
            residual_parameter, byte_parameter, unit_port,
            *expected_inputs, *expected_outputs,
        }
        if not all(identifier.fullmatch(value) for value in identifiers):
            raise RuntimeError("bounded VLD bindings contain invalid identifier")

        parameter_specs = [
            f"{str(parameter.get('type', 'int')).strip()} {parameter.get('name')}"
            for parameter in parameters
        ]
        parameter_names = [str(parameter.get("name")) for parameter in parameters]
        caller_declarations = ", ".join(parameter_specs)
        alias_call = ", ".join(parameter_names)
        function_name = str(contract_function(contract).get("name"))
        original = function_name + "_original"

        config_abi = {
            "bits_per_component": "cfg_bits_per_component",
            "somewhat_flat_qp_thresh": "cfg_somewhat_flat_qp_thresh",
            "dsc_version_minor": "cfg_dsc_version_minor",
            "native_420": "cfg_native_420",
            "flatness_min_qp": "cfg_flatness_min_qp",
            "flatness_max_qp": "cfg_flatness_max_qp",
        }
        state_abi = {
            "firstFlat": "state_first_flat",
            "flatnessType": "state_flatness_type",
            "groupCount": "state_group_count",
            "ichIndicesInGroup": "state_ich_indices_in_group",
            "ichSelected": "state_ich_selected",
            "prevFirstFlat": "state_prev_first_flat",
            "prevIchSelected": "state_prev_ich_selected",
            "primaryQp": "state_primary_qp",
            "prevPrimaryQp": "state_prev_primary_qp",
            "unitsPerGroup": "state_units_per_group",
            "numBits": "state_num_bits",
        }
        array_abi = {
            "cpntBitDepth": "cpnt_bit_depth",
            "unitCType": "unit_c_type",
            "unitSspMap": "unit_ssp_map",
            "ichIndexUnitMap": "ich_index_unit_map",
            "ichLookup": "ich_lookup",
            "predictedSize": "predicted_size",
            "rcSizeUnit": "rc_size_unit",
            "useMidpoint": "use_midpoint",
        }
        qlevel_abi = {
            "luma_primary": "qlevel_luma_primary",
            "chroma_primary": "qlevel_chroma_primary",
            "luma_previous": "qlevel_luma_previous",
            "chroma_previous": "qlevel_chroma_previous",
        }

        abi = source_dir / "dsc_cicd_rtl_abi.h"
        abi.write_text(
            "#ifndef DSC_CICD_RTL_ABI_H\n#define DSC_CICD_RTL_ABI_H\n"
            "#include <stdint.h>\n"
            f"#define DSC_CICD_VLD_UNITS {units}\n"
            f"#define DSC_CICD_VLD_SAMPLES {samples}\n"
            f"#define DSC_CICD_VLD_INDICES {indices}\n"
            f"#define DSC_CICD_VLD_FIFO_BYTES {fifo_bytes}\n"
            "typedef struct {\n"
            "    int32_t unit;\n"
            + "".join(f"    int32_t {name};\n" for name in config_abi.values())
            + "".join(f"    int32_t {name};\n" for name in state_abi.values())
            + "    int32_t cpnt_bit_depth[DSC_CICD_VLD_UNITS];\n"
            "    int32_t unit_c_type[DSC_CICD_VLD_UNITS];\n"
            "    int32_t unit_ssp_map[DSC_CICD_VLD_UNITS];\n"
            "    int32_t ich_index_unit_map[DSC_CICD_VLD_INDICES];\n"
            "    int32_t ich_lookup[DSC_CICD_VLD_INDICES];\n"
            "    int32_t predicted_size[DSC_CICD_VLD_UNITS];\n"
            "    int32_t rc_size_unit[DSC_CICD_VLD_UNITS];\n"
            "    int32_t use_midpoint[DSC_CICD_VLD_UNITS];\n"
            + "".join(f"    int32_t {name};\n" for name in qlevel_abi.values())
            + "    int32_t quantized_residual[DSC_CICD_VLD_SAMPLES];\n"
            "    int32_t fifo_size;\n    int32_t fifo_fullness;\n"
            "    int32_t fifo_read_ptr;\n"
            "    uint8_t fifo_data[DSC_CICD_VLD_FIFO_BYTES];\n"
            "} dsc_cicd_vld_input_t;\n"
            "typedef struct {\n"
            "    int32_t domain_valid;\n"
            "    int32_t first_flat;\n    int32_t flatness_type;\n"
            "    int32_t ich_selected;\n    int32_t prev_first_flat;\n"
            "    int32_t prev_ich_selected;\n    int32_t num_bits;\n"
            "    int32_t ich_lookup[DSC_CICD_VLD_INDICES];\n"
            "    int32_t predicted_size[DSC_CICD_VLD_UNITS];\n"
            "    int32_t rc_size_unit[DSC_CICD_VLD_UNITS];\n"
            "    int32_t use_midpoint[DSC_CICD_VLD_UNITS];\n"
            "    int32_t quantized_residual[DSC_CICD_VLD_SAMPLES];\n"
            "    int32_t fifo_lane;\n    int32_t fifo_fullness;\n"
            "    int32_t fifo_read_ptr;\n"
            "} dsc_cicd_vld_output_t;\n"
            "#ifdef __cplusplus\nextern \"C\" {\n#endif\n"
            "void dsc_cicd_rtl(const dsc_cicd_vld_input_t *input, "
            "dsc_cicd_vld_output_t *output);\n"
            "#ifdef __cplusplus\n}\n#endif\n#endif\n",
            encoding="utf-8",
        )
        header = source_dir / "dsc_cicd_overlay.h"
        header.write_text(
            "#ifndef DSC_CICD_OVERLAY_H\n#define DSC_CICD_OVERLAY_H\n"
            "#include \"dsc_types.h\"\n"
            f"void dsc_cicd_invoke({caller_declarations});\n#endif\n",
            encoding="utf-8",
        )

        capture_input_scalars = "".join(
            f"    dsc_cicd_input.{abi_name} = {config_parameter}->{field};\n"
            for field, abi_name in config_abi.items()
        ) + "".join(
            f"    dsc_cicd_input.{abi_name} = {state_parameter}->{field};\n"
            for field, abi_name in state_abi.items()
        )
        capture_input_arrays = "".join(
            f"    memcpy(dsc_cicd_input.{abi_name}, {state_parameter}->{field}, "
            f"sizeof(dsc_cicd_input.{abi_name}));\n"
            for field, abi_name in array_abi.items()
        )
        capture_output_arrays = "".join(
            f"    memcpy(output->{array_abi[field]}, state->{field}, "
            f"sizeof(output->{array_abi[field]}));\n"
            for field in ("ichLookup", "predictedSize", "rcSizeUnit", "useMidpoint")
        )
        apply_output_arrays = "".join(
            f"    memcpy(state->{field}, output->{array_abi[field]}, "
            f"sizeof(output->{array_abi[field]}));\n"
            for field in ("ichLookup", "predictedSize", "rcSizeUnit", "useMidpoint")
        )

        overlay = source_dir / "dsc_cicd_overlay.c"
        overlay.write_text(
            "#include <stdint.h>\n#include <stdio.h>\n#include <stdlib.h>\n"
            "#include <string.h>\n#include \"dsc_cicd_overlay.h\"\n"
            "#include \"dsc_cicd_rtl_abi.h\"\n"
            f"extern void {original}({caller_declarations});\n"
            "static int dsc_cicd_mode(void) {\n"
            "    const char *value = getenv(\"DSC_CICD_MODE\");\n"
            "    if (value && strcmp(value, \"SHADOW\") == 0) return 1;\n"
            "    if (value && strcmp(value, \"RTL_RETURN\") == 0) return 2;\n"
            "    return 0;\n}\n"
            + self.overlay_runtime_metrics_source()
            + "static void dsc_cicd_require_vld(const dsc_cfg_t *cfg, "
            "const dsc_state_t *state, int unit, const int *residuals, "
            "unsigned char **byte_in_p) {\n"
            "    if (!cfg || !state || !residuals || !byte_in_p || unit < 0 || "
            "unit >= DSC_CICD_VLD_UNITS || !state->quantTableLuma || "
            "!state->quantTableChroma || state->primaryQp < 0 || "
            "state->primaryQp > 31 || state->prevPrimaryQp < 0 || "
            "state->prevPrimaryQp > 31 || state->ichIndicesInGroup < 0 || "
            "state->ichIndicesInGroup > DSC_CICD_VLD_INDICES || "
            "state->unitsPerGroup < 0 || state->unitsPerGroup > DSC_CICD_VLD_UNITS) {\n"
            "        fprintf(stderr, \"unsupported VLD scalar domain: unit=%d\\n\", unit);\n"
            "        exit(2);\n    }\n"
            "    int cpnt = state->unitCType[unit];\n"
            "    int lane = state->unitSspMap[unit];\n"
            "    if (cpnt < 0 || cpnt >= DSC_CICD_VLD_UNITS || lane < 0 || "
            "lane >= DSC_CICD_VLD_UNITS) {\n"
            "        fprintf(stderr, \"unsupported VLD component/lane: cpnt=%d lane=%d\\n\", "
            "cpnt, lane);\n        exit(2);\n    }\n"
            "    const fifo_t *fifo = &state->shifter[lane];\n"
            "    if (!fifo->data || fifo->size <= 0 || fifo->size > "
            "DSC_CICD_VLD_FIFO_BYTES * 8 || (fifo->size & 7) != 0 || "
            "fifo->fullness < 0 || fifo->fullness > fifo->size || "
            "fifo->read_ptr < 0 || fifo->read_ptr >= fifo->size) {\n"
            "        fprintf(stderr, \"unsupported VLD FIFO domain: size=%d fullness=%d "
            "read_ptr=%d\\n\", fifo->size, fifo->fullness, fifo->read_ptr);\n"
            "        exit(2);\n    }\n}\n"
            "static void dsc_cicd_capture_vld(const dsc_state_t *state, int lane, "
            "const int *residuals, dsc_cicd_vld_output_t *output) {\n"
            "    memset(output, 0, sizeof(*output));\n"
            "    output->domain_valid = 1;\n"
            "    output->first_flat = state->firstFlat;\n"
            "    output->flatness_type = state->flatnessType;\n"
            "    output->ich_selected = state->ichSelected;\n"
            "    output->prev_first_flat = state->prevFirstFlat;\n"
            "    output->prev_ich_selected = state->prevIchSelected;\n"
            "    output->num_bits = state->numBits;\n"
            + capture_output_arrays
            + "    memcpy(output->quantized_residual, residuals, "
            "sizeof(output->quantized_residual));\n"
            "    output->fifo_lane = lane;\n"
            "    output->fifo_fullness = state->shifter[lane].fullness;\n"
            "    output->fifo_read_ptr = state->shifter[lane].read_ptr;\n"
            "}\n"
            "static void dsc_cicd_apply_vld(dsc_state_t *state, int *residuals, "
            "int lane, const dsc_cicd_vld_output_t *output) {\n"
            "    state->firstFlat = output->first_flat;\n"
            "    state->flatnessType = output->flatness_type;\n"
            "    state->ichSelected = output->ich_selected;\n"
            "    state->prevFirstFlat = output->prev_first_flat;\n"
            "    state->prevIchSelected = output->prev_ich_selected;\n"
            "    state->numBits = output->num_bits;\n"
            + apply_output_arrays
            + "    memcpy(residuals, output->quantized_residual, "
            "sizeof(output->quantized_residual));\n"
            "    state->shifter[lane].fullness = output->fifo_fullness;\n"
            "    state->shifter[lane].read_ptr = output->fifo_read_ptr;\n"
            "}\n"
            "static int dsc_cicd_vld_mismatch(const dsc_cicd_vld_output_t *left, "
            "const dsc_cicd_vld_output_t *right) {\n"
            "    return memcmp(left, right, sizeof(*left)) != 0;\n}\n"
            "static void dsc_cicd_print_vld_mismatch(int unit, int group, "
            "const dsc_cicd_vld_output_t *c, const dsc_cicd_vld_output_t *rtl) {\n"
            "    fprintf(stderr, \"C/RTL VLDUnit mismatch: unit=%d group=%d "
            "domain=%d/%d bits=%d/%d fifo=%d,%d/%d,%d "
            "ich=%d/%d prevIch=%d/%d first=%d/%d prevFirst=%d/%d "
            "residual=%d,%d,%d/%d,%d,%d\\n\", unit, group, "
            "c->domain_valid, rtl->domain_valid, c->num_bits, rtl->num_bits, "
            "c->fifo_fullness, c->fifo_read_ptr, rtl->fifo_fullness, "
            "rtl->fifo_read_ptr, c->ich_selected, rtl->ich_selected, "
            "c->prev_ich_selected, rtl->prev_ich_selected, c->first_flat, "
            "rtl->first_flat, c->prev_first_flat, rtl->prev_first_flat, "
            "c->quantized_residual[0], c->quantized_residual[1], "
            "c->quantized_residual[2], rtl->quantized_residual[0], "
            "rtl->quantized_residual[1], rtl->quantized_residual[2]);\n"
            "}\n"
            + f"void dsc_cicd_invoke({caller_declarations}) {{\n"
            f"    dsc_cicd_require_vld({config_parameter}, {state_parameter}, "
            f"{unit_parameter}, {residual_parameter}, {byte_parameter});\n"
            f"    int dsc_cicd_lane = {state_parameter}->unitSspMap[{unit_parameter}];\n"
            "    dsc_cicd_vld_input_t dsc_cicd_input;\n"
            "    dsc_cicd_vld_output_t dsc_cicd_c_output;\n"
            "    dsc_cicd_vld_output_t dsc_cicd_rtl_output;\n"
            "    memset(&dsc_cicd_input, 0, sizeof(dsc_cicd_input));\n"
            f"    dsc_cicd_input.unit = {unit_parameter};\n"
            + capture_input_scalars
            + capture_input_arrays
            + f"    dsc_cicd_input.qlevel_luma_primary = {state_parameter}->"
            f"quantTableLuma[{state_parameter}->primaryQp];\n"
            f"    dsc_cicd_input.qlevel_chroma_primary = {state_parameter}->"
            f"quantTableChroma[{state_parameter}->primaryQp];\n"
            f"    dsc_cicd_input.qlevel_luma_previous = {state_parameter}->"
            f"quantTableLuma[{state_parameter}->prevPrimaryQp];\n"
            f"    dsc_cicd_input.qlevel_chroma_previous = {state_parameter}->"
            f"quantTableChroma[{state_parameter}->prevPrimaryQp];\n"
            f"    memcpy(dsc_cicd_input.quantized_residual, {residual_parameter}, "
            "sizeof(dsc_cicd_input.quantized_residual));\n"
            f"    const fifo_t *dsc_cicd_fifo = &{state_parameter}->shifter[dsc_cicd_lane];\n"
            "    dsc_cicd_input.fifo_size = dsc_cicd_fifo->size;\n"
            "    dsc_cicd_input.fifo_fullness = dsc_cicd_fifo->fullness;\n"
            "    dsc_cicd_input.fifo_read_ptr = dsc_cicd_fifo->read_ptr;\n"
            "    memcpy(dsc_cicd_input.fifo_data, dsc_cicd_fifo->data, "
            "(size_t)dsc_cicd_fifo->size / 8);\n"
            f"    dsc_state_t dsc_cicd_c_state = *{state_parameter};\n"
            "    unsigned char dsc_cicd_c_fifo[DSC_CICD_VLD_FIFO_BYTES] = {0};\n"
            "    int dsc_cicd_c_residual[DSC_CICD_VLD_SAMPLES];\n"
            "    memcpy(dsc_cicd_c_fifo, dsc_cicd_input.fifo_data, "
            "sizeof(dsc_cicd_c_fifo));\n"
            "    memcpy(dsc_cicd_c_residual, dsc_cicd_input.quantized_residual, "
            "sizeof(dsc_cicd_c_residual));\n"
            "    dsc_cicd_c_state.shifter[dsc_cicd_lane].data = dsc_cicd_c_fifo;\n"
            f"    {original}({config_parameter}, &dsc_cicd_c_state, {unit_parameter}, "
            f"dsc_cicd_c_residual, {byte_parameter});\n"
            "    dsc_cicd_capture_vld(&dsc_cicd_c_state, dsc_cicd_lane, "
            "dsc_cicd_c_residual, &dsc_cicd_c_output);\n"
            "    int mode = dsc_cicd_mode();\n    dsc_cicd_note_call(mode);\n"
            "    if (mode == 0) {\n"
            f"        dsc_cicd_apply_vld({state_parameter}, {residual_parameter}, "
            "dsc_cicd_lane, &dsc_cicd_c_output);\n        return;\n    }\n"
            "    memset(&dsc_cicd_rtl_output, 0, sizeof(dsc_cicd_rtl_output));\n"
            "    dsc_cicd_rtl(&dsc_cicd_input, &dsc_cicd_rtl_output);\n"
            "    if (dsc_cicd_vld_mismatch(&dsc_cicd_c_output, "
            "&dsc_cicd_rtl_output)) {\n"
            "        ++dsc_cicd_mismatches;\n"
            "        if (dsc_cicd_mismatches <= 16)\n"
            f"            dsc_cicd_print_vld_mismatch({unit_parameter}, "
            f"{state_parameter}->groupCount, &dsc_cicd_c_output, "
            "&dsc_cicd_rtl_output);\n    }\n"
            "    if (mode == 2) {\n"
            f"        dsc_cicd_apply_vld({state_parameter}, {residual_parameter}, "
            "dsc_cicd_lane, &dsc_cicd_rtl_output);\n        return;\n    }\n"
            f"    dsc_cicd_apply_vld({state_parameter}, {residual_parameter}, "
            "dsc_cicd_lane, &dsc_cicd_c_output);\n}\n"
            + f"void {function_name}({caller_declarations}) {{\n"
            f"    dsc_cicd_invoke({alias_call});\n}}\n",
            encoding="utf-8",
        )

        bridge_assignments = [
            f"    dut.{unit_port} = static_cast<std::uint32_t>(input->unit);"
        ]
        bridge_assignments.extend(
            f"    dut.{config_ports[field]} = static_cast<std::uint32_t>(input->{abi_name});"
            for field, abi_name in config_abi.items()
        )
        bridge_assignments.extend(
            f"    dut.{state_ports[field]} = static_cast<std::uint32_t>(input->{abi_name});"
            for field, abi_name in state_abi.items()
        )
        for field, names in array_inputs.items():
            bridge_assignments.extend(
                f"    dut.{name} = static_cast<std::uint32_t>(input->{array_abi[field]}[{index}]);"
                for index, name in enumerate(names)
            )
        bridge_assignments.extend(
            f"    dut.{qlevel_ports[field]} = static_cast<std::uint32_t>(input->{abi_name});"
            for field, abi_name in qlevel_abi.items()
        )
        bridge_assignments.extend(
            f"    dut.{name} = static_cast<std::uint32_t>(input->quantized_residual[{index}]);"
            for index, name in enumerate(residual_inputs)
        )
        bridge_assignments.extend([
            f"    dut.{fifo_ports['size']} = static_cast<std::uint32_t>(input->fifo_size);",
            f"    dut.{fifo_ports['fullness']} = static_cast<std::uint32_t>(input->fifo_fullness);",
            f"    dut.{fifo_ports['read_ptr']} = static_cast<std::uint32_t>(input->fifo_read_ptr);",
        ])
        bridge_assignments.extend(
            f"    dut.{name} = input->fifo_data[{index}];"
            for index, name in enumerate(fifo_data_ports)
        )

        bridge_outputs = [
            "    output->domain_valid = static_cast<std::int32_t>(dut.domain_valid);",
            f"    output->first_flat = static_cast<std::int32_t>(dut.{state_outputs['firstFlat']});",
            f"    output->flatness_type = static_cast<std::int32_t>(dut.{state_outputs['flatnessType']});",
            f"    output->ich_selected = static_cast<std::int32_t>(dut.{state_outputs['ichSelected']});",
            f"    output->prev_first_flat = static_cast<std::int32_t>(dut.{state_outputs['prevFirstFlat']});",
            f"    output->prev_ich_selected = static_cast<std::int32_t>(dut.{state_outputs['prevIchSelected']});",
            f"    output->num_bits = static_cast<std::int32_t>(dut.{state_outputs['numBits']});",
        ]
        for field, names in array_outputs.items():
            bridge_outputs.extend(
                f"    output->{array_abi[field]}[{index}] = "
                f"static_cast<std::int32_t>(dut.{name});"
                for index, name in enumerate(names)
            )
        bridge_outputs.extend(
            f"    output->quantized_residual[{index}] = "
            f"static_cast<std::int32_t>(dut.{name});"
            for index, name in enumerate(residual_outputs)
        )
        bridge_outputs.extend([
            f"    output->fifo_lane = static_cast<std::int32_t>(dut.{fifo_outputs['lane']});",
            f"    output->fifo_fullness = static_cast<std::int32_t>(dut.{fifo_outputs['fullness']});",
            f"    output->fifo_read_ptr = static_cast<std::int32_t>(dut.{fifo_outputs['read_ptr']});",
        ])
        bridge = source_dir / "rtl_bridge.cpp"
        bridge.write_text(
            "#include <cstdint>\n#include \"verilated.h\"\n"
            "#include \"dsc_cicd_rtl_abi.h\"\n"
            f"#include \"V{safe_identifier(module)}.h\"\n"
            "double sc_time_stamp() { return 0.0; }\n"
            "extern \"C\" void dsc_cicd_rtl(const dsc_cicd_vld_input_t *input, "
            "dsc_cicd_vld_output_t *output) {\n"
            f"    static V{safe_identifier(module)} dut;\n"
            + "\n".join(bridge_assignments)
            + "\n    dut.eval();\n"
            + "\n".join(bridge_outputs)
            + "\n}\n",
            encoding="utf-8",
        )
        main = source_dir / "dsc_cicd_main.c"
        main.write_text(
            "#include <stdio.h>\nextern int dsc_cicd_original_main(int, char **);\n"
            "int main(int argc, char **argv) { return dsc_cicd_original_main(argc, argv); }\n",
            encoding="utf-8",
        )
        rtl_bindings = [
            unit_parameter,
            *[f"{config_parameter}->{field}" for field in config_abi],
            *[f"{state_parameter}->{field}" for field in state_abi],
            *[
                f"{state_parameter}->{field}[{index}]"
                for field, size in expected_array_sizes.items()
                for index in range(size)
            ],
            f"{state_parameter}->quantTableLuma[primaryQp]",
            f"{state_parameter}->quantTableChroma[primaryQp]",
            f"{state_parameter}->quantTableLuma[prevPrimaryQp]",
            f"{state_parameter}->quantTableChroma[prevPrimaryQp]",
            *[f"{residual_parameter}[{index}]" for index in range(samples)],
            *[
                f"{state_parameter}->shifter[unitSspMap[unit]].{field}"
                for field in ("size", "fullness", "read_ptr")
            ],
            *[
                f"{state_parameter}->shifter[unitSspMap[unit]].data[{index}]"
                for index in range(fifo_bytes)
            ],
        ]
        return {
            "header": header,
            "abi": abi,
            "overlay": overlay,
            "bridge": bridge,
            "main": main,
            "candidate": candidate_sv,
            "composition": {
                "status": "PASS",
                "adapter_kind": "explicit_bounded_vld_unit_transition",
                "caller_parameter_count": len(parameters),
                "rtl_input_count": len(inputs),
                "frozen_input_ports": [str(port.get("name")) for port in inputs],
                "rtl_bindings": rtl_bindings,
                "state_outputs": [str(port.get("name")) for port in outputs],
                "selected_fifo_snapshot_bytes": fifo_bytes,
                "prefix_unroll_bound": prefix_bits,
                "rtl_return_controls_complete_vld_write_footprint": True,
                "c_oracle_uses_private_state_fifo_and_residuals": True,
                "byte_input_pointer_is_not_dereferenced_by_rtl": True,
                "residual_symbol_alias_routes_to_dispatcher": True,
            },
        }

    def write_bounded_vld_group_decode_transition_overlay_sources(
        self,
        contract: dict[str, Any],
        source_dir: pathlib.Path,
        module: str,
        candidate_sv: pathlib.Path,
    ) -> dict[str, Any]:
        """Bind a complete decoder group state image to composed Verilated RTL."""
        semantics = contract.get("semantics", {}) or {}
        constants = semantics.get("constants", {}) or {}
        bindings = semantics.get("bindings", {}) or {}
        units = int(constants.get("max_units", 0))
        samples = int(constants.get("samples_per_unit", 0))
        indices = int(constants.get("max_ich_indices", 0))
        fifo_bytes = int(constants.get("fifo_bytes", 0))
        stream_bytes = int(constants.get("stream_window_bytes", 0))
        if (units, samples, indices, fifo_bytes, stream_bytes) != (4, 3, 6, 17, 33):
            raise RuntimeError("bounded VLD group constants are incomplete")

        mux = bindings.get("mux", {}) or {}
        vld = bindings.get("vld", {}) or {}
        residual_inputs = [
            [str(value) for value in row]
            for row in bindings.get("residual_input_ports", [])
        ]
        residual_outputs = [
            [str(value) for value in row]
            for row in bindings.get("residual_output_ports", [])
        ]
        direct_inputs = {
            str(key): str(value)
            for key, value in (bindings.get("direct_input_ports", {}) or {}).items()
        }
        direct_outputs = {
            str(key): str(value)
            for key, value in (bindings.get("direct_output_ports", {}) or {}).items()
        }
        lanes = [dict(value) for value in mux.get("fifo_lanes", [])]
        vld_config = {
            str(key): str(value)
            for key, value in (vld.get("config_ports", {}) or {}).items()
        }
        vld_state = {
            str(key): str(value)
            for key, value in (vld.get("state_ports", {}) or {}).items()
        }
        vld_arrays = {
            str(key): [str(value) for value in values]
            for key, values in (vld.get("array_input_ports", {}) or {}).items()
        }
        vld_state_outputs = {
            str(key): str(value)
            for key, value in (vld.get("state_output_ports", {}) or {}).items()
        }
        vld_array_outputs = {
            str(key): [str(value) for value in values]
            for key, values in (vld.get("array_output_ports", {}) or {}).items()
        }
        qlevels = {
            str(key): str(value)
            for key, value in (vld.get("qlevel_ports", {}) or {}).items()
        }
        if (
            len(lanes) != units
            or len(residual_inputs) != units
            or len(residual_outputs) != units
            or any(len(row) != samples for row in residual_inputs + residual_outputs)
            or set(direct_inputs) != {
                "rcb_bits", "bufferFullness", "errorOccurred", "groupCountLine"
            }
            or set(direct_outputs) != {
                "prevPrimaryQp", "codedGroupSize", "bufferFullness",
                "errorOccurred", "origIsFlat", "groupCountLine",
            }
        ):
            raise RuntimeError("bounded VLD group bindings are incomplete")

        ports = [
            port for port in (contract.get("interface", {}) or {}).get("ports", [])
            if isinstance(port, dict)
        ]
        inputs = [port for port in ports if port.get("direction") == "input"]
        outputs = [port for port in ports if port.get("direction") == "output"]
        input_names = [str(port.get("name")) for port in inputs]
        output_names = [str(port.get("name")) for port in outputs]
        if len(inputs) != 205 or len(outputs) != 136 or "domain_valid" not in output_names:
            raise RuntimeError("bounded VLD group flattened interface changed")

        parameters = self.function_parameters(contract)
        parameter_by_name = {
            str(parameter.get("name")): parameter for parameter in parameters
        }
        config_parameter = str(bindings.get("config_parameter", ""))
        state_parameter = str(bindings.get("state_parameter", ""))
        byte_parameter = str(bindings.get("byte_pointer_parameter", ""))
        if set(parameter_by_name) != {config_parameter, state_parameter, byte_parameter}:
            raise RuntimeError("bounded VLD group native ABI is incomplete")
        if not all(parameter_is_pointer(parameter_by_name[name]) for name in parameter_by_name):
            raise RuntimeError("bounded VLD group native ABI must be pointer-only")

        identifier = re.compile(r"^[A-Za-z_][A-Za-z0-9_]*$")
        if not all(identifier.fullmatch(value) for value in [
            config_parameter, state_parameter, byte_parameter, *input_names, *output_names,
        ]):
            raise RuntimeError("bounded VLD group contains an invalid identifier")
        parameter_specs = [
            f"{str(parameter.get('type', 'int')).strip()} {parameter.get('name')}"
            for parameter in parameters
        ]
        parameter_names = [str(parameter.get("name")) for parameter in parameters]
        caller_declarations = ", ".join(parameter_specs)
        alias_call = ", ".join(parameter_names)
        function_name = str(contract_function(contract).get("name"))
        original = function_name + "_original"

        input_captures: dict[str, str] = {}
        output_captures: dict[str, str] = {"domain_valid": "1"}
        output_applies: dict[str, str] = {}
        fifo_data_apply_guards: dict[str, tuple[str, int]] = {}

        mux_word_port = str(mux["mux_word_size_port"])
        num_ssps_port = str(mux["num_ssps_port"])
        post_port = str(mux["post_mux_num_bits_port"])
        post_output = str(mux["post_mux_num_bits_output_port"])
        mux_word_field = str(mux["mux_word_size_field"])
        num_ssps_field = str(mux["num_ssps_field"])
        post_field = str(mux["post_mux_num_bits_field"])
        max_se_field = str(mux["max_se_size_field"])
        shifter_field = str(mux["shifter_field"])
        input_captures[mux_word_port] = f"{config_parameter}->{mux_word_field}"
        input_captures[num_ssps_port] = f"{state_parameter}->{num_ssps_field}"
        input_captures[post_port] = f"{state_parameter}->{post_field}"
        for index, port in enumerate(mux["max_se_size_ports"]):
            input_captures[str(port)] = f"{state_parameter}->{max_se_field}[{index}]"
        for index, port in enumerate(mux["stream_byte_ports"]):
            input_captures[str(port)] = f"dsc_cicd_stream[{index}]"
        output_captures[post_output] = f"state->{post_field}"
        output_applies[post_output] = f"state->{post_field}"
        fifo_scalar_pairs = (
            ("size_port", "size_output_port", "size"),
            ("fullness_port", "fullness_output_port", "fullness"),
            ("read_ptr_port", "read_ptr_output_port", "read_ptr"),
            ("write_ptr_port", "write_ptr_output_port", "write_ptr"),
            ("max_fullness_port", "max_fullness_output_port", "max_fullness"),
            ("byte_ctr_port", "byte_ctr_output_port", "byte_ctr"),
        )
        for lane_index, lane in enumerate(lanes):
            for input_key, output_key, field in fifo_scalar_pairs:
                input_captures[str(lane[input_key])] = (
                    f"{state_parameter}->{shifter_field}[{lane_index}].{field}"
                )
                output_captures[str(lane[output_key])] = (
                    f"state->{shifter_field}[{lane_index}].{field}"
                )
                output_applies[str(lane[output_key])] = (
                    f"state->{shifter_field}[{lane_index}].{field}"
                )
            for byte_index, (input_port, output_port) in enumerate(zip(
                lane["data_input_ports"], lane["data_output_ports"]
            )):
                input_captures[str(input_port)] = (
                    f"({byte_index} < {state_parameter}->{shifter_field}[{lane_index}].size / 8 "
                    f"? {state_parameter}->{shifter_field}[{lane_index}].data[{byte_index}] : 0)"
                )
                output_captures[str(output_port)] = (
                    f"state->{shifter_field}[{lane_index}].data[{byte_index}]"
                )
                output_applies[str(output_port)] = (
                    f"state->{shifter_field}[{lane_index}].data[{byte_index}]"
                )
                fifo_data_apply_guards[str(output_port)] = (
                    str(lane["size_output_port"]), byte_index
                )

        for field, port in vld_config.items():
            input_captures[port] = f"{config_parameter}->{field}"
        for field, port in vld_state.items():
            input_captures[port] = f"{state_parameter}->{field}"
        for field, names in vld_arrays.items():
            for index, port in enumerate(names):
                input_captures[port] = f"{state_parameter}->{field}[{index}]"
        qlevel_expressions = {
            "luma_primary": (
                f"{state_parameter}->quantTableLuma[{state_parameter}->primaryQp]"
            ),
            "chroma_primary": (
                f"{state_parameter}->quantTableChroma[{state_parameter}->primaryQp]"
            ),
            "luma_previous": (
                f"{state_parameter}->quantTableLuma[{state_parameter}->prevPrimaryQp]"
            ),
            "chroma_previous": (
                f"{state_parameter}->quantTableChroma[{state_parameter}->prevPrimaryQp]"
            ),
        }
        for field, port in qlevels.items():
            input_captures[port] = qlevel_expressions[field]
        for unit in range(units):
            for sample in range(samples):
                input_captures[residual_inputs[unit][sample]] = (
                    f"{state_parameter}->quantizedResidual[{unit}][{sample}]"
                )
                output_captures[residual_outputs[unit][sample]] = (
                    f"state->quantizedResidual[{unit}][{sample}]"
                )
                output_applies[residual_outputs[unit][sample]] = (
                    f"state->quantizedResidual[{unit}][{sample}]"
                )
        for field, port in vld_state_outputs.items():
            output_captures[port] = f"state->{field}"
            output_applies[port] = f"state->{field}"
        for field, names in vld_array_outputs.items():
            for index, port in enumerate(names):
                output_captures[port] = f"state->{field}[{index}]"
                output_applies[port] = f"state->{field}[{index}]"
        for field, port in direct_inputs.items():
            owner = config_parameter if field == "rcb_bits" else state_parameter
            input_captures[port] = f"{owner}->{field}"
        for field, port in direct_outputs.items():
            output_captures[port] = f"state->{field}"
            output_applies[port] = f"state->{field}"
        if set(input_captures) != set(input_names):
            missing = sorted(set(input_names) - set(input_captures))
            extra = sorted(set(input_captures) - set(input_names))
            raise RuntimeError(f"bounded VLD group input mapping mismatch: {missing}/{extra}")
        if set(output_captures) != set(output_names) or set(output_applies) != (
            set(output_names) - {"domain_valid"}
        ):
            raise RuntimeError("bounded VLD group output mapping is incomplete")

        abi = source_dir / "dsc_cicd_rtl_abi.h"
        abi.write_text(
            "#ifndef DSC_CICD_RTL_ABI_H\n#define DSC_CICD_RTL_ABI_H\n"
            "#include <stdint.h>\n"
            f"#define DSC_CICD_VLD_GROUP_UNITS {units}\n"
            f"#define DSC_CICD_VLD_GROUP_FIFO_BYTES {fifo_bytes}\n"
            f"#define DSC_CICD_VLD_GROUP_STREAM_BYTES {stream_bytes}\n"
            "typedef struct {\n"
            + "".join(f"    int32_t {name};\n" for name in input_names)
            + "} dsc_cicd_vld_group_input_t;\n"
            "typedef struct {\n"
            + "".join(f"    int32_t {name};\n" for name in output_names)
            + "} dsc_cicd_vld_group_output_t;\n"
            "#ifdef __cplusplus\nextern \"C\" {\n#endif\n"
            "void dsc_cicd_rtl(const dsc_cicd_vld_group_input_t *input, "
            "dsc_cicd_vld_group_output_t *output);\n"
            "#ifdef __cplusplus\n}\n#endif\n#endif\n",
            encoding="utf-8",
        )
        header = source_dir / "dsc_cicd_overlay.h"
        header.write_text(
            "#ifndef DSC_CICD_OVERLAY_H\n#define DSC_CICD_OVERLAY_H\n"
            "#include \"dsc_types.h\"\n"
            f"void dsc_cicd_invoke({caller_declarations});\n#endif\n",
            encoding="utf-8",
        )
        capture_input_source = "".join(
            f"    dsc_cicd_input.{name} = (int32_t)({input_captures[name]});\n"
            for name in input_names
        )
        capture_output_source = "".join(
            f"    output->{name} = (int32_t)({output_captures[name]});\n"
            for name in output_names
        )
        apply_output_source = "".join(
            (
                f"    if ({fifo_data_apply_guards[name][1]} < "
                f"output->{fifo_data_apply_guards[name][0]} / 8) "
                f"{output_applies[name]} = output->{name};\n"
                if name in fifo_data_apply_guards
                else f"    {output_applies[name]} = output->{name};\n"
            )
            for name in output_names if name != "domain_valid"
        )

        overlay = source_dir / "dsc_cicd_overlay.c"
        overlay.write_text(
            "#include <stdint.h>\n#include <stdio.h>\n#include <stdlib.h>\n"
            "#include <string.h>\n#include \"dsc_cicd_overlay.h\"\n"
            "#include \"dsc_cicd_rtl_abi.h\"\n"
            f"extern void {original}({caller_declarations});\n"
            "static int dsc_cicd_mode(void) {\n"
            "    const char *value = getenv(\"DSC_CICD_MODE\");\n"
            "    if (value && strcmp(value, \"SHADOW\") == 0) return 1;\n"
            "    if (value && strcmp(value, \"RTL_RETURN\") == 0) return 2;\n"
            "    return 0;\n}\n"
            + self.overlay_runtime_metrics_source()
            + "static void dsc_cicd_require_vld_group(const dsc_cfg_t *cfg, "
            "const dsc_state_t *state, unsigned char **byte_in_p) {\n"
            "    if (!cfg || !state || !byte_in_p || !*byte_in_p || "
            "!state->quantTableLuma || !state->quantTableChroma || "
            "state->unitsPerGroup < 3 || state->unitsPerGroup > "
            "DSC_CICD_VLD_GROUP_UNITS || state->numSsps < 0 || "
            "state->numSsps > DSC_CICD_VLD_GROUP_UNITS || "
            "(cfg->mux_word_size != 48 && cfg->mux_word_size != 64) || "
            "state->primaryQp < 0 || state->primaryQp > 31 || "
            "state->prevPrimaryQp < 0 || state->prevPrimaryQp > 31 || "
            "state->ichIndicesInGroup < 0 || state->ichIndicesInGroup > 6) {\n"
            "        fprintf(stderr, \"unsupported VLDGroup scalar domain\\n\");\n"
            "        exit(2);\n    }\n"
            "    for (int unit = 0; unit < DSC_CICD_VLD_GROUP_UNITS; ++unit) {\n"
            "        if (state->unitCType[unit] < 0 || state->unitCType[unit] >= 4 || "
            "state->unitSspMap[unit] < 0 || state->unitSspMap[unit] >= 4) {\n"
            "            fprintf(stderr, \"unsupported VLDGroup unit map\\n\");\n"
            "            exit(2);\n        }\n"
            "        const fifo_t *fifo = &state->shifter[unit];\n"
            "        if (!fifo->data || fifo->size <= 0 || fifo->size > "
            "DSC_CICD_VLD_GROUP_FIFO_BYTES * 8 || (fifo->size & 7) || "
            "fifo->fullness < 0 || fifo->fullness > fifo->size || "
            "fifo->read_ptr < 0 || fifo->read_ptr >= fifo->size || "
            "fifo->write_ptr < 0 || fifo->write_ptr >= fifo->size) {\n"
            "            fprintf(stderr, \"unsupported VLDGroup FIFO domain: lane=%d\\n\", unit);\n"
            "            exit(2);\n        }\n    }\n"
            "    for (int index = 0; index < 6; ++index) {\n"
            "        if (state->ichIndexUnitMap[index] < 0 || "
            "state->ichIndexUnitMap[index] >= 4) {\n"
            "            fprintf(stderr, \"unsupported VLDGroup ICH map\\n\");\n"
            "            exit(2);\n        }\n    }\n}\n"
            "static void dsc_cicd_capture_output(const dsc_state_t *state, "
            "dsc_cicd_vld_group_output_t *output) {\n"
            "    memset(output, 0, sizeof(*output));\n"
            + capture_output_source
            + "}\n"
            "static void dsc_cicd_apply_output(dsc_state_t *state, "
            "dsc_cicd_vld_group_output_t const *output) {\n"
            + apply_output_source
            + "}\n"
            + f"void dsc_cicd_invoke({caller_declarations}) {{\n"
            f"    dsc_cicd_require_vld_group({config_parameter}, {state_parameter}, "
            f"{byte_parameter});\n"
            "    uint8_t dsc_cicd_stream[DSC_CICD_VLD_GROUP_STREAM_BYTES] = {0};\n"
            f"    int dsc_cicd_base = {state_parameter}->{post_field} >> 3;\n"
            "    for (int index = 0; index < DSC_CICD_VLD_GROUP_STREAM_BYTES; ++index) {\n"
            f"        if (index + 1 < DSC_CICD_VLD_GROUP_STREAM_BYTES || "
            f"({state_parameter}->{post_field} & 7))\n"
            f"            dsc_cicd_stream[index] = (*{byte_parameter})[dsc_cicd_base + index];\n"
            "    }\n"
            "    dsc_cicd_vld_group_input_t dsc_cicd_input;\n"
            "    dsc_cicd_vld_group_output_t dsc_cicd_c_output;\n"
            "    dsc_cicd_vld_group_output_t dsc_cicd_rtl_output;\n"
            "    memset(&dsc_cicd_input, 0, sizeof(dsc_cicd_input));\n"
            + capture_input_source
            + f"    dsc_state_t dsc_cicd_c_state = *{state_parameter};\n"
            "    unsigned char dsc_cicd_c_fifo[DSC_CICD_VLD_GROUP_UNITS]"
            "[DSC_CICD_VLD_GROUP_FIFO_BYTES] = {{0}};\n"
            "    for (int lane = 0; lane < DSC_CICD_VLD_GROUP_UNITS; ++lane) {\n"
            f"        memcpy(dsc_cicd_c_fifo[lane], {state_parameter}->{shifter_field}[lane].data, "
            f"(size_t){state_parameter}->{shifter_field}[lane].size / 8);\n"
            f"        dsc_cicd_c_state.{shifter_field}[lane].data = dsc_cicd_c_fifo[lane];\n"
            "    }\n"
            f"    unsigned char *dsc_cicd_c_byte = *{byte_parameter};\n"
            f"    {original}({config_parameter}, &dsc_cicd_c_state, &dsc_cicd_c_byte);\n"
            "    dsc_cicd_capture_output(&dsc_cicd_c_state, &dsc_cicd_c_output);\n"
            "    int mode = dsc_cicd_mode();\n    dsc_cicd_note_call(mode);\n"
            "    if (mode == 0) {\n"
            f"        dsc_cicd_apply_output({state_parameter}, &dsc_cicd_c_output);\n"
            "        return;\n    }\n"
            "    memset(&dsc_cicd_rtl_output, 0, sizeof(dsc_cicd_rtl_output));\n"
            "    dsc_cicd_rtl(&dsc_cicd_input, &dsc_cicd_rtl_output);\n"
            "    int mismatch = memcmp(&dsc_cicd_c_output, &dsc_cicd_rtl_output, "
            "sizeof(dsc_cicd_c_output)) != 0;\n"
            "    if (mismatch) {\n        ++dsc_cicd_mismatches;\n"
            "        if (dsc_cicd_mismatches <= 16)\n"
            "            fprintf(stderr, \"C/RTL VLDGroup mismatch: group=%d "
            "bits=%d/%d fullness=%d/%d domain=%d\\n\", "
            f"{state_parameter}->groupCount, dsc_cicd_c_output."
            f"{vld_state_outputs['numBits']}, dsc_cicd_rtl_output."
            f"{vld_state_outputs['numBits']}, dsc_cicd_c_output."
            f"{direct_outputs['bufferFullness']}, dsc_cicd_rtl_output."
            f"{direct_outputs['bufferFullness']}, dsc_cicd_rtl_output.domain_valid);\n"
            "    }\n"
            "    if (mode == 2 && dsc_cicd_rtl_output.domain_valid) {\n"
            f"        dsc_cicd_apply_output({state_parameter}, &dsc_cicd_rtl_output);\n"
            "        return;\n    }\n"
            f"    dsc_cicd_apply_output({state_parameter}, &dsc_cicd_c_output);\n"
            "}\n"
            + f"void {function_name}({caller_declarations}) {{\n"
            f"    dsc_cicd_invoke({alias_call});\n}}\n",
            encoding="utf-8",
        )

        bridge_assignments = [
            f"    dut.{name} = static_cast<std::uint32_t>(input->{name});"
            for name in input_names
        ]
        bridge_outputs = [
            f"    output->{name} = static_cast<std::int32_t>(dut.{name});"
            for name in output_names
        ]
        bridge = source_dir / "rtl_bridge.cpp"
        bridge.write_text(
            "#include <cstdint>\n#include \"verilated.h\"\n"
            "#include \"dsc_cicd_rtl_abi.h\"\n"
            f"#include \"V{safe_identifier(module)}.h\"\n"
            "double sc_time_stamp() { return 0.0; }\n"
            "extern \"C\" void dsc_cicd_rtl("
            "const dsc_cicd_vld_group_input_t *input, "
            "dsc_cicd_vld_group_output_t *output) {\n"
            f"    static V{safe_identifier(module)} dut;\n"
            + "\n".join(bridge_assignments)
            + "\n    dut.eval();\n"
            + "\n".join(bridge_outputs)
            + "\n}\n",
            encoding="utf-8",
        )
        main = source_dir / "dsc_cicd_main.c"
        main.write_text(
            "#include <stdio.h>\nextern int dsc_cicd_original_main(int, char **);\n"
            "int main(int argc, char **argv) { return dsc_cicd_original_main(argc, argv); }\n",
            encoding="utf-8",
        )
        return {
            "header": header,
            "abi": abi,
            "overlay": overlay,
            "bridge": bridge,
            "main": main,
            "candidate": candidate_sv,
            "composition": {
                "status": "PASS",
                "adapter_kind": "explicit_bounded_vld_group_decode_transition",
                "caller_parameter_count": len(parameters),
                "rtl_input_count": len(inputs),
                "rtl_output_count": len(outputs),
                "frozen_input_ports": input_names,
                "rtl_bindings": [input_captures[name] for name in input_names],
                "state_outputs": output_names,
                "source_order_child_sequence": [
                    "ProcessGroupDec", "VLDUnit[0]", "VLDUnit[1]",
                    "VLDUnit[2]", "VLDUnit[3]",
                ],
                "rtl_return_controls_complete_vld_group_write_footprint": True,
                "c_oracle_uses_private_state_and_four_fifo_images": True,
                "byte_input_pointer_is_read_only": True,
                "residual_symbol_alias_routes_to_dispatcher": True,
            },
        }

    def write_raster_color_transform_overlay_sources(
        self,
        contract: dict[str, Any],
        source_dir: pathlib.Path,
        module: str,
        candidate_sv: pathlib.Path,
    ) -> dict[str, Any]:
        """Iterate a Verilated three-channel kernel over the source raster bounds."""
        semantics = contract.get("semantics", {}) or {}
        constants = semantics.get("constants", {}) or {}
        bindings = semantics.get("bindings", {}) or {}
        direction = str(bindings.get("direction", ""))
        input_ports = [str(value) for value in bindings.get("input_ports", [])]
        output_ports = [str(value) for value in bindings.get("output_ports", [])]
        input_fields = [str(value) for value in bindings.get("input_plane_fields", [])]
        output_fields = [str(value) for value in bindings.get("output_plane_fields", [])]
        bits_port = str(bindings.get("bits_port", ""))
        if (
            direction not in {"rgb_to_ycocg", "ycocg_to_rgb"}
            or len(input_ports) != 3
            or len(output_ports) != 3
            or len(input_fields) != 3
            or len(output_fields) != 3
            or int(constants.get("channel_count", 0)) != 3
            or not constants.get("reduce_chroma_16bpc")
        ):
            raise RuntimeError("raster color transform bindings are incomplete")
        ports = [
            port for port in (contract.get("interface", {}) or {}).get("ports", [])
            if isinstance(port, dict)
        ]
        inputs = [port for port in ports if port.get("direction") == "input"]
        outputs = [port for port in ports if port.get("direction") == "output"]
        if (
            [str(port.get("name")) for port in inputs] != [bits_port, *input_ports]
            or {str(port.get("name")) for port in outputs}
            != {"domain_valid", *output_ports}
        ):
            raise RuntimeError("raster color transform interface changed")

        parameters = self.function_parameters(contract)
        parameter_by_name = {
            str(parameter.get("name")): parameter for parameter in parameters
        }
        input_parameter = str(bindings.get("input_parameter", ""))
        output_parameter = str(bindings.get("output_parameter", ""))
        config_parameter = str(bindings.get("config_parameter", ""))
        if set(parameter_by_name) != {
            input_parameter, output_parameter, config_parameter
        } or not all(parameter_is_pointer(value) for value in parameter_by_name.values()):
            raise RuntimeError("raster color transform native ABI changed")
        parameter_specs = [
            f"{str(parameter.get('type', 'int')).strip()} {parameter.get('name')}"
            for parameter in parameters
        ]
        parameter_names = [str(parameter.get("name")) for parameter in parameters]
        caller_declarations = ", ".join(parameter_specs)
        alias_call = ", ".join(parameter_names)
        function_name = str(contract_function(contract).get("name"))
        original = function_name + "_original"
        input_union = "rgb" if direction == "rgb_to_ycocg" else "yuv"
        output_union = "yuv" if direction == "rgb_to_ycocg" else "rgb"
        input_access = [
            f"{input_parameter}->data.{input_union}.{field}[row][column]"
            for field in input_fields
        ]
        output_access = [
            f"{output_parameter}->data.{output_union}.{field}[row][column]"
            for field in output_fields
        ]

        abi = source_dir / "dsc_cicd_rtl_abi.h"
        abi.write_text(
            "#ifndef DSC_CICD_RTL_ABI_H\n#define DSC_CICD_RTL_ABI_H\n"
            "#include <stdint.h>\n#ifdef __cplusplus\nextern \"C\" {\n#endif\n"
            "void dsc_cicd_rtl(int32_t bits, int32_t input_0, int32_t input_1, "
            "int32_t input_2, int32_t *domain_valid, int32_t *output_0, "
            "int32_t *output_1, int32_t *output_2);\n"
            "#ifdef __cplusplus\n}\n#endif\n#endif\n",
            encoding="utf-8",
        )
        header = source_dir / "dsc_cicd_overlay.h"
        header.write_text(
            "#ifndef DSC_CICD_OVERLAY_H\n#define DSC_CICD_OVERLAY_H\n"
            "#include \"dsc_utils.h\"\n"
            f"void dsc_cicd_invoke({caller_declarations});\n#endif\n",
            encoding="utf-8",
        )
        save_lines = "".join(
            f"            saved[position * 3 + {index}] = {access};\n"
            for index, access in enumerate(output_access)
        )
        capture_lines = "".join(
            f"            c_result[position * 3 + {index}] = {access};\n"
            for index, access in enumerate(output_access)
        )
        restore_lines = "".join(
            f"            {access} = saved[position * 3 + {index}];\n"
            for index, access in enumerate(output_access)
        )
        apply_lines = "".join(
            f"            {access} = selected[position * 3 + {index}];\n"
            for index, access in enumerate(output_access)
        )
        rtl_call_inputs = ", ".join(input_access)
        overlay = source_dir / "dsc_cicd_overlay.c"
        overlay.write_text(
            "#include <stdint.h>\n#include <stdio.h>\n#include <stdlib.h>\n"
            "#include <string.h>\n#include \"dsc_cicd_overlay.h\"\n"
            "#include \"dsc_cicd_rtl_abi.h\"\n"
            f"extern void {original}({caller_declarations});\n"
            "static int dsc_cicd_mode(void) {\n"
            "    const char *value = getenv(\"DSC_CICD_MODE\");\n"
            "    if (value && strcmp(value, \"SHADOW\") == 0) return 1;\n"
            "    if (value && strcmp(value, \"RTL_RETURN\") == 0) return 2;\n"
            "    return 0;\n}\n"
            + self.overlay_runtime_metrics_source()
            + f"void dsc_cicd_invoke({caller_declarations}) {{\n"
            f"    if (!{input_parameter} || !{output_parameter} || !{config_parameter} || "
            f"{input_parameter} == {output_parameter} || {input_parameter}->w != "
            f"{output_parameter}->w || {input_parameter}->h != {output_parameter}->h || "
            f"{input_parameter}->bits < 8 || {input_parameter}->bits > 16 || "
            f"{config_parameter}->xstart < 0 || {config_parameter}->ystart < 0 || "
            f"{config_parameter}->slice_width < 0 || {config_parameter}->slice_height < 0) {{\n"
            "        fprintf(stderr, \"unsupported raster color-transform domain\\n\");\n"
            "        exit(2);\n    }\n"
            f"    int x_begin = {config_parameter}->xstart;\n"
            f"    int y_begin = {config_parameter}->ystart;\n"
            f"    int x_end = x_begin + {config_parameter}->slice_width;\n"
            f"    int y_end = y_begin + {config_parameter}->slice_height;\n"
            f"    if (x_end > {input_parameter}->w) x_end = {input_parameter}->w;\n"
            f"    if (y_end > {input_parameter}->h) y_end = {input_parameter}->h;\n"
            "    if (x_end < x_begin) x_end = x_begin;\n"
            "    if (y_end < y_begin) y_end = y_begin;\n"
            "    size_t width = (size_t)(x_end - x_begin);\n"
            "    size_t height = (size_t)(y_end - y_begin);\n"
            "    size_t pixels = width * height;\n"
            "    size_t elements = (pixels ? pixels : 1) * 3;\n"
            "    int *saved = (int *)malloc(elements * sizeof(int));\n"
            "    int *c_result = (int *)malloc(elements * sizeof(int));\n"
            "    int *rtl_result = (int *)malloc(elements * sizeof(int));\n"
            "    if (!saved || !c_result || !rtl_result) {\n"
            "        fprintf(stderr, \"color-transform oracle allocation failed\\n\");\n"
            "        exit(2);\n    }\n"
            "    for (int row = y_begin; row < y_end; ++row) {\n"
            "        for (int column = x_begin; column < x_end; ++column) {\n"
            "            size_t position = (size_t)(row - y_begin) * width + "
            "(size_t)(column - x_begin);\n"
            + save_lines
            + "        }\n    }\n"
            f"    {original}({alias_call});\n"
            "    for (int row = y_begin; row < y_end; ++row) {\n"
            "        for (int column = x_begin; column < x_end; ++column) {\n"
            "            size_t position = (size_t)(row - y_begin) * width + "
            "(size_t)(column - x_begin);\n"
            + capture_lines
            + restore_lines
            + "        }\n    }\n"
            "    int mode = dsc_cicd_mode();\n"
            "    dsc_cicd_note_call(0);\n"
            "    int rtl_all_valid = 1;\n"
            "    if (mode != 0) {\n"
            "        for (int row = y_begin; row < y_end; ++row) {\n"
            "            for (int column = x_begin; column < x_end; ++column) {\n"
            "                size_t position = (size_t)(row - y_begin) * width + "
            "(size_t)(column - x_begin);\n"
            "                int32_t domain_valid = 0, out_0 = 0, out_1 = 0, out_2 = 0;\n"
            f"                dsc_cicd_rtl({input_parameter}->bits, {rtl_call_inputs}, "
            "&domain_valid, &out_0, &out_1, &out_2);\n"
            "                ++dsc_cicd_rtl_invocations;\n"
            "                rtl_result[position * 3 + 0] = out_0;\n"
            "                rtl_result[position * 3 + 1] = out_1;\n"
            "                rtl_result[position * 3 + 2] = out_2;\n"
            "                if (!domain_valid) rtl_all_valid = 0;\n"
            "                if (!domain_valid || out_0 != c_result[position * 3 + 0] || "
            "out_1 != c_result[position * 3 + 1] || "
            "out_2 != c_result[position * 3 + 2]) ++dsc_cicd_mismatches;\n"
            "            }\n        }\n    }\n"
            "    const int *selected = "
            "(mode == 2 && rtl_all_valid) ? rtl_result : c_result;\n"
            "    for (int row = y_begin; row < y_end; ++row) {\n"
            "        for (int column = x_begin; column < x_end; ++column) {\n"
            "            size_t position = (size_t)(row - y_begin) * width + "
            "(size_t)(column - x_begin);\n"
            + apply_lines
            + "        }\n    }\n"
            "    free(rtl_result);\n    free(c_result);\n    free(saved);\n}\n"
            + f"void {function_name}({caller_declarations}) {{\n"
            f"    dsc_cicd_invoke({alias_call});\n}}\n",
            encoding="utf-8",
        )

        bridge = source_dir / "rtl_bridge.cpp"
        bridge.write_text(
            "#include <cstdint>\n#include \"verilated.h\"\n"
            "#include \"dsc_cicd_rtl_abi.h\"\n"
            f"#include \"V{safe_identifier(module)}.h\"\n"
            "double sc_time_stamp() { return 0.0; }\n"
            "extern \"C\" void dsc_cicd_rtl(int32_t bits, int32_t input_0, "
            "int32_t input_1, int32_t input_2, int32_t *domain_valid, "
            "int32_t *output_0, int32_t *output_1, int32_t *output_2) {\n"
            f"    static V{safe_identifier(module)} dut;\n"
            f"    dut.{bits_port} = static_cast<std::uint32_t>(bits);\n"
            f"    dut.{input_ports[0]} = static_cast<std::uint32_t>(input_0);\n"
            f"    dut.{input_ports[1]} = static_cast<std::uint32_t>(input_1);\n"
            f"    dut.{input_ports[2]} = static_cast<std::uint32_t>(input_2);\n"
            "    dut.eval();\n"
            "    *domain_valid = static_cast<std::int32_t>(dut.domain_valid);\n"
            f"    *output_0 = static_cast<std::int32_t>(dut.{output_ports[0]});\n"
            f"    *output_1 = static_cast<std::int32_t>(dut.{output_ports[1]});\n"
            f"    *output_2 = static_cast<std::int32_t>(dut.{output_ports[2]});\n"
            "}\n",
            encoding="utf-8",
        )
        main = source_dir / "dsc_cicd_main.c"
        main.write_text(
            "#include <stdio.h>\nextern int dsc_cicd_original_main(int, char **);\n"
            "int main(int argc, char **argv) { return dsc_cicd_original_main(argc, argv); }\n",
            encoding="utf-8",
        )
        return {
            "header": header,
            "abi": abi,
            "overlay": overlay,
            "bridge": bridge,
            "main": main,
            "candidate": candidate_sv,
            "composition": {
                "status": "PASS",
                "adapter_kind": "iterated_raster_color_transform_transition",
                "caller_parameter_count": len(parameters),
                "rtl_input_count": len(inputs),
                "frozen_input_ports": [str(port.get("name")) for port in inputs],
                "rtl_bindings": [
                    f"{input_parameter}->bits",
                    *[
                        f"{input_parameter}->data.{input_union}.{field}[row][column]"
                        for field in input_fields
                    ],
                ],
                "state_outputs": [str(port.get("name")) for port in outputs],
                "iteration_adapter_invokes_rtl_per_active_pixel": True,
                "rtl_return_controls_every_active_output_pixel": True,
                "original_c_writes_are_saved_and_restored_before_commit": True,
                "input_and_output_picture_alias_is_rejected": True,
            },
        }

    def write_bounded_rate_control_decode_transition_overlay_sources(
        self,
        contract: dict[str, Any],
        source_dir: pathlib.Path,
        module: str,
        candidate_sv: pathlib.Path,
    ) -> dict[str, Any]:
        """Bind decoder rate-control scalar state around three child stages."""
        semantics = contract.get("semantics", {}) or {}
        constants = semantics.get("constants", {}) or {}
        bindings = semantics.get("bindings", {}) or {}
        ranges = int(constants.get("num_buf_ranges", 0))
        units = int(constants.get("max_units", 0))
        samples = int(constants.get("samples_per_unit", 0))
        stages = int(constants.get("max_remove_stages", 0))
        if (ranges, units, samples, stages) != (15, 4, 3, 3):
            raise RuntimeError("bounded rate-control constants are incomplete")
        argument_ports = {
            str(key): str(value)
            for key, value in (bindings.get("argument_ports", {}) or {}).items()
        }
        config_ports = {
            str(key): str(value)
            for key, value in (bindings.get("config_ports", {}) or {}).items()
        }
        state_ports = {
            str(key): str(value)
            for key, value in (bindings.get("state_ports", {}) or {}).items()
        }
        depth_ports = [str(value) for value in bindings.get("depth_ports", [])]
        predicted_ports = [
            str(value) for value in bindings.get("predicted_ports", [])
        ]
        rc_size_ports = [str(value) for value in bindings.get("rc_size_ports", [])]
        use_midpoint_ports = [
            str(value) for value in bindings.get("use_midpoint_ports", [])
        ]
        threshold_ports = [
            str(value) for value in bindings.get("threshold_ports", [])
        ]
        range_ports = {
            str(key): [str(value) for value in row]
            for key, row in (bindings.get("range_ports", {}) or {}).items()
        }
        state_output_ports = {
            str(key): str(value)
            for key, value in (bindings.get("state_output_ports", {}) or {}).items()
        }
        expected_config = {
            "bits_per_component", "bits_per_pixel", "chunk_size",
            "dsc_version_minor", "initial_xmit_delay", "native_420", "native_422",
            "rc_edge_factor", "rc_model_size", "rc_quant_incr_limit0",
            "rc_quant_incr_limit1", "rc_tgt_offset_hi", "rc_tgt_offset_lo",
            "rcb_bits", "vbr_enable",
        }
        expected_state = {
            "bitSaveMode", "bitsClamped", "bpgFracAccum", "bufferFullness",
            "chunkCount", "chunkPixelTimes", "codedGroupSize", "errorOccurred",
            "firstFlat", "ichSelected", "isEncoder", "mppState", "numBitsChunk",
            "pixelCount", "prevQp", "prevRange", "rcSizeGroup", "sliceWidth",
            "stQp", "unitsPerGroup", "vPos",
        }
        expected_outputs = {
            "bitSaveMode", "bitsClamped", "bpgFracAccum", "bufferFullness",
            "chunkCount", "chunkPixelTimes", "errorOccurred", "mppState",
            "numBitsChunk", "pixelCount", "prevQp", "prevRange",
            "rcSizeGroup", "stQp",
        }
        if (
            len(argument_ports) != 5 or set(config_ports) != expected_config
            or set(state_ports) != expected_state
            or set(state_output_ports) != expected_outputs
            or len(depth_ports) != 2 or len(predicted_ports) != units
            or len(rc_size_ports) != units or len(use_midpoint_ports) != units
            or len(threshold_ports) != ranges - 1
            or set(range_ports) != {
                "range_min_qp", "range_max_qp", "range_bpg_offset"
            }
            or any(len(row) != ranges for row in range_ports.values())
        ):
            raise RuntimeError("bounded rate-control bindings are incomplete")
        ports = [
            port for port in (contract.get("interface", {}) or {}).get("ports", [])
            if isinstance(port, dict)
        ]
        inputs = [port for port in ports if port.get("direction") == "input"]
        outputs = [port for port in ports if port.get("direction") == "output"]
        expected_inputs = {
            *argument_ports.values(), *config_ports.values(), *state_ports.values(),
            *depth_ports, *predicted_ports, *rc_size_ports, *use_midpoint_ports,
            *threshold_ports, *[value for row in range_ports.values() for value in row],
        }
        expected_output_ports = {"domain_valid", *state_output_ports.values()}
        if (
            {str(port.get("name")) for port in inputs} != expected_inputs
            or {str(port.get("name")) for port in outputs} != expected_output_ports
        ):
            raise RuntimeError("bounded rate-control ports changed")
        parameters = self.function_parameters(contract)
        parameter_by_name = {
            str(parameter.get("name")): parameter for parameter in parameters
        }
        config_parameter = str(bindings.get("config_parameter", ""))
        state_parameter = str(bindings.get("state_parameter", ""))
        scalar_parameters = [
            str(parameter.get("name"))
            for parameter in parameters if not parameter_is_pointer(parameter)
        ]
        if (
            set(parameter_by_name) != {
                config_parameter, state_parameter, *scalar_parameters
            }
            or len(scalar_parameters) != 5
            or not parameter_is_pointer(parameter_by_name[config_parameter])
            or not parameter_is_pointer(parameter_by_name[state_parameter])
        ):
            raise RuntimeError("bounded rate-control native ABI is incomplete")
        throttle_parameter, bpg_parameter, group_count_parameter, scale_parameter, group_size_parameter = scalar_parameters
        identifier = re.compile(r"^[A-Za-z_][A-Za-z0-9_]*$")
        identifiers = {
            config_parameter, state_parameter, *scalar_parameters,
            *expected_inputs, *expected_output_ports,
        }
        if not all(identifier.fullmatch(value) for value in identifiers):
            raise RuntimeError("bounded rate-control contains invalid identifiers")
        parameter_specs = [
            f"{str(parameter.get('type', 'int')).strip()} {parameter.get('name')}"
            for parameter in parameters
        ]
        parameter_names = [str(parameter.get("name")) for parameter in parameters]
        caller_declarations = ", ".join(parameter_specs)
        alias_call = ", ".join(parameter_names)
        function_name = str(contract_function(contract).get("name"))
        original = function_name + "_original"

        argument_abi = {name: safe_identifier(name) for name in scalar_parameters}
        config_abi = {field: "cfg_" + safe_identifier(field) for field in config_ports}
        state_abi = {field: "state_" + safe_identifier(field) for field in state_ports}
        output_abi = {field: safe_identifier(field) for field in state_output_ports}
        abi = source_dir / "dsc_cicd_rtl_abi.h"
        abi.write_text(
            "#ifndef DSC_CICD_RTL_ABI_H\n#define DSC_CICD_RTL_ABI_H\n"
            "#include <stdint.h>\n"
            f"#define DSC_CICD_RC_RANGES {ranges}\n"
            f"#define DSC_CICD_RC_THRESHOLDS {ranges - 1}\n"
            f"#define DSC_CICD_RC_UNITS {units}\n"
            "typedef struct {\n"
            + "".join(
                f"    int32_t {argument_abi[name]};\n" for name in scalar_parameters
            )
            + "".join(
                f"    int32_t {config_abi[field]};\n" for field in config_ports
            )
            + "".join(
                f"    int32_t {state_abi[field]};\n" for field in state_ports
            )
            + "    int32_t cpnt_bit_depth[2];\n"
            "    int32_t predicted_size[DSC_CICD_RC_UNITS];\n"
            "    int32_t rc_size_unit[DSC_CICD_RC_UNITS];\n"
            "    int32_t use_midpoint[DSC_CICD_RC_UNITS];\n"
            "    int32_t rc_buf_thresh[DSC_CICD_RC_THRESHOLDS];\n"
            "    int32_t range_min_qp[DSC_CICD_RC_RANGES];\n"
            "    int32_t range_max_qp[DSC_CICD_RC_RANGES];\n"
            "    int32_t range_bpg_offset[DSC_CICD_RC_RANGES];\n"
            "} dsc_cicd_rate_control_input_t;\n"
            "typedef struct {\n    int32_t domain_valid;\n"
            + "".join(
                f"    int32_t {output_abi[field]};\n"
                for field in state_output_ports
            )
            + "} dsc_cicd_rate_control_output_t;\n"
            "#ifdef __cplusplus\nextern \"C\" {\n#endif\n"
            "void dsc_cicd_rtl(const dsc_cicd_rate_control_input_t *input, "
            "dsc_cicd_rate_control_output_t *output);\n"
            "#ifdef __cplusplus\n}\n#endif\n#endif\n",
            encoding="utf-8",
        )
        header = source_dir / "dsc_cicd_overlay.h"
        header.write_text(
            "#ifndef DSC_CICD_OVERLAY_H\n#define DSC_CICD_OVERLAY_H\n"
            "#include \"dsc_types.h\"\n"
            f"void dsc_cicd_invoke({caller_declarations});\n#endif\n",
            encoding="utf-8",
        )
        capture_lines = "".join(
            f"    output->{output_abi[field]} = state->{field};\n"
            for field in state_output_ports
        )
        apply_lines = "".join(
            f"    state->{field} = output->{output_abi[field]};\n"
            for field in state_output_ports
        )
        input_scalar_lines = "".join(
            f"    dsc_cicd_input.{argument_abi[name]} = {name};\n"
            for name in scalar_parameters
        ) + "".join(
            f"    dsc_cicd_input.{config_abi[field]} = {config_parameter}->{field};\n"
            for field in config_ports
        ) + "".join(
            f"    dsc_cicd_input.{state_abi[field]} = {state_parameter}->{field};\n"
            for field in state_ports
        )
        overlay = source_dir / "dsc_cicd_overlay.c"
        overlay.write_text(
            "#include <stdint.h>\n#include <stdio.h>\n#include <stdlib.h>\n"
            "#include <string.h>\n#include \"dsc_cicd_overlay.h\"\n"
            "#include \"dsc_cicd_rtl_abi.h\"\n"
            f"extern void {original}({caller_declarations});\n"
            "static int dsc_cicd_mode(void) {\n"
            "    const char *value = getenv(\"DSC_CICD_MODE\");\n"
            "    if (value && strcmp(value, \"SHADOW\") == 0) return 1;\n"
            "    if (value && strcmp(value, \"RTL_RETURN\") == 0) return 2;\n"
            "    return 0;\n}\n"
            + self.overlay_runtime_metrics_source()
            + "static void dsc_cicd_require_rate_control(const dsc_cfg_t *cfg, "
            "const dsc_state_t *state, int group_count, int group_size) {\n"
            "    if (!cfg || !state || state->isEncoder != 0 || group_count < 0 || "
            "group_size < 1 || group_size > 3 || state->unitsPerGroup < 3 || "
            "state->unitsPerGroup > 4 || state->prevRange < 0 || "
            "state->prevRange >= 15 || state->sliceWidth <= 0 || "
            "state->chunkPixelTimes < 0 || state->chunkPixelTimes >= state->sliceWidth || "
            "cfg->dsc_version_minor < 1 || cfg->dsc_version_minor > 2 || "
            "(cfg->native_420 != 0 && cfg->native_420 != 1) || "
            "(cfg->native_422 != 0 && cfg->native_422 != 1) || "
            "(cfg->native_420 && cfg->native_422) || "
            "state->cpntBitDepth[0] < 8 || state->cpntBitDepth[0] > 16 || "
            "state->cpntBitDepth[1] < 8 || state->cpntBitDepth[1] > 16) {\n"
            "        fprintf(stderr, \"unsupported RateControl decode domain: "
            "group=%d size=%d\\n\", group_count, group_size);\n"
            "        exit(2);\n    }\n}\n"
            "static void dsc_cicd_capture_rate_control(const dsc_state_t *state, "
            "dsc_cicd_rate_control_output_t *output) {\n"
            "    memset(output, 0, sizeof(*output));\n"
            "    output->domain_valid = 1;\n"
            + capture_lines
            + "}\n"
            "static void dsc_cicd_apply_rate_control(dsc_state_t *state, "
            "const dsc_cicd_rate_control_output_t *output) {\n"
            + apply_lines
            + "}\n"
            "static int dsc_cicd_rate_control_mismatch("
            "const dsc_cicd_rate_control_output_t *left, "
            "const dsc_cicd_rate_control_output_t *right) {\n"
            "    return memcmp(left, right, sizeof(*left)) != 0;\n}\n"
            "static void dsc_cicd_print_rate_control_mismatch(int group_count, "
            "int group_size, const dsc_cicd_rate_control_output_t *c, "
            "const dsc_cicd_rate_control_output_t *rtl) {\n"
            "    fprintf(stderr, \"C/RTL RateControl decode mismatch: group=%d "
            "size=%d domain=%d/%d qp=%d/%d fullness=%d/%d range=%d/%d "
            "pixel=%d/%d error=%d/%d\\n\", group_count, group_size, "
            f"c->domain_valid, rtl->domain_valid, c->{output_abi['stQp']}, "
            f"rtl->{output_abi['stQp']}, c->{output_abi['bufferFullness']}, "
            f"rtl->{output_abi['bufferFullness']}, c->{output_abi['prevRange']}, "
            f"rtl->{output_abi['prevRange']}, c->{output_abi['pixelCount']}, "
            f"rtl->{output_abi['pixelCount']}, c->{output_abi['errorOccurred']}, "
            f"rtl->{output_abi['errorOccurred']});\n}}\n"
            + f"void dsc_cicd_invoke({caller_declarations}) {{\n"
            f"    if (!{state_parameter}) {{ fprintf(stderr, \"null RateControl state\\n\"); exit(2); }}\n"
            f"    if ({state_parameter}->isEncoder != 0) {{\n"
            f"        {original}({alias_call});\n        return;\n    }}\n"
            f"    dsc_cicd_require_rate_control({config_parameter}, {state_parameter}, "
            f"{group_count_parameter}, {group_size_parameter});\n"
            "    dsc_cicd_rate_control_input_t dsc_cicd_input;\n"
            "    dsc_cicd_rate_control_output_t dsc_cicd_c_output;\n"
            "    dsc_cicd_rate_control_output_t dsc_cicd_rtl_output;\n"
            "    memset(&dsc_cicd_input, 0, sizeof(dsc_cicd_input));\n"
            + input_scalar_lines
            + f"    dsc_cicd_input.cpnt_bit_depth[0] = {state_parameter}->cpntBitDepth[0];\n"
            f"    dsc_cicd_input.cpnt_bit_depth[1] = {state_parameter}->cpntBitDepth[1];\n"
            f"    memcpy(dsc_cicd_input.predicted_size, {state_parameter}->predictedSize, "
            "sizeof(dsc_cicd_input.predicted_size));\n"
            f"    memcpy(dsc_cicd_input.rc_size_unit, {state_parameter}->rcSizeUnit, "
            "sizeof(dsc_cicd_input.rc_size_unit));\n"
            f"    memcpy(dsc_cicd_input.use_midpoint, {state_parameter}->useMidpoint, "
            "sizeof(dsc_cicd_input.use_midpoint));\n"
            f"    memcpy(dsc_cicd_input.rc_buf_thresh, {config_parameter}->rc_buf_thresh, "
            "sizeof(dsc_cicd_input.rc_buf_thresh));\n"
            "    for (int range = 0; range < DSC_CICD_RC_RANGES; ++range) {\n"
            f"        dsc_cicd_input.range_min_qp[range] = {config_parameter}->"
            "rc_range_parameters[range].range_min_qp;\n"
            f"        dsc_cicd_input.range_max_qp[range] = {config_parameter}->"
            "rc_range_parameters[range].range_max_qp;\n"
            f"        dsc_cicd_input.range_bpg_offset[range] = {config_parameter}->"
            "rc_range_parameters[range].range_bpg_offset;\n    }\n"
            f"    dsc_state_t dsc_cicd_c_state = *{state_parameter};\n"
            f"    {original}({config_parameter}, &dsc_cicd_c_state, "
            f"{throttle_parameter}, {bpg_parameter}, {group_count_parameter}, "
            f"{scale_parameter}, {group_size_parameter});\n"
            "    dsc_cicd_capture_rate_control(&dsc_cicd_c_state, &dsc_cicd_c_output);\n"
            "    int mode = dsc_cicd_mode();\n    dsc_cicd_note_call(mode);\n"
            "    if (mode == 0) {\n"
            f"        dsc_cicd_apply_rate_control({state_parameter}, &dsc_cicd_c_output);\n"
            "        return;\n    }\n"
            "    memset(&dsc_cicd_rtl_output, 0, sizeof(dsc_cicd_rtl_output));\n"
            "    dsc_cicd_rtl(&dsc_cicd_input, &dsc_cicd_rtl_output);\n"
            "    if (dsc_cicd_rate_control_mismatch(&dsc_cicd_c_output, "
            "&dsc_cicd_rtl_output)) {\n"
            "        ++dsc_cicd_mismatches;\n"
            "        if (dsc_cicd_mismatches <= 16)\n"
            f"            dsc_cicd_print_rate_control_mismatch({group_count_parameter}, "
            f"{group_size_parameter}, &dsc_cicd_c_output, &dsc_cicd_rtl_output);\n"
            "    }\n"
            "    if (mode == 2) {\n"
            f"        dsc_cicd_apply_rate_control({state_parameter}, &dsc_cicd_rtl_output);\n"
            "        return;\n    }\n"
            f"    dsc_cicd_apply_rate_control({state_parameter}, &dsc_cicd_c_output);\n"
            "}\n"
            + f"void {function_name}({caller_declarations}) {{\n"
            f"    dsc_cicd_invoke({alias_call});\n}}\n",
            encoding="utf-8",
        )

        bridge_assignments = []
        bridge_assignments.extend(
            f"    dut.{argument_ports[name]} = static_cast<std::uint32_t>(input->{argument_abi[name]});"
            for name in scalar_parameters
        )
        bridge_assignments.extend(
            f"    dut.{config_ports[field]} = static_cast<std::uint32_t>(input->{config_abi[field]});"
            for field in config_ports
        )
        bridge_assignments.extend(
            f"    dut.{state_ports[field]} = static_cast<std::uint32_t>(input->{state_abi[field]});"
            for field in state_ports
        )
        bridge_assignments.extend(
            f"    dut.{port} = static_cast<std::uint32_t>(input->cpnt_bit_depth[{index}]);"
            for index, port in enumerate(depth_ports)
        )
        bridge_assignments.extend(
            f"    dut.{port} = static_cast<std::uint32_t>(input->predicted_size[{index}]);"
            for index, port in enumerate(predicted_ports)
        )
        bridge_assignments.extend(
            f"    dut.{port} = static_cast<std::uint32_t>(input->rc_size_unit[{index}]);"
            for index, port in enumerate(rc_size_ports)
        )
        bridge_assignments.extend(
            f"    dut.{port} = static_cast<std::uint32_t>(input->use_midpoint[{index}]);"
            for index, port in enumerate(use_midpoint_ports)
        )
        bridge_assignments.extend(
            f"    dut.{port} = static_cast<std::uint32_t>(input->rc_buf_thresh[{index}]);"
            for index, port in enumerate(threshold_ports)
        )
        for field, abi_field in (
            ("range_min_qp", "range_min_qp"),
            ("range_max_qp", "range_max_qp"),
            ("range_bpg_offset", "range_bpg_offset"),
        ):
            bridge_assignments.extend(
                f"    dut.{port} = static_cast<std::uint32_t>(input->{abi_field}[{index}]);"
                for index, port in enumerate(range_ports[field])
            )
        bridge_outputs = [
            "    output->domain_valid = static_cast<std::int32_t>(dut.domain_valid);",
            *[
                f"    output->{output_abi[field]} = static_cast<std::int32_t>(dut.{state_output_ports[field]});"
                for field in state_output_ports
            ],
        ]
        bridge = source_dir / "rtl_bridge.cpp"
        bridge.write_text(
            "#include <cstdint>\n#include \"verilated.h\"\n"
            "#include \"dsc_cicd_rtl_abi.h\"\n"
            f"#include \"V{safe_identifier(module)}.h\"\n"
            "double sc_time_stamp() { return 0.0; }\n"
            "extern \"C\" void dsc_cicd_rtl("
            "const dsc_cicd_rate_control_input_t *input, "
            "dsc_cicd_rate_control_output_t *output) {\n"
            f"    static V{safe_identifier(module)} dut;\n"
            + "\n".join(bridge_assignments)
            + "\n    dut.eval();\n"
            + "\n".join(bridge_outputs)
            + "\n}\n",
            encoding="utf-8",
        )
        main = source_dir / "dsc_cicd_main.c"
        main.write_text(
            "#include <stdio.h>\nextern int dsc_cicd_original_main(int, char **);\n"
            "int main(int argc, char **argv) { return dsc_cicd_original_main(argc, argv); }\n",
            encoding="utf-8",
        )
        rtl_bindings = [
            *scalar_parameters,
            *[f"{config_parameter}->{field}" for field in config_ports],
            *[f"{state_parameter}->{field}" for field in state_ports],
            f"{state_parameter}->cpntBitDepth[0]",
            f"{state_parameter}->cpntBitDepth[1]",
            *[f"{state_parameter}->predictedSize[{index}]" for index in range(units)],
            *[f"{state_parameter}->rcSizeUnit[{index}]" for index in range(units)],
            *[f"{state_parameter}->useMidpoint[{index}]" for index in range(units)],
            *[f"{config_parameter}->rc_buf_thresh[{index}]" for index in range(ranges - 1)],
            *[
                f"{config_parameter}->rc_range_parameters[{index}].{field}"
                for field in ("range_min_qp", "range_max_qp", "range_bpg_offset")
                for index in range(ranges)
            ],
        ]
        return {
            "header": header, "abi": abi, "overlay": overlay,
            "bridge": bridge, "main": main, "candidate": candidate_sv,
            "composition": {
                "status": "PASS",
                "adapter_kind": "explicit_bounded_rate_control_decode_transition",
                "caller_parameter_count": len(parameters),
                "rtl_input_count": len(inputs),
                "frozen_input_ports": [str(port.get("name")) for port in inputs],
                "rtl_bindings": rtl_bindings,
                "state_outputs": [str(port.get("name")) for port in outputs],
                "decoder_only_specialization_is_explicit": True,
                "encoder_calls_bypass_rtl_and_remain_original_c": True,
                "three_remove_bits_stages_are_hash_bound_and_ordered": True,
                "decoder_specialization_has_no_chunk_memory_write": True,
                "c_oracle_uses_private_embedded_state": True,
                "rtl_return_controls_complete_rate_control_scalar_footprint": True,
                "residual_symbol_alias_routes_to_dispatcher": True,
            },
        }

    def write_bounded_prediction_decode_transition_overlay_sources(
        self,
        contract: dict[str, Any],
        source_dir: pathlib.Path,
        module: str,
        candidate_sv: pathlib.Path,
    ) -> dict[str, Any]:
        """Bind decoder reconstruction to four explicit line-write slots."""
        semantics = contract.get("semantics", {}) or {}
        constants = semantics.get("constants", {}) or {}
        bindings = semantics.get("bindings", {}) or {}
        units = int(constants.get("max_units", 0))
        samples = int(constants.get("samples_per_unit", 0))
        components = int(constants.get("component_count", 0))
        padding_left = int(constants.get("padding_left", 0))
        pred_block_size = int(constants.get("pred_block_size", 0))
        pt_map = int(constants.get("pt_map", -1))
        pt_left = int(constants.get("pt_left", -1))
        pt_block = int(constants.get("pt_block", -1))
        if (
            units, samples, components, padding_left, pred_block_size,
            pt_map, pt_left, pt_block
        ) != (4, 3, 4, 5, 3, 0, 1, 2):
            raise RuntimeError("bounded prediction decoder constants are incomplete")

        argument_ports = {
            str(key): str(value)
            for key, value in (bindings.get("argument_ports", {}) or {}).items()
        }
        config_ports = {
            str(key): str(value)
            for key, value in (bindings.get("config_ports", {}) or {}).items()
        }
        state_ports = {
            str(key): str(value)
            for key, value in (bindings.get("state_ports", {}) or {}).items()
        }
        depth_ports = [str(value) for value in bindings.get("depth_ports", [])]
        unit_type_ports = [str(value) for value in bindings.get("unit_type_ports", [])]
        unit_start_ports = [str(value) for value in bindings.get("unit_start_ports", [])]
        midpoint_ports = [str(value) for value in bindings.get("midpoint_ports", [])]
        left_ports = [str(value) for value in bindings.get("left_ports", [])]
        residual_ports = [
            [str(value) for value in row]
            for row in bindings.get("residual_ports", [])
        ]
        qlevel_ports = {
            str(key): str(value)
            for key, value in (bindings.get("qlevel_ports", {}) or {}).items()
        }
        prediction_port = str(bindings.get("prediction_port", ""))
        previous_ports = [
            [str(value) for value in row]
            for row in bindings.get("previous_line_ports", [])
        ]
        current_a_ports = [
            str(value) for value in bindings.get("current_a_ports", [])
        ]
        current_block_ports = [
            str(value) for value in bindings.get("current_block_ports", [])
        ]
        write_ports = [
            {str(key): str(value) for key, value in slot.items()}
            for slot in bindings.get("write_ports", [])
        ]
        if (
            len(argument_ports) != 4
            or set(config_ports) != {"native_420", "dsc_version_minor"}
            or set(state_ports) != {"isEncoder", "unitsPerGroup"}
            or len(depth_ports) != components
            or len(unit_type_ports) != units
            or len(unit_start_ports) != units
            or len(midpoint_ports) != units
            or len(left_ports) != components
            or len(residual_ports) != units
            or any(len(row) != samples for row in residual_ports)
            or set(qlevel_ports) != {"luma", "chroma"}
            or not prediction_port
            or len(previous_ports) != units
            or any(len(row) != 6 for row in previous_ports)
            or len(current_a_ports) != units
            or len(current_block_ports) != units
            or len(write_ports) != units
            or any(
                set(slot) != {"enable", "component", "index", "value"}
                for slot in write_ports
            )
        ):
            raise RuntimeError("bounded prediction decoder bindings are incomplete")

        ports = [
            port for port in (contract.get("interface", {}) or {}).get("ports", [])
            if isinstance(port, dict)
        ]
        inputs = [port for port in ports if port.get("direction") == "input"]
        outputs = [port for port in ports if port.get("direction") == "output"]
        expected_inputs = {
            *argument_ports.values(), *config_ports.values(), *state_ports.values(),
            *depth_ports, *unit_type_ports, *unit_start_ports, *midpoint_ports,
            *left_ports, *[value for row in residual_ports for value in row],
            *qlevel_ports.values(), prediction_port,
            *[value for row in previous_ports for value in row],
            *current_a_ports, *current_block_ports,
        }
        expected_outputs = {
            "domain_valid",
            *[value for slot in write_ports for value in slot.values()],
        }
        if (
            {str(port.get("name")) for port in inputs} != expected_inputs
            or {str(port.get("name")) for port in outputs} != expected_outputs
        ):
            raise RuntimeError("bounded prediction decoder ports changed")

        parameters = self.function_parameters(contract)
        parameter_by_name = {
            str(parameter.get("name")): parameter for parameter in parameters
        }
        config_parameter = str(bindings.get("config_parameter", ""))
        state_parameter = str(bindings.get("state_parameter", ""))
        hpos_parameter = str(bindings.get("horizontal_parameter", ""))
        vpos_parameter = str(bindings.get("vertical_parameter", ""))
        sample_parameter = str(bindings.get("sample_count_parameter", ""))
        qp_parameter = str(bindings.get("qp_parameter", ""))
        if set(parameter_by_name) != {
            config_parameter, state_parameter, hpos_parameter, vpos_parameter,
            sample_parameter, qp_parameter,
        }:
            raise RuntimeError("bounded prediction decoder native ABI is incomplete")
        if (
            not parameter_is_pointer(parameter_by_name[config_parameter])
            or not parameter_is_pointer(parameter_by_name[state_parameter])
            or any(
                parameter_is_pointer(parameter_by_name[name])
                for name in (hpos_parameter, vpos_parameter, sample_parameter, qp_parameter)
            )
        ):
            raise RuntimeError("bounded prediction decoder pointer/scalar ABI changed")
        identifier = re.compile(r"^[A-Za-z_][A-Za-z0-9_]*$")
        identifiers = {
            config_parameter, state_parameter, hpos_parameter, vpos_parameter,
            sample_parameter, qp_parameter, *expected_inputs, *expected_outputs,
        }
        if not all(identifier.fullmatch(value) for value in identifiers):
            raise RuntimeError("bounded prediction decoder contains invalid identifiers")

        parameter_specs = [
            f"{str(parameter.get('type', 'int')).strip()} {parameter.get('name')}"
            for parameter in parameters
        ]
        parameter_names = [str(parameter.get("name")) for parameter in parameters]
        caller_declarations = ", ".join(parameter_specs)
        alias_call = ", ".join(parameter_names)
        function_name = str(contract_function(contract).get("name"))
        original = function_name + "_original"

        abi = source_dir / "dsc_cicd_rtl_abi.h"
        abi.write_text(
            "#ifndef DSC_CICD_RTL_ABI_H\n#define DSC_CICD_RTL_ABI_H\n"
            "#include <stdint.h>\n"
            f"#define DSC_CICD_PRED_UNITS {units}\n"
            f"#define DSC_CICD_PRED_SAMPLES {samples}\n"
            f"#define DSC_CICD_PRED_COMPONENTS {components}\n"
            "#define DSC_CICD_PRED_PREV_TAPS 6\n"
            "typedef struct {\n"
            "    int32_t hpos;\n    int32_t vpos;\n"
            "    int32_t sample_count;\n    int32_t qp;\n"
            "    int32_t cfg_native_420;\n    int32_t cfg_dsc_version_minor;\n"
            "    int32_t is_encoder;\n    int32_t units_per_group;\n"
            "    int32_t cpnt_bit_depth[DSC_CICD_PRED_COMPONENTS];\n"
            "    int32_t unit_c_type[DSC_CICD_PRED_UNITS];\n"
            "    int32_t unit_start_hpos[DSC_CICD_PRED_UNITS];\n"
            "    int32_t use_midpoint[DSC_CICD_PRED_UNITS];\n"
            "    int32_t left_recon[DSC_CICD_PRED_COMPONENTS];\n"
            "    int32_t quantized_residual[DSC_CICD_PRED_UNITS]"
            "[DSC_CICD_PRED_SAMPLES];\n"
            "    int32_t qlevel_luma;\n    int32_t qlevel_chroma;\n"
            "    int32_t prev_line_prediction;\n"
            "    int32_t prev_line[DSC_CICD_PRED_UNITS]"
            "[DSC_CICD_PRED_PREV_TAPS];\n"
            "    int32_t curr_a[DSC_CICD_PRED_UNITS];\n"
            "    int32_t curr_block[DSC_CICD_PRED_UNITS];\n"
            "} dsc_cicd_prediction_input_t;\n"
            "typedef struct {\n"
            "    int32_t domain_valid;\n"
            "    int32_t write_enable[DSC_CICD_PRED_UNITS];\n"
            "    int32_t write_component[DSC_CICD_PRED_UNITS];\n"
            "    int32_t write_index[DSC_CICD_PRED_UNITS];\n"
            "    int32_t write_value[DSC_CICD_PRED_UNITS];\n"
            "} dsc_cicd_prediction_output_t;\n"
            "#ifdef __cplusplus\nextern \"C\" {\n#endif\n"
            "void dsc_cicd_rtl(const dsc_cicd_prediction_input_t *input, "
            "dsc_cicd_prediction_output_t *output);\n"
            "#ifdef __cplusplus\n}\n#endif\n#endif\n",
            encoding="utf-8",
        )
        header = source_dir / "dsc_cicd_overlay.h"
        header.write_text(
            "#ifndef DSC_CICD_OVERLAY_H\n#define DSC_CICD_OVERLAY_H\n"
            "#include \"dsc_types.h\"\n"
            f"void dsc_cicd_invoke({caller_declarations});\n#endif\n",
            encoding="utf-8",
        )

        overlay = source_dir / "dsc_cicd_overlay.c"
        overlay.write_text(
            "#include <stdint.h>\n#include <stdio.h>\n#include <stdlib.h>\n"
            "#include <string.h>\n#include \"dsc_cicd_overlay.h\"\n"
            "#include \"dsc_cicd_rtl_abi.h\"\n"
            f"extern void {original}({caller_declarations});\n"
            "static int dsc_cicd_mode(void) {\n"
            "    const char *value = getenv(\"DSC_CICD_MODE\");\n"
            "    if (value && strcmp(value, \"SHADOW\") == 0) return 1;\n"
            "    if (value && strcmp(value, \"RTL_RETURN\") == 0) return 2;\n"
            "    return 0;\n}\n"
            + self.overlay_runtime_metrics_source()
            + "static int dsc_cicd_map_qlevel_c(const dsc_cfg_t *cfg, "
            "const dsc_state_t *state, int qp, int cpnt) {\n"
            "    int qlevel;\n"
            "    if ((cpnt % 3) == 0) qlevel = state->quantTableLuma[qp];\n"
            "    else if (cfg->native_420 && cpnt == 1) "
            "qlevel = state->quantTableLuma[qp];\n"
            "    else {\n        qlevel = state->quantTableChroma[qp];\n"
            "        if (cfg->dsc_version_minor == 2 && "
            "state->cpntBitDepth[0] == state->cpntBitDepth[1])\n"
            "            qlevel = qlevel > 0 ? qlevel - 1 : 0;\n    }\n"
            "    return qlevel;\n}\n"
            "static int dsc_cicd_prediction_type(const dsc_cfg_t *cfg, "
            "const dsc_state_t *state, int cpnt, int hpos, int vpos) {\n"
            f"    int pred = vpos == 0 ? {pt_left} : state->prevLinePred[hpos / {pred_block_size}];\n"
            f"    if (cfg->native_420 && cpnt == 2) pred = vpos <= 1 ? {pt_left} : {pt_map};\n"
            "    return pred;\n}\n"
            "static void dsc_cicd_require_prediction(const dsc_cfg_t *cfg, "
            "const dsc_state_t *state, int hpos, int vpos, int sample_count, int qp) {\n"
            "    if (!cfg || !state || state->isEncoder != 0 || "
            "state->unitsPerGroup < 3 || state->unitsPerGroup > DSC_CICD_PRED_UNITS || "
            "hpos < 0 || hpos >= state->sliceWidth || vpos < 0 || "
            "vpos >= cfg->slice_height || sample_count < 0 || "
            "sample_count >= DSC_CICD_PRED_SAMPLES || qp < 0 || qp > 31 || "
            "!state->quantTableLuma || !state->quantTableChroma || "
            "(vpos > 0 && !state->prevLinePred)) {\n"
            "        fprintf(stderr, \"unsupported PredictionLoop decode domain: "
            "hpos=%d vpos=%d sample=%d qp=%d\\n\", hpos, vpos, sample_count, qp);\n"
            "        exit(2);\n    }\n"
            "    int seen[DSC_CICD_PRED_COMPONENTS] = {0};\n"
            "    for (int unit = 0; unit < state->unitsPerGroup; ++unit) {\n"
            "        int cpnt = state->unitCType[unit];\n"
            "        int residual_index = sample_count - state->unitStartHPos[unit];\n"
            "        if (cpnt < 0 || cpnt >= DSC_CICD_PRED_COMPONENTS || seen[cpnt] || "
            "state->cpntBitDepth[cpnt] < 8 || state->cpntBitDepth[cpnt] > 16 || "
            "residual_index < 0 || residual_index >= DSC_CICD_PRED_SAMPLES || "
            "!state->currLine[cpnt]) {\n"
            "            fprintf(stderr, \"unsupported PredictionLoop unit domain: "
            "unit=%d cpnt=%d residual=%d\\n\", unit, cpnt, residual_index);\n"
            "            exit(2);\n        }\n"
            "        seen[cpnt] = 1;\n"
            "        int plane = cfg->native_420 && cpnt == 2 ? cpnt + (vpos % 2) : cpnt;\n"
            "        int qlevel = dsc_cicd_map_qlevel_c(cfg, state, qp, cpnt);\n"
            "        int pred = dsc_cicd_prediction_type(cfg, state, cpnt, hpos, vpos);\n"
            "        if (plane < 0 || plane > DSC_CICD_PRED_COMPONENTS || "
            "!state->prevLine[plane] || qlevel < 0 || qlevel > state->cpntBitDepth[cpnt] || "
            f"pred < {pt_map} || pred > 11) {{\n"
            "            fprintf(stderr, \"unsupported PredictionLoop taps: "
            "unit=%d plane=%d qlevel=%d pred=%d\\n\", unit, plane, qlevel, pred);\n"
            "            exit(2);\n        }\n    }\n}\n"
            "static void dsc_cicd_apply_prediction(dsc_state_t *state, "
            "const dsc_cicd_prediction_output_t *output) {\n"
            "    for (int unit = 0; unit < DSC_CICD_PRED_UNITS; ++unit)\n"
            "        if (output->write_enable[unit])\n"
            "            state->currLine[output->write_component[unit]]"
            "[output->write_index[unit]] = output->write_value[unit];\n}\n"
            "static int dsc_cicd_prediction_mismatch("
            "const dsc_cicd_prediction_output_t *left, "
            "const dsc_cicd_prediction_output_t *right) {\n"
            "    return memcmp(left, right, sizeof(*left)) != 0;\n}\n"
            "static void dsc_cicd_print_prediction_mismatch(int hpos, int vpos, "
            "int sample_count, const dsc_cicd_prediction_output_t *c, "
            "const dsc_cicd_prediction_output_t *rtl) {\n"
            "    fprintf(stderr, \"C/RTL PredictionLoop decode mismatch: "
            "hpos=%d vpos=%d sample=%d domain=%d/%d\", hpos, vpos, sample_count, "
            "c->domain_valid, rtl->domain_valid);\n"
            "    for (int unit = 0; unit < DSC_CICD_PRED_UNITS; ++unit)\n"
            "        fprintf(stderr, \" u%d=%d,%d,%d,%d/%d,%d,%d,%d\", unit, "
            "c->write_enable[unit], c->write_component[unit], c->write_index[unit], "
            "c->write_value[unit], rtl->write_enable[unit], "
            "rtl->write_component[unit], rtl->write_index[unit], "
            "rtl->write_value[unit]);\n"
            "    fputc('\\n', stderr);\n}\n"
            + f"void dsc_cicd_invoke({caller_declarations}) {{\n"
            f"    if (!{state_parameter}) {{ fprintf(stderr, \"null PredictionLoop state\\n\"); exit(2); }}\n"
            f"    if ({state_parameter}->isEncoder != 0) {{\n"
            f"        {original}({alias_call});\n        return;\n    }}\n"
            f"    dsc_cicd_require_prediction({config_parameter}, {state_parameter}, "
            f"{hpos_parameter}, {vpos_parameter}, {sample_parameter}, {qp_parameter});\n"
            "    dsc_cicd_prediction_input_t dsc_cicd_input;\n"
            "    dsc_cicd_prediction_output_t dsc_cicd_c_output;\n"
            "    dsc_cicd_prediction_output_t dsc_cicd_rtl_output;\n"
            "    memset(&dsc_cicd_input, 0, sizeof(dsc_cicd_input));\n"
            "    memset(&dsc_cicd_c_output, 0, sizeof(dsc_cicd_c_output));\n"
            f"    dsc_cicd_input.hpos = {hpos_parameter};\n"
            f"    dsc_cicd_input.vpos = {vpos_parameter};\n"
            f"    dsc_cicd_input.sample_count = {sample_parameter};\n"
            f"    dsc_cicd_input.qp = {qp_parameter};\n"
            f"    dsc_cicd_input.cfg_native_420 = {config_parameter}->native_420;\n"
            f"    dsc_cicd_input.cfg_dsc_version_minor = {config_parameter}->dsc_version_minor;\n"
            f"    dsc_cicd_input.is_encoder = {state_parameter}->isEncoder;\n"
            f"    dsc_cicd_input.units_per_group = {state_parameter}->unitsPerGroup;\n"
            f"    memcpy(dsc_cicd_input.cpnt_bit_depth, {state_parameter}->cpntBitDepth, "
            "sizeof(dsc_cicd_input.cpnt_bit_depth));\n"
            f"    memcpy(dsc_cicd_input.unit_c_type, {state_parameter}->unitCType, "
            "sizeof(dsc_cicd_input.unit_c_type));\n"
            f"    memcpy(dsc_cicd_input.unit_start_hpos, {state_parameter}->unitStartHPos, "
            "sizeof(dsc_cicd_input.unit_start_hpos));\n"
            f"    memcpy(dsc_cicd_input.use_midpoint, {state_parameter}->useMidpoint, "
            "sizeof(dsc_cicd_input.use_midpoint));\n"
            f"    memcpy(dsc_cicd_input.left_recon, {state_parameter}->leftRecon, "
            "sizeof(dsc_cicd_input.left_recon));\n"
            f"    memcpy(dsc_cicd_input.quantized_residual, {state_parameter}->quantizedResidual, "
            "sizeof(dsc_cicd_input.quantized_residual));\n"
            f"    dsc_cicd_input.qlevel_luma = {state_parameter}->quantTableLuma[{qp_parameter}];\n"
            f"    dsc_cicd_input.qlevel_chroma = {state_parameter}->quantTableChroma[{qp_parameter}];\n"
            f"    dsc_cicd_input.prev_line_prediction = {vpos_parameter} == 0 ? {pt_left} : "
            f"{state_parameter}->prevLinePred[{hpos_parameter} / {pred_block_size}];\n"
            "    int dsc_cicd_prior[DSC_CICD_PRED_UNITS] = {0};\n"
            f"    int dsc_cicd_write_index = {hpos_parameter} + {padding_left};\n"
            f"    int dsc_cicd_group_base = ({hpos_parameter} / {samples}) * {samples} + {padding_left};\n"
            f"    for (int unit = 0; unit < {state_parameter}->unitsPerGroup; ++unit) {{\n"
            f"        int cpnt = {state_parameter}->unitCType[unit];\n"
            f"        int plane = {config_parameter}->native_420 && cpnt == 2 ? "
            f"cpnt + ({vpos_parameter} % 2) : cpnt;\n"
            f"        int pred = dsc_cicd_prediction_type({config_parameter}, "
            f"{state_parameter}, cpnt, {hpos_parameter}, {vpos_parameter});\n"
            "        for (int tap = 0; tap < DSC_CICD_PRED_PREV_TAPS; ++tap)\n"
            f"            dsc_cicd_input.prev_line[unit][tap] = {state_parameter}->"
            "prevLine[plane][dsc_cicd_group_base - 2 + tap];\n"
            f"        dsc_cicd_input.curr_a[unit] = {state_parameter}->"
            "currLine[cpnt][dsc_cicd_group_base - 1];\n"
            f"        if (pred >= {pt_block}) {{\n"
            f"            int block_index = {hpos_parameter} + {padding_left} - 1 - "
            f"(pred - {pt_block});\n"
            "            if (block_index < 0) block_index = 0;\n"
            f"            dsc_cicd_input.curr_block[unit] = {state_parameter}->"
            "currLine[cpnt][block_index];\n        }\n"
            f"        dsc_cicd_prior[unit] = {state_parameter}->"
            "currLine[cpnt][dsc_cicd_write_index];\n    }\n"
            f"    dsc_state_t dsc_cicd_c_state = *{state_parameter};\n"
            f"    {original}({config_parameter}, &dsc_cicd_c_state, "
            f"{hpos_parameter}, {vpos_parameter}, {sample_parameter}, {qp_parameter});\n"
            "    dsc_cicd_c_output.domain_valid = 1;\n"
            f"    for (int unit = 0; unit < {state_parameter}->unitsPerGroup; ++unit) {{\n"
            f"        int cpnt = {state_parameter}->unitCType[unit];\n"
            "        dsc_cicd_c_output.write_enable[unit] = 1;\n"
            "        dsc_cicd_c_output.write_component[unit] = cpnt;\n"
            "        dsc_cicd_c_output.write_index[unit] = dsc_cicd_write_index;\n"
            f"        dsc_cicd_c_output.write_value[unit] = {state_parameter}->"
            "currLine[cpnt][dsc_cicd_write_index];\n"
            f"        {state_parameter}->currLine[cpnt][dsc_cicd_write_index] = "
            "dsc_cicd_prior[unit];\n    }\n"
            "    int mode = dsc_cicd_mode();\n    dsc_cicd_note_call(mode);\n"
            "    if (mode == 0) {\n"
            f"        dsc_cicd_apply_prediction({state_parameter}, &dsc_cicd_c_output);\n"
            "        return;\n    }\n"
            "    memset(&dsc_cicd_rtl_output, 0, sizeof(dsc_cicd_rtl_output));\n"
            "    dsc_cicd_rtl(&dsc_cicd_input, &dsc_cicd_rtl_output);\n"
            "    if (dsc_cicd_prediction_mismatch(&dsc_cicd_c_output, "
            "&dsc_cicd_rtl_output)) {\n"
            "        ++dsc_cicd_mismatches;\n"
            "        if (dsc_cicd_mismatches <= 16)\n"
            f"            dsc_cicd_print_prediction_mismatch({hpos_parameter}, "
            f"{vpos_parameter}, {sample_parameter}, &dsc_cicd_c_output, "
            "&dsc_cicd_rtl_output);\n    }\n"
            "    if (mode == 2) {\n"
            f"        dsc_cicd_apply_prediction({state_parameter}, &dsc_cicd_rtl_output);\n"
            "        return;\n    }\n"
            f"    dsc_cicd_apply_prediction({state_parameter}, &dsc_cicd_c_output);\n"
            "}\n"
            + f"void {function_name}({caller_declarations}) {{\n"
            f"    dsc_cicd_invoke({alias_call});\n}}\n",
            encoding="utf-8",
        )

        bridge_assignments = [
            f"    dut.{argument_ports[hpos_parameter]} = static_cast<std::uint32_t>(input->hpos);",
            f"    dut.{argument_ports[vpos_parameter]} = static_cast<std::uint32_t>(input->vpos);",
            f"    dut.{argument_ports[sample_parameter]} = static_cast<std::uint32_t>(input->sample_count);",
            f"    dut.{argument_ports[qp_parameter]} = static_cast<std::uint32_t>(input->qp);",
            f"    dut.{config_ports['native_420']} = static_cast<std::uint32_t>(input->cfg_native_420);",
            f"    dut.{config_ports['dsc_version_minor']} = static_cast<std::uint32_t>(input->cfg_dsc_version_minor);",
            f"    dut.{state_ports['isEncoder']} = static_cast<std::uint32_t>(input->is_encoder);",
            f"    dut.{state_ports['unitsPerGroup']} = static_cast<std::uint32_t>(input->units_per_group);",
        ]
        bridge_assignments.extend(
            f"    dut.{port} = static_cast<std::uint32_t>(input->cpnt_bit_depth[{index}]);"
            for index, port in enumerate(depth_ports)
        )
        bridge_assignments.extend(
            f"    dut.{port} = static_cast<std::uint32_t>(input->unit_c_type[{index}]);"
            for index, port in enumerate(unit_type_ports)
        )
        bridge_assignments.extend(
            f"    dut.{port} = static_cast<std::uint32_t>(input->unit_start_hpos[{index}]);"
            for index, port in enumerate(unit_start_ports)
        )
        bridge_assignments.extend(
            f"    dut.{port} = static_cast<std::uint32_t>(input->use_midpoint[{index}]);"
            for index, port in enumerate(midpoint_ports)
        )
        bridge_assignments.extend(
            f"    dut.{port} = static_cast<std::uint32_t>(input->left_recon[{index}]);"
            for index, port in enumerate(left_ports)
        )
        bridge_assignments.extend(
            f"    dut.{residual_ports[unit][index]} = static_cast<std::uint32_t>("
            f"input->quantized_residual[{unit}][{index}]);"
            for unit in range(units) for index in range(samples)
        )
        bridge_assignments.extend([
            f"    dut.{qlevel_ports['luma']} = static_cast<std::uint32_t>(input->qlevel_luma);",
            f"    dut.{qlevel_ports['chroma']} = static_cast<std::uint32_t>(input->qlevel_chroma);",
            f"    dut.{prediction_port} = static_cast<std::uint32_t>(input->prev_line_prediction);",
        ])
        bridge_assignments.extend(
            f"    dut.{previous_ports[unit][tap]} = static_cast<std::uint32_t>("
            f"input->prev_line[{unit}][{tap}]);"
            for unit in range(units) for tap in range(6)
        )
        bridge_assignments.extend(
            f"    dut.{current_a_ports[unit]} = static_cast<std::uint32_t>(input->curr_a[{unit}]);"
            for unit in range(units)
        )
        bridge_assignments.extend(
            f"    dut.{current_block_ports[unit]} = static_cast<std::uint32_t>(input->curr_block[{unit}]);"
            for unit in range(units)
        )
        bridge_outputs = [
            "    output->domain_valid = static_cast<std::int32_t>(dut.domain_valid);"
        ]
        for unit, slot in enumerate(write_ports):
            bridge_outputs.extend([
                f"    output->write_enable[{unit}] = static_cast<std::int32_t>(dut.{slot['enable']});",
                f"    output->write_component[{unit}] = static_cast<std::int32_t>(dut.{slot['component']});",
                f"    output->write_index[{unit}] = static_cast<std::int32_t>(dut.{slot['index']});",
                f"    output->write_value[{unit}] = static_cast<std::int32_t>(dut.{slot['value']});",
            ])
        bridge = source_dir / "rtl_bridge.cpp"
        bridge.write_text(
            "#include <cstdint>\n#include \"verilated.h\"\n"
            "#include \"dsc_cicd_rtl_abi.h\"\n"
            f"#include \"V{safe_identifier(module)}.h\"\n"
            "double sc_time_stamp() { return 0.0; }\n"
            "extern \"C\" void dsc_cicd_rtl("
            "const dsc_cicd_prediction_input_t *input, "
            "dsc_cicd_prediction_output_t *output) {\n"
            f"    static V{safe_identifier(module)} dut;\n"
            + "\n".join(bridge_assignments)
            + "\n    dut.eval();\n"
            + "\n".join(bridge_outputs)
            + "\n}\n",
            encoding="utf-8",
        )
        main = source_dir / "dsc_cicd_main.c"
        main.write_text(
            "#include <stdio.h>\nextern int dsc_cicd_original_main(int, char **);\n"
            "int main(int argc, char **argv) { return dsc_cicd_original_main(argc, argv); }\n",
            encoding="utf-8",
        )
        rtl_bindings = [
            hpos_parameter, vpos_parameter, sample_parameter, qp_parameter,
            f"{config_parameter}->native_420",
            f"{config_parameter}->dsc_version_minor",
            f"{state_parameter}->isEncoder",
            f"{state_parameter}->unitsPerGroup",
            *[f"{state_parameter}->cpntBitDepth[{index}]" for index in range(components)],
            *[f"{state_parameter}->unitCType[{index}]" for index in range(units)],
            *[f"{state_parameter}->unitStartHPos[{index}]" for index in range(units)],
            *[f"{state_parameter}->useMidpoint[{index}]" for index in range(units)],
            *[f"{state_parameter}->leftRecon[{index}]" for index in range(components)],
            *[
                f"{state_parameter}->quantizedResidual[{unit}][{index}]"
                for unit in range(units) for index in range(samples)
            ],
            f"{state_parameter}->quantTableLuma[{qp_parameter}]",
            f"{state_parameter}->quantTableChroma[{qp_parameter}]",
            f"guarded {state_parameter}->prevLinePred[{hpos_parameter}/{pred_block_size}]",
            *[
                f"selected {state_parameter}->prevLine[plane][group_base-2+{tap}]"
                for plane in range(units) for tap in range(6)
            ],
            *[f"selected {state_parameter}->currLine[cpnt][group_base-1]" for _ in range(units)],
            *[f"guarded {state_parameter}->currLine[cpnt][block_index]" for _ in range(units)],
        ]
        return {
            "header": header, "abi": abi, "overlay": overlay,
            "bridge": bridge, "main": main, "candidate": candidate_sv,
            "composition": {
                "status": "PASS",
                "adapter_kind": "explicit_bounded_prediction_decode_transition",
                "caller_parameter_count": len(parameters),
                "rtl_input_count": len(inputs),
                "frozen_input_ports": [str(port.get("name")) for port in inputs],
                "rtl_bindings": rtl_bindings,
                "state_outputs": [str(port.get("name")) for port in outputs],
                "decoder_only_specialization_is_explicit": True,
                "encoder_calls_bypass_rtl_and_remain_original_c": True,
                "rtl_return_controls_complete_decoder_line_write_footprint": True,
                "c_oracle_uses_private_embedded_state_and_restored_line_writes": True,
                "inactive_line_taps_are_not_dereferenced": True,
                "residual_symbol_alias_routes_to_dispatcher": True,
            },
        }

    def write_bounded_block_pred_search_transition_overlay_sources(
        self,
        contract: dict[str, Any],
        source_dir: pathlib.Path,
        module: str,
        candidate_sv: pathlib.Path,
    ) -> dict[str, Any]:
        """Bind the bounded predictor accumulators and one decision write."""
        semantics = contract.get("semantics", {}) or {}
        constants = semantics.get("constants", {}) or {}
        bindings = semantics.get("bindings", {}) or {}
        components = int(constants.get("component_count", 0))
        bp_range = int(constants.get("bp_range", 0))
        bp_size = int(constants.get("bp_size", 0))
        pred_block_size = int(constants.get("pred_block_size", 0))
        padding_left = int(constants.get("padding_left", 0))
        if (
            components, bp_range, bp_size, pred_block_size, padding_left
        ) != (4, 13, 3, 3, 5):
            raise RuntimeError("bounded block predictor constants are incomplete")

        argument_ports = {
            str(key): str(value)
            for key, value in (bindings.get("argument_ports", {}) or {}).items()
        }
        config_ports = {
            str(key): str(value)
            for key, value in (bindings.get("config_ports", {}) or {}).items()
        }
        state_ports = {
            str(key): str(value)
            for key, value in (bindings.get("state_ports", {}) or {}).items()
        }
        depth_ports = [str(value) for value in bindings.get("depth_ports", [])]
        pred_inputs = [
            [str(value) for value in row]
            for row in bindings.get("pred_input_ports", [])
        ]
        last_inputs = [
            [[str(value) for value in block] for block in component]
            for component in bindings.get("last_input_ports", [])
        ]
        line_offsets = [int(value) for value in bindings.get("line_sample_offsets", [])]
        line_ports = [str(value) for value in bindings.get("line_sample_ports", [])]
        state_outputs = {
            str(key): str(value)
            for key, value in (bindings.get("state_output_ports", {}) or {}).items()
        }
        pred_outputs = [
            [str(value) for value in row]
            for row in bindings.get("pred_output_ports", [])
        ]
        last_outputs = [
            [[str(value) for value in block] for block in component]
            for component in bindings.get("last_output_ports", [])
        ]
        write_ports = {
            str(key): str(value)
            for key, value in (bindings.get("write_ports", {}) or {}).items()
        }
        if (
            len(argument_ports) != 2
            or set(config_ports) != {
                "bits_per_component", "block_pred_enable", "native_420"
            }
            or set(state_ports) != {
                "numComponents", "bpCount", "lastEdgeCount", "edgeDetected"
            }
            or len(depth_ports) != components
            or len(pred_inputs) != components
            or len(pred_outputs) != components
            or any(len(row) != bp_range for row in pred_inputs + pred_outputs)
            or len(last_inputs) != components
            or len(last_outputs) != components
            or any(len(component) != bp_size for component in last_inputs + last_outputs)
            or any(
                len(block) != bp_range
                for component in last_inputs + last_outputs for block in component
            )
            or line_offsets != list(range(-8, 6))
            or len(line_ports) != len(line_offsets)
            or set(state_outputs) != {"bpCount", "lastEdgeCount", "edgeDetected"}
            or set(write_ports) != {"enable", "index", "value"}
        ):
            raise RuntimeError("bounded block predictor bindings are incomplete")

        ports = [
            port for port in (contract.get("interface", {}) or {}).get("ports", [])
            if isinstance(port, dict)
        ]
        inputs = [port for port in ports if port.get("direction") == "input"]
        outputs = [port for port in ports if port.get("direction") == "output"]
        expected_inputs = {
            *argument_ports.values(), *config_ports.values(), *state_ports.values(),
            *depth_ports, *[value for row in pred_inputs for value in row],
            *[
                value for component in last_inputs
                for block in component for value in block
            ],
            *line_ports,
        }
        expected_outputs = {
            "domain_valid", *state_outputs.values(),
            *[value for row in pred_outputs for value in row],
            *[
                value for component in last_outputs
                for block in component for value in block
            ],
            *write_ports.values(),
        }
        if (
            {str(port.get("name")) for port in inputs} != expected_inputs
            or {str(port.get("name")) for port in outputs} != expected_outputs
        ):
            raise RuntimeError("bounded block predictor ports changed")

        parameters = self.function_parameters(contract)
        parameter_by_name = {
            str(parameter.get("name")): parameter for parameter in parameters
        }
        config_parameter = str(bindings.get("config_parameter", ""))
        state_parameter = str(bindings.get("state_parameter", ""))
        line_parameter = str(bindings.get("line_parameter", ""))
        cpnt_parameter = str(bindings.get("component_parameter", ""))
        hpos_parameter = str(bindings.get("horizontal_parameter", ""))
        if set(parameter_by_name) != {
            config_parameter, state_parameter, line_parameter,
            cpnt_parameter, hpos_parameter,
        }:
            raise RuntimeError("bounded block predictor native ABI is incomplete")
        if (
            not parameter_is_pointer(parameter_by_name[config_parameter])
            or not parameter_is_pointer(parameter_by_name[state_parameter])
            or not parameter_is_pointer(parameter_by_name[line_parameter])
            or parameter_is_pointer(parameter_by_name[cpnt_parameter])
            or parameter_is_pointer(parameter_by_name[hpos_parameter])
        ):
            raise RuntimeError("bounded block predictor pointer/scalar ABI changed")
        identifier = re.compile(r"^[A-Za-z_][A-Za-z0-9_]*$")
        identifiers = {
            config_parameter, state_parameter, line_parameter,
            cpnt_parameter, hpos_parameter,
            *expected_inputs, *expected_outputs,
        }
        if not all(identifier.fullmatch(value) for value in identifiers):
            raise RuntimeError("bounded block predictor contains invalid identifiers")

        parameter_specs = [
            f"{str(parameter.get('type', 'int')).strip()} {parameter.get('name')}"
            for parameter in parameters
        ]
        parameter_names = [str(parameter.get("name")) for parameter in parameters]
        caller_declarations = ", ".join(parameter_specs)
        alias_call = ", ".join(parameter_names)
        function_name = str(contract_function(contract).get("name"))
        original = function_name + "_original"

        abi = source_dir / "dsc_cicd_rtl_abi.h"
        abi.write_text(
            "#ifndef DSC_CICD_RTL_ABI_H\n#define DSC_CICD_RTL_ABI_H\n"
            "#include <stdint.h>\n"
            f"#define DSC_CICD_BP_COMPONENTS {components}\n"
            f"#define DSC_CICD_BP_RANGE {bp_range}\n"
            f"#define DSC_CICD_BP_SIZE {bp_size}\n"
            f"#define DSC_CICD_BP_LINE_SAMPLES {len(line_ports)}\n"
            "typedef struct {\n"
            "    int32_t cpnt;\n    int32_t hpos;\n"
            "    int32_t cfg_bits_per_component;\n"
            "    int32_t cfg_block_pred_enable;\n    int32_t cfg_native_420;\n"
            "    int32_t num_components;\n    int32_t bp_count;\n"
            "    int32_t last_edge_count;\n    int32_t edge_detected;\n"
            "    int32_t cpnt_bit_depth[DSC_CICD_BP_COMPONENTS];\n"
            "    int32_t pred_err[DSC_CICD_BP_COMPONENTS][DSC_CICD_BP_RANGE];\n"
            "    int32_t last_err[DSC_CICD_BP_COMPONENTS][DSC_CICD_BP_SIZE]"
            "[DSC_CICD_BP_RANGE];\n"
            "    int32_t line_sample[DSC_CICD_BP_LINE_SAMPLES];\n"
            "} dsc_cicd_bp_input_t;\n"
            "typedef struct {\n"
            "    int32_t domain_valid;\n    int32_t bp_count;\n"
            "    int32_t last_edge_count;\n    int32_t edge_detected;\n"
            "    int32_t pred_err[DSC_CICD_BP_COMPONENTS][DSC_CICD_BP_RANGE];\n"
            "    int32_t last_err[DSC_CICD_BP_COMPONENTS][DSC_CICD_BP_SIZE]"
            "[DSC_CICD_BP_RANGE];\n"
            "    int32_t write_enable;\n    int32_t write_index;\n"
            "    int32_t write_value;\n"
            "} dsc_cicd_bp_output_t;\n"
            "#ifdef __cplusplus\nextern \"C\" {\n#endif\n"
            "void dsc_cicd_rtl(const dsc_cicd_bp_input_t *input, "
            "dsc_cicd_bp_output_t *output);\n"
            "#ifdef __cplusplus\n}\n#endif\n#endif\n",
            encoding="utf-8",
        )
        header = source_dir / "dsc_cicd_overlay.h"
        header.write_text(
            "#ifndef DSC_CICD_OVERLAY_H\n#define DSC_CICD_OVERLAY_H\n"
            "#include \"dsc_types.h\"\n"
            f"void dsc_cicd_invoke({caller_declarations});\n#endif\n",
            encoding="utf-8",
        )

        overlay = source_dir / "dsc_cicd_overlay.c"
        overlay.write_text(
            "#include <stdint.h>\n#include <stdio.h>\n#include <stdlib.h>\n"
            "#include <string.h>\n#include \"dsc_cicd_overlay.h\"\n"
            "#include \"dsc_cicd_rtl_abi.h\"\n"
            f"extern void {original}({caller_declarations});\n"
            "static int dsc_cicd_mode(void) {\n"
            "    const char *value = getenv(\"DSC_CICD_MODE\");\n"
            "    if (value && strcmp(value, \"SHADOW\") == 0) return 1;\n"
            "    if (value && strcmp(value, \"RTL_RETURN\") == 0) return 2;\n"
            "    return 0;\n}\n"
            + self.overlay_runtime_metrics_source()
            + "static int dsc_cicd_bp_active(const dsc_cfg_t *cfg, int cpnt) {\n"
            "    return !(cfg->native_420 && cpnt > 1);\n}\n"
            "static int dsc_cicd_bp_write_enable(const dsc_cfg_t *cfg, "
            "const dsc_state_t *state, int cpnt, int hpos) {\n"
            "    int max_cpnt = cfg->native_420 ? 1 : state->numComponents - 1;\n"
            f"    return dsc_cicd_bp_active(cfg, cpnt) && "
            f"(hpos % {pred_block_size}) == {pred_block_size - 1} && cpnt >= max_cpnt;\n"
            "}\n"
            "static void dsc_cicd_require_bp(const dsc_cfg_t *cfg, "
            "const dsc_state_t *state, int cpnt, int **line, int hpos) {\n"
            "    if (!cfg || !state || cpnt < 0 || cpnt >= DSC_CICD_BP_COMPONENTS || "
            "hpos < 0 || state->numComponents < 3 || "
            "state->numComponents > DSC_CICD_BP_COMPONENTS || "
            "cpnt >= state->numComponents || cfg->bits_per_component < 8 || "
            "cfg->bits_per_component > 16 || state->cpntBitDepth[cpnt] < 8 || "
            "state->cpntBitDepth[cpnt] > 16) {\n"
            "        fprintf(stderr, \"unsupported block predictor domain: "
            "cpnt=%d hpos=%d\\n\", cpnt, hpos);\n        exit(2);\n    }\n"
            "    if (dsc_cicd_bp_active(cfg, cpnt) && (!line || !line[cpnt])) {\n"
            "        fprintf(stderr, \"missing active block predictor line plane\\n\");\n"
            "        exit(2);\n    }\n"
            "    if (dsc_cicd_bp_write_enable(cfg, state, cpnt, hpos) && "
            "!state->prevLinePred) {\n"
            "        fprintf(stderr, \"missing block predictor decision buffer\\n\");\n"
            "        exit(2);\n    }\n}\n"
            "static void dsc_cicd_capture_bp(const dsc_state_t *state, "
            "int write_enable, int write_index, int write_value, "
            "dsc_cicd_bp_output_t *output) {\n"
            "    memset(output, 0, sizeof(*output));\n"
            "    output->domain_valid = 1;\n"
            "    output->bp_count = state->bpCount;\n"
            "    output->last_edge_count = state->lastEdgeCount;\n"
            "    output->edge_detected = state->edgeDetected;\n"
            "    memcpy(output->pred_err, state->predErr, sizeof(output->pred_err));\n"
            "    memcpy(output->last_err, state->lastErr, sizeof(output->last_err));\n"
            "    output->write_enable = write_enable;\n"
            "    output->write_index = write_index;\n"
            "    output->write_value = write_value;\n"
            "}\n"
            "static void dsc_cicd_apply_bp(dsc_state_t *state, "
            "const dsc_cicd_bp_output_t *output) {\n"
            "    state->bpCount = output->bp_count;\n"
            "    state->lastEdgeCount = output->last_edge_count;\n"
            "    state->edgeDetected = output->edge_detected;\n"
            "    memcpy(state->predErr, output->pred_err, sizeof(output->pred_err));\n"
            "    memcpy(state->lastErr, output->last_err, sizeof(output->last_err));\n"
            "    if (output->write_enable)\n"
            "        state->prevLinePred[output->write_index] = "
            "(PRED_TYPE)output->write_value;\n"
            "}\n"
            "static int dsc_cicd_bp_mismatch(const dsc_cicd_bp_output_t *left, "
            "const dsc_cicd_bp_output_t *right) {\n"
            "    return memcmp(left, right, sizeof(*left)) != 0;\n}\n"
            "static void dsc_cicd_print_bp_mismatch(int cpnt, int hpos, "
            "const dsc_cicd_bp_output_t *c, const dsc_cicd_bp_output_t *rtl) {\n"
            "    fprintf(stderr, \"C/RTL BlockPredSearch mismatch: cpnt=%d hpos=%d "
            "domain=%d/%d bp=%d/%d edge=%d/%d last=%d/%d "
            "write=%d,%d,%d/%d,%d,%d\\n\", cpnt, hpos, "
            "c->domain_valid, rtl->domain_valid, c->bp_count, rtl->bp_count, "
            "c->edge_detected, rtl->edge_detected, c->last_edge_count, "
            "rtl->last_edge_count, c->write_enable, c->write_index, "
            "c->write_value, rtl->write_enable, rtl->write_index, "
            "rtl->write_value);\n}\n"
            + f"void dsc_cicd_invoke({caller_declarations}) {{\n"
            f"    dsc_cicd_require_bp({config_parameter}, {state_parameter}, "
            f"{cpnt_parameter}, {line_parameter}, {hpos_parameter});\n"
            "    dsc_cicd_bp_input_t dsc_cicd_input;\n"
            "    dsc_cicd_bp_output_t dsc_cicd_c_output;\n"
            "    dsc_cicd_bp_output_t dsc_cicd_rtl_output;\n"
            "    memset(&dsc_cicd_input, 0, sizeof(dsc_cicd_input));\n"
            f"    dsc_cicd_input.cpnt = {cpnt_parameter};\n"
            f"    dsc_cicd_input.hpos = {hpos_parameter};\n"
            f"    dsc_cicd_input.cfg_bits_per_component = "
            f"{config_parameter}->bits_per_component;\n"
            f"    dsc_cicd_input.cfg_block_pred_enable = "
            f"{config_parameter}->block_pred_enable;\n"
            f"    dsc_cicd_input.cfg_native_420 = {config_parameter}->native_420;\n"
            f"    dsc_cicd_input.num_components = {state_parameter}->numComponents;\n"
            f"    dsc_cicd_input.bp_count = {state_parameter}->bpCount;\n"
            f"    dsc_cicd_input.last_edge_count = {state_parameter}->lastEdgeCount;\n"
            f"    dsc_cicd_input.edge_detected = {state_parameter}->edgeDetected;\n"
            f"    memcpy(dsc_cicd_input.cpnt_bit_depth, {state_parameter}->cpntBitDepth, "
            "sizeof(dsc_cicd_input.cpnt_bit_depth));\n"
            f"    memcpy(dsc_cicd_input.pred_err, {state_parameter}->predErr, "
            "sizeof(dsc_cicd_input.pred_err));\n"
            f"    memcpy(dsc_cicd_input.last_err, {state_parameter}->lastErr, "
            "sizeof(dsc_cicd_input.last_err));\n"
            f"    if (dsc_cicd_bp_active({config_parameter}, {cpnt_parameter})) {{\n"
            f"        dsc_cicd_input.line_sample[13] = {line_parameter}[{cpnt_parameter}]"
            f"[{hpos_parameter} + {padding_left}];\n"
            f"        for (int vector = 0; vector < {bp_range}; ++vector)\n"
            f"            if ({hpos_parameter} > vector)\n"
            f"                dsc_cicd_input.line_sample[12 - vector] = "
            f"{line_parameter}[{cpnt_parameter}]"
            f"[{hpos_parameter} + {padding_left} - 1 - vector];\n"
            "    }\n"
            f"    int dsc_cicd_write_enable = dsc_cicd_bp_write_enable("
            f"{config_parameter}, {state_parameter}, {cpnt_parameter}, "
            f"{hpos_parameter});\n"
            f"    int dsc_cicd_write_index = {hpos_parameter} / {pred_block_size};\n"
            "    int dsc_cicd_prior_write = 0;\n"
            "    if (dsc_cicd_write_enable)\n"
            f"        dsc_cicd_prior_write = {state_parameter}->"
            "prevLinePred[dsc_cicd_write_index];\n"
            f"    dsc_state_t dsc_cicd_c_state = *{state_parameter};\n"
            f"    {original}({config_parameter}, &dsc_cicd_c_state, "
            f"{cpnt_parameter}, {line_parameter}, {hpos_parameter});\n"
            "    int dsc_cicd_c_write = 0;\n"
            "    if (dsc_cicd_write_enable) {\n"
            f"        dsc_cicd_c_write = {state_parameter}->"
            "prevLinePred[dsc_cicd_write_index];\n"
            f"        {state_parameter}->prevLinePred[dsc_cicd_write_index] = "
            "(PRED_TYPE)dsc_cicd_prior_write;\n    }\n"
            "    dsc_cicd_capture_bp(&dsc_cicd_c_state, dsc_cicd_write_enable, "
            "dsc_cicd_write_index, dsc_cicd_c_write, &dsc_cicd_c_output);\n"
            "    int mode = dsc_cicd_mode();\n    dsc_cicd_note_call(mode);\n"
            "    if (mode == 0) {\n"
            f"        dsc_cicd_apply_bp({state_parameter}, &dsc_cicd_c_output);\n"
            "        return;\n    }\n"
            "    memset(&dsc_cicd_rtl_output, 0, sizeof(dsc_cicd_rtl_output));\n"
            "    dsc_cicd_rtl(&dsc_cicd_input, &dsc_cicd_rtl_output);\n"
            "    if (dsc_cicd_bp_mismatch(&dsc_cicd_c_output, "
            "&dsc_cicd_rtl_output)) {\n"
            "        ++dsc_cicd_mismatches;\n"
            "        if (dsc_cicd_mismatches <= 16)\n"
            f"            dsc_cicd_print_bp_mismatch({cpnt_parameter}, "
            f"{hpos_parameter}, &dsc_cicd_c_output, &dsc_cicd_rtl_output);\n"
            "    }\n"
            "    if (mode == 2) {\n"
            f"        dsc_cicd_apply_bp({state_parameter}, &dsc_cicd_rtl_output);\n"
            "        return;\n    }\n"
            f"    dsc_cicd_apply_bp({state_parameter}, &dsc_cicd_c_output);\n"
            "}\n"
            + f"void {function_name}({caller_declarations}) {{\n"
            f"    dsc_cicd_invoke({alias_call});\n}}\n",
            encoding="utf-8",
        )

        bridge_assignments = [
            f"    dut.{argument_ports[cpnt_parameter]} = "
            "static_cast<std::uint32_t>(input->cpnt);",
            f"    dut.{argument_ports[hpos_parameter]} = "
            "static_cast<std::uint32_t>(input->hpos);",
            f"    dut.{config_ports['bits_per_component']} = "
            "static_cast<std::uint32_t>(input->cfg_bits_per_component);",
            f"    dut.{config_ports['block_pred_enable']} = "
            "static_cast<std::uint32_t>(input->cfg_block_pred_enable);",
            f"    dut.{config_ports['native_420']} = "
            "static_cast<std::uint32_t>(input->cfg_native_420);",
            f"    dut.{state_ports['numComponents']} = "
            "static_cast<std::uint32_t>(input->num_components);",
            f"    dut.{state_ports['bpCount']} = "
            "static_cast<std::uint32_t>(input->bp_count);",
            f"    dut.{state_ports['lastEdgeCount']} = "
            "static_cast<std::uint32_t>(input->last_edge_count);",
            f"    dut.{state_ports['edgeDetected']} = "
            "static_cast<std::uint32_t>(input->edge_detected);",
        ]
        bridge_assignments.extend(
            f"    dut.{port} = static_cast<std::uint32_t>(input->cpnt_bit_depth[{index}]);"
            for index, port in enumerate(depth_ports)
        )
        bridge_assignments.extend(
            f"    dut.{pred_inputs[component][vector]} = "
            f"static_cast<std::uint32_t>(input->pred_err[{component}][{vector}]);"
            for component in range(components) for vector in range(bp_range)
        )
        bridge_assignments.extend(
            f"    dut.{last_inputs[component][block][vector]} = "
            f"static_cast<std::uint32_t>(input->last_err[{component}][{block}][{vector}]);"
            for component in range(components)
            for block in range(bp_size)
            for vector in range(bp_range)
        )
        bridge_assignments.extend(
            f"    dut.{port} = static_cast<std::uint32_t>(input->line_sample[{index}]);"
            for index, port in enumerate(line_ports)
        )
        bridge_outputs = [
            "    output->domain_valid = static_cast<std::int32_t>(dut.domain_valid);",
            f"    output->bp_count = static_cast<std::int32_t>(dut.{state_outputs['bpCount']});",
            f"    output->last_edge_count = static_cast<std::int32_t>(dut.{state_outputs['lastEdgeCount']});",
            f"    output->edge_detected = static_cast<std::int32_t>(dut.{state_outputs['edgeDetected']});",
        ]
        bridge_outputs.extend(
            f"    output->pred_err[{component}][{vector}] = "
            f"static_cast<std::int32_t>(dut.{pred_outputs[component][vector]});"
            for component in range(components) for vector in range(bp_range)
        )
        bridge_outputs.extend(
            f"    output->last_err[{component}][{block}][{vector}] = "
            f"static_cast<std::int32_t>(dut.{last_outputs[component][block][vector]});"
            for component in range(components)
            for block in range(bp_size)
            for vector in range(bp_range)
        )
        bridge_outputs.extend([
            f"    output->write_enable = static_cast<std::int32_t>(dut.{write_ports['enable']});",
            f"    output->write_index = static_cast<std::int32_t>(dut.{write_ports['index']});",
            f"    output->write_value = static_cast<std::int32_t>(dut.{write_ports['value']});",
        ])
        bridge = source_dir / "rtl_bridge.cpp"
        bridge.write_text(
            "#include <cstdint>\n#include \"verilated.h\"\n"
            "#include \"dsc_cicd_rtl_abi.h\"\n"
            f"#include \"V{safe_identifier(module)}.h\"\n"
            "double sc_time_stamp() { return 0.0; }\n"
            "extern \"C\" void dsc_cicd_rtl(const dsc_cicd_bp_input_t *input, "
            "dsc_cicd_bp_output_t *output) {\n"
            f"    static V{safe_identifier(module)} dut;\n"
            + "\n".join(bridge_assignments)
            + "\n    dut.eval();\n"
            + "\n".join(bridge_outputs)
            + "\n}\n",
            encoding="utf-8",
        )
        main = source_dir / "dsc_cicd_main.c"
        main.write_text(
            "#include <stdio.h>\nextern int dsc_cicd_original_main(int, char **);\n"
            "int main(int argc, char **argv) { return dsc_cicd_original_main(argc, argv); }\n",
            encoding="utf-8",
        )
        rtl_bindings = [
            cpnt_parameter, hpos_parameter,
            *[f"{config_parameter}->{field}" for field in (
                "bits_per_component", "block_pred_enable", "native_420"
            )],
            *[f"{state_parameter}->{field}" for field in (
                "numComponents", "bpCount", "lastEdgeCount", "edgeDetected"
            )],
            *[
                f"{state_parameter}->cpntBitDepth[{index}]"
                for index in range(components)
            ],
            *[
                f"{state_parameter}->predErr[{component}][{vector}]"
                for component in range(components) for vector in range(bp_range)
            ],
            *[
                f"{state_parameter}->lastErr[{component}][{block}][{vector}]"
                for component in range(components)
                for block in range(bp_size)
                for vector in range(bp_range)
            ],
            *[
                f"guarded {line_parameter}[{cpnt_parameter}]"
                f"[{hpos_parameter}+{padding_left + offset}]"
                for offset in line_offsets
            ],
        ]
        return {
            "header": header,
            "abi": abi,
            "overlay": overlay,
            "bridge": bridge,
            "main": main,
            "candidate": candidate_sv,
            "composition": {
                "status": "PASS",
                "adapter_kind": "explicit_bounded_block_pred_search_transition",
                "caller_parameter_count": len(parameters),
                "rtl_input_count": len(inputs),
                "frozen_input_ports": [str(port.get("name")) for port in inputs],
                "rtl_bindings": rtl_bindings,
                "state_outputs": [str(port.get("name")) for port in outputs],
                "rtl_return_controls_complete_predictor_accumulators": True,
                "rtl_return_controls_indexed_prev_line_prediction_write": True,
                "c_oracle_uses_private_state_arrays": True,
                "c_oracle_decision_write_is_restored_before_mode_commit": True,
                "inactive_candidate_line_taps_are_not_dereferenced": True,
                "residual_symbol_alias_routes_to_dispatcher": True,
            },
        }

    def write_overlay_sources(self, contract: dict[str, Any], source_dir: pathlib.Path,
                              module: str, candidate_sv: pathlib.Path) -> dict[str, Any]:
        if (contract.get("semantics", {}) or {}).get("kind") == "flatness_window":
            return self.write_flatness_overlay_sources(contract, source_dir, module, candidate_sv)
        if (contract.get("semantics", {}) or {}).get("kind") == "ich_decision":
            return self.write_ich_decision_overlay_sources(contract, source_dir, module, candidate_sv)
        if (contract.get("semantics", {}) or {}).get("kind") == "bitstream_read_transition":
            return self.write_bitstream_read_transition_overlay_sources(
                contract, source_dir, module, candidate_sv
            )
        if (contract.get("semantics", {}) or {}).get("kind") == "bitstream_write_transition":
            return self.write_bitstream_write_transition_overlay_sources(
                contract, source_dir, module, candidate_sv
            )
        if (contract.get("semantics", {}) or {}).get("kind") == "fifo_read_transition":
            return self.write_fifo_read_transition_overlay_sources(
                contract, source_dir, module, candidate_sv
            )
        if (contract.get("semantics", {}) or {}).get("kind") == "fifo_read_accounting_transition":
            return self.write_fifo_read_accounting_transition_overlay_sources(
                contract, source_dir, module, candidate_sv
            )
        if (contract.get("semantics", {}) or {}).get("kind") == "fifo_write_transition":
            return self.write_fifo_write_transition_overlay_sources(
                contract, source_dir, module, candidate_sv
            )
        if (contract.get("semantics", {}) or {}).get("kind") == "fifo_write_accounting_transition":
            return self.write_fifo_write_accounting_transition_overlay_sources(
                contract, source_dir, module, candidate_sv
            )
        if (contract.get("semantics", {}) or {}).get("kind") == "bounded_midpoint_line_write_transition":
            return self.write_midpoint_line_write_transition_overlay_sources(
                contract, source_dir, module, candidate_sv
            )
        if (contract.get("semantics", {}) or {}).get("kind") == "populate_orig_line_memory_transition":
            return self.write_populate_orig_line_transition_overlay_sources(
                contract, source_dir, module, candidate_sv
            )
        if (contract.get("semantics", {}) or {}).get("kind") == "bounded_ich_decision_transition":
            return self.write_bounded_ich_decision_transition_overlay_sources(
                contract, source_dir, module, candidate_sv
            )
        if (contract.get("semantics", {}) or {}).get("kind") in {
            "history_reduction_transition", "history_qerr_transition"
        }:
            try:
                from encode_history_adapters import (
                    write_history_encode_overlay_sources,
                )
            except ImportError:
                from tools.encode_history_adapters import (
                    write_history_encode_overlay_sources,
                )
            return write_history_encode_overlay_sources(
                self, contract, source_dir, module, candidate_sv
            )
        if (contract.get("semantics", {}) or {}).get("kind") == "bounded_prediction_encode_transition":
            try:
                from encode_prediction_adapter import (
                    write_prediction_encode_overlay_sources,
                )
            except ImportError:
                from tools.encode_prediction_adapter import (
                    write_prediction_encode_overlay_sources,
                )
            return write_prediction_encode_overlay_sources(
                self, contract, source_dir, module, candidate_sv
            )
        if (contract.get("semantics", {}) or {}).get("kind") == "bounded_process_group_encode_transition":
            try:
                from encode_process_group_adapter import (
                    write_process_group_encode_overlay_sources,
                )
            except ImportError:
                from tools.encode_process_group_adapter import (
                    write_process_group_encode_overlay_sources,
                )
            return write_process_group_encode_overlay_sources(
                self, contract, source_dir, module, candidate_sv
            )
        if (contract.get("semantics", {}) or {}).get("kind") == "bounded_rate_control_encode_transition":
            try:
                from encode_rate_control_adapter import (
                    write_rate_control_encode_overlay_sources,
                )
            except ImportError:
                from tools.encode_rate_control_adapter import (
                    write_rate_control_encode_overlay_sources,
                )
            return write_rate_control_encode_overlay_sources(
                self, contract, source_dir, module, candidate_sv
            )
        if (contract.get("semantics", {}) or {}).get("kind") == "bounded_vlc_unit_encode_transition":
            try:
                from encode_vlc_unit_adapter import (
                    write_vlc_unit_encode_overlay_sources,
                )
            except ImportError:
                from tools.encode_vlc_unit_adapter import (
                    write_vlc_unit_encode_overlay_sources,
                )
            return write_vlc_unit_encode_overlay_sources(
                self, contract, source_dir, module, candidate_sv
            )
        if (contract.get("semantics", {}) or {}).get("kind") == "vlc_group_encode_fsm":
            try:
                from encode_vlc_group_adapter import (
                    write_vlc_group_encode_overlay_sources,
                )
            except ImportError:
                from tools.encode_vlc_group_adapter import (
                    write_vlc_group_encode_overlay_sources,
                )
            return write_vlc_group_encode_overlay_sources(
                self, contract, source_dir, module, candidate_sv
            )
        if (contract.get("semantics", {}) or {}).get("kind") == "scalar_record_next_state":
            return self.write_scalar_record_next_state_overlay_sources(
                contract, source_dir, module, candidate_sv
            )
        if (contract.get("semantics", {}) or {}).get("kind") == "sampled_lookup_transition":
            return self.write_sampled_lookup_transition_overlay_sources(
                contract, source_dir, module, candidate_sv
            )
        if (contract.get("semantics", {}) or {}).get("kind") == "scalar_record_memory_transition":
            return self.write_scalar_record_memory_transition_overlay_sources(
                contract, source_dir, module, candidate_sv
            )
        if (contract.get("semantics", {}) or {}).get("kind") == "bounded_mux_refill_transition":
            return self.write_bounded_mux_refill_transition_overlay_sources(
                contract, source_dir, module, candidate_sv
            )
        if (contract.get("semantics", {}) or {}).get("kind") == "bounded_flatness_state_transition":
            return self.write_bounded_flatness_state_transition_overlay_sources(
                contract, source_dir, module, candidate_sv
            )
        if (contract.get("semantics", {}) or {}).get("kind") == "bounded_line_write_transition":
            return self.write_bounded_line_write_transition_overlay_sources(
                contract, source_dir, module, candidate_sv
            )
        if (contract.get("semantics", {}) or {}).get("kind") == "bounded_history_update_transition":
            return self.write_bounded_history_update_transition_overlay_sources(
                contract, source_dir, module, candidate_sv
            )
        if (contract.get("semantics", {}) or {}).get("kind") == "bounded_history_caller_transition":
            return self.write_bounded_history_caller_transition_overlay_sources(
                contract, source_dir, module, candidate_sv
            )
        if (contract.get("semantics", {}) or {}).get("kind") == "bounded_vld_unit_transition":
            return self.write_bounded_vld_unit_transition_overlay_sources(
                contract, source_dir, module, candidate_sv
            )
        if (contract.get("semantics", {}) or {}).get("kind") == "bounded_block_pred_search_transition":
            return self.write_bounded_block_pred_search_transition_overlay_sources(
                contract, source_dir, module, candidate_sv
            )
        if (contract.get("semantics", {}) or {}).get("kind") == "bounded_prediction_decode_transition":
            return self.write_bounded_prediction_decode_transition_overlay_sources(
                contract, source_dir, module, candidate_sv
            )
        if (contract.get("semantics", {}) or {}).get("kind") == "bounded_rate_control_decode_transition":
            return self.write_bounded_rate_control_decode_transition_overlay_sources(
                contract, source_dir, module, candidate_sv
            )
        if (contract.get("semantics", {}) or {}).get("kind") == "bounded_vld_group_decode_transition":
            return self.write_bounded_vld_group_decode_transition_overlay_sources(
                contract, source_dir, module, candidate_sv
            )
        if (contract.get("semantics", {}) or {}).get("kind") == "raster_color_transform_transition":
            return self.write_raster_color_transform_overlay_sources(
                contract, source_dir, module, candidate_sv
            )
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
            + self.overlay_runtime_metrics_source()
            + f"int dsc_cicd_invoke({caller_declarations}) {{\n"
            f"    int c_value = {original}({caller_call});\n"
            "    int mode = dsc_cicd_mode();\n"
            "    dsc_cicd_note_call(mode);\n"
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
        return {
            "header": header,
            "overlay": overlay,
            "bridge": bridge,
            "main": main,
            "candidate": candidate_sv,
            "composition": {
                "status": "PASS",
                "adapter_kind": "flattened_pointer_state" if flattened else "direct_scalar",
                "caller_parameter_count": len(self.function_parameters(contract)) or len(inputs),
                "rtl_input_count": len(rtl_arguments) if flattened else len(inputs),
                "frozen_input_ports": [str(port.get("name")) for port in inputs],
                "rtl_bindings": list(rtl_arguments) if flattened else [str(port.get("name")) for port in inputs],
            },
        }

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

    @staticmethod
    def parse_overlay_metrics(output: str) -> dict[str, Any]:
        matches = re.findall(
            r"DSC_CICD_OVERLAY_METRICS(?:\s+candidate=([A-Za-z0-9_.-]+))?\s+"
            r"calls=(\d+)\s+"
            r"rtl_invocations=(\d+)\s+mismatches=(\d+)",
            str(output),
        )
        if not matches:
            return {
                "metrics_present": False,
                "calls": 0,
                "rtl_invocations": 0,
                "mismatches": len(re.findall(r"C/RTL mismatch", str(output))),
                "replacement_reached": False,
                "rtl_exercised": False,
            }
        calls = sum(int(item[1]) for item in matches)
        rtl_invocations = sum(int(item[2]) for item in matches)
        mismatches = sum(int(item[3]) for item in matches)
        candidate_metrics = {
            candidate: {
                "calls": int(candidate_calls),
                "rtl_invocations": int(candidate_rtl),
                "mismatches": int(candidate_mismatches),
                "replacement_reached": int(candidate_calls) > 0,
                "rtl_exercised": int(candidate_rtl) > 0,
            }
            for candidate, candidate_calls, candidate_rtl, candidate_mismatches in matches
            if candidate
        }
        parsed = {
            "metrics_present": True,
            "calls": calls,
            "rtl_invocations": rtl_invocations,
            "mismatches": mismatches,
            "replacement_reached": calls > 0,
            "rtl_exercised": rtl_invocations > 0,
        }
        if candidate_metrics:
            parsed["candidates"] = candidate_metrics
        return parsed

    @staticmethod
    def files_byte_equal(left: pathlib.Path, right: pathlib.Path) -> bool:
        if not left.is_file() or not right.is_file():
            return False
        if left.stat().st_size != right.stat().st_size:
            return False
        with left.open("rb") as left_handle, right.open("rb") as right_handle:
            while True:
                left_block = left_handle.read(1024 * 1024)
                right_block = right_handle.read(1024 * 1024)
                if left_block != right_block:
                    return False
                if not left_block:
                    return True

    def run_decode_frame(
        self,
        model_root: pathlib.Path,
        binary: pathlib.Path,
        scenario: dict[str, Any],
        bitstream: pathlib.Path,
        output_dir: pathlib.Path,
        mode: str | None = None,
    ) -> dict[str, Any]:
        if output_dir.exists():
            shutil.rmtree(output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)
        copied_bitstream = output_dir / pathlib.Path(str(scenario["golden"])).name
        if not bitstream.is_file():
            return {
                "status": "FAIL",
                "reason": "decode input bitstream is missing",
                "input_bitstream": str(bitstream),
                "output_directory": str(output_dir),
            }
        shutil.copy2(bitstream, copied_bitstream)
        command = self.run_process(
            [
                str(binary),
                "-F", str(scenario["config"]),
                "-do", "2",
                "-ppm", "1",
                "-O", f"LOG_FILENAME {output_dir / 'decode.log'}",
                str(scenario["list"]),
                str(output_dir),
            ],
            cwd=model_root,
            env={"DSC_CICD_MODE": mode} if mode else None,
            timeout=1800,
        )
        outputs = sorted(output_dir.glob("*.out.ppm"))
        output_file = outputs[0] if len(outputs) == 1 else None
        metrics = self.parse_overlay_metrics(str(command.get("output", "")))
        execution_pass = command.get("returncode") == 0 and output_file is not None
        return {
            "status": "PASS" if execution_pass else "FAIL",
            "command": command,
            "mode": mode or "ORIGINAL_C",
            "input_bitstream": str(copied_bitstream),
            "input_bitstream_sha256": file_hash(copied_bitstream),
            "output_directory": str(output_dir),
            "output_count": len(outputs),
            "output_file": str(output_file) if output_file else None,
            "sha256": file_hash(output_file) if output_file else None,
            "size_bytes": output_file.stat().st_size if output_file else None,
            "overlay_metrics": metrics,
        }

    @staticmethod
    def matrix_scope() -> str:
        scope = os.environ.get("DSC_CICD_MATRIX_SCOPE", "smoke").strip().lower() or "smoke"
        if scope not in {"smoke", "all"}:
            raise ValueError(
                "DSC_CICD_MATRIX_SCOPE must be either 'smoke' or 'all'"
            )
        return scope

    @staticmethod
    def matrix_evidence_summary(scenarios: list[dict[str, Any]]) -> dict[str, Any]:
        anchored = sum(
            1 for scenario in scenarios
            if scenario.get("oracle_class") == "ANCHORED_EXPECTED_SHA"
        )
        differential_only = len(scenarios) - anchored
        mode_count = 3
        return {
            "selected_profiles": len(scenarios),
            "anchored_profiles": anchored,
            "differential_only_profiles": differential_only,
            "all_profiles_anchored": differential_only == 0,
            "mode_count": mode_count,
            "anchored_mode_rows": anchored * mode_count,
            "differential_only_mode_rows": differential_only * mode_count,
            "differential_only_excluded_from_promotion": True,
            "policy": (
                "ANCHORED_EXPECTED_SHA profiles must match both the fixed script SHA-256 "
                "and the same-run C baseline; C_BASELINE_DIFFERENTIAL_ONLY profiles may "
                "provide simulation evidence but are not promotion evidence"
            ),
        }

    def discover_matrix(self) -> list[dict[str, Any]]:
        scripts = sorted({
            str(item) for item in self.input_facts.get("baseline_scripts", [])
        })
        if self.matrix_scope() == "all":
            return [self.scenario_info(name) for name in scripts]
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
        expected_match = re.search(
            r'\b(expected_hash|expected)\s*=\s*["\']?([0-9a-fA-F]{64})["\']?',
            text,
        )
        expected = expected_match.group(2).lower() if expected_match else None
        config_match = re.search(r'(?:-F|--config)\s+([A-Za-z0-9_./{}-]+)', text)
        config = config_match.group(1) if config_match else ""
        if config.startswith("$model_dir/"):
            config = config[len("$model_dir/"):]
        config_path = model_root / config
        list_path = config_path.with_suffix(".list") if config else pathlib.Path()
        list_file = (
            str(list_path.relative_to(model_root))
            if config and list_path.is_absolute() and list_path.is_relative_to(model_root)
            else str(pathlib.Path(config).with_suffix(".list")) if config else ""
        )
        return {
            "script": script,
            "name": pathlib.Path(script).stem,
            "golden": golden,
            "config": config,
            "list": list_file,
            "expected_sha256": expected,
            "expected_variable": expected_match.group(1) if expected_match else None,
            "oracle_class": (
                "ANCHORED_EXPECTED_SHA"
                if expected
                else "C_BASELINE_DIFFERENTIAL_ONLY"
            ),
            "parse_status": (
                "PASS"
                if golden and config and config_path.is_file() and list_path.is_file()
                else "FAIL"
            ),
            "script_sha256": file_hash(path),
            "config_sha256": file_hash(config_path) if config_path.is_file() else None,
            "list_sha256": file_hash(list_path) if list_path.is_file() else None,
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
        try:
            matrix_scope = self.matrix_scope()
            scenarios = self.discover_matrix()
        except ValueError as error:
            result = {
                "status": "INFRASTRUCTURE_FAILURE",
                "reason": str(error),
                "matrix_scope": os.environ.get("DSC_CICD_MATRIX_SCOPE"),
            }
            write_json(artifact / "matrix-receipt.json", result)
            return result
        evidence_summary = self.matrix_evidence_summary(scenarios)
        if len(scenarios) < 1:
            result = {
                "status": "INFRASTRUCTURE_FAILURE",
                "reason": "no baseline scripts discovered",
                "matrix_scope": matrix_scope,
                "evidence_summary": evidence_summary,
            }
            write_json(artifact / "matrix-receipt.json", result)
            return result
        if not all(scenario.get("parse_status") == "PASS" for scenario in scenarios):
            result = {
                "status": "INFRASTRUCTURE_FAILURE",
                "reason": "one or more matrix scripts lack a parseable golden or config",
                "matrix_scope": matrix_scope,
                "scenarios": scenarios,
                "evidence_summary": evidence_summary,
            }
            write_json(artifact / "matrix-receipt.json", result)
            return result
        base_model = self.copy_model("baseline")
        overlay_model: pathlib.Path | None = None
        baseline_decode_results: list[dict[str, Any]] = []

        def persist_matrix_failure(result: dict[str, Any]) -> dict[str, Any]:
            result.setdefault("matrix_scope", matrix_scope)
            result.setdefault("matrix_profiles_selected", len(scenarios))
            result.setdefault("matrix_scripts_discovered", len(self.input_facts.get("baseline_scripts", [])))
            result.setdefault("evidence_summary", evidence_summary)
            roots: list[pathlib.Path] = [base_model, base_model.parent, self.root]
            if overlay_model is not None:
                roots[0:0] = [overlay_model, overlay_model.parent]
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
                expected = scenario.get("expected_sha256")
                expected_match = actual == expected if expected else None
                baseline_pass = bool(
                    result["returncode"] == 0
                    and actual
                    and expected_match is not False
                )
                baseline_results.append({
                    "scenario": scenario,
                    "status": "PASS" if baseline_pass else "FAIL",
                    "command": result,
                    "sha256": actual,
                    "size_bytes": golden.stat().st_size if golden.is_file() else None,
                    "oracle_class": scenario.get("oracle_class"),
                    "expected_sha256": expected,
                    "expected_sha256_match": expected_match,
                })
            if not all(item["status"] == "PASS" for item in baseline_results):
                return persist_matrix_failure({
                    "status": "INFRASTRUCTURE_FAILURE",
                    "reason": "baseline matrix failed",
                    "baseline": baseline_results,
                })

            # The encode scripts above only prepare anchored input bitstreams.
            # Decode is the first replacement phase: the immutable C model
            # produces the frame oracle before any Verilator overlay is built.
            baseline_decode_root = base_model.parent / "decode-original-c"
            baseline_binary = base_model / "source" / "dsc"
            for baseline in baseline_results:
                scenario = baseline["scenario"]
                decode = self.run_decode_frame(
                    base_model,
                    baseline_binary,
                    scenario,
                    base_model / scenario["golden"],
                    baseline_decode_root / safe_identifier(str(scenario["name"])),
                )
                decode["scenario"] = scenario
                baseline_decode_results.append(decode)
            if not all(item.get("status") == "PASS" for item in baseline_decode_results):
                return persist_matrix_failure({
                    "status": "INFRASTRUCTURE_FAILURE",
                    "reason": "original C full-frame decode oracle failed",
                    "phase_order": ["DECODE", "ENCODE"],
                    "baseline": baseline_results,
                    "decode": {
                        "status": "FAIL",
                        "oracle": baseline_decode_results,
                    },
                })

            overlay_temp = pathlib.Path(tempfile.mkdtemp(prefix="dsc-cicd-overlay-", dir=str(self.root / "tmp")))
            overlay_model = overlay_temp / base_model.name
            shutil.copytree(base_model, overlay_model, ignore=shutil.ignore_patterns(".git", "__pycache__", "target", "build", "dsc-rs", "operator_bittrue"))
            candidate_sv = artifact / str(candidate["path"])
            overlay_copy_sv = overlay_model / "candidate.sv"
            shutil.copy2(candidate_sv, overlay_copy_sv)
            module = str(candidate.get("module") or self.module_name(candidate_sv.read_text(encoding="utf-8")))
            try:
                overlay_paths = self.write_overlay_sources(
                    contract,
                    overlay_model / "source",
                    module,
                    overlay_copy_sv,
                )
            except RuntimeError as error:
                # An incomplete deterministic binding is a real C boundary,
                # not permission to pass a guessed pointer or dummy state.
                return persist_matrix_failure({
                    "status": "COMPOSITION_BLOCKED",
                    "reason": f"generated caller adapter could not bind the frozen DUT interface: {error}",
                    "baseline": baseline_results,
                    "composition": {
                        "status": "C_BOUNDARY",
                        "adapter_status": "UNRESOLVED",
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
            overlay_receipt = self.run_overlay_rewriter(
                contract,
                overlay_model / "source",
                overlay_paths["header"],
                allow_residual_symbol_alias=bool(
                    (overlay_paths.get("composition", {}) or {}).get(
                        "residual_symbol_alias_routes_to_dispatcher"
                    )
                ),
            )
            if overlay_receipt.get("status") != "PASS":
                return persist_matrix_failure({
                    "status": "INFRASTRUCTURE_FAILURE",
                    "reason": "Clang overlay rewrite failed",
                    "baseline": baseline_results,
                    "overlay": overlay_receipt,
                })
            frozen_input_ports = [
                str(port.get("name"))
                for port in contract.get("interface", {}).get("ports", [])
                if port.get("direction") == "input"
            ]
            frozen_input_count = len(frozen_input_ports)
            call_sites = [
                site for site in overlay_receipt.get("call_sites", [])
                if isinstance(site, dict)
            ]
            call_site_arities = [len(site.get("arguments", [])) for site in call_sites]
            composition = dict(overlay_paths.get("composition", {}) or {})
            composition["native_call_site_argument_counts"] = call_site_arities
            composition["native_call_site_count"] = len(call_sites)
            composition["frozen_input_count"] = frozen_input_count
            composition["adapter_input_count"] = composition.get("rtl_input_count")
            composition["adapter_status"] = composition.get("status", "UNRESOLVED")
            adapter_ports = [
                str(value) for value in composition.get("frozen_input_ports", [])
            ]
            if (
                composition.get("status") != "PASS"
                or composition.get("rtl_input_count") != frozen_input_count
                or adapter_ports != frozen_input_ports
                or len(composition.get("rtl_bindings", [])) != frozen_input_count
            ):
                # Native C callsites are allowed to use the function's real
                # pointer/state signature.  The generated adapter is the
                # composition boundary: it must bind every frozen RTL input
                # exactly once, without dummy state or guessed arguments.
                return persist_matrix_failure({
                    "status": "COMPOSITION_BLOCKED",
                    "reason": "generated caller adapter does not provide the frozen DUT interface; retain C boundary",
                    "baseline": baseline_results,
                    "overlay": overlay_receipt,
                    "composition": dict(composition, status="C_BOUNDARY", c_only_status="PASS", rtl_modes="NOT_RUN"),
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
            binary = overlay_model / "source" / "dsc"

            decode_mode_results: dict[str, Any] = {}
            decode_output_root = overlay_model.parent / "decode-verilator-overlay"
            decode_oracles = {
                str(item["scenario"]["script"]): item
                for item in baseline_decode_results
            }
            for mode in ("C_ONLY", "SHADOW", "RTL_RETURN"):
                scenario_results = []
                for baseline in baseline_results:
                    scenario = baseline["scenario"]
                    oracle = decode_oracles[str(scenario["script"])]
                    decode = self.run_decode_frame(
                        overlay_model,
                        binary,
                        scenario,
                        base_model / scenario["golden"],
                        decode_output_root
                        / mode.lower()
                        / safe_identifier(str(scenario["name"])),
                        mode=mode,
                    )
                    execution_status = decode.get("status")
                    output_file = pathlib.Path(str(decode.get("output_file", "")))
                    oracle_file = pathlib.Path(str(oracle.get("output_file", "")))
                    byte_equal = self.files_byte_equal(output_file, oracle_file)
                    metrics = decode.get("overlay_metrics", {}) or {}
                    mismatch_count = int(metrics.get("mismatches", 0))
                    scenario_pass = bool(
                        execution_status == "PASS"
                        and byte_equal
                        and mismatch_count == 0
                    )
                    if mode == "C_ONLY":
                        replacement_status = (
                            "C_PATH_REACHED"
                            if metrics.get("replacement_reached")
                            else "NOT_REACHED"
                        )
                    else:
                        replacement_status = (
                            "RTL_EXERCISED"
                            if metrics.get("rtl_exercised")
                            else "NOT_REACHED"
                        )
                    decode.update({
                        "scenario": scenario,
                        "status": "PASS" if scenario_pass else "FAIL",
                        "execution_status": execution_status,
                        "oracle_sha256": oracle.get("sha256"),
                        "oracle_size_bytes": oracle.get("size_bytes"),
                        "byte_for_byte_match": byte_equal,
                        "mismatch_count": mismatch_count,
                        "replacement_status": replacement_status,
                    })
                    scenario_results.append(decode)
                total_calls = sum(
                    int((item.get("overlay_metrics", {}) or {}).get("calls", 0))
                    for item in scenario_results
                )
                total_rtl_invocations = sum(
                    int((item.get("overlay_metrics", {}) or {}).get("rtl_invocations", 0))
                    for item in scenario_results
                )
                coverage_status = (
                    "RTL_EXERCISED"
                    if total_rtl_invocations > 0
                    else "C_PATH_REACHED"
                    if total_calls > 0
                    else "NOT_REACHED"
                )
                decode_mode_results[mode] = {
                    "status": (
                        "PASS"
                        if all(item["status"] == "PASS" for item in scenario_results)
                        else "FAIL"
                    ),
                    "coverage_status": coverage_status,
                    "total_calls": total_calls,
                    "total_rtl_invocations": total_rtl_invocations,
                    "scenarios": scenario_results,
                }

            decode_modes_pass = all(
                decode_mode_results.get(mode, {}).get("status") == "PASS"
                for mode in ("C_ONLY", "SHADOW", "RTL_RETURN")
            )
            decode_shadow_rtl = int(
                decode_mode_results.get("SHADOW", {}).get("total_rtl_invocations", 0)
            )
            decode_return_rtl = int(
                decode_mode_results.get("RTL_RETURN", {}).get("total_rtl_invocations", 0)
            )
            decode_coverage_status = (
                "RTL_EXERCISED"
                if decode_shadow_rtl > 0 and decode_return_rtl > 0
                else "PARTIAL"
                if decode_shadow_rtl > 0 or decode_return_rtl > 0
                else "NOT_REACHED"
            )

            # Encode runs second.  The legacy top-level `modes` field remains
            # an alias for these rows so existing receipt readers stay valid.
            mode_results: dict[str, Any] = {}
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
                    metrics = self.parse_overlay_metrics(output)
                    mismatch_count = int(metrics.get("mismatches", 0))
                    expected = scenario.get("expected_sha256")
                    expected_match = actual == expected if expected else None
                    baseline_match = actual == baseline["sha256"]
                    scenario_pass = bool(
                        command["returncode"] == 0
                        and baseline_match
                        and expected_match is not False
                        and mismatch_count == 0
                    )
                    scenario_results.append({
                        "scenario": scenario,
                        "status": "PASS" if scenario_pass else "FAIL",
                        "command": command,
                        "sha256": actual,
                        "size_bytes": golden.stat().st_size if golden.is_file() else None,
                        "baseline_sha256": baseline["sha256"],
                        "baseline_sha256_match": baseline_match,
                        "oracle_class": scenario.get("oracle_class"),
                        "expected_sha256": expected,
                        "expected_sha256_match": expected_match,
                        "mismatch_count": mismatch_count,
                        "overlay_metrics": metrics,
                        "replacement_status": (
                            "RTL_EXERCISED"
                            if metrics.get("rtl_exercised")
                            else "C_PATH_REACHED"
                            if metrics.get("replacement_reached")
                            else "NOT_REACHED"
                        ),
                    })
                total_calls = sum(
                    int((item.get("overlay_metrics", {}) or {}).get("calls", 0))
                    for item in scenario_results
                )
                total_rtl_invocations = sum(
                    int((item.get("overlay_metrics", {}) or {}).get("rtl_invocations", 0))
                    for item in scenario_results
                )
                mode_results[mode] = {
                    "status": "PASS" if all(item["status"] == "PASS" for item in scenario_results) else "FAIL",
                    "coverage_status": (
                        "RTL_EXERCISED"
                        if total_rtl_invocations > 0
                        else "C_PATH_REACHED"
                        if total_calls > 0
                        else "NOT_REACHED"
                    ),
                    "total_calls": total_calls,
                    "total_rtl_invocations": total_rtl_invocations,
                    "scenarios": scenario_results,
                }
            overlay_receipt = scrub_paths(overlay_receipt, [base_model, overlay_model, self.root])
            compile_receipt = scrub_paths(compile_receipt, [base_model, overlay_model, self.root])
            mode_results = scrub_paths(mode_results, [base_model, overlay_model, self.root])
            decode_mode_results = scrub_paths(
                decode_mode_results,
                [base_model, base_model.parent, overlay_model, overlay_model.parent, self.root],
            )
            scrubbed_decode_oracles = scrub_paths(
                baseline_decode_results,
                [base_model, base_model.parent, overlay_model, overlay_model.parent, self.root],
            )
            encode_modes_pass = all(
                mode_results.get(mode, {}).get("status") == "PASS"
                for mode in ("C_ONLY", "SHADOW", "RTL_RETURN")
            )
            combined_shadow_rtl = decode_shadow_rtl + int(
                mode_results.get("SHADOW", {}).get("total_rtl_invocations", 0)
            )
            combined_return_rtl = decode_return_rtl + int(
                mode_results.get("RTL_RETURN", {}).get("total_rtl_invocations", 0)
            )
            replacement_coverage_pass = (
                combined_shadow_rtl > 0 and combined_return_rtl > 0
            )
            all_phases_pass = bool(
                decode_modes_pass
                and encode_modes_pass
                and replacement_coverage_pass
            )
            decode_receipt = {
                "status": "PASS" if decode_modes_pass else "FAIL",
                "execution_order": 1,
                "oracle": "ORIGINAL_C_SOURCE",
                "replacement": "VERILOG_VIA_VERILATOR_CXX",
                "comparison": "FULL_DECODED_FRAME_BYTE_FOR_BYTE",
                "coverage_status": decode_coverage_status,
                "oracle_frames": scrubbed_decode_oracles,
                "modes": decode_mode_results,
            }
            encode_receipt = {
                "status": "PASS" if encode_modes_pass else "FAIL",
                "execution_order": 2,
                "oracle": "ORIGINAL_C_SOURCE",
                "replacement": "VERILOG_VIA_VERILATOR_CXX",
                "comparison": "FULL_ENCODED_BITSTREAM_BYTE_FOR_BYTE",
                "modes": mode_results,
            }
            result = {
                "status": "PASS" if all_phases_pass else "FAIL",
                "matrix_scope": matrix_scope,
                "matrix_profiles_selected": len(scenarios),
                "matrix_scripts_discovered": len(self.input_facts.get("baseline_scripts", [])),
                "evidence_summary": evidence_summary,
                "phase_order": ["DECODE", "ENCODE"],
                "scenarios": [item["scenario"] for item in baseline_results],
                "baseline": scrub_paths(baseline_results, [base_model, overlay_model, self.root]),
                "overlay": overlay_receipt,
                "compile": compile_receipt,
                "composition": composition,
                "decode": decode_receipt,
                "encode": encode_receipt,
                "replacement_coverage": {
                    "status": "PASS" if replacement_coverage_pass else "FAIL",
                    "policy": (
                        "SHADOW and RTL_RETURN must each invoke the Verilated replacement "
                        "in at least one full-frame Decode or Encode scenario"
                    ),
                    "shadow_rtl_invocations": combined_shadow_rtl,
                    "rtl_return_rtl_invocations": combined_return_rtl,
                    "decode_coverage_status": decode_coverage_status,
                    "encode_shadow_coverage_status": mode_results.get("SHADOW", {}).get("coverage_status"),
                    "encode_rtl_return_coverage_status": mode_results.get("RTL_RETURN", {}).get("coverage_status"),
                },
                "modes": mode_results,
                "candidate": candidate.get("candidate"),
                "execution_status": "EXECUTED_NOW",
            }
            write_json(artifact / "shadow-receipt.json", result["modes"]["SHADOW"])
            write_json(artifact / "rtl-return-receipt.json", result["modes"]["RTL_RETURN"])
            write_json(artifact / "decode-receipt.json", result["decode"])
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
                "receipt": self.artifact_reference(rejected_artifact / "rejection-receipt.json"),
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
                self.update_state(cid, "PROMOTED", "CACHE_REUSED", artifacts=[self.artifact_reference(artifact)], extra={
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
                promotion = self.promote_library_component(contract, item, artifact, result)
                result["library_promotion"] = promotion
                result["promotion_status"] = promotion.get("status")
                if promotion.get("status") == "AWAITING_HUMAN_APPROVAL":
                    result["status"] = "PASS"
                    self.update_state(
                        cid,
                        "BITSTREAM_PASS",
                        "PASS",
                        artifacts=[self.artifact_reference(artifact)],
                        extra={
                            "promotion_status": promotion.get("status"),
                            "pending_rtl_sha256": promotion.get("rtl_sha256"),
                            "promotion_approval_file": (promotion.get("approval") or {}).get("approval_file"),
                        },
                    )
                self.append_result(result)
                return result
            except (OSError, RuntimeError, ValueError, subprocess.SubprocessError) as error:
                self.update_state(cid, "DISCOVERED", "INFRASTRUCTURE_FAILURE", artifacts=[self.artifact_reference(artifact)], failure=str(error))
                result = {"contract_id": cid, "status": "INFRASTRUCTURE_FAILURE", "reason": str(error)}
                self.append_result(result)
                return result
        try:
            self.update_state(cid, "CONTRACT_LOCKED", "EXECUTING")
            generation = self.generate_artifacts(contract, item, artifact)
            self.update_state(cid, "RTL_GENERATED", generation.get("status", "FAIL"), artifacts=[self.artifact_reference(artifact)], extra={
                "model_calls": generation.get("model_calls", 0),
                "token_count": generation.get("tokens", 0),
            })
            if generation.get("status") != "PASS":
                result = {"contract_id": cid, "status": generation.get("status", "GENERATION_FAILED"), "generation": generation}
                self.append_result(result)
                return result
            unit = self.unit_verify(contract, artifact)
            unit_status = "PASS" if unit.get("promoted_candidate") else unit.get("verification_status", "UNPROVED")
            self.update_state(cid, "UNIT_VERIFIED", unit_status, artifacts=[self.artifact_reference(artifact)], extra={
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
                artifacts=[self.artifact_reference(artifact)],
                failure=matrix_failure,
            )
            self.update_state(
                cid,
                "RTL_RETURN_PASS",
                "PASS" if rtl_status else "FAIL",
                artifacts=[self.artifact_reference(artifact)],
                failure=matrix_failure,
            )
            dependency = self.dependency_verify(contract, item, artifact, unit, matrix)
            self.update_state(
                cid,
                "DEPENDENCIES_VERIFIED",
                dependency.get("status", "FAIL"),
                artifacts=[self.artifact_reference(artifact)],
                failure=dependency.get("failure_reason"),
            )
            bitstream_status = matrix.get("status") == "PASS"
            self.update_state(
                cid,
                "BITSTREAM_PASS",
                "PASS" if bitstream_status else "FAIL",
                artifacts=[self.artifact_reference(artifact)],
                failure=matrix_failure,
            )
            result = {
                "contract_id": cid,
                "status": "FAILED" if not (bitstream_status and dependency.get("status") == "PASS") else "PROMOTED",
                "generation": generation,
                "unit": unit,
                "matrix": matrix,
                "dependency": dependency,
                "rejected_candidates": rejected_candidates,
            }
            final = result["status"]
            promotion = None
            if final == "PROMOTED":
                promotion = self.promote_library_component(contract, item, artifact, result)
                result["library_promotion"] = promotion
                result["promotion_status"] = promotion.get("status")
                if promotion.get("status") in {"AWAITING_HUMAN_APPROVAL", "VERIFIED_REFRESH"}:
                    final = "PASS"
                    result["status"] = final
            self.update_state(
                cid,
                "PROMOTED" if final == "PROMOTED" else "BITSTREAM_PASS",
                final,
                artifacts=[self.artifact_reference(artifact)],
                failure=None if final != "FAILED" else (matrix_failure or dependency.get("failure_reason")),
                extra=(
                    {
                        "promotion_status": promotion.get("status"),
                        "pending_rtl_sha256": promotion.get("rtl_sha256"),
                        "promotion_approval_file": (promotion.get("approval") or {}).get("approval_file"),
                    }
                    if promotion and promotion.get("status") in {"AWAITING_HUMAN_APPROVAL", "VERIFIED_REFRESH"}
                    else None
                ),
            )
            self.append_result(result)
            for name in ("shards", "shard-results", "oracle-build", "candidate-build", "generated"):
                path = artifact / name
                if path.is_dir() and name != "generated":
                    shutil.rmtree(path, ignore_errors=True)
            return result
        except (OSError, RuntimeError, ValueError, subprocess.SubprocessError) as error:
            self.update_state(cid, "DISCOVERED", "INFRASTRUCTURE_FAILURE", artifacts=[self.artifact_reference(artifact)], failure=str(error))
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
            verified_refresh = status == "PASS" and result.get("promotion_status") == "VERIFIED_REFRESH"
            valid = (status in ("PROMOTED", "CACHE_REUSED") or verified_refresh) and (artifact / "unit-receipt.json").is_file() and (artifact / "bitstream-receipt.json").is_file()
            entries[item["cache_key"]] = {
                "schema_version": 2,
                "cache_key": item["cache_key"],
                "contract_id": item["contract_id"],
                "artifact_dir": self.artifact_reference(artifact),
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

    @staticmethod
    def _reason_text(value: Any) -> list[str]:
        if isinstance(value, str) and value:
            return [value]
        if isinstance(value, list):
            return [str(item) for item in value if item]
        return []

    def report_blockers(self) -> list[str]:
        """Aggregate current plan, run, and durable-state blockers.

        Reports must not claim a clean run merely because a later no-work
        invocation produced no new result.  Keep the latest executable
        failure visible alongside planner blockers; historical runs remain in
        the regression dashboard and are not folded into this current list.
        """
        blockers: list[str] = list(self.input_facts.get("errors", []))
        current_blocker_contracts: set[str] = set()
        for blocked in self.plan.get("blocked_contracts", []):
            cid = str(blocked.get("contract_id", "contract"))
            current_blocker_contracts.add(cid)
            for reason in blocked.get("reasons", []) or []:
                blockers.append(f"{cid}: {reason}")
        terminal = {
            "BLOCKED",
            "FAILED",
            "INFRASTRUCTURE_FAILURE",
            "GENERATION_REQUIRED",
            "GENERATION_FAILED",
            "COUNTEREXAMPLE",
            "UNPROVED",
            "UNSUPPORTED",
        }
        for result in self.run_results:
            status = str(result.get("status", ""))
            promotion = result.get("library_promotion", {}) or {}
            if promotion.get("status") == "AWAITING_HUMAN_APPROVAL":
                blockers.append(f"{result.get('contract_id', 'contract')}: human_promotion_approval_required")
            if status not in terminal:
                continue
            cid = str(result.get("contract_id", "contract"))
            current_blocker_contracts.add(cid)
            reasons: list[str] = []
            reasons.extend(self._reason_text(result.get("reason")))
            for section in ("generation", "unit", "matrix", "dependency"):
                value = result.get(section, {}) or {}
                reasons.extend(self._reason_text(value.get("reason")))
                reasons.extend(self._reason_text(value.get("failure_reason")))
            if not reasons:
                reasons.append(status)
            blockers.extend(f"{cid}: {reason}" for reason in reasons)
        for item in self.state.get("contracts", []):
            status = str(item.get("status", ""))
            if item.get("promotion_status") == "AWAITING_HUMAN_APPROVAL":
                blockers.append(f"{item.get('contract_id', 'contract')}: human_promotion_approval_required")
            if status not in terminal:
                continue
            cid = str(item.get("contract_id", "contract"))
            current_blocker_contracts.add(cid)
            reasons = self._reason_text(item.get("failure_reason")) or [status]
            blockers.extend(f"{cid}: {reason}" for reason in reasons)
        # A later no-work plan can append DEFERRED/BLOCKED state and otherwise
        # hide the last executable failure.  Walk each durable history
        # backwards, stopping at the newest successful terminal state and
        # retaining only the latest failure before planner-only events.
        failure_statuses = terminal - {"BLOCKED"}
        success_statuses = {"PASS", "PROMOTED", "CACHE_REUSED"}
        for item in self.previous_state.get("contracts", []):
            cid = str(item.get("contract_id", "contract"))
            if cid in current_blocker_contracts:
                continue
            for event in reversed(item.get("history", []) or []):
                event_status = str(event.get("status", ""))
                if event_status in {"DEFERRED", "BLOCKED"}:
                    continue
                if event_status in success_statuses:
                    break
                if event_status in failure_statuses:
                    reason = str(event.get("failure_reason") or event_status)
                    blockers.append(f"{cid}: {reason}")
                    break
        return sorted(set(str(value) for value in blockers if value))

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
                "rtl_materialization": result.get("generation", {}).get("execution_status", "NOT_RUN"),
                "model_calls": result.get("generation", {}).get("model_calls", 0),
                "tokens": result.get("generation", {}).get("tokens", 0),
                "unit_status": result.get("unit", {}).get("verification_status"),
                "dependency_status": result.get("dependency", {}).get("status"),
                "matrix_status": result.get("matrix", {}).get("status"),
                "matrix_modes": {
                    mode: matrix.get("modes", {}).get(mode, {}).get("status")
                    for mode in ("C_ONLY", "SHADOW", "RTL_RETURN")
                },
                "decode_status": (matrix.get("decode", {}) or {}).get("status"),
                "decode_coverage_status": (matrix.get("decode", {}) or {}).get("coverage_status"),
                "replacement_coverage_status": (matrix.get("replacement_coverage", {}) or {}).get("status"),
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
            "matrix_scope": os.environ.get("DSC_CICD_MATRIX_SCOPE", "smoke").strip().lower() or "smoke",
            "matrix_scripts_discovered": len(self.input_facts.get("baseline_scripts", [])),
            "results": result_lines,
            "blockers": self.report_blockers(),
            "receipt_policy": {
                "fresh_run": "EXECUTED_NOW",
                "cache_hit": "REUSED_VERIFIED_RECEIPT",
                "accepted_rtl_refresh": "REUSED_ACCEPTED_RTL; deterministic verification still executes",
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
            f"- matrix scope: {report['matrix_scope']}",
            f"- baseline scripts discovered: {len(self.input_facts.get('baseline_scripts', []))}",
            "",
            "## Results",
            "",
        ]
        for value in result_lines:
            lines.append(f"- {value['contract_id']}: {value['status']} ({value['execution_status']}); rtl={value['rtl_materialization']}; unit={value['unit_status']}; dependency={value['dependency_status']}; matrix={value['matrix_status']}; library={value['library_promotion'].get('status', 'NOT_ATTEMPTED')}")
            lines.append(
                f"  - executed vectors/shards: {value['executed_vectors']}/{value['executed_shards']}; "
                f"shard seconds: {value['shard_durations_seconds']}; "
                f"domain_proof_complete={value['domain_proof_complete']}; "
                f"formal={value['formal_proof_status']}/{value['formal_proof_complete']}; "
                f"strategy={value['vector_strategy']}"
            )
            lines.append(f"  - matrix modes: {json.dumps(value['matrix_modes'], sort_keys=True)}")
            lines.append(
                f"  - decode: {value['decode_status']} "
                f"({value['decode_coverage_status']}); replacement coverage: "
                f"{value['replacement_coverage_status']}"
            )
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
        successful = any(
            result.get("status") in ("PROMOTED", "CACHE_REUSED")
            or (
                result.get("status") == "PASS"
                and result.get("promotion_status") in {"VERIFIED_REFRESH", "AWAITING_HUMAN_APPROVAL"}
            )
            for result in self.run_results
        )
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
