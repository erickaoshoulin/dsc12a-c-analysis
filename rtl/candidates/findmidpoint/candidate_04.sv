module findmidpoint_candidate_04(
  input logic [1:0]  cpnt,
  input logic [4:0]  cpnt_bit_depth,
  input logic [15:0] left_recon,
  input logic [4:0]  qlevel,
  output logic [16:0] return_value
);
  logic [16:0] range_value;
  logic [16:0] divisor_value;
  logic [16:0] left_value;
  assign range_value = 17'd1 << cpnt_bit_depth;
  assign divisor_value = 17'd1 << qlevel;
  assign left_value = {1'b0, left_recon};

  logic [16:0] off_by_one_divisor_value;
  assign off_by_one_divisor_value = (qlevel == 5'd16) ? 17'd65536 : (17'd1 << (qlevel + 5'd1));

  assign return_value = (range_value >> 1) + (left_value % off_by_one_divisor_value);
endmodule
