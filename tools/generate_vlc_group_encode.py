#!/usr/bin/env python3
"""Generate a bounded, encoder-only RTL boundary for the discovered VLC group.

The source function is selected from Encode coverage and structural facts.  Its
spelling is retained as traceability only; it is never an admission predicate.
The generated module is an intentionally externalized parent transition.  The
VLCUnit and ProcessGroupEnc candidates are pinned by their provisional contract
and candidate-module bytes, while the adapter owns their transaction-level
state snapshots and bounded FIFO/frame events.  This keeps the artifact
deterministic and synthesizable without claiming that an unavailable child
candidate has been inlined or promoted.
"""

from __future__ import annotations

import argparse
import copy
import hashlib
import json
import pathlib
import re
from dataclasses import dataclass
from typing import Any, Iterable, Mapping, Sequence


MAX_SSPS = 4
MIN_SSPS = 3
MAX_UNITS = 4
MIN_UNITS = 3
MUX_WORD_SIZES = (48, 64)
MAX_SE_SIZE = 68
FIFO_ADDR_WIDTH = 16
FRAME_ADDR_WIDTH = 32
MAX_CYCLES = 4096
SAMPLES_PER_UNIT = 3

FIFO_FIELDS = (
    "size_bits",
    "fullness",
    "read_ptr",
    "write_ptr",
    "max_fullness",
    "byte_ctr",
)
FIFO_PREFIXES = ("enc_balance", "shifter", "se_size")
CHILD_ROLES = ("vlc_unit", "process_group")


class DiscoveryError(RuntimeError):
    """Raised when target or child discovery is incomplete or ambiguous."""


def _read_json(path: pathlib.Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def _write_json(path: pathlib.Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(value, indent=2, sort_keys=True, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )


def _sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def _sha256_text(value: str) -> str:
    return _sha256_bytes(value.encode("utf-8"))


def _sha256_file(path: pathlib.Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def _rows(document: Any, key: str | None = None) -> list[dict[str, Any]]:
    if isinstance(document, list):
        return [item for item in document if isinstance(item, dict)]
    if not isinstance(document, dict):
        return []
    value = document.get(key, []) if key else document
    if isinstance(value, list):
        return [item for item in value if isinstance(item, dict)]
    return []


def _normal_type(value: Any) -> str:
    return re.sub(r"\s+", " ", str(value or "").strip())


def _parameter_types(function: Mapping[str, Any]) -> list[str]:
    return [_normal_type(item.get("type")) for item in function.get("parameters", []) or []]


def _field_names(function: Mapping[str, Any], key: str, record: str | None = None) -> set[str]:
    result: set[str] = set()
    for item in function.get(key, []) or []:
        if not isinstance(item, dict):
            continue
        if record is not None and str(item.get("record")) != record:
            continue
        if item.get("name"):
            result.add(str(item["name"]))
    return result


def _callee_usrs(function: Mapping[str, Any]) -> set[str]:
    result: set[str] = set()
    for key in ("calls", "callees"):
        for item in function.get(key, []) or []:
            if isinstance(item, dict) and item.get("clang_usr"):
                result.add(str(item["clang_usr"]))
    return result


def _covered_row(row: Mapping[str, Any]) -> tuple[bool, int]:
    nested = row.get("coverage", {})
    coverage = nested if isinstance(nested, dict) else {}
    count = int(
        coverage.get(
            "execution_count",
            row.get("execution_count", row.get("encode_execution_count", 0)),
        )
        or 0
    )
    covered = coverage.get("covered", row.get("covered", count > 0))
    return bool(covered) and count > 0, count


def _coverage_by_usr(*documents: Any) -> dict[str, tuple[bool, int, dict[str, Any]]]:
    """Index coverage, keeping the first document authoritative per USR."""

    result: dict[str, tuple[bool, int, dict[str, Any]]] = {}
    for document in documents:
        rows: list[dict[str, Any]] = []
        if isinstance(document, dict):
            rows.extend(_rows(document, "functions"))
            for key in ("reached", "rtl", "compute_gap", "c_shell"):
                rows.extend(_rows(document, key))
        else:
            rows.extend(_rows(document))
        for row in rows:
            usr = row.get("clang_usr")
            if not usr or str(usr) in result:
                continue
            covered, count = _covered_row(row)
            result[str(usr)] = (covered, count, row)
    return result


def _source_text(source_dir: pathlib.Path, function: Mapping[str, Any]) -> str:
    source_name = str(function.get("source_file", ""))
    source = pathlib.Path(source_name)
    if not source.is_absolute():
        source = source_dir / source
    if not source.is_file():
        raise DiscoveryError(f"source file is missing: {source}")
    lines = source.read_text(encoding="utf-8", errors="replace").splitlines()
    span = function.get("source_span", {})
    start = int(span.get("start_line", function.get("line", 0)) or 0)
    end = int(span.get("end_line", function.get("end_line", 0)) or 0)
    if start <= 0 or end < start or end > len(lines):
        raise DiscoveryError(
            f"invalid source span for {function.get('clang_usr')}: {start}..{end}"
        )
    return "\n".join(lines[start - 1 : end])


def source_body_sha256(source_dir: pathlib.Path, function: Mapping[str, Any]) -> str:
    return _sha256_text(_source_text(source_dir, function))


def _merge_fact_documents(
    functions_document: Any,
    *,
    loops_document: Any | None = None,
    field_access_document: Any | None = None,
    value_ranges_document: Any | None = None,
) -> list[dict[str, Any]]:
    """Merge optional fact exports without changing the canonical function rows."""

    base_rows = _rows(functions_document, "functions")
    by_usr = {
        str(row.get("clang_usr")): copy.deepcopy(row)
        for row in base_rows
        if row.get("clang_usr")
    }
    for document in (loops_document, field_access_document, value_ranges_document):
        if document is None:
            continue
        candidates = _rows(document, "functions")
        if isinstance(document, dict):
            candidates.extend(_rows(document, "fields"))
        for row in candidates:
            usr = row.get("clang_usr")
            if not usr or str(usr) not in by_usr:
                continue
            destination = by_usr[str(usr)]
            if "loops" in row:
                destination["loops"] = copy.deepcopy(row["loops"])
                destination["loop_count"] = int(row.get("loop_count", len(row["loops"])))
            for key in ("fields_read", "fields_write", "value_ranges", "eva_checks"):
                if key in row:
                    destination[key] = copy.deepcopy(row[key])
    return list(by_usr.values())


def _is_vlc_unit_shape(function: Mapping[str, Any]) -> bool:
    types = _parameter_types(function)
    if _normal_type(function.get("return_type")) != "void" or len(types) != 5:
        return False
    if types.count("dsc_cfg_t *") != 1 or types.count("dsc_state_t *") != 1:
        return False
    if "int *" not in types or types.count("int") < 2:
        return False
    reads = _field_names(function, "fields_read", "dsc_state_t")
    writes = _field_names(function, "fields_write", "dsc_state_t")
    return (
        bool({"quantizedResidual", "quantizedResidualMid"}.intersection(reads))
        and {"groupCount", "unitCType"}.issubset(reads)
        and bool({"rcSizeUnit", "predictedSize", "midpointSelected"}.intersection(writes))
    )


def _is_process_group_shape(function: Mapping[str, Any]) -> bool:
    types = _parameter_types(function)
    if types != ["dsc_cfg_t *", "dsc_state_t *", "unsigned char *"]:
        return False
    if _normal_type(function.get("return_type")) != "void":
        return False
    if int(function.get("loop_count", 0) or 0) < 2:
        return False
    reads = _field_names(function, "fields_read", "dsc_state_t")
    config_reads = _field_names(function, "fields_read", "dsc_cfg_t")
    return {
        "encBalanceFifo",
        "seSizeFifo",
        "shifter",
        "numSsps",
        "maxSeSize",
    }.issubset(reads) and "mux_word_size" in config_reads


def _is_fifo_put_shape(function: Mapping[str, Any]) -> bool:
    types = _parameter_types(function)
    if _normal_type(function.get("return_type")) != "void" or len(types) != 3:
        return False
    if types[0] != "fifo_t *" or types[1] not in {"unsigned int", "unsigned"}:
        return False
    if types[2] not in {"int", "signed int"}:
        return False
    return {"fullness", "write_ptr"}.issubset(_field_names(function, "fields_write"))


def _call_role_lines(
    function: Mapping[str, Any], functions_by_usr: Mapping[str, Mapping[str, Any]]
) -> dict[str, list[int]]:
    result = {"vlc_unit": [], "process_group": [], "fifo_put": []}
    for item in function.get("calls", []) or []:
        if not isinstance(item, dict):
            continue
        callee = functions_by_usr.get(str(item.get("clang_usr", "")), {})
        line = int((item.get("location", {}) or {}).get("line", 0) or 0)
        if _is_vlc_unit_shape(callee):
            result["vlc_unit"].append(line)
        if _is_process_group_shape(callee):
            result["process_group"].append(line)
        if _is_fifo_put_shape(callee):
            result["fifo_put"].append(line)
    return result


def _structural_target_score(
    function: Mapping[str, Any],
    functions_by_usr: Mapping[str, Mapping[str, Any]],
    source_dir: pathlib.Path,
    candidate_record: Mapping[str, Any] | None = None,
) -> tuple[int, list[str], dict[str, list[int]]]:
    reasons: list[str] = []
    score = 0
    types = _parameter_types(function)
    if _normal_type(function.get("return_type")) != "void" or len(types) != 4:
        return -1, reasons, {}
    if types.count("dsc_cfg_t *") != 1 or types.count("dsc_state_t *") != 1:
        return -1, reasons, {}
    if "unsigned char **" not in types or types.count("int") != 1:
        return -1, reasons, {}
    score += 10
    reasons.append("void-four-parameter-config-state-output-pointer-signature")

    loops = function.get("loops", []) or []
    conditions = [str(item.get("condition", "")) for item in loops if isinstance(item, dict)]
    if int(function.get("loop_count", 0) or 0) >= 7:
        score += 5
        reasons.append("seven-source-loop-facts")
    if sum("unitsPerGroup" in condition for condition in conditions) >= 3:
        score += 5
        reasons.append("units-per-group-loop-bound")
    if sum("numSsps" in condition for condition in conditions) >= 3:
        score += 5
        reasons.append("ssp-loop-bound")

    state_reads = _field_names(function, "fields_read", "dsc_state_t")
    config_reads = _field_names(function, "fields_read", "dsc_cfg_t")
    state_writes = _field_names(function, "fields_write", "dsc_state_t")
    required_state_reads = {
        "bufferFullness",
        "encBalanceFifo",
        "groupCount",
        "maxSeSize",
        "numBits",
        "numBitsChunk",
        "numSsps",
        "pixelCount",
        "pixelsInGroup",
        "prevNumBits",
        "primaryQp",
        "quantizedResidual",
        "seSizeFifo",
        "sliceWidth",
        "unitsPerGroup",
    }
    required_config_reads = {
        "bits_per_component",
        "bits_per_pixel",
        "chunk_size",
        "initial_xmit_delay",
        "mux_word_size",
        "rcb_bits",
        "vbr_enable",
    }
    required_writes = {
        "bufferFullness",
        "codedGroupSize",
        "forceMpp",
        "groupCountLine",
        "midpointSelected",
        "prevNumBits",
        "prevPrimaryQp",
    }
    state_hits = required_state_reads.intersection(state_reads)
    config_hits = required_config_reads.intersection(config_reads)
    write_hits = required_writes.intersection(state_writes)
    score += len(state_hits) + len(config_hits) + len(write_hits)
    reasons.extend(f"state-read:{field}" for field in sorted(state_hits))
    reasons.extend(f"config-read:{field}" for field in sorted(config_hits))
    reasons.extend(f"state-write:{field}" for field in sorted(write_hits))
    if not required_state_reads.issubset(state_reads):
        return -1, reasons, {}
    if not required_config_reads.issubset(config_reads):
        return -1, reasons, {}
    if not required_writes.issubset(state_writes):
        return -1, reasons, {}

    role_lines = _call_role_lines(function, functions_by_usr)
    if len(role_lines["vlc_unit"]) < 2:
        return -1, reasons, role_lines
    if not role_lines["process_group"] or not role_lines["fifo_put"]:
        return -1, reasons, role_lines
    first_unit = min(role_lines["vlc_unit"])
    first_fifo = min(role_lines["fifo_put"])
    first_process = min(role_lines["process_group"])
    if not first_unit < first_fifo < first_process:
        return -1, reasons, role_lines
    score += 16
    reasons.append("source-order-unit-then-se-size-fifo-then-process-group")
    if max(role_lines["process_group"]) < min(
        line
        for item in function.get("fields_write", []) or []
        if isinstance(item, dict)
        for line in [int((item.get("location", {}) or {}).get("line", 0) or 0)]
        if line > 0 and item.get("name") == "bufferFullness"
    ):
        score += 4
        reasons.append("completion-accounting-after-process-group")

    body = _source_text(source_dir, function)
    source_markers = (
        "dsc_state->prevNumBits",
        "dsc_state->forceMpp",
        "dsc_state->seSizeFifo",
        "dsc_state->numBits",
        "dsc_state->bufferFullness",
        "dsc_state->codedGroupSize",
        "dsc_state->groupCountLine",
    )
    if not all(marker in body for marker in source_markers):
        return -1, reasons, role_lines
    score += 14
    reasons.append("source-state-effects-and-completion-markers")
    if "if(0)" in body or "if (0)" in body:
        score += 2
        reasons.append("native-422-branch-is-source-disabled")
    if candidate_record and candidate_record.get("contributes_to_observable_output"):
        score += 2
        reasons.append("candidate-observable-output-fact")
    return score, reasons, role_lines


def discover_vlc_group_candidate(
    functions_document: Any,
    coverage_document: Any,
    source_dir: pathlib.Path,
    *,
    encode_frontier_document: Any | None = None,
    loops_document: Any | None = None,
    field_access_document: Any | None = None,
    value_ranges_document: Any | None = None,
    candidates_document: Any | None = None,
) -> dict[str, Any]:
    """Select the unique positive Encode VLC-group compute boundary."""

    functions = _merge_fact_documents(
        functions_document,
        loops_document=loops_document,
        field_access_document=field_access_document,
        value_ranges_document=value_ranges_document,
    )
    functions_by_usr = {
        str(item.get("clang_usr")): item
        for item in functions
        if item.get("clang_usr")
    }
    candidate_by_usr = {
        str(item.get("clang_usr")): item
        for item in _rows(candidates_document, "functions")
        if item.get("clang_usr")
    }
    coverage = _coverage_by_usr(coverage_document, encode_frontier_document)
    matches: list[dict[str, Any]] = []
    for function in functions:
        usr = str(function.get("clang_usr", ""))
        covered, execution_count, coverage_row = coverage.get(usr, (False, 0, {}))
        if not covered or execution_count <= 0:
            continue
        score, reasons, role_lines = _structural_target_score(
            function,
            functions_by_usr,
            source_dir,
            candidate_by_usr.get(usr),
        )
        if score >= 0:
            matches.append(
                {
                    "function": function,
                    "coverage": coverage_row,
                    "execution_count": execution_count,
                    "score": score,
                    "reasons": reasons,
                    "role_lines": role_lines,
                }
            )
    if not matches:
        raise DiscoveryError("Encode coverage contains no structural VLCGroup target")
    matches.sort(
        key=lambda item: (
            -int(item["score"]),
            -int(item["execution_count"]),
            str(item["function"].get("clang_usr", "")),
        )
    )
    if len(matches) > 1 and matches[0]["score"] == matches[1]["score"]:
        usrs = [str(item["function"].get("clang_usr")) for item in matches]
        raise DiscoveryError(f"ambiguous structural Encode VLCGroup targets: {usrs}")
    selected = matches[0]
    function = selected["function"]
    return {
        "clang_usr": function.get("clang_usr"),
        "name": function.get("name"),
        "source_file": function.get("source_file"),
        "source_span": {
            "start_line": int(function.get("line", 0) or 0),
            "end_line": int(function.get("end_line", 0) or 0),
        },
        "source_body_sha256": source_body_sha256(source_dir, function),
        "execution_count": selected["execution_count"],
        "structural_score": selected["score"],
        "structural_evidence": selected["reasons"],
        "source_order_evidence": selected["role_lines"],
        "coverage": selected["coverage"],
        "function": function,
    }


@dataclass(frozen=True)
class ChildPin:
    role: str
    artifact_path: str
    contract_path: str
    module_path: str
    contract_sha256: str
    module_sha256: str
    contract_id: str
    module: str
    semantic_kind: str
    function: dict[str, Any]
    source_file_sha256: str | None

    @property
    def kind(self) -> str:
        return self.semantic_kind

    @property
    def clang_usr(self) -> str:
        return str(self.function.get("clang_usr", ""))

    @property
    def function_name(self) -> str:
        return str(self.function.get("name", ""))

    @property
    def source_file(self) -> str:
        return str(self.function.get("source_file", ""))

    @property
    def source_span(self) -> dict[str, Any]:
        return dict(self.function.get("source_span", {}) or {})

    @property
    def source_body_sha256(self) -> str:
        return str(self.function.get("source_body_sha256", ""))

    def as_dict(self) -> dict[str, Any]:
        function = copy.deepcopy(self.function)
        function["source_file_sha256"] = self.source_file_sha256
        return {
            "role": self.role,
            "artifact_path": self.artifact_path,
            "contract_file": self.contract_path,
            "module_file": self.module_path,
            "contract_sha256": self.contract_sha256,
            "module_sha256": self.module_sha256,
            "contract_id": self.contract_id,
            "module": self.module,
            "semantic_kind": self.semantic_kind,
            "function": function,
            "composition": {
                "status": "EXTERNALIZED_CHILD_BOUNDARY",
                "module_embedded_in_parent": False,
                "state_and_memory_adapter_required": True,
            },
        }


def _default_source_dir(root: pathlib.Path) -> pathlib.Path:
    receipt_path = root / "facts" / "build-receipt.json"
    if receipt_path.is_file():
        receipt = _read_json(receipt_path)
        model_root = receipt.get("model_root")
        if model_root:
            source = pathlib.Path(str(model_root)) / "source"
            if source.is_dir():
                return source
    compile_commands = root / "facts" / "compile_commands.json"
    if compile_commands.is_file():
        for row in _read_json(compile_commands):
            directory = row.get("directory") if isinstance(row, dict) else None
            if directory and (pathlib.Path(directory) / "dsc_codec.c").is_file():
                return pathlib.Path(directory)
    raise DiscoveryError("cannot locate immutable DSC source directory")


def _resolve_path(value: pathlib.Path, base: pathlib.Path) -> pathlib.Path:
    path = value
    if not path.is_absolute():
        path = base / path
    return path.resolve()


def _module_name(module_path: pathlib.Path, contract: Mapping[str, Any]) -> str:
    expected = str(
        (contract.get("rtl", {}) or {}).get(
            "module",
            (contract.get("interface", {}) or {}).get("module", ""),
        )
    )
    text = module_path.read_text(encoding="utf-8", errors="replace")
    found = re.search(r"\bmodule\s+([A-Za-z_][A-Za-z0-9_]*)\b", text)
    if not found:
        raise DiscoveryError(f"child module has no SystemVerilog module declaration: {module_path}")
    actual = found.group(1)
    if expected and actual != expected:
        raise DiscoveryError(
            f"child module name mismatch for {module_path}: contract={expected}, source={actual}"
        )
    return actual


def _artifact_paths(value: pathlib.Path, root: pathlib.Path) -> tuple[pathlib.Path, pathlib.Path, pathlib.Path]:
    """Resolve a directory, contract, module, or simple artifact descriptor."""

    original = _resolve_path(value, root)
    if not original.exists():
        raise DiscoveryError(f"explicit child artifact does not exist: {original}")
    if original.is_dir():
        contract_path = original / "provisional-contract.json"
        module_candidates = (
            original / "candidate_01.sv",
            original / "candidate.sv",
            original / "module.sv",
        )
        module_path = next((item for item in module_candidates if item.is_file()), None)
        if not contract_path.is_file() or module_path is None:
            raise DiscoveryError(
                f"child artifact directory must contain provisional-contract.json and candidate_01.sv: {original}"
            )
        return original, contract_path, module_path
    if original.suffix.lower() == ".sv":
        contract_path = original.parent / "provisional-contract.json"
        if not contract_path.is_file():
            raise DiscoveryError(f"child module has no sibling provisional contract: {original}")
        return original.parent, contract_path, original
    if original.suffix.lower() == ".json":
        document = _read_json(original)
        if "contract_id" in document and "interface" in document:
            contract_path = original
            module_value = (document.get("rtl", {}) or {}).get("candidate_file")
            if not module_value:
                module_value = (document.get("rtl", {}) or {}).get("module_file")
            candidates = []
            if module_value:
                candidates.append(_resolve_path(pathlib.Path(str(module_value)), original.parent))
            candidates.extend(
                [
                    original.parent / "candidate_01.sv",
                    original.parent / "candidate.sv",
                    original.parent / "module.sv",
                ]
            )
            module_path = next((item for item in candidates if item.is_file()), None)
            if module_path is None:
                raise DiscoveryError(f"child contract has no candidate module beside it: {original}")
            return original.parent, contract_path, module_path
        contract_value = document.get("contract_file") or document.get("contract_path")
        module_value = (
            document.get("module_file")
            or document.get("candidate_file")
            or document.get("module_path")
        )
        if not contract_value or not module_value:
            raise DiscoveryError(f"unsupported child artifact descriptor: {original}")
        contract_path = _resolve_path(pathlib.Path(str(contract_value)), original.parent)
        module_path = _resolve_path(pathlib.Path(str(module_value)), original.parent)
        if not contract_path.is_file() or not module_path.is_file():
            raise DiscoveryError(f"child descriptor points to missing files: {original}")
        return original.parent, contract_path, module_path
    raise DiscoveryError(f"unsupported child artifact path: {original}")


def _child_text(contract: Mapping[str, Any]) -> str:
    semantics = contract.get("semantics", {}) or {}
    function = contract.get("function", {}) or {}
    return " ".join(
        str(value).lower()
        for value in (
            semantics.get("kind", ""),
            contract.get("contract_id", ""),
            contract.get("origin", ""),
            function.get("source_file", ""),
        )
    )


def _looks_like_child_contract(contract: Mapping[str, Any], role: str) -> bool:
    function = contract.get("function", {}) or {}
    semantics = contract.get("semantics", {}) or {}
    kind = str(semantics.get("kind", "")).lower()
    text = _child_text(contract)
    ports = {
        str(item.get("name"))
        for item in (contract.get("interface", {}) or {}).get("ports", []) or []
        if isinstance(item, dict) and item.get("name")
    }
    if role == "vlc_unit":
        return (
            ("vlc" in text and "unit" in text and ("encode" in text or "encoder" in text))
            or (
                _is_vlc_unit_shape(function)
                and "domain_valid" in ports
                and bool(ports.intersection({"num_bits_out", "state_num_bits_out", "fifo_fullness_out"}))
            )
        )
    if role == "process_group":
        return (
            ("process" in text and "group" in text and ("encode" in text or "encoder" in text))
            or (
                _is_process_group_shape(function)
                and "frame_mem_write_req" in ports
                and "post_mux_num_bits_out" in ports
            )
        )
    return False


def _pin_child(
    role: str,
    artifact: pathlib.Path,
    root: pathlib.Path,
    source_dir: pathlib.Path,
) -> ChildPin:
    artifact_path, contract_path, module_path = _artifact_paths(artifact, root)
    raw_contract = contract_path.read_bytes()
    contract = json.loads(raw_contract.decode("utf-8"))
    if not _looks_like_child_contract(contract, role):
        kind = (contract.get("semantics", {}) or {}).get("kind")
        raise DiscoveryError(
            f"child artifact {contract_path} does not satisfy structural {role} contract (kind={kind!r})"
        )
    module = _module_name(module_path, contract)
    expected_candidate_hash = str((contract.get("rtl", {}) or {}).get("candidate_sha256", ""))
    module_hash = _sha256_file(module_path)
    if expected_candidate_hash and expected_candidate_hash != module_hash:
        raise DiscoveryError(
            f"child candidate hash mismatch for {module_path}: "
            f"contract={expected_candidate_hash}, actual={module_hash}"
        )
    function = copy.deepcopy(contract.get("function", {}) or {})
    source_name = str(function.get("source_file", ""))
    source_path = pathlib.Path(source_name)
    if not source_path.is_absolute():
        source_path = source_dir / source_path
    source_file_hash: str | None = None
    if source_path.is_file():
        source_file_hash = _sha256_file(source_path)
        expected_body_hash = str(function.get("source_body_sha256", ""))
        if expected_body_hash:
            try:
                actual_body_hash = source_body_sha256(source_dir, function)
            except DiscoveryError as exc:
                raise DiscoveryError(f"cannot verify child source span for {contract_path}: {exc}") from exc
            if actual_body_hash != expected_body_hash:
                raise DiscoveryError(
                    f"child source-body hash mismatch for {contract_path}: "
                    f"contract={expected_body_hash}, actual={actual_body_hash}"
                )
    elif function.get("source_file_sha256"):
        raise DiscoveryError(f"child source file is missing for recorded hash: {source_path}")
    return ChildPin(
        role=role,
        artifact_path=str(artifact_path),
        contract_path=str(contract_path),
        module_path=str(module_path),
        contract_sha256=_sha256_bytes(raw_contract),
        module_sha256=module_hash,
        contract_id=str(contract.get("contract_id", "")),
        module=module,
        semantic_kind=str((contract.get("semantics", {}) or {}).get("kind", "")),
        function=function,
        source_file_sha256=source_file_hash,
    )


def _candidate_artifact_paths(root: pathlib.Path) -> list[pathlib.Path]:
    paths = list(root.glob("rtl/**/provisional-contract.json"))
    paths.extend(root.glob("artifacts/**/provisional-contract.json"))
    return sorted({path.resolve() for path in paths if path.is_file()})


def discover_dependency_pins(
    root: pathlib.Path,
    source_dir: pathlib.Path | None = None,
    *,
    vlc_unit_artifact: pathlib.Path | None = None,
    process_group_artifact: pathlib.Path | None = None,
    child_artifacts: Mapping[str, pathlib.Path] | None = None,
    contract_paths: Sequence[pathlib.Path] | None = None,
) -> dict[str, ChildPin]:
    """Resolve both child artifacts by semantic shape and hash-pin their bytes."""

    root = root.resolve()
    source_dir = source_dir or _default_source_dir(root)
    explicit: dict[str, pathlib.Path] = {}
    if vlc_unit_artifact is not None:
        explicit["vlc_unit"] = pathlib.Path(vlc_unit_artifact)
    if process_group_artifact is not None:
        explicit["process_group"] = pathlib.Path(process_group_artifact)
    if child_artifacts:
        for role, path in child_artifacts.items():
            if role not in CHILD_ROLES:
                raise DiscoveryError(f"unknown child role: {role}")
            explicit[role] = pathlib.Path(path)
    if contract_paths:
        for raw_path in contract_paths:
            artifact_path, _, _ = _artifact_paths(pathlib.Path(raw_path), root)
            _, contract_path, _ = _artifact_paths(pathlib.Path(raw_path), root)
            contract = _read_json(contract_path)
            matching = [role for role in CHILD_ROLES if _looks_like_child_contract(contract, role)]
            if len(matching) != 1:
                raise DiscoveryError(
                    f"explicit child contract is not uniquely classifiable: {contract_path}"
                )
            explicit[matching[0]] = artifact_path

    pins: dict[str, ChildPin] = {}
    for role in CHILD_ROLES:
        if role in explicit:
            pins[role] = _pin_child(role, explicit[role], root, source_dir)
            continue
        matches: list[ChildPin] = []
        errors: list[str] = []
        for contract_path in _candidate_artifact_paths(root):
            try:
                contract = _read_json(contract_path)
                if not _looks_like_child_contract(contract, role):
                    continue
                matches.append(_pin_child(role, contract_path, root, source_dir))
            except (DiscoveryError, OSError, json.JSONDecodeError) as exc:
                errors.append(str(exc))
        if not matches:
            detail = "; ".join(errors[:2])
            raise DiscoveryError(
                f"missing pinned child artifact for {role}; provide "
                f"--{role.replace('_', '-')}-artifact PATH from "
                f"tools/generate_{role}_encode.py"
                + (f" ({detail})" if detail else "")
            )
        module_hashes = {pin.module_sha256 for pin in matches}
        source_hashes = {pin.function.get("source_body_sha256") for pin in matches}
        if len(module_hashes) != 1 or len(source_hashes) != 1:
            raise DiscoveryError(f"ambiguous hash-pinned child artifacts for {role}")
        matches.sort(key=lambda pin: pin.contract_path)
        pins[role] = matches[0]
    return pins


# Compatibility aliases make the semantic role explicit to callers without
# introducing a second discovery implementation.
discover_child_pins = discover_dependency_pins
resolve_child_pins = discover_dependency_pins


def _port(
    name: str,
    direction: str,
    width: int,
    *,
    signed: bool = False,
    unpacked: str = "",
) -> dict[str, Any]:
    return {
        "name": name,
        "direction": direction,
        "width": int(width),
        "signed": bool(signed),
        "unpacked": unpacked,
    }


def _fifo_port_pair(prefix: str) -> list[dict[str, Any]]:
    ports: list[dict[str, Any]] = []
    for field in FIFO_FIELDS:
        ports.append(_port(f"{prefix}_{field}_in", "input", 32, signed=False, unpacked="[0:3]"))
        ports.append(_port(f"{prefix}_{field}_out", "output", 32, signed=False, unpacked="[0:3]"))
    return ports


def _memory_ports(prefix: str, *, child_role: str | None = None) -> list[dict[str, Any]]:
    if child_role:
        stem = f"{child_role}_{prefix}"
        return [
            _port(f"{stem}_mem_read_req", "input", 4),
            _port(f"{stem}_mem_read_addr", "input", FIFO_ADDR_WIDTH, unpacked="[0:3]"),
            _port(f"{stem}_mem_read_valid", "output", 4),
            _port(f"{stem}_mem_read_data", "output", 8, unpacked="[0:3]"),
            _port(f"{stem}_mem_write_req", "input", 4),
            _port(f"{stem}_mem_write_addr", "input", FIFO_ADDR_WIDTH, unpacked="[0:3]"),
            _port(f"{stem}_mem_write_ready", "output", 4),
            _port(f"{stem}_mem_write_data", "input", 8, unpacked="[0:3]"),
            _port(f"{stem}_mem_write_bit_mask", "input", 8, unpacked="[0:3]"),
        ]
    return [
        _port(f"{prefix}_mem_read_req", "output", 4),
        _port(f"{prefix}_mem_read_addr", "output", FIFO_ADDR_WIDTH, unpacked="[0:3]"),
        _port(f"{prefix}_mem_read_valid", "input", 4),
        _port(f"{prefix}_mem_read_data", "input", 8, unpacked="[0:3]"),
        _port(f"{prefix}_mem_write_req", "output", 4),
        _port(f"{prefix}_mem_write_addr", "output", FIFO_ADDR_WIDTH, unpacked="[0:3]"),
        _port(f"{prefix}_mem_write_ready", "input", 4),
        _port(f"{prefix}_mem_write_data", "output", 8, unpacked="[0:3]"),
        _port(f"{prefix}_mem_write_bit_mask", "output", 8, unpacked="[0:3]"),
    ]


def contract_interface() -> list[dict[str, Any]]:
    """Describe the complete parent/adapter ABI."""

    ports: list[dict[str, Any]] = [
        _port("clk", "input", 1),
        _port("rst_n", "input", 1),
        _port("start", "input", 1),
        _port("is_encoder", "input", 1),
        _port("units_per_group", "input", 3),
        _port("num_ssps", "input", 3),
        _port("mux_word_size", "input", 7),
        _port("bits_per_pixel", "input", 32, signed=True),
        _port("bits_per_component", "input", 6, signed=True),
        _port("chunk_size", "input", 32, signed=True),
        _port("initial_xmit_delay", "input", 32, signed=True),
        _port("vbr_enable", "input", 1),
        _port("rcb_bits", "input", 32, signed=True),
        _port("frame_capacity_bits", "input", 32, signed=False),
        _port("max_se_size", "input", 7, unpacked="[0:3]"),
        _port("busy", "output", 1),
        _port("done", "output", 1),
        _port("domain_valid", "output", 1),
        _port("illegal_domain", "output", 1),
        _port("fatal_error", "output", 1),
        _port("bound_violation", "output", 1),
        _port("child_error", "output", 1),
        _port("fifo_underflow", "output", 1),
        _port("fifo_overflow", "output", 1),
        _port("se_size_overflow", "output", 1),
        _port("buffer_overflow", "output", 1),
        _port("post_mux_num_bits_in", "input", 32),
        _port("post_mux_num_bits_out", "output", 32),
    ]
    scalar_fields = (
        "num_bits",
        "buffer_fullness",
        "num_bits_chunk",
        "pixels_in_group",
        "slice_width",
        "pixel_count",
        "group_count",
        "primary_qp",
        "prev_primary_qp",
        "prev_num_bits",
        "coded_group_size",
        "group_count_line",
        "force_mpp",
    )
    for field in scalar_fields:
        ports.append(_port(f"{field}_in", "input", 32, signed=True))
        ports.append(_port(f"{field}_out", "output", 32, signed=True))
    ports.extend([
        _port("midpoint_selected_in", "input", 32, signed=True, unpacked="[0:3]"),
        _port("midpoint_selected_out", "output", 32, signed=True, unpacked="[0:3]"),
        _port("quantized_residual_in", "input", 32, signed=True, unpacked="[0:3][0:2]"),
        _port("quantized_residual_out", "output", 32, signed=True, unpacked="[0:3][0:2]"),
        _port("quantized_residual_mid_in", "input", 32, signed=True, unpacked="[0:3][0:2]"),
        _port("quantized_residual_mid_out", "output", 32, signed=True, unpacked="[0:3][0:2]"),
    ])
    for prefix in FIFO_PREFIXES:
        ports.extend(_fifo_port_pair(prefix))
        ports.extend(_memory_ports(prefix))

    # The VLCUnit adapter is a transaction-level child boundary.  It returns
    # the complete scalar FIFO snapshot that the parent needs for SE accounting.
    ports.extend([
        _port("vlc_unit_start", "output", 1),
        _port("vlc_unit_ready", "input", 1),
        _port("vlc_unit_done", "input", 1),
        _port("vlc_unit_domain_valid", "input", 1),
        _port("vlc_unit_fatal_error", "input", 1),
        _port("vlc_unit_index", "output", 3),
        _port("vlc_unit_force_p1_ich2", "output", 32, signed=True),
        _port("vlc_unit_num_bits_in", "output", 32, signed=True),
        _port("vlc_unit_num_bits_out", "input", 32, signed=True),
        _port("vlc_unit_primary_qp_in", "output", 32, signed=True),
        _port("vlc_unit_primary_qp_out", "input", 32, signed=True),
    ])
    for prefix in FIFO_PREFIXES:
        for field in FIFO_FIELDS:
            ports.append(_port(f"vlc_unit_{prefix}_{field}_in", "output", 32, unpacked="[0:3]"))
            if prefix == "enc_balance":
                ports.append(_port(f"vlc_unit_{prefix}_{field}_out", "input", 32, unpacked="[0:3]"))
    for prefix in FIFO_PREFIXES:
        ports.extend(_memory_ports(prefix, child_role="vlc_unit"))

    # ProcessGroupEnc is also externalized, but its returned full FIFO image and
    # frame write event are committed only after its done handshake.
    ports.extend([
        _port("process_group_start", "output", 1),
        _port("process_group_ready", "input", 1),
        _port("process_group_done", "input", 1),
        _port("process_group_domain_valid", "input", 1),
        _port("process_group_fatal_error", "input", 1),
        _port("process_group_is_encoder", "output", 1),
        _port("process_group_num_ssps", "output", 3),
        _port("process_group_mux_word_size", "output", 7),
        _port("process_group_frame_capacity_bits", "output", 32),
        _port("process_group_post_mux_num_bits_in", "output", 32),
        _port("process_group_post_mux_num_bits_out", "input", 32),
    ])
    for prefix in FIFO_PREFIXES:
        for field in FIFO_FIELDS:
            ports.append(_port(f"process_group_{prefix}_{field}_in", "output", 32, unpacked="[0:3]"))
            ports.append(_port(f"process_group_{prefix}_{field}_out", "input", 32, unpacked="[0:3]"))
        ports.extend(_memory_ports(prefix, child_role="process_group"))
    ports.extend([
        _port("process_group_frame_mem_write_req", "input", 1),
        _port("process_group_frame_mem_write_addr", "input", FRAME_ADDR_WIDTH),
        _port("process_group_frame_mem_write_ready", "output", 1),
        _port("process_group_frame_mem_write_data", "input", 8),
        _port("process_group_frame_mem_write_bit_mask", "input", 8),
        _port("frame_mem_write_req", "output", 1),
        _port("frame_mem_write_addr", "output", FRAME_ADDR_WIDTH),
        _port("frame_mem_write_ready", "input", 1),
        _port("frame_mem_write_data", "output", 8),
        _port("frame_mem_write_bit_mask", "output", 8),
    ])
    return ports


def _pin_map(pins: Mapping[str, ChildPin] | Iterable[ChildPin]) -> dict[str, ChildPin]:
    if isinstance(pins, Mapping):
        return {str(role): pin for role, pin in pins.items()}
    return {pin.role: pin for pin in pins}


def _pin_record(pin: ChildPin | Mapping[str, Any]) -> dict[str, Any]:
    return pin.as_dict() if isinstance(pin, ChildPin) else copy.deepcopy(dict(pin))


def build_contract(
    candidate: Mapping[str, Any],
    pins: Mapping[str, ChildPin] | Iterable[ChildPin],
    *,
    rtl_sha256: str | None = None,
) -> dict[str, Any]:
    pin_map = _pin_map(pins)
    if set(pin_map) != set(CHILD_ROLES):
        raise DiscoveryError(f"VLCGroup requires child roles {CHILD_ROLES}, got {sorted(pin_map)}")
    function = candidate.get("function", {}) or {}
    function_record = {
        "clang_usr": candidate.get("clang_usr"),
        "name": candidate.get("name"),
        "parameters": function.get("parameters", []),
        "return_type": function.get("return_type"),
        "source_file": candidate.get("source_file"),
        "source_span": candidate.get("source_span"),
        "source_body_sha256": candidate.get("source_body_sha256"),
    }
    dependencies = [_pin_record(pin_map[role]) for role in CHILD_ROLES]
    contract: dict[str, Any] = {
        "schema_version": 1,
        "contract_id": "vlc_group_encode_fsm_v1",
        "status": "PROVISIONAL_SIMULATION_ONLY",
        "origin": "tool_discovered_encode_coverage_structural_sequential_parent",
        "function": function_record,
        "selection": {
            "basis": [
                "positive Encode-phase execution coverage",
                "four-parameter config/state/output-pointer signature",
                "Clang state/config read and write footprint",
                "structural VLCUnit and ProcessGroupEnc callee roles",
                "source-order call locations for units, SE-size FIFO, and mux processing",
                "completion/accounting markers after the child calls",
                "function spelling is traceability only, not an admission predicate",
            ],
            "execution_count": int(candidate.get("execution_count", 0) or 0),
            "structural_score": int(candidate.get("structural_score", 0) or 0),
            "structural_evidence": candidate.get("structural_evidence", []),
            "source_order_evidence": candidate.get("source_order_evidence", {}),
        },
        "dependencies": dependencies,
        "dependency_pins_by_role": {
            role: _pin_record(pin_map[role]) for role in CHILD_ROLES
        },
        "domain": {
            "is_encoder": 1,
            "units_per_group": [MIN_UNITS, MAX_UNITS],
            "num_ssps": [MIN_SSPS, MAX_SSPS],
            "mux_word_size": list(MUX_WORD_SIZES),
            "bits_per_component": [8, 16],
            "max_se_size": MAX_SE_SIZE,
            "fifo_size_positive_multiple_of_8": True,
            "fifo_pointer_is_bit_address": True,
            "frame_capacity_bits_positive": True,
            "max_cycles": MAX_CYCLES,
            "native_422_branch": "source-disabled-if-zero-not-composed",
        },
        "source_order": [
            "clear midpointSelected for active units",
            "capture encBalanceFifo fullness before any VLCUnit call",
            "set prevNumBits and compute forceMpp",
            "for unit=0..unitsPerGroup-1: call VLCUnit and commit its state snapshot",
            "for ssp=0..numSsps-1: fifo_put_bits(seSizeFifo, encBalance delta, 8)",
            "if groupCount > mux_word_size + (4 * bits_per_component + 4) - 3: call ProcessGroupEnc",
            "native 4:2:2 second pass is excluded because the source predicate is if(0)",
            "update bufferFullness, codedGroupSize, prevPrimaryQp, and groupCountLine",
        ],
        "semantics": {
            "kind": "vlc_group_encode_fsm",
            "state_transition": (
                "bounded sequential encoder parent with one ordered VLCUnit transaction per active unit, "
                "SE-size FIFO accounting, optional ProcessGroupEnc, and final group accounting"
            ),
            "legal_domain": {
                "units_per_group": [MIN_UNITS, MAX_UNITS],
                "num_ssps": [MIN_SSPS, MAX_SSPS],
                "mux_word_size": list(MUX_WORD_SIZES),
                "child_domain_valid_required": True,
                "se_size_delta": [0, MAX_SE_SIZE],
            },
            "finite_bounds": {
                "max_units": MAX_UNITS,
                "max_ssps": MAX_SSPS,
                "max_se_size": MAX_SE_SIZE,
                "max_cycles": MAX_CYCLES,
            },
            "bindings": {
                "unit_child_role": "vlc_unit",
                "process_child_role": "process_group",
                "se_size_fifo_write": "se_size_mem_write_req",
                "frame_write_event": "frame_mem_write_req",
                "completion": "done",
            },
            "composition_reduction": (
                "child modules are hash-pinned and exposed through external transaction/state/memory "
                "adapters; no child source is inlined or represented as absorbed"
            ),
        },
        "interface": {
            "module": "vlc_group_encode_fsm",
            "ports": contract_interface(),
        },
        "composition": {
            "status": "EXTERNALIZED_CHILD_BOUNDARY",
            "absorption": "NONE",
            "child_modules_instantiated": False,
            "child_source_embedded": False,
            "ordered_child_sequence": [
                "vlc_unit[0..units_per_group-1]",
                "se_size_fifo_put[0..num_ssps-1]",
                "process_group_enc[conditional]",
            ],
            "memory_events_externalized": [
                "enc_balance",
                "shifter",
                "se_size",
                "frame",
            ],
            "children": [
                {
                    "role": role,
                    "module": pin_map[role].module,
                    "module_file": pin_map[role].module_path,
                    "module_sha256": pin_map[role].module_sha256,
                    "contract_file": pin_map[role].contract_path,
                    "contract_sha256": pin_map[role].contract_sha256,
                    "source_file": pin_map[role].function.get("source_file"),
                    "source_file_sha256": pin_map[role].source_file_sha256,
                    "source_body_sha256": pin_map[role].function.get("source_body_sha256"),
                    "absorption": "EXTERNALIZED_TRANSACTION_ADAPTER",
                }
                for role in CHILD_ROLES
            ],
        },
        "flags": [
            "illegal_domain",
            "fatal_error",
            "bound_violation",
            "child_error",
            "fifo_underflow",
            "fifo_overflow",
            "se_size_overflow",
            "buffer_overflow",
            "done",
        ],
        "promotion": {
            "simulation_may_proceed": True,
            "status": "BLOCKED_PENDING_HUMAN_CONTRACT_REVIEW",
        },
        "obligations": [
            "compose the pinned VLCUnit and ProcessGroupEnc modules in the Verilator C adapter",
            "compare full state/FIFO/frame write footprints against the C source",
            "exercise legal and illegal finite-bound domains",
            "human review before promotion; no promotion is performed by this generator",
        ],
    }
    if rtl_sha256 is not None:
        contract["rtl"] = {
            "module": "vlc_group_encode_fsm",
            "candidate_sha256": rtl_sha256,
        }
    return contract


def _sv_port_declaration(port: Mapping[str, Any]) -> str:
    width = int(port.get("width", 1))
    signed = " signed" if port.get("signed") and width > 1 else ""
    packed = "logic" if width == 1 else f"logic{signed} [{width - 1}:0]"
    return f"    {port['direction']} {packed} {port['name']}{port.get('unpacked', '')}"


def _path_from_record(value: str, root: pathlib.Path) -> pathlib.Path:
    path = pathlib.Path(value)
    return path if path.is_absolute() else (root / path).resolve()


def _verify_pin(pin: ChildPin | Mapping[str, Any], root: pathlib.Path) -> None:
    if isinstance(pin, ChildPin):
        contract_path = pathlib.Path(pin.contract_path)
        module_path = pathlib.Path(pin.module_path)
        expected_contract = pin.contract_sha256
        expected_module = pin.module_sha256
        expected_source = pin.source_file_sha256
        function = pin.function
    else:
        contract_path = _path_from_record(str(pin.get("contract_file", "")), root)
        module_path = _path_from_record(str(pin.get("module_file", "")), root)
        expected_contract = str(pin.get("contract_sha256", ""))
        expected_module = str(pin.get("module_sha256", ""))
        function = pin.get("function", {}) or {}
        expected_source = function.get("source_file_sha256")
    if not contract_path.is_file() or not module_path.is_file():
        raise DiscoveryError(f"pinned child file is missing: {contract_path} / {module_path}")
    if _sha256_file(contract_path) != expected_contract:
        raise DiscoveryError(f"pinned child contract changed: {contract_path}")
    if _sha256_file(module_path) != expected_module:
        raise DiscoveryError(f"pinned child module changed: {module_path}")
    if expected_source:
        source_name = pathlib.Path(str(function.get("source_file", "")))
        source_path = source_name if source_name.is_absolute() else root / source_name
        if source_path.is_file() and _sha256_file(source_path) != str(expected_source):
            raise DiscoveryError(f"pinned child source file changed: {source_path}")


def _render_memory_forwarding() -> str:
    lines: list[str] = []
    for prefix in FIFO_PREFIXES:
        lines.extend([
            f"    {prefix}_mem_read_req = '0;",
            f"    {prefix}_mem_read_addr = '{{default:'0}};",
            f"    {prefix}_mem_write_req = '0;",
            f"    {prefix}_mem_write_addr = '{{default:'0}};",
            f"    {prefix}_mem_write_data = '{{default:'0}};",
            f"    {prefix}_mem_write_bit_mask = '{{default:'0}};",
        ])
        for role in CHILD_ROLES:
            stem = f"{role}_{prefix}"
            lines.extend([
                f"    {stem}_mem_read_valid = '0;",
                f"    {stem}_mem_read_data = '{{default:'0}};",
                f"    {stem}_mem_write_ready = '0;",
            ])
    lines.extend([
        "    frame_mem_write_req = 1'b0;",
        "    frame_mem_write_addr = '0;",
        "    frame_mem_write_data = 8'h00;",
        "    frame_mem_write_bit_mask = 8'h00;",
        "    process_group_frame_mem_write_ready = 1'b0;",
    ])
    lines.extend([
        "    if (state_r == ST_VLC_WAIT) begin",
    ])
    for prefix in FIFO_PREFIXES:
        stem = f"vlc_unit_{prefix}"
        lines.extend([
            f"      {prefix}_mem_read_req = {stem}_mem_read_req;",
            f"      {prefix}_mem_read_addr = {stem}_mem_read_addr;",
            f"      {prefix}_mem_write_req = {stem}_mem_write_req;",
            f"      {prefix}_mem_write_addr = {stem}_mem_write_addr;",
            f"      {prefix}_mem_write_data = {stem}_mem_write_data;",
            f"      {prefix}_mem_write_bit_mask = {stem}_mem_write_bit_mask;",
            f"      {stem}_mem_read_valid = {prefix}_mem_read_valid;",
            f"      {stem}_mem_read_data = {prefix}_mem_read_data;",
            f"      {stem}_mem_write_ready = {prefix}_mem_write_ready;",
        ])
    lines.append("    end")
    lines.append("    else if (state_r == ST_PROCESS_WAIT) begin")
    for prefix in FIFO_PREFIXES:
        stem = f"process_group_{prefix}"
        lines.extend([
            f"      {prefix}_mem_read_req = {stem}_mem_read_req;",
            f"      {prefix}_mem_read_addr = {stem}_mem_read_addr;",
            f"      {prefix}_mem_write_req = {stem}_mem_write_req;",
            f"      {prefix}_mem_write_addr = {stem}_mem_write_addr;",
            f"      {prefix}_mem_write_data = {stem}_mem_write_data;",
            f"      {prefix}_mem_write_bit_mask = {stem}_mem_write_bit_mask;",
            f"      {stem}_mem_read_valid = {prefix}_mem_read_valid;",
            f"      {stem}_mem_read_data = {prefix}_mem_read_data;",
            f"      {stem}_mem_write_ready = {prefix}_mem_write_ready;",
        ])
    lines.extend([
        "      frame_mem_write_req = process_group_frame_mem_write_req;",
        "      frame_mem_write_addr = process_group_frame_mem_write_addr;",
        "      frame_mem_write_data = process_group_frame_mem_write_data;",
        "      frame_mem_write_bit_mask = process_group_frame_mem_write_bit_mask;",
        "      process_group_frame_mem_write_ready = frame_mem_write_ready;",
        "    end",
        "    if (state_r == ST_SE_WRITE) begin",
        "      se_size_mem_write_req[ssp_index_r] = 1'b1;",
        "      se_size_mem_write_addr[ssp_index_r] = se_size_write_ptr_r[ssp_index_r] >> 3;",
        "      se_size_mem_write_data[ssp_index_r] = se_write_data_r;",
        "      se_size_mem_write_bit_mask[ssp_index_r] = 8'hff;",
        "    end",
    ])
    return "\n".join(lines)


def render_rtl(
    candidate_or_contract: Mapping[str, Any],
    pins: Mapping[str, ChildPin] | Iterable[ChildPin] | None = None,
    *,
    module_name: str = "vlc_group_encode_fsm",
    root: pathlib.Path | None = None,
) -> str:
    """Render the bounded sequential parent; never mutate child artifacts."""

    root = (root or pathlib.Path(__file__).resolve().parent.parent).resolve()
    if pins is None and "interface" in candidate_or_contract and "semantics" in candidate_or_contract:
        contract = copy.deepcopy(dict(candidate_or_contract))
        records = contract.get("dependencies", []) or []
        pin_records = {
            str(item.get("role")): item for item in records if isinstance(item, dict)
        }
        if set(pin_records) != set(CHILD_ROLES):
            raise DiscoveryError("contract does not contain both pinned VLCGroup children")
        for item in pin_records.values():
            _verify_pin(item, root)
        pin_comment_records = pin_records
    else:
        if pins is None:
            raise DiscoveryError("render_rtl requires child pins")
        pin_map = _pin_map(pins)
        for pin in pin_map.values():
            _verify_pin(pin, root)
        contract = build_contract(candidate_or_contract, pin_map)
        pin_comment_records = {role: _pin_record(pin) for role, pin in pin_map.items()}
    ports = contract_interface()
    declarations = ",\n".join(_sv_port_declaration(port) for port in ports)
    safe_module = re.sub(r"[^A-Za-z0-9_]", "_", module_name)
    dependency_comment = "\n".join(
        "// pinned {role}: contract_sha256={contract_sha256} module_sha256={module_sha256} "
        "source_body_sha256={source_body} source_file_sha256={source_file}".format(
            role=role,
            contract_sha256=record.get("contract_sha256", ""),
            module_sha256=record.get("module_sha256", ""),
            source_body=(record.get("function", {}) or {}).get("source_body_sha256", ""),
            source_file=(record.get("function", {}) or {}).get("source_file_sha256"),
        )
        for role, record in sorted(pin_comment_records.items())
    )
    scalar_assignments = []
    for field in (
        "num_bits",
        "buffer_fullness",
        "num_bits_chunk",
        "pixels_in_group",
        "slice_width",
        "pixel_count",
        "group_count",
        "primary_qp",
        "prev_primary_qp",
        "prev_num_bits",
        "coded_group_size",
        "group_count_line",
        "force_mpp",
    ):
        scalar_assignments.append(f"  assign {field}_out = {field}_r;")
    scalar_assignments.extend([
        "  assign post_mux_num_bits_out = post_mux_num_bits_r;",
        "  assign busy = (state_r != ST_IDLE) && (state_r != ST_DONE) && (state_r != ST_ERROR);",
        "  assign done = (state_r == ST_DONE) || (state_r == ST_ERROR);",
        "  assign domain_valid = domain_valid_r && !fatal_error_r;",
        "  assign illegal_domain = illegal_domain_r;",
        "  assign fatal_error = fatal_error_r;",
        "  assign bound_violation = bound_violation_r;",
        "  assign child_error = child_error_r;",
        "  assign fifo_underflow = fifo_underflow_r;",
        "  assign fifo_overflow = fifo_overflow_r;",
        "  assign se_size_overflow = se_size_overflow_r;",
        "  assign buffer_overflow = buffer_overflow_r;",
        "  assign vlc_unit_start = (state_r == ST_VLC_START);",
        "  assign vlc_unit_index = unit_index_r;",
        "  assign vlc_unit_force_p1_ich2 = force_p1_ich2_r;",
        "  assign vlc_unit_num_bits_in = num_bits_r;",
        "  assign vlc_unit_primary_qp_in = primary_qp_r;",
        "  assign process_group_start = (state_r == ST_PROCESS_START);",
        "  assign process_group_is_encoder = is_encoder;",
        "  assign process_group_num_ssps = num_ssps;",
        "  assign process_group_mux_word_size = mux_word_size;",
        "  assign process_group_frame_capacity_bits = frame_capacity_bits;",
        "  assign process_group_post_mux_num_bits_in = post_mux_num_bits_r;",
    ])
    for prefix in FIFO_PREFIXES:
        for field in FIFO_FIELDS:
            scalar_assignments.append(f"  assign {prefix}_{field}_out = {prefix}_{field}_r;")
    for unit in range(MAX_UNITS):
        scalar_assignments.append(f"  assign midpoint_selected_out[{unit}] = midpoint_selected_r[{unit}];")
        for sample in range(SAMPLES_PER_UNIT):
            scalar_assignments.append(
                f"  assign quantized_residual_out[{unit}][{sample}] = quantized_residual_in[{unit}][{sample}];"
            )
            scalar_assignments.append(
                f"  assign quantized_residual_mid_out[{unit}][{sample}] = quantized_residual_mid_in[{unit}][{sample}];"
            )
    for prefix in FIFO_PREFIXES:
        for field in FIFO_FIELDS:
            scalar_assignments.append(
                f"  assign vlc_unit_{prefix}_{field}_in = {prefix}_{field}_r;"
            )
            scalar_assignments.append(
                f"  assign process_group_{prefix}_{field}_in = {prefix}_{field}_r;"
            )

    fifo_reg_declarations = []
    reset_fifo = []
    copy_fifo = []
    for prefix in FIFO_PREFIXES:
        for field in FIFO_FIELDS:
            fifo_reg_declarations.append(f"  logic [31:0] {prefix}_{field}_r [0:MAX_SSPS-1];")
            reset_fifo.append(f"        {prefix}_{field}_r[reset_i] <= 32'd0;")
            copy_fifo.append(
                f"        {prefix}_{field}_r[reset_i] <= {prefix}_{field}_in[reset_i];"
            )
    process_commit = []
    for prefix in FIFO_PREFIXES:
        for field in FIFO_FIELDS:
            process_commit.append(
                f"              {prefix}_{field}_r[k] <= process_group_{prefix}_{field}_out[k];"
            )
    vlc_commit = []
    for field in FIFO_FIELDS:
        vlc_commit.append(
            f"              enc_balance_{field}_r[k] <= vlc_unit_enc_balance_{field}_out[k];"
        )
    memory_forwarding = _render_memory_forwarding()
    template = f"""// Generated by tools/generate_vlc_group_encode.py
// Encoder-only bounded sequential parent; child RTL is externally composed.
// No C source, promotion state, or child module is modified or absorbed here.
{dependency_comment}
module {safe_module} #(
    parameter integer MAX_SSPS = {MAX_SSPS},
    parameter integer MAX_UNITS = {MAX_UNITS},
    parameter integer MAX_SE_SIZE = {MAX_SE_SIZE},
    parameter integer MAX_CYCLES = {MAX_CYCLES}
) (
{declarations}
);

  localparam integer ST_IDLE = 0;
  localparam integer ST_INIT = 1;
  localparam integer ST_VLC_START = 2;
  localparam integer ST_VLC_WAIT = 3;
  localparam integer ST_SE_PREP = 4;
  localparam integer ST_SE_WRITE = 5;
  localparam integer ST_PROCESS_CHECK = 6;
  localparam integer ST_PROCESS_START = 7;
  localparam integer ST_PROCESS_WAIT = 8;
  localparam integer ST_ACCOUNT = 9;
  localparam integer ST_DONE = 10;
  localparam integer ST_ERROR = 11;
  localparam integer MIN_SSPS = {MIN_SSPS};
  localparam integer MIN_UNITS = {MIN_UNITS};

  logic [3:0] state_r;
  logic [2:0] unit_index_r;
  logic [2:0] ssp_index_r;
  logic [31:0] cycle_count_r;
  logic [31:0] start_fullness_r [0:MAX_SSPS-1];
  logic [31:0] se_delta_r;
  logic [7:0] se_write_data_r;
  logic signed [31:0] num_bits_r;
  logic signed [31:0] buffer_fullness_r;
  logic signed [31:0] num_bits_chunk_r;
  logic signed [31:0] pixels_in_group_r;
  logic signed [31:0] slice_width_r;
  logic signed [31:0] pixel_count_r;
  logic signed [31:0] group_count_r;
  logic signed [31:0] primary_qp_r;
  logic signed [31:0] prev_primary_qp_r;
  logic signed [31:0] prev_num_bits_r;
  logic signed [31:0] coded_group_size_r;
  logic signed [31:0] group_count_line_r;
  logic signed [31:0] force_mpp_r;
  logic signed [31:0] force_p1_ich2_r;
  logic [31:0] post_mux_num_bits_r;
  logic signed [31:0] midpoint_selected_r [0:MAX_UNITS-1];
  logic domain_valid_r;
  logic illegal_domain_r;
  logic fatal_error_r;
  logic bound_violation_r;
  logic child_error_r;
  logic fifo_underflow_r;
  logic fifo_overflow_r;
  logic se_size_overflow_r;
  logic buffer_overflow_r;
  logic input_legal;
  logic force_mpp_calc;
  logic signed [31:0] active_max_se_size;
{chr(10).join(fifo_reg_declarations)}

  integer reset_i;
  integer k;
  integer max_bits_i;
  integer adjusted_fullness_i;
  integer bug_fix_condition_i;

  assign active_max_se_size =
      ($signed(bits_per_component) * 32'sd4) + 32'sd4;

  always_comb begin
    input_legal = 1'b1;
    if (is_encoder != 1'b1)
      input_legal = 1'b0;
    if ((units_per_group < MIN_UNITS) || (units_per_group > MAX_UNITS))
      input_legal = 1'b0;
    if ((num_ssps < MIN_SSPS) || (num_ssps > MAX_SSPS))
      input_legal = 1'b0;
    if ((mux_word_size != 7'd48) && (mux_word_size != 7'd64))
      input_legal = 1'b0;
    if ((bits_per_component < 8) || (bits_per_component > 16))
      input_legal = 1'b0;
    if ((bits_per_pixel < 0) || (chunk_size <= 0) || (rcb_bits <= 0) ||
        (frame_capacity_bits <= 0))
      input_legal = 1'b0;
    for (k = 0; k < MAX_SSPS; k = k + 1) begin
      if (k < num_ssps) begin
        if ((max_se_size[k] == 0) || (max_se_size[k] > MAX_SE_SIZE))
          input_legal = 1'b0;
        if ((enc_balance_size_bits_in[k] == 0) ||
            ((enc_balance_size_bits_in[k] % 8) != 0) ||
            (enc_balance_fullness_in[k] > enc_balance_size_bits_in[k]) ||
            (enc_balance_read_ptr_in[k] >= enc_balance_size_bits_in[k]) ||
            (enc_balance_write_ptr_in[k] >= enc_balance_size_bits_in[k]) ||
            (enc_balance_max_fullness_in[k] > enc_balance_size_bits_in[k]))
          input_legal = 1'b0;
        if ((shifter_size_bits_in[k] == 0) ||
            ((shifter_size_bits_in[k] % 8) != 0) ||
            (shifter_fullness_in[k] > shifter_size_bits_in[k]) ||
            (shifter_read_ptr_in[k] >= shifter_size_bits_in[k]) ||
            (shifter_write_ptr_in[k] >= shifter_size_bits_in[k]) ||
            (shifter_max_fullness_in[k] > shifter_size_bits_in[k]))
          input_legal = 1'b0;
        if ((se_size_size_bits_in[k] == 0) ||
            ((se_size_size_bits_in[k] % 8) != 0) ||
            (se_size_fullness_in[k] > se_size_size_bits_in[k]) ||
            (se_size_read_ptr_in[k] >= se_size_size_bits_in[k]) ||
            (se_size_write_ptr_in[k] >= se_size_size_bits_in[k]) ||
            (se_size_max_fullness_in[k] > se_size_size_bits_in[k]))
          input_legal = 1'b0;
      end
    end
  end

  always_comb begin
    max_bits_i = ((pixels_in_group_in * bits_per_pixel) + 15) >>> 4;
    adjusted_fullness_i = buffer_fullness_in;
    bug_fix_condition_i = (bits_per_pixel * slice_width_in) & 15;
    force_mpp_calc = 1'b0;
    if (((bug_fix_condition_i != 0) &&
         (num_bits_chunk_in + max_bits_i + 8 == chunk_size * 8)) ||
        (num_bits_chunk_in + max_bits_i + 8 > chunk_size * 8)) begin
      adjusted_fullness_i = adjusted_fullness_i - 8;
      if (adjusted_fullness_i <
          (max_bits_i - $signed({{1'b0, units_per_group}})))
        force_mpp_calc = 1'b1;
    end
    else if ((vbr_enable == 1'b0) && (pixel_count_in >= initial_xmit_delay) &&
             (adjusted_fullness_i <
              (max_bits_i - $signed({{1'b0, units_per_group}})))) begin
      force_mpp_calc = 1'b1;
    end
  end

  always_comb begin
{memory_forwarding}
  end

{chr(10).join(scalar_assignments)}

  function automatic [31:0] advance_byte_ptr(
      input [31:0] pointer,
      input [31:0] size_bits
  );
    begin
      if ((size_bits == 0) || ((pointer + 32'd8) >= size_bits))
        advance_byte_ptr = 32'd0;
      else
        advance_byte_ptr = pointer + 32'd8;
    end
  endfunction

  always_ff @(posedge clk or negedge rst_n) begin
    if (!rst_n) begin
      state_r <= ST_IDLE;
      unit_index_r <= 3'd0;
      ssp_index_r <= 3'd0;
      cycle_count_r <= 32'd0;
      se_delta_r <= 32'd0;
      se_write_data_r <= 8'd0;
      num_bits_r <= 32'sd0;
      buffer_fullness_r <= 32'sd0;
      num_bits_chunk_r <= 32'sd0;
      pixels_in_group_r <= 32'sd0;
      slice_width_r <= 32'sd0;
      pixel_count_r <= 32'sd0;
      group_count_r <= 32'sd0;
      primary_qp_r <= 32'sd0;
      prev_primary_qp_r <= 32'sd0;
      prev_num_bits_r <= 32'sd0;
      coded_group_size_r <= 32'sd0;
      group_count_line_r <= 32'sd0;
      force_mpp_r <= 32'sd0;
      force_p1_ich2_r <= 32'sd0;
      domain_valid_r <= 1'b0;
      illegal_domain_r <= 1'b0;
      fatal_error_r <= 1'b0;
      bound_violation_r <= 1'b0;
      child_error_r <= 1'b0;
      fifo_underflow_r <= 1'b0;
      fifo_overflow_r <= 1'b0;
      se_size_overflow_r <= 1'b0;
      buffer_overflow_r <= 1'b0;
      for (reset_i = 0; reset_i < MAX_SSPS; reset_i = reset_i + 1) begin
{chr(10).join(reset_fifo)}
        start_fullness_r[reset_i] <= 32'd0;
      end
      for (reset_i = 0; reset_i < MAX_UNITS; reset_i = reset_i + 1)
        midpoint_selected_r[reset_i] <= 32'sd0;
    end
    else if ((state_r != ST_IDLE) && (state_r != ST_DONE) &&
             (state_r != ST_ERROR) && (cycle_count_r >= MAX_CYCLES - 1)) begin
      bound_violation_r <= 1'b1;
      fatal_error_r <= 1'b1;
      domain_valid_r <= 1'b0;
      state_r <= ST_ERROR;
    end
    else begin
      if ((state_r != ST_IDLE) && (state_r != ST_DONE) && (state_r != ST_ERROR))
        cycle_count_r <= cycle_count_r + 32'd1;
      case (state_r)
        ST_IDLE: begin
          if (start) begin
            cycle_count_r <= 32'd0;
            illegal_domain_r <= 1'b0;
            fatal_error_r <= 1'b0;
            bound_violation_r <= 1'b0;
            child_error_r <= 1'b0;
            fifo_underflow_r <= 1'b0;
            fifo_overflow_r <= 1'b0;
            se_size_overflow_r <= 1'b0;
            buffer_overflow_r <= 1'b0;
            domain_valid_r <= input_legal;
            if (!input_legal) begin
              illegal_domain_r <= 1'b1;
              fatal_error_r <= 1'b1;
              state_r <= ST_ERROR;
            end
            else begin
              num_bits_r <= num_bits_in;
              buffer_fullness_r <= buffer_fullness_in;
              num_bits_chunk_r <= num_bits_chunk_in;
              pixels_in_group_r <= pixels_in_group_in;
              slice_width_r <= slice_width_in;
              pixel_count_r <= pixel_count_in;
              group_count_r <= group_count_in;
              primary_qp_r <= primary_qp_in;
              prev_primary_qp_r <= prev_primary_qp_in;
              prev_num_bits_r <= prev_num_bits_in;
              coded_group_size_r <= coded_group_size_in;
              group_count_line_r <= group_count_line_in;
              force_mpp_r <= force_mpp_in;
              post_mux_num_bits_r <= post_mux_num_bits_in;
              for (reset_i = 0; reset_i < MAX_SSPS; reset_i = reset_i + 1) begin
{chr(10).join(copy_fifo)}
              end
              for (reset_i = 0; reset_i < MAX_UNITS; reset_i = reset_i + 1)
                midpoint_selected_r[reset_i] <= midpoint_selected_in[reset_i];
              state_r <= ST_INIT;
            end
          end
        end

        ST_INIT: begin
          // Exact source order: clear unit midpoint markers, then snapshot FIFO fullness.
          for (reset_i = 0; reset_i < MAX_UNITS; reset_i = reset_i + 1)
            midpoint_selected_r[reset_i] <=
                (reset_i < units_per_group) ? 32'sd0 : midpoint_selected_r[reset_i];
          for (reset_i = 0; reset_i < MAX_SSPS; reset_i = reset_i + 1)
            start_fullness_r[reset_i] <= enc_balance_fullness_r[reset_i];
          prev_num_bits_r <= num_bits_r;
          force_mpp_r <= force_mpp_calc ? 32'sd1 : 32'sd0;
          unit_index_r <= 3'd0;
          ssp_index_r <= 3'd0;
          state_r <= ST_VLC_START;
        end

        ST_VLC_START: begin
          if (vlc_unit_ready)
            state_r <= ST_VLC_WAIT;
        end

        ST_VLC_WAIT: begin
          if (vlc_unit_done) begin
            if (!vlc_unit_domain_valid || vlc_unit_fatal_error) begin
              child_error_r <= 1'b1;
              illegal_domain_r <= !vlc_unit_domain_valid;
              fatal_error_r <= 1'b1;
              domain_valid_r <= 1'b0;
              state_r <= ST_ERROR;
            end
            else begin
              num_bits_r <= vlc_unit_num_bits_out;
              primary_qp_r <= vlc_unit_primary_qp_out;
              for (k = 0; k < MAX_SSPS; k = k + 1) begin
{chr(10).join(vlc_commit)}
              end
              if (unit_index_r + 3'd1 < units_per_group) begin
                unit_index_r <= unit_index_r + 3'd1;
                state_r <= ST_VLC_START;
              end
              else begin
                ssp_index_r <= 3'd0;
                state_r <= ST_SE_PREP;
              end
            end
          end
        end

        ST_SE_PREP: begin
          if (ssp_index_r >= num_ssps) begin
            state_r <= ST_PROCESS_CHECK;
          end
          else if (enc_balance_fullness_r[ssp_index_r] < start_fullness_r[ssp_index_r]) begin
            fifo_underflow_r <= 1'b1;
            fatal_error_r <= 1'b1;
            state_r <= ST_ERROR;
          end
          else begin
            se_delta_r <= enc_balance_fullness_r[ssp_index_r] - start_fullness_r[ssp_index_r];
            se_write_data_r <= enc_balance_fullness_r[ssp_index_r] - start_fullness_r[ssp_index_r];
            if ((enc_balance_fullness_r[ssp_index_r] - start_fullness_r[ssp_index_r]) > MAX_SE_SIZE) begin
              se_size_overflow_r <= 1'b1;
              illegal_domain_r <= 1'b1;
              fatal_error_r <= 1'b1;
              domain_valid_r <= 1'b0;
              state_r <= ST_ERROR;
            end
            else if ((enc_balance_fullness_r[ssp_index_r] - start_fullness_r[ssp_index_r]) > max_se_size[ssp_index_r]) begin
              se_size_overflow_r <= 1'b1;
              fatal_error_r <= 1'b1;
              state_r <= ST_ERROR;
            end
            else if ((se_size_fullness_r[ssp_index_r] + 32'd8) >
                     se_size_size_bits_r[ssp_index_r]) begin
              fifo_overflow_r <= 1'b1;
              fatal_error_r <= 1'b1;
              state_r <= ST_ERROR;
            end
            else begin
              state_r <= ST_SE_WRITE;
            end
          end
        end

        ST_SE_WRITE: begin
          if (se_size_mem_write_ready[ssp_index_r]) begin
            se_size_fullness_r[ssp_index_r] <= se_size_fullness_r[ssp_index_r] + 32'd8;
            se_size_write_ptr_r[ssp_index_r] <= advance_byte_ptr(
                se_size_write_ptr_r[ssp_index_r], se_size_size_bits_r[ssp_index_r]);
            if ((se_size_fullness_r[ssp_index_r] + 32'd8) >
                se_size_max_fullness_r[ssp_index_r])
              se_size_max_fullness_r[ssp_index_r] <=
                  se_size_fullness_r[ssp_index_r] + 32'd8;
            if (ssp_index_r + 3'd1 < num_ssps) begin
              ssp_index_r <= ssp_index_r + 3'd1;
              state_r <= ST_SE_PREP;
            end
            else begin
              state_r <= ST_PROCESS_CHECK;
            end
          end
        end

        ST_PROCESS_CHECK: begin
          if (group_count_r >
              ($signed({{1'b0, mux_word_size}}) + active_max_se_size - 32'sd3))
            state_r <= ST_PROCESS_START;
          else
            state_r <= ST_ACCOUNT;
        end

        ST_PROCESS_START: begin
          if (process_group_ready)
            state_r <= ST_PROCESS_WAIT;
        end

        ST_PROCESS_WAIT: begin
          if (process_group_done) begin
            if (!process_group_domain_valid || process_group_fatal_error) begin
              child_error_r <= 1'b1;
              illegal_domain_r <= !process_group_domain_valid;
              fatal_error_r <= 1'b1;
              domain_valid_r <= 1'b0;
              state_r <= ST_ERROR;
            end
            else begin
              post_mux_num_bits_r <= process_group_post_mux_num_bits_out;
              for (k = 0; k < MAX_SSPS; k = k + 1) begin
{chr(10).join(process_commit)}
              end
              state_r <= ST_ACCOUNT;
            end
          end
        end

        ST_ACCOUNT: begin
          buffer_fullness_r <= buffer_fullness_r + (num_bits_r - prev_num_bits_r);
          coded_group_size_r <= num_bits_r - prev_num_bits_r;
          prev_primary_qp_r <= primary_qp_r;
          group_count_line_r <= group_count_line_r + 32'sd1;
          if ((buffer_fullness_r + (num_bits_r - prev_num_bits_r)) > rcb_bits) begin
            buffer_overflow_r <= 1'b1;
            fatal_error_r <= 1'b1;
            state_r <= ST_ERROR;
          end
          else begin
            state_r <= ST_DONE;
          end
        end

        ST_DONE: begin
          state_r <= ST_IDLE;
        end

        ST_ERROR: begin
          state_r <= ST_IDLE;
        end

        default: begin
          illegal_domain_r <= 1'b1;
          fatal_error_r <= 1'b1;
          domain_valid_r <= 1'b0;
          state_r <= ST_ERROR;
        end
      endcase
    end
  end

endmodule
"""
    return template


def generate_artifact(
    root: pathlib.Path,
    output_dir: pathlib.Path,
    *,
    source_dir: pathlib.Path | None = None,
    functions_path: pathlib.Path | None = None,
    coverage_path: pathlib.Path | None = None,
    frontier_path: pathlib.Path | None = None,
    loops_path: pathlib.Path | None = None,
    field_access_path: pathlib.Path | None = None,
    value_ranges_path: pathlib.Path | None = None,
    candidates_path: pathlib.Path | None = None,
    vlc_unit_artifact: pathlib.Path | None = None,
    process_group_artifact: pathlib.Path | None = None,
    child_artifacts: Mapping[str, pathlib.Path] | None = None,
    contract_paths: Sequence[pathlib.Path] | None = None,
) -> dict[str, Any]:
    """Discover, pin, render, and write only candidate_01.sv plus its contract."""

    root = root.resolve()
    source_dir = source_dir or _default_source_dir(root)
    functions_document = _read_json(functions_path or root / "facts" / "functions.json")
    coverage_document = _read_json(coverage_path or root / "coverage" / "coverage.json")
    frontier_document = None
    selected_frontier = frontier_path or root / "coverage" / "encode" / "frontier.json"
    if selected_frontier.is_file():
        frontier_document = _read_json(selected_frontier)
    candidate = discover_vlc_group_candidate(
        functions_document,
        coverage_document,
        source_dir,
        encode_frontier_document=frontier_document,
        loops_document=_read_json(loops_path) if loops_path and loops_path.is_file() else None,
        field_access_document=(
            _read_json(field_access_path) if field_access_path and field_access_path.is_file() else None
        ),
        value_ranges_document=(
            _read_json(value_ranges_path) if value_ranges_path and value_ranges_path.is_file() else None
        ),
        candidates_document=(
            _read_json(candidates_path) if candidates_path and candidates_path.is_file() else None
        ),
    )
    pins = discover_dependency_pins(
        root,
        source_dir,
        vlc_unit_artifact=vlc_unit_artifact,
        process_group_artifact=process_group_artifact,
        child_artifacts=child_artifacts,
        contract_paths=contract_paths,
    )
    contract = build_contract(candidate, pins)
    rtl = render_rtl(contract, root=root)
    contract["rtl"] = {
        "module": "vlc_group_encode_fsm",
        "candidate_sha256": _sha256_text(rtl),
    }
    output_dir.mkdir(parents=True, exist_ok=True)
    (output_dir / "candidate_01.sv").write_text(rtl, encoding="utf-8")
    _write_json(output_dir / "provisional-contract.json", contract)
    return {"candidate": candidate, "pins": pins, "contract": contract, "rtl": rtl}


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=pathlib.Path, default=pathlib.Path("."))
    parser.add_argument("--source-dir", type=pathlib.Path)
    parser.add_argument("--functions", type=pathlib.Path)
    parser.add_argument("--coverage", type=pathlib.Path)
    parser.add_argument("--encode-frontier", type=pathlib.Path)
    parser.add_argument("--loops", type=pathlib.Path)
    parser.add_argument("--field-access", type=pathlib.Path)
    parser.add_argument("--value-ranges", type=pathlib.Path)
    parser.add_argument("--candidates", type=pathlib.Path)
    parser.add_argument("--output", type=pathlib.Path, required=True)
    parser.add_argument("--vlc-unit-artifact", type=pathlib.Path)
    parser.add_argument("--process-group-artifact", type=pathlib.Path)
    parser.add_argument(
        "--dependency-contract",
        type=pathlib.Path,
        action="append",
        dest="dependency_contracts",
        help="explicit VLCUnit/ProcessGroupEnc contract or artifact path; repeat twice",
    )
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    args = _build_parser().parse_args(argv)
    try:
        artifact = generate_artifact(
            args.root,
            args.output,
            source_dir=args.source_dir,
            functions_path=args.functions,
            coverage_path=args.coverage,
            frontier_path=args.encode_frontier,
            loops_path=args.loops,
            field_access_path=args.field_access,
            value_ranges_path=args.value_ranges,
            candidates_path=args.candidates,
            vlc_unit_artifact=args.vlc_unit_artifact,
            process_group_artifact=args.process_group_artifact,
            contract_paths=args.dependency_contracts,
        )
    except (DiscoveryError, OSError, json.JSONDecodeError) as exc:
        print(f"DISCOVERY_INCOMPLETE: {exc}")
        return 2
    print(
        json.dumps(
            {
                "status": "GENERATED",
                "target": artifact["candidate"]["name"],
                "execution_count": artifact["candidate"]["execution_count"],
                "output": str(args.output),
                "dependencies": sorted(artifact["pins"]),
                "composition": artifact["contract"]["composition"]["status"],
            },
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
