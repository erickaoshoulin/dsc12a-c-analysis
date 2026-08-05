#!/usr/bin/env python3
"""Generate a provisional Encode RTL candidate for the VLC-unit boundary.

The generator is deliberately generator-only.  It consumes the immutable C
source span, Clang facts, Encode coverage, and an already verified FIFO-write
child contract.  It emits a self-contained SystemVerilog candidate plus a
contract when invoked as a CLI; it never changes the C model, CI/CD adapter,
promotion state, or any repository artifact.

Selection is based on signature, field effects, loop shape, source semantics,
coverage, and a structurally matching child contract.  Function spellings are
metadata only and are not an allowlist.
"""

from __future__ import annotations

import argparse
import ast
import hashlib
import json
import pathlib
import re
from typing import Any, Iterable


SEMANTICS_KIND = "bounded_vlc_unit_encode_transition"
MAX_ADDBITS_COMMANDS = 9
DEFAULT_SAMPLES_PER_UNIT = 3
DEFAULT_MAX_UNITS_PER_GROUP = 4
DEFAULT_MAX_PIXELS_PER_GROUP = 6
DEFAULT_GROUPS_PER_SUPERGROUP = 4
DEFAULT_ICH_BITS = 5


REQUIRED_STATE_READ_FIELDS = {
    "cpntBitDepth",
    "firstFlat",
    "flatnessType",
    "forceMpp",
    "groupCount",
    "ichIndexUnitMap",
    "ichIndicesInGroup",
    "ichLookup",
    "ichSelected",
    "origWithinQerr",
    "prevFirstFlat",
    "prevIchSelected",
    "primaryQp",
    "quantizedResidualMid",
    "unitCType",
    "unitSspMap",
}

REQUIRED_STATE_WRITE_FIELDS = {
    "flatnessType",
    "ichSelected",
    "midpointSelected",
    "predictedSize",
    "prevIchSelected",
    "rcSizeUnit",
}

REQUIRED_CONFIG_READ_FIELDS = {"bits_per_component"}


def read_json(path: pathlib.Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: pathlib.Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(value, indent=2, sort_keys=True, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )


def sha256_file(path: pathlib.Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


file_hash = sha256_file


def sha256_text(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def safe_identifier(value: str) -> str:
    result = re.sub(r"[^A-Za-z0-9_]", "_", value).lower()
    if not result:
        result = "vlc_unit_encode_transition"
    return ("c_" + result) if result[0].isdigit() else result


def _rows(document: Any) -> list[dict[str, Any]]:
    if isinstance(document, list):
        return [item for item in document if isinstance(item, dict)]
    if not isinstance(document, dict):
        return []
    for key in ("functions", "reached", "candidates"):
        value = document.get(key)
        if isinstance(value, list):
            return [item for item in value if isinstance(item, dict)]
    if document.get("clang_usr"):
        return [document]
    return []


def _by_usr(document: Any) -> dict[str, dict[str, Any]]:
    return {
        str(item.get("clang_usr")): item
        for item in _rows(document)
        if item.get("clang_usr")
    }


def _coverage_by_usr(document: Any) -> dict[str, dict[str, Any]]:
    result: dict[str, dict[str, Any]] = {}
    for item in _rows(document):
        usr = str(item.get("clang_usr", ""))
        if not usr:
            continue
        nested = item.get("coverage")
        nested = nested if isinstance(nested, dict) else {}
        raw_count = nested.get("execution_count", item.get("execution_count", 0))
        try:
            count = int(raw_count or 0)
        except (TypeError, ValueError):
            count = 0
        covered = nested.get("covered", item.get("covered"))
        if covered is None:
            covered = count > 0
        normalized = {
            **item,
            "coverage_status": nested.get(
                "coverage_status", item.get("coverage_status", "EXECUTED" if count > 0 else "NOT_REACHED")
            ),
            "execution_count": count,
            "covered": bool(covered) or count > 0,
        }
        prior = result.get(usr)
        if prior is None or count > int(prior.get("execution_count", 0) or 0):
            result[usr] = normalized
    return result


def _source_path(function: dict[str, Any], source_dir: pathlib.Path) -> pathlib.Path:
    value = pathlib.Path(str(function.get("source_file", "")))
    return value if value.is_absolute() else source_dir / value


def _source_body(
    function: dict[str, Any], source_dir: pathlib.Path
) -> tuple[pathlib.Path, int, int, str]:
    source = _source_path(function, source_dir)
    start = int(function.get("line", function.get("start_line", 0)) or 0)
    end = int(function.get("end_line", function.get("end", start)) or 0)
    if not source.is_file():
        raise FileNotFoundError(f"source span file does not exist: {source}")
    lines = source.read_text(encoding="utf-8", errors="replace").splitlines()
    if start < 1 or end < start or end > len(lines):
        raise ValueError(f"invalid source span {start}:{end} for {source}")
    return source, start, end, "\n".join(lines[start - 1 : end])


def _field_names(function: dict[str, Any], key: str, record: str | None = None) -> set[str]:
    return {
        str(item.get("name"))
        for item in function.get(key, []) or []
        if isinstance(item, dict)
        and item.get("name")
        and (record is None or item.get("record") == record)
    }


def _field_types(
    function: dict[str, Any], key: str, record: str | None = None
) -> dict[str, set[str]]:
    result: dict[str, set[str]] = {}
    for item in function.get(key, []) or []:
        if not isinstance(item, dict) or not item.get("name"):
            continue
        if record is not None and item.get("record") != record:
            continue
        result.setdefault(str(item["name"]), set()).add(str(item.get("type", "")))
    return result


def _scalar_parameters(function: dict[str, Any]) -> list[dict[str, Any]]:
    return [
        item
        for item in function.get("parameters", []) or []
        if isinstance(item, dict) and not item.get("pointer")
    ]


def _is_int_type(value: Any) -> bool:
    return str(value or "").strip() in {"int", "signed int"}


def _callee_refs(function: dict[str, Any]) -> list[dict[str, Any]]:
    result: list[dict[str, Any]] = []
    seen: set[str] = set()
    for key in ("callees", "calls"):
        for item in function.get(key, []) or []:
            if not isinstance(item, dict):
                continue
            usr = str(item.get("clang_usr", ""))
            if usr and usr not in seen:
                seen.add(usr)
                result.append(item)
    return result


def _repo_relative(path: pathlib.Path, repo_root: pathlib.Path) -> str:
    try:
        return str(path.resolve().relative_to(repo_root.resolve()))
    except ValueError:
        return str(path.resolve())


def _resolve_repo_path(value: str | pathlib.Path, repo_root: pathlib.Path) -> pathlib.Path:
    path = pathlib.Path(str(value))
    return path if path.is_absolute() else repo_root / path


def _macro_definitions(source_dir: pathlib.Path) -> dict[str, str]:
    definitions: dict[str, str] = {}
    for source in sorted((*source_dir.glob("*.h"), *source_dir.glob("*.c"))):
        text = source.read_text(encoding="utf-8", errors="replace")
        for match in re.finditer(
            r"^[ \t]*#[ \t]*define[ \t]+([A-Za-z_][A-Za-z0-9_]*)[ \t]+([^\r\n]+)",
            text,
            re.MULTILINE,
        ):
            definitions.setdefault(match.group(1), match.group(2).strip())
    return definitions


def _eval_int_expression(expression: str, definitions: dict[str, str]) -> int:
    value = expression.strip()
    value = re.sub(r"/\*.*?\*/", "", value)
    value = re.sub(r"//.*", "", value).strip()
    value = value.replace("UL", "").replace("U", "").replace("L", "")
    value = value.replace("&&", " and ").replace("||", " or ")
    value = re.sub(r"\b(0[xX][0-9A-Fa-f]+|[0-9]+)\b", r"\1", value)
    for _ in range(8):
        changed = False
        for name, replacement in definitions.items():
            if name == expression:
                continue
            if re.search(rf"\b{re.escape(name)}\b", value):
                value = re.sub(rf"\b{re.escape(name)}\b", f"({replacement})", value)
                changed = True
        if not changed:
            break
    tree = ast.parse(value, mode="eval")
    allowed = (
        ast.Expression,
        ast.Constant,
        ast.UnaryOp,
        ast.UAdd,
        ast.USub,
        ast.Invert,
        ast.BinOp,
        ast.Add,
        ast.Sub,
        ast.Mult,
        ast.FloorDiv,
        ast.LShift,
        ast.RShift,
        ast.BitOr,
        ast.BitAnd,
        ast.BitXor,
        ast.Mod,
        ast.BoolOp,
        ast.And,
        ast.Or,
        ast.Compare,
        ast.Eq,
        ast.NotEq,
        ast.Lt,
        ast.LtE,
        ast.Gt,
        ast.GtE,
    )
    if any(not isinstance(node, allowed) for node in ast.walk(tree)):
        raise ValueError(f"non-integer macro expression: {expression}")
    result = eval(compile(tree, "<macro>", "eval"), {"__builtins__": {}}, {})
    if not isinstance(result, int):
        raise ValueError(f"macro is not an integer: {expression}")
    return result


def _source_constant(
    source_dir: pathlib.Path,
    name: str,
    default: int | None = None,
) -> int:
    definitions = _macro_definitions(source_dir)
    expression = definitions.get(name)
    if expression is None:
        if default is None:
            raise RuntimeError(f"source constant {name} is not defined")
        return default
    try:
        return _eval_int_expression(expression, definitions)
    except (SyntaxError, TypeError, ValueError, NameError, ZeroDivisionError):
        if default is not None:
            return default
        raise RuntimeError(f"source constant {name} is not an integer")


def _default_source_dir(repo_root: pathlib.Path) -> pathlib.Path:
    receipt_path = repo_root / "facts" / "build-receipt.json"
    if receipt_path.is_file():
        try:
            receipt = read_json(receipt_path)
        except (OSError, ValueError, TypeError):
            receipt = {}
        model_root = receipt.get("model_root")
        if model_root:
            candidate = pathlib.Path(str(model_root)) / "source"
            if candidate.is_dir():
                return candidate
    commands_path = repo_root / "facts" / "compile_commands.json"
    if commands_path.is_file():
        try:
            commands = read_json(commands_path)
        except (OSError, ValueError, TypeError):
            commands = []
        if isinstance(commands, list):
            for row in commands:
                if not isinstance(row, dict):
                    continue
                directory = row.get("directory")
                if directory and (pathlib.Path(str(directory)) / "multiplex.c").is_file():
                    return pathlib.Path(str(directory))
    for candidate in (
        pathlib.Path("/Users/snow/Desktop/Display Stream Compression (DSC)/DSC 1.2a/DSC_model_20210623/source"),
        repo_root / "DSC_model_20210623" / "source",
    ):
        if (candidate / "multiplex.c").is_file():
            return candidate
    raise RuntimeError("cannot locate immutable DSC source directory")


def _source_constants(source_dir: pathlib.Path) -> dict[str, int]:
    return {
        "samples_per_unit": _source_constant(
            source_dir, "SAMPLES_PER_UNIT", DEFAULT_SAMPLES_PER_UNIT
        ),
        "max_units_per_group": _source_constant(
            source_dir, "MAX_UNITS_PER_GROUP", DEFAULT_MAX_UNITS_PER_GROUP
        ),
        "num_components": _source_constant(source_dir, "NUM_COMPONENTS", DEFAULT_MAX_UNITS_PER_GROUP),
        "max_pixels_per_group": _source_constant(
            source_dir, "MAX_PIXELS_PER_GROUP", DEFAULT_MAX_PIXELS_PER_GROUP
        ),
        "groups_per_supergroup": _source_constant(
            source_dir, "GROUPS_PER_SUPERGROUP", DEFAULT_GROUPS_PER_SUPERGROUP
        ),
        "ich_bits": _source_constant(source_dir, "ICH_BITS", DEFAULT_ICH_BITS),
    }


def _is_fifo_write_contract(contract: dict[str, Any]) -> bool:
    semantics = contract.get("semantics", {}) or {}
    kind = str(semantics.get("kind", "")).lower()
    bindings = semantics.get("bindings", {}) or {}
    ports = {
        str(item.get("name"))
        for item in (contract.get("interface", {}) or {}).get("ports", []) or []
        if isinstance(item, dict) and item.get("name")
    }
    required = {
        "data",
        "nbits",
        "num_bits",
        "fullness",
        "write_ptr",
        "fifo_size",
        "max_fullness",
        "num_bits_out",
        "fullness_out",
        "write_ptr_out",
        "max_fullness_out",
        "byte_0",
        "byte_1",
        "byte_2",
        "byte_3",
        "byte_4",
    }
    return (
        ("fifo" in kind and "write" in kind)
        and required.issubset(ports)
        and bool(bindings.get("fifo_array_field"))
        and bool(bindings.get("state_counter_field"))
    )


def _is_addbits_fact(function: dict[str, Any]) -> bool:
    parameters = function.get("parameters", []) or []
    if str(function.get("return_type")) != "void" or len(parameters) != 5:
        return False
    pointer_types = {
        str(item.get("type"))
        for item in parameters
        if isinstance(item, dict) and item.get("pointer")
    }
    scalars = _scalar_parameters(function)
    state_reads = _field_types(function, "fields_read", "dsc_state_t")
    state_writes = _field_names(function, "fields_write", "dsc_state_t")
    has_array_read = any("[" in type_name for types in state_reads.values() for type_name in types)
    return (
        pointer_types == {"dsc_cfg_t *", "dsc_state_t *"}
        and len(scalars) == 3
        and all(_is_int_type(item.get("type")) for item in scalars)
        and int(function.get("loop_count", 0) or 0) == 0
        and not (function.get("loops", []) or [])
        and has_array_read
        and bool(state_writes)
    )


def _dependency_pin_from_contract(
    contract_path: pathlib.Path,
    contract: dict[str, Any],
    repo_root: pathlib.Path,
    source_dir: pathlib.Path,
) -> dict[str, Any] | None:
    if not _is_fifo_write_contract(contract):
        return None
    function_meta = contract.get("function", {}) or {}
    function_usr = str(function_meta.get("clang_usr", ""))
    if not function_usr:
        return None
    artifact_dir = contract_path.parent
    candidate_path = artifact_dir / "candidate_01.sv"
    matrix_path = artifact_dir / "matrix-receipt.json"
    rtl_return_path = artifact_dir / "rtl-return-receipt.json"
    if not (candidate_path.is_file() and matrix_path.is_file() and rtl_return_path.is_file()):
        return None
    try:
        matrix = read_json(matrix_path)
        rtl_return = read_json(rtl_return_path)
    except (OSError, ValueError, TypeError):
        return None
    if matrix.get("status") != "PASS" or matrix.get("matrix_scope") != "all":
        return None
    if rtl_return.get("status") != "PASS":
        return None
    try:
        invocations = int(rtl_return.get("total_rtl_invocations", 0) or 0)
    except (TypeError, ValueError):
        invocations = 0
    if invocations <= 0:
        return None
    module = safe_identifier(str(contract.get("contract_id", "")))
    try:
        candidate_text = candidate_path.read_text(encoding="utf-8", errors="replace")
    except OSError:
        return None
    if not re.search(rf"\bmodule\s+{re.escape(module)}\s*\(", candidate_text):
        return None
    try:
        _, start, end, body = _source_body(
            {
                "source_file": function_meta.get("source_file"),
                "line": (function_meta.get("source_span", {}) or {}).get("start_line"),
                "end_line": (function_meta.get("source_span", {}) or {}).get("end_line"),
            },
            source_dir,
        )
        source_file = _source_path(
            {"source_file": function_meta.get("source_file")}, source_dir
        )
    except (OSError, ValueError, TypeError):
        return None
    expected_body_hash = str(function_meta.get("source_body_sha256", ""))
    body_hash = sha256_text(body)
    if not expected_body_hash or body_hash != expected_body_hash:
        return None
    return {
        "role": "addbits_command_sink",
        "kind": str((contract.get("semantics", {}) or {}).get("kind", "")),
        "function_usr": function_usr,
        "function_name": function_meta.get("name"),
        "contract_id": contract.get("contract_id"),
        "module": module,
        "contract_file": _repo_relative(contract_path, repo_root),
        "contract_sha256": sha256_file(contract_path),
        "module_file": _repo_relative(candidate_path, repo_root),
        "module_sha256": sha256_file(candidate_path),
        "matrix_receipt_file": _repo_relative(matrix_path, repo_root),
        "matrix_receipt_sha256": sha256_file(matrix_path),
        "rtl_return_receipt_file": _repo_relative(rtl_return_path, repo_root),
        "rtl_return_receipt_sha256": sha256_file(rtl_return_path),
        "rtl_return_invocations": invocations,
        "source_file": str(function_meta.get("source_file", "")),
        "source_span": {"start_line": start, "end_line": end},
        "source_body_sha256": body_hash,
        "source_file_sha256": sha256_file(source_file),
        "source_root": str(source_dir.resolve()),
    }


def _find_addbits_dependency(
    repo_root: pathlib.Path,
    source_dir: pathlib.Path,
    function_usr: str | None = None,
) -> dict[str, Any] | None:
    matches: list[dict[str, Any]] = []
    root = repo_root / "rtl"
    if not root.is_dir():
        return None
    for contract_path in sorted(root.rglob("provisional-contract.json")):
        try:
            contract = read_json(contract_path)
        except (OSError, ValueError, TypeError):
            continue
        meta = contract.get("function", {}) or {}
        if function_usr and str(meta.get("clang_usr", "")) != function_usr:
            continue
        pin = _dependency_pin_from_contract(contract_path, contract, repo_root, source_dir)
        if pin is not None:
            matches.append(pin)
    if not matches:
        return None
    matches.sort(
        key=lambda item: (-int(item.get("rtl_return_invocations", 0)), str(item.get("contract_file", "")))
    )
    return matches[0]


def find_addbits_dependency_pin(
    repo_root: pathlib.Path,
    source_dir: pathlib.Path | None = None,
    function_usr: str | None = None,
) -> dict[str, Any]:
    root = pathlib.Path(repo_root)
    source = pathlib.Path(source_dir) if source_dir is not None else _default_source_dir(root)
    pin = _find_addbits_dependency(root, source, function_usr)
    if pin is None:
        raise RuntimeError("no hash-verifiable FIFO-write dependency was discovered")
    return pin


def find_dependency_pins(
    repo_root: pathlib.Path,
    source_dir: pathlib.Path | None = None,
    function_usr: str | None = None,
) -> dict[str, dict[str, Any]]:
    return {
        "addbits": find_addbits_dependency_pin(repo_root, source_dir, function_usr)
    }


def _dependency_source_path(
    dependency: dict[str, Any], source_dir: pathlib.Path | None
) -> pathlib.Path:
    root_value = dependency.get("source_root")
    root = pathlib.Path(str(root_value)) if root_value else source_dir
    if root is None:
        raise RuntimeError("source directory is required to verify dependency source hash")
    source = pathlib.Path(str(dependency.get("source_file", "")))
    return source if source.is_absolute() else root / source


def _verify_dependency_pin(
    dependency: dict[str, Any],
    repo_root: pathlib.Path,
    source_dir: pathlib.Path | None = None,
) -> dict[str, Any]:
    contract_path = _resolve_repo_path(str(dependency.get("contract_file", "")), repo_root)
    module_path = _resolve_repo_path(str(dependency.get("module_file", "")), repo_root)
    if not contract_path.is_file() or not module_path.is_file():
        raise RuntimeError("pinned AddBits dependency artifact is missing")
    actual_contract_hash = sha256_file(contract_path)
    if actual_contract_hash != str(dependency.get("contract_sha256", "")):
        raise RuntimeError("AddBits dependency contract hash drift")
    actual_module_hash = sha256_file(module_path)
    if actual_module_hash != str(dependency.get("module_sha256", "")):
        raise RuntimeError("AddBits dependency module hash drift")
    contract = read_json(contract_path)
    if not _is_fifo_write_contract(contract):
        raise RuntimeError("pinned AddBits dependency contract shape drift")
    if contract.get("contract_id") != dependency.get("contract_id"):
        raise RuntimeError("pinned AddBits dependency contract identity drift")
    module_name = safe_identifier(str(contract.get("contract_id", "")))
    module_text = module_path.read_text(encoding="utf-8", errors="replace")
    if not re.search(rf"\bmodule\s+{re.escape(module_name)}\s*\(", module_text):
        raise RuntimeError("pinned AddBits dependency module identity drift")
    matrix_path = _resolve_repo_path(str(dependency.get("matrix_receipt_file", "")), repo_root)
    rtl_return_path = _resolve_repo_path(
        str(dependency.get("rtl_return_receipt_file", "")), repo_root
    )
    if not matrix_path.is_file() or not rtl_return_path.is_file():
        raise RuntimeError("pinned AddBits dependency proof receipt is missing")
    if dependency.get("matrix_receipt_sha256") and sha256_file(matrix_path) != dependency.get(
        "matrix_receipt_sha256"
    ):
        raise RuntimeError("AddBits dependency matrix receipt hash drift")
    if dependency.get("rtl_return_receipt_sha256") and sha256_file(rtl_return_path) != dependency.get(
        "rtl_return_receipt_sha256"
    ):
        raise RuntimeError("AddBits dependency RTL_RETURN receipt hash drift")
    matrix = read_json(matrix_path)
    rtl_return = read_json(rtl_return_path)
    if matrix.get("status") != "PASS" or matrix.get("matrix_scope") != "all":
        raise RuntimeError("pinned AddBits dependency matrix is not a full PASS")
    if rtl_return.get("status") != "PASS" or int(rtl_return.get("total_rtl_invocations", 0) or 0) <= 0:
        raise RuntimeError("pinned AddBits dependency has no RTL_RETURN proof")
    meta = contract.get("function", {}) or {}
    if str(meta.get("clang_usr", "")) != str(dependency.get("function_usr", "")):
        raise RuntimeError("pinned AddBits dependency function identity drift")
    source_file = _dependency_source_path(dependency, source_dir)
    if not source_file.is_file():
        raise RuntimeError(f"pinned AddBits source file is missing: {source_file}")
    span = dependency.get("source_span", {}) or {}
    start = int(span.get("start_line", 0) or 0)
    end = int(span.get("end_line", 0) or 0)
    lines = source_file.read_text(encoding="utf-8", errors="replace").splitlines()
    if start < 1 or end < start or end > len(lines):
        raise RuntimeError("pinned AddBits source span is invalid")
    body_hash = sha256_text("\n".join(lines[start - 1 : end]))
    if body_hash != str(dependency.get("source_body_sha256", "")):
        raise RuntimeError("AddBits dependency source body hash drift")
    expected_contract_body = str(meta.get("source_body_sha256", ""))
    if expected_contract_body and body_hash != expected_contract_body:
        raise RuntimeError("AddBits dependency contract source body hash drift")
    if dependency.get("source_file_sha256") and sha256_file(source_file) != dependency.get(
        "source_file_sha256"
    ):
        raise RuntimeError("AddBits dependency source file hash drift")
    return contract


def verify_dependency_pins(
    contract: dict[str, Any],
    repo_root: pathlib.Path | None = None,
    source_dir: pathlib.Path | None = None,
) -> list[dict[str, Any]]:
    root = pathlib.Path(repo_root or pathlib.Path(__file__).resolve().parent.parent)
    dependencies = contract.get("dependencies", []) or []
    if len(dependencies) != 1:
        raise RuntimeError("VLC-unit contract requires exactly one AddBits dependency")
    if str(dependencies[0].get("role", "")) != "addbits_command_sink":
        raise RuntimeError("VLC-unit dependency role is not AddBits")
    child = _verify_dependency_pin(dependencies[0], root, source_dir)
    return [child]


def _looks_like_vlc_boundary(
    function: dict[str, Any],
    body: str,
    facts_by_usr: dict[str, dict[str, Any]],
) -> tuple[bool, dict[str, Any], str]:
    parameters = function.get("parameters", []) or []
    if str(function.get("return_type")) != "void" or len(parameters) != 5:
        return False, {}, "void five-parameter stateful shape is absent"
    if not (
        parameters[0].get("pointer")
        and str(parameters[0].get("type")) == "dsc_cfg_t *"
        and parameters[1].get("pointer")
        and str(parameters[1].get("type")) == "dsc_state_t *"
        and not parameters[2].get("pointer")
        and _is_int_type(parameters[2].get("type"))
        and parameters[3].get("pointer")
        and _is_int_type(str(parameters[3].get("type", "")).replace("*", "").strip())
        and not parameters[4].get("pointer")
        and _is_int_type(parameters[4].get("type"))
    ):
        return False, {}, "configuration/state/scalar/array signature is absent"
    state_reads = _field_names(function, "fields_read", "dsc_state_t")
    state_writes = _field_names(function, "fields_write", "dsc_state_t")
    cfg_reads = _field_names(function, "fields_read", "dsc_cfg_t")
    if not REQUIRED_STATE_READ_FIELDS.issubset(state_reads):
        return False, {}, "required encoder state reads are absent"
    if not REQUIRED_STATE_WRITE_FIELDS.issubset(state_writes):
        return False, {}, "required encoder state writes are absent"
    if not REQUIRED_CONFIG_READ_FIELDS.issubset(cfg_reads):
        return False, {}, "required encoder configuration read is absent"
    loops = [item for item in function.get("loops", []) or [] if isinstance(item, dict)]
    fixed = [item for item in loops if item.get("has_fixed_trip_count") or item.get("fixed_trip_count")]
    dynamic_ich = [
        item
        for item in loops
        if "ichIndicesInGroup" in str(item.get("condition", ""))
    ]
    fixed_sample = [
        item
        for item in fixed
        if "SAMPLES_PER_UNIT" in str(item.get("condition", ""))
    ]
    fixed_units = [
        item
        for item in fixed
        if "MAX_UNITS_PER_GROUP" in str(item.get("condition", ""))
    ]
    if len(fixed_sample) < 1 or len(fixed_units) < 1 or len(dynamic_ich) < 2:
        return False, {}, "fixed sample/unit loops and bounded ICH loops are absent"
    source_tokens = (
        "required_size",
        "prefix_value",
        "max_pfx_size",
        "quantized_residuals",
        "quantizedResidualMid",
        "origWithinQerr",
        "rcSizeUnit",
        "predictedSize",
        "midpointSelected",
        "ichSelected",
    )
    if not all(token in body for token in source_tokens):
        return False, {}, "source does not carry the residual/ICH/VLC state shape"
    child_fact: dict[str, Any] | None = None
    child_usr = ""
    for callee in _callee_refs(function):
        usr = str(callee.get("clang_usr", ""))
        fact = facts_by_usr.get(usr)
        if fact and _is_addbits_fact(fact):
            child_fact = fact
            child_usr = usr
            break
    if child_fact is None:
        return False, {}, "no structurally matching stateful bit-write child callee"
    child_calls = [
        item
        for item in function.get("calls", []) or []
        if isinstance(item, dict) and str(item.get("clang_usr", "")) == child_usr
    ]
    if len(child_calls) < 3:
        return False, {}, "source has too few ordered bit-write call sites"
    evidence = {
        "pointer_parameter_types": sorted(
            str(item.get("type"))
            for item in parameters
            if item.get("pointer")
        ),
        "scalar_parameter_types": [str(item.get("type")) for item in _scalar_parameters(function)],
        "state_read_fields": sorted(state_reads),
        "state_write_fields": sorted(state_writes),
        "config_read_fields": sorted(cfg_reads),
        "loop_conditions": [str(item.get("condition", "")) for item in loops],
        "fixed_loop_trip_counts": [
            int(item.get("fixed_trip_count"))
            for item in fixed
            if item.get("fixed_trip_count") is not None
        ],
        "fixed_sample_loop_count": len(fixed_sample),
        "fixed_unit_loop_count": len(fixed_units),
        "bounded_ich_loop_count": len(dynamic_ich),
        "child_clang_usr": child_usr,
        "child_call_sites": [
            int((item.get("location", {}) or {}).get("line", 0) or 0)
            for item in child_calls
        ],
        "direct_effects": function.get("effects", {}),
        "bounded_loop_proofs": [
            {
                "condition": item.get("condition"),
                "fixed_trip_count": item.get("fixed_trip_count"),
                "has_fixed_trip_count": bool(item.get("has_fixed_trip_count")),
                "proof": item.get("proof"),
                "iteration_dependency": item.get("iteration_dependency"),
            }
            for item in loops
        ],
    }
    return (
        True,
        evidence,
        "covered stateful encoder boundary with ordered bit-write calls, fixed sample/unit loops, and bounded ICH loops",
    )


def discover_vlc_unit_encode_candidates(
    functions: Any,
    candidates: Any,
    coverage: Any,
    source_dir: pathlib.Path,
    repo_root: pathlib.Path | None = None,
) -> list[dict[str, Any]]:
    """Discover covered VLC-like Encode boundaries from facts and source shape."""

    source_dir = pathlib.Path(source_dir)
    repo_root = pathlib.Path(repo_root or pathlib.Path(__file__).resolve().parent.parent)
    function_rows = _rows(functions)
    facts_by_usr = _by_usr(functions)
    candidate_by_usr = _by_usr(candidates)
    coverage_by_usr = _coverage_by_usr(coverage)
    constants = _source_constants(source_dir)
    discovered: list[dict[str, Any]] = []
    for function in function_rows:
        usr = str(function.get("clang_usr", ""))
        if not usr:
            continue
        coverage_row = coverage_by_usr.get(usr)
        if not coverage_row or not coverage_row.get("covered"):
            continue
        execution_count = int(coverage_row.get("execution_count", 0) or 0)
        if execution_count <= 0:
            continue
        candidate = candidate_by_usr.get(usr, {})
        if candidate and candidate.get("production_reachable") is False:
            continue
        try:
            _, _, _, body = _source_body(function, source_dir)
            matches, structural_evidence, reason = _looks_like_vlc_boundary(
                function, body, facts_by_usr
            )
        except (OSError, ValueError, TypeError, RuntimeError):
            continue
        if not matches:
            continue
        child_usr = str(structural_evidence["child_clang_usr"])
        dependency = _find_addbits_dependency(repo_root, source_dir, child_usr)
        if dependency is None:
            continue
        source_hash = sha256_text(body)
        max_ich = constants["max_pixels_per_group"]
        max_commands = 2 + 1 + max_ich
        if max_commands != MAX_ADDBITS_COMMANDS:
            continue
        structural_evidence = {
            **structural_evidence,
            "source_body_sha256": source_hash,
            "max_addbits_commands": max_commands,
            "dynamic_ich_bound": max_ich,
            "source_ordered": True,
            "fatal_side_effects_separated": bool(
                (function.get("effects", {}) or {}).get("assert")
                or (function.get("effects", {}) or {}).get("file_io")
            ),
        }
        discovered.append(
            {
                "name": function.get("name"),
                "qualified_name": function.get("qualified_name", function.get("name")),
                "clang_usr": usr,
                "source_file": function.get("source_file"),
                "line": function.get("line"),
                "end_line": function.get("end_line"),
                "source_body_sha256": source_hash,
                "semantics_kind": SEMANTICS_KIND,
                "execution_count": execution_count,
                "selection_basis": [
                    reason,
                    "positive Encode execution coverage is required",
                    "Clang fields identify the complete residual/ICH state transition",
                    "the child is selected by stateful FIFO-write signature and PASSed RTL evidence",
                    "fixed-trip and bounded dynamic loops are retained as generation evidence",
                    "function spelling is not used as a selection predicate",
                ],
                "structural_evidence": structural_evidence,
                "literal_size_bound": {
                    "samples_per_unit": constants["samples_per_unit"],
                    "max_units_per_group": constants["max_units_per_group"],
                    "max_pixels_per_group": max_ich,
                    "ich_bits": constants["ich_bits"],
                    "groups_per_supergroup": constants["groups_per_supergroup"],
                    "max_addbits_commands": max_commands,
                    "child_clang_usr": child_usr,
                },
                "dependency": dependency,
            }
        )
    discovered.sort(
        key=lambda row: (
            -int(row.get("execution_count", 0)),
            int(row.get("line", 0) or 0),
            str(row.get("clang_usr", "")),
        )
    )
    return discovered


def select_candidate(candidates: Iterable[dict[str, Any]]) -> dict[str, Any]:
    rows = list(candidates)
    if not rows:
        raise RuntimeError("no covered structural Encode VLC-unit candidate")
    return sorted(
        rows,
        key=lambda row: (
            -int(row.get("execution_count", 0)),
            int(row.get("line", 0) or 0),
            str(row.get("clang_usr", "")),
        ),
    )[0]


def _port(
    name: str,
    direction: str,
    width: int = 32,
    signed: bool = True,
) -> dict[str, Any]:
    return {"name": name, "direction": direction, "width": width, "signed": signed}


def _build_interface(constants: dict[str, int]) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    samples = constants["samples_per_unit"]
    units = constants["max_units_per_group"]
    pixels = constants["max_pixels_per_group"]
    ports: list[dict[str, Any]] = []
    seen: set[str] = set()

    def add(name: str, direction: str, width: int = 32, signed: bool = True) -> str:
        if name not in seen:
            ports.append(_port(name, direction, width, signed))
            seen.add(name)
        return name

    inputs: dict[str, Any] = {}
    outputs: dict[str, Any] = {}
    helper_ports = {
        "results_valid": add("helper_results_valid", "input", 1, False),
        "qlevel": add("helper_qlevel", "input"),
        "adj_predicted_size": add("helper_adj_predicted_size", "input"),
        "flatness_info_sent": add("helper_flatness_info_sent", "input", 1, False),
        "escape_code_size": add("helper_escape_code_size", "input"),
        "ich_decision": add("helper_ich_decision", "input", 1, False),
        "max_residual_size": add("helper_max_residual_size", "input"),
        "predicted_size": add("helper_predicted_size", "input"),
        "required_size": [
            add(f"helper_required_size_{index}", "input") for index in range(samples)
        ],
    }
    inputs["helper_result_ports"] = helper_ports
    inputs["config_ports"] = {
        "bits_per_component": add("cfg_bits_per_component", "input"),
        "somewhat_flat_qp_thresh": add("cfg_somewhat_flat_qp_thresh", "input"),
    }
    inputs["argument_ports"] = {
        "unit": add("unit", "input"),
        "quantized_residuals": [
            add(f"quantized_residual_{index}", "input") for index in range(samples)
        ],
        "force_p1_ich2": add("force_p1_ich2", "input"),
    }
    state_inputs: dict[str, Any] = {
        "numBits": add("state_num_bits", "input"),
        "forceMpp": add("state_force_mpp", "input"),
        "primaryQp": add("state_primary_qp", "input"),
        "groupCount": add("state_group_count", "input"),
        "prevFirstFlat": add("state_prev_first_flat", "input"),
        "firstFlat": add("state_first_flat", "input"),
        "flatnessType": add("state_flatness_type", "input"),
        "ichSelected": add("state_ich_selected", "input"),
        "prevIchSelected": add("state_prev_ich_selected", "input"),
        "ichIndicesInGroup": add("state_ich_indices_in_group", "input"),
        "cpntBitDepth": [
            add(f"state_cpnt_bit_depth_{index}", "input") for index in range(units)
        ],
        "unitCType": [
            add(f"state_unit_c_type_{index}", "input") for index in range(units)
        ],
        "unitSspMap": [
            add(f"state_unit_ssp_map_{index}", "input") for index in range(units)
        ],
        "ichIndexUnitMap": [
            add(f"state_ich_index_unit_map_{index}", "input") for index in range(pixels)
        ],
        "ichLookup": [
            add(f"state_ich_lookup_{index}", "input") for index in range(pixels)
        ],
        "origWithinQerr": [
            add(f"state_orig_within_qerr_{index}", "input") for index in range(pixels)
        ],
        "quantizedResidualMid": [
            [
                add(f"state_quantized_residual_mid_{unit_index}_{sample}", "input")
                for sample in range(samples)
            ]
            for unit_index in range(units)
        ],
        "midpointSelected": [
            add(f"state_midpoint_selected_{index}", "input") for index in range(units)
        ],
        "predictedSize": [
            add(f"state_predicted_size_{index}", "input") for index in range(units)
        ],
        "rcSizeUnit": [
            add(f"state_rc_size_unit_{index}", "input") for index in range(units)
        ],
    }
    inputs["state_ports"] = state_inputs

    outputs["domain_valid"] = add("domain_valid", "output", 1, False)
    outputs["illegal_domain"] = add("illegal_domain", "output", 1, False)
    outputs["fatal_error"] = add("fatal_error", "output", 1, False)
    outputs["fatal_error_code"] = add("fatal_error_code", "output", 4, False)
    outputs["bounded_loop_violation"] = add("bounded_loop_violation", "output", 1, False)
    outputs["command_overflow"] = add("command_overflow", "output", 1, False)
    outputs["arithmetic_domain_violation"] = add(
        "arithmetic_domain_violation", "output", 1, False
    )
    outputs["source_order_valid"] = add("source_order_valid", "output", 1, False)
    outputs["num_bits_delta"] = add("num_bits_delta_out", "output")
    outputs["command_count"] = add("addbits_command_count", "output", 4, False)
    outputs["state_num_bits"] = add("state_num_bits_out", "output")
    outputs["state"] = {
        "flatnessType": add("state_flatness_type_out", "output"),
        "ichSelected": add("state_ich_selected_out", "output"),
        "prevIchSelected": add("state_prev_ich_selected_out", "output"),
        "midpointSelected": [
            add(f"state_midpoint_selected_{index}_out", "output") for index in range(units)
        ],
        "predictedSize": [
            add(f"state_predicted_size_{index}_out", "output") for index in range(units)
        ],
        "rcSizeUnit": [
            add(f"state_rc_size_unit_{index}_out", "output") for index in range(units)
        ],
    }
    command_ports: list[dict[str, str]] = []
    for command in range(MAX_ADDBITS_COMMANDS):
        command_ports.append(
            {
                "valid": add(f"addbits_cmd_valid_{command}", "output", 1, False),
                "ctype": add(f"addbits_cmd_ctype_{command}", "output"),
                "data": add(f"addbits_cmd_data_{command}", "output"),
                "nbits": add(f"addbits_cmd_nbits_{command}", "output", 6, False),
            }
        )
    outputs["command_ports"] = command_ports
    return ports, {"inputs": inputs, "outputs": outputs}


def build_vlc_unit_encode_contract(
    selected: dict[str, Any],
    function: dict[str, Any],
    source_dir: pathlib.Path,
    repo_root: pathlib.Path | None = None,
) -> dict[str, Any]:
    """Build a source- and dependency-hash-pinned provisional contract."""

    if selected.get("semantics_kind") != SEMANTICS_KIND:
        raise RuntimeError("selection is not the discovered VLC-unit Encode transition")
    source_dir = pathlib.Path(source_dir)
    repo_root = pathlib.Path(repo_root or pathlib.Path(__file__).resolve().parent.parent)
    _, start, end, body = _source_body(function, source_dir)
    body_hash = sha256_text(body)
    if selected.get("source_body_sha256") and str(selected["source_body_sha256"]) != body_hash:
        raise RuntimeError("immutable Encode VLC-unit source span changed")
    dependency = dict(selected.get("dependency", {}) or {})
    if not dependency:
        child_usr = str(
            (selected.get("structural_evidence", {}) or {}).get("child_clang_usr", "")
        )
        dependency = find_addbits_dependency_pin(repo_root, source_dir, child_usr)
    temporary_contract = {"dependencies": [dependency]}
    verify_dependency_pins(temporary_contract, repo_root, source_dir)
    constants = _source_constants(source_dir)
    bound = selected.get("literal_size_bound", {}) or {}
    for key, value in (
        ("samples_per_unit", constants["samples_per_unit"]),
        ("max_units_per_group", constants["max_units_per_group"]),
        ("max_pixels_per_group", constants["max_pixels_per_group"]),
        ("ich_bits", constants["ich_bits"]),
        ("max_addbits_commands", MAX_ADDBITS_COMMANDS),
    ):
        if key in bound and int(bound[key]) != value:
            raise RuntimeError(f"source bound changed for {key}")
    ports, interface_bindings = _build_interface(constants)
    function_record = {
        "clang_usr": function.get("clang_usr"),
        "name": function.get("name"),
        "qualified_name": function.get("qualified_name", function.get("name")),
        "parameters": function.get("parameters", []),
        "return_type": function.get("return_type"),
        "source_file": function.get("source_file"),
        "source_span": {"start_line": start, "end_line": end},
        "source_body_sha256": body_hash,
    }
    input_bindings = interface_bindings["inputs"]
    output_bindings = interface_bindings["outputs"]
    command_order = [
        {"stage": "flatness_flag", "source_lines": [1535, 1541], "order": "first"},
        {"stage": "first_flat", "source_lines": [1548, 1552], "order": "after_flatness_flag"},
        {"stage": "early_ich_indices", "source_lines": [1560], "order": "ascending_i"},
        {"stage": "ich_prefix", "source_lines": [1633, 1635], "order": "before_ich_indices"},
        {"stage": "ich_indices", "source_lines": [1640], "order": "ascending_i"},
        {"stage": "residual_prefix", "source_lines": [1673, 1675], "order": "before_samples"},
        {"stage": "sample_deltas", "source_lines": [1682, 1689], "order": "ascending_i"},
    ]
    state_read_ports = input_bindings["state_ports"]
    state_output_ports = output_bindings["state"]
    semantics = {
        "kind": SEMANTICS_KIND,
        "specialization": {
            "encoder_branch_only": True,
            "decoder_branch_is_not_modeled": True,
            "debug_file_io_is_not_in_rtl": True,
            "assertion_is_a_fatal_domain_sideband": True,
        },
        "constants": {
            **constants,
            "max_addbits_commands": MAX_ADDBITS_COMMANDS,
            "command_nbits_width": 6,
            "command_data_width": 32,
            "command_ctype_width": 32,
        },
        "bindings": {
            "config_ports": input_bindings["config_ports"],
            "argument_ports": input_bindings["argument_ports"],
            "helper_result_ports": input_bindings["helper_result_ports"],
            "state_input_ports": state_read_ports,
            "state_output_ports": state_output_ports,
            "state_num_bits_input": state_read_ports["numBits"],
            "state_num_bits_output": output_bindings["state_num_bits"],
            "command_count_port": output_bindings["command_count"],
            "num_bits_delta_port": output_bindings["num_bits_delta"],
            "command_ports": output_bindings["command_ports"],
            "fatal_ports": {
                key: output_bindings[key]
                for key in (
                    "domain_valid",
                    "illegal_domain",
                    "fatal_error",
                    "fatal_error_code",
                    "bounded_loop_violation",
                    "command_overflow",
                    "arithmetic_domain_violation",
                    "source_order_valid",
                )
            },
        },
        "command_stream": {
            "max_commands": MAX_ADDBITS_COMMANDS,
            "bounded": True,
            "ordered": True,
            "command_fields": ["valid", "ctype", "data", "nbits"],
            "source_order": command_order,
            "overflow_behavior": "fatal_error_code=2; no state or command commit",
            "num_bits_behavior": "state_num_bits_out = state_num_bits + sum(command nbits)",
        },
        "source_order": {
            "model": "single combinational transaction; commands are emitted in C source order",
            "stages": [
                "scalar setup and helper-result binding",
                "flatness flag and first-flat syntax elements",
                "early ICH index path with bounded six-entry scan",
                "required-size reduction and midpoint override",
                "prefix arithmetic and all-orig-within-qerr scan",
                "ICH decision and ordered ICH command emission",
                "residual prefix and three sample-delta commands",
                "state/scalar commit and numBits accounting",
            ],
        },
        "legal_domain": {
            "unit": [0, constants["max_units_per_group"] - 1],
            "force_p1_ich2": [0, 2],
            "bits_per_component": [8, 16],
            "force_mpp": [0, 1],
            "ich_selected": [0, 1],
            "ich_indices_in_group": [0, constants["max_pixels_per_group"]],
            "ich_index_unit_map": [0, constants["max_units_per_group"] - 1],
            "orig_within_qerr": [0, 1],
            "bounded_dynamic_loop_max": constants["max_pixels_per_group"],
            "fixed_loop_trip_counts": sorted(
                {
                    int(item.get("fixed_trip_count"))
                    for item in (selected.get("structural_evidence", {}) or {}).get(
                        "bounded_loop_proofs", []
                    )
                    if item.get("fixed_trip_count") is not None
                }
                or {constants["samples_per_unit"], constants["max_units_per_group"]}
            ),
            "fatal_paths": {
                "invalid_unit_or_force": "fatal_error_code=1",
                "dynamic_loop_bound_or_command_overflow": "fatal_error_code=2",
                "negative_or_oversized_nbits_or_signed_overflow": "fatal_error_code=3",
                "missing_or_invalid_helper_result": "fatal_error_code=4",
            },
            "invalid_domain_code": 1,
            "bounded_loop_code": 2,
            "arithmetic_code": 3,
            "helper_code": 4,
        },
        "state_transition": (
            "bit-true encoder branch with source-ordered AddBits command stream; update flatness, ICH, "
            "midpoint, RC-size, prediction-size, previous-ICH, and numBits state outputs"
        ),
        "adapter_boundary": (
            "the adapter consumes command slots 0..command_count-1 and binds each slot to the "
            "hash-pinned AddBits FIFO-write child"
        ),
    }
    return {
        "schema_version": 2,
        "contract_id": safe_identifier(str(function.get("name", "vlc_unit"))) + "_encode_transition",
        "status": "PROVISIONAL_SIMULATION_ONLY",
        "origin": "tool_discovered_encode_vlc_unit_compute_boundary",
        "promotion": {"status": "NOT_REQUESTED", "simulation_may_proceed": True},
        "function": function_record,
        "interface": {"ports": ports},
        "dependencies": [dependency],
        "semantics": semantics,
        "selection": {
            "basis": selected.get("selection_basis", []),
            "encode_execution_count": selected.get("execution_count"),
            "structural_evidence": selected.get("structural_evidence", {}),
            "coverage_status": "EXECUTED",
            "no_function_name_allowlist": True,
        },
    }


def build_contract(
    selected: dict[str, Any],
    function: dict[str, Any],
    source_dir: pathlib.Path,
    repo_root: pathlib.Path | None = None,
) -> dict[str, Any]:
    return build_vlc_unit_encode_contract(selected, function, source_dir, repo_root)


def _render_port_decl(port: dict[str, Any]) -> str:
    direction = str(port["direction"])
    width = int(port.get("width", 32))
    signed = " signed" if port.get("signed", True) and width > 1 else ""
    range_text = f" [{width - 1}:0]" if width > 1 else ""
    return f"    {direction} logic{signed}{range_text} {port['name']}"


def _state_array_copy_lines(
    bindings: dict[str, Any], constants: dict[str, int]
) -> list[str]:
    inputs = bindings["state_input_ports"]
    lines: list[str] = []
    for index, port in enumerate(inputs["cpntBitDepth"]):
        lines.append(f"        cpnt_depth_i[{index}] = {port};")
    for index, port in enumerate(inputs["unitCType"]):
        lines.append(f"        unit_c_type_i[{index}] = {port};")
    for index, port in enumerate(inputs["unitSspMap"]):
        lines.append(f"        unit_ssp_map_i[{index}] = {port};")
    for index, port in enumerate(inputs["ichIndexUnitMap"]):
        lines.append(f"        ich_index_unit_map_i[{index}] = {port};")
    for index, port in enumerate(inputs["ichLookup"]):
        lines.append(f"        ich_lookup_i[{index}] = {port};")
    for index, port in enumerate(inputs["origWithinQerr"]):
        lines.append(f"        orig_within_qerr_i[{index}] = {port};")
    for unit in range(constants["max_units_per_group"]):
        for sample in range(constants["samples_per_unit"]):
            port = inputs["quantizedResidualMid"][unit][sample]
            lines.append(f"        quantized_mid_i[{unit}][{sample}] = {port};")
        lines.append(f"        midpoint_selected_i[{unit}] = {inputs['midpointSelected'][unit]};")
        lines.append(f"        predicted_size_i[{unit}] = {inputs['predictedSize'][unit]};")
        lines.append(f"        rc_size_unit_i[{unit}] = {inputs['rcSizeUnit'][unit]};")
    return lines


def _state_output_lines(bindings: dict[str, Any], constants: dict[str, int]) -> list[str]:
    outputs = bindings["state_output_ports"]
    lines = [
        f"        {outputs['flatnessType']} = flatness_type_i;",
        f"        {outputs['ichSelected']} = ich_selected_i;",
        f"        {outputs['prevIchSelected']} = prev_ich_selected_i;",
    ]
    for index in range(constants["max_units_per_group"]):
        lines.extend(
            [
                f"        {outputs['midpointSelected'][index]} = midpoint_selected_i[{index}];",
                f"        {outputs['predictedSize'][index]} = predicted_size_i[{index}];",
                f"        {outputs['rcSizeUnit'][index]} = rc_size_unit_i[{index}];",
            ]
        )
    return lines


def render_vlc_unit_encode_rtl(
    contract: dict[str, Any],
    repo_root: pathlib.Path | None = None,
    source_dir: pathlib.Path | None = None,
) -> str:
    """Render the dependency plus a standalone synthesizable SV candidate."""

    root = pathlib.Path(repo_root or pathlib.Path(__file__).resolve().parent.parent)
    verify_dependency_pins(contract, root, source_dir)
    dependencies = contract.get("dependencies", []) or []
    dependency_path = _resolve_repo_path(str(dependencies[0]["module_file"]), root)
    dependency_source = dependency_path.read_text(encoding="utf-8").rstrip()
    semantics = contract.get("semantics", {}) or {}
    constants = semantics.get("constants", {}) or {}
    samples = int(constants.get("samples_per_unit", DEFAULT_SAMPLES_PER_UNIT))
    units = int(constants.get("max_units_per_group", DEFAULT_MAX_UNITS_PER_GROUP))
    pixels = int(constants.get("max_pixels_per_group", DEFAULT_MAX_PIXELS_PER_GROUP))
    if samples != 3 or units != 4 or pixels != 6:
        raise RuntimeError("unsupported VLC-unit constants for this generator")
    bindings = semantics["bindings"]
    inputs = bindings["argument_ports"]
    state_inputs = bindings["state_input_ports"]
    helpers = bindings["helper_result_ports"]
    outputs = bindings["fatal_ports"]
    module = safe_identifier(str(contract["contract_id"]))
    port_lines = [_render_port_decl(port) for port in contract["interface"]["ports"]]

    local_declarations = [
        "    integer i;",
        "    integer command_count_i;",
        "    logic signed [63:0] num_bits_delta_wide_i;",
        "    logic signed [63:0] num_bits_wide_i;",
        "    logic signed [31:0] cpnt_depth_i [0:3];",
        "    logic signed [31:0] unit_c_type_i [0:3];",
        "    logic signed [31:0] unit_ssp_map_i [0:3];",
        "    logic signed [31:0] ich_index_unit_map_i [0:5];",
        "    logic signed [31:0] ich_lookup_i [0:5];",
        "    logic signed [31:0] orig_within_qerr_i [0:5];",
        "    logic signed [31:0] quantized_mid_i [0:3][0:2];",
        "    logic signed [31:0] midpoint_selected_i [0:3];",
        "    logic signed [31:0] predicted_size_i [0:3];",
        "    logic signed [31:0] rc_size_unit_i [0:3];",
        "    logic addbits_cmd_valid_i [0:8];",
        "    logic signed [31:0] addbits_cmd_ctype_i [0:8];",
        "    logic signed [31:0] addbits_cmd_data_i [0:8];",
        "    logic [5:0] addbits_cmd_nbits_i [0:8];",
        "    logic signed [31:0] force_mpp_i;",
        "    logic signed [31:0] qp_i;",
        "    logic signed [31:0] cpnt_i;",
        "    logic signed [31:0] ssp_i;",
        "    logic signed [31:0] qlevel_i;",
        "    logic signed [31:0] adj_predicted_size_i;",
        "    logic signed [31:0] max_size_i;",
        "    logic signed [31:0] prefix_value_i;",
        "    logic signed [31:0] size_i;",
        "    logic signed [31:0] max_pfx_size_i;",
        "    logic signed [31:0] alt_pfx_i;",
        "    logic signed [31:0] alt_size_to_generate_i;",
        "    logic signed [31:0] ich_disallow_i;",
        "    logic signed [31:0] all_orig_within_qerr_i;",
        "    logic signed [31:0] early_return_i;",
        "    logic signed [31:0] flatness_type_i;",
        "    logic signed [31:0] ich_selected_i;",
        "    logic signed [31:0] prev_ich_selected_i;",
        "    logic signed [31:0] required_size_i [0:2];",
        "    logic signed [31:0] quantized_residual_i [0:2];",
        "    logic signed [31:0] component_limit_i;",
        "    logic fatal_error_i;",
        "    logic [3:0] fatal_error_code_i;",
        "    logic bounded_loop_violation_i;",
        "    logic command_overflow_i;",
        "    logic arithmetic_domain_violation_i;",
        "    logic source_order_valid_i;",
    ]
    task_source = r"""    function automatic logic [5:0] narrow_nbits(input logic signed [31:0] value);
        begin
            narrow_nbits = value[5:0];
        end
    endfunction

    function automatic logic signed [63:0] widen_signed(input logic signed [31:0] value);
        begin
            widen_signed = {{32{value[31]}}, value};
        end
    endfunction

`define emit_addbits(CTYPE_ARG, DATA_ARG, NBITS_ARG) \
        begin \
            if ((NBITS_ARG < 32'sd0) || (NBITS_ARG > 32'sd32)) begin \
                arithmetic_domain_violation_i = 1'b1; \
                fatal_error_i = 1'b1; \
                fatal_error_code_i = 4'd3; \
            end else if (command_count_i >= 9) begin \
                command_overflow_i = 1'b1; \
                bounded_loop_violation_i = 1'b1; \
                fatal_error_i = 1'b1; \
                fatal_error_code_i = 4'd2; \
            end else begin \
                addbits_cmd_valid_i[command_count_i] = 1'b1; \
                addbits_cmd_ctype_i[command_count_i] = CTYPE_ARG; \
                addbits_cmd_data_i[command_count_i] = DATA_ARG; \
                addbits_cmd_nbits_i[command_count_i] = narrow_nbits(NBITS_ARG); \
                num_bits_delta_wide_i = num_bits_delta_wide_i + widen_signed(NBITS_ARG); \
                command_count_i = command_count_i + 1; \
            end \
        end
"""

    lines: list[str] = [
        "// Hash-pinned provisional AddBits child; the adapter binds command slots to this module.",
        dependency_source,
        "",
        f"module {module}(",
        ",\n".join(port_lines),
        ");",
        "",
        "    // Generator-only candidate: no C, adapter, or promotion behavior is inlined.",
        "    // All command slots are bounded and emitted in immutable C source order.",
        *local_declarations,
        "",
        task_source.rstrip("\n"),
        "",
        "    always_comb begin",
        "        domain_valid = 1'b1;",
        "        illegal_domain = 1'b0;",
        "        fatal_error_i = 1'b0;",
        "        fatal_error_code_i = 4'd0;",
        "        bounded_loop_violation_i = 1'b0;",
        "        command_overflow_i = 1'b0;",
        "        arithmetic_domain_violation_i = 1'b0;",
        "        source_order_valid_i = 1'b1;",
        "        command_count_i = 0;",
        "        num_bits_delta_wide_i = 64'sd0;",
        "        num_bits_wide_i = {{32{state_num_bits[31]}}, state_num_bits};",
        "        state_num_bits_out = state_num_bits;",
        "        force_mpp_i = state_force_mpp;",
        "        qp_i = state_primary_qp;",
        "        cpnt_i = 32'sd0;",
        "        ssp_i = 32'sd0;",
        f"        qlevel_i = {helpers['qlevel']};",
        f"        adj_predicted_size_i = {helpers['adj_predicted_size']};",
        f"        alt_size_to_generate_i = {helpers['escape_code_size']};",
        f"        max_pfx_size_i = {helpers['max_residual_size']};",
        "        max_size_i = 32'sd0;",
        "        prefix_value_i = 32'sd0;",
        "        size_i = 32'sd0;",
        "        alt_pfx_i = 32'sd0;",
        "        ich_disallow_i = 32'sd0;",
        "        all_orig_within_qerr_i = 32'sd1;",
        "        early_return_i = 32'sd0;",
        "        flatness_type_i = state_flatness_type;",
        "        ich_selected_i = state_ich_selected;",
        "        prev_ich_selected_i = state_prev_ich_selected;",
        *_state_array_copy_lines(bindings, constants),
        f"        required_size_i[0] = {helpers['required_size'][0]};",
        f"        required_size_i[1] = {helpers['required_size'][1]};",
        f"        required_size_i[2] = {helpers['required_size'][2]};",
        "        quantized_residual_i[0] = quantized_residual_0;",
        "        quantized_residual_i[1] = quantized_residual_1;",
        "        quantized_residual_i[2] = quantized_residual_2;",
        "        component_limit_i = 32'sd0;",
    ]
    for command in range(MAX_ADDBITS_COMMANDS):
        lines.extend(
            [
                f"        addbits_cmd_valid_i[{command}] = 1'b0;",
                f"        addbits_cmd_ctype_i[{command}] = 32'sd0;",
                f"        addbits_cmd_data_i[{command}] = 32'sd0;",
                f"        addbits_cmd_nbits_i[{command}] = 6'd0;",
            ]
        )
    lines.extend(
        [
            "",
            "        // Legal-domain checks separate the C assertion/error path from RTL semantics.",
            "        if ((unit < 32'sd0) || (unit > 32'sd3) ||",
            "            (force_p1_ich2 < 32'sd0) || (force_p1_ich2 > 32'sd2) ||",
            "            (cfg_bits_per_component < 32'sd8) || (cfg_bits_per_component > 32'sd16) ||",
            "            (state_force_mpp < 32'sd0) || (state_force_mpp > 32'sd1) ||",
            "            (state_ich_selected < 32'sd0) || (state_ich_selected > 32'sd1) ||",
            "            (state_ich_indices_in_group < 32'sd0) || (state_ich_indices_in_group > 32'sd6) ||",
            f"            ({helpers['results_valid']} == 1'b0)) begin",
            "            domain_valid = 1'b0;",
            "            illegal_domain = 1'b1;",
            "            fatal_error_i = 1'b1;",
            "            fatal_error_code_i = (helper_results_valid == 1'b0) ? 4'd4 : 4'd1;",
            "        end",
            "        for (i = 0; i < 6; i = i + 1) begin",
            "            if (i < state_ich_indices_in_group) begin",
            "                if ((ich_index_unit_map_i[i] < 32'sd0) || (ich_index_unit_map_i[i] > 32'sd3) ||",
            "                    (orig_within_qerr_i[i] < 32'sd0) || (orig_within_qerr_i[i] > 32'sd1)) begin",
            "                    domain_valid = 1'b0;",
            "                    bounded_loop_violation_i = 1'b1;",
            "                    fatal_error_i = 1'b1;",
            "                    fatal_error_code_i = 4'd2;",
            "                end",
            "            end",
            "        end",
            "        if (domain_valid != 1'b0) begin",
            "            // Source lines 1514..1526: scalar setup and previous-ICH capture.",
            "            case (unit)",
            "                32'sd0: begin cpnt_i = unit_c_type_i[0]; ssp_i = unit_ssp_map_i[0]; end",
            "                32'sd1: begin cpnt_i = unit_c_type_i[1]; ssp_i = unit_ssp_map_i[1]; end",
            "                32'sd2: begin cpnt_i = unit_c_type_i[2]; ssp_i = unit_ssp_map_i[2]; end",
            "                default: begin cpnt_i = unit_c_type_i[3]; ssp_i = unit_ssp_map_i[3]; end",
            "            endcase",
            "            case (cpnt_i)",
            "                32'sd0: if ((cpnt_depth_i[0] < 32'sd1) || (cpnt_depth_i[0] > 32'sd32)) begin domain_valid = 1'b0; illegal_domain = 1'b1; fatal_error_i = 1'b1; fatal_error_code_i = 4'd1; end",
            "                32'sd1: if ((cpnt_depth_i[1] < 32'sd1) || (cpnt_depth_i[1] > 32'sd32)) begin domain_valid = 1'b0; illegal_domain = 1'b1; fatal_error_i = 1'b1; fatal_error_code_i = 4'd1; end",
            "                32'sd2: if ((cpnt_depth_i[2] < 32'sd1) || (cpnt_depth_i[2] > 32'sd32)) begin domain_valid = 1'b0; illegal_domain = 1'b1; fatal_error_i = 1'b1; fatal_error_code_i = 4'd1; end",
            "                32'sd3: if ((cpnt_depth_i[3] < 32'sd1) || (cpnt_depth_i[3] > 32'sd32)) begin domain_valid = 1'b0; illegal_domain = 1'b1; fatal_error_i = 1'b1; fatal_error_code_i = 4'd1; end",
            "                default: begin domain_valid = 1'b0; illegal_domain = 1'b1; fatal_error_i = 1'b1; fatal_error_code_i = 4'd1; end",
            "            endcase",
            "            case (cpnt_i)",
            "                32'sd0: component_limit_i = cpnt_depth_i[0] - qlevel_i;",
            "                32'sd1: component_limit_i = cpnt_depth_i[1] - qlevel_i;",
            "                32'sd2: component_limit_i = cpnt_depth_i[2] - qlevel_i;",
            "                default: component_limit_i = cpnt_depth_i[3] - qlevel_i;",
            "            endcase",
            "            if ((ssp_i < 32'sd0) || (ssp_i > 32'sd3)) begin domain_valid = 1'b0; illegal_domain = 1'b1; fatal_error_i = 1'b1; fatal_error_code_i = 4'd1; end",
            "            ich_disallow_i = ((cfg_bits_per_component == 32'sd16) && (unit == 32'sd0) &&",
            "                ((32'sd3 * qlevel_i) <= (32'sd3 - adj_predicted_size_i))) ? 32'sd1 : 32'sd0;",
            "            if (unit == 32'sd0)",
            "                prev_ich_selected_i = state_ich_selected;",
            "",
            "            // Source lines 1528..1552: flatness syntax elements precede all later commands.",
            "            if ((unit == 32'sd0) && ((state_group_count % 32'sd4) == 32'sd3) &&",
            f"                ({helpers['flatness_info_sent']} != 1'b0)) begin",
            "                if (state_prev_first_flat < 32'sd0)",
            "                    emit_addbits(ssp_i, 32'sd0, 32'sd1); // source line 1535",
            "                else",
            "                    emit_addbits(ssp_i, 32'sd1, 32'sd1); // source line 1541",
            "            end",
            "            if ((unit == 32'sd0) && ((state_group_count % 32'sd4) == 32'sd0) &&",
            "                (state_first_flat >= 32'sd0)) begin",
            "                if (qp_i >= cfg_somewhat_flat_qp_thresh)",
            "                    emit_addbits(ssp_i, state_flatness_type, 32'sd1); // source line 1548",
            "                else",
            "                    flatness_type_i = 32'sd0;",
            "                emit_addbits(ssp_i, state_first_flat, 32'sd2); // source line 1552",
            "            end",
            "",
            "            // Source lines 1556..1561: bounded early ICH path.",
            "            if ((unit > 32'sd0) && (state_ich_selected != 32'sd0)) begin",
            "                for (i = 0; i < 6; i = i + 1) begin",
            "                    if ((i < state_ich_indices_in_group) && (ich_index_unit_map_i[i] == unit))",
            "                        emit_addbits(ssp_i, ich_lookup_i[i], 32'sd5); // source line 1560",
            "                end",
            "                early_return_i = 32'sd1;",
            "            end",
            "",
            "            if (early_return_i == 32'sd0) begin",
            "                // Source lines 1564..1584: required-size reduction and MPP override.",
            "                max_size_i = 32'sd0;",
            "                for (i = 0; i < 3; i = i + 1) begin",
            "                    if (required_size_i[i] > max_size_i)",
            "                        max_size_i = required_size_i[i];",
            "                end",
            "                case (cpnt_i)",
            "                    32'sd0: if ((force_mpp_i != 32'sd0) || (max_size_i >= (cpnt_depth_i[0] - qlevel_i))) begin max_size_i = cpnt_depth_i[0] - qlevel_i; for (i = 0; i < 3; i = i + 1) required_size_i[i] = max_size_i; end",
            "                    32'sd1: if ((force_mpp_i != 32'sd0) || (max_size_i >= (cpnt_depth_i[1] - qlevel_i))) begin max_size_i = cpnt_depth_i[1] - qlevel_i; for (i = 0; i < 3; i = i + 1) required_size_i[i] = max_size_i; end",
            "                    32'sd2: if ((force_mpp_i != 32'sd0) || (max_size_i >= (cpnt_depth_i[2] - qlevel_i))) begin max_size_i = cpnt_depth_i[2] - qlevel_i; for (i = 0; i < 3; i = i + 1) required_size_i[i] = max_size_i; end",
            "                    default: if ((force_mpp_i != 32'sd0) || (max_size_i >= (cpnt_depth_i[3] - qlevel_i))) begin max_size_i = cpnt_depth_i[3] - qlevel_i; for (i = 0; i < 3; i = i + 1) required_size_i[i] = max_size_i; end",
            "                endcase",
            "                if (adj_predicted_size_i < max_size_i) begin",
            "                    prefix_value_i = max_size_i - adj_predicted_size_i;",
            "                    size_i = max_size_i;",
            "                end else begin",
            "                    prefix_value_i = 32'sd0;",
            "                    size_i = adj_predicted_size_i;",
            "                end",
            "                if (unit == 32'sd0)",
            "                    prefix_value_i = prefix_value_i + ((prev_ich_selected_i != 32'sd0) && (ich_disallow_i == 32'sd0));",
            "",
            "                // Source lines 1600..1607: bounded all-orig-within-qerr reduction.",
            "                ich_selected_i = 32'sd0;",
            "                all_orig_within_qerr_i = 32'sd1;",
            "                for (i = 0; i < 6; i = i + 1) begin",
            "                    if ((i < state_ich_indices_in_group) && (orig_within_qerr_i[i] == 32'sd0))",
            "                        all_orig_within_qerr_i = 32'sd0;",
            "                end",
            "",
            "                // Source lines 1610..1645: ICH decision and source-ordered commands.",
            "                if ((force_p1_ich2 != 32'sd1) && (unit == 32'sd0) &&",
            "                    (all_orig_within_qerr_i != 32'sd0) && (force_mpp_i == 32'sd0) &&",
            "                    (ich_disallow_i == 32'sd0)) begin",
            "                    if (prev_ich_selected_i != 32'sd0)",
            "                        alt_pfx_i = 32'sd0;",
            "                    else",
            "                        alt_pfx_i = alt_size_to_generate_i - adj_predicted_size_i;",
            f"                    if ((force_p1_ich2 == 32'sd2) || ({helpers['ich_decision']} != 1'b0)) begin",
            "                        ich_selected_i = 32'sd1;",
            "                        if (prev_ich_selected_i != 32'sd0)",
            "                            emit_addbits(ssp_i, 32'sd1, alt_pfx_i + 32'sd1); // source line 1633",
            "                        else",
            "                            emit_addbits(ssp_i, 32'sd0, alt_pfx_i); // source line 1635",
            "                        for (i = 0; i < 6; i = i + 1) begin",
            "                            if ((i < state_ich_indices_in_group) && (ich_index_unit_map_i[i] == unit))",
            "                                emit_addbits(ssp_i, ich_lookup_i[i], 32'sd5); // source line 1640",
            "                        end",
            "                        rc_size_unit_i[0] = (state_ich_indices_in_group * 32'sd5) + 32'sd1;",
            "                        for (i = 1; i < 4; i = i + 1)",
            "                            rc_size_unit_i[i] = 32'sd0;",
            "                        early_return_i = 32'sd1;",
            "                    end",
            "                end",
            "",
            "                if (early_return_i == 32'sd0) begin",
            "                    // Source lines 1650..1665: SE-size limiting syntax branch.",
            "                    max_pfx_size_i = helper_max_residual_size + (((unit == 32'sd0) && (ich_disallow_i == 32'sd0)) ? 32'sd1 : 32'sd0) - adj_predicted_size_i;",
            "                    if ((cfg_bits_per_component == 32'sd16) && (unit == 32'sd0) &&",
            "                        (qlevel_i == 32'sd0) && (ich_disallow_i != 32'sd0) &&",
            "                        ((max_pfx_size_i + (32'sd16 * 32'sd3)) > 32'sd61)) begin",
            "                        max_pfx_size_i = 32'sd61 - (32'sd16 * 32'sd3);",
            "                        prefix_value_i = max_pfx_size_i;",
            "                        if (prefix_value_i >= max_pfx_size_i) begin",
            "                            prefix_value_i = max_pfx_size_i;",
            "                            case (cpnt_i)",
            "                                32'sd0: begin size_i = cpnt_depth_i[0] - qlevel_i; max_size_i = size_i; end",
            "                                32'sd1: begin size_i = cpnt_depth_i[1] - qlevel_i; max_size_i = size_i; end",
            "                                32'sd2: begin size_i = cpnt_depth_i[2] - qlevel_i; max_size_i = size_i; end",
            "                                default: begin size_i = cpnt_depth_i[3] - qlevel_i; max_size_i = size_i; end",
            "                            endcase",
            "                            for (i = 0; i < 3; i = i + 1)",
            "                                required_size_i[i] = max_size_i;",
            "                        end",
            "                    end",
            "",
            "                    // Source lines 1671..1694: prefix then three sample commands.",
            "                    if (prefix_value_i == max_pfx_size_i)",
            "                        emit_addbits(ssp_i, 32'sd0, max_pfx_size_i); // source line 1673",
            "                    else",
            "                        emit_addbits(ssp_i, 32'sd1, prefix_value_i + 32'sd1); // source line 1675",
            "                    for (i = 0; i < 3; i = i + 1) begin",
            "                        if (max_size_i == component_limit_i) begin",
            "                            emit_addbits(ssp_i, quantized_mid_i[unit][i], size_i); // source line 1682",
            "                            midpoint_selected_i[unit] = 32'sd1;",
            "                        end else begin",
            "                            emit_addbits(ssp_i, quantized_residual_i[i], size_i); // source line 1689",
            "                            midpoint_selected_i[unit] = 32'sd0;",
            "                        end",
            "                    end",
            "                    rc_size_unit_i[unit] = (max_size_i * 32'sd3) + 32'sd1;",
            f"                    predicted_size_i[unit] = {helpers['predicted_size']};",
            "                end",
            "            end",
            "        end",
            "",
            "        if ((num_bits_delta_wide_i > 64'sd2147483647) ||",
            "            (num_bits_delta_wide_i < -64'sd2147483648)) begin",
            "            arithmetic_domain_violation_i = 1'b1;",
            "            fatal_error_i = 1'b1;",
            "            fatal_error_code_i = 4'd3;",
            "        end",
            "        num_bits_wide_i = {{32{state_num_bits[31]}}, state_num_bits} + num_bits_delta_wide_i;",
            "        if ((num_bits_wide_i > 64'sd2147483647) || (num_bits_wide_i < -64'sd2147483648)) begin",
            "            arithmetic_domain_violation_i = 1'b1;",
            "            fatal_error_i = 1'b1;",
            "            fatal_error_code_i = 4'd3;",
            "        end",
            "",
            "        if (fatal_error_i != 1'b0) begin",
            "            // Fatal paths have no observable state or command commit.",
            "            domain_valid = 1'b0;",
            "            command_count_i = 0;",
            "            num_bits_delta_wide_i = 64'sd0;",
            "            flatness_type_i = state_flatness_type;",
            "            ich_selected_i = state_ich_selected;",
            "            prev_ich_selected_i = state_prev_ich_selected;",
        ]
    )
    for index in range(units):
        lines.extend(
            [
                f"            midpoint_selected_i[{index}] = {state_inputs['midpointSelected'][index]};",
                f"            predicted_size_i[{index}] = {state_inputs['predictedSize'][index]};",
                f"            rc_size_unit_i[{index}] = {state_inputs['rcSizeUnit'][index]};",
            ]
        )
    lines.extend(
        [
            "            for (i = 0; i < 9; i = i + 1) begin",
            "                addbits_cmd_valid_i[i] = 1'b0;",
            "                addbits_cmd_ctype_i[i] = 32'sd0;",
            "                addbits_cmd_data_i[i] = 32'sd0;",
            "                addbits_cmd_nbits_i[i] = 6'd0;",
            "            end",
            "        end else begin",
            "            state_num_bits_out = num_bits_wide_i[31:0];",
            "        end",
            f"        {outputs['domain_valid']} = domain_valid;",
            f"        {outputs['illegal_domain']} = illegal_domain;",
            f"        {outputs['fatal_error']} = fatal_error_i;",
            f"        {outputs['fatal_error_code']} = fatal_error_code_i;",
            f"        {outputs['bounded_loop_violation']} = bounded_loop_violation_i;",
            f"        {outputs['command_overflow']} = command_overflow_i;",
            f"        {outputs['arithmetic_domain_violation']} = arithmetic_domain_violation_i;",
            f"        {outputs['source_order_valid']} = source_order_valid_i && !fatal_error_i;",
            f"        {bindings['num_bits_delta_port']} = num_bits_delta_wide_i[31:0];",
            f"        {bindings['command_count_port']} = command_count_i[3:0];",
            *_state_output_lines(bindings, constants),
        ]
    )
    for command, command_ports in enumerate(bindings["command_ports"]):
        lines.extend(
            [
                f"        {command_ports['valid']} = addbits_cmd_valid_i[{command}];",
                f"        {command_ports['ctype']} = addbits_cmd_ctype_i[{command}];",
                f"        {command_ports['data']} = addbits_cmd_data_i[{command}];",
                f"        {command_ports['nbits']} = addbits_cmd_nbits_i[{command}];",
            ]
        )
    lines.extend(["    end", "endmodule", ""])
    rendered = "\n".join(lines)
    rendered = rendered.replace("emit_addbits(", "`emit_addbits(")
    rendered = rendered.replace("`define `emit_addbits(", "`define emit_addbits(")
    rendered = re.sub(r"(`emit_addbits\([^\n]*\));", r"\1", rendered)
    return rendered


def render_rtl(
    contract: dict[str, Any],
    repo_root: pathlib.Path | None = None,
    source_dir: pathlib.Path | None = None,
) -> str:
    return render_vlc_unit_encode_rtl(contract, repo_root, source_dir)


def build_contract_from_documents(
    functions: Any,
    candidates: Any,
    coverage: Any,
    source_dir: pathlib.Path,
    repo_root: pathlib.Path | None = None,
) -> dict[str, Any]:
    root = pathlib.Path(repo_root or pathlib.Path(__file__).resolve().parent.parent)
    discovered = discover_vlc_unit_encode_candidates(
        functions, candidates, coverage, source_dir, root
    )
    selected = select_candidate(discovered)
    function = _by_usr(functions)[str(selected["clang_usr"])]
    return build_vlc_unit_encode_contract(selected, function, source_dir, root)


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=pathlib.Path, default=pathlib.Path.cwd())
    parser.add_argument("--source-dir", type=pathlib.Path, required=True)
    parser.add_argument("--functions", type=pathlib.Path)
    parser.add_argument("--candidates", type=pathlib.Path)
    parser.add_argument("--coverage", type=pathlib.Path)
    parser.add_argument("--output", type=pathlib.Path, required=True)
    return parser.parse_args()


def main(argv: list[str] | None = None) -> int:
    args = _parse_args() if argv is None else _parse_args_from(argv)
    root = args.root.resolve()
    functions = read_json(args.functions or root / "facts" / "functions.json")
    candidates = read_json(args.candidates or root / "facts" / "candidates.json")
    coverage = read_json(args.coverage or root / "coverage" / "coverage.json")
    discovered = discover_vlc_unit_encode_candidates(
        functions, candidates, coverage, args.source_dir.resolve(), root
    )
    if not discovered:
        raise SystemExit("DISCOVERY_INCOMPLETE: no covered structural Encode VLC-unit candidate")
    selected = select_candidate(discovered)
    function = _by_usr(functions)[str(selected["clang_usr"])]
    contract = build_vlc_unit_encode_contract(
        selected, function, args.source_dir.resolve(), root
    )
    args.output.mkdir(parents=True, exist_ok=True)
    write_json(args.output / "provisional-contract.json", contract)
    (args.output / "candidate_01.sv").write_text(
        render_vlc_unit_encode_rtl(contract, root, args.source_dir.resolve()),
        encoding="utf-8",
    )
    print(f"generated {contract['contract_id']} ({selected['execution_count']} Encode calls)")
    return 0


def _parse_args_from(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=pathlib.Path, default=pathlib.Path.cwd())
    parser.add_argument("--source-dir", type=pathlib.Path, required=True)
    parser.add_argument("--functions", type=pathlib.Path)
    parser.add_argument("--candidates", type=pathlib.Path)
    parser.add_argument("--coverage", type=pathlib.Path)
    parser.add_argument("--output", type=pathlib.Path, required=True)
    return parser.parse_args(argv)


if __name__ == "__main__":
    raise SystemExit(main())
