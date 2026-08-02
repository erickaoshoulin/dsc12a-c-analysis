# DSC Verilog library

This directory contains only RTL that passed the executable C-to-RTL gates and
was explicitly promoted from a durable regression receipt.

Promotion requires:

- exact PDF/C traceability and reviewed port authority;
- Verilator compile/lint and exhaustive legal-domain comparison;
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
