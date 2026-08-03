module ceil_log2_candidate_02 (
    input logic [15:0] val,
    output logic [4:0] return_value
);
    logic [31:0] expression_wide;
    assign expression_wide = ($clog2(val + 1));
    assign return_value = expression_wide[4:0] + 5'd1;
endmodule
