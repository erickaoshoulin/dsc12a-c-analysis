# Executable generic C-to-RTL pipeline

This report is produced from the current run receipts. The PDF and immutable C model remain external inputs.

- PDF: /Users/snow/Desktop/Display Stream Compression (DSC)/DSC 1.2a/DSC_v1.2a.pdf (724c0979b0a04bb9a5ad7143755bf6fab4bf8cf9598d24a536a5048a66e2aecd)
- C source root: /Users/snow/Desktop/Display Stream Compression (DSC)/DSC 1.2a/DSC_model_20210623 (1cd2ac33e983d1489b2fcc5e138324efba18069db5a6bbe72f6cce3b7d8b9cdf)
- selected contracts: ceil_log2, escapecodesize, findmidpoint, findresidualsize, getqpadjpredsize, isflatnessinfosent, isorigflathindex, mapqptoqlevel, maxresidualsize, predictsize, qp2qlevel, quantizeresidual, samplepredict, samptolinebuf
- selected new work: none
- generator invocations: 14
- model calls: 14
- token count: 67301
- dependency pair: {"call_sites": [{"callee_contract": "ceil_log2", "callee_function": "ceil_log2", "callee_usr": "c:@F@ceil_log2", "caller_contract": null, "caller_function": "IchDecision", "caller_usr": "c:@F@IchDecision", "location": {"column": 21, "file": "dsc_codec.c", "line": 513}, "source": "facts/callgraph.json"}, {"callee_contract": "ceil_log2", "callee_function": "ceil_log2", "callee_usr": "c:@F@ceil_log2", "caller_contract": null, "caller_function": "IchDecision", "caller_usr": "c:@F@IchDecision", "location": {"column": 23, "file": "dsc_codec.c", "line": 514}, "source": "facts/callgraph.json"}], "callee_contract": "ceil_log2", "callee_function": "ceil_log2", "callee_usr": "c:@F@ceil_log2", "caller_contract": null, "caller_function": "IchDecision", "caller_usr": "c:@F@IchDecision", "selection_basis": "smallest acyclic direct call site from facts/callgraph.json"}
- baseline scripts discovered: 22

## Results

- ceil_log2: PROMOTED (EXECUTED_NOW); unit=EXHAUSTIVE_EQUIVALENT; dependency=PASS; matrix=PASS; library=PASS
  - executed vectors/shards: 65536/8; shard seconds: [2.354, 2.284, 2.241, 2.153, 2.049, 1.949, 1.866, 1.801]; domain_proof_complete=True; formal=NOT_APPLICABLE/False; strategy=cartesian
  - matrix modes: {"C_ONLY": "PASS", "RTL_RETURN": "PASS", "SHADOW": "PASS"}
  - dependency evidence: {"call_sites": 2, "compile_commands": true, "direct_call_sites": 2, "matrix_commands": true, "vectors": true}
  - rejected candidate_02: unit=FAIL; bitstream=FAIL; receipt=artifacts/aa7d7eefb3fad458001508932987614cc5ab43a10476ef5a987c769eeebf7896/rejected/candidate_02/rejection-receipt.json
- escapecodesize: PROMOTED (EXECUTED_NOW); unit=EXHAUSTIVE_EQUIVALENT; dependency=PASS; matrix=PASS; library=PASS
  - executed vectors/shards: 16320/8; shard seconds: [0.859, 0.842, 0.822, 0.837, 0.81, 0.792, 0.815, 0.765]; domain_proof_complete=True; formal=NOT_APPLICABLE/False; strategy=cartesian
  - matrix modes: {"C_ONLY": "PASS", "RTL_RETURN": "PASS", "SHADOW": "PASS"}
  - dependency evidence: {"call_sites": 2, "compile_commands": true, "direct_call_sites": 2, "matrix_commands": true, "vectors": true}
  - rejected candidate_02: unit=FAIL; bitstream=FAIL; receipt=artifacts/919d079c4ab2b01d886ad37974c76bdb2c104f3d7457219c8520735c4dab47d1/rejected/candidate_02/rejection-receipt.json
- findmidpoint: PROMOTED (EXECUTED_NOW); unit=EXHAUSTIVE_EQUIVALENT; dependency=PASS; matrix=PASS; library=PASS
  - executed vectors/shards: 8207360/8; shard seconds: [5.758, 5.738, 5.597, 5.354, 5.809, 5.902, 5.848, 5.917]; domain_proof_complete=True; formal=NOT_APPLICABLE/False; strategy=conditional
  - matrix modes: {"C_ONLY": "PASS", "RTL_RETURN": "PASS", "SHADOW": "PASS"}
  - dependency evidence: {"call_sites": 3, "compile_commands": true, "direct_call_sites": 3, "matrix_commands": true, "vectors": true}
  - rejected candidate_02: unit=FAIL; bitstream=FAIL; receipt=artifacts/b73ae28f057ca94e607e12a999acef29d76ecb5a69c7015b1eb1cf800f405632/rejected/candidate_02/rejection-receipt.json
- findresidualsize: PROMOTED (EXECUTED_NOW); unit=EXHAUSTIVE_EQUIVALENT; dependency=PASS; matrix=PASS; library=PASS
  - executed vectors/shards: 131071/8; shard seconds: [2.934, 2.9, 2.789, 2.727, 2.545, 2.514, 2.423, 2.37]; domain_proof_complete=True; formal=NOT_APPLICABLE/False; strategy=cartesian
  - matrix modes: {"C_ONLY": "PASS", "RTL_RETURN": "PASS", "SHADOW": "PASS"}
  - dependency evidence: {"call_sites": 6, "compile_commands": true, "direct_call_sites": 6, "matrix_commands": true, "vectors": true}
  - rejected candidate_02: unit=FAIL; bitstream=FAIL; receipt=artifacts/38ec41d9edb5f8fa1f125a2b86dba9193ce6ae29154c24cdaf3ddaf981fa856b/rejected/candidate_02/rejection-receipt.json
- getqpadjpredsize: PROMOTED (EXECUTED_NOW); unit=EXHAUSTIVE_EQUIVALENT; dependency=PASS; matrix=PASS; library=PASS
  - executed vectors/shards: 14831616/8; shard seconds: [5.568, 5.322, 5.633, 5.272, 5.665, 5.614, 5.446, 5.697]; domain_proof_complete=True; formal=NOT_APPLICABLE/False; strategy=table_lookup
  - matrix modes: {"C_ONLY": "PASS", "RTL_RETURN": "PASS", "SHADOW": "PASS"}
  - dependency evidence: {"call_sites": 3, "compile_commands": true, "direct_call_sites": 3, "matrix_commands": true, "vectors": true}
  - rejected candidate_02: unit=FAIL; bitstream=FAIL; receipt=artifacts/dcab7637a1a2c69f878a404a3ca7a732ca495dc0b8c7d4525100d99b4b593e7c/rejected/candidate_02/rejection-receipt.json
- isflatnessinfosent: PROMOTED (EXECUTED_NOW); unit=EXHAUSTIVE_EQUIVALENT; dependency=PASS; matrix=PASS; library=PASS
  - executed vectors/shards: 32768/8; shard seconds: [2.591, 2.547, 2.408, 2.359, 2.29, 2.191, 2.153, 2.048]; domain_proof_complete=True; formal=NOT_APPLICABLE/False; strategy=cartesian
  - matrix modes: {"C_ONLY": "PASS", "RTL_RETURN": "PASS", "SHADOW": "PASS"}
  - dependency evidence: {"call_sites": 4, "compile_commands": true, "direct_call_sites": 4, "matrix_commands": true, "vectors": true}
  - rejected candidate_02: unit=FAIL; bitstream=FAIL; receipt=artifacts/bf7447eb0d360538c6dffdacf94982d7b1671af91edb93db9435bc43f539818d/rejected/candidate_02/rejection-receipt.json
- isorigflathindex: PROMOTED (EXECUTED_NOW); unit=FORMAL_EQUIVALENT; dependency=PASS; matrix=PASS; library=PASS
  - executed vectors/shards: 575552/8; shard seconds: [1.185, 1.178, 1.117, 1.121, 1.113, 1.095, 1.154, 1.153]; domain_proof_complete=False; formal=PASS/True; strategy=flatness_window
  - matrix modes: {"C_ONLY": "PASS", "RTL_RETURN": "PASS", "SHADOW": "PASS"}
  - dependency evidence: {"call_sites": 2, "compile_commands": true, "direct_call_sites": 2, "matrix_commands": true, "vectors": true}
  - rejected candidate_02: unit=FAIL; bitstream=FAIL; receipt=artifacts/ede1a64844ae2271851a9b28a12aa879360255ea68f5e98ffacb1a12b1ba8115/rejected/candidate_02/rejection-receipt.json
- mapqptoqlevel: PROMOTED (EXECUTED_NOW); unit=EXHAUSTIVE_EQUIVALENT; dependency=PASS; matrix=PASS; library=PASS
  - executed vectors/shards: 5548800/8; shard seconds: [3.608, 4.035, 3.739, 3.338, 4.109, 4.154, 4.068, 4.043]; domain_proof_complete=True; formal=NOT_APPLICABLE/False; strategy=cartesian
  - matrix modes: {"C_ONLY": "PASS", "RTL_RETURN": "PASS", "SHADOW": "PASS"}
  - dependency evidence: {"call_sites": 12, "compile_commands": true, "direct_call_sites": 12, "matrix_commands": true, "vectors": true}
  - rejected candidate_02: unit=FAIL; bitstream=FAIL; receipt=artifacts/ac022d1dc609d17daa512d4e387a221dfa8c2d16311e526c36e7bb40445d2371/rejected/candidate_02/rejection-receipt.json
- maxresidualsize: PROMOTED (EXECUTED_NOW); unit=EXHAUSTIVE_EQUIVALENT; dependency=PASS; matrix=PASS; library=PASS
  - executed vectors/shards: 27744000/8; shard seconds: [10.449, 10.618, 10.258, 9.997, 10.477, 10.717, 10.667, 9.796]; domain_proof_complete=True; formal=NOT_APPLICABLE/False; strategy=cartesian
  - matrix modes: {"C_ONLY": "PASS", "RTL_RETURN": "PASS", "SHADOW": "PASS"}
  - dependency evidence: {"call_sites": 8, "compile_commands": true, "direct_call_sites": 8, "matrix_commands": true, "vectors": true}
  - rejected candidate_02: unit=FAIL; bitstream=FAIL; receipt=artifacts/1ba06acae8e3adf593df5fd4ed3f54a56c531c75a512e3e7564af9e8cf552b2c/rejected/candidate_02/rejection-receipt.json
- predictsize: PROMOTED (EXECUTED_NOW); unit=EXHAUSTIVE_EQUIVALENT; dependency=PASS; matrix=PASS; library=PASS
  - executed vectors/shards: 4913/8; shard seconds: [2.089, 2.155, 2.111, 2.105, 2.04, 1.968, 1.847, 1.793]; domain_proof_complete=True; formal=NOT_APPLICABLE/False; strategy=cartesian
  - matrix modes: {"C_ONLY": "PASS", "RTL_RETURN": "PASS", "SHADOW": "PASS"}
  - dependency evidence: {"call_sites": 2, "compile_commands": true, "direct_call_sites": 2, "matrix_commands": true, "vectors": true}
  - rejected candidate_02: unit=FAIL; bitstream=FAIL; receipt=artifacts/19a8feb4db7de6eca3d912962cb93f776c85cc04cb99ee509ad8151adec2fe4d/rejected/candidate_02/rejection-receipt.json
- qp2qlevel: PROMOTED (EXECUTED_NOW); unit=EXHAUSTIVE_EQUIVALENT; dependency=PASS; matrix=PASS; library=PASS
  - executed vectors/shards: 5760/8; shard seconds: [3.001, 2.933, 2.872, 2.738, 2.697, 2.627, 2.574, 2.58]; domain_proof_complete=True; formal=NOT_APPLICABLE/False; strategy=qp_table
  - matrix modes: {"C_ONLY": "PASS", "RTL_RETURN": "PASS", "SHADOW": "PASS"}
  - dependency evidence: {"call_sites": 2, "compile_commands": true, "direct_call_sites": 2, "matrix_commands": true, "vectors": true}
  - rejected candidate_02: unit=FAIL; bitstream=FAIL; receipt=artifacts/ac55b700324881611f728c9419b69341ef1592de9753de719c3a3109d0c3d026/rejected/candidate_02/rejection-receipt.json
- quantizeresidual: PROMOTED (EXECUTED_NOW); unit=EXHAUSTIVE_EQUIVALENT; dependency=PASS; matrix=PASS; library=PASS
  - executed vectors/shards: 2228207/8; shard seconds: [1.765, 1.635, 1.524, 1.796, 1.707, 1.8, 1.768, 1.72]; domain_proof_complete=True; formal=NOT_APPLICABLE/False; strategy=cartesian
  - matrix modes: {"C_ONLY": "PASS", "RTL_RETURN": "PASS", "SHADOW": "PASS"}
  - dependency evidence: {"call_sites": 3, "compile_commands": true, "direct_call_sites": 3, "matrix_commands": true, "vectors": true}
  - rejected candidate_02: unit=FAIL; bitstream=FAIL; receipt=artifacts/fdd965df16f8ed6aab36d5bec2aa7f9e252ff7fcab4c5b51a3308ae106af7d0a/rejected/candidate_02/rejection-receipt.json
- samplepredict: PROMOTED (EXECUTED_NOW); unit=FORMAL_EQUIVALENT; dependency=PASS; matrix=PASS; library=PASS
  - executed vectors/shards: 25960080/8; shard seconds: [18.033, 18.162, 18.219, 17.901, 16.78, 17.668, 17.966, 17.768]; domain_proof_complete=False; formal=PASS/True; strategy=windowed_boundary
  - matrix modes: {"C_ONLY": "PASS", "RTL_RETURN": "PASS", "SHADOW": "PASS"}
  - dependency evidence: {"call_sites": 5, "compile_commands": true, "direct_call_sites": 5, "matrix_commands": true, "vectors": true}
  - rejected candidate_02: unit=FAIL; bitstream=FAIL; receipt=artifacts/66e5309e5cf66c9b07022c746307cf37fecbccfa92d7c8ff549ed8b0cbb69509/rejected/candidate_02/rejection-receipt.json
- samptolinebuf: PROMOTED (EXECUTED_NOW); unit=EXHAUSTIVE_EQUIVALENT; dependency=PASS; matrix=PASS; library=PASS
  - executed vectors/shards: 21233664/8; shard seconds: [9.446, 9.584, 9.515, 8.749, 9.274, 9.124, 9.315, 8.604]; domain_proof_complete=True; formal=NOT_APPLICABLE/False; strategy=cartesian
  - matrix modes: {"C_ONLY": "PASS", "RTL_RETURN": "PASS", "SHADOW": "PASS"}
  - dependency evidence: {"call_sites": 2, "compile_commands": true, "direct_call_sites": 2, "matrix_commands": true, "vectors": true}
  - rejected candidate_02: unit=FAIL; bitstream=FAIL; receipt=artifacts/cfd1b515d7114e627f43d8306df877d2c0010024613afccddb7263203e02215a/rejected/candidate_02/rejection-receipt.json

## Blockers

- none
