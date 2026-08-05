# Encode RTL frontier

Generated from the DSC_Encode root graph, Encode coverage, Clang facts, the stable RTL manifest, and phase-specific provisional receipts.
No function-name allowlist is used.

- root: `DSC_Encode`
- reached Encode functions: 44
- RTL reached: 39 (15 stable, 24 provisional)
- C shells: 5
- compute gaps: 0
- root functions not executed in Encode coverage: 8
- simultaneous Encode multi-RTL integration: PASS

## Traceability inputs

- source directory: `/Users/snow/Desktop/Display Stream Compression (DSC)/DSC 1.2a/DSC_model_20210623/source`
- candidates: `/private/tmp/dsc12a-regression-dashboard/facts/candidates.json` (e8b6c0b7c55821e9346c44ed7f231083f7115521a4501bf8485b4be64d83474b)
- coverage: `/private/tmp/dsc12a-regression-dashboard/coverage/coverage.json` (c1ffa82c8aa75cda7d43bf5f50c7453c5881c081bf97bf4768be803266b76d32)
- functions: `/private/tmp/dsc12a-regression-dashboard/facts/functions.json` (745223bd2321d4683d2fe9e5bd72334b4ca8ded7e2efbfb29802191e5518c106)
- manifest: `/private/tmp/dsc12a-regression-dashboard/library/manifest.json` (3c42a038a8d3367eb7225a40e102f7150495daab672e2de2ea261446cef301d0)
- provisional_root: `/private/tmp/dsc12a-regression-dashboard/rtl` (unhashed/unavailable)

## Reached Encode functions

| Function | Class | Calls | Source | Receipt |
|---|---|---:|---|---|
| AddBits | RTL | 1535313 | multiplex.c:89 | addbits_encode_transition |
| BlockPredSearch | RTL | 1213056 | dsc_codec.c:924 | blockpredsearch_decode_transition |
| CalcFullnessOffset | RTL | 131328 | dsc_codec.c:2188 | calcfullnessoffset_decode_transition |
| DSC_Algorithm | C_SHELL | 24 | dsc_codec.c:2594 | C/source |
| DSC_Encode | C_SHELL | 24 | dsc_codec.c:3118 | C/source |
| EscapeCodeSize | RTL | 20889 | dsc_codec.c:443 | escapecodesize |
| EstimateBitsForGroup | RTL | 20889 | dsc_codec.c:390 | estimatebitsforgroup |
| FindMidpoint | RTL | 2426112 | dsc_codec.c:906 | findmidpoint |
| FindResidualSize | RTL | 2743727 | dsc_codec.c:1078 | findresidualsize |
| FlatnessAdjustment | RTL | 131328 | dsc_codec.c:2510 | flatnessadjustment_decode_transition |
| GetQpAdjPredSize | RTL | 469602 | dsc_codec.c:278 | getqpadjpredsize |
| HistoryLookup | RTL | 25291655 | dsc_codec.c:543 | historylookup_decode_transition |
| IchDecision | RTL | 20889 | dsc_codec.c:484 | ichdecision_encode_transition |
| InitializeDSCState | C_SHELL | 24 | dsc_codec.c:2056 | C/source |
| IsFlatnessInfoSent | RTL | 275863 | dsc_codec.c:1116 | isflatnessinfosent |
| IsOrigFlatHIndex | RTL | 99389 | dsc_codec.c:1126 | isorigflathindex |
| IsOrigWithinQerr | RTL | 393984 | dsc_codec.c:611 | isorigwithinqerr_encode_history_transition |
| MapQpToQlevel | RTL | 7561479 | dsc_codec.c:221 | mapqptoqlevel |
| MaxResidualSize | RTL | 2181573 | dsc_codec.c:263 | maxresidualsize |
| PickBestHistoryValue | RTL | 125208 | dsc_codec.c:736 | pickbesthistoryvalue_encode_history_transition |
| PopulateOrigLine | RTL | 2592 | dsc_codec.c:2294 | populateorigline_encode_transition |
| PredictSize | RTL | 367218 | dsc_codec.c:1476 | predictsize |
| PredictionLoop | RTL | 393984 | dsc_codec.c:2361 | predictionloop_encode_transition |
| ProcessGroupEnc | RTL | 131328 | multiplex.c:116 | process_group_encode_fsm_v1 |
| QuantizeResidual | RTL | 2426112 | dsc_codec.c:245 | quantizeresidual |
| RateControl | RTL | 131328 | dsc_codec.c:1242 | ratecontrol_encode_transition |
| RemoveBitsEncoderBuffer | RTL | 387818 | dsc_codec.c:1201 | removebitsencoderbuffer_decode_transition |
| SampToLineBuf | RTL | 1334556 | dsc_codec.c:2036 | samptolinebuf |
| SamplePredict | RTL | 15870816 | dsc_codec.c:308 | samplepredict |
| UpdateHistoryElement | RTL | 386208 | dsc_codec.c:674 | updatehistoryelement_decode_transition |
| UpdateICHistory | RTL | 393984 | dsc_codec.c:787 | updateichistory_decode_transition |
| UpdateMidpoint | RTL | 131328 | dsc_codec.c:875 | updatemidpoint_encode_transition |
| UseICHistory | RTL | 11704 | dsc_codec.c:832 | useichistory_decode_transition |
| UsingMidpoint | RTL | 65250 | dsc_codec.c:457 | usingmidpoint |
| VLCGroup | RTL | 131328 | dsc_codec.c:1710 | vlc_group_encode_fsm_v1 |
| VLCUnit | RTL | 404352 | dsc_codec.c:1494 | vlcunit_encode_transition |
| ceil_log2 | RTL | 130500 | dsc_utils.c:67 | ceil_log2 |
| fifo_free | C_SHELL | 288 | fifo.c:66 | C/source |
| fifo_get_bits | RTL | 1392526 | fifo.c:77 | fifo_get_bits_decode_transition |
| fifo_init | C_SHELL | 288 | fifo.c:43 | C/source |
| fifo_put_bits | RTL | 2523961 | fifo.c:115 | fifo_put_bits_decode_transition |
| putbits | RTL | 586716 | dsc_utils.c:81 | putbits_encode_transition |
| rgb2ycocg | RTL | 15 | dsc_utils.c:145 | rgb2ycocg_pixel_transition |
| ycocg2rgb | RTL | 15 | dsc_utils.c:225 | ycocg2rgb_pixel_transition |

## RTL reached

| Function | Calls | Contract | Encode RTL_RETURN invocations |
|---|---:|---|---:|
| EscapeCodeSize | 20889 | escapecodesize | 0 |
| EstimateBitsForGroup | 20889 | estimatebitsforgroup | 0 |
| FindMidpoint | 2426112 | findmidpoint | 0 |
| FindResidualSize | 2743727 | findresidualsize | 0 |
| GetQpAdjPredSize | 469602 | getqpadjpredsize | 0 |
| IsFlatnessInfoSent | 275863 | isflatnessinfosent | 0 |
| IsOrigFlatHIndex | 99389 | isorigflathindex | 0 |
| MapQpToQlevel | 7561479 | mapqptoqlevel | 0 |
| MaxResidualSize | 2181573 | maxresidualsize | 0 |
| PredictSize | 367218 | predictsize | 0 |
| QuantizeResidual | 2426112 | quantizeresidual | 0 |
| SampToLineBuf | 1334556 | samptolinebuf | 0 |
| SamplePredict | 15870816 | samplepredict | 0 |
| UsingMidpoint | 65250 | usingmidpoint | 0 |
| ceil_log2 | 130500 | ceil_log2 | 0 |
| AddBits | 1535313 | addbits_encode_transition | 1535313 |
| BlockPredSearch | 1213056 | blockpredsearch_decode_transition | 1213056 |
| CalcFullnessOffset | 131328 | calcfullnessoffset_decode_transition | 131328 |
| FlatnessAdjustment | 131328 | flatnessadjustment_decode_transition | 131328 |
| HistoryLookup | 25291655 | historylookup_decode_transition | 25291655 |
| IchDecision | 20889 | ichdecision_encode_transition | 20889 |
| IsOrigWithinQerr | 393984 | isorigwithinqerr_encode_history_transition | 393984 |
| PickBestHistoryValue | 125208 | pickbesthistoryvalue_encode_history_transition | 125208 |
| PopulateOrigLine | 2592 | populateorigline_encode_transition | 2592 |
| PredictionLoop | 393984 | predictionloop_encode_transition | 393984 |
| ProcessGroupEnc | 131328 | process_group_encode_fsm_v1 | 131328 |
| RateControl | 131328 | ratecontrol_encode_transition | 131328 |
| RemoveBitsEncoderBuffer | 387818 | removebitsencoderbuffer_decode_transition | 387818 |
| UpdateHistoryElement | 386208 | updatehistoryelement_decode_transition | 386208 |
| UpdateICHistory | 393984 | updateichistory_decode_transition | 393984 |
| UpdateMidpoint | 131328 | updatemidpoint_encode_transition | 131328 |
| UseICHistory | 11704 | useichistory_decode_transition | 11704 |
| VLCGroup | 131328 | vlc_group_encode_fsm_v1 | 131328 |
| VLCUnit | 404352 | vlcunit_encode_transition | 404352 |
| fifo_get_bits | 1392526 | fifo_get_bits_decode_transition | 1392526 |
| fifo_put_bits | 2523961 | fifo_put_bits_decode_transition | 2523961 |
| putbits | 586716 | putbits_encode_transition | 586716 |
| rgb2ycocg | 15 | rgb2ycocg_pixel_transition | 269568 |
| ycocg2rgb | 15 | ycocg2rgb_pixel_transition | 269568 |

## C shells

| Function | Calls | Boundary | Source |
|---|---:|---|---|
| DSC_Algorithm | 24 | FRAME_IO_ORCHESTRATION | dsc_codec.c:2594 |
| DSC_Encode | 24 | THIN_CALL_WRAPPER | dsc_codec.c:3118 |
| InitializeDSCState | 24 | MEMORY_LIFECYCLE | dsc_codec.c:2056 |
| fifo_free | 288 | MEMORY_LIFECYCLE | fifo.c:66 |
| fifo_init | 288 | MEMORY_LIFECYCLE | fifo.c:43 |

## Compute gaps

| Function | Calls | Frontier | Required work | Source |
|---|---:|---|---|---|
| none | 0 | complete | none | none |

## Root functions not reached by Encode coverage

| Function | Source | Reason |
|---|---|---|
| ErrorHandler | dsc_codec.c:171 | NOT_EXECUTED_IN_ENCODE_COVERAGE |
| GetBits | multiplex.c:104 | NOT_EXECUTED_IN_ENCODE_COVERAGE |
| ProcessGroupDec | multiplex.c:159 | NOT_EXECUTED_IN_ENCODE_COVERAGE |
| VLDGroup | dsc_codec.c:1988 | NOT_EXECUTED_IN_ENCODE_COVERAGE |
| VLDUnit | dsc_codec.c:1808 | NOT_EXECUTED_IN_ENCODE_COVERAGE |
| getbits | dsc_utils.c:109 | NOT_EXECUTED_IN_ENCODE_COVERAGE |
| yuv_422_444_region | dsc_utils.c:375 | NOT_EXECUTED_IN_ENCODE_COVERAGE |
| yuv_444_422_region | dsc_utils.c:385 | NOT_EXECUTED_IN_ENCODE_COVERAGE |
