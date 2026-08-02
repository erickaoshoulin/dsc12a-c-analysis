# Executable generic C-to-RTL pipeline

This report is produced from the current run receipts. The PDF and immutable C model remain external inputs.

- PDF: /Users/snow/Desktop/Display Stream Compression (DSC)/DSC 1.2a/DSC_v1.2a.pdf (724c0979b0a04bb9a5ad7143755bf6fab4bf8cf9598d24a536a5048a66e2aecd)
- C source root: /Users/snow/Desktop/Display Stream Compression (DSC)/DSC 1.2a/DSC_model_20210623 (1cd2ac33e983d1489b2fcc5e138324efba18069db5a6bbe72f6cce3b7d8b9cdf)
- selected new work: samplepredict
- generator invocations: 1
- model calls: 1
- token count: 12302
- dependency pair: {"call_sites": [{"callee_contract": "samplepredict", "callee_function": "SamplePredict", "callee_usr": "c:@F@SamplePredict", "caller_contract": null, "caller_function": "BlockPredSearch", "caller_usr": "c:@F@BlockPredSearch", "location": {"column": 13, "file": "dsc_codec.c", "line": 1002}, "source": "facts/callgraph.json"}], "callee_contract": "samplepredict", "callee_function": "SamplePredict", "callee_usr": "c:@F@SamplePredict", "caller_contract": null, "caller_function": "BlockPredSearch", "caller_usr": "c:@F@BlockPredSearch", "selection_basis": "smallest acyclic direct call site from facts/callgraph.json"}
- baseline scripts discovered: 22

## Results

- samplepredict: PROMOTED (EXECUTED_NOW); unit=FORMAL_EQUIVALENT; dependency=PASS; matrix=PASS
  - executed vectors/shards: 25960080/8; shard seconds: [17.584, 17.037, 17.986, 17.787, 18.116, 17.88, 17.684, 18.051]; sampled_domain_proof_complete=False; formal=PASS/True; formal_partitions=1002/1002; strategy=STRUCTURAL_HPOS_RESIDUE_PARTITION
  - matrix modes: {"C_ONLY": "PASS", "RTL_RETURN": "PASS", "SHADOW": "PASS"}
  - dependency evidence: {"call_sites": 5, "compile_commands": true, "direct_call_sites": 5, "matrix_commands": true, "vectors": true}
  - rejected candidate_02: unit=FAIL; bitstream=FAIL; receipt=artifacts/66e5309e5cf66c9b07022c746307cf37fecbccfa92d7c8ff549ed8b0cbb69509/rejected/candidate_02/rejection-receipt.json

## Blockers

- none
