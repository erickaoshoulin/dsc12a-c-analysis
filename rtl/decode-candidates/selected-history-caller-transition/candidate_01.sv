module historylookup_decode_transition(
    input logic native_420,
    input logic native_422,
    input logic [4:0] entry,
    input logic first_line_flag,
    input logic is_odd_line,
    input logic [2:0] num_components,
    input logic [31:0] history_0,
    input logic [31:0] history_1,
    input logic [31:0] history_2,
    input logic [31:0] history_3,
    input logic [31:0] native_base_0,
    input logic [31:0] native_base_1,
    input logic [31:0] native_base_2,
    input logic [31:0] native_base_3,
    input logic [31:0] native_base1_0,
    input logic [31:0] native_base1_1,
    input logic [31:0] native_base1_2,
    input logic [31:0] native_base1_3,
    input logic [31:0] simple_tap_0,
    input logic [31:0] simple_tap_1,
    input logic [31:0] simple_tap_2,
    output logic [31:0] p_0_out,
    output logic [31:0] p_1_out,
    output logic [31:0] p_2_out,
    output logic [31:0] p_3_out
);
    always_comb begin
        p_0_out = 32'd0;
        p_1_out = 32'd0;
        p_2_out = 32'd0;
        p_3_out = 32'd0;
        if ((first_line_flag == 0) && (entry >= 25)) begin
            if (native_420 != 0) begin
                if (((entry - 25) & 1) != 0) begin
                    p_0_out = native_base_0;
                    p_1_out = native_base_1;
                    p_2_out = is_odd_line ? native_base_3 : native_base_2;
                end else begin
                    p_0_out = native_base_1;
                    p_1_out = native_base1_0;
                    p_2_out = is_odd_line ? native_base1_3 : native_base1_2;
                end
            end else if (native_422 != 0) begin
                if (((entry - 25) & 1) != 0) begin
                    p_0_out = native_base_0;
                    p_1_out = native_base_1;
                    p_2_out = native_base_2;
                    p_3_out = native_base_3;
                end else begin
                    p_0_out = native_base_3;
                    p_1_out = native_base1_1;
                    p_2_out = native_base1_2;
                    p_3_out = native_base1_0;
                end
            end else begin
                p_0_out = simple_tap_0;
                p_1_out = simple_tap_1;
                p_2_out = simple_tap_2;
            end
        end else begin
            if (num_components > 0) p_0_out = history_0;
            if (num_components > 1) p_1_out = history_1;
            if (num_components > 2) p_2_out = history_2;
            if (num_components > 3) p_3_out = history_3;
        end
    end
endmodule

module updatehistoryelement_decode_transition(
    input logic signed [31:0] cfg_native_420,
    input logic signed [31:0] state_hpos,
    input logic signed [31:0] state_vpos,
    input logic signed [31:0] state_num_components,
    input logic signed [31:0] state_is_encoder,
    input logic signed [31:0] state_ich_selected,
    input logic signed [31:0] state_prev_ich_selected,
    input logic [31:0] recon_0,
    input logic [31:0] recon_1,
    input logic [31:0] recon_2,
    input logic [31:0] recon_3,
    input logic signed [31:0] history_valid_0,
    input logic signed [31:0] history_valid_1,
    input logic signed [31:0] history_valid_2,
    input logic signed [31:0] history_valid_3,
    input logic signed [31:0] history_valid_4,
    input logic signed [31:0] history_valid_5,
    input logic signed [31:0] history_valid_6,
    input logic signed [31:0] history_valid_7,
    input logic signed [31:0] history_valid_8,
    input logic signed [31:0] history_valid_9,
    input logic signed [31:0] history_valid_10,
    input logic signed [31:0] history_valid_11,
    input logic signed [31:0] history_valid_12,
    input logic signed [31:0] history_valid_13,
    input logic signed [31:0] history_valid_14,
    input logic signed [31:0] history_valid_15,
    input logic signed [31:0] history_valid_16,
    input logic signed [31:0] history_valid_17,
    input logic signed [31:0] history_valid_18,
    input logic signed [31:0] history_valid_19,
    input logic signed [31:0] history_valid_20,
    input logic signed [31:0] history_valid_21,
    input logic signed [31:0] history_valid_22,
    input logic signed [31:0] history_valid_23,
    input logic signed [31:0] history_valid_24,
    input logic signed [31:0] history_valid_25,
    input logic signed [31:0] history_valid_26,
    input logic signed [31:0] history_valid_27,
    input logic signed [31:0] history_valid_28,
    input logic signed [31:0] history_valid_29,
    input logic signed [31:0] history_valid_30,
    input logic signed [31:0] history_valid_31,
    input logic [31:0] history_pixel_0_0,
    input logic [31:0] history_pixel_0_1,
    input logic [31:0] history_pixel_0_2,
    input logic [31:0] history_pixel_0_3,
    input logic [31:0] history_pixel_0_4,
    input logic [31:0] history_pixel_0_5,
    input logic [31:0] history_pixel_0_6,
    input logic [31:0] history_pixel_0_7,
    input logic [31:0] history_pixel_0_8,
    input logic [31:0] history_pixel_0_9,
    input logic [31:0] history_pixel_0_10,
    input logic [31:0] history_pixel_0_11,
    input logic [31:0] history_pixel_0_12,
    input logic [31:0] history_pixel_0_13,
    input logic [31:0] history_pixel_0_14,
    input logic [31:0] history_pixel_0_15,
    input logic [31:0] history_pixel_0_16,
    input logic [31:0] history_pixel_0_17,
    input logic [31:0] history_pixel_0_18,
    input logic [31:0] history_pixel_0_19,
    input logic [31:0] history_pixel_0_20,
    input logic [31:0] history_pixel_0_21,
    input logic [31:0] history_pixel_0_22,
    input logic [31:0] history_pixel_0_23,
    input logic [31:0] history_pixel_0_24,
    input logic [31:0] history_pixel_0_25,
    input logic [31:0] history_pixel_0_26,
    input logic [31:0] history_pixel_0_27,
    input logic [31:0] history_pixel_0_28,
    input logic [31:0] history_pixel_0_29,
    input logic [31:0] history_pixel_0_30,
    input logic [31:0] history_pixel_0_31,
    input logic [31:0] history_pixel_1_0,
    input logic [31:0] history_pixel_1_1,
    input logic [31:0] history_pixel_1_2,
    input logic [31:0] history_pixel_1_3,
    input logic [31:0] history_pixel_1_4,
    input logic [31:0] history_pixel_1_5,
    input logic [31:0] history_pixel_1_6,
    input logic [31:0] history_pixel_1_7,
    input logic [31:0] history_pixel_1_8,
    input logic [31:0] history_pixel_1_9,
    input logic [31:0] history_pixel_1_10,
    input logic [31:0] history_pixel_1_11,
    input logic [31:0] history_pixel_1_12,
    input logic [31:0] history_pixel_1_13,
    input logic [31:0] history_pixel_1_14,
    input logic [31:0] history_pixel_1_15,
    input logic [31:0] history_pixel_1_16,
    input logic [31:0] history_pixel_1_17,
    input logic [31:0] history_pixel_1_18,
    input logic [31:0] history_pixel_1_19,
    input logic [31:0] history_pixel_1_20,
    input logic [31:0] history_pixel_1_21,
    input logic [31:0] history_pixel_1_22,
    input logic [31:0] history_pixel_1_23,
    input logic [31:0] history_pixel_1_24,
    input logic [31:0] history_pixel_1_25,
    input logic [31:0] history_pixel_1_26,
    input logic [31:0] history_pixel_1_27,
    input logic [31:0] history_pixel_1_28,
    input logic [31:0] history_pixel_1_29,
    input logic [31:0] history_pixel_1_30,
    input logic [31:0] history_pixel_1_31,
    input logic [31:0] history_pixel_2_0,
    input logic [31:0] history_pixel_2_1,
    input logic [31:0] history_pixel_2_2,
    input logic [31:0] history_pixel_2_3,
    input logic [31:0] history_pixel_2_4,
    input logic [31:0] history_pixel_2_5,
    input logic [31:0] history_pixel_2_6,
    input logic [31:0] history_pixel_2_7,
    input logic [31:0] history_pixel_2_8,
    input logic [31:0] history_pixel_2_9,
    input logic [31:0] history_pixel_2_10,
    input logic [31:0] history_pixel_2_11,
    input logic [31:0] history_pixel_2_12,
    input logic [31:0] history_pixel_2_13,
    input logic [31:0] history_pixel_2_14,
    input logic [31:0] history_pixel_2_15,
    input logic [31:0] history_pixel_2_16,
    input logic [31:0] history_pixel_2_17,
    input logic [31:0] history_pixel_2_18,
    input logic [31:0] history_pixel_2_19,
    input logic [31:0] history_pixel_2_20,
    input logic [31:0] history_pixel_2_21,
    input logic [31:0] history_pixel_2_22,
    input logic [31:0] history_pixel_2_23,
    input logic [31:0] history_pixel_2_24,
    input logic [31:0] history_pixel_2_25,
    input logic [31:0] history_pixel_2_26,
    input logic [31:0] history_pixel_2_27,
    input logic [31:0] history_pixel_2_28,
    input logic [31:0] history_pixel_2_29,
    input logic [31:0] history_pixel_2_30,
    input logic [31:0] history_pixel_2_31,
    input logic [31:0] history_pixel_3_0,
    input logic [31:0] history_pixel_3_1,
    input logic [31:0] history_pixel_3_2,
    input logic [31:0] history_pixel_3_3,
    input logic [31:0] history_pixel_3_4,
    input logic [31:0] history_pixel_3_5,
    input logic [31:0] history_pixel_3_6,
    input logic [31:0] history_pixel_3_7,
    input logic [31:0] history_pixel_3_8,
    input logic [31:0] history_pixel_3_9,
    input logic [31:0] history_pixel_3_10,
    input logic [31:0] history_pixel_3_11,
    input logic [31:0] history_pixel_3_12,
    input logic [31:0] history_pixel_3_13,
    input logic [31:0] history_pixel_3_14,
    input logic [31:0] history_pixel_3_15,
    input logic [31:0] history_pixel_3_16,
    input logic [31:0] history_pixel_3_17,
    input logic [31:0] history_pixel_3_18,
    input logic [31:0] history_pixel_3_19,
    input logic [31:0] history_pixel_3_20,
    input logic [31:0] history_pixel_3_21,
    input logic [31:0] history_pixel_3_22,
    input logic [31:0] history_pixel_3_23,
    input logic [31:0] history_pixel_3_24,
    input logic [31:0] history_pixel_3_25,
    input logic [31:0] history_pixel_3_26,
    input logic [31:0] history_pixel_3_27,
    input logic [31:0] history_pixel_3_28,
    input logic [31:0] history_pixel_3_29,
    input logic [31:0] history_pixel_3_30,
    input logic [31:0] history_pixel_3_31,
    output logic signed [31:0] history_valid_0_out,
    output logic signed [31:0] history_valid_1_out,
    output logic signed [31:0] history_valid_2_out,
    output logic signed [31:0] history_valid_3_out,
    output logic signed [31:0] history_valid_4_out,
    output logic signed [31:0] history_valid_5_out,
    output logic signed [31:0] history_valid_6_out,
    output logic signed [31:0] history_valid_7_out,
    output logic signed [31:0] history_valid_8_out,
    output logic signed [31:0] history_valid_9_out,
    output logic signed [31:0] history_valid_10_out,
    output logic signed [31:0] history_valid_11_out,
    output logic signed [31:0] history_valid_12_out,
    output logic signed [31:0] history_valid_13_out,
    output logic signed [31:0] history_valid_14_out,
    output logic signed [31:0] history_valid_15_out,
    output logic signed [31:0] history_valid_16_out,
    output logic signed [31:0] history_valid_17_out,
    output logic signed [31:0] history_valid_18_out,
    output logic signed [31:0] history_valid_19_out,
    output logic signed [31:0] history_valid_20_out,
    output logic signed [31:0] history_valid_21_out,
    output logic signed [31:0] history_valid_22_out,
    output logic signed [31:0] history_valid_23_out,
    output logic signed [31:0] history_valid_24_out,
    output logic signed [31:0] history_valid_25_out,
    output logic signed [31:0] history_valid_26_out,
    output logic signed [31:0] history_valid_27_out,
    output logic signed [31:0] history_valid_28_out,
    output logic signed [31:0] history_valid_29_out,
    output logic signed [31:0] history_valid_30_out,
    output logic signed [31:0] history_valid_31_out,
    output logic [31:0] history_pixel_0_0_out,
    output logic [31:0] history_pixel_0_1_out,
    output logic [31:0] history_pixel_0_2_out,
    output logic [31:0] history_pixel_0_3_out,
    output logic [31:0] history_pixel_0_4_out,
    output logic [31:0] history_pixel_0_5_out,
    output logic [31:0] history_pixel_0_6_out,
    output logic [31:0] history_pixel_0_7_out,
    output logic [31:0] history_pixel_0_8_out,
    output logic [31:0] history_pixel_0_9_out,
    output logic [31:0] history_pixel_0_10_out,
    output logic [31:0] history_pixel_0_11_out,
    output logic [31:0] history_pixel_0_12_out,
    output logic [31:0] history_pixel_0_13_out,
    output logic [31:0] history_pixel_0_14_out,
    output logic [31:0] history_pixel_0_15_out,
    output logic [31:0] history_pixel_0_16_out,
    output logic [31:0] history_pixel_0_17_out,
    output logic [31:0] history_pixel_0_18_out,
    output logic [31:0] history_pixel_0_19_out,
    output logic [31:0] history_pixel_0_20_out,
    output logic [31:0] history_pixel_0_21_out,
    output logic [31:0] history_pixel_0_22_out,
    output logic [31:0] history_pixel_0_23_out,
    output logic [31:0] history_pixel_0_24_out,
    output logic [31:0] history_pixel_0_25_out,
    output logic [31:0] history_pixel_0_26_out,
    output logic [31:0] history_pixel_0_27_out,
    output logic [31:0] history_pixel_0_28_out,
    output logic [31:0] history_pixel_0_29_out,
    output logic [31:0] history_pixel_0_30_out,
    output logic [31:0] history_pixel_0_31_out,
    output logic [31:0] history_pixel_1_0_out,
    output logic [31:0] history_pixel_1_1_out,
    output logic [31:0] history_pixel_1_2_out,
    output logic [31:0] history_pixel_1_3_out,
    output logic [31:0] history_pixel_1_4_out,
    output logic [31:0] history_pixel_1_5_out,
    output logic [31:0] history_pixel_1_6_out,
    output logic [31:0] history_pixel_1_7_out,
    output logic [31:0] history_pixel_1_8_out,
    output logic [31:0] history_pixel_1_9_out,
    output logic [31:0] history_pixel_1_10_out,
    output logic [31:0] history_pixel_1_11_out,
    output logic [31:0] history_pixel_1_12_out,
    output logic [31:0] history_pixel_1_13_out,
    output logic [31:0] history_pixel_1_14_out,
    output logic [31:0] history_pixel_1_15_out,
    output logic [31:0] history_pixel_1_16_out,
    output logic [31:0] history_pixel_1_17_out,
    output logic [31:0] history_pixel_1_18_out,
    output logic [31:0] history_pixel_1_19_out,
    output logic [31:0] history_pixel_1_20_out,
    output logic [31:0] history_pixel_1_21_out,
    output logic [31:0] history_pixel_1_22_out,
    output logic [31:0] history_pixel_1_23_out,
    output logic [31:0] history_pixel_1_24_out,
    output logic [31:0] history_pixel_1_25_out,
    output logic [31:0] history_pixel_1_26_out,
    output logic [31:0] history_pixel_1_27_out,
    output logic [31:0] history_pixel_1_28_out,
    output logic [31:0] history_pixel_1_29_out,
    output logic [31:0] history_pixel_1_30_out,
    output logic [31:0] history_pixel_1_31_out,
    output logic [31:0] history_pixel_2_0_out,
    output logic [31:0] history_pixel_2_1_out,
    output logic [31:0] history_pixel_2_2_out,
    output logic [31:0] history_pixel_2_3_out,
    output logic [31:0] history_pixel_2_4_out,
    output logic [31:0] history_pixel_2_5_out,
    output logic [31:0] history_pixel_2_6_out,
    output logic [31:0] history_pixel_2_7_out,
    output logic [31:0] history_pixel_2_8_out,
    output logic [31:0] history_pixel_2_9_out,
    output logic [31:0] history_pixel_2_10_out,
    output logic [31:0] history_pixel_2_11_out,
    output logic [31:0] history_pixel_2_12_out,
    output logic [31:0] history_pixel_2_13_out,
    output logic [31:0] history_pixel_2_14_out,
    output logic [31:0] history_pixel_2_15_out,
    output logic [31:0] history_pixel_2_16_out,
    output logic [31:0] history_pixel_2_17_out,
    output logic [31:0] history_pixel_2_18_out,
    output logic [31:0] history_pixel_2_19_out,
    output logic [31:0] history_pixel_2_20_out,
    output logic [31:0] history_pixel_2_21_out,
    output logic [31:0] history_pixel_2_22_out,
    output logic [31:0] history_pixel_2_23_out,
    output logic [31:0] history_pixel_2_24_out,
    output logic [31:0] history_pixel_2_25_out,
    output logic [31:0] history_pixel_2_26_out,
    output logic [31:0] history_pixel_2_27_out,
    output logic [31:0] history_pixel_2_28_out,
    output logic [31:0] history_pixel_2_29_out,
    output logic [31:0] history_pixel_2_30_out,
    output logic [31:0] history_pixel_2_31_out,
    output logic [31:0] history_pixel_3_0_out,
    output logic [31:0] history_pixel_3_1_out,
    output logic [31:0] history_pixel_3_2_out,
    output logic [31:0] history_pixel_3_3_out,
    output logic [31:0] history_pixel_3_4_out,
    output logic [31:0] history_pixel_3_5_out,
    output logic [31:0] history_pixel_3_6_out,
    output logic [31:0] history_pixel_3_7_out,
    output logic [31:0] history_pixel_3_8_out,
    output logic [31:0] history_pixel_3_9_out,
    output logic [31:0] history_pixel_3_10_out,
    output logic [31:0] history_pixel_3_11_out,
    output logic [31:0] history_pixel_3_12_out,
    output logic [31:0] history_pixel_3_13_out,
    output logic [31:0] history_pixel_3_14_out,
    output logic [31:0] history_pixel_3_15_out,
    output logic [31:0] history_pixel_3_16_out,
    output logic [31:0] history_pixel_3_17_out,
    output logic [31:0] history_pixel_3_18_out,
    output logic [31:0] history_pixel_3_19_out,
    output logic [31:0] history_pixel_3_20_out,
    output logic [31:0] history_pixel_3_21_out,
    output logic [31:0] history_pixel_3_22_out,
    output logic [31:0] history_pixel_3_23_out,
    output logic [31:0] history_pixel_3_24_out,
    output logic [31:0] history_pixel_3_25_out,
    output logic [31:0] history_pixel_3_26_out,
    output logic [31:0] history_pixel_3_27_out,
    output logic [31:0] history_pixel_3_28_out,
    output logic [31:0] history_pixel_3_29_out,
    output logic [31:0] history_pixel_3_30_out,
    output logic [31:0] history_pixel_3_31_out
);
    logic first_line_i;
    logic active_selection_i;
    logic [5:0] reserved_i;
    logic [4:0] location_i;
    logic found_i;
    logic [31:0] lookup_0_0_i;
    logic [31:0] lookup_0_1_i;
    logic [31:0] lookup_0_2_i;
    logic [31:0] lookup_0_3_i;
    logic [31:0] lookup_1_0_i;
    logic [31:0] lookup_1_1_i;
    logic [31:0] lookup_1_2_i;
    logic [31:0] lookup_1_3_i;
    logic [31:0] lookup_2_0_i;
    logic [31:0] lookup_2_1_i;
    logic [31:0] lookup_2_2_i;
    logic [31:0] lookup_2_3_i;
    logic [31:0] lookup_3_0_i;
    logic [31:0] lookup_3_1_i;
    logic [31:0] lookup_3_2_i;
    logic [31:0] lookup_3_3_i;
    logic [31:0] lookup_4_0_i;
    logic [31:0] lookup_4_1_i;
    logic [31:0] lookup_4_2_i;
    logic [31:0] lookup_4_3_i;
    logic [31:0] lookup_5_0_i;
    logic [31:0] lookup_5_1_i;
    logic [31:0] lookup_5_2_i;
    logic [31:0] lookup_5_3_i;
    logic [31:0] lookup_6_0_i;
    logic [31:0] lookup_6_1_i;
    logic [31:0] lookup_6_2_i;
    logic [31:0] lookup_6_3_i;
    logic [31:0] lookup_7_0_i;
    logic [31:0] lookup_7_1_i;
    logic [31:0] lookup_7_2_i;
    logic [31:0] lookup_7_3_i;
    logic [31:0] lookup_8_0_i;
    logic [31:0] lookup_8_1_i;
    logic [31:0] lookup_8_2_i;
    logic [31:0] lookup_8_3_i;
    logic [31:0] lookup_9_0_i;
    logic [31:0] lookup_9_1_i;
    logic [31:0] lookup_9_2_i;
    logic [31:0] lookup_9_3_i;
    logic [31:0] lookup_10_0_i;
    logic [31:0] lookup_10_1_i;
    logic [31:0] lookup_10_2_i;
    logic [31:0] lookup_10_3_i;
    logic [31:0] lookup_11_0_i;
    logic [31:0] lookup_11_1_i;
    logic [31:0] lookup_11_2_i;
    logic [31:0] lookup_11_3_i;
    logic [31:0] lookup_12_0_i;
    logic [31:0] lookup_12_1_i;
    logic [31:0] lookup_12_2_i;
    logic [31:0] lookup_12_3_i;
    logic [31:0] lookup_13_0_i;
    logic [31:0] lookup_13_1_i;
    logic [31:0] lookup_13_2_i;
    logic [31:0] lookup_13_3_i;
    logic [31:0] lookup_14_0_i;
    logic [31:0] lookup_14_1_i;
    logic [31:0] lookup_14_2_i;
    logic [31:0] lookup_14_3_i;
    logic [31:0] lookup_15_0_i;
    logic [31:0] lookup_15_1_i;
    logic [31:0] lookup_15_2_i;
    logic [31:0] lookup_15_3_i;
    logic [31:0] lookup_16_0_i;
    logic [31:0] lookup_16_1_i;
    logic [31:0] lookup_16_2_i;
    logic [31:0] lookup_16_3_i;
    logic [31:0] lookup_17_0_i;
    logic [31:0] lookup_17_1_i;
    logic [31:0] lookup_17_2_i;
    logic [31:0] lookup_17_3_i;
    logic [31:0] lookup_18_0_i;
    logic [31:0] lookup_18_1_i;
    logic [31:0] lookup_18_2_i;
    logic [31:0] lookup_18_3_i;
    logic [31:0] lookup_19_0_i;
    logic [31:0] lookup_19_1_i;
    logic [31:0] lookup_19_2_i;
    logic [31:0] lookup_19_3_i;
    logic [31:0] lookup_20_0_i;
    logic [31:0] lookup_20_1_i;
    logic [31:0] lookup_20_2_i;
    logic [31:0] lookup_20_3_i;
    logic [31:0] lookup_21_0_i;
    logic [31:0] lookup_21_1_i;
    logic [31:0] lookup_21_2_i;
    logic [31:0] lookup_21_3_i;
    logic [31:0] lookup_22_0_i;
    logic [31:0] lookup_22_1_i;
    logic [31:0] lookup_22_2_i;
    logic [31:0] lookup_22_3_i;
    logic [31:0] lookup_23_0_i;
    logic [31:0] lookup_23_1_i;
    logic [31:0] lookup_23_2_i;
    logic [31:0] lookup_23_3_i;
    logic [31:0] lookup_24_0_i;
    logic [31:0] lookup_24_1_i;
    logic [31:0] lookup_24_2_i;
    logic [31:0] lookup_24_3_i;
    logic [31:0] lookup_25_0_i;
    logic [31:0] lookup_25_1_i;
    logic [31:0] lookup_25_2_i;
    logic [31:0] lookup_25_3_i;
    logic [31:0] lookup_26_0_i;
    logic [31:0] lookup_26_1_i;
    logic [31:0] lookup_26_2_i;
    logic [31:0] lookup_26_3_i;
    logic [31:0] lookup_27_0_i;
    logic [31:0] lookup_27_1_i;
    logic [31:0] lookup_27_2_i;
    logic [31:0] lookup_27_3_i;
    logic [31:0] lookup_28_0_i;
    logic [31:0] lookup_28_1_i;
    logic [31:0] lookup_28_2_i;
    logic [31:0] lookup_28_3_i;
    logic [31:0] lookup_29_0_i;
    logic [31:0] lookup_29_1_i;
    logic [31:0] lookup_29_2_i;
    logic [31:0] lookup_29_3_i;
    logic [31:0] lookup_30_0_i;
    logic [31:0] lookup_30_1_i;
    logic [31:0] lookup_30_2_i;
    logic [31:0] lookup_30_3_i;
    logic [31:0] lookup_31_0_i;
    logic [31:0] lookup_31_1_i;
    logic [31:0] lookup_31_2_i;
    logic [31:0] lookup_31_3_i;

    assign first_line_i = (state_vpos == 0) || ((cfg_native_420 != 0) && (state_vpos == 1));
    assign active_selection_i = ((state_is_encoder != 0) && (state_ich_selected != 0)) || ((state_is_encoder == 0) && (state_prev_ich_selected != 0));
    assign reserved_i = first_line_i ? 6'd32 : 6'd25;

    historylookup_decode_transition u_history_lookup_0(
        .native_420(cfg_native_420[0]),
        .native_422(1'b0),
        .entry(5'd0),
        .first_line_flag(first_line_i),
        .is_odd_line(state_vpos[0]),
        .num_components(state_num_components[2:0]),
        .history_0(history_pixel_0_0),
        .history_1(history_pixel_1_0),
        .history_2(history_pixel_2_0),
        .history_3(history_pixel_3_0),
        .native_base_0(32'd0),
        .native_base_1(32'd0),
        .native_base_2(32'd0),
        .native_base_3(32'd0),
        .native_base1_0(32'd0),
        .native_base1_1(32'd0),
        .native_base1_2(32'd0),
        .native_base1_3(32'd0),
        .simple_tap_0(32'd0),
        .simple_tap_1(32'd0),
        .simple_tap_2(32'd0),
        .p_0_out(lookup_0_0_i),
        .p_1_out(lookup_0_1_i),
        .p_2_out(lookup_0_2_i),
        .p_3_out(lookup_0_3_i)
    );

    historylookup_decode_transition u_history_lookup_1(
        .native_420(cfg_native_420[0]),
        .native_422(1'b0),
        .entry(5'd1),
        .first_line_flag(first_line_i),
        .is_odd_line(state_vpos[0]),
        .num_components(state_num_components[2:0]),
        .history_0(history_pixel_0_1),
        .history_1(history_pixel_1_1),
        .history_2(history_pixel_2_1),
        .history_3(history_pixel_3_1),
        .native_base_0(32'd0),
        .native_base_1(32'd0),
        .native_base_2(32'd0),
        .native_base_3(32'd0),
        .native_base1_0(32'd0),
        .native_base1_1(32'd0),
        .native_base1_2(32'd0),
        .native_base1_3(32'd0),
        .simple_tap_0(32'd0),
        .simple_tap_1(32'd0),
        .simple_tap_2(32'd0),
        .p_0_out(lookup_1_0_i),
        .p_1_out(lookup_1_1_i),
        .p_2_out(lookup_1_2_i),
        .p_3_out(lookup_1_3_i)
    );

    historylookup_decode_transition u_history_lookup_2(
        .native_420(cfg_native_420[0]),
        .native_422(1'b0),
        .entry(5'd2),
        .first_line_flag(first_line_i),
        .is_odd_line(state_vpos[0]),
        .num_components(state_num_components[2:0]),
        .history_0(history_pixel_0_2),
        .history_1(history_pixel_1_2),
        .history_2(history_pixel_2_2),
        .history_3(history_pixel_3_2),
        .native_base_0(32'd0),
        .native_base_1(32'd0),
        .native_base_2(32'd0),
        .native_base_3(32'd0),
        .native_base1_0(32'd0),
        .native_base1_1(32'd0),
        .native_base1_2(32'd0),
        .native_base1_3(32'd0),
        .simple_tap_0(32'd0),
        .simple_tap_1(32'd0),
        .simple_tap_2(32'd0),
        .p_0_out(lookup_2_0_i),
        .p_1_out(lookup_2_1_i),
        .p_2_out(lookup_2_2_i),
        .p_3_out(lookup_2_3_i)
    );

    historylookup_decode_transition u_history_lookup_3(
        .native_420(cfg_native_420[0]),
        .native_422(1'b0),
        .entry(5'd3),
        .first_line_flag(first_line_i),
        .is_odd_line(state_vpos[0]),
        .num_components(state_num_components[2:0]),
        .history_0(history_pixel_0_3),
        .history_1(history_pixel_1_3),
        .history_2(history_pixel_2_3),
        .history_3(history_pixel_3_3),
        .native_base_0(32'd0),
        .native_base_1(32'd0),
        .native_base_2(32'd0),
        .native_base_3(32'd0),
        .native_base1_0(32'd0),
        .native_base1_1(32'd0),
        .native_base1_2(32'd0),
        .native_base1_3(32'd0),
        .simple_tap_0(32'd0),
        .simple_tap_1(32'd0),
        .simple_tap_2(32'd0),
        .p_0_out(lookup_3_0_i),
        .p_1_out(lookup_3_1_i),
        .p_2_out(lookup_3_2_i),
        .p_3_out(lookup_3_3_i)
    );

    historylookup_decode_transition u_history_lookup_4(
        .native_420(cfg_native_420[0]),
        .native_422(1'b0),
        .entry(5'd4),
        .first_line_flag(first_line_i),
        .is_odd_line(state_vpos[0]),
        .num_components(state_num_components[2:0]),
        .history_0(history_pixel_0_4),
        .history_1(history_pixel_1_4),
        .history_2(history_pixel_2_4),
        .history_3(history_pixel_3_4),
        .native_base_0(32'd0),
        .native_base_1(32'd0),
        .native_base_2(32'd0),
        .native_base_3(32'd0),
        .native_base1_0(32'd0),
        .native_base1_1(32'd0),
        .native_base1_2(32'd0),
        .native_base1_3(32'd0),
        .simple_tap_0(32'd0),
        .simple_tap_1(32'd0),
        .simple_tap_2(32'd0),
        .p_0_out(lookup_4_0_i),
        .p_1_out(lookup_4_1_i),
        .p_2_out(lookup_4_2_i),
        .p_3_out(lookup_4_3_i)
    );

    historylookup_decode_transition u_history_lookup_5(
        .native_420(cfg_native_420[0]),
        .native_422(1'b0),
        .entry(5'd5),
        .first_line_flag(first_line_i),
        .is_odd_line(state_vpos[0]),
        .num_components(state_num_components[2:0]),
        .history_0(history_pixel_0_5),
        .history_1(history_pixel_1_5),
        .history_2(history_pixel_2_5),
        .history_3(history_pixel_3_5),
        .native_base_0(32'd0),
        .native_base_1(32'd0),
        .native_base_2(32'd0),
        .native_base_3(32'd0),
        .native_base1_0(32'd0),
        .native_base1_1(32'd0),
        .native_base1_2(32'd0),
        .native_base1_3(32'd0),
        .simple_tap_0(32'd0),
        .simple_tap_1(32'd0),
        .simple_tap_2(32'd0),
        .p_0_out(lookup_5_0_i),
        .p_1_out(lookup_5_1_i),
        .p_2_out(lookup_5_2_i),
        .p_3_out(lookup_5_3_i)
    );

    historylookup_decode_transition u_history_lookup_6(
        .native_420(cfg_native_420[0]),
        .native_422(1'b0),
        .entry(5'd6),
        .first_line_flag(first_line_i),
        .is_odd_line(state_vpos[0]),
        .num_components(state_num_components[2:0]),
        .history_0(history_pixel_0_6),
        .history_1(history_pixel_1_6),
        .history_2(history_pixel_2_6),
        .history_3(history_pixel_3_6),
        .native_base_0(32'd0),
        .native_base_1(32'd0),
        .native_base_2(32'd0),
        .native_base_3(32'd0),
        .native_base1_0(32'd0),
        .native_base1_1(32'd0),
        .native_base1_2(32'd0),
        .native_base1_3(32'd0),
        .simple_tap_0(32'd0),
        .simple_tap_1(32'd0),
        .simple_tap_2(32'd0),
        .p_0_out(lookup_6_0_i),
        .p_1_out(lookup_6_1_i),
        .p_2_out(lookup_6_2_i),
        .p_3_out(lookup_6_3_i)
    );

    historylookup_decode_transition u_history_lookup_7(
        .native_420(cfg_native_420[0]),
        .native_422(1'b0),
        .entry(5'd7),
        .first_line_flag(first_line_i),
        .is_odd_line(state_vpos[0]),
        .num_components(state_num_components[2:0]),
        .history_0(history_pixel_0_7),
        .history_1(history_pixel_1_7),
        .history_2(history_pixel_2_7),
        .history_3(history_pixel_3_7),
        .native_base_0(32'd0),
        .native_base_1(32'd0),
        .native_base_2(32'd0),
        .native_base_3(32'd0),
        .native_base1_0(32'd0),
        .native_base1_1(32'd0),
        .native_base1_2(32'd0),
        .native_base1_3(32'd0),
        .simple_tap_0(32'd0),
        .simple_tap_1(32'd0),
        .simple_tap_2(32'd0),
        .p_0_out(lookup_7_0_i),
        .p_1_out(lookup_7_1_i),
        .p_2_out(lookup_7_2_i),
        .p_3_out(lookup_7_3_i)
    );

    historylookup_decode_transition u_history_lookup_8(
        .native_420(cfg_native_420[0]),
        .native_422(1'b0),
        .entry(5'd8),
        .first_line_flag(first_line_i),
        .is_odd_line(state_vpos[0]),
        .num_components(state_num_components[2:0]),
        .history_0(history_pixel_0_8),
        .history_1(history_pixel_1_8),
        .history_2(history_pixel_2_8),
        .history_3(history_pixel_3_8),
        .native_base_0(32'd0),
        .native_base_1(32'd0),
        .native_base_2(32'd0),
        .native_base_3(32'd0),
        .native_base1_0(32'd0),
        .native_base1_1(32'd0),
        .native_base1_2(32'd0),
        .native_base1_3(32'd0),
        .simple_tap_0(32'd0),
        .simple_tap_1(32'd0),
        .simple_tap_2(32'd0),
        .p_0_out(lookup_8_0_i),
        .p_1_out(lookup_8_1_i),
        .p_2_out(lookup_8_2_i),
        .p_3_out(lookup_8_3_i)
    );

    historylookup_decode_transition u_history_lookup_9(
        .native_420(cfg_native_420[0]),
        .native_422(1'b0),
        .entry(5'd9),
        .first_line_flag(first_line_i),
        .is_odd_line(state_vpos[0]),
        .num_components(state_num_components[2:0]),
        .history_0(history_pixel_0_9),
        .history_1(history_pixel_1_9),
        .history_2(history_pixel_2_9),
        .history_3(history_pixel_3_9),
        .native_base_0(32'd0),
        .native_base_1(32'd0),
        .native_base_2(32'd0),
        .native_base_3(32'd0),
        .native_base1_0(32'd0),
        .native_base1_1(32'd0),
        .native_base1_2(32'd0),
        .native_base1_3(32'd0),
        .simple_tap_0(32'd0),
        .simple_tap_1(32'd0),
        .simple_tap_2(32'd0),
        .p_0_out(lookup_9_0_i),
        .p_1_out(lookup_9_1_i),
        .p_2_out(lookup_9_2_i),
        .p_3_out(lookup_9_3_i)
    );

    historylookup_decode_transition u_history_lookup_10(
        .native_420(cfg_native_420[0]),
        .native_422(1'b0),
        .entry(5'd10),
        .first_line_flag(first_line_i),
        .is_odd_line(state_vpos[0]),
        .num_components(state_num_components[2:0]),
        .history_0(history_pixel_0_10),
        .history_1(history_pixel_1_10),
        .history_2(history_pixel_2_10),
        .history_3(history_pixel_3_10),
        .native_base_0(32'd0),
        .native_base_1(32'd0),
        .native_base_2(32'd0),
        .native_base_3(32'd0),
        .native_base1_0(32'd0),
        .native_base1_1(32'd0),
        .native_base1_2(32'd0),
        .native_base1_3(32'd0),
        .simple_tap_0(32'd0),
        .simple_tap_1(32'd0),
        .simple_tap_2(32'd0),
        .p_0_out(lookup_10_0_i),
        .p_1_out(lookup_10_1_i),
        .p_2_out(lookup_10_2_i),
        .p_3_out(lookup_10_3_i)
    );

    historylookup_decode_transition u_history_lookup_11(
        .native_420(cfg_native_420[0]),
        .native_422(1'b0),
        .entry(5'd11),
        .first_line_flag(first_line_i),
        .is_odd_line(state_vpos[0]),
        .num_components(state_num_components[2:0]),
        .history_0(history_pixel_0_11),
        .history_1(history_pixel_1_11),
        .history_2(history_pixel_2_11),
        .history_3(history_pixel_3_11),
        .native_base_0(32'd0),
        .native_base_1(32'd0),
        .native_base_2(32'd0),
        .native_base_3(32'd0),
        .native_base1_0(32'd0),
        .native_base1_1(32'd0),
        .native_base1_2(32'd0),
        .native_base1_3(32'd0),
        .simple_tap_0(32'd0),
        .simple_tap_1(32'd0),
        .simple_tap_2(32'd0),
        .p_0_out(lookup_11_0_i),
        .p_1_out(lookup_11_1_i),
        .p_2_out(lookup_11_2_i),
        .p_3_out(lookup_11_3_i)
    );

    historylookup_decode_transition u_history_lookup_12(
        .native_420(cfg_native_420[0]),
        .native_422(1'b0),
        .entry(5'd12),
        .first_line_flag(first_line_i),
        .is_odd_line(state_vpos[0]),
        .num_components(state_num_components[2:0]),
        .history_0(history_pixel_0_12),
        .history_1(history_pixel_1_12),
        .history_2(history_pixel_2_12),
        .history_3(history_pixel_3_12),
        .native_base_0(32'd0),
        .native_base_1(32'd0),
        .native_base_2(32'd0),
        .native_base_3(32'd0),
        .native_base1_0(32'd0),
        .native_base1_1(32'd0),
        .native_base1_2(32'd0),
        .native_base1_3(32'd0),
        .simple_tap_0(32'd0),
        .simple_tap_1(32'd0),
        .simple_tap_2(32'd0),
        .p_0_out(lookup_12_0_i),
        .p_1_out(lookup_12_1_i),
        .p_2_out(lookup_12_2_i),
        .p_3_out(lookup_12_3_i)
    );

    historylookup_decode_transition u_history_lookup_13(
        .native_420(cfg_native_420[0]),
        .native_422(1'b0),
        .entry(5'd13),
        .first_line_flag(first_line_i),
        .is_odd_line(state_vpos[0]),
        .num_components(state_num_components[2:0]),
        .history_0(history_pixel_0_13),
        .history_1(history_pixel_1_13),
        .history_2(history_pixel_2_13),
        .history_3(history_pixel_3_13),
        .native_base_0(32'd0),
        .native_base_1(32'd0),
        .native_base_2(32'd0),
        .native_base_3(32'd0),
        .native_base1_0(32'd0),
        .native_base1_1(32'd0),
        .native_base1_2(32'd0),
        .native_base1_3(32'd0),
        .simple_tap_0(32'd0),
        .simple_tap_1(32'd0),
        .simple_tap_2(32'd0),
        .p_0_out(lookup_13_0_i),
        .p_1_out(lookup_13_1_i),
        .p_2_out(lookup_13_2_i),
        .p_3_out(lookup_13_3_i)
    );

    historylookup_decode_transition u_history_lookup_14(
        .native_420(cfg_native_420[0]),
        .native_422(1'b0),
        .entry(5'd14),
        .first_line_flag(first_line_i),
        .is_odd_line(state_vpos[0]),
        .num_components(state_num_components[2:0]),
        .history_0(history_pixel_0_14),
        .history_1(history_pixel_1_14),
        .history_2(history_pixel_2_14),
        .history_3(history_pixel_3_14),
        .native_base_0(32'd0),
        .native_base_1(32'd0),
        .native_base_2(32'd0),
        .native_base_3(32'd0),
        .native_base1_0(32'd0),
        .native_base1_1(32'd0),
        .native_base1_2(32'd0),
        .native_base1_3(32'd0),
        .simple_tap_0(32'd0),
        .simple_tap_1(32'd0),
        .simple_tap_2(32'd0),
        .p_0_out(lookup_14_0_i),
        .p_1_out(lookup_14_1_i),
        .p_2_out(lookup_14_2_i),
        .p_3_out(lookup_14_3_i)
    );

    historylookup_decode_transition u_history_lookup_15(
        .native_420(cfg_native_420[0]),
        .native_422(1'b0),
        .entry(5'd15),
        .first_line_flag(first_line_i),
        .is_odd_line(state_vpos[0]),
        .num_components(state_num_components[2:0]),
        .history_0(history_pixel_0_15),
        .history_1(history_pixel_1_15),
        .history_2(history_pixel_2_15),
        .history_3(history_pixel_3_15),
        .native_base_0(32'd0),
        .native_base_1(32'd0),
        .native_base_2(32'd0),
        .native_base_3(32'd0),
        .native_base1_0(32'd0),
        .native_base1_1(32'd0),
        .native_base1_2(32'd0),
        .native_base1_3(32'd0),
        .simple_tap_0(32'd0),
        .simple_tap_1(32'd0),
        .simple_tap_2(32'd0),
        .p_0_out(lookup_15_0_i),
        .p_1_out(lookup_15_1_i),
        .p_2_out(lookup_15_2_i),
        .p_3_out(lookup_15_3_i)
    );

    historylookup_decode_transition u_history_lookup_16(
        .native_420(cfg_native_420[0]),
        .native_422(1'b0),
        .entry(5'd16),
        .first_line_flag(first_line_i),
        .is_odd_line(state_vpos[0]),
        .num_components(state_num_components[2:0]),
        .history_0(history_pixel_0_16),
        .history_1(history_pixel_1_16),
        .history_2(history_pixel_2_16),
        .history_3(history_pixel_3_16),
        .native_base_0(32'd0),
        .native_base_1(32'd0),
        .native_base_2(32'd0),
        .native_base_3(32'd0),
        .native_base1_0(32'd0),
        .native_base1_1(32'd0),
        .native_base1_2(32'd0),
        .native_base1_3(32'd0),
        .simple_tap_0(32'd0),
        .simple_tap_1(32'd0),
        .simple_tap_2(32'd0),
        .p_0_out(lookup_16_0_i),
        .p_1_out(lookup_16_1_i),
        .p_2_out(lookup_16_2_i),
        .p_3_out(lookup_16_3_i)
    );

    historylookup_decode_transition u_history_lookup_17(
        .native_420(cfg_native_420[0]),
        .native_422(1'b0),
        .entry(5'd17),
        .first_line_flag(first_line_i),
        .is_odd_line(state_vpos[0]),
        .num_components(state_num_components[2:0]),
        .history_0(history_pixel_0_17),
        .history_1(history_pixel_1_17),
        .history_2(history_pixel_2_17),
        .history_3(history_pixel_3_17),
        .native_base_0(32'd0),
        .native_base_1(32'd0),
        .native_base_2(32'd0),
        .native_base_3(32'd0),
        .native_base1_0(32'd0),
        .native_base1_1(32'd0),
        .native_base1_2(32'd0),
        .native_base1_3(32'd0),
        .simple_tap_0(32'd0),
        .simple_tap_1(32'd0),
        .simple_tap_2(32'd0),
        .p_0_out(lookup_17_0_i),
        .p_1_out(lookup_17_1_i),
        .p_2_out(lookup_17_2_i),
        .p_3_out(lookup_17_3_i)
    );

    historylookup_decode_transition u_history_lookup_18(
        .native_420(cfg_native_420[0]),
        .native_422(1'b0),
        .entry(5'd18),
        .first_line_flag(first_line_i),
        .is_odd_line(state_vpos[0]),
        .num_components(state_num_components[2:0]),
        .history_0(history_pixel_0_18),
        .history_1(history_pixel_1_18),
        .history_2(history_pixel_2_18),
        .history_3(history_pixel_3_18),
        .native_base_0(32'd0),
        .native_base_1(32'd0),
        .native_base_2(32'd0),
        .native_base_3(32'd0),
        .native_base1_0(32'd0),
        .native_base1_1(32'd0),
        .native_base1_2(32'd0),
        .native_base1_3(32'd0),
        .simple_tap_0(32'd0),
        .simple_tap_1(32'd0),
        .simple_tap_2(32'd0),
        .p_0_out(lookup_18_0_i),
        .p_1_out(lookup_18_1_i),
        .p_2_out(lookup_18_2_i),
        .p_3_out(lookup_18_3_i)
    );

    historylookup_decode_transition u_history_lookup_19(
        .native_420(cfg_native_420[0]),
        .native_422(1'b0),
        .entry(5'd19),
        .first_line_flag(first_line_i),
        .is_odd_line(state_vpos[0]),
        .num_components(state_num_components[2:0]),
        .history_0(history_pixel_0_19),
        .history_1(history_pixel_1_19),
        .history_2(history_pixel_2_19),
        .history_3(history_pixel_3_19),
        .native_base_0(32'd0),
        .native_base_1(32'd0),
        .native_base_2(32'd0),
        .native_base_3(32'd0),
        .native_base1_0(32'd0),
        .native_base1_1(32'd0),
        .native_base1_2(32'd0),
        .native_base1_3(32'd0),
        .simple_tap_0(32'd0),
        .simple_tap_1(32'd0),
        .simple_tap_2(32'd0),
        .p_0_out(lookup_19_0_i),
        .p_1_out(lookup_19_1_i),
        .p_2_out(lookup_19_2_i),
        .p_3_out(lookup_19_3_i)
    );

    historylookup_decode_transition u_history_lookup_20(
        .native_420(cfg_native_420[0]),
        .native_422(1'b0),
        .entry(5'd20),
        .first_line_flag(first_line_i),
        .is_odd_line(state_vpos[0]),
        .num_components(state_num_components[2:0]),
        .history_0(history_pixel_0_20),
        .history_1(history_pixel_1_20),
        .history_2(history_pixel_2_20),
        .history_3(history_pixel_3_20),
        .native_base_0(32'd0),
        .native_base_1(32'd0),
        .native_base_2(32'd0),
        .native_base_3(32'd0),
        .native_base1_0(32'd0),
        .native_base1_1(32'd0),
        .native_base1_2(32'd0),
        .native_base1_3(32'd0),
        .simple_tap_0(32'd0),
        .simple_tap_1(32'd0),
        .simple_tap_2(32'd0),
        .p_0_out(lookup_20_0_i),
        .p_1_out(lookup_20_1_i),
        .p_2_out(lookup_20_2_i),
        .p_3_out(lookup_20_3_i)
    );

    historylookup_decode_transition u_history_lookup_21(
        .native_420(cfg_native_420[0]),
        .native_422(1'b0),
        .entry(5'd21),
        .first_line_flag(first_line_i),
        .is_odd_line(state_vpos[0]),
        .num_components(state_num_components[2:0]),
        .history_0(history_pixel_0_21),
        .history_1(history_pixel_1_21),
        .history_2(history_pixel_2_21),
        .history_3(history_pixel_3_21),
        .native_base_0(32'd0),
        .native_base_1(32'd0),
        .native_base_2(32'd0),
        .native_base_3(32'd0),
        .native_base1_0(32'd0),
        .native_base1_1(32'd0),
        .native_base1_2(32'd0),
        .native_base1_3(32'd0),
        .simple_tap_0(32'd0),
        .simple_tap_1(32'd0),
        .simple_tap_2(32'd0),
        .p_0_out(lookup_21_0_i),
        .p_1_out(lookup_21_1_i),
        .p_2_out(lookup_21_2_i),
        .p_3_out(lookup_21_3_i)
    );

    historylookup_decode_transition u_history_lookup_22(
        .native_420(cfg_native_420[0]),
        .native_422(1'b0),
        .entry(5'd22),
        .first_line_flag(first_line_i),
        .is_odd_line(state_vpos[0]),
        .num_components(state_num_components[2:0]),
        .history_0(history_pixel_0_22),
        .history_1(history_pixel_1_22),
        .history_2(history_pixel_2_22),
        .history_3(history_pixel_3_22),
        .native_base_0(32'd0),
        .native_base_1(32'd0),
        .native_base_2(32'd0),
        .native_base_3(32'd0),
        .native_base1_0(32'd0),
        .native_base1_1(32'd0),
        .native_base1_2(32'd0),
        .native_base1_3(32'd0),
        .simple_tap_0(32'd0),
        .simple_tap_1(32'd0),
        .simple_tap_2(32'd0),
        .p_0_out(lookup_22_0_i),
        .p_1_out(lookup_22_1_i),
        .p_2_out(lookup_22_2_i),
        .p_3_out(lookup_22_3_i)
    );

    historylookup_decode_transition u_history_lookup_23(
        .native_420(cfg_native_420[0]),
        .native_422(1'b0),
        .entry(5'd23),
        .first_line_flag(first_line_i),
        .is_odd_line(state_vpos[0]),
        .num_components(state_num_components[2:0]),
        .history_0(history_pixel_0_23),
        .history_1(history_pixel_1_23),
        .history_2(history_pixel_2_23),
        .history_3(history_pixel_3_23),
        .native_base_0(32'd0),
        .native_base_1(32'd0),
        .native_base_2(32'd0),
        .native_base_3(32'd0),
        .native_base1_0(32'd0),
        .native_base1_1(32'd0),
        .native_base1_2(32'd0),
        .native_base1_3(32'd0),
        .simple_tap_0(32'd0),
        .simple_tap_1(32'd0),
        .simple_tap_2(32'd0),
        .p_0_out(lookup_23_0_i),
        .p_1_out(lookup_23_1_i),
        .p_2_out(lookup_23_2_i),
        .p_3_out(lookup_23_3_i)
    );

    historylookup_decode_transition u_history_lookup_24(
        .native_420(cfg_native_420[0]),
        .native_422(1'b0),
        .entry(5'd24),
        .first_line_flag(first_line_i),
        .is_odd_line(state_vpos[0]),
        .num_components(state_num_components[2:0]),
        .history_0(history_pixel_0_24),
        .history_1(history_pixel_1_24),
        .history_2(history_pixel_2_24),
        .history_3(history_pixel_3_24),
        .native_base_0(32'd0),
        .native_base_1(32'd0),
        .native_base_2(32'd0),
        .native_base_3(32'd0),
        .native_base1_0(32'd0),
        .native_base1_1(32'd0),
        .native_base1_2(32'd0),
        .native_base1_3(32'd0),
        .simple_tap_0(32'd0),
        .simple_tap_1(32'd0),
        .simple_tap_2(32'd0),
        .p_0_out(lookup_24_0_i),
        .p_1_out(lookup_24_1_i),
        .p_2_out(lookup_24_2_i),
        .p_3_out(lookup_24_3_i)
    );

    historylookup_decode_transition u_history_lookup_25(
        .native_420(cfg_native_420[0]),
        .native_422(1'b0),
        .entry(5'd25),
        .first_line_flag(first_line_i),
        .is_odd_line(state_vpos[0]),
        .num_components(state_num_components[2:0]),
        .history_0(history_pixel_0_25),
        .history_1(history_pixel_1_25),
        .history_2(history_pixel_2_25),
        .history_3(history_pixel_3_25),
        .native_base_0(32'd0),
        .native_base_1(32'd0),
        .native_base_2(32'd0),
        .native_base_3(32'd0),
        .native_base1_0(32'd0),
        .native_base1_1(32'd0),
        .native_base1_2(32'd0),
        .native_base1_3(32'd0),
        .simple_tap_0(32'd0),
        .simple_tap_1(32'd0),
        .simple_tap_2(32'd0),
        .p_0_out(lookup_25_0_i),
        .p_1_out(lookup_25_1_i),
        .p_2_out(lookup_25_2_i),
        .p_3_out(lookup_25_3_i)
    );

    historylookup_decode_transition u_history_lookup_26(
        .native_420(cfg_native_420[0]),
        .native_422(1'b0),
        .entry(5'd26),
        .first_line_flag(first_line_i),
        .is_odd_line(state_vpos[0]),
        .num_components(state_num_components[2:0]),
        .history_0(history_pixel_0_26),
        .history_1(history_pixel_1_26),
        .history_2(history_pixel_2_26),
        .history_3(history_pixel_3_26),
        .native_base_0(32'd0),
        .native_base_1(32'd0),
        .native_base_2(32'd0),
        .native_base_3(32'd0),
        .native_base1_0(32'd0),
        .native_base1_1(32'd0),
        .native_base1_2(32'd0),
        .native_base1_3(32'd0),
        .simple_tap_0(32'd0),
        .simple_tap_1(32'd0),
        .simple_tap_2(32'd0),
        .p_0_out(lookup_26_0_i),
        .p_1_out(lookup_26_1_i),
        .p_2_out(lookup_26_2_i),
        .p_3_out(lookup_26_3_i)
    );

    historylookup_decode_transition u_history_lookup_27(
        .native_420(cfg_native_420[0]),
        .native_422(1'b0),
        .entry(5'd27),
        .first_line_flag(first_line_i),
        .is_odd_line(state_vpos[0]),
        .num_components(state_num_components[2:0]),
        .history_0(history_pixel_0_27),
        .history_1(history_pixel_1_27),
        .history_2(history_pixel_2_27),
        .history_3(history_pixel_3_27),
        .native_base_0(32'd0),
        .native_base_1(32'd0),
        .native_base_2(32'd0),
        .native_base_3(32'd0),
        .native_base1_0(32'd0),
        .native_base1_1(32'd0),
        .native_base1_2(32'd0),
        .native_base1_3(32'd0),
        .simple_tap_0(32'd0),
        .simple_tap_1(32'd0),
        .simple_tap_2(32'd0),
        .p_0_out(lookup_27_0_i),
        .p_1_out(lookup_27_1_i),
        .p_2_out(lookup_27_2_i),
        .p_3_out(lookup_27_3_i)
    );

    historylookup_decode_transition u_history_lookup_28(
        .native_420(cfg_native_420[0]),
        .native_422(1'b0),
        .entry(5'd28),
        .first_line_flag(first_line_i),
        .is_odd_line(state_vpos[0]),
        .num_components(state_num_components[2:0]),
        .history_0(history_pixel_0_28),
        .history_1(history_pixel_1_28),
        .history_2(history_pixel_2_28),
        .history_3(history_pixel_3_28),
        .native_base_0(32'd0),
        .native_base_1(32'd0),
        .native_base_2(32'd0),
        .native_base_3(32'd0),
        .native_base1_0(32'd0),
        .native_base1_1(32'd0),
        .native_base1_2(32'd0),
        .native_base1_3(32'd0),
        .simple_tap_0(32'd0),
        .simple_tap_1(32'd0),
        .simple_tap_2(32'd0),
        .p_0_out(lookup_28_0_i),
        .p_1_out(lookup_28_1_i),
        .p_2_out(lookup_28_2_i),
        .p_3_out(lookup_28_3_i)
    );

    historylookup_decode_transition u_history_lookup_29(
        .native_420(cfg_native_420[0]),
        .native_422(1'b0),
        .entry(5'd29),
        .first_line_flag(first_line_i),
        .is_odd_line(state_vpos[0]),
        .num_components(state_num_components[2:0]),
        .history_0(history_pixel_0_29),
        .history_1(history_pixel_1_29),
        .history_2(history_pixel_2_29),
        .history_3(history_pixel_3_29),
        .native_base_0(32'd0),
        .native_base_1(32'd0),
        .native_base_2(32'd0),
        .native_base_3(32'd0),
        .native_base1_0(32'd0),
        .native_base1_1(32'd0),
        .native_base1_2(32'd0),
        .native_base1_3(32'd0),
        .simple_tap_0(32'd0),
        .simple_tap_1(32'd0),
        .simple_tap_2(32'd0),
        .p_0_out(lookup_29_0_i),
        .p_1_out(lookup_29_1_i),
        .p_2_out(lookup_29_2_i),
        .p_3_out(lookup_29_3_i)
    );

    historylookup_decode_transition u_history_lookup_30(
        .native_420(cfg_native_420[0]),
        .native_422(1'b0),
        .entry(5'd30),
        .first_line_flag(first_line_i),
        .is_odd_line(state_vpos[0]),
        .num_components(state_num_components[2:0]),
        .history_0(history_pixel_0_30),
        .history_1(history_pixel_1_30),
        .history_2(history_pixel_2_30),
        .history_3(history_pixel_3_30),
        .native_base_0(32'd0),
        .native_base_1(32'd0),
        .native_base_2(32'd0),
        .native_base_3(32'd0),
        .native_base1_0(32'd0),
        .native_base1_1(32'd0),
        .native_base1_2(32'd0),
        .native_base1_3(32'd0),
        .simple_tap_0(32'd0),
        .simple_tap_1(32'd0),
        .simple_tap_2(32'd0),
        .p_0_out(lookup_30_0_i),
        .p_1_out(lookup_30_1_i),
        .p_2_out(lookup_30_2_i),
        .p_3_out(lookup_30_3_i)
    );

    historylookup_decode_transition u_history_lookup_31(
        .native_420(cfg_native_420[0]),
        .native_422(1'b0),
        .entry(5'd31),
        .first_line_flag(first_line_i),
        .is_odd_line(state_vpos[0]),
        .num_components(state_num_components[2:0]),
        .history_0(history_pixel_0_31),
        .history_1(history_pixel_1_31),
        .history_2(history_pixel_2_31),
        .history_3(history_pixel_3_31),
        .native_base_0(32'd0),
        .native_base_1(32'd0),
        .native_base_2(32'd0),
        .native_base_3(32'd0),
        .native_base1_0(32'd0),
        .native_base1_1(32'd0),
        .native_base1_2(32'd0),
        .native_base1_3(32'd0),
        .simple_tap_0(32'd0),
        .simple_tap_1(32'd0),
        .simple_tap_2(32'd0),
        .p_0_out(lookup_31_0_i),
        .p_1_out(lookup_31_1_i),
        .p_2_out(lookup_31_2_i),
        .p_3_out(lookup_31_3_i)
    );

    always_comb begin
        history_valid_0_out = history_valid_0;
        history_valid_1_out = history_valid_1;
        history_valid_2_out = history_valid_2;
        history_valid_3_out = history_valid_3;
        history_valid_4_out = history_valid_4;
        history_valid_5_out = history_valid_5;
        history_valid_6_out = history_valid_6;
        history_valid_7_out = history_valid_7;
        history_valid_8_out = history_valid_8;
        history_valid_9_out = history_valid_9;
        history_valid_10_out = history_valid_10;
        history_valid_11_out = history_valid_11;
        history_valid_12_out = history_valid_12;
        history_valid_13_out = history_valid_13;
        history_valid_14_out = history_valid_14;
        history_valid_15_out = history_valid_15;
        history_valid_16_out = history_valid_16;
        history_valid_17_out = history_valid_17;
        history_valid_18_out = history_valid_18;
        history_valid_19_out = history_valid_19;
        history_valid_20_out = history_valid_20;
        history_valid_21_out = history_valid_21;
        history_valid_22_out = history_valid_22;
        history_valid_23_out = history_valid_23;
        history_valid_24_out = history_valid_24;
        history_valid_25_out = history_valid_25;
        history_valid_26_out = history_valid_26;
        history_valid_27_out = history_valid_27;
        history_valid_28_out = history_valid_28;
        history_valid_29_out = history_valid_29;
        history_valid_30_out = history_valid_30;
        history_valid_31_out = history_valid_31;
        history_pixel_0_0_out = history_pixel_0_0;
        history_pixel_0_1_out = history_pixel_0_1;
        history_pixel_0_2_out = history_pixel_0_2;
        history_pixel_0_3_out = history_pixel_0_3;
        history_pixel_0_4_out = history_pixel_0_4;
        history_pixel_0_5_out = history_pixel_0_5;
        history_pixel_0_6_out = history_pixel_0_6;
        history_pixel_0_7_out = history_pixel_0_7;
        history_pixel_0_8_out = history_pixel_0_8;
        history_pixel_0_9_out = history_pixel_0_9;
        history_pixel_0_10_out = history_pixel_0_10;
        history_pixel_0_11_out = history_pixel_0_11;
        history_pixel_0_12_out = history_pixel_0_12;
        history_pixel_0_13_out = history_pixel_0_13;
        history_pixel_0_14_out = history_pixel_0_14;
        history_pixel_0_15_out = history_pixel_0_15;
        history_pixel_0_16_out = history_pixel_0_16;
        history_pixel_0_17_out = history_pixel_0_17;
        history_pixel_0_18_out = history_pixel_0_18;
        history_pixel_0_19_out = history_pixel_0_19;
        history_pixel_0_20_out = history_pixel_0_20;
        history_pixel_0_21_out = history_pixel_0_21;
        history_pixel_0_22_out = history_pixel_0_22;
        history_pixel_0_23_out = history_pixel_0_23;
        history_pixel_0_24_out = history_pixel_0_24;
        history_pixel_0_25_out = history_pixel_0_25;
        history_pixel_0_26_out = history_pixel_0_26;
        history_pixel_0_27_out = history_pixel_0_27;
        history_pixel_0_28_out = history_pixel_0_28;
        history_pixel_0_29_out = history_pixel_0_29;
        history_pixel_0_30_out = history_pixel_0_30;
        history_pixel_0_31_out = history_pixel_0_31;
        history_pixel_1_0_out = history_pixel_1_0;
        history_pixel_1_1_out = history_pixel_1_1;
        history_pixel_1_2_out = history_pixel_1_2;
        history_pixel_1_3_out = history_pixel_1_3;
        history_pixel_1_4_out = history_pixel_1_4;
        history_pixel_1_5_out = history_pixel_1_5;
        history_pixel_1_6_out = history_pixel_1_6;
        history_pixel_1_7_out = history_pixel_1_7;
        history_pixel_1_8_out = history_pixel_1_8;
        history_pixel_1_9_out = history_pixel_1_9;
        history_pixel_1_10_out = history_pixel_1_10;
        history_pixel_1_11_out = history_pixel_1_11;
        history_pixel_1_12_out = history_pixel_1_12;
        history_pixel_1_13_out = history_pixel_1_13;
        history_pixel_1_14_out = history_pixel_1_14;
        history_pixel_1_15_out = history_pixel_1_15;
        history_pixel_1_16_out = history_pixel_1_16;
        history_pixel_1_17_out = history_pixel_1_17;
        history_pixel_1_18_out = history_pixel_1_18;
        history_pixel_1_19_out = history_pixel_1_19;
        history_pixel_1_20_out = history_pixel_1_20;
        history_pixel_1_21_out = history_pixel_1_21;
        history_pixel_1_22_out = history_pixel_1_22;
        history_pixel_1_23_out = history_pixel_1_23;
        history_pixel_1_24_out = history_pixel_1_24;
        history_pixel_1_25_out = history_pixel_1_25;
        history_pixel_1_26_out = history_pixel_1_26;
        history_pixel_1_27_out = history_pixel_1_27;
        history_pixel_1_28_out = history_pixel_1_28;
        history_pixel_1_29_out = history_pixel_1_29;
        history_pixel_1_30_out = history_pixel_1_30;
        history_pixel_1_31_out = history_pixel_1_31;
        history_pixel_2_0_out = history_pixel_2_0;
        history_pixel_2_1_out = history_pixel_2_1;
        history_pixel_2_2_out = history_pixel_2_2;
        history_pixel_2_3_out = history_pixel_2_3;
        history_pixel_2_4_out = history_pixel_2_4;
        history_pixel_2_5_out = history_pixel_2_5;
        history_pixel_2_6_out = history_pixel_2_6;
        history_pixel_2_7_out = history_pixel_2_7;
        history_pixel_2_8_out = history_pixel_2_8;
        history_pixel_2_9_out = history_pixel_2_9;
        history_pixel_2_10_out = history_pixel_2_10;
        history_pixel_2_11_out = history_pixel_2_11;
        history_pixel_2_12_out = history_pixel_2_12;
        history_pixel_2_13_out = history_pixel_2_13;
        history_pixel_2_14_out = history_pixel_2_14;
        history_pixel_2_15_out = history_pixel_2_15;
        history_pixel_2_16_out = history_pixel_2_16;
        history_pixel_2_17_out = history_pixel_2_17;
        history_pixel_2_18_out = history_pixel_2_18;
        history_pixel_2_19_out = history_pixel_2_19;
        history_pixel_2_20_out = history_pixel_2_20;
        history_pixel_2_21_out = history_pixel_2_21;
        history_pixel_2_22_out = history_pixel_2_22;
        history_pixel_2_23_out = history_pixel_2_23;
        history_pixel_2_24_out = history_pixel_2_24;
        history_pixel_2_25_out = history_pixel_2_25;
        history_pixel_2_26_out = history_pixel_2_26;
        history_pixel_2_27_out = history_pixel_2_27;
        history_pixel_2_28_out = history_pixel_2_28;
        history_pixel_2_29_out = history_pixel_2_29;
        history_pixel_2_30_out = history_pixel_2_30;
        history_pixel_2_31_out = history_pixel_2_31;
        history_pixel_3_0_out = history_pixel_3_0;
        history_pixel_3_1_out = history_pixel_3_1;
        history_pixel_3_2_out = history_pixel_3_2;
        history_pixel_3_3_out = history_pixel_3_3;
        history_pixel_3_4_out = history_pixel_3_4;
        history_pixel_3_5_out = history_pixel_3_5;
        history_pixel_3_6_out = history_pixel_3_6;
        history_pixel_3_7_out = history_pixel_3_7;
        history_pixel_3_8_out = history_pixel_3_8;
        history_pixel_3_9_out = history_pixel_3_9;
        history_pixel_3_10_out = history_pixel_3_10;
        history_pixel_3_11_out = history_pixel_3_11;
        history_pixel_3_12_out = history_pixel_3_12;
        history_pixel_3_13_out = history_pixel_3_13;
        history_pixel_3_14_out = history_pixel_3_14;
        history_pixel_3_15_out = history_pixel_3_15;
        history_pixel_3_16_out = history_pixel_3_16;
        history_pixel_3_17_out = history_pixel_3_17;
        history_pixel_3_18_out = history_pixel_3_18;
        history_pixel_3_19_out = history_pixel_3_19;
        history_pixel_3_20_out = history_pixel_3_20;
        history_pixel_3_21_out = history_pixel_3_21;
        history_pixel_3_22_out = history_pixel_3_22;
        history_pixel_3_23_out = history_pixel_3_23;
        history_pixel_3_24_out = history_pixel_3_24;
        history_pixel_3_25_out = history_pixel_3_25;
        history_pixel_3_26_out = history_pixel_3_26;
        history_pixel_3_27_out = history_pixel_3_27;
        history_pixel_3_28_out = history_pixel_3_28;
        history_pixel_3_29_out = history_pixel_3_29;
        history_pixel_3_30_out = history_pixel_3_30;
        history_pixel_3_31_out = history_pixel_3_31;
        found_i = 1'b0;
        location_i = first_line_i ? 5'd31 : 5'd24;
        if (!found_i && (6'd0 < reserved_i)) begin
            if (history_valid_0 == 0) begin
                location_i = 5'd0;
                found_i = 1'b1;
            end else if (active_selection_i && (((state_num_components <= 32'sd0) || (lookup_0_0_i == recon_0)) && ((state_num_components <= 32'sd1) || (lookup_0_1_i == recon_1)) && ((state_num_components <= 32'sd2) || (lookup_0_2_i == recon_2)) && ((state_num_components <= 32'sd3) || (lookup_0_3_i == recon_3)))) begin
                location_i = 5'd0;
                found_i = 1'b1;
            end
        end
        if (!found_i && (6'd1 < reserved_i)) begin
            if (history_valid_1 == 0) begin
                location_i = 5'd1;
                found_i = 1'b1;
            end else if (active_selection_i && (((state_num_components <= 32'sd0) || (lookup_1_0_i == recon_0)) && ((state_num_components <= 32'sd1) || (lookup_1_1_i == recon_1)) && ((state_num_components <= 32'sd2) || (lookup_1_2_i == recon_2)) && ((state_num_components <= 32'sd3) || (lookup_1_3_i == recon_3)))) begin
                location_i = 5'd1;
                found_i = 1'b1;
            end
        end
        if (!found_i && (6'd2 < reserved_i)) begin
            if (history_valid_2 == 0) begin
                location_i = 5'd2;
                found_i = 1'b1;
            end else if (active_selection_i && (((state_num_components <= 32'sd0) || (lookup_2_0_i == recon_0)) && ((state_num_components <= 32'sd1) || (lookup_2_1_i == recon_1)) && ((state_num_components <= 32'sd2) || (lookup_2_2_i == recon_2)) && ((state_num_components <= 32'sd3) || (lookup_2_3_i == recon_3)))) begin
                location_i = 5'd2;
                found_i = 1'b1;
            end
        end
        if (!found_i && (6'd3 < reserved_i)) begin
            if (history_valid_3 == 0) begin
                location_i = 5'd3;
                found_i = 1'b1;
            end else if (active_selection_i && (((state_num_components <= 32'sd0) || (lookup_3_0_i == recon_0)) && ((state_num_components <= 32'sd1) || (lookup_3_1_i == recon_1)) && ((state_num_components <= 32'sd2) || (lookup_3_2_i == recon_2)) && ((state_num_components <= 32'sd3) || (lookup_3_3_i == recon_3)))) begin
                location_i = 5'd3;
                found_i = 1'b1;
            end
        end
        if (!found_i && (6'd4 < reserved_i)) begin
            if (history_valid_4 == 0) begin
                location_i = 5'd4;
                found_i = 1'b1;
            end else if (active_selection_i && (((state_num_components <= 32'sd0) || (lookup_4_0_i == recon_0)) && ((state_num_components <= 32'sd1) || (lookup_4_1_i == recon_1)) && ((state_num_components <= 32'sd2) || (lookup_4_2_i == recon_2)) && ((state_num_components <= 32'sd3) || (lookup_4_3_i == recon_3)))) begin
                location_i = 5'd4;
                found_i = 1'b1;
            end
        end
        if (!found_i && (6'd5 < reserved_i)) begin
            if (history_valid_5 == 0) begin
                location_i = 5'd5;
                found_i = 1'b1;
            end else if (active_selection_i && (((state_num_components <= 32'sd0) || (lookup_5_0_i == recon_0)) && ((state_num_components <= 32'sd1) || (lookup_5_1_i == recon_1)) && ((state_num_components <= 32'sd2) || (lookup_5_2_i == recon_2)) && ((state_num_components <= 32'sd3) || (lookup_5_3_i == recon_3)))) begin
                location_i = 5'd5;
                found_i = 1'b1;
            end
        end
        if (!found_i && (6'd6 < reserved_i)) begin
            if (history_valid_6 == 0) begin
                location_i = 5'd6;
                found_i = 1'b1;
            end else if (active_selection_i && (((state_num_components <= 32'sd0) || (lookup_6_0_i == recon_0)) && ((state_num_components <= 32'sd1) || (lookup_6_1_i == recon_1)) && ((state_num_components <= 32'sd2) || (lookup_6_2_i == recon_2)) && ((state_num_components <= 32'sd3) || (lookup_6_3_i == recon_3)))) begin
                location_i = 5'd6;
                found_i = 1'b1;
            end
        end
        if (!found_i && (6'd7 < reserved_i)) begin
            if (history_valid_7 == 0) begin
                location_i = 5'd7;
                found_i = 1'b1;
            end else if (active_selection_i && (((state_num_components <= 32'sd0) || (lookup_7_0_i == recon_0)) && ((state_num_components <= 32'sd1) || (lookup_7_1_i == recon_1)) && ((state_num_components <= 32'sd2) || (lookup_7_2_i == recon_2)) && ((state_num_components <= 32'sd3) || (lookup_7_3_i == recon_3)))) begin
                location_i = 5'd7;
                found_i = 1'b1;
            end
        end
        if (!found_i && (6'd8 < reserved_i)) begin
            if (history_valid_8 == 0) begin
                location_i = 5'd8;
                found_i = 1'b1;
            end else if (active_selection_i && (((state_num_components <= 32'sd0) || (lookup_8_0_i == recon_0)) && ((state_num_components <= 32'sd1) || (lookup_8_1_i == recon_1)) && ((state_num_components <= 32'sd2) || (lookup_8_2_i == recon_2)) && ((state_num_components <= 32'sd3) || (lookup_8_3_i == recon_3)))) begin
                location_i = 5'd8;
                found_i = 1'b1;
            end
        end
        if (!found_i && (6'd9 < reserved_i)) begin
            if (history_valid_9 == 0) begin
                location_i = 5'd9;
                found_i = 1'b1;
            end else if (active_selection_i && (((state_num_components <= 32'sd0) || (lookup_9_0_i == recon_0)) && ((state_num_components <= 32'sd1) || (lookup_9_1_i == recon_1)) && ((state_num_components <= 32'sd2) || (lookup_9_2_i == recon_2)) && ((state_num_components <= 32'sd3) || (lookup_9_3_i == recon_3)))) begin
                location_i = 5'd9;
                found_i = 1'b1;
            end
        end
        if (!found_i && (6'd10 < reserved_i)) begin
            if (history_valid_10 == 0) begin
                location_i = 5'd10;
                found_i = 1'b1;
            end else if (active_selection_i && (((state_num_components <= 32'sd0) || (lookup_10_0_i == recon_0)) && ((state_num_components <= 32'sd1) || (lookup_10_1_i == recon_1)) && ((state_num_components <= 32'sd2) || (lookup_10_2_i == recon_2)) && ((state_num_components <= 32'sd3) || (lookup_10_3_i == recon_3)))) begin
                location_i = 5'd10;
                found_i = 1'b1;
            end
        end
        if (!found_i && (6'd11 < reserved_i)) begin
            if (history_valid_11 == 0) begin
                location_i = 5'd11;
                found_i = 1'b1;
            end else if (active_selection_i && (((state_num_components <= 32'sd0) || (lookup_11_0_i == recon_0)) && ((state_num_components <= 32'sd1) || (lookup_11_1_i == recon_1)) && ((state_num_components <= 32'sd2) || (lookup_11_2_i == recon_2)) && ((state_num_components <= 32'sd3) || (lookup_11_3_i == recon_3)))) begin
                location_i = 5'd11;
                found_i = 1'b1;
            end
        end
        if (!found_i && (6'd12 < reserved_i)) begin
            if (history_valid_12 == 0) begin
                location_i = 5'd12;
                found_i = 1'b1;
            end else if (active_selection_i && (((state_num_components <= 32'sd0) || (lookup_12_0_i == recon_0)) && ((state_num_components <= 32'sd1) || (lookup_12_1_i == recon_1)) && ((state_num_components <= 32'sd2) || (lookup_12_2_i == recon_2)) && ((state_num_components <= 32'sd3) || (lookup_12_3_i == recon_3)))) begin
                location_i = 5'd12;
                found_i = 1'b1;
            end
        end
        if (!found_i && (6'd13 < reserved_i)) begin
            if (history_valid_13 == 0) begin
                location_i = 5'd13;
                found_i = 1'b1;
            end else if (active_selection_i && (((state_num_components <= 32'sd0) || (lookup_13_0_i == recon_0)) && ((state_num_components <= 32'sd1) || (lookup_13_1_i == recon_1)) && ((state_num_components <= 32'sd2) || (lookup_13_2_i == recon_2)) && ((state_num_components <= 32'sd3) || (lookup_13_3_i == recon_3)))) begin
                location_i = 5'd13;
                found_i = 1'b1;
            end
        end
        if (!found_i && (6'd14 < reserved_i)) begin
            if (history_valid_14 == 0) begin
                location_i = 5'd14;
                found_i = 1'b1;
            end else if (active_selection_i && (((state_num_components <= 32'sd0) || (lookup_14_0_i == recon_0)) && ((state_num_components <= 32'sd1) || (lookup_14_1_i == recon_1)) && ((state_num_components <= 32'sd2) || (lookup_14_2_i == recon_2)) && ((state_num_components <= 32'sd3) || (lookup_14_3_i == recon_3)))) begin
                location_i = 5'd14;
                found_i = 1'b1;
            end
        end
        if (!found_i && (6'd15 < reserved_i)) begin
            if (history_valid_15 == 0) begin
                location_i = 5'd15;
                found_i = 1'b1;
            end else if (active_selection_i && (((state_num_components <= 32'sd0) || (lookup_15_0_i == recon_0)) && ((state_num_components <= 32'sd1) || (lookup_15_1_i == recon_1)) && ((state_num_components <= 32'sd2) || (lookup_15_2_i == recon_2)) && ((state_num_components <= 32'sd3) || (lookup_15_3_i == recon_3)))) begin
                location_i = 5'd15;
                found_i = 1'b1;
            end
        end
        if (!found_i && (6'd16 < reserved_i)) begin
            if (history_valid_16 == 0) begin
                location_i = 5'd16;
                found_i = 1'b1;
            end else if (active_selection_i && (((state_num_components <= 32'sd0) || (lookup_16_0_i == recon_0)) && ((state_num_components <= 32'sd1) || (lookup_16_1_i == recon_1)) && ((state_num_components <= 32'sd2) || (lookup_16_2_i == recon_2)) && ((state_num_components <= 32'sd3) || (lookup_16_3_i == recon_3)))) begin
                location_i = 5'd16;
                found_i = 1'b1;
            end
        end
        if (!found_i && (6'd17 < reserved_i)) begin
            if (history_valid_17 == 0) begin
                location_i = 5'd17;
                found_i = 1'b1;
            end else if (active_selection_i && (((state_num_components <= 32'sd0) || (lookup_17_0_i == recon_0)) && ((state_num_components <= 32'sd1) || (lookup_17_1_i == recon_1)) && ((state_num_components <= 32'sd2) || (lookup_17_2_i == recon_2)) && ((state_num_components <= 32'sd3) || (lookup_17_3_i == recon_3)))) begin
                location_i = 5'd17;
                found_i = 1'b1;
            end
        end
        if (!found_i && (6'd18 < reserved_i)) begin
            if (history_valid_18 == 0) begin
                location_i = 5'd18;
                found_i = 1'b1;
            end else if (active_selection_i && (((state_num_components <= 32'sd0) || (lookup_18_0_i == recon_0)) && ((state_num_components <= 32'sd1) || (lookup_18_1_i == recon_1)) && ((state_num_components <= 32'sd2) || (lookup_18_2_i == recon_2)) && ((state_num_components <= 32'sd3) || (lookup_18_3_i == recon_3)))) begin
                location_i = 5'd18;
                found_i = 1'b1;
            end
        end
        if (!found_i && (6'd19 < reserved_i)) begin
            if (history_valid_19 == 0) begin
                location_i = 5'd19;
                found_i = 1'b1;
            end else if (active_selection_i && (((state_num_components <= 32'sd0) || (lookup_19_0_i == recon_0)) && ((state_num_components <= 32'sd1) || (lookup_19_1_i == recon_1)) && ((state_num_components <= 32'sd2) || (lookup_19_2_i == recon_2)) && ((state_num_components <= 32'sd3) || (lookup_19_3_i == recon_3)))) begin
                location_i = 5'd19;
                found_i = 1'b1;
            end
        end
        if (!found_i && (6'd20 < reserved_i)) begin
            if (history_valid_20 == 0) begin
                location_i = 5'd20;
                found_i = 1'b1;
            end else if (active_selection_i && (((state_num_components <= 32'sd0) || (lookup_20_0_i == recon_0)) && ((state_num_components <= 32'sd1) || (lookup_20_1_i == recon_1)) && ((state_num_components <= 32'sd2) || (lookup_20_2_i == recon_2)) && ((state_num_components <= 32'sd3) || (lookup_20_3_i == recon_3)))) begin
                location_i = 5'd20;
                found_i = 1'b1;
            end
        end
        if (!found_i && (6'd21 < reserved_i)) begin
            if (history_valid_21 == 0) begin
                location_i = 5'd21;
                found_i = 1'b1;
            end else if (active_selection_i && (((state_num_components <= 32'sd0) || (lookup_21_0_i == recon_0)) && ((state_num_components <= 32'sd1) || (lookup_21_1_i == recon_1)) && ((state_num_components <= 32'sd2) || (lookup_21_2_i == recon_2)) && ((state_num_components <= 32'sd3) || (lookup_21_3_i == recon_3)))) begin
                location_i = 5'd21;
                found_i = 1'b1;
            end
        end
        if (!found_i && (6'd22 < reserved_i)) begin
            if (history_valid_22 == 0) begin
                location_i = 5'd22;
                found_i = 1'b1;
            end else if (active_selection_i && (((state_num_components <= 32'sd0) || (lookup_22_0_i == recon_0)) && ((state_num_components <= 32'sd1) || (lookup_22_1_i == recon_1)) && ((state_num_components <= 32'sd2) || (lookup_22_2_i == recon_2)) && ((state_num_components <= 32'sd3) || (lookup_22_3_i == recon_3)))) begin
                location_i = 5'd22;
                found_i = 1'b1;
            end
        end
        if (!found_i && (6'd23 < reserved_i)) begin
            if (history_valid_23 == 0) begin
                location_i = 5'd23;
                found_i = 1'b1;
            end else if (active_selection_i && (((state_num_components <= 32'sd0) || (lookup_23_0_i == recon_0)) && ((state_num_components <= 32'sd1) || (lookup_23_1_i == recon_1)) && ((state_num_components <= 32'sd2) || (lookup_23_2_i == recon_2)) && ((state_num_components <= 32'sd3) || (lookup_23_3_i == recon_3)))) begin
                location_i = 5'd23;
                found_i = 1'b1;
            end
        end
        if (!found_i && (6'd24 < reserved_i)) begin
            if (history_valid_24 == 0) begin
                location_i = 5'd24;
                found_i = 1'b1;
            end else if (active_selection_i && (((state_num_components <= 32'sd0) || (lookup_24_0_i == recon_0)) && ((state_num_components <= 32'sd1) || (lookup_24_1_i == recon_1)) && ((state_num_components <= 32'sd2) || (lookup_24_2_i == recon_2)) && ((state_num_components <= 32'sd3) || (lookup_24_3_i == recon_3)))) begin
                location_i = 5'd24;
                found_i = 1'b1;
            end
        end
        if (!found_i && (6'd25 < reserved_i)) begin
            if (history_valid_25 == 0) begin
                location_i = 5'd25;
                found_i = 1'b1;
            end else if (active_selection_i && (((state_num_components <= 32'sd0) || (lookup_25_0_i == recon_0)) && ((state_num_components <= 32'sd1) || (lookup_25_1_i == recon_1)) && ((state_num_components <= 32'sd2) || (lookup_25_2_i == recon_2)) && ((state_num_components <= 32'sd3) || (lookup_25_3_i == recon_3)))) begin
                location_i = 5'd25;
                found_i = 1'b1;
            end
        end
        if (!found_i && (6'd26 < reserved_i)) begin
            if (history_valid_26 == 0) begin
                location_i = 5'd26;
                found_i = 1'b1;
            end else if (active_selection_i && (((state_num_components <= 32'sd0) || (lookup_26_0_i == recon_0)) && ((state_num_components <= 32'sd1) || (lookup_26_1_i == recon_1)) && ((state_num_components <= 32'sd2) || (lookup_26_2_i == recon_2)) && ((state_num_components <= 32'sd3) || (lookup_26_3_i == recon_3)))) begin
                location_i = 5'd26;
                found_i = 1'b1;
            end
        end
        if (!found_i && (6'd27 < reserved_i)) begin
            if (history_valid_27 == 0) begin
                location_i = 5'd27;
                found_i = 1'b1;
            end else if (active_selection_i && (((state_num_components <= 32'sd0) || (lookup_27_0_i == recon_0)) && ((state_num_components <= 32'sd1) || (lookup_27_1_i == recon_1)) && ((state_num_components <= 32'sd2) || (lookup_27_2_i == recon_2)) && ((state_num_components <= 32'sd3) || (lookup_27_3_i == recon_3)))) begin
                location_i = 5'd27;
                found_i = 1'b1;
            end
        end
        if (!found_i && (6'd28 < reserved_i)) begin
            if (history_valid_28 == 0) begin
                location_i = 5'd28;
                found_i = 1'b1;
            end else if (active_selection_i && (((state_num_components <= 32'sd0) || (lookup_28_0_i == recon_0)) && ((state_num_components <= 32'sd1) || (lookup_28_1_i == recon_1)) && ((state_num_components <= 32'sd2) || (lookup_28_2_i == recon_2)) && ((state_num_components <= 32'sd3) || (lookup_28_3_i == recon_3)))) begin
                location_i = 5'd28;
                found_i = 1'b1;
            end
        end
        if (!found_i && (6'd29 < reserved_i)) begin
            if (history_valid_29 == 0) begin
                location_i = 5'd29;
                found_i = 1'b1;
            end else if (active_selection_i && (((state_num_components <= 32'sd0) || (lookup_29_0_i == recon_0)) && ((state_num_components <= 32'sd1) || (lookup_29_1_i == recon_1)) && ((state_num_components <= 32'sd2) || (lookup_29_2_i == recon_2)) && ((state_num_components <= 32'sd3) || (lookup_29_3_i == recon_3)))) begin
                location_i = 5'd29;
                found_i = 1'b1;
            end
        end
        if (!found_i && (6'd30 < reserved_i)) begin
            if (history_valid_30 == 0) begin
                location_i = 5'd30;
                found_i = 1'b1;
            end else if (active_selection_i && (((state_num_components <= 32'sd0) || (lookup_30_0_i == recon_0)) && ((state_num_components <= 32'sd1) || (lookup_30_1_i == recon_1)) && ((state_num_components <= 32'sd2) || (lookup_30_2_i == recon_2)) && ((state_num_components <= 32'sd3) || (lookup_30_3_i == recon_3)))) begin
                location_i = 5'd30;
                found_i = 1'b1;
            end
        end
        if (!found_i && (6'd31 < reserved_i)) begin
            if (history_valid_31 == 0) begin
                location_i = 5'd31;
                found_i = 1'b1;
            end else if (active_selection_i && (((state_num_components <= 32'sd0) || (lookup_31_0_i == recon_0)) && ((state_num_components <= 32'sd1) || (lookup_31_1_i == recon_1)) && ((state_num_components <= 32'sd2) || (lookup_31_2_i == recon_2)) && ((state_num_components <= 32'sd3) || (lookup_31_3_i == recon_3)))) begin
                location_i = 5'd31;
                found_i = 1'b1;
            end
        end
        if (state_num_components > 32'sd0) begin
            history_valid_0_out = 32'sd1;
            if (location_i == 5'd0)
                history_valid_0_out = 32'sd1;
            if (location_i == 5'd1)
                history_valid_1_out = 32'sd1;
            if (location_i == 5'd2)
                history_valid_2_out = 32'sd1;
            if (location_i == 5'd3)
                history_valid_3_out = 32'sd1;
            if (location_i == 5'd4)
                history_valid_4_out = 32'sd1;
            if (location_i == 5'd5)
                history_valid_5_out = 32'sd1;
            if (location_i == 5'd6)
                history_valid_6_out = 32'sd1;
            if (location_i == 5'd7)
                history_valid_7_out = 32'sd1;
            if (location_i == 5'd8)
                history_valid_8_out = 32'sd1;
            if (location_i == 5'd9)
                history_valid_9_out = 32'sd1;
            if (location_i == 5'd10)
                history_valid_10_out = 32'sd1;
            if (location_i == 5'd11)
                history_valid_11_out = 32'sd1;
            if (location_i == 5'd12)
                history_valid_12_out = 32'sd1;
            if (location_i == 5'd13)
                history_valid_13_out = 32'sd1;
            if (location_i == 5'd14)
                history_valid_14_out = 32'sd1;
            if (location_i == 5'd15)
                history_valid_15_out = 32'sd1;
            if (location_i == 5'd16)
                history_valid_16_out = 32'sd1;
            if (location_i == 5'd17)
                history_valid_17_out = 32'sd1;
            if (location_i == 5'd18)
                history_valid_18_out = 32'sd1;
            if (location_i == 5'd19)
                history_valid_19_out = 32'sd1;
            if (location_i == 5'd20)
                history_valid_20_out = 32'sd1;
            if (location_i == 5'd21)
                history_valid_21_out = 32'sd1;
            if (location_i == 5'd22)
                history_valid_22_out = 32'sd1;
            if (location_i == 5'd23)
                history_valid_23_out = 32'sd1;
            if (location_i == 5'd24)
                history_valid_24_out = 32'sd1;
            if (location_i == 5'd25)
                history_valid_25_out = 32'sd1;
            if (location_i == 5'd26)
                history_valid_26_out = 32'sd1;
            if (location_i == 5'd27)
                history_valid_27_out = 32'sd1;
            if (location_i == 5'd28)
                history_valid_28_out = 32'sd1;
            if (location_i == 5'd29)
                history_valid_29_out = 32'sd1;
            if (location_i == 5'd30)
                history_valid_30_out = 32'sd1;
            if (location_i == 5'd31)
                history_valid_31_out = 32'sd1;
        end
        if (state_num_components > 32'sd0) begin
            history_pixel_0_0_out = recon_0;
            if (location_i >= 5'd1)
                history_pixel_0_1_out = history_pixel_0_0;
            if (location_i >= 5'd2)
                history_pixel_0_2_out = history_pixel_0_1;
            if (location_i >= 5'd3)
                history_pixel_0_3_out = history_pixel_0_2;
            if (location_i >= 5'd4)
                history_pixel_0_4_out = history_pixel_0_3;
            if (location_i >= 5'd5)
                history_pixel_0_5_out = history_pixel_0_4;
            if (location_i >= 5'd6)
                history_pixel_0_6_out = history_pixel_0_5;
            if (location_i >= 5'd7)
                history_pixel_0_7_out = history_pixel_0_6;
            if (location_i >= 5'd8)
                history_pixel_0_8_out = history_pixel_0_7;
            if (location_i >= 5'd9)
                history_pixel_0_9_out = history_pixel_0_8;
            if (location_i >= 5'd10)
                history_pixel_0_10_out = history_pixel_0_9;
            if (location_i >= 5'd11)
                history_pixel_0_11_out = history_pixel_0_10;
            if (location_i >= 5'd12)
                history_pixel_0_12_out = history_pixel_0_11;
            if (location_i >= 5'd13)
                history_pixel_0_13_out = history_pixel_0_12;
            if (location_i >= 5'd14)
                history_pixel_0_14_out = history_pixel_0_13;
            if (location_i >= 5'd15)
                history_pixel_0_15_out = history_pixel_0_14;
            if (location_i >= 5'd16)
                history_pixel_0_16_out = history_pixel_0_15;
            if (location_i >= 5'd17)
                history_pixel_0_17_out = history_pixel_0_16;
            if (location_i >= 5'd18)
                history_pixel_0_18_out = history_pixel_0_17;
            if (location_i >= 5'd19)
                history_pixel_0_19_out = history_pixel_0_18;
            if (location_i >= 5'd20)
                history_pixel_0_20_out = history_pixel_0_19;
            if (location_i >= 5'd21)
                history_pixel_0_21_out = history_pixel_0_20;
            if (location_i >= 5'd22)
                history_pixel_0_22_out = history_pixel_0_21;
            if (location_i >= 5'd23)
                history_pixel_0_23_out = history_pixel_0_22;
            if (location_i >= 5'd24)
                history_pixel_0_24_out = history_pixel_0_23;
            if (location_i >= 5'd25)
                history_pixel_0_25_out = history_pixel_0_24;
            if (location_i >= 5'd26)
                history_pixel_0_26_out = history_pixel_0_25;
            if (location_i >= 5'd27)
                history_pixel_0_27_out = history_pixel_0_26;
            if (location_i >= 5'd28)
                history_pixel_0_28_out = history_pixel_0_27;
            if (location_i >= 5'd29)
                history_pixel_0_29_out = history_pixel_0_28;
            if (location_i >= 5'd30)
                history_pixel_0_30_out = history_pixel_0_29;
            if (location_i >= 5'd31)
                history_pixel_0_31_out = history_pixel_0_30;
        end
        if (state_num_components > 32'sd1) begin
            history_pixel_1_0_out = recon_1;
            if (location_i >= 5'd1)
                history_pixel_1_1_out = history_pixel_1_0;
            if (location_i >= 5'd2)
                history_pixel_1_2_out = history_pixel_1_1;
            if (location_i >= 5'd3)
                history_pixel_1_3_out = history_pixel_1_2;
            if (location_i >= 5'd4)
                history_pixel_1_4_out = history_pixel_1_3;
            if (location_i >= 5'd5)
                history_pixel_1_5_out = history_pixel_1_4;
            if (location_i >= 5'd6)
                history_pixel_1_6_out = history_pixel_1_5;
            if (location_i >= 5'd7)
                history_pixel_1_7_out = history_pixel_1_6;
            if (location_i >= 5'd8)
                history_pixel_1_8_out = history_pixel_1_7;
            if (location_i >= 5'd9)
                history_pixel_1_9_out = history_pixel_1_8;
            if (location_i >= 5'd10)
                history_pixel_1_10_out = history_pixel_1_9;
            if (location_i >= 5'd11)
                history_pixel_1_11_out = history_pixel_1_10;
            if (location_i >= 5'd12)
                history_pixel_1_12_out = history_pixel_1_11;
            if (location_i >= 5'd13)
                history_pixel_1_13_out = history_pixel_1_12;
            if (location_i >= 5'd14)
                history_pixel_1_14_out = history_pixel_1_13;
            if (location_i >= 5'd15)
                history_pixel_1_15_out = history_pixel_1_14;
            if (location_i >= 5'd16)
                history_pixel_1_16_out = history_pixel_1_15;
            if (location_i >= 5'd17)
                history_pixel_1_17_out = history_pixel_1_16;
            if (location_i >= 5'd18)
                history_pixel_1_18_out = history_pixel_1_17;
            if (location_i >= 5'd19)
                history_pixel_1_19_out = history_pixel_1_18;
            if (location_i >= 5'd20)
                history_pixel_1_20_out = history_pixel_1_19;
            if (location_i >= 5'd21)
                history_pixel_1_21_out = history_pixel_1_20;
            if (location_i >= 5'd22)
                history_pixel_1_22_out = history_pixel_1_21;
            if (location_i >= 5'd23)
                history_pixel_1_23_out = history_pixel_1_22;
            if (location_i >= 5'd24)
                history_pixel_1_24_out = history_pixel_1_23;
            if (location_i >= 5'd25)
                history_pixel_1_25_out = history_pixel_1_24;
            if (location_i >= 5'd26)
                history_pixel_1_26_out = history_pixel_1_25;
            if (location_i >= 5'd27)
                history_pixel_1_27_out = history_pixel_1_26;
            if (location_i >= 5'd28)
                history_pixel_1_28_out = history_pixel_1_27;
            if (location_i >= 5'd29)
                history_pixel_1_29_out = history_pixel_1_28;
            if (location_i >= 5'd30)
                history_pixel_1_30_out = history_pixel_1_29;
            if (location_i >= 5'd31)
                history_pixel_1_31_out = history_pixel_1_30;
        end
        if (state_num_components > 32'sd2) begin
            history_pixel_2_0_out = recon_2;
            if (location_i >= 5'd1)
                history_pixel_2_1_out = history_pixel_2_0;
            if (location_i >= 5'd2)
                history_pixel_2_2_out = history_pixel_2_1;
            if (location_i >= 5'd3)
                history_pixel_2_3_out = history_pixel_2_2;
            if (location_i >= 5'd4)
                history_pixel_2_4_out = history_pixel_2_3;
            if (location_i >= 5'd5)
                history_pixel_2_5_out = history_pixel_2_4;
            if (location_i >= 5'd6)
                history_pixel_2_6_out = history_pixel_2_5;
            if (location_i >= 5'd7)
                history_pixel_2_7_out = history_pixel_2_6;
            if (location_i >= 5'd8)
                history_pixel_2_8_out = history_pixel_2_7;
            if (location_i >= 5'd9)
                history_pixel_2_9_out = history_pixel_2_8;
            if (location_i >= 5'd10)
                history_pixel_2_10_out = history_pixel_2_9;
            if (location_i >= 5'd11)
                history_pixel_2_11_out = history_pixel_2_10;
            if (location_i >= 5'd12)
                history_pixel_2_12_out = history_pixel_2_11;
            if (location_i >= 5'd13)
                history_pixel_2_13_out = history_pixel_2_12;
            if (location_i >= 5'd14)
                history_pixel_2_14_out = history_pixel_2_13;
            if (location_i >= 5'd15)
                history_pixel_2_15_out = history_pixel_2_14;
            if (location_i >= 5'd16)
                history_pixel_2_16_out = history_pixel_2_15;
            if (location_i >= 5'd17)
                history_pixel_2_17_out = history_pixel_2_16;
            if (location_i >= 5'd18)
                history_pixel_2_18_out = history_pixel_2_17;
            if (location_i >= 5'd19)
                history_pixel_2_19_out = history_pixel_2_18;
            if (location_i >= 5'd20)
                history_pixel_2_20_out = history_pixel_2_19;
            if (location_i >= 5'd21)
                history_pixel_2_21_out = history_pixel_2_20;
            if (location_i >= 5'd22)
                history_pixel_2_22_out = history_pixel_2_21;
            if (location_i >= 5'd23)
                history_pixel_2_23_out = history_pixel_2_22;
            if (location_i >= 5'd24)
                history_pixel_2_24_out = history_pixel_2_23;
            if (location_i >= 5'd25)
                history_pixel_2_25_out = history_pixel_2_24;
            if (location_i >= 5'd26)
                history_pixel_2_26_out = history_pixel_2_25;
            if (location_i >= 5'd27)
                history_pixel_2_27_out = history_pixel_2_26;
            if (location_i >= 5'd28)
                history_pixel_2_28_out = history_pixel_2_27;
            if (location_i >= 5'd29)
                history_pixel_2_29_out = history_pixel_2_28;
            if (location_i >= 5'd30)
                history_pixel_2_30_out = history_pixel_2_29;
            if (location_i >= 5'd31)
                history_pixel_2_31_out = history_pixel_2_30;
        end
        if (state_num_components > 32'sd3) begin
            history_pixel_3_0_out = recon_3;
            if (location_i >= 5'd1)
                history_pixel_3_1_out = history_pixel_3_0;
            if (location_i >= 5'd2)
                history_pixel_3_2_out = history_pixel_3_1;
            if (location_i >= 5'd3)
                history_pixel_3_3_out = history_pixel_3_2;
            if (location_i >= 5'd4)
                history_pixel_3_4_out = history_pixel_3_3;
            if (location_i >= 5'd5)
                history_pixel_3_5_out = history_pixel_3_4;
            if (location_i >= 5'd6)
                history_pixel_3_6_out = history_pixel_3_5;
            if (location_i >= 5'd7)
                history_pixel_3_7_out = history_pixel_3_6;
            if (location_i >= 5'd8)
                history_pixel_3_8_out = history_pixel_3_7;
            if (location_i >= 5'd9)
                history_pixel_3_9_out = history_pixel_3_8;
            if (location_i >= 5'd10)
                history_pixel_3_10_out = history_pixel_3_9;
            if (location_i >= 5'd11)
                history_pixel_3_11_out = history_pixel_3_10;
            if (location_i >= 5'd12)
                history_pixel_3_12_out = history_pixel_3_11;
            if (location_i >= 5'd13)
                history_pixel_3_13_out = history_pixel_3_12;
            if (location_i >= 5'd14)
                history_pixel_3_14_out = history_pixel_3_13;
            if (location_i >= 5'd15)
                history_pixel_3_15_out = history_pixel_3_14;
            if (location_i >= 5'd16)
                history_pixel_3_16_out = history_pixel_3_15;
            if (location_i >= 5'd17)
                history_pixel_3_17_out = history_pixel_3_16;
            if (location_i >= 5'd18)
                history_pixel_3_18_out = history_pixel_3_17;
            if (location_i >= 5'd19)
                history_pixel_3_19_out = history_pixel_3_18;
            if (location_i >= 5'd20)
                history_pixel_3_20_out = history_pixel_3_19;
            if (location_i >= 5'd21)
                history_pixel_3_21_out = history_pixel_3_20;
            if (location_i >= 5'd22)
                history_pixel_3_22_out = history_pixel_3_21;
            if (location_i >= 5'd23)
                history_pixel_3_23_out = history_pixel_3_22;
            if (location_i >= 5'd24)
                history_pixel_3_24_out = history_pixel_3_23;
            if (location_i >= 5'd25)
                history_pixel_3_25_out = history_pixel_3_24;
            if (location_i >= 5'd26)
                history_pixel_3_26_out = history_pixel_3_25;
            if (location_i >= 5'd27)
                history_pixel_3_27_out = history_pixel_3_26;
            if (location_i >= 5'd28)
                history_pixel_3_28_out = history_pixel_3_27;
            if (location_i >= 5'd29)
                history_pixel_3_29_out = history_pixel_3_28;
            if (location_i >= 5'd30)
                history_pixel_3_30_out = history_pixel_3_29;
            if (location_i >= 5'd31)
                history_pixel_3_31_out = history_pixel_3_30;
        end
    end
endmodule

module updateichistory_decode_transition(
    input logic signed [31:0] hpos,
    input logic signed [31:0] vpos,
    input logic signed [31:0] cfg_native_420,
    input logic signed [31:0] cfg_slice_width,
    input logic signed [31:0] cfg_pic_width,
    input logic signed [31:0] state_hpos,
    input logic signed [31:0] state_vpos,
    input logic signed [31:0] state_num_components,
    input logic signed [31:0] state_pixels_in_group,
    input logic signed [31:0] state_is_encoder,
    input logic signed [31:0] state_ich_selected,
    input logic signed [31:0] state_prev_ich_selected,
    input logic [31:0] line_sample_0,
    input logic [31:0] line_sample_1,
    input logic [31:0] line_sample_2,
    input logic [31:0] line_sample_3,
    input logic signed [31:0] history_valid_0,
    input logic signed [31:0] history_valid_1,
    input logic signed [31:0] history_valid_2,
    input logic signed [31:0] history_valid_3,
    input logic signed [31:0] history_valid_4,
    input logic signed [31:0] history_valid_5,
    input logic signed [31:0] history_valid_6,
    input logic signed [31:0] history_valid_7,
    input logic signed [31:0] history_valid_8,
    input logic signed [31:0] history_valid_9,
    input logic signed [31:0] history_valid_10,
    input logic signed [31:0] history_valid_11,
    input logic signed [31:0] history_valid_12,
    input logic signed [31:0] history_valid_13,
    input logic signed [31:0] history_valid_14,
    input logic signed [31:0] history_valid_15,
    input logic signed [31:0] history_valid_16,
    input logic signed [31:0] history_valid_17,
    input logic signed [31:0] history_valid_18,
    input logic signed [31:0] history_valid_19,
    input logic signed [31:0] history_valid_20,
    input logic signed [31:0] history_valid_21,
    input logic signed [31:0] history_valid_22,
    input logic signed [31:0] history_valid_23,
    input logic signed [31:0] history_valid_24,
    input logic signed [31:0] history_valid_25,
    input logic signed [31:0] history_valid_26,
    input logic signed [31:0] history_valid_27,
    input logic signed [31:0] history_valid_28,
    input logic signed [31:0] history_valid_29,
    input logic signed [31:0] history_valid_30,
    input logic signed [31:0] history_valid_31,
    input logic [31:0] history_pixel_0_0,
    input logic [31:0] history_pixel_0_1,
    input logic [31:0] history_pixel_0_2,
    input logic [31:0] history_pixel_0_3,
    input logic [31:0] history_pixel_0_4,
    input logic [31:0] history_pixel_0_5,
    input logic [31:0] history_pixel_0_6,
    input logic [31:0] history_pixel_0_7,
    input logic [31:0] history_pixel_0_8,
    input logic [31:0] history_pixel_0_9,
    input logic [31:0] history_pixel_0_10,
    input logic [31:0] history_pixel_0_11,
    input logic [31:0] history_pixel_0_12,
    input logic [31:0] history_pixel_0_13,
    input logic [31:0] history_pixel_0_14,
    input logic [31:0] history_pixel_0_15,
    input logic [31:0] history_pixel_0_16,
    input logic [31:0] history_pixel_0_17,
    input logic [31:0] history_pixel_0_18,
    input logic [31:0] history_pixel_0_19,
    input logic [31:0] history_pixel_0_20,
    input logic [31:0] history_pixel_0_21,
    input logic [31:0] history_pixel_0_22,
    input logic [31:0] history_pixel_0_23,
    input logic [31:0] history_pixel_0_24,
    input logic [31:0] history_pixel_0_25,
    input logic [31:0] history_pixel_0_26,
    input logic [31:0] history_pixel_0_27,
    input logic [31:0] history_pixel_0_28,
    input logic [31:0] history_pixel_0_29,
    input logic [31:0] history_pixel_0_30,
    input logic [31:0] history_pixel_0_31,
    input logic [31:0] history_pixel_1_0,
    input logic [31:0] history_pixel_1_1,
    input logic [31:0] history_pixel_1_2,
    input logic [31:0] history_pixel_1_3,
    input logic [31:0] history_pixel_1_4,
    input logic [31:0] history_pixel_1_5,
    input logic [31:0] history_pixel_1_6,
    input logic [31:0] history_pixel_1_7,
    input logic [31:0] history_pixel_1_8,
    input logic [31:0] history_pixel_1_9,
    input logic [31:0] history_pixel_1_10,
    input logic [31:0] history_pixel_1_11,
    input logic [31:0] history_pixel_1_12,
    input logic [31:0] history_pixel_1_13,
    input logic [31:0] history_pixel_1_14,
    input logic [31:0] history_pixel_1_15,
    input logic [31:0] history_pixel_1_16,
    input logic [31:0] history_pixel_1_17,
    input logic [31:0] history_pixel_1_18,
    input logic [31:0] history_pixel_1_19,
    input logic [31:0] history_pixel_1_20,
    input logic [31:0] history_pixel_1_21,
    input logic [31:0] history_pixel_1_22,
    input logic [31:0] history_pixel_1_23,
    input logic [31:0] history_pixel_1_24,
    input logic [31:0] history_pixel_1_25,
    input logic [31:0] history_pixel_1_26,
    input logic [31:0] history_pixel_1_27,
    input logic [31:0] history_pixel_1_28,
    input logic [31:0] history_pixel_1_29,
    input logic [31:0] history_pixel_1_30,
    input logic [31:0] history_pixel_1_31,
    input logic [31:0] history_pixel_2_0,
    input logic [31:0] history_pixel_2_1,
    input logic [31:0] history_pixel_2_2,
    input logic [31:0] history_pixel_2_3,
    input logic [31:0] history_pixel_2_4,
    input logic [31:0] history_pixel_2_5,
    input logic [31:0] history_pixel_2_6,
    input logic [31:0] history_pixel_2_7,
    input logic [31:0] history_pixel_2_8,
    input logic [31:0] history_pixel_2_9,
    input logic [31:0] history_pixel_2_10,
    input logic [31:0] history_pixel_2_11,
    input logic [31:0] history_pixel_2_12,
    input logic [31:0] history_pixel_2_13,
    input logic [31:0] history_pixel_2_14,
    input logic [31:0] history_pixel_2_15,
    input logic [31:0] history_pixel_2_16,
    input logic [31:0] history_pixel_2_17,
    input logic [31:0] history_pixel_2_18,
    input logic [31:0] history_pixel_2_19,
    input logic [31:0] history_pixel_2_20,
    input logic [31:0] history_pixel_2_21,
    input logic [31:0] history_pixel_2_22,
    input logic [31:0] history_pixel_2_23,
    input logic [31:0] history_pixel_2_24,
    input logic [31:0] history_pixel_2_25,
    input logic [31:0] history_pixel_2_26,
    input logic [31:0] history_pixel_2_27,
    input logic [31:0] history_pixel_2_28,
    input logic [31:0] history_pixel_2_29,
    input logic [31:0] history_pixel_2_30,
    input logic [31:0] history_pixel_2_31,
    input logic [31:0] history_pixel_3_0,
    input logic [31:0] history_pixel_3_1,
    input logic [31:0] history_pixel_3_2,
    input logic [31:0] history_pixel_3_3,
    input logic [31:0] history_pixel_3_4,
    input logic [31:0] history_pixel_3_5,
    input logic [31:0] history_pixel_3_6,
    input logic [31:0] history_pixel_3_7,
    input logic [31:0] history_pixel_3_8,
    input logic [31:0] history_pixel_3_9,
    input logic [31:0] history_pixel_3_10,
    input logic [31:0] history_pixel_3_11,
    input logic [31:0] history_pixel_3_12,
    input logic [31:0] history_pixel_3_13,
    input logic [31:0] history_pixel_3_14,
    input logic [31:0] history_pixel_3_15,
    input logic [31:0] history_pixel_3_16,
    input logic [31:0] history_pixel_3_17,
    input logic [31:0] history_pixel_3_18,
    input logic [31:0] history_pixel_3_19,
    input logic [31:0] history_pixel_3_20,
    input logic [31:0] history_pixel_3_21,
    input logic [31:0] history_pixel_3_22,
    input logic [31:0] history_pixel_3_23,
    input logic [31:0] history_pixel_3_24,
    input logic [31:0] history_pixel_3_25,
    input logic [31:0] history_pixel_3_26,
    input logic [31:0] history_pixel_3_27,
    input logic [31:0] history_pixel_3_28,
    input logic [31:0] history_pixel_3_29,
    input logic [31:0] history_pixel_3_30,
    input logic [31:0] history_pixel_3_31,
    output logic signed [31:0] history_valid_0_out,
    output logic signed [31:0] history_valid_1_out,
    output logic signed [31:0] history_valid_2_out,
    output logic signed [31:0] history_valid_3_out,
    output logic signed [31:0] history_valid_4_out,
    output logic signed [31:0] history_valid_5_out,
    output logic signed [31:0] history_valid_6_out,
    output logic signed [31:0] history_valid_7_out,
    output logic signed [31:0] history_valid_8_out,
    output logic signed [31:0] history_valid_9_out,
    output logic signed [31:0] history_valid_10_out,
    output logic signed [31:0] history_valid_11_out,
    output logic signed [31:0] history_valid_12_out,
    output logic signed [31:0] history_valid_13_out,
    output logic signed [31:0] history_valid_14_out,
    output logic signed [31:0] history_valid_15_out,
    output logic signed [31:0] history_valid_16_out,
    output logic signed [31:0] history_valid_17_out,
    output logic signed [31:0] history_valid_18_out,
    output logic signed [31:0] history_valid_19_out,
    output logic signed [31:0] history_valid_20_out,
    output logic signed [31:0] history_valid_21_out,
    output logic signed [31:0] history_valid_22_out,
    output logic signed [31:0] history_valid_23_out,
    output logic signed [31:0] history_valid_24_out,
    output logic signed [31:0] history_valid_25_out,
    output logic signed [31:0] history_valid_26_out,
    output logic signed [31:0] history_valid_27_out,
    output logic signed [31:0] history_valid_28_out,
    output logic signed [31:0] history_valid_29_out,
    output logic signed [31:0] history_valid_30_out,
    output logic signed [31:0] history_valid_31_out,
    output logic [31:0] history_pixel_0_0_out,
    output logic [31:0] history_pixel_0_1_out,
    output logic [31:0] history_pixel_0_2_out,
    output logic [31:0] history_pixel_0_3_out,
    output logic [31:0] history_pixel_0_4_out,
    output logic [31:0] history_pixel_0_5_out,
    output logic [31:0] history_pixel_0_6_out,
    output logic [31:0] history_pixel_0_7_out,
    output logic [31:0] history_pixel_0_8_out,
    output logic [31:0] history_pixel_0_9_out,
    output logic [31:0] history_pixel_0_10_out,
    output logic [31:0] history_pixel_0_11_out,
    output logic [31:0] history_pixel_0_12_out,
    output logic [31:0] history_pixel_0_13_out,
    output logic [31:0] history_pixel_0_14_out,
    output logic [31:0] history_pixel_0_15_out,
    output logic [31:0] history_pixel_0_16_out,
    output logic [31:0] history_pixel_0_17_out,
    output logic [31:0] history_pixel_0_18_out,
    output logic [31:0] history_pixel_0_19_out,
    output logic [31:0] history_pixel_0_20_out,
    output logic [31:0] history_pixel_0_21_out,
    output logic [31:0] history_pixel_0_22_out,
    output logic [31:0] history_pixel_0_23_out,
    output logic [31:0] history_pixel_0_24_out,
    output logic [31:0] history_pixel_0_25_out,
    output logic [31:0] history_pixel_0_26_out,
    output logic [31:0] history_pixel_0_27_out,
    output logic [31:0] history_pixel_0_28_out,
    output logic [31:0] history_pixel_0_29_out,
    output logic [31:0] history_pixel_0_30_out,
    output logic [31:0] history_pixel_0_31_out,
    output logic [31:0] history_pixel_1_0_out,
    output logic [31:0] history_pixel_1_1_out,
    output logic [31:0] history_pixel_1_2_out,
    output logic [31:0] history_pixel_1_3_out,
    output logic [31:0] history_pixel_1_4_out,
    output logic [31:0] history_pixel_1_5_out,
    output logic [31:0] history_pixel_1_6_out,
    output logic [31:0] history_pixel_1_7_out,
    output logic [31:0] history_pixel_1_8_out,
    output logic [31:0] history_pixel_1_9_out,
    output logic [31:0] history_pixel_1_10_out,
    output logic [31:0] history_pixel_1_11_out,
    output logic [31:0] history_pixel_1_12_out,
    output logic [31:0] history_pixel_1_13_out,
    output logic [31:0] history_pixel_1_14_out,
    output logic [31:0] history_pixel_1_15_out,
    output logic [31:0] history_pixel_1_16_out,
    output logic [31:0] history_pixel_1_17_out,
    output logic [31:0] history_pixel_1_18_out,
    output logic [31:0] history_pixel_1_19_out,
    output logic [31:0] history_pixel_1_20_out,
    output logic [31:0] history_pixel_1_21_out,
    output logic [31:0] history_pixel_1_22_out,
    output logic [31:0] history_pixel_1_23_out,
    output logic [31:0] history_pixel_1_24_out,
    output logic [31:0] history_pixel_1_25_out,
    output logic [31:0] history_pixel_1_26_out,
    output logic [31:0] history_pixel_1_27_out,
    output logic [31:0] history_pixel_1_28_out,
    output logic [31:0] history_pixel_1_29_out,
    output logic [31:0] history_pixel_1_30_out,
    output logic [31:0] history_pixel_1_31_out,
    output logic [31:0] history_pixel_2_0_out,
    output logic [31:0] history_pixel_2_1_out,
    output logic [31:0] history_pixel_2_2_out,
    output logic [31:0] history_pixel_2_3_out,
    output logic [31:0] history_pixel_2_4_out,
    output logic [31:0] history_pixel_2_5_out,
    output logic [31:0] history_pixel_2_6_out,
    output logic [31:0] history_pixel_2_7_out,
    output logic [31:0] history_pixel_2_8_out,
    output logic [31:0] history_pixel_2_9_out,
    output logic [31:0] history_pixel_2_10_out,
    output logic [31:0] history_pixel_2_11_out,
    output logic [31:0] history_pixel_2_12_out,
    output logic [31:0] history_pixel_2_13_out,
    output logic [31:0] history_pixel_2_14_out,
    output logic [31:0] history_pixel_2_15_out,
    output logic [31:0] history_pixel_2_16_out,
    output logic [31:0] history_pixel_2_17_out,
    output logic [31:0] history_pixel_2_18_out,
    output logic [31:0] history_pixel_2_19_out,
    output logic [31:0] history_pixel_2_20_out,
    output logic [31:0] history_pixel_2_21_out,
    output logic [31:0] history_pixel_2_22_out,
    output logic [31:0] history_pixel_2_23_out,
    output logic [31:0] history_pixel_2_24_out,
    output logic [31:0] history_pixel_2_25_out,
    output logic [31:0] history_pixel_2_26_out,
    output logic [31:0] history_pixel_2_27_out,
    output logic [31:0] history_pixel_2_28_out,
    output logic [31:0] history_pixel_2_29_out,
    output logic [31:0] history_pixel_2_30_out,
    output logic [31:0] history_pixel_2_31_out,
    output logic [31:0] history_pixel_3_0_out,
    output logic [31:0] history_pixel_3_1_out,
    output logic [31:0] history_pixel_3_2_out,
    output logic [31:0] history_pixel_3_3_out,
    output logic [31:0] history_pixel_3_4_out,
    output logic [31:0] history_pixel_3_5_out,
    output logic [31:0] history_pixel_3_6_out,
    output logic [31:0] history_pixel_3_7_out,
    output logic [31:0] history_pixel_3_8_out,
    output logic [31:0] history_pixel_3_9_out,
    output logic [31:0] history_pixel_3_10_out,
    output logic [31:0] history_pixel_3_11_out,
    output logic [31:0] history_pixel_3_12_out,
    output logic [31:0] history_pixel_3_13_out,
    output logic [31:0] history_pixel_3_14_out,
    output logic [31:0] history_pixel_3_15_out,
    output logic [31:0] history_pixel_3_16_out,
    output logic [31:0] history_pixel_3_17_out,
    output logic [31:0] history_pixel_3_18_out,
    output logic [31:0] history_pixel_3_19_out,
    output logic [31:0] history_pixel_3_20_out,
    output logic [31:0] history_pixel_3_21_out,
    output logic [31:0] history_pixel_3_22_out,
    output logic [31:0] history_pixel_3_23_out,
    output logic [31:0] history_pixel_3_24_out,
    output logic [31:0] history_pixel_3_25_out,
    output logic [31:0] history_pixel_3_26_out,
    output logic [31:0] history_pixel_3_27_out,
    output logic [31:0] history_pixel_3_28_out,
    output logic [31:0] history_pixel_3_29_out,
    output logic [31:0] history_pixel_3_30_out,
    output logic [31:0] history_pixel_3_31_out
);
    logic clear_history_i;
    logic update_history_i;
    logic signed [31:0] previous_hpos_i;
    logic signed [31:0] child_valid_0_i;
    logic signed [31:0] child_valid_1_i;
    logic signed [31:0] child_valid_2_i;
    logic signed [31:0] child_valid_3_i;
    logic signed [31:0] child_valid_4_i;
    logic signed [31:0] child_valid_5_i;
    logic signed [31:0] child_valid_6_i;
    logic signed [31:0] child_valid_7_i;
    logic signed [31:0] child_valid_8_i;
    logic signed [31:0] child_valid_9_i;
    logic signed [31:0] child_valid_10_i;
    logic signed [31:0] child_valid_11_i;
    logic signed [31:0] child_valid_12_i;
    logic signed [31:0] child_valid_13_i;
    logic signed [31:0] child_valid_14_i;
    logic signed [31:0] child_valid_15_i;
    logic signed [31:0] child_valid_16_i;
    logic signed [31:0] child_valid_17_i;
    logic signed [31:0] child_valid_18_i;
    logic signed [31:0] child_valid_19_i;
    logic signed [31:0] child_valid_20_i;
    logic signed [31:0] child_valid_21_i;
    logic signed [31:0] child_valid_22_i;
    logic signed [31:0] child_valid_23_i;
    logic signed [31:0] child_valid_24_i;
    logic signed [31:0] child_valid_25_i;
    logic signed [31:0] child_valid_26_i;
    logic signed [31:0] child_valid_27_i;
    logic signed [31:0] child_valid_28_i;
    logic signed [31:0] child_valid_29_i;
    logic signed [31:0] child_valid_30_i;
    logic signed [31:0] child_valid_31_i;
    logic [31:0] child_pixel_0_0_i;
    logic [31:0] child_pixel_0_1_i;
    logic [31:0] child_pixel_0_2_i;
    logic [31:0] child_pixel_0_3_i;
    logic [31:0] child_pixel_0_4_i;
    logic [31:0] child_pixel_0_5_i;
    logic [31:0] child_pixel_0_6_i;
    logic [31:0] child_pixel_0_7_i;
    logic [31:0] child_pixel_0_8_i;
    logic [31:0] child_pixel_0_9_i;
    logic [31:0] child_pixel_0_10_i;
    logic [31:0] child_pixel_0_11_i;
    logic [31:0] child_pixel_0_12_i;
    logic [31:0] child_pixel_0_13_i;
    logic [31:0] child_pixel_0_14_i;
    logic [31:0] child_pixel_0_15_i;
    logic [31:0] child_pixel_0_16_i;
    logic [31:0] child_pixel_0_17_i;
    logic [31:0] child_pixel_0_18_i;
    logic [31:0] child_pixel_0_19_i;
    logic [31:0] child_pixel_0_20_i;
    logic [31:0] child_pixel_0_21_i;
    logic [31:0] child_pixel_0_22_i;
    logic [31:0] child_pixel_0_23_i;
    logic [31:0] child_pixel_0_24_i;
    logic [31:0] child_pixel_0_25_i;
    logic [31:0] child_pixel_0_26_i;
    logic [31:0] child_pixel_0_27_i;
    logic [31:0] child_pixel_0_28_i;
    logic [31:0] child_pixel_0_29_i;
    logic [31:0] child_pixel_0_30_i;
    logic [31:0] child_pixel_0_31_i;
    logic [31:0] child_pixel_1_0_i;
    logic [31:0] child_pixel_1_1_i;
    logic [31:0] child_pixel_1_2_i;
    logic [31:0] child_pixel_1_3_i;
    logic [31:0] child_pixel_1_4_i;
    logic [31:0] child_pixel_1_5_i;
    logic [31:0] child_pixel_1_6_i;
    logic [31:0] child_pixel_1_7_i;
    logic [31:0] child_pixel_1_8_i;
    logic [31:0] child_pixel_1_9_i;
    logic [31:0] child_pixel_1_10_i;
    logic [31:0] child_pixel_1_11_i;
    logic [31:0] child_pixel_1_12_i;
    logic [31:0] child_pixel_1_13_i;
    logic [31:0] child_pixel_1_14_i;
    logic [31:0] child_pixel_1_15_i;
    logic [31:0] child_pixel_1_16_i;
    logic [31:0] child_pixel_1_17_i;
    logic [31:0] child_pixel_1_18_i;
    logic [31:0] child_pixel_1_19_i;
    logic [31:0] child_pixel_1_20_i;
    logic [31:0] child_pixel_1_21_i;
    logic [31:0] child_pixel_1_22_i;
    logic [31:0] child_pixel_1_23_i;
    logic [31:0] child_pixel_1_24_i;
    logic [31:0] child_pixel_1_25_i;
    logic [31:0] child_pixel_1_26_i;
    logic [31:0] child_pixel_1_27_i;
    logic [31:0] child_pixel_1_28_i;
    logic [31:0] child_pixel_1_29_i;
    logic [31:0] child_pixel_1_30_i;
    logic [31:0] child_pixel_1_31_i;
    logic [31:0] child_pixel_2_0_i;
    logic [31:0] child_pixel_2_1_i;
    logic [31:0] child_pixel_2_2_i;
    logic [31:0] child_pixel_2_3_i;
    logic [31:0] child_pixel_2_4_i;
    logic [31:0] child_pixel_2_5_i;
    logic [31:0] child_pixel_2_6_i;
    logic [31:0] child_pixel_2_7_i;
    logic [31:0] child_pixel_2_8_i;
    logic [31:0] child_pixel_2_9_i;
    logic [31:0] child_pixel_2_10_i;
    logic [31:0] child_pixel_2_11_i;
    logic [31:0] child_pixel_2_12_i;
    logic [31:0] child_pixel_2_13_i;
    logic [31:0] child_pixel_2_14_i;
    logic [31:0] child_pixel_2_15_i;
    logic [31:0] child_pixel_2_16_i;
    logic [31:0] child_pixel_2_17_i;
    logic [31:0] child_pixel_2_18_i;
    logic [31:0] child_pixel_2_19_i;
    logic [31:0] child_pixel_2_20_i;
    logic [31:0] child_pixel_2_21_i;
    logic [31:0] child_pixel_2_22_i;
    logic [31:0] child_pixel_2_23_i;
    logic [31:0] child_pixel_2_24_i;
    logic [31:0] child_pixel_2_25_i;
    logic [31:0] child_pixel_2_26_i;
    logic [31:0] child_pixel_2_27_i;
    logic [31:0] child_pixel_2_28_i;
    logic [31:0] child_pixel_2_29_i;
    logic [31:0] child_pixel_2_30_i;
    logic [31:0] child_pixel_2_31_i;
    logic [31:0] child_pixel_3_0_i;
    logic [31:0] child_pixel_3_1_i;
    logic [31:0] child_pixel_3_2_i;
    logic [31:0] child_pixel_3_3_i;
    logic [31:0] child_pixel_3_4_i;
    logic [31:0] child_pixel_3_5_i;
    logic [31:0] child_pixel_3_6_i;
    logic [31:0] child_pixel_3_7_i;
    logic [31:0] child_pixel_3_8_i;
    logic [31:0] child_pixel_3_9_i;
    logic [31:0] child_pixel_3_10_i;
    logic [31:0] child_pixel_3_11_i;
    logic [31:0] child_pixel_3_12_i;
    logic [31:0] child_pixel_3_13_i;
    logic [31:0] child_pixel_3_14_i;
    logic [31:0] child_pixel_3_15_i;
    logic [31:0] child_pixel_3_16_i;
    logic [31:0] child_pixel_3_17_i;
    logic [31:0] child_pixel_3_18_i;
    logic [31:0] child_pixel_3_19_i;
    logic [31:0] child_pixel_3_20_i;
    logic [31:0] child_pixel_3_21_i;
    logic [31:0] child_pixel_3_22_i;
    logic [31:0] child_pixel_3_23_i;
    logic [31:0] child_pixel_3_24_i;
    logic [31:0] child_pixel_3_25_i;
    logic [31:0] child_pixel_3_26_i;
    logic [31:0] child_pixel_3_27_i;
    logic [31:0] child_pixel_3_28_i;
    logic [31:0] child_pixel_3_29_i;
    logic [31:0] child_pixel_3_30_i;
    logic [31:0] child_pixel_3_31_i;

    assign previous_hpos_i = hpos - state_pixels_in_group;
    assign update_history_i = previous_hpos_i >= 0;
    assign clear_history_i = (hpos == 0) && ((vpos == 0) || (cfg_slice_width != cfg_pic_width));

    updatehistoryelement_decode_transition u_history_update(
        .cfg_native_420(cfg_native_420),
        .state_hpos(state_hpos),
        .state_vpos(state_vpos),
        .state_num_components(state_num_components),
        .state_is_encoder(state_is_encoder),
        .state_ich_selected(state_ich_selected),
        .state_prev_ich_selected(state_prev_ich_selected),
        .recon_0(line_sample_0),
        .recon_1(line_sample_1),
        .recon_2(line_sample_2),
        .recon_3(line_sample_3),
        .history_valid_0(clear_history_i ? 32'sd0 : history_valid_0),
        .history_valid_1(clear_history_i ? 32'sd0 : history_valid_1),
        .history_valid_2(clear_history_i ? 32'sd0 : history_valid_2),
        .history_valid_3(clear_history_i ? 32'sd0 : history_valid_3),
        .history_valid_4(clear_history_i ? 32'sd0 : history_valid_4),
        .history_valid_5(clear_history_i ? 32'sd0 : history_valid_5),
        .history_valid_6(clear_history_i ? 32'sd0 : history_valid_6),
        .history_valid_7(clear_history_i ? 32'sd0 : history_valid_7),
        .history_valid_8(clear_history_i ? 32'sd0 : history_valid_8),
        .history_valid_9(clear_history_i ? 32'sd0 : history_valid_9),
        .history_valid_10(clear_history_i ? 32'sd0 : history_valid_10),
        .history_valid_11(clear_history_i ? 32'sd0 : history_valid_11),
        .history_valid_12(clear_history_i ? 32'sd0 : history_valid_12),
        .history_valid_13(clear_history_i ? 32'sd0 : history_valid_13),
        .history_valid_14(clear_history_i ? 32'sd0 : history_valid_14),
        .history_valid_15(clear_history_i ? 32'sd0 : history_valid_15),
        .history_valid_16(clear_history_i ? 32'sd0 : history_valid_16),
        .history_valid_17(clear_history_i ? 32'sd0 : history_valid_17),
        .history_valid_18(clear_history_i ? 32'sd0 : history_valid_18),
        .history_valid_19(clear_history_i ? 32'sd0 : history_valid_19),
        .history_valid_20(clear_history_i ? 32'sd0 : history_valid_20),
        .history_valid_21(clear_history_i ? 32'sd0 : history_valid_21),
        .history_valid_22(clear_history_i ? 32'sd0 : history_valid_22),
        .history_valid_23(clear_history_i ? 32'sd0 : history_valid_23),
        .history_valid_24(clear_history_i ? 32'sd0 : history_valid_24),
        .history_valid_25(clear_history_i ? 32'sd0 : history_valid_25),
        .history_valid_26(clear_history_i ? 32'sd0 : history_valid_26),
        .history_valid_27(clear_history_i ? 32'sd0 : history_valid_27),
        .history_valid_28(clear_history_i ? 32'sd0 : history_valid_28),
        .history_valid_29(clear_history_i ? 32'sd0 : history_valid_29),
        .history_valid_30(clear_history_i ? 32'sd0 : history_valid_30),
        .history_valid_31(clear_history_i ? 32'sd0 : history_valid_31),
        .history_pixel_0_0(history_pixel_0_0),
        .history_pixel_0_1(history_pixel_0_1),
        .history_pixel_0_2(history_pixel_0_2),
        .history_pixel_0_3(history_pixel_0_3),
        .history_pixel_0_4(history_pixel_0_4),
        .history_pixel_0_5(history_pixel_0_5),
        .history_pixel_0_6(history_pixel_0_6),
        .history_pixel_0_7(history_pixel_0_7),
        .history_pixel_0_8(history_pixel_0_8),
        .history_pixel_0_9(history_pixel_0_9),
        .history_pixel_0_10(history_pixel_0_10),
        .history_pixel_0_11(history_pixel_0_11),
        .history_pixel_0_12(history_pixel_0_12),
        .history_pixel_0_13(history_pixel_0_13),
        .history_pixel_0_14(history_pixel_0_14),
        .history_pixel_0_15(history_pixel_0_15),
        .history_pixel_0_16(history_pixel_0_16),
        .history_pixel_0_17(history_pixel_0_17),
        .history_pixel_0_18(history_pixel_0_18),
        .history_pixel_0_19(history_pixel_0_19),
        .history_pixel_0_20(history_pixel_0_20),
        .history_pixel_0_21(history_pixel_0_21),
        .history_pixel_0_22(history_pixel_0_22),
        .history_pixel_0_23(history_pixel_0_23),
        .history_pixel_0_24(history_pixel_0_24),
        .history_pixel_0_25(history_pixel_0_25),
        .history_pixel_0_26(history_pixel_0_26),
        .history_pixel_0_27(history_pixel_0_27),
        .history_pixel_0_28(history_pixel_0_28),
        .history_pixel_0_29(history_pixel_0_29),
        .history_pixel_0_30(history_pixel_0_30),
        .history_pixel_0_31(history_pixel_0_31),
        .history_pixel_1_0(history_pixel_1_0),
        .history_pixel_1_1(history_pixel_1_1),
        .history_pixel_1_2(history_pixel_1_2),
        .history_pixel_1_3(history_pixel_1_3),
        .history_pixel_1_4(history_pixel_1_4),
        .history_pixel_1_5(history_pixel_1_5),
        .history_pixel_1_6(history_pixel_1_6),
        .history_pixel_1_7(history_pixel_1_7),
        .history_pixel_1_8(history_pixel_1_8),
        .history_pixel_1_9(history_pixel_1_9),
        .history_pixel_1_10(history_pixel_1_10),
        .history_pixel_1_11(history_pixel_1_11),
        .history_pixel_1_12(history_pixel_1_12),
        .history_pixel_1_13(history_pixel_1_13),
        .history_pixel_1_14(history_pixel_1_14),
        .history_pixel_1_15(history_pixel_1_15),
        .history_pixel_1_16(history_pixel_1_16),
        .history_pixel_1_17(history_pixel_1_17),
        .history_pixel_1_18(history_pixel_1_18),
        .history_pixel_1_19(history_pixel_1_19),
        .history_pixel_1_20(history_pixel_1_20),
        .history_pixel_1_21(history_pixel_1_21),
        .history_pixel_1_22(history_pixel_1_22),
        .history_pixel_1_23(history_pixel_1_23),
        .history_pixel_1_24(history_pixel_1_24),
        .history_pixel_1_25(history_pixel_1_25),
        .history_pixel_1_26(history_pixel_1_26),
        .history_pixel_1_27(history_pixel_1_27),
        .history_pixel_1_28(history_pixel_1_28),
        .history_pixel_1_29(history_pixel_1_29),
        .history_pixel_1_30(history_pixel_1_30),
        .history_pixel_1_31(history_pixel_1_31),
        .history_pixel_2_0(history_pixel_2_0),
        .history_pixel_2_1(history_pixel_2_1),
        .history_pixel_2_2(history_pixel_2_2),
        .history_pixel_2_3(history_pixel_2_3),
        .history_pixel_2_4(history_pixel_2_4),
        .history_pixel_2_5(history_pixel_2_5),
        .history_pixel_2_6(history_pixel_2_6),
        .history_pixel_2_7(history_pixel_2_7),
        .history_pixel_2_8(history_pixel_2_8),
        .history_pixel_2_9(history_pixel_2_9),
        .history_pixel_2_10(history_pixel_2_10),
        .history_pixel_2_11(history_pixel_2_11),
        .history_pixel_2_12(history_pixel_2_12),
        .history_pixel_2_13(history_pixel_2_13),
        .history_pixel_2_14(history_pixel_2_14),
        .history_pixel_2_15(history_pixel_2_15),
        .history_pixel_2_16(history_pixel_2_16),
        .history_pixel_2_17(history_pixel_2_17),
        .history_pixel_2_18(history_pixel_2_18),
        .history_pixel_2_19(history_pixel_2_19),
        .history_pixel_2_20(history_pixel_2_20),
        .history_pixel_2_21(history_pixel_2_21),
        .history_pixel_2_22(history_pixel_2_22),
        .history_pixel_2_23(history_pixel_2_23),
        .history_pixel_2_24(history_pixel_2_24),
        .history_pixel_2_25(history_pixel_2_25),
        .history_pixel_2_26(history_pixel_2_26),
        .history_pixel_2_27(history_pixel_2_27),
        .history_pixel_2_28(history_pixel_2_28),
        .history_pixel_2_29(history_pixel_2_29),
        .history_pixel_2_30(history_pixel_2_30),
        .history_pixel_2_31(history_pixel_2_31),
        .history_pixel_3_0(history_pixel_3_0),
        .history_pixel_3_1(history_pixel_3_1),
        .history_pixel_3_2(history_pixel_3_2),
        .history_pixel_3_3(history_pixel_3_3),
        .history_pixel_3_4(history_pixel_3_4),
        .history_pixel_3_5(history_pixel_3_5),
        .history_pixel_3_6(history_pixel_3_6),
        .history_pixel_3_7(history_pixel_3_7),
        .history_pixel_3_8(history_pixel_3_8),
        .history_pixel_3_9(history_pixel_3_9),
        .history_pixel_3_10(history_pixel_3_10),
        .history_pixel_3_11(history_pixel_3_11),
        .history_pixel_3_12(history_pixel_3_12),
        .history_pixel_3_13(history_pixel_3_13),
        .history_pixel_3_14(history_pixel_3_14),
        .history_pixel_3_15(history_pixel_3_15),
        .history_pixel_3_16(history_pixel_3_16),
        .history_pixel_3_17(history_pixel_3_17),
        .history_pixel_3_18(history_pixel_3_18),
        .history_pixel_3_19(history_pixel_3_19),
        .history_pixel_3_20(history_pixel_3_20),
        .history_pixel_3_21(history_pixel_3_21),
        .history_pixel_3_22(history_pixel_3_22),
        .history_pixel_3_23(history_pixel_3_23),
        .history_pixel_3_24(history_pixel_3_24),
        .history_pixel_3_25(history_pixel_3_25),
        .history_pixel_3_26(history_pixel_3_26),
        .history_pixel_3_27(history_pixel_3_27),
        .history_pixel_3_28(history_pixel_3_28),
        .history_pixel_3_29(history_pixel_3_29),
        .history_pixel_3_30(history_pixel_3_30),
        .history_pixel_3_31(history_pixel_3_31),
        .history_valid_0_out(child_valid_0_i),
        .history_valid_1_out(child_valid_1_i),
        .history_valid_2_out(child_valid_2_i),
        .history_valid_3_out(child_valid_3_i),
        .history_valid_4_out(child_valid_4_i),
        .history_valid_5_out(child_valid_5_i),
        .history_valid_6_out(child_valid_6_i),
        .history_valid_7_out(child_valid_7_i),
        .history_valid_8_out(child_valid_8_i),
        .history_valid_9_out(child_valid_9_i),
        .history_valid_10_out(child_valid_10_i),
        .history_valid_11_out(child_valid_11_i),
        .history_valid_12_out(child_valid_12_i),
        .history_valid_13_out(child_valid_13_i),
        .history_valid_14_out(child_valid_14_i),
        .history_valid_15_out(child_valid_15_i),
        .history_valid_16_out(child_valid_16_i),
        .history_valid_17_out(child_valid_17_i),
        .history_valid_18_out(child_valid_18_i),
        .history_valid_19_out(child_valid_19_i),
        .history_valid_20_out(child_valid_20_i),
        .history_valid_21_out(child_valid_21_i),
        .history_valid_22_out(child_valid_22_i),
        .history_valid_23_out(child_valid_23_i),
        .history_valid_24_out(child_valid_24_i),
        .history_valid_25_out(child_valid_25_i),
        .history_valid_26_out(child_valid_26_i),
        .history_valid_27_out(child_valid_27_i),
        .history_valid_28_out(child_valid_28_i),
        .history_valid_29_out(child_valid_29_i),
        .history_valid_30_out(child_valid_30_i),
        .history_valid_31_out(child_valid_31_i),
        .history_pixel_0_0_out(child_pixel_0_0_i),
        .history_pixel_0_1_out(child_pixel_0_1_i),
        .history_pixel_0_2_out(child_pixel_0_2_i),
        .history_pixel_0_3_out(child_pixel_0_3_i),
        .history_pixel_0_4_out(child_pixel_0_4_i),
        .history_pixel_0_5_out(child_pixel_0_5_i),
        .history_pixel_0_6_out(child_pixel_0_6_i),
        .history_pixel_0_7_out(child_pixel_0_7_i),
        .history_pixel_0_8_out(child_pixel_0_8_i),
        .history_pixel_0_9_out(child_pixel_0_9_i),
        .history_pixel_0_10_out(child_pixel_0_10_i),
        .history_pixel_0_11_out(child_pixel_0_11_i),
        .history_pixel_0_12_out(child_pixel_0_12_i),
        .history_pixel_0_13_out(child_pixel_0_13_i),
        .history_pixel_0_14_out(child_pixel_0_14_i),
        .history_pixel_0_15_out(child_pixel_0_15_i),
        .history_pixel_0_16_out(child_pixel_0_16_i),
        .history_pixel_0_17_out(child_pixel_0_17_i),
        .history_pixel_0_18_out(child_pixel_0_18_i),
        .history_pixel_0_19_out(child_pixel_0_19_i),
        .history_pixel_0_20_out(child_pixel_0_20_i),
        .history_pixel_0_21_out(child_pixel_0_21_i),
        .history_pixel_0_22_out(child_pixel_0_22_i),
        .history_pixel_0_23_out(child_pixel_0_23_i),
        .history_pixel_0_24_out(child_pixel_0_24_i),
        .history_pixel_0_25_out(child_pixel_0_25_i),
        .history_pixel_0_26_out(child_pixel_0_26_i),
        .history_pixel_0_27_out(child_pixel_0_27_i),
        .history_pixel_0_28_out(child_pixel_0_28_i),
        .history_pixel_0_29_out(child_pixel_0_29_i),
        .history_pixel_0_30_out(child_pixel_0_30_i),
        .history_pixel_0_31_out(child_pixel_0_31_i),
        .history_pixel_1_0_out(child_pixel_1_0_i),
        .history_pixel_1_1_out(child_pixel_1_1_i),
        .history_pixel_1_2_out(child_pixel_1_2_i),
        .history_pixel_1_3_out(child_pixel_1_3_i),
        .history_pixel_1_4_out(child_pixel_1_4_i),
        .history_pixel_1_5_out(child_pixel_1_5_i),
        .history_pixel_1_6_out(child_pixel_1_6_i),
        .history_pixel_1_7_out(child_pixel_1_7_i),
        .history_pixel_1_8_out(child_pixel_1_8_i),
        .history_pixel_1_9_out(child_pixel_1_9_i),
        .history_pixel_1_10_out(child_pixel_1_10_i),
        .history_pixel_1_11_out(child_pixel_1_11_i),
        .history_pixel_1_12_out(child_pixel_1_12_i),
        .history_pixel_1_13_out(child_pixel_1_13_i),
        .history_pixel_1_14_out(child_pixel_1_14_i),
        .history_pixel_1_15_out(child_pixel_1_15_i),
        .history_pixel_1_16_out(child_pixel_1_16_i),
        .history_pixel_1_17_out(child_pixel_1_17_i),
        .history_pixel_1_18_out(child_pixel_1_18_i),
        .history_pixel_1_19_out(child_pixel_1_19_i),
        .history_pixel_1_20_out(child_pixel_1_20_i),
        .history_pixel_1_21_out(child_pixel_1_21_i),
        .history_pixel_1_22_out(child_pixel_1_22_i),
        .history_pixel_1_23_out(child_pixel_1_23_i),
        .history_pixel_1_24_out(child_pixel_1_24_i),
        .history_pixel_1_25_out(child_pixel_1_25_i),
        .history_pixel_1_26_out(child_pixel_1_26_i),
        .history_pixel_1_27_out(child_pixel_1_27_i),
        .history_pixel_1_28_out(child_pixel_1_28_i),
        .history_pixel_1_29_out(child_pixel_1_29_i),
        .history_pixel_1_30_out(child_pixel_1_30_i),
        .history_pixel_1_31_out(child_pixel_1_31_i),
        .history_pixel_2_0_out(child_pixel_2_0_i),
        .history_pixel_2_1_out(child_pixel_2_1_i),
        .history_pixel_2_2_out(child_pixel_2_2_i),
        .history_pixel_2_3_out(child_pixel_2_3_i),
        .history_pixel_2_4_out(child_pixel_2_4_i),
        .history_pixel_2_5_out(child_pixel_2_5_i),
        .history_pixel_2_6_out(child_pixel_2_6_i),
        .history_pixel_2_7_out(child_pixel_2_7_i),
        .history_pixel_2_8_out(child_pixel_2_8_i),
        .history_pixel_2_9_out(child_pixel_2_9_i),
        .history_pixel_2_10_out(child_pixel_2_10_i),
        .history_pixel_2_11_out(child_pixel_2_11_i),
        .history_pixel_2_12_out(child_pixel_2_12_i),
        .history_pixel_2_13_out(child_pixel_2_13_i),
        .history_pixel_2_14_out(child_pixel_2_14_i),
        .history_pixel_2_15_out(child_pixel_2_15_i),
        .history_pixel_2_16_out(child_pixel_2_16_i),
        .history_pixel_2_17_out(child_pixel_2_17_i),
        .history_pixel_2_18_out(child_pixel_2_18_i),
        .history_pixel_2_19_out(child_pixel_2_19_i),
        .history_pixel_2_20_out(child_pixel_2_20_i),
        .history_pixel_2_21_out(child_pixel_2_21_i),
        .history_pixel_2_22_out(child_pixel_2_22_i),
        .history_pixel_2_23_out(child_pixel_2_23_i),
        .history_pixel_2_24_out(child_pixel_2_24_i),
        .history_pixel_2_25_out(child_pixel_2_25_i),
        .history_pixel_2_26_out(child_pixel_2_26_i),
        .history_pixel_2_27_out(child_pixel_2_27_i),
        .history_pixel_2_28_out(child_pixel_2_28_i),
        .history_pixel_2_29_out(child_pixel_2_29_i),
        .history_pixel_2_30_out(child_pixel_2_30_i),
        .history_pixel_2_31_out(child_pixel_2_31_i),
        .history_pixel_3_0_out(child_pixel_3_0_i),
        .history_pixel_3_1_out(child_pixel_3_1_i),
        .history_pixel_3_2_out(child_pixel_3_2_i),
        .history_pixel_3_3_out(child_pixel_3_3_i),
        .history_pixel_3_4_out(child_pixel_3_4_i),
        .history_pixel_3_5_out(child_pixel_3_5_i),
        .history_pixel_3_6_out(child_pixel_3_6_i),
        .history_pixel_3_7_out(child_pixel_3_7_i),
        .history_pixel_3_8_out(child_pixel_3_8_i),
        .history_pixel_3_9_out(child_pixel_3_9_i),
        .history_pixel_3_10_out(child_pixel_3_10_i),
        .history_pixel_3_11_out(child_pixel_3_11_i),
        .history_pixel_3_12_out(child_pixel_3_12_i),
        .history_pixel_3_13_out(child_pixel_3_13_i),
        .history_pixel_3_14_out(child_pixel_3_14_i),
        .history_pixel_3_15_out(child_pixel_3_15_i),
        .history_pixel_3_16_out(child_pixel_3_16_i),
        .history_pixel_3_17_out(child_pixel_3_17_i),
        .history_pixel_3_18_out(child_pixel_3_18_i),
        .history_pixel_3_19_out(child_pixel_3_19_i),
        .history_pixel_3_20_out(child_pixel_3_20_i),
        .history_pixel_3_21_out(child_pixel_3_21_i),
        .history_pixel_3_22_out(child_pixel_3_22_i),
        .history_pixel_3_23_out(child_pixel_3_23_i),
        .history_pixel_3_24_out(child_pixel_3_24_i),
        .history_pixel_3_25_out(child_pixel_3_25_i),
        .history_pixel_3_26_out(child_pixel_3_26_i),
        .history_pixel_3_27_out(child_pixel_3_27_i),
        .history_pixel_3_28_out(child_pixel_3_28_i),
        .history_pixel_3_29_out(child_pixel_3_29_i),
        .history_pixel_3_30_out(child_pixel_3_30_i),
        .history_pixel_3_31_out(child_pixel_3_31_i)
    );

    always_comb begin
        history_valid_0_out = history_valid_0;
        history_valid_1_out = history_valid_1;
        history_valid_2_out = history_valid_2;
        history_valid_3_out = history_valid_3;
        history_valid_4_out = history_valid_4;
        history_valid_5_out = history_valid_5;
        history_valid_6_out = history_valid_6;
        history_valid_7_out = history_valid_7;
        history_valid_8_out = history_valid_8;
        history_valid_9_out = history_valid_9;
        history_valid_10_out = history_valid_10;
        history_valid_11_out = history_valid_11;
        history_valid_12_out = history_valid_12;
        history_valid_13_out = history_valid_13;
        history_valid_14_out = history_valid_14;
        history_valid_15_out = history_valid_15;
        history_valid_16_out = history_valid_16;
        history_valid_17_out = history_valid_17;
        history_valid_18_out = history_valid_18;
        history_valid_19_out = history_valid_19;
        history_valid_20_out = history_valid_20;
        history_valid_21_out = history_valid_21;
        history_valid_22_out = history_valid_22;
        history_valid_23_out = history_valid_23;
        history_valid_24_out = history_valid_24;
        history_valid_25_out = history_valid_25;
        history_valid_26_out = history_valid_26;
        history_valid_27_out = history_valid_27;
        history_valid_28_out = history_valid_28;
        history_valid_29_out = history_valid_29;
        history_valid_30_out = history_valid_30;
        history_valid_31_out = history_valid_31;
        history_pixel_0_0_out = history_pixel_0_0;
        history_pixel_0_1_out = history_pixel_0_1;
        history_pixel_0_2_out = history_pixel_0_2;
        history_pixel_0_3_out = history_pixel_0_3;
        history_pixel_0_4_out = history_pixel_0_4;
        history_pixel_0_5_out = history_pixel_0_5;
        history_pixel_0_6_out = history_pixel_0_6;
        history_pixel_0_7_out = history_pixel_0_7;
        history_pixel_0_8_out = history_pixel_0_8;
        history_pixel_0_9_out = history_pixel_0_9;
        history_pixel_0_10_out = history_pixel_0_10;
        history_pixel_0_11_out = history_pixel_0_11;
        history_pixel_0_12_out = history_pixel_0_12;
        history_pixel_0_13_out = history_pixel_0_13;
        history_pixel_0_14_out = history_pixel_0_14;
        history_pixel_0_15_out = history_pixel_0_15;
        history_pixel_0_16_out = history_pixel_0_16;
        history_pixel_0_17_out = history_pixel_0_17;
        history_pixel_0_18_out = history_pixel_0_18;
        history_pixel_0_19_out = history_pixel_0_19;
        history_pixel_0_20_out = history_pixel_0_20;
        history_pixel_0_21_out = history_pixel_0_21;
        history_pixel_0_22_out = history_pixel_0_22;
        history_pixel_0_23_out = history_pixel_0_23;
        history_pixel_0_24_out = history_pixel_0_24;
        history_pixel_0_25_out = history_pixel_0_25;
        history_pixel_0_26_out = history_pixel_0_26;
        history_pixel_0_27_out = history_pixel_0_27;
        history_pixel_0_28_out = history_pixel_0_28;
        history_pixel_0_29_out = history_pixel_0_29;
        history_pixel_0_30_out = history_pixel_0_30;
        history_pixel_0_31_out = history_pixel_0_31;
        history_pixel_1_0_out = history_pixel_1_0;
        history_pixel_1_1_out = history_pixel_1_1;
        history_pixel_1_2_out = history_pixel_1_2;
        history_pixel_1_3_out = history_pixel_1_3;
        history_pixel_1_4_out = history_pixel_1_4;
        history_pixel_1_5_out = history_pixel_1_5;
        history_pixel_1_6_out = history_pixel_1_6;
        history_pixel_1_7_out = history_pixel_1_7;
        history_pixel_1_8_out = history_pixel_1_8;
        history_pixel_1_9_out = history_pixel_1_9;
        history_pixel_1_10_out = history_pixel_1_10;
        history_pixel_1_11_out = history_pixel_1_11;
        history_pixel_1_12_out = history_pixel_1_12;
        history_pixel_1_13_out = history_pixel_1_13;
        history_pixel_1_14_out = history_pixel_1_14;
        history_pixel_1_15_out = history_pixel_1_15;
        history_pixel_1_16_out = history_pixel_1_16;
        history_pixel_1_17_out = history_pixel_1_17;
        history_pixel_1_18_out = history_pixel_1_18;
        history_pixel_1_19_out = history_pixel_1_19;
        history_pixel_1_20_out = history_pixel_1_20;
        history_pixel_1_21_out = history_pixel_1_21;
        history_pixel_1_22_out = history_pixel_1_22;
        history_pixel_1_23_out = history_pixel_1_23;
        history_pixel_1_24_out = history_pixel_1_24;
        history_pixel_1_25_out = history_pixel_1_25;
        history_pixel_1_26_out = history_pixel_1_26;
        history_pixel_1_27_out = history_pixel_1_27;
        history_pixel_1_28_out = history_pixel_1_28;
        history_pixel_1_29_out = history_pixel_1_29;
        history_pixel_1_30_out = history_pixel_1_30;
        history_pixel_1_31_out = history_pixel_1_31;
        history_pixel_2_0_out = history_pixel_2_0;
        history_pixel_2_1_out = history_pixel_2_1;
        history_pixel_2_2_out = history_pixel_2_2;
        history_pixel_2_3_out = history_pixel_2_3;
        history_pixel_2_4_out = history_pixel_2_4;
        history_pixel_2_5_out = history_pixel_2_5;
        history_pixel_2_6_out = history_pixel_2_6;
        history_pixel_2_7_out = history_pixel_2_7;
        history_pixel_2_8_out = history_pixel_2_8;
        history_pixel_2_9_out = history_pixel_2_9;
        history_pixel_2_10_out = history_pixel_2_10;
        history_pixel_2_11_out = history_pixel_2_11;
        history_pixel_2_12_out = history_pixel_2_12;
        history_pixel_2_13_out = history_pixel_2_13;
        history_pixel_2_14_out = history_pixel_2_14;
        history_pixel_2_15_out = history_pixel_2_15;
        history_pixel_2_16_out = history_pixel_2_16;
        history_pixel_2_17_out = history_pixel_2_17;
        history_pixel_2_18_out = history_pixel_2_18;
        history_pixel_2_19_out = history_pixel_2_19;
        history_pixel_2_20_out = history_pixel_2_20;
        history_pixel_2_21_out = history_pixel_2_21;
        history_pixel_2_22_out = history_pixel_2_22;
        history_pixel_2_23_out = history_pixel_2_23;
        history_pixel_2_24_out = history_pixel_2_24;
        history_pixel_2_25_out = history_pixel_2_25;
        history_pixel_2_26_out = history_pixel_2_26;
        history_pixel_2_27_out = history_pixel_2_27;
        history_pixel_2_28_out = history_pixel_2_28;
        history_pixel_2_29_out = history_pixel_2_29;
        history_pixel_2_30_out = history_pixel_2_30;
        history_pixel_2_31_out = history_pixel_2_31;
        history_pixel_3_0_out = history_pixel_3_0;
        history_pixel_3_1_out = history_pixel_3_1;
        history_pixel_3_2_out = history_pixel_3_2;
        history_pixel_3_3_out = history_pixel_3_3;
        history_pixel_3_4_out = history_pixel_3_4;
        history_pixel_3_5_out = history_pixel_3_5;
        history_pixel_3_6_out = history_pixel_3_6;
        history_pixel_3_7_out = history_pixel_3_7;
        history_pixel_3_8_out = history_pixel_3_8;
        history_pixel_3_9_out = history_pixel_3_9;
        history_pixel_3_10_out = history_pixel_3_10;
        history_pixel_3_11_out = history_pixel_3_11;
        history_pixel_3_12_out = history_pixel_3_12;
        history_pixel_3_13_out = history_pixel_3_13;
        history_pixel_3_14_out = history_pixel_3_14;
        history_pixel_3_15_out = history_pixel_3_15;
        history_pixel_3_16_out = history_pixel_3_16;
        history_pixel_3_17_out = history_pixel_3_17;
        history_pixel_3_18_out = history_pixel_3_18;
        history_pixel_3_19_out = history_pixel_3_19;
        history_pixel_3_20_out = history_pixel_3_20;
        history_pixel_3_21_out = history_pixel_3_21;
        history_pixel_3_22_out = history_pixel_3_22;
        history_pixel_3_23_out = history_pixel_3_23;
        history_pixel_3_24_out = history_pixel_3_24;
        history_pixel_3_25_out = history_pixel_3_25;
        history_pixel_3_26_out = history_pixel_3_26;
        history_pixel_3_27_out = history_pixel_3_27;
        history_pixel_3_28_out = history_pixel_3_28;
        history_pixel_3_29_out = history_pixel_3_29;
        history_pixel_3_30_out = history_pixel_3_30;
        history_pixel_3_31_out = history_pixel_3_31;
        if (clear_history_i) begin
            history_valid_0_out = 32'sd0;
            history_valid_1_out = 32'sd0;
            history_valid_2_out = 32'sd0;
            history_valid_3_out = 32'sd0;
            history_valid_4_out = 32'sd0;
            history_valid_5_out = 32'sd0;
            history_valid_6_out = 32'sd0;
            history_valid_7_out = 32'sd0;
            history_valid_8_out = 32'sd0;
            history_valid_9_out = 32'sd0;
            history_valid_10_out = 32'sd0;
            history_valid_11_out = 32'sd0;
            history_valid_12_out = 32'sd0;
            history_valid_13_out = 32'sd0;
            history_valid_14_out = 32'sd0;
            history_valid_15_out = 32'sd0;
            history_valid_16_out = 32'sd0;
            history_valid_17_out = 32'sd0;
            history_valid_18_out = 32'sd0;
            history_valid_19_out = 32'sd0;
            history_valid_20_out = 32'sd0;
            history_valid_21_out = 32'sd0;
            history_valid_22_out = 32'sd0;
            history_valid_23_out = 32'sd0;
            history_valid_24_out = 32'sd0;
            history_valid_25_out = 32'sd0;
            history_valid_26_out = 32'sd0;
            history_valid_27_out = 32'sd0;
            history_valid_28_out = 32'sd0;
            history_valid_29_out = 32'sd0;
            history_valid_30_out = 32'sd0;
            history_valid_31_out = 32'sd0;
        end
        if (update_history_i) begin
            history_valid_0_out = child_valid_0_i;
            history_valid_1_out = child_valid_1_i;
            history_valid_2_out = child_valid_2_i;
            history_valid_3_out = child_valid_3_i;
            history_valid_4_out = child_valid_4_i;
            history_valid_5_out = child_valid_5_i;
            history_valid_6_out = child_valid_6_i;
            history_valid_7_out = child_valid_7_i;
            history_valid_8_out = child_valid_8_i;
            history_valid_9_out = child_valid_9_i;
            history_valid_10_out = child_valid_10_i;
            history_valid_11_out = child_valid_11_i;
            history_valid_12_out = child_valid_12_i;
            history_valid_13_out = child_valid_13_i;
            history_valid_14_out = child_valid_14_i;
            history_valid_15_out = child_valid_15_i;
            history_valid_16_out = child_valid_16_i;
            history_valid_17_out = child_valid_17_i;
            history_valid_18_out = child_valid_18_i;
            history_valid_19_out = child_valid_19_i;
            history_valid_20_out = child_valid_20_i;
            history_valid_21_out = child_valid_21_i;
            history_valid_22_out = child_valid_22_i;
            history_valid_23_out = child_valid_23_i;
            history_valid_24_out = child_valid_24_i;
            history_valid_25_out = child_valid_25_i;
            history_valid_26_out = child_valid_26_i;
            history_valid_27_out = child_valid_27_i;
            history_valid_28_out = child_valid_28_i;
            history_valid_29_out = child_valid_29_i;
            history_valid_30_out = child_valid_30_i;
            history_valid_31_out = child_valid_31_i;
            history_pixel_0_0_out = child_pixel_0_0_i;
            history_pixel_0_1_out = child_pixel_0_1_i;
            history_pixel_0_2_out = child_pixel_0_2_i;
            history_pixel_0_3_out = child_pixel_0_3_i;
            history_pixel_0_4_out = child_pixel_0_4_i;
            history_pixel_0_5_out = child_pixel_0_5_i;
            history_pixel_0_6_out = child_pixel_0_6_i;
            history_pixel_0_7_out = child_pixel_0_7_i;
            history_pixel_0_8_out = child_pixel_0_8_i;
            history_pixel_0_9_out = child_pixel_0_9_i;
            history_pixel_0_10_out = child_pixel_0_10_i;
            history_pixel_0_11_out = child_pixel_0_11_i;
            history_pixel_0_12_out = child_pixel_0_12_i;
            history_pixel_0_13_out = child_pixel_0_13_i;
            history_pixel_0_14_out = child_pixel_0_14_i;
            history_pixel_0_15_out = child_pixel_0_15_i;
            history_pixel_0_16_out = child_pixel_0_16_i;
            history_pixel_0_17_out = child_pixel_0_17_i;
            history_pixel_0_18_out = child_pixel_0_18_i;
            history_pixel_0_19_out = child_pixel_0_19_i;
            history_pixel_0_20_out = child_pixel_0_20_i;
            history_pixel_0_21_out = child_pixel_0_21_i;
            history_pixel_0_22_out = child_pixel_0_22_i;
            history_pixel_0_23_out = child_pixel_0_23_i;
            history_pixel_0_24_out = child_pixel_0_24_i;
            history_pixel_0_25_out = child_pixel_0_25_i;
            history_pixel_0_26_out = child_pixel_0_26_i;
            history_pixel_0_27_out = child_pixel_0_27_i;
            history_pixel_0_28_out = child_pixel_0_28_i;
            history_pixel_0_29_out = child_pixel_0_29_i;
            history_pixel_0_30_out = child_pixel_0_30_i;
            history_pixel_0_31_out = child_pixel_0_31_i;
            history_pixel_1_0_out = child_pixel_1_0_i;
            history_pixel_1_1_out = child_pixel_1_1_i;
            history_pixel_1_2_out = child_pixel_1_2_i;
            history_pixel_1_3_out = child_pixel_1_3_i;
            history_pixel_1_4_out = child_pixel_1_4_i;
            history_pixel_1_5_out = child_pixel_1_5_i;
            history_pixel_1_6_out = child_pixel_1_6_i;
            history_pixel_1_7_out = child_pixel_1_7_i;
            history_pixel_1_8_out = child_pixel_1_8_i;
            history_pixel_1_9_out = child_pixel_1_9_i;
            history_pixel_1_10_out = child_pixel_1_10_i;
            history_pixel_1_11_out = child_pixel_1_11_i;
            history_pixel_1_12_out = child_pixel_1_12_i;
            history_pixel_1_13_out = child_pixel_1_13_i;
            history_pixel_1_14_out = child_pixel_1_14_i;
            history_pixel_1_15_out = child_pixel_1_15_i;
            history_pixel_1_16_out = child_pixel_1_16_i;
            history_pixel_1_17_out = child_pixel_1_17_i;
            history_pixel_1_18_out = child_pixel_1_18_i;
            history_pixel_1_19_out = child_pixel_1_19_i;
            history_pixel_1_20_out = child_pixel_1_20_i;
            history_pixel_1_21_out = child_pixel_1_21_i;
            history_pixel_1_22_out = child_pixel_1_22_i;
            history_pixel_1_23_out = child_pixel_1_23_i;
            history_pixel_1_24_out = child_pixel_1_24_i;
            history_pixel_1_25_out = child_pixel_1_25_i;
            history_pixel_1_26_out = child_pixel_1_26_i;
            history_pixel_1_27_out = child_pixel_1_27_i;
            history_pixel_1_28_out = child_pixel_1_28_i;
            history_pixel_1_29_out = child_pixel_1_29_i;
            history_pixel_1_30_out = child_pixel_1_30_i;
            history_pixel_1_31_out = child_pixel_1_31_i;
            history_pixel_2_0_out = child_pixel_2_0_i;
            history_pixel_2_1_out = child_pixel_2_1_i;
            history_pixel_2_2_out = child_pixel_2_2_i;
            history_pixel_2_3_out = child_pixel_2_3_i;
            history_pixel_2_4_out = child_pixel_2_4_i;
            history_pixel_2_5_out = child_pixel_2_5_i;
            history_pixel_2_6_out = child_pixel_2_6_i;
            history_pixel_2_7_out = child_pixel_2_7_i;
            history_pixel_2_8_out = child_pixel_2_8_i;
            history_pixel_2_9_out = child_pixel_2_9_i;
            history_pixel_2_10_out = child_pixel_2_10_i;
            history_pixel_2_11_out = child_pixel_2_11_i;
            history_pixel_2_12_out = child_pixel_2_12_i;
            history_pixel_2_13_out = child_pixel_2_13_i;
            history_pixel_2_14_out = child_pixel_2_14_i;
            history_pixel_2_15_out = child_pixel_2_15_i;
            history_pixel_2_16_out = child_pixel_2_16_i;
            history_pixel_2_17_out = child_pixel_2_17_i;
            history_pixel_2_18_out = child_pixel_2_18_i;
            history_pixel_2_19_out = child_pixel_2_19_i;
            history_pixel_2_20_out = child_pixel_2_20_i;
            history_pixel_2_21_out = child_pixel_2_21_i;
            history_pixel_2_22_out = child_pixel_2_22_i;
            history_pixel_2_23_out = child_pixel_2_23_i;
            history_pixel_2_24_out = child_pixel_2_24_i;
            history_pixel_2_25_out = child_pixel_2_25_i;
            history_pixel_2_26_out = child_pixel_2_26_i;
            history_pixel_2_27_out = child_pixel_2_27_i;
            history_pixel_2_28_out = child_pixel_2_28_i;
            history_pixel_2_29_out = child_pixel_2_29_i;
            history_pixel_2_30_out = child_pixel_2_30_i;
            history_pixel_2_31_out = child_pixel_2_31_i;
            history_pixel_3_0_out = child_pixel_3_0_i;
            history_pixel_3_1_out = child_pixel_3_1_i;
            history_pixel_3_2_out = child_pixel_3_2_i;
            history_pixel_3_3_out = child_pixel_3_3_i;
            history_pixel_3_4_out = child_pixel_3_4_i;
            history_pixel_3_5_out = child_pixel_3_5_i;
            history_pixel_3_6_out = child_pixel_3_6_i;
            history_pixel_3_7_out = child_pixel_3_7_i;
            history_pixel_3_8_out = child_pixel_3_8_i;
            history_pixel_3_9_out = child_pixel_3_9_i;
            history_pixel_3_10_out = child_pixel_3_10_i;
            history_pixel_3_11_out = child_pixel_3_11_i;
            history_pixel_3_12_out = child_pixel_3_12_i;
            history_pixel_3_13_out = child_pixel_3_13_i;
            history_pixel_3_14_out = child_pixel_3_14_i;
            history_pixel_3_15_out = child_pixel_3_15_i;
            history_pixel_3_16_out = child_pixel_3_16_i;
            history_pixel_3_17_out = child_pixel_3_17_i;
            history_pixel_3_18_out = child_pixel_3_18_i;
            history_pixel_3_19_out = child_pixel_3_19_i;
            history_pixel_3_20_out = child_pixel_3_20_i;
            history_pixel_3_21_out = child_pixel_3_21_i;
            history_pixel_3_22_out = child_pixel_3_22_i;
            history_pixel_3_23_out = child_pixel_3_23_i;
            history_pixel_3_24_out = child_pixel_3_24_i;
            history_pixel_3_25_out = child_pixel_3_25_i;
            history_pixel_3_26_out = child_pixel_3_26_i;
            history_pixel_3_27_out = child_pixel_3_27_i;
            history_pixel_3_28_out = child_pixel_3_28_i;
            history_pixel_3_29_out = child_pixel_3_29_i;
            history_pixel_3_30_out = child_pixel_3_30_i;
            history_pixel_3_31_out = child_pixel_3_31_i;
        end
    end
endmodule
