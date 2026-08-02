# Executable generic C-to-RTL pipeline

This report is produced from the current run receipts. The PDF and immutable C model remain external inputs.

- PDF: /Users/snow/Desktop/Display Stream Compression (DSC)/DSC 1.2a/DSC_v1.2a.pdf (724c0979b0a04bb9a5ad7143755bf6fab4bf8cf9598d24a536a5048a66e2aecd)
- C source root: /Users/snow/Desktop/Display Stream Compression (DSC)/DSC 1.2a/DSC_model_20210623 (1cd2ac33e983d1489b2fcc5e138324efba18069db5a6bbe72f6cce3b7d8b9cdf)
- selected contracts: escapecodesize, findmidpoint, getqpadjpredsize, isflatnessinfosent, mapqptoqlevel, maxresidualsize, predictsize, quantizeresidual, samplepredict, samptolinebuf
- selected new work: none
- generator invocations: 10
- model calls: 10
- token count: 36434
- dependency pair: {"call_sites": [{"callee_contract": "escapecodesize", "callee_function": "EscapeCodeSize", "callee_usr": "c:@F@EscapeCodeSize", "caller_contract": null, "caller_function": "VLCUnit", "caller_usr": "c:@F@VLCUnit", "location": {"column": 26, "file": "dsc_codec.c", "line": 1614}, "source": "facts/callgraph.json"}], "callee_contract": "escapecodesize", "callee_function": "EscapeCodeSize", "callee_usr": "c:@F@EscapeCodeSize", "caller_contract": null, "caller_function": "VLCUnit", "caller_usr": "c:@F@VLCUnit", "selection_basis": "smallest acyclic direct call site from facts/callgraph.json"}
- baseline scripts discovered: 22

## Results

- escapecodesize: PROMOTED (EXECUTED_NOW); unit=EXHAUSTIVE_EQUIVALENT; dependency=PASS; matrix=PASS; library=PASS
  - executed vectors/shards: 16320/8; shard seconds: [0.774, 0.775, 0.783, 0.783, 0.774, 0.774, 0.775, 0.78]; domain_proof_complete=True; formal=NOT_APPLICABLE/False; strategy=cartesian
  - matrix modes: {"C_ONLY": "PASS", "RTL_RETURN": "PASS", "SHADOW": "PASS"}
  - dependency evidence: {"call_sites": 2, "compile_commands": true, "direct_call_sites": 2, "matrix_commands": true, "vectors": true}
  - rejected candidate_02: unit=FAIL; bitstream=FAIL; receipt=artifacts/480f0f8595c56a062af62c4eabd3f0adc50bf08788abc6865dd1b1143b61e5f7/rejected/candidate_02/rejection-receipt.json
- findmidpoint: PROMOTED (EXECUTED_NOW); unit=EXHAUSTIVE_EQUIVALENT; dependency=PASS; matrix=PASS; library=PASS
  - executed vectors/shards: 8207360/8; shard seconds: [2.996, 2.565, 3.071, 3.316, 2.788, 3.214, 3.128, 3.103]; domain_proof_complete=True; formal=NOT_APPLICABLE/False; strategy=conditional
  - matrix modes: {"C_ONLY": "PASS", "RTL_RETURN": "PASS", "SHADOW": "PASS"}
  - dependency evidence: {"call_sites": 3, "compile_commands": true, "direct_call_sites": 3, "matrix_commands": true, "vectors": true}
  - rejected candidate_02: unit=FAIL; bitstream=FAIL; receipt=artifacts/b73ae28f057ca94e607e12a999acef29d76ecb5a69c7015b1eb1cf800f405632/rejected/candidate_02/rejection-receipt.json
- getqpadjpredsize: PROMOTED (EXECUTED_NOW); unit=EXHAUSTIVE_EQUIVALENT; dependency=PASS; matrix=PASS; library=PASS
  - executed vectors/shards: 14831616/8; shard seconds: [5.719, 5.631, 5.327, 5.396, 5.443, 5.59, 5.708, 5.766]; domain_proof_complete=True; formal=NOT_APPLICABLE/False; strategy=table_lookup
  - matrix modes: {"C_ONLY": "PASS", "RTL_RETURN": "PASS", "SHADOW": "PASS"}
  - dependency evidence: {"call_sites": 3, "compile_commands": true, "direct_call_sites": 3, "matrix_commands": true, "vectors": true}
  - rejected candidate_02: unit=FAIL; bitstream=FAIL; receipt=artifacts/5f5aca8e104da0024c8af97f48a06bbb5420a37964a8bd9237fb8b005e59d6c1/rejected/candidate_02/rejection-receipt.json
- isflatnessinfosent: PROMOTED (EXECUTED_NOW); unit=EXHAUSTIVE_EQUIVALENT; dependency=PASS; matrix=PASS; library=PASS
  - executed vectors/shards: 32768/8; shard seconds: [1.205, 1.252, 1.046, 1.019, 0.999, 1.023, 0.981, 0.988]; domain_proof_complete=True; formal=NOT_APPLICABLE/False; strategy=cartesian
  - matrix modes: {"C_ONLY": "PASS", "RTL_RETURN": "PASS", "SHADOW": "PASS"}
  - dependency evidence: {"call_sites": 4, "compile_commands": true, "direct_call_sites": 4, "matrix_commands": true, "vectors": true}
  - rejected candidate_02: unit=FAIL; bitstream=FAIL; receipt=artifacts/bf7447eb0d360538c6dffdacf94982d7b1671af91edb93db9435bc43f539818d/rejected/candidate_02/rejection-receipt.json
- mapqptoqlevel: PROMOTED (EXECUTED_NOW); unit=EXHAUSTIVE_EQUIVALENT; dependency=PASS; matrix=PASS; library=PASS
  - executed vectors/shards: 5548800/8; shard seconds: [2.487, 2.615, 2.455, 2.571, 2.618, 2.51, 2.448, 2.556]; domain_proof_complete=True; formal=NOT_APPLICABLE/False; strategy=cartesian
  - matrix modes: {"C_ONLY": "PASS", "RTL_RETURN": "PASS", "SHADOW": "PASS"}
  - dependency evidence: {"call_sites": 12, "compile_commands": true, "direct_call_sites": 12, "matrix_commands": true, "vectors": true}
  - rejected candidate_02: unit=FAIL; bitstream=FAIL; receipt=artifacts/ac022d1dc609d17daa512d4e387a221dfa8c2d16311e526c36e7bb40445d2371/rejected/candidate_02/rejection-receipt.json
- maxresidualsize: PROMOTED (EXECUTED_NOW); unit=EXHAUSTIVE_EQUIVALENT; dependency=PASS; matrix=PASS; library=PASS
  - executed vectors/shards: 27744000/8; shard seconds: [8.762, 9.574, 8.873, 9.54, 9.507, 9.404, 9.149, 9.473]; domain_proof_complete=True; formal=NOT_APPLICABLE/False; strategy=cartesian
  - matrix modes: {"C_ONLY": "PASS", "RTL_RETURN": "PASS", "SHADOW": "PASS"}
  - dependency evidence: {"call_sites": 8, "compile_commands": true, "direct_call_sites": 8, "matrix_commands": true, "vectors": true}
  - rejected candidate_02: unit=FAIL; bitstream=FAIL; receipt=artifacts/068017b8a23d03a9d7d16aac74ab5358cfea6ea0c1d2c2e2dc53361421d7f34d/rejected/candidate_02/rejection-receipt.json
- predictsize: PROMOTED (EXECUTED_NOW); unit=EXHAUSTIVE_EQUIVALENT; dependency=PASS; matrix=PASS; library=PASS
  - executed vectors/shards: 4913/8; shard seconds: [1.065, 0.997, 1.074, 1.116, 1.108, 0.954, 0.914, 0.96]; domain_proof_complete=True; formal=NOT_APPLICABLE/False; strategy=cartesian
  - matrix modes: {"C_ONLY": "PASS", "RTL_RETURN": "PASS", "SHADOW": "PASS"}
  - dependency evidence: {"call_sites": 2, "compile_commands": true, "direct_call_sites": 2, "matrix_commands": true, "vectors": true}
  - rejected candidate_02: unit=FAIL; bitstream=FAIL; receipt=artifacts/19a8feb4db7de6eca3d912962cb93f776c85cc04cb99ee509ad8151adec2fe4d/rejected/candidate_02/rejection-receipt.json
- quantizeresidual: PROMOTED (EXECUTED_NOW); unit=EXHAUSTIVE_EQUIVALENT; dependency=PASS; matrix=PASS; library=PASS
  - executed vectors/shards: 2228207/8; shard seconds: [1.616, 1.802, 1.833, 1.69, 1.759, 1.488, 1.676, 1.511]; domain_proof_complete=True; formal=NOT_APPLICABLE/False; strategy=cartesian
  - matrix modes: {"C_ONLY": "PASS", "RTL_RETURN": "PASS", "SHADOW": "PASS"}
  - dependency evidence: {"call_sites": 3, "compile_commands": true, "direct_call_sites": 3, "matrix_commands": true, "vectors": true}
  - rejected candidate_02: unit=FAIL; bitstream=FAIL; receipt=artifacts/fdd965df16f8ed6aab36d5bec2aa7f9e252ff7fcab4c5b51a3308ae106af7d0a/rejected/candidate_02/rejection-receipt.json
- samplepredict: PROMOTED (EXECUTED_NOW); unit=FORMAL_EQUIVALENT; dependency=PASS; matrix=PASS; library=PASS
  - executed vectors/shards: 25960080/8; shard seconds: [18.007, 17.894, 17.831, 17.524, 17.778, 17.691, 16.274, 17.585]; domain_proof_complete=False; formal=PASS/True; strategy=windowed_boundary
  - matrix modes: {"C_ONLY": "PASS", "RTL_RETURN": "PASS", "SHADOW": "PASS"}
  - dependency evidence: {"call_sites": 5, "compile_commands": true, "direct_call_sites": 5, "matrix_commands": true, "vectors": true}
  - rejected candidate_02: unit=FAIL; bitstream=FAIL; receipt=artifacts/66e5309e5cf66c9b07022c746307cf37fecbccfa92d7c8ff549ed8b0cbb69509/rejected/candidate_02/rejection-receipt.json
- samptolinebuf: PROMOTED (EXECUTED_NOW); unit=EXHAUSTIVE_EQUIVALENT; dependency=PASS; matrix=PASS; library=PASS
  - executed vectors/shards: 21233664/8; shard seconds: [10.877, 10.601, 10.993, 11.054, 10.406, 10.668, 10.738, 9.885]; domain_proof_complete=True; formal=NOT_APPLICABLE/False; strategy=cartesian
  - matrix modes: {"C_ONLY": "PASS", "RTL_RETURN": "PASS", "SHADOW": "PASS"}
  - dependency evidence: {"call_sites": 2, "compile_commands": true, "direct_call_sites": 2, "matrix_commands": true, "vectors": true}
  - rejected candidate_02: unit=FAIL; bitstream=FAIL; receipt=artifacts/cfd1b515d7114e627f43d8306df877d2c0010024613afccddb7263203e02215a/rejected/candidate_02/rejection-receipt.json

## Blockers

- none
