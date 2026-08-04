# Traceability orphan triage

This is a deterministic evidence projection for human review. It does not create traceability links or select RTL targets.

- Untraced production functions: 53
- Untraced PDF anchors: 150

## Production C functions

### `AddBits`

- Anchor: `code:function:c:@F@AddBits`; source: `multiplex.c:89-93`
- Next action: `KEEP_STATEFUL_OR_UNPROVEN_BOUNDARY` — Tool facts show stateful, impure, or non-combinational behavior
- Tool rank/score: `29` / `59.95`; eligible: `False`; purity/timing: `IMPURE` / `UNKNOWN`
- Coverage: `EXECUTED`; executed: `1535313`; eligible after coverage: `False`
- C evidence: `multiplex.c:83` — //! Add bits to one of the encoder FIFO's
- C evidence: `multiplex.c:84` — /*! \param dsc_cfg DSC configuration structure \param dsc_state Current DSC state \param CType Which component FIFO to add to \param d Data to add \param nbits Number of bits to add */

### `DSC_Algorithm`

- Anchor: `code:function:c:@F@DSC_Algorithm`; source: `dsc_codec.c:2594-3108`
- Next action: `KEEP_STATEFUL_OR_UNPROVEN_BOUNDARY` — Tool facts show stateful, impure, or non-combinational behavior
- Tool rank/score: `59` / `59.0`; eligible: `False`; purity/timing: `IMPURE` / `UNKNOWN`
- Coverage: `EXECUTED`; executed: `24`; eligible after coverage: `False`
- C evidence: `dsc_codec.c:2586` — //! Main DSC encoding and decoding algorithm
- C evidence: `dsc_codec.c:2587` — /*! \param isEncoder Flag indicating whether to do an encode (1) or decode (0) \param dsc_cfg DSC configuration structure \param ip Input picutre \param op Output picture (modified, only affects area of current slice) \param cmpr_buf Compr…

### `DSC_Decode`

- Anchor: `code:function:c:@F@DSC_Decode`; source: `dsc_codec.c:3129-3132`
- Next action: `KEEP_STATEFUL_OR_UNPROVEN_BOUNDARY` — Tool facts show stateful, impure, or non-combinational behavior
- Tool rank/score: `31` / `59.95`; eligible: `False`; purity/timing: `IMPURE` / `UNKNOWN`
- Coverage: `STATIC_BUT_UNCOVERED`; executed: `0`; eligible after coverage: `False`
- C evidence: `dsc_codec.c:3124` — //! Wrapper function for decode
- C evidence: `dsc_codec.c:3125` — /*! \param dsc_cfg DSC configuration structure \param p_out Output picture \param cmpr_buf Pointer to buffer containing compressed bitstream \param temp_pic Array of two pictures to use as temporary storage for YCoCg conversions */

### `DSC_Encode`

- Anchor: `code:function:c:@F@DSC_Encode`; source: `dsc_codec.c:3118-3121`
- Next action: `KEEP_STATEFUL_OR_UNPROVEN_BOUNDARY` — Tool facts show stateful, impure, or non-combinational behavior
- Tool rank/score: `32` / `59.95`; eligible: `False`; purity/timing: `IMPURE` / `UNKNOWN`
- Coverage: `EXECUTED`; executed: `24`; eligible after coverage: `False`
- C evidence: `dsc_codec.c:3111` — //! Wrapper function for encode
- C evidence: `dsc_codec.c:3112` — /*! \param dsc_cfg DSC configuration structure \param p_in Input picture \param p_out Output picture \param cmpr_buf Pointer to empty buffer to hold compressed bitstream \param temp_pic Array of two pictures to use as temporary storage for…

### `ErrorHandler`

- Anchor: `code:function:c:@F@ErrorHandler`; source: `dsc_codec.c:171-213`
- Next action: `KEEP_STATEFUL_OR_UNPROVEN_BOUNDARY` — Tool facts show stateful, impure, or non-combinational behavior
- Tool rank/score: `25` / `60.0`; eligible: `False`; purity/timing: `IMPURE` / `UNKNOWN`
- Coverage: `STATIC_BUT_UNCOVERED`; executed: `0`; eligible after coverage: `False`
- C evidence: `dsc_codec.c:168` — //! Fill out the rest of the slice with valid pixels when an error occurs. Note the standard does not specify what the pixels should be & this is just an example.
- C evidence: `dsc_codec.c:169` — /*! \param dsc_cfg DSC parameters \param dsc_state DSC state structure */

### `GetBits`

- Anchor: `code:function:c:@F@GetBits`; source: `multiplex.c:104-109`
- Next action: `KEEP_STATEFUL_OR_UNPROVEN_BOUNDARY` — Tool facts show stateful, impure, or non-combinational behavior
- Tool rank/score: `33` / `59.95`; eligible: `False`; purity/timing: `IMPURE` / `UNKNOWN`
- Coverage: `STATIC_BUT_UNCOVERED`; executed: `0`; eligible after coverage: `False`
- C evidence: `multiplex.c:96` — //! Get bits from the input bitstream (in non-susbtream mode) or from one of the funnel shifters (in substream mode)
- C evidence: `multiplex.c:97` — /*! \param dsc_cfg DSC configuration structure \param dsc_state Current DSC state \param unit Which substream (component) shifter to get data from \param nbits Number of bits to retrieve \param sign_extend Flag indicating whether return va…

### `HistoryLookup`

- Anchor: `code:function:c:@F@HistoryLookup`; source: `dsc_codec.c:543-600`
- Next action: `KEEP_STATEFUL_OR_UNPROVEN_BOUNDARY` — Tool facts show stateful, impure, or non-combinational behavior
- Tool rank/score: `40` / `59.9`; eligible: `False`; purity/timing: `IMPURE` / `UNKNOWN`
- Coverage: `EXECUTED`; executed: `25291655`; eligible after coverage: `False`
- C evidence: `dsc_codec.c:536` — //! Look up the pixel values for a given ICH index
- C evidence: `dsc_codec.c:537` — /*! \param dsc_cfg DSC configuration structure \param dsc_state DSC state structure \param entry History index (0-31) \param p Returned pixel value \param hPos Horizontal position in slice (to determine upper pixels, if applicable) \param…

### `InitializeDSCState`

- Anchor: `code:function:c:@F@InitializeDSCState`; source: `dsc_codec.c:2056-2178`
- Next action: `KEEP_STATEFUL_OR_UNPROVEN_BOUNDARY` — Tool facts show stateful, impure, or non-combinational behavior
- Tool rank/score: `54` / `59.7`; eligible: `False`; purity/timing: `IMPURE` / `UNKNOWN`
- Coverage: `EXECUTED`; executed: `24`; eligible after coverage: `False`
- C evidence: `dsc_codec.c:2052` — //! Initialize the DSC state
- C evidence: `dsc_codec.c:2053` — /*! \param dsc_cfg DSC configuration structure \param dsc_state DSC state structure \return Returns dsc_state that was passed in */

### `PopulateOrigLine`

- Anchor: `code:function:c:@F@PopulateOrigLine`; source: `dsc_codec.c:2294-2351`
- Next action: `KEEP_STATEFUL_OR_UNPROVEN_BOUNDARY` — Tool facts show stateful, impure, or non-combinational behavior
- Tool rank/score: `26` / `60.0`; eligible: `False`; purity/timing: `IMPURE` / `UNKNOWN`
- Coverage: `EXECUTED`; executed: `2592`; eligible after coverage: `False`
- C evidence: `dsc_codec.c:2289` — //! Convert original pixels in pic_t format to an array of unsigned int for easy access/
- C evidence: `dsc_codec.c:2290` — /*! \param dsc_cfg DSC configuration structure \param dsc_state DSC state structure \param ip Input picture \param vPos Which line of slice to use */

### `ProcessGroupDec`

- Anchor: `code:function:c:@F@ProcessGroupDec`; source: `multiplex.c:159-176`
- Next action: `KEEP_STATEFUL_OR_UNPROVEN_BOUNDARY` — Tool facts show stateful, impure, or non-combinational behavior
- Tool rank/score: `41` / `59.9`; eligible: `False`; purity/timing: `IMPURE` / `UNKNOWN`
- Coverage: `STATIC_BUT_UNCOVERED`; executed: `0`; eligible after coverage: `False`
- C evidence: `multiplex.c:155` — //! Process a single group through the FIFO's, and insert 0 - 3 mux words in shifters
- C evidence: `multiplex.c:156` — /*! \param dsc_cfg DSC configuration structure \param dsc_state Current DSC state \param buf Pointer to input buffer */

### `ProcessGroupEnc`

- Anchor: `code:function:c:@F@ProcessGroupEnc`; source: `multiplex.c:116-152`
- Next action: `KEEP_STATEFUL_OR_UNPROVEN_BOUNDARY` — Tool facts show stateful, impure, or non-combinational behavior
- Tool rank/score: `51` / `59.8`; eligible: `False`; purity/timing: `IMPURE` / `UNKNOWN`
- Coverage: `EXECUTED`; executed: `131328`; eligible after coverage: `False`
- C evidence: `multiplex.c:112` — //! Process a single group through the FIFO's, and generate 0 - 3 mux words
- C evidence: `multiplex.c:113` — /*! \param dsc_cfg DSC configuration structure \param dsc_state Current DSC state \param buf Pointer to output buffer */

### `RemoveBitsEncoderBuffer`

- Anchor: `code:function:c:@F@RemoveBitsEncoderBuffer`; source: `dsc_codec.c:1201-1231`
- Next action: `KEEP_STATEFUL_OR_UNPROVEN_BOUNDARY` — Tool facts show stateful, impure, or non-combinational behavior
- Tool rank/score: `23` / `65.0`; eligible: `False`; purity/timing: `IMPURE` / `STATEFUL`
- Coverage: `EXECUTED`; executed: `387818`; eligible after coverage: `False`
- C evidence: `dsc_codec.c:1198` — //! Function to remove one pixel's worth of bits from the encoder buffer model
- C evidence: `dsc_codec.c:1199` — /*! \param dsc_cfg DSC configuration structure \param dsc_state DSC state structure */

### `UpdateICHistory`

- Anchor: `code:function:c:@F@UpdateICHistory`; source: `dsc_codec.c:787-825`
- Next action: `KEEP_STATEFUL_OR_UNPROVEN_BOUNDARY` — Tool facts show stateful, impure, or non-combinational behavior
- Tool rank/score: `35` / `59.95`; eligible: `False`; purity/timing: `IMPURE` / `UNKNOWN`
- Coverage: `EXECUTED`; executed: `393984`; eligible after coverage: `False`
- C evidence: `dsc_codec.c:780` — //! Updates the ICH state using final reconstructed value
- C evidence: `dsc_codec.c:781` — /*! \param dsc_cfg DSC configuration structure \param dsc_state DSC state structure \param currLine Reconstructed samples for current line \param sampModCnt Index of which pixel within group \param hPos Horizontal position within slice (no…

### `UpdateMidpoint`

- Anchor: `code:function:c:@F@UpdateMidpoint`; source: `dsc_codec.c:875-899`
- Next action: `KEEP_STATEFUL_OR_UNPROVEN_BOUNDARY` — Tool facts show stateful, impure, or non-combinational behavior
- Tool rank/score: `27` / `60.0`; eligible: `False`; purity/timing: `IMPURE` / `UNKNOWN`
- Coverage: `EXECUTED`; executed: `131328`; eligible after coverage: `False`
- C evidence: `dsc_codec.c:870` — //! Encoder function to updated reconstructed pixels if midpoint prediction was selected
- C evidence: `dsc_codec.c:871` — /*! \param dsc_cfg DSC configuration structure \param dsc_state DSC state structure \param currLine Current line reconstructed samples (modified) \param flag_first_luma For 4:2:2, flag indicating that only the first luma unit has been proc…

### `UseICHistory`

- Anchor: `code:function:c:@F@UseICHistory`; source: `dsc_codec.c:832-867`
- Next action: `KEEP_STATEFUL_OR_UNPROVEN_BOUNDARY` — Tool facts show stateful, impure, or non-combinational behavior
- Tool rank/score: `36` / `59.95`; eligible: `False`; purity/timing: `IMPURE` / `UNKNOWN`
- Coverage: `EXECUTED`; executed: `11704`; eligible after coverage: `False`
- C evidence: `dsc_codec.c:828` — //! Encoder function to update the reconstructed samples & output picture if ICH is selected
- C evidence: `dsc_codec.c:829` — /*! \param dsc_cfg DSC configuration structure \param dsc_state DSC state structure \param currLine Current line reconstructed samples (modified) */

### `VLCGroup`

- Anchor: `code:function:c:@F@VLCGroup`; source: `dsc_codec.c:1710-1799`
- Next action: `KEEP_STATEFUL_OR_UNPROVEN_BOUNDARY` — Tool facts show stateful, impure, or non-combinational behavior
- Tool rank/score: `53` / `59.75`; eligible: `False`; purity/timing: `IMPURE` / `UNKNOWN`
- Coverage: `EXECUTED`; executed: `131328`; eligible after coverage: `False`
- C evidence: `dsc_codec.c:1706` — //! Code one unit
- C evidence: `dsc_codec.c:1707` — /*! \param dsc_cfg DSC configuration structure \param dsc_state DSC state structure \param byte_out_p Pointer to compressed bits buffer (modified) */

### `conv`

- Anchor: `code:function:c:@F@conv`; source: `utl.c:470-495`
- Next action: `CHECK_NON_OUTPUT_SCOPE` — The discovered function is reachable but not marked as observable-output contributing
- Tool rank/score: `62` / `50.0`; eligible: `False`; purity/timing: `PURE` / `UNKNOWN`
- Coverage: `STATIC_BUT_UNCOVERED`; executed: `0`; eligible after coverage: `False`

### `convertbits`

- Anchor: `code:function:c:@F@convertbits`; source: `utl.c:710-1036`
- Next action: `CHECK_NON_OUTPUT_SCOPE` — The discovered function is reachable but not marked as observable-output contributing
- Tool rank/score: `150` / `29.75`; eligible: `False`; purity/timing: `IMPURE` / `UNKNOWN`
- Coverage: `STATIC_BUT_UNCOVERED`; executed: `0`; eligible after coverage: `False`

### `fifo_clear`

- Anchor: `code:function:c:@F@fifo_clear`; source: `fifo.c:55-61`
- Next action: `CHECK_NON_OUTPUT_SCOPE` — The discovered function is reachable but not marked as observable-output contributing
- Tool rank/score: `86` / `35.0`; eligible: `False`; purity/timing: `IMPURE` / `STATEFUL`
- Coverage: `STATIC_BUT_UNCOVERED`; executed: `0`; eligible after coverage: `False`
- C evidence: `fifo.c:53` — //! Clear a FIFO object while keeping it allocated
- C evidence: `fifo.c:54` — /*! \param fifo Pointer to FIFO data structure */

### `fifo_flip_get_bits`

- Anchor: `code:function:c:@F@fifo_flip_get_bits`; source: `fifo.c:174-210`
- Next action: `CHECK_NON_OUTPUT_SCOPE` — The discovered function is reachable but not marked as observable-output contributing
- Tool rank/score: `109` / `29.9`; eligible: `False`; purity/timing: `IMPURE` / `UNKNOWN`
- Coverage: `STATIC_BUT_UNCOVERED`; executed: `0`; eligible after coverage: `False`
- C evidence: `fifo.c:169` — //! Get bits from a FIFO in a 32-bit reverse order
- C evidence: `fifo.c:170` — /*! \param fifo Pointer to FIFO data structure \param n Number of bits to retrieve \param sign_extend Flag indicating to extend sign bit for return value \return Value from FIFO */

### `fifo_flip_put_bits`

- Anchor: `code:function:c:@F@fifo_flip_put_bits`; source: `fifo.c:217-247`
- Next action: `CHECK_NON_OUTPUT_SCOPE` — The discovered function is reachable but not marked as observable-output contributing
- Tool rank/score: `110` / `29.9`; eligible: `False`; purity/timing: `IMPURE` / `UNKNOWN`
- Coverage: `STATIC_BUT_UNCOVERED`; executed: `0`; eligible after coverage: `False`
- C evidence: `fifo.c:213` — //! Put bits into a FIFO in 32-bit reverse order
- C evidence: `fifo.c:214` — /*! \param fifo Pointer to FIFO data structure \param d Value to add to FIFO \param n Number of bits to add to FIFO */

### `fifo_free`

- Anchor: `code:function:c:@F@fifo_free`; source: `fifo.c:66-69`
- Next action: `KEEP_STATEFUL_OR_UNPROVEN_BOUNDARY` — Tool facts show stateful, impure, or non-combinational behavior
- Tool rank/score: `14` / `79.95`; eligible: `False`; purity/timing: `IMPURE` / `COMBINATIONAL`
- Coverage: `EXECUTED`; executed: `288`; eligible after coverage: `False`
- C evidence: `fifo.c:64` — //! Free a FIFO object
- C evidence: `fifo.c:65` — /*! \param fifo Pointer to FIFO data structure */

### `fifo_get_bits`

- Anchor: `code:function:c:@F@fifo_get_bits`; source: `fifo.c:77-108`
- Next action: `KEEP_STATEFUL_OR_UNPROVEN_BOUNDARY` — Tool facts show stateful, impure, or non-combinational behavior
- Tool rank/score: `42` / `59.9`; eligible: `False`; purity/timing: `IMPURE` / `UNKNOWN`
- Coverage: `EXECUTED`; executed: `1392526`; eligible after coverage: `False`
- C evidence: `fifo.c:72` — //! Get bits from a FIFO
- C evidence: `fifo.c:73` — /*! \param fifo Pointer to FIFO data structure \param n Number of bits to retrieve \param sign_extend Flag indicating to extend sign bit for return value \return Value from FIFO */

### `fifo_init`

- Anchor: `code:function:c:@F@fifo_init`; source: `fifo.c:43-51`
- Next action: `KEEP_STATEFUL_OR_UNPROVEN_BOUNDARY` — Tool facts show stateful, impure, or non-combinational behavior
- Tool rank/score: `24` / `64.95`; eligible: `False`; purity/timing: `IMPURE` / `STATEFUL`
- Coverage: `EXECUTED`; executed: `288`; eligible after coverage: `False`
- C evidence: `fifo.c:33` — /*! \file fifo.c * Generic bit FIFO functions */
- C evidence: `fifo.c:40` — //! Initialize a FIFO object
- C evidence: `fifo.c:41` — /*! \param fifo Pointer to FIFO data structure \param size Specifies FIFO size in bytes */

### `fifo_put_bits`

- Anchor: `code:function:c:@F@fifo_put_bits`; source: `fifo.c:115-140`
- Next action: `KEEP_STATEFUL_OR_UNPROVEN_BOUNDARY` — Tool facts show stateful, impure, or non-combinational behavior
- Tool rank/score: `43` / `59.9`; eligible: `False`; purity/timing: `IMPURE` / `UNKNOWN`
- Coverage: `EXECUTED`; executed: `2523961`; eligible after coverage: `False`
- C evidence: `fifo.c:111` — //! Put bits into a FIFO
- C evidence: `fifo.c:112` — /*! \param fifo Pointer to FIFO data structure \param d Value to add to FIFO \param n Number of bits to add to FIFO */

### `getbits`

- Anchor: `code:function:c:@F@getbits`; source: `dsc_utils.c:109-138`
- Next action: `KEEP_STATEFUL_OR_UNPROVEN_BOUNDARY` — Tool facts show stateful, impure, or non-combinational behavior
- Tool rank/score: `28` / `60.0`; eligible: `False`; purity/timing: `IMPURE` / `UNKNOWN`
- Coverage: `STATIC_BUT_UNCOVERED`; executed: `0`; eligible after coverage: `False`
- C evidence: `dsc_utils.c:103` — //! Read bits from a buffer in memory
- C evidence: `dsc_utils.c:104` — /*! \param size Number of bits to read \param buf Pointer to compressed bits buffer \param bit_count Number of bits read so far (modified) \param sign_extend Flag indicating to do a sign extension on the result \return Value from bitstream…

### `gettoken`

- Anchor: `code:function:c:@F@gettoken`; source: `utl.c:1038-1066`
- Next action: `CHECK_NON_OUTPUT_SCOPE` — The discovered function is reachable but not marked as observable-output contributing
- Tool rank/score: `101` / `29.95`; eligible: `False`; purity/timing: `IMPURE` / `UNKNOWN`
- Coverage: `EXECUTED`; executed: `52`; eligible after coverage: `False`

### `line_to_int`

- Anchor: `code:function:c:@F@line_to_int`; source: `rc_tables.h:382-402`
- Next action: `CHECK_NON_OUTPUT_SCOPE` — The discovered function is reachable but not marked as observable-output contributing
- Tool rank/score: `113` / `29.9`; eligible: `False`; purity/timing: `IMPURE` / `UNKNOWN`
- Coverage: `STATIC_BUT_UNCOVERED`; executed: `0`; eligible after coverage: `False`

### `palloc`

- Anchor: `code:function:c:@F@palloc`; source: `utl.c:55-80`
- Next action: `CHECK_NON_OUTPUT_SCOPE` — The discovered function is reachable but not marked as observable-output contributing
- Tool rank/score: `153` / `29.75`; eligible: `False`; purity/timing: `IMPURE` / `UNKNOWN`
- Coverage: `EXECUTED`; executed: `328`; eligible after coverage: `False`

### `parse_pps`

- Anchor: `code:function:c:@F@parse_pps`; source: `dsc_utils.c:404-499`
- Next action: `CHECK_NON_OUTPUT_SCOPE` — The discovered function is reachable but not marked as observable-output contributing
- Tool rank/score: `115` / `29.9`; eligible: `False`; purity/timing: `IMPURE` / `UNKNOWN`
- Coverage: `STATIC_BUT_UNCOVERED`; executed: `0`; eligible after coverage: `False`
- C evidence: `dsc_utils.c:392` — /*! ************************************************************************ * \brief * parse_pps() - Parse picture parameter set (PPS) * * \param buf * Pointer to PPS buffer * \param dsc_cfg * Configuration structure (output) * **********…

### `pcopy_header`

- Anchor: `code:function:c:@F@pcopy_header`; source: `utl.c:225-239`
- Next action: `CHECK_NON_OUTPUT_SCOPE` — The discovered function is reachable but not marked as observable-output contributing
- Tool rank/score: `87` / `35.0`; eligible: `False`; purity/timing: `IMPURE` / `STATEFUL`
- Coverage: `EXECUTED`; executed: `34`; eligible after coverage: `False`

### `pcreate_ext`

- Anchor: `code:function:c:@F@pcreate_ext`; source: `utl.c:144-223`
- Next action: `CHECK_NON_OUTPUT_SCOPE` — The discovered function is reachable but not marked as observable-output contributing
- Tool rank/score: `147` / `29.8`; eligible: `False`; purity/timing: `IMPURE` / `UNKNOWN`
- Coverage: `EXECUTED`; executed: `82`; eligible after coverage: `False`

### `pdestroy`

- Anchor: `code:function:c:@F@pdestroy`; source: `utl.c:241-302`
- Next action: `CHECK_NON_OUTPUT_SCOPE` — The discovered function is reachable but not marked as observable-output contributing
- Tool rank/score: `104` / `29.95`; eligible: `False`; purity/timing: `IMPURE` / `UNKNOWN`
- Coverage: `EXECUTED`; executed: `82`; eligible after coverage: `False`

### `ppm_read`

- Anchor: `code:function:c:@F@ppm_read`; source: `utl.c:1206-1219`
- Next action: `CHECK_NON_OUTPUT_SCOPE` — The discovered function is reachable but not marked as observable-output contributing
- Tool rank/score: `124` / `29.85`; eligible: `False`; purity/timing: `IMPURE` / `UNKNOWN`
- Coverage: `EXECUTED`; executed: `13`; eligible after coverage: `False`

### `ppm_write`

- Anchor: `code:function:c:@F@ppm_write`; source: `utl.c:1246-1303`
- Next action: `CHECK_NON_OUTPUT_SCOPE` — The discovered function is reachable but not marked as observable-output contributing
- Tool rank/score: `164` / `29.55`; eligible: `False`; purity/timing: `IMPURE` / `UNKNOWN`
- Coverage: `STATIC_BUT_UNCOVERED`; executed: `0`; eligible after coverage: `False`

### `print_pps`

- Anchor: `code:function:c:@F@print_pps`; source: `dsc_utils.c:609-678`
- Next action: `CHECK_NON_OUTPUT_SCOPE` — The discovered function is reachable but not marked as observable-output contributing
- Tool rank/score: `65` / `49.95`; eligible: `False`; purity/timing: `IMPURE` / `COMBINATIONAL`
- Coverage: `STATIC_BUT_UNCOVERED`; executed: `0`; eligible after coverage: `False`
- C evidence: `dsc_utils.c:597` — /*! ************************************************************************ * \brief * print_pps() - Display the picture parameter set (PPS) * * \param logfp * File pointer for log file * \param dsc_cfg * Configuration structure * *******…

### `print_pps_v2`

- Anchor: `code:function:c:@F@print_pps_v2`; source: `dsc_utils.c:694-798`
- Next action: `CHECK_NON_OUTPUT_SCOPE` — The discovered function is reachable but not marked as observable-output contributing
- Tool rank/score: `155` / `29.75`; eligible: `False`; purity/timing: `IMPURE` / `UNKNOWN`
- Coverage: `STATIC_BUT_UNCOVERED`; executed: `0`; eligible after coverage: `False`
- C evidence: `dsc_utils.c:681` — /*! ************************************************************************ * \brief * print_pps_v2() - Display the picture parameter set (PPS) * * \param logfp * File pointer for log file * \param dsc_cfg * Configuration structure * ****…

### `putbits`

- Anchor: `code:function:c:@F@putbits`; source: `dsc_utils.c:81-101`
- Next action: `KEEP_STATEFUL_OR_UNPROVEN_BOUNDARY` — Tool facts show stateful, impure, or non-combinational behavior
- Tool rank/score: `38` / `59.95`; eligible: `False`; purity/timing: `IMPURE` / `UNKNOWN`
- Coverage: `EXECUTED`; executed: `586716`; eligible after coverage: `False`
- C evidence: `dsc_utils.c:76` — //! Put bits into a buffer in memory
- C evidence: `dsc_utils.c:77` — /*! \param val Value to write \param size Number of bits to write \param buf Pointer to buffer location \param bit_count Bit index into buffer (modified) */

### `rgb2yuv`

- Anchor: `code:function:c:@F@rgb2yuv`; source: `utl.c:305-386`
- Next action: `CHECK_NON_OUTPUT_SCOPE` — The discovered function is reachable but not marked as observable-output contributing
- Tool rank/score: `126` / `29.85`; eligible: `False`; purity/timing: `IMPURE` / `UNKNOWN`
- Coverage: `STATIC_BUT_UNCOVERED`; executed: `0`; eligible after coverage: `False`

### `set_convertbits_rounding`

- Anchor: `code:function:c:@F@set_convertbits_rounding`; source: `utl.c:705-708`
- Next action: `CHECK_NON_OUTPUT_SCOPE` — The discovered function is reachable but not marked as observable-output contributing
- Tool rank/score: `88` / `35.0`; eligible: `False`; purity/timing: `IMPURE` / `STATEFUL`
- Coverage: `EXECUTED`; executed: `22`; eligible after coverage: `False`

### `uyvy_read`

- Anchor: `code:function:c:@F@uyvy_read`; source: `utl.c:1306-1332`
- Next action: `CHECK_NON_OUTPUT_SCOPE` — The discovered function is reachable but not marked as observable-output contributing
- Tool rank/score: `116` / `29.9`; eligible: `False`; purity/timing: `IMPURE` / `UNKNOWN`
- Coverage: `EXECUTED`; executed: `6`; eligible after coverage: `False`

### `uyvy_write`

- Anchor: `code:function:c:@F@uyvy_write`; source: `utl.c:1420-1447`
- Next action: `CHECK_NON_OUTPUT_SCOPE` — The discovered function is reachable but not marked as observable-output contributing
- Tool rank/score: `117` / `29.9`; eligible: `False`; purity/timing: `IMPURE` / `UNKNOWN`
- Coverage: `STATIC_BUT_UNCOVERED`; executed: `0`; eligible after coverage: `False`

### `write_pps`

- Anchor: `code:function:c:@F@write_pps`; source: `dsc_utils.c:514-595`
- Next action: `CHECK_NON_OUTPUT_SCOPE` — The discovered function is reachable but not marked as observable-output contributing
- Tool rank/score: `105` / `29.95`; eligible: `False`; purity/timing: `IMPURE` / `UNKNOWN`
- Coverage: `EXECUTED`; executed: `22`; eligible after coverage: `False`
- C evidence: `dsc_utils.c:502` — /*! ************************************************************************ * \brief * write_pps() - Construct picture parameter set (PPS) * * \param buf * Pointer to PPS buffer * \param dsc_cfg * Configuration structure * ***************…

### `writeppm`

- Anchor: `code:function:c:@F@writeppm`; source: `utl.c:1222-1243`
- Next action: `CHECK_NON_OUTPUT_SCOPE` — The discovered function is reachable but not marked as observable-output contributing
- Tool rank/score: `118` / `29.9`; eligible: `False`; purity/timing: `IMPURE` / `UNKNOWN`
- Coverage: `STATIC_BUT_UNCOVERED`; executed: `0`; eligible after coverage: `False`

### `yuv2rgb`

- Anchor: `code:function:c:@F@yuv2rgb`; source: `utl.c:389-465`
- Next action: `CHECK_NON_OUTPUT_SCOPE` — The discovered function is reachable but not marked as observable-output contributing
- Tool rank/score: `142` / `29.85`; eligible: `False`; purity/timing: `IMPURE` / `UNKNOWN`
- Coverage: `STATIC_BUT_UNCOVERED`; executed: `0`; eligible after coverage: `False`

### `yuv_420_422`

- Anchor: `code:function:c:@F@yuv_420_422`; source: `utl.c:671-701`
- Next action: `CHECK_NON_OUTPUT_SCOPE` — The discovered function is reachable but not marked as observable-output contributing
- Tool rank/score: `106` / `29.95`; eligible: `False`; purity/timing: `IMPURE` / `UNKNOWN`
- Coverage: `STATIC_BUT_UNCOVERED`; executed: `0`; eligible after coverage: `False`

### `yuv_422_420`

- Anchor: `code:function:c:@F@yuv_422_420`; source: `utl.c:615-667`
- Next action: `CHECK_NON_OUTPUT_SCOPE` — The discovered function is reachable but not marked as observable-output contributing
- Tool rank/score: `148` / `29.8`; eligible: `False`; purity/timing: `IMPURE` / `UNKNOWN`
- Coverage: `STATIC_BUT_UNCOVERED`; executed: `0`; eligible after coverage: `False`

### `yuv_422_444`

- Anchor: `code:function:c:@F@yuv_422_444`; source: `utl.c:503-531`
- Next action: `CHECK_NON_OUTPUT_SCOPE` — The discovered function is reachable but not marked as observable-output contributing
- Tool rank/score: `107` / `29.95`; eligible: `False`; purity/timing: `IMPURE` / `UNKNOWN`
- Coverage: `STATIC_BUT_UNCOVERED`; executed: `0`; eligible after coverage: `False`

### `yuv_422_444_region`

- Anchor: `code:function:c:@F@yuv_422_444_region`; source: `dsc_utils.c:375-379`
- Next action: `KEEP_STATEFUL_OR_UNPROVEN_BOUNDARY` — Tool facts show stateful, impure, or non-combinational behavior
- Tool rank/score: `16` / `79.9`; eligible: `False`; purity/timing: `IMPURE` / `COMBINATIONAL`
- Coverage: `STATIC_BUT_UNCOVERED`; executed: `0`; eligible after coverage: `False`

### `yuv_444_422`

- Anchor: `code:function:c:@F@yuv_444_422`; source: `utl.c:533-609`
- Next action: `CHECK_NON_OUTPUT_SCOPE` — The discovered function is reachable but not marked as observable-output contributing
- Tool rank/score: `149` / `29.8`; eligible: `False`; purity/timing: `IMPURE` / `UNKNOWN`
- Coverage: `STATIC_BUT_UNCOVERED`; executed: `0`; eligible after coverage: `False`

### `yuv_444_422_region`

- Anchor: `code:function:c:@F@yuv_444_422_region`; source: `dsc_utils.c:385-389`
- Next action: `KEEP_STATEFUL_OR_UNPROVEN_BOUNDARY` — Tool facts show stateful, impure, or non-combinational behavior
- Tool rank/score: `17` / `79.9`; eligible: `False`; purity/timing: `IMPURE` / `COMBINATIONAL`
- Coverage: `STATIC_BUT_UNCOVERED`; executed: `0`; eligible after coverage: `False`

### `yuv_read`

- Anchor: `code:function:c:@F@yuv_read`; source: `utl.c:1335-1417`
- Next action: `CHECK_NON_OUTPUT_SCOPE` — The discovered function is reachable but not marked as observable-output contributing
- Tool rank/score: `162` / `29.6`; eligible: `False`; purity/timing: `IMPURE` / `UNKNOWN`
- Coverage: `EXECUTED`; executed: `9`; eligible after coverage: `False`

### `yuv_write`

- Anchor: `code:function:c:@F@yuv_write`; source: `utl.c:1450-1518`
- Next action: `CHECK_NON_OUTPUT_SCOPE` — The discovered function is reachable but not marked as observable-output contributing
- Tool rank/score: `158` / `29.7`; eligible: `False`; purity/timing: `IMPURE` / `UNKNOWN`
- Coverage: `STATIC_BUT_UNCOVERED`; executed: `0`; eligible after coverage: `False`

## PDF anchors

### `pdf:figure:3-1`

- Kind/page: `figure` / `25`; title: illustrates how DSC works in an end-to-end system.
- Next action: `REVIEW_SPEC_SCOPE` — No matching C comment evidence was found for this PDF anchor
- Related C functions: none

### `pdf:figure:3-10`

- Kind/page: `figure` / `37`; title: Example of Substream Multiplexing
- Next action: `REVIEW_SPEC_SCOPE` — No matching C comment evidence was found for this PDF anchor
- Related C functions: none

### `pdf:figure:3-11`

- Kind/page: `figure` / `46`; title: illustrates an example of the buffering and decoding timing in a decoder that is
- Next action: `REVIEW_SPEC_SCOPE` — No matching C comment evidence was found for this PDF anchor
- Related C functions: none

### `pdf:figure:3-12`

- Kind/page: `figure` / `47`; title: Sample Positions in a Group for Native 4:2:2 Mode
- Next action: `REVIEW_SPEC_SCOPE` — No matching C comment evidence was found for this PDF anchor
- Related C functions: none

### `pdf:figure:3-13`

- Kind/page: `figure` / `48`; title: Mapping of 4:2:2/4:2:0 Picture to 4:4:4:4/4:4:4 Container
- Next action: `REVIEW_SPEC_SCOPE` — No matching C comment evidence was found for this PDF anchor
- Related C functions: none

### `pdf:figure:3-14`

- Kind/page: `figure` / `49`; title: Sample Positions in a Group for Native 4:2:0 Mode
- Next action: `REVIEW_SPEC_SCOPE` — No matching C comment evidence was found for this PDF anchor
- Related C functions: none

### `pdf:figure:3-2`

- Kind/page: `figure` / `26`; title: DSC Syntax and Application Layer Hierarchy
- Next action: `REVIEW_SPEC_SCOPE` — No matching C comment evidence was found for this PDF anchor
- Related C functions: none

### `pdf:figure:3-3`

- Kind/page: `figure` / `27`; title: Relationship between Picture Parameter Set, Pictures, and Slices
- Next action: `REVIEW_SPEC_SCOPE` — No matching C comment evidence was found for this PDF anchor
- Related C functions: none

### `pdf:figure:3-4`

- Kind/page: `figure` / `28`; title: illustrates the DSC encoding process, which generates bitstreams that precisely conform
- Next action: `REVIEW_SPEC_SCOPE` — No matching C comment evidence was found for this PDF anchor
- Related C functions: none

### `pdf:figure:3-5`

- Kind/page: `figure` / `29`; title: Decoding Process
- Next action: `REVIEW_SPEC_SCOPE` — No matching C comment evidence was found for this PDF anchor
- Related C functions: none

### `pdf:figure:3-6`

- Kind/page: `figure` / `31`; title: illustrates the sets of samples used for BP search and prediction for an example
- Next action: `REVIEW_SPEC_SCOPE` — No matching C comment evidence was found for this PDF anchor
- Related C functions: none

### `pdf:figure:3-7`

- Kind/page: `figure` / `33`; title: Indexed Color History Concept
- Next action: `REVIEW_SPEC_SCOPE` — No matching C comment evidence was found for this PDF anchor
- Related C functions: none

### `pdf:figure:3-8`

- Kind/page: `figure` / `36`; title: Example of Slice Layer Multiplexing Output
- Next action: `REVIEW_SPEC_SCOPE` — No matching C comment evidence was found for this PDF anchor
- Related C functions: none

### `pdf:figure:3-9`

- Kind/page: `figure` / `36`; title: Example of Substream Demultiplexing
- Next action: `REVIEW_SPEC_SCOPE` — No matching C comment evidence was found for this PDF anchor
- Related C functions: none

### `pdf:figure:6-1`

- Kind/page: `figure` / `76`; title: Pixels Surrounding Current Group
- Next action: `REVIEW_SPEC_SCOPE` — No matching C comment evidence was found for this PDF anchor
- Related C functions: none

### `pdf:figure:6-10`

- Kind/page: `figure` / `87`; title: Indexed Color History State Update Example – Two Unique Indices Selected
- Next action: `REVIEW_SPEC_SCOPE` — No matching C comment evidence was found for this PDF anchor
- Related C functions: none

### `pdf:figure:6-11`

- Kind/page: `figure` / `95`; title: Encoder Substream Multiplexer Block Diagram
- Next action: `REVIEW_SPEC_SCOPE` — No matching C comment evidence was found for this PDF anchor
- Related C functions: none

### `pdf:figure:6-12`

- Kind/page: `figure` / `97`; title: illustrates the overall RC algorithm structure.
- Next action: `REVIEW_SPEC_SCOPE` — No matching C comment evidence was found for this PDF anchor
- Related C functions: none

### `pdf:figure:6-13`

- Kind/page: `figure` / `98`; title: Long- and Short-term Rate Control Timing
- Next action: `REVIEW_SPEC_SCOPE` — No matching C comment evidence was found for this PDF anchor
- Related C functions: none

### `pdf:figure:6-14`

- Kind/page: `figure` / `99`; title: Buffer Level Tracker
- Next action: `REVIEW_SPEC_SCOPE` — No matching C comment evidence was found for this PDF anchor
- Related C functions: none

### `pdf:figure:6-15`

- Kind/page: `figure` / `104`; title: Example of Offset and Scale in Linear Transformation after First Line of Slice
- Next action: `REVIEW_SPEC_SCOPE` — No matching C comment evidence was found for this PDF anchor
- Related C functions: none

### `pdf:figure:6-16`

- Kind/page: `figure` / `106`; title: Range Selection
- Next action: `REVIEW_SPEC_SCOPE` — No matching C comment evidence was found for this PDF anchor
- Related C functions: none

### `pdf:figure:6-18`

- Kind/page: `figure` / `109`; title: illustrates the QP increment logic.
- Next action: `REVIEW_SPEC_SCOPE` — No matching C comment evidence was found for this PDF anchor
- Related C functions: none

### `pdf:figure:6-2`

- Kind/page: `figure` / `78`; title: Pixel Positions Used for Luma MMAP in Native 4:2:2 and 4:2:0 Modes
- Next action: `REVIEW_SPEC_SCOPE` — No matching C comment evidence was found for this PDF anchor
- Related C functions: none

### `pdf:figure:6-3`

- Kind/page: `figure` / `78`; title: Pixel Positions Used for Chroma MMAP in Native 4:2:2 Mode
- Next action: `REVIEW_SPEC_SCOPE` — No matching C comment evidence was found for this PDF anchor
- Related C functions: none

### `pdf:figure:6-4`

- Kind/page: `figure` / `79`; title: Pixel Positions Used for Chroma MMAP in Native 4:2:0 Mode
- Next action: `REVIEW_SPEC_SCOPE` — No matching C comment evidence was found for this PDF anchor
- Related C functions: none

### `pdf:figure:6-5`

- Kind/page: `figure` / `81`; title: 3x1 Partial Sum of Absolute Differences Used to Form
- Next action: `REVIEW_SPEC_SCOPE` — No matching C comment evidence was found for this PDF anchor
- Related C functions: none

### `pdf:figure:6-7`

- Kind/page: `figure` / `85`; title: Pixels with Chroma in Native 4:2:2 Mode
- Next action: `REVIEW_SPEC_SCOPE` — No matching C comment evidence was found for this PDF anchor
- Related C functions: none

### `pdf:figure:6-8`

- Kind/page: `figure` / `86`; title: Pixels with Chroma in Native 4:2:0 Mode (Even-position Line Example)
- Next action: `REVIEW_SPEC_SCOPE` — No matching C comment evidence was found for this PDF anchor
- Related C functions: none

### `pdf:figure:6-9`

- Kind/page: `figure` / `87`; title: Indexed Color History State Update Example – Three Unique Indices Selected
- Next action: `REVIEW_SPEC_SCOPE` — No matching C comment evidence was found for this PDF anchor
- Related C functions: none

### `pdf:figure:7-1`

- Kind/page: `figure` / `115`; title: Substream Demultiplexing Block Diagram
- Next action: `REVIEW_SPEC_SCOPE` — No matching C comment evidence was found for this PDF anchor
- Related C functions: none

### `pdf:figure:7-2`

- Kind/page: `figure` / `119`; title: Indexed Color History in Decoder
- Next action: `REVIEW_SPEC_SCOPE` — No matching C comment evidence was found for this PDF anchor
- Related C functions: none

### `pdf:figure:B-1`

- Kind/page: `figure` / `123`; title: illustrates the system view with 4:2:2 input/output.
- Next action: `REVIEW_SPEC_SCOPE` — No matching C comment evidence was found for this PDF anchor
- Related C functions: none

### `pdf:figure:B-2`

- Kind/page: `figure` / `123`; title: Simple 4:2:2 to 4:4:4 Conversion at Encoder Input
- Next action: `REVIEW_SPEC_SCOPE` — No matching C comment evidence was found for this PDF anchor
- Related C functions: none

### `pdf:figure:B-3`

- Kind/page: `figure` / `124`; title: 4:4:4 to Simple 4:2:2 Conversion at Decoder Output
- Next action: `REVIEW_SPEC_SCOPE` — No matching C comment evidence was found for this PDF anchor
- Related C functions: none

### `pdf:figure:F-1`

- Kind/page: `figure` / `134`; title: illustrates an example of decoder buffer fullness at different points within a slice.
- Next action: `REVIEW_SPEC_SCOPE` — No matching C comment evidence was found for this PDF anchor
- Related C functions: none

### `pdf:figure:G-1`

- Kind/page: `figure` / `137`; title: 1 Slice/Line
- Next action: `REVIEW_SPEC_SCOPE` — No matching C comment evidence was found for this PDF anchor
- Related C functions: none

### `pdf:figure:G-2`

- Kind/page: `figure` / `139`; title: 2 Slices/Line
- Next action: `REVIEW_SPEC_SCOPE` — No matching C comment evidence was found for this PDF anchor
- Related C functions: none

### `pdf:figure:G-3`

- Kind/page: `figure` / `142`; title: 4 Slices/Line
- Next action: `REVIEW_SPEC_SCOPE` — No matching C comment evidence was found for this PDF anchor
- Related C functions: none

### `pdf:model-note:MN_MIN_RBS:p129`

- Kind/page: `model_note` / `129`; title: unattached ; MN_MIN_RBS in codec_main.c for details).
- Next action: `REVIEW_SPEC_SCOPE` — No matching C comment evidence was found for this PDF anchor
- Related C functions: none

### `pdf:section:1`

- Kind/page: `section` / `15`; title: Introduction
- Next action: `REVIEW_SPEC_SCOPE` — No matching C comment evidence was found for this PDF anchor
- Related C functions: none

### `pdf:section:1.1`

- Kind/page: `section` / `15`; title: Document Organization
- Next action: `REVIEW_SPEC_SCOPE` — No matching C comment evidence was found for this PDF anchor
- Related C functions: none

### `pdf:section:1.2`

- Kind/page: `section` / `16`; title: Display Stream Compression Objectives
- Next action: `REVIEW_SPEC_SCOPE` — No matching C comment evidence was found for this PDF anchor
- Related C functions: none

### `pdf:section:1.3`

- Kind/page: `section` / `16`; title: Display Stream Compression Versions
- Next action: `REVIEW_SPEC_SCOPE` — No matching C comment evidence was found for this PDF anchor
- Related C functions: none

### `pdf:section:1.4`

- Kind/page: `section` / `17`; title: Acronyms, Initialisms, and Abbreviations
- Next action: `REVIEW_SPEC_SCOPE` — No matching C comment evidence was found for this PDF anchor
- Related C functions: none

### `pdf:section:1.5`

- Kind/page: `section` / `19`; title: Glossary
- Next action: `REVIEW_SPEC_SCOPE` — No matching C comment evidence was found for this PDF anchor
- Related C functions: none

### `pdf:section:1.6`

- Kind/page: `section` / `22`; title: Symbols
- Next action: `REVIEW_SPEC_SCOPE` — No matching C comment evidence was found for this PDF anchor
- Related C functions: none

### `pdf:section:1.6.1`

- Kind/page: `section` / `22`; title: Bit Ordering
- Next action: `REVIEW_SPEC_SCOPE` — No matching C comment evidence was found for this PDF anchor
- Related C functions: none

### `pdf:section:1.7`

- Kind/page: `section` / `23`; title: Conventions
- Next action: `REVIEW_SPEC_SCOPE` — No matching C comment evidence was found for this PDF anchor
- Related C functions: none

### `pdf:section:1.8`

- Kind/page: `section` / `23`; title: Reference Documents
- Next action: `REVIEW_SPEC_SCOPE` — No matching C comment evidence was found for this PDF anchor
- Related C functions: none

### `pdf:section:2`

- Kind/page: `section` / `24`; title: Requirements (Informative)
- Next action: `REVIEW_SPEC_SCOPE` — No matching C comment evidence was found for this PDF anchor
- Related C functions: none

### `pdf:section:3`

- Kind/page: `section` / `25`; title: Theory of Operation (Informative)
- Next action: `REVIEW_SPEC_SCOPE` — No matching C comment evidence was found for this PDF anchor
- Related C functions: none

### `pdf:section:3.1`

- Kind/page: `section` / `25`; title: Overview
- Next action: `REVIEW_SPEC_SCOPE` — No matching C comment evidence was found for this PDF anchor
- Related C functions: none

### `pdf:section:3.10`

- Kind/page: `section` / `47`; title: Differences between DSC v1.1 and DSC v1.2
- Next action: `REVIEW_SPEC_SCOPE` — No matching C comment evidence was found for this PDF anchor
- Related C functions: none

### `pdf:section:3.10.1`

- Kind/page: `section` / `47`; title: Native 4:2:2 and 4:2:0 Modes
- Next action: `REVIEW_SPEC_SCOPE` — No matching C comment evidence was found for this PDF anchor
- Related C functions: none

### `pdf:section:3.10.2`

- Kind/page: `section` / `49`; title: 14- and 16-bits Per Component Support
- Next action: `REVIEW_SPEC_SCOPE` — No matching C comment evidence was found for this PDF anchor
- Related C functions: none

### `pdf:section:3.10.3`

- Kind/page: `section` / `49`; title: Other Differences
- Next action: `REVIEW_SPEC_SCOPE` — No matching C comment evidence was found for this PDF anchor
- Related C functions: none

### `pdf:section:3.2`

- Kind/page: `section` / `30`; title: Color Space Conversion
- Next action: `REVIEW_SPEC_SCOPE` — No matching C comment evidence was found for this PDF anchor
- Related C functions: none

### `pdf:section:3.3`

- Kind/page: `section` / `30`; title: Prediction and Quantization
- Next action: `REVIEW_SPEC_SCOPE` — No matching C comment evidence was found for this PDF anchor
- Related C functions: none

### `pdf:section:3.3.1`

- Kind/page: `section` / `30`; title: Modified Median-Adaptive Prediction
- Next action: `REVIEW_SPEC_SCOPE` — No matching C comment evidence was found for this PDF anchor
- Related C functions: none

### `pdf:section:3.3.2`

- Kind/page: `section` / `31`; title: Block Prediction
- Next action: `REVIEW_SPEC_SCOPE` — No matching C comment evidence was found for this PDF anchor
- Related C functions: none

### `pdf:section:3.3.3`

- Kind/page: `section` / `32`; title: Midpoint Prediction
- Next action: `REVIEW_SPEC_SCOPE` — No matching C comment evidence was found for this PDF anchor
- Related C functions: none

### `pdf:section:3.4`

- Kind/page: `section` / `33`; title: Indexed Color History
- Next action: `REVIEW_SPEC_SCOPE` — No matching C comment evidence was found for this PDF anchor
- Related C functions: none

### `pdf:section:3.5`

- Kind/page: `section` / `34`; title: Bitstream Construction
- Next action: `REVIEW_SPEC_SCOPE` — No matching C comment evidence was found for this PDF anchor
- Related C functions: none

### `pdf:section:3.5.2`

- Kind/page: `section` / `36`; title: Substream Multiplexing
- Next action: `REVIEW_SPEC_SCOPE` — No matching C comment evidence was found for this PDF anchor
- Related C functions: none

### `pdf:section:3.6`

- Kind/page: `section` / `38`; title: Rate Control
- Next action: `REVIEW_SPEC_SCOPE` — No matching C comment evidence was found for this PDF anchor
- Related C functions: none

### `pdf:section:3.7`

- Kind/page: `section` / `39`; title: Timing
- Next action: `REVIEW_SPEC_SCOPE` — No matching C comment evidence was found for this PDF anchor
- Related C functions: none

### `pdf:section:3.7.1`

- Kind/page: `section` / `39`; title: Hypothetical Reference Decoder-Based Timing Model
- Next action: `REVIEW_SPEC_SCOPE` — No matching C comment evidence was found for this PDF anchor
- Related C functions: none

### `pdf:section:3.7.2`

- Kind/page: `section` / `41`; title: Constant and Variable Bit Rate Modes
- Next action: `REVIEW_SPEC_SCOPE` — No matching C comment evidence was found for this PDF anchor
- Related C functions: none

### `pdf:section:3.7.3`

- Kind/page: `section` / `42`; title: Slices and Timing
- Next action: `REVIEW_SPEC_SCOPE` — No matching C comment evidence was found for this PDF anchor
- Related C functions: none

### `pdf:section:3.8`

- Kind/page: `section` / `45`; title: Options for Slices
- Next action: `REVIEW_SPEC_SCOPE` — No matching C comment evidence was found for this PDF anchor
- Related C functions: none

### `pdf:section:3.9`

- Kind/page: `section` / `46`; title: Slice Multiplexing
- Next action: `REVIEW_SPEC_SCOPE` — No matching C comment evidence was found for this PDF anchor
- Related C functions: none

### `pdf:section:4`

- Kind/page: `section` / `50`; title: Syntax (Normative)
- Next action: `REVIEW_SPEC_SCOPE` — No matching C comment evidence was found for this PDF anchor
- Related C functions: none

### `pdf:section:4.1`

- Kind/page: `section` / `50`; title: Picture Parameter Set
- Next action: `REVIEW_SPEC_SCOPE` — No matching C comment evidence was found for this PDF anchor
- Related C functions: none

### `pdf:section:4.1.1`

- Kind/page: `section` / `50`; title: Syntax
- Next action: `REVIEW_SPEC_SCOPE` — No matching C comment evidence was found for this PDF anchor
- Related C functions: none

### `pdf:section:4.1.2`

- Kind/page: `section` / `58`; title: Picture Parameter Set Timing
- Next action: `REVIEW_SPEC_SCOPE` — No matching C comment evidence was found for this PDF anchor
- Related C functions: none

### `pdf:section:4.2`

- Kind/page: `section` / `59`; title: Picture Syntax
- Next action: `REVIEW_SPEC_SCOPE` — No matching C comment evidence was found for this PDF anchor
- Related C functions: none

### `pdf:section:4.2.1`

- Kind/page: `section` / `59`; title: Picture Syntax Overview
- Next action: `REVIEW_SPEC_SCOPE` — No matching C comment evidence was found for this PDF anchor
- Related C functions: none

### `pdf:section:4.2.2`

- Kind/page: `section` / `59`; title: Slice Multiplexing in Constant Bit Rate Mode
- Next action: `REVIEW_SPEC_SCOPE` — No matching C comment evidence was found for this PDF anchor
- Related C functions: none

### `pdf:section:4.2.3`

- Kind/page: `section` / `60`; title: Slice Multiplexing in Variable Bit Rate Mode
- Next action: `REVIEW_SPEC_SCOPE` — No matching C comment evidence was found for this PDF anchor
- Related C functions: none

### `pdf:section:4.4`

- Kind/page: `section` / `63`; title: Substream Multiplexing
- Next action: `REVIEW_SPEC_SCOPE` — No matching C comment evidence was found for this PDF anchor
- Related C functions: none

### `pdf:section:4.5`

- Kind/page: `section` / `65`; title: Substream Syntax
- Next action: `REVIEW_SPEC_SCOPE` — No matching C comment evidence was found for this PDF anchor
- Related C functions: none

### `pdf:section:5`

- Kind/page: `section` / `73`; title: Capability Parameter Set (Informative)
- Next action: `REVIEW_SPEC_SCOPE` — No matching C comment evidence was found for this PDF anchor
- Related C functions: none

### `pdf:section:6`

- Kind/page: `section` / `74`; title: Encoding Process (Normative)
- Next action: `REVIEW_SPEC_SCOPE` — No matching C comment evidence was found for this PDF anchor
- Related C functions: none

### `pdf:section:6.2`

- Kind/page: `section` / `75`; title: Slice Padding
- Next action: `REVIEW_SPEC_SCOPE` — No matching C comment evidence was found for this PDF anchor
- Related C functions: none

### `pdf:section:6.4`

- Kind/page: `section` / `76`; title: Prediction and Quantization
- Next action: `REVIEW_SPEC_SCOPE` — No matching C comment evidence was found for this PDF anchor
- Related C functions: none

### `pdf:section:6.4.4`

- Kind/page: `section` / `80`; title: Prediction Method Decision
- Next action: `REVIEW_SPEC_SCOPE` — No matching C comment evidence was found for this PDF anchor
- Related C functions: none

### `pdf:section:6.5`

- Kind/page: `section` / `84`; title: Indexed Color History
- Next action: `REVIEW_SPEC_SCOPE` — No matching C comment evidence was found for this PDF anchor
- Related C functions: none

### `pdf:section:6.5.1`

- Kind/page: `section` / `84`; title: Pixel History
- Next action: `REVIEW_SPEC_SCOPE` — No matching C comment evidence was found for this PDF anchor
- Related C functions: none

### `pdf:section:6.5.2`

- Kind/page: `section` / `86`; title: Indexed Color History Updates
- Next action: `REVIEW_SPEC_SCOPE` — No matching C comment evidence was found for this PDF anchor
- Related C functions: none

### `pdf:section:6.5.3`

- Kind/page: `section` / `88`; title: Encoder Decisions
- Next action: `REVIEW_SPEC_SCOPE` — No matching C comment evidence was found for this PDF anchor
- Related C functions: none

### `pdf:section:6.5.3.3`

- Kind/page: `section` / `91`; title: Full Error Precision for ICH Decision
- Next action: `REVIEW_SPEC_SCOPE` — No matching C comment evidence was found for this PDF anchor
- Related C functions: none

### `pdf:section:6.7`

- Kind/page: `section` / `95`; title: Substream Multiplexer
- Next action: `REVIEW_SPEC_SCOPE` — No matching C comment evidence was found for this PDF anchor
- Related C functions: none

### `pdf:section:6.7.1`

- Kind/page: `section` / `95`; title: Balance FIFOs
- Next action: `REVIEW_SPEC_SCOPE` — No matching C comment evidence was found for this PDF anchor
- Related C functions: none

### `pdf:section:6.7.2`

- Kind/page: `section` / `96`; title: Multiplexer
- Next action: `REVIEW_SPEC_SCOPE` — No matching C comment evidence was found for this PDF anchor
- Related C functions: none

### `pdf:section:6.7.3`

- Kind/page: `section` / `96`; title: Decoder Model
- Next action: `REVIEW_SPEC_SCOPE` — No matching C comment evidence was found for this PDF anchor
- Related C functions: none

### `pdf:section:6.7.4`

- Kind/page: `section` / `96`; title: End of Slice
- Next action: `REVIEW_SPEC_SCOPE` — No matching C comment evidence was found for this PDF anchor
- Related C functions: none

### `pdf:section:6.8`

- Kind/page: `section` / `97`; title: Rate Control Algorithm
- Next action: `REVIEW_SPEC_SCOPE` — No matching C comment evidence was found for this PDF anchor
- Related C functions: none

### `pdf:section:6.8.1`

- Kind/page: `section` / `99`; title: Buffer Level Tracker
- Next action: `REVIEW_SPEC_SCOPE` — No matching C comment evidence was found for this PDF anchor
- Related C functions: none

### `pdf:section:6.8.5`

- Kind/page: `section` / `94`; title: describes the encoder algorithm that is used to determine the values to use for
- Next action: `REVIEW_SPEC_SCOPE` — No matching C comment evidence was found for this PDF anchor
- Related C functions: none

### `pdf:section:7`

- Kind/page: `section` / `114`; title: 3 4 3 4 3 4 3 4 3 4
- Next action: `REVIEW_SPEC_SCOPE` — No matching C comment evidence was found for this PDF anchor
- Related C functions: none

### `pdf:section:7.1`

- Kind/page: `section` / `115`; title: Substream Demultiplexing
- Next action: `REVIEW_SPEC_SCOPE` — No matching C comment evidence was found for this PDF anchor
- Related C functions: none

### `pdf:section:7.3`

- Kind/page: `section` / `116`; title: Rate Control
- Next action: `REVIEW_SPEC_SCOPE` — No matching C comment evidence was found for this PDF anchor
- Related C functions: none

### `pdf:section:7.5`

- Kind/page: `section` / `118`; title: Prediction and Reconstruction
- Next action: `REVIEW_SPEC_SCOPE` — No matching C comment evidence was found for this PDF anchor
- Related C functions: none

### `pdf:section:7.5.1`

- Kind/page: `section` / `118`; title: Prediction Methods
- Next action: `REVIEW_SPEC_SCOPE` — No matching C comment evidence was found for this PDF anchor
- Related C functions: none

### `pdf:section:7.5.2`

- Kind/page: `section` / `118`; title: Prediction Method Selection
- Next action: `REVIEW_SPEC_SCOPE` — No matching C comment evidence was found for this PDF anchor
- Related C functions: none

### `pdf:section:7.5.2.1`

- Kind/page: `section` / `118`; title: Selection between Block and Modified Median-Adaptive Prediction
- Next action: `REVIEW_SPEC_SCOPE` — No matching C comment evidence was found for this PDF anchor
- Related C functions: none

### `pdf:section:7.6`

- Kind/page: `section` / `119`; title: Indexed Color History
- Next action: `REVIEW_SPEC_SCOPE` — No matching C comment evidence was found for this PDF anchor
- Related C functions: none

### `pdf:section:7.6.1`

- Kind/page: `section` / `119`; title: History
- Next action: `REVIEW_SPEC_SCOPE` — No matching C comment evidence was found for this PDF anchor
- Related C functions: none

### `pdf:section:7.6.2`

- Kind/page: `section` / `119`; title: Decoder History Updates
- Next action: `REVIEW_SPEC_SCOPE` — No matching C comment evidence was found for this PDF anchor
- Related C functions: none

### `pdf:section:7.8`

- Kind/page: `section` / `121`; title: Error Handling
- Next action: `REVIEW_SPEC_SCOPE` — No matching C comment evidence was found for this PDF anchor
- Related C functions: none

### `pdf:section:A`

- Kind/page: `section` / `122`; title: DSC File Format (Normative)
- Next action: `REVIEW_SPEC_SCOPE` — No matching C comment evidence was found for this PDF anchor
- Related C functions: none

### `pdf:section:G`

- Kind/page: `section` / `136`; title: Slice Timing Examples (Informative)
- Next action: `REVIEW_SPEC_SCOPE` — No matching C comment evidence was found for this PDF anchor
- Related C functions: none

### `pdf:table:1`

- Kind/page: `table` / `10`; title: Patents (Continued)
- Next action: `REVIEW_SPEC_SCOPE` — No matching C comment evidence was found for this PDF anchor
- Related C functions: none

### `pdf:table:1-1`

- Kind/page: `table` / `17`; title: DSC Supported Modes, by Version
- Next action: `REVIEW_SPEC_SCOPE` — No matching C comment evidence was found for this PDF anchor
- Related C functions: none

### `pdf:table:1-2`

- Kind/page: `table` / `17`; title: Acronyms, Initialisms, and Abbreviations
- Next action: `REVIEW_SPEC_SCOPE` — No matching C comment evidence was found for this PDF anchor
- Related C functions: none

### `pdf:table:1-3`

- Kind/page: `table` / `19`; title: Glossary of Terms
- Next action: `REVIEW_SPEC_SCOPE` — No matching C comment evidence was found for this PDF anchor
- Related C functions: none

### `pdf:table:1-4`

- Kind/page: `table` / `23`; title: Normative Reference Document
- Next action: `REVIEW_SPEC_SCOPE` — No matching C comment evidence was found for this PDF anchor
- Related C functions: none

### `pdf:table:1-5`

- Kind/page: `table` / `23`; title: Informative Reference Documents
- Next action: `REVIEW_SPEC_SCOPE` — No matching C comment evidence was found for this PDF anchor
- Related C functions: none

### `pdf:table:2`

- Kind/page: `table` / `11`; title: Main Contributors to DSC v1.2a
- Next action: `REVIEW_SPEC_SCOPE` — No matching C comment evidence was found for this PDF anchor
- Related C functions: none

### `pdf:table:3`

- Kind/page: `table` / `13`; title: Revision History
- Next action: `REVIEW_SPEC_SCOPE` — No matching C comment evidence was found for this PDF anchor
- Related C functions: none

### `pdf:table:3-2`

- Kind/page: `table` / `38`; title: Rate Control Components
- Next action: `REVIEW_SPEC_SCOPE` — No matching C comment evidence was found for this PDF anchor
- Related C functions: none

### `pdf:table:4-1`

- Kind/page: `table` / `50`; title: Picture Parameter Set Syntax Elements
- Next action: `REVIEW_SPEC_SCOPE` — No matching C comment evidence was found for this PDF anchor
- Related C functions: none

### `pdf:table:4-10`

- Kind/page: `table` / `65`; title: describes each Y_syntax_element(). Table 4-11 lists the Y2_syntax_element() syntax
- Next action: `REVIEW_SPEC_SCOPE` — No matching C comment evidence was found for this PDF anchor
- Related C functions: none

### `pdf:table:4-11`

- Kind/page: `table` / `67`; title: Y2 Substream Layer Syntax (Native 4:2:2 Mode Only)
- Next action: `REVIEW_SPEC_SCOPE` — No matching C comment evidence was found for this PDF anchor
- Related C functions: none

### `pdf:table:4-12`

- Kind/page: `table` / `68`; title: Y2_syntax_element() Syntax (Native 4:2:2 Mode Only)
- Next action: `REVIEW_SPEC_SCOPE` — No matching C comment evidence was found for this PDF anchor
- Related C functions: none

### `pdf:table:4-13`

- Kind/page: `table` / `68`; title: Y2_syntax_element() Descriptions
- Next action: `REVIEW_SPEC_SCOPE` — No matching C comment evidence was found for this PDF anchor
- Related C functions: none

### `pdf:table:4-14`

- Kind/page: `table` / `69`; title: lists the Co Substream Layer syntax. Table 4-15 lists the Co_syntax_element() syntax.
- Next action: `REVIEW_SPEC_SCOPE` — No matching C comment evidence was found for this PDF anchor
- Related C functions: none

### `pdf:table:4-15`

- Kind/page: `table` / `69`; title: Co_syntax_element() Syntax
- Next action: `REVIEW_SPEC_SCOPE` — No matching C comment evidence was found for this PDF anchor
- Related C functions: none

### `pdf:table:4-16`

- Kind/page: `table` / `69`; title: describes each Co_syntax_element().
- Next action: `REVIEW_SPEC_SCOPE` — No matching C comment evidence was found for this PDF anchor
- Related C functions: none

### `pdf:table:4-17`

- Kind/page: `table` / `71`; title: lists the Cg Substream Layer syntax. Table 4-18 lists the Cg_syntax_element() syntax.
- Next action: `REVIEW_SPEC_SCOPE` — No matching C comment evidence was found for this PDF anchor
- Related C functions: none

### `pdf:table:4-18`

- Kind/page: `table` / `71`; title: Cg_syntax_element() Syntax
- Next action: `REVIEW_SPEC_SCOPE` — No matching C comment evidence was found for this PDF anchor
- Related C functions: none

### `pdf:table:4-19`

- Kind/page: `table` / `71`; title: describes each Cg_syntax_element().
- Next action: `REVIEW_SPEC_SCOPE` — No matching C comment evidence was found for this PDF anchor
- Related C functions: none

### `pdf:table:4-2`

- Kind/page: `table` / `55`; title: through for details).
- Next action: `REVIEW_SPEC_SCOPE` — No matching C comment evidence was found for this PDF anchor
- Related C functions: none

### `pdf:table:4-3`

- Kind/page: `table` / `58`; title: rc_range_parameters Field Descriptions
- Next action: `REVIEW_SPEC_SCOPE` — No matching C comment evidence was found for this PDF anchor
- Related C functions: none

### `pdf:table:4-4`

- Kind/page: `table` / `59`; title: Picture Layer Syntax (Constant Bit Rate Mode)
- Next action: `REVIEW_SPEC_SCOPE` — No matching C comment evidence was found for this PDF anchor
- Related C functions: none

### `pdf:table:4-5`

- Kind/page: `table` / `61`; title: lists the Picture Layer syntax used when VBR mode is enabled.
- Next action: `REVIEW_SPEC_SCOPE` — No matching C comment evidence was found for this PDF anchor
- Related C functions: none

### `pdf:table:4-6`

- Kind/page: `table` / `63`; title: lists the Slice Layer syntax. Table 4-7 describes each Slice Layer syntax field.
- Next action: `REVIEW_SPEC_SCOPE` — No matching C comment evidence was found for this PDF anchor
- Related C functions: none

### `pdf:table:4-7`

- Kind/page: `table` / `64`; title: Slice Layer Syntax Field Descriptions
- Next action: `REVIEW_SPEC_SCOPE` — No matching C comment evidence was found for this PDF anchor
- Related C functions: none

### `pdf:table:4-8`

- Kind/page: `table` / `65`; title: lists the Y Substream Layer syntax. Table 4-9 lists the Y_syntax_element() syntax.
- Next action: `REVIEW_SPEC_SCOPE` — No matching C comment evidence was found for this PDF anchor
- Related C functions: none

### `pdf:table:4-9`

- Kind/page: `table` / `65`; title: Y_syntax_element() Syntax
- Next action: `REVIEW_SPEC_SCOPE` — No matching C comment evidence was found for this PDF anchor
- Related C functions: none

### `pdf:table:5-1`

- Kind/page: `table` / `73`; title: Recommended Capability Parameter Set
- Next action: `REVIEW_SPEC_SCOPE` — No matching C comment evidence was found for this PDF anchor
- Related C functions: none

### `pdf:table:6-1`

- Kind/page: `table` / `93`; title: summarizes the prefix codebooks for P- and ICH-modes.
- Next action: `REVIEW_SPEC_SCOPE` — No matching C comment evidence was found for this PDF anchor
- Related C functions: none

### `pdf:table:A-1`

- Kind/page: `table` / `122`; title: .DSC File Format
- Next action: `REVIEW_SPEC_SCOPE` — No matching C comment evidence was found for this PDF anchor
- Related C functions: none

### `pdf:table:E-1`

- Kind/page: `table` / `129`; title: lists intermediate RC parameter values that are useful to compute.
- Next action: `REVIEW_SPEC_SCOPE` — No matching C comment evidence was found for this PDF anchor
- Related C functions: none

### `pdf:table:E-2`

- Kind/page: `table` / `130`; title: lists recommended and required PPS syntax element rate control values.
- Next action: `REVIEW_SPEC_SCOPE` — No matching C comment evidence was found for this PDF anchor
- Related C functions: none

### `pdf:table:E-3`

- Kind/page: `table` / `131`; title: Recommended Alternative Slice Dimensions to Prevent scale_increment_interval
- Next action: `REVIEW_SPEC_SCOPE` — No matching C comment evidence was found for this PDF anchor
- Related C functions: none

### `pdf:table:E-4`

- Kind/page: `table` / `131`; title: rc_parameter_set Syntax Elements Typically Constant across Operating Modes
- Next action: `REVIEW_SPEC_SCOPE` — No matching C comment evidence was found for this PDF anchor
- Related C functions: none

### `pdf:table:E-5`

- Kind/page: `table` / `132`; title: Common Recommended Rate Control-Related Parameter Valuesa
- Next action: `REVIEW_SPEC_SCOPE` — No matching C comment evidence was found for this PDF anchor
- Related C functions: none

### `pdf:table:H-1`

- Kind/page: `table` / `144`; title: Main Contributor History (Previous Versions)
- Next action: `REVIEW_SPEC_SCOPE` — No matching C comment evidence was found for this PDF anchor
- Related C functions: none
