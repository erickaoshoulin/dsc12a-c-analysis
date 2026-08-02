#!/usr/bin/env python3
"""Prove a reviewed windowed RTL candidate against its C/spec semantics.

The executable CI runner already provides concrete C-vs-Verilator differential
coverage.  This companion gate handles the value domain that is too large for
Cartesian enumeration: Verilator emits its parsed AST as JSON, the restricted
combinational AST is interpreted into Z3 expressions, and the locked
contract's exact window equations are used as the independent oracle model.

This is deliberately a semantic-kind adapter, not a function-name selector.
The candidate is admitted only when the locked contract is already selected by
the normal facts/coverage pipeline and declares the reviewed
``windowed_sample_predict`` semantics.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import re
import subprocess
import tempfile
from pathlib import Path
from typing import Any

try:
    import z3
except ImportError as error:  # pragma: no cover - exercised by infrastructure
    raise SystemExit("formal_rtl.py requires the z3-solver Python package") from error


class FormalError(RuntimeError):
    """Raised when a candidate cannot be translated into the proof subset."""


def file_digest(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def as_list(value: Any) -> list[Any]:
    if value is None:
        return []
    return value if isinstance(value, list) else [value]


def first(value: Any) -> dict[str, Any]:
    values = as_list(value)
    if not values or not isinstance(values[0], dict):
        raise FormalError("AST node is missing its first child")
    return values[0]


def sum_expr(values: list[Any]) -> Any:
    return z3.Sum(values) if values else z3.IntVal(0)


def pow2_expr(value: Any, low: int = 0, high: int = 32) -> Any:
    """Encode a bounded variable shift without nonlinear exponentiation."""

    return sum_expr([
        z3.If(value == exponent, 1 << exponent, 0)
        for exponent in range(low, high + 1)
    ])


def const_value(name: str) -> int:
    """Decode the scalar literal spellings used by Verilator's JSON AST."""

    text = str(name).replace("_", "")
    match = re.fullmatch(r"(?:(\d+)'([sS]?)([hHbBoOdD])([0-9a-fA-F]+)|(-?\d+))", text)
    if not match:
        raise FormalError(f"unsupported AST constant: {name}")
    if match.group(5) is not None:
        return int(match.group(5), 10)
    width = int(match.group(1))
    signed = bool(match.group(2))
    base_letter = match.group(3).lower()
    base = {"h": 16, "b": 2, "o": 8, "d": 10}[base_letter]
    value = int(match.group(4), base)
    if signed and value >= (1 << (width - 1)):
        value -= 1 << width
    return value


def clamp(value: Any, lower: Any, upper: Any) -> Any:
    return z3.If(value < lower, lower, z3.If(value > upper, upper, value))


def minimum(left: Any, right: Any) -> Any:
    return z3.If(left < right, left, right)


def maximum(left: Any, right: Any) -> Any:
    return z3.If(left > right, left, right)


class AstInterpreter:
    """Small symbolic interpreter for the combinational Verilator JSON subset."""

    def __init__(self, module: dict[str, Any]) -> None:
        self.module = module
        self.functions = {
            str(node.get("name")): node
            for node in as_list(module.get("stmtsp"))
            if isinstance(node, dict) and node.get("type") == "FUNC"
        }

    def expr(self, node: dict[str, Any], env: dict[str, Any]) -> Any:
        kind = str(node.get("type", ""))
        if kind == "VARREF":
            name = str(node.get("name"))
            if name not in env:
                raise FormalError(f"AST references unknown variable {name}")
            return env[name]
        if kind == "CONST":
            return z3.IntVal(const_value(str(node.get("name"))))
        if kind in {"EXTEND", "EXTENDS", "SIGNED", "UNSIGNED", "CONSTRAINT"}:
            return self.expr(first(node.get("lhsp")), env)
        if kind == "CRESET":
            return z3.IntVal(0)
        if kind == "NEGATE":
            return -self.expr(first(node.get("lhsp")), env)
        if kind in {"NOT", "LOGNOT"}:
            return z3.Not(self.expr(first(node.get("lhsp")), env))
        if kind in {"ADD", "ADDW", "ADDWRAP"}:
            return self.expr(first(node.get("lhsp")), env) + self.expr(first(node.get("rhsp")), env)
        if kind in {"SUB", "SUBW", "SUBWRAP"}:
            return self.expr(first(node.get("lhsp")), env) - self.expr(first(node.get("rhsp")), env)
        if kind in {"MUL", "MULS", "MULW"}:
            return self.expr(first(node.get("lhsp")), env) * self.expr(first(node.get("rhsp")), env)
        if kind in {"DIV", "DIVS"}:
            return self.expr(first(node.get("lhsp")), env) / self.expr(first(node.get("rhsp")), env)
        if kind in {"MODDIV", "MODDIVS"}:
            return self.expr(first(node.get("lhsp")), env) % self.expr(first(node.get("rhsp")), env)
        if kind in {"SHIFTL", "SHIFTLW"}:
            left = self.expr(first(node.get("lhsp")), env)
            shift = self.expr(first(node.get("rhsp")), env)
            return left * pow2_expr(shift, 0, 32)
        if kind in {"SHIFTR", "SHIFTRS", "SHIFTRW"}:
            left = self.expr(first(node.get("lhsp")), env)
            shift = self.expr(first(node.get("rhsp")), env)
            # All right shifts in the reviewed window equations are on
            # non-negative filter sums.  Z3 integer division also matches
            # arithmetic right shift for the signed values used here.
            return left / pow2_expr(shift, 0, 32)
        if kind in {"EQ", "CASEEQ", "EQW"}:
            return self.expr(first(node.get("lhsp")), env) == self.expr(first(node.get("rhsp")), env)
        if kind in {"NEQ", "CASENEQ", "NEQW"}:
            return self.expr(first(node.get("lhsp")), env) != self.expr(first(node.get("rhsp")), env)
        if kind in {"LTS", "LT"}:
            return self.expr(first(node.get("lhsp")), env) < self.expr(first(node.get("rhsp")), env)
        if kind in {"LTES", "LTE"}:
            return self.expr(first(node.get("lhsp")), env) <= self.expr(first(node.get("rhsp")), env)
        if kind in {"GTS", "GT"}:
            return self.expr(first(node.get("lhsp")), env) > self.expr(first(node.get("rhsp")), env)
        if kind in {"GTES", "GTE"}:
            return self.expr(first(node.get("lhsp")), env) >= self.expr(first(node.get("rhsp")), env)
        if kind in {"AND", "BITAND"}:
            left = self.expr(first(node.get("lhsp")), env)
            right = self.expr(first(node.get("rhsp")), env)
            if z3.is_bool(left) or z3.is_bool(right):
                return z3.And(left, right)
            return left & right
        if kind in {"OR", "BITOR"}:
            left = self.expr(first(node.get("lhsp")), env)
            right = self.expr(first(node.get("rhsp")), env)
            if z3.is_bool(left) or z3.is_bool(right):
                return z3.Or(left, right)
            return left | right
        if kind in {"XOR", "BITXOR"}:
            return self.expr(first(node.get("lhsp")), env) ^ self.expr(first(node.get("rhsp")), env)
        if kind == "COND":
            condition = self.expr(first(node.get("condp")), env)
            then_value = self.expr(first(node.get("thenp")), env)
            else_value = self.expr(first(node.get("elsep")), env)
            return z3.If(condition, then_value, else_value)
        if kind == "SEL":
            value = self.expr(first(node.get("fromp")), env)
            lsb = self.expr(first(node.get("lsbp")), env)
            width = int(node.get("widthConst", 1))
            return (value / pow2_expr(lsb, 0, 32)) % (1 << width)
        if kind == "FUNCREF":
            name = str(node.get("name"))
            args = [self.expr(first(argument.get("exprp")), env) for argument in as_list(node.get("argsp"))]
            return self.call(name, args, env)
        raise FormalError(f"unsupported AST expression node: {kind}")

    def call(self, name: str, args: list[Any], parent_env: dict[str, Any]) -> Any:
        function = self.functions.get(name)
        if function is None:
            raise FormalError(f"AST calls unknown function {name}")
        # Verilator keeps the function return variable in ``fvarp`` but
        # emits function input declarations in the function's statement list.
        parameters = [
            node for node in as_list(function.get("stmtsp"))
            if isinstance(node, dict) and node.get("type") == "VAR"
            and node.get("direction") == "INPUT"
        ]
        if len(parameters) != len(args):
            raise FormalError(f"function {name} argument count mismatch")
        output = next((str(node.get("name")) for node in as_list(function.get("fvarp"))
                       if isinstance(node, dict) and node.get("isFuncReturn")), name)
        # Verilog functions declared inside a module may read module-scope
        # input ports in addition to their explicit arguments.  Preserve the
        # caller environment so a parsed selector/helper function is evaluated
        # with the same frozen DUT inputs as the enclosing always block.
        local = dict(parent_env)
        local.update({
            str(parameter.get("name")): value
            for parameter, value in zip(parameters, args)
        })
        local[output] = z3.IntVal(0)
        self.exec_nodes(as_list(function.get("stmtsp")), local)
        return local[output]

    def assign(self, node: dict[str, Any], env: dict[str, Any]) -> None:
        target = first(node.get("lhsp"))
        if target.get("type") != "VARREF":
            raise FormalError(f"unsupported procedural assignment target: {target.get('type')}")
        env[str(target.get("name"))] = self.expr(first(node.get("rhsp")), env)

    def merge(self, base: dict[str, Any], branches: list[tuple[Any, dict[str, Any]]]) -> dict[str, Any]:
        names = set(base)
        for _, branch in branches:
            names.update(branch)
        merged: dict[str, Any] = {}
        for name in names:
            value = base.get(name, z3.IntVal(0))
            for guard, branch in reversed(branches):
                value = z3.If(guard, branch.get(name, value), value)
            merged[name] = value
        return merged

    def execute_if(self, node: dict[str, Any], env: dict[str, Any]) -> dict[str, Any]:
        condition = self.expr(first(node.get("condp")), env)
        then_env = dict(env)
        self.exec_nodes(as_list(node.get("thensp")), then_env)
        else_env = dict(env)
        self.exec_nodes(as_list(node.get("elsesp")), else_env)
        return self.merge(env, [(condition, then_env), (z3.Not(condition), else_env)])

    def execute_case(self, node: dict[str, Any], env: dict[str, Any]) -> dict[str, Any]:
        selector = self.expr(first(node.get("exprp")), env)
        branches: list[tuple[Any, dict[str, Any]]] = []
        prior: Any = z3.BoolVal(False)
        default: dict[str, Any] | None = None
        for item in as_list(node.get("itemsp")):
            if not isinstance(item, dict):
                continue
            conditions = as_list(item.get("condsp"))
            branch = dict(env)
            self.exec_nodes(as_list(item.get("stmtsp")), branch)
            if conditions:
                matches = [selector == self.expr(condition, env) for condition in conditions]
                guard = z3.And(z3.Or(matches), z3.Not(prior))
                branches.append((guard, branch))
                prior = z3.Or(prior, z3.Or(matches))
            else:
                default = branch
        if default is None:
            default = dict(env)
        branches.append((z3.Not(prior), default))
        return self.merge(env, branches)

    def execute(self, node: dict[str, Any], env: dict[str, Any]) -> None:
        self.exec_node(node, env)

    def exec_nodes(self, nodes: list[Any], env: dict[str, Any]) -> None:
        for node in nodes:
            if isinstance(node, dict):
                self.exec_node(node, env)

    def exec_node(self, node: dict[str, Any], env: dict[str, Any]) -> None:
        kind = str(node.get("type", ""))
        if kind in {"VAR", "CRESET"}:
            return
        if kind == "ASSIGN":
            self.assign(node, env)
            return
        if kind == "BEGIN":
            self.exec_nodes(as_list(node.get("stmtsp")), env)
            return
        if kind == "IF":
            env.update(self.execute_if(node, env))
            return
        if kind == "CASE":
            env.update(self.execute_case(node, env))
            return
        if kind == "ALWAYS":
            self.exec_nodes(as_list(node.get("stmtsp")), env)
            return
        raise FormalError(f"unsupported AST statement node: {kind}")

    def output_expression(self, inputs: dict[str, Any], output_name: str) -> Any:
        env = dict(inputs)
        always = [node for node in as_list(self.module.get("stmtsp"))
                  if isinstance(node, dict) and node.get("type") == "ALWAYS"]
        if len(always) != 1:
            raise FormalError(f"expected one always block, found {len(always)}")
        self.execute(always[0], env)
        if output_name not in env:
            raise FormalError(f"candidate never assigns output {output_name}")
        return env[output_name]


def domain_values(domain: dict[str, Any]) -> list[int] | None:
    values = domain.get("values")
    if isinstance(values, list):
        return [int(value) for value in values]
    bounds = domain.get("range")
    if isinstance(bounds, list) and len(bounds) == 2:
        return list(range(int(bounds[0]), int(bounds[1]) + 1))
    return None


def add_domain_constraints(solver: Any, contract: dict[str, Any], variables: dict[str, Any]) -> None:
    ports = [port for port in contract.get("interface", {}).get("ports", []) if isinstance(port, dict)]
    for port in ports:
        if port.get("direction") != "input":
            continue
        name = str(port.get("name"))
        domain = port.get("legal_domain") or {}
        values = domain_values(domain)
        if values is None:
            raise FormalError(f"input {name} has no finite legal domain")
        if len(values) <= 64:
            solver.add(z3.Or([variables[name] == value for value in values]))
        else:
            solver.add(variables[name] >= values[0], variables[name] <= values[-1])

    semantics = contract.get("semantics", {}) or {}
    strategy = semantics.get("legal_vector_strategy") or {}
    if strategy.get("kind") != "windowed_boundary":
        raise FormalError("formal window proof requires a reviewed windowed_boundary strategy")
    bit_name = str(strategy.get("bit_depth_port"))
    cpnt_name = str(strategy.get("component_type_port"))
    q_name = str(strategy.get("qlevel_port"))
    bit_values = strategy.get("bit_depth_values_by_component") or {}
    luma_values = [int(value) for value in bit_values.get("luma", [])]
    chroma_values = [int(value) for value in bit_values.get("chroma", [])]
    if not luma_values or not chroma_values:
        raise FormalError("window proof lacks component-specific bit-depth domains")
    solver.add(z3.Implies(variables[cpnt_name] % 3 == 0,
                           z3.Or([variables[bit_name] == value for value in luma_values])))
    solver.add(z3.Implies(variables[cpnt_name] % 3 != 0,
                           z3.Or([variables[bit_name] == value for value in chroma_values])))

    qmax = strategy.get("qlevel_max_by_component") or {}
    luma_map = {int(key): int(value) for key, value in (qmax.get("luma") or {}).items()}
    chroma_map = {int(key): int(value) for key, value in (qmax.get("chroma") or {}).items()}
    luma_expr = sum_expr([z3.If(variables[bit_name] == key, value, 0) for key, value in luma_map.items()])
    chroma_expr = sum_expr([z3.If(variables[bit_name] == key, value, 0) for key, value in chroma_map.items()])
    solver.add(variables[q_name] <= z3.If(variables[cpnt_name] % 3 == 0, luma_expr, chroma_expr))

    window = semantics.get("window_spec") or {}
    sample_ports = [str(value) for value in strategy.get("sample_ports", [])]
    residual_ports = [str(value) for value in strategy.get("residual_ports", [])]
    sample_max = pow2_expr(variables[bit_name], 8, 16) - 1
    for name in sample_ports:
        if name not in variables:
            raise FormalError(f"window proof references missing sample port {name}")
        solver.add(variables[name] >= 0, variables[name] <= sample_max)
    width = variables[bit_name] - variables[q_name]
    decoded_width = pow2_expr(width, 0, 16)
    for name in residual_ports:
        if name not in variables:
            raise FormalError(f"window proof references missing residual port {name}")
        solver.add(z3.If(width <= 0,
                         variables[name] == 0,
                         z3.And(variables[name] >= -(decoded_width / 2),
                                variables[name] <= (decoded_width / 2) - 1)))


def contract_expression(contract: dict[str, Any], variables: dict[str, Any]) -> Any:
    semantics = contract.get("semantics", {}) or {}
    strategy = semantics.get("legal_vector_strategy") or {}
    window = semantics.get("window_spec") or {}
    samples_per_unit = int(window.get("samples_per_unit", 3))
    padding_left = int(window.get("padding_left", 5))
    offsets = [int(value) for value in window.get("group_h_offsets", [])]
    if not offsets:
        raise FormalError("window proof lacks group_h_offsets")
    h = variables[str(strategy.get("hpos_port"))]
    pred = variables[str(strategy.get("pred_type_port"))]
    q = variables[str(strategy.get("qlevel_port"))]
    bpc = variables[str(strategy.get("bit_depth_port"))]
    dynamic = window.get("dynamic_line_window")
    if isinstance(dynamic, dict) and dynamic:
        prev_names = [str(value) for value in dynamic.get("prev_window_ports", [])]
        curr_names = [str(value) for value in dynamic.get("curr_window_ports", [])]
        if len(prev_names) != 6 or len(curr_names) != 13:
            raise FormalError("dynamic window proof requires six previous and thirteen current taps")
        if any(name not in variables for name in prev_names + curr_names):
            raise FormalError("dynamic window proof references a missing frozen tap")
        samples_per_unit = int(dynamic.get("samples_per_unit", 3))
        padding_left = int(dynamic.get("padding_left", 5))
        current_window_left = int(dynamic.get("current_window_left", 8))
        window_start = z3.If(
            h > current_window_left,
            h - current_window_left,
            z3.IntVal(0),
        )
        group_a_global = (h / samples_per_unit) * samples_per_unit + padding_left - 1
        group_a_index = group_a_global - window_start

        def current_at(index: Any) -> Any:
            return sum_expr([
                z3.If(index == slot, variables[name], z3.IntVal(0))
                for slot, name in enumerate(curr_names)
            ])

        a = current_at(group_a_index)
        b = variables[prev_names[2]]
        c = variables[prev_names[1]]
        d = variables[prev_names[3]]
        e = variables[prev_names[4]]
        filt_c = (
            variables[prev_names[0]]
            + 2 * variables[prev_names[1]]
            + variables[prev_names[2]]
            + 2
        ) / 4
        filt_b = (
            variables[prev_names[1]]
            + 2 * variables[prev_names[2]]
            + variables[prev_names[3]]
            + 2
        ) / 4
        filt_d = (
            variables[prev_names[2]]
            + 2 * variables[prev_names[3]]
            + variables[prev_names[4]]
            + 2
        ) / 4
        filt_e = (
            variables[prev_names[3]]
            + 2 * variables[prev_names[4]]
            + variables[prev_names[5]]
            + 2
        ) / 4
        qdiv = pow2_expr(q, 0, 16)
        qhalf = qdiv / 2
        blend_c = c + clamp(filt_c - c, -qhalf, qhalf)
        blend_b = b + clamp(filt_b - b, -qhalf, qhalf)
        blend_d = d + clamp(filt_d - d, -qhalf, qhalf)
        blend_e = e + clamp(filt_e - e, -qhalf, qhalf)
        blend_c = z3.If((h / samples_per_unit) == 0, a, blend_c)
        qr0 = variables[str(strategy.get("residual_ports")[0])]
        qr1 = variables[str(strategy.get("residual_ports")[1])]
        mmap = z3.If(
            h % samples_per_unit == 0,
            clamp(a + blend_b - blend_c, minimum(a, blend_b), maximum(a, blend_b)),
            z3.If(
                h % samples_per_unit == 1,
                clamp(
                    a + blend_d - blend_c + qr0 * qdiv,
                    minimum(a, minimum(blend_b, blend_d)),
                    maximum(a, maximum(blend_b, blend_d)),
                ),
                clamp(
                    a + blend_e - blend_c + (qr0 + qr1) * qdiv,
                    minimum(a, minimum(blend_b, minimum(blend_d, blend_e))),
                    maximum(a, maximum(blend_b, maximum(blend_d, blend_e))),
                ),
            ),
        )
        left = z3.If(
            h % samples_per_unit == 0,
            a,
            z3.If(
                h % samples_per_unit == 1,
                clamp(a + qr0 * qdiv, 0, pow2_expr(bpc, 8, 16) - 1),
                clamp(a + (qr0 + qr1) * qdiv, 0, pow2_expr(bpc, 8, 16) - 1),
            ),
        )
        block_global = h + padding_left - 1 - (pred - 2)
        block_global = z3.If(block_global < 0, 0, block_global)
        block = current_at(block_global - window_start)
        return z3.If(pred == 0, mmap, z3.If(pred == 1, left, block))

    sample_ports = {int(name.split("_", 1)[1]): variables[name]
                    for name in strategy.get("sample_ports", []) if str(name).startswith("curr_")}
    prev_ports = {int(name.split("_", 1)[1]): variables[name]
                  for name in strategy.get("sample_ports", []) if str(name).startswith("prev_")}
    required_curr = set(int(value) for value in window.get("curr_tap_indices", []))
    required_prev = set(int(value) for value in window.get("prev_tap_indices", []))
    if not required_curr.issubset(sample_ports) or not required_prev.issubset(prev_ports):
        raise FormalError("window proof tap metadata and strategy ports disagree")
    offset = (h / samples_per_unit) * samples_per_unit + padding_left

    def select(mapping: dict[int, Any], index_fn: Any) -> Any:
        return sum_expr([z3.If(offset == value, mapping[index_fn(value)], 0) for value in offsets])

    a = select(sample_ports, lambda value: value - 1)
    b = select(prev_ports, lambda value: value)
    c = select(prev_ports, lambda value: value - 1)
    d = select(prev_ports, lambda value: value + 1)
    e = select(prev_ports, lambda value: value + 2)
    # Spell the filter taps explicitly to keep the spec mapping auditable.
    filt_c = sum_expr([z3.If(offset == value,
                             (prev_ports[value - 2] + 2 * prev_ports[value - 1] + prev_ports[value] + 2) / 4,
                             0) for value in offsets])
    filt_b = sum_expr([z3.If(offset == value,
                             (prev_ports[value - 1] + 2 * prev_ports[value] + prev_ports[value + 1] + 2) / 4,
                             0) for value in offsets])
    filt_d = sum_expr([z3.If(offset == value,
                             (prev_ports[value] + 2 * prev_ports[value + 1] + prev_ports[value + 2] + 2) / 4,
                             0) for value in offsets])
    filt_e = sum_expr([z3.If(offset == value,
                             (prev_ports[value + 1] + 2 * prev_ports[value + 2] + prev_ports[value + 3] + 2) / 4,
                             0) for value in offsets])
    qdiv = pow2_expr(q, 0, 16)
    qhalf = qdiv / 2
    blend_c = c + clamp(filt_c - c, -qhalf, qhalf)
    blend_b = b + clamp(filt_b - b, -qhalf, qhalf)
    blend_d = d + clamp(filt_d - d, -qhalf, qhalf)
    blend_e = e + clamp(filt_e - e, -qhalf, qhalf)
    blend_c = z3.If((h / samples_per_unit) == 0, a, blend_c)
    qr0 = variables[str(strategy.get("residual_ports")[0])]
    qr1 = variables[str(strategy.get("residual_ports")[1])]
    mmap = z3.If(h % samples_per_unit == 0,
                 clamp(a + blend_b - blend_c, minimum(a, blend_b), maximum(a, blend_b)),
                 z3.If(h % samples_per_unit == 1,
                       clamp(a + blend_d - blend_c + qr0 * qdiv,
                             minimum(a, minimum(blend_b, blend_d)),
                             maximum(a, maximum(blend_b, blend_d))),
                       clamp(a + blend_e - blend_c + (qr0 + qr1) * qdiv,
                             minimum(a, minimum(blend_b, minimum(blend_d, blend_e))),
                             maximum(a, maximum(blend_b, maximum(blend_d, blend_e))))))
    left = z3.If(h % samples_per_unit == 0,
                 a,
                 z3.If(h % samples_per_unit == 1,
                       clamp(a + qr0 * qdiv, 0, pow2_expr(bpc, 8, 16) - 1),
                       clamp(a + (qr0 + qr1) * qdiv, 0, pow2_expr(bpc, 8, 16) - 1)))
    bp = z3.If(h + padding_left - 1 - (pred - 2) < 0,
               0,
               h + padding_left - 1 - (pred - 2))
    block = sum_expr([z3.If(bp == index, sample_ports[index], 0)
                      for index in sorted(sample_ports)])
    return z3.If(pred == 0, mmap, z3.If(pred == 1, left, block))


def dynamic_structural_partitions(
    contract: dict[str, Any],
    variables: dict[str, Any],
) -> list[dict[str, Any]]:
    """Return a complete, solver-friendly partition of a dynamic hPos domain.

    The relative window is piecewise by the early/late line-buffer boundary,
    hPos modulo SAMPLES_PER_UNIT, and predType.  MMAP has the heaviest
    arithmetic branch structure, so its legal bit-depth/qLevel combinations
    are split as well.  The union of these cases is exactly the reviewed
    input domain; no concrete sample tap is fixed by this partition.
    """
    semantics = contract.get("semantics", {}) or {}
    window = semantics.get("window_spec", {}) or {}
    dynamic = window.get("dynamic_line_window")
    if not isinstance(dynamic, dict) or not dynamic:
        return []
    strategy = semantics.get("legal_vector_strategy") or {}
    h_name = str(strategy.get("hpos_port"))
    pred_name = str(strategy.get("pred_type_port"))
    bpc_name = str(strategy.get("bit_depth_port"))
    q_name = str(strategy.get("qlevel_port"))
    if not all(name in variables for name in (h_name, pred_name, bpc_name, q_name)):
        raise FormalError("dynamic formal partition references a missing control port")

    def values_for(name: str) -> list[int]:
        port = next(
            (
                item for item in contract.get("interface", {}).get("ports", [])
                if str(item.get("name")) == name
            ),
            None,
        )
        if not isinstance(port, dict):
            raise FormalError(f"dynamic formal partition cannot find port: {name}")
        values = domain_values(port.get("legal_domain") or {})
        if not values:
            raise FormalError(f"dynamic formal partition needs a finite domain: {name}")
        return values

    h_values = values_for(h_name)
    pred_values = values_for(pred_name)
    bpc_values = values_for(bpc_name)
    q_values = values_for(q_name)
    h = variables[h_name]
    pred = variables[pred_name]
    bpc = variables[bpc_name]
    q = variables[q_name]
    h_min = min(h_values)
    h_max = max(h_values)
    samples_per_unit = int(dynamic.get("samples_per_unit", 3))
    boundary = int(dynamic.get("current_window_left", 8))
    regions: list[tuple[str, Any]] = []
    if h_min <= boundary:
        regions.append(("EARLY", h <= boundary))
    if h_max > boundary:
        regions.append(("LATE", h > boundary))

    partitions: list[dict[str, Any]] = []
    for region_name, region_constraint in regions:
        for remainder in range(samples_per_unit):
            residue_constraint = h % samples_per_unit == remainder
            for pred_value in pred_values:
                controls: list[Any] = [
                    region_constraint,
                    residue_constraint,
                    pred == pred_value,
                ]
                if pred_value == 0:
                    for bpc_value in bpc_values:
                        for q_value in q_values:
                            partitions.append({
                                "region": region_name,
                                "hpos_remainder": remainder,
                                "predType": pred_value,
                                "cpnt_bit_depth": bpc_value,
                                "qLevel": q_value,
                                "constraints": controls + [bpc == bpc_value, q == q_value],
                            })
                else:
                    partitions.append({
                        "region": region_name,
                        "hpos_remainder": remainder,
                        "predType": pred_value,
                        "constraints": controls,
                    })
    return partitions


def run_partitioned_proof(
    contract: dict[str, Any],
    variables: dict[str, Any],
    c_model: Any,
    rtl: Any,
    partitions: list[dict[str, Any]],
    timeout_ms: int,
) -> dict[str, Any]:
    """Check every structural partition while preserving full symbolic taps."""
    per_partition_timeout = min(max(int(timeout_ms), 1000), 10000)
    total_constraints = 0
    checked = 0
    for partition in partitions:
        solver = z3.Solver()
        solver.set(timeout=per_partition_timeout)
        add_domain_constraints(solver, contract, variables)
        solver.add(*partition["constraints"])
        solver.add(c_model != rtl)
        total_constraints += len(solver.assertions())
        checked += 1
        result = solver.check()
        if result == z3.sat:
            model = solver.model()
            return {
                "status": "COUNTEREXAMPLE",
                "proof_complete": False,
                "constraint_count": total_constraints,
                "partition_count": len(partitions),
                "partitions_checked": checked,
                "proof_strategy": "STRUCTURAL_HPOS_RESIDUE_PARTITION",
                "counterexample": {
                    name: model.eval(value, model_completion=True).as_long()
                    for name, value in variables.items()
                },
                "expected": model.eval(c_model, model_completion=True).as_long(),
                "actual": model.eval(rtl, model_completion=True).as_long(),
                "partition": {
                    key: value for key, value in partition.items() if key != "constraints"
                },
            }
        if result == z3.unknown:
            return {
                "status": "UNKNOWN",
                "proof_complete": False,
                "constraint_count": total_constraints,
                "partition_count": len(partitions),
                "partitions_checked": checked,
                "proof_strategy": "STRUCTURAL_HPOS_RESIDUE_PARTITION",
                "reason": solver.reason_unknown(),
                "partition": {
                    key: value for key, value in partition.items() if key != "constraints"
                },
            }
    return {
        "status": "PASS",
        "proof_complete": True,
        "constraint_count": total_constraints,
        "partition_count": len(partitions),
        "partitions_checked": checked,
        "proof_strategy": "STRUCTURAL_HPOS_RESIDUE_PARTITION",
    }


def load_candidate_module(path: Path, verilator: str) -> dict[str, Any]:
    with tempfile.TemporaryDirectory(prefix="dsc-formal-") as directory:
        output = Path(directory) / "candidate.json"
        mdir = Path(directory) / "obj"
        result = subprocess.run(
            [verilator, "--Wno-fatal", "--json-only", "--json-only-output", str(output),
             "--Mdir", str(mdir), str(path)],
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            check=False,
        )
        if result.returncode != 0:
            raise FormalError(f"Verilator AST export failed ({result.returncode}): {result.stdout[-4000:]}")
        document = json.loads(output.read_text(encoding="utf-8"))
    modules = [module for module in document.get("modulesp", []) if isinstance(module, dict)]
    candidates = [module for module in modules if any(
        isinstance(node, dict) and node.get("type") == "ALWAYS"
        for node in as_list(module.get("stmtsp"))
    )]
    if len(candidates) != 1:
        raise FormalError(f"expected one combinational candidate module, found {len(candidates)}")
    return candidates[0]


def run_proof(contract_path: Path, candidate_path: Path, verilator: str, timeout_ms: int) -> dict[str, Any]:
    contract = json.loads(contract_path.read_text(encoding="utf-8"))
    semantics = contract.get("semantics", {}) or {}
    if semantics.get("kind") != "windowed_sample_predict":
        raise FormalError("formal_rtl currently supports only a reviewed windowed_sample_predict contract")
    ports = [port for port in contract.get("interface", {}).get("ports", []) if isinstance(port, dict)]
    inputs = [port for port in ports if port.get("direction") == "input"]
    output = next((port for port in ports if port.get("direction") == "output"), None)
    if output is None:
        raise FormalError("locked contract has no output port")
    variables = {str(port.get("name")): z3.Int(str(port.get("name"))) for port in inputs}
    solver = z3.Solver()
    solver.set(timeout=int(timeout_ms))
    add_domain_constraints(solver, contract, variables)
    module = load_candidate_module(candidate_path, verilator)
    rtl = AstInterpreter(module).output_expression(variables, str(output.get("name")))
    c_model = contract_expression(contract, variables)
    partitions = dynamic_structural_partitions(contract, variables)
    if partitions:
        partitioned = run_partitioned_proof(
            contract,
            variables,
            c_model,
            rtl,
            partitions,
            timeout_ms,
        )
        partitioned.update({
            "schema_version": 1,
            "contract_id": contract.get("contract_id"),
            "contract_sha256": file_digest(contract_path),
            "candidate": candidate_path.name,
            "candidate_path": str(candidate_path),
            "candidate_sha256": file_digest(candidate_path),
            "solver": "z3",
            "ast_frontend": "verilator --json-only",
            "proof_basis": "locked exact spec-linked window equations versus parsed combinational RTL AST",
            "timeout_ms": int(timeout_ms),
        })
        return partitioned
    solver.add(c_model != rtl)
    result = solver.check()
    receipt: dict[str, Any] = {
        "schema_version": 1,
        "contract_id": contract.get("contract_id"),
        "contract_sha256": file_digest(contract_path),
        "candidate": candidate_path.name,
        "candidate_path": str(candidate_path),
        "candidate_sha256": file_digest(candidate_path),
        "solver": "z3",
        "ast_frontend": "verilator --json-only",
        "proof_basis": "locked exact spec-linked window equations versus parsed combinational RTL AST",
        "timeout_ms": int(timeout_ms),
        "constraint_count": len(solver.assertions()),
        "status": "PASS" if result == z3.unsat else "COUNTEREXAMPLE" if result == z3.sat else "UNKNOWN",
        "proof_complete": result == z3.unsat,
    }
    if result == z3.sat:
        model = solver.model()
        receipt["counterexample"] = {
            name: model.eval(value, model_completion=True).as_long()
            for name, value in variables.items()
        }
        receipt["expected"] = model.eval(c_model, model_completion=True).as_long()
        receipt["actual"] = model.eval(rtl, model_completion=True).as_long()
    elif result == z3.unknown:
        receipt["reason"] = solver.reason_unknown()
    return receipt


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--contract", required=True, type=Path)
    parser.add_argument("--candidate", required=True, type=Path)
    parser.add_argument("--output", type=Path)
    parser.add_argument("--verilator", default="verilator")
    parser.add_argument("--timeout-ms", type=int, default=120000)
    args = parser.parse_args()
    try:
        receipt = run_proof(args.contract, args.candidate, args.verilator, args.timeout_ms)
    except (FormalError, OSError, json.JSONDecodeError) as error:
        receipt = {
            "schema_version": 1,
            "contract_id": None,
            "candidate": args.candidate.name,
            "status": "INFRASTRUCTURE_FAILURE",
            "proof_complete": False,
            "error": str(error),
        }
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(json.dumps(receipt, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(receipt, indent=2, sort_keys=True))
    return 0 if receipt.get("status") == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
