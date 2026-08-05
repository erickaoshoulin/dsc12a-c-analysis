module getbits_fifo_accounting_decode_transition(
    input  logic [6:0] nbits,
    input  logic [7:0] byte_0,
    input  logic [7:0] byte_1,
    input  logic [7:0] byte_2,
    input  logic [7:0] byte_3,
    input  logic [7:0] byte_4,
    input  logic [7:0] byte_5,
    input  logic [7:0] byte_6,
    input  logic [7:0] byte_7,
    input  logic [7:0] byte_8,
    input  logic signed [31:0] bit_count,
    input  logic [31:0] fullness,
    input  logic [31:0] read_ptr,
    input  logic [31:0] fifo_size,
    input  logic sign_extend,
    output logic signed [31:0] return_value,
    output logic signed [31:0] bit_count_out,
    output logic [31:0] fullness_out,
    output logic [31:0] read_ptr_out
);
    logic [79:0] window_i;
    logic [79:0] shifted_i;
    logic [79:0] extracted_i;
    logic [31:0] raw_i;
    logic [31:0] mask_i;
    logic [32:0] read_sum_i;
    logic sign_i;

    always_comb begin
        window_i = {byte_0, byte_1, byte_2, byte_3, byte_4, byte_5, byte_6, byte_7, byte_8, 8'b0};
        shifted_i = window_i << read_ptr[2:0];
        extracted_i = '0;
        bit_count_out = bit_count + {25'd0, nbits};
        fullness_out = fullness - {25'd0, nbits};
        read_sum_i = {1'b0, read_ptr} + {26'd0, nbits};
        if (read_sum_i >= {1'b0, fifo_size})
            read_ptr_out = read_sum_i[31:0] - fifo_size;
        else
            read_ptr_out = read_sum_i[31:0];
        raw_i = 32'd0;
        mask_i = 32'd0;
        return_value = 32'sd0;
        sign_i = shifted_i[79];
        if (nbits != 0) begin
            extracted_i = shifted_i >> (80 - nbits);
            raw_i = extracted_i[31:0];
            if (nbits >= 32) mask_i = 32'hffffffff;
            else mask_i = (32'h00000001 << nbits) - 1;
            raw_i = raw_i & mask_i;
            if (sign_extend && sign_i)
                return_value = $signed(raw_i | ~mask_i);
            else
                return_value = $signed(raw_i);
        end
    end
endmodule
