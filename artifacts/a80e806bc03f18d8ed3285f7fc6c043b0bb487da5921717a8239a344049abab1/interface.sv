module usingmidpoint_interface (
    input logic [1:0] unit,
    input logic [1:0] cpnt,
    input logic [1:0] dsc_version_minor,
    input logic native_420,
    input logic [4:0] primary_qp,
    input logic [4:0] cpntBitDepth_0,
    input logic [4:0] cpntBitDepth_1,
    input logic [4:0] cpntBitDepth_2,
    input logic [4:0] cpntBitDepth_3,
    input logic [4:0] cpntBitDepth_selected,
    input logic [4:0] qlevel_luma,
    input logic [4:0] qlevel_chroma,
    input logic signed [16:0] quantized_residual_0,
    input logic signed [16:0] quantized_residual_1,
    input logic signed [16:0] quantized_residual_2,
    output logic return_value
);
endmodule
