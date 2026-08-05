module addbits_encode_transition(
    input  logic [31:0] data,
    input  logic [5:0] nbits,
    input  logic [7:0] byte_0,
    input  logic [7:0] byte_1,
    input  logic [7:0] byte_2,
    input  logic [7:0] byte_3,
    input  logic [7:0] byte_4,
    input  logic signed [31:0] num_bits,
    input  logic [31:0] fullness,
    input  logic [31:0] write_ptr,
    input  logic [31:0] fifo_size,
    input  logic [31:0] max_fullness,
    output logic [7:0] byte_0_out,
    output logic [7:0] byte_1_out,
    output logic [7:0] byte_2_out,
    output logic [7:0] byte_3_out,
    output logic [7:0] byte_4_out,
    output logic signed [31:0] num_bits_out,
    output logic [31:0] fullness_out,
    output logic [31:0] write_ptr_out,
    output logic [31:0] max_fullness_out
);
    logic [39:0] window_i;
    logic [39:0] window_out_i;
    logic [32:0] write_sum_i;
    integer i;

    always_comb begin
        window_i = {byte_0, byte_1, byte_2, byte_3, byte_4};
        window_out_i = window_i;
        for (i = 0; i < 32; i = i + 1) begin
            if (i < int'(nbits))
                window_out_i[39 - int'(write_ptr[2:0]) - i] = data[int'(nbits) - 1 - i];
        end
        byte_0_out = window_out_i[39 -: 8];
        byte_1_out = window_out_i[31 -: 8];
        byte_2_out = window_out_i[23 -: 8];
        byte_3_out = window_out_i[15 -: 8];
        byte_4_out = window_out_i[7 -: 8];
        num_bits_out = num_bits + {{26{1'b0}}, nbits};
        fullness_out = fullness + {{26{1'b0}}, nbits};
        write_sum_i = {1'b0, write_ptr} + {{27{1'b0}}, nbits};
        if (write_sum_i >= {1'b0, fifo_size})
            write_ptr_out = write_sum_i[31:0] - fifo_size;
        else
            write_ptr_out = write_sum_i[31:0];
        if (fullness_out > max_fullness)
            max_fullness_out = fullness_out;
        else
            max_fullness_out = max_fullness;
    end
endmodule
