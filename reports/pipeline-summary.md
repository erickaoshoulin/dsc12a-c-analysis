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
  - executed vectors/shards: 65536/8; shard seconds: [2.385, 2.339, 2.363, 2.342, 2.332, 2.258, 2.257, 2.192]; domain_proof_complete=True; formal=NOT_APPLICABLE/False; strategy=cartesian
  - matrix modes: {"C_ONLY": "PASS", "RTL_RETURN": "PASS", "SHADOW": "PASS"}
  - dependency evidence: {"call_sites": 2, "compile_commands": true, "direct_call_sites": 2, "matrix_commands": true, "vectors": true}
  - rejected candidate_02: unit=FAIL; bitstream=FAIL; receipt=artifacts/aa7d7eefb3fad458001508932987614cc5ab43a10476ef5a987c769eeebf7896/rejected/candidate_02/rejection-receipt.json
- escapecodesize: PROMOTED (EXECUTED_NOW); unit=EXHAUSTIVE_EQUIVALENT; dependency=PASS; matrix=PASS; library=PASS
  - executed vectors/shards: 16320/8; shard seconds: [0.818, 0.856, 0.877, 0.835, 0.87, 0.859, 0.757, 0.794]; domain_proof_complete=True; formal=NOT_APPLICABLE/False; strategy=cartesian
  - matrix modes: {"C_ONLY": "PASS", "RTL_RETURN": "PASS", "SHADOW": "PASS"}
  - dependency evidence: {"call_sites": 2, "compile_commands": true, "direct_call_sites": 2, "matrix_commands": true, "vectors": true}
  - rejected candidate_02: unit=FAIL; bitstream=FAIL; receipt=artifacts/919d079c4ab2b01d886ad37974c76bdb2c104f3d7457219c8520735c4dab47d1/rejected/candidate_02/rejection-receipt.json
- findmidpoint: PROMOTED (EXECUTED_NOW); unit=EXHAUSTIVE_EQUIVALENT; dependency=PASS; matrix=PASS; library=PASS
  - executed vectors/shards: 8207360/8; shard seconds: [5.506, 5.317, 5.452, 4.257, 5.424, 5.179, 5.397, 5.087]; domain_proof_complete=True; formal=NOT_APPLICABLE/False; strategy=conditional
  - matrix modes: {"C_ONLY": "PASS", "RTL_RETURN": "PASS", "SHADOW": "PASS"}
  - dependency evidence: {"call_sites": 3, "compile_commands": true, "direct_call_sites": 3, "matrix_commands": true, "vectors": true}
  - rejected candidate_02: unit=FAIL; bitstream=FAIL; receipt=artifacts/b73ae28f057ca94e607e12a999acef29d76ecb5a69c7015b1eb1cf800f405632/rejected/candidate_02/rejection-receipt.json
- findresidualsize: PROMOTED (EXECUTED_NOW); unit=EXHAUSTIVE_EQUIVALENT; dependency=PASS; matrix=PASS; library=PASS
  - executed vectors/shards: 131071/8; shard seconds: [2.155, 2.126, 2.131, 2.106, 2.13, 2.112, 2.079, 2.087]; domain_proof_complete=True; formal=NOT_APPLICABLE/False; strategy=cartesian
  - matrix modes: {"C_ONLY": "PASS", "RTL_RETURN": "PASS", "SHADOW": "PASS"}
  - dependency evidence: {"call_sites": 6, "compile_commands": true, "direct_call_sites": 6, "matrix_commands": true, "vectors": true}
  - rejected candidate_02: unit=FAIL; bitstream=FAIL; receipt=artifacts/38ec41d9edb5f8fa1f125a2b86dba9193ce6ae29154c24cdaf3ddaf981fa856b/rejected/candidate_02/rejection-receipt.json
- getqpadjpredsize: PROMOTED (EXECUTED_NOW); unit=EXHAUSTIVE_EQUIVALENT; dependency=PASS; matrix=PASS; library=PASS
  - executed vectors/shards: 14831616/8; shard seconds: [5.621, 5.674, 5.653, 4.918, 5.536, 5.206, 5.093, 5.557]; domain_proof_complete=True; formal=NOT_APPLICABLE/False; strategy=table_lookup
  - matrix modes: {"C_ONLY": "PASS", "RTL_RETURN": "PASS", "SHADOW": "PASS"}
  - dependency evidence: {"call_sites": 3, "compile_commands": true, "direct_call_sites": 3, "matrix_commands": true, "vectors": true}
  - rejected candidate_02: unit=FAIL; bitstream=FAIL; receipt=artifacts/dcab7637a1a2c69f878a404a3ca7a732ca495dc0b8c7d4525100d99b4b593e7c/rejected/candidate_02/rejection-receipt.json
- isflatnessinfosent: PROMOTED (EXECUTED_NOW); unit=EXHAUSTIVE_EQUIVALENT; dependency=PASS; matrix=PASS; library=PASS
  - executed vectors/shards: 32768/8; shard seconds: [2.609, 2.541, 2.537, 2.422, 2.417, 2.327, 2.252, 2.167]; domain_proof_complete=True; formal=NOT_APPLICABLE/False; strategy=cartesian
  - matrix modes: {"C_ONLY": "PASS", "RTL_RETURN": "PASS", "SHADOW": "PASS"}
  - dependency evidence: {"call_sites": 4, "compile_commands": true, "direct_call_sites": 4, "matrix_commands": true, "vectors": true}
  - rejected candidate_02: unit=FAIL; bitstream=FAIL; receipt=artifacts/bf7447eb0d360538c6dffdacf94982d7b1671af91edb93db9435bc43f539818d/rejected/candidate_02/rejection-receipt.json
- isorigflathindex: PROMOTED (EXECUTED_NOW); unit=FORMAL_EQUIVALENT; dependency=PASS; matrix=PASS; library=PASS
  - executed vectors/shards: 575552/8; shard seconds: [1.212, 1.101, 1.098, 1.173, 1.108, 1.154, 1.119, 1.157]; domain_proof_complete=False; formal=PASS/True; strategy=flatness_window
  - matrix modes: {"C_ONLY": "PASS", "RTL_RETURN": "PASS", "SHADOW": "PASS"}
  - dependency evidence: {"call_sites": 2, "compile_commands": true, "direct_call_sites": 2, "matrix_commands": true, "vectors": true}
  - rejected candidate_02: unit=FAIL; bitstream=FAIL; receipt=artifacts/ede1a64844ae2271851a9b28a12aa879360255ea68f5e98ffacb1a12b1ba8115/rejected/candidate_02/rejection-receipt.json
- mapqptoqlevel: PROMOTED (EXECUTED_NOW); unit=EXHAUSTIVE_EQUIVALENT; dependency=PASS; matrix=PASS; library=PASS
  - executed vectors/shards: 5548800/8; shard seconds: [4.362, 3.853, 4.282, 4.059, 4.294, 4.319, 3.519, 3.773]; domain_proof_complete=True; formal=NOT_APPLICABLE/False; strategy=cartesian
  - matrix modes: {"C_ONLY": "PASS", "RTL_RETURN": "PASS", "SHADOW": "PASS"}
  - dependency evidence: {"call_sites": 12, "compile_commands": true, "direct_call_sites": 12, "matrix_commands": true, "vectors": true}
  - rejected candidate_02: unit=FAIL; bitstream=FAIL; receipt=artifacts/ac022d1dc609d17daa512d4e387a221dfa8c2d16311e526c36e7bb40445d2371/rejected/candidate_02/rejection-receipt.json
- maxresidualsize: PROMOTED (EXECUTED_NOW); unit=EXHAUSTIVE_EQUIVALENT; dependency=PASS; matrix=PASS; library=PASS
  - executed vectors/shards: 27744000/8; shard seconds: [8.352, 9.881, 10.257, 10.116, 10.003, 10.29, 9.688, 9.45]; domain_proof_complete=True; formal=NOT_APPLICABLE/False; strategy=cartesian
  - matrix modes: {"C_ONLY": "PASS", "RTL_RETURN": "PASS", "SHADOW": "PASS"}
  - dependency evidence: {"call_sites": 8, "compile_commands": true, "direct_call_sites": 8, "matrix_commands": true, "vectors": true}
  - rejected candidate_02: unit=FAIL; bitstream=FAIL; receipt=artifacts/1ba06acae8e3adf593df5fd4ed3f54a56c531c75a512e3e7564af9e8cf552b2c/rejected/candidate_02/rejection-receipt.json
- predictsize: PROMOTED (EXECUTED_NOW); unit=EXHAUSTIVE_EQUIVALENT; dependency=PASS; matrix=PASS; library=PASS
  - executed vectors/shards: 4913/8; shard seconds: [3.017, 2.953, 2.953, 2.844, 2.722, 2.698, 2.606, 2.569]; domain_proof_complete=True; formal=NOT_APPLICABLE/False; strategy=cartesian
  - matrix modes: {"C_ONLY": "PASS", "RTL_RETURN": "PASS", "SHADOW": "PASS"}
  - dependency evidence: {"call_sites": 2, "compile_commands": true, "direct_call_sites": 2, "matrix_commands": true, "vectors": true}
  - rejected candidate_02: unit=FAIL; bitstream=FAIL; receipt=artifacts/19a8feb4db7de6eca3d912962cb93f776c85cc04cb99ee509ad8151adec2fe4d/rejected/candidate_02/rejection-receipt.json
- qp2qlevel: PROMOTED (EXECUTED_NOW); unit=EXHAUSTIVE_EQUIVALENT; dependency=PASS; matrix=PASS; library=PASS
  - executed vectors/shards: 5760/8; shard seconds: [2.797, 2.677, 2.69, 2.59, 2.367, 2.471, 2.381, 2.341]; domain_proof_complete=True; formal=NOT_APPLICABLE/False; strategy=qp_table
  - matrix modes: {"C_ONLY": "PASS", "RTL_RETURN": "PASS", "SHADOW": "PASS"}
  - dependency evidence: {"call_sites": 2, "compile_commands": true, "direct_call_sites": 2, "matrix_commands": true, "vectors": true}
  - rejected candidate_02: unit=FAIL; bitstream=FAIL; receipt=artifacts/ac55b700324881611f728c9419b69341ef1592de9753de719c3a3109d0c3d026/rejected/candidate_02/rejection-receipt.json
- quantizeresidual: PROMOTED (EXECUTED_NOW); unit=EXHAUSTIVE_EQUIVALENT; dependency=PASS; matrix=PASS; library=PASS
  - executed vectors/shards: 2228207/8; shard seconds: [1.539, 1.573, 1.847, 1.914, 1.506, 1.625, 1.633, 1.596]; domain_proof_complete=True; formal=NOT_APPLICABLE/False; strategy=cartesian
  - matrix modes: {"C_ONLY": "PASS", "RTL_RETURN": "PASS", "SHADOW": "PASS"}
  - dependency evidence: {"call_sites": 3, "compile_commands": true, "direct_call_sites": 3, "matrix_commands": true, "vectors": true}
  - rejected candidate_02: unit=FAIL; bitstream=FAIL; receipt=artifacts/fdd965df16f8ed6aab36d5bec2aa7f9e252ff7fcab4c5b51a3308ae106af7d0a/rejected/candidate_02/rejection-receipt.json
- samplepredict: PROMOTED (EXECUTED_NOW); unit=FORMAL_EQUIVALENT; dependency=PASS; matrix=PASS; library=PASS
  - executed vectors/shards: 25960080/8; shard seconds: [17.494, 17.981, 18.309, 17.896, 18.368, 18.255, 18.188, 17.772]; domain_proof_complete=False; formal=PASS/True; strategy=windowed_boundary
  - matrix modes: {"C_ONLY": "PASS", "RTL_RETURN": "PASS", "SHADOW": "PASS"}
  - dependency evidence: {"call_sites": 5, "compile_commands": true, "direct_call_sites": 5, "matrix_commands": true, "vectors": true}
  - rejected candidate_02: unit=FAIL; bitstream=FAIL; receipt=artifacts/66e5309e5cf66c9b07022c746307cf37fecbccfa92d7c8ff549ed8b0cbb69509/rejected/candidate_02/rejection-receipt.json
- samptolinebuf: PROMOTED (EXECUTED_NOW); unit=EXHAUSTIVE_EQUIVALENT; dependency=PASS; matrix=PASS; library=PASS
  - executed vectors/shards: 21233664/8; shard seconds: [8.925, 9.264, 8.724, 8.806, 9.283, 9.154, 9.067, 8.575]; domain_proof_complete=True; formal=NOT_APPLICABLE/False; strategy=cartesian
  - matrix modes: {"C_ONLY": "PASS", "RTL_RETURN": "PASS", "SHADOW": "PASS"}
  - dependency evidence: {"call_sites": 2, "compile_commands": true, "direct_call_sites": 2, "matrix_commands": true, "vectors": true}
  - rejected candidate_02: unit=FAIL; bitstream=FAIL; receipt=artifacts/cfd1b515d7114e627f43d8306df877d2c0010024613afccddb7263203e02215a/rejected/candidate_02/rejection-receipt.json

## Blockers

- none
