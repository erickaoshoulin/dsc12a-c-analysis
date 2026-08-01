module cicd_mapqptoqlevel_stub(
  input logic [31:0] qp,
  input logic [1:0] cpnt,
  input logic [31:0] dsc_version_minor,
  input logic [31:0] native_420,
  input logic [4:0] cpntBitDepth,
  input logic [4:0] quantTableChroma,
  input logic [4:0] quantTableLuma,
  output logic [31:0] return_value);
  assign return_value = '0;
endmodule
