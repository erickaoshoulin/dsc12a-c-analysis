# Executable generic C-to-RTL pipeline

This report is produced from the current run receipts. The PDF and immutable C model remain external inputs.

- PDF: /Users/snow/Desktop/Display Stream Compression (DSC)/DSC 1.2a/DSC_v1.2a.pdf (724c0979b0a04bb9a5ad7143755bf6fab4bf8cf9598d24a536a5048a66e2aecd)
- C source root: /Users/snow/Desktop/Display Stream Compression (DSC)/DSC 1.2a/DSC_model_20210623 (1cd2ac33e983d1489b2fcc5e138324efba18069db5a6bbe72f6cce3b7d8b9cdf)
- selected new work: quantizeresidual
- generator invocations: 0
- model calls: 0
- token count: 0
- dependency pair: {"call_sites": [{"callee_contract": "quantizeresidual", "callee_function": "QuantizeResidual", "callee_usr": "c:@F@QuantizeResidual", "caller_contract": null, "caller_function": "PredictionLoop", "caller_usr": "c:@F@PredictionLoop", "location": {"column": 12, "file": "dsc_codec.c", "line": 2419}, "source": "facts/callgraph.json"}, {"callee_contract": "quantizeresidual", "callee_function": "QuantizeResidual", "callee_usr": "c:@F@QuantizeResidual", "caller_contract": null, "caller_function": "PredictionLoop", "caller_usr": "c:@F@PredictionLoop", "location": {"column": 130, "file": "dsc_codec.c", "line": 2424}, "source": "facts/callgraph.json"}, {"callee_contract": "quantizeresidual", "callee_function": "QuantizeResidual", "callee_usr": "c:@F@QuantizeResidual", "caller_contract": null, "caller_function": "PredictionLoop", "caller_usr": "c:@F@PredictionLoop", "location": {"column": 60, "file": "dsc_codec.c", "line": 2431}, "source": "facts/callgraph.json"}], "callee_contract": "quantizeresidual", "callee_function": "QuantizeResidual", "callee_usr": "c:@F@QuantizeResidual", "caller_contract": null, "caller_function": "PredictionLoop", "caller_usr": "c:@F@PredictionLoop", "selection_basis": "smallest acyclic direct call site from facts/callgraph.json"}
- baseline scripts discovered: 22

## Results

- quantizeresidual: CACHE_REUSED (REUSED_VERIFIED_RECEIPT); unit=EXHAUSTIVE_EQUIVALENT; dependency=PASS; matrix=PASS
  - executed vectors/shards: 2228207/4; shard seconds: [1.478, 1.485, 0.66, 0.668]
  - matrix modes: {"C_ONLY": "PASS", "RTL_RETURN": "PASS", "SHADOW": "PASS"}
  - dependency evidence: {"call_sites": 3, "compile_commands": true, "direct_call_sites": 3, "matrix_commands": true, "vectors": true}
  - rejected candidate_02: unit=FAIL; bitstream=FAIL; receipt=artifacts/fa7bad1d4165aa6912b83c77ce46b6856c11019d21b91da8d407ac61a62f6cb2/rejected/candidate_02/rejection-receipt.json

## Blockers

- arithmetic_semantics
- field:dsc_cfg_t.flatness_max_qp
- field:dsc_cfg_t.flatness_min_qp
- interface:flatness_max_qp
- interface:flatness_min_qp
- interface:qp
- interface:return_value
- no_exact_spec_link
- parameter:qp
- arithmetic_semantics
- field:dsc_cfg_t.dsc_version_minor
- field:dsc_cfg_t.native_420
- field:dsc_state_t.quantTableChroma
- field:dsc_state_t.quantTableLuma
- interface:dsc_version_minor
- interface:native_420
- interface:qp
- interface:quantTableChroma
- interface:quantTableLuma
- interface:return_value
- parameter:qp
