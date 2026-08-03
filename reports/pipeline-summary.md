# Executable generic C-to-RTL pipeline

This report is produced from the current run receipts. The PDF and immutable C model remain external inputs.

- PDF: /Users/snow/Desktop/Display Stream Compression (DSC)/DSC 1.2a/DSC_v1.2a.pdf (724c0979b0a04bb9a5ad7143755bf6fab4bf8cf9598d24a536a5048a66e2aecd)
- C source root: /Users/snow/Desktop/Display Stream Compression (DSC)/DSC 1.2a/DSC_model_20210623 (1cd2ac33e983d1489b2fcc5e138324efba18069db5a6bbe72f6cce3b7d8b9cdf)
- selected contracts: findmidpoint
- selected new work: none
- generator invocations: 0
- model calls: 0
- token count: 0
- dependency pair: {"call_sites": [{"callee_contract": "findmidpoint", "callee_function": "FindMidpoint", "callee_usr": "c:@F@FindMidpoint", "caller_contract": null, "caller_function": "PredictionLoop", "caller_usr": "c:@F@PredictionLoop", "location": {"column": 14, "file": "dsc_codec.c", "line": 2452}, "source": "facts/callgraph.json"}, {"callee_contract": "findmidpoint", "callee_function": "FindMidpoint", "callee_usr": "c:@F@FindMidpoint", "caller_contract": null, "caller_function": "PredictionLoop", "caller_usr": "c:@F@PredictionLoop", "location": {"column": 20, "file": "dsc_codec.c", "line": 2483}, "source": "facts/callgraph.json"}, {"callee_contract": "findmidpoint", "callee_function": "FindMidpoint", "callee_usr": "c:@F@FindMidpoint", "caller_contract": null, "caller_function": "PredictionLoop", "caller_usr": "c:@F@PredictionLoop", "location": {"column": 25, "file": "dsc_codec.c", "line": 2421}, "source": "facts/callgraph.json"}], "callee_contract": "findmidpoint", "callee_function": "FindMidpoint", "callee_usr": "c:@F@FindMidpoint", "caller_contract": null, "caller_function": "PredictionLoop", "caller_usr": "c:@F@PredictionLoop", "selection_basis": "smallest acyclic direct call site from facts/callgraph.json"}
- baseline scripts discovered: 22

## Results

- findmidpoint: FAILED (EXECUTED_NOW); rtl=REUSED_ACCEPTED_RTL; unit=EXHAUSTIVE_EQUIVALENT; dependency=FAIL; matrix=COMPOSITION_BLOCKED; library=NOT_ATTEMPTED
  - executed vectors/shards: 8207360/4; shard seconds: [3.327, 3.367, 2.624, 2.697]; domain_proof_complete=True; formal=NOT_APPLICABLE/False; strategy=conditional
  - matrix modes: {"C_ONLY": "PASS", "RTL_RETURN": "NOT_RUN", "SHADOW": "NOT_RUN"}
  - dependency evidence: {"call_sites": 3, "compile_commands": true, "direct_call_sites": 3, "matrix_commands": true, "vectors": true}

## Blockers

- findmidpoint: caller call signature does not provide the frozen DUT interface; retain C boundary
- findmidpoint: dependency composition did not pass all real gates
- ichdecision: prior_composition_boundary_unresolved
- isflatnessinfosent: prior_composition_boundary_unresolved
- mapqptoqlevel: prior_composition_boundary_unresolved
- predictsize: prior_composition_boundary_unresolved
- samplepredict: prior_composition_boundary_unresolved
