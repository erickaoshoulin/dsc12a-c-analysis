# Regression summary

Selected run: 20260803T014654Z-scale-2b8c6c5c (PASS)
Storage: /Users/snow/.svrt-network/dsc12a-regression (ENV_ROOT)
SMB fallback: none

## Overview

| Measure | Result |
|---|---:|
| Functions passing | 16/16 |
| Candidate equivalence | 16/32 |
| Frame sanity | 48/48 |
| Vectors executed | 108011919 |
| Runs indexed | 20 |

## Source gate

- PDF: AVAILABLE; /Users/snow/Desktop/Display Stream Compression (DSC)/DSC 1.2a/DSC_v1.2a.pdf
- Source/build gate: PASS
- PDF and C source remain external/immutable inputs.

## Function results

| Function | Status | Stage | Candidates | Vectors | Unit/formal | Frame | Next action |
|---|---|---|---|---:|---|---|---|
| [EscapeCodeSize (escapecodesize)](functions/escapecodesize.md) | PASS | complete | 1/2 | 16320 | EXHAUSTIVE_EQUIVALENT | 3/3 | Review the accepted RTL and retain the recorded C_ONLY rollback/reference path. |
| [EstimateBitsForGroup (estimatebitsforgroup)](functions/estimatebitsforgroup.md) | PASS | complete | 1/2 | 1040928 | FORMAL_EQUIVALENT | 3/3 | Review the accepted RTL and retain the recorded C_ONLY rollback/reference path. |
| [FindMidpoint (findmidpoint)](functions/findmidpoint.md) | PASS | complete | 1/2 | 8207360 | EXHAUSTIVE_EQUIVALENT | 3/3 | Review the accepted RTL and retain the recorded C_ONLY rollback/reference path. |
| [FindResidualSize (findresidualsize)](functions/findresidualsize.md) | PASS | complete | 1/2 | 131071 | EXHAUSTIVE_EQUIVALENT | 3/3 | Review the accepted RTL and retain the recorded C_ONLY rollback/reference path. |
| [GetQpAdjPredSize (getqpadjpredsize)](functions/getqpadjpredsize.md) | PASS | complete | 1/2 | 14831616 | EXHAUSTIVE_EQUIVALENT | 3/3 | Review the accepted RTL and retain the recorded C_ONLY rollback/reference path. |
| [IsFlatnessInfoSent (isflatnessinfosent)](functions/isflatnessinfosent.md) | PASS | complete | 1/2 | 32768 | EXHAUSTIVE_EQUIVALENT | 3/3 | Review the accepted RTL and retain the recorded C_ONLY rollback/reference path. |
| [IsOrigFlatHIndex (isorigflathindex)](functions/isorigflathindex.md) | PASS | complete | 1/2 | 575552 | FORMAL_EQUIVALENT | 3/3 | Review the accepted RTL and retain the recorded C_ONLY rollback/reference path. |
| [MapQpToQlevel (mapqptoqlevel)](functions/mapqptoqlevel.md) | PASS | complete | 1/2 | 5548800 | EXHAUSTIVE_EQUIVALENT | 3/3 | Review the accepted RTL and retain the recorded C_ONLY rollback/reference path. |
| [MaxResidualSize (maxresidualsize)](functions/maxresidualsize.md) | PASS | complete | 1/2 | 27744000 | EXHAUSTIVE_EQUIVALENT | 3/3 | Review the accepted RTL and retain the recorded C_ONLY rollback/reference path. |
| [PredictSize (predictsize)](functions/predictsize.md) | PASS | complete | 1/2 | 4913 | EXHAUSTIVE_EQUIVALENT | 3/3 | Review the accepted RTL and retain the recorded C_ONLY rollback/reference path. |
| [Qp2Qlevel (qp2qlevel)](functions/qp2qlevel.md) | PASS | complete | 1/2 | 5760 | EXHAUSTIVE_EQUIVALENT | 3/3 | Review the accepted RTL and retain the recorded C_ONLY rollback/reference path. |
| [QuantizeResidual (quantizeresidual)](functions/quantizeresidual.md) | PASS | complete | 1/2 | 2228207 | EXHAUSTIVE_EQUIVALENT | 3/3 | Review the accepted RTL and retain the recorded C_ONLY rollback/reference path. |
| [SampToLineBuf (samptolinebuf)](functions/samptolinebuf.md) | PASS | complete | 1/2 | 21233664 | EXHAUSTIVE_EQUIVALENT | 3/3 | Review the accepted RTL and retain the recorded C_ONLY rollback/reference path. |
| [SamplePredict (samplepredict)](functions/samplepredict.md) | PASS | complete | 1/2 | 25960080 | FORMAL_EQUIVALENT | 3/3 | Review the accepted RTL and retain the recorded C_ONLY rollback/reference path. |
| [UsingMidpoint (usingmidpoint)](functions/usingmidpoint.md) | PASS | complete | 1/2 | 385344 | FORMAL_EQUIVALENT | 3/3 | Review the accepted RTL and retain the recorded C_ONLY rollback/reference path. |
| [ceil_log2 (ceil_log2)](functions/ceil_log2.md) | PASS | complete | 1/2 | 65536 | EXHAUSTIVE_EQUIVALENT | 3/3 | Review the accepted RTL and retain the recorded C_ONLY rollback/reference path. |

## Failure and blocker summary

The selected run has no function-level failure or blocker.

### Historical failures

| Run | Function | Status | Cause / counterexample |
|---|---|---|---|
| 20260802T124401Z-scale-e03da363 | GetQpAdjPredSize | INFRASTRUCTURE_FAILURE | current C-to-RTL flow failed: FAIL |
| 20260802T122524Z-scale-ddc3d67c | GetQpAdjPredSize | INFRASTRUCTURE_FAILURE | current C-to-RTL flow failed: FAIL |
| 20260802T122049Z-scale-d2066dca | GetQpAdjPredSize | INFRASTRUCTURE_FAILURE | current C-to-RTL flow failed: FAIL |
| 20260802T120021Z-scale-92d39833 | MaxResidualSize | INFRASTRUCTURE_FAILURE | current C-to-RTL flow failed: FAIL |
| 20260802T115152Z-scale-b9191e5c | MaxResidualSize | INFRASTRUCTURE_FAILURE | current C-to-RTL flow failed: FAIL |

## Run history

| Run | Profile | Status | Functions | Candidates | Frames | Vectors |
|---|---|---|---:|---|---|---:|
| 20260803T014654Z-scale-2b8c6c5c | scale | PASS | 16 | 16/32 | 48/48 | 108011919 |
| 20260803T013704Z-05a52482 | pilot | PASS | 2 | 2/4 | 6/6 | 13756160 |
| 20260802T230757Z-scale-7a24e3ac | scale | PASS | 15 | 15/30 | 45/45 | 106970991 |
| 20260802T225324Z-scale-dc5543ab | scale | PASS | 1 | 1/2 | 3/3 | 385344 |
| 20260802T213843Z-scale-41855a25 | scale | PASS | 5 | 5/10 | 15/15 | 26737999 |
| 20260802T133447Z-scale-4b440064 | scale | PASS | 9 | 9/18 | 27/27 | 79847648 |
| 20260802T131813Z-scale-4f72935f | scale | PASS | 7 | 7/14 | 21/21 | 37272032 |
| 20260802T125235Z-scale-31386cb4 | scale | PASS | 1 | 1/2 | 3/3 | 14831616 |
| 20260802T124401Z-scale-e03da363 | scale | FAIL | 1 | 0/0 | 0/0 | 0 |
| 20260802T122524Z-scale-ddc3d67c | scale | FAIL | 1 | 0/0 | 0/0 | 0 |
| 20260802T122049Z-scale-d2066dca | scale | FAIL | 1 | 0/0 | 0/0 | 0 |
| 20260802T120730Z-scale-e3f4cdd8 | scale | PASS | 1 | 1/2 | 3/3 | 27744000 |
| 20260802T120021Z-scale-92d39833 | scale | FAIL | 1 | 0/0 | 0/0 | 0 |
| 20260802T115152Z-scale-b9191e5c | scale | FAIL | 2 | 1/2 | 3/3 | 16320 |
| 20260802T113444Z-scale-8ac90c28 | scale | PASS | 1 | 1/2 | 3/3 | 5548800 |
| 20260802T111122Z-scale-ccc96e95 | scale | PASS | 1 | 1/2 | 3/3 | 4913 |
| 20260802T105600Z-scale-67d0be81 | scale | PASS | 1 | 1/2 | 3/3 | 21233664 |
| 20260802T102758Z-scale-45761593 | scale | PASS | 1 | 1/2 | 3/3 | 32768 |
| 20260802T093510Z-scale-22275ebc | scale | PASS | 2 | 2/4 | 6/6 | 10435567 |
| 20260802T062208Z-0ad45a41 | pilot | PASS | 2 | 2/4 | 4/6 | 2228207 |

## How to open

- Open dashboard/index.html for the static overview.
- Use dashboard/functions/<contract-id>.html for full traceability.
- Use path-map.json and library/index.json to resolve legacy paths and stale accepted artifacts.
