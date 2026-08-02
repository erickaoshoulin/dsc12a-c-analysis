#!/usr/bin/env python3
"""Check compact pilot receipts without interpreting function names."""

from __future__ import annotations

import json
import pathlib
import re
import sys


SECRET = re.compile(r"//[^/\s]+:[^/\s]+@|password|passwd|secret", re.I)


def main() -> int:
    if len(sys.argv) != 2:
        print("usage: verify_receipts.py RUN_DIR", file=sys.stderr)
        return 2
    root = pathlib.Path(sys.argv[1])
    errors = []
    receipt_paths = sorted(root.glob("functions/*/receipt.json"))
    if not receipt_paths:
        errors.append("no function receipts")
    for path in receipt_paths:
        try:
            value = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as error:
            errors.append(f"{path}: {error}")
            continue
        for key in ("run_id", "contract_id", "status", "execution_status", "stages", "traceability"):
            if key not in value:
                errors.append(f"{path}: missing {key}")
        if SECRET.search(json.dumps(value, ensure_ascii=False)):
            errors.append(f"{path}: possible credential material")
        ports = value.get("traceability", {}).get("ports", [])
        for port in ports:
            for key in ("width", "signed", "domain", "role", "authority", "derivation", "review_status", "contract_hash"):
                if key not in port:
                    errors.append(f"{path}: port missing {key}")
    if errors:
        print(json.dumps({"status": "FAIL", "errors": errors}, indent=2))
        return 1
    print(json.dumps({"status": "PASS", "receipts": len(receipt_paths)}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
