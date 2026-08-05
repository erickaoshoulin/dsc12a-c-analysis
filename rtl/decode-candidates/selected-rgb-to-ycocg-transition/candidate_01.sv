module rgb2ycocg_pixel_transition(
    input logic signed [31:0] bits,
    input logic signed [31:0] input_channel_0,
    input logic signed [31:0] input_channel_1,
    input logic signed [31:0] input_channel_2,
    output logic domain_valid,
    output logic signed [31:0] output_channel_0,
    output logic signed [31:0] output_channel_1,
    output logic signed [31:0] output_channel_2
);
    logic signed [31:0] half_i, max_i;
    logic signed [31:0] co_i, cg_i, temp_i;
    logic signed [31:0] r_i, g_i, b_i, y_i;
    always_comb begin
        domain_valid = 1'b1;
        output_channel_0 = 32'sd0;
        output_channel_1 = 32'sd0;
        output_channel_2 = 32'sd0;
        half_i = 32'sd0; max_i = 32'sd0;
        co_i = 32'sd0; cg_i = 32'sd0; temp_i = 32'sd0;
        r_i = 32'sd0; g_i = 32'sd0; b_i = 32'sd0; y_i = 32'sd0;
        if (($signed(bits) < 32'sd8) || ($signed(bits) > 32'sd16)) domain_valid = 1'b0;
        half_i = 32'sd1 <<< ($signed(bits) - 32'sd1);
        r_i = input_channel_0; g_i = input_channel_1; b_i = input_channel_2;
        co_i = r_i - b_i;
        temp_i = b_i + (co_i >>> 1);
        cg_i = g_i - temp_i;
        y_i = temp_i + (cg_i >>> 1);
        output_channel_0 = y_i;
        if ($signed(bits) == 32'sd16) begin
            temp_i = ((co_i + 32'sd1) >>> 1) + half_i;
            output_channel_1 = (temp_i < 32'sd65535) ? temp_i : 32'sd65535;
            temp_i = ((cg_i + 32'sd1) >>> 1) + half_i;
            output_channel_2 = (temp_i < 32'sd65535) ? temp_i : 32'sd65535;
        end else begin
            output_channel_1 = co_i + (half_i <<< 1);
            output_channel_2 = cg_i + (half_i <<< 1);
        end
    end
endmodule
