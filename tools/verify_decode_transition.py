#!/usr/bin/env python3
"""Run a generated provisional decode transition through the frame matrix."""

from __future__ import annotations

import argparse
import json
import pathlib

from cicd_agent import Agent, read_json, write_json


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=pathlib.Path, required=True)
    parser.add_argument("--artifact", type=pathlib.Path, required=True)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    root = args.root.resolve()
    artifact = args.artifact.resolve()
    contract = read_json(artifact / "provisional-contract.json", {}) or {}
    candidate = artifact / "candidate_01.sv"
    if not contract or not candidate.is_file():
        raise SystemExit("provisional contract or candidate_01.sv is missing")
    agent = Agent(root, "decode-transition-verification")
    agent.load_inputs()
    candidate_record = {
        "candidate": candidate.name,
        "path": candidate.name,
        "module": str(contract.get("contract_id")),
    }
    matrix = agent.run_matrix(contract, artifact, candidate_record)
    receipt = {
        "schema_version": 1,
        "status": matrix.get("status"),
        "contract_id": contract.get("contract_id"),
        "candidate": candidate.name,
        "matrix_scope": matrix.get("matrix_scope"),
        "phase_order": matrix.get("phase_order"),
        "decode": {
            "status": (matrix.get("decode", {}) or {}).get("status"),
            "coverage_status": (matrix.get("decode", {}) or {}).get("coverage_status"),
            "rtl_return_invocations": (
                (matrix.get("decode", {}) or {}).get("modes", {}).get("RTL_RETURN", {}) or {}
            ).get("total_rtl_invocations", 0),
        },
        "encode": {
            "status": (matrix.get("encode", {}) or {}).get("status"),
            "rtl_return_invocations": (
                (matrix.get("encode", {}) or {}).get("modes", {}).get("RTL_RETURN", {}) or {}
            ).get("total_rtl_invocations", 0),
        },
        "replacement_coverage": matrix.get("replacement_coverage", {}),
        "promotion_status": "BLOCKED_PENDING_HUMAN_CONTRACT_REVIEW",
        "matrix_receipt": "matrix-receipt.json",
    }
    write_json(artifact / "verification-receipt.json", receipt)
    print(json.dumps(receipt, sort_keys=True))
    return 0 if matrix.get("status") == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
