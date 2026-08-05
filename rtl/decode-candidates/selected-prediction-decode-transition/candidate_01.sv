module predictionloop_decode_transition(
    input logic signed [31:0] hpos,
    input logic signed [31:0] vpos,
    input logic signed [31:0] sampmodcnt,
    input logic signed [31:0] qp,
    input logic signed [31:0] cfg_native_420,
    input logic signed [31:0] cfg_dsc_version_minor,
    input logic signed [31:0] state_is_encoder,
    input logic signed [31:0] state_units_per_group,
    input logic signed [31:0] state_cpnt_bit_depth_0,
    input logic signed [31:0] state_cpnt_bit_depth_1,
    input logic signed [31:0] state_cpnt_bit_depth_2,
    input logic signed [31:0] state_cpnt_bit_depth_3,
    input logic signed [31:0] state_unit_c_type_0,
    input logic signed [31:0] state_unit_c_type_1,
    input logic signed [31:0] state_unit_c_type_2,
    input logic signed [31:0] state_unit_c_type_3,
    input logic signed [31:0] state_unit_start_hpos_0,
    input logic signed [31:0] state_unit_start_hpos_1,
    input logic signed [31:0] state_unit_start_hpos_2,
    input logic signed [31:0] state_unit_start_hpos_3,
    input logic signed [31:0] state_use_midpoint_0,
    input logic signed [31:0] state_use_midpoint_1,
    input logic signed [31:0] state_use_midpoint_2,
    input logic signed [31:0] state_use_midpoint_3,
    input logic signed [31:0] state_left_recon_0,
    input logic signed [31:0] state_left_recon_1,
    input logic signed [31:0] state_left_recon_2,
    input logic signed [31:0] state_left_recon_3,
    input logic signed [31:0] state_quantized_residual_0_0,
    input logic signed [31:0] state_quantized_residual_0_1,
    input logic signed [31:0] state_quantized_residual_0_2,
    input logic signed [31:0] state_quantized_residual_1_0,
    input logic signed [31:0] state_quantized_residual_1_1,
    input logic signed [31:0] state_quantized_residual_1_2,
    input logic signed [31:0] state_quantized_residual_2_0,
    input logic signed [31:0] state_quantized_residual_2_1,
    input logic signed [31:0] state_quantized_residual_2_2,
    input logic signed [31:0] state_quantized_residual_3_0,
    input logic signed [31:0] state_quantized_residual_3_1,
    input logic signed [31:0] state_quantized_residual_3_2,
    input logic signed [31:0] qlevel_luma_qp,
    input logic signed [31:0] qlevel_chroma_qp,
    input logic signed [31:0] prev_line_prediction,
    input logic signed [31:0] prev_line_unit_0_tap_0,
    input logic signed [31:0] prev_line_unit_0_tap_1,
    input logic signed [31:0] prev_line_unit_0_tap_2,
    input logic signed [31:0] prev_line_unit_0_tap_3,
    input logic signed [31:0] prev_line_unit_0_tap_4,
    input logic signed [31:0] prev_line_unit_0_tap_5,
    input logic signed [31:0] prev_line_unit_1_tap_0,
    input logic signed [31:0] prev_line_unit_1_tap_1,
    input logic signed [31:0] prev_line_unit_1_tap_2,
    input logic signed [31:0] prev_line_unit_1_tap_3,
    input logic signed [31:0] prev_line_unit_1_tap_4,
    input logic signed [31:0] prev_line_unit_1_tap_5,
    input logic signed [31:0] prev_line_unit_2_tap_0,
    input logic signed [31:0] prev_line_unit_2_tap_1,
    input logic signed [31:0] prev_line_unit_2_tap_2,
    input logic signed [31:0] prev_line_unit_2_tap_3,
    input logic signed [31:0] prev_line_unit_2_tap_4,
    input logic signed [31:0] prev_line_unit_2_tap_5,
    input logic signed [31:0] prev_line_unit_3_tap_0,
    input logic signed [31:0] prev_line_unit_3_tap_1,
    input logic signed [31:0] prev_line_unit_3_tap_2,
    input logic signed [31:0] prev_line_unit_3_tap_3,
    input logic signed [31:0] prev_line_unit_3_tap_4,
    input logic signed [31:0] prev_line_unit_3_tap_5,
    input logic signed [31:0] curr_line_unit_0_a,
    input logic signed [31:0] curr_line_unit_1_a,
    input logic signed [31:0] curr_line_unit_2_a,
    input logic signed [31:0] curr_line_unit_3_a,
    input logic signed [31:0] curr_line_unit_0_block,
    input logic signed [31:0] curr_line_unit_1_block,
    input logic signed [31:0] curr_line_unit_2_block,
    input logic signed [31:0] curr_line_unit_3_block,
    output logic domain_valid,
    output logic line_write_0_enable,
    output logic signed [31:0] line_write_0_component,
    output logic signed [31:0] line_write_0_index,
    output logic signed [31:0] line_write_0_value,
    output logic line_write_1_enable,
    output logic signed [31:0] line_write_1_component,
    output logic signed [31:0] line_write_1_index,
    output logic signed [31:0] line_write_1_value,
    output logic line_write_2_enable,
    output logic signed [31:0] line_write_2_component,
    output logic signed [31:0] line_write_2_index,
    output logic signed [31:0] line_write_2_value,
    output logic line_write_3_enable,
    output logic signed [31:0] line_write_3_component,
    output logic signed [31:0] line_write_3_index,
    output logic signed [31:0] line_write_3_value
);
    logic signed [31:0] cpnt_0_i;
    logic signed [31:0] depth_0_i;
    logic signed [31:0] qlevel_0_i;
    logic signed [31:0] pred_type_0_i;
    logic signed [31:0] pred_0_i;
    logic signed [31:0] residual_index_0_i;
    logic signed [31:0] err_0_i;
    logic signed [31:0] max_value_0_i;
    logic signed [31:0] recon_0_i;
    logic signed [31:0] cpnt_1_i;
    logic signed [31:0] depth_1_i;
    logic signed [31:0] qlevel_1_i;
    logic signed [31:0] pred_type_1_i;
    logic signed [31:0] pred_1_i;
    logic signed [31:0] residual_index_1_i;
    logic signed [31:0] err_1_i;
    logic signed [31:0] max_value_1_i;
    logic signed [31:0] recon_1_i;
    logic signed [31:0] cpnt_2_i;
    logic signed [31:0] depth_2_i;
    logic signed [31:0] qlevel_2_i;
    logic signed [31:0] pred_type_2_i;
    logic signed [31:0] pred_2_i;
    logic signed [31:0] residual_index_2_i;
    logic signed [31:0] err_2_i;
    logic signed [31:0] max_value_2_i;
    logic signed [31:0] recon_2_i;
    logic signed [31:0] cpnt_3_i;
    logic signed [31:0] depth_3_i;
    logic signed [31:0] qlevel_3_i;
    logic signed [31:0] pred_type_3_i;
    logic signed [31:0] pred_3_i;
    logic signed [31:0] residual_index_3_i;
    logic signed [31:0] err_3_i;
    logic signed [31:0] max_value_3_i;
    logic signed [31:0] recon_3_i;

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

    function automatic signed [31:0] dsc_cicd_map_qlevel(
        input logic signed [31:0] cpnt_i,
        input logic signed [31:0] native_i,
        input logic signed [31:0] version_i,
        input logic signed [31:0] depth0_i,
        input logic signed [31:0] depth1_i,
        input logic signed [31:0] luma_i,
        input logic signed [31:0] chroma_i);
        logic signed [31:0] mapped_i;
        begin
            if ((cpnt_i % 32'sd3) == 0) mapped_i = luma_i;
            else if ((native_i != 0) && (cpnt_i == 32'sd1)) mapped_i = luma_i;
            else begin
                mapped_i = chroma_i;
                if ((version_i == 32'sd2) && (depth0_i == depth1_i) && (mapped_i > 0))
                    mapped_i = mapped_i - 1;
            end
            dsc_cicd_map_qlevel = mapped_i;
        end
    endfunction

    function automatic signed [31:0] dsc_cicd_midpoint(
        input logic signed [31:0] depth_i,
        input logic signed [31:0] left_i,
        input logic signed [31:0] qlevel_i);
        begin
            dsc_cicd_midpoint = (32'sd1 <<< (depth_i - 1))
                + (left_i % (32'sd1 <<< qlevel_i));
        end
    endfunction

    function automatic signed [31:0] dsc_cicd_predict(
        input logic signed [31:0] hpos_i,
        input logic signed [31:0] pred_type_i,
        input logic signed [31:0] qlevel_i,
        input logic signed [31:0] depth_i,
        input logic signed [31:0] qr0_i,
        input logic signed [31:0] qr1_i,
        input logic signed [31:0] prev0_i,
        input logic signed [31:0] prev1_i,
        input logic signed [31:0] prev2_i,
        input logic signed [31:0] prev3_i,
        input logic signed [31:0] prev4_i,
        input logic signed [31:0] prev5_i,
        input logic signed [31:0] curr_a_i,
        input logic signed [31:0] curr_block_i);
        logic signed [31:0] a_i;
        logic signed [31:0] b_i;
        logic signed [31:0] c_i;
        logic signed [31:0] d_i;
        logic signed [31:0] e_i;
        logic signed [31:0] filt_b_i;
        logic signed [31:0] filt_c_i;
        logic signed [31:0] filt_d_i;
        logic signed [31:0] filt_e_i;
        logic signed [31:0] blend_b_i;
        logic signed [31:0] blend_c_i;
        logic signed [31:0] blend_d_i;
        logic signed [31:0] blend_e_i;
        logic signed [31:0] qdiv_i;
        logic signed [31:0] half_i;
        logic signed [31:0] result_i;
        begin
            a_i = curr_a_i;
            c_i = prev1_i; b_i = prev2_i; d_i = prev3_i; e_i = prev4_i;
            filt_c_i = (prev0_i + (32'sd2 * prev1_i) + prev2_i + 2) >>> 2;
            filt_b_i = (prev1_i + (32'sd2 * prev2_i) + prev3_i + 2) >>> 2;
            filt_d_i = (prev2_i + (32'sd2 * prev3_i) + prev4_i + 2) >>> 2;
            filt_e_i = (prev3_i + (32'sd2 * prev4_i) + prev5_i + 2) >>> 2;
            qdiv_i = 32'sd1 <<< qlevel_i;
            half_i = qdiv_i / 2;
            blend_c_i = c_i + dsc_cicd_clamp(filt_c_i - c_i, -half_i, half_i);
            blend_b_i = b_i + dsc_cicd_clamp(filt_b_i - b_i, -half_i, half_i);
            blend_d_i = d_i + dsc_cicd_clamp(filt_d_i - d_i, -half_i, half_i);
            blend_e_i = e_i + dsc_cicd_clamp(filt_e_i - e_i, -half_i, half_i);
            result_i = 0;
            if (pred_type_i == 32'sd0) begin
                if ((hpos_i / 32'sd3) == 0) blend_c_i = a_i;
                if ((hpos_i % 32'sd3) == 0)
                    result_i = dsc_cicd_clamp(a_i + blend_b_i - blend_c_i,
                        dsc_cicd_min(a_i, blend_b_i), dsc_cicd_max(a_i, blend_b_i));
                else if ((hpos_i % 32'sd3) == 1)
                    result_i = dsc_cicd_clamp(a_i + blend_d_i - blend_c_i + (qr0_i * qdiv_i),
                        dsc_cicd_min(dsc_cicd_min(a_i, blend_b_i), blend_d_i),
                        dsc_cicd_max(dsc_cicd_max(a_i, blend_b_i), blend_d_i));
                else
                    result_i = dsc_cicd_clamp(a_i + blend_e_i - blend_c_i
                            + ((qr0_i + qr1_i) * qdiv_i),
                        dsc_cicd_min(dsc_cicd_min(a_i, blend_b_i), dsc_cicd_min(blend_d_i, blend_e_i)),
                        dsc_cicd_max(dsc_cicd_max(a_i, blend_b_i), dsc_cicd_max(blend_d_i, blend_e_i)));
            end else if (pred_type_i == 32'sd1) begin
                result_i = a_i;
                if ((hpos_i % 32'sd3) == 1)
                    result_i = dsc_cicd_clamp(a_i + (qr0_i * qdiv_i), 0,
                        (32'sd1 <<< depth_i) - 1);
                else if ((hpos_i % 32'sd3) == 2)
                    result_i = dsc_cicd_clamp(a_i + ((qr0_i + qr1_i) * qdiv_i), 0,
                        (32'sd1 <<< depth_i) - 1);
            end else result_i = curr_block_i;
            dsc_cicd_predict = result_i;
        end
    endfunction

    always_comb begin
        domain_valid = 1'b1;
        line_write_0_enable = 1'b0;
        line_write_0_component = 32'sd0;
        line_write_0_index = 32'sd0;
        line_write_0_value = 32'sd0;
        cpnt_0_i = state_unit_c_type_0;
        depth_0_i = ((cpnt_0_i == 32'sd0) ? state_cpnt_bit_depth_0 : ((cpnt_0_i == 32'sd1) ? state_cpnt_bit_depth_1 : ((cpnt_0_i == 32'sd2) ? state_cpnt_bit_depth_2 : state_cpnt_bit_depth_3)));
        qlevel_0_i = dsc_cicd_map_qlevel(cpnt_0_i, cfg_native_420, cfg_dsc_version_minor, state_cpnt_bit_depth_0, state_cpnt_bit_depth_1, qlevel_luma_qp, qlevel_chroma_qp);
        residual_index_0_i = sampmodcnt - state_unit_start_hpos_0;
        pred_type_0_i = (vpos == 0) ? 32'sd1 : prev_line_prediction;
        if ((cfg_native_420 != 0) && (cpnt_0_i == 32'sd2))
            pred_type_0_i = (vpos <= 1) ? 32'sd1 : 32'sd0;
        err_0_i = (residual_index_0_i == 0) ? state_quantized_residual_0_0 : ((residual_index_0_i == 1) ? state_quantized_residual_0_1 : state_quantized_residual_0_2);
        pred_0_i = dsc_cicd_predict(hpos, pred_type_0_i, qlevel_0_i, depth_0_i, state_quantized_residual_0_0, state_quantized_residual_0_1, prev_line_unit_0_tap_0, prev_line_unit_0_tap_1, prev_line_unit_0_tap_2, prev_line_unit_0_tap_3, prev_line_unit_0_tap_4, prev_line_unit_0_tap_5, curr_line_unit_0_a, curr_line_unit_0_block);
        if (state_use_midpoint_0 != 0)
            pred_0_i = dsc_cicd_midpoint(depth_0_i, ((cpnt_0_i == 32'sd0) ? state_left_recon_0 : ((cpnt_0_i == 32'sd1) ? state_left_recon_1 : ((cpnt_0_i == 32'sd2) ? state_left_recon_2 : state_left_recon_3))), qlevel_0_i);
        max_value_0_i = (32'sd1 <<< depth_0_i) - 1;
        recon_0_i = dsc_cicd_clamp(pred_0_i + (err_0_i <<< qlevel_0_i), 0, max_value_0_i);
        line_write_1_enable = 1'b0;
        line_write_1_component = 32'sd0;
        line_write_1_index = 32'sd0;
        line_write_1_value = 32'sd0;
        cpnt_1_i = state_unit_c_type_1;
        depth_1_i = ((cpnt_1_i == 32'sd0) ? state_cpnt_bit_depth_0 : ((cpnt_1_i == 32'sd1) ? state_cpnt_bit_depth_1 : ((cpnt_1_i == 32'sd2) ? state_cpnt_bit_depth_2 : state_cpnt_bit_depth_3)));
        qlevel_1_i = dsc_cicd_map_qlevel(cpnt_1_i, cfg_native_420, cfg_dsc_version_minor, state_cpnt_bit_depth_0, state_cpnt_bit_depth_1, qlevel_luma_qp, qlevel_chroma_qp);
        residual_index_1_i = sampmodcnt - state_unit_start_hpos_1;
        pred_type_1_i = (vpos == 0) ? 32'sd1 : prev_line_prediction;
        if ((cfg_native_420 != 0) && (cpnt_1_i == 32'sd2))
            pred_type_1_i = (vpos <= 1) ? 32'sd1 : 32'sd0;
        err_1_i = (residual_index_1_i == 0) ? state_quantized_residual_1_0 : ((residual_index_1_i == 1) ? state_quantized_residual_1_1 : state_quantized_residual_1_2);
        pred_1_i = dsc_cicd_predict(hpos, pred_type_1_i, qlevel_1_i, depth_1_i, state_quantized_residual_1_0, state_quantized_residual_1_1, prev_line_unit_1_tap_0, prev_line_unit_1_tap_1, prev_line_unit_1_tap_2, prev_line_unit_1_tap_3, prev_line_unit_1_tap_4, prev_line_unit_1_tap_5, curr_line_unit_1_a, curr_line_unit_1_block);
        if (state_use_midpoint_1 != 0)
            pred_1_i = dsc_cicd_midpoint(depth_1_i, ((cpnt_1_i == 32'sd0) ? state_left_recon_0 : ((cpnt_1_i == 32'sd1) ? state_left_recon_1 : ((cpnt_1_i == 32'sd2) ? state_left_recon_2 : state_left_recon_3))), qlevel_1_i);
        max_value_1_i = (32'sd1 <<< depth_1_i) - 1;
        recon_1_i = dsc_cicd_clamp(pred_1_i + (err_1_i <<< qlevel_1_i), 0, max_value_1_i);
        line_write_2_enable = 1'b0;
        line_write_2_component = 32'sd0;
        line_write_2_index = 32'sd0;
        line_write_2_value = 32'sd0;
        cpnt_2_i = state_unit_c_type_2;
        depth_2_i = ((cpnt_2_i == 32'sd0) ? state_cpnt_bit_depth_0 : ((cpnt_2_i == 32'sd1) ? state_cpnt_bit_depth_1 : ((cpnt_2_i == 32'sd2) ? state_cpnt_bit_depth_2 : state_cpnt_bit_depth_3)));
        qlevel_2_i = dsc_cicd_map_qlevel(cpnt_2_i, cfg_native_420, cfg_dsc_version_minor, state_cpnt_bit_depth_0, state_cpnt_bit_depth_1, qlevel_luma_qp, qlevel_chroma_qp);
        residual_index_2_i = sampmodcnt - state_unit_start_hpos_2;
        pred_type_2_i = (vpos == 0) ? 32'sd1 : prev_line_prediction;
        if ((cfg_native_420 != 0) && (cpnt_2_i == 32'sd2))
            pred_type_2_i = (vpos <= 1) ? 32'sd1 : 32'sd0;
        err_2_i = (residual_index_2_i == 0) ? state_quantized_residual_2_0 : ((residual_index_2_i == 1) ? state_quantized_residual_2_1 : state_quantized_residual_2_2);
        pred_2_i = dsc_cicd_predict(hpos, pred_type_2_i, qlevel_2_i, depth_2_i, state_quantized_residual_2_0, state_quantized_residual_2_1, prev_line_unit_2_tap_0, prev_line_unit_2_tap_1, prev_line_unit_2_tap_2, prev_line_unit_2_tap_3, prev_line_unit_2_tap_4, prev_line_unit_2_tap_5, curr_line_unit_2_a, curr_line_unit_2_block);
        if (state_use_midpoint_2 != 0)
            pred_2_i = dsc_cicd_midpoint(depth_2_i, ((cpnt_2_i == 32'sd0) ? state_left_recon_0 : ((cpnt_2_i == 32'sd1) ? state_left_recon_1 : ((cpnt_2_i == 32'sd2) ? state_left_recon_2 : state_left_recon_3))), qlevel_2_i);
        max_value_2_i = (32'sd1 <<< depth_2_i) - 1;
        recon_2_i = dsc_cicd_clamp(pred_2_i + (err_2_i <<< qlevel_2_i), 0, max_value_2_i);
        line_write_3_enable = 1'b0;
        line_write_3_component = 32'sd0;
        line_write_3_index = 32'sd0;
        line_write_3_value = 32'sd0;
        cpnt_3_i = state_unit_c_type_3;
        depth_3_i = ((cpnt_3_i == 32'sd0) ? state_cpnt_bit_depth_0 : ((cpnt_3_i == 32'sd1) ? state_cpnt_bit_depth_1 : ((cpnt_3_i == 32'sd2) ? state_cpnt_bit_depth_2 : state_cpnt_bit_depth_3)));
        qlevel_3_i = dsc_cicd_map_qlevel(cpnt_3_i, cfg_native_420, cfg_dsc_version_minor, state_cpnt_bit_depth_0, state_cpnt_bit_depth_1, qlevel_luma_qp, qlevel_chroma_qp);
        residual_index_3_i = sampmodcnt - state_unit_start_hpos_3;
        pred_type_3_i = (vpos == 0) ? 32'sd1 : prev_line_prediction;
        if ((cfg_native_420 != 0) && (cpnt_3_i == 32'sd2))
            pred_type_3_i = (vpos <= 1) ? 32'sd1 : 32'sd0;
        err_3_i = (residual_index_3_i == 0) ? state_quantized_residual_3_0 : ((residual_index_3_i == 1) ? state_quantized_residual_3_1 : state_quantized_residual_3_2);
        pred_3_i = dsc_cicd_predict(hpos, pred_type_3_i, qlevel_3_i, depth_3_i, state_quantized_residual_3_0, state_quantized_residual_3_1, prev_line_unit_3_tap_0, prev_line_unit_3_tap_1, prev_line_unit_3_tap_2, prev_line_unit_3_tap_3, prev_line_unit_3_tap_4, prev_line_unit_3_tap_5, curr_line_unit_3_a, curr_line_unit_3_block);
        if (state_use_midpoint_3 != 0)
            pred_3_i = dsc_cicd_midpoint(depth_3_i, ((cpnt_3_i == 32'sd0) ? state_left_recon_0 : ((cpnt_3_i == 32'sd1) ? state_left_recon_1 : ((cpnt_3_i == 32'sd2) ? state_left_recon_2 : state_left_recon_3))), qlevel_3_i);
        max_value_3_i = (32'sd1 <<< depth_3_i) - 1;
        recon_3_i = dsc_cicd_clamp(pred_3_i + (err_3_i <<< qlevel_3_i), 0, max_value_3_i);
        if ((state_is_encoder != 0) || (state_units_per_group < 3) || (state_units_per_group > 4) || (hpos < 0) || (vpos < 0) || (sampmodcnt < 0) || (sampmodcnt >= 3) || (qp < 0) || (qp > 31) || (qlevel_luma_qp < 0) || (qlevel_luma_qp > 16) || (qlevel_chroma_qp < 0) || (qlevel_chroma_qp > 16) || (prev_line_prediction < 0) || (prev_line_prediction > 11)) domain_valid = 1'b0;
        if (state_units_per_group > 0) begin
            if ((cpnt_0_i < 0) || (cpnt_0_i >= 4) || (depth_0_i < 8) || (depth_0_i > 16) || (qlevel_0_i < 0) || (qlevel_0_i > depth_0_i) || (residual_index_0_i < 0) || (residual_index_0_i >= 3)) domain_valid = 1'b0;
            line_write_0_enable = 1'b1;
            line_write_0_component = cpnt_0_i;
            line_write_0_index = hpos + 32'sd5;
            line_write_0_value = recon_0_i;
        end
        if (state_units_per_group > 1) begin
            if ((cpnt_1_i < 0) || (cpnt_1_i >= 4) || (depth_1_i < 8) || (depth_1_i > 16) || (qlevel_1_i < 0) || (qlevel_1_i > depth_1_i) || (residual_index_1_i < 0) || (residual_index_1_i >= 3)) domain_valid = 1'b0;
            if ((state_units_per_group > 0) && (cpnt_1_i == cpnt_0_i)) domain_valid = 1'b0;
            line_write_1_enable = 1'b1;
            line_write_1_component = cpnt_1_i;
            line_write_1_index = hpos + 32'sd5;
            line_write_1_value = recon_1_i;
        end
        if (state_units_per_group > 2) begin
            if ((cpnt_2_i < 0) || (cpnt_2_i >= 4) || (depth_2_i < 8) || (depth_2_i > 16) || (qlevel_2_i < 0) || (qlevel_2_i > depth_2_i) || (residual_index_2_i < 0) || (residual_index_2_i >= 3)) domain_valid = 1'b0;
            if ((state_units_per_group > 0) && (cpnt_2_i == cpnt_0_i)) domain_valid = 1'b0;
            if ((state_units_per_group > 1) && (cpnt_2_i == cpnt_1_i)) domain_valid = 1'b0;
            line_write_2_enable = 1'b1;
            line_write_2_component = cpnt_2_i;
            line_write_2_index = hpos + 32'sd5;
            line_write_2_value = recon_2_i;
        end
        if (state_units_per_group > 3) begin
            if ((cpnt_3_i < 0) || (cpnt_3_i >= 4) || (depth_3_i < 8) || (depth_3_i > 16) || (qlevel_3_i < 0) || (qlevel_3_i > depth_3_i) || (residual_index_3_i < 0) || (residual_index_3_i >= 3)) domain_valid = 1'b0;
            if ((state_units_per_group > 0) && (cpnt_3_i == cpnt_0_i)) domain_valid = 1'b0;
            if ((state_units_per_group > 1) && (cpnt_3_i == cpnt_1_i)) domain_valid = 1'b0;
            if ((state_units_per_group > 2) && (cpnt_3_i == cpnt_2_i)) domain_valid = 1'b0;
            line_write_3_enable = 1'b1;
            line_write_3_component = cpnt_3_i;
            line_write_3_index = hpos + 32'sd5;
            line_write_3_value = recon_3_i;
        end
    end
endmodule
