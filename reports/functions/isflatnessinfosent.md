# IsFlatnessInfoSent (isflatnessinfosent)

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
| input | qp | 5 | False | qp | Table 6-2 masterQp rows | EXACT_SPEC: Table 6-2 masterQp rows (REVIEWED) |
| input | flatness_min_qp | 5 | False | CONFIG_STATIC | PPS36[4:0] unsigned field | EXACT_SPEC: PPS36[4:0] unsigned field (REVIEWED) |
| input | flatness_max_qp | 5 | False | CONFIG_STATIC | PPS37[4:0] unsigned field | EXACT_SPEC: PPS37[4:0] unsigned field (REVIEWED) |
| output | return_value | 1 | False | return_value | — | EXACT_SPEC: EXACT_SPEC (REVIEWED) |

## Spec -> C -> Contract -> RTL -> Verification -> Frame

- Spec: PASS (file:///Users/snow/Desktop/Display%20Stream%20Compression%20%28DSC%29/DSC%201.2a/DSC_v1.2a.pdf#page=54)
- C: PASS (https://github.com/erickaoshoulin/dsc-1-2a-rust-port/blob/f26ecb2afa83aa9f0cc608b5b7c2742901ee9207/dsc_codec.c#L1116-L1119)
- Contract: PASS (../../library/contracts/isflatnessinfosent.json)
- RTL: PASS (file:///Users/snow/.svrt-network/dsc12a-regression/runs/20260803T014654Z-scale-2b8c6c5c/functions/isflatnessinfosent/accepted/candidate_01.sv)
- Verification: PASS (file:///private/tmp/dsc12a-regression-dashboard/library/verification/isflatnessinfosent.json)
- Frame: PASS (#frame-matrix)

- Spec status: AVAILABLE; PDF: /Users/snow/Desktop/Display Stream Compression (DSC)/DSC 1.2a/DSC_v1.2a.pdf
- C: dsc_codec.c (https://github.com/erickaoshoulin/dsc-1-2a-rust-port/blob/f26ecb2afa83aa9f0cc608b5b7c2742901ee9207/dsc_codec.c#L1116-L1119) lines 1116-1119

## Candidates, mutations, and counterexamples

- Candidates passed: 1/2
- Vectors: 32768, shards 4/4, verification EXHAUSTIVE_EQUIVALENT
- Mutation evidence: 0/5, planned 5 (planned mutation cases; per-case result receipt not recorded)

| Stage | Candidate | Expected | Actual | Inputs |
|---|---|---|---|---|
| generator_cache | candidate_02 | 1 | 0 | [0, 0, 0] |

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
| contract | bf7447eb0d360538c6dffdacf94982d7b1671af91edb93db9435bc43f539818d |
| rtl | 0a4b0d5ee2f45598e3ea1859102a42e3fa2ef66aba94e7049fc1d47876a5c07e |
| promotion | PASS; immutable=True; stale=False |

### Strategy history

| Run | Decision | Tier | Rationale |
|---|---|---|---|
| 20260802T062208Z-0ad45a41 | enqueue | — | user-authorized large-scale batch; each discovered contract has an independent flow worktree |
| 20260802T102758Z-scale-45761593 | planned | strong | explicit scale batch from facts-driven GENERATION_READY plan |
| 20260802T102758Z-scale-45761593 | selected | strong | explicit scale batch; current facts/spec plan; independent contract flow worktrees; no SVRT |
| 20260802T131813Z-scale-4f72935f | planned | strong | explicit scale batch from facts-driven GENERATION_READY plan |
| 20260802T131813Z-scale-4f72935f | selected | strong | explicit scale batch; current facts/spec plan; independent contract flow worktrees; no SVRT |
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
| 20260802T102758Z-scale-45761593 | PASS | 1/2 | 3/3 | 32768 |  |
| 20260802T131813Z-scale-4f72935f | PASS | 1/2 | 3/3 | 32768 |  |
| 20260802T133447Z-scale-4b440064 | PASS | 1/2 | 3/3 | 32768 |  |
| 20260802T230757Z-scale-7a24e3ac | PASS | 1/2 | 3/3 | 32768 |  |
| 20260803T014654Z-scale-2b8c6c5c | PASS | 1/2 | 3/3 | 32768 | current |
