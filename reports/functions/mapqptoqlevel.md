# MapQpToQlevel (mapqptoqlevel)

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
| input | cpnt | 2 | False | cpnt | dsc_state_t component index domain | EXACT_SPEC: dsc_state_t component index domain (REVIEWED) |
| input | qp | 5 | False | qp | Table 6-2 masterQp rows | EXACT_SPEC: Table 6-2 masterQp rows (REVIEWED) |
| input | dsc_version_minor | 2 | False | CONFIG_STATIC | DSC 1.1/1.2 version branches used by the normative mapping rule | EXACT_SPEC: DSC 1.1/1.2 version branches used by the normative mapping rule (REVIEWED) |
| input | native_420 | 1 | False | CONFIG_STATIC | PPS native_420 flag | EXACT_SPEC: PPS native_420 flag (REVIEWED) |
| input | cpntBitDepth_0 | 5 | False | CONFIG_STATIC | DSC supported component bit depths | EXACT_SPEC: DSC supported component bit depths (REVIEWED) |
| input | cpntBitDepth_1 | 5 | False | CONFIG_STATIC | DSC supported component bit depths | EXACT_SPEC: DSC supported component bit depths (REVIEWED) |
| input | qlevel_luma | 5 | False | TABLE_LOOKUP_LUMA | Table 6-2 qLevelY output domain | EXACT_SPEC: Table 6-2 qLevelY output domain (REVIEWED) |
| input | qlevel_chroma | 5 | False | TABLE_LOOKUP_CHROMA | Table 6-2 qLevelC output domain | EXACT_SPEC: Table 6-2 qLevelC output domain (REVIEWED) |
| output | return_value | 5 | False | return_value | — | EXACT_SPEC: EXACT_SPEC (REVIEWED) |

## Spec -> C -> Contract -> RTL -> Verification -> Frame

- Spec: PASS (file:///Users/snow/Desktop/Display%20Stream%20Compression%20%28DSC%29/DSC%201.2a/DSC_v1.2a.pdf#page=113)
- C: PASS (https://github.com/erickaoshoulin/dsc-1-2a-rust-port/blob/f26ecb2afa83aa9f0cc608b5b7c2742901ee9207/dsc_codec.c#L221-L238)
- Contract: PASS (../../library/contracts/mapqptoqlevel.json)
- RTL: PASS (file:///Users/snow/.svrt-network/dsc12a-regression/runs/20260803T014654Z-scale-2b8c6c5c/functions/mapqptoqlevel/accepted/candidate_01.sv)
- Verification: PASS (file:///private/tmp/dsc12a-regression-dashboard/library/verification/mapqptoqlevel.json)
- Frame: PASS (#frame-matrix)

- Spec status: AVAILABLE; PDF: /Users/snow/Desktop/Display Stream Compression (DSC)/DSC 1.2a/DSC_v1.2a.pdf
- C: dsc_codec.c (https://github.com/erickaoshoulin/dsc-1-2a-rust-port/blob/f26ecb2afa83aa9f0cc608b5b7c2742901ee9207/dsc_codec.c#L221-L238) lines 221-238

## Candidates, mutations, and counterexamples

- Candidates passed: 1/2
- Vectors: 5548800, shards 4/4, verification EXHAUSTIVE_EQUIVALENT
- Mutation evidence: 0/5, planned 5 (planned mutation cases; per-case result receipt not recorded)

| Stage | Candidate | Expected | Actual | Inputs |
|---|---|---|---|---|
| generator_cache | candidate_02 | 0 | 1 | [0, 0, 0, 0, 8, 8, 0, 0] |

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
| contract | ac022d1dc609d17daa512d4e387a221dfa8c2d16311e526c36e7bb40445d2371 |
| rtl | 5dda9dc25483193295e7af8abbd927b209f8e9715f2f4791864200f2fc0a3334 |
| promotion | PASS; immutable=True; stale=False |

### Strategy history

| Run | Decision | Tier | Rationale |
|---|---|---|---|
| 20260802T062208Z-0ad45a41 | enqueue | — | user-authorized large-scale batch; each discovered contract has an independent flow worktree |
| 20260802T113444Z-scale-8ac90c28 | planned | strong | explicit scale batch from facts-driven GENERATION_READY plan |
| 20260802T113444Z-scale-8ac90c28 | selected | strong | explicit scale batch; current facts/spec plan; independent contract flow worktrees; no SVRT |
| 20260802T131813Z-scale-4f72935f | planned | strong | explicit scale batch from facts-driven GENERATION_READY plan |
| 20260802T131813Z-scale-4f72935f | selected | strong | explicit scale batch; current facts/spec plan; independent contract flow worktrees; no SVRT |
| 20260802T133447Z-scale-4b440064 | planned | strong | explicit scale batch from facts-driven GENERATION_READY plan |
| 20260802T133447Z-scale-4b440064 | selected | strong | explicit scale batch; current facts/spec plan; independent contract flow worktrees; no SVRT |
| 20260802T230757Z-scale-7a24e3ac | planned | strong | explicit scale batch from facts-driven GENERATION_READY plan |
| 20260802T230757Z-scale-7a24e3ac | selected | strong | explicit scale batch; current facts/spec plan; independent contract flow worktrees; no SVRT |
| 20260803T013704Z-05a52482 | enqueue | — | user-authorized large-scale batch; each discovered contract has an independent flow worktree |
| 20260803T013704Z-05a52482 | planned | strong | one GENERATION_READY table/config leaf when available |
| 20260803T013704Z-05a52482 | selected | strong | pilot only; no scale jobs are enqueued |
| 20260803T014654Z-scale-2b8c6c5c | planned | strong | explicit scale batch from facts-driven GENERATION_READY plan |
| 20260803T014654Z-scale-2b8c6c5c | selected | strong | explicit scale batch; current facts/spec plan; independent contract flow worktrees; no SVRT |

## Run comparison

| Run | Status | Candidates | Frames | Vectors | Change |
|---|---|---|---|---:|---|
| 20260802T113444Z-scale-8ac90c28 | PASS | 1/2 | 3/3 | 5548800 |  |
| 20260802T131813Z-scale-4f72935f | PASS | 1/2 | 3/3 | 5548800 |  |
| 20260802T133447Z-scale-4b440064 | PASS | 1/2 | 3/3 | 5548800 |  |
| 20260802T230757Z-scale-7a24e3ac | PASS | 1/2 | 3/3 | 5548800 |  |
| 20260803T013704Z-05a52482 | PASS | 1/2 | 3/3 | 5548800 |  |
| 20260803T014654Z-scale-2b8c6c5c | PASS | 1/2 | 3/3 | 5548800 | current |
