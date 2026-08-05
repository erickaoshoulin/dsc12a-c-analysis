# Decode RTL frontier

Generated from decoder-only LLVM coverage, Clang facts, candidate effects, and the stable RTL manifest.
No function-name allowlist is used.

- decode profiles: 22/22 PASS
- runtime source functions: 68
- runtime DUT functions: 35
- runtime DUT functions with stable RTL: 10
- runtime DUT functions with provisional RTL PASS: 19
- runtime C orchestration/lifecycle boundaries: 6
- runtime DUT functions missing stable RTL: 25
- runtime DUT functions without any RTL: 6
- unresolved runtime compute functions without RTL: 0
- existing auto-generation-ready gaps: 0
- provisional state-transition candidates: 0
- simultaneous multi-RTL integration: PASS
- integration profiles/candidates: 22/29

## Stable RTL reached by Decode

| Function | Calls | Contract |
|---|---:|---|
| EscapeCodeSize | 378922 | escapecodesize |
| FindMidpoint | 111447 | findmidpoint |
| FindResidualSize | 1101654 | findresidualsize |
| GetQpAdjPredSize | 404352 | getqpadjpredsize |
| IsFlatnessInfoSent | 32832 | isflatnessinfosent |
| MapQpToQlevel | 4801364 | mapqptoqlevel |
| MaxResidualSize | 783274 | maxresidualsize |
| PredictSize | 367218 | predictsize |
| SampToLineBuf | 1334556 | samptolinebuf |
| SamplePredict | 15870816 | samplepredict |

## Provisional RTL passed full-frame regression

| Function | Calls | Contract |
|---|---:|---|
| BlockPredSearch | 1213056 | blockpredsearch_decode_transition |
| CalcFullnessOffset | 131328 | calcfullnessoffset_decode_transition |
| FlatnessAdjustment | 131328 | flatnessadjustment_decode_transition |
| GetBits | 1835127 | getbits_fifo_accounting_decode_transition |
| HistoryLookup | 9471828 | historylookup_decode_transition |
| PredictionLoop | 393984 | predictionloop_decode_transition |
| ProcessGroupDec | 131328 | processgroupdec_decode_transition |
| RateControl | 131328 | ratecontrol_decode_transition |
| RemoveBitsEncoderBuffer | 386271 | removebitsencoderbuffer_decode_transition |
| UpdateHistoryElement | 386208 | updatehistoryelement_decode_transition |
| UpdateICHistory | 393984 | updateichistory_decode_transition |
| UseICHistory | 11704 | useichistory_decode_transition |
| VLDGroup | 131328 | vldgroup_decode_transition |
| VLDUnit | 404352 | vldunit_decode_transition |
| fifo_get_bits | 1835127 | fifo_get_bits_decode_transition |
| fifo_put_bits | 584296 | fifo_put_bits_decode_transition |
| getbits | 586716 | getbits_decode_transition |
| rgb2ycocg | 15 | rgb2ycocg_pixel_transition |
| ycocg2rgb | 15 | ycocg2rgb_pixel_transition |

## Intentional C orchestration and lifecycle boundaries

| Function | Calls | Boundary class |
|---|---:|---|
| DSC_Algorithm | 24 | FRAME_IO_ORCHESTRATION |
| DSC_Decode | 24 | THIN_CALL_WRAPPER |
| InitializeDSCState | 24 | MEMORY_LIFECYCLE |
| fifo_free | 288 | MEMORY_LIFECYCLE |
| fifo_init | 288 | MEMORY_LIFECYCLE |
| main | 22 | FRAME_IO_ORCHESTRATION |

## Unresolved runtime compute functions

| Function | Calls | Frontier | Required work |
|---|---:|---|---|
| none | 0 | complete at current compute boundaries |

## Tool-selected provisional transition candidates

None.
