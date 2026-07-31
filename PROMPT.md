# Standalone DSC 1.2a analysis prompt

Use the local public VESA DSC 1.2a specification and the public DSC 1.2a C
reference model to produce a deterministic, rerunnable analysis repository.

The repository is standalone. Do not assume or modify SVRT, RTL, sequential
hardware, or any unrelated project. Do not add a handwritten C parser and do
not call an LLM as a fallback.

## Required workflow

1. Locate and record the applicable local PDF/specification metadata. The
   current local reference is `DSC_v1.2a.pdf`, VESA DSC Standard Version 1.2a.
2. Generate `compile_commands.json` from the public model's build inputs.
3. Run the compiler front end over every C translation unit in the compilation
   database. A successful analysis requires every command to pass
   `-fsyntax-only`; missing tools, bad includes, timeouts, or a failed command
   are `INFRASTRUCTURE_FAILURE` after one deterministic retry.
4. Use Clang LibTooling/AST Matchers to discover every defined C function from
   the translation units. The function inventory must come from the AST facts;
   function names must not be embedded in the collector or used as a parser
   substitute.
5. Use `analysis-profile.json` only to select optional focused entry points
   from that discovered inventory for Frama-C Eva/From. If the profile is empty,
   the runner must be able to use the complete discovered inventory.
6. Retain unknowns as `UNKNOWN`; do not infer facts from naming conventions.

## Required facts

For each discovered function, record its source location, Clang USR, callers,
callees, parameters, return type, global and struct field reads/writes, pointer
write mode, static mutable state, file I/O/logging/assert/malloc effects, loops
and trip-count proofs, return dependencies, Eva ranges/checks, warnings,
unknowns, and purity/combinational proposals with evidence.

The focused profile currently compares Qp2Qlevel with MapQpToQlevel and covers
the seven codec helpers named in the profile. These names define analysis
scope only; they do not define the function inventory.

## Guardrails

Do not modify upstream C source. Do not generate RTL. Do not simplify `cpnt % 3`
unless a caller-specific range is proven. Keep all source/tool revisions,
compile-check receipts, source hashes, and a semantic hash in the outputs.
