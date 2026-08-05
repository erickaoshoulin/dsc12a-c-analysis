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
