# Executable generic C-to-RTL pipeline

This report is produced from the current run receipts. The PDF and immutable C model remain external inputs.

- PDF: /Users/snow/Desktop/Display Stream Compression (DSC)/DSC 1.2a/DSC_v1.2a.pdf (724c0979b0a04bb9a5ad7143755bf6fab4bf8cf9598d24a536a5048a66e2aecd)
- C source root: /Users/snow/Desktop/Display Stream Compression (DSC)/DSC 1.2a/DSC_model_20210623 (1cd2ac33e983d1489b2fcc5e138324efba18069db5a6bbe72f6cce3b7d8b9cdf)
- selected contracts: usingmidpoint
- selected new work: usingmidpoint
- generator invocations: 1
- model calls: 1
- token count: 7731
- dependency pair: {"call_sites": [{"callee_contract": "usingmidpoint", "callee_function": "UsingMidpoint", "callee_usr": "c:@F@UsingMidpoint", "caller_contract": null, "caller_function": "IchDecision", "caller_usr": "c:@F@IchDecision", "location": {"column": 6, "file": "dsc_codec.c", "line": 496}, "source": "facts/callgraph.json"}], "callee_contract": "usingmidpoint", "callee_function": "UsingMidpoint", "callee_usr": "c:@F@UsingMidpoint", "caller_contract": null, "caller_function": "IchDecision", "caller_usr": "c:@F@IchDecision", "selection_basis": "smallest acyclic direct call site from facts/callgraph.json"}
- baseline scripts discovered: 22

## Results

- usingmidpoint: PROMOTED (EXECUTED_NOW); unit=FORMAL_EQUIVALENT; dependency=PASS; matrix=PASS; library=PASS
  - executed vectors/shards: 385344/8; shard seconds: [0.736, 0.693, 0.141, 0.115, 0.116, 0.14, 0.125, 0.106]; domain_proof_complete=False; formal=PASS/True; strategy=using_midpoint
  - matrix modes: {"C_ONLY": "PASS", "RTL_RETURN": "PASS", "SHADOW": "PASS"}
  - dependency evidence: {"call_sites": 1, "compile_commands": true, "direct_call_sites": 1, "matrix_commands": true, "vectors": true}
  - rejected candidate_02: unit=FAIL; bitstream=FAIL; receipt=artifacts/46c31f1a781d9f532c5509d7dfe9f834be86693e1736754aaff40fc7c1e95abf/rejected/candidate_02/rejection-receipt.json

## Blockers

- none
