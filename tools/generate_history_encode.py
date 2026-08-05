#!/usr/bin/env python3
"""Discover and generate the two bounded ICH Encode transitions.

This module deliberately owns only the generator/RTL half of the transition.
The C adapter, source rewrite, execution modes, and promotion gate remain in
their existing owners.  Discovery is driven by Clang facts, immutable source
spans, and runtime coverage.  A function's spelling is retained as evidence,
but is never an admission predicate for either transition.

The generated modules use explicit child-result ports for the existing
HistoryLookup and MapQpToQlevel contracts.  This keeps SAD and quantization
error decisions in RTL while leaving composition and memory binding to the
separate adapter/integration layer.
"""

from __future__ import annotations

import argparse
import ast
import hashlib
import json
import pathlib
import re
from typing import Any, Iterable


HISTORY_REDUCTION_ROLE = "history_reduction"
HISTORY_QERR_ROLE = "history_qerr"
HISTORY_LOOKUP_KIND = "sampled_lookup_transition"
MAP_QP_KIND = "qp_mapping"
ICH_SIZE = 32
NUM_COMPONENTS = 4
QERR_SLOTS = 6


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


def sha256_text(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def safe_identifier(value: str) -> str:
    result = re.sub(r"[^A-Za-z0-9_]", "_", value).lower()
    if not result:
        result = "history_encode_transition"
    return ("c_" + result) if result[0].isdigit() else result


def _rows(document: dict[str, Any], *keys: str) -> list[dict[str, Any]]:
    for key in keys:
        value = document.get(key)
        if isinstance(value, list):
            return [item for item in value if isinstance(item, dict)]
    return []


def _function_span(function: dict[str, Any]) -> tuple[int, int]:
    start = function.get("line", function.get("start_line", 0))
    end = function.get("end_line", function.get("end", start))
    return int(start or 0), int(end or start or 0)


def _source_body(
    function: dict[str, Any], source_dir: pathlib.Path
) -> tuple[pathlib.Path, int, int, str]:
    source_value = pathlib.Path(str(function.get("source_file", "")))
    source = source_value if source_value.is_absolute() else source_dir / source_value
    start, end = _function_span(function)
    if not source.is_file():
        raise FileNotFoundError(f"source span file does not exist: {source}")
    lines = source.read_text(encoding="utf-8", errors="replace").splitlines()
    if start < 1 or end < start or end > len(lines):
        raise ValueError(
            f"invalid source span {start}:{end} for {source} ({len(lines)} lines)"
        )
    return source, start, end, "\n".join(lines[start - 1 : end])


def _is_int_type(type_name: Any) -> bool:
    return str(type_name or "").strip() in {"int", "signed int"}


def _parameter(function: dict[str, Any], name: str) -> dict[str, Any] | None:
    for item in function.get("parameters", []) or []:
        if isinstance(item, dict) and item.get("name") == name:
            return item
    return None


def _callee_usr_set(function: dict[str, Any]) -> set[str]:
    result: set[str] = set()
    for item in (function.get("callees", []) or []) + (
        function.get("calls", []) or []
    ):
        if isinstance(item, dict) and item.get("clang_usr"):
            result.add(str(item["clang_usr"]))
    return result


def _callee_name_set(function: dict[str, Any]) -> set[str]:
    result: set[str] = set()
    for item in (function.get("callees", []) or []) + (
        function.get("calls", []) or []
    ):
        if isinstance(item, dict) and item.get("name"):
            result.add(str(item["name"]))
    return result


def _field_names(function: dict[str, Any], key: str) -> set[str]:
    return {
        str(item.get("name"))
        for item in function.get(key, []) or []
        if isinstance(item, dict) and item.get("name")
    }


def _coverage_by_usr(document: dict[str, Any]) -> dict[str, dict[str, Any]]:
    """Normalize both coverage.json and the Encode frontier shape."""

    result: dict[str, dict[str, Any]] = {}
    rows = _rows(document, "functions", "reached")
    for item in rows:
        usr = str(item.get("clang_usr", ""))
        if not usr:
            continue
        nested = item.get("coverage") if isinstance(item.get("coverage"), dict) else {}
        count = nested.get("execution_count", item.get("execution_count", 0))
        try:
            execution_count = int(count or 0)
        except (TypeError, ValueError):
            execution_count = 0
        status = item.get("coverage_status")
        if status is None:
            status = "EXECUTED" if execution_count > 0 else "NOT_REACHED"
        covered = nested.get("covered", item.get("runtime_status") == "EXECUTED")
        if covered is None:
            covered = execution_count > 0
        normalized = {
            **item,
            "coverage_status": status,
            "execution_count": execution_count,
            "covered": bool(covered) or execution_count > 0,
        }
        prior = result.get(usr)
        if prior is None or execution_count > int(prior.get("execution_count", 0)):
            result[usr] = normalized
    return result


def _candidate_by_usr(document: dict[str, Any]) -> dict[str, dict[str, Any]]:
    return {
        str(item.get("clang_usr")): item
        for item in _rows(document, "functions", "candidates")
        if item.get("clang_usr")
    }


def _structural_common(
    function: dict[str, Any],
    body: str,
    *,
    require_unsigned_sample_pointer: bool = False,
) -> tuple[bool, list[str]]:
    parameters = function.get("parameters", []) or []
    evidence: list[str] = []
    if not (_is_int_type(function.get("return_type")) and len(parameters) >= 4):
        return False, evidence
    if not any(
        item.get("pointer")
        and str(item.get("type", "")).strip() == "dsc_cfg_t *"
        for item in parameters
        if isinstance(item, dict)
    ):
        return False, evidence
    if not any(
        item.get("pointer")
        and str(item.get("type", "")).strip() == "dsc_state_t *"
        for item in parameters
        if isinstance(item, dict)
    ):
        return False, evidence
    if require_unsigned_sample_pointer and not any(
        item.get("pointer")
        and "unsigned int" in str(item.get("type", ""))
        for item in parameters
        if isinstance(item, dict)
    ):
        return False, evidence
    if "HistoryLookup" not in body:
        return False, evidence
    evidence.extend(
        [
            "signed-int return with configuration/state pointers",
            "immutable source directly calls the sampled history lookup role",
        ]
    )
    if require_unsigned_sample_pointer:
        evidence.append("unsigned sample-array input is represented as explicit child-result data")
    return True, evidence


def _looks_like_history_reduction(function: dict[str, Any], body: str) -> tuple[bool, list[str]]:
    ok, evidence = _structural_common(
        function, body, require_unsigned_sample_pointer=True
    )
    if not ok:
        return False, []
    parameters = function.get("parameters", []) or []
    if len(parameters) != 4:
        return False, []
    if not re.search(r"for\s*\([^)]*<\s*ICH_SIZE\s*;", body):
        return False, []
    loops = function.get("loops", []) or []
    if int(function.get("loop_count", 0) or 0) != 1 or len(loops) != 1:
        return False, []
    loop = loops[0] if isinstance(loops[0], dict) else {}
    if loop.get("fixed_trip_count") not in {None, ICH_SIZE} and int(
        loop.get("fixed_trip_count", 0) or 0
    ) != ICH_SIZE:
        return False, []
    required_tokens = (
        "lowest_sad",
        "weighted_sad",
        "best",
        "native_422",
        "native_420",
        "dsc_version_minor",
        "abs(",
        "lowest_sad > weighted_sad",
        "best==99",
    )
    compact = re.sub(r"\s+", "", body)
    if not all(re.sub(r"\s+", "", token) in compact for token in required_tokens):
        return False, []
    evidence.extend(
        [
            "exactly one source loop is bounded by ICH_SIZE",
            "source carries lowest_sad/best cross-iteration reduction state",
            "source contains native 4:2:2, native 4:2:0, and version weight branches",
            "source uses signed abs differences and strict lowest_sad > weighted_sad",
            "source initializes and reports the no-history result 99",
        ]
    )
    return True, evidence


def _looks_like_history_qerr(function: dict[str, Any], body: str) -> tuple[bool, list[str]]:
    ok, evidence = _structural_common(function, body)
    if not ok:
        return False, []
    parameters = function.get("parameters", []) or []
    if len(parameters) != 6 or int(function.get("loop_count", 0) or 0) < 3:
        return False, []
    compact = re.sub(r"\s+", "", body)
    required_fragments = (
        "origWithinQerr",
        "QuantDivisor",
        "MapQpToQlevel",
        "ICH_SIZE",
        "PADDING_LEFT",
        "max_qerr",
        "absdiff",
        "sampModCnt",
        "hPos==0",
        "vPos==0",
        "absdiff>max_qerr",
        "return(1)",
    )
    if not all(fragment.replace(" ", "") in compact for fragment in required_fragments):
        return False, []
    loops = [item for item in function.get("loops", []) or [] if isinstance(item, dict)]
    if not any(item.get("fixed_trip_count") == 7 for item in loops):
        return False, []
    if not any(
        item.get("fixed_trip_count") in {None, ICH_SIZE}
        and "ICH_SIZE" in str(item.get("condition", ""))
        for item in loops
    ):
        return False, []
    fields_write = _field_names(function, "fields_write")
    if fields_write and not {"origWithinQerr", "history"}.intersection(fields_write):
        return False, []
    evidence.extend(
        [
            "source has the six-slot origWithinQerr indexed state transition",
            "source maps QP through QuantDivisor-derived per-component thresholds",
            "source writes upper history valid entries before the ICH scan",
            "source scans a fixed ICH_SIZE loop and uses inclusive absdiff > max_qerr rejection",
            "source has the exact first-pixel early-return guard",
        ]
    )
    return True, evidence


def discover_history_encode_candidates(
    functions_document: dict[str, Any],
    candidates_document: dict[str, Any],
    coverage_document: dict[str, Any],
    source_dir: pathlib.Path,
    dependencies: dict[str, dict[str, Any]] | None = None,
) -> list[dict[str, Any]]:
    """Return structurally admitted, Encode-covered history transitions.

    No function spelling is used to choose a role.  The optional dependency
    argument adds a USR-level call binding; when omitted, the immutable source
    call spelling is used only to recognize the already-pinned child role.
    """

    source_dir = pathlib.Path(source_dir)
    coverage_by_usr = _coverage_by_usr(coverage_document)
    candidate_by_usr = _candidate_by_usr(candidates_document)
    dependency_usrs = {
        str(item.get("function_usr"))
        for item in (dependencies or {}).values()
        if item.get("function_usr")
    }
    matches: list[dict[str, Any]] = []
    for function in _rows(functions_document, "functions"):
        usr = str(function.get("clang_usr", ""))
        coverage = coverage_by_usr.get(usr)
        if not usr or not coverage or int(coverage.get("execution_count", 0)) <= 0:
            continue
        candidate = candidate_by_usr.get(usr, {})
        if candidate.get("production_reachable") is False:
            continue
        if candidate.get("contributes_to_observable_output") is False:
            continue
        try:
            source, start, end, body = _source_body(function, source_dir)
        except (FileNotFoundError, ValueError):
            continue
        callee_usrs = _callee_usr_set(function)
        callee_names = _callee_name_set(function)
        if dependency_usrs and not dependency_usrs.intersection(callee_usrs):
            # A fixture may omit USRs, but a real facts set must bind the call
            # graph to one of the pinned dependencies.
            if "HistoryLookup" not in callee_names:
                continue
        reduction, reduction_evidence = _looks_like_history_reduction(function, body)
        qerr, qerr_evidence = _looks_like_history_qerr(function, body)
        if reduction == qerr:
            # Neither or both means the fingerprint is not closed-world.
            continue
        role = HISTORY_REDUCTION_ROLE if reduction else HISTORY_QERR_ROLE
        matches.append(
            {
                "role": role,
                "name": function.get("name"),
                "clang_usr": usr,
                "function": function,
                "execution_count": int(coverage.get("execution_count", 0)),
                "coverage": coverage,
                "source_span": {"start_line": start, "end_line": end},
                "source_file": str(source),
                "source_body": body,
                "structural_evidence": (
                    reduction_evidence if reduction else qerr_evidence
                ),
                "selection_basis": [
                    "immutable source span was read from Clang facts",
                    "Encode coverage reports a positive execution count",
                    "candidate facts retain production reachability and observable output",
                    "role was selected by loop/call/field/effect fingerprint, not function spelling",
                ],
            }
        )
    return sorted(
        matches,
        key=lambda item: (-int(item["execution_count"]), str(item.get("name", ""))),
    )


def _contract_function(contract: dict[str, Any]) -> dict[str, Any]:
    value = contract.get("function", {})
    if isinstance(value, dict):
        return value
    return {"name": str(value)}


def _contract_ports(contract: dict[str, Any]) -> list[dict[str, Any]]:
    interface = contract.get("interface", {})
    return [item for item in interface.get("ports", []) or [] if isinstance(item, dict)]


def _is_history_contract(contract: dict[str, Any]) -> bool:
    semantics = contract.get("semantics", {}) or {}
    ports = {str(item.get("name")) for item in _contract_ports(contract)}
    function = _contract_function(contract)
    parameters = function.get("parameters", []) or []
    return bool(
        semantics.get("kind") == HISTORY_LOOKUP_KIND
        and {"entry", "p_0_out", "p_1_out", "p_2_out", "p_3_out"}.issubset(ports)
        and len(parameters) == 7
        and any(
            item.get("pointer") and "unsigned int" in str(item.get("type", ""))
            for item in parameters
            if isinstance(item, dict)
        )
    )


def _is_map_contract(contract: dict[str, Any]) -> bool:
    semantics = contract.get("semantics", {}) or {}
    ports = {str(item.get("name")) for item in _contract_ports(contract)}
    function = _contract_function(contract)
    parameters = function.get("parameters", []) or []
    parameter_shape = len(parameters) == 4 or (
        not parameters and {"cpnt", "qp"}.issubset(ports)
    )
    return bool(
        semantics.get("kind") == MAP_QP_KIND
        and {"cpnt", "qp", "return_value"}.issubset(ports)
        and parameter_shape
    )


def _dependency_contract_paths(repo_root: pathlib.Path) -> list[pathlib.Path]:
    result = list((repo_root / "library" / "contracts").glob("*.json"))
    result.extend((repo_root / "rtl").glob("**/provisional-contract.json"))
    return sorted({path.resolve() for path in result if path.is_file()})


def _relative_or_absolute(path: pathlib.Path, repo_root: pathlib.Path) -> str:
    try:
        return path.resolve().relative_to(repo_root.resolve()).as_posix()
    except ValueError:
        return str(path.resolve())


def _find_dependency_module(contract_path: pathlib.Path, contract: dict[str, Any]) -> pathlib.Path:
    contract_id = safe_identifier(str(contract.get("contract_id", "")))
    candidates: list[pathlib.Path] = []
    if contract_path.parent.name == "contracts" and contract_path.parent.parent.name == "library":
        candidates.append(contract_path.parent.parent / "rtl" / f"{contract_id}.sv")
    candidates.extend(
        [
            contract_path.parent / "candidate_01.sv",
            contract_path.parent / f"{contract_id}.sv",
        ]
    )
    for candidate in candidates:
        if candidate.is_file():
            return candidate.resolve()
    raise FileNotFoundError(
        f"no RTL module found for dependency contract {contract_path}"
    )


def _frontier_dependency_evidence(
    repo_root: pathlib.Path, contract_id: str
) -> dict[str, Any]:
    frontier_path = repo_root / "coverage" / "encode" / "frontier.json"
    if not frontier_path.is_file():
        return {"status": "NOT_AVAILABLE", "path": None}
    document = read_json(frontier_path)
    for row in _rows(document, "reached"):
        if row.get("provisional_contract_id") == contract_id:
            return {
                "status": "PASS" if row.get("rtl_status") == "PROVISIONAL_RTL_PASS" else "FAIL",
                "contract_id": contract_id,
                "encode_rtl_return_invocations": int(
                    row.get("provisional_encode_rtl_return_invocations", 0) or 0
                ),
                "frontier_file": _relative_or_absolute(frontier_path, repo_root),
                "frontier_sha256": sha256_file(frontier_path),
            }
    return {"status": "NOT_FOUND", "contract_id": contract_id}


def _make_dependency_pin(
    role: str,
    contract_path: pathlib.Path,
    contract: dict[str, Any],
    module_path: pathlib.Path,
    repo_root: pathlib.Path,
) -> dict[str, Any]:
    function = _contract_function(contract)
    result = {
        "role": role,
        "contract_id": contract.get("contract_id"),
        "contract_file": _relative_or_absolute(contract_path, repo_root),
        "contract_sha256": sha256_file(contract_path),
        "module_file": _relative_or_absolute(module_path, repo_root),
        "module_sha256": sha256_file(module_path),
        "function": function.get("name"),
        "function_usr": function.get("clang_usr"),
        "source_body_sha256": function.get("source_body_sha256"),
        "semantics_kind": (contract.get("semantics", {}) or {}).get("kind"),
        "contract_status": contract.get("status"),
    }
    if role == "history_lookup":
        result["encode_evidence"] = _frontier_dependency_evidence(
            repo_root, str(contract.get("contract_id"))
        )
    else:
        verification = repo_root / "library" / "verification" / (
            f"{safe_identifier(str(contract.get('contract_id', '')))}.json"
        )
        result["verification_file"] = _relative_or_absolute(verification, repo_root)
        result["verification_sha256"] = (
            sha256_file(verification) if verification.is_file() else None
        )
        result["verification_status"] = (
            read_json(verification).get("status") if verification.is_file() else None
        )
    return result


def find_dependency_pins(repo_root: pathlib.Path) -> dict[str, dict[str, Any]]:
    """Find the existing structural child contracts and freeze their hashes."""

    repo_root = pathlib.Path(repo_root).resolve()
    found: dict[str, tuple[pathlib.Path, dict[str, Any]]] = {}
    for contract_path in _dependency_contract_paths(repo_root):
        try:
            contract = read_json(contract_path)
        except (OSError, json.JSONDecodeError):
            continue
        if _is_history_contract(contract):
            key = "history_lookup"
        elif _is_map_contract(contract):
            key = "map_qp_to_qlevel"
        else:
            continue
        if key in found:
            raise RuntimeError(f"ambiguous {key} dependency contracts")
        found[key] = (contract_path, contract)
    missing = {"history_lookup", "map_qp_to_qlevel"} - set(found)
    if missing:
        raise RuntimeError(f"missing pinned dependency contracts: {sorted(missing)}")
    result: dict[str, dict[str, Any]] = {}
    for key, (contract_path, contract) in found.items():
        module_path = _find_dependency_module(contract_path, contract)
        result[key] = _make_dependency_pin(
            key, contract_path, contract, module_path, repo_root
        )
    return result


def _resolve_repo_path(repo_root: pathlib.Path, value: str) -> pathlib.Path:
    path = pathlib.Path(value)
    return path if path.is_absolute() else repo_root / path


def verify_dependency_pins(
    contract: dict[str, Any], repo_root: pathlib.Path
) -> dict[str, Any]:
    """Re-read every pinned dependency and fail closed on a hash drift."""

    repo_root = pathlib.Path(repo_root).resolve()
    checked: list[dict[str, Any]] = []
    for dependency in contract.get("dependencies", []) or []:
        if not isinstance(dependency, dict):
            raise ValueError("dependency entry is not an object")
        contract_path = _resolve_repo_path(
            repo_root, str(dependency.get("contract_file", ""))
        )
        module_path = _resolve_repo_path(
            repo_root, str(dependency.get("module_file", ""))
        )
        if not contract_path.is_file() or not module_path.is_file():
            raise FileNotFoundError(
                f"pinned dependency missing: {contract_path} / {module_path}"
            )
        actual_contract_sha = sha256_file(contract_path)
        actual_module_sha = sha256_file(module_path)
        if actual_contract_sha != dependency.get("contract_sha256"):
            raise RuntimeError(
                f"dependency contract hash drift for {dependency.get('role')}: "
                f"{actual_contract_sha} != {dependency.get('contract_sha256')}"
            )
        if actual_module_sha != dependency.get("module_sha256"):
            raise RuntimeError(
                f"dependency module hash drift for {dependency.get('role')}: "
                f"{actual_module_sha} != {dependency.get('module_sha256')}"
            )
        checked.append(
            {
                "role": dependency.get("role"),
                "contract_file": str(contract_path),
                "module_file": str(module_path),
                "contract_sha256": actual_contract_sha,
                "module_sha256": actual_module_sha,
                "status": "PASS",
            }
        )
    required_roles = {"history_lookup"}
    if (contract.get("semantics", {}) or {}).get("kind") == "history_qerr_transition":
        required_roles.add("map_qp_to_qlevel")
    if {item.get("role") for item in checked} != required_roles:
        raise RuntimeError(
            "history transition dependency set does not match its structural child roles"
        )
    return {"status": "PASS", "dependencies": checked}


def _macro_definitions(source_dir: pathlib.Path) -> dict[str, str]:
    definitions: dict[str, str] = {}
    for path in sorted(source_dir.glob("*.[ch]")):
        text = path.read_text(encoding="utf-8", errors="replace")
        for match in re.finditer(
            r"^[ \t]*#[ \t]*define[ \t]+([A-Za-z_]\w*)[ \t]+([^\n/]+)",
            text,
            re.MULTILINE,
        ):
            definitions[match.group(1)] = match.group(2).strip()
    return definitions


def _eval_integer_expression(expression: str, definitions: dict[str, str]) -> int:
    value = expression
    for _ in range(16):
        changed = False
        for name, replacement in definitions.items():
            new_value = re.sub(rf"\b{re.escape(name)}\b", f"({replacement})", value)
            changed |= new_value != value
            value = new_value
        if not changed:
            break
    value = re.sub(r"/\*.*?\*/", "", value, flags=re.S).strip()
    tree = ast.parse(value, mode="eval")
    allowed = (
        ast.Expression,
        ast.Constant,
        ast.UnaryOp,
        ast.UAdd,
        ast.USub,
        ast.BinOp,
        ast.LShift,
        ast.RShift,
        ast.BitOr,
        ast.BitAnd,
        ast.Add,
        ast.Sub,
        ast.Mult,
        ast.FloorDiv,
        ast.Div,
        ast.Mod,
        ast.Pow,
        ast.Load,
    )
    for node in ast.walk(tree):
        if not isinstance(node, allowed):
            raise ValueError(f"unsupported integer macro expression: {expression}")
    result = eval(compile(tree, "<macro>", "eval"), {"__builtins__": {}}, {})
    if not isinstance(result, int):
        raise ValueError(f"macro expression is not an integer: {expression}")
    return result


def _source_constant(source_dir: pathlib.Path, name: str) -> int:
    definitions = _macro_definitions(source_dir)
    if name not in definitions:
        raise RuntimeError(f"source constant {name} is not defined")
    return _eval_integer_expression(definitions[name], definitions)


def _quant_divisor_table(source_dir: pathlib.Path) -> list[int]:
    text_parts = [
        path.read_text(encoding="utf-8", errors="replace")
        for path in sorted(source_dir.glob("*.c"))
    ]
    match = re.search(
        r"QuantDivisor\s*\[\s*\]\s*=\s*\{([^}]*)\}",
        "\n".join(text_parts),
        re.S,
    )
    if not match:
        raise RuntimeError("immutable source QuantDivisor table was not found")
    values = [int(item) for item in re.findall(r"\b\d+\b", match.group(1))]
    if len(values) != 17:
        raise RuntimeError(f"expected 17 QuantDivisor entries, got {len(values)}")
    return values


def _port(
    name: str,
    direction: str,
    width: int,
    *,
    signed: bool = False,
    array: list[int] | None = None,
    role: str | None = None,
) -> dict[str, Any]:
    result: dict[str, Any] = {
        "name": name,
        "direction": direction,
        "width": width,
        "signed": signed,
    }
    if array is not None:
        result["array"] = array
    if role is not None:
        result["role"] = role
    return result


def _history_child_ports(prefix: str = "history_lookup") -> list[dict[str, Any]]:
    ports: list[dict[str, Any]] = []
    for index in range(NUM_COMPONENTS):
        ports.append(
            _port(
                f"{prefix}_{index}",
                "input",
                32,
                array=[0, ICH_SIZE - 1],
                role="HistoryLookup child result",
            )
        )
    ports.append(
        _port(
            f"{prefix}_result_valid",
            "input",
            1,
            array=[0, ICH_SIZE - 1],
            role="HistoryLookup child result valid",
        )
    )
    for name, width, signed in (
        ("lookup_request_valid", 1, False),
        ("lookup_request_entry", 5, False),
        ("lookup_request_first_line", 1, False),
        ("lookup_request_is_odd_line", 1, False),
        ("lookup_request_h_pos", 32, True),
    ):
        ports.append(
            _port(
                name,
                "output",
                width,
                signed=signed,
                array=[0, ICH_SIZE - 1],
                role="HistoryLookup child request",
            )
        )
    return ports


def _reduction_ports() -> list[dict[str, Any]]:
    ports = [
        _port("cfg_native_420", "input", 1),
        _port("cfg_native_422", "input", 1),
        _port("cfg_dsc_version_minor", "input", 2),
        _port("state_v_pos", "input", 32, signed=True),
        _port("state_num_components", "input", 32, signed=True),
        _port("state_pixels_in_group", "input", 32, signed=True),
        _port("state_slice_width", "input", 32, signed=True),
        _port("h_pos", "input", 32, signed=True),
        _port("history_valid", "input", 32, signed=True, array=[0, ICH_SIZE - 1]),
    ]
    for index in range(NUM_COMPONENTS):
        ports.append(_port(f"orig_{index}", "input", 32))
    ports.extend(_history_child_ports())
    ports.extend(
        [
            _port("return_value", "output", 32, signed=True, role="selected history index"),
            _port("search_failed", "output", 1, role="no valid history entry"),
            _port("illegal_domain", "output", 1, role="legal-domain sideband"),
        ]
    )
    return ports


def _qerr_ports() -> list[dict[str, Any]]:
    ports = [
        _port("cfg_bits_per_component", "input", 32, signed=True),
        _port("cfg_native_420", "input", 1),
        _port("cfg_native_422", "input", 1),
        _port("cfg_dsc_version_minor", "input", 2),
        _port("state_v_pos", "input", 32, signed=True),
        _port("state_num_components", "input", 32, signed=True),
        _port("state_pixels_in_group", "input", 32, signed=True),
        _port("state_slice_width", "input", 32, signed=True),
        _port("h_pos", "input", 32, signed=True),
        _port("v_pos", "input", 32, signed=True),
        _port("qp", "input", 32, signed=True),
        _port("samp_mod_cnt", "input", 32, signed=True),
    ]
    for index in range(NUM_COMPONENTS):
        ports.append(_port(f"cpnt_bit_depth_{index}", "input", 32, signed=True))
    ports.append(
        _port(
            "orig_within_qerr",
            "input",
            32,
            signed=True,
            array=[0, QERR_SLOTS - 1],
            role="state input image",
        )
    )
    ports.append(
        _port(
            "history_valid",
            "input",
            32,
            signed=True,
            array=[0, ICH_SIZE - 1],
            role="history state input image",
        )
    )
    for index in range(NUM_COMPONENTS):
        ports.append(
            _port(
                f"orig_line_sample_{index}",
                "input",
                32,
                signed=True,
                role="origLine sample at h_pos + PADDING_LEFT",
            )
        )
    ports.extend(_history_child_ports())
    ports.extend(
        [
            _port(
                "map_qlevel",
                "input",
                5,
                array=[0, NUM_COMPONENTS - 1],
                role="MapQpToQlevel child result",
            ),
            _port(
                "map_request_valid",
                "output",
                1,
                array=[0, NUM_COMPONENTS - 1],
                role="MapQpToQlevel child request",
            ),
            _port("map_request_qp", "output", 5, role="MapQpToQlevel child request"),
            _port(
                "map_request_cpnt",
                "output",
                2,
                array=[0, NUM_COMPONENTS - 1],
                role="MapQpToQlevel child request",
            ),
            _port(
                "max_qerr",
                "output",
                32,
                signed=True,
                array=[0, NUM_COMPONENTS - 1],
                role="QuantDivisor[MapQpToQlevel(...)] / 2",
            ),
            _port(
                "orig_within_qerr_out",
                "output",
                32,
                signed=True,
                array=[0, QERR_SLOTS - 1],
                role="state output image",
            ),
            _port(
                "history_valid_out",
                "output",
                32,
                signed=True,
                array=[0, ICH_SIZE - 1],
                role="state output image",
            ),
            _port("return_value", "output", 32, signed=True, role="qerr predicate"),
            _port("illegal_domain", "output", 1, role="legal-domain sideband"),
        ]
    )
    return ports


def build_history_encode_contract(
    selected: dict[str, Any],
    repo_root: pathlib.Path,
    source_dir: pathlib.Path | None = None,
    dependency_pins: dict[str, dict[str, Any]] | None = None,
) -> dict[str, Any]:
    """Build a source/hash/dependency-pinned provisional contract."""

    repo_root = pathlib.Path(repo_root).resolve()
    source_dir = pathlib.Path(source_dir or pathlib.Path(selected["source_file"]).parent)
    function = selected["function"]
    source, start, end, body = _source_body(function, source_dir)
    constants = {
        "ich_size": _source_constant(source_dir, "ICH_SIZE"),
        "ich_pixels_above": _source_constant(source_dir, "ICH_PIXELS_ABOVE"),
        "padding_left": _source_constant(source_dir, "PADDING_LEFT"),
        "large_int": _source_constant(source_dir, "LARGE_INT"),
    }
    quant_divisor = _quant_divisor_table(source_dir)
    if constants["ich_size"] != ICH_SIZE:
        raise RuntimeError("source ICH_SIZE is not the bounded 32-entry domain")
    if constants["ich_pixels_above"] != 7 or constants["padding_left"] != 5:
        raise RuntimeError("source ICH geometry changed; history generator is closed-world")
    if constants["large_int"] != 1 << 30:
        raise RuntimeError("source LARGE_INT changed; reduction contract is not bit-true")
    role = str(selected["role"])
    if role not in {HISTORY_REDUCTION_ROLE, HISTORY_QERR_ROLE}:
        raise ValueError(f"unsupported history transition role: {role}")
    pins = dependency_pins or find_dependency_pins(repo_root)
    if set(pins) != {"history_lookup", "map_qp_to_qlevel"}:
        raise RuntimeError("both HistoryLookup and MapQpToQlevel must be pinned")
    dependencies = [pins["history_lookup"]]
    if role == HISTORY_QERR_ROLE:
        dependencies.append(pins["map_qp_to_qlevel"])
    interface_ports = _reduction_ports() if role == HISTORY_REDUCTION_ROLE else _qerr_ports()
    contract_id = safe_identifier(f"{selected.get('name', 'history')}_encode_history_transition")
    function_record = {
        "clang_usr": function.get("clang_usr"),
        "name": function.get("name"),
        "return_type": function.get("return_type"),
        "parameters": function.get("parameters", []),
        "source_file": function.get("source_file"),
        "source_span": {"start_line": start, "end_line": end},
        "source_body_sha256": sha256_text(body),
        "source_file_sha256": sha256_file(source),
    }
    selection = {
        "role": role,
        "basis": (
            "immutable source structure + Clang facts + positive Encode coverage; "
            "function spelling is evidence only and is not an allowlist"
        ),
        "encode_execution_count": int(selected.get("execution_count", 0)),
        "structural_evidence": selected.get("structural_evidence", []),
        "selection_basis": selected.get("selection_basis", []),
        "coverage": selected.get("coverage", {}),
    }
    semantics: dict[str, Any]
    if role == HISTORY_REDUCTION_ROLE:
        semantics = {
            "kind": "history_reduction_transition",
            "constants": constants,
            "algorithm": {
                "entry_count": ICH_SIZE,
                "lowest_sad_initial": constants["large_int"],
                "no_history_result": 99,
                "tie_rule": "strict lowest_sad > weighted_sad; first entry wins ties",
                "native_422_weights": [2, 1, 1, 2],
                "native_420_v1_or_non420_weights": [2, 1, 1, 0],
                "native_420_v2_weights": [1, 1, 1, 0],
                "signed_sample_difference": True,
                "search_failed": "return_value == 99",
            },
            "child_result_protocol": {
                "history_lookup_result_ports": "history_lookup_0..3[0..31]",
                "history_lookup_result_valid": "history_lookup_result_valid[0..31]",
                "request_ports": "lookup_request_*[0..31]",
                "sad_is_computed_in_rtl": True,
                "c_precomputed_sad_forbidden": True,
            },
        }
        legal_domain = {
            "entry": [0, 31],
            "num_components": [3, 4],
            "native_flags_not_both_set": True,
            "num_components_matches_native_422": True,
            "pixels_in_group": 3,
            "slice_width_minimum": {"native": 5, "non_native": 7},
            "h_pos": "0 <= h_pos < state_slice_width",
            "history_lookup_result_valid_for_requested_entries": True,
        }
        obligations = [
            "bind every history_lookup result port to the hash-pinned HistoryLookup child",
            "compare return_value/search_failed/illegal_domain in the adapter",
            "preserve source-order first-winner tie behavior",
            "human review remains required before promotion",
        ]
    else:
        semantics = {
            "kind": "history_qerr_transition",
            "constants": {**constants, "quant_divisor": quant_divisor},
            "algorithm": {
                "entry_count": ICH_SIZE,
                "qerr_slots": QERR_SLOTS,
                "ich_bits_nonzero": True,
                "modified_qp": "min(2*bits_per_component-1, qp+2)",
                "max_qerr": "QuantDivisor[MapQpToQlevel(modified_qp, cpnt)] / 2",
                "threshold": "inclusive; reject only when absdiff > max_qerr",
                "upper_valid_update": "history.valid[25..31] before the 32-entry scan",
                "first_pixel_early_return": "(h_pos == 0) && (v_pos == 0)",
                "entry_scan": "fixed 32 entries; valid candidate may early-break on a complete hit",
                "component_scan": "must complete all active components after a mismatch",
            },
            "child_result_protocol": {
                "history_lookup_result_ports": "history_lookup_0..3[0..31]",
                "history_lookup_result_valid": "history_lookup_result_valid[0..31]",
                "map_qlevel_result_ports": "map_qlevel[0..3]",
                "request_ports": "lookup_request_* and map_request_*",
                "qerr_is_computed_in_rtl": True,
                "c_precomputed_qerr_forbidden": True,
            },
        }
        legal_domain = {
            "entry": [0, 31],
            "samp_mod_cnt": [0, 5],
            "num_components": [3, 4],
            "native_flags_not_both_set": True,
            "num_components_matches_native_422": True,
            "pixels_in_group": 3,
            "bits_per_component": [8, 10, 12, 14, 16],
            "qp": [0, 31],
            "slice_width_minimum": {"native": 5, "non_native": 7},
            "history_lookup_result_valid_for_requested_entries": True,
            "map_qlevel": [0, 16],
        }
        obligations = [
            "bind map_qlevel ports to the hash-pinned MapQpToQlevel child",
            "bind every history_lookup result port to the hash-pinned HistoryLookup child",
            "commit only origWithinQerr[sampModCnt] and history.valid[25..31] state outputs",
            "compare qerr result and state image in the adapter",
            "human review remains required before promotion",
        ]
    return {
        "schema_version": 1,
        "contract_id": contract_id,
        "status": "PROVISIONAL_SIMULATION_ONLY",
        "origin": "tool_discovered_encode_history_transition",
        "function": function_record,
        "interface": {"ports": interface_ports},
        "selection": selection,
        "dependencies": dependencies,
        "semantics": semantics,
        "legal_domain": legal_domain,
        "obligations": obligations,
        "promotion": {
            "simulation_may_proceed": True,
            "status": "BLOCKED_PENDING_HUMAN_CONTRACT_REVIEW",
        },
    }


def build_contract(
    selected: dict[str, Any],
    repo_root: pathlib.Path,
    source_dir: pathlib.Path | None = None,
    dependency_pins: dict[str, dict[str, Any]] | None = None,
) -> dict[str, Any]:
    """Compatibility alias for callers that use the other generators."""

    return build_history_encode_contract(
        selected, repo_root, source_dir, dependency_pins
    )


def _render_port_decl(port: dict[str, Any]) -> str:
    direction = str(port["direction"])
    signed = " signed" if port.get("signed") else ""
    width = int(port.get("width", 1))
    packed = "logic" if width == 1 else f"logic [{width - 1}:0]"
    if signed:
        packed = packed.replace("logic", "logic signed", 1)
    array = port.get("array")
    unpacked = f" [{int(array[0])}:{int(array[1])}]" if array else ""
    return f"    {direction} {packed} {port['name']}{unpacked}"


def _render_module_header(contract: dict[str, Any]) -> str:
    module = safe_identifier(str(contract["contract_id"]))
    declarations = [_render_port_decl(port) for port in _contract_ports(contract)]
    return "module " + module + " (\n" + ",\n".join(declarations) + "\n);"


def _render_reduction_rtl(contract: dict[str, Any]) -> str:
    header = _render_module_header(contract)
    return f"""{header}
    integer j;
    logic signed [32:0] diff0_i;
    logic signed [32:0] diff1_i;
    logic signed [32:0] diff2_i;
    logic signed [32:0] diff3_i;
    logic signed [63:0] weighted_sad_i;
    logic signed [63:0] lowest_sad_i;
    logic signed [31:0] best_i;
    logic first_line_i;
    logic illegal_i;

    function automatic logic signed [32:0] abs_i33(input logic signed [32:0] value);
        begin
            if (value < 0)
                abs_i33 = -value;
            else
                abs_i33 = value;
        end
    endfunction

    always_comb begin
        return_value = 32'sd99;
        search_failed = 1'b1;
        illegal_domain = 1'b0;
        best_i = 32'sd99;
        lowest_sad_i = 64'sd{int(contract['semantics']['algorithm']['lowest_sad_initial'])};
        first_line_i = 1'b0;
        diff0_i = 33'sd0;
        diff1_i = 33'sd0;
        diff2_i = 33'sd0;
        diff3_i = 33'sd0;
        weighted_sad_i = 64'sd0;
        illegal_i = 1'b0;

        for (j = 0; j < {ICH_SIZE}; j = j + 1) begin
            lookup_request_valid[j] = 1'b0;
            lookup_request_entry[j] = j[4:0];
            lookup_request_first_line[j] = 1'b0;
            lookup_request_is_odd_line[j] = 1'b0;
            lookup_request_h_pos[j] = h_pos;
        end

        if ((cfg_native_420 != 0) && (cfg_native_422 != 0)) illegal_i = 1'b1;
        if (!((state_num_components == 32'sd3) || (state_num_components == 32'sd4))) illegal_i = 1'b1;
        if ((cfg_native_422 != 0) && (state_num_components != 32'sd4)) illegal_i = 1'b1;
        if ((cfg_native_422 == 0) && (state_num_components != 32'sd3)) illegal_i = 1'b1;
        if (state_pixels_in_group != 32'sd3) illegal_i = 1'b1;
        if ((state_v_pos < 0) || (h_pos < 0) || (state_slice_width <= 0) || (h_pos >= state_slice_width)) illegal_i = 1'b1;
        if (((cfg_native_420 != 0) || (cfg_native_422 != 0)) && (state_slice_width < 5)) illegal_i = 1'b1;
        if ((cfg_native_420 == 0) && (cfg_native_422 == 0) && (state_slice_width < 7)) illegal_i = 1'b1;

        first_line_i = (state_v_pos == 0) || ((cfg_native_420 != 0) && (state_v_pos == 1));
        if (!illegal_i) begin
            for (j = 0; j < {ICH_SIZE}; j = j + 1) begin
                lookup_request_valid[j] = (history_valid[j] != 0);
                lookup_request_first_line[j] = first_line_i;
                lookup_request_is_odd_line[j] = (state_v_pos[0] != 0);
                if ((history_valid[j] != 0) && (history_lookup_result_valid[j] == 0))
                    illegal_i = 1'b1;
            end
        end

        if (!illegal_i) begin
            for (j = 0; j < {ICH_SIZE}; j = j + 1) begin
                if (history_valid[j] != 0) begin
                    diff0_i = $signed({{1'b0, history_lookup_0[j]}}) - $signed({{1'b0, orig_0}});
                    diff1_i = $signed({{1'b0, history_lookup_1[j]}}) - $signed({{1'b0, orig_1}});
                    diff2_i = $signed({{1'b0, history_lookup_2[j]}}) - $signed({{1'b0, orig_2}});
                    diff3_i = $signed({{1'b0, history_lookup_3[j]}}) - $signed({{1'b0, orig_3}});
                    if (cfg_native_422 != 0)
                        weighted_sad_i = (64'sd2 * abs_i33(diff0_i)) + abs_i33(diff1_i) + abs_i33(diff2_i) + (64'sd2 * abs_i33(diff3_i));
                    else if ((cfg_native_420 == 0) || (cfg_dsc_version_minor == 2'd1))
                        weighted_sad_i = (64'sd2 * abs_i33(diff0_i)) + abs_i33(diff1_i) + abs_i33(diff2_i);
                    else
                        weighted_sad_i = abs_i33(diff0_i) + abs_i33(diff1_i) + abs_i33(diff2_i);
                    if (lowest_sad_i > weighted_sad_i) begin
                        lowest_sad_i = weighted_sad_i;
                        best_i = j;
                    end
                end
            end
        end

        illegal_domain = illegal_i;
        if (!illegal_i) begin
            return_value = best_i;
            search_failed = (best_i == 32'sd99);
        end
    end
endmodule
"""


def _render_qerr_rtl(contract: dict[str, Any]) -> str:
    header = _render_module_header(contract)
    constants = contract["semantics"]["constants"]
    quant_divisor = constants["quant_divisor"]
    cases = "\n".join(
        f"            5'd{index}: quant_divisor = 32'sd{value};"
        for index, value in enumerate(quant_divisor)
    )
    return f"""{header}
    integer i;
    integer j;
    logic signed [32:0] diff_i;
    logic signed [32:0] absdiff_i;
    logic signed [31:0] max_qerr_i [0:3];
    logic signed [31:0] history_valid_next [0:31];
    logic signed [31:0] orig_within_next [0:5];
    logic signed [63:0] qp_candidate_i;
    logic signed [63:0] modified_qp_i;
    logic first_line_i;
    logic candidate_hit_i;
    logic found_i;
    logic illegal_i;
    logic signed [31:0] quant_divisor_i;

    function automatic logic signed [32:0] abs_i33(input logic signed [32:0] value);
        begin
            if (value < 0)
                abs_i33 = -value;
            else
                abs_i33 = value;
        end
    endfunction

    function automatic logic signed [31:0] quant_divisor(input logic [4:0] qlevel);
        begin
            quant_divisor = 32'sd0;
            case (qlevel)
{cases}
                default: quant_divisor = 32'sd0;
            endcase
        end
    endfunction

    always_comb begin
        return_value = 32'sd0;
        illegal_domain = 1'b0;
        illegal_i = 1'b0;
        found_i = 1'b0;
        candidate_hit_i = 1'b0;
        first_line_i = 1'b0;
        qp_candidate_i = 64'sd0;
        modified_qp_i = 64'sd0;
        diff_i = 33'sd0;
        absdiff_i = 33'sd0;
        quant_divisor_i = 32'sd0;
        map_request_qp = 5'd0;

        for (i = 0; i < {NUM_COMPONENTS}; i = i + 1) begin
            max_qerr_i[i] = 32'sd0;
            max_qerr[i] = 32'sd0;
            map_request_valid[i] = 1'b0;
            map_request_cpnt[i] = i[1:0];
        end
        for (i = 0; i < {QERR_SLOTS}; i = i + 1)
            orig_within_next[i] = orig_within_qerr[i];
        for (j = 0; j < {ICH_SIZE}; j = j + 1) begin
            history_valid_next[j] = history_valid[j];
            lookup_request_valid[j] = 1'b0;
            lookup_request_entry[j] = j[4:0];
            lookup_request_first_line[j] = 1'b0;
            lookup_request_is_odd_line[j] = 1'b0;
            lookup_request_h_pos[j] = h_pos;
        end

        if ((cfg_native_420 != 0) && (cfg_native_422 != 0)) illegal_i = 1'b1;
        if (!((state_num_components == 32'sd3) || (state_num_components == 32'sd4))) illegal_i = 1'b1;
        if ((cfg_native_422 != 0) && (state_num_components != 32'sd4)) illegal_i = 1'b1;
        if ((cfg_native_422 == 0) && (state_num_components != 32'sd3)) illegal_i = 1'b1;
        if (state_pixels_in_group != 32'sd3) illegal_i = 1'b1;
        if ((samp_mod_cnt < 0) || (samp_mod_cnt >= {QERR_SLOTS})) illegal_i = 1'b1;
        if ((h_pos < 0) || (v_pos < 0) || (state_v_pos < 0) || (state_slice_width <= 0) || (h_pos >= state_slice_width)) illegal_i = 1'b1;
        if (((cfg_native_420 != 0) || (cfg_native_422 != 0)) && (state_slice_width < 5)) illegal_i = 1'b1;
        if ((cfg_native_420 == 0) && (cfg_native_422 == 0) && (state_slice_width < 7)) illegal_i = 1'b1;
        if ((cfg_bits_per_component != 32'sd8) && (cfg_bits_per_component != 32'sd10) && (cfg_bits_per_component != 32'sd12) && (cfg_bits_per_component != 32'sd14) && (cfg_bits_per_component != 32'sd16)) illegal_i = 1'b1;
        if ((qp < 0) || (qp > 31)) illegal_i = 1'b1;

        // The C function clears the selected slot before either early return.
        if ((samp_mod_cnt >= 0) && (samp_mod_cnt < {QERR_SLOTS}))
            orig_within_next[samp_mod_cnt] = 32'sd0;

        if (!illegal_i && !((h_pos == 0) && (v_pos == 0))) begin
            qp_candidate_i = (64'sd2 * cfg_bits_per_component) - 64'sd1;
            modified_qp_i = qp + 64'sd2;
            if (modified_qp_i > qp_candidate_i)
                modified_qp_i = qp_candidate_i;
            map_request_qp = modified_qp_i[4:0];
            for (i = 0; i < {NUM_COMPONENTS}; i = i + 1) begin
                map_request_valid[i] = (i < state_num_components);
                if (map_request_valid[i] && (map_qlevel[i] > 5'd16))
                    illegal_i = 1'b1;
                if (map_request_valid[i]) begin
                    quant_divisor_i = quant_divisor(map_qlevel[i]);
                    max_qerr_i[i] = quant_divisor_i >>> 1;
                    max_qerr[i] = max_qerr_i[i];
                end
            end

            // Source order: update UL/U/UR validity, then scan history.
            if (((cfg_native_420 == 0) && (state_v_pos > 0)) || ((cfg_native_420 != 0) && (state_v_pos > 1))) begin
                for (i = 25; i < {ICH_SIZE}; i = i + 1)
                    history_valid_next[i] = 32'sd1;
            end

            first_line_i = (v_pos == 0) || ((cfg_native_420 != 0) && (v_pos == 1));
            for (j = 0; j < {ICH_SIZE}; j = j + 1) begin
                lookup_request_valid[j] = (history_valid_next[j] != 0);
                lookup_request_first_line[j] = first_line_i;
                lookup_request_is_odd_line[j] = (v_pos[0] != 0);
                if ((history_valid_next[j] != 0) && (history_lookup_result_valid[j] == 0))
                    illegal_i = 1'b1;
                if (history_valid_next[j] != 0) begin
                    candidate_hit_i = 1'b1;
                    for (i = 0; i < {NUM_COMPONENTS}; i = i + 1) begin
                        if (i < state_num_components) begin
                            case (i)
                                0: diff_i = $signed({{1'b0, history_lookup_0[j]}}) - $signed({{orig_line_sample_0[31], orig_line_sample_0}});
                                1: diff_i = $signed({{1'b0, history_lookup_1[j]}}) - $signed({{orig_line_sample_1[31], orig_line_sample_1}});
                                2: diff_i = $signed({{1'b0, history_lookup_2[j]}}) - $signed({{orig_line_sample_2[31], orig_line_sample_2}});
                                default: diff_i = $signed({{1'b0, history_lookup_3[j]}}) - $signed({{orig_line_sample_3[31], orig_line_sample_3}});
                            endcase
                            absdiff_i = abs_i33(diff_i);
                            if (absdiff_i > max_qerr_i[i])
                                candidate_hit_i = 1'b0;
                        end
                    end
                    if (candidate_hit_i && !found_i)
                        found_i = 1'b1;
                end
            end
            if (found_i) begin
                orig_within_next[samp_mod_cnt] = 32'sd1;
                return_value = 32'sd1;
            end
        end

        illegal_domain = illegal_i;
        for (i = 0; i < {QERR_SLOTS}; i = i + 1)
            orig_within_qerr_out[i] = orig_within_next[i];
        for (j = 0; j < {ICH_SIZE}; j = j + 1)
            history_valid_out[j] = history_valid_next[j];
        if (illegal_i)
            return_value = 32'sd0;
    end
endmodule
"""


def render_history_encode_rtl(contract: dict[str, Any]) -> str:
    kind = (contract.get("semantics", {}) or {}).get("kind")
    if kind == "history_reduction_transition":
        return _render_reduction_rtl(contract)
    if kind == "history_qerr_transition":
        return _render_qerr_rtl(contract)
    raise ValueError(f"unsupported history RTL semantics: {kind}")


def render_rtl(contract: dict[str, Any]) -> str:
    return render_history_encode_rtl(contract)


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=pathlib.Path, required=True)
    parser.add_argument("--source-dir", type=pathlib.Path, required=True)
    parser.add_argument("--functions", type=pathlib.Path, required=True)
    parser.add_argument("--candidates", type=pathlib.Path, required=True)
    parser.add_argument("--coverage", type=pathlib.Path, required=True)
    parser.add_argument(
        "--output",
        "--output-dir",
        dest="output",
        type=pathlib.Path,
        required=True,
    )
    parser.add_argument(
        "--role", choices=("all", HISTORY_REDUCTION_ROLE, HISTORY_QERR_ROLE), default="all"
    )
    return parser.parse_args()


def main() -> int:
    args = _parse_args()
    root = args.root.resolve()
    source_dir = args.source_dir.resolve()
    dependencies = find_dependency_pins(root)
    selected = discover_history_encode_candidates(
        read_json(args.functions),
        read_json(args.candidates),
        read_json(args.coverage),
        source_dir,
        dependencies,
    )
    if args.role != "all":
        selected = [item for item in selected if item["role"] == args.role]
    if not selected:
        raise SystemExit("no structurally admitted covered history Encode transition")
    args.output.mkdir(parents=True, exist_ok=True)
    emitted: list[dict[str, Any]] = []
    for item in selected:
        contract = build_history_encode_contract(
            item, root, source_dir, dependencies
        )
        if args.role != "all" and len(selected) == 1:
            contract_path = args.output / "provisional-contract.json"
            rtl_path = args.output / "candidate_01.sv"
        else:
            contract_path = args.output / f"{contract['contract_id']}.json"
            rtl_path = args.output / f"{contract['contract_id']}.sv"
        write_json(contract_path, contract)
        rtl_path.write_text(render_history_encode_rtl(contract), encoding="utf-8")
        emitted.append(
            {
                "role": item["role"],
                "function": item.get("name"),
                "contract": str(contract_path),
                "rtl": str(rtl_path),
                "contract_sha256": sha256_file(contract_path),
                "rtl_sha256": sha256_file(rtl_path),
            }
        )
    print(json.dumps({"status": "PASS", "generated": emitted}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
