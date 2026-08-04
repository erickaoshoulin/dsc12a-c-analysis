# Contract review

Contracts are generated from tool-discovered production/output leaf functions; no function name allowlist is used.

- Coverage executed functions: 78
- Static-but-uncovered functions: 102
- Exact PDF/C links: 53
- Selection cap: 10; frontier: 10; leaf contracts selected: 7
- Dependency-deferred candidates: 3

## findmidpoint — `FindMidpoint`

- selection rank: 1; score: 100.0; leaf: True
- coverage: `EXECUTED`; execution count: 2426112
- source: `dsc_codec.c:906-914`
- exact spec links: 2
- unresolved obligations: none

  - `EXACT` `pdf:model-note:MN_MIDPOINT_PRED:p080` page 80
  - `EXACT` `pdf:section:6.4.3` page 80

## isflatnessinfosent — `IsFlatnessInfoSent`

- selection rank: 2; score: 100.0; leaf: True
- coverage: `EXECUTED`; execution count: 275863
- source: `dsc_codec.c:1116-1119`
- exact spec links: 0
- unresolved obligations: parameter:qp, field:dsc_cfg_t.flatness_max_qp, field:dsc_cfg_t.flatness_min_qp

  - `REVIEWED` `pdf:section:4.3` page 62
  - `REVIEWED` `pdf:section:6.6.3` page 94

## mapqptoqlevel — `MapQpToQlevel`

- selection rank: 3; score: 100.0; leaf: True
- coverage: `EXECUTED`; execution count: 7561479
- source: `dsc_codec.c:221-238`
- exact spec links: 2
- unresolved obligations: parameter:qp, field:dsc_cfg_t.dsc_version_minor, field:dsc_cfg_t.native_420, field:dsc_state_t.quantTableChroma, field:dsc_state_t.quantTableLuma

  - `EXACT` `pdf:model-note:MN_MAP_QP_TO_QLEVEL:p113` page 113
  - `EXACT` `pdf:section:6.8.6` page 113
  - `REVIEWED` `pdf:table:6-2` page 114

## predictsize — `PredictSize`

- selection rank: 4; score: 100.0; leaf: True
- coverage: `EXECUTED`; execution count: 367218
- source: `dsc_codec.c:1476-1486`
- exact spec links: 0
- unresolved obligations: none

  - `REVIEWED` `pdf:section:6.4.5` page 83
  - `REVIEWED` `pdf:section:6.6.1` page 91

## quantizeresidual — `QuantizeResidual`

- selection rank: 5; score: 100.0; leaf: True
- coverage: `EXECUTED`; execution count: 2426112
- source: `dsc_codec.c:245-255`
- exact spec links: 2
- unresolved obligations: parameter:e

  - `EXACT` `pdf:model-note:MN_ENC_QUANTIZATION:p083` page 83
  - `EXACT` `pdf:section:6.4.5` page 83

## samptolinebuf — `SampToLineBuf`

- selection rank: 6; score: 100.0; leaf: True
- coverage: `EXECUTED`; execution count: 1334556
- source: `dsc_codec.c:2036-2049`
- exact spec links: 4
- unresolved obligations: parameter:x, field:dsc_cfg_t.linebuf_depth

  - `EXACT` `pdf:model-note:MN_LINE_STORAGE:p075` page 75
  - `EXACT` `pdf:section:6.3` page 75
  - `EXACT` `pdf:model-note:MN_LINE_STORAGE:p117` page 117
  - `EXACT` `pdf:section:7.4` page 117

## samplepredict — `SamplePredict`

- selection rank: 7; score: 100.0; leaf: True
- coverage: `EXECUTED`; execution count: 15870816
- source: `dsc_codec.c:308-383`
- exact spec links: 8
- unresolved obligations: parameter:hPos, parameter:predType, parameter:qLevel, parameter:unit, field:dsc_state_t.quantizedResidual, field:dsc_state_t.unitCType

  - `EXACT` `pdf:model-note:MN_MMAP:p076` page 76
  - `EXACT` `pdf:section:6.4.1` page 76
  - `EXACT` `pdf:model-note:MN_MMAP:p078` page 78
  - `EXACT` `pdf:section:6.4.1.1` page 78
  - `EXACT` `pdf:model-note:MN_BLOCK_PRED:p079` page 79
  - `EXACT` `pdf:model-note:MN_MMAP:p079` page 79
  - `EXACT` `pdf:section:6.4.1.2` page 79
  - `EXACT` `pdf:section:6.4.2` page 79

## Deferred dependency candidates

These candidates are tool-discovered and coverage-eligible, but they are not leaf contracts. They remain visible for a later dependency-aware batch and are not emitted as locked contracts.

### `EscapeCodeSize`

- candidate rank: 8; score: 99.95
- coverage: `EXECUTED`; execution count: 20889
- state: `DEPENDENCY_DEFERRED`
- direct source callees: `MapQpToQlevel`
- reason: direct source dependencies require dependency-aware contract work before caller selection

### `MaxResidualSize`

- candidate rank: 9; score: 99.95
- coverage: `EXECUTED`; execution count: 2181573
- state: `DEPENDENCY_DEFERRED`
- direct source callees: `MapQpToQlevel`
- reason: direct source dependencies require dependency-aware contract work before caller selection

### `GetQpAdjPredSize`

- candidate rank: 10; score: 99.9
- coverage: `EXECUTED`; execution count: 469602
- state: `DEPENDENCY_DEFERRED`
- direct source callees: `MapQpToQlevel`, `MaxResidualSize`
- reason: direct source dependencies require dependency-aware contract work before caller selection
