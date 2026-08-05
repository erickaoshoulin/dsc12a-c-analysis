module removebitsencoderbuffer_decode_transition(
    input logic signed [31:0] cfg_bits_per_pixel,
    input logic signed [31:0] cfg_chunk_size,
    input logic signed [31:0] cfg_vbr_enable,
    input logic signed [31:0] state_bitsclamped,
    input logic signed [31:0] state_bpgfracaccum,
    input logic signed [31:0] state_bufferfullness,
    input logic signed [31:0] state_chunkcount,
    input logic signed [31:0] state_chunkpixeltimes,
    input logic signed [31:0] state_isencoder,
    input logic signed [31:0] state_numbitschunk,
    input logic signed [31:0] state_slicewidth,
    output logic signed [31:0] state_bitsclamped_out,
    output logic signed [31:0] state_bpgfracaccum_out,
    output logic signed [31:0] state_bufferfullness_out,
    output logic signed [31:0] state_chunkcount_out,
    output logic signed [31:0] state_chunkpixeltimes_out,
    output logic signed [31:0] state_numbitschunk_out,
    output logic chunk_write_enable,
    output logic signed [31:0] chunk_write_index,
    output logic signed [31:0] chunk_write_value
);
    logic signed [31:0] removal_bits_i;
    logic signed [31:0] size_i;
    logic signed [31:0] adjustment_bits_i;

    always_comb begin
        state_bitsclamped_out = state_bitsclamped;
        state_bpgfracaccum_out = state_bpgfracaccum;
        state_bufferfullness_out = state_bufferfullness;
        state_chunkcount_out = state_chunkcount;
        state_chunkpixeltimes_out = state_chunkpixeltimes;
        state_numbitschunk_out = state_numbitschunk;
        chunk_write_enable = 1'b0;
        chunk_write_index = state_chunkcount;
        chunk_write_value = 32'sd0;
        removal_bits_i = 32'sd0;
        size_i = 32'sd0;
        adjustment_bits_i = 32'sd0;
        state_bpgfracaccum_out = state_bpgfracaccum + (cfg_bits_per_pixel & 32'sd15);
        removal_bits_i = (cfg_bits_per_pixel >>> 4) + (state_bpgfracaccum_out >>> 4);
        state_bufferfullness_out = state_bufferfullness - removal_bits_i;
        state_numbitschunk_out = state_numbitschunk + removal_bits_i;
        state_bpgfracaccum_out = state_bpgfracaccum_out & 32'sd15;
        state_chunkpixeltimes_out = state_chunkpixeltimes + 32'sd1;
        if (state_chunkpixeltimes_out >= state_slicewidth) begin
            if (cfg_vbr_enable != 0) begin
                size_i = (state_numbitschunk_out - state_bitsclamped + 32'sd7) / 32'sd8;
                adjustment_bits_i = size_i * 32'sd8 - (state_numbitschunk_out - state_bitsclamped);
                state_bufferfullness_out = state_bufferfullness_out - adjustment_bits_i;
                state_bitsclamped_out = 32'sd0;
                if (state_isencoder != 0) begin
                    chunk_write_enable = 1'b1;
                    chunk_write_value = size_i;
                end
            end else begin
                adjustment_bits_i = cfg_chunk_size * 32'sd8 - state_numbitschunk_out;
                state_bufferfullness_out = state_bufferfullness_out - adjustment_bits_i;
            end
            state_bpgfracaccum_out = 32'sd0;
            state_numbitschunk_out = 32'sd0;
            state_chunkcount_out = state_chunkcount + 32'sd1;
            state_chunkpixeltimes_out = 32'sd0;
        end
    end
endmodule
