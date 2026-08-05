module blockpredsearch_decode_transition(
    input logic signed [31:0] cpnt,
    input logic signed [31:0] hpos,
    input logic signed [31:0] cfg_bits_per_component,
    input logic signed [31:0] cfg_block_pred_enable,
    input logic signed [31:0] cfg_native_420,
    input logic signed [31:0] state_numcomponents,
    input logic signed [31:0] state_bpcount,
    input logic signed [31:0] state_lastedgecount,
    input logic signed [31:0] state_edgedetected,
    input logic signed [31:0] state_cpnt_bit_depth_0,
    input logic signed [31:0] state_cpnt_bit_depth_1,
    input logic signed [31:0] state_cpnt_bit_depth_2,
    input logic signed [31:0] state_cpnt_bit_depth_3,
    input logic signed [31:0] state_pred_err_0_0,
    input logic signed [31:0] state_pred_err_0_1,
    input logic signed [31:0] state_pred_err_0_2,
    input logic signed [31:0] state_pred_err_0_3,
    input logic signed [31:0] state_pred_err_0_4,
    input logic signed [31:0] state_pred_err_0_5,
    input logic signed [31:0] state_pred_err_0_6,
    input logic signed [31:0] state_pred_err_0_7,
    input logic signed [31:0] state_pred_err_0_8,
    input logic signed [31:0] state_pred_err_0_9,
    input logic signed [31:0] state_pred_err_0_10,
    input logic signed [31:0] state_pred_err_0_11,
    input logic signed [31:0] state_pred_err_0_12,
    input logic signed [31:0] state_pred_err_1_0,
    input logic signed [31:0] state_pred_err_1_1,
    input logic signed [31:0] state_pred_err_1_2,
    input logic signed [31:0] state_pred_err_1_3,
    input logic signed [31:0] state_pred_err_1_4,
    input logic signed [31:0] state_pred_err_1_5,
    input logic signed [31:0] state_pred_err_1_6,
    input logic signed [31:0] state_pred_err_1_7,
    input logic signed [31:0] state_pred_err_1_8,
    input logic signed [31:0] state_pred_err_1_9,
    input logic signed [31:0] state_pred_err_1_10,
    input logic signed [31:0] state_pred_err_1_11,
    input logic signed [31:0] state_pred_err_1_12,
    input logic signed [31:0] state_pred_err_2_0,
    input logic signed [31:0] state_pred_err_2_1,
    input logic signed [31:0] state_pred_err_2_2,
    input logic signed [31:0] state_pred_err_2_3,
    input logic signed [31:0] state_pred_err_2_4,
    input logic signed [31:0] state_pred_err_2_5,
    input logic signed [31:0] state_pred_err_2_6,
    input logic signed [31:0] state_pred_err_2_7,
    input logic signed [31:0] state_pred_err_2_8,
    input logic signed [31:0] state_pred_err_2_9,
    input logic signed [31:0] state_pred_err_2_10,
    input logic signed [31:0] state_pred_err_2_11,
    input logic signed [31:0] state_pred_err_2_12,
    input logic signed [31:0] state_pred_err_3_0,
    input logic signed [31:0] state_pred_err_3_1,
    input logic signed [31:0] state_pred_err_3_2,
    input logic signed [31:0] state_pred_err_3_3,
    input logic signed [31:0] state_pred_err_3_4,
    input logic signed [31:0] state_pred_err_3_5,
    input logic signed [31:0] state_pred_err_3_6,
    input logic signed [31:0] state_pred_err_3_7,
    input logic signed [31:0] state_pred_err_3_8,
    input logic signed [31:0] state_pred_err_3_9,
    input logic signed [31:0] state_pred_err_3_10,
    input logic signed [31:0] state_pred_err_3_11,
    input logic signed [31:0] state_pred_err_3_12,
    input logic signed [31:0] state_last_err_0_0_0,
    input logic signed [31:0] state_last_err_0_0_1,
    input logic signed [31:0] state_last_err_0_0_2,
    input logic signed [31:0] state_last_err_0_0_3,
    input logic signed [31:0] state_last_err_0_0_4,
    input logic signed [31:0] state_last_err_0_0_5,
    input logic signed [31:0] state_last_err_0_0_6,
    input logic signed [31:0] state_last_err_0_0_7,
    input logic signed [31:0] state_last_err_0_0_8,
    input logic signed [31:0] state_last_err_0_0_9,
    input logic signed [31:0] state_last_err_0_0_10,
    input logic signed [31:0] state_last_err_0_0_11,
    input logic signed [31:0] state_last_err_0_0_12,
    input logic signed [31:0] state_last_err_0_1_0,
    input logic signed [31:0] state_last_err_0_1_1,
    input logic signed [31:0] state_last_err_0_1_2,
    input logic signed [31:0] state_last_err_0_1_3,
    input logic signed [31:0] state_last_err_0_1_4,
    input logic signed [31:0] state_last_err_0_1_5,
    input logic signed [31:0] state_last_err_0_1_6,
    input logic signed [31:0] state_last_err_0_1_7,
    input logic signed [31:0] state_last_err_0_1_8,
    input logic signed [31:0] state_last_err_0_1_9,
    input logic signed [31:0] state_last_err_0_1_10,
    input logic signed [31:0] state_last_err_0_1_11,
    input logic signed [31:0] state_last_err_0_1_12,
    input logic signed [31:0] state_last_err_0_2_0,
    input logic signed [31:0] state_last_err_0_2_1,
    input logic signed [31:0] state_last_err_0_2_2,
    input logic signed [31:0] state_last_err_0_2_3,
    input logic signed [31:0] state_last_err_0_2_4,
    input logic signed [31:0] state_last_err_0_2_5,
    input logic signed [31:0] state_last_err_0_2_6,
    input logic signed [31:0] state_last_err_0_2_7,
    input logic signed [31:0] state_last_err_0_2_8,
    input logic signed [31:0] state_last_err_0_2_9,
    input logic signed [31:0] state_last_err_0_2_10,
    input logic signed [31:0] state_last_err_0_2_11,
    input logic signed [31:0] state_last_err_0_2_12,
    input logic signed [31:0] state_last_err_1_0_0,
    input logic signed [31:0] state_last_err_1_0_1,
    input logic signed [31:0] state_last_err_1_0_2,
    input logic signed [31:0] state_last_err_1_0_3,
    input logic signed [31:0] state_last_err_1_0_4,
    input logic signed [31:0] state_last_err_1_0_5,
    input logic signed [31:0] state_last_err_1_0_6,
    input logic signed [31:0] state_last_err_1_0_7,
    input logic signed [31:0] state_last_err_1_0_8,
    input logic signed [31:0] state_last_err_1_0_9,
    input logic signed [31:0] state_last_err_1_0_10,
    input logic signed [31:0] state_last_err_1_0_11,
    input logic signed [31:0] state_last_err_1_0_12,
    input logic signed [31:0] state_last_err_1_1_0,
    input logic signed [31:0] state_last_err_1_1_1,
    input logic signed [31:0] state_last_err_1_1_2,
    input logic signed [31:0] state_last_err_1_1_3,
    input logic signed [31:0] state_last_err_1_1_4,
    input logic signed [31:0] state_last_err_1_1_5,
    input logic signed [31:0] state_last_err_1_1_6,
    input logic signed [31:0] state_last_err_1_1_7,
    input logic signed [31:0] state_last_err_1_1_8,
    input logic signed [31:0] state_last_err_1_1_9,
    input logic signed [31:0] state_last_err_1_1_10,
    input logic signed [31:0] state_last_err_1_1_11,
    input logic signed [31:0] state_last_err_1_1_12,
    input logic signed [31:0] state_last_err_1_2_0,
    input logic signed [31:0] state_last_err_1_2_1,
    input logic signed [31:0] state_last_err_1_2_2,
    input logic signed [31:0] state_last_err_1_2_3,
    input logic signed [31:0] state_last_err_1_2_4,
    input logic signed [31:0] state_last_err_1_2_5,
    input logic signed [31:0] state_last_err_1_2_6,
    input logic signed [31:0] state_last_err_1_2_7,
    input logic signed [31:0] state_last_err_1_2_8,
    input logic signed [31:0] state_last_err_1_2_9,
    input logic signed [31:0] state_last_err_1_2_10,
    input logic signed [31:0] state_last_err_1_2_11,
    input logic signed [31:0] state_last_err_1_2_12,
    input logic signed [31:0] state_last_err_2_0_0,
    input logic signed [31:0] state_last_err_2_0_1,
    input logic signed [31:0] state_last_err_2_0_2,
    input logic signed [31:0] state_last_err_2_0_3,
    input logic signed [31:0] state_last_err_2_0_4,
    input logic signed [31:0] state_last_err_2_0_5,
    input logic signed [31:0] state_last_err_2_0_6,
    input logic signed [31:0] state_last_err_2_0_7,
    input logic signed [31:0] state_last_err_2_0_8,
    input logic signed [31:0] state_last_err_2_0_9,
    input logic signed [31:0] state_last_err_2_0_10,
    input logic signed [31:0] state_last_err_2_0_11,
    input logic signed [31:0] state_last_err_2_0_12,
    input logic signed [31:0] state_last_err_2_1_0,
    input logic signed [31:0] state_last_err_2_1_1,
    input logic signed [31:0] state_last_err_2_1_2,
    input logic signed [31:0] state_last_err_2_1_3,
    input logic signed [31:0] state_last_err_2_1_4,
    input logic signed [31:0] state_last_err_2_1_5,
    input logic signed [31:0] state_last_err_2_1_6,
    input logic signed [31:0] state_last_err_2_1_7,
    input logic signed [31:0] state_last_err_2_1_8,
    input logic signed [31:0] state_last_err_2_1_9,
    input logic signed [31:0] state_last_err_2_1_10,
    input logic signed [31:0] state_last_err_2_1_11,
    input logic signed [31:0] state_last_err_2_1_12,
    input logic signed [31:0] state_last_err_2_2_0,
    input logic signed [31:0] state_last_err_2_2_1,
    input logic signed [31:0] state_last_err_2_2_2,
    input logic signed [31:0] state_last_err_2_2_3,
    input logic signed [31:0] state_last_err_2_2_4,
    input logic signed [31:0] state_last_err_2_2_5,
    input logic signed [31:0] state_last_err_2_2_6,
    input logic signed [31:0] state_last_err_2_2_7,
    input logic signed [31:0] state_last_err_2_2_8,
    input logic signed [31:0] state_last_err_2_2_9,
    input logic signed [31:0] state_last_err_2_2_10,
    input logic signed [31:0] state_last_err_2_2_11,
    input logic signed [31:0] state_last_err_2_2_12,
    input logic signed [31:0] state_last_err_3_0_0,
    input logic signed [31:0] state_last_err_3_0_1,
    input logic signed [31:0] state_last_err_3_0_2,
    input logic signed [31:0] state_last_err_3_0_3,
    input logic signed [31:0] state_last_err_3_0_4,
    input logic signed [31:0] state_last_err_3_0_5,
    input logic signed [31:0] state_last_err_3_0_6,
    input logic signed [31:0] state_last_err_3_0_7,
    input logic signed [31:0] state_last_err_3_0_8,
    input logic signed [31:0] state_last_err_3_0_9,
    input logic signed [31:0] state_last_err_3_0_10,
    input logic signed [31:0] state_last_err_3_0_11,
    input logic signed [31:0] state_last_err_3_0_12,
    input logic signed [31:0] state_last_err_3_1_0,
    input logic signed [31:0] state_last_err_3_1_1,
    input logic signed [31:0] state_last_err_3_1_2,
    input logic signed [31:0] state_last_err_3_1_3,
    input logic signed [31:0] state_last_err_3_1_4,
    input logic signed [31:0] state_last_err_3_1_5,
    input logic signed [31:0] state_last_err_3_1_6,
    input logic signed [31:0] state_last_err_3_1_7,
    input logic signed [31:0] state_last_err_3_1_8,
    input logic signed [31:0] state_last_err_3_1_9,
    input logic signed [31:0] state_last_err_3_1_10,
    input logic signed [31:0] state_last_err_3_1_11,
    input logic signed [31:0] state_last_err_3_1_12,
    input logic signed [31:0] state_last_err_3_2_0,
    input logic signed [31:0] state_last_err_3_2_1,
    input logic signed [31:0] state_last_err_3_2_2,
    input logic signed [31:0] state_last_err_3_2_3,
    input logic signed [31:0] state_last_err_3_2_4,
    input logic signed [31:0] state_last_err_3_2_5,
    input logic signed [31:0] state_last_err_3_2_6,
    input logic signed [31:0] state_last_err_3_2_7,
    input logic signed [31:0] state_last_err_3_2_8,
    input logic signed [31:0] state_last_err_3_2_9,
    input logic signed [31:0] state_last_err_3_2_10,
    input logic signed [31:0] state_last_err_3_2_11,
    input logic signed [31:0] state_last_err_3_2_12,
    input logic signed [31:0] line_sample_m8,
    input logic signed [31:0] line_sample_m7,
    input logic signed [31:0] line_sample_m6,
    input logic signed [31:0] line_sample_m5,
    input logic signed [31:0] line_sample_m4,
    input logic signed [31:0] line_sample_m3,
    input logic signed [31:0] line_sample_m2,
    input logic signed [31:0] line_sample_m1,
    input logic signed [31:0] line_sample_p0,
    input logic signed [31:0] line_sample_p1,
    input logic signed [31:0] line_sample_p2,
    input logic signed [31:0] line_sample_p3,
    input logic signed [31:0] line_sample_p4,
    input logic signed [31:0] line_sample_p5,
    output logic domain_valid,
    output logic signed [31:0] state_bpcount_out,
    output logic signed [31:0] state_lastedgecount_out,
    output logic signed [31:0] state_edgedetected_out,
    output logic signed [31:0] state_pred_err_0_0_out,
    output logic signed [31:0] state_pred_err_0_1_out,
    output logic signed [31:0] state_pred_err_0_2_out,
    output logic signed [31:0] state_pred_err_0_3_out,
    output logic signed [31:0] state_pred_err_0_4_out,
    output logic signed [31:0] state_pred_err_0_5_out,
    output logic signed [31:0] state_pred_err_0_6_out,
    output logic signed [31:0] state_pred_err_0_7_out,
    output logic signed [31:0] state_pred_err_0_8_out,
    output logic signed [31:0] state_pred_err_0_9_out,
    output logic signed [31:0] state_pred_err_0_10_out,
    output logic signed [31:0] state_pred_err_0_11_out,
    output logic signed [31:0] state_pred_err_0_12_out,
    output logic signed [31:0] state_pred_err_1_0_out,
    output logic signed [31:0] state_pred_err_1_1_out,
    output logic signed [31:0] state_pred_err_1_2_out,
    output logic signed [31:0] state_pred_err_1_3_out,
    output logic signed [31:0] state_pred_err_1_4_out,
    output logic signed [31:0] state_pred_err_1_5_out,
    output logic signed [31:0] state_pred_err_1_6_out,
    output logic signed [31:0] state_pred_err_1_7_out,
    output logic signed [31:0] state_pred_err_1_8_out,
    output logic signed [31:0] state_pred_err_1_9_out,
    output logic signed [31:0] state_pred_err_1_10_out,
    output logic signed [31:0] state_pred_err_1_11_out,
    output logic signed [31:0] state_pred_err_1_12_out,
    output logic signed [31:0] state_pred_err_2_0_out,
    output logic signed [31:0] state_pred_err_2_1_out,
    output logic signed [31:0] state_pred_err_2_2_out,
    output logic signed [31:0] state_pred_err_2_3_out,
    output logic signed [31:0] state_pred_err_2_4_out,
    output logic signed [31:0] state_pred_err_2_5_out,
    output logic signed [31:0] state_pred_err_2_6_out,
    output logic signed [31:0] state_pred_err_2_7_out,
    output logic signed [31:0] state_pred_err_2_8_out,
    output logic signed [31:0] state_pred_err_2_9_out,
    output logic signed [31:0] state_pred_err_2_10_out,
    output logic signed [31:0] state_pred_err_2_11_out,
    output logic signed [31:0] state_pred_err_2_12_out,
    output logic signed [31:0] state_pred_err_3_0_out,
    output logic signed [31:0] state_pred_err_3_1_out,
    output logic signed [31:0] state_pred_err_3_2_out,
    output logic signed [31:0] state_pred_err_3_3_out,
    output logic signed [31:0] state_pred_err_3_4_out,
    output logic signed [31:0] state_pred_err_3_5_out,
    output logic signed [31:0] state_pred_err_3_6_out,
    output logic signed [31:0] state_pred_err_3_7_out,
    output logic signed [31:0] state_pred_err_3_8_out,
    output logic signed [31:0] state_pred_err_3_9_out,
    output logic signed [31:0] state_pred_err_3_10_out,
    output logic signed [31:0] state_pred_err_3_11_out,
    output logic signed [31:0] state_pred_err_3_12_out,
    output logic signed [31:0] state_last_err_0_0_0_out,
    output logic signed [31:0] state_last_err_0_0_1_out,
    output logic signed [31:0] state_last_err_0_0_2_out,
    output logic signed [31:0] state_last_err_0_0_3_out,
    output logic signed [31:0] state_last_err_0_0_4_out,
    output logic signed [31:0] state_last_err_0_0_5_out,
    output logic signed [31:0] state_last_err_0_0_6_out,
    output logic signed [31:0] state_last_err_0_0_7_out,
    output logic signed [31:0] state_last_err_0_0_8_out,
    output logic signed [31:0] state_last_err_0_0_9_out,
    output logic signed [31:0] state_last_err_0_0_10_out,
    output logic signed [31:0] state_last_err_0_0_11_out,
    output logic signed [31:0] state_last_err_0_0_12_out,
    output logic signed [31:0] state_last_err_0_1_0_out,
    output logic signed [31:0] state_last_err_0_1_1_out,
    output logic signed [31:0] state_last_err_0_1_2_out,
    output logic signed [31:0] state_last_err_0_1_3_out,
    output logic signed [31:0] state_last_err_0_1_4_out,
    output logic signed [31:0] state_last_err_0_1_5_out,
    output logic signed [31:0] state_last_err_0_1_6_out,
    output logic signed [31:0] state_last_err_0_1_7_out,
    output logic signed [31:0] state_last_err_0_1_8_out,
    output logic signed [31:0] state_last_err_0_1_9_out,
    output logic signed [31:0] state_last_err_0_1_10_out,
    output logic signed [31:0] state_last_err_0_1_11_out,
    output logic signed [31:0] state_last_err_0_1_12_out,
    output logic signed [31:0] state_last_err_0_2_0_out,
    output logic signed [31:0] state_last_err_0_2_1_out,
    output logic signed [31:0] state_last_err_0_2_2_out,
    output logic signed [31:0] state_last_err_0_2_3_out,
    output logic signed [31:0] state_last_err_0_2_4_out,
    output logic signed [31:0] state_last_err_0_2_5_out,
    output logic signed [31:0] state_last_err_0_2_6_out,
    output logic signed [31:0] state_last_err_0_2_7_out,
    output logic signed [31:0] state_last_err_0_2_8_out,
    output logic signed [31:0] state_last_err_0_2_9_out,
    output logic signed [31:0] state_last_err_0_2_10_out,
    output logic signed [31:0] state_last_err_0_2_11_out,
    output logic signed [31:0] state_last_err_0_2_12_out,
    output logic signed [31:0] state_last_err_1_0_0_out,
    output logic signed [31:0] state_last_err_1_0_1_out,
    output logic signed [31:0] state_last_err_1_0_2_out,
    output logic signed [31:0] state_last_err_1_0_3_out,
    output logic signed [31:0] state_last_err_1_0_4_out,
    output logic signed [31:0] state_last_err_1_0_5_out,
    output logic signed [31:0] state_last_err_1_0_6_out,
    output logic signed [31:0] state_last_err_1_0_7_out,
    output logic signed [31:0] state_last_err_1_0_8_out,
    output logic signed [31:0] state_last_err_1_0_9_out,
    output logic signed [31:0] state_last_err_1_0_10_out,
    output logic signed [31:0] state_last_err_1_0_11_out,
    output logic signed [31:0] state_last_err_1_0_12_out,
    output logic signed [31:0] state_last_err_1_1_0_out,
    output logic signed [31:0] state_last_err_1_1_1_out,
    output logic signed [31:0] state_last_err_1_1_2_out,
    output logic signed [31:0] state_last_err_1_1_3_out,
    output logic signed [31:0] state_last_err_1_1_4_out,
    output logic signed [31:0] state_last_err_1_1_5_out,
    output logic signed [31:0] state_last_err_1_1_6_out,
    output logic signed [31:0] state_last_err_1_1_7_out,
    output logic signed [31:0] state_last_err_1_1_8_out,
    output logic signed [31:0] state_last_err_1_1_9_out,
    output logic signed [31:0] state_last_err_1_1_10_out,
    output logic signed [31:0] state_last_err_1_1_11_out,
    output logic signed [31:0] state_last_err_1_1_12_out,
    output logic signed [31:0] state_last_err_1_2_0_out,
    output logic signed [31:0] state_last_err_1_2_1_out,
    output logic signed [31:0] state_last_err_1_2_2_out,
    output logic signed [31:0] state_last_err_1_2_3_out,
    output logic signed [31:0] state_last_err_1_2_4_out,
    output logic signed [31:0] state_last_err_1_2_5_out,
    output logic signed [31:0] state_last_err_1_2_6_out,
    output logic signed [31:0] state_last_err_1_2_7_out,
    output logic signed [31:0] state_last_err_1_2_8_out,
    output logic signed [31:0] state_last_err_1_2_9_out,
    output logic signed [31:0] state_last_err_1_2_10_out,
    output logic signed [31:0] state_last_err_1_2_11_out,
    output logic signed [31:0] state_last_err_1_2_12_out,
    output logic signed [31:0] state_last_err_2_0_0_out,
    output logic signed [31:0] state_last_err_2_0_1_out,
    output logic signed [31:0] state_last_err_2_0_2_out,
    output logic signed [31:0] state_last_err_2_0_3_out,
    output logic signed [31:0] state_last_err_2_0_4_out,
    output logic signed [31:0] state_last_err_2_0_5_out,
    output logic signed [31:0] state_last_err_2_0_6_out,
    output logic signed [31:0] state_last_err_2_0_7_out,
    output logic signed [31:0] state_last_err_2_0_8_out,
    output logic signed [31:0] state_last_err_2_0_9_out,
    output logic signed [31:0] state_last_err_2_0_10_out,
    output logic signed [31:0] state_last_err_2_0_11_out,
    output logic signed [31:0] state_last_err_2_0_12_out,
    output logic signed [31:0] state_last_err_2_1_0_out,
    output logic signed [31:0] state_last_err_2_1_1_out,
    output logic signed [31:0] state_last_err_2_1_2_out,
    output logic signed [31:0] state_last_err_2_1_3_out,
    output logic signed [31:0] state_last_err_2_1_4_out,
    output logic signed [31:0] state_last_err_2_1_5_out,
    output logic signed [31:0] state_last_err_2_1_6_out,
    output logic signed [31:0] state_last_err_2_1_7_out,
    output logic signed [31:0] state_last_err_2_1_8_out,
    output logic signed [31:0] state_last_err_2_1_9_out,
    output logic signed [31:0] state_last_err_2_1_10_out,
    output logic signed [31:0] state_last_err_2_1_11_out,
    output logic signed [31:0] state_last_err_2_1_12_out,
    output logic signed [31:0] state_last_err_2_2_0_out,
    output logic signed [31:0] state_last_err_2_2_1_out,
    output logic signed [31:0] state_last_err_2_2_2_out,
    output logic signed [31:0] state_last_err_2_2_3_out,
    output logic signed [31:0] state_last_err_2_2_4_out,
    output logic signed [31:0] state_last_err_2_2_5_out,
    output logic signed [31:0] state_last_err_2_2_6_out,
    output logic signed [31:0] state_last_err_2_2_7_out,
    output logic signed [31:0] state_last_err_2_2_8_out,
    output logic signed [31:0] state_last_err_2_2_9_out,
    output logic signed [31:0] state_last_err_2_2_10_out,
    output logic signed [31:0] state_last_err_2_2_11_out,
    output logic signed [31:0] state_last_err_2_2_12_out,
    output logic signed [31:0] state_last_err_3_0_0_out,
    output logic signed [31:0] state_last_err_3_0_1_out,
    output logic signed [31:0] state_last_err_3_0_2_out,
    output logic signed [31:0] state_last_err_3_0_3_out,
    output logic signed [31:0] state_last_err_3_0_4_out,
    output logic signed [31:0] state_last_err_3_0_5_out,
    output logic signed [31:0] state_last_err_3_0_6_out,
    output logic signed [31:0] state_last_err_3_0_7_out,
    output logic signed [31:0] state_last_err_3_0_8_out,
    output logic signed [31:0] state_last_err_3_0_9_out,
    output logic signed [31:0] state_last_err_3_0_10_out,
    output logic signed [31:0] state_last_err_3_0_11_out,
    output logic signed [31:0] state_last_err_3_0_12_out,
    output logic signed [31:0] state_last_err_3_1_0_out,
    output logic signed [31:0] state_last_err_3_1_1_out,
    output logic signed [31:0] state_last_err_3_1_2_out,
    output logic signed [31:0] state_last_err_3_1_3_out,
    output logic signed [31:0] state_last_err_3_1_4_out,
    output logic signed [31:0] state_last_err_3_1_5_out,
    output logic signed [31:0] state_last_err_3_1_6_out,
    output logic signed [31:0] state_last_err_3_1_7_out,
    output logic signed [31:0] state_last_err_3_1_8_out,
    output logic signed [31:0] state_last_err_3_1_9_out,
    output logic signed [31:0] state_last_err_3_1_10_out,
    output logic signed [31:0] state_last_err_3_1_11_out,
    output logic signed [31:0] state_last_err_3_1_12_out,
    output logic signed [31:0] state_last_err_3_2_0_out,
    output logic signed [31:0] state_last_err_3_2_1_out,
    output logic signed [31:0] state_last_err_3_2_2_out,
    output logic signed [31:0] state_last_err_3_2_3_out,
    output logic signed [31:0] state_last_err_3_2_4_out,
    output logic signed [31:0] state_last_err_3_2_5_out,
    output logic signed [31:0] state_last_err_3_2_6_out,
    output logic signed [31:0] state_last_err_3_2_7_out,
    output logic signed [31:0] state_last_err_3_2_8_out,
    output logic signed [31:0] state_last_err_3_2_9_out,
    output logic signed [31:0] state_last_err_3_2_10_out,
    output logic signed [31:0] state_last_err_3_2_11_out,
    output logic signed [31:0] state_last_err_3_2_12_out,
    output logic prev_line_pred_write_enable,
    output logic signed [31:0] prev_line_pred_write_index,
    output logic signed [31:0] prev_line_pred_write_value
);
    logic signed [31:0] depth_i;
    logic signed [31:0] max_cpnt_i;
    logic signed [31:0] pixel_mod_i;
    logic signed [31:0] cursamp_i;
    logic signed [31:0] recon_i;
    logic signed [31:0] pred_x_i;
    logic signed [31:0] pixdiff_i;
    logic signed [31:0] modified_i;
    logic signed [31:0] sad3_i;
    logic signed [31:0] min_err_i;
    logic signed [31:0] min_pred_i;
    logic done_i;
    logic signed [31:0] bp_sad_0_i;
    logic signed [31:0] bp_sad_1_i;
    logic signed [31:0] bp_sad_2_i;
    logic signed [31:0] bp_sad_3_i;
    logic signed [31:0] bp_sad_4_i;
    logic signed [31:0] bp_sad_5_i;
    logic signed [31:0] bp_sad_6_i;
    logic signed [31:0] bp_sad_7_i;
    logic signed [31:0] bp_sad_8_i;
    logic signed [31:0] bp_sad_9_i;
    logic signed [31:0] bp_sad_10_i;
    logic signed [31:0] bp_sad_11_i;
    logic signed [31:0] bp_sad_12_i;

    assign depth_i = ((cpnt == 32'sd0) ? state_cpnt_bit_depth_0 : ((cpnt == 32'sd1) ? state_cpnt_bit_depth_1 : ((cpnt == 32'sd2) ? state_cpnt_bit_depth_2 : state_cpnt_bit_depth_3)));

    always_comb begin
        domain_valid = 1'b1;
        state_bpcount_out = state_bpcount;
        state_lastedgecount_out = state_lastedgecount;
        state_edgedetected_out = state_edgedetected;
        state_pred_err_0_0_out = state_pred_err_0_0;
        state_pred_err_0_1_out = state_pred_err_0_1;
        state_pred_err_0_2_out = state_pred_err_0_2;
        state_pred_err_0_3_out = state_pred_err_0_3;
        state_pred_err_0_4_out = state_pred_err_0_4;
        state_pred_err_0_5_out = state_pred_err_0_5;
        state_pred_err_0_6_out = state_pred_err_0_6;
        state_pred_err_0_7_out = state_pred_err_0_7;
        state_pred_err_0_8_out = state_pred_err_0_8;
        state_pred_err_0_9_out = state_pred_err_0_9;
        state_pred_err_0_10_out = state_pred_err_0_10;
        state_pred_err_0_11_out = state_pred_err_0_11;
        state_pred_err_0_12_out = state_pred_err_0_12;
        state_pred_err_1_0_out = state_pred_err_1_0;
        state_pred_err_1_1_out = state_pred_err_1_1;
        state_pred_err_1_2_out = state_pred_err_1_2;
        state_pred_err_1_3_out = state_pred_err_1_3;
        state_pred_err_1_4_out = state_pred_err_1_4;
        state_pred_err_1_5_out = state_pred_err_1_5;
        state_pred_err_1_6_out = state_pred_err_1_6;
        state_pred_err_1_7_out = state_pred_err_1_7;
        state_pred_err_1_8_out = state_pred_err_1_8;
        state_pred_err_1_9_out = state_pred_err_1_9;
        state_pred_err_1_10_out = state_pred_err_1_10;
        state_pred_err_1_11_out = state_pred_err_1_11;
        state_pred_err_1_12_out = state_pred_err_1_12;
        state_pred_err_2_0_out = state_pred_err_2_0;
        state_pred_err_2_1_out = state_pred_err_2_1;
        state_pred_err_2_2_out = state_pred_err_2_2;
        state_pred_err_2_3_out = state_pred_err_2_3;
        state_pred_err_2_4_out = state_pred_err_2_4;
        state_pred_err_2_5_out = state_pred_err_2_5;
        state_pred_err_2_6_out = state_pred_err_2_6;
        state_pred_err_2_7_out = state_pred_err_2_7;
        state_pred_err_2_8_out = state_pred_err_2_8;
        state_pred_err_2_9_out = state_pred_err_2_9;
        state_pred_err_2_10_out = state_pred_err_2_10;
        state_pred_err_2_11_out = state_pred_err_2_11;
        state_pred_err_2_12_out = state_pred_err_2_12;
        state_pred_err_3_0_out = state_pred_err_3_0;
        state_pred_err_3_1_out = state_pred_err_3_1;
        state_pred_err_3_2_out = state_pred_err_3_2;
        state_pred_err_3_3_out = state_pred_err_3_3;
        state_pred_err_3_4_out = state_pred_err_3_4;
        state_pred_err_3_5_out = state_pred_err_3_5;
        state_pred_err_3_6_out = state_pred_err_3_6;
        state_pred_err_3_7_out = state_pred_err_3_7;
        state_pred_err_3_8_out = state_pred_err_3_8;
        state_pred_err_3_9_out = state_pred_err_3_9;
        state_pred_err_3_10_out = state_pred_err_3_10;
        state_pred_err_3_11_out = state_pred_err_3_11;
        state_pred_err_3_12_out = state_pred_err_3_12;
        state_last_err_0_0_0_out = state_last_err_0_0_0;
        state_last_err_0_0_1_out = state_last_err_0_0_1;
        state_last_err_0_0_2_out = state_last_err_0_0_2;
        state_last_err_0_0_3_out = state_last_err_0_0_3;
        state_last_err_0_0_4_out = state_last_err_0_0_4;
        state_last_err_0_0_5_out = state_last_err_0_0_5;
        state_last_err_0_0_6_out = state_last_err_0_0_6;
        state_last_err_0_0_7_out = state_last_err_0_0_7;
        state_last_err_0_0_8_out = state_last_err_0_0_8;
        state_last_err_0_0_9_out = state_last_err_0_0_9;
        state_last_err_0_0_10_out = state_last_err_0_0_10;
        state_last_err_0_0_11_out = state_last_err_0_0_11;
        state_last_err_0_0_12_out = state_last_err_0_0_12;
        state_last_err_0_1_0_out = state_last_err_0_1_0;
        state_last_err_0_1_1_out = state_last_err_0_1_1;
        state_last_err_0_1_2_out = state_last_err_0_1_2;
        state_last_err_0_1_3_out = state_last_err_0_1_3;
        state_last_err_0_1_4_out = state_last_err_0_1_4;
        state_last_err_0_1_5_out = state_last_err_0_1_5;
        state_last_err_0_1_6_out = state_last_err_0_1_6;
        state_last_err_0_1_7_out = state_last_err_0_1_7;
        state_last_err_0_1_8_out = state_last_err_0_1_8;
        state_last_err_0_1_9_out = state_last_err_0_1_9;
        state_last_err_0_1_10_out = state_last_err_0_1_10;
        state_last_err_0_1_11_out = state_last_err_0_1_11;
        state_last_err_0_1_12_out = state_last_err_0_1_12;
        state_last_err_0_2_0_out = state_last_err_0_2_0;
        state_last_err_0_2_1_out = state_last_err_0_2_1;
        state_last_err_0_2_2_out = state_last_err_0_2_2;
        state_last_err_0_2_3_out = state_last_err_0_2_3;
        state_last_err_0_2_4_out = state_last_err_0_2_4;
        state_last_err_0_2_5_out = state_last_err_0_2_5;
        state_last_err_0_2_6_out = state_last_err_0_2_6;
        state_last_err_0_2_7_out = state_last_err_0_2_7;
        state_last_err_0_2_8_out = state_last_err_0_2_8;
        state_last_err_0_2_9_out = state_last_err_0_2_9;
        state_last_err_0_2_10_out = state_last_err_0_2_10;
        state_last_err_0_2_11_out = state_last_err_0_2_11;
        state_last_err_0_2_12_out = state_last_err_0_2_12;
        state_last_err_1_0_0_out = state_last_err_1_0_0;
        state_last_err_1_0_1_out = state_last_err_1_0_1;
        state_last_err_1_0_2_out = state_last_err_1_0_2;
        state_last_err_1_0_3_out = state_last_err_1_0_3;
        state_last_err_1_0_4_out = state_last_err_1_0_4;
        state_last_err_1_0_5_out = state_last_err_1_0_5;
        state_last_err_1_0_6_out = state_last_err_1_0_6;
        state_last_err_1_0_7_out = state_last_err_1_0_7;
        state_last_err_1_0_8_out = state_last_err_1_0_8;
        state_last_err_1_0_9_out = state_last_err_1_0_9;
        state_last_err_1_0_10_out = state_last_err_1_0_10;
        state_last_err_1_0_11_out = state_last_err_1_0_11;
        state_last_err_1_0_12_out = state_last_err_1_0_12;
        state_last_err_1_1_0_out = state_last_err_1_1_0;
        state_last_err_1_1_1_out = state_last_err_1_1_1;
        state_last_err_1_1_2_out = state_last_err_1_1_2;
        state_last_err_1_1_3_out = state_last_err_1_1_3;
        state_last_err_1_1_4_out = state_last_err_1_1_4;
        state_last_err_1_1_5_out = state_last_err_1_1_5;
        state_last_err_1_1_6_out = state_last_err_1_1_6;
        state_last_err_1_1_7_out = state_last_err_1_1_7;
        state_last_err_1_1_8_out = state_last_err_1_1_8;
        state_last_err_1_1_9_out = state_last_err_1_1_9;
        state_last_err_1_1_10_out = state_last_err_1_1_10;
        state_last_err_1_1_11_out = state_last_err_1_1_11;
        state_last_err_1_1_12_out = state_last_err_1_1_12;
        state_last_err_1_2_0_out = state_last_err_1_2_0;
        state_last_err_1_2_1_out = state_last_err_1_2_1;
        state_last_err_1_2_2_out = state_last_err_1_2_2;
        state_last_err_1_2_3_out = state_last_err_1_2_3;
        state_last_err_1_2_4_out = state_last_err_1_2_4;
        state_last_err_1_2_5_out = state_last_err_1_2_5;
        state_last_err_1_2_6_out = state_last_err_1_2_6;
        state_last_err_1_2_7_out = state_last_err_1_2_7;
        state_last_err_1_2_8_out = state_last_err_1_2_8;
        state_last_err_1_2_9_out = state_last_err_1_2_9;
        state_last_err_1_2_10_out = state_last_err_1_2_10;
        state_last_err_1_2_11_out = state_last_err_1_2_11;
        state_last_err_1_2_12_out = state_last_err_1_2_12;
        state_last_err_2_0_0_out = state_last_err_2_0_0;
        state_last_err_2_0_1_out = state_last_err_2_0_1;
        state_last_err_2_0_2_out = state_last_err_2_0_2;
        state_last_err_2_0_3_out = state_last_err_2_0_3;
        state_last_err_2_0_4_out = state_last_err_2_0_4;
        state_last_err_2_0_5_out = state_last_err_2_0_5;
        state_last_err_2_0_6_out = state_last_err_2_0_6;
        state_last_err_2_0_7_out = state_last_err_2_0_7;
        state_last_err_2_0_8_out = state_last_err_2_0_8;
        state_last_err_2_0_9_out = state_last_err_2_0_9;
        state_last_err_2_0_10_out = state_last_err_2_0_10;
        state_last_err_2_0_11_out = state_last_err_2_0_11;
        state_last_err_2_0_12_out = state_last_err_2_0_12;
        state_last_err_2_1_0_out = state_last_err_2_1_0;
        state_last_err_2_1_1_out = state_last_err_2_1_1;
        state_last_err_2_1_2_out = state_last_err_2_1_2;
        state_last_err_2_1_3_out = state_last_err_2_1_3;
        state_last_err_2_1_4_out = state_last_err_2_1_4;
        state_last_err_2_1_5_out = state_last_err_2_1_5;
        state_last_err_2_1_6_out = state_last_err_2_1_6;
        state_last_err_2_1_7_out = state_last_err_2_1_7;
        state_last_err_2_1_8_out = state_last_err_2_1_8;
        state_last_err_2_1_9_out = state_last_err_2_1_9;
        state_last_err_2_1_10_out = state_last_err_2_1_10;
        state_last_err_2_1_11_out = state_last_err_2_1_11;
        state_last_err_2_1_12_out = state_last_err_2_1_12;
        state_last_err_2_2_0_out = state_last_err_2_2_0;
        state_last_err_2_2_1_out = state_last_err_2_2_1;
        state_last_err_2_2_2_out = state_last_err_2_2_2;
        state_last_err_2_2_3_out = state_last_err_2_2_3;
        state_last_err_2_2_4_out = state_last_err_2_2_4;
        state_last_err_2_2_5_out = state_last_err_2_2_5;
        state_last_err_2_2_6_out = state_last_err_2_2_6;
        state_last_err_2_2_7_out = state_last_err_2_2_7;
        state_last_err_2_2_8_out = state_last_err_2_2_8;
        state_last_err_2_2_9_out = state_last_err_2_2_9;
        state_last_err_2_2_10_out = state_last_err_2_2_10;
        state_last_err_2_2_11_out = state_last_err_2_2_11;
        state_last_err_2_2_12_out = state_last_err_2_2_12;
        state_last_err_3_0_0_out = state_last_err_3_0_0;
        state_last_err_3_0_1_out = state_last_err_3_0_1;
        state_last_err_3_0_2_out = state_last_err_3_0_2;
        state_last_err_3_0_3_out = state_last_err_3_0_3;
        state_last_err_3_0_4_out = state_last_err_3_0_4;
        state_last_err_3_0_5_out = state_last_err_3_0_5;
        state_last_err_3_0_6_out = state_last_err_3_0_6;
        state_last_err_3_0_7_out = state_last_err_3_0_7;
        state_last_err_3_0_8_out = state_last_err_3_0_8;
        state_last_err_3_0_9_out = state_last_err_3_0_9;
        state_last_err_3_0_10_out = state_last_err_3_0_10;
        state_last_err_3_0_11_out = state_last_err_3_0_11;
        state_last_err_3_0_12_out = state_last_err_3_0_12;
        state_last_err_3_1_0_out = state_last_err_3_1_0;
        state_last_err_3_1_1_out = state_last_err_3_1_1;
        state_last_err_3_1_2_out = state_last_err_3_1_2;
        state_last_err_3_1_3_out = state_last_err_3_1_3;
        state_last_err_3_1_4_out = state_last_err_3_1_4;
        state_last_err_3_1_5_out = state_last_err_3_1_5;
        state_last_err_3_1_6_out = state_last_err_3_1_6;
        state_last_err_3_1_7_out = state_last_err_3_1_7;
        state_last_err_3_1_8_out = state_last_err_3_1_8;
        state_last_err_3_1_9_out = state_last_err_3_1_9;
        state_last_err_3_1_10_out = state_last_err_3_1_10;
        state_last_err_3_1_11_out = state_last_err_3_1_11;
        state_last_err_3_1_12_out = state_last_err_3_1_12;
        state_last_err_3_2_0_out = state_last_err_3_2_0;
        state_last_err_3_2_1_out = state_last_err_3_2_1;
        state_last_err_3_2_2_out = state_last_err_3_2_2;
        state_last_err_3_2_3_out = state_last_err_3_2_3;
        state_last_err_3_2_4_out = state_last_err_3_2_4;
        state_last_err_3_2_5_out = state_last_err_3_2_5;
        state_last_err_3_2_6_out = state_last_err_3_2_6;
        state_last_err_3_2_7_out = state_last_err_3_2_7;
        state_last_err_3_2_8_out = state_last_err_3_2_8;
        state_last_err_3_2_9_out = state_last_err_3_2_9;
        state_last_err_3_2_10_out = state_last_err_3_2_10;
        state_last_err_3_2_11_out = state_last_err_3_2_11;
        state_last_err_3_2_12_out = state_last_err_3_2_12;
        prev_line_pred_write_enable = 1'b0;
        prev_line_pred_write_index = hpos / 32'sd3;
        prev_line_pred_write_value = 32'sd0;
        max_cpnt_i = 32'sd0;
        pixel_mod_i = 32'sd0;
        cursamp_i = 32'sd0;
        recon_i = 32'sd0;
        pred_x_i = 32'sd0;
        pixdiff_i = 32'sd0;
        modified_i = 32'sd0;
        sad3_i = 32'sd0;
        min_err_i = 32'sd0;
        min_pred_i = 32'sd0;
        done_i = 1'b0;
        bp_sad_0_i = 32'sd0;
        bp_sad_1_i = 32'sd0;
        bp_sad_2_i = 32'sd0;
        bp_sad_3_i = 32'sd0;
        bp_sad_4_i = 32'sd0;
        bp_sad_5_i = 32'sd0;
        bp_sad_6_i = 32'sd0;
        bp_sad_7_i = 32'sd0;
        bp_sad_8_i = 32'sd0;
        bp_sad_9_i = 32'sd0;
        bp_sad_10_i = 32'sd0;
        bp_sad_11_i = 32'sd0;
        bp_sad_12_i = 32'sd0;
        if ((cpnt < 0) || (cpnt >= 32'sd4) || (hpos < 0) || (state_numcomponents < 32'sd3) || (state_numcomponents > 32'sd4) || (cfg_bits_per_component < 32'sd8) || (cfg_bits_per_component > 32'sd16) || (depth_i < 32'sd8) || (depth_i > 32'sd16)) domain_valid = 1'b0;
        max_cpnt_i = state_numcomponents - 1;
        if (cfg_native_420 != 0) max_cpnt_i = 32'sd1;
        if ((cfg_native_420 != 0) && (cpnt > 32'sd1)) done_i = 1'b1;
        if (!done_i) begin
            if (hpos == 0) begin
                state_bpcount_out = 32'sd0;
                state_lastedgecount_out = 32'sd10;
                if (state_numcomponents > 32'sd0) begin
                    state_last_err_0_0_0_out = 32'sd0;
                    state_last_err_0_0_1_out = 32'sd0;
                    state_last_err_0_0_2_out = 32'sd0;
                    state_last_err_0_0_3_out = 32'sd0;
                    state_last_err_0_0_4_out = 32'sd0;
                    state_last_err_0_0_5_out = 32'sd0;
                    state_last_err_0_0_6_out = 32'sd0;
                    state_last_err_0_0_7_out = 32'sd0;
                    state_last_err_0_0_8_out = 32'sd0;
                    state_last_err_0_0_9_out = 32'sd0;
                    state_last_err_0_0_10_out = 32'sd0;
                    state_last_err_0_0_11_out = 32'sd0;
                    state_last_err_0_0_12_out = 32'sd0;
                    state_last_err_0_1_0_out = 32'sd0;
                    state_last_err_0_1_1_out = 32'sd0;
                    state_last_err_0_1_2_out = 32'sd0;
                    state_last_err_0_1_3_out = 32'sd0;
                    state_last_err_0_1_4_out = 32'sd0;
                    state_last_err_0_1_5_out = 32'sd0;
                    state_last_err_0_1_6_out = 32'sd0;
                    state_last_err_0_1_7_out = 32'sd0;
                    state_last_err_0_1_8_out = 32'sd0;
                    state_last_err_0_1_9_out = 32'sd0;
                    state_last_err_0_1_10_out = 32'sd0;
                    state_last_err_0_1_11_out = 32'sd0;
                    state_last_err_0_1_12_out = 32'sd0;
                    state_last_err_0_2_0_out = 32'sd0;
                    state_last_err_0_2_1_out = 32'sd0;
                    state_last_err_0_2_2_out = 32'sd0;
                    state_last_err_0_2_3_out = 32'sd0;
                    state_last_err_0_2_4_out = 32'sd0;
                    state_last_err_0_2_5_out = 32'sd0;
                    state_last_err_0_2_6_out = 32'sd0;
                    state_last_err_0_2_7_out = 32'sd0;
                    state_last_err_0_2_8_out = 32'sd0;
                    state_last_err_0_2_9_out = 32'sd0;
                    state_last_err_0_2_10_out = 32'sd0;
                    state_last_err_0_2_11_out = 32'sd0;
                    state_last_err_0_2_12_out = 32'sd0;
                end
                if (state_numcomponents > 32'sd1) begin
                    state_last_err_1_0_0_out = 32'sd0;
                    state_last_err_1_0_1_out = 32'sd0;
                    state_last_err_1_0_2_out = 32'sd0;
                    state_last_err_1_0_3_out = 32'sd0;
                    state_last_err_1_0_4_out = 32'sd0;
                    state_last_err_1_0_5_out = 32'sd0;
                    state_last_err_1_0_6_out = 32'sd0;
                    state_last_err_1_0_7_out = 32'sd0;
                    state_last_err_1_0_8_out = 32'sd0;
                    state_last_err_1_0_9_out = 32'sd0;
                    state_last_err_1_0_10_out = 32'sd0;
                    state_last_err_1_0_11_out = 32'sd0;
                    state_last_err_1_0_12_out = 32'sd0;
                    state_last_err_1_1_0_out = 32'sd0;
                    state_last_err_1_1_1_out = 32'sd0;
                    state_last_err_1_1_2_out = 32'sd0;
                    state_last_err_1_1_3_out = 32'sd0;
                    state_last_err_1_1_4_out = 32'sd0;
                    state_last_err_1_1_5_out = 32'sd0;
                    state_last_err_1_1_6_out = 32'sd0;
                    state_last_err_1_1_7_out = 32'sd0;
                    state_last_err_1_1_8_out = 32'sd0;
                    state_last_err_1_1_9_out = 32'sd0;
                    state_last_err_1_1_10_out = 32'sd0;
                    state_last_err_1_1_11_out = 32'sd0;
                    state_last_err_1_1_12_out = 32'sd0;
                    state_last_err_1_2_0_out = 32'sd0;
                    state_last_err_1_2_1_out = 32'sd0;
                    state_last_err_1_2_2_out = 32'sd0;
                    state_last_err_1_2_3_out = 32'sd0;
                    state_last_err_1_2_4_out = 32'sd0;
                    state_last_err_1_2_5_out = 32'sd0;
                    state_last_err_1_2_6_out = 32'sd0;
                    state_last_err_1_2_7_out = 32'sd0;
                    state_last_err_1_2_8_out = 32'sd0;
                    state_last_err_1_2_9_out = 32'sd0;
                    state_last_err_1_2_10_out = 32'sd0;
                    state_last_err_1_2_11_out = 32'sd0;
                    state_last_err_1_2_12_out = 32'sd0;
                end
                if (state_numcomponents > 32'sd2) begin
                    state_last_err_2_0_0_out = 32'sd0;
                    state_last_err_2_0_1_out = 32'sd0;
                    state_last_err_2_0_2_out = 32'sd0;
                    state_last_err_2_0_3_out = 32'sd0;
                    state_last_err_2_0_4_out = 32'sd0;
                    state_last_err_2_0_5_out = 32'sd0;
                    state_last_err_2_0_6_out = 32'sd0;
                    state_last_err_2_0_7_out = 32'sd0;
                    state_last_err_2_0_8_out = 32'sd0;
                    state_last_err_2_0_9_out = 32'sd0;
                    state_last_err_2_0_10_out = 32'sd0;
                    state_last_err_2_0_11_out = 32'sd0;
                    state_last_err_2_0_12_out = 32'sd0;
                    state_last_err_2_1_0_out = 32'sd0;
                    state_last_err_2_1_1_out = 32'sd0;
                    state_last_err_2_1_2_out = 32'sd0;
                    state_last_err_2_1_3_out = 32'sd0;
                    state_last_err_2_1_4_out = 32'sd0;
                    state_last_err_2_1_5_out = 32'sd0;
                    state_last_err_2_1_6_out = 32'sd0;
                    state_last_err_2_1_7_out = 32'sd0;
                    state_last_err_2_1_8_out = 32'sd0;
                    state_last_err_2_1_9_out = 32'sd0;
                    state_last_err_2_1_10_out = 32'sd0;
                    state_last_err_2_1_11_out = 32'sd0;
                    state_last_err_2_1_12_out = 32'sd0;
                    state_last_err_2_2_0_out = 32'sd0;
                    state_last_err_2_2_1_out = 32'sd0;
                    state_last_err_2_2_2_out = 32'sd0;
                    state_last_err_2_2_3_out = 32'sd0;
                    state_last_err_2_2_4_out = 32'sd0;
                    state_last_err_2_2_5_out = 32'sd0;
                    state_last_err_2_2_6_out = 32'sd0;
                    state_last_err_2_2_7_out = 32'sd0;
                    state_last_err_2_2_8_out = 32'sd0;
                    state_last_err_2_2_9_out = 32'sd0;
                    state_last_err_2_2_10_out = 32'sd0;
                    state_last_err_2_2_11_out = 32'sd0;
                    state_last_err_2_2_12_out = 32'sd0;
                end
                if (state_numcomponents > 32'sd3) begin
                    state_last_err_3_0_0_out = 32'sd0;
                    state_last_err_3_0_1_out = 32'sd0;
                    state_last_err_3_0_2_out = 32'sd0;
                    state_last_err_3_0_3_out = 32'sd0;
                    state_last_err_3_0_4_out = 32'sd0;
                    state_last_err_3_0_5_out = 32'sd0;
                    state_last_err_3_0_6_out = 32'sd0;
                    state_last_err_3_0_7_out = 32'sd0;
                    state_last_err_3_0_8_out = 32'sd0;
                    state_last_err_3_0_9_out = 32'sd0;
                    state_last_err_3_0_10_out = 32'sd0;
                    state_last_err_3_0_11_out = 32'sd0;
                    state_last_err_3_0_12_out = 32'sd0;
                    state_last_err_3_1_0_out = 32'sd0;
                    state_last_err_3_1_1_out = 32'sd0;
                    state_last_err_3_1_2_out = 32'sd0;
                    state_last_err_3_1_3_out = 32'sd0;
                    state_last_err_3_1_4_out = 32'sd0;
                    state_last_err_3_1_5_out = 32'sd0;
                    state_last_err_3_1_6_out = 32'sd0;
                    state_last_err_3_1_7_out = 32'sd0;
                    state_last_err_3_1_8_out = 32'sd0;
                    state_last_err_3_1_9_out = 32'sd0;
                    state_last_err_3_1_10_out = 32'sd0;
                    state_last_err_3_1_11_out = 32'sd0;
                    state_last_err_3_1_12_out = 32'sd0;
                    state_last_err_3_2_0_out = 32'sd0;
                    state_last_err_3_2_1_out = 32'sd0;
                    state_last_err_3_2_2_out = 32'sd0;
                    state_last_err_3_2_3_out = 32'sd0;
                    state_last_err_3_2_4_out = 32'sd0;
                    state_last_err_3_2_5_out = 32'sd0;
                    state_last_err_3_2_6_out = 32'sd0;
                    state_last_err_3_2_7_out = 32'sd0;
                    state_last_err_3_2_8_out = 32'sd0;
                    state_last_err_3_2_9_out = 32'sd0;
                    state_last_err_3_2_10_out = 32'sd0;
                    state_last_err_3_2_11_out = 32'sd0;
                    state_last_err_3_2_12_out = 32'sd0;
                end
            end
            recon_i = line_sample_p5;
            if (hpos > 0) pixdiff_i = recon_i - line_sample_p4;
            else pixdiff_i = recon_i - (32'sd1 <<< (depth_i - 1));
            if (pixdiff_i < 0) pixdiff_i = -pixdiff_i;
            if (cpnt == 0) state_edgedetected_out = 32'sd0;
            if (pixdiff_i > (32'sd32 <<< (cfg_bits_per_component - 32'sd8)))
                state_edgedetected_out = 32'sd1;
            if (cpnt == max_cpnt_i) begin
                if (state_edgedetected_out != 0) state_lastedgecount_out = 32'sd0;
                else state_lastedgecount_out = state_lastedgecount_out + 1;
            end
            cursamp_i = ((hpos / 32'sd3) % 32'sd3);
            pixel_mod_i = hpos % 32'sd3;
            if ((cpnt == 32'sd0) && (pixel_mod_i == 0))
                state_pred_err_0_0_out = 32'sd0;
            if ((cpnt == 32'sd1) && (pixel_mod_i == 0))
                state_pred_err_1_0_out = 32'sd0;
            if ((cpnt == 32'sd2) && (pixel_mod_i == 0))
                state_pred_err_2_0_out = 32'sd0;
            if ((cpnt == 32'sd3) && (pixel_mod_i == 0))
                state_pred_err_3_0_out = 32'sd0;
            if (hpos > 32'sd0) pred_x_i = line_sample_p4;
            else pred_x_i = 32'sd1 <<< (depth_i - 1);
            pixdiff_i = recon_i - pred_x_i;
            if (pixdiff_i < 0) pixdiff_i = -pixdiff_i;
            modified_i = pixdiff_i >>> (depth_i - 32'sd7);
            if (modified_i > 32'sd63) modified_i = 32'sd63;
            if (cpnt == 32'sd0)
                state_pred_err_0_0_out = state_pred_err_0_0_out + modified_i;
            if (cpnt == 32'sd1)
                state_pred_err_1_0_out = state_pred_err_1_0_out + modified_i;
            if (cpnt == 32'sd2)
                state_pred_err_2_0_out = state_pred_err_2_0_out + modified_i;
            if (cpnt == 32'sd3)
                state_pred_err_3_0_out = state_pred_err_3_0_out + modified_i;
            if ((cpnt == 32'sd0) && (pixel_mod_i == 0))
                state_pred_err_0_1_out = 32'sd0;
            if ((cpnt == 32'sd1) && (pixel_mod_i == 0))
                state_pred_err_1_1_out = 32'sd0;
            if ((cpnt == 32'sd2) && (pixel_mod_i == 0))
                state_pred_err_2_1_out = 32'sd0;
            if ((cpnt == 32'sd3) && (pixel_mod_i == 0))
                state_pred_err_3_1_out = 32'sd0;
            if (hpos > 32'sd1) pred_x_i = line_sample_p3;
            else pred_x_i = 32'sd1 <<< (depth_i - 1);
            pixdiff_i = recon_i - pred_x_i;
            if (pixdiff_i < 0) pixdiff_i = -pixdiff_i;
            modified_i = pixdiff_i >>> (depth_i - 32'sd7);
            if (modified_i > 32'sd63) modified_i = 32'sd63;
            if (cpnt == 32'sd0)
                state_pred_err_0_1_out = state_pred_err_0_1_out + modified_i;
            if (cpnt == 32'sd1)
                state_pred_err_1_1_out = state_pred_err_1_1_out + modified_i;
            if (cpnt == 32'sd2)
                state_pred_err_2_1_out = state_pred_err_2_1_out + modified_i;
            if (cpnt == 32'sd3)
                state_pred_err_3_1_out = state_pred_err_3_1_out + modified_i;
            if ((cpnt == 32'sd0) && (pixel_mod_i == 0))
                state_pred_err_0_2_out = 32'sd0;
            if ((cpnt == 32'sd1) && (pixel_mod_i == 0))
                state_pred_err_1_2_out = 32'sd0;
            if ((cpnt == 32'sd2) && (pixel_mod_i == 0))
                state_pred_err_2_2_out = 32'sd0;
            if ((cpnt == 32'sd3) && (pixel_mod_i == 0))
                state_pred_err_3_2_out = 32'sd0;
            if (hpos > 32'sd2) pred_x_i = line_sample_p2;
            else pred_x_i = 32'sd1 <<< (depth_i - 1);
            pixdiff_i = recon_i - pred_x_i;
            if (pixdiff_i < 0) pixdiff_i = -pixdiff_i;
            modified_i = pixdiff_i >>> (depth_i - 32'sd7);
            if (modified_i > 32'sd63) modified_i = 32'sd63;
            if (cpnt == 32'sd0)
                state_pred_err_0_2_out = state_pred_err_0_2_out + modified_i;
            if (cpnt == 32'sd1)
                state_pred_err_1_2_out = state_pred_err_1_2_out + modified_i;
            if (cpnt == 32'sd2)
                state_pred_err_2_2_out = state_pred_err_2_2_out + modified_i;
            if (cpnt == 32'sd3)
                state_pred_err_3_2_out = state_pred_err_3_2_out + modified_i;
            if ((cpnt == 32'sd0) && (pixel_mod_i == 0))
                state_pred_err_0_3_out = 32'sd0;
            if ((cpnt == 32'sd1) && (pixel_mod_i == 0))
                state_pred_err_1_3_out = 32'sd0;
            if ((cpnt == 32'sd2) && (pixel_mod_i == 0))
                state_pred_err_2_3_out = 32'sd0;
            if ((cpnt == 32'sd3) && (pixel_mod_i == 0))
                state_pred_err_3_3_out = 32'sd0;
            if (hpos > 32'sd3) pred_x_i = line_sample_p1;
            else pred_x_i = 32'sd1 <<< (depth_i - 1);
            pixdiff_i = recon_i - pred_x_i;
            if (pixdiff_i < 0) pixdiff_i = -pixdiff_i;
            modified_i = pixdiff_i >>> (depth_i - 32'sd7);
            if (modified_i > 32'sd63) modified_i = 32'sd63;
            if (cpnt == 32'sd0)
                state_pred_err_0_3_out = state_pred_err_0_3_out + modified_i;
            if (cpnt == 32'sd1)
                state_pred_err_1_3_out = state_pred_err_1_3_out + modified_i;
            if (cpnt == 32'sd2)
                state_pred_err_2_3_out = state_pred_err_2_3_out + modified_i;
            if (cpnt == 32'sd3)
                state_pred_err_3_3_out = state_pred_err_3_3_out + modified_i;
            if ((cpnt == 32'sd0) && (pixel_mod_i == 0))
                state_pred_err_0_4_out = 32'sd0;
            if ((cpnt == 32'sd1) && (pixel_mod_i == 0))
                state_pred_err_1_4_out = 32'sd0;
            if ((cpnt == 32'sd2) && (pixel_mod_i == 0))
                state_pred_err_2_4_out = 32'sd0;
            if ((cpnt == 32'sd3) && (pixel_mod_i == 0))
                state_pred_err_3_4_out = 32'sd0;
            if (hpos > 32'sd4) pred_x_i = line_sample_p0;
            else pred_x_i = 32'sd1 <<< (depth_i - 1);
            pixdiff_i = recon_i - pred_x_i;
            if (pixdiff_i < 0) pixdiff_i = -pixdiff_i;
            modified_i = pixdiff_i >>> (depth_i - 32'sd7);
            if (modified_i > 32'sd63) modified_i = 32'sd63;
            if (cpnt == 32'sd0)
                state_pred_err_0_4_out = state_pred_err_0_4_out + modified_i;
            if (cpnt == 32'sd1)
                state_pred_err_1_4_out = state_pred_err_1_4_out + modified_i;
            if (cpnt == 32'sd2)
                state_pred_err_2_4_out = state_pred_err_2_4_out + modified_i;
            if (cpnt == 32'sd3)
                state_pred_err_3_4_out = state_pred_err_3_4_out + modified_i;
            if ((cpnt == 32'sd0) && (pixel_mod_i == 0))
                state_pred_err_0_5_out = 32'sd0;
            if ((cpnt == 32'sd1) && (pixel_mod_i == 0))
                state_pred_err_1_5_out = 32'sd0;
            if ((cpnt == 32'sd2) && (pixel_mod_i == 0))
                state_pred_err_2_5_out = 32'sd0;
            if ((cpnt == 32'sd3) && (pixel_mod_i == 0))
                state_pred_err_3_5_out = 32'sd0;
            if (hpos > 32'sd5) pred_x_i = line_sample_m1;
            else pred_x_i = 32'sd1 <<< (depth_i - 1);
            pixdiff_i = recon_i - pred_x_i;
            if (pixdiff_i < 0) pixdiff_i = -pixdiff_i;
            modified_i = pixdiff_i >>> (depth_i - 32'sd7);
            if (modified_i > 32'sd63) modified_i = 32'sd63;
            if (cpnt == 32'sd0)
                state_pred_err_0_5_out = state_pred_err_0_5_out + modified_i;
            if (cpnt == 32'sd1)
                state_pred_err_1_5_out = state_pred_err_1_5_out + modified_i;
            if (cpnt == 32'sd2)
                state_pred_err_2_5_out = state_pred_err_2_5_out + modified_i;
            if (cpnt == 32'sd3)
                state_pred_err_3_5_out = state_pred_err_3_5_out + modified_i;
            if ((cpnt == 32'sd0) && (pixel_mod_i == 0))
                state_pred_err_0_6_out = 32'sd0;
            if ((cpnt == 32'sd1) && (pixel_mod_i == 0))
                state_pred_err_1_6_out = 32'sd0;
            if ((cpnt == 32'sd2) && (pixel_mod_i == 0))
                state_pred_err_2_6_out = 32'sd0;
            if ((cpnt == 32'sd3) && (pixel_mod_i == 0))
                state_pred_err_3_6_out = 32'sd0;
            if (hpos > 32'sd6) pred_x_i = line_sample_m2;
            else pred_x_i = 32'sd1 <<< (depth_i - 1);
            pixdiff_i = recon_i - pred_x_i;
            if (pixdiff_i < 0) pixdiff_i = -pixdiff_i;
            modified_i = pixdiff_i >>> (depth_i - 32'sd7);
            if (modified_i > 32'sd63) modified_i = 32'sd63;
            if (cpnt == 32'sd0)
                state_pred_err_0_6_out = state_pred_err_0_6_out + modified_i;
            if (cpnt == 32'sd1)
                state_pred_err_1_6_out = state_pred_err_1_6_out + modified_i;
            if (cpnt == 32'sd2)
                state_pred_err_2_6_out = state_pred_err_2_6_out + modified_i;
            if (cpnt == 32'sd3)
                state_pred_err_3_6_out = state_pred_err_3_6_out + modified_i;
            if ((cpnt == 32'sd0) && (pixel_mod_i == 0))
                state_pred_err_0_7_out = 32'sd0;
            if ((cpnt == 32'sd1) && (pixel_mod_i == 0))
                state_pred_err_1_7_out = 32'sd0;
            if ((cpnt == 32'sd2) && (pixel_mod_i == 0))
                state_pred_err_2_7_out = 32'sd0;
            if ((cpnt == 32'sd3) && (pixel_mod_i == 0))
                state_pred_err_3_7_out = 32'sd0;
            if (hpos > 32'sd7) pred_x_i = line_sample_m3;
            else pred_x_i = 32'sd1 <<< (depth_i - 1);
            pixdiff_i = recon_i - pred_x_i;
            if (pixdiff_i < 0) pixdiff_i = -pixdiff_i;
            modified_i = pixdiff_i >>> (depth_i - 32'sd7);
            if (modified_i > 32'sd63) modified_i = 32'sd63;
            if (cpnt == 32'sd0)
                state_pred_err_0_7_out = state_pred_err_0_7_out + modified_i;
            if (cpnt == 32'sd1)
                state_pred_err_1_7_out = state_pred_err_1_7_out + modified_i;
            if (cpnt == 32'sd2)
                state_pred_err_2_7_out = state_pred_err_2_7_out + modified_i;
            if (cpnt == 32'sd3)
                state_pred_err_3_7_out = state_pred_err_3_7_out + modified_i;
            if ((cpnt == 32'sd0) && (pixel_mod_i == 0))
                state_pred_err_0_8_out = 32'sd0;
            if ((cpnt == 32'sd1) && (pixel_mod_i == 0))
                state_pred_err_1_8_out = 32'sd0;
            if ((cpnt == 32'sd2) && (pixel_mod_i == 0))
                state_pred_err_2_8_out = 32'sd0;
            if ((cpnt == 32'sd3) && (pixel_mod_i == 0))
                state_pred_err_3_8_out = 32'sd0;
            if (hpos > 32'sd8) pred_x_i = line_sample_m4;
            else pred_x_i = 32'sd1 <<< (depth_i - 1);
            pixdiff_i = recon_i - pred_x_i;
            if (pixdiff_i < 0) pixdiff_i = -pixdiff_i;
            modified_i = pixdiff_i >>> (depth_i - 32'sd7);
            if (modified_i > 32'sd63) modified_i = 32'sd63;
            if (cpnt == 32'sd0)
                state_pred_err_0_8_out = state_pred_err_0_8_out + modified_i;
            if (cpnt == 32'sd1)
                state_pred_err_1_8_out = state_pred_err_1_8_out + modified_i;
            if (cpnt == 32'sd2)
                state_pred_err_2_8_out = state_pred_err_2_8_out + modified_i;
            if (cpnt == 32'sd3)
                state_pred_err_3_8_out = state_pred_err_3_8_out + modified_i;
            if ((cpnt == 32'sd0) && (pixel_mod_i == 0))
                state_pred_err_0_9_out = 32'sd0;
            if ((cpnt == 32'sd1) && (pixel_mod_i == 0))
                state_pred_err_1_9_out = 32'sd0;
            if ((cpnt == 32'sd2) && (pixel_mod_i == 0))
                state_pred_err_2_9_out = 32'sd0;
            if ((cpnt == 32'sd3) && (pixel_mod_i == 0))
                state_pred_err_3_9_out = 32'sd0;
            if (hpos > 32'sd9) pred_x_i = line_sample_m5;
            else pred_x_i = 32'sd1 <<< (depth_i - 1);
            pixdiff_i = recon_i - pred_x_i;
            if (pixdiff_i < 0) pixdiff_i = -pixdiff_i;
            modified_i = pixdiff_i >>> (depth_i - 32'sd7);
            if (modified_i > 32'sd63) modified_i = 32'sd63;
            if (cpnt == 32'sd0)
                state_pred_err_0_9_out = state_pred_err_0_9_out + modified_i;
            if (cpnt == 32'sd1)
                state_pred_err_1_9_out = state_pred_err_1_9_out + modified_i;
            if (cpnt == 32'sd2)
                state_pred_err_2_9_out = state_pred_err_2_9_out + modified_i;
            if (cpnt == 32'sd3)
                state_pred_err_3_9_out = state_pred_err_3_9_out + modified_i;
            if ((cpnt == 32'sd0) && (pixel_mod_i == 0))
                state_pred_err_0_10_out = 32'sd0;
            if ((cpnt == 32'sd1) && (pixel_mod_i == 0))
                state_pred_err_1_10_out = 32'sd0;
            if ((cpnt == 32'sd2) && (pixel_mod_i == 0))
                state_pred_err_2_10_out = 32'sd0;
            if ((cpnt == 32'sd3) && (pixel_mod_i == 0))
                state_pred_err_3_10_out = 32'sd0;
            if (hpos > 32'sd10) pred_x_i = line_sample_m6;
            else pred_x_i = 32'sd1 <<< (depth_i - 1);
            pixdiff_i = recon_i - pred_x_i;
            if (pixdiff_i < 0) pixdiff_i = -pixdiff_i;
            modified_i = pixdiff_i >>> (depth_i - 32'sd7);
            if (modified_i > 32'sd63) modified_i = 32'sd63;
            if (cpnt == 32'sd0)
                state_pred_err_0_10_out = state_pred_err_0_10_out + modified_i;
            if (cpnt == 32'sd1)
                state_pred_err_1_10_out = state_pred_err_1_10_out + modified_i;
            if (cpnt == 32'sd2)
                state_pred_err_2_10_out = state_pred_err_2_10_out + modified_i;
            if (cpnt == 32'sd3)
                state_pred_err_3_10_out = state_pred_err_3_10_out + modified_i;
            if ((cpnt == 32'sd0) && (pixel_mod_i == 0))
                state_pred_err_0_11_out = 32'sd0;
            if ((cpnt == 32'sd1) && (pixel_mod_i == 0))
                state_pred_err_1_11_out = 32'sd0;
            if ((cpnt == 32'sd2) && (pixel_mod_i == 0))
                state_pred_err_2_11_out = 32'sd0;
            if ((cpnt == 32'sd3) && (pixel_mod_i == 0))
                state_pred_err_3_11_out = 32'sd0;
            if (hpos > 32'sd11) pred_x_i = line_sample_m7;
            else pred_x_i = 32'sd1 <<< (depth_i - 1);
            pixdiff_i = recon_i - pred_x_i;
            if (pixdiff_i < 0) pixdiff_i = -pixdiff_i;
            modified_i = pixdiff_i >>> (depth_i - 32'sd7);
            if (modified_i > 32'sd63) modified_i = 32'sd63;
            if (cpnt == 32'sd0)
                state_pred_err_0_11_out = state_pred_err_0_11_out + modified_i;
            if (cpnt == 32'sd1)
                state_pred_err_1_11_out = state_pred_err_1_11_out + modified_i;
            if (cpnt == 32'sd2)
                state_pred_err_2_11_out = state_pred_err_2_11_out + modified_i;
            if (cpnt == 32'sd3)
                state_pred_err_3_11_out = state_pred_err_3_11_out + modified_i;
            if ((cpnt == 32'sd0) && (pixel_mod_i == 0))
                state_pred_err_0_12_out = 32'sd0;
            if ((cpnt == 32'sd1) && (pixel_mod_i == 0))
                state_pred_err_1_12_out = 32'sd0;
            if ((cpnt == 32'sd2) && (pixel_mod_i == 0))
                state_pred_err_2_12_out = 32'sd0;
            if ((cpnt == 32'sd3) && (pixel_mod_i == 0))
                state_pred_err_3_12_out = 32'sd0;
            if (hpos > 32'sd12) pred_x_i = line_sample_m8;
            else pred_x_i = 32'sd1 <<< (depth_i - 1);
            pixdiff_i = recon_i - pred_x_i;
            if (pixdiff_i < 0) pixdiff_i = -pixdiff_i;
            modified_i = pixdiff_i >>> (depth_i - 32'sd7);
            if (modified_i > 32'sd63) modified_i = 32'sd63;
            if (cpnt == 32'sd0)
                state_pred_err_0_12_out = state_pred_err_0_12_out + modified_i;
            if (cpnt == 32'sd1)
                state_pred_err_1_12_out = state_pred_err_1_12_out + modified_i;
            if (cpnt == 32'sd2)
                state_pred_err_2_12_out = state_pred_err_2_12_out + modified_i;
            if (cpnt == 32'sd3)
                state_pred_err_3_12_out = state_pred_err_3_12_out + modified_i;
            if (pixel_mod_i == 32'sd2) begin
                if (cpnt == 32'sd0) begin
                    if (cursamp_i == 32'sd0) begin
                        state_last_err_0_0_0_out = state_pred_err_0_0_out;
                        state_last_err_0_0_1_out = state_pred_err_0_1_out;
                        state_last_err_0_0_2_out = state_pred_err_0_2_out;
                        state_last_err_0_0_3_out = state_pred_err_0_3_out;
                        state_last_err_0_0_4_out = state_pred_err_0_4_out;
                        state_last_err_0_0_5_out = state_pred_err_0_5_out;
                        state_last_err_0_0_6_out = state_pred_err_0_6_out;
                        state_last_err_0_0_7_out = state_pred_err_0_7_out;
                        state_last_err_0_0_8_out = state_pred_err_0_8_out;
                        state_last_err_0_0_9_out = state_pred_err_0_9_out;
                        state_last_err_0_0_10_out = state_pred_err_0_10_out;
                        state_last_err_0_0_11_out = state_pred_err_0_11_out;
                        state_last_err_0_0_12_out = state_pred_err_0_12_out;
                    end
                    if (cursamp_i == 32'sd1) begin
                        state_last_err_0_1_0_out = state_pred_err_0_0_out;
                        state_last_err_0_1_1_out = state_pred_err_0_1_out;
                        state_last_err_0_1_2_out = state_pred_err_0_2_out;
                        state_last_err_0_1_3_out = state_pred_err_0_3_out;
                        state_last_err_0_1_4_out = state_pred_err_0_4_out;
                        state_last_err_0_1_5_out = state_pred_err_0_5_out;
                        state_last_err_0_1_6_out = state_pred_err_0_6_out;
                        state_last_err_0_1_7_out = state_pred_err_0_7_out;
                        state_last_err_0_1_8_out = state_pred_err_0_8_out;
                        state_last_err_0_1_9_out = state_pred_err_0_9_out;
                        state_last_err_0_1_10_out = state_pred_err_0_10_out;
                        state_last_err_0_1_11_out = state_pred_err_0_11_out;
                        state_last_err_0_1_12_out = state_pred_err_0_12_out;
                    end
                    if (cursamp_i == 32'sd2) begin
                        state_last_err_0_2_0_out = state_pred_err_0_0_out;
                        state_last_err_0_2_1_out = state_pred_err_0_1_out;
                        state_last_err_0_2_2_out = state_pred_err_0_2_out;
                        state_last_err_0_2_3_out = state_pred_err_0_3_out;
                        state_last_err_0_2_4_out = state_pred_err_0_4_out;
                        state_last_err_0_2_5_out = state_pred_err_0_5_out;
                        state_last_err_0_2_6_out = state_pred_err_0_6_out;
                        state_last_err_0_2_7_out = state_pred_err_0_7_out;
                        state_last_err_0_2_8_out = state_pred_err_0_8_out;
                        state_last_err_0_2_9_out = state_pred_err_0_9_out;
                        state_last_err_0_2_10_out = state_pred_err_0_10_out;
                        state_last_err_0_2_11_out = state_pred_err_0_11_out;
                        state_last_err_0_2_12_out = state_pred_err_0_12_out;
                    end
                end
                if (cpnt == 32'sd1) begin
                    if (cursamp_i == 32'sd0) begin
                        state_last_err_1_0_0_out = state_pred_err_1_0_out;
                        state_last_err_1_0_1_out = state_pred_err_1_1_out;
                        state_last_err_1_0_2_out = state_pred_err_1_2_out;
                        state_last_err_1_0_3_out = state_pred_err_1_3_out;
                        state_last_err_1_0_4_out = state_pred_err_1_4_out;
                        state_last_err_1_0_5_out = state_pred_err_1_5_out;
                        state_last_err_1_0_6_out = state_pred_err_1_6_out;
                        state_last_err_1_0_7_out = state_pred_err_1_7_out;
                        state_last_err_1_0_8_out = state_pred_err_1_8_out;
                        state_last_err_1_0_9_out = state_pred_err_1_9_out;
                        state_last_err_1_0_10_out = state_pred_err_1_10_out;
                        state_last_err_1_0_11_out = state_pred_err_1_11_out;
                        state_last_err_1_0_12_out = state_pred_err_1_12_out;
                    end
                    if (cursamp_i == 32'sd1) begin
                        state_last_err_1_1_0_out = state_pred_err_1_0_out;
                        state_last_err_1_1_1_out = state_pred_err_1_1_out;
                        state_last_err_1_1_2_out = state_pred_err_1_2_out;
                        state_last_err_1_1_3_out = state_pred_err_1_3_out;
                        state_last_err_1_1_4_out = state_pred_err_1_4_out;
                        state_last_err_1_1_5_out = state_pred_err_1_5_out;
                        state_last_err_1_1_6_out = state_pred_err_1_6_out;
                        state_last_err_1_1_7_out = state_pred_err_1_7_out;
                        state_last_err_1_1_8_out = state_pred_err_1_8_out;
                        state_last_err_1_1_9_out = state_pred_err_1_9_out;
                        state_last_err_1_1_10_out = state_pred_err_1_10_out;
                        state_last_err_1_1_11_out = state_pred_err_1_11_out;
                        state_last_err_1_1_12_out = state_pred_err_1_12_out;
                    end
                    if (cursamp_i == 32'sd2) begin
                        state_last_err_1_2_0_out = state_pred_err_1_0_out;
                        state_last_err_1_2_1_out = state_pred_err_1_1_out;
                        state_last_err_1_2_2_out = state_pred_err_1_2_out;
                        state_last_err_1_2_3_out = state_pred_err_1_3_out;
                        state_last_err_1_2_4_out = state_pred_err_1_4_out;
                        state_last_err_1_2_5_out = state_pred_err_1_5_out;
                        state_last_err_1_2_6_out = state_pred_err_1_6_out;
                        state_last_err_1_2_7_out = state_pred_err_1_7_out;
                        state_last_err_1_2_8_out = state_pred_err_1_8_out;
                        state_last_err_1_2_9_out = state_pred_err_1_9_out;
                        state_last_err_1_2_10_out = state_pred_err_1_10_out;
                        state_last_err_1_2_11_out = state_pred_err_1_11_out;
                        state_last_err_1_2_12_out = state_pred_err_1_12_out;
                    end
                end
                if (cpnt == 32'sd2) begin
                    if (cursamp_i == 32'sd0) begin
                        state_last_err_2_0_0_out = state_pred_err_2_0_out;
                        state_last_err_2_0_1_out = state_pred_err_2_1_out;
                        state_last_err_2_0_2_out = state_pred_err_2_2_out;
                        state_last_err_2_0_3_out = state_pred_err_2_3_out;
                        state_last_err_2_0_4_out = state_pred_err_2_4_out;
                        state_last_err_2_0_5_out = state_pred_err_2_5_out;
                        state_last_err_2_0_6_out = state_pred_err_2_6_out;
                        state_last_err_2_0_7_out = state_pred_err_2_7_out;
                        state_last_err_2_0_8_out = state_pred_err_2_8_out;
                        state_last_err_2_0_9_out = state_pred_err_2_9_out;
                        state_last_err_2_0_10_out = state_pred_err_2_10_out;
                        state_last_err_2_0_11_out = state_pred_err_2_11_out;
                        state_last_err_2_0_12_out = state_pred_err_2_12_out;
                    end
                    if (cursamp_i == 32'sd1) begin
                        state_last_err_2_1_0_out = state_pred_err_2_0_out;
                        state_last_err_2_1_1_out = state_pred_err_2_1_out;
                        state_last_err_2_1_2_out = state_pred_err_2_2_out;
                        state_last_err_2_1_3_out = state_pred_err_2_3_out;
                        state_last_err_2_1_4_out = state_pred_err_2_4_out;
                        state_last_err_2_1_5_out = state_pred_err_2_5_out;
                        state_last_err_2_1_6_out = state_pred_err_2_6_out;
                        state_last_err_2_1_7_out = state_pred_err_2_7_out;
                        state_last_err_2_1_8_out = state_pred_err_2_8_out;
                        state_last_err_2_1_9_out = state_pred_err_2_9_out;
                        state_last_err_2_1_10_out = state_pred_err_2_10_out;
                        state_last_err_2_1_11_out = state_pred_err_2_11_out;
                        state_last_err_2_1_12_out = state_pred_err_2_12_out;
                    end
                    if (cursamp_i == 32'sd2) begin
                        state_last_err_2_2_0_out = state_pred_err_2_0_out;
                        state_last_err_2_2_1_out = state_pred_err_2_1_out;
                        state_last_err_2_2_2_out = state_pred_err_2_2_out;
                        state_last_err_2_2_3_out = state_pred_err_2_3_out;
                        state_last_err_2_2_4_out = state_pred_err_2_4_out;
                        state_last_err_2_2_5_out = state_pred_err_2_5_out;
                        state_last_err_2_2_6_out = state_pred_err_2_6_out;
                        state_last_err_2_2_7_out = state_pred_err_2_7_out;
                        state_last_err_2_2_8_out = state_pred_err_2_8_out;
                        state_last_err_2_2_9_out = state_pred_err_2_9_out;
                        state_last_err_2_2_10_out = state_pred_err_2_10_out;
                        state_last_err_2_2_11_out = state_pred_err_2_11_out;
                        state_last_err_2_2_12_out = state_pred_err_2_12_out;
                    end
                end
                if (cpnt == 32'sd3) begin
                    if (cursamp_i == 32'sd0) begin
                        state_last_err_3_0_0_out = state_pred_err_3_0_out;
                        state_last_err_3_0_1_out = state_pred_err_3_1_out;
                        state_last_err_3_0_2_out = state_pred_err_3_2_out;
                        state_last_err_3_0_3_out = state_pred_err_3_3_out;
                        state_last_err_3_0_4_out = state_pred_err_3_4_out;
                        state_last_err_3_0_5_out = state_pred_err_3_5_out;
                        state_last_err_3_0_6_out = state_pred_err_3_6_out;
                        state_last_err_3_0_7_out = state_pred_err_3_7_out;
                        state_last_err_3_0_8_out = state_pred_err_3_8_out;
                        state_last_err_3_0_9_out = state_pred_err_3_9_out;
                        state_last_err_3_0_10_out = state_pred_err_3_10_out;
                        state_last_err_3_0_11_out = state_pred_err_3_11_out;
                        state_last_err_3_0_12_out = state_pred_err_3_12_out;
                    end
                    if (cursamp_i == 32'sd1) begin
                        state_last_err_3_1_0_out = state_pred_err_3_0_out;
                        state_last_err_3_1_1_out = state_pred_err_3_1_out;
                        state_last_err_3_1_2_out = state_pred_err_3_2_out;
                        state_last_err_3_1_3_out = state_pred_err_3_3_out;
                        state_last_err_3_1_4_out = state_pred_err_3_4_out;
                        state_last_err_3_1_5_out = state_pred_err_3_5_out;
                        state_last_err_3_1_6_out = state_pred_err_3_6_out;
                        state_last_err_3_1_7_out = state_pred_err_3_7_out;
                        state_last_err_3_1_8_out = state_pred_err_3_8_out;
                        state_last_err_3_1_9_out = state_pred_err_3_9_out;
                        state_last_err_3_1_10_out = state_pred_err_3_10_out;
                        state_last_err_3_1_11_out = state_pred_err_3_11_out;
                        state_last_err_3_1_12_out = state_pred_err_3_12_out;
                    end
                    if (cursamp_i == 32'sd2) begin
                        state_last_err_3_2_0_out = state_pred_err_3_0_out;
                        state_last_err_3_2_1_out = state_pred_err_3_1_out;
                        state_last_err_3_2_2_out = state_pred_err_3_2_out;
                        state_last_err_3_2_3_out = state_pred_err_3_3_out;
                        state_last_err_3_2_4_out = state_pred_err_3_4_out;
                        state_last_err_3_2_5_out = state_pred_err_3_5_out;
                        state_last_err_3_2_6_out = state_pred_err_3_6_out;
                        state_last_err_3_2_7_out = state_pred_err_3_7_out;
                        state_last_err_3_2_8_out = state_pred_err_3_8_out;
                        state_last_err_3_2_9_out = state_pred_err_3_9_out;
                        state_last_err_3_2_10_out = state_pred_err_3_10_out;
                        state_last_err_3_2_11_out = state_pred_err_3_11_out;
                        state_last_err_3_2_12_out = state_pred_err_3_12_out;
                    end
                end
                if (cpnt >= max_cpnt_i) begin
                    bp_sad_0_i = 32'sd0;
                    sad3_i = 32'sd0;
                    if (state_numcomponents > 32'sd0)
                        sad3_i = sad3_i + state_last_err_0_0_0_out;
                    if (state_numcomponents > 32'sd1)
                        sad3_i = sad3_i + state_last_err_1_0_0_out;
                    if (state_numcomponents > 32'sd2)
                        sad3_i = sad3_i + state_last_err_2_0_0_out;
                    if (state_numcomponents > 32'sd3)
                        sad3_i = sad3_i + state_last_err_3_0_0_out;
                    if (sad3_i > 32'sd511) sad3_i = 32'sd511;
                    bp_sad_0_i = bp_sad_0_i + sad3_i;
                    sad3_i = 32'sd0;
                    if (state_numcomponents > 32'sd0)
                        sad3_i = sad3_i + state_last_err_0_1_0_out;
                    if (state_numcomponents > 32'sd1)
                        sad3_i = sad3_i + state_last_err_1_1_0_out;
                    if (state_numcomponents > 32'sd2)
                        sad3_i = sad3_i + state_last_err_2_1_0_out;
                    if (state_numcomponents > 32'sd3)
                        sad3_i = sad3_i + state_last_err_3_1_0_out;
                    if (sad3_i > 32'sd511) sad3_i = 32'sd511;
                    bp_sad_0_i = bp_sad_0_i + sad3_i;
                    sad3_i = 32'sd0;
                    if (state_numcomponents > 32'sd0)
                        sad3_i = sad3_i + state_last_err_0_2_0_out;
                    if (state_numcomponents > 32'sd1)
                        sad3_i = sad3_i + state_last_err_1_2_0_out;
                    if (state_numcomponents > 32'sd2)
                        sad3_i = sad3_i + state_last_err_2_2_0_out;
                    if (state_numcomponents > 32'sd3)
                        sad3_i = sad3_i + state_last_err_3_2_0_out;
                    if (sad3_i > 32'sd511) sad3_i = 32'sd511;
                    bp_sad_0_i = bp_sad_0_i + sad3_i;
                    bp_sad_0_i = bp_sad_0_i >>> 3;
                    bp_sad_1_i = 32'sd0;
                    sad3_i = 32'sd0;
                    if (state_numcomponents > 32'sd0)
                        sad3_i = sad3_i + state_last_err_0_0_1_out;
                    if (state_numcomponents > 32'sd1)
                        sad3_i = sad3_i + state_last_err_1_0_1_out;
                    if (state_numcomponents > 32'sd2)
                        sad3_i = sad3_i + state_last_err_2_0_1_out;
                    if (state_numcomponents > 32'sd3)
                        sad3_i = sad3_i + state_last_err_3_0_1_out;
                    if (sad3_i > 32'sd511) sad3_i = 32'sd511;
                    bp_sad_1_i = bp_sad_1_i + sad3_i;
                    sad3_i = 32'sd0;
                    if (state_numcomponents > 32'sd0)
                        sad3_i = sad3_i + state_last_err_0_1_1_out;
                    if (state_numcomponents > 32'sd1)
                        sad3_i = sad3_i + state_last_err_1_1_1_out;
                    if (state_numcomponents > 32'sd2)
                        sad3_i = sad3_i + state_last_err_2_1_1_out;
                    if (state_numcomponents > 32'sd3)
                        sad3_i = sad3_i + state_last_err_3_1_1_out;
                    if (sad3_i > 32'sd511) sad3_i = 32'sd511;
                    bp_sad_1_i = bp_sad_1_i + sad3_i;
                    sad3_i = 32'sd0;
                    if (state_numcomponents > 32'sd0)
                        sad3_i = sad3_i + state_last_err_0_2_1_out;
                    if (state_numcomponents > 32'sd1)
                        sad3_i = sad3_i + state_last_err_1_2_1_out;
                    if (state_numcomponents > 32'sd2)
                        sad3_i = sad3_i + state_last_err_2_2_1_out;
                    if (state_numcomponents > 32'sd3)
                        sad3_i = sad3_i + state_last_err_3_2_1_out;
                    if (sad3_i > 32'sd511) sad3_i = 32'sd511;
                    bp_sad_1_i = bp_sad_1_i + sad3_i;
                    bp_sad_1_i = bp_sad_1_i >>> 3;
                    bp_sad_2_i = 32'sd0;
                    sad3_i = 32'sd0;
                    if (state_numcomponents > 32'sd0)
                        sad3_i = sad3_i + state_last_err_0_0_2_out;
                    if (state_numcomponents > 32'sd1)
                        sad3_i = sad3_i + state_last_err_1_0_2_out;
                    if (state_numcomponents > 32'sd2)
                        sad3_i = sad3_i + state_last_err_2_0_2_out;
                    if (state_numcomponents > 32'sd3)
                        sad3_i = sad3_i + state_last_err_3_0_2_out;
                    if (sad3_i > 32'sd511) sad3_i = 32'sd511;
                    bp_sad_2_i = bp_sad_2_i + sad3_i;
                    sad3_i = 32'sd0;
                    if (state_numcomponents > 32'sd0)
                        sad3_i = sad3_i + state_last_err_0_1_2_out;
                    if (state_numcomponents > 32'sd1)
                        sad3_i = sad3_i + state_last_err_1_1_2_out;
                    if (state_numcomponents > 32'sd2)
                        sad3_i = sad3_i + state_last_err_2_1_2_out;
                    if (state_numcomponents > 32'sd3)
                        sad3_i = sad3_i + state_last_err_3_1_2_out;
                    if (sad3_i > 32'sd511) sad3_i = 32'sd511;
                    bp_sad_2_i = bp_sad_2_i + sad3_i;
                    sad3_i = 32'sd0;
                    if (state_numcomponents > 32'sd0)
                        sad3_i = sad3_i + state_last_err_0_2_2_out;
                    if (state_numcomponents > 32'sd1)
                        sad3_i = sad3_i + state_last_err_1_2_2_out;
                    if (state_numcomponents > 32'sd2)
                        sad3_i = sad3_i + state_last_err_2_2_2_out;
                    if (state_numcomponents > 32'sd3)
                        sad3_i = sad3_i + state_last_err_3_2_2_out;
                    if (sad3_i > 32'sd511) sad3_i = 32'sd511;
                    bp_sad_2_i = bp_sad_2_i + sad3_i;
                    bp_sad_2_i = bp_sad_2_i >>> 3;
                    bp_sad_3_i = 32'sd0;
                    sad3_i = 32'sd0;
                    if (state_numcomponents > 32'sd0)
                        sad3_i = sad3_i + state_last_err_0_0_3_out;
                    if (state_numcomponents > 32'sd1)
                        sad3_i = sad3_i + state_last_err_1_0_3_out;
                    if (state_numcomponents > 32'sd2)
                        sad3_i = sad3_i + state_last_err_2_0_3_out;
                    if (state_numcomponents > 32'sd3)
                        sad3_i = sad3_i + state_last_err_3_0_3_out;
                    if (sad3_i > 32'sd511) sad3_i = 32'sd511;
                    bp_sad_3_i = bp_sad_3_i + sad3_i;
                    sad3_i = 32'sd0;
                    if (state_numcomponents > 32'sd0)
                        sad3_i = sad3_i + state_last_err_0_1_3_out;
                    if (state_numcomponents > 32'sd1)
                        sad3_i = sad3_i + state_last_err_1_1_3_out;
                    if (state_numcomponents > 32'sd2)
                        sad3_i = sad3_i + state_last_err_2_1_3_out;
                    if (state_numcomponents > 32'sd3)
                        sad3_i = sad3_i + state_last_err_3_1_3_out;
                    if (sad3_i > 32'sd511) sad3_i = 32'sd511;
                    bp_sad_3_i = bp_sad_3_i + sad3_i;
                    sad3_i = 32'sd0;
                    if (state_numcomponents > 32'sd0)
                        sad3_i = sad3_i + state_last_err_0_2_3_out;
                    if (state_numcomponents > 32'sd1)
                        sad3_i = sad3_i + state_last_err_1_2_3_out;
                    if (state_numcomponents > 32'sd2)
                        sad3_i = sad3_i + state_last_err_2_2_3_out;
                    if (state_numcomponents > 32'sd3)
                        sad3_i = sad3_i + state_last_err_3_2_3_out;
                    if (sad3_i > 32'sd511) sad3_i = 32'sd511;
                    bp_sad_3_i = bp_sad_3_i + sad3_i;
                    bp_sad_3_i = bp_sad_3_i >>> 3;
                    bp_sad_4_i = 32'sd0;
                    sad3_i = 32'sd0;
                    if (state_numcomponents > 32'sd0)
                        sad3_i = sad3_i + state_last_err_0_0_4_out;
                    if (state_numcomponents > 32'sd1)
                        sad3_i = sad3_i + state_last_err_1_0_4_out;
                    if (state_numcomponents > 32'sd2)
                        sad3_i = sad3_i + state_last_err_2_0_4_out;
                    if (state_numcomponents > 32'sd3)
                        sad3_i = sad3_i + state_last_err_3_0_4_out;
                    if (sad3_i > 32'sd511) sad3_i = 32'sd511;
                    bp_sad_4_i = bp_sad_4_i + sad3_i;
                    sad3_i = 32'sd0;
                    if (state_numcomponents > 32'sd0)
                        sad3_i = sad3_i + state_last_err_0_1_4_out;
                    if (state_numcomponents > 32'sd1)
                        sad3_i = sad3_i + state_last_err_1_1_4_out;
                    if (state_numcomponents > 32'sd2)
                        sad3_i = sad3_i + state_last_err_2_1_4_out;
                    if (state_numcomponents > 32'sd3)
                        sad3_i = sad3_i + state_last_err_3_1_4_out;
                    if (sad3_i > 32'sd511) sad3_i = 32'sd511;
                    bp_sad_4_i = bp_sad_4_i + sad3_i;
                    sad3_i = 32'sd0;
                    if (state_numcomponents > 32'sd0)
                        sad3_i = sad3_i + state_last_err_0_2_4_out;
                    if (state_numcomponents > 32'sd1)
                        sad3_i = sad3_i + state_last_err_1_2_4_out;
                    if (state_numcomponents > 32'sd2)
                        sad3_i = sad3_i + state_last_err_2_2_4_out;
                    if (state_numcomponents > 32'sd3)
                        sad3_i = sad3_i + state_last_err_3_2_4_out;
                    if (sad3_i > 32'sd511) sad3_i = 32'sd511;
                    bp_sad_4_i = bp_sad_4_i + sad3_i;
                    bp_sad_4_i = bp_sad_4_i >>> 3;
                    bp_sad_5_i = 32'sd0;
                    sad3_i = 32'sd0;
                    if (state_numcomponents > 32'sd0)
                        sad3_i = sad3_i + state_last_err_0_0_5_out;
                    if (state_numcomponents > 32'sd1)
                        sad3_i = sad3_i + state_last_err_1_0_5_out;
                    if (state_numcomponents > 32'sd2)
                        sad3_i = sad3_i + state_last_err_2_0_5_out;
                    if (state_numcomponents > 32'sd3)
                        sad3_i = sad3_i + state_last_err_3_0_5_out;
                    if (sad3_i > 32'sd511) sad3_i = 32'sd511;
                    bp_sad_5_i = bp_sad_5_i + sad3_i;
                    sad3_i = 32'sd0;
                    if (state_numcomponents > 32'sd0)
                        sad3_i = sad3_i + state_last_err_0_1_5_out;
                    if (state_numcomponents > 32'sd1)
                        sad3_i = sad3_i + state_last_err_1_1_5_out;
                    if (state_numcomponents > 32'sd2)
                        sad3_i = sad3_i + state_last_err_2_1_5_out;
                    if (state_numcomponents > 32'sd3)
                        sad3_i = sad3_i + state_last_err_3_1_5_out;
                    if (sad3_i > 32'sd511) sad3_i = 32'sd511;
                    bp_sad_5_i = bp_sad_5_i + sad3_i;
                    sad3_i = 32'sd0;
                    if (state_numcomponents > 32'sd0)
                        sad3_i = sad3_i + state_last_err_0_2_5_out;
                    if (state_numcomponents > 32'sd1)
                        sad3_i = sad3_i + state_last_err_1_2_5_out;
                    if (state_numcomponents > 32'sd2)
                        sad3_i = sad3_i + state_last_err_2_2_5_out;
                    if (state_numcomponents > 32'sd3)
                        sad3_i = sad3_i + state_last_err_3_2_5_out;
                    if (sad3_i > 32'sd511) sad3_i = 32'sd511;
                    bp_sad_5_i = bp_sad_5_i + sad3_i;
                    bp_sad_5_i = bp_sad_5_i >>> 3;
                    bp_sad_6_i = 32'sd0;
                    sad3_i = 32'sd0;
                    if (state_numcomponents > 32'sd0)
                        sad3_i = sad3_i + state_last_err_0_0_6_out;
                    if (state_numcomponents > 32'sd1)
                        sad3_i = sad3_i + state_last_err_1_0_6_out;
                    if (state_numcomponents > 32'sd2)
                        sad3_i = sad3_i + state_last_err_2_0_6_out;
                    if (state_numcomponents > 32'sd3)
                        sad3_i = sad3_i + state_last_err_3_0_6_out;
                    if (sad3_i > 32'sd511) sad3_i = 32'sd511;
                    bp_sad_6_i = bp_sad_6_i + sad3_i;
                    sad3_i = 32'sd0;
                    if (state_numcomponents > 32'sd0)
                        sad3_i = sad3_i + state_last_err_0_1_6_out;
                    if (state_numcomponents > 32'sd1)
                        sad3_i = sad3_i + state_last_err_1_1_6_out;
                    if (state_numcomponents > 32'sd2)
                        sad3_i = sad3_i + state_last_err_2_1_6_out;
                    if (state_numcomponents > 32'sd3)
                        sad3_i = sad3_i + state_last_err_3_1_6_out;
                    if (sad3_i > 32'sd511) sad3_i = 32'sd511;
                    bp_sad_6_i = bp_sad_6_i + sad3_i;
                    sad3_i = 32'sd0;
                    if (state_numcomponents > 32'sd0)
                        sad3_i = sad3_i + state_last_err_0_2_6_out;
                    if (state_numcomponents > 32'sd1)
                        sad3_i = sad3_i + state_last_err_1_2_6_out;
                    if (state_numcomponents > 32'sd2)
                        sad3_i = sad3_i + state_last_err_2_2_6_out;
                    if (state_numcomponents > 32'sd3)
                        sad3_i = sad3_i + state_last_err_3_2_6_out;
                    if (sad3_i > 32'sd511) sad3_i = 32'sd511;
                    bp_sad_6_i = bp_sad_6_i + sad3_i;
                    bp_sad_6_i = bp_sad_6_i >>> 3;
                    bp_sad_7_i = 32'sd0;
                    sad3_i = 32'sd0;
                    if (state_numcomponents > 32'sd0)
                        sad3_i = sad3_i + state_last_err_0_0_7_out;
                    if (state_numcomponents > 32'sd1)
                        sad3_i = sad3_i + state_last_err_1_0_7_out;
                    if (state_numcomponents > 32'sd2)
                        sad3_i = sad3_i + state_last_err_2_0_7_out;
                    if (state_numcomponents > 32'sd3)
                        sad3_i = sad3_i + state_last_err_3_0_7_out;
                    if (sad3_i > 32'sd511) sad3_i = 32'sd511;
                    bp_sad_7_i = bp_sad_7_i + sad3_i;
                    sad3_i = 32'sd0;
                    if (state_numcomponents > 32'sd0)
                        sad3_i = sad3_i + state_last_err_0_1_7_out;
                    if (state_numcomponents > 32'sd1)
                        sad3_i = sad3_i + state_last_err_1_1_7_out;
                    if (state_numcomponents > 32'sd2)
                        sad3_i = sad3_i + state_last_err_2_1_7_out;
                    if (state_numcomponents > 32'sd3)
                        sad3_i = sad3_i + state_last_err_3_1_7_out;
                    if (sad3_i > 32'sd511) sad3_i = 32'sd511;
                    bp_sad_7_i = bp_sad_7_i + sad3_i;
                    sad3_i = 32'sd0;
                    if (state_numcomponents > 32'sd0)
                        sad3_i = sad3_i + state_last_err_0_2_7_out;
                    if (state_numcomponents > 32'sd1)
                        sad3_i = sad3_i + state_last_err_1_2_7_out;
                    if (state_numcomponents > 32'sd2)
                        sad3_i = sad3_i + state_last_err_2_2_7_out;
                    if (state_numcomponents > 32'sd3)
                        sad3_i = sad3_i + state_last_err_3_2_7_out;
                    if (sad3_i > 32'sd511) sad3_i = 32'sd511;
                    bp_sad_7_i = bp_sad_7_i + sad3_i;
                    bp_sad_7_i = bp_sad_7_i >>> 3;
                    bp_sad_8_i = 32'sd0;
                    sad3_i = 32'sd0;
                    if (state_numcomponents > 32'sd0)
                        sad3_i = sad3_i + state_last_err_0_0_8_out;
                    if (state_numcomponents > 32'sd1)
                        sad3_i = sad3_i + state_last_err_1_0_8_out;
                    if (state_numcomponents > 32'sd2)
                        sad3_i = sad3_i + state_last_err_2_0_8_out;
                    if (state_numcomponents > 32'sd3)
                        sad3_i = sad3_i + state_last_err_3_0_8_out;
                    if (sad3_i > 32'sd511) sad3_i = 32'sd511;
                    bp_sad_8_i = bp_sad_8_i + sad3_i;
                    sad3_i = 32'sd0;
                    if (state_numcomponents > 32'sd0)
                        sad3_i = sad3_i + state_last_err_0_1_8_out;
                    if (state_numcomponents > 32'sd1)
                        sad3_i = sad3_i + state_last_err_1_1_8_out;
                    if (state_numcomponents > 32'sd2)
                        sad3_i = sad3_i + state_last_err_2_1_8_out;
                    if (state_numcomponents > 32'sd3)
                        sad3_i = sad3_i + state_last_err_3_1_8_out;
                    if (sad3_i > 32'sd511) sad3_i = 32'sd511;
                    bp_sad_8_i = bp_sad_8_i + sad3_i;
                    sad3_i = 32'sd0;
                    if (state_numcomponents > 32'sd0)
                        sad3_i = sad3_i + state_last_err_0_2_8_out;
                    if (state_numcomponents > 32'sd1)
                        sad3_i = sad3_i + state_last_err_1_2_8_out;
                    if (state_numcomponents > 32'sd2)
                        sad3_i = sad3_i + state_last_err_2_2_8_out;
                    if (state_numcomponents > 32'sd3)
                        sad3_i = sad3_i + state_last_err_3_2_8_out;
                    if (sad3_i > 32'sd511) sad3_i = 32'sd511;
                    bp_sad_8_i = bp_sad_8_i + sad3_i;
                    bp_sad_8_i = bp_sad_8_i >>> 3;
                    bp_sad_9_i = 32'sd0;
                    sad3_i = 32'sd0;
                    if (state_numcomponents > 32'sd0)
                        sad3_i = sad3_i + state_last_err_0_0_9_out;
                    if (state_numcomponents > 32'sd1)
                        sad3_i = sad3_i + state_last_err_1_0_9_out;
                    if (state_numcomponents > 32'sd2)
                        sad3_i = sad3_i + state_last_err_2_0_9_out;
                    if (state_numcomponents > 32'sd3)
                        sad3_i = sad3_i + state_last_err_3_0_9_out;
                    if (sad3_i > 32'sd511) sad3_i = 32'sd511;
                    bp_sad_9_i = bp_sad_9_i + sad3_i;
                    sad3_i = 32'sd0;
                    if (state_numcomponents > 32'sd0)
                        sad3_i = sad3_i + state_last_err_0_1_9_out;
                    if (state_numcomponents > 32'sd1)
                        sad3_i = sad3_i + state_last_err_1_1_9_out;
                    if (state_numcomponents > 32'sd2)
                        sad3_i = sad3_i + state_last_err_2_1_9_out;
                    if (state_numcomponents > 32'sd3)
                        sad3_i = sad3_i + state_last_err_3_1_9_out;
                    if (sad3_i > 32'sd511) sad3_i = 32'sd511;
                    bp_sad_9_i = bp_sad_9_i + sad3_i;
                    sad3_i = 32'sd0;
                    if (state_numcomponents > 32'sd0)
                        sad3_i = sad3_i + state_last_err_0_2_9_out;
                    if (state_numcomponents > 32'sd1)
                        sad3_i = sad3_i + state_last_err_1_2_9_out;
                    if (state_numcomponents > 32'sd2)
                        sad3_i = sad3_i + state_last_err_2_2_9_out;
                    if (state_numcomponents > 32'sd3)
                        sad3_i = sad3_i + state_last_err_3_2_9_out;
                    if (sad3_i > 32'sd511) sad3_i = 32'sd511;
                    bp_sad_9_i = bp_sad_9_i + sad3_i;
                    bp_sad_9_i = bp_sad_9_i >>> 3;
                    bp_sad_10_i = 32'sd0;
                    sad3_i = 32'sd0;
                    if (state_numcomponents > 32'sd0)
                        sad3_i = sad3_i + state_last_err_0_0_10_out;
                    if (state_numcomponents > 32'sd1)
                        sad3_i = sad3_i + state_last_err_1_0_10_out;
                    if (state_numcomponents > 32'sd2)
                        sad3_i = sad3_i + state_last_err_2_0_10_out;
                    if (state_numcomponents > 32'sd3)
                        sad3_i = sad3_i + state_last_err_3_0_10_out;
                    if (sad3_i > 32'sd511) sad3_i = 32'sd511;
                    bp_sad_10_i = bp_sad_10_i + sad3_i;
                    sad3_i = 32'sd0;
                    if (state_numcomponents > 32'sd0)
                        sad3_i = sad3_i + state_last_err_0_1_10_out;
                    if (state_numcomponents > 32'sd1)
                        sad3_i = sad3_i + state_last_err_1_1_10_out;
                    if (state_numcomponents > 32'sd2)
                        sad3_i = sad3_i + state_last_err_2_1_10_out;
                    if (state_numcomponents > 32'sd3)
                        sad3_i = sad3_i + state_last_err_3_1_10_out;
                    if (sad3_i > 32'sd511) sad3_i = 32'sd511;
                    bp_sad_10_i = bp_sad_10_i + sad3_i;
                    sad3_i = 32'sd0;
                    if (state_numcomponents > 32'sd0)
                        sad3_i = sad3_i + state_last_err_0_2_10_out;
                    if (state_numcomponents > 32'sd1)
                        sad3_i = sad3_i + state_last_err_1_2_10_out;
                    if (state_numcomponents > 32'sd2)
                        sad3_i = sad3_i + state_last_err_2_2_10_out;
                    if (state_numcomponents > 32'sd3)
                        sad3_i = sad3_i + state_last_err_3_2_10_out;
                    if (sad3_i > 32'sd511) sad3_i = 32'sd511;
                    bp_sad_10_i = bp_sad_10_i + sad3_i;
                    bp_sad_10_i = bp_sad_10_i >>> 3;
                    bp_sad_11_i = 32'sd0;
                    sad3_i = 32'sd0;
                    if (state_numcomponents > 32'sd0)
                        sad3_i = sad3_i + state_last_err_0_0_11_out;
                    if (state_numcomponents > 32'sd1)
                        sad3_i = sad3_i + state_last_err_1_0_11_out;
                    if (state_numcomponents > 32'sd2)
                        sad3_i = sad3_i + state_last_err_2_0_11_out;
                    if (state_numcomponents > 32'sd3)
                        sad3_i = sad3_i + state_last_err_3_0_11_out;
                    if (sad3_i > 32'sd511) sad3_i = 32'sd511;
                    bp_sad_11_i = bp_sad_11_i + sad3_i;
                    sad3_i = 32'sd0;
                    if (state_numcomponents > 32'sd0)
                        sad3_i = sad3_i + state_last_err_0_1_11_out;
                    if (state_numcomponents > 32'sd1)
                        sad3_i = sad3_i + state_last_err_1_1_11_out;
                    if (state_numcomponents > 32'sd2)
                        sad3_i = sad3_i + state_last_err_2_1_11_out;
                    if (state_numcomponents > 32'sd3)
                        sad3_i = sad3_i + state_last_err_3_1_11_out;
                    if (sad3_i > 32'sd511) sad3_i = 32'sd511;
                    bp_sad_11_i = bp_sad_11_i + sad3_i;
                    sad3_i = 32'sd0;
                    if (state_numcomponents > 32'sd0)
                        sad3_i = sad3_i + state_last_err_0_2_11_out;
                    if (state_numcomponents > 32'sd1)
                        sad3_i = sad3_i + state_last_err_1_2_11_out;
                    if (state_numcomponents > 32'sd2)
                        sad3_i = sad3_i + state_last_err_2_2_11_out;
                    if (state_numcomponents > 32'sd3)
                        sad3_i = sad3_i + state_last_err_3_2_11_out;
                    if (sad3_i > 32'sd511) sad3_i = 32'sd511;
                    bp_sad_11_i = bp_sad_11_i + sad3_i;
                    bp_sad_11_i = bp_sad_11_i >>> 3;
                    bp_sad_12_i = 32'sd0;
                    sad3_i = 32'sd0;
                    if (state_numcomponents > 32'sd0)
                        sad3_i = sad3_i + state_last_err_0_0_12_out;
                    if (state_numcomponents > 32'sd1)
                        sad3_i = sad3_i + state_last_err_1_0_12_out;
                    if (state_numcomponents > 32'sd2)
                        sad3_i = sad3_i + state_last_err_2_0_12_out;
                    if (state_numcomponents > 32'sd3)
                        sad3_i = sad3_i + state_last_err_3_0_12_out;
                    if (sad3_i > 32'sd511) sad3_i = 32'sd511;
                    bp_sad_12_i = bp_sad_12_i + sad3_i;
                    sad3_i = 32'sd0;
                    if (state_numcomponents > 32'sd0)
                        sad3_i = sad3_i + state_last_err_0_1_12_out;
                    if (state_numcomponents > 32'sd1)
                        sad3_i = sad3_i + state_last_err_1_1_12_out;
                    if (state_numcomponents > 32'sd2)
                        sad3_i = sad3_i + state_last_err_2_1_12_out;
                    if (state_numcomponents > 32'sd3)
                        sad3_i = sad3_i + state_last_err_3_1_12_out;
                    if (sad3_i > 32'sd511) sad3_i = 32'sd511;
                    bp_sad_12_i = bp_sad_12_i + sad3_i;
                    sad3_i = 32'sd0;
                    if (state_numcomponents > 32'sd0)
                        sad3_i = sad3_i + state_last_err_0_2_12_out;
                    if (state_numcomponents > 32'sd1)
                        sad3_i = sad3_i + state_last_err_1_2_12_out;
                    if (state_numcomponents > 32'sd2)
                        sad3_i = sad3_i + state_last_err_2_2_12_out;
                    if (state_numcomponents > 32'sd3)
                        sad3_i = sad3_i + state_last_err_3_2_12_out;
                    if (sad3_i > 32'sd511) sad3_i = 32'sd511;
                    bp_sad_12_i = bp_sad_12_i + sad3_i;
                    bp_sad_12_i = bp_sad_12_i >>> 3;
                    min_err_i = bp_sad_0_i;
                    min_pred_i = 32'sd0;
                    if (min_err_i > bp_sad_2_i) begin
                        min_err_i = bp_sad_2_i;
                        min_pred_i = 32'sd4;
                    end
                    if (min_err_i > bp_sad_3_i) begin
                        min_err_i = bp_sad_3_i;
                        min_pred_i = 32'sd5;
                    end
                    if (min_err_i > bp_sad_4_i) begin
                        min_err_i = bp_sad_4_i;
                        min_pred_i = 32'sd6;
                    end
                    if (min_err_i > bp_sad_5_i) begin
                        min_err_i = bp_sad_5_i;
                        min_pred_i = 32'sd7;
                    end
                    if (min_err_i > bp_sad_6_i) begin
                        min_err_i = bp_sad_6_i;
                        min_pred_i = 32'sd8;
                    end
                    if (min_err_i > bp_sad_7_i) begin
                        min_err_i = bp_sad_7_i;
                        min_pred_i = 32'sd9;
                    end
                    if (min_err_i > bp_sad_8_i) begin
                        min_err_i = bp_sad_8_i;
                        min_pred_i = 32'sd10;
                    end
                    if (min_err_i > bp_sad_9_i) begin
                        min_err_i = bp_sad_9_i;
                        min_pred_i = 32'sd11;
                    end
                    if ((cfg_block_pred_enable != 0) && (hpos >= 32'sd9)) begin
                        if (min_pred_i > 32'sd2) state_bpcount_out = state_bpcount_out + 1;
                        else state_bpcount_out = 32'sd0;
                    end
                    prev_line_pred_write_enable = 1'b1;
                    if ((state_bpcount_out >= 32'sd3) && (state_lastedgecount_out < 32'sd3))
                        prev_line_pred_write_value = min_pred_i;
                    else prev_line_pred_write_value = 32'sd0;
                end
            end
        end
    end
endmodule
