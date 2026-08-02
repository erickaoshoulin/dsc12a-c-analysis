# Executable generic C-to-RTL pipeline

This report is produced from the current run receipts. The PDF and immutable C model remain external inputs.

- PDF: /Users/snow/Desktop/Display Stream Compression (DSC)/DSC 1.2a/DSC_v1.2a.pdf (724c0979b0a04bb9a5ad7143755bf6fab4bf8cf9598d24a536a5048a66e2aecd)
- C source root: /Users/snow/Desktop/Display Stream Compression (DSC)/DSC 1.2a/DSC_model_20210623 (1cd2ac33e983d1489b2fcc5e138324efba18069db5a6bbe72f6cce3b7d8b9cdf)
- selected contracts: ceil_log2, escapecodesize, findmidpoint, findresidualsize, getqpadjpredsize, isflatnessinfosent, mapqptoqlevel, maxresidualsize, predictsize, quantizeresidual, samplepredict, samptolinebuf
- selected new work: none
- generator invocations: 12
- model calls: 12
- token count: 39644
- dependency pair: {"call_sites": [{"callee_contract": "ceil_log2", "callee_function": "ceil_log2", "callee_usr": "c:@F@ceil_log2", "caller_contract": null, "caller_function": "IchDecision", "caller_usr": "c:@F@IchDecision", "location": {"column": 21, "file": "dsc_codec.c", "line": 513}, "source": "facts/callgraph.json"}, {"callee_contract": "ceil_log2", "callee_function": "ceil_log2", "callee_usr": "c:@F@ceil_log2", "caller_contract": null, "caller_function": "IchDecision", "caller_usr": "c:@F@IchDecision", "location": {"column": 23, "file": "dsc_codec.c", "line": 514}, "source": "facts/callgraph.json"}], "callee_contract": "ceil_log2", "callee_function": "ceil_log2", "callee_usr": "c:@F@ceil_log2", "caller_contract": null, "caller_function": "IchDecision", "caller_usr": "c:@F@IchDecision", "selection_basis": "smallest acyclic direct call site from facts/callgraph.json"}
- baseline scripts discovered: 22

## Results

- ceil_log2: PROMOTED (EXECUTED_NOW); unit=EXHAUSTIVE_EQUIVALENT; dependency=PASS; matrix=PASS; library=PASS
  - executed vectors/shards: 65536/8; shard seconds: [1.98, 1.853, 1.904, 1.883, 1.865, 2.014, 1.861, 1.866]; domain_proof_complete=True; formal=NOT_APPLICABLE/False; strategy=cartesian
  - matrix modes: {"C_ONLY": "PASS", "RTL_RETURN": "PASS", "SHADOW": "PASS"}
  - dependency evidence: {"call_sites": 2, "compile_commands": true, "direct_call_sites": 2, "matrix_commands": true, "vectors": true}
  - rejected candidate_02: unit=FAIL; bitstream=FAIL; receipt=artifacts/aa7d7eefb3fad458001508932987614cc5ab43a10476ef5a987c769eeebf7896/rejected/candidate_02/rejection-receipt.json
- escapecodesize: PROMOTED (EXECUTED_NOW); unit=EXHAUSTIVE_EQUIVALENT; dependency=PASS; matrix=PASS; library=PASS
  - executed vectors/shards: 16320/8; shard seconds: [0.845, 0.83, 0.822, 0.813, 0.83, 0.814, 0.797, 0.829]; domain_proof_complete=True; formal=NOT_APPLICABLE/False; strategy=cartesian
  - matrix modes: {"C_ONLY": "PASS", "RTL_RETURN": "PASS", "SHADOW": "PASS"}
  - dependency evidence: {"call_sites": 2, "compile_commands": true, "direct_call_sites": 2, "matrix_commands": true, "vectors": true}
  - rejected candidate_02: unit=FAIL; bitstream=FAIL; receipt=artifacts/919d079c4ab2b01d886ad37974c76bdb2c104f3d7457219c8520735c4dab47d1/rejected/candidate_02/rejection-receipt.json
- findmidpoint: PROMOTED (EXECUTED_NOW); unit=EXHAUSTIVE_EQUIVALENT; dependency=PASS; matrix=PASS; library=PASS
  - executed vectors/shards: 8207360/8; shard seconds: [5.066, 5.792, 5.681, 5.397, 5.519, 5.621, 5.404, 5.675]; domain_proof_complete=True; formal=NOT_APPLICABLE/False; strategy=conditional
  - matrix modes: {"C_ONLY": "PASS", "RTL_RETURN": "PASS", "SHADOW": "PASS"}
  - dependency evidence: {"call_sites": 3, "compile_commands": true, "direct_call_sites": 3, "matrix_commands": true, "vectors": true}
  - rejected candidate_02: unit=FAIL; bitstream=FAIL; receipt=artifacts/b73ae28f057ca94e607e12a999acef29d76ecb5a69c7015b1eb1cf800f405632/rejected/candidate_02/rejection-receipt.json
- findresidualsize: PROMOTED (EXECUTED_NOW); unit=EXHAUSTIVE_EQUIVALENT; dependency=PASS; matrix=PASS; library=PASS
  - executed vectors/shards: 131071/8; shard seconds: [1.965, 2.041, 1.907, 1.882, 1.877, 1.894, 1.831, 1.824]; domain_proof_complete=True; formal=NOT_APPLICABLE/False; strategy=cartesian
  - matrix modes: {"C_ONLY": "PASS", "RTL_RETURN": "PASS", "SHADOW": "PASS"}
  - dependency evidence: {"call_sites": 6, "compile_commands": true, "direct_call_sites": 6, "matrix_commands": true, "vectors": true}
  - rejected candidate_02: unit=FAIL; bitstream=FAIL; receipt=artifacts/38ec41d9edb5f8fa1f125a2b86dba9193ce6ae29154c24cdaf3ddaf981fa856b/rejected/candidate_02/rejection-receipt.json
- getqpadjpredsize: PROMOTED (EXECUTED_NOW); unit=EXHAUSTIVE_EQUIVALENT; dependency=PASS; matrix=PASS; library=PASS
  - executed vectors/shards: 14831616/8; shard seconds: [5.314, 5.613, 5.007, 5.649, 5.62, 5.143, 5.571, 5.659]; domain_proof_complete=True; formal=NOT_APPLICABLE/False; strategy=table_lookup
  - matrix modes: {"C_ONLY": "PASS", "RTL_RETURN": "PASS", "SHADOW": "PASS"}
  - dependency evidence: {"call_sites": 3, "compile_commands": true, "direct_call_sites": 3, "matrix_commands": true, "vectors": true}
  - rejected candidate_02: unit=FAIL; bitstream=FAIL; receipt=artifacts/dcab7637a1a2c69f878a404a3ca7a732ca495dc0b8c7d4525100d99b4b593e7c/rejected/candidate_02/rejection-receipt.json
- isflatnessinfosent: PROMOTED (EXECUTED_NOW); unit=EXHAUSTIVE_EQUIVALENT; dependency=PASS; matrix=PASS; library=PASS
  - executed vectors/shards: 32768/8; shard seconds: [1.119, 1.186, 1.093, 1.101, 1.124, 1.07, 1.065, 1.103]; domain_proof_complete=True; formal=NOT_APPLICABLE/False; strategy=cartesian
  - matrix modes: {"C_ONLY": "PASS", "RTL_RETURN": "PASS", "SHADOW": "PASS"}
  - dependency evidence: {"call_sites": 4, "compile_commands": true, "direct_call_sites": 4, "matrix_commands": true, "vectors": true}
  - rejected candidate_02: unit=FAIL; bitstream=FAIL; receipt=artifacts/bf7447eb0d360538c6dffdacf94982d7b1671af91edb93db9435bc43f539818d/rejected/candidate_02/rejection-receipt.json
- mapqptoqlevel: PROMOTED (EXECUTED_NOW); unit=EXHAUSTIVE_EQUIVALENT; dependency=PASS; matrix=PASS; library=PASS
  - executed vectors/shards: 5548800/8; shard seconds: [2.388, 2.17, 2.438, 2.417, 2.149, 2.294, 2.04, 2.174]; domain_proof_complete=True; formal=NOT_APPLICABLE/False; strategy=cartesian
  - matrix modes: {"C_ONLY": "PASS", "RTL_RETURN": "PASS", "SHADOW": "PASS"}
  - dependency evidence: {"call_sites": 12, "compile_commands": true, "direct_call_sites": 12, "matrix_commands": true, "vectors": true}
  - rejected candidate_02: unit=FAIL; bitstream=FAIL; receipt=artifacts/ac022d1dc609d17daa512d4e387a221dfa8c2d16311e526c36e7bb40445d2371/rejected/candidate_02/rejection-receipt.json
- maxresidualsize: PROMOTED (EXECUTED_NOW); unit=EXHAUSTIVE_EQUIVALENT; dependency=PASS; matrix=PASS; library=PASS
  - executed vectors/shards: 27744000/8; shard seconds: [8.675, 9.473, 9.379, 9.612, 9.352, 9.192, 8.591, 9.561]; domain_proof_complete=True; formal=NOT_APPLICABLE/False; strategy=cartesian
  - matrix modes: {"C_ONLY": "PASS", "RTL_RETURN": "PASS", "SHADOW": "PASS"}
  - dependency evidence: {"call_sites": 8, "compile_commands": true, "direct_call_sites": 8, "matrix_commands": true, "vectors": true}
  - rejected candidate_02: unit=FAIL; bitstream=FAIL; receipt=artifacts/1ba06acae8e3adf593df5fd4ed3f54a56c531c75a512e3e7564af9e8cf552b2c/rejected/candidate_02/rejection-receipt.json
- predictsize: PROMOTED (EXECUTED_NOW); unit=EXHAUSTIVE_EQUIVALENT; dependency=PASS; matrix=PASS; library=PASS
  - executed vectors/shards: 4913/8; shard seconds: [2.019, 2.133, 1.991, 1.991, 2.093, 1.996, 2.08, 1.949]; domain_proof_complete=True; formal=NOT_APPLICABLE/False; strategy=cartesian
  - matrix modes: {"C_ONLY": "PASS", "RTL_RETURN": "PASS", "SHADOW": "PASS"}
  - dependency evidence: {"call_sites": 2, "compile_commands": true, "direct_call_sites": 2, "matrix_commands": true, "vectors": true}
  - rejected candidate_02: unit=FAIL; bitstream=FAIL; receipt=artifacts/19a8feb4db7de6eca3d912962cb93f776c85cc04cb99ee509ad8151adec2fe4d/rejected/candidate_02/rejection-receipt.json
- quantizeresidual: PROMOTED (EXECUTED_NOW); unit=EXHAUSTIVE_EQUIVALENT; dependency=PASS; matrix=PASS; library=PASS
  - executed vectors/shards: 2228207/8; shard seconds: [1.933, 1.868, 1.686, 1.532, 1.651, 1.637, 1.499, 1.654]; domain_proof_complete=True; formal=NOT_APPLICABLE/False; strategy=cartesian
  - matrix modes: {"C_ONLY": "PASS", "RTL_RETURN": "PASS", "SHADOW": "PASS"}
  - dependency evidence: {"call_sites": 3, "compile_commands": true, "direct_call_sites": 3, "matrix_commands": true, "vectors": true}
  - rejected candidate_02: unit=FAIL; bitstream=FAIL; receipt=artifacts/fdd965df16f8ed6aab36d5bec2aa7f9e252ff7fcab4c5b51a3308ae106af7d0a/rejected/candidate_02/rejection-receipt.json
- samplepredict: PROMOTED (EXECUTED_NOW); unit=FORMAL_EQUIVALENT; dependency=PASS; matrix=PASS; library=PASS
  - executed vectors/shards: 25960080/8; shard seconds: [18.096, 18.006, 17.107, 17.943, 17.815, 17.869, 17.757, 17.567]; domain_proof_complete=False; formal=PASS/True; strategy=windowed_boundary
  - matrix modes: {"C_ONLY": "PASS", "RTL_RETURN": "PASS", "SHADOW": "PASS"}
  - dependency evidence: {"call_sites": 5, "compile_commands": true, "direct_call_sites": 5, "matrix_commands": true, "vectors": true}
  - rejected candidate_02: unit=FAIL; bitstream=FAIL; receipt=artifacts/66e5309e5cf66c9b07022c746307cf37fecbccfa92d7c8ff549ed8b0cbb69509/rejected/candidate_02/rejection-receipt.json
- samptolinebuf: PROMOTED (EXECUTED_NOW); unit=EXHAUSTIVE_EQUIVALENT; dependency=PASS; matrix=PASS; library=PASS
  - executed vectors/shards: 21233664/8; shard seconds: [8.231, 8.698, 8.89, 8.587, 8.172, 8.319, 8.815, 8.614]; domain_proof_complete=True; formal=NOT_APPLICABLE/False; strategy=cartesian
  - matrix modes: {"C_ONLY": "PASS", "RTL_RETURN": "PASS", "SHADOW": "PASS"}
  - dependency evidence: {"call_sites": 2, "compile_commands": true, "direct_call_sites": 2, "matrix_commands": true, "vectors": true}
  - rejected candidate_02: unit=FAIL; bitstream=FAIL; receipt=artifacts/cfd1b515d7114e627f43d8306df877d2c0010024613afccddb7263203e02215a/rejected/candidate_02/rejection-receipt.json

## Blockers

- none
