#!/usr/bin/env python3
"""Run one provisional Encode transition through the full frame matrix."""

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
        raise SystemExit(
            "provisional contract or candidate_01.sv is missing"
        )
    agent = Agent(root, "encode-transition-verification")
    agent.load_inputs()
    matrix = agent.run_matrix(
        contract,
        artifact,
        {
            "candidate": candidate.name,
            "path": candidate.name,
            "module": str(
                (contract.get("rtl", {}) or {}).get("module")
                or contract.get("contract_id")
            ),
        },
    )
    encode = matrix.get("encode", {}) or {}
    modes = encode.get("modes", {}) or {}
    shadow_invocations = int(
        (modes.get("SHADOW", {}) or {}).get("total_rtl_invocations", 0)
    )
    rtl_return_invocations = int(
        (modes.get("RTL_RETURN", {}) or {}).get(
            "total_rtl_invocations", 0
        )
    )
    encode_exercised = (
        encode.get("status") == "PASS"
        and shadow_invocations > 0
        and rtl_return_invocations > 0
    )
    status = (
        "PASS"
        if matrix.get("status") == "PASS" and encode_exercised
        else "FAIL"
    )
    receipt = {
        "schema_version": 1,
        "status": status,
        "contract_id": contract.get("contract_id"),
        "candidate": candidate.name,
        "matrix_scope": matrix.get("matrix_scope"),
        "phase_order": matrix.get("phase_order"),
        "encode": {
            "status": encode.get("status"),
            "shadow_rtl_invocations": shadow_invocations,
            "rtl_return_invocations": rtl_return_invocations,
            "phase_specific_replacement_exercised": encode_exercised,
        },
        "decode": {
            "status": (matrix.get("decode", {}) or {}).get("status"),
            "rtl_return_invocations": (
                (
                    (matrix.get("decode", {}) or {})
                    .get("modes", {})
                    .get("RTL_RETURN", {})
                )
                or {}
            ).get("total_rtl_invocations", 0),
        },
        "replacement_coverage": matrix.get(
            "replacement_coverage", {}
        ),
        "promotion_status": "BLOCKED_PENDING_HUMAN_CONTRACT_REVIEW",
        "matrix_receipt": "matrix-receipt.json",
    }
    write_json(artifact / "verification-receipt.json", receipt)
    print(json.dumps(receipt, sort_keys=True))
    return 0 if status == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
