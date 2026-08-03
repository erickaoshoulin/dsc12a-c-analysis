# DSC analysis progress

This handoff is isolated from SVRT. The local PDF and upstream C model were read-only inputs; no upstream source or PDF was copied or modified.

## Gates

- C clean build/smoke: `PASS`; golden smoke: `2fe0f356fa9c0a008dd3b1500ebb6af2782e2acc9c1a37718f9f5a1835408797`
- PDF extraction: `724c0979b0a04bb9a5ad7143755bf6fab4bf8cf9598d24a536a5048a66e2aecd`; anchors: `358` / page count recorded in `spec/anchors.json`
- Exact links before/after: `53` -> `53`; shared MN IDs exact: `23`

## Coverage

- LLVM instrumented smoke: `PASS`; functions: `194`; executed: `78`; static-but-uncovered: `102`
- Eligibility after dynamic coverage: `10`

### Candidate ranking before coverage

1. `FindMidpoint` — score `100.0`
2. `IsFlatnessInfoSent` — score `100.0`
3. `MapQpToQlevel` — score `100.0`
4. `PredictSize` — score `100.0`
5. `QuantizeResidual` — score `100.0`
6. `SampToLineBuf` — score `100.0`
7. `SamplePredict` — score `100.0`
8. `EscapeCodeSize` — score `99.95`
9. `MaxResidualSize` — score `99.95`
10. `GetQpAdjPredSize` — score `99.9`

### Candidate ranking after coverage

1. `FindMidpoint` — score `100.0`
2. `IsFlatnessInfoSent` — score `100.0`
3. `MapQpToQlevel` — score `100.0`
4. `PredictSize` — score `100.0`
5. `QuantizeResidual` — score `100.0`
6. `SampToLineBuf` — score `100.0`
7. `SamplePredict` — score `100.0`
8. `EscapeCodeSize` — score `99.95`
9. `MaxResidualSize` — score `99.95`
10. `GetQpAdjPredSize` — score `99.9`

## Three contracts

- `findmidpoint`: `FindMidpoint` at `dsc_codec.c:906`; leaf `True`; coverage `EXECUTED`
  - exact spec links: `2`; unresolved obligations: `none`
- `isflatnessinfosent`: `IsFlatnessInfoSent` at `dsc_codec.c:1116`; leaf `True`; coverage `EXECUTED`
  - exact spec links: `0`; unresolved obligations: `parameter:qp, field:dsc_cfg_t.flatness_max_qp, field:dsc_cfg_t.flatness_min_qp`
- `mapqptoqlevel`: `MapQpToQlevel` at `dsc_codec.c:221`; leaf `True`; coverage `EXECUTED`
  - exact spec links: `2`; unresolved obligations: `parameter:qp, field:dsc_cfg_t.dsc_version_minor, field:dsc_cfg_t.native_420, field:dsc_state_t.quantTableChroma, field:dsc_state_t.quantTableLuma`
- `predictsize`: `PredictSize` at `dsc_codec.c:1476`; leaf `True`; coverage `EXECUTED`
  - exact spec links: `0`; unresolved obligations: `none`
- `quantizeresidual`: `QuantizeResidual` at `dsc_codec.c:245`; leaf `True`; coverage `EXECUTED`
  - exact spec links: `2`; unresolved obligations: `parameter:e`
- `samplepredict`: `SamplePredict` at `dsc_codec.c:308`; leaf `True`; coverage `EXECUTED`
  - exact spec links: `8`; unresolved obligations: `parameter:hPos, parameter:predType, parameter:qLevel, parameter:unit, field:dsc_state_t.quantizedResidual, field:dsc_state_t.unitCType`
- `samptolinebuf`: `SampToLineBuf` at `dsc_codec.c:2036`; leaf `True`; coverage `EXECUTED`
  - exact spec links: `4`; unresolved obligations: `parameter:x, field:dsc_cfg_t.linebuf_depth`

## First RTL slice

- Chosen `findmidpoint` / `FindMidpoint` because it has `2` exact spec links, no unresolved obligations, and a finite legal domain.
- Exhaustive legal-domain vectors: `8207360`
- `candidate_01` (reference): `EXHAUSTIVE_EQUIVALENT`
- `candidate_02` (signedness): `COUNTEREXAMPLE`; smallest counterexample `{'actual': 32767, 'cpnt': 0, 'cpnt_bit_depth': 16, 'expected': 32769, 'left_recon': 32769, 'qlevel': 1}`
- `candidate_03` (boundary): `COUNTEREXAMPLE`; smallest counterexample `{'actual': 128, 'cpnt': 0, 'cpnt_bit_depth': 8, 'expected': 129, 'left_recon': 1, 'qlevel': 1}`
- `candidate_04` (off_by_one): `COUNTEREXAMPLE`; smallest counterexample `{'actual': 129, 'cpnt': 0, 'cpnt_bit_depth': 8, 'expected': 128, 'left_recon': 1, 'qlevel': 0}`
- mutation `array-index`: `COUNTEREXAMPLE`; smallest counterexample `{'actual': 256, 'cpnt': 1, 'cpnt_bit_depth': 8, 'expected': 128, 'left_recon': 0, 'qlevel': 0}`

## Recommendation

Resolve the remaining obligations in `isflatnessinfosent`, `mapqptoqlevel`, `quantizeresidual`, `samplepredict`, `samptolinebuf`, then repeat the same C-oracle/Verilator exhaustive flow. The selected `FindMidpoint` reference candidate is the promoted result; all deliberate negative variants remain visible as counterexamples.

## Receipts

- [coverage/coverage.json](../coverage/coverage.json)
- [contracts/proposed](../contracts/proposed)
- [verification/verification-receipt.json](../verification/verification-receipt.json)
- [traceability/traceability.json](../traceability/traceability.json)
