# UsingMidpoint (usingmidpoint)

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
| input | unit | 2 | False | unit | dsc_state_t quantizedResidual unit index; SAMPLES_PER_UNIT is 3 and four component lanes are modeled | EXACT_SPEC: dsc_state_t quantizedResidual unit index; SAMPLES_PER_UNIT is 3 and four component lanes are modeled (REVIEWED) |
| input | cpnt | 2 | False | cpnt | dsc_state_t component index domain | EXACT_SPEC: dsc_state_t component index domain (REVIEWED) |
| input | dsc_version_minor | 2 | False | CONFIG_STATIC | DSC 1.1/1.2 version branches used by MapQpToQlevel | EXACT_SPEC: DSC 1.1/1.2 version branches used by MapQpToQlevel (REVIEWED) |
| input | native_420 | 1 | False | CONFIG_STATIC | PPS native_420 flag | EXACT_SPEC: PPS native_420 flag (REVIEWED) |
| input | primary_qp | 5 | False | STATE_RUNTIME | Table 6-2 masterQp rows | EXACT_SPEC: Table 6-2 masterQp rows (REVIEWED) |
| input | cpntBitDepth_0 | 5 | False | CONFIG_STATIC | DSC supported component bit depths | EXACT_SPEC: DSC supported component bit depths (REVIEWED) |
| input | cpntBitDepth_1 | 5 | False | CONFIG_STATIC | DSC supported component bit depths | EXACT_SPEC: DSC supported component bit depths (REVIEWED) |
| input | cpntBitDepth_2 | 5 | False | CONFIG_STATIC | DSC supported component bit depths | EXACT_SPEC: DSC supported component bit depths (REVIEWED) |
| input | cpntBitDepth_3 | 5 | False | CONFIG_STATIC | DSC supported component bit depths | EXACT_SPEC: DSC supported component bit depths (REVIEWED) |
| input | cpntBitDepth_selected | 5 | False | CONFIG_SELECTED | selected dsc_state_t component bit depth; exact cpnt array projection | EXACT_SPEC: selected dsc_state_t component bit depth; exact cpnt array projection (REVIEWED) |
| input | qlevel_luma | 5 | False | TABLE_LOOKUP_LUMA | Table 6-2 qLevelY entry domain | EXACT_SPEC: Table 6-2 qLevelY entry domain (REVIEWED) |
| input | qlevel_chroma | 5 | False | TABLE_LOOKUP_CHROMA | Table 6-2 qLevelC entry domain | EXACT_SPEC: Table 6-2 qLevelC entry domain (REVIEWED) |
| input | quantized_residual_0 | 17 | True | RUNTIME_INPUT | signed quantized residual envelope used by the reviewed C source gate | EXACT_SPEC: signed quantized residual envelope used by the reviewed C source gate (REVIEWED) |
| input | quantized_residual_1 | 17 | True | RUNTIME_INPUT | signed quantized residual envelope used by the reviewed C source gate | EXACT_SPEC: signed quantized residual envelope used by the reviewed C source gate (REVIEWED) |
| input | quantized_residual_2 | 17 | True | RUNTIME_INPUT | signed quantized residual envelope used by the reviewed C source gate | EXACT_SPEC: signed quantized residual envelope used by the reviewed C source gate (REVIEWED) |
| output | return_value | 1 | False | return_value | — | EXACT_SPEC: EXACT_SPEC (REVIEWED) |

## Spec -> C -> Contract -> RTL -> Verification -> Frame

- Spec: PASS (file:///Users/snow/Desktop/Display%20Stream%20Compression%20%28DSC%29/DSC%201.2a/DSC_v1.2a.pdf#page=82)
- C: UNPROVED (file:///Users/snow/Desktop/Display%20Stream%20Compression%20%28DSC%29/DSC%201.2a/DSC_model_20210623/dsc_codec.c#L457)
- Contract: PASS (../../library/contracts/usingmidpoint.json)
- RTL: PASS (file:///Users/snow/.svrt-network/dsc12a-regression/runs/20260803T014654Z-scale-2b8c6c5c/functions/usingmidpoint/accepted/candidate_01.sv)
- Verification: PASS (file:///private/tmp/dsc12a-regression-dashboard/library/verification/usingmidpoint.json)
- Frame: PASS (#frame-matrix)

- Spec status: AVAILABLE; PDF: /Users/snow/Desktop/Display Stream Compression (DSC)/DSC 1.2a/DSC_v1.2a.pdf
- C: dsc_codec.c (file:///Users/snow/Desktop/Display%20Stream%20Compression%20%28DSC%29/DSC%201.2a/DSC_model_20210623/dsc_codec.c#L457) lines 457-476

## Candidates, mutations, and counterexamples

- Candidates passed: 1/2
- Vectors: 385344, shards 4/4, verification FORMAL_EQUIVALENT
- Mutation evidence: 0/5, planned 5 (planned mutation cases; per-case result receipt not recorded)

| Stage | Candidate | Expected | Actual | Inputs |
|---|---|---|---|---|
| generator_cache | candidate_02 | 0 | 1 | [0, 0, 0, 0, 0, 8, 8, 8, 8, 8, 0, 0, 0, 0, 0] |

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
| contract | 46c31f1a781d9f532c5509d7dfe9f834be86693e1736754aaff40fc7c1e95abf |
| rtl | fc765032b32c15013196fa87328b8692da41071277c4bdd13ffb941c86132ab8 |
| promotion | PASS; immutable=True; stale=False |

### Strategy history

| Run | Decision | Tier | Rationale |
|---|---|---|---|
| 20260802T062208Z-0ad45a41 | enqueue | — | user-authorized large-scale batch; each discovered contract has an independent flow worktree |
| 20260802T225324Z-scale-dc5543ab | planned | cheap | explicit scale batch from facts-driven GENERATION_READY plan |
| 20260802T225324Z-scale-dc5543ab | selected | cheap | explicit scale batch; current facts/spec plan; independent contract flow worktrees; no SVRT |
| 20260802T230757Z-scale-7a24e3ac | planned | cheap | explicit scale batch from facts-driven GENERATION_READY plan |
| 20260802T230757Z-scale-7a24e3ac | selected | cheap | explicit scale batch; current facts/spec plan; independent contract flow worktrees; no SVRT |
| 20260803T013704Z-05a52482 | enqueue | — | user-authorized large-scale batch; each discovered contract has an independent flow worktree |
| 20260803T014654Z-scale-2b8c6c5c | planned | cheap | explicit scale batch from facts-driven GENERATION_READY plan |
| 20260803T014654Z-scale-2b8c6c5c | selected | cheap | explicit scale batch; current facts/spec plan; independent contract flow worktrees; no SVRT |

## Run comparison

| Run | Status | Candidates | Frames | Vectors | Change |
|---|---|---|---|---:|---|
| 20260802T225324Z-scale-dc5543ab | PASS | 1/2 | 3/3 | 385344 |  |
| 20260802T230757Z-scale-7a24e3ac | PASS | 1/2 | 3/3 | 385344 |  |
| 20260803T014654Z-scale-2b8c6c5c | PASS | 1/2 | 3/3 | 385344 | current |
