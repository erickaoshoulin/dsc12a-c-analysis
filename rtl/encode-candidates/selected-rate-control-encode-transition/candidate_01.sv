module removebitsencoderbuffer_decode_transition(
    input logic signed [31:0] cfg_bits_per_pixel,
    input logic signed [31:0] cfg_chunk_size,
    input logic signed [31:0] cfg_vbr_enable,
    input logic signed [31:0] state_bitsclamped,
    input logic signed [31:0] state_bpgfracaccum,
    input logic signed [31:0] state_bufferfullness,
    input logic signed [31:0] state_chunkcount,
    input logic signed [31:0] state_chunkpixeltimes,
    input logic signed [31:0] state_isencoder,
    input logic signed [31:0] state_numbitschunk,
    input logic signed [31:0] state_slicewidth,
    output logic signed [31:0] state_bitsclamped_out,
    output logic signed [31:0] state_bpgfracaccum_out,
    output logic signed [31:0] state_bufferfullness_out,
    output logic signed [31:0] state_chunkcount_out,
    output logic signed [31:0] state_chunkpixeltimes_out,
    output logic signed [31:0] state_numbitschunk_out,
    output logic chunk_write_enable,
    output logic signed [31:0] chunk_write_index,
    output logic signed [31:0] chunk_write_value
);
    logic signed [31:0] removal_bits_i;
    logic signed [31:0] size_i;
    logic signed [31:0] adjustment_bits_i;

    always_comb begin
        state_bitsclamped_out = state_bitsclamped;
        state_bpgfracaccum_out = state_bpgfracaccum;
        state_bufferfullness_out = state_bufferfullness;
        state_chunkcount_out = state_chunkcount;
        state_chunkpixeltimes_out = state_chunkpixeltimes;
        state_numbitschunk_out = state_numbitschunk;
        chunk_write_enable = 1'b0;
        chunk_write_index = state_chunkcount;
        chunk_write_value = 32'sd0;
        removal_bits_i = 32'sd0;
        size_i = 32'sd0;
        adjustment_bits_i = 32'sd0;
        state_bpgfracaccum_out = state_bpgfracaccum + (cfg_bits_per_pixel & 32'sd15);
        removal_bits_i = (cfg_bits_per_pixel >>> 4) + (state_bpgfracaccum_out >>> 4);
        state_bufferfullness_out = state_bufferfullness - removal_bits_i;
        state_numbitschunk_out = state_numbitschunk + removal_bits_i;
        state_bpgfracaccum_out = state_bpgfracaccum_out & 32'sd15;
        state_chunkpixeltimes_out = state_chunkpixeltimes + 32'sd1;
        if (state_chunkpixeltimes_out >= state_slicewidth) begin
            if (cfg_vbr_enable != 0) begin
                size_i = (state_numbitschunk_out - state_bitsclamped + 32'sd7) / 32'sd8;
                adjustment_bits_i = size_i * 32'sd8 - (state_numbitschunk_out - state_bitsclamped);
                state_bufferfullness_out = state_bufferfullness_out - adjustment_bits_i;
                state_bitsclamped_out = 32'sd0;
                if (state_isencoder != 0) begin
                    chunk_write_enable = 1'b1;
                    chunk_write_value = size_i;
                end
            end else begin
                adjustment_bits_i = cfg_chunk_size * 32'sd8 - state_numbitschunk_out;
                state_bufferfullness_out = state_bufferfullness_out - adjustment_bits_i;
            end
            state_bpgfracaccum_out = 32'sd0;
            state_numbitschunk_out = 32'sd0;
            state_chunkcount_out = state_chunkcount + 32'sd1;
            state_chunkpixeltimes_out = 32'sd0;
        end
    end
endmodule

module ratecontrol_encode_transition(
    input logic signed [31:0] throttle_offset,
    input logic signed [31:0] bpg_offset,
    input logic signed [31:0] group_count,
    input logic signed [31:0] scale,
    input logic signed [31:0] group_size,
    input logic signed [31:0] cfg_bits_per_component,
    input logic signed [31:0] cfg_bits_per_pixel,
    input logic signed [31:0] cfg_chunk_size,
    input logic signed [31:0] cfg_dsc_version_minor,
    input logic signed [31:0] cfg_initial_xmit_delay,
    input logic signed [31:0] cfg_native_420,
    input logic signed [31:0] cfg_native_422,
    input logic signed [31:0] cfg_rc_edge_factor,
    input logic signed [31:0] cfg_rc_model_size,
    input logic signed [31:0] cfg_rc_quant_incr_limit0,
    input logic signed [31:0] cfg_rc_quant_incr_limit1,
    input logic signed [31:0] cfg_rc_tgt_offset_hi,
    input logic signed [31:0] cfg_rc_tgt_offset_lo,
    input logic signed [31:0] cfg_rcb_bits,
    input logic signed [31:0] cfg_vbr_enable,
    input logic signed [31:0] state_bitsavemode,
    input logic signed [31:0] state_bitsclamped,
    input logic signed [31:0] state_bpgfracaccum,
    input logic signed [31:0] state_bufferfullness,
    input logic signed [31:0] state_chunkcount,
    input logic signed [31:0] state_chunkpixeltimes,
    input logic signed [31:0] state_codedgroupsize,
    input logic signed [31:0] state_erroroccurred,
    input logic signed [31:0] state_firstflat,
    input logic signed [31:0] state_ichselected,
    input logic signed [31:0] state_isencoder,
    input logic signed [31:0] state_mppstate,
    input logic signed [31:0] state_numbitschunk,
    input logic signed [31:0] state_pixelcount,
    input logic signed [31:0] state_prevqp,
    input logic signed [31:0] state_prevrange,
    input logic signed [31:0] state_rcsizegroup,
    input logic signed [31:0] state_slicewidth,
    input logic signed [31:0] state_stqp,
    input logic signed [31:0] state_unitspergroup,
    input logic signed [31:0] state_vpos,
    input logic signed [31:0] state_midpoint_selected_0,
    input logic signed [31:0] state_midpoint_selected_1,
    input logic signed [31:0] state_midpoint_selected_2,
    input logic signed [31:0] state_midpoint_selected_3,
    input logic signed [31:0] state_cpnt_bit_depth_0,
    input logic signed [31:0] state_cpnt_bit_depth_1,
    input logic signed [31:0] state_predicted_size_0,
    input logic signed [31:0] state_predicted_size_1,
    input logic signed [31:0] state_predicted_size_2,
    input logic signed [31:0] state_predicted_size_3,
    input logic signed [31:0] state_rc_size_unit_0,
    input logic signed [31:0] state_rc_size_unit_1,
    input logic signed [31:0] state_rc_size_unit_2,
    input logic signed [31:0] state_rc_size_unit_3,
    input logic signed [31:0] cfg_rc_buf_thresh_0,
    input logic signed [31:0] cfg_rc_buf_thresh_1,
    input logic signed [31:0] cfg_rc_buf_thresh_2,
    input logic signed [31:0] cfg_rc_buf_thresh_3,
    input logic signed [31:0] cfg_rc_buf_thresh_4,
    input logic signed [31:0] cfg_rc_buf_thresh_5,
    input logic signed [31:0] cfg_rc_buf_thresh_6,
    input logic signed [31:0] cfg_rc_buf_thresh_7,
    input logic signed [31:0] cfg_rc_buf_thresh_8,
    input logic signed [31:0] cfg_rc_buf_thresh_9,
    input logic signed [31:0] cfg_rc_buf_thresh_10,
    input logic signed [31:0] cfg_rc_buf_thresh_11,
    input logic signed [31:0] cfg_rc_buf_thresh_12,
    input logic signed [31:0] cfg_rc_buf_thresh_13,
    input logic signed [31:0] cfg_range_min_qp_0,
    input logic signed [31:0] cfg_range_min_qp_1,
    input logic signed [31:0] cfg_range_min_qp_2,
    input logic signed [31:0] cfg_range_min_qp_3,
    input logic signed [31:0] cfg_range_min_qp_4,
    input logic signed [31:0] cfg_range_min_qp_5,
    input logic signed [31:0] cfg_range_min_qp_6,
    input logic signed [31:0] cfg_range_min_qp_7,
    input logic signed [31:0] cfg_range_min_qp_8,
    input logic signed [31:0] cfg_range_min_qp_9,
    input logic signed [31:0] cfg_range_min_qp_10,
    input logic signed [31:0] cfg_range_min_qp_11,
    input logic signed [31:0] cfg_range_min_qp_12,
    input logic signed [31:0] cfg_range_min_qp_13,
    input logic signed [31:0] cfg_range_min_qp_14,
    input logic signed [31:0] cfg_range_max_qp_0,
    input logic signed [31:0] cfg_range_max_qp_1,
    input logic signed [31:0] cfg_range_max_qp_2,
    input logic signed [31:0] cfg_range_max_qp_3,
    input logic signed [31:0] cfg_range_max_qp_4,
    input logic signed [31:0] cfg_range_max_qp_5,
    input logic signed [31:0] cfg_range_max_qp_6,
    input logic signed [31:0] cfg_range_max_qp_7,
    input logic signed [31:0] cfg_range_max_qp_8,
    input logic signed [31:0] cfg_range_max_qp_9,
    input logic signed [31:0] cfg_range_max_qp_10,
    input logic signed [31:0] cfg_range_max_qp_11,
    input logic signed [31:0] cfg_range_max_qp_12,
    input logic signed [31:0] cfg_range_max_qp_13,
    input logic signed [31:0] cfg_range_max_qp_14,
    input logic signed [31:0] cfg_range_bpg_offset_0,
    input logic signed [31:0] cfg_range_bpg_offset_1,
    input logic signed [31:0] cfg_range_bpg_offset_2,
    input logic signed [31:0] cfg_range_bpg_offset_3,
    input logic signed [31:0] cfg_range_bpg_offset_4,
    input logic signed [31:0] cfg_range_bpg_offset_5,
    input logic signed [31:0] cfg_range_bpg_offset_6,
    input logic signed [31:0] cfg_range_bpg_offset_7,
    input logic signed [31:0] cfg_range_bpg_offset_8,
    input logic signed [31:0] cfg_range_bpg_offset_9,
    input logic signed [31:0] cfg_range_bpg_offset_10,
    input logic signed [31:0] cfg_range_bpg_offset_11,
    input logic signed [31:0] cfg_range_bpg_offset_12,
    input logic signed [31:0] cfg_range_bpg_offset_13,
    input logic signed [31:0] cfg_range_bpg_offset_14,
    output logic domain_valid,
    output logic fatal_error,
    output logic [2:0] fatal_error_code,
    output logic signed [31:0] state_bitsavemode_out,
    output logic signed [31:0] state_bitsclamped_out,
    output logic signed [31:0] state_bpgfracaccum_out,
    output logic signed [31:0] state_bufferfullness_out,
    output logic signed [31:0] state_chunkcount_out,
    output logic signed [31:0] state_chunkpixeltimes_out,
    output logic signed [31:0] state_erroroccurred_out,
    output logic signed [31:0] state_mppstate_out,
    output logic signed [31:0] state_numbitschunk_out,
    output logic signed [31:0] state_pixelcount_out,
    output logic signed [31:0] state_prevqp_out,
    output logic signed [31:0] state_prevrange_out,
    output logic signed [31:0] state_rcsizegroup_out,
    output logic signed [31:0] state_stqp_out,
    output logic chunk_write_enable_0,
    output logic signed [31:0] chunk_write_index_0,
    output logic signed [31:0] chunk_write_value_0,
    output logic chunk_write_enable_1,
    output logic signed [31:0] chunk_write_index_1,
    output logic signed [31:0] chunk_write_value_1,
    output logic chunk_write_enable_2,
    output logic signed [31:0] chunk_write_index_2,
    output logic signed [31:0] chunk_write_value_2
);
    logic signed [31:0] pixelcount_stage_0_i;
    logic signed [31:0] bitsclamped_stage_0_i;
    logic signed [31:0] bpgfracaccum_stage_0_i;
    logic signed [31:0] bufferfullness_stage_0_i;
    logic signed [31:0] chunkcount_stage_0_i;
    logic signed [31:0] chunkpixeltimes_stage_0_i;
    logic signed [31:0] numbitschunk_stage_0_i;
    logic signed [31:0] pixelcount_stage_1_i;
    logic signed [31:0] bitsclamped_stage_1_i;
    logic signed [31:0] bpgfracaccum_stage_1_i;
    logic signed [31:0] bufferfullness_stage_1_i;
    logic signed [31:0] chunkcount_stage_1_i;
    logic signed [31:0] chunkpixeltimes_stage_1_i;
    logic signed [31:0] numbitschunk_stage_1_i;
    logic signed [31:0] pixelcount_stage_2_i;
    logic signed [31:0] bitsclamped_stage_2_i;
    logic signed [31:0] bpgfracaccum_stage_2_i;
    logic signed [31:0] bufferfullness_stage_2_i;
    logic signed [31:0] chunkcount_stage_2_i;
    logic signed [31:0] chunkpixeltimes_stage_2_i;
    logic signed [31:0] numbitschunk_stage_2_i;
    logic signed [31:0] pixelcount_stage_3_i;
    logic signed [31:0] bitsclamped_stage_3_i;
    logic signed [31:0] bpgfracaccum_stage_3_i;
    logic signed [31:0] bufferfullness_stage_3_i;
    logic signed [31:0] chunkcount_stage_3_i;
    logic signed [31:0] chunkpixeltimes_stage_3_i;
    logic signed [31:0] numbitschunk_stage_3_i;
    logic signed [31:0] pixelcount_after_0_i;
    logic remove_stage_0_i;
    logic signed [31:0] bitsclamped_child_0_i;
    logic signed [31:0] bpgfracaccum_child_0_i;
    logic signed [31:0] bufferfullness_child_0_i;
    logic signed [31:0] chunkcount_child_0_i;
    logic signed [31:0] chunkpixeltimes_child_0_i;
    logic signed [31:0] numbitschunk_child_0_i;
    logic chunk_write_enable_child_0_i;
    logic signed [31:0] chunk_write_index_child_0_i;
    logic signed [31:0] chunk_write_value_child_0_i;
    logic signed [31:0] pixelcount_after_1_i;
    logic remove_stage_1_i;
    logic signed [31:0] bitsclamped_child_1_i;
    logic signed [31:0] bpgfracaccum_child_1_i;
    logic signed [31:0] bufferfullness_child_1_i;
    logic signed [31:0] chunkcount_child_1_i;
    logic signed [31:0] chunkpixeltimes_child_1_i;
    logic signed [31:0] numbitschunk_child_1_i;
    logic chunk_write_enable_child_1_i;
    logic signed [31:0] chunk_write_index_child_1_i;
    logic signed [31:0] chunk_write_value_child_1_i;
    logic signed [31:0] pixelcount_after_2_i;
    logic remove_stage_2_i;
    logic signed [31:0] bitsclamped_child_2_i;
    logic signed [31:0] bpgfracaccum_child_2_i;
    logic signed [31:0] bufferfullness_child_2_i;
    logic signed [31:0] chunkcount_child_2_i;
    logic signed [31:0] chunkpixeltimes_child_2_i;
    logic signed [31:0] numbitschunk_child_2_i;
    logic chunk_write_enable_child_2_i;
    logic signed [31:0] chunk_write_index_child_2_i;
    logic signed [31:0] chunk_write_value_child_2_i;
    logic signed [31:0] throttle_i;
    logic signed [31:0] rc_model_fullness_i;
    logic signed [31:0] selected_range_i;
    logic signed [31:0] next_range_i;
    logic signed [31:0] rc_size_group_i;
    logic signed [31:0] rc_target_i;
    logic signed [31:0] min_qp_i;
    logic signed [31:0] max_qp_i;
    logic signed [31:0] target_minus_i;
    logic signed [31:0] target_plus_i;
    logic signed [31:0] increment_i;
    logic signed [31:0] bpg_i;
    logic signed [31:0] mpsel_i;
    logic signed [31:0] pred_activity_i;
    logic signed [31:0] bit_save_thresh_i;
    logic signed [31:0] previous_qp_i;
    logic signed [31:0] previous2_qp_i;
    logic signed [31:0] current_qp_i;
    logic signed [31:0] new_qp_i;
    logic overflow_avoid_i;
    logic range_found_i;
    logic arithmetic_invalid_i;
    logic signed [63:0] fullness_throttle_wide_i;
    logic signed [63:0] model_product_wide_i;
    logic signed [63:0] model_shift_wide_i;
    logic signed [63:0] bpg_product_wide_i;
    logic signed [63:0] bpg_shift_wide_i;
    logic signed [63:0] rc_size_group_wide_i;
    logic signed [63:0] increment_wide_i;

    function automatic signed [31:0] dsc_cicd_min(
        input logic signed [31:0] left_i,
        input logic signed [31:0] right_i);
        begin dsc_cicd_min = (left_i < right_i) ? left_i : right_i; end
    endfunction

    function automatic signed [31:0] dsc_cicd_max(
        input logic signed [31:0] left_i,
        input logic signed [31:0] right_i);
        begin dsc_cicd_max = (left_i > right_i) ? left_i : right_i; end
    endfunction

    function automatic signed [31:0] dsc_cicd_clamp(
        input logic signed [31:0] value_i,
        input logic signed [31:0] lower_i,
        input logic signed [31:0] upper_i);
        begin
            if (value_i < lower_i) dsc_cicd_clamp = lower_i;
            else if (value_i > upper_i) dsc_cicd_clamp = upper_i;
            else dsc_cicd_clamp = value_i;
        end
    endfunction

    assign pixelcount_stage_0_i = state_pixelcount;
    assign bitsclamped_stage_0_i = state_bitsclamped;
    assign bpgfracaccum_stage_0_i = state_bpgfracaccum;
    assign bufferfullness_stage_0_i = state_bufferfullness;
    assign chunkcount_stage_0_i = state_chunkcount;
    assign chunkpixeltimes_stage_0_i = state_chunkpixeltimes;
    assign numbitschunk_stage_0_i = state_numbitschunk;
    assign pixelcount_after_0_i = pixelcount_stage_0_i + ((group_size > 32'sd0) ? 32'sd1 : 32'sd0);
    assign remove_stage_0_i = (group_size > 32'sd0) && (pixelcount_after_0_i >= cfg_initial_xmit_delay);
    assign pixelcount_stage_1_i = pixelcount_after_0_i;
    assign bitsclamped_stage_1_i = remove_stage_0_i ? bitsclamped_child_0_i : bitsclamped_stage_0_i;
    assign bpgfracaccum_stage_1_i = remove_stage_0_i ? bpgfracaccum_child_0_i : bpgfracaccum_stage_0_i;
    assign bufferfullness_stage_1_i = remove_stage_0_i ? bufferfullness_child_0_i : bufferfullness_stage_0_i;
    assign chunkcount_stage_1_i = remove_stage_0_i ? chunkcount_child_0_i : chunkcount_stage_0_i;
    assign chunkpixeltimes_stage_1_i = remove_stage_0_i ? chunkpixeltimes_child_0_i : chunkpixeltimes_stage_0_i;
    assign numbitschunk_stage_1_i = remove_stage_0_i ? numbitschunk_child_0_i : numbitschunk_stage_0_i;
    assign pixelcount_after_1_i = pixelcount_stage_1_i + ((group_size > 32'sd1) ? 32'sd1 : 32'sd0);
    assign remove_stage_1_i = (group_size > 32'sd1) && (pixelcount_after_1_i >= cfg_initial_xmit_delay);
    assign pixelcount_stage_2_i = pixelcount_after_1_i;
    assign bitsclamped_stage_2_i = remove_stage_1_i ? bitsclamped_child_1_i : bitsclamped_stage_1_i;
    assign bpgfracaccum_stage_2_i = remove_stage_1_i ? bpgfracaccum_child_1_i : bpgfracaccum_stage_1_i;
    assign bufferfullness_stage_2_i = remove_stage_1_i ? bufferfullness_child_1_i : bufferfullness_stage_1_i;
    assign chunkcount_stage_2_i = remove_stage_1_i ? chunkcount_child_1_i : chunkcount_stage_1_i;
    assign chunkpixeltimes_stage_2_i = remove_stage_1_i ? chunkpixeltimes_child_1_i : chunkpixeltimes_stage_1_i;
    assign numbitschunk_stage_2_i = remove_stage_1_i ? numbitschunk_child_1_i : numbitschunk_stage_1_i;
    assign pixelcount_after_2_i = pixelcount_stage_2_i + ((group_size > 32'sd2) ? 32'sd1 : 32'sd0);
    assign remove_stage_2_i = (group_size > 32'sd2) && (pixelcount_after_2_i >= cfg_initial_xmit_delay);
    assign pixelcount_stage_3_i = pixelcount_after_2_i;
    assign bitsclamped_stage_3_i = remove_stage_2_i ? bitsclamped_child_2_i : bitsclamped_stage_2_i;
    assign bpgfracaccum_stage_3_i = remove_stage_2_i ? bpgfracaccum_child_2_i : bpgfracaccum_stage_2_i;
    assign bufferfullness_stage_3_i = remove_stage_2_i ? bufferfullness_child_2_i : bufferfullness_stage_2_i;
    assign chunkcount_stage_3_i = remove_stage_2_i ? chunkcount_child_2_i : chunkcount_stage_2_i;
    assign chunkpixeltimes_stage_3_i = remove_stage_2_i ? chunkpixeltimes_child_2_i : chunkpixeltimes_stage_2_i;
    assign numbitschunk_stage_3_i = remove_stage_2_i ? numbitschunk_child_2_i : numbitschunk_stage_2_i;

    removebitsencoderbuffer_decode_transition remove_stage_0(
        .cfg_bits_per_pixel(cfg_bits_per_pixel),
        .cfg_chunk_size(cfg_chunk_size),
        .cfg_vbr_enable(cfg_vbr_enable),
        .state_bitsclamped(bitsclamped_stage_0_i),
        .state_bpgfracaccum(bpgfracaccum_stage_0_i),
        .state_bufferfullness(bufferfullness_stage_0_i),
        .state_chunkcount(chunkcount_stage_0_i),
        .state_chunkpixeltimes(chunkpixeltimes_stage_0_i),
        .state_isencoder(state_isencoder),
        .state_numbitschunk(numbitschunk_stage_0_i),
        .state_slicewidth(state_slicewidth),
        .state_bitsclamped_out(bitsclamped_child_0_i),
        .state_bpgfracaccum_out(bpgfracaccum_child_0_i),
        .state_bufferfullness_out(bufferfullness_child_0_i),
        .state_chunkcount_out(chunkcount_child_0_i),
        .state_chunkpixeltimes_out(chunkpixeltimes_child_0_i),
        .state_numbitschunk_out(numbitschunk_child_0_i),
        .chunk_write_enable(chunk_write_enable_child_0_i),
        .chunk_write_index(chunk_write_index_child_0_i),
        .chunk_write_value(chunk_write_value_child_0_i)
    );

    removebitsencoderbuffer_decode_transition remove_stage_1(
        .cfg_bits_per_pixel(cfg_bits_per_pixel),
        .cfg_chunk_size(cfg_chunk_size),
        .cfg_vbr_enable(cfg_vbr_enable),
        .state_bitsclamped(bitsclamped_stage_1_i),
        .state_bpgfracaccum(bpgfracaccum_stage_1_i),
        .state_bufferfullness(bufferfullness_stage_1_i),
        .state_chunkcount(chunkcount_stage_1_i),
        .state_chunkpixeltimes(chunkpixeltimes_stage_1_i),
        .state_isencoder(state_isencoder),
        .state_numbitschunk(numbitschunk_stage_1_i),
        .state_slicewidth(state_slicewidth),
        .state_bitsclamped_out(bitsclamped_child_1_i),
        .state_bpgfracaccum_out(bpgfracaccum_child_1_i),
        .state_bufferfullness_out(bufferfullness_child_1_i),
        .state_chunkcount_out(chunkcount_child_1_i),
        .state_chunkpixeltimes_out(chunkpixeltimes_child_1_i),
        .state_numbitschunk_out(numbitschunk_child_1_i),
        .chunk_write_enable(chunk_write_enable_child_1_i),
        .chunk_write_index(chunk_write_index_child_1_i),
        .chunk_write_value(chunk_write_value_child_1_i)
    );

    removebitsencoderbuffer_decode_transition remove_stage_2(
        .cfg_bits_per_pixel(cfg_bits_per_pixel),
        .cfg_chunk_size(cfg_chunk_size),
        .cfg_vbr_enable(cfg_vbr_enable),
        .state_bitsclamped(bitsclamped_stage_2_i),
        .state_bpgfracaccum(bpgfracaccum_stage_2_i),
        .state_bufferfullness(bufferfullness_stage_2_i),
        .state_chunkcount(chunkcount_stage_2_i),
        .state_chunkpixeltimes(chunkpixeltimes_stage_2_i),
        .state_isencoder(state_isencoder),
        .state_numbitschunk(numbitschunk_stage_2_i),
        .state_slicewidth(state_slicewidth),
        .state_bitsclamped_out(bitsclamped_child_2_i),
        .state_bpgfracaccum_out(bpgfracaccum_child_2_i),
        .state_bufferfullness_out(bufferfullness_child_2_i),
        .state_chunkcount_out(chunkcount_child_2_i),
        .state_chunkpixeltimes_out(chunkpixeltimes_child_2_i),
        .state_numbitschunk_out(numbitschunk_child_2_i),
        .chunk_write_enable(chunk_write_enable_child_2_i),
        .chunk_write_index(chunk_write_index_child_2_i),
        .chunk_write_value(chunk_write_value_child_2_i)
    );

    always_comb begin
        domain_valid = 1'b1;
        fatal_error = 1'b0;
        fatal_error_code = 3'd0;
        state_bitsavemode_out = state_bitsavemode;
        state_bitsclamped_out = state_bitsclamped;
        state_bpgfracaccum_out = state_bpgfracaccum;
        state_bufferfullness_out = state_bufferfullness;
        state_chunkcount_out = state_chunkcount;
        state_chunkpixeltimes_out = state_chunkpixeltimes;
        state_erroroccurred_out = state_erroroccurred;
        state_mppstate_out = state_mppstate;
        state_numbitschunk_out = state_numbitschunk;
        state_pixelcount_out = state_pixelcount;
        state_prevqp_out = state_prevqp;
        state_prevrange_out = state_prevrange;
        state_rcsizegroup_out = state_rcsizegroup;
        state_stqp_out = state_stqp;
        chunk_write_enable_0 = 1'b0;
        chunk_write_index_0 = 32'sd0;
        chunk_write_value_0 = 32'sd0;
        chunk_write_enable_1 = 1'b0;
        chunk_write_index_1 = 32'sd0;
        chunk_write_value_1 = 32'sd0;
        chunk_write_enable_2 = 1'b0;
        chunk_write_index_2 = 32'sd0;
        chunk_write_value_2 = 32'sd0;
        arithmetic_invalid_i = 1'b0;
        fullness_throttle_wide_i = 64'sd0;
        model_product_wide_i = 64'sd0;
        model_shift_wide_i = 64'sd0;
        bpg_product_wide_i = 64'sd0;
        bpg_shift_wide_i = 64'sd0;
        rc_size_group_wide_i = 64'sd0;
        increment_wide_i = 64'sd0;
        rc_size_group_i = 32'sd0;
        throttle_i = 32'sd0;
        rc_model_fullness_i = 32'sd0;
        selected_range_i = 32'sd0;
        next_range_i = 32'sd0;
        rc_target_i = 32'sd0;
        min_qp_i = 32'sd0;
        max_qp_i = 32'sd0;
        target_minus_i = 32'sd0;
        target_plus_i = 32'sd0;
        increment_i = 32'sd0;
        bpg_i = 32'sd0;
        mpsel_i = 32'sd0;
        pred_activity_i = 32'sd0;
        bit_save_thresh_i = 32'sd0;
        previous_qp_i = state_stqp;
        previous2_qp_i = state_prevqp;
        current_qp_i = 32'sd0;
        new_qp_i = state_stqp;
        overflow_avoid_i = 1'b0;
        range_found_i = 1'b0;
        rc_size_group_wide_i = 64'sd0;
        if (state_unitspergroup > 32'sd0) rc_size_group_wide_i = rc_size_group_wide_i + $signed({{32{state_rc_size_unit_0[31]}}, state_rc_size_unit_0});
        if (state_unitspergroup > 32'sd1) rc_size_group_wide_i = rc_size_group_wide_i + $signed({{32{state_rc_size_unit_1[31]}}, state_rc_size_unit_1});
        if (state_unitspergroup > 32'sd2) rc_size_group_wide_i = rc_size_group_wide_i + $signed({{32{state_rc_size_unit_2[31]}}, state_rc_size_unit_2});
        if (state_unitspergroup > 32'sd3) rc_size_group_wide_i = rc_size_group_wide_i + $signed({{32{state_rc_size_unit_3[31]}}, state_rc_size_unit_3});
        rc_size_group_i = rc_size_group_wide_i[31:0];
        throttle_i = throttle_offset - cfg_rc_model_size;
        fullness_throttle_wide_i = $signed({{32{bufferfullness_stage_3_i[31]}}, bufferfullness_stage_3_i}) + $signed({{32{throttle_i[31]}}, throttle_i});
        model_product_wide_i = $signed({{32{scale[31]}}, scale}) * fullness_throttle_wide_i;
        model_shift_wide_i = model_product_wide_i >>> 3;
        rc_model_fullness_i = model_shift_wide_i[31:0];
        bpg_product_wide_i = $signed({{32{cfg_bits_per_pixel[31]}}, cfg_bits_per_pixel}) * $signed({{32{group_size[31]}}, group_size});
        bpg_shift_wide_i = (bpg_product_wide_i + 64'sd8) >>> 4;
        bpg_i = bpg_shift_wide_i[31:0];
        selected_range_i = state_prevrange;
        next_range_i = 32'sd0;
        range_found_i = 1'b0;
        if (!range_found_i && (rc_model_fullness_i > (cfg_rc_buf_thresh_13 - cfg_rc_model_size))) begin
            next_range_i = 32'sd14;
            range_found_i = 1'b1;
        end
        if (!range_found_i && (rc_model_fullness_i > (cfg_rc_buf_thresh_12 - cfg_rc_model_size))) begin
            next_range_i = 32'sd13;
            range_found_i = 1'b1;
        end
        if (!range_found_i && (rc_model_fullness_i > (cfg_rc_buf_thresh_11 - cfg_rc_model_size))) begin
            next_range_i = 32'sd12;
            range_found_i = 1'b1;
        end
        if (!range_found_i && (rc_model_fullness_i > (cfg_rc_buf_thresh_10 - cfg_rc_model_size))) begin
            next_range_i = 32'sd11;
            range_found_i = 1'b1;
        end
        if (!range_found_i && (rc_model_fullness_i > (cfg_rc_buf_thresh_9 - cfg_rc_model_size))) begin
            next_range_i = 32'sd10;
            range_found_i = 1'b1;
        end
        if (!range_found_i && (rc_model_fullness_i > (cfg_rc_buf_thresh_8 - cfg_rc_model_size))) begin
            next_range_i = 32'sd9;
            range_found_i = 1'b1;
        end
        if (!range_found_i && (rc_model_fullness_i > (cfg_rc_buf_thresh_7 - cfg_rc_model_size))) begin
            next_range_i = 32'sd8;
            range_found_i = 1'b1;
        end
        if (!range_found_i && (rc_model_fullness_i > (cfg_rc_buf_thresh_6 - cfg_rc_model_size))) begin
            next_range_i = 32'sd7;
            range_found_i = 1'b1;
        end
        if (!range_found_i && (rc_model_fullness_i > (cfg_rc_buf_thresh_5 - cfg_rc_model_size))) begin
            next_range_i = 32'sd6;
            range_found_i = 1'b1;
        end
        if (!range_found_i && (rc_model_fullness_i > (cfg_rc_buf_thresh_4 - cfg_rc_model_size))) begin
            next_range_i = 32'sd5;
            range_found_i = 1'b1;
        end
        if (!range_found_i && (rc_model_fullness_i > (cfg_rc_buf_thresh_3 - cfg_rc_model_size))) begin
            next_range_i = 32'sd4;
            range_found_i = 1'b1;
        end
        if (!range_found_i && (rc_model_fullness_i > (cfg_rc_buf_thresh_2 - cfg_rc_model_size))) begin
            next_range_i = 32'sd3;
            range_found_i = 1'b1;
        end
        if (!range_found_i && (rc_model_fullness_i > (cfg_rc_buf_thresh_1 - cfg_rc_model_size))) begin
            next_range_i = 32'sd2;
            range_found_i = 1'b1;
        end
        if (!range_found_i && (rc_model_fullness_i > (cfg_rc_buf_thresh_0 - cfg_rc_model_size))) begin
            next_range_i = 32'sd1;
            range_found_i = 1'b1;
        end
        overflow_avoid_i = (fullness_throttle_wide_i > ((cfg_native_422 != 0) ? -64'sd224 : -64'sd172));
        rc_target_i = dsc_cicd_max(32'sd0, bpg_i + ((selected_range_i == 32'sd0) ? cfg_range_bpg_offset_0 : ((selected_range_i == 32'sd1) ? cfg_range_bpg_offset_1 : ((selected_range_i == 32'sd2) ? cfg_range_bpg_offset_2 : ((selected_range_i == 32'sd3) ? cfg_range_bpg_offset_3 : ((selected_range_i == 32'sd4) ? cfg_range_bpg_offset_4 : ((selected_range_i == 32'sd5) ? cfg_range_bpg_offset_5 : ((selected_range_i == 32'sd6) ? cfg_range_bpg_offset_6 : ((selected_range_i == 32'sd7) ? cfg_range_bpg_offset_7 : ((selected_range_i == 32'sd8) ? cfg_range_bpg_offset_8 : ((selected_range_i == 32'sd9) ? cfg_range_bpg_offset_9 : ((selected_range_i == 32'sd10) ? cfg_range_bpg_offset_10 : ((selected_range_i == 32'sd11) ? cfg_range_bpg_offset_11 : ((selected_range_i == 32'sd12) ? cfg_range_bpg_offset_12 : ((selected_range_i == 32'sd13) ? cfg_range_bpg_offset_13 : cfg_range_bpg_offset_14)))))))))))))) + bpg_offset);
        min_qp_i = ((selected_range_i == 32'sd0) ? cfg_range_min_qp_0 : ((selected_range_i == 32'sd1) ? cfg_range_min_qp_1 : ((selected_range_i == 32'sd2) ? cfg_range_min_qp_2 : ((selected_range_i == 32'sd3) ? cfg_range_min_qp_3 : ((selected_range_i == 32'sd4) ? cfg_range_min_qp_4 : ((selected_range_i == 32'sd5) ? cfg_range_min_qp_5 : ((selected_range_i == 32'sd6) ? cfg_range_min_qp_6 : ((selected_range_i == 32'sd7) ? cfg_range_min_qp_7 : ((selected_range_i == 32'sd8) ? cfg_range_min_qp_8 : ((selected_range_i == 32'sd9) ? cfg_range_min_qp_9 : ((selected_range_i == 32'sd10) ? cfg_range_min_qp_10 : ((selected_range_i == 32'sd11) ? cfg_range_min_qp_11 : ((selected_range_i == 32'sd12) ? cfg_range_min_qp_12 : ((selected_range_i == 32'sd13) ? cfg_range_min_qp_13 : cfg_range_min_qp_14))))))))))))));
        max_qp_i = ((selected_range_i == 32'sd0) ? cfg_range_max_qp_0 : ((selected_range_i == 32'sd1) ? cfg_range_max_qp_1 : ((selected_range_i == 32'sd2) ? cfg_range_max_qp_2 : ((selected_range_i == 32'sd3) ? cfg_range_max_qp_3 : ((selected_range_i == 32'sd4) ? cfg_range_max_qp_4 : ((selected_range_i == 32'sd5) ? cfg_range_max_qp_5 : ((selected_range_i == 32'sd6) ? cfg_range_max_qp_6 : ((selected_range_i == 32'sd7) ? cfg_range_max_qp_7 : ((selected_range_i == 32'sd8) ? cfg_range_max_qp_8 : ((selected_range_i == 32'sd9) ? cfg_range_max_qp_9 : ((selected_range_i == 32'sd10) ? cfg_range_max_qp_10 : ((selected_range_i == 32'sd11) ? cfg_range_max_qp_11 : ((selected_range_i == 32'sd12) ? cfg_range_max_qp_12 : ((selected_range_i == 32'sd13) ? cfg_range_max_qp_13 : cfg_range_max_qp_14))))))))))))));
        target_minus_i = dsc_cicd_max(32'sd0, rc_target_i - cfg_rc_tgt_offset_lo);
        target_plus_i = dsc_cicd_max(32'sd0, rc_target_i + cfg_rc_tgt_offset_hi);
        increment_wide_i = ($signed({{32{state_codedgroupsize[31]}}, state_codedgroupsize}) - $signed({{32{rc_target_i[31]}}, rc_target_i})) >>> 1;
        increment_i = increment_wide_i[31:0];
        mpsel_i = state_midpoint_selected_0 + state_midpoint_selected_1 + state_midpoint_selected_2 + state_midpoint_selected_3;
        if (cfg_native_420 != 0) pred_activity_i = state_prevqp + dsc_cicd_max(state_predicted_size_0, state_predicted_size_1) + state_predicted_size_2;
        else if (cfg_native_422 == 0) pred_activity_i = state_prevqp + state_predicted_size_0 + dsc_cicd_max(state_predicted_size_1, state_predicted_size_2);
        else pred_activity_i = state_prevqp + ((state_predicted_size_0 + state_predicted_size_3 + state_predicted_size_1 + state_predicted_size_2) >>> 1);
        bit_save_thresh_i = state_cpnt_bit_depth_0 + state_cpnt_bit_depth_1 - 32'sd2;
        if ((cfg_dsc_version_minor == 32'sd2) && (state_vpos > 32'sd0) && (state_firstflat == -32'sd1)) begin
            if ((state_ichselected == 32'sd0) && (mpsel_i >= 32'sd3)) begin
                state_mppstate_out = state_mppstate + 32'sd1;
                if (state_mppstate_out >= 32'sd2) state_bitsavemode_out = 32'sd2;
            end
            else if ((state_ichselected == 32'sd0) && (pred_activity_i >= bit_save_thresh_i)) begin end
            else if (state_ichselected != 32'sd0) state_bitsavemode_out = dsc_cicd_max(32'sd1, state_bitsavemode_out);
            else begin
                state_mppstate_out = 32'sd0;
                state_bitsavemode_out = 32'sd0;
            end
        end else begin
            state_bitsavemode_out = 32'sd0;
            state_mppstate_out = 32'sd0;
        end
        if ((cfg_dsc_version_minor == 32'sd2) && (bufferfullness_stage_3_i < 32'sd192)) new_qp_i = min_qp_i;
        else if (state_bitsavemode_out != 32'sd0) begin
            max_qp_i = dsc_cicd_min((cfg_bits_per_component * 32'sd2) - 32'sd1, max_qp_i + 32'sd1);
            if (state_bitsavemode_out == 32'sd1) new_qp_i = previous_qp_i;
            else new_qp_i = previous_qp_i + 32'sd2;
        end else if (rc_size_group_i == state_unitspergroup) begin
            if (cfg_dsc_version_minor == 32'sd2) begin
                min_qp_i = dsc_cicd_max(min_qp_i - 32'sd4, 32'sd0);
                new_qp_i = previous_qp_i - 32'sd1;
            end else new_qp_i = dsc_cicd_max(min_qp_i / 32'sd2, previous_qp_i - 32'sd1);
        end
        else if (((cfg_dsc_version_minor == 32'sd1) && (state_codedgroupsize < target_minus_i) && (rc_size_group_i < target_minus_i)) ||
                 ((cfg_dsc_version_minor == 32'sd2) && (rc_size_group_i < target_minus_i))) begin
            if (cfg_dsc_version_minor == 32'sd2) new_qp_i = previous_qp_i - 32'sd1;
            else new_qp_i = dsc_cicd_max(min_qp_i, previous_qp_i - 32'sd1);
        end
        else if ((bufferfullness_stage_3_i >= 32'sd64) && (state_codedgroupsize > target_plus_i)) begin
            current_qp_i = dsc_cicd_max(previous_qp_i, min_qp_i);
            if (previous2_qp_i == current_qp_i) begin
                if ((rc_size_group_i * 32'sd2) < (state_rcsizegroup * cfg_rc_edge_factor)) begin
                    if (cfg_dsc_version_minor == 32'sd2) new_qp_i = current_qp_i + increment_i;
                    else new_qp_i = dsc_cicd_min(max_qp_i, current_qp_i + increment_i);
                end else new_qp_i = current_qp_i;
            end else if (previous2_qp_i < current_qp_i) begin
                if (((rc_size_group_i * 32'sd2) < (state_rcsizegroup * cfg_rc_edge_factor)) && (current_qp_i < cfg_rc_quant_incr_limit0)) begin
                    if (cfg_dsc_version_minor == 32'sd2) new_qp_i = current_qp_i + increment_i;
                    else new_qp_i = dsc_cicd_min(max_qp_i, current_qp_i + increment_i);
                end else new_qp_i = current_qp_i;
            end else if (current_qp_i < cfg_rc_quant_incr_limit1) begin
                if (cfg_dsc_version_minor == 32'sd2) new_qp_i = current_qp_i + increment_i;
                else new_qp_i = dsc_cicd_min(max_qp_i, current_qp_i + increment_i);
            end else new_qp_i = current_qp_i;
        end else new_qp_i = previous_qp_i;
        if (cfg_dsc_version_minor == 32'sd2) new_qp_i = dsc_cicd_clamp(new_qp_i, min_qp_i, max_qp_i);
        if (overflow_avoid_i) new_qp_i = cfg_range_max_qp_14;
        state_bitsavemode_out = state_bitsavemode_out;
        state_erroroccurred_out = state_erroroccurred;
        state_prevqp_out = previous_qp_i;
        state_prevrange_out = next_range_i;
        state_rcsizegroup_out = rc_size_group_i;
        state_stqp_out = new_qp_i;
        if ((rc_size_group_wide_i > 64'sd2147483647) || (rc_size_group_wide_i < -64'sd2147483648) ||
            (fullness_throttle_wide_i > 64'sd2147483647) || (fullness_throttle_wide_i < -64'sd2147483648) ||
            (model_shift_wide_i > 64'sd2147483647) || (model_shift_wide_i < -64'sd2147483648) ||
            (bpg_shift_wide_i > 64'sd2147483647) || (bpg_shift_wide_i < -64'sd2147483648) ||
            (increment_wide_i > 64'sd2147483647) || (increment_wide_i < -64'sd2147483648))
            arithmetic_invalid_i = 1'b1;
        if ((state_isencoder != 32'sd1) || (group_size < 32'sd1) || (group_size > 32'sd3) || (state_unitspergroup < 32'sd3) || (state_unitspergroup > 32'sd4) || (state_prevrange < 32'sd0) || (state_prevrange >= 32'sd15) || (state_slicewidth <= 32'sd0) || (state_chunkpixeltimes < 32'sd0) || (state_chunkpixeltimes >= state_slicewidth) || (cfg_dsc_version_minor < 32'sd1) || (cfg_dsc_version_minor > 32'sd2) || ((cfg_native_420 != 32'sd0) && (cfg_native_420 != 32'sd1)) || ((cfg_native_422 != 32'sd0) && (cfg_native_422 != 32'sd1)) || ((cfg_native_420 != 32'sd0) && (cfg_native_422 != 32'sd0)) || (cfg_vbr_enable < 32'sd0) || (cfg_vbr_enable > 32'sd1) || (cfg_initial_xmit_delay < 32'sd0) || (state_cpnt_bit_depth_0 < 32'sd8) || (state_cpnt_bit_depth_0 > 32'sd16) || (state_cpnt_bit_depth_1 < 32'sd8) || (state_cpnt_bit_depth_1 > 32'sd16)) begin
            domain_valid = 1'b0;
            fatal_error = 1'b1;
            fatal_error_code = 3'd1;
        end
        if (arithmetic_invalid_i && (domain_valid != 1'b0)) begin
            fatal_error = 1'b1;
            fatal_error_code = 3'd4;
        end
        if ((domain_valid != 1'b0) && !arithmetic_invalid_i && (rc_model_fullness_i > 32'sd0)) begin
            fatal_error = 1'b1;
            fatal_error_code = 3'd2;
        end
        else if ((domain_valid != 1'b0) && !arithmetic_invalid_i && (bufferfullness_stage_3_i > cfg_rcb_bits)) begin
            fatal_error = 1'b1;
            fatal_error_code = 3'd3;
        end
        if ((domain_valid != 1'b0) && (fatal_error == 1'b0)) begin
            state_bitsclamped_out = bitsclamped_stage_3_i;
            state_bpgfracaccum_out = bpgfracaccum_stage_3_i;
            state_bufferfullness_out = bufferfullness_stage_3_i;
            state_chunkcount_out = chunkcount_stage_3_i;
            state_chunkpixeltimes_out = chunkpixeltimes_stage_3_i;
            state_numbitschunk_out = numbitschunk_stage_3_i;
            state_pixelcount_out = pixelcount_stage_3_i;
            chunk_write_enable_0 = remove_stage_0_i && chunk_write_enable_child_0_i;
            chunk_write_index_0 = chunk_write_index_child_0_i;
            chunk_write_value_0 = chunk_write_value_child_0_i;
            chunk_write_enable_1 = remove_stage_1_i && chunk_write_enable_child_1_i;
            chunk_write_index_1 = chunk_write_index_child_1_i;
            chunk_write_value_1 = chunk_write_value_child_1_i;
            chunk_write_enable_2 = remove_stage_2_i && chunk_write_enable_child_2_i;
            chunk_write_index_2 = chunk_write_index_child_2_i;
            chunk_write_value_2 = chunk_write_value_child_2_i;
        end
        if ((domain_valid == 1'b0) || (fatal_error != 1'b0)) begin
            state_bitsavemode_out = state_bitsavemode;
            state_bitsclamped_out = state_bitsclamped;
            state_bpgfracaccum_out = state_bpgfracaccum;
            state_bufferfullness_out = state_bufferfullness;
            state_chunkcount_out = state_chunkcount;
            state_chunkpixeltimes_out = state_chunkpixeltimes;
            state_erroroccurred_out = state_erroroccurred;
            state_mppstate_out = state_mppstate;
            state_numbitschunk_out = state_numbitschunk;
            state_pixelcount_out = state_pixelcount;
            state_prevqp_out = state_prevqp;
            state_prevrange_out = state_prevrange;
            state_rcsizegroup_out = state_rcsizegroup;
            state_stqp_out = state_stqp;
            chunk_write_enable_0 = 1'b0;
            chunk_write_index_0 = 32'sd0;
            chunk_write_value_0 = 32'sd0;
            chunk_write_enable_1 = 1'b0;
            chunk_write_index_1 = 32'sd0;
            chunk_write_value_1 = 32'sd0;
            chunk_write_enable_2 = 1'b0;
            chunk_write_index_2 = 32'sd0;
            chunk_write_value_2 = 32'sd0;
        end
    end
endmodule
