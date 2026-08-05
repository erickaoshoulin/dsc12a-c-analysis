// Hash-pinned provisional AddBits child; the adapter binds command slots to this module.
module addbits_encode_transition(
    input  logic [31:0] data,
    input  logic [5:0] nbits,
    input  logic [7:0] byte_0,
    input  logic [7:0] byte_1,
    input  logic [7:0] byte_2,
    input  logic [7:0] byte_3,
    input  logic [7:0] byte_4,
    input  logic signed [31:0] num_bits,
    input  logic [31:0] fullness,
    input  logic [31:0] write_ptr,
    input  logic [31:0] fifo_size,
    input  logic [31:0] max_fullness,
    output logic [7:0] byte_0_out,
    output logic [7:0] byte_1_out,
    output logic [7:0] byte_2_out,
    output logic [7:0] byte_3_out,
    output logic [7:0] byte_4_out,
    output logic signed [31:0] num_bits_out,
    output logic [31:0] fullness_out,
    output logic [31:0] write_ptr_out,
    output logic [31:0] max_fullness_out
);
    logic [39:0] window_i;
    logic [39:0] window_out_i;
    logic [32:0] write_sum_i;
    integer i;

    always_comb begin
        window_i = {byte_0, byte_1, byte_2, byte_3, byte_4};
        window_out_i = window_i;
        for (i = 0; i < 32; i = i + 1) begin
            if (i < int'(nbits))
                window_out_i[39 - int'(write_ptr[2:0]) - i] = data[int'(nbits) - 1 - i];
        end
        byte_0_out = window_out_i[39 -: 8];
        byte_1_out = window_out_i[31 -: 8];
        byte_2_out = window_out_i[23 -: 8];
        byte_3_out = window_out_i[15 -: 8];
        byte_4_out = window_out_i[7 -: 8];
        num_bits_out = num_bits + {{26{1'b0}}, nbits};
        fullness_out = fullness + {{26{1'b0}}, nbits};
        write_sum_i = {1'b0, write_ptr} + {{27{1'b0}}, nbits};
        if (write_sum_i >= {1'b0, fifo_size})
            write_ptr_out = write_sum_i[31:0] - fifo_size;
        else
            write_ptr_out = write_sum_i[31:0];
        if (fullness_out > max_fullness)
            max_fullness_out = fullness_out;
        else
            max_fullness_out = max_fullness;
    end
endmodule

module vlcunit_encode_transition(
    input logic helper_results_valid,
    input logic signed [31:0] helper_qlevel,
    input logic signed [31:0] helper_adj_predicted_size,
    input logic helper_flatness_info_sent,
    input logic signed [31:0] helper_escape_code_size,
    input logic helper_ich_decision,
    input logic signed [31:0] helper_max_residual_size,
    input logic signed [31:0] helper_predicted_size,
    input logic signed [31:0] helper_required_size_0,
    input logic signed [31:0] helper_required_size_1,
    input logic signed [31:0] helper_required_size_2,
    input logic signed [31:0] cfg_bits_per_component,
    input logic signed [31:0] cfg_somewhat_flat_qp_thresh,
    input logic signed [31:0] unit,
    input logic signed [31:0] quantized_residual_0,
    input logic signed [31:0] quantized_residual_1,
    input logic signed [31:0] quantized_residual_2,
    input logic signed [31:0] force_p1_ich2,
    input logic signed [31:0] state_num_bits,
    input logic signed [31:0] state_force_mpp,
    input logic signed [31:0] state_primary_qp,
    input logic signed [31:0] state_group_count,
    input logic signed [31:0] state_prev_first_flat,
    input logic signed [31:0] state_first_flat,
    input logic signed [31:0] state_flatness_type,
    input logic signed [31:0] state_ich_selected,
    input logic signed [31:0] state_prev_ich_selected,
    input logic signed [31:0] state_ich_indices_in_group,
    input logic signed [31:0] state_cpnt_bit_depth_0,
    input logic signed [31:0] state_cpnt_bit_depth_1,
    input logic signed [31:0] state_cpnt_bit_depth_2,
    input logic signed [31:0] state_cpnt_bit_depth_3,
    input logic signed [31:0] state_unit_c_type_0,
    input logic signed [31:0] state_unit_c_type_1,
    input logic signed [31:0] state_unit_c_type_2,
    input logic signed [31:0] state_unit_c_type_3,
    input logic signed [31:0] state_unit_ssp_map_0,
    input logic signed [31:0] state_unit_ssp_map_1,
    input logic signed [31:0] state_unit_ssp_map_2,
    input logic signed [31:0] state_unit_ssp_map_3,
    input logic signed [31:0] state_ich_index_unit_map_0,
    input logic signed [31:0] state_ich_index_unit_map_1,
    input logic signed [31:0] state_ich_index_unit_map_2,
    input logic signed [31:0] state_ich_index_unit_map_3,
    input logic signed [31:0] state_ich_index_unit_map_4,
    input logic signed [31:0] state_ich_index_unit_map_5,
    input logic signed [31:0] state_ich_lookup_0,
    input logic signed [31:0] state_ich_lookup_1,
    input logic signed [31:0] state_ich_lookup_2,
    input logic signed [31:0] state_ich_lookup_3,
    input logic signed [31:0] state_ich_lookup_4,
    input logic signed [31:0] state_ich_lookup_5,
    input logic signed [31:0] state_orig_within_qerr_0,
    input logic signed [31:0] state_orig_within_qerr_1,
    input logic signed [31:0] state_orig_within_qerr_2,
    input logic signed [31:0] state_orig_within_qerr_3,
    input logic signed [31:0] state_orig_within_qerr_4,
    input logic signed [31:0] state_orig_within_qerr_5,
    input logic signed [31:0] state_quantized_residual_mid_0_0,
    input logic signed [31:0] state_quantized_residual_mid_0_1,
    input logic signed [31:0] state_quantized_residual_mid_0_2,
    input logic signed [31:0] state_quantized_residual_mid_1_0,
    input logic signed [31:0] state_quantized_residual_mid_1_1,
    input logic signed [31:0] state_quantized_residual_mid_1_2,
    input logic signed [31:0] state_quantized_residual_mid_2_0,
    input logic signed [31:0] state_quantized_residual_mid_2_1,
    input logic signed [31:0] state_quantized_residual_mid_2_2,
    input logic signed [31:0] state_quantized_residual_mid_3_0,
    input logic signed [31:0] state_quantized_residual_mid_3_1,
    input logic signed [31:0] state_quantized_residual_mid_3_2,
    input logic signed [31:0] state_midpoint_selected_0,
    input logic signed [31:0] state_midpoint_selected_1,
    input logic signed [31:0] state_midpoint_selected_2,
    input logic signed [31:0] state_midpoint_selected_3,
    input logic signed [31:0] state_predicted_size_0,
    input logic signed [31:0] state_predicted_size_1,
    input logic signed [31:0] state_predicted_size_2,
    input logic signed [31:0] state_predicted_size_3,
    input logic signed [31:0] state_rc_size_unit_0,
    input logic signed [31:0] state_rc_size_unit_1,
    input logic signed [31:0] state_rc_size_unit_2,
    input logic signed [31:0] state_rc_size_unit_3,
    output logic domain_valid,
    output logic illegal_domain,
    output logic fatal_error,
    output logic [3:0] fatal_error_code,
    output logic bounded_loop_violation,
    output logic command_overflow,
    output logic arithmetic_domain_violation,
    output logic source_order_valid,
    output logic signed [31:0] num_bits_delta_out,
    output logic [3:0] addbits_command_count,
    output logic signed [31:0] state_num_bits_out,
    output logic signed [31:0] state_flatness_type_out,
    output logic signed [31:0] state_ich_selected_out,
    output logic signed [31:0] state_prev_ich_selected_out,
    output logic signed [31:0] state_midpoint_selected_0_out,
    output logic signed [31:0] state_midpoint_selected_1_out,
    output logic signed [31:0] state_midpoint_selected_2_out,
    output logic signed [31:0] state_midpoint_selected_3_out,
    output logic signed [31:0] state_predicted_size_0_out,
    output logic signed [31:0] state_predicted_size_1_out,
    output logic signed [31:0] state_predicted_size_2_out,
    output logic signed [31:0] state_predicted_size_3_out,
    output logic signed [31:0] state_rc_size_unit_0_out,
    output logic signed [31:0] state_rc_size_unit_1_out,
    output logic signed [31:0] state_rc_size_unit_2_out,
    output logic signed [31:0] state_rc_size_unit_3_out,
    output logic addbits_cmd_valid_0,
    output logic signed [31:0] addbits_cmd_ctype_0,
    output logic signed [31:0] addbits_cmd_data_0,
    output logic [5:0] addbits_cmd_nbits_0,
    output logic addbits_cmd_valid_1,
    output logic signed [31:0] addbits_cmd_ctype_1,
    output logic signed [31:0] addbits_cmd_data_1,
    output logic [5:0] addbits_cmd_nbits_1,
    output logic addbits_cmd_valid_2,
    output logic signed [31:0] addbits_cmd_ctype_2,
    output logic signed [31:0] addbits_cmd_data_2,
    output logic [5:0] addbits_cmd_nbits_2,
    output logic addbits_cmd_valid_3,
    output logic signed [31:0] addbits_cmd_ctype_3,
    output logic signed [31:0] addbits_cmd_data_3,
    output logic [5:0] addbits_cmd_nbits_3,
    output logic addbits_cmd_valid_4,
    output logic signed [31:0] addbits_cmd_ctype_4,
    output logic signed [31:0] addbits_cmd_data_4,
    output logic [5:0] addbits_cmd_nbits_4,
    output logic addbits_cmd_valid_5,
    output logic signed [31:0] addbits_cmd_ctype_5,
    output logic signed [31:0] addbits_cmd_data_5,
    output logic [5:0] addbits_cmd_nbits_5,
    output logic addbits_cmd_valid_6,
    output logic signed [31:0] addbits_cmd_ctype_6,
    output logic signed [31:0] addbits_cmd_data_6,
    output logic [5:0] addbits_cmd_nbits_6,
    output logic addbits_cmd_valid_7,
    output logic signed [31:0] addbits_cmd_ctype_7,
    output logic signed [31:0] addbits_cmd_data_7,
    output logic [5:0] addbits_cmd_nbits_7,
    output logic addbits_cmd_valid_8,
    output logic signed [31:0] addbits_cmd_ctype_8,
    output logic signed [31:0] addbits_cmd_data_8,
    output logic [5:0] addbits_cmd_nbits_8
);

    // Generator-only candidate: no C, adapter, or promotion behavior is inlined.
    // All command slots are bounded and emitted in immutable C source order.
    integer i;
    integer command_count_i;
    logic signed [63:0] num_bits_delta_wide_i;
    logic signed [63:0] num_bits_wide_i;
    logic signed [31:0] cpnt_depth_i [0:3];
    logic signed [31:0] unit_c_type_i [0:3];
    logic signed [31:0] unit_ssp_map_i [0:3];
    logic signed [31:0] ich_index_unit_map_i [0:5];
    logic signed [31:0] ich_lookup_i [0:5];
    logic signed [31:0] orig_within_qerr_i [0:5];
    logic signed [31:0] quantized_mid_i [0:3][0:2];
    logic signed [31:0] midpoint_selected_i [0:3];
    logic signed [31:0] predicted_size_i [0:3];
    logic signed [31:0] rc_size_unit_i [0:3];
    logic addbits_cmd_valid_i [0:8];
    logic signed [31:0] addbits_cmd_ctype_i [0:8];
    logic signed [31:0] addbits_cmd_data_i [0:8];
    logic [5:0] addbits_cmd_nbits_i [0:8];
    logic signed [31:0] force_mpp_i;
    logic signed [31:0] qp_i;
    logic signed [31:0] cpnt_i;
    logic signed [31:0] ssp_i;
    logic signed [31:0] qlevel_i;
    logic signed [31:0] adj_predicted_size_i;
    logic signed [31:0] max_size_i;
    logic signed [31:0] prefix_value_i;
    logic signed [31:0] size_i;
    logic signed [31:0] max_pfx_size_i;
    logic signed [31:0] alt_pfx_i;
    logic signed [31:0] alt_size_to_generate_i;
    logic signed [31:0] ich_disallow_i;
    logic signed [31:0] all_orig_within_qerr_i;
    logic signed [31:0] early_return_i;
    logic signed [31:0] flatness_type_i;
    logic signed [31:0] ich_selected_i;
    logic signed [31:0] prev_ich_selected_i;
    logic signed [31:0] required_size_i [0:2];
    logic signed [31:0] quantized_residual_i [0:2];
    logic signed [31:0] component_limit_i;
    logic fatal_error_i;
    logic [3:0] fatal_error_code_i;
    logic bounded_loop_violation_i;
    logic command_overflow_i;
    logic arithmetic_domain_violation_i;
    logic source_order_valid_i;

    function automatic logic [5:0] narrow_nbits(input logic signed [31:0] value);
        begin
            narrow_nbits = value[5:0];
        end
    endfunction

    function automatic logic signed [63:0] widen_signed(input logic signed [31:0] value);
        begin
            widen_signed = {{32{value[31]}}, value};
        end
    endfunction

`define emit_addbits(CTYPE_ARG, DATA_ARG, NBITS_ARG) \
        begin \
            if ((NBITS_ARG < 32'sd0) || (NBITS_ARG > 32'sd32)) begin \
                arithmetic_domain_violation_i = 1'b1; \
                fatal_error_i = 1'b1; \
                fatal_error_code_i = 4'd3; \
            end else if (command_count_i >= 9) begin \
                command_overflow_i = 1'b1; \
                bounded_loop_violation_i = 1'b1; \
                fatal_error_i = 1'b1; \
                fatal_error_code_i = 4'd2; \
            end else begin \
                addbits_cmd_valid_i[command_count_i] = 1'b1; \
                addbits_cmd_ctype_i[command_count_i] = CTYPE_ARG; \
                addbits_cmd_data_i[command_count_i] = DATA_ARG; \
                addbits_cmd_nbits_i[command_count_i] = narrow_nbits(NBITS_ARG); \
                num_bits_delta_wide_i = num_bits_delta_wide_i + widen_signed(NBITS_ARG); \
                command_count_i = command_count_i + 1; \
            end \
        end

    always_comb begin
        domain_valid = 1'b1;
        illegal_domain = 1'b0;
        fatal_error_i = 1'b0;
        fatal_error_code_i = 4'd0;
        bounded_loop_violation_i = 1'b0;
        command_overflow_i = 1'b0;
        arithmetic_domain_violation_i = 1'b0;
        source_order_valid_i = 1'b1;
        command_count_i = 0;
        num_bits_delta_wide_i = 64'sd0;
        num_bits_wide_i = {{32{state_num_bits[31]}}, state_num_bits};
        state_num_bits_out = state_num_bits;
        force_mpp_i = state_force_mpp;
        qp_i = state_primary_qp;
        cpnt_i = 32'sd0;
        ssp_i = 32'sd0;
        qlevel_i = helper_qlevel;
        adj_predicted_size_i = helper_adj_predicted_size;
        alt_size_to_generate_i = helper_escape_code_size;
        max_pfx_size_i = helper_max_residual_size;
        max_size_i = 32'sd0;
        prefix_value_i = 32'sd0;
        size_i = 32'sd0;
        alt_pfx_i = 32'sd0;
        ich_disallow_i = 32'sd0;
        all_orig_within_qerr_i = 32'sd1;
        early_return_i = 32'sd0;
        flatness_type_i = state_flatness_type;
        ich_selected_i = state_ich_selected;
        prev_ich_selected_i = state_prev_ich_selected;
        cpnt_depth_i[0] = state_cpnt_bit_depth_0;
        cpnt_depth_i[1] = state_cpnt_bit_depth_1;
        cpnt_depth_i[2] = state_cpnt_bit_depth_2;
        cpnt_depth_i[3] = state_cpnt_bit_depth_3;
        unit_c_type_i[0] = state_unit_c_type_0;
        unit_c_type_i[1] = state_unit_c_type_1;
        unit_c_type_i[2] = state_unit_c_type_2;
        unit_c_type_i[3] = state_unit_c_type_3;
        unit_ssp_map_i[0] = state_unit_ssp_map_0;
        unit_ssp_map_i[1] = state_unit_ssp_map_1;
        unit_ssp_map_i[2] = state_unit_ssp_map_2;
        unit_ssp_map_i[3] = state_unit_ssp_map_3;
        ich_index_unit_map_i[0] = state_ich_index_unit_map_0;
        ich_index_unit_map_i[1] = state_ich_index_unit_map_1;
        ich_index_unit_map_i[2] = state_ich_index_unit_map_2;
        ich_index_unit_map_i[3] = state_ich_index_unit_map_3;
        ich_index_unit_map_i[4] = state_ich_index_unit_map_4;
        ich_index_unit_map_i[5] = state_ich_index_unit_map_5;
        ich_lookup_i[0] = state_ich_lookup_0;
        ich_lookup_i[1] = state_ich_lookup_1;
        ich_lookup_i[2] = state_ich_lookup_2;
        ich_lookup_i[3] = state_ich_lookup_3;
        ich_lookup_i[4] = state_ich_lookup_4;
        ich_lookup_i[5] = state_ich_lookup_5;
        orig_within_qerr_i[0] = state_orig_within_qerr_0;
        orig_within_qerr_i[1] = state_orig_within_qerr_1;
        orig_within_qerr_i[2] = state_orig_within_qerr_2;
        orig_within_qerr_i[3] = state_orig_within_qerr_3;
        orig_within_qerr_i[4] = state_orig_within_qerr_4;
        orig_within_qerr_i[5] = state_orig_within_qerr_5;
        quantized_mid_i[0][0] = state_quantized_residual_mid_0_0;
        quantized_mid_i[0][1] = state_quantized_residual_mid_0_1;
        quantized_mid_i[0][2] = state_quantized_residual_mid_0_2;
        midpoint_selected_i[0] = state_midpoint_selected_0;
        predicted_size_i[0] = state_predicted_size_0;
        rc_size_unit_i[0] = state_rc_size_unit_0;
        quantized_mid_i[1][0] = state_quantized_residual_mid_1_0;
        quantized_mid_i[1][1] = state_quantized_residual_mid_1_1;
        quantized_mid_i[1][2] = state_quantized_residual_mid_1_2;
        midpoint_selected_i[1] = state_midpoint_selected_1;
        predicted_size_i[1] = state_predicted_size_1;
        rc_size_unit_i[1] = state_rc_size_unit_1;
        quantized_mid_i[2][0] = state_quantized_residual_mid_2_0;
        quantized_mid_i[2][1] = state_quantized_residual_mid_2_1;
        quantized_mid_i[2][2] = state_quantized_residual_mid_2_2;
        midpoint_selected_i[2] = state_midpoint_selected_2;
        predicted_size_i[2] = state_predicted_size_2;
        rc_size_unit_i[2] = state_rc_size_unit_2;
        quantized_mid_i[3][0] = state_quantized_residual_mid_3_0;
        quantized_mid_i[3][1] = state_quantized_residual_mid_3_1;
        quantized_mid_i[3][2] = state_quantized_residual_mid_3_2;
        midpoint_selected_i[3] = state_midpoint_selected_3;
        predicted_size_i[3] = state_predicted_size_3;
        rc_size_unit_i[3] = state_rc_size_unit_3;
        required_size_i[0] = helper_required_size_0;
        required_size_i[1] = helper_required_size_1;
        required_size_i[2] = helper_required_size_2;
        quantized_residual_i[0] = quantized_residual_0;
        quantized_residual_i[1] = quantized_residual_1;
        quantized_residual_i[2] = quantized_residual_2;
        component_limit_i = 32'sd0;
        addbits_cmd_valid_i[0] = 1'b0;
        addbits_cmd_ctype_i[0] = 32'sd0;
        addbits_cmd_data_i[0] = 32'sd0;
        addbits_cmd_nbits_i[0] = 6'd0;
        addbits_cmd_valid_i[1] = 1'b0;
        addbits_cmd_ctype_i[1] = 32'sd0;
        addbits_cmd_data_i[1] = 32'sd0;
        addbits_cmd_nbits_i[1] = 6'd0;
        addbits_cmd_valid_i[2] = 1'b0;
        addbits_cmd_ctype_i[2] = 32'sd0;
        addbits_cmd_data_i[2] = 32'sd0;
        addbits_cmd_nbits_i[2] = 6'd0;
        addbits_cmd_valid_i[3] = 1'b0;
        addbits_cmd_ctype_i[3] = 32'sd0;
        addbits_cmd_data_i[3] = 32'sd0;
        addbits_cmd_nbits_i[3] = 6'd0;
        addbits_cmd_valid_i[4] = 1'b0;
        addbits_cmd_ctype_i[4] = 32'sd0;
        addbits_cmd_data_i[4] = 32'sd0;
        addbits_cmd_nbits_i[4] = 6'd0;
        addbits_cmd_valid_i[5] = 1'b0;
        addbits_cmd_ctype_i[5] = 32'sd0;
        addbits_cmd_data_i[5] = 32'sd0;
        addbits_cmd_nbits_i[5] = 6'd0;
        addbits_cmd_valid_i[6] = 1'b0;
        addbits_cmd_ctype_i[6] = 32'sd0;
        addbits_cmd_data_i[6] = 32'sd0;
        addbits_cmd_nbits_i[6] = 6'd0;
        addbits_cmd_valid_i[7] = 1'b0;
        addbits_cmd_ctype_i[7] = 32'sd0;
        addbits_cmd_data_i[7] = 32'sd0;
        addbits_cmd_nbits_i[7] = 6'd0;
        addbits_cmd_valid_i[8] = 1'b0;
        addbits_cmd_ctype_i[8] = 32'sd0;
        addbits_cmd_data_i[8] = 32'sd0;
        addbits_cmd_nbits_i[8] = 6'd0;

        // Legal-domain checks separate the C assertion/error path from RTL semantics.
        if ((unit < 32'sd0) || (unit > 32'sd3) ||
            (force_p1_ich2 < 32'sd0) || (force_p1_ich2 > 32'sd2) ||
            (cfg_bits_per_component < 32'sd8) || (cfg_bits_per_component > 32'sd16) ||
            (state_force_mpp < 32'sd0) || (state_force_mpp > 32'sd1) ||
            (state_ich_selected < 32'sd0) || (state_ich_selected > 32'sd1) ||
            (state_ich_indices_in_group < 32'sd0) || (state_ich_indices_in_group > 32'sd6) ||
            (helper_results_valid == 1'b0)) begin
            domain_valid = 1'b0;
            illegal_domain = 1'b1;
            fatal_error_i = 1'b1;
            fatal_error_code_i = (helper_results_valid == 1'b0) ? 4'd4 : 4'd1;
        end
        for (i = 0; i < 6; i = i + 1) begin
            if (i < state_ich_indices_in_group) begin
                if ((ich_index_unit_map_i[i] < 32'sd0) || (ich_index_unit_map_i[i] > 32'sd3) ||
                    (orig_within_qerr_i[i] < 32'sd0) || (orig_within_qerr_i[i] > 32'sd1)) begin
                    domain_valid = 1'b0;
                    bounded_loop_violation_i = 1'b1;
                    fatal_error_i = 1'b1;
                    fatal_error_code_i = 4'd2;
                end
            end
        end
        if (domain_valid != 1'b0) begin
            // Source lines 1514..1526: scalar setup and previous-ICH capture.
            case (unit)
                32'sd0: begin cpnt_i = unit_c_type_i[0]; ssp_i = unit_ssp_map_i[0]; end
                32'sd1: begin cpnt_i = unit_c_type_i[1]; ssp_i = unit_ssp_map_i[1]; end
                32'sd2: begin cpnt_i = unit_c_type_i[2]; ssp_i = unit_ssp_map_i[2]; end
                default: begin cpnt_i = unit_c_type_i[3]; ssp_i = unit_ssp_map_i[3]; end
            endcase
            case (cpnt_i)
                32'sd0: if ((cpnt_depth_i[0] < 32'sd1) || (cpnt_depth_i[0] > 32'sd32)) begin domain_valid = 1'b0; illegal_domain = 1'b1; fatal_error_i = 1'b1; fatal_error_code_i = 4'd1; end
                32'sd1: if ((cpnt_depth_i[1] < 32'sd1) || (cpnt_depth_i[1] > 32'sd32)) begin domain_valid = 1'b0; illegal_domain = 1'b1; fatal_error_i = 1'b1; fatal_error_code_i = 4'd1; end
                32'sd2: if ((cpnt_depth_i[2] < 32'sd1) || (cpnt_depth_i[2] > 32'sd32)) begin domain_valid = 1'b0; illegal_domain = 1'b1; fatal_error_i = 1'b1; fatal_error_code_i = 4'd1; end
                32'sd3: if ((cpnt_depth_i[3] < 32'sd1) || (cpnt_depth_i[3] > 32'sd32)) begin domain_valid = 1'b0; illegal_domain = 1'b1; fatal_error_i = 1'b1; fatal_error_code_i = 4'd1; end
                default: begin domain_valid = 1'b0; illegal_domain = 1'b1; fatal_error_i = 1'b1; fatal_error_code_i = 4'd1; end
            endcase
            case (cpnt_i)
                32'sd0: component_limit_i = cpnt_depth_i[0] - qlevel_i;
                32'sd1: component_limit_i = cpnt_depth_i[1] - qlevel_i;
                32'sd2: component_limit_i = cpnt_depth_i[2] - qlevel_i;
                default: component_limit_i = cpnt_depth_i[3] - qlevel_i;
            endcase
            if ((ssp_i < 32'sd0) || (ssp_i > 32'sd3)) begin domain_valid = 1'b0; illegal_domain = 1'b1; fatal_error_i = 1'b1; fatal_error_code_i = 4'd1; end
            ich_disallow_i = ((cfg_bits_per_component == 32'sd16) && (unit == 32'sd0) &&
                ((32'sd3 * qlevel_i) <= (32'sd3 - adj_predicted_size_i))) ? 32'sd1 : 32'sd0;
            if (unit == 32'sd0)
                prev_ich_selected_i = state_ich_selected;

            // Source lines 1528..1552: flatness syntax elements precede all later commands.
            if ((unit == 32'sd0) && ((state_group_count % 32'sd4) == 32'sd3) &&
                (helper_flatness_info_sent != 1'b0)) begin
                if (state_prev_first_flat < 32'sd0)
                    `emit_addbits(ssp_i, 32'sd0, 32'sd1) // source line 1535
                else
                    `emit_addbits(ssp_i, 32'sd1, 32'sd1) // source line 1541
            end
            if ((unit == 32'sd0) && ((state_group_count % 32'sd4) == 32'sd0) &&
                (state_first_flat >= 32'sd0)) begin
                if (qp_i >= cfg_somewhat_flat_qp_thresh)
                    `emit_addbits(ssp_i, state_flatness_type, 32'sd1) // source line 1548
                else
                    flatness_type_i = 32'sd0;
                `emit_addbits(ssp_i, state_first_flat, 32'sd2) // source line 1552
            end

            // Source lines 1556..1561: bounded early ICH path.
            if ((unit > 32'sd0) && (state_ich_selected != 32'sd0)) begin
                for (i = 0; i < 6; i = i + 1) begin
                    if ((i < state_ich_indices_in_group) && (ich_index_unit_map_i[i] == unit))
                        `emit_addbits(ssp_i, ich_lookup_i[i], 32'sd5) // source line 1560
                end
                early_return_i = 32'sd1;
            end

            if (early_return_i == 32'sd0) begin
                // Source lines 1564..1584: required-size reduction and MPP override.
                max_size_i = 32'sd0;
                for (i = 0; i < 3; i = i + 1) begin
                    if (required_size_i[i] > max_size_i)
                        max_size_i = required_size_i[i];
                end
                case (cpnt_i)
                    32'sd0: if ((force_mpp_i != 32'sd0) || (max_size_i >= (cpnt_depth_i[0] - qlevel_i))) begin max_size_i = cpnt_depth_i[0] - qlevel_i; for (i = 0; i < 3; i = i + 1) required_size_i[i] = max_size_i; end
                    32'sd1: if ((force_mpp_i != 32'sd0) || (max_size_i >= (cpnt_depth_i[1] - qlevel_i))) begin max_size_i = cpnt_depth_i[1] - qlevel_i; for (i = 0; i < 3; i = i + 1) required_size_i[i] = max_size_i; end
                    32'sd2: if ((force_mpp_i != 32'sd0) || (max_size_i >= (cpnt_depth_i[2] - qlevel_i))) begin max_size_i = cpnt_depth_i[2] - qlevel_i; for (i = 0; i < 3; i = i + 1) required_size_i[i] = max_size_i; end
                    default: if ((force_mpp_i != 32'sd0) || (max_size_i >= (cpnt_depth_i[3] - qlevel_i))) begin max_size_i = cpnt_depth_i[3] - qlevel_i; for (i = 0; i < 3; i = i + 1) required_size_i[i] = max_size_i; end
                endcase
                if (adj_predicted_size_i < max_size_i) begin
                    prefix_value_i = max_size_i - adj_predicted_size_i;
                    size_i = max_size_i;
                end else begin
                    prefix_value_i = 32'sd0;
                    size_i = adj_predicted_size_i;
                end
                if (unit == 32'sd0)
                    prefix_value_i = prefix_value_i + ((prev_ich_selected_i != 32'sd0) && (ich_disallow_i == 32'sd0));

                // Source lines 1600..1607: bounded all-orig-within-qerr reduction.
                ich_selected_i = 32'sd0;
                all_orig_within_qerr_i = 32'sd1;
                for (i = 0; i < 6; i = i + 1) begin
                    if ((i < state_ich_indices_in_group) && (orig_within_qerr_i[i] == 32'sd0))
                        all_orig_within_qerr_i = 32'sd0;
                end

                // Source lines 1610..1645: ICH decision and source-ordered commands.
                if ((force_p1_ich2 != 32'sd1) && (unit == 32'sd0) &&
                    (all_orig_within_qerr_i != 32'sd0) && (force_mpp_i == 32'sd0) &&
                    (ich_disallow_i == 32'sd0)) begin
                    if (prev_ich_selected_i != 32'sd0)
                        alt_pfx_i = 32'sd0;
                    else
                        alt_pfx_i = alt_size_to_generate_i - adj_predicted_size_i;
                    if ((force_p1_ich2 == 32'sd2) || (helper_ich_decision != 1'b0)) begin
                        ich_selected_i = 32'sd1;
                        if (prev_ich_selected_i != 32'sd0)
                            `emit_addbits(ssp_i, 32'sd1, alt_pfx_i + 32'sd1) // source line 1633
                        else
                            `emit_addbits(ssp_i, 32'sd0, alt_pfx_i) // source line 1635
                        for (i = 0; i < 6; i = i + 1) begin
                            if ((i < state_ich_indices_in_group) && (ich_index_unit_map_i[i] == unit))
                                `emit_addbits(ssp_i, ich_lookup_i[i], 32'sd5) // source line 1640
                        end
                        rc_size_unit_i[0] = (state_ich_indices_in_group * 32'sd5) + 32'sd1;
                        for (i = 1; i < 4; i = i + 1)
                            rc_size_unit_i[i] = 32'sd0;
                        early_return_i = 32'sd1;
                    end
                end

                if (early_return_i == 32'sd0) begin
                    // Source lines 1650..1665: SE-size limiting syntax branch.
                    max_pfx_size_i = helper_max_residual_size + (((unit == 32'sd0) && (ich_disallow_i == 32'sd0)) ? 32'sd1 : 32'sd0) - adj_predicted_size_i;
                    if ((cfg_bits_per_component == 32'sd16) && (unit == 32'sd0) &&
                        (qlevel_i == 32'sd0) && (ich_disallow_i != 32'sd0) &&
                        ((max_pfx_size_i + (32'sd16 * 32'sd3)) > 32'sd61)) begin
                        max_pfx_size_i = 32'sd61 - (32'sd16 * 32'sd3);
                        prefix_value_i = max_pfx_size_i;
                        if (prefix_value_i >= max_pfx_size_i) begin
                            prefix_value_i = max_pfx_size_i;
                            case (cpnt_i)
                                32'sd0: begin size_i = cpnt_depth_i[0] - qlevel_i; max_size_i = size_i; end
                                32'sd1: begin size_i = cpnt_depth_i[1] - qlevel_i; max_size_i = size_i; end
                                32'sd2: begin size_i = cpnt_depth_i[2] - qlevel_i; max_size_i = size_i; end
                                default: begin size_i = cpnt_depth_i[3] - qlevel_i; max_size_i = size_i; end
                            endcase
                            for (i = 0; i < 3; i = i + 1)
                                required_size_i[i] = max_size_i;
                        end
                    end

                    // Source lines 1671..1694: prefix then three sample commands.
                    if (prefix_value_i == max_pfx_size_i)
                        `emit_addbits(ssp_i, 32'sd0, max_pfx_size_i) // source line 1673
                    else
                        `emit_addbits(ssp_i, 32'sd1, prefix_value_i + 32'sd1) // source line 1675
                    for (i = 0; i < 3; i = i + 1) begin
                        if (max_size_i == component_limit_i) begin
                            `emit_addbits(ssp_i, quantized_mid_i[unit][i], size_i) // source line 1682
                            midpoint_selected_i[unit] = 32'sd1;
                        end else begin
                            `emit_addbits(ssp_i, quantized_residual_i[i], size_i) // source line 1689
                            midpoint_selected_i[unit] = 32'sd0;
                        end
                    end
                    rc_size_unit_i[unit] = (max_size_i * 32'sd3) + 32'sd1;
                    predicted_size_i[unit] = helper_predicted_size;
                end
            end
        end

        if ((num_bits_delta_wide_i > 64'sd2147483647) ||
            (num_bits_delta_wide_i < -64'sd2147483648)) begin
            arithmetic_domain_violation_i = 1'b1;
            fatal_error_i = 1'b1;
            fatal_error_code_i = 4'd3;
        end
        num_bits_wide_i = {{32{state_num_bits[31]}}, state_num_bits} + num_bits_delta_wide_i;
        if ((num_bits_wide_i > 64'sd2147483647) || (num_bits_wide_i < -64'sd2147483648)) begin
            arithmetic_domain_violation_i = 1'b1;
            fatal_error_i = 1'b1;
            fatal_error_code_i = 4'd3;
        end

        if (fatal_error_i != 1'b0) begin
            // Fatal paths have no observable state or command commit.
            domain_valid = 1'b0;
            command_count_i = 0;
            num_bits_delta_wide_i = 64'sd0;
            flatness_type_i = state_flatness_type;
            ich_selected_i = state_ich_selected;
            prev_ich_selected_i = state_prev_ich_selected;
            midpoint_selected_i[0] = state_midpoint_selected_0;
            predicted_size_i[0] = state_predicted_size_0;
            rc_size_unit_i[0] = state_rc_size_unit_0;
            midpoint_selected_i[1] = state_midpoint_selected_1;
            predicted_size_i[1] = state_predicted_size_1;
            rc_size_unit_i[1] = state_rc_size_unit_1;
            midpoint_selected_i[2] = state_midpoint_selected_2;
            predicted_size_i[2] = state_predicted_size_2;
            rc_size_unit_i[2] = state_rc_size_unit_2;
            midpoint_selected_i[3] = state_midpoint_selected_3;
            predicted_size_i[3] = state_predicted_size_3;
            rc_size_unit_i[3] = state_rc_size_unit_3;
            for (i = 0; i < 9; i = i + 1) begin
                addbits_cmd_valid_i[i] = 1'b0;
                addbits_cmd_ctype_i[i] = 32'sd0;
                addbits_cmd_data_i[i] = 32'sd0;
                addbits_cmd_nbits_i[i] = 6'd0;
            end
        end else begin
            state_num_bits_out = num_bits_wide_i[31:0];
        end
        domain_valid = domain_valid;
        illegal_domain = illegal_domain;
        fatal_error = fatal_error_i;
        fatal_error_code = fatal_error_code_i;
        bounded_loop_violation = bounded_loop_violation_i;
        command_overflow = command_overflow_i;
        arithmetic_domain_violation = arithmetic_domain_violation_i;
        source_order_valid = source_order_valid_i && !fatal_error_i;
        num_bits_delta_out = num_bits_delta_wide_i[31:0];
        addbits_command_count = command_count_i[3:0];
        state_flatness_type_out = flatness_type_i;
        state_ich_selected_out = ich_selected_i;
        state_prev_ich_selected_out = prev_ich_selected_i;
        state_midpoint_selected_0_out = midpoint_selected_i[0];
        state_predicted_size_0_out = predicted_size_i[0];
        state_rc_size_unit_0_out = rc_size_unit_i[0];
        state_midpoint_selected_1_out = midpoint_selected_i[1];
        state_predicted_size_1_out = predicted_size_i[1];
        state_rc_size_unit_1_out = rc_size_unit_i[1];
        state_midpoint_selected_2_out = midpoint_selected_i[2];
        state_predicted_size_2_out = predicted_size_i[2];
        state_rc_size_unit_2_out = rc_size_unit_i[2];
        state_midpoint_selected_3_out = midpoint_selected_i[3];
        state_predicted_size_3_out = predicted_size_i[3];
        state_rc_size_unit_3_out = rc_size_unit_i[3];
        addbits_cmd_valid_0 = addbits_cmd_valid_i[0];
        addbits_cmd_ctype_0 = addbits_cmd_ctype_i[0];
        addbits_cmd_data_0 = addbits_cmd_data_i[0];
        addbits_cmd_nbits_0 = addbits_cmd_nbits_i[0];
        addbits_cmd_valid_1 = addbits_cmd_valid_i[1];
        addbits_cmd_ctype_1 = addbits_cmd_ctype_i[1];
        addbits_cmd_data_1 = addbits_cmd_data_i[1];
        addbits_cmd_nbits_1 = addbits_cmd_nbits_i[1];
        addbits_cmd_valid_2 = addbits_cmd_valid_i[2];
        addbits_cmd_ctype_2 = addbits_cmd_ctype_i[2];
        addbits_cmd_data_2 = addbits_cmd_data_i[2];
        addbits_cmd_nbits_2 = addbits_cmd_nbits_i[2];
        addbits_cmd_valid_3 = addbits_cmd_valid_i[3];
        addbits_cmd_ctype_3 = addbits_cmd_ctype_i[3];
        addbits_cmd_data_3 = addbits_cmd_data_i[3];
        addbits_cmd_nbits_3 = addbits_cmd_nbits_i[3];
        addbits_cmd_valid_4 = addbits_cmd_valid_i[4];
        addbits_cmd_ctype_4 = addbits_cmd_ctype_i[4];
        addbits_cmd_data_4 = addbits_cmd_data_i[4];
        addbits_cmd_nbits_4 = addbits_cmd_nbits_i[4];
        addbits_cmd_valid_5 = addbits_cmd_valid_i[5];
        addbits_cmd_ctype_5 = addbits_cmd_ctype_i[5];
        addbits_cmd_data_5 = addbits_cmd_data_i[5];
        addbits_cmd_nbits_5 = addbits_cmd_nbits_i[5];
        addbits_cmd_valid_6 = addbits_cmd_valid_i[6];
        addbits_cmd_ctype_6 = addbits_cmd_ctype_i[6];
        addbits_cmd_data_6 = addbits_cmd_data_i[6];
        addbits_cmd_nbits_6 = addbits_cmd_nbits_i[6];
        addbits_cmd_valid_7 = addbits_cmd_valid_i[7];
        addbits_cmd_ctype_7 = addbits_cmd_ctype_i[7];
        addbits_cmd_data_7 = addbits_cmd_data_i[7];
        addbits_cmd_nbits_7 = addbits_cmd_nbits_i[7];
        addbits_cmd_valid_8 = addbits_cmd_valid_i[8];
        addbits_cmd_ctype_8 = addbits_cmd_ctype_i[8];
        addbits_cmd_data_8 = addbits_cmd_data_i[8];
        addbits_cmd_nbits_8 = addbits_cmd_nbits_i[8];
    end
endmodule
