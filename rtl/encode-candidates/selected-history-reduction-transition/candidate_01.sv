module pickbesthistoryvalue_encode_history_transition (
    input logic cfg_native_420,
    input logic cfg_native_422,
    input logic [1:0] cfg_dsc_version_minor,
    input logic signed [31:0] state_v_pos,
    input logic signed [31:0] state_num_components,
    input logic signed [31:0] state_pixels_in_group,
    input logic signed [31:0] state_slice_width,
    input logic signed [31:0] h_pos,
    input logic signed [31:0] history_valid [0:31],
    input logic [31:0] orig_0,
    input logic [31:0] orig_1,
    input logic [31:0] orig_2,
    input logic [31:0] orig_3,
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
    output logic signed [31:0] return_value,
    output logic search_failed,
    output logic illegal_domain
);
    integer j;
    logic signed [32:0] diff0_i;
    logic signed [32:0] diff1_i;
    logic signed [32:0] diff2_i;
    logic signed [32:0] diff3_i;
    logic signed [63:0] weighted_sad_i;
    logic signed [63:0] lowest_sad_i;
    logic signed [31:0] best_i;
    logic first_line_i;
    logic illegal_i;

    function automatic logic signed [32:0] abs_i33(input logic signed [32:0] value);
        begin
            if (value < 0)
                abs_i33 = -value;
            else
                abs_i33 = value;
        end
    endfunction

    always_comb begin
        return_value = 32'sd99;
        search_failed = 1'b1;
        illegal_domain = 1'b0;
        best_i = 32'sd99;
        lowest_sad_i = 64'sd1073741824;
        first_line_i = 1'b0;
        diff0_i = 33'sd0;
        diff1_i = 33'sd0;
        diff2_i = 33'sd0;
        diff3_i = 33'sd0;
        weighted_sad_i = 64'sd0;
        illegal_i = 1'b0;

        for (j = 0; j < 32; j = j + 1) begin
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
        if ((state_v_pos < 0) || (h_pos < 0) || (state_slice_width <= 0) || (h_pos >= state_slice_width)) illegal_i = 1'b1;
        if (((cfg_native_420 != 0) || (cfg_native_422 != 0)) && (state_slice_width < 5)) illegal_i = 1'b1;
        if ((cfg_native_420 == 0) && (cfg_native_422 == 0) && (state_slice_width < 7)) illegal_i = 1'b1;

        first_line_i = (state_v_pos == 0) || ((cfg_native_420 != 0) && (state_v_pos == 1));
        if (!illegal_i) begin
            for (j = 0; j < 32; j = j + 1) begin
                lookup_request_valid[j] = (history_valid[j] != 0);
                lookup_request_first_line[j] = first_line_i;
                lookup_request_is_odd_line[j] = (state_v_pos[0] != 0);
                if ((history_valid[j] != 0) && (history_lookup_result_valid[j] == 0))
                    illegal_i = 1'b1;
            end
        end

        if (!illegal_i) begin
            for (j = 0; j < 32; j = j + 1) begin
                if (history_valid[j] != 0) begin
                    diff0_i = $signed({1'b0, history_lookup_0[j]}) - $signed({1'b0, orig_0});
                    diff1_i = $signed({1'b0, history_lookup_1[j]}) - $signed({1'b0, orig_1});
                    diff2_i = $signed({1'b0, history_lookup_2[j]}) - $signed({1'b0, orig_2});
                    diff3_i = $signed({1'b0, history_lookup_3[j]}) - $signed({1'b0, orig_3});
                    if (cfg_native_422 != 0)
                        weighted_sad_i = (64'sd2 * abs_i33(diff0_i)) + abs_i33(diff1_i) + abs_i33(diff2_i) + (64'sd2 * abs_i33(diff3_i));
                    else if ((cfg_native_420 == 0) || (cfg_dsc_version_minor == 2'd1))
                        weighted_sad_i = (64'sd2 * abs_i33(diff0_i)) + abs_i33(diff1_i) + abs_i33(diff2_i);
                    else
                        weighted_sad_i = abs_i33(diff0_i) + abs_i33(diff1_i) + abs_i33(diff2_i);
                    if (lowest_sad_i > weighted_sad_i) begin
                        lowest_sad_i = weighted_sad_i;
                        best_i = j;
                    end
                end
            end
        end

        illegal_domain = illegal_i;
        if (!illegal_i) begin
            return_value = best_i;
            search_failed = (best_i == 32'sd99);
        end
    end
endmodule
