# Executable generic C-to-RTL pipeline

This report is produced from the current run receipts. The PDF and immutable C model remain external inputs.

- PDF: /Users/snow/Desktop/Display Stream Compression (DSC)/DSC 1.2a/DSC_v1.2a.pdf (724c0979b0a04bb9a5ad7143755bf6fab4bf8cf9598d24a536a5048a66e2aecd)
- C source root: /Users/snow/Desktop/Display Stream Compression (DSC)/DSC 1.2a/DSC_model_20210623 (1cd2ac33e983d1489b2fcc5e138324efba18069db5a6bbe72f6cce3b7d8b9cdf)
- selected new work: escapecodesize
- generator invocations: 1
- model calls: 1
- token count: 1696
- dependency pair: {"call_sites": [{"callee_contract": "escapecodesize", "callee_function": "EscapeCodeSize", "callee_usr": "c:@F@EscapeCodeSize", "caller_contract": null, "caller_function": "VLCUnit", "caller_usr": "c:@F@VLCUnit", "location": {"column": 26, "file": "dsc_codec.c", "line": 1614}, "source": "facts/callgraph.json"}], "callee_contract": "escapecodesize", "callee_function": "EscapeCodeSize", "callee_usr": "c:@F@EscapeCodeSize", "caller_contract": null, "caller_function": "VLCUnit", "caller_usr": "c:@F@VLCUnit", "selection_basis": "smallest acyclic direct call site from facts/callgraph.json"}
- baseline scripts discovered: 22

## Results

- escapecodesize: PROMOTED (EXECUTED_NOW); unit=EXHAUSTIVE_EQUIVALENT; dependency=PASS; matrix=PASS
  - executed vectors/shards: 16320/4; shard seconds: [0.862, 0.864, 0.864, 0.858]
  - matrix modes: {"C_ONLY": "PASS", "RTL_RETURN": "PASS", "SHADOW": "PASS"}
  - dependency evidence: {"call_sites": 2, "compile_commands": true, "direct_call_sites": 2, "matrix_commands": true, "vectors": true}
  - rejected candidate_02: unit=FAIL; bitstream=FAIL; receipt=artifacts/57a8e4aaed55ff339fa73fdaa6571457d5438d8a23f474360c12d7a43db68c69/rejected/candidate_02/rejection-receipt.json

## Blockers

- none
