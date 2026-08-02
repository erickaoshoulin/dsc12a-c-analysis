# Executable generic C-to-RTL pipeline

This report is produced from the current run receipts. The PDF and immutable C model remain external inputs.

- PDF: /Users/snow/Desktop/Display Stream Compression (DSC)/DSC 1.2a/DSC_v1.2a.pdf (724c0979b0a04bb9a5ad7143755bf6fab4bf8cf9598d24a536a5048a66e2aecd)
- C source root: /Users/snow/Desktop/Display Stream Compression (DSC)/DSC 1.2a/DSC_model_20210623 (1cd2ac33e983d1489b2fcc5e138324efba18069db5a6bbe72f6cce3b7d8b9cdf)
- selected new work: isflatnessinfosent
- generator invocations: 1
- model calls: 1
- token count: 2013
- dependency pair: {"call_sites": [{"callee_contract": "isflatnessinfosent", "callee_function": "IsFlatnessInfoSent", "callee_usr": "c:@F@IsFlatnessInfoSent", "caller_contract": null, "caller_function": "FlatnessAdjustment", "caller_usr": "c:@F@FlatnessAdjustment", "location": {"column": 15, "file": "dsc_codec.c", "line": 2537}, "source": "facts/callgraph.json"}, {"callee_contract": "isflatnessinfosent", "callee_function": "IsFlatnessInfoSent", "callee_usr": "c:@F@IsFlatnessInfoSent", "caller_contract": null, "caller_function": "FlatnessAdjustment", "caller_usr": "c:@F@FlatnessAdjustment", "location": {"column": 7, "file": "dsc_codec.c", "line": 2516}, "source": "facts/callgraph.json"}], "callee_contract": "isflatnessinfosent", "callee_function": "IsFlatnessInfoSent", "callee_usr": "c:@F@IsFlatnessInfoSent", "caller_contract": null, "caller_function": "FlatnessAdjustment", "caller_usr": "c:@F@FlatnessAdjustment", "selection_basis": "smallest acyclic direct call site from facts/callgraph.json"}
- baseline scripts discovered: 22

## Results

- isflatnessinfosent: PROMOTED (EXECUTED_NOW); unit=EXHAUSTIVE_EQUIVALENT; dependency=PASS; matrix=PASS
  - executed vectors/shards: 32768/4; shard seconds: [0.852, 0.866, 0.032, 0.032]
  - matrix modes: {"C_ONLY": "PASS", "RTL_RETURN": "PASS", "SHADOW": "PASS"}
  - dependency evidence: {"call_sites": 4, "compile_commands": true, "direct_call_sites": 4, "matrix_commands": true, "vectors": true}
  - rejected candidate_02: unit=FAIL; bitstream=FAIL; receipt=artifacts/60ce2907e7323bd6841b496b2d0109ba05b244c47de52ab037daa087916113e2/rejected/candidate_02/rejection-receipt.json

## Blockers

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
