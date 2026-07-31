# DSC 1.2a C model analysis

This standalone repository contains a small, rerunnable structural analysis of
the public DSC 1.2a C reference model. It produces deterministic facts for
later DUT mining and LLM work. It does not modify the upstream model, generate
RTL, introduce a C parser, or make a sequential-hardware claim.

## Scope

The default source is:

```text
DSC_model_20210623/source/
```

The nested public-model revision and hashes are recorded in every JSON fact
file. Override the source location without changing the experiment:

```sh
DSC_SOURCE_DIR=/path/to/DSC_model_20210623/source ./run.sh
```

The focused targets are `Qp2Qlevel`, `MapQpToQlevel`, `QuantizeResidual`,
`FindResidualSize`, `SampToLineBuf`, `MaxResidualSize`, and
`GetQpAdjPredSize`. Clang collects facts for every C function in the generated
compilation database; Eva and From are run only for those seven entry points.

## Method

1. `tools/generate_compile_commands.py` emits a stable `facts/compile_commands.json`
   from the public model's C translation units.
2. `clang_facts.cpp` uses Clang LibTooling and AST Matchers for function USRs,
   calls, global/field accesses, pointer writes, effects, loops, return
   expressions, constant table initializers, and operator evidence.
3. `run_frama.py` runs focused Frama-C Eva and From commands. Eva warnings are
   retained for bounds, shifts, signed overflow, pointer validity, and
   unreachable-branch checks. From output is retained for return and modified
   memory dependencies.
4. `assemble_facts.py` combines only the tool outputs into JSON facts and
   Markdown reports. It never lexes or parses C text.

The focused Frama-C invocation excludes the command-line/platform glue units
`cmd_parse.c`, `dpx.c`, `hdr_dpx.c`, and `logging.c`: their host-specific
headers or dynamic DPX layout are outside the seven helper entry points and
cannot be consumed by this Frama-C parser configuration. The Clang collection
still covers every translation unit in the compile database, and the exact
exclusion list is recorded in the Frama manifest and fact metadata.

The generated timestamp is excluded from `metadata.semantic_hash`. A missing
proof is recorded as `UNKNOWN`; no `% 3` simplification is proposed until a
caller-specific `cpnt` range is proved. Struct roles are per-field proposals:
`dsc_cfg_t` is not treated as one static-configuration object, and
`dsc_state_t` table pointers, runtime state, and model-only data are kept
separate or explicitly left unknown.

## Run

```sh
./run.sh
```

The script performs the same command at most twice. It stops with
`INFRASTRUCTURE_FAILURE` for missing source, compile database errors, missing
Clang/LibTooling, missing Frama-C, include/configuration errors, timeout, or
disk/write failures. It does not call an LLM or invoke a fallback parser.

Set `DSC_ANALYSIS_TIMEOUT_SECONDS` to change the per-command timeout. The
temporary build and raw logs are outside the repository and are removed after
the run.

## Outputs

```text
facts/
  compile_commands.json
  functions.json
  callgraph.json
  field-access.json
  loops.json
  value-ranges.json
  dependencies.json
reports/
  function-summary.md
  field-summary.md
  candidate-functions.md
  unresolved.md
summary.json
```

Each JSON file contains `metadata` with the DSC source revision, source file
hashes, the consumed `compile_commands.json` hash, Clang and Frama-C versions,
analysis commands, semantic hash, and generated timestamp. `summary.json` also records the Qp2Qlevel/MapQpToQlevel
comparison, quantization-table initialization/use evidence, loop facts, and
the candidate count gate.

## Limitations

Eva's `NO_ALARM_OBSERVED_NOT_PROOF` status is intentionally not rewritten as a
proof. Entry-point parameter ranges can remain unknown without a contract;
From can similarly leave return or modified-memory dependencies unknown when
the plugin does not emit a parseable dependency line. These limitations are
listed in `reports/unresolved.md`.
