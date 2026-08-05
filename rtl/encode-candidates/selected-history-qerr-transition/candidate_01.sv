module isorigwithinqerr_encode_history_transition (
    input logic signed [31:0] cfg_bits_per_component,
    input logic cfg_native_420,
    input logic cfg_native_422,
    input logic [1:0] cfg_dsc_version_minor,
    input logic signed [31:0] state_v_pos,
    input logic signed [31:0] state_num_components,
    input logic signed [31:0] state_pixels_in_group,
    input logic signed [31:0] state_slice_width,
    input logic signed [31:0] h_pos,
    input logic signed [31:0] v_pos,
    input logic signed [31:0] qp,
    input logic signed [31:0] samp_mod_cnt,
    input logic signed [31:0] cpnt_bit_depth_0,
    input logic signed [31:0] cpnt_bit_depth_1,
    input logic signed [31:0] cpnt_bit_depth_2,
    input logic signed [31:0] cpnt_bit_depth_3,
    input logic signed [31:0] orig_within_qerr [0:5],
    input logic signed [31:0] history_valid [0:31],
    input logic signed [31:0] orig_line_sample_0,
    input logic signed [31:0] orig_line_sample_1,
    input logic signed [31:0] orig_line_sample_2,
    input logic signed [31:0] orig_line_sample_3,
    input logic [31:0] history_lookup_0 [0:31],
    input logic [31:0] history_lookup_1 [0:31],
    input logic [31:0] history_lookup_2 [0:31],
    input logic [31:0] history_lookup_3 [0:31],
    input logic history_lookup_result_valid [0:31],
    output logic lookup_request_valid [0:31],
    output logic [4:0] lookup_request_entry [0:31],
    output logic lookup_request_first_line [0:31],
    output logic lookup_request_is_odd_line [0:31],
    output logic signed [31:0] lookup_request_h_pos [0:31],
    input logic [4:0] map_qlevel [0:3],
    output logic map_request_valid [0:3],
    output logic [4:0] map_request_qp,
    output logic [1:0] map_request_cpnt [0:3],
    output logic signed [31:0] max_qerr [0:3],
    output logic signed [31:0] orig_within_qerr_out [0:5],
    output logic signed [31:0] history_valid_out [0:31],
    output logic signed [31:0] return_value,
    output logic illegal_domain
);
    integer i;
    integer j;
    logic signed [32:0] diff_i;
    logic signed [32:0] absdiff_i;
    logic signed [31:0] max_qerr_i [0:3];
    logic signed [31:0] history_valid_next [0:31];
    logic signed [31:0] orig_within_next [0:5];
    logic signed [63:0] qp_candidate_i;
    logic signed [63:0] modified_qp_i;
    logic first_line_i;
    logic candidate_hit_i;
    logic found_i;
    logic illegal_i;
    logic signed [31:0] quant_divisor_i;

    function automatic logic signed [32:0] abs_i33(input logic signed [32:0] value);
        begin
            if (value < 0)
                abs_i33 = -value;
            else
                abs_i33 = value;
        end
    endfunction

    function automatic logic signed [31:0] quant_divisor(input logic [4:0] qlevel);
        begin
            quant_divisor = 32'sd0;
            case (qlevel)
            5'd0: quant_divisor = 32'sd1;
            5'd1: quant_divisor = 32'sd2;
            5'd2: quant_divisor = 32'sd4;
            5'd3: quant_divisor = 32'sd8;
            5'd4: quant_divisor = 32'sd16;
            5'd5: quant_divisor = 32'sd32;
            5'd6: quant_divisor = 32'sd64;
            5'd7: quant_divisor = 32'sd128;
            5'd8: quant_divisor = 32'sd256;
            5'd9: quant_divisor = 32'sd512;
            5'd10: quant_divisor = 32'sd1024;
            5'd11: quant_divisor = 32'sd2048;
            5'd12: quant_divisor = 32'sd4096;
            5'd13: quant_divisor = 32'sd8192;
            5'd14: quant_divisor = 32'sd16384;
            5'd15: quant_divisor = 32'sd32768;
            5'd16: quant_divisor = 32'sd65536;
                default: quant_divisor = 32'sd0;
            endcase
        end
    endfunction

    always_comb begin
        return_value = 32'sd0;
        illegal_domain = 1'b0;
        illegal_i = 1'b0;
        found_i = 1'b0;
        candidate_hit_i = 1'b0;
        first_line_i = 1'b0;
        qp_candidate_i = 64'sd0;
        modified_qp_i = 64'sd0;
        diff_i = 33'sd0;
        absdiff_i = 33'sd0;
        quant_divisor_i = 32'sd0;
        map_request_qp = 5'd0;

        for (i = 0; i < 4; i = i + 1) begin
            max_qerr_i[i] = 32'sd0;
            max_qerr[i] = 32'sd0;
            map_request_valid[i] = 1'b0;
            map_request_cpnt[i] = i[1:0];
        end
        for (i = 0; i < 6; i = i + 1)
            orig_within_next[i] = orig_within_qerr[i];
        for (j = 0; j < 32; j = j + 1) begin
            history_valid_next[j] = history_valid[j];
            lookup_request_valid[j] = 1'b0;
            lookup_request_entry[j] = j[4:0];
            lookup_request_first_line[j] = 1'b0;
            lookup_request_is_odd_line[j] = 1'b0;
            lookup_request_h_pos[j] = h_pos;
        end

        if ((cfg_native_420 != 0) && (cfg_native_422 != 0)) illegal_i = 1'b1;
        if (!((state_num_components == 32'sd3) || (state_num_components == 32'sd4))) illegal_i = 1'b1;
        if ((cfg_native_422 != 0) && (state_num_components != 32'sd4)) illegal_i = 1'b1;
        if ((cfg_native_422 == 0) && (state_num_components != 32'sd3)) illegal_i = 1'b1;
        if (state_pixels_in_group != 32'sd3) illegal_i = 1'b1;
        if ((samp_mod_cnt < 0) || (samp_mod_cnt >= 6)) illegal_i = 1'b1;
        if ((h_pos < 0) || (v_pos < 0) || (state_v_pos < 0) || (state_slice_width <= 0) || (h_pos >= state_slice_width)) illegal_i = 1'b1;
        if (((cfg_native_420 != 0) || (cfg_native_422 != 0)) && (state_slice_width < 5)) illegal_i = 1'b1;
        if ((cfg_native_420 == 0) && (cfg_native_422 == 0) && (state_slice_width < 7)) illegal_i = 1'b1;
        if ((cfg_bits_per_component != 32'sd8) && (cfg_bits_per_component != 32'sd10) && (cfg_bits_per_component != 32'sd12) && (cfg_bits_per_component != 32'sd14) && (cfg_bits_per_component != 32'sd16)) illegal_i = 1'b1;
        if ((qp < 0) || (qp > 31)) illegal_i = 1'b1;

        // The C function clears the selected slot before either early return.
        if ((samp_mod_cnt >= 0) && (samp_mod_cnt < 6))
            orig_within_next[samp_mod_cnt] = 32'sd0;

        if (!illegal_i && !((h_pos == 0) && (v_pos == 0))) begin
            qp_candidate_i = (64'sd2 * cfg_bits_per_component) - 64'sd1;
            modified_qp_i = qp + 64'sd2;
            if (modified_qp_i > qp_candidate_i)
                modified_qp_i = qp_candidate_i;
            map_request_qp = modified_qp_i[4:0];
            for (i = 0; i < 4; i = i + 1) begin
                map_request_valid[i] = (i < state_num_components);
                if (map_request_valid[i] && (map_qlevel[i] > 5'd16))
                    illegal_i = 1'b1;
                if (map_request_valid[i]) begin
                    quant_divisor_i = quant_divisor(map_qlevel[i]);
                    max_qerr_i[i] = quant_divisor_i >>> 1;
                    max_qerr[i] = max_qerr_i[i];
                end
            end

            // Source order: update UL/U/UR validity, then scan history.
            if (((cfg_native_420 == 0) && (state_v_pos > 0)) || ((cfg_native_420 != 0) && (state_v_pos > 1))) begin
                for (i = 25; i < 32; i = i + 1)
                    history_valid_next[i] = 32'sd1;
            end

            first_line_i = (v_pos == 0) || ((cfg_native_420 != 0) && (v_pos == 1));
            for (j = 0; j < 32; j = j + 1) begin
                lookup_request_valid[j] = (history_valid_next[j] != 0);
                lookup_request_first_line[j] = first_line_i;
                lookup_request_is_odd_line[j] = (v_pos[0] != 0);
                if ((history_valid_next[j] != 0) && (history_lookup_result_valid[j] == 0))
                    illegal_i = 1'b1;
                if (history_valid_next[j] != 0) begin
                    candidate_hit_i = 1'b1;
                    for (i = 0; i < 4; i = i + 1) begin
                        if (i < state_num_components) begin
                            case (i)
                                0: diff_i = $signed({1'b0, history_lookup_0[j]}) - $signed({orig_line_sample_0[31], orig_line_sample_0});
                                1: diff_i = $signed({1'b0, history_lookup_1[j]}) - $signed({orig_line_sample_1[31], orig_line_sample_1});
                                2: diff_i = $signed({1'b0, history_lookup_2[j]}) - $signed({orig_line_sample_2[31], orig_line_sample_2});
                                default: diff_i = $signed({1'b0, history_lookup_3[j]}) - $signed({orig_line_sample_3[31], orig_line_sample_3});
                            endcase
                            absdiff_i = abs_i33(diff_i);
                            if (absdiff_i > max_qerr_i[i])
                                candidate_hit_i = 1'b0;
                        end
                    end
                    if (candidate_hit_i && !found_i)
                        found_i = 1'b1;
                end
            end
            if (found_i) begin
                orig_within_next[samp_mod_cnt] = 32'sd1;
                return_value = 32'sd1;
            end
        end

        illegal_domain = illegal_i;
        for (i = 0; i < 6; i = i + 1)
            orig_within_qerr_out[i] = orig_within_next[i];
        for (j = 0; j < 32; j = j + 1)
            history_valid_out[j] = history_valid_next[j];
        if (illegal_i)
            return_value = 32'sd0;
    end
endmodule
