module useichistory_decode_transition(
    input logic signed [31:0] state_hpos,
    input logic signed [31:0] state_pixels_in_group,
    input logic signed [31:0] state_ich_indices,
    input logic signed [31:0] state_ich_selected,
    input logic signed [31:0] state_num_components,
    input logic [31:0] ich_pixel_0_0,
    input logic [31:0] ich_pixel_0_1,
    input logic [31:0] ich_pixel_0_2,
    input logic [31:0] ich_pixel_0_3,
    input logic [31:0] ich_pixel_1_0,
    input logic [31:0] ich_pixel_1_1,
    input logic [31:0] ich_pixel_1_2,
    input logic [31:0] ich_pixel_1_3,
    input logic [31:0] ich_pixel_2_0,
    input logic [31:0] ich_pixel_2_1,
    input logic [31:0] ich_pixel_2_2,
    input logic [31:0] ich_pixel_2_3,
    input logic [31:0] ich_pixel_3_0,
    input logic [31:0] ich_pixel_3_1,
    input logic [31:0] ich_pixel_3_2,
    input logic [31:0] ich_pixel_3_3,
    input logic [31:0] ich_pixel_4_0,
    input logic [31:0] ich_pixel_4_1,
    input logic [31:0] ich_pixel_4_2,
    input logic [31:0] ich_pixel_4_3,
    input logic [31:0] ich_pixel_5_0,
    input logic [31:0] ich_pixel_5_1,
    input logic [31:0] ich_pixel_5_2,
    input logic [31:0] ich_pixel_5_3,
    output logic signed [31:0] write_index_0,
    output logic signed [31:0] write_index_1,
    output logic signed [31:0] write_index_2,
    output logic signed [31:0] write_index_3,
    output logic signed [31:0] write_index_4,
    output logic signed [31:0] write_index_5,
    output logic write_enable_0_0,
    output logic write_enable_0_1,
    output logic write_enable_0_2,
    output logic write_enable_0_3,
    output logic write_enable_1_0,
    output logic write_enable_1_1,
    output logic write_enable_1_2,
    output logic write_enable_1_3,
    output logic write_enable_2_0,
    output logic write_enable_2_1,
    output logic write_enable_2_2,
    output logic write_enable_2_3,
    output logic write_enable_3_0,
    output logic write_enable_3_1,
    output logic write_enable_3_2,
    output logic write_enable_3_3,
    output logic write_enable_4_0,
    output logic write_enable_4_1,
    output logic write_enable_4_2,
    output logic write_enable_4_3,
    output logic write_enable_5_0,
    output logic write_enable_5_1,
    output logic write_enable_5_2,
    output logic write_enable_5_3,
    output logic signed [31:0] write_value_0_0,
    output logic signed [31:0] write_value_0_1,
    output logic signed [31:0] write_value_0_2,
    output logic signed [31:0] write_value_0_3,
    output logic signed [31:0] write_value_1_0,
    output logic signed [31:0] write_value_1_1,
    output logic signed [31:0] write_value_1_2,
    output logic signed [31:0] write_value_1_3,
    output logic signed [31:0] write_value_2_0,
    output logic signed [31:0] write_value_2_1,
    output logic signed [31:0] write_value_2_2,
    output logic signed [31:0] write_value_2_3,
    output logic signed [31:0] write_value_3_0,
    output logic signed [31:0] write_value_3_1,
    output logic signed [31:0] write_value_3_2,
    output logic signed [31:0] write_value_3_3,
    output logic signed [31:0] write_value_4_0,
    output logic signed [31:0] write_value_4_1,
    output logic signed [31:0] write_value_4_2,
    output logic signed [31:0] write_value_4_3,
    output logic signed [31:0] write_value_5_0,
    output logic signed [31:0] write_value_5_1,
    output logic signed [31:0] write_value_5_2,
    output logic signed [31:0] write_value_5_3
);
    always_comb begin
        write_index_0 = state_hpos - state_pixels_in_group + 32'sd6;
        write_index_1 = state_hpos - state_pixels_in_group + 32'sd7;
        write_index_2 = state_hpos - state_pixels_in_group + 32'sd8;
        write_index_3 = state_hpos - state_pixels_in_group + 32'sd9;
        write_index_4 = state_hpos - state_pixels_in_group + 32'sd10;
        write_index_5 = state_hpos - state_pixels_in_group + 32'sd11;
        write_enable_0_0 = 1'b0;
        write_value_0_0 = 32'sd0;
        if ((state_ich_selected != 0) && (state_ich_indices > 32'sd0) && (state_num_components > 32'sd0)) begin
            write_enable_0_0 = 1'b1;
            write_value_0_0 = $signed(ich_pixel_0_0);
        end
        write_enable_0_1 = 1'b0;
        write_value_0_1 = 32'sd0;
        if ((state_ich_selected != 0) && (state_ich_indices > 32'sd0) && (state_num_components > 32'sd1)) begin
            write_enable_0_1 = 1'b1;
            write_value_0_1 = $signed(ich_pixel_0_1);
        end
        write_enable_0_2 = 1'b0;
        write_value_0_2 = 32'sd0;
        if ((state_ich_selected != 0) && (state_ich_indices > 32'sd0) && (state_num_components > 32'sd2)) begin
            write_enable_0_2 = 1'b1;
            write_value_0_2 = $signed(ich_pixel_0_2);
        end
        write_enable_0_3 = 1'b0;
        write_value_0_3 = 32'sd0;
        if ((state_ich_selected != 0) && (state_ich_indices > 32'sd0) && (state_num_components > 32'sd3)) begin
            write_enable_0_3 = 1'b1;
            write_value_0_3 = $signed(ich_pixel_0_3);
        end
        write_enable_1_0 = 1'b0;
        write_value_1_0 = 32'sd0;
        if ((state_ich_selected != 0) && (state_ich_indices > 32'sd1) && (state_num_components > 32'sd0)) begin
            write_enable_1_0 = 1'b1;
            write_value_1_0 = $signed(ich_pixel_1_0);
        end
        write_enable_1_1 = 1'b0;
        write_value_1_1 = 32'sd0;
        if ((state_ich_selected != 0) && (state_ich_indices > 32'sd1) && (state_num_components > 32'sd1)) begin
            write_enable_1_1 = 1'b1;
            write_value_1_1 = $signed(ich_pixel_1_1);
        end
        write_enable_1_2 = 1'b0;
        write_value_1_2 = 32'sd0;
        if ((state_ich_selected != 0) && (state_ich_indices > 32'sd1) && (state_num_components > 32'sd2)) begin
            write_enable_1_2 = 1'b1;
            write_value_1_2 = $signed(ich_pixel_1_2);
        end
        write_enable_1_3 = 1'b0;
        write_value_1_3 = 32'sd0;
        if ((state_ich_selected != 0) && (state_ich_indices > 32'sd1) && (state_num_components > 32'sd3)) begin
            write_enable_1_3 = 1'b1;
            write_value_1_3 = $signed(ich_pixel_1_3);
        end
        write_enable_2_0 = 1'b0;
        write_value_2_0 = 32'sd0;
        if ((state_ich_selected != 0) && (state_ich_indices > 32'sd2) && (state_num_components > 32'sd0)) begin
            write_enable_2_0 = 1'b1;
            write_value_2_0 = $signed(ich_pixel_2_0);
        end
        write_enable_2_1 = 1'b0;
        write_value_2_1 = 32'sd0;
        if ((state_ich_selected != 0) && (state_ich_indices > 32'sd2) && (state_num_components > 32'sd1)) begin
            write_enable_2_1 = 1'b1;
            write_value_2_1 = $signed(ich_pixel_2_1);
        end
        write_enable_2_2 = 1'b0;
        write_value_2_2 = 32'sd0;
        if ((state_ich_selected != 0) && (state_ich_indices > 32'sd2) && (state_num_components > 32'sd2)) begin
            write_enable_2_2 = 1'b1;
            write_value_2_2 = $signed(ich_pixel_2_2);
        end
        write_enable_2_3 = 1'b0;
        write_value_2_3 = 32'sd0;
        if ((state_ich_selected != 0) && (state_ich_indices > 32'sd2) && (state_num_components > 32'sd3)) begin
            write_enable_2_3 = 1'b1;
            write_value_2_3 = $signed(ich_pixel_2_3);
        end
        write_enable_3_0 = 1'b0;
        write_value_3_0 = 32'sd0;
        if ((state_ich_selected != 0) && (state_ich_indices > 32'sd3) && (state_num_components > 32'sd0)) begin
            write_enable_3_0 = 1'b1;
            write_value_3_0 = $signed(ich_pixel_3_0);
        end
        write_enable_3_1 = 1'b0;
        write_value_3_1 = 32'sd0;
        if ((state_ich_selected != 0) && (state_ich_indices > 32'sd3) && (state_num_components > 32'sd1)) begin
            write_enable_3_1 = 1'b1;
            write_value_3_1 = $signed(ich_pixel_3_1);
        end
        write_enable_3_2 = 1'b0;
        write_value_3_2 = 32'sd0;
        if ((state_ich_selected != 0) && (state_ich_indices > 32'sd3) && (state_num_components > 32'sd2)) begin
            write_enable_3_2 = 1'b1;
            write_value_3_2 = $signed(ich_pixel_3_2);
        end
        write_enable_3_3 = 1'b0;
        write_value_3_3 = 32'sd0;
        if ((state_ich_selected != 0) && (state_ich_indices > 32'sd3) && (state_num_components > 32'sd3)) begin
            write_enable_3_3 = 1'b1;
            write_value_3_3 = $signed(ich_pixel_3_3);
        end
        write_enable_4_0 = 1'b0;
        write_value_4_0 = 32'sd0;
        if ((state_ich_selected != 0) && (state_ich_indices > 32'sd4) && (state_num_components > 32'sd0)) begin
            write_enable_4_0 = 1'b1;
            write_value_4_0 = $signed(ich_pixel_4_0);
        end
        write_enable_4_1 = 1'b0;
        write_value_4_1 = 32'sd0;
        if ((state_ich_selected != 0) && (state_ich_indices > 32'sd4) && (state_num_components > 32'sd1)) begin
            write_enable_4_1 = 1'b1;
            write_value_4_1 = $signed(ich_pixel_4_1);
        end
        write_enable_4_2 = 1'b0;
        write_value_4_2 = 32'sd0;
        if ((state_ich_selected != 0) && (state_ich_indices > 32'sd4) && (state_num_components > 32'sd2)) begin
            write_enable_4_2 = 1'b1;
            write_value_4_2 = $signed(ich_pixel_4_2);
        end
        write_enable_4_3 = 1'b0;
        write_value_4_3 = 32'sd0;
        if ((state_ich_selected != 0) && (state_ich_indices > 32'sd4) && (state_num_components > 32'sd3)) begin
            write_enable_4_3 = 1'b1;
            write_value_4_3 = $signed(ich_pixel_4_3);
        end
        write_enable_5_0 = 1'b0;
        write_value_5_0 = 32'sd0;
        if ((state_ich_selected != 0) && (state_ich_indices > 32'sd5) && (state_num_components > 32'sd0)) begin
            write_enable_5_0 = 1'b1;
            write_value_5_0 = $signed(ich_pixel_5_0);
        end
        write_enable_5_1 = 1'b0;
        write_value_5_1 = 32'sd0;
        if ((state_ich_selected != 0) && (state_ich_indices > 32'sd5) && (state_num_components > 32'sd1)) begin
            write_enable_5_1 = 1'b1;
            write_value_5_1 = $signed(ich_pixel_5_1);
        end
        write_enable_5_2 = 1'b0;
        write_value_5_2 = 32'sd0;
        if ((state_ich_selected != 0) && (state_ich_indices > 32'sd5) && (state_num_components > 32'sd2)) begin
            write_enable_5_2 = 1'b1;
            write_value_5_2 = $signed(ich_pixel_5_2);
        end
        write_enable_5_3 = 1'b0;
        write_value_5_3 = 32'sd0;
        if ((state_ich_selected != 0) && (state_ich_indices > 32'sd5) && (state_num_components > 32'sd3)) begin
            write_enable_5_3 = 1'b1;
            write_value_5_3 = $signed(ich_pixel_5_3);
        end
    end
endmodule
