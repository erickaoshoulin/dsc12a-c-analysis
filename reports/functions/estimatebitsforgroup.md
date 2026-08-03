# EstimateBitsForGroup (estimatebitsforgroup)

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
| input | dsc_version_minor | 2 | False | dsc_version_minor | DSC 1.1/1.2 version branches used by MapQpToQlevel | EXACT_SPEC: DSC 1.1/1.2 version branches used by MapQpToQlevel (REVIEWED) |
| input | native_420 | 1 | False | native_420 | PPS native_420 flag used by MapQpToQlevel | EXACT_SPEC: PPS native_420 flag used by MapQpToQlevel (REVIEWED) |
| input | units_per_group | 3 | False | units_per_group | DSC source initialization and native 4:2:2 group structure | EXACT_SPEC: DSC source initialization and native 4:2:2 group structure (REVIEWED) |
| input | pixels_in_group | 2 | False | pixels_in_group | SAMPLES_PER_UNIT and source pixelsInGroup initialization | EXACT_SPEC: SAMPLES_PER_UNIT and source pixelsInGroup initialization (REVIEWED) |
| input | hPos | 16 | False | hPos | DSC slice-relative horizontal position domain | EXACT_SPEC: DSC slice-relative horizontal position domain (REVIEWED) |
| input | slice_width | 16 | False | slice_width | DSC sliceWidth positive finite source domain | EXACT_SPEC: DSC sliceWidth positive finite source domain (REVIEWED) |
| input | prev_ich_selected | 1 | False | prev_ich_selected | Previous-group ICH selection flag | EXACT_SPEC: Previous-group ICH selection flag (REVIEWED) |
| input | primary_qp | 5 | False | primary_qp | Table 6-2 masterQp rows | EXACT_SPEC: Table 6-2 masterQp rows (REVIEWED) |
| input | prev_primary_qp | 5 | False | prev_primary_qp | Table 6-2 masterQp rows | EXACT_SPEC: Table 6-2 masterQp rows (REVIEWED) |
| input | cpntBitDepth_0 | 5 | False | cpntBitDepth_0 | DSC supported base component bit depths | EXACT_SPEC: DSC supported base component bit depths (REVIEWED) |
| input | cpntBitDepth_1 | 5 | False | cpntBitDepth_1 | DSC component bit-depth projection; Table 6-2 base-depth relation is enforced by the vector/formal strategy | EXACT_SPEC: DSC component bit-depth projection; Table 6-2 base-depth relation is enforced by the vector/formal strategy (REVIEWED) |
| input | cpntBitDepth_2 | 5 | False | cpntBitDepth_2 | DSC component bit-depth projection; Table 6-2 base-depth relation is enforced by the vector/formal strategy | EXACT_SPEC: DSC component bit-depth projection; Table 6-2 base-depth relation is enforced by the vector/formal strategy (REVIEWED) |
| input | cpntBitDepth_3 | 5 | False | cpntBitDepth_3 | DSC component bit-depth projection; Table 6-2 base-depth relation is enforced by the vector/formal strategy | EXACT_SPEC: DSC component bit-depth projection; Table 6-2 base-depth relation is enforced by the vector/formal strategy (REVIEWED) |
| input | unit_c_type_0 | 2 | False | unit_c_type_0 | dsc_state_t unitCType component index domain | EXACT_SPEC: dsc_state_t unitCType component index domain (REVIEWED) |
| input | unit_c_type_1 | 2 | False | unit_c_type_1 | dsc_state_t unitCType component index domain | EXACT_SPEC: dsc_state_t unitCType component index domain (REVIEWED) |
| input | unit_c_type_2 | 2 | False | unit_c_type_2 | dsc_state_t unitCType component index domain | EXACT_SPEC: dsc_state_t unitCType component index domain (REVIEWED) |
| input | unit_c_type_3 | 2 | False | unit_c_type_3 | dsc_state_t unitCType component index domain | EXACT_SPEC: dsc_state_t unitCType component index domain (REVIEWED) |
| input | unit_start_h_pos_0 | 16 | False | unit_start_h_pos_0 | source initialization leaves unitStartHPos at zero | EXACT_SPEC: source initialization leaves unitStartHPos at zero (REVIEWED) |
| input | unit_start_h_pos_1 | 16 | False | unit_start_h_pos_1 | source initialization leaves unitStartHPos at zero | EXACT_SPEC: source initialization leaves unitStartHPos at zero (REVIEWED) |
| input | unit_start_h_pos_2 | 16 | False | unit_start_h_pos_2 | source initialization leaves unitStartHPos at zero | EXACT_SPEC: source initialization leaves unitStartHPos at zero (REVIEWED) |
| input | unit_start_h_pos_3 | 16 | False | unit_start_h_pos_3 | source initialization leaves unitStartHPos at zero | EXACT_SPEC: source initialization leaves unitStartHPos at zero (REVIEWED) |
| input | predicted_size_0 | 5 | False | predicted_size_0 | DSC DSU predicted size domain | EXACT_SPEC: DSC DSU predicted size domain (REVIEWED) |
| input | predicted_size_1 | 5 | False | predicted_size_1 | DSC DSU predicted size domain | EXACT_SPEC: DSC DSU predicted size domain (REVIEWED) |
| input | predicted_size_2 | 5 | False | predicted_size_2 | DSC DSU predicted size domain | EXACT_SPEC: DSC DSU predicted size domain (REVIEWED) |
| input | predicted_size_3 | 5 | False | predicted_size_3 | DSC DSU predicted size domain | EXACT_SPEC: DSC DSU predicted size domain (REVIEWED) |
| input | quantized_residual_0_0 | 17 | True | quantized_residual_0_0 | DSC signed quantized residual domain used by FindResidualSize | EXACT_SPEC: DSC signed quantized residual domain used by FindResidualSize (REVIEWED) |
| input | quantized_residual_0_1 | 17 | True | quantized_residual_0_1 | DSC signed quantized residual domain used by FindResidualSize | EXACT_SPEC: DSC signed quantized residual domain used by FindResidualSize (REVIEWED) |
| input | quantized_residual_0_2 | 17 | True | quantized_residual_0_2 | DSC signed quantized residual domain used by FindResidualSize | EXACT_SPEC: DSC signed quantized residual domain used by FindResidualSize (REVIEWED) |
| input | quantized_residual_1_0 | 17 | True | quantized_residual_1_0 | DSC signed quantized residual domain used by FindResidualSize | EXACT_SPEC: DSC signed quantized residual domain used by FindResidualSize (REVIEWED) |
| input | quantized_residual_1_1 | 17 | True | quantized_residual_1_1 | DSC signed quantized residual domain used by FindResidualSize | EXACT_SPEC: DSC signed quantized residual domain used by FindResidualSize (REVIEWED) |
| input | quantized_residual_1_2 | 17 | True | quantized_residual_1_2 | DSC signed quantized residual domain used by FindResidualSize | EXACT_SPEC: DSC signed quantized residual domain used by FindResidualSize (REVIEWED) |
| input | quantized_residual_2_0 | 17 | True | quantized_residual_2_0 | DSC signed quantized residual domain used by FindResidualSize | EXACT_SPEC: DSC signed quantized residual domain used by FindResidualSize (REVIEWED) |
| input | quantized_residual_2_1 | 17 | True | quantized_residual_2_1 | DSC signed quantized residual domain used by FindResidualSize | EXACT_SPEC: DSC signed quantized residual domain used by FindResidualSize (REVIEWED) |
| input | quantized_residual_2_2 | 17 | True | quantized_residual_2_2 | DSC signed quantized residual domain used by FindResidualSize | EXACT_SPEC: DSC signed quantized residual domain used by FindResidualSize (REVIEWED) |
| input | quantized_residual_3_0 | 17 | True | quantized_residual_3_0 | DSC signed quantized residual domain used by FindResidualSize | EXACT_SPEC: DSC signed quantized residual domain used by FindResidualSize (REVIEWED) |
| input | quantized_residual_3_1 | 17 | True | quantized_residual_3_1 | DSC signed quantized residual domain used by FindResidualSize | EXACT_SPEC: DSC signed quantized residual domain used by FindResidualSize (REVIEWED) |
| input | quantized_residual_3_2 | 17 | True | quantized_residual_3_2 | DSC signed quantized residual domain used by FindResidualSize | EXACT_SPEC: DSC signed quantized residual domain used by FindResidualSize (REVIEWED) |
| input | qlevel_luma_new | 5 | False | qlevel_luma_new | Table 6-2 qLevel entry domain | EXACT_SPEC: Table 6-2 qLevel entry domain (REVIEWED) |
| input | qlevel_luma_old | 5 | False | qlevel_luma_old | Table 6-2 qLevel entry domain | EXACT_SPEC: Table 6-2 qLevel entry domain (REVIEWED) |
| input | qlevel_chroma_new | 5 | False | qlevel_chroma_new | Table 6-2 qLevel entry domain | EXACT_SPEC: Table 6-2 qLevel entry domain (REVIEWED) |
| input | qlevel_chroma_old | 5 | False | qlevel_chroma_old | Table 6-2 qLevel entry domain | EXACT_SPEC: Table 6-2 qLevel entry domain (REVIEWED) |
| output | return_value | 9 | False | return_value | — | EXACT_SPEC: DERIVED_SPEC_DOMAIN (REVIEWED) |

## Spec -> C -> Contract -> RTL -> Verification -> Frame

- Spec: PASS (file:///Users/snow/Desktop/Display%20Stream%20Compression%20%28DSC%29/DSC%201.2a/DSC_v1.2a.pdf#page=88)
- C: UNPROVED (file:///Users/snow/Desktop/Display%20Stream%20Compression%20%28DSC%29/DSC%201.2a/DSC_model_20210623/dsc_codec.c#L390)
- Contract: PASS (../../library/contracts/estimatebitsforgroup.json)
- RTL: PASS (file:///Users/snow/.svrt-network/dsc12a-regression/runs/20260803T014654Z-scale-2b8c6c5c/functions/estimatebitsforgroup/accepted/candidate_01.sv)
- Verification: PASS (file:///private/tmp/dsc12a-regression-dashboard/library/verification/estimatebitsforgroup.json)
- Frame: PASS (#frame-matrix)

- Spec status: AVAILABLE; PDF: /Users/snow/Desktop/Display Stream Compression (DSC)/DSC 1.2a/DSC_v1.2a.pdf
- C: dsc_codec.c (file:///Users/snow/Desktop/Display%20Stream%20Compression%20%28DSC%29/DSC%201.2a/DSC_model_20210623/dsc_codec.c#L390) lines 390-437

## Candidates, mutations, and counterexamples

- Candidates passed: 1/2
- Vectors: 1040928, shards 4/4, verification FORMAL_EQUIVALENT
- Mutation evidence: 0/5, planned 5 (planned mutation cases; per-case result receipt not recorded)

| Stage | Candidate | Expected | Actual | Inputs |
|---|---|---|---|---|
| generator_cache | candidate_02 | 3 | 4 | [1, 0, 3, 3, 0, 1, 0, 0, 0, 8, 8, 8, 8, 0, 1, 2, 2, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0] |

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
| contract | c5df1296bcc105ab0e0796e782a82abc3434bc173f8320565e5f4586f6562a13 |
| rtl | da8e09494b9dad38a4591c81c21adf445cc0b92cdaf4eabc1604aa1ca2db3f9f |
| promotion | PASS; immutable=True; stale=False |

### Strategy history

| Run | Decision | Tier | Rationale |
|---|---|---|---|
| 20260803T013704Z-05a52482 | enqueue | — | user-authorized large-scale batch; each discovered contract has an independent flow worktree |
| 20260803T014654Z-scale-2b8c6c5c | planned | strong | explicit scale batch from facts-driven GENERATION_READY plan |
| 20260803T014654Z-scale-2b8c6c5c | selected | strong | explicit scale batch; current facts/spec plan; independent contract flow worktrees; no SVRT |

## Run comparison

| Run | Status | Candidates | Frames | Vectors | Change |
|---|---|---|---|---:|---|
| 20260803T014654Z-scale-2b8c6c5c | PASS | 1/2 | 3/3 | 1040928 | current |
