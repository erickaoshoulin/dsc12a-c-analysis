module ycocg2rgb_pixel_transition(
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
        y_i = input_channel_0;
        if ($signed(bits) == 32'sd16) begin
            co_i = (input_channel_1 - half_i) <<< 1;
            cg_i = (input_channel_2 - half_i) <<< 1;
        end else begin
            co_i = input_channel_1 - (half_i <<< 1);
            cg_i = input_channel_2 - (half_i <<< 1);
        end
        temp_i = y_i - (cg_i >>> 1);
        g_i = cg_i + temp_i;
        b_i = temp_i - (co_i >>> 1);
        r_i = co_i + b_i;
        max_i = (32'sd1 <<< $signed(bits)) - 32'sd1;
        output_channel_0 = (r_i < 0) ? 0 : ((r_i > max_i) ? max_i : r_i);
        output_channel_1 = (g_i < 0) ? 0 : ((g_i > max_i) ? max_i : g_i);
        output_channel_2 = (b_i < 0) ? 0 : ((b_i > max_i) ? max_i : b_i);
    end
endmodule
