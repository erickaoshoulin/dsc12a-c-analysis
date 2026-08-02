# SamplePredict multi-group differential run

This is the next exploratory receipt for the tool-discovered
`c:@F@SamplePredict` leaf. It remains outside the stable library because the
concrete value space is bounded by reviewed boundary probes, not exhaustively
enumerated.

- PDF: local DSC 1.2a, SHA-256 `724c0979b0a04bb9a5ad7143755bf6fab4bf8cf9598d24a536a5048a66e2aecd`
- C source: immutable DSC model, SHA-256 `1cd2ac33e983d1489b2fcc5e138324efba18069db5a6bbe72f6cce3b7d8b9cdf`
- exact anchors: sections 6.4.1, 6.4.1.1, 6.4.1.2, 6.4.2, plus Table 6-2
- frozen interface: 35 scalar inputs plus one 16-bit output
- window: `hPos=0..11`, four three-sample groups, `prevLine[3..17]`, `currLine[0..15]`
- component depths: 8..16 bpc, including the model's RGB chroma +1-bit extension
- structural cases: 249,120; strategy: `windowed_boundary`
- vectors: 11,584,800 across 8 shards with 8 workers
- C oracle: all source translation units compiled and linked successfully
- `candidate_01`: `DIFFERENTIAL_PASS` over all vectors
- `candidate_02`: `COUNTEREXAMPLE`, caught at the first vector (`expected=127`, `actual=128`)
- compact receipt: `artifacts/e7095d17e58206f007e7d9a28c7832ca724b33ebabcdea37b2c690ffb31c64f8/`
- promotion: withheld because `exhaustive=false`; stable `library/manifest.json` is unchanged

The adapter keeps stateful line storage and caller state in the C boundary. The
next proof frontier is either a formal equivalence argument for this declared
window or a smaller exact block/MMAP slice with a complete legal domain.
