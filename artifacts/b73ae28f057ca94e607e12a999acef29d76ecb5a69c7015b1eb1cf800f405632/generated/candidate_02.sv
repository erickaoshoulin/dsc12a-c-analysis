module findmidpoint_candidate_02 (
    input logic [1:0] cpnt,
    input logic [4:0] qlevel,
    input logic [4:0] cpntBitDepth,
    input logic [15:0] leftRecon,
    output logic [16:0] return_value
);
    assign return_value = (((1 << (cpntBitDepth - 1)) + (leftRecon % (1 << qlevel)))) + 1;
endmodule
