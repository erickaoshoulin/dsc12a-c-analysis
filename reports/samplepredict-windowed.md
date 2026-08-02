# SamplePredict production relative-window promotion

`SamplePredict` is now promoted as the tenth stable combinational leaf. The
caller still owns the C line-buffer state; the RTL boundary receives only the
spec-defined relative taps needed by MMAP, left prediction, and the 13-sample
block predictor.

- PDF: local DSC 1.2a, SHA-256 `724c0979b0a04bb9a5ad7143755bf6fab4bf8cf9598d24a536a5048a66e2aecd`, 145 pages
- C source: immutable DSC model, SHA-256 `1cd2ac33e983d1489b2fcc5e138324efba18069db5a6bbe72f6cce3b7d8b9cdf`
- exact anchors: sections 6.4.1, 6.4.1.1, 6.4.1.2, and 6.4.2
- legal `hPos`: `0..65534`; concrete boundary strategy: 25,960,080 vectors across 8 shards
- C oracle: all 11 translation units compiled and linked; all 8 C/RTL shards passed
- formal RTL gate: `PASS`, `proof_complete=true`, 1,002 structural partitions checked with Verilator AST + Z3
- mutation: `candidate_02` rejected by differential and formal counterexample (`expected=127`, `actual=128`)
- caller frame modes: `C_ONLY`, `SHADOW`, and `RTL_RETURN` all `PASS`
- dependency composition: 5 tool-discovered call sites, C callee, RTL callee, and caller frame all `PASS`

The canonical module is [library/rtl/samplepredict.sv](../library/rtl/samplepredict.sv),
with its reviewed contract and promotion receipt in `library/contracts/` and
`library/verification/`. Temporary vector shards remain outside the check-in.
