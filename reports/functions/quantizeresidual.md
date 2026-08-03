# QuantizeResidual (quantizeresidual)

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
| input | e | 17 | True | e | runtime sample-domain evidence for 16bpc residuals | EXACT_SPEC: runtime sample-domain evidence for 16bpc residuals (REVIEWED) |
| input | qlevel | 5 | False | qlevel | EXACT Table 6-2 qLevel domain | EXACT_SPEC: EXACT Table 6-2 qLevel domain (REVIEWED) |
| output | return_value | 17 | True | return_value | — | EXACT_SPEC: not recorded (REVIEWED) |

## Spec -> C -> Contract -> RTL -> Verification -> Frame

- Spec: PASS (file:///Users/snow/Desktop/Display%20Stream%20Compression%20%28DSC%29/DSC%201.2a/DSC_v1.2a.pdf#page=83)
- C: PASS (https://github.com/erickaoshoulin/dsc-1-2a-rust-port/blob/f26ecb2afa83aa9f0cc608b5b7c2742901ee9207/dsc_codec.c#L245-L255)
- Contract: PASS (../../library/contracts/quantizeresidual.json)
- RTL: PASS (file:///Users/snow/.svrt-network/dsc12a-regression/runs/20260803T014654Z-scale-2b8c6c5c/functions/quantizeresidual/accepted/candidate_01.sv)
- Verification: PASS (file:///private/tmp/dsc12a-regression-dashboard/library/verification/quantizeresidual.json)
- Frame: PASS (#frame-matrix)

- Spec status: AVAILABLE; PDF: /Users/snow/Desktop/Display Stream Compression (DSC)/DSC 1.2a/DSC_v1.2a.pdf
- C: dsc_codec.c (https://github.com/erickaoshoulin/dsc-1-2a-rust-port/blob/f26ecb2afa83aa9f0cc608b5b7c2742901ee9207/dsc_codec.c#L245-L255) lines 245-255

## Candidates, mutations, and counterexamples

- Candidates passed: 1/2
- Vectors: 2228207, shards 4/4, verification EXHAUSTIVE_EQUIVALENT
- Mutation evidence: 0/5, planned 5 (planned mutation cases; per-case result receipt not recorded)

| Stage | Candidate | Expected | Actual | Inputs |
|---|---|---|---|---|
| generator_cache | candidate_02 | -65535 | -65534 | [-65535, 0] |

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
| contract | fdd965df16f8ed6aab36d5bec2aa7f9e252ff7fcab4c5b51a3308ae106af7d0a |
| rtl | 7c9d729bbe1ac193b6f355b3d8281a92ab350a9c27a7717145fdea31a863d9cd |
| promotion | PASS; immutable=True; stale=False |

### Strategy history

| Run | Decision | Tier | Rationale |
|---|---|---|---|
| 20260802T062208Z-0ad45a41 | enqueue | — | user-authorized large-scale batch; each discovered contract has an independent flow worktree |
| 20260802T062208Z-0ad45a41 | planned | cheap | one newly GENERATION_READY arithmetic leaf; smallest acyclic dependency pair |
| 20260802T062208Z-0ad45a41 | requeue | — | manual resume after inspecting failed receipt |
| 20260802T062208Z-0ad45a41 | selected | cheap | pilot only; no scale jobs are enqueued |
| 20260802T093510Z-scale-22275ebc | planned | cheap | explicit scale batch from facts-driven GENERATION_READY plan |
| 20260802T093510Z-scale-22275ebc | selected | cheap | explicit scale batch; independent contract flow worktrees; no SVRT |
| 20260802T131813Z-scale-4f72935f | planned | cheap | explicit scale batch from facts-driven GENERATION_READY plan |
| 20260802T131813Z-scale-4f72935f | selected | cheap | explicit scale batch; current facts/spec plan; independent contract flow worktrees; no SVRT |
| 20260802T133447Z-scale-4b440064 | planned | cheap | explicit scale batch from facts-driven GENERATION_READY plan |
| 20260802T133447Z-scale-4b440064 | selected | cheap | explicit scale batch; current facts/spec plan; independent contract flow worktrees; no SVRT |
| 20260802T230757Z-scale-7a24e3ac | planned | cheap | explicit scale batch from facts-driven GENERATION_READY plan |
| 20260802T230757Z-scale-7a24e3ac | selected | cheap | explicit scale batch; current facts/spec plan; independent contract flow worktrees; no SVRT |
| 20260803T013704Z-05a52482 | enqueue | — | user-authorized large-scale batch; each discovered contract has an independent flow worktree |
| 20260803T014654Z-scale-2b8c6c5c | planned | cheap | explicit scale batch from facts-driven GENERATION_READY plan |
| 20260803T014654Z-scale-2b8c6c5c | selected | cheap | explicit scale batch; current facts/spec plan; independent contract flow worktrees; no SVRT |

## Run comparison

| Run | Status | Candidates | Frames | Vectors | Change |
|---|---|---|---|---:|---|
| 20260802T062208Z-0ad45a41 | PASS | 1/2 | 3/3 | 2228207 |  |
| 20260802T093510Z-scale-22275ebc | PASS | 1/2 | 3/3 | 2228207 |  |
| 20260802T131813Z-scale-4f72935f | PASS | 1/2 | 3/3 | 2228207 |  |
| 20260802T133447Z-scale-4b440064 | PASS | 1/2 | 3/3 | 2228207 |  |
| 20260802T230757Z-scale-7a24e3ac | PASS | 1/2 | 3/3 | 2228207 |  |
| 20260803T014654Z-scale-2b8c6c5c | PASS | 1/2 | 3/3 | 2228207 | current |
