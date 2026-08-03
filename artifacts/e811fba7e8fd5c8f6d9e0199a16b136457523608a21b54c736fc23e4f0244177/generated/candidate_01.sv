module findresidualsize_candidate_01 (
    input logic signed [16:0] eq,
    output logic [4:0] return_value
);
    integer signed eq_i;
    always_comb begin
        eq_i = $signed(eq);
        return_value = 0;
        if (eq_i == 0) return_value = 0;
        else if ((eq_i >= -1) && (eq_i <= 0)) return_value = 1;
        else if ((eq_i >= -2) && (eq_i <= 1)) return_value = 2;
        else if ((eq_i >= -4) && (eq_i <= 3)) return_value = 3;
        else if ((eq_i >= -8) && (eq_i <= 7)) return_value = 4;
        else if ((eq_i >= -16) && (eq_i <= 15)) return_value = 5;
        else if ((eq_i >= -32) && (eq_i <= 31)) return_value = 6;
        else if ((eq_i >= -64) && (eq_i <= 63)) return_value = 7;
        else if ((eq_i >= -128) && (eq_i <= 127)) return_value = 8;
        else if ((eq_i >= -256) && (eq_i <= 255)) return_value = 9;
        else if ((eq_i >= -512) && (eq_i <= 511)) return_value = 10;
        else if ((eq_i >= -1024) && (eq_i <= 1023)) return_value = 11;
        else if ((eq_i >= -2048) && (eq_i <= 2047)) return_value = 12;
        else if ((eq_i >= -4096) && (eq_i <= 4095)) return_value = 13;
        else if ((eq_i >= -8192) && (eq_i <= 8191)) return_value = 14;
        else if ((eq_i >= -16384) && (eq_i <= 16383)) return_value = 15;
        else if ((eq_i >= -32768) && (eq_i <= 32767)) return_value = 16;
        else if ((eq_i >= -65536) && (eq_i <= 65535)) return_value = 17;
        else if ((eq_i >= -131702) && (eq_i <= 131701)) return_value = 18;
    end
endmodule
