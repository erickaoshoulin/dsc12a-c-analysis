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

## Environment

Set `DSC_ANALYSIS_TIMEOUT_SECONDS` for compiler/Clang/Frama-C commands,
`DSC_BUILD_TIMEOUT_SECONDS` for the isolated build/smoke gate, and
`DSC_ANALYSIS_TOP_N` for the Frama-C candidate count. The temporary copy and
raw logs are removed after each run.
