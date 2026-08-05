module calcfullnessoffset_decode_transition(
    input logic signed [31:0] vpos,
    input logic signed [31:0] group_count,
    input logic signed [31:0] cfg_bits_per_pixel,
    input logic signed [31:0] cfg_final_offset,
    input logic signed [31:0] cfg_first_line_bpg_ofs,
    input logic signed [31:0] cfg_initial_scale_value,
    input logic signed [31:0] cfg_initial_xmit_delay,
    input logic signed [31:0] cfg_nfl_bpg_offset,
    input logic signed [31:0] cfg_nsl_bpg_offset,
    input logic signed [31:0] cfg_scale_decrement_interval,
    input logic signed [31:0] cfg_scale_increment_interval,
    input logic signed [31:0] cfg_second_line_bpg_ofs,
    input logic signed [31:0] cfg_second_line_ofs_adj,
    input logic signed [31:0] cfg_slice_bpg_offset,
    input logic signed [31:0] state_currentscale,
    input logic signed [31:0] state_pixelcount,
    input logic signed [31:0] state_pixelsingroup,
    input logic signed [31:0] state_prevpixelcount,
    input logic signed [31:0] state_rcoffsetclampenable,
    input logic signed [31:0] state_rcxformoffset,
    input logic signed [31:0] state_scaleadjustcounter,
    input logic signed [31:0] state_scaleincrementstart,
    input logic signed [31:0] state_secondoffsetapplied,
    input logic signed [31:0] state_throttlefrac,
    output logic signed [31:0] scale_out,
    output logic signed [31:0] bpg_offset_out,
    output logic signed [31:0] state_currentscale_out,
    output logic signed [31:0] state_prevpixelcount_out,
    output logic signed [31:0] state_rcoffsetclampenable_out,
    output logic signed [31:0] state_rcxformoffset_out,
    output logic signed [31:0] state_scaleadjustcounter_out,
    output logic signed [31:0] state_scaleincrementstart_out,
    output logic signed [31:0] state_secondoffsetapplied_out,
    output logic signed [31:0] state_throttlefrac_out
);
    logic signed [31:0] current_bpg_target_i;
    logic signed [31:0] increment_i;
    logic signed [31:0] num_pixels_i;

    always_comb begin
        state_currentscale_out = state_currentscale;
        state_prevpixelcount_out = state_prevpixelcount;
        state_rcoffsetclampenable_out = state_rcoffsetclampenable;
        state_rcxformoffset_out = state_rcxformoffset;
        state_scaleadjustcounter_out = state_scaleadjustcounter;
        state_scaleincrementstart_out = state_scaleincrementstart;
        state_secondoffsetapplied_out = state_secondoffsetapplied;
        state_throttlefrac_out = state_throttlefrac;
        current_bpg_target_i = 32'sd0;
        increment_i = 32'sd0;
        num_pixels_i = 32'sd0;
        if (group_count == 0) begin
            state_currentscale_out = cfg_initial_scale_value;
            state_scaleadjustcounter_out = 32'sd1;
        end else if ((vpos == 0) && (state_currentscale > 32'sd8)) begin
            state_scaleadjustcounter_out = state_scaleadjustcounter + 1;
            if (state_scaleadjustcounter_out >= cfg_scale_decrement_interval) begin
                state_scaleadjustcounter_out = 0;
                state_currentscale_out = state_currentscale - 1;
            end
        end else if (state_scaleincrementstart != 0) begin
            state_scaleadjustcounter_out = state_scaleadjustcounter + 1;
            if (state_scaleadjustcounter_out >= cfg_scale_increment_interval) begin
                state_scaleadjustcounter_out = 0;
                state_currentscale_out = state_currentscale + 1;
            end
        end
        if (vpos == 0) begin
            current_bpg_target_i = cfg_first_line_bpg_ofs;
            increment_i = -(cfg_first_line_bpg_ofs <<< 11);
        end else begin
            current_bpg_target_i = -(cfg_nfl_bpg_offset >>> 11);
            increment_i = cfg_nfl_bpg_offset;
        end
        if (vpos == 1) begin
            current_bpg_target_i = current_bpg_target_i + cfg_second_line_bpg_ofs;
            increment_i = increment_i - (cfg_second_line_bpg_ofs <<< 11);
            if (state_secondoffsetapplied == 0) begin
                state_secondoffsetapplied_out = 1;
                state_rcxformoffset_out = state_rcxformoffset - cfg_second_line_ofs_adj;
            end
        end else begin
            current_bpg_target_i = current_bpg_target_i - (cfg_nsl_bpg_offset >>> 11);
            increment_i = increment_i + cfg_nsl_bpg_offset;
        end
        if (state_pixelcount < cfg_initial_xmit_delay) begin
            if (state_pixelcount == 0)
                num_pixels_i = state_pixelsingroup;
            else
                num_pixels_i = state_pixelcount - state_prevpixelcount;
            if ((cfg_initial_xmit_delay - state_pixelcount) < num_pixels_i)
                num_pixels_i = cfg_initial_xmit_delay - state_pixelcount;
            increment_i = increment_i - ((cfg_bits_per_pixel * num_pixels_i) <<< 7);
        end else begin
            if ((cfg_scale_increment_interval != 0) && (state_scaleincrementstart == 0) && (vpos > 0) && (state_rcxformoffset > 0)) begin
                state_currentscale_out = 9;
                state_scaleadjustcounter_out = 0;
                state_scaleincrementstart_out = 1;
            end
        end
        state_prevpixelcount_out = state_pixelcount;
        current_bpg_target_i = current_bpg_target_i - (cfg_slice_bpg_offset >>> 11);
        increment_i = increment_i + cfg_slice_bpg_offset;
        state_throttlefrac_out = state_throttlefrac + increment_i;
        state_rcxformoffset_out = state_rcxformoffset_out + (state_throttlefrac_out >>> 11);
        state_throttlefrac_out = state_throttlefrac_out & 32'h000007ff;
        if (state_rcxformoffset_out < cfg_final_offset)
            state_rcoffsetclampenable_out = 1;
        if ((state_rcoffsetclampenable_out != 0) && (state_rcxformoffset_out > cfg_final_offset))
            state_rcxformoffset_out = cfg_final_offset;
        scale_out = state_currentscale_out;
        bpg_offset_out = current_bpg_target_i;
    end
endmodule
