# GetQpAdjPredSize (getqpadjpredsize)

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
| input | unit | 2 | False | unit | MAX_UNITS_PER_GROUP | EXACT_SPEC: MAX_UNITS_PER_GROUP (REVIEWED) |
| input | dsc_version_minor | 2 | False | CONFIG_STATIC | DSC 1.1/1.2 version branches used by the called mapping functions | EXACT_SPEC: DSC 1.1/1.2 version branches used by the called mapping functions (REVIEWED) |
| input | native_420 | 1 | False | CONFIG_STATIC | PPS native_420 flag used by the called mapping functions | EXACT_SPEC: PPS native_420 flag used by the called mapping functions (REVIEWED) |
| input | unit_c_type_selected | 2 | False | STATE_SELECTED | dsc_state_t unit-to-component mapping domain | EXACT_SPEC: dsc_state_t unit-to-component mapping domain (REVIEWED) |
| input | predicted_size_selected | 5 | False | STATE_SELECTED | PredictSize output domain for one unit | EXACT_SPEC: PredictSize output domain for one unit (REVIEWED) |
| input | primary_qp | 5 | False | STATE_RUNTIME | Table 6-2 masterQp rows | EXACT_SPEC: Table 6-2 masterQp rows (REVIEWED) |
| input | prev_primary_qp | 5 | False | STATE_RUNTIME | Table 6-2 masterQp rows | EXACT_SPEC: Table 6-2 masterQp rows (REVIEWED) |
| input | cpntBitDepth_0 | 5 | False | CONFIG_STATIC | DSC supported component bit depths | EXACT_SPEC: DSC supported component bit depths (REVIEWED) |
| input | cpntBitDepth_1 | 5 | False | CONFIG_STATIC | DSC supported component bit depths | EXACT_SPEC: DSC supported component bit depths (REVIEWED) |
| input | cpntBitDepth_2 | 5 | False | CONFIG_STATIC | DSC supported component bit depths | EXACT_SPEC: DSC supported component bit depths (REVIEWED) |
| input | cpntBitDepth_3 | 5 | False | CONFIG_STATIC | DSC supported component bit depths | EXACT_SPEC: DSC supported component bit depths (REVIEWED) |
| input | qlevel_luma_new | 5 | False | TABLE_LOOKUP_LUMA | Table 6-2 qLevelY entry domain | EXACT_SPEC: Table 6-2 qLevelY entry domain (REVIEWED) |
| input | qlevel_chroma_new | 5 | False | TABLE_LOOKUP_CHROMA | Table 6-2 qLevelC entry domain | EXACT_SPEC: Table 6-2 qLevelC entry domain (REVIEWED) |
| input | qlevel_luma_old | 5 | False | TABLE_LOOKUP_LUMA | Table 6-2 qLevelY entry domain | EXACT_SPEC: Table 6-2 qLevelY entry domain (REVIEWED) |
| input | qlevel_chroma_old | 5 | False | TABLE_LOOKUP_CHROMA | Table 6-2 qLevelC entry domain | EXACT_SPEC: Table 6-2 qLevelC entry domain (REVIEWED) |
| output | return_value | 5 | True | return_value | — | EXACT_SPEC: DERIVED_SPEC_DOMAIN (REVIEWED) |

## Spec -> C -> Contract -> RTL -> Verification -> Frame

- Spec: PASS (file:///Users/snow/Desktop/Display%20Stream%20Compression%20%28DSC%29/DSC%201.2a/DSC_v1.2a.pdf#page=113)
- C: UNPROVED (file:///Users/snow/Desktop/Display%20Stream%20Compression%20%28DSC%29/DSC%201.2a/DSC_model_20210623/dsc_codec.c#L278)
- Contract: PASS (../../library/contracts/getqpadjpredsize.json)
- RTL: PASS (file:///Users/snow/.svrt-network/dsc12a-regression/runs/20260803T014654Z-scale-2b8c6c5c/functions/getqpadjpredsize/accepted/candidate_01.sv)
- Verification: PASS (file:///private/tmp/dsc12a-regression-dashboard/library/verification/getqpadjpredsize.json)
- Frame: PASS (#frame-matrix)

- Spec status: AVAILABLE; PDF: /Users/snow/Desktop/Display Stream Compression (DSC)/DSC 1.2a/DSC_v1.2a.pdf
- C: dsc_codec.c (file:///Users/snow/Desktop/Display%20Stream%20Compression%20%28DSC%29/DSC%201.2a/DSC_model_20210623/dsc_codec.c#L278) lines 278-297

## Candidates, mutations, and counterexamples

- Candidates passed: 1/2
- Vectors: 14831616, shards 4/4, verification EXHAUSTIVE_EQUIVALENT
- Mutation evidence: 0/5, planned 5 (planned mutation cases; per-case result receipt not recorded)

| Stage | Candidate | Expected | Actual | Inputs |
|---|---|---|---|---|
| generator_cache | candidate_02 | 0 | 1 | [0, 0, 0, 0, 0, 0, 0, 8, 8, 8, 8, 0, 0, 0, 0] |

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
| contract | dcab7637a1a2c69f878a404a3ca7a732ca495dc0b8c7d4525100d99b4b593e7c |
| rtl | a8a237d111078f013fa7c15edf430b37d8c58a60595b1082166f16b0334c24b4 |
| promotion | PASS; immutable=True; stale=False |

### Strategy history

| Run | Decision | Tier | Rationale |
|---|---|---|---|
| 20260802T062208Z-0ad45a41 | enqueue | — | user-authorized large-scale batch; each discovered contract has an independent flow worktree |
| 20260802T122049Z-scale-d2066dca | planned | strong | explicit scale batch from facts-driven GENERATION_READY plan |
| 20260802T122049Z-scale-d2066dca | selected | strong | explicit scale batch; current facts/spec plan; independent contract flow worktrees; no SVRT |
| 20260802T122524Z-scale-ddc3d67c | planned | strong | explicit scale batch from facts-driven GENERATION_READY plan |
| 20260802T122524Z-scale-ddc3d67c | selected | strong | explicit scale batch; current facts/spec plan; independent contract flow worktrees; no SVRT |
| 20260802T124401Z-scale-e03da363 | planned | strong | explicit scale batch from facts-driven GENERATION_READY plan |
| 20260802T124401Z-scale-e03da363 | selected | strong | explicit scale batch; current facts/spec plan; independent contract flow worktrees; no SVRT |
| 20260802T125235Z-scale-31386cb4 | planned | strong | explicit scale batch from facts-driven GENERATION_READY plan |
| 20260802T125235Z-scale-31386cb4 | selected | strong | explicit scale batch; current facts/spec plan; independent contract flow worktrees; no SVRT |
| 20260802T133447Z-scale-4b440064 | planned | strong | explicit scale batch from facts-driven GENERATION_READY plan |
| 20260802T133447Z-scale-4b440064 | selected | strong | explicit scale batch; current facts/spec plan; independent contract flow worktrees; no SVRT |
| 20260802T230757Z-scale-7a24e3ac | planned | strong | explicit scale batch from facts-driven GENERATION_READY plan |
| 20260802T230757Z-scale-7a24e3ac | selected | strong | explicit scale batch; current facts/spec plan; independent contract flow worktrees; no SVRT |
| 20260803T013704Z-05a52482 | enqueue | — | user-authorized large-scale batch; each discovered contract has an independent flow worktree |
| 20260803T014654Z-scale-2b8c6c5c | planned | strong | explicit scale batch from facts-driven GENERATION_READY plan |
| 20260803T014654Z-scale-2b8c6c5c | selected | strong | explicit scale batch; current facts/spec plan; independent contract flow worktrees; no SVRT |

## Run comparison

| Run | Status | Candidates | Frames | Vectors | Change |
|---|---|---|---|---:|---|
| 20260802T122049Z-scale-d2066dca | INFRASTRUCTURE_FAILURE | 0/0 | 0/0 | 0 |  |
| 20260802T122524Z-scale-ddc3d67c | INFRASTRUCTURE_FAILURE | 0/0 | 0/0 | 0 |  |
| 20260802T124401Z-scale-e03da363 | INFRASTRUCTURE_FAILURE | 0/0 | 0/0 | 0 |  |
| 20260802T125235Z-scale-31386cb4 | PASS | 1/2 | 3/3 | 14831616 |  |
| 20260802T133447Z-scale-4b440064 | PASS | 1/2 | 3/3 | 14831616 |  |
| 20260802T230757Z-scale-7a24e3ac | PASS | 1/2 | 3/3 | 14831616 |  |
| 20260803T014654Z-scale-2b8c6c5c | PASS | 1/2 | 3/3 | 14831616 | current |
