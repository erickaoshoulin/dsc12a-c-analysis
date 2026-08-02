# Standalone DSC 1.2a auto-discovery, contracts, coverage, and RTL-slice prompt

Work only in this standalone repository. The project is unrelated to SVRT,
RTL generation, sequential-hardware design, and LLM runtime behavior. Do not
modify or commit the upstream C model or the local PDF.

## Goal

Build a deterministic, rerunnable pipeline that discovers the local DSC 1.2a
PDF and C model, proves the C model can clean-build and smoke-run, discovers
combinational DUT candidates from tool facts rather than hardcoded names,
generates bidirectional PDF <-> C traceability, joins dynamic LLVM coverage,
and incrementally grows a stable designer-facing Verilog library. Every new
leaf is first exercised through the immutable C oracle, real Verilator builds,
and parallel shards; only a complete legal-domain proof may enter the stable
library. This project is not SVRT and must not grow SVRT integration,
whole-codec RTL generation, an LLM runtime, C/Rust parsing, or
sequential-hardware behavior.

## Input discovery

- Prefer `DSC_SPEC_PDF`, `DSC_SOURCE_DIR`, and `DSC_MODEL_ROOT`.
- When unset, use macOS `mdfind`, then a bounded search under the repository
  parent, `~/Desktop`, and `~/Downloads`.
- Accept a PDF only when `pdfinfo` metadata identifies Display Stream
  Compression and version 1.2a and the page count is 145. Record path, size,
  SHA-256, metadata, and the gate evidence.
- Accept a C model only when the source contains `Makefile`,
  `codec_main.c`, and `dsc_codec.c`. Record source path, source hashes,
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
- Treat every AST-observed `WRITES_THROUGH` pointer parameter, global/field
  write, or mutable static as a stateful effect. Detect writes through
  dereference and increment/compound-assignment wrappers (for example
  `(*bit_count)++`); an unqualified pointer type is never evidence of a
  read-only DUT interface. No reviewed domain override may waive a state write.

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
`-fprofile-instr-generate -fcoverage-mapping`. Automatically discover every
existing `bittrue_smoke/run_c_baseline*.sh` script and run them sequentially
against that instrumented copy; do not maintain a function or script-name
allowlist. Each script must retain its own profile prefix, expected hash, and
output receipt. The default analysis uses every discovered script; set
`DSC_COVERAGE_SCRIPTS=default` only for an explicitly bounded smoke run. Merge
all `*.profraw` files using `llvm-profdata`, and export machine-readable
function/line/branch data with `llvm-cov export`. For every Clang-discovered
function record execution count when available, line and branch coverage,
production reachability, direct effects, and transitive effects.

An RTL candidate must remain production-reachable, output-contributing, pure,
bounded, free of state writes/I/O/allocation/logging, and dynamically executed
or explicitly marked `STATIC_BUT_UNCOVERED`. No function name may be supplied
as a selection allowlist.

The DUT rule above applies to production-output RTL. A tool-ranked, executed
pure/combinational `CONFIG` helper whose only failed criterion is
`contributes_to_observable_output` may instead be admitted as a reusable
configuration-library primitive, but only with a complete finite exact-spec
domain and reviewed `tool_admission.kind: CONFIG_LIBRARY`,
`role: CONFIG_HELPER`, and `non_dut_boundary: true`. This admission must not
waive state, I/O/allocation/logging, boundedness, coverage, dependency, or
source gates. Emit it under the configuration/library boundary and never count
it as production codec DUT or output logic.

## Contract and RTL-slice contract

Select up to the top N eligible leaf functions from tool facts (default N=10;
the bounded batch may be changed only with `DSC_ANALYSIS_TOP_N`). A smaller
selection is valid when leaf/dependency/spec filters leave fewer than N
candidates. Any reviewed domain override may enrich a tool-selected candidate,
but it must not select a function or bypass `facts/candidates.json` and
`coverage/coverage.json`:

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
counts, coverage ranking before/after, the selected contracts, chosen-function
rationale, candidate results, counterexamples, and the next recommendation.

## Validation and handoff

Require deterministic JSON, complete C compilation/front-end checks, a full
linked C build/smoke receipt, coverage/tool receipts, Verilator evidence, no
hardcoded function targets, no LLM-created exact links, and provenance with
`do_not_edit` on generated artifacts. Update `README.md`, `run.sh`, and tests.
Report build status, candidate counts, link counts, orphan counts, coverage
before/after rankings, selected contracts, and the first RTL result. Commit with:

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
   legal domains, packing, C oracle, harness, and mutation cases. A reviewed
   pointer/window leaf may flatten only the read-only taps that the C body and
   spec actually use; stateful callers, line-buffer storage, and unrelated
   helpers remain C boundaries. Reject clocks, resets, latches, delays,
   `initial`, stateful memory, and testbench logic. Compile each candidate once
   with Verilator. Run every candidate over the complete legal domain as real
   parallel input-shard processes, cancel after mismatch, reduce
   deterministically, and retain the smallest counterexample. Only complete
   coverage is `EXHAUSTIVE_EQUIVALENT`.

   If the legal value space is too large for concrete enumeration, use an
   explicitly reviewed `windowed_boundary`/equivalent strategy that records
   `exhaustive: false`. It must still cover every structural mode, exact
   qLevel/component relation, signedness, boundaries, array indices, and
   pairwise tap interactions. A multi-group window must declare its padding,
   samples-per-unit, group offsets, static pointer indices, and per-group
   pairwise tap sets in reviewed data; the generator and adapter derive the
   frozen ports from those facts rather than embedding a single sample index.
   A clean concrete result is `DIFFERENTIAL_PASS`, never a promotion or
   stable-library proof. For a reviewed production-domain relative-window
   contract, keep the complete C line-buffer state at the caller boundary and
   give the DUT only the exact spec-defined read-only taps. Run the independent
   `tools/formal_rtl.py` gate: it must parse the candidate with Verilator's
   AST, compare the AST to the locked spec-linked equations, and prove the
   complete reviewed legal relation with Z3. Only that independent receipt
   may upgrade the candidate to `FORMAL_EQUIVALENT`; a copied C expression,
   function-name check, or concrete sample count is not a proof. Continue
   iterating from counterexamples and proof gaps toward a formal proof or a
   smaller spec-grounded DUT slice. `FORMAL_EQUIVALENT` proves only the
   declared reviewed window; require `proof_complete=true`, and treat a proof
   timeout as `UNPROVED`. Production frame, dependency, and source gates still
   decide whether the leaf can enter `library/manifest.json`.

   For a reviewed `flatness_window`, derive the interface and equations from
   the tool-discovered contract data, never from a function-name recipe. The
   contract must declare the four component lanes and seven read-only original
   pixel taps per lane, with Figure 6-19 check-1 offsets `0..3`, check-2
   offsets `1..6`, and the line-window padding. Lock the exact Table 6-2
   luma/chroma rows, `flatQLevel = MapQpToQlevel(MAX(0, primaryQp -
   somewhatFlatQpDelta))`, the DSC 1.2a `flatnessDetThresh` relation, and the
   native-420/version adjustment as reviewed semantics. The C oracle may own
   line storage, but the RTL leaf receives only those read-only taps; an
   adapter must short-circuit every lane whose `numComponents` is not active
   before dereferencing its `origLine`. Concrete vectors must cover structural
   modes, line ends, every tap at both boundaries, and pairwise tap effects;
   the independent Verilator-AST/Z3 proof must establish the full declared
   relation before promotion.

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

## Durable per-function regression service v1

This repository remains a standalone DSC C-model analysis project. The
regression service is an orchestration layer for the existing generic
C-to-RTL flow; it is not SVRT integration, a whole-codec RTL generator, a
sequential-hardware project, or an LLM runtime. Do not add SVRT dependencies,
SVRT configuration, C/Rust parsers, or hardcoded function-name targets.

Before submitting any regression job, re-check the immutable local inputs from
the manifest. The PDF must pass the DSC 1.2a metadata/page gate. The C model
must pass the front-end compile database check, a clean isolated
`make -j1 clean` followed by `make -j1`, produce `source/dsc`, and pass the
discovered bit-true smoke/golden-hash check. Any missing tool, changed source
or PDF hash, compiler failure, smoke mismatch, timeout, or path failure is an
`INFRASTRUCTURE_FAILURE`; do not invoke a generator to repair it. Keep the PDF
and upstream C source outside this repository and read-only.

Function selection is facts-driven. Discover functions through the existing
Clang/facts/contracts/callgraph/coverage/cache artifacts and preserve the
function names only as discovered data in receipts. Reviewed overrides may
carry domain evidence for a known facts identity, but they cannot materialize
a function that is absent from the tool-ranked candidate and coverage facts.
Never add a target list, allowlist, source-file selector, or prompt field that
supplies a function name.

An explicit `STATIC_BUT_UNCOVERED` review may admit a statically eligible
candidate only when the override carries exact PDF authority and a complete
finite legal domain. A bounded exploratory subset is
`DIFFERENTIAL_PASS`/`UNPROVED`; a reviewed, independently parsed proof may
be `FORMAL_EQUIVALENT`, but it still needs dependency, frame, and source
gates before stable-library promotion. A function
already recorded as PASS in `library/manifest.json` is not new work and is
excluded from ordinary queue planning; it may be re-run only when the durable
queue explicitly requests a refresh or dependency composition.

When Clang marks only `bounded_computation` false for an otherwise eligible,
executed production leaf, a reviewed `BOUNDED_DOMAIN` admission may discharge
that one fact. The admission must match the discovered Clang identity, carry an
exact PDF link, provide a complete finite legal domain for every input and
output, and record a tool-readable loop proof plus a finite maximum iteration
count. It must never waive state writes, I/O, allocation, logging, indirect
calls, output reachability, or coverage. The receipt records
`coverage_basis: reviewed_bounded_domain`; negative/out-of-domain behavior is
not silently promoted into the contract.

When Clang marks only `no_io_allocation_or_logging` false for an otherwise
eligible, executed production leaf, a reviewed `DOMAIN_EFFECT` admission may
discharge only a logging effect proven unreachable throughout the contracted
finite domain. It must carry exact PDF authority, a complete input/output
domain, a tool-readable unreachable-condition proof, and
`discharged_effects: ["logging"]`. It cannot waive allocation, state writes,
indirect calls, output reachability, coverage, or any other failed criterion;
the RTL contract covers the legal domain only and never models the diagnostic
branch as DUT behavior. The receipt records
`coverage_basis: reviewed_domain_effect`.

When the only failed candidate criterion is observable-output contribution for
a tool-discovered `CONFIG` function, a reviewed `CONFIG_LIBRARY` admission may
promote a pure/combinational, finite, exact-spec lookup or helper for designer
reuse. The override must explicitly set `role: CONFIG_HELPER` and
`non_dut_boundary: true`; it cannot select a function, waive any other fact,
or make configuration plumbing part of the production-output DUT. Its receipt
records `coverage_basis: reviewed_config_library`.

Composite candidates are also tool-discovered work. A reviewed override may
resolve a pure, bounded function with direct callees only after every direct
callee has a PASS entry in `library/manifest.json`; the override supplies
spec/domain/semantics evidence, never the selection. Keep the immutable C call
chain as the oracle/reference boundary and promote only the selected
combinational function after its own C-vs-RTL and frame gates pass. Do not
flatten stateful callers, host code, or unrelated helpers into the DUT.
Reject recursive or combinational dependency cycles. A generation authority
must be `EXACT_SPEC`, `DERIVED`, or `HUMAN_APPROVED`; `AI_PROPOSED` and
`C_TYPE_FALLBACK` are visible blockers and cannot generate RTL.

The durable service is `tools/cicd_agent.py` and stores mutable state only in
the repository's JSON receipts under `ci/`, `artifacts/`, and `integration/`.
Do not add a network share, SQLite queue, SVRT state, or a second orchestration
service. Publish each receipt atomically, preserve prior receipts for audit,
and treat missing PDF/source/tools, stale hashes, low disk, or timeout as
infrastructure failures. `plan` consumes tool-discovered facts and reviewed
contracts; a target ID is routing metadata and never a source-level function
allowlist.

The supported commands are:

```sh
python3 tools/cicd_agent.py plan
python3 tools/cicd_agent.py run
python3 tools/cicd_agent.py resume
python3 tools/cicd_agent.py status
```

For a bounded regression refresh of already promoted leaves, the queue may use
`DSC_CICD_REFRESH_STABLE=1` together with `DSC_CICD_MAX_NEW` and
`DSC_CICD_CONTRACT_WORKERS`. This refresh selects the current PASS components
from `library/manifest.json` only after re-reading the tool/spec-ready contract
frontier; those variables are routing and parallelism metadata, never a
function-name allowlist. `DSC_CICD_FORCE_REGENERATE=1` remains the explicit
single-contract refresh route through `DSC_CICD_TARGET_CONTRACT`.

Each bounded batch may generate at most four candidates per selected contract.
Independent contracts run in stable parallel workers. Preserve the immutable
C model as oracle/reference, run the real C/Verilator shards, and promote only
after unit, formal-or-exhaustive, dependency, C_ONLY/SHADOW/RTL_RETURN, and
frame byte/SHA-256 gates pass.

### Continuous scale and library loop

Use the executable agent directly for bounded iterative batches:

```sh
python3 tools/cicd_agent.py plan
python3 tools/cicd_agent.py run
python3 tools/cicd_agent.py status
```

Each run reads the current facts/spec plan at dispatch. A reviewed contract
that becomes eligible later enters a subsequent batch without editing a
function allowlist. Each selected contract gets an independent generator
invocation, C oracle, Verilator build, parallel shard set, caller composition
check, and frame matrix. A target contract is queue routing metadata only; it
is never a source-level function selector. A refresh intentionally bypasses a
valid leaf cache while preserving prior receipts and accepted RTL for audit
and rollback. If no unproven ready contract exists, the run reports no new
work and does not enqueue a duplicate batch.

For an explicit stable refresh, the scale function set is the union of the
current facts/spec-ready plan and PASS components already recorded in
`library/manifest.json`, rechecked through the current exact width/spec gate.
Stable components that need to be rematerialized from reviewed overrides are
discovered by their tool facts identity during that refresh. This keeps every
verified leaf in the regression surface without turning the manifest into a
source-level function allowlist.

Within one executable CI/CD run, independent selected contracts execute in
stable dependency-aware parallel batches (`DSC_CICD_CONTRACT_WORKERS`); a
selected caller waits for selected callees, while already-promoted callees
are treated as verified boundaries. Each contract still compiles its C oracle
and Verilator candidate once and runs its input shards in parallel under the
separate shard worker limit.

Run the loop continuously in bounded batches, keeping the immutable C model as
the oracle while replacing only proven DUT leaves:

```text
facts/spec review → scale dispatch → parallel generate → C oracle + Verilator
→ exhaustive/legal-domain or explicitly bounded differential shards
→ AST/Z3 proof when reviewed → smallest counterexample / DIFFERENTIAL_PASS /
FORMAL_EQUIVALENT / EXHAUSTIVE_EQUIVALENT
→ caller/frame gates → promote PASS leaves → inspect blockers → next batch
```

On a counterexample, retain the receipt and feed the smallest failing vector
back into the next generator/repair attempt. On an infrastructure failure,
repair the tool/domain/oracle gate and resume only the affected queue job.
Never promote a candidate because it compiles alone. Promotion requires all
unit, dependency, C_ONLY/SHADOW/RTL_RETURN, frame byte/SHA, exact PDF
traceability, and reviewed-port gates. The promotion stage writes
only stable, purely combinational DUT leaves to `library/rtl/`, together with
`library/contracts/`, `library/verification/`, and `library/manifest.json`.
The executable agent performs that materialization automatically under a
library write lock after a `PROMOTED` result, canonicalizes the module name,
archives a replaced RTL file, and records `library_promotion: PASS`. A receipt
that only passes unit or differential comparison is never materialized.
The library is an incremental designer-facing RTL set, not a whole-codec
rewrite: keep stateful callers, unresolved pointer/table dependencies, and
non-DUT code in C until their contracts are independently proven.

Each function job must produce evidence for the ordered gates:

```text
width/spec
→ generator/cache
→ Verilator lint/build once
→ real parallel shards
→ deterministic reduction/mutations
→ dependency composition
→ C_ONLY/SHADOW/RTL_RETURN
→ frame byte/SHA-256 comparison
```

Large logs, build trees, vectors, and flow worktrees stay outside the handoff.
Compact receipts, traceability, accepted RTL, and pipeline metadata are the
handoff. Verified shards may be reused only after the current contract input
order, vector strategy, and every shard line count match the prior receipt.
Receipts must include candidate and frame pass rates, shard/vector counts,
counterexamples, blockers, cache/execution status, model tier/call budget,
artifact links, and the C/PDF source gate. Pipeline reports expose overview,
progress, failure buckets, per-function details, artifact links, and
PDF/spec-to-C cross-links. For every port/intermediate retain width,
signedness, domain, role, authority, derivation, review status, exact PDF
page/section/table, C span, and contract hash.

Read `model-policy.yaml` for routing. Discovery, contracts, testbench, and
verification work are deterministic. Cheap models handle only
repetitive classification/syntax/local repair; strong models handle only
ambiguous spec, boundary, or complex dependency work. Resolve model names
from environment variables, allow at most one initial and one escalation call
per function, and never duplicate agents on one function.

The executable loop follows `observe → plan → dispatch → verify → update`
using durable JSON receipts under `ci/`, `artifacts/`, and `integration/`, not
chat memory. Passing a batch is a checkpoint, not the end of the migration:
after each promotion, re-read facts/spec/coverage and dispatch the next
bounded batch of newly eligible leaves or composites. `NO_NEW_WORK` means the
current frontier is exhausted and must be re-checked after the next reviewed
contract or dependency promotion; it is not permission to add a function-name
target. Run tests for cache reuse, bad RTL, authority traceability,
deterministic reports, composite promotion gates, and the no-function-allowlist
invariant before publishing a flow change. Commit with a scope-specific title,
push the requested branch, and update the existing draft PR rather than
creating a duplicate.
