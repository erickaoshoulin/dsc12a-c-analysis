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
- matrix scope: all
- baseline scripts discovered: 22

## Results

- ceil_log2: PASS (EXECUTED_NOW); rtl=REUSED_ACCEPTED_RTL; unit=EXHAUSTIVE_EQUIVALENT; dependency=PASS; matrix=PASS; library=VERIFIED_REFRESH
  - executed vectors/shards: 65536/8; shard seconds: [1.394, 1.437, 1.438, 1.436, 1.392, 1.382, 1.317, 1.348]; domain_proof_complete=True; formal=NOT_APPLICABLE/False; strategy=cartesian
  - matrix modes: {"C_ONLY": "PASS", "RTL_RETURN": "PASS", "SHADOW": "PASS"}
  - dependency evidence: {"call_sites": 2, "compile_commands": true, "direct_call_sites": 2, "matrix_commands": true, "vectors": true}
- escapecodesize: PASS (EXECUTED_NOW); rtl=REUSED_ACCEPTED_RTL; unit=EXHAUSTIVE_EQUIVALENT; dependency=PASS; matrix=PASS; library=VERIFIED_REFRESH
  - executed vectors/shards: 16320/8; shard seconds: [0.826, 0.897, 0.88, 0.896, 0.926, 0.872, 0.872, 0.787]; domain_proof_complete=True; formal=NOT_APPLICABLE/False; strategy=cartesian
  - matrix modes: {"C_ONLY": "PASS", "RTL_RETURN": "PASS", "SHADOW": "PASS"}
  - dependency evidence: {"call_sites": 2, "compile_commands": true, "direct_call_sites": 2, "matrix_commands": true, "vectors": true}
- estimatebitsforgroup: PASS (EXECUTED_NOW); rtl=REUSED_ACCEPTED_RTL; unit=FORMAL_EQUIVALENT; dependency=PASS; matrix=PASS; library=VERIFIED_REFRESH
  - executed vectors/shards: 1040928/8; shard seconds: [1.353, 1.283, 1.319, 1.374, 1.328, 1.302, 1.334, 1.359]; domain_proof_complete=False; formal=PASS/True; strategy=estimate_bits
  - matrix modes: {"C_ONLY": "PASS", "RTL_RETURN": "PASS", "SHADOW": "PASS"}
  - dependency evidence: {"call_sites": 1, "compile_commands": true, "direct_call_sites": 1, "matrix_commands": true, "vectors": true}
- findmidpoint: PASS (EXECUTED_NOW); rtl=REUSED_ACCEPTED_RTL; unit=EXHAUSTIVE_EQUIVALENT; dependency=PASS; matrix=PASS; library=VERIFIED_REFRESH
  - executed vectors/shards: 8207360/8; shard seconds: [4.677, 4.447, 4.757, 4.627, 4.775, 4.28, 4.595, 4.704]; domain_proof_complete=True; formal=NOT_APPLICABLE/False; strategy=conditional
  - matrix modes: {"C_ONLY": "PASS", "RTL_RETURN": "PASS", "SHADOW": "PASS"}
  - dependency evidence: {"call_sites": 3, "compile_commands": true, "direct_call_sites": 3, "matrix_commands": true, "vectors": true}
- findresidualsize: PASS (EXECUTED_NOW); rtl=REUSED_ACCEPTED_RTL; unit=EXHAUSTIVE_EQUIVALENT; dependency=PASS; matrix=PASS; library=VERIFIED_REFRESH
  - executed vectors/shards: 131071/8; shard seconds: [1.661, 1.651, 1.673, 1.697, 1.657, 1.623, 1.729, 1.605]; domain_proof_complete=True; formal=NOT_APPLICABLE/False; strategy=cartesian
  - matrix modes: {"C_ONLY": "PASS", "RTL_RETURN": "PASS", "SHADOW": "PASS"}
  - dependency evidence: {"call_sites": 6, "compile_commands": true, "direct_call_sites": 6, "matrix_commands": true, "vectors": true}
- getqpadjpredsize: PASS (EXECUTED_NOW); rtl=REUSED_ACCEPTED_RTL; unit=EXHAUSTIVE_EQUIVALENT; dependency=PASS; matrix=PASS; library=VERIFIED_REFRESH
  - executed vectors/shards: 14831616/8; shard seconds: [6.963, 7.165, 7.055, 7.262, 7.231, 7.033, 6.711, 7.202]; domain_proof_complete=True; formal=NOT_APPLICABLE/False; strategy=table_lookup
  - matrix modes: {"C_ONLY": "PASS", "RTL_RETURN": "PASS", "SHADOW": "PASS"}
  - dependency evidence: {"call_sites": 3, "compile_commands": true, "direct_call_sites": 3, "matrix_commands": true, "vectors": true}
- isflatnessinfosent: PASS (EXECUTED_NOW); rtl=REUSED_ACCEPTED_RTL; unit=EXHAUSTIVE_EQUIVALENT; dependency=PASS; matrix=PASS; library=VERIFIED_REFRESH
  - executed vectors/shards: 32768/8; shard seconds: [1.986, 1.957, 2.006, 1.957, 2.012, 1.923, 1.906, 1.888]; domain_proof_complete=True; formal=NOT_APPLICABLE/False; strategy=cartesian
  - matrix modes: {"C_ONLY": "PASS", "RTL_RETURN": "PASS", "SHADOW": "PASS"}
  - dependency evidence: {"call_sites": 4, "compile_commands": true, "direct_call_sites": 4, "matrix_commands": true, "vectors": true}
- isorigflathindex: PASS (EXECUTED_NOW); rtl=REUSED_ACCEPTED_RTL; unit=FORMAL_EQUIVALENT; dependency=PASS; matrix=PASS; library=VERIFIED_REFRESH
  - executed vectors/shards: 575552/8; shard seconds: [1.735, 1.776, 1.769, 1.724, 1.729, 1.693, 1.704, 1.725]; domain_proof_complete=False; formal=PASS/True; strategy=flatness_window
  - matrix modes: {"C_ONLY": "PASS", "RTL_RETURN": "PASS", "SHADOW": "PASS"}
  - dependency evidence: {"call_sites": 2, "compile_commands": true, "direct_call_sites": 2, "matrix_commands": true, "vectors": true}
- mapqptoqlevel: PASS (EXECUTED_NOW); rtl=REUSED_ACCEPTED_RTL; unit=EXHAUSTIVE_EQUIVALENT; dependency=PASS; matrix=PASS; library=VERIFIED_REFRESH
  - executed vectors/shards: 5548800/8; shard seconds: [3.541, 3.726, 3.511, 3.647, 3.259, 3.536, 3.492, 3.693]; domain_proof_complete=True; formal=NOT_APPLICABLE/False; strategy=cartesian
  - matrix modes: {"C_ONLY": "PASS", "RTL_RETURN": "PASS", "SHADOW": "PASS"}
  - dependency evidence: {"call_sites": 12, "compile_commands": true, "direct_call_sites": 12, "matrix_commands": true, "vectors": true}
- maxresidualsize: PASS (EXECUTED_NOW); rtl=REUSED_ACCEPTED_RTL; unit=EXHAUSTIVE_EQUIVALENT; dependency=PASS; matrix=PASS; library=VERIFIED_REFRESH
  - executed vectors/shards: 27744000/8; shard seconds: [17.188, 16.483, 16.332, 17.324, 17.253, 16.881, 17.083, 17.006]; domain_proof_complete=True; formal=NOT_APPLICABLE/False; strategy=cartesian
  - matrix modes: {"C_ONLY": "PASS", "RTL_RETURN": "PASS", "SHADOW": "PASS"}
  - dependency evidence: {"call_sites": 8, "compile_commands": true, "direct_call_sites": 8, "matrix_commands": true, "vectors": true}
- predictsize: PASS (EXECUTED_NOW); rtl=REUSED_ACCEPTED_RTL; unit=EXHAUSTIVE_EQUIVALENT; dependency=PASS; matrix=PASS; library=VERIFIED_REFRESH
  - executed vectors/shards: 4913/8; shard seconds: [1.026, 1.022, 1.034, 1.044, 1.042, 1.065, 1.045, 1.011]; domain_proof_complete=True; formal=NOT_APPLICABLE/False; strategy=cartesian
  - matrix modes: {"C_ONLY": "PASS", "RTL_RETURN": "PASS", "SHADOW": "PASS"}
  - dependency evidence: {"call_sites": 2, "compile_commands": true, "direct_call_sites": 2, "matrix_commands": true, "vectors": true}
- qp2qlevel: PASS (EXECUTED_NOW); rtl=REUSED_ACCEPTED_RTL; unit=EXHAUSTIVE_EQUIVALENT; dependency=PASS; matrix=PASS; library=VERIFIED_REFRESH
  - executed vectors/shards: 5760/8; shard seconds: [0.924, 0.923, 0.895, 0.895, 0.851, 0.787, 0.791, 0.811]; domain_proof_complete=True; formal=NOT_APPLICABLE/False; strategy=qp_table
  - matrix modes: {"C_ONLY": "PASS", "RTL_RETURN": "PASS", "SHADOW": "PASS"}
  - dependency evidence: {"call_sites": 2, "compile_commands": true, "direct_call_sites": 2, "matrix_commands": true, "vectors": true}
- quantizeresidual: PASS (EXECUTED_NOW); rtl=REUSED_ACCEPTED_RTL; unit=EXHAUSTIVE_EQUIVALENT; dependency=PASS; matrix=PASS; library=VERIFIED_REFRESH
  - executed vectors/shards: 2228207/8; shard seconds: [1.675, 1.738, 1.47, 1.653, 1.712, 1.632, 1.574, 1.589]; domain_proof_complete=True; formal=NOT_APPLICABLE/False; strategy=cartesian
  - matrix modes: {"C_ONLY": "PASS", "RTL_RETURN": "PASS", "SHADOW": "PASS"}
  - dependency evidence: {"call_sites": 3, "compile_commands": true, "direct_call_sites": 3, "matrix_commands": true, "vectors": true}
- samplepredict: PASS (EXECUTED_NOW); rtl=REUSED_ACCEPTED_RTL; unit=FORMAL_EQUIVALENT; dependency=PASS; matrix=PASS; library=VERIFIED_REFRESH
  - executed vectors/shards: 25960080/8; shard seconds: [23.57, 23.759, 23.201, 22.855, 23.459, 23.291, 22.999, 23.661]; domain_proof_complete=False; formal=PASS/True; strategy=windowed_boundary
  - matrix modes: {"C_ONLY": "PASS", "RTL_RETURN": "PASS", "SHADOW": "PASS"}
  - dependency evidence: {"call_sites": 5, "compile_commands": true, "direct_call_sites": 5, "matrix_commands": true, "vectors": true}
- samptolinebuf: PASS (EXECUTED_NOW); rtl=REUSED_ACCEPTED_RTL; unit=EXHAUSTIVE_EQUIVALENT; dependency=PASS; matrix=PASS; library=VERIFIED_REFRESH
  - executed vectors/shards: 21233664/8; shard seconds: [10.458, 10.74, 10.894, 10.597, 11.115, 11.216, 10.989, 11.163]; domain_proof_complete=True; formal=NOT_APPLICABLE/False; strategy=cartesian
  - matrix modes: {"C_ONLY": "PASS", "RTL_RETURN": "PASS", "SHADOW": "PASS"}
  - dependency evidence: {"call_sites": 2, "compile_commands": true, "direct_call_sites": 2, "matrix_commands": true, "vectors": true}
- usingmidpoint: PASS (EXECUTED_NOW); rtl=REUSED_ACCEPTED_RTL; unit=FORMAL_EQUIVALENT; dependency=PASS; matrix=PASS; library=VERIFIED_REFRESH
  - executed vectors/shards: 385344/8; shard seconds: [1.036, 0.992, 0.903, 0.891, 0.974, 0.917, 0.874, 0.826]; domain_proof_complete=False; formal=PASS/True; strategy=using_midpoint
  - matrix modes: {"C_ONLY": "PASS", "RTL_RETURN": "PASS", "SHADOW": "PASS"}
  - dependency evidence: {"call_sites": 1, "compile_commands": true, "direct_call_sites": 1, "matrix_commands": true, "vectors": true}

## Blockers

- ichdecision: human_promotion_approval_pending
- ichdecision: human_promotion_approval_required
