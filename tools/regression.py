#!/usr/bin/env python3
"""Durable SMB-backed per-function regression service.

The service intentionally keeps orchestration state outside the git checkout.
Queue items are directories claimed with mkdir/rename, JSON is written with
temp-file+rename, and all large flow work is kept below the configured SMB
root. Function selection comes from the existing facts/contracts/cache; this
module has no function-name allowlist.
"""

from __future__ import annotations

import argparse
import calendar
import concurrent.futures
import dataclasses
import hashlib
import json
import os
import platform
import re
import shutil
import socket
import subprocess
import sys
import tempfile
import threading
import time
import uuid
from pathlib import Path
from typing import Any, Iterable


REPO_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_ROOT = Path("/Volumes/homes/dsc12a-regression")
EXPECTED_SHARE = "//kslin@192.168.68.52/homes"
MIN_FREE_BYTES = 1 << 30
HEARTBEAT_SECONDS = 5
STALE_SECONDS = 15 * 60
QUEUE_STATES = ("pending", "running", "done", "failed")
STAGES = (
    "width_spec_gate",
    "generator_cache",
    "verilator_lint_build",
    "shards_mutations",
    "dependency_composition",
    "model_matrix",
    "frame_compare",
)
ATOMIC_WRITE_LOCK = threading.RLock()


class InfrastructureFailure(RuntimeError):
    """An environment or durable-state failure that must not invoke a model."""


def utc_now() -> str:
    return time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())


def epoch_now() -> float:
    return time.time()


def safe_id(value: str) -> str:
    value = re.sub(r"[^A-Za-z0-9_.-]+", "-", str(value)).strip("-.")
    return value or "item"


def digest(value: Any) -> str:
    payload = json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False)
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


def file_hash(path: Path) -> str | None:
    if not path.is_file():
        return None
    hasher = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            hasher.update(chunk)
    return hasher.hexdigest()


def read_json(path: Path, default: Any = None) -> Any:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (FileNotFoundError, OSError, json.JSONDecodeError):
        return default


def atomic_write_bytes(path: Path, payload: bytes) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with ATOMIC_WRITE_LOCK:
        fd, temporary = tempfile.mkstemp(
            prefix=f".{path.name}.", suffix=".tmp", dir=str(path.parent)
        )
        try:
            with os.fdopen(fd, "wb") as stream:
                stream.write(payload)
                stream.flush()
                os.fsync(stream.fileno())
            for attempt in range(8):
                try:
                    os.replace(temporary, path)
                    break
                except FileExistsError:
                    # Some SMB configurations reject replace-over-existing-file
                    # even though the POSIX API requests it.  Remove only this
                    # exact output path, then retry the rename of the complete
                    # temp file; the in-process lock prevents local writers
                    # from interleaving this fallback.
                    try:
                        os.unlink(path)
                    except FileNotFoundError:
                        pass
                    if attempt == 7:
                        raise
                    time.sleep(0.05 * (attempt + 1))
            try:
                directory_fd = os.open(path.parent, os.O_RDONLY)
                try:
                    os.fsync(directory_fd)
                finally:
                    os.close(directory_fd)
            except OSError:
                pass
        finally:
            try:
                os.unlink(temporary)
            except FileNotFoundError:
                pass


def atomic_write_json(path: Path, value: Any) -> None:
    atomic_write_bytes(
        path,
        (json.dumps(value, indent=2, sort_keys=True, ensure_ascii=False) + "\n").encode("utf-8"),
    )


def append_jsonl(path: Path, value: Any) -> None:
    """Append one durable JSONL record using the same-directory replace rule."""
    with ATOMIC_WRITE_LOCK:
        try:
            previous = path.read_bytes()
        except FileNotFoundError:
            previous = b""
        line = (json.dumps(redact(value), sort_keys=True, ensure_ascii=False) + "\n").encode(
            "utf-8"
        )
        atomic_write_bytes(path, previous + line)


def redact_mount_source(value: str) -> str:
    return re.sub(r"//[^/\s]+@", "//<user>@", value)


def redact(value: Any) -> Any:
    if isinstance(value, str):
        return redact_mount_source(value)
    if isinstance(value, list):
        return [redact(item) for item in value]
    if isinstance(value, dict):
        return {key: redact(item) for key, item in value.items()}
    return value


@dataclasses.dataclass(frozen=True)
class ShareMount:
    source: str
    mountpoint: Path
    total_bytes: int
    free_bytes: int


def command_output(command: list[str]) -> tuple[int, str]:
    try:
        result = subprocess.run(
            command,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            encoding="utf-8",
            errors="replace",
            check=False,
            timeout=20,
        )
    except (OSError, subprocess.TimeoutExpired) as error:
        raise InfrastructureFailure(f"cannot inspect SMB mount: {error}") from error
    return result.returncode, result.stdout or ""


def is_expected_share(source: str) -> bool:
    normalized = source.rstrip("/").lower()
    expected = EXPECTED_SHARE.rstrip("/").lower()
    return normalized == expected or (
        "192.168.68.52" in normalized and normalized.endswith("/homes")
    )


def discover_share_mounts() -> list[ShareMount]:
    mount_code, mount_text = command_output(["mount"])
    df_code, df_text = command_output(["df", "-Pk"])
    if mount_code != 0 or df_code != 0:
        raise InfrastructureFailure("mount/df did not complete successfully")
    mountpoints: dict[str, str] = {}
    for line in mount_text.splitlines():
        if " on " not in line:
            continue
        source, remainder = line.split(" on ", 1)
        mountpoint = remainder.split(" (", 1)[0].strip()
        if is_expected_share(source):
            mountpoints[mountpoint] = source
    rows: dict[str, tuple[str, int, int]] = {}
    for line in df_text.splitlines()[1:]:
        fields = line.split()
        if len(fields) < 6:
            continue
        source = fields[0]
        mountpoint = fields[-1]
        try:
            total = int(fields[1]) * 1024
            free = int(fields[3]) * 1024
        except ValueError:
            continue
        rows[mountpoint] = (source, total, free)
    result: list[ShareMount] = []
    for mountpoint, source in mountpoints.items():
        df_source, total, free = rows.get(mountpoint, (source, 0, 0))
        result.append(ShareMount(source, Path(mountpoint), total, free))
    return sorted(result, key=lambda item: str(item.mountpoint))


def path_is_under(path: Path, parent: Path) -> bool:
    try:
        path.resolve().relative_to(parent.resolve())
        return True
    except ValueError:
        return False


def validate_regression_root(root: Path | None = None, *, test_mode: bool = False) -> tuple[Path, ShareMount | None]:
    configured = root or Path(os.environ.get("DSC_REGRESSION_ROOT", str(DEFAULT_ROOT))).expanduser()
    if not configured.is_absolute():
        raise InfrastructureFailure("DSC_REGRESSION_ROOT must be an absolute path")
    if test_mode:
        configured.mkdir(parents=True, exist_ok=True)
        return configured, None
    mounts = discover_share_mounts()
    matching = [mount for mount in mounts if path_is_under(configured, mount.mountpoint)]
    if not matching:
        discovered = ", ".join(str(item.mountpoint) for item in mounts) or "none"
        raise InfrastructureFailure(
            f"configured regression root {configured} is not under the requested SMB share; "
            f"discovered share mountpoints: {discovered}"
        )
    mount = matching[0]
    if mount.free_bytes and mount.free_bytes < int(os.environ.get("DSC_REGRESSION_MIN_FREE_BYTES", MIN_FREE_BYTES)):
        raise InfrastructureFailure(f"SMB mount has too little free space: {mount.free_bytes} bytes")
    try:
        configured.mkdir(parents=True, exist_ok=True)
        probe = configured / f".write-probe-{uuid.uuid4().hex}"
        with probe.open("x", encoding="utf-8") as stream:
            stream.write("dsc-regression\n")
            stream.flush()
            os.fsync(stream.fileno())
        probe.unlink()
    except OSError as error:
        raise InfrastructureFailure(f"SMB regression root is not writable: {configured}: {error}") from error
    stat = os.statvfs(configured)
    free = int(stat.f_bavail * stat.f_frsize)
    total = int(stat.f_blocks * stat.f_frsize)
    if free < int(os.environ.get("DSC_REGRESSION_MIN_FREE_BYTES", MIN_FREE_BYTES)):
        raise InfrastructureFailure(f"SMB regression root has too little free space: {free} bytes")
    return configured, ShareMount(mount.source, mount.mountpoint, total, free)


class DurableStore:
    def __init__(self, root: Path, *, validate: bool = True):
        self.root, self.mount = validate_regression_root(root, test_mode=not validate)
        self.queue = self.root / "queue"
        self.runs = self.root / "runs"
        self.cache = self.root / "cache"
        self.dashboard = self.root / "dashboard"
        self.locks = self.root / "locks"

    def ensure_layout(self) -> None:
        for state in QUEUE_STATES:
            (self.queue / state).mkdir(parents=True, exist_ok=True)
        for path in (self.runs, self.cache, self.dashboard, self.locks):
            path.mkdir(parents=True, exist_ok=True)
        metadata = {
            "schema_version": 1,
            "root": str(self.root),
            "share": redact_mount_source(self.mount.source) if self.mount else "TEST_ROOT",
            "mountpoint": str(self.mount.mountpoint) if self.mount else None,
            "host": socket.gethostname(),
            "updated_at": utc_now(),
        }
        atomic_write_json(self.root / "metadata.json", metadata)

    def record_strategy(self, run_id: str | None, value: dict[str, Any]) -> None:
        if not run_id:
            return
        run_dir = self.run_dir(str(run_id))
        if run_dir.is_dir():
            append_jsonl(run_dir / "strategy.jsonl", {"at": utc_now(), **value})

    def run_dir(self, run_id: str) -> Path:
        return self.runs / safe_id(run_id)

    def job_dir(self, state: str, job_id: str) -> Path:
        return self.queue / state / safe_id(job_id)

    def write_status(self, directory: Path, **changes: Any) -> dict[str, Any]:
        path = directory / "status.json"
        status = read_json(path, {}) or {}
        status.update(changes)
        status["updated_at"] = utc_now()
        status["elapsed_seconds"] = max(0.0, epoch_now() - float(status.get("started_epoch", epoch_now())))
        atomic_write_json(path, redact(status))
        return status

    def write_heartbeat(self, directory: Path, **changes: Any) -> dict[str, Any]:
        status = read_json(directory / "status.json", {}) or {}
        heartbeat = {
            "schema_version": 1,
            "job_id": status.get("job_id"),
            "run_id": status.get("run_id"),
            "host": socket.gethostname(),
            "pid": os.getpid(),
            "stage": status.get("stage"),
            "progress": status.get("progress", {}),
            "elapsed_seconds": status.get("elapsed_seconds", 0),
            "last_error": status.get("last_error"),
            "updated_at": utc_now(),
        }
        heartbeat.update(changes)
        atomic_write_json(directory / "heartbeat.json", redact(heartbeat))
        return heartbeat

    def enqueue(self, job: dict[str, Any]) -> Path:
        job_id = safe_id(str(job["job_id"]))
        target = self.job_dir("pending", job_id)
        if target.exists():
            raise InfrastructureFailure(f"queue job already exists: {job_id}")
        temporary = self.queue / "pending" / f".{job_id}.{uuid.uuid4().hex}.tmp"
        temporary.mkdir(parents=True)
        payload = dict(job)
        payload.setdefault("schema_version", 1)
        payload.setdefault("created_at", utc_now())
        payload.setdefault("attempt", 0)
        atomic_write_json(temporary / "job.json", redact(payload))
        atomic_write_json(
            temporary / "status.json",
            {
                "schema_version": 1,
                "job_id": job_id,
                "run_id": payload.get("run_id"),
                "contract_id": payload.get("contract_id"),
                "function": payload.get("function"),
                "status": "queued",
                "stage": "queued",
                "progress": {"completed": 0, "total": len(STAGES), "unit": "stages"},
                "started_epoch": 0,
                "elapsed_seconds": 0,
                "last_error": None,
                "created_at": payload.get("created_at"),
                "updated_at": utc_now(),
            },
        )
        os.replace(temporary, target)
        return target

    def claim_one(self) -> Path | None:
        pending = self.queue / "pending"
        for candidate in sorted(pending.iterdir() if pending.exists() else []):
            if not candidate.is_dir() or candidate.name.startswith("."):
                continue
            claim = candidate / ".claim"
            try:
                claim.mkdir()
                atomic_write_json(
                    claim / "owner.json",
                    {"host": socket.gethostname(), "pid": os.getpid(), "claimed_at": utc_now()},
                )
            except FileExistsError:
                continue
            running = self.job_dir("running", candidate.name)
            try:
                os.replace(candidate, running)
                self.write_status(running, status="running", started_epoch=epoch_now(), stage="claimed")
                self.write_heartbeat(running)
                return running
            except OSError:
                try:
                    shutil.rmtree(claim)
                except OSError:
                    pass
                raise
        return None

    def finish(self, running: Path, state: str, **changes: Any) -> Path:
        if state not in ("done", "failed"):
            raise ValueError(state)
        status = self.write_status(running, status=state, **changes)
        claim = running / ".claim"
        if claim.exists():
            shutil.rmtree(claim)
        destination = self.job_dir(state, running.name)
        if destination.exists():
            destination = self.job_dir(state, f"{running.name}-{uuid.uuid4().hex[:8]}")
        os.replace(running, destination)
        return destination

    def list_jobs(self) -> list[dict[str, Any]]:
        jobs: list[dict[str, Any]] = []
        for state in QUEUE_STATES:
            directory = self.queue / state
            for item in sorted(directory.iterdir() if directory.exists() else []):
                if item.is_dir() and not item.name.startswith("."):
                    status = read_json(item / "status.json", {}) or {}
                    status["queue_state"] = state
                    status["path"] = str(item)
                    jobs.append(status)
        return jobs

    def recover_stale(self, stale_seconds: int = STALE_SECONDS) -> list[dict[str, Any]]:
        recovered: list[dict[str, Any]] = []
        now = epoch_now()
        running_root = self.queue / "running"
        for running in sorted(running_root.iterdir() if running_root.exists() else []):
            if not running.is_dir() or running.name.startswith("."):
                continue
            heartbeat = read_json(running / "heartbeat.json", {}) or {}
            timestamp = heartbeat.get("updated_at") or (running / "heartbeat.json").stat().st_mtime
            try:
                if isinstance(timestamp, str):
                    parsed = calendar.timegm(time.strptime(timestamp, "%Y-%m-%dT%H:%M:%SZ"))
                else:
                    parsed = float(timestamp)
            except (ValueError, OSError):
                parsed = 0
            if now - parsed <= stale_seconds:
                continue
            recovery_lock = running / ".recovery"
            try:
                recovery_lock.mkdir()
            except FileExistsError:
                continue
            job = read_json(running / "job.json", {}) or {}
            attempt = int(job.get("attempt", 0)) + 1
            job["attempt"] = attempt
            job["last_error"] = f"stale heartbeat recovered after {int(now - parsed)} seconds"
            atomic_write_json(running / "job.json", redact(job))
            self.write_status(
                running,
                status="queued",
                stage="recovered_stale",
                last_error=job["last_error"],
                progress={"completed": 0, "total": len(STAGES), "unit": "stages"},
            )
            claim = running / ".claim"
            if claim.exists():
                shutil.rmtree(claim)
            try:
                recovery_lock.rmdir()
            except OSError:
                pass
            self.record_strategy(
                str(job.get("run_id")),
                {
                    "event": "stale_recovery",
                    "decision": "requeue",
                    "job_id": job.get("job_id", running.name),
                    "attempt": attempt,
                    "rationale": job["last_error"],
                },
            )
            destination = self.job_dir("pending", running.name)
            if destination.exists():
                destination = self.job_dir("pending", f"{running.name}-retry-{attempt}")
            os.replace(running, destination)
            recovered.append({"job_id": job.get("job_id", running.name), "attempt": attempt, "reason": job["last_error"]})
        return recovered


class Heartbeat:
    def __init__(self, store: DurableStore, directory: Path, interval: int = HEARTBEAT_SECONDS):
        self.store = store
        self.directory = directory
        self.interval = max(1, interval)
        self.stop_event = threading.Event()
        self.thread: threading.Thread | None = None

    def start(self) -> None:
        self.thread = threading.Thread(target=self._run, name=f"heartbeat-{self.directory.name}", daemon=True)
        self.thread.start()

    def _run(self) -> None:
        while not self.stop_event.wait(self.interval):
            try:
                self.store.write_heartbeat(self.directory)
            except OSError:
                return

    def stop(self) -> None:
        self.stop_event.set()
        if self.thread:
            self.thread.join(timeout=self.interval + 1)


class LocalContext:
    def __init__(self, repo: Path = REPO_ROOT):
        self.repo = repo
        self.manifest = read_json(repo / "spec" / "manifest.json", {}) or {}
        self.plan = read_json(repo / "ci" / "plan.json", {}) or {}
        self.state = read_json(repo / "ci" / "state.json", {}) or {}
        self.cache_index = read_json(repo / "ci" / "cache-index.json", {}) or {}
        self.contracts: dict[str, dict[str, Any]] = {}
        for path in sorted((repo / "contracts" / "locked").glob("*.json")):
            payload = read_json(path, {}) or {}
            if payload.get("contract_id"):
                self.contracts[str(payload["contract_id"])] = payload
        for path in sorted((repo / "ci" / "discovered-contracts").glob("*.json")):
            payload = read_json(path, {}) or {}
            if payload.get("contract_id"):
                self.contracts[str(payload["contract_id"])] = payload
        for item in self.plan.get("contracts", []):
            cid = str(item.get("contract_id", ""))
            if cid and cid not in self.contracts:
                self.contracts[cid] = {"contract_id": cid, "function": {"name": item.get("function")}}

    def plan_item(self, contract_id: str) -> dict[str, Any]:
        return next((item for item in self.plan.get("contracts", []) if item.get("contract_id") == contract_id), {})

    def state_item(self, contract_id: str) -> dict[str, Any]:
        return next((item for item in self.state.get("contracts", []) if item.get("contract_id") == contract_id), {})

    def cache_entries(self, contract_id: str | None = None) -> list[dict[str, Any]]:
        values = self.cache_index.get("entries", {})
        if isinstance(values, dict):
            entries = list(values.values())
        else:
            entries = list(values or [])
        return [
            item for item in entries
            if contract_id is None or item.get("contract_id") == contract_id
        ]

    def artifact_dir(self, contract_id: str, base: Path | None = None) -> Path | None:
        base = base or self.repo
        state = self.state_item(contract_id)
        for raw in state.get("artifacts", []):
            path = base / raw if not Path(raw).is_absolute() else Path(raw)
            if path.is_dir():
                return path
        entries = [item for item in self.cache_entries(contract_id) if item.get("valid")]
        entries.sort(key=lambda item: str(item.get("updated_at", "")), reverse=True)
        for item in entries:
            raw = Path(str(item.get("artifact_dir", "")))
            path = base / raw if not raw.is_absolute() else raw
            if path.is_dir():
                return path
        return None

    def contract_hash(self, contract_id: str) -> str:
        return digest(self.contracts.get(contract_id, {"contract_id": contract_id}))

    def exact_links(self, contract: dict[str, Any]) -> list[dict[str, Any]]:
        return [link for link in contract.get("spec_links", []) if link.get("status") == "EXACT"]

    def port_records(self, contract: dict[str, Any]) -> list[dict[str, Any]]:
        interface = contract.get("interface", {}) or {}
        ports = list(interface.get("ports", []))
        if not ports:
            for item in interface.get("inputs", []):
                ports.append({
                    "name": item.get("name"),
                    "role": item.get("name"),
                    "direction": "input",
                    "width": item.get("logical_width"),
                    "signed": item.get("signed"),
                    "legal_domain": item.get("legal_domain"),
                })
            output = interface.get("output", {}) or {}
            ports.append({
                "name": output.get("name", "return_value"),
                "role": "return_value",
                "direction": "output",
                "width": output.get("logical_width"),
                "signed": output.get("signed"),
                "legal_range": output.get("legal_range"),
            })
        else:
            input_by_name = {str(item.get("name")): item for item in interface.get("inputs", [])}
            output = interface.get("output", {}) or {}
            enriched: list[dict[str, Any]] = []
            for port in ports:
                candidate = dict(port)
                name = str(candidate.get("name"))
                source = output if candidate.get("direction") == "output" else input_by_name.get(name, {})
                for key in ("legal_domain", "legal_range", "logical_width", "signed", "role"):
                    if candidate.get(key) is None and source.get(key) is not None:
                        candidate[key] = source.get(key)
                enriched.append(candidate)
            ports = enriched
        links = self.exact_links(contract)
        exact_page = sorted({link.get("page") for link in links if link.get("page") is not None})
        exact_sections = sorted({link.get("section") for link in links if link.get("section")})
        exact_tables = sorted({link.get("table") for link in links if link.get("table")})
        function = contract.get("function", {}) or {}
        function_span = function.get("source_span", {})
        records = []
        for port in ports:
            domain = port.get("legal_domain") or {}
            if not domain and port.get("legal_range") is not None:
                domain = {"range": port.get("legal_range")}
            basis = str(domain.get("basis", "")).lower()
            unresolved = bool(port.get("unresolved")) or domain.get("kind") == "unresolved"
            if unresolved:
                authority = "C_TYPE_FALLBACK"
            elif any(token in basis for token in ("runtime", "eva", "coverage", "observed", "derived")):
                authority = "DERIVED"
            elif "human" in basis or "review" in basis:
                authority = "HUMAN_APPROVED"
            elif links:
                authority = "EXACT_SPEC"
            else:
                authority = "C_TYPE_FALLBACK"
            derivation = domain.get("basis") or port.get("derivation") or "locked contract interface"
            records.append({
                "name": port.get("name"),
                "width": port.get("width") or port.get("logical_width"),
                "signed": port.get("signed"),
                "domain": domain,
                "role": port.get("role"),
                "authority": authority,
                "derivation": derivation,
                "review_status": "REVIEWED" if links else "UNREVIEWED",
                "spec_pages": exact_page,
                "spec_sections": exact_sections,
                "spec_tables": exact_tables,
                "c_span": function_span,
                "contract_hash": self.contract_hash(str(contract.get("contract_id"))),
            })
        return records

    def traceability(self, contract: dict[str, Any]) -> dict[str, Any]:
        links = self.exact_links(contract)
        function = contract.get("function", {}) or {}
        source = self.manifest.get("source", {}) or {}
        spec = self.manifest.get("spec", {}) or {}
        return {
            "authority": "EXACT_SPEC" if links else "C_TYPE_FALLBACK",
            "review_status": "REVIEWED" if links else "UNREVIEWED",
            "spec_links": links,
            "spec_pdf": spec.get("path"),
            "source_file": function.get("source_file"),
            "source_root": source.get("model_root"),
            "c_span": function.get("source_span", {}),
            "contract_hash": self.contract_hash(str(contract.get("contract_id"))),
            "ports": self.port_records(contract),
        }

    def source_gate(self) -> dict[str, Any]:
        source = self.manifest.get("source", {}) or {}
        spec = self.manifest.get("spec", {}) or {}
        build = read_json(self.repo / "build" / "build-receipt.json", {}) or {}
        compile_check = read_json(self.repo / "facts" / "compile-check.json", {}) or {}
        blockers: list[str] = []
        pdf_path = Path(str(spec.get("path", ""))).expanduser()
        source_dir = Path(str(source.get("source_dir", ""))).expanduser()
        if source.get("status") != "PASS":
            blockers.append("source_manifest_gate_not_pass")
        if source.get("gate", {}).get("status") != "PASS":
            blockers.append("source_file_gate_not_pass")
        if spec.get("status") not in ("OK", "PASS") or spec.get("gate", {}).get("pages_145") is False:
            blockers.append("pdf_gate_not_pass")
        if not pdf_path.is_file():
            blockers.append("pdf_file_missing")
        elif spec.get("sha256") and file_hash(pdf_path) != spec.get("sha256"):
            blockers.append("pdf_hash_mismatch")
        if not source_dir.is_dir():
            blockers.append("c_source_directory_missing")
        if compile_check.get("status") != "PASS":
            blockers.append("c_frontend_compile_check_not_pass")
        if build.get("status") != "PASS":
            blockers.append("c_clean_build_not_pass")
        smoke = build.get("smoke", {}) or {}
        if smoke and smoke.get("expected_hash") and not any(item.get("sha256") == smoke.get("expected_hash") for item in smoke.get("outputs", [])):
            blockers.append("c_smoke_golden_hash_not_pass")
        binary = build.get("binary", {}) or {}
        smoke_summary = {
            "mode": smoke.get("mode"),
            "expected_hash": smoke.get("expected_hash"),
            "matching_outputs": [
                {"path": item.get("path"), "sha256": item.get("sha256"), "size_bytes": item.get("size_bytes")}
                for item in smoke.get("outputs", [])
                if item.get("sha256") == smoke.get("expected_hash")
            ],
        }
        return {
            "status": "PASS" if not blockers else "BLOCKED",
            "blockers": blockers,
            "pdf": {"path": spec.get("path"), "sha256": spec.get("sha256"), "pages": self.manifest.get("pdf_extraction", {}).get("page_count") or spec.get("gate", {}).get("pages")},
            "source": {"path": source.get("source_dir"), "sha256": source.get("source_hashes_sha256")},
            "compile_check": {"status": compile_check.get("status"), "translation_units": compile_check.get("compiler_command_count")},
            "build": {
                "status": build.get("status"),
                "binary": {key: binary.get(key) for key in ("path", "sha256", "size_bytes")},
                "smoke": smoke_summary,
            },
        }

    def width_spec_gate(self, contract_id: str) -> dict[str, Any]:
        contract = self.contracts.get(contract_id, {})
        trace = self.traceability(contract)
        blockers: list[str] = []
        if not self.exact_links(contract):
            blockers.append("missing_exact_spec_link")
        if not contract.get("function", {}).get("name"):
            blockers.append("missing_function_fact")
        for port in trace["ports"]:
            if not port.get("width") or int(port["width"]) <= 0:
                blockers.append(f"missing_width:{port.get('name')}")
            if port.get("authority") in {"C_TYPE_FALLBACK", "AI_PROPOSED"}:
                blockers.append(f"generation_blocked_authority:{port.get('name')}")
        if str(contract.get("review_status", "")).upper() in {"AI_PROPOSED", "C_TYPE_FALLBACK"}:
            blockers.append(f"generation_blocked_contract:{contract.get('review_status')}")
        return {
            "status": "PASS" if not blockers else "BLOCKED",
            "blockers": sorted(set(blockers)),
            "traceability": trace,
        }

    def classify(self, entry: dict[str, Any]) -> str:
        contract = self.contracts.get(str(entry.get("contract_id")), {})
        semantic_kind = str((contract.get("semantics") or {}).get("kind", "")).lower()
        if any(token in semantic_kind for token in ("arithmetic", "quant", "round", "shift", "numeric", "midpoint")):
            return "arithmetic"
        if any(token in semantic_kind for token in ("table", "lookup", "config", "configuration", "mapping")):
            return "table_config"
        text = json.dumps({
            "proposal": contract.get("proposal"),
            "semantics": contract.get("semantics"),
            "roles": [item.get("role") for item in (contract.get("interface", {}) or {}).get("ports", [])],
            "role": entry.get("role"),
        }, sort_keys=True).lower()
        if any(token in text for token in ("table", "config", "configuration", "lookup")):
            return "table_config"
        if any(token in text for token in ("arithmetic", "quantization", "rounding", "shift", "numeric")):
            return "arithmetic"
        return "leaf"

    def valid_cached_ids(self) -> list[str]:
        result: set[str] = set()
        for item in self.cache_entries():
            cid = str(item.get("contract_id", ""))
            if item.get("valid") and cid and self.artifact_dir(cid):
                result.add(cid)
        return sorted(result)

    def frame_matrix(self) -> list[dict[str, Any]]:
        source = self.manifest.get("source", {}) or {}
        model_root = Path(str(source.get("model_root", "")))
        scripts = sorted((model_root / "bittrue_smoke").glob("run_c_baseline*.sh")) if model_root.is_dir() else []
        records = []
        for path in scripts:
            name = path.stem
            lowered = name.lower()
            kind = "default"
            if "bpc" in lowered or "bit" in lowered:
                kind = "bit_depth"
            elif any(token in lowered for token in ("420", "444", "sampling", "native")):
                kind = "sampling"
            records.append({"name": name, "script": str(path.relative_to(model_root)) if model_root.is_dir() else str(path), "kind": kind})
        selected: list[dict[str, Any]] = []
        for kind in ("default", "bit_depth", "sampling"):
            item = next((value for value in records if value["kind"] == kind), None)
            if item and item not in selected:
                selected.append(item)
        return selected

    def dependency_pair(self) -> dict[str, Any] | None:
        pair = self.plan.get("dependency_pair")
        return pair if isinstance(pair, dict) and pair.get("callee_contract") else None

    def pilot_functions(self, model_router: "ModelRouter") -> list[dict[str, Any]]:
        entries = list(self.plan.get("contracts", []))
        selected: list[dict[str, Any]] = []
        used: set[str] = set()

        def add(entry: dict[str, Any], reason: str, cached: bool = False) -> None:
            cid = str(entry.get("contract_id", ""))
            if not cid or cid in used or len(selected) >= 4:
                return
            kind = self.classify(entry)
            selected.append({
                "contract_id": cid,
                "function": entry.get("function"),
                "kind": kind,
                "selection_reason": reason,
                "cached_control": cached,
                "candidate_limit": 2,
                "model_tier": model_router.route(kind, cached=cached)["tier"],
                "contract_hash": self.contract_hash(cid),
                "interface_shape": entry.get("interface_shape", []),
            })
            used.add(cid)

        for cid in self.valid_cached_ids():
            entry = self.plan_item(cid)
            if entry:
                add(entry, "one cached promoted control", cached=True)
                break
        arithmetic = [entry for entry in entries if entry.get("ready") and entry.get("new_work") and self.classify(entry) == "arithmetic"]
        for entry in sorted(arithmetic, key=lambda item: str(item.get("contract_id"))):
            add(entry, "one newly GENERATION_READY arithmetic leaf")
            break
        table = [entry for entry in entries if entry.get("ready") and self.classify(entry) == "table_config"]
        for entry in sorted(table, key=lambda item: str(item.get("contract_id"))):
            add(entry, "one GENERATION_READY table/config leaf when available")
            break
        pair = self.dependency_pair()
        if pair:
            callee = str(pair.get("callee_contract"))
            entry = self.plan_item(callee)
            if entry:
                for item in selected:
                    if item["contract_id"] == callee:
                        item["dependency_pair"] = pair
                        item["selection_reason"] += "; smallest acyclic dependency pair"
                        break
                else:
                    add(entry, "smallest acyclic dependency pair", cached=False)
                    if selected:
                        selected[-1]["dependency_pair"] = pair
        return selected[:4]

    def scale_plan(self, model_router: "ModelRouter") -> dict[str, Any]:
        ready = [
            {
                "contract_id": item.get("contract_id"),
                "function": item.get("function"),
                "kind": self.classify(item),
                "contract_hash": self.contract_hash(str(item.get("contract_id"))),
                "model_tier": model_router.route(self.classify(item))["tier"],
            }
            for item in self.plan.get("contracts", [])
            if item.get("ready")
        ]
        return {
            "schema_version": 1,
            "status": "PLANNED_NOT_STARTED",
            "start_policy": "MANUAL_ONLY_AFTER_PILOT",
            "candidate_limit": 4,
            "functions": ready,
            "frames": self.frame_matrix(),
            "created_at": utc_now(),
            "source_hash": self.manifest.get("source", {}).get("source_hashes_sha256"),
        }


class ModelRouter:
    def __init__(self, policy_path: Path = REPO_ROOT / "model-policy.yaml"):
        self.policy_path = policy_path
        try:
            self.policy = json.loads(policy_path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            self.policy = {"routes": {}}

    def route(self, kind: str, *, cached: bool = False) -> dict[str, Any]:
        if cached:
            tier = "deterministic"
        elif kind == "table_config":
            tier = "strong"
        elif kind == "arithmetic":
            tier = "cheap"
        else:
            tier = "strong"
        route = (self.policy.get("routes", {}) or {}).get(tier, {}) or {}
        env_name = route.get("model_env")
        return {
            "tier": tier,
            "model_env": env_name,
            "model": os.environ.get(str(env_name)) if env_name else None,
            "initial_calls_allowed": int(route.get("initial_calls", 0)),
            "escalation_calls_allowed": int(route.get("escalation_calls", 0)),
            "source": "model-policy.yaml",
        }


def summarize_candidates(generation: dict[str, Any], unit: dict[str, Any], limit: int) -> list[dict[str, Any]]:
    observations = list(unit.get("candidates", []) or unit.get("matrix", []) or [])
    unit_by_name = {str(item.get("candidate")): item for item in observations}
    candidates = list(generation.get("candidates", []))
    if not candidates:
        candidates = [{"candidate": item.get("candidate")} for item in observations]
    compile_records = {
        str(item.get("candidate")): item
        for item in unit.get("compile_once", [])
        if isinstance(item, dict) and item.get("candidate")
    }
    result = []
    for candidate in candidates[:limit]:
        name = str(candidate.get("candidate"))
        observed = unit_by_name.get(name, {})
        compile_evidence = observed.get("compile") or candidate.get("compile") or {}
        if not compile_evidence and observed.get("compile_once") is True:
            compile_evidence = {"status": "PASS", "source": "candidate receipt"}
        if not compile_evidence and name in compile_records:
            compile_evidence = {"status": "PASS", "source": "compile_once receipt"}
        result.append({
            "candidate": name,
            "validation": candidate.get("validation"),
            "verification_status": observed.get("verification_status") or observed.get("candidate_status"),
            "vectors_executed": observed.get("vectors_executed", observed.get("vectors")),
            "smallest_counterexample": observed.get("smallest_counterexample"),
            "compile_status": compile_evidence.get("status", "PASS" if compile_evidence else "FAIL"),
            "accepted": name == unit.get("promoted_candidate"),
        })
    return result


def normalize_modes(bitstream: dict[str, Any]) -> dict[str, list[dict[str, Any]]]:
    modes = bitstream.get("modes", {})
    if isinstance(modes, dict):
        return {str(name): list(value.get("scenarios", [])) for name, value in modes.items() if isinstance(value, dict)}
    if isinstance(modes, list):
        result: dict[str, list[dict[str, Any]]] = {}
        for item in modes:
            result.setdefault(str(item.get("mode", "unknown")), []).append(item)
        return result
    return {}


def compact_frames(bitstream: dict[str, Any], selected_frames: list[dict[str, Any]]) -> list[dict[str, Any]]:
    modes = normalize_modes(bitstream)
    all_scenarios = [scenario for scenarios in modes.values() for scenario in scenarios]
    result = []
    for frame in selected_frames:
        def scenario_value(item: dict[str, Any], key: str, default: Any = None) -> Any:
            nested = item.get("scenario")
            if isinstance(nested, dict) and nested.get(key) is not None:
                return nested.get(key)
            return item.get(key, default)

        matched = [item for item in all_scenarios if scenario_value(item, "name") == frame["name"] or str(scenario_value(item, "script", "")).endswith(frame["script"])]
        if not matched:
            matched = [item for item in all_scenarios if frame["kind"] == "default" and "baseline" in str(scenario_value(item, "name", ""))]
        if not matched and frame["kind"] == "default" and all("scenario" not in item for item in all_scenarios):
            # Older cached receipts contain one record per mode, without a nested
            # scenario. Their only frame is the verified default frame.
            matched = all_scenarios
        result.append({
            "name": frame["name"],
            "kind": frame["kind"],
            "script": frame["script"],
            "modes": [
                {
                    "mode": mode,
                    "status": next((item.get("status") for item in scenarios if item in matched), "MISSING"),
                    "sha256": next((item.get("sha256") for item in scenarios if item in matched), None),
                    "baseline_sha256": next((item.get("baseline_sha256") or item.get("expected_sha256") for item in scenarios if item in matched), None),
                    "byte_equal": next((item.get("byte_equal", item.get("byte_for_byte_equal", item.get("size_bytes") == item.get("expected_size_bytes", item.get("size_bytes")))) for item in scenarios if item in matched), False),
                }
                for mode, scenarios in modes.items()
            ],
        })
    return result


class FlowRunner:
    def __init__(
        self,
        store: DurableStore,
        run_id: str,
        contract_id: str | None = None,
        repo: Path = REPO_ROOT,
        *,
        refresh: bool = False,
    ):
        self.store = store
        self.run_id = run_id
        self.contract_id = safe_id(contract_id) if contract_id else "shared"
        self.refresh = refresh
        self.repo = repo
        self.directory = store.cache / "flow" / safe_id(run_id) / self.contract_id
        self.worktree = self.directory / "repo"
        self.receipt_path = self.directory / "flow-receipt.json"
        self.lock = store.locks / f"flow-{safe_id(run_id)}-{self.contract_id}.lock"

    def run_once(self) -> dict[str, Any]:
        existing = read_json(self.receipt_path, {}) or {}
        if existing.get("status") == "PASS":
            return existing
        try:
            self.lock.mkdir()
        except FileExistsError:
            for _ in range(600):
                if self.receipt_path.is_file():
                    return read_json(self.receipt_path, {}) or {}
                time.sleep(0.5)
            raise InfrastructureFailure("timed out waiting for current-flow lock")
        try:
            self.directory.mkdir(parents=True, exist_ok=True)
            existing = read_json(self.receipt_path, {}) or {}
            if existing.get("status") == "PASS":
                return existing
            if existing:
                # Preserve failed attempts on SMB, then retry from a clean
                # repository copy so a partial flow state cannot poison the
                # resumed run.
                failed_receipt = self.directory / f"flow-receipt.failed-{uuid.uuid4().hex[:8]}.json"
                os.replace(self.receipt_path, failed_receipt)
                if self.worktree.exists():
                    os.replace(self.worktree, self.directory / f"repo.failed-{uuid.uuid4().hex[:8]}")
            if not self.worktree.exists():
                shutil.copytree(
                    self.repo,
                    self.worktree,
                    ignore=shutil.ignore_patterns(".git", "tmp", "__pycache__", ".DS_Store"),
                )
            # The existing flow uses this directory as the parent for isolated
            # temporary C/overlay copies. It is intentionally empty on SMB;
            # keeping the repository's large local tmp tree out of the copy
            # avoids duplicating vectors while preserving the flow contract.
            (self.worktree / "tmp").mkdir(parents=True, exist_ok=True)
            log_path = self.directory / "flow.log"
            command = [sys.executable, "tools/cicd_agent.py", "run"]
            env = os.environ.copy()
            env.update({
                "DSC_CICD_GENERATOR_CMD": os.environ.get("DSC_CICD_GENERATOR_CMD", "python3 tools/generator_fixture.py"),
                "DSC_CICD_MODEL": f"regression-{safe_id(self.run_id)}-{self.contract_id}",
                "DSC_CICD_SHARDS": os.environ.get("DSC_CICD_SHARDS", "4"),
                "DSC_CICD_WORKERS": os.environ.get("DSC_CICD_WORKERS", "2"),
                "DSC_CICD_TARGET_CONTRACT": self.contract_id,
            })
            if self.refresh:
                env["DSC_CICD_FORCE_REGENERATE"] = "1"
            started = epoch_now()
            with log_path.open("w", encoding="utf-8") as log:
                log.write(json.dumps({"command": command, "cwd": str(self.worktree), "started_at": utc_now()}) + "\n")
                log.flush()
                process = subprocess.run(
                    command,
                    cwd=str(self.worktree),
                    env=env,
                    stdout=log,
                    stderr=subprocess.STDOUT,
                    check=False,
                    timeout=int(os.environ.get("DSC_REGRESSION_FLOW_TIMEOUT", "1800")),
                )
            receipt = {
                "schema_version": 1,
                "run_id": self.run_id,
                "contract_id": self.contract_id,
                "status": "PASS" if process.returncode == 0 else "FAIL",
                "execution_status": "EXECUTED_NOW",
                "command": command,
                "worktree": str(self.worktree),
                "log": str(log_path),
                "returncode": process.returncode,
                "duration_seconds": round(epoch_now() - started, 3),
                "started_at": utc_now(),
                "generator": env.get("DSC_CICD_GENERATOR_CMD"),
                "model_name_source": "DSC_CICD_MODEL",
                "target_contract_source": "queue-discovered-contract-id",
                "refresh": self.refresh,
            }
            atomic_write_json(self.receipt_path, redact(receipt))
            return receipt
        except (OSError, subprocess.SubprocessError, TimeoutError) as error:
            receipt = {
                "schema_version": 1,
                "run_id": self.run_id,
                "contract_id": self.contract_id,
                "status": "INFRASTRUCTURE_FAILURE",
                "execution_status": "EXECUTED_NOW",
                "refresh": self.refresh,
                "last_error": str(error),
            }
            atomic_write_json(self.receipt_path, redact(receipt))
            return receipt
        finally:
            try:
                self.lock.rmdir()
            except OSError:
                pass


class RegressionService:
    def __init__(self, store: DurableStore, repo: Path = REPO_ROOT):
        self.store = store
        self.repo = repo
        self.router = ModelRouter(repo / "model-policy.yaml")

    def init(self) -> dict[str, Any]:
        self.store.ensure_layout()
        self.refresh_dashboard()
        return {
            "status": "PASS",
            "root": str(self.store.root),
            "mountpoint": str(self.store.mount.mountpoint) if self.store.mount else None,
            "layout": QUEUE_STATES,
            "source_gate": LocalContext(self.repo).source_gate(),
        }

    def submit(self, profile: str) -> dict[str, Any]:
        if profile != "pilot":
            raise ValueError("only --profile pilot is allowed; scale plans are manual and never auto-started")
        self.store.ensure_layout()
        context = LocalContext(self.repo)
        source_gate = context.source_gate()
        if source_gate["status"] != "PASS":
            raise InfrastructureFailure("C/PDF input gate blocked: " + ", ".join(source_gate["blockers"]))
        functions = context.pilot_functions(self.router)
        if not functions:
            raise InfrastructureFailure("pilot selection found no cached control or GENERATION_READY leaf")
        run_id = time.strftime("%Y%m%dT%H%M%SZ", time.gmtime()) + "-" + uuid.uuid4().hex[:8]
        frames = context.frame_matrix()
        run = {
            "schema_version": 1,
            "run_id": run_id,
            "profile": profile,
            "status": "QUEUED",
            "created_at": utc_now(),
            "candidate_limit": 2,
            "max_functions": 4,
            "frames": frames,
            "functions": functions,
            "source_hash": context.manifest.get("source", {}).get("source_hashes_sha256"),
            "spec_hash": context.manifest.get("spec", {}).get("sha256"),
            "source_gate": source_gate,
            "strategy": "pilot only; no scale jobs are enqueued",
        }
        run_dir = self.store.run_dir(run_id)
        (run_dir / "functions").mkdir(parents=True, exist_ok=False)
        atomic_write_json(run_dir / "run.json", redact(run))
        for function in functions:
            cid = safe_id(str(function["contract_id"]))
            function_dir = run_dir / "functions" / cid
            function_dir.mkdir(parents=True, exist_ok=True)
            atomic_write_json(function_dir / "plan.json", redact(function))
            job = {
                "job_id": f"{run_id}--{cid}",
                "run_id": run_id,
                "contract_id": function["contract_id"],
                "function": function.get("function"),
                "kind": function.get("kind"),
                "candidate_limit": 2,
                "frames": frames,
                "model_tier": function.get("model_tier"),
                "cached_control": function.get("cached_control", False),
                "dependency_pair": function.get("dependency_pair"),
            }
            self.store.enqueue(job)
        append_jsonl(run_dir / "strategy.jsonl", {"event": "submit", "decision": "pilot", "rationale": "bounded selection from facts/cache; scale is not enqueued"})
        self.refresh_dashboard()
        return run

    def set_stage(self, directory: Path, stage: str, completed: int, total: int, *, last_error: str | None = None) -> None:
        self.store.write_status(
            directory,
            status="running",
            stage=stage,
            progress={"completed": completed, "total": total, "unit": "stages"},
            last_error=last_error,
        )
        self.store.write_heartbeat(directory)

    def resolve_artifact_context(self, job: dict[str, Any], flow: dict[str, Any] | None) -> LocalContext:
        if flow and flow.get("worktree"):
            return LocalContext(Path(str(flow["worktree"])))
        return LocalContext(self.repo)

    def load_receipt_bundle(self, context: LocalContext, contract_id: str) -> tuple[Path | None, dict[str, Any]]:
        artifact = context.artifact_dir(contract_id)
        if not artifact:
            return None, {}
        bundle: dict[str, Any] = {}
        for name in (
            "generation.json",
            "unit-receipt.json",
            "dependency-receipt.json",
            "bitstream-receipt.json",
            "overlay-receipt.json",
            "shadow-receipt.json",
            "rtl-return-receipt.json",
        ):
            path = artifact / name
            if path.is_file():
                key = name[:-5]
                if key.endswith("-receipt"):
                    key = key[:-8]
                bundle[key] = read_json(path, {}) or {}
        if not bundle.get("generation"):
            bundle["generation"] = {"status": "REUSED_VALID_RECEIPT", "execution_status": "REUSED_VERIFIED_RECEIPT"}
        return artifact, bundle

    def copy_accepted_rtl(self, artifact: Path | None, function_dir: Path, unit: dict[str, Any]) -> str | None:
        if not artifact:
            return None
        candidate = str(unit.get("promoted_candidate", ""))
        names = [artifact / "generated" / f"{candidate}.sv", artifact / "rtl" / f"{candidate}.sv"]
        source = next((path for path in names if path.is_file()), None)
        if not source:
            return None
        target = function_dir / "accepted" / source.name
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source, target)
        return str(target)

    def execute_job(self, directory: Path) -> dict[str, Any]:
        job = read_json(directory / "job.json", {}) or {}
        run_id = str(job.get("run_id"))
        cid = str(job.get("contract_id"))
        heartbeat = Heartbeat(self.store, directory)
        heartbeat.start()
        started = epoch_now()
        stage_results: dict[str, Any] = {}
        traceability: dict[str, Any] = {}
        source_gate: dict[str, Any] = {}
        function_dir = self.store.run_dir(run_id) / "functions" / safe_id(cid)
        function_dir.mkdir(parents=True, exist_ok=True)
        try:
            context = LocalContext(self.repo)
            source_gate = context.source_gate()
            if source_gate["status"] != "PASS":
                raise InfrastructureFailure("C/PDF input gate blocked: " + ", ".join(source_gate["blockers"]))
            total = len(STAGES)
            self.set_stage(directory, STAGES[0], 0, total)
            gate = context.width_spec_gate(cid)
            traceability = gate["traceability"]
            stage_results[STAGES[0]] = gate
            if gate["status"] != "PASS":
                raise InfrastructureFailure("width/spec gate blocked: " + ", ".join(gate["blockers"]))

            flow: dict[str, Any] | None = None
            if not job.get("cached_control"):
                self.set_stage(directory, STAGES[1], 1, total)
                flow = FlowRunner(
                    self.store,
                    run_id,
                    cid,
                    self.repo,
                    refresh=bool(job.get("refresh")),
                ).run_once()
                if flow.get("status") != "PASS":
                    raise InfrastructureFailure(f"current C-to-RTL flow failed: {flow.get('last_error') or flow.get('status')}")
            else:
                self.set_stage(directory, STAGES[1], 1, total)
                flow = {"status": "REUSED_VALID_RECEIPT", "execution_status": "REUSED_VERIFIED_RECEIPT", "source": "cache-index"}
            flow_context = self.resolve_artifact_context(job, flow if not job.get("cached_control") else None)
            artifact, bundle = self.load_receipt_bundle(flow_context, cid)
            if not artifact:
                raise InfrastructureFailure(f"no artifact bundle for contract {cid}")
            generation = bundle.get("generation", {})
            unit = bundle.get("unit", {})
            dependency = bundle.get("dependency", {})
            bitstream = bundle.get("bitstream", {})
            candidate_limit = min(4, int(job.get("candidate_limit", 2)))
            candidates = summarize_candidates(generation, unit, candidate_limit)
            stage_results[STAGES[1]] = {
                "status": "PASS",
                "execution_status": generation.get("execution_status", "REUSED_VERIFIED_RECEIPT"),
                "model_calls": generation.get("model_calls", 0),
                "tokens": generation.get("tokens", 0),
                "candidates": candidates,
                "route": self.router.route(str(job.get("kind", "leaf")), cached=bool(job.get("cached_control"))),
            }
            self.set_stage(directory, STAGES[2], 2, total)
            compile_statuses = [item.get("compile_status") for item in candidates]
            stage_results[STAGES[2]] = {
                "status": "PASS" if all(status == "PASS" for status in compile_statuses) and candidates else "FAIL",
                "compile_once": unit.get("compile_once", []),
                "candidate_count": len(candidates),
            }
            self.set_stage(directory, STAGES[3], 3, total)
            domain = unit.get("domain", {}) or {}
            stage_results[STAGES[3]] = {
                "status": "PASS" if unit.get("verification_status") in ("EXHAUSTIVE_EQUIVALENT", "PASS") else "FAIL",
                "vectors": domain.get("total_vectors", unit.get("vectors_executed", 0)),
                "shards": domain.get("shards", []),
                "verification_status": unit.get("verification_status"),
                "counterexample": unit.get("smallest_counterexample"),
                "candidates": candidates,
            }
            self.set_stage(directory, STAGES[4], 4, total)
            pair = job.get("dependency_pair")
            dependency_status = dependency.get("status")
            stage_results[STAGES[4]] = {
                "status": (dependency_status if dependency_status == "PASS" else "FAIL") if pair else "NOT_APPLICABLE",
                "pair": pair,
                "receipt_status": dependency_status,
                "ports": dependency.get("dependency_ports", []),
                "evidence": dependency.get("execution_evidence", {}),
            }
            self.set_stage(directory, STAGES[5], 5, total)
            modes = normalize_modes(bitstream)
            matrix_status = bitstream.get("status")
            shadow = bundle.get("shadow", {}) or {}
            rtl_return = bundle.get("rtl-return", {}) or {}
            overlay = bundle.get("overlay", {}) or {}
            mode_gate = {
                "C_ONLY": bitstream.get("status"),
                "SHADOW": shadow.get("status"),
                "RTL_RETURN": rtl_return.get("status"),
                "OVERLAY": overlay.get("status") if overlay else "NOT_RECORDED",
            }
            stage_results[STAGES[5]] = {
                "status": "PASS" if matrix_status == "PASS" and shadow.get("status") == "PASS" and rtl_return.get("status") == "PASS" else "FAIL",
                "authority_modes": mode_gate,
                "scenario_modes": {mode: {"status": "PASS" if all(item.get("status") == "PASS" for item in scenarios) else "FAIL", "scenario_count": len(scenarios)} for mode, scenarios in modes.items()},
            }
            self.set_stage(directory, STAGES[6], 6, total)
            frames = compact_frames(bitstream, list(job.get("frames", [])))
            missing_frames = [
                frame.get("name") for frame in frames
                if not frame.get("modes") or all(mode.get("status") == "MISSING" for mode in frame.get("modes", []))
            ]
            selected_frame_pass = all(
                mode.get("status") == "PASS" and mode.get("sha256") == mode.get("baseline_sha256")
                for frame in frames for mode in frame.get("modes", [])
            ) if frames else matrix_status == "PASS"
            if job.get("cached_control") and missing_frames:
                selected_frame_pass = matrix_status == "PASS" and any(
                    frame.get("kind") == "default"
                    and any(mode.get("status") == "PASS" for mode in frame.get("modes", []))
                    for frame in frames
                )
            stage_results[STAGES[6]] = {"status": "PASS" if selected_frame_pass else "FAIL", "frames": frames}
            if missing_frames:
                stage_results[STAGES[6]]["coverage_warning"] = "cached control receipt does not contain every pilot frame"
                stage_results[STAGES[6]]["missing_frames"] = missing_frames
            accepted_rtl = self.copy_accepted_rtl(artifact, function_dir, unit)
            blockers = []
            if any(result.get("status") == "FAIL" for result in stage_results.values()):
                blockers.append("one or more regression gates failed")
            receipt = {
                "schema_version": 1,
                "run_id": run_id,
                "contract_id": cid,
                "function": job.get("function"),
                "kind": job.get("kind"),
                "status": "PASS" if not blockers else "FAIL",
                "execution_status": "EXECUTED_NOW" if not job.get("cached_control") else "REUSED_VERIFIED_RECEIPT",
                "created_at": utc_now(),
                "duration_seconds": round(epoch_now() - started, 3),
                "contract_hash": context.contract_hash(cid),
                "source_gate": source_gate,
                "traceability": traceability,
                "stages": stage_results,
                "candidate_pass_rate": f"{sum(1 for item in candidates if item.get('accepted') or item.get('verification_status') in ('EXHAUSTIVE_EQUIVALENT', 'PASS'))}/{len(candidates) or 0}",
                "frame_pass_rate": f"{sum(1 for frame in frames if all(mode.get('status') == 'PASS' and mode.get('sha256') == mode.get('baseline_sha256') for mode in frame.get('modes', [])))}/{len(frames) or 0}",
                "accepted_rtl": accepted_rtl,
                "source_artifact": str(artifact),
                "raw_flow": flow,
                "blockers": blockers,
            }
            atomic_write_json(function_dir / "receipt.json", redact(receipt))
            atomic_write_json(function_dir / "traceability.json", redact(gate["traceability"]))
            final_state = "done" if not blockers else "failed"
            self.store.finish(
                directory,
                final_state,
                stage="complete",
                progress={"completed": total, "total": total, "unit": "stages"},
                last_error=None if not blockers else "; ".join(blockers),
                receipt=str(function_dir / "receipt.json"),
            )
            return receipt
        except Exception as error:
            error_text = str(error)
            failure = {
                "schema_version": 1,
                "run_id": run_id,
                "contract_id": cid,
                "function": job.get("function"),
                "status": "INFRASTRUCTURE_FAILURE" if isinstance(error, InfrastructureFailure) else "FAIL",
                "execution_status": "EXECUTED_NOW",
                "duration_seconds": round(epoch_now() - started, 3),
                "stages": stage_results,
                "traceability": traceability,
                "blockers": [error_text],
            }
            atomic_write_json(function_dir / "receipt.json", redact(failure))
            self.store.finish(directory, "failed", stage=directory.name, last_error=error_text, progress={"completed": len(stage_results), "total": len(STAGES), "unit": "stages"}, receipt=str(function_dir / "receipt.json"))
            return failure
        finally:
            heartbeat.stop()
            self.refresh_dashboard()

    def worker(self, jobs: int) -> dict[str, Any]:
        self.store.ensure_layout()
        recovered = self.store.recover_stale()
        claimed: list[Path] = []
        while len(claimed) < max(1, jobs):
            item = self.store.claim_one()
            if not item:
                break
            claimed.append(item)
        results: list[dict[str, Any]] = []
        with concurrent.futures.ThreadPoolExecutor(max_workers=max(1, jobs)) as executor:
            futures = [executor.submit(self.execute_job, item) for item in claimed]
            for future in futures:
                results.append(future.result())
        self.maybe_create_scale_plans()
        self.refresh_dashboard()
        return {"status": "PASS" if all(item.get("status") == "PASS" for item in results) else "FAIL", "recovered": recovered, "claimed": len(claimed), "results": results}

    def maybe_create_scale_plans(self) -> None:
        for run_dir in sorted(self.store.runs.iterdir() if self.store.runs.exists() else []):
            if not run_dir.is_dir():
                continue
            run = read_json(run_dir / "run.json", {}) or {}
            if run.get("profile") != "pilot" or (run_dir / "scale-plan.json").exists():
                continue
            function_dirs = [path for path in (run_dir / "functions").iterdir() if path.is_dir()] if (run_dir / "functions").is_dir() else []
            receipts = [read_json(path / "receipt.json", {}) or {} for path in function_dirs]
            if receipts and all(receipt.get("status") == "PASS" for receipt in receipts):
                plan = LocalContext(self.repo).scale_plan(self.router)
                atomic_write_json(run_dir / "scale-plan.json", redact(plan))
                atomic_write_json(self.store.root / "scale-plan.json", redact(plan))
                append_jsonl(
                    run_dir / "strategy.jsonl",
                    {
                        "event": "scale_plan_created",
                        "decision": "do_not_start",
                        "rationale": "pilot PASS; all GENERATION_READY contracts are planned but not enqueued",
                    },
                )

    def start_scale(self, pilot_run_id: str, *, refresh: bool = False) -> dict[str, Any]:
        """Start one explicit scale batch from a passing pilot plan.

        Scale is intentionally a separate run so its receipts never overwrite
        pilot evidence.  Each queued function receives its discovered contract
        id and gets an independent flow worktree; this permits parallel fresh
        generator/model passes without introducing a source-level allowlist.
        """
        pilot_dir = self.store.run_dir(pilot_run_id)
        if not pilot_dir.is_dir():
            raise FileNotFoundError(pilot_run_id)
        pilot = read_json(pilot_dir / "run.json", {}) or {}
        if pilot.get("profile") != "pilot":
            raise InfrastructureFailure(f"scale parent is not a pilot run: {pilot_run_id}")
        scale_path = pilot_dir / "scale-plan.json"
        scale = read_json(scale_path, {}) or {}
        if not scale:
            raise InfrastructureFailure(f"pilot has no scale plan: {pilot_run_id}")
        started_run_id = scale.get("started_run_id")
        if scale.get("status") == "STARTED" and started_run_id:
            existing = self.store.run_dir(str(started_run_id))
            if existing.is_dir():
                return read_json(existing / "run.json", {}) or {"run_id": started_run_id}
        if scale.get("status") not in {"PLANNED_NOT_STARTED", "STARTED"}:
            raise InfrastructureFailure(f"scale plan is not startable: {scale.get('status')}")

        pilot_functions = [
            read_json(path / "receipt.json", {}) or {}
            for path in (pilot_dir / "functions").iterdir()
            if path.is_dir()
        ] if (pilot_dir / "functions").is_dir() else []
        if not pilot_functions or not all(item.get("status") == "PASS" for item in pilot_functions):
            raise InfrastructureFailure("scale requires every pilot function receipt to be PASS")
        context = LocalContext(self.repo)
        source_gate = context.source_gate()
        if source_gate["status"] != "PASS":
            raise InfrastructureFailure("C/PDF input gate blocked: " + ", ".join(source_gate["blockers"]))
        functions = list(scale.get("functions", []))
        if not functions:
            raise InfrastructureFailure("scale plan has no GENERATION_READY functions")
        frames = list(scale.get("frames") or context.frame_matrix())
        valid_cached = set(context.valid_cached_ids())
        discovered_pair = context.dependency_pair()
        run_id = time.strftime("%Y%m%dT%H%M%SZ", time.gmtime()) + "-scale-" + uuid.uuid4().hex[:8]
        run_functions: list[dict[str, Any]] = []
        for item in functions:
            cid = safe_id(str(item.get("contract_id")))
            cached_control = cid in valid_cached and not refresh
            run_functions.append({
                "contract_id": cid,
                "function": item.get("function"),
                "kind": item.get("kind", "leaf"),
                "selection_reason": "explicit scale batch from facts-driven GENERATION_READY plan",
                "cached_control": cached_control,
                "refresh": refresh,
                "candidate_limit": int(scale.get("candidate_limit", 4)),
                "model_tier": item.get("model_tier") or self.router.route(str(item.get("kind", "leaf")))["tier"],
                "contract_hash": item.get("contract_hash"),
            })
        run = {
            "schema_version": 1,
            "run_id": run_id,
            "profile": "scale",
            "parent_run_id": pilot_run_id,
            "status": "QUEUED",
            "created_at": utc_now(),
            "candidate_limit": int(scale.get("candidate_limit", 4)),
            "max_functions": len(run_functions),
            "frames": frames,
            "functions": run_functions,
            "source_hash": context.manifest.get("source", {}).get("source_hashes_sha256"),
            "spec_hash": context.manifest.get("spec", {}).get("sha256"),
            "source_gate": source_gate,
            "refresh": refresh,
            "strategy": "explicit scale batch; independent contract flow worktrees; no SVRT",
        }
        run_dir = self.store.run_dir(run_id)
        (run_dir / "functions").mkdir(parents=True, exist_ok=False)
        atomic_write_json(run_dir / "run.json", redact(run))
        for function in run_functions:
            cid = safe_id(str(function["contract_id"]))
            function_dir = run_dir / "functions" / cid
            function_dir.mkdir(parents=True, exist_ok=True)
            atomic_write_json(function_dir / "plan.json", redact(function))
            self.store.enqueue({
                "job_id": f"{run_id}--{cid}",
                "run_id": run_id,
                "contract_id": cid,
                "function": function.get("function"),
                "kind": function.get("kind"),
                "candidate_limit": function.get("candidate_limit", 4),
                "frames": frames,
                "model_tier": function.get("model_tier"),
                "cached_control": function.get("cached_control", False),
                "refresh": function.get("refresh", False),
                "dependency_pair": discovered_pair if discovered_pair and discovered_pair.get("callee_contract") == cid else None,
            })
        scale.update({
            "status": "STARTED",
            "started_at": utc_now(),
            "started_run_id": run_id,
            "refresh": refresh,
            "jobs_enqueued": len(run_functions),
        })
        atomic_write_json(scale_path, redact(scale))
        atomic_write_json(self.store.root / "scale-plan.json", redact(scale))
        append_jsonl(
            pilot_dir / "strategy.jsonl",
            {
                "event": "scale_started",
                "decision": "enqueue",
                "run_id": run_id,
                "refresh": refresh,
                "jobs": [item["contract_id"] for item in run_functions],
                "rationale": "user-authorized large-scale batch; each discovered contract has an independent flow worktree",
            },
        )
        self.refresh_dashboard()
        return run

    @staticmethod
    def _library_rtl_blockers(source: str) -> list[str]:
        scrubbed = re.sub(r"//.*|/\*.*?\*/", "", source, flags=re.S)
        forbidden = (
            (r"\balways_ff\b", "sequential always_ff"),
            (r"\balways_latch\b", "latch always_latch"),
            (r"\bposedge\b|\bnegedge\b", "clock edge"),
            (r"\binitial\b|\bwait\s*\(", "testbench timing"),
            (r"\bfork\b|\bjoin\b", "parallel procedural block"),
        )
        blockers = [label for pattern, label in forbidden if re.search(pattern, scrubbed, flags=re.I)]
        modules = re.findall(r"\bmodule\s+([A-Za-z_][A-Za-z0-9_]*)\s*\(", scrubbed)
        if not modules:
            blockers.append("missing module")
        elif len(modules) != 1:
            blockers.append("multiple modules")
        if not re.search(r"\bendmodule\b", scrubbed):
            blockers.append("missing endmodule")
        return sorted(set(blockers))

    @staticmethod
    def _canonical_library_source(source: str, contract_id: str) -> tuple[str, str | None]:
        """Give a verified single-module leaf a stable contract-based name."""
        pattern = re.compile(r"(\bmodule\s+)([A-Za-z_][A-Za-z0-9_]*)(\s*\()")
        matches = list(pattern.finditer(source))
        if len(matches) != 1:
            return source, None
        module = re.sub(r"[^A-Za-z0-9_]", "_", str(contract_id))
        if not module or module[0].isdigit():
            module = "c_" + module
        match = matches[0]
        canonical_source = source[:match.start(2)] + module + source[match.end(2):]
        return canonical_source, module

    def promote_library(self, run_id: str) -> dict[str, Any]:
        """Promote only PASS, spec-traceable leaf RTL into the designer library."""
        run_dir = self.store.run_dir(run_id)
        if not run_dir.is_dir():
            raise FileNotFoundError(run_id)
        run = read_json(run_dir / "run.json", {}) or {}
        library = self.repo / "library"
        rtl_root = library / "rtl"
        receipt_root = library / "verification"
        contract_root = library / "contracts"
        archive_root = library / "archive"
        for path in (rtl_root, receipt_root, contract_root, archive_root):
            path.mkdir(parents=True, exist_ok=True)
        manifest_path = library / "manifest.json"
        manifest = read_json(manifest_path, {}) or {}
        components = {str(item.get("contract_id")): item for item in manifest.get("components", [])}
        promoted: list[dict[str, Any]] = []
        skipped: list[dict[str, Any]] = []
        function_root = run_dir / "functions"
        for function_dir in sorted(function_root.iterdir() if function_root.is_dir() else []):
            if not function_dir.is_dir():
                continue
            receipt = read_json(function_dir / "receipt.json", {}) or {}
            cid = str(receipt.get("contract_id") or function_dir.name)
            if receipt.get("status") != "PASS":
                skipped.append({"contract_id": cid, "reason": "receipt_not_pass"})
                continue
            trace = receipt.get("traceability", {}) or {}
            if trace.get("review_status") != "REVIEWED" or trace.get("authority") in {"AI_PROPOSED", "C_TYPE_FALLBACK"}:
                skipped.append({"contract_id": cid, "reason": "traceability_not_promotable"})
                continue
            bad_ports = [
                str(port.get("name"))
                for port in trace.get("ports", [])
                if port.get("authority") in {"AI_PROPOSED", "C_TYPE_FALLBACK"}
            ]
            if bad_ports:
                skipped.append({"contract_id": cid, "reason": "port_authority_blocked", "ports": bad_ports})
                continue
            accepted = Path(str(receipt.get("accepted_rtl", "")))
            if not accepted.is_file():
                skipped.append({"contract_id": cid, "reason": "accepted_rtl_missing"})
                continue
            source = accepted.read_text(encoding="utf-8", errors="replace")
            canonical_source, module_name = self._canonical_library_source(source, cid)
            rtl_blockers = self._library_rtl_blockers(canonical_source)
            if module_name is None:
                rtl_blockers.append("stable single-module name unavailable")
            if rtl_blockers:
                skipped.append({"contract_id": cid, "reason": "rtl_boundary_blocked", "blockers": rtl_blockers})
                continue
            destination = rtl_root / f"{safe_id(cid)}.sv"
            old_hash = file_hash(destination)
            canonical_bytes = canonical_source.encode("utf-8")
            canonical_hash = hashlib.sha256(canonical_bytes).hexdigest()
            if old_hash and old_hash != canonical_hash:
                archive = archive_root / safe_id(cid) / f"{safe_id(run_id)}.sv"
                atomic_write_bytes(archive, destination.read_bytes())
            atomic_write_bytes(destination, canonical_bytes)
            compact = {
                "schema_version": 1,
                "run_id": run_id,
                "profile": run.get("profile"),
                "parent_run_id": run.get("parent_run_id"),
                "contract_id": cid,
                "function": receipt.get("function"),
                "kind": receipt.get("kind"),
                "status": "PASS",
                "execution_status": receipt.get("execution_status"),
                "candidate": Path(str(receipt.get("accepted_rtl"))).stem,
                "module": module_name,
                "rtl_sha256": file_hash(destination),
                "contract_hash": receipt.get("contract_hash"),
                "source_gate": receipt.get("source_gate"),
                "traceability": trace,
                "candidate_pass_rate": receipt.get("candidate_pass_rate"),
                "frame_pass_rate": receipt.get("frame_pass_rate"),
                "stages": {key: value.get("status") for key, value in (receipt.get("stages", {}) or {}).items()},
                "promoted_at": utc_now(),
            }
            atomic_write_json(contract_root / f"{safe_id(cid)}.json", redact(trace))
            atomic_write_json(receipt_root / f"{safe_id(cid)}.json", redact(compact))
            components[cid] = {
                "contract_id": cid,
                "function": receipt.get("function"),
                "module_file": str(destination.relative_to(library)),
                "module": module_name,
                "module_sha256": file_hash(destination),
                "verification_file": str((receipt_root / f"{safe_id(cid)}.json").relative_to(library)),
                "contract_hash": receipt.get("contract_hash"),
                "source_file": trace.get("source_file"),
                "c_span": trace.get("c_span"),
                "spec_links": trace.get("spec_links", []),
                "authority": trace.get("authority"),
                "boundary": "verified combinational leaf; C_ONLY remains rollback/reference",
                "run_id": run_id,
                "status": "PASS",
            }
            promoted.append(components[cid])
        manifest = {
            "schema_version": 1,
            "library": "dsc-verilog-library",
            "policy": "Only spec-traceable PASS leaf RTL is canonical; stateful callers remain C until separately contracted and verified.",
            "source_policy": "immutable external C model and local DSC 1.2a PDF; no SVRT",
            "spec_hash": run.get("spec_hash"),
            "source_hash": run.get("source_hash"),
            "updated_at": utc_now(),
            "components": sorted(components.values(), key=lambda item: str(item.get("contract_id"))),
        }
        atomic_write_json(manifest_path, redact(manifest))
        return {"status": "PASS" if promoted else "NO_PROMOTION", "run_id": run_id, "promoted": promoted, "skipped": skipped, "manifest": str(manifest_path)}

    def _href_for_path(self, path: Path) -> str:
        """Prefer dashboard-relative links for SMB artifacts, else a local file URI."""
        try:
            resolved = path.resolve()
            if path_is_under(resolved, self.store.root):
                return os.path.relpath(resolved, self.store.dashboard)
            return resolved.as_uri()
        except (OSError, ValueError):
            return str(path)

    def _function_details(self, run_dir: Path, function_dir: Path, plan: dict[str, Any], receipt: dict[str, Any]) -> dict[str, Any]:
        trace = receipt.get("traceability", {}) or {}
        links = [
            {"label": "receipt", "href": self._href_for_path(function_dir / "receipt.json")},
            {"label": "traceability", "href": self._href_for_path(function_dir / "traceability.json")},
        ]
        accepted = receipt.get("accepted_rtl")
        if accepted:
            links.append({"label": "accepted RTL", "href": self._href_for_path(Path(str(accepted)))})
        artifact = receipt.get("source_artifact")
        if artifact:
            links.append({"label": "artifact bundle", "href": self._href_for_path(Path(str(artifact)))})
        spec_links = []
        spec_pdf = trace.get("spec_pdf")
        for item in trace.get("spec_links", []) or []:
            page = item.get("page")
            href = self._href_for_path(Path(str(spec_pdf))) if spec_pdf else ""
            if href and page is not None:
                href += f"#page={int(page)}"
            spec_links.append({"anchor_id": item.get("anchor_id"), "page": page, "section": item.get("section"), "href": href})
        source_file = trace.get("source_file")
        source_root = trace.get("source_root")
        c_href = ""
        if source_file and source_root:
            c_href = self._href_for_path(Path(str(source_root)) / str(source_file))
            start_line = (trace.get("c_span") or {}).get("start_line")
            if start_line:
                c_href += f"#L{int(start_line)}"
        stages = receipt.get("stages", {}) or {}
        shard_stage = stages.get("shards_mutations", {}) or {}
        candidates = shard_stage.get("candidates", []) or []
        frames = (stages.get("frame_compare", {}) or {}).get("frames", []) or []
        return {
            "vectors": shard_stage.get("vectors"),
            "shards": shard_stage.get("shards", []),
            "candidates": candidates,
            "counterexamples": [item.get("smallest_counterexample") for item in candidates if item.get("smallest_counterexample")],
            "frames": frames,
            "artifact_links": links,
            "spec_links": spec_links,
            "c_source_link": {"href": c_href, "file": source_file, "span": trace.get("c_span", {})},
            "traceability": trace,
        }

    def snapshot(self) -> dict[str, Any]:
        jobs = self.store.list_jobs()
        counts = {state: sum(1 for item in jobs if item.get("queue_state") == state) for state in QUEUE_STATES}
        function_rows: list[dict[str, Any]] = []
        for run_dir in sorted(self.store.runs.iterdir() if self.store.runs.exists() else [], reverse=True):
            if not run_dir.is_dir():
                continue
            run = read_json(run_dir / "run.json", {}) or {}
            for function_dir in sorted((run_dir / "functions").iterdir() if (run_dir / "functions").is_dir() else []):
                receipt = read_json(function_dir / "receipt.json", {}) or {}
                plan = read_json(function_dir / "plan.json", {}) or {}
                if receipt or plan:
                    details = self._function_details(run_dir, function_dir, plan, receipt)
                    function_rows.append({
                        "run_id": run.get("run_id"),
                        "contract_id": plan.get("contract_id", function_dir.name),
                        "function": plan.get("function"),
                        "status": receipt.get("status", "QUEUED"),
                        "stage": next((item.get("stage") for item in jobs if item.get("run_id") == run.get("run_id") and item.get("contract_id") == plan.get("contract_id")), "complete" if receipt else "queued"),
                        "candidate_pass_rate": receipt.get("candidate_pass_rate"),
                        "frame_pass_rate": receipt.get("frame_pass_rate"),
                        "blockers": receipt.get("blockers", []),
                        "model_tier": plan.get("model_tier"),
                        **details,
                    })
        completed = [item for item in function_rows if item.get("status") == "PASS"]
        running = [item for item in jobs if item.get("queue_state") == "running"]
        eta = None
        if completed:
            samples = [float(read_json(self.store.run_dir(str(item["run_id"])) / "functions" / safe_id(str(item["contract_id"])) / "receipt.json", {}).get("duration_seconds", 0)) for item in completed]
            average = sum(samples) / len(samples) if samples else 0
            remaining = counts["pending"] + counts["running"]
            eta = round(average * remaining / max(1, int(os.environ.get("DSC_REGRESSION_WORKERS", "1"))), 1)
        return {
            "schema_version": 1,
            "generated_at": utc_now(),
            "root": str(self.store.root),
            "counts": counts,
            "jobs": jobs,
            "functions": function_rows,
            "failure_buckets": self.failure_buckets(function_rows),
            "eta_seconds": eta,
            "eta_basis": "completed samples" if eta is not None else None,
        }

    @staticmethod
    def failure_buckets(rows: list[dict[str, Any]]) -> dict[str, int]:
        buckets: dict[str, int] = {}
        for row in rows:
            for blocker in row.get("blockers", []) or []:
                key = str(blocker).split(":", 1)[0]
                buckets[key] = buckets.get(key, 0) + 1
        return dict(sorted(buckets.items()))

    def refresh_dashboard(self) -> dict[str, Any]:
        self.store.ensure_layout()
        latest = self.snapshot()
        atomic_write_json(self.store.dashboard / "latest.json", redact(latest))
        html = self.dashboard_html()
        atomic_write_bytes(self.store.dashboard / "index.html", html.encode("utf-8"))
        return latest

    @staticmethod
    def dashboard_html() -> str:
        return """<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>DSC Regression Dashboard</title><style>
body{font:14px system-ui,sans-serif;margin:24px;background:#f6f7fb;color:#172033}main{max-width:1400px;margin:auto}h1{margin-bottom:4px}.muted{color:#667085}.cards{display:flex;gap:12px;flex-wrap:wrap;margin:18px 0}.card{background:#fff;border:1px solid #d9deea;border-radius:10px;padding:14px 18px;min-width:130px}.ok{color:#087443}.bad{color:#b42318}table{width:100%;border-collapse:collapse;background:#fff}th,td{border-bottom:1px solid #e5e7eb;text-align:left;padding:9px;vertical-align:top}th{background:#eef2f8}select{padding:6px;margin-right:8px}.bar{height:8px;background:#e6eaf1;border-radius:8px;overflow:hidden}.fill{height:100%;background:#2e90fa}.small{font-size:12px}</style></head>
<body><main><h1>DSC per-function regression</h1><div id="meta" class="muted">Loading latest.json…</div><section id="cards" class="cards"></section>
<p><label>Status <select id="status"><option value="">all</option></select></label><label>Function <select id="function"><option value="">all</option></select></label><label>Model tier <select id="tier"><option value="">all</option></select></label><label>Stage <select id="stage"><option value="">all</option></select></label></p>
<table><thead><tr><th>Run / contract</th><th>Function</th><th>Status</th><th>Stage</th><th>Candidate pass</th><th>Frame pass</th><th>Blockers</th><th>Details / links</th></tr></thead><tbody id="rows"></tbody></table></main>
<script>
let data={}; const $=id=>document.getElementById(id); const esc=x=>String(x??'').replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
function options(id,values){const e=$(id),current=e.value; e.innerHTML='<option value="">all</option>'+values.sort().map(v=>'<option>'+esc(v)+'</option>').join('');e.value=current;}
function links(items){return (items||[]).map(x=>x.href?'<a href="'+esc(x.href)+'">'+esc(x.label||x.anchor_id||'link')+'</a>':esc(x.label||x.anchor_id||'link')).join(' · ')}
function details(x){const d=x||{};return '<details><summary>inspect</summary><div class="small">'+links(d.artifact_links)+'<br>'+links((d.spec_links||[]).map(y=>({href:y.href,label:(y.anchor_id||'spec')+(y.page?' p'+y.page:'')})))+'</div><pre class="small">'+esc(JSON.stringify({vectors:d.vectors,shards:d.shards,candidates:d.candidates,counterexamples:d.counterexamples,frames:d.frames,c_source_link:d.c_source_link,traceability:d.traceability},null,2))+'</pre></details>'}
function render(){const rows=data.functions||[];options('status',[...new Set(rows.map(x=>x.status).filter(Boolean))]);options('function',[...new Set(rows.map(x=>x.function).filter(Boolean))]);options('tier',[...new Set(rows.map(x=>x.model_tier).filter(Boolean))]);options('stage',[...new Set(rows.map(x=>x.stage).filter(Boolean))]);const filtered=rows.filter(x=>(!$('status').value||x.status===$('status').value)&&(!$('function').value||x.function===$('function').value)&&(!$('tier').value||x.model_tier===$('tier').value)&&(!$('stage').value||x.stage===$('stage').value));$('rows').innerHTML=filtered.map(x=>'<tr><td>'+esc(x.run_id)+'<br><span class="small">'+esc(x.contract_id)+'</span></td><td>'+esc(x.function)+'</td><td class="'+(x.status==='PASS'?'ok':'bad')+'">'+esc(x.status)+'</td><td>'+esc(x.stage)+'</td><td>'+esc(x.candidate_pass_rate)+'</td><td>'+esc(x.frame_pass_rate)+'</td><td>'+esc((x.blockers||[]).join(', '))+'</td><td>'+details(x)+'</td></tr>').join('');const c=data.counts||{};$('cards').innerHTML=['pending','running','done','failed'].map(k=>'<div class="card"><div class="muted">'+k+'</div><strong>'+esc(c[k]||0)+'</strong></div>').join('')+'<div class="card"><div class="muted">ETA</div><strong>'+esc(data.eta_seconds==null?'—':data.eta_seconds+'s')+'</strong><div class="small">'+esc(data.eta_basis||'not enough samples')+'</div></div>';$('meta').textContent='Updated '+(data.generated_at||'')+' · auto-refresh 5s · '+filtered.length+'/'+rows.length+' functions';}
async function load(){try{data=await fetch('latest.json?ts='+Date.now()).then(r=>r.json());render()}catch(e){$('meta').textContent='latest.json unavailable: '+e}}['status','function','tier','stage'].forEach(id=>$(id).addEventListener('change',render));load();setInterval(load,5000);
</script></body></html>"""

    def report(self, run_id: str) -> dict[str, Any]:
        run_dir = self.store.run_dir(run_id)
        if not run_dir.is_dir():
            raise FileNotFoundError(run_id)
        run = read_json(run_dir / "run.json", {}) or {}
        functions = []
        for function_dir in sorted((run_dir / "functions").iterdir() if (run_dir / "functions").is_dir() else []):
            receipt = read_json(function_dir / "receipt.json", {}) or {}
            if receipt:
                functions.append(receipt)
        report = {"schema_version": 1, "run": run, "functions": functions, "scale_plan": read_json(run_dir / "scale-plan.json", None)}
        atomic_write_json(run_dir / "report.json", redact(report))
        self.refresh_dashboard()
        return report


def print_json(value: Any) -> None:
    print(json.dumps(redact(value), indent=2, sort_keys=True, ensure_ascii=False))


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Durable SMB-backed DSC per-function regression service")
    sub = parser.add_subparsers(dest="command", required=True)
    sub.add_parser("init")
    submit = sub.add_parser("submit")
    submit.add_argument("--profile", choices=("pilot",), required=True)
    worker = sub.add_parser("worker")
    worker.add_argument("--jobs", type=int, default=1)
    poll = sub.add_parser("poll")
    group = poll.add_mutually_exclusive_group()
    group.add_argument("--once", action="store_true")
    group.add_argument("--watch", type=int)
    resume = sub.add_parser("resume")
    resume.add_argument("run_id")
    report = sub.add_parser("report")
    report.add_argument("run_id")
    scale = sub.add_parser("scale")
    scale.add_argument("run_id")
    scale.add_argument("--refresh", action="store_true", help="force a fresh generator/model pass even when a verified cache exists")
    promote = sub.add_parser("promote")
    promote.add_argument("run_id")
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    try:
        root, _ = validate_regression_root()
        service = RegressionService(DurableStore(root), REPO_ROOT)
        if args.command == "init":
            print_json(service.init())
            return 0
        if args.command == "submit":
            print_json(service.submit(args.profile))
            return 0
        if args.command == "worker":
            print_json(service.worker(args.jobs))
            return 0
        if args.command == "poll":
            if args.watch is not None:
                deadline = epoch_now() + max(0, args.watch)
                while True:
                    print_json(service.refresh_dashboard())
                    remaining = deadline - epoch_now()
                    if remaining <= 0:
                        break
                    time.sleep(min(5, remaining))
            else:
                print_json(service.refresh_dashboard())
            return 0
        if args.command == "resume":
            run_dir = service.store.run_dir(args.run_id)
            if not run_dir.is_dir():
                raise FileNotFoundError(args.run_id)
            resumed = []
            for queue_state in ("failed", "done"):
                queue_root = service.store.queue / queue_state
                for failed in sorted(queue_root.iterdir() if queue_root.exists() else []):
                    if not failed.is_dir() or failed.name.startswith("."):
                        continue
                    job = read_json(failed / "job.json", {}) or {}
                    if job.get("run_id") != args.run_id:
                        continue
                    receipt_path = service.store.run_dir(args.run_id) / "functions" / safe_id(str(job.get("contract_id"))) / "receipt.json"
                    receipt = read_json(receipt_path, {}) or {}
                    if queue_state == "done" and receipt.get("status") == "PASS":
                        continue
                    resume_lock = failed / ".resume"
                    try:
                        resume_lock.mkdir()
                    except FileExistsError:
                        continue
                    job["attempt"] = int(job.get("attempt", 0)) + 1
                    job["resumed_at"] = utc_now()
                    target = service.store.queue / "pending" / failed.name
                    if target.exists():
                        target = service.store.queue / "pending" / f"{failed.name}-retry-{job['attempt']}"
                    try:
                        atomic_write_json(failed / "job.json", redact(job))
                        claim = failed / ".claim"
                        if claim.exists():
                            shutil.rmtree(claim)
                        service.store.write_status(failed, status="queued", stage="resumed", last_error=None, progress={"completed": 0, "total": len(STAGES), "unit": "stages"})
                        service.store.record_strategy(args.run_id, {"event": "resume", "decision": "requeue", "job_id": job.get("job_id"), "attempt": job["attempt"], "rationale": "manual resume after inspecting failed receipt"})
                        # Remove the per-job resume lock before moving the
                        # directory.  Otherwise a worker that fails again
                        # carries the lock into queue/failed and blocks the
                        # next deliberate resume forever.
                        resume_lock.rmdir()
                        os.replace(failed, target)
                        resumed.append(job.get("job_id"))
                    finally:
                        try:
                            resume_lock.rmdir()
                        except OSError:
                            pass
            print_json({"run_id": args.run_id, "resumed": resumed})
            return 0
        if args.command == "report":
            print_json(service.report(args.run_id))
            return 0
        if args.command == "scale":
            print_json(service.start_scale(args.run_id, refresh=args.refresh))
            return 0
        if args.command == "promote":
            print_json(service.promote_library(args.run_id))
            return 0
        raise ValueError(args.command)
    except (InfrastructureFailure, FileNotFoundError, OSError, ValueError) as error:
        print_json({"status": "INFRASTRUCTURE_FAILURE", "error": str(error)})
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
