module ceil_log2_candidate_02 (
    input logic [15:0] val,
    output logic [4:0] return_value
);
    assign return_value = (($clog2(val + 1))) + 1;
endmodule
