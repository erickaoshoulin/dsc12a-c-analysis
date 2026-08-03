module usingmidpoint_candidate_01 (
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
        else if ((residual_0_i >= -1) && (residual_0_i <= 0)) req_size_0_i = 1;
        else if ((residual_0_i >= -2) && (residual_0_i <= 1)) req_size_0_i = 2;
        else if ((residual_0_i >= -4) && (residual_0_i <= 3)) req_size_0_i = 3;
        else if ((residual_0_i >= -8) && (residual_0_i <= 7)) req_size_0_i = 4;
        else if ((residual_0_i >= -16) && (residual_0_i <= 15)) req_size_0_i = 5;
        else if ((residual_0_i >= -32) && (residual_0_i <= 31)) req_size_0_i = 6;
        else if ((residual_0_i >= -64) && (residual_0_i <= 63)) req_size_0_i = 7;
        else if ((residual_0_i >= -128) && (residual_0_i <= 127)) req_size_0_i = 8;
        else if ((residual_0_i >= -256) && (residual_0_i <= 255)) req_size_0_i = 9;
        else if ((residual_0_i >= -512) && (residual_0_i <= 511)) req_size_0_i = 10;
        else if ((residual_0_i >= -1024) && (residual_0_i <= 1023)) req_size_0_i = 11;
        else if ((residual_0_i >= -2048) && (residual_0_i <= 2047)) req_size_0_i = 12;
        else if ((residual_0_i >= -4096) && (residual_0_i <= 4095)) req_size_0_i = 13;
        else if ((residual_0_i >= -8192) && (residual_0_i <= 8191)) req_size_0_i = 14;
        else if ((residual_0_i >= -16384) && (residual_0_i <= 16383)) req_size_0_i = 15;
        else if ((residual_0_i >= -32768) && (residual_0_i <= 32767)) req_size_0_i = 16;
        else if ((residual_0_i >= -65536) && (residual_0_i <= 65535)) req_size_0_i = 17;
        else if ((residual_0_i >= -131702) && (residual_0_i <= 131701)) req_size_0_i = 18;
        residual_1_i = $signed(quantized_residual_1);
        req_size_1_i = 0;
        if (residual_1_i == 0) req_size_1_i = 0;
        else if ((residual_1_i >= -1) && (residual_1_i <= 0)) req_size_1_i = 1;
        else if ((residual_1_i >= -2) && (residual_1_i <= 1)) req_size_1_i = 2;
        else if ((residual_1_i >= -4) && (residual_1_i <= 3)) req_size_1_i = 3;
        else if ((residual_1_i >= -8) && (residual_1_i <= 7)) req_size_1_i = 4;
        else if ((residual_1_i >= -16) && (residual_1_i <= 15)) req_size_1_i = 5;
        else if ((residual_1_i >= -32) && (residual_1_i <= 31)) req_size_1_i = 6;
        else if ((residual_1_i >= -64) && (residual_1_i <= 63)) req_size_1_i = 7;
        else if ((residual_1_i >= -128) && (residual_1_i <= 127)) req_size_1_i = 8;
        else if ((residual_1_i >= -256) && (residual_1_i <= 255)) req_size_1_i = 9;
        else if ((residual_1_i >= -512) && (residual_1_i <= 511)) req_size_1_i = 10;
        else if ((residual_1_i >= -1024) && (residual_1_i <= 1023)) req_size_1_i = 11;
        else if ((residual_1_i >= -2048) && (residual_1_i <= 2047)) req_size_1_i = 12;
        else if ((residual_1_i >= -4096) && (residual_1_i <= 4095)) req_size_1_i = 13;
        else if ((residual_1_i >= -8192) && (residual_1_i <= 8191)) req_size_1_i = 14;
        else if ((residual_1_i >= -16384) && (residual_1_i <= 16383)) req_size_1_i = 15;
        else if ((residual_1_i >= -32768) && (residual_1_i <= 32767)) req_size_1_i = 16;
        else if ((residual_1_i >= -65536) && (residual_1_i <= 65535)) req_size_1_i = 17;
        else if ((residual_1_i >= -131702) && (residual_1_i <= 131701)) req_size_1_i = 18;
        residual_2_i = $signed(quantized_residual_2);
        req_size_2_i = 0;
        if (residual_2_i == 0) req_size_2_i = 0;
        else if ((residual_2_i >= -1) && (residual_2_i <= 0)) req_size_2_i = 1;
        else if ((residual_2_i >= -2) && (residual_2_i <= 1)) req_size_2_i = 2;
        else if ((residual_2_i >= -4) && (residual_2_i <= 3)) req_size_2_i = 3;
        else if ((residual_2_i >= -8) && (residual_2_i <= 7)) req_size_2_i = 4;
        else if ((residual_2_i >= -16) && (residual_2_i <= 15)) req_size_2_i = 5;
        else if ((residual_2_i >= -32) && (residual_2_i <= 31)) req_size_2_i = 6;
        else if ((residual_2_i >= -64) && (residual_2_i <= 63)) req_size_2_i = 7;
        else if ((residual_2_i >= -128) && (residual_2_i <= 127)) req_size_2_i = 8;
        else if ((residual_2_i >= -256) && (residual_2_i <= 255)) req_size_2_i = 9;
        else if ((residual_2_i >= -512) && (residual_2_i <= 511)) req_size_2_i = 10;
        else if ((residual_2_i >= -1024) && (residual_2_i <= 1023)) req_size_2_i = 11;
        else if ((residual_2_i >= -2048) && (residual_2_i <= 2047)) req_size_2_i = 12;
        else if ((residual_2_i >= -4096) && (residual_2_i <= 4095)) req_size_2_i = 13;
        else if ((residual_2_i >= -8192) && (residual_2_i <= 8191)) req_size_2_i = 14;
        else if ((residual_2_i >= -16384) && (residual_2_i <= 16383)) req_size_2_i = 15;
        else if ((residual_2_i >= -32768) && (residual_2_i <= 32767)) req_size_2_i = 16;
        else if ((residual_2_i >= -65536) && (residual_2_i <= 65535)) req_size_2_i = 17;
        else if ((residual_2_i >= -131702) && (residual_2_i <= 131701)) req_size_2_i = 18;
        max_size_i = req_size_0_i;
        if (req_size_1_i > max_size_i) max_size_i = req_size_1_i;
        if (req_size_2_i > max_size_i) max_size_i = req_size_2_i;
        threshold_i = cpntBitDepth_selected;
        threshold_i = threshold_i - qlevel_i;
        return_value = (max_size_i >= threshold_i) ? 1 : 0;
    end
endmodule
