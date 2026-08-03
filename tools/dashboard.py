#!/usr/bin/env python3
"""Build a readable regression and traceability site from durable receipts.

The receipt JSON remains authoritative. This module only reads repository
contracts/library files and the durable regression root, then emits compact
view models, Markdown reports, and a dependency-free static site. It never
selects a function by name and never copies RTL or source artifacts.
"""

from __future__ import annotations

import argparse
import dataclasses
import hashlib
import html
import http.server
import json
import os
import re
import socketserver
import sys
import urllib.parse
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[1]
EXPECTED_SHARE = "//kslin@192.168.68.52/homes"
DEFAULT_REGRESSION_ROOT = Path("/Volumes/homes/dsc12a-regression")
RUNS_DIR_NAME = "dsc12a-regression"
VALID_STATUSES = {
    "PASS",
    "FAIL",
    "RUNNING",
    "BLOCKED",
    "UNPROVED",
    "INFRASTRUCTURE_FAILURE",
}
STAGE_ORDER = (
    ("width_spec_gate", "width/spec gate"),
    ("generator_cache", "candidate generation/cache"),
    ("verilator_lint_build", "RTL lint/build"),
    ("formal", "formal proof"),
    ("formal_rtl_equivalence", "formal RTL equivalence"),
    ("unit_equivalence", "unit equivalence"),
    ("shards_mutations", "vectors and mutations"),
    ("dependency_composition", "dependency composition"),
    ("model_matrix", "C_ONLY / SHADOW / RTL_RETURN"),
    ("frame_compare", "frame/bitstream sanity"),
)
MATRIX_MODES = ("C_ONLY", "SHADOW", "RTL_RETURN")


def read_json(path: Path, default: Any = None) -> Any:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (FileNotFoundError, OSError, json.JSONDecodeError):
        return default


def write_json(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(value, indent=2, sort_keys=True, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )


def write_text(path: Path, value: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(value.rstrip() + "\n", encoding="utf-8")


def file_hash(path: Path) -> str | None:
    if not path.is_file():
        return None
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def safe_id(value: Any) -> str:
    result = re.sub(r"[^A-Za-z0-9_.-]+", "-", str(value)).strip("-.")
    return result or "item"


def first(value: Any, *keys: str, default: Any = None) -> Any:
    if not isinstance(value, dict):
        return default
    for key in keys:
        if key in value and value[key] is not None:
            return value[key]
    return default


def as_int(value: Any, default: int | None = None) -> int | None:
    try:
        if value is None or value == "":
            return default
        return int(value)
    except (TypeError, ValueError):
        return default


def ratio(value: Any) -> dict[str, Any]:
    if isinstance(value, dict):
        passed = as_int(first(value, "passed", "success", "ok"))
        total = as_int(first(value, "total", "count", "expected"))
    elif isinstance(value, str) and "/" in value:
        left, right = value.split("/", 1)
        passed, total = as_int(left), as_int(right)
    else:
        passed = as_int(value)
        total = passed if passed is not None else None
    display = f"{passed}/{total}" if passed is not None and total is not None else "—/—"
    return {"passed": passed, "total": total, "display": display}


def status(value: Any, *, not_applicable: str = "UNPROVED") -> str:
    text = str(value or "").upper()
    if text in VALID_STATUSES:
        return text
    if text in {"OK", "EXHAUSTIVE_EQUIVALENT", "FORMAL_EQUIVALENT", "COMPLETED"}:
        return "PASS"
    if text in {"NOT_APPLICABLE", "NOT_RUN", "UNKNOWN", "PENDING", "UNRESOLVED"}:
        return not_applicable
    if "INFRASTRUCTURE" in text or text in {"ERROR", "EXCEPTION"}:
        return "INFRASTRUCTURE_FAILURE"
    if "BLOCK" in text:
        return "BLOCKED"
    if "RUN" in text or "QUEUE" in text:
        return "RUNNING"
    if "COUNTEREXAMPLE" in text or "FAIL" in text or "MISMATCH" in text:
        return "FAIL"
    if "PROOF" in text and "PASS" not in text:
        return "UNPROVED"
    if "PASS" in text or "EQUIVALENT" in text:
        return "PASS"
    return not_applicable


def status_rank(value: str) -> int:
    return {
        "PASS": 4,
        "UNPROVED": 3,
        "RUNNING": 2,
        "BLOCKED": 1,
        "FAIL": 0,
        "INFRASTRUCTURE_FAILURE": 0,
    }.get(value, 0)


def compact_text(value: Any, limit: int = 320) -> str:
    if value is None:
        return ""
    if isinstance(value, (dict, list)):
        text = json.dumps(value, sort_keys=True, ensure_ascii=False)
    else:
        text = str(value)
    return text if len(text) <= limit else text[: limit - 1] + "…"


def file_uri(path: Path, fragment: str | None = None) -> str:
    uri = Path(path).expanduser().resolve().as_uri()
    return uri + (fragment or "")


@dataclasses.dataclass(frozen=True)
class StorageResolution:
    root: Path
    mode: str
    requested: str
    share: str | None
    mountpoint: str | None
    fallback_reason: str | None

    @property
    def fallback(self) -> bool:
        return self.mode.startswith("LOCAL_") or self.mode == "FALLBACK"

    def as_dict(self) -> dict[str, Any]:
        return {
            "root": str(self.root),
            "mode": self.mode,
            "requested": self.requested,
            "share": self.share,
            "mountpoint": self.mountpoint,
            "fallback": self.fallback,
            "fallback_reason": self.fallback_reason,
        }


def mount_candidates() -> list[tuple[str, Path]]:
    """Return matching SMB sources and mountpoints without requiring SMB."""
    try:
        output = os.popen("mount").read()
    except OSError:
        return []
    matches: list[tuple[str, Path]] = []
    for line in output.splitlines():
        if " on " not in line:
            continue
        source, rest = line.split(" on ", 1)
        mountpoint = rest.split(" (", 1)[0].strip()
        normalized = source.rstrip("/").lower()
        expected = EXPECTED_SHARE.rstrip("/").lower()
        if normalized == expected or (
            "192.168.68.52" in normalized and normalized.endswith("/homes")
        ):
            matches.append((source, Path(mountpoint)))
    return matches


def resolve_storage(repo: Path, explicit: str | None = None) -> StorageResolution:
    env_root = os.environ.get("DSC_REGRESSION_ROOT")
    requested = explicit or env_root or str(DEFAULT_REGRESSION_ROOT)
    if explicit:
        path = Path(explicit).expanduser()
        if path.is_dir():
            return StorageResolution(path, "EXPLICIT_ROOT", requested, None, None, None)
        local_runs = repo / "runs"
        if local_runs.is_dir():
            return StorageResolution(
                local_runs, "LOCAL_REPOSITORY", requested, None, None,
                f"requested root does not exist: {path}",
            )
        return StorageResolution(
            repo, "LOCAL_REPOSITORY", requested, None, None,
            f"requested root does not exist: {path}; using repository legacy receipts",
        )
    if env_root:
        path = Path(env_root).expanduser()
        if path.is_dir():
            return StorageResolution(path, "ENV_ROOT", requested, None, None, None)
        reason = f"DSC_REGRESSION_ROOT is unavailable: {path}"
    else:
        reason = None
    for share, mountpoint in mount_candidates():
        candidate = mountpoint / RUNS_DIR_NAME
        if candidate.is_dir():
            return StorageResolution(candidate, "SMB", requested, share, str(mountpoint), None)
    local_runs = repo / "runs"
    if local_runs.is_dir():
        return StorageResolution(
            local_runs, "LOCAL_REPOSITORY", requested, None, None,
            reason or f"SMB share {EXPECTED_SHARE} is unavailable",
        )
    return StorageResolution(
        repo, "LOCAL_REPOSITORY", requested, None, None,
        reason or f"SMB share {EXPECTED_SHARE} is unavailable; using repository legacy receipts",
    )


def run_timestamp(run: dict[str, Any], fallback: str) -> str:
    return str(first(run, "updated_at", "completed_at", "created_at", default=fallback))


def load_run_records(storage: Path) -> list[dict[str, Any]]:
    runs_dir = storage / "runs" if (storage / "runs").is_dir() else storage
    records: list[dict[str, Any]] = []
    if not runs_dir.is_dir():
        return records
    for path in sorted(runs_dir.iterdir()):
        if not path.is_dir() or path.name.startswith("."):
            continue
        run = read_json(path / "run.json", {}) or {}
        if not run and not (path / "functions").is_dir():
            continue
        run.setdefault("run_id", path.name)
        functions_dir = path / "functions"
        receipts: list[dict[str, Any]] = []
        if functions_dir.is_dir():
            for function_dir in sorted(functions_dir.iterdir()):
                if not function_dir.is_dir():
                    continue
                receipt = read_json(function_dir / "receipt.json", {}) or {}
                if receipt:
                    receipt.setdefault("contract_id", function_dir.name)
                    receipts.append(receipt)
        counts = Counter(status(item.get("status"), not_applicable="UNPROVED") for item in receipts)
        run_status = status(run.get("status"), not_applicable="RUNNING")
        if run.get("status") in {"COMPLETED", "FAILED"}:
            run_status = "PASS" if run.get("status") == "COMPLETED" else "FAIL"
        records.append({
            "path": path,
            "run": run,
            "receipts": receipts,
            "status": run_status,
            "counts": dict(sorted(counts.items())),
            "timestamp": run_timestamp(run, path.name),
        })
    records.sort(
        key=lambda item: (str(item["timestamp"]), str(item["run"].get("run_id"))),
        reverse=True,
    )
    return records


def resolve_run_id(records: list[dict[str, Any]], requested: str) -> str | None:
    if not records:
        return None
    if requested == "latest":
        return str(records[0]["run"].get("run_id"))
    return requested if any(
        str(item["run"].get("run_id")) == requested for item in records
    ) else None


def load_contracts(repo: Path) -> dict[str, dict[str, Any]]:
    result: dict[str, dict[str, Any]] = {}
    search_roots = (
        repo / "library" / "contracts",
        repo / "ci" / "discovered-contracts",
        repo / "ci" / "reviewed-contracts",
        repo / "contracts" / "locked",
    )
    for root in search_roots:
        if not root.is_dir():
            continue
        for path in sorted(root.glob("*.json")):
            value = read_json(path, {}) or {}
            cid = str(value.get("contract_id") or path.stem)
            if cid and cid not in result:
                value["_path"] = str(path)
                result[cid] = value
    return result


def load_library_manifest(repo: Path) -> dict[str, Any]:
    return read_json(repo / "library" / "manifest.json", {}) or {}


def spec_manifest(repo: Path) -> dict[str, Any]:
    return read_json(repo / "spec" / "manifest.json", {}) or {}


def contract_for(
    contracts: dict[str, dict[str, Any]], cid: str, receipt: dict[str, Any]
) -> dict[str, Any]:
    value = dict(contracts.get(cid, {}))
    trace = receipt.get("traceability") or {}
    if not value:
        value = {"contract_id": cid}
    value.setdefault("contract_id", cid)
    if "function" not in value:
        value["function"] = {"name": receipt.get("function", cid)}
    if "interface" not in value and trace.get("ports"):
        value["interface"] = {"ports": trace["ports"]}
    if "spec_links" not in value and trace.get("spec_links"):
        value["spec_links"] = trace["spec_links"]
    return value


def stage_counterexample(stage: Any) -> dict[str, Any] | None:
    if not isinstance(stage, dict):
        return None
    for key in ("counterexample", "smallest_counterexample"):
        value = stage.get(key)
        if isinstance(value, dict) and value:
            return value
    for key in ("candidates", "mutations", "counterexamples"):
        values = stage.get(key)
        if isinstance(values, list):
            for item in values:
                if isinstance(item, dict):
                    found = stage_counterexample(item)
                    if found:
                        return found
    evidence = stage.get("evidence")
    if isinstance(evidence, dict):
        return stage_counterexample(evidence)
    return None


def collect_counterexamples(receipt: dict[str, Any]) -> list[dict[str, Any]]:
    values: list[dict[str, Any]] = []
    stages = receipt.get("stages") or {}
    for stage_name in sorted(stages):
        stage = stages[stage_name]
        if not isinstance(stage, dict):
            continue
        candidates = stage.get("candidates") or []
        if isinstance(candidates, list):
            for candidate in candidates:
                if not isinstance(candidate, dict):
                    continue
                ce = candidate.get("smallest_counterexample")
                if isinstance(ce, dict) and ce:
                    values.append({"stage": stage_name, "candidate": candidate.get("candidate"), **ce})
        ce = stage_counterexample(stage)
        if ce:
            values.append({"stage": stage_name, **ce})
    unique: list[dict[str, Any]] = []
    seen: set[str] = set()
    for value in values:
        key = json.dumps(
            {
                "expected": value.get("expected"),
                "actual": value.get("actual"),
                "inputs": value.get("inputs"),
                "shard_id": value.get("shard_id"),
            },
            sort_keys=True,
            ensure_ascii=False,
        )
        if key not in seen:
            seen.add(key)
            unique.append(value)
    return unique


def stage_detail(stage: dict[str, Any]) -> dict[str, Any]:
    raw = str(stage.get("status") or stage.get("receipt_status") or "MISSING")
    normalized = status(raw)
    if raw == "NOT_APPLICABLE":
        normalized = "UNPROVED"
    blockers = stage.get("blockers") if isinstance(stage.get("blockers"), list) else []
    reason = first(stage, "reason", "error", "last_error", "message")
    if reason:
        blockers = [*blockers, str(reason)]
    return {
        "status": normalized,
        "raw_status": raw,
        "blockers": sorted({str(item) for item in blockers if item}),
        "counterexample": stage_counterexample(stage),
        "detail": compact_text(reason or raw),
        "required": raw != "NOT_APPLICABLE",
    }


def make_stage_checklist(
    receipt: dict[str, Any], plan: dict[str, Any]
) -> list[dict[str, Any]]:
    stages = receipt.get("stages") if isinstance(receipt.get("stages"), dict) else {}
    running = str(receipt.get("status", "")).upper() in {"RUNNING", "QUEUED", "PENDING"}
    seen: set[str] = set()
    result: list[dict[str, Any]] = []
    for stage_id, label in STAGE_ORDER:
        seen.add(stage_id)
        if stage_id in stages and isinstance(stages[stage_id], dict):
            value = stage_detail(stages[stage_id])
        elif stage_id == "unit_equivalence" and isinstance(stages.get("shards_mutations"), dict):
            value = stage_detail(stages["shards_mutations"])
            value["detail"] = "unit equivalence is recorded in the vectors/mutations receipt"
        else:
            value = {
                "status": "RUNNING" if running else "UNPROVED",
                "raw_status": "MISSING",
                "blockers": [],
                "counterexample": None,
                "detail": "receipt stage not present",
                "required": True,
            }
        result.append({"id": stage_id, "label": label, **value})
    for stage_id in sorted(set(stages) - seen):
        if not isinstance(stages[stage_id], dict):
            continue
        result.append({
            "id": stage_id,
            "label": stage_id.replace("_", " "),
            **stage_detail(stages[stage_id]),
        })
    return result


def find_stage(receipt: dict[str, Any], *names: str) -> dict[str, Any]:
    stages = receipt.get("stages") or {}
    for name in names:
        if isinstance(stages.get(name), dict):
            return stages[name]
    return {}


def normalize_ports(
    contract: dict[str, Any], trace: dict[str, Any]
) -> list[dict[str, Any]]:
    interface = contract.get("interface") if isinstance(contract.get("interface"), dict) else {}
    raw_ports = interface.get("ports") or trace.get("ports") or []
    if not isinstance(raw_ports, list):
        raw_ports = []
    records: list[dict[str, Any]] = []
    input_index = {
        str(item.get("name")): item
        for item in interface.get("inputs", [])
        if isinstance(item, dict) and item.get("name")
    }
    output = interface.get("output") if isinstance(interface.get("output"), dict) else {}
    for port in raw_ports:
        if not isinstance(port, dict):
            continue
        name = str(port.get("name") or port.get("port_name") or "unknown")
        source = input_index.get(name, output if name == output.get("name") else {})
        domain = first(
            port, "legal_domain", "domain",
            default=source.get("legal_domain", {}),
        )
        if not isinstance(domain, dict):
            domain = {"basis": str(domain)}
        width = as_int(
            first(port, "width", "logical_width", default=source.get("logical_width"))
        )
        width_source = first(
            port, "width_source", "derivation", default=source.get("width_source")
        )
        formula = first(
            port, "range_formula", "formula", "derivation",
            default=source.get("range_formula"),
        )
        if not formula:
            formula = domain.get("basis") or width_source or "not recorded"
        authority = first(
            port,
            "authority",
            default=(
                "EXACT_SPEC"
                if "EXACT" in str(width_source or "")
                or trace.get("review_status") == "REVIEWED"
                else "UNREVIEWED"
            ),
        )
        review = first(
            port,
            "review_status",
            default="REVIEWED" if trace.get("review_status") == "REVIEWED" else "UNREVIEWED",
        )
        signed = port.get("signed", source.get("signed"))
        if signed is None:
            signed = "signed" in str(
                port.get("c_type", source.get("c_type", ""))
            ).lower()
        records.append({
            "name": name,
            "direction": str(
                port.get("direction")
                or ("output" if name == output.get("name") else "input")
            ),
            "width": width,
            "signed": signed,
            "c_type": port.get("c_type", source.get("c_type")),
            "role": port.get("role", source.get("role")),
            "domain": {
                "kind": domain.get("kind"),
                "range": domain.get("range"),
                "values": domain.get("values", []),
                "basis": domain.get("basis"),
            },
            "width_derivation": {
                "formula": str(formula),
                "authority": str(authority),
                "review_status": str(review),
                "width_source": width_source,
            },
        })
    return records


def contract_function(
    contract: dict[str, Any], receipt: dict[str, Any]
) -> dict[str, Any]:
    value = contract.get("function") if isinstance(contract.get("function"), dict) else {}
    name = str(value.get("name") or receipt.get("function") or contract.get("contract_id"))
    span = value.get("source_span") if isinstance(value.get("source_span"), dict) else {}
    return {
        "name": name,
        "qualified_name": value.get("qualified_name", name),
        "source_file": value.get("source_file"),
        "source_file_sha256": value.get("source_file_sha256"),
        "source_body_sha256": value.get("source_body_sha256"),
        "source_span": {
            "start_line": as_int(span.get("start_line")),
            "end_line": as_int(span.get("end_line")),
        },
        "permalink": value.get("permalink"),
    }


def traceability_model(
    repo: Path, contract: dict[str, Any], receipt: dict[str, Any], cid: str
) -> dict[str, Any]:
    trace = receipt.get("traceability") if isinstance(receipt.get("traceability"), dict) else {}
    contract_function_value = contract_function(contract, receipt)
    source_root = first(
        trace, "source_root",
        default=(contract.get("provenance") or {}).get("source_root"),
    )
    source_file = first(
        trace, "source_file", default=contract_function_value.get("source_file")
    )
    source_path = None
    if source_file:
        candidate = Path(str(source_file)).expanduser()
        if not candidate.is_absolute() and source_root:
            candidate = Path(str(source_root)).expanduser() / candidate
        source_path = candidate
    span = trace.get("c_span") or contract_function_value.get("source_span") or {}
    start_line = as_int(span.get("start_line"), 1)
    end_line = as_int(span.get("end_line"), start_line)
    permalink = contract_function_value.get("permalink")
    code_href = str(permalink) if permalink else (
        file_uri(source_path, f"#L{start_line}") if source_path else None
    )
    code = {
        "file": source_file,
        "path": str(source_path) if source_path else None,
        "span": {"start_line": start_line, "end_line": end_line},
        "href": code_href,
        "fixed_commit": bool(
            permalink and re.search(r"/blob/[0-9a-f]{40}/", str(permalink))
        ),
        "available": bool(source_path and source_path.is_file()) or bool(permalink),
    }
    spec = spec_manifest(repo).get("spec", {})
    pdf_path_value = first(trace, "spec_pdf", default=spec.get("path"))
    pdf_path = Path(str(pdf_path_value)).expanduser() if pdf_path_value else None
    pdf_available = bool(pdf_path and pdf_path.is_file())
    raw_links = trace.get("spec_links") or contract.get("spec_links") or []
    if not isinstance(raw_links, list):
        raw_links = []
    spec_links: list[dict[str, Any]] = []
    for link in raw_links:
        if not isinstance(link, dict):
            continue
        page = as_int(link.get("page"))
        anchor_id = link.get("anchor_id")
        spec_links.append({
            "anchor_id": anchor_id,
            "page": page,
            "section": link.get("section"),
            "table": link.get("table") or (
                anchor_id if str(anchor_id or "").startswith("pdf:table:") else None
            ),
            "status": link.get("status", "UNREVIEWED"),
            "evidence": link.get("evidence"),
            "href": file_uri(pdf_path, f"#page={page}") if pdf_available and page else None,
        })
    spec_status = "AVAILABLE" if pdf_available else "SPEC_UNAVAILABLE"
    chain = [
        {"id": "spec", "label": "Spec", "status": "PASS" if pdf_available and spec_links else "UNPROVED", "href": spec_links[0].get("href") if spec_links else None},
        {"id": "c", "label": "C", "status": "PASS" if code["available"] else "UNPROVED", "href": code_href},
        {"id": "contract", "label": "Contract", "status": "PASS" if contract.get("contract_id") else "UNPROVED", "href": f"../../library/contracts/{safe_id(cid)}.json"},
        {"id": "rtl", "label": "RTL", "status": "UNPROVED", "href": None},
        {"id": "verification", "label": "Verification", "status": "UNPROVED", "href": None},
        {"id": "frame", "label": "Frame", "status": "UNPROVED", "href": "#frame-matrix"},
    ]
    return {
        "authority": trace.get("authority", "UNREVIEWED"),
        "review_status": trace.get("review_status", "UNREVIEWED"),
        "source": code,
        "spec": {
            "status": spec_status,
            "path": str(pdf_path) if pdf_path else None,
            "sha256": spec.get("sha256") or first(receipt.get("source_gate", {}).get("pdf", {}), "sha256"),
            "links": spec_links,
            "reason": None if pdf_available else "DSC PDF is not available at the recorded path",
        },
        "contract_hash": receipt.get("contract_hash") or contract.get("lock", {}).get("contract_sha256"),
        "ports": normalize_ports(contract, trace),
        "chain": chain,
    }


def candidate_model(receipt: dict[str, Any]) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    generation = find_stage(receipt, "generator_cache", "generator")
    verification = find_stage(receipt, "shards_mutations", "unit_equivalence")
    values: list[dict[str, Any]] = []
    for stage in (generation, verification):
        candidates = stage.get("candidates") if isinstance(stage, dict) else []
        if not isinstance(candidates, list):
            continue
        for item in candidates:
            if not isinstance(item, dict):
                continue
            candidate = str(item.get("candidate", "candidate"))
            values = [old for old in values if old.get("candidate") != candidate]
            values.append({
                "candidate": candidate,
                "accepted": bool(item.get("accepted")),
                "compile_status": status(item.get("compile_status"), not_applicable="UNPROVED"),
                "validation": status(item.get("validation"), not_applicable="UNPROVED"),
                "verification_status": item.get("verification_status"),
                "vectors_executed": as_int(item.get("vectors_executed"), 0),
                "smallest_counterexample": item.get("smallest_counterexample"),
            })
    passed = sum(1 for item in values if item.get("accepted"))
    candidate_ratio = ratio(receipt.get("candidate_pass_rate"))
    if candidate_ratio["total"] is None:
        candidate_ratio = {
            "passed": passed,
            "total": len(values),
            "display": f"{passed}/{len(values)}",
        }
    return values, candidate_ratio


def vector_model(receipt: dict[str, Any]) -> dict[str, Any]:
    stage = find_stage(receipt, "shards_mutations", "unit_equivalence")
    vectors = as_int(stage.get("vectors"), as_int(receipt.get("unit_vectors"), 0))
    shards = stage.get("shards") if isinstance(stage.get("shards"), list) else []
    verification_status = stage.get("verification_status")
    exhaustive = "EXHAUSTIVE" in str(verification_status or "").upper()
    formal = "FORMAL" in str(verification_status or "").upper()
    passed = len(shards) if status(stage.get("status")) == "PASS" else 0
    return {
        "executed": vectors or 0,
        "shards": {
            "passed": passed,
            "total": len(shards),
            "display": f"{passed}/{len(shards)}" if shards else "0/0",
        },
        "verification_status": verification_status,
        "exhaustive": exhaustive,
        "formal": formal,
        "status": status(stage.get("status"), not_applicable="UNPROVED"),
    }


def mutation_model(repo: Path, receipt: dict[str, Any]) -> dict[str, Any]:
    stage = find_stage(receipt, "shards_mutations")
    planned = None
    candidates: list[Path] = []
    artifact = receipt.get("source_artifact")
    if artifact:
        candidates.append(Path(str(artifact)) / "mutations.json")
    if receipt.get("contract_hash"):
        candidates.append(repo / "artifacts" / str(receipt["contract_hash"]) / "mutations.json")
    plan_value = next((read_json(path, None) for path in candidates if path.is_file()), None)
    if isinstance(plan_value, dict) and isinstance(plan_value.get("mutations"), list):
        planned = len(plan_value["mutations"])
    elif isinstance(plan_value, list):
        planned = len(plan_value)
    counterexamples = collect_counterexamples(receipt)
    evidence = stage.get("mutations") if isinstance(stage, dict) else None
    result = ratio(evidence) if evidence is not None else ratio(None)
    if result["total"] is None:
        result = {
            "passed": 0,
            "total": planned or 0,
            "display": f"0/{planned or 0}",
            "recorded": False,
            "basis": "planned mutation cases; per-case result receipt not recorded",
        }
    else:
        result["recorded"] = True
        result["basis"] = "mutation result receipt"
    return {
        "status": status(stage.get("status"), not_applicable="UNPROVED"),
        "planned": planned or 0,
        "result": result,
        "counterexamples": counterexamples,
        "smallest_counterexample": counterexamples[0] if counterexamples else None,
    }


def mode_result(value: Any) -> dict[str, Any]:
    if isinstance(value, str):
        normalized = status(value, not_applicable="UNPROVED")
        passed = 1 if normalized == "PASS" else 0
        return {
            "status": normalized,
            "raw_status": value,
            "passed": passed,
            "total": 1,
            "display": f"{passed}/1",
        }
    if isinstance(value, dict):
        raw = value.get("status") or value.get("execution_status")
        normalized = status(raw, not_applicable="UNPROVED")
        total = as_int(value.get("scenario_count"), 1) or 1
        passed = total if normalized == "PASS" else 0
        return {
            "status": normalized,
            "raw_status": raw,
            "passed": passed,
            "total": total,
            "display": f"{passed}/{total}",
        }
    return {
        "status": "UNPROVED",
        "raw_status": None,
        "passed": 0,
        "total": 0,
        "display": "0/0",
    }


def matrix_model(receipt: dict[str, Any]) -> dict[str, Any]:
    stage = find_stage(receipt, "model_matrix")
    authority = stage.get("authority_modes") if isinstance(stage.get("authority_modes"), dict) else {}
    scenarios = stage.get("scenario_modes") if isinstance(stage.get("scenario_modes"), dict) else {}
    modes: dict[str, Any] = {}
    for name in MATRIX_MODES:
        modes[name] = mode_result(authority.get(name, scenarios.get(name)))
    frame = find_stage(receipt, "frame_compare")
    frames = frame.get("frames") if isinstance(frame.get("frames"), list) else []
    frame_passed = sum(
        1 for item in frames
        if isinstance(item, dict) and status(item.get("status"), not_applicable="UNPROVED") == "PASS"
    )
    frame_total = len([item for item in frames if isinstance(item, dict)])
    top_ratio = ratio(receipt.get("frame_pass_rate"))
    if top_ratio["total"] is not None:
        frame_passed, frame_total = top_ratio["passed"], top_ratio["total"]
    modes["frame"] = {
        "status": status(frame.get("status"), not_applicable="UNPROVED"),
        "passed": frame_passed,
        "total": frame_total,
        "display": f"{frame_passed}/{frame_total}",
        "frames": frames,
    }
    return {
        "modes": modes,
        "status": status(stage.get("status"), not_applicable="UNPROVED"),
        "frame": modes["frame"],
    }


def find_library_component(manifest: dict[str, Any], cid: str) -> dict[str, Any]:
    for item in manifest.get("components", []) if isinstance(manifest.get("components"), list) else []:
        if str(item.get("contract_id")) == cid:
            return item
    return {}


def rtl_reference(
    repo: Path, receipt: dict[str, Any], component: dict[str, Any], cid: str
) -> dict[str, Any]:
    accepted = receipt.get("accepted_rtl")
    module_path = (
        repo / "library" / str(component.get("module_file", ""))
        if component.get("module_file")
        else None
    )
    if accepted and Path(str(accepted)).is_file():
        path = Path(str(accepted))
    elif module_path and module_path.is_file():
        path = module_path
    else:
        path = None
    return {
        "module": component.get("module") or cid,
        "path": str(path) if path else component.get("module_file"),
        "href": file_uri(path) if path else None,
        "sha256": component.get("module_sha256") or (file_hash(path) if path else None),
        "artifact_dir": component.get("artifact_dir") or receipt.get("source_artifact"),
        "available": bool(path and path.is_file()),
    }


def promotion_model(
    repo: Path, receipt: dict[str, Any], component: dict[str, Any], cid: str
) -> dict[str, Any]:
    stale: list[str] = []
    if component:
        if (
            component.get("contract_hash")
            and receipt.get("contract_hash")
            and component.get("contract_hash") != receipt.get("contract_hash")
        ):
            stale.append("accepted artifact contract hash differs from selected receipt")
        artifact_dir = repo / str(component.get("artifact_dir", ""))
        if component.get("artifact_dir") and not artifact_dir.is_dir():
            stale.append("content-addressed artifact directory is missing")
        module_file = repo / "library" / str(component.get("module_file", ""))
        if component.get("module_file") and not module_file.is_file():
            stale.append("legacy RTL path is missing")
    return {
        "status": status(component.get("status"), not_applicable="UNPROVED") if component else "UNPROVED",
        "immutable": bool(component),
        "contract_hash": receipt.get("contract_hash") or component.get("contract_hash"),
        "promoted_at": component.get("promoted_at"),
        "last_verified_run_id": component.get("last_verified_run_id"),
        "module": component.get("module"),
        "artifact_dir": component.get("artifact_dir"),
        "stale": bool(stale),
        "stale_reasons": stale,
    }


def strategy_entries(storage: Path, cid: str) -> list[dict[str, Any]]:
    runs_dir = storage / "runs" if (storage / "runs").is_dir() else storage
    result: list[dict[str, Any]] = []
    if not runs_dir.is_dir():
        return result
    for run_dir in sorted(runs_dir.iterdir()):
        if not run_dir.is_dir():
            continue
        run = read_json(run_dir / "run.json", {}) or {}
        run_id = str(run.get("run_id") or run_dir.name)
        selected_ids = {
            str(item.get("contract_id"))
            for item in run.get("functions", [])
            if isinstance(item, dict)
        }
        if cid in selected_ids:
            selected = next(
                (item for item in run.get("functions", [])
                 if isinstance(item, dict) and str(item.get("contract_id")) == cid),
                {},
            )
            result.append({
                "run_id": run_id,
                "decision": "selected",
                "rationale": run.get("strategy"),
                "profile": run.get("profile"),
                "model_tier": selected.get("model_tier"),
            })
        function_dir = run_dir / "functions" / safe_id(cid)
        plan = read_json(function_dir / "plan.json", {}) or {}
        if plan:
            result.append({
                "run_id": run_id,
                "decision": "planned",
                "rationale": plan.get("selection_reason"),
                "profile": run.get("profile"),
                "model_tier": plan.get("model_tier"),
                "refresh": plan.get("refresh"),
            })
        strategy = run_dir / "strategy.jsonl"
        if strategy.is_file():
            for line in strategy.read_text(encoding="utf-8", errors="replace").splitlines():
                try:
                    entry = json.loads(line)
                except json.JSONDecodeError:
                    continue
                if cid in json.dumps(entry, sort_keys=True):
                    result.append({
                        "run_id": run_id,
                        "event": entry.get("event"),
                        "decision": entry.get("decision"),
                        "rationale": entry.get("rationale"),
                        "attempt": entry.get("attempt"),
                        "job_id": entry.get("job_id"),
                    })
    unique: list[dict[str, Any]] = []
    seen: set[str] = set()
    for item in result:
        key = json.dumps(item, sort_keys=True, ensure_ascii=False)
        if key not in seen:
            seen.add(key)
            unique.append(item)
    return sorted(unique, key=lambda item: (str(item.get("run_id")), str(item.get("decision"))))


def short_receipt(
    receipt: dict[str, Any], run: dict[str, Any], function_dir: Path | None = None
) -> dict[str, Any]:
    _, candidate_ratio = candidate_model(receipt)
    vector = vector_model(receipt)
    matrix = matrix_model(receipt)
    return {
        "run_id": run.get("run_id"),
        "profile": run.get("profile"),
        "status": status(receipt.get("status"), not_applicable="UNPROVED"),
        "candidate_pass_rate": candidate_ratio.get("display", "—/—"),
        "frame_pass_rate": matrix["frame"].get("display", "0/0"),
        "vectors": vector.get("executed", 0),
        "contract_hash": receipt.get("contract_hash"),
        "rtl_sha256": receipt.get("rtl_sha256"),
        "timestamp": run_timestamp(run, str(run.get("run_id", ""))),
    }


def comparison(history: list[dict[str, Any]]) -> str:
    if len(history) < 2:
        return "NEW"
    current, previous = history[-1], history[-2]
    if (
        current.get("status") == previous.get("status")
        and current.get("candidate_pass_rate") == previous.get("candidate_pass_rate")
        and current.get("frame_pass_rate") == previous.get("frame_pass_rate")
    ):
        return "UNCHANGED"
    if status_rank(str(current.get("status"))) > status_rank(str(previous.get("status"))):
        return "IMPROVED"
    if status_rank(str(current.get("status"))) < status_rank(str(previous.get("status"))):
        return "REGRESSION"
    return "CHANGED"


def normalized_function(
    repo: Path,
    storage: Path,
    run: dict[str, Any],
    receipt: dict[str, Any],
    plan: dict[str, Any],
    contracts: dict[str, dict[str, Any]],
    manifest: dict[str, Any],
    history_receipts: list[tuple[dict[str, Any], dict[str, Any]]],
    function_dir: Path | None,
) -> dict[str, Any]:
    if receipt.get("contract_id"):
        cid = str(receipt["contract_id"])
    elif plan.get("contract_id"):
        cid = str(plan["contract_id"])
    elif function_dir:
        cid = function_dir.name
    else:
        cid = "unknown"
    contract = contract_for(contracts, cid, receipt)
    trace = traceability_model(repo, contract, receipt, cid)
    stages = make_stage_checklist(receipt, plan)
    receipt_status = status(
        receipt.get("status"),
        not_applicable="RUNNING" if plan else "UNPROVED",
    )
    source_gate = receipt.get("source_gate") if isinstance(receipt.get("source_gate"), dict) else {}
    blockers: list[str] = [str(item) for item in (receipt.get("blockers") or []) if item]
    blockers.extend(str(item) for item in (source_gate.get("blockers") or []) if item)
    for stage in stages:
        if stage.get("required") and stage.get("status") in {"FAIL", "BLOCKED", "INFRASTRUCTURE_FAILURE"}:
            blockers.extend(stage.get("blockers") or [])
    if trace["spec"]["status"] == "SPEC_UNAVAILABLE":
        blockers.append("SPEC_UNAVAILABLE")
    if receipt_status == "PASS" and source_gate.get("status") == "BLOCKED":
        receipt_status = "BLOCKED"
    candidates, candidate_ratio = candidate_model(receipt)
    vectors = vector_model(receipt)
    mutations = mutation_model(repo, receipt)
    matrix = matrix_model(receipt)
    generator = find_stage(receipt, "generator_cache", "generator")
    route = generator.get("route") if isinstance(generator.get("route"), dict) else {}
    component = find_library_component(manifest, cid)
    rtl = rtl_reference(repo, receipt, component, cid)
    promotion = promotion_model(repo, receipt, component, cid)
    if promotion["stale"]:
        blockers.extend(promotion["stale_reasons"])
    history = [short_receipt(raw, run_value) for run_value, raw in history_receipts]
    history.sort(key=lambda item: (str(item.get("timestamp")), str(item.get("run_id"))))
    if history:
        current_summary = short_receipt(receipt, run)
        history = [item for item in history if item.get("run_id") != run.get("run_id")]
        history.append(current_summary)
        history.sort(key=lambda item: (str(item.get("timestamp")), str(item.get("run_id"))))
    comparison_value = comparison(history)
    current_stage = (
        "complete"
        if receipt_status == "PASS"
        else next(
            (
                item["label"]
                for item in stages
                if item.get("status") not in {"PASS", "UNPROVED"}
                or item.get("raw_status") == "MISSING"
            ),
            "unavailable",
        )
    )
    if receipt_status in {"FAIL", "INFRASTRUCTURE_FAILURE", "BLOCKED"} and blockers:
        next_action = "Inspect the failed stage, expected/actual values, and smallest counterexample before rerunning."
    elif receipt_status == "UNPROVED":
        next_action = "Complete the missing proof/receipt stage; keep the C boundary authoritative until then."
    elif receipt_status == "RUNNING":
        next_action = "Wait for the durable receipt, then rebuild the dashboard."
    elif promotion["stale"]:
        next_action = "Refresh the accepted artifact for the current contract hash before using it as library evidence."
    else:
        next_action = "Review the accepted RTL and retain the recorded C_ONLY rollback/reference path."
    source_gate_model = {
        "status": status(source_gate.get("status"), not_applicable="UNPROVED"),
        "blockers": source_gate.get("blockers", []),
        "pdf": source_gate.get("pdf", {}),
        "source": source_gate.get("source", {}),
        "compile_check": source_gate.get("compile_check", {}),
        "build": source_gate.get("build", {}),
    }
    chain = trace["chain"]
    chain[3]["href"] = rtl.get("href")
    chain[3]["status"] = "PASS" if rtl.get("available") or component.get("status") == "PASS" else "UNPROVED"
    verification_path = (
        repo / "library" / str(component.get("verification_file", ""))
        if component.get("verification_file")
        else None
    )
    chain[4]["href"] = file_uri(verification_path) if verification_path and verification_path.is_file() else None
    chain[4]["status"] = "PASS" if receipt_status == "PASS" else receipt_status
    chain[5]["status"] = matrix["frame"].get("status", "UNPROVED")
    return {
        "schema_version": 1,
        "contract_id": cid,
        "function": contract_function(contract, receipt),
        "run_id": run.get("run_id"),
        "profile": run.get("profile"),
        "status": receipt_status,
        "raw_status": receipt.get("status"),
        "stage": {"current": current_stage, "checklist": stages},
        "blockers": sorted(set(blockers)),
        "candidates": {"items": candidates, **candidate_ratio},
        "vectors": vectors,
        "mutations": mutations,
        "matrix": matrix,
        "cache": {
            "status": status(generator.get("status"), not_applicable="UNPROVED"),
            "execution_status": generator.get("execution_status"),
            "hit": "REUSED" in str(generator.get("execution_status", "")).upper() or bool(plan.get("cached_control")),
        },
        "model": {
            "tier": route.get("tier") or plan.get("model_tier"),
            "name": route.get("model"),
            "model_env": route.get("model_env"),
            "calls": as_int(generator.get("model_calls"), as_int(receipt.get("model_calls"), 0)),
            "tokens": as_int(generator.get("tokens"), as_int(receipt.get("tokens"), 0)),
            "route_source": route.get("source"),
        },
        "hashes": {
            "source": first(source_gate.get("source", {}), "sha256", "source_hashes_sha256", default=run.get("source_hash")),
            "spec": first(source_gate.get("pdf", {}), "sha256", default=run.get("spec_hash")),
            "contract": receipt.get("contract_hash") or component.get("contract_hash"),
            "rtl": rtl.get("sha256"),
        },
        "source_gate": source_gate_model,
        "traceability": {**trace, "chain": chain},
        "promotion": promotion,
        "rtl": rtl,
        "history": history,
        "comparison": comparison_value,
        "strategy_history": strategy_entries(storage, cid),
        "plan": {
            key: plan.get(key)
            for key in (
                "selection_reason", "kind", "candidate_limit", "model_tier",
                "refresh", "cached_control",
            )
            if key in plan
        },
        "next_action": next_action,
        "links": {
            "page": f"functions/{safe_id(cid)}.html",
            "report": f"../reports/functions/{safe_id(cid)}.md",
            "contract": f"../library/contracts/{safe_id(cid)}.json",
        },
        "artifact": {
            "source_artifact": receipt.get("source_artifact"),
            "function_dir": str(function_dir) if function_dir else None,
            "receipt": str(function_dir / "receipt.json") if function_dir else None,
            "traceability": str(function_dir / "traceability.json") if function_dir else None,
        },
    }


def synthetic_library_receipt(
    component: dict[str, Any], verification: dict[str, Any], run_id: str | None
) -> dict[str, Any]:
    value = dict(verification or {})
    value.setdefault("contract_id", component.get("contract_id"))
    value.setdefault("function", component.get("function"))
    value.setdefault("contract_hash", component.get("contract_hash"))
    value.setdefault("status", component.get("status", "UNPROVED"))
    value.setdefault("candidate_pass_rate", "—/—")
    value.setdefault("frame_pass_rate", "0/0")
    value.setdefault("run_id", run_id)
    return value


@dataclasses.dataclass
class Dataset:
    repo: Path
    resolution: StorageResolution
    records: list[dict[str, Any]]
    selected_run_id: str | None
    overview: dict[str, Any]
    functions: list[dict[str, Any]]
    runs: list[dict[str, Any]]
    traceability: dict[str, Any]
    library_index: dict[str, Any]
    path_map: dict[str, Any]
    docs: str


def make_traceability_index(functions: list[dict[str, Any]]) -> dict[str, Any]:
    spec: dict[str, list[dict[str, Any]]] = defaultdict(list)
    code: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for item in functions:
        link = {
            "contract_id": item["contract_id"],
            "function": item["function"]["name"],
            "page": item["links"]["page"],
        }
        for value in item["traceability"]["spec"].get("links", []):
            key = str(value.get("anchor_id") or value.get("section") or value.get("page"))
            spec[key].append({
                **link,
                "page_number": value.get("page"),
                "section": value.get("section"),
                "table": value.get("table"),
                "status": value.get("status"),
                "href": value.get("href"),
            })
        source = item["traceability"]["source"]
        source_file = source.get("file") or "unknown"
        key = f"{source_file}:{source['span'].get('start_line')}"
        code[key].append({
            **link,
            "source_file": source_file,
            "span": source.get("span"),
            "href": source.get("href"),
        })
    return {
        "schema_version": 1,
        "spec_to_code": dict(sorted(spec.items())),
        "code_to_spec": dict(sorted(code.items())),
    }


def make_library_index(
    repo: Path,
    manifest: dict[str, Any],
    functions: list[dict[str, Any]],
    resolution: StorageResolution,
) -> dict[str, Any]:
    function_by_id = {item["contract_id"]: item for item in functions}
    components: list[dict[str, Any]] = []
    stale: list[dict[str, Any]] = []
    for component in manifest.get("components", []) if isinstance(manifest.get("components"), list) else []:
        cid = str(component.get("contract_id"))
        item = function_by_id.get(cid, {})
        contract_hash = str(
            component.get("contract_hash")
            or item.get("hashes", {}).get("contract")
            or ""
        )
        canonical = f"library/accepted/{safe_id(cid)}/{contract_hash}"
        module_file = str(component.get("module_file") or f"rtl/{safe_id(cid)}.sv")
        verification_file = str(
            component.get("verification_file") or f"verification/{safe_id(cid)}.json"
        )
        entry = {
            "contract_id": cid,
            "function": component.get("function") or item.get("function", {}).get("name"),
            "status": status(component.get("status"), not_applicable="UNPROVED"),
            "immutable": True,
            "contract_hash": contract_hash,
            "canonical_path": canonical,
            "rtl": {
                "path": f"{canonical}/rtl/{Path(module_file).name}",
                "legacy_path": f"library/{module_file}",
                "reference_path": component.get("artifact_dir"),
                "sha256": component.get("module_sha256"),
                "materialized": False,
            },
            "verification": {
                "path": f"{canonical}/verification/{Path(verification_file).name}",
                "legacy_path": f"library/{verification_file}",
                "reference_path": component.get("verification_file"),
                "materialized": False,
            },
            "contract": {
                "path": f"{canonical}/contract/contract.json",
                "legacy_path": component.get("contract_file"),
                "materialized": False,
            },
            "provenance": {
                "source_hash": manifest.get("source_hash"),
                "spec_hash": manifest.get("spec_hash"),
                "artifact_dir": component.get("artifact_dir"),
                "promoted_at": component.get("promoted_at"),
                "last_verified_run_id": component.get("last_verified_run_id"),
                "boundary": component.get("boundary"),
                "authority": component.get("authority"),
            },
            "history": item.get("history", []),
            "stale": item.get("promotion", {}).get("stale", False),
            "stale_reasons": item.get("promotion", {}).get("stale_reasons", []),
        }
        components.append(entry)
        if entry["stale"]:
            stale.append({"contract_id": cid, "reasons": entry["stale_reasons"]})
    return {
        "schema_version": 1,
        "source_of_truth": "durable receipts and immutable content-addressed artifacts",
        "library": manifest.get("library", "dsc-verilog-library"),
        "source_hash": manifest.get("source_hash"),
        "spec_hash": manifest.get("spec_hash"),
        "storage": resolution.as_dict(),
        "components": components,
        "stale_artifacts": stale,
    }


def make_path_map(
    repo: Path,
    storage: Path,
    manifest: dict[str, Any],
    functions: list[dict[str, Any]],
) -> dict[str, Any]:
    components = {
        str(item.get("contract_id")): item
        for item in manifest.get("components", [])
        if isinstance(item, dict)
    }
    entries: list[dict[str, Any]] = []
    legacy_roots = {
        "rtl/": {
            "meaning": "legacy candidate/promoted RTL; index only",
            "canonical": "runs/<run-id>/functions/<contract-id>/rtl/",
        },
        "verification/": {
            "meaning": "legacy run-local verification receipts",
            "canonical": "runs/<run-id>/functions/<contract-id>/verification/",
        },
        "library/rtl/": {
            "meaning": "legacy accepted RTL flat path",
            "canonical": "library/accepted/<contract-id>/<contract-hash>/rtl/",
        },
        "library/verification/": {
            "meaning": "legacy accepted verification flat path",
            "canonical": "library/accepted/<contract-id>/<contract-hash>/verification/",
        },
        "library/contracts/": {
            "meaning": "legacy accepted contract flat path",
            "canonical": "library/accepted/<contract-id>/<contract-hash>/contract/",
        },
    }

    def add(
        path: Path,
        canonical: str,
        reference: str | None,
        sha256: str | None,
        kind: str,
    ) -> None:
        try:
            legacy_path = str(path.relative_to(repo))
        except ValueError:
            legacy_path = str(path)
        reference_exists = bool(reference and Path(reference).exists())
        entries.append({
            "legacy_path": legacy_path,
            "canonical_path": canonical,
            "reference_path": reference,
            "sha256": sha256,
            "kind": kind,
            "legacy_exists": path.exists(),
            "reference_exists": reference_exists,
        })

    rtl_root = repo / "library" / "rtl"
    if rtl_root.is_dir():
        for path in sorted(rtl_root.glob("*")):
            component = next(
                (
                    value for value in components.values()
                    if Path(str(value.get("module_file", ""))).name == path.name
                ),
                None,
            )
            if not component:
                continue
            cid = str(component.get("contract_id"))
            contract_hash = str(component.get("contract_hash"))
            reference = (
                str(repo / str(component.get("artifact_dir")))
                if component.get("artifact_dir")
                else None
            )
            add(
                path,
                f"library/accepted/{safe_id(cid)}/{contract_hash}/rtl/{path.name}",
                reference,
                component.get("module_sha256") or file_hash(path),
                "accepted_rtl",
            )

    verification_root = repo / "library" / "verification"
    if verification_root.is_dir():
        for path in sorted(verification_root.glob("*.json")):
            cid = path.stem
            component = components.get(cid, {})
            contract_hash = str(component.get("contract_hash", "unknown"))
            add(
                path,
                f"library/accepted/{safe_id(cid)}/{contract_hash}/verification/{path.name}",
                str(repo / str(component.get("verification_file")))
                if component.get("verification_file")
                else None,
                file_hash(path),
                "accepted_verification",
            )

    contract_root = repo / "library" / "contracts"
    if contract_root.is_dir():
        for path in sorted(contract_root.glob("*.json")):
            cid = path.stem
            component = components.get(cid, {})
            contract_hash = str(component.get("contract_hash", "unknown"))
            add(
                path,
                f"library/accepted/{safe_id(cid)}/{contract_hash}/contract/contract.json",
                str(path),
                file_hash(path),
                "accepted_contract",
            )

    verification_legacy = repo / "verification"
    if verification_legacy.is_dir():
        for path in sorted(verification_legacy.rglob("*.json")):
            if path.name == "verification-receipt.json" or path.parent == verification_legacy:
                continue
            cid = path.parent.name
            item = next(
                (value for value in functions if value.get("contract_id") == cid), {}
            )
            run_id = item.get("run_id") or "<run-id>"
            add(
                path,
                f"runs/{run_id}/functions/{safe_id(cid)}/verification/{path.name}",
                str(path),
                file_hash(path),
                "legacy_run_verification",
            )

    candidate_root = repo / "rtl" / "candidates"
    if candidate_root.is_dir():
        for path in sorted(candidate_root.rglob("*.sv")):
            cid = path.parent.name
            item = next(
                (value for value in functions if value.get("contract_id") == cid), {}
            )
            run_id = item.get("run_id") or "<run-id>"
            add(
                path,
                f"runs/{run_id}/functions/{safe_id(cid)}/rtl/{path.name}",
                item.get("artifact", {}).get("source_artifact"),
                file_hash(path),
                "legacy_candidate_rtl",
            )

    for item in functions:
        cid = str(item.get("contract_id"))
        component = components.get(cid, {})
        contract_hash = str(
            component.get("contract_hash")
            or item.get("hashes", {}).get("contract")
            or "unknown"
        )
        reference = component.get("artifact_dir") or item.get("artifact", {}).get("source_artifact")
        entries.append({
            "legacy_path": f"library/accepted/{safe_id(cid)}/{contract_hash}/",
            "canonical_path": f"library/accepted/{safe_id(cid)}/{contract_hash}/",
            "reference_path": reference,
            "sha256": contract_hash,
            "kind": "canonical_content_addressed",
            "legacy_exists": False,
            "reference_exists": bool(reference),
        })
    return {
        "schema_version": 1,
        "source_of_truth": "JSON receipts and content-addressed artifact hashes",
        "legacy_receipts_readable": True,
        "storage_root": str(storage),
        "roots": legacy_roots,
        "entries": sorted(
            entries, key=lambda value: (value["legacy_path"], value["kind"])
        ),
    }


def directory_layout_doc(resolution: StorageResolution) -> str:
    fallback = resolution.fallback_reason or "none"
    return f"""# Regression and traceability directory layout

JSON receipts remain the source of truth. This checkout contains indexes and
human-readable projections; it does not copy RTL, C source, or the external
DSC PDF.

## New meanings

    runs/<run-id>/functions/<contract-id>/
      rtl/              run-local candidate RTL references
      verification/     run-local receipt/counterexample references
      logs/             run-local tool logs

    library/accepted/<contract-id>/<contract-hash>/
      rtl/              immutable accepted RTL (content-addressed reference)
      verification/     accepted evidence (content-addressed reference)
      contract/         locked contract (content-addressed reference)

    dashboard/          static HTML and normalized view models
    reports/            readable regression-summary.md and per-function reports
    library/index.json  accepted-library index with stale/provenance checks
    path-map.json       legacy-to-new path mapping

## Legacy compatibility

The existing rtl/, verification/, library/rtl/, library/verification/, and
library/contracts/ paths are indexed in path-map.json and remain readable.
Entries point at the existing content-addressed artifact or receipt; no large
file is copied into the new layout.

## Storage resolution

- selected root: {resolution.root}
- resolution mode: {resolution.mode}
- requested root: {resolution.requested}
- SMB fallback reason: {fallback}

If the SMB share is unavailable, the dashboard reports LOCAL_REPOSITORY and
uses only repository-local legacy receipts. The PDF remains external and is
shown as SPEC_UNAVAILABLE when its recorded path cannot be opened.
"""


def build_dataset(
    repo: Path, resolution: StorageResolution, requested_run: str
) -> Dataset:
    records = load_run_records(resolution.root)
    selected_id = resolve_run_id(records, requested_run)
    selected_record = next(
        (item for item in records if str(item["run"].get("run_id")) == selected_id),
        None,
    )
    selected_run = (
        selected_record["run"]
        if selected_record
        else {"run_id": selected_id or "no-run", "profile": "none", "status": "UNPROVED"}
    )
    contracts = load_contracts(repo)
    manifest = load_library_manifest(repo)
    verification_by_id: dict[str, dict[str, Any]] = {}
    verification_dir = repo / "library" / "verification"
    if verification_dir.is_dir():
        for path in verification_dir.glob("*.json"):
            verification_by_id[path.stem] = read_json(path, {}) or {}

    selected_receipts: dict[str, tuple[dict[str, Any], Path]] = {}
    if selected_record:
        functions_dir = selected_record["path"] / "functions"
        if functions_dir.is_dir():
            for function_dir in sorted(functions_dir.iterdir()):
                if not function_dir.is_dir():
                    continue
                receipt = read_json(function_dir / "receipt.json", {}) or {}
                plan = read_json(function_dir / "plan.json", {}) or {}
                if receipt or plan:
                    receipt.setdefault("contract_id", function_dir.name)
                    if not receipt:
                        receipt = {
                            "contract_id": function_dir.name,
                            "function": plan.get("function"),
                            "status": "RUNNING",
                        }
                    selected_receipts[str(receipt.get("contract_id"))] = (
                        receipt, function_dir
                    )
        for item in selected_run.get("functions", []) if isinstance(selected_run.get("functions"), list) else []:
            if not isinstance(item, dict):
                continue
            cid = str(item.get("contract_id", ""))
            if cid and cid not in selected_receipts:
                selected_receipts[cid] = (
                    {
                        "contract_id": cid,
                        "function": item.get("function"),
                        "status": "RUNNING",
                    },
                    selected_record["path"] / "functions" / safe_id(cid),
                )

    if not selected_receipts:
        for component in manifest.get("components", []) if isinstance(manifest.get("components"), list) else []:
            cid = str(component.get("contract_id", ""))
            if cid:
                selected_receipts[cid] = (
                    synthetic_library_receipt(
                        component, verification_by_id.get(cid, {}), selected_id
                    ),
                    repo / "library" / "verification" / f"{cid}.json",
                )

    # Include accepted leaves absent from an incomplete selected run as
    # explicit UNPROVED rows instead of silently dropping coverage.
    for component in manifest.get("components", []) if isinstance(manifest.get("components"), list) else []:
        cid = str(component.get("contract_id", ""))
        if cid and cid not in selected_receipts:
            selected_receipts[cid] = (
                {
                    "contract_id": cid,
                    "function": component.get("function"),
                    "status": "UNPROVED",
                    "blockers": ["not present in selected run"],
                },
                repo / "library" / "verification" / f"{cid}.json",
            )

    history_by_id: dict[str, list[tuple[dict[str, Any], dict[str, Any]]]] = defaultdict(list)
    for record in records:
        for receipt in record["receipts"]:
            cid = str(receipt.get("contract_id", ""))
            if cid:
                history_by_id[cid].append((record["run"], receipt))

    functions: list[dict[str, Any]] = []
    for cid, (receipt, function_dir) in sorted(selected_receipts.items()):
        plan = read_json(function_dir / "plan.json", {}) if function_dir.is_dir() else {}
        plan = plan or {}
        functions.append(
            normalized_function(
                repo,
                resolution.root,
                selected_run,
                receipt,
                plan,
                contracts,
                manifest,
                history_by_id.get(cid, []),
                function_dir if function_dir.is_dir() else None,
            )
        )
    functions.sort(
        key=lambda item: (
            str(item.get("function", {}).get("name", "")),
            str(item.get("contract_id")),
        )
    )

    run_summaries: list[dict[str, Any]] = []
    for record in records:
        run = record["run"]
        candidate_passed = candidate_total = frame_passed = frame_total = vectors = 0
        for receipt in record["receipts"]:
            _, candidate_ratio = candidate_model(receipt)
            candidate_passed += candidate_ratio.get("passed") or 0
            candidate_total += candidate_ratio.get("total") or 0
            matrix = matrix_model(receipt)
            frame_passed += matrix["frame"].get("passed") or 0
            frame_total += matrix["frame"].get("total") or 0
            vectors += vector_model(receipt).get("executed") or 0
        run_summaries.append({
            "run_id": run.get("run_id"),
            "profile": run.get("profile"),
            "status": record["status"],
            "raw_status": run.get("status"),
            "timestamp": record["timestamp"],
            "function_count": len(record["receipts"]),
            "counts": record["counts"],
            "candidates": {
                "passed": candidate_passed,
                "total": candidate_total,
                "display": f"{candidate_passed}/{candidate_total}",
            },
            "frames": {
                "passed": frame_passed,
                "total": frame_total,
                "display": f"{frame_passed}/{frame_total}",
            },
            "vectors": vectors,
            "source_hash": run.get("source_hash"),
            "spec_hash": run.get("spec_hash"),
        })
    selected_summary = next(
        (item for item in run_summaries if item.get("run_id") == selected_id),
        None,
    )
    if selected_summary is None:
        selected_summary = {
            "run_id": selected_id,
            "status": "UNPROVED",
            "function_count": len(functions),
            "counts": {},
        }

    counts = Counter(item.get("status") for item in functions)
    candidates = {
        "passed": sum(item["candidates"].get("passed") or 0 for item in functions),
        "total": sum(item["candidates"].get("total") or 0 for item in functions),
    }
    frames = {
        "passed": sum(item["matrix"]["frame"].get("passed") or 0 for item in functions),
        "total": sum(item["matrix"]["frame"].get("total") or 0 for item in functions),
    }
    vector_count = sum(item["vectors"].get("executed") or 0 for item in functions)

    failures: list[dict[str, Any]] = []
    for item in functions:
        if item.get("status") != "PASS" or item.get("blockers"):
            failures.append({
                "contract_id": item.get("contract_id"),
                "function": item.get("function", {}).get("name"),
                "run_id": item.get("run_id"),
                "status": item.get("status"),
                "stage": item.get("stage", {}).get("current"),
                "blockers": item.get("blockers", []),
                "counterexample": item.get("mutations", {}).get("smallest_counterexample"),
                "next_action": item.get("next_action"),
            })

    historical_failures: list[dict[str, Any]] = []
    for record in records:
        for receipt in record["receipts"]:
            normalized = status(receipt.get("status"), not_applicable="UNPROVED")
            if normalized == "PASS":
                continue
            historical_failures.append({
                "run_id": record["run"].get("run_id"),
                "contract_id": receipt.get("contract_id"),
                "function": receipt.get("function"),
                "status": normalized,
                "blockers": receipt.get("blockers", []),
                "counterexample": collect_counterexamples(receipt)[:1],
            })

    spec = spec_manifest(repo)
    source_gate = selected_run.get("source_gate") or (
        functions[0].get("source_gate") if functions else {}
    )
    overview = {
        "schema_version": 1,
        "selected_run": selected_summary,
        "storage": resolution.as_dict(),
        "source": {
            "pdf": spec.get("spec", {}),
            "source": spec.get("source", {}),
            "source_gate": source_gate,
            "spec_status": (
                "AVAILABLE"
                if Path(str(spec.get("spec", {}).get("path", ""))).is_file()
                else "SPEC_UNAVAILABLE"
            ),
        },
        "counts": dict(sorted(counts.items())),
        "progress": {
            "functions": {
                "passed": counts.get("PASS", 0),
                "total": len(functions),
                "display": f"{counts.get('PASS', 0)}/{len(functions)}",
            },
            "candidates": {**candidates, "display": f"{candidates['passed']}/{candidates['total']}"},
            "frames": {**frames, "display": f"{frames['passed']}/{frames['total']}"},
            "vectors": vector_count,
        },
        "failures": failures,
        "historical_failures": historical_failures[:50],
        "function_count": len(functions),
        "run_count": len(run_summaries),
    }
    return Dataset(
        repo=repo,
        resolution=resolution,
        records=records,
        selected_run_id=selected_id,
        overview=overview,
        functions=functions,
        runs=run_summaries,
        traceability=make_traceability_index(functions),
        library_index=make_library_index(repo, manifest, functions, resolution),
        path_map=make_path_map(repo, resolution.root, manifest, functions),
        docs=directory_layout_doc(resolution),
    )


def md_escape(value: Any) -> str:
    return str(value if value is not None else "—").replace("|", "\\|").replace("\n", " ")


def markdown_link(label: Any, href: str | None) -> str:
    return f"{md_escape(label)} ({href})" if href else md_escape(label)


def report_function(item: dict[str, Any]) -> str:
    trace = item["traceability"]
    lines = [
        f"# {item['function']['name']} ({item['contract_id']})",
        "",
        f"Status: {item['status']}",
        f"Selected run: {item.get('run_id')}",
        f"Stage: {item['stage']['current']}",
        f"Next action: {item['next_action']}",
        "",
    ]
    if item.get("blockers"):
        lines += ["## Blockers", "", *[f"- {value}" for value in item["blockers"]], ""]
    lines += [
        "## Stage checklist", "",
        "| Stage | Status | Detail |", "|---|---|---|",
    ]
    lines += [
        f"| {md_escape(stage['label'])} | {stage['status']} | {md_escape(stage.get('detail'))} |"
        for stage in item["stage"]["checklist"]
    ]
    lines += [
        "", "## Interface and width derivation", "",
        "| Direction | Port | Width | Signed | Role | Domain | Authority / formula |",
        "|---|---|---:|---|---|---|---|",
    ]
    for port in trace.get("ports", []):
        domain = port.get("domain", {})
        domain_text = domain.get("basis") or domain.get("range") or domain.get("values") or "—"
        derivation = port.get("width_derivation", {})
        lines.append(
            f"| {md_escape(port.get('direction'))} | {md_escape(port.get('name'))} | "
            f"{md_escape(port.get('width'))} | {md_escape(port.get('signed'))} | "
            f"{md_escape(port.get('role'))} | {md_escape(domain_text)} | "
            f"{md_escape(derivation.get('authority'))}: {md_escape(derivation.get('formula'))} "
            f"({md_escape(derivation.get('review_status'))}) |"
        )
    lines += ["", "## Spec -> C -> Contract -> RTL -> Verification -> Frame", ""]
    for link in trace.get("chain", []):
        lines.append(f"- {link['label']}: {markdown_link(link['status'], link.get('href'))}")
    lines += [
        "",
        f"- Spec status: {trace['spec']['status']}; PDF: {md_escape(trace['spec'].get('path'))}",
        f"- C: {markdown_link(trace['source'].get('file'), trace['source'].get('href'))} "
        f"lines {trace['source']['span'].get('start_line')}-{trace['source']['span'].get('end_line')}",
        "",
        "## Candidates, mutations, and counterexamples", "",
        f"- Candidates passed: {item['candidates']['display']}",
        f"- Vectors: {item['vectors']['executed']}, shards {item['vectors']['shards']['display']}, "
        f"verification {md_escape(item['vectors'].get('verification_status'))}",
        f"- Mutation evidence: {item['mutations']['result']['display']}, planned {item['mutations']['planned']} "
        f"({md_escape(item['mutations']['result'].get('basis'))})",
    ]
    if item["mutations"].get("counterexamples"):
        lines += [
            "", "| Stage | Candidate | Expected | Actual | Inputs |",
            "|---|---|---|---|---|",
        ]
        for ce in item["mutations"]["counterexamples"]:
            lines.append(
                f"| {md_escape(ce.get('stage'))} | {md_escape(ce.get('candidate'))} | "
                f"{md_escape(ce.get('expected'))} | {md_escape(ce.get('actual'))} | "
                f"{md_escape(ce.get('inputs'))} |"
            )
    else:
        lines.append("\nNo counterexample was recorded for the selected accepted path.")
    lines += ["", "## Matrix", "", "| Mode | Result |", "|---|---|"]
    for mode, result in item["matrix"]["modes"].items():
        lines.append(f"| {mode} | {result.get('status')} ({result.get('display')}) |")
    lines += [
        "", "## Hashes, promotion, and strategy", "",
        "| Identity | Value |", "|---|---|",
    ]
    for key, value in item["hashes"].items():
        lines.append(f"| {key} | {md_escape(value)} |")
    lines += [
        f"| promotion | {md_escape(item['promotion'].get('status'))}; "
        f"immutable={md_escape(item['promotion'].get('immutable'))}; "
        f"stale={md_escape(item['promotion'].get('stale'))} |",
        "", "### Strategy history", "",
    ]
    if item["strategy_history"]:
        lines += ["| Run | Decision | Tier | Rationale |", "|---|---|---|---|"]
        for entry in item["strategy_history"]:
            lines.append(
                f"| {md_escape(entry.get('run_id'))} | {md_escape(entry.get('decision'))} | "
                f"{md_escape(entry.get('model_tier'))} | {md_escape(entry.get('rationale'))} |"
            )
    else:
        lines.append("No durable strategy record was found for this function.")
    lines += [
        "", "## Run comparison", "",
        "| Run | Status | Candidates | Frames | Vectors | Change |",
        "|---|---|---|---|---:|---|",
    ]
    history = item.get("history", [])
    for index, entry in enumerate(history):
        change = "current" if index == len(history) - 1 else ""
        lines.append(
            f"| {md_escape(entry.get('run_id'))} | {md_escape(entry.get('status'))} | "
            f"{md_escape(entry.get('candidate_pass_rate'))} | "
            f"{md_escape(entry.get('frame_pass_rate'))} | {md_escape(entry.get('vectors'))} | {change} |"
        )
    return "\n".join(lines)


CSS = """
:root{color-scheme:light;--ink:#17212b;--muted:#64748b;--line:#d8e0e8;--panel:#fff;--bg:#f5f7fa;--blue:#2563eb;--green:#16803c;--red:#b42318;--amber:#a15c00;--purple:#6941c6}
*{box-sizing:border-box}body{margin:0;background:var(--bg);color:var(--ink);font:14px/1.5 -apple-system,BlinkMacSystemFont,"Segoe UI",sans-serif}a{color:var(--blue);text-decoration:none}a:hover{text-decoration:underline}.wrap{max-width:1500px;margin:0 auto;padding:28px 32px}header{display:flex;justify-content:space-between;gap:24px;align-items:flex-start;margin-bottom:24px}h1{font-size:30px;line-height:1.15;margin:0 0 6px}h2{font-size:20px;margin:28px 0 12px}h3{font-size:16px;margin:22px 0 10px}.muted,.small{color:var(--muted);font-size:12px}.nav{display:flex;flex-wrap:wrap;gap:10px}.nav a,.button{background:var(--panel);border:1px solid var(--line);border-radius:8px;padding:7px 10px}.cards{display:grid;grid-template-columns:repeat(auto-fit,minmax(160px,1fr));gap:12px}.card,.panel{background:var(--panel);border:1px solid var(--line);border-radius:12px;padding:16px;box-shadow:0 1px 2px #00000008}.card strong{font-size:26px;display:block}.grid2{display:grid;grid-template-columns:minmax(0,1fr) minmax(0,1fr);gap:16px}@media(max-width:900px){.wrap{padding:20px 16px}.grid2{grid-template-columns:1fr}header{display:block}.nav{margin-top:14px}}table{border-collapse:collapse;width:100%;background:var(--panel)}th,td{border-bottom:1px solid var(--line);padding:9px 10px;text-align:left;vertical-align:top}th{position:sticky;top:0;background:#eef3f8;z-index:1;cursor:pointer;font-size:12px}tr:hover td{background:#f8fbff}.table-scroll{overflow:auto;border:1px solid var(--line);border-radius:10px}.pill{display:inline-block;border-radius:999px;padding:2px 8px;font-size:11px;font-weight:700;white-space:nowrap}.PASS{background:#dcfce7;color:#166534}.FAIL,.INFRASTRUCTURE_FAILURE{background:#fee4e2;color:#9b1c1c}.BLOCKED{background:#fff0c2;color:#8a4b00}.RUNNING{background:#dbeafe;color:#1e40af}.UNPROVED{background:#eee9fe;color:#5b35a2}.bar{height:10px;border-radius:999px;background:#e8edf2;overflow:hidden;min-width:120px}.bar>i{height:100%;display:block;background:var(--blue)}.bar.green>i{background:var(--green)}.statline{display:flex;justify-content:space-between;gap:12px;margin:8px 0}.failure{border-left:4px solid var(--red);padding:10px 12px;background:#fff5f4;margin:8px 0}.notice{border-left:4px solid var(--amber);padding:10px 12px;background:#fff9e8;margin:10px 0}.chain{display:grid;grid-template-columns:repeat(6,minmax(100px,1fr));gap:8px}@media(max-width:900px){.chain{grid-template-columns:repeat(2,1fr)}}.chain div{border:1px solid var(--line);border-radius:8px;padding:10px;background:#fbfcfe}.chain b{display:block;margin-bottom:4px}.code{font-family:ui-monospace,SFMono-Regular,Menlo,monospace;font-size:12px;word-break:break-word}.nowrap{white-space:nowrap}input,select{padding:8px;border:1px solid var(--line);border-radius:7px;background:#fff}.filters{display:flex;flex-wrap:wrap;gap:8px;margin:12px 0}
"""


def html_status(value: Any) -> str:
    text = str(value or "UNPROVED")
    return f'<span class="pill {html.escape(text)}">{html.escape(text)}</span>'


def embedded_json(value: Any) -> str:
    return json.dumps(value, sort_keys=True, ensure_ascii=False).replace("</", "<\\/")


def page_shell(
    title: str, body: str, script_data: Any | None = None, script: str = ""
) -> str:
    data = (
        f'<script type="application/json" id="page-data">{embedded_json(script_data)}</script>'
        if script_data is not None else ""
    )
    return (
        "<!doctype html><html lang=\"en\"><head><meta charset=\"utf-8\">"
        "<meta name=\"viewport\" content=\"width=device-width,initial-scale=1\">"
        f"<title>{html.escape(title)}</title><style>{CSS}</style></head><body>"
        f"<main class=\"wrap\">{body}</main>{data}<script>{script}</script></body></html>"
    )


def header(title: str, subtitle: str, links: list[tuple[str, str]]) -> str:
    nav = "".join(
        f'<a href="{html.escape(href)}">{html.escape(label)}</a>'
        for label, href in links
    )
    return (
        f"<header><div><h1>{html.escape(title)}</h1>"
        f"<div class=\"muted\">{html.escape(subtitle)}</div></div>"
        f"<nav class=\"nav\">{nav}</nav></header>"
    )


def bar(label: str, passed: int | None, total: int | None, color: str = "") -> str:
    passed = passed or 0
    total = total or 0
    percent = 0 if total <= 0 else max(0, min(100, passed * 100 / total))
    return (
        f'<div class="statline"><span>{html.escape(label)}</span>'
        f"<b>{passed}/{total}</b></div>"
        f'<div class="bar {color}"><i style="width:{percent:.2f}%"></i></div>'
    )


def render_index(dataset: Dataset) -> str:
    overview = dataset.overview
    storage = dataset.resolution
    selected = overview["selected_run"]
    cards = [
        ("Functions", overview["progress"]["functions"]["display"]),
        ("Candidates", overview["progress"]["candidates"]["display"]),
        ("Frame sanity", overview["progress"]["frames"]["display"]),
        ("Vectors", f"{overview['progress']['vectors']:,}"),
        ("Indexed runs", dataset.overview["run_count"]),
    ]
    card_html = "".join(
        f'<div class="card"><div class="muted">{html.escape(str(label))}</div>'
        f'<strong>{html.escape(str(value))}</strong></div>'
        for label, value in cards
    )
    status_bars = "".join(
        bar(key, value, len(dataset.functions), "green" if key == "PASS" else "")
        for key, value in sorted(overview["counts"].items())
    )
    progress_bars = (
        bar("Candidate equivalence", overview["progress"]["candidates"]["passed"], overview["progress"]["candidates"]["total"])
        + bar("Frame sanity", overview["progress"]["frames"]["passed"], overview["progress"]["frames"]["total"], "green")
    )
    notice = (
        f'<div class="notice"><b>LOCAL FALLBACK</b>: '
        f'{html.escape(storage.fallback_reason)}<br>Receipts used: '
        f'<span class="code">{html.escape(str(storage.root))}</span></div>'
        if storage.fallback_reason
        else f'<div class="notice"><b>Storage</b>: {html.escape(storage.mode)} at '
        f'<span class="code">{html.escape(str(storage.root))}</span></div>'
    )
    source_notice = (
        ""
        if overview["source"]["spec_status"] == "AVAILABLE"
        else '<div class="failure"><b>SPEC_UNAVAILABLE</b>: the recorded PDF path is not readable; traceability links remain visible but are not asserted.</div>'
    )
    body = header(
        "DSC regression dashboard",
        f"run {selected.get('run_id')} · {selected.get('status')} · JSON receipts are authoritative",
        [
            ("History", "history.html"),
            ("Traceability", "traceability.html"),
            ("Summary report", "../reports/regression-summary.md"),
            ("Layout", "../DIRECTORY_LAYOUT.md"),
        ],
    )
    body += notice + source_notice + f'<section class="cards">{card_html}</section>'
    body += (
        '<section class="grid2"><div class="panel"><h2>Status distribution</h2>'
        + status_bars
        + '</div><div class="panel"><h2>Verification progress</h2>'
        + progress_bars
        + "</div></section>"
    )
    body += (
        '<h2>Function regression table</h2><div class="filters">'
        '<input id="filter" placeholder="filter function, contract, blocker…">'
        '<select id="status-filter"><option value="">all statuses</option>'
        + "".join(f"<option>{html.escape(key)}</option>" for key in sorted(VALID_STATUSES))
        + '</select></div><div class="table-scroll"><table id="functions">'
        '<thead><tr><th data-key="function">Function</th><th data-key="status">Status</th>'
        '<th data-key="stage">Stage</th><th data-key="candidate">Candidates</th>'
        '<th data-key="vectors">Vectors</th><th data-key="unit">Unit/formal</th>'
        '<th data-key="frame">Frame</th><th>Blocker / next action</th></tr></thead>'
        '<tbody></tbody></table></div>'
    )
    body += '<h2>Failure / blocker summary</h2><div id="failure-summary">'
    if overview["failures"]:
        for failure in overview["failures"]:
            body += (
                f'<div class="failure"><b>{html.escape(str(failure.get("function")))}</b> '
                f'{html_status(failure.get("status"))} · {html.escape(str(failure.get("stage")))}<br>'
                f'{html.escape("; ".join(failure.get("blockers") or []) or str(failure.get("next_action")))}</div>'
            )
    else:
        body += '<div class="panel">No selected-run function failure or blocker.</div>'
    if overview["historical_failures"]:
        body += (
            '<details class="panel"><summary>historical failures</summary>'
            + "".join(
                f'<div class="failure"><span class="code">{html.escape(str(value.get("run_id")))}</span> · '
                f'{html.escape(str(value.get("function") or value.get("contract_id")))} '
                f'{html_status(value.get("status"))}<br>'
                f'{html.escape("; ".join(value.get("blockers") or []) or compact_text(value.get("counterexample")))}</div>'
                for value in overview["historical_failures"]
            )
            + "</details>"
        )
    body += "</div>"
    rows = []
    for item in dataset.functions:
        rows.append({
            "function": item["function"]["name"],
            "contract_id": item["contract_id"],
            "status": item["status"],
            "stage": item["stage"]["current"],
            "candidate": item["candidates"]["display"],
            "vectors": item["vectors"]["executed"],
            "unit": item["vectors"].get("verification_status") or "—",
            "frame": item["matrix"]["frame"]["display"],
            "blockers": item["blockers"],
            "next_action": item["next_action"],
            "href": item["links"]["page"],
        })
    script = """
const data=JSON.parse(document.getElementById('page-data').textContent);
const tbody=document.querySelector('#functions tbody');
const filter=document.getElementById('filter');
const statusFilter=document.getElementById('status-filter');
let sortKey='function', descending=false;
function esc(x){return String(x??'').replace(/[&<>\"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','\"':'&quot;',"'":'&#39;'}[c]));}
function pill(x){return '<span class="pill '+esc(x)+'">'+esc(x)+'</span>';}
function render(){
  let rows=data.functions.filter(x=>(!statusFilter.value||x.status===statusFilter.value)&&(!filter.value||JSON.stringify(x).toLowerCase().includes(filter.value.toLowerCase())));
  rows.sort((a,b)=>String(a[sortKey]??'').localeCompare(String(b[sortKey]??''),undefined,{numeric:true})*(descending?-1:1));
  tbody.innerHTML=rows.map(x=>'<tr><td><a href="'+esc(x.href)+'">'+esc(x.function)+'</a><br><span class="small">'+esc(x.contract_id)+'</span></td><td>'+pill(x.status)+'</td><td>'+esc(x.stage)+'</td><td>'+esc(x.candidate)+'</td><td>'+esc(x.vectors)+'</td><td>'+esc(x.unit)+'</td><td>'+esc(x.frame)+'</td><td>'+esc((x.blockers||[]).join('; ')||x.next_action)+'</td></tr>').join('');
}
filter.addEventListener('input',render);
statusFilter.addEventListener('change',render);
document.querySelectorAll('th[data-key]').forEach(th=>th.addEventListener('click',()=>{if(sortKey===th.dataset.key)descending=!descending;else{sortKey=th.dataset.key;descending=false;}render();}));
render();
"""
    return page_shell("DSC regression dashboard", body, {"functions": rows}, script)


def render_history(dataset: Dataset) -> str:
    body = header(
        "Run history",
        "Run-to-run status, coverage, and regression/improvement context",
        [
            ("Overview", "index.html"),
            ("Traceability", "traceability.html"),
            ("Summary report", "../reports/regression-summary.md"),
        ],
    )
    body += (
        '<div class="table-scroll"><table><thead><tr><th>Run</th><th>Profile</th>'
        '<th>Status</th><th>Functions</th><th>Candidates</th><th>Frames</th>'
        '<th>Vectors</th><th>Hashes</th></tr></thead><tbody>'
    )
    for run in dataset.runs:
        body += (
            f'<tr><td class="code">{html.escape(str(run.get("run_id")))}</td>'
            f'<td>{html.escape(str(run.get("profile")))}</td>'
            f'<td>{html_status(run.get("status"))}</td>'
            f'<td>{html.escape(str(run.get("function_count")))}</td>'
            f'<td>{html.escape(str(run.get("candidates", {}).get("display")))}</td>'
            f'<td>{html.escape(str(run.get("frames", {}).get("display")))}</td>'
            f'<td>{html.escape(f"{run.get("vectors", 0):,}")}</td>'
            f'<td class="small">source {html.escape(str(run.get("source_hash")))}<br>'
            f'spec {html.escape(str(run.get("spec_hash")))}</td></tr>'
        )
    body += (
        '</tbody></table></div><h2>Per-function changes in selected view</h2>'
        '<div class="table-scroll"><table><thead><tr><th>Function</th><th>Status</th>'
        '<th>Change</th><th>Last run</th><th>Previous run</th></tr></thead><tbody>'
    )
    for item in dataset.functions:
        history = item.get("history", [])
        previous = history[-2] if len(history) > 1 else {}
        current = history[-1] if history else {}
        body += (
            f'<tr><td><a href="{html.escape(item["links"]["page"])}">'
            f'{html.escape(item["function"]["name"])}</a></td>'
            f'<td>{html_status(item.get("status"))}</td>'
            f'<td>{html.escape(str(item.get("comparison")))}</td>'
            f'<td>{html.escape(str(current.get("run_id")))} · '
            f'{html.escape(str(current.get("candidate_pass_rate")))}</td>'
            f'<td>{html.escape(str(previous.get("run_id", "—")))} · '
            f'{html.escape(str(previous.get("candidate_pass_rate", "—")))}</td></tr>'
        )
    body += "</tbody></table></div>"
    return page_shell("Run history", body)


def render_traceability(dataset: Dataset) -> str:
    body = header(
        "Traceability index",
        "Bidirectional Spec -> C -> Contract -> RTL -> Verification links",
        [("Overview", "index.html"), ("History", "history.html")],
    )
    body += (
        '<h2>Spec -> code / functions</h2><div class="table-scroll"><table><thead>'
        '<tr><th>Spec anchor</th><th>Function</th><th>Section/table</th><th>Status</th>'
        '<th>PDF</th></tr></thead><tbody>'
    )
    for key, values in dataset.traceability.get("spec_to_code", {}).items():
        for value in values:
            pdf = (
                f'<a href="{html.escape(str(value.get("href")))}">open external PDF</a>'
                if value.get("href") else "SPEC_UNAVAILABLE"
            )
            body += (
                f'<tr id="spec-{html.escape(safe_id(key))}"><td class="code">{html.escape(key)}</td>'
                f'<td><a href="{html.escape(value["page"])}">{html.escape(value["function"])}</a></td>'
                f'<td>{html.escape(str(value.get("section") or value.get("table") or value.get("page_number")))}</td>'
                f'<td>{html_status(value.get("status"))}</td><td>{pdf}</td></tr>'
            )
    body += (
        '</tbody></table></div><h2>Code -> spec</h2><div class="table-scroll"><table><thead>'
        '<tr><th>C source</th><th>Function</th><th>Lines</th><th>Fixed commit / local link</th>'
        '</tr></thead><tbody>'
    )
    for key, values in dataset.traceability.get("code_to_spec", {}).items():
        for value in values:
            span = value.get("span") or {}
            href = value.get("href")
            code = (
                f'<a href="{html.escape(str(href))}">open fixed-commit C</a>'
                if href else "unavailable"
            )
            body += (
                f'<tr><td class="code">{html.escape(key)}</td>'
                f'<td><a href="{html.escape(value["page"])}">{html.escape(value["function"])}</a></td>'
                f'<td>{html.escape(str(span.get("start_line")))}-{html.escape(str(span.get("end_line")))}</td>'
                f'<td>{code}</td></tr>'
            )
    body += '</tbody></table></div>'
    return page_shell("Traceability index", body)


def write_site(dataset: Dataset, site_root: Path) -> list[Path]:
    outputs: list[Path] = []
    site_root.mkdir(parents=True, exist_ok=True)
    index_path = site_root / "index.html"
    write_text(index_path, render_index(dataset))
    outputs.append(index_path)
    path = site_root / "history.html"
    write_text(path, render_history(dataset))
    outputs.append(path)
    path = site_root / "traceability.html"
    write_text(path, render_traceability(dataset))
    outputs.append(path)
    for path, value in (
        (site_root / "data" / "overview.json", dataset.overview),
        (site_root / "data" / "runs.json", dataset.runs),
        (site_root / "data" / "traceability.json", dataset.traceability),
    ):
        write_json(path, value)
        outputs.append(path)
    for item in dataset.functions:
        model_path = site_root / "data" / "functions" / f"{safe_id(item['contract_id'])}.json"
        page_path = site_root / "functions" / f"{safe_id(item['contract_id'])}.html"
        write_json(model_path, item)
        write_text(page_path, render_function(item))
        outputs.extend([model_path, page_path])
    manifest_path = site_root / "manifest.json"
    write_json(
        manifest_path,
        {
            "schema_version": 1,
            "pages": ["index.html", "history.html", "traceability.html"],
            "functions": [item["contract_id"] for item in dataset.functions],
            "data": [
                str(path.relative_to(site_root))
                for path in outputs
                if path.suffix == ".json"
            ],
        },
    )
    outputs.append(manifest_path)
    return outputs


def write_reports(dataset: Dataset, repo: Path) -> list[Path]:
    summary_path = repo / "reports" / "regression-summary.md"
    write_text(summary_path, report_summary(dataset))
    outputs = [summary_path]
    for item in dataset.functions:
        path = repo / "reports" / "functions" / f"{safe_id(item['contract_id'])}.md"
        write_text(path, report_function(item))
        outputs.append(path)
    return outputs


def write_indexes(dataset: Dataset, repo: Path) -> list[Path]:
    library_path = repo / "library" / "index.json"
    path_map = repo / "path-map.json"
    layout = repo / "DIRECTORY_LAYOUT.md"
    write_json(library_path, dataset.library_index)
    write_json(path_map, dataset.path_map)
    write_text(layout, dataset.docs)
    return [library_path, path_map, layout]


def build(
    repo: Path,
    storage_arg: str | None,
    requested_run: str,
    *,
    output: Path | None = None,
    mirror_external: bool = True,
) -> tuple[Dataset, list[Path]]:
    resolution = resolve_storage(repo, storage_arg)
    dataset = build_dataset(repo, resolution, requested_run)
    outputs: list[Path] = []
    site_root = (output or (repo / "dashboard")).resolve()
    outputs.extend(write_site(dataset, site_root))
    outputs.extend(write_reports(dataset, repo))
    outputs.extend(write_indexes(dataset, repo))
    external_site = resolution.root / "dashboard"
    if (
        mirror_external
        and resolution.root != repo
        and output is None
        and resolution.root.is_dir()
    ):
        # latest.json belongs to the legacy regression worker and is kept.
        write_site(dataset, external_site)
        outputs.append(external_site / "index.html")
    return dataset, outputs


def relative_files(root: Path) -> list[Path]:
    return [path for path in root.rglob("*") if path.is_file()]


def check_site(repo: Path, output: Path | None = None) -> tuple[bool, list[str]]:
    site = (output or (repo / "dashboard")).resolve()
    errors: list[str] = []
    required = [
        site / "index.html",
        site / "history.html",
        site / "traceability.html",
        site / "manifest.json",
        repo / "reports" / "regression-summary.md",
        repo / "library" / "index.json",
        repo / "path-map.json",
        repo / "DIRECTORY_LAYOUT.md",
    ]
    for path in required:
        if not path.is_file():
            errors.append(f"missing output: {path}")
    manifest = read_json(site / "manifest.json", {}) or {}
    function_ids = manifest.get("functions", []) if isinstance(manifest.get("functions"), list) else []
    for cid in function_ids:
        if not (site / "functions" / f"{safe_id(cid)}.html").is_file():
            errors.append(f"missing function page: {cid}")
        if not (site / "data" / "functions" / f"{safe_id(cid)}.json").is_file():
            errors.append(f"missing function view model: {cid}")
        if not (repo / "reports" / "functions" / f"{safe_id(cid)}.md").is_file():
            errors.append(f"missing function report: {cid}")
    if site.is_dir():
        for path in relative_files(site):
            if path.suffix != ".html":
                continue
            text = path.read_text(encoding="utf-8", errors="replace")
            for href in re.findall(r"""href=["']([^"']+)["']""", text):
                if not href or href.startswith(("#", "http:", "https:", "file:", "mailto:")):
                    continue
                target = (path.parent / urllib.parse.unquote(href.split("#", 1)[0])).resolve()
                if not target.is_file():
                    errors.append(f"broken internal link: {path.relative_to(site)} -> {href}")
    for cid in function_ids:
        model = read_json(site / "data" / "functions" / f"{safe_id(cid)}.json", {}) or {}
        if model.get("status") not in VALID_STATUSES:
            errors.append(f"invalid function status: {cid}: {model.get('status')}")
        for key in ("candidates", "vectors", "matrix"):
            if key not in model:
                errors.append(f"missing normalized field {key}: {cid}")
    path_map = read_json(repo / "path-map.json", {}) or {}
    for entry in path_map.get("entries", []) if isinstance(path_map.get("entries"), list) else []:
        legacy = repo / str(entry.get("legacy_path", ""))
        if entry.get("legacy_exists") and not legacy.exists():
            errors.append(f"legacy path disappeared: {entry.get('legacy_path')}")
    return not errors, errors


def serve(site: Path, host: str, port: int) -> int:
    site = site.resolve()
    if not (site / "index.html").is_file():
        print(f"dashboard is not built: {site}", file=sys.stderr)
        return 2
    os.chdir(site)
    handler = http.server.SimpleHTTPRequestHandler
    with socketserver.ThreadingTCPServer((host, port), handler) as server:
        print(f"Serving dashboard at http://{host}:{port}/ from {site}")
        try:
            server.serve_forever()
        except KeyboardInterrupt:
            return 0
    return 0


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Build a human-readable DSC regression dashboard from receipts"
    )
    parser.add_argument(
        "--repo", type=Path, default=REPO_ROOT,
        help="repository containing contracts/library (default: checkout root)",
    )
    sub = parser.add_subparsers(dest="command", required=True)
    build_parser = sub.add_parser("build")
    build_parser.add_argument("--run", default="latest", help="run id or latest")
    build_parser.add_argument("--root", type=Path, default=None)
    build_parser.add_argument("--output", type=Path, default=None)
    check_parser = sub.add_parser("check")
    check_parser.add_argument("--output", type=Path, default=None)
    serve_parser = sub.add_parser("serve")
    serve_parser.add_argument("--output", type=Path, default=None)
    serve_parser.add_argument("--host", default="127.0.0.1")
    serve_parser.add_argument("--port", type=int, default=8000)
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    repo = args.repo.resolve()
    if args.command == "build":
        dataset, outputs = build(
            repo,
            str(args.root) if args.root else None,
            args.run,
            output=args.output,
        )
        print(json.dumps({
            "status": "PASS",
            "run_id": dataset.selected_run_id,
            "storage": dataset.resolution.as_dict(),
            "functions": len(dataset.functions),
            "outputs": [str(path) for path in outputs],
        }, indent=2, sort_keys=True))
        return 0
    if args.command == "check":
        ok, errors = check_site(repo, args.output)
        print(json.dumps({
            "status": "PASS" if ok else "FAIL",
            "errors": errors,
        }, indent=2, sort_keys=True))
        return 0 if ok else 2
    if args.command == "serve":
        return serve(args.output or (repo / "dashboard"), args.host, args.port)
    return 2


def render_function(item: dict[str, Any]) -> str:
    links = [
        ("Overview", "../index.html"),
        ("History", "../history.html"),
        ("Traceability", "../traceability.html"),
        ("Markdown report", f"../../reports/functions/{safe_id(item['contract_id'])}.md"),
    ]
    body = header(
        item["function"]["name"],
        f"contract {item['contract_id']} · run {item.get('run_id')} · comparison {item.get('comparison')}",
        links,
    )
    body += (
        '<div class="panel"><div class="statline"><span>Status</span>'
        + html_status(item.get("status"))
        + f'</div><div class="statline"><span>Current stage</span><b>{html.escape(str(item["stage"]["current"]))}</b></div>'
        f'<div class="statline"><span>Next action</span><b>{html.escape(str(item["next_action"]))}</b></div></div>'
    )
    if item.get("blockers"):
        body += (
            '<div class="failure"><b>Blockers</b><ul>'
            + "".join(f"<li>{html.escape(str(value))}</li>" for value in item["blockers"])
            + "</ul></div>"
        )

    body += (
        '<h2>1. Stage checklist</h2><div class="table-scroll"><table><thead><tr>'
        "<th>Stage</th><th>Status</th><th>Raw</th><th>Detail</th></tr></thead><tbody>"
        + "".join(
            f'<tr><td>{html.escape(str(value["label"]))}</td>'
            f'<td>{html_status(value.get("status"))}</td>'
            f'<td class="code">{html.escape(str(value.get("raw_status")))}</td>'
            f'<td>{html.escape(str(value.get("detail")))}</td></tr>'
            for value in item["stage"]["checklist"]
        )
        + "</tbody></table></div>"
    )
    body += (
        '<h2>2. Interface</h2><div class="table-scroll"><table><thead><tr>'
        "<th>Direction</th><th>Port</th><th>Width</th><th>Signedness</th>"
        "<th>Domain</th><th>Role</th></tr></thead><tbody>"
    )
    for port in item["traceability"]["ports"]:
        domain = port.get("domain", {})
        domain_text = compact_text({
            "kind": domain.get("kind"),
            "range": domain.get("range"),
            "values": domain.get("values"),
            "basis": domain.get("basis"),
        }, 240)
        body += (
            f'<tr><td>{html.escape(str(port.get("direction")))}</td>'
            f'<td class="code">{html.escape(str(port.get("name")))}</td>'
            f'<td>{html.escape(str(port.get("width")))}</td>'
            f'<td>{html.escape(str(port.get("signed")))}</td>'
            f'<td>{html.escape(domain_text)}</td>'
            f'<td>{html.escape(str(port.get("role")))}</td></tr>'
        )
    body += "</tbody></table></div>"
    body += (
        '<h2>3. Width derivation</h2><div class="table-scroll"><table><thead><tr>'
        "<th>Port</th><th>Width</th><th>Formula / basis</th><th>Authority</th>"
        "<th>Review</th></tr></thead><tbody>"
        + "".join(
            f'<tr><td class="code">{html.escape(str(port.get("name")))}</td>'
            f'<td>{html.escape(str(port.get("width")))}</td>'
            f'<td>{html.escape(str(port.get("width_derivation", {}).get("formula")))}</td>'
            f'<td>{html.escape(str(port.get("width_derivation", {}).get("authority")))}</td>'
            f'<td>{html.escape(str(port.get("width_derivation", {}).get("review_status")))}</td></tr>'
            for port in item["traceability"]["ports"]
        )
        + "</tbody></table></div>"
    )
    body += '<h2>4. Spec -> C -> Contract -> RTL -> Verification -> Frame</h2><div class="chain">'
    for link in item["traceability"]["chain"]:
        href = link.get("href")
        label = (
            f'<a href="{html.escape(str(href))}">{html.escape(str(link["status"]))}</a>'
            if href else html_status(link.get("status"))
        )
        body += f'<div><b>{html.escape(str(link["label"]))}</b>{label}</div>'
    body += "</div>"
    spec = item["traceability"]["spec"]
    if spec["status"] != "AVAILABLE":
        body += (
            '<div class="failure"><b>SPEC_UNAVAILABLE</b>: '
            + html.escape(str(spec.get("reason")))
            + "</div>"
        )

    body += (
        '<h2>5. Candidates, mutations, and counterexamples</h2>'
        '<div class="panel">'
        + bar("Candidates passed", item["candidates"].get("passed"), item["candidates"].get("total"))
        + bar("Vector shards", item["vectors"]["shards"].get("passed"), item["vectors"]["shards"].get("total"), "green")
        + f'<p>Vectors executed: <b>{html.escape(str(item["vectors"].get("executed")))}</b>; '
        f'verification: <b>{html.escape(str(item["vectors"].get("verification_status")))}</b>; '
        f'mutation evidence: <b>{html.escape(str(item["mutations"]["result"]["display"]))}</b> '
        f'({html.escape(str(item["mutations"]["result"].get("basis")))}).</p>'
        "</div>"
        '<div class="table-scroll"><table><thead><tr><th>Candidate</th><th>Accepted</th>'
        "<th>Compile</th><th>Validation</th><th>Verification</th>"
        "<th>Smallest counterexample</th></tr></thead><tbody>"
    )
    for candidate in item["candidates"]["items"]:
        body += (
            f'<tr><td class="code">{html.escape(str(candidate.get("candidate")))}</td>'
            f'<td>{html.escape(str(candidate.get("accepted")))}</td>'
            f'<td>{html_status(candidate.get("compile_status"))}</td>'
            f'<td>{html_status(candidate.get("validation"))}</td>'
            f'<td>{html.escape(str(candidate.get("verification_status")))}</td>'
            f'<td class="code">{html.escape(compact_text(candidate.get("smallest_counterexample")) or "none")}</td></tr>'
        )
    body += "</tbody></table></div>"
    if item["mutations"].get("counterexamples"):
        body += (
            '<h3>Smallest counterexamples</h3><div class="table-scroll"><table><thead>'
            "<tr><th>Stage</th><th>Candidate</th><th>Expected</th><th>Actual</th>"
            "<th>Inputs</th></tr></thead><tbody>"
            + "".join(
                f'<tr><td>{html.escape(str(ce.get("stage")))}</td>'
                f'<td>{html.escape(str(ce.get("candidate")))}</td>'
                f'<td>{html.escape(str(ce.get("expected")))}</td>'
                f'<td>{html.escape(str(ce.get("actual")))}</td>'
                f'<td class="code">{html.escape(str(ce.get("inputs")))}</td></tr>'
                for ce in item["mutations"]["counterexamples"]
            )
            + "</tbody></table></div>"
        )

    body += (
        '<h2 id="frame-matrix">6. Frame / bitstream matrix</h2>'
        '<div class="table-scroll"><table><thead><tr><th>Mode</th>'
        "<th>Status</th><th>Result</th></tr></thead><tbody>"
        + "".join(
            f'<tr><td>{html.escape(str(mode))}</td>'
            f'<td>{html_status(value.get("status"))}</td>'
            f'<td>{html.escape(str(value.get("display")))}</td></tr>'
            for mode, value in item["matrix"]["modes"].items()
        )
        + "</tbody></table></div>"
    )
    body += (
        '<h2>7. Promotion / model / strategy history</h2><div class="panel">'
        "<p>Promotion: "
        + html_status(item["promotion"].get("status"))
        + f' · immutable={html.escape(str(item["promotion"].get("immutable")))}'
        f' · stale={html.escape(str(item["promotion"].get("stale")))}</p>'
        f'<p>Model tier: <b>{html.escape(str(item["model"].get("tier")))}</b> · '
        f'calls {html.escape(str(item["model"].get("calls")))} · '
        f'tokens {html.escape(str(item["model"].get("tokens")))}</p>'
        f'<p>Hashes: source <span class="code">{html.escape(str(item["hashes"].get("source")))}</span>, '
        f'spec <span class="code">{html.escape(str(item["hashes"].get("spec")))}</span>, '
        f'contract <span class="code">{html.escape(str(item["hashes"].get("contract")))}</span>, '
        f'RTL <span class="code">{html.escape(str(item["hashes"].get("rtl")))}</span>.</p>'
        "</div>"
        '<div class="table-scroll"><table><thead><tr><th>Run</th><th>Decision</th>'
        "<th>Tier</th><th>Rationale</th></tr></thead><tbody>"
        + "".join(
            f'<tr><td class="code">{html.escape(str(value.get("run_id")))}</td>'
            f'<td>{html.escape(str(value.get("decision")))}</td>'
            f'<td>{html.escape(str(value.get("model_tier")))}</td>'
            f'<td>{html.escape(str(value.get("rationale")))}</td></tr>'
            for value in item["strategy_history"]
        )
        + "</tbody></table></div>"
    )
    body += (
        '<h2>8. Recommended next action</h2><div class="panel"><b>'
        + html.escape(str(item["next_action"]))
        + "</b></div>"
    )
    return page_shell(item["function"]["name"], body, item)


def report_summary(dataset: Dataset) -> str:
    overview = dataset.overview
    selected = overview["selected_run"]
    lines = [
        "# Regression summary", "",
        f"Selected run: {md_escape(selected.get('run_id'))} ({md_escape(selected.get('status'))})",
        f"Storage: {md_escape(dataset.resolution.root)} ({md_escape(dataset.resolution.mode)})",
        f"SMB fallback: {md_escape(dataset.resolution.fallback_reason or 'none')}",
        "", "## Overview", "",
        "| Measure | Result |", "|---|---:|",
        f"| Functions passing | {overview['progress']['functions']['display']} |",
        f"| Candidate equivalence | {overview['progress']['candidates']['display']} |",
        f"| Frame sanity | {overview['progress']['frames']['display']} |",
        f"| Vectors executed | {overview['progress']['vectors']} |",
        f"| Runs indexed | {overview['run_count']} |",
        "", "## Source gate", "",
    ]
    source = overview["source"]
    lines += [
        f"- PDF: {source['spec_status']}; {md_escape((source.get('pdf') or {}).get('path'))}",
        f"- Source/build gate: {md_escape((source.get('source_gate') or {}).get('status'))}",
        "- PDF and C source remain external/immutable inputs.", "",
        "## Function results", "",
        "| Function | Status | Stage | Candidates | Vectors | Unit/formal | Frame | Next action |",
        "|---|---|---|---|---:|---|---|---|",
    ]
    for item in dataset.functions:
        lines.append(
            f"| [{item['function']['name']} ({item['contract_id']})](functions/{safe_id(item['contract_id'])}.md) | {item['status']} | "
            f"{md_escape(item['stage']['current'])} | {item['candidates']['display']} | "
            f"{item['vectors']['executed']} | {md_escape(item['vectors'].get('verification_status'))} | "
            f"{item['matrix']['frame']['display']} | {md_escape(item['next_action'])} |"
        )
    lines += ["", "## Failure and blocker summary", ""]
    if overview["failures"]:
        lines += [
            "### Selected run", "",
            "| Function | Status | Failed stage | Cause / next action |",
            "|---|---|---|---|",
        ]
        for item in overview["failures"]:
            cause = "; ".join(item.get("blockers") or []) or item.get("next_action")
            lines.append(
                f"| {md_escape(item.get('function'))} | {item.get('status')} | "
                f"{md_escape(item.get('stage'))} | {md_escape(cause)} |"
            )
    else:
        lines.append("The selected run has no function-level failure or blocker.")
    if overview["historical_failures"]:
        lines += [
            "", "### Historical failures", "",
            "| Run | Function | Status | Cause / counterexample |",
            "|---|---|---|---|",
        ]
        for item in overview["historical_failures"]:
            cause = "; ".join(item.get("blockers") or []) or compact_text(item.get("counterexample"))
            lines.append(
                f"| {md_escape(item.get('run_id'))} | "
                f"{md_escape(item.get('function') or item.get('contract_id'))} | "
                f"{item.get('status')} | {md_escape(cause)} |"
            )
    lines += [
        "", "## Run history", "",
        "| Run | Profile | Status | Functions | Candidates | Frames | Vectors |",
        "|---|---|---|---:|---|---|---:|",
    ]
    for run in dataset.runs:
        lines.append(
            f"| {md_escape(run.get('run_id'))} | {md_escape(run.get('profile'))} | "
            f"{run.get('status')} | {md_escape(run.get('function_count'))} | "
            f"{md_escape(run.get('candidates', {}).get('display'))} | "
            f"{md_escape(run.get('frames', {}).get('display'))} | {md_escape(run.get('vectors'))} |"
        )
    lines += [
        "", "## How to open", "",
        "- Open dashboard/index.html for the static overview.",
        "- Use dashboard/functions/<contract-id>.html for full traceability.",
        "- Use path-map.json and library/index.json to resolve legacy paths and stale accepted artifacts.",
        "",
    ]
    return "\n".join(lines)
if __name__ == "__main__":
    raise SystemExit(main())
