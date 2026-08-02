# DSC 1.2a C model analysis

This standalone repository analyzes the local DSC 1.2a C reference model and
links tool-discovered C facts back to the local PDF specification. It is
isolated from SVRT and unrelated projects. It does not modify the upstream
model or copy the PDF. The pipeline also uses LLVM coverage, creates three
tool-selected contracts, and verifies one small combinational RTL slice; it
does not generate whole-codec RTL or add sequential hardware.

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
and bounded computation. The top 10 (configurable with
`DSC_ANALYSIS_TOP_N`) are passed to Frama-C Eva/From when analyzable.

## Specification traceability

The primary PDF extractor is `pdfinfo` plus `pdftotext -layout`. It records page
count, headings, tables, figures, short anchors, and same-page nearest-heading
assignments for `MN_*` model notes in `spec/anchors.json`; it never stores long
PDF text.
C comments, `MN_*` model notes, explicit page/section/table references,
function ranges, constants, tables, USRs, source hashes, and fixed-commit
permalinks are recorded in `facts/comments.json`.

`traceability/links.proposed.yaml` contains generated exact/proposed links.
`traceability/links.reviewed.yaml` is the human-edited review surface and is
never overwritten. A reviewed link becomes `STALE` if either input hash
changes. Reports are bidirectional and retain visible unknowns/orphans.

After C facts are assembled, an instrumented temporary copy runs the existing
bit-true smoke and is analyzed with `llvm-profdata`/`llvm-cov`. Contracts are
selected without a function-name allowlist. A selected exact-link contract is
checked with a generated C oracle, up to four combinational SystemVerilog
candidates, Verilator, and exhaustive legal-domain enumeration. Deliberate
signedness, boundary, index, and off-by-one mutations remain visible as
counterexamples.

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
visible in `ci/plan.json` and cannot silently reuse old artifacts.

The state machine is recorded in `ci/dag.json` and `ci/state.json`. Each
contract hash gets an artifact bundle containing its frozen interface, C
oracle adapter, harness, input packing, legal-domain plan, mutations, overlay
wrapper, and receipt schema. The integration overlay supports `C_ONLY`,
`SHADOW`, and `RTL_RETURN`; the latter two compare C and RTL while the full
DSC smoke stream is checked byte-for-byte and by SHA-256. Rollback is a
manifest change back to `C_ONLY`.

Generated CI outputs are under `ci/`, `artifacts/<contract-hash>/`,
`integration/generated-overlay/`, `integration/replacement-plan.yaml`,
`integration/bitstream-receipts/`, and
`reports/pipeline-summary.md`. The upstream C model and PDF are never edited.

### Executable generator contract

The migration agent has no function-name target or implicit model stub. Tool
facts, exact traceability, and reviewed domain evidence discover the next ready
leaf; the reviewed override is matched by an exact spec anchor, not by a
function-name allowlist. A ready cache miss requires an external hook:

```sh
DSC_CICD_GENERATOR_CMD='python3 tools/generator_fixture.py' \
  python3 tools/cicd_agent.py run
```

The hook receives only `locked_contract`, `frozen_interface`, `c_body`, and
short `exact_spec_anchors`. It emits at most four combinational `.sv`
candidates plus telemetry. The fixture emits one correct and one deliberately
wrong candidate so the verifier records both an exhaustive pass and a
smallest counterexample. A missing hook records `GENERATION_REQUIRED` and
makes no model call.

The verifier compiles the immutable C oracle and every candidate once, runs
the complete legal domain through parallel shards, and writes `EXECUTED_NOW`
receipts. It then uses the Clang LibTooling rewriter to rename the discovered
definition and rewrite every direct call site in an isolated copy.
`C_ONLY`, `SHADOW`, and `RTL_RETURN` run against default, alternate-bpc, and
sampling scenarios; promotion requires all byte/SHA bitstream gates. A second
run exercises the valid cache and reports `REUSED_VERIFIED_RECEIPT` with zero
generator/model calls.

## Durable regression queue

The per-function regression service is independent of SVRT and discovers its
work from the existing facts, contracts, callgraph, frame scripts, and valid
cache receipts. It does not contain a function-name allowlist. Before a pilot,
it requires the manifest PDF gate, C front-end compile receipt, isolated clean
C build, and bit-true smoke/golden hash to be `PASS`.

The service stores queue state, flow worktrees, builds, vectors, and large logs
on the requested SMB share `//kslin@192.168.68.52/homes`. The default root is
`/Volumes/homes/dsc12a-regression`; if macOS exposes the share at a different
mountpoint, set `DSC_REGRESSION_ROOT` to a directory below that discovered
mountpoint. Credentials are never stored or printed.

```sh
python3 tools/regression.py init
python3 tools/regression.py submit --profile pilot
python3 tools/regression.py worker --jobs 4
python3 tools/regression.py poll --once
python3 tools/regression.py report <run-id>
```

The pilot is capped at four functions and two candidates per function. A
passing pilot writes a `PLANNED_NOT_STARTED` scale plan without enqueuing the
full corpus. Start a deliberate scale batch only after reviewing that plan:

```sh
DSC_REGRESSION_ROOT=<share-root> python3 tools/regression.py scale <pilot-run-id> --refresh
DSC_REGRESSION_ROOT=<share-root> python3 tools/regression.py worker --jobs 4
DSC_REGRESSION_ROOT=<share-root> python3 tools/regression.py promote <scale-run-id>
```

Scale jobs use independent per-contract flow worktrees and queue-discovered
contract IDs; no source-level function allowlist is used. `--refresh` forces a
new generator/verification attempt for the selected leaf while preserving old
receipts. Promotion copies only PASS, spec-reviewed, purely combinational DUT
RTL into `library/rtl/` with compact traceability and verification manifests.
Stateful callers, unresolved table/pointer dependencies, and non-DUT C code
remain in the immutable C reference and are not promoted. The static dashboard
is at `<root>/dashboard/index.html` and refreshes from `latest.json`; receipts
retain candidate/frame rates, exact PDF links, C spans, port traceability,
artifact links, and blockers. See
[`PROMPT.md`](PROMPT.md) and [`skills/dsc-regression/SKILL.md`](skills/dsc-regression/SKILL.md)
for the execution contract and durable workflow.

## Environment

Set `DSC_ANALYSIS_TIMEOUT_SECONDS` for compiler/Clang/Frama-C commands,
`DSC_BUILD_TIMEOUT_SECONDS` for the isolated build/smoke gate, and
`DSC_ANALYSIS_TOP_N` for the Frama-C candidate count. The CI/CD verifier also
accepts `DSC_CICD_SHARDS`, `DSC_CICD_GENERATOR_CMD`, and compile/shard timeout
variables. Temporary model copies exclude the unrelated `dsc-rs` and
`operator_bittrue` trees; the local PDF and upstream C source remain outside
the repository and are never edited.
