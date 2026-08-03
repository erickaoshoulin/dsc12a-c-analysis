# Qp2Qlevel (qp2qlevel)

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
| input | cpnt | 2 | False | cpnt | DSC component index domain for native 4:4:4/4:2:2/4:2:0 container components | EXACT_SPEC: DSC component index domain for native 4:4:4/4:2:2/4:2:0 container components (REVIEWED) |
| input | qp | 5 | False | qp | Table 6-2 masterQp rows, constrained by the selected bits_per_component table row | EXACT_SPEC: Table 6-2 masterQp rows, constrained by the selected bits_per_component table row (REVIEWED) |
| input | bits_per_component | 5 | False | bits_per_component | DSC supported component bit depths | EXACT_SPEC: DSC supported component bit depths (REVIEWED) |
| input | convert_rgb | 1 | False | convert_rgb | PPS convert_rgb flag | EXACT_SPEC: PPS convert_rgb flag (REVIEWED) |
| input | dsc_version_minor | 2 | False | dsc_version_minor | DSC minor-version branch domain used by the C model | EXACT_SPEC: DSC minor-version branch domain used by the C model (REVIEWED) |
| input | native_420 | 1 | False | native_420 | PPS native_420 flag | EXACT_SPEC: PPS native_420 flag (REVIEWED) |
| output | return_value | 5 | False | return_value | — | EXACT_SPEC: EXACT_SPEC (REVIEWED) |

## Spec -> C -> Contract -> RTL -> Verification -> Frame

- Spec: PASS (file:///Users/snow/Desktop/Display%20Stream%20Compression%20%28DSC%29/DSC%201.2a/DSC_v1.2a.pdf#page=114)
- C: UNPROVED (file:///Users/snow/Desktop/Display%20Stream%20Compression%20%28DSC%29/DSC%201.2a/DSC_model_20210623/codec_main.c#L816)
- Contract: PASS (../../library/contracts/qp2qlevel.json)
- RTL: PASS (file:///Users/snow/.svrt-network/dsc12a-regression/runs/20260803T014654Z-scale-2b8c6c5c/functions/qp2qlevel/accepted/candidate_01.sv)
- Verification: PASS (file:///private/tmp/dsc12a-regression-dashboard/library/verification/qp2qlevel.json)
- Frame: PASS (#frame-matrix)

- Spec status: AVAILABLE; PDF: /Users/snow/Desktop/Display Stream Compression (DSC)/DSC 1.2a/DSC_v1.2a.pdf
- C: codec_main.c (file:///Users/snow/Desktop/Display%20Stream%20Compression%20%28DSC%29/DSC%201.2a/DSC_model_20210623/codec_main.c#L816) lines 816-844

## Candidates, mutations, and counterexamples

- Candidates passed: 1/2
- Vectors: 5760, shards 4/4, verification EXHAUSTIVE_EQUIVALENT
- Mutation evidence: 0/5, planned 5 (planned mutation cases; per-case result receipt not recorded)

| Stage | Candidate | Expected | Actual | Inputs |
|---|---|---|---|---|
| generator_cache | candidate_02 | 0 | 1 | [0, 0, 8, 0, 0, 0] |

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
| contract | ac55b700324881611f728c9419b69341ef1592de9753de719c3a3109d0c3d026 |
| rtl | 18f078d82f020604fbcae57261373e69e9291f7757f81585163bb47fa1d893df |
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
| 20260802T213843Z-scale-41855a25 | PASS | 1/2 | 3/3 | 5760 |  |
| 20260802T230757Z-scale-7a24e3ac | PASS | 1/2 | 3/3 | 5760 |  |
| 20260803T014654Z-scale-2b8c6c5c | PASS | 1/2 | 3/3 | 5760 | current |
