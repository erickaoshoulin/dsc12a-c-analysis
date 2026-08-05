module updatemidpoint_encode_transition(
    input logic signed [31:0] hpos,
    input logic signed [31:0] pixels_per_group,
    input logic signed [31:0] units_per_group,
    input logic signed [31:0] slice_width,
    input logic signed [31:0] unit_selected_0,
    input logic signed [31:0] unit_selected_1,
    input logic signed [31:0] unit_selected_2,
    input logic signed [31:0] unit_selected_3,
    input logic signed [31:0] unit_component_0,
    input logic signed [31:0] unit_component_1,
    input logic signed [31:0] unit_component_2,
    input logic signed [31:0] unit_component_3,
    input logic signed [31:0] unit_start_0,
    input logic signed [31:0] unit_start_1,
    input logic signed [31:0] unit_start_2,
    input logic signed [31:0] unit_start_3,
    input logic signed [31:0] reconstruction_0_0,
    input logic signed [31:0] reconstruction_0_1,
    input logic signed [31:0] reconstruction_0_2,
    input logic signed [31:0] reconstruction_1_0,
    input logic signed [31:0] reconstruction_1_1,
    input logic signed [31:0] reconstruction_1_2,
    input logic signed [31:0] reconstruction_2_0,
    input logic signed [31:0] reconstruction_2_1,
    input logic signed [31:0] reconstruction_2_2,
    input logic signed [31:0] reconstruction_3_0,
    input logic signed [31:0] reconstruction_3_1,
    input logic signed [31:0] reconstruction_3_2,
    output logic write_enable_0,
    output logic [1:0] write_component_0,
    output logic signed [31:0] write_address_0,
    output logic signed [31:0] write_value_0,
    output logic write_enable_1,
    output logic [1:0] write_component_1,
    output logic signed [31:0] write_address_1,
    output logic signed [31:0] write_value_1,
    output logic write_enable_2,
    output logic [1:0] write_component_2,
    output logic signed [31:0] write_address_2,
    output logic signed [31:0] write_value_2,
    output logic write_enable_3,
    output logic [1:0] write_component_3,
    output logic signed [31:0] write_address_3,
    output logic signed [31:0] write_value_3,
    output logic write_enable_4,
    output logic [1:0] write_component_4,
    output logic signed [31:0] write_address_4,
    output logic signed [31:0] write_value_4,
    output logic write_enable_5,
    output logic [1:0] write_component_5,
    output logic signed [31:0] write_address_5,
    output logic signed [31:0] write_value_5,
    output logic write_enable_6,
    output logic [1:0] write_component_6,
    output logic signed [31:0] write_address_6,
    output logic signed [31:0] write_value_6,
    output logic write_enable_7,
    output logic [1:0] write_component_7,
    output logic signed [31:0] write_address_7,
    output logic signed [31:0] write_value_7,
    output logic write_enable_8,
    output logic [1:0] write_component_8,
    output logic signed [31:0] write_address_8,
    output logic signed [31:0] write_value_8,
    output logic write_enable_9,
    output logic [1:0] write_component_9,
    output logic signed [31:0] write_address_9,
    output logic signed [31:0] write_value_9,
    output logic write_enable_10,
    output logic [1:0] write_component_10,
    output logic signed [31:0] write_address_10,
    output logic signed [31:0] write_value_10,
    output logic write_enable_11,
    output logic [1:0] write_component_11,
    output logic signed [31:0] write_address_11,
    output logic signed [31:0] write_value_11
);

    logic signed [31:0] start_hpos;

    always_comb begin
        start_hpos = hpos - (hpos % pixels_per_group);
        write_enable_0 = (units_per_group > 32'sd0) && (unit_selected_0 != 0) && 1'b1;
        write_component_0 = unit_component_0[1:0];
        write_address_0 = start_hpos + 32'sd5 + unit_start_0 + 32'sd0;
        write_value_0 = reconstruction_0_0;
        write_enable_1 = (units_per_group > 32'sd1) && (unit_selected_1 != 0) && 1'b1;
        write_component_1 = unit_component_1[1:0];
        write_address_1 = start_hpos + 32'sd5 + unit_start_1 + 32'sd0;
        write_value_1 = reconstruction_1_0;
        write_enable_2 = (units_per_group > 32'sd2) && (unit_selected_2 != 0) && 1'b1;
        write_component_2 = unit_component_2[1:0];
        write_address_2 = start_hpos + 32'sd5 + unit_start_2 + 32'sd0;
        write_value_2 = reconstruction_2_0;
        write_enable_3 = (units_per_group > 32'sd3) && (unit_selected_3 != 0) && 1'b1;
        write_component_3 = unit_component_3[1:0];
        write_address_3 = start_hpos + 32'sd5 + unit_start_3 + 32'sd0;
        write_value_3 = reconstruction_3_0;
        write_enable_4 = (units_per_group > 32'sd0) && (unit_selected_0 != 0) && ((hpos + 32'sd0) < slice_width);
        write_component_4 = unit_component_0[1:0];
        write_address_4 = start_hpos + 32'sd5 + unit_start_0 + 32'sd1;
        write_value_4 = reconstruction_0_1;
        write_enable_5 = (units_per_group > 32'sd1) && (unit_selected_1 != 0) && ((hpos + 32'sd0) < slice_width);
        write_component_5 = unit_component_1[1:0];
        write_address_5 = start_hpos + 32'sd5 + unit_start_1 + 32'sd1;
        write_value_5 = reconstruction_1_1;
        write_enable_6 = (units_per_group > 32'sd2) && (unit_selected_2 != 0) && ((hpos + 32'sd0) < slice_width);
        write_component_6 = unit_component_2[1:0];
        write_address_6 = start_hpos + 32'sd5 + unit_start_2 + 32'sd1;
        write_value_6 = reconstruction_2_1;
        write_enable_7 = (units_per_group > 32'sd3) && (unit_selected_3 != 0) && ((hpos + 32'sd0) < slice_width);
        write_component_7 = unit_component_3[1:0];
        write_address_7 = start_hpos + 32'sd5 + unit_start_3 + 32'sd1;
        write_value_7 = reconstruction_3_1;
        write_enable_8 = (units_per_group > 32'sd0) && (unit_selected_0 != 0) && ((hpos + 32'sd1) < slice_width);
        write_component_8 = unit_component_0[1:0];
        write_address_8 = start_hpos + 32'sd5 + unit_start_0 + 32'sd2;
        write_value_8 = reconstruction_0_2;
        write_enable_9 = (units_per_group > 32'sd1) && (unit_selected_1 != 0) && ((hpos + 32'sd1) < slice_width);
        write_component_9 = unit_component_1[1:0];
        write_address_9 = start_hpos + 32'sd5 + unit_start_1 + 32'sd2;
        write_value_9 = reconstruction_1_2;
        write_enable_10 = (units_per_group > 32'sd2) && (unit_selected_2 != 0) && ((hpos + 32'sd1) < slice_width);
        write_component_10 = unit_component_2[1:0];
        write_address_10 = start_hpos + 32'sd5 + unit_start_2 + 32'sd2;
        write_value_10 = reconstruction_2_2;
        write_enable_11 = (units_per_group > 32'sd3) && (unit_selected_3 != 0) && ((hpos + 32'sd1) < slice_width);
        write_component_11 = unit_component_3[1:0];
        write_address_11 = start_hpos + 32'sd5 + unit_start_3 + 32'sd2;
        write_value_11 = reconstruction_3_2;
    end
endmodule
