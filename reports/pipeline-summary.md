# Executable generic C-to-RTL pipeline

This report is produced from the current run receipts. The PDF and immutable C model remain external inputs.

- PDF: /Users/snow/Desktop/Display Stream Compression (DSC)/DSC 1.2a/DSC_v1.2a.pdf (724c0979b0a04bb9a5ad7143755bf6fab4bf8cf9598d24a536a5048a66e2aecd)
- C source root: /Users/snow/Desktop/Display Stream Compression (DSC)/DSC 1.2a/DSC_model_20210623 (1cd2ac33e983d1489b2fcc5e138324efba18069db5a6bbe72f6cce3b7d8b9cdf)
- selected contracts: ichdecision
- selected new work: ichdecision
- generator invocations: 0
- model calls: 0
- token count: 0
- dependency pair: {"call_sites": [{"callee_contract": "ichdecision", "callee_function": "IchDecision", "callee_usr": "c:@F@IchDecision", "caller_contract": null, "caller_function": "VLCUnit", "caller_usr": "c:@F@VLCUnit", "location": {"column": 28, "file": "dsc_codec.c", "line": 1620}, "source": "facts/callgraph.json"}], "callee_contract": "ichdecision", "callee_function": "IchDecision", "callee_usr": "c:@F@IchDecision", "caller_contract": null, "caller_function": "VLCUnit", "caller_usr": "c:@F@VLCUnit", "selection_basis": "smallest acyclic direct call site from facts/callgraph.json"}
- baseline scripts discovered: 22

## Results

- ichdecision: GENERATION_REQUIRED (EXECUTED_NOW); rtl=EXECUTED_NOW; unit=None; dependency=None; matrix=None; library=NOT_ATTEMPTED
  - executed vectors/shards: 0/0; shard seconds: []; domain_proof_complete=True; formal=None/False; strategy=None
  - matrix modes: {"C_ONLY": null, "RTL_RETURN": null, "SHADOW": null}
  - dependency evidence: {"call_sites": 0, "compile_commands": false, "direct_call_sites": 0, "matrix_commands": false, "vectors": false}

## Blockers

- ichdecision: DSC_CICD_GENERATOR_CMD is not configured
- ichdecision: GENERATION_REQUIRED
