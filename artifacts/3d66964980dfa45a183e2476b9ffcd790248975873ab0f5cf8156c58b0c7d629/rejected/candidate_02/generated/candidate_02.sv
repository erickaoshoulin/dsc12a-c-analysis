module estimatebitsforgroup_candidate_02 (
    input logic [1:0] dsc_version_minor,
    input logic native_420,
    input logic [2:0] units_per_group,
    input logic [1:0] pixels_in_group,
    input logic [15:0] hPos,
    input logic [15:0] slice_width,
    input logic prev_ich_selected,
    input logic [4:0] primary_qp,
    input logic [4:0] prev_primary_qp,
    input logic [4:0] cpntBitDepth_0,
    input logic [4:0] cpntBitDepth_1,
    input logic [4:0] cpntBitDepth_2,
    input logic [4:0] cpntBitDepth_3,
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
    input logic [4:0] qlevel_luma_new,
    input logic [4:0] qlevel_luma_old,
    input logic [4:0] qlevel_chroma_new,
    input logic [4:0] qlevel_chroma_old,
    output logic [8:0] return_value
);
    integer signed total_size_i;
    integer signed bit_depth_i;
    integer signed qlevel_new_i;
    integer signed qlevel_old_i;
    integer signed max_residual_size_i;
    integer signed pred_size_i;
    integer signed hpos_value_i;
    integer signed pixels_in_group_value_i;
    integer signed slice_width_value_i;
    integer signed unit_start_h_pos_value_i;
    integer signed max_size_0_i;
    integer signed sample_hpos_0_i;
    integer signed residual_0_i;
    integer signed req_size_0_i;
    integer signed max_size_1_i;
    integer signed sample_hpos_1_i;
    integer signed residual_1_i;
    integer signed req_size_1_i;
    integer signed max_size_2_i;
    integer signed sample_hpos_2_i;
    integer signed residual_2_i;
    integer signed req_size_2_i;
    integer signed max_size_3_i;
    integer signed sample_hpos_3_i;
    integer signed residual_3_i;
    integer signed req_size_3_i;
    always_comb begin
        total_size_i = 0;
        hpos_value_i = hPos;
        pixels_in_group_value_i = pixels_in_group;
        slice_width_value_i = slice_width;
        max_size_0_i = 0;
        unit_start_h_pos_value_i = unit_start_h_pos_0;
            sample_hpos_0_i = hpos_value_i + 0 - (pixels_in_group_value_i - 1) + unit_start_h_pos_value_i;
            residual_0_i = $signed(quantized_residual_0_0);
            req_size_0_i = 0;
            if (residual_0_i == 0) req_size_0_i = 0;
            else if ((residual_0_i >= 32'shffffffff) && (residual_0_i <= 0)) req_size_0_i = 1;
            else if ((residual_0_i >= 32'shfffffffe) && (residual_0_i <= 1)) req_size_0_i = 2;
            else if ((residual_0_i >= 32'shfffffffc) && (residual_0_i <= 3)) req_size_0_i = 3;
            else if ((residual_0_i >= 32'shfffffff8) && (residual_0_i <= 7)) req_size_0_i = 4;
            else if ((residual_0_i >= 32'shfffffff0) && (residual_0_i <= 15)) req_size_0_i = 5;
            else if ((residual_0_i >= 32'shffffffe0) && (residual_0_i <= 31)) req_size_0_i = 6;
            else if ((residual_0_i >= 32'shffffffc0) && (residual_0_i <= 63)) req_size_0_i = 7;
            else if ((residual_0_i >= 32'shffffff80) && (residual_0_i <= 127)) req_size_0_i = 8;
            else if ((residual_0_i >= 32'shffffff00) && (residual_0_i <= 255)) req_size_0_i = 9;
            else if ((residual_0_i >= 32'shfffffe00) && (residual_0_i <= 511)) req_size_0_i = 10;
            else if ((residual_0_i >= 32'shfffffc00) && (residual_0_i <= 1023)) req_size_0_i = 11;
            else if ((residual_0_i >= 32'shfffff800) && (residual_0_i <= 2047)) req_size_0_i = 12;
            else if ((residual_0_i >= 32'shfffff000) && (residual_0_i <= 4095)) req_size_0_i = 13;
            else if ((residual_0_i >= 32'shffffe000) && (residual_0_i <= 8191)) req_size_0_i = 14;
            else if ((residual_0_i >= 32'shffffc000) && (residual_0_i <= 16383)) req_size_0_i = 15;
            else if ((residual_0_i >= 32'shffff8000) && (residual_0_i <= 32767)) req_size_0_i = 16;
            else if ((residual_0_i >= 32'shffff0000) && (residual_0_i <= 65535)) req_size_0_i = 17;
            else if ((residual_0_i >= 32'shfffdfd8a) && (residual_0_i <= 131701)) req_size_0_i = 18;
            if (sample_hpos_0_i < slice_width_value_i) begin
                if (req_size_0_i > max_size_0_i) max_size_0_i = req_size_0_i;
            end
            sample_hpos_0_i = hpos_value_i + 1 - (pixels_in_group_value_i - 1) + unit_start_h_pos_value_i;
            residual_0_i = $signed(quantized_residual_0_1);
            req_size_0_i = 0;
            if (residual_0_i == 0) req_size_0_i = 0;
            else if ((residual_0_i >= 32'shffffffff) && (residual_0_i <= 0)) req_size_0_i = 1;
            else if ((residual_0_i >= 32'shfffffffe) && (residual_0_i <= 1)) req_size_0_i = 2;
            else if ((residual_0_i >= 32'shfffffffc) && (residual_0_i <= 3)) req_size_0_i = 3;
            else if ((residual_0_i >= 32'shfffffff8) && (residual_0_i <= 7)) req_size_0_i = 4;
            else if ((residual_0_i >= 32'shfffffff0) && (residual_0_i <= 15)) req_size_0_i = 5;
            else if ((residual_0_i >= 32'shffffffe0) && (residual_0_i <= 31)) req_size_0_i = 6;
            else if ((residual_0_i >= 32'shffffffc0) && (residual_0_i <= 63)) req_size_0_i = 7;
            else if ((residual_0_i >= 32'shffffff80) && (residual_0_i <= 127)) req_size_0_i = 8;
            else if ((residual_0_i >= 32'shffffff00) && (residual_0_i <= 255)) req_size_0_i = 9;
            else if ((residual_0_i >= 32'shfffffe00) && (residual_0_i <= 511)) req_size_0_i = 10;
            else if ((residual_0_i >= 32'shfffffc00) && (residual_0_i <= 1023)) req_size_0_i = 11;
            else if ((residual_0_i >= 32'shfffff800) && (residual_0_i <= 2047)) req_size_0_i = 12;
            else if ((residual_0_i >= 32'shfffff000) && (residual_0_i <= 4095)) req_size_0_i = 13;
            else if ((residual_0_i >= 32'shffffe000) && (residual_0_i <= 8191)) req_size_0_i = 14;
            else if ((residual_0_i >= 32'shffffc000) && (residual_0_i <= 16383)) req_size_0_i = 15;
            else if ((residual_0_i >= 32'shffff8000) && (residual_0_i <= 32767)) req_size_0_i = 16;
            else if ((residual_0_i >= 32'shffff0000) && (residual_0_i <= 65535)) req_size_0_i = 17;
            else if ((residual_0_i >= 32'shfffdfd8a) && (residual_0_i <= 131701)) req_size_0_i = 18;
            if (sample_hpos_0_i < slice_width_value_i) begin
                if (req_size_0_i > max_size_0_i) max_size_0_i = req_size_0_i;
            end
            sample_hpos_0_i = hpos_value_i + 2 - (pixels_in_group_value_i - 1) + unit_start_h_pos_value_i;
            residual_0_i = $signed(quantized_residual_0_2);
            req_size_0_i = 0;
            if (residual_0_i == 0) req_size_0_i = 0;
            else if ((residual_0_i >= 32'shffffffff) && (residual_0_i <= 0)) req_size_0_i = 1;
            else if ((residual_0_i >= 32'shfffffffe) && (residual_0_i <= 1)) req_size_0_i = 2;
            else if ((residual_0_i >= 32'shfffffffc) && (residual_0_i <= 3)) req_size_0_i = 3;
            else if ((residual_0_i >= 32'shfffffff8) && (residual_0_i <= 7)) req_size_0_i = 4;
            else if ((residual_0_i >= 32'shfffffff0) && (residual_0_i <= 15)) req_size_0_i = 5;
            else if ((residual_0_i >= 32'shffffffe0) && (residual_0_i <= 31)) req_size_0_i = 6;
            else if ((residual_0_i >= 32'shffffffc0) && (residual_0_i <= 63)) req_size_0_i = 7;
            else if ((residual_0_i >= 32'shffffff80) && (residual_0_i <= 127)) req_size_0_i = 8;
            else if ((residual_0_i >= 32'shffffff00) && (residual_0_i <= 255)) req_size_0_i = 9;
            else if ((residual_0_i >= 32'shfffffe00) && (residual_0_i <= 511)) req_size_0_i = 10;
            else if ((residual_0_i >= 32'shfffffc00) && (residual_0_i <= 1023)) req_size_0_i = 11;
            else if ((residual_0_i >= 32'shfffff800) && (residual_0_i <= 2047)) req_size_0_i = 12;
            else if ((residual_0_i >= 32'shfffff000) && (residual_0_i <= 4095)) req_size_0_i = 13;
            else if ((residual_0_i >= 32'shffffe000) && (residual_0_i <= 8191)) req_size_0_i = 14;
            else if ((residual_0_i >= 32'shffffc000) && (residual_0_i <= 16383)) req_size_0_i = 15;
            else if ((residual_0_i >= 32'shffff8000) && (residual_0_i <= 32767)) req_size_0_i = 16;
            else if ((residual_0_i >= 32'shffff0000) && (residual_0_i <= 65535)) req_size_0_i = 17;
            else if ((residual_0_i >= 32'shfffdfd8a) && (residual_0_i <= 131701)) req_size_0_i = 18;
            if (sample_hpos_0_i < slice_width_value_i) begin
                if (req_size_0_i > max_size_0_i) max_size_0_i = req_size_0_i;
            end
            case (unit_c_type_0)
                0: bit_depth_i = cpntBitDepth_0;
                1: bit_depth_i = cpntBitDepth_1;
                2: bit_depth_i = cpntBitDepth_2;
                3: bit_depth_i = cpntBitDepth_3;
                default: bit_depth_i = cpntBitDepth_0;
            endcase
        if ((unit_c_type_0 % 3) == 0) begin
            qlevel_new_i = qlevel_luma_new;
        end else if ((native_420 != 0) && (unit_c_type_0 == 1)) begin
            qlevel_new_i = qlevel_luma_new;
        end else begin
            qlevel_new_i = qlevel_chroma_new;
            if ((dsc_version_minor == 2) && (cpntBitDepth_0 == cpntBitDepth_1) && (qlevel_new_i > 0)) begin
                qlevel_new_i = qlevel_new_i - 1;
            end
        end
            max_residual_size_i = bit_depth_i - qlevel_new_i;
            if (max_size_0_i > max_residual_size_i) max_size_0_i = max_residual_size_i;
        max_size_1_i = 0;
        unit_start_h_pos_value_i = unit_start_h_pos_1;
            sample_hpos_1_i = hpos_value_i + 0 - (pixels_in_group_value_i - 1) + unit_start_h_pos_value_i;
            residual_1_i = $signed(quantized_residual_1_0);
            req_size_1_i = 0;
            if (residual_1_i == 0) req_size_1_i = 0;
            else if ((residual_1_i >= 32'shffffffff) && (residual_1_i <= 0)) req_size_1_i = 1;
            else if ((residual_1_i >= 32'shfffffffe) && (residual_1_i <= 1)) req_size_1_i = 2;
            else if ((residual_1_i >= 32'shfffffffc) && (residual_1_i <= 3)) req_size_1_i = 3;
            else if ((residual_1_i >= 32'shfffffff8) && (residual_1_i <= 7)) req_size_1_i = 4;
            else if ((residual_1_i >= 32'shfffffff0) && (residual_1_i <= 15)) req_size_1_i = 5;
            else if ((residual_1_i >= 32'shffffffe0) && (residual_1_i <= 31)) req_size_1_i = 6;
            else if ((residual_1_i >= 32'shffffffc0) && (residual_1_i <= 63)) req_size_1_i = 7;
            else if ((residual_1_i >= 32'shffffff80) && (residual_1_i <= 127)) req_size_1_i = 8;
            else if ((residual_1_i >= 32'shffffff00) && (residual_1_i <= 255)) req_size_1_i = 9;
            else if ((residual_1_i >= 32'shfffffe00) && (residual_1_i <= 511)) req_size_1_i = 10;
            else if ((residual_1_i >= 32'shfffffc00) && (residual_1_i <= 1023)) req_size_1_i = 11;
            else if ((residual_1_i >= 32'shfffff800) && (residual_1_i <= 2047)) req_size_1_i = 12;
            else if ((residual_1_i >= 32'shfffff000) && (residual_1_i <= 4095)) req_size_1_i = 13;
            else if ((residual_1_i >= 32'shffffe000) && (residual_1_i <= 8191)) req_size_1_i = 14;
            else if ((residual_1_i >= 32'shffffc000) && (residual_1_i <= 16383)) req_size_1_i = 15;
            else if ((residual_1_i >= 32'shffff8000) && (residual_1_i <= 32767)) req_size_1_i = 16;
            else if ((residual_1_i >= 32'shffff0000) && (residual_1_i <= 65535)) req_size_1_i = 17;
            else if ((residual_1_i >= 32'shfffdfd8a) && (residual_1_i <= 131701)) req_size_1_i = 18;
            if (sample_hpos_1_i < slice_width_value_i) begin
                if (req_size_1_i > max_size_1_i) max_size_1_i = req_size_1_i;
            end
            sample_hpos_1_i = hpos_value_i + 1 - (pixels_in_group_value_i - 1) + unit_start_h_pos_value_i;
            residual_1_i = $signed(quantized_residual_1_1);
            req_size_1_i = 0;
            if (residual_1_i == 0) req_size_1_i = 0;
            else if ((residual_1_i >= 32'shffffffff) && (residual_1_i <= 0)) req_size_1_i = 1;
            else if ((residual_1_i >= 32'shfffffffe) && (residual_1_i <= 1)) req_size_1_i = 2;
            else if ((residual_1_i >= 32'shfffffffc) && (residual_1_i <= 3)) req_size_1_i = 3;
            else if ((residual_1_i >= 32'shfffffff8) && (residual_1_i <= 7)) req_size_1_i = 4;
            else if ((residual_1_i >= 32'shfffffff0) && (residual_1_i <= 15)) req_size_1_i = 5;
            else if ((residual_1_i >= 32'shffffffe0) && (residual_1_i <= 31)) req_size_1_i = 6;
            else if ((residual_1_i >= 32'shffffffc0) && (residual_1_i <= 63)) req_size_1_i = 7;
            else if ((residual_1_i >= 32'shffffff80) && (residual_1_i <= 127)) req_size_1_i = 8;
            else if ((residual_1_i >= 32'shffffff00) && (residual_1_i <= 255)) req_size_1_i = 9;
            else if ((residual_1_i >= 32'shfffffe00) && (residual_1_i <= 511)) req_size_1_i = 10;
            else if ((residual_1_i >= 32'shfffffc00) && (residual_1_i <= 1023)) req_size_1_i = 11;
            else if ((residual_1_i >= 32'shfffff800) && (residual_1_i <= 2047)) req_size_1_i = 12;
            else if ((residual_1_i >= 32'shfffff000) && (residual_1_i <= 4095)) req_size_1_i = 13;
            else if ((residual_1_i >= 32'shffffe000) && (residual_1_i <= 8191)) req_size_1_i = 14;
            else if ((residual_1_i >= 32'shffffc000) && (residual_1_i <= 16383)) req_size_1_i = 15;
            else if ((residual_1_i >= 32'shffff8000) && (residual_1_i <= 32767)) req_size_1_i = 16;
            else if ((residual_1_i >= 32'shffff0000) && (residual_1_i <= 65535)) req_size_1_i = 17;
            else if ((residual_1_i >= 32'shfffdfd8a) && (residual_1_i <= 131701)) req_size_1_i = 18;
            if (sample_hpos_1_i < slice_width_value_i) begin
                if (req_size_1_i > max_size_1_i) max_size_1_i = req_size_1_i;
            end
            sample_hpos_1_i = hpos_value_i + 2 - (pixels_in_group_value_i - 1) + unit_start_h_pos_value_i;
            residual_1_i = $signed(quantized_residual_1_2);
            req_size_1_i = 0;
            if (residual_1_i == 0) req_size_1_i = 0;
            else if ((residual_1_i >= 32'shffffffff) && (residual_1_i <= 0)) req_size_1_i = 1;
            else if ((residual_1_i >= 32'shfffffffe) && (residual_1_i <= 1)) req_size_1_i = 2;
            else if ((residual_1_i >= 32'shfffffffc) && (residual_1_i <= 3)) req_size_1_i = 3;
            else if ((residual_1_i >= 32'shfffffff8) && (residual_1_i <= 7)) req_size_1_i = 4;
            else if ((residual_1_i >= 32'shfffffff0) && (residual_1_i <= 15)) req_size_1_i = 5;
            else if ((residual_1_i >= 32'shffffffe0) && (residual_1_i <= 31)) req_size_1_i = 6;
            else if ((residual_1_i >= 32'shffffffc0) && (residual_1_i <= 63)) req_size_1_i = 7;
            else if ((residual_1_i >= 32'shffffff80) && (residual_1_i <= 127)) req_size_1_i = 8;
            else if ((residual_1_i >= 32'shffffff00) && (residual_1_i <= 255)) req_size_1_i = 9;
            else if ((residual_1_i >= 32'shfffffe00) && (residual_1_i <= 511)) req_size_1_i = 10;
            else if ((residual_1_i >= 32'shfffffc00) && (residual_1_i <= 1023)) req_size_1_i = 11;
            else if ((residual_1_i >= 32'shfffff800) && (residual_1_i <= 2047)) req_size_1_i = 12;
            else if ((residual_1_i >= 32'shfffff000) && (residual_1_i <= 4095)) req_size_1_i = 13;
            else if ((residual_1_i >= 32'shffffe000) && (residual_1_i <= 8191)) req_size_1_i = 14;
            else if ((residual_1_i >= 32'shffffc000) && (residual_1_i <= 16383)) req_size_1_i = 15;
            else if ((residual_1_i >= 32'shffff8000) && (residual_1_i <= 32767)) req_size_1_i = 16;
            else if ((residual_1_i >= 32'shffff0000) && (residual_1_i <= 65535)) req_size_1_i = 17;
            else if ((residual_1_i >= 32'shfffdfd8a) && (residual_1_i <= 131701)) req_size_1_i = 18;
            if (sample_hpos_1_i < slice_width_value_i) begin
                if (req_size_1_i > max_size_1_i) max_size_1_i = req_size_1_i;
            end
            case (unit_c_type_1)
                0: bit_depth_i = cpntBitDepth_0;
                1: bit_depth_i = cpntBitDepth_1;
                2: bit_depth_i = cpntBitDepth_2;
                3: bit_depth_i = cpntBitDepth_3;
                default: bit_depth_i = cpntBitDepth_0;
            endcase
        if ((unit_c_type_1 % 3) == 0) begin
            qlevel_new_i = qlevel_luma_new;
        end else if ((native_420 != 0) && (unit_c_type_1 == 1)) begin
            qlevel_new_i = qlevel_luma_new;
        end else begin
            qlevel_new_i = qlevel_chroma_new;
            if ((dsc_version_minor == 2) && (cpntBitDepth_0 == cpntBitDepth_1) && (qlevel_new_i > 0)) begin
                qlevel_new_i = qlevel_new_i - 1;
            end
        end
            max_residual_size_i = bit_depth_i - qlevel_new_i;
            if (max_size_1_i > max_residual_size_i) max_size_1_i = max_residual_size_i;
        max_size_2_i = 0;
        unit_start_h_pos_value_i = unit_start_h_pos_2;
            sample_hpos_2_i = hpos_value_i + 0 - (pixels_in_group_value_i - 1) + unit_start_h_pos_value_i;
            residual_2_i = $signed(quantized_residual_2_0);
            req_size_2_i = 0;
            if (residual_2_i == 0) req_size_2_i = 0;
            else if ((residual_2_i >= 32'shffffffff) && (residual_2_i <= 0)) req_size_2_i = 1;
            else if ((residual_2_i >= 32'shfffffffe) && (residual_2_i <= 1)) req_size_2_i = 2;
            else if ((residual_2_i >= 32'shfffffffc) && (residual_2_i <= 3)) req_size_2_i = 3;
            else if ((residual_2_i >= 32'shfffffff8) && (residual_2_i <= 7)) req_size_2_i = 4;
            else if ((residual_2_i >= 32'shfffffff0) && (residual_2_i <= 15)) req_size_2_i = 5;
            else if ((residual_2_i >= 32'shffffffe0) && (residual_2_i <= 31)) req_size_2_i = 6;
            else if ((residual_2_i >= 32'shffffffc0) && (residual_2_i <= 63)) req_size_2_i = 7;
            else if ((residual_2_i >= 32'shffffff80) && (residual_2_i <= 127)) req_size_2_i = 8;
            else if ((residual_2_i >= 32'shffffff00) && (residual_2_i <= 255)) req_size_2_i = 9;
            else if ((residual_2_i >= 32'shfffffe00) && (residual_2_i <= 511)) req_size_2_i = 10;
            else if ((residual_2_i >= 32'shfffffc00) && (residual_2_i <= 1023)) req_size_2_i = 11;
            else if ((residual_2_i >= 32'shfffff800) && (residual_2_i <= 2047)) req_size_2_i = 12;
            else if ((residual_2_i >= 32'shfffff000) && (residual_2_i <= 4095)) req_size_2_i = 13;
            else if ((residual_2_i >= 32'shffffe000) && (residual_2_i <= 8191)) req_size_2_i = 14;
            else if ((residual_2_i >= 32'shffffc000) && (residual_2_i <= 16383)) req_size_2_i = 15;
            else if ((residual_2_i >= 32'shffff8000) && (residual_2_i <= 32767)) req_size_2_i = 16;
            else if ((residual_2_i >= 32'shffff0000) && (residual_2_i <= 65535)) req_size_2_i = 17;
            else if ((residual_2_i >= 32'shfffdfd8a) && (residual_2_i <= 131701)) req_size_2_i = 18;
            if (sample_hpos_2_i < slice_width_value_i) begin
                if (req_size_2_i > max_size_2_i) max_size_2_i = req_size_2_i;
            end
            sample_hpos_2_i = hpos_value_i + 1 - (pixels_in_group_value_i - 1) + unit_start_h_pos_value_i;
            residual_2_i = $signed(quantized_residual_2_1);
            req_size_2_i = 0;
            if (residual_2_i == 0) req_size_2_i = 0;
            else if ((residual_2_i >= 32'shffffffff) && (residual_2_i <= 0)) req_size_2_i = 1;
            else if ((residual_2_i >= 32'shfffffffe) && (residual_2_i <= 1)) req_size_2_i = 2;
            else if ((residual_2_i >= 32'shfffffffc) && (residual_2_i <= 3)) req_size_2_i = 3;
            else if ((residual_2_i >= 32'shfffffff8) && (residual_2_i <= 7)) req_size_2_i = 4;
            else if ((residual_2_i >= 32'shfffffff0) && (residual_2_i <= 15)) req_size_2_i = 5;
            else if ((residual_2_i >= 32'shffffffe0) && (residual_2_i <= 31)) req_size_2_i = 6;
            else if ((residual_2_i >= 32'shffffffc0) && (residual_2_i <= 63)) req_size_2_i = 7;
            else if ((residual_2_i >= 32'shffffff80) && (residual_2_i <= 127)) req_size_2_i = 8;
            else if ((residual_2_i >= 32'shffffff00) && (residual_2_i <= 255)) req_size_2_i = 9;
            else if ((residual_2_i >= 32'shfffffe00) && (residual_2_i <= 511)) req_size_2_i = 10;
            else if ((residual_2_i >= 32'shfffffc00) && (residual_2_i <= 1023)) req_size_2_i = 11;
            else if ((residual_2_i >= 32'shfffff800) && (residual_2_i <= 2047)) req_size_2_i = 12;
            else if ((residual_2_i >= 32'shfffff000) && (residual_2_i <= 4095)) req_size_2_i = 13;
            else if ((residual_2_i >= 32'shffffe000) && (residual_2_i <= 8191)) req_size_2_i = 14;
            else if ((residual_2_i >= 32'shffffc000) && (residual_2_i <= 16383)) req_size_2_i = 15;
            else if ((residual_2_i >= 32'shffff8000) && (residual_2_i <= 32767)) req_size_2_i = 16;
            else if ((residual_2_i >= 32'shffff0000) && (residual_2_i <= 65535)) req_size_2_i = 17;
            else if ((residual_2_i >= 32'shfffdfd8a) && (residual_2_i <= 131701)) req_size_2_i = 18;
            if (sample_hpos_2_i < slice_width_value_i) begin
                if (req_size_2_i > max_size_2_i) max_size_2_i = req_size_2_i;
            end
            sample_hpos_2_i = hpos_value_i + 2 - (pixels_in_group_value_i - 1) + unit_start_h_pos_value_i;
            residual_2_i = $signed(quantized_residual_2_2);
            req_size_2_i = 0;
            if (residual_2_i == 0) req_size_2_i = 0;
            else if ((residual_2_i >= 32'shffffffff) && (residual_2_i <= 0)) req_size_2_i = 1;
            else if ((residual_2_i >= 32'shfffffffe) && (residual_2_i <= 1)) req_size_2_i = 2;
            else if ((residual_2_i >= 32'shfffffffc) && (residual_2_i <= 3)) req_size_2_i = 3;
            else if ((residual_2_i >= 32'shfffffff8) && (residual_2_i <= 7)) req_size_2_i = 4;
            else if ((residual_2_i >= 32'shfffffff0) && (residual_2_i <= 15)) req_size_2_i = 5;
            else if ((residual_2_i >= 32'shffffffe0) && (residual_2_i <= 31)) req_size_2_i = 6;
            else if ((residual_2_i >= 32'shffffffc0) && (residual_2_i <= 63)) req_size_2_i = 7;
            else if ((residual_2_i >= 32'shffffff80) && (residual_2_i <= 127)) req_size_2_i = 8;
            else if ((residual_2_i >= 32'shffffff00) && (residual_2_i <= 255)) req_size_2_i = 9;
            else if ((residual_2_i >= 32'shfffffe00) && (residual_2_i <= 511)) req_size_2_i = 10;
            else if ((residual_2_i >= 32'shfffffc00) && (residual_2_i <= 1023)) req_size_2_i = 11;
            else if ((residual_2_i >= 32'shfffff800) && (residual_2_i <= 2047)) req_size_2_i = 12;
            else if ((residual_2_i >= 32'shfffff000) && (residual_2_i <= 4095)) req_size_2_i = 13;
            else if ((residual_2_i >= 32'shffffe000) && (residual_2_i <= 8191)) req_size_2_i = 14;
            else if ((residual_2_i >= 32'shffffc000) && (residual_2_i <= 16383)) req_size_2_i = 15;
            else if ((residual_2_i >= 32'shffff8000) && (residual_2_i <= 32767)) req_size_2_i = 16;
            else if ((residual_2_i >= 32'shffff0000) && (residual_2_i <= 65535)) req_size_2_i = 17;
            else if ((residual_2_i >= 32'shfffdfd8a) && (residual_2_i <= 131701)) req_size_2_i = 18;
            if (sample_hpos_2_i < slice_width_value_i) begin
                if (req_size_2_i > max_size_2_i) max_size_2_i = req_size_2_i;
            end
            case (unit_c_type_2)
                0: bit_depth_i = cpntBitDepth_0;
                1: bit_depth_i = cpntBitDepth_1;
                2: bit_depth_i = cpntBitDepth_2;
                3: bit_depth_i = cpntBitDepth_3;
                default: bit_depth_i = cpntBitDepth_0;
            endcase
        if ((unit_c_type_2 % 3) == 0) begin
            qlevel_new_i = qlevel_luma_new;
        end else if ((native_420 != 0) && (unit_c_type_2 == 1)) begin
            qlevel_new_i = qlevel_luma_new;
        end else begin
            qlevel_new_i = qlevel_chroma_new;
            if ((dsc_version_minor == 2) && (cpntBitDepth_0 == cpntBitDepth_1) && (qlevel_new_i > 0)) begin
                qlevel_new_i = qlevel_new_i - 1;
            end
        end
            max_residual_size_i = bit_depth_i - qlevel_new_i;
            if (max_size_2_i > max_residual_size_i) max_size_2_i = max_residual_size_i;
        max_size_3_i = 0;
        unit_start_h_pos_value_i = unit_start_h_pos_3;
            sample_hpos_3_i = hpos_value_i + 0 - (pixels_in_group_value_i - 1) + unit_start_h_pos_value_i;
            residual_3_i = $signed(quantized_residual_3_0);
            req_size_3_i = 0;
            if (residual_3_i == 0) req_size_3_i = 0;
            else if ((residual_3_i >= 32'shffffffff) && (residual_3_i <= 0)) req_size_3_i = 1;
            else if ((residual_3_i >= 32'shfffffffe) && (residual_3_i <= 1)) req_size_3_i = 2;
            else if ((residual_3_i >= 32'shfffffffc) && (residual_3_i <= 3)) req_size_3_i = 3;
            else if ((residual_3_i >= 32'shfffffff8) && (residual_3_i <= 7)) req_size_3_i = 4;
            else if ((residual_3_i >= 32'shfffffff0) && (residual_3_i <= 15)) req_size_3_i = 5;
            else if ((residual_3_i >= 32'shffffffe0) && (residual_3_i <= 31)) req_size_3_i = 6;
            else if ((residual_3_i >= 32'shffffffc0) && (residual_3_i <= 63)) req_size_3_i = 7;
            else if ((residual_3_i >= 32'shffffff80) && (residual_3_i <= 127)) req_size_3_i = 8;
            else if ((residual_3_i >= 32'shffffff00) && (residual_3_i <= 255)) req_size_3_i = 9;
            else if ((residual_3_i >= 32'shfffffe00) && (residual_3_i <= 511)) req_size_3_i = 10;
            else if ((residual_3_i >= 32'shfffffc00) && (residual_3_i <= 1023)) req_size_3_i = 11;
            else if ((residual_3_i >= 32'shfffff800) && (residual_3_i <= 2047)) req_size_3_i = 12;
            else if ((residual_3_i >= 32'shfffff000) && (residual_3_i <= 4095)) req_size_3_i = 13;
            else if ((residual_3_i >= 32'shffffe000) && (residual_3_i <= 8191)) req_size_3_i = 14;
            else if ((residual_3_i >= 32'shffffc000) && (residual_3_i <= 16383)) req_size_3_i = 15;
            else if ((residual_3_i >= 32'shffff8000) && (residual_3_i <= 32767)) req_size_3_i = 16;
            else if ((residual_3_i >= 32'shffff0000) && (residual_3_i <= 65535)) req_size_3_i = 17;
            else if ((residual_3_i >= 32'shfffdfd8a) && (residual_3_i <= 131701)) req_size_3_i = 18;
            if (sample_hpos_3_i < slice_width_value_i) begin
                if (req_size_3_i > max_size_3_i) max_size_3_i = req_size_3_i;
            end
            sample_hpos_3_i = hpos_value_i + 1 - (pixels_in_group_value_i - 1) + unit_start_h_pos_value_i;
            residual_3_i = $signed(quantized_residual_3_1);
            req_size_3_i = 0;
            if (residual_3_i == 0) req_size_3_i = 0;
            else if ((residual_3_i >= 32'shffffffff) && (residual_3_i <= 0)) req_size_3_i = 1;
            else if ((residual_3_i >= 32'shfffffffe) && (residual_3_i <= 1)) req_size_3_i = 2;
            else if ((residual_3_i >= 32'shfffffffc) && (residual_3_i <= 3)) req_size_3_i = 3;
            else if ((residual_3_i >= 32'shfffffff8) && (residual_3_i <= 7)) req_size_3_i = 4;
            else if ((residual_3_i >= 32'shfffffff0) && (residual_3_i <= 15)) req_size_3_i = 5;
            else if ((residual_3_i >= 32'shffffffe0) && (residual_3_i <= 31)) req_size_3_i = 6;
            else if ((residual_3_i >= 32'shffffffc0) && (residual_3_i <= 63)) req_size_3_i = 7;
            else if ((residual_3_i >= 32'shffffff80) && (residual_3_i <= 127)) req_size_3_i = 8;
            else if ((residual_3_i >= 32'shffffff00) && (residual_3_i <= 255)) req_size_3_i = 9;
            else if ((residual_3_i >= 32'shfffffe00) && (residual_3_i <= 511)) req_size_3_i = 10;
            else if ((residual_3_i >= 32'shfffffc00) && (residual_3_i <= 1023)) req_size_3_i = 11;
            else if ((residual_3_i >= 32'shfffff800) && (residual_3_i <= 2047)) req_size_3_i = 12;
            else if ((residual_3_i >= 32'shfffff000) && (residual_3_i <= 4095)) req_size_3_i = 13;
            else if ((residual_3_i >= 32'shffffe000) && (residual_3_i <= 8191)) req_size_3_i = 14;
            else if ((residual_3_i >= 32'shffffc000) && (residual_3_i <= 16383)) req_size_3_i = 15;
            else if ((residual_3_i >= 32'shffff8000) && (residual_3_i <= 32767)) req_size_3_i = 16;
            else if ((residual_3_i >= 32'shffff0000) && (residual_3_i <= 65535)) req_size_3_i = 17;
            else if ((residual_3_i >= 32'shfffdfd8a) && (residual_3_i <= 131701)) req_size_3_i = 18;
            if (sample_hpos_3_i < slice_width_value_i) begin
                if (req_size_3_i > max_size_3_i) max_size_3_i = req_size_3_i;
            end
            sample_hpos_3_i = hpos_value_i + 2 - (pixels_in_group_value_i - 1) + unit_start_h_pos_value_i;
            residual_3_i = $signed(quantized_residual_3_2);
            req_size_3_i = 0;
            if (residual_3_i == 0) req_size_3_i = 0;
            else if ((residual_3_i >= 32'shffffffff) && (residual_3_i <= 0)) req_size_3_i = 1;
            else if ((residual_3_i >= 32'shfffffffe) && (residual_3_i <= 1)) req_size_3_i = 2;
            else if ((residual_3_i >= 32'shfffffffc) && (residual_3_i <= 3)) req_size_3_i = 3;
            else if ((residual_3_i >= 32'shfffffff8) && (residual_3_i <= 7)) req_size_3_i = 4;
            else if ((residual_3_i >= 32'shfffffff0) && (residual_3_i <= 15)) req_size_3_i = 5;
            else if ((residual_3_i >= 32'shffffffe0) && (residual_3_i <= 31)) req_size_3_i = 6;
            else if ((residual_3_i >= 32'shffffffc0) && (residual_3_i <= 63)) req_size_3_i = 7;
            else if ((residual_3_i >= 32'shffffff80) && (residual_3_i <= 127)) req_size_3_i = 8;
            else if ((residual_3_i >= 32'shffffff00) && (residual_3_i <= 255)) req_size_3_i = 9;
            else if ((residual_3_i >= 32'shfffffe00) && (residual_3_i <= 511)) req_size_3_i = 10;
            else if ((residual_3_i >= 32'shfffffc00) && (residual_3_i <= 1023)) req_size_3_i = 11;
            else if ((residual_3_i >= 32'shfffff800) && (residual_3_i <= 2047)) req_size_3_i = 12;
            else if ((residual_3_i >= 32'shfffff000) && (residual_3_i <= 4095)) req_size_3_i = 13;
            else if ((residual_3_i >= 32'shffffe000) && (residual_3_i <= 8191)) req_size_3_i = 14;
            else if ((residual_3_i >= 32'shffffc000) && (residual_3_i <= 16383)) req_size_3_i = 15;
            else if ((residual_3_i >= 32'shffff8000) && (residual_3_i <= 32767)) req_size_3_i = 16;
            else if ((residual_3_i >= 32'shffff0000) && (residual_3_i <= 65535)) req_size_3_i = 17;
            else if ((residual_3_i >= 32'shfffdfd8a) && (residual_3_i <= 131701)) req_size_3_i = 18;
            if (sample_hpos_3_i < slice_width_value_i) begin
                if (req_size_3_i > max_size_3_i) max_size_3_i = req_size_3_i;
            end
            case (unit_c_type_3)
                0: bit_depth_i = cpntBitDepth_0;
                1: bit_depth_i = cpntBitDepth_1;
                2: bit_depth_i = cpntBitDepth_2;
                3: bit_depth_i = cpntBitDepth_3;
                default: bit_depth_i = cpntBitDepth_0;
            endcase
        if ((unit_c_type_3 % 3) == 0) begin
            qlevel_new_i = qlevel_luma_new;
        end else if ((native_420 != 0) && (unit_c_type_3 == 1)) begin
            qlevel_new_i = qlevel_luma_new;
        end else begin
            qlevel_new_i = qlevel_chroma_new;
            if ((dsc_version_minor == 2) && (cpntBitDepth_0 == cpntBitDepth_1) && (qlevel_new_i > 0)) begin
                qlevel_new_i = qlevel_new_i - 1;
            end
        end
            max_residual_size_i = bit_depth_i - qlevel_new_i;
            if (max_size_3_i > max_residual_size_i) max_size_3_i = max_residual_size_i;
        if (units_per_group > 0) begin
            case (unit_c_type_0)
                0: bit_depth_i = cpntBitDepth_0;
                1: bit_depth_i = cpntBitDepth_1;
                2: bit_depth_i = cpntBitDepth_2;
                3: bit_depth_i = cpntBitDepth_3;
                default: bit_depth_i = cpntBitDepth_0;
            endcase
        if ((unit_c_type_0 % 3) == 0) begin
            qlevel_new_i = qlevel_luma_new;
        end else if ((native_420 != 0) && (unit_c_type_0 == 1)) begin
            qlevel_new_i = qlevel_luma_new;
        end else begin
            qlevel_new_i = qlevel_chroma_new;
            if ((dsc_version_minor == 2) && (cpntBitDepth_0 == cpntBitDepth_1) && (qlevel_new_i > 0)) begin
                qlevel_new_i = qlevel_new_i - 1;
            end
        end
        if ((unit_c_type_0 % 3) == 0) begin
            qlevel_old_i = qlevel_luma_old;
        end else if ((native_420 != 0) && (unit_c_type_0 == 1)) begin
            qlevel_old_i = qlevel_luma_old;
        end else begin
            qlevel_old_i = qlevel_chroma_old;
            if ((dsc_version_minor == 2) && (cpntBitDepth_0 == cpntBitDepth_1) && (qlevel_old_i > 0)) begin
                qlevel_old_i = qlevel_old_i - 1;
            end
        end
            pred_size_i = predicted_size_0 + qlevel_old_i - qlevel_new_i;
            max_residual_size_i = bit_depth_i - qlevel_new_i;
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
            case (unit_c_type_1)
                0: bit_depth_i = cpntBitDepth_0;
                1: bit_depth_i = cpntBitDepth_1;
                2: bit_depth_i = cpntBitDepth_2;
                3: bit_depth_i = cpntBitDepth_3;
                default: bit_depth_i = cpntBitDepth_0;
            endcase
        if ((unit_c_type_1 % 3) == 0) begin
            qlevel_new_i = qlevel_luma_new;
        end else if ((native_420 != 0) && (unit_c_type_1 == 1)) begin
            qlevel_new_i = qlevel_luma_new;
        end else begin
            qlevel_new_i = qlevel_chroma_new;
            if ((dsc_version_minor == 2) && (cpntBitDepth_0 == cpntBitDepth_1) && (qlevel_new_i > 0)) begin
                qlevel_new_i = qlevel_new_i - 1;
            end
        end
        if ((unit_c_type_1 % 3) == 0) begin
            qlevel_old_i = qlevel_luma_old;
        end else if ((native_420 != 0) && (unit_c_type_1 == 1)) begin
            qlevel_old_i = qlevel_luma_old;
        end else begin
            qlevel_old_i = qlevel_chroma_old;
            if ((dsc_version_minor == 2) && (cpntBitDepth_0 == cpntBitDepth_1) && (qlevel_old_i > 0)) begin
                qlevel_old_i = qlevel_old_i - 1;
            end
        end
            pred_size_i = predicted_size_1 + qlevel_old_i - qlevel_new_i;
            max_residual_size_i = bit_depth_i - qlevel_new_i;
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
            case (unit_c_type_2)
                0: bit_depth_i = cpntBitDepth_0;
                1: bit_depth_i = cpntBitDepth_1;
                2: bit_depth_i = cpntBitDepth_2;
                3: bit_depth_i = cpntBitDepth_3;
                default: bit_depth_i = cpntBitDepth_0;
            endcase
        if ((unit_c_type_2 % 3) == 0) begin
            qlevel_new_i = qlevel_luma_new;
        end else if ((native_420 != 0) && (unit_c_type_2 == 1)) begin
            qlevel_new_i = qlevel_luma_new;
        end else begin
            qlevel_new_i = qlevel_chroma_new;
            if ((dsc_version_minor == 2) && (cpntBitDepth_0 == cpntBitDepth_1) && (qlevel_new_i > 0)) begin
                qlevel_new_i = qlevel_new_i - 1;
            end
        end
        if ((unit_c_type_2 % 3) == 0) begin
            qlevel_old_i = qlevel_luma_old;
        end else if ((native_420 != 0) && (unit_c_type_2 == 1)) begin
            qlevel_old_i = qlevel_luma_old;
        end else begin
            qlevel_old_i = qlevel_chroma_old;
            if ((dsc_version_minor == 2) && (cpntBitDepth_0 == cpntBitDepth_1) && (qlevel_old_i > 0)) begin
                qlevel_old_i = qlevel_old_i - 1;
            end
        end
            pred_size_i = predicted_size_2 + qlevel_old_i - qlevel_new_i;
            max_residual_size_i = bit_depth_i - qlevel_new_i;
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
            case (unit_c_type_3)
                0: bit_depth_i = cpntBitDepth_0;
                1: bit_depth_i = cpntBitDepth_1;
                2: bit_depth_i = cpntBitDepth_2;
                3: bit_depth_i = cpntBitDepth_3;
                default: bit_depth_i = cpntBitDepth_0;
            endcase
        if ((unit_c_type_3 % 3) == 0) begin
            qlevel_new_i = qlevel_luma_new;
        end else if ((native_420 != 0) && (unit_c_type_3 == 1)) begin
            qlevel_new_i = qlevel_luma_new;
        end else begin
            qlevel_new_i = qlevel_chroma_new;
            if ((dsc_version_minor == 2) && (cpntBitDepth_0 == cpntBitDepth_1) && (qlevel_new_i > 0)) begin
                qlevel_new_i = qlevel_new_i - 1;
            end
        end
        if ((unit_c_type_3 % 3) == 0) begin
            qlevel_old_i = qlevel_luma_old;
        end else if ((native_420 != 0) && (unit_c_type_3 == 1)) begin
            qlevel_old_i = qlevel_luma_old;
        end else begin
            qlevel_old_i = qlevel_chroma_old;
            if ((dsc_version_minor == 2) && (cpntBitDepth_0 == cpntBitDepth_1) && (qlevel_old_i > 0)) begin
                qlevel_old_i = qlevel_old_i - 1;
            end
        end
            pred_size_i = predicted_size_3 + qlevel_old_i - qlevel_new_i;
            max_residual_size_i = bit_depth_i - qlevel_new_i;
            if (pred_size_i < 0) pred_size_i = 0;
            else if (pred_size_i > (max_residual_size_i - 1)) pred_size_i = max_residual_size_i - 1;
            if (max_size_3_i < pred_size_i)
                total_size_i = total_size_i + 1 + 3 * pred_size_i;
            else if ((max_size_3_i == max_residual_size_i) && (3 != 0))
                total_size_i = total_size_i + (max_size_3_i - pred_size_i) + 3 * max_size_3_i;
            else
                total_size_i = total_size_i + 1 + (max_size_3_i - pred_size_i) + 3 * max_size_3_i;
        end
        bit_depth_i = cpntBitDepth_0;
        qlevel_new_i = qlevel_luma_new;
        max_residual_size_i = bit_depth_i - qlevel_new_i;
        if ((max_size_0_i < max_residual_size_i) && (prev_ich_selected != 0)) total_size_i = total_size_i + 1;
        return_value = total_size_i;
        return_value = return_value + 1;
    end
endmodule
