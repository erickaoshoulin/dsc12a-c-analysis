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
