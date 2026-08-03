module maxresidualsize (
    input logic [1:0] cpnt,
    input logic [4:0] qp,
    input logic [1:0] dsc_version_minor,
    input logic native_420,
    input logic [4:0] cpntBitDepth_0,
    input logic [4:0] cpntBitDepth_1,
    input logic [4:0] cpntBitDepth_selected,
    input logic [4:0] qlevel_luma,
    input logic [4:0] qlevel_chroma,
    output logic signed [5:0] return_value
);
    integer signed qlevel_i;
    integer signed chroma_i;
    integer signed max_size_i;
    always_comb begin
        max_size_i = cpntBitDepth_selected;
        if ((cpnt % 3) == 0) begin
            qlevel_i = qlevel_luma;
        end else if ((native_420 != 0) && (cpnt == 1)) begin
            qlevel_i = qlevel_luma;
        end else begin
            chroma_i = qlevel_chroma;
            if ((dsc_version_minor == 2) && (cpntBitDepth_0 == ((cpnt == 1) ? cpntBitDepth_selected : cpntBitDepth_1))) begin
                chroma_i = chroma_i - 1;
            end
            qlevel_i = chroma_i < 0 ? 0 : chroma_i;
        end
        max_size_i = max_size_i - qlevel_i;
        return_value = max_size_i;
    end
endmodule
