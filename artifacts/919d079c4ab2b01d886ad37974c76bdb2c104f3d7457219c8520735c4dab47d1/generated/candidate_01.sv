module escapecodesize (
    input logic [4:0] qp,
    input logic [1:0] dsc_version_minor,
    input logic native_420,
    input logic [4:0] cpntBitDepth_0,
    input logic [4:0] qlevel_luma,
    output logic signed [5:0] return_value
);
    assign return_value = (cpntBitDepth_0 + 1 - qlevel_luma);
endmodule
