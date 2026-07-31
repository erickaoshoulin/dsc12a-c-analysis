# Candidate functions

These are proposal labels supported by recorded AST/Frama evidence; they are not RTL generation decisions.

## `DSC_Decode` — COMPOSITE_COMB_CANDIDATE

- Pure candidate: `False`
- Combinational candidate: `True`
- Evidence: AST observed no global/field/pointee writes; AST pointer modes: ['UNKNOWN', 'UNKNOWN', 'UNKNOWN', 'UNKNOWN']; AST observed no loop

## `DSC_Encode` — COMPOSITE_COMB_CANDIDATE

- Pure candidate: `False`
- Combinational candidate: `True`
- Evidence: AST observed no global/field/pointee writes; AST pointer modes: ['UNKNOWN', 'UNKNOWN', 'UNKNOWN', 'UNKNOWN', 'UNKNOWN', 'UNKNOWN']; AST observed no loop

## `EscapeCodeSize` — COMPOSITE_COMB_CANDIDATE

- Pure candidate: `False`
- Combinational candidate: `True`
- Evidence: AST observed no global/field/pointee writes; AST pointer modes: ['UNKNOWN', 'UNKNOWN']; AST observed field reads: dsc_state_t.cpntBitDepth; AST observed no loop

## `EstimateBitsForGroup` — COMPOSITE_COMB_CANDIDATE

- Pure candidate: `False`
- Combinational candidate: `True`
- Evidence: AST observed no global/field/pointee writes; AST pointer modes: ['UNKNOWN', 'UNKNOWN']; AST observed field reads: dsc_state_t.hPos, dsc_state_t.pixelsInGroup, dsc_state_t.prevIchSelected, dsc_state_t.primaryQp, dsc_state_t.primaryQp, dsc_state_t.primaryQp, dsc_state_t.quantizedResidual, dsc_state_t.sliceWidth, dsc_state_t.unitCType, dsc_state_t.unitCType, dsc_state_t.unitStartHPos, dsc_state_t.unitsPerGroup, dsc_state_t.unitsPerGroup; AST loop count is 4; trip proofs are retained per loop

## `FindMidpoint` — PURE_COMB_CANDIDATE

- Pure candidate: `True`
- Combinational candidate: `True`
- Evidence: AST observed no global/field/pointee writes; AST pointer modes: ['READ_ONLY']; AST observed field reads: dsc_state_t.cpntBitDepth, dsc_state_t.leftRecon; AST observed no loop; No direct calls and no non-const global read were observed

## `GetQpAdjPredSize` — COMPOSITE_COMB_CANDIDATE

- Pure candidate: `False`
- Combinational candidate: `True`
- Evidence: AST observed no global/field/pointee writes; AST pointer modes: ['UNKNOWN', 'UNKNOWN']; AST observed field reads: dsc_state_t.predictedSize, dsc_state_t.prevPrimaryQp, dsc_state_t.primaryQp, dsc_state_t.primaryQp, dsc_state_t.unitCType; AST observed no loop

## `IsFlatnessInfoSent` — CONFIG_HELPER

- Pure candidate: `False`
- Combinational candidate: `True`
- Evidence: AST observed no global/field/pointee writes; AST pointer modes: ['READ_ONLY']; AST observed field reads: dsc_cfg_t.flatness_max_qp, dsc_cfg_t.flatness_min_qp; AST observed no loop; The proposal is per-field input use; the containing struct is not classified as static configuration

## `IsOrigFlatHIndex` — CONFIG_HELPER

- Pure candidate: `False`
- Combinational candidate: `True`
- Evidence: AST observed no global/field/pointee writes; AST pointer modes: ['UNKNOWN', 'UNKNOWN']; AST observed global reads: QuantDivisor, QuantDivisor; AST observed field reads: dsc_cfg_t.flatness_det_thresh, dsc_cfg_t.flatness_det_thresh, dsc_cfg_t.somewhat_flat_qp_delta, dsc_state_t.numComponents, dsc_state_t.numComponents, dsc_state_t.numComponents, dsc_state_t.origLine, dsc_state_t.origLine, dsc_state_t.primaryQp, dsc_state_t.sliceWidth, dsc_state_t.sliceWidth; AST loop count is 5; trip proofs are retained per loop; The proposal is per-field input use; the containing struct is not classified as static configuration

## `MapQpToQlevel` — CONFIG_HELPER

- Pure candidate: `False`
- Combinational candidate: `True`
- Evidence: AST observed no global/field/pointee writes; AST pointer modes: ['READ_ONLY', 'READ_ONLY']; AST observed field reads: dsc_cfg_t.dsc_version_minor, dsc_cfg_t.native_420, dsc_state_t.cpntBitDepth, dsc_state_t.cpntBitDepth, dsc_state_t.quantTableChroma, dsc_state_t.quantTableLuma, dsc_state_t.quantTableLuma; AST observed no loop; The proposal is per-field input use; the containing struct is not classified as static configuration

## `MaxResidualSize` — COMPOSITE_COMB_CANDIDATE

- Pure candidate: `False`
- Combinational candidate: `True`
- Evidence: AST observed no global/field/pointee writes; AST pointer modes: ['UNKNOWN', 'UNKNOWN']; AST observed field reads: dsc_state_t.cpntBitDepth; AST observed no loop

## `PredictSize` — PURE_COMB_CANDIDATE

- Pure candidate: `True`
- Combinational candidate: `True`
- Evidence: AST observed no global/field/pointee writes; AST pointer modes: ['READ_ONLY', 'READ_ONLY']; AST observed no loop; No direct calls and no non-const global read were observed

## `ProcessGroupDec` — CONFIG_HELPER

- Pure candidate: `False`
- Combinational candidate: `True`
- Evidence: AST observed no global/field/pointee writes; AST pointer modes: ['READ_ONLY', 'UNKNOWN', 'UNKNOWN']; AST observed field reads: dsc_cfg_t.mux_word_size, dsc_state_t.maxSeSize, dsc_state_t.numSsps, dsc_state_t.postMuxNumBits, dsc_state_t.shifter, dsc_state_t.shifter, fifo_s.fullness; AST loop count is 2; trip proofs are retained per loop; The proposal is per-field input use; the containing struct is not classified as static configuration

## `ProcessGroupEnc` — CONFIG_HELPER

- Pure candidate: `False`
- Combinational candidate: `True`
- Evidence: AST observed no global/field/pointee writes; AST pointer modes: ['READ_ONLY', 'UNKNOWN', 'UNKNOWN']; AST observed field reads: dsc_cfg_t.mux_word_size, dsc_state_t.encBalanceFifo, dsc_state_t.encBalanceFifo, dsc_state_t.encBalanceFifo, dsc_state_t.isEncoder, dsc_state_t.maxSeSize, dsc_state_t.numBits, dsc_state_t.numSsps, dsc_state_t.postMuxNumBits, dsc_state_t.seSizeFifo, dsc_state_t.shifter, dsc_state_t.shifter, dsc_state_t.shifter, fifo_s.fullness, fifo_s.fullness; AST loop count is 2; trip proofs are retained per loop; The proposal is per-field input use; the containing struct is not classified as static configuration

## `Qp2Qlevel` — CONFIG_HELPER

- Pure candidate: `False`
- Combinational candidate: `True`
- Evidence: AST observed no global/field/pointee writes; AST pointer modes: ['READ_ONLY']; AST observed global reads: qlevel_chroma_10bpc, qlevel_chroma_12bpc, qlevel_chroma_14bpc, qlevel_chroma_16bpc, qlevel_chroma_8bpc, qlevel_luma_10bpc, qlevel_luma_12bpc, qlevel_luma_14bpc, qlevel_luma_16bpc, qlevel_luma_8bpc; AST observed field reads: dsc_cfg_t.bits_per_component, dsc_cfg_t.bits_per_component, dsc_cfg_t.convert_rgb, dsc_cfg_t.dsc_version_minor, dsc_cfg_t.native_420; AST observed no loop; The proposal is per-field input use; the containing struct is not classified as static configuration

## `QuantizeResidual` — PURE_COMB_CANDIDATE

- Pure candidate: `True`
- Combinational candidate: `True`
- Evidence: AST observed no global/field/pointee writes; AST observed global reads: QuantOffset, QuantOffset; AST observed no loop; No direct calls and no non-const global read were observed

## `SampToLineBuf` — CONFIG_HELPER

- Pure candidate: `False`
- Combinational candidate: `True`
- Evidence: AST observed no global/field/pointee writes; AST pointer modes: ['READ_ONLY', 'READ_ONLY']; AST observed field reads: dsc_cfg_t.linebuf_depth, dsc_cfg_t.linebuf_depth, dsc_state_t.cpntBitDepth; AST observed no loop; The proposal is per-field input use; the containing struct is not classified as static configuration

## `SamplePredict` — PURE_COMB_CANDIDATE

- Pure candidate: `True`
- Combinational candidate: `True`
- Evidence: AST observed no global/field/pointee writes; AST pointer modes: ['READ_ONLY', 'READ_ONLY', 'READ_ONLY']; AST observed global reads: QuantDivisor, QuantDivisor, QuantDivisor, QuantDivisor, QuantDivisor, QuantDivisor, QuantDivisor, QuantDivisor; AST observed field reads: dsc_state_t.cpntBitDepth, dsc_state_t.cpntBitDepth, dsc_state_t.quantizedResidual, dsc_state_t.quantizedResidual, dsc_state_t.quantizedResidual, dsc_state_t.quantizedResidual, dsc_state_t.unitCType; AST observed no loop; No direct calls and no non-const global read were observed

## `UsingMidpoint` — COMPOSITE_COMB_CANDIDATE

- Pure candidate: `False`
- Combinational candidate: `True`
- Evidence: AST observed no global/field/pointee writes; AST pointer modes: ['UNKNOWN', 'UNKNOWN']; AST observed field reads: dsc_state_t.cpntBitDepth, dsc_state_t.primaryQp, dsc_state_t.quantizedResidual; AST loop count is 1; trip proofs are retained per loop

## `appendarg` — COMPOSITE_COMB_CANDIDATE

- Pure candidate: `False`
- Combinational candidate: `True`
- Evidence: AST observed no global/field/pointee writes; AST pointer modes: ['UNKNOWN']; AST observed field reads: cmdarg_s.type; AST observed no loop

## `ceil_log2` — PURE_COMB_CANDIDATE

- Pure candidate: `True`
- Combinational candidate: `True`
- Evidence: AST observed no global/field/pointee writes; AST loop count is 1; trip proofs are retained per loop; No direct calls and no non-const global read were observed

## `change_ext` — COMPOSITE_COMB_CANDIDATE

- Pure candidate: `False`
- Combinational candidate: `True`
- Evidence: AST observed no global/field/pointee writes; AST pointer modes: ['READ_ONLY', 'UNKNOWN']; AST loop count is 1; trip proofs are retained per loop

## `conv` — PURE_COMB_CANDIDATE

- Pure candidate: `True`
- Combinational candidate: `True`
- Evidence: AST observed no global/field/pointee writes; AST pointer modes: ['READ_ONLY']; AST observed field reads: fir_s.coeff, fir_s.sub, fir_s.sub, fir_s.sub, fir_s.tap, fir_s.tap; AST loop count is 2; trip proofs are retained per loop; No direct calls and no non-const global read were observed

## `dpx_read` — COMPOSITE_COMB_CANDIDATE

- Pure candidate: `False`
- Combinational candidate: `True`
- Evidence: AST observed no global/field/pointee writes; AST pointer modes: ['UNKNOWN', 'UNKNOWN']; AST observed no loop

## `dpx_write` — COMPOSITE_COMB_CANDIDATE

- Pure candidate: `False`
- Combinational candidate: `True`
- Evidence: AST observed no global/field/pointee writes; AST pointer modes: ['UNKNOWN', 'UNKNOWN']; AST observed field reads: pic_s.ar1, pic_s.ar2, pic_s.bits, pic_s.framerate, pic_s.frm_no, pic_s.interlaced, pic_s.seq_len; AST observed no loop

## `ends_in_percentd` — PURE_COMB_CANDIDATE

- Pure candidate: `True`
- Combinational candidate: `True`
- Evidence: AST observed no global/field/pointee writes; AST pointer modes: ['READ_ONLY']; AST loop count is 1; trip proofs are retained per loop; No direct calls and no non-const global read were observed

## `fifo_clone` — COMPOSITE_COMB_CANDIDATE

- Pure candidate: `False`
- Combinational candidate: `True`
- Evidence: AST observed no global/field/pointee writes; AST pointer modes: ['UNKNOWN', 'UNKNOWN']; AST observed field reads: fifo_s.fullness, fifo_s.fullness, fifo_s.fullness, fifo_s.fullness, fifo_s.fullness, fifo_s.fullness, fifo_s.size, fifo_s.size; AST loop count is 2; trip proofs are retained per loop

## `generate_timecode` — PURE_COMB_CANDIDATE

- Pure candidate: `True`
- Combinational candidate: `True`
- Evidence: AST observed no global/field/pointee writes; AST observed no loop; No direct calls and no non-const global read were observed

## `getbits` — PURE_COMB_CANDIDATE

- Pure candidate: `True`
- Combinational candidate: `True`
- Evidence: AST observed no global/field/pointee writes; AST pointer modes: ['READ_ONLY', 'READ_ONLY']; AST loop count is 1; trip proofs are retained per loop; No direct calls and no non-const global read were observed

## `has_ext` — COMPOSITE_COMB_CANDIDATE

- Pure candidate: `False`
- Combinational candidate: `True`
- Evidence: AST observed no global/field/pointee writes; AST pointer modes: ['READ_ONLY']; AST observed no loop

## `hdr_dpx_byte_swap` — PURE_COMB_CANDIDATE

- Pure candidate: `True`
- Combinational candidate: `True`
- Evidence: AST observed no global/field/pointee writes; AST pointer modes: ['READ_ONLY']; AST loop count is 2; trip proofs are retained per loop; No direct calls and no non-const global read were observed

## `lower_case` — COMPOSITE_COMB_CANDIDATE

- Pure candidate: `False`
- Combinational candidate: `True`
- Evidence: AST observed no global/field/pointee writes; AST pointer modes: ['UNKNOWN']; AST loop count is 1; trip proofs are retained per loop

## `make_qp_tables` — COMPOSITE_COMB_CANDIDATE

- Pure candidate: `False`
- Combinational candidate: `True`
- Evidence: AST observed no global/field/pointee writes; AST observed global reads: maxqp420_10b, maxqp420_12b, maxqp420_8b, maxqp422_10b, maxqp422_12b, maxqp422_8b, maxqp444_10b, maxqp444_12b, maxqp444_8b, maxqp_420, maxqp_420, maxqp_420, maxqp_422, maxqp_422, maxqp_422, maxqp_444, maxqp_444, maxqp_444, minqp420_10b, minqp420_12b, minqp420_8b, minqp422_10b, minqp422_12b, minqp422_8b, minqp444_10b, minqp444_12b, minqp444_8b, minqp_420, minqp_420, minqp_420, minqp_422, minqp_422, minqp_422, minqp_444, minqp_444, minqp_444; AST observed no loop

## `splitstring_exact` — COMPOSITE_COMB_CANDIDATE

- Pure candidate: `False`
- Combinational candidate: `True`
- Evidence: AST observed no global/field/pointee writes; AST pointer modes: ['READ_ONLY', 'READ_ONLY']; AST observed no loop

## `str2d` — COMPOSITE_COMB_CANDIDATE

- Pure candidate: `False`
- Combinational candidate: `True`
- Evidence: AST observed no global/field/pointee writes; AST pointer modes: ['UNKNOWN', 'UNKNOWN']; AST observed no loop

## `str2f` — COMPOSITE_COMB_CANDIDATE

- Pure candidate: `False`
- Combinational candidate: `True`
- Evidence: AST observed no global/field/pointee writes; AST pointer modes: ['READ_ONLY', 'UNKNOWN']; AST observed no loop

## `str2i` — COMPOSITE_COMB_CANDIDATE

- Pure candidate: `False`
- Combinational candidate: `True`
- Evidence: AST observed no global/field/pointee writes; AST pointer modes: ['UNKNOWN', 'UNKNOWN']; AST observed no loop

## `str2l` — COMPOSITE_COMB_CANDIDATE

- Pure candidate: `False`
- Combinational candidate: `True`
- Evidence: AST observed no global/field/pointee writes; AST pointer modes: ['READ_ONLY', 'UNKNOWN']; AST observed no loop

## `str2ll` — COMPOSITE_COMB_CANDIDATE

- Pure candidate: `False`
- Combinational candidate: `True`
- Evidence: AST observed no global/field/pointee writes; AST pointer modes: ['UNKNOWN', 'UNKNOWN']; AST observed no loop

## `str2p` — COMPOSITE_COMB_CANDIDATE

- Pure candidate: `False`
- Combinational candidate: `True`
- Evidence: AST observed no global/field/pointee writes; AST pointer modes: ['UNKNOWN', 'UNKNOWN']; AST observed no loop

## `str2ui` — COMPOSITE_COMB_CANDIDATE

- Pure candidate: `False`
- Combinational candidate: `True`
- Evidence: AST observed no global/field/pointee writes; AST pointer modes: ['UNKNOWN', 'UNKNOWN']; AST observed no loop

## `str2ul` — COMPOSITE_COMB_CANDIDATE

- Pure candidate: `False`
- Combinational candidate: `True`
- Evidence: AST observed no global/field/pointee writes; AST pointer modes: ['READ_ONLY', 'UNKNOWN']; AST observed no loop

## `str2ull` — COMPOSITE_COMB_CANDIDATE

- Pure candidate: `False`
- Combinational candidate: `True`
- Evidence: AST observed no global/field/pointee writes; AST pointer modes: ['UNKNOWN', 'UNKNOWN']; AST observed no loop

## `strisdim` — COMPOSITE_COMB_CANDIDATE

- Pure candidate: `False`
- Combinational candidate: `True`
- Evidence: AST observed no global/field/pointee writes; AST pointer modes: ['UNKNOWN']; AST loop count is 1; trip proofs are retained per loop

## `strisnum` — COMPOSITE_COMB_CANDIDATE

- Pure candidate: `False`
- Combinational candidate: `True`
- Evidence: AST observed no global/field/pointee writes; AST pointer modes: ['UNKNOWN']; AST loop count is 1; trip proofs are retained per loop

## `strisrange` — COMPOSITE_COMB_CANDIDATE

- Pure candidate: `False`
- Combinational candidate: `True`
- Evidence: AST observed no global/field/pointee writes; AST pointer modes: ['UNKNOWN']; AST loop count is 1; trip proofs are retained per loop

## `write_dpx` — COMPOSITE_COMB_CANDIDATE

- Pure candidate: `False`
- Combinational candidate: `True`
- Evidence: AST observed no global/field/pointee writes; AST pointer modes: ['UNKNOWN', 'UNKNOWN']; AST observed no loop

## `write_pps` — CONFIG_HELPER

- Pure candidate: `False`
- Combinational candidate: `True`
- Evidence: AST observed no global/field/pointee writes; AST pointer modes: ['UNKNOWN', 'UNKNOWN']; AST observed field reads: dsc_cfg_t.bits_per_component, dsc_cfg_t.bits_per_pixel, dsc_cfg_t.block_pred_enable, dsc_cfg_t.chunk_size, dsc_cfg_t.convert_rgb, dsc_cfg_t.dsc_version_minor, dsc_cfg_t.dsc_version_minor, dsc_cfg_t.final_offset, dsc_cfg_t.first_line_bpg_ofs, dsc_cfg_t.flatness_max_qp, dsc_cfg_t.flatness_min_qp, dsc_cfg_t.initial_dec_delay, dsc_cfg_t.initial_offset, dsc_cfg_t.initial_scale_value, dsc_cfg_t.initial_xmit_delay, dsc_cfg_t.linebuf_depth, dsc_cfg_t.native_420, dsc_cfg_t.native_422, dsc_cfg_t.nfl_bpg_offset, dsc_cfg_t.nsl_bpg_offset, dsc_cfg_t.pic_height, dsc_cfg_t.pic_width, dsc_cfg_t.pps_identifier, dsc_cfg_t.rc_buf_thresh, dsc_cfg_t.rc_edge_factor, dsc_cfg_t.rc_model_size, dsc_cfg_t.rc_quant_incr_limit0, dsc_cfg_t.rc_quant_incr_limit1, dsc_cfg_t.rc_range_parameters, dsc_cfg_t.rc_range_parameters, dsc_cfg_t.rc_range_parameters, dsc_cfg_t.rc_tgt_offset_hi, dsc_cfg_t.rc_tgt_offset_lo, dsc_cfg_t.scale_decrement_interval, dsc_cfg_t.scale_increment_interval, dsc_cfg_t.second_line_bpg_ofs, dsc_cfg_t.second_line_ofs_adj, dsc_cfg_t.simple_422, dsc_cfg_t.slice_bpg_offset, dsc_cfg_t.slice_height, dsc_cfg_t.slice_width, dsc_cfg_t.vbr_enable, dsc_range_cfg_t.range_bpg_offset, dsc_range_cfg_t.range_max_qp, dsc_range_cfg_t.range_min_qp; AST loop count is 2; trip proofs are retained per loop; The proposal is per-field input use; the containing struct is not classified as static configuration
