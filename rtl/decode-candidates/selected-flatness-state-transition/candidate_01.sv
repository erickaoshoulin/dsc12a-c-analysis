module isflatnessinfosent (
    input logic [4:0] qp,
    input logic [4:0] flatness_min_qp,
    input logic [4:0] flatness_max_qp,
    output logic return_value
);
    assign return_value = ((qp >= flatness_min_qp) && (qp <= flatness_max_qp));
endmodule

module isorigflathindex (
    input logic [15:0] hPos,
    input logic [4:0] bits_per_component,
    input logic [4:0] primary_qp,
    input logic [2:0] num_components,
    input logic [15:0] slice_width,
    input logic [9:0] flatness_det_thresh,
    input logic [2:0] somewhat_flat_qp_delta,
    input logic native_420,
    input logic [1:0] dsc_version_minor,
    input logic [4:0] cpnt_bit_depth_0,
    input logic [4:0] cpnt_bit_depth_1,
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
    output logic [1:0] return_value
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
    function automatic integer luma_qlevel_i;
        input integer bit_depth;
        input integer qp;
        begin
            luma_qlevel_i = 0;
            case (bit_depth)
                8: begin
                    case (qp)
                        0: luma_qlevel_i = 0;
                        1: luma_qlevel_i = 0;
                        2: luma_qlevel_i = 0;
                        3: luma_qlevel_i = 1;
                        4: luma_qlevel_i = 1;
                        5: luma_qlevel_i = 2;
                        6: luma_qlevel_i = 2;
                        7: luma_qlevel_i = 3;
                        8: luma_qlevel_i = 3;
                        9: luma_qlevel_i = 4;
                        10: luma_qlevel_i = 4;
                        11: luma_qlevel_i = 5;
                        12: luma_qlevel_i = 5;
                        13: luma_qlevel_i = 5;
                        14: luma_qlevel_i = 6;
                        15: luma_qlevel_i = 7;
                        default: luma_qlevel_i = 0;
                    endcase
                end
                10: begin
                    case (qp)
                        0: luma_qlevel_i = 0;
                        1: luma_qlevel_i = 0;
                        2: luma_qlevel_i = 0;
                        3: luma_qlevel_i = 1;
                        4: luma_qlevel_i = 1;
                        5: luma_qlevel_i = 2;
                        6: luma_qlevel_i = 2;
                        7: luma_qlevel_i = 3;
                        8: luma_qlevel_i = 3;
                        9: luma_qlevel_i = 4;
                        10: luma_qlevel_i = 4;
                        11: luma_qlevel_i = 5;
                        12: luma_qlevel_i = 5;
                        13: luma_qlevel_i = 6;
                        14: luma_qlevel_i = 6;
                        15: luma_qlevel_i = 7;
                        16: luma_qlevel_i = 7;
                        17: luma_qlevel_i = 7;
                        18: luma_qlevel_i = 8;
                        19: luma_qlevel_i = 9;
                        default: luma_qlevel_i = 0;
                    endcase
                end
                12: begin
                    case (qp)
                        0: luma_qlevel_i = 0;
                        1: luma_qlevel_i = 0;
                        2: luma_qlevel_i = 0;
                        3: luma_qlevel_i = 1;
                        4: luma_qlevel_i = 1;
                        5: luma_qlevel_i = 2;
                        6: luma_qlevel_i = 2;
                        7: luma_qlevel_i = 3;
                        8: luma_qlevel_i = 3;
                        9: luma_qlevel_i = 4;
                        10: luma_qlevel_i = 4;
                        11: luma_qlevel_i = 5;
                        12: luma_qlevel_i = 5;
                        13: luma_qlevel_i = 6;
                        14: luma_qlevel_i = 6;
                        15: luma_qlevel_i = 7;
                        16: luma_qlevel_i = 7;
                        17: luma_qlevel_i = 8;
                        18: luma_qlevel_i = 8;
                        19: luma_qlevel_i = 9;
                        20: luma_qlevel_i = 9;
                        21: luma_qlevel_i = 9;
                        22: luma_qlevel_i = 10;
                        23: luma_qlevel_i = 11;
                        default: luma_qlevel_i = 0;
                    endcase
                end
                14: begin
                    case (qp)
                        0: luma_qlevel_i = 0;
                        1: luma_qlevel_i = 0;
                        2: luma_qlevel_i = 0;
                        3: luma_qlevel_i = 1;
                        4: luma_qlevel_i = 1;
                        5: luma_qlevel_i = 2;
                        6: luma_qlevel_i = 2;
                        7: luma_qlevel_i = 3;
                        8: luma_qlevel_i = 3;
                        9: luma_qlevel_i = 4;
                        10: luma_qlevel_i = 4;
                        11: luma_qlevel_i = 5;
                        12: luma_qlevel_i = 5;
                        13: luma_qlevel_i = 6;
                        14: luma_qlevel_i = 6;
                        15: luma_qlevel_i = 7;
                        16: luma_qlevel_i = 7;
                        17: luma_qlevel_i = 8;
                        18: luma_qlevel_i = 8;
                        19: luma_qlevel_i = 9;
                        20: luma_qlevel_i = 9;
                        21: luma_qlevel_i = 10;
                        22: luma_qlevel_i = 10;
                        23: luma_qlevel_i = 11;
                        24: luma_qlevel_i = 11;
                        25: luma_qlevel_i = 11;
                        26: luma_qlevel_i = 12;
                        27: luma_qlevel_i = 13;
                        default: luma_qlevel_i = 0;
                    endcase
                end
                16: begin
                    case (qp)
                        0: luma_qlevel_i = 0;
                        1: luma_qlevel_i = 0;
                        2: luma_qlevel_i = 0;
                        3: luma_qlevel_i = 1;
                        4: luma_qlevel_i = 1;
                        5: luma_qlevel_i = 2;
                        6: luma_qlevel_i = 2;
                        7: luma_qlevel_i = 3;
                        8: luma_qlevel_i = 3;
                        9: luma_qlevel_i = 4;
                        10: luma_qlevel_i = 4;
                        11: luma_qlevel_i = 5;
                        12: luma_qlevel_i = 5;
                        13: luma_qlevel_i = 6;
                        14: luma_qlevel_i = 6;
                        15: luma_qlevel_i = 7;
                        16: luma_qlevel_i = 7;
                        17: luma_qlevel_i = 8;
                        18: luma_qlevel_i = 8;
                        19: luma_qlevel_i = 9;
                        20: luma_qlevel_i = 9;
                        21: luma_qlevel_i = 10;
                        22: luma_qlevel_i = 10;
                        23: luma_qlevel_i = 11;
                        24: luma_qlevel_i = 11;
                        25: luma_qlevel_i = 12;
                        26: luma_qlevel_i = 12;
                        27: luma_qlevel_i = 13;
                        28: luma_qlevel_i = 13;
                        29: luma_qlevel_i = 13;
                        30: luma_qlevel_i = 14;
                        31: luma_qlevel_i = 15;
                        default: luma_qlevel_i = 0;
                    endcase
                end
                default: luma_qlevel_i = 0;
            endcase
        end
    endfunction
    function automatic integer chroma_qlevel_i;
        input integer bit_depth;
        input integer qp;
        begin
            chroma_qlevel_i = 0;
            case (bit_depth)
                8: begin
                    case (qp)
                        0: chroma_qlevel_i = 0;
                        1: chroma_qlevel_i = 1;
                        2: chroma_qlevel_i = 2;
                        3: chroma_qlevel_i = 2;
                        4: chroma_qlevel_i = 3;
                        5: chroma_qlevel_i = 3;
                        6: chroma_qlevel_i = 4;
                        7: chroma_qlevel_i = 4;
                        8: chroma_qlevel_i = 5;
                        9: chroma_qlevel_i = 5;
                        10: chroma_qlevel_i = 6;
                        11: chroma_qlevel_i = 6;
                        12: chroma_qlevel_i = 7;
                        13: chroma_qlevel_i = 8;
                        14: chroma_qlevel_i = 8;
                        15: chroma_qlevel_i = 8;
                        default: chroma_qlevel_i = 0;
                    endcase
                end
                10: begin
                    case (qp)
                        0: chroma_qlevel_i = 0;
                        1: chroma_qlevel_i = 1;
                        2: chroma_qlevel_i = 2;
                        3: chroma_qlevel_i = 2;
                        4: chroma_qlevel_i = 3;
                        5: chroma_qlevel_i = 3;
                        6: chroma_qlevel_i = 4;
                        7: chroma_qlevel_i = 4;
                        8: chroma_qlevel_i = 5;
                        9: chroma_qlevel_i = 5;
                        10: chroma_qlevel_i = 6;
                        11: chroma_qlevel_i = 6;
                        12: chroma_qlevel_i = 7;
                        13: chroma_qlevel_i = 7;
                        14: chroma_qlevel_i = 8;
                        15: chroma_qlevel_i = 8;
                        16: chroma_qlevel_i = 9;
                        17: chroma_qlevel_i = 10;
                        18: chroma_qlevel_i = 10;
                        19: chroma_qlevel_i = 10;
                        default: chroma_qlevel_i = 0;
                    endcase
                end
                12: begin
                    case (qp)
                        0: chroma_qlevel_i = 0;
                        1: chroma_qlevel_i = 1;
                        2: chroma_qlevel_i = 2;
                        3: chroma_qlevel_i = 2;
                        4: chroma_qlevel_i = 3;
                        5: chroma_qlevel_i = 3;
                        6: chroma_qlevel_i = 4;
                        7: chroma_qlevel_i = 4;
                        8: chroma_qlevel_i = 5;
                        9: chroma_qlevel_i = 5;
                        10: chroma_qlevel_i = 6;
                        11: chroma_qlevel_i = 6;
                        12: chroma_qlevel_i = 7;
                        13: chroma_qlevel_i = 7;
                        14: chroma_qlevel_i = 8;
                        15: chroma_qlevel_i = 8;
                        16: chroma_qlevel_i = 9;
                        17: chroma_qlevel_i = 9;
                        18: chroma_qlevel_i = 10;
                        19: chroma_qlevel_i = 10;
                        20: chroma_qlevel_i = 11;
                        21: chroma_qlevel_i = 12;
                        22: chroma_qlevel_i = 12;
                        23: chroma_qlevel_i = 12;
                        default: chroma_qlevel_i = 0;
                    endcase
                end
                14: begin
                    case (qp)
                        0: chroma_qlevel_i = 0;
                        1: chroma_qlevel_i = 1;
                        2: chroma_qlevel_i = 2;
                        3: chroma_qlevel_i = 2;
                        4: chroma_qlevel_i = 3;
                        5: chroma_qlevel_i = 3;
                        6: chroma_qlevel_i = 4;
                        7: chroma_qlevel_i = 4;
                        8: chroma_qlevel_i = 5;
                        9: chroma_qlevel_i = 5;
                        10: chroma_qlevel_i = 6;
                        11: chroma_qlevel_i = 6;
                        12: chroma_qlevel_i = 7;
                        13: chroma_qlevel_i = 7;
                        14: chroma_qlevel_i = 8;
                        15: chroma_qlevel_i = 8;
                        16: chroma_qlevel_i = 9;
                        17: chroma_qlevel_i = 9;
                        18: chroma_qlevel_i = 10;
                        19: chroma_qlevel_i = 10;
                        20: chroma_qlevel_i = 11;
                        21: chroma_qlevel_i = 11;
                        22: chroma_qlevel_i = 12;
                        23: chroma_qlevel_i = 12;
                        24: chroma_qlevel_i = 13;
                        25: chroma_qlevel_i = 14;
                        26: chroma_qlevel_i = 14;
                        27: chroma_qlevel_i = 14;
                        default: chroma_qlevel_i = 0;
                    endcase
                end
                16: begin
                    case (qp)
                        0: chroma_qlevel_i = 0;
                        1: chroma_qlevel_i = 1;
                        2: chroma_qlevel_i = 2;
                        3: chroma_qlevel_i = 2;
                        4: chroma_qlevel_i = 3;
                        5: chroma_qlevel_i = 3;
                        6: chroma_qlevel_i = 4;
                        7: chroma_qlevel_i = 4;
                        8: chroma_qlevel_i = 5;
                        9: chroma_qlevel_i = 5;
                        10: chroma_qlevel_i = 6;
                        11: chroma_qlevel_i = 6;
                        12: chroma_qlevel_i = 7;
                        13: chroma_qlevel_i = 7;
                        14: chroma_qlevel_i = 8;
                        15: chroma_qlevel_i = 8;
                        16: chroma_qlevel_i = 9;
                        17: chroma_qlevel_i = 9;
                        18: chroma_qlevel_i = 10;
                        19: chroma_qlevel_i = 10;
                        20: chroma_qlevel_i = 11;
                        21: chroma_qlevel_i = 11;
                        22: chroma_qlevel_i = 12;
                        23: chroma_qlevel_i = 12;
                        24: chroma_qlevel_i = 13;
                        25: chroma_qlevel_i = 13;
                        26: chroma_qlevel_i = 14;
                        27: chroma_qlevel_i = 14;
                        28: chroma_qlevel_i = 15;
                        29: chroma_qlevel_i = 16;
                        30: chroma_qlevel_i = 16;
                        31: chroma_qlevel_i = 16;
                        default: chroma_qlevel_i = 0;
                    endcase
                end
                default: chroma_qlevel_i = 0;
            endcase
        end
    endfunction
    function automatic integer sample_i;
        input integer component;
        input integer offset;
        begin
            sample_i = 0;
            case (component)
                0: begin
                    case (offset)
                        0: sample_i = {16'b0, orig_0_0};
                        1: sample_i = {16'b0, orig_0_1};
                        2: sample_i = {16'b0, orig_0_2};
                        3: sample_i = {16'b0, orig_0_3};
                        4: sample_i = {16'b0, orig_0_4};
                        5: sample_i = {16'b0, orig_0_5};
                        6: sample_i = {16'b0, orig_0_6};
                        default: sample_i = 0;
                    endcase
                end
                1: begin
                    case (offset)
                        0: sample_i = {16'b0, orig_1_0};
                        1: sample_i = {16'b0, orig_1_1};
                        2: sample_i = {16'b0, orig_1_2};
                        3: sample_i = {16'b0, orig_1_3};
                        4: sample_i = {16'b0, orig_1_4};
                        5: sample_i = {16'b0, orig_1_5};
                        6: sample_i = {16'b0, orig_1_6};
                        default: sample_i = 0;
                    endcase
                end
                2: begin
                    case (offset)
                        0: sample_i = {16'b0, orig_2_0};
                        1: sample_i = {16'b0, orig_2_1};
                        2: sample_i = {16'b0, orig_2_2};
                        3: sample_i = {16'b0, orig_2_3};
                        4: sample_i = {16'b0, orig_2_4};
                        5: sample_i = {16'b0, orig_2_5};
                        6: sample_i = {16'b0, orig_2_6};
                        default: sample_i = 0;
                    endcase
                end
                3: begin
                    case (offset)
                        0: sample_i = {16'b0, orig_3_0};
                        1: sample_i = {16'b0, orig_3_1};
                        2: sample_i = {16'b0, orig_3_2};
                        3: sample_i = {16'b0, orig_3_3};
                        4: sample_i = {16'b0, orig_3_4};
                        5: sample_i = {16'b0, orig_3_5};
                        6: sample_i = {16'b0, orig_3_6};
                        default: sample_i = 0;
                    endcase
                end
                default: sample_i = 0;
            endcase
        end
    endfunction
    function automatic integer spread4_i;
        input integer component;
        begin
            spread4_i = max_i(max_i(max_i(sample_i(component, 0), sample_i(component, 1)), sample_i(component, 2)), sample_i(component, 3)) - min_i(min_i(min_i(sample_i(component, 0), sample_i(component, 1)), sample_i(component, 2)), sample_i(component, 3));
        end
    endfunction
    function automatic integer spread6_i;
        input integer component;
        begin
            spread6_i = max_i(max_i(max_i(max_i(max_i(sample_i(component, 1), sample_i(component, 2)), sample_i(component, 3)), sample_i(component, 4)), sample_i(component, 5)), sample_i(component, 6)) - min_i(min_i(min_i(min_i(min_i(sample_i(component, 1), sample_i(component, 2)), sample_i(component, 3)), sample_i(component, 4)), sample_i(component, 5)), sample_i(component, 6));
        end
    endfunction
    function automatic integer qlevel_i;
        input integer component;
        integer adjusted_qp;
        begin
            adjusted_qp = {27'b0, primary_qp} - {29'b0, somewhat_flat_qp_delta};
            if (adjusted_qp < 0) adjusted_qp = 0;
            if ((component % 3) == 0) qlevel_i = luma_qlevel_i({27'b0, bits_per_component}, adjusted_qp);
            else if ((native_420 != 0) && (component == 1)) qlevel_i = luma_qlevel_i({27'b0, bits_per_component}, adjusted_qp);
            else begin qlevel_i = chroma_qlevel_i({27'b0, bits_per_component}, adjusted_qp);
                if ((dsc_version_minor == 2) && (cpnt_bit_depth_0 == cpnt_bit_depth_1) && (qlevel_i > 0)) qlevel_i = qlevel_i - 1;
            end
        end
    endfunction
    function automatic bit somewhat_flat4_i;
        input integer component;
        begin
            somewhat_flat4_i = spread4_i(component) <= max_i({22'b0, flatness_det_thresh}, quant_divisor_i(qlevel_i(component)));
        end
    endfunction
    function automatic bit very_flat4_i;
        input integer component;
        begin
            very_flat4_i = spread4_i(component) <= {22'b0, flatness_det_thresh};
        end
    endfunction
    function automatic bit somewhat_flat6_i;
        input integer component;
        begin
            somewhat_flat6_i = spread6_i(component) <= max_i({22'b0, flatness_det_thresh}, quant_divisor_i(qlevel_i(component)));
        end
    endfunction
    function automatic bit very_flat6_i;
        input integer component;
        begin
            very_flat6_i = spread6_i(component) <= {22'b0, flatness_det_thresh};
        end
    endfunction
    integer first_somewhat_i;
    integer first_very_i;
    integer second_somewhat_i;
    integer second_very_i;
    always_comb begin
        first_somewhat_i = 1;
        first_very_i = 1;
        second_somewhat_i = 1;
        second_very_i = 1;
        if (num_components > 0) begin
            if (somewhat_flat4_i(0) == 0) first_somewhat_i = 0;
            if (very_flat4_i(0) == 0) first_very_i = 0;
            if (somewhat_flat6_i(0) == 0) second_somewhat_i = 0;
            if (very_flat6_i(0) == 0) second_very_i = 0;
        end
        if (num_components > 1) begin
            if (somewhat_flat4_i(1) == 0) first_somewhat_i = 0;
            if (very_flat4_i(1) == 0) first_very_i = 0;
            if (somewhat_flat6_i(1) == 0) second_somewhat_i = 0;
            if (very_flat6_i(1) == 0) second_very_i = 0;
        end
        if (num_components > 2) begin
            if (somewhat_flat4_i(2) == 0) first_somewhat_i = 0;
            if (very_flat4_i(2) == 0) first_very_i = 0;
            if (somewhat_flat6_i(2) == 0) second_somewhat_i = 0;
            if (very_flat6_i(2) == 0) second_very_i = 0;
        end
        if (num_components > 3) begin
            if (somewhat_flat4_i(3) == 0) first_somewhat_i = 0;
            if (very_flat4_i(3) == 0) first_very_i = 0;
            if (somewhat_flat6_i(3) == 0) second_somewhat_i = 0;
            if (very_flat6_i(3) == 0) second_very_i = 0;
        end
        return_value = 0;
        if (hPos + 1 < slice_width) begin
            if (first_very_i != 0) return_value = 2;
            else if (first_somewhat_i != 0) return_value = 1;
            else if (hPos + 2 < slice_width) begin
                if (second_very_i != 0) return_value = 2;
                else if (second_somewhat_i != 0) return_value = 1;
            end
        end
    end
endmodule

module flatnessadjustment_decode_transition(
    input logic signed [31:0] hpos,
    input logic signed [31:0] qp,
    input logic signed [31:0] new_quant,
    input logic signed [31:0] cfg_dsc_version_minor,
    input logic signed [31:0] cfg_somewhat_flat_qp_delta,
    input logic signed [31:0] cfg_somewhat_flat_qp_thresh,
    input logic signed [31:0] cfg_very_flat_qp,
    input logic signed [31:0] cfg_bits_per_component,
    input logic signed [31:0] cfg_flatness_det_thresh,
    input logic signed [31:0] cfg_flatness_max_qp,
    input logic signed [31:0] cfg_flatness_min_qp,
    input logic signed [31:0] cfg_native_420,
    input logic signed [31:0] cfg_last_range_max_qp,
    input logic signed [31:0] state_firstflat,
    input logic signed [31:0] state_flatnesstype,
    input logic signed [31:0] state_groupcount,
    input logic signed [31:0] state_isencoder,
    input logic signed [31:0] state_origisflat,
    input logic signed [31:0] state_pixelsingroup,
    input logic signed [31:0] state_prevfirstflat,
    input logic signed [31:0] state_prevflatnesstype,
    input logic signed [31:0] state_previsflat,
    input logic signed [31:0] state_prevqp,
    input logic signed [31:0] state_primaryqp,
    input logic signed [31:0] state_slicewidth,
    input logic signed [31:0] state_stqp,
    input logic signed [31:0] state_numcomponents,
    input logic signed [31:0] state_cpntbitdepth_0,
    input logic signed [31:0] state_cpntbitdepth_1,
    input logic [15:0] orig_call_0_c0_0,
    input logic [15:0] orig_call_0_c0_1,
    input logic [15:0] orig_call_0_c0_2,
    input logic [15:0] orig_call_0_c0_3,
    input logic [15:0] orig_call_0_c0_4,
    input logic [15:0] orig_call_0_c0_5,
    input logic [15:0] orig_call_0_c0_6,
    input logic [15:0] orig_call_0_c1_0,
    input logic [15:0] orig_call_0_c1_1,
    input logic [15:0] orig_call_0_c1_2,
    input logic [15:0] orig_call_0_c1_3,
    input logic [15:0] orig_call_0_c1_4,
    input logic [15:0] orig_call_0_c1_5,
    input logic [15:0] orig_call_0_c1_6,
    input logic [15:0] orig_call_0_c2_0,
    input logic [15:0] orig_call_0_c2_1,
    input logic [15:0] orig_call_0_c2_2,
    input logic [15:0] orig_call_0_c2_3,
    input logic [15:0] orig_call_0_c2_4,
    input logic [15:0] orig_call_0_c2_5,
    input logic [15:0] orig_call_0_c2_6,
    input logic [15:0] orig_call_0_c3_0,
    input logic [15:0] orig_call_0_c3_1,
    input logic [15:0] orig_call_0_c3_2,
    input logic [15:0] orig_call_0_c3_3,
    input logic [15:0] orig_call_0_c3_4,
    input logic [15:0] orig_call_0_c3_5,
    input logic [15:0] orig_call_0_c3_6,
    input logic [15:0] orig_call_1_c0_0,
    input logic [15:0] orig_call_1_c0_1,
    input logic [15:0] orig_call_1_c0_2,
    input logic [15:0] orig_call_1_c0_3,
    input logic [15:0] orig_call_1_c0_4,
    input logic [15:0] orig_call_1_c0_5,
    input logic [15:0] orig_call_1_c0_6,
    input logic [15:0] orig_call_1_c1_0,
    input logic [15:0] orig_call_1_c1_1,
    input logic [15:0] orig_call_1_c1_2,
    input logic [15:0] orig_call_1_c1_3,
    input logic [15:0] orig_call_1_c1_4,
    input logic [15:0] orig_call_1_c1_5,
    input logic [15:0] orig_call_1_c1_6,
    input logic [15:0] orig_call_1_c2_0,
    input logic [15:0] orig_call_1_c2_1,
    input logic [15:0] orig_call_1_c2_2,
    input logic [15:0] orig_call_1_c2_3,
    input logic [15:0] orig_call_1_c2_4,
    input logic [15:0] orig_call_1_c2_5,
    input logic [15:0] orig_call_1_c2_6,
    input logic [15:0] orig_call_1_c3_0,
    input logic [15:0] orig_call_1_c3_1,
    input logic [15:0] orig_call_1_c3_2,
    input logic [15:0] orig_call_1_c3_3,
    input logic [15:0] orig_call_1_c3_4,
    input logic [15:0] orig_call_1_c3_5,
    input logic [15:0] orig_call_1_c3_6,
    input logic [15:0] orig_call_2_c0_0,
    input logic [15:0] orig_call_2_c0_1,
    input logic [15:0] orig_call_2_c0_2,
    input logic [15:0] orig_call_2_c0_3,
    input logic [15:0] orig_call_2_c0_4,
    input logic [15:0] orig_call_2_c0_5,
    input logic [15:0] orig_call_2_c0_6,
    input logic [15:0] orig_call_2_c1_0,
    input logic [15:0] orig_call_2_c1_1,
    input logic [15:0] orig_call_2_c1_2,
    input logic [15:0] orig_call_2_c1_3,
    input logic [15:0] orig_call_2_c1_4,
    input logic [15:0] orig_call_2_c1_5,
    input logic [15:0] orig_call_2_c1_6,
    input logic [15:0] orig_call_2_c2_0,
    input logic [15:0] orig_call_2_c2_1,
    input logic [15:0] orig_call_2_c2_2,
    input logic [15:0] orig_call_2_c2_3,
    input logic [15:0] orig_call_2_c2_4,
    input logic [15:0] orig_call_2_c2_5,
    input logic [15:0] orig_call_2_c2_6,
    input logic [15:0] orig_call_2_c3_0,
    input logic [15:0] orig_call_2_c3_1,
    input logic [15:0] orig_call_2_c3_2,
    input logic [15:0] orig_call_2_c3_3,
    input logic [15:0] orig_call_2_c3_4,
    input logic [15:0] orig_call_2_c3_5,
    input logic [15:0] orig_call_2_c3_6,
    input logic [15:0] orig_call_3_c0_0,
    input logic [15:0] orig_call_3_c0_1,
    input logic [15:0] orig_call_3_c0_2,
    input logic [15:0] orig_call_3_c0_3,
    input logic [15:0] orig_call_3_c0_4,
    input logic [15:0] orig_call_3_c0_5,
    input logic [15:0] orig_call_3_c0_6,
    input logic [15:0] orig_call_3_c1_0,
    input logic [15:0] orig_call_3_c1_1,
    input logic [15:0] orig_call_3_c1_2,
    input logic [15:0] orig_call_3_c1_3,
    input logic [15:0] orig_call_3_c1_4,
    input logic [15:0] orig_call_3_c1_5,
    input logic [15:0] orig_call_3_c1_6,
    input logic [15:0] orig_call_3_c2_0,
    input logic [15:0] orig_call_3_c2_1,
    input logic [15:0] orig_call_3_c2_2,
    input logic [15:0] orig_call_3_c2_3,
    input logic [15:0] orig_call_3_c2_4,
    input logic [15:0] orig_call_3_c2_5,
    input logic [15:0] orig_call_3_c2_6,
    input logic [15:0] orig_call_3_c3_0,
    input logic [15:0] orig_call_3_c3_1,
    input logic [15:0] orig_call_3_c3_2,
    input logic [15:0] orig_call_3_c3_3,
    input logic [15:0] orig_call_3_c3_4,
    input logic [15:0] orig_call_3_c3_5,
    input logic [15:0] orig_call_3_c3_6,
    output logic signed [31:0] state_firstflat_out,
    output logic signed [31:0] state_flatnesstype_out,
    output logic signed [31:0] state_origisflat_out,
    output logic signed [31:0] state_prevfirstflat_out,
    output logic signed [31:0] state_prevflatnesstype_out,
    output logic signed [31:0] state_previsflat_out,
    output logic signed [31:0] state_prevqp_out,
    output logic signed [31:0] state_stqp_out
);
    logic flatness_sent_i;
    logic found_i;
    logic ignored_new_quant_i;
    logic signed [31:0] call_h_0_i;
    logic [1:0] flatness_raw_0_i;
    logic [1:0] flatness_result_0_i;
    logic signed [31:0] call_h_1_i;
    logic [1:0] flatness_raw_1_i;
    logic [1:0] flatness_result_1_i;
    logic signed [31:0] call_h_2_i;
    logic [1:0] flatness_raw_2_i;
    logic [1:0] flatness_result_2_i;
    logic signed [31:0] call_h_3_i;
    logic [1:0] flatness_raw_3_i;
    logic [1:0] flatness_result_3_i;

    isflatnessinfosent u_flatness_interval(
        .qp(qp[4:0]),
        .flatness_min_qp(cfg_flatness_min_qp[4:0]),
        .flatness_max_qp(cfg_flatness_max_qp[4:0]),
        .return_value(flatness_sent_i)
    );
    isorigflathindex u_original_window_0(
        .hPos(call_h_0_i[15:0]),
        .bits_per_component(cfg_bits_per_component[4:0]),
        .primary_qp(state_primaryqp[4:0]),
        .num_components(state_numcomponents[2:0]),
        .slice_width(state_slicewidth[15:0]),
        .flatness_det_thresh(cfg_flatness_det_thresh[9:0]),
        .somewhat_flat_qp_delta(cfg_somewhat_flat_qp_delta[2:0]),
        .native_420(cfg_native_420[0]),
        .dsc_version_minor(cfg_dsc_version_minor[1:0]),
        .cpnt_bit_depth_0(state_cpntbitdepth_0[4:0]),
        .cpnt_bit_depth_1(state_cpntbitdepth_1[4:0]),
        .orig_0_0(orig_call_0_c0_0),
        .orig_0_1(orig_call_0_c0_1),
        .orig_0_2(orig_call_0_c0_2),
        .orig_0_3(orig_call_0_c0_3),
        .orig_0_4(orig_call_0_c0_4),
        .orig_0_5(orig_call_0_c0_5),
        .orig_0_6(orig_call_0_c0_6),
        .orig_1_0(orig_call_0_c1_0),
        .orig_1_1(orig_call_0_c1_1),
        .orig_1_2(orig_call_0_c1_2),
        .orig_1_3(orig_call_0_c1_3),
        .orig_1_4(orig_call_0_c1_4),
        .orig_1_5(orig_call_0_c1_5),
        .orig_1_6(orig_call_0_c1_6),
        .orig_2_0(orig_call_0_c2_0),
        .orig_2_1(orig_call_0_c2_1),
        .orig_2_2(orig_call_0_c2_2),
        .orig_2_3(orig_call_0_c2_3),
        .orig_2_4(orig_call_0_c2_4),
        .orig_2_5(orig_call_0_c2_5),
        .orig_2_6(orig_call_0_c2_6),
        .orig_3_0(orig_call_0_c3_0),
        .orig_3_1(orig_call_0_c3_1),
        .orig_3_2(orig_call_0_c3_2),
        .orig_3_3(orig_call_0_c3_3),
        .orig_3_4(orig_call_0_c3_4),
        .orig_3_5(orig_call_0_c3_5),
        .orig_3_6(orig_call_0_c3_6),
        .return_value(flatness_raw_0_i)
    );
    assign call_h_0_i = hpos + (state_pixelsingroup * 32'sd1);
    assign flatness_result_0_i = ((call_h_0_i + 32'sd1) >= state_slicewidth) ? 2'd0 : flatness_raw_0_i;

    isorigflathindex u_original_window_1(
        .hPos(call_h_1_i[15:0]),
        .bits_per_component(cfg_bits_per_component[4:0]),
        .primary_qp(state_primaryqp[4:0]),
        .num_components(state_numcomponents[2:0]),
        .slice_width(state_slicewidth[15:0]),
        .flatness_det_thresh(cfg_flatness_det_thresh[9:0]),
        .somewhat_flat_qp_delta(cfg_somewhat_flat_qp_delta[2:0]),
        .native_420(cfg_native_420[0]),
        .dsc_version_minor(cfg_dsc_version_minor[1:0]),
        .cpnt_bit_depth_0(state_cpntbitdepth_0[4:0]),
        .cpnt_bit_depth_1(state_cpntbitdepth_1[4:0]),
        .orig_0_0(orig_call_1_c0_0),
        .orig_0_1(orig_call_1_c0_1),
        .orig_0_2(orig_call_1_c0_2),
        .orig_0_3(orig_call_1_c0_3),
        .orig_0_4(orig_call_1_c0_4),
        .orig_0_5(orig_call_1_c0_5),
        .orig_0_6(orig_call_1_c0_6),
        .orig_1_0(orig_call_1_c1_0),
        .orig_1_1(orig_call_1_c1_1),
        .orig_1_2(orig_call_1_c1_2),
        .orig_1_3(orig_call_1_c1_3),
        .orig_1_4(orig_call_1_c1_4),
        .orig_1_5(orig_call_1_c1_5),
        .orig_1_6(orig_call_1_c1_6),
        .orig_2_0(orig_call_1_c2_0),
        .orig_2_1(orig_call_1_c2_1),
        .orig_2_2(orig_call_1_c2_2),
        .orig_2_3(orig_call_1_c2_3),
        .orig_2_4(orig_call_1_c2_4),
        .orig_2_5(orig_call_1_c2_5),
        .orig_2_6(orig_call_1_c2_6),
        .orig_3_0(orig_call_1_c3_0),
        .orig_3_1(orig_call_1_c3_1),
        .orig_3_2(orig_call_1_c3_2),
        .orig_3_3(orig_call_1_c3_3),
        .orig_3_4(orig_call_1_c3_4),
        .orig_3_5(orig_call_1_c3_5),
        .orig_3_6(orig_call_1_c3_6),
        .return_value(flatness_raw_1_i)
    );
    assign call_h_1_i = hpos + (state_pixelsingroup * 32'sd2);
    assign flatness_result_1_i = ((call_h_1_i + 32'sd1) >= state_slicewidth) ? 2'd0 : flatness_raw_1_i;

    isorigflathindex u_original_window_2(
        .hPos(call_h_2_i[15:0]),
        .bits_per_component(cfg_bits_per_component[4:0]),
        .primary_qp(state_primaryqp[4:0]),
        .num_components(state_numcomponents[2:0]),
        .slice_width(state_slicewidth[15:0]),
        .flatness_det_thresh(cfg_flatness_det_thresh[9:0]),
        .somewhat_flat_qp_delta(cfg_somewhat_flat_qp_delta[2:0]),
        .native_420(cfg_native_420[0]),
        .dsc_version_minor(cfg_dsc_version_minor[1:0]),
        .cpnt_bit_depth_0(state_cpntbitdepth_0[4:0]),
        .cpnt_bit_depth_1(state_cpntbitdepth_1[4:0]),
        .orig_0_0(orig_call_2_c0_0),
        .orig_0_1(orig_call_2_c0_1),
        .orig_0_2(orig_call_2_c0_2),
        .orig_0_3(orig_call_2_c0_3),
        .orig_0_4(orig_call_2_c0_4),
        .orig_0_5(orig_call_2_c0_5),
        .orig_0_6(orig_call_2_c0_6),
        .orig_1_0(orig_call_2_c1_0),
        .orig_1_1(orig_call_2_c1_1),
        .orig_1_2(orig_call_2_c1_2),
        .orig_1_3(orig_call_2_c1_3),
        .orig_1_4(orig_call_2_c1_4),
        .orig_1_5(orig_call_2_c1_5),
        .orig_1_6(orig_call_2_c1_6),
        .orig_2_0(orig_call_2_c2_0),
        .orig_2_1(orig_call_2_c2_1),
        .orig_2_2(orig_call_2_c2_2),
        .orig_2_3(orig_call_2_c2_3),
        .orig_2_4(orig_call_2_c2_4),
        .orig_2_5(orig_call_2_c2_5),
        .orig_2_6(orig_call_2_c2_6),
        .orig_3_0(orig_call_2_c3_0),
        .orig_3_1(orig_call_2_c3_1),
        .orig_3_2(orig_call_2_c3_2),
        .orig_3_3(orig_call_2_c3_3),
        .orig_3_4(orig_call_2_c3_4),
        .orig_3_5(orig_call_2_c3_5),
        .orig_3_6(orig_call_2_c3_6),
        .return_value(flatness_raw_2_i)
    );
    assign call_h_2_i = hpos + (state_pixelsingroup * 32'sd3);
    assign flatness_result_2_i = ((call_h_2_i + 32'sd1) >= state_slicewidth) ? 2'd0 : flatness_raw_2_i;

    isorigflathindex u_original_window_3(
        .hPos(call_h_3_i[15:0]),
        .bits_per_component(cfg_bits_per_component[4:0]),
        .primary_qp(state_primaryqp[4:0]),
        .num_components(state_numcomponents[2:0]),
        .slice_width(state_slicewidth[15:0]),
        .flatness_det_thresh(cfg_flatness_det_thresh[9:0]),
        .somewhat_flat_qp_delta(cfg_somewhat_flat_qp_delta[2:0]),
        .native_420(cfg_native_420[0]),
        .dsc_version_minor(cfg_dsc_version_minor[1:0]),
        .cpnt_bit_depth_0(state_cpntbitdepth_0[4:0]),
        .cpnt_bit_depth_1(state_cpntbitdepth_1[4:0]),
        .orig_0_0(orig_call_3_c0_0),
        .orig_0_1(orig_call_3_c0_1),
        .orig_0_2(orig_call_3_c0_2),
        .orig_0_3(orig_call_3_c0_3),
        .orig_0_4(orig_call_3_c0_4),
        .orig_0_5(orig_call_3_c0_5),
        .orig_0_6(orig_call_3_c0_6),
        .orig_1_0(orig_call_3_c1_0),
        .orig_1_1(orig_call_3_c1_1),
        .orig_1_2(orig_call_3_c1_2),
        .orig_1_3(orig_call_3_c1_3),
        .orig_1_4(orig_call_3_c1_4),
        .orig_1_5(orig_call_3_c1_5),
        .orig_1_6(orig_call_3_c1_6),
        .orig_2_0(orig_call_3_c2_0),
        .orig_2_1(orig_call_3_c2_1),
        .orig_2_2(orig_call_3_c2_2),
        .orig_2_3(orig_call_3_c2_3),
        .orig_2_4(orig_call_3_c2_4),
        .orig_2_5(orig_call_3_c2_5),
        .orig_2_6(orig_call_3_c2_6),
        .orig_3_0(orig_call_3_c3_0),
        .orig_3_1(orig_call_3_c3_1),
        .orig_3_2(orig_call_3_c3_2),
        .orig_3_3(orig_call_3_c3_3),
        .orig_3_4(orig_call_3_c3_4),
        .orig_3_5(orig_call_3_c3_5),
        .orig_3_6(orig_call_3_c3_6),
        .return_value(flatness_raw_3_i)
    );
    assign call_h_3_i = hpos + (state_pixelsingroup * 32'sd4);
    assign flatness_result_3_i = ((call_h_3_i + 32'sd1) >= state_slicewidth) ? 2'd0 : flatness_raw_3_i;

    always_comb begin
        state_firstflat_out = state_firstflat;
        state_flatnesstype_out = state_flatnesstype;
        state_origisflat_out = state_origisflat;
        state_prevfirstflat_out = state_prevfirstflat;
        state_prevflatnesstype_out = state_prevflatnesstype;
        state_previsflat_out = state_previsflat;
        state_prevqp_out = state_prevqp;
        state_stqp_out = state_stqp;
        found_i = 1'b0;
        ignored_new_quant_i = ^new_quant;
        if (state_isencoder != 0) begin
            if (flatness_sent_i && (state_groupcount[1:0] == 2'd3)) begin
                state_previsflat_out = (state_firstflat >= 0) ? 32'sd1 : 32'sd0;
                state_prevfirstflat_out = -32'sd1;
                if (!found_i) begin
                    if ((state_previsflat_out == 0) && (flatness_result_0_i != 0)) begin
                        state_prevfirstflat_out = 32'sd0;
                        state_prevflatnesstype_out = {30'd0, flatness_result_0_i} - 32'sd1;
                        found_i = 1'b1;
                    end else begin
                        state_previsflat_out = {30'd0, flatness_result_0_i};
                    end
                end
                if (!found_i) begin
                    if ((state_previsflat_out == 0) && (flatness_result_1_i != 0)) begin
                        state_prevfirstflat_out = 32'sd1;
                        state_prevflatnesstype_out = {30'd0, flatness_result_1_i} - 32'sd1;
                        found_i = 1'b1;
                    end else begin
                        state_previsflat_out = {30'd0, flatness_result_1_i};
                    end
                end
                if (!found_i) begin
                    if ((state_previsflat_out == 0) && (flatness_result_2_i != 0)) begin
                        state_prevfirstflat_out = 32'sd2;
                        state_prevflatnesstype_out = {30'd0, flatness_result_2_i} - 32'sd1;
                        found_i = 1'b1;
                    end else begin
                        state_previsflat_out = {30'd0, flatness_result_2_i};
                    end
                end
                if (!found_i) begin
                    if ((state_previsflat_out == 0) && (flatness_result_3_i != 0)) begin
                        state_prevfirstflat_out = 32'sd3;
                        state_prevflatnesstype_out = {30'd0, flatness_result_3_i} - 32'sd1;
                        found_i = 1'b1;
                    end else begin
                        state_previsflat_out = {30'd0, flatness_result_3_i};
                    end
                end
            end else if (!flatness_sent_i && (state_groupcount[1:0] == 2'd3)) begin
                state_prevfirstflat_out = -32'sd1;
            end else if (state_groupcount[1:0] == 2'd0) begin
                state_firstflat_out = state_prevfirstflat;
                state_flatnesstype_out = state_prevflatnesstype;
            end
            state_origisflat_out = 32'sd0;
            if ((state_firstflat_out >= 0) && (state_groupcount[1:0] == state_firstflat_out[1:0]))
                state_origisflat_out = 32'sd1;
        end
        if (cfg_dsc_version_minor == 32'sd1) begin
            if ((state_origisflat_out != 0) && (state_primaryqp < cfg_last_range_max_qp)) begin
                if ((state_flatnesstype_out == 0) || (state_primaryqp < cfg_somewhat_flat_qp_thresh)) begin
                    if (state_stqp > cfg_somewhat_flat_qp_delta)
                        state_stqp_out = state_stqp - cfg_somewhat_flat_qp_delta;
                    else state_stqp_out = 32'sd0;
                end else begin
                    state_stqp_out = cfg_very_flat_qp;
                end
            end
        end else begin
            if (hpos >= (state_slicewidth - 32'sd1)) begin
                state_origisflat_out = 32'sd1;
                state_flatnesstype_out = 32'sd1;
            end
            if ((state_origisflat_out != 0) && (state_primaryqp < cfg_last_range_max_qp)) begin
                if ((state_flatnesstype_out == 0) || (state_primaryqp < cfg_somewhat_flat_qp_thresh)) begin
                    if (state_stqp > cfg_somewhat_flat_qp_delta)
                        state_stqp_out = state_stqp - cfg_somewhat_flat_qp_delta;
                    else state_stqp_out = 32'sd0;
                    if (state_prevqp > cfg_somewhat_flat_qp_delta)
                        state_prevqp_out = state_prevqp - cfg_somewhat_flat_qp_delta;
                    else state_prevqp_out = 32'sd0;
                end else begin
                    state_stqp_out = cfg_very_flat_qp;
                    state_prevqp_out = cfg_very_flat_qp;
                end
            end
        end
    end
endmodule
