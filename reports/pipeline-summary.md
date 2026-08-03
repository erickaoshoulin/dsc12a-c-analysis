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
  - executed vectors/shards: 65536/8; shard seconds: [1.135, 1.162, 1.132, 1.1, 1.068, 1.071, 1.065, 1.066]; domain_proof_complete=True; formal=NOT_APPLICABLE/False; strategy=cartesian
  - matrix modes: {"C_ONLY": "PASS", "RTL_RETURN": "PASS", "SHADOW": "PASS"}
  - dependency evidence: {"call_sites": 2, "compile_commands": true, "direct_call_sites": 2, "matrix_commands": true, "vectors": true}
- escapecodesize: PASS (EXECUTED_NOW); rtl=REUSED_ACCEPTED_RTL; unit=EXHAUSTIVE_EQUIVALENT; dependency=PASS; matrix=PASS; library=VERIFIED_REFRESH
  - executed vectors/shards: 16320/8; shard seconds: [0.834, 0.839, 0.758, 0.746, 0.731, 0.804, 0.765, 0.764]; domain_proof_complete=True; formal=NOT_APPLICABLE/False; strategy=cartesian
  - matrix modes: {"C_ONLY": "PASS", "RTL_RETURN": "PASS", "SHADOW": "PASS"}
  - dependency evidence: {"call_sites": 2, "compile_commands": true, "direct_call_sites": 2, "matrix_commands": true, "vectors": true}
- estimatebitsforgroup: PASS (EXECUTED_NOW); rtl=REUSED_ACCEPTED_RTL; unit=FORMAL_EQUIVALENT; dependency=PASS; matrix=PASS; library=VERIFIED_REFRESH
  - executed vectors/shards: 1040928/8; shard seconds: [1.242, 1.311, 1.302, 1.228, 1.294, 1.287, 1.276, 1.263]; domain_proof_complete=False; formal=PASS/True; strategy=estimate_bits
  - matrix modes: {"C_ONLY": "PASS", "RTL_RETURN": "PASS", "SHADOW": "PASS"}
  - dependency evidence: {"call_sites": 1, "compile_commands": true, "direct_call_sites": 1, "matrix_commands": true, "vectors": true}
- findmidpoint: PASS (EXECUTED_NOW); rtl=REUSED_ACCEPTED_RTL; unit=EXHAUSTIVE_EQUIVALENT; dependency=PASS; matrix=PASS; library=VERIFIED_REFRESH
  - executed vectors/shards: 8207360/8; shard seconds: [3.977, 3.454, 3.849, 4.09, 4.123, 4.012, 4.065, 4.138]; domain_proof_complete=True; formal=NOT_APPLICABLE/False; strategy=conditional
  - matrix modes: {"C_ONLY": "PASS", "RTL_RETURN": "PASS", "SHADOW": "PASS"}
  - dependency evidence: {"call_sites": 3, "compile_commands": true, "direct_call_sites": 3, "matrix_commands": true, "vectors": true}
- findresidualsize: PASS (EXECUTED_NOW); rtl=REUSED_ACCEPTED_RTL; unit=EXHAUSTIVE_EQUIVALENT; dependency=PASS; matrix=PASS; library=VERIFIED_REFRESH
  - executed vectors/shards: 131071/8; shard seconds: [1.68, 1.73, 1.684, 1.675, 1.652, 1.61, 1.583, 1.669]; domain_proof_complete=True; formal=NOT_APPLICABLE/False; strategy=cartesian
  - matrix modes: {"C_ONLY": "PASS", "RTL_RETURN": "PASS", "SHADOW": "PASS"}
  - dependency evidence: {"call_sites": 6, "compile_commands": true, "direct_call_sites": 6, "matrix_commands": true, "vectors": true}
- getqpadjpredsize: PASS (EXECUTED_NOW); rtl=REUSED_ACCEPTED_RTL; unit=EXHAUSTIVE_EQUIVALENT; dependency=PASS; matrix=PASS; library=VERIFIED_REFRESH
  - executed vectors/shards: 14831616/8; shard seconds: [6.099, 6.09, 6.126, 6.011, 6.174, 5.677, 5.954, 5.492]; domain_proof_complete=True; formal=NOT_APPLICABLE/False; strategy=table_lookup
  - matrix modes: {"C_ONLY": "PASS", "RTL_RETURN": "PASS", "SHADOW": "PASS"}
  - dependency evidence: {"call_sites": 3, "compile_commands": true, "direct_call_sites": 3, "matrix_commands": true, "vectors": true}
- isflatnessinfosent: PASS (EXECUTED_NOW); rtl=REUSED_ACCEPTED_RTL; unit=EXHAUSTIVE_EQUIVALENT; dependency=PASS; matrix=PASS; library=VERIFIED_REFRESH
  - executed vectors/shards: 32768/8; shard seconds: [1.429, 1.514, 1.506, 1.425, 1.467, 1.435, 1.403, 1.321]; domain_proof_complete=True; formal=NOT_APPLICABLE/False; strategy=cartesian
  - matrix modes: {"C_ONLY": "PASS", "RTL_RETURN": "PASS", "SHADOW": "PASS"}
  - dependency evidence: {"call_sites": 4, "compile_commands": true, "direct_call_sites": 4, "matrix_commands": true, "vectors": true}
- isorigflathindex: PASS (EXECUTED_NOW); rtl=REUSED_ACCEPTED_RTL; unit=FORMAL_EQUIVALENT; dependency=PASS; matrix=PASS; library=VERIFIED_REFRESH
  - executed vectors/shards: 575552/8; shard seconds: [1.351, 1.347, 1.405, 1.398, 1.283, 1.343, 1.374, 1.267]; domain_proof_complete=False; formal=PASS/True; strategy=flatness_window
  - matrix modes: {"C_ONLY": "PASS", "RTL_RETURN": "PASS", "SHADOW": "PASS"}
  - dependency evidence: {"call_sites": 2, "compile_commands": true, "direct_call_sites": 2, "matrix_commands": true, "vectors": true}
- mapqptoqlevel: PASS (EXECUTED_NOW); rtl=REUSED_ACCEPTED_RTL; unit=EXHAUSTIVE_EQUIVALENT; dependency=PASS; matrix=PASS; library=VERIFIED_REFRESH
  - executed vectors/shards: 5548800/8; shard seconds: [3.635, 3.732, 3.517, 3.669, 3.591, 3.468, 3.604, 3.293]; domain_proof_complete=True; formal=NOT_APPLICABLE/False; strategy=cartesian
  - matrix modes: {"C_ONLY": "PASS", "RTL_RETURN": "PASS", "SHADOW": "PASS"}
  - dependency evidence: {"call_sites": 12, "compile_commands": true, "direct_call_sites": 12, "matrix_commands": true, "vectors": true}
- maxresidualsize: PASS (EXECUTED_NOW); rtl=REUSED_ACCEPTED_RTL; unit=EXHAUSTIVE_EQUIVALENT; dependency=PASS; matrix=PASS; library=VERIFIED_REFRESH
  - executed vectors/shards: 27744000/8; shard seconds: [11.768, 11.013, 11.997, 11.808, 11.887, 12.079, 12.03, 11.829]; domain_proof_complete=True; formal=NOT_APPLICABLE/False; strategy=cartesian
  - matrix modes: {"C_ONLY": "PASS", "RTL_RETURN": "PASS", "SHADOW": "PASS"}
  - dependency evidence: {"call_sites": 8, "compile_commands": true, "direct_call_sites": 8, "matrix_commands": true, "vectors": true}
- predictsize: PASS (EXECUTED_NOW); rtl=REUSED_ACCEPTED_RTL; unit=EXHAUSTIVE_EQUIVALENT; dependency=PASS; matrix=PASS; library=VERIFIED_REFRESH
  - executed vectors/shards: 4913/8; shard seconds: [0.967, 0.967, 1.01, 0.982, 1.011, 0.99, 0.964, 0.982]; domain_proof_complete=True; formal=NOT_APPLICABLE/False; strategy=cartesian
  - matrix modes: {"C_ONLY": "PASS", "RTL_RETURN": "PASS", "SHADOW": "PASS"}
  - dependency evidence: {"call_sites": 2, "compile_commands": true, "direct_call_sites": 2, "matrix_commands": true, "vectors": true}
- qp2qlevel: PASS (EXECUTED_NOW); rtl=REUSED_ACCEPTED_RTL; unit=EXHAUSTIVE_EQUIVALENT; dependency=PASS; matrix=PASS; library=VERIFIED_REFRESH
  - executed vectors/shards: 5760/8; shard seconds: [1.58, 1.59, 1.597, 1.584, 1.617, 1.622, 1.591, 1.584]; domain_proof_complete=True; formal=NOT_APPLICABLE/False; strategy=qp_table
  - matrix modes: {"C_ONLY": "PASS", "RTL_RETURN": "PASS", "SHADOW": "PASS"}
  - dependency evidence: {"call_sites": 2, "compile_commands": true, "direct_call_sites": 2, "matrix_commands": true, "vectors": true}
- quantizeresidual: PASS (EXECUTED_NOW); rtl=REUSED_ACCEPTED_RTL; unit=EXHAUSTIVE_EQUIVALENT; dependency=PASS; matrix=PASS; library=VERIFIED_REFRESH
  - executed vectors/shards: 2228207/8; shard seconds: [1.57, 1.531, 1.411, 1.577, 1.627, 1.637, 1.549, 1.434]; domain_proof_complete=True; formal=NOT_APPLICABLE/False; strategy=cartesian
  - matrix modes: {"C_ONLY": "PASS", "RTL_RETURN": "PASS", "SHADOW": "PASS"}
  - dependency evidence: {"call_sites": 3, "compile_commands": true, "direct_call_sites": 3, "matrix_commands": true, "vectors": true}
- samplepredict: PASS (EXECUTED_NOW); rtl=REUSED_ACCEPTED_RTL; unit=FORMAL_EQUIVALENT; dependency=PASS; matrix=PASS; library=VERIFIED_REFRESH
  - executed vectors/shards: 25960080/8; shard seconds: [20.209, 20.442, 20.311, 20.684, 19.627, 20.787, 20.128, 20.525]; domain_proof_complete=False; formal=PASS/True; strategy=windowed_boundary
  - matrix modes: {"C_ONLY": "PASS", "RTL_RETURN": "PASS", "SHADOW": "PASS"}
  - dependency evidence: {"call_sites": 5, "compile_commands": true, "direct_call_sites": 5, "matrix_commands": true, "vectors": true}
- samptolinebuf: PASS (EXECUTED_NOW); rtl=REUSED_ACCEPTED_RTL; unit=EXHAUSTIVE_EQUIVALENT; dependency=PASS; matrix=PASS; library=VERIFIED_REFRESH
  - executed vectors/shards: 21233664/8; shard seconds: [8.037, 8.655, 8.868, 8.597, 8.397, 8.703, 8.934, 8.8]; domain_proof_complete=True; formal=NOT_APPLICABLE/False; strategy=cartesian
  - matrix modes: {"C_ONLY": "PASS", "RTL_RETURN": "PASS", "SHADOW": "PASS"}
  - dependency evidence: {"call_sites": 2, "compile_commands": true, "direct_call_sites": 2, "matrix_commands": true, "vectors": true}
- usingmidpoint: PASS (EXECUTED_NOW); rtl=REUSED_ACCEPTED_RTL; unit=FORMAL_EQUIVALENT; dependency=PASS; matrix=PASS; library=VERIFIED_REFRESH
  - executed vectors/shards: 385344/8; shard seconds: [0.931, 0.916, 0.921, 0.91, 0.881, 0.905, 0.91, 0.873]; domain_proof_complete=False; formal=PASS/True; strategy=using_midpoint
  - matrix modes: {"C_ONLY": "PASS", "RTL_RETURN": "PASS", "SHADOW": "PASS"}
  - dependency evidence: {"call_sites": 1, "compile_commands": true, "direct_call_sites": 1, "matrix_commands": true, "vectors": true}

## Blockers

- ichdecision: human_promotion_approval_pending
- ichdecision: human_promotion_approval_required
