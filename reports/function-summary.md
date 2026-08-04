# Function summary

Facts are from Clang LibTooling/AST Matchers and Frama-C runs selected by the auto-ranked candidate receipt.
A proposal is not a hardware equivalence claim.

## `AddBits`

- Source: `multiplex.c:89`
- Clang USR: `c:@F@AddBits`
- Return: `void`; parameters: `dsc_cfg: dsc_cfg_t *`, `dsc_state: dsc_state_t *`, `CType: int`, `d: int`, `nbits: int`
- Callers: VLCUnit
- Callees: fifo_put_bits
- Global read/write: 0/0; field read/write: 1/1
- Pointer modes: dsc_cfg=READ_ONLY, dsc_state=WRITES_THROUGH
- Loops: 0; fixed counts: UNKNOWN
- Effects: `{"assert": false, "file_io": false, "indirect_call": false, "logging": false, "malloc": false}`
- Proposal: **STATEFUL**; purity=False; combinational=False
- Classification evidence:
  - AST observed writes or mutable-state effects: ['dsc_state', 'dsc_state_t.numBits']
  - AST pointer modes: ['READ_ONLY', 'WRITES_THROUGH']
  - AST observed field reads: dsc_state_t.encBalanceFifo
  - AST observed no loop

## `Assert_func`

- Source: `logging.c:155`
- Clang USR: `c:@F@Assert_func`
- Return: `void`; parameters: `condition: int`, `condition_str: const char *const`, `cline: int`, `cfile: const char *const`, `cfunction: const char *const`
- Callers: parse_cmd, parse_line, retrieve_cmds_var, retrieve_keys_var, assign_val, distinguish_dist, order_cmds, order_keys, parse_kvline
- Callees: exit, fprintf
- Global read/write: 1/0; field read/write: 0/0
- Pointer modes: condition_str=UNKNOWN, cfile=UNKNOWN, cfunction=UNKNOWN
- Loops: 0; fixed counts: UNKNOWN
- Effects: `{"assert": false, "file_io": true, "indirect_call": false, "logging": false, "malloc": false}`
- Proposal: **IO_OR_DEBUG**; purity=False; combinational=False
- Classification evidence:
  - AST observed no global/field/pointee writes
  - AST pointer modes: ['UNKNOWN', 'UNKNOWN', 'UNKNOWN']
  - AST observed global reads: __stderrp
  - AST observed no loop

## `BlockPredSearch`

- Source: `dsc_codec.c:924`
- Clang USR: `c:@F@BlockPredSearch`
- Return: `void`; parameters: `dsc_cfg: dsc_cfg_t *`, `dsc_state: dsc_state_t *`, `cpnt: int`, `currLine: int **`, `hPos: int`
- Callers: DSC_Algorithm
- Callees: SamplePredict
- Global read/write: 0/0; field read/write: 14/14
- Pointer modes: dsc_cfg=READ_ONLY, dsc_state=WRITES_THROUGH, currLine=UNKNOWN
- Loops: 9; fixed counts: 3, 13, 13, 13, 13, 3
- Effects: `{"assert": false, "file_io": false, "indirect_call": false, "logging": false, "malloc": false}`
- Proposal: **STATEFUL**; purity=False; combinational=False
- Classification evidence:
  - AST observed writes or mutable-state effects: ['dsc_state', 'dsc_state_t.bpCount', 'dsc_state_t.edgeDetected', 'dsc_state_t.lastEdgeCount', 'dsc_state_t.lastErr', 'dsc_state_t.predErr', 'dsc_state_t.prevLinePred']
  - AST pointer modes: ['READ_ONLY', 'UNKNOWN', 'WRITES_THROUGH']
  - AST observed field reads: dsc_cfg_t.bits_per_component, dsc_cfg_t.block_pred_enable, dsc_cfg_t.native_420, dsc_state_t.bpCount, dsc_state_t.cpntBitDepth, dsc_state_t.cpntBitDepth, dsc_state_t.cpntBitDepth, dsc_state_t.edgeDetected, dsc_state_t.lastEdgeCount, dsc_state_t.lastErr, dsc_state_t.numComponents, dsc_state_t.numComponents, dsc_state_t.numComponents, dsc_state_t.predErr
  - AST loop count is 9; trip proofs are retained per loop

## `CErr`

- Source: `logging.c:123`
- Clang USR: `c:@F@CErr`
- Return: `void`; parameters: `format: char *`
- Callers: parse_cmd, parse_line, error_check
- Callees: __builtin_va_end, __builtin_va_start, exit, fprintf, vfprintf
- Global read/write: 3/0; field read/write: 0/0
- Pointer modes: format=UNKNOWN
- Loops: 0; fixed counts: UNKNOWN
- Effects: `{"assert": false, "file_io": true, "indirect_call": false, "logging": false, "malloc": false}`
- Proposal: **IO_OR_DEBUG**; purity=False; combinational=False
- Classification evidence:
  - AST observed no global/field/pointee writes
  - AST pointer modes: ['UNKNOWN']
  - AST observed global reads: __stderrp, __stderrp, __stderrp
  - AST observed no loop

## `CalcFullnessOffset`

- Source: `dsc_codec.c:2188`
- Clang USR: `c:@F@CalcFullnessOffset`
- Return: `void`; parameters: `dsc_cfg: dsc_cfg_t *`, `dsc_state: dsc_state_t *`, `vPos: int`, `group_count: int`, `scale: int *`, `bpg_offset: int *`
- Callers: DSC_Algorithm
- Callees: NONE
- Global read/write: 0/0; field read/write: 40/19
- Pointer modes: dsc_cfg=READ_ONLY, dsc_state=WRITES_THROUGH, scale=WRITES_THROUGH, bpg_offset=WRITES_THROUGH
- Loops: 0; fixed counts: UNKNOWN
- Effects: `{"assert": false, "file_io": false, "indirect_call": false, "logging": false, "malloc": false}`
- Proposal: **STATEFUL**; purity=False; combinational=False
- Classification evidence:
  - AST observed writes or mutable-state effects: ['bpg_offset', 'dsc_state', 'dsc_state_t.currentScale', 'dsc_state_t.prevPixelCount', 'dsc_state_t.rcOffsetClampEnable', 'dsc_state_t.rcXformOffset', 'dsc_state_t.scaleAdjustCounter', 'dsc_state_t.scaleIncrementStart', 'dsc_state_t.secondOffsetApplied', 'dsc_state_t.throttleFrac', 'scale']
  - AST pointer modes: ['READ_ONLY', 'WRITES_THROUGH', 'WRITES_THROUGH', 'WRITES_THROUGH']
  - AST observed field reads: dsc_cfg_t.bits_per_pixel, dsc_cfg_t.final_offset, dsc_cfg_t.final_offset, dsc_cfg_t.first_line_bpg_ofs, dsc_cfg_t.first_line_bpg_ofs, dsc_cfg_t.initial_scale_value, dsc_cfg_t.initial_xmit_delay, dsc_cfg_t.initial_xmit_delay, dsc_cfg_t.nfl_bpg_offset, dsc_cfg_t.nfl_bpg_offset, dsc_cfg_t.nsl_bpg_offset, dsc_cfg_t.nsl_bpg_offset, dsc_cfg_t.scale_decrement_interval, dsc_cfg_t.scale_increment_interval, dsc_cfg_t.scale_increment_interval, dsc_cfg_t.second_line_bpg_ofs, dsc_cfg_t.second_line_bpg_ofs, dsc_cfg_t.second_line_ofs_adj, dsc_cfg_t.slice_bpg_offset, dsc_cfg_t.slice_bpg_offset, dsc_state_t.currentScale, dsc_state_t.currentScale, dsc_state_t.pixelCount, dsc_state_t.pixelCount, dsc_state_t.pixelCount, dsc_state_t.pixelCount, dsc_state_t.pixelCount, dsc_state_t.pixelsInGroup, dsc_state_t.prevPixelCount, dsc_state_t.rcOffsetClampEnable, dsc_state_t.rcXformOffset, dsc_state_t.rcXformOffset, dsc_state_t.rcXformOffset, dsc_state_t.scaleAdjustCounter, dsc_state_t.scaleAdjustCounter, dsc_state_t.scaleIncrementStart, dsc_state_t.scaleIncrementStart, dsc_state_t.secondOffsetApplied, dsc_state_t.throttleFrac, dsc_state_t.throttleFrac
  - AST observed no loop

## `DSC_Algorithm`

- Source: `dsc_codec.c:2594`
- Clang USR: `c:@F@DSC_Algorithm`
- Return: `int`; parameters: `isEncoder: int`, `dsc_cfg: dsc_cfg_t *`, `ip: pic_t *`, `op: pic_t *`, `cmpr_buf: unsigned char *`, `temp_pic: pic_t **`, `chunk_sizes: int *`
- Callers: DSC_Decode, DSC_Encode
- Callees: BlockPredSearch, CalcFullnessOffset, ErrorHandler, FlatnessAdjustment, HistoryLookup, InitializeDSCState, IsOrigWithinQerr, PickBestHistoryValue, PopulateOrigLine, PredictionLoop, ProcessGroupEnc, RateControl, RemoveBitsEncoderBuffer, SampToLineBuf, UpdateICHistory, UpdateMidpoint, UseICHistory, VLCGroup, VLDGroup, abs, exit, fifo_free, fprintf, free, malloc, printf, rgb2ycocg, ycocg2rgb, yuv_422_444_region, yuv_444_422_region
- Global read/write: 6/0; field read/write: 127/62
- Pointer modes: dsc_cfg=UNKNOWN, ip=UNKNOWN, op=UNKNOWN, cmpr_buf=UNKNOWN, temp_pic=READ_ONLY, chunk_sizes=READ_ONLY
- Loops: 29; fixed counts: 4, 32, 3, 4
- Effects: `{"assert": false, "file_io": true, "indirect_call": false, "logging": true, "malloc": true}`
- Proposal: **IO_OR_DEBUG**; purity=False; combinational=False
- Classification evidence:
  - AST observed writes or mutable-state effects: ['data_u.yuv', 'dsc_history_t.pixels', 'dsc_state_t.bitsClamped', 'dsc_state_t.bufferFullness', 'dsc_state_t.chunkCount', 'dsc_state_t.chunkSizes', 'dsc_state_t.cpntBitDepth', 'dsc_state_t.currLine', 'dsc_state_t.errorOccurred', 'dsc_state_t.groupCount', 'dsc_state_t.groupCountLine', 'dsc_state_t.hPos', 'dsc_state_t.history', 'dsc_state_t.ichLookup', 'dsc_state_t.isEncoder', 'dsc_state_t.leftRecon', 'dsc_state_t.maxError', 'dsc_state_t.maxIchError', 'dsc_state_t.maxMidError', 'dsc_state_t.midpointSelected', 'dsc_state_t.origLine', 'dsc_state_t.origWithinQerr', 'dsc_state_t.prevLine', 'dsc_state_t.primaryQp', 'dsc_state_t.quantizedResidual', 'dsc_state_t.quantizedResidualMid', 'dsc_state_t.vPos', 'pic_s.data', 'yuv_s.u', 'yuv_s.v', 'yuv_s.y']
  - AST pointer modes: ['READ_ONLY', 'READ_ONLY', 'UNKNOWN', 'UNKNOWN', 'UNKNOWN', 'UNKNOWN']
  - AST observed global reads: g_fp_dbg, g_fp_dbg, g_verbose, g_verbose, g_verbose, g_verbose
  - AST observed field reads: dsc_cfg_t.bits_per_component, dsc_cfg_t.bits_per_component, dsc_cfg_t.bits_per_component, dsc_cfg_t.bits_per_component, dsc_cfg_t.bits_per_component, dsc_cfg_t.bits_per_pixel, dsc_cfg_t.convert_rgb, dsc_cfg_t.convert_rgb, dsc_cfg_t.convert_rgb, dsc_cfg_t.convert_rgb, dsc_cfg_t.convert_rgb, dsc_cfg_t.full_ich_err_precision, dsc_cfg_t.initial_xmit_delay, dsc_cfg_t.native_420, dsc_cfg_t.native_420, dsc_cfg_t.native_420, dsc_cfg_t.native_420, dsc_cfg_t.native_420, dsc_cfg_t.native_420, dsc_cfg_t.native_420, dsc_cfg_t.native_422, dsc_cfg_t.native_422, dsc_cfg_t.native_422, dsc_cfg_t.native_422, dsc_cfg_t.slice_height, dsc_cfg_t.slice_height, dsc_cfg_t.slice_height, dsc_cfg_t.slice_height, dsc_cfg_t.slice_height, dsc_cfg_t.slice_height, dsc_cfg_t.vbr_enable, dsc_cfg_t.vbr_enable, dsc_cfg_t.vbr_enable, dsc_cfg_t.xstart, dsc_cfg_t.xstart, dsc_cfg_t.xstart, dsc_cfg_t.ystart, dsc_history_t.pixels, dsc_history_t.valid, dsc_state_t.bufferFullness, dsc_state_t.bufferFullness, dsc_state_t.bufferFullness, dsc_state_t.bufferFullness, dsc_state_t.bufferFullness, dsc_state_t.chunkCount, dsc_state_t.chunkCount, dsc_state_t.chunkCount, dsc_state_t.chunkSizes, dsc_state_t.cpntBitDepth, dsc_state_t.currLine, dsc_state_t.currLine, dsc_state_t.encBalanceFifo, dsc_state_t.errorOccurred, dsc_state_t.history, dsc_state_t.history, dsc_state_t.ichLookup, dsc_state_t.ichLookup, dsc_state_t.ichLookup, dsc_state_t.ichPixels, dsc_state_t.ichPixels, dsc_state_t.ichPixels, dsc_state_t.ichPixels, dsc_state_t.ichPixels, dsc_state_t.ichPixels, dsc_state_t.ichPixels, dsc_state_t.ichSelected, dsc_state_t.ichSelected, dsc_state_t.isEncoder, dsc_state_t.isEncoder, dsc_state_t.isEncoder, dsc_state_t.maxIchError, dsc_state_t.numComponents, dsc_state_t.numComponents, dsc_state_t.numComponents, dsc_state_t.numComponents, dsc_state_t.numComponents, dsc_state_t.numComponents, dsc_state_t.numComponents, dsc_state_t.numComponents, dsc_state_t.numComponents, dsc_state_t.numComponents, dsc_state_t.origLine, dsc_state_t.origLine, dsc_state_t.pixelsInGroup, dsc_state_t.pixelsInGroup, dsc_state_t.pixelsInGroup, dsc_state_t.pixelsInGroup, dsc_state_t.pixelsInGroup, dsc_state_t.pixelsInGroup, dsc_state_t.pixelsInGroup, dsc_state_t.pixelsInGroup, dsc_state_t.pixelsInGroup, dsc_state_t.pixelsInGroup, dsc_state_t.pixelsInGroup, dsc_state_t.postMuxNumBits, dsc_state_t.postMuxNumBits, dsc_state_t.prevLinePred, dsc_state_t.prevQp, dsc_state_t.prevQp, dsc_state_t.primaryQp, dsc_state_t.rcXformOffset, dsc_state_t.rcXformOffset, dsc_state_t.seSizeFifo, dsc_state_t.seSizeFifo, dsc_state_t.shifter, dsc_state_t.sliceWidth, dsc_state_t.sliceWidth, dsc_state_t.sliceWidth, dsc_state_t.sliceWidth, dsc_state_t.sliceWidth, dsc_state_t.sliceWidth, dsc_state_t.sliceWidth, dsc_state_t.sliceWidth, dsc_state_t.sliceWidth, dsc_state_t.sliceWidth, dsc_state_t.sliceWidth, dsc_state_t.stQp, dsc_state_t.stQp, dsc_state_t.unitCType, dsc_state_t.unitsPerGroup, dsc_state_t.unitsPerGroup, dsc_state_t.unitsPerGroup, fifo_s.fullness, pic_s.bits, pic_s.h, pic_s.w, pic_s.w
  - AST loop count is 29; trip proofs are retained per loop

## `DSC_Decode`

- Source: `dsc_codec.c:3129`
- Clang USR: `c:@F@DSC_Decode`
- Return: `void`; parameters: `dsc_cfg: dsc_cfg_t *`, `p_out: pic_t *`, `cmpr_buf: unsigned char *`, `temp_pic: pic_t **`
- Callers: main
- Callees: DSC_Algorithm
- Global read/write: 0/0; field read/write: 0/0
- Pointer modes: dsc_cfg=UNKNOWN, p_out=UNKNOWN, cmpr_buf=UNKNOWN, temp_pic=UNKNOWN
- Loops: 0; fixed counts: UNKNOWN
- Effects: `{"assert": false, "file_io": false, "indirect_call": false, "logging": false, "malloc": false}`
- Proposal: **COMPOSITE_COMB_CANDIDATE**; purity=False; combinational=True
- Classification evidence:
  - AST observed no global/field/pointee writes
  - AST pointer modes: ['UNKNOWN', 'UNKNOWN', 'UNKNOWN', 'UNKNOWN']
  - AST observed no loop

## `DSC_Encode`

- Source: `dsc_codec.c:3118`
- Clang USR: `c:@F@DSC_Encode`
- Return: `int`; parameters: `dsc_cfg: dsc_cfg_t *`, `p_in: pic_t *`, `p_out: pic_t *`, `cmpr_buf: unsigned char *`, `temp_pic: pic_t **`, `chunk_sizes: int *`
- Callers: main
- Callees: DSC_Algorithm
- Global read/write: 0/0; field read/write: 0/0
- Pointer modes: dsc_cfg=UNKNOWN, p_in=UNKNOWN, p_out=UNKNOWN, cmpr_buf=UNKNOWN, temp_pic=UNKNOWN, chunk_sizes=UNKNOWN
- Loops: 0; fixed counts: UNKNOWN
- Effects: `{"assert": false, "file_io": false, "indirect_call": false, "logging": false, "malloc": false}`
- Proposal: **COMPOSITE_COMB_CANDIDATE**; purity=False; combinational=True
- Classification evidence:
  - AST observed no global/field/pointee writes
  - AST pointer modes: ['UNKNOWN', 'UNKNOWN', 'UNKNOWN', 'UNKNOWN', 'UNKNOWN', 'UNKNOWN']
  - AST observed no loop

## `Err`

- Source: `logging.c:94`
- Clang USR: `c:@F@Err`
- Return: `void`; parameters: `format: char *`
- Callers: readppm, str2d, str2i, str2ll, str2p, str2ui, str2ull, parse_cfgfile
- Callees: __builtin_va_end, __builtin_va_start, exit, fprintf, vfprintf
- Global read/write: 3/0; field read/write: 0/0
- Pointer modes: format=UNKNOWN
- Loops: 0; fixed counts: UNKNOWN
- Effects: `{"assert": false, "file_io": true, "indirect_call": false, "logging": false, "malloc": false}`
- Proposal: **IO_OR_DEBUG**; purity=False; combinational=False
- Classification evidence:
  - AST observed no global/field/pointee writes
  - AST pointer modes: ['UNKNOWN']
  - AST observed global reads: __stderrp, __stderrp, __stderrp
  - AST observed no loop

## `ErrorHandler`

- Source: `dsc_codec.c:171`
- Clang USR: `c:@F@ErrorHandler`
- Return: `void`; parameters: `dsc_cfg: dsc_cfg_t *`, `dsc_state: dsc_state_t *`, `hPos: int`, `vPos: int`, `op: pic_t *`
- Callers: DSC_Algorithm
- Callees: NONE
- Global read/write: 0/0; field read/write: 16/13
- Pointer modes: dsc_cfg=WRITES_THROUGH, dsc_state=READ_ONLY, op=WRITES_THROUGH
- Loops: 3; fixed counts: UNKNOWN
- Effects: `{"assert": false, "file_io": false, "indirect_call": false, "logging": false, "malloc": false}`
- Proposal: **STATEFUL**; purity=False; combinational=False
- Classification evidence:
  - AST observed writes or mutable-state effects: ['data_u.yuv', 'dsc_cfg', 'dsc_cfg_t.native_422', 'op', 'pic_s.data', 'yuv_s.u', 'yuv_s.v', 'yuv_s.y']
  - AST pointer modes: ['READ_ONLY', 'WRITES_THROUGH', 'WRITES_THROUGH']
  - AST observed field reads: dsc_cfg_t.native_420, dsc_cfg_t.native_422, dsc_cfg_t.native_422, dsc_cfg_t.slice_height, dsc_cfg_t.xstart, dsc_cfg_t.xstart, dsc_cfg_t.ystart, dsc_state_t.numComponents, dsc_state_t.prevLine, dsc_state_t.prevLine, dsc_state_t.prevLine, dsc_state_t.prevLine, dsc_state_t.sliceWidth, pic_s.h, pic_s.w, pic_s.w
  - AST loop count is 3; trip proofs are retained per loop

## `EscapeCodeSize`

- Source: `dsc_codec.c:443`
- Clang USR: `c:@F@EscapeCodeSize`
- Return: `int`; parameters: `dsc_cfg: dsc_cfg_t *`, `dsc_state: dsc_state_t *`, `qp: int`
- Callers: VLCUnit, VLDUnit
- Callees: MapQpToQlevel
- Global read/write: 0/0; field read/write: 1/0
- Pointer modes: dsc_cfg=UNKNOWN, dsc_state=UNKNOWN
- Loops: 0; fixed counts: UNKNOWN
- Effects: `{"assert": false, "file_io": false, "indirect_call": false, "logging": false, "malloc": false}`
- Proposal: **COMPOSITE_COMB_CANDIDATE**; purity=False; combinational=True
- Classification evidence:
  - AST observed no global/field/pointee writes
  - AST pointer modes: ['UNKNOWN', 'UNKNOWN']
  - AST observed field reads: dsc_state_t.cpntBitDepth
  - AST observed no loop

## `EstimateBitsForGroup`

- Source: `dsc_codec.c:390`
- Clang USR: `c:@F@EstimateBitsForGroup`
- Return: `int`; parameters: `dsc_cfg: dsc_cfg_t *`, `dsc_state: dsc_state_t *`
- Callers: IchDecision
- Callees: FindResidualSize, GetQpAdjPredSize, MaxResidualSize
- Global read/write: 0/0; field read/write: 13/0
- Pointer modes: dsc_cfg=UNKNOWN, dsc_state=UNKNOWN
- Loops: 4; fixed counts: 4, 3
- Effects: `{"assert": false, "file_io": false, "indirect_call": false, "logging": false, "malloc": false}`
- Proposal: **COMPOSITE_COMB_CANDIDATE**; purity=False; combinational=True
- Classification evidence:
  - AST observed no global/field/pointee writes
  - AST pointer modes: ['UNKNOWN', 'UNKNOWN']
  - AST observed field reads: dsc_state_t.hPos, dsc_state_t.pixelsInGroup, dsc_state_t.prevIchSelected, dsc_state_t.primaryQp, dsc_state_t.primaryQp, dsc_state_t.primaryQp, dsc_state_t.quantizedResidual, dsc_state_t.sliceWidth, dsc_state_t.unitCType, dsc_state_t.unitCType, dsc_state_t.unitStartHPos, dsc_state_t.unitsPerGroup, dsc_state_t.unitsPerGroup
  - AST loop count is 4; trip proofs are retained per loop

## `FindMidpoint`

- Source: `dsc_codec.c:906`
- Clang USR: `c:@F@FindMidpoint`
- Return: `int`; parameters: `dsc_state: dsc_state_t *`, `cpnt: int`, `qlevel: int`
- Callers: PredictionLoop
- Callees: NONE
- Global read/write: 0/0; field read/write: 2/0
- Pointer modes: dsc_state=READ_ONLY
- Loops: 0; fixed counts: UNKNOWN
- Effects: `{"assert": false, "file_io": false, "indirect_call": false, "logging": false, "malloc": false}`
- Proposal: **PURE_COMB_CANDIDATE**; purity=True; combinational=True
- Classification evidence:
  - AST observed no global/field/pointee writes
  - AST pointer modes: ['READ_ONLY']
  - AST observed field reads: dsc_state_t.cpntBitDepth, dsc_state_t.leftRecon
  - AST observed no loop
  - No direct calls and no non-const global read were observed

## `FindResidualSize`

- Source: `dsc_codec.c:1078`
- Clang USR: `c:@F@FindResidualSize`
- Return: `int`; parameters: `eq: int`
- Callers: EstimateBitsForGroup, PredictionLoop, UsingMidpoint, VLCUnit, VLDUnit
- Callees: printf
- Global read/write: 0/0; field read/write: 0/0
- Pointer modes: NONE
- Loops: 0; fixed counts: UNKNOWN
- Effects: `{"assert": false, "file_io": false, "indirect_call": false, "logging": true, "malloc": false}`
- Proposal: **IO_OR_DEBUG**; purity=False; combinational=False
- Classification evidence:
  - AST observed no global/field/pointee writes
  - AST observed no loop

## `FlatnessAdjustment`

- Source: `dsc_codec.c:2510`
- Clang USR: `c:@F@FlatnessAdjustment`
- Return: `void`; parameters: `dsc_cfg: dsc_cfg_t *`, `dsc_state: dsc_state_t *`, `hPos: int`, `qp: int`, `new_quant: int`
- Callers: DSC_Algorithm
- Callees: IsFlatnessInfoSent, IsOrigFlatHIndex
- Global read/write: 0/0; field read/write: 37/19
- Pointer modes: dsc_cfg=UNKNOWN, dsc_state=WRITES_THROUGH
- Loops: 1; fixed counts: UNKNOWN
- Effects: `{"assert": false, "file_io": false, "indirect_call": false, "logging": false, "malloc": false}`
- Proposal: **STATEFUL**; purity=False; combinational=False
- Classification evidence:
  - AST observed writes or mutable-state effects: ['dsc_state', 'dsc_state_t.firstFlat', 'dsc_state_t.flatnessType', 'dsc_state_t.origIsFlat', 'dsc_state_t.prevFirstFlat', 'dsc_state_t.prevFlatnessType', 'dsc_state_t.prevIsFlat', 'dsc_state_t.prevQp', 'dsc_state_t.stQp']
  - AST pointer modes: ['UNKNOWN', 'WRITES_THROUGH']
  - AST observed field reads: dsc_cfg_t.dsc_version_minor, dsc_cfg_t.rc_range_parameters, dsc_cfg_t.rc_range_parameters, dsc_cfg_t.somewhat_flat_qp_delta, dsc_cfg_t.somewhat_flat_qp_delta, dsc_cfg_t.somewhat_flat_qp_delta, dsc_cfg_t.somewhat_flat_qp_thresh, dsc_cfg_t.somewhat_flat_qp_thresh, dsc_cfg_t.very_flat_qp, dsc_cfg_t.very_flat_qp, dsc_cfg_t.very_flat_qp, dsc_range_cfg_t.range_max_qp, dsc_range_cfg_t.range_max_qp, dsc_state_t.firstFlat, dsc_state_t.firstFlat, dsc_state_t.firstFlat, dsc_state_t.flatnessType, dsc_state_t.flatnessType, dsc_state_t.groupCount, dsc_state_t.groupCount, dsc_state_t.groupCount, dsc_state_t.groupCount, dsc_state_t.isEncoder, dsc_state_t.origIsFlat, dsc_state_t.origIsFlat, dsc_state_t.pixelsInGroup, dsc_state_t.prevFirstFlat, dsc_state_t.prevFlatnessType, dsc_state_t.prevIsFlat, dsc_state_t.prevQp, dsc_state_t.primaryQp, dsc_state_t.primaryQp, dsc_state_t.primaryQp, dsc_state_t.primaryQp, dsc_state_t.sliceWidth, dsc_state_t.stQp, dsc_state_t.stQp
  - AST loop count is 1; trip proofs are retained per loop

## `GetBits`

- Source: `multiplex.c:104`
- Clang USR: `c:@F@GetBits`
- Return: `int`; parameters: `dsc_cfg: dsc_cfg_t *`, `dsc_state: dsc_state_t *`, `unit: int`, `nbits: int`, `sign_extend: int`, `buf: unsigned char *`
- Callers: VLDUnit
- Callees: fifo_get_bits
- Global read/write: 0/0; field read/write: 1/1
- Pointer modes: dsc_cfg=READ_ONLY, dsc_state=UNKNOWN, buf=READ_ONLY
- Loops: 0; fixed counts: UNKNOWN
- Effects: `{"assert": false, "file_io": false, "indirect_call": false, "logging": false, "malloc": false}`
- Proposal: **STATEFUL**; purity=False; combinational=False
- Classification evidence:
  - AST observed writes or mutable-state effects: ['dsc_state_t.numBits']
  - AST pointer modes: ['READ_ONLY', 'READ_ONLY', 'UNKNOWN']
  - AST observed field reads: dsc_state_t.shifter
  - AST observed no loop

## `GetQpAdjPredSize`

- Source: `dsc_codec.c:278`
- Clang USR: `c:@F@GetQpAdjPredSize`
- Return: `int`; parameters: `dsc_cfg: dsc_cfg_t *`, `dsc_state: dsc_state_t *`, `unit: int`
- Callers: EstimateBitsForGroup, VLCUnit, VLDUnit
- Callees: MapQpToQlevel, MaxResidualSize
- Global read/write: 0/0; field read/write: 5/0
- Pointer modes: dsc_cfg=UNKNOWN, dsc_state=UNKNOWN
- Loops: 0; fixed counts: UNKNOWN
- Effects: `{"assert": false, "file_io": false, "indirect_call": false, "logging": false, "malloc": false}`
- Proposal: **COMPOSITE_COMB_CANDIDATE**; purity=False; combinational=True
- Classification evidence:
  - AST observed no global/field/pointee writes
  - AST pointer modes: ['UNKNOWN', 'UNKNOWN']
  - AST observed field reads: dsc_state_t.predictedSize, dsc_state_t.prevPrimaryQp, dsc_state_t.primaryQp, dsc_state_t.primaryQp, dsc_state_t.unitCType
  - AST observed no loop

## `HistoryLookup`

- Source: `dsc_codec.c:543`
- Clang USR: `c:@F@HistoryLookup`
- Return: `void`; parameters: `dsc_cfg: dsc_cfg_t *`, `dsc_state: dsc_state_t *`, `entry: int`, `p: unsigned int *`, `hPos: int`, `first_line_flag: int`, `is_odd_line: int`
- Callers: DSC_Algorithm, IsOrigWithinQerr, PickBestHistoryValue, UpdateHistoryElement
- Callees: __builtin___memset_chk, __builtin_object_size
- Global read/write: 0/0; field read/write: 29/0
- Pointer modes: dsc_cfg=READ_ONLY, dsc_state=READ_ONLY, p=WRITES_THROUGH
- Loops: 1; fixed counts: UNKNOWN
- Effects: `{"assert": false, "file_io": false, "indirect_call": false, "logging": false, "malloc": false}`
- Proposal: **STATEFUL**; purity=False; combinational=False
- Classification evidence:
  - AST observed writes or mutable-state effects: ['p']
  - AST pointer modes: ['READ_ONLY', 'READ_ONLY', 'WRITES_THROUGH']
  - AST observed field reads: dsc_cfg_t.native_420, dsc_cfg_t.native_420, dsc_cfg_t.native_422, dsc_cfg_t.native_422, dsc_history_t.pixels, dsc_state_t.history, dsc_state_t.numComponents, dsc_state_t.pixelsInGroup, dsc_state_t.pixelsInGroup, dsc_state_t.pixelsInGroup, dsc_state_t.prevLine, dsc_state_t.prevLine, dsc_state_t.prevLine, dsc_state_t.prevLine, dsc_state_t.prevLine, dsc_state_t.prevLine, dsc_state_t.prevLine, dsc_state_t.prevLine, dsc_state_t.prevLine, dsc_state_t.prevLine, dsc_state_t.prevLine, dsc_state_t.prevLine, dsc_state_t.prevLine, dsc_state_t.prevLine, dsc_state_t.prevLine, dsc_state_t.prevLine, dsc_state_t.prevLine, dsc_state_t.sliceWidth, dsc_state_t.sliceWidth
  - AST loop count is 1; trip proofs are retained per loop

## `IchDecision`

- Source: `dsc_codec.c:484`
- Clang USR: `c:@F@IchDecision`
- Return: `int`; parameters: `dsc_cfg: dsc_cfg_t *`, `dsc_state: dsc_state_t *`, `adj_predicted_size: int`, `alt_pfx: int`, `alt_size_to_generate: int`
- Callers: VLCUnit
- Callees: EstimateBitsForGroup, IsOrigFlatHIndex, UsingMidpoint, ceil_log2
- Global read/write: 0/0; field read/write: 12/0
- Pointer modes: dsc_cfg=UNKNOWN, dsc_state=UNKNOWN
- Loops: 3; fixed counts: UNKNOWN
- Effects: `{"assert": false, "file_io": false, "indirect_call": false, "logging": true, "malloc": false}`
- Proposal: **IO_OR_DEBUG**; purity=False; combinational=False
- Classification evidence:
  - AST observed no global/field/pointee writes
  - AST pointer modes: ['UNKNOWN', 'UNKNOWN']
  - AST observed field reads: dsc_cfg_t.dsc_version_minor, dsc_cfg_t.dsc_version_minor, dsc_state_t.hPos, dsc_state_t.ichIndicesInGroup, dsc_state_t.maxError, dsc_state_t.maxIchError, dsc_state_t.maxMidError, dsc_state_t.prevIchSelected, dsc_state_t.unitCType, dsc_state_t.unitsPerGroup, dsc_state_t.unitsPerGroup, dsc_state_t.unitsPerGroup
  - AST loop count is 3; trip proofs are retained per loop

## `InitializeDSCState`

- Source: `dsc_codec.c:2056`
- Clang USR: `c:@F@InitializeDSCState`
- Return: `dsc_state_t *`; parameters: `dsc_cfg: dsc_cfg_t *`, `dsc_state: dsc_state_t *`
- Callers: DSC_Algorithm
- Callees: __assert_rtn, __builtin___memset_chk, __builtin_expect, __builtin_object_size, fifo_init, malloc
- Global read/write: 10/0; field read/write: 35/63
- Pointer modes: dsc_cfg=UNKNOWN, dsc_state=WRITES_THROUGH
- Loops: 10; fixed counts: 4, 3, 6, 4, 13, 3, 4, 32
- Effects: `{"assert": true, "file_io": false, "indirect_call": false, "logging": false, "malloc": true}`
- Proposal: **IO_OR_DEBUG**; purity=False; combinational=False
- Classification evidence:
  - AST observed writes or mutable-state effects: ['dsc_history_t.pixels', 'dsc_history_t.valid', 'dsc_state', 'dsc_state_t.bufferFullness', 'dsc_state_t.firstFlat', 'dsc_state_t.history', 'dsc_state_t.ichIndexUnitMap', 'dsc_state_t.ichIndicesInGroup', 'dsc_state_t.ichSelected', 'dsc_state_t.lastErr', 'dsc_state_t.maxSeSize', 'dsc_state_t.native420', 'dsc_state_t.nonFirstLineBpgTarget', 'dsc_state_t.numBits', 'dsc_state_t.numComponents', 'dsc_state_t.numSsps', 'dsc_state_t.pixelsInGroup', 'dsc_state_t.predictedSize', 'dsc_state_t.prevFirstFlat', 'dsc_state_t.prevLinePred', 'dsc_state_t.prevNumBits', 'dsc_state_t.prevPrimaryQp', 'dsc_state_t.prevQp', 'dsc_state_t.primaryQp', 'dsc_state_t.quantTableChroma', 'dsc_state_t.quantTableLuma', 'dsc_state_t.quantizedResidual', 'dsc_state_t.rcSizeGroup', 'dsc_state_t.rcSizeUnit', 'dsc_state_t.rcXformOffset', 'dsc_state_t.sliceWidth', 'dsc_state_t.stQp', 'dsc_state_t.throttleFrac', 'dsc_state_t.throttleInt', 'dsc_state_t.unitCType', 'dsc_state_t.unitSspMap', 'dsc_state_t.unitStartHPos', 'dsc_state_t.unitsPerGroup']
  - AST pointer modes: ['UNKNOWN', 'WRITES_THROUGH']
  - AST observed global reads: qlevel_chroma_10bpc, qlevel_chroma_12bpc, qlevel_chroma_14bpc, qlevel_chroma_16bpc, qlevel_chroma_8bpc, qlevel_luma_10bpc, qlevel_luma_12bpc, qlevel_luma_14bpc, qlevel_luma_16bpc, qlevel_luma_8bpc
  - AST observed field reads: dsc_cfg_t.bits_per_component, dsc_cfg_t.bits_per_component, dsc_cfg_t.bits_per_component, dsc_cfg_t.bits_per_component, dsc_cfg_t.bits_per_component, dsc_cfg_t.bits_per_component, dsc_cfg_t.bits_per_component, dsc_cfg_t.bits_per_component, dsc_cfg_t.bits_per_component, dsc_cfg_t.bits_per_component, dsc_cfg_t.convert_rgb, dsc_cfg_t.convert_rgb, dsc_cfg_t.initial_offset, dsc_cfg_t.mux_word_size, dsc_cfg_t.mux_word_size, dsc_cfg_t.mux_word_size, dsc_cfg_t.native_420, dsc_cfg_t.native_420, dsc_cfg_t.native_422, dsc_cfg_t.native_422, dsc_cfg_t.second_line_ofs_adj, dsc_cfg_t.slice_width, dsc_cfg_t.slice_width, dsc_history_t.valid, dsc_state_t.encBalanceFifo, dsc_state_t.history, dsc_state_t.numComponents, dsc_state_t.numComponents, dsc_state_t.pixelsInGroup, dsc_state_t.prevLinePred, dsc_state_t.prevLinePred, dsc_state_t.seSizeFifo, dsc_state_t.shifter, dsc_state_t.sliceWidth, dsc_state_t.sliceWidth
  - AST loop count is 10; trip proofs are retained per loop

## `IsFlatnessInfoSent`

- Source: `dsc_codec.c:1116`
- Clang USR: `c:@F@IsFlatnessInfoSent`
- Return: `int`; parameters: `dsc_cfg: dsc_cfg_t *`, `qp: int`
- Callers: FlatnessAdjustment, VLCUnit, VLDUnit
- Callees: NONE
- Global read/write: 0/0; field read/write: 2/0
- Pointer modes: dsc_cfg=READ_ONLY
- Loops: 0; fixed counts: UNKNOWN
- Effects: `{"assert": false, "file_io": false, "indirect_call": false, "logging": false, "malloc": false}`
- Proposal: **CONFIG_HELPER**; purity=False; combinational=True
- Classification evidence:
  - AST observed no global/field/pointee writes
  - AST pointer modes: ['READ_ONLY']
  - AST observed field reads: dsc_cfg_t.flatness_max_qp, dsc_cfg_t.flatness_min_qp
  - AST observed no loop
  - The proposal is per-field input use; the containing struct is not classified as static configuration

## `IsOrigFlatHIndex`

- Source: `dsc_codec.c:1126`
- Clang USR: `c:@F@IsOrigFlatHIndex`
- Return: `int`; parameters: `dsc_cfg: dsc_cfg_t *`, `dsc_state: dsc_state_t *`, `hPos: int`
- Callers: FlatnessAdjustment, IchDecision
- Callees: MapQpToQlevel
- Global read/write: 2/0; field read/write: 11/0
- Pointer modes: dsc_cfg=UNKNOWN, dsc_state=UNKNOWN
- Loops: 5; fixed counts: UNKNOWN
- Effects: `{"assert": false, "file_io": false, "indirect_call": false, "logging": false, "malloc": false}`
- Proposal: **CONFIG_HELPER**; purity=False; combinational=True
- Classification evidence:
  - AST observed no global/field/pointee writes
  - AST pointer modes: ['UNKNOWN', 'UNKNOWN']
  - AST observed global reads: QuantDivisor, QuantDivisor
  - AST observed field reads: dsc_cfg_t.flatness_det_thresh, dsc_cfg_t.flatness_det_thresh, dsc_cfg_t.somewhat_flat_qp_delta, dsc_state_t.numComponents, dsc_state_t.numComponents, dsc_state_t.numComponents, dsc_state_t.origLine, dsc_state_t.origLine, dsc_state_t.primaryQp, dsc_state_t.sliceWidth, dsc_state_t.sliceWidth
  - AST loop count is 5; trip proofs are retained per loop
  - The proposal is per-field input use; the containing struct is not classified as static configuration

## `IsOrigWithinQerr`

- Source: `dsc_codec.c:611`
- Clang USR: `c:@F@IsOrigWithinQerr`
- Return: `int`; parameters: `dsc_cfg: dsc_cfg_t *`, `dsc_state: dsc_state_t *`, `hPos: int`, `vPos: int`, `qp: int`, `sampModCnt: int`
- Callers: DSC_Algorithm
- Callees: HistoryLookup, MapQpToQlevel, abs
- Global read/write: 1/0; field read/write: 11/4
- Pointer modes: dsc_cfg=UNKNOWN, dsc_state=WRITES_THROUGH
- Loops: 4; fixed counts: 7
- Effects: `{"assert": false, "file_io": false, "indirect_call": false, "logging": false, "malloc": false}`
- Proposal: **STATEFUL**; purity=False; combinational=False
- Classification evidence:
  - AST observed writes or mutable-state effects: ['dsc_history_t.valid', 'dsc_state', 'dsc_state_t.history', 'dsc_state_t.origWithinQerr']
  - AST pointer modes: ['UNKNOWN', 'WRITES_THROUGH']
  - AST observed global reads: QuantDivisor
  - AST observed field reads: dsc_cfg_t.bits_per_component, dsc_cfg_t.native_420, dsc_cfg_t.native_420, dsc_cfg_t.native_420, dsc_history_t.valid, dsc_state_t.history, dsc_state_t.numComponents, dsc_state_t.numComponents, dsc_state_t.origLine, dsc_state_t.vPos, dsc_state_t.vPos
  - AST loop count is 4; trip proofs are retained per loop

## `MapQpToQlevel`

- Source: `dsc_codec.c:221`
- Clang USR: `c:@F@MapQpToQlevel`
- Return: `int`; parameters: `dsc_cfg: dsc_cfg_t *`, `dsc_state: dsc_state_t *`, `qp: int`, `cpnt: int`
- Callers: EscapeCodeSize, GetQpAdjPredSize, IsOrigFlatHIndex, IsOrigWithinQerr, MaxResidualSize, PredictionLoop, UsingMidpoint, VLCUnit, VLDUnit
- Callees: NONE
- Global read/write: 0/0; field read/write: 7/0
- Pointer modes: dsc_cfg=READ_ONLY, dsc_state=READ_ONLY
- Loops: 0; fixed counts: UNKNOWN
- Effects: `{"assert": false, "file_io": false, "indirect_call": false, "logging": false, "malloc": false}`
- Proposal: **CONFIG_HELPER**; purity=False; combinational=True
- Classification evidence:
  - AST observed no global/field/pointee writes
  - AST pointer modes: ['READ_ONLY', 'READ_ONLY']
  - AST observed field reads: dsc_cfg_t.dsc_version_minor, dsc_cfg_t.native_420, dsc_state_t.cpntBitDepth, dsc_state_t.cpntBitDepth, dsc_state_t.quantTableChroma, dsc_state_t.quantTableLuma, dsc_state_t.quantTableLuma
  - AST observed no loop
  - The proposal is per-field input use; the containing struct is not classified as static configuration

## `MaxResidualSize`

- Source: `dsc_codec.c:263`
- Clang USR: `c:@F@MaxResidualSize`
- Return: `int`; parameters: `dsc_cfg: dsc_cfg_t *`, `dsc_state: dsc_state_t *`, `cpnt: int`, `qp: int`
- Callers: EstimateBitsForGroup, GetQpAdjPredSize, PredictionLoop, VLCUnit, VLDUnit
- Callees: MapQpToQlevel
- Global read/write: 0/0; field read/write: 1/0
- Pointer modes: dsc_cfg=UNKNOWN, dsc_state=UNKNOWN
- Loops: 0; fixed counts: UNKNOWN
- Effects: `{"assert": false, "file_io": false, "indirect_call": false, "logging": false, "malloc": false}`
- Proposal: **COMPOSITE_COMB_CANDIDATE**; purity=False; combinational=True
- Classification evidence:
  - AST observed no global/field/pointee writes
  - AST pointer modes: ['UNKNOWN', 'UNKNOWN']
  - AST observed field reads: dsc_state_t.cpntBitDepth
  - AST observed no loop

## `PErr`

- Source: `logging.c:140`
- Clang USR: `c:@F@PErr`
- Return: `void`; parameters: `format: char *`
- Callers: easy_mkdir, parse_cfgfile
- Callees: __builtin_va_end, __builtin_va_start, exit, fprintf, perror, vfprintf
- Global read/write: 3/0; field read/write: 0/0
- Pointer modes: format=UNKNOWN
- Loops: 0; fixed counts: UNKNOWN
- Effects: `{"assert": false, "file_io": true, "indirect_call": false, "logging": true, "malloc": false}`
- Proposal: **IO_OR_DEBUG**; purity=False; combinational=False
- Classification evidence:
  - AST observed no global/field/pointee writes
  - AST pointer modes: ['UNKNOWN']
  - AST observed global reads: __stderrp, __stderrp, __stderrp
  - AST observed no loop

## `PickBestHistoryValue`

- Source: `dsc_codec.c:736`
- Clang USR: `c:@F@PickBestHistoryValue`
- Return: `int`; parameters: `dsc_cfg: dsc_cfg_t *`, `dsc_state: dsc_state_t *`, `hPos: int`, `orig: unsigned int *`
- Callers: DSC_Algorithm
- Callees: HistoryLookup, abs, printf
- Global read/write: 0/0; field read/write: 9/0
- Pointer modes: dsc_cfg=UNKNOWN, dsc_state=UNKNOWN, orig=READ_ONLY
- Loops: 1; fixed counts: 32
- Effects: `{"assert": false, "file_io": false, "indirect_call": false, "logging": true, "malloc": false}`
- Proposal: **IO_OR_DEBUG**; purity=False; combinational=False
- Classification evidence:
  - AST observed no global/field/pointee writes
  - AST pointer modes: ['READ_ONLY', 'UNKNOWN', 'UNKNOWN']
  - AST observed field reads: dsc_cfg_t.dsc_version_minor, dsc_cfg_t.native_420, dsc_cfg_t.native_420, dsc_cfg_t.native_422, dsc_history_t.valid, dsc_state_t.history, dsc_state_t.vPos, dsc_state_t.vPos, dsc_state_t.vPos
  - AST loop count is 1; trip proofs are retained per loop

## `PopulateOrigLine`

- Source: `dsc_codec.c:2294`
- Clang USR: `c:@F@PopulateOrigLine`
- Return: `void`; parameters: `dsc_cfg: dsc_cfg_t *`, `dsc_state: dsc_state_t *`, `ip: pic_t *`, `vPos: int`
- Callers: DSC_Algorithm
- Callees: NONE
- Global read/write: 0/0; field read/write: 37/8
- Pointer modes: dsc_cfg=READ_ONLY, dsc_state=WRITES_THROUGH, ip=READ_ONLY
- Loops: 2; fixed counts: UNKNOWN
- Effects: `{"assert": false, "file_io": false, "indirect_call": false, "logging": false, "malloc": false}`
- Proposal: **STATEFUL**; purity=False; combinational=False
- Classification evidence:
  - AST observed writes or mutable-state effects: ['dsc_state', 'dsc_state_t.origLine']
  - AST pointer modes: ['READ_ONLY', 'READ_ONLY', 'WRITES_THROUGH']
  - AST observed field reads: data_u.yuv, data_u.yuv, data_u.yuv, data_u.yuv, data_u.yuv, data_u.yuv, data_u.yuv, dsc_cfg_t.native_420, dsc_cfg_t.native_422, dsc_cfg_t.native_422, dsc_cfg_t.native_422, dsc_cfg_t.native_422, dsc_cfg_t.xstart, dsc_cfg_t.ystart, dsc_cfg_t.ystart, dsc_state_t.cpntBitDepth, dsc_state_t.numComponents, dsc_state_t.sliceWidth, dsc_state_t.sliceWidth, dsc_state_t.sliceWidth, pic_s.data, pic_s.data, pic_s.data, pic_s.data, pic_s.data, pic_s.data, pic_s.data, pic_s.h, pic_s.h, pic_s.w, yuv_s.u, yuv_s.u, yuv_s.v, yuv_s.v, yuv_s.y, yuv_s.y, yuv_s.y
  - AST loop count is 2; trip proofs are retained per loop

## `PredictSize`

- Source: `dsc_codec.c:1476`
- Clang USR: `c:@F@PredictSize`
- Return: `int`; parameters: `dsc_cfg: dsc_cfg_t *`, `req_size: int *`
- Callers: VLCUnit, VLDUnit
- Callees: NONE
- Global read/write: 0/0; field read/write: 0/0
- Pointer modes: dsc_cfg=READ_ONLY, req_size=READ_ONLY
- Loops: 0; fixed counts: UNKNOWN
- Effects: `{"assert": false, "file_io": false, "indirect_call": false, "logging": false, "malloc": false}`
- Proposal: **PURE_COMB_CANDIDATE**; purity=True; combinational=True
- Classification evidence:
  - AST observed no global/field/pointee writes
  - AST pointer modes: ['READ_ONLY', 'READ_ONLY']
  - AST observed no loop
  - No direct calls and no non-const global read were observed

## `PredictionLoop`

- Source: `dsc_codec.c:2361`
- Clang USR: `c:@F@PredictionLoop`
- Return: `void`; parameters: `dsc_cfg: dsc_cfg_t *`, `dsc_state: dsc_state_t *`, `hPos: int`, `vPos: int`, `sampModCnt: int`, `qp: int`
- Callers: DSC_Algorithm
- Callees: FindMidpoint, FindResidualSize, MapQpToQlevel, MaxResidualSize, QuantizeResidual, SamplePredict, __assert_rtn, __builtin_expect, abs, printf
- Global read/write: 3/0; field read/write: 33/9
- Pointer modes: dsc_cfg=UNKNOWN, dsc_state=WRITES_THROUGH
- Loops: 3; fixed counts: UNKNOWN
- Effects: `{"assert": true, "file_io": false, "indirect_call": false, "logging": true, "malloc": false}`
- Proposal: **IO_OR_DEBUG**; purity=False; combinational=False
- Classification evidence:
  - AST observed writes or mutable-state effects: ['dsc_state', 'dsc_state_t.currLine', 'dsc_state_t.maxError', 'dsc_state_t.maxMidError', 'dsc_state_t.midpointRecon', 'dsc_state_t.primaryQp', 'dsc_state_t.quantizedResidual', 'dsc_state_t.quantizedResidualMid']
  - AST pointer modes: ['UNKNOWN', 'WRITES_THROUGH']
  - AST observed global reads: g_verbose, g_verbose, g_verbose
  - AST observed field reads: dsc_cfg_t.bits_per_component, dsc_cfg_t.bits_per_component, dsc_cfg_t.full_ich_err_precision, dsc_cfg_t.full_ich_err_precision, dsc_cfg_t.native_420, dsc_state_t.cpntBitDepth, dsc_state_t.currLine, dsc_state_t.currLine, dsc_state_t.currLine, dsc_state_t.currLine, dsc_state_t.isEncoder, dsc_state_t.isEncoder, dsc_state_t.isEncoder, dsc_state_t.maxError, dsc_state_t.maxMidError, dsc_state_t.midpointRecon, dsc_state_t.midpointRecon, dsc_state_t.origLine, dsc_state_t.prevLine, dsc_state_t.prevLine, dsc_state_t.prevLine, dsc_state_t.prevLine, dsc_state_t.prevLinePred, dsc_state_t.quantizedResidual, dsc_state_t.quantizedResidualMid, dsc_state_t.quantizedResidualMid, dsc_state_t.quantizedResidualMid, dsc_state_t.quantizedResidualMid, dsc_state_t.unitCType, dsc_state_t.unitStartHPos, dsc_state_t.unitsPerGroup, dsc_state_t.useMidpoint, dsc_state_t.useMidpoint
  - AST loop count is 3; trip proofs are retained per loop

## `ProcessGroupDec`

- Source: `multiplex.c:159`
- Clang USR: `c:@F@ProcessGroupDec`
- Return: `void`; parameters: `dsc_cfg: dsc_cfg_t *`, `dsc_state: dsc_state_t *`, `buf: unsigned char *`
- Callers: VLDGroup
- Callees: fifo_put_bits, getbits
- Global read/write: 0/0; field read/write: 7/0
- Pointer modes: dsc_cfg=READ_ONLY, dsc_state=UNKNOWN, buf=UNKNOWN
- Loops: 2; fixed counts: UNKNOWN
- Effects: `{"assert": false, "file_io": false, "indirect_call": false, "logging": false, "malloc": false}`
- Proposal: **CONFIG_HELPER**; purity=False; combinational=True
- Classification evidence:
  - AST observed no global/field/pointee writes
  - AST pointer modes: ['READ_ONLY', 'UNKNOWN', 'UNKNOWN']
  - AST observed field reads: dsc_cfg_t.mux_word_size, dsc_state_t.maxSeSize, dsc_state_t.numSsps, dsc_state_t.postMuxNumBits, dsc_state_t.shifter, dsc_state_t.shifter, fifo_s.fullness
  - AST loop count is 2; trip proofs are retained per loop
  - The proposal is per-field input use; the containing struct is not classified as static configuration

## `ProcessGroupEnc`

- Source: `multiplex.c:116`
- Clang USR: `c:@F@ProcessGroupEnc`
- Return: `void`; parameters: `dsc_cfg: dsc_cfg_t *`, `dsc_state: dsc_state_t *`, `buf: unsigned char *`
- Callers: DSC_Algorithm, VLCGroup
- Callees: fifo_get_bits, fifo_put_bits, getbits, putbits
- Global read/write: 0/0; field read/write: 15/0
- Pointer modes: dsc_cfg=READ_ONLY, dsc_state=UNKNOWN, buf=UNKNOWN
- Loops: 2; fixed counts: UNKNOWN
- Effects: `{"assert": false, "file_io": false, "indirect_call": false, "logging": false, "malloc": false}`
- Proposal: **CONFIG_HELPER**; purity=False; combinational=True
- Classification evidence:
  - AST observed no global/field/pointee writes
  - AST pointer modes: ['READ_ONLY', 'UNKNOWN', 'UNKNOWN']
  - AST observed field reads: dsc_cfg_t.mux_word_size, dsc_state_t.encBalanceFifo, dsc_state_t.encBalanceFifo, dsc_state_t.encBalanceFifo, dsc_state_t.isEncoder, dsc_state_t.maxSeSize, dsc_state_t.numBits, dsc_state_t.numSsps, dsc_state_t.postMuxNumBits, dsc_state_t.seSizeFifo, dsc_state_t.shifter, dsc_state_t.shifter, dsc_state_t.shifter, fifo_s.fullness, fifo_s.fullness
  - AST loop count is 2; trip proofs are retained per loop
  - The proposal is per-field input use; the containing struct is not classified as static configuration

## `Qp2Qlevel`

- Source: `codec_main.c:816`
- Clang USR: `c:@F@Qp2Qlevel`
- Return: `int`; parameters: `dsc_cfg: dsc_cfg_t *`, `qp: int`, `cpnt: int`
- Callers: check_qp_for_overflow
- Callees: NONE
- Global read/write: 10/0; field read/write: 5/0
- Pointer modes: dsc_cfg=READ_ONLY
- Loops: 0; fixed counts: UNKNOWN
- Effects: `{"assert": false, "file_io": false, "indirect_call": false, "logging": false, "malloc": false}`
- Proposal: **CONFIG_HELPER**; purity=False; combinational=True
- Classification evidence:
  - AST observed no global/field/pointee writes
  - AST pointer modes: ['READ_ONLY']
  - AST observed global reads: qlevel_chroma_10bpc, qlevel_chroma_12bpc, qlevel_chroma_14bpc, qlevel_chroma_16bpc, qlevel_chroma_8bpc, qlevel_luma_10bpc, qlevel_luma_12bpc, qlevel_luma_14bpc, qlevel_luma_16bpc, qlevel_luma_8bpc
  - AST observed field reads: dsc_cfg_t.bits_per_component, dsc_cfg_t.bits_per_component, dsc_cfg_t.convert_rgb, dsc_cfg_t.dsc_version_minor, dsc_cfg_t.native_420
  - AST observed no loop
  - The proposal is per-field input use; the containing struct is not classified as static configuration

## `QuantizeResidual`

- Source: `dsc_codec.c:245`
- Clang USR: `c:@F@QuantizeResidual`
- Return: `int`; parameters: `e: int`, `qlevel: int`
- Callers: PredictionLoop
- Callees: NONE
- Global read/write: 2/0; field read/write: 0/0
- Pointer modes: NONE
- Loops: 0; fixed counts: UNKNOWN
- Effects: `{"assert": false, "file_io": false, "indirect_call": false, "logging": false, "malloc": false}`
- Proposal: **PURE_COMB_CANDIDATE**; purity=True; combinational=True
- Classification evidence:
  - AST observed no global/field/pointee writes
  - AST observed global reads: QuantOffset, QuantOffset
  - AST observed no loop
  - No direct calls and no non-const global read were observed

## `RateControl`

- Source: `dsc_codec.c:1242`
- Clang USR: `c:@F@RateControl`
- Return: `void`; parameters: `dsc_cfg: dsc_cfg_t *`, `dsc_state: dsc_state_t *`, `throttle_offset: int`, `bpg_offset: int`, `group_count: int`, `scale: int`, `group_size: int`
- Callers: DSC_Algorithm
- Callees: RemoveBitsEncoderBuffer, exit, fprintf, printf
- Global read/write: 6/0; field read/write: 92/15
- Pointer modes: dsc_cfg=UNKNOWN, dsc_state=WRITES_THROUGH
- Loops: 3; fixed counts: UNKNOWN
- Effects: `{"assert": false, "file_io": true, "indirect_call": false, "logging": true, "malloc": false}`
- Proposal: **IO_OR_DEBUG**; purity=False; combinational=False
- Classification evidence:
  - AST observed writes or mutable-state effects: ['dsc_state', 'dsc_state_t.bitSaveMode', 'dsc_state_t.errorOccurred', 'dsc_state_t.mppState', 'dsc_state_t.pixelCount', 'dsc_state_t.prevQp', 'dsc_state_t.prevRange', 'dsc_state_t.rcSizeGroup', 'dsc_state_t.stQp']
  - AST pointer modes: ['UNKNOWN', 'WRITES_THROUGH']
  - AST observed global reads: g_fp_dbg, g_fp_dbg, g_fp_dbg, g_fp_dbg, g_fp_dbg, g_fp_dbg
  - AST observed field reads: dsc_cfg_t.bits_per_component, dsc_cfg_t.bits_per_pixel, dsc_cfg_t.bits_per_pixel, dsc_cfg_t.dsc_version_minor, dsc_cfg_t.dsc_version_minor, dsc_cfg_t.dsc_version_minor, dsc_cfg_t.dsc_version_minor, dsc_cfg_t.dsc_version_minor, dsc_cfg_t.dsc_version_minor, dsc_cfg_t.dsc_version_minor, dsc_cfg_t.dsc_version_minor, dsc_cfg_t.dsc_version_minor, dsc_cfg_t.dsc_version_minor, dsc_cfg_t.initial_xmit_delay, dsc_cfg_t.native_420, dsc_cfg_t.native_422, dsc_cfg_t.native_422, dsc_cfg_t.rc_buf_thresh, dsc_cfg_t.rc_edge_factor, dsc_cfg_t.rc_edge_factor, dsc_cfg_t.rc_model_size, dsc_cfg_t.rc_model_size, dsc_cfg_t.rc_quant_incr_limit0, dsc_cfg_t.rc_quant_incr_limit1, dsc_cfg_t.rc_range_parameters, dsc_cfg_t.rc_tgt_offset_hi, dsc_cfg_t.rc_tgt_offset_lo, dsc_cfg_t.rcb_bits, dsc_cfg_t.rcb_bits, dsc_range_cfg_t.range_bpg_offset, dsc_range_cfg_t.range_bpg_offset, dsc_range_cfg_t.range_max_qp, dsc_range_cfg_t.range_max_qp, dsc_range_cfg_t.range_max_qp, dsc_range_cfg_t.range_min_qp, dsc_range_cfg_t.range_min_qp, dsc_state_t.bitSaveMode, dsc_state_t.bitSaveMode, dsc_state_t.bitSaveMode, dsc_state_t.bitSaveMode, dsc_state_t.bufferFullness, dsc_state_t.bufferFullness, dsc_state_t.bufferFullness, dsc_state_t.bufferFullness, dsc_state_t.bufferFullness, dsc_state_t.bufferFullness, dsc_state_t.bufferFullness, dsc_state_t.bufferFullness, dsc_state_t.bufferFullness, dsc_state_t.codedGroupSize, dsc_state_t.codedGroupSize, dsc_state_t.codedGroupSize, dsc_state_t.codedGroupSize, dsc_state_t.cpntBitDepth, dsc_state_t.cpntBitDepth, dsc_state_t.firstFlat, dsc_state_t.ichSelected, dsc_state_t.ichSelected, dsc_state_t.ichSelected, dsc_state_t.isEncoder, dsc_state_t.isEncoder, dsc_state_t.isEncoder, dsc_state_t.midpointSelected, dsc_state_t.midpointSelected, dsc_state_t.midpointSelected, dsc_state_t.midpointSelected, dsc_state_t.mppState, dsc_state_t.pixelCount, dsc_state_t.predictedSize, dsc_state_t.predictedSize, dsc_state_t.predictedSize, dsc_state_t.predictedSize, dsc_state_t.predictedSize, dsc_state_t.predictedSize, dsc_state_t.predictedSize, dsc_state_t.predictedSize, dsc_state_t.prevQp, dsc_state_t.prevQp, dsc_state_t.prevQp, dsc_state_t.prevQp, dsc_state_t.prevRange, dsc_state_t.rcSizeGroup, dsc_state_t.rcSizeUnit, dsc_state_t.stQp, dsc_state_t.stQp, dsc_state_t.unitsPerGroup, dsc_state_t.unitsPerGroup, dsc_state_t.useMidpoint, dsc_state_t.useMidpoint, dsc_state_t.useMidpoint, dsc_state_t.useMidpoint, dsc_state_t.vPos
  - AST loop count is 3; trip proofs are retained per loop

## `RemoveBitsEncoderBuffer`

- Source: `dsc_codec.c:1201`
- Clang USR: `c:@F@RemoveBitsEncoderBuffer`
- Return: `void`; parameters: `dsc_cfg: dsc_cfg_t *`, `dsc_state: dsc_state_t *`
- Callers: DSC_Algorithm, RateControl
- Callees: NONE
- Global read/write: 0/0; field read/write: 15/14
- Pointer modes: dsc_cfg=READ_ONLY, dsc_state=WRITES_THROUGH
- Loops: 0; fixed counts: UNKNOWN
- Effects: `{"assert": false, "file_io": false, "indirect_call": false, "logging": false, "malloc": false}`
- Proposal: **STATEFUL**; purity=False; combinational=False
- Classification evidence:
  - AST observed writes or mutable-state effects: ['dsc_state', 'dsc_state_t.bitsClamped', 'dsc_state_t.bpgFracAccum', 'dsc_state_t.bufferFullness', 'dsc_state_t.chunkCount', 'dsc_state_t.chunkPixelTimes', 'dsc_state_t.chunkSizes', 'dsc_state_t.numBitsChunk']
  - AST pointer modes: ['READ_ONLY', 'WRITES_THROUGH']
  - AST observed field reads: dsc_cfg_t.bits_per_pixel, dsc_cfg_t.bits_per_pixel, dsc_cfg_t.bits_per_pixel, dsc_cfg_t.chunk_size, dsc_cfg_t.vbr_enable, dsc_state_t.bitsClamped, dsc_state_t.bitsClamped, dsc_state_t.bpgFracAccum, dsc_state_t.bpgFracAccum, dsc_state_t.chunkPixelTimes, dsc_state_t.isEncoder, dsc_state_t.numBitsChunk, dsc_state_t.numBitsChunk, dsc_state_t.numBitsChunk, dsc_state_t.sliceWidth
  - AST observed no loop

## `SampToLineBuf`

- Source: `dsc_codec.c:2036`
- Clang USR: `c:@F@SampToLineBuf`
- Return: `int`; parameters: `dsc_cfg: dsc_cfg_t *`, `dsc_state: dsc_state_t *`, `x: int`, `cpnt: int`
- Callers: DSC_Algorithm
- Callees: NONE
- Global read/write: 0/0; field read/write: 3/0
- Pointer modes: dsc_cfg=READ_ONLY, dsc_state=READ_ONLY
- Loops: 0; fixed counts: UNKNOWN
- Effects: `{"assert": false, "file_io": false, "indirect_call": false, "logging": false, "malloc": false}`
- Proposal: **CONFIG_HELPER**; purity=False; combinational=True
- Classification evidence:
  - AST observed no global/field/pointee writes
  - AST pointer modes: ['READ_ONLY', 'READ_ONLY']
  - AST observed field reads: dsc_cfg_t.linebuf_depth, dsc_cfg_t.linebuf_depth, dsc_state_t.cpntBitDepth
  - AST observed no loop
  - The proposal is per-field input use; the containing struct is not classified as static configuration

## `SamplePredict`

- Source: `dsc_codec.c:308`
- Clang USR: `c:@F@SamplePredict`
- Return: `int`; parameters: `dsc_state: dsc_state_t *`, `prevLine: int *`, `currLine: int *`, `hPos: int`, `predType: PRED_TYPE`, `qLevel: int`, `unit: int`
- Callers: BlockPredSearch, PredictionLoop
- Callees: NONE
- Global read/write: 8/0; field read/write: 7/0
- Pointer modes: dsc_state=READ_ONLY, prevLine=READ_ONLY, currLine=READ_ONLY
- Loops: 0; fixed counts: UNKNOWN
- Effects: `{"assert": false, "file_io": false, "indirect_call": false, "logging": false, "malloc": false}`
- Proposal: **PURE_COMB_CANDIDATE**; purity=True; combinational=True
- Classification evidence:
  - AST observed no global/field/pointee writes
  - AST pointer modes: ['READ_ONLY', 'READ_ONLY', 'READ_ONLY']
  - AST observed global reads: QuantDivisor, QuantDivisor, QuantDivisor, QuantDivisor, QuantDivisor, QuantDivisor, QuantDivisor, QuantDivisor
  - AST observed field reads: dsc_state_t.cpntBitDepth, dsc_state_t.cpntBitDepth, dsc_state_t.quantizedResidual, dsc_state_t.quantizedResidual, dsc_state_t.quantizedResidual, dsc_state_t.quantizedResidual, dsc_state_t.unitCType
  - AST observed no loop
  - No direct calls and no non-const global read were observed

## `UErr`

- Source: `logging.c:110`
- Clang USR: `c:@F@UErr`
- Return: `void`; parameters: `format: char *`
- Callers: compute_rc_parameters, convert_rgb_2020_to_709, generate_rc_parameters, main, parse_pps, populate_pps, rgba_read, splitstring_exact_strict, str2dvect, str2fvect, str2ivect, str2llvect, str2lvect, str2pvect, str2uivect, str2ullvect, str2ulvect, assign_val, error_check, parse_kvline, assign_line
- Callees: __builtin_va_end, __builtin_va_start, exit, fprintf, vfprintf
- Global read/write: 3/0; field read/write: 0/0
- Pointer modes: format=UNKNOWN
- Loops: 0; fixed counts: UNKNOWN
- Effects: `{"assert": false, "file_io": true, "indirect_call": false, "logging": false, "malloc": false}`
- Proposal: **IO_OR_DEBUG**; purity=False; combinational=False
- Classification evidence:
  - AST observed no global/field/pointee writes
  - AST pointer modes: ['UNKNOWN']
  - AST observed global reads: __stderrp, __stderrp, __stderrp
  - AST observed no loop

## `UpdateHistoryElement`

- Source: `dsc_codec.c:674`
- Clang USR: `c:@F@UpdateHistoryElement`
- Return: `void`; parameters: `dsc_cfg: dsc_cfg_t *`, `dsc_state: dsc_state_t *`, `recon: unsigned int *`
- Callers: UpdateICHistory
- Callees: HistoryLookup
- Global read/write: 0/0; field read/write: 15/8
- Pointer modes: dsc_cfg=UNKNOWN, dsc_state=WRITES_THROUGH, recon=READ_ONLY
- Loops: 4; fixed counts: UNKNOWN
- Effects: `{"assert": false, "file_io": false, "indirect_call": false, "logging": false, "malloc": false}`
- Proposal: **STATEFUL**; purity=False; combinational=False
- Classification evidence:
  - AST observed writes or mutable-state effects: ['dsc_history_t.pixels', 'dsc_history_t.valid', 'dsc_state', 'dsc_state_t.history']
  - AST pointer modes: ['READ_ONLY', 'UNKNOWN', 'WRITES_THROUGH']
  - AST observed field reads: dsc_cfg_t.native_420, dsc_history_t.pixels, dsc_history_t.valid, dsc_state_t.hPos, dsc_state_t.history, dsc_state_t.history, dsc_state_t.ichSelected, dsc_state_t.isEncoder, dsc_state_t.isEncoder, dsc_state_t.numComponents, dsc_state_t.numComponents, dsc_state_t.prevIchSelected, dsc_state_t.vPos, dsc_state_t.vPos, dsc_state_t.vPos
  - AST loop count is 4; trip proofs are retained per loop

## `UpdateICHistory`

- Source: `dsc_codec.c:787`
- Clang USR: `c:@F@UpdateICHistory`
- Return: `void`; parameters: `dsc_cfg: dsc_cfg_t *`, `dsc_state: dsc_state_t *`, `currLine: int **`, `hPos: int`, `vPos: int`
- Callers: DSC_Algorithm
- Callees: UpdateHistoryElement
- Global read/write: 0/0; field read/write: 4/4
- Pointer modes: dsc_cfg=UNKNOWN, dsc_state=UNKNOWN, currLine=READ_ONLY
- Loops: 3; fixed counts: 32, 32
- Effects: `{"assert": false, "file_io": false, "indirect_call": false, "logging": false, "malloc": false}`
- Proposal: **STATEFUL**; purity=False; combinational=False
- Classification evidence:
  - AST observed writes or mutable-state effects: ['dsc_history_t.valid', 'dsc_state_t.history']
  - AST pointer modes: ['READ_ONLY', 'UNKNOWN', 'UNKNOWN']
  - AST observed field reads: dsc_cfg_t.pic_width, dsc_cfg_t.slice_width, dsc_state_t.numComponents, dsc_state_t.pixelsInGroup
  - AST loop count is 3; trip proofs are retained per loop

## `UpdateMidpoint`

- Source: `dsc_codec.c:875`
- Clang USR: `c:@F@UpdateMidpoint`
- Return: `void`; parameters: `dsc_cfg: dsc_cfg_t *`, `dsc_state: dsc_state_t *`, `currLine: int **`, `hPos: int`
- Callers: DSC_Algorithm
- Callees: NONE
- Global read/write: 0/0; field read/write: 7/0
- Pointer modes: dsc_cfg=READ_ONLY, dsc_state=WRITES_THROUGH, currLine=WRITES_THROUGH
- Loops: 2; fixed counts: 3
- Effects: `{"assert": false, "file_io": false, "indirect_call": false, "logging": false, "malloc": false}`
- Proposal: **STATEFUL**; purity=False; combinational=False
- Classification evidence:
  - AST observed writes or mutable-state effects: ['currLine', 'dsc_state']
  - AST pointer modes: ['READ_ONLY', 'WRITES_THROUGH', 'WRITES_THROUGH']
  - AST observed field reads: dsc_state_t.midpointRecon, dsc_state_t.midpointSelected, dsc_state_t.pixelsInGroup, dsc_state_t.sliceWidth, dsc_state_t.unitCType, dsc_state_t.unitStartHPos, dsc_state_t.unitsPerGroup
  - AST loop count is 2; trip proofs are retained per loop

## `UseICHistory`

- Source: `dsc_codec.c:832`
- Clang USR: `c:@F@UseICHistory`
- Return: `void`; parameters: `dsc_cfg: dsc_cfg_t *`, `dsc_state: dsc_state_t *`, `currLine: int **`
- Callers: DSC_Algorithm
- Callees: printf
- Global read/write: 3/0; field read/write: 10/0
- Pointer modes: dsc_cfg=READ_ONLY, dsc_state=UNKNOWN, currLine=WRITES_THROUGH
- Loops: 2; fixed counts: UNKNOWN
- Effects: `{"assert": false, "file_io": false, "indirect_call": false, "logging": true, "malloc": false}`
- Proposal: **IO_OR_DEBUG**; purity=False; combinational=False
- Classification evidence:
  - AST observed writes or mutable-state effects: ['currLine']
  - AST pointer modes: ['READ_ONLY', 'UNKNOWN', 'WRITES_THROUGH']
  - AST observed global reads: g_verbose, g_verbose, g_verbose
  - AST observed field reads: dsc_state_t.hPos, dsc_state_t.ichIndicesInGroup, dsc_state_t.ichLookup, dsc_state_t.ichPixels, dsc_state_t.ichPixels, dsc_state_t.ichPixels, dsc_state_t.ichPixels, dsc_state_t.ichSelected, dsc_state_t.numComponents, dsc_state_t.pixelsInGroup
  - AST loop count is 2; trip proofs are retained per loop

## `UsingMidpoint`

- Source: `dsc_codec.c:457`
- Clang USR: `c:@F@UsingMidpoint`
- Return: `int`; parameters: `dsc_cfg: dsc_cfg_t *`, `dsc_state: dsc_state_t *`, `unit: int`, `cpnt: int`
- Callers: IchDecision
- Callees: FindResidualSize, MapQpToQlevel
- Global read/write: 0/0; field read/write: 3/0
- Pointer modes: dsc_cfg=UNKNOWN, dsc_state=UNKNOWN
- Loops: 1; fixed counts: 3
- Effects: `{"assert": false, "file_io": false, "indirect_call": false, "logging": false, "malloc": false}`
- Proposal: **COMPOSITE_COMB_CANDIDATE**; purity=False; combinational=True
- Classification evidence:
  - AST observed no global/field/pointee writes
  - AST pointer modes: ['UNKNOWN', 'UNKNOWN']
  - AST observed field reads: dsc_state_t.cpntBitDepth, dsc_state_t.primaryQp, dsc_state_t.quantizedResidual
  - AST loop count is 1; trip proofs are retained per loop

## `VLCGroup`

- Source: `dsc_codec.c:1710`
- Clang USR: `c:@F@VLCGroup`
- Return: `void`; parameters: `dsc_cfg: dsc_cfg_t *`, `dsc_state: dsc_state_t *`, `byte_out_p: unsigned char **`, `force_p1_ich2: int`
- Callers: DSC_Algorithm
- Callees: ProcessGroupEnc, VLCUnit, exit, fifo_put_bits, printf
- Global read/write: 0/0; field read/write: 56/9
- Pointer modes: dsc_cfg=UNKNOWN, dsc_state=WRITES_THROUGH, byte_out_p=UNKNOWN
- Loops: 7; fixed counts: UNKNOWN
- Effects: `{"assert": false, "file_io": false, "indirect_call": false, "logging": true, "malloc": false}`
- Proposal: **IO_OR_DEBUG**; purity=False; combinational=False
- Classification evidence:
  - AST observed writes or mutable-state effects: ['dsc_state', 'dsc_state_t.bufferFullness', 'dsc_state_t.codedGroupSize', 'dsc_state_t.forceMpp', 'dsc_state_t.groupCountLine', 'dsc_state_t.midpointSelected', 'dsc_state_t.prevNumBits', 'dsc_state_t.prevPrimaryQp']
  - AST pointer modes: ['UNKNOWN', 'UNKNOWN', 'WRITES_THROUGH']
  - AST observed field reads: dsc_cfg_t.bits_per_component, dsc_cfg_t.bits_per_component, dsc_cfg_t.bits_per_pixel, dsc_cfg_t.bits_per_pixel, dsc_cfg_t.chunk_size, dsc_cfg_t.chunk_size, dsc_cfg_t.initial_xmit_delay, dsc_cfg_t.mux_word_size, dsc_cfg_t.mux_word_size, dsc_cfg_t.rcb_bits, dsc_cfg_t.rcb_bits, dsc_cfg_t.vbr_enable, dsc_state_t.bufferFullness, dsc_state_t.bufferFullness, dsc_state_t.bufferFullness, dsc_state_t.encBalanceFifo, dsc_state_t.encBalanceFifo, dsc_state_t.encBalanceFifo, dsc_state_t.encBalanceFifo, dsc_state_t.encBalanceFifo, dsc_state_t.encBalanceFifo, dsc_state_t.groupCount, dsc_state_t.groupCount, dsc_state_t.maxSeSize, dsc_state_t.maxSeSize, dsc_state_t.numBits, dsc_state_t.numBits, dsc_state_t.numBits, dsc_state_t.numBitsChunk, dsc_state_t.numBitsChunk, dsc_state_t.numSsps, dsc_state_t.numSsps, dsc_state_t.numSsps, dsc_state_t.numSsps, dsc_state_t.pixelCount, dsc_state_t.pixelsInGroup, dsc_state_t.prevNumBits, dsc_state_t.prevNumBits, dsc_state_t.primaryQp, dsc_state_t.quantizedResidual, dsc_state_t.quantizedResidual, dsc_state_t.seSizeFifo, dsc_state_t.seSizeFifo, dsc_state_t.sliceWidth, dsc_state_t.unitsPerGroup, dsc_state_t.unitsPerGroup, dsc_state_t.unitsPerGroup, dsc_state_t.unitsPerGroup, dsc_state_t.unitsPerGroup, dsc_state_t.unitsPerGroup, fifo_s.fullness, fifo_s.fullness, fifo_s.fullness, fifo_s.fullness, fifo_s.fullness, fifo_s.fullness
  - AST loop count is 7; trip proofs are retained per loop

## `VLCUnit`

- Source: `dsc_codec.c:1494`
- Clang USR: `c:@F@VLCUnit`
- Return: `void`; parameters: `dsc_cfg: dsc_cfg_t *`, `dsc_state: dsc_state_t *`, `unit: int`, `quantized_residuals: int *`, `force_p1_ich2: int`
- Callers: VLCGroup
- Callees: AddBits, EscapeCodeSize, FindResidualSize, GetQpAdjPredSize, IchDecision, IsFlatnessInfoSent, MapQpToQlevel, MaxResidualSize, PredictSize, __assert_rtn, __builtin_expect, fprintf
- Global read/write: 12/0; field read/write: 44/10
- Pointer modes: dsc_cfg=UNKNOWN, dsc_state=WRITES_THROUGH, quantized_residuals=UNKNOWN
- Loops: 9; fixed counts: 3, 3, 3, 3, 3
- Effects: `{"assert": true, "file_io": true, "indirect_call": false, "logging": false, "malloc": false}`
- Proposal: **IO_OR_DEBUG**; purity=False; combinational=False
- Classification evidence:
  - AST observed writes or mutable-state effects: ['dsc_state', 'dsc_state_t.flatnessType', 'dsc_state_t.ichSelected', 'dsc_state_t.midpointSelected', 'dsc_state_t.predictedSize', 'dsc_state_t.prevIchSelected', 'dsc_state_t.rcSizeUnit']
  - AST pointer modes: ['UNKNOWN', 'UNKNOWN', 'WRITES_THROUGH']
  - AST observed global reads: g_fp_dbg, g_fp_dbg, g_fp_dbg, g_fp_dbg, g_fp_dbg, g_fp_dbg, g_fp_dbg, g_fp_dbg, g_fp_dbg, g_fp_dbg, g_fp_dbg, g_fp_dbg
  - AST observed field reads: dsc_cfg_t.bits_per_component, dsc_cfg_t.bits_per_component, dsc_cfg_t.somewhat_flat_qp_thresh, dsc_state_t.cpntBitDepth, dsc_state_t.cpntBitDepth, dsc_state_t.cpntBitDepth, dsc_state_t.cpntBitDepth, dsc_state_t.firstFlat, dsc_state_t.firstFlat, dsc_state_t.firstFlat, dsc_state_t.flatnessType, dsc_state_t.flatnessType, dsc_state_t.forceMpp, dsc_state_t.forceMpp, dsc_state_t.groupCount, dsc_state_t.groupCount, dsc_state_t.ichIndexUnitMap, dsc_state_t.ichIndexUnitMap, dsc_state_t.ichIndicesInGroup, dsc_state_t.ichIndicesInGroup, dsc_state_t.ichIndicesInGroup, dsc_state_t.ichIndicesInGroup, dsc_state_t.ichIndicesInGroup, dsc_state_t.ichLookup, dsc_state_t.ichLookup, dsc_state_t.ichLookup, dsc_state_t.ichSelected, dsc_state_t.ichSelected, dsc_state_t.origWithinQerr, dsc_state_t.prevFirstFlat, dsc_state_t.prevIchSelected, dsc_state_t.prevIchSelected, dsc_state_t.prevIchSelected, dsc_state_t.prevIchSelected, dsc_state_t.primaryQp, dsc_state_t.primaryQp, dsc_state_t.primaryQp, dsc_state_t.primaryQp, dsc_state_t.primaryQp, dsc_state_t.primaryQp, dsc_state_t.quantizedResidualMid, dsc_state_t.quantizedResidualMid, dsc_state_t.unitCType, dsc_state_t.unitSspMap
  - AST loop count is 9; trip proofs are retained per loop

## `VLDGroup`

- Source: `dsc_codec.c:1988`
- Clang USR: `c:@F@VLDGroup`
- Return: `void`; parameters: `dsc_cfg: dsc_cfg_t *`, `dsc_state: dsc_state_t *`, `byte_in_p: unsigned char **`
- Callers: DSC_Algorithm
- Callees: ProcessGroupDec, VLDUnit, printf
- Global read/write: 0/0; field read/write: 17/7
- Pointer modes: dsc_cfg=UNKNOWN, dsc_state=WRITES_THROUGH, byte_in_p=UNKNOWN
- Loops: 3; fixed counts: UNKNOWN
- Effects: `{"assert": false, "file_io": false, "indirect_call": false, "logging": true, "malloc": false}`
- Proposal: **IO_OR_DEBUG**; purity=False; combinational=False
- Classification evidence:
  - AST observed writes or mutable-state effects: ['dsc_state', 'dsc_state_t.bufferFullness', 'dsc_state_t.codedGroupSize', 'dsc_state_t.errorOccurred', 'dsc_state_t.groupCountLine', 'dsc_state_t.origIsFlat', 'dsc_state_t.prevPrimaryQp']
  - AST pointer modes: ['UNKNOWN', 'UNKNOWN', 'WRITES_THROUGH']
  - AST observed field reads: dsc_cfg_t.rcb_bits, dsc_cfg_t.rcb_bits, dsc_state_t.bufferFullness, dsc_state_t.bufferFullness, dsc_state_t.codedGroupSize, dsc_state_t.firstFlat, dsc_state_t.groupCount, dsc_state_t.numBits, dsc_state_t.numBits, dsc_state_t.primaryQp, dsc_state_t.quantizedResidual, dsc_state_t.quantizedResidual, dsc_state_t.quantizedResidual, dsc_state_t.unitsPerGroup, dsc_state_t.unitsPerGroup, dsc_state_t.unitsPerGroup, dsc_state_t.unitsPerGroup
  - AST loop count is 3; trip proofs are retained per loop

## `VLDUnit`

- Source: `dsc_codec.c:1808`
- Clang USR: `c:@F@VLDUnit`
- Return: `void`; parameters: `dsc_cfg: dsc_cfg_t *`, `dsc_state: dsc_state_t *`, `unit: int`, `quantized_residuals: int *`, `byte_in_p: unsigned char **`
- Callers: VLDGroup
- Callees: EscapeCodeSize, FindResidualSize, GetBits, GetQpAdjPredSize, IsFlatnessInfoSent, MapQpToQlevel, MaxResidualSize, PredictSize, fprintf
- Global read/write: 9/0; field read/write: 31/17
- Pointer modes: dsc_cfg=UNKNOWN, dsc_state=WRITES_THROUGH, quantized_residuals=UNKNOWN, byte_in_p=UNKNOWN
- Loops: 9; fixed counts: 3, 3
- Effects: `{"assert": false, "file_io": true, "indirect_call": false, "logging": false, "malloc": false}`
- Proposal: **IO_OR_DEBUG**; purity=False; combinational=False
- Classification evidence:
  - AST observed writes or mutable-state effects: ['dsc_state', 'dsc_state_t.firstFlat', 'dsc_state_t.flatnessType', 'dsc_state_t.ichLookup', 'dsc_state_t.ichSelected', 'dsc_state_t.predictedSize', 'dsc_state_t.prevFirstFlat', 'dsc_state_t.prevIchSelected', 'dsc_state_t.rcSizeUnit', 'dsc_state_t.useMidpoint']
  - AST pointer modes: ['UNKNOWN', 'UNKNOWN', 'UNKNOWN', 'WRITES_THROUGH']
  - AST observed global reads: g_fp_dbg, g_fp_dbg, g_fp_dbg, g_fp_dbg, g_fp_dbg, g_fp_dbg, g_fp_dbg, g_fp_dbg, g_fp_dbg
  - AST observed field reads: dsc_cfg_t.bits_per_component, dsc_cfg_t.bits_per_component, dsc_cfg_t.somewhat_flat_qp_thresh, dsc_state_t.cpntBitDepth, dsc_state_t.firstFlat, dsc_state_t.flatnessType, dsc_state_t.groupCount, dsc_state_t.groupCount, dsc_state_t.ichIndexUnitMap, dsc_state_t.ichIndexUnitMap, dsc_state_t.ichIndicesInGroup, dsc_state_t.ichIndicesInGroup, dsc_state_t.ichIndicesInGroup, dsc_state_t.ichIndicesInGroup, dsc_state_t.ichLookup, dsc_state_t.ichSelected, dsc_state_t.ichSelected, dsc_state_t.prevFirstFlat, dsc_state_t.prevFirstFlat, dsc_state_t.prevIchSelected, dsc_state_t.prevIchSelected, dsc_state_t.primaryQp, dsc_state_t.primaryQp, dsc_state_t.primaryQp, dsc_state_t.primaryQp, dsc_state_t.primaryQp, dsc_state_t.primaryQp, dsc_state_t.unitCType, dsc_state_t.unitSspMap, dsc_state_t.unitsPerGroup, dsc_state_t.unitsPerGroup
  - AST loop count is 9; trip proofs are retained per loop

## `WriteEntryToBitstream`

- Source: `multiplex.c:60`
- Clang USR: `c:@F@WriteEntryToBitstream`
- Return: `void`; parameters: `dsc_cfg: dsc_cfg_t *`, `dsc_state: dsc_state_t *`, `buf: unsigned char *`
- Callers: NONE
- Callees: fifo_get_bits, printf, putbits
- Global read/write: 0/0; field read/write: 8/0
- Pointer modes: dsc_cfg=READ_ONLY, dsc_state=UNKNOWN, buf=UNKNOWN
- Loops: 1; fixed counts: UNKNOWN
- Effects: `{"assert": false, "file_io": false, "indirect_call": false, "logging": true, "malloc": false}`
- Proposal: **IO_OR_DEBUG**; purity=False; combinational=False
- Classification evidence:
  - AST observed no global/field/pointee writes
  - AST pointer modes: ['READ_ONLY', 'UNKNOWN', 'UNKNOWN']
  - AST observed field reads: dsc_state_t.encBalanceFifo, dsc_state_t.encBalanceFifo, dsc_state_t.encBalanceFifo, dsc_state_t.numSsps, dsc_state_t.postMuxNumBits, dsc_state_t.postMuxNumBits, dsc_state_t.seSizeFifo, fifo_s.fullness
  - AST loop count is 1; trip proofs are retained per loop

## `appendarg`

- Source: `cmd_parse.c:1328`
- Clang USR: `c:@F@appendarg`
- Return: `void`; parameters: `string: char *`, `cmdarg: const cmdarg_t`
- Callers: parse_cmd_usage, parse_key_usage
- Callees: __builtin___strcat_chk, __builtin_object_size
- Global read/write: 0/0; field read/write: 1/0
- Pointer modes: string=UNKNOWN
- Loops: 0; fixed counts: UNKNOWN
- Effects: `{"assert": false, "file_io": false, "indirect_call": false, "logging": false, "malloc": false}`
- Proposal: **COMPOSITE_COMB_CANDIDATE**; purity=False; combinational=True
- Classification evidence:
  - AST observed no global/field/pointee writes
  - AST pointer modes: ['UNKNOWN']
  - AST observed field reads: cmdarg_s.type
  - AST observed no loop

## `assign_line`

- Source: `codec_main.c:358`
- Clang USR: `c:codec_main.c@F@assign_line`
- Return: `int`; parameters: `line: char *`, `cmdargs: cmdarg_t *`
- Callers: parse_cfgfile, process_args
- Callees: UErr, parse_line, parse_cfgfile
- Global read/write: 2/0; field read/write: 0/0
- Pointer modes: line=UNKNOWN, cmdargs=UNKNOWN
- Loops: 0; fixed counts: UNKNOWN
- Effects: `{"assert": false, "file_io": false, "indirect_call": false, "logging": true, "malloc": false}`
- Proposal: **IO_OR_DEBUG**; purity=False; combinational=False
- Classification evidence:
  - AST observed writes or mutable-state effects: ['filepath']
  - AST pointer modes: ['UNKNOWN', 'UNKNOWN']
  - AST observed global reads: filepath, filepath
  - AST observed no loop

## `assign_val`

- Source: `cmd_parse.c:799`
- Clang USR: `c:cmd_parse.c@F@assign_val`
- Return: `int`; parameters: `cmdarg: const cmdarg_t`, `v: char *`, `cmd: int`
- Callers: parse_cmd, parse_line
- Callees: Assert_func, UErr, __builtin___strcpy_chk, __builtin_object_size, str2d, str2dim, str2dvect, str2f, str2fdim, str2frange, str2fvect, str2i, str2ivect, str2l, str2ll, str2llvect, str2lvect, str2p, str2pdim, str2prange, str2pvect, str2range, str2ui, str2uivect, str2ul, str2ull, str2ullvect, str2ulvect
- Global read/write: 0/0; field read/write: 39/10
- Pointer modes: v=UNKNOWN
- Loops: 0; fixed counts: UNKNOWN
- Effects: `{"assert": true, "file_io": false, "indirect_call": false, "logging": true, "malloc": false}`
- Proposal: **IO_OR_DEBUG**; purity=False; combinational=False
- Classification evidence:
  - AST observed writes or mutable-state effects: ['cmdarg_s.var_ptr']
  - AST pointer modes: ['UNKNOWN']
  - AST observed field reads: cmdarg_s.cmd, cmdarg_s.key, cmdarg_s.type, cmdarg_s.type, cmdarg_s.type, cmdarg_s.type, cmdarg_s.type, cmdarg_s.value, cmdarg_s.var_ptr, cmdarg_s.var_ptr, cmdarg_s.var_ptr, cmdarg_s.var_ptr, cmdarg_s.var_ptr, cmdarg_s.var_ptr, cmdarg_s.var_ptr, cmdarg_s.var_ptr, cmdarg_s.var_ptr, cmdarg_s.var_ptr, cmdarg_s.var_ptr, cmdarg_s.var_ptr, cmdarg_s.var_ptr, cmdarg_s.var_ptr, cmdarg_s.var_ptr, cmdarg_s.var_ptr, cmdarg_s.var_ptr, cmdarg_s.var_ptr, cmdarg_s.var_ptr, cmdarg_s.var_ptr, cmdarg_s.var_ptr, cmdarg_s.var_ptr, cmdarg_s.vct_lng, cmdarg_s.vct_lng, cmdarg_s.vct_lng, cmdarg_s.vct_lng, cmdarg_s.vct_lng, cmdarg_s.vct_lng, cmdarg_s.vct_lng, cmdarg_s.vct_lng, cmdarg_s.vct_lng
  - AST observed no loop

## `ceil_log2`

- Source: `dsc_utils.c:67`
- Clang USR: `c:@F@ceil_log2`
- Return: `int`; parameters: `val: int`
- Callers: IchDecision
- Callees: NONE
- Global read/write: 0/0; field read/write: 0/0
- Pointer modes: NONE
- Loops: 1; fixed counts: UNKNOWN
- Effects: `{"assert": false, "file_io": false, "indirect_call": false, "logging": false, "malloc": false}`
- Proposal: **PURE_COMB_CANDIDATE**; purity=True; combinational=True
- Classification evidence:
  - AST observed no global/field/pointee writes
  - AST loop count is 1; trip proofs are retained per loop
  - No direct calls and no non-const global read were observed

## `change_ext`

- Source: `cmd_parse.c:376`
- Clang USR: `c:@F@change_ext`
- Return: `void`; parameters: `path: char *`, `ext: char *`
- Callers: NONE
- Callees: __builtin___strcpy_chk, __builtin_object_size
- Global read/write: 0/0; field read/write: 0/0
- Pointer modes: path=UNKNOWN, ext=READ_ONLY
- Loops: 1; fixed counts: UNKNOWN
- Effects: `{"assert": false, "file_io": false, "indirect_call": false, "logging": false, "malloc": false}`
- Proposal: **COMPOSITE_COMB_CANDIDATE**; purity=False; combinational=True
- Classification evidence:
  - AST observed no global/field/pointee writes
  - AST pointer modes: ['READ_ONLY', 'UNKNOWN']
  - AST loop count is 1; trip proofs are retained per loop

## `check_qp_for_overflow`

- Source: `codec_main.c:860`
- Clang USR: `c:@F@check_qp_for_overflow`
- Return: `void`; parameters: `dsc_cfg: dsc_cfg_t *`, `pixelsPerGroup: int`
- Callers: populate_pps
- Callees: Qp2Qlevel, printf
- Global read/write: 1/0; field read/write: 11/0
- Pointer modes: dsc_cfg=UNKNOWN
- Loops: 3; fixed counts: 4
- Effects: `{"assert": false, "file_io": false, "indirect_call": false, "logging": true, "malloc": false}`
- Proposal: **IO_OR_DEBUG**; purity=False; combinational=False
- Classification evidence:
  - AST observed writes or mutable-state effects: ['bitsPerPixel']
  - AST pointer modes: ['UNKNOWN']
  - AST observed global reads: bitsPerPixel
  - AST observed field reads: dsc_cfg_t.bits_per_component, dsc_cfg_t.bits_per_component, dsc_cfg_t.convert_rgb, dsc_cfg_t.native_422, dsc_cfg_t.native_422, dsc_cfg_t.nfl_bpg_offset, dsc_cfg_t.rc_range_parameters, dsc_cfg_t.rc_range_parameters, dsc_cfg_t.slice_bpg_offset, dsc_range_cfg_t.range_max_qp, dsc_range_cfg_t.range_max_qp
  - AST loop count is 3; trip proofs are retained per loop

## `chop_dir`

- Source: `cmd_parse.c:132`
- Clang USR: `c:@F@chop_dir`
- Return: `char *`; parameters: `path: const char *`
- Callers: NONE
- Callees: __builtin___strcpy_chk, __builtin_object_size, malloc, strlen, strrchr
- Global read/write: 0/0; field read/write: 0/0
- Pointer modes: path=READ_ONLY
- Loops: 0; fixed counts: UNKNOWN
- Effects: `{"assert": false, "file_io": false, "indirect_call": false, "logging": false, "malloc": true}`
- Proposal: **IO_OR_DEBUG**; purity=False; combinational=False
- Classification evidence:
  - AST observed no global/field/pointee writes
  - AST pointer modes: ['READ_ONLY']
  - AST observed no loop

## `chop_ext`

- Source: `cmd_parse.c:102`
- Clang USR: `c:@F@chop_ext`
- Return: `char *`; parameters: `path: const char *`
- Callers: determine_field_format
- Callees: __builtin___strcpy_chk, __builtin___strncpy_chk, __builtin_object_size, malloc, strlen, strrchr
- Global read/write: 0/0; field read/write: 0/0
- Pointer modes: path=READ_ONLY
- Loops: 0; fixed counts: UNKNOWN
- Effects: `{"assert": false, "file_io": false, "indirect_call": false, "logging": false, "malloc": true}`
- Proposal: **IO_OR_DEBUG**; purity=False; combinational=False
- Classification evidence:
  - AST observed no global/field/pointee writes
  - AST pointer modes: ['READ_ONLY']
  - AST observed no loop

## `compute_and_display_PSNR`

- Source: `psnr.c:66`
- Clang USR: `c:@F@compute_and_display_PSNR`
- Return: `void`; parameters: `p_in: pic_t *`, `p_out: pic_t *`, `bpp: int`, `logfp: FILE *`
- Callers: main
- Callees: abs, fprintf, log10, printf
- Global read/write: 0/0; field read/write: 56/0
- Pointer modes: p_in=READ_ONLY, p_out=READ_ONLY, logfp=UNKNOWN
- Loops: 9; fixed counts: UNKNOWN
- Effects: `{"assert": false, "file_io": true, "indirect_call": false, "logging": true, "malloc": false}`
- Proposal: **IO_OR_DEBUG**; purity=False; combinational=False
- Classification evidence:
  - AST observed no global/field/pointee writes
  - AST pointer modes: ['READ_ONLY', 'READ_ONLY', 'UNKNOWN']
  - AST observed field reads: data_u.rgb, data_u.rgb, data_u.rgb, data_u.rgb, data_u.rgb, data_u.rgb, data_u.yuv, data_u.yuv, data_u.yuv, data_u.yuv, data_u.yuv, data_u.yuv, pic_s.bits, pic_s.bits, pic_s.chroma, pic_s.chroma, pic_s.chroma, pic_s.chroma, pic_s.color, pic_s.data, pic_s.data, pic_s.data, pic_s.data, pic_s.data, pic_s.data, pic_s.data, pic_s.data, pic_s.data, pic_s.data, pic_s.data, pic_s.data, pic_s.h, pic_s.h, pic_s.h, pic_s.h, pic_s.h, pic_s.h, pic_s.w, pic_s.w, pic_s.w, pic_s.w, pic_s.w, pic_s.w, pic_s.w, rgb_s.b, rgb_s.b, rgb_s.g, rgb_s.g, rgb_s.r, rgb_s.r, yuv_s.u, yuv_s.u, yuv_s.v, yuv_s.v, yuv_s.y, yuv_s.y
  - AST loop count is 9; trip proofs are retained per loop

## `compute_offset`

- Source: `codec_main.c:616`
- Clang USR: `c:@F@compute_offset`
- Return: `int`; parameters: `dsc_cfg: dsc_cfg_t *`, `pixelsPerGroup: int`, `groupsPerLine: int`, `grpcnt: int`
- Callers: compute_rc_parameters
- Callees: ceil
- Global read/write: 8/0; field read/write: 5/0
- Pointer modes: dsc_cfg=READ_ONLY
- Loops: 0; fixed counts: UNKNOWN
- Effects: `{"assert": false, "file_io": false, "indirect_call": false, "logging": false, "malloc": false}`
- Proposal: **STATEFUL**; purity=False; combinational=False
- Classification evidence:
  - AST observed writes or mutable-state effects: ['bitsPerPixel', 'firstLineBpgOfs', 'initialDelay', 'native420', 'secondLineBpgOfs']
  - AST pointer modes: ['READ_ONLY']
  - AST observed global reads: bitsPerPixel, bitsPerPixel, firstLineBpgOfs, firstLineBpgOfs, initialDelay, native420, secondLineBpgOfs, secondLineBpgOfs
  - AST observed field reads: dsc_cfg_t.nfl_bpg_offset, dsc_cfg_t.nsl_bpg_offset, dsc_cfg_t.nsl_bpg_offset, dsc_cfg_t.nsl_bpg_offset, dsc_cfg_t.slice_bpg_offset
  - AST observed no loop

## `compute_rc_parameters`

- Source: `codec_main.c:661`
- Clang USR: `c:@F@compute_rc_parameters`
- Return: `int`; parameters: `dsc_cfg: dsc_cfg_t *`, `pixelsPerGroup: int`, `numSsps: int`
- Callers: populate_pps
- Callees: UErr, ceil, compute_offset, printf
- Global read/write: 30/5; field read/write: 58/17
- Pointer modes: dsc_cfg=WRITES_THROUGH
- Loops: 1; fixed counts: UNKNOWN
- Effects: `{"assert": false, "file_io": false, "indirect_call": false, "logging": true, "malloc": false}`
- Proposal: **IO_OR_DEBUG**; purity=False; combinational=False
- Classification evidence:
  - AST observed writes or mutable-state effects: ['bitsPerComponent', 'bitsPerPixel', 'dsc_cfg', 'dsc_cfg_t.chunk_size', 'dsc_cfg_t.final_offset', 'dsc_cfg_t.first_line_bpg_ofs', 'dsc_cfg_t.initial_dec_delay', 'dsc_cfg_t.initial_scale_value', 'dsc_cfg_t.nfl_bpg_offset', 'dsc_cfg_t.nsl_bpg_offset', 'dsc_cfg_t.rcb_bits', 'dsc_cfg_t.scale_decrement_interval', 'dsc_cfg_t.scale_increment_interval', 'dsc_cfg_t.second_line_bpg_ofs', 'dsc_cfg_t.slice_bpg_offset', 'firstLineBpgOfs', 'initialDelay', 'initialFullnessOfs', 'native420', 'native422', 'secondLineBpgOfs', 'useYuvInput']
  - AST pointer modes: ['WRITES_THROUGH']
  - AST observed global reads: bitsPerComponent, bitsPerComponent, bitsPerComponent, bitsPerComponent, bitsPerComponent, bitsPerComponent, bitsPerComponent, bitsPerPixel, bitsPerPixel, bitsPerPixel, bitsPerPixel, bitsPerPixel, bitsPerPixel, bitsPerPixel, firstLineBpgOfs, firstLineBpgOfs, firstLineBpgOfs, firstLineBpgOfs, initialDelay, initialDelay, initialFullnessOfs, initialFullnessOfs, native420, native420, native422, native422, secondLineBpgOfs, secondLineBpgOfs, secondLineBpgOfs, useYuvInput
  - AST observed field reads: dsc_cfg_t.bits_per_pixel, dsc_cfg_t.chunk_size, dsc_cfg_t.chunk_size, dsc_cfg_t.convert_rgb, dsc_cfg_t.dsc_version_minor, dsc_cfg_t.final_offset, dsc_cfg_t.final_offset, dsc_cfg_t.first_line_bpg_ofs, dsc_cfg_t.first_line_bpg_ofs, dsc_cfg_t.first_line_bpg_ofs, dsc_cfg_t.initial_dec_delay, dsc_cfg_t.initial_offset, dsc_cfg_t.initial_offset, dsc_cfg_t.initial_scale_value, dsc_cfg_t.initial_scale_value, dsc_cfg_t.initial_scale_value, dsc_cfg_t.initial_scale_value, dsc_cfg_t.initial_xmit_delay, dsc_cfg_t.initial_xmit_delay, dsc_cfg_t.mux_word_size, dsc_cfg_t.mux_word_size, dsc_cfg_t.mux_word_size, dsc_cfg_t.mux_word_size, dsc_cfg_t.native_420, dsc_cfg_t.native_422, dsc_cfg_t.native_422, dsc_cfg_t.nfl_bpg_offset, dsc_cfg_t.nfl_bpg_offset, dsc_cfg_t.nfl_bpg_offset, dsc_cfg_t.nsl_bpg_offset, dsc_cfg_t.nsl_bpg_offset, dsc_cfg_t.rc_model_size, dsc_cfg_t.rc_model_size, dsc_cfg_t.rc_model_size, dsc_cfg_t.rc_model_size, dsc_cfg_t.rc_model_size, dsc_cfg_t.rc_model_size, dsc_cfg_t.rc_model_size, dsc_cfg_t.rc_model_size, dsc_cfg_t.rc_model_size, dsc_cfg_t.scale_decrement_interval, dsc_cfg_t.scale_increment_interval, dsc_cfg_t.second_line_bpg_ofs, dsc_cfg_t.second_line_bpg_ofs, dsc_cfg_t.slice_bpg_offset, dsc_cfg_t.slice_bpg_offset, dsc_cfg_t.slice_bpg_offset, dsc_cfg_t.slice_height, dsc_cfg_t.slice_height, dsc_cfg_t.slice_height, dsc_cfg_t.slice_height, dsc_cfg_t.slice_height, dsc_cfg_t.slice_height, dsc_cfg_t.slice_height, dsc_cfg_t.slice_height, dsc_cfg_t.slice_height, dsc_cfg_t.slice_height, dsc_cfg_t.slice_width
  - AST loop count is 1; trip proofs are retained per loop

## `conv`

- Source: `utl.c:470`
- Clang USR: `c:@F@conv`
- Return: `float`; parameters: `p: int **`, `fir: fir_t`, `w: int`, `h: int`, `x: int`, `y: int`
- Callers: yuv_422_420, yuv_444_422
- Callees: NONE
- Global read/write: 0/0; field read/write: 6/0
- Pointer modes: p=READ_ONLY
- Loops: 2; fixed counts: UNKNOWN
- Effects: `{"assert": false, "file_io": false, "indirect_call": false, "logging": false, "malloc": false}`
- Proposal: **PURE_COMB_CANDIDATE**; purity=True; combinational=True
- Classification evidence:
  - AST observed no global/field/pointee writes
  - AST pointer modes: ['READ_ONLY']
  - AST observed field reads: fir_s.coeff, fir_s.sub, fir_s.sub, fir_s.sub, fir_s.tap, fir_s.tap
  - AST loop count is 2; trip proofs are retained per loop
  - No direct calls and no non-const global read were observed

## `convert_rgb_2020_to_709`

- Source: `utl.c:1644`
- Clang USR: `c:@F@convert_rgb_2020_to_709`
- Return: `void`; parameters: `ip: pic_t *`, `op: pic_t *`
- Callers: NONE
- Callees: UErr, exit, printf
- Global read/write: 1/0; field read/write: 23/9
- Pointer modes: ip=READ_ONLY, op=WRITES_THROUGH
- Loops: 3; fixed counts: 12
- Effects: `{"assert": false, "file_io": false, "indirect_call": false, "logging": true, "malloc": false}`
- Proposal: **IO_OR_DEBUG**; purity=False; combinational=False
- Classification evidence:
  - AST observed writes or mutable-state effects: ['data_u.rgb', 'op', 'pic_s.data', 'rgb_s.b', 'rgb_s.g', 'rgb_s.r']
  - AST pointer modes: ['READ_ONLY', 'WRITES_THROUGH']
  - AST observed global reads: rgb_2020_709
  - AST observed field reads: data_u.rgb, data_u.rgb, data_u.rgb, pic_s.bits, pic_s.bits, pic_s.chroma, pic_s.chroma, pic_s.color, pic_s.color, pic_s.data, pic_s.data, pic_s.data, pic_s.h, pic_s.w, rgb_s.b, rgb_s.b, rgb_s.b, rgb_s.g, rgb_s.g, rgb_s.g, rgb_s.r, rgb_s.r, rgb_s.r
  - AST loop count is 3; trip proofs are retained per loop

## `convertbits`

- Source: `utl.c:710`
- Clang USR: `c:@F@convertbits`
- Return: `pic_t *`; parameters: `p: pic_t *`, `newbits: int`
- Callers: main, ppm_write
- Callees: exit, fprintf, pcopy_header, pcreate_ext, printf
- Global read/write: 2/0; field read/write: 259/222
- Pointer modes: p=UNKNOWN
- Loops: 11; fixed counts: UNKNOWN
- Effects: `{"assert": false, "file_io": true, "indirect_call": false, "logging": true, "malloc": false}`
- Proposal: **IO_OR_DEBUG**; purity=False; combinational=False
- Classification evidence:
  - AST observed writes or mutable-state effects: ['bit_convert_rounding', 'data_u.gc', 'data_u.gc_d', 'data_u.gc_s', 'data_u.rgb', 'data_u.rgb_d', 'data_u.rgb_s', 'data_u.yuv', 'data_u.yuv_d', 'data_u.yuv_s', 'pic_s.data', 'rgb_d_s.a', 'rgb_d_s.b', 'rgb_d_s.g', 'rgb_d_s.r', 'rgb_s.a', 'rgb_s.b', 'rgb_s.g', 'rgb_s.r', 'rgb_s_s.a', 'rgb_s_s.b', 'rgb_s_s.g', 'rgb_s_s.r', 'yuv_d_s.a', 'yuv_d_s.u', 'yuv_d_s.v', 'yuv_d_s.y', 'yuv_s.a', 'yuv_s.u', 'yuv_s.v', 'yuv_s.y', 'yuv_s_s.a', 'yuv_s_s.u', 'yuv_s_s.v', 'yuv_s_s.y']
  - AST pointer modes: ['UNKNOWN']
  - AST observed global reads: __stderrp, bit_convert_rounding
  - AST observed field reads: data_u.gc, data_u.gc_d, data_u.gc_s, data_u.rgb, data_u.rgb, data_u.rgb, data_u.rgb, data_u.rgb_d, data_u.rgb_d, data_u.rgb_d, data_u.rgb_d, data_u.rgb_s, data_u.rgb_s, data_u.rgb_s, data_u.rgb_s, data_u.yuv, data_u.yuv, data_u.yuv, data_u.yuv, data_u.yuv, data_u.yuv, data_u.yuv, data_u.yuv, data_u.yuv, data_u.yuv, data_u.yuv, data_u.yuv, data_u.yuv, data_u.yuv, data_u.yuv, data_u.yuv, data_u.yuv, data_u.yuv, data_u.yuv, data_u.yuv, data_u.yuv, data_u.yuv, data_u.yuv, data_u.yuv, data_u.yuv, data_u.yuv, data_u.yuv, data_u.yuv, data_u.yuv, data_u.yuv, data_u.yuv, data_u.yuv, data_u.yuv, data_u.yuv, data_u.yuv, data_u.yuv, data_u.yuv_d, data_u.yuv_d, data_u.yuv_d, data_u.yuv_d, data_u.yuv_s, data_u.yuv_s, data_u.yuv_s, data_u.yuv_s, data_u.yuv_s, data_u.yuv_s, data_u.yuv_s, data_u.yuv_s, data_u.yuv_s, data_u.yuv_s, data_u.yuv_s, data_u.yuv_s, data_u.yuv_s, data_u.yuv_s, data_u.yuv_s, data_u.yuv_s, data_u.yuv_s, data_u.yuv_s, data_u.yuv_s, data_u.yuv_s, pic_s.bits, pic_s.bits, pic_s.bits, pic_s.bits, pic_s.bits, pic_s.bits, pic_s.bits, pic_s.bits, pic_s.bits, pic_s.bits, pic_s.bits, pic_s.bits, pic_s.chroma, pic_s.chroma, pic_s.chroma, pic_s.chroma, pic_s.chroma, pic_s.chroma, pic_s.chroma, pic_s.color, pic_s.color, pic_s.color, pic_s.color, pic_s.color, pic_s.data, pic_s.data, pic_s.data, pic_s.data, pic_s.data, pic_s.data, pic_s.data, pic_s.data, pic_s.data, pic_s.data, pic_s.data, pic_s.data, pic_s.data, pic_s.data, pic_s.data, pic_s.data, pic_s.data, pic_s.data, pic_s.data, pic_s.data, pic_s.data, pic_s.data, pic_s.data, pic_s.data, pic_s.data, pic_s.data, pic_s.data, pic_s.data, pic_s.data, pic_s.data, pic_s.data, pic_s.data, pic_s.data, pic_s.data, pic_s.data, pic_s.data, pic_s.data, pic_s.data, pic_s.data, pic_s.data, pic_s.data, pic_s.data, pic_s.data, pic_s.data, pic_s.data, pic_s.data, pic_s.data, pic_s.data, pic_s.data, pic_s.data, pic_s.data, pic_s.data, pic_s.data, pic_s.data, pic_s.data, pic_s.data, pic_s.data, pic_s.data, pic_s.data, pic_s.data, pic_s.data, pic_s.data, pic_s.data, pic_s.data, pic_s.data, pic_s.data, pic_s.data, pic_s.data, pic_s.data, pic_s.data, pic_s.data, pic_s.data, pic_s.data, pic_s.data, pic_s.data, pic_s.format, pic_s.h, pic_s.h, pic_s.h, pic_s.h, pic_s.h, pic_s.h, pic_s.w, pic_s.w, pic_s.w, pic_s.w, pic_s.w, pic_s.w, rgb_d_s.a, rgb_d_s.b, rgb_d_s.g, rgb_d_s.r, rgb_s.a, rgb_s.b, rgb_s.g, rgb_s.r, rgb_s_s.a, rgb_s_s.b, rgb_s_s.g, rgb_s_s.r, yuv_d_s.a, yuv_d_s.u, yuv_d_s.v, yuv_d_s.y, yuv_s.a, yuv_s.a, yuv_s.a, yuv_s.a, yuv_s.a, yuv_s.a, yuv_s.a, yuv_s.a, yuv_s.a, yuv_s.a, yuv_s.a, yuv_s.a, yuv_s.a, yuv_s.u, yuv_s.u, yuv_s.u, yuv_s.u, yuv_s.u, yuv_s.v, yuv_s.v, yuv_s.v, yuv_s.v, yuv_s.v, yuv_s.y, yuv_s.y, yuv_s.y, yuv_s.y, yuv_s.y, yuv_s.y, yuv_s.y, yuv_s.y, yuv_s.y, yuv_s.y, yuv_s.y, yuv_s.y, yuv_s.y, yuv_s_s.a, yuv_s_s.a, yuv_s_s.a, yuv_s_s.a, yuv_s_s.a, yuv_s_s.a, yuv_s_s.a, yuv_s_s.u, yuv_s_s.u, yuv_s_s.u, yuv_s_s.v, yuv_s_s.v, yuv_s_s.v, yuv_s_s.y, yuv_s_s.y, yuv_s_s.y, yuv_s_s.y, yuv_s_s.y, yuv_s_s.y, yuv_s_s.y
  - AST loop count is 11; trip proofs are retained per loop

## `create_dpx_pic`

- Source: `dpx.c:1420`
- Clang USR: `c:dpx.c@F@create_dpx_pic`
- Return: `int`; parameters: `p: pic_t **`, `chroma: chroma_t`, `color: color_t`, `w: int`, `h: int`, `bits: int`
- Callers: read_dpx_image_data
- Callees: pcreate_ext
- Global read/write: 0/0; field read/write: 9/18
- Pointer modes: p=WRITES_THROUGH
- Loops: 6; fixed counts: UNKNOWN
- Effects: `{"assert": false, "file_io": false, "indirect_call": false, "logging": false, "malloc": false}`
- Proposal: **STATEFUL**; purity=False; combinational=False
- Classification evidence:
  - AST observed writes or mutable-state effects: ['data_u.yuv', 'p', 'pic_s.data', 'yuv_s.u', 'yuv_s.v']
  - AST pointer modes: ['WRITES_THROUGH']
  - AST observed field reads: pic_s.chroma, pic_s.color, pic_s.color, pic_s.h, pic_s.h, pic_s.h, pic_s.w, pic_s.w, pic_s.w
  - AST loop count is 6; trip proofs are retained per loop

## `determine_field_format`

- Source: `dpx.c:67`
- Clang USR: `c:@F@determine_field_format`
- Return: `format_t`; parameters: `file_name: char *`
- Callers: dpx_read_hl
- Callees: chop_ext, ends_in_percentd, free, strlen
- Global read/write: 0/0; field read/write: 0/0
- Pointer modes: file_name=READ_ONLY
- Loops: 0; fixed counts: UNKNOWN
- Effects: `{"assert": false, "file_io": false, "indirect_call": false, "logging": false, "malloc": true}`
- Proposal: **IO_OR_DEBUG**; purity=False; combinational=False
- Classification evidence:
  - AST observed no global/field/pointee writes
  - AST pointer modes: ['READ_ONLY']
  - AST observed no loop

## `distinguish_dist`

- Source: `cmd_parse.c:1084`
- Clang USR: `c:cmd_parse.c@F@distinguish_dist`
- Return: `int *`; parameters: `cmdargs: cmdarg_t *`, `order: int *`, `num_args: int`
- Callers: parse_cmd, parse_cmd_usage
- Callees: Assert_func, calloc, strlen
- Global read/write: 0/0; field read/write: 4/0
- Pointer modes: cmdargs=UNKNOWN, order=WRITES_THROUGH
- Loops: 2; fixed counts: UNKNOWN
- Effects: `{"assert": true, "file_io": false, "indirect_call": false, "logging": false, "malloc": true}`
- Proposal: **IO_OR_DEBUG**; purity=False; combinational=False
- Classification evidence:
  - AST observed writes or mutable-state effects: ['order']
  - AST pointer modes: ['UNKNOWN', 'WRITES_THROUGH']
  - AST observed field reads: cmdarg_s.cmd, cmdarg_s.cmd, cmdarg_s.cmd, cmdarg_s.cmd
  - AST loop count is 2; trip proofs are retained per loop

## `dpx_read`

- Source: `dpx.c:744`
- Clang USR: `c:@F@dpx_read`
- Return: `int`; parameters: `fname: char *`, `p: pic_t **`, `pad_ends: int`, `noswap: int`, `datum_order: int`, `swap_r_and_b: int`
- Callers: main
- Callees: dpx_read_hl
- Global read/write: 0/0; field read/write: 0/0
- Pointer modes: fname=UNKNOWN, p=UNKNOWN
- Loops: 0; fixed counts: UNKNOWN
- Effects: `{"assert": false, "file_io": false, "indirect_call": false, "logging": false, "malloc": false}`
- Proposal: **COMPOSITE_COMB_CANDIDATE**; purity=False; combinational=True
- Classification evidence:
  - AST observed no global/field/pointee writes
  - AST pointer modes: ['UNKNOWN', 'UNKNOWN']
  - AST observed no loop

## `dpx_read_hl`

- Source: `dpx.c:750`
- Clang USR: `c:@F@dpx_read_hl`
- Return: `int`; parameters: `fname: char *`, `p: pic_t **`, `highdata: int *`, `lowdata: int *`, `pad_ends: int`, `noswap: int`, `datum_order: int`, `swap_r_and_b: int`
- Callers: dpx_read, read_dpx
- Callees: __builtin___memcpy_chk, __builtin___memset_chk, __builtin_object_size, determine_field_format, fclose, fgetc, fopen, fprintf, fread, fseek, perror, printf, strcmp, strstr, read_dpx_image_data
- Global read/write: 7/1; field read/write: 119/36
- Pointer modes: fname=UNKNOWN, p=WRITES_THROUGH, highdata=WRITES_THROUGH, lowdata=WRITES_THROUGH
- Loops: 1; fixed counts: UNKNOWN
- Effects: `{"assert": false, "file_io": true, "indirect_call": false, "logging": true, "malloc": false}`
- Proposal: **IO_OR_DEBUG**; purity=False; combinational=False
- Classification evidence:
  - AST observed writes or mutable-state effects: ['_DpxFileFormat.ImageHeader', '_GenericImageHeader.ImageElement', '_ImageElement.HighData', '_ImageElement.LowData', 'highdata', 'lowdata', 'p', 'pic_s.ar1', 'pic_s.ar2', 'pic_s.bits', 'pic_s.color', 'pic_s.colorimetry', 'pic_s.format', 'pic_s.framerate', 'pic_s.frm_no', 'pic_s.interlaced', 'pic_s.seq_len', 'pic_s.transfer', 'show_range_warn']
  - AST pointer modes: ['UNKNOWN', 'WRITES_THROUGH', 'WRITES_THROUGH', 'WRITES_THROUGH']
  - AST observed global reads: __stderrp, __stderrp, __stderrp, __stderrp, __stderrp, __stderrp, show_range_warn
  - AST observed field reads: _DpxFileFormat.FileHeader, _DpxFileFormat.FileHeader, _DpxFileFormat.FileHeader, _DpxFileFormat.FilmHeader, _DpxFileFormat.FilmHeader, _DpxFileFormat.FilmHeader, _DpxFileFormat.FilmHeader, _DpxFileFormat.ImageHeader, _DpxFileFormat.ImageHeader, _DpxFileFormat.ImageHeader, _DpxFileFormat.ImageHeader, _DpxFileFormat.ImageHeader, _DpxFileFormat.ImageHeader, _DpxFileFormat.ImageHeader, _DpxFileFormat.ImageHeader, _DpxFileFormat.ImageHeader, _DpxFileFormat.ImageHeader, _DpxFileFormat.ImageHeader, _DpxFileFormat.ImageHeader, _DpxFileFormat.ImageHeader, _DpxFileFormat.ImageHeader, _DpxFileFormat.ImageHeader, _DpxFileFormat.ImageHeader, _DpxFileFormat.ImageHeader, _DpxFileFormat.ImageHeader, _DpxFileFormat.ImageHeader, _DpxFileFormat.ImageHeader, _DpxFileFormat.ImageHeader, _DpxFileFormat.ImageHeader, _DpxFileFormat.ImageHeader, _DpxFileFormat.ImageHeader, _DpxFileFormat.ImageHeader, _DpxFileFormat.ImageHeader, _DpxFileFormat.ImageHeader, _DpxFileFormat.ImageHeader, _DpxFileFormat.ImageHeader, _DpxFileFormat.ImageHeader, _DpxFileFormat.ImageHeader, _DpxFileFormat.ImageHeader, _DpxFileFormat.OrientHeader, _DpxFileFormat.OrientHeader, _DpxFileFormat.OrientHeader, _DpxFileFormat.TvHeader, _DpxFileFormat.TvHeader, _DpxFileFormat.TvHeader, _GenericFileHeader.Copyright, _GenericFileHeader.Version, _GenericFileHeader.Version, _GenericImageHeader.ImageElement, _GenericImageHeader.ImageElement, _GenericImageHeader.ImageElement, _GenericImageHeader.ImageElement, _GenericImageHeader.ImageElement, _GenericImageHeader.ImageElement, _GenericImageHeader.ImageElement, _GenericImageHeader.ImageElement, _GenericImageHeader.ImageElement, _GenericImageHeader.ImageElement, _GenericImageHeader.ImageElement, _GenericImageHeader.ImageElement, _GenericImageHeader.ImageElement, _GenericImageHeader.ImageElement, _GenericImageHeader.ImageElement, _GenericImageHeader.ImageElement, _GenericImageHeader.ImageElement, _GenericImageHeader.ImageElement, _GenericImageHeader.ImageElement, _GenericImageHeader.ImageElement, _GenericImageHeader.ImageElement, _GenericImageHeader.ImageElement, _GenericImageHeader.ImageElement, _GenericImageHeader.ImageElement, _GenericImageHeader.ImageElement, _GenericImageHeader.ImageElement, _GenericImageHeader.ImageElement, _GenericImageHeader.LinesPerElement, _GenericImageHeader.NumberElements, _GenericImageHeader.Orientation, _GenericImageHeader.Orientation, _GenericImageHeader.PixelsPerLine, _GenericOrientationHeader.AspectRatio, _GenericOrientationHeader.AspectRatio, _GenericOrientationHeader.AspectRatio, _ImageElement.BitSize, _ImageElement.BitSize, _ImageElement.BitSize, _ImageElement.BitSize, _ImageElement.BitSize, _ImageElement.Colorimetric, _ImageElement.DataOffset, _ImageElement.DataOffset, _ImageElement.DataSign, _ImageElement.DataSign, _ImageElement.Descriptor, _ImageElement.Descriptor, _ImageElement.Descriptor, _ImageElement.Descriptor, _ImageElement.Encoding, _ImageElement.Encoding, _ImageElement.HighData, _ImageElement.HighData, _ImageElement.HighData, _ImageElement.HighData, _ImageElement.LowData, _ImageElement.LowData, _ImageElement.LowData, _ImageElement.LowData, _ImageElement.Packing, _ImageElement.Packing, _ImageElement.Transfer, _IndustryFilmInfoHeader.FramePosition, _IndustryFilmInfoHeader.FramePosition, _IndustryFilmInfoHeader.SequenceLen, _IndustryFilmInfoHeader.SequenceLen, _IndustryTelevisionInfoHeader.FrameRate, _IndustryTelevisionInfoHeader.Interlace, _IndustryTelevisionInfoHeader.Interlace, pic_s.color, pic_s.framerate
  - AST loop count is 1; trip proofs are retained per loop

## `dpx_write`

- Source: `dpx.c:225`
- Clang USR: `c:@F@dpx_write`
- Return: `int`; parameters: `fname: char *`, `p: pic_t *`, `pad_ends: int`, `datum_order: int`, `force_packing: int`, `swaprb: int`, `wbswap: int`
- Callers: main
- Callees: write_dpx_ver
- Global read/write: 0/0; field read/write: 7/0
- Pointer modes: fname=UNKNOWN, p=UNKNOWN
- Loops: 0; fixed counts: UNKNOWN
- Effects: `{"assert": false, "file_io": false, "indirect_call": false, "logging": false, "malloc": false}`
- Proposal: **COMPOSITE_COMB_CANDIDATE**; purity=False; combinational=True
- Classification evidence:
  - AST observed no global/field/pointee writes
  - AST pointer modes: ['UNKNOWN', 'UNKNOWN']
  - AST observed field reads: pic_s.ar1, pic_s.ar2, pic_s.bits, pic_s.framerate, pic_s.frm_no, pic_s.interlaced, pic_s.seq_len
  - AST observed no loop

## `easy_mkdir`

- Source: `cmd_parse.c:220`
- Clang USR: `c:@F@easy_mkdir`
- Return: `int`; parameters: `dn: const char *`
- Callers: NONE
- Callees: PErr, __builtin___strncat_chk, __builtin_object_size, closedir, file_dir, free, has_ext, opendir, system
- Global read/write: 0/0; field read/write: 0/0
- Pointer modes: dn=UNKNOWN
- Loops: 0; fixed counts: UNKNOWN
- Effects: `{"assert": false, "file_io": false, "indirect_call": false, "logging": false, "malloc": true}`
- Proposal: **IO_OR_DEBUG**; purity=False; combinational=False
- Classification evidence:
  - AST observed no global/field/pointee writes
  - AST pointer modes: ['UNKNOWN']
  - AST observed no loop

## `ends_in_percentd`

- Source: `dpx.c:86`
- Clang USR: `c:@F@ends_in_percentd`
- Return: `int`; parameters: `str: char *`, `length: int`
- Callers: determine_field_format
- Callees: NONE
- Global read/write: 0/0; field read/write: 0/0
- Pointer modes: str=READ_ONLY
- Loops: 1; fixed counts: UNKNOWN
- Effects: `{"assert": false, "file_io": false, "indirect_call": false, "logging": false, "malloc": false}`
- Proposal: **PURE_COMB_CANDIDATE**; purity=True; combinational=True
- Classification evidence:
  - AST observed no global/field/pointee writes
  - AST pointer modes: ['READ_ONLY']
  - AST loop count is 1; trip proofs are retained per loop
  - No direct calls and no non-const global read were observed

## `error_check`

- Source: `cmd_parse.c:952`
- Clang USR: `c:cmd_parse.c@F@error_check`
- Return: `void`; parameters: `cmdargs: cmdarg_t *`, `num_args: const int`, `cmd: const int`
- Callers: parse_cmd, parse_line
- Callees: CErr, UErr, strcmp
- Global read/write: 0/0; field read/write: 40/1
- Pointer modes: cmdargs=UNKNOWN
- Loops: 3; fixed counts: UNKNOWN
- Effects: `{"assert": false, "file_io": false, "indirect_call": false, "logging": true, "malloc": false}`
- Proposal: **IO_OR_DEBUG**; purity=False; combinational=False
- Classification evidence:
  - AST observed writes or mutable-state effects: ['cmdarg_s.value']
  - AST pointer modes: ['UNKNOWN']
  - AST observed field reads: cmdarg_s.cmd, cmdarg_s.cmd, cmdarg_s.cmd, cmdarg_s.cmd, cmdarg_s.cmd, cmdarg_s.cmd, cmdarg_s.cmd, cmdarg_s.cmd, cmdarg_s.key, cmdarg_s.key, cmdarg_s.key, cmdarg_s.key, cmdarg_s.key, cmdarg_s.key, cmdarg_s.key, cmdarg_s.key, cmdarg_s.type, cmdarg_s.type, cmdarg_s.type, cmdarg_s.type, cmdarg_s.type, cmdarg_s.type, cmdarg_s.type, cmdarg_s.type, cmdarg_s.type, cmdarg_s.type, cmdarg_s.type, cmdarg_s.type, cmdarg_s.type, cmdarg_s.type, cmdarg_s.type, cmdarg_s.type, cmdarg_s.type, cmdarg_s.type, cmdarg_s.vct_lng, cmdarg_s.vct_lng, cmdarg_s.vct_lng, cmdarg_s.vct_lng, cmdarg_s.vct_lng, cmdarg_s.vct_lng
  - AST loop count is 3; trip proofs are retained per loop

## `fifo_clear`

- Source: `fifo.c:55`
- Clang USR: `c:@F@fifo_clear`
- Return: `void`; parameters: `fifo: fifo_t *`
- Callers: hdr_dpx_get_pic_data
- Callees: NONE
- Global read/write: 0/0; field read/write: 0/5
- Pointer modes: fifo=WRITES_THROUGH
- Loops: 0; fixed counts: UNKNOWN
- Effects: `{"assert": false, "file_io": false, "indirect_call": false, "logging": false, "malloc": false}`
- Proposal: **STATEFUL**; purity=False; combinational=False
- Classification evidence:
  - AST observed writes or mutable-state effects: ['fifo', 'fifo_s.byte_ctr', 'fifo_s.fullness', 'fifo_s.max_fullness', 'fifo_s.read_ptr', 'fifo_s.write_ptr']
  - AST pointer modes: ['WRITES_THROUGH']
  - AST observed no loop

## `fifo_clone`

- Source: `fifo.c:146`
- Clang USR: `c:@F@fifo_clone`
- Return: `void`; parameters: `dst: fifo_t *`, `src: fifo_t *`
- Callers: NONE
- Callees: fifo_free, fifo_get_bits, fifo_init, fifo_put_bits
- Global read/write: 0/0; field read/write: 8/0
- Pointer modes: dst=UNKNOWN, src=UNKNOWN
- Loops: 2; fixed counts: UNKNOWN
- Effects: `{"assert": false, "file_io": false, "indirect_call": false, "logging": false, "malloc": false}`
- Proposal: **COMPOSITE_COMB_CANDIDATE**; purity=False; combinational=True
- Classification evidence:
  - AST observed no global/field/pointee writes
  - AST pointer modes: ['UNKNOWN', 'UNKNOWN']
  - AST observed field reads: fifo_s.fullness, fifo_s.fullness, fifo_s.fullness, fifo_s.fullness, fifo_s.fullness, fifo_s.fullness, fifo_s.size, fifo_s.size
  - AST loop count is 2; trip proofs are retained per loop

## `fifo_flip_get_bits`

- Source: `fifo.c:174`
- Clang USR: `c:@F@fifo_flip_get_bits`
- Return: `int`; parameters: `fifo: fifo_t *`, `n: int`, `sign_extend: int`
- Callers: hdr_dpx_get_datum, hdr_dpx_get_pic_data, read_dpx_image_data
- Callees: exit, printf
- Global read/write: 0/0; field read/write: 7/3
- Pointer modes: fifo=WRITES_THROUGH
- Loops: 1; fixed counts: UNKNOWN
- Effects: `{"assert": false, "file_io": false, "indirect_call": false, "logging": true, "malloc": false}`
- Proposal: **IO_OR_DEBUG**; purity=False; combinational=False
- Classification evidence:
  - AST observed writes or mutable-state effects: ['fifo', 'fifo_s.fullness', 'fifo_s.read_ptr']
  - AST pointer modes: ['WRITES_THROUGH']
  - AST observed field reads: fifo_s.data, fifo_s.fullness, fifo_s.read_ptr, fifo_s.read_ptr, fifo_s.read_ptr, fifo_s.read_ptr, fifo_s.size
  - AST loop count is 1; trip proofs are retained per loop

## `fifo_flip_put_bits`

- Source: `fifo.c:217`
- Clang USR: `c:@F@fifo_flip_put_bits`
- Return: `void`; parameters: `fifo: fifo_t *`, `d: unsigned int`, `nbits: int`
- Callers: hdr_dpx_write, write_dpx_ver
- Callees: exit, printf
- Global read/write: 0/0; field read/write: 10/6
- Pointer modes: fifo=WRITES_THROUGH
- Loops: 1; fixed counts: UNKNOWN
- Effects: `{"assert": false, "file_io": false, "indirect_call": false, "logging": true, "malloc": false}`
- Proposal: **IO_OR_DEBUG**; purity=False; combinational=False
- Classification evidence:
  - AST observed writes or mutable-state effects: ['fifo', 'fifo_s.data', 'fifo_s.fullness', 'fifo_s.max_fullness', 'fifo_s.write_ptr']
  - AST pointer modes: ['WRITES_THROUGH']
  - AST observed field reads: fifo_s.fullness, fifo_s.fullness, fifo_s.fullness, fifo_s.max_fullness, fifo_s.size, fifo_s.size, fifo_s.write_ptr, fifo_s.write_ptr, fifo_s.write_ptr, fifo_s.write_ptr
  - AST loop count is 1; trip proofs are retained per loop

## `fifo_free`

- Source: `fifo.c:66`
- Clang USR: `c:@F@fifo_free`
- Return: `void`; parameters: `fifo: fifo_t *`
- Callers: DSC_Algorithm, fifo_clone, hdr_dpx_write
- Callees: free
- Global read/write: 0/0; field read/write: 1/0
- Pointer modes: fifo=UNKNOWN
- Loops: 0; fixed counts: UNKNOWN
- Effects: `{"assert": false, "file_io": false, "indirect_call": false, "logging": false, "malloc": true}`
- Proposal: **IO_OR_DEBUG**; purity=False; combinational=False
- Classification evidence:
  - AST observed no global/field/pointee writes
  - AST pointer modes: ['UNKNOWN']
  - AST observed field reads: fifo_s.data
  - AST observed no loop

## `fifo_get_bits`

- Source: `fifo.c:77`
- Clang USR: `c:@F@fifo_get_bits`
- Return: `int`; parameters: `fifo: fifo_t *`, `n: int`, `sign_extend: int`
- Callers: GetBits, ProcessGroupEnc, WriteEntryToBitstream, fifo_clone, hdr_dpx_get_datum, hdr_dpx_get_pic_data, hdr_dpx_write, write_dpx_ver, read_dpx_image_data
- Callees: exit, printf
- Global read/write: 0/0; field read/write: 6/3
- Pointer modes: fifo=WRITES_THROUGH
- Loops: 1; fixed counts: UNKNOWN
- Effects: `{"assert": false, "file_io": false, "indirect_call": false, "logging": true, "malloc": false}`
- Proposal: **IO_OR_DEBUG**; purity=False; combinational=False
- Classification evidence:
  - AST observed writes or mutable-state effects: ['fifo', 'fifo_s.fullness', 'fifo_s.read_ptr']
  - AST pointer modes: ['WRITES_THROUGH']
  - AST observed field reads: fifo_s.data, fifo_s.fullness, fifo_s.read_ptr, fifo_s.read_ptr, fifo_s.read_ptr, fifo_s.size
  - AST loop count is 1; trip proofs are retained per loop

## `fifo_init`

- Source: `fifo.c:43`
- Clang USR: `c:@F@fifo_init`
- Return: `void`; parameters: `fifo: fifo_t *`, `size: int`
- Callers: InitializeDSCState, fifo_clone, hdr_dpx_get_pic_data, hdr_dpx_write, write_dpx_ver, read_dpx_image_data
- Callees: malloc
- Global read/write: 0/0; field read/write: 0/7
- Pointer modes: fifo=WRITES_THROUGH
- Loops: 0; fixed counts: UNKNOWN
- Effects: `{"assert": false, "file_io": false, "indirect_call": false, "logging": false, "malloc": true}`
- Proposal: **IO_OR_DEBUG**; purity=False; combinational=False
- Classification evidence:
  - AST observed writes or mutable-state effects: ['fifo', 'fifo_s.byte_ctr', 'fifo_s.data', 'fifo_s.fullness', 'fifo_s.max_fullness', 'fifo_s.read_ptr', 'fifo_s.size', 'fifo_s.write_ptr']
  - AST pointer modes: ['WRITES_THROUGH']
  - AST observed no loop

## `fifo_put_bits`

- Source: `fifo.c:115`
- Clang USR: `c:@F@fifo_put_bits`
- Return: `void`; parameters: `fifo: fifo_t *`, `d: unsigned int`, `nbits: int`
- Callers: AddBits, ProcessGroupDec, ProcessGroupEnc, VLCGroup, fifo_clone, hdr_dpx_get_pic_data, hdr_dpx_write, write_dpx_ver, read_dpx_image_data
- Callees: exit, printf
- Global read/write: 0/0; field read/write: 11/6
- Pointer modes: fifo=WRITES_THROUGH
- Loops: 1; fixed counts: UNKNOWN
- Effects: `{"assert": false, "file_io": false, "indirect_call": false, "logging": true, "malloc": false}`
- Proposal: **IO_OR_DEBUG**; purity=False; combinational=False
- Classification evidence:
  - AST observed writes or mutable-state effects: ['fifo', 'fifo_s.data', 'fifo_s.fullness', 'fifo_s.max_fullness', 'fifo_s.write_ptr']
  - AST pointer modes: ['WRITES_THROUGH']
  - AST observed field reads: fifo_s.fullness, fifo_s.fullness, fifo_s.fullness, fifo_s.max_fullness, fifo_s.size, fifo_s.size, fifo_s.write_ptr, fifo_s.write_ptr, fifo_s.write_ptr, fifo_s.write_ptr, fifo_s.write_ptr
  - AST loop count is 1; trip proofs are retained per loop

## `file_dir`

- Source: `cmd_parse.c:189`
- Clang USR: `c:@F@file_dir`
- Return: `char *`; parameters: `path: const char *`
- Callers: easy_mkdir
- Callees: __builtin___strcpy_chk, __builtin___strncpy_chk, __builtin_object_size, malloc, strlen, strrchr
- Global read/write: 0/0; field read/write: 0/0
- Pointer modes: path=READ_ONLY
- Loops: 0; fixed counts: UNKNOWN
- Effects: `{"assert": false, "file_io": false, "indirect_call": false, "logging": false, "malloc": true}`
- Proposal: **IO_OR_DEBUG**; purity=False; combinational=False
- Classification evidence:
  - AST observed no global/field/pointee writes
  - AST pointer modes: ['READ_ONLY']
  - AST observed no loop

## `file_ext`

- Source: `cmd_parse.c:161`
- Clang USR: `c:@F@file_ext`
- Return: `char *`; parameters: `path: const char *`
- Callers: NONE
- Callees: __builtin___strcpy_chk, __builtin_object_size, malloc, strlen, strrchr
- Global read/write: 0/0; field read/write: 0/0
- Pointer modes: path=READ_ONLY
- Loops: 0; fixed counts: UNKNOWN
- Effects: `{"assert": false, "file_io": false, "indirect_call": false, "logging": false, "malloc": true}`
- Proposal: **IO_OR_DEBUG**; purity=False; combinational=False
- Classification evidence:
  - AST observed no global/field/pointee writes
  - AST pointer modes: ['READ_ONLY']
  - AST observed no loop

## `generate_rc_parameters`

- Source: `codec_main.c:904`
- Clang USR: `c:@F@generate_rc_parameters`
- Return: `void`; parameters: `dsc_codec: dsc_cfg_t *`
- Callers: populate_pps
- Callees: UErr, make_qp_tables
- Global read/write: 66/4; field read/write: 11/57
- Pointer modes: dsc_codec=WRITES_THROUGH
- Loops: 1; fixed counts: 15
- Effects: `{"assert": false, "file_io": false, "indirect_call": false, "logging": true, "malloc": false}`
- Proposal: **IO_OR_DEBUG**; purity=False; combinational=False
- Classification evidence:
  - AST observed writes or mutable-state effects: ['bitsPerComponent', 'bitsPerPixel', 'dscVersionMinor', 'dsc_cfg_t.flatness_det_thresh', 'dsc_cfg_t.flatness_max_qp', 'dsc_cfg_t.flatness_min_qp', 'dsc_cfg_t.initial_offset', 'dsc_cfg_t.initial_xmit_delay', 'dsc_cfg_t.rc_quant_incr_limit0', 'dsc_cfg_t.rc_quant_incr_limit1', 'dsc_cfg_t.rc_range_parameters', 'dsc_cfg_t.second_line_ofs_adj', 'dsc_codec', 'dsc_range_cfg_t.range_bpg_offset', 'dsc_range_cfg_t.range_max_qp', 'dsc_range_cfg_t.range_min_qp', 'firstLineBpgOfs', 'initialDelay', 'initialFullnessOfs', 'native420', 'native422', 'secondLineBpgOfs', 'useYuvInput']
  - AST pointer modes: ['WRITES_THROUGH']
  - AST observed global reads: bitsPerComponent, bitsPerComponent, bitsPerComponent, bitsPerComponent, bitsPerComponent, bitsPerComponent, bitsPerComponent, bitsPerComponent, bitsPerComponent, bitsPerComponent, bitsPerComponent, bitsPerPixel, bitsPerPixel, bitsPerPixel, bitsPerPixel, bitsPerPixel, bitsPerPixel, bitsPerPixel, bitsPerPixel, bitsPerPixel, bitsPerPixel, bitsPerPixel, bitsPerPixel, bitsPerPixel, bitsPerPixel, bitsPerPixel, bitsPerPixel, bitsPerPixel, bitsPerPixel, bitsPerPixel, bitsPerPixel, bitsPerPixel, bitsPerPixel, bitsPerPixel, bitsPerPixel, bitsPerPixel, bitsPerPixel, bitsPerPixel, bitsPerPixel, bitsPerPixel, bitsPerPixel, bitsPerPixel, bitsPerPixel, bitsPerPixel, bitsPerPixel, dscVersionMinor, dscVersionMinor, dscVersionMinor, dscVersionMinor, maxqp_420, maxqp_422, maxqp_444, minqp_420, minqp_422, minqp_444, native420, native420, native420, native422, native422, native422, native422, useYuvInput, useYuvInput, useYuvInput, useYuvInput
  - AST observed field reads: dsc_cfg_t.initial_offset, dsc_cfg_t.initial_xmit_delay, dsc_cfg_t.initial_xmit_delay, dsc_cfg_t.initial_xmit_delay, dsc_cfg_t.initial_xmit_delay, dsc_cfg_t.rc_range_parameters, dsc_cfg_t.rc_range_parameters, dsc_cfg_t.slice_width, dsc_cfg_t.slice_width, dsc_range_cfg_t.range_max_qp, dsc_range_cfg_t.range_max_qp
  - AST loop count is 1; trip proofs are retained per loop

## `generate_timecode`

- Source: `dpx.c:708`
- Clang USR: `c:dpx.c@F@generate_timecode`
- Return: `DWORD`; parameters: `frameno: int`, `framerate: float`
- Callers: write_dpx_ver
- Callees: NONE
- Global read/write: 0/0; field read/write: 0/0
- Pointer modes: NONE
- Loops: 0; fixed counts: UNKNOWN
- Effects: `{"assert": false, "file_io": false, "indirect_call": false, "logging": false, "malloc": false}`
- Proposal: **PURE_COMB_CANDIDATE**; purity=True; combinational=True
- Classification evidence:
  - AST observed no global/field/pointee writes
  - AST observed no loop
  - No direct calls and no non-const global read were observed

## `getbits`

- Source: `dsc_utils.c:109`
- Clang USR: `c:@F@getbits`
- Return: `int`; parameters: `size: int`, `buf: unsigned char *`, `bit_count: int *`, `sign_extend: int`
- Callers: ProcessGroupDec, ProcessGroupEnc, parse_pps
- Callees: NONE
- Global read/write: 0/0; field read/write: 0/0
- Pointer modes: buf=READ_ONLY, bit_count=WRITES_THROUGH
- Loops: 1; fixed counts: UNKNOWN
- Effects: `{"assert": false, "file_io": false, "indirect_call": false, "logging": false, "malloc": false}`
- Proposal: **STATEFUL**; purity=False; combinational=False
- Classification evidence:
  - AST observed writes or mutable-state effects: ['bit_count']
  - AST pointer modes: ['READ_ONLY', 'WRITES_THROUGH']
  - AST loop count is 1; trip proofs are retained per loop

## `gettoken`

- Source: `utl.c:1038`
- Clang USR: `c:@F@gettoken`
- Return: `void`; parameters: `fp: FILE *`, `token: char *`, `line: char *`, `pos: int *`
- Callers: readppm
- Callees: fgets
- Global read/write: 0/0; field read/write: 0/0
- Pointer modes: fp=UNKNOWN, token=WRITES_THROUGH, line=UNKNOWN, pos=WRITES_THROUGH
- Loops: 2; fixed counts: UNKNOWN
- Effects: `{"assert": false, "file_io": false, "indirect_call": false, "logging": false, "malloc": false}`
- Proposal: **STATEFUL**; purity=False; combinational=False
- Classification evidence:
  - AST observed writes or mutable-state effects: ['pos', 'token']
  - AST pointer modes: ['UNKNOWN', 'UNKNOWN', 'WRITES_THROUGH', 'WRITES_THROUGH']
  - AST loop count is 2; trip proofs are retained per loop

## `has_ext`

- Source: `cmd_parse.c:84`
- Clang USR: `c:@F@has_ext`
- Return: `int`; parameters: `path: const char *`
- Callers: easy_mkdir
- Callees: strlen, strrchr
- Global read/write: 0/0; field read/write: 0/0
- Pointer modes: path=READ_ONLY
- Loops: 0; fixed counts: UNKNOWN
- Effects: `{"assert": false, "file_io": false, "indirect_call": false, "logging": false, "malloc": false}`
- Proposal: **COMPOSITE_COMB_CANDIDATE**; purity=False; combinational=True
- Classification evidence:
  - AST observed no global/field/pointee writes
  - AST pointer modes: ['READ_ONLY']
  - AST observed no loop

## `hdr_dpx_byte_swap`

- Source: `hdr_dpx.c:1445`
- Clang USR: `c:@F@hdr_dpx_byte_swap`
- Return: `void`; parameters: `f: HDRDPXFILEFORMAT *`
- Callers: hdr_dpx_read, hdr_dpx_write
- Callees: NONE
- Global read/write: 0/0; field read/write: 0/0
- Pointer modes: f=READ_ONLY
- Loops: 2; fixed counts: 8, 4
- Effects: `{"assert": false, "file_io": false, "indirect_call": false, "logging": false, "malloc": false}`
- Proposal: **PURE_COMB_CANDIDATE**; purity=True; combinational=True
- Classification evidence:
  - AST observed no global/field/pointee writes
  - AST pointer modes: ['READ_ONLY']
  - AST loop count is 2; trip proofs are retained per loop
  - No direct calls and no non-const global read were observed

## `hdr_dpx_check_string`

- Source: `hdr_dpx.c:1537`
- Clang USR: `c:hdr_dpx.c@F@hdr_dpx_check_string`
- Return: `void`; parameters: `str: char *`, `size: int`
- Callers: hdr_dpx_fill_core_fields
- Callees: NONE
- Global read/write: 0/0; field read/write: 0/0
- Pointer modes: str=WRITES_THROUGH
- Loops: 1; fixed counts: UNKNOWN
- Effects: `{"assert": false, "file_io": false, "indirect_call": false, "logging": false, "malloc": false}`
- Proposal: **STATEFUL**; purity=False; combinational=False
- Classification evidence:
  - AST observed writes or mutable-state effects: ['str']
  - AST pointer modes: ['WRITES_THROUGH']
  - AST loop count is 1; trip proofs are retained per loop

## `hdr_dpx_compute_offsets`

- Source: `hdr_dpx.c:1514`
- Clang USR: `c:@F@hdr_dpx_compute_offsets`
- Return: `int`; parameters: `dpxh: HDRDPXFILEFORMAT *`, `dpxu: HDRDPXUSERDATA *`, `dpxsbm: HDRDPXSBMDATA *`
- Callers: hdr_dpx_write
- Callees: fprintf
- Global read/write: 1/0; field read/write: 8/4
- Pointer modes: dpxh=WRITES_THROUGH, dpxu=READ_ONLY, dpxsbm=READ_ONLY
- Loops: 0; fixed counts: UNKNOWN
- Effects: `{"assert": false, "file_io": true, "indirect_call": false, "logging": false, "malloc": false}`
- Proposal: **IO_OR_DEBUG**; purity=False; combinational=False
- Classification evidence:
  - AST observed writes or mutable-state effects: ['_HDRDPX_GenericFileHeader.ImageOffset', '_HDRDPX_GenericFileHeader.StandardsBasedMetadataOffset', '_HdrDpxFileFormat.FileHeader', 'dpxh']
  - AST pointer modes: ['READ_ONLY', 'READ_ONLY', 'WRITES_THROUGH']
  - AST observed global reads: __stderrp
  - AST observed field reads: _HDRDPX_GenericFileHeader.ImageOffset, _HDRDPX_GenericFileHeader.ImageOffset, _HDRDPX_GenericFileHeader.ImageOffset, _HDRDPX_GenericFileHeader.UserSize, _HdrDpxFileFormat.FileHeader, _HdrDpxFileFormat.FileHeader, _HdrDpxFileFormat.FileHeader, _HdrDpxFileFormat.FileHeader
  - AST observed no loop

## `hdr_dpx_create_pic`

- Source: `hdr_dpx.c:234`
- Clang USR: `c:@F@hdr_dpx_create_pic`
- Return: `int`; parameters: `f: HDRDPXFILEFORMAT *`, `out_pic: pic_t **`
- Callers: hdr_dpx_get_pic_data
- Callees: fprintf, memcmp, pcreate_ext
- Global read/write: 23/0; field read/write: 83/43
- Pointer modes: f=READ_ONLY, out_pic=WRITES_THROUGH
- Loops: 1; fixed counts: UNKNOWN
- Effects: `{"assert": false, "file_io": true, "indirect_call": false, "logging": false, "malloc": false}`
- Proposal: **IO_OR_DEBUG**; purity=False; combinational=False
- Classification evidence:
  - AST observed writes or mutable-state effects: ['out_pic', 'pic_s.alpha', 'pic_s.ar1', 'pic_s.ar2', 'pic_s.chroma_siting', 'pic_s.colorimetry', 'pic_s.framerate', 'pic_s.frm_no', 'pic_s.interlaced', 'pic_s.limited_range', 'pic_s.seq_len', 'pic_s.transfer']
  - AST pointer modes: ['READ_ONLY', 'WRITES_THROUGH']
  - AST observed global reads: __stderrp, __stderrp, __stderrp, __stderrp, __stderrp, __stderrp, __stderrp, __stderrp, __stderrp, __stderrp, __stderrp, __stderrp, __stderrp, __stderrp, __stderrp, __stderrp, __stderrp, __stderrp, __stderrp, __stderrp, __stderrp, undefined_4bytes, undefined_4bytes
  - AST observed field reads: _HDRDPX_GenericImageHeader.ChromaSubsampling, _HDRDPX_GenericImageHeader.ChromaSubsampling, _HDRDPX_GenericImageHeader.ChromaSubsampling, _HDRDPX_GenericImageHeader.ChromaSubsampling, _HDRDPX_GenericImageHeader.ImageElement, _HDRDPX_GenericImageHeader.ImageElement, _HDRDPX_GenericImageHeader.ImageElement, _HDRDPX_GenericImageHeader.ImageElement, _HDRDPX_GenericImageHeader.ImageElement, _HDRDPX_GenericImageHeader.ImageElement, _HDRDPX_GenericImageHeader.ImageElement, _HDRDPX_GenericImageHeader.ImageElement, _HDRDPX_GenericImageHeader.ImageElement, _HDRDPX_GenericImageHeader.ImageElement, _HDRDPX_GenericImageHeader.ImageElement, _HDRDPX_GenericImageHeader.ImageElement, _HDRDPX_GenericImageHeader.LinesPerElement, _HDRDPX_GenericImageHeader.NumberElements, _HDRDPX_GenericImageHeader.PixelsPerLine, _HDRDPX_GenericSourceInfoHeader.AspectRatio, _HDRDPX_GenericSourceInfoHeader.AspectRatio, _HDRDPX_GenericSourceInfoHeader.AspectRatio, _HDRDPX_GenericSourceInfoHeader.AspectRatio, _HDRDPX_HiLoCode.d, _HDRDPX_ImageElement.BitSize, _HDRDPX_ImageElement.BitSize, _HDRDPX_ImageElement.BitSize, _HDRDPX_ImageElement.BitSize, _HDRDPX_ImageElement.Colorimetric, _HDRDPX_ImageElement.Colorimetric, _HDRDPX_ImageElement.Colorimetric, _HDRDPX_ImageElement.Descriptor, _HDRDPX_ImageElement.LowData, _HDRDPX_ImageElement.Transfer, _HDRDPX_ImageElement.Transfer, _HDRDPX_ImageElement.Transfer, _HDRDPX_IndustryFilmInfoHeader.FramePosition, _HDRDPX_IndustryFilmInfoHeader.FramePosition, _HDRDPX_IndustryFilmInfoHeader.FrameRate, _HDRDPX_IndustryFilmInfoHeader.FrameRate, _HDRDPX_IndustryFilmInfoHeader.SequenceLen, _HDRDPX_IndustryFilmInfoHeader.SequenceLen, _HDRDPX_IndustryTelevisionInfoHeader.FieldNumber, _HDRDPX_IndustryTelevisionInfoHeader.FrameRate, _HDRDPX_IndustryTelevisionInfoHeader.FrameRate, _HDRDPX_IndustryTelevisionInfoHeader.Interlace, _HDRDPX_IndustryTelevisionInfoHeader.Interlace, _HDRDPX_IndustryTelevisionInfoHeader.Interlace, _HdrDpxFileFormat.FilmHeader, _HdrDpxFileFormat.FilmHeader, _HdrDpxFileFormat.FilmHeader, _HdrDpxFileFormat.FilmHeader, _HdrDpxFileFormat.FilmHeader, _HdrDpxFileFormat.FilmHeader, _HdrDpxFileFormat.ImageHeader, _HdrDpxFileFormat.ImageHeader, _HdrDpxFileFormat.ImageHeader, _HdrDpxFileFormat.ImageHeader, _HdrDpxFileFormat.ImageHeader, _HdrDpxFileFormat.ImageHeader, _HdrDpxFileFormat.ImageHeader, _HdrDpxFileFormat.ImageHeader, _HdrDpxFileFormat.ImageHeader, _HdrDpxFileFormat.ImageHeader, _HdrDpxFileFormat.ImageHeader, _HdrDpxFileFormat.ImageHeader, _HdrDpxFileFormat.ImageHeader, _HdrDpxFileFormat.ImageHeader, _HdrDpxFileFormat.ImageHeader, _HdrDpxFileFormat.ImageHeader, _HdrDpxFileFormat.ImageHeader, _HdrDpxFileFormat.ImageHeader, _HdrDpxFileFormat.ImageHeader, _HdrDpxFileFormat.SourceInfoHeader, _HdrDpxFileFormat.SourceInfoHeader, _HdrDpxFileFormat.SourceInfoHeader, _HdrDpxFileFormat.SourceInfoHeader, _HdrDpxFileFormat.TvHeader, _HdrDpxFileFormat.TvHeader, _HdrDpxFileFormat.TvHeader, _HdrDpxFileFormat.TvHeader, _HdrDpxFileFormat.TvHeader, _HdrDpxFileFormat.TvHeader
  - AST loop count is 1; trip proofs are retained per loop

## `hdr_dpx_determine_file_type`

- Source: `hdr_dpx.c:2051`
- Clang USR: `c:@F@hdr_dpx_determine_file_type`
- Return: `int`; parameters: `fname: char *`
- Callers: main
- Callees: fclose, fopen, fprintf, fread, strcmp
- Global read/write: 2/0; field read/write: 6/0
- Pointer modes: fname=UNKNOWN
- Loops: 0; fixed counts: UNKNOWN
- Effects: `{"assert": false, "file_io": true, "indirect_call": false, "logging": false, "malloc": false}`
- Proposal: **IO_OR_DEBUG**; purity=False; combinational=False
- Classification evidence:
  - AST observed no global/field/pointee writes
  - AST pointer modes: ['UNKNOWN']
  - AST observed global reads: __stderrp, __stderrp
  - AST observed field reads: _HDRDPX_GenericFileHeader.Version, _HDRDPX_GenericFileHeader.Version, _HDRDPX_GenericFileHeader.Version, _HdrDpxFileFormat.FileHeader, _HdrDpxFileFormat.FileHeader, _HdrDpxFileFormat.FileHeader
  - AST observed no loop

## `hdr_dpx_fill_core_fields`

- Source: `hdr_dpx.c:1551`
- Clang USR: `c:@F@hdr_dpx_fill_core_fields`
- Return: `int`; parameters: `dpxh: HDRDPXFILEFORMAT *`, `p: pic_t *`
- Callers: hdr_dpx_write
- Callees: __builtin___sprintf_chk, __builtin_object_size, fprintf, memcmp, hdr_dpx_check_string
- Global read/write: 5/0; field read/write: 197/202
- Pointer modes: dpxh=UNKNOWN, p=UNKNOWN
- Loops: 1; fixed counts: UNKNOWN
- Effects: `{"assert": false, "file_io": true, "indirect_call": false, "logging": true, "malloc": false}`
- Proposal: **IO_OR_DEBUG**; purity=False; combinational=False
- Classification evidence:
  - AST observed writes or mutable-state effects: ['_HDRDPX_GenericFileHeader.DatumMappingDirection', '_HDRDPX_GenericFileHeader.GenericSize', '_HDRDPX_GenericFileHeader.IndustrySize', '_HDRDPX_GenericFileHeader.Magic', '_HDRDPX_GenericFileHeader.UserSize', '_HDRDPX_GenericImageHeader.ChromaSubsampling', '_HDRDPX_GenericImageHeader.ImageElement', '_HDRDPX_GenericImageHeader.LinesPerElement', '_HDRDPX_GenericImageHeader.NumberElements', '_HDRDPX_GenericImageHeader.Orientation', '_HDRDPX_GenericImageHeader.PixelsPerLine', '_HDRDPX_GenericSourceInfoHeader.AspectRatio', '_HDRDPX_HiLoCode.d', '_HDRDPX_HiLoCode.f', '_HDRDPX_ImageElement.BitSize', '_HDRDPX_ImageElement.Colorimetric', '_HDRDPX_ImageElement.DataSign', '_HDRDPX_ImageElement.Descriptor', '_HDRDPX_ImageElement.Encoding', '_HDRDPX_ImageElement.EndOfImagePadding', '_HDRDPX_ImageElement.EndOfLinePadding', '_HDRDPX_ImageElement.HighData', '_HDRDPX_ImageElement.LowData', '_HDRDPX_ImageElement.Packing', '_HDRDPX_ImageElement.Transfer', '_HDRDPX_IndustryFilmInfoHeader.FramePosition', '_HDRDPX_IndustryFilmInfoHeader.FrameRate', '_HDRDPX_IndustryFilmInfoHeader.SequenceLen', '_HDRDPX_IndustryTelevisionInfoHeader.FieldNumber', '_HDRDPX_IndustryTelevisionInfoHeader.FrameRate', '_HDRDPX_IndustryTelevisionInfoHeader.Interlace', '_HdrDpxFileFormat.FileHeader', '_HdrDpxFileFormat.FilmHeader', '_HdrDpxFileFormat.ImageHeader', '_HdrDpxFileFormat.SourceInfoHeader', '_HdrDpxFileFormat.TvHeader']
  - AST pointer modes: ['UNKNOWN', 'UNKNOWN']
  - AST observed global reads: __stderrp, __stderrp, __stderrp, undefined_4bytes, undefined_4bytes
  - AST observed field reads: _HDRDPX_GenericFileHeader.Copyright, _HDRDPX_GenericFileHeader.Creator, _HDRDPX_GenericFileHeader.DatumMappingDirection, _HDRDPX_GenericFileHeader.FileName, _HDRDPX_GenericFileHeader.Project, _HDRDPX_GenericFileHeader.TimeDate, _HDRDPX_GenericFileHeader.UserSize, _HDRDPX_GenericFileHeader.Version, _HDRDPX_GenericImageHeader.ChromaSubsampling, _HDRDPX_GenericImageHeader.ImageElement, _HDRDPX_GenericImageHeader.ImageElement, _HDRDPX_GenericImageHeader.ImageElement, _HDRDPX_GenericImageHeader.ImageElement, _HDRDPX_GenericImageHeader.ImageElement, _HDRDPX_GenericImageHeader.ImageElement, _HDRDPX_GenericImageHeader.ImageElement, _HDRDPX_GenericImageHeader.ImageElement, _HDRDPX_GenericImageHeader.ImageElement, _HDRDPX_GenericImageHeader.ImageElement, _HDRDPX_GenericImageHeader.ImageElement, _HDRDPX_GenericImageHeader.ImageElement, _HDRDPX_GenericImageHeader.ImageElement, _HDRDPX_GenericImageHeader.ImageElement, _HDRDPX_GenericImageHeader.ImageElement, _HDRDPX_GenericImageHeader.ImageElement, _HDRDPX_GenericImageHeader.ImageElement, _HDRDPX_GenericImageHeader.ImageElement, _HDRDPX_GenericImageHeader.ImageElement, _HDRDPX_GenericImageHeader.ImageElement, _HDRDPX_GenericImageHeader.LinesPerElement, _HDRDPX_GenericImageHeader.NumberElements, _HDRDPX_GenericImageHeader.NumberElements, _HDRDPX_GenericImageHeader.NumberElements, _HDRDPX_GenericImageHeader.Orientation, _HDRDPX_GenericImageHeader.PixelsPerLine, _HDRDPX_GenericSourceInfoHeader.AspectRatio, _HDRDPX_GenericSourceInfoHeader.AspectRatio, _HDRDPX_GenericSourceInfoHeader.InputName, _HDRDPX_GenericSourceInfoHeader.InputSN, _HDRDPX_GenericSourceInfoHeader.SourceFileName, _HDRDPX_GenericSourceInfoHeader.SourceTimeDate, _HDRDPX_HiLoCode.d, _HDRDPX_HiLoCode.d, _HDRDPX_ImageElement.BitSize, _HDRDPX_ImageElement.BitSize, _HDRDPX_ImageElement.BitSize, _HDRDPX_ImageElement.BitSize, _HDRDPX_ImageElement.BitSize, _HDRDPX_ImageElement.BitSize, _HDRDPX_ImageElement.BitSize, _HDRDPX_ImageElement.BitSize, _HDRDPX_ImageElement.Colorimetric, _HDRDPX_ImageElement.DataSign, _HDRDPX_ImageElement.Description, _HDRDPX_ImageElement.Descriptor, _HDRDPX_ImageElement.Descriptor, _HDRDPX_ImageElement.Encoding, _HDRDPX_ImageElement.EndOfImagePadding, _HDRDPX_ImageElement.EndOfLinePadding, _HDRDPX_ImageElement.HighData, _HDRDPX_ImageElement.LowData, _HDRDPX_ImageElement.Packing, _HDRDPX_ImageElement.Transfer, _HDRDPX_IndustryFilmInfoHeader.Count, _HDRDPX_IndustryFilmInfoHeader.FilmMfgId, _HDRDPX_IndustryFilmInfoHeader.FilmType, _HDRDPX_IndustryFilmInfoHeader.Format, _HDRDPX_IndustryFilmInfoHeader.FrameId, _HDRDPX_IndustryFilmInfoHeader.FramePosition, _HDRDPX_IndustryFilmInfoHeader.FrameRate, _HDRDPX_IndustryFilmInfoHeader.OffsetPerfs, _HDRDPX_IndustryFilmInfoHeader.Prefix, _HDRDPX_IndustryFilmInfoHeader.SequenceLen, _HDRDPX_IndustryFilmInfoHeader.SlateInfo, _HDRDPX_IndustryTelevisionInfoHeader.FieldNumber, _HDRDPX_IndustryTelevisionInfoHeader.FrameRate, _HDRDPX_IndustryTelevisionInfoHeader.Interlace, _HdrDpxFileFormat.FileHeader, _HdrDpxFileFormat.FileHeader, _HdrDpxFileFormat.FileHeader, _HdrDpxFileFormat.FileHeader, _HdrDpxFileFormat.FileHeader, _HdrDpxFileFormat.FileHeader, _HdrDpxFileFormat.FileHeader, _HdrDpxFileFormat.FileHeader, _HdrDpxFileFormat.FilmHeader, _HdrDpxFileFormat.FilmHeader, _HdrDpxFileFormat.FilmHeader, _HdrDpxFileFormat.FilmHeader, _HdrDpxFileFormat.FilmHeader, _HdrDpxFileFormat.FilmHeader, _HdrDpxFileFormat.FilmHeader, _HdrDpxFileFormat.FilmHeader, _HdrDpxFileFormat.FilmHeader, _HdrDpxFileFormat.FilmHeader, _HdrDpxFileFormat.FilmHeader, _HdrDpxFileFormat.ImageHeader, _HdrDpxFileFormat.ImageHeader, _HdrDpxFileFormat.ImageHeader, _HdrDpxFileFormat.ImageHeader, _HdrDpxFileFormat.ImageHeader, _HdrDpxFileFormat.ImageHeader, _HdrDpxFileFormat.ImageHeader, _HdrDpxFileFormat.ImageHeader, _HdrDpxFileFormat.ImageHeader, _HdrDpxFileFormat.ImageHeader, _HdrDpxFileFormat.ImageHeader, _HdrDpxFileFormat.ImageHeader, _HdrDpxFileFormat.ImageHeader, _HdrDpxFileFormat.ImageHeader, _HdrDpxFileFormat.ImageHeader, _HdrDpxFileFormat.ImageHeader, _HdrDpxFileFormat.ImageHeader, _HdrDpxFileFormat.ImageHeader, _HdrDpxFileFormat.ImageHeader, _HdrDpxFileFormat.ImageHeader, _HdrDpxFileFormat.ImageHeader, _HdrDpxFileFormat.ImageHeader, _HdrDpxFileFormat.ImageHeader, _HdrDpxFileFormat.ImageHeader, _HdrDpxFileFormat.ImageHeader, _HdrDpxFileFormat.ImageHeader, _HdrDpxFileFormat.ImageHeader, _HdrDpxFileFormat.SourceInfoHeader, _HdrDpxFileFormat.SourceInfoHeader, _HdrDpxFileFormat.SourceInfoHeader, _HdrDpxFileFormat.SourceInfoHeader, _HdrDpxFileFormat.SourceInfoHeader, _HdrDpxFileFormat.SourceInfoHeader, _HdrDpxFileFormat.TvHeader, _HdrDpxFileFormat.TvHeader, _HdrDpxFileFormat.TvHeader, pic_s.alpha, pic_s.alpha, pic_s.alpha, pic_s.alpha, pic_s.ar1, pic_s.ar1, pic_s.ar2, pic_s.bits, pic_s.bits, pic_s.bits, pic_s.bits, pic_s.chroma, pic_s.chroma, pic_s.chroma, pic_s.chroma, pic_s.chroma_siting, pic_s.color, pic_s.color, pic_s.color, pic_s.color, pic_s.color, pic_s.color, pic_s.colorimetry, pic_s.colorimetry, pic_s.colorimetry, pic_s.colorimetry, pic_s.colorimetry, pic_s.colorimetry, pic_s.colorimetry, pic_s.colorimetry, pic_s.colorimetry, pic_s.colorimetry, pic_s.colorimetry, pic_s.colorimetry, pic_s.colorimetry, pic_s.format, pic_s.framerate, pic_s.framerate, pic_s.framerate, pic_s.framerate, pic_s.frm_no, pic_s.h, pic_s.interlaced, pic_s.limited_range, pic_s.seq_len, pic_s.transfer, pic_s.transfer, pic_s.transfer, pic_s.transfer, pic_s.transfer, pic_s.transfer, pic_s.transfer, pic_s.transfer, pic_s.transfer, pic_s.transfer, pic_s.transfer, pic_s.transfer, pic_s.transfer, pic_s.transfer, pic_s.transfer, pic_s.transfer, pic_s.transfer, pic_s.transfer, pic_s.transfer, pic_s.w
  - AST loop count is 1; trip proofs are retained per loop

## `hdr_dpx_get_datum`

- Source: `hdr_dpx.c:1153`
- Clang USR: `c:@F@hdr_dpx_get_datum`
- Return: `datum_t`; parameters: `fifo: fifo_t *`, `bits: int`, `dir: int`
- Callers: hdr_dpx_get_pic_data
- Callees: fifo_flip_get_bits, fifo_get_bits
- Global read/write: 0/0; field read/write: 0/4
- Pointer modes: fifo=UNKNOWN
- Loops: 0; fixed counts: UNKNOWN
- Effects: `{"assert": false, "file_io": false, "indirect_call": false, "logging": false, "malloc": false}`
- Proposal: **STATEFUL**; purity=False; combinational=False
- Classification evidence:
  - AST observed writes or mutable-state effects: ['_datum.d']
  - AST pointer modes: ['UNKNOWN']
  - AST observed no loop

## `hdr_dpx_get_pic_data`

- Source: `hdr_dpx.c:1172`
- Clang USR: `c:@F@hdr_dpx_get_pic_data`
- Return: `int`; parameters: `f: HDRDPXFILEFORMAT *`, `fp: FILE *`, `p: pic_t **`, `bswap: int`
- Callers: hdr_dpx_read
- Callees: fifo_clear, fifo_flip_get_bits, fifo_get_bits, fifo_init, fifo_put_bits, fprintf, fread, fseek, hdr_dpx_create_pic, hdr_dpx_get_datum, hdr_dpx_map_datum_to_pic, printf
- Global read/write: 9/0; field read/write: 126/0
- Pointer modes: f=UNKNOWN, fp=UNKNOWN, p=UNKNOWN
- Loops: 11; fixed counts: 8, 8, 8
- Effects: `{"assert": false, "file_io": true, "indirect_call": false, "logging": true, "malloc": false}`
- Proposal: **IO_OR_DEBUG**; purity=False; combinational=False
- Classification evidence:
  - AST observed no global/field/pointee writes
  - AST pointer modes: ['UNKNOWN', 'UNKNOWN', 'UNKNOWN']
  - AST observed global reads: __stderrp, __stderrp, __stderrp, __stderrp, __stderrp, __stderrp, __stderrp, __stderrp, __stderrp
  - AST observed field reads: _HDRDPX_GenericFileHeader.DatumMappingDirection, _HDRDPX_GenericFileHeader.DatumMappingDirection, _HDRDPX_GenericFileHeader.DatumMappingDirection, _HDRDPX_GenericFileHeader.DatumMappingDirection, _HDRDPX_GenericFileHeader.DatumMappingDirection, _HDRDPX_GenericFileHeader.DatumMappingDirection, _HDRDPX_GenericFileHeader.DatumMappingDirection, _HDRDPX_GenericFileHeader.DatumMappingDirection, _HDRDPX_GenericFileHeader.DatumMappingDirection, _HDRDPX_GenericImageHeader.ImageElement, _HDRDPX_GenericImageHeader.ImageElement, _HDRDPX_GenericImageHeader.ImageElement, _HDRDPX_GenericImageHeader.ImageElement, _HDRDPX_GenericImageHeader.ImageElement, _HDRDPX_GenericImageHeader.ImageElement, _HDRDPX_GenericImageHeader.ImageElement, _HDRDPX_GenericImageHeader.ImageElement, _HDRDPX_GenericImageHeader.ImageElement, _HDRDPX_GenericImageHeader.ImageElement, _HDRDPX_GenericImageHeader.ImageElement, _HDRDPX_GenericImageHeader.ImageElement, _HDRDPX_GenericImageHeader.ImageElement, _HDRDPX_GenericImageHeader.ImageElement, _HDRDPX_GenericImageHeader.ImageElement, _HDRDPX_GenericImageHeader.ImageElement, _HDRDPX_GenericImageHeader.ImageElement, _HDRDPX_GenericImageHeader.ImageElement, _HDRDPX_GenericImageHeader.ImageElement, _HDRDPX_GenericImageHeader.NumberElements, _HDRDPX_ImageElement.BitSize, _HDRDPX_ImageElement.BitSize, _HDRDPX_ImageElement.BitSize, _HDRDPX_ImageElement.BitSize, _HDRDPX_ImageElement.BitSize, _HDRDPX_ImageElement.BitSize, _HDRDPX_ImageElement.BitSize, _HDRDPX_ImageElement.BitSize, _HDRDPX_ImageElement.BitSize, _HDRDPX_ImageElement.BitSize, _HDRDPX_ImageElement.BitSize, _HDRDPX_ImageElement.BitSize, _HDRDPX_ImageElement.BitSize, _HDRDPX_ImageElement.DataOffset, _HDRDPX_ImageElement.Encoding, _HDRDPX_ImageElement.Encoding, _HDRDPX_ImageElement.EndOfLinePadding, _HDRDPX_ImageElement.Packing, _HDRDPX_ImageElement.Packing, _HdrDpxFileFormat.FileHeader, _HdrDpxFileFormat.FileHeader, _HdrDpxFileFormat.FileHeader, _HdrDpxFileFormat.FileHeader, _HdrDpxFileFormat.FileHeader, _HdrDpxFileFormat.FileHeader, _HdrDpxFileFormat.FileHeader, _HdrDpxFileFormat.FileHeader, _HdrDpxFileFormat.FileHeader, _HdrDpxFileFormat.ImageHeader, _HdrDpxFileFormat.ImageHeader, _HdrDpxFileFormat.ImageHeader, _HdrDpxFileFormat.ImageHeader, _HdrDpxFileFormat.ImageHeader, _HdrDpxFileFormat.ImageHeader, _HdrDpxFileFormat.ImageHeader, _HdrDpxFileFormat.ImageHeader, _HdrDpxFileFormat.ImageHeader, _HdrDpxFileFormat.ImageHeader, _HdrDpxFileFormat.ImageHeader, _HdrDpxFileFormat.ImageHeader, _HdrDpxFileFormat.ImageHeader, _HdrDpxFileFormat.ImageHeader, _HdrDpxFileFormat.ImageHeader, _HdrDpxFileFormat.ImageHeader, _HdrDpxFileFormat.ImageHeader, _HdrDpxFileFormat.ImageHeader, _HdrDpxFileFormat.ImageHeader, _HdrDpxFileFormat.ImageHeader, _datum.d, _datum.d, _datum.d, _datum.d, _datum.d, _datum.d, _datum.d, _datum.d, _datum.d, _datum.d, _datum.d, datum_ptrs_s.alt_chroma, datum_ptrs_s.alt_chroma, datum_ptrs_s.alt_chroma, datum_ptrs_s.alt_chroma, datum_ptrs_s.datum, datum_ptrs_s.datum, datum_ptrs_s.hbuff, datum_ptrs_s.ndatum, datum_ptrs_s.ndatum, datum_ptrs_s.ndatum, datum_ptrs_s.ndatum, datum_ptrs_s.offset, datum_ptrs_s.stride, datum_ptrs_s.stride, datum_ptrs_s.stride, datum_ptrs_s.stride, datum_ptrs_s.stride, datum_ptrs_s.stride, datum_ptrs_s.stride, datum_ptrs_s.wbuff, datum_ptrs_s.wbuff, datum_ptrs_s.wbuff, datum_ptrs_s.wbuff, datum_ptrs_s.wbuff, fifo_s.fullness, fifo_s.fullness, fifo_s.fullness, fifo_s.fullness, fifo_s.fullness, fifo_s.fullness, fifo_s.fullness, fifo_s.fullness, fifo_s.fullness, fifo_s.fullness, fifo_s.fullness, fifo_s.fullness, fifo_s.fullness, fifo_s.fullness
  - AST loop count is 11; trip proofs are retained per loop

## `hdr_dpx_map_datum_to_pic`

- Source: `hdr_dpx.c:621`
- Clang USR: `c:@F@hdr_dpx_map_datum_to_pic`
- Return: `int`; parameters: `f: HDRDPXFILEFORMAT *`, `p: pic_t *`, `dptr: datum_ptrs_t *`
- Callers: hdr_dpx_get_pic_data, hdr_dpx_pic_to_datum_list
- Callees: fprintf
- Global read/write: 4/0; field read/write: 704/238
- Pointer modes: f=UNKNOWN, p=READ_ONLY, dptr=WRITES_THROUGH
- Loops: 3; fixed counts: 8
- Effects: `{"assert": false, "file_io": true, "indirect_call": false, "logging": false, "malloc": false}`
- Proposal: **IO_OR_DEBUG**; purity=False; combinational=False
- Classification evidence:
  - AST observed writes or mutable-state effects: ['datum_ptrs_s.alt_chroma', 'datum_ptrs_s.datum', 'datum_ptrs_s.hbuff', 'datum_ptrs_s.ndatum', 'datum_ptrs_s.offset', 'datum_ptrs_s.stride', 'datum_ptrs_s.wbuff', 'dptr']
  - AST pointer modes: ['READ_ONLY', 'UNKNOWN', 'WRITES_THROUGH']
  - AST observed global reads: __stderrp, __stderrp, __stderrp, __stderrp
  - AST observed field reads: _HDRDPX_GenericImageHeader.ImageElement, _HDRDPX_GenericImageHeader.ImageElement, _HDRDPX_GenericImageHeader.ImageElement, _HDRDPX_GenericImageHeader.ImageElement, _HDRDPX_GenericImageHeader.ImageElement, _HDRDPX_GenericImageHeader.ImageElement, _HDRDPX_GenericImageHeader.ImageElement, _HDRDPX_GenericImageHeader.ImageElement, _HDRDPX_GenericImageHeader.ImageElement, _HDRDPX_GenericImageHeader.ImageElement, _HDRDPX_GenericImageHeader.ImageElement, _HDRDPX_GenericImageHeader.ImageElement, _HDRDPX_GenericImageHeader.ImageElement, _HDRDPX_GenericImageHeader.ImageElement, _HDRDPX_GenericImageHeader.ImageElement, _HDRDPX_GenericImageHeader.ImageElement, _HDRDPX_GenericImageHeader.ImageElement, _HDRDPX_GenericImageHeader.ImageElement, _HDRDPX_GenericImageHeader.ImageElement, _HDRDPX_GenericImageHeader.ImageElement, _HDRDPX_GenericImageHeader.ImageElement, _HDRDPX_GenericImageHeader.ImageElement, _HDRDPX_GenericImageHeader.ImageElement, _HDRDPX_GenericImageHeader.ImageElement, _HDRDPX_GenericImageHeader.ImageElement, _HDRDPX_GenericImageHeader.ImageElement, _HDRDPX_GenericImageHeader.ImageElement, _HDRDPX_GenericImageHeader.ImageElement, _HDRDPX_GenericImageHeader.ImageElement, _HDRDPX_GenericImageHeader.ImageElement, _HDRDPX_GenericImageHeader.ImageElement, _HDRDPX_GenericImageHeader.ImageElement, _HDRDPX_GenericImageHeader.ImageElement, _HDRDPX_GenericImageHeader.ImageElement, _HDRDPX_GenericImageHeader.ImageElement, _HDRDPX_GenericImageHeader.ImageElement, _HDRDPX_GenericImageHeader.ImageElement, _HDRDPX_GenericImageHeader.ImageElement, _HDRDPX_GenericImageHeader.ImageElement, _HDRDPX_GenericImageHeader.ImageElement, _HDRDPX_GenericImageHeader.ImageElement, _HDRDPX_GenericImageHeader.ImageElement, _HDRDPX_GenericImageHeader.ImageElement, _HDRDPX_GenericImageHeader.ImageElement, _HDRDPX_GenericImageHeader.ImageElement, _HDRDPX_GenericImageHeader.ImageElement, _HDRDPX_GenericImageHeader.ImageElement, _HDRDPX_GenericImageHeader.ImageElement, _HDRDPX_GenericImageHeader.ImageElement, _HDRDPX_GenericImageHeader.NumberElements, _HDRDPX_ImageElement.BitSize, _HDRDPX_ImageElement.BitSize, _HDRDPX_ImageElement.BitSize, _HDRDPX_ImageElement.BitSize, _HDRDPX_ImageElement.BitSize, _HDRDPX_ImageElement.BitSize, _HDRDPX_ImageElement.BitSize, _HDRDPX_ImageElement.BitSize, _HDRDPX_ImageElement.BitSize, _HDRDPX_ImageElement.BitSize, _HDRDPX_ImageElement.BitSize, _HDRDPX_ImageElement.BitSize, _HDRDPX_ImageElement.BitSize, _HDRDPX_ImageElement.BitSize, _HDRDPX_ImageElement.BitSize, _HDRDPX_ImageElement.BitSize, _HDRDPX_ImageElement.BitSize, _HDRDPX_ImageElement.BitSize, _HDRDPX_ImageElement.BitSize, _HDRDPX_ImageElement.BitSize, _HDRDPX_ImageElement.BitSize, _HDRDPX_ImageElement.BitSize, _HDRDPX_ImageElement.BitSize, _HDRDPX_ImageElement.BitSize, _HDRDPX_ImageElement.BitSize, _HDRDPX_ImageElement.BitSize, _HDRDPX_ImageElement.BitSize, _HDRDPX_ImageElement.BitSize, _HDRDPX_ImageElement.BitSize, _HDRDPX_ImageElement.BitSize, _HDRDPX_ImageElement.BitSize, _HDRDPX_ImageElement.BitSize, _HDRDPX_ImageElement.BitSize, _HDRDPX_ImageElement.BitSize, _HDRDPX_ImageElement.BitSize, _HDRDPX_ImageElement.BitSize, _HDRDPX_ImageElement.BitSize, _HDRDPX_ImageElement.BitSize, _HDRDPX_ImageElement.BitSize, _HDRDPX_ImageElement.BitSize, _HDRDPX_ImageElement.BitSize, _HDRDPX_ImageElement.BitSize, _HDRDPX_ImageElement.BitSize, _HDRDPX_ImageElement.BitSize, _HDRDPX_ImageElement.BitSize, _HDRDPX_ImageElement.BitSize, _HDRDPX_ImageElement.Descriptor, _HDRDPX_ImageElement.Descriptor, _HDRDPX_ImageElement.Descriptor, _HdrDpxFileFormat.ImageHeader, _HdrDpxFileFormat.ImageHeader, _HdrDpxFileFormat.ImageHeader, _HdrDpxFileFormat.ImageHeader, _HdrDpxFileFormat.ImageHeader, _HdrDpxFileFormat.ImageHeader, _HdrDpxFileFormat.ImageHeader, _HdrDpxFileFormat.ImageHeader, _HdrDpxFileFormat.ImageHeader, _HdrDpxFileFormat.ImageHeader, _HdrDpxFileFormat.ImageHeader, _HdrDpxFileFormat.ImageHeader, _HdrDpxFileFormat.ImageHeader, _HdrDpxFileFormat.ImageHeader, _HdrDpxFileFormat.ImageHeader, _HdrDpxFileFormat.ImageHeader, _HdrDpxFileFormat.ImageHeader, _HdrDpxFileFormat.ImageHeader, _HdrDpxFileFormat.ImageHeader, _HdrDpxFileFormat.ImageHeader, _HdrDpxFileFormat.ImageHeader, _HdrDpxFileFormat.ImageHeader, _HdrDpxFileFormat.ImageHeader, _HdrDpxFileFormat.ImageHeader, _HdrDpxFileFormat.ImageHeader, _HdrDpxFileFormat.ImageHeader, _HdrDpxFileFormat.ImageHeader, _HdrDpxFileFormat.ImageHeader, _HdrDpxFileFormat.ImageHeader, _HdrDpxFileFormat.ImageHeader, _HdrDpxFileFormat.ImageHeader, _HdrDpxFileFormat.ImageHeader, _HdrDpxFileFormat.ImageHeader, _HdrDpxFileFormat.ImageHeader, _HdrDpxFileFormat.ImageHeader, _HdrDpxFileFormat.ImageHeader, _HdrDpxFileFormat.ImageHeader, _HdrDpxFileFormat.ImageHeader, _HdrDpxFileFormat.ImageHeader, _HdrDpxFileFormat.ImageHeader, _HdrDpxFileFormat.ImageHeader, _HdrDpxFileFormat.ImageHeader, _HdrDpxFileFormat.ImageHeader, _HdrDpxFileFormat.ImageHeader, _HdrDpxFileFormat.ImageHeader, _HdrDpxFileFormat.ImageHeader, _HdrDpxFileFormat.ImageHeader, _HdrDpxFileFormat.ImageHeader, _HdrDpxFileFormat.ImageHeader, _HdrDpxFileFormat.ImageHeader, data_u.gc, data_u.gc, data_u.gc, data_u.gc_d, data_u.gc_d, data_u.gc_d, data_u.gc_s, data_u.gc_s, data_u.gc_s, data_u.rgb, data_u.rgb, data_u.rgb, data_u.rgb, data_u.rgb, data_u.rgb, data_u.rgb, data_u.rgb, data_u.rgb, data_u.rgb, data_u.rgb, data_u.rgb, data_u.rgb, data_u.rgb, data_u.rgb, data_u.rgb, data_u.rgb, data_u.rgb, data_u.rgb, data_u.rgb, data_u.rgb, data_u.rgb, data_u.rgb, data_u.rgb, data_u.rgb, data_u.rgb, data_u.rgb_d, data_u.rgb_d, data_u.rgb_d, data_u.rgb_d, data_u.rgb_d, data_u.rgb_d, data_u.rgb_d, data_u.rgb_d, data_u.rgb_d, data_u.rgb_d, data_u.rgb_d, data_u.rgb_d, data_u.rgb_d, data_u.rgb_d, data_u.rgb_d, data_u.rgb_d, data_u.rgb_d, data_u.rgb_d, data_u.rgb_d, data_u.rgb_d, data_u.rgb_d, data_u.rgb_d, data_u.rgb_d, data_u.rgb_d, data_u.rgb_d, data_u.rgb_d, data_u.rgb_s, data_u.rgb_s, data_u.rgb_s, data_u.rgb_s, data_u.rgb_s, data_u.rgb_s, data_u.rgb_s, data_u.rgb_s, data_u.rgb_s, data_u.rgb_s, data_u.rgb_s, data_u.rgb_s, data_u.rgb_s, data_u.rgb_s, data_u.rgb_s, data_u.rgb_s, data_u.rgb_s, data_u.rgb_s, data_u.rgb_s, data_u.rgb_s, data_u.rgb_s, data_u.rgb_s, data_u.rgb_s, data_u.rgb_s, data_u.rgb_s, data_u.rgb_s, data_u.yuv, data_u.yuv, data_u.yuv, data_u.yuv, data_u.yuv, data_u.yuv, data_u.yuv, data_u.yuv, data_u.yuv, data_u.yuv, data_u.yuv, data_u.yuv, data_u.yuv, data_u.yuv, data_u.yuv, data_u.yuv, data_u.yuv, data_u.yuv, data_u.yuv, data_u.yuv, data_u.yuv, data_u.yuv, data_u.yuv, data_u.yuv, data_u.yuv, data_u.yuv, data_u.yuv, data_u.yuv, data_u.yuv, data_u.yuv, data_u.yuv, data_u.yuv, data_u.yuv, data_u.yuv_d, data_u.yuv_d, data_u.yuv_d, data_u.yuv_d, data_u.yuv_d, data_u.yuv_d, data_u.yuv_d, data_u.yuv_d, data_u.yuv_d, data_u.yuv_d, data_u.yuv_d, data_u.yuv_d, data_u.yuv_d, data_u.yuv_d, data_u.yuv_d, data_u.yuv_d, data_u.yuv_d, data_u.yuv_d, data_u.yuv_d, data_u.yuv_d, data_u.yuv_d, data_u.yuv_d, data_u.yuv_d, data_u.yuv_d, data_u.yuv_d, data_u.yuv_d, data_u.yuv_d, data_u.yuv_d, data_u.yuv_d, data_u.yuv_d, data_u.yuv_d, data_u.yuv_d, data_u.yuv_d, data_u.yuv_s, data_u.yuv_s, data_u.yuv_s, data_u.yuv_s, data_u.yuv_s, data_u.yuv_s, data_u.yuv_s, data_u.yuv_s, data_u.yuv_s, data_u.yuv_s, data_u.yuv_s, data_u.yuv_s, data_u.yuv_s, data_u.yuv_s, data_u.yuv_s, data_u.yuv_s, data_u.yuv_s, data_u.yuv_s, data_u.yuv_s, data_u.yuv_s, data_u.yuv_s, data_u.yuv_s, data_u.yuv_s, data_u.yuv_s, data_u.yuv_s, data_u.yuv_s, data_u.yuv_s, data_u.yuv_s, data_u.yuv_s, data_u.yuv_s, data_u.yuv_s, data_u.yuv_s, data_u.yuv_s, datum_ptrs_s.ndatum, pic_s.color, pic_s.color, pic_s.color, pic_s.data, pic_s.data, pic_s.data, pic_s.data, pic_s.data, pic_s.data, pic_s.data, pic_s.data, pic_s.data, pic_s.data, pic_s.data, pic_s.data, pic_s.data, pic_s.data, pic_s.data, pic_s.data, pic_s.data, pic_s.data, pic_s.data, pic_s.data, pic_s.data, pic_s.data, pic_s.data, pic_s.data, pic_s.data, pic_s.data, pic_s.data, pic_s.data, pic_s.data, pic_s.data, pic_s.data, pic_s.data, pic_s.data, pic_s.data, pic_s.data, pic_s.data, pic_s.data, pic_s.data, pic_s.data, pic_s.data, pic_s.data, pic_s.data, pic_s.data, pic_s.data, pic_s.data, pic_s.data, pic_s.data, pic_s.data, pic_s.data, pic_s.data, pic_s.data, pic_s.data, pic_s.data, pic_s.data, pic_s.data, pic_s.data, pic_s.data, pic_s.data, pic_s.data, pic_s.data, pic_s.data, pic_s.data, pic_s.data, pic_s.data, pic_s.data, pic_s.data, pic_s.data, pic_s.data, pic_s.data, pic_s.data, pic_s.data, pic_s.data, pic_s.data, pic_s.data, pic_s.data, pic_s.data, pic_s.data, pic_s.data, pic_s.data, pic_s.data, pic_s.data, pic_s.data, pic_s.data, pic_s.data, pic_s.data, pic_s.data, pic_s.data, pic_s.data, pic_s.data, pic_s.data, pic_s.data, pic_s.data, pic_s.data, pic_s.data, pic_s.data, pic_s.data, pic_s.data, pic_s.data, pic_s.data, pic_s.data, pic_s.data, pic_s.data, pic_s.data, pic_s.data, pic_s.data, pic_s.data, pic_s.data, pic_s.data, pic_s.data, pic_s.data, pic_s.data, pic_s.data, pic_s.data, pic_s.data, pic_s.data, pic_s.data, pic_s.data, pic_s.data, pic_s.data, pic_s.data, pic_s.data, pic_s.data, pic_s.data, pic_s.data, pic_s.data, pic_s.data, pic_s.data, pic_s.data, pic_s.data, pic_s.data, pic_s.data, pic_s.data, pic_s.data, pic_s.data, pic_s.data, pic_s.data, pic_s.data, pic_s.data, pic_s.data, pic_s.data, pic_s.data, pic_s.data, pic_s.data, pic_s.data, pic_s.data, pic_s.data, pic_s.data, pic_s.data, pic_s.data, pic_s.data, pic_s.data, pic_s.data, pic_s.data, pic_s.data, pic_s.data, pic_s.data, pic_s.data, pic_s.data, pic_s.data, pic_s.data, pic_s.data, pic_s.data, pic_s.data, pic_s.data, pic_s.data, pic_s.data, pic_s.data, pic_s.data, pic_s.data, pic_s.data, pic_s.data, pic_s.data, pic_s.data, pic_s.data, pic_s.data, pic_s.data, pic_s.data, pic_s.data, pic_s.data, pic_s.data, pic_s.data, pic_s.data, pic_s.data, pic_s.data, pic_s.data, pic_s.data, pic_s.h, pic_s.w, rgb_d_s.a, rgb_d_s.a, rgb_d_s.a, rgb_d_s.a, rgb_d_s.a, rgb_d_s.b, rgb_d_s.b, rgb_d_s.b, rgb_d_s.b, rgb_d_s.b, rgb_d_s.b, rgb_d_s.b, rgb_d_s.g, rgb_d_s.g, rgb_d_s.g, rgb_d_s.g, rgb_d_s.g, rgb_d_s.g, rgb_d_s.g, rgb_d_s.r, rgb_d_s.r, rgb_d_s.r, rgb_d_s.r, rgb_d_s.r, rgb_d_s.r, rgb_d_s.r, rgb_s.a, rgb_s.a, rgb_s.a, rgb_s.a, rgb_s.a, rgb_s.b, rgb_s.b, rgb_s.b, rgb_s.b, rgb_s.b, rgb_s.b, rgb_s.b, rgb_s.g, rgb_s.g, rgb_s.g, rgb_s.g, rgb_s.g, rgb_s.g, rgb_s.g, rgb_s.r, rgb_s.r, rgb_s.r, rgb_s.r, rgb_s.r, rgb_s.r, rgb_s.r, rgb_s_s.a, rgb_s_s.a, rgb_s_s.a, rgb_s_s.a, rgb_s_s.a, rgb_s_s.b, rgb_s_s.b, rgb_s_s.b, rgb_s_s.b, rgb_s_s.b, rgb_s_s.b, rgb_s_s.b, rgb_s_s.g, rgb_s_s.g, rgb_s_s.g, rgb_s_s.g, rgb_s_s.g, rgb_s_s.g, rgb_s_s.g, rgb_s_s.r, rgb_s_s.r, rgb_s_s.r, rgb_s_s.r, rgb_s_s.r, rgb_s_s.r, rgb_s_s.r, yuv_d_s.a, yuv_d_s.a, yuv_d_s.a, yuv_d_s.a, yuv_d_s.a, yuv_d_s.a, yuv_d_s.u, yuv_d_s.u, yuv_d_s.u, yuv_d_s.u, yuv_d_s.u, yuv_d_s.u, yuv_d_s.u, yuv_d_s.u, yuv_d_s.v, yuv_d_s.v, yuv_d_s.v, yuv_d_s.v, yuv_d_s.v, yuv_d_s.v, yuv_d_s.v, yuv_d_s.v, yuv_d_s.y, yuv_d_s.y, yuv_d_s.y, yuv_d_s.y, yuv_d_s.y, yuv_d_s.y, yuv_d_s.y, yuv_d_s.y, yuv_d_s.y, yuv_d_s.y, yuv_d_s.y, yuv_s.a, yuv_s.a, yuv_s.a, yuv_s.a, yuv_s.a, yuv_s.a, yuv_s.u, yuv_s.u, yuv_s.u, yuv_s.u, yuv_s.u, yuv_s.u, yuv_s.u, yuv_s.u, yuv_s.v, yuv_s.v, yuv_s.v, yuv_s.v, yuv_s.v, yuv_s.v, yuv_s.v, yuv_s.v, yuv_s.y, yuv_s.y, yuv_s.y, yuv_s.y, yuv_s.y, yuv_s.y, yuv_s.y, yuv_s.y, yuv_s.y, yuv_s.y, yuv_s.y, yuv_s_s.a, yuv_s_s.a, yuv_s_s.a, yuv_s_s.a, yuv_s_s.a, yuv_s_s.a, yuv_s_s.u, yuv_s_s.u, yuv_s_s.u, yuv_s_s.u, yuv_s_s.u, yuv_s_s.u, yuv_s_s.u, yuv_s_s.u, yuv_s_s.v, yuv_s_s.v, yuv_s_s.v, yuv_s_s.v, yuv_s_s.v, yuv_s_s.v, yuv_s_s.v, yuv_s_s.v, yuv_s_s.y, yuv_s_s.y, yuv_s_s.y, yuv_s_s.y, yuv_s_s.y, yuv_s_s.y, yuv_s_s.y, yuv_s_s.y, yuv_s_s.y, yuv_s_s.y, yuv_s_s.y
  - AST loop count is 3; trip proofs are retained per loop

## `hdr_dpx_pic_to_datum_list`

- Source: `hdr_dpx.c:1077`
- Clang USR: `c:@F@hdr_dpx_pic_to_datum_list`
- Return: `int`; parameters: `f: HDRDPXFILEFORMAT *`, `dlist: datum_list_t *`, `p: pic_t *`
- Callers: hdr_dpx_write
- Callees: fprintf, hdr_dpx_map_datum_to_pic, hdr_dpx_rle_encode, malloc
- Global read/write: 1/0; field read/write: 29/12
- Pointer modes: f=WRITES_THROUGH, dlist=UNKNOWN, p=UNKNOWN
- Loops: 7; fixed counts: 8, 8, 8
- Effects: `{"assert": false, "file_io": true, "indirect_call": false, "logging": false, "malloc": true}`
- Proposal: **IO_OR_DEBUG**; purity=False; combinational=False
- Classification evidence:
  - AST observed writes or mutable-state effects: ['_HDRDPX_GenericImageHeader.ImageElement', '_HDRDPX_ImageElement.Encoding', '_HdrDpxFileFormat.ImageHeader', '_datum_list_s.bit_depth', '_datum_list_s.d', '_datum_list_s.eol_flag', '_datum_list_s.ndatum', 'f']
  - AST pointer modes: ['UNKNOWN', 'UNKNOWN', 'WRITES_THROUGH']
  - AST observed global reads: __stderrp
  - AST observed field reads: _HDRDPX_GenericImageHeader.ImageElement, _HDRDPX_GenericImageHeader.ImageElement, _HDRDPX_GenericImageHeader.ImageElement, _HDRDPX_GenericImageHeader.ImageElement, _HDRDPX_GenericImageHeader.NumberElements, _HDRDPX_ImageElement.BitSize, _HDRDPX_ImageElement.BitSize, _HDRDPX_ImageElement.BitSize, _HDRDPX_ImageElement.Encoding, _HdrDpxFileFormat.ImageHeader, _HdrDpxFileFormat.ImageHeader, _HdrDpxFileFormat.ImageHeader, _HdrDpxFileFormat.ImageHeader, _HdrDpxFileFormat.ImageHeader, datum_ptrs_s.alt_chroma, datum_ptrs_s.alt_chroma, datum_ptrs_s.datum, datum_ptrs_s.hbuff, datum_ptrs_s.hbuff, datum_ptrs_s.hbuff, datum_ptrs_s.ndatum, datum_ptrs_s.ndatum, datum_ptrs_s.ndatum, datum_ptrs_s.ndatum, datum_ptrs_s.offset, datum_ptrs_s.stride, datum_ptrs_s.wbuff, datum_ptrs_s.wbuff, datum_ptrs_s.wbuff
  - AST loop count is 7; trip proofs are retained per loop

## `hdr_dpx_read`

- Source: `hdr_dpx.c:1966`
- Clang USR: `c:@F@hdr_dpx_read`
- Return: `int`; parameters: `fname: char *`, `p: pic_t **`, `dpxh: HDRDPXFILEFORMAT *`, `dpxu: HDRDPXUSERDATA *`, `dpxsbm: HDRDPXSBMDATA *`
- Callers: main
- Callees: __builtin___memcpy_chk, __builtin___memset_chk, __builtin_object_size, fclose, fgetc, fopen, fprintf, fread, fseek, hdr_dpx_byte_swap, hdr_dpx_get_pic_data, malloc, perror
- Global read/write: 3/0; field read/write: 15/7
- Pointer modes: fname=UNKNOWN, p=UNKNOWN, dpxh=UNKNOWN, dpxu=WRITES_THROUGH, dpxsbm=WRITES_THROUGH
- Loops: 4; fixed counts: 128, 32
- Effects: `{"assert": false, "file_io": true, "indirect_call": false, "logging": true, "malloc": true}`
- Proposal: **IO_OR_DEBUG**; purity=False; combinational=False
- Classification evidence:
  - AST observed writes or mutable-state effects: ['_HdrDpxSbmData.SbmData', '_HdrDpxSbmData.SbmFormatDescriptor', '_HdrDpxSbmData.SbmLength', '_HdrDpxUserData.UserData', '_HdrDpxUserData.UserIdentification', 'dpxsbm', 'dpxu']
  - AST pointer modes: ['UNKNOWN', 'UNKNOWN', 'UNKNOWN', 'WRITES_THROUGH', 'WRITES_THROUGH']
  - AST observed global reads: __stderrp, __stderrp, __stderrp
  - AST observed field reads: _HDRDPX_GenericFileHeader.StandardsBasedMetadataOffset, _HDRDPX_GenericFileHeader.StandardsBasedMetadataOffset, _HDRDPX_GenericFileHeader.UserSize, _HDRDPX_GenericFileHeader.UserSize, _HDRDPX_GenericFileHeader.UserSize, _HDRDPX_GenericFileHeader.UserSize, _HdrDpxFileFormat.FileHeader, _HdrDpxFileFormat.FileHeader, _HdrDpxFileFormat.FileHeader, _HdrDpxFileFormat.FileHeader, _HdrDpxFileFormat.FileHeader, _HdrDpxFileFormat.FileHeader, _HdrDpxSbmData.SbmLength, _HdrDpxSbmData.SbmLength, _HdrDpxSbmData.SbmLength
  - AST loop count is 4; trip proofs are retained per loop

## `hdr_dpx_rle_encode`

- Source: `hdr_dpx.c:80`
- Clang USR: `c:@F@hdr_dpx_rle_encode`
- Return: `void`; parameters: `dlist: datum_list_t *`, `d_per_pixel: int`
- Callers: hdr_dpx_pic_to_datum_list
- Callees: exit, fprintf, free, malloc, realloc
- Global read/write: 2/0; field read/write: 38/26
- Pointer modes: dlist=WRITES_THROUGH
- Loops: 12; fixed counts: UNKNOWN
- Effects: `{"assert": false, "file_io": true, "indirect_call": false, "logging": false, "malloc": true}`
- Proposal: **IO_OR_DEBUG**; purity=False; combinational=False
- Classification evidence:
  - AST observed writes or mutable-state effects: ['_datum_list_s.bit_depth', '_datum_list_s.d', '_datum_list_s.eol_flag', '_datum_list_s.ndatum', 'dlist', 'rle_ll_s.count', 'rle_ll_s.d', 'rle_ll_s.eol_flag', 'rle_ll_s.f', 'rle_ll_s.next']
  - AST pointer modes: ['WRITES_THROUGH']
  - AST observed global reads: __stderrp, __stderrp
  - AST observed field reads: _datum_list_s.bit_depth, _datum_list_s.bit_depth, _datum_list_s.d, _datum_list_s.d, _datum_list_s.d, _datum_list_s.d, _datum_list_s.d, _datum_list_s.d, _datum_list_s.eol_flag, _datum_list_s.eol_flag, _datum_list_s.eol_flag, _datum_list_s.eol_flag, _datum_list_s.eol_flag, _datum_list_s.eol_flag, _datum_list_s.eol_flag, _datum_list_s.ndatum, _datum_list_s.ndatum, _datum_list_s.ndatum, _datum_list_s.ndatum, _datum_list_s.ndatum, _datum_list_s.ndatum, rle_ll_s.count, rle_ll_s.count, rle_ll_s.count, rle_ll_s.count, rle_ll_s.d, rle_ll_s.d, rle_ll_s.d, rle_ll_s.d, rle_ll_s.d, rle_ll_s.d, rle_ll_s.eol_flag, rle_ll_s.eol_flag, rle_ll_s.f, rle_ll_s.f, rle_ll_s.next, rle_ll_s.next, rle_ll_s.next
  - AST loop count is 12; trip proofs are retained per loop

## `hdr_dpx_write`

- Source: `hdr_dpx.c:1746`
- Clang USR: `c:@F@hdr_dpx_write`
- Return: `int`; parameters: `fname: char *`, `p: pic_t *`, `dpxh: HDRDPXFILEFORMAT *`, `dpxu: HDRDPXUSERDATA *`, `dpxsbm: HDRDPXSBMDATA *`, `write_as_be: int`, `dpxh_written: HDRDPXFILEFORMAT *`
- Callers: main
- Callees: __builtin___memcpy_chk, __builtin___memset_chk, __builtin_object_size, exit, fclose, fifo_flip_put_bits, fifo_free, fifo_get_bits, fifo_init, fifo_put_bits, fopen, fprintf, fputc, free, fseek, ftell, fwrite, hdr_dpx_byte_swap, hdr_dpx_compute_offsets, hdr_dpx_fill_core_fields, hdr_dpx_pic_to_datum_list
- Global read/write: 2/0; field read/write: 95/8
- Pointer modes: fname=UNKNOWN, p=UNKNOWN, dpxh=UNKNOWN, dpxu=UNKNOWN, dpxsbm=UNKNOWN, dpxh_written=UNKNOWN
- Loops: 10; fixed counts: 128, 32
- Effects: `{"assert": false, "file_io": true, "indirect_call": false, "logging": false, "malloc": true}`
- Proposal: **IO_OR_DEBUG**; purity=False; combinational=False
- Classification evidence:
  - AST observed writes or mutable-state effects: ['ANONYMOUS.ui', '_HDRDPX_GenericFileHeader.FileSize', '_HDRDPX_GenericFileHeader.StandardsBasedMetadataOffset', '_HDRDPX_GenericImageHeader.ImageElement', '_HDRDPX_ImageElement.DataOffset', '_HdrDpxFileFormat.FileHeader', '_HdrDpxFileFormat.ImageHeader']
  - AST pointer modes: ['UNKNOWN', 'UNKNOWN', 'UNKNOWN', 'UNKNOWN', 'UNKNOWN', 'UNKNOWN']
  - AST observed global reads: __stderrp, __stderrp
  - AST observed field reads: ANONYMOUS.c, _HDRDPX_GenericFileHeader.DatumMappingDirection, _HDRDPX_GenericFileHeader.DatumMappingDirection, _HDRDPX_GenericFileHeader.DatumMappingDirection, _HDRDPX_GenericFileHeader.DatumMappingDirection, _HDRDPX_GenericFileHeader.ImageOffset, _HDRDPX_GenericFileHeader.StandardsBasedMetadataOffset, _HDRDPX_GenericFileHeader.StandardsBasedMetadataOffset, _HDRDPX_GenericFileHeader.UserSize, _HDRDPX_GenericFileHeader.UserSize, _HDRDPX_GenericImageHeader.ImageElement, _HDRDPX_GenericImageHeader.ImageElement, _HDRDPX_GenericImageHeader.ImageElement, _HDRDPX_GenericImageHeader.ImageElement, _HDRDPX_GenericImageHeader.ImageElement, _HDRDPX_GenericImageHeader.ImageElement, _HDRDPX_GenericImageHeader.ImageElement, _HDRDPX_GenericImageHeader.ImageElement, _HDRDPX_GenericImageHeader.ImageElement, _HDRDPX_GenericImageHeader.ImageElement, _HDRDPX_GenericImageHeader.ImageElement, _HDRDPX_GenericImageHeader.ImageElement, _HDRDPX_GenericImageHeader.ImageElement, _HDRDPX_GenericImageHeader.NumberElements, _HDRDPX_GenericImageHeader.NumberElements, _HDRDPX_ImageElement.BitSize, _HDRDPX_ImageElement.BitSize, _HDRDPX_ImageElement.BitSize, _HDRDPX_ImageElement.BitSize, _HDRDPX_ImageElement.BitSize, _HDRDPX_ImageElement.BitSize, _HDRDPX_ImageElement.BitSize, _HDRDPX_ImageElement.BitSize, _HDRDPX_ImageElement.DataOffset, _HDRDPX_ImageElement.EndOfImagePadding, _HDRDPX_ImageElement.EndOfLinePadding, _HDRDPX_ImageElement.Packing, _HDRDPX_ImageElement.Packing, _HdrDpxFileFormat.FileHeader, _HdrDpxFileFormat.FileHeader, _HdrDpxFileFormat.FileHeader, _HdrDpxFileFormat.FileHeader, _HdrDpxFileFormat.FileHeader, _HdrDpxFileFormat.FileHeader, _HdrDpxFileFormat.FileHeader, _HdrDpxFileFormat.FileHeader, _HdrDpxFileFormat.FileHeader, _HdrDpxFileFormat.ImageHeader, _HdrDpxFileFormat.ImageHeader, _HdrDpxFileFormat.ImageHeader, _HdrDpxFileFormat.ImageHeader, _HdrDpxFileFormat.ImageHeader, _HdrDpxFileFormat.ImageHeader, _HdrDpxFileFormat.ImageHeader, _HdrDpxFileFormat.ImageHeader, _HdrDpxFileFormat.ImageHeader, _HdrDpxFileFormat.ImageHeader, _HdrDpxFileFormat.ImageHeader, _HdrDpxFileFormat.ImageHeader, _HdrDpxFileFormat.ImageHeader, _HdrDpxFileFormat.ImageHeader, _HdrDpxFileFormat.ImageHeader, _HdrDpxSbmData.SbmData, _HdrDpxSbmData.SbmFormatDescriptor, _HdrDpxSbmData.SbmFormatDescriptor, _HdrDpxSbmData.SbmLength, _HdrDpxSbmData.SbmLength, _HdrDpxSbmData.SbmLength, _HdrDpxUserData.UserData, _HdrDpxUserData.UserIdentification, _HdrDpxUserData.UserIdentification, _datum_list_s.d, _datum_list_s.d, _datum_list_s.d, _datum_list_s.d, _datum_list_s.d, _datum_list_s.d, _datum_list_s.d, _datum_list_s.eol_flag, _datum_list_s.eol_flag, _datum_list_s.ndatum, fifo_s.fullness, fifo_s.fullness, fifo_s.fullness, fifo_s.fullness, fifo_s.fullness, fifo_s.fullness, fifo_s.fullness, fifo_s.fullness, fifo_s.fullness, fifo_s.fullness, fifo_s.fullness, fifo_s.fullness, fifo_s.fullness, fifo_s.fullness
  - AST loop count is 10; trip proofs are retained per loop

## `line_to_int`

- Source: `rc_tables.h:382`
- Clang USR: `c:@F@line_to_int`
- Return: `void`; parameters: `s: char *`, `l: int **`
- Callers: make_qp_table
- Callees: atoi, malloc
- Global read/write: 0/0; field read/write: 0/0
- Pointer modes: s=WRITES_THROUGH, l=WRITES_THROUGH
- Loops: 3; fixed counts: UNKNOWN
- Effects: `{"assert": false, "file_io": false, "indirect_call": false, "logging": false, "malloc": true}`
- Proposal: **IO_OR_DEBUG**; purity=False; combinational=False
- Classification evidence:
  - AST observed writes or mutable-state effects: ['l', 's']
  - AST pointer modes: ['WRITES_THROUGH', 'WRITES_THROUGH']
  - AST loop count is 3; trip proofs are retained per loop

## `lower_case`

- Source: `cmd_parse.c:367`
- Clang USR: `c:@F@lower_case`
- Return: `char *`; parameters: `str: char *`
- Callers: str2dim, str2fdim, str2pdim
- Callees: tolower
- Global read/write: 0/0; field read/write: 0/0
- Pointer modes: str=UNKNOWN
- Loops: 1; fixed counts: UNKNOWN
- Effects: `{"assert": false, "file_io": false, "indirect_call": false, "logging": false, "malloc": false}`
- Proposal: **COMPOSITE_COMB_CANDIDATE**; purity=False; combinational=True
- Classification evidence:
  - AST observed no global/field/pointee writes
  - AST pointer modes: ['UNKNOWN']
  - AST loop count is 1; trip proofs are retained per loop

## `main`

- Source: `codec_main.c:1276`
- Clang USR: `c:@F@main`
- Return: `int`; parameters: `argc: int`, `argv: char **`
- Callers: NONE
- Callees: DSC_Decode, DSC_Encode, UErr, __builtin___memset_chk, __builtin___sprintf_chk, __builtin___strcat_chk, __builtin___strcpy_chk, __builtin_object_size, ceil, compute_and_display_PSNR, convertbits, dpx_read, dpx_write, exit, fclose, feof, fflush, fgetc, fgets, fopen, fprintf, fputc, free, hdr_dpx_determine_file_type, hdr_dpx_read, hdr_dpx_write, malloc, parse_pps, pcopy_header, pcreate_ext, pdestroy, populate_pps, ppm_read, ppm_write, print_pps, print_pps_v2, printf, read_dsc_data, rgb2yuv, set_convertbits_rounding, set_defaults, simple422to444, simple444to422, split_base_and_ext, strcmp, strlen, write_dsc_data, write_pps, yuv2rgb, yuv_420_422, yuv_422_420, yuv_422_444, yuv_444_422, yuv_read, yuv_write, process_args
- Global read/write: 141/11; field read/write: 176/57
- Pointer modes: argv=UNKNOWN
- Loops: 15; fixed counts: 128, 128, 2
- Effects: `{"assert": false, "file_io": true, "indirect_call": false, "logging": true, "malloc": true}`
- Proposal: **IO_OR_DEBUG**; purity=False; combinational=False
- Classification evidence:
  - AST observed writes or mutable-state effects: ['bitDepthConvRounding', 'bitsPerComponent', 'bitsPerPixel', 'bpEnable', 'cmd_args', 'cmdarg_s.var_ptr', 'colorDifferenceSiting', 'colorimetry', 'data_u.yuv', 'dpxFileOutput', 'dpxRDatumOrder', 'dpxRForceBe', 'dpxRPadEnds', 'dpxWByteSwap', 'dpxWDatumOrder', 'dpxWForcePacking', 'dpxWPadEnds', 'dscFileOutput', 'dsc_cfg_t.bits_per_component', 'dsc_cfg_t.convert_rgb', 'dsc_cfg_t.mux_word_size', 'dsc_cfg_t.native_420', 'dsc_cfg_t.native_422', 'dsc_cfg_t.pic_height', 'dsc_cfg_t.pic_width', 'dsc_cfg_t.rcb_bits', 'dsc_cfg_t.simple_422', 'dsc_cfg_t.somewhat_flat_qp_delta', 'dsc_cfg_t.somewhat_flat_qp_thresh', 'dsc_cfg_t.very_flat_qp', 'dsc_cfg_t.xstart', 'dsc_cfg_t.ystart', 'enable422', 'fn_i', 'fn_log', 'fn_o', 'function', 'hdrDpxFileOutput', 'native420', 'native422', 'picHeight', 'picWidth', 'pic_s.alpha', 'pic_s.bits', 'pic_s.chroma_siting', 'pic_s.colorimetry', 'pic_s.data', 'pic_s.h', 'pic_s.transfer', 'pic_s.w', 'ppmFileOutput', 'printPps', 'printPpsFormat', 'rbSwap', 'rbSwapOut', 'rcBufThresh', 'rcMaxQp', 'rcMinQp', 'rcOffset', 'simple422', 'sliceHeight', 'sliceWidth', 'transferFunction', 'useYuvInput', 'yuvFileFormat', 'yuvFileOutput', 'yuv_s.u', 'yuv_s.v', 'yuv_s.y']
  - AST pointer modes: ['UNKNOWN']
  - AST observed global reads: __stderrp, __stderrp, __stderrp, __stderrp, __stderrp, __stderrp, __stderrp, __stderrp, __stderrp, __stderrp, __stderrp, __stderrp, __stderrp, __stderrp, __stderrp, __stderrp, __stderrp, __stdoutp, __stdoutp, __stdoutp, bitDepthConvRounding, bitsPerComponent, bitsPerComponent, bitsPerComponent, bitsPerComponent, bitsPerComponent, bitsPerComponent, bitsPerPixel, bitsPerPixel, bitsPerPixel, bpEnable, cmd_args, colorDifferenceSiting, colorDifferenceSiting, colorDifferenceSiting, colorDifferenceSiting, colorimetry, colorimetry, colorimetry, colorimetry, dpxFileOutput, dpxFileOutput, dpxFileOutput, dpxRDatumOrder, dpxRForceBe, dpxRPadEnds, dpxWByteSwap, dpxWByteSwap, dpxWDatumOrder, dpxWDatumOrder, dpxWForcePacking, dpxWForcePacking, dpxWPadEnds, dpxWPadEnds, dscFileOutput, dscFileOutput, dscFileOutput, enable422, fn_i, fn_i, fn_log, fn_o, fn_o, fn_o, fn_o, fn_o, fn_o, fn_o, fn_o, fn_o, fn_o, fn_o, fn_o, function, function, function, function, function, function, function, function, function, function, function, function, function, function, function, function, function, function, function, function, hdrDpxFileOutput, hdrDpxFileOutput, hdrDpxFileOutput, native420, native420, native420, native420, native422, native422, native422, native422, picHeight, picHeight, picWidth, picWidth, ppmFileOutput, ppmFileOutput, printPps, printPpsFormat, printPpsFormat, printPpsFormat, printPpsFormat, rbSwap, rbSwapOut, rbSwapOut, rcBufThresh, rcMaxQp, rcMinQp, rcOffset, simple422, simple422, simple422, sliceHeight, sliceWidth, transferFunction, transferFunction, transferFunction, transferFunction, useYuvInput, useYuvInput, useYuvInput, useYuvInput, useYuvInput, yuvFileFormat, yuvFileFormat, yuvFileFormat, yuvFileOutput, yuvFileOutput
  - AST observed field reads: data_u.yuv, data_u.yuv, data_u.yuv, data_u.yuv, data_u.yuv, data_u.yuv, data_u.yuv, data_u.yuv, dsc_cfg_t.bits_per_component, dsc_cfg_t.bits_per_component, dsc_cfg_t.bits_per_component, dsc_cfg_t.bits_per_component, dsc_cfg_t.bits_per_component, dsc_cfg_t.bits_per_component, dsc_cfg_t.bits_per_component, dsc_cfg_t.bits_per_component, dsc_cfg_t.bits_per_component, dsc_cfg_t.bits_per_component, dsc_cfg_t.bits_per_component, dsc_cfg_t.bits_per_component, dsc_cfg_t.bits_per_pixel, dsc_cfg_t.chunk_size, dsc_cfg_t.chunk_size, dsc_cfg_t.chunk_size, dsc_cfg_t.convert_rgb, dsc_cfg_t.convert_rgb, dsc_cfg_t.convert_rgb, dsc_cfg_t.convert_rgb, dsc_cfg_t.convert_rgb, dsc_cfg_t.initial_dec_delay, dsc_cfg_t.initial_xmit_delay, dsc_cfg_t.native_420, dsc_cfg_t.native_420, dsc_cfg_t.native_420, dsc_cfg_t.native_420, dsc_cfg_t.native_420, dsc_cfg_t.native_420, dsc_cfg_t.native_420, dsc_cfg_t.native_420, dsc_cfg_t.native_420, dsc_cfg_t.native_420, dsc_cfg_t.native_420, dsc_cfg_t.native_420, dsc_cfg_t.native_420, dsc_cfg_t.native_420, dsc_cfg_t.native_420, dsc_cfg_t.native_420, dsc_cfg_t.native_422, dsc_cfg_t.native_422, dsc_cfg_t.native_422, dsc_cfg_t.native_422, dsc_cfg_t.native_422, dsc_cfg_t.native_422, dsc_cfg_t.native_422, dsc_cfg_t.native_422, dsc_cfg_t.native_422, dsc_cfg_t.native_422, dsc_cfg_t.native_422, dsc_cfg_t.pic_height, dsc_cfg_t.pic_height, dsc_cfg_t.pic_height, dsc_cfg_t.pic_height, dsc_cfg_t.pic_height, dsc_cfg_t.pic_height, dsc_cfg_t.pic_height, dsc_cfg_t.pic_width, dsc_cfg_t.pic_width, dsc_cfg_t.pic_width, dsc_cfg_t.pic_width, dsc_cfg_t.pic_width, dsc_cfg_t.pic_width, dsc_cfg_t.pic_width, dsc_cfg_t.simple_422, dsc_cfg_t.simple_422, dsc_cfg_t.simple_422, dsc_cfg_t.simple_422, dsc_cfg_t.simple_422, dsc_cfg_t.simple_422, dsc_cfg_t.simple_422, dsc_cfg_t.simple_422, dsc_cfg_t.slice_height, dsc_cfg_t.slice_height, dsc_cfg_t.slice_height, dsc_cfg_t.slice_width, dsc_cfg_t.slice_width, dsc_cfg_t.slice_width, dsc_cfg_t.slice_width, dsc_cfg_t.slice_width, dsc_cfg_t.slice_width, dsc_cfg_t.vbr_enable, dsc_cfg_t.vbr_enable, pic_s.bits, pic_s.bits, pic_s.bits, pic_s.bits, pic_s.bits, pic_s.bits, pic_s.bits, pic_s.bits, pic_s.bits, pic_s.bits, pic_s.bits, pic_s.bits, pic_s.bits, pic_s.bits, pic_s.bits, pic_s.bits, pic_s.bits, pic_s.bits, pic_s.bits, pic_s.chroma, pic_s.chroma, pic_s.chroma, pic_s.chroma, pic_s.chroma, pic_s.chroma, pic_s.color, pic_s.color, pic_s.color, pic_s.color, pic_s.color, pic_s.color, pic_s.color, pic_s.color, pic_s.color, pic_s.color, pic_s.color, pic_s.color, pic_s.color, pic_s.color, pic_s.data, pic_s.data, pic_s.data, pic_s.data, pic_s.data, pic_s.data, pic_s.data, pic_s.data, pic_s.h, pic_s.h, pic_s.h, pic_s.h, pic_s.h, pic_s.h, pic_s.h, pic_s.h, pic_s.h, pic_s.h, pic_s.h, pic_s.h, pic_s.h, pic_s.h, pic_s.h, pic_s.w, pic_s.w, pic_s.w, pic_s.w, pic_s.w, pic_s.w, pic_s.w, pic_s.w, pic_s.w, pic_s.w, pic_s.w, pic_s.w, pic_s.w, pic_s.w, pic_s.w, yuv_s.u, yuv_s.u, yuv_s.v, yuv_s.v, yuv_s.v, yuv_s.y, yuv_s.y, yuv_s.y
  - AST loop count is 15; trip proofs are retained per loop

## `make_qp_table`

- Source: `rc_tables.h:404`
- Clang USR: `c:@F@make_qp_table`
- Return: `void`; parameters: `table: char **`, `dest: int ***`
- Callers: make_qp_tables
- Callees: line_to_int, malloc
- Global read/write: 0/0; field read/write: 0/0
- Pointer modes: table=UNKNOWN, dest=UNKNOWN
- Loops: 1; fixed counts: 15
- Effects: `{"assert": false, "file_io": false, "indirect_call": false, "logging": false, "malloc": true}`
- Proposal: **IO_OR_DEBUG**; purity=False; combinational=False
- Classification evidence:
  - AST observed no global/field/pointee writes
  - AST pointer modes: ['UNKNOWN', 'UNKNOWN']
  - AST loop count is 1; trip proofs are retained per loop

## `make_qp_tables`

- Source: `rc_tables.h:414`
- Clang USR: `c:@F@make_qp_tables`
- Return: `void`; parameters: NONE
- Callers: generate_rc_parameters
- Callees: make_qp_table
- Global read/write: 36/0; field read/write: 0/0
- Pointer modes: NONE
- Loops: 0; fixed counts: UNKNOWN
- Effects: `{"assert": false, "file_io": false, "indirect_call": false, "logging": false, "malloc": false}`
- Proposal: **COMPOSITE_COMB_CANDIDATE**; purity=False; combinational=True
- Classification evidence:
  - AST observed no global/field/pointee writes
  - AST observed global reads: maxqp420_10b, maxqp420_12b, maxqp420_8b, maxqp422_10b, maxqp422_12b, maxqp422_8b, maxqp444_10b, maxqp444_12b, maxqp444_8b, maxqp_420, maxqp_420, maxqp_420, maxqp_422, maxqp_422, maxqp_422, maxqp_444, maxqp_444, maxqp_444, minqp420_10b, minqp420_12b, minqp420_8b, minqp422_10b, minqp422_12b, minqp422_8b, minqp444_10b, minqp444_12b, minqp444_8b, minqp_420, minqp_420, minqp_420, minqp_422, minqp_422, minqp_422, minqp_444, minqp_444, minqp_444
  - AST observed no loop

## `merge_cmd_args`

- Source: `cmd_parse.c:1180`
- Clang USR: `c:@F@merge_cmd_args`
- Return: `cmdarg_t *`; parameters: `args1: cmdarg_t *`, `args2: cmdarg_t *`
- Callers: NONE
- Callees: calloc
- Global read/write: 0/0; field read/write: 14/12
- Pointer modes: args1=READ_ONLY, args2=READ_ONLY
- Loops: 4; fixed counts: UNKNOWN
- Effects: `{"assert": false, "file_io": false, "indirect_call": false, "logging": false, "malloc": true}`
- Proposal: **IO_OR_DEBUG**; purity=False; combinational=False
- Classification evidence:
  - AST observed writes or mutable-state effects: ['cmdarg_s.cmd', 'cmdarg_s.key', 'cmdarg_s.type', 'cmdarg_s.value', 'cmdarg_s.var_ptr', 'cmdarg_s.vct_lng']
  - AST pointer modes: ['READ_ONLY', 'READ_ONLY']
  - AST observed field reads: cmdarg_s.cmd, cmdarg_s.cmd, cmdarg_s.key, cmdarg_s.key, cmdarg_s.type, cmdarg_s.type, cmdarg_s.value, cmdarg_s.value, cmdarg_s.var_ptr, cmdarg_s.var_ptr, cmdarg_s.var_ptr, cmdarg_s.var_ptr, cmdarg_s.vct_lng, cmdarg_s.vct_lng
  - AST loop count is 4; trip proofs are retained per loop

## `order_cmds`

- Source: `cmd_parse.c:1045`
- Clang USR: `c:cmd_parse.c@F@order_cmds`
- Return: `int *`; parameters: `cmdargs: cmdarg_t *`, `num_args: int`
- Callers: parse_cmd, parse_cmd_usage
- Callees: Assert_func, calloc, strcmp
- Global read/write: 0/0; field read/write: 5/0
- Pointer modes: cmdargs=UNKNOWN
- Loops: 3; fixed counts: UNKNOWN
- Effects: `{"assert": true, "file_io": false, "indirect_call": false, "logging": false, "malloc": true}`
- Proposal: **IO_OR_DEBUG**; purity=False; combinational=False
- Classification evidence:
  - AST observed no global/field/pointee writes
  - AST pointer modes: ['UNKNOWN']
  - AST observed field reads: cmdarg_s.cmd, cmdarg_s.cmd, cmdarg_s.cmd, cmdarg_s.cmd, cmdarg_s.cmd
  - AST loop count is 3; trip proofs are retained per loop

## `order_keys`

- Source: `cmd_parse.c:1012`
- Clang USR: `c:cmd_parse.c@F@order_keys`
- Return: `int *`; parameters: `cmdargs: cmdarg_t *`, `num_args: int`
- Callers: parse_key_usage
- Callees: Assert_func, calloc, strcmp
- Global read/write: 0/0; field read/write: 5/0
- Pointer modes: cmdargs=UNKNOWN
- Loops: 3; fixed counts: UNKNOWN
- Effects: `{"assert": true, "file_io": false, "indirect_call": false, "logging": false, "malloc": true}`
- Proposal: **IO_OR_DEBUG**; purity=False; combinational=False
- Classification evidence:
  - AST observed no global/field/pointee writes
  - AST pointer modes: ['UNKNOWN']
  - AST observed field reads: cmdarg_s.cmd, cmdarg_s.cmd, cmdarg_s.key, cmdarg_s.key, cmdarg_s.key
  - AST loop count is 3; trip proofs are retained per loop

## `palloc`

- Source: `utl.c:55`
- Clang USR: `c:@F@palloc`
- Return: `void *`; parameters: `w: int`, `h: int`
- Callers: pcreate, pcreate_ext
- Callees: __assert_rtn, __builtin_expect, calloc, exit, fprintf
- Global read/write: 2/0; field read/write: 0/0
- Pointer modes: NONE
- Loops: 1; fixed counts: UNKNOWN
- Effects: `{"assert": true, "file_io": true, "indirect_call": false, "logging": false, "malloc": true}`
- Proposal: **IO_OR_DEBUG**; purity=False; combinational=False
- Classification evidence:
  - AST observed no global/field/pointee writes
  - AST observed global reads: __stderrp, __stderrp
  - AST loop count is 1; trip proofs are retained per loop

## `parse_cfgfile`

- Source: `codec_main.c:314`
- Clang USR: `c:codec_main.c@F@parse_cfgfile`
- Return: `int`; parameters: `fn: char *`, `cmdargs: cmdarg_t *`
- Callers: assign_line, process_args
- Callees: Err, PErr, fclose, feof, fgets, fopen, assign_line
- Global read/write: 0/0; field read/write: 0/0
- Pointer modes: fn=UNKNOWN, cmdargs=UNKNOWN
- Loops: 1; fixed counts: UNKNOWN
- Effects: `{"assert": false, "file_io": true, "indirect_call": false, "logging": false, "malloc": false}`
- Proposal: **IO_OR_DEBUG**; purity=False; combinational=False
- Classification evidence:
  - AST observed no global/field/pointee writes
  - AST pointer modes: ['UNKNOWN', 'UNKNOWN']
  - AST loop count is 1; trip proofs are retained per loop

## `parse_cmd`

- Source: `cmd_parse.c:1255`
- Clang USR: `c:@F@parse_cmd`
- Return: `int`; parameters: `arg0: char *`, `arg1: char *`, `cmdargs: cmdarg_t *`
- Callers: parse_cmd_strict, process_args
- Callees: Assert_func, CErr, free, strlen, assign_val, distinguish_dist, error_check, order_cmds, test_cmd
- Global read/write: 0/0; field read/write: 8/0
- Pointer modes: arg0=UNKNOWN, arg1=READ_ONLY, cmdargs=UNKNOWN
- Loops: 3; fixed counts: UNKNOWN
- Effects: `{"assert": true, "file_io": false, "indirect_call": false, "logging": false, "malloc": true}`
- Proposal: **IO_OR_DEBUG**; purity=False; combinational=False
- Classification evidence:
  - AST observed no global/field/pointee writes
  - AST pointer modes: ['READ_ONLY', 'UNKNOWN', 'UNKNOWN']
  - AST observed field reads: cmdarg_s.cmd, cmdarg_s.cmd, cmdarg_s.type, cmdarg_s.type, cmdarg_s.type, cmdarg_s.type, cmdarg_s.type, cmdarg_s.var_ptr
  - AST loop count is 3; trip proofs are retained per loop

## `parse_cmd_strict`

- Source: `cmd_parse.c:1307`
- Clang USR: `c:@F@parse_cmd_strict`
- Return: `int`; parameters: `arg0: char *`, `arg1: char *`, `cmdargs: cmdarg_t *`
- Callers: NONE
- Callees: exit, parse_cmd, parse_cmd_usage, printf
- Global read/write: 0/0; field read/write: 0/0
- Pointer modes: arg0=UNKNOWN, arg1=UNKNOWN, cmdargs=UNKNOWN
- Loops: 0; fixed counts: UNKNOWN
- Effects: `{"assert": false, "file_io": false, "indirect_call": false, "logging": true, "malloc": false}`
- Proposal: **IO_OR_DEBUG**; purity=False; combinational=False
- Classification evidence:
  - AST observed no global/field/pointee writes
  - AST pointer modes: ['UNKNOWN', 'UNKNOWN', 'UNKNOWN']
  - AST observed no loop

## `parse_cmd_usage`

- Source: `cmd_parse.c:1427`
- Clang USR: `c:@F@parse_cmd_usage`
- Return: `void`; parameters: `cmdargs: cmdarg_t *`
- Callers: parse_cmd_strict
- Callees: __builtin___strcpy_chk, __builtin_object_size, appendarg, calloc, free, printf, strlen, distinguish_dist, order_cmds
- Global read/write: 0/0; field read/write: 5/0
- Pointer modes: cmdargs=UNKNOWN
- Loops: 3; fixed counts: UNKNOWN
- Effects: `{"assert": false, "file_io": false, "indirect_call": false, "logging": true, "malloc": true}`
- Proposal: **IO_OR_DEBUG**; purity=False; combinational=False
- Classification evidence:
  - AST observed no global/field/pointee writes
  - AST pointer modes: ['UNKNOWN']
  - AST observed field reads: cmdarg_s.cmd, cmdarg_s.cmd, cmdarg_s.cmd, cmdarg_s.cmd, cmdarg_s.var_ptr
  - AST loop count is 3; trip proofs are retained per loop

## `parse_key_usage`

- Source: `cmd_parse.c:1480`
- Clang USR: `c:@F@parse_key_usage`
- Return: `void`; parameters: `cmdargs: cmdarg_t *`
- Callers: parse_line_strict
- Callees: __builtin___strcat_chk, __builtin___strcpy_chk, __builtin_object_size, appendarg, calloc, free, printf, strlen, order_keys
- Global read/write: 0/0; field read/write: 5/0
- Pointer modes: cmdargs=UNKNOWN
- Loops: 2; fixed counts: UNKNOWN
- Effects: `{"assert": false, "file_io": false, "indirect_call": false, "logging": true, "malloc": true}`
- Proposal: **IO_OR_DEBUG**; purity=False; combinational=False
- Classification evidence:
  - AST observed no global/field/pointee writes
  - AST pointer modes: ['UNKNOWN']
  - AST observed field reads: cmdarg_s.cmd, cmdarg_s.key, cmdarg_s.key, cmdarg_s.key, cmdarg_s.var_ptr
  - AST loop count is 2; trip proofs are retained per loop

## `parse_kvline`

- Source: `cmd_parse.c:1142`
- Clang USR: `c:cmd_parse.c@F@parse_kvline`
- Return: `int`; parameters: `in: char *`, `key_r: char **`, `val_r: char **`
- Callers: parse_line
- Callees: Assert_func, UErr, strcspn, strspn, strstr
- Global read/write: 0/0; field read/write: 0/0
- Pointer modes: in=UNKNOWN, key_r=WRITES_THROUGH, val_r=WRITES_THROUGH
- Loops: 0; fixed counts: UNKNOWN
- Effects: `{"assert": true, "file_io": false, "indirect_call": false, "logging": true, "malloc": false}`
- Proposal: **IO_OR_DEBUG**; purity=False; combinational=False
- Classification evidence:
  - AST observed writes or mutable-state effects: ['key_r', 'val_r']
  - AST pointer modes: ['UNKNOWN', 'WRITES_THROUGH', 'WRITES_THROUGH']
  - AST observed no loop

## `parse_line`

- Source: `cmd_parse.c:1219`
- Clang USR: `c:@F@parse_line`
- Return: `int`; parameters: `line: char *`, `cmdargs: cmdarg_t *`
- Callers: parse_line_strict, assign_line
- Callees: Assert_func, CErr, strcmp, assign_val, error_check, parse_kvline
- Global read/write: 0/0; field read/write: 6/0
- Pointer modes: line=UNKNOWN, cmdargs=UNKNOWN
- Loops: 2; fixed counts: UNKNOWN
- Effects: `{"assert": true, "file_io": false, "indirect_call": false, "logging": false, "malloc": false}`
- Proposal: **TEST_OR_CHECKER**; purity=False; combinational=False
- Classification evidence:
  - AST observed no global/field/pointee writes
  - AST pointer modes: ['UNKNOWN', 'UNKNOWN']
  - AST observed field reads: cmdarg_s.key, cmdarg_s.key, cmdarg_s.key, cmdarg_s.key, cmdarg_s.type, cmdarg_s.var_ptr
  - AST loop count is 2; trip proofs are retained per loop

## `parse_line_strict`

- Source: `cmd_parse.c:1318`
- Clang USR: `c:@F@parse_line_strict`
- Return: `void`; parameters: `line: char *`, `cmdargs: cmdarg_t *`
- Callers: NONE
- Callees: exit, parse_key_usage, parse_line, printf
- Global read/write: 0/0; field read/write: 0/0
- Pointer modes: line=UNKNOWN, cmdargs=UNKNOWN
- Loops: 0; fixed counts: UNKNOWN
- Effects: `{"assert": false, "file_io": false, "indirect_call": false, "logging": true, "malloc": false}`
- Proposal: **IO_OR_DEBUG**; purity=False; combinational=False
- Classification evidence:
  - AST observed no global/field/pointee writes
  - AST pointer modes: ['UNKNOWN', 'UNKNOWN']
  - AST observed no loop

## `parse_pps`

- Source: `dsc_utils.c:404`
- Clang USR: `c:@F@parse_pps`
- Return: `void`; parameters: `buf: unsigned char *`, `dsc_cfg: dsc_cfg_t *`
- Callers: main
- Callees: UErr, getbits
- Global read/write: 0/0; field read/write: 3/51
- Pointer modes: buf=UNKNOWN, dsc_cfg=WRITES_THROUGH
- Loops: 2; fixed counts: 14, 15
- Effects: `{"assert": false, "file_io": false, "indirect_call": false, "logging": true, "malloc": false}`
- Proposal: **IO_OR_DEBUG**; purity=False; combinational=False
- Classification evidence:
  - AST observed writes or mutable-state effects: ['dsc_cfg', 'dsc_cfg_t.bits_per_component', 'dsc_cfg_t.bits_per_pixel', 'dsc_cfg_t.block_pred_enable', 'dsc_cfg_t.chunk_size', 'dsc_cfg_t.convert_rgb', 'dsc_cfg_t.dsc_version_minor', 'dsc_cfg_t.final_offset', 'dsc_cfg_t.first_line_bpg_ofs', 'dsc_cfg_t.flatness_max_qp', 'dsc_cfg_t.flatness_min_qp', 'dsc_cfg_t.initial_dec_delay', 'dsc_cfg_t.initial_offset', 'dsc_cfg_t.initial_scale_value', 'dsc_cfg_t.initial_xmit_delay', 'dsc_cfg_t.linebuf_depth', 'dsc_cfg_t.native_420', 'dsc_cfg_t.native_422', 'dsc_cfg_t.nfl_bpg_offset', 'dsc_cfg_t.nsl_bpg_offset', 'dsc_cfg_t.pic_height', 'dsc_cfg_t.pic_width', 'dsc_cfg_t.pps_identifier', 'dsc_cfg_t.rc_buf_thresh', 'dsc_cfg_t.rc_edge_factor', 'dsc_cfg_t.rc_model_size', 'dsc_cfg_t.rc_quant_incr_limit0', 'dsc_cfg_t.rc_quant_incr_limit1', 'dsc_cfg_t.rc_range_parameters', 'dsc_cfg_t.rc_tgt_offset_hi', 'dsc_cfg_t.rc_tgt_offset_lo', 'dsc_cfg_t.scale_decrement_interval', 'dsc_cfg_t.scale_increment_interval', 'dsc_cfg_t.second_line_bpg_ofs', 'dsc_cfg_t.second_line_ofs_adj', 'dsc_cfg_t.simple_422', 'dsc_cfg_t.slice_bpg_offset', 'dsc_cfg_t.slice_height', 'dsc_cfg_t.slice_width', 'dsc_cfg_t.vbr_enable', 'dsc_range_cfg_t.range_bpg_offset', 'dsc_range_cfg_t.range_max_qp', 'dsc_range_cfg_t.range_min_qp']
  - AST pointer modes: ['UNKNOWN', 'WRITES_THROUGH']
  - AST observed field reads: dsc_cfg_t.bits_per_component, dsc_cfg_t.dsc_version_minor, dsc_cfg_t.linebuf_depth
  - AST loop count is 2; trip proofs are retained per loop

## `pcopy`

- Source: `utl.c:1520`
- Clang USR: `c:@F@pcopy`
- Return: `pic_t *`; parameters: `ip: pic_t *`
- Callers: NONE
- Callees: pcopy_header, pcreate_ext
- Global read/write: 0/0; field read/write: 71/50
- Pointer modes: ip=UNKNOWN
- Loops: 11; fixed counts: UNKNOWN
- Effects: `{"assert": false, "file_io": false, "indirect_call": false, "logging": false, "malloc": false}`
- Proposal: **STATEFUL**; purity=False; combinational=False
- Classification evidence:
  - AST observed writes or mutable-state effects: ['data_u.gc', 'data_u.rgb', 'data_u.yuv', 'pic_s.data', 'rgb_s.a', 'rgb_s.b', 'rgb_s.g', 'rgb_s.r', 'yuv_s.a', 'yuv_s.u', 'yuv_s.v', 'yuv_s.y']
  - AST pointer modes: ['UNKNOWN']
  - AST observed field reads: data_u.gc, data_u.rgb, data_u.rgb, data_u.rgb, data_u.rgb, data_u.yuv, data_u.yuv, data_u.yuv, data_u.yuv, data_u.yuv, data_u.yuv, data_u.yuv, data_u.yuv, data_u.yuv, data_u.yuv, data_u.yuv, data_u.yuv, pic_s.bits, pic_s.bits, pic_s.chroma, pic_s.chroma, pic_s.chroma, pic_s.color, pic_s.color, pic_s.color, pic_s.color, pic_s.color, pic_s.data, pic_s.data, pic_s.data, pic_s.data, pic_s.data, pic_s.data, pic_s.data, pic_s.data, pic_s.data, pic_s.data, pic_s.data, pic_s.data, pic_s.data, pic_s.data, pic_s.data, pic_s.data, pic_s.data, pic_s.format, pic_s.h, pic_s.h, pic_s.h, pic_s.h, pic_s.h, pic_s.h, pic_s.h, pic_s.w, pic_s.w, pic_s.w, rgb_s.a, rgb_s.b, rgb_s.g, rgb_s.r, yuv_s.a, yuv_s.a, yuv_s.u, yuv_s.u, yuv_s.u, yuv_s.v, yuv_s.v, yuv_s.v, yuv_s.y, yuv_s.y, yuv_s.y, yuv_s.y
  - AST loop count is 11; trip proofs are retained per loop

## `pcopy_header`

- Source: `utl.c:225`
- Clang USR: `c:@F@pcopy_header`
- Return: `void`; parameters: `ip: pic_t *`, `op: pic_t *`
- Callers: convertbits, main, pcopy, rgb2yuv, simple422to444, simple444to422, yuv2rgb, yuv_420_422, yuv_422_420, yuv_422_444, yuv_444_422
- Callees: NONE
- Global read/write: 0/0; field read/write: 11/11
- Pointer modes: ip=READ_ONLY, op=WRITES_THROUGH
- Loops: 0; fixed counts: UNKNOWN
- Effects: `{"assert": false, "file_io": false, "indirect_call": false, "logging": false, "malloc": false}`
- Proposal: **STATEFUL**; purity=False; combinational=False
- Classification evidence:
  - AST observed writes or mutable-state effects: ['op', 'pic_s.alpha', 'pic_s.ar1', 'pic_s.ar2', 'pic_s.chroma_siting', 'pic_s.colorimetry', 'pic_s.framerate', 'pic_s.frm_no', 'pic_s.interlaced', 'pic_s.limited_range', 'pic_s.seq_len', 'pic_s.transfer']
  - AST pointer modes: ['READ_ONLY', 'WRITES_THROUGH']
  - AST observed field reads: pic_s.alpha, pic_s.ar1, pic_s.ar2, pic_s.chroma_siting, pic_s.colorimetry, pic_s.framerate, pic_s.frm_no, pic_s.interlaced, pic_s.limited_range, pic_s.seq_len, pic_s.transfer
  - AST observed no loop

## `pcreate`

- Source: `utl.c:83`
- Clang USR: `c:@F@pcreate`
- Return: `pic_t *`; parameters: `format: int`, `color: int`, `chroma: int`, `w: int`, `h: int`
- Callers: NONE
- Callees: exit, fprintf, malloc, palloc
- Global read/write: 1/0; field read/write: 0/60
- Pointer modes: NONE
- Loops: 0; fixed counts: UNKNOWN
- Effects: `{"assert": false, "file_io": true, "indirect_call": false, "logging": false, "malloc": true}`
- Proposal: **IO_OR_DEBUG**; purity=False; combinational=False
- Classification evidence:
  - AST observed writes or mutable-state effects: ['data_u.rgb', 'data_u.yuv', 'pic_s.alpha', 'pic_s.ar1', 'pic_s.ar2', 'pic_s.chroma', 'pic_s.color', 'pic_s.data', 'pic_s.format', 'pic_s.framerate', 'pic_s.frm_no', 'pic_s.h', 'pic_s.interlaced', 'pic_s.seq_len', 'pic_s.w', 'rgb_s.a', 'rgb_s.b', 'rgb_s.g', 'rgb_s.r', 'yuv_s.a', 'yuv_s.u', 'yuv_s.v', 'yuv_s.y']
  - AST observed global reads: __stderrp
  - AST observed no loop

## `pcreate_ext`

- Source: `utl.c:144`
- Clang USR: `c:@F@pcreate_ext`
- Return: `pic_t *`; parameters: `format: format_t`, `color: color_t`, `chroma: chroma_t`, `w: int`, `h: int`, `bits: int`
- Callers: convertbits, hdr_dpx_create_pic, main, pcopy, ppm_write, readppm, rgba_read, yuv_read, create_dpx_pic
- Callees: exit, fprintf, malloc, palloc
- Global read/write: 2/0; field read/write: 0/67
- Pointer modes: NONE
- Loops: 1; fixed counts: UNKNOWN
- Effects: `{"assert": false, "file_io": true, "indirect_call": false, "logging": false, "malloc": true}`
- Proposal: **IO_OR_DEBUG**; purity=False; combinational=False
- Classification evidence:
  - AST observed writes or mutable-state effects: ['data_u.gc', 'data_u.rgb', 'data_u.yuv', 'pic_s.alpha', 'pic_s.ar1', 'pic_s.ar2', 'pic_s.bits', 'pic_s.chroma', 'pic_s.chroma_siting', 'pic_s.color', 'pic_s.colorimetry', 'pic_s.data', 'pic_s.format', 'pic_s.framerate', 'pic_s.frm_no', 'pic_s.h', 'pic_s.interlaced', 'pic_s.limited_range', 'pic_s.seq_len', 'pic_s.transfer', 'pic_s.w', 'rgb_s.a', 'rgb_s.b', 'rgb_s.g', 'rgb_s.r', 'yuv_s.a', 'yuv_s.u', 'yuv_s.v', 'yuv_s.y']
  - AST observed global reads: __stderrp, __stderrp
  - AST loop count is 1; trip proofs are retained per loop

## `pdestroy`

- Source: `utl.c:241`
- Clang USR: `c:@F@pdestroy`
- Return: `void *`; parameters: `p: pic_t *`
- Callers: main, ppm_write
- Callees: free
- Global read/write: 0/0; field read/write: 86/0
- Pointer modes: p=UNKNOWN
- Loops: 6; fixed counts: UNKNOWN
- Effects: `{"assert": false, "file_io": false, "indirect_call": false, "logging": false, "malloc": true}`
- Proposal: **IO_OR_DEBUG**; purity=False; combinational=False
- Classification evidence:
  - AST observed no global/field/pointee writes
  - AST pointer modes: ['UNKNOWN']
  - AST observed field reads: data_u.gc, data_u.gc, data_u.rgb, data_u.rgb, data_u.rgb, data_u.rgb, data_u.rgb, data_u.rgb, data_u.rgb, data_u.rgb, data_u.yuv, data_u.yuv, data_u.yuv, data_u.yuv, data_u.yuv, data_u.yuv, data_u.yuv, data_u.yuv, data_u.yuv, data_u.yuv, data_u.yuv, data_u.yuv, data_u.yuv, data_u.yuv, data_u.yuv, data_u.yuv, pic_s.chroma, pic_s.color, pic_s.color, pic_s.color, pic_s.color, pic_s.data, pic_s.data, pic_s.data, pic_s.data, pic_s.data, pic_s.data, pic_s.data, pic_s.data, pic_s.data, pic_s.data, pic_s.data, pic_s.data, pic_s.data, pic_s.data, pic_s.data, pic_s.data, pic_s.data, pic_s.data, pic_s.data, pic_s.data, pic_s.data, pic_s.data, pic_s.data, pic_s.data, pic_s.data, pic_s.data, pic_s.h, pic_s.h, pic_s.h, pic_s.h, pic_s.h, rgb_s.a, rgb_s.a, rgb_s.b, rgb_s.b, rgb_s.g, rgb_s.g, rgb_s.r, rgb_s.r, yuv_s.a, yuv_s.a, yuv_s.a, yuv_s.a, yuv_s.u, yuv_s.u, yuv_s.u, yuv_s.u, yuv_s.v, yuv_s.v, yuv_s.v, yuv_s.v, yuv_s.y, yuv_s.y, yuv_s.y, yuv_s.y
  - AST loop count is 6; trip proofs are retained per loop

## `populate_pps`

- Source: `codec_main.c:1047`
- Clang USR: `c:@F@populate_pps`
- Return: `void`; parameters: `dsc_codec: dsc_cfg_t *`, `slicew: int *`, `sliceh: int *`
- Callers: main
- Callees: UErr, check_qp_for_overflow, compute_rc_parameters, generate_rc_parameters, printf
- Global read/write: 66/1; field read/write: 58/44
- Pointer modes: dsc_codec=UNKNOWN, slicew=WRITES_THROUGH, sliceh=UNKNOWN
- Loops: 4; fixed counts: 15
- Effects: `{"assert": false, "file_io": false, "indirect_call": false, "logging": true, "malloc": false}`
- Proposal: **IO_OR_DEBUG**; purity=False; combinational=False
- Classification evidence:
  - AST observed writes or mutable-state effects: ['autoSliceHeightAlgorithm', 'bitsPerComponent', 'bitsPerPixel', 'bpEnable', 'dscVersionMinor', 'dsc_cfg_t.bits_per_component', 'dsc_cfg_t.bits_per_pixel', 'dsc_cfg_t.block_pred_enable', 'dsc_cfg_t.convert_rgb', 'dsc_cfg_t.dsc_version_minor', 'dsc_cfg_t.flatness_det_thresh', 'dsc_cfg_t.flatness_max_qp', 'dsc_cfg_t.flatness_min_qp', 'dsc_cfg_t.full_ich_err_precision', 'dsc_cfg_t.initial_offset', 'dsc_cfg_t.initial_scale_value', 'dsc_cfg_t.initial_xmit_delay', 'dsc_cfg_t.linebuf_depth', 'dsc_cfg_t.mux_word_size', 'dsc_cfg_t.native_420', 'dsc_cfg_t.native_422', 'dsc_cfg_t.rc_buf_thresh', 'dsc_cfg_t.rc_edge_factor', 'dsc_cfg_t.rc_model_size', 'dsc_cfg_t.rc_quant_incr_limit0', 'dsc_cfg_t.rc_quant_incr_limit1', 'dsc_cfg_t.rc_range_parameters', 'dsc_cfg_t.rc_tgt_offset_hi', 'dsc_cfg_t.rc_tgt_offset_lo', 'dsc_cfg_t.rcb_bits', 'dsc_cfg_t.second_line_ofs_adj', 'dsc_cfg_t.simple_422', 'dsc_cfg_t.slice_height', 'dsc_cfg_t.slice_width', 'dsc_cfg_t.somewhat_flat_qp_delta', 'dsc_cfg_t.somewhat_flat_qp_thresh', 'dsc_cfg_t.vbr_enable', 'dsc_cfg_t.very_flat_qp', 'dsc_cfg_t.xstart', 'dsc_cfg_t.ystart', 'dsc_range_cfg_t.range_bpg_offset', 'dsc_range_cfg_t.range_max_qp', 'dsc_range_cfg_t.range_min_qp', 'enableVbr', 'flatnessDetThresh', 'flatnessMaxQp', 'flatnessMinQp', 'fullIchErrPrecision', 'function', 'generateRcParameters', 'initialDelay', 'initialFullnessOfs', 'lineBufferBpc', 'native420', 'native422', 'quantIncrLimit0', 'quantIncrLimit1', 'rcBufThresh', 'rcEdgeFactor', 'rcMaxQp', 'rcMinQp', 'rcModelSize', 'rcOffset', 'secondLineOfsAdj', 'simple422', 'sliceHeight', 'sliceWidth', 'slicew', 'tgtOffsetHi', 'tgtOffsetLo', 'useYuvInput']
  - AST pointer modes: ['UNKNOWN', 'UNKNOWN', 'WRITES_THROUGH']
  - AST observed global reads: autoSliceHeightAlgorithm, autoSliceHeightAlgorithm, bitsPerComponent, bitsPerComponent, bitsPerComponent, bitsPerComponent, bitsPerComponent, bitsPerPixel, bpEnable, dscVersionMinor, dscVersionMinor, dscVersionMinor, dscVersionMinor, dscVersionMinor, enableVbr, flatnessDetThresh, flatnessMaxQp, flatnessMinQp, fullIchErrPrecision, fullIchErrPrecision, function, generateRcParameters, generateRcParameters, initialDelay, initialFullnessOfs, lineBufferBpc, lineBufferBpc, native420, native420, native420, native422, native422, quantIncrLimit0, quantIncrLimit1, rcBufThresh, rcBufThresh, rcBufThresh, rcBufThresh, rcEdgeFactor, rcEdgeFactor, rcMaxQp, rcMaxQp, rcMaxQp, rcMaxQp, rcMinQp, rcMinQp, rcMinQp, rcMinQp, rcModelSize, rcModelSize, rcModelSize, rcOffset, rcOffset, rcOffset, rcOffset, secondLineOfsAdj, simple422, sliceHeight, sliceHeight, sliceHeight, sliceWidth, sliceWidth, tgtOffsetHi, tgtOffsetLo, useYuvInput, useYuvInput
  - AST observed field reads: dsc_cfg_t.bits_per_component, dsc_cfg_t.bits_per_component, dsc_cfg_t.bits_per_component, dsc_cfg_t.bits_per_component, dsc_cfg_t.bits_per_component, dsc_cfg_t.bits_per_component, dsc_cfg_t.bits_per_component, dsc_cfg_t.bits_per_component, dsc_cfg_t.bits_per_component, dsc_cfg_t.bits_per_component, dsc_cfg_t.bits_per_component, dsc_cfg_t.block_pred_enable, dsc_cfg_t.flatness_max_qp, dsc_cfg_t.flatness_min_qp, dsc_cfg_t.initial_offset, dsc_cfg_t.initial_offset, dsc_cfg_t.initial_offset, dsc_cfg_t.initial_scale_value, dsc_cfg_t.initial_xmit_delay, dsc_cfg_t.linebuf_depth, dsc_cfg_t.linebuf_depth, dsc_cfg_t.native_420, dsc_cfg_t.native_420, dsc_cfg_t.native_422, dsc_cfg_t.pic_height, dsc_cfg_t.pic_height, dsc_cfg_t.pic_height, dsc_cfg_t.pic_height, dsc_cfg_t.pic_height, dsc_cfg_t.pic_height, dsc_cfg_t.pic_height, dsc_cfg_t.pic_height, dsc_cfg_t.pic_width, dsc_cfg_t.pic_width, dsc_cfg_t.pic_width, dsc_cfg_t.rc_buf_thresh, dsc_cfg_t.rc_buf_thresh, dsc_cfg_t.rc_edge_factor, dsc_cfg_t.rc_model_size, dsc_cfg_t.rc_model_size, dsc_cfg_t.rc_model_size, dsc_cfg_t.rc_model_size, dsc_cfg_t.rc_quant_incr_limit0, dsc_cfg_t.rc_quant_incr_limit1, dsc_cfg_t.rc_range_parameters, dsc_cfg_t.rc_range_parameters, dsc_cfg_t.rc_range_parameters, dsc_cfg_t.rc_range_parameters, dsc_cfg_t.rc_tgt_offset_hi, dsc_cfg_t.rc_tgt_offset_lo, dsc_cfg_t.simple_422, dsc_cfg_t.slice_height, dsc_cfg_t.slice_width, dsc_cfg_t.vbr_enable, dsc_range_cfg_t.range_bpg_offset, dsc_range_cfg_t.range_max_qp, dsc_range_cfg_t.range_max_qp, dsc_range_cfg_t.range_min_qp
  - AST loop count is 4; trip proofs are retained per loop

## `ppm_read`

- Source: `utl.c:1206`
- Clang USR: `c:@F@ppm_read`
- Return: `int`; parameters: `fname: char *`, `pic: pic_t **`
- Callers: main
- Callees: fclose, fopen, readppm
- Global read/write: 0/0; field read/write: 0/0
- Pointer modes: fname=READ_ONLY, pic=WRITES_THROUGH
- Loops: 0; fixed counts: UNKNOWN
- Effects: `{"assert": false, "file_io": true, "indirect_call": false, "logging": false, "malloc": false}`
- Proposal: **IO_OR_DEBUG**; purity=False; combinational=False
- Classification evidence:
  - AST observed writes or mutable-state effects: ['pic']
  - AST pointer modes: ['READ_ONLY', 'WRITES_THROUGH']
  - AST observed no loop

## `ppm_write`

- Source: `utl.c:1246`
- Clang USR: `c:@F@ppm_write`
- Return: `int`; parameters: `fname: char *`, `pic_in: pic_t *`
- Callers: main
- Callees: convertbits, fclose, fopen, pcreate_ext, pdestroy, writeppm, yuv2rgb, yuv_420_422, yuv_422_444
- Global read/write: 0/0; field read/write: 29/1
- Pointer modes: fname=READ_ONLY, pic_in=UNKNOWN
- Loops: 0; fixed counts: UNKNOWN
- Effects: `{"assert": false, "file_io": true, "indirect_call": false, "logging": false, "malloc": false}`
- Proposal: **IO_OR_DEBUG**; purity=False; combinational=False
- Classification evidence:
  - AST observed writes or mutable-state effects: ['pic_s.bits']
  - AST pointer modes: ['READ_ONLY', 'UNKNOWN']
  - AST observed field reads: pic_s.bits, pic_s.bits, pic_s.bits, pic_s.bits, pic_s.bits, pic_s.bits, pic_s.bits, pic_s.bits, pic_s.bits, pic_s.bits, pic_s.bits, pic_s.chroma, pic_s.chroma, pic_s.color, pic_s.color, pic_s.color, pic_s.color, pic_s.h, pic_s.h, pic_s.h, pic_s.h, pic_s.h, pic_s.h, pic_s.w, pic_s.w, pic_s.w, pic_s.w, pic_s.w, pic_s.w
  - AST observed no loop

## `print_pps`

- Source: `dsc_utils.c:609`
- Clang USR: `c:@F@print_pps`
- Return: `void`; parameters: `logfp: FILE *`, `dsc_cfg: dsc_cfg_t *`
- Callers: main
- Callees: fprintf
- Global read/write: 0/0; field read/write: 48/0
- Pointer modes: logfp=UNKNOWN, dsc_cfg=UNKNOWN
- Loops: 2; fixed counts: 14, 15
- Effects: `{"assert": false, "file_io": true, "indirect_call": false, "logging": false, "malloc": false}`
- Proposal: **IO_OR_DEBUG**; purity=False; combinational=False
- Classification evidence:
  - AST observed no global/field/pointee writes
  - AST pointer modes: ['UNKNOWN', 'UNKNOWN']
  - AST observed field reads: dsc_cfg_t.bits_per_component, dsc_cfg_t.bits_per_component, dsc_cfg_t.bits_per_pixel, dsc_cfg_t.bits_per_pixel, dsc_cfg_t.block_pred_enable, dsc_cfg_t.chunk_size, dsc_cfg_t.convert_rgb, dsc_cfg_t.dsc_version_minor, dsc_cfg_t.dsc_version_minor, dsc_cfg_t.final_offset, dsc_cfg_t.first_line_bpg_ofs, dsc_cfg_t.flatness_max_qp, dsc_cfg_t.flatness_min_qp, dsc_cfg_t.initial_dec_delay, dsc_cfg_t.initial_offset, dsc_cfg_t.initial_scale_value, dsc_cfg_t.initial_xmit_delay, dsc_cfg_t.linebuf_depth, dsc_cfg_t.linebuf_depth, dsc_cfg_t.native_420, dsc_cfg_t.native_422, dsc_cfg_t.nfl_bpg_offset, dsc_cfg_t.nsl_bpg_offset, dsc_cfg_t.pic_height, dsc_cfg_t.pic_width, dsc_cfg_t.pps_identifier, dsc_cfg_t.rc_buf_thresh, dsc_cfg_t.rc_edge_factor, dsc_cfg_t.rc_model_size, dsc_cfg_t.rc_quant_incr_limit0, dsc_cfg_t.rc_quant_incr_limit1, dsc_cfg_t.rc_range_parameters, dsc_cfg_t.rc_range_parameters, dsc_cfg_t.rc_range_parameters, dsc_cfg_t.rc_tgt_offset_hi, dsc_cfg_t.rc_tgt_offset_lo, dsc_cfg_t.scale_decrement_interval, dsc_cfg_t.scale_increment_interval, dsc_cfg_t.second_line_bpg_ofs, dsc_cfg_t.second_line_ofs_adj, dsc_cfg_t.simple_422, dsc_cfg_t.slice_bpg_offset, dsc_cfg_t.slice_height, dsc_cfg_t.slice_width, dsc_cfg_t.vbr_enable, dsc_range_cfg_t.range_bpg_offset, dsc_range_cfg_t.range_max_qp, dsc_range_cfg_t.range_min_qp
  - AST loop count is 2; trip proofs are retained per loop

## `print_pps_v2`

- Source: `dsc_utils.c:694`
- Clang USR: `c:@F@print_pps_v2`
- Return: `void`; parameters: `logfp: FILE *`, `dsc_cfg: dsc_cfg_t *`
- Callers: main
- Callees: __builtin___memset_chk, __builtin___sprintf_chk, __builtin_object_size, fprintf, write_pps
- Global read/write: 0/0; field read/write: 59/0
- Pointer modes: logfp=UNKNOWN, dsc_cfg=UNKNOWN
- Loops: 3; fixed counts: 128, 14, 15
- Effects: `{"assert": false, "file_io": true, "indirect_call": false, "logging": true, "malloc": false}`
- Proposal: **IO_OR_DEBUG**; purity=False; combinational=False
- Classification evidence:
  - AST observed no global/field/pointee writes
  - AST pointer modes: ['UNKNOWN', 'UNKNOWN']
  - AST observed field reads: dsc_cfg_t.bits_per_component, dsc_cfg_t.bits_per_component, dsc_cfg_t.bits_per_pixel, dsc_cfg_t.bits_per_pixel, dsc_cfg_t.bits_per_pixel, dsc_cfg_t.block_pred_enable, dsc_cfg_t.chunk_size, dsc_cfg_t.convert_rgb, dsc_cfg_t.dsc_version_minor, dsc_cfg_t.dsc_version_minor, dsc_cfg_t.final_offset, dsc_cfg_t.first_line_bpg_ofs, dsc_cfg_t.flatness_max_qp, dsc_cfg_t.flatness_min_qp, dsc_cfg_t.initial_dec_delay, dsc_cfg_t.initial_offset, dsc_cfg_t.initial_scale_value, dsc_cfg_t.initial_scale_value, dsc_cfg_t.initial_xmit_delay, dsc_cfg_t.linebuf_depth, dsc_cfg_t.linebuf_depth, dsc_cfg_t.native_420, dsc_cfg_t.native_420, dsc_cfg_t.native_422, dsc_cfg_t.native_422, dsc_cfg_t.nfl_bpg_offset, dsc_cfg_t.nfl_bpg_offset, dsc_cfg_t.nsl_bpg_offset, dsc_cfg_t.nsl_bpg_offset, dsc_cfg_t.pic_height, dsc_cfg_t.pic_width, dsc_cfg_t.pps_identifier, dsc_cfg_t.rc_buf_thresh, dsc_cfg_t.rc_buf_thresh, dsc_cfg_t.rc_edge_factor, dsc_cfg_t.rc_edge_factor, dsc_cfg_t.rc_model_size, dsc_cfg_t.rc_quant_incr_limit0, dsc_cfg_t.rc_quant_incr_limit1, dsc_cfg_t.rc_range_parameters, dsc_cfg_t.rc_range_parameters, dsc_cfg_t.rc_range_parameters, dsc_cfg_t.rc_range_parameters, dsc_cfg_t.rc_tgt_offset_hi, dsc_cfg_t.rc_tgt_offset_lo, dsc_cfg_t.scale_decrement_interval, dsc_cfg_t.scale_increment_interval, dsc_cfg_t.second_line_bpg_ofs, dsc_cfg_t.second_line_ofs_adj, dsc_cfg_t.simple_422, dsc_cfg_t.slice_bpg_offset, dsc_cfg_t.slice_bpg_offset, dsc_cfg_t.slice_height, dsc_cfg_t.slice_width, dsc_cfg_t.vbr_enable, dsc_range_cfg_t.range_bpg_offset, dsc_range_cfg_t.range_bpg_offset, dsc_range_cfg_t.range_max_qp, dsc_range_cfg_t.range_min_qp
  - AST loop count is 3; trip proofs are retained per loop

## `process_args`

- Source: `codec_main.c:402`
- Clang USR: `c:codec_main.c@F@process_args`
- Return: `int`; parameters: `argc: int`, `argv: char **`, `cmdargs: cmdarg_t *`
- Callers: main
- Callees: __builtin___strcpy_chk, __builtin_object_size, fprintf, parse_cmd, usage, assign_line, parse_cfgfile
- Global read/write: 11/1; field read/write: 0/0
- Pointer modes: argv=UNKNOWN, cmdargs=UNKNOWN
- Loops: 1; fixed counts: UNKNOWN
- Effects: `{"assert": false, "file_io": true, "indirect_call": false, "logging": false, "malloc": false}`
- Proposal: **IO_OR_DEBUG**; purity=False; combinational=False
- Classification evidence:
  - AST observed writes or mutable-state effects: ['filepath', 'fn_i', 'fn_o', 'help', 'option']
  - AST pointer modes: ['UNKNOWN', 'UNKNOWN']
  - AST observed global reads: __stderrp, __stderrp, filepath, filepath, fn_i, fn_i, fn_o, fn_o, help, option, option
  - AST loop count is 1; trip proofs are retained per loop

## `putbits`

- Source: `dsc_utils.c:81`
- Clang USR: `c:@F@putbits`
- Return: `void`; parameters: `val: int`, `size: int`, `buf: unsigned char *`, `bit_count: int *`
- Callers: ProcessGroupEnc, WriteEntryToBitstream, write_pps
- Callees: printf
- Global read/write: 0/0; field read/write: 0/0
- Pointer modes: buf=WRITES_THROUGH, bit_count=WRITES_THROUGH
- Loops: 1; fixed counts: UNKNOWN
- Effects: `{"assert": false, "file_io": false, "indirect_call": false, "logging": true, "malloc": false}`
- Proposal: **IO_OR_DEBUG**; purity=False; combinational=False
- Classification evidence:
  - AST observed writes or mutable-state effects: ['bit_count', 'buf']
  - AST pointer modes: ['WRITES_THROUGH', 'WRITES_THROUGH']
  - AST loop count is 1; trip proofs are retained per loop

## `read_dpx`

- Source: `dpx.c:727`
- Clang USR: `c:@F@read_dpx`
- Return: `int`; parameters: `fname: char *`, `p: pic_t **`, `ar1: int *`, `ar2: int *`, `frameno: int *`, `seqlen: int *`, `framerate: float *`, `interlaced: int *`, `bpp: int *`, `dpx_bugs: int`, `noswap: int`, `datum_order: int`, `swap_r_and_b: int`
- Callers: NONE
- Callees: dpx_read_hl
- Global read/write: 0/0; field read/write: 7/0
- Pointer modes: fname=UNKNOWN, p=UNKNOWN, ar1=WRITES_THROUGH, ar2=WRITES_THROUGH, frameno=WRITES_THROUGH, seqlen=WRITES_THROUGH, framerate=WRITES_THROUGH, interlaced=WRITES_THROUGH, bpp=WRITES_THROUGH
- Loops: 0; fixed counts: UNKNOWN
- Effects: `{"assert": false, "file_io": false, "indirect_call": false, "logging": false, "malloc": false}`
- Proposal: **STATEFUL**; purity=False; combinational=False
- Classification evidence:
  - AST observed writes or mutable-state effects: ['ar1', 'ar2', 'bpp', 'frameno', 'framerate', 'interlaced', 'seqlen']
  - AST pointer modes: ['UNKNOWN', 'UNKNOWN', 'WRITES_THROUGH', 'WRITES_THROUGH', 'WRITES_THROUGH', 'WRITES_THROUGH', 'WRITES_THROUGH', 'WRITES_THROUGH', 'WRITES_THROUGH']
  - AST observed field reads: pic_s.ar1, pic_s.ar2, pic_s.bits, pic_s.framerate, pic_s.frm_no, pic_s.interlaced, pic_s.seq_len
  - AST observed no loop

## `read_dpx_image_data`

- Source: `dpx.c:981`
- Clang USR: `c:dpx.c@F@read_dpx_image_data`
- Return: `int`; parameters: `fp: FILE *`, `p: pic_t **`, `orientation: int`, `sign: int`, `bpp: int`, `descriptor: int`, `rle: int`, `pad_ends: int`, `w: int`, `h: int`, `bswap: int`, `packing: int`, `datum_order: int`, `swap_r_and_b: int`
- Callers: dpx_read_hl
- Callees: feof, fifo_flip_get_bits, fifo_get_bits, fifo_init, fifo_put_bits, fread, create_dpx_pic
- Global read/write: 0/0; field read/write: 131/4
- Pointer modes: fp=UNKNOWN, p=UNKNOWN
- Loops: 7; fixed counts: 4, 6
- Effects: `{"assert": false, "file_io": true, "indirect_call": false, "logging": false, "malloc": false}`
- Proposal: **IO_OR_DEBUG**; purity=False; combinational=False
- Classification evidence:
  - AST observed writes or mutable-state effects: ['pic_s.alpha']
  - AST pointer modes: ['UNKNOWN', 'UNKNOWN']
  - AST observed field reads: data_u.rgb, data_u.rgb, data_u.rgb, data_u.rgb, data_u.rgb, data_u.rgb, data_u.rgb, data_u.rgb, data_u.rgb, data_u.rgb, data_u.rgb, data_u.rgb, data_u.rgb, data_u.rgb, data_u.rgb, data_u.rgb, data_u.rgb, data_u.rgb, data_u.rgb, data_u.rgb, data_u.yuv, data_u.yuv, data_u.yuv, data_u.yuv, data_u.yuv, data_u.yuv, data_u.yuv, data_u.yuv, data_u.yuv, data_u.yuv, data_u.yuv, data_u.yuv, data_u.yuv, data_u.yuv, data_u.yuv, data_u.yuv, data_u.yuv, data_u.yuv, data_u.yuv, data_u.yuv, data_u.yuv, data_u.yuv, data_u.yuv, fifo_s.fullness, fifo_s.fullness, pic_s.data, pic_s.data, pic_s.data, pic_s.data, pic_s.data, pic_s.data, pic_s.data, pic_s.data, pic_s.data, pic_s.data, pic_s.data, pic_s.data, pic_s.data, pic_s.data, pic_s.data, pic_s.data, pic_s.data, pic_s.data, pic_s.data, pic_s.data, pic_s.data, pic_s.data, pic_s.data, pic_s.data, pic_s.data, pic_s.data, pic_s.data, pic_s.data, pic_s.data, pic_s.data, pic_s.data, pic_s.data, pic_s.data, pic_s.data, pic_s.data, pic_s.data, pic_s.data, pic_s.data, pic_s.data, pic_s.data, pic_s.data, pic_s.data, pic_s.data, rgb_s.a, rgb_s.a, rgb_s.b, rgb_s.b, rgb_s.b, rgb_s.b, rgb_s.b, rgb_s.b, rgb_s.g, rgb_s.g, rgb_s.g, rgb_s.g, rgb_s.g, rgb_s.g, rgb_s.r, rgb_s.r, rgb_s.r, rgb_s.r, rgb_s.r, rgb_s.r, yuv_s.a, yuv_s.a, yuv_s.a, yuv_s.u, yuv_s.u, yuv_s.u, yuv_s.u, yuv_s.u, yuv_s.u, yuv_s.v, yuv_s.v, yuv_s.v, yuv_s.v, yuv_s.v, yuv_s.v, yuv_s.y, yuv_s.y, yuv_s.y, yuv_s.y, yuv_s.y, yuv_s.y, yuv_s.y, yuv_s.y
  - AST loop count is 7; trip proofs are retained per loop

## `read_dsc_data`

- Source: `codec_main.c:568`
- Clang USR: `c:@F@read_dsc_data`
- Return: `int`; parameters: `bit_buffer: unsigned char **`, `nbytes: int`, `fp: FILE *`, `vbr_enable: int`, `slices_per_line: int`, `slice_height: int`
- Callers: main
- Callees: fgetc, free, malloc
- Global read/write: 0/0; field read/write: 0/0
- Pointer modes: bit_buffer=WRITES_THROUGH, fp=UNKNOWN
- Loops: 5; fixed counts: 2
- Effects: `{"assert": false, "file_io": false, "indirect_call": false, "logging": false, "malloc": true}`
- Proposal: **IO_OR_DEBUG**; purity=False; combinational=False
- Classification evidence:
  - AST observed writes or mutable-state effects: ['bit_buffer']
  - AST pointer modes: ['UNKNOWN', 'WRITES_THROUGH']
  - AST loop count is 5; trip proofs are retained per loop

## `readppm`

- Source: `utl.c:1068`
- Clang USR: `c:@F@readppm`
- Return: `pic_t *`; parameters: `fp: FILE *`
- Callers: ppm_read
- Callees: Err, __builtin___strcpy_chk, __builtin_object_size, atoi, feof, fgetc, fgets, fscanf, gettoken, pcreate_ext, printf
- Global read/write: 0/0; field read/write: 9/46
- Pointer modes: fp=UNKNOWN
- Loops: 13; fixed counts: UNKNOWN
- Effects: `{"assert": false, "file_io": false, "indirect_call": false, "logging": true, "malloc": false}`
- Proposal: **IO_OR_DEBUG**; purity=False; combinational=False
- Classification evidence:
  - AST observed writes or mutable-state effects: ['data_u.rgb', 'pic_s.data', 'pic_s.limited_range', 'rgb_s.b', 'rgb_s.g', 'rgb_s.r']
  - AST pointer modes: ['UNKNOWN']
  - AST observed field reads: data_u.rgb, data_u.rgb, data_u.rgb, pic_s.data, pic_s.data, pic_s.data, rgb_s.b, rgb_s.g, rgb_s.r
  - AST loop count is 13; trip proofs are retained per loop

## `retrieve_cmds_var`

- Source: `cmd_parse.c:1521`
- Clang USR: `c:@F@retrieve_cmds_var`
- Return: `void *`; parameters: `cmd: char *`, `cmdargs: cmdarg_t *`
- Callers: NONE
- Callees: Assert_func, strcmp
- Global read/write: 0/0; field read/write: 3/0
- Pointer modes: cmd=UNKNOWN, cmdargs=UNKNOWN
- Loops: 1; fixed counts: UNKNOWN
- Effects: `{"assert": true, "file_io": false, "indirect_call": false, "logging": false, "malloc": false}`
- Proposal: **TEST_OR_CHECKER**; purity=False; combinational=False
- Classification evidence:
  - AST observed no global/field/pointee writes
  - AST pointer modes: ['UNKNOWN', 'UNKNOWN']
  - AST observed field reads: cmdarg_s.cmd, cmdarg_s.var_ptr, cmdarg_s.var_ptr
  - AST loop count is 1; trip proofs are retained per loop

## `retrieve_keys_var`

- Source: `cmd_parse.c:1508`
- Clang USR: `c:@F@retrieve_keys_var`
- Return: `void *`; parameters: `key: char *`, `cmdargs: cmdarg_t *`
- Callers: NONE
- Callees: Assert_func, strcmp
- Global read/write: 0/0; field read/write: 3/0
- Pointer modes: key=UNKNOWN, cmdargs=UNKNOWN
- Loops: 1; fixed counts: UNKNOWN
- Effects: `{"assert": true, "file_io": false, "indirect_call": false, "logging": false, "malloc": false}`
- Proposal: **TEST_OR_CHECKER**; purity=False; combinational=False
- Classification evidence:
  - AST observed no global/field/pointee writes
  - AST pointer modes: ['UNKNOWN', 'UNKNOWN']
  - AST observed field reads: cmdarg_s.key, cmdarg_s.var_ptr, cmdarg_s.var_ptr
  - AST loop count is 1; trip proofs are retained per loop

## `rgb2ycocg`

- Source: `dsc_utils.c:145`
- Clang USR: `c:@F@rgb2ycocg`
- Return: `void`; parameters: `ip: pic_t *`, `op: pic_t *`, `dsc_cfg: dsc_cfg_t *`
- Callers: DSC_Algorithm
- Callees: exit, fprintf
- Global read/write: 5/0; field read/write: 28/15
- Pointer modes: ip=READ_ONLY, op=WRITES_THROUGH, dsc_cfg=READ_ONLY
- Loops: 2; fixed counts: UNKNOWN
- Effects: `{"assert": false, "file_io": true, "indirect_call": false, "logging": false, "malloc": false}`
- Proposal: **IO_OR_DEBUG**; purity=False; combinational=False
- Classification evidence:
  - AST observed writes or mutable-state effects: ['data_u.yuv', 'op', 'pic_s.data', 'yuv_s.u', 'yuv_s.v', 'yuv_s.y']
  - AST pointer modes: ['READ_ONLY', 'READ_ONLY', 'WRITES_THROUGH']
  - AST observed global reads: __stderrp, __stderrp, __stderrp, __stderrp, __stderrp
  - AST observed field reads: data_u.rgb, data_u.rgb, data_u.rgb, dsc_cfg_t.slice_height, dsc_cfg_t.slice_width, dsc_cfg_t.xstart, dsc_cfg_t.xstart, dsc_cfg_t.ystart, dsc_cfg_t.ystart, pic_s.bits, pic_s.bits, pic_s.chroma, pic_s.chroma, pic_s.color, pic_s.color, pic_s.color, pic_s.data, pic_s.data, pic_s.data, pic_s.h, pic_s.h, pic_s.h, pic_s.w, pic_s.w, pic_s.w, rgb_s.b, rgb_s.g, rgb_s.r
  - AST loop count is 2; trip proofs are retained per loop

## `rgb2yuv`

- Source: `utl.c:305`
- Clang USR: `c:@F@rgb2yuv`
- Return: `void`; parameters: `ip: pic_t *`, `op: pic_t *`
- Callers: main
- Callees: exit, fprintf, pcopy_header
- Global read/write: 7/0; field read/write: 28/9
- Pointer modes: ip=UNKNOWN, op=WRITES_THROUGH
- Loops: 2; fixed counts: UNKNOWN
- Effects: `{"assert": false, "file_io": true, "indirect_call": false, "logging": false, "malloc": false}`
- Proposal: **IO_OR_DEBUG**; purity=False; combinational=False
- Classification evidence:
  - AST observed writes or mutable-state effects: ['data_u.yuv', 'op', 'pic_s.data', 'yuv_s.u', 'yuv_s.v', 'yuv_s.y']
  - AST pointer modes: ['UNKNOWN', 'WRITES_THROUGH']
  - AST observed global reads: __stderrp, __stderrp, __stderrp, __stderrp, __stderrp, __stderrp, __stderrp
  - AST observed field reads: data_u.rgb, data_u.rgb, data_u.rgb, pic_s.bits, pic_s.bits, pic_s.bits, pic_s.bits, pic_s.bits, pic_s.bits, pic_s.chroma, pic_s.chroma, pic_s.color, pic_s.color, pic_s.color, pic_s.color, pic_s.color, pic_s.data, pic_s.data, pic_s.data, pic_s.h, pic_s.h, pic_s.h, pic_s.w, pic_s.w, pic_s.w, rgb_s.b, rgb_s.g, rgb_s.r
  - AST loop count is 2; trip proofs are retained per loop

## `rgba_read`

- Source: `utl.c:1592`
- Clang USR: `c:@F@rgba_read`
- Return: `int`; parameters: `fname: char *`, `ip: pic_t **`, `width: int`, `height: int`, `bpc: int`, `alpha_present: int`
- Callers: NONE
- Callees: UErr, fclose, fgetc, fopen, pcreate_ext, printf
- Global read/write: 0/0; field read/write: 15/26
- Pointer modes: fname=UNKNOWN, ip=WRITES_THROUGH
- Loops: 2; fixed counts: UNKNOWN
- Effects: `{"assert": false, "file_io": true, "indirect_call": false, "logging": true, "malloc": false}`
- Proposal: **IO_OR_DEBUG**; purity=False; combinational=False
- Classification evidence:
  - AST observed writes or mutable-state effects: ['data_u.rgb', 'ip', 'pic_s.alpha', 'pic_s.data', 'pic_s.limited_range', 'rgb_s.a', 'rgb_s.b', 'rgb_s.g', 'rgb_s.r']
  - AST pointer modes: ['UNKNOWN', 'WRITES_THROUGH']
  - AST observed field reads: data_u.rgb, data_u.rgb, data_u.rgb, data_u.rgb, pic_s.bits, pic_s.data, pic_s.data, pic_s.data, pic_s.data, pic_s.h, pic_s.w, rgb_s.a, rgb_s.b, rgb_s.g, rgb_s.r
  - AST loop count is 2; trip proofs are retained per loop

## `set_convertbits_rounding`

- Source: `utl.c:705`
- Clang USR: `c:@F@set_convertbits_rounding`
- Return: `void`; parameters: `round: int`
- Callers: main
- Callees: NONE
- Global read/write: 0/1; field read/write: 0/0
- Pointer modes: NONE
- Loops: 0; fixed counts: UNKNOWN
- Effects: `{"assert": false, "file_io": false, "indirect_call": false, "logging": false, "malloc": false}`
- Proposal: **STATEFUL**; purity=False; combinational=False
- Classification evidence:
  - AST observed writes or mutable-state effects: ['bit_convert_rounding']
  - AST observed no loop

## `set_defaults`

- Source: `codec_main.c:222`
- Clang USR: `c:@F@set_defaults`
- Return: `void`; parameters: NONE
- Callers: main
- Callees: __builtin___strcpy_chk, __builtin_object_size
- Global read/write: 2/57; field read/write: 0/0
- Pointer modes: NONE
- Loops: 1; fixed counts: 15
- Effects: `{"assert": false, "file_io": false, "indirect_call": false, "logging": false, "malloc": false}`
- Proposal: **STATEFUL**; purity=False; combinational=False
- Classification evidence:
  - AST observed writes or mutable-state effects: ['autoSliceHeightAlgorithm', 'bitDepthConvRounding', 'bitsPerComponent', 'bitsPerPixel', 'bpEnable', 'colorDifferenceSiting', 'colorimetry', 'dpxFileOutput', 'dpxRDatumOrder', 'dpxRForceBe', 'dpxRPadEnds', 'dpxWDatumOrder', 'dpxWForcePacking', 'dpxWPadEnds', 'dscFileOutput', 'dscVersionMinor', 'enable422', 'enableVbr', 'firstLineBpgOfs', 'flatnessDetThresh', 'flatnessMaxQp', 'flatnessMinQp', 'fn_log', 'fn_o', 'fullIchErrPrecision', 'function', 'generateRcParameters', 'hdrDpxFileOutput', 'initialDelay', 'initialFullnessOfs', 'lineBufferBpc', 'native420', 'native422', 'picHeight', 'picWidth', 'ppmFileOutput', 'printPps', 'printPpsFormat', 'quantIncrLimit0', 'quantIncrLimit1', 'rbSwap', 'rbSwapOut', 'rcBufThresh', 'rcEdgeFactor', 'rcMaxQp', 'rcMinQp', 'rcModelSize', 'rcOffset', 'secondLineBpgOfs', 'secondLineOfsAdj', 'simple422', 'sliceHeight', 'sliceWidth', 'tgtOffsetHi', 'tgtOffsetLo', 'transferFunction', 'useYuvInput', 'yuvFileFormat', 'yuvFileOutput']
  - AST observed global reads: fn_log, fn_o
  - AST loop count is 1; trip proofs are retained per loop

## `set_dpx_colorspace`

- Source: `dpx.c:1474`
- Clang USR: `c:@F@set_dpx_colorspace`
- Return: `void`; parameters: `color: int`
- Callers: NONE
- Callees: NONE
- Global read/write: 0/1; field read/write: 0/0
- Pointer modes: NONE
- Loops: 0; fixed counts: UNKNOWN
- Effects: `{"assert": false, "file_io": false, "indirect_call": false, "logging": false, "malloc": false}`
- Proposal: **STATEFUL**; purity=False; combinational=False
- Classification evidence:
  - AST observed writes or mutable-state effects: ['dpxcolor']
  - AST observed no loop

## `simple422to444`

- Source: `dsc_utils.c:306`
- Clang USR: `c:@F@simple422to444`
- Return: `void`; parameters: `ip: pic_t *`, `op: pic_t *`
- Callers: main
- Callees: exit, fprintf, pcopy_header
- Global read/write: 2/0; field read/write: 31/15
- Pointer modes: ip=UNKNOWN, op=WRITES_THROUGH
- Loops: 2; fixed counts: UNKNOWN
- Effects: `{"assert": false, "file_io": true, "indirect_call": false, "logging": false, "malloc": false}`
- Proposal: **IO_OR_DEBUG**; purity=False; combinational=False
- Classification evidence:
  - AST observed writes or mutable-state effects: ['data_u.yuv', 'op', 'pic_s.data', 'yuv_s.u', 'yuv_s.v', 'yuv_s.y']
  - AST pointer modes: ['UNKNOWN', 'WRITES_THROUGH']
  - AST observed global reads: __stderrp, __stderrp
  - AST observed field reads: data_u.yuv, data_u.yuv, data_u.yuv, data_u.yuv, data_u.yuv, data_u.yuv, data_u.yuv, pic_s.chroma, pic_s.chroma, pic_s.color, pic_s.data, pic_s.data, pic_s.data, pic_s.data, pic_s.data, pic_s.data, pic_s.data, pic_s.h, pic_s.h, pic_s.h, pic_s.w, pic_s.w, pic_s.w, pic_s.w, yuv_s.u, yuv_s.u, yuv_s.u, yuv_s.v, yuv_s.v, yuv_s.v, yuv_s.y
  - AST loop count is 2; trip proofs are retained per loop

## `simple444to422`

- Source: `dsc_utils.c:344`
- Clang USR: `c:@F@simple444to422`
- Return: `void`; parameters: `ip: pic_t *`, `op: pic_t *`
- Callers: main
- Callees: exit, fprintf, pcopy_header
- Global read/write: 2/0; field read/write: 18/9
- Pointer modes: ip=UNKNOWN, op=WRITES_THROUGH
- Loops: 2; fixed counts: UNKNOWN
- Effects: `{"assert": false, "file_io": true, "indirect_call": false, "logging": false, "malloc": false}`
- Proposal: **IO_OR_DEBUG**; purity=False; combinational=False
- Classification evidence:
  - AST observed writes or mutable-state effects: ['data_u.yuv', 'op', 'pic_s.data', 'yuv_s.u', 'yuv_s.v', 'yuv_s.y']
  - AST pointer modes: ['UNKNOWN', 'WRITES_THROUGH']
  - AST observed global reads: __stderrp, __stderrp
  - AST observed field reads: data_u.yuv, data_u.yuv, data_u.yuv, pic_s.chroma, pic_s.chroma, pic_s.color, pic_s.data, pic_s.data, pic_s.data, pic_s.h, pic_s.h, pic_s.h, pic_s.w, pic_s.w, pic_s.w, yuv_s.u, yuv_s.v, yuv_s.y
  - AST loop count is 2; trip proofs are retained per loop

## `split_base_and_ext`

- Source: `codec_main.c:481`
- Clang USR: `c:@F@split_base_and_ext`
- Return: `void`; parameters: `infname: char *`, `base_name: char *`, `extension: char **`
- Callers: main
- Callees: __builtin___strcpy_chk, __builtin_object_size, exit, printf, strlen
- Global read/write: 0/0; field read/write: 0/0
- Pointer modes: infname=READ_ONLY, base_name=WRITES_THROUGH, extension=WRITES_THROUGH
- Loops: 1; fixed counts: UNKNOWN
- Effects: `{"assert": false, "file_io": false, "indirect_call": false, "logging": true, "malloc": false}`
- Proposal: **IO_OR_DEBUG**; purity=False; combinational=False
- Classification evidence:
  - AST observed writes or mutable-state effects: ['base_name', 'extension']
  - AST pointer modes: ['READ_ONLY', 'WRITES_THROUGH', 'WRITES_THROUGH']
  - AST loop count is 1; trip proofs are retained per loop

## `splitstring`

- Source: `cmd_parse.c:392`
- Clang USR: `c:@F@splitstring`
- Return: `char *`; parameters: `in: char *`, `sep: char *`
- Callers: str2dvect, str2fvect, str2ivect, str2llvect, str2lvect, str2pvect, str2uivect, str2ullvect, str2ulvect
- Callees: strcspn, strspn
- Global read/write: 0/0; field read/write: 0/0
- Pointer modes: in=WRITES_THROUGH, sep=READ_ONLY
- Loops: 0; fixed counts: UNKNOWN
- Effects: `{"assert": false, "file_io": false, "indirect_call": false, "logging": false, "malloc": false}`
- Proposal: **STATEFUL**; purity=False; combinational=False
- Classification evidence:
  - AST observed writes or mutable-state effects: ['in']
  - AST pointer modes: ['READ_ONLY', 'WRITES_THROUGH']
  - AST observed no loop

## `splitstring_exact`

- Source: `cmd_parse.c:416`
- Clang USR: `c:@F@splitstring_exact`
- Return: `char *`; parameters: `in: char *`, `substr: char *`
- Callers: splitstring_exact_strict
- Callees: strlen, strstr
- Global read/write: 0/0; field read/write: 0/0
- Pointer modes: in=READ_ONLY, substr=READ_ONLY
- Loops: 0; fixed counts: UNKNOWN
- Effects: `{"assert": false, "file_io": false, "indirect_call": false, "logging": false, "malloc": false}`
- Proposal: **COMPOSITE_COMB_CANDIDATE**; purity=False; combinational=True
- Classification evidence:
  - AST observed no global/field/pointee writes
  - AST pointer modes: ['READ_ONLY', 'READ_ONLY']
  - AST observed no loop

## `splitstring_exact_strict`

- Source: `cmd_parse.c:438`
- Clang USR: `c:@F@splitstring_exact_strict`
- Return: `char *`; parameters: `in: char *`, `substr: char *`, `arg: const char *`
- Callers: str2dim, str2fdim, str2frange, str2pdim, str2prange, str2range
- Callees: UErr, splitstring_exact
- Global read/write: 0/0; field read/write: 0/0
- Pointer modes: in=UNKNOWN, substr=UNKNOWN, arg=UNKNOWN
- Loops: 0; fixed counts: UNKNOWN
- Effects: `{"assert": false, "file_io": false, "indirect_call": false, "logging": true, "malloc": false}`
- Proposal: **IO_OR_DEBUG**; purity=False; combinational=False
- Classification evidence:
  - AST observed no global/field/pointee writes
  - AST pointer modes: ['UNKNOWN', 'UNKNOWN', 'UNKNOWN']
  - AST observed no loop

## `str2d`

- Source: `cmd_parse.c:564`
- Clang USR: `c:@F@str2d`
- Return: `double`; parameters: `arg: char *`, `title: const char *`
- Callers: str2dvect, str2f, assign_val
- Callees: Err, strtod
- Global read/write: 0/0; field read/write: 0/0
- Pointer modes: arg=UNKNOWN, title=UNKNOWN
- Loops: 0; fixed counts: UNKNOWN
- Effects: `{"assert": false, "file_io": false, "indirect_call": false, "logging": false, "malloc": false}`
- Proposal: **COMPOSITE_COMB_CANDIDATE**; purity=False; combinational=True
- Classification evidence:
  - AST observed no global/field/pointee writes
  - AST pointer modes: ['UNKNOWN', 'UNKNOWN']
  - AST observed no loop

## `str2dim`

- Source: `cmd_parse.c:612`
- Clang USR: `c:@F@str2dim`
- Return: `void`; parameters: `arg: char *`, `title: const char *`, `sep: char`, `result: xy_dim_t *`
- Callers: assign_val
- Callees: lower_case, splitstring_exact_strict, str2i
- Global read/write: 0/0; field read/write: 0/2
- Pointer modes: arg=UNKNOWN, title=READ_ONLY, result=WRITES_THROUGH
- Loops: 0; fixed counts: UNKNOWN
- Effects: `{"assert": false, "file_io": false, "indirect_call": false, "logging": false, "malloc": false}`
- Proposal: **STATEFUL**; purity=False; combinational=False
- Classification evidence:
  - AST observed writes or mutable-state effects: ['result', 'xy_dim_s.x', 'xy_dim_s.y']
  - AST pointer modes: ['READ_ONLY', 'UNKNOWN', 'WRITES_THROUGH']
  - AST observed no loop

## `str2dvect`

- Source: `cmd_parse.c:780`
- Clang USR: `c:@F@str2dvect`
- Return: `void`; parameters: `arg: char *`, `title: const char *`, `result: double *`, `vlng: int`
- Callers: assign_val
- Callees: UErr, splitstring, str2d
- Global read/write: 0/0; field read/write: 0/0
- Pointer modes: arg=WRITES_THROUGH, title=UNKNOWN, result=WRITES_THROUGH
- Loops: 1; fixed counts: UNKNOWN
- Effects: `{"assert": false, "file_io": false, "indirect_call": false, "logging": true, "malloc": false}`
- Proposal: **IO_OR_DEBUG**; purity=False; combinational=False
- Classification evidence:
  - AST observed writes or mutable-state effects: ['arg', 'result']
  - AST pointer modes: ['UNKNOWN', 'WRITES_THROUGH', 'WRITES_THROUGH']
  - AST loop count is 1; trip proofs are retained per loop

## `str2f`

- Source: `cmd_parse.c:557`
- Clang USR: `c:@F@str2f`
- Return: `float`; parameters: `arg: char *`, `title: const char *`
- Callers: str2fdim, str2frange, str2fvect, assign_val
- Callees: str2d
- Global read/write: 0/0; field read/write: 0/0
- Pointer modes: arg=UNKNOWN, title=READ_ONLY
- Loops: 0; fixed counts: UNKNOWN
- Effects: `{"assert": false, "file_io": false, "indirect_call": false, "logging": false, "malloc": false}`
- Proposal: **COMPOSITE_COMB_CANDIDATE**; purity=False; combinational=True
- Classification evidence:
  - AST observed no global/field/pointee writes
  - AST pointer modes: ['READ_ONLY', 'UNKNOWN']
  - AST observed no loop

## `str2fdim`

- Source: `cmd_parse.c:620`
- Clang USR: `c:@F@str2fdim`
- Return: `void`; parameters: `arg: char *`, `title: const char *`, `sep: char`, `result: fxy_dim_t *`
- Callers: assign_val
- Callees: lower_case, splitstring_exact_strict, str2f
- Global read/write: 0/0; field read/write: 0/2
- Pointer modes: arg=UNKNOWN, title=READ_ONLY, result=WRITES_THROUGH
- Loops: 0; fixed counts: UNKNOWN
- Effects: `{"assert": false, "file_io": false, "indirect_call": false, "logging": false, "malloc": false}`
- Proposal: **STATEFUL**; purity=False; combinational=False
- Classification evidence:
  - AST observed writes or mutable-state effects: ['fxy_dim_s.x', 'fxy_dim_s.y', 'result']
  - AST pointer modes: ['READ_ONLY', 'UNKNOWN', 'WRITES_THROUGH']
  - AST observed no loop

## `str2frange`

- Source: `cmd_parse.c:596`
- Clang USR: `c:@F@str2frange`
- Return: `void`; parameters: `arg: char *`, `title: const char *`, `result: frange_t *`
- Callers: assign_val
- Callees: splitstring_exact_strict, str2f
- Global read/write: 0/0; field read/write: 0/2
- Pointer modes: arg=UNKNOWN, title=READ_ONLY, result=WRITES_THROUGH
- Loops: 0; fixed counts: UNKNOWN
- Effects: `{"assert": false, "file_io": false, "indirect_call": false, "logging": false, "malloc": false}`
- Proposal: **STATEFUL**; purity=False; combinational=False
- Classification evidence:
  - AST observed writes or mutable-state effects: ['frange_s.end', 'frange_s.start', 'result']
  - AST pointer modes: ['READ_ONLY', 'UNKNOWN', 'WRITES_THROUGH']
  - AST observed no loop

## `str2fvect`

- Source: `cmd_parse.c:761`
- Clang USR: `c:@F@str2fvect`
- Return: `void`; parameters: `arg: char *`, `title: const char *`, `result: float *`, `vlng: int`
- Callers: assign_val
- Callees: UErr, splitstring, str2f
- Global read/write: 0/0; field read/write: 0/0
- Pointer modes: arg=WRITES_THROUGH, title=UNKNOWN, result=WRITES_THROUGH
- Loops: 1; fixed counts: UNKNOWN
- Effects: `{"assert": false, "file_io": false, "indirect_call": false, "logging": true, "malloc": false}`
- Proposal: **IO_OR_DEBUG**; purity=False; combinational=False
- Classification evidence:
  - AST observed writes or mutable-state effects: ['arg', 'result']
  - AST pointer modes: ['UNKNOWN', 'WRITES_THROUGH', 'WRITES_THROUGH']
  - AST loop count is 1; trip proofs are retained per loop

## `str2i`

- Source: `cmd_parse.c:451`
- Clang USR: `c:@F@str2i`
- Return: `int`; parameters: `arg: char *`, `title: const char *`
- Callers: str2dim, str2ivect, str2range, assign_val
- Callees: Err, str2l
- Global read/write: 0/0; field read/write: 0/0
- Pointer modes: arg=UNKNOWN, title=UNKNOWN
- Loops: 0; fixed counts: UNKNOWN
- Effects: `{"assert": false, "file_io": false, "indirect_call": false, "logging": false, "malloc": false}`
- Proposal: **COMPOSITE_COMB_CANDIDATE**; purity=False; combinational=True
- Classification evidence:
  - AST observed no global/field/pointee writes
  - AST pointer modes: ['UNKNOWN', 'UNKNOWN']
  - AST observed no loop

## `str2ivect`

- Source: `cmd_parse.c:628`
- Clang USR: `c:@F@str2ivect`
- Return: `void`; parameters: `arg: char *`, `title: const char *`, `result: int *`, `vlng: int`
- Callers: assign_val
- Callees: UErr, splitstring, str2i
- Global read/write: 0/0; field read/write: 0/0
- Pointer modes: arg=WRITES_THROUGH, title=UNKNOWN, result=WRITES_THROUGH
- Loops: 1; fixed counts: UNKNOWN
- Effects: `{"assert": false, "file_io": false, "indirect_call": false, "logging": true, "malloc": false}`
- Proposal: **IO_OR_DEBUG**; purity=False; combinational=False
- Classification evidence:
  - AST observed writes or mutable-state effects: ['arg', 'result']
  - AST pointer modes: ['UNKNOWN', 'WRITES_THROUGH', 'WRITES_THROUGH']
  - AST loop count is 1; trip proofs are retained per loop

## `str2l`

- Source: `cmd_parse.c:481`
- Clang USR: `c:@F@str2l`
- Return: `long`; parameters: `arg: char *`, `title: const char *`
- Callers: str2i, str2lvect, str2p, assign_val
- Callees: str2ll
- Global read/write: 0/0; field read/write: 0/0
- Pointer modes: arg=UNKNOWN, title=READ_ONLY
- Loops: 0; fixed counts: UNKNOWN
- Effects: `{"assert": false, "file_io": false, "indirect_call": false, "logging": false, "malloc": false}`
- Proposal: **COMPOSITE_COMB_CANDIDATE**; purity=False; combinational=True
- Classification evidence:
  - AST observed no global/field/pointee writes
  - AST pointer modes: ['READ_ONLY', 'UNKNOWN']
  - AST observed no loop

## `str2ll`

- Source: `cmd_parse.c:494`
- Clang USR: `c:@F@str2ll`
- Return: `long long`; parameters: `arg: char *`, `title: const char *`
- Callers: str2l, str2llvect, assign_val
- Callees: Err, __error, strtoll
- Global read/write: 0/0; field read/write: 0/0
- Pointer modes: arg=UNKNOWN, title=UNKNOWN
- Loops: 0; fixed counts: UNKNOWN
- Effects: `{"assert": false, "file_io": false, "indirect_call": false, "logging": false, "malloc": false}`
- Proposal: **COMPOSITE_COMB_CANDIDATE**; purity=False; combinational=True
- Classification evidence:
  - AST observed no global/field/pointee writes
  - AST pointer modes: ['UNKNOWN', 'UNKNOWN']
  - AST observed no loop

## `str2llvect`

- Source: `cmd_parse.c:723`
- Clang USR: `c:@F@str2llvect`
- Return: `void`; parameters: `arg: char *`, `title: const char *`, `result: long long *`, `vlng: int`
- Callers: assign_val
- Callees: UErr, splitstring, str2ll
- Global read/write: 0/0; field read/write: 0/0
- Pointer modes: arg=WRITES_THROUGH, title=UNKNOWN, result=WRITES_THROUGH
- Loops: 1; fixed counts: UNKNOWN
- Effects: `{"assert": false, "file_io": false, "indirect_call": false, "logging": true, "malloc": false}`
- Proposal: **IO_OR_DEBUG**; purity=False; combinational=False
- Classification evidence:
  - AST observed writes or mutable-state effects: ['arg', 'result']
  - AST pointer modes: ['UNKNOWN', 'WRITES_THROUGH', 'WRITES_THROUGH']
  - AST loop count is 1; trip proofs are retained per loop

## `str2lvect`

- Source: `cmd_parse.c:685`
- Clang USR: `c:@F@str2lvect`
- Return: `void`; parameters: `arg: char *`, `title: const char *`, `result: long *`, `vlng: int`
- Callers: assign_val
- Callees: UErr, splitstring, str2l
- Global read/write: 0/0; field read/write: 0/0
- Pointer modes: arg=WRITES_THROUGH, title=UNKNOWN, result=WRITES_THROUGH
- Loops: 1; fixed counts: UNKNOWN
- Effects: `{"assert": false, "file_io": false, "indirect_call": false, "logging": true, "malloc": false}`
- Proposal: **IO_OR_DEBUG**; purity=False; combinational=False
- Classification evidence:
  - AST observed writes or mutable-state effects: ['arg', 'result']
  - AST pointer modes: ['UNKNOWN', 'WRITES_THROUGH', 'WRITES_THROUGH']
  - AST loop count is 1; trip proofs are retained per loop

## `str2p`

- Source: `cmd_parse.c:464`
- Clang USR: `c:@F@str2p`
- Return: `int`; parameters: `arg: char *`, `title: const char *`
- Callers: str2pdim, str2prange, str2pvect, assign_val
- Callees: Err, str2l
- Global read/write: 0/0; field read/write: 0/0
- Pointer modes: arg=UNKNOWN, title=UNKNOWN
- Loops: 0; fixed counts: UNKNOWN
- Effects: `{"assert": false, "file_io": false, "indirect_call": false, "logging": false, "malloc": false}`
- Proposal: **COMPOSITE_COMB_CANDIDATE**; purity=False; combinational=True
- Classification evidence:
  - AST observed no global/field/pointee writes
  - AST pointer modes: ['UNKNOWN', 'UNKNOWN']
  - AST observed no loop

## `str2pdim`

- Source: `cmd_parse.c:604`
- Clang USR: `c:@F@str2pdim`
- Return: `void`; parameters: `arg: char *`, `title: const char *`, `sep: char`, `result: xy_dim_t *`
- Callers: assign_val
- Callees: lower_case, splitstring_exact_strict, str2p
- Global read/write: 0/0; field read/write: 0/2
- Pointer modes: arg=UNKNOWN, title=READ_ONLY, result=WRITES_THROUGH
- Loops: 0; fixed counts: UNKNOWN
- Effects: `{"assert": false, "file_io": false, "indirect_call": false, "logging": false, "malloc": false}`
- Proposal: **STATEFUL**; purity=False; combinational=False
- Classification evidence:
  - AST observed writes or mutable-state effects: ['result', 'xy_dim_s.x', 'xy_dim_s.y']
  - AST pointer modes: ['READ_ONLY', 'UNKNOWN', 'WRITES_THROUGH']
  - AST observed no loop

## `str2prange`

- Source: `cmd_parse.c:580`
- Clang USR: `c:@F@str2prange`
- Return: `void`; parameters: `arg: char *`, `title: const char *`, `result: range_t *`
- Callers: assign_val
- Callees: splitstring_exact_strict, str2p
- Global read/write: 0/0; field read/write: 0/2
- Pointer modes: arg=UNKNOWN, title=READ_ONLY, result=WRITES_THROUGH
- Loops: 0; fixed counts: UNKNOWN
- Effects: `{"assert": false, "file_io": false, "indirect_call": false, "logging": false, "malloc": false}`
- Proposal: **STATEFUL**; purity=False; combinational=False
- Classification evidence:
  - AST observed writes or mutable-state effects: ['range_s.end', 'range_s.start', 'result']
  - AST pointer modes: ['READ_ONLY', 'UNKNOWN', 'WRITES_THROUGH']
  - AST observed no loop

## `str2pvect`

- Source: `cmd_parse.c:647`
- Clang USR: `c:@F@str2pvect`
- Return: `void`; parameters: `arg: char *`, `title: const char *`, `result: int *`, `vlng: int`
- Callers: assign_val
- Callees: UErr, splitstring, str2p
- Global read/write: 0/0; field read/write: 0/0
- Pointer modes: arg=WRITES_THROUGH, title=UNKNOWN, result=WRITES_THROUGH
- Loops: 1; fixed counts: UNKNOWN
- Effects: `{"assert": false, "file_io": false, "indirect_call": false, "logging": true, "malloc": false}`
- Proposal: **IO_OR_DEBUG**; purity=False; combinational=False
- Classification evidence:
  - AST observed writes or mutable-state effects: ['arg', 'result']
  - AST pointer modes: ['UNKNOWN', 'WRITES_THROUGH', 'WRITES_THROUGH']
  - AST loop count is 1; trip proofs are retained per loop

## `str2range`

- Source: `cmd_parse.c:588`
- Clang USR: `c:@F@str2range`
- Return: `void`; parameters: `arg: char *`, `title: const char *`, `result: range_t *`
- Callers: assign_val
- Callees: splitstring_exact_strict, str2i
- Global read/write: 0/0; field read/write: 0/2
- Pointer modes: arg=UNKNOWN, title=READ_ONLY, result=WRITES_THROUGH
- Loops: 0; fixed counts: UNKNOWN
- Effects: `{"assert": false, "file_io": false, "indirect_call": false, "logging": false, "malloc": false}`
- Proposal: **STATEFUL**; purity=False; combinational=False
- Classification evidence:
  - AST observed writes or mutable-state effects: ['range_s.end', 'range_s.start', 'result']
  - AST pointer modes: ['READ_ONLY', 'UNKNOWN', 'WRITES_THROUGH']
  - AST observed no loop

## `str2ui`

- Source: `cmd_parse.c:512`
- Clang USR: `c:@F@str2ui`
- Return: `unsigned int`; parameters: `arg: char *`, `title: const char *`
- Callers: str2uivect, assign_val
- Callees: Err, str2ul
- Global read/write: 0/0; field read/write: 0/0
- Pointer modes: arg=UNKNOWN, title=UNKNOWN
- Loops: 0; fixed counts: UNKNOWN
- Effects: `{"assert": false, "file_io": false, "indirect_call": false, "logging": false, "malloc": false}`
- Proposal: **COMPOSITE_COMB_CANDIDATE**; purity=False; combinational=True
- Classification evidence:
  - AST observed no global/field/pointee writes
  - AST pointer modes: ['UNKNOWN', 'UNKNOWN']
  - AST observed no loop

## `str2uivect`

- Source: `cmd_parse.c:666`
- Clang USR: `c:@F@str2uivect`
- Return: `void`; parameters: `arg: char *`, `title: const char *`, `result: unsigned int *`, `vlng: int`
- Callers: assign_val
- Callees: UErr, splitstring, str2ui
- Global read/write: 0/0; field read/write: 0/0
- Pointer modes: arg=WRITES_THROUGH, title=UNKNOWN, result=WRITES_THROUGH
- Loops: 1; fixed counts: UNKNOWN
- Effects: `{"assert": false, "file_io": false, "indirect_call": false, "logging": true, "malloc": false}`
- Proposal: **IO_OR_DEBUG**; purity=False; combinational=False
- Classification evidence:
  - AST observed writes or mutable-state effects: ['arg', 'result']
  - AST pointer modes: ['UNKNOWN', 'WRITES_THROUGH', 'WRITES_THROUGH']
  - AST loop count is 1; trip proofs are retained per loop

## `str2ul`

- Source: `cmd_parse.c:525`
- Clang USR: `c:@F@str2ul`
- Return: `unsigned long`; parameters: `arg: char *`, `title: const char *`
- Callers: str2ui, str2ulvect, assign_val
- Callees: str2ull
- Global read/write: 0/0; field read/write: 0/0
- Pointer modes: arg=UNKNOWN, title=READ_ONLY
- Loops: 0; fixed counts: UNKNOWN
- Effects: `{"assert": false, "file_io": false, "indirect_call": false, "logging": false, "malloc": false}`
- Proposal: **COMPOSITE_COMB_CANDIDATE**; purity=False; combinational=True
- Classification evidence:
  - AST observed no global/field/pointee writes
  - AST pointer modes: ['READ_ONLY', 'UNKNOWN']
  - AST observed no loop

## `str2ull`

- Source: `cmd_parse.c:538`
- Clang USR: `c:@F@str2ull`
- Return: `unsigned long long`; parameters: `arg: char *`, `title: const char *`
- Callers: str2ul, str2ullvect, assign_val
- Callees: Err, __error, strtoull
- Global read/write: 0/0; field read/write: 0/0
- Pointer modes: arg=UNKNOWN, title=UNKNOWN
- Loops: 0; fixed counts: UNKNOWN
- Effects: `{"assert": false, "file_io": false, "indirect_call": false, "logging": false, "malloc": false}`
- Proposal: **COMPOSITE_COMB_CANDIDATE**; purity=False; combinational=True
- Classification evidence:
  - AST observed no global/field/pointee writes
  - AST pointer modes: ['UNKNOWN', 'UNKNOWN']
  - AST observed no loop

## `str2ullvect`

- Source: `cmd_parse.c:742`
- Clang USR: `c:@F@str2ullvect`
- Return: `void`; parameters: `arg: char *`, `title: const char *`, `result: unsigned long long *`, `vlng: int`
- Callers: assign_val
- Callees: UErr, splitstring, str2ull
- Global read/write: 0/0; field read/write: 0/0
- Pointer modes: arg=WRITES_THROUGH, title=UNKNOWN, result=WRITES_THROUGH
- Loops: 1; fixed counts: UNKNOWN
- Effects: `{"assert": false, "file_io": false, "indirect_call": false, "logging": true, "malloc": false}`
- Proposal: **IO_OR_DEBUG**; purity=False; combinational=False
- Classification evidence:
  - AST observed writes or mutable-state effects: ['arg', 'result']
  - AST pointer modes: ['UNKNOWN', 'WRITES_THROUGH', 'WRITES_THROUGH']
  - AST loop count is 1; trip proofs are retained per loop

## `str2ulvect`

- Source: `cmd_parse.c:704`
- Clang USR: `c:@F@str2ulvect`
- Return: `void`; parameters: `arg: char *`, `title: const char *`, `result: unsigned long *`, `vlng: int`
- Callers: assign_val
- Callees: UErr, splitstring, str2ul
- Global read/write: 0/0; field read/write: 0/0
- Pointer modes: arg=WRITES_THROUGH, title=UNKNOWN, result=WRITES_THROUGH
- Loops: 1; fixed counts: UNKNOWN
- Effects: `{"assert": false, "file_io": false, "indirect_call": false, "logging": true, "malloc": false}`
- Proposal: **IO_OR_DEBUG**; purity=False; combinational=False
- Classification evidence:
  - AST observed writes or mutable-state effects: ['arg', 'result']
  - AST pointer modes: ['UNKNOWN', 'WRITES_THROUGH', 'WRITES_THROUGH']
  - AST loop count is 1; trip proofs are retained per loop

## `strisdim`

- Source: `cmd_parse.c:333`
- Clang USR: `c:@F@strisdim`
- Return: `int`; parameters: `in: char *`, `sep: char`
- Callers: NONE
- Callees: isdigit, strlen
- Global read/write: 0/0; field read/write: 0/0
- Pointer modes: in=UNKNOWN
- Loops: 1; fixed counts: UNKNOWN
- Effects: `{"assert": false, "file_io": false, "indirect_call": false, "logging": false, "malloc": false}`
- Proposal: **COMPOSITE_COMB_CANDIDATE**; purity=False; combinational=True
- Classification evidence:
  - AST observed no global/field/pointee writes
  - AST pointer modes: ['UNKNOWN']
  - AST loop count is 1; trip proofs are retained per loop

## `strisnum`

- Source: `cmd_parse.c:273`
- Clang USR: `c:@F@strisnum`
- Return: `int`; parameters: `in: char *`
- Callers: NONE
- Callees: isdigit, strlen
- Global read/write: 0/0; field read/write: 0/0
- Pointer modes: in=UNKNOWN
- Loops: 1; fixed counts: UNKNOWN
- Effects: `{"assert": false, "file_io": false, "indirect_call": false, "logging": false, "malloc": false}`
- Proposal: **COMPOSITE_COMB_CANDIDATE**; purity=False; combinational=True
- Classification evidence:
  - AST observed no global/field/pointee writes
  - AST pointer modes: ['UNKNOWN']
  - AST loop count is 1; trip proofs are retained per loop

## `strisrange`

- Source: `cmd_parse.c:297`
- Clang USR: `c:@F@strisrange`
- Return: `int`; parameters: `in: char *`
- Callers: NONE
- Callees: isdigit, strlen
- Global read/write: 0/0; field read/write: 0/0
- Pointer modes: in=UNKNOWN
- Loops: 1; fixed counts: UNKNOWN
- Effects: `{"assert": false, "file_io": false, "indirect_call": false, "logging": false, "malloc": false}`
- Proposal: **COMPOSITE_COMB_CANDIDATE**; purity=False; combinational=True
- Classification evidence:
  - AST observed no global/field/pointee writes
  - AST pointer modes: ['UNKNOWN']
  - AST loop count is 1; trip proofs are retained per loop

## `test_cmd`

- Source: `cmd_parse.c:1116`
- Clang USR: `c:cmd_parse.c@F@test_cmd`
- Return: `int`; parameters: `arg: char *`, `v: char **`, `cmdarg: const cmdarg_t`, `distinguish: const int`
- Callers: parse_cmd
- Callees: NONE
- Global read/write: 0/0; field read/write: 4/0
- Pointer modes: arg=READ_ONLY, v=WRITES_THROUGH
- Loops: 1; fixed counts: UNKNOWN
- Effects: `{"assert": false, "file_io": false, "indirect_call": false, "logging": false, "malloc": false}`
- Proposal: **STATEFUL**; purity=False; combinational=False
- Classification evidence:
  - AST observed writes or mutable-state effects: ['v']
  - AST pointer modes: ['READ_ONLY', 'WRITES_THROUGH']
  - AST observed field reads: cmdarg_s.cmd, cmdarg_s.cmd, cmdarg_s.type, cmdarg_s.type
  - AST loop count is 1; trip proofs are retained per loop

## `usage`

- Source: `codec_main.c:377`
- Clang USR: `c:@F@usage`
- Return: `void`; parameters: NONE
- Callers: process_args
- Callees: exit, printf
- Global read/write: 0/0; field read/write: 0/0
- Pointer modes: NONE
- Loops: 0; fixed counts: UNKNOWN
- Effects: `{"assert": false, "file_io": false, "indirect_call": false, "logging": true, "malloc": false}`
- Proposal: **IO_OR_DEBUG**; purity=False; combinational=False
- Classification evidence:
  - AST observed no global/field/pointee writes
  - AST observed no loop

## `uyvy_read`

- Source: `utl.c:1306`
- Clang USR: `c:@F@uyvy_read`
- Return: `int`; parameters: `ip: pic_t *`, `fp: FILE *`
- Callers: yuv_read
- Callees: fclose, fgetc
- Global read/write: 0/0; field read/write: 4/36
- Pointer modes: ip=WRITES_THROUGH, fp=UNKNOWN
- Loops: 2; fixed counts: UNKNOWN
- Effects: `{"assert": false, "file_io": true, "indirect_call": false, "logging": false, "malloc": false}`
- Proposal: **IO_OR_DEBUG**; purity=False; combinational=False
- Classification evidence:
  - AST observed writes or mutable-state effects: ['data_u.yuv', 'ip', 'pic_s.data', 'yuv_s.u', 'yuv_s.v', 'yuv_s.y']
  - AST pointer modes: ['UNKNOWN', 'WRITES_THROUGH']
  - AST observed field reads: pic_s.bits, pic_s.bits, pic_s.h, pic_s.w
  - AST loop count is 2; trip proofs are retained per loop

## `uyvy_write`

- Source: `utl.c:1420`
- Clang USR: `c:@F@uyvy_write`
- Return: `int`; parameters: `op: pic_t *`, `fp: FILE *`
- Callers: yuv_write
- Callees: fclose, fputc
- Global read/write: 0/0; field read/write: 16/0
- Pointer modes: op=READ_ONLY, fp=UNKNOWN
- Loops: 2; fixed counts: UNKNOWN
- Effects: `{"assert": false, "file_io": true, "indirect_call": false, "logging": false, "malloc": false}`
- Proposal: **IO_OR_DEBUG**; purity=False; combinational=False
- Classification evidence:
  - AST observed no global/field/pointee writes
  - AST pointer modes: ['READ_ONLY', 'UNKNOWN']
  - AST observed field reads: data_u.yuv, data_u.yuv, data_u.yuv, data_u.yuv, pic_s.bits, pic_s.bits, pic_s.data, pic_s.data, pic_s.data, pic_s.data, pic_s.h, pic_s.w, yuv_s.u, yuv_s.v, yuv_s.y, yuv_s.y
  - AST loop count is 2; trip proofs are retained per loop

## `write_dpx`

- Source: `dpx.c:230`
- Clang USR: `c:@F@write_dpx`
- Return: `int`; parameters: `fname: char *`, `p: pic_t *`, `ar1: int`, `ar2: int`, `frameno: int`, `seqlen: int`, `framerate: float`, `interlaced: int`, `bpp: int`, `pad_ends: int`, `datum_order: int`, `force_packing: int`, `swaprb: int`, `wbswap: int`
- Callers: NONE
- Callees: write_dpx_ver
- Global read/write: 0/0; field read/write: 0/0
- Pointer modes: fname=UNKNOWN, p=UNKNOWN
- Loops: 0; fixed counts: UNKNOWN
- Effects: `{"assert": false, "file_io": false, "indirect_call": false, "logging": false, "malloc": false}`
- Proposal: **COMPOSITE_COMB_CANDIDATE**; purity=False; combinational=True
- Classification evidence:
  - AST observed no global/field/pointee writes
  - AST pointer modes: ['UNKNOWN', 'UNKNOWN']
  - AST observed no loop

## `write_dpx_ver`

- Source: `dpx.c:235`
- Clang USR: `c:@F@write_dpx_ver`
- Return: `int`; parameters: `fname: char *`, `p: pic_t *`, `ar1: int`, `ar2: int`, `frameno: int`, `seqlen: int`, `framerate: float`, `interlaced: int`, `bpp: int`, `ver: int`, `pad_ends: int`, `datum_order: int`, `force_packing: int`, `swaprb: int`, `wbswap: int`
- Callers: dpx_write, write_dpx
- Callees: __builtin___memset_chk, __builtin___snprintf_chk, __builtin___sprintf_chk, __builtin_object_size, exit, fclose, fifo_flip_put_bits, fifo_get_bits, fifo_init, fifo_put_bits, fopen, fprintf, fseek, ftell, fwrite, generate_timecode
- Global read/write: 3/0; field read/write: 156/180
- Pointer modes: fname=UNKNOWN, p=READ_ONLY
- Loops: 6; fixed counts: 7
- Effects: `{"assert": false, "file_io": true, "indirect_call": false, "logging": true, "malloc": false}`
- Proposal: **IO_OR_DEBUG**; purity=False; combinational=False
- Classification evidence:
  - AST observed writes or mutable-state effects: ['ANONYMOUS.ui', '_DpxFileFormat.FileHeader', '_DpxFileFormat.FilmHeader', '_DpxFileFormat.ImageHeader', '_DpxFileFormat.OrientHeader', '_DpxFileFormat.TvHeader', '_GenericFileHeader.DittoKey', '_GenericFileHeader.EncryptKey', '_GenericFileHeader.FileSize', '_GenericFileHeader.GenericSize', '_GenericFileHeader.ImageOffset', '_GenericFileHeader.IndustrySize', '_GenericFileHeader.Magic', '_GenericFileHeader.UserSize', '_GenericImageHeader.ImageElement', '_GenericImageHeader.LinesPerElement', '_GenericImageHeader.NumberElements', '_GenericImageHeader.Orientation', '_GenericImageHeader.PixelsPerLine', '_GenericOrientationHeader.AspectRatio', '_GenericOrientationHeader.Border', '_GenericOrientationHeader.XCenter', '_GenericOrientationHeader.XOffset', '_GenericOrientationHeader.XOriginalSize', '_GenericOrientationHeader.YCenter', '_GenericOrientationHeader.YOffset', '_GenericOrientationHeader.YOriginalSize', '_ImageElement.BitSize', '_ImageElement.Colorimetric', '_ImageElement.DataOffset', '_ImageElement.DataSign', '_ImageElement.Descriptor', '_ImageElement.Encoding', '_ImageElement.EndOfImagePadding', '_ImageElement.EndOfLinePadding', '_ImageElement.HighData', '_ImageElement.HighQuantity', '_ImageElement.LowData', '_ImageElement.LowQuantity', '_ImageElement.Packing', '_ImageElement.Transfer', '_IndustryFilmInfoHeader.FramePosition', '_IndustryFilmInfoHeader.FrameRate', '_IndustryFilmInfoHeader.HeldCount', '_IndustryFilmInfoHeader.SequenceLen', '_IndustryFilmInfoHeader.ShutterAngle', '_IndustryTelevisionInfoHeader.BlackGain', '_IndustryTelevisionInfoHeader.BlackLevel', '_IndustryTelevisionInfoHeader.Breakpoint', '_IndustryTelevisionInfoHeader.FieldNumber', '_IndustryTelevisionInfoHeader.FrameRate', '_IndustryTelevisionInfoHeader.Gamma', '_IndustryTelevisionInfoHeader.HorzSampleRate', '_IndustryTelevisionInfoHeader.IntegrationTimes', '_IndustryTelevisionInfoHeader.Interlace', '_IndustryTelevisionInfoHeader.TimeCode', '_IndustryTelevisionInfoHeader.TimeOffset', '_IndustryTelevisionInfoHeader.UserBits', '_IndustryTelevisionInfoHeader.VertSampleRate', '_IndustryTelevisionInfoHeader.VideoSignal', '_IndustryTelevisionInfoHeader.WhiteLevel', 'dpxcolor']
  - AST pointer modes: ['READ_ONLY', 'UNKNOWN']
  - AST observed global reads: __stderrp, dpxcolor, dpxcolor
  - AST observed field reads: ANONYMOUS.c, _DpxFileFormat.FileHeader, _DpxFileFormat.FileHeader, _DpxFileFormat.FileHeader, _DpxFileFormat.FileHeader, _DpxFileFormat.FileHeader, _DpxFileFormat.FileHeader, _DpxFileFormat.FileHeader, _DpxFileFormat.FilmHeader, _DpxFileFormat.FilmHeader, _DpxFileFormat.FilmHeader, _DpxFileFormat.FilmHeader, _DpxFileFormat.ImageHeader, _DpxFileFormat.ImageHeader, _DpxFileFormat.OrientHeader, _DpxFileFormat.OrientHeader, _DpxFileFormat.OrientHeader, _DpxFileFormat.OrientHeader, _GenericFileHeader.Copyright, _GenericFileHeader.Creator, _GenericFileHeader.FileName, _GenericFileHeader.Project, _GenericFileHeader.Project, _GenericFileHeader.TimeDate, _GenericFileHeader.Version, _GenericImageHeader.ImageElement, _GenericImageHeader.ImageElement, _GenericOrientationHeader.FileName, _GenericOrientationHeader.InputName, _GenericOrientationHeader.InputSN, _GenericOrientationHeader.TimeDate, _ImageElement.Description, _IndustryFilmInfoHeader.Format, _IndustryFilmInfoHeader.FrameId, _IndustryFilmInfoHeader.SlateInfo, data_u.rgb, data_u.rgb, data_u.rgb, data_u.rgb, data_u.rgb, data_u.rgb, data_u.rgb, data_u.yuv, data_u.yuv, data_u.yuv, data_u.yuv, data_u.yuv, data_u.yuv, data_u.yuv, data_u.yuv, data_u.yuv, data_u.yuv, data_u.yuv, data_u.yuv, data_u.yuv, data_u.yuv, data_u.yuv, data_u.yuv, data_u.yuv, fifo_s.fullness, fifo_s.fullness, fifo_s.fullness, fifo_s.fullness, fifo_s.fullness, fifo_s.fullness, fifo_s.fullness, pic_s.alpha, pic_s.alpha, pic_s.alpha, pic_s.alpha, pic_s.alpha, pic_s.alpha, pic_s.chroma, pic_s.chroma, pic_s.chroma, pic_s.chroma, pic_s.chroma, pic_s.chroma, pic_s.color, pic_s.color, pic_s.color, pic_s.color, pic_s.color, pic_s.data, pic_s.data, pic_s.data, pic_s.data, pic_s.data, pic_s.data, pic_s.data, pic_s.data, pic_s.data, pic_s.data, pic_s.data, pic_s.data, pic_s.data, pic_s.data, pic_s.data, pic_s.data, pic_s.data, pic_s.data, pic_s.data, pic_s.data, pic_s.data, pic_s.data, pic_s.data, pic_s.data, pic_s.h, pic_s.h, pic_s.h, pic_s.h, pic_s.h, pic_s.h, pic_s.h, pic_s.h, pic_s.h, pic_s.h, pic_s.h, pic_s.h, pic_s.h, pic_s.h, pic_s.h, pic_s.h, pic_s.w, pic_s.w, pic_s.w, pic_s.w, pic_s.w, pic_s.w, pic_s.w, pic_s.w, pic_s.w, rgb_s.a, rgb_s.b, rgb_s.b, rgb_s.g, rgb_s.g, rgb_s.r, rgb_s.r, yuv_s.a, yuv_s.a, yuv_s.a, yuv_s.u, yuv_s.u, yuv_s.u, yuv_s.u, yuv_s.v, yuv_s.v, yuv_s.v, yuv_s.v, yuv_s.y, yuv_s.y, yuv_s.y, yuv_s.y, yuv_s.y, yuv_s.y
  - AST loop count is 6; trip proofs are retained per loop

## `write_dsc_data`

- Source: `codec_main.c:521`
- Clang USR: `c:@F@write_dsc_data`
- Return: `void`; parameters: `bit_buffer: unsigned char **`, `nbytes: int`, `fp: FILE *`, `vbr_enable: int`, `slices_per_line: int`, `slice_height: int`, `sizes: int **`
- Callers: main
- Callees: fputc, free, malloc
- Global read/write: 0/0; field read/write: 0/0
- Pointer modes: bit_buffer=UNKNOWN, fp=UNKNOWN, sizes=READ_ONLY
- Loops: 4; fixed counts: UNKNOWN
- Effects: `{"assert": false, "file_io": false, "indirect_call": false, "logging": false, "malloc": true}`
- Proposal: **IO_OR_DEBUG**; purity=False; combinational=False
- Classification evidence:
  - AST observed no global/field/pointee writes
  - AST pointer modes: ['READ_ONLY', 'UNKNOWN', 'UNKNOWN']
  - AST loop count is 4; trip proofs are retained per loop

## `write_pps`

- Source: `dsc_utils.c:514`
- Clang USR: `c:@F@write_pps`
- Return: `void`; parameters: `buf: unsigned char *`, `dsc_cfg: dsc_cfg_t *`
- Callers: main, print_pps_v2
- Callees: putbits
- Global read/write: 0/0; field read/write: 45/0
- Pointer modes: buf=UNKNOWN, dsc_cfg=UNKNOWN
- Loops: 2; fixed counts: 14, 15
- Effects: `{"assert": false, "file_io": false, "indirect_call": false, "logging": false, "malloc": false}`
- Proposal: **CONFIG_HELPER**; purity=False; combinational=True
- Classification evidence:
  - AST observed no global/field/pointee writes
  - AST pointer modes: ['UNKNOWN', 'UNKNOWN']
  - AST observed field reads: dsc_cfg_t.bits_per_component, dsc_cfg_t.bits_per_pixel, dsc_cfg_t.block_pred_enable, dsc_cfg_t.chunk_size, dsc_cfg_t.convert_rgb, dsc_cfg_t.dsc_version_minor, dsc_cfg_t.dsc_version_minor, dsc_cfg_t.final_offset, dsc_cfg_t.first_line_bpg_ofs, dsc_cfg_t.flatness_max_qp, dsc_cfg_t.flatness_min_qp, dsc_cfg_t.initial_dec_delay, dsc_cfg_t.initial_offset, dsc_cfg_t.initial_scale_value, dsc_cfg_t.initial_xmit_delay, dsc_cfg_t.linebuf_depth, dsc_cfg_t.native_420, dsc_cfg_t.native_422, dsc_cfg_t.nfl_bpg_offset, dsc_cfg_t.nsl_bpg_offset, dsc_cfg_t.pic_height, dsc_cfg_t.pic_width, dsc_cfg_t.pps_identifier, dsc_cfg_t.rc_buf_thresh, dsc_cfg_t.rc_edge_factor, dsc_cfg_t.rc_model_size, dsc_cfg_t.rc_quant_incr_limit0, dsc_cfg_t.rc_quant_incr_limit1, dsc_cfg_t.rc_range_parameters, dsc_cfg_t.rc_range_parameters, dsc_cfg_t.rc_range_parameters, dsc_cfg_t.rc_tgt_offset_hi, dsc_cfg_t.rc_tgt_offset_lo, dsc_cfg_t.scale_decrement_interval, dsc_cfg_t.scale_increment_interval, dsc_cfg_t.second_line_bpg_ofs, dsc_cfg_t.second_line_ofs_adj, dsc_cfg_t.simple_422, dsc_cfg_t.slice_bpg_offset, dsc_cfg_t.slice_height, dsc_cfg_t.slice_width, dsc_cfg_t.vbr_enable, dsc_range_cfg_t.range_bpg_offset, dsc_range_cfg_t.range_max_qp, dsc_range_cfg_t.range_min_qp
  - AST loop count is 2; trip proofs are retained per loop
  - The proposal is per-field input use; the containing struct is not classified as static configuration

## `writeppm`

- Source: `utl.c:1222`
- Clang USR: `c:@F@writeppm`
- Return: `void`; parameters: `fp: FILE *`, `p: pic_t *`
- Callers: ppm_write
- Callees: fprintf, fputc
- Global read/write: 0/0; field read/write: 26/0
- Pointer modes: fp=UNKNOWN, p=UNKNOWN
- Loops: 2; fixed counts: UNKNOWN
- Effects: `{"assert": false, "file_io": true, "indirect_call": false, "logging": false, "malloc": false}`
- Proposal: **IO_OR_DEBUG**; purity=False; combinational=False
- Classification evidence:
  - AST observed no global/field/pointee writes
  - AST pointer modes: ['UNKNOWN', 'UNKNOWN']
  - AST observed field reads: data_u.rgb, data_u.rgb, data_u.rgb, data_u.rgb, data_u.rgb, data_u.rgb, pic_s.bits, pic_s.bits, pic_s.bits, pic_s.bits, pic_s.data, pic_s.data, pic_s.data, pic_s.data, pic_s.data, pic_s.data, pic_s.h, pic_s.h, pic_s.w, pic_s.w, rgb_s.b, rgb_s.b, rgb_s.g, rgb_s.g, rgb_s.r, rgb_s.r
  - AST loop count is 2; trip proofs are retained per loop

## `ycocg2rgb`

- Source: `dsc_utils.c:225`
- Clang USR: `c:@F@ycocg2rgb`
- Return: `void`; parameters: `ip: pic_t *`, `op: pic_t *`, `dsc_cfg: dsc_cfg_t *`
- Callers: DSC_Algorithm
- Callees: exit, fprintf
- Global read/write: 5/0; field read/write: 35/9
- Pointer modes: ip=READ_ONLY, op=WRITES_THROUGH, dsc_cfg=READ_ONLY
- Loops: 2; fixed counts: UNKNOWN
- Effects: `{"assert": false, "file_io": true, "indirect_call": false, "logging": false, "malloc": false}`
- Proposal: **IO_OR_DEBUG**; purity=False; combinational=False
- Classification evidence:
  - AST observed writes or mutable-state effects: ['data_u.rgb', 'op', 'pic_s.data', 'rgb_s.b', 'rgb_s.g', 'rgb_s.r']
  - AST pointer modes: ['READ_ONLY', 'READ_ONLY', 'WRITES_THROUGH']
  - AST observed global reads: __stderrp, __stderrp, __stderrp, __stderrp, __stderrp
  - AST observed field reads: data_u.yuv, data_u.yuv, data_u.yuv, data_u.yuv, data_u.yuv, dsc_cfg_t.slice_height, dsc_cfg_t.slice_width, dsc_cfg_t.xstart, dsc_cfg_t.xstart, dsc_cfg_t.ystart, dsc_cfg_t.ystart, pic_s.bits, pic_s.bits, pic_s.bits, pic_s.chroma, pic_s.chroma, pic_s.color, pic_s.color, pic_s.color, pic_s.data, pic_s.data, pic_s.data, pic_s.data, pic_s.data, pic_s.h, pic_s.h, pic_s.h, pic_s.w, pic_s.w, pic_s.w, yuv_s.u, yuv_s.u, yuv_s.v, yuv_s.v, yuv_s.y
  - AST loop count is 2; trip proofs are retained per loop

## `yuv2rgb`

- Source: `utl.c:389`
- Clang USR: `c:@F@yuv2rgb`
- Return: `void`; parameters: `ip: pic_t *`, `op: pic_t *`
- Callers: main, ppm_write
- Callees: exit, fprintf, pcopy_header
- Global read/write: 6/0; field read/write: 25/9
- Pointer modes: ip=UNKNOWN, op=WRITES_THROUGH
- Loops: 2; fixed counts: UNKNOWN
- Effects: `{"assert": false, "file_io": true, "indirect_call": false, "logging": false, "malloc": false}`
- Proposal: **IO_OR_DEBUG**; purity=False; combinational=False
- Classification evidence:
  - AST observed writes or mutable-state effects: ['data_u.rgb', 'op', 'pic_s.data', 'rgb_s.b', 'rgb_s.g', 'rgb_s.r']
  - AST pointer modes: ['UNKNOWN', 'WRITES_THROUGH']
  - AST observed global reads: __stderrp, __stderrp, __stderrp, __stderrp, __stderrp, __stderrp
  - AST observed field reads: data_u.yuv, data_u.yuv, data_u.yuv, pic_s.bits, pic_s.bits, pic_s.bits, pic_s.chroma, pic_s.chroma, pic_s.color, pic_s.color, pic_s.color, pic_s.color, pic_s.color, pic_s.data, pic_s.data, pic_s.data, pic_s.h, pic_s.h, pic_s.h, pic_s.w, pic_s.w, pic_s.w, yuv_s.u, yuv_s.v, yuv_s.y
  - AST loop count is 2; trip proofs are retained per loop

## `yuv_420_422`

- Source: `utl.c:671`
- Clang USR: `c:@F@yuv_420_422`
- Return: `void`; parameters: `ip: pic_t *`, `op: pic_t *`
- Callers: main, ppm_write
- Callees: pcopy_header
- Global read/write: 0/0; field read/write: 51/24
- Pointer modes: ip=UNKNOWN, op=WRITES_THROUGH
- Loops: 2; fixed counts: UNKNOWN
- Effects: `{"assert": false, "file_io": false, "indirect_call": false, "logging": false, "malloc": false}`
- Proposal: **STATEFUL**; purity=False; combinational=False
- Classification evidence:
  - AST observed writes or mutable-state effects: ['data_u.yuv', 'op', 'pic_s.data', 'yuv_s.u', 'yuv_s.v', 'yuv_s.y']
  - AST pointer modes: ['UNKNOWN', 'WRITES_THROUGH']
  - AST observed field reads: data_u.yuv, data_u.yuv, data_u.yuv, data_u.yuv, data_u.yuv, data_u.yuv, data_u.yuv, data_u.yuv, data_u.yuv, data_u.yuv, data_u.yuv, data_u.yuv, data_u.yuv, data_u.yuv, pic_s.bits, pic_s.data, pic_s.data, pic_s.data, pic_s.data, pic_s.data, pic_s.data, pic_s.data, pic_s.data, pic_s.data, pic_s.data, pic_s.data, pic_s.data, pic_s.data, pic_s.data, pic_s.h, pic_s.h, pic_s.h, pic_s.h, pic_s.h, pic_s.h, pic_s.h, pic_s.w, yuv_s.u, yuv_s.u, yuv_s.u, yuv_s.u, yuv_s.u, yuv_s.v, yuv_s.v, yuv_s.v, yuv_s.v, yuv_s.v, yuv_s.y, yuv_s.y, yuv_s.y, yuv_s.y
  - AST loop count is 2; trip proofs are retained per loop

## `yuv_422_420`

- Source: `utl.c:615`
- Clang USR: `c:@F@yuv_422_420`
- Return: `void`; parameters: `ip: pic_t *`, `op: pic_t *`
- Callers: main
- Callees: conv, exit, pcopy_header, printf
- Global read/write: 1/0; field read/write: 25/10
- Pointer modes: ip=UNKNOWN, op=WRITES_THROUGH
- Loops: 6; fixed counts: UNKNOWN
- Effects: `{"assert": false, "file_io": false, "indirect_call": false, "logging": true, "malloc": false}`
- Proposal: **IO_OR_DEBUG**; purity=False; combinational=False
- Classification evidence:
  - AST observed writes or mutable-state effects: ['data_u.yuv', 'op', 'pic_s.chroma', 'pic_s.data', 'yuv_s.u', 'yuv_s.v', 'yuv_s.y']
  - AST pointer modes: ['UNKNOWN', 'WRITES_THROUGH']
  - AST observed global reads: chm_422_420_03
  - AST observed field reads: data_u.yuv, data_u.yuv, data_u.yuv, pic_s.bits, pic_s.chroma, pic_s.data, pic_s.data, pic_s.data, pic_s.h, pic_s.h, pic_s.h, pic_s.h, pic_s.h, pic_s.h, pic_s.h, pic_s.w, pic_s.w, pic_s.w, pic_s.w, pic_s.w, pic_s.w, pic_s.w, yuv_s.u, yuv_s.v, yuv_s.y
  - AST loop count is 6; trip proofs are retained per loop

## `yuv_422_444`

- Source: `utl.c:503`
- Clang USR: `c:@F@yuv_422_444`
- Return: `void`; parameters: `ip: pic_t *`, `op: pic_t *`
- Callers: main, ppm_write
- Callees: pcopy_header
- Global read/write: 0/0; field read/write: 45/18
- Pointer modes: ip=UNKNOWN, op=WRITES_THROUGH
- Loops: 2; fixed counts: UNKNOWN
- Effects: `{"assert": false, "file_io": false, "indirect_call": false, "logging": false, "malloc": false}`
- Proposal: **STATEFUL**; purity=False; combinational=False
- Classification evidence:
  - AST observed writes or mutable-state effects: ['data_u.yuv', 'op', 'pic_s.data', 'yuv_s.u', 'yuv_s.v', 'yuv_s.y']
  - AST pointer modes: ['UNKNOWN', 'WRITES_THROUGH']
  - AST observed field reads: data_u.yuv, data_u.yuv, data_u.yuv, data_u.yuv, data_u.yuv, data_u.yuv, data_u.yuv, data_u.yuv, data_u.yuv, data_u.yuv, data_u.yuv, data_u.yuv, pic_s.bits, pic_s.data, pic_s.data, pic_s.data, pic_s.data, pic_s.data, pic_s.data, pic_s.data, pic_s.data, pic_s.data, pic_s.data, pic_s.data, pic_s.data, pic_s.h, pic_s.w, pic_s.w, pic_s.w, pic_s.w, pic_s.w, pic_s.w, pic_s.w, yuv_s.u, yuv_s.u, yuv_s.u, yuv_s.u, yuv_s.u, yuv_s.v, yuv_s.v, yuv_s.v, yuv_s.v, yuv_s.v, yuv_s.y, yuv_s.y
  - AST loop count is 2; trip proofs are retained per loop

## `yuv_422_444_region`

- Source: `dsc_utils.c:375`
- Clang USR: `c:@F@yuv_422_444_region`
- Return: `void`; parameters: `p: pic_t *`, `dsc_cfg: dsc_cfg_t *`
- Callers: DSC_Algorithm
- Callees: exit, printf
- Global read/write: 0/0; field read/write: 0/0
- Pointer modes: p=READ_ONLY, dsc_cfg=READ_ONLY
- Loops: 0; fixed counts: UNKNOWN
- Effects: `{"assert": false, "file_io": false, "indirect_call": false, "logging": true, "malloc": false}`
- Proposal: **IO_OR_DEBUG**; purity=False; combinational=False
- Classification evidence:
  - AST observed no global/field/pointee writes
  - AST pointer modes: ['READ_ONLY', 'READ_ONLY']
  - AST observed no loop

## `yuv_444_422`

- Source: `utl.c:533`
- Clang USR: `c:@F@yuv_444_422`
- Return: `void`; parameters: `ip: pic_t *`, `op: pic_t *`
- Callers: main
- Callees: conv, exit, pcopy_header, printf
- Global read/write: 1/0; field read/write: 41/19
- Pointer modes: ip=UNKNOWN, op=WRITES_THROUGH
- Loops: 12; fixed counts: UNKNOWN
- Effects: `{"assert": false, "file_io": false, "indirect_call": false, "logging": true, "malloc": false}`
- Proposal: **IO_OR_DEBUG**; purity=False; combinational=False
- Classification evidence:
  - AST observed writes or mutable-state effects: ['data_u.yuv', 'op', 'pic_s.chroma', 'pic_s.data', 'yuv_s.u', 'yuv_s.v', 'yuv_s.y']
  - AST pointer modes: ['UNKNOWN', 'WRITES_THROUGH']
  - AST observed global reads: chm_444_422_03
  - AST observed field reads: data_u.yuv, data_u.yuv, data_u.yuv, data_u.yuv, data_u.yuv, data_u.yuv, pic_s.bits, pic_s.chroma, pic_s.chroma, pic_s.data, pic_s.data, pic_s.data, pic_s.data, pic_s.data, pic_s.data, pic_s.h, pic_s.h, pic_s.h, pic_s.h, pic_s.h, pic_s.h, pic_s.h, pic_s.h, pic_s.h, pic_s.h, pic_s.w, pic_s.w, pic_s.w, pic_s.w, pic_s.w, pic_s.w, pic_s.w, pic_s.w, pic_s.w, pic_s.w, yuv_s.u, yuv_s.u, yuv_s.v, yuv_s.v, yuv_s.y, yuv_s.y
  - AST loop count is 12; trip proofs are retained per loop

## `yuv_444_422_region`

- Source: `dsc_utils.c:385`
- Clang USR: `c:@F@yuv_444_422_region`
- Return: `void`; parameters: `p: pic_t *`, `dsc_cfg: dsc_cfg_t *`
- Callers: DSC_Algorithm
- Callees: exit, printf
- Global read/write: 0/0; field read/write: 0/0
- Pointer modes: p=READ_ONLY, dsc_cfg=READ_ONLY
- Loops: 0; fixed counts: UNKNOWN
- Effects: `{"assert": false, "file_io": false, "indirect_call": false, "logging": true, "malloc": false}`
- Proposal: **IO_OR_DEBUG**; purity=False; combinational=False
- Classification evidence:
  - AST observed no global/field/pointee writes
  - AST pointer modes: ['READ_ONLY', 'READ_ONLY']
  - AST observed no loop

## `yuv_read`

- Source: `utl.c:1335`
- Clang USR: `c:@F@yuv_read`
- Return: `int`; parameters: `fname: char *`, `ip: pic_t **`, `width: int`, `height: int`, `framenum: int`, `bpc: int`, `numframes: int *`, `filetype: int`
- Callers: main
- Callees: fclose, fgetc, fopen, fseeko, ftello, pcreate_ext, printf, uyvy_read
- Global read/write: 0/0; field read/write: 12/25
- Pointer modes: fname=UNKNOWN, ip=WRITES_THROUGH, numframes=WRITES_THROUGH
- Loops: 6; fixed counts: UNKNOWN
- Effects: `{"assert": false, "file_io": true, "indirect_call": false, "logging": true, "malloc": false}`
- Proposal: **IO_OR_DEBUG**; purity=False; combinational=False
- Classification evidence:
  - AST observed writes or mutable-state effects: ['data_u.yuv', 'ip', 'numframes', 'pic_s.data', 'pic_s.limited_range', 'yuv_s.u', 'yuv_s.v', 'yuv_s.y']
  - AST pointer modes: ['UNKNOWN', 'WRITES_THROUGH', 'WRITES_THROUGH']
  - AST observed field reads: data_u.yuv, data_u.yuv, data_u.yuv, data_u.yuv, pic_s.data, pic_s.data, pic_s.data, pic_s.data, yuv_s.y, yuv_s.y, yuv_s.y, yuv_s.y
  - AST loop count is 6; trip proofs are retained per loop

## `yuv_write`

- Source: `utl.c:1450`
- Clang USR: `c:@F@yuv_write`
- Return: `int`; parameters: `fname: char *`, `op: pic_t *`, `framenum: int`, `filetype: int`
- Callers: main
- Callees: fclose, fopen, fputc, fseek, printf, uyvy_write
- Global read/write: 0/0; field read/write: 30/0
- Pointer modes: fname=UNKNOWN, op=UNKNOWN
- Loops: 6; fixed counts: UNKNOWN
- Effects: `{"assert": false, "file_io": true, "indirect_call": false, "logging": true, "malloc": false}`
- Proposal: **IO_OR_DEBUG**; purity=False; combinational=False
- Classification evidence:
  - AST observed no global/field/pointee writes
  - AST pointer modes: ['UNKNOWN', 'UNKNOWN']
  - AST observed field reads: data_u.yuv, data_u.yuv, data_u.yuv, data_u.yuv, data_u.yuv, data_u.yuv, data_u.yuv, data_u.yuv, data_u.yuv, pic_s.bits, pic_s.data, pic_s.data, pic_s.data, pic_s.data, pic_s.data, pic_s.data, pic_s.data, pic_s.data, pic_s.data, pic_s.h, pic_s.w, yuv_s.u, yuv_s.u, yuv_s.u, yuv_s.v, yuv_s.v, yuv_s.v, yuv_s.y, yuv_s.y, yuv_s.y
  - AST loop count is 6; trip proofs are retained per loop

## Component-loop evidence

Conditional component bounds are retained as AST facts; no fixed 3/4 simplification is made without proof.

- `BlockPredSearch` line 959: `i<dsc_state->numComponents`; cases=[]; dependency=POTENTIAL_CROSS_ITERATION_DEPENDENCY
- `BlockPredSearch` line 1035: `j<dsc_state->numComponents`; cases=[]; dependency=NO_SAME_LOCATION_READ_WRITE_OBSERVED
- `DSC_Algorithm` line 2667: `cpnt<dsc_state->numComponents`; cases=[]; dependency=POTENTIAL_CROSS_ITERATION_DEPENDENCY
- `DSC_Algorithm` line 2757: `i<dsc_state->numComponents`; cases=[]; dependency=POTENTIAL_CROSS_ITERATION_DEPENDENCY
- `DSC_Algorithm` line 2820: `cpnt < dsc_state->numComponents`; cases=[]; dependency=POTENTIAL_CROSS_ITERATION_DEPENDENCY
- `DSC_Algorithm` line 2886: `cpnt < dsc_state->numComponents`; cases=[]; dependency=POTENTIAL_CROSS_ITERATION_DEPENDENCY
- `DSC_Algorithm` line 2941: `cpnt < dsc_state->numComponents`; cases=[]; dependency=POTENTIAL_CROSS_ITERATION_DEPENDENCY
- `DSC_Algorithm` line 2987: `cpnt<dsc_state->numComponents`; cases=[]; dependency=POTENTIAL_CROSS_ITERATION_DEPENDENCY
- `DSC_Algorithm` line 3002: `cpnt<dsc_state->numComponents`; cases=[]; dependency=NO_SAME_LOCATION_READ_WRITE_OBSERVED
- `DSC_Algorithm` line 3033: `cpnt<dsc_state->numComponents`; cases=[]; dependency=NO_SAME_LOCATION_READ_WRITE_OBSERVED
- `DSC_Algorithm` line 3076: `cpnt<dsc_state->numComponents`; cases=[]; dependency=NO_SAME_LOCATION_READ_WRITE_OBSERVED
- `ErrorHandler` line 180: `cpnt<dsc_state->numComponents`; cases=[]; dependency=POTENTIAL_CROSS_ITERATION_DEPENDENCY
- `HistoryLookup` line 597: `i<dsc_state->numComponents`; cases=[]; dependency=POTENTIAL_CROSS_ITERATION_DEPENDENCY
- `InitializeDSCState` line 2117: `i<dsc_state->numComponents`; cases=[]; dependency=POTENTIAL_CROSS_ITERATION_DEPENDENCY
- `InitializeDSCState` line 2170: `i<dsc_state->numComponents`; cases=[]; dependency=NO_SAME_LOCATION_READ_WRITE_OBSERVED
- `IsOrigFlatHIndex` line 1139: `i<dsc_state->numComponents`; cases=[]; dependency=POTENTIAL_CROSS_ITERATION_DEPENDENCY
- `IsOrigFlatHIndex` line 1148: `cpnt<dsc_state->numComponents`; cases=[]; dependency=POTENTIAL_CROSS_ITERATION_DEPENDENCY
- `IsOrigFlatHIndex` line 1174: `cpnt<dsc_state->numComponents`; cases=[]; dependency=POTENTIAL_CROSS_ITERATION_DEPENDENCY
- `IsOrigWithinQerr` line 632: `i<dsc_state->numComponents`; cases=[]; dependency=POTENTIAL_CROSS_ITERATION_DEPENDENCY
- `IsOrigWithinQerr` line 651: `cpnt<dsc_state->numComponents`; cases=[]; dependency=POTENTIAL_CROSS_ITERATION_DEPENDENCY
- `PopulateOrigLine` line 2300: `cpnt < dsc_state->numComponents`; cases=[]; dependency=POTENTIAL_CROSS_ITERATION_DEPENDENCY
- `UpdateHistoryElement` line 701: `cpnt<dsc_state->numComponents`; cases=[]; dependency=NO_SAME_LOCATION_READ_WRITE_OBSERVED
- `UpdateHistoryElement` line 713: `cpnt<dsc_state->numComponents`; cases=[]; dependency=POTENTIAL_CROSS_ITERATION_DEPENDENCY
- `UpdateICHistory` line 818: `cpnt<dsc_state->numComponents`; cases=[]; dependency=POTENTIAL_CROSS_ITERATION_DEPENDENCY
- `UseICHistory` line 861: `cpnt<dsc_state->numComponents`; cases=[]; dependency=POTENTIAL_CROSS_ITERATION_DEPENDENCY
- `check_qp_for_overflow` line 875: `cpnt<(dsc_cfg->native_422 ? 4 : 3)`; cases=[{'condition': 'condition true', 'count': 4}, {'condition': 'condition false', 'count': 3}]; dependency=POTENTIAL_CROSS_ITERATION_DEPENDENCY
- `check_qp_for_overflow` line 884: `cpnt<(dsc_cfg->native_422 ? 4 : 3)`; cases=[{'condition': 'condition true', 'count': 4}, {'condition': 'condition false', 'count': 3}]; dependency=POTENTIAL_CROSS_ITERATION_DEPENDENCY
