module samptolinebuf_candidate_01 (
    input logic [15:0] x,
    input logic [1:0] cpnt,
    input logic [4:0] cpntBitDepth,
    input logic [3:0] linebuf_depth,
    output logic [15:0] return_value
);
    integer signed shift_amount_i;
    integer signed round_i;
    integer signed stored_sample_i;
    always_comb begin
        shift_amount_i = cpntBitDepth - linebuf_depth;
        if (shift_amount_i < 0) shift_amount_i = 0;
        round_i = shift_amount_i > 0 ? (1 <<< (shift_amount_i - 1)) : 0;
        stored_sample_i = (x + round_i) >>> shift_amount_i;
        if (stored_sample_i > ((1 <<< linebuf_depth) - 1)) stored_sample_i = (1 <<< linebuf_depth) - 1;
        return_value = stored_sample_i <<< shift_amount_i;
    end
endmodule
