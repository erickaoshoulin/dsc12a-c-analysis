module ichdecision_candidate_02 (
    input logic [5:0] adj_predicted_size,
    input logic [5:0] alt_pfx,
    input logic [5:0] alt_size_to_generate,
    input logic [1:0] dsc_version_minor,
    input logic native_420,
    input logic [9:0] flatness_det_thresh,
    input logic [2:0] somewhat_flat_qp_delta,
    input logic [2:0] units_per_group,
    input logic [1:0] pixels_in_group,
    input logic [15:0] hPos,
    input logic [15:0] slice_width,
    input logic prev_ich_selected,
    input logic [4:0] primary_qp,
    input logic [4:0] prev_primary_qp,
    input logic [2:0] ich_indices_in_group,
    input logic [2:0] num_components,
    input logic [4:0] cpnt_bit_depth_0,
    input logic [4:0] cpnt_bit_depth_1,
    input logic [4:0] cpnt_bit_depth_2,
    input logic [4:0] cpnt_bit_depth_3,
    input logic [1:0] unit_c_type_0,
    input logic [1:0] unit_c_type_1,
    input logic [1:0] unit_c_type_2,
    input logic [1:0] unit_c_type_3,
    input logic [15:0] unit_start_h_pos_0,
    input logic [15:0] unit_start_h_pos_1,
    input logic [15:0] unit_start_h_pos_2,
    input logic [15:0] unit_start_h_pos_3,
    input logic [4:0] predicted_size_0,
    input logic [4:0] predicted_size_1,
    input logic [4:0] predicted_size_2,
    input logic [4:0] predicted_size_3,
    input logic [16:0] max_error_0,
    input logic [16:0] max_error_1,
    input logic [16:0] max_error_2,
    input logic [16:0] max_error_3,
    input logic [16:0] max_mid_error_0,
    input logic [16:0] max_mid_error_1,
    input logic [16:0] max_mid_error_2,
    input logic [16:0] max_mid_error_3,
    input logic [16:0] max_ich_error_0,
    input logic [16:0] max_ich_error_1,
    input logic [16:0] max_ich_error_2,
    input logic [16:0] max_ich_error_3,
    input logic signed [16:0] quantized_residual_0_0,
    input logic signed [16:0] quantized_residual_0_1,
    input logic signed [16:0] quantized_residual_0_2,
    input logic signed [16:0] quantized_residual_1_0,
    input logic signed [16:0] quantized_residual_1_1,
    input logic signed [16:0] quantized_residual_1_2,
    input logic signed [16:0] quantized_residual_2_0,
    input logic signed [16:0] quantized_residual_2_1,
    input logic signed [16:0] quantized_residual_2_2,
    input logic signed [16:0] quantized_residual_3_0,
    input logic signed [16:0] quantized_residual_3_1,
    input logic signed [16:0] quantized_residual_3_2,
    input logic [4:0] qlevel_luma_primary,
    input logic [4:0] qlevel_chroma_primary,
    input logic [4:0] qlevel_luma_previous,
    input logic [4:0] qlevel_chroma_previous,
    input logic [4:0] qlevel_luma_flat,
    input logic [4:0] qlevel_chroma_flat,
    input logic [15:0] orig_0_0,
    input logic [15:0] orig_0_1,
    input logic [15:0] orig_0_2,
    input logic [15:0] orig_0_3,
    input logic [15:0] orig_0_4,
    input logic [15:0] orig_0_5,
    input logic [15:0] orig_0_6,
    input logic [15:0] orig_1_0,
    input logic [15:0] orig_1_1,
    input logic [15:0] orig_1_2,
    input logic [15:0] orig_1_3,
    input logic [15:0] orig_1_4,
    input logic [15:0] orig_1_5,
    input logic [15:0] orig_1_6,
    input logic [15:0] orig_2_0,
    input logic [15:0] orig_2_1,
    input logic [15:0] orig_2_2,
    input logic [15:0] orig_2_3,
    input logic [15:0] orig_2_4,
    input logic [15:0] orig_2_5,
    input logic [15:0] orig_2_6,
    input logic [15:0] orig_3_0,
    input logic [15:0] orig_3_1,
    input logic [15:0] orig_3_2,
    input logic [15:0] orig_3_3,
    input logic [15:0] orig_3_4,
    input logic [15:0] orig_3_5,
    input logic [15:0] orig_3_6,
    output logic return_value
);
    function automatic integer min_i;
        input integer left;
        input integer right;
        begin min_i = (left < right) ? left : right; end
    endfunction
    function automatic integer max_i;
        input integer left;
        input integer right;
        begin max_i = (left > right) ? left : right; end
    endfunction
    function automatic integer quant_divisor_i;
        input integer qlevel;
        begin
            quant_divisor_i = 1;
            case (qlevel)
                0: quant_divisor_i = 1;
                1: quant_divisor_i = 2;
                2: quant_divisor_i = 4;
                3: quant_divisor_i = 8;
                4: quant_divisor_i = 16;
                5: quant_divisor_i = 32;
                6: quant_divisor_i = 64;
                7: quant_divisor_i = 128;
                8: quant_divisor_i = 256;
                9: quant_divisor_i = 512;
                10: quant_divisor_i = 1024;
                11: quant_divisor_i = 2048;
                12: quant_divisor_i = 4096;
                13: quant_divisor_i = 8192;
                14: quant_divisor_i = 16384;
                15: quant_divisor_i = 32768;
                16: quant_divisor_i = 65536;
                default: quant_divisor_i = 1;
            endcase
        end
    endfunction
    function automatic integer residual_size_i;
        input integer value;
        begin
            residual_size_i = 0;
            if (value == 0) residual_size_i = 0;
            else if ((value >= 32'shffffffff) && (value <= 0)) residual_size_i = 1;
            else if ((value >= 32'shfffffffe) && (value <= 1)) residual_size_i = 2;
            else if ((value >= 32'shfffffffc) && (value <= 3)) residual_size_i = 3;
            else if ((value >= 32'shfffffff8) && (value <= 7)) residual_size_i = 4;
            else if ((value >= 32'shfffffff0) && (value <= 15)) residual_size_i = 5;
            else if ((value >= 32'shffffffe0) && (value <= 31)) residual_size_i = 6;
            else if ((value >= 32'shffffffc0) && (value <= 63)) residual_size_i = 7;
            else if ((value >= 32'shffffff80) && (value <= 127)) residual_size_i = 8;
            else if ((value >= 32'shffffff00) && (value <= 255)) residual_size_i = 9;
            else if ((value >= 32'shfffffe00) && (value <= 511)) residual_size_i = 10;
            else if ((value >= 32'shfffffc00) && (value <= 1023)) residual_size_i = 11;
            else if ((value >= 32'shfffff800) && (value <= 2047)) residual_size_i = 12;
            else if ((value >= 32'shfffff000) && (value <= 4095)) residual_size_i = 13;
            else if ((value >= 32'shffffe000) && (value <= 8191)) residual_size_i = 14;
            else if ((value >= 32'shffffc000) && (value <= 16383)) residual_size_i = 15;
            else if ((value >= 32'shffff8000) && (value <= 32767)) residual_size_i = 16;
            else if ((value >= 32'shffff0000) && (value <= 65535)) residual_size_i = 17;
        end
    endfunction
    function automatic integer ceil_log2_i;
        input integer value;
        begin
            if (value <= 0) ceil_log2_i = 0;
            else if (value <= 1) ceil_log2_i = 1;
            else if (value <= 3) ceil_log2_i = 2;
            else if (value <= 7) ceil_log2_i = 3;
            else if (value <= 15) ceil_log2_i = 4;
            else if (value <= 31) ceil_log2_i = 5;
            else if (value <= 63) ceil_log2_i = 6;
            else if (value <= 127) ceil_log2_i = 7;
            else if (value <= 255) ceil_log2_i = 8;
            else if (value <= 511) ceil_log2_i = 9;
            else if (value <= 1023) ceil_log2_i = 10;
            else if (value <= 2047) ceil_log2_i = 11;
            else if (value <= 4095) ceil_log2_i = 12;
            else if (value <= 8191) ceil_log2_i = 13;
            else if (value <= 16383) ceil_log2_i = 14;
            else if (value <= 32767) ceil_log2_i = 15;
            else ceil_log2_i = 16;
        end
    endfunction
    function automatic integer qlevel_for_i;
        input integer component;
        input integer luma_value;
        input integer chroma_value;
        begin
            if ((component % 3) == 0) qlevel_for_i = luma_value;
            else if ((native_420 != 0) && (component == 1)) qlevel_for_i = luma_value;
            else begin
                qlevel_for_i = chroma_value;
                if ((dsc_version_minor == 2) && (cpnt_bit_depth_0 == cpnt_bit_depth_1) && (qlevel_for_i > 0)) qlevel_for_i = qlevel_for_i - 1;
            end
        end
    endfunction
    function automatic integer depth_for_i;
        input integer component;
        begin
            case (component)
                0: depth_for_i = cpnt_bit_depth_0;
                1: depth_for_i = cpnt_bit_depth_1;
                2: depth_for_i = cpnt_bit_depth_2;
                3: depth_for_i = cpnt_bit_depth_3;
                default: depth_for_i = cpnt_bit_depth_0;
            endcase
        end
    endfunction
    function automatic integer orig_sample_i;
        input integer component;
        input integer offset;
        begin
            orig_sample_i = 0;
            case (component)
                0: begin
                    case (offset)
                        0: orig_sample_i = orig_0_0;
                        1: orig_sample_i = orig_0_1;
                        2: orig_sample_i = orig_0_2;
                        3: orig_sample_i = orig_0_3;
                        4: orig_sample_i = orig_0_4;
                        5: orig_sample_i = orig_0_5;
                        6: orig_sample_i = orig_0_6;
                        default: orig_sample_i = 0;
                    endcase
                end
                1: begin
                    case (offset)
                        0: orig_sample_i = orig_1_0;
                        1: orig_sample_i = orig_1_1;
                        2: orig_sample_i = orig_1_2;
                        3: orig_sample_i = orig_1_3;
                        4: orig_sample_i = orig_1_4;
                        5: orig_sample_i = orig_1_5;
                        6: orig_sample_i = orig_1_6;
                        default: orig_sample_i = 0;
                    endcase
                end
                2: begin
                    case (offset)
                        0: orig_sample_i = orig_2_0;
                        1: orig_sample_i = orig_2_1;
                        2: orig_sample_i = orig_2_2;
                        3: orig_sample_i = orig_2_3;
                        4: orig_sample_i = orig_2_4;
                        5: orig_sample_i = orig_2_5;
                        6: orig_sample_i = orig_2_6;
                        default: orig_sample_i = 0;
                    endcase
                end
                3: begin
                    case (offset)
                        0: orig_sample_i = orig_3_0;
                        1: orig_sample_i = orig_3_1;
                        2: orig_sample_i = orig_3_2;
                        3: orig_sample_i = orig_3_3;
                        4: orig_sample_i = orig_3_4;
                        5: orig_sample_i = orig_3_5;
                        6: orig_sample_i = orig_3_6;
                        default: orig_sample_i = 0;
                    endcase
                end
                default: orig_sample_i = 0;
            endcase
        end
    endfunction
    function automatic integer spread4_i;
        input integer component;
        begin
            spread4_i = max_i(max_i(max_i(orig_sample_i(component, 0), orig_sample_i(component, 1)), orig_sample_i(component, 2)), orig_sample_i(component, 3)) - min_i(min_i(min_i(orig_sample_i(component, 0), orig_sample_i(component, 1)), orig_sample_i(component, 2)), orig_sample_i(component, 3));
        end
    endfunction
    function automatic integer spread6_i;
        input integer component;
        begin
            spread6_i = max_i(max_i(max_i(max_i(max_i(orig_sample_i(component, 1), orig_sample_i(component, 2)), orig_sample_i(component, 3)), orig_sample_i(component, 4)), orig_sample_i(component, 5)), orig_sample_i(component, 6)) - min_i(min_i(min_i(min_i(min_i(orig_sample_i(component, 1), orig_sample_i(component, 2)), orig_sample_i(component, 3)), orig_sample_i(component, 4)), orig_sample_i(component, 5)), orig_sample_i(component, 6));
        end
    endfunction
    integer signed total_size_i;
    integer signed bits_p_mode_i;
    integer signed bits_ich_mode_i;
    integer signed log_err_p_mode_i;
    integer signed log_err_ich_mode_i;
    integer signed p_mode_cost_i;
    integer signed ich_mode_cost_i;
    integer signed qlevel_new_i;
    integer signed qlevel_old_i;
    integer signed qlevel_flat_i;
    integer signed bit_depth_i;
    integer signed max_residual_size_i;
    integer signed pred_size_i;
    integer signed sample_hpos_i;
    integer signed req_size_i;
    integer signed flat_index_i;
    integer signed first_somewhat_i;
    integer signed first_very_i;
    integer signed second_somewhat_i;
    integer signed second_very_i;
    integer signed max_size_0_i;
    integer signed max_p_error_0_i;
    integer signed midpoint_0_i;
    integer signed residual_0_i;
    integer signed req_size_0_i;
    integer signed max_size_1_i;
    integer signed max_p_error_1_i;
    integer signed midpoint_1_i;
    integer signed residual_1_i;
    integer signed req_size_1_i;
    integer signed max_size_2_i;
    integer signed max_p_error_2_i;
    integer signed midpoint_2_i;
    integer signed residual_2_i;
    integer signed req_size_2_i;
    integer signed max_size_3_i;
    integer signed max_p_error_3_i;
    integer signed midpoint_3_i;
    integer signed residual_3_i;
    integer signed req_size_3_i;
    always_comb begin
        total_size_i = 0;
        log_err_p_mode_i = 0;
        log_err_ich_mode_i = 0;
        bits_ich_mode_i = (prev_ich_selected != 0) ? 1 : (alt_size_to_generate - adj_predicted_size);
        bits_ich_mode_i = bits_ich_mode_i + 5 * ich_indices_in_group;
        max_size_0_i = 0;
        midpoint_0_i = 0;
        max_p_error_0_i = 0;
        qlevel_new_i = qlevel_for_i(unit_c_type_0, qlevel_luma_primary, qlevel_chroma_primary);
        bit_depth_i = depth_for_i(unit_c_type_0);
        residual_0_i = $signed(quantized_residual_0_0);
        req_size_0_i = residual_size_i(residual_0_i);
        if (req_size_0_i > max_size_0_i) max_size_0_i = req_size_0_i;
        residual_0_i = $signed(quantized_residual_0_1);
        req_size_0_i = residual_size_i(residual_0_i);
        if (req_size_0_i > max_size_0_i) max_size_0_i = req_size_0_i;
        residual_0_i = $signed(quantized_residual_0_2);
        req_size_0_i = residual_size_i(residual_0_i);
        if (req_size_0_i > max_size_0_i) max_size_0_i = req_size_0_i;
        if (max_size_0_i >= (bit_depth_i - qlevel_new_i)) midpoint_0_i = 1;
        max_p_error_0_i = (midpoint_0_i != 0) ? max_mid_error_0 : max_error_0;
        max_size_1_i = 0;
        midpoint_1_i = 0;
        max_p_error_1_i = 0;
        qlevel_new_i = qlevel_for_i(unit_c_type_1, qlevel_luma_primary, qlevel_chroma_primary);
        bit_depth_i = depth_for_i(unit_c_type_1);
        residual_1_i = $signed(quantized_residual_1_0);
        req_size_1_i = residual_size_i(residual_1_i);
        if (req_size_1_i > max_size_1_i) max_size_1_i = req_size_1_i;
        residual_1_i = $signed(quantized_residual_1_1);
        req_size_1_i = residual_size_i(residual_1_i);
        if (req_size_1_i > max_size_1_i) max_size_1_i = req_size_1_i;
        residual_1_i = $signed(quantized_residual_1_2);
        req_size_1_i = residual_size_i(residual_1_i);
        if (req_size_1_i > max_size_1_i) max_size_1_i = req_size_1_i;
        if (max_size_1_i >= (bit_depth_i - qlevel_new_i)) midpoint_1_i = 1;
        max_p_error_1_i = (midpoint_1_i != 0) ? max_mid_error_1 : max_error_1;
        max_size_2_i = 0;
        midpoint_2_i = 0;
        max_p_error_2_i = 0;
        qlevel_new_i = qlevel_for_i(unit_c_type_2, qlevel_luma_primary, qlevel_chroma_primary);
        bit_depth_i = depth_for_i(unit_c_type_2);
        residual_2_i = $signed(quantized_residual_2_0);
        req_size_2_i = residual_size_i(residual_2_i);
        if (req_size_2_i > max_size_2_i) max_size_2_i = req_size_2_i;
        residual_2_i = $signed(quantized_residual_2_1);
        req_size_2_i = residual_size_i(residual_2_i);
        if (req_size_2_i > max_size_2_i) max_size_2_i = req_size_2_i;
        residual_2_i = $signed(quantized_residual_2_2);
        req_size_2_i = residual_size_i(residual_2_i);
        if (req_size_2_i > max_size_2_i) max_size_2_i = req_size_2_i;
        if (max_size_2_i >= (bit_depth_i - qlevel_new_i)) midpoint_2_i = 1;
        max_p_error_2_i = (midpoint_2_i != 0) ? max_mid_error_2 : max_error_2;
        max_size_3_i = 0;
        midpoint_3_i = 0;
        max_p_error_3_i = 0;
        qlevel_new_i = qlevel_for_i(unit_c_type_3, qlevel_luma_primary, qlevel_chroma_primary);
        bit_depth_i = depth_for_i(unit_c_type_3);
        residual_3_i = $signed(quantized_residual_3_0);
        req_size_3_i = residual_size_i(residual_3_i);
        if (req_size_3_i > max_size_3_i) max_size_3_i = req_size_3_i;
        residual_3_i = $signed(quantized_residual_3_1);
        req_size_3_i = residual_size_i(residual_3_i);
        if (req_size_3_i > max_size_3_i) max_size_3_i = req_size_3_i;
        residual_3_i = $signed(quantized_residual_3_2);
        req_size_3_i = residual_size_i(residual_3_i);
        if (req_size_3_i > max_size_3_i) max_size_3_i = req_size_3_i;
        if (max_size_3_i >= (bit_depth_i - qlevel_new_i)) midpoint_3_i = 1;
        max_p_error_3_i = (midpoint_3_i != 0) ? max_mid_error_3 : max_error_3;
        if (units_per_group > 0) begin
            max_size_0_i = 0;
            residual_0_i = $signed(quantized_residual_0_0);
            req_size_0_i = residual_size_i(residual_0_i);
            sample_hpos_i = hPos + 0 - (pixels_in_group - 1) + unit_start_h_pos_0;
            if ((sample_hpos_i < slice_width) && (req_size_0_i > max_size_0_i)) max_size_0_i = req_size_0_i;
            residual_0_i = $signed(quantized_residual_0_1);
            req_size_0_i = residual_size_i(residual_0_i);
            sample_hpos_i = hPos + 1 - (pixels_in_group - 1) + unit_start_h_pos_0;
            if ((sample_hpos_i < slice_width) && (req_size_0_i > max_size_0_i)) max_size_0_i = req_size_0_i;
            residual_0_i = $signed(quantized_residual_0_2);
            req_size_0_i = residual_size_i(residual_0_i);
            sample_hpos_i = hPos + 2 - (pixels_in_group - 1) + unit_start_h_pos_0;
            if ((sample_hpos_i < slice_width) && (req_size_0_i > max_size_0_i)) max_size_0_i = req_size_0_i;
        qlevel_new_i = qlevel_for_i(unit_c_type_0, qlevel_luma_primary, qlevel_chroma_primary);
            bit_depth_i = depth_for_i(unit_c_type_0);
            max_residual_size_i = bit_depth_i - qlevel_new_i;
            if (max_size_0_i > max_residual_size_i) max_size_0_i = max_residual_size_i;
        qlevel_old_i = qlevel_for_i(unit_c_type_0, qlevel_luma_previous, qlevel_chroma_previous);
            pred_size_i = predicted_size_0 + qlevel_old_i - qlevel_new_i;
            if (pred_size_i < 0) pred_size_i = 0;
            else if (pred_size_i > (max_residual_size_i - 1)) pred_size_i = max_residual_size_i - 1;
            if (max_size_0_i < pred_size_i)
                total_size_i = total_size_i + 1 + 3 * pred_size_i;
            else if ((max_size_0_i == max_residual_size_i) && (0 != 0))
                total_size_i = total_size_i + (max_size_0_i - pred_size_i) + 3 * max_size_0_i;
            else
                total_size_i = total_size_i + 1 + (max_size_0_i - pred_size_i) + 3 * max_size_0_i;
        end
        if (units_per_group > 1) begin
            max_size_1_i = 0;
            residual_1_i = $signed(quantized_residual_1_0);
            req_size_1_i = residual_size_i(residual_1_i);
            sample_hpos_i = hPos + 0 - (pixels_in_group - 1) + unit_start_h_pos_1;
            if ((sample_hpos_i < slice_width) && (req_size_1_i > max_size_1_i)) max_size_1_i = req_size_1_i;
            residual_1_i = $signed(quantized_residual_1_1);
            req_size_1_i = residual_size_i(residual_1_i);
            sample_hpos_i = hPos + 1 - (pixels_in_group - 1) + unit_start_h_pos_1;
            if ((sample_hpos_i < slice_width) && (req_size_1_i > max_size_1_i)) max_size_1_i = req_size_1_i;
            residual_1_i = $signed(quantized_residual_1_2);
            req_size_1_i = residual_size_i(residual_1_i);
            sample_hpos_i = hPos + 2 - (pixels_in_group - 1) + unit_start_h_pos_1;
            if ((sample_hpos_i < slice_width) && (req_size_1_i > max_size_1_i)) max_size_1_i = req_size_1_i;
        qlevel_new_i = qlevel_for_i(unit_c_type_1, qlevel_luma_primary, qlevel_chroma_primary);
            bit_depth_i = depth_for_i(unit_c_type_1);
            max_residual_size_i = bit_depth_i - qlevel_new_i;
            if (max_size_1_i > max_residual_size_i) max_size_1_i = max_residual_size_i;
        qlevel_old_i = qlevel_for_i(unit_c_type_1, qlevel_luma_previous, qlevel_chroma_previous);
            pred_size_i = predicted_size_1 + qlevel_old_i - qlevel_new_i;
            if (pred_size_i < 0) pred_size_i = 0;
            else if (pred_size_i > (max_residual_size_i - 1)) pred_size_i = max_residual_size_i - 1;
            if (max_size_1_i < pred_size_i)
                total_size_i = total_size_i + 1 + 3 * pred_size_i;
            else if ((max_size_1_i == max_residual_size_i) && (1 != 0))
                total_size_i = total_size_i + (max_size_1_i - pred_size_i) + 3 * max_size_1_i;
            else
                total_size_i = total_size_i + 1 + (max_size_1_i - pred_size_i) + 3 * max_size_1_i;
        end
        if (units_per_group > 2) begin
            max_size_2_i = 0;
            residual_2_i = $signed(quantized_residual_2_0);
            req_size_2_i = residual_size_i(residual_2_i);
            sample_hpos_i = hPos + 0 - (pixels_in_group - 1) + unit_start_h_pos_2;
            if ((sample_hpos_i < slice_width) && (req_size_2_i > max_size_2_i)) max_size_2_i = req_size_2_i;
            residual_2_i = $signed(quantized_residual_2_1);
            req_size_2_i = residual_size_i(residual_2_i);
            sample_hpos_i = hPos + 1 - (pixels_in_group - 1) + unit_start_h_pos_2;
            if ((sample_hpos_i < slice_width) && (req_size_2_i > max_size_2_i)) max_size_2_i = req_size_2_i;
            residual_2_i = $signed(quantized_residual_2_2);
            req_size_2_i = residual_size_i(residual_2_i);
            sample_hpos_i = hPos + 2 - (pixels_in_group - 1) + unit_start_h_pos_2;
            if ((sample_hpos_i < slice_width) && (req_size_2_i > max_size_2_i)) max_size_2_i = req_size_2_i;
        qlevel_new_i = qlevel_for_i(unit_c_type_2, qlevel_luma_primary, qlevel_chroma_primary);
            bit_depth_i = depth_for_i(unit_c_type_2);
            max_residual_size_i = bit_depth_i - qlevel_new_i;
            if (max_size_2_i > max_residual_size_i) max_size_2_i = max_residual_size_i;
        qlevel_old_i = qlevel_for_i(unit_c_type_2, qlevel_luma_previous, qlevel_chroma_previous);
            pred_size_i = predicted_size_2 + qlevel_old_i - qlevel_new_i;
            if (pred_size_i < 0) pred_size_i = 0;
            else if (pred_size_i > (max_residual_size_i - 1)) pred_size_i = max_residual_size_i - 1;
            if (max_size_2_i < pred_size_i)
                total_size_i = total_size_i + 1 + 3 * pred_size_i;
            else if ((max_size_2_i == max_residual_size_i) && (2 != 0))
                total_size_i = total_size_i + (max_size_2_i - pred_size_i) + 3 * max_size_2_i;
            else
                total_size_i = total_size_i + 1 + (max_size_2_i - pred_size_i) + 3 * max_size_2_i;
        end
        if (units_per_group > 3) begin
            max_size_3_i = 0;
            residual_3_i = $signed(quantized_residual_3_0);
            req_size_3_i = residual_size_i(residual_3_i);
            sample_hpos_i = hPos + 0 - (pixels_in_group - 1) + unit_start_h_pos_3;
            if ((sample_hpos_i < slice_width) && (req_size_3_i > max_size_3_i)) max_size_3_i = req_size_3_i;
            residual_3_i = $signed(quantized_residual_3_1);
            req_size_3_i = residual_size_i(residual_3_i);
            sample_hpos_i = hPos + 1 - (pixels_in_group - 1) + unit_start_h_pos_3;
            if ((sample_hpos_i < slice_width) && (req_size_3_i > max_size_3_i)) max_size_3_i = req_size_3_i;
            residual_3_i = $signed(quantized_residual_3_2);
            req_size_3_i = residual_size_i(residual_3_i);
            sample_hpos_i = hPos + 2 - (pixels_in_group - 1) + unit_start_h_pos_3;
            if ((sample_hpos_i < slice_width) && (req_size_3_i > max_size_3_i)) max_size_3_i = req_size_3_i;
        qlevel_new_i = qlevel_for_i(unit_c_type_3, qlevel_luma_primary, qlevel_chroma_primary);
            bit_depth_i = depth_for_i(unit_c_type_3);
            max_residual_size_i = bit_depth_i - qlevel_new_i;
            if (max_size_3_i > max_residual_size_i) max_size_3_i = max_residual_size_i;
        qlevel_old_i = qlevel_for_i(unit_c_type_3, qlevel_luma_previous, qlevel_chroma_previous);
            pred_size_i = predicted_size_3 + qlevel_old_i - qlevel_new_i;
            if (pred_size_i < 0) pred_size_i = 0;
            else if (pred_size_i > (max_residual_size_i - 1)) pred_size_i = max_residual_size_i - 1;
            if (max_size_3_i < pred_size_i)
                total_size_i = total_size_i + 1 + 3 * pred_size_i;
            else if ((max_size_3_i == max_residual_size_i) && (3 != 0))
                total_size_i = total_size_i + (max_size_3_i - pred_size_i) + 3 * max_size_3_i;
            else
                total_size_i = total_size_i + 1 + (max_size_3_i - pred_size_i) + 3 * max_size_3_i;
        end
        qlevel_new_i = qlevel_luma_primary;
        max_residual_size_i = cpnt_bit_depth_0 - qlevel_new_i;
        if ((max_size_0_i < max_residual_size_i) && (prev_ich_selected != 0)) total_size_i = total_size_i + 1;
        bits_p_mode_i = total_size_i;
        if (units_per_group > 0) begin
            log_err_p_mode_i = log_err_p_mode_i + ceil_log2_i(max_p_error_0_i);
            log_err_ich_mode_i = log_err_ich_mode_i + ceil_log2_i(max_ich_error_0);
            if ((dsc_version_minor == 1) && (0 == 0)) begin
                log_err_p_mode_i = log_err_p_mode_i + ceil_log2_i(max_p_error_0_i);
                log_err_ich_mode_i = log_err_ich_mode_i + ceil_log2_i(max_ich_error_0);
            end
        end
        if (units_per_group > 1) begin
            log_err_p_mode_i = log_err_p_mode_i + ceil_log2_i(max_p_error_1_i);
            log_err_ich_mode_i = log_err_ich_mode_i + ceil_log2_i(max_ich_error_1);
            if ((dsc_version_minor == 1) && (1 == 0)) begin
                log_err_p_mode_i = log_err_p_mode_i + ceil_log2_i(max_p_error_1_i);
                log_err_ich_mode_i = log_err_ich_mode_i + ceil_log2_i(max_ich_error_1);
            end
        end
        if (units_per_group > 2) begin
            log_err_p_mode_i = log_err_p_mode_i + ceil_log2_i(max_p_error_2_i);
            log_err_ich_mode_i = log_err_ich_mode_i + ceil_log2_i(max_ich_error_2);
            if ((dsc_version_minor == 1) && (2 == 0)) begin
                log_err_p_mode_i = log_err_p_mode_i + ceil_log2_i(max_p_error_2_i);
                log_err_ich_mode_i = log_err_ich_mode_i + ceil_log2_i(max_ich_error_2);
            end
        end
        if (units_per_group > 3) begin
            log_err_p_mode_i = log_err_p_mode_i + ceil_log2_i(max_p_error_3_i);
            log_err_ich_mode_i = log_err_ich_mode_i + ceil_log2_i(max_ich_error_3);
            if ((dsc_version_minor == 1) && (3 == 0)) begin
                log_err_p_mode_i = log_err_p_mode_i + ceil_log2_i(max_p_error_3_i);
                log_err_ich_mode_i = log_err_ich_mode_i + ceil_log2_i(max_ich_error_3);
            end
        end
        p_mode_cost_i = bits_p_mode_i + 4 * log_err_p_mode_i;
        ich_mode_cost_i = bits_ich_mode_i + 4 * log_err_ich_mode_i;
        first_somewhat_i = 1;
        first_very_i = 1;
        second_somewhat_i = 1;
        second_very_i = 1;
        qlevel_flat_i = qlevel_for_i(0, qlevel_luma_flat, qlevel_chroma_flat);
        qlevel_flat_i = qlevel_for_i(0, qlevel_luma_flat, qlevel_chroma_flat);
        if (num_components > 0) begin
            if (spread4_i(0) > max_i(flatness_det_thresh, quant_divisor_i(qlevel_flat_i))) first_somewhat_i = 0;
            if (spread4_i(0) > flatness_det_thresh) first_very_i = 0;
            if (spread6_i(0) > max_i(flatness_det_thresh, quant_divisor_i(qlevel_flat_i))) second_somewhat_i = 0;
            if (spread6_i(0) > flatness_det_thresh) second_very_i = 0;
        end
        qlevel_flat_i = qlevel_for_i(1, qlevel_luma_flat, qlevel_chroma_flat);
        if (num_components > 1) begin
            if (spread4_i(1) > max_i(flatness_det_thresh, quant_divisor_i(qlevel_flat_i))) first_somewhat_i = 0;
            if (spread4_i(1) > flatness_det_thresh) first_very_i = 0;
            if (spread6_i(1) > max_i(flatness_det_thresh, quant_divisor_i(qlevel_flat_i))) second_somewhat_i = 0;
            if (spread6_i(1) > flatness_det_thresh) second_very_i = 0;
        end
        qlevel_flat_i = qlevel_for_i(2, qlevel_luma_flat, qlevel_chroma_flat);
        if (num_components > 2) begin
            if (spread4_i(2) > max_i(flatness_det_thresh, quant_divisor_i(qlevel_flat_i))) first_somewhat_i = 0;
            if (spread4_i(2) > flatness_det_thresh) first_very_i = 0;
            if (spread6_i(2) > max_i(flatness_det_thresh, quant_divisor_i(qlevel_flat_i))) second_somewhat_i = 0;
            if (spread6_i(2) > flatness_det_thresh) second_very_i = 0;
        end
        qlevel_flat_i = qlevel_for_i(3, qlevel_luma_flat, qlevel_chroma_flat);
        if (num_components > 3) begin
            if (spread4_i(3) > max_i(flatness_det_thresh, quant_divisor_i(qlevel_flat_i))) first_somewhat_i = 0;
            if (spread4_i(3) > flatness_det_thresh) first_very_i = 0;
            if (spread6_i(3) > max_i(flatness_det_thresh, quant_divisor_i(qlevel_flat_i))) second_somewhat_i = 0;
            if (spread6_i(3) > flatness_det_thresh) second_very_i = 0;
        end
        flat_index_i = 0;
        if (hPos + 1 < slice_width) begin
            if (first_very_i != 0) flat_index_i = 2;
            else if (first_somewhat_i != 0) flat_index_i = 1;
            else if (hPos + 2 < slice_width) begin
                if (second_very_i != 0) flat_index_i = 2;
                else if (second_somewhat_i != 0) flat_index_i = 1;
            end
        end
        if (dsc_version_minor == 2) begin
            if (flat_index_i == 2) return_value = ((log_err_ich_mode_i <= log_err_p_mode_i) && (ich_mode_cost_i < p_mode_cost_i)) ? 1 : 0;
            else return_value = (ich_mode_cost_i < p_mode_cost_i) ? 1 : 0;
        end else return_value = ((log_err_ich_mode_i <= log_err_p_mode_i) && (ich_mode_cost_i < p_mode_cost_i)) ? 1 : 0;
        return_value = return_value + 1;
    end
endmodule
