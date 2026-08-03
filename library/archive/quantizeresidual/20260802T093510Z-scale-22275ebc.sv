module quantizeresidual_candidate_01 (
    input logic signed [16:0] e,
    input logic [4:0] qlevel,
    output logic signed [16:0] return_value
);
    integer signed e_i;
    integer signed round_i;
    always_comb begin
        e_i = $signed(e);
        round_i = 0;
        case (qlevel)
            0: round_i = 0;
            1: round_i = 0;
            2: round_i = 1;
            3: round_i = 3;
            4: round_i = 7;
            5: round_i = 15;
            6: round_i = 31;
            7: round_i = 63;
            8: round_i = 127;
            9: round_i = 255;
            10: round_i = 511;
            11: round_i = 1023;
            12: round_i = 2047;
            13: round_i = 4095;
            14: round_i = 8191;
            15: round_i = 16383;
            16: round_i = 32767;
            default: round_i = 0;
        endcase
        if (e_i > 0) return_value = (e_i + round_i) >>> qlevel;
        else return_value = -((round_i - e_i) >>> qlevel);
    end
endmodule
