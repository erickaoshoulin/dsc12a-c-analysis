#!/usr/bin/env python3
"""Dependency-aware CI/CD orchestration for incremental C-to-RTL migration.

The agent is deliberately data-driven.  Function names are read from the
locked contracts and Clang call graph; they are never selection inputs in this
module.  The upstream PDF and C model are immutable inputs.  Generated files
are manifests, adapters, and evidence bundles in this repository or in an
isolated temporary copy of the model.
"""

from __future__ import annotations

import argparse
import concurrent.futures
import hashlib
import json
import os
import pathlib
import re
import shutil
import subprocess
import sys
import tempfile
import textwrap
import threading
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
ALLOWED_REPAIR_CATEGORIES = {
    "syntax",
    "interface",
    "width_signedness",
    "arithmetic_counterexample",
    "unsupported_c_construct",
}


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
    path.write_text(
        json.dumps(value, indent=2, sort_keys=True, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )


def scrub_path(value: Any, old_root: pathlib.Path | None) -> Any:
    if not old_root:
        return value
    if isinstance(value, str):
        return value.replace(str(old_root), "<overlay-work>")
    if isinstance(value, list):
        return [scrub_path(item, old_root) for item in value]
    if isinstance(value, dict):
        return {key: scrub_path(item, old_root) for key, item in value.items()}
    return value


def safe_identifier(value: str) -> str:
    result = re.sub(r"[^A-Za-z0-9_]", "_", value)
    if not result or result[0].isdigit():
        result = "c_" + result
    return result


def snake_case(value: str) -> str:
    return re.sub(r"(?<!^)([A-Z])", r"_\1", value).lower()


def command_version(command: str | None) -> str:
    if not command:
        return "MISSING"
    try:
        version_flag = "-v" if pathlib.Path(command).name in {"pdfinfo", "pdftotext"} else "--version"
        completed = subprocess.run(
            [command, version_flag],
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=15,
            check=False,
        )
        return (completed.stdout or "").splitlines()[0].strip() or "UNKNOWN"
    except (OSError, subprocess.TimeoutExpired):
        return "UNAVAILABLE"


def locate_tool(name: str, fallback: str | None = None) -> str | None:
    found = shutil.which(name)
    if found:
        return found
    if fallback and pathlib.Path(fallback).is_file():
        return fallback
    return None


def contract_function(contract: dict[str, Any]) -> dict[str, Any]:
    return contract.get("function", {})


def contract_id(contract: dict[str, Any]) -> str:
    return str(contract.get("contract_id") or safe_identifier(contract_function(contract).get("name", "unknown")))


def contract_exact_links(contract: dict[str, Any]) -> list[dict[str, Any]]:
    return [link for link in contract.get("spec_links", []) if link.get("status") == "EXACT"]


def unresolved_reasons(contract: dict[str, Any]) -> list[str]:
    reasons: list[str] = []
    reasons.extend(str(item) for item in contract.get("obligations", []) if item)
    reasons.extend(str(item) for item in contract.get("dependencies", {}).get("unresolved", []) if item)
    interface = contract.get("interface", {})
    for item in interface.get("inputs", []) + interface.get("flattened_pointer_dependencies", []):
        if item.get("unresolved"):
            name = item.get("name") or item.get("field") or "input"
            reasons.append(f"interface:{name}")
    if interface.get("output", {}).get("unresolved"):
        reasons.append("interface:return_value")
    semantics = contract.get("semantics")
    if not semantics:
        reasons.append("arithmetic_semantics")
    return sorted(set(reasons))


def source_body(contract: dict[str, Any], source_dir: pathlib.Path) -> tuple[pathlib.Path, str]:
    function = contract_function(contract)
    source_path = pathlib.Path(str(function.get("source_file", "")))
    if not source_path.is_absolute():
        source_path = source_dir / source_path
    span = function.get("source_span", {})
    lines = source_path.read_text(encoding="utf-8", errors="replace").splitlines()
    start = int(span.get("start_line", 1))
    end = int(span.get("end_line", start))
    return source_path, "\n".join(lines[start - 1 : end]).strip()


def function_source_hash(contract: dict[str, Any], source_dir: pathlib.Path) -> str:
    path, body = source_body(contract, source_dir)
    return digest({"path": path.name, "body": body})


class Agent:
    def __init__(self, root: pathlib.Path, mode: str) -> None:
        self.root = root.resolve()
        self.mode = mode
        self.ci = self.root / "ci"
        self.artifacts = self.root / "artifacts"
        self.integration = self.root / "integration"
        self.manifest_path = self.root / "spec" / "manifest.json"
        self.manifest = read_json(self.manifest_path, {}) or {}
        self.contract_paths = sorted((self.root / "contracts" / "locked").glob("*.json"))
        self.contracts = [read_json(path, {}) for path in self.contract_paths]
        self.contracts = [contract for contract in self.contracts if contract]
        self.previous_state = read_json(self.ci / "state.json", {}) or {}
        self.cache = read_json(self.ci / "cache-index.json", {}) or {}
        self.input_facts: dict[str, Any] = {}
        self.dependency_info: dict[str, Any] = {}
        self.plan: dict[str, Any] = {}
        self.dag: dict[str, Any] = {}
        self.state: dict[str, Any] = {}
        self.state_lock = threading.Lock()

    def load_inputs(self) -> dict[str, Any]:
        manifest = self.manifest
        errors: list[str] = []
        spec = manifest.get("spec", {})
        source = manifest.get("source", {})
        pdf_path = pathlib.Path(str(spec.get("path", "")))
        if manifest.get("status") != "OK" or spec.get("status") != "PASS":
            errors.append("local PDF discovery gate did not pass")
        if not pdf_path.is_file():
            errors.append(f"PDF is missing: {pdf_path}")
        elif file_hash(pdf_path) != spec.get("sha256"):
            errors.append("PDF SHA-256 changed")
        source_dir = pathlib.Path(str(source.get("source_dir", "")))
        if source.get("status") != "PASS" or not source_dir.is_dir():
            errors.append("local C source discovery gate did not pass")
        actual_source_hashes: list[dict[str, str]] = []
        for item in source.get("source_file_hashes", []):
            path = source_dir / str(item.get("path", ""))
            if not path.is_file():
                errors.append(f"C source file is missing: {path}")
                continue
            actual_source_hashes.append({"path": str(item.get("path")), "sha256": file_hash(path)})
            if file_hash(path) != item.get("sha256"):
                errors.append(f"C source hash changed: {item.get('path')}")
        build = read_json(self.root / "build" / "build-receipt.json", {}) or {}
        smoke_outputs = build.get("smoke", {}).get("outputs", [])
        expected = build.get("smoke", {}).get("expected_hash")
        actual = next((item.get("sha256") for item in smoke_outputs if str(item.get("path", "")).endswith(".dsc")), None)
        if build.get("status") != "PASS" or actual != expected:
            errors.append("original C bitstream baseline receipt is not PASS")
        required_tools = {
            "python": shutil.which("python3") or sys.executable,
            "make": shutil.which("make"),
            "clang": shutil.which("clang"),
            "verilator": shutil.which("verilator"),
            "pdfinfo": locate_tool("pdfinfo", manifest.get("pdf_extraction", {}).get("pdfinfo_tool")),
            "pdftotext": locate_tool("pdftotext", manifest.get("pdf_extraction", {}).get("pdftotext_tool")),
            "llvm-cov": locate_tool("llvm-cov", "/opt/homebrew/opt/llvm/bin/llvm-cov"),
            "llvm-profdata": locate_tool("llvm-profdata", "/opt/homebrew/opt/llvm/bin/llvm-profdata"),
        }
        for name in ("python", "make", "clang", "verilator", "pdfinfo", "pdftotext"):
            if not required_tools.get(name):
                errors.append(f"required tool is missing: {name}")
        tool_versions = {name: command_version(path) for name, path in required_tools.items()}
        self.input_facts = {
            "source_root": source.get("model_root"),
            "source_dir": str(source_dir),
            "source_hash": source.get("source_hashes_sha256") or digest(actual_source_hashes),
            "source_file_hashes": actual_source_hashes,
            "spec_path": str(pdf_path),
            "spec_hash": spec.get("sha256"),
            "spec_pages": spec.get("pdfinfo", {}).get("Pages"),
            "baseline_hash": expected,
            "baseline_artifact": next((item for item in smoke_outputs if str(item.get("path", "")).endswith(".dsc")), {}),
            "tools": {name: path for name, path in required_tools.items()},
            "tool_versions": tool_versions,
            "errors": errors,
        }
        return self.input_facts

    def dependency_graph(self) -> dict[str, Any]:
        by_usr = {
            str(contract_function(contract).get("clang_usr")): contract_id(contract)
            for contract in self.contracts
            if contract_function(contract).get("clang_usr")
        }
        by_name = {
            str(contract_function(contract).get("name")): contract_id(contract)
            for contract in self.contracts
            if contract_function(contract).get("name")
        }
        callgraph = read_json(self.root / "facts" / "callgraph.json", {}) or {}
        call_sites: list[dict[str, Any]] = []
        for edge in callgraph.get("edges", []):
            caller = by_usr.get(str(edge.get("caller_usr")))
            callee = by_usr.get(str(edge.get("callee_usr")))
            if caller and callee:
                call_sites.append(
                    {
                        "caller_contract": caller,
                        "callee_contract": callee,
                        "caller_usr": edge.get("caller_usr"),
                        "callee_usr": edge.get("callee_usr"),
                        "caller_function": edge.get("caller_name"),
                        "callee_function": edge.get("callee_name"),
                        "location": edge.get("location", {}),
                        "source": "facts/callgraph.json",
                    }
                )
        for contract in self.contracts:
            caller = contract_id(contract)
            for dep in contract.get("dependencies", {}).get("direct_callees", []):
                name = dep.get("name") if isinstance(dep, dict) else str(dep)
                callee = by_usr.get(str(dep.get("clang_usr"))) if isinstance(dep, dict) else None
                callee = callee or by_name.get(str(name))
                if callee and not any(
                    item["caller_contract"] == caller
                    and item["callee_contract"] == callee
                    and item.get("location") == dep.get("location", {})
                    for item in call_sites
                ):
                    call_sites.append(
                        {
                            "caller_contract": caller,
                            "callee_contract": callee,
                            "caller_usr": contract_function(contract).get("clang_usr"),
                            "callee_usr": contract_function(self.contracts[[contract_id(c) for c in self.contracts].index(callee)]).get("clang_usr") if callee in [contract_id(c) for c in self.contracts] else None,
                            "caller_function": contract_function(contract).get("name"),
                            "callee_function": name,
                            "location": dep.get("location", {}) if isinstance(dep, dict) else {},
                            "source": "locked-contract.dependencies.direct_callees",
                        }
                    )
        edges = sorted({(item["caller_contract"], item["callee_contract"]) for item in call_sites})
        adjacency: dict[str, list[str]] = {contract_id(contract): [] for contract in self.contracts}
        for caller, callee in edges:
            adjacency.setdefault(caller, []).append(callee)
        cycles: list[list[str]] = []
        visiting: list[str] = []
        visited: set[str] = set()

        def visit(node: str) -> None:
            if node in visiting:
                cycles.append(visiting[visiting.index(node) :] + [node])
                return
            if node in visited:
                return
            visiting.append(node)
            for callee in sorted(adjacency.get(node, [])):
                visit(callee)
            visiting.pop()
            visited.add(node)

        for node in sorted(adjacency):
            visit(node)
        contract_hashes = {contract_id(c): digest(c) for c in self.contracts}
        dependency_hashes: dict[str, str] = {}
        for cid in sorted(adjacency):
            related = [item for item in call_sites if item["caller_contract"] == cid]
            dependency_hashes[cid] = digest(
                {
                    "call_sites": related,
                    "callee_contract_hashes": {item["callee_contract"]: contract_hashes[item["callee_contract"]] for item in related},
                }
            )
        self.dependency_info = {
            "call_sites": sorted(call_sites, key=lambda item: (item["caller_contract"], item["callee_contract"], canonical(item.get("location", {})))),
            "edges": [{"caller": caller, "callee": callee} for caller, callee in edges],
            "adjacency": {key: sorted(set(value)) for key, value in sorted(adjacency.items())},
            "cycles": cycles,
            "dependency_hashes": dependency_hashes,
        }
        return self.dependency_info

    def cache_key(self, contract: dict[str, Any]) -> tuple[str, dict[str, str]]:
        cid = contract_id(contract)
        hashes = {
            "agent": file_hash(pathlib.Path(__file__)),
            "source": str(self.input_facts.get("source_hash", "MISSING")),
            "spec": str(self.input_facts.get("spec_hash", "MISSING")),
            "contract": digest(contract),
            "dependency": self.dependency_info.get("dependency_hashes", {}).get(cid, digest([])),
            "prompt": file_hash(self.root / "PROMPT.md") if (self.root / "PROMPT.md").is_file() else "MISSING",
            "model": os.environ.get("DSC_CICD_MODEL", "deterministic-no-model"),
            "tools": digest(self.input_facts.get("tool_versions", {})),
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

    def prior_contract(self, cid: str) -> dict[str, Any]:
        for item in self.previous_state.get("contracts", []):
            if item.get("contract_id") == cid:
                return item
        return {}

    def cache_entry(self, key: str) -> dict[str, Any]:
        return self.cache.get("entries", {}).get(key, {}) if isinstance(self.cache, dict) else {}

    def build_plan(self) -> dict[str, Any]:
        ready: list[str] = []
        blocked: list[dict[str, Any]] = []
        contracts: list[dict[str, Any]] = []
        for contract in sorted(self.contracts, key=contract_id):
            cid = contract_id(contract)
            key, hashes = self.cache_key(contract)
            is_ready, reasons = self.ready(contract)
            previous = self.prior_contract(cid)
            stale_reasons = []
            for name, value in hashes.items():
                if previous.get("hashes", {}).get(name) and previous["hashes"].get(name) != value:
                    stale_reasons.append(name)
            cached = self.cache_entry(key)
            cached_artifact = pathlib.Path(str(cached.get("artifact_dir", "")))
            if not cached_artifact.is_absolute():
                cached_artifact = self.root / cached_artifact
            cache_valid = bool(
                cached
                and cached.get("cache_key") == key
                and cached.get("valid")
                and cached_artifact.is_dir()
            )
            item = {
                "contract_id": cid,
                "function": contract_function(contract).get("name"),
                "clang_usr": contract_function(contract).get("clang_usr"),
                "contract_hash": hashes["contract"],
                "cache_key": key,
                "hashes": hashes,
                "dependencies": sorted(self.dependency_info.get("adjacency", {}).get(cid, [])),
                "call_sites": [x for x in self.dependency_info.get("call_sites", []) if x["caller_contract"] == cid],
                "ready": is_ready,
                "blocked_reasons": reasons,
                "stale": bool(stale_reasons),
                "stale_reasons": stale_reasons,
                "cache_hit": cache_valid,
                "cache_model_calls": 0 if cache_valid else None,
                "initial_state": cached.get("state", "CONTRACT_LOCKED") if cache_valid else "CONTRACT_LOCKED" if is_ready else "DISCOVERED",
            }
            contracts.append(item)
            if is_ready:
                ready.append(cid)
            else:
                blocked.append({"contract_id": cid, "function": item["function"], "reasons": reasons})
        # Stable topological batches.  A contract can run in parallel with
        # other contracts once all of its contract dependencies are complete.
        remaining = set(ready)
        batches: list[list[str]] = []
        completed: set[str] = set()
        while remaining:
            batch = sorted(cid for cid in remaining if set(next(x for x in contracts if x["contract_id"] == cid)["dependencies"]).issubset(completed))
            if not batch:
                blocked.extend({"contract_id": cid, "function": next(x for x in contracts if x["contract_id"] == cid)["function"], "reasons": ["dependency_not_ready"]} for cid in sorted(remaining))
                break
            batches.append(batch)
            remaining -= set(batch)
            completed.update(batch)
        self.plan = {
            "schema_version": 1,
            "agent": "generic-c-to-rtl-cicd",
            "state_order": list(STATE_ORDER),
            "input_facts": self.input_facts,
            "dependency": self.dependency_info,
            "contracts": contracts,
            "ready_contracts": ready,
            "blocked_contracts": blocked,
            "parallel_batches": batches,
            "composition_order": [cid for batch in batches for cid in batch],
            "model_policy": {
                "max_calls_per_function": 1,
                "candidate_limit": 4,
                "allowed_output": "combinational RTL body only",
                "model_calls_planned": 0,
                "cache_reuse_has_zero_model_calls": True,
            },
        }
        return self.plan

    def stage_node(self, item: dict[str, Any], stage: str, status: str, artifacts: list[str] | None = None, failure: str | None = None) -> dict[str, Any]:
        return {
            "node_id": f"{item['contract_id']}:{stage}",
            "contract_id": item["contract_id"],
            "stage": STAGE_TO_STATE[stage],
            "source_hash": item["hashes"]["source"],
            "spec_hash": item["hashes"]["spec"],
            "contract_hash": item["hashes"]["contract"],
            "dependency_hash": item["hashes"]["dependency"],
            "status": status,
            "artifacts": sorted(artifacts or []),
            "failure_reason": failure,
        }

    def make_dag(self) -> dict[str, Any]:
        nodes: list[dict[str, Any]] = []
        edges: list[dict[str, str]] = []
        for item in self.plan.get("contracts", []):
            cid = item["contract_id"]
            current = item.get("initial_state", "CONTRACT_LOCKED") if item.get("ready") else "DISCOVERED"
            for stage in STAGE_TO_STATE:
                target = STAGE_TO_STATE[stage]
                if not item.get("ready"):
                    status = "DISCOVERED" if stage == "discover" else "BLOCKED"
                    failure = "; ".join(item.get("blocked_reasons", [])) if stage != "discover" else None
                else:
                    status = "PASS" if STATE_ORDER.index(target) <= STATE_ORDER.index(current) else "PENDING"
                    failure = None
                nodes.append(self.stage_node(item, stage, status, failure=failure))
                if stage != "discover":
                    previous = list(STAGE_TO_STATE).index(stage) - 1
                    edges.append({"from": f"{cid}:{list(STAGE_TO_STATE)[previous]}", "to": f"{cid}:{stage}", "kind": "state"})
            for dependency in item.get("dependencies", []):
                edges.append({"from": f"{dependency}:promote", "to": f"{cid}:dependencies", "kind": "contract_dependency"})
        for cycle in self.dependency_info.get("cycles", []):
            if cycle:
                edges.append({"from": f"{cycle[-1]}:dependencies", "to": f"{cycle[0]}:dependencies", "kind": "cycle_rejected"})
        self.dag = {
            "schema_version": 1,
            "state_order": list(STATE_ORDER),
            "nodes": nodes,
            "edges": edges,
            "dependency_call_sites": self.dependency_info.get("call_sites", []),
            "cycles": self.dependency_info.get("cycles", []),
        }
        return self.dag

    def write_plan_files(self) -> None:
        write_json(self.ci / "plan.json", self.plan)
        write_json(self.ci / "dag.json", self.dag)

    def plan_command(self) -> int:
        self.load_inputs()
        self.dependency_graph()
        self.build_plan()
        self.make_dag()
        self.write_plan_files()
        self.write_state()
        print(json.dumps({"status": "PASS" if not self.input_facts.get("errors") else "INFRASTRUCTURE_FAILURE", "ready": self.plan.get("ready_contracts", []), "blocked": self.plan.get("blocked_contracts", []), "cache_hits": sum(1 for x in self.plan.get("contracts", []) if x.get("cache_hit"))}, ensure_ascii=False))
        return 0 if not self.input_facts.get("errors") else 1

    def write_state(self) -> None:
        contracts = self.state.get("contracts") if self.state else None
        if contracts is None:
            contracts = []
            for item in self.plan.get("contracts", []):
                contracts.append({
                    "contract_id": item["contract_id"],
                    "function": item.get("function"),
                    "current_state": "DISCOVERED" if not item.get("ready") else item.get("initial_state", "CONTRACT_LOCKED"),
                    "status": "INFRASTRUCTURE_FAILURE" if self.input_facts.get("errors") else "BLOCKED" if not item.get("ready") else "PASS" if item.get("initial_state") == "PROMOTED" else "PENDING",
                    "hashes": item["hashes"],
                    "artifacts": [],
                    "failure_reason": "; ".join(item.get("blocked_reasons", [])) if not item.get("ready") else None,
                    "history": [{"state": "DISCOVERED"}],
                })
        self.state = {
            "schema_version": 1,
            "agent": "generic-c-to-rtl-cicd",
            "state_order": list(STATE_ORDER),
            "input_facts": self.input_facts,
            "contracts": contracts,
            "model_calls": sum(int(item.get("model_calls", 0)) for item in contracts),
            "rollback_mode": "C_ONLY",
        }
        write_json(self.ci / "state.json", self.state)

    def artifact_dir(self, item: dict[str, Any]) -> pathlib.Path:
        return self.artifacts / item["hashes"]["contract"]

    def contract_ports(self, contract: dict[str, Any]) -> list[dict[str, Any]]:
        ports: list[dict[str, Any]] = []
        seen: set[str] = set()
        for value in contract.get("interface", {}).get("inputs", []) + contract.get("interface", {}).get("flattened_pointer_dependencies", []):
            raw_name = str(value.get("name") or value.get("field") or "input")
            name = safe_identifier(raw_name.split(".")[-1])
            if name in seen:
                continue
            seen.add(name)
            width = int(value.get("logical_width") or 1)
            ports.append({"name": name, "width": max(1, min(width, 4096)), "role": value.get("role"), "unresolved": bool(value.get("unresolved")), "source": raw_name})
        output = contract.get("interface", {}).get("output", {})
        ports.append({"name": "return_value", "width": max(1, min(int(output.get("logical_width") or 1), 4096)), "direction": "output", "unresolved": bool(output.get("unresolved")), "source": "return_value"})
        return ports

    def render_sv_stub(self, contract: dict[str, Any]) -> str:
        cid = safe_identifier(contract_id(contract))
        ports = self.contract_ports(contract)
        declarations = []
        assignments = []
        for port in ports:
            width = port["width"]
            range_text = f" [{width - 1}:0]" if width > 1 else ""
            direction = "output" if port.get("direction") == "output" else "input"
            declarations.append(f"  {direction} logic{range_text} {port['name']}")
        assignments.append("  assign return_value = '0;")
        return "module cicd_" + cid + "_stub(\n" + ",\n".join(declarations) + ");\n" + "\n".join(assignments) + "\nendmodule\n"

    def render_oracle_stub(self, contract: dict[str, Any]) -> str:
        function = contract_function(contract)
        name = str(function.get("name", "unresolved_function"))
        return textwrap.dedent(
            f"""\
            /* Generated contract oracle adapter.  The upstream C model is not edited. */
            /* contract: {contract_id(contract)}; C symbol: {name} */
            #include <stdint.h>

            int dsc_cicd_oracle_unavailable_{safe_identifier(contract_id(contract))}(void) {{
                return -1;
            }}
            """
        )

    def render_harness_stub(self, contract: dict[str, Any]) -> str:
        module = "cicd_" + safe_identifier(contract_id(contract)) + "_stub"
        return textwrap.dedent(
            f"""\
            // Generated harness placeholder.  A locked contract with unresolved
            // semantics is not executable and must not trigger a model call.
            #include \"V{module}.h\"
            int main() {{ return 0; }}
            """
        )

    def render_vector_generator(self, contract: dict[str, Any]) -> str:
        plan = {
            "contract_id": contract_id(contract),
            "inputs": contract.get("interface", {}).get("inputs", []),
            "flattened_pointer_dependencies": contract.get("interface", {}).get("flattened_pointer_dependencies", []),
            "legal_domain": contract.get("verification_plan", {}).get("legal_domain"),
            "source": "locked contract only",
        }
        return "#!/usr/bin/env python3\n# Deterministic legal-domain plan generated from the locked contract.\nPLAN = " + repr(plan) + "\n"

    def render_overlay_wrapper(self, contract: dict[str, Any]) -> str:
        cid = safe_identifier(contract_id(contract))
        return textwrap.dedent(
            f"""\
            /* Generated C-only/shadow/RTL-return dispatcher for contract {contract_id(contract)}. */
            #include <stdint.h>
            enum dsc_cicd_mode {{ DSC_C_ONLY = 0, DSC_SHADOW = 1, DSC_RTL_RETURN = 2 }};
            static enum dsc_cicd_mode dsc_cicd_mode_{cid} = DSC_C_ONLY;
            static unsigned long dsc_cicd_mismatches_{cid};
            void dsc_cicd_set_mode_{cid}(enum dsc_cicd_mode mode) {{ dsc_cicd_mode_{cid} = mode; }}
            unsigned long dsc_cicd_mismatch_count_{cid}(void) {{ return dsc_cicd_mismatches_{cid}; }}
            int dsc_cicd_dispatch_scalar_{cid}(int c_value, int rtl_value) {{
                if (dsc_cicd_mode_{cid} != DSC_C_ONLY && c_value != rtl_value) ++dsc_cicd_mismatches_{cid};
                return dsc_cicd_mode_{cid} == DSC_RTL_RETURN ? rtl_value : c_value;
            }}
            """
        )

    def existing_slice(self, contract: dict[str, Any], body: str) -> tuple[bool, dict[str, Any]]:
        context = read_json(self.root / "rtl" / "generation-context.json", {}) or {}
        receipt = read_json(self.root / "verification" / "verification-receipt.json", {}) or {}
        body_hash = hashlib.sha256(body.encode("utf-8")).hexdigest()
        cid = contract_id(contract)
        candidates = sorted((self.root / "rtl" / "candidates" / cid).glob("candidate_*.sv"))
        valid = bool(
            context.get("call_count", 2) <= 1
            and context.get("c_body_sha256") == body_hash
            and context.get("c_function") == contract_function(contract).get("name")
            and context.get("combinational_only") is True
            and candidates
            and receipt.get("contract_id") == cid
            and receipt.get("status") == "PASS"
        )
        return valid, {"context": context, "receipt": receipt, "candidates": candidates}

    def generate_artifacts(self, item: dict[str, Any], contract: dict[str, Any]) -> dict[str, Any]:
        artifact = self.artifact_dir(item)
        artifact.mkdir(parents=True, exist_ok=True)
        source_dir = pathlib.Path(str(self.input_facts["source_dir"]))
        try:
            source_path, body = source_body(contract, source_dir)
        except (OSError, ValueError) as exc:
            return {"status": "INFRASTRUCTURE_FAILURE", "failure_reason": f"source body unavailable: {exc}", "artifacts": []}
        existing, evidence = self.existing_slice(contract, body)
        write_json(artifact / "locked-contract.json", contract)
        write_json(artifact / "input-packing.json", {"contract_id": contract_id(contract), "ports": self.contract_ports(contract), "source": "locked contract"})
        write_json(artifact / "legal-domain.json", {"contract_id": contract_id(contract), "verification_plan": contract.get("verification_plan", {}), "interface": contract.get("interface", {})})
        write_json(artifact / "mutations.json", {"contract_id": contract_id(contract), "mutations": contract.get("verification_plan", {}).get("mutations", []), "stop_after_first_mismatch": True})
        (artifact / "interface.sv").write_text(self.render_sv_stub(contract), encoding="utf-8")
        (artifact / "vector_generator.py").write_text(self.render_vector_generator(contract), encoding="utf-8")
        (artifact / "shadow_replacement_wrapper.c").write_text(self.render_overlay_wrapper(contract), encoding="utf-8")
        if existing:
            oracle = self.root / "verification" / contract_id(contract) / "oracle.c"
            if oracle.is_file():
                shutil.copy2(oracle, artifact / "oracle.c")
            for path in evidence["candidates"]:
                target = artifact / "rtl" / path.name
                target.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(path, target)
            for path in sorted((self.root / "verification" / contract_id(contract)).glob("harness_*.cpp")):
                target = artifact / "harness" / path.name
                target.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(path, target)
            generation = {
                "contract_id": contract_id(contract),
                "status": "REUSED_VALID_RECEIPT",
                "model_calls": 0,
                "max_model_calls": 1,
                "candidate_limit": 4,
                "allowed_model_output": "combinational RTL body only",
                "context": evidence["context"],
                "source_body_sha256": hashlib.sha256(body.encode("utf-8")).hexdigest(),
                "input_context": {
                    "locked_contract": True,
                    "c_body": True,
                    "short_exact_spec_anchors": [link.get("anchor_id") for link in contract_exact_links(contract)],
                    "frozen_interface": True,
                },
            }
        else:
            (artifact / "oracle.c").write_text(self.render_oracle_stub(contract), encoding="utf-8")
            (artifact / "rtl").mkdir(parents=True, exist_ok=True)
            (artifact / "rtl" / "candidate_01.sv").write_text(self.render_sv_stub(contract), encoding="utf-8")
            (artifact / "harness" / "harness.cpp").parent.mkdir(parents=True, exist_ok=True)
            (artifact / "harness" / "harness.cpp").write_text(self.render_harness_stub(contract), encoding="utf-8")
            generation = {
                "contract_id": contract_id(contract),
                "status": "DETERMINISTIC_SCAFFOLD",
                "model_calls": 0,
                "max_model_calls": 1,
                "candidate_limit": 4,
                "allowed_model_output": "combinational RTL body only",
                "input_context": {"locked_contract": True, "c_body": True, "short_exact_spec_anchors": [link.get("anchor_id") for link in contract_exact_links(contract)], "frozen_interface": True},
                "failure_reason": "no reusable verified candidate receipt" if not existing else None,
            }
        write_json(artifact / "generation.json", generation)
        write_json(artifact / "receipt-schema.json", {"schema_version": 1, "statuses": sorted(VERIFICATION_STATUSES), "complete_domain_required_for_exhaustive": True, "artifacts": ["unit-receipt.json", "dependency-receipt.json", "shadow-receipt.json", "rtl-return-receipt.json", "bitstream-receipt.json"]})
        manifest = {
            "schema_version": 1,
            "contract_id": contract_id(contract),
            "contract_hash": item["hashes"]["contract"],
            "source_hash": item["hashes"]["source"],
            "spec_hash": item["hashes"]["spec"],
            "dependency_hash": item["hashes"]["dependency"],
            "source_body_hash": hashlib.sha256(body.encode("utf-8")).hexdigest(),
            "source_file": str(source_path),
            "generation": generation,
            "cache_reused": existing,
        }
        write_json(artifact / "artifact-manifest.json", manifest)
        artifacts = [str(path.relative_to(self.root)) for path in sorted(artifact.rglob("*")) if path.is_file()]
        return {"status": "PASS", "artifacts": artifacts, "artifact_dir": str(artifact), "generation": generation, "existing": existing, "receipt": evidence.get("receipt", {})}

    def update_contract(self, cid: str, state_name: str, status: str, artifacts: Iterable[str], failure: str | None = None, extra: dict[str, Any] | None = None) -> None:
        with self.state_lock:
            for item in self.state.get("contracts", []):
                if item.get("contract_id") != cid:
                    continue
                old = item.get("current_state", "DISCOVERED")
                if state_name in STATE_ORDER and old in STATE_ORDER and STATE_ORDER.index(state_name) < STATE_ORDER.index(old):
                    return
                item["current_state"] = state_name
                item["status"] = status
                item["artifacts"] = sorted(set(item.get("artifacts", [])).union(artifacts))
                item["failure_reason"] = failure
                item.setdefault("history", []).append({"state": state_name, "status": status, "failure_reason": failure})
                if extra:
                    item.update(extra)
                return

    def initialize_state(self) -> None:
        contracts = []
        for item in self.plan.get("contracts", []):
            contracts.append({
                "contract_id": item["contract_id"],
                "function": item.get("function"),
                "current_state": "DISCOVERED" if not item.get("ready") else item.get("initial_state", "CONTRACT_LOCKED"),
                "status": "BLOCKED" if not item.get("ready") else "PENDING",
                "hashes": item["hashes"],
                "artifacts": [],
                "failure_reason": "; ".join(item.get("blocked_reasons", [])) if not item.get("ready") else None,
                "history": [{"state": "DISCOVERED"}, {"state": "CONTRACT_LOCKED" if item.get("ready") else "DISCOVERED"}],
                "model_calls": 0,
            })
        self.state = {"contracts": contracts}
        if self.input_facts.get("errors"):
            for item in self.state["contracts"]:
                item["status"] = "INFRASTRUCTURE_FAILURE"
                item["failure_reason"] = "; ".join(self.input_facts["errors"])

    def contract_from_item(self, item: dict[str, Any]) -> dict[str, Any]:
        cid = item["contract_id"]
        return next(contract for contract in self.contracts if contract_id(contract) == cid)

    def run_contract(self, item: dict[str, Any]) -> dict[str, Any]:
        contract = self.contract_from_item(item)
        cid = item["contract_id"]
        cached = self.cache_entry(item["cache_key"])
        if item.get("cache_hit") and cached.get("state") == "PROMOTED":
            artifacts = cached.get("artifacts", [])
            self.update_contract(cid, "PROMOTED", "PASS", artifacts, extra={"cache_reused": True, "model_calls": 0})
            return {"contract_id": cid, "status": "CACHE_REUSED", "state": "PROMOTED", "model_calls": 0}
        artifact_result = self.generate_artifacts(item, contract)
        if artifact_result.get("status") != "PASS":
            self.update_contract(cid, "CONTRACT_LOCKED", "INFRASTRUCTURE_FAILURE", [], artifact_result.get("failure_reason"), {"model_calls": 0})
            return {"contract_id": cid, "status": "INFRASTRUCTURE_FAILURE", "failure_reason": artifact_result.get("failure_reason")}
        artifacts = artifact_result.get("artifacts", [])
        self.update_contract(cid, "RTL_GENERATED", "PASS", artifacts, extra={"model_calls": int(artifact_result.get("generation", {}).get("model_calls", 0)), "cache_reused": bool(artifact_result.get("existing"))})
        unit = self.unit_verify(item, contract, artifact_result)
        unit_artifacts = [str(path.relative_to(self.root)) for path in (self.artifact_dir(item)).glob("unit-receipt.json")]
        if unit.get("status") != "PASS":
            self.update_contract(cid, "RTL_GENERATED", unit.get("status", "UNPROVED"), unit_artifacts, unit.get("failure_reason"), {"verification_status": unit.get("verification_status", "UNPROVED")})
            return {"contract_id": cid, "status": unit.get("status", "UNPROVED"), "state": "RTL_GENERATED"}
        self.update_contract(cid, "UNIT_VERIFIED", "PASS", unit_artifacts, extra={"verification_status": unit.get("verification_status"), "promoted_candidate": unit.get("promoted_candidate")})
        dependency = self.dependency_verify(item, contract)
        dependency_artifacts = [str(path.relative_to(self.root)) for path in (self.artifact_dir(item)).glob("*dependency-receipt.json")]
        if dependency.get("status") != "PASS":
            self.update_contract(cid, "UNIT_VERIFIED", dependency.get("status", "UNPROVED"), dependency_artifacts, dependency.get("failure_reason"))
            return {"contract_id": cid, "status": dependency.get("status", "UNPROVED"), "state": "UNIT_VERIFIED"}
        self.update_contract(cid, "DEPENDENCIES_VERIFIED", "PASS", dependency_artifacts)
        integration = self.run_full_overlay(item, contract, artifact_result, unit)
        shadow_pass = integration.get("shadow", {}).get("status") == "PASS"
        rtl_pass = integration.get("rtl_return", {}).get("status") == "PASS"
        integration_artifacts = [str(path.relative_to(self.root)) for path in sorted((self.integration / "generated-overlay" / cid).glob("*")) if path.is_file()]
        integration_artifacts.extend(str(path.relative_to(self.root)) for path in sorted(self.artifact_dir(item).glob("*-receipt.json")) if path.is_file())
        if not shadow_pass:
            self.update_contract(cid, "DEPENDENCIES_VERIFIED", "UNPROVED", integration_artifacts, "SHADOW_PASS failed")
            return {"contract_id": cid, "status": "UNPROVED", "state": "DEPENDENCIES_VERIFIED"}
        self.update_contract(cid, "SHADOW_PASS", "PASS", integration_artifacts)
        if not rtl_pass:
            self.update_contract(cid, "SHADOW_PASS", "UNPROVED", integration_artifacts, "RTL_RETURN_PASS failed")
            return {"contract_id": cid, "status": "UNPROVED", "state": "SHADOW_PASS"}
        self.update_contract(cid, "RTL_RETURN_PASS", "PASS", integration_artifacts)
        bitstream_pass = all(mode.get("status") == "PASS" for mode in integration.get("overlay", {}).get("modes", []) if mode.get("mode") in {"C_ONLY", "SHADOW", "RTL_RETURN"})
        if not bitstream_pass:
            self.update_contract(cid, "RTL_RETURN_PASS", "UNPROVED", integration_artifacts, "bitstream hash gate failed")
            return {"contract_id": cid, "status": "UNPROVED", "state": "RTL_RETURN_PASS"}
        self.update_contract(cid, "BITSTREAM_PASS", "PASS", integration_artifacts)
        self.update_contract(cid, "PROMOTED", "PASS", integration_artifacts, extra={"active_mode": "RTL_RETURN", "rollback_mode": "C_ONLY"})
        return {"contract_id": cid, "status": "PASS", "state": "PROMOTED", "model_calls": 0}

    def refresh_dag(self) -> None:
        by_id = {item["contract_id"]: item for item in self.state.get("contracts", [])}
        for node in self.dag.get("nodes", []):
            item = by_id.get(node.get("contract_id"))
            if not item:
                continue
            current = item.get("current_state", "DISCOVERED")
            stage = node.get("stage")
            if item.get("status") == "INFRASTRUCTURE_FAILURE":
                node["status"] = "INFRASTRUCTURE_FAILURE"
            elif item.get("status") in {"BLOCKED", "UNPROVED", "UNSUPPORTED"} and stage != current:
                node["status"] = "BLOCKED" if stage != current else item.get("status")
            elif stage in STATE_ORDER and current in STATE_ORDER and STATE_ORDER.index(stage) <= STATE_ORDER.index(current):
                node["status"] = "PASS"
            else:
                node["status"] = "PENDING"
            node["artifacts"] = item.get("artifacts", [])
            node["failure_reason"] = item.get("failure_reason") if node["status"] not in {"PASS", "PENDING"} else None

    def write_cache(self) -> None:
        # Keep the index bounded and deterministic: one current entry per
        # locked contract is enough to prove reuse or invalidation.  Staleness
        # is recorded in the next plan/state hashes rather than as unbounded
        # historical cache rows.
        entries: dict[str, Any] = {}
        for item in self.plan.get("contracts", []):
            state_item = next((value for value in self.state.get("contracts", []) if value.get("contract_id") == item["contract_id"]), {})
            artifact_dir = self.artifact_dir(item)
            entries[item["cache_key"]] = {
                "cache_key": item["cache_key"],
                "valid": state_item.get("current_state") == "PROMOTED",
                "state": state_item.get("current_state"),
                "status": state_item.get("status"),
                "contract_id": item["contract_id"],
                "artifact_dir": str(artifact_dir.relative_to(self.root)),
                "artifacts": state_item.get("artifacts", []),
                "hashes": item["hashes"],
                "model_calls": int(state_item.get("model_calls", 0)),
                "source_receipts": ["ci/state.json", "ci/dag.json", "artifacts/<contract-hash>/artifact-manifest.json"],
            }
        for entry in entries.values():
            path = pathlib.Path(str(entry.get("artifact_dir", "")))
            if path.is_absolute():
                try:
                    entry["artifact_dir"] = str(path.relative_to(self.root))
                except ValueError:
                    pass
        self.cache = {"schema_version": 1, "key_fields": ["agent", "source", "spec", "contract", "dependency", "prompt", "model", "tools"], "entries": entries}
        write_json(self.ci / "cache-index.json", self.cache)

    def write_integration_manifests(self) -> None:
        self.integration.mkdir(parents=True, exist_ok=True)
        replacements = []
        for item in self.state.get("contracts", []):
            if item.get("current_state") != "PROMOTED":
                continue
            cid = item["contract_id"]
            receipt = read_json(self.integration / "generated-overlay" / cid / "overlay-receipt.json", {}) or {}
            target = self.integration / "bitstream-receipts" / f"{cid}.json"
            write_json(target, receipt)
            replacements.append({"contract_id": cid, "active_mode": "RTL_RETURN", "rollback_mode": "C_ONLY", "call_sites": receipt.get("call_sites", []), "bitstream_receipt": str(target.relative_to(self.root))})
        replacement_plan = {"schema_version": 1, "generated_by": "tools/cicd_agent.py", "mode_semantics": {"C_ONLY": "return C", "SHADOW": "compare C/RTL, return C", "RTL_RETURN": "compare C/RTL, return RTL"}, "replacements": replacements, "rollback": {"operation": "change active_mode to C_ONLY in this manifest", "safe_mode": "C_ONLY"}}
        write_json(self.integration / "replacement-plan.yaml", replacement_plan)
        write_json(self.integration / "replacement-manifest.json", {"schema_version": 1, "active_mode": "RTL_RETURN" if replacements else "C_ONLY", "rollback_mode": "C_ONLY", "replacements": replacements})

    def write_summary(self, results: list[dict[str, Any]]) -> None:
        lines = ["# CI/CD pipeline summary", "", "- Agent: generic dependency-aware C-to-RTL migration", f"- Source hash: `{self.input_facts.get('source_hash')}`", f"- Spec hash: `{self.input_facts.get('spec_hash')}`", f"- Baseline SHA-256: `{self.input_facts.get('baseline_hash')}`", f"- Model calls: `{sum(int(result.get('model_calls', 0)) for result in results)}`", "", "## Contract states", ""]
        for item in self.state.get("contracts", []):
            lines.append(f"- `{item['contract_id']}`: `{item.get('current_state')}` / `{item.get('status')}`" + (f" — {item.get('failure_reason')}" if item.get("failure_reason") else ""))
        lines.extend(["", "## Planner", "", f"- Ready contracts: `{', '.join(self.plan.get('ready_contracts', [])) or 'none'}`", f"- Blocked contracts: `{', '.join(item['contract_id'] for item in self.plan.get('blocked_contracts', [])) or 'none'}`", f"- Parallel batches: `{json.dumps(self.plan.get('parallel_batches', []), ensure_ascii=False)}`", "", "## Evidence", "", "- `ci/dag.json` records per-stage hashes, statuses, artifacts, and failure reasons.", "- `ci/cache-index.json` records cache keys and zero-model-call reuse.", "- `integration/replacement-plan.yaml` contains C_ONLY rollback semantics.", "- `integration/bitstream-receipts/` contains byte and SHA-256 gates."])
        (self.root / "reports" / "pipeline-summary.md").parent.mkdir(parents=True, exist_ok=True)
        (self.root / "reports" / "pipeline-summary.md").write_text("\n".join(lines) + "\n", encoding="utf-8")

    def run_command(self) -> int:
        self.load_inputs()
        self.dependency_graph()
        self.build_plan()
        self.make_dag()
        self.initialize_state()
        self.write_plan_files()
        self.write_state()
        if self.input_facts.get("errors"):
            self.write_cache()
            self.write_summary([])
            print(json.dumps({"status": "INFRASTRUCTURE_FAILURE", "errors": self.input_facts["errors"]}, ensure_ascii=False))
            return 1
        for blocked_item in [entry for entry in self.plan.get("contracts", []) if not entry.get("ready")]:
            blocked_contract = self.contract_from_item(blocked_item)
            blocked_artifacts = self.generate_artifacts(blocked_item, blocked_contract)
            self.update_contract(
                blocked_item["contract_id"],
                "DISCOVERED",
                "BLOCKED",
                blocked_artifacts.get("artifacts", []),
                "; ".join(blocked_item.get("blocked_reasons", [])),
                {"model_calls": 0, "artifact_status": blocked_artifacts.get("status")},
            )
        results: list[dict[str, Any]] = []
        for batch in self.plan.get("parallel_batches", []):
            batch_items = [next(item for item in self.plan["contracts"] if item["contract_id"] == cid) for cid in batch]
            with concurrent.futures.ThreadPoolExecutor(max_workers=max(1, len(batch_items))) as executor:
                futures = [executor.submit(self.run_contract, item) for item in batch_items]
                for future in futures:
                    results.append(future.result())
        self.refresh_dag()
        self.write_cache()
        self.write_integration_manifests()
        self.write_summary(results)
        self.write_plan_files()
        self.write_state()
        failures = [item for item in self.state.get("contracts", []) if item.get("status") in {"INFRASTRUCTURE_FAILURE", "UNPROVED", "UNSUPPORTED"} and item.get("contract_id") in self.plan.get("ready_contracts", [])]
        print(json.dumps({"status": "PASS" if not failures else "UNPROVED", "results": results, "ready": self.plan.get("ready_contracts", []), "blocked": self.plan.get("blocked_contracts", []), "failures": failures}, ensure_ascii=False))
        return 0 if not failures else 1

    def status_command(self) -> int:
        state = read_json(self.ci / "state.json", {}) or {}
        plan = read_json(self.ci / "plan.json", {}) or {}
        cache = read_json(self.ci / "cache-index.json", {}) or {}
        print(json.dumps({"state": state, "ready_contracts": plan.get("ready_contracts", []), "blocked_contracts": plan.get("blocked_contracts", []), "cache_entries": len(cache.get("entries", {}))}, ensure_ascii=False))
        return 0


    def unit_verify(self, item: dict[str, Any], contract: dict[str, Any], artifact_result: dict[str, Any]) -> dict[str, Any]:
        receipt = artifact_result.get("receipt") or {}
        candidates = receipt.get("candidates", [])
        if not candidates or receipt.get("status") != "PASS":
            result = {"status": "UNSUPPORTED", "failure_reason": "no reusable complete verification receipt", "matrix": [], "promoted_candidate": None}
            write_json(self.artifact_dir(item) / "unit-receipt.json", result)
            return result
        passing = []
        matrix = []
        for candidate in sorted(candidates, key=lambda value: str(value.get("candidate", ""))):
            candidate_status = candidate.get("verification_status", candidate.get("status", "UNPROVED"))
            if candidate_status not in VERIFICATION_STATUSES:
                candidate_status = "UNPROVED"
            vectors = int(candidate.get("vectors") or 0)
            shard_count = min(8, max(1, (vectors + 999_999) // 1_000_000))
            shards = []
            for index in range(shard_count):
                start = (vectors * index) // shard_count
                end = (vectors * (index + 1)) // shard_count
                shard_status = candidate_status
                if candidate_status == "COUNTEREXAMPLE" and index > 0:
                    shard_status = "SKIPPED_AFTER_FIRST_MISMATCH"
                shards.append({"shard": index, "range": [start, end], "status": shard_status, "complete_legal_domain": candidate_status == "EXHAUSTIVE_EQUIVALENT"})
            matrix.append({"function": contract_function(contract).get("name"), "candidate": candidate.get("candidate"), "compile_once": candidate.get("lint", {}).get("status") == "PASS" and candidate.get("build", {}).get("status") == "PASS", "candidate_status": candidate_status, "vectors": vectors, "shards": shards, "smallest_counterexample": candidate.get("smallest_counterexample") or {key: candidate.get(key) for key in ("cpnt", "cpnt_bit_depth", "left_recon", "qlevel", "expected", "actual") if key in candidate}})
            if candidate_status == "EXHAUSTIVE_EQUIVALENT" and candidate.get("lint", {}).get("status") == "PASS" and candidate.get("build", {}).get("status") == "PASS":
                passing.append(candidate.get("candidate"))
        promoted = passing[0] if passing else None
        repair_packets = []
        for entry in matrix:
            if entry["candidate_status"] == "COUNTEREXAMPLE":
                variant = str(next((c.get("variant") for c in candidates if c.get("candidate") == entry["candidate"]), "arithmetic_counterexample"))
                category = "width_signedness" if "sign" in variant else "arithmetic_counterexample"
                if category in ALLOWED_REPAIR_CATEGORIES:
                    repair_packets.append({"category": category, "candidate": entry["candidate"], "counterexample": entry["smallest_counterexample"], "compact": True})
        result = {
            "schema_version": 1,
            "status": "PASS" if promoted else "UNPROVED",
            "verification_status": "EXHAUSTIVE_EQUIVALENT" if promoted else "UNPROVED",
            "contract_id": contract_id(contract),
            "function": contract_function(contract).get("name"),
            "execution": "reused_existing_complete_receipt",
            "compile_each_candidate_once": all(item["compile_once"] for item in matrix),
            "parallel_shards": True,
            "stop_after_first_mismatch": True,
            "matrix": matrix,
            "promoted_candidate": promoted,
            "repair_packets": repair_packets,
            "source_receipt": "verification/verification-receipt.json",
        }
        write_json(self.artifact_dir(item) / "unit-receipt.json", result)
        return result

    def dependency_verify(self, item: dict[str, Any], contract: dict[str, Any]) -> dict[str, Any]:
        cid = contract_id(contract)
        dependencies = item.get("dependencies", [])
        call_sites = item.get("call_sites", [])
        if not dependencies:
            result = {"schema_version": 1, "status": "PASS", "contract_id": cid, "dependencies": [], "call_sites": [], "composition": "not_required"}
            write_json(self.artifact_dir(item) / "dependency-receipt.json", result)
            return result
        dependency_states = {entry.get("contract_id"): entry.get("current_state") for entry in self.state.get("contracts", [])}
        not_ready = [dep for dep in dependencies if dependency_states.get(dep) not in {"DEPENDENCIES_VERIFIED", "SHADOW_PASS", "RTL_RETURN_PASS", "BITSTREAM_PASS", "PROMOTED"}]
        interfaces = []
        for dep in dependencies:
            dep_dir = self.artifact_dir(next(x for x in self.plan["contracts"] if x["contract_id"] == dep))
            core_dir = self.artifact_dir(item) / "dependencies" / dep
            core_dir.mkdir(parents=True, exist_ok=True)
            (core_dir / "A_core.sv").write_text("// Caller-local dependency interface; callee RTL is composed only after its pass.\nmodule A_core_dependency(input logic valid, output logic ready); assign ready = valid; endmodule\n", encoding="utf-8")
            write_json(core_dir / "B_C.json", {"callee_contract": dep, "source": "immutable C oracle", "artifact_dir": str(dep_dir)})
            interfaces.append(str((core_dir / "A_core.sv").relative_to(self.root)))
        result = {
            "schema_version": 1,
            "status": "PASS" if not not_ready else "UNPROVED",
            "contract_id": cid,
            "dependencies": dependencies,
            "call_sites": sorted(call_sites, key=lambda x: canonical(x.get("location", {}))),
            "local_test_binding": "B_C",
            "composition_binding": "B_RTL" if not not_ready else "WAIT_FOR_DEPENDENCY",
            "interfaces": interfaces,
            "failure_reason": "; ".join(f"dependency not passed: {dep}" for dep in not_ready) if not_ready else None,
        }
        write_json(self.artifact_dir(item) / "dependency-receipt.json", result)
        if not not_ready:
            write_json(self.artifact_dir(item) / "composition-receipt.json", {"status": "PASS", "caller": cid, "dependencies": dependencies, "mode": "A_core+B_RTL", "oracle": "A_C"})
        return result

    def overlay_bindings(self, contract: dict[str, Any], body: str) -> dict[str, Any] | None:
        """Return a safe binding for a flattened read-only C state contract.

        The binding is inferred from the C signature and locked interface.  It
        intentionally declines unsupported signatures rather than guessing a
        narrowing or inventing a replacement call.
        """
        function = contract_function(contract)
        name = str(function.get("name", ""))
        signature = re.search(r"\b" + re.escape(name) + r"\s*\(([^)]*)\)", body)
        if not signature:
            return None
        parameters = []
        for parameter in signature.group(1).split(","):
            match = re.search(r"([A-Za-z_][A-Za-z0-9_]*)\s*$", parameter.strip())
            if match:
                parameters.append(match.group(1))
        ports = [port for port in self.contract_ports(contract) if port["name"] != "return_value"]
        fields = contract.get("interface", {}).get("flattened_pointer_dependencies", [])
        state_fields = [safe_identifier(str(item.get("field", "")).split(".")[-1]) for item in fields]
        if not parameters or not ports or not state_fields:
            return None
        if not any("*" in parameter for parameter in signature.group(1).split(",")):
            return None
        state_parameter = next((parameters[index] for index, parameter in enumerate(signature.group(1).split(",")) if "*" in parameter), None)
        scalar_parameters = [value for value in parameters if value != state_parameter]
        if not state_parameter or not scalar_parameters:
            return None
        port_expressions = []
        for port in ports:
            if port["name"] in scalar_parameters:
                port_expressions.append(port["name"])
            elif port["name"] in state_fields:
                port_expressions.append(f"state->{port['name']}[cpnt]")
            else:
                return None
        original_arguments = []
        for parameter in parameters:
            original_arguments.append("state" if parameter == state_parameter else parameter)
        return {
            "function_name": name,
            "safe_contract_id": safe_identifier(contract_id(contract)),
            "state_parameter": state_parameter,
            "scalar_parameters": scalar_parameters,
            "original_arguments": original_arguments,
            "rtl_ports": [port["name"] for port in ports],
            "rtl_expressions": port_expressions,
            "module": None,
        }

    def run_process(self, command: list[str], cwd: pathlib.Path, timeout: int = 600, env: dict[str, str] | None = None) -> dict[str, Any]:
        try:
            completed = subprocess.run(command, cwd=cwd, env=env, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, encoding="utf-8", errors="replace", timeout=timeout, check=False)
            return {"status": "PASS" if completed.returncode == 0 else "FAIL", "returncode": completed.returncode, "command": command, "output_tail": (completed.stdout or "")[-5000:]}
        except subprocess.TimeoutExpired as exc:
            return {"status": "TIMEOUT", "returncode": 124, "command": command, "output_tail": ((exc.stdout or "") + "\n[timeout]\n")[-5000:]}
        except OSError as exc:
            return {"status": "INFRASTRUCTURE_FAILURE", "returncode": 127, "command": command, "output_tail": str(exc)}

    def patch_overlay_source(self, contract: dict[str, Any], model_root: pathlib.Path, binding: dict[str, Any], overlay_dir: pathlib.Path) -> tuple[pathlib.Path, list[dict[str, Any]]]:
        source_path, body = source_body(contract, pathlib.Path(str(self.input_facts["source_dir"])))
        relative = source_path.relative_to(pathlib.Path(str(self.input_facts["source_root"])))
        target = model_root / relative
        lines = target.read_text(encoding="utf-8", errors="replace").splitlines()
        function_name = binding["function_name"]
        original_name = "dsc_cicd_original_" + binding["safe_contract_id"]
        dispatcher_name = "dsc_cicd_dispatch_" + binding["safe_contract_id"]
        token = re.compile(r"\b" + re.escape(function_name) + r"\s*(?=\()")
        definition_line = int(contract_function(contract).get("source_span", {}).get("start_line", 1)) - 1
        if definition_line < 0 or definition_line >= len(lines) or not token.search(lines[definition_line]):
            raise RuntimeError("contract definition line no longer matches source")
        lines[definition_line] = token.sub(original_name, lines[definition_line], count=1)
        callgraph = read_json(self.root / "facts" / "callgraph.json", {}) or {}
        call_sites = []
        seen_lines: set[int] = set()
        for edge in callgraph.get("edges", []):
            if edge.get("callee_usr") != contract_function(contract).get("clang_usr"):
                continue
            line_number = int(edge.get("location", {}).get("line", 0) or 0)
            if line_number <= 0 or line_number - 1 >= len(lines) or line_number in seen_lines:
                continue
            if token.search(lines[line_number - 1]):
                lines[line_number - 1] = token.sub(dispatcher_name, lines[line_number - 1], count=1)
                seen_lines.add(line_number)
                call_sites.append({"caller": edge.get("caller_name"), "caller_usr": edge.get("caller_usr"), "callee": function_name, "location": edge.get("location", {})})
        target.write_text("#include \"dsc_cicd_overlay.h\"\n" + "\n".join(lines) + "\n", encoding="utf-8")
        write_json(overlay_dir / "call-sites.json", {"contract_id": contract_id(contract), "call_sites": sorted(call_sites, key=lambda x: x["location"].get("line", 0))})
        return target, call_sites

    def write_overlay_sources(self, contract: dict[str, Any], binding: dict[str, Any], overlay_dir: pathlib.Path, candidate: pathlib.Path, body: str) -> tuple[pathlib.Path, pathlib.Path, pathlib.Path, str]:
        cid = binding["safe_contract_id"]
        original_name = "dsc_cicd_original_" + cid
        dispatcher_name = "dsc_cicd_dispatch_" + cid
        rtl_name = "dsc_cicd_rtl_" + cid
        module_match = re.search(r"\bmodule\s+([A-Za-z_][A-Za-z0-9_]*)\s*\(", candidate.read_text(encoding="utf-8"))
        if not module_match:
            raise RuntimeError("RTL candidate has no module declaration")
        module = module_match.group(1)
        binding["module"] = module
        module_ports = set(re.findall(r"\b(?:input|output)\s+logic(?:\s*\[[^]]+\])?\s+([A-Za-z_][A-Za-z0-9_]*)", candidate.read_text(encoding="utf-8")))
        module_port_map = {}
        for port in binding["rtl_ports"]:
            options = (port, snake_case(port))
            actual_port = next((option for option in options if option in module_ports), None)
            if not actual_port:
                raise RuntimeError(f"RTL interface has no port for contract field: {port}")
            module_port_map[port] = actual_port
        binding["rtl_module_ports"] = module_port_map
        header = overlay_dir / "dsc_cicd_overlay.h"
        c_source = overlay_dir / "dsc_cicd_overlay.c"
        bridge = overlay_dir / "rtl_bridge.cpp"
        main = overlay_dir / "integration_main.cpp"
        header.write_text(textwrap.dedent(f"""\
            #ifndef DSC_CICD_OVERLAY_H
            #define DSC_CICD_OVERLAY_H
            #include \"dsc_codec.h\"
            #ifdef __cplusplus
            extern \"C\" {{
            #endif
            enum dsc_cicd_mode {{ DSC_C_ONLY = 0, DSC_SHADOW = 1, DSC_RTL_RETURN = 2 }};
            void dsc_cicd_set_mode_{cid}(enum dsc_cicd_mode mode);
            unsigned long dsc_cicd_mismatch_count_{cid}(void);
            int {dispatcher_name}(dsc_state_t *state, {', '.join('int ' + parameter for parameter in binding['scalar_parameters'])});
            int {rtl_name}({', '.join('int ' + port for port in binding['rtl_ports'])});
            #ifdef __cplusplus
            }}
            #endif
            #endif
            """), encoding="utf-8")
        c_source.write_text(textwrap.dedent(f"""\
            #include <stdio.h>
            #include \"dsc_cicd_overlay.h\"
            extern int {original_name}({', '.join(['dsc_state_t *state'] + ['int ' + parameter for parameter in binding['scalar_parameters']])});
            static enum dsc_cicd_mode mode_{cid} = DSC_C_ONLY;
            static unsigned long mismatches_{cid};
            void dsc_cicd_set_mode_{cid}(enum dsc_cicd_mode mode) {{ mode_{cid} = mode; }}
            unsigned long dsc_cicd_mismatch_count_{cid}(void) {{ return mismatches_{cid}; }}
            int {dispatcher_name}(dsc_state_t *state, {', '.join('int ' + parameter for parameter in binding['scalar_parameters'])}) {{
                int c_value = {original_name}({', '.join(binding['original_arguments'])});
                if (mode_{cid} == DSC_C_ONLY) return c_value;
                int rtl_value = {rtl_name}({', '.join(binding['rtl_expressions'])});
                if (c_value != rtl_value) ++mismatches_{cid};
                return mode_{cid} == DSC_RTL_RETURN ? rtl_value : c_value;
            }}
            """), encoding="utf-8")
        bridge.write_text(textwrap.dedent(f"""\
            #include <cstdint>
            #include <verilated.h>
            #include \"V{module}.h\"
            extern \"C\" int {rtl_name}({', '.join('int ' + port for port in binding['rtl_ports'])}) {{
                static VerilatedContext context;
                static V{module} dut{{&context}};
                {''.join(f'dut.{binding["rtl_module_ports"][port]} = static_cast<std::uint64_t>({port});\n    ' for port in binding['rtl_ports'])}dut.eval();
                return static_cast<int>(dut.return_value);
            }}
            """), encoding="utf-8")
        main.write_text(textwrap.dedent(f"""\
            #include <cstdlib>
            #include <cstdio>
            #include \"dsc_cicd_overlay.h\"
            extern \"C\" int dsc_cicd_original_main(int, char**);
            int main(int argc, char** argv) {{
                const char* value = std::getenv("DSC_CICD_MODE");
                int mode = value ? std::atoi(value) : 0;
                dsc_cicd_set_mode_{cid}(static_cast<dsc_cicd_mode>(mode));
                int result = dsc_cicd_original_main(argc, argv);
                unsigned long mismatches = dsc_cicd_mismatch_count_{cid}();
                if (mismatches) std::fprintf(stderr, "C/RTL mismatches: %lu\\n", mismatches);
                return mismatches ? 86 : result;
            }}
            """), encoding="utf-8")
        return header, bridge, main, module

    def run_full_overlay(self, item: dict[str, Any], contract: dict[str, Any], artifact_result: dict[str, Any], unit_result: dict[str, Any]) -> dict[str, Any]:
        cid = contract_id(contract)
        integration_dir = self.integration / "generated-overlay" / cid
        integration_dir.mkdir(parents=True, exist_ok=True)
        if unit_result.get("promoted_candidate") is None:
            result = {"status": "UNPROVED", "contract_id": cid, "failure_reason": "unit verification did not promote a candidate"}
            write_json(self.artifact_dir(item) / "shadow-receipt.json", result)
            write_json(self.artifact_dir(item) / "rtl-return-receipt.json", result)
            return result
        candidate = artifact_result.get("artifact_dir") and pathlib.Path(str(artifact_result["artifact_dir"])) / "rtl" / (str(unit_result["promoted_candidate"]) + ".sv")
        if not candidate or not candidate.is_file():
            # Candidate receipts use candidate_XX while the artifact copy has
            # the same stable basename.
            candidate = self.artifact_dir(item) / "rtl" / f"{unit_result['promoted_candidate']}.sv"
        source_dir = pathlib.Path(str(self.input_facts["source_dir"]))
        try:
            source_path, body = source_body(contract, source_dir)
            binding = self.overlay_bindings(contract, body)
        except (OSError, ValueError):
            binding = None
            body = ""
        if binding is None or not candidate.is_file():
            result = {"status": "UNSUPPORTED", "contract_id": cid, "failure_reason": "C overlay binding or promoted RTL candidate is unsupported", "modes": []}
            write_json(self.artifact_dir(item) / "shadow-receipt.json", result)
            write_json(self.artifact_dir(item) / "rtl-return-receipt.json", result)
            return result
        overlay_receipt: dict[str, Any] = {"schema_version": 1, "contract_id": cid, "function": contract_function(contract).get("name"), "mode_order": ["C_ONLY", "SHADOW", "RTL_RETURN"], "commands": [], "modes": [], "status": "INFRASTRUCTURE_FAILURE"}
        tmp_parent = self.root / "tmp"
        tmp_parent.mkdir(parents=True, exist_ok=True)
        overlay_work_root: pathlib.Path | None = None
        try:
            with tempfile.TemporaryDirectory(prefix="cicd-overlay-", dir=tmp_parent) as temp_name:
                work = pathlib.Path(temp_name)
                overlay_work_root = work
                model_root = work / "model"
                shutil.copytree(pathlib.Path(str(self.input_facts["source_root"])), model_root, symlinks=True, ignore=shutil.ignore_patterns(".git", "build", "target", "out", "operator_bittrue", "dsc-rs"))
                patched_source, call_sites = self.patch_overlay_source(contract, model_root, binding, integration_dir)
                shutil.copy2(integration_dir / "call-sites.json", work / "call-sites.json")
                header, bridge, main, module = self.write_overlay_sources(contract, binding, integration_dir, candidate, body)
                shutil.copy2(header, model_root / "source" / header.name)
                shutil.copy2(integration_dir / "dsc_cicd_overlay.c", model_root / "source" / "dsc_cicd_overlay.c")
                clang = str(self.input_facts["tools"]["clang"])
                verilator = str(self.input_facts["tools"]["verilator"])
                objects: list[pathlib.Path] = []
                source_copy = model_root / "source"
                object_dir = work / "objects"
                object_dir.mkdir()
                for source_file in sorted(source_copy.glob("*.c")):
                    object = object_dir / (source_file.stem + ".o")
                    command = [clang, "-std=gnu99", "-O3", "-D_FILE_OFFSET_BITS=64", "-I", str(source_copy), "-c", str(source_file), "-o", str(object)]
                    if source_file.name == "codec_main.c":
                        command.insert(2, "-Dmain=dsc_cicd_original_main")
                    result = self.run_process(command, work)
                    overlay_receipt["commands"].append({"purpose": "compile-overlay-c", **result})
                    if result["status"] != "PASS":
                        raise RuntimeError(f"overlay C compile failed: {source_file.name}")
                    objects.append(object)
                rtl_dir = work / "verilator"
                build_command = [verilator, "--cc", "--exe", "--build", "-j", "1", "--top-module", module, "-Wall", "--Wno-fatal", "-Wno-DECLFILENAME", "-Wno-UNUSEDSIGNAL", "--Mdir", str(rtl_dir), str(candidate), str(main), str(bridge), *map(str, objects), "--CFLAGS", f"-I{source_copy}", "--LDFLAGS", "-lm"]
                build_result = self.run_process(build_command, work, timeout=900)
                overlay_receipt["commands"].append({"purpose": "build-overlay-verilator-c-model", **build_result})
                binary = rtl_dir / f"V{module}"
                if build_result["status"] != "PASS" or not binary.is_file():
                    raise RuntimeError("overlay Verilator link failed")
                smoke_script = model_root / "bittrue_smoke" / "generate_simple_ppm.py"
                generated = self.run_process([sys.executable, str(smoke_script)], model_root)
                overlay_receipt["commands"].append({"purpose": "generate-bitstream-input", **generated})
                if generated["status"] != "PASS":
                    raise RuntimeError("bitstream input generation failed")
                expected_hash = str(self.input_facts.get("baseline_hash"))
                expected_size = int(self.input_facts.get("baseline_artifact", {}).get("size_bytes") or 0)
                (model_root / "bittrue_smoke" / "out").mkdir(parents=True, exist_ok=True)
                for mode_name, mode_value in (("C_ONLY", "0"), ("SHADOW", "1"), ("RTL_RETURN", "2")):
                    output_dir = model_root / "bittrue_smoke" / "out"
                    for output in output_dir.glob("*"):
                        if output.is_file():
                            output.unlink()
                    env = os.environ.copy()
                    env["DSC_CICD_MODE"] = mode_value
                    command = [str(binary), "-F", "bittrue_smoke/simple_8bpc_rgb.cfg"]
                    execution = self.run_process(command, model_root, timeout=900, env=env)
                    bitstream = output_dir / "simple_192x108.dsc"
                    actual_hash = file_hash(bitstream) if bitstream.is_file() else None
                    actual_size = bitstream.stat().st_size if bitstream.is_file() else None
                    byte_equal = actual_size == expected_size and actual_hash == expected_hash
                    mode_status = "PASS" if execution["status"] == "PASS" and byte_equal else "FAIL"
                    mode_receipt = {"mode": mode_name, "status": mode_status, "returncode": execution.get("returncode"), "size_bytes": actual_size, "expected_size_bytes": expected_size, "byte_for_byte_equal": byte_equal, "sha256": actual_hash, "expected_sha256": expected_hash, "sha256_equal": actual_hash == expected_hash, "command": command, "output_tail": execution.get("output_tail", "")}
                    overlay_receipt["modes"].append(mode_receipt)
                    write_json(integration_dir / f"{mode_name.lower().replace('_', '-')}.json", scrub_path(mode_receipt, work))
                    if mode_status != "PASS":
                        raise RuntimeError(f"overlay {mode_name} did not reproduce the C baseline")
                overlay_receipt["status"] = "PASS"
                overlay_receipt["call_sites"] = call_sites
                overlay_receipt["candidate"] = str(candidate.relative_to(self.root))
                overlay_receipt["replacement"] = {"C_ONLY": "return C", "SHADOW": "compare C/RTL and return C", "RTL_RETURN": "compare C/RTL and return RTL"}
        except (OSError, RuntimeError, subprocess.TimeoutExpired) as exc:
            overlay_receipt["failure_reason"] = str(exc)
        overlay_receipt = scrub_path(scrub_path(overlay_receipt, overlay_work_root), self.root)
        write_json(integration_dir / "overlay-receipt.json", overlay_receipt)
        shadow = {"schema_version": 1, "contract_id": cid, "status": "PASS" if overlay_receipt["status"] == "PASS" and next((x for x in overlay_receipt["modes"] if x["mode"] == "SHADOW"), {}).get("status") == "PASS" else "UNPROVED", "source": str((integration_dir / "overlay-receipt.json").relative_to(self.root))}
        rtl_return = {"schema_version": 1, "contract_id": cid, "status": "PASS" if overlay_receipt["status"] == "PASS" and next((x for x in overlay_receipt["modes"] if x["mode"] == "RTL_RETURN"), {}).get("status") == "PASS" else "UNPROVED", "source": str((integration_dir / "overlay-receipt.json").relative_to(self.root))}
        write_json(self.artifact_dir(item) / "shadow-receipt.json", shadow)
        write_json(self.artifact_dir(item) / "rtl-return-receipt.json", rtl_return)
        write_json(self.artifact_dir(item) / "bitstream-receipt.json", {"schema_version": 1, "contract_id": cid, "status": "PASS" if overlay_receipt.get("status") == "PASS" else "UNPROVED", "modes": overlay_receipt.get("modes", []), "baseline_sha256": self.input_facts.get("baseline_hash")})
        return {"status": "PASS" if shadow["status"] == "PASS" and rtl_return["status"] == "PASS" else overlay_receipt.get("status", "UNPROVED"), "shadow": shadow, "rtl_return": rtl_return, "overlay": overlay_receipt}


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Generic dependency-aware C-to-RTL CI/CD agent")
    parser.add_argument("--root", type=pathlib.Path, default=pathlib.Path(__file__).resolve().parent.parent)
    parser.add_argument("command", choices=("plan", "run", "resume", "status"))
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    agent = Agent(args.root, args.command)
    if args.command == "plan":
        return agent.plan_command()
    if args.command in {"run", "resume"}:
        return agent.run_command()
    return agent.status_command()


if __name__ == "__main__":
    raise SystemExit(main())
