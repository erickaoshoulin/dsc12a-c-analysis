# SamplePredict (samplepredict)

Status: PASS
Selected run: 20260803T014654Z-scale-2b8c6c5c
Stage: complete
Next action: Review the accepted RTL and retain the recorded C_ONLY rollback/reference path.

## Stage checklist

| Stage | Status | Detail |
|---|---|---|
| width/spec gate | PASS | PASS |
| candidate generation/cache | PASS | PASS |
| RTL lint/build | PASS | PASS |
| formal proof | UNPROVED | receipt stage not present |
| formal RTL equivalence | UNPROVED | receipt stage not present |
| unit equivalence | PASS | unit equivalence is recorded in the vectors/mutations receipt |
| vectors and mutations | PASS | PASS |
| dependency composition | UNPROVED | NOT_APPLICABLE |
| C_ONLY / SHADOW / RTL_RETURN | PASS | PASS |
| frame/bitstream sanity | PASS | PASS |

## Interface and width derivation

| Direction | Port | Width | Signed | Role | Domain | Authority / formula |
|---|---|---:|---|---|---|---|
| input | hPos | 16 | False | hPos | hPos is the production slice-relative position; source bounds slice_width to 1..65535 and SamplePredict is called for hPos < sliceWidth | EXACT_SPEC: hPos is the production slice-relative position; source bounds slice_width to 1..65535 and SamplePredict is called for hPos < sliceWidth (REVIEWED) |
| input | predType | 4 | False | predType | PT_MAP/PT_LEFT plus NUM_PRED_TYPES from dsc_types.h; BP_RANGE=13 | EXACT_SPEC: PT_MAP/PT_LEFT plus NUM_PRED_TYPES from dsc_types.h; BP_RANGE=13 (REVIEWED) |
| input | qLevel | 5 | False | qLevel | QuantDivisor[17] and Table 6-2 qLevel output domain | EXACT_SPEC: QuantDivisor[17] and Table 6-2 qLevel output domain (REVIEWED) |
| input | unit | 2 | False | unit | MAX_UNITS_PER_GROUP=4 | EXACT_SPEC: MAX_UNITS_PER_GROUP=4 (REVIEWED) |
| input | cpnt_bit_depth | 5 | False | CONFIG_STATIC | DSC base component bit depths plus the immutable model RGB chroma +1-bit extension | EXACT_SPEC: DSC base component bit depths plus the immutable model RGB chroma +1-bit extension (REVIEWED) |
| input | unit_c_type | 2 | False | RUNTIME_INPUT | dsc_state_t.unitCType component-index domain | EXACT_SPEC: dsc_state_t.unitCType component-index domain (REVIEWED) |
| input | quantized_residual_0 | 16 | True | RUNTIME_INPUT | signed decoded residual envelope; vector strategy narrows to cpntBitDepth-qLevel signed n-bit boundaries | EXACT_SPEC: signed decoded residual envelope; vector strategy narrows to cpntBitDepth-qLevel signed n-bit boundaries (REVIEWED) |
| input | quantized_residual_1 | 16 | True | RUNTIME_INPUT | signed decoded residual envelope; vector strategy narrows to cpntBitDepth-qLevel signed n-bit boundaries | EXACT_SPEC: signed decoded residual envelope; vector strategy narrows to cpntBitDepth-qLevel signed n-bit boundaries (REVIEWED) |
| input | prev_3 | 16 | False | RUNTIME_INPUT | reconstructed sample range for 8..16 bpc | EXACT_SPEC: reconstructed sample range for 8..16 bpc (REVIEWED) |
| input | prev_4 | 16 | False | RUNTIME_INPUT | reconstructed sample range for 8..16 bpc | EXACT_SPEC: reconstructed sample range for 8..16 bpc (REVIEWED) |
| input | prev_5 | 16 | False | RUNTIME_INPUT | reconstructed sample range for 8..16 bpc | EXACT_SPEC: reconstructed sample range for 8..16 bpc (REVIEWED) |
| input | prev_6 | 16 | False | RUNTIME_INPUT | reconstructed sample range for 8..16 bpc | EXACT_SPEC: reconstructed sample range for 8..16 bpc (REVIEWED) |
| input | prev_7 | 16 | False | RUNTIME_INPUT | reconstructed sample range for 8..16 bpc | EXACT_SPEC: reconstructed sample range for 8..16 bpc (REVIEWED) |
| input | prev_8 | 16 | False | RUNTIME_INPUT | reconstructed sample range for 8..16 bpc | EXACT_SPEC: reconstructed sample range for 8..16 bpc (REVIEWED) |
| input | prev_9 | 16 | False | RUNTIME_INPUT | reconstructed sample range for 8..16 bpc | EXACT_SPEC: reconstructed sample range for 8..16 bpc (REVIEWED) |
| input | prev_10 | 16 | False | RUNTIME_INPUT | reconstructed sample range for 8..16 bpc | EXACT_SPEC: reconstructed sample range for 8..16 bpc (REVIEWED) |
| input | prev_11 | 16 | False | RUNTIME_INPUT | reconstructed sample range for 8..16 bpc | EXACT_SPEC: reconstructed sample range for 8..16 bpc (REVIEWED) |
| input | prev_12 | 16 | False | RUNTIME_INPUT | reconstructed sample range for 8..16 bpc | EXACT_SPEC: reconstructed sample range for 8..16 bpc (REVIEWED) |
| input | prev_13 | 16 | False | RUNTIME_INPUT | reconstructed sample range for 8..16 bpc | EXACT_SPEC: reconstructed sample range for 8..16 bpc (REVIEWED) |
| input | prev_14 | 16 | False | RUNTIME_INPUT | reconstructed sample range for 8..16 bpc | EXACT_SPEC: reconstructed sample range for 8..16 bpc (REVIEWED) |
| input | prev_15 | 16 | False | RUNTIME_INPUT | reconstructed sample range for 8..16 bpc | EXACT_SPEC: reconstructed sample range for 8..16 bpc (REVIEWED) |
| input | prev_16 | 16 | False | RUNTIME_INPUT | reconstructed sample range for 8..16 bpc | EXACT_SPEC: reconstructed sample range for 8..16 bpc (REVIEWED) |
| input | prev_17 | 16 | False | RUNTIME_INPUT | reconstructed sample range for 8..16 bpc | EXACT_SPEC: reconstructed sample range for 8..16 bpc (REVIEWED) |
| input | curr_0 | 16 | False | RUNTIME_INPUT | reconstructed sample range for 8..16 bpc | EXACT_SPEC: reconstructed sample range for 8..16 bpc (REVIEWED) |
| input | curr_1 | 16 | False | RUNTIME_INPUT | reconstructed sample range for 8..16 bpc | EXACT_SPEC: reconstructed sample range for 8..16 bpc (REVIEWED) |
| input | curr_2 | 16 | False | RUNTIME_INPUT | reconstructed sample range for 8..16 bpc | EXACT_SPEC: reconstructed sample range for 8..16 bpc (REVIEWED) |
| input | curr_3 | 16 | False | RUNTIME_INPUT | reconstructed sample range for 8..16 bpc | EXACT_SPEC: reconstructed sample range for 8..16 bpc (REVIEWED) |
| input | curr_4 | 16 | False | RUNTIME_INPUT | reconstructed sample range for 8..16 bpc | EXACT_SPEC: reconstructed sample range for 8..16 bpc (REVIEWED) |
| input | curr_5 | 16 | False | RUNTIME_INPUT | reconstructed sample range for 8..16 bpc | EXACT_SPEC: reconstructed sample range for 8..16 bpc (REVIEWED) |
| input | curr_6 | 16 | False | RUNTIME_INPUT | reconstructed sample range for 8..16 bpc | EXACT_SPEC: reconstructed sample range for 8..16 bpc (REVIEWED) |
| input | curr_7 | 16 | False | RUNTIME_INPUT | reconstructed sample range for 8..16 bpc | EXACT_SPEC: reconstructed sample range for 8..16 bpc (REVIEWED) |
| input | curr_8 | 16 | False | RUNTIME_INPUT | reconstructed sample range for 8..16 bpc | EXACT_SPEC: reconstructed sample range for 8..16 bpc (REVIEWED) |
| input | curr_9 | 16 | False | RUNTIME_INPUT | reconstructed sample range for 8..16 bpc | EXACT_SPEC: reconstructed sample range for 8..16 bpc (REVIEWED) |
| input | curr_10 | 16 | False | RUNTIME_INPUT | reconstructed sample range for 8..16 bpc | EXACT_SPEC: reconstructed sample range for 8..16 bpc (REVIEWED) |
| input | curr_11 | 16 | False | RUNTIME_INPUT | reconstructed sample range for 8..16 bpc | EXACT_SPEC: reconstructed sample range for 8..16 bpc (REVIEWED) |
| input | curr_12 | 16 | False | RUNTIME_INPUT | reconstructed sample range for 8..16 bpc | EXACT_SPEC: reconstructed sample range for 8..16 bpc (REVIEWED) |
| input | curr_13 | 16 | False | RUNTIME_INPUT | reconstructed sample range for 8..16 bpc | EXACT_SPEC: reconstructed sample range for 8..16 bpc (REVIEWED) |
| input | curr_14 | 16 | False | RUNTIME_INPUT | reconstructed sample range for 8..16 bpc | EXACT_SPEC: reconstructed sample range for 8..16 bpc (REVIEWED) |
| input | curr_15 | 16 | False | RUNTIME_INPUT | reconstructed sample range for 8..16 bpc | EXACT_SPEC: reconstructed sample range for 8..16 bpc (REVIEWED) |
| output | return_value | 16 | False | return_value | — | EXACT_SPEC: EXACT_SPEC_SAMPLE_DOMAIN (REVIEWED) |

## Spec -> C -> Contract -> RTL -> Verification -> Frame

- Spec: PASS (file:///Users/snow/Desktop/Display%20Stream%20Compression%20%28DSC%29/DSC%201.2a/DSC_v1.2a.pdf#page=76)
- C: PASS (https://github.com/erickaoshoulin/dsc-1-2a-rust-port/blob/f26ecb2afa83aa9f0cc608b5b7c2742901ee9207/dsc_codec.c#L308-L383)
- Contract: PASS (../../library/contracts/samplepredict.json)
- RTL: PASS (file:///Users/snow/.svrt-network/dsc12a-regression/runs/20260803T014654Z-scale-2b8c6c5c/functions/samplepredict/accepted/candidate_01.sv)
- Verification: PASS (file:///private/tmp/dsc12a-regression-dashboard/library/verification/samplepredict.json)
- Frame: PASS (#frame-matrix)

- Spec status: AVAILABLE; PDF: /Users/snow/Desktop/Display Stream Compression (DSC)/DSC 1.2a/DSC_v1.2a.pdf
- C: dsc_codec.c (https://github.com/erickaoshoulin/dsc-1-2a-rust-port/blob/f26ecb2afa83aa9f0cc608b5b7c2742901ee9207/dsc_codec.c#L308-L383) lines 308-383

## Candidates, mutations, and counterexamples

- Candidates passed: 1/2
- Vectors: 25960080, shards 4/4, verification FORMAL_EQUIVALENT
- Mutation evidence: 0/5, planned 5 (planned mutation cases; per-case result receipt not recorded)

| Stage | Candidate | Expected | Actual | Inputs |
|---|---|---|---|---|
| generator_cache | candidate_02 | 127 | 128 | [0, 1, 0, 0, 8, 0, 0, 0, 127, 127, 127, 127, 127, 127, 32768, 32768, 32768, 32768, 32768, 32768, 32768, 32768, 32768, 127, 127, 127, 127, 127, 127, 127, 127, 127, 127, 127, 127, 127, 32768, 32768, 32768] |

## Matrix

| Mode | Result |
|---|---|
| C_ONLY | PASS (1/1) |
| SHADOW | PASS (1/1) |
| RTL_RETURN | PASS (1/1) |
| frame | PASS (3/3) |

## Hashes, promotion, and strategy

| Identity | Value |
|---|---|
| source | 1cd2ac33e983d1489b2fcc5e138324efba18069db5a6bbe72f6cce3b7d8b9cdf |
| spec | 724c0979b0a04bb9a5ad7143755bf6fab4bf8cf9598d24a536a5048a66e2aecd |
| contract | 66e5309e5cf66c9b07022c746307cf37fecbccfa92d7c8ff549ed8b0cbb69509 |
| rtl | 831411aefb7fd14c630f6a71d75191a62320ce17566d6292637fcdab603e2011 |
| promotion | PASS; immutable=True; stale=False |

### Strategy history

| Run | Decision | Tier | Rationale |
|---|---|---|---|
| 20260802T062208Z-0ad45a41 | enqueue | — | user-authorized large-scale batch; each discovered contract has an independent flow worktree |
| 20260802T213843Z-scale-41855a25 | planned | strong | explicit scale batch from facts-driven GENERATION_READY plan |
| 20260802T213843Z-scale-41855a25 | selected | strong | explicit scale batch; current facts/spec plan; independent contract flow worktrees; no SVRT |
| 20260802T230757Z-scale-7a24e3ac | planned | strong | explicit scale batch from facts-driven GENERATION_READY plan |
| 20260802T230757Z-scale-7a24e3ac | selected | strong | explicit scale batch; current facts/spec plan; independent contract flow worktrees; no SVRT |
| 20260803T013704Z-05a52482 | enqueue | — | user-authorized large-scale batch; each discovered contract has an independent flow worktree |
| 20260803T014654Z-scale-2b8c6c5c | planned | strong | explicit scale batch from facts-driven GENERATION_READY plan |
| 20260803T014654Z-scale-2b8c6c5c | selected | strong | explicit scale batch; current facts/spec plan; independent contract flow worktrees; no SVRT |

## Run comparison

| Run | Status | Candidates | Frames | Vectors | Change |
|---|---|---|---|---:|---|
| 20260802T213843Z-scale-41855a25 | PASS | 1/2 | 3/3 | 25960080 |  |
| 20260802T230757Z-scale-7a24e3ac | PASS | 1/2 | 3/3 | 25960080 |  |
| 20260803T014654Z-scale-2b8c6c5c | PASS | 1/2 | 3/3 | 25960080 | current |
