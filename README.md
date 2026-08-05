# DSC 1.2a C model analysis

This standalone repository analyzes the local DSC 1.2a C reference model and
links tool-discovered C facts back to the local PDF specification. It is
isolated from SVRT and unrelated projects, does not modify the upstream model
or copy the PDF, and does not use Rust. The pipeline uses LLVM coverage and
Clang facts to create tool-selected contract batches. Promoted `library/rtl`
remains a human-reviewed combinational library; an isolated provisional plane
also verifies bounded stateful Encode/Decode RTL inside the copied full-frame C
model through Verilator-generated C++. Provisional success is simulation
evidence and never bypasses human promotion review.

## Inputs

Run:

```sh
./run.sh
```

Input discovery uses this precedence:

1. `DSC_SPEC_PDF`, `DSC_SOURCE_DIR`, or `DSC_MODEL_ROOT`.
2. macOS `mdfind`.
3. A bounded search under the repository parent, `~/Desktop`, and
   `~/Downloads`.

The PDF gate records the path, SHA-256, `pdfinfo` metadata, and requires DSC
1.2a metadata plus 145 pages. The C gate requires a model root containing
`source/Makefile`, `source/codec_main.c`, and `source/dsc_codec.c`.
Missing inputs are recorded as `SPEC_UNAVAILABLE` or
`SOURCE_UNAVAILABLE`; the pipeline does not download or synthesize inputs.

## Build and analysis

Before analysis, the model root is copied to a temporary directory. The copy is
clean-built with `make -j1 clean` and `make -j1`; the resulting
`source/dsc` is run through `bittrue_smoke/run_c_baseline.sh` when available.
The receipt records commands, versions, warnings, smoke/golden hashes, binary
hashes, and excluded derived directories. The upstream source remains
read-only.

Clang LibTooling analyzes every translation unit in
`compile_commands.json`. It records the complete function inventory, USRs,
call graph, direct/transitive global/field/pointee effects, loops and trip
facts, return dependencies, and source ranges. Production scope is inferred
from linked executable entry symbols and dataflow to observable bitstream or
reconstructed-output sinks.

Candidates are ranked without a function-name allowlist. Each function gets
purity, timing, role, production reachability, observable-output contribution,
confidence, and evidence. The eligible criteria are production reachability,
output contribution, no direct/transitive state write, no I/O/allocation/logging,
and bounded computation. If Clang proves every criterion except a loop bound,
the CI/CD agent may accept a tool-ranked, executed candidate only through a
reviewed `BOUNDED_DOMAIN` admission containing exact PDF authority, a complete
finite input/output domain, and a finite loop proof; this never selects a
function by name or waives any other effect/coverage criterion. The top 10
(configurable with
`DSC_ANALYSIS_TOP_N`) are passed to Frama-C Eva/From when analyzable.

A reviewed `DOMAIN_EFFECT` admission can discharge only a logging effect that
is proven unreachable over the complete contracted domain. It must name exact
PDF authority, finite input/output domains, the unreachable condition, and
`discharged_effects: ["logging"]`; it cannot waive any other criterion or turn
the diagnostic branch into DUT logic. Its receipt is marked
`coverage_basis: reviewed_domain_effect`.

The production-output criterion has one explicit library boundary: a
tool-ranked, executed pure/combinational `CONFIG` helper whose only failed
criterion is observable-output contribution may be admitted as a reusable
configuration primitive. It requires a complete finite exact-spec domain and
reviewed `CONFIG_LIBRARY` evidence with `role: CONFIG_HELPER` and
`non_dut_boundary: true`; it never turns configuration plumbing into codec DUT
logic or waives effects, boundedness, coverage, dependency, or source gates.

## Specification traceability

The primary PDF extractor is `pdfinfo` plus `pdftotext -layout`. It records page
count, headings, tables, figures, short anchors, and same-page nearest-heading
assignments for `MN_*` model notes in `spec/anchors.json`; it never stores long
PDF text.
C comments, `MN_*` model notes, explicit page/section/table references,
function ranges, constants, tables, USRs, source hashes, and fixed-commit
permalinks are recorded in `facts/comments.json`.

`traceability/links.proposed.yaml` contains generated exact/proposed links plus
`REVIEWED` links projected from accepted library contracts. A `PASS` component
with `authority: EXACT_SPEC` is joined by its contract's Clang USR and exact PDF
anchors only after the library manifest's source/spec hashes match; this is
traceability enrichment, never a function-name selector or new-work admission.
`traceability/links.reviewed.yaml` is the human-edited review surface and is
never overwritten. A reviewed link becomes `STALE` if either input hash
changes. Reports are bidirectional and retain visible unknowns/orphans. The
dashboard traceability page also shows repository-wide exact/proposed/reviewed
counts, accepted-library projection status, the proposal queue, linked-versus-total
anchors, and complete orphan lists. `reports/orphan-triage.md` and the dashboard triage tables add
evidence-backed next actions from Clang, candidate, coverage, comment, and PDF
facts without creating links or RTL targets, so raw JSON is not required to
find the next review work.

After C facts are assembled, an instrumented temporary copy automatically
discovers and runs every `bittrue_smoke/run_c_baseline*.sh` profile, retaining a
separate LLVM profile prefix and expected-output receipt for each script. Set
`DSC_COVERAGE_SCRIPTS=default` only for a deliberately bounded smoke run.
Contracts are selected without a function-name allowlist. A selected exact-link
contract is checked with a generated C oracle, up to four combinational
SystemVerilog candidates, Verilator, and either exhaustive legal-domain
enumeration or the independent proof required by a reviewed finite window.
Deliberate signedness, boundary, index, and off-by-one mutations remain
visible as counterexamples.

## Outputs

```text
spec/
  manifest.json
  anchors.json
build/
  build-receipt.json
facts/
  compile_commands.json
  compile-check.json
  discovered-functions.json
  functions.json
  callgraph.json
  field-access.json
  loops.json
  value-ranges.json
  dependencies.json
  candidates.json
  comments.json
traceability/
  links.proposed.yaml
  links.reviewed.yaml
  traceability.json
reports/
  candidates.md
  candidate-functions.md
  spec-to-code.md
  code-to-spec.md
  orphan-triage.md
  orphans.md
  function-summary.md
  field-summary.md
  unresolved.md
summary.json
coverage/
  coverage.json
  coverage-receipt.json
contracts/
  proposed/
  locked/
  selection.json
rtl/
  candidates/
  generation-context.json
verification/
  <contract>/
  verification-receipt.json
reports/
  contract-review.md
  progress.md
```

`contracts/selection.json` also records the complete tool-selected frontier:
leaf functions emitted in the current batch and eligible callers deferred with
their direct dependency evidence. Deferred callers are not silently dropped
and are not treated as locked contracts.

All generated JSON includes provenance and semantic hashes. Build/tool/path,
compiler, timeout, or source-integrity failures are
`INFRASTRUCTURE_FAILURE`; no regeneration or LLM fallback is attempted.

## Dependency-aware CI/CD agent

The generic migration agent consumes the locked contracts, coverage facts,
traceability, call graph, and existing verification receipts. It does not take
function names as configuration. Run it with:

```sh
python3 tools/cicd_agent.py plan
python3 tools/cicd_agent.py run
python3 tools/cicd_agent.py resume
python3 tools/cicd_agent.py status
```

`plan` verifies the local PDF/C source, tool versions, and immutable C
bitstream baseline; hashes source/spec/contract/dependency/prompt/model/tool
inputs; detects cycles; and schedules every locked contract whose semantics
are resolved. Independent ready contracts use stable parallel batches.
`resume` reuses a valid cache entry with zero model calls. Stale hashes are
visible in `ci/plan.json` and cannot silently reuse old artifacts. Reviewed
domain evidence can enrich a tool-selected eligible leaf under
`ci/reviewed-contracts/` without editing the immutable generated lock.

The state machine is recorded in `ci/dag.json` and `ci/state.json`. Each
contract hash gets an artifact bundle containing its frozen interface, C
oracle adapter, harness, input packing, legal-domain plan, mutations, overlay
wrapper, and receipt schema. The integration overlay supports `C_ONLY`,
`SHADOW`, and `RTL_RETURN`; the latter two compare C and RTL while the full
DSC smoke stream is checked byte-for-byte and by SHA-256. Rollback is a
manifest change back to `C_ONLY`.

Compact CI outputs are under `ci/`, `artifacts/<contract-hash>`
(receipts/contracts only), `integration/generated-overlay/`,
`integration/replacement-plan.yaml`, `integration/bitstream-receipts/`, and
`reports/pipeline-summary.md`. The upstream C model and PDF are never edited.
The candidate RTL, C oracle, harness, vector generator, rejected candidates,
and verbose build logs are external flow material. Durable flows set
`DSC_CICD_ARTIFACT_ROOT` and `DSC_REGRESSION_ROOT`; state/cache receipts
retain the logical `artifacts/<contract-hash>` reference without copying the
large files into this checkout.

Scale dispatch is incremental: after a terminal batch, another `scale
<pilot-run-id>` call re-reads the current facts/spec plan and enqueues only
ready contracts without a prior PASS scale receipt. It returns `NO_NEW_WORK`
when the current ready frontier is already proven.

### Executable generator contract

The migration agent has no function-name target or implicit model stub. Tool
facts and coverage first select an eligible leaf; exact traceability and
reviewed domain evidence only enrich that leaf. A reviewed override cannot
materialize a function absent from `facts/candidates.json` and
`coverage/coverage.json`. A ready cache miss requires an external hook:

```sh
DSC_CICD_GENERATOR_CMD='python3 tools/generator_fixture.py' \
  python3 tools/cicd_agent.py run
```

The hook receives only `locked_contract`, `frozen_interface`, `c_body`, and
short `exact_spec_anchors`. It emits at most four combinational `.sv`
candidates plus telemetry. The fixture emits one correct and one deliberately
wrong candidate so the verifier records both an exhaustive pass and a
smallest counterexample. The planner preflights the hook for new/repair work;
a missing hook records `GENERATION_REQUIRED` in `ci/plan.json` as an
infrastructure blocker, stops before any generator/model call, and does not
reselect the same contract until the hook is configured.

The verifier compiles the immutable C oracle and every candidate once, runs
the complete legal domain through parallel shards, and writes `EXECUTED_NOW`
receipts. It then uses the Clang LibTooling rewriter to rename the discovered
definition and rewrite every direct call site in an isolated copy.
`C_ONLY`, `SHADOW`, and `RTL_RETURN` run against default, alternate-bpc, and
sampling scenarios; promotion requires all byte/SHA bitstream gates. A second
run exercises the valid cache and reports `REUSED_VERIFIED_RECEIPT` with zero
generator/model calls.

Windowed/pointer-heavy DUTs use a reviewed scalar-tap adapter only for the
read-only values consumed by the C body. The `windowed_boundary` strategy
currently drives all structural modes plus deterministic boundary and
pairwise tap cases. Its result is `DIFFERENTIAL_PASS` when every generated
vector matches; it is deliberately not `EXHAUSTIVE_EQUIVALENT`. The independent
Verilator-AST/Z3 gate may upgrade a complete reviewed window to
`FORMAL_EQUIVALENT`, but production dependency, frame, and source gates still
must pass before promotion. This keeps the designer-facing library
combinational and stable while stateful line storage and non-DUT C logic
remain reference boundaries.

Reviewed spec-defined flatness windows use the data-driven `flatness_window`
strategy. The contract declares the four component lanes, seven original-pixel
taps per lane, Figure 6-19 offsets, Table 6-2 qLevel rows, and the exact
`flatnessDetThresh` relation. Concrete tests cover structural modes, line-end
and per-tap boundaries, and pairwise taps; Verilator AST plus Z3 proves the
complete reviewed relation. The line buffer stays at the C caller boundary,
and the adapter must short-circuit unused component lanes before reading
`origLine`. This is now the 16-component stable library frontier.

## Continuous CI/CD library loop

The executable migration agent discovers work from facts, contracts, callgraph,
frame scripts, reviewed PDF/source evidence, and valid cache receipts. It has
no function-name allowlist, SVRT integration, or second orchestrator. The
durable per-function regression service uses `DSC_REGRESSION_ROOT`; its queue,
run receipts, vectors, and large logs remain on that configured SMB-backed
root. The repository stores compact CI receipts, indexes, reports, and
accepted RTL references under `ci/`, `artifacts/`, `integration/`, and
`reports/`; candidate bundles, temporary vectors, build trees, and verbose
logs stay under the external root. Run
`python3 tools/repo_hygiene.py check` or `python3 tools/dashboard.py check`
before handoff; the dashboard check fails if transient/generated material is
tracked.

```sh
python3 tools/cicd_agent.py plan
python3 tools/cicd_agent.py run
python3 tools/cicd_agent.py status
```

For a bounded parallel refresh of the currently reviewed stable frontier, use
routing metadata only; the contract IDs still come from the tool-selected
ready plan:

```sh
DSC_CICD_REFRESH_STABLE=1 DSC_CICD_MAX_NEW=4 \
DSC_CICD_CONTRACT_WORKERS=4 DSC_CICD_WORKERS=8 \
DSC_CICD_SHARDS=8 DSC_CICD_GENERATOR_CMD='python3 tools/generator_fixture.py' \
python3 tools/cicd_agent.py run
```

The default frame gate uses three smoke profiles. Set
`DSC_CICD_MATRIX_SCOPE=all` for a full data-driven sweep of every discovered
`bittrue_smoke/run_c_baseline*.sh` profile. Each script's `expected_hash=` or
`expected=` SHA-256 is parsed into the receipt and independently checked in
all three execution modes; any future profile without a fixed SHA is labeled
`C_BASELINE_DIFFERENTIAL_ONLY` and excluded from promotion evidence.

The frame gate is Decode-first after fixture preparation. For every selected
profile, the immutable original C decoder first produces the decoded-frame
oracle. The same `.dsc` is then decoded in `C_ONLY`, `SHADOW`, and
`RTL_RETURN` using the Verilog candidate compiled to C++ by Verilator. Decoded
frames are compared byte-for-byte. Every generated overlay emits an exit-time
invocation receipt, so a candidate that was not called is reported as
`NOT_REACHED` and cannot masquerade as replacement evidence. Encode runs
second and retains the fixed `.dsc` SHA-256 gates. Rust is not part of either
oracle or replacement path.

### Decode frontier and integration

Decoder runtime discovery can be refreshed independently with LLVM coverage:

```sh
python3 tools/run_coverage.py \
  --model-root "$DSC_MODEL_ROOT" --output-dir coverage/decode \
  --work-dir "$DSC_COVERAGE_WORK" --timeout 1800 \
  --functions facts/functions.json --candidates facts/candidates.json \
  --build-receipt facts/build-receipt.json \
  --coverage-scripts all --coverage-phases decode

python3 tools/decode_frontier.py \
  --coverage coverage/decode/coverage.json \
  --functions facts/functions.json --candidates facts/candidates.json \
  --manifest library/manifest.json --source-dir "$DSC_SOURCE_DIR" \
  --provisional-root rtl/decode-candidates \
  --integration-receipt \
    rtl/decode-integration/whole-frame-multi-rtl/matrix-receipt.json \
  --output coverage/decode/frontier.json \
  --report reports/decode-rtl-frontier.md
```

This profile excludes encoder fixture execution before merging LLVM data. If
the existing combinational frontier is exhausted, the frontier tool may select
a provisional explicit state-transition shape. Such RTL may be generated and
run through full-frame C/Verilator regression, but remains outside
`library/rtl/` until its state contract is reviewed. The provisional scan is
recursive and accepts only `all`-scope PASS receipts, so a verified lower-level
transition can unlock a caller without being mistaken for stable/promoted RTL.
Current structural classes cover bounded bitstream and FIFO read/write state,
composed FIFO accounting/refill, scalar record next-state, sampled lookup
taps, scalar state plus explicit indexed-memory writes, composed flatness
state, bounded reconstructed-line scatter writes, and complete 32-entry ICH
memory transitions (including a guarded reconstructed-line sampling caller),
plus source-ordered parent composition over complete decoder/FIFO state images.
Fixed-capacity FIFO ports canonicalize bytes beyond the active `size / 8`
extent and never compare or commit those inactive backing bytes.
Selection remains based on Clang USRs/facts and decoder execution counts,
never a function-name list.

```sh
python3 tools/generate_decode_transition.py \
  --frontier coverage/decode/frontier.json \
  --functions facts/functions.json --source-dir "$DSC_SOURCE_DIR" \
  --output-dir rtl/decode-candidates/selected-transition-N

DSC_CICD_MATRIX_SCOPE=all python3 tools/verify_decode_transition.py \
  --root . --artifact rtl/decode-candidates/selected-transition-N
```

Once individual Decode transitions have full-matrix receipts, the simultaneous
integration gate discovers every Decode-exercised PASS candidate and links all
of their Verilator-generated C++ models into one copied source model. It does
not use a function allowlist. The immutable original C decoder produces each
frame oracle first; the integrated executable then runs `C_ONLY`, `SHADOW`, and
`RTL_RETURN` against the same fixtures, records named metrics for every
replacement, and requires every decoded frame to match byte-for-byte.

```sh
python3 tools/verify_decode_integration.py \
  --root . \
  --artifact rtl/decode-integration/whole-frame-multi-rtl \
  --scope all --jobs 4
```

The current authoritative `all`-scope receipt covers 29 simultaneous Verilog
replacements across 22 Decode profiles. `SHADOW` and `RTL_RETURN` each made
43,345,758 instrumented boundary calls and 4,449,264 Verilator invocations,
with zero candidate mismatches and zero decoded-frame differences. Decoder
coverage also reaches six non-datapath C boundaries: frame/process I/O
orchestration, memory lifecycle, and a thin call wrapper. They remain in C by
structural effect classification; the current unresolved Decode compute
frontier is zero.

### Encode frontier and integration

The Encode frontier starts from the tool-discovered `DSC_Encode` root graph,
Encode execution counts, Clang effects, the stable manifest, and hash-verified
provisional receipts. Refresh it without a function allowlist:

```sh
python3 tools/encode_frontier.py \
  --coverage coverage/coverage.json \
  --functions facts/functions.json \
  --candidates facts/candidates.json \
  --manifest library/manifest.json \
  --source-dir "$DSC_SOURCE_DIR" \
  --provisional-root rtl \
  --integration-receipt \
    rtl/encode-integration/whole-frame-multi-rtl/matrix-receipt.json \
  --output coverage/encode/frontier.json \
  --report reports/encode-rtl-frontier.md

python3 tools/verify_encode_integration.py \
  --root . \
  --artifact rtl/encode-integration/whole-frame-multi-rtl \
  --scope all --jobs 6
```

The current frontier reaches 44 Encode functions: 39 RTL compute boundaries
(15 stable and 24 provisional), five C orchestration/lifecycle shells, and
zero compute gaps. The authoritative 22-profile receipt links all 39 Verilog
replacements into the copied full-frame source model. `C_ONLY` made 89,066,025
instrumented calls and no RTL calls. `SHADOW` and `RTL_RETURN` each made
160,636,518 calls and 30,978,137 Verilator invocations; 32 candidates executed
directly and seven were hash-pinned, source-ordered children absorbed by a
parent RTL boundary. Candidate mismatches, encoded-frame byte differences,
and SHA-256 differences are all zero.

The three-profile smoke scope is only a development gate: it may not reach a
branch-specific boundary such as the VBR-only encoder-buffer removal path.
Only the `all`-scope receipt is authoritative for zero-gap replacement. This
provisional result remains `BLOCKED_PENDING_HUMAN_CONTRACT_REVIEW`; it does not
promote stateful RTL into `library/rtl/`.

New/repair contracts get their own generator invocation, C oracle, Verilator
candidate build, parallel differential shards, caller composition check, and
frame matrix. A stable refresh first hash-checks the matching PASS component
in `library/manifest.json` and reuses its accepted `library/rtl/` file as the
sole candidate, so it runs the same deterministic gates with zero generator or
model calls. A missing or changed accepted file is an infrastructure failure,
not an implicit regeneration request. A candidate becomes promotion-eligible
only after unit, formal-or-exhaustive, dependency,
`C_ONLY`/`SHADOW`/`RTL_RETURN`, source, and exact spec gates. Stable-library
promotion additionally requires an explicit human approval receipt at
`ci/promotion-approvals/<contract-id>/<contract-hash>.json`, bound to the
exact canonical RTL, source/spec/interface hashes, design intent, QoR review,
reviewer, and all gate decisions. The agent never creates that receipt and
never auto-promotes a new or repaired candidate: without it the result is
`AWAITING_HUMAN_APPROVAL` and the library is unchanged. After approval, only
stable, purely combinational DUT leaves are written to `library/rtl/` with
their locked contract and verification receipt. The agent canonicalizes the
module, archives replacements, and updates the manifest under a library write
lock; stateful callers, line storage, and other non-DUT C logic remain
reference boundaries. Existing PASS manifest entries are a grandfathered
stable baseline; their accepted-RTL refresh is verification-only and reports
`VERIFIED_REFRESH` without rewriting the library.

Accepted leaves with stale source/spec/contract/dependency, controller, prompt,
generator, or tool hashes automatically enter a bounded regression frontier;
valid cache entries are reused without regeneration. Stale stable entries reuse
accepted RTL and rerun verification rather than regenerating RTL. A deliberate
new RTL attempt requires explicit queue routing with
`DSC_CICD_FORCE_REGENERATE=1`. `DSC_CICD_REFRESH_STABLE=1` is available when
the entire reviewed stable frontier must be verification-refreshed.

If a completed receipt records `COMPOSITION_BLOCKED` with a `C_BOUNDARY`
composition, the planner keeps that boundary visible and does not invoke the
generator again for the same source/spec/contract/dependency identity. A
changed semantic input reopens the contract automatically; an intentional
retry may set `DSC_CICD_RETRY_BLOCKED=1` (or use explicit queue routing). The
agent never invents a pointer/state adapter or passes dummy caller state just
to make RTL composition compile.

Composition validation uses the generated deterministic caller adapter, not a
raw comparison between native C call-site arity and frozen RTL input count. A
native caller may pass one pointer/state aggregate while a reviewed adapter
binds its read-only fields or windows to several frozen scalar ports. The
adapter must bind every frozen port exactly once and record both native arity
and adapter bindings; only an adapter that cannot provide the complete frozen
DUT interface remains a `C_BOUNDARY`.

If a process stops after entering an executable stage, durable history requeues
that exact contract even when hashes are unchanged. If verification completes
before human approval, the planner retains the exact candidate and resumes it
after the matching approval receipt appears without a generator or model call;
a missing or mismatched pending artifact fails closed as infrastructure.

## Human-readable regression dashboard

The receipt-backed dashboard is a reporting and traceability view; JSON
receipts remain authoritative and no new RTL regression is launched by the
dashboard. Build it from the latest indexed run with:

```sh
python3 tools/dashboard.py build --run latest
python3 tools/dashboard.py check
python3 tools/dashboard.py serve
python3 tools/regression.py report <run-id>
```

`DSC_REGRESSION_ROOT` is preferred when set. Otherwise the builder uses the
mounted regression share when available and visibly falls back to repository
local receipts. Open `dashboard/index.html` for the overview, then use
`dashboard/functions/<contract-id>.html`, `dashboard/history.html`, and
`dashboard/traceability.html` for details. The overview also shows the current
tool-selected CI ready frontier, candidate queue, and blockers from
`ci/plan.json`, `ci/state.json`, and `summary.json`; a green selected regression
run cannot hide a pending human review or traceability orphan. The traceability
page keeps `PROPOSED` links and orphan lists visibly unresolved until human
review. `DIRECTORY_LAYOUT.md` explains the new
run/library meanings and `path-map.json` keeps legacy paths readable without
copying large RTL or verification files.

## Environment

Set `DSC_ANALYSIS_TIMEOUT_SECONDS` for compiler/Clang/Frama-C commands,
`DSC_BUILD_TIMEOUT_SECONDS` for the isolated build/smoke gate, and
`DSC_ANALYSIS_TOP_N` for the bounded contract/candidate count. The CI/CD verifier also
accepts `DSC_CICD_SHARDS`, `DSC_CICD_GENERATOR_CMD`, and compile/shard timeout
variables. `DSC_CICD_ARTIFACT_ROOT` may explicitly select an external per-flow
artifact directory; `run.sh` derives one under `DSC_REGRESSION_ROOT` when
`DSC_RUN_CICD=1`. Temporary model copies exclude the unrelated `dsc-rs` and
`operator_bittrue` trees; the local PDF and upstream C source remain outside
the repository and are never edited. `run.sh` records the analysis-tool
preflight in compact `build/analysis-preflight.json` after the C gate and
before clearing facts; both `run.sh` and the receipt producer resolve the
standard Homebrew LLVM paths and record whether each tool came from explicit
configuration, Homebrew, `PATH`, or an already-installed Opam switch for
Frama-C. They never install or initialize a package manager during a run.
Missing Frama-C/LLVM tools are visible in the dashboard/report. `run.sh`
refreshes and checks the static dashboard after a successful run and after a
preflight failure, so the latest blocker is visible without hand-editing
receipts.
