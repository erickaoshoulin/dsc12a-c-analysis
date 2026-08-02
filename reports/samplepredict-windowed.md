# SamplePredict windowed differential run

This is an exploratory frontier receipt for the tool-discovered
`c:@F@SamplePredict` leaf. It is not a stable-library promotion.

- PDF: local DSC 1.2a, SHA-256 `724c0979b0a04bb9a5ad7143755bf6fab4bf8cf9598d24a536a5048a66e2aecd`
- C source: immutable DSC model, SHA-256 `1cd2ac33e983d1489b2fcc5e138324efba18069db5a6bbe72f6cce3b7d8b9cdf`
- exact anchors: sections 6.4.1, 6.4.1.1, 6.4.1.2, and 6.4.2
- frozen interface: 21 scalar inputs plus one 16-bit output; read-only state/tap bindings only
- vectors: 708,120 across 8 shards with 8 workers
- structural cases: 44,280; strategy: `windowed_boundary`
- C oracle: all source translation units compiled and linked successfully
- `candidate_01`: `DIFFERENTIAL_PASS` over all 708,120 vectors
- `candidate_02`: `COUNTEREXAMPLE`, mutation caught at the first vector (`expected=127`, `actual=128`)
- compact receipt: `artifacts/b384a0ea6cd610d0d2efeb99c88954750f8ccda00d3ceaa7147589d9f24f250a/`
- promotion: withheld because `exhaustive=false`; no SamplePredict RTL entered `library/`

Next iteration: expand the window mapping beyond the first three-sample group,
cover the RGB chroma bit-depth extension explicitly, and seek a formal or
smaller spec-grounded proof boundary before promotion.
