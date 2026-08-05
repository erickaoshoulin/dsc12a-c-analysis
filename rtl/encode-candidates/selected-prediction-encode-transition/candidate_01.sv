module predictionloop_encode_transition(
    input logic signed [31:0] hpos,
    input logic signed [31:0] vpos,
    input logic signed [31:0] sampmodcnt,
    input logic signed [31:0] qp,
    input logic signed [31:0] cfg_native_420,
    input logic signed [31:0] cfg_dsc_version_minor,
    input logic signed [31:0] cfg_bits_per_component,
    input logic signed [31:0] cfg_full_ich_err_precision,
    input logic signed [31:0] state_is_encoder,
    input logic signed [31:0] state_units_per_group,
    input logic signed [31:0] state_primary_qp,
    input logic signed [31:0] state_prev_line_prediction,
    input logic signed [31:0] state_qlevel_luma_qp,
    input logic signed [31:0] state_qlevel_chroma_qp,
    input logic signed [31:0] state_cpnt_bit_depth_0,
    input logic signed [31:0] state_left_recon_0,
    input logic signed [31:0] state_cpnt_bit_depth_1,
    input logic signed [31:0] state_left_recon_1,
    input logic signed [31:0] state_cpnt_bit_depth_2,
    input logic signed [31:0] state_left_recon_2,
    input logic signed [31:0] state_cpnt_bit_depth_3,
    input logic signed [31:0] state_left_recon_3,
    input logic signed [31:0] state_unit_c_type_0,
    input logic signed [31:0] state_unit_start_hpos_0,
    input logic signed [31:0] state_max_error_0,
    input logic signed [31:0] state_max_mid_error_0,
    input logic signed [31:0] orig_sample_0,
    input logic signed [31:0] state_quantized_residual_0_0,
    input logic signed [31:0] state_quantized_residual_mid_0_0,
    input logic signed [31:0] state_quantized_residual_0_1,
    input logic signed [31:0] state_quantized_residual_mid_0_1,
    input logic signed [31:0] state_quantized_residual_0_2,
    input logic signed [31:0] state_quantized_residual_mid_0_2,
    input logic signed [31:0] state_midpoint_recon_0_0,
    input logic signed [31:0] state_midpoint_recon_0_1,
    input logic signed [31:0] state_midpoint_recon_0_2,
    input logic signed [31:0] state_midpoint_recon_0_3,
    input logic signed [31:0] state_midpoint_recon_0_4,
    input logic signed [31:0] state_midpoint_recon_0_5,
    input logic signed [31:0] prev_line_unit_0_tap_0,
    input logic signed [31:0] prev_line_unit_0_tap_1,
    input logic signed [31:0] prev_line_unit_0_tap_2,
    input logic signed [31:0] prev_line_unit_0_tap_3,
    input logic signed [31:0] prev_line_unit_0_tap_4,
    input logic signed [31:0] prev_line_unit_0_tap_5,
    input logic signed [31:0] prev_line_unit_0_tap_6,
    input logic signed [31:0] prev_line_unit_0_tap_7,
    input logic signed [31:0] prev_line_unit_0_tap_8,
    input logic signed [31:0] prev_line_unit_0_tap_9,
    input logic signed [31:0] prev_line_unit_0_tap_10,
    input logic signed [31:0] prev_line_unit_0_tap_11,
    input logic signed [31:0] prev_line_unit_0_tap_12,
    input logic signed [31:0] prev_line_unit_0_tap_13,
    input logic signed [31:0] prev_line_unit_0_tap_14,
    input logic signed [31:0] curr_line_unit_0_tap_0,
    input logic signed [31:0] curr_line_unit_0_tap_1,
    input logic signed [31:0] curr_line_unit_0_tap_2,
    input logic signed [31:0] curr_line_unit_0_tap_3,
    input logic signed [31:0] curr_line_unit_0_tap_4,
    input logic signed [31:0] curr_line_unit_0_tap_5,
    input logic signed [31:0] curr_line_unit_0_tap_6,
    input logic signed [31:0] curr_line_unit_0_tap_7,
    input logic signed [31:0] curr_line_unit_0_tap_8,
    input logic signed [31:0] curr_line_unit_0_tap_9,
    input logic signed [31:0] curr_line_unit_0_tap_10,
    input logic signed [31:0] curr_line_unit_0_tap_11,
    input logic signed [31:0] curr_line_unit_0_tap_12,
    input logic signed [31:0] curr_line_unit_0_tap_13,
    input logic signed [31:0] curr_line_unit_0_tap_14,
    input logic signed [31:0] curr_line_unit_0_tap_15,
    input logic signed [31:0] state_unit_c_type_1,
    input logic signed [31:0] state_unit_start_hpos_1,
    input logic signed [31:0] state_max_error_1,
    input logic signed [31:0] state_max_mid_error_1,
    input logic signed [31:0] orig_sample_1,
    input logic signed [31:0] state_quantized_residual_1_0,
    input logic signed [31:0] state_quantized_residual_mid_1_0,
    input logic signed [31:0] state_quantized_residual_1_1,
    input logic signed [31:0] state_quantized_residual_mid_1_1,
    input logic signed [31:0] state_quantized_residual_1_2,
    input logic signed [31:0] state_quantized_residual_mid_1_2,
    input logic signed [31:0] state_midpoint_recon_1_0,
    input logic signed [31:0] state_midpoint_recon_1_1,
    input logic signed [31:0] state_midpoint_recon_1_2,
    input logic signed [31:0] state_midpoint_recon_1_3,
    input logic signed [31:0] state_midpoint_recon_1_4,
    input logic signed [31:0] state_midpoint_recon_1_5,
    input logic signed [31:0] prev_line_unit_1_tap_0,
    input logic signed [31:0] prev_line_unit_1_tap_1,
    input logic signed [31:0] prev_line_unit_1_tap_2,
    input logic signed [31:0] prev_line_unit_1_tap_3,
    input logic signed [31:0] prev_line_unit_1_tap_4,
    input logic signed [31:0] prev_line_unit_1_tap_5,
    input logic signed [31:0] prev_line_unit_1_tap_6,
    input logic signed [31:0] prev_line_unit_1_tap_7,
    input logic signed [31:0] prev_line_unit_1_tap_8,
    input logic signed [31:0] prev_line_unit_1_tap_9,
    input logic signed [31:0] prev_line_unit_1_tap_10,
    input logic signed [31:0] prev_line_unit_1_tap_11,
    input logic signed [31:0] prev_line_unit_1_tap_12,
    input logic signed [31:0] prev_line_unit_1_tap_13,
    input logic signed [31:0] prev_line_unit_1_tap_14,
    input logic signed [31:0] curr_line_unit_1_tap_0,
    input logic signed [31:0] curr_line_unit_1_tap_1,
    input logic signed [31:0] curr_line_unit_1_tap_2,
    input logic signed [31:0] curr_line_unit_1_tap_3,
    input logic signed [31:0] curr_line_unit_1_tap_4,
    input logic signed [31:0] curr_line_unit_1_tap_5,
    input logic signed [31:0] curr_line_unit_1_tap_6,
    input logic signed [31:0] curr_line_unit_1_tap_7,
    input logic signed [31:0] curr_line_unit_1_tap_8,
    input logic signed [31:0] curr_line_unit_1_tap_9,
    input logic signed [31:0] curr_line_unit_1_tap_10,
    input logic signed [31:0] curr_line_unit_1_tap_11,
    input logic signed [31:0] curr_line_unit_1_tap_12,
    input logic signed [31:0] curr_line_unit_1_tap_13,
    input logic signed [31:0] curr_line_unit_1_tap_14,
    input logic signed [31:0] curr_line_unit_1_tap_15,
    input logic signed [31:0] state_unit_c_type_2,
    input logic signed [31:0] state_unit_start_hpos_2,
    input logic signed [31:0] state_max_error_2,
    input logic signed [31:0] state_max_mid_error_2,
    input logic signed [31:0] orig_sample_2,
    input logic signed [31:0] state_quantized_residual_2_0,
    input logic signed [31:0] state_quantized_residual_mid_2_0,
    input logic signed [31:0] state_quantized_residual_2_1,
    input logic signed [31:0] state_quantized_residual_mid_2_1,
    input logic signed [31:0] state_quantized_residual_2_2,
    input logic signed [31:0] state_quantized_residual_mid_2_2,
    input logic signed [31:0] state_midpoint_recon_2_0,
    input logic signed [31:0] state_midpoint_recon_2_1,
    input logic signed [31:0] state_midpoint_recon_2_2,
    input logic signed [31:0] state_midpoint_recon_2_3,
    input logic signed [31:0] state_midpoint_recon_2_4,
    input logic signed [31:0] state_midpoint_recon_2_5,
    input logic signed [31:0] prev_line_unit_2_tap_0,
    input logic signed [31:0] prev_line_unit_2_tap_1,
    input logic signed [31:0] prev_line_unit_2_tap_2,
    input logic signed [31:0] prev_line_unit_2_tap_3,
    input logic signed [31:0] prev_line_unit_2_tap_4,
    input logic signed [31:0] prev_line_unit_2_tap_5,
    input logic signed [31:0] prev_line_unit_2_tap_6,
    input logic signed [31:0] prev_line_unit_2_tap_7,
    input logic signed [31:0] prev_line_unit_2_tap_8,
    input logic signed [31:0] prev_line_unit_2_tap_9,
    input logic signed [31:0] prev_line_unit_2_tap_10,
    input logic signed [31:0] prev_line_unit_2_tap_11,
    input logic signed [31:0] prev_line_unit_2_tap_12,
    input logic signed [31:0] prev_line_unit_2_tap_13,
    input logic signed [31:0] prev_line_unit_2_tap_14,
    input logic signed [31:0] curr_line_unit_2_tap_0,
    input logic signed [31:0] curr_line_unit_2_tap_1,
    input logic signed [31:0] curr_line_unit_2_tap_2,
    input logic signed [31:0] curr_line_unit_2_tap_3,
    input logic signed [31:0] curr_line_unit_2_tap_4,
    input logic signed [31:0] curr_line_unit_2_tap_5,
    input logic signed [31:0] curr_line_unit_2_tap_6,
    input logic signed [31:0] curr_line_unit_2_tap_7,
    input logic signed [31:0] curr_line_unit_2_tap_8,
    input logic signed [31:0] curr_line_unit_2_tap_9,
    input logic signed [31:0] curr_line_unit_2_tap_10,
    input logic signed [31:0] curr_line_unit_2_tap_11,
    input logic signed [31:0] curr_line_unit_2_tap_12,
    input logic signed [31:0] curr_line_unit_2_tap_13,
    input logic signed [31:0] curr_line_unit_2_tap_14,
    input logic signed [31:0] curr_line_unit_2_tap_15,
    input logic signed [31:0] state_unit_c_type_3,
    input logic signed [31:0] state_unit_start_hpos_3,
    input logic signed [31:0] state_max_error_3,
    input logic signed [31:0] state_max_mid_error_3,
    input logic signed [31:0] orig_sample_3,
    input logic signed [31:0] state_quantized_residual_3_0,
    input logic signed [31:0] state_quantized_residual_mid_3_0,
    input logic signed [31:0] state_quantized_residual_3_1,
    input logic signed [31:0] state_quantized_residual_mid_3_1,
    input logic signed [31:0] state_quantized_residual_3_2,
    input logic signed [31:0] state_quantized_residual_mid_3_2,
    input logic signed [31:0] state_midpoint_recon_3_0,
    input logic signed [31:0] state_midpoint_recon_3_1,
    input logic signed [31:0] state_midpoint_recon_3_2,
    input logic signed [31:0] state_midpoint_recon_3_3,
    input logic signed [31:0] state_midpoint_recon_3_4,
    input logic signed [31:0] state_midpoint_recon_3_5,
    input logic signed [31:0] prev_line_unit_3_tap_0,
    input logic signed [31:0] prev_line_unit_3_tap_1,
    input logic signed [31:0] prev_line_unit_3_tap_2,
    input logic signed [31:0] prev_line_unit_3_tap_3,
    input logic signed [31:0] prev_line_unit_3_tap_4,
    input logic signed [31:0] prev_line_unit_3_tap_5,
    input logic signed [31:0] prev_line_unit_3_tap_6,
    input logic signed [31:0] prev_line_unit_3_tap_7,
    input logic signed [31:0] prev_line_unit_3_tap_8,
    input logic signed [31:0] prev_line_unit_3_tap_9,
    input logic signed [31:0] prev_line_unit_3_tap_10,
    input logic signed [31:0] prev_line_unit_3_tap_11,
    input logic signed [31:0] prev_line_unit_3_tap_12,
    input logic signed [31:0] prev_line_unit_3_tap_13,
    input logic signed [31:0] prev_line_unit_3_tap_14,
    input logic signed [31:0] curr_line_unit_3_tap_0,
    input logic signed [31:0] curr_line_unit_3_tap_1,
    input logic signed [31:0] curr_line_unit_3_tap_2,
    input logic signed [31:0] curr_line_unit_3_tap_3,
    input logic signed [31:0] curr_line_unit_3_tap_4,
    input logic signed [31:0] curr_line_unit_3_tap_5,
    input logic signed [31:0] curr_line_unit_3_tap_6,
    input logic signed [31:0] curr_line_unit_3_tap_7,
    input logic signed [31:0] curr_line_unit_3_tap_8,
    input logic signed [31:0] curr_line_unit_3_tap_9,
    input logic signed [31:0] curr_line_unit_3_tap_10,
    input logic signed [31:0] curr_line_unit_3_tap_11,
    input logic signed [31:0] curr_line_unit_3_tap_12,
    input logic signed [31:0] curr_line_unit_3_tap_13,
    input logic signed [31:0] curr_line_unit_3_tap_14,
    input logic signed [31:0] curr_line_unit_3_tap_15,
    output logic domain_valid,
    output logic illegal_domain,
    output logic bound_violation,
    output logic midpoint_clamp_violation,
    output logic arithmetic_domain_violation,
    output logic signed [31:0] state_primary_qp_out,
    output logic signed [31:0] state_quantized_residual_0_0_out,
    output logic signed [31:0] state_quantized_residual_mid_0_0_out,
    output logic signed [31:0] state_quantized_residual_0_1_out,
    output logic signed [31:0] state_quantized_residual_mid_0_1_out,
    output logic signed [31:0] state_quantized_residual_0_2_out,
    output logic signed [31:0] state_quantized_residual_mid_0_2_out,
    output logic signed [31:0] state_midpoint_recon_0_0_out,
    output logic signed [31:0] state_midpoint_recon_0_1_out,
    output logic signed [31:0] state_midpoint_recon_0_2_out,
    output logic signed [31:0] state_midpoint_recon_0_3_out,
    output logic signed [31:0] state_midpoint_recon_0_4_out,
    output logic signed [31:0] state_midpoint_recon_0_5_out,
    output logic signed [31:0] state_max_error_0_out,
    output logic signed [31:0] state_max_mid_error_0_out,
    output logic curr_line_write_0_enable,
    output logic signed [31:0] curr_line_write_0_component,
    output logic signed [31:0] curr_line_write_0_index,
    output logic signed [31:0] curr_line_write_0_value,
    output logic signed [31:0] state_quantized_residual_1_0_out,
    output logic signed [31:0] state_quantized_residual_mid_1_0_out,
    output logic signed [31:0] state_quantized_residual_1_1_out,
    output logic signed [31:0] state_quantized_residual_mid_1_1_out,
    output logic signed [31:0] state_quantized_residual_1_2_out,
    output logic signed [31:0] state_quantized_residual_mid_1_2_out,
    output logic signed [31:0] state_midpoint_recon_1_0_out,
    output logic signed [31:0] state_midpoint_recon_1_1_out,
    output logic signed [31:0] state_midpoint_recon_1_2_out,
    output logic signed [31:0] state_midpoint_recon_1_3_out,
    output logic signed [31:0] state_midpoint_recon_1_4_out,
    output logic signed [31:0] state_midpoint_recon_1_5_out,
    output logic signed [31:0] state_max_error_1_out,
    output logic signed [31:0] state_max_mid_error_1_out,
    output logic curr_line_write_1_enable,
    output logic signed [31:0] curr_line_write_1_component,
    output logic signed [31:0] curr_line_write_1_index,
    output logic signed [31:0] curr_line_write_1_value,
    output logic signed [31:0] state_quantized_residual_2_0_out,
    output logic signed [31:0] state_quantized_residual_mid_2_0_out,
    output logic signed [31:0] state_quantized_residual_2_1_out,
    output logic signed [31:0] state_quantized_residual_mid_2_1_out,
    output logic signed [31:0] state_quantized_residual_2_2_out,
    output logic signed [31:0] state_quantized_residual_mid_2_2_out,
    output logic signed [31:0] state_midpoint_recon_2_0_out,
    output logic signed [31:0] state_midpoint_recon_2_1_out,
    output logic signed [31:0] state_midpoint_recon_2_2_out,
    output logic signed [31:0] state_midpoint_recon_2_3_out,
    output logic signed [31:0] state_midpoint_recon_2_4_out,
    output logic signed [31:0] state_midpoint_recon_2_5_out,
    output logic signed [31:0] state_max_error_2_out,
    output logic signed [31:0] state_max_mid_error_2_out,
    output logic curr_line_write_2_enable,
    output logic signed [31:0] curr_line_write_2_component,
    output logic signed [31:0] curr_line_write_2_index,
    output logic signed [31:0] curr_line_write_2_value,
    output logic signed [31:0] state_quantized_residual_3_0_out,
    output logic signed [31:0] state_quantized_residual_mid_3_0_out,
    output logic signed [31:0] state_quantized_residual_3_1_out,
    output logic signed [31:0] state_quantized_residual_mid_3_1_out,
    output logic signed [31:0] state_quantized_residual_3_2_out,
    output logic signed [31:0] state_quantized_residual_mid_3_2_out,
    output logic signed [31:0] state_midpoint_recon_3_0_out,
    output logic signed [31:0] state_midpoint_recon_3_1_out,
    output logic signed [31:0] state_midpoint_recon_3_2_out,
    output logic signed [31:0] state_midpoint_recon_3_3_out,
    output logic signed [31:0] state_midpoint_recon_3_4_out,
    output logic signed [31:0] state_midpoint_recon_3_5_out,
    output logic signed [31:0] state_max_error_3_out,
    output logic signed [31:0] state_max_mid_error_3_out,
    output logic curr_line_write_3_enable,
    output logic signed [31:0] curr_line_write_3_component,
    output logic signed [31:0] curr_line_write_3_index,
    output logic signed [31:0] curr_line_write_3_value
);

    // Child contract pins are recorded in provisional-contract.json.
    // Their pure semantics are inlined here to keep this candidate standalone.
    logic signed [31:0] cpnt_0_i;
    logic signed [31:0] depth_0_i;
    logic signed [31:0] qlevel_0_i;
    logic signed [31:0] pred_type_0_i;
    logic signed [31:0] pred_0_i;
    logic signed [31:0] actual_0_i;
    logic signed [31:0] err_raw_0_i;
    logic signed [31:0] err_q_0_i;
    logic signed [31:0] qmid_initial_0_i;
    logic signed [31:0] qmid_0_i;
    logic signed [31:0] max_size_0_i;
    logic signed [31:0] max_value_0_i;
    logic signed [31:0] recon_0_i;
    logic signed [31:0] midpoint_pred_0_i;
    logic signed [31:0] midpoint_recon_0_i;
    logic signed [31:0] abs_error_0_i;
    logic signed [31:0] abs_mid_error_0_i;
    logic signed [31:0] residual_index_0_i;
    logic signed [31:0] find_size_0_i;
    logic signed [31:0] cpnt_1_i;
    logic signed [31:0] depth_1_i;
    logic signed [31:0] qlevel_1_i;
    logic signed [31:0] pred_type_1_i;
    logic signed [31:0] pred_1_i;
    logic signed [31:0] actual_1_i;
    logic signed [31:0] err_raw_1_i;
    logic signed [31:0] err_q_1_i;
    logic signed [31:0] qmid_initial_1_i;
    logic signed [31:0] qmid_1_i;
    logic signed [31:0] max_size_1_i;
    logic signed [31:0] max_value_1_i;
    logic signed [31:0] recon_1_i;
    logic signed [31:0] midpoint_pred_1_i;
    logic signed [31:0] midpoint_recon_1_i;
    logic signed [31:0] abs_error_1_i;
    logic signed [31:0] abs_mid_error_1_i;
    logic signed [31:0] residual_index_1_i;
    logic signed [31:0] find_size_1_i;
    logic signed [31:0] cpnt_2_i;
    logic signed [31:0] depth_2_i;
    logic signed [31:0] qlevel_2_i;
    logic signed [31:0] pred_type_2_i;
    logic signed [31:0] pred_2_i;
    logic signed [31:0] actual_2_i;
    logic signed [31:0] err_raw_2_i;
    logic signed [31:0] err_q_2_i;
    logic signed [31:0] qmid_initial_2_i;
    logic signed [31:0] qmid_2_i;
    logic signed [31:0] max_size_2_i;
    logic signed [31:0] max_value_2_i;
    logic signed [31:0] recon_2_i;
    logic signed [31:0] midpoint_pred_2_i;
    logic signed [31:0] midpoint_recon_2_i;
    logic signed [31:0] abs_error_2_i;
    logic signed [31:0] abs_mid_error_2_i;
    logic signed [31:0] residual_index_2_i;
    logic signed [31:0] find_size_2_i;
    logic signed [31:0] cpnt_3_i;
    logic signed [31:0] depth_3_i;
    logic signed [31:0] qlevel_3_i;
    logic signed [31:0] pred_type_3_i;
    logic signed [31:0] pred_3_i;
    logic signed [31:0] actual_3_i;
    logic signed [31:0] err_raw_3_i;
    logic signed [31:0] err_q_3_i;
    logic signed [31:0] qmid_initial_3_i;
    logic signed [31:0] qmid_3_i;
    logic signed [31:0] max_size_3_i;
    logic signed [31:0] max_value_3_i;
    logic signed [31:0] recon_3_i;
    logic signed [31:0] midpoint_pred_3_i;
    logic signed [31:0] midpoint_recon_3_i;
    logic signed [31:0] abs_error_3_i;
    logic signed [31:0] abs_mid_error_3_i;
    logic signed [31:0] residual_index_3_i;
    logic signed [31:0] find_size_3_i;

    function automatic signed [31:0] dsc_clamp_i(
        input logic signed [31:0] value_i,
        input logic signed [31:0] lower_i,
        input logic signed [31:0] upper_i);
        begin
            if (value_i < lower_i) dsc_clamp_i = lower_i;
            else if (value_i > upper_i) dsc_clamp_i = upper_i;
            else dsc_clamp_i = value_i;
        end
    endfunction

    function automatic signed [31:0] dsc_min_i(
        input logic signed [31:0] left_i,
        input logic signed [31:0] right_i);
        begin dsc_min_i = (left_i < right_i) ? left_i : right_i; end
    endfunction

    function automatic signed [31:0] dsc_max_i(
        input logic signed [31:0] left_i,
        input logic signed [31:0] right_i);
        begin dsc_max_i = (left_i > right_i) ? left_i : right_i; end
    endfunction

    function automatic signed [31:0] dsc_abs_i(
        input logic signed [31:0] value_i);
        begin dsc_abs_i = (value_i < 0) ? -value_i : value_i; end
    endfunction

    function automatic signed [31:0] dsc_map_qlevel_i(
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
                    mapped_i = mapped_i - 32'sd1;
            end
            dsc_map_qlevel_i = mapped_i;
        end
    endfunction

    function automatic signed [31:0] dsc_quantize_i(
        input logic signed [31:0] error_i,
        input logic signed [31:0] qlevel_i);
        logic signed [31:0] offset_i;
        begin
            offset_i = 32'sd0;
            case (qlevel_i)
                0: offset_i = 32'sd0;
                1: offset_i = 32'sd0;
                2: offset_i = 32'sd1;
                3: offset_i = 32'sd3;
                4: offset_i = 32'sd7;
                5: offset_i = 32'sd15;
                6: offset_i = 32'sd31;
                7: offset_i = 32'sd63;
                8: offset_i = 32'sd127;
                9: offset_i = 32'sd255;
                10: offset_i = 32'sd511;
                11: offset_i = 32'sd1023;
                12: offset_i = 32'sd2047;
                13: offset_i = 32'sd4095;
                14: offset_i = 32'sd8191;
                15: offset_i = 32'sd16383;
                16: offset_i = 32'sd32767;
                default: offset_i = 32'sd0;
            endcase
            if (error_i > 0)
                dsc_quantize_i = (error_i + offset_i) >>> qlevel_i;
            else
                dsc_quantize_i = -((offset_i - error_i) >>> qlevel_i);
        end
    endfunction

    function automatic signed [31:0] dsc_find_residual_size_i(
        input logic signed [31:0] error_i);
        begin
            dsc_find_residual_size_i = 0;
            if (error_i == 0) dsc_find_residual_size_i = 0;
            else if ((error_i >= -1) && (error_i <= 0)) dsc_find_residual_size_i = 1;
            else if ((error_i >= -2) && (error_i <= 1)) dsc_find_residual_size_i = 2;
            else if ((error_i >= -4) && (error_i <= 3)) dsc_find_residual_size_i = 3;
            else if ((error_i >= -8) && (error_i <= 7)) dsc_find_residual_size_i = 4;
            else if ((error_i >= -16) && (error_i <= 15)) dsc_find_residual_size_i = 5;
            else if ((error_i >= -32) && (error_i <= 31)) dsc_find_residual_size_i = 6;
            else if ((error_i >= -64) && (error_i <= 63)) dsc_find_residual_size_i = 7;
            else if ((error_i >= -128) && (error_i <= 127)) dsc_find_residual_size_i = 8;
            else if ((error_i >= -256) && (error_i <= 255)) dsc_find_residual_size_i = 9;
            else if ((error_i >= -512) && (error_i <= 511)) dsc_find_residual_size_i = 10;
            else if ((error_i >= -1024) && (error_i <= 1023)) dsc_find_residual_size_i = 11;
            else if ((error_i >= -2048) && (error_i <= 2047)) dsc_find_residual_size_i = 12;
            else if ((error_i >= -4096) && (error_i <= 4095)) dsc_find_residual_size_i = 13;
            else if ((error_i >= -8192) && (error_i <= 8191)) dsc_find_residual_size_i = 14;
            else if ((error_i >= -16384) && (error_i <= 16383)) dsc_find_residual_size_i = 15;
            else if ((error_i >= -32768) && (error_i <= 32767)) dsc_find_residual_size_i = 16;
            else if ((error_i >= -65536) && (error_i <= 65535)) dsc_find_residual_size_i = 17;
            else if ((error_i >= -131702) && (error_i <= 131701)) dsc_find_residual_size_i = 18;
        end
    endfunction

    function automatic signed [31:0] dsc_max_residual_size_i(
        input logic signed [31:0] cpnt_i,
        input logic signed [31:0] version_i,
        input logic signed [31:0] native_i,
        input logic signed [31:0] depth0_i,
        input logic signed [31:0] depth1_i,
        input logic signed [31:0] selected_depth_i,
        input logic signed [31:0] qlevel_luma_i,
        input logic signed [31:0] qlevel_chroma_i);
        logic signed [31:0] qlevel_i;
        logic signed [31:0] chroma_i;
        begin
            qlevel_i = qlevel_luma_i;
            if ((cpnt_i % 32'sd3) == 0) qlevel_i = qlevel_luma_i;
            else if ((native_i != 0) && (cpnt_i == 32'sd1)) qlevel_i = qlevel_luma_i;
            else begin
                chroma_i = qlevel_chroma_i;
                if ((version_i == 32'sd2) &&
                    (depth0_i == ((cpnt_i == 32'sd1) ? selected_depth_i : depth1_i)) &&
                    (chroma_i > 0)) chroma_i = chroma_i - 32'sd1;
                qlevel_i = (chroma_i < 0) ? 0 : chroma_i;
            end
            dsc_max_residual_size_i = selected_depth_i - qlevel_i;
        end
    endfunction

    function automatic signed [31:0] dsc_find_midpoint_i(
        input logic signed [31:0] depth_i,
        input logic signed [31:0] left_i,
        input logic signed [31:0] qlevel_i);
        begin
            dsc_find_midpoint_i = (32'sd1 <<< (depth_i - 32'sd1))
                + (left_i % (32'sd1 <<< qlevel_i));
        end
    endfunction

    function automatic signed [31:0] dsc_current_at_i(
        input logic signed [31:0] index_i,
        input logic signed [31:0] curr_0_i,
        input logic signed [31:0] curr_1_i,
        input logic signed [31:0] curr_2_i,
        input logic signed [31:0] curr_3_i,
        input logic signed [31:0] curr_4_i,
        input logic signed [31:0] curr_5_i,
        input logic signed [31:0] curr_6_i,
        input logic signed [31:0] curr_7_i,
        input logic signed [31:0] curr_8_i,
        input logic signed [31:0] curr_9_i,
        input logic signed [31:0] curr_10_i,
        input logic signed [31:0] curr_11_i,
        input logic signed [31:0] curr_12_i,
        input logic signed [31:0] curr_13_i,
        input logic signed [31:0] curr_14_i,
        input logic signed [31:0] curr_15_i);
        begin
            case (index_i)
                0: dsc_current_at_i = curr_0_i;
                1: dsc_current_at_i = curr_1_i;
                2: dsc_current_at_i = curr_2_i;
                3: dsc_current_at_i = curr_3_i;
                4: dsc_current_at_i = curr_4_i;
                5: dsc_current_at_i = curr_5_i;
                6: dsc_current_at_i = curr_6_i;
                7: dsc_current_at_i = curr_7_i;
                8: dsc_current_at_i = curr_8_i;
                9: dsc_current_at_i = curr_9_i;
                10: dsc_current_at_i = curr_10_i;
                11: dsc_current_at_i = curr_11_i;
                12: dsc_current_at_i = curr_12_i;
                13: dsc_current_at_i = curr_13_i;
                14: dsc_current_at_i = curr_14_i;
                15: dsc_current_at_i = curr_15_i;
                default: dsc_current_at_i = 0;
            endcase
        end
    endfunction

    function automatic signed [31:0] dsc_sample_predict_i(
        input logic signed [31:0] hpos_i,
        input logic signed [31:0] pred_type_i,
        input logic signed [31:0] qlevel_i,
        input logic signed [31:0] depth_i,
        input logic signed [31:0] qr0_i,
        input logic signed [31:0] qr1_i,
        input logic signed [31:0] prev_0_i,
        input logic signed [31:0] prev_1_i,
        input logic signed [31:0] prev_2_i,
        input logic signed [31:0] prev_3_i,
        input logic signed [31:0] prev_4_i,
        input logic signed [31:0] prev_5_i,
        input logic signed [31:0] prev_6_i,
        input logic signed [31:0] prev_7_i,
        input logic signed [31:0] prev_8_i,
        input logic signed [31:0] prev_9_i,
        input logic signed [31:0] prev_10_i,
        input logic signed [31:0] prev_11_i,
        input logic signed [31:0] prev_12_i,
        input logic signed [31:0] prev_13_i,
        input logic signed [31:0] prev_14_i,
        input logic signed [31:0] curr_0_i,
        input logic signed [31:0] curr_1_i,
        input logic signed [31:0] curr_2_i,
        input logic signed [31:0] curr_3_i,
        input logic signed [31:0] curr_4_i,
        input logic signed [31:0] curr_5_i,
        input logic signed [31:0] curr_6_i,
        input logic signed [31:0] curr_7_i,
        input logic signed [31:0] curr_8_i,
        input logic signed [31:0] curr_9_i,
        input logic signed [31:0] curr_10_i,
        input logic signed [31:0] curr_11_i,
        input logic signed [31:0] curr_12_i,
        input logic signed [31:0] curr_13_i,
        input logic signed [31:0] curr_14_i,
        input logic signed [31:0] curr_15_i);
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
        logic signed [31:0] diff_i;
        logic signed [31:0] qdiv_i;
        logic signed [31:0] qhalf_i;
        logic signed [31:0] max_i;
        logic signed [31:0] window_start_i;
        logic signed [31:0] group_a_index_i;
        logic signed [31:0] block_global_index_i;
        logic signed [31:0] block_window_index_i;
        logic signed [31:0] block_i;
        logic signed [31:0] result_i;
        begin
            window_start_i = (hpos_i > 32'sd8) ? (hpos_i - 32'sd8) : 32'sd0;
            group_a_index_i = ((hpos_i / 32'sd3) * 32'sd3) + 32'sd4 - window_start_i;
            a_i = dsc_current_at_i(group_a_index_i, curr_0_i, curr_1_i, curr_2_i, curr_3_i, curr_4_i, curr_5_i, curr_6_i, curr_7_i, curr_8_i, curr_9_i, curr_10_i, curr_11_i, curr_12_i, curr_13_i, curr_14_i, curr_15_i);
            c_i = prev_1_i;
            b_i = prev_2_i;
            d_i = prev_3_i;
            e_i = prev_4_i;
            filt_c_i = (prev_0_i + (32'sd2 * prev_1_i) + prev_2_i + 32'sd2) >>> 2;
            filt_b_i = (prev_1_i + (32'sd2 * prev_2_i) + prev_3_i + 32'sd2) >>> 2;
            filt_d_i = (prev_2_i + (32'sd2 * prev_3_i) + prev_4_i + 32'sd2) >>> 2;
            filt_e_i = (prev_3_i + (32'sd2 * prev_4_i) + prev_5_i + 32'sd2) >>> 2;
            qdiv_i = 32'sd1 <<< qlevel_i;
            qhalf_i = qdiv_i / 32'sd2;
            max_i = (32'sd1 <<< depth_i) - 32'sd1;
            diff_i = dsc_clamp_i(filt_c_i - c_i, -qhalf_i, qhalf_i);
            blend_c_i = c_i + diff_i;
            diff_i = dsc_clamp_i(filt_b_i - b_i, -qhalf_i, qhalf_i);
            blend_b_i = b_i + diff_i;
            diff_i = dsc_clamp_i(filt_d_i - d_i, -qhalf_i, qhalf_i);
            blend_d_i = d_i + diff_i;
            diff_i = dsc_clamp_i(filt_e_i - e_i, -qhalf_i, qhalf_i);
            blend_e_i = e_i + diff_i;
            block_global_index_i = hpos_i + 32'sd5 - 32'sd1 - (pred_type_i - 32'sd2);
            if (block_global_index_i < 0) block_global_index_i = 0;
            block_window_index_i = block_global_index_i - window_start_i;
            block_i = dsc_current_at_i(block_window_index_i, curr_0_i, curr_1_i, curr_2_i, curr_3_i, curr_4_i, curr_5_i, curr_6_i, curr_7_i, curr_8_i, curr_9_i, curr_10_i, curr_11_i, curr_12_i, curr_13_i, curr_14_i, curr_15_i);
            result_i = 0;
            if ((hpos_i / 32'sd3) == 0) blend_c_i = a_i;
            if (pred_type_i == 32'sd0) begin
                if ((hpos_i % 32'sd3) == 0)
                    result_i = dsc_clamp_i(a_i + blend_b_i - blend_c_i,
                        dsc_min_i(a_i, blend_b_i), dsc_max_i(a_i, blend_b_i));
                else if ((hpos_i % 32'sd3) == 1)
                    result_i = dsc_clamp_i(a_i + blend_d_i - blend_c_i + (qr0_i * qdiv_i),
                        dsc_min_i(dsc_min_i(a_i, blend_b_i), blend_d_i),
                        dsc_max_i(dsc_max_i(a_i, blend_b_i), blend_d_i));
                else
                    result_i = dsc_clamp_i(a_i + blend_e_i - blend_c_i
                        + ((qr0_i + qr1_i) * qdiv_i),
                        dsc_min_i(dsc_min_i(a_i, blend_b_i), dsc_min_i(blend_d_i, blend_e_i)),
                        dsc_max_i(dsc_max_i(a_i, blend_b_i), dsc_max_i(blend_d_i, blend_e_i)));
            end else if (pred_type_i == 32'sd1) begin
                result_i = a_i;
                if ((hpos_i % 32'sd3) == 1)
                    result_i = dsc_clamp_i(a_i + (qr0_i * qdiv_i), 0, max_i);
                else if ((hpos_i % 32'sd3) == 2)
                    result_i = dsc_clamp_i(a_i + ((qr0_i + qr1_i) * qdiv_i), 0, max_i);
            end else result_i = block_i;
            dsc_sample_predict_i = result_i;
        end
    endfunction

    function automatic signed [31:0] dsc_lower_for_size_i(
        input logic signed [31:0] size_i);
        begin
            if (size_i <= 0) dsc_lower_for_size_i = 0;
            else if (size_i == 1) dsc_lower_for_size_i = -1;
            else dsc_lower_for_size_i = -(32'sd1 <<< (size_i - 1));
        end
    endfunction

    function automatic signed [31:0] dsc_upper_for_size_i(
        input logic signed [31:0] size_i);
        begin
            if (size_i <= 1) dsc_upper_for_size_i = 0;
            else dsc_upper_for_size_i = (32'sd1 <<< (size_i - 1)) - 32'sd1;
        end
    endfunction

    function automatic signed [31:0] dsc_project_midpoint_i(
        input logic signed [31:0] value_i,
        input logic signed [31:0] max_size_i);
        logic signed [31:0] lower_i;
        logic signed [31:0] upper_i;
        begin
            lower_i = dsc_lower_for_size_i(max_size_i);
            upper_i = dsc_upper_for_size_i(max_size_i);
            dsc_project_midpoint_i = dsc_clamp_i(value_i, lower_i, upper_i);
        end
    endfunction

    always_comb begin
        domain_valid = 1'b1;
        illegal_domain = 1'b0;
        bound_violation = 1'b0;
        midpoint_clamp_violation = 1'b0;
        arithmetic_domain_violation = 1'b0;
        state_primary_qp_out = state_primary_qp;
        state_quantized_residual_0_0_out = state_quantized_residual_0_0;
        state_quantized_residual_mid_0_0_out = state_quantized_residual_mid_0_0;
        state_quantized_residual_0_1_out = state_quantized_residual_0_1;
        state_quantized_residual_mid_0_1_out = state_quantized_residual_mid_0_1;
        state_quantized_residual_0_2_out = state_quantized_residual_0_2;
        state_quantized_residual_mid_0_2_out = state_quantized_residual_mid_0_2;
        state_midpoint_recon_0_0_out = state_midpoint_recon_0_0;
        state_midpoint_recon_0_1_out = state_midpoint_recon_0_1;
        state_midpoint_recon_0_2_out = state_midpoint_recon_0_2;
        state_midpoint_recon_0_3_out = state_midpoint_recon_0_3;
        state_midpoint_recon_0_4_out = state_midpoint_recon_0_4;
        state_midpoint_recon_0_5_out = state_midpoint_recon_0_5;
        state_max_error_0_out = state_max_error_0;
        state_max_mid_error_0_out = state_max_mid_error_0;
        curr_line_write_0_enable = 1'b0;
        curr_line_write_0_component = 32'sd0;
        curr_line_write_0_index = 32'sd0;
        curr_line_write_0_value = 32'sd0;
        cpnt_0_i = 32'sd0;
        depth_0_i = 32'sd0;
        qlevel_0_i = 32'sd0;
        pred_type_0_i = 32'sd0;
        pred_0_i = 32'sd0;
        actual_0_i = 32'sd0;
        err_raw_0_i = 32'sd0;
        err_q_0_i = 32'sd0;
        qmid_initial_0_i = 32'sd0;
        qmid_0_i = 32'sd0;
        max_size_0_i = 32'sd0;
        max_value_0_i = 32'sd0;
        recon_0_i = 32'sd0;
        midpoint_pred_0_i = 32'sd0;
        midpoint_recon_0_i = 32'sd0;
        abs_error_0_i = 32'sd0;
        abs_mid_error_0_i = 32'sd0;
        residual_index_0_i = 32'sd0;
        find_size_0_i = 32'sd0;
        state_quantized_residual_1_0_out = state_quantized_residual_1_0;
        state_quantized_residual_mid_1_0_out = state_quantized_residual_mid_1_0;
        state_quantized_residual_1_1_out = state_quantized_residual_1_1;
        state_quantized_residual_mid_1_1_out = state_quantized_residual_mid_1_1;
        state_quantized_residual_1_2_out = state_quantized_residual_1_2;
        state_quantized_residual_mid_1_2_out = state_quantized_residual_mid_1_2;
        state_midpoint_recon_1_0_out = state_midpoint_recon_1_0;
        state_midpoint_recon_1_1_out = state_midpoint_recon_1_1;
        state_midpoint_recon_1_2_out = state_midpoint_recon_1_2;
        state_midpoint_recon_1_3_out = state_midpoint_recon_1_3;
        state_midpoint_recon_1_4_out = state_midpoint_recon_1_4;
        state_midpoint_recon_1_5_out = state_midpoint_recon_1_5;
        state_max_error_1_out = state_max_error_1;
        state_max_mid_error_1_out = state_max_mid_error_1;
        curr_line_write_1_enable = 1'b0;
        curr_line_write_1_component = 32'sd0;
        curr_line_write_1_index = 32'sd0;
        curr_line_write_1_value = 32'sd0;
        cpnt_1_i = 32'sd0;
        depth_1_i = 32'sd0;
        qlevel_1_i = 32'sd0;
        pred_type_1_i = 32'sd0;
        pred_1_i = 32'sd0;
        actual_1_i = 32'sd0;
        err_raw_1_i = 32'sd0;
        err_q_1_i = 32'sd0;
        qmid_initial_1_i = 32'sd0;
        qmid_1_i = 32'sd0;
        max_size_1_i = 32'sd0;
        max_value_1_i = 32'sd0;
        recon_1_i = 32'sd0;
        midpoint_pred_1_i = 32'sd0;
        midpoint_recon_1_i = 32'sd0;
        abs_error_1_i = 32'sd0;
        abs_mid_error_1_i = 32'sd0;
        residual_index_1_i = 32'sd0;
        find_size_1_i = 32'sd0;
        state_quantized_residual_2_0_out = state_quantized_residual_2_0;
        state_quantized_residual_mid_2_0_out = state_quantized_residual_mid_2_0;
        state_quantized_residual_2_1_out = state_quantized_residual_2_1;
        state_quantized_residual_mid_2_1_out = state_quantized_residual_mid_2_1;
        state_quantized_residual_2_2_out = state_quantized_residual_2_2;
        state_quantized_residual_mid_2_2_out = state_quantized_residual_mid_2_2;
        state_midpoint_recon_2_0_out = state_midpoint_recon_2_0;
        state_midpoint_recon_2_1_out = state_midpoint_recon_2_1;
        state_midpoint_recon_2_2_out = state_midpoint_recon_2_2;
        state_midpoint_recon_2_3_out = state_midpoint_recon_2_3;
        state_midpoint_recon_2_4_out = state_midpoint_recon_2_4;
        state_midpoint_recon_2_5_out = state_midpoint_recon_2_5;
        state_max_error_2_out = state_max_error_2;
        state_max_mid_error_2_out = state_max_mid_error_2;
        curr_line_write_2_enable = 1'b0;
        curr_line_write_2_component = 32'sd0;
        curr_line_write_2_index = 32'sd0;
        curr_line_write_2_value = 32'sd0;
        cpnt_2_i = 32'sd0;
        depth_2_i = 32'sd0;
        qlevel_2_i = 32'sd0;
        pred_type_2_i = 32'sd0;
        pred_2_i = 32'sd0;
        actual_2_i = 32'sd0;
        err_raw_2_i = 32'sd0;
        err_q_2_i = 32'sd0;
        qmid_initial_2_i = 32'sd0;
        qmid_2_i = 32'sd0;
        max_size_2_i = 32'sd0;
        max_value_2_i = 32'sd0;
        recon_2_i = 32'sd0;
        midpoint_pred_2_i = 32'sd0;
        midpoint_recon_2_i = 32'sd0;
        abs_error_2_i = 32'sd0;
        abs_mid_error_2_i = 32'sd0;
        residual_index_2_i = 32'sd0;
        find_size_2_i = 32'sd0;
        state_quantized_residual_3_0_out = state_quantized_residual_3_0;
        state_quantized_residual_mid_3_0_out = state_quantized_residual_mid_3_0;
        state_quantized_residual_3_1_out = state_quantized_residual_3_1;
        state_quantized_residual_mid_3_1_out = state_quantized_residual_mid_3_1;
        state_quantized_residual_3_2_out = state_quantized_residual_3_2;
        state_quantized_residual_mid_3_2_out = state_quantized_residual_mid_3_2;
        state_midpoint_recon_3_0_out = state_midpoint_recon_3_0;
        state_midpoint_recon_3_1_out = state_midpoint_recon_3_1;
        state_midpoint_recon_3_2_out = state_midpoint_recon_3_2;
        state_midpoint_recon_3_3_out = state_midpoint_recon_3_3;
        state_midpoint_recon_3_4_out = state_midpoint_recon_3_4;
        state_midpoint_recon_3_5_out = state_midpoint_recon_3_5;
        state_max_error_3_out = state_max_error_3;
        state_max_mid_error_3_out = state_max_mid_error_3;
        curr_line_write_3_enable = 1'b0;
        curr_line_write_3_component = 32'sd0;
        curr_line_write_3_index = 32'sd0;
        curr_line_write_3_value = 32'sd0;
        cpnt_3_i = 32'sd0;
        depth_3_i = 32'sd0;
        qlevel_3_i = 32'sd0;
        pred_type_3_i = 32'sd0;
        pred_3_i = 32'sd0;
        actual_3_i = 32'sd0;
        err_raw_3_i = 32'sd0;
        err_q_3_i = 32'sd0;
        qmid_initial_3_i = 32'sd0;
        qmid_3_i = 32'sd0;
        max_size_3_i = 32'sd0;
        max_value_3_i = 32'sd0;
        recon_3_i = 32'sd0;
        midpoint_pred_3_i = 32'sd0;
        midpoint_recon_3_i = 32'sd0;
        abs_error_3_i = 32'sd0;
        abs_mid_error_3_i = 32'sd0;
        residual_index_3_i = 32'sd0;
        find_size_3_i = 32'sd0;

        if ((state_is_encoder != 32'sd1) ||
            (state_units_per_group < 0) || (state_units_per_group > 32'sd4) ||
            (hpos < 0) || (vpos < 0) ||
            (sampmodcnt < 0) || (sampmodcnt >= 32'sd3) ||
            (qp < 0) || (qp > 32'sd31) ||
            ((cfg_native_420 != 0) && (cfg_native_420 != 1)) ||
            ((cfg_dsc_version_minor != 32'sd1) && (cfg_dsc_version_minor != 32'sd2)) ||
            (cfg_bits_per_component < 32'sd8) || (cfg_bits_per_component > 32'sd16) ||
            ((cfg_full_ich_err_precision != 0) && (cfg_full_ich_err_precision != 1)) ||
            (state_qlevel_luma_qp < 0) || (state_qlevel_luma_qp > 32'sd16) ||
            (state_qlevel_chroma_qp < 0) || (state_qlevel_chroma_qp > 32'sd16) ||
            (state_prev_line_prediction < 0) || (state_prev_line_prediction > 32'sd14)) begin
            domain_valid = 1'b0;
            illegal_domain = 1'b1;
        end
        cpnt_0_i = state_unit_c_type_0;
        depth_0_i = ((cpnt_0_i == 32'sd0) ? state_cpnt_bit_depth_0 : ((cpnt_0_i == 32'sd1) ? state_cpnt_bit_depth_1 : ((cpnt_0_i == 32'sd2) ? state_cpnt_bit_depth_2 : state_cpnt_bit_depth_3)));
        qlevel_0_i = dsc_map_qlevel_i(cpnt_0_i, cfg_native_420, cfg_dsc_version_minor, state_cpnt_bit_depth_0, state_cpnt_bit_depth_1, state_qlevel_luma_qp, state_qlevel_chroma_qp);
        residual_index_0_i = sampmodcnt - state_unit_start_hpos_0;
        pred_type_0_i = (vpos == 0) ? 32'sd1 : state_prev_line_prediction;
        if ((cfg_native_420 != 0) && (cpnt_0_i == 32'sd2))
            pred_type_0_i = (vpos <= 32'sd1) ? 32'sd1 : 32'sd0;
        pred_0_i = dsc_sample_predict_i(hpos, pred_type_0_i, qlevel_0_i, depth_0_i, state_quantized_residual_0_0, state_quantized_residual_0_1, prev_line_unit_0_tap_0, prev_line_unit_0_tap_1, prev_line_unit_0_tap_2, prev_line_unit_0_tap_3, prev_line_unit_0_tap_4, prev_line_unit_0_tap_5, prev_line_unit_0_tap_6, prev_line_unit_0_tap_7, prev_line_unit_0_tap_8, prev_line_unit_0_tap_9, prev_line_unit_0_tap_10, prev_line_unit_0_tap_11, prev_line_unit_0_tap_12, prev_line_unit_0_tap_13, prev_line_unit_0_tap_14, curr_line_unit_0_tap_0, curr_line_unit_0_tap_1, curr_line_unit_0_tap_2, curr_line_unit_0_tap_3, curr_line_unit_0_tap_4, curr_line_unit_0_tap_5, curr_line_unit_0_tap_6, curr_line_unit_0_tap_7, curr_line_unit_0_tap_8, curr_line_unit_0_tap_9, curr_line_unit_0_tap_10, curr_line_unit_0_tap_11, curr_line_unit_0_tap_12, curr_line_unit_0_tap_13, curr_line_unit_0_tap_14, curr_line_unit_0_tap_15);
        actual_0_i = orig_sample_0;
        err_raw_0_i = actual_0_i - pred_0_i;
        qlevel_0_i = dsc_map_qlevel_i(cpnt_0_i, cfg_native_420, cfg_dsc_version_minor, state_cpnt_bit_depth_0, state_cpnt_bit_depth_1, state_qlevel_luma_qp, state_qlevel_chroma_qp);
        err_q_0_i = dsc_quantize_i(err_raw_0_i, qlevel_0_i);
        midpoint_pred_0_i = dsc_find_midpoint_i(depth_0_i, ((cpnt_0_i == 32'sd0) ? state_left_recon_0 : ((cpnt_0_i == 32'sd1) ? state_left_recon_1 : ((cpnt_0_i == 32'sd2) ? state_left_recon_2 : state_left_recon_3))), qlevel_0_i);
        err_raw_0_i = actual_0_i - midpoint_pred_0_i;
        qmid_initial_0_i = dsc_quantize_i(err_raw_0_i, qlevel_0_i);
        max_size_0_i = dsc_max_residual_size_i(cpnt_0_i, cfg_dsc_version_minor, cfg_native_420, state_cpnt_bit_depth_0, state_cpnt_bit_depth_1, depth_0_i, state_qlevel_luma_qp, state_qlevel_chroma_qp);
        find_size_0_i = dsc_find_residual_size_i(qmid_initial_0_i);
        qmid_0_i = dsc_project_midpoint_i(qmid_initial_0_i, max_size_0_i);
        if (state_units_per_group > 32'sd0) begin
            if ((cpnt_0_i < 0) || (cpnt_0_i > 32'sd3) || (depth_0_i < 32'sd8) || (depth_0_i > 32'sd16) || (qlevel_0_i < 0) || (qlevel_0_i > depth_0_i) || (state_unit_start_hpos_0 < 0) || (state_unit_start_hpos_0 >= 32'sd3) || (residual_index_0_i < 0) || (residual_index_0_i >= 32'sd3)) begin
                domain_valid = 1'b0;
                illegal_domain = 1'b1;
            end
            if ((orig_sample_0 < 0) || (orig_sample_0 > 32'sd65535) || (state_left_recon_0 < 0) || (state_left_recon_0 > 32'sd65535)) begin
                domain_valid = 1'b0;
                arithmetic_domain_violation = 1'b1;
            end
            if (dsc_find_residual_size_i(qmid_0_i) > max_size_0_i)
                midpoint_clamp_violation = 1'b1;
            if (sampmodcnt == 0) state_primary_qp_out = qp;
            if ((residual_index_0_i >= 0) && (residual_index_0_i < 32'sd3)) begin
                if (residual_index_0_i == 32'sd0) begin
                    state_quantized_residual_0_0_out = err_q_0_i;
                    state_quantized_residual_mid_0_0_out = qmid_0_i;
                end
                if (residual_index_0_i == 32'sd1) begin
                    state_quantized_residual_0_1_out = err_q_0_i;
                    state_quantized_residual_mid_0_1_out = qmid_0_i;
                end
                if (residual_index_0_i == 32'sd2) begin
                    state_quantized_residual_0_2_out = err_q_0_i;
                    state_quantized_residual_mid_0_2_out = qmid_0_i;
                end
            end
            max_value_0_i = (32'sd1 <<< depth_0_i) - 32'sd1;
            recon_0_i = dsc_clamp_i(pred_0_i + (err_q_0_i <<< qlevel_0_i), 0, max_value_0_i);
            abs_error_0_i = dsc_abs_i(actual_0_i - recon_0_i);
            if (cfg_full_ich_err_precision == 0)
                abs_error_0_i = abs_error_0_i >>> (cfg_bits_per_component - 32'sd8);
            state_max_error_0_out = dsc_max_i(state_max_error_0, abs_error_0_i);
            midpoint_pred_0_i = dsc_find_midpoint_i(depth_0_i, ((cpnt_0_i == 32'sd0) ? state_left_recon_0 : ((cpnt_0_i == 32'sd1) ? state_left_recon_1 : ((cpnt_0_i == 32'sd2) ? state_left_recon_2 : state_left_recon_3))), qlevel_0_i);
            midpoint_recon_0_i = midpoint_pred_0_i + (qmid_0_i <<< qlevel_0_i);
            midpoint_recon_0_i = dsc_clamp_i(midpoint_recon_0_i, 0, max_value_0_i);
            if (residual_index_0_i == 32'sd0)
                state_midpoint_recon_0_0_out = midpoint_recon_0_i;
            if (residual_index_0_i == 32'sd1)
                state_midpoint_recon_0_1_out = midpoint_recon_0_i;
            if (residual_index_0_i == 32'sd2)
                state_midpoint_recon_0_2_out = midpoint_recon_0_i;
            abs_mid_error_0_i = dsc_abs_i(actual_0_i - midpoint_recon_0_i);
            if (cfg_full_ich_err_precision == 0)
                abs_mid_error_0_i = abs_mid_error_0_i >>> (cfg_bits_per_component - 32'sd8);
            state_max_mid_error_0_out = dsc_max_i(state_max_mid_error_0, abs_mid_error_0_i);
            curr_line_write_0_enable = 1'b1;
            curr_line_write_0_component = cpnt_0_i;
            curr_line_write_0_index = hpos + 32'sd5;
            curr_line_write_0_value = recon_0_i;
        end
        cpnt_1_i = state_unit_c_type_1;
        depth_1_i = ((cpnt_1_i == 32'sd0) ? state_cpnt_bit_depth_0 : ((cpnt_1_i == 32'sd1) ? state_cpnt_bit_depth_1 : ((cpnt_1_i == 32'sd2) ? state_cpnt_bit_depth_2 : state_cpnt_bit_depth_3)));
        qlevel_1_i = dsc_map_qlevel_i(cpnt_1_i, cfg_native_420, cfg_dsc_version_minor, state_cpnt_bit_depth_0, state_cpnt_bit_depth_1, state_qlevel_luma_qp, state_qlevel_chroma_qp);
        residual_index_1_i = sampmodcnt - state_unit_start_hpos_1;
        pred_type_1_i = (vpos == 0) ? 32'sd1 : state_prev_line_prediction;
        if ((cfg_native_420 != 0) && (cpnt_1_i == 32'sd2))
            pred_type_1_i = (vpos <= 32'sd1) ? 32'sd1 : 32'sd0;
        pred_1_i = dsc_sample_predict_i(hpos, pred_type_1_i, qlevel_1_i, depth_1_i, state_quantized_residual_1_0, state_quantized_residual_1_1, prev_line_unit_1_tap_0, prev_line_unit_1_tap_1, prev_line_unit_1_tap_2, prev_line_unit_1_tap_3, prev_line_unit_1_tap_4, prev_line_unit_1_tap_5, prev_line_unit_1_tap_6, prev_line_unit_1_tap_7, prev_line_unit_1_tap_8, prev_line_unit_1_tap_9, prev_line_unit_1_tap_10, prev_line_unit_1_tap_11, prev_line_unit_1_tap_12, prev_line_unit_1_tap_13, prev_line_unit_1_tap_14, curr_line_unit_1_tap_0, curr_line_unit_1_tap_1, curr_line_unit_1_tap_2, curr_line_unit_1_tap_3, curr_line_unit_1_tap_4, curr_line_unit_1_tap_5, curr_line_unit_1_tap_6, curr_line_unit_1_tap_7, curr_line_unit_1_tap_8, curr_line_unit_1_tap_9, curr_line_unit_1_tap_10, curr_line_unit_1_tap_11, curr_line_unit_1_tap_12, curr_line_unit_1_tap_13, curr_line_unit_1_tap_14, curr_line_unit_1_tap_15);
        actual_1_i = orig_sample_1;
        err_raw_1_i = actual_1_i - pred_1_i;
        qlevel_1_i = dsc_map_qlevel_i(cpnt_1_i, cfg_native_420, cfg_dsc_version_minor, state_cpnt_bit_depth_0, state_cpnt_bit_depth_1, state_qlevel_luma_qp, state_qlevel_chroma_qp);
        err_q_1_i = dsc_quantize_i(err_raw_1_i, qlevel_1_i);
        midpoint_pred_1_i = dsc_find_midpoint_i(depth_1_i, ((cpnt_1_i == 32'sd0) ? state_left_recon_0 : ((cpnt_1_i == 32'sd1) ? state_left_recon_1 : ((cpnt_1_i == 32'sd2) ? state_left_recon_2 : state_left_recon_3))), qlevel_1_i);
        err_raw_1_i = actual_1_i - midpoint_pred_1_i;
        qmid_initial_1_i = dsc_quantize_i(err_raw_1_i, qlevel_1_i);
        max_size_1_i = dsc_max_residual_size_i(cpnt_1_i, cfg_dsc_version_minor, cfg_native_420, state_cpnt_bit_depth_0, state_cpnt_bit_depth_1, depth_1_i, state_qlevel_luma_qp, state_qlevel_chroma_qp);
        find_size_1_i = dsc_find_residual_size_i(qmid_initial_1_i);
        qmid_1_i = dsc_project_midpoint_i(qmid_initial_1_i, max_size_1_i);
        if (state_units_per_group > 32'sd1) begin
            if ((cpnt_1_i < 0) || (cpnt_1_i > 32'sd3) || (depth_1_i < 32'sd8) || (depth_1_i > 32'sd16) || (qlevel_1_i < 0) || (qlevel_1_i > depth_1_i) || (state_unit_start_hpos_1 < 0) || (state_unit_start_hpos_1 >= 32'sd3) || (residual_index_1_i < 0) || (residual_index_1_i >= 32'sd3)) begin
                domain_valid = 1'b0;
                illegal_domain = 1'b1;
            end
            if ((orig_sample_1 < 0) || (orig_sample_1 > 32'sd65535) || (state_left_recon_1 < 0) || (state_left_recon_1 > 32'sd65535)) begin
                domain_valid = 1'b0;
                arithmetic_domain_violation = 1'b1;
            end
            if (dsc_find_residual_size_i(qmid_1_i) > max_size_1_i)
                midpoint_clamp_violation = 1'b1;
            if (sampmodcnt == 0) state_primary_qp_out = qp;
            if ((residual_index_1_i >= 0) && (residual_index_1_i < 32'sd3)) begin
                if (residual_index_1_i == 32'sd0) begin
                    state_quantized_residual_1_0_out = err_q_1_i;
                    state_quantized_residual_mid_1_0_out = qmid_1_i;
                end
                if (residual_index_1_i == 32'sd1) begin
                    state_quantized_residual_1_1_out = err_q_1_i;
                    state_quantized_residual_mid_1_1_out = qmid_1_i;
                end
                if (residual_index_1_i == 32'sd2) begin
                    state_quantized_residual_1_2_out = err_q_1_i;
                    state_quantized_residual_mid_1_2_out = qmid_1_i;
                end
            end
            max_value_1_i = (32'sd1 <<< depth_1_i) - 32'sd1;
            recon_1_i = dsc_clamp_i(pred_1_i + (err_q_1_i <<< qlevel_1_i), 0, max_value_1_i);
            abs_error_1_i = dsc_abs_i(actual_1_i - recon_1_i);
            if (cfg_full_ich_err_precision == 0)
                abs_error_1_i = abs_error_1_i >>> (cfg_bits_per_component - 32'sd8);
            state_max_error_1_out = dsc_max_i(state_max_error_1, abs_error_1_i);
            midpoint_pred_1_i = dsc_find_midpoint_i(depth_1_i, ((cpnt_1_i == 32'sd0) ? state_left_recon_0 : ((cpnt_1_i == 32'sd1) ? state_left_recon_1 : ((cpnt_1_i == 32'sd2) ? state_left_recon_2 : state_left_recon_3))), qlevel_1_i);
            midpoint_recon_1_i = midpoint_pred_1_i + (qmid_1_i <<< qlevel_1_i);
            midpoint_recon_1_i = dsc_clamp_i(midpoint_recon_1_i, 0, max_value_1_i);
            if (residual_index_1_i == 32'sd0)
                state_midpoint_recon_1_0_out = midpoint_recon_1_i;
            if (residual_index_1_i == 32'sd1)
                state_midpoint_recon_1_1_out = midpoint_recon_1_i;
            if (residual_index_1_i == 32'sd2)
                state_midpoint_recon_1_2_out = midpoint_recon_1_i;
            abs_mid_error_1_i = dsc_abs_i(actual_1_i - midpoint_recon_1_i);
            if (cfg_full_ich_err_precision == 0)
                abs_mid_error_1_i = abs_mid_error_1_i >>> (cfg_bits_per_component - 32'sd8);
            state_max_mid_error_1_out = dsc_max_i(state_max_mid_error_1, abs_mid_error_1_i);
            curr_line_write_1_enable = 1'b1;
            curr_line_write_1_component = cpnt_1_i;
            curr_line_write_1_index = hpos + 32'sd5;
            curr_line_write_1_value = recon_1_i;
        end
        cpnt_2_i = state_unit_c_type_2;
        depth_2_i = ((cpnt_2_i == 32'sd0) ? state_cpnt_bit_depth_0 : ((cpnt_2_i == 32'sd1) ? state_cpnt_bit_depth_1 : ((cpnt_2_i == 32'sd2) ? state_cpnt_bit_depth_2 : state_cpnt_bit_depth_3)));
        qlevel_2_i = dsc_map_qlevel_i(cpnt_2_i, cfg_native_420, cfg_dsc_version_minor, state_cpnt_bit_depth_0, state_cpnt_bit_depth_1, state_qlevel_luma_qp, state_qlevel_chroma_qp);
        residual_index_2_i = sampmodcnt - state_unit_start_hpos_2;
        pred_type_2_i = (vpos == 0) ? 32'sd1 : state_prev_line_prediction;
        if ((cfg_native_420 != 0) && (cpnt_2_i == 32'sd2))
            pred_type_2_i = (vpos <= 32'sd1) ? 32'sd1 : 32'sd0;
        pred_2_i = dsc_sample_predict_i(hpos, pred_type_2_i, qlevel_2_i, depth_2_i, state_quantized_residual_2_0, state_quantized_residual_2_1, prev_line_unit_2_tap_0, prev_line_unit_2_tap_1, prev_line_unit_2_tap_2, prev_line_unit_2_tap_3, prev_line_unit_2_tap_4, prev_line_unit_2_tap_5, prev_line_unit_2_tap_6, prev_line_unit_2_tap_7, prev_line_unit_2_tap_8, prev_line_unit_2_tap_9, prev_line_unit_2_tap_10, prev_line_unit_2_tap_11, prev_line_unit_2_tap_12, prev_line_unit_2_tap_13, prev_line_unit_2_tap_14, curr_line_unit_2_tap_0, curr_line_unit_2_tap_1, curr_line_unit_2_tap_2, curr_line_unit_2_tap_3, curr_line_unit_2_tap_4, curr_line_unit_2_tap_5, curr_line_unit_2_tap_6, curr_line_unit_2_tap_7, curr_line_unit_2_tap_8, curr_line_unit_2_tap_9, curr_line_unit_2_tap_10, curr_line_unit_2_tap_11, curr_line_unit_2_tap_12, curr_line_unit_2_tap_13, curr_line_unit_2_tap_14, curr_line_unit_2_tap_15);
        actual_2_i = orig_sample_2;
        err_raw_2_i = actual_2_i - pred_2_i;
        qlevel_2_i = dsc_map_qlevel_i(cpnt_2_i, cfg_native_420, cfg_dsc_version_minor, state_cpnt_bit_depth_0, state_cpnt_bit_depth_1, state_qlevel_luma_qp, state_qlevel_chroma_qp);
        err_q_2_i = dsc_quantize_i(err_raw_2_i, qlevel_2_i);
        midpoint_pred_2_i = dsc_find_midpoint_i(depth_2_i, ((cpnt_2_i == 32'sd0) ? state_left_recon_0 : ((cpnt_2_i == 32'sd1) ? state_left_recon_1 : ((cpnt_2_i == 32'sd2) ? state_left_recon_2 : state_left_recon_3))), qlevel_2_i);
        err_raw_2_i = actual_2_i - midpoint_pred_2_i;
        qmid_initial_2_i = dsc_quantize_i(err_raw_2_i, qlevel_2_i);
        max_size_2_i = dsc_max_residual_size_i(cpnt_2_i, cfg_dsc_version_minor, cfg_native_420, state_cpnt_bit_depth_0, state_cpnt_bit_depth_1, depth_2_i, state_qlevel_luma_qp, state_qlevel_chroma_qp);
        find_size_2_i = dsc_find_residual_size_i(qmid_initial_2_i);
        qmid_2_i = dsc_project_midpoint_i(qmid_initial_2_i, max_size_2_i);
        if (state_units_per_group > 32'sd2) begin
            if ((cpnt_2_i < 0) || (cpnt_2_i > 32'sd3) || (depth_2_i < 32'sd8) || (depth_2_i > 32'sd16) || (qlevel_2_i < 0) || (qlevel_2_i > depth_2_i) || (state_unit_start_hpos_2 < 0) || (state_unit_start_hpos_2 >= 32'sd3) || (residual_index_2_i < 0) || (residual_index_2_i >= 32'sd3)) begin
                domain_valid = 1'b0;
                illegal_domain = 1'b1;
            end
            if ((orig_sample_2 < 0) || (orig_sample_2 > 32'sd65535) || (state_left_recon_2 < 0) || (state_left_recon_2 > 32'sd65535)) begin
                domain_valid = 1'b0;
                arithmetic_domain_violation = 1'b1;
            end
            if (dsc_find_residual_size_i(qmid_2_i) > max_size_2_i)
                midpoint_clamp_violation = 1'b1;
            if (sampmodcnt == 0) state_primary_qp_out = qp;
            if ((residual_index_2_i >= 0) && (residual_index_2_i < 32'sd3)) begin
                if (residual_index_2_i == 32'sd0) begin
                    state_quantized_residual_2_0_out = err_q_2_i;
                    state_quantized_residual_mid_2_0_out = qmid_2_i;
                end
                if (residual_index_2_i == 32'sd1) begin
                    state_quantized_residual_2_1_out = err_q_2_i;
                    state_quantized_residual_mid_2_1_out = qmid_2_i;
                end
                if (residual_index_2_i == 32'sd2) begin
                    state_quantized_residual_2_2_out = err_q_2_i;
                    state_quantized_residual_mid_2_2_out = qmid_2_i;
                end
            end
            max_value_2_i = (32'sd1 <<< depth_2_i) - 32'sd1;
            recon_2_i = dsc_clamp_i(pred_2_i + (err_q_2_i <<< qlevel_2_i), 0, max_value_2_i);
            abs_error_2_i = dsc_abs_i(actual_2_i - recon_2_i);
            if (cfg_full_ich_err_precision == 0)
                abs_error_2_i = abs_error_2_i >>> (cfg_bits_per_component - 32'sd8);
            state_max_error_2_out = dsc_max_i(state_max_error_2, abs_error_2_i);
            midpoint_pred_2_i = dsc_find_midpoint_i(depth_2_i, ((cpnt_2_i == 32'sd0) ? state_left_recon_0 : ((cpnt_2_i == 32'sd1) ? state_left_recon_1 : ((cpnt_2_i == 32'sd2) ? state_left_recon_2 : state_left_recon_3))), qlevel_2_i);
            midpoint_recon_2_i = midpoint_pred_2_i + (qmid_2_i <<< qlevel_2_i);
            midpoint_recon_2_i = dsc_clamp_i(midpoint_recon_2_i, 0, max_value_2_i);
            if (residual_index_2_i == 32'sd0)
                state_midpoint_recon_2_0_out = midpoint_recon_2_i;
            if (residual_index_2_i == 32'sd1)
                state_midpoint_recon_2_1_out = midpoint_recon_2_i;
            if (residual_index_2_i == 32'sd2)
                state_midpoint_recon_2_2_out = midpoint_recon_2_i;
            abs_mid_error_2_i = dsc_abs_i(actual_2_i - midpoint_recon_2_i);
            if (cfg_full_ich_err_precision == 0)
                abs_mid_error_2_i = abs_mid_error_2_i >>> (cfg_bits_per_component - 32'sd8);
            state_max_mid_error_2_out = dsc_max_i(state_max_mid_error_2, abs_mid_error_2_i);
            curr_line_write_2_enable = 1'b1;
            curr_line_write_2_component = cpnt_2_i;
            curr_line_write_2_index = hpos + 32'sd5;
            curr_line_write_2_value = recon_2_i;
        end
        cpnt_3_i = state_unit_c_type_3;
        depth_3_i = ((cpnt_3_i == 32'sd0) ? state_cpnt_bit_depth_0 : ((cpnt_3_i == 32'sd1) ? state_cpnt_bit_depth_1 : ((cpnt_3_i == 32'sd2) ? state_cpnt_bit_depth_2 : state_cpnt_bit_depth_3)));
        qlevel_3_i = dsc_map_qlevel_i(cpnt_3_i, cfg_native_420, cfg_dsc_version_minor, state_cpnt_bit_depth_0, state_cpnt_bit_depth_1, state_qlevel_luma_qp, state_qlevel_chroma_qp);
        residual_index_3_i = sampmodcnt - state_unit_start_hpos_3;
        pred_type_3_i = (vpos == 0) ? 32'sd1 : state_prev_line_prediction;
        if ((cfg_native_420 != 0) && (cpnt_3_i == 32'sd2))
            pred_type_3_i = (vpos <= 32'sd1) ? 32'sd1 : 32'sd0;
        pred_3_i = dsc_sample_predict_i(hpos, pred_type_3_i, qlevel_3_i, depth_3_i, state_quantized_residual_3_0, state_quantized_residual_3_1, prev_line_unit_3_tap_0, prev_line_unit_3_tap_1, prev_line_unit_3_tap_2, prev_line_unit_3_tap_3, prev_line_unit_3_tap_4, prev_line_unit_3_tap_5, prev_line_unit_3_tap_6, prev_line_unit_3_tap_7, prev_line_unit_3_tap_8, prev_line_unit_3_tap_9, prev_line_unit_3_tap_10, prev_line_unit_3_tap_11, prev_line_unit_3_tap_12, prev_line_unit_3_tap_13, prev_line_unit_3_tap_14, curr_line_unit_3_tap_0, curr_line_unit_3_tap_1, curr_line_unit_3_tap_2, curr_line_unit_3_tap_3, curr_line_unit_3_tap_4, curr_line_unit_3_tap_5, curr_line_unit_3_tap_6, curr_line_unit_3_tap_7, curr_line_unit_3_tap_8, curr_line_unit_3_tap_9, curr_line_unit_3_tap_10, curr_line_unit_3_tap_11, curr_line_unit_3_tap_12, curr_line_unit_3_tap_13, curr_line_unit_3_tap_14, curr_line_unit_3_tap_15);
        actual_3_i = orig_sample_3;
        err_raw_3_i = actual_3_i - pred_3_i;
        qlevel_3_i = dsc_map_qlevel_i(cpnt_3_i, cfg_native_420, cfg_dsc_version_minor, state_cpnt_bit_depth_0, state_cpnt_bit_depth_1, state_qlevel_luma_qp, state_qlevel_chroma_qp);
        err_q_3_i = dsc_quantize_i(err_raw_3_i, qlevel_3_i);
        midpoint_pred_3_i = dsc_find_midpoint_i(depth_3_i, ((cpnt_3_i == 32'sd0) ? state_left_recon_0 : ((cpnt_3_i == 32'sd1) ? state_left_recon_1 : ((cpnt_3_i == 32'sd2) ? state_left_recon_2 : state_left_recon_3))), qlevel_3_i);
        err_raw_3_i = actual_3_i - midpoint_pred_3_i;
        qmid_initial_3_i = dsc_quantize_i(err_raw_3_i, qlevel_3_i);
        max_size_3_i = dsc_max_residual_size_i(cpnt_3_i, cfg_dsc_version_minor, cfg_native_420, state_cpnt_bit_depth_0, state_cpnt_bit_depth_1, depth_3_i, state_qlevel_luma_qp, state_qlevel_chroma_qp);
        find_size_3_i = dsc_find_residual_size_i(qmid_initial_3_i);
        qmid_3_i = dsc_project_midpoint_i(qmid_initial_3_i, max_size_3_i);
        if (state_units_per_group > 32'sd3) begin
            if ((cpnt_3_i < 0) || (cpnt_3_i > 32'sd3) || (depth_3_i < 32'sd8) || (depth_3_i > 32'sd16) || (qlevel_3_i < 0) || (qlevel_3_i > depth_3_i) || (state_unit_start_hpos_3 < 0) || (state_unit_start_hpos_3 >= 32'sd3) || (residual_index_3_i < 0) || (residual_index_3_i >= 32'sd3)) begin
                domain_valid = 1'b0;
                illegal_domain = 1'b1;
            end
            if ((orig_sample_3 < 0) || (orig_sample_3 > 32'sd65535) || (state_left_recon_3 < 0) || (state_left_recon_3 > 32'sd65535)) begin
                domain_valid = 1'b0;
                arithmetic_domain_violation = 1'b1;
            end
            if (dsc_find_residual_size_i(qmid_3_i) > max_size_3_i)
                midpoint_clamp_violation = 1'b1;
            if (sampmodcnt == 0) state_primary_qp_out = qp;
            if ((residual_index_3_i >= 0) && (residual_index_3_i < 32'sd3)) begin
                if (residual_index_3_i == 32'sd0) begin
                    state_quantized_residual_3_0_out = err_q_3_i;
                    state_quantized_residual_mid_3_0_out = qmid_3_i;
                end
                if (residual_index_3_i == 32'sd1) begin
                    state_quantized_residual_3_1_out = err_q_3_i;
                    state_quantized_residual_mid_3_1_out = qmid_3_i;
                end
                if (residual_index_3_i == 32'sd2) begin
                    state_quantized_residual_3_2_out = err_q_3_i;
                    state_quantized_residual_mid_3_2_out = qmid_3_i;
                end
            end
            max_value_3_i = (32'sd1 <<< depth_3_i) - 32'sd1;
            recon_3_i = dsc_clamp_i(pred_3_i + (err_q_3_i <<< qlevel_3_i), 0, max_value_3_i);
            abs_error_3_i = dsc_abs_i(actual_3_i - recon_3_i);
            if (cfg_full_ich_err_precision == 0)
                abs_error_3_i = abs_error_3_i >>> (cfg_bits_per_component - 32'sd8);
            state_max_error_3_out = dsc_max_i(state_max_error_3, abs_error_3_i);
            midpoint_pred_3_i = dsc_find_midpoint_i(depth_3_i, ((cpnt_3_i == 32'sd0) ? state_left_recon_0 : ((cpnt_3_i == 32'sd1) ? state_left_recon_1 : ((cpnt_3_i == 32'sd2) ? state_left_recon_2 : state_left_recon_3))), qlevel_3_i);
            midpoint_recon_3_i = midpoint_pred_3_i + (qmid_3_i <<< qlevel_3_i);
            midpoint_recon_3_i = dsc_clamp_i(midpoint_recon_3_i, 0, max_value_3_i);
            if (residual_index_3_i == 32'sd0)
                state_midpoint_recon_3_0_out = midpoint_recon_3_i;
            if (residual_index_3_i == 32'sd1)
                state_midpoint_recon_3_1_out = midpoint_recon_3_i;
            if (residual_index_3_i == 32'sd2)
                state_midpoint_recon_3_2_out = midpoint_recon_3_i;
            abs_mid_error_3_i = dsc_abs_i(actual_3_i - midpoint_recon_3_i);
            if (cfg_full_ich_err_precision == 0)
                abs_mid_error_3_i = abs_mid_error_3_i >>> (cfg_bits_per_component - 32'sd8);
            state_max_mid_error_3_out = dsc_max_i(state_max_mid_error_3, abs_mid_error_3_i);
            curr_line_write_3_enable = 1'b1;
            curr_line_write_3_component = cpnt_3_i;
            curr_line_write_3_index = hpos + 32'sd5;
            curr_line_write_3_value = recon_3_i;
        end
        if (midpoint_clamp_violation != 0) bound_violation = 1'b1;
        if (illegal_domain != 0) domain_valid = 1'b0;
        if (bound_violation != 0) domain_valid = 1'b0;
    end
endmodule
