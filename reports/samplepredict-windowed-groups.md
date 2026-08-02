# SamplePredict multi-group differential run

This is the next exploratory receipt for the tool-discovered
`c:@F@SamplePredict` leaf. It remains outside the stable library because the
reviewed RTL window is deliberately smaller than the production line-buffer
domain.

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
- `candidate_01`: independent Verilator-AST/Z3 proof `PASS` over the complete reviewed relation (140 constraints)
- `candidate_02`: independent proof `COUNTEREXAMPLE` (`hPos=0`, `predType=14`, `qLevel=5`)
- compact receipt: `artifacts/e7095d17e58206f007e7d9a28c7832ca724b33ebabcdea37b2c690ffb31c64f8/`
- overlay C compile: `PASS`; immutable upstream source hash unchanged
- frame gates: `C_ONLY=PASS`, `SHADOW=FAIL`, `RTL_RETURN=FAIL`
- first frame boundary: production calls reach `hPos=12`, while the reviewed scalar window is `hPos=0..11`; the candidate falls back to group-0 taps and is rejected
- promotion: withheld; stable `library/manifest.json` is unchanged

The adapter keeps stateful line storage and caller state in the C boundary. The
formal proof is complete for the declared window, but that window is not the
whole production function. The next frontier is a spec-grounded array/window
interface (or a smaller exact block/MMAP slice) whose frame integration covers
the full caller domain without moving line-buffer state into the DUT.
