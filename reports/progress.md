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

## Production-domain promotion

- `samplepredict` / `SamplePredict` is now the tenth stable library leaf.
- The reviewed boundary keeps the C line-buffer state at the caller and exposes only the exact relative taps required by MMAP, left prediction, and block prediction.
- C/RTL differential coverage passed `25,960,080` legal-domain vectors across `8` shards; the structural formal gate passed `1,002/1,002` partitions with `proof_complete=true`.
- The deliberate mutation remains rejected with a differential and formal counterexample; the stable RTL and compact promotion receipt are in `library/`.

## Ten-leaf parallel refresh

- The tool/spec-ready stable frontier was refreshed in one bounded parallel run with `10` selected contracts and `8` vector shards per leaf.
- All ten leaves returned `PROMOTED`: nine `EXHAUSTIVE_EQUIVALENT` leaves plus the reviewed `SamplePredict` `FORMAL_EQUIVALENT` leaf.
- The run executed `105,807,728` C/RTL vectors in total; every leaf passed dependency composition, `C_ONLY`, `SHADOW`, `RTL_RETURN`, frame/SHA, and source gates, and each deliberate `candidate_02` was retained as an expected rejection.
- The refresh also materialized the three stable manifest leaves that were not present in `contracts/locked`, using their tool facts and reviewed PDF/source overrides rather than a hardcoded target list.
- The executable promotion stage materialized all ten canonical RTL modules, contracts, verification receipts, and manifest entries under a library write lock; each result records `library_promotion: PASS` and any replaced RTL is archived.

## Configuration-library extension

- The facts-driven frontier selected `Qp2Qlevel` from `codec_main.c:816-844` as a production-reachable, pure/combinational `CONFIG` helper. It was not selected by a function-name allowlist.
- DSC 1.2a Table 6-2 (PDF page `114`, section `6.8.6`) was added as a reviewed exact link. The contract carries the normative luma/chroma rows, the version-2 chroma adjustment, and a row-constrained `qp_table` exhaustive strategy.
- Because the helper is configuration plumbing rather than observable codec output, it entered through reviewed `CONFIG_LIBRARY` admission with `role: CONFIG_HELPER` and `non_dut_boundary: true`. This does not waive effects, boundedness, coverage, dependency, source, or C-oracle gates.
- The C oracle now compiles all model translation units, including `codec_main.c` with its CLI `main` renamed for the wrapper link. The immutable C build/smoke gate remains `PASS` with golden hash `2fe0f356fa9c0a008dd3b1500ebb6af2782e2acc9c1a37718f9f5a1835408797`.
- `Qp2Qlevel` passed `5,760` exhaustive C/RTL vectors across `8` shards, C_ONLY/SHADOW/RTL_RETURN, dependency, frame/SHA, source, and strict Verilator lint gates. The deliberately mutated candidate was rejected by the first-vector counterexample.

## Thirteen-component parallel refresh

- The reviewed stable frontier now contains `13` promoted components: `12` exhaustive-equivalent leaves plus `SamplePredict` as the reviewed `FORMAL_EQUIVALENT` relative-window leaf.
- The final refresh executed `106,010,095` C/RTL vectors across `104` parallel shards. Every component passed dependency composition, C_ONLY, SHADOW, RTL_RETURN, frame/SHA, source, and exact-spec gates; deliberate negative candidates remained expected rejections.
- The stable manifest now includes `qp2qlevel` as a reusable configuration-library primitive while stateful callers, line-buffer storage, and other non-DUT C logic remain outside the RTL library.

## Flatness-window promotion

- The next candidate was selected from Clang identity, coverage, exact PDF links, and reviewed domain data; no function-name allowlist was added. Its exact authority is DSC 1.2a section `6.8.5.1` and Figure `6-19` (PDF page `111`), with the direct `MapQpToQlevel` dependency already promoted.
- The reviewed `flatness_window` contract keeps the C line storage at the caller boundary and exposes four lanes × seven original-pixel taps. Figure 6-19 check-1 offsets are `0..3`, check-2 offsets are `1..6`; Table 6-2 and the native-420/version qLevel relation are contract data.
- The concrete suite passed `575,552` vectors across `8` shards, including `172,800` structural cases, line-end probes, per-tap boundaries, and pairwise tap cases. Candidate RTL compiled with Verilator; the independent Verilator-AST/Z3 proof returned `PASS` with `proof_complete=true`.
- The C oracle compiled all `11` translation units. `C_ONLY`, `SHADOW`, and `RTL_RETURN` passed all three frame scenarios. The deliberately mutated candidate was rejected by concrete and formal counterexamples. Unconfigured component lanes are guarded in the C adapter so `origLine` is never dereferenced outside `numComponents`.
- `isorigflathindex` is promoted as the fourteenth stable component; the stable library now has `14` leaves while stateful line storage and non-DUT caller logic remain outside RTL.

## Frontier re-audit

- A fresh facts/spec `plan` after promotion returned `new_candidates: []` and selected no new contract. The next ranked lowercase `getbits` fact is not bounded and has unknown timing, while the uppercase `GetBits` fact is stateful and carries logging/state-write effects.
- Neither is admitted to the RTL library without a new exact spec contract that proves a bounded, combinational DUT slice. The C model remains the reference for this frontier; no non-DUT/stateful logic was converted just to keep the queue moving.

## Recommendation

Continue by re-reading the tool-ranked frontier for a new reviewed leaf or composite whose direct callees are already PASS, then repeat the same C-oracle/Verilator/formal flow. The current fourteen-component stable frontier is revalidated; its static Eva/From limitations remain recorded separately and do not weaken the executable RTL gates. Deliberate negative variants stay visible as counterexamples.

## Receipts

- [coverage/coverage.json](../coverage/coverage.json)
- [contracts/proposed](../contracts/proposed)
- [verification/verification-receipt.json](../verification/verification-receipt.json)
- [traceability/traceability.json](../traceability/traceability.json)
