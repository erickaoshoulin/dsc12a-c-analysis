module getbits_decode_transition(
    input  logic [4:0] size,
    input  logic [7:0] byte_0,
    input  logic [7:0] byte_1,
    input  logic [7:0] byte_2,
    input  logic [31:0] bit_count,
    input  logic sign_extend,
    output logic signed [31:0] return_value,
    output logic [31:0] bit_count_out
);
    logic [31:0] window_i;
    logic [31:0] shifted_i;
    logic [31:0] raw_i;
    logic [31:0] mask_i;

    always_comb begin
        window_i = {byte_0, byte_1, byte_2, 8'b0};
        shifted_i = window_i << bit_count[2:0];
        bit_count_out = bit_count + {27'd0, size};
        raw_i = 32'd0;
        mask_i = 32'd0;
        return_value = 32'sd0;
        if (size != 0) begin
            raw_i = shifted_i >> (32 - size);
            mask_i = (32'h00000001 << size) - 1;
            raw_i = raw_i & mask_i;
            if (sign_extend && raw_i[size - 1])
                return_value = $signed(raw_i | ~mask_i);
            else
                return_value = $signed(raw_i);
        end
    end
endmodule
