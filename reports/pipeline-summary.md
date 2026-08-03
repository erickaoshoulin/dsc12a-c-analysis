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
  - executed vectors/shards: 65536/4; shard seconds: [2.119, 2.134, 0.148, 0.147]; domain_proof_complete=True; formal=NOT_APPLICABLE/False; strategy=cartesian
  - matrix modes: {"C_ONLY": "PASS", "RTL_RETURN": "PASS", "SHADOW": "PASS"}
  - dependency evidence: {"call_sites": 2, "compile_commands": true, "direct_call_sites": 2, "matrix_commands": true, "vectors": true}
- escapecodesize: PASS (EXECUTED_NOW); rtl=REUSED_ACCEPTED_RTL; unit=EXHAUSTIVE_EQUIVALENT; dependency=PASS; matrix=PASS; library=VERIFIED_REFRESH
  - executed vectors/shards: 16320/4; shard seconds: [0.886, 0.87, 0.177, 0.165]; domain_proof_complete=True; formal=NOT_APPLICABLE/False; strategy=cartesian
  - matrix modes: {"C_ONLY": "PASS", "RTL_RETURN": "PASS", "SHADOW": "PASS"}
  - dependency evidence: {"call_sites": 2, "compile_commands": true, "direct_call_sites": 2, "matrix_commands": true, "vectors": true}
- estimatebitsforgroup: PASS (EXECUTED_NOW); rtl=REUSED_ACCEPTED_RTL; unit=FORMAL_EQUIVALENT; dependency=PASS; matrix=PASS; library=VERIFIED_REFRESH
  - executed vectors/shards: 1040928/4; shard seconds: [1.476, 1.501, 0.962, 0.934]; domain_proof_complete=False; formal=PASS/True; strategy=estimate_bits
  - matrix modes: {"C_ONLY": "PASS", "RTL_RETURN": "PASS", "SHADOW": "PASS"}
  - dependency evidence: {"call_sites": 1, "compile_commands": true, "direct_call_sites": 1, "matrix_commands": true, "vectors": true}
- findmidpoint: PASS (EXECUTED_NOW); rtl=REUSED_ACCEPTED_RTL; unit=EXHAUSTIVE_EQUIVALENT; dependency=PASS; matrix=PASS; library=VERIFIED_REFRESH
  - executed vectors/shards: 8207360/4; shard seconds: [3.761, 3.843, 3.384, 3.263]; domain_proof_complete=True; formal=NOT_APPLICABLE/False; strategy=conditional
  - matrix modes: {"C_ONLY": "PASS", "RTL_RETURN": "PASS", "SHADOW": "PASS"}
  - dependency evidence: {"call_sites": 3, "compile_commands": true, "direct_call_sites": 3, "matrix_commands": true, "vectors": true}
- findresidualsize: PASS (EXECUTED_NOW); rtl=REUSED_ACCEPTED_RTL; unit=EXHAUSTIVE_EQUIVALENT; dependency=PASS; matrix=PASS; library=VERIFIED_REFRESH
  - executed vectors/shards: 131071/4; shard seconds: [1.561, 1.562, 0.15, 0.148]; domain_proof_complete=True; formal=NOT_APPLICABLE/False; strategy=cartesian
  - matrix modes: {"C_ONLY": "PASS", "RTL_RETURN": "PASS", "SHADOW": "PASS"}
  - dependency evidence: {"call_sites": 6, "compile_commands": true, "direct_call_sites": 6, "matrix_commands": true, "vectors": true}
- getqpadjpredsize: PASS (EXECUTED_NOW); rtl=REUSED_ACCEPTED_RTL; unit=EXHAUSTIVE_EQUIVALENT; dependency=PASS; matrix=PASS; library=VERIFIED_REFRESH
  - executed vectors/shards: 14831616/4; shard seconds: [7.199, 7.246, 7.09, 6.973]; domain_proof_complete=True; formal=NOT_APPLICABLE/False; strategy=table_lookup
  - matrix modes: {"C_ONLY": "PASS", "RTL_RETURN": "PASS", "SHADOW": "PASS"}
  - dependency evidence: {"call_sites": 3, "compile_commands": true, "direct_call_sites": 3, "matrix_commands": true, "vectors": true}
- isflatnessinfosent: PASS (EXECUTED_NOW); rtl=REUSED_ACCEPTED_RTL; unit=EXHAUSTIVE_EQUIVALENT; dependency=PASS; matrix=PASS; library=VERIFIED_REFRESH
  - executed vectors/shards: 32768/4; shard seconds: [1.838, 1.843, 0.102, 0.105]; domain_proof_complete=True; formal=NOT_APPLICABLE/False; strategy=cartesian
  - matrix modes: {"C_ONLY": "PASS", "RTL_RETURN": "PASS", "SHADOW": "PASS"}
  - dependency evidence: {"call_sites": 4, "compile_commands": true, "direct_call_sites": 4, "matrix_commands": true, "vectors": true}
- isorigflathindex: PASS (EXECUTED_NOW); rtl=REUSED_ACCEPTED_RTL; unit=FORMAL_EQUIVALENT; dependency=PASS; matrix=PASS; library=VERIFIED_REFRESH
  - executed vectors/shards: 575552/4; shard seconds: [1.334, 1.32, 0.679, 0.701]; domain_proof_complete=False; formal=PASS/True; strategy=flatness_window
  - matrix modes: {"C_ONLY": "PASS", "RTL_RETURN": "PASS", "SHADOW": "PASS"}
  - dependency evidence: {"call_sites": 2, "compile_commands": true, "direct_call_sites": 2, "matrix_commands": true, "vectors": true}
- mapqptoqlevel: PASS (EXECUTED_NOW); rtl=REUSED_ACCEPTED_RTL; unit=EXHAUSTIVE_EQUIVALENT; dependency=PASS; matrix=PASS; library=VERIFIED_REFRESH
  - executed vectors/shards: 5548800/4; shard seconds: [3.423, 3.412, 2.602, 2.483]; domain_proof_complete=True; formal=NOT_APPLICABLE/False; strategy=cartesian
  - matrix modes: {"C_ONLY": "PASS", "RTL_RETURN": "PASS", "SHADOW": "PASS"}
  - dependency evidence: {"call_sites": 12, "compile_commands": true, "direct_call_sites": 12, "matrix_commands": true, "vectors": true}
- maxresidualsize: PASS (EXECUTED_NOW); rtl=REUSED_ACCEPTED_RTL; unit=EXHAUSTIVE_EQUIVALENT; dependency=PASS; matrix=PASS; library=VERIFIED_REFRESH
  - executed vectors/shards: 27744000/4; shard seconds: [12.037, 12.128, 10.764, 10.623]; domain_proof_complete=True; formal=NOT_APPLICABLE/False; strategy=cartesian
  - matrix modes: {"C_ONLY": "PASS", "RTL_RETURN": "PASS", "SHADOW": "PASS"}
  - dependency evidence: {"call_sites": 8, "compile_commands": true, "direct_call_sites": 8, "matrix_commands": true, "vectors": true}
- predictsize: PASS (EXECUTED_NOW); rtl=REUSED_ACCEPTED_RTL; unit=EXHAUSTIVE_EQUIVALENT; dependency=PASS; matrix=PASS; library=VERIFIED_REFRESH
  - executed vectors/shards: 4913/4; shard seconds: [1.026, 1.026, 0.011, 0.011]; domain_proof_complete=True; formal=NOT_APPLICABLE/False; strategy=cartesian
  - matrix modes: {"C_ONLY": "PASS", "RTL_RETURN": "PASS", "SHADOW": "PASS"}
  - dependency evidence: {"call_sites": 2, "compile_commands": true, "direct_call_sites": 2, "matrix_commands": true, "vectors": true}
- qp2qlevel: PASS (EXECUTED_NOW); rtl=REUSED_ACCEPTED_RTL; unit=EXHAUSTIVE_EQUIVALENT; dependency=PASS; matrix=PASS; library=VERIFIED_REFRESH
  - executed vectors/shards: 5760/4; shard seconds: [1.436, 1.418, 0.021, 0.014]; domain_proof_complete=True; formal=NOT_APPLICABLE/False; strategy=qp_table
  - matrix modes: {"C_ONLY": "PASS", "RTL_RETURN": "PASS", "SHADOW": "PASS"}
  - dependency evidence: {"call_sites": 2, "compile_commands": true, "direct_call_sites": 2, "matrix_commands": true, "vectors": true}
- quantizeresidual: PASS (EXECUTED_NOW); rtl=REUSED_ACCEPTED_RTL; unit=EXHAUSTIVE_EQUIVALENT; dependency=PASS; matrix=PASS; library=VERIFIED_REFRESH
  - executed vectors/shards: 2228207/4; shard seconds: [1.459, 1.571, 0.84, 0.854]; domain_proof_complete=True; formal=NOT_APPLICABLE/False; strategy=cartesian
  - matrix modes: {"C_ONLY": "PASS", "RTL_RETURN": "PASS", "SHADOW": "PASS"}
  - dependency evidence: {"call_sites": 3, "compile_commands": true, "direct_call_sites": 3, "matrix_commands": true, "vectors": true}
- samplepredict: PASS (EXECUTED_NOW); rtl=REUSED_ACCEPTED_RTL; unit=FORMAL_EQUIVALENT; dependency=PASS; matrix=PASS; library=VERIFIED_REFRESH
  - executed vectors/shards: 25960080/4; shard seconds: [23.058, 23.306, 22.552, 22.411]; domain_proof_complete=False; formal=PASS/True; strategy=windowed_boundary
  - matrix modes: {"C_ONLY": "PASS", "RTL_RETURN": "PASS", "SHADOW": "PASS"}
  - dependency evidence: {"call_sites": 5, "compile_commands": true, "direct_call_sites": 5, "matrix_commands": true, "vectors": true}
- samptolinebuf: PASS (EXECUTED_NOW); rtl=REUSED_ACCEPTED_RTL; unit=EXHAUSTIVE_EQUIVALENT; dependency=PASS; matrix=PASS; library=VERIFIED_REFRESH
  - executed vectors/shards: 21233664/4; shard seconds: [8.789, 8.897, 8.361, 8.159]; domain_proof_complete=True; formal=NOT_APPLICABLE/False; strategy=cartesian
  - matrix modes: {"C_ONLY": "PASS", "RTL_RETURN": "PASS", "SHADOW": "PASS"}
  - dependency evidence: {"call_sites": 2, "compile_commands": true, "direct_call_sites": 2, "matrix_commands": true, "vectors": true}
- usingmidpoint: PASS (EXECUTED_NOW); rtl=REUSED_ACCEPTED_RTL; unit=FORMAL_EQUIVALENT; dependency=PASS; matrix=PASS; library=VERIFIED_REFRESH
  - executed vectors/shards: 385344/4; shard seconds: [1.089, 1.013, 0.256, 0.309]; domain_proof_complete=False; formal=PASS/True; strategy=using_midpoint
  - matrix modes: {"C_ONLY": "PASS", "RTL_RETURN": "PASS", "SHADOW": "PASS"}
  - dependency evidence: {"call_sites": 1, "compile_commands": true, "direct_call_sites": 1, "matrix_commands": true, "vectors": true}

## Blockers

- ichdecision: human_promotion_approval_pending
- ichdecision: human_promotion_approval_required
