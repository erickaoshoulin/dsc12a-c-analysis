# Standalone DSC 1.2a auto-discovery and traceability prompt

Work only in this standalone repository. The project is unrelated to SVRT,
RTL generation, sequential-hardware design, and LLM runtime behavior. Do not
modify or commit the upstream C model or the local PDF.

## Goal

Build a deterministic, rerunnable pipeline that discovers the local DSC 1.2a
PDF and C model, proves the C model can clean-build and smoke-run, discovers
combinational DUT candidates from tool facts rather than hardcoded names, and
generates bidirectional PDF <-> C traceability.

## Input discovery

- Prefer `DSC_SPEC_PDF`, `DSC_SOURCE_DIR`, and `DSC_MODEL_ROOT`.
- When unset, use macOS `mdfind`, then a bounded search under the repository
  parent, `~/Desktop`, and `~/Downloads`.
- Accept a PDF only when `pdfinfo` metadata identifies Display Stream
  Compression and version 1.2a and the page count is 145. Record path, size,
  SHA-256, metadata, and the gate evidence.
- Accept a C model only when the source contains `Makefile`,
  `codec_main.c`, and `dsc_codec.c\). Record source path, source hashes,
  Git remote, branch, commit, and status.
- Write `SPEC_UNAVAILABLE` or `SOURCE_UNAVAILABLE` when the corresponding
  gate fails. Never download, invent, or use an LLM to fill missing inputs.

## Build gate

Copy the discovered model root to a temporary directory and run, in order:

```text
make -j1 -C source clean
make -j1 -C source
```

Require `source/dsc`. If `bittrue_smoke/run_c_baseline.sh` exists, run it
and verify its expected golden hash; otherwise run a safe help/smoke command.
Record commands, return codes, warnings, tool versions, timeout/path failures,
smoke outputs, and binary SHA-256 in `build/build-receipt.json`.

Any build/tool/path/timeout failure is `INFRASTRUCTURE_FAILURE`. Stop before
regenerating analysis artifacts and do not invoke an LLM.

## Tool-driven discovery

- Generate `compile_commands.json` from the public build inputs.
- Run the compiler front end over every translation unit.
- Run Clang LibTooling/AST Matchers over every translation unit and discover
  every source-defined function, USR, call edge, caller/callee, direct and
  transitive global/field/pointee reads/writes, loops/trip facts, and return
  dependencies.
- Infer production roots from linked executable entry symbols and infer
  observable-output paths from structural calls/dataflow to compressed bitstream
  or reconstructed-output sinks.
- Do not maintain `TARGETS`, function-name allowlists, source-name selection,
  or an analysis profile containing function names.
- For every function record:
  - purity: `PURE`, `IMPURE`, or `UNKNOWN`;
  - timing: `COMBINATIONAL`, `STATEFUL`, or `UNKNOWN`;
  - role: `DUT`, `CONFIG`, `CHECKER`, `HOST_IO`, `TEST`, or
    `UNRESOLVED`;
  - production reachability, observable-output contribution, confidence, and
    evidence.
- Rank a candidate only when it is production-reachable, output-contributing,
  free of direct/transitive state writes, free of I/O/allocation/logging, and
  bounded. Run Eva/From on the top 10 ranked analyzable candidates by default.
  Names may appear in receipts only as discovered output, never as selection
  input.

## Traceability contract

Do not commit the PDF or long extracted PDF text. Record PDF manifest/hash/page,
headings, tables, figures, short anchors, model-note `MN_*` IDs, explicit
function/table/page references, C comments/constants/tables, USRs, file and
line ranges, and fixed-commit permalinks.

Generate:

- `spec/manifest.json`, `spec/anchors.json`,
  `facts/comments.json`;
- `traceability/links.proposed.yaml`,
  `traceability/links.reviewed.yaml`, and
  `traceability/traceability.json`;
- `reports/spec-to-code.md`, `reports/code-to-spec.md`,
  `reports/orphans.md`, and `reports/candidates.md`.

Link precedence is exact `MN_*` match, explicit page/section/table reference,
normalized function/table identifier, then optional LLM proposal. Exact links
must never be created by an LLM. Proposed, reviewed, exact, and stale statuses
remain distinct; reviewed links are human-edited and become stale when input
hashes change. Unknowns and orphans must remain visible.

## Validation and handoff

Require deterministic JSON, complete C compilation/front-end checks, a full
linked C build/smoke receipt, no hardcoded function targets, no LLM-created
exact links, and provenance with `do_not_edit` on generated artifacts.
Update `README.md`, `run.sh`, and tests. Report build status, candidate
counts, link counts, orphan counts, and the top three candidates. Commit with:

```text
feat: auto-discover DSC DUT candidates and spec traceability
```

Then push the requested branch and open a draft PR with the same title.
