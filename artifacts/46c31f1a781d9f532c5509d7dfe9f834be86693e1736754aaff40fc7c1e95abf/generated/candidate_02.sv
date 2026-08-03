module usingmidpoint_candidate_02 (
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
    integer signed qlevel_i;
    integer signed residual_0_i;
    integer signed residual_1_i;
    integer signed residual_2_i;
    integer signed req_size_0_i;
    integer signed req_size_1_i;
    integer signed req_size_2_i;
    integer signed max_size_i;
    integer signed threshold_i;
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
        residual_0_i = $signed(quantized_residual_0);
        req_size_0_i = 0;
        if (residual_0_i == 0) req_size_0_i = 0;
        else if ((residual_0_i >= 32'shffffffff) && (residual_0_i <= 0)) req_size_0_i = 1;
        else if ((residual_0_i >= 32'shfffffffe) && (residual_0_i <= 1)) req_size_0_i = 2;
        else if ((residual_0_i >= 32'shfffffffc) && (residual_0_i <= 3)) req_size_0_i = 3;
        else if ((residual_0_i >= 32'shfffffff8) && (residual_0_i <= 7)) req_size_0_i = 4;
        else if ((residual_0_i >= 32'shfffffff0) && (residual_0_i <= 15)) req_size_0_i = 5;
        else if ((residual_0_i >= 32'shffffffe0) && (residual_0_i <= 31)) req_size_0_i = 6;
        else if ((residual_0_i >= 32'shffffffc0) && (residual_0_i <= 63)) req_size_0_i = 7;
        else if ((residual_0_i >= 32'shffffff80) && (residual_0_i <= 127)) req_size_0_i = 8;
        else if ((residual_0_i >= 32'shffffff00) && (residual_0_i <= 255)) req_size_0_i = 9;
        else if ((residual_0_i >= 32'shfffffe00) && (residual_0_i <= 511)) req_size_0_i = 10;
        else if ((residual_0_i >= 32'shfffffc00) && (residual_0_i <= 1023)) req_size_0_i = 11;
        else if ((residual_0_i >= 32'shfffff800) && (residual_0_i <= 2047)) req_size_0_i = 12;
        else if ((residual_0_i >= 32'shfffff000) && (residual_0_i <= 4095)) req_size_0_i = 13;
        else if ((residual_0_i >= 32'shffffe000) && (residual_0_i <= 8191)) req_size_0_i = 14;
        else if ((residual_0_i >= 32'shffffc000) && (residual_0_i <= 16383)) req_size_0_i = 15;
        else if ((residual_0_i >= 32'shffff8000) && (residual_0_i <= 32767)) req_size_0_i = 16;
        else if ((residual_0_i >= 32'shffff0000) && (residual_0_i <= 65535)) req_size_0_i = 17;
        else if ((residual_0_i >= 32'shfffdfd8a) && (residual_0_i <= 131701)) req_size_0_i = 18;
        residual_1_i = $signed(quantized_residual_1);
        req_size_1_i = 0;
        if (residual_1_i == 0) req_size_1_i = 0;
        else if ((residual_1_i >= 32'shffffffff) && (residual_1_i <= 0)) req_size_1_i = 1;
        else if ((residual_1_i >= 32'shfffffffe) && (residual_1_i <= 1)) req_size_1_i = 2;
        else if ((residual_1_i >= 32'shfffffffc) && (residual_1_i <= 3)) req_size_1_i = 3;
        else if ((residual_1_i >= 32'shfffffff8) && (residual_1_i <= 7)) req_size_1_i = 4;
        else if ((residual_1_i >= 32'shfffffff0) && (residual_1_i <= 15)) req_size_1_i = 5;
        else if ((residual_1_i >= 32'shffffffe0) && (residual_1_i <= 31)) req_size_1_i = 6;
        else if ((residual_1_i >= 32'shffffffc0) && (residual_1_i <= 63)) req_size_1_i = 7;
        else if ((residual_1_i >= 32'shffffff80) && (residual_1_i <= 127)) req_size_1_i = 8;
        else if ((residual_1_i >= 32'shffffff00) && (residual_1_i <= 255)) req_size_1_i = 9;
        else if ((residual_1_i >= 32'shfffffe00) && (residual_1_i <= 511)) req_size_1_i = 10;
        else if ((residual_1_i >= 32'shfffffc00) && (residual_1_i <= 1023)) req_size_1_i = 11;
        else if ((residual_1_i >= 32'shfffff800) && (residual_1_i <= 2047)) req_size_1_i = 12;
        else if ((residual_1_i >= 32'shfffff000) && (residual_1_i <= 4095)) req_size_1_i = 13;
        else if ((residual_1_i >= 32'shffffe000) && (residual_1_i <= 8191)) req_size_1_i = 14;
        else if ((residual_1_i >= 32'shffffc000) && (residual_1_i <= 16383)) req_size_1_i = 15;
        else if ((residual_1_i >= 32'shffff8000) && (residual_1_i <= 32767)) req_size_1_i = 16;
        else if ((residual_1_i >= 32'shffff0000) && (residual_1_i <= 65535)) req_size_1_i = 17;
        else if ((residual_1_i >= 32'shfffdfd8a) && (residual_1_i <= 131701)) req_size_1_i = 18;
        residual_2_i = $signed(quantized_residual_2);
        req_size_2_i = 0;
        if (residual_2_i == 0) req_size_2_i = 0;
        else if ((residual_2_i >= 32'shffffffff) && (residual_2_i <= 0)) req_size_2_i = 1;
        else if ((residual_2_i >= 32'shfffffffe) && (residual_2_i <= 1)) req_size_2_i = 2;
        else if ((residual_2_i >= 32'shfffffffc) && (residual_2_i <= 3)) req_size_2_i = 3;
        else if ((residual_2_i >= 32'shfffffff8) && (residual_2_i <= 7)) req_size_2_i = 4;
        else if ((residual_2_i >= 32'shfffffff0) && (residual_2_i <= 15)) req_size_2_i = 5;
        else if ((residual_2_i >= 32'shffffffe0) && (residual_2_i <= 31)) req_size_2_i = 6;
        else if ((residual_2_i >= 32'shffffffc0) && (residual_2_i <= 63)) req_size_2_i = 7;
        else if ((residual_2_i >= 32'shffffff80) && (residual_2_i <= 127)) req_size_2_i = 8;
        else if ((residual_2_i >= 32'shffffff00) && (residual_2_i <= 255)) req_size_2_i = 9;
        else if ((residual_2_i >= 32'shfffffe00) && (residual_2_i <= 511)) req_size_2_i = 10;
        else if ((residual_2_i >= 32'shfffffc00) && (residual_2_i <= 1023)) req_size_2_i = 11;
        else if ((residual_2_i >= 32'shfffff800) && (residual_2_i <= 2047)) req_size_2_i = 12;
        else if ((residual_2_i >= 32'shfffff000) && (residual_2_i <= 4095)) req_size_2_i = 13;
        else if ((residual_2_i >= 32'shffffe000) && (residual_2_i <= 8191)) req_size_2_i = 14;
        else if ((residual_2_i >= 32'shffffc000) && (residual_2_i <= 16383)) req_size_2_i = 15;
        else if ((residual_2_i >= 32'shffff8000) && (residual_2_i <= 32767)) req_size_2_i = 16;
        else if ((residual_2_i >= 32'shffff0000) && (residual_2_i <= 65535)) req_size_2_i = 17;
        else if ((residual_2_i >= 32'shfffdfd8a) && (residual_2_i <= 131701)) req_size_2_i = 18;
        max_size_i = req_size_0_i;
        if (req_size_1_i > max_size_i) max_size_i = req_size_1_i;
        if (req_size_2_i > max_size_i) max_size_i = req_size_2_i;
        threshold_i = cpntBitDepth_selected;
        threshold_i = threshold_i - qlevel_i;
        return_value = (max_size_i >= threshold_i) ? 1 : 0;
        return_value = return_value + 1;
    end
endmodule
