# IsOrigFlatHIndex (isorigflathindex)

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
| input | hPos | 16 | False | hPos | DSC slice horizontal position domain; hPos + 1 is compared against the positive slice width | EXACT_SPEC: DSC slice horizontal position domain; hPos + 1 is compared against the positive slice width (REVIEWED) |
| input | bits_per_component | 5 | False | bits_per_component | DSC supported component bit depths | EXACT_SPEC: DSC supported component bit depths (REVIEWED) |
| input | primary_qp | 5 | False | primary_qp | DSC masterQp/Table 6-2 index domain | EXACT_SPEC: DSC masterQp/Table 6-2 index domain (REVIEWED) |
| input | num_components | 3 | False | num_components | DSC model component count: three components except native 4:2:2's four component lanes | EXACT_SPEC: DSC model component count: three components except native 4:2:2's four component lanes (REVIEWED) |
| input | slice_width | 16 | False | slice_width | Positive DSC slice width domain used by the line-end decision | EXACT_SPEC: Positive DSC slice width domain used by the line-end decision (REVIEWED) |
| input | flatness_det_thresh | 10 | False | flatness_det_thresh | DSC 1.2a flatnessDetThresh = 2 << (bits_per_component - 8) | EXACT_SPEC: DSC 1.2a flatnessDetThresh = 2 << (bits_per_component - 8) (REVIEWED) |
| input | somewhat_flat_qp_delta | 3 | False | somewhat_flat_qp_delta | DSC 1.2a section 6.8.5.1 normative somewhatFlatQpDelta | EXACT_SPEC: DSC 1.2a section 6.8.5.1 normative somewhatFlatQpDelta (REVIEWED) |
| input | native_420 | 1 | False | native_420 | DSC native_420 configuration flag | EXACT_SPEC: DSC native_420 configuration flag (REVIEWED) |
| input | dsc_version_minor | 2 | False | dsc_version_minor | DSC 1.1/1.2 model modes; the 1.2 chroma qLevel adjustment is active only at minor version 2 | EXACT_SPEC: DSC 1.1/1.2 model modes; the 1.2 chroma qLevel adjustment is active only at minor version 2 (REVIEWED) |
| input | cpnt_bit_depth_0 | 5 | False | cpnt_bit_depth_0 | DSC luma component bit depth used by MapQpToQlevel's YCbCr adjustment | EXACT_SPEC: DSC luma component bit depth used by MapQpToQlevel's YCbCr adjustment (REVIEWED) |
| input | cpnt_bit_depth_1 | 5 | False | cpnt_bit_depth_1 | DSC component bit depth, including the RGB-conversion +1 component depth used by the model | EXACT_SPEC: DSC component bit depth, including the RGB-conversion +1 component depth used by the model (REVIEWED) |
| input | orig_0_0 | 16 | False | orig_0_0 | DSC component sample domain | EXACT_SPEC: DSC component sample domain (REVIEWED) |
| input | orig_0_1 | 16 | False | orig_0_1 | DSC component sample domain | EXACT_SPEC: DSC component sample domain (REVIEWED) |
| input | orig_0_2 | 16 | False | orig_0_2 | DSC component sample domain | EXACT_SPEC: DSC component sample domain (REVIEWED) |
| input | orig_0_3 | 16 | False | orig_0_3 | DSC component sample domain | EXACT_SPEC: DSC component sample domain (REVIEWED) |
| input | orig_0_4 | 16 | False | orig_0_4 | DSC component sample domain | EXACT_SPEC: DSC component sample domain (REVIEWED) |
| input | orig_0_5 | 16 | False | orig_0_5 | DSC component sample domain | EXACT_SPEC: DSC component sample domain (REVIEWED) |
| input | orig_0_6 | 16 | False | orig_0_6 | DSC component sample domain | EXACT_SPEC: DSC component sample domain (REVIEWED) |
| input | orig_1_0 | 16 | False | orig_1_0 | DSC component sample domain | EXACT_SPEC: DSC component sample domain (REVIEWED) |
| input | orig_1_1 | 16 | False | orig_1_1 | DSC component sample domain | EXACT_SPEC: DSC component sample domain (REVIEWED) |
| input | orig_1_2 | 16 | False | orig_1_2 | DSC component sample domain | EXACT_SPEC: DSC component sample domain (REVIEWED) |
| input | orig_1_3 | 16 | False | orig_1_3 | DSC component sample domain | EXACT_SPEC: DSC component sample domain (REVIEWED) |
| input | orig_1_4 | 16 | False | orig_1_4 | DSC component sample domain | EXACT_SPEC: DSC component sample domain (REVIEWED) |
| input | orig_1_5 | 16 | False | orig_1_5 | DSC component sample domain | EXACT_SPEC: DSC component sample domain (REVIEWED) |
| input | orig_1_6 | 16 | False | orig_1_6 | DSC component sample domain | EXACT_SPEC: DSC component sample domain (REVIEWED) |
| input | orig_2_0 | 16 | False | orig_2_0 | DSC component sample domain | EXACT_SPEC: DSC component sample domain (REVIEWED) |
| input | orig_2_1 | 16 | False | orig_2_1 | DSC component sample domain | EXACT_SPEC: DSC component sample domain (REVIEWED) |
| input | orig_2_2 | 16 | False | orig_2_2 | DSC component sample domain | EXACT_SPEC: DSC component sample domain (REVIEWED) |
| input | orig_2_3 | 16 | False | orig_2_3 | DSC component sample domain | EXACT_SPEC: DSC component sample domain (REVIEWED) |
| input | orig_2_4 | 16 | False | orig_2_4 | DSC component sample domain | EXACT_SPEC: DSC component sample domain (REVIEWED) |
| input | orig_2_5 | 16 | False | orig_2_5 | DSC component sample domain | EXACT_SPEC: DSC component sample domain (REVIEWED) |
| input | orig_2_6 | 16 | False | orig_2_6 | DSC component sample domain | EXACT_SPEC: DSC component sample domain (REVIEWED) |
| input | orig_3_0 | 16 | False | orig_3_0 | DSC component sample domain | EXACT_SPEC: DSC component sample domain (REVIEWED) |
| input | orig_3_1 | 16 | False | orig_3_1 | DSC component sample domain | EXACT_SPEC: DSC component sample domain (REVIEWED) |
| input | orig_3_2 | 16 | False | orig_3_2 | DSC component sample domain | EXACT_SPEC: DSC component sample domain (REVIEWED) |
| input | orig_3_3 | 16 | False | orig_3_3 | DSC component sample domain | EXACT_SPEC: DSC component sample domain (REVIEWED) |
| input | orig_3_4 | 16 | False | orig_3_4 | DSC component sample domain | EXACT_SPEC: DSC component sample domain (REVIEWED) |
| input | orig_3_5 | 16 | False | orig_3_5 | DSC component sample domain | EXACT_SPEC: DSC component sample domain (REVIEWED) |
| input | orig_3_6 | 16 | False | orig_3_6 | DSC component sample domain | EXACT_SPEC: DSC component sample domain (REVIEWED) |
| output | return_value | 2 | False | return_value | — | EXACT_SPEC: EXACT_SPEC (REVIEWED) |

## Spec -> C -> Contract -> RTL -> Verification -> Frame

- Spec: PASS (file:///Users/snow/Desktop/Display%20Stream%20Compression%20%28DSC%29/DSC%201.2a/DSC_v1.2a.pdf#page=111)
- C: UNPROVED (file:///Users/snow/Desktop/Display%20Stream%20Compression%20%28DSC%29/DSC%201.2a/DSC_model_20210623/dsc_codec.c#L1126)
- Contract: PASS (../../library/contracts/isorigflathindex.json)
- RTL: PASS (file:///Users/snow/.svrt-network/dsc12a-regression/runs/20260803T014654Z-scale-2b8c6c5c/functions/isorigflathindex/accepted/candidate_01.sv)
- Verification: PASS (file:///private/tmp/dsc12a-regression-dashboard/library/verification/isorigflathindex.json)
- Frame: PASS (#frame-matrix)

- Spec status: AVAILABLE; PDF: /Users/snow/Desktop/Display Stream Compression (DSC)/DSC 1.2a/DSC_v1.2a.pdf
- C: dsc_codec.c (file:///Users/snow/Desktop/Display%20Stream%20Compression%20%28DSC%29/DSC%201.2a/DSC_model_20210623/dsc_codec.c#L1126) lines 1126-1195

## Candidates, mutations, and counterexamples

- Candidates passed: 1/2
- Vectors: 575552, shards 4/4, verification FORMAL_EQUIVALENT
- Mutation evidence: 0/5, planned 5 (planned mutation cases; per-case result receipt not recorded)

| Stage | Candidate | Expected | Actual | Inputs |
|---|---|---|---|---|
| generator_cache | candidate_02 | 0 | 1 | [0, 8, 0, 3, 1, 2, 4, 0, 1, 8, 8, 127, 127, 127, 127, 127, 127, 127, 127, 127, 127, 127, 127, 127, 127, 127, 127, 127, 127, 127, 127, 127, 127, 127, 127, 127, 127, 127, 127] |

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
| contract | ede1a64844ae2271851a9b28a12aa879360255ea68f5e98ffacb1a12b1ba8115 |
| rtl | cfb707d7aa001c86145ecff6476c1fd36b7d2755ecabe5d5af41f817ea22d855 |
| promotion | PASS; immutable=True; stale=False |

### Strategy history

| Run | Decision | Tier | Rationale |
|---|---|---|---|
| 20260802T062208Z-0ad45a41 | enqueue | — | user-authorized large-scale batch; each discovered contract has an independent flow worktree |
| 20260802T213843Z-scale-41855a25 | planned | strong | explicit scale batch from facts-driven GENERATION_READY plan |
| 20260802T213843Z-scale-41855a25 | requeue | — | manual resume after inspecting failed receipt |
| 20260802T213843Z-scale-41855a25 | selected | strong | explicit scale batch; current facts/spec plan; independent contract flow worktrees; no SVRT |
| 20260802T230757Z-scale-7a24e3ac | planned | strong | explicit scale batch from facts-driven GENERATION_READY plan |
| 20260802T230757Z-scale-7a24e3ac | selected | strong | explicit scale batch; current facts/spec plan; independent contract flow worktrees; no SVRT |
| 20260803T013704Z-05a52482 | enqueue | — | user-authorized large-scale batch; each discovered contract has an independent flow worktree |
| 20260803T014654Z-scale-2b8c6c5c | planned | strong | explicit scale batch from facts-driven GENERATION_READY plan |
| 20260803T014654Z-scale-2b8c6c5c | selected | strong | explicit scale batch; current facts/spec plan; independent contract flow worktrees; no SVRT |

## Run comparison

| Run | Status | Candidates | Frames | Vectors | Change |
|---|---|---|---|---:|---|
| 20260802T213843Z-scale-41855a25 | PASS | 1/2 | 3/3 | 575552 |  |
| 20260802T230757Z-scale-7a24e3ac | PASS | 1/2 | 3/3 | 575552 |  |
| 20260803T014654Z-scale-2b8c6c5c | PASS | 1/2 | 3/3 | 575552 | current |
