# Executable generic C-to-RTL pipeline

This report is produced from the current run receipts. The PDF and immutable C model remain external inputs.

- PDF: /Users/snow/Desktop/Display Stream Compression (DSC)/DSC 1.2a/DSC_v1.2a.pdf (724c0979b0a04bb9a5ad7143755bf6fab4bf8cf9598d24a536a5048a66e2aecd)
- C source root: /Users/snow/Desktop/Display Stream Compression (DSC)/DSC 1.2a/DSC_model_20210623 (1cd2ac33e983d1489b2fcc5e138324efba18069db5a6bbe72f6cce3b7d8b9cdf)
- selected contracts: ichdecision
- selected new work: ichdecision
- generator invocations: 1
- model calls: 1
- token count: 24405
- dependency pair: {"call_sites": [{"callee_contract": "ichdecision", "callee_function": "IchDecision", "callee_usr": "c:@F@IchDecision", "caller_contract": null, "caller_function": "VLCUnit", "caller_usr": "c:@F@VLCUnit", "location": {"column": 28, "file": "dsc_codec.c", "line": 1620}, "source": "facts/callgraph.json"}], "callee_contract": "ichdecision", "callee_function": "IchDecision", "callee_usr": "c:@F@IchDecision", "caller_contract": null, "caller_function": "VLCUnit", "caller_usr": "c:@F@VLCUnit", "selection_basis": "smallest acyclic direct call site from facts/callgraph.json"}
- baseline scripts discovered: 22

## Results

- ichdecision: FAILED (EXECUTED_NOW); unit=FORMAL_EQUIVALENT; dependency=FAIL; matrix=COMPOSITION_BLOCKED; library=NOT_ATTEMPTED
  - executed vectors/shards: 187232/4; shard seconds: [1.054, 1.057, 0.345, 0.346]; domain_proof_complete=False; formal=PASS/True; strategy=ich_decision
  - matrix modes: {"C_ONLY": "PASS", "RTL_RETURN": "NOT_RUN", "SHADOW": "NOT_RUN"}
  - dependency evidence: {"call_sites": 1, "compile_commands": true, "direct_call_sites": 1, "matrix_commands": true, "vectors": true}
  - rejected candidate_02: unit=FAIL; bitstream=FAIL; receipt=artifacts/c6ce277dabb46d076d390f7be80c6b6106e2d5aa774f130fa01d3f097ba99919/rejected/candidate_02/rejection-receipt.json

## Blockers

- none
