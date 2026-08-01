# Auto-discovered DUT candidates

Candidate selection is derived from the linked executable entry symbol, Clang call/dataflow facts, effects, and loop proofs. No source function-name allowlist is used.

- Source functions: 194
- Production reachable: 167
- Output contributing: 57
- Eligible candidates: 10
- Selected for Eva/From: 10

## Ranked candidates

### 1. `FindMidpoint`

- Score: `100.0`; confidence: `0.95`; role: `DUT`
- Purity: `PURE`; timing: `COMBINATIONAL`; bounded: `True`
- Production reachable: `True`; output contributing: `True`
- Source: `dsc_codec.c:906`
- Eligible: `True`
- Evidence:
  - production reachability is a graph traversal from linked executable entry symbols
  - observable output is inferred from output file calls and codec boundary dataflow shape
  - direct effects: {"allocation": false, "assertion": false, "indirect_call": false, "io": false, "logging": false, "state_write": false, "unknown_facts": []}
  - transitive effects: {"allocation": false, "assertion": false, "indirect_call": false, "io": false, "logging": false, "state_write": false, "unknown_facts": []}
  - all reachable loops have fixed AST bounds

### 2. `IsFlatnessInfoSent`

- Score: `100.0`; confidence: `0.95`; role: `DUT`
- Purity: `PURE`; timing: `COMBINATIONAL`; bounded: `True`
- Production reachable: `True`; output contributing: `True`
- Source: `dsc_codec.c:1116`
- Eligible: `True`
- Evidence:
  - production reachability is a graph traversal from linked executable entry symbols
  - observable output is inferred from output file calls and codec boundary dataflow shape
  - direct effects: {"allocation": false, "assertion": false, "indirect_call": false, "io": false, "logging": false, "state_write": false, "unknown_facts": []}
  - transitive effects: {"allocation": false, "assertion": false, "indirect_call": false, "io": false, "logging": false, "state_write": false, "unknown_facts": []}
  - all reachable loops have fixed AST bounds

### 3. `MapQpToQlevel`

- Score: `100.0`; confidence: `0.95`; role: `DUT`
- Purity: `PURE`; timing: `COMBINATIONAL`; bounded: `True`
- Production reachable: `True`; output contributing: `True`
- Source: `dsc_codec.c:221`
- Eligible: `True`
- Evidence:
  - production reachability is a graph traversal from linked executable entry symbols
  - observable output is inferred from output file calls and codec boundary dataflow shape
  - direct effects: {"allocation": false, "assertion": false, "indirect_call": false, "io": false, "logging": false, "state_write": false, "unknown_facts": []}
  - transitive effects: {"allocation": false, "assertion": false, "indirect_call": false, "io": false, "logging": false, "state_write": false, "unknown_facts": []}
  - all reachable loops have fixed AST bounds

### 4. `PredictSize`

- Score: `100.0`; confidence: `0.95`; role: `DUT`
- Purity: `PURE`; timing: `COMBINATIONAL`; bounded: `True`
- Production reachable: `True`; output contributing: `True`
- Source: `dsc_codec.c:1476`
- Eligible: `True`
- Evidence:
  - production reachability is a graph traversal from linked executable entry symbols
  - observable output is inferred from output file calls and codec boundary dataflow shape
  - direct effects: {"allocation": false, "assertion": false, "indirect_call": false, "io": false, "logging": false, "state_write": false, "unknown_facts": []}
  - transitive effects: {"allocation": false, "assertion": false, "indirect_call": false, "io": false, "logging": false, "state_write": false, "unknown_facts": []}
  - all reachable loops have fixed AST bounds

### 5. `QuantizeResidual`

- Score: `100.0`; confidence: `0.95`; role: `DUT`
- Purity: `PURE`; timing: `COMBINATIONAL`; bounded: `True`
- Production reachable: `True`; output contributing: `True`
- Source: `dsc_codec.c:245`
- Eligible: `True`
- Evidence:
  - production reachability is a graph traversal from linked executable entry symbols
  - observable output is inferred from output file calls and codec boundary dataflow shape
  - direct effects: {"allocation": false, "assertion": false, "indirect_call": false, "io": false, "logging": false, "state_write": false, "unknown_facts": []}
  - transitive effects: {"allocation": false, "assertion": false, "indirect_call": false, "io": false, "logging": false, "state_write": false, "unknown_facts": []}
  - all reachable loops have fixed AST bounds

### 6. `SampToLineBuf`

- Score: `100.0`; confidence: `0.95`; role: `DUT`
- Purity: `PURE`; timing: `COMBINATIONAL`; bounded: `True`
- Production reachable: `True`; output contributing: `True`
- Source: `dsc_codec.c:2036`
- Eligible: `True`
- Evidence:
  - production reachability is a graph traversal from linked executable entry symbols
  - observable output is inferred from output file calls and codec boundary dataflow shape
  - direct effects: {"allocation": false, "assertion": false, "indirect_call": false, "io": false, "logging": false, "state_write": false, "unknown_facts": []}
  - transitive effects: {"allocation": false, "assertion": false, "indirect_call": false, "io": false, "logging": false, "state_write": false, "unknown_facts": []}
  - all reachable loops have fixed AST bounds

### 7. `SamplePredict`

- Score: `100.0`; confidence: `0.95`; role: `DUT`
- Purity: `PURE`; timing: `COMBINATIONAL`; bounded: `True`
- Production reachable: `True`; output contributing: `True`
- Source: `dsc_codec.c:308`
- Eligible: `True`
- Evidence:
  - production reachability is a graph traversal from linked executable entry symbols
  - observable output is inferred from output file calls and codec boundary dataflow shape
  - direct effects: {"allocation": false, "assertion": false, "indirect_call": false, "io": false, "logging": false, "state_write": false, "unknown_facts": []}
  - transitive effects: {"allocation": false, "assertion": false, "indirect_call": false, "io": false, "logging": false, "state_write": false, "unknown_facts": []}
  - all reachable loops have fixed AST bounds

### 8. `EscapeCodeSize`

- Score: `99.95`; confidence: `0.95`; role: `DUT`
- Purity: `PURE`; timing: `COMBINATIONAL`; bounded: `True`
- Production reachable: `True`; output contributing: `True`
- Source: `dsc_codec.c:443`
- Eligible: `True`
- Evidence:
  - production reachability is a graph traversal from linked executable entry symbols
  - observable output is inferred from output file calls and codec boundary dataflow shape
  - direct effects: {"allocation": false, "assertion": false, "indirect_call": false, "io": false, "logging": false, "state_write": false, "unknown_facts": []}
  - transitive effects: {"allocation": false, "assertion": false, "indirect_call": false, "io": false, "logging": false, "state_write": false, "unknown_facts": []}
  - all reachable loops have fixed AST bounds

### 9. `MaxResidualSize`

- Score: `99.95`; confidence: `0.95`; role: `DUT`
- Purity: `PURE`; timing: `COMBINATIONAL`; bounded: `True`
- Production reachable: `True`; output contributing: `True`
- Source: `dsc_codec.c:263`
- Eligible: `True`
- Evidence:
  - production reachability is a graph traversal from linked executable entry symbols
  - observable output is inferred from output file calls and codec boundary dataflow shape
  - direct effects: {"allocation": false, "assertion": false, "indirect_call": false, "io": false, "logging": false, "state_write": false, "unknown_facts": []}
  - transitive effects: {"allocation": false, "assertion": false, "indirect_call": false, "io": false, "logging": false, "state_write": false, "unknown_facts": []}
  - all reachable loops have fixed AST bounds

### 10. `GetQpAdjPredSize`

- Score: `99.9`; confidence: `0.95`; role: `DUT`
- Purity: `PURE`; timing: `COMBINATIONAL`; bounded: `True`
- Production reachable: `True`; output contributing: `True`
- Source: `dsc_codec.c:278`
- Eligible: `True`
- Evidence:
  - production reachability is a graph traversal from linked executable entry symbols
  - observable output is inferred from output file calls and codec boundary dataflow shape
  - direct effects: {"allocation": false, "assertion": false, "indirect_call": false, "io": false, "logging": false, "state_write": false, "unknown_facts": []}
  - transitive effects: {"allocation": false, "assertion": false, "indirect_call": false, "io": false, "logging": false, "state_write": false, "unknown_facts": []}
  - all reachable loops have fixed AST bounds

### 11. `ceil_log2`

- Score: `80.0`; confidence: `0.75`; role: `DUT`
- Purity: `PURE`; timing: `UNKNOWN`; bounded: `False`
- Production reachable: `True`; output contributing: `True`
- Source: `dsc_utils.c:67`
- Eligible: `False`
- Evidence:
  - production reachability is a graph traversal from linked executable entry symbols
  - observable output is inferred from output file calls and codec boundary dataflow shape
  - direct effects: {"allocation": false, "assertion": false, "indirect_call": false, "io": false, "logging": false, "state_write": false, "unknown_facts": []}
  - transitive effects: {"allocation": false, "assertion": false, "indirect_call": false, "io": false, "logging": false, "state_write": false, "unknown_facts": []}
  - at least one reachable loop has UNKNOWN bounds

### 12. `getbits`

- Score: `80.0`; confidence: `0.75`; role: `DUT`
- Purity: `PURE`; timing: `UNKNOWN`; bounded: `False`
- Production reachable: `True`; output contributing: `True`
- Source: `dsc_utils.c:109`
- Eligible: `False`
- Evidence:
  - production reachability is a graph traversal from linked executable entry symbols
  - observable output is inferred from output file calls and codec boundary dataflow shape
  - direct effects: {"allocation": false, "assertion": false, "indirect_call": false, "io": false, "logging": false, "state_write": false, "unknown_facts": []}
  - transitive effects: {"allocation": false, "assertion": false, "indirect_call": false, "io": false, "logging": false, "state_write": false, "unknown_facts": []}
  - at least one reachable loop has UNKNOWN bounds

### 13. `FindResidualSize`

- Score: `79.95`; confidence: `0.75`; role: `DUT`
- Purity: `IMPURE`; timing: `COMBINATIONAL`; bounded: `True`
- Production reachable: `True`; output contributing: `True`
- Source: `dsc_codec.c:1078`
- Eligible: `False`
- Evidence:
  - production reachability is a graph traversal from linked executable entry symbols
  - observable output is inferred from output file calls and codec boundary dataflow shape
  - direct effects: {"allocation": false, "assertion": false, "indirect_call": false, "io": false, "logging": true, "state_write": false, "unknown_facts": []}
  - transitive effects: {"allocation": false, "assertion": false, "indirect_call": false, "io": false, "logging": true, "state_write": false, "unknown_facts": []}
  - all reachable loops have fixed AST bounds

### 14. `IsOrigFlatHIndex`

- Score: `79.95`; confidence: `0.75`; role: `DUT`
- Purity: `PURE`; timing: `UNKNOWN`; bounded: `False`
- Production reachable: `True`; output contributing: `True`
- Source: `dsc_codec.c:1126`
- Eligible: `False`
- Evidence:
  - production reachability is a graph traversal from linked executable entry symbols
  - observable output is inferred from output file calls and codec boundary dataflow shape
  - direct effects: {"allocation": false, "assertion": false, "indirect_call": false, "io": false, "logging": false, "state_write": false, "unknown_facts": []}
  - transitive effects: {"allocation": false, "assertion": false, "indirect_call": false, "io": false, "logging": false, "state_write": false, "unknown_facts": []}
  - at least one reachable loop has UNKNOWN bounds

### 15. `fifo_free`

- Score: `79.95`; confidence: `0.75`; role: `DUT`
- Purity: `IMPURE`; timing: `COMBINATIONAL`; bounded: `True`
- Production reachable: `True`; output contributing: `True`
- Source: `fifo.c:66`
- Eligible: `False`
- Evidence:
  - production reachability is a graph traversal from linked executable entry symbols
  - observable output is inferred from output file calls and codec boundary dataflow shape
  - direct effects: {"allocation": true, "assertion": false, "indirect_call": false, "io": false, "logging": false, "state_write": false, "unknown_facts": []}
  - transitive effects: {"allocation": true, "assertion": false, "indirect_call": false, "io": false, "logging": false, "state_write": false, "unknown_facts": []}
  - all reachable loops have fixed AST bounds

### 16. `UsingMidpoint`

- Score: `79.9`; confidence: `0.75`; role: `DUT`
- Purity: `IMPURE`; timing: `COMBINATIONAL`; bounded: `True`
- Production reachable: `True`; output contributing: `True`
- Source: `dsc_codec.c:457`
- Eligible: `False`
- Evidence:
  - production reachability is a graph traversal from linked executable entry symbols
  - observable output is inferred from output file calls and codec boundary dataflow shape
  - direct effects: {"allocation": false, "assertion": false, "indirect_call": false, "io": false, "logging": false, "state_write": false, "unknown_facts": []}
  - transitive effects: {"allocation": false, "assertion": false, "indirect_call": false, "io": false, "logging": true, "state_write": false, "unknown_facts": []}
  - all reachable loops have fixed AST bounds

### 17. `yuv_422_444_region`

- Score: `79.9`; confidence: `0.75`; role: `DUT`
- Purity: `IMPURE`; timing: `COMBINATIONAL`; bounded: `True`
- Production reachable: `True`; output contributing: `True`
- Source: `dsc_utils.c:375`
- Eligible: `False`
- Evidence:
  - production reachability is a graph traversal from linked executable entry symbols
  - observable output is inferred from output file calls and codec boundary dataflow shape
  - direct effects: {"allocation": false, "assertion": false, "indirect_call": false, "io": false, "logging": true, "state_write": false, "unknown_facts": []}
  - transitive effects: {"allocation": false, "assertion": false, "indirect_call": false, "io": false, "logging": true, "state_write": false, "unknown_facts": []}
  - all reachable loops have fixed AST bounds

### 18. `yuv_444_422_region`

- Score: `79.9`; confidence: `0.75`; role: `DUT`
- Purity: `IMPURE`; timing: `COMBINATIONAL`; bounded: `True`
- Production reachable: `True`; output contributing: `True`
- Source: `dsc_utils.c:385`
- Eligible: `False`
- Evidence:
  - production reachability is a graph traversal from linked executable entry symbols
  - observable output is inferred from output file calls and codec boundary dataflow shape
  - direct effects: {"allocation": false, "assertion": false, "indirect_call": false, "io": false, "logging": true, "state_write": false, "unknown_facts": []}
  - transitive effects: {"allocation": false, "assertion": false, "indirect_call": false, "io": false, "logging": true, "state_write": false, "unknown_facts": []}
  - all reachable loops have fixed AST bounds

### 19. `Qp2Qlevel`

- Score: `70.0`; confidence: `0.55`; role: `CONFIG`
- Purity: `PURE`; timing: `COMBINATIONAL`; bounded: `True`
- Production reachable: `True`; output contributing: `False`
- Source: `codec_main.c:816`
- Eligible: `False`
- Evidence:
  - production reachability is a graph traversal from linked executable entry symbols
  - observable output is inferred from output file calls and codec boundary dataflow shape
  - direct effects: {"allocation": false, "assertion": false, "indirect_call": false, "io": false, "logging": false, "state_write": false, "unknown_facts": []}
  - transitive effects: {"allocation": false, "assertion": false, "indirect_call": false, "io": false, "logging": false, "state_write": false, "unknown_facts": []}
  - all reachable loops have fixed AST bounds

### 20. `generate_timecode`

- Score: `70.0`; confidence: `0.55`; role: `UNRESOLVED`
- Purity: `PURE`; timing: `COMBINATIONAL`; bounded: `True`
- Production reachable: `True`; output contributing: `False`
- Source: `dpx.c:708`
- Eligible: `False`
- Evidence:
  - production reachability is a graph traversal from linked executable entry symbols
  - observable output is inferred from output file calls and codec boundary dataflow shape
  - direct effects: {"allocation": false, "assertion": false, "indirect_call": false, "io": false, "logging": false, "state_write": false, "unknown_facts": []}
  - transitive effects: {"allocation": false, "assertion": false, "indirect_call": false, "io": false, "logging": false, "state_write": false, "unknown_facts": []}
  - all reachable loops have fixed AST bounds

### 21. `hdr_dpx_byte_swap`

- Score: `70.0`; confidence: `0.55`; role: `UNRESOLVED`
- Purity: `PURE`; timing: `COMBINATIONAL`; bounded: `True`
- Production reachable: `True`; output contributing: `False`
- Source: `hdr_dpx.c:1445`
- Eligible: `False`
- Evidence:
  - production reachability is a graph traversal from linked executable entry symbols
  - observable output is inferred from output file calls and codec boundary dataflow shape
  - direct effects: {"allocation": false, "assertion": false, "indirect_call": false, "io": false, "logging": false, "state_write": false, "unknown_facts": []}
  - transitive effects: {"allocation": false, "assertion": false, "indirect_call": false, "io": false, "logging": false, "state_write": false, "unknown_facts": []}
  - all reachable loops have fixed AST bounds

### 22. `splitstring_exact`

- Score: `69.9`; confidence: `0.55`; role: `UNRESOLVED`
- Purity: `PURE`; timing: `COMBINATIONAL`; bounded: `True`
- Production reachable: `True`; output contributing: `False`
- Source: `cmd_parse.c:416`
- Eligible: `False`
- Evidence:
  - production reachability is a graph traversal from linked executable entry symbols
  - observable output is inferred from output file calls and codec boundary dataflow shape
  - direct effects: {"allocation": false, "assertion": false, "indirect_call": false, "io": false, "logging": false, "state_write": false, "unknown_facts": []}
  - transitive effects: {"allocation": false, "assertion": false, "indirect_call": false, "io": false, "logging": false, "state_write": false, "unknown_facts": []}
  - all reachable loops have fixed AST bounds

### 23. `CalcFullnessOffset`

- Score: `65.0`; confidence: `0.75`; role: `DUT`
- Purity: `IMPURE`; timing: `STATEFUL`; bounded: `True`
- Production reachable: `True`; output contributing: `True`
- Source: `dsc_codec.c:2188`
- Eligible: `False`
- Evidence:
  - production reachability is a graph traversal from linked executable entry symbols
  - observable output is inferred from output file calls and codec boundary dataflow shape
  - direct effects: {"allocation": false, "assertion": false, "indirect_call": false, "io": false, "logging": false, "state_write": true, "unknown_facts": []}
  - transitive effects: {"allocation": false, "assertion": false, "indirect_call": false, "io": false, "logging": false, "state_write": true, "unknown_facts": []}
  - all reachable loops have fixed AST bounds

### 24. `RemoveBitsEncoderBuffer`

- Score: `65.0`; confidence: `0.75`; role: `DUT`
- Purity: `IMPURE`; timing: `STATEFUL`; bounded: `True`
- Production reachable: `True`; output contributing: `True`
- Source: `dsc_codec.c:1201`
- Eligible: `False`
- Evidence:
  - production reachability is a graph traversal from linked executable entry symbols
  - observable output is inferred from output file calls and codec boundary dataflow shape
  - direct effects: {"allocation": false, "assertion": false, "indirect_call": false, "io": false, "logging": false, "state_write": true, "unknown_facts": []}
  - transitive effects: {"allocation": false, "assertion": false, "indirect_call": false, "io": false, "logging": false, "state_write": true, "unknown_facts": []}
  - all reachable loops have fixed AST bounds

### 25. `fifo_init`

- Score: `64.95`; confidence: `0.75`; role: `DUT`
- Purity: `IMPURE`; timing: `STATEFUL`; bounded: `True`
- Production reachable: `True`; output contributing: `True`
- Source: `fifo.c:43`
- Eligible: `False`
- Evidence:
  - production reachability is a graph traversal from linked executable entry symbols
  - observable output is inferred from output file calls and codec boundary dataflow shape
  - direct effects: {"allocation": true, "assertion": false, "indirect_call": false, "io": false, "logging": false, "state_write": true, "unknown_facts": []}
  - transitive effects: {"allocation": true, "assertion": false, "indirect_call": false, "io": false, "logging": false, "state_write": true, "unknown_facts": []}
  - all reachable loops have fixed AST bounds

### 26. `ErrorHandler`

- Score: `60.0`; confidence: `0.75`; role: `DUT`
- Purity: `IMPURE`; timing: `UNKNOWN`; bounded: `False`
- Production reachable: `True`; output contributing: `True`
- Source: `dsc_codec.c:171`
- Eligible: `False`
- Evidence:
  - production reachability is a graph traversal from linked executable entry symbols
  - observable output is inferred from output file calls and codec boundary dataflow shape
  - direct effects: {"allocation": false, "assertion": false, "indirect_call": false, "io": false, "logging": false, "state_write": true, "unknown_facts": []}
  - transitive effects: {"allocation": false, "assertion": false, "indirect_call": false, "io": false, "logging": false, "state_write": true, "unknown_facts": []}
  - at least one reachable loop has UNKNOWN bounds

### 27. `PopulateOrigLine`

- Score: `60.0`; confidence: `0.75`; role: `DUT`
- Purity: `IMPURE`; timing: `UNKNOWN`; bounded: `False`
- Production reachable: `True`; output contributing: `True`
- Source: `dsc_codec.c:2294`
- Eligible: `False`
- Evidence:
  - production reachability is a graph traversal from linked executable entry symbols
  - observable output is inferred from output file calls and codec boundary dataflow shape
  - direct effects: {"allocation": false, "assertion": false, "indirect_call": false, "io": false, "logging": false, "state_write": true, "unknown_facts": []}
  - transitive effects: {"allocation": false, "assertion": false, "indirect_call": false, "io": false, "logging": false, "state_write": true, "unknown_facts": []}
  - at least one reachable loop has UNKNOWN bounds

### 28. `UpdateMidpoint`

- Score: `60.0`; confidence: `0.75`; role: `DUT`
- Purity: `IMPURE`; timing: `UNKNOWN`; bounded: `False`
- Production reachable: `True`; output contributing: `True`
- Source: `dsc_codec.c:875`
- Eligible: `False`
- Evidence:
  - production reachability is a graph traversal from linked executable entry symbols
  - observable output is inferred from output file calls and codec boundary dataflow shape
  - direct effects: {"allocation": false, "assertion": false, "indirect_call": false, "io": false, "logging": false, "state_write": true, "unknown_facts": []}
  - transitive effects: {"allocation": false, "assertion": false, "indirect_call": false, "io": false, "logging": false, "state_write": true, "unknown_facts": []}
  - at least one reachable loop has UNKNOWN bounds

### 29. `AddBits`

- Score: `59.95`; confidence: `0.75`; role: `DUT`
- Purity: `IMPURE`; timing: `UNKNOWN`; bounded: `False`
- Production reachable: `True`; output contributing: `True`
- Source: `multiplex.c:89`
- Eligible: `False`
- Evidence:
  - production reachability is a graph traversal from linked executable entry symbols
  - observable output is inferred from output file calls and codec boundary dataflow shape
  - direct effects: {"allocation": false, "assertion": false, "indirect_call": false, "io": false, "logging": false, "state_write": true, "unknown_facts": []}
  - transitive effects: {"allocation": false, "assertion": false, "indirect_call": false, "io": false, "logging": true, "state_write": true, "unknown_facts": []}
  - at least one reachable loop has UNKNOWN bounds

### 30. `BlockPredSearch`

- Score: `59.95`; confidence: `0.75`; role: `DUT`
- Purity: `IMPURE`; timing: `UNKNOWN`; bounded: `False`
- Production reachable: `True`; output contributing: `True`
- Source: `dsc_codec.c:924`
- Eligible: `False`
- Evidence:
  - production reachability is a graph traversal from linked executable entry symbols
  - observable output is inferred from output file calls and codec boundary dataflow shape
  - direct effects: {"allocation": false, "assertion": false, "indirect_call": false, "io": false, "logging": false, "state_write": true, "unknown_facts": []}
  - transitive effects: {"allocation": false, "assertion": false, "indirect_call": false, "io": false, "logging": false, "state_write": true, "unknown_facts": []}
  - at least one reachable loop has UNKNOWN bounds

### 31. `DSC_Decode`

- Score: `59.95`; confidence: `0.75`; role: `DUT`
- Purity: `IMPURE`; timing: `UNKNOWN`; bounded: `False`
- Production reachable: `True`; output contributing: `True`
- Source: `dsc_codec.c:3129`
- Eligible: `False`
- Evidence:
  - production reachability is a graph traversal from linked executable entry symbols
  - observable output is inferred from output file calls and codec boundary dataflow shape
  - direct effects: {"allocation": false, "assertion": false, "indirect_call": false, "io": false, "logging": false, "state_write": false, "unknown_facts": []}
  - transitive effects: {"allocation": true, "assertion": true, "indirect_call": false, "io": true, "logging": true, "state_write": true, "unknown_facts": []}
  - at least one reachable loop has UNKNOWN bounds

### 32. `DSC_Encode`

- Score: `59.95`; confidence: `0.75`; role: `DUT`
- Purity: `IMPURE`; timing: `UNKNOWN`; bounded: `False`
- Production reachable: `True`; output contributing: `True`
- Source: `dsc_codec.c:3118`
- Eligible: `False`
- Evidence:
  - production reachability is a graph traversal from linked executable entry symbols
  - observable output is inferred from output file calls and codec boundary dataflow shape
  - direct effects: {"allocation": false, "assertion": false, "indirect_call": false, "io": false, "logging": false, "state_write": false, "unknown_facts": []}
  - transitive effects: {"allocation": true, "assertion": true, "indirect_call": false, "io": true, "logging": true, "state_write": true, "unknown_facts": []}
  - at least one reachable loop has UNKNOWN bounds

### 33. `GetBits`

- Score: `59.95`; confidence: `0.75`; role: `DUT`
- Purity: `IMPURE`; timing: `UNKNOWN`; bounded: `False`
- Production reachable: `True`; output contributing: `True`
- Source: `multiplex.c:104`
- Eligible: `False`
- Evidence:
  - production reachability is a graph traversal from linked executable entry symbols
  - observable output is inferred from output file calls and codec boundary dataflow shape
  - direct effects: {"allocation": false, "assertion": false, "indirect_call": false, "io": false, "logging": false, "state_write": true, "unknown_facts": []}
  - transitive effects: {"allocation": false, "assertion": false, "indirect_call": false, "io": false, "logging": true, "state_write": true, "unknown_facts": []}
  - at least one reachable loop has UNKNOWN bounds

### 34. `UpdateHistoryElement`

- Score: `59.95`; confidence: `0.75`; role: `DUT`
- Purity: `IMPURE`; timing: `UNKNOWN`; bounded: `False`
- Production reachable: `True`; output contributing: `True`
- Source: `dsc_codec.c:674`
- Eligible: `False`
- Evidence:
  - production reachability is a graph traversal from linked executable entry symbols
  - observable output is inferred from output file calls and codec boundary dataflow shape
  - direct effects: {"allocation": false, "assertion": false, "indirect_call": false, "io": false, "logging": false, "state_write": true, "unknown_facts": []}
  - transitive effects: {"allocation": false, "assertion": false, "indirect_call": false, "io": false, "logging": false, "state_write": true, "unknown_facts": []}
  - at least one reachable loop has UNKNOWN bounds

### 35. `UpdateICHistory`

- Score: `59.95`; confidence: `0.75`; role: `DUT`
- Purity: `IMPURE`; timing: `UNKNOWN`; bounded: `False`
- Production reachable: `True`; output contributing: `True`
- Source: `dsc_codec.c:787`
- Eligible: `False`
- Evidence:
  - production reachability is a graph traversal from linked executable entry symbols
  - observable output is inferred from output file calls and codec boundary dataflow shape
  - direct effects: {"allocation": false, "assertion": false, "indirect_call": false, "io": false, "logging": false, "state_write": true, "unknown_facts": []}
  - transitive effects: {"allocation": false, "assertion": false, "indirect_call": false, "io": false, "logging": false, "state_write": true, "unknown_facts": []}
  - at least one reachable loop has UNKNOWN bounds

### 36. `UseICHistory`

- Score: `59.95`; confidence: `0.75`; role: `DUT`
- Purity: `IMPURE`; timing: `UNKNOWN`; bounded: `False`
- Production reachable: `True`; output contributing: `True`
- Source: `dsc_codec.c:832`
- Eligible: `False`
- Evidence:
  - production reachability is a graph traversal from linked executable entry symbols
  - observable output is inferred from output file calls and codec boundary dataflow shape
  - direct effects: {"allocation": false, "assertion": false, "indirect_call": false, "io": false, "logging": true, "state_write": true, "unknown_facts": []}
  - transitive effects: {"allocation": false, "assertion": false, "indirect_call": false, "io": false, "logging": true, "state_write": true, "unknown_facts": []}
  - at least one reachable loop has UNKNOWN bounds

### 37. `dpx_write`

- Score: `59.95`; confidence: `0.75`; role: `DUT`
- Purity: `IMPURE`; timing: `UNKNOWN`; bounded: `False`
- Production reachable: `True`; output contributing: `True`
- Source: `dpx.c:225`
- Eligible: `False`
- Evidence:
  - production reachability is a graph traversal from linked executable entry symbols
  - observable output is inferred from output file calls and codec boundary dataflow shape
  - direct effects: {"allocation": false, "assertion": false, "indirect_call": false, "io": false, "logging": false, "state_write": false, "unknown_facts": []}
  - transitive effects: {"allocation": true, "assertion": false, "indirect_call": false, "io": true, "logging": true, "state_write": true, "unknown_facts": []}
  - at least one reachable loop has UNKNOWN bounds

### 38. `putbits`

- Score: `59.95`; confidence: `0.75`; role: `DUT`
- Purity: `IMPURE`; timing: `UNKNOWN`; bounded: `False`
- Production reachable: `True`; output contributing: `True`
- Source: `dsc_utils.c:81`
- Eligible: `False`
- Evidence:
  - production reachability is a graph traversal from linked executable entry symbols
  - observable output is inferred from output file calls and codec boundary dataflow shape
  - direct effects: {"allocation": false, "assertion": false, "indirect_call": false, "io": false, "logging": true, "state_write": true, "unknown_facts": []}
  - transitive effects: {"allocation": false, "assertion": false, "indirect_call": false, "io": false, "logging": true, "state_write": true, "unknown_facts": []}
  - at least one reachable loop has UNKNOWN bounds

### 39. `FlatnessAdjustment`

- Score: `59.9`; confidence: `0.75`; role: `DUT`
- Purity: `IMPURE`; timing: `UNKNOWN`; bounded: `False`
- Production reachable: `True`; output contributing: `True`
- Source: `dsc_codec.c:2510`
- Eligible: `False`
- Evidence:
  - production reachability is a graph traversal from linked executable entry symbols
  - observable output is inferred from output file calls and codec boundary dataflow shape
  - direct effects: {"allocation": false, "assertion": false, "indirect_call": false, "io": false, "logging": false, "state_write": true, "unknown_facts": []}
  - transitive effects: {"allocation": false, "assertion": false, "indirect_call": false, "io": false, "logging": false, "state_write": true, "unknown_facts": []}
  - at least one reachable loop has UNKNOWN bounds

### 40. `HistoryLookup`

- Score: `59.9`; confidence: `0.75`; role: `DUT`
- Purity: `IMPURE`; timing: `UNKNOWN`; bounded: `False`
- Production reachable: `True`; output contributing: `True`
- Source: `dsc_codec.c:543`
- Eligible: `False`
- Evidence:
  - production reachability is a graph traversal from linked executable entry symbols
  - observable output is inferred from output file calls and codec boundary dataflow shape
  - direct effects: {"allocation": false, "assertion": false, "indirect_call": false, "io": false, "logging": false, "state_write": true, "unknown_facts": []}
  - transitive effects: {"allocation": false, "assertion": false, "indirect_call": false, "io": false, "logging": false, "state_write": true, "unknown_facts": []}
  - at least one reachable loop has UNKNOWN bounds

### 41. `ProcessGroupDec`

- Score: `59.9`; confidence: `0.75`; role: `DUT`
- Purity: `IMPURE`; timing: `UNKNOWN`; bounded: `False`
- Production reachable: `True`; output contributing: `True`
- Source: `multiplex.c:159`
- Eligible: `False`
- Evidence:
  - production reachability is a graph traversal from linked executable entry symbols
  - observable output is inferred from output file calls and codec boundary dataflow shape
  - direct effects: {"allocation": false, "assertion": false, "indirect_call": false, "io": false, "logging": false, "state_write": false, "unknown_facts": []}
  - transitive effects: {"allocation": false, "assertion": false, "indirect_call": false, "io": false, "logging": true, "state_write": true, "unknown_facts": []}
  - at least one reachable loop has UNKNOWN bounds

### 42. `fifo_get_bits`

- Score: `59.9`; confidence: `0.75`; role: `DUT`
- Purity: `IMPURE`; timing: `UNKNOWN`; bounded: `False`
- Production reachable: `True`; output contributing: `True`
- Source: `fifo.c:77`
- Eligible: `False`
- Evidence:
  - production reachability is a graph traversal from linked executable entry symbols
  - observable output is inferred from output file calls and codec boundary dataflow shape
  - direct effects: {"allocation": false, "assertion": false, "indirect_call": false, "io": false, "logging": true, "state_write": true, "unknown_facts": []}
  - transitive effects: {"allocation": false, "assertion": false, "indirect_call": false, "io": false, "logging": true, "state_write": true, "unknown_facts": []}
  - at least one reachable loop has UNKNOWN bounds

### 43. `fifo_put_bits`

- Score: `59.9`; confidence: `0.75`; role: `DUT`
- Purity: `IMPURE`; timing: `UNKNOWN`; bounded: `False`
- Production reachable: `True`; output contributing: `True`
- Source: `fifo.c:115`
- Eligible: `False`
- Evidence:
  - production reachability is a graph traversal from linked executable entry symbols
  - observable output is inferred from output file calls and codec boundary dataflow shape
  - direct effects: {"allocation": false, "assertion": false, "indirect_call": false, "io": false, "logging": true, "state_write": true, "unknown_facts": []}
  - transitive effects: {"allocation": false, "assertion": false, "indirect_call": false, "io": false, "logging": true, "state_write": true, "unknown_facts": []}
  - at least one reachable loop has UNKNOWN bounds

### 44. `rgb2ycocg`

- Score: `59.9`; confidence: `0.75`; role: `DUT`
- Purity: `IMPURE`; timing: `UNKNOWN`; bounded: `False`
- Production reachable: `True`; output contributing: `True`
- Source: `dsc_utils.c:145`
- Eligible: `False`
- Evidence:
  - production reachability is a graph traversal from linked executable entry symbols
  - observable output is inferred from output file calls and codec boundary dataflow shape
  - direct effects: {"allocation": false, "assertion": false, "indirect_call": false, "io": true, "logging": false, "state_write": true, "unknown_facts": []}
  - transitive effects: {"allocation": false, "assertion": false, "indirect_call": false, "io": true, "logging": false, "state_write": true, "unknown_facts": []}
  - at least one reachable loop has UNKNOWN bounds

### 45. `ycocg2rgb`

- Score: `59.9`; confidence: `0.75`; role: `DUT`
- Purity: `IMPURE`; timing: `UNKNOWN`; bounded: `False`
- Production reachable: `True`; output contributing: `True`
- Source: `dsc_utils.c:225`
- Eligible: `False`
- Evidence:
  - production reachability is a graph traversal from linked executable entry symbols
  - observable output is inferred from output file calls and codec boundary dataflow shape
  - direct effects: {"allocation": false, "assertion": false, "indirect_call": false, "io": true, "logging": false, "state_write": true, "unknown_facts": []}
  - transitive effects: {"allocation": false, "assertion": false, "indirect_call": false, "io": true, "logging": false, "state_write": true, "unknown_facts": []}
  - at least one reachable loop has UNKNOWN bounds

### 46. `EstimateBitsForGroup`

- Score: `59.85`; confidence: `0.75`; role: `DUT`
- Purity: `IMPURE`; timing: `UNKNOWN`; bounded: `False`
- Production reachable: `True`; output contributing: `True`
- Source: `dsc_codec.c:390`
- Eligible: `False`
- Evidence:
  - production reachability is a graph traversal from linked executable entry symbols
  - observable output is inferred from output file calls and codec boundary dataflow shape
  - direct effects: {"allocation": false, "assertion": false, "indirect_call": false, "io": false, "logging": false, "state_write": false, "unknown_facts": []}
  - transitive effects: {"allocation": false, "assertion": false, "indirect_call": false, "io": false, "logging": true, "state_write": false, "unknown_facts": []}
  - at least one reachable loop has UNKNOWN bounds

### 47. `IsOrigWithinQerr`

- Score: `59.85`; confidence: `0.75`; role: `DUT`
- Purity: `IMPURE`; timing: `UNKNOWN`; bounded: `False`
- Production reachable: `True`; output contributing: `True`
- Source: `dsc_codec.c:611`
- Eligible: `False`
- Evidence:
  - production reachability is a graph traversal from linked executable entry symbols
  - observable output is inferred from output file calls and codec boundary dataflow shape
  - direct effects: {"allocation": false, "assertion": false, "indirect_call": false, "io": false, "logging": false, "state_write": true, "unknown_facts": []}
  - transitive effects: {"allocation": false, "assertion": false, "indirect_call": false, "io": false, "logging": false, "state_write": true, "unknown_facts": []}
  - at least one reachable loop has UNKNOWN bounds

### 48. `PickBestHistoryValue`

- Score: `59.85`; confidence: `0.75`; role: `DUT`
- Purity: `IMPURE`; timing: `UNKNOWN`; bounded: `False`
- Production reachable: `True`; output contributing: `True`
- Source: `dsc_codec.c:736`
- Eligible: `False`
- Evidence:
  - production reachability is a graph traversal from linked executable entry symbols
  - observable output is inferred from output file calls and codec boundary dataflow shape
  - direct effects: {"allocation": false, "assertion": false, "indirect_call": false, "io": false, "logging": true, "state_write": false, "unknown_facts": []}
  - transitive effects: {"allocation": false, "assertion": false, "indirect_call": false, "io": false, "logging": true, "state_write": true, "unknown_facts": []}
  - at least one reachable loop has UNKNOWN bounds

### 49. `VLDGroup`

- Score: `59.85`; confidence: `0.75`; role: `DUT`
- Purity: `IMPURE`; timing: `UNKNOWN`; bounded: `False`
- Production reachable: `True`; output contributing: `True`
- Source: `dsc_codec.c:1988`
- Eligible: `False`
- Evidence:
  - production reachability is a graph traversal from linked executable entry symbols
  - observable output is inferred from output file calls and codec boundary dataflow shape
  - direct effects: {"allocation": false, "assertion": false, "indirect_call": false, "io": false, "logging": true, "state_write": true, "unknown_facts": []}
  - transitive effects: {"allocation": false, "assertion": false, "indirect_call": false, "io": true, "logging": true, "state_write": true, "unknown_facts": []}
  - at least one reachable loop has UNKNOWN bounds

### 50. `IchDecision`

- Score: `59.8`; confidence: `0.75`; role: `DUT`
- Purity: `IMPURE`; timing: `UNKNOWN`; bounded: `False`
- Production reachable: `True`; output contributing: `True`
- Source: `dsc_codec.c:484`
- Eligible: `False`
- Evidence:
  - production reachability is a graph traversal from linked executable entry symbols
  - observable output is inferred from output file calls and codec boundary dataflow shape
  - direct effects: {"allocation": false, "assertion": false, "indirect_call": false, "io": false, "logging": true, "state_write": false, "unknown_facts": []}
  - transitive effects: {"allocation": false, "assertion": false, "indirect_call": false, "io": false, "logging": true, "state_write": false, "unknown_facts": []}
  - at least one reachable loop has UNKNOWN bounds

### 51. `ProcessGroupEnc`

- Score: `59.8`; confidence: `0.75`; role: `DUT`
- Purity: `IMPURE`; timing: `UNKNOWN`; bounded: `False`
- Production reachable: `True`; output contributing: `True`
- Source: `multiplex.c:116`
- Eligible: `False`
- Evidence:
  - production reachability is a graph traversal from linked executable entry symbols
  - observable output is inferred from output file calls and codec boundary dataflow shape
  - direct effects: {"allocation": false, "assertion": false, "indirect_call": false, "io": false, "logging": false, "state_write": false, "unknown_facts": []}
  - transitive effects: {"allocation": false, "assertion": false, "indirect_call": false, "io": false, "logging": true, "state_write": true, "unknown_facts": []}
  - at least one reachable loop has UNKNOWN bounds

### 52. `RateControl`

- Score: `59.8`; confidence: `0.75`; role: `DUT`
- Purity: `IMPURE`; timing: `UNKNOWN`; bounded: `False`
- Production reachable: `True`; output contributing: `True`
- Source: `dsc_codec.c:1242`
- Eligible: `False`
- Evidence:
  - production reachability is a graph traversal from linked executable entry symbols
  - observable output is inferred from output file calls and codec boundary dataflow shape
  - direct effects: {"allocation": false, "assertion": false, "indirect_call": false, "io": true, "logging": true, "state_write": true, "unknown_facts": []}
  - transitive effects: {"allocation": false, "assertion": false, "indirect_call": false, "io": true, "logging": true, "state_write": true, "unknown_facts": []}
  - at least one reachable loop has UNKNOWN bounds

### 53. `VLCGroup`

- Score: `59.75`; confidence: `0.75`; role: `DUT`
- Purity: `IMPURE`; timing: `UNKNOWN`; bounded: `False`
- Production reachable: `True`; output contributing: `True`
- Source: `dsc_codec.c:1710`
- Eligible: `False`
- Evidence:
  - production reachability is a graph traversal from linked executable entry symbols
  - observable output is inferred from output file calls and codec boundary dataflow shape
  - direct effects: {"allocation": false, "assertion": false, "indirect_call": false, "io": false, "logging": true, "state_write": true, "unknown_facts": []}
  - transitive effects: {"allocation": false, "assertion": true, "indirect_call": false, "io": true, "logging": true, "state_write": true, "unknown_facts": []}
  - at least one reachable loop has UNKNOWN bounds

### 54. `InitializeDSCState`

- Score: `59.7`; confidence: `0.75`; role: `DUT`
- Purity: `IMPURE`; timing: `UNKNOWN`; bounded: `False`
- Production reachable: `True`; output contributing: `True`
- Source: `dsc_codec.c:2056`
- Eligible: `False`
- Evidence:
  - production reachability is a graph traversal from linked executable entry symbols
  - observable output is inferred from output file calls and codec boundary dataflow shape
  - direct effects: {"allocation": true, "assertion": true, "indirect_call": false, "io": false, "logging": false, "state_write": true, "unknown_facts": []}
  - transitive effects: {"allocation": true, "assertion": true, "indirect_call": false, "io": false, "logging": false, "state_write": true, "unknown_facts": []}
  - at least one reachable loop has UNKNOWN bounds

### 55. `VLDUnit`

- Score: `59.55`; confidence: `0.75`; role: `DUT`
- Purity: `IMPURE`; timing: `UNKNOWN`; bounded: `False`
- Production reachable: `True`; output contributing: `True`
- Source: `dsc_codec.c:1808`
- Eligible: `False`
- Evidence:
  - production reachability is a graph traversal from linked executable entry symbols
  - observable output is inferred from output file calls and codec boundary dataflow shape
  - direct effects: {"allocation": false, "assertion": false, "indirect_call": false, "io": true, "logging": false, "state_write": true, "unknown_facts": []}
  - transitive effects: {"allocation": false, "assertion": false, "indirect_call": false, "io": true, "logging": true, "state_write": true, "unknown_facts": []}
  - at least one reachable loop has UNKNOWN bounds

### 56. `PredictionLoop`

- Score: `59.5`; confidence: `0.75`; role: `DUT`
- Purity: `IMPURE`; timing: `UNKNOWN`; bounded: `False`
- Production reachable: `True`; output contributing: `True`
- Source: `dsc_codec.c:2361`
- Eligible: `False`
- Evidence:
  - production reachability is a graph traversal from linked executable entry symbols
  - observable output is inferred from output file calls and codec boundary dataflow shape
  - direct effects: {"allocation": false, "assertion": true, "indirect_call": false, "io": false, "logging": true, "state_write": true, "unknown_facts": []}
  - transitive effects: {"allocation": false, "assertion": true, "indirect_call": false, "io": false, "logging": true, "state_write": true, "unknown_facts": []}
  - at least one reachable loop has UNKNOWN bounds

### 57. `VLCUnit`

- Score: `59.4`; confidence: `0.75`; role: `DUT`
- Purity: `IMPURE`; timing: `UNKNOWN`; bounded: `False`
- Production reachable: `True`; output contributing: `True`
- Source: `dsc_codec.c:1494`
- Eligible: `False`
- Evidence:
  - production reachability is a graph traversal from linked executable entry symbols
  - observable output is inferred from output file calls and codec boundary dataflow shape
  - direct effects: {"allocation": false, "assertion": true, "indirect_call": false, "io": true, "logging": false, "state_write": true, "unknown_facts": []}
  - transitive effects: {"allocation": false, "assertion": true, "indirect_call": false, "io": true, "logging": true, "state_write": true, "unknown_facts": []}
  - at least one reachable loop has UNKNOWN bounds

### 58. `write_dpx_ver`

- Score: `59.2`; confidence: `0.75`; role: `DUT`
- Purity: `IMPURE`; timing: `UNKNOWN`; bounded: `False`
- Production reachable: `True`; output contributing: `True`
- Source: `dpx.c:235`
- Eligible: `False`
- Evidence:
  - production reachability is a graph traversal from linked executable entry symbols
  - observable output is inferred from output file calls and codec boundary dataflow shape
  - direct effects: {"allocation": false, "assertion": false, "indirect_call": false, "io": true, "logging": true, "state_write": true, "unknown_facts": []}
  - transitive effects: {"allocation": true, "assertion": false, "indirect_call": false, "io": true, "logging": true, "state_write": true, "unknown_facts": []}
  - at least one reachable loop has UNKNOWN bounds

### 59. `DSC_Algorithm`

- Score: `59.0`; confidence: `0.75`; role: `DUT`
- Purity: `IMPURE`; timing: `UNKNOWN`; bounded: `False`
- Production reachable: `True`; output contributing: `True`
- Source: `dsc_codec.c:2594`
- Eligible: `False`
- Evidence:
  - production reachability is a graph traversal from linked executable entry symbols
  - observable output is inferred from output file calls and codec boundary dataflow shape
  - direct effects: {"allocation": true, "assertion": false, "indirect_call": false, "io": true, "logging": true, "state_write": true, "unknown_facts": []}
  - transitive effects: {"allocation": true, "assertion": true, "indirect_call": false, "io": true, "logging": true, "state_write": true, "unknown_facts": []}
  - at least one reachable loop has UNKNOWN bounds

### 60. `hdr_dpx_write`

- Score: `59.0`; confidence: `0.75`; role: `DUT`
- Purity: `IMPURE`; timing: `UNKNOWN`; bounded: `False`
- Production reachable: `True`; output contributing: `True`
- Source: `hdr_dpx.c:1746`
- Eligible: `False`
- Evidence:
  - production reachability is a graph traversal from linked executable entry symbols
  - observable output is inferred from output file calls and codec boundary dataflow shape
  - direct effects: {"allocation": true, "assertion": false, "indirect_call": false, "io": true, "logging": false, "state_write": true, "unknown_facts": []}
  - transitive effects: {"allocation": true, "assertion": false, "indirect_call": false, "io": true, "logging": true, "state_write": true, "unknown_facts": []}
  - at least one reachable loop has UNKNOWN bounds

### 61. `main`

- Score: `59.0`; confidence: `0.75`; role: `DUT`
- Purity: `IMPURE`; timing: `UNKNOWN`; bounded: `False`
- Production reachable: `True`; output contributing: `True`
- Source: `codec_main.c:1276`
- Eligible: `False`
- Evidence:
  - production reachability is a graph traversal from linked executable entry symbols
  - observable output is inferred from output file calls and codec boundary dataflow shape
  - direct effects: {"allocation": true, "assertion": false, "indirect_call": false, "io": true, "logging": true, "state_write": true, "unknown_facts": []}
  - transitive effects: {"allocation": true, "assertion": true, "indirect_call": false, "io": true, "logging": true, "state_write": true, "unknown_facts": []}
  - at least one reachable loop has UNKNOWN bounds

### 62. `conv`

- Score: `50.0`; confidence: `0.55`; role: `UNRESOLVED`
- Purity: `PURE`; timing: `UNKNOWN`; bounded: `False`
- Production reachable: `True`; output contributing: `False`
- Source: `utl.c:470`
- Eligible: `False`
- Evidence:
  - production reachability is a graph traversal from linked executable entry symbols
  - observable output is inferred from output file calls and codec boundary dataflow shape
  - direct effects: {"allocation": false, "assertion": false, "indirect_call": false, "io": false, "logging": false, "state_write": false, "unknown_facts": []}
  - transitive effects: {"allocation": false, "assertion": false, "indirect_call": false, "io": false, "logging": false, "state_write": false, "unknown_facts": []}
  - at least one reachable loop has UNKNOWN bounds

### 63. `ends_in_percentd`

- Score: `50.0`; confidence: `0.55`; role: `UNRESOLVED`
- Purity: `PURE`; timing: `UNKNOWN`; bounded: `False`
- Production reachable: `True`; output contributing: `False`
- Source: `dpx.c:86`
- Eligible: `False`
- Evidence:
  - production reachability is a graph traversal from linked executable entry symbols
  - observable output is inferred from output file calls and codec boundary dataflow shape
  - direct effects: {"allocation": false, "assertion": false, "indirect_call": false, "io": false, "logging": false, "state_write": false, "unknown_facts": []}
  - transitive effects: {"allocation": false, "assertion": false, "indirect_call": false, "io": false, "logging": false, "state_write": false, "unknown_facts": []}
  - at least one reachable loop has UNKNOWN bounds

### 64. `lower_case`

- Score: `49.95`; confidence: `0.55`; role: `UNRESOLVED`
- Purity: `PURE`; timing: `UNKNOWN`; bounded: `False`
- Production reachable: `True`; output contributing: `False`
- Source: `cmd_parse.c:367`
- Eligible: `False`
- Evidence:
  - production reachability is a graph traversal from linked executable entry symbols
  - observable output is inferred from output file calls and codec boundary dataflow shape
  - direct effects: {"allocation": false, "assertion": false, "indirect_call": false, "io": false, "logging": false, "state_write": false, "unknown_facts": []}
  - transitive effects: {"allocation": false, "assertion": false, "indirect_call": false, "io": false, "logging": false, "state_write": false, "unknown_facts": []}
  - at least one reachable loop has UNKNOWN bounds

### 65. `print_pps`

- Score: `49.95`; confidence: `0.55`; role: `CONFIG`
- Purity: `IMPURE`; timing: `COMBINATIONAL`; bounded: `True`
- Production reachable: `True`; output contributing: `False`
- Source: `dsc_utils.c:609`
- Eligible: `False`
- Evidence:
  - production reachability is a graph traversal from linked executable entry symbols
  - observable output is inferred from output file calls and codec boundary dataflow shape
  - direct effects: {"allocation": false, "assertion": false, "indirect_call": false, "io": true, "logging": false, "state_write": false, "unknown_facts": []}
  - transitive effects: {"allocation": false, "assertion": false, "indirect_call": false, "io": true, "logging": false, "state_write": false, "unknown_facts": []}
  - all reachable loops have fixed AST bounds

### 66. `str2f`

- Score: `49.95`; confidence: `0.55`; role: `HOST_IO`
- Purity: `IMPURE`; timing: `COMBINATIONAL`; bounded: `True`
- Production reachable: `True`; output contributing: `False`
- Source: `cmd_parse.c:557`
- Eligible: `False`
- Evidence:
  - production reachability is a graph traversal from linked executable entry symbols
  - observable output is inferred from output file calls and codec boundary dataflow shape
  - direct effects: {"allocation": false, "assertion": false, "indirect_call": false, "io": false, "logging": false, "state_write": false, "unknown_facts": []}
  - transitive effects: {"allocation": false, "assertion": false, "indirect_call": false, "io": true, "logging": false, "state_write": false, "unknown_facts": []}
  - all reachable loops have fixed AST bounds

### 67. `str2l`

- Score: `49.95`; confidence: `0.55`; role: `HOST_IO`
- Purity: `IMPURE`; timing: `COMBINATIONAL`; bounded: `True`
- Production reachable: `True`; output contributing: `False`
- Source: `cmd_parse.c:481`
- Eligible: `False`
- Evidence:
  - production reachability is a graph traversal from linked executable entry symbols
  - observable output is inferred from output file calls and codec boundary dataflow shape
  - direct effects: {"allocation": false, "assertion": false, "indirect_call": false, "io": false, "logging": false, "state_write": false, "unknown_facts": []}
  - transitive effects: {"allocation": false, "assertion": false, "indirect_call": false, "io": true, "logging": false, "state_write": false, "unknown_facts": []}
  - all reachable loops have fixed AST bounds

### 68. `str2ul`

- Score: `49.95`; confidence: `0.55`; role: `HOST_IO`
- Purity: `IMPURE`; timing: `COMBINATIONAL`; bounded: `True`
- Production reachable: `True`; output contributing: `False`
- Source: `cmd_parse.c:525`
- Eligible: `False`
- Evidence:
  - production reachability is a graph traversal from linked executable entry symbols
  - observable output is inferred from output file calls and codec boundary dataflow shape
  - direct effects: {"allocation": false, "assertion": false, "indirect_call": false, "io": false, "logging": false, "state_write": false, "unknown_facts": []}
  - transitive effects: {"allocation": false, "assertion": false, "indirect_call": false, "io": true, "logging": false, "state_write": false, "unknown_facts": []}
  - all reachable loops have fixed AST bounds

### 69. `Assert_func`

- Score: `49.9`; confidence: `0.55`; role: `HOST_IO`
- Purity: `IMPURE`; timing: `COMBINATIONAL`; bounded: `True`
- Production reachable: `True`; output contributing: `False`
- Source: `logging.c:155`
- Eligible: `False`
- Evidence:
  - production reachability is a graph traversal from linked executable entry symbols
  - observable output is inferred from output file calls and codec boundary dataflow shape
  - direct effects: {"allocation": false, "assertion": false, "indirect_call": false, "io": true, "logging": false, "state_write": false, "unknown_facts": []}
  - transitive effects: {"allocation": false, "assertion": false, "indirect_call": false, "io": true, "logging": false, "state_write": false, "unknown_facts": []}
  - all reachable loops have fixed AST bounds

### 70. `splitstring_exact_strict`

- Score: `49.9`; confidence: `0.55`; role: `HOST_IO`
- Purity: `IMPURE`; timing: `COMBINATIONAL`; bounded: `True`
- Production reachable: `True`; output contributing: `False`
- Source: `cmd_parse.c:438`
- Eligible: `False`
- Evidence:
  - production reachability is a graph traversal from linked executable entry symbols
  - observable output is inferred from output file calls and codec boundary dataflow shape
  - direct effects: {"allocation": false, "assertion": false, "indirect_call": false, "io": false, "logging": true, "state_write": false, "unknown_facts": []}
  - transitive effects: {"allocation": false, "assertion": false, "indirect_call": false, "io": true, "logging": true, "state_write": false, "unknown_facts": []}
  - all reachable loops have fixed AST bounds

### 71. `str2d`

- Score: `49.9`; confidence: `0.55`; role: `HOST_IO`
- Purity: `IMPURE`; timing: `COMBINATIONAL`; bounded: `True`
- Production reachable: `True`; output contributing: `False`
- Source: `cmd_parse.c:564`
- Eligible: `False`
- Evidence:
  - production reachability is a graph traversal from linked executable entry symbols
  - observable output is inferred from output file calls and codec boundary dataflow shape
  - direct effects: {"allocation": false, "assertion": false, "indirect_call": false, "io": false, "logging": false, "state_write": false, "unknown_facts": []}
  - transitive effects: {"allocation": false, "assertion": false, "indirect_call": false, "io": true, "logging": false, "state_write": false, "unknown_facts": []}
  - all reachable loops have fixed AST bounds

### 72. `str2i`

- Score: `49.9`; confidence: `0.55`; role: `HOST_IO`
- Purity: `IMPURE`; timing: `COMBINATIONAL`; bounded: `True`
- Production reachable: `True`; output contributing: `False`
- Source: `cmd_parse.c:451`
- Eligible: `False`
- Evidence:
  - production reachability is a graph traversal from linked executable entry symbols
  - observable output is inferred from output file calls and codec boundary dataflow shape
  - direct effects: {"allocation": false, "assertion": false, "indirect_call": false, "io": false, "logging": false, "state_write": false, "unknown_facts": []}
  - transitive effects: {"allocation": false, "assertion": false, "indirect_call": false, "io": true, "logging": false, "state_write": false, "unknown_facts": []}
  - all reachable loops have fixed AST bounds

### 73. `str2p`

- Score: `49.9`; confidence: `0.55`; role: `HOST_IO`
- Purity: `IMPURE`; timing: `COMBINATIONAL`; bounded: `True`
- Production reachable: `True`; output contributing: `False`
- Source: `cmd_parse.c:464`
- Eligible: `False`
- Evidence:
  - production reachability is a graph traversal from linked executable entry symbols
  - observable output is inferred from output file calls and codec boundary dataflow shape
  - direct effects: {"allocation": false, "assertion": false, "indirect_call": false, "io": false, "logging": false, "state_write": false, "unknown_facts": []}
  - transitive effects: {"allocation": false, "assertion": false, "indirect_call": false, "io": true, "logging": false, "state_write": false, "unknown_facts": []}
  - all reachable loops have fixed AST bounds

### 74. `str2ui`

- Score: `49.9`; confidence: `0.55`; role: `HOST_IO`
- Purity: `IMPURE`; timing: `COMBINATIONAL`; bounded: `True`
- Production reachable: `True`; output contributing: `False`
- Source: `cmd_parse.c:512`
- Eligible: `False`
- Evidence:
  - production reachability is a graph traversal from linked executable entry symbols
  - observable output is inferred from output file calls and codec boundary dataflow shape
  - direct effects: {"allocation": false, "assertion": false, "indirect_call": false, "io": false, "logging": false, "state_write": false, "unknown_facts": []}
  - transitive effects: {"allocation": false, "assertion": false, "indirect_call": false, "io": true, "logging": false, "state_write": false, "unknown_facts": []}
  - all reachable loops have fixed AST bounds

### 75. `usage`

- Score: `49.9`; confidence: `0.55`; role: `HOST_IO`
- Purity: `IMPURE`; timing: `COMBINATIONAL`; bounded: `True`
- Production reachable: `True`; output contributing: `False`
- Source: `codec_main.c:377`
- Eligible: `False`
- Evidence:
  - production reachability is a graph traversal from linked executable entry symbols
  - observable output is inferred from output file calls and codec boundary dataflow shape
  - direct effects: {"allocation": false, "assertion": false, "indirect_call": false, "io": false, "logging": true, "state_write": false, "unknown_facts": []}
  - transitive effects: {"allocation": false, "assertion": false, "indirect_call": false, "io": false, "logging": true, "state_write": false, "unknown_facts": []}
  - all reachable loops have fixed AST bounds

### 76. `str2ll`

- Score: `49.85`; confidence: `0.55`; role: `HOST_IO`
- Purity: `IMPURE`; timing: `COMBINATIONAL`; bounded: `True`
- Production reachable: `True`; output contributing: `False`
- Source: `cmd_parse.c:494`
- Eligible: `False`
- Evidence:
  - production reachability is a graph traversal from linked executable entry symbols
  - observable output is inferred from output file calls and codec boundary dataflow shape
  - direct effects: {"allocation": false, "assertion": false, "indirect_call": false, "io": false, "logging": false, "state_write": false, "unknown_facts": []}
  - transitive effects: {"allocation": false, "assertion": false, "indirect_call": false, "io": true, "logging": false, "state_write": false, "unknown_facts": []}
  - all reachable loops have fixed AST bounds

### 77. `str2ull`

- Score: `49.85`; confidence: `0.55`; role: `HOST_IO`
- Purity: `IMPURE`; timing: `COMBINATIONAL`; bounded: `True`
- Production reachable: `True`; output contributing: `False`
- Source: `cmd_parse.c:538`
- Eligible: `False`
- Evidence:
  - production reachability is a graph traversal from linked executable entry symbols
  - observable output is inferred from output file calls and codec boundary dataflow shape
  - direct effects: {"allocation": false, "assertion": false, "indirect_call": false, "io": false, "logging": false, "state_write": false, "unknown_facts": []}
  - transitive effects: {"allocation": false, "assertion": false, "indirect_call": false, "io": true, "logging": false, "state_write": false, "unknown_facts": []}
  - all reachable loops have fixed AST bounds

### 78. `CErr`

- Score: `49.75`; confidence: `0.55`; role: `HOST_IO`
- Purity: `IMPURE`; timing: `COMBINATIONAL`; bounded: `True`
- Production reachable: `True`; output contributing: `False`
- Source: `logging.c:123`
- Eligible: `False`
- Evidence:
  - production reachability is a graph traversal from linked executable entry symbols
  - observable output is inferred from output file calls and codec boundary dataflow shape
  - direct effects: {"allocation": false, "assertion": false, "indirect_call": false, "io": true, "logging": false, "state_write": false, "unknown_facts": []}
  - transitive effects: {"allocation": false, "assertion": false, "indirect_call": false, "io": true, "logging": false, "state_write": false, "unknown_facts": []}
  - all reachable loops have fixed AST bounds

### 79. `Err`

- Score: `49.75`; confidence: `0.55`; role: `HOST_IO`
- Purity: `IMPURE`; timing: `COMBINATIONAL`; bounded: `True`
- Production reachable: `True`; output contributing: `False`
- Source: `logging.c:94`
- Eligible: `False`
- Evidence:
  - production reachability is a graph traversal from linked executable entry symbols
  - observable output is inferred from output file calls and codec boundary dataflow shape
  - direct effects: {"allocation": false, "assertion": false, "indirect_call": false, "io": true, "logging": false, "state_write": false, "unknown_facts": []}
  - transitive effects: {"allocation": false, "assertion": false, "indirect_call": false, "io": true, "logging": false, "state_write": false, "unknown_facts": []}
  - all reachable loops have fixed AST bounds

### 80. `UErr`

- Score: `49.75`; confidence: `0.55`; role: `HOST_IO`
- Purity: `IMPURE`; timing: `COMBINATIONAL`; bounded: `True`
- Production reachable: `True`; output contributing: `False`
- Source: `logging.c:110`
- Eligible: `False`
- Evidence:
  - production reachability is a graph traversal from linked executable entry symbols
  - observable output is inferred from output file calls and codec boundary dataflow shape
  - direct effects: {"allocation": false, "assertion": false, "indirect_call": false, "io": true, "logging": false, "state_write": false, "unknown_facts": []}
  - transitive effects: {"allocation": false, "assertion": false, "indirect_call": false, "io": true, "logging": false, "state_write": false, "unknown_facts": []}
  - all reachable loops have fixed AST bounds

### 81. `hdr_dpx_determine_file_type`

- Score: `49.75`; confidence: `0.55`; role: `HOST_IO`
- Purity: `IMPURE`; timing: `COMBINATIONAL`; bounded: `True`
- Production reachable: `True`; output contributing: `False`
- Source: `hdr_dpx.c:2051`
- Eligible: `False`
- Evidence:
  - production reachability is a graph traversal from linked executable entry symbols
  - observable output is inferred from output file calls and codec boundary dataflow shape
  - direct effects: {"allocation": false, "assertion": false, "indirect_call": false, "io": true, "logging": false, "state_write": false, "unknown_facts": []}
  - transitive effects: {"allocation": false, "assertion": false, "indirect_call": false, "io": true, "logging": false, "state_write": false, "unknown_facts": []}
  - all reachable loops have fixed AST bounds

### 82. `PErr`

- Score: `49.7`; confidence: `0.55`; role: `HOST_IO`
- Purity: `IMPURE`; timing: `COMBINATIONAL`; bounded: `True`
- Production reachable: `True`; output contributing: `False`
- Source: `logging.c:140`
- Eligible: `False`
- Evidence:
  - production reachability is a graph traversal from linked executable entry symbols
  - observable output is inferred from output file calls and codec boundary dataflow shape
  - direct effects: {"allocation": false, "assertion": false, "indirect_call": false, "io": true, "logging": true, "state_write": false, "unknown_facts": []}
  - transitive effects: {"allocation": false, "assertion": false, "indirect_call": false, "io": true, "logging": true, "state_write": false, "unknown_facts": []}
  - all reachable loops have fixed AST bounds

### 83. `chop_ext`

- Score: `49.7`; confidence: `0.55`; role: `HOST_IO`
- Purity: `IMPURE`; timing: `COMBINATIONAL`; bounded: `True`
- Production reachable: `True`; output contributing: `False`
- Source: `cmd_parse.c:102`
- Eligible: `False`
- Evidence:
  - production reachability is a graph traversal from linked executable entry symbols
  - observable output is inferred from output file calls and codec boundary dataflow shape
  - direct effects: {"allocation": true, "assertion": false, "indirect_call": false, "io": false, "logging": false, "state_write": false, "unknown_facts": []}
  - transitive effects: {"allocation": true, "assertion": false, "indirect_call": false, "io": false, "logging": false, "state_write": false, "unknown_facts": []}
  - all reachable loops have fixed AST bounds

### 84. `appendarg`

- Score: `39.9`; confidence: `0.55`; role: `UNRESOLVED`
- Purity: `PURE`; timing: `COMBINATIONAL`; bounded: `True`
- Production reachable: `False`; output contributing: `False`
- Source: `cmd_parse.c:1328`
- Eligible: `False`
- Evidence:
  - production reachability is a graph traversal from linked executable entry symbols
  - observable output is inferred from output file calls and codec boundary dataflow shape
  - direct effects: {"allocation": false, "assertion": false, "indirect_call": false, "io": false, "logging": false, "state_write": false, "unknown_facts": []}
  - transitive effects: {"allocation": false, "assertion": false, "indirect_call": false, "io": false, "logging": false, "state_write": false, "unknown_facts": []}
  - all reachable loops have fixed AST bounds

### 85. `has_ext`

- Score: `39.9`; confidence: `0.55`; role: `UNRESOLVED`
- Purity: `PURE`; timing: `COMBINATIONAL`; bounded: `True`
- Production reachable: `False`; output contributing: `False`
- Source: `cmd_parse.c:84`
- Eligible: `False`
- Evidence:
  - production reachability is a graph traversal from linked executable entry symbols
  - observable output is inferred from output file calls and codec boundary dataflow shape
  - direct effects: {"allocation": false, "assertion": false, "indirect_call": false, "io": false, "logging": false, "state_write": false, "unknown_facts": []}
  - transitive effects: {"allocation": false, "assertion": false, "indirect_call": false, "io": false, "logging": false, "state_write": false, "unknown_facts": []}
  - all reachable loops have fixed AST bounds

### 86. `fifo_clear`

- Score: `35.0`; confidence: `0.55`; role: `UNRESOLVED`
- Purity: `IMPURE`; timing: `STATEFUL`; bounded: `True`
- Production reachable: `True`; output contributing: `False`
- Source: `fifo.c:55`
- Eligible: `False`
- Evidence:
  - production reachability is a graph traversal from linked executable entry symbols
  - observable output is inferred from output file calls and codec boundary dataflow shape
  - direct effects: {"allocation": false, "assertion": false, "indirect_call": false, "io": false, "logging": false, "state_write": true, "unknown_facts": []}
  - transitive effects: {"allocation": false, "assertion": false, "indirect_call": false, "io": false, "logging": false, "state_write": true, "unknown_facts": []}
  - all reachable loops have fixed AST bounds

### 87. `pcopy_header`

- Score: `35.0`; confidence: `0.55`; role: `UNRESOLVED`
- Purity: `IMPURE`; timing: `STATEFUL`; bounded: `True`
- Production reachable: `True`; output contributing: `False`
- Source: `utl.c:225`
- Eligible: `False`
- Evidence:
  - production reachability is a graph traversal from linked executable entry symbols
  - observable output is inferred from output file calls and codec boundary dataflow shape
  - direct effects: {"allocation": false, "assertion": false, "indirect_call": false, "io": false, "logging": false, "state_write": true, "unknown_facts": []}
  - transitive effects: {"allocation": false, "assertion": false, "indirect_call": false, "io": false, "logging": false, "state_write": true, "unknown_facts": []}
  - all reachable loops have fixed AST bounds

### 88. `set_convertbits_rounding`

- Score: `35.0`; confidence: `0.55`; role: `UNRESOLVED`
- Purity: `IMPURE`; timing: `STATEFUL`; bounded: `True`
- Production reachable: `True`; output contributing: `False`
- Source: `utl.c:705`
- Eligible: `False`
- Evidence:
  - production reachability is a graph traversal from linked executable entry symbols
  - observable output is inferred from output file calls and codec boundary dataflow shape
  - direct effects: {"allocation": false, "assertion": false, "indirect_call": false, "io": false, "logging": false, "state_write": true, "unknown_facts": []}
  - transitive effects: {"allocation": false, "assertion": false, "indirect_call": false, "io": false, "logging": false, "state_write": true, "unknown_facts": []}
  - all reachable loops have fixed AST bounds

### 89. `compute_offset`

- Score: `34.95`; confidence: `0.55`; role: `CONFIG`
- Purity: `IMPURE`; timing: `STATEFUL`; bounded: `True`
- Production reachable: `True`; output contributing: `False`
- Source: `codec_main.c:616`
- Eligible: `False`
- Evidence:
  - production reachability is a graph traversal from linked executable entry symbols
  - observable output is inferred from output file calls and codec boundary dataflow shape
  - direct effects: {"allocation": false, "assertion": false, "indirect_call": false, "io": false, "logging": false, "state_write": true, "unknown_facts": []}
  - transitive effects: {"allocation": false, "assertion": false, "indirect_call": false, "io": false, "logging": false, "state_write": true, "unknown_facts": []}
  - all reachable loops have fixed AST bounds

### 90. `hdr_dpx_compute_offsets`

- Score: `34.95`; confidence: `0.55`; role: `HOST_IO`
- Purity: `IMPURE`; timing: `STATEFUL`; bounded: `True`
- Production reachable: `True`; output contributing: `False`
- Source: `hdr_dpx.c:1514`
- Eligible: `False`
- Evidence:
  - production reachability is a graph traversal from linked executable entry symbols
  - observable output is inferred from output file calls and codec boundary dataflow shape
  - direct effects: {"allocation": false, "assertion": false, "indirect_call": false, "io": true, "logging": false, "state_write": true, "unknown_facts": []}
  - transitive effects: {"allocation": false, "assertion": false, "indirect_call": false, "io": true, "logging": false, "state_write": true, "unknown_facts": []}
  - all reachable loops have fixed AST bounds

### 91. `set_defaults`

- Score: `34.9`; confidence: `0.55`; role: `UNRESOLVED`
- Purity: `IMPURE`; timing: `STATEFUL`; bounded: `True`
- Production reachable: `True`; output contributing: `False`
- Source: `codec_main.c:222`
- Eligible: `False`
- Evidence:
  - production reachability is a graph traversal from linked executable entry symbols
  - observable output is inferred from output file calls and codec boundary dataflow shape
  - direct effects: {"allocation": false, "assertion": false, "indirect_call": false, "io": false, "logging": false, "state_write": true, "unknown_facts": []}
  - transitive effects: {"allocation": false, "assertion": false, "indirect_call": false, "io": false, "logging": false, "state_write": true, "unknown_facts": []}
  - all reachable loops have fixed AST bounds

### 92. `splitstring`

- Score: `34.9`; confidence: `0.55`; role: `UNRESOLVED`
- Purity: `IMPURE`; timing: `STATEFUL`; bounded: `True`
- Production reachable: `True`; output contributing: `False`
- Source: `cmd_parse.c:392`
- Eligible: `False`
- Evidence:
  - production reachability is a graph traversal from linked executable entry symbols
  - observable output is inferred from output file calls and codec boundary dataflow shape
  - direct effects: {"allocation": false, "assertion": false, "indirect_call": false, "io": false, "logging": false, "state_write": true, "unknown_facts": []}
  - transitive effects: {"allocation": false, "assertion": false, "indirect_call": false, "io": false, "logging": false, "state_write": true, "unknown_facts": []}
  - all reachable loops have fixed AST bounds

### 93. `str2frange`

- Score: `34.9`; confidence: `0.55`; role: `HOST_IO`
- Purity: `IMPURE`; timing: `STATEFUL`; bounded: `True`
- Production reachable: `True`; output contributing: `False`
- Source: `cmd_parse.c:596`
- Eligible: `False`
- Evidence:
  - production reachability is a graph traversal from linked executable entry symbols
  - observable output is inferred from output file calls and codec boundary dataflow shape
  - direct effects: {"allocation": false, "assertion": false, "indirect_call": false, "io": false, "logging": false, "state_write": true, "unknown_facts": []}
  - transitive effects: {"allocation": false, "assertion": false, "indirect_call": false, "io": true, "logging": true, "state_write": true, "unknown_facts": []}
  - all reachable loops have fixed AST bounds

### 94. `str2prange`

- Score: `34.9`; confidence: `0.55`; role: `HOST_IO`
- Purity: `IMPURE`; timing: `STATEFUL`; bounded: `True`
- Production reachable: `True`; output contributing: `False`
- Source: `cmd_parse.c:580`
- Eligible: `False`
- Evidence:
  - production reachability is a graph traversal from linked executable entry symbols
  - observable output is inferred from output file calls and codec boundary dataflow shape
  - direct effects: {"allocation": false, "assertion": false, "indirect_call": false, "io": false, "logging": false, "state_write": true, "unknown_facts": []}
  - transitive effects: {"allocation": false, "assertion": false, "indirect_call": false, "io": true, "logging": true, "state_write": true, "unknown_facts": []}
  - all reachable loops have fixed AST bounds

### 95. `str2range`

- Score: `34.9`; confidence: `0.55`; role: `HOST_IO`
- Purity: `IMPURE`; timing: `STATEFUL`; bounded: `True`
- Production reachable: `True`; output contributing: `False`
- Source: `cmd_parse.c:588`
- Eligible: `False`
- Evidence:
  - production reachability is a graph traversal from linked executable entry symbols
  - observable output is inferred from output file calls and codec boundary dataflow shape
  - direct effects: {"allocation": false, "assertion": false, "indirect_call": false, "io": false, "logging": false, "state_write": true, "unknown_facts": []}
  - transitive effects: {"allocation": false, "assertion": false, "indirect_call": false, "io": true, "logging": true, "state_write": true, "unknown_facts": []}
  - all reachable loops have fixed AST bounds

### 96. `parse_kvline`

- Score: `34.75`; confidence: `0.55`; role: `CHECKER`
- Purity: `IMPURE`; timing: `STATEFUL`; bounded: `True`
- Production reachable: `True`; output contributing: `False`
- Source: `cmd_parse.c:1142`
- Eligible: `False`
- Evidence:
  - production reachability is a graph traversal from linked executable entry symbols
  - observable output is inferred from output file calls and codec boundary dataflow shape
  - direct effects: {"allocation": false, "assertion": true, "indirect_call": false, "io": false, "logging": true, "state_write": true, "unknown_facts": []}
  - transitive effects: {"allocation": false, "assertion": true, "indirect_call": false, "io": true, "logging": true, "state_write": true, "unknown_facts": []}
  - all reachable loops have fixed AST bounds

### 97. `hdr_dpx_check_string`

- Score: `30.0`; confidence: `0.55`; role: `UNRESOLVED`
- Purity: `IMPURE`; timing: `UNKNOWN`; bounded: `False`
- Production reachable: `True`; output contributing: `False`
- Source: `hdr_dpx.c:1537`
- Eligible: `False`
- Evidence:
  - production reachability is a graph traversal from linked executable entry symbols
  - observable output is inferred from output file calls and codec boundary dataflow shape
  - direct effects: {"allocation": false, "assertion": false, "indirect_call": false, "io": false, "logging": false, "state_write": true, "unknown_facts": []}
  - transitive effects: {"allocation": false, "assertion": false, "indirect_call": false, "io": false, "logging": false, "state_write": true, "unknown_facts": []}
  - at least one reachable loop has UNKNOWN bounds

### 98. `test_cmd`

- Score: `30.0`; confidence: `0.55`; role: `UNRESOLVED`
- Purity: `IMPURE`; timing: `UNKNOWN`; bounded: `False`
- Production reachable: `True`; output contributing: `False`
- Source: `cmd_parse.c:1116`
- Eligible: `False`
- Evidence:
  - production reachability is a graph traversal from linked executable entry symbols
  - observable output is inferred from output file calls and codec boundary dataflow shape
  - direct effects: {"allocation": false, "assertion": false, "indirect_call": false, "io": false, "logging": false, "state_write": true, "unknown_facts": []}
  - transitive effects: {"allocation": false, "assertion": false, "indirect_call": false, "io": false, "logging": false, "state_write": true, "unknown_facts": []}
  - at least one reachable loop has UNKNOWN bounds

### 99. `create_dpx_pic`

- Score: `29.95`; confidence: `0.55`; role: `CHECKER`
- Purity: `IMPURE`; timing: `UNKNOWN`; bounded: `False`
- Production reachable: `True`; output contributing: `False`
- Source: `dpx.c:1420`
- Eligible: `False`
- Evidence:
  - production reachability is a graph traversal from linked executable entry symbols
  - observable output is inferred from output file calls and codec boundary dataflow shape
  - direct effects: {"allocation": false, "assertion": false, "indirect_call": false, "io": false, "logging": false, "state_write": true, "unknown_facts": []}
  - transitive effects: {"allocation": true, "assertion": true, "indirect_call": false, "io": true, "logging": false, "state_write": true, "unknown_facts": []}
  - at least one reachable loop has UNKNOWN bounds

### 100. `dpx_read`

- Score: `29.95`; confidence: `0.55`; role: `CHECKER`
- Purity: `IMPURE`; timing: `UNKNOWN`; bounded: `False`
- Production reachable: `True`; output contributing: `False`
- Source: `dpx.c:744`
- Eligible: `False`
- Evidence:
  - production reachability is a graph traversal from linked executable entry symbols
  - observable output is inferred from output file calls and codec boundary dataflow shape
  - direct effects: {"allocation": false, "assertion": false, "indirect_call": false, "io": false, "logging": false, "state_write": false, "unknown_facts": []}
  - transitive effects: {"allocation": true, "assertion": true, "indirect_call": false, "io": true, "logging": true, "state_write": true, "unknown_facts": []}
  - at least one reachable loop has UNKNOWN bounds

### 101. `gettoken`

- Score: `29.95`; confidence: `0.55`; role: `UNRESOLVED`
- Purity: `IMPURE`; timing: `UNKNOWN`; bounded: `False`
- Production reachable: `True`; output contributing: `False`
- Source: `utl.c:1038`
- Eligible: `False`
- Evidence:
  - production reachability is a graph traversal from linked executable entry symbols
  - observable output is inferred from output file calls and codec boundary dataflow shape
  - direct effects: {"allocation": false, "assertion": false, "indirect_call": false, "io": false, "logging": false, "state_write": true, "unknown_facts": []}
  - transitive effects: {"allocation": false, "assertion": false, "indirect_call": false, "io": false, "logging": false, "state_write": true, "unknown_facts": []}
  - at least one reachable loop has UNKNOWN bounds

### 102. `hdr_dpx_map_datum_to_pic`

- Score: `29.95`; confidence: `0.55`; role: `HOST_IO`
- Purity: `IMPURE`; timing: `UNKNOWN`; bounded: `False`
- Production reachable: `True`; output contributing: `False`
- Source: `hdr_dpx.c:621`
- Eligible: `False`
- Evidence:
  - production reachability is a graph traversal from linked executable entry symbols
  - observable output is inferred from output file calls and codec boundary dataflow shape
  - direct effects: {"allocation": false, "assertion": false, "indirect_call": false, "io": true, "logging": false, "state_write": true, "unknown_facts": []}
  - transitive effects: {"allocation": false, "assertion": false, "indirect_call": false, "io": true, "logging": false, "state_write": true, "unknown_facts": []}
  - at least one reachable loop has UNKNOWN bounds

### 103. `make_qp_tables`

- Score: `29.95`; confidence: `0.55`; role: `HOST_IO`
- Purity: `IMPURE`; timing: `UNKNOWN`; bounded: `False`
- Production reachable: `True`; output contributing: `False`
- Source: `rc_tables.h:414`
- Eligible: `False`
- Evidence:
  - production reachability is a graph traversal from linked executable entry symbols
  - observable output is inferred from output file calls and codec boundary dataflow shape
  - direct effects: {"allocation": false, "assertion": false, "indirect_call": false, "io": false, "logging": false, "state_write": false, "unknown_facts": []}
  - transitive effects: {"allocation": true, "assertion": false, "indirect_call": false, "io": false, "logging": false, "state_write": true, "unknown_facts": []}
  - at least one reachable loop has UNKNOWN bounds

### 104. `pdestroy`

- Score: `29.95`; confidence: `0.55`; role: `HOST_IO`
- Purity: `IMPURE`; timing: `UNKNOWN`; bounded: `False`
- Production reachable: `True`; output contributing: `False`
- Source: `utl.c:241`
- Eligible: `False`
- Evidence:
  - production reachability is a graph traversal from linked executable entry symbols
  - observable output is inferred from output file calls and codec boundary dataflow shape
  - direct effects: {"allocation": true, "assertion": false, "indirect_call": false, "io": false, "logging": false, "state_write": false, "unknown_facts": []}
  - transitive effects: {"allocation": true, "assertion": false, "indirect_call": false, "io": false, "logging": false, "state_write": false, "unknown_facts": []}
  - at least one reachable loop has UNKNOWN bounds

### 105. `write_pps`

- Score: `29.95`; confidence: `0.55`; role: `CONFIG`
- Purity: `IMPURE`; timing: `UNKNOWN`; bounded: `False`
- Production reachable: `True`; output contributing: `False`
- Source: `dsc_utils.c:514`
- Eligible: `False`
- Evidence:
  - production reachability is a graph traversal from linked executable entry symbols
  - observable output is inferred from output file calls and codec boundary dataflow shape
  - direct effects: {"allocation": false, "assertion": false, "indirect_call": false, "io": false, "logging": false, "state_write": false, "unknown_facts": []}
  - transitive effects: {"allocation": false, "assertion": false, "indirect_call": false, "io": false, "logging": true, "state_write": true, "unknown_facts": []}
  - at least one reachable loop has UNKNOWN bounds

### 106. `yuv_420_422`

- Score: `29.95`; confidence: `0.55`; role: `UNRESOLVED`
- Purity: `IMPURE`; timing: `UNKNOWN`; bounded: `False`
- Production reachable: `True`; output contributing: `False`
- Source: `utl.c:671`
- Eligible: `False`
- Evidence:
  - production reachability is a graph traversal from linked executable entry symbols
  - observable output is inferred from output file calls and codec boundary dataflow shape
  - direct effects: {"allocation": false, "assertion": false, "indirect_call": false, "io": false, "logging": false, "state_write": true, "unknown_facts": []}
  - transitive effects: {"allocation": false, "assertion": false, "indirect_call": false, "io": false, "logging": false, "state_write": true, "unknown_facts": []}
  - at least one reachable loop has UNKNOWN bounds

### 107. `yuv_422_444`

- Score: `29.95`; confidence: `0.55`; role: `UNRESOLVED`
- Purity: `IMPURE`; timing: `UNKNOWN`; bounded: `False`
- Production reachable: `True`; output contributing: `False`
- Source: `utl.c:503`
- Eligible: `False`
- Evidence:
  - production reachability is a graph traversal from linked executable entry symbols
  - observable output is inferred from output file calls and codec boundary dataflow shape
  - direct effects: {"allocation": false, "assertion": false, "indirect_call": false, "io": false, "logging": false, "state_write": true, "unknown_facts": []}
  - transitive effects: {"allocation": false, "assertion": false, "indirect_call": false, "io": false, "logging": false, "state_write": true, "unknown_facts": []}
  - at least one reachable loop has UNKNOWN bounds

### 108. `check_qp_for_overflow`

- Score: `29.9`; confidence: `0.55`; role: `CONFIG`
- Purity: `IMPURE`; timing: `UNKNOWN`; bounded: `False`
- Production reachable: `True`; output contributing: `False`
- Source: `codec_main.c:860`
- Eligible: `False`
- Evidence:
  - production reachability is a graph traversal from linked executable entry symbols
  - observable output is inferred from output file calls and codec boundary dataflow shape
  - direct effects: {"allocation": false, "assertion": false, "indirect_call": false, "io": false, "logging": true, "state_write": true, "unknown_facts": []}
  - transitive effects: {"allocation": false, "assertion": false, "indirect_call": false, "io": false, "logging": true, "state_write": true, "unknown_facts": []}
  - at least one reachable loop has UNKNOWN bounds

### 109. `fifo_flip_get_bits`

- Score: `29.9`; confidence: `0.55`; role: `HOST_IO`
- Purity: `IMPURE`; timing: `UNKNOWN`; bounded: `False`
- Production reachable: `True`; output contributing: `False`
- Source: `fifo.c:174`
- Eligible: `False`
- Evidence:
  - production reachability is a graph traversal from linked executable entry symbols
  - observable output is inferred from output file calls and codec boundary dataflow shape
  - direct effects: {"allocation": false, "assertion": false, "indirect_call": false, "io": false, "logging": true, "state_write": true, "unknown_facts": []}
  - transitive effects: {"allocation": false, "assertion": false, "indirect_call": false, "io": false, "logging": true, "state_write": true, "unknown_facts": []}
  - at least one reachable loop has UNKNOWN bounds

### 110. `fifo_flip_put_bits`

- Score: `29.9`; confidence: `0.55`; role: `HOST_IO`
- Purity: `IMPURE`; timing: `UNKNOWN`; bounded: `False`
- Production reachable: `True`; output contributing: `False`
- Source: `fifo.c:217`
- Eligible: `False`
- Evidence:
  - production reachability is a graph traversal from linked executable entry symbols
  - observable output is inferred from output file calls and codec boundary dataflow shape
  - direct effects: {"allocation": false, "assertion": false, "indirect_call": false, "io": false, "logging": true, "state_write": true, "unknown_facts": []}
  - transitive effects: {"allocation": false, "assertion": false, "indirect_call": false, "io": false, "logging": true, "state_write": true, "unknown_facts": []}
  - at least one reachable loop has UNKNOWN bounds

### 111. `generate_rc_parameters`

- Score: `29.9`; confidence: `0.55`; role: `CONFIG`
- Purity: `IMPURE`; timing: `UNKNOWN`; bounded: `False`
- Production reachable: `True`; output contributing: `False`
- Source: `codec_main.c:904`
- Eligible: `False`
- Evidence:
  - production reachability is a graph traversal from linked executable entry symbols
  - observable output is inferred from output file calls and codec boundary dataflow shape
  - direct effects: {"allocation": false, "assertion": false, "indirect_call": false, "io": false, "logging": true, "state_write": true, "unknown_facts": []}
  - transitive effects: {"allocation": true, "assertion": false, "indirect_call": false, "io": true, "logging": true, "state_write": true, "unknown_facts": []}
  - at least one reachable loop has UNKNOWN bounds

### 112. `hdr_dpx_get_datum`

- Score: `29.9`; confidence: `0.55`; role: `HOST_IO`
- Purity: `IMPURE`; timing: `UNKNOWN`; bounded: `False`
- Production reachable: `True`; output contributing: `False`
- Source: `hdr_dpx.c:1153`
- Eligible: `False`
- Evidence:
  - production reachability is a graph traversal from linked executable entry symbols
  - observable output is inferred from output file calls and codec boundary dataflow shape
  - direct effects: {"allocation": false, "assertion": false, "indirect_call": false, "io": false, "logging": false, "state_write": true, "unknown_facts": []}
  - transitive effects: {"allocation": false, "assertion": false, "indirect_call": false, "io": false, "logging": true, "state_write": true, "unknown_facts": []}
  - at least one reachable loop has UNKNOWN bounds

### 113. `line_to_int`

- Score: `29.9`; confidence: `0.55`; role: `HOST_IO`
- Purity: `IMPURE`; timing: `UNKNOWN`; bounded: `False`
- Production reachable: `True`; output contributing: `False`
- Source: `rc_tables.h:382`
- Eligible: `False`
- Evidence:
  - production reachability is a graph traversal from linked executable entry symbols
  - observable output is inferred from output file calls and codec boundary dataflow shape
  - direct effects: {"allocation": true, "assertion": false, "indirect_call": false, "io": false, "logging": false, "state_write": true, "unknown_facts": []}
  - transitive effects: {"allocation": true, "assertion": false, "indirect_call": false, "io": false, "logging": false, "state_write": true, "unknown_facts": []}
  - at least one reachable loop has UNKNOWN bounds

### 114. `make_qp_table`

- Score: `29.9`; confidence: `0.55`; role: `HOST_IO`
- Purity: `IMPURE`; timing: `UNKNOWN`; bounded: `False`
- Production reachable: `True`; output contributing: `False`
- Source: `rc_tables.h:404`
- Eligible: `False`
- Evidence:
  - production reachability is a graph traversal from linked executable entry symbols
  - observable output is inferred from output file calls and codec boundary dataflow shape
  - direct effects: {"allocation": true, "assertion": false, "indirect_call": false, "io": false, "logging": false, "state_write": false, "unknown_facts": []}
  - transitive effects: {"allocation": true, "assertion": false, "indirect_call": false, "io": false, "logging": false, "state_write": true, "unknown_facts": []}
  - at least one reachable loop has UNKNOWN bounds

### 115. `parse_pps`

- Score: `29.9`; confidence: `0.55`; role: `CONFIG`
- Purity: `IMPURE`; timing: `UNKNOWN`; bounded: `False`
- Production reachable: `True`; output contributing: `False`
- Source: `dsc_utils.c:404`
- Eligible: `False`
- Evidence:
  - production reachability is a graph traversal from linked executable entry symbols
  - observable output is inferred from output file calls and codec boundary dataflow shape
  - direct effects: {"allocation": false, "assertion": false, "indirect_call": false, "io": false, "logging": true, "state_write": true, "unknown_facts": []}
  - transitive effects: {"allocation": false, "assertion": false, "indirect_call": false, "io": true, "logging": true, "state_write": true, "unknown_facts": []}
  - at least one reachable loop has UNKNOWN bounds

### 116. `uyvy_read`

- Score: `29.9`; confidence: `0.55`; role: `HOST_IO`
- Purity: `IMPURE`; timing: `UNKNOWN`; bounded: `False`
- Production reachable: `True`; output contributing: `False`
- Source: `utl.c:1306`
- Eligible: `False`
- Evidence:
  - production reachability is a graph traversal from linked executable entry symbols
  - observable output is inferred from output file calls and codec boundary dataflow shape
  - direct effects: {"allocation": false, "assertion": false, "indirect_call": false, "io": true, "logging": false, "state_write": true, "unknown_facts": []}
  - transitive effects: {"allocation": false, "assertion": false, "indirect_call": false, "io": true, "logging": false, "state_write": true, "unknown_facts": []}
  - at least one reachable loop has UNKNOWN bounds

### 117. `uyvy_write`

- Score: `29.9`; confidence: `0.55`; role: `HOST_IO`
- Purity: `IMPURE`; timing: `UNKNOWN`; bounded: `False`
- Production reachable: `True`; output contributing: `False`
- Source: `utl.c:1420`
- Eligible: `False`
- Evidence:
  - production reachability is a graph traversal from linked executable entry symbols
  - observable output is inferred from output file calls and codec boundary dataflow shape
  - direct effects: {"allocation": false, "assertion": false, "indirect_call": false, "io": true, "logging": false, "state_write": false, "unknown_facts": []}
  - transitive effects: {"allocation": false, "assertion": false, "indirect_call": false, "io": true, "logging": false, "state_write": false, "unknown_facts": []}
  - at least one reachable loop has UNKNOWN bounds

### 118. `writeppm`

- Score: `29.9`; confidence: `0.55`; role: `HOST_IO`
- Purity: `IMPURE`; timing: `UNKNOWN`; bounded: `False`
- Production reachable: `True`; output contributing: `False`
- Source: `utl.c:1222`
- Eligible: `False`
- Evidence:
  - production reachability is a graph traversal from linked executable entry symbols
  - observable output is inferred from output file calls and codec boundary dataflow shape
  - direct effects: {"allocation": false, "assertion": false, "indirect_call": false, "io": true, "logging": false, "state_write": false, "unknown_facts": []}
  - transitive effects: {"allocation": false, "assertion": false, "indirect_call": false, "io": true, "logging": false, "state_write": false, "unknown_facts": []}
  - at least one reachable loop has UNKNOWN bounds

### 119. `assign_line`

- Score: `29.85`; confidence: `0.55`; role: `CHECKER`
- Purity: `IMPURE`; timing: `UNKNOWN`; bounded: `False`
- Production reachable: `True`; output contributing: `False`
- Source: `codec_main.c:358`
- Eligible: `False`
- Evidence:
  - production reachability is a graph traversal from linked executable entry symbols
  - observable output is inferred from output file calls and codec boundary dataflow shape
  - direct effects: {"allocation": false, "assertion": false, "indirect_call": false, "io": false, "logging": true, "state_write": true, "unknown_facts": []}
  - transitive effects: {"allocation": false, "assertion": true, "indirect_call": false, "io": true, "logging": true, "state_write": true, "unknown_facts": []}
  - at least one reachable loop has UNKNOWN bounds

### 120. `distinguish_dist`

- Score: `29.85`; confidence: `0.55`; role: `CHECKER`
- Purity: `IMPURE`; timing: `UNKNOWN`; bounded: `False`
- Production reachable: `True`; output contributing: `False`
- Source: `cmd_parse.c:1084`
- Eligible: `False`
- Evidence:
  - production reachability is a graph traversal from linked executable entry symbols
  - observable output is inferred from output file calls and codec boundary dataflow shape
  - direct effects: {"allocation": true, "assertion": true, "indirect_call": false, "io": false, "logging": false, "state_write": true, "unknown_facts": []}
  - transitive effects: {"allocation": true, "assertion": true, "indirect_call": false, "io": true, "logging": false, "state_write": true, "unknown_facts": []}
  - at least one reachable loop has UNKNOWN bounds

### 121. `error_check`

- Score: `29.85`; confidence: `0.55`; role: `HOST_IO`
- Purity: `IMPURE`; timing: `UNKNOWN`; bounded: `False`
- Production reachable: `True`; output contributing: `False`
- Source: `cmd_parse.c:952`
- Eligible: `False`
- Evidence:
  - production reachability is a graph traversal from linked executable entry symbols
  - observable output is inferred from output file calls and codec boundary dataflow shape
  - direct effects: {"allocation": false, "assertion": false, "indirect_call": false, "io": false, "logging": true, "state_write": true, "unknown_facts": []}
  - transitive effects: {"allocation": false, "assertion": false, "indirect_call": false, "io": true, "logging": true, "state_write": true, "unknown_facts": []}
  - at least one reachable loop has UNKNOWN bounds

### 122. `hdr_dpx_create_pic`

- Score: `29.85`; confidence: `0.55`; role: `CHECKER`
- Purity: `IMPURE`; timing: `UNKNOWN`; bounded: `False`
- Production reachable: `True`; output contributing: `False`
- Source: `hdr_dpx.c:234`
- Eligible: `False`
- Evidence:
  - production reachability is a graph traversal from linked executable entry symbols
  - observable output is inferred from output file calls and codec boundary dataflow shape
  - direct effects: {"allocation": false, "assertion": false, "indirect_call": false, "io": true, "logging": false, "state_write": true, "unknown_facts": []}
  - transitive effects: {"allocation": true, "assertion": true, "indirect_call": false, "io": true, "logging": false, "state_write": true, "unknown_facts": []}
  - at least one reachable loop has UNKNOWN bounds

### 123. `order_cmds`

- Score: `29.85`; confidence: `0.55`; role: `CHECKER`
- Purity: `IMPURE`; timing: `UNKNOWN`; bounded: `False`
- Production reachable: `True`; output contributing: `False`
- Source: `cmd_parse.c:1045`
- Eligible: `False`
- Evidence:
  - production reachability is a graph traversal from linked executable entry symbols
  - observable output is inferred from output file calls and codec boundary dataflow shape
  - direct effects: {"allocation": true, "assertion": true, "indirect_call": false, "io": false, "logging": false, "state_write": false, "unknown_facts": []}
  - transitive effects: {"allocation": true, "assertion": true, "indirect_call": false, "io": true, "logging": false, "state_write": false, "unknown_facts": []}
  - at least one reachable loop has UNKNOWN bounds

### 124. `ppm_read`

- Score: `29.85`; confidence: `0.55`; role: `CHECKER`
- Purity: `IMPURE`; timing: `UNKNOWN`; bounded: `False`
- Production reachable: `True`; output contributing: `False`
- Source: `utl.c:1206`
- Eligible: `False`
- Evidence:
  - production reachability is a graph traversal from linked executable entry symbols
  - observable output is inferred from output file calls and codec boundary dataflow shape
  - direct effects: {"allocation": false, "assertion": false, "indirect_call": false, "io": true, "logging": false, "state_write": true, "unknown_facts": []}
  - transitive effects: {"allocation": true, "assertion": true, "indirect_call": false, "io": true, "logging": true, "state_write": true, "unknown_facts": []}
  - at least one reachable loop has UNKNOWN bounds

### 125. `read_dsc_data`

- Score: `29.85`; confidence: `0.55`; role: `HOST_IO`
- Purity: `IMPURE`; timing: `UNKNOWN`; bounded: `False`
- Production reachable: `True`; output contributing: `False`
- Source: `codec_main.c:568`
- Eligible: `False`
- Evidence:
  - production reachability is a graph traversal from linked executable entry symbols
  - observable output is inferred from output file calls and codec boundary dataflow shape
  - direct effects: {"allocation": true, "assertion": false, "indirect_call": false, "io": false, "logging": false, "state_write": true, "unknown_facts": []}
  - transitive effects: {"allocation": true, "assertion": false, "indirect_call": false, "io": false, "logging": false, "state_write": true, "unknown_facts": []}
  - at least one reachable loop has UNKNOWN bounds

### 126. `rgb2yuv`

- Score: `29.85`; confidence: `0.55`; role: `HOST_IO`
- Purity: `IMPURE`; timing: `UNKNOWN`; bounded: `False`
- Production reachable: `True`; output contributing: `False`
- Source: `utl.c:305`
- Eligible: `False`
- Evidence:
  - production reachability is a graph traversal from linked executable entry symbols
  - observable output is inferred from output file calls and codec boundary dataflow shape
  - direct effects: {"allocation": false, "assertion": false, "indirect_call": false, "io": true, "logging": false, "state_write": true, "unknown_facts": []}
  - transitive effects: {"allocation": false, "assertion": false, "indirect_call": false, "io": true, "logging": false, "state_write": true, "unknown_facts": []}
  - at least one reachable loop has UNKNOWN bounds

### 127. `simple422to444`

- Score: `29.85`; confidence: `0.55`; role: `HOST_IO`
- Purity: `IMPURE`; timing: `UNKNOWN`; bounded: `False`
- Production reachable: `True`; output contributing: `False`
- Source: `dsc_utils.c:306`
- Eligible: `False`
- Evidence:
  - production reachability is a graph traversal from linked executable entry symbols
  - observable output is inferred from output file calls and codec boundary dataflow shape
  - direct effects: {"allocation": false, "assertion": false, "indirect_call": false, "io": true, "logging": false, "state_write": true, "unknown_facts": []}
  - transitive effects: {"allocation": false, "assertion": false, "indirect_call": false, "io": true, "logging": false, "state_write": true, "unknown_facts": []}
  - at least one reachable loop has UNKNOWN bounds

### 128. `simple444to422`

- Score: `29.85`; confidence: `0.55`; role: `HOST_IO`
- Purity: `IMPURE`; timing: `UNKNOWN`; bounded: `False`
- Production reachable: `True`; output contributing: `False`
- Source: `dsc_utils.c:344`
- Eligible: `False`
- Evidence:
  - production reachability is a graph traversal from linked executable entry symbols
  - observable output is inferred from output file calls and codec boundary dataflow shape
  - direct effects: {"allocation": false, "assertion": false, "indirect_call": false, "io": true, "logging": false, "state_write": true, "unknown_facts": []}
  - transitive effects: {"allocation": false, "assertion": false, "indirect_call": false, "io": true, "logging": false, "state_write": true, "unknown_facts": []}
  - at least one reachable loop has UNKNOWN bounds

### 129. `str2dim`

- Score: `29.85`; confidence: `0.55`; role: `HOST_IO`
- Purity: `IMPURE`; timing: `UNKNOWN`; bounded: `False`
- Production reachable: `True`; output contributing: `False`
- Source: `cmd_parse.c:612`
- Eligible: `False`
- Evidence:
  - production reachability is a graph traversal from linked executable entry symbols
  - observable output is inferred from output file calls and codec boundary dataflow shape
  - direct effects: {"allocation": false, "assertion": false, "indirect_call": false, "io": false, "logging": false, "state_write": true, "unknown_facts": []}
  - transitive effects: {"allocation": false, "assertion": false, "indirect_call": false, "io": true, "logging": true, "state_write": true, "unknown_facts": []}
  - at least one reachable loop has UNKNOWN bounds

### 130. `str2dvect`

- Score: `29.85`; confidence: `0.55`; role: `HOST_IO`
- Purity: `IMPURE`; timing: `UNKNOWN`; bounded: `False`
- Production reachable: `True`; output contributing: `False`
- Source: `cmd_parse.c:780`
- Eligible: `False`
- Evidence:
  - production reachability is a graph traversal from linked executable entry symbols
  - observable output is inferred from output file calls and codec boundary dataflow shape
  - direct effects: {"allocation": false, "assertion": false, "indirect_call": false, "io": false, "logging": true, "state_write": true, "unknown_facts": []}
  - transitive effects: {"allocation": false, "assertion": false, "indirect_call": false, "io": true, "logging": true, "state_write": true, "unknown_facts": []}
  - at least one reachable loop has UNKNOWN bounds

### 131. `str2fdim`

- Score: `29.85`; confidence: `0.55`; role: `HOST_IO`
- Purity: `IMPURE`; timing: `UNKNOWN`; bounded: `False`
- Production reachable: `True`; output contributing: `False`
- Source: `cmd_parse.c:620`
- Eligible: `False`
- Evidence:
  - production reachability is a graph traversal from linked executable entry symbols
  - observable output is inferred from output file calls and codec boundary dataflow shape
  - direct effects: {"allocation": false, "assertion": false, "indirect_call": false, "io": false, "logging": false, "state_write": true, "unknown_facts": []}
  - transitive effects: {"allocation": false, "assertion": false, "indirect_call": false, "io": true, "logging": true, "state_write": true, "unknown_facts": []}
  - at least one reachable loop has UNKNOWN bounds

### 132. `str2fvect`

- Score: `29.85`; confidence: `0.55`; role: `HOST_IO`
- Purity: `IMPURE`; timing: `UNKNOWN`; bounded: `False`
- Production reachable: `True`; output contributing: `False`
- Source: `cmd_parse.c:761`
- Eligible: `False`
- Evidence:
  - production reachability is a graph traversal from linked executable entry symbols
  - observable output is inferred from output file calls and codec boundary dataflow shape
  - direct effects: {"allocation": false, "assertion": false, "indirect_call": false, "io": false, "logging": true, "state_write": true, "unknown_facts": []}
  - transitive effects: {"allocation": false, "assertion": false, "indirect_call": false, "io": true, "logging": true, "state_write": true, "unknown_facts": []}
  - at least one reachable loop has UNKNOWN bounds

### 133. `str2ivect`

- Score: `29.85`; confidence: `0.55`; role: `HOST_IO`
- Purity: `IMPURE`; timing: `UNKNOWN`; bounded: `False`
- Production reachable: `True`; output contributing: `False`
- Source: `cmd_parse.c:628`
- Eligible: `False`
- Evidence:
  - production reachability is a graph traversal from linked executable entry symbols
  - observable output is inferred from output file calls and codec boundary dataflow shape
  - direct effects: {"allocation": false, "assertion": false, "indirect_call": false, "io": false, "logging": true, "state_write": true, "unknown_facts": []}
  - transitive effects: {"allocation": false, "assertion": false, "indirect_call": false, "io": true, "logging": true, "state_write": true, "unknown_facts": []}
  - at least one reachable loop has UNKNOWN bounds

### 134. `str2llvect`

- Score: `29.85`; confidence: `0.55`; role: `HOST_IO`
- Purity: `IMPURE`; timing: `UNKNOWN`; bounded: `False`
- Production reachable: `True`; output contributing: `False`
- Source: `cmd_parse.c:723`
- Eligible: `False`
- Evidence:
  - production reachability is a graph traversal from linked executable entry symbols
  - observable output is inferred from output file calls and codec boundary dataflow shape
  - direct effects: {"allocation": false, "assertion": false, "indirect_call": false, "io": false, "logging": true, "state_write": true, "unknown_facts": []}
  - transitive effects: {"allocation": false, "assertion": false, "indirect_call": false, "io": true, "logging": true, "state_write": true, "unknown_facts": []}
  - at least one reachable loop has UNKNOWN bounds

### 135. `str2lvect`

- Score: `29.85`; confidence: `0.55`; role: `HOST_IO`
- Purity: `IMPURE`; timing: `UNKNOWN`; bounded: `False`
- Production reachable: `True`; output contributing: `False`
- Source: `cmd_parse.c:685`
- Eligible: `False`
- Evidence:
  - production reachability is a graph traversal from linked executable entry symbols
  - observable output is inferred from output file calls and codec boundary dataflow shape
  - direct effects: {"allocation": false, "assertion": false, "indirect_call": false, "io": false, "logging": true, "state_write": true, "unknown_facts": []}
  - transitive effects: {"allocation": false, "assertion": false, "indirect_call": false, "io": true, "logging": true, "state_write": true, "unknown_facts": []}
  - at least one reachable loop has UNKNOWN bounds

### 136. `str2pdim`

- Score: `29.85`; confidence: `0.55`; role: `HOST_IO`
- Purity: `IMPURE`; timing: `UNKNOWN`; bounded: `False`
- Production reachable: `True`; output contributing: `False`
- Source: `cmd_parse.c:604`
- Eligible: `False`
- Evidence:
  - production reachability is a graph traversal from linked executable entry symbols
  - observable output is inferred from output file calls and codec boundary dataflow shape
  - direct effects: {"allocation": false, "assertion": false, "indirect_call": false, "io": false, "logging": false, "state_write": true, "unknown_facts": []}
  - transitive effects: {"allocation": false, "assertion": false, "indirect_call": false, "io": true, "logging": true, "state_write": true, "unknown_facts": []}
  - at least one reachable loop has UNKNOWN bounds

### 137. `str2pvect`

- Score: `29.85`; confidence: `0.55`; role: `HOST_IO`
- Purity: `IMPURE`; timing: `UNKNOWN`; bounded: `False`
- Production reachable: `True`; output contributing: `False`
- Source: `cmd_parse.c:647`
- Eligible: `False`
- Evidence:
  - production reachability is a graph traversal from linked executable entry symbols
  - observable output is inferred from output file calls and codec boundary dataflow shape
  - direct effects: {"allocation": false, "assertion": false, "indirect_call": false, "io": false, "logging": true, "state_write": true, "unknown_facts": []}
  - transitive effects: {"allocation": false, "assertion": false, "indirect_call": false, "io": true, "logging": true, "state_write": true, "unknown_facts": []}
  - at least one reachable loop has UNKNOWN bounds

### 138. `str2uivect`

- Score: `29.85`; confidence: `0.55`; role: `HOST_IO`
- Purity: `IMPURE`; timing: `UNKNOWN`; bounded: `False`
- Production reachable: `True`; output contributing: `False`
- Source: `cmd_parse.c:666`
- Eligible: `False`
- Evidence:
  - production reachability is a graph traversal from linked executable entry symbols
  - observable output is inferred from output file calls and codec boundary dataflow shape
  - direct effects: {"allocation": false, "assertion": false, "indirect_call": false, "io": false, "logging": true, "state_write": true, "unknown_facts": []}
  - transitive effects: {"allocation": false, "assertion": false, "indirect_call": false, "io": true, "logging": true, "state_write": true, "unknown_facts": []}
  - at least one reachable loop has UNKNOWN bounds

### 139. `str2ullvect`

- Score: `29.85`; confidence: `0.55`; role: `HOST_IO`
- Purity: `IMPURE`; timing: `UNKNOWN`; bounded: `False`
- Production reachable: `True`; output contributing: `False`
- Source: `cmd_parse.c:742`
- Eligible: `False`
- Evidence:
  - production reachability is a graph traversal from linked executable entry symbols
  - observable output is inferred from output file calls and codec boundary dataflow shape
  - direct effects: {"allocation": false, "assertion": false, "indirect_call": false, "io": false, "logging": true, "state_write": true, "unknown_facts": []}
  - transitive effects: {"allocation": false, "assertion": false, "indirect_call": false, "io": true, "logging": true, "state_write": true, "unknown_facts": []}
  - at least one reachable loop has UNKNOWN bounds

### 140. `str2ulvect`

- Score: `29.85`; confidence: `0.55`; role: `HOST_IO`
- Purity: `IMPURE`; timing: `UNKNOWN`; bounded: `False`
- Production reachable: `True`; output contributing: `False`
- Source: `cmd_parse.c:704`
- Eligible: `False`
- Evidence:
  - production reachability is a graph traversal from linked executable entry symbols
  - observable output is inferred from output file calls and codec boundary dataflow shape
  - direct effects: {"allocation": false, "assertion": false, "indirect_call": false, "io": false, "logging": true, "state_write": true, "unknown_facts": []}
  - transitive effects: {"allocation": false, "assertion": false, "indirect_call": false, "io": true, "logging": true, "state_write": true, "unknown_facts": []}
  - at least one reachable loop has UNKNOWN bounds

### 141. `write_dsc_data`

- Score: `29.85`; confidence: `0.55`; role: `HOST_IO`
- Purity: `IMPURE`; timing: `UNKNOWN`; bounded: `False`
- Production reachable: `True`; output contributing: `False`
- Source: `codec_main.c:521`
- Eligible: `False`
- Evidence:
  - production reachability is a graph traversal from linked executable entry symbols
  - observable output is inferred from output file calls and codec boundary dataflow shape
  - direct effects: {"allocation": true, "assertion": false, "indirect_call": false, "io": false, "logging": false, "state_write": false, "unknown_facts": []}
  - transitive effects: {"allocation": true, "assertion": false, "indirect_call": false, "io": false, "logging": false, "state_write": false, "unknown_facts": []}
  - at least one reachable loop has UNKNOWN bounds

### 142. `yuv2rgb`

- Score: `29.85`; confidence: `0.55`; role: `HOST_IO`
- Purity: `IMPURE`; timing: `UNKNOWN`; bounded: `False`
- Production reachable: `True`; output contributing: `False`
- Source: `utl.c:389`
- Eligible: `False`
- Evidence:
  - production reachability is a graph traversal from linked executable entry symbols
  - observable output is inferred from output file calls and codec boundary dataflow shape
  - direct effects: {"allocation": false, "assertion": false, "indirect_call": false, "io": true, "logging": false, "state_write": true, "unknown_facts": []}
  - transitive effects: {"allocation": false, "assertion": false, "indirect_call": false, "io": true, "logging": false, "state_write": true, "unknown_facts": []}
  - at least one reachable loop has UNKNOWN bounds

### 143. `compute_and_display_PSNR`

- Score: `29.8`; confidence: `0.55`; role: `HOST_IO`
- Purity: `IMPURE`; timing: `UNKNOWN`; bounded: `False`
- Production reachable: `True`; output contributing: `False`
- Source: `psnr.c:66`
- Eligible: `False`
- Evidence:
  - production reachability is a graph traversal from linked executable entry symbols
  - observable output is inferred from output file calls and codec boundary dataflow shape
  - direct effects: {"allocation": false, "assertion": false, "indirect_call": false, "io": true, "logging": true, "state_write": false, "unknown_facts": []}
  - transitive effects: {"allocation": false, "assertion": false, "indirect_call": false, "io": true, "logging": true, "state_write": false, "unknown_facts": []}
  - at least one reachable loop has UNKNOWN bounds

### 144. `compute_rc_parameters`

- Score: `29.8`; confidence: `0.55`; role: `CONFIG`
- Purity: `IMPURE`; timing: `UNKNOWN`; bounded: `False`
- Production reachable: `True`; output contributing: `False`
- Source: `codec_main.c:661`
- Eligible: `False`
- Evidence:
  - production reachability is a graph traversal from linked executable entry symbols
  - observable output is inferred from output file calls and codec boundary dataflow shape
  - direct effects: {"allocation": false, "assertion": false, "indirect_call": false, "io": false, "logging": true, "state_write": true, "unknown_facts": []}
  - transitive effects: {"allocation": false, "assertion": false, "indirect_call": false, "io": true, "logging": true, "state_write": true, "unknown_facts": []}
  - at least one reachable loop has UNKNOWN bounds

### 145. `determine_field_format`

- Score: `29.8`; confidence: `0.55`; role: `HOST_IO`
- Purity: `IMPURE`; timing: `UNKNOWN`; bounded: `False`
- Production reachable: `True`; output contributing: `False`
- Source: `dpx.c:67`
- Eligible: `False`
- Evidence:
  - production reachability is a graph traversal from linked executable entry symbols
  - observable output is inferred from output file calls and codec boundary dataflow shape
  - direct effects: {"allocation": true, "assertion": false, "indirect_call": false, "io": false, "logging": false, "state_write": false, "unknown_facts": []}
  - transitive effects: {"allocation": true, "assertion": false, "indirect_call": false, "io": false, "logging": false, "state_write": false, "unknown_facts": []}
  - at least one reachable loop has UNKNOWN bounds

### 146. `hdr_dpx_pic_to_datum_list`

- Score: `29.8`; confidence: `0.55`; role: `HOST_IO`
- Purity: `IMPURE`; timing: `UNKNOWN`; bounded: `False`
- Production reachable: `True`; output contributing: `False`
- Source: `hdr_dpx.c:1077`
- Eligible: `False`
- Evidence:
  - production reachability is a graph traversal from linked executable entry symbols
  - observable output is inferred from output file calls and codec boundary dataflow shape
  - direct effects: {"allocation": true, "assertion": false, "indirect_call": false, "io": true, "logging": false, "state_write": true, "unknown_facts": []}
  - transitive effects: {"allocation": true, "assertion": false, "indirect_call": false, "io": true, "logging": false, "state_write": true, "unknown_facts": []}
  - at least one reachable loop has UNKNOWN bounds

### 147. `pcreate_ext`

- Score: `29.8`; confidence: `0.55`; role: `CHECKER`
- Purity: `IMPURE`; timing: `UNKNOWN`; bounded: `False`
- Production reachable: `True`; output contributing: `False`
- Source: `utl.c:144`
- Eligible: `False`
- Evidence:
  - production reachability is a graph traversal from linked executable entry symbols
  - observable output is inferred from output file calls and codec boundary dataflow shape
  - direct effects: {"allocation": true, "assertion": false, "indirect_call": false, "io": true, "logging": false, "state_write": true, "unknown_facts": []}
  - transitive effects: {"allocation": true, "assertion": true, "indirect_call": false, "io": true, "logging": false, "state_write": true, "unknown_facts": []}
  - at least one reachable loop has UNKNOWN bounds

### 148. `yuv_422_420`

- Score: `29.8`; confidence: `0.55`; role: `HOST_IO`
- Purity: `IMPURE`; timing: `UNKNOWN`; bounded: `False`
- Production reachable: `True`; output contributing: `False`
- Source: `utl.c:615`
- Eligible: `False`
- Evidence:
  - production reachability is a graph traversal from linked executable entry symbols
  - observable output is inferred from output file calls and codec boundary dataflow shape
  - direct effects: {"allocation": false, "assertion": false, "indirect_call": false, "io": false, "logging": true, "state_write": true, "unknown_facts": []}
  - transitive effects: {"allocation": false, "assertion": false, "indirect_call": false, "io": false, "logging": true, "state_write": true, "unknown_facts": []}
  - at least one reachable loop has UNKNOWN bounds

### 149. `yuv_444_422`

- Score: `29.8`; confidence: `0.55`; role: `HOST_IO`
- Purity: `IMPURE`; timing: `UNKNOWN`; bounded: `False`
- Production reachable: `True`; output contributing: `False`
- Source: `utl.c:533`
- Eligible: `False`
- Evidence:
  - production reachability is a graph traversal from linked executable entry symbols
  - observable output is inferred from output file calls and codec boundary dataflow shape
  - direct effects: {"allocation": false, "assertion": false, "indirect_call": false, "io": false, "logging": true, "state_write": true, "unknown_facts": []}
  - transitive effects: {"allocation": false, "assertion": false, "indirect_call": false, "io": false, "logging": true, "state_write": true, "unknown_facts": []}
  - at least one reachable loop has UNKNOWN bounds

### 150. `convertbits`

- Score: `29.75`; confidence: `0.55`; role: `CHECKER`
- Purity: `IMPURE`; timing: `UNKNOWN`; bounded: `False`
- Production reachable: `True`; output contributing: `False`
- Source: `utl.c:710`
- Eligible: `False`
- Evidence:
  - production reachability is a graph traversal from linked executable entry symbols
  - observable output is inferred from output file calls and codec boundary dataflow shape
  - direct effects: {"allocation": false, "assertion": false, "indirect_call": false, "io": true, "logging": true, "state_write": true, "unknown_facts": []}
  - transitive effects: {"allocation": true, "assertion": true, "indirect_call": false, "io": true, "logging": true, "state_write": true, "unknown_facts": []}
  - at least one reachable loop has UNKNOWN bounds

### 151. `hdr_dpx_fill_core_fields`

- Score: `29.75`; confidence: `0.55`; role: `HOST_IO`
- Purity: `IMPURE`; timing: `UNKNOWN`; bounded: `False`
- Production reachable: `True`; output contributing: `False`
- Source: `hdr_dpx.c:1551`
- Eligible: `False`
- Evidence:
  - production reachability is a graph traversal from linked executable entry symbols
  - observable output is inferred from output file calls and codec boundary dataflow shape
  - direct effects: {"allocation": false, "assertion": false, "indirect_call": false, "io": true, "logging": true, "state_write": true, "unknown_facts": []}
  - transitive effects: {"allocation": false, "assertion": false, "indirect_call": false, "io": true, "logging": true, "state_write": true, "unknown_facts": []}
  - at least one reachable loop has UNKNOWN bounds

### 152. `hdr_dpx_rle_encode`

- Score: `29.75`; confidence: `0.55`; role: `HOST_IO`
- Purity: `IMPURE`; timing: `UNKNOWN`; bounded: `False`
- Production reachable: `True`; output contributing: `False`
- Source: `hdr_dpx.c:80`
- Eligible: `False`
- Evidence:
  - production reachability is a graph traversal from linked executable entry symbols
  - observable output is inferred from output file calls and codec boundary dataflow shape
  - direct effects: {"allocation": true, "assertion": false, "indirect_call": false, "io": true, "logging": false, "state_write": true, "unknown_facts": []}
  - transitive effects: {"allocation": true, "assertion": false, "indirect_call": false, "io": true, "logging": false, "state_write": true, "unknown_facts": []}
  - at least one reachable loop has UNKNOWN bounds

### 153. `palloc`

- Score: `29.75`; confidence: `0.55`; role: `CHECKER`
- Purity: `IMPURE`; timing: `UNKNOWN`; bounded: `False`
- Production reachable: `True`; output contributing: `False`
- Source: `utl.c:55`
- Eligible: `False`
- Evidence:
  - production reachability is a graph traversal from linked executable entry symbols
  - observable output is inferred from output file calls and codec boundary dataflow shape
  - direct effects: {"allocation": true, "assertion": true, "indirect_call": false, "io": true, "logging": false, "state_write": false, "unknown_facts": []}
  - transitive effects: {"allocation": true, "assertion": true, "indirect_call": false, "io": true, "logging": false, "state_write": false, "unknown_facts": []}
  - at least one reachable loop has UNKNOWN bounds

### 154. `populate_pps`

- Score: `29.75`; confidence: `0.55`; role: `CONFIG`
- Purity: `IMPURE`; timing: `UNKNOWN`; bounded: `False`
- Production reachable: `True`; output contributing: `False`
- Source: `codec_main.c:1047`
- Eligible: `False`
- Evidence:
  - production reachability is a graph traversal from linked executable entry symbols
  - observable output is inferred from output file calls and codec boundary dataflow shape
  - direct effects: {"allocation": false, "assertion": false, "indirect_call": false, "io": false, "logging": true, "state_write": true, "unknown_facts": []}
  - transitive effects: {"allocation": true, "assertion": false, "indirect_call": false, "io": true, "logging": true, "state_write": true, "unknown_facts": []}
  - at least one reachable loop has UNKNOWN bounds

### 155. `print_pps_v2`

- Score: `29.75`; confidence: `0.55`; role: `CONFIG`
- Purity: `IMPURE`; timing: `UNKNOWN`; bounded: `False`
- Production reachable: `True`; output contributing: `False`
- Source: `dsc_utils.c:694`
- Eligible: `False`
- Evidence:
  - production reachability is a graph traversal from linked executable entry symbols
  - observable output is inferred from output file calls and codec boundary dataflow shape
  - direct effects: {"allocation": false, "assertion": false, "indirect_call": false, "io": true, "logging": true, "state_write": false, "unknown_facts": []}
  - transitive effects: {"allocation": false, "assertion": false, "indirect_call": false, "io": true, "logging": true, "state_write": true, "unknown_facts": []}
  - at least one reachable loop has UNKNOWN bounds

### 156. `split_base_and_ext`

- Score: `29.75`; confidence: `0.55`; role: `HOST_IO`
- Purity: `IMPURE`; timing: `UNKNOWN`; bounded: `False`
- Production reachable: `True`; output contributing: `False`
- Source: `codec_main.c:481`
- Eligible: `False`
- Evidence:
  - production reachability is a graph traversal from linked executable entry symbols
  - observable output is inferred from output file calls and codec boundary dataflow shape
  - direct effects: {"allocation": false, "assertion": false, "indirect_call": false, "io": false, "logging": true, "state_write": true, "unknown_facts": []}
  - transitive effects: {"allocation": false, "assertion": false, "indirect_call": false, "io": false, "logging": true, "state_write": true, "unknown_facts": []}
  - at least one reachable loop has UNKNOWN bounds

### 157. `parse_line`

- Score: `29.7`; confidence: `0.55`; role: `CHECKER`
- Purity: `IMPURE`; timing: `UNKNOWN`; bounded: `False`
- Production reachable: `True`; output contributing: `False`
- Source: `cmd_parse.c:1219`
- Eligible: `False`
- Evidence:
  - production reachability is a graph traversal from linked executable entry symbols
  - observable output is inferred from output file calls and codec boundary dataflow shape
  - direct effects: {"allocation": false, "assertion": true, "indirect_call": false, "io": false, "logging": false, "state_write": false, "unknown_facts": []}
  - transitive effects: {"allocation": false, "assertion": true, "indirect_call": false, "io": true, "logging": true, "state_write": true, "unknown_facts": []}
  - at least one reachable loop has UNKNOWN bounds

### 158. `yuv_write`

- Score: `29.7`; confidence: `0.55`; role: `HOST_IO`
- Purity: `IMPURE`; timing: `UNKNOWN`; bounded: `False`
- Production reachable: `True`; output contributing: `False`
- Source: `utl.c:1450`
- Eligible: `False`
- Evidence:
  - production reachability is a graph traversal from linked executable entry symbols
  - observable output is inferred from output file calls and codec boundary dataflow shape
  - direct effects: {"allocation": false, "assertion": false, "indirect_call": false, "io": true, "logging": true, "state_write": false, "unknown_facts": []}
  - transitive effects: {"allocation": false, "assertion": false, "indirect_call": false, "io": true, "logging": true, "state_write": false, "unknown_facts": []}
  - at least one reachable loop has UNKNOWN bounds

### 159. `parse_cfgfile`

- Score: `29.65`; confidence: `0.55`; role: `CHECKER`
- Purity: `IMPURE`; timing: `UNKNOWN`; bounded: `False`
- Production reachable: `True`; output contributing: `False`
- Source: `codec_main.c:314`
- Eligible: `False`
- Evidence:
  - production reachability is a graph traversal from linked executable entry symbols
  - observable output is inferred from output file calls and codec boundary dataflow shape
  - direct effects: {"allocation": false, "assertion": false, "indirect_call": false, "io": true, "logging": false, "state_write": false, "unknown_facts": []}
  - transitive effects: {"allocation": false, "assertion": true, "indirect_call": false, "io": true, "logging": true, "state_write": true, "unknown_facts": []}
  - at least one reachable loop has UNKNOWN bounds

### 160. `process_args`

- Score: `29.65`; confidence: `0.55`; role: `CHECKER`
- Purity: `IMPURE`; timing: `UNKNOWN`; bounded: `False`
- Production reachable: `True`; output contributing: `False`
- Source: `codec_main.c:402`
- Eligible: `False`
- Evidence:
  - production reachability is a graph traversal from linked executable entry symbols
  - observable output is inferred from output file calls and codec boundary dataflow shape
  - direct effects: {"allocation": false, "assertion": false, "indirect_call": false, "io": true, "logging": false, "state_write": true, "unknown_facts": []}
  - transitive effects: {"allocation": true, "assertion": true, "indirect_call": false, "io": true, "logging": true, "state_write": true, "unknown_facts": []}
  - at least one reachable loop has UNKNOWN bounds

### 161. `read_dpx_image_data`

- Score: `29.65`; confidence: `0.55`; role: `CHECKER`
- Purity: `IMPURE`; timing: `UNKNOWN`; bounded: `False`
- Production reachable: `True`; output contributing: `False`
- Source: `dpx.c:981`
- Eligible: `False`
- Evidence:
  - production reachability is a graph traversal from linked executable entry symbols
  - observable output is inferred from output file calls and codec boundary dataflow shape
  - direct effects: {"allocation": false, "assertion": false, "indirect_call": false, "io": true, "logging": false, "state_write": true, "unknown_facts": []}
  - transitive effects: {"allocation": true, "assertion": true, "indirect_call": false, "io": true, "logging": true, "state_write": true, "unknown_facts": []}
  - at least one reachable loop has UNKNOWN bounds

### 162. `yuv_read`

- Score: `29.6`; confidence: `0.55`; role: `CHECKER`
- Purity: `IMPURE`; timing: `UNKNOWN`; bounded: `False`
- Production reachable: `True`; output contributing: `False`
- Source: `utl.c:1335`
- Eligible: `False`
- Evidence:
  - production reachability is a graph traversal from linked executable entry symbols
  - observable output is inferred from output file calls and codec boundary dataflow shape
  - direct effects: {"allocation": false, "assertion": false, "indirect_call": false, "io": true, "logging": true, "state_write": true, "unknown_facts": []}
  - transitive effects: {"allocation": true, "assertion": true, "indirect_call": false, "io": true, "logging": true, "state_write": true, "unknown_facts": []}
  - at least one reachable loop has UNKNOWN bounds

### 163. `parse_cmd`

- Score: `29.55`; confidence: `0.55`; role: `CHECKER`
- Purity: `IMPURE`; timing: `UNKNOWN`; bounded: `False`
- Production reachable: `True`; output contributing: `False`
- Source: `cmd_parse.c:1255`
- Eligible: `False`
- Evidence:
  - production reachability is a graph traversal from linked executable entry symbols
  - observable output is inferred from output file calls and codec boundary dataflow shape
  - direct effects: {"allocation": true, "assertion": true, "indirect_call": false, "io": false, "logging": false, "state_write": false, "unknown_facts": []}
  - transitive effects: {"allocation": true, "assertion": true, "indirect_call": false, "io": true, "logging": true, "state_write": true, "unknown_facts": []}
  - at least one reachable loop has UNKNOWN bounds

### 164. `ppm_write`

- Score: `29.55`; confidence: `0.55`; role: `CHECKER`
- Purity: `IMPURE`; timing: `UNKNOWN`; bounded: `False`
- Production reachable: `True`; output contributing: `False`
- Source: `utl.c:1246`
- Eligible: `False`
- Evidence:
  - production reachability is a graph traversal from linked executable entry symbols
  - observable output is inferred from output file calls and codec boundary dataflow shape
  - direct effects: {"allocation": false, "assertion": false, "indirect_call": false, "io": true, "logging": false, "state_write": true, "unknown_facts": []}
  - transitive effects: {"allocation": true, "assertion": true, "indirect_call": false, "io": true, "logging": true, "state_write": true, "unknown_facts": []}
  - at least one reachable loop has UNKNOWN bounds

### 165. `readppm`

- Score: `29.45`; confidence: `0.55`; role: `CHECKER`
- Purity: `IMPURE`; timing: `UNKNOWN`; bounded: `False`
- Production reachable: `True`; output contributing: `False`
- Source: `utl.c:1068`
- Eligible: `False`
- Evidence:
  - production reachability is a graph traversal from linked executable entry symbols
  - observable output is inferred from output file calls and codec boundary dataflow shape
  - direct effects: {"allocation": false, "assertion": false, "indirect_call": false, "io": false, "logging": true, "state_write": true, "unknown_facts": []}
  - transitive effects: {"allocation": true, "assertion": true, "indirect_call": false, "io": true, "logging": true, "state_write": true, "unknown_facts": []}
  - at least one reachable loop has UNKNOWN bounds

### 166. `hdr_dpx_get_pic_data`

- Score: `29.4`; confidence: `0.55`; role: `CHECKER`
- Purity: `IMPURE`; timing: `UNKNOWN`; bounded: `False`
- Production reachable: `True`; output contributing: `False`
- Source: `hdr_dpx.c:1172`
- Eligible: `False`
- Evidence:
  - production reachability is a graph traversal from linked executable entry symbols
  - observable output is inferred from output file calls and codec boundary dataflow shape
  - direct effects: {"allocation": false, "assertion": false, "indirect_call": false, "io": true, "logging": true, "state_write": false, "unknown_facts": []}
  - transitive effects: {"allocation": true, "assertion": true, "indirect_call": false, "io": true, "logging": true, "state_write": true, "unknown_facts": []}
  - at least one reachable loop has UNKNOWN bounds

### 167. `hdr_dpx_read`

- Score: `29.35`; confidence: `0.55`; role: `CHECKER`
- Purity: `IMPURE`; timing: `UNKNOWN`; bounded: `False`
- Production reachable: `True`; output contributing: `False`
- Source: `hdr_dpx.c:1966`
- Eligible: `False`
- Evidence:
  - production reachability is a graph traversal from linked executable entry symbols
  - observable output is inferred from output file calls and codec boundary dataflow shape
  - direct effects: {"allocation": true, "assertion": false, "indirect_call": false, "io": true, "logging": true, "state_write": true, "unknown_facts": []}
  - transitive effects: {"allocation": true, "assertion": true, "indirect_call": false, "io": true, "logging": true, "state_write": true, "unknown_facts": []}
  - at least one reachable loop has UNKNOWN bounds

### 168. `dpx_read_hl`

- Score: `29.25`; confidence: `0.55`; role: `CHECKER`
- Purity: `IMPURE`; timing: `UNKNOWN`; bounded: `False`
- Production reachable: `True`; output contributing: `False`
- Source: `dpx.c:750`
- Eligible: `False`
- Evidence:
  - production reachability is a graph traversal from linked executable entry symbols
  - observable output is inferred from output file calls and codec boundary dataflow shape
  - direct effects: {"allocation": false, "assertion": false, "indirect_call": false, "io": true, "logging": true, "state_write": true, "unknown_facts": []}
  - transitive effects: {"allocation": true, "assertion": true, "indirect_call": false, "io": true, "logging": true, "state_write": true, "unknown_facts": []}
  - at least one reachable loop has UNKNOWN bounds

### 169. `assign_val`

- Score: `29.0`; confidence: `0.55`; role: `CHECKER`
- Purity: `IMPURE`; timing: `UNKNOWN`; bounded: `False`
- Production reachable: `True`; output contributing: `False`
- Source: `cmd_parse.c:799`
- Eligible: `False`
- Evidence:
  - production reachability is a graph traversal from linked executable entry symbols
  - observable output is inferred from output file calls and codec boundary dataflow shape
  - direct effects: {"allocation": false, "assertion": true, "indirect_call": false, "io": false, "logging": true, "state_write": false, "unknown_facts": []}
  - transitive effects: {"allocation": false, "assertion": true, "indirect_call": false, "io": true, "logging": true, "state_write": true, "unknown_facts": []}
  - at least one reachable loop has UNKNOWN bounds

### 170. `change_ext`

- Score: `19.9`; confidence: `0.55`; role: `UNRESOLVED`
- Purity: `PURE`; timing: `UNKNOWN`; bounded: `False`
- Production reachable: `False`; output contributing: `False`
- Source: `cmd_parse.c:376`
- Eligible: `False`
- Evidence:
  - production reachability is a graph traversal from linked executable entry symbols
  - observable output is inferred from output file calls and codec boundary dataflow shape
  - direct effects: {"allocation": false, "assertion": false, "indirect_call": false, "io": false, "logging": false, "state_write": false, "unknown_facts": []}
  - transitive effects: {"allocation": false, "assertion": false, "indirect_call": false, "io": false, "logging": false, "state_write": false, "unknown_facts": []}
  - at least one reachable loop has UNKNOWN bounds

### 171. `strisdim`

- Score: `19.9`; confidence: `0.55`; role: `UNRESOLVED`
- Purity: `PURE`; timing: `UNKNOWN`; bounded: `False`
- Production reachable: `False`; output contributing: `False`
- Source: `cmd_parse.c:333`
- Eligible: `False`
- Evidence:
  - production reachability is a graph traversal from linked executable entry symbols
  - observable output is inferred from output file calls and codec boundary dataflow shape
  - direct effects: {"allocation": false, "assertion": false, "indirect_call": false, "io": false, "logging": false, "state_write": false, "unknown_facts": []}
  - transitive effects: {"allocation": false, "assertion": false, "indirect_call": false, "io": false, "logging": false, "state_write": false, "unknown_facts": []}
  - at least one reachable loop has UNKNOWN bounds

### 172. `strisnum`

- Score: `19.9`; confidence: `0.55`; role: `UNRESOLVED`
- Purity: `PURE`; timing: `UNKNOWN`; bounded: `False`
- Production reachable: `False`; output contributing: `False`
- Source: `cmd_parse.c:273`
- Eligible: `False`
- Evidence:
  - production reachability is a graph traversal from linked executable entry symbols
  - observable output is inferred from output file calls and codec boundary dataflow shape
  - direct effects: {"allocation": false, "assertion": false, "indirect_call": false, "io": false, "logging": false, "state_write": false, "unknown_facts": []}
  - transitive effects: {"allocation": false, "assertion": false, "indirect_call": false, "io": false, "logging": false, "state_write": false, "unknown_facts": []}
  - at least one reachable loop has UNKNOWN bounds

### 173. `strisrange`

- Score: `19.9`; confidence: `0.55`; role: `UNRESOLVED`
- Purity: `PURE`; timing: `UNKNOWN`; bounded: `False`
- Production reachable: `False`; output contributing: `False`
- Source: `cmd_parse.c:297`
- Eligible: `False`
- Evidence:
  - production reachability is a graph traversal from linked executable entry symbols
  - observable output is inferred from output file calls and codec boundary dataflow shape
  - direct effects: {"allocation": false, "assertion": false, "indirect_call": false, "io": false, "logging": false, "state_write": false, "unknown_facts": []}
  - transitive effects: {"allocation": false, "assertion": false, "indirect_call": false, "io": false, "logging": false, "state_write": false, "unknown_facts": []}
  - at least one reachable loop has UNKNOWN bounds

### 174. `chop_dir`

- Score: `19.75`; confidence: `0.55`; role: `HOST_IO`
- Purity: `IMPURE`; timing: `COMBINATIONAL`; bounded: `True`
- Production reachable: `False`; output contributing: `False`
- Source: `cmd_parse.c:132`
- Eligible: `False`
- Evidence:
  - production reachability is a graph traversal from linked executable entry symbols
  - observable output is inferred from output file calls and codec boundary dataflow shape
  - direct effects: {"allocation": true, "assertion": false, "indirect_call": false, "io": false, "logging": false, "state_write": false, "unknown_facts": []}
  - transitive effects: {"allocation": true, "assertion": false, "indirect_call": false, "io": false, "logging": false, "state_write": false, "unknown_facts": []}
  - all reachable loops have fixed AST bounds

### 175. `file_ext`

- Score: `19.75`; confidence: `0.55`; role: `HOST_IO`
- Purity: `IMPURE`; timing: `COMBINATIONAL`; bounded: `True`
- Production reachable: `False`; output contributing: `False`
- Source: `cmd_parse.c:161`
- Eligible: `False`
- Evidence:
  - production reachability is a graph traversal from linked executable entry symbols
  - observable output is inferred from output file calls and codec boundary dataflow shape
  - direct effects: {"allocation": true, "assertion": false, "indirect_call": false, "io": false, "logging": false, "state_write": false, "unknown_facts": []}
  - transitive effects: {"allocation": true, "assertion": false, "indirect_call": false, "io": false, "logging": false, "state_write": false, "unknown_facts": []}
  - all reachable loops have fixed AST bounds

### 176. `file_dir`

- Score: `19.7`; confidence: `0.55`; role: `HOST_IO`
- Purity: `IMPURE`; timing: `COMBINATIONAL`; bounded: `True`
- Production reachable: `False`; output contributing: `False`
- Source: `cmd_parse.c:189`
- Eligible: `False`
- Evidence:
  - production reachability is a graph traversal from linked executable entry symbols
  - observable output is inferred from output file calls and codec boundary dataflow shape
  - direct effects: {"allocation": true, "assertion": false, "indirect_call": false, "io": false, "logging": false, "state_write": false, "unknown_facts": []}
  - transitive effects: {"allocation": true, "assertion": false, "indirect_call": false, "io": false, "logging": false, "state_write": false, "unknown_facts": []}
  - all reachable loops have fixed AST bounds

### 177. `easy_mkdir`

- Score: `19.55`; confidence: `0.55`; role: `HOST_IO`
- Purity: `IMPURE`; timing: `COMBINATIONAL`; bounded: `True`
- Production reachable: `False`; output contributing: `False`
- Source: `cmd_parse.c:220`
- Eligible: `False`
- Evidence:
  - production reachability is a graph traversal from linked executable entry symbols
  - observable output is inferred from output file calls and codec boundary dataflow shape
  - direct effects: {"allocation": true, "assertion": false, "indirect_call": false, "io": false, "logging": false, "state_write": false, "unknown_facts": []}
  - transitive effects: {"allocation": true, "assertion": false, "indirect_call": false, "io": true, "logging": true, "state_write": false, "unknown_facts": []}
  - all reachable loops have fixed AST bounds

### 178. `set_dpx_colorspace`

- Score: `5.0`; confidence: `0.55`; role: `UNRESOLVED`
- Purity: `IMPURE`; timing: `STATEFUL`; bounded: `True`
- Production reachable: `False`; output contributing: `False`
- Source: `dpx.c:1474`
- Eligible: `False`
- Evidence:
  - production reachability is a graph traversal from linked executable entry symbols
  - observable output is inferred from output file calls and codec boundary dataflow shape
  - direct effects: {"allocation": false, "assertion": false, "indirect_call": false, "io": false, "logging": false, "state_write": true, "unknown_facts": []}
  - transitive effects: {"allocation": false, "assertion": false, "indirect_call": false, "io": false, "logging": false, "state_write": true, "unknown_facts": []}
  - all reachable loops have fixed AST bounds

### 179. `merge_cmd_args`

- Score: `-0.05`; confidence: `0.55`; role: `HOST_IO`
- Purity: `IMPURE`; timing: `UNKNOWN`; bounded: `False`
- Production reachable: `False`; output contributing: `False`
- Source: `cmd_parse.c:1180`
- Eligible: `False`
- Evidence:
  - production reachability is a graph traversal from linked executable entry symbols
  - observable output is inferred from output file calls and codec boundary dataflow shape
  - direct effects: {"allocation": true, "assertion": false, "indirect_call": false, "io": false, "logging": false, "state_write": true, "unknown_facts": []}
  - transitive effects: {"allocation": true, "assertion": false, "indirect_call": false, "io": false, "logging": false, "state_write": true, "unknown_facts": []}
  - at least one reachable loop has UNKNOWN bounds

### 180. `read_dpx`

- Score: `-0.05`; confidence: `0.55`; role: `CHECKER`
- Purity: `IMPURE`; timing: `UNKNOWN`; bounded: `False`
- Production reachable: `False`; output contributing: `False`
- Source: `dpx.c:727`
- Eligible: `False`
- Evidence:
  - production reachability is a graph traversal from linked executable entry symbols
  - observable output is inferred from output file calls and codec boundary dataflow shape
  - direct effects: {"allocation": false, "assertion": false, "indirect_call": false, "io": false, "logging": false, "state_write": true, "unknown_facts": []}
  - transitive effects: {"allocation": true, "assertion": true, "indirect_call": false, "io": true, "logging": true, "state_write": true, "unknown_facts": []}
  - at least one reachable loop has UNKNOWN bounds

### 181. `write_dpx`

- Score: `-0.05`; confidence: `0.55`; role: `HOST_IO`
- Purity: `IMPURE`; timing: `UNKNOWN`; bounded: `False`
- Production reachable: `False`; output contributing: `False`
- Source: `dpx.c:230`
- Eligible: `False`
- Evidence:
  - production reachability is a graph traversal from linked executable entry symbols
  - observable output is inferred from output file calls and codec boundary dataflow shape
  - direct effects: {"allocation": false, "assertion": false, "indirect_call": false, "io": false, "logging": false, "state_write": false, "unknown_facts": []}
  - transitive effects: {"allocation": true, "assertion": false, "indirect_call": false, "io": true, "logging": true, "state_write": true, "unknown_facts": []}
  - at least one reachable loop has UNKNOWN bounds

### 182. `pcopy`

- Score: `-0.1`; confidence: `0.55`; role: `CHECKER`
- Purity: `IMPURE`; timing: `UNKNOWN`; bounded: `False`
- Production reachable: `False`; output contributing: `False`
- Source: `utl.c:1520`
- Eligible: `False`
- Evidence:
  - production reachability is a graph traversal from linked executable entry symbols
  - observable output is inferred from output file calls and codec boundary dataflow shape
  - direct effects: {"allocation": false, "assertion": false, "indirect_call": false, "io": false, "logging": false, "state_write": true, "unknown_facts": []}
  - transitive effects: {"allocation": true, "assertion": true, "indirect_call": false, "io": true, "logging": false, "state_write": true, "unknown_facts": []}
  - at least one reachable loop has UNKNOWN bounds

### 183. `retrieve_cmds_var`

- Score: `-0.1`; confidence: `0.55`; role: `CHECKER`
- Purity: `IMPURE`; timing: `UNKNOWN`; bounded: `False`
- Production reachable: `False`; output contributing: `False`
- Source: `cmd_parse.c:1521`
- Eligible: `False`
- Evidence:
  - production reachability is a graph traversal from linked executable entry symbols
  - observable output is inferred from output file calls and codec boundary dataflow shape
  - direct effects: {"allocation": false, "assertion": true, "indirect_call": false, "io": false, "logging": false, "state_write": false, "unknown_facts": []}
  - transitive effects: {"allocation": false, "assertion": true, "indirect_call": false, "io": true, "logging": false, "state_write": false, "unknown_facts": []}
  - at least one reachable loop has UNKNOWN bounds

### 184. `retrieve_keys_var`

- Score: `-0.1`; confidence: `0.55`; role: `CHECKER`
- Purity: `IMPURE`; timing: `UNKNOWN`; bounded: `False`
- Production reachable: `False`; output contributing: `False`
- Source: `cmd_parse.c:1508`
- Eligible: `False`
- Evidence:
  - production reachability is a graph traversal from linked executable entry symbols
  - observable output is inferred from output file calls and codec boundary dataflow shape
  - direct effects: {"allocation": false, "assertion": true, "indirect_call": false, "io": false, "logging": false, "state_write": false, "unknown_facts": []}
  - transitive effects: {"allocation": false, "assertion": true, "indirect_call": false, "io": true, "logging": false, "state_write": false, "unknown_facts": []}
  - at least one reachable loop has UNKNOWN bounds

### 185. `WriteEntryToBitstream`

- Score: `-0.15`; confidence: `0.55`; role: `HOST_IO`
- Purity: `IMPURE`; timing: `UNKNOWN`; bounded: `False`
- Production reachable: `False`; output contributing: `False`
- Source: `multiplex.c:60`
- Eligible: `False`
- Evidence:
  - production reachability is a graph traversal from linked executable entry symbols
  - observable output is inferred from output file calls and codec boundary dataflow shape
  - direct effects: {"allocation": false, "assertion": false, "indirect_call": false, "io": false, "logging": true, "state_write": false, "unknown_facts": []}
  - transitive effects: {"allocation": false, "assertion": false, "indirect_call": false, "io": false, "logging": true, "state_write": true, "unknown_facts": []}
  - at least one reachable loop has UNKNOWN bounds

### 186. `convert_rgb_2020_to_709`

- Score: `-0.15`; confidence: `0.55`; role: `HOST_IO`
- Purity: `IMPURE`; timing: `UNKNOWN`; bounded: `False`
- Production reachable: `False`; output contributing: `False`
- Source: `utl.c:1644`
- Eligible: `False`
- Evidence:
  - production reachability is a graph traversal from linked executable entry symbols
  - observable output is inferred from output file calls and codec boundary dataflow shape
  - direct effects: {"allocation": false, "assertion": false, "indirect_call": false, "io": false, "logging": true, "state_write": true, "unknown_facts": []}
  - transitive effects: {"allocation": false, "assertion": false, "indirect_call": false, "io": true, "logging": true, "state_write": true, "unknown_facts": []}
  - at least one reachable loop has UNKNOWN bounds

### 187. `order_keys`

- Score: `-0.15`; confidence: `0.55`; role: `CHECKER`
- Purity: `IMPURE`; timing: `UNKNOWN`; bounded: `False`
- Production reachable: `False`; output contributing: `False`
- Source: `cmd_parse.c:1012`
- Eligible: `False`
- Evidence:
  - production reachability is a graph traversal from linked executable entry symbols
  - observable output is inferred from output file calls and codec boundary dataflow shape
  - direct effects: {"allocation": true, "assertion": true, "indirect_call": false, "io": false, "logging": false, "state_write": false, "unknown_facts": []}
  - transitive effects: {"allocation": true, "assertion": true, "indirect_call": false, "io": true, "logging": false, "state_write": false, "unknown_facts": []}
  - at least one reachable loop has UNKNOWN bounds

### 188. `fifo_clone`

- Score: `-0.2`; confidence: `0.55`; role: `HOST_IO`
- Purity: `IMPURE`; timing: `UNKNOWN`; bounded: `False`
- Production reachable: `False`; output contributing: `False`
- Source: `fifo.c:146`
- Eligible: `False`
- Evidence:
  - production reachability is a graph traversal from linked executable entry symbols
  - observable output is inferred from output file calls and codec boundary dataflow shape
  - direct effects: {"allocation": false, "assertion": false, "indirect_call": false, "io": false, "logging": false, "state_write": false, "unknown_facts": []}
  - transitive effects: {"allocation": true, "assertion": false, "indirect_call": false, "io": false, "logging": true, "state_write": true, "unknown_facts": []}
  - at least one reachable loop has UNKNOWN bounds

### 189. `parse_cmd_strict`

- Score: `-0.2`; confidence: `0.55`; role: `CHECKER`
- Purity: `IMPURE`; timing: `UNKNOWN`; bounded: `False`
- Production reachable: `False`; output contributing: `False`
- Source: `cmd_parse.c:1307`
- Eligible: `False`
- Evidence:
  - production reachability is a graph traversal from linked executable entry symbols
  - observable output is inferred from output file calls and codec boundary dataflow shape
  - direct effects: {"allocation": false, "assertion": false, "indirect_call": false, "io": false, "logging": true, "state_write": false, "unknown_facts": []}
  - transitive effects: {"allocation": true, "assertion": true, "indirect_call": false, "io": true, "logging": true, "state_write": true, "unknown_facts": []}
  - at least one reachable loop has UNKNOWN bounds

### 190. `parse_line_strict`

- Score: `-0.2`; confidence: `0.55`; role: `CHECKER`
- Purity: `IMPURE`; timing: `UNKNOWN`; bounded: `False`
- Production reachable: `False`; output contributing: `False`
- Source: `cmd_parse.c:1318`
- Eligible: `False`
- Evidence:
  - production reachability is a graph traversal from linked executable entry symbols
  - observable output is inferred from output file calls and codec boundary dataflow shape
  - direct effects: {"allocation": false, "assertion": false, "indirect_call": false, "io": false, "logging": true, "state_write": false, "unknown_facts": []}
  - transitive effects: {"allocation": true, "assertion": true, "indirect_call": false, "io": true, "logging": true, "state_write": true, "unknown_facts": []}
  - at least one reachable loop has UNKNOWN bounds

### 191. `pcreate`

- Score: `-0.2`; confidence: `0.55`; role: `CHECKER`
- Purity: `IMPURE`; timing: `UNKNOWN`; bounded: `False`
- Production reachable: `False`; output contributing: `False`
- Source: `utl.c:83`
- Eligible: `False`
- Evidence:
  - production reachability is a graph traversal from linked executable entry symbols
  - observable output is inferred from output file calls and codec boundary dataflow shape
  - direct effects: {"allocation": true, "assertion": false, "indirect_call": false, "io": true, "logging": false, "state_write": true, "unknown_facts": []}
  - transitive effects: {"allocation": true, "assertion": true, "indirect_call": false, "io": true, "logging": false, "state_write": true, "unknown_facts": []}
  - at least one reachable loop has UNKNOWN bounds

### 192. `rgba_read`

- Score: `-0.3`; confidence: `0.55`; role: `CHECKER`
- Purity: `IMPURE`; timing: `UNKNOWN`; bounded: `False`
- Production reachable: `False`; output contributing: `False`
- Source: `utl.c:1592`
- Eligible: `False`
- Evidence:
  - production reachability is a graph traversal from linked executable entry symbols
  - observable output is inferred from output file calls and codec boundary dataflow shape
  - direct effects: {"allocation": false, "assertion": false, "indirect_call": false, "io": true, "logging": true, "state_write": true, "unknown_facts": []}
  - transitive effects: {"allocation": true, "assertion": true, "indirect_call": false, "io": true, "logging": true, "state_write": true, "unknown_facts": []}
  - at least one reachable loop has UNKNOWN bounds

### 193. `parse_cmd_usage`

- Score: `-0.45`; confidence: `0.55`; role: `CHECKER`
- Purity: `IMPURE`; timing: `UNKNOWN`; bounded: `False`
- Production reachable: `False`; output contributing: `False`
- Source: `cmd_parse.c:1427`
- Eligible: `False`
- Evidence:
  - production reachability is a graph traversal from linked executable entry symbols
  - observable output is inferred from output file calls and codec boundary dataflow shape
  - direct effects: {"allocation": true, "assertion": false, "indirect_call": false, "io": false, "logging": true, "state_write": false, "unknown_facts": []}
  - transitive effects: {"allocation": true, "assertion": true, "indirect_call": false, "io": true, "logging": true, "state_write": true, "unknown_facts": []}
  - at least one reachable loop has UNKNOWN bounds

### 194. `parse_key_usage`

- Score: `-0.45`; confidence: `0.55`; role: `CHECKER`
- Purity: `IMPURE`; timing: `UNKNOWN`; bounded: `False`
- Production reachable: `False`; output contributing: `False`
- Source: `cmd_parse.c:1480`
- Eligible: `False`
- Evidence:
  - production reachability is a graph traversal from linked executable entry symbols
  - observable output is inferred from output file calls and codec boundary dataflow shape
  - direct effects: {"allocation": true, "assertion": false, "indirect_call": false, "io": false, "logging": true, "state_write": false, "unknown_facts": []}
  - transitive effects: {"allocation": true, "assertion": true, "indirect_call": false, "io": true, "logging": true, "state_write": false, "unknown_facts": []}
  - at least one reachable loop has UNKNOWN bounds
