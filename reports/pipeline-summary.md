# Executable generic C-to-RTL pipeline

This report is produced from the current run receipts. The PDF and immutable C model remain external inputs.

- PDF: /Users/snow/Desktop/Display Stream Compression (DSC)/DSC 1.2a/DSC_v1.2a.pdf (724c0979b0a04bb9a5ad7143755bf6fab4bf8cf9598d24a536a5048a66e2aecd)
- C source root: /Users/snow/Desktop/Display Stream Compression (DSC)/DSC 1.2a/DSC_model_20210623 (1cd2ac33e983d1489b2fcc5e138324efba18069db5a6bbe72f6cce3b7d8b9cdf)
- selected contracts: isorigflathindex
- selected new work: isorigflathindex
- generator invocations: 1
- model calls: 1
- token count: 19139
- dependency pair: {"call_sites": [{"callee_contract": "isorigflathindex", "callee_function": "IsOrigFlatHIndex", "callee_usr": "c:@F@IsOrigFlatHIndex", "caller_contract": null, "caller_function": "FlatnessAdjustment", "caller_usr": "c:@F@FlatnessAdjustment", "location": {"column": 21, "file": "dsc_codec.c", "line": 2528}, "source": "facts/callgraph.json"}], "callee_contract": "isorigflathindex", "callee_function": "IsOrigFlatHIndex", "callee_usr": "c:@F@IsOrigFlatHIndex", "caller_contract": null, "caller_function": "FlatnessAdjustment", "caller_usr": "c:@F@FlatnessAdjustment", "selection_basis": "smallest acyclic direct call site from facts/callgraph.json"}
- baseline scripts discovered: 22

## Results

- isorigflathindex: PROMOTED (EXECUTED_NOW); unit=FORMAL_EQUIVALENT; dependency=PASS; matrix=PASS; library=PASS
  - executed vectors/shards: 575552/8; shard seconds: [1.245, 1.272, 1.276, 1.284, 1.234, 1.259, 1.265, 1.272]; domain_proof_complete=False; formal=PASS/True; strategy=flatness_window
  - matrix modes: {"C_ONLY": "PASS", "RTL_RETURN": "PASS", "SHADOW": "PASS"}
  - dependency evidence: {"call_sites": 2, "compile_commands": true, "direct_call_sites": 2, "matrix_commands": true, "vectors": true}
  - rejected candidate_02: unit=FAIL; bitstream=FAIL; receipt=artifacts/15e7e4bc9522fa586e9fcf9db6663660e37f2a62d310df0ae5eee7251fcd1c3a/rejected/candidate_02/rejection-receipt.json

## Blockers

- none
