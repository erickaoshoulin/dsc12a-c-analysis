# CI/CD pipeline summary

- Agent: generic dependency-aware C-to-RTL migration
- Source hash: `1cd2ac33e983d1489b2fcc5e138324efba18069db5a6bbe72f6cce3b7d8b9cdf`
- Spec hash: `724c0979b0a04bb9a5ad7143755bf6fab4bf8cf9598d24a536a5048a66e2aecd`
- Baseline SHA-256: `2fe0f356fa9c0a008dd3b1500ebb6af2782e2acc9c1a37718f9f5a1835408797`
- Model calls: `0`

## Contract states

- `findmidpoint`: `PROMOTED` / `PASS`
- `isflatnessinfosent`: `DISCOVERED` / `BLOCKED` — arithmetic_semantics; field:dsc_cfg_t.flatness_max_qp; field:dsc_cfg_t.flatness_min_qp; interface:flatness_max_qp; interface:flatness_min_qp; interface:qp; interface:return_value; no_exact_spec_link; parameter:qp
- `mapqptoqlevel`: `DISCOVERED` / `BLOCKED` — arithmetic_semantics; field:dsc_cfg_t.dsc_version_minor; field:dsc_cfg_t.native_420; field:dsc_state_t.quantTableChroma; field:dsc_state_t.quantTableLuma; interface:dsc_version_minor; interface:native_420; interface:qp; interface:quantTableChroma; interface:quantTableLuma; interface:return_value; parameter:qp

## Planner

- Ready contracts: `findmidpoint`
- Blocked contracts: `isflatnessinfosent, mapqptoqlevel`
- Parallel batches: `[["findmidpoint"]]`

## Evidence

- `ci/dag.json` records per-stage hashes, statuses, artifacts, and failure reasons.
- `ci/cache-index.json` records cache keys and zero-model-call reuse.
- `integration/replacement-plan.yaml` contains C_ONLY rollback semantics.
- `integration/bitstream-receipts/` contains byte and SHA-256 gates.
