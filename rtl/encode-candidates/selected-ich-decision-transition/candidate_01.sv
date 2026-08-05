module ichdecision_encode_transition(
    input logic signed [31:0] adjusted_predicted_size,
    input logic signed [31:0] alternate_prefix,
    input logic signed [31:0] alternate_size,
    input logic signed [31:0] version_minor,
    input logic signed [31:0] units_per_group,
    input logic signed [31:0] previous_ich_selected,
    input logic signed [31:0] ich_indices_in_group,
    input logic signed [31:0] max_mid_error_0,
    input logic signed [31:0] max_mid_error_1,
    input logic signed [31:0] max_mid_error_2,
    input logic signed [31:0] max_mid_error_3,
    input logic signed [31:0] max_error_0,
    input logic signed [31:0] max_error_1,
    input logic signed [31:0] max_error_2,
    input logic signed [31:0] max_error_3,
    input logic signed [31:0] max_ich_error_0,
    input logic signed [31:0] max_ich_error_1,
    input logic signed [31:0] max_ich_error_2,
    input logic signed [31:0] max_ich_error_3,
    input logic signed [31:0] using_midpoint_0,
    input logic signed [31:0] using_midpoint_1,
    input logic signed [31:0] using_midpoint_2,
    input logic signed [31:0] using_midpoint_3,
    input logic signed [31:0] estimated_p_mode_bits,
    input logic signed [31:0] original_flat_index,
    output logic return_value
);

    logic signed [31:0] log_error_p_mode;
    logic signed [31:0] log_error_ich_mode;
    logic signed [31:0] bits_ich_mode;
    logic signed [31:0] p_mode_cost;
    logic signed [31:0] ich_mode_cost;

    function automatic signed [31:0] c_ceil_log2(
        input logic signed [31:0] value
    );
        logic [31:0] x;
        integer bit_index;
        begin
            x = value[31:0];
            c_ceil_log2 = 32'sd0;
            for (bit_index = 0; bit_index < 32; bit_index = bit_index + 1) begin
                if (x != 0) begin
                    c_ceil_log2 = c_ceil_log2 + 32'sd1;
                    x = x >> 1;
                end
            end
        end
    endfunction

    always_comb begin
        if (previous_ich_selected != 0)
            bits_ich_mode = 32'sd1;
        else
            bits_ich_mode = alternate_size - adjusted_predicted_size;
        bits_ich_mode = bits_ich_mode + (32'sd5 * ich_indices_in_group) + (alternate_prefix & 32'sd0);
        log_error_p_mode = 32'sd0;
        log_error_ich_mode = 32'sd0;
        if (units_per_group > 32'sd0) begin
            if (using_midpoint_0 != 0)
                log_error_p_mode = log_error_p_mode + c_ceil_log2(max_mid_error_0);
            else
                log_error_p_mode = log_error_p_mode + c_ceil_log2(max_error_0);
            log_error_ich_mode = log_error_ich_mode + c_ceil_log2(max_ich_error_0);
            if (version_minor == 32'sd1) begin
                log_error_p_mode = log_error_p_mode * 32'sd2;
                log_error_ich_mode = log_error_ich_mode * 32'sd2;
            end
        end
        if (units_per_group > 32'sd1) begin
            if (using_midpoint_1 != 0)
                log_error_p_mode = log_error_p_mode + c_ceil_log2(max_mid_error_1);
            else
                log_error_p_mode = log_error_p_mode + c_ceil_log2(max_error_1);
            log_error_ich_mode = log_error_ich_mode + c_ceil_log2(max_ich_error_1);
        end
        if (units_per_group > 32'sd2) begin
            if (using_midpoint_2 != 0)
                log_error_p_mode = log_error_p_mode + c_ceil_log2(max_mid_error_2);
            else
                log_error_p_mode = log_error_p_mode + c_ceil_log2(max_error_2);
            log_error_ich_mode = log_error_ich_mode + c_ceil_log2(max_ich_error_2);
        end
        if (units_per_group > 32'sd3) begin
            if (using_midpoint_3 != 0)
                log_error_p_mode = log_error_p_mode + c_ceil_log2(max_mid_error_3);
            else
                log_error_p_mode = log_error_p_mode + c_ceil_log2(max_error_3);
            log_error_ich_mode = log_error_ich_mode + c_ceil_log2(max_ich_error_3);
        end
        p_mode_cost = estimated_p_mode_bits + (32'sd4 * log_error_p_mode);
        ich_mode_cost = bits_ich_mode + (32'sd4 * log_error_ich_mode);
        if (version_minor == 32'sd2) begin
            if (original_flat_index == 32'sd2)
                return_value = (log_error_ich_mode <= log_error_p_mode) && (ich_mode_cost < p_mode_cost);
            else
                return_value = ich_mode_cost < p_mode_cost;
        end else begin
            return_value = (log_error_ich_mode <= log_error_p_mode) && (ich_mode_cost < p_mode_cost);
        end
    end
endmodule
