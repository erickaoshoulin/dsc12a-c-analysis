# Contract review

Contracts are generated from tool-discovered production/output leaf functions; no function name allowlist is used.

- Coverage executed functions: 72
- Static-but-uncovered functions: 107
- Exact PDF/C links: 53

## findmidpoint — `FindMidpoint`

- selection rank: 1; score: 100.0; leaf: True
- coverage: `EXECUTED`; execution count: 124416
- source: `dsc_codec.c:906-914`
- exact spec links: 2
- unresolved obligations: none

  - `EXACT` `pdf:model-note:MN_MIDPOINT_PRED:p080` page 80
  - `EXACT` `pdf:section:6.4.3` page 80

## isflatnessinfosent — `IsFlatnessInfoSent`

- selection rank: 2; score: 100.0; leaf: True
- coverage: `EXECUTED`; execution count: 14021
- source: `dsc_codec.c:1116-1119`
- exact spec links: 0
- unresolved obligations: parameter:qp, field:dsc_cfg_t.flatness_max_qp, field:dsc_cfg_t.flatness_min_qp


## mapqptoqlevel — `MapQpToQlevel`

- selection rank: 3; score: 100.0; leaf: True
- coverage: `EXECUTED`; execution count: 404099
- source: `dsc_codec.c:221-238`
- exact spec links: 2
- unresolved obligations: parameter:qp, field:dsc_cfg_t.dsc_version_minor, field:dsc_cfg_t.native_420, field:dsc_state_t.quantTableChroma, field:dsc_state_t.quantTableLuma

  - `EXACT` `pdf:model-note:MN_MAP_QP_TO_QLEVEL:p113` page 113
  - `EXACT` `pdf:section:6.8.6` page 113

## predictsize — `PredictSize`

- selection rank: 4; score: 100.0; leaf: True
- coverage: `EXECUTED`; execution count: 17367
- source: `dsc_codec.c:1476-1486`
- exact spec links: 0
- unresolved obligations: none


## quantizeresidual — `QuantizeResidual`

- selection rank: 5; score: 100.0; leaf: True
- coverage: `EXECUTED`; execution count: 124416
- source: `dsc_codec.c:245-255`
- exact spec links: 2
- unresolved obligations: parameter:e

  - `EXACT` `pdf:model-note:MN_ENC_QUANTIZATION:p083` page 83
  - `EXACT` `pdf:section:6.4.5` page 83

## samptolinebuf — `SampToLineBuf`

- selection rank: 6; score: 100.0; leaf: True
- coverage: `EXECUTED`; execution count: 67068
- source: `dsc_codec.c:2036-2049`
- exact spec links: 4
- unresolved obligations: parameter:x, field:dsc_cfg_t.linebuf_depth

  - `EXACT` `pdf:model-note:MN_LINE_STORAGE:p075` page 75
  - `EXACT` `pdf:section:6.3` page 75
  - `EXACT` `pdf:model-note:MN_LINE_STORAGE:p117` page 117
  - `EXACT` `pdf:section:7.4` page 117
