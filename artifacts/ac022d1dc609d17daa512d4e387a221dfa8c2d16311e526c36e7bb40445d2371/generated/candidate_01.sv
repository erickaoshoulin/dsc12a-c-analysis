module mapqptoqlevel_candidate_01 (
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
    integer signed qlevel_i;
    always_comb begin
        if ((cpnt % 3) == 0) begin
            qlevel_i = qlevel_luma;
        end else if ((native_420 != 0) && (cpnt == 1)) begin
            qlevel_i = qlevel_luma;
        end else begin
            qlevel_i = qlevel_chroma;
            if ((dsc_version_minor == 2) && (cpntBitDepth_0 == cpntBitDepth_1) && (qlevel_i > 0)) begin
                qlevel_i = qlevel_i - 1;
            end
        end
        return_value = qlevel_i;
    end
endmodule
