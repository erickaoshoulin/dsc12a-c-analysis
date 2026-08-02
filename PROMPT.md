# Standalone DSC 1.2a auto-discovery, contracts, coverage, and RTL-slice prompt

Work only in this standalone repository. The project is unrelated to SVRT,
RTL generation, sequential-hardware design, and LLM runtime behavior. Do not
modify or commit the upstream C model or the local PDF.

## Goal

Build a deterministic, rerunnable pipeline that discovers the local DSC 1.2a
PDF and C model, proves the C model can clean-build and smoke-run, discovers
combinational DUT candidates from tool facts rather than hardcoded names,
generates bidirectional PDF <-> C traceability, joins dynamic LLVM coverage,
creates three machine-selected contracts, and verifies one exhaustive
combinational RTL slice against the immutable C model. This project is not
SVRT and must not grow SVRT integration, whole-codec RTL generation, an LLM
runtime, C/Rust parsing, or sequential-hardware behavior.

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

The primary PDF text path is `pdfinfo` plus `pdftotext -layout`. Every PDF
`model note: MN_*` line is attached to the nearest preceding section heading
on the same page. A shared PDF/C model-note ID is `EXACT`; an explicit C
section/table/page reference may also be `EXACT`. Similarity or LLM suggestions
are only `PROPOSED`, and every heuristic requires at least two meaningful
shared tokens. Do not create traceability from revision history, CLI/host-only
code, DPX, logging, PSNR, or other non-codec plumbing.

## Dynamic coverage contract

Copy the discovered model to a temporary directory and rebuild the copy with
`-fprofile-instr-generate -fcoverage-mapping`. Run the existing bit-true smoke
flow, merge `*.profraw` using `llvm-profdata`, and export machine-readable
function/line/branch data with `llvm-cov export`. For every Clang-discovered
function record execution count when available, line and branch coverage,
production reachability, direct effects, and transitive effects.

An RTL candidate must remain production-reachable, output-contributing, pure,
bounded, free of state writes/I/O/allocation/logging, and dynamically executed
or explicitly marked `STATIC_BUT_UNCOVERED`. No function name may be supplied
as a selection allowlist.

## Contract and RTL-slice contract

Select the top three eligible leaf functions from tool facts and write:

- `contracts/proposed/<id>.yaml`
- `contracts/locked/<id>.json`
- `reports/contract-review.md`

Each contract records the Clang USR, source span/hash/permalink, exact/proposed
spec links, flattened inputs, only read struct fields, roles
`CONFIG_STATIC`/`RUNTIME_INPUT`/`CONSTANT_TABLE`/`DEPENDENCY`, signedness,
logical widths, legal domains, output ranges, overflow/shift/rounding rules,
dependencies, unresolved obligations, input-bit count, and the verification
plan. Infer widths in this order: normative spec, exact table/domain size,
Eva range, then C type fallback. A C-type fallback remains unresolved and is
never silently narrowed.

Choose the easiest contract with at least one `EXACT` spec link, no unresolved
arithmetic semantics, an exhaustive legal domain, and no state dependency. Make
a deterministic C oracle wrapper, combinational SystemVerilog candidates,
Verilator harness, exhaustive enumerator, and verification receipt. Use one
Codex generation call with only the chosen contract, the C function body, and
short exact spec anchors as context; generate at most four candidates. A
candidate must contain no clock, reset, latch, delay, or testbench logic.

Run Verilator lint/compile and exhaustive C-vs-RTL comparison for every
candidate. Exercise signedness, boundary, array-index, and off-by-one
mutations. Only a complete legal-domain pass is `EXHAUSTIVE_EQUIVALENT`; keep
smallest counterexamples and use `COUNTEREXAMPLE`, `UNPROVED`, or `UNSUPPORTED`
otherwise.

Write `coverage/`, `contracts/`, `rtl/candidates/`, `verification/`, and
`reports/progress.md`, and extend `summary.json` with exact-link before/after
counts, coverage ranking before/after, the three contracts, chosen-function
rationale, candidate results, counterexamples, and the next recommendation.

## Validation and handoff

Require deterministic JSON, complete C compilation/front-end checks, a full
linked C build/smoke receipt, coverage/tool receipts, Verilator evidence, no
hardcoded function targets, no LLM-created exact links, and provenance with
`do_not_edit` on generated artifacts. Update `README.md`, `run.sh`, and tests.
Report build status, candidate counts, link counts, orphan counts, coverage
before/after rankings, three contracts, and the first RTL result. Commit with:

```text
feat: create DSC contracts and first bit-true RTL slice
```

Then push the requested branch and open a draft PR with the same title.

## Dependency-aware CI/CD migration agent

The next migration stage is generic and must not add a function-name allowlist.
Use `python3 tools/cicd_agent.py plan|run|resume|status` and consume the
existing manifest, Clang facts, coverage, traceability, locked contracts,
callgraph, and verification receipts.

Emit `ci/dag.json`, `ci/plan.json`, `ci/state.json`, and
`ci/cache-index.json`. Each node records source/spec/contract/dependency
hashes, status, artifacts, and failure reason. Hash changes make old entries
stale. A valid cache entry is reusable with zero model calls; cache keys also
include prompt/model and tool-version hashes. Select every locked contract
whose semantics are resolved, execute independent contracts in stable parallel
batches, and compose callers only after callee RTL passes. Reject recursion and
combinational dependency cycles.

The contract-driven artifact bundle is under
`artifacts/<contract-hash>/` and includes a frozen SV interface/stub, C oracle,
Verilator harness, input packing, legal-domain/vector generator, mutations,
shadow/replacement wrapper, and receipt schema. The model may generate only a
combinational RTL body, at most once per function and at most four candidates.
Reject clocks, resets, latches, delays, initial blocks, stateful memory, and
testbench logic.

Verification is function × candidate × input shard. Compile each candidate
once, run shards in parallel, stop after the first mismatch, and retain the
smallest deterministic counterexample. Only complete legal-domain coverage is
`EXHAUSTIVE_EQUIVALENT`; other outcomes use `DIFFERENTIAL_PASS`,
`COUNTEREXAMPLE`, `UNPROVED`, `UNSUPPORTED`, or
`INFRASTRUCTURE_FAILURE`.

For caller/callee dependencies create an `A_core` interface, use `B_C` for
local testing, and compose `A_core+B_RTL` only after the callee passes. Record
each call site separately. Generate an immutable-C overlay with `C_ONLY`,
`SHADOW`, and `RTL_RETURN` modes. Run SHADOW before RTL_RETURN; require the
RTL_RETURN DSC stream to match the original byte-for-byte and by SHA-256.
Promotion requires unit, dependency, shadow, RTL_RETURN, and bitstream passes.
Rollback is a manifest change back to `C_ONLY`. Missing tools/source/PDF,
checkout failures, baseline mismatches, stale cache, timeouts, disk/network
failures, and missing Verilator are infrastructure failures and never trigger
an LLM call. Write `integration/generated-overlay/`,
`integration/replacement-plan.yaml`, `integration/bitstream-receipts/`, and
`reports/pipeline-summary.md`.

For the dependency-aware CI/CD change, commit and open a draft PR with:

```text
feat: add dependency-aware C-to-RTL CI/CD agent
```

## Execution contract v2: generic, tool-discovered migration

The previous migration paragraph is superseded by this executable contract.
This repository is independent of SVRT: do not add SVRT integration, C/Rust
parsers, whole-codec RTL, sequential hardware, or an LLM runtime. The local
PDF and upstream C model are immutable external inputs.

1. Discover and gate inputs. Find the local DSC 1.2a PDF and C model from the
   manifest/discovery facts. Require the PDF hash/page gate, a clean `make`
   build of `source/dsc`, and the existing `run_c_baseline*.sh` smoke receipt.
   Missing or changed inputs/tools are `INFRASTRUCTURE_FAILURE`; never invoke
   the generator to repair infrastructure.

2. Discover work from facts. Use Clang facts, exact traceability, coverage,
   callgraph, purity/timing/effect facts, and reviewed domain evidence. Do not
   configure a function name, source filename, or target allowlist. The
   reviewed domain file must match an exact spec anchor or reviewed runtime
   evidence; otherwise the candidate remains blocked. Select at least one new
   ready leaf whose frozen interface shape differs from existing promoted
   work. Reject recursive/combinational dependency cycles.

3. Invoke the real generator hook. On a ready cache miss invoke
   `DSC_CICD_GENERATOR_CMD request.json output_dir` exactly once. The request
   contains only `locked_contract`, `frozen_interface`, `c_body`, and short
   `exact_spec_anchors`. The hook emits at most four SystemVerilog candidates
   and telemetry. A missing hook is `GENERATION_REQUIRED`; zero-output or
   invalid output is `GENERATION_FAILED`. Cache hits reuse verified receipts
   with zero generator/model calls.

4. Verify executable candidates. Freeze direct scalar argument/result ports,
   legal domains, packing, C oracle, harness, and mutation cases. Reject
   clocks, resets, latches, delays, `initial`, stateful memory, and testbench
   logic. Compile each candidate once with Verilator. Run every candidate over
   the complete legal domain as real parallel input-shard processes, cancel
   after mismatch, reduce deterministically, and retain the smallest
   counterexample. Only complete coverage is `EXHAUSTIVE_EQUIVALENT`.

5. Verify a real dependency. Automatically choose the smallest acyclic direct
   caller-to-callee edge from the callgraph. Prove caller core with callee C,
   callee RTL against the callee C oracle, and caller core plus callee RTL.
   Record each direct call site and direct argument/result port; state-only or
   dummy passes are invalid. A wrong callee candidate must fail composition.

6. Rewrite safely. Use Clang LibTooling/Rewriter and USRs, not line-number
   text replacement. Rename the selected definition, rewrite every direct
   cross-file/multiple-per-line call, and fail closed for macro, indirect, or
   ambiguous references. Receipt old/new hashes, changed files, rewritten
   USRs, call sites, and failures; verify the upstream source hash is unchanged.

7. Run the model gates. Build an isolated immutable-C overlay with `C_ONLY`,
   `SHADOW`, and `RTL_RETURN`. Auto-discover the default smoke script, a
   different bpc script, and a sampling script when present. Run SHADOW before
   RTL_RETURN. Require zero C/RTL mismatches and byte-for-byte plus SHA-256
   equality with the original C stream. Promote only after unit, dependency,
   shadow, RTL_RETURN, and bitstream gates pass. Rollback is `C_ONLY`.

8. Report and hand off. Write deterministic `ci/plan.json`, `ci/dag.json`,
   `ci/state.json`, `ci/cache-index.json`, artifact receipts, generated-overlay
   receipts, bitstream receipts, and `reports/pipeline-summary.md`. Report
   candidates, model calls/tokens, shard counts, timings, dependency pair,
   matrix scenarios, cache status, blockers, and counterexamples. Run tests,
   commit, push the requested branch, and open a draft PR titled exactly:

```text
feat: execute generic RTL generation and dependency composition
```
