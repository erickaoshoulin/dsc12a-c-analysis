# Regression and traceability directory layout

JSON receipts remain the source of truth. This checkout contains indexes and
human-readable projections; it does not copy RTL, C source, or the external
DSC PDF.

## New meanings

    /Users/snow/.svrt-network/dsc12a-regression/cache/flow/<run-id>/<contract-id>/
      repo/             isolated source/controller copy
      artifacts-<attempt>/
                        external candidate RTL/oracle/harness/build material
      flow.log          durable flow log

    /Users/snow/.svrt-network/dsc12a-regression/runs/<run-id>/functions/<contract-id>/
      accepted/         compact accepted-RTL handoff reference

    library/accepted/<contract-id>/<contract-hash>/
      rtl/              immutable accepted RTL (content-addressed reference)
      verification/     accepted evidence (content-addressed reference)
      contract/         locked contract (content-addressed reference)

    dashboard/          static HTML and normalized view models
    build/              compact C build and analysis-preflight receipts only
    dashboard/data/ci-frontier.json
                        current tool-selected ready/candidate/blocker frontier
    dashboard/data/traceability.json
                        repository-wide exact/proposed/reviewed/orphan audit
    reports/            readable regression-summary.md, orphan triage, and per-function reports
    library/index.json  accepted-library index with stale/provenance checks
    path-map.json       legacy-to-new path mapping

## Legacy compatibility

The existing rtl/, verification/, library/rtl/, library/verification/, and
library/contracts/ paths are indexed in path-map.json and remain readable.
Entries point at the existing content-addressed artifact or receipt; no large
file is copied into the new layout.

## Storage resolution

- selected root: /Users/snow/.svrt-network/dsc12a-regression
- resolution mode: ENV_ROOT
- requested root: /Users/snow/.svrt-network/dsc12a-regression
- SMB fallback reason: none

If the SMB share is unavailable, the dashboard reports LOCAL_REPOSITORY and
uses only repository-local legacy receipts. The PDF remains external and is
shown as SPEC_UNAVAILABLE when its recorded path cannot be opened.
