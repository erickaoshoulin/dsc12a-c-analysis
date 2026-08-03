# Executable generic C-to-RTL pipeline

This report is produced from the current run receipts. The PDF and immutable C model remain external inputs.

- PDF: /Users/snow/Desktop/Display Stream Compression (DSC)/DSC 1.2a/DSC_v1.2a.pdf (724c0979b0a04bb9a5ad7143755bf6fab4bf8cf9598d24a536a5048a66e2aecd)
- C source root: /Users/snow/Desktop/Display Stream Compression (DSC)/DSC 1.2a/DSC_model_20210623 (1cd2ac33e983d1489b2fcc5e138324efba18069db5a6bbe72f6cce3b7d8b9cdf)
- selected contracts: ceil_log2, escapecodesize, estimatebitsforgroup, findmidpoint, findresidualsize, getqpadjpredsize, isflatnessinfosent, isorigflathindex, mapqptoqlevel, maxresidualsize, predictsize, qp2qlevel, quantizeresidual, samplepredict, samptolinebuf, usingmidpoint
- selected new work: none
- generator invocations: 0
- model calls: 0
- token count: 0
- dependency pair: {"call_sites": [{"callee_contract": "ceil_log2", "callee_function": "ceil_log2", "callee_usr": "c:@F@ceil_log2", "caller_contract": "ichdecision", "caller_function": "IchDecision", "caller_usr": "c:@F@IchDecision", "location": {"column": 21, "file": "dsc_codec.c", "line": 513}, "source": "facts/callgraph.json"}, {"callee_contract": "ceil_log2", "callee_function": "ceil_log2", "callee_usr": "c:@F@ceil_log2", "caller_contract": "ichdecision", "caller_function": "IchDecision", "caller_usr": "c:@F@IchDecision", "location": {"column": 23, "file": "dsc_codec.c", "line": 514}, "source": "facts/callgraph.json"}], "callee_contract": "ceil_log2", "callee_function": "ceil_log2", "callee_usr": "c:@F@ceil_log2", "caller_contract": "ichdecision", "caller_function": "IchDecision", "caller_usr": "c:@F@IchDecision", "selection_basis": "smallest acyclic direct call site from facts/callgraph.json"}
- baseline scripts discovered: 22

## Results

- ceil_log2: PASS (EXECUTED_NOW); rtl=REUSED_ACCEPTED_RTL; unit=EXHAUSTIVE_EQUIVALENT; dependency=PASS; matrix=PASS; library=VERIFIED_REFRESH
  - executed vectors/shards: 65536/8; shard seconds: [2.006, 1.978, 1.943, 1.923, 1.917, 1.92, 1.948, 1.88]; domain_proof_complete=True; formal=NOT_APPLICABLE/False; strategy=cartesian
  - matrix modes: {"C_ONLY": "PASS", "RTL_RETURN": "PASS", "SHADOW": "PASS"}
  - dependency evidence: {"call_sites": 2, "compile_commands": true, "direct_call_sites": 2, "matrix_commands": true, "vectors": true}
- escapecodesize: PASS (EXECUTED_NOW); rtl=REUSED_ACCEPTED_RTL; unit=EXHAUSTIVE_EQUIVALENT; dependency=PASS; matrix=PASS; library=VERIFIED_REFRESH
  - executed vectors/shards: 16320/8; shard seconds: [0.868, 0.853, 0.837, 0.784, 0.771, 0.814, 0.766, 0.799]; domain_proof_complete=True; formal=NOT_APPLICABLE/False; strategy=cartesian
  - matrix modes: {"C_ONLY": "PASS", "RTL_RETURN": "PASS", "SHADOW": "PASS"}
  - dependency evidence: {"call_sites": 2, "compile_commands": true, "direct_call_sites": 2, "matrix_commands": true, "vectors": true}
- estimatebitsforgroup: PASS (EXECUTED_NOW); rtl=REUSED_ACCEPTED_RTL; unit=FORMAL_EQUIVALENT; dependency=PASS; matrix=PASS; library=VERIFIED_REFRESH
  - executed vectors/shards: 1040928/8; shard seconds: [1.337, 1.322, 1.313, 1.275, 1.297, 1.283, 1.305, 1.329]; domain_proof_complete=False; formal=PASS/True; strategy=estimate_bits
  - matrix modes: {"C_ONLY": "PASS", "RTL_RETURN": "PASS", "SHADOW": "PASS"}
  - dependency evidence: {"call_sites": 1, "compile_commands": true, "direct_call_sites": 1, "matrix_commands": true, "vectors": true}
- findmidpoint: PASS (EXECUTED_NOW); rtl=REUSED_ACCEPTED_RTL; unit=EXHAUSTIVE_EQUIVALENT; dependency=PASS; matrix=PASS; library=VERIFIED_REFRESH
  - executed vectors/shards: 8207360/8; shard seconds: [3.907, 4.054, 4.087, 3.996, 4.039, 4.015, 3.936, 3.312]; domain_proof_complete=True; formal=NOT_APPLICABLE/False; strategy=conditional
  - matrix modes: {"C_ONLY": "PASS", "RTL_RETURN": "PASS", "SHADOW": "PASS"}
  - dependency evidence: {"call_sites": 3, "compile_commands": true, "direct_call_sites": 3, "matrix_commands": true, "vectors": true}
- findresidualsize: PASS (EXECUTED_NOW); rtl=REUSED_ACCEPTED_RTL; unit=EXHAUSTIVE_EQUIVALENT; dependency=PASS; matrix=PASS; library=VERIFIED_REFRESH
  - executed vectors/shards: 131071/8; shard seconds: [1.736, 1.705, 1.667, 1.628, 1.583, 1.565, 1.555, 1.493]; domain_proof_complete=True; formal=NOT_APPLICABLE/False; strategy=cartesian
  - matrix modes: {"C_ONLY": "PASS", "RTL_RETURN": "PASS", "SHADOW": "PASS"}
  - dependency evidence: {"call_sites": 6, "compile_commands": true, "direct_call_sites": 6, "matrix_commands": true, "vectors": true}
- getqpadjpredsize: PASS (EXECUTED_NOW); rtl=REUSED_ACCEPTED_RTL; unit=EXHAUSTIVE_EQUIVALENT; dependency=PASS; matrix=PASS; library=VERIFIED_REFRESH
  - executed vectors/shards: 14831616/8; shard seconds: [6.031, 6.124, 5.433, 5.53, 5.934, 6.137, 5.975, 6.107]; domain_proof_complete=True; formal=NOT_APPLICABLE/False; strategy=table_lookup
  - matrix modes: {"C_ONLY": "PASS", "RTL_RETURN": "PASS", "SHADOW": "PASS"}
  - dependency evidence: {"call_sites": 3, "compile_commands": true, "direct_call_sites": 3, "matrix_commands": true, "vectors": true}
- isflatnessinfosent: PASS (EXECUTED_NOW); rtl=REUSED_ACCEPTED_RTL; unit=EXHAUSTIVE_EQUIVALENT; dependency=PASS; matrix=PASS; library=VERIFIED_REFRESH
  - executed vectors/shards: 32768/8; shard seconds: [1.403, 1.404, 1.477, 1.467, 1.463, 1.376, 1.318, 1.374]; domain_proof_complete=True; formal=NOT_APPLICABLE/False; strategy=cartesian
  - matrix modes: {"C_ONLY": "PASS", "RTL_RETURN": "PASS", "SHADOW": "PASS"}
  - dependency evidence: {"call_sites": 4, "compile_commands": true, "direct_call_sites": 4, "matrix_commands": true, "vectors": true}
- isorigflathindex: PASS (EXECUTED_NOW); rtl=REUSED_ACCEPTED_RTL; unit=FORMAL_EQUIVALENT; dependency=PASS; matrix=PASS; library=VERIFIED_REFRESH
  - executed vectors/shards: 575552/8; shard seconds: [1.347, 1.283, 1.279, 1.224, 1.317, 1.305, 1.214, 1.26]; domain_proof_complete=False; formal=PASS/True; strategy=flatness_window
  - matrix modes: {"C_ONLY": "PASS", "RTL_RETURN": "PASS", "SHADOW": "PASS"}
  - dependency evidence: {"call_sites": 2, "compile_commands": true, "direct_call_sites": 2, "matrix_commands": true, "vectors": true}
- mapqptoqlevel: PASS (EXECUTED_NOW); rtl=REUSED_ACCEPTED_RTL; unit=EXHAUSTIVE_EQUIVALENT; dependency=PASS; matrix=PASS; library=VERIFIED_REFRESH
  - executed vectors/shards: 5548800/8; shard seconds: [3.71, 3.894, 3.879, 3.769, 3.995, 3.859, 3.558, 3.994]; domain_proof_complete=True; formal=NOT_APPLICABLE/False; strategy=cartesian
  - matrix modes: {"C_ONLY": "PASS", "RTL_RETURN": "PASS", "SHADOW": "PASS"}
  - dependency evidence: {"call_sites": 12, "compile_commands": true, "direct_call_sites": 12, "matrix_commands": true, "vectors": true}
- maxresidualsize: PASS (EXECUTED_NOW); rtl=REUSED_ACCEPTED_RTL; unit=EXHAUSTIVE_EQUIVALENT; dependency=PASS; matrix=PASS; library=VERIFIED_REFRESH
  - executed vectors/shards: 27744000/8; shard seconds: [11.698, 11.83, 11.658, 11.857, 11.954, 11.755, 11.221, 11.897]; domain_proof_complete=True; formal=NOT_APPLICABLE/False; strategy=cartesian
  - matrix modes: {"C_ONLY": "PASS", "RTL_RETURN": "PASS", "SHADOW": "PASS"}
  - dependency evidence: {"call_sites": 8, "compile_commands": true, "direct_call_sites": 8, "matrix_commands": true, "vectors": true}
- predictsize: PASS (EXECUTED_NOW); rtl=REUSED_ACCEPTED_RTL; unit=EXHAUSTIVE_EQUIVALENT; dependency=PASS; matrix=PASS; library=VERIFIED_REFRESH
  - executed vectors/shards: 4913/8; shard seconds: [0.997, 0.971, 1.004, 0.969, 0.971, 1.015, 0.97, 0.987]; domain_proof_complete=True; formal=NOT_APPLICABLE/False; strategy=cartesian
  - matrix modes: {"C_ONLY": "PASS", "RTL_RETURN": "PASS", "SHADOW": "PASS"}
  - dependency evidence: {"call_sites": 2, "compile_commands": true, "direct_call_sites": 2, "matrix_commands": true, "vectors": true}
- qp2qlevel: PASS (EXECUTED_NOW); rtl=REUSED_ACCEPTED_RTL; unit=EXHAUSTIVE_EQUIVALENT; dependency=PASS; matrix=PASS; library=VERIFIED_REFRESH
  - executed vectors/shards: 5760/8; shard seconds: [1.42, 1.399, 1.423, 1.427, 1.422, 1.399, 1.376, 1.422]; domain_proof_complete=True; formal=NOT_APPLICABLE/False; strategy=qp_table
  - matrix modes: {"C_ONLY": "PASS", "RTL_RETURN": "PASS", "SHADOW": "PASS"}
  - dependency evidence: {"call_sites": 2, "compile_commands": true, "direct_call_sites": 2, "matrix_commands": true, "vectors": true}
- quantizeresidual: PASS (EXECUTED_NOW); rtl=REUSED_ACCEPTED_RTL; unit=EXHAUSTIVE_EQUIVALENT; dependency=PASS; matrix=PASS; library=VERIFIED_REFRESH
  - executed vectors/shards: 2228207/8; shard seconds: [1.52, 1.603, 1.551, 1.381, 1.611, 1.389, 1.503, 1.579]; domain_proof_complete=True; formal=NOT_APPLICABLE/False; strategy=cartesian
  - matrix modes: {"C_ONLY": "PASS", "RTL_RETURN": "PASS", "SHADOW": "PASS"}
  - dependency evidence: {"call_sites": 3, "compile_commands": true, "direct_call_sites": 3, "matrix_commands": true, "vectors": true}
- samplepredict: PASS (EXECUTED_NOW); rtl=REUSED_ACCEPTED_RTL; unit=FORMAL_EQUIVALENT; dependency=PASS; matrix=PASS; library=VERIFIED_REFRESH
  - executed vectors/shards: 25960080/8; shard seconds: [20.72, 20.828, 19.694, 19.914, 20.946, 21.02, 20.622, 20.356]; domain_proof_complete=False; formal=PASS/True; strategy=windowed_boundary
  - matrix modes: {"C_ONLY": "PASS", "RTL_RETURN": "PASS", "SHADOW": "PASS"}
  - dependency evidence: {"call_sites": 5, "compile_commands": true, "direct_call_sites": 5, "matrix_commands": true, "vectors": true}
- samptolinebuf: PASS (EXECUTED_NOW); rtl=REUSED_ACCEPTED_RTL; unit=EXHAUSTIVE_EQUIVALENT; dependency=PASS; matrix=PASS; library=VERIFIED_REFRESH
  - executed vectors/shards: 21233664/8; shard seconds: [8.825, 8.652, 8.758, 8.579, 8.997, 8.889, 8.268, 8.343]; domain_proof_complete=True; formal=NOT_APPLICABLE/False; strategy=cartesian
  - matrix modes: {"C_ONLY": "PASS", "RTL_RETURN": "PASS", "SHADOW": "PASS"}
  - dependency evidence: {"call_sites": 2, "compile_commands": true, "direct_call_sites": 2, "matrix_commands": true, "vectors": true}
- usingmidpoint: PASS (EXECUTED_NOW); rtl=REUSED_ACCEPTED_RTL; unit=FORMAL_EQUIVALENT; dependency=PASS; matrix=PASS; library=VERIFIED_REFRESH
  - executed vectors/shards: 385344/8; shard seconds: [0.977, 0.927, 0.93, 0.933, 0.927, 0.976, 0.902, 0.868]; domain_proof_complete=False; formal=PASS/True; strategy=using_midpoint
  - matrix modes: {"C_ONLY": "PASS", "RTL_RETURN": "PASS", "SHADOW": "PASS"}
  - dependency evidence: {"call_sites": 1, "compile_commands": true, "direct_call_sites": 1, "matrix_commands": true, "vectors": true}

## Blockers

- ichdecision: human_promotion_approval_pending
- ichdecision: human_promotion_approval_required
