module findmidpoint_candidate_02(
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

  logic signed [16:0] signed_left_value;
  logic signed [16:0] signed_divisor_value;
  logic signed [16:0] signed_midpoint_value;
  assign signed_left_value = $signed({left_recon[15], left_recon});
  assign signed_divisor_value = $signed(divisor_value);
  assign signed_midpoint_value = $signed(range_value >> 1) + (signed_left_value % signed_divisor_value);

  assign return_value = signed_midpoint_value;
endmodule
