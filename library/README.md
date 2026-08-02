# DSC Verilog library

This directory contains only RTL that passed the executable C-to-RTL gates and
was explicitly promoted from a durable regression receipt.

Promotion requires:

- exact PDF/C traceability and reviewed port authority;
- Verilator compile/lint and either exhaustive legal-domain comparison or an
  independent proof of a reviewed finite window;
- C_ONLY, SHADOW, RTL_RETURN, and discovered frame byte/SHA-256 passes; and
- no clock, reset, latch, testbench timing, or stateful caller logic in the
  promoted leaf.

The immutable C model remains the reference and C_ONLY is the rollback path.
Stateful functions, table dependencies, callers, and architecture-level logic
stay out of this library until they have their own spec-backed contract and
composition evidence. This library is independent of SVRT.

`manifest.json` is the index. `rtl/` contains canonical contract-named modules
(for example `findmidpoint`),
`verification/` contains compact promotion receipts, `contracts/` contains
traceability, and `archive/` preserves an older canonical module when a later
verified iteration replaces it.

The executable CI/CD agent writes these stable entries automatically only
after all promotion gates pass, using a library write lock and recording the
source artifact directory in the manifest and receipt.

`samplepredict` is the first production-domain relative-window leaf: its C
line-buffer state remains at the caller boundary, while the RTL consumes the
reviewed MMAP/left/block predictor taps.

`qp2qlevel` is a configuration-library primitive, not production codec-output
DUT logic. It is the reviewed DSC 1.2a Table 6-2 qLevel lookup, with its C
configuration pointer flattened into finite read-only ports and its legal QP
range constrained to each normative table row.

Reviewed pointer-heavy leaves use a data-driven window contract. The
`windowed_boundary` strategy covers structural, boundary, and pairwise tap
cases, while independent Verilator-AST/Z3 proof is required before a reviewed
window can become `FORMAL_EQUIVALENT`. For a `flatness_window`, the contract
declares four component lanes and seven read-only original-pixel taps per
lane, including Figure 6-19 check-1 offsets `0..3` and check-2 offsets `1..6`.
Table 6-2, the qLevel adjustment, and `flatnessDetThresh` relation are locked
in reviewed semantics. Line storage stays at the C caller boundary, and the
adapter short-circuits inactive lanes before dereferencing `origLine`. The
stable library now contains 14 promoted components.
