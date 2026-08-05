module putbits_encode_transition (
    input logic [31:0] value,
    input logic [5:0] size,
    input logic [7:0] byte_0,
    input logic [7:0] byte_1,
    input logic [7:0] byte_2,
    input logic [7:0] byte_3,
    input logic [7:0] byte_4,
    input logic [31:0] bit_count,
    output logic [7:0] byte_0_out,
    output logic [7:0] byte_1_out,
    output logic [7:0] byte_2_out,
    output logic [7:0] byte_3_out,
    output logic [7:0] byte_4_out,
    output logic [31:0] bit_count_out
);

  integer k;
  integer logical_bit;
  integer slot;
  integer source_bit;
  logic [7:0] work_0;
  logic [7:0] work_1;
  logic [7:0] work_2;
  logic [7:0] work_3;
  logic [7:0] work_4;

  always_comb begin
    work_0 = byte_0;
    work_1 = byte_1;
    work_2 = byte_2;
    work_3 = byte_3;
    work_4 = byte_4;
    logical_bit = 0;
    slot = 0;
    source_bit = 0;
    bit_count_out = bit_count + {{26{1'b0}}, size};
    for (k = 0; k < 32; k = k + 1) begin
      if (k < int'(size)) begin
        logical_bit = int'(bit_count[2:0]) + k;
        slot = logical_bit >> 3;
        source_bit = int'(size) - 1 - k;
        case (slot)
          0: begin
            if ((logical_bit & 7) == 0)
              work_0 = 8'h00;
            if (value[source_bit])
              work_0 = work_0 | (8'h80 >> (logical_bit & 7));
          end
          1: begin
            if ((logical_bit & 7) == 0)
              work_1 = 8'h00;
            if (value[source_bit])
              work_1 = work_1 | (8'h80 >> (logical_bit & 7));
          end
          2: begin
            if ((logical_bit & 7) == 0)
              work_2 = 8'h00;
            if (value[source_bit])
              work_2 = work_2 | (8'h80 >> (logical_bit & 7));
          end
          3: begin
            if ((logical_bit & 7) == 0)
              work_3 = 8'h00;
            if (value[source_bit])
              work_3 = work_3 | (8'h80 >> (logical_bit & 7));
          end
          4: begin
            if ((logical_bit & 7) == 0)
              work_4 = 8'h00;
            if (value[source_bit])
              work_4 = work_4 | (8'h80 >> (logical_bit & 7));
          end
          default: begin end
        endcase
      end
    end
    byte_0_out = work_0;
    byte_1_out = work_1;
    byte_2_out = work_2;
    byte_3_out = work_3;
    byte_4_out = work_4;
  end

endmodule
