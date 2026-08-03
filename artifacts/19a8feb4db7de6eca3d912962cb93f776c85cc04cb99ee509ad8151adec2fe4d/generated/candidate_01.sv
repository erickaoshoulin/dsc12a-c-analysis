module predictsize (
    input logic [4:0] req_size_0,
    input logic [4:0] req_size_1,
    input logic [4:0] req_size_2,
    output logic [4:0] return_value
);
    assign return_value = ((req_size_0 + req_size_1 + (2 * req_size_2) + 2) >> 2);
endmodule
