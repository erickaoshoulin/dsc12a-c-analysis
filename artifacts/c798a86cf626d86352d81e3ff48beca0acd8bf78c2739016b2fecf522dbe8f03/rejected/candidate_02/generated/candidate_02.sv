module isorigflathindex_candidate_02 (
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
                        0: sample_i = orig_0_0;
                        1: sample_i = orig_0_1;
                        2: sample_i = orig_0_2;
                        3: sample_i = orig_0_3;
                        4: sample_i = orig_0_4;
                        5: sample_i = orig_0_5;
                        6: sample_i = orig_0_6;
                        default: sample_i = 0;
                    endcase
                end
                1: begin
                    case (offset)
                        0: sample_i = orig_1_0;
                        1: sample_i = orig_1_1;
                        2: sample_i = orig_1_2;
                        3: sample_i = orig_1_3;
                        4: sample_i = orig_1_4;
                        5: sample_i = orig_1_5;
                        6: sample_i = orig_1_6;
                        default: sample_i = 0;
                    endcase
                end
                2: begin
                    case (offset)
                        0: sample_i = orig_2_0;
                        1: sample_i = orig_2_1;
                        2: sample_i = orig_2_2;
                        3: sample_i = orig_2_3;
                        4: sample_i = orig_2_4;
                        5: sample_i = orig_2_5;
                        6: sample_i = orig_2_6;
                        default: sample_i = 0;
                    endcase
                end
                3: begin
                    case (offset)
                        0: sample_i = orig_3_0;
                        1: sample_i = orig_3_1;
                        2: sample_i = orig_3_2;
                        3: sample_i = orig_3_3;
                        4: sample_i = orig_3_4;
                        5: sample_i = orig_3_5;
                        6: sample_i = orig_3_6;
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
            adjusted_qp = primary_qp - somewhat_flat_qp_delta;
            if (adjusted_qp < 0) adjusted_qp = 0;
            if ((component % 3) == 0) qlevel_i = luma_qlevel_i(bits_per_component, adjusted_qp);
            else if ((native_420 != 0) && (component == 1)) qlevel_i = luma_qlevel_i(bits_per_component, adjusted_qp);
            else begin qlevel_i = chroma_qlevel_i(bits_per_component, adjusted_qp);
                if ((dsc_version_minor == 2) && (cpnt_bit_depth_0 == cpnt_bit_depth_1) && (qlevel_i > 0)) qlevel_i = qlevel_i - 1;
            end
        end
    endfunction
    function automatic integer somewhat_flat4_i;
        input integer component;
        begin
            somewhat_flat4_i = spread4_i(component) <= max_i(flatness_det_thresh, quant_divisor_i(qlevel_i(component)));
        end
    endfunction
    function automatic integer very_flat4_i;
        input integer component;
        begin
            very_flat4_i = spread4_i(component) <= flatness_det_thresh;
        end
    endfunction
    function automatic integer somewhat_flat6_i;
        input integer component;
        begin
            somewhat_flat6_i = spread6_i(component) <= max_i(flatness_det_thresh, quant_divisor_i(qlevel_i(component)));
        end
    endfunction
    function automatic integer very_flat6_i;
        input integer component;
        begin
            very_flat6_i = spread6_i(component) <= flatness_det_thresh;
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
        return_value = return_value + 1;
    end
endmodule
