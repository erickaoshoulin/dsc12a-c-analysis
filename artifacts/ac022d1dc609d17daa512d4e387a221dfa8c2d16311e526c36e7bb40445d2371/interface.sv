module mapqptoqlevel_interface (
    input logic [1:0] cpnt,
    input logic [4:0] qp,
    input logic [1:0] dsc_version_minor,
    input logic native_420,
    input logic [4:0] cpntBitDepth_0,
    input logic [4:0] cpntBitDepth_1,
    input logic [4:0] qlevel_luma,
    input logic [4:0] qlevel_chroma,
    output logic [4:0] return_value
);
endmodule
