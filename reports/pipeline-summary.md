# Executable generic C-to-RTL pipeline

This report is produced from the current run receipts. The PDF and immutable C model remain external inputs.

- PDF: /Users/snow/Desktop/Display Stream Compression (DSC)/DSC 1.2a/DSC_v1.2a.pdf (724c0979b0a04bb9a5ad7143755bf6fab4bf8cf9598d24a536a5048a66e2aecd)
- C source root: /Users/snow/Desktop/Display Stream Compression (DSC)/DSC 1.2a/DSC_model_20210623 (1cd2ac33e983d1489b2fcc5e138324efba18069db5a6bbe72f6cce3b7d8b9cdf)
- selected contracts: estimatebitsforgroup
- selected new work: estimatebitsforgroup
- generator invocations: 1
- model calls: 1
- token count: 32629
- dependency pair: {"call_sites": [{"callee_contract": "estimatebitsforgroup", "callee_function": "EstimateBitsForGroup", "callee_usr": "c:@F@EstimateBitsForGroup", "caller_contract": null, "caller_function": "IchDecision", "caller_usr": "c:@F@IchDecision", "location": {"column": 16, "file": "dsc_codec.c", "line": 522}, "source": "facts/callgraph.json"}], "callee_contract": "estimatebitsforgroup", "callee_function": "EstimateBitsForGroup", "callee_usr": "c:@F@EstimateBitsForGroup", "caller_contract": null, "caller_function": "IchDecision", "caller_usr": "c:@F@IchDecision", "selection_basis": "smallest acyclic direct call site from facts/callgraph.json"}
- baseline scripts discovered: 22

## Results

- estimatebitsforgroup: PROMOTED (EXECUTED_NOW); unit=FORMAL_EQUIVALENT; dependency=PASS; matrix=PASS; library=PASS
  - executed vectors/shards: 1040928/4; shard seconds: [1.602, 1.655, 1.619, 1.653]; domain_proof_complete=False; formal=PASS/True; strategy=estimate_bits
  - matrix modes: {"C_ONLY": "PASS", "RTL_RETURN": "PASS", "SHADOW": "PASS"}
  - dependency evidence: {"call_sites": 1, "compile_commands": true, "direct_call_sites": 1, "matrix_commands": true, "vectors": true}
  - rejected candidate_02: unit=FAIL; bitstream=FAIL; receipt=artifacts/c5df1296bcc105ab0e0796e782a82abc3434bc173f8320565e5f4586f6562a13/rejected/candidate_02/rejection-receipt.json

## Blockers

- none
