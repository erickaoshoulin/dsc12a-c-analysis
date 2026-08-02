module samplepredict_candidate_01 (
    input logic [15:0] hPos,
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
    integer signed window_start_i;
    integer signed group_a_index_i;
    integer signed block_global_index_i;
    integer signed block_window_index_i;
    integer signed result_i;
    integer signed qr0_i;
    integer signed qr1_i;
    integer signed block_value_i;
    function automatic integer current_at_i;
        input integer index;
        begin
            case (index)
                0: current_at_i = curr_0;
                1: current_at_i = curr_1;
                2: current_at_i = curr_2;
                3: current_at_i = curr_3;
                4: current_at_i = curr_4;
                5: current_at_i = curr_5;
                6: current_at_i = curr_6;
                7: current_at_i = curr_7;
                8: current_at_i = curr_8;
                9: current_at_i = curr_9;
                10: current_at_i = curr_10;
                11: current_at_i = curr_11;
                12: current_at_i = curr_12;
                default: current_at_i = 0;
            endcase
        end
    endfunction
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
        window_start_i = (hPos > 8) ? (hPos - 8) : 0;
        group_a_index_i = ((hPos / 3) * 3) + 5 - 1 - window_start_i;
        a_i = current_at_i(group_a_index_i);
        b_i = prev_5;
        c_i = prev_4;
        d_i = prev_6;
        e_i = prev_7;
        filt_c_i = (prev_3 + (2 * prev_4) + prev_5 + 2) >>> 2;
        filt_b_i = (prev_4 + (2 * prev_5) + prev_6 + 2) >>> 2;
        filt_d_i = (prev_5 + (2 * prev_6) + prev_7 + 2) >>> 2;
        filt_e_i = (prev_6 + (2 * prev_7) + prev_8 + 2) >>> 2;
        block_global_index_i = hPos + 5 - 1 - (predType - 2);
        if (block_global_index_i < 0) block_global_index_i = 0;
        block_window_index_i = block_global_index_i - window_start_i;
        block_value_i = current_at_i(block_window_index_i);
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
