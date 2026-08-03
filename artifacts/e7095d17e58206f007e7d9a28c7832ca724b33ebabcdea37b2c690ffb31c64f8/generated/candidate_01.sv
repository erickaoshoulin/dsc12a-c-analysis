module samplepredict_candidate_01 (
    input logic [3:0] hPos,
    input logic [3:0] predType,
    input logic [4:0] qLevel,
    input logic [1:0] unit,
    input logic [4:0] cpnt_bit_depth,
    input logic [1:0] unit_c_type,
    input logic signed [15:0] quantized_residual_0,
    input logic signed [15:0] quantized_residual_1,
    input logic [15:0] prev_3,
    input logic [15:0] prev_4,
    input logic [15:0] prev_5,
    input logic [15:0] prev_6,
    input logic [15:0] prev_7,
    input logic [15:0] prev_8,
    input logic [15:0] prev_9,
    input logic [15:0] prev_10,
    input logic [15:0] prev_11,
    input logic [15:0] prev_12,
    input logic [15:0] prev_13,
    input logic [15:0] prev_14,
    input logic [15:0] prev_15,
    input logic [15:0] prev_16,
    input logic [15:0] prev_17,
    input logic [15:0] curr_0,
    input logic [15:0] curr_1,
    input logic [15:0] curr_2,
    input logic [15:0] curr_3,
    input logic [15:0] curr_4,
    input logic [15:0] curr_5,
    input logic [15:0] curr_6,
    input logic [15:0] curr_7,
    input logic [15:0] curr_8,
    input logic [15:0] curr_9,
    input logic [15:0] curr_10,
    input logic [15:0] curr_11,
    input logic [15:0] curr_12,
    input logic [15:0] curr_13,
    input logic [15:0] curr_14,
    input logic [15:0] curr_15,
    output logic [15:0] return_value
);
    integer signed a_i;
    integer signed b_i;
    integer signed c_i;
    integer signed d_i;
    integer signed e_i;
    integer signed filt_c_i;
    integer signed filt_b_i;
    integer signed filt_d_i;
    integer signed filt_e_i;
    integer signed blend_b_i;
    integer signed blend_c_i;
    integer signed blend_d_i;
    integer signed blend_e_i;
    integer signed diff_i;
    integer signed qdiv_i;
    integer signed qhalf_i;
    integer signed cpnt_max_i;
    integer signed bp_index_i;
    integer signed result_i;
    integer signed qr0_i;
    integer signed qr1_i;
    integer signed block_value_i;
    function automatic integer clamp_i;
        input integer value;
        input integer lower;
        input integer upper;
        begin
            if (value < lower) clamp_i = lower;
            else if (value > upper) clamp_i = upper;
            else clamp_i = value;
        end
    endfunction
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
    always_comb begin
        case (hPos / 3)
            0: begin
                a_i = curr_4;
                b_i = prev_5;
                c_i = prev_4;
                d_i = prev_6;
                e_i = prev_7;
                filt_c_i = (prev_3 + (2 * prev_4) + prev_5 + 2) >>> 2;
                filt_b_i = (prev_4 + (2 * prev_5) + prev_6 + 2) >>> 2;
                filt_d_i = (prev_5 + (2 * prev_6) + prev_7 + 2) >>> 2;
                filt_e_i = (prev_6 + (2 * prev_7) + prev_8 + 2) >>> 2;
            end
            1: begin
                a_i = curr_7;
                b_i = prev_8;
                c_i = prev_7;
                d_i = prev_9;
                e_i = prev_10;
                filt_c_i = (prev_6 + (2 * prev_7) + prev_8 + 2) >>> 2;
                filt_b_i = (prev_7 + (2 * prev_8) + prev_9 + 2) >>> 2;
                filt_d_i = (prev_8 + (2 * prev_9) + prev_10 + 2) >>> 2;
                filt_e_i = (prev_9 + (2 * prev_10) + prev_11 + 2) >>> 2;
            end
            2: begin
                a_i = curr_10;
                b_i = prev_11;
                c_i = prev_10;
                d_i = prev_12;
                e_i = prev_13;
                filt_c_i = (prev_9 + (2 * prev_10) + prev_11 + 2) >>> 2;
                filt_b_i = (prev_10 + (2 * prev_11) + prev_12 + 2) >>> 2;
                filt_d_i = (prev_11 + (2 * prev_12) + prev_13 + 2) >>> 2;
                filt_e_i = (prev_12 + (2 * prev_13) + prev_14 + 2) >>> 2;
            end
            3: begin
                a_i = curr_13;
                b_i = prev_14;
                c_i = prev_13;
                d_i = prev_15;
                e_i = prev_16;
                filt_c_i = (prev_12 + (2 * prev_13) + prev_14 + 2) >>> 2;
                filt_b_i = (prev_13 + (2 * prev_14) + prev_15 + 2) >>> 2;
                filt_d_i = (prev_14 + (2 * prev_15) + prev_16 + 2) >>> 2;
                filt_e_i = (prev_15 + (2 * prev_16) + prev_17 + 2) >>> 2;
            end
            default: begin
                a_i = curr_4;
                b_i = prev_5;
                c_i = prev_4;
                d_i = prev_6;
                e_i = prev_7;
                filt_c_i = (prev_3 + (2 * prev_4) + prev_5 + 2) >>> 2;
                filt_b_i = (prev_4 + (2 * prev_5) + prev_6 + 2) >>> 2;
                filt_d_i = (prev_5 + (2 * prev_6) + prev_7 + 2) >>> 2;
                filt_e_i = (prev_6 + (2 * prev_7) + prev_8 + 2) >>> 2;
            end
        endcase
        qdiv_i = 1 <<< qLevel;
        qhalf_i = qdiv_i / 2;
        cpnt_max_i = (1 <<< cpnt_bit_depth) - 1;
        qr0_i = $signed(quantized_residual_0);
        qr1_i = $signed(quantized_residual_1);
        diff_i = 0;
        blend_b_i = b_i;
        blend_c_i = c_i;
        blend_d_i = d_i;
        blend_e_i = e_i;
        result_i = 0;
        block_value_i = 0;
        bp_index_i = hPos + 4 - (predType - 2);
        if (bp_index_i < 0) bp_index_i = 0;
        case (bp_index_i)
            0: block_value_i = curr_0;
            1: block_value_i = curr_1;
            2: block_value_i = curr_2;
            3: block_value_i = curr_3;
            4: block_value_i = curr_4;
            5: block_value_i = curr_5;
            6: block_value_i = curr_6;
            7: block_value_i = curr_7;
            8: block_value_i = curr_8;
            9: block_value_i = curr_9;
            10: block_value_i = curr_10;
            11: block_value_i = curr_11;
            12: block_value_i = curr_12;
            13: block_value_i = curr_13;
            14: block_value_i = curr_14;
            15: block_value_i = curr_15;
            default: block_value_i = 0;
        endcase
        diff_i = clamp_i(filt_c_i - c_i, -qhalf_i, qhalf_i);
        blend_c_i = c_i + diff_i;
        diff_i = clamp_i(filt_b_i - b_i, -qhalf_i, qhalf_i);
        blend_b_i = b_i + diff_i;
        diff_i = clamp_i(filt_d_i - d_i, -qhalf_i, qhalf_i);
        blend_d_i = d_i + diff_i;
        diff_i = clamp_i(filt_e_i - e_i, -qhalf_i, qhalf_i);
        blend_e_i = e_i + diff_i;
        if ((hPos / 3) == 0) blend_c_i = a_i;
        if (predType == 0) begin
            if ((hPos % 3) == 0)
                result_i = clamp_i(a_i + blend_b_i - blend_c_i, min_i(a_i, blend_b_i), max_i(a_i, blend_b_i));
            else if ((hPos % 3) == 1)
                result_i = clamp_i(a_i + blend_d_i - blend_c_i + (qr0_i * qdiv_i), min_i(a_i, min_i(blend_b_i, blend_d_i)), max_i(a_i, max_i(blend_b_i, blend_d_i)));
            else
                result_i = clamp_i(a_i + blend_e_i - blend_c_i + ((qr0_i + qr1_i) * qdiv_i), min_i(a_i, min_i(blend_b_i, min_i(blend_d_i, blend_e_i))), max_i(a_i, max_i(blend_b_i, max_i(blend_d_i, blend_e_i))));
        end else if (predType == 1) begin
            if ((hPos % 3) == 0) result_i = a_i;
            else if ((hPos % 3) == 1) result_i = clamp_i(a_i + (qr0_i * qdiv_i), 0, cpnt_max_i);
            else result_i = clamp_i(a_i + ((qr0_i + qr1_i) * qdiv_i), 0, cpnt_max_i);
        end else begin
            result_i = block_value_i;
        end
        return_value = result_i;
    end
endmodule
