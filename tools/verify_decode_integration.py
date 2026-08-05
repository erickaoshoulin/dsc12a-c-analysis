#!/usr/bin/env python3
"""Run every verified Decode RTL adapter together in one whole-frame binary.

The immutable C model remains the frame oracle and orchestration shell.  This
tool discovers provisional RTL from executed receipts, rewrites all selected C
boundaries in one copied source tree, compiles each Verilog module through
Verilator, and checks C_ONLY/SHADOW/RTL_RETURN decoded frames byte-for-byte.
"""

from __future__ import annotations

import argparse
import concurrent.futures
import json
import os
import pathlib
import re
import shutil
import tempfile
import time
from typing import Any

try:
    from cicd_agent import (
        Agent,
        contract_function,
        file_hash,
        read_json,
        safe_identifier,
        scrub_paths,
        write_json,
    )
except ModuleNotFoundError:  # Imported as tools.verify_decode_integration in tests.
    from tools.cicd_agent import (
        Agent,
        contract_function,
        file_hash,
        read_json,
        safe_identifier,
        scrub_paths,
        write_json,
    )


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=pathlib.Path, required=True)
    parser.add_argument("--artifact", type=pathlib.Path, required=True)
    parser.add_argument("--scope", choices=("smoke", "all"), default="smoke")
    parser.add_argument("--jobs", type=int, default=min(4, os.cpu_count() or 1))
    return parser.parse_args()


def discover_decode_candidates(root: pathlib.Path) -> list[dict[str, Any]]:
    """Select candidates from proof receipts, never from a function allowlist."""
    selected: list[dict[str, Any]] = []
    coverage = read_json(root / "coverage" / "decode" / "coverage.json", {}) or {}
    executed_usrs = {
        str(item.get("clang_usr"))
        for item in coverage.get("functions", []) or []
        if item.get("coverage_status") == "EXECUTED"
    }
    manifest = read_json(root / "library" / "manifest.json", {}) or {}
    stable_functions: set[str] = set()
    for component in sorted(
        manifest.get("components", []) or [],
        key=lambda item: str(item.get("contract_id", "")),
    ):
        if component.get("status") != "PASS":
            continue
        contract_path = root / "library" / str(component.get("contract_file", ""))
        candidate_path = root / "library" / str(component.get("module_file", ""))
        verification_path = root / "library" / str(component.get("verification_file", ""))
        if not contract_path.is_file():
            continue
        contract = read_json(contract_path, {}) or {}
        function = contract_function(contract)
        if str(function.get("clang_usr")) not in executed_usrs:
            continue
        if not candidate_path.is_file():
            raise RuntimeError(
                f"stable Decode RTL is missing for {function.get('name')}"
            )
        expected_rtl_hash = str(component.get("module_sha256", ""))
        actual_rtl_hash = file_hash(candidate_path)
        if expected_rtl_hash and actual_rtl_hash != expected_rtl_hash:
            raise RuntimeError(
                f"stable Decode RTL hash mismatch for {function.get('name')}"
            )
        slug = safe_identifier(
            str(contract.get("contract_id") or function.get("name"))
        ).lower()
        function_name = str(function.get("name", ""))
        stable_functions.add(function_name)
        selected.append({
            "slug": slug,
            "rtl_tier": "STABLE_RTL",
            "artifact": root / "library" / str(component.get("artifact_dir", "")),
            "contract_path": contract_path,
            "contract": contract,
            "candidate_path": candidate_path,
            "module": str(component.get("module") or contract.get("contract_id")),
            "function": function_name,
            "clang_usr": str(function["clang_usr"]),
            "contract_sha256": file_hash(contract_path),
            "candidate_sha256": actual_rtl_hash,
            "source_matrix_sha256": (
                file_hash(verification_path) if verification_path.is_file() else None
            ),
        })
    provisional_root = root / "rtl" / "decode-candidates"
    for contract_path in sorted(provisional_root.glob("*/provisional-contract.json")):
        candidate_path = contract_path.parent / "candidate_01.sv"
        matrix_path = contract_path.parent / "matrix-receipt.json"
        contract = read_json(contract_path, {}) or {}
        matrix = read_json(matrix_path, {}) or {}
        decode_modes = (matrix.get("decode", {}) or {}).get("modes", {}) or {}
        exercised = all(
            (decode_modes.get(mode, {}) or {}).get("status") == "PASS"
            and int((decode_modes.get(mode, {}) or {}).get("total_rtl_invocations", 0)) > 0
            for mode in ("SHADOW", "RTL_RETURN")
        )
        if matrix.get("status") != "PASS" or not exercised or not candidate_path.is_file():
            continue
        function = contract_function(contract)
        if not function.get("name") or not function.get("clang_usr"):
            continue
        if str(function["name"]) in stable_functions:
            continue
        slug = safe_identifier(str(contract.get("contract_id") or function["name"])).lower()
        selected.append({
            "slug": slug,
            "rtl_tier": "PROVISIONAL_RTL_PASS",
            "artifact": contract_path.parent,
            "contract_path": contract_path,
            "contract": contract,
            "candidate_path": candidate_path,
            "module": str(contract.get("contract_id")),
            "function": str(function["name"]),
            "clang_usr": str(function["clang_usr"]),
            "contract_sha256": file_hash(contract_path),
            "candidate_sha256": file_hash(candidate_path),
            "source_matrix_sha256": file_hash(matrix_path),
        })
    slugs = [item["slug"] for item in selected]
    if len(slugs) != len(set(slugs)):
        raise RuntimeError("discovered Decode contracts do not have unique identifiers")
    if not selected:
        raise RuntimeError("no matrix-proven Decode RTL candidates were discovered")
    return selected


def source_order_candidates(
    candidates: list[dict[str, Any]], functions_facts: dict[str, Any]
) -> list[dict[str, Any]]:
    """Put selected callers before their selected callees for nested rewriting."""
    by_name = {item["function"]: item for item in candidates}
    functions = functions_facts.get("functions", []) if isinstance(functions_facts, dict) else []
    graph: dict[str, set[str]] = {name: set() for name in by_name}
    indegree = {name: 0 for name in by_name}
    for function in functions:
        caller = str(function.get("name", ""))
        if caller not in by_name:
            continue
        for callee_record in function.get("callees", []) or []:
            callee = str(callee_record.get("name", ""))
            if callee in by_name and callee != caller and callee not in graph[caller]:
                graph[caller].add(callee)
                indegree[callee] += 1
    ready = sorted(name for name, value in indegree.items() if value == 0)
    ordered_names: list[str] = []
    while ready:
        name = ready.pop(0)
        ordered_names.append(name)
        for callee in sorted(graph[name]):
            indegree[callee] -= 1
            if indegree[callee] == 0:
                ready.append(callee)
                ready.sort()
    # A recursive call cycle is not expected here, but deterministic fallback
    # is safer than silently dropping a proven candidate.
    ordered_names.extend(sorted(set(by_name) - set(ordered_names)))
    return [by_name[name] for name in ordered_names]


def namespace_adapter_text(
    text: str,
    *,
    slug: str,
    function_name: str,
    keep_time_definition: bool = False,
) -> str:
    """Make one generated adapter coexist with every other generated adapter."""
    upper = safe_identifier(slug).upper()
    original_default = f"{function_name}_original"
    original_unique = f"{function_name}_original_{slug}"
    text = re.sub(rf"\b{re.escape(original_default)}\b", original_unique, text)
    text = re.sub(r"\bdsc_cicd_", f"dsc_cicd_{slug}_", text)
    text = re.sub(r"\bDSC_CICD_", f"DSC_CICD_{upper}_", text)
    # All adapters share one runtime mode.  Other DSC_CICD_* identifiers are
    # deliberately namespaced because several generated ABI headers use the
    # same macro/type names with different dimensions.
    text = text.replace(f'"DSC_CICD_{upper}_MODE"', '"DSC_CICD_MODE"')
    text = text.replace(
        f"DSC_CICD_{upper}_OVERLAY_METRICS calls=",
        f"DSC_CICD_OVERLAY_METRICS candidate={slug} calls=",
    )
    mode_marker = f"static int dsc_cicd_{slug}_mode(void) {{\n"
    if mode_marker in text:
        text = text.replace(
            mode_marker,
            "extern int dsc_cicd_multi_oracle_depth;\n"
            + mode_marker
            + "    if (dsc_cicd_multi_oracle_depth > 0) return 0;\n",
            1,
        )
    if not keep_time_definition:
        text = text.replace("double sc_time_stamp() { return 0.0; }\n", "")
    return text


def namespaced_filename(name: str, slug: str) -> str:
    if name.startswith("dsc_cicd_"):
        return name.replace("dsc_cicd_", f"dsc_cicd_{slug}_", 1)
    if name == "rtl_bridge.cpp":
        return f"dsc_cicd_{slug}_rtl_bridge.cpp"
    return f"dsc_cicd_{slug}_{name}"


def route_adapter_child_dispatchers(
    text: str,
    *,
    own_function: str,
    candidates: list[dict[str, Any]],
) -> tuple[str, list[dict[str, str]]]:
    """Route calls made by one generated adapter through selected children.

    The Clang source rewriter intentionally skips generated ``dsc_cicd_*``
    files.  A composed adapter can nevertheless call another selected C
    boundary while preparing explicit child results.  Once the immutable C
    copy has been rewritten, the child's original public symbol no longer
    exists, so those generated declarations/calls must target the child's
    namespaced dispatcher too.

    Selection remains receipt driven: every possible replacement comes from
    ``candidates``.  Matching requires an identifier followed by ``(``, which
    avoids touching similarly named fields, strings, or the adapter's unique
    ``*_original_*`` oracle symbol.
    """

    routed: list[dict[str, str]] = []
    result = text
    for candidate in candidates:
        function = str(candidate.get("function", ""))
        slug = str(candidate.get("slug", ""))
        if not function or not slug or function == own_function:
            continue
        dispatcher = f"dsc_cicd_{slug}_invoke"
        pattern = re.compile(
            rf"(?<![A-Za-z0-9_]){re.escape(function)}(?=\s*\()"
        )
        result, replacements = pattern.subn(dispatcher, result)
        if replacements:
            routed.append({
                "function": function,
                "dispatcher": dispatcher,
                "replacements": str(replacements),
            })
    return result, routed


def render_private_oracle_wrapper(candidate: dict[str, Any]) -> str:
    """Wrap one renamed C implementation in a nested-oracle C_ONLY scope."""

    function = contract_function(candidate["contract"])
    parameters = function.get("parameters", []) or []
    declarations = ", ".join(
        f"{str(parameter.get('type', 'int')).strip()} "
        f"{str(parameter.get('name', '')).strip()}"
        for parameter in parameters
    )
    arguments = ", ".join(
        str(parameter.get("name", "")).strip() for parameter in parameters
    )
    return_type = str(function.get("return_type", "void")).strip()
    wrapper = str(candidate["original_name"])
    implementation = str(candidate["original_impl_name"])
    call = f"{implementation}({arguments})"
    if return_type == "void":
        body = (
            "    ++dsc_cicd_multi_oracle_depth;\n"
            f"    {call};\n"
            "    --dsc_cicd_multi_oracle_depth;\n"
        )
    else:
        body = (
            "    ++dsc_cicd_multi_oracle_depth;\n"
            f"    {return_type} result = {call};\n"
            "    --dsc_cicd_multi_oracle_depth;\n"
            "    return result;\n"
        )
    return (
        '#include "dsc_cicd_overlay.h"\n'
        "extern int dsc_cicd_multi_oracle_depth;\n"
        f"extern {return_type} {implementation}({declarations});\n"
        f"{return_type} {wrapper}({declarations}) {{\n"
        f"{body}"
        "}\n"
    )


def write_multi_overlay_sources(
    agent: Agent,
    source_dir: pathlib.Path,
    candidates: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    generated: list[dict[str, Any]] = []
    header_names: list[str] = []
    main_source: str | None = None
    staging_parent = source_dir.parent / "adapter-staging"
    staging_parent.mkdir(parents=True, exist_ok=True)
    for candidate in candidates:
        slug = candidate["slug"]
        stage = pathlib.Path(tempfile.mkdtemp(prefix=f"{slug}-", dir=str(staging_parent)))
        paths = agent.write_overlay_sources(
            candidate["contract"],
            stage,
            candidate["module"],
            candidate["candidate_path"],
        )
        composition = dict(paths.get("composition", {}) or {})
        frozen_inputs = [
            str(port.get("name"))
            for port in candidate["contract"].get("interface", {}).get("ports", [])
            if port.get("direction") == "input"
        ]
        if (
            composition.get("status") != "PASS"
            or composition.get("rtl_input_count") != len(frozen_inputs)
            or list(composition.get("frozen_input_ports", [])) != frozen_inputs
            or len(composition.get("rtl_bindings", [])) != len(frozen_inputs)
        ):
            raise RuntimeError(
                f"{candidate['function']} adapter does not bind its frozen RTL interface"
            )
        routed_children: list[dict[str, str]] = []
        for path in sorted(stage.iterdir()):
            if path.name == "dsc_cicd_main.c":
                main_source = main_source or path.read_text(encoding="utf-8")
                continue
            if path.suffix not in {".c", ".h", ".cpp"}:
                continue
            destination_name = namespaced_filename(path.name, slug)
            content = namespace_adapter_text(
                path.read_text(encoding="utf-8"),
                slug=slug,
                function_name=candidate["function"],
            )
            if path.suffix == ".c":
                content, routed = route_adapter_child_dispatchers(
                    content,
                    own_function=str(candidate["function"]),
                    candidates=candidates,
                )
                routed_children.extend(routed)
            (source_dir / destination_name).write_text(content, encoding="utf-8")
            if path.name == "dsc_cicd_overlay.h":
                header_names.append(destination_name)
        sv_name = f"dsc_cicd_{slug}_candidate.sv"
        shutil.copy2(candidate["candidate_path"], source_dir / sv_name)
        original_name = f"{candidate['function']}_original_{slug}"
        original_impl_name = (
            f"{candidate['function']}_original_impl_{slug}"
        )
        generated_item = {
            **candidate,
            "candidate_copy": source_dir / sv_name,
            "bridge": source_dir / f"dsc_cicd_{slug}_rtl_bridge.cpp",
            "original_name": original_name,
            "original_impl_name": original_impl_name,
            "dispatcher_name": f"dsc_cicd_{slug}_invoke",
            "composition": {
                **composition,
                "simultaneous_child_dispatchers": routed_children,
                "private_c_oracle_forces_nested_dispatchers_c_only": True,
            },
        }
        wrapper_path = source_dir / f"dsc_cicd_{slug}_oracle_wrapper.c"
        wrapper_path.write_text(
            render_private_oracle_wrapper(generated_item),
            encoding="utf-8",
        )
        generated.append(generated_item)
    if main_source is None:
        raise RuntimeError("generated adapters did not provide the codec main wrapper")
    (source_dir / "dsc_cicd_main.c").write_text(main_source, encoding="utf-8")
    umbrella = source_dir / "dsc_cicd_overlay.h"
    umbrella.write_text(
        "#ifndef DSC_CICD_OVERLAY_H\n#define DSC_CICD_OVERLAY_H\n"
        + "".join(f'#include "{name}"\n' for name in sorted(header_names))
        + "#endif\n",
        encoding="utf-8",
    )
    (source_dir / "dsc_cicd_multi_time.cpp").write_text(
        "double sc_time_stamp() { return 0.0; }\n", encoding="utf-8"
    )
    (source_dir / "dsc_cicd_multi_oracle.c").write_text(
        "int dsc_cicd_multi_oracle_depth = 0;\n", encoding="utf-8"
    )
    shutil.rmtree(staging_parent, ignore_errors=True)
    return generated


def rewrite_multi_overlay(
    agent: Agent,
    source_dir: pathlib.Path,
    generated: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    receipts: list[dict[str, Any]] = []
    umbrella = source_dir / "dsc_cicd_overlay.h"
    for item in generated:
        receipt = agent.run_overlay_rewriter(
            item["contract"],
            source_dir,
            umbrella,
            allow_residual_symbol_alias=bool(
                item["composition"].get("residual_symbol_alias_routes_to_dispatcher")
            ),
            original_name=item["original_impl_name"],
            dispatcher_name=item["dispatcher_name"],
            receipt_name=f"clang-overlay-receipt-{item['slug']}.json",
        )
        receipts.append(receipt)
        if receipt.get("status") != "PASS":
            raise RuntimeError(f"Clang rewrite failed for {item['function']}")
    return receipts


def compile_multi_overlay(
    agent: Agent,
    source_dir: pathlib.Path,
    generated: list[dict[str, Any]],
    jobs: int,
) -> dict[str, Any]:
    verilator = agent.input_facts["tools"].get("verilator") or "verilator"
    clang = agent.input_facts["tools"].get("clang") or "clang"
    clangxx = agent.input_facts["tools"].get("clang++") or "clang++"
    build_dir = source_dir.parent / "multi-overlay-build"
    if build_dir.exists():
        shutil.rmtree(build_dir)
    build_dir.mkdir(parents=True)

    def build_rtl(item: dict[str, Any]) -> dict[str, Any]:
        obj_dir = build_dir / f"rtl-{item['slug']}"
        verilator_result = agent.run_process(
            [
                verilator,
                "--cc",
                str(item["candidate_copy"]),
                "--Mdir",
                str(obj_dir),
                "--top-module",
                item["module"],
                "--Wno-fatal",
            ],
            cwd=source_dir,
            timeout=1800,
        )
        if verilator_result["returncode"] != 0:
            return {"status": "FAIL", "item": item, "verilator": verilator_result}
        make_result = agent.run_process(
            ["make", "-C", str(obj_dir), "-f", f"V{item['module']}.mk", "-j", "1"],
            cwd=source_dir,
            timeout=1800,
        )
        archive = obj_dir / f"V{item['module']}__ALL.a"
        return {
            "status": "PASS" if make_result["returncode"] == 0 and archive.is_file() else "FAIL",
            "item": item,
            "obj_dir": obj_dir,
            "archive": archive,
            "verilator": verilator_result,
            "make": make_result,
        }

    with concurrent.futures.ThreadPoolExecutor(max_workers=max(1, jobs)) as pool:
        rtl_builds = list(pool.map(build_rtl, generated))
    if not all(item["status"] == "PASS" for item in rtl_builds):
        return {"status": "INFRASTRUCTURE_FAILURE", "reason": "one or more Verilator builds failed", "rtl_builds": rtl_builds}

    compile_jobs: list[tuple[list[str], pathlib.Path, str]] = []
    for source in sorted(source_dir.glob("*.c")):
        output = build_dir / f"c-{source.stem}.o"
        extra = ["-Dmain=dsc_cicd_original_main"] if source.name == "codec_main.c" else []
        compile_jobs.append((
            [clang, "-std=gnu99", "-O3", "-I", str(source_dir), *extra, "-c", str(source), "-o", str(output)],
            output,
            source.name,
        ))
    verilator_include = pathlib.Path(verilator).resolve().parent.parent / "share" / "verilator" / "include"
    by_slug = {item["item"]["slug"]: item for item in rtl_builds}
    for item in generated:
        output = build_dir / f"cpp-{item['slug']}.o"
        compile_jobs.append((
            [
                clangxx,
                "-std=c++17",
                "-O2",
                "-I",
                str(by_slug[item["slug"]]["obj_dir"]),
                "-I",
                str(verilator_include),
                "-c",
                str(item["bridge"]),
                "-o",
                str(output),
            ],
            output,
            item["bridge"].name,
        ))
    time_object = build_dir / "cpp-multi-time.o"
    compile_jobs.append((
        [clangxx, "-std=c++17", "-O2", "-c", str(source_dir / "dsc_cicd_multi_time.cpp"), "-o", str(time_object)],
        time_object,
        "dsc_cicd_multi_time.cpp",
    ))

    def compile_source(job: tuple[list[str], pathlib.Path, str]) -> dict[str, Any]:
        command, output, label = job
        result = agent.run_process(command, cwd=source_dir, timeout=1200)
        return {
            "status": "PASS" if result["returncode"] == 0 and output.is_file() else "FAIL",
            "label": label,
            "object": output,
            "command": result,
        }

    with concurrent.futures.ThreadPoolExecutor(max_workers=max(1, jobs)) as pool:
        source_builds = list(pool.map(compile_source, compile_jobs))
    if not all(item["status"] == "PASS" for item in source_builds):
        return {
            "status": "INFRASTRUCTURE_FAILURE",
            "reason": "one or more adapter/model source compilations failed",
            "rtl_builds": rtl_builds,
            "source_builds": source_builds,
        }

    runtime_archives: list[pathlib.Path] = []
    for rtl in rtl_builds:
        for name in ("libverilated.a", "libverilated_threads.a"):
            path = rtl["obj_dir"] / name
            if path.is_file() and name not in {item.name for item in runtime_archives}:
                runtime_archives.append(path)
    if not any(path.name == "libverilated.a" for path in runtime_archives):
        runtime_objects: list[pathlib.Path] = []
        for name in ("verilated.cpp", "verilated_threads.cpp"):
            source = verilator_include / name
            if not source.is_file():
                continue
            output = build_dir / f"runtime-{source.stem}.o"
            result = agent.run_process(
                [
                    clangxx,
                    "-std=c++17",
                    "-O2",
                    "-I",
                    str(verilator_include),
                    "-I",
                    str(verilator_include / "vltstd"),
                    "-c",
                    str(source),
                    "-o",
                    str(output),
                ],
                cwd=source_dir,
                timeout=1200,
            )
            if result["returncode"] != 0 or not output.is_file():
                return {
                    "status": "INFRASTRUCTURE_FAILURE",
                    "reason": f"failed to compile {name}",
                    "runtime_compile": result,
                }
            runtime_objects.append(output)
    else:
        runtime_objects = []

    binary = source_dir / "dsc"
    objects = [item["object"] for item in source_builds]
    archives = [item["archive"] for item in rtl_builds]
    link = agent.run_process(
        [
            clangxx,
            "-O2",
            "-pthread",
            "-o",
            str(binary),
            *[str(path) for path in objects],
            *[str(path) for path in archives],
            *[str(path) for path in runtime_archives],
            *[str(path) for path in runtime_objects],
        ],
        cwd=source_dir,
        timeout=1800,
    )
    return {
        "status": "PASS" if link["returncode"] == 0 and binary.is_file() else "INFRASTRUCTURE_FAILURE",
        "binary": binary,
        "parallel_jobs": max(1, jobs),
        "rtl_builds": rtl_builds,
        "source_builds": source_builds,
        "link": link,
    }


def aggregate_candidate_metrics(scenarios: list[dict[str, Any]]) -> dict[str, Any]:
    totals: dict[str, dict[str, int | bool]] = {}
    for scenario in scenarios:
        candidates = (scenario.get("overlay_metrics", {}) or {}).get("candidates", {}) or {}
        for name, metrics in candidates.items():
            total = totals.setdefault(name, {"calls": 0, "rtl_invocations": 0, "mismatches": 0})
            total["calls"] = int(total["calls"]) + int(metrics.get("calls", 0))
            total["rtl_invocations"] = int(total["rtl_invocations"]) + int(metrics.get("rtl_invocations", 0))
            total["mismatches"] = int(total["mismatches"]) + int(metrics.get("mismatches", 0))
    for total in totals.values():
        total["replacement_reached"] = int(total["calls"]) > 0
        total["rtl_exercised"] = int(total["rtl_invocations"]) > 0
    return totals


def absorbed_rtl_dependencies(
    generated: list[dict[str, Any]],
) -> dict[str, list[dict[str, Any]]]:
    """Find hash-pinned children instantiated or inlined by parent RTL."""

    selected_by_function = {
        str(item.get("function")): item
        for item in generated
        if item.get("function")
    }
    selected_by_contract_id = {
        str((item.get("contract", {}) or {}).get("contract_id")): item
        for item in generated
        if (item.get("contract", {}) or {}).get("contract_id")
    }
    result: dict[str, list[dict[str, Any]]] = {}
    for parent in generated:
        contract = parent.get("contract", {}) or {}
        dependency_rows: list[dict[str, Any]] = []
        for value in (
            contract.get("dependencies"),
            (contract.get("composition", {}) or {}).get("dependencies"),
        ):
            if isinstance(value, list):
                dependency_rows.extend(
                    item for item in value if isinstance(item, dict)
                )
        routed = {
            str(item.get("function"))
            for item in (
                (parent.get("composition", {}) or {}).get(
                    "simultaneous_child_dispatchers", []
                )
                or []
            )
            if isinstance(item, dict) and item.get("function")
        }
        for dependency in dependency_rows:
            function = str(dependency.get("function", ""))
            child = selected_by_function.get(function)
            if child is None or function in routed:
                continue
            expected_contract = str(
                dependency.get("contract_sha256", "")
            )
            expected_candidate = str(
                dependency.get("module_sha256")
                or dependency.get("candidate_sha256")
                or ""
            )
            contract_match = bool(
                expected_contract
                and expected_contract == str(child.get("contract_sha256", ""))
            )
            candidate_match = bool(
                expected_candidate
                and expected_candidate == str(child.get("candidate_sha256", ""))
            )
            if not contract_match or not candidate_match:
                continue
            child_slug = str(child.get("slug", ""))
            if not child_slug:
                continue
            result.setdefault(child_slug, []).append({
                "child_function": function,
                "parent_function": parent.get("function"),
                "parent_slug": parent.get("slug"),
                "dependency_contract_sha256": expected_contract,
                "dependency_candidate_sha256": expected_candidate,
                "contract_hash_match": contract_match,
                "candidate_hash_match": candidate_match,
                "execution_class": "ABSORBED_BY_PARENT_RTL",
            })

        # Early provisional transition contracts froze their direct callees in
        # ``selection`` before the dependency array became mandatory.  Bind
        # those frozen edges to the exact child contract/module selected for
        # this executable.  This is intentionally narrower than inferring from
        # a live call graph: an edge must already be named or contract-id pinned
        # in the immutable parent contract, and both sides' artifact hashes are
        # recorded in the integration receipt.
        selection = contract.get("selection", {}) or {}
        frozen_children: list[tuple[dict[str, Any], str]] = []
        callee_contract_id = str(selection.get("callee_contract_id", ""))
        if callee_contract_id:
            child = selected_by_contract_id.get(callee_contract_id)
            if child is not None:
                frozen_children.append((child, "callee_contract_id"))
        for function in selection.get("callee_names", []) or []:
            child = selected_by_function.get(str(function))
            if child is not None:
                frozen_children.append((child, "callee_names"))
        for child, evidence_key in frozen_children:
            function = str(child.get("function", ""))
            child_slug = str(child.get("slug", ""))
            if (
                not function
                or not child_slug
                or function in routed
                or child_slug == str(parent.get("slug", ""))
            ):
                continue
            existing = result.get(child_slug, [])
            if any(
                str(item.get("parent_slug")) == str(parent.get("slug"))
                for item in existing
            ):
                continue
            child_contract_hash = str(child.get("contract_sha256", ""))
            child_candidate_hash = str(child.get("candidate_sha256", ""))
            parent_contract_hash = str(parent.get("contract_sha256", ""))
            parent_candidate_hash = str(parent.get("candidate_sha256", ""))
            if not all(
                (
                    child_contract_hash,
                    child_candidate_hash,
                    parent_contract_hash,
                    parent_candidate_hash,
                )
            ):
                continue
            result.setdefault(child_slug, []).append({
                "child_function": function,
                "parent_function": parent.get("function"),
                "parent_slug": parent.get("slug"),
                "dependency_contract_sha256": child_contract_hash,
                "dependency_candidate_sha256": child_candidate_hash,
                "parent_contract_sha256": parent_contract_hash,
                "parent_candidate_sha256": parent_candidate_hash,
                "contract_hash_match": True,
                "candidate_hash_match": True,
                "pin_origin": "INTEGRATION_HASH_BINDING_OVER_FROZEN_CALLEE_EVIDENCE",
                "frozen_evidence_key": evidence_key,
                "execution_class": "ABSORBED_BY_PARENT_RTL",
            })
    return result


def active_absorbed_rtl_dependencies(
    candidate_totals: dict[str, dict[str, Any]],
    absorbed_dependencies: dict[str, list[dict[str, Any]]],
) -> dict[str, list[dict[str, Any]]]:
    """Propagate hash-pinned RTL absorption through composed parent RTL.

    A child can be several composition levels below the directly invoked RTL
    dispatcher (for example VLDGroup -> VLDUnit -> EscapeCodeSize).  Requiring
    the immediate parent to have a direct invocation incorrectly classifies
    those transitive children as C fallbacks.  Only dependency edges already
    accepted by ``absorbed_rtl_dependencies`` participate in this closure, so
    every propagated edge remains contract- and module-hash pinned.
    """

    active = {
        slug
        for slug, metrics in candidate_totals.items()
        if int(metrics.get("rtl_invocations", 0)) > 0
    }
    active_rows: dict[str, list[dict[str, Any]]] = {}
    changed = True
    while changed:
        changed = False
        for child_slug, rows in absorbed_dependencies.items():
            eligible: list[dict[str, Any]] = []
            for row in rows:
                parent_slug = str(row.get("parent_slug", ""))
                if parent_slug not in active:
                    continue
                annotated = dict(row)
                annotated["parent_execution_class"] = (
                    "DIRECT_RTL"
                    if int(
                        candidate_totals.get(parent_slug, {}).get(
                            "rtl_invocations", 0
                        )
                    )
                    > 0
                    else "ABSORBED_BY_PARENT_RTL"
                )
                eligible.append(annotated)
            if not eligible:
                continue
            active_rows[child_slug] = eligible
            if child_slug not in active:
                active.add(child_slug)
                changed = True
    return active_rows


def run_decode_integration(
    root: pathlib.Path,
    artifact: pathlib.Path,
    scope: str,
    jobs: int,
) -> dict[str, Any]:
    started = time.time()
    agent = Agent(root, "decode-multi-rtl-integration")
    agent.load_inputs()
    previous_scope = os.environ.get("DSC_CICD_MATRIX_SCOPE")
    os.environ["DSC_CICD_MATRIX_SCOPE"] = scope
    base_model: pathlib.Path | None = None
    overlay_model: pathlib.Path | None = None
    try:
        candidates = source_order_candidates(
            discover_decode_candidates(root),
            read_json(root / "facts" / "functions.json", {}) or {},
        )
        scenarios = agent.discover_matrix()
        if not scenarios or not all(item.get("parse_status") == "PASS" for item in scenarios):
            raise RuntimeError("Decode matrix contains no usable profile or an unparseable profile")
        artifact.mkdir(parents=True, exist_ok=True)
        selection = [{
            key: (str(value.relative_to(root)) if isinstance(value, pathlib.Path) and value.is_relative_to(root) else str(value) if isinstance(value, pathlib.Path) else value)
            for key, value in item.items()
            if key not in {"contract"}
        } for item in candidates]
        write_json(artifact / "selected-candidates.json", {
            "schema_version": 1,
            "policy": (
                "hash-checked stable manifest RTL reached by Decode plus provisional "
                "matrix PASS RTL with Decode SHADOW and RTL_RETURN runtime exercise"
            ),
            "count": len(selection),
            "candidates": selection,
        })

        base_model = agent.copy_model("decode-integration-baseline")
        baseline_results: list[dict[str, Any]] = []
        for scenario in scenarios:
            command = agent.run_process([str(base_model / scenario["script"])], cwd=base_model, timeout=1800)
            bitstream = base_model / scenario["golden"]
            actual = file_hash(bitstream) if bitstream.is_file() else None
            expected = scenario.get("expected_sha256")
            passed = command["returncode"] == 0 and actual is not None and (not expected or actual == expected)
            baseline_results.append({
                "scenario": scenario,
                "status": "PASS" if passed else "FAIL",
                "command": command,
                "sha256": actual,
                "size_bytes": bitstream.stat().st_size if bitstream.is_file() else None,
                "expected_sha256": expected,
                "expected_sha256_match": actual == expected if expected else None,
            })
        if not all(item["status"] == "PASS" for item in baseline_results):
            raise RuntimeError("original C baseline bitstream generation failed")

        oracle_root = base_model.parent / "decode-original-c"
        oracle_frames: list[dict[str, Any]] = []
        for baseline in baseline_results:
            scenario = baseline["scenario"]
            decoded = agent.run_decode_frame(
                base_model,
                base_model / "source" / "dsc",
                scenario,
                base_model / scenario["golden"],
                oracle_root / safe_identifier(str(scenario["name"])),
            )
            decoded["scenario"] = scenario
            oracle_frames.append(decoded)
        if not all(item.get("status") == "PASS" for item in oracle_frames):
            raise RuntimeError("original C full-frame Decode oracle failed")

        overlay_temp = pathlib.Path(tempfile.mkdtemp(prefix="dsc-multi-overlay-", dir=str(root / "tmp")))
        overlay_model = overlay_temp / base_model.name
        shutil.copytree(base_model, overlay_model, ignore=shutil.ignore_patterns(".git", "__pycache__", "target", "build", "dsc-rs", "operator_bittrue"))
        source_dir = overlay_model / "source"
        generated = write_multi_overlay_sources(agent, source_dir, candidates)
        absorbed_dependencies = absorbed_rtl_dependencies(generated)
        rewrite_receipts = rewrite_multi_overlay(agent, source_dir, generated)
        compile_receipt = compile_multi_overlay(agent, source_dir, generated, jobs)
        if compile_receipt.get("status") != "PASS":
            raise RuntimeError("multi-RTL Decode executable failed to compile")

        oracle_by_script = {str(item["scenario"]["script"]): item for item in oracle_frames}
        mode_results: dict[str, Any] = {}
        output_root = overlay_model.parent / "decode-multi-rtl"
        expected_slugs = {item["slug"] for item in generated}
        for mode in ("C_ONLY", "SHADOW", "RTL_RETURN"):
            scenario_results: list[dict[str, Any]] = []
            for baseline in baseline_results:
                scenario = baseline["scenario"]
                oracle = oracle_by_script[str(scenario["script"])]
                decoded = agent.run_decode_frame(
                    overlay_model,
                    pathlib.Path(compile_receipt["binary"]),
                    scenario,
                    base_model / scenario["golden"],
                    output_root / mode.lower() / safe_identifier(str(scenario["name"])),
                    mode=mode,
                )
                output_file = pathlib.Path(str(decoded.get("output_file", "")))
                oracle_file = pathlib.Path(str(oracle.get("output_file", "")))
                byte_equal = agent.files_byte_equal(output_file, oracle_file)
                mismatches = int((decoded.get("overlay_metrics", {}) or {}).get("mismatches", 0))
                passed = decoded.get("status") == "PASS" and byte_equal and mismatches == 0
                decoded.update({
                    "scenario": scenario,
                    "status": "PASS" if passed else "FAIL",
                    "oracle_sha256": oracle.get("sha256"),
                    "oracle_size_bytes": oracle.get("size_bytes"),
                    "byte_for_byte_match": byte_equal,
                    "mismatch_count": mismatches,
                })
                scenario_results.append(decoded)
            candidate_totals = aggregate_candidate_metrics(scenario_results)
            active_absorbed = active_absorbed_rtl_dependencies(
                candidate_totals, absorbed_dependencies
            )
            for slug in expected_slugs:
                total = candidate_totals.setdefault(
                    slug,
                    {
                        "calls": 0,
                        "rtl_invocations": 0,
                        "mismatches": 0,
                        "replacement_reached": False,
                        "rtl_exercised": False,
                    },
                )
                active_parents = active_absorbed.get(slug, [])
                total["absorbed_by_parent_rtl"] = active_parents
                total["execution_class"] = (
                    "DIRECT_RTL"
                    if int(total.get("rtl_invocations", 0)) > 0
                    else "ABSORBED_BY_PARENT_RTL"
                    if active_parents
                    else "C_ONLY"
                    if mode == "C_ONLY"
                    else "NOT_RTL_EXERCISED"
                )

            def reached(slug: str) -> bool:
                total = candidate_totals.get(slug, {})
                return bool(
                    int(total.get("calls", 0)) > 0
                    or total.get("absorbed_by_parent_rtl")
                )

            def rtl_exercised(slug: str) -> bool:
                total = candidate_totals.get(slug, {})
                return bool(
                    int(total.get("rtl_invocations", 0)) > 0
                    or total.get("absorbed_by_parent_rtl")
                ) and int(total.get("mismatches", 0)) == 0

            all_candidates_reached = all(
                reached(slug) for slug in expected_slugs
            )
            if mode in {"SHADOW", "RTL_RETURN"}:
                all_candidates_exercised = all(
                    rtl_exercised(slug) for slug in expected_slugs
                )
            else:
                all_candidates_exercised = all(
                    reached(slug)
                    and int(candidate_totals.get(slug, {}).get("rtl_invocations", 0)) == 0
                    for slug in expected_slugs
                )
            mode_pass = all(item["status"] == "PASS" for item in scenario_results) and all_candidates_reached and all_candidates_exercised
            mode_results[mode] = {
                "status": "PASS" if mode_pass else "FAIL",
                "profiles": len(scenario_results),
                "all_candidates_reached": all_candidates_reached,
                "all_candidates_exercised_as_expected": all_candidates_exercised,
                "total_calls": sum(int(item.get("calls", 0)) for item in candidate_totals.values()),
                "total_rtl_invocations": sum(int(item.get("rtl_invocations", 0)) for item in candidate_totals.values()),
                "candidate_metrics": candidate_totals,
                "scenarios": scenario_results,
            }

        status = "PASS" if all(item["status"] == "PASS" for item in mode_results.values()) else "FAIL"
        roots = [root, base_model, base_model.parent, overlay_model, overlay_model.parent]
        result = {
            "schema_version": 1,
            "status": status,
            "matrix_scope": scope,
            "profiles": len(scenarios),
            "phase_order": ["DECODE"],
            "oracle": "IMMUTABLE_ORIGINAL_C_SOURCE",
            "replacement": "ALL_DISCOVERED_DECODE_VERILOG_VIA_VERILATOR_CXX_IN_ONE_EXECUTABLE",
            "comparison": "FULL_DECODED_FRAME_BYTE_FOR_BYTE_AND_SHA256",
            "candidate_count": len(candidates),
            "candidate_order": [item["function"] for item in candidates],
            "absorbed_rtl_dependencies": absorbed_dependencies,
            "source_hash": agent.input_facts.get("source_hash"),
            "baseline": baseline_results,
            "oracle_frames": oracle_frames,
            "rewrites": rewrite_receipts,
            "compile": compile_receipt,
            "modes": mode_results,
            "promotion_status": "BLOCKED_PENDING_HUMAN_CONTRACT_REVIEW",
            "duration_seconds": round(time.time() - started, 3),
        }
        result = scrub_paths(result, roots)
        write_json(artifact / "matrix-receipt.json", result)
        write_json(artifact / "compile-receipt.json", result["compile"])
        write_json(artifact / "rewrite-receipts.json", result["rewrites"])
        write_json(artifact / "verification-receipt.json", {
            "schema_version": 1,
            "status": status,
            "candidate_count": len(candidates),
            "matrix_scope": scope,
            "profiles": len(scenarios),
            "c_only": mode_results["C_ONLY"]["status"],
            "shadow": mode_results["SHADOW"]["status"],
            "rtl_return": mode_results["RTL_RETURN"]["status"],
            "rtl_return_invocations": mode_results["RTL_RETURN"]["total_rtl_invocations"],
            "promotion_status": "BLOCKED_PENDING_HUMAN_CONTRACT_REVIEW",
            "matrix_receipt": "matrix-receipt.json",
        })
        return result
    except Exception as error:
        failure = {
            "schema_version": 1,
            "status": "INFRASTRUCTURE_FAILURE",
            "matrix_scope": scope,
            "reason": str(error),
            "duration_seconds": round(time.time() - started, 3),
        }
        artifact.mkdir(parents=True, exist_ok=True)
        write_json(artifact / "matrix-receipt.json", failure)
        return failure
    finally:
        if base_model is not None:
            shutil.rmtree(base_model.parent, ignore_errors=True)
        if overlay_model is not None:
            shutil.rmtree(overlay_model.parent, ignore_errors=True)
        if previous_scope is None:
            os.environ.pop("DSC_CICD_MATRIX_SCOPE", None)
        else:
            os.environ["DSC_CICD_MATRIX_SCOPE"] = previous_scope


def main() -> int:
    args = parse_args()
    root = args.root.resolve()
    artifact = args.artifact.resolve()
    result = run_decode_integration(root, artifact, args.scope, max(1, args.jobs))
    print(json.dumps({
        "status": result.get("status"),
        "matrix_scope": result.get("matrix_scope"),
        "profiles": result.get("profiles"),
        "candidate_count": result.get("candidate_count"),
        "reason": result.get("reason"),
        "duration_seconds": result.get("duration_seconds"),
    }, sort_keys=True))
    return 0 if result.get("status") == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
