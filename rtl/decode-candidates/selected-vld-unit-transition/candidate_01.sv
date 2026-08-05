module getqpadjpredsize (
    input logic [1:0] unit,
    input logic [1:0] dsc_version_minor,
    input logic native_420,
    input logic [1:0] unit_c_type_selected,
    input logic [4:0] predicted_size_selected,
    input logic [4:0] primary_qp,
    input logic [4:0] prev_primary_qp,
    input logic [4:0] cpntBitDepth_0,
    input logic [4:0] cpntBitDepth_1,
    input logic [4:0] cpntBitDepth_2,
    input logic [4:0] cpntBitDepth_3,
    input logic [4:0] qlevel_luma_new,
    input logic [4:0] qlevel_chroma_new,
    input logic [4:0] qlevel_luma_old,
    input logic [4:0] qlevel_chroma_old,
    output logic signed [4:0] return_value
);
    integer signed cpnt_i;
    integer signed bit_depth_i;
    integer signed qlevel_new_i;
    integer signed qlevel_old_i;
    integer signed pred_size_i;
    integer signed max_size_i;
    always_comb begin
        cpnt_i = unit_c_type_selected;
        case (cpnt_i)
            0: bit_depth_i = cpntBitDepth_0;
            1: bit_depth_i = cpntBitDepth_1;
            2: bit_depth_i = cpntBitDepth_2;
            3: bit_depth_i = cpntBitDepth_3;
            default: bit_depth_i = cpntBitDepth_0;
        endcase
        if ((cpnt_i % 3) == 0) begin
            qlevel_new_i = qlevel_luma_new;
        end else if ((native_420 != 0) && (cpnt_i == 1)) begin
            qlevel_new_i = qlevel_luma_new;
        end else begin
            qlevel_new_i = qlevel_chroma_new;
            if ((dsc_version_minor == 2) && (cpntBitDepth_0 == cpntBitDepth_1) && (qlevel_new_i > 0)) begin
                qlevel_new_i = qlevel_new_i - 1;
            end
        end
        if ((cpnt_i % 3) == 0) begin
            qlevel_old_i = qlevel_luma_old;
        end else if ((native_420 != 0) && (cpnt_i == 1)) begin
            qlevel_old_i = qlevel_luma_old;
        end else begin
            qlevel_old_i = qlevel_chroma_old;
            if ((dsc_version_minor == 2) && (cpntBitDepth_0 == cpntBitDepth_1) && (qlevel_old_i > 0)) begin
                qlevel_old_i = qlevel_old_i - 1;
            end
        end
        pred_size_i = predicted_size_selected + qlevel_old_i - qlevel_new_i;
        max_size_i = bit_depth_i - qlevel_new_i;
        if (pred_size_i < 0) pred_size_i = 0;
        else if (pred_size_i > (max_size_i - 1)) pred_size_i = max_size_i - 1;
        return_value = pred_size_i;
    end
endmodule

module escapecodesize (
    input logic [4:0] qp,
    input logic [1:0] dsc_version_minor,
    input logic native_420,
    input logic [4:0] cpntBitDepth_0,
    input logic [4:0] qlevel_luma,
    output logic signed [5:0] return_value
);
    assign return_value = (cpntBitDepth_0 + 1 - qlevel_luma);
endmodule

module isflatnessinfosent (
    input logic [4:0] qp,
    input logic [4:0] flatness_min_qp,
    input logic [4:0] flatness_max_qp,
    output logic return_value
);
    assign return_value = ((qp >= flatness_min_qp) && (qp <= flatness_max_qp));
endmodule

module maxresidualsize (
    input logic [1:0] cpnt,
    input logic [4:0] qp,
    input logic [1:0] dsc_version_minor,
    input logic native_420,
    input logic [4:0] cpntBitDepth_0,
    input logic [4:0] cpntBitDepth_1,
    input logic [4:0] cpntBitDepth_selected,
    input logic [4:0] qlevel_luma,
    input logic [4:0] qlevel_chroma,
    output logic signed [5:0] return_value
);
    integer signed qlevel_i;
    integer signed chroma_i;
    integer signed max_size_i;
    always_comb begin
        max_size_i = cpntBitDepth_selected;
        if ((cpnt % 3) == 0) begin
            qlevel_i = qlevel_luma;
        end else if ((native_420 != 0) && (cpnt == 1)) begin
            qlevel_i = qlevel_luma;
        end else begin
            chroma_i = qlevel_chroma;
            if ((dsc_version_minor == 2) && (cpntBitDepth_0 == ((cpnt == 1) ? cpntBitDepth_selected : cpntBitDepth_1))) begin
                chroma_i = chroma_i - 1;
            end
            qlevel_i = chroma_i < 0 ? 0 : chroma_i;
        end
        max_size_i = max_size_i - qlevel_i;
        return_value = max_size_i;
    end
endmodule

module predictsize (
    input logic [4:0] req_size_0,
    input logic [4:0] req_size_1,
    input logic [4:0] req_size_2,
    output logic [4:0] return_value
);
    assign return_value = ((req_size_0 + req_size_1 + (2 * req_size_2) + 2) >> 2);
endmodule

module mapqptoqlevel (
    input logic [1:0] cpnt,
    input logic [4:0] qp,
    input logic [1:0] dsc_version_minor,
    input logic native_420,
    input logic [4:0] cpntBitDepth_0,
    input logic [4:0] cpntBitDepth_1,
    input logic [4:0] qlevel_luma,
    input logic [4:0] qlevel_chroma,
    output logic [4:0] return_value
);
    integer signed qlevel_i;
    always_comb begin
        if ((cpnt % 3) == 0) begin
            qlevel_i = qlevel_luma;
        end else if ((native_420 != 0) && (cpnt == 1)) begin
            qlevel_i = qlevel_luma;
        end else begin
            qlevel_i = qlevel_chroma;
            if ((dsc_version_minor == 2) && (cpntBitDepth_0 == cpntBitDepth_1) && (qlevel_i > 0)) begin
                qlevel_i = qlevel_i - 1;
            end
        end
        return_value = qlevel_i;
    end
endmodule

module findresidualsize (
    input logic signed [16:0] eq,
    output logic [4:0] return_value
);
    integer signed eq_i;
    always_comb begin
        eq_i = $signed({{15{eq[16]}}, eq});
        return_value = 0;
        if (eq_i == 0) return_value = 0;
        else if ((eq_i >= -1) && (eq_i <= 0)) return_value = 1;
        else if ((eq_i >= -2) && (eq_i <= 1)) return_value = 2;
        else if ((eq_i >= -4) && (eq_i <= 3)) return_value = 3;
        else if ((eq_i >= -8) && (eq_i <= 7)) return_value = 4;
        else if ((eq_i >= -16) && (eq_i <= 15)) return_value = 5;
        else if ((eq_i >= -32) && (eq_i <= 31)) return_value = 6;
        else if ((eq_i >= -64) && (eq_i <= 63)) return_value = 7;
        else if ((eq_i >= -128) && (eq_i <= 127)) return_value = 8;
        else if ((eq_i >= -256) && (eq_i <= 255)) return_value = 9;
        else if ((eq_i >= -512) && (eq_i <= 511)) return_value = 10;
        else if ((eq_i >= -1024) && (eq_i <= 1023)) return_value = 11;
        else if ((eq_i >= -2048) && (eq_i <= 2047)) return_value = 12;
        else if ((eq_i >= -4096) && (eq_i <= 4095)) return_value = 13;
        else if ((eq_i >= -8192) && (eq_i <= 8191)) return_value = 14;
        else if ((eq_i >= -16384) && (eq_i <= 16383)) return_value = 15;
        else if ((eq_i >= -32768) && (eq_i <= 32767)) return_value = 16;
        else if ((eq_i >= -65536) && (eq_i <= 65535)) return_value = 17;
        else if ((eq_i >= -131702) && (eq_i <= 131701)) return_value = 18;
    end
endmodule

module vldunit_decode_transition(
    input logic signed [31:0] unit,
    input logic signed [31:0] cfg_bits_per_component,
    input logic signed [31:0] cfg_somewhat_flat_qp_thresh,
    input logic signed [31:0] cfg_dsc_version_minor,
    input logic signed [31:0] cfg_native_420,
    input logic signed [31:0] cfg_flatness_min_qp,
    input logic signed [31:0] cfg_flatness_max_qp,
    input logic signed [31:0] state_firstflat,
    input logic signed [31:0] state_flatnesstype,
    input logic signed [31:0] state_groupcount,
    input logic signed [31:0] state_ichindicesingroup,
    input logic signed [31:0] state_ichselected,
    input logic signed [31:0] state_prevfirstflat,
    input logic signed [31:0] state_previchselected,
    input logic signed [31:0] state_primaryqp,
    input logic signed [31:0] state_prevprimaryqp,
    input logic signed [31:0] state_unitspergroup,
    input logic signed [31:0] state_numbits,
    input logic signed [31:0] state_cpntbitdepth_0,
    input logic signed [31:0] state_cpntbitdepth_1,
    input logic signed [31:0] state_cpntbitdepth_2,
    input logic signed [31:0] state_cpntbitdepth_3,
    input logic signed [31:0] state_unitctype_0,
    input logic signed [31:0] state_unitctype_1,
    input logic signed [31:0] state_unitctype_2,
    input logic signed [31:0] state_unitctype_3,
    input logic signed [31:0] state_unitsspmap_0,
    input logic signed [31:0] state_unitsspmap_1,
    input logic signed [31:0] state_unitsspmap_2,
    input logic signed [31:0] state_unitsspmap_3,
    input logic signed [31:0] state_ichindexunitmap_0,
    input logic signed [31:0] state_ichindexunitmap_1,
    input logic signed [31:0] state_ichindexunitmap_2,
    input logic signed [31:0] state_ichindexunitmap_3,
    input logic signed [31:0] state_ichindexunitmap_4,
    input logic signed [31:0] state_ichindexunitmap_5,
    input logic signed [31:0] state_ichlookup_0,
    input logic signed [31:0] state_ichlookup_1,
    input logic signed [31:0] state_ichlookup_2,
    input logic signed [31:0] state_ichlookup_3,
    input logic signed [31:0] state_ichlookup_4,
    input logic signed [31:0] state_ichlookup_5,
    input logic signed [31:0] state_predictedsize_0,
    input logic signed [31:0] state_predictedsize_1,
    input logic signed [31:0] state_predictedsize_2,
    input logic signed [31:0] state_predictedsize_3,
    input logic signed [31:0] state_rcsizeunit_0,
    input logic signed [31:0] state_rcsizeunit_1,
    input logic signed [31:0] state_rcsizeunit_2,
    input logic signed [31:0] state_rcsizeunit_3,
    input logic signed [31:0] state_usemidpoint_0,
    input logic signed [31:0] state_usemidpoint_1,
    input logic signed [31:0] state_usemidpoint_2,
    input logic signed [31:0] state_usemidpoint_3,
    input logic signed [31:0] qlevel_luma_primary,
    input logic signed [31:0] qlevel_chroma_primary,
    input logic signed [31:0] qlevel_luma_previous,
    input logic signed [31:0] qlevel_chroma_previous,
    input logic signed [31:0] quantized_residual_0,
    input logic signed [31:0] quantized_residual_1,
    input logic signed [31:0] quantized_residual_2,
    input logic signed [31:0] fifo_size,
    input logic signed [31:0] fifo_fullness,
    input logic signed [31:0] fifo_read_ptr,
    input logic [7:0] fifo_byte_0,
    input logic [7:0] fifo_byte_1,
    input logic [7:0] fifo_byte_2,
    input logic [7:0] fifo_byte_3,
    input logic [7:0] fifo_byte_4,
    input logic [7:0] fifo_byte_5,
    input logic [7:0] fifo_byte_6,
    input logic [7:0] fifo_byte_7,
    input logic [7:0] fifo_byte_8,
    input logic [7:0] fifo_byte_9,
    input logic [7:0] fifo_byte_10,
    input logic [7:0] fifo_byte_11,
    input logic [7:0] fifo_byte_12,
    input logic [7:0] fifo_byte_13,
    input logic [7:0] fifo_byte_14,
    input logic [7:0] fifo_byte_15,
    input logic [7:0] fifo_byte_16,
    output logic domain_valid,
    output logic signed [31:0] state_firstflat_out,
    output logic signed [31:0] state_flatnesstype_out,
    output logic signed [31:0] state_ichselected_out,
    output logic signed [31:0] state_prevfirstflat_out,
    output logic signed [31:0] state_previchselected_out,
    output logic signed [31:0] state_numbits_out,
    output logic signed [31:0] state_ichlookup_0_out,
    output logic signed [31:0] state_ichlookup_1_out,
    output logic signed [31:0] state_ichlookup_2_out,
    output logic signed [31:0] state_ichlookup_3_out,
    output logic signed [31:0] state_ichlookup_4_out,
    output logic signed [31:0] state_ichlookup_5_out,
    output logic signed [31:0] state_predictedsize_0_out,
    output logic signed [31:0] state_predictedsize_1_out,
    output logic signed [31:0] state_predictedsize_2_out,
    output logic signed [31:0] state_predictedsize_3_out,
    output logic signed [31:0] state_rcsizeunit_0_out,
    output logic signed [31:0] state_rcsizeunit_1_out,
    output logic signed [31:0] state_rcsizeunit_2_out,
    output logic signed [31:0] state_rcsizeunit_3_out,
    output logic signed [31:0] state_usemidpoint_0_out,
    output logic signed [31:0] state_usemidpoint_1_out,
    output logic signed [31:0] state_usemidpoint_2_out,
    output logic signed [31:0] state_usemidpoint_3_out,
    output logic signed [31:0] quantized_residual_0_out,
    output logic signed [31:0] quantized_residual_1_out,
    output logic signed [31:0] quantized_residual_2_out,
    output logic signed [31:0] fifo_lane_out,
    output logic signed [31:0] fifo_fullness_out,
    output logic signed [31:0] fifo_read_ptr_out
);
    logic signed [31:0] cpnt_i;
    logic signed [31:0] ssp_i;
    logic signed [31:0] predicted_selected_i;
    logic signed [31:0] depth_selected_i;
    logic signed [31:0] qlevel_i;
    logic signed [31:0] adj_predicted_i;
    logic signed [31:0] max_prefix_i;
    logic signed [31:0] prefix_limit_i;
    logic signed [31:0] old_max_prefix_i;
    logic signed [31:0] prefix_value_i;
    logic signed [31:0] size_i;
    logic signed [31:0] max_size_i;
    logic signed [31:0] read_value_i;
    logic signed [31:0] req_0_i;
    logic signed [31:0] req_1_i;
    logic signed [31:0] req_2_i;
    logic done_i;
    logic prefix_stop_i;
    logic special_cap_i;
    logic ich_disallow_i;
    logic use_ich_i;
    logic midpoint_i;
    logic [32:0] read_sum_i;
    logic [135:0] fifo_data_i;
    logic [4:0] qlevel_leaf_i;
    logic signed [4:0] adjusted_leaf_i;
    logic signed [5:0] max_residual_leaf_i;
    logic signed [5:0] escape_leaf_i;
    logic flatness_sent_i;
    logic [4:0] required_0_leaf_i;
    logic [4:0] required_1_leaf_i;
    logic [4:0] required_2_leaf_i;
    logic [4:0] predicted_leaf_i;

    assign cpnt_i = ((unit == 32'sd0) ? state_unitctype_0 : ((unit == 32'sd1) ? state_unitctype_1 : ((unit == 32'sd2) ? state_unitctype_2 : state_unitctype_3)));
    assign ssp_i = ((unit == 32'sd0) ? state_unitsspmap_0 : ((unit == 32'sd1) ? state_unitsspmap_1 : ((unit == 32'sd2) ? state_unitsspmap_2 : state_unitsspmap_3)));
    assign predicted_selected_i = ((unit == 32'sd0) ? state_predictedsize_0 : ((unit == 32'sd1) ? state_predictedsize_1 : ((unit == 32'sd2) ? state_predictedsize_2 : state_predictedsize_3)));
    assign depth_selected_i = ((cpnt_i == 32'sd0) ? state_cpntbitdepth_0 : ((cpnt_i == 32'sd1) ? state_cpntbitdepth_1 : ((cpnt_i == 32'sd2) ? state_cpntbitdepth_2 : state_cpntbitdepth_3)));
    assign fifo_data_i = {fifo_byte_0, fifo_byte_1, fifo_byte_2, fifo_byte_3, fifo_byte_4, fifo_byte_5, fifo_byte_6, fifo_byte_7, fifo_byte_8, fifo_byte_9, fifo_byte_10, fifo_byte_11, fifo_byte_12, fifo_byte_13, fifo_byte_14, fifo_byte_15, fifo_byte_16};

    mapqptoqlevel u_qp_mapping(
        .cpnt(cpnt_i[1:0]), .qp(state_primaryqp[4:0]),
        .dsc_version_minor(cfg_dsc_version_minor[1:0]),
        .native_420(cfg_native_420[0]),
        .cpntBitDepth_0(state_cpntbitdepth_0[4:0]),
        .cpntBitDepth_1(state_cpntbitdepth_1[4:0]),
        .qlevel_luma(qlevel_luma_primary[4:0]),
        .qlevel_chroma(qlevel_chroma_primary[4:0]),
        .return_value(qlevel_leaf_i));

    getqpadjpredsize u_adjusted_prediction(
        .unit(unit[1:0]), .dsc_version_minor(cfg_dsc_version_minor[1:0]),
        .native_420(cfg_native_420[0]),
        .unit_c_type_selected(cpnt_i[1:0]),
        .predicted_size_selected(predicted_selected_i[4:0]),
        .primary_qp(state_primaryqp[4:0]),
        .prev_primary_qp(state_prevprimaryqp[4:0]),
        .cpntBitDepth_0(state_cpntbitdepth_0[4:0]),
        .cpntBitDepth_1(state_cpntbitdepth_1[4:0]),
        .cpntBitDepth_2(state_cpntbitdepth_2[4:0]),
        .cpntBitDepth_3(state_cpntbitdepth_3[4:0]),
        .qlevel_luma_new(qlevel_luma_primary[4:0]),
        .qlevel_chroma_new(qlevel_chroma_primary[4:0]),
        .qlevel_luma_old(qlevel_luma_previous[4:0]),
        .qlevel_chroma_old(qlevel_chroma_previous[4:0]),
        .return_value(adjusted_leaf_i));

    maxresidualsize u_max_residual(
        .cpnt(cpnt_i[1:0]), .qp(state_primaryqp[4:0]),
        .dsc_version_minor(cfg_dsc_version_minor[1:0]),
        .native_420(cfg_native_420[0]),
        .cpntBitDepth_0(state_cpntbitdepth_0[4:0]),
        .cpntBitDepth_1(state_cpntbitdepth_1[4:0]),
        .cpntBitDepth_selected(depth_selected_i[4:0]),
        .qlevel_luma(qlevel_luma_primary[4:0]),
        .qlevel_chroma(qlevel_chroma_primary[4:0]),
        .return_value(max_residual_leaf_i));

    escapecodesize u_escape_size(
        .qp(state_primaryqp[4:0]),
        .dsc_version_minor(cfg_dsc_version_minor[1:0]),
        .native_420(cfg_native_420[0]),
        .cpntBitDepth_0(state_cpntbitdepth_0[4:0]),
        .qlevel_luma(qlevel_luma_primary[4:0]),
        .return_value(escape_leaf_i));

    isflatnessinfosent u_flatness_sent(
        .qp(state_primaryqp[4:0]),
        .flatness_min_qp(cfg_flatness_min_qp[4:0]),
        .flatness_max_qp(cfg_flatness_max_qp[4:0]),
        .return_value(flatness_sent_i));

    findresidualsize u_residual_size_0(
        .eq(quantized_residual_0_out[16:0]),
        .return_value(required_0_leaf_i));

    findresidualsize u_residual_size_1(
        .eq(quantized_residual_1_out[16:0]),
        .return_value(required_1_leaf_i));

    findresidualsize u_residual_size_2(
        .eq(quantized_residual_2_out[16:0]),
        .return_value(required_2_leaf_i));

    predictsize u_predict_size(
        .req_size_0(req_0_i[4:0]), .req_size_1(req_1_i[4:0]),
        .req_size_2(req_2_i[4:0]), .return_value(predicted_leaf_i));

    function automatic signed [31:0] dsc_cicd_read_bits(
        input logic [135:0] data_i,
        input logic signed [31:0] size_i,
        input logic signed [31:0] pointer_i,
        input logic signed [31:0] count_i,
        input logic sign_i);
        integer bit_i;
        integer position_i;
        logic signed [31:0] value_i;
        begin
            value_i = 32'sd0;
            for (bit_i = 0; bit_i < 32; bit_i = bit_i + 1) begin
                if (bit_i < count_i) begin
                    position_i = pointer_i + bit_i;
                    if (position_i >= size_i) position_i = position_i - size_i;
                    if ((position_i >= 0) && (position_i < 136))
                        value_i = (value_i <<< 1) | data_i[135 - position_i];
                end
            end
            if (sign_i && (count_i > 0) && value_i[count_i-1])
                value_i = value_i | (32'hffffffff << count_i);
            dsc_cicd_read_bits = value_i;
        end
    endfunction

    always_comb begin
        state_firstflat_out = state_firstflat;
        state_flatnesstype_out = state_flatnesstype;
        state_ichselected_out = state_ichselected;
        state_prevfirstflat_out = state_prevfirstflat;
        state_previchselected_out = state_previchselected;
        state_numbits_out = state_numbits;
        state_ichlookup_0_out = state_ichlookup_0;
        state_ichlookup_1_out = state_ichlookup_1;
        state_ichlookup_2_out = state_ichlookup_2;
        state_ichlookup_3_out = state_ichlookup_3;
        state_ichlookup_4_out = state_ichlookup_4;
        state_ichlookup_5_out = state_ichlookup_5;
        state_predictedsize_0_out = state_predictedsize_0;
        state_predictedsize_1_out = state_predictedsize_1;
        state_predictedsize_2_out = state_predictedsize_2;
        state_predictedsize_3_out = state_predictedsize_3;
        state_rcsizeunit_0_out = state_rcsizeunit_0;
        state_rcsizeunit_1_out = state_rcsizeunit_1;
        state_rcsizeunit_2_out = state_rcsizeunit_2;
        state_rcsizeunit_3_out = state_rcsizeunit_3;
        state_usemidpoint_0_out = state_usemidpoint_0;
        state_usemidpoint_1_out = state_usemidpoint_1;
        state_usemidpoint_2_out = state_usemidpoint_2;
        state_usemidpoint_3_out = state_usemidpoint_3;
        quantized_residual_0_out = quantized_residual_0;
        quantized_residual_1_out = quantized_residual_1;
        quantized_residual_2_out = quantized_residual_2;
        fifo_lane_out = ssp_i;
        fifo_fullness_out = fifo_fullness;
        fifo_read_ptr_out = fifo_read_ptr;
        domain_valid = 1'b1;
        done_i = 1'b0;
        prefix_stop_i = 1'b0;
        special_cap_i = 1'b0;
        prefix_value_i = 32'sd0;
        prefix_limit_i = 32'sd0;
        old_max_prefix_i = 32'sd0;
        size_i = 32'sd0;
        max_size_i = 32'sd0;
        read_value_i = 32'sd0;
        read_sum_i = 33'd0;
        max_prefix_i = 32'sd0;
        req_0_i = 32'sd0; req_1_i = 32'sd0; req_2_i = 32'sd0;
        use_ich_i = 1'b0; midpoint_i = 1'b0;
        qlevel_i = $signed({27'd0, qlevel_leaf_i});
        adj_predicted_i = $signed(adjusted_leaf_i);
        ich_disallow_i = (cfg_bits_per_component == 32'sd16) && (unit == 0) && ((32'sd3 * qlevel_i) <= (32'sd3 - adj_predicted_i));
        if ((unit < 0) || (unit >= 32'sd4) || (cpnt_i < 0) || (cpnt_i >= 32'sd4) || (ssp_i < 0) || (ssp_i >= 32'sd4) || (state_unitspergroup < 0) || (state_unitspergroup > 32'sd4) || (state_ichindicesingroup < 0) || (state_ichindicesingroup > 32'sd6) || (fifo_size <= 0) || (fifo_size > 32'sd136) || ((fifo_size & 32'sd7) != 0)) domain_valid = 1'b0;
        if (unit == 0) begin
            state_previchselected_out = state_ichselected;
            state_ichselected_out = 32'sd0;
        end
        if ((unit == 0) && (state_groupcount[1:0] == 2'd3)) begin
            if (flatness_sent_i) begin
                if ((32'sd1 < 0) || (32'sd1 > 32) || (fifo_fullness_out < 32'sd1)) domain_valid = 1'b0;
                read_value_i = dsc_cicd_read_bits(fifo_data_i, fifo_size, fifo_read_ptr_out, 32'sd1, 1'b0);
                state_numbits_out = state_numbits_out + 32'sd1;
                fifo_fullness_out = fifo_fullness_out - 32'sd1;
                read_sum_i = {1'b0, fifo_read_ptr_out} + 32'sd1;
                if (read_sum_i >= {1'b0, fifo_size})
                    fifo_read_ptr_out = read_sum_i[31:0] - fifo_size;
                else fifo_read_ptr_out = read_sum_i[31:0];
                state_prevfirstflat_out = (read_value_i != 0) ? 32'sd0 : -32'sd1;
            end else state_prevfirstflat_out = -32'sd1;
        end
        if ((unit == 0) && (state_groupcount[1:0] == 2'd0)) begin
            if (state_prevfirstflat_out >= 0) begin
                state_flatnesstype_out = 32'sd0;
                if (state_primaryqp >= cfg_somewhat_flat_qp_thresh) begin
                    if ((32'sd1 < 0) || (32'sd1 > 32) || (fifo_fullness_out < 32'sd1)) domain_valid = 1'b0;
                    read_value_i = dsc_cicd_read_bits(fifo_data_i, fifo_size, fifo_read_ptr_out, 32'sd1, 1'b0);
                    state_numbits_out = state_numbits_out + 32'sd1;
                    fifo_fullness_out = fifo_fullness_out - 32'sd1;
                    read_sum_i = {1'b0, fifo_read_ptr_out} + 32'sd1;
                    if (read_sum_i >= {1'b0, fifo_size})
                        fifo_read_ptr_out = read_sum_i[31:0] - fifo_size;
                    else fifo_read_ptr_out = read_sum_i[31:0];
                    state_flatnesstype_out = read_value_i;
                end
                if ((32'sd2 < 0) || (32'sd2 > 32) || (fifo_fullness_out < 32'sd2)) domain_valid = 1'b0;
                read_value_i = dsc_cicd_read_bits(fifo_data_i, fifo_size, fifo_read_ptr_out, 32'sd2, 1'b0);
                state_numbits_out = state_numbits_out + 32'sd2;
                fifo_fullness_out = fifo_fullness_out - 32'sd2;
                read_sum_i = {1'b0, fifo_read_ptr_out} + 32'sd2;
                if (read_sum_i >= {1'b0, fifo_size})
                    fifo_read_ptr_out = read_sum_i[31:0] - fifo_size;
                else fifo_read_ptr_out = read_sum_i[31:0];
                state_firstflat_out = read_value_i;
            end else state_firstflat_out = -32'sd1;
        end
        if (state_ichselected_out != 0) begin
            if ((32'sd0 < state_ichindicesingroup) && (state_ichindexunitmap_0 == unit)) begin
                if ((32'sd1 * 32'sd5 < 0) || (32'sd1 * 32'sd5 > 32) || (fifo_fullness_out < 32'sd1 * 32'sd5)) domain_valid = 1'b0;
                read_value_i = dsc_cicd_read_bits(fifo_data_i, fifo_size, fifo_read_ptr_out, 32'sd1 * 32'sd5, 1'b0);
                state_numbits_out = state_numbits_out + 32'sd1 * 32'sd5;
                fifo_fullness_out = fifo_fullness_out - 32'sd1 * 32'sd5;
                read_sum_i = {1'b0, fifo_read_ptr_out} + 32'sd1 * 32'sd5;
                if (read_sum_i >= {1'b0, fifo_size})
                    fifo_read_ptr_out = read_sum_i[31:0] - fifo_size;
                else fifo_read_ptr_out = read_sum_i[31:0];
                state_ichlookup_0_out = read_value_i;
            end
            if ((32'sd1 < state_ichindicesingroup) && (state_ichindexunitmap_1 == unit)) begin
                if ((32'sd1 * 32'sd5 < 0) || (32'sd1 * 32'sd5 > 32) || (fifo_fullness_out < 32'sd1 * 32'sd5)) domain_valid = 1'b0;
                read_value_i = dsc_cicd_read_bits(fifo_data_i, fifo_size, fifo_read_ptr_out, 32'sd1 * 32'sd5, 1'b0);
                state_numbits_out = state_numbits_out + 32'sd1 * 32'sd5;
                fifo_fullness_out = fifo_fullness_out - 32'sd1 * 32'sd5;
                read_sum_i = {1'b0, fifo_read_ptr_out} + 32'sd1 * 32'sd5;
                if (read_sum_i >= {1'b0, fifo_size})
                    fifo_read_ptr_out = read_sum_i[31:0] - fifo_size;
                else fifo_read_ptr_out = read_sum_i[31:0];
                state_ichlookup_1_out = read_value_i;
            end
            if ((32'sd2 < state_ichindicesingroup) && (state_ichindexunitmap_2 == unit)) begin
                if ((32'sd1 * 32'sd5 < 0) || (32'sd1 * 32'sd5 > 32) || (fifo_fullness_out < 32'sd1 * 32'sd5)) domain_valid = 1'b0;
                read_value_i = dsc_cicd_read_bits(fifo_data_i, fifo_size, fifo_read_ptr_out, 32'sd1 * 32'sd5, 1'b0);
                state_numbits_out = state_numbits_out + 32'sd1 * 32'sd5;
                fifo_fullness_out = fifo_fullness_out - 32'sd1 * 32'sd5;
                read_sum_i = {1'b0, fifo_read_ptr_out} + 32'sd1 * 32'sd5;
                if (read_sum_i >= {1'b0, fifo_size})
                    fifo_read_ptr_out = read_sum_i[31:0] - fifo_size;
                else fifo_read_ptr_out = read_sum_i[31:0];
                state_ichlookup_2_out = read_value_i;
            end
            if ((32'sd3 < state_ichindicesingroup) && (state_ichindexunitmap_3 == unit)) begin
                if ((32'sd1 * 32'sd5 < 0) || (32'sd1 * 32'sd5 > 32) || (fifo_fullness_out < 32'sd1 * 32'sd5)) domain_valid = 1'b0;
                read_value_i = dsc_cicd_read_bits(fifo_data_i, fifo_size, fifo_read_ptr_out, 32'sd1 * 32'sd5, 1'b0);
                state_numbits_out = state_numbits_out + 32'sd1 * 32'sd5;
                fifo_fullness_out = fifo_fullness_out - 32'sd1 * 32'sd5;
                read_sum_i = {1'b0, fifo_read_ptr_out} + 32'sd1 * 32'sd5;
                if (read_sum_i >= {1'b0, fifo_size})
                    fifo_read_ptr_out = read_sum_i[31:0] - fifo_size;
                else fifo_read_ptr_out = read_sum_i[31:0];
                state_ichlookup_3_out = read_value_i;
            end
            if ((32'sd4 < state_ichindicesingroup) && (state_ichindexunitmap_4 == unit)) begin
                if ((32'sd1 * 32'sd5 < 0) || (32'sd1 * 32'sd5 > 32) || (fifo_fullness_out < 32'sd1 * 32'sd5)) domain_valid = 1'b0;
                read_value_i = dsc_cicd_read_bits(fifo_data_i, fifo_size, fifo_read_ptr_out, 32'sd1 * 32'sd5, 1'b0);
                state_numbits_out = state_numbits_out + 32'sd1 * 32'sd5;
                fifo_fullness_out = fifo_fullness_out - 32'sd1 * 32'sd5;
                read_sum_i = {1'b0, fifo_read_ptr_out} + 32'sd1 * 32'sd5;
                if (read_sum_i >= {1'b0, fifo_size})
                    fifo_read_ptr_out = read_sum_i[31:0] - fifo_size;
                else fifo_read_ptr_out = read_sum_i[31:0];
                state_ichlookup_4_out = read_value_i;
            end
            if ((32'sd5 < state_ichindicesingroup) && (state_ichindexunitmap_5 == unit)) begin
                if ((32'sd1 * 32'sd5 < 0) || (32'sd1 * 32'sd5 > 32) || (fifo_fullness_out < 32'sd1 * 32'sd5)) domain_valid = 1'b0;
                read_value_i = dsc_cicd_read_bits(fifo_data_i, fifo_size, fifo_read_ptr_out, 32'sd1 * 32'sd5, 1'b0);
                state_numbits_out = state_numbits_out + 32'sd1 * 32'sd5;
                fifo_fullness_out = fifo_fullness_out - 32'sd1 * 32'sd5;
                read_sum_i = {1'b0, fifo_read_ptr_out} + 32'sd1 * 32'sd5;
                if (read_sum_i >= {1'b0, fifo_size})
                    fifo_read_ptr_out = read_sum_i[31:0] - fifo_size;
                else fifo_read_ptr_out = read_sum_i[31:0];
                state_ichlookup_5_out = read_value_i;
            end
            done_i = 1'b1;
        end
        if (!done_i) begin
            max_prefix_i = $signed(max_residual_leaf_i) + (((unit == 0) && !ich_disallow_i) ? 32'sd1 : 32'sd0) - adj_predicted_i;
            old_max_prefix_i = max_prefix_i;
            prefix_limit_i = max_prefix_i;
            if ((cfg_bits_per_component == 32'sd16) && (unit == 0) && (qlevel_i == 0) && ich_disallow_i && ((max_prefix_i + 32'sd48) > 32'sd61)) begin
                prefix_limit_i = 32'sd13;
                special_cap_i = 1'b1;
            end
            if (!prefix_stop_i && (prefix_value_i < prefix_limit_i)) begin
                if ((32'sd1 < 0) || (32'sd1 > 32) || (fifo_fullness_out < 32'sd1)) domain_valid = 1'b0;
                read_value_i = dsc_cicd_read_bits(fifo_data_i, fifo_size, fifo_read_ptr_out, 32'sd1, 1'b0);
                state_numbits_out = state_numbits_out + 32'sd1;
                fifo_fullness_out = fifo_fullness_out - 32'sd1;
                read_sum_i = {1'b0, fifo_read_ptr_out} + 32'sd1;
                if (read_sum_i >= {1'b0, fifo_size})
                    fifo_read_ptr_out = read_sum_i[31:0] - fifo_size;
                else fifo_read_ptr_out = read_sum_i[31:0];
                if (read_value_i == 0) prefix_value_i = prefix_value_i + 1;
                else prefix_stop_i = 1'b1;
            end
            if (!prefix_stop_i && (prefix_value_i < prefix_limit_i)) begin
                if ((32'sd1 < 0) || (32'sd1 > 32) || (fifo_fullness_out < 32'sd1)) domain_valid = 1'b0;
                read_value_i = dsc_cicd_read_bits(fifo_data_i, fifo_size, fifo_read_ptr_out, 32'sd1, 1'b0);
                state_numbits_out = state_numbits_out + 32'sd1;
                fifo_fullness_out = fifo_fullness_out - 32'sd1;
                read_sum_i = {1'b0, fifo_read_ptr_out} + 32'sd1;
                if (read_sum_i >= {1'b0, fifo_size})
                    fifo_read_ptr_out = read_sum_i[31:0] - fifo_size;
                else fifo_read_ptr_out = read_sum_i[31:0];
                if (read_value_i == 0) prefix_value_i = prefix_value_i + 1;
                else prefix_stop_i = 1'b1;
            end
            if (!prefix_stop_i && (prefix_value_i < prefix_limit_i)) begin
                if ((32'sd1 < 0) || (32'sd1 > 32) || (fifo_fullness_out < 32'sd1)) domain_valid = 1'b0;
                read_value_i = dsc_cicd_read_bits(fifo_data_i, fifo_size, fifo_read_ptr_out, 32'sd1, 1'b0);
                state_numbits_out = state_numbits_out + 32'sd1;
                fifo_fullness_out = fifo_fullness_out - 32'sd1;
                read_sum_i = {1'b0, fifo_read_ptr_out} + 32'sd1;
                if (read_sum_i >= {1'b0, fifo_size})
                    fifo_read_ptr_out = read_sum_i[31:0] - fifo_size;
                else fifo_read_ptr_out = read_sum_i[31:0];
                if (read_value_i == 0) prefix_value_i = prefix_value_i + 1;
                else prefix_stop_i = 1'b1;
            end
            if (!prefix_stop_i && (prefix_value_i < prefix_limit_i)) begin
                if ((32'sd1 < 0) || (32'sd1 > 32) || (fifo_fullness_out < 32'sd1)) domain_valid = 1'b0;
                read_value_i = dsc_cicd_read_bits(fifo_data_i, fifo_size, fifo_read_ptr_out, 32'sd1, 1'b0);
                state_numbits_out = state_numbits_out + 32'sd1;
                fifo_fullness_out = fifo_fullness_out - 32'sd1;
                read_sum_i = {1'b0, fifo_read_ptr_out} + 32'sd1;
                if (read_sum_i >= {1'b0, fifo_size})
                    fifo_read_ptr_out = read_sum_i[31:0] - fifo_size;
                else fifo_read_ptr_out = read_sum_i[31:0];
                if (read_value_i == 0) prefix_value_i = prefix_value_i + 1;
                else prefix_stop_i = 1'b1;
            end
            if (!prefix_stop_i && (prefix_value_i < prefix_limit_i)) begin
                if ((32'sd1 < 0) || (32'sd1 > 32) || (fifo_fullness_out < 32'sd1)) domain_valid = 1'b0;
                read_value_i = dsc_cicd_read_bits(fifo_data_i, fifo_size, fifo_read_ptr_out, 32'sd1, 1'b0);
                state_numbits_out = state_numbits_out + 32'sd1;
                fifo_fullness_out = fifo_fullness_out - 32'sd1;
                read_sum_i = {1'b0, fifo_read_ptr_out} + 32'sd1;
                if (read_sum_i >= {1'b0, fifo_size})
                    fifo_read_ptr_out = read_sum_i[31:0] - fifo_size;
                else fifo_read_ptr_out = read_sum_i[31:0];
                if (read_value_i == 0) prefix_value_i = prefix_value_i + 1;
                else prefix_stop_i = 1'b1;
            end
            if (!prefix_stop_i && (prefix_value_i < prefix_limit_i)) begin
                if ((32'sd1 < 0) || (32'sd1 > 32) || (fifo_fullness_out < 32'sd1)) domain_valid = 1'b0;
                read_value_i = dsc_cicd_read_bits(fifo_data_i, fifo_size, fifo_read_ptr_out, 32'sd1, 1'b0);
                state_numbits_out = state_numbits_out + 32'sd1;
                fifo_fullness_out = fifo_fullness_out - 32'sd1;
                read_sum_i = {1'b0, fifo_read_ptr_out} + 32'sd1;
                if (read_sum_i >= {1'b0, fifo_size})
                    fifo_read_ptr_out = read_sum_i[31:0] - fifo_size;
                else fifo_read_ptr_out = read_sum_i[31:0];
                if (read_value_i == 0) prefix_value_i = prefix_value_i + 1;
                else prefix_stop_i = 1'b1;
            end
            if (!prefix_stop_i && (prefix_value_i < prefix_limit_i)) begin
                if ((32'sd1 < 0) || (32'sd1 > 32) || (fifo_fullness_out < 32'sd1)) domain_valid = 1'b0;
                read_value_i = dsc_cicd_read_bits(fifo_data_i, fifo_size, fifo_read_ptr_out, 32'sd1, 1'b0);
                state_numbits_out = state_numbits_out + 32'sd1;
                fifo_fullness_out = fifo_fullness_out - 32'sd1;
                read_sum_i = {1'b0, fifo_read_ptr_out} + 32'sd1;
                if (read_sum_i >= {1'b0, fifo_size})
                    fifo_read_ptr_out = read_sum_i[31:0] - fifo_size;
                else fifo_read_ptr_out = read_sum_i[31:0];
                if (read_value_i == 0) prefix_value_i = prefix_value_i + 1;
                else prefix_stop_i = 1'b1;
            end
            if (!prefix_stop_i && (prefix_value_i < prefix_limit_i)) begin
                if ((32'sd1 < 0) || (32'sd1 > 32) || (fifo_fullness_out < 32'sd1)) domain_valid = 1'b0;
                read_value_i = dsc_cicd_read_bits(fifo_data_i, fifo_size, fifo_read_ptr_out, 32'sd1, 1'b0);
                state_numbits_out = state_numbits_out + 32'sd1;
                fifo_fullness_out = fifo_fullness_out - 32'sd1;
                read_sum_i = {1'b0, fifo_read_ptr_out} + 32'sd1;
                if (read_sum_i >= {1'b0, fifo_size})
                    fifo_read_ptr_out = read_sum_i[31:0] - fifo_size;
                else fifo_read_ptr_out = read_sum_i[31:0];
                if (read_value_i == 0) prefix_value_i = prefix_value_i + 1;
                else prefix_stop_i = 1'b1;
            end
            if (!prefix_stop_i && (prefix_value_i < prefix_limit_i)) begin
                if ((32'sd1 < 0) || (32'sd1 > 32) || (fifo_fullness_out < 32'sd1)) domain_valid = 1'b0;
                read_value_i = dsc_cicd_read_bits(fifo_data_i, fifo_size, fifo_read_ptr_out, 32'sd1, 1'b0);
                state_numbits_out = state_numbits_out + 32'sd1;
                fifo_fullness_out = fifo_fullness_out - 32'sd1;
                read_sum_i = {1'b0, fifo_read_ptr_out} + 32'sd1;
                if (read_sum_i >= {1'b0, fifo_size})
                    fifo_read_ptr_out = read_sum_i[31:0] - fifo_size;
                else fifo_read_ptr_out = read_sum_i[31:0];
                if (read_value_i == 0) prefix_value_i = prefix_value_i + 1;
                else prefix_stop_i = 1'b1;
            end
            if (!prefix_stop_i && (prefix_value_i < prefix_limit_i)) begin
                if ((32'sd1 < 0) || (32'sd1 > 32) || (fifo_fullness_out < 32'sd1)) domain_valid = 1'b0;
                read_value_i = dsc_cicd_read_bits(fifo_data_i, fifo_size, fifo_read_ptr_out, 32'sd1, 1'b0);
                state_numbits_out = state_numbits_out + 32'sd1;
                fifo_fullness_out = fifo_fullness_out - 32'sd1;
                read_sum_i = {1'b0, fifo_read_ptr_out} + 32'sd1;
                if (read_sum_i >= {1'b0, fifo_size})
                    fifo_read_ptr_out = read_sum_i[31:0] - fifo_size;
                else fifo_read_ptr_out = read_sum_i[31:0];
                if (read_value_i == 0) prefix_value_i = prefix_value_i + 1;
                else prefix_stop_i = 1'b1;
            end
            if (!prefix_stop_i && (prefix_value_i < prefix_limit_i)) begin
                if ((32'sd1 < 0) || (32'sd1 > 32) || (fifo_fullness_out < 32'sd1)) domain_valid = 1'b0;
                read_value_i = dsc_cicd_read_bits(fifo_data_i, fifo_size, fifo_read_ptr_out, 32'sd1, 1'b0);
                state_numbits_out = state_numbits_out + 32'sd1;
                fifo_fullness_out = fifo_fullness_out - 32'sd1;
                read_sum_i = {1'b0, fifo_read_ptr_out} + 32'sd1;
                if (read_sum_i >= {1'b0, fifo_size})
                    fifo_read_ptr_out = read_sum_i[31:0] - fifo_size;
                else fifo_read_ptr_out = read_sum_i[31:0];
                if (read_value_i == 0) prefix_value_i = prefix_value_i + 1;
                else prefix_stop_i = 1'b1;
            end
            if (!prefix_stop_i && (prefix_value_i < prefix_limit_i)) begin
                if ((32'sd1 < 0) || (32'sd1 > 32) || (fifo_fullness_out < 32'sd1)) domain_valid = 1'b0;
                read_value_i = dsc_cicd_read_bits(fifo_data_i, fifo_size, fifo_read_ptr_out, 32'sd1, 1'b0);
                state_numbits_out = state_numbits_out + 32'sd1;
                fifo_fullness_out = fifo_fullness_out - 32'sd1;
                read_sum_i = {1'b0, fifo_read_ptr_out} + 32'sd1;
                if (read_sum_i >= {1'b0, fifo_size})
                    fifo_read_ptr_out = read_sum_i[31:0] - fifo_size;
                else fifo_read_ptr_out = read_sum_i[31:0];
                if (read_value_i == 0) prefix_value_i = prefix_value_i + 1;
                else prefix_stop_i = 1'b1;
            end
            if (!prefix_stop_i && (prefix_value_i < prefix_limit_i)) begin
                if ((32'sd1 < 0) || (32'sd1 > 32) || (fifo_fullness_out < 32'sd1)) domain_valid = 1'b0;
                read_value_i = dsc_cicd_read_bits(fifo_data_i, fifo_size, fifo_read_ptr_out, 32'sd1, 1'b0);
                state_numbits_out = state_numbits_out + 32'sd1;
                fifo_fullness_out = fifo_fullness_out - 32'sd1;
                read_sum_i = {1'b0, fifo_read_ptr_out} + 32'sd1;
                if (read_sum_i >= {1'b0, fifo_size})
                    fifo_read_ptr_out = read_sum_i[31:0] - fifo_size;
                else fifo_read_ptr_out = read_sum_i[31:0];
                if (read_value_i == 0) prefix_value_i = prefix_value_i + 1;
                else prefix_stop_i = 1'b1;
            end
            if (!prefix_stop_i && (prefix_value_i < prefix_limit_i)) begin
                if ((32'sd1 < 0) || (32'sd1 > 32) || (fifo_fullness_out < 32'sd1)) domain_valid = 1'b0;
                read_value_i = dsc_cicd_read_bits(fifo_data_i, fifo_size, fifo_read_ptr_out, 32'sd1, 1'b0);
                state_numbits_out = state_numbits_out + 32'sd1;
                fifo_fullness_out = fifo_fullness_out - 32'sd1;
                read_sum_i = {1'b0, fifo_read_ptr_out} + 32'sd1;
                if (read_sum_i >= {1'b0, fifo_size})
                    fifo_read_ptr_out = read_sum_i[31:0] - fifo_size;
                else fifo_read_ptr_out = read_sum_i[31:0];
                if (read_value_i == 0) prefix_value_i = prefix_value_i + 1;
                else prefix_stop_i = 1'b1;
            end
            if (!prefix_stop_i && (prefix_value_i < prefix_limit_i)) begin
                if ((32'sd1 < 0) || (32'sd1 > 32) || (fifo_fullness_out < 32'sd1)) domain_valid = 1'b0;
                read_value_i = dsc_cicd_read_bits(fifo_data_i, fifo_size, fifo_read_ptr_out, 32'sd1, 1'b0);
                state_numbits_out = state_numbits_out + 32'sd1;
                fifo_fullness_out = fifo_fullness_out - 32'sd1;
                read_sum_i = {1'b0, fifo_read_ptr_out} + 32'sd1;
                if (read_sum_i >= {1'b0, fifo_size})
                    fifo_read_ptr_out = read_sum_i[31:0] - fifo_size;
                else fifo_read_ptr_out = read_sum_i[31:0];
                if (read_value_i == 0) prefix_value_i = prefix_value_i + 1;
                else prefix_stop_i = 1'b1;
            end
            if (!prefix_stop_i && (prefix_value_i < prefix_limit_i)) begin
                if ((32'sd1 < 0) || (32'sd1 > 32) || (fifo_fullness_out < 32'sd1)) domain_valid = 1'b0;
                read_value_i = dsc_cicd_read_bits(fifo_data_i, fifo_size, fifo_read_ptr_out, 32'sd1, 1'b0);
                state_numbits_out = state_numbits_out + 32'sd1;
                fifo_fullness_out = fifo_fullness_out - 32'sd1;
                read_sum_i = {1'b0, fifo_read_ptr_out} + 32'sd1;
                if (read_sum_i >= {1'b0, fifo_size})
                    fifo_read_ptr_out = read_sum_i[31:0] - fifo_size;
                else fifo_read_ptr_out = read_sum_i[31:0];
                if (read_value_i == 0) prefix_value_i = prefix_value_i + 1;
                else prefix_stop_i = 1'b1;
            end
            if (!prefix_stop_i && (prefix_value_i < prefix_limit_i)) begin
                if ((32'sd1 < 0) || (32'sd1 > 32) || (fifo_fullness_out < 32'sd1)) domain_valid = 1'b0;
                read_value_i = dsc_cicd_read_bits(fifo_data_i, fifo_size, fifo_read_ptr_out, 32'sd1, 1'b0);
                state_numbits_out = state_numbits_out + 32'sd1;
                fifo_fullness_out = fifo_fullness_out - 32'sd1;
                read_sum_i = {1'b0, fifo_read_ptr_out} + 32'sd1;
                if (read_sum_i >= {1'b0, fifo_size})
                    fifo_read_ptr_out = read_sum_i[31:0] - fifo_size;
                else fifo_read_ptr_out = read_sum_i[31:0];
                if (read_value_i == 0) prefix_value_i = prefix_value_i + 1;
                else prefix_stop_i = 1'b1;
            end
            if (special_cap_i && (prefix_value_i == prefix_limit_i))
                prefix_value_i = old_max_prefix_i;
            if ((unit == 0) && (state_previchselected_out != 0) && !ich_disallow_i)
                size_i = adj_predicted_i + prefix_value_i - 1;
            else size_i = adj_predicted_i + prefix_value_i;
            if (state_previchselected_out != 0)
                use_ich_i = !ich_disallow_i && (prefix_value_i == 0);
            else use_ich_i = !ich_disallow_i && (size_i >= $signed(escape_leaf_i));
            if ((unit == 0) && use_ich_i) begin
                state_ichselected_out = 32'sd1;
                state_rcsizeunit_0_out = 32'sd1 + (32'sd5 * state_ichindicesingroup);
                if (state_unitspergroup > 32'sd1)
                    state_rcsizeunit_1_out = 32'sd0;
                if (state_unitspergroup > 32'sd2)
                    state_rcsizeunit_2_out = 32'sd0;
                if (state_unitspergroup > 32'sd3)
                    state_rcsizeunit_3_out = 32'sd0;
                if ((32'sd0 < state_ichindicesingroup) && (state_ichindexunitmap_0 == unit)) begin
                    if ((32'sd5 < 0) || (32'sd5 > 32) || (fifo_fullness_out < 32'sd5)) domain_valid = 1'b0;
                    read_value_i = dsc_cicd_read_bits(fifo_data_i, fifo_size, fifo_read_ptr_out, 32'sd5, 1'b0);
                    state_numbits_out = state_numbits_out + 32'sd5;
                    fifo_fullness_out = fifo_fullness_out - 32'sd5;
                    read_sum_i = {1'b0, fifo_read_ptr_out} + 32'sd5;
                    if (read_sum_i >= {1'b0, fifo_size})
                        fifo_read_ptr_out = read_sum_i[31:0] - fifo_size;
                    else fifo_read_ptr_out = read_sum_i[31:0];
                    state_ichlookup_0_out = read_value_i;
                end
                if ((32'sd1 < state_ichindicesingroup) && (state_ichindexunitmap_1 == unit)) begin
                    if ((32'sd5 < 0) || (32'sd5 > 32) || (fifo_fullness_out < 32'sd5)) domain_valid = 1'b0;
                    read_value_i = dsc_cicd_read_bits(fifo_data_i, fifo_size, fifo_read_ptr_out, 32'sd5, 1'b0);
                    state_numbits_out = state_numbits_out + 32'sd5;
                    fifo_fullness_out = fifo_fullness_out - 32'sd5;
                    read_sum_i = {1'b0, fifo_read_ptr_out} + 32'sd5;
                    if (read_sum_i >= {1'b0, fifo_size})
                        fifo_read_ptr_out = read_sum_i[31:0] - fifo_size;
                    else fifo_read_ptr_out = read_sum_i[31:0];
                    state_ichlookup_1_out = read_value_i;
                end
                if ((32'sd2 < state_ichindicesingroup) && (state_ichindexunitmap_2 == unit)) begin
                    if ((32'sd5 < 0) || (32'sd5 > 32) || (fifo_fullness_out < 32'sd5)) domain_valid = 1'b0;
                    read_value_i = dsc_cicd_read_bits(fifo_data_i, fifo_size, fifo_read_ptr_out, 32'sd5, 1'b0);
                    state_numbits_out = state_numbits_out + 32'sd5;
                    fifo_fullness_out = fifo_fullness_out - 32'sd5;
                    read_sum_i = {1'b0, fifo_read_ptr_out} + 32'sd5;
                    if (read_sum_i >= {1'b0, fifo_size})
                        fifo_read_ptr_out = read_sum_i[31:0] - fifo_size;
                    else fifo_read_ptr_out = read_sum_i[31:0];
                    state_ichlookup_2_out = read_value_i;
                end
                if ((32'sd3 < state_ichindicesingroup) && (state_ichindexunitmap_3 == unit)) begin
                    if ((32'sd5 < 0) || (32'sd5 > 32) || (fifo_fullness_out < 32'sd5)) domain_valid = 1'b0;
                    read_value_i = dsc_cicd_read_bits(fifo_data_i, fifo_size, fifo_read_ptr_out, 32'sd5, 1'b0);
                    state_numbits_out = state_numbits_out + 32'sd5;
                    fifo_fullness_out = fifo_fullness_out - 32'sd5;
                    read_sum_i = {1'b0, fifo_read_ptr_out} + 32'sd5;
                    if (read_sum_i >= {1'b0, fifo_size})
                        fifo_read_ptr_out = read_sum_i[31:0] - fifo_size;
                    else fifo_read_ptr_out = read_sum_i[31:0];
                    state_ichlookup_3_out = read_value_i;
                end
                if ((32'sd4 < state_ichindicesingroup) && (state_ichindexunitmap_4 == unit)) begin
                    if ((32'sd5 < 0) || (32'sd5 > 32) || (fifo_fullness_out < 32'sd5)) domain_valid = 1'b0;
                    read_value_i = dsc_cicd_read_bits(fifo_data_i, fifo_size, fifo_read_ptr_out, 32'sd5, 1'b0);
                    state_numbits_out = state_numbits_out + 32'sd5;
                    fifo_fullness_out = fifo_fullness_out - 32'sd5;
                    read_sum_i = {1'b0, fifo_read_ptr_out} + 32'sd5;
                    if (read_sum_i >= {1'b0, fifo_size})
                        fifo_read_ptr_out = read_sum_i[31:0] - fifo_size;
                    else fifo_read_ptr_out = read_sum_i[31:0];
                    state_ichlookup_4_out = read_value_i;
                end
                if ((32'sd5 < state_ichindicesingroup) && (state_ichindexunitmap_5 == unit)) begin
                    if ((32'sd5 < 0) || (32'sd5 > 32) || (fifo_fullness_out < 32'sd5)) domain_valid = 1'b0;
                    read_value_i = dsc_cicd_read_bits(fifo_data_i, fifo_size, fifo_read_ptr_out, 32'sd5, 1'b0);
                    state_numbits_out = state_numbits_out + 32'sd5;
                    fifo_fullness_out = fifo_fullness_out - 32'sd5;
                    read_sum_i = {1'b0, fifo_read_ptr_out} + 32'sd5;
                    if (read_sum_i >= {1'b0, fifo_size})
                        fifo_read_ptr_out = read_sum_i[31:0] - fifo_size;
                    else fifo_read_ptr_out = read_sum_i[31:0];
                    state_ichlookup_5_out = read_value_i;
                end
                done_i = 1'b1;
            end
        end
        if (!done_i) begin
            midpoint_i = (size_i == ((((cpnt_i == 32'sd0) ? state_cpntbitdepth_0 : ((cpnt_i == 32'sd1) ? state_cpntbitdepth_1 : ((cpnt_i == 32'sd2) ? state_cpntbitdepth_2 : state_cpntbitdepth_3)))) - qlevel_i));
            if (unit == 32'sd0)
                state_usemidpoint_0_out = midpoint_i;
            if (unit == 32'sd1)
                state_usemidpoint_1_out = midpoint_i;
            if (unit == 32'sd2)
                state_usemidpoint_2_out = midpoint_i;
            if (unit == 32'sd3)
                state_usemidpoint_3_out = midpoint_i;
            if ((size_i < 0) || (size_i > 32) || (fifo_fullness_out < size_i)) domain_valid = 1'b0;
            quantized_residual_0_out = dsc_cicd_read_bits(fifo_data_i, fifo_size, fifo_read_ptr_out, size_i, 1'b1);
            state_numbits_out = state_numbits_out + size_i;
            fifo_fullness_out = fifo_fullness_out - size_i;
            read_sum_i = {1'b0, fifo_read_ptr_out} + size_i;
            if (read_sum_i >= {1'b0, fifo_size})
                fifo_read_ptr_out = read_sum_i[31:0] - fifo_size;
            else fifo_read_ptr_out = read_sum_i[31:0];
            if ((size_i < 0) || (size_i > 32) || (fifo_fullness_out < size_i)) domain_valid = 1'b0;
            quantized_residual_1_out = dsc_cicd_read_bits(fifo_data_i, fifo_size, fifo_read_ptr_out, size_i, 1'b1);
            state_numbits_out = state_numbits_out + size_i;
            fifo_fullness_out = fifo_fullness_out - size_i;
            read_sum_i = {1'b0, fifo_read_ptr_out} + size_i;
            if (read_sum_i >= {1'b0, fifo_size})
                fifo_read_ptr_out = read_sum_i[31:0] - fifo_size;
            else fifo_read_ptr_out = read_sum_i[31:0];
            if ((size_i < 0) || (size_i > 32) || (fifo_fullness_out < size_i)) domain_valid = 1'b0;
            quantized_residual_2_out = dsc_cicd_read_bits(fifo_data_i, fifo_size, fifo_read_ptr_out, size_i, 1'b1);
            state_numbits_out = state_numbits_out + size_i;
            fifo_fullness_out = fifo_fullness_out - size_i;
            read_sum_i = {1'b0, fifo_read_ptr_out} + size_i;
            if (read_sum_i >= {1'b0, fifo_size})
                fifo_read_ptr_out = read_sum_i[31:0] - fifo_size;
            else fifo_read_ptr_out = read_sum_i[31:0];
            req_0_i = $signed({27'd0, required_0_leaf_i});
            req_1_i = $signed({27'd0, required_1_leaf_i});
            req_2_i = $signed({27'd0, required_2_leaf_i});
            max_size_i = req_0_i;
            if (req_1_i > max_size_i) max_size_i = req_1_i;
            if (req_2_i > max_size_i) max_size_i = req_2_i;
            if (midpoint_i) begin
                max_size_i = size_i;
                req_0_i = size_i; req_1_i = size_i; req_2_i = size_i;
            end
            if (unit == 32'sd0) begin
                state_rcsizeunit_0_out = (max_size_i * 32'sd3) + 1;
                state_predictedsize_0_out = $signed({27'd0, predicted_leaf_i});
            end
            if (unit == 32'sd1) begin
                state_rcsizeunit_1_out = (max_size_i * 32'sd3) + 1;
                state_predictedsize_1_out = $signed({27'd0, predicted_leaf_i});
            end
            if (unit == 32'sd2) begin
                state_rcsizeunit_2_out = (max_size_i * 32'sd3) + 1;
                state_predictedsize_2_out = $signed({27'd0, predicted_leaf_i});
            end
            if (unit == 32'sd3) begin
                state_rcsizeunit_3_out = (max_size_i * 32'sd3) + 1;
                state_predictedsize_3_out = $signed({27'd0, predicted_leaf_i});
            end
        end
    end
endmodule
