module getqpadjpredsize_interface (
    input logic [1:0] unit,
    input logic [1:0] dsc_version_minor,
    input logic native_420,
    input logic [1:0] unit_c_type_selected,
    input logic [4:0] predicted_size_selected,
    input logic [4:0] primary_qp,
    input logic [4:0] prev_primary_qp,
    input logic [4:0] cpntBitDepth_0,
    input logic [4:0] cpntBitDepth_1,
    input logic [4:0] cpntBitDepth_2,
    input logic [4:0] cpntBitDepth_3,
    input logic [4:0] qlevel_luma_new,
    input logic [4:0] qlevel_chroma_new,
    input logic [4:0] qlevel_luma_old,
    input logic [4:0] qlevel_chroma_old,
    output logic signed [4:0] return_value
);
endmodule
