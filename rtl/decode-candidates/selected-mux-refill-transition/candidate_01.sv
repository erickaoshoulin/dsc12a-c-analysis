module processgroupdec_decode_transition(
    input logic [6:0] mux_word_size,
    input logic [2:0] num_ssps,
    input logic [31:0] post_mux_num_bits,
    input logic [6:0] max_se_size_0,
    input logic [6:0] max_se_size_1,
    input logic [6:0] max_se_size_2,
    input logic [6:0] max_se_size_3,
    input logic [7:0] stream_byte_0,
    input logic [7:0] stream_byte_1,
    input logic [7:0] stream_byte_2,
    input logic [7:0] stream_byte_3,
    input logic [7:0] stream_byte_4,
    input logic [7:0] stream_byte_5,
    input logic [7:0] stream_byte_6,
    input logic [7:0] stream_byte_7,
    input logic [7:0] stream_byte_8,
    input logic [7:0] stream_byte_9,
    input logic [7:0] stream_byte_10,
    input logic [7:0] stream_byte_11,
    input logic [7:0] stream_byte_12,
    input logic [7:0] stream_byte_13,
    input logic [7:0] stream_byte_14,
    input logic [7:0] stream_byte_15,
    input logic [7:0] stream_byte_16,
    input logic [7:0] stream_byte_17,
    input logic [7:0] stream_byte_18,
    input logic [7:0] stream_byte_19,
    input logic [7:0] stream_byte_20,
    input logic [7:0] stream_byte_21,
    input logic [7:0] stream_byte_22,
    input logic [7:0] stream_byte_23,
    input logic [7:0] stream_byte_24,
    input logic [7:0] stream_byte_25,
    input logic [7:0] stream_byte_26,
    input logic [7:0] stream_byte_27,
    input logic [7:0] stream_byte_28,
    input logic [7:0] stream_byte_29,
    input logic [7:0] stream_byte_30,
    input logic [7:0] stream_byte_31,
    input logic [7:0] stream_byte_32,
    input logic [31:0] fifo_0_size,
    input logic [31:0] fifo_0_fullness,
    input logic [31:0] fifo_0_read_ptr,
    input logic [31:0] fifo_0_write_ptr,
    input logic [31:0] fifo_0_max_fullness,
    input logic [31:0] fifo_0_byte_ctr,
    input logic [31:0] fifo_1_size,
    input logic [31:0] fifo_1_fullness,
    input logic [31:0] fifo_1_read_ptr,
    input logic [31:0] fifo_1_write_ptr,
    input logic [31:0] fifo_1_max_fullness,
    input logic [31:0] fifo_1_byte_ctr,
    input logic [31:0] fifo_2_size,
    input logic [31:0] fifo_2_fullness,
    input logic [31:0] fifo_2_read_ptr,
    input logic [31:0] fifo_2_write_ptr,
    input logic [31:0] fifo_2_max_fullness,
    input logic [31:0] fifo_2_byte_ctr,
    input logic [31:0] fifo_3_size,
    input logic [31:0] fifo_3_fullness,
    input logic [31:0] fifo_3_read_ptr,
    input logic [31:0] fifo_3_write_ptr,
    input logic [31:0] fifo_3_max_fullness,
    input logic [31:0] fifo_3_byte_ctr,
    input logic [7:0] fifo_0_byte_0,
    input logic [7:0] fifo_0_byte_1,
    input logic [7:0] fifo_0_byte_2,
    input logic [7:0] fifo_0_byte_3,
    input logic [7:0] fifo_0_byte_4,
    input logic [7:0] fifo_0_byte_5,
    input logic [7:0] fifo_0_byte_6,
    input logic [7:0] fifo_0_byte_7,
    input logic [7:0] fifo_0_byte_8,
    input logic [7:0] fifo_0_byte_9,
    input logic [7:0] fifo_0_byte_10,
    input logic [7:0] fifo_0_byte_11,
    input logic [7:0] fifo_0_byte_12,
    input logic [7:0] fifo_0_byte_13,
    input logic [7:0] fifo_0_byte_14,
    input logic [7:0] fifo_0_byte_15,
    input logic [7:0] fifo_0_byte_16,
    input logic [7:0] fifo_1_byte_0,
    input logic [7:0] fifo_1_byte_1,
    input logic [7:0] fifo_1_byte_2,
    input logic [7:0] fifo_1_byte_3,
    input logic [7:0] fifo_1_byte_4,
    input logic [7:0] fifo_1_byte_5,
    input logic [7:0] fifo_1_byte_6,
    input logic [7:0] fifo_1_byte_7,
    input logic [7:0] fifo_1_byte_8,
    input logic [7:0] fifo_1_byte_9,
    input logic [7:0] fifo_1_byte_10,
    input logic [7:0] fifo_1_byte_11,
    input logic [7:0] fifo_1_byte_12,
    input logic [7:0] fifo_1_byte_13,
    input logic [7:0] fifo_1_byte_14,
    input logic [7:0] fifo_1_byte_15,
    input logic [7:0] fifo_1_byte_16,
    input logic [7:0] fifo_2_byte_0,
    input logic [7:0] fifo_2_byte_1,
    input logic [7:0] fifo_2_byte_2,
    input logic [7:0] fifo_2_byte_3,
    input logic [7:0] fifo_2_byte_4,
    input logic [7:0] fifo_2_byte_5,
    input logic [7:0] fifo_2_byte_6,
    input logic [7:0] fifo_2_byte_7,
    input logic [7:0] fifo_2_byte_8,
    input logic [7:0] fifo_2_byte_9,
    input logic [7:0] fifo_2_byte_10,
    input logic [7:0] fifo_2_byte_11,
    input logic [7:0] fifo_2_byte_12,
    input logic [7:0] fifo_2_byte_13,
    input logic [7:0] fifo_2_byte_14,
    input logic [7:0] fifo_2_byte_15,
    input logic [7:0] fifo_2_byte_16,
    input logic [7:0] fifo_3_byte_0,
    input logic [7:0] fifo_3_byte_1,
    input logic [7:0] fifo_3_byte_2,
    input logic [7:0] fifo_3_byte_3,
    input logic [7:0] fifo_3_byte_4,
    input logic [7:0] fifo_3_byte_5,
    input logic [7:0] fifo_3_byte_6,
    input logic [7:0] fifo_3_byte_7,
    input logic [7:0] fifo_3_byte_8,
    input logic [7:0] fifo_3_byte_9,
    input logic [7:0] fifo_3_byte_10,
    input logic [7:0] fifo_3_byte_11,
    input logic [7:0] fifo_3_byte_12,
    input logic [7:0] fifo_3_byte_13,
    input logic [7:0] fifo_3_byte_14,
    input logic [7:0] fifo_3_byte_15,
    input logic [7:0] fifo_3_byte_16,
    output logic domain_valid,
    output logic [31:0] post_mux_num_bits_out,
    output logic [7:0] fifo_0_byte_0_out,
    output logic [7:0] fifo_0_byte_1_out,
    output logic [7:0] fifo_0_byte_2_out,
    output logic [7:0] fifo_0_byte_3_out,
    output logic [7:0] fifo_0_byte_4_out,
    output logic [7:0] fifo_0_byte_5_out,
    output logic [7:0] fifo_0_byte_6_out,
    output logic [7:0] fifo_0_byte_7_out,
    output logic [7:0] fifo_0_byte_8_out,
    output logic [7:0] fifo_0_byte_9_out,
    output logic [7:0] fifo_0_byte_10_out,
    output logic [7:0] fifo_0_byte_11_out,
    output logic [7:0] fifo_0_byte_12_out,
    output logic [7:0] fifo_0_byte_13_out,
    output logic [7:0] fifo_0_byte_14_out,
    output logic [7:0] fifo_0_byte_15_out,
    output logic [7:0] fifo_0_byte_16_out,
    output logic [7:0] fifo_1_byte_0_out,
    output logic [7:0] fifo_1_byte_1_out,
    output logic [7:0] fifo_1_byte_2_out,
    output logic [7:0] fifo_1_byte_3_out,
    output logic [7:0] fifo_1_byte_4_out,
    output logic [7:0] fifo_1_byte_5_out,
    output logic [7:0] fifo_1_byte_6_out,
    output logic [7:0] fifo_1_byte_7_out,
    output logic [7:0] fifo_1_byte_8_out,
    output logic [7:0] fifo_1_byte_9_out,
    output logic [7:0] fifo_1_byte_10_out,
    output logic [7:0] fifo_1_byte_11_out,
    output logic [7:0] fifo_1_byte_12_out,
    output logic [7:0] fifo_1_byte_13_out,
    output logic [7:0] fifo_1_byte_14_out,
    output logic [7:0] fifo_1_byte_15_out,
    output logic [7:0] fifo_1_byte_16_out,
    output logic [7:0] fifo_2_byte_0_out,
    output logic [7:0] fifo_2_byte_1_out,
    output logic [7:0] fifo_2_byte_2_out,
    output logic [7:0] fifo_2_byte_3_out,
    output logic [7:0] fifo_2_byte_4_out,
    output logic [7:0] fifo_2_byte_5_out,
    output logic [7:0] fifo_2_byte_6_out,
    output logic [7:0] fifo_2_byte_7_out,
    output logic [7:0] fifo_2_byte_8_out,
    output logic [7:0] fifo_2_byte_9_out,
    output logic [7:0] fifo_2_byte_10_out,
    output logic [7:0] fifo_2_byte_11_out,
    output logic [7:0] fifo_2_byte_12_out,
    output logic [7:0] fifo_2_byte_13_out,
    output logic [7:0] fifo_2_byte_14_out,
    output logic [7:0] fifo_2_byte_15_out,
    output logic [7:0] fifo_2_byte_16_out,
    output logic [7:0] fifo_3_byte_0_out,
    output logic [7:0] fifo_3_byte_1_out,
    output logic [7:0] fifo_3_byte_2_out,
    output logic [7:0] fifo_3_byte_3_out,
    output logic [7:0] fifo_3_byte_4_out,
    output logic [7:0] fifo_3_byte_5_out,
    output logic [7:0] fifo_3_byte_6_out,
    output logic [7:0] fifo_3_byte_7_out,
    output logic [7:0] fifo_3_byte_8_out,
    output logic [7:0] fifo_3_byte_9_out,
    output logic [7:0] fifo_3_byte_10_out,
    output logic [7:0] fifo_3_byte_11_out,
    output logic [7:0] fifo_3_byte_12_out,
    output logic [7:0] fifo_3_byte_13_out,
    output logic [7:0] fifo_3_byte_14_out,
    output logic [7:0] fifo_3_byte_15_out,
    output logic [7:0] fifo_3_byte_16_out,
    output logic [31:0] fifo_0_size_out,
    output logic [31:0] fifo_0_fullness_out,
    output logic [31:0] fifo_0_read_ptr_out,
    output logic [31:0] fifo_0_write_ptr_out,
    output logic [31:0] fifo_0_max_fullness_out,
    output logic [31:0] fifo_0_byte_ctr_out,
    output logic [31:0] fifo_1_size_out,
    output logic [31:0] fifo_1_fullness_out,
    output logic [31:0] fifo_1_read_ptr_out,
    output logic [31:0] fifo_1_write_ptr_out,
    output logic [31:0] fifo_1_max_fullness_out,
    output logic [31:0] fifo_1_byte_ctr_out,
    output logic [31:0] fifo_2_size_out,
    output logic [31:0] fifo_2_fullness_out,
    output logic [31:0] fifo_2_read_ptr_out,
    output logic [31:0] fifo_2_write_ptr_out,
    output logic [31:0] fifo_2_max_fullness_out,
    output logic [31:0] fifo_2_byte_ctr_out,
    output logic [31:0] fifo_3_size_out,
    output logic [31:0] fifo_3_fullness_out,
    output logic [31:0] fifo_3_read_ptr_out,
    output logic [31:0] fifo_3_write_ptr_out,
    output logic [31:0] fifo_3_max_fullness_out,
    output logic [31:0] fifo_3_byte_ctr_out
);
    logic [263:0] stream_window_i;
    logic [263:0] aligned_window_i;
    logic [3:0] mux_bytes_i;
    logic [5:0] stream_index_i;
    logic [7:0] data_byte_i;
    logic [135:0] fifo_0_data_work_i;
    logic [31:0] fifo_0_fullness_work_i;
    logic [31:0] fifo_0_write_ptr_work_i;
    logic [31:0] fifo_0_max_fullness_work_i;
    logic [135:0] fifo_1_data_work_i;
    logic [31:0] fifo_1_fullness_work_i;
    logic [31:0] fifo_1_write_ptr_work_i;
    logic [31:0] fifo_1_max_fullness_work_i;
    logic [135:0] fifo_2_data_work_i;
    logic [31:0] fifo_2_fullness_work_i;
    logic [31:0] fifo_2_write_ptr_work_i;
    logic [31:0] fifo_2_max_fullness_work_i;
    logic [135:0] fifo_3_data_work_i;
    logic [31:0] fifo_3_fullness_work_i;
    logic [31:0] fifo_3_write_ptr_work_i;
    logic [31:0] fifo_3_max_fullness_work_i;

    always_comb begin
        stream_window_i = {stream_byte_0, stream_byte_1, stream_byte_2, stream_byte_3, stream_byte_4, stream_byte_5, stream_byte_6, stream_byte_7, stream_byte_8, stream_byte_9, stream_byte_10, stream_byte_11, stream_byte_12, stream_byte_13, stream_byte_14, stream_byte_15, stream_byte_16, stream_byte_17, stream_byte_18, stream_byte_19, stream_byte_20, stream_byte_21, stream_byte_22, stream_byte_23, stream_byte_24, stream_byte_25, stream_byte_26, stream_byte_27, stream_byte_28, stream_byte_29, stream_byte_30, stream_byte_31, stream_byte_32};
        aligned_window_i = stream_window_i << post_mux_num_bits[2:0];
        mux_bytes_i = 4'd0;
        if (mux_word_size == 7'd48) mux_bytes_i = 4'd6;
        else if (mux_word_size == 7'd64) mux_bytes_i = 4'd8;
        stream_index_i = 6'd0;
        data_byte_i = 8'd0;
        domain_valid = 1'b1;
        post_mux_num_bits_out = post_mux_num_bits;
        fifo_0_data_work_i = {fifo_0_byte_0, fifo_0_byte_1, fifo_0_byte_2, fifo_0_byte_3, fifo_0_byte_4, fifo_0_byte_5, fifo_0_byte_6, fifo_0_byte_7, fifo_0_byte_8, fifo_0_byte_9, fifo_0_byte_10, fifo_0_byte_11, fifo_0_byte_12, fifo_0_byte_13, fifo_0_byte_14, fifo_0_byte_15, fifo_0_byte_16};
        fifo_0_fullness_work_i = fifo_0_fullness;
        fifo_0_write_ptr_work_i = fifo_0_write_ptr;
        fifo_0_max_fullness_work_i = fifo_0_max_fullness;
        fifo_0_size_out = fifo_0_size;
        fifo_0_fullness_out = fifo_0_fullness;
        fifo_0_read_ptr_out = fifo_0_read_ptr;
        fifo_0_write_ptr_out = fifo_0_write_ptr;
        fifo_0_max_fullness_out = fifo_0_max_fullness;
        fifo_0_byte_ctr_out = fifo_0_byte_ctr;
        fifo_0_byte_0_out = 8'd0;
        fifo_0_byte_1_out = 8'd0;
        fifo_0_byte_2_out = 8'd0;
        fifo_0_byte_3_out = 8'd0;
        fifo_0_byte_4_out = 8'd0;
        fifo_0_byte_5_out = 8'd0;
        fifo_0_byte_6_out = 8'd0;
        fifo_0_byte_7_out = 8'd0;
        fifo_0_byte_8_out = 8'd0;
        fifo_0_byte_9_out = 8'd0;
        fifo_0_byte_10_out = 8'd0;
        fifo_0_byte_11_out = 8'd0;
        fifo_0_byte_12_out = 8'd0;
        fifo_0_byte_13_out = 8'd0;
        fifo_0_byte_14_out = 8'd0;
        fifo_0_byte_15_out = 8'd0;
        fifo_0_byte_16_out = 8'd0;
        fifo_1_data_work_i = {fifo_1_byte_0, fifo_1_byte_1, fifo_1_byte_2, fifo_1_byte_3, fifo_1_byte_4, fifo_1_byte_5, fifo_1_byte_6, fifo_1_byte_7, fifo_1_byte_8, fifo_1_byte_9, fifo_1_byte_10, fifo_1_byte_11, fifo_1_byte_12, fifo_1_byte_13, fifo_1_byte_14, fifo_1_byte_15, fifo_1_byte_16};
        fifo_1_fullness_work_i = fifo_1_fullness;
        fifo_1_write_ptr_work_i = fifo_1_write_ptr;
        fifo_1_max_fullness_work_i = fifo_1_max_fullness;
        fifo_1_size_out = fifo_1_size;
        fifo_1_fullness_out = fifo_1_fullness;
        fifo_1_read_ptr_out = fifo_1_read_ptr;
        fifo_1_write_ptr_out = fifo_1_write_ptr;
        fifo_1_max_fullness_out = fifo_1_max_fullness;
        fifo_1_byte_ctr_out = fifo_1_byte_ctr;
        fifo_1_byte_0_out = 8'd0;
        fifo_1_byte_1_out = 8'd0;
        fifo_1_byte_2_out = 8'd0;
        fifo_1_byte_3_out = 8'd0;
        fifo_1_byte_4_out = 8'd0;
        fifo_1_byte_5_out = 8'd0;
        fifo_1_byte_6_out = 8'd0;
        fifo_1_byte_7_out = 8'd0;
        fifo_1_byte_8_out = 8'd0;
        fifo_1_byte_9_out = 8'd0;
        fifo_1_byte_10_out = 8'd0;
        fifo_1_byte_11_out = 8'd0;
        fifo_1_byte_12_out = 8'd0;
        fifo_1_byte_13_out = 8'd0;
        fifo_1_byte_14_out = 8'd0;
        fifo_1_byte_15_out = 8'd0;
        fifo_1_byte_16_out = 8'd0;
        fifo_2_data_work_i = {fifo_2_byte_0, fifo_2_byte_1, fifo_2_byte_2, fifo_2_byte_3, fifo_2_byte_4, fifo_2_byte_5, fifo_2_byte_6, fifo_2_byte_7, fifo_2_byte_8, fifo_2_byte_9, fifo_2_byte_10, fifo_2_byte_11, fifo_2_byte_12, fifo_2_byte_13, fifo_2_byte_14, fifo_2_byte_15, fifo_2_byte_16};
        fifo_2_fullness_work_i = fifo_2_fullness;
        fifo_2_write_ptr_work_i = fifo_2_write_ptr;
        fifo_2_max_fullness_work_i = fifo_2_max_fullness;
        fifo_2_size_out = fifo_2_size;
        fifo_2_fullness_out = fifo_2_fullness;
        fifo_2_read_ptr_out = fifo_2_read_ptr;
        fifo_2_write_ptr_out = fifo_2_write_ptr;
        fifo_2_max_fullness_out = fifo_2_max_fullness;
        fifo_2_byte_ctr_out = fifo_2_byte_ctr;
        fifo_2_byte_0_out = 8'd0;
        fifo_2_byte_1_out = 8'd0;
        fifo_2_byte_2_out = 8'd0;
        fifo_2_byte_3_out = 8'd0;
        fifo_2_byte_4_out = 8'd0;
        fifo_2_byte_5_out = 8'd0;
        fifo_2_byte_6_out = 8'd0;
        fifo_2_byte_7_out = 8'd0;
        fifo_2_byte_8_out = 8'd0;
        fifo_2_byte_9_out = 8'd0;
        fifo_2_byte_10_out = 8'd0;
        fifo_2_byte_11_out = 8'd0;
        fifo_2_byte_12_out = 8'd0;
        fifo_2_byte_13_out = 8'd0;
        fifo_2_byte_14_out = 8'd0;
        fifo_2_byte_15_out = 8'd0;
        fifo_2_byte_16_out = 8'd0;
        fifo_3_data_work_i = {fifo_3_byte_0, fifo_3_byte_1, fifo_3_byte_2, fifo_3_byte_3, fifo_3_byte_4, fifo_3_byte_5, fifo_3_byte_6, fifo_3_byte_7, fifo_3_byte_8, fifo_3_byte_9, fifo_3_byte_10, fifo_3_byte_11, fifo_3_byte_12, fifo_3_byte_13, fifo_3_byte_14, fifo_3_byte_15, fifo_3_byte_16};
        fifo_3_fullness_work_i = fifo_3_fullness;
        fifo_3_write_ptr_work_i = fifo_3_write_ptr;
        fifo_3_max_fullness_work_i = fifo_3_max_fullness;
        fifo_3_size_out = fifo_3_size;
        fifo_3_fullness_out = fifo_3_fullness;
        fifo_3_read_ptr_out = fifo_3_read_ptr;
        fifo_3_write_ptr_out = fifo_3_write_ptr;
        fifo_3_max_fullness_out = fifo_3_max_fullness;
        fifo_3_byte_ctr_out = fifo_3_byte_ctr;
        fifo_3_byte_0_out = 8'd0;
        fifo_3_byte_1_out = 8'd0;
        fifo_3_byte_2_out = 8'd0;
        fifo_3_byte_3_out = 8'd0;
        fifo_3_byte_4_out = 8'd0;
        fifo_3_byte_5_out = 8'd0;
        fifo_3_byte_6_out = 8'd0;
        fifo_3_byte_7_out = 8'd0;
        fifo_3_byte_8_out = 8'd0;
        fifo_3_byte_9_out = 8'd0;
        fifo_3_byte_10_out = 8'd0;
        fifo_3_byte_11_out = 8'd0;
        fifo_3_byte_12_out = 8'd0;
        fifo_3_byte_13_out = 8'd0;
        fifo_3_byte_14_out = 8'd0;
        fifo_3_byte_15_out = 8'd0;
        fifo_3_byte_16_out = 8'd0;
        if ((mux_word_size != 7'd48) && (mux_word_size != 7'd64))
            domain_valid = 1'b0;
        if (num_ssps > 3'd4) domain_valid = 1'b0;
        if ((fifo_0_size == 0) || (fifo_0_size[2:0] != 0) || (fifo_0_size > 32'd136) || (fifo_0_write_ptr >= fifo_0_size))
            domain_valid = 1'b0;
        if ((num_ssps > 3'd0) && (fifo_0_fullness < max_se_size_0) && ({1'b0, fifo_0_fullness} + {26'd0, mux_word_size} > {1'b0, fifo_0_size}))
            domain_valid = 1'b0;
        if ((fifo_1_size == 0) || (fifo_1_size[2:0] != 0) || (fifo_1_size > 32'd136) || (fifo_1_write_ptr >= fifo_1_size))
            domain_valid = 1'b0;
        if ((num_ssps > 3'd1) && (fifo_1_fullness < max_se_size_1) && ({1'b0, fifo_1_fullness} + {26'd0, mux_word_size} > {1'b0, fifo_1_size}))
            domain_valid = 1'b0;
        if ((fifo_2_size == 0) || (fifo_2_size[2:0] != 0) || (fifo_2_size > 32'd136) || (fifo_2_write_ptr >= fifo_2_size))
            domain_valid = 1'b0;
        if ((num_ssps > 3'd2) && (fifo_2_fullness < max_se_size_2) && ({1'b0, fifo_2_fullness} + {26'd0, mux_word_size} > {1'b0, fifo_2_size}))
            domain_valid = 1'b0;
        if ((fifo_3_size == 0) || (fifo_3_size[2:0] != 0) || (fifo_3_size > 32'd136) || (fifo_3_write_ptr >= fifo_3_size))
            domain_valid = 1'b0;
        if ((num_ssps > 3'd3) && (fifo_3_fullness < max_se_size_3) && ({1'b0, fifo_3_fullness} + {26'd0, mux_word_size} > {1'b0, fifo_3_size}))
            domain_valid = 1'b0;
        if (domain_valid && (num_ssps > 3'd0) && (fifo_0_fullness < max_se_size_0)) begin
            if (mux_bytes_i > 4'd0) begin
                data_byte_i = aligned_window_i[263 - (stream_index_i * 8) -: 8];
                fifo_0_data_work_i[135 - fifo_0_write_ptr_work_i] = data_byte_i[7];
                if ((fifo_0_write_ptr_work_i + 32'd1) >= fifo_0_size)
                    fifo_0_write_ptr_work_i = 32'd0;
                else
                    fifo_0_write_ptr_work_i = fifo_0_write_ptr_work_i + 32'd1;
                fifo_0_data_work_i[135 - fifo_0_write_ptr_work_i] = data_byte_i[6];
                if ((fifo_0_write_ptr_work_i + 32'd1) >= fifo_0_size)
                    fifo_0_write_ptr_work_i = 32'd0;
                else
                    fifo_0_write_ptr_work_i = fifo_0_write_ptr_work_i + 32'd1;
                fifo_0_data_work_i[135 - fifo_0_write_ptr_work_i] = data_byte_i[5];
                if ((fifo_0_write_ptr_work_i + 32'd1) >= fifo_0_size)
                    fifo_0_write_ptr_work_i = 32'd0;
                else
                    fifo_0_write_ptr_work_i = fifo_0_write_ptr_work_i + 32'd1;
                fifo_0_data_work_i[135 - fifo_0_write_ptr_work_i] = data_byte_i[4];
                if ((fifo_0_write_ptr_work_i + 32'd1) >= fifo_0_size)
                    fifo_0_write_ptr_work_i = 32'd0;
                else
                    fifo_0_write_ptr_work_i = fifo_0_write_ptr_work_i + 32'd1;
                fifo_0_data_work_i[135 - fifo_0_write_ptr_work_i] = data_byte_i[3];
                if ((fifo_0_write_ptr_work_i + 32'd1) >= fifo_0_size)
                    fifo_0_write_ptr_work_i = 32'd0;
                else
                    fifo_0_write_ptr_work_i = fifo_0_write_ptr_work_i + 32'd1;
                fifo_0_data_work_i[135 - fifo_0_write_ptr_work_i] = data_byte_i[2];
                if ((fifo_0_write_ptr_work_i + 32'd1) >= fifo_0_size)
                    fifo_0_write_ptr_work_i = 32'd0;
                else
                    fifo_0_write_ptr_work_i = fifo_0_write_ptr_work_i + 32'd1;
                fifo_0_data_work_i[135 - fifo_0_write_ptr_work_i] = data_byte_i[1];
                if ((fifo_0_write_ptr_work_i + 32'd1) >= fifo_0_size)
                    fifo_0_write_ptr_work_i = 32'd0;
                else
                    fifo_0_write_ptr_work_i = fifo_0_write_ptr_work_i + 32'd1;
                fifo_0_data_work_i[135 - fifo_0_write_ptr_work_i] = data_byte_i[0];
                if ((fifo_0_write_ptr_work_i + 32'd1) >= fifo_0_size)
                    fifo_0_write_ptr_work_i = 32'd0;
                else
                    fifo_0_write_ptr_work_i = fifo_0_write_ptr_work_i + 32'd1;
                fifo_0_fullness_work_i = fifo_0_fullness_work_i + 32'd8;
                if (fifo_0_fullness_work_i > fifo_0_max_fullness_work_i)
                    fifo_0_max_fullness_work_i = fifo_0_fullness_work_i;
                stream_index_i = stream_index_i + 6'd1;
            end
            if (mux_bytes_i > 4'd1) begin
                data_byte_i = aligned_window_i[263 - (stream_index_i * 8) -: 8];
                fifo_0_data_work_i[135 - fifo_0_write_ptr_work_i] = data_byte_i[7];
                if ((fifo_0_write_ptr_work_i + 32'd1) >= fifo_0_size)
                    fifo_0_write_ptr_work_i = 32'd0;
                else
                    fifo_0_write_ptr_work_i = fifo_0_write_ptr_work_i + 32'd1;
                fifo_0_data_work_i[135 - fifo_0_write_ptr_work_i] = data_byte_i[6];
                if ((fifo_0_write_ptr_work_i + 32'd1) >= fifo_0_size)
                    fifo_0_write_ptr_work_i = 32'd0;
                else
                    fifo_0_write_ptr_work_i = fifo_0_write_ptr_work_i + 32'd1;
                fifo_0_data_work_i[135 - fifo_0_write_ptr_work_i] = data_byte_i[5];
                if ((fifo_0_write_ptr_work_i + 32'd1) >= fifo_0_size)
                    fifo_0_write_ptr_work_i = 32'd0;
                else
                    fifo_0_write_ptr_work_i = fifo_0_write_ptr_work_i + 32'd1;
                fifo_0_data_work_i[135 - fifo_0_write_ptr_work_i] = data_byte_i[4];
                if ((fifo_0_write_ptr_work_i + 32'd1) >= fifo_0_size)
                    fifo_0_write_ptr_work_i = 32'd0;
                else
                    fifo_0_write_ptr_work_i = fifo_0_write_ptr_work_i + 32'd1;
                fifo_0_data_work_i[135 - fifo_0_write_ptr_work_i] = data_byte_i[3];
                if ((fifo_0_write_ptr_work_i + 32'd1) >= fifo_0_size)
                    fifo_0_write_ptr_work_i = 32'd0;
                else
                    fifo_0_write_ptr_work_i = fifo_0_write_ptr_work_i + 32'd1;
                fifo_0_data_work_i[135 - fifo_0_write_ptr_work_i] = data_byte_i[2];
                if ((fifo_0_write_ptr_work_i + 32'd1) >= fifo_0_size)
                    fifo_0_write_ptr_work_i = 32'd0;
                else
                    fifo_0_write_ptr_work_i = fifo_0_write_ptr_work_i + 32'd1;
                fifo_0_data_work_i[135 - fifo_0_write_ptr_work_i] = data_byte_i[1];
                if ((fifo_0_write_ptr_work_i + 32'd1) >= fifo_0_size)
                    fifo_0_write_ptr_work_i = 32'd0;
                else
                    fifo_0_write_ptr_work_i = fifo_0_write_ptr_work_i + 32'd1;
                fifo_0_data_work_i[135 - fifo_0_write_ptr_work_i] = data_byte_i[0];
                if ((fifo_0_write_ptr_work_i + 32'd1) >= fifo_0_size)
                    fifo_0_write_ptr_work_i = 32'd0;
                else
                    fifo_0_write_ptr_work_i = fifo_0_write_ptr_work_i + 32'd1;
                fifo_0_fullness_work_i = fifo_0_fullness_work_i + 32'd8;
                if (fifo_0_fullness_work_i > fifo_0_max_fullness_work_i)
                    fifo_0_max_fullness_work_i = fifo_0_fullness_work_i;
                stream_index_i = stream_index_i + 6'd1;
            end
            if (mux_bytes_i > 4'd2) begin
                data_byte_i = aligned_window_i[263 - (stream_index_i * 8) -: 8];
                fifo_0_data_work_i[135 - fifo_0_write_ptr_work_i] = data_byte_i[7];
                if ((fifo_0_write_ptr_work_i + 32'd1) >= fifo_0_size)
                    fifo_0_write_ptr_work_i = 32'd0;
                else
                    fifo_0_write_ptr_work_i = fifo_0_write_ptr_work_i + 32'd1;
                fifo_0_data_work_i[135 - fifo_0_write_ptr_work_i] = data_byte_i[6];
                if ((fifo_0_write_ptr_work_i + 32'd1) >= fifo_0_size)
                    fifo_0_write_ptr_work_i = 32'd0;
                else
                    fifo_0_write_ptr_work_i = fifo_0_write_ptr_work_i + 32'd1;
                fifo_0_data_work_i[135 - fifo_0_write_ptr_work_i] = data_byte_i[5];
                if ((fifo_0_write_ptr_work_i + 32'd1) >= fifo_0_size)
                    fifo_0_write_ptr_work_i = 32'd0;
                else
                    fifo_0_write_ptr_work_i = fifo_0_write_ptr_work_i + 32'd1;
                fifo_0_data_work_i[135 - fifo_0_write_ptr_work_i] = data_byte_i[4];
                if ((fifo_0_write_ptr_work_i + 32'd1) >= fifo_0_size)
                    fifo_0_write_ptr_work_i = 32'd0;
                else
                    fifo_0_write_ptr_work_i = fifo_0_write_ptr_work_i + 32'd1;
                fifo_0_data_work_i[135 - fifo_0_write_ptr_work_i] = data_byte_i[3];
                if ((fifo_0_write_ptr_work_i + 32'd1) >= fifo_0_size)
                    fifo_0_write_ptr_work_i = 32'd0;
                else
                    fifo_0_write_ptr_work_i = fifo_0_write_ptr_work_i + 32'd1;
                fifo_0_data_work_i[135 - fifo_0_write_ptr_work_i] = data_byte_i[2];
                if ((fifo_0_write_ptr_work_i + 32'd1) >= fifo_0_size)
                    fifo_0_write_ptr_work_i = 32'd0;
                else
                    fifo_0_write_ptr_work_i = fifo_0_write_ptr_work_i + 32'd1;
                fifo_0_data_work_i[135 - fifo_0_write_ptr_work_i] = data_byte_i[1];
                if ((fifo_0_write_ptr_work_i + 32'd1) >= fifo_0_size)
                    fifo_0_write_ptr_work_i = 32'd0;
                else
                    fifo_0_write_ptr_work_i = fifo_0_write_ptr_work_i + 32'd1;
                fifo_0_data_work_i[135 - fifo_0_write_ptr_work_i] = data_byte_i[0];
                if ((fifo_0_write_ptr_work_i + 32'd1) >= fifo_0_size)
                    fifo_0_write_ptr_work_i = 32'd0;
                else
                    fifo_0_write_ptr_work_i = fifo_0_write_ptr_work_i + 32'd1;
                fifo_0_fullness_work_i = fifo_0_fullness_work_i + 32'd8;
                if (fifo_0_fullness_work_i > fifo_0_max_fullness_work_i)
                    fifo_0_max_fullness_work_i = fifo_0_fullness_work_i;
                stream_index_i = stream_index_i + 6'd1;
            end
            if (mux_bytes_i > 4'd3) begin
                data_byte_i = aligned_window_i[263 - (stream_index_i * 8) -: 8];
                fifo_0_data_work_i[135 - fifo_0_write_ptr_work_i] = data_byte_i[7];
                if ((fifo_0_write_ptr_work_i + 32'd1) >= fifo_0_size)
                    fifo_0_write_ptr_work_i = 32'd0;
                else
                    fifo_0_write_ptr_work_i = fifo_0_write_ptr_work_i + 32'd1;
                fifo_0_data_work_i[135 - fifo_0_write_ptr_work_i] = data_byte_i[6];
                if ((fifo_0_write_ptr_work_i + 32'd1) >= fifo_0_size)
                    fifo_0_write_ptr_work_i = 32'd0;
                else
                    fifo_0_write_ptr_work_i = fifo_0_write_ptr_work_i + 32'd1;
                fifo_0_data_work_i[135 - fifo_0_write_ptr_work_i] = data_byte_i[5];
                if ((fifo_0_write_ptr_work_i + 32'd1) >= fifo_0_size)
                    fifo_0_write_ptr_work_i = 32'd0;
                else
                    fifo_0_write_ptr_work_i = fifo_0_write_ptr_work_i + 32'd1;
                fifo_0_data_work_i[135 - fifo_0_write_ptr_work_i] = data_byte_i[4];
                if ((fifo_0_write_ptr_work_i + 32'd1) >= fifo_0_size)
                    fifo_0_write_ptr_work_i = 32'd0;
                else
                    fifo_0_write_ptr_work_i = fifo_0_write_ptr_work_i + 32'd1;
                fifo_0_data_work_i[135 - fifo_0_write_ptr_work_i] = data_byte_i[3];
                if ((fifo_0_write_ptr_work_i + 32'd1) >= fifo_0_size)
                    fifo_0_write_ptr_work_i = 32'd0;
                else
                    fifo_0_write_ptr_work_i = fifo_0_write_ptr_work_i + 32'd1;
                fifo_0_data_work_i[135 - fifo_0_write_ptr_work_i] = data_byte_i[2];
                if ((fifo_0_write_ptr_work_i + 32'd1) >= fifo_0_size)
                    fifo_0_write_ptr_work_i = 32'd0;
                else
                    fifo_0_write_ptr_work_i = fifo_0_write_ptr_work_i + 32'd1;
                fifo_0_data_work_i[135 - fifo_0_write_ptr_work_i] = data_byte_i[1];
                if ((fifo_0_write_ptr_work_i + 32'd1) >= fifo_0_size)
                    fifo_0_write_ptr_work_i = 32'd0;
                else
                    fifo_0_write_ptr_work_i = fifo_0_write_ptr_work_i + 32'd1;
                fifo_0_data_work_i[135 - fifo_0_write_ptr_work_i] = data_byte_i[0];
                if ((fifo_0_write_ptr_work_i + 32'd1) >= fifo_0_size)
                    fifo_0_write_ptr_work_i = 32'd0;
                else
                    fifo_0_write_ptr_work_i = fifo_0_write_ptr_work_i + 32'd1;
                fifo_0_fullness_work_i = fifo_0_fullness_work_i + 32'd8;
                if (fifo_0_fullness_work_i > fifo_0_max_fullness_work_i)
                    fifo_0_max_fullness_work_i = fifo_0_fullness_work_i;
                stream_index_i = stream_index_i + 6'd1;
            end
            if (mux_bytes_i > 4'd4) begin
                data_byte_i = aligned_window_i[263 - (stream_index_i * 8) -: 8];
                fifo_0_data_work_i[135 - fifo_0_write_ptr_work_i] = data_byte_i[7];
                if ((fifo_0_write_ptr_work_i + 32'd1) >= fifo_0_size)
                    fifo_0_write_ptr_work_i = 32'd0;
                else
                    fifo_0_write_ptr_work_i = fifo_0_write_ptr_work_i + 32'd1;
                fifo_0_data_work_i[135 - fifo_0_write_ptr_work_i] = data_byte_i[6];
                if ((fifo_0_write_ptr_work_i + 32'd1) >= fifo_0_size)
                    fifo_0_write_ptr_work_i = 32'd0;
                else
                    fifo_0_write_ptr_work_i = fifo_0_write_ptr_work_i + 32'd1;
                fifo_0_data_work_i[135 - fifo_0_write_ptr_work_i] = data_byte_i[5];
                if ((fifo_0_write_ptr_work_i + 32'd1) >= fifo_0_size)
                    fifo_0_write_ptr_work_i = 32'd0;
                else
                    fifo_0_write_ptr_work_i = fifo_0_write_ptr_work_i + 32'd1;
                fifo_0_data_work_i[135 - fifo_0_write_ptr_work_i] = data_byte_i[4];
                if ((fifo_0_write_ptr_work_i + 32'd1) >= fifo_0_size)
                    fifo_0_write_ptr_work_i = 32'd0;
                else
                    fifo_0_write_ptr_work_i = fifo_0_write_ptr_work_i + 32'd1;
                fifo_0_data_work_i[135 - fifo_0_write_ptr_work_i] = data_byte_i[3];
                if ((fifo_0_write_ptr_work_i + 32'd1) >= fifo_0_size)
                    fifo_0_write_ptr_work_i = 32'd0;
                else
                    fifo_0_write_ptr_work_i = fifo_0_write_ptr_work_i + 32'd1;
                fifo_0_data_work_i[135 - fifo_0_write_ptr_work_i] = data_byte_i[2];
                if ((fifo_0_write_ptr_work_i + 32'd1) >= fifo_0_size)
                    fifo_0_write_ptr_work_i = 32'd0;
                else
                    fifo_0_write_ptr_work_i = fifo_0_write_ptr_work_i + 32'd1;
                fifo_0_data_work_i[135 - fifo_0_write_ptr_work_i] = data_byte_i[1];
                if ((fifo_0_write_ptr_work_i + 32'd1) >= fifo_0_size)
                    fifo_0_write_ptr_work_i = 32'd0;
                else
                    fifo_0_write_ptr_work_i = fifo_0_write_ptr_work_i + 32'd1;
                fifo_0_data_work_i[135 - fifo_0_write_ptr_work_i] = data_byte_i[0];
                if ((fifo_0_write_ptr_work_i + 32'd1) >= fifo_0_size)
                    fifo_0_write_ptr_work_i = 32'd0;
                else
                    fifo_0_write_ptr_work_i = fifo_0_write_ptr_work_i + 32'd1;
                fifo_0_fullness_work_i = fifo_0_fullness_work_i + 32'd8;
                if (fifo_0_fullness_work_i > fifo_0_max_fullness_work_i)
                    fifo_0_max_fullness_work_i = fifo_0_fullness_work_i;
                stream_index_i = stream_index_i + 6'd1;
            end
            if (mux_bytes_i > 4'd5) begin
                data_byte_i = aligned_window_i[263 - (stream_index_i * 8) -: 8];
                fifo_0_data_work_i[135 - fifo_0_write_ptr_work_i] = data_byte_i[7];
                if ((fifo_0_write_ptr_work_i + 32'd1) >= fifo_0_size)
                    fifo_0_write_ptr_work_i = 32'd0;
                else
                    fifo_0_write_ptr_work_i = fifo_0_write_ptr_work_i + 32'd1;
                fifo_0_data_work_i[135 - fifo_0_write_ptr_work_i] = data_byte_i[6];
                if ((fifo_0_write_ptr_work_i + 32'd1) >= fifo_0_size)
                    fifo_0_write_ptr_work_i = 32'd0;
                else
                    fifo_0_write_ptr_work_i = fifo_0_write_ptr_work_i + 32'd1;
                fifo_0_data_work_i[135 - fifo_0_write_ptr_work_i] = data_byte_i[5];
                if ((fifo_0_write_ptr_work_i + 32'd1) >= fifo_0_size)
                    fifo_0_write_ptr_work_i = 32'd0;
                else
                    fifo_0_write_ptr_work_i = fifo_0_write_ptr_work_i + 32'd1;
                fifo_0_data_work_i[135 - fifo_0_write_ptr_work_i] = data_byte_i[4];
                if ((fifo_0_write_ptr_work_i + 32'd1) >= fifo_0_size)
                    fifo_0_write_ptr_work_i = 32'd0;
                else
                    fifo_0_write_ptr_work_i = fifo_0_write_ptr_work_i + 32'd1;
                fifo_0_data_work_i[135 - fifo_0_write_ptr_work_i] = data_byte_i[3];
                if ((fifo_0_write_ptr_work_i + 32'd1) >= fifo_0_size)
                    fifo_0_write_ptr_work_i = 32'd0;
                else
                    fifo_0_write_ptr_work_i = fifo_0_write_ptr_work_i + 32'd1;
                fifo_0_data_work_i[135 - fifo_0_write_ptr_work_i] = data_byte_i[2];
                if ((fifo_0_write_ptr_work_i + 32'd1) >= fifo_0_size)
                    fifo_0_write_ptr_work_i = 32'd0;
                else
                    fifo_0_write_ptr_work_i = fifo_0_write_ptr_work_i + 32'd1;
                fifo_0_data_work_i[135 - fifo_0_write_ptr_work_i] = data_byte_i[1];
                if ((fifo_0_write_ptr_work_i + 32'd1) >= fifo_0_size)
                    fifo_0_write_ptr_work_i = 32'd0;
                else
                    fifo_0_write_ptr_work_i = fifo_0_write_ptr_work_i + 32'd1;
                fifo_0_data_work_i[135 - fifo_0_write_ptr_work_i] = data_byte_i[0];
                if ((fifo_0_write_ptr_work_i + 32'd1) >= fifo_0_size)
                    fifo_0_write_ptr_work_i = 32'd0;
                else
                    fifo_0_write_ptr_work_i = fifo_0_write_ptr_work_i + 32'd1;
                fifo_0_fullness_work_i = fifo_0_fullness_work_i + 32'd8;
                if (fifo_0_fullness_work_i > fifo_0_max_fullness_work_i)
                    fifo_0_max_fullness_work_i = fifo_0_fullness_work_i;
                stream_index_i = stream_index_i + 6'd1;
            end
            if (mux_bytes_i > 4'd6) begin
                data_byte_i = aligned_window_i[263 - (stream_index_i * 8) -: 8];
                fifo_0_data_work_i[135 - fifo_0_write_ptr_work_i] = data_byte_i[7];
                if ((fifo_0_write_ptr_work_i + 32'd1) >= fifo_0_size)
                    fifo_0_write_ptr_work_i = 32'd0;
                else
                    fifo_0_write_ptr_work_i = fifo_0_write_ptr_work_i + 32'd1;
                fifo_0_data_work_i[135 - fifo_0_write_ptr_work_i] = data_byte_i[6];
                if ((fifo_0_write_ptr_work_i + 32'd1) >= fifo_0_size)
                    fifo_0_write_ptr_work_i = 32'd0;
                else
                    fifo_0_write_ptr_work_i = fifo_0_write_ptr_work_i + 32'd1;
                fifo_0_data_work_i[135 - fifo_0_write_ptr_work_i] = data_byte_i[5];
                if ((fifo_0_write_ptr_work_i + 32'd1) >= fifo_0_size)
                    fifo_0_write_ptr_work_i = 32'd0;
                else
                    fifo_0_write_ptr_work_i = fifo_0_write_ptr_work_i + 32'd1;
                fifo_0_data_work_i[135 - fifo_0_write_ptr_work_i] = data_byte_i[4];
                if ((fifo_0_write_ptr_work_i + 32'd1) >= fifo_0_size)
                    fifo_0_write_ptr_work_i = 32'd0;
                else
                    fifo_0_write_ptr_work_i = fifo_0_write_ptr_work_i + 32'd1;
                fifo_0_data_work_i[135 - fifo_0_write_ptr_work_i] = data_byte_i[3];
                if ((fifo_0_write_ptr_work_i + 32'd1) >= fifo_0_size)
                    fifo_0_write_ptr_work_i = 32'd0;
                else
                    fifo_0_write_ptr_work_i = fifo_0_write_ptr_work_i + 32'd1;
                fifo_0_data_work_i[135 - fifo_0_write_ptr_work_i] = data_byte_i[2];
                if ((fifo_0_write_ptr_work_i + 32'd1) >= fifo_0_size)
                    fifo_0_write_ptr_work_i = 32'd0;
                else
                    fifo_0_write_ptr_work_i = fifo_0_write_ptr_work_i + 32'd1;
                fifo_0_data_work_i[135 - fifo_0_write_ptr_work_i] = data_byte_i[1];
                if ((fifo_0_write_ptr_work_i + 32'd1) >= fifo_0_size)
                    fifo_0_write_ptr_work_i = 32'd0;
                else
                    fifo_0_write_ptr_work_i = fifo_0_write_ptr_work_i + 32'd1;
                fifo_0_data_work_i[135 - fifo_0_write_ptr_work_i] = data_byte_i[0];
                if ((fifo_0_write_ptr_work_i + 32'd1) >= fifo_0_size)
                    fifo_0_write_ptr_work_i = 32'd0;
                else
                    fifo_0_write_ptr_work_i = fifo_0_write_ptr_work_i + 32'd1;
                fifo_0_fullness_work_i = fifo_0_fullness_work_i + 32'd8;
                if (fifo_0_fullness_work_i > fifo_0_max_fullness_work_i)
                    fifo_0_max_fullness_work_i = fifo_0_fullness_work_i;
                stream_index_i = stream_index_i + 6'd1;
            end
            if (mux_bytes_i > 4'd7) begin
                data_byte_i = aligned_window_i[263 - (stream_index_i * 8) -: 8];
                fifo_0_data_work_i[135 - fifo_0_write_ptr_work_i] = data_byte_i[7];
                if ((fifo_0_write_ptr_work_i + 32'd1) >= fifo_0_size)
                    fifo_0_write_ptr_work_i = 32'd0;
                else
                    fifo_0_write_ptr_work_i = fifo_0_write_ptr_work_i + 32'd1;
                fifo_0_data_work_i[135 - fifo_0_write_ptr_work_i] = data_byte_i[6];
                if ((fifo_0_write_ptr_work_i + 32'd1) >= fifo_0_size)
                    fifo_0_write_ptr_work_i = 32'd0;
                else
                    fifo_0_write_ptr_work_i = fifo_0_write_ptr_work_i + 32'd1;
                fifo_0_data_work_i[135 - fifo_0_write_ptr_work_i] = data_byte_i[5];
                if ((fifo_0_write_ptr_work_i + 32'd1) >= fifo_0_size)
                    fifo_0_write_ptr_work_i = 32'd0;
                else
                    fifo_0_write_ptr_work_i = fifo_0_write_ptr_work_i + 32'd1;
                fifo_0_data_work_i[135 - fifo_0_write_ptr_work_i] = data_byte_i[4];
                if ((fifo_0_write_ptr_work_i + 32'd1) >= fifo_0_size)
                    fifo_0_write_ptr_work_i = 32'd0;
                else
                    fifo_0_write_ptr_work_i = fifo_0_write_ptr_work_i + 32'd1;
                fifo_0_data_work_i[135 - fifo_0_write_ptr_work_i] = data_byte_i[3];
                if ((fifo_0_write_ptr_work_i + 32'd1) >= fifo_0_size)
                    fifo_0_write_ptr_work_i = 32'd0;
                else
                    fifo_0_write_ptr_work_i = fifo_0_write_ptr_work_i + 32'd1;
                fifo_0_data_work_i[135 - fifo_0_write_ptr_work_i] = data_byte_i[2];
                if ((fifo_0_write_ptr_work_i + 32'd1) >= fifo_0_size)
                    fifo_0_write_ptr_work_i = 32'd0;
                else
                    fifo_0_write_ptr_work_i = fifo_0_write_ptr_work_i + 32'd1;
                fifo_0_data_work_i[135 - fifo_0_write_ptr_work_i] = data_byte_i[1];
                if ((fifo_0_write_ptr_work_i + 32'd1) >= fifo_0_size)
                    fifo_0_write_ptr_work_i = 32'd0;
                else
                    fifo_0_write_ptr_work_i = fifo_0_write_ptr_work_i + 32'd1;
                fifo_0_data_work_i[135 - fifo_0_write_ptr_work_i] = data_byte_i[0];
                if ((fifo_0_write_ptr_work_i + 32'd1) >= fifo_0_size)
                    fifo_0_write_ptr_work_i = 32'd0;
                else
                    fifo_0_write_ptr_work_i = fifo_0_write_ptr_work_i + 32'd1;
                fifo_0_fullness_work_i = fifo_0_fullness_work_i + 32'd8;
                if (fifo_0_fullness_work_i > fifo_0_max_fullness_work_i)
                    fifo_0_max_fullness_work_i = fifo_0_fullness_work_i;
                stream_index_i = stream_index_i + 6'd1;
            end
        end
        if (domain_valid && (num_ssps > 3'd1) && (fifo_1_fullness < max_se_size_1)) begin
            if (mux_bytes_i > 4'd0) begin
                data_byte_i = aligned_window_i[263 - (stream_index_i * 8) -: 8];
                fifo_1_data_work_i[135 - fifo_1_write_ptr_work_i] = data_byte_i[7];
                if ((fifo_1_write_ptr_work_i + 32'd1) >= fifo_1_size)
                    fifo_1_write_ptr_work_i = 32'd0;
                else
                    fifo_1_write_ptr_work_i = fifo_1_write_ptr_work_i + 32'd1;
                fifo_1_data_work_i[135 - fifo_1_write_ptr_work_i] = data_byte_i[6];
                if ((fifo_1_write_ptr_work_i + 32'd1) >= fifo_1_size)
                    fifo_1_write_ptr_work_i = 32'd0;
                else
                    fifo_1_write_ptr_work_i = fifo_1_write_ptr_work_i + 32'd1;
                fifo_1_data_work_i[135 - fifo_1_write_ptr_work_i] = data_byte_i[5];
                if ((fifo_1_write_ptr_work_i + 32'd1) >= fifo_1_size)
                    fifo_1_write_ptr_work_i = 32'd0;
                else
                    fifo_1_write_ptr_work_i = fifo_1_write_ptr_work_i + 32'd1;
                fifo_1_data_work_i[135 - fifo_1_write_ptr_work_i] = data_byte_i[4];
                if ((fifo_1_write_ptr_work_i + 32'd1) >= fifo_1_size)
                    fifo_1_write_ptr_work_i = 32'd0;
                else
                    fifo_1_write_ptr_work_i = fifo_1_write_ptr_work_i + 32'd1;
                fifo_1_data_work_i[135 - fifo_1_write_ptr_work_i] = data_byte_i[3];
                if ((fifo_1_write_ptr_work_i + 32'd1) >= fifo_1_size)
                    fifo_1_write_ptr_work_i = 32'd0;
                else
                    fifo_1_write_ptr_work_i = fifo_1_write_ptr_work_i + 32'd1;
                fifo_1_data_work_i[135 - fifo_1_write_ptr_work_i] = data_byte_i[2];
                if ((fifo_1_write_ptr_work_i + 32'd1) >= fifo_1_size)
                    fifo_1_write_ptr_work_i = 32'd0;
                else
                    fifo_1_write_ptr_work_i = fifo_1_write_ptr_work_i + 32'd1;
                fifo_1_data_work_i[135 - fifo_1_write_ptr_work_i] = data_byte_i[1];
                if ((fifo_1_write_ptr_work_i + 32'd1) >= fifo_1_size)
                    fifo_1_write_ptr_work_i = 32'd0;
                else
                    fifo_1_write_ptr_work_i = fifo_1_write_ptr_work_i + 32'd1;
                fifo_1_data_work_i[135 - fifo_1_write_ptr_work_i] = data_byte_i[0];
                if ((fifo_1_write_ptr_work_i + 32'd1) >= fifo_1_size)
                    fifo_1_write_ptr_work_i = 32'd0;
                else
                    fifo_1_write_ptr_work_i = fifo_1_write_ptr_work_i + 32'd1;
                fifo_1_fullness_work_i = fifo_1_fullness_work_i + 32'd8;
                if (fifo_1_fullness_work_i > fifo_1_max_fullness_work_i)
                    fifo_1_max_fullness_work_i = fifo_1_fullness_work_i;
                stream_index_i = stream_index_i + 6'd1;
            end
            if (mux_bytes_i > 4'd1) begin
                data_byte_i = aligned_window_i[263 - (stream_index_i * 8) -: 8];
                fifo_1_data_work_i[135 - fifo_1_write_ptr_work_i] = data_byte_i[7];
                if ((fifo_1_write_ptr_work_i + 32'd1) >= fifo_1_size)
                    fifo_1_write_ptr_work_i = 32'd0;
                else
                    fifo_1_write_ptr_work_i = fifo_1_write_ptr_work_i + 32'd1;
                fifo_1_data_work_i[135 - fifo_1_write_ptr_work_i] = data_byte_i[6];
                if ((fifo_1_write_ptr_work_i + 32'd1) >= fifo_1_size)
                    fifo_1_write_ptr_work_i = 32'd0;
                else
                    fifo_1_write_ptr_work_i = fifo_1_write_ptr_work_i + 32'd1;
                fifo_1_data_work_i[135 - fifo_1_write_ptr_work_i] = data_byte_i[5];
                if ((fifo_1_write_ptr_work_i + 32'd1) >= fifo_1_size)
                    fifo_1_write_ptr_work_i = 32'd0;
                else
                    fifo_1_write_ptr_work_i = fifo_1_write_ptr_work_i + 32'd1;
                fifo_1_data_work_i[135 - fifo_1_write_ptr_work_i] = data_byte_i[4];
                if ((fifo_1_write_ptr_work_i + 32'd1) >= fifo_1_size)
                    fifo_1_write_ptr_work_i = 32'd0;
                else
                    fifo_1_write_ptr_work_i = fifo_1_write_ptr_work_i + 32'd1;
                fifo_1_data_work_i[135 - fifo_1_write_ptr_work_i] = data_byte_i[3];
                if ((fifo_1_write_ptr_work_i + 32'd1) >= fifo_1_size)
                    fifo_1_write_ptr_work_i = 32'd0;
                else
                    fifo_1_write_ptr_work_i = fifo_1_write_ptr_work_i + 32'd1;
                fifo_1_data_work_i[135 - fifo_1_write_ptr_work_i] = data_byte_i[2];
                if ((fifo_1_write_ptr_work_i + 32'd1) >= fifo_1_size)
                    fifo_1_write_ptr_work_i = 32'd0;
                else
                    fifo_1_write_ptr_work_i = fifo_1_write_ptr_work_i + 32'd1;
                fifo_1_data_work_i[135 - fifo_1_write_ptr_work_i] = data_byte_i[1];
                if ((fifo_1_write_ptr_work_i + 32'd1) >= fifo_1_size)
                    fifo_1_write_ptr_work_i = 32'd0;
                else
                    fifo_1_write_ptr_work_i = fifo_1_write_ptr_work_i + 32'd1;
                fifo_1_data_work_i[135 - fifo_1_write_ptr_work_i] = data_byte_i[0];
                if ((fifo_1_write_ptr_work_i + 32'd1) >= fifo_1_size)
                    fifo_1_write_ptr_work_i = 32'd0;
                else
                    fifo_1_write_ptr_work_i = fifo_1_write_ptr_work_i + 32'd1;
                fifo_1_fullness_work_i = fifo_1_fullness_work_i + 32'd8;
                if (fifo_1_fullness_work_i > fifo_1_max_fullness_work_i)
                    fifo_1_max_fullness_work_i = fifo_1_fullness_work_i;
                stream_index_i = stream_index_i + 6'd1;
            end
            if (mux_bytes_i > 4'd2) begin
                data_byte_i = aligned_window_i[263 - (stream_index_i * 8) -: 8];
                fifo_1_data_work_i[135 - fifo_1_write_ptr_work_i] = data_byte_i[7];
                if ((fifo_1_write_ptr_work_i + 32'd1) >= fifo_1_size)
                    fifo_1_write_ptr_work_i = 32'd0;
                else
                    fifo_1_write_ptr_work_i = fifo_1_write_ptr_work_i + 32'd1;
                fifo_1_data_work_i[135 - fifo_1_write_ptr_work_i] = data_byte_i[6];
                if ((fifo_1_write_ptr_work_i + 32'd1) >= fifo_1_size)
                    fifo_1_write_ptr_work_i = 32'd0;
                else
                    fifo_1_write_ptr_work_i = fifo_1_write_ptr_work_i + 32'd1;
                fifo_1_data_work_i[135 - fifo_1_write_ptr_work_i] = data_byte_i[5];
                if ((fifo_1_write_ptr_work_i + 32'd1) >= fifo_1_size)
                    fifo_1_write_ptr_work_i = 32'd0;
                else
                    fifo_1_write_ptr_work_i = fifo_1_write_ptr_work_i + 32'd1;
                fifo_1_data_work_i[135 - fifo_1_write_ptr_work_i] = data_byte_i[4];
                if ((fifo_1_write_ptr_work_i + 32'd1) >= fifo_1_size)
                    fifo_1_write_ptr_work_i = 32'd0;
                else
                    fifo_1_write_ptr_work_i = fifo_1_write_ptr_work_i + 32'd1;
                fifo_1_data_work_i[135 - fifo_1_write_ptr_work_i] = data_byte_i[3];
                if ((fifo_1_write_ptr_work_i + 32'd1) >= fifo_1_size)
                    fifo_1_write_ptr_work_i = 32'd0;
                else
                    fifo_1_write_ptr_work_i = fifo_1_write_ptr_work_i + 32'd1;
                fifo_1_data_work_i[135 - fifo_1_write_ptr_work_i] = data_byte_i[2];
                if ((fifo_1_write_ptr_work_i + 32'd1) >= fifo_1_size)
                    fifo_1_write_ptr_work_i = 32'd0;
                else
                    fifo_1_write_ptr_work_i = fifo_1_write_ptr_work_i + 32'd1;
                fifo_1_data_work_i[135 - fifo_1_write_ptr_work_i] = data_byte_i[1];
                if ((fifo_1_write_ptr_work_i + 32'd1) >= fifo_1_size)
                    fifo_1_write_ptr_work_i = 32'd0;
                else
                    fifo_1_write_ptr_work_i = fifo_1_write_ptr_work_i + 32'd1;
                fifo_1_data_work_i[135 - fifo_1_write_ptr_work_i] = data_byte_i[0];
                if ((fifo_1_write_ptr_work_i + 32'd1) >= fifo_1_size)
                    fifo_1_write_ptr_work_i = 32'd0;
                else
                    fifo_1_write_ptr_work_i = fifo_1_write_ptr_work_i + 32'd1;
                fifo_1_fullness_work_i = fifo_1_fullness_work_i + 32'd8;
                if (fifo_1_fullness_work_i > fifo_1_max_fullness_work_i)
                    fifo_1_max_fullness_work_i = fifo_1_fullness_work_i;
                stream_index_i = stream_index_i + 6'd1;
            end
            if (mux_bytes_i > 4'd3) begin
                data_byte_i = aligned_window_i[263 - (stream_index_i * 8) -: 8];
                fifo_1_data_work_i[135 - fifo_1_write_ptr_work_i] = data_byte_i[7];
                if ((fifo_1_write_ptr_work_i + 32'd1) >= fifo_1_size)
                    fifo_1_write_ptr_work_i = 32'd0;
                else
                    fifo_1_write_ptr_work_i = fifo_1_write_ptr_work_i + 32'd1;
                fifo_1_data_work_i[135 - fifo_1_write_ptr_work_i] = data_byte_i[6];
                if ((fifo_1_write_ptr_work_i + 32'd1) >= fifo_1_size)
                    fifo_1_write_ptr_work_i = 32'd0;
                else
                    fifo_1_write_ptr_work_i = fifo_1_write_ptr_work_i + 32'd1;
                fifo_1_data_work_i[135 - fifo_1_write_ptr_work_i] = data_byte_i[5];
                if ((fifo_1_write_ptr_work_i + 32'd1) >= fifo_1_size)
                    fifo_1_write_ptr_work_i = 32'd0;
                else
                    fifo_1_write_ptr_work_i = fifo_1_write_ptr_work_i + 32'd1;
                fifo_1_data_work_i[135 - fifo_1_write_ptr_work_i] = data_byte_i[4];
                if ((fifo_1_write_ptr_work_i + 32'd1) >= fifo_1_size)
                    fifo_1_write_ptr_work_i = 32'd0;
                else
                    fifo_1_write_ptr_work_i = fifo_1_write_ptr_work_i + 32'd1;
                fifo_1_data_work_i[135 - fifo_1_write_ptr_work_i] = data_byte_i[3];
                if ((fifo_1_write_ptr_work_i + 32'd1) >= fifo_1_size)
                    fifo_1_write_ptr_work_i = 32'd0;
                else
                    fifo_1_write_ptr_work_i = fifo_1_write_ptr_work_i + 32'd1;
                fifo_1_data_work_i[135 - fifo_1_write_ptr_work_i] = data_byte_i[2];
                if ((fifo_1_write_ptr_work_i + 32'd1) >= fifo_1_size)
                    fifo_1_write_ptr_work_i = 32'd0;
                else
                    fifo_1_write_ptr_work_i = fifo_1_write_ptr_work_i + 32'd1;
                fifo_1_data_work_i[135 - fifo_1_write_ptr_work_i] = data_byte_i[1];
                if ((fifo_1_write_ptr_work_i + 32'd1) >= fifo_1_size)
                    fifo_1_write_ptr_work_i = 32'd0;
                else
                    fifo_1_write_ptr_work_i = fifo_1_write_ptr_work_i + 32'd1;
                fifo_1_data_work_i[135 - fifo_1_write_ptr_work_i] = data_byte_i[0];
                if ((fifo_1_write_ptr_work_i + 32'd1) >= fifo_1_size)
                    fifo_1_write_ptr_work_i = 32'd0;
                else
                    fifo_1_write_ptr_work_i = fifo_1_write_ptr_work_i + 32'd1;
                fifo_1_fullness_work_i = fifo_1_fullness_work_i + 32'd8;
                if (fifo_1_fullness_work_i > fifo_1_max_fullness_work_i)
                    fifo_1_max_fullness_work_i = fifo_1_fullness_work_i;
                stream_index_i = stream_index_i + 6'd1;
            end
            if (mux_bytes_i > 4'd4) begin
                data_byte_i = aligned_window_i[263 - (stream_index_i * 8) -: 8];
                fifo_1_data_work_i[135 - fifo_1_write_ptr_work_i] = data_byte_i[7];
                if ((fifo_1_write_ptr_work_i + 32'd1) >= fifo_1_size)
                    fifo_1_write_ptr_work_i = 32'd0;
                else
                    fifo_1_write_ptr_work_i = fifo_1_write_ptr_work_i + 32'd1;
                fifo_1_data_work_i[135 - fifo_1_write_ptr_work_i] = data_byte_i[6];
                if ((fifo_1_write_ptr_work_i + 32'd1) >= fifo_1_size)
                    fifo_1_write_ptr_work_i = 32'd0;
                else
                    fifo_1_write_ptr_work_i = fifo_1_write_ptr_work_i + 32'd1;
                fifo_1_data_work_i[135 - fifo_1_write_ptr_work_i] = data_byte_i[5];
                if ((fifo_1_write_ptr_work_i + 32'd1) >= fifo_1_size)
                    fifo_1_write_ptr_work_i = 32'd0;
                else
                    fifo_1_write_ptr_work_i = fifo_1_write_ptr_work_i + 32'd1;
                fifo_1_data_work_i[135 - fifo_1_write_ptr_work_i] = data_byte_i[4];
                if ((fifo_1_write_ptr_work_i + 32'd1) >= fifo_1_size)
                    fifo_1_write_ptr_work_i = 32'd0;
                else
                    fifo_1_write_ptr_work_i = fifo_1_write_ptr_work_i + 32'd1;
                fifo_1_data_work_i[135 - fifo_1_write_ptr_work_i] = data_byte_i[3];
                if ((fifo_1_write_ptr_work_i + 32'd1) >= fifo_1_size)
                    fifo_1_write_ptr_work_i = 32'd0;
                else
                    fifo_1_write_ptr_work_i = fifo_1_write_ptr_work_i + 32'd1;
                fifo_1_data_work_i[135 - fifo_1_write_ptr_work_i] = data_byte_i[2];
                if ((fifo_1_write_ptr_work_i + 32'd1) >= fifo_1_size)
                    fifo_1_write_ptr_work_i = 32'd0;
                else
                    fifo_1_write_ptr_work_i = fifo_1_write_ptr_work_i + 32'd1;
                fifo_1_data_work_i[135 - fifo_1_write_ptr_work_i] = data_byte_i[1];
                if ((fifo_1_write_ptr_work_i + 32'd1) >= fifo_1_size)
                    fifo_1_write_ptr_work_i = 32'd0;
                else
                    fifo_1_write_ptr_work_i = fifo_1_write_ptr_work_i + 32'd1;
                fifo_1_data_work_i[135 - fifo_1_write_ptr_work_i] = data_byte_i[0];
                if ((fifo_1_write_ptr_work_i + 32'd1) >= fifo_1_size)
                    fifo_1_write_ptr_work_i = 32'd0;
                else
                    fifo_1_write_ptr_work_i = fifo_1_write_ptr_work_i + 32'd1;
                fifo_1_fullness_work_i = fifo_1_fullness_work_i + 32'd8;
                if (fifo_1_fullness_work_i > fifo_1_max_fullness_work_i)
                    fifo_1_max_fullness_work_i = fifo_1_fullness_work_i;
                stream_index_i = stream_index_i + 6'd1;
            end
            if (mux_bytes_i > 4'd5) begin
                data_byte_i = aligned_window_i[263 - (stream_index_i * 8) -: 8];
                fifo_1_data_work_i[135 - fifo_1_write_ptr_work_i] = data_byte_i[7];
                if ((fifo_1_write_ptr_work_i + 32'd1) >= fifo_1_size)
                    fifo_1_write_ptr_work_i = 32'd0;
                else
                    fifo_1_write_ptr_work_i = fifo_1_write_ptr_work_i + 32'd1;
                fifo_1_data_work_i[135 - fifo_1_write_ptr_work_i] = data_byte_i[6];
                if ((fifo_1_write_ptr_work_i + 32'd1) >= fifo_1_size)
                    fifo_1_write_ptr_work_i = 32'd0;
                else
                    fifo_1_write_ptr_work_i = fifo_1_write_ptr_work_i + 32'd1;
                fifo_1_data_work_i[135 - fifo_1_write_ptr_work_i] = data_byte_i[5];
                if ((fifo_1_write_ptr_work_i + 32'd1) >= fifo_1_size)
                    fifo_1_write_ptr_work_i = 32'd0;
                else
                    fifo_1_write_ptr_work_i = fifo_1_write_ptr_work_i + 32'd1;
                fifo_1_data_work_i[135 - fifo_1_write_ptr_work_i] = data_byte_i[4];
                if ((fifo_1_write_ptr_work_i + 32'd1) >= fifo_1_size)
                    fifo_1_write_ptr_work_i = 32'd0;
                else
                    fifo_1_write_ptr_work_i = fifo_1_write_ptr_work_i + 32'd1;
                fifo_1_data_work_i[135 - fifo_1_write_ptr_work_i] = data_byte_i[3];
                if ((fifo_1_write_ptr_work_i + 32'd1) >= fifo_1_size)
                    fifo_1_write_ptr_work_i = 32'd0;
                else
                    fifo_1_write_ptr_work_i = fifo_1_write_ptr_work_i + 32'd1;
                fifo_1_data_work_i[135 - fifo_1_write_ptr_work_i] = data_byte_i[2];
                if ((fifo_1_write_ptr_work_i + 32'd1) >= fifo_1_size)
                    fifo_1_write_ptr_work_i = 32'd0;
                else
                    fifo_1_write_ptr_work_i = fifo_1_write_ptr_work_i + 32'd1;
                fifo_1_data_work_i[135 - fifo_1_write_ptr_work_i] = data_byte_i[1];
                if ((fifo_1_write_ptr_work_i + 32'd1) >= fifo_1_size)
                    fifo_1_write_ptr_work_i = 32'd0;
                else
                    fifo_1_write_ptr_work_i = fifo_1_write_ptr_work_i + 32'd1;
                fifo_1_data_work_i[135 - fifo_1_write_ptr_work_i] = data_byte_i[0];
                if ((fifo_1_write_ptr_work_i + 32'd1) >= fifo_1_size)
                    fifo_1_write_ptr_work_i = 32'd0;
                else
                    fifo_1_write_ptr_work_i = fifo_1_write_ptr_work_i + 32'd1;
                fifo_1_fullness_work_i = fifo_1_fullness_work_i + 32'd8;
                if (fifo_1_fullness_work_i > fifo_1_max_fullness_work_i)
                    fifo_1_max_fullness_work_i = fifo_1_fullness_work_i;
                stream_index_i = stream_index_i + 6'd1;
            end
            if (mux_bytes_i > 4'd6) begin
                data_byte_i = aligned_window_i[263 - (stream_index_i * 8) -: 8];
                fifo_1_data_work_i[135 - fifo_1_write_ptr_work_i] = data_byte_i[7];
                if ((fifo_1_write_ptr_work_i + 32'd1) >= fifo_1_size)
                    fifo_1_write_ptr_work_i = 32'd0;
                else
                    fifo_1_write_ptr_work_i = fifo_1_write_ptr_work_i + 32'd1;
                fifo_1_data_work_i[135 - fifo_1_write_ptr_work_i] = data_byte_i[6];
                if ((fifo_1_write_ptr_work_i + 32'd1) >= fifo_1_size)
                    fifo_1_write_ptr_work_i = 32'd0;
                else
                    fifo_1_write_ptr_work_i = fifo_1_write_ptr_work_i + 32'd1;
                fifo_1_data_work_i[135 - fifo_1_write_ptr_work_i] = data_byte_i[5];
                if ((fifo_1_write_ptr_work_i + 32'd1) >= fifo_1_size)
                    fifo_1_write_ptr_work_i = 32'd0;
                else
                    fifo_1_write_ptr_work_i = fifo_1_write_ptr_work_i + 32'd1;
                fifo_1_data_work_i[135 - fifo_1_write_ptr_work_i] = data_byte_i[4];
                if ((fifo_1_write_ptr_work_i + 32'd1) >= fifo_1_size)
                    fifo_1_write_ptr_work_i = 32'd0;
                else
                    fifo_1_write_ptr_work_i = fifo_1_write_ptr_work_i + 32'd1;
                fifo_1_data_work_i[135 - fifo_1_write_ptr_work_i] = data_byte_i[3];
                if ((fifo_1_write_ptr_work_i + 32'd1) >= fifo_1_size)
                    fifo_1_write_ptr_work_i = 32'd0;
                else
                    fifo_1_write_ptr_work_i = fifo_1_write_ptr_work_i + 32'd1;
                fifo_1_data_work_i[135 - fifo_1_write_ptr_work_i] = data_byte_i[2];
                if ((fifo_1_write_ptr_work_i + 32'd1) >= fifo_1_size)
                    fifo_1_write_ptr_work_i = 32'd0;
                else
                    fifo_1_write_ptr_work_i = fifo_1_write_ptr_work_i + 32'd1;
                fifo_1_data_work_i[135 - fifo_1_write_ptr_work_i] = data_byte_i[1];
                if ((fifo_1_write_ptr_work_i + 32'd1) >= fifo_1_size)
                    fifo_1_write_ptr_work_i = 32'd0;
                else
                    fifo_1_write_ptr_work_i = fifo_1_write_ptr_work_i + 32'd1;
                fifo_1_data_work_i[135 - fifo_1_write_ptr_work_i] = data_byte_i[0];
                if ((fifo_1_write_ptr_work_i + 32'd1) >= fifo_1_size)
                    fifo_1_write_ptr_work_i = 32'd0;
                else
                    fifo_1_write_ptr_work_i = fifo_1_write_ptr_work_i + 32'd1;
                fifo_1_fullness_work_i = fifo_1_fullness_work_i + 32'd8;
                if (fifo_1_fullness_work_i > fifo_1_max_fullness_work_i)
                    fifo_1_max_fullness_work_i = fifo_1_fullness_work_i;
                stream_index_i = stream_index_i + 6'd1;
            end
            if (mux_bytes_i > 4'd7) begin
                data_byte_i = aligned_window_i[263 - (stream_index_i * 8) -: 8];
                fifo_1_data_work_i[135 - fifo_1_write_ptr_work_i] = data_byte_i[7];
                if ((fifo_1_write_ptr_work_i + 32'd1) >= fifo_1_size)
                    fifo_1_write_ptr_work_i = 32'd0;
                else
                    fifo_1_write_ptr_work_i = fifo_1_write_ptr_work_i + 32'd1;
                fifo_1_data_work_i[135 - fifo_1_write_ptr_work_i] = data_byte_i[6];
                if ((fifo_1_write_ptr_work_i + 32'd1) >= fifo_1_size)
                    fifo_1_write_ptr_work_i = 32'd0;
                else
                    fifo_1_write_ptr_work_i = fifo_1_write_ptr_work_i + 32'd1;
                fifo_1_data_work_i[135 - fifo_1_write_ptr_work_i] = data_byte_i[5];
                if ((fifo_1_write_ptr_work_i + 32'd1) >= fifo_1_size)
                    fifo_1_write_ptr_work_i = 32'd0;
                else
                    fifo_1_write_ptr_work_i = fifo_1_write_ptr_work_i + 32'd1;
                fifo_1_data_work_i[135 - fifo_1_write_ptr_work_i] = data_byte_i[4];
                if ((fifo_1_write_ptr_work_i + 32'd1) >= fifo_1_size)
                    fifo_1_write_ptr_work_i = 32'd0;
                else
                    fifo_1_write_ptr_work_i = fifo_1_write_ptr_work_i + 32'd1;
                fifo_1_data_work_i[135 - fifo_1_write_ptr_work_i] = data_byte_i[3];
                if ((fifo_1_write_ptr_work_i + 32'd1) >= fifo_1_size)
                    fifo_1_write_ptr_work_i = 32'd0;
                else
                    fifo_1_write_ptr_work_i = fifo_1_write_ptr_work_i + 32'd1;
                fifo_1_data_work_i[135 - fifo_1_write_ptr_work_i] = data_byte_i[2];
                if ((fifo_1_write_ptr_work_i + 32'd1) >= fifo_1_size)
                    fifo_1_write_ptr_work_i = 32'd0;
                else
                    fifo_1_write_ptr_work_i = fifo_1_write_ptr_work_i + 32'd1;
                fifo_1_data_work_i[135 - fifo_1_write_ptr_work_i] = data_byte_i[1];
                if ((fifo_1_write_ptr_work_i + 32'd1) >= fifo_1_size)
                    fifo_1_write_ptr_work_i = 32'd0;
                else
                    fifo_1_write_ptr_work_i = fifo_1_write_ptr_work_i + 32'd1;
                fifo_1_data_work_i[135 - fifo_1_write_ptr_work_i] = data_byte_i[0];
                if ((fifo_1_write_ptr_work_i + 32'd1) >= fifo_1_size)
                    fifo_1_write_ptr_work_i = 32'd0;
                else
                    fifo_1_write_ptr_work_i = fifo_1_write_ptr_work_i + 32'd1;
                fifo_1_fullness_work_i = fifo_1_fullness_work_i + 32'd8;
                if (fifo_1_fullness_work_i > fifo_1_max_fullness_work_i)
                    fifo_1_max_fullness_work_i = fifo_1_fullness_work_i;
                stream_index_i = stream_index_i + 6'd1;
            end
        end
        if (domain_valid && (num_ssps > 3'd2) && (fifo_2_fullness < max_se_size_2)) begin
            if (mux_bytes_i > 4'd0) begin
                data_byte_i = aligned_window_i[263 - (stream_index_i * 8) -: 8];
                fifo_2_data_work_i[135 - fifo_2_write_ptr_work_i] = data_byte_i[7];
                if ((fifo_2_write_ptr_work_i + 32'd1) >= fifo_2_size)
                    fifo_2_write_ptr_work_i = 32'd0;
                else
                    fifo_2_write_ptr_work_i = fifo_2_write_ptr_work_i + 32'd1;
                fifo_2_data_work_i[135 - fifo_2_write_ptr_work_i] = data_byte_i[6];
                if ((fifo_2_write_ptr_work_i + 32'd1) >= fifo_2_size)
                    fifo_2_write_ptr_work_i = 32'd0;
                else
                    fifo_2_write_ptr_work_i = fifo_2_write_ptr_work_i + 32'd1;
                fifo_2_data_work_i[135 - fifo_2_write_ptr_work_i] = data_byte_i[5];
                if ((fifo_2_write_ptr_work_i + 32'd1) >= fifo_2_size)
                    fifo_2_write_ptr_work_i = 32'd0;
                else
                    fifo_2_write_ptr_work_i = fifo_2_write_ptr_work_i + 32'd1;
                fifo_2_data_work_i[135 - fifo_2_write_ptr_work_i] = data_byte_i[4];
                if ((fifo_2_write_ptr_work_i + 32'd1) >= fifo_2_size)
                    fifo_2_write_ptr_work_i = 32'd0;
                else
                    fifo_2_write_ptr_work_i = fifo_2_write_ptr_work_i + 32'd1;
                fifo_2_data_work_i[135 - fifo_2_write_ptr_work_i] = data_byte_i[3];
                if ((fifo_2_write_ptr_work_i + 32'd1) >= fifo_2_size)
                    fifo_2_write_ptr_work_i = 32'd0;
                else
                    fifo_2_write_ptr_work_i = fifo_2_write_ptr_work_i + 32'd1;
                fifo_2_data_work_i[135 - fifo_2_write_ptr_work_i] = data_byte_i[2];
                if ((fifo_2_write_ptr_work_i + 32'd1) >= fifo_2_size)
                    fifo_2_write_ptr_work_i = 32'd0;
                else
                    fifo_2_write_ptr_work_i = fifo_2_write_ptr_work_i + 32'd1;
                fifo_2_data_work_i[135 - fifo_2_write_ptr_work_i] = data_byte_i[1];
                if ((fifo_2_write_ptr_work_i + 32'd1) >= fifo_2_size)
                    fifo_2_write_ptr_work_i = 32'd0;
                else
                    fifo_2_write_ptr_work_i = fifo_2_write_ptr_work_i + 32'd1;
                fifo_2_data_work_i[135 - fifo_2_write_ptr_work_i] = data_byte_i[0];
                if ((fifo_2_write_ptr_work_i + 32'd1) >= fifo_2_size)
                    fifo_2_write_ptr_work_i = 32'd0;
                else
                    fifo_2_write_ptr_work_i = fifo_2_write_ptr_work_i + 32'd1;
                fifo_2_fullness_work_i = fifo_2_fullness_work_i + 32'd8;
                if (fifo_2_fullness_work_i > fifo_2_max_fullness_work_i)
                    fifo_2_max_fullness_work_i = fifo_2_fullness_work_i;
                stream_index_i = stream_index_i + 6'd1;
            end
            if (mux_bytes_i > 4'd1) begin
                data_byte_i = aligned_window_i[263 - (stream_index_i * 8) -: 8];
                fifo_2_data_work_i[135 - fifo_2_write_ptr_work_i] = data_byte_i[7];
                if ((fifo_2_write_ptr_work_i + 32'd1) >= fifo_2_size)
                    fifo_2_write_ptr_work_i = 32'd0;
                else
                    fifo_2_write_ptr_work_i = fifo_2_write_ptr_work_i + 32'd1;
                fifo_2_data_work_i[135 - fifo_2_write_ptr_work_i] = data_byte_i[6];
                if ((fifo_2_write_ptr_work_i + 32'd1) >= fifo_2_size)
                    fifo_2_write_ptr_work_i = 32'd0;
                else
                    fifo_2_write_ptr_work_i = fifo_2_write_ptr_work_i + 32'd1;
                fifo_2_data_work_i[135 - fifo_2_write_ptr_work_i] = data_byte_i[5];
                if ((fifo_2_write_ptr_work_i + 32'd1) >= fifo_2_size)
                    fifo_2_write_ptr_work_i = 32'd0;
                else
                    fifo_2_write_ptr_work_i = fifo_2_write_ptr_work_i + 32'd1;
                fifo_2_data_work_i[135 - fifo_2_write_ptr_work_i] = data_byte_i[4];
                if ((fifo_2_write_ptr_work_i + 32'd1) >= fifo_2_size)
                    fifo_2_write_ptr_work_i = 32'd0;
                else
                    fifo_2_write_ptr_work_i = fifo_2_write_ptr_work_i + 32'd1;
                fifo_2_data_work_i[135 - fifo_2_write_ptr_work_i] = data_byte_i[3];
                if ((fifo_2_write_ptr_work_i + 32'd1) >= fifo_2_size)
                    fifo_2_write_ptr_work_i = 32'd0;
                else
                    fifo_2_write_ptr_work_i = fifo_2_write_ptr_work_i + 32'd1;
                fifo_2_data_work_i[135 - fifo_2_write_ptr_work_i] = data_byte_i[2];
                if ((fifo_2_write_ptr_work_i + 32'd1) >= fifo_2_size)
                    fifo_2_write_ptr_work_i = 32'd0;
                else
                    fifo_2_write_ptr_work_i = fifo_2_write_ptr_work_i + 32'd1;
                fifo_2_data_work_i[135 - fifo_2_write_ptr_work_i] = data_byte_i[1];
                if ((fifo_2_write_ptr_work_i + 32'd1) >= fifo_2_size)
                    fifo_2_write_ptr_work_i = 32'd0;
                else
                    fifo_2_write_ptr_work_i = fifo_2_write_ptr_work_i + 32'd1;
                fifo_2_data_work_i[135 - fifo_2_write_ptr_work_i] = data_byte_i[0];
                if ((fifo_2_write_ptr_work_i + 32'd1) >= fifo_2_size)
                    fifo_2_write_ptr_work_i = 32'd0;
                else
                    fifo_2_write_ptr_work_i = fifo_2_write_ptr_work_i + 32'd1;
                fifo_2_fullness_work_i = fifo_2_fullness_work_i + 32'd8;
                if (fifo_2_fullness_work_i > fifo_2_max_fullness_work_i)
                    fifo_2_max_fullness_work_i = fifo_2_fullness_work_i;
                stream_index_i = stream_index_i + 6'd1;
            end
            if (mux_bytes_i > 4'd2) begin
                data_byte_i = aligned_window_i[263 - (stream_index_i * 8) -: 8];
                fifo_2_data_work_i[135 - fifo_2_write_ptr_work_i] = data_byte_i[7];
                if ((fifo_2_write_ptr_work_i + 32'd1) >= fifo_2_size)
                    fifo_2_write_ptr_work_i = 32'd0;
                else
                    fifo_2_write_ptr_work_i = fifo_2_write_ptr_work_i + 32'd1;
                fifo_2_data_work_i[135 - fifo_2_write_ptr_work_i] = data_byte_i[6];
                if ((fifo_2_write_ptr_work_i + 32'd1) >= fifo_2_size)
                    fifo_2_write_ptr_work_i = 32'd0;
                else
                    fifo_2_write_ptr_work_i = fifo_2_write_ptr_work_i + 32'd1;
                fifo_2_data_work_i[135 - fifo_2_write_ptr_work_i] = data_byte_i[5];
                if ((fifo_2_write_ptr_work_i + 32'd1) >= fifo_2_size)
                    fifo_2_write_ptr_work_i = 32'd0;
                else
                    fifo_2_write_ptr_work_i = fifo_2_write_ptr_work_i + 32'd1;
                fifo_2_data_work_i[135 - fifo_2_write_ptr_work_i] = data_byte_i[4];
                if ((fifo_2_write_ptr_work_i + 32'd1) >= fifo_2_size)
                    fifo_2_write_ptr_work_i = 32'd0;
                else
                    fifo_2_write_ptr_work_i = fifo_2_write_ptr_work_i + 32'd1;
                fifo_2_data_work_i[135 - fifo_2_write_ptr_work_i] = data_byte_i[3];
                if ((fifo_2_write_ptr_work_i + 32'd1) >= fifo_2_size)
                    fifo_2_write_ptr_work_i = 32'd0;
                else
                    fifo_2_write_ptr_work_i = fifo_2_write_ptr_work_i + 32'd1;
                fifo_2_data_work_i[135 - fifo_2_write_ptr_work_i] = data_byte_i[2];
                if ((fifo_2_write_ptr_work_i + 32'd1) >= fifo_2_size)
                    fifo_2_write_ptr_work_i = 32'd0;
                else
                    fifo_2_write_ptr_work_i = fifo_2_write_ptr_work_i + 32'd1;
                fifo_2_data_work_i[135 - fifo_2_write_ptr_work_i] = data_byte_i[1];
                if ((fifo_2_write_ptr_work_i + 32'd1) >= fifo_2_size)
                    fifo_2_write_ptr_work_i = 32'd0;
                else
                    fifo_2_write_ptr_work_i = fifo_2_write_ptr_work_i + 32'd1;
                fifo_2_data_work_i[135 - fifo_2_write_ptr_work_i] = data_byte_i[0];
                if ((fifo_2_write_ptr_work_i + 32'd1) >= fifo_2_size)
                    fifo_2_write_ptr_work_i = 32'd0;
                else
                    fifo_2_write_ptr_work_i = fifo_2_write_ptr_work_i + 32'd1;
                fifo_2_fullness_work_i = fifo_2_fullness_work_i + 32'd8;
                if (fifo_2_fullness_work_i > fifo_2_max_fullness_work_i)
                    fifo_2_max_fullness_work_i = fifo_2_fullness_work_i;
                stream_index_i = stream_index_i + 6'd1;
            end
            if (mux_bytes_i > 4'd3) begin
                data_byte_i = aligned_window_i[263 - (stream_index_i * 8) -: 8];
                fifo_2_data_work_i[135 - fifo_2_write_ptr_work_i] = data_byte_i[7];
                if ((fifo_2_write_ptr_work_i + 32'd1) >= fifo_2_size)
                    fifo_2_write_ptr_work_i = 32'd0;
                else
                    fifo_2_write_ptr_work_i = fifo_2_write_ptr_work_i + 32'd1;
                fifo_2_data_work_i[135 - fifo_2_write_ptr_work_i] = data_byte_i[6];
                if ((fifo_2_write_ptr_work_i + 32'd1) >= fifo_2_size)
                    fifo_2_write_ptr_work_i = 32'd0;
                else
                    fifo_2_write_ptr_work_i = fifo_2_write_ptr_work_i + 32'd1;
                fifo_2_data_work_i[135 - fifo_2_write_ptr_work_i] = data_byte_i[5];
                if ((fifo_2_write_ptr_work_i + 32'd1) >= fifo_2_size)
                    fifo_2_write_ptr_work_i = 32'd0;
                else
                    fifo_2_write_ptr_work_i = fifo_2_write_ptr_work_i + 32'd1;
                fifo_2_data_work_i[135 - fifo_2_write_ptr_work_i] = data_byte_i[4];
                if ((fifo_2_write_ptr_work_i + 32'd1) >= fifo_2_size)
                    fifo_2_write_ptr_work_i = 32'd0;
                else
                    fifo_2_write_ptr_work_i = fifo_2_write_ptr_work_i + 32'd1;
                fifo_2_data_work_i[135 - fifo_2_write_ptr_work_i] = data_byte_i[3];
                if ((fifo_2_write_ptr_work_i + 32'd1) >= fifo_2_size)
                    fifo_2_write_ptr_work_i = 32'd0;
                else
                    fifo_2_write_ptr_work_i = fifo_2_write_ptr_work_i + 32'd1;
                fifo_2_data_work_i[135 - fifo_2_write_ptr_work_i] = data_byte_i[2];
                if ((fifo_2_write_ptr_work_i + 32'd1) >= fifo_2_size)
                    fifo_2_write_ptr_work_i = 32'd0;
                else
                    fifo_2_write_ptr_work_i = fifo_2_write_ptr_work_i + 32'd1;
                fifo_2_data_work_i[135 - fifo_2_write_ptr_work_i] = data_byte_i[1];
                if ((fifo_2_write_ptr_work_i + 32'd1) >= fifo_2_size)
                    fifo_2_write_ptr_work_i = 32'd0;
                else
                    fifo_2_write_ptr_work_i = fifo_2_write_ptr_work_i + 32'd1;
                fifo_2_data_work_i[135 - fifo_2_write_ptr_work_i] = data_byte_i[0];
                if ((fifo_2_write_ptr_work_i + 32'd1) >= fifo_2_size)
                    fifo_2_write_ptr_work_i = 32'd0;
                else
                    fifo_2_write_ptr_work_i = fifo_2_write_ptr_work_i + 32'd1;
                fifo_2_fullness_work_i = fifo_2_fullness_work_i + 32'd8;
                if (fifo_2_fullness_work_i > fifo_2_max_fullness_work_i)
                    fifo_2_max_fullness_work_i = fifo_2_fullness_work_i;
                stream_index_i = stream_index_i + 6'd1;
            end
            if (mux_bytes_i > 4'd4) begin
                data_byte_i = aligned_window_i[263 - (stream_index_i * 8) -: 8];
                fifo_2_data_work_i[135 - fifo_2_write_ptr_work_i] = data_byte_i[7];
                if ((fifo_2_write_ptr_work_i + 32'd1) >= fifo_2_size)
                    fifo_2_write_ptr_work_i = 32'd0;
                else
                    fifo_2_write_ptr_work_i = fifo_2_write_ptr_work_i + 32'd1;
                fifo_2_data_work_i[135 - fifo_2_write_ptr_work_i] = data_byte_i[6];
                if ((fifo_2_write_ptr_work_i + 32'd1) >= fifo_2_size)
                    fifo_2_write_ptr_work_i = 32'd0;
                else
                    fifo_2_write_ptr_work_i = fifo_2_write_ptr_work_i + 32'd1;
                fifo_2_data_work_i[135 - fifo_2_write_ptr_work_i] = data_byte_i[5];
                if ((fifo_2_write_ptr_work_i + 32'd1) >= fifo_2_size)
                    fifo_2_write_ptr_work_i = 32'd0;
                else
                    fifo_2_write_ptr_work_i = fifo_2_write_ptr_work_i + 32'd1;
                fifo_2_data_work_i[135 - fifo_2_write_ptr_work_i] = data_byte_i[4];
                if ((fifo_2_write_ptr_work_i + 32'd1) >= fifo_2_size)
                    fifo_2_write_ptr_work_i = 32'd0;
                else
                    fifo_2_write_ptr_work_i = fifo_2_write_ptr_work_i + 32'd1;
                fifo_2_data_work_i[135 - fifo_2_write_ptr_work_i] = data_byte_i[3];
                if ((fifo_2_write_ptr_work_i + 32'd1) >= fifo_2_size)
                    fifo_2_write_ptr_work_i = 32'd0;
                else
                    fifo_2_write_ptr_work_i = fifo_2_write_ptr_work_i + 32'd1;
                fifo_2_data_work_i[135 - fifo_2_write_ptr_work_i] = data_byte_i[2];
                if ((fifo_2_write_ptr_work_i + 32'd1) >= fifo_2_size)
                    fifo_2_write_ptr_work_i = 32'd0;
                else
                    fifo_2_write_ptr_work_i = fifo_2_write_ptr_work_i + 32'd1;
                fifo_2_data_work_i[135 - fifo_2_write_ptr_work_i] = data_byte_i[1];
                if ((fifo_2_write_ptr_work_i + 32'd1) >= fifo_2_size)
                    fifo_2_write_ptr_work_i = 32'd0;
                else
                    fifo_2_write_ptr_work_i = fifo_2_write_ptr_work_i + 32'd1;
                fifo_2_data_work_i[135 - fifo_2_write_ptr_work_i] = data_byte_i[0];
                if ((fifo_2_write_ptr_work_i + 32'd1) >= fifo_2_size)
                    fifo_2_write_ptr_work_i = 32'd0;
                else
                    fifo_2_write_ptr_work_i = fifo_2_write_ptr_work_i + 32'd1;
                fifo_2_fullness_work_i = fifo_2_fullness_work_i + 32'd8;
                if (fifo_2_fullness_work_i > fifo_2_max_fullness_work_i)
                    fifo_2_max_fullness_work_i = fifo_2_fullness_work_i;
                stream_index_i = stream_index_i + 6'd1;
            end
            if (mux_bytes_i > 4'd5) begin
                data_byte_i = aligned_window_i[263 - (stream_index_i * 8) -: 8];
                fifo_2_data_work_i[135 - fifo_2_write_ptr_work_i] = data_byte_i[7];
                if ((fifo_2_write_ptr_work_i + 32'd1) >= fifo_2_size)
                    fifo_2_write_ptr_work_i = 32'd0;
                else
                    fifo_2_write_ptr_work_i = fifo_2_write_ptr_work_i + 32'd1;
                fifo_2_data_work_i[135 - fifo_2_write_ptr_work_i] = data_byte_i[6];
                if ((fifo_2_write_ptr_work_i + 32'd1) >= fifo_2_size)
                    fifo_2_write_ptr_work_i = 32'd0;
                else
                    fifo_2_write_ptr_work_i = fifo_2_write_ptr_work_i + 32'd1;
                fifo_2_data_work_i[135 - fifo_2_write_ptr_work_i] = data_byte_i[5];
                if ((fifo_2_write_ptr_work_i + 32'd1) >= fifo_2_size)
                    fifo_2_write_ptr_work_i = 32'd0;
                else
                    fifo_2_write_ptr_work_i = fifo_2_write_ptr_work_i + 32'd1;
                fifo_2_data_work_i[135 - fifo_2_write_ptr_work_i] = data_byte_i[4];
                if ((fifo_2_write_ptr_work_i + 32'd1) >= fifo_2_size)
                    fifo_2_write_ptr_work_i = 32'd0;
                else
                    fifo_2_write_ptr_work_i = fifo_2_write_ptr_work_i + 32'd1;
                fifo_2_data_work_i[135 - fifo_2_write_ptr_work_i] = data_byte_i[3];
                if ((fifo_2_write_ptr_work_i + 32'd1) >= fifo_2_size)
                    fifo_2_write_ptr_work_i = 32'd0;
                else
                    fifo_2_write_ptr_work_i = fifo_2_write_ptr_work_i + 32'd1;
                fifo_2_data_work_i[135 - fifo_2_write_ptr_work_i] = data_byte_i[2];
                if ((fifo_2_write_ptr_work_i + 32'd1) >= fifo_2_size)
                    fifo_2_write_ptr_work_i = 32'd0;
                else
                    fifo_2_write_ptr_work_i = fifo_2_write_ptr_work_i + 32'd1;
                fifo_2_data_work_i[135 - fifo_2_write_ptr_work_i] = data_byte_i[1];
                if ((fifo_2_write_ptr_work_i + 32'd1) >= fifo_2_size)
                    fifo_2_write_ptr_work_i = 32'd0;
                else
                    fifo_2_write_ptr_work_i = fifo_2_write_ptr_work_i + 32'd1;
                fifo_2_data_work_i[135 - fifo_2_write_ptr_work_i] = data_byte_i[0];
                if ((fifo_2_write_ptr_work_i + 32'd1) >= fifo_2_size)
                    fifo_2_write_ptr_work_i = 32'd0;
                else
                    fifo_2_write_ptr_work_i = fifo_2_write_ptr_work_i + 32'd1;
                fifo_2_fullness_work_i = fifo_2_fullness_work_i + 32'd8;
                if (fifo_2_fullness_work_i > fifo_2_max_fullness_work_i)
                    fifo_2_max_fullness_work_i = fifo_2_fullness_work_i;
                stream_index_i = stream_index_i + 6'd1;
            end
            if (mux_bytes_i > 4'd6) begin
                data_byte_i = aligned_window_i[263 - (stream_index_i * 8) -: 8];
                fifo_2_data_work_i[135 - fifo_2_write_ptr_work_i] = data_byte_i[7];
                if ((fifo_2_write_ptr_work_i + 32'd1) >= fifo_2_size)
                    fifo_2_write_ptr_work_i = 32'd0;
                else
                    fifo_2_write_ptr_work_i = fifo_2_write_ptr_work_i + 32'd1;
                fifo_2_data_work_i[135 - fifo_2_write_ptr_work_i] = data_byte_i[6];
                if ((fifo_2_write_ptr_work_i + 32'd1) >= fifo_2_size)
                    fifo_2_write_ptr_work_i = 32'd0;
                else
                    fifo_2_write_ptr_work_i = fifo_2_write_ptr_work_i + 32'd1;
                fifo_2_data_work_i[135 - fifo_2_write_ptr_work_i] = data_byte_i[5];
                if ((fifo_2_write_ptr_work_i + 32'd1) >= fifo_2_size)
                    fifo_2_write_ptr_work_i = 32'd0;
                else
                    fifo_2_write_ptr_work_i = fifo_2_write_ptr_work_i + 32'd1;
                fifo_2_data_work_i[135 - fifo_2_write_ptr_work_i] = data_byte_i[4];
                if ((fifo_2_write_ptr_work_i + 32'd1) >= fifo_2_size)
                    fifo_2_write_ptr_work_i = 32'd0;
                else
                    fifo_2_write_ptr_work_i = fifo_2_write_ptr_work_i + 32'd1;
                fifo_2_data_work_i[135 - fifo_2_write_ptr_work_i] = data_byte_i[3];
                if ((fifo_2_write_ptr_work_i + 32'd1) >= fifo_2_size)
                    fifo_2_write_ptr_work_i = 32'd0;
                else
                    fifo_2_write_ptr_work_i = fifo_2_write_ptr_work_i + 32'd1;
                fifo_2_data_work_i[135 - fifo_2_write_ptr_work_i] = data_byte_i[2];
                if ((fifo_2_write_ptr_work_i + 32'd1) >= fifo_2_size)
                    fifo_2_write_ptr_work_i = 32'd0;
                else
                    fifo_2_write_ptr_work_i = fifo_2_write_ptr_work_i + 32'd1;
                fifo_2_data_work_i[135 - fifo_2_write_ptr_work_i] = data_byte_i[1];
                if ((fifo_2_write_ptr_work_i + 32'd1) >= fifo_2_size)
                    fifo_2_write_ptr_work_i = 32'd0;
                else
                    fifo_2_write_ptr_work_i = fifo_2_write_ptr_work_i + 32'd1;
                fifo_2_data_work_i[135 - fifo_2_write_ptr_work_i] = data_byte_i[0];
                if ((fifo_2_write_ptr_work_i + 32'd1) >= fifo_2_size)
                    fifo_2_write_ptr_work_i = 32'd0;
                else
                    fifo_2_write_ptr_work_i = fifo_2_write_ptr_work_i + 32'd1;
                fifo_2_fullness_work_i = fifo_2_fullness_work_i + 32'd8;
                if (fifo_2_fullness_work_i > fifo_2_max_fullness_work_i)
                    fifo_2_max_fullness_work_i = fifo_2_fullness_work_i;
                stream_index_i = stream_index_i + 6'd1;
            end
            if (mux_bytes_i > 4'd7) begin
                data_byte_i = aligned_window_i[263 - (stream_index_i * 8) -: 8];
                fifo_2_data_work_i[135 - fifo_2_write_ptr_work_i] = data_byte_i[7];
                if ((fifo_2_write_ptr_work_i + 32'd1) >= fifo_2_size)
                    fifo_2_write_ptr_work_i = 32'd0;
                else
                    fifo_2_write_ptr_work_i = fifo_2_write_ptr_work_i + 32'd1;
                fifo_2_data_work_i[135 - fifo_2_write_ptr_work_i] = data_byte_i[6];
                if ((fifo_2_write_ptr_work_i + 32'd1) >= fifo_2_size)
                    fifo_2_write_ptr_work_i = 32'd0;
                else
                    fifo_2_write_ptr_work_i = fifo_2_write_ptr_work_i + 32'd1;
                fifo_2_data_work_i[135 - fifo_2_write_ptr_work_i] = data_byte_i[5];
                if ((fifo_2_write_ptr_work_i + 32'd1) >= fifo_2_size)
                    fifo_2_write_ptr_work_i = 32'd0;
                else
                    fifo_2_write_ptr_work_i = fifo_2_write_ptr_work_i + 32'd1;
                fifo_2_data_work_i[135 - fifo_2_write_ptr_work_i] = data_byte_i[4];
                if ((fifo_2_write_ptr_work_i + 32'd1) >= fifo_2_size)
                    fifo_2_write_ptr_work_i = 32'd0;
                else
                    fifo_2_write_ptr_work_i = fifo_2_write_ptr_work_i + 32'd1;
                fifo_2_data_work_i[135 - fifo_2_write_ptr_work_i] = data_byte_i[3];
                if ((fifo_2_write_ptr_work_i + 32'd1) >= fifo_2_size)
                    fifo_2_write_ptr_work_i = 32'd0;
                else
                    fifo_2_write_ptr_work_i = fifo_2_write_ptr_work_i + 32'd1;
                fifo_2_data_work_i[135 - fifo_2_write_ptr_work_i] = data_byte_i[2];
                if ((fifo_2_write_ptr_work_i + 32'd1) >= fifo_2_size)
                    fifo_2_write_ptr_work_i = 32'd0;
                else
                    fifo_2_write_ptr_work_i = fifo_2_write_ptr_work_i + 32'd1;
                fifo_2_data_work_i[135 - fifo_2_write_ptr_work_i] = data_byte_i[1];
                if ((fifo_2_write_ptr_work_i + 32'd1) >= fifo_2_size)
                    fifo_2_write_ptr_work_i = 32'd0;
                else
                    fifo_2_write_ptr_work_i = fifo_2_write_ptr_work_i + 32'd1;
                fifo_2_data_work_i[135 - fifo_2_write_ptr_work_i] = data_byte_i[0];
                if ((fifo_2_write_ptr_work_i + 32'd1) >= fifo_2_size)
                    fifo_2_write_ptr_work_i = 32'd0;
                else
                    fifo_2_write_ptr_work_i = fifo_2_write_ptr_work_i + 32'd1;
                fifo_2_fullness_work_i = fifo_2_fullness_work_i + 32'd8;
                if (fifo_2_fullness_work_i > fifo_2_max_fullness_work_i)
                    fifo_2_max_fullness_work_i = fifo_2_fullness_work_i;
                stream_index_i = stream_index_i + 6'd1;
            end
        end
        if (domain_valid && (num_ssps > 3'd3) && (fifo_3_fullness < max_se_size_3)) begin
            if (mux_bytes_i > 4'd0) begin
                data_byte_i = aligned_window_i[263 - (stream_index_i * 8) -: 8];
                fifo_3_data_work_i[135 - fifo_3_write_ptr_work_i] = data_byte_i[7];
                if ((fifo_3_write_ptr_work_i + 32'd1) >= fifo_3_size)
                    fifo_3_write_ptr_work_i = 32'd0;
                else
                    fifo_3_write_ptr_work_i = fifo_3_write_ptr_work_i + 32'd1;
                fifo_3_data_work_i[135 - fifo_3_write_ptr_work_i] = data_byte_i[6];
                if ((fifo_3_write_ptr_work_i + 32'd1) >= fifo_3_size)
                    fifo_3_write_ptr_work_i = 32'd0;
                else
                    fifo_3_write_ptr_work_i = fifo_3_write_ptr_work_i + 32'd1;
                fifo_3_data_work_i[135 - fifo_3_write_ptr_work_i] = data_byte_i[5];
                if ((fifo_3_write_ptr_work_i + 32'd1) >= fifo_3_size)
                    fifo_3_write_ptr_work_i = 32'd0;
                else
                    fifo_3_write_ptr_work_i = fifo_3_write_ptr_work_i + 32'd1;
                fifo_3_data_work_i[135 - fifo_3_write_ptr_work_i] = data_byte_i[4];
                if ((fifo_3_write_ptr_work_i + 32'd1) >= fifo_3_size)
                    fifo_3_write_ptr_work_i = 32'd0;
                else
                    fifo_3_write_ptr_work_i = fifo_3_write_ptr_work_i + 32'd1;
                fifo_3_data_work_i[135 - fifo_3_write_ptr_work_i] = data_byte_i[3];
                if ((fifo_3_write_ptr_work_i + 32'd1) >= fifo_3_size)
                    fifo_3_write_ptr_work_i = 32'd0;
                else
                    fifo_3_write_ptr_work_i = fifo_3_write_ptr_work_i + 32'd1;
                fifo_3_data_work_i[135 - fifo_3_write_ptr_work_i] = data_byte_i[2];
                if ((fifo_3_write_ptr_work_i + 32'd1) >= fifo_3_size)
                    fifo_3_write_ptr_work_i = 32'd0;
                else
                    fifo_3_write_ptr_work_i = fifo_3_write_ptr_work_i + 32'd1;
                fifo_3_data_work_i[135 - fifo_3_write_ptr_work_i] = data_byte_i[1];
                if ((fifo_3_write_ptr_work_i + 32'd1) >= fifo_3_size)
                    fifo_3_write_ptr_work_i = 32'd0;
                else
                    fifo_3_write_ptr_work_i = fifo_3_write_ptr_work_i + 32'd1;
                fifo_3_data_work_i[135 - fifo_3_write_ptr_work_i] = data_byte_i[0];
                if ((fifo_3_write_ptr_work_i + 32'd1) >= fifo_3_size)
                    fifo_3_write_ptr_work_i = 32'd0;
                else
                    fifo_3_write_ptr_work_i = fifo_3_write_ptr_work_i + 32'd1;
                fifo_3_fullness_work_i = fifo_3_fullness_work_i + 32'd8;
                if (fifo_3_fullness_work_i > fifo_3_max_fullness_work_i)
                    fifo_3_max_fullness_work_i = fifo_3_fullness_work_i;
                stream_index_i = stream_index_i + 6'd1;
            end
            if (mux_bytes_i > 4'd1) begin
                data_byte_i = aligned_window_i[263 - (stream_index_i * 8) -: 8];
                fifo_3_data_work_i[135 - fifo_3_write_ptr_work_i] = data_byte_i[7];
                if ((fifo_3_write_ptr_work_i + 32'd1) >= fifo_3_size)
                    fifo_3_write_ptr_work_i = 32'd0;
                else
                    fifo_3_write_ptr_work_i = fifo_3_write_ptr_work_i + 32'd1;
                fifo_3_data_work_i[135 - fifo_3_write_ptr_work_i] = data_byte_i[6];
                if ((fifo_3_write_ptr_work_i + 32'd1) >= fifo_3_size)
                    fifo_3_write_ptr_work_i = 32'd0;
                else
                    fifo_3_write_ptr_work_i = fifo_3_write_ptr_work_i + 32'd1;
                fifo_3_data_work_i[135 - fifo_3_write_ptr_work_i] = data_byte_i[5];
                if ((fifo_3_write_ptr_work_i + 32'd1) >= fifo_3_size)
                    fifo_3_write_ptr_work_i = 32'd0;
                else
                    fifo_3_write_ptr_work_i = fifo_3_write_ptr_work_i + 32'd1;
                fifo_3_data_work_i[135 - fifo_3_write_ptr_work_i] = data_byte_i[4];
                if ((fifo_3_write_ptr_work_i + 32'd1) >= fifo_3_size)
                    fifo_3_write_ptr_work_i = 32'd0;
                else
                    fifo_3_write_ptr_work_i = fifo_3_write_ptr_work_i + 32'd1;
                fifo_3_data_work_i[135 - fifo_3_write_ptr_work_i] = data_byte_i[3];
                if ((fifo_3_write_ptr_work_i + 32'd1) >= fifo_3_size)
                    fifo_3_write_ptr_work_i = 32'd0;
                else
                    fifo_3_write_ptr_work_i = fifo_3_write_ptr_work_i + 32'd1;
                fifo_3_data_work_i[135 - fifo_3_write_ptr_work_i] = data_byte_i[2];
                if ((fifo_3_write_ptr_work_i + 32'd1) >= fifo_3_size)
                    fifo_3_write_ptr_work_i = 32'd0;
                else
                    fifo_3_write_ptr_work_i = fifo_3_write_ptr_work_i + 32'd1;
                fifo_3_data_work_i[135 - fifo_3_write_ptr_work_i] = data_byte_i[1];
                if ((fifo_3_write_ptr_work_i + 32'd1) >= fifo_3_size)
                    fifo_3_write_ptr_work_i = 32'd0;
                else
                    fifo_3_write_ptr_work_i = fifo_3_write_ptr_work_i + 32'd1;
                fifo_3_data_work_i[135 - fifo_3_write_ptr_work_i] = data_byte_i[0];
                if ((fifo_3_write_ptr_work_i + 32'd1) >= fifo_3_size)
                    fifo_3_write_ptr_work_i = 32'd0;
                else
                    fifo_3_write_ptr_work_i = fifo_3_write_ptr_work_i + 32'd1;
                fifo_3_fullness_work_i = fifo_3_fullness_work_i + 32'd8;
                if (fifo_3_fullness_work_i > fifo_3_max_fullness_work_i)
                    fifo_3_max_fullness_work_i = fifo_3_fullness_work_i;
                stream_index_i = stream_index_i + 6'd1;
            end
            if (mux_bytes_i > 4'd2) begin
                data_byte_i = aligned_window_i[263 - (stream_index_i * 8) -: 8];
                fifo_3_data_work_i[135 - fifo_3_write_ptr_work_i] = data_byte_i[7];
                if ((fifo_3_write_ptr_work_i + 32'd1) >= fifo_3_size)
                    fifo_3_write_ptr_work_i = 32'd0;
                else
                    fifo_3_write_ptr_work_i = fifo_3_write_ptr_work_i + 32'd1;
                fifo_3_data_work_i[135 - fifo_3_write_ptr_work_i] = data_byte_i[6];
                if ((fifo_3_write_ptr_work_i + 32'd1) >= fifo_3_size)
                    fifo_3_write_ptr_work_i = 32'd0;
                else
                    fifo_3_write_ptr_work_i = fifo_3_write_ptr_work_i + 32'd1;
                fifo_3_data_work_i[135 - fifo_3_write_ptr_work_i] = data_byte_i[5];
                if ((fifo_3_write_ptr_work_i + 32'd1) >= fifo_3_size)
                    fifo_3_write_ptr_work_i = 32'd0;
                else
                    fifo_3_write_ptr_work_i = fifo_3_write_ptr_work_i + 32'd1;
                fifo_3_data_work_i[135 - fifo_3_write_ptr_work_i] = data_byte_i[4];
                if ((fifo_3_write_ptr_work_i + 32'd1) >= fifo_3_size)
                    fifo_3_write_ptr_work_i = 32'd0;
                else
                    fifo_3_write_ptr_work_i = fifo_3_write_ptr_work_i + 32'd1;
                fifo_3_data_work_i[135 - fifo_3_write_ptr_work_i] = data_byte_i[3];
                if ((fifo_3_write_ptr_work_i + 32'd1) >= fifo_3_size)
                    fifo_3_write_ptr_work_i = 32'd0;
                else
                    fifo_3_write_ptr_work_i = fifo_3_write_ptr_work_i + 32'd1;
                fifo_3_data_work_i[135 - fifo_3_write_ptr_work_i] = data_byte_i[2];
                if ((fifo_3_write_ptr_work_i + 32'd1) >= fifo_3_size)
                    fifo_3_write_ptr_work_i = 32'd0;
                else
                    fifo_3_write_ptr_work_i = fifo_3_write_ptr_work_i + 32'd1;
                fifo_3_data_work_i[135 - fifo_3_write_ptr_work_i] = data_byte_i[1];
                if ((fifo_3_write_ptr_work_i + 32'd1) >= fifo_3_size)
                    fifo_3_write_ptr_work_i = 32'd0;
                else
                    fifo_3_write_ptr_work_i = fifo_3_write_ptr_work_i + 32'd1;
                fifo_3_data_work_i[135 - fifo_3_write_ptr_work_i] = data_byte_i[0];
                if ((fifo_3_write_ptr_work_i + 32'd1) >= fifo_3_size)
                    fifo_3_write_ptr_work_i = 32'd0;
                else
                    fifo_3_write_ptr_work_i = fifo_3_write_ptr_work_i + 32'd1;
                fifo_3_fullness_work_i = fifo_3_fullness_work_i + 32'd8;
                if (fifo_3_fullness_work_i > fifo_3_max_fullness_work_i)
                    fifo_3_max_fullness_work_i = fifo_3_fullness_work_i;
                stream_index_i = stream_index_i + 6'd1;
            end
            if (mux_bytes_i > 4'd3) begin
                data_byte_i = aligned_window_i[263 - (stream_index_i * 8) -: 8];
                fifo_3_data_work_i[135 - fifo_3_write_ptr_work_i] = data_byte_i[7];
                if ((fifo_3_write_ptr_work_i + 32'd1) >= fifo_3_size)
                    fifo_3_write_ptr_work_i = 32'd0;
                else
                    fifo_3_write_ptr_work_i = fifo_3_write_ptr_work_i + 32'd1;
                fifo_3_data_work_i[135 - fifo_3_write_ptr_work_i] = data_byte_i[6];
                if ((fifo_3_write_ptr_work_i + 32'd1) >= fifo_3_size)
                    fifo_3_write_ptr_work_i = 32'd0;
                else
                    fifo_3_write_ptr_work_i = fifo_3_write_ptr_work_i + 32'd1;
                fifo_3_data_work_i[135 - fifo_3_write_ptr_work_i] = data_byte_i[5];
                if ((fifo_3_write_ptr_work_i + 32'd1) >= fifo_3_size)
                    fifo_3_write_ptr_work_i = 32'd0;
                else
                    fifo_3_write_ptr_work_i = fifo_3_write_ptr_work_i + 32'd1;
                fifo_3_data_work_i[135 - fifo_3_write_ptr_work_i] = data_byte_i[4];
                if ((fifo_3_write_ptr_work_i + 32'd1) >= fifo_3_size)
                    fifo_3_write_ptr_work_i = 32'd0;
                else
                    fifo_3_write_ptr_work_i = fifo_3_write_ptr_work_i + 32'd1;
                fifo_3_data_work_i[135 - fifo_3_write_ptr_work_i] = data_byte_i[3];
                if ((fifo_3_write_ptr_work_i + 32'd1) >= fifo_3_size)
                    fifo_3_write_ptr_work_i = 32'd0;
                else
                    fifo_3_write_ptr_work_i = fifo_3_write_ptr_work_i + 32'd1;
                fifo_3_data_work_i[135 - fifo_3_write_ptr_work_i] = data_byte_i[2];
                if ((fifo_3_write_ptr_work_i + 32'd1) >= fifo_3_size)
                    fifo_3_write_ptr_work_i = 32'd0;
                else
                    fifo_3_write_ptr_work_i = fifo_3_write_ptr_work_i + 32'd1;
                fifo_3_data_work_i[135 - fifo_3_write_ptr_work_i] = data_byte_i[1];
                if ((fifo_3_write_ptr_work_i + 32'd1) >= fifo_3_size)
                    fifo_3_write_ptr_work_i = 32'd0;
                else
                    fifo_3_write_ptr_work_i = fifo_3_write_ptr_work_i + 32'd1;
                fifo_3_data_work_i[135 - fifo_3_write_ptr_work_i] = data_byte_i[0];
                if ((fifo_3_write_ptr_work_i + 32'd1) >= fifo_3_size)
                    fifo_3_write_ptr_work_i = 32'd0;
                else
                    fifo_3_write_ptr_work_i = fifo_3_write_ptr_work_i + 32'd1;
                fifo_3_fullness_work_i = fifo_3_fullness_work_i + 32'd8;
                if (fifo_3_fullness_work_i > fifo_3_max_fullness_work_i)
                    fifo_3_max_fullness_work_i = fifo_3_fullness_work_i;
                stream_index_i = stream_index_i + 6'd1;
            end
            if (mux_bytes_i > 4'd4) begin
                data_byte_i = aligned_window_i[263 - (stream_index_i * 8) -: 8];
                fifo_3_data_work_i[135 - fifo_3_write_ptr_work_i] = data_byte_i[7];
                if ((fifo_3_write_ptr_work_i + 32'd1) >= fifo_3_size)
                    fifo_3_write_ptr_work_i = 32'd0;
                else
                    fifo_3_write_ptr_work_i = fifo_3_write_ptr_work_i + 32'd1;
                fifo_3_data_work_i[135 - fifo_3_write_ptr_work_i] = data_byte_i[6];
                if ((fifo_3_write_ptr_work_i + 32'd1) >= fifo_3_size)
                    fifo_3_write_ptr_work_i = 32'd0;
                else
                    fifo_3_write_ptr_work_i = fifo_3_write_ptr_work_i + 32'd1;
                fifo_3_data_work_i[135 - fifo_3_write_ptr_work_i] = data_byte_i[5];
                if ((fifo_3_write_ptr_work_i + 32'd1) >= fifo_3_size)
                    fifo_3_write_ptr_work_i = 32'd0;
                else
                    fifo_3_write_ptr_work_i = fifo_3_write_ptr_work_i + 32'd1;
                fifo_3_data_work_i[135 - fifo_3_write_ptr_work_i] = data_byte_i[4];
                if ((fifo_3_write_ptr_work_i + 32'd1) >= fifo_3_size)
                    fifo_3_write_ptr_work_i = 32'd0;
                else
                    fifo_3_write_ptr_work_i = fifo_3_write_ptr_work_i + 32'd1;
                fifo_3_data_work_i[135 - fifo_3_write_ptr_work_i] = data_byte_i[3];
                if ((fifo_3_write_ptr_work_i + 32'd1) >= fifo_3_size)
                    fifo_3_write_ptr_work_i = 32'd0;
                else
                    fifo_3_write_ptr_work_i = fifo_3_write_ptr_work_i + 32'd1;
                fifo_3_data_work_i[135 - fifo_3_write_ptr_work_i] = data_byte_i[2];
                if ((fifo_3_write_ptr_work_i + 32'd1) >= fifo_3_size)
                    fifo_3_write_ptr_work_i = 32'd0;
                else
                    fifo_3_write_ptr_work_i = fifo_3_write_ptr_work_i + 32'd1;
                fifo_3_data_work_i[135 - fifo_3_write_ptr_work_i] = data_byte_i[1];
                if ((fifo_3_write_ptr_work_i + 32'd1) >= fifo_3_size)
                    fifo_3_write_ptr_work_i = 32'd0;
                else
                    fifo_3_write_ptr_work_i = fifo_3_write_ptr_work_i + 32'd1;
                fifo_3_data_work_i[135 - fifo_3_write_ptr_work_i] = data_byte_i[0];
                if ((fifo_3_write_ptr_work_i + 32'd1) >= fifo_3_size)
                    fifo_3_write_ptr_work_i = 32'd0;
                else
                    fifo_3_write_ptr_work_i = fifo_3_write_ptr_work_i + 32'd1;
                fifo_3_fullness_work_i = fifo_3_fullness_work_i + 32'd8;
                if (fifo_3_fullness_work_i > fifo_3_max_fullness_work_i)
                    fifo_3_max_fullness_work_i = fifo_3_fullness_work_i;
                stream_index_i = stream_index_i + 6'd1;
            end
            if (mux_bytes_i > 4'd5) begin
                data_byte_i = aligned_window_i[263 - (stream_index_i * 8) -: 8];
                fifo_3_data_work_i[135 - fifo_3_write_ptr_work_i] = data_byte_i[7];
                if ((fifo_3_write_ptr_work_i + 32'd1) >= fifo_3_size)
                    fifo_3_write_ptr_work_i = 32'd0;
                else
                    fifo_3_write_ptr_work_i = fifo_3_write_ptr_work_i + 32'd1;
                fifo_3_data_work_i[135 - fifo_3_write_ptr_work_i] = data_byte_i[6];
                if ((fifo_3_write_ptr_work_i + 32'd1) >= fifo_3_size)
                    fifo_3_write_ptr_work_i = 32'd0;
                else
                    fifo_3_write_ptr_work_i = fifo_3_write_ptr_work_i + 32'd1;
                fifo_3_data_work_i[135 - fifo_3_write_ptr_work_i] = data_byte_i[5];
                if ((fifo_3_write_ptr_work_i + 32'd1) >= fifo_3_size)
                    fifo_3_write_ptr_work_i = 32'd0;
                else
                    fifo_3_write_ptr_work_i = fifo_3_write_ptr_work_i + 32'd1;
                fifo_3_data_work_i[135 - fifo_3_write_ptr_work_i] = data_byte_i[4];
                if ((fifo_3_write_ptr_work_i + 32'd1) >= fifo_3_size)
                    fifo_3_write_ptr_work_i = 32'd0;
                else
                    fifo_3_write_ptr_work_i = fifo_3_write_ptr_work_i + 32'd1;
                fifo_3_data_work_i[135 - fifo_3_write_ptr_work_i] = data_byte_i[3];
                if ((fifo_3_write_ptr_work_i + 32'd1) >= fifo_3_size)
                    fifo_3_write_ptr_work_i = 32'd0;
                else
                    fifo_3_write_ptr_work_i = fifo_3_write_ptr_work_i + 32'd1;
                fifo_3_data_work_i[135 - fifo_3_write_ptr_work_i] = data_byte_i[2];
                if ((fifo_3_write_ptr_work_i + 32'd1) >= fifo_3_size)
                    fifo_3_write_ptr_work_i = 32'd0;
                else
                    fifo_3_write_ptr_work_i = fifo_3_write_ptr_work_i + 32'd1;
                fifo_3_data_work_i[135 - fifo_3_write_ptr_work_i] = data_byte_i[1];
                if ((fifo_3_write_ptr_work_i + 32'd1) >= fifo_3_size)
                    fifo_3_write_ptr_work_i = 32'd0;
                else
                    fifo_3_write_ptr_work_i = fifo_3_write_ptr_work_i + 32'd1;
                fifo_3_data_work_i[135 - fifo_3_write_ptr_work_i] = data_byte_i[0];
                if ((fifo_3_write_ptr_work_i + 32'd1) >= fifo_3_size)
                    fifo_3_write_ptr_work_i = 32'd0;
                else
                    fifo_3_write_ptr_work_i = fifo_3_write_ptr_work_i + 32'd1;
                fifo_3_fullness_work_i = fifo_3_fullness_work_i + 32'd8;
                if (fifo_3_fullness_work_i > fifo_3_max_fullness_work_i)
                    fifo_3_max_fullness_work_i = fifo_3_fullness_work_i;
                stream_index_i = stream_index_i + 6'd1;
            end
            if (mux_bytes_i > 4'd6) begin
                data_byte_i = aligned_window_i[263 - (stream_index_i * 8) -: 8];
                fifo_3_data_work_i[135 - fifo_3_write_ptr_work_i] = data_byte_i[7];
                if ((fifo_3_write_ptr_work_i + 32'd1) >= fifo_3_size)
                    fifo_3_write_ptr_work_i = 32'd0;
                else
                    fifo_3_write_ptr_work_i = fifo_3_write_ptr_work_i + 32'd1;
                fifo_3_data_work_i[135 - fifo_3_write_ptr_work_i] = data_byte_i[6];
                if ((fifo_3_write_ptr_work_i + 32'd1) >= fifo_3_size)
                    fifo_3_write_ptr_work_i = 32'd0;
                else
                    fifo_3_write_ptr_work_i = fifo_3_write_ptr_work_i + 32'd1;
                fifo_3_data_work_i[135 - fifo_3_write_ptr_work_i] = data_byte_i[5];
                if ((fifo_3_write_ptr_work_i + 32'd1) >= fifo_3_size)
                    fifo_3_write_ptr_work_i = 32'd0;
                else
                    fifo_3_write_ptr_work_i = fifo_3_write_ptr_work_i + 32'd1;
                fifo_3_data_work_i[135 - fifo_3_write_ptr_work_i] = data_byte_i[4];
                if ((fifo_3_write_ptr_work_i + 32'd1) >= fifo_3_size)
                    fifo_3_write_ptr_work_i = 32'd0;
                else
                    fifo_3_write_ptr_work_i = fifo_3_write_ptr_work_i + 32'd1;
                fifo_3_data_work_i[135 - fifo_3_write_ptr_work_i] = data_byte_i[3];
                if ((fifo_3_write_ptr_work_i + 32'd1) >= fifo_3_size)
                    fifo_3_write_ptr_work_i = 32'd0;
                else
                    fifo_3_write_ptr_work_i = fifo_3_write_ptr_work_i + 32'd1;
                fifo_3_data_work_i[135 - fifo_3_write_ptr_work_i] = data_byte_i[2];
                if ((fifo_3_write_ptr_work_i + 32'd1) >= fifo_3_size)
                    fifo_3_write_ptr_work_i = 32'd0;
                else
                    fifo_3_write_ptr_work_i = fifo_3_write_ptr_work_i + 32'd1;
                fifo_3_data_work_i[135 - fifo_3_write_ptr_work_i] = data_byte_i[1];
                if ((fifo_3_write_ptr_work_i + 32'd1) >= fifo_3_size)
                    fifo_3_write_ptr_work_i = 32'd0;
                else
                    fifo_3_write_ptr_work_i = fifo_3_write_ptr_work_i + 32'd1;
                fifo_3_data_work_i[135 - fifo_3_write_ptr_work_i] = data_byte_i[0];
                if ((fifo_3_write_ptr_work_i + 32'd1) >= fifo_3_size)
                    fifo_3_write_ptr_work_i = 32'd0;
                else
                    fifo_3_write_ptr_work_i = fifo_3_write_ptr_work_i + 32'd1;
                fifo_3_fullness_work_i = fifo_3_fullness_work_i + 32'd8;
                if (fifo_3_fullness_work_i > fifo_3_max_fullness_work_i)
                    fifo_3_max_fullness_work_i = fifo_3_fullness_work_i;
                stream_index_i = stream_index_i + 6'd1;
            end
            if (mux_bytes_i > 4'd7) begin
                data_byte_i = aligned_window_i[263 - (stream_index_i * 8) -: 8];
                fifo_3_data_work_i[135 - fifo_3_write_ptr_work_i] = data_byte_i[7];
                if ((fifo_3_write_ptr_work_i + 32'd1) >= fifo_3_size)
                    fifo_3_write_ptr_work_i = 32'd0;
                else
                    fifo_3_write_ptr_work_i = fifo_3_write_ptr_work_i + 32'd1;
                fifo_3_data_work_i[135 - fifo_3_write_ptr_work_i] = data_byte_i[6];
                if ((fifo_3_write_ptr_work_i + 32'd1) >= fifo_3_size)
                    fifo_3_write_ptr_work_i = 32'd0;
                else
                    fifo_3_write_ptr_work_i = fifo_3_write_ptr_work_i + 32'd1;
                fifo_3_data_work_i[135 - fifo_3_write_ptr_work_i] = data_byte_i[5];
                if ((fifo_3_write_ptr_work_i + 32'd1) >= fifo_3_size)
                    fifo_3_write_ptr_work_i = 32'd0;
                else
                    fifo_3_write_ptr_work_i = fifo_3_write_ptr_work_i + 32'd1;
                fifo_3_data_work_i[135 - fifo_3_write_ptr_work_i] = data_byte_i[4];
                if ((fifo_3_write_ptr_work_i + 32'd1) >= fifo_3_size)
                    fifo_3_write_ptr_work_i = 32'd0;
                else
                    fifo_3_write_ptr_work_i = fifo_3_write_ptr_work_i + 32'd1;
                fifo_3_data_work_i[135 - fifo_3_write_ptr_work_i] = data_byte_i[3];
                if ((fifo_3_write_ptr_work_i + 32'd1) >= fifo_3_size)
                    fifo_3_write_ptr_work_i = 32'd0;
                else
                    fifo_3_write_ptr_work_i = fifo_3_write_ptr_work_i + 32'd1;
                fifo_3_data_work_i[135 - fifo_3_write_ptr_work_i] = data_byte_i[2];
                if ((fifo_3_write_ptr_work_i + 32'd1) >= fifo_3_size)
                    fifo_3_write_ptr_work_i = 32'd0;
                else
                    fifo_3_write_ptr_work_i = fifo_3_write_ptr_work_i + 32'd1;
                fifo_3_data_work_i[135 - fifo_3_write_ptr_work_i] = data_byte_i[1];
                if ((fifo_3_write_ptr_work_i + 32'd1) >= fifo_3_size)
                    fifo_3_write_ptr_work_i = 32'd0;
                else
                    fifo_3_write_ptr_work_i = fifo_3_write_ptr_work_i + 32'd1;
                fifo_3_data_work_i[135 - fifo_3_write_ptr_work_i] = data_byte_i[0];
                if ((fifo_3_write_ptr_work_i + 32'd1) >= fifo_3_size)
                    fifo_3_write_ptr_work_i = 32'd0;
                else
                    fifo_3_write_ptr_work_i = fifo_3_write_ptr_work_i + 32'd1;
                fifo_3_fullness_work_i = fifo_3_fullness_work_i + 32'd8;
                if (fifo_3_fullness_work_i > fifo_3_max_fullness_work_i)
                    fifo_3_max_fullness_work_i = fifo_3_fullness_work_i;
                stream_index_i = stream_index_i + 6'd1;
            end
        end
        post_mux_num_bits_out = post_mux_num_bits + {23'd0, stream_index_i, 3'b000};
        fifo_0_fullness_out = fifo_0_fullness_work_i;
        fifo_0_write_ptr_out = fifo_0_write_ptr_work_i;
        fifo_0_max_fullness_out = fifo_0_max_fullness_work_i;
        fifo_0_byte_0_out = fifo_0_data_work_i[135 -: 8];
        fifo_0_byte_1_out = fifo_0_data_work_i[127 -: 8];
        fifo_0_byte_2_out = fifo_0_data_work_i[119 -: 8];
        fifo_0_byte_3_out = fifo_0_data_work_i[111 -: 8];
        fifo_0_byte_4_out = fifo_0_data_work_i[103 -: 8];
        fifo_0_byte_5_out = fifo_0_data_work_i[95 -: 8];
        fifo_0_byte_6_out = fifo_0_data_work_i[87 -: 8];
        fifo_0_byte_7_out = fifo_0_data_work_i[79 -: 8];
        fifo_0_byte_8_out = fifo_0_data_work_i[71 -: 8];
        fifo_0_byte_9_out = fifo_0_data_work_i[63 -: 8];
        fifo_0_byte_10_out = fifo_0_data_work_i[55 -: 8];
        fifo_0_byte_11_out = fifo_0_data_work_i[47 -: 8];
        fifo_0_byte_12_out = fifo_0_data_work_i[39 -: 8];
        fifo_0_byte_13_out = fifo_0_data_work_i[31 -: 8];
        fifo_0_byte_14_out = fifo_0_data_work_i[23 -: 8];
        fifo_0_byte_15_out = fifo_0_data_work_i[15 -: 8];
        fifo_0_byte_16_out = fifo_0_data_work_i[7 -: 8];
        fifo_1_fullness_out = fifo_1_fullness_work_i;
        fifo_1_write_ptr_out = fifo_1_write_ptr_work_i;
        fifo_1_max_fullness_out = fifo_1_max_fullness_work_i;
        fifo_1_byte_0_out = fifo_1_data_work_i[135 -: 8];
        fifo_1_byte_1_out = fifo_1_data_work_i[127 -: 8];
        fifo_1_byte_2_out = fifo_1_data_work_i[119 -: 8];
        fifo_1_byte_3_out = fifo_1_data_work_i[111 -: 8];
        fifo_1_byte_4_out = fifo_1_data_work_i[103 -: 8];
        fifo_1_byte_5_out = fifo_1_data_work_i[95 -: 8];
        fifo_1_byte_6_out = fifo_1_data_work_i[87 -: 8];
        fifo_1_byte_7_out = fifo_1_data_work_i[79 -: 8];
        fifo_1_byte_8_out = fifo_1_data_work_i[71 -: 8];
        fifo_1_byte_9_out = fifo_1_data_work_i[63 -: 8];
        fifo_1_byte_10_out = fifo_1_data_work_i[55 -: 8];
        fifo_1_byte_11_out = fifo_1_data_work_i[47 -: 8];
        fifo_1_byte_12_out = fifo_1_data_work_i[39 -: 8];
        fifo_1_byte_13_out = fifo_1_data_work_i[31 -: 8];
        fifo_1_byte_14_out = fifo_1_data_work_i[23 -: 8];
        fifo_1_byte_15_out = fifo_1_data_work_i[15 -: 8];
        fifo_1_byte_16_out = fifo_1_data_work_i[7 -: 8];
        fifo_2_fullness_out = fifo_2_fullness_work_i;
        fifo_2_write_ptr_out = fifo_2_write_ptr_work_i;
        fifo_2_max_fullness_out = fifo_2_max_fullness_work_i;
        fifo_2_byte_0_out = fifo_2_data_work_i[135 -: 8];
        fifo_2_byte_1_out = fifo_2_data_work_i[127 -: 8];
        fifo_2_byte_2_out = fifo_2_data_work_i[119 -: 8];
        fifo_2_byte_3_out = fifo_2_data_work_i[111 -: 8];
        fifo_2_byte_4_out = fifo_2_data_work_i[103 -: 8];
        fifo_2_byte_5_out = fifo_2_data_work_i[95 -: 8];
        fifo_2_byte_6_out = fifo_2_data_work_i[87 -: 8];
        fifo_2_byte_7_out = fifo_2_data_work_i[79 -: 8];
        fifo_2_byte_8_out = fifo_2_data_work_i[71 -: 8];
        fifo_2_byte_9_out = fifo_2_data_work_i[63 -: 8];
        fifo_2_byte_10_out = fifo_2_data_work_i[55 -: 8];
        fifo_2_byte_11_out = fifo_2_data_work_i[47 -: 8];
        fifo_2_byte_12_out = fifo_2_data_work_i[39 -: 8];
        fifo_2_byte_13_out = fifo_2_data_work_i[31 -: 8];
        fifo_2_byte_14_out = fifo_2_data_work_i[23 -: 8];
        fifo_2_byte_15_out = fifo_2_data_work_i[15 -: 8];
        fifo_2_byte_16_out = fifo_2_data_work_i[7 -: 8];
        fifo_3_fullness_out = fifo_3_fullness_work_i;
        fifo_3_write_ptr_out = fifo_3_write_ptr_work_i;
        fifo_3_max_fullness_out = fifo_3_max_fullness_work_i;
        fifo_3_byte_0_out = fifo_3_data_work_i[135 -: 8];
        fifo_3_byte_1_out = fifo_3_data_work_i[127 -: 8];
        fifo_3_byte_2_out = fifo_3_data_work_i[119 -: 8];
        fifo_3_byte_3_out = fifo_3_data_work_i[111 -: 8];
        fifo_3_byte_4_out = fifo_3_data_work_i[103 -: 8];
        fifo_3_byte_5_out = fifo_3_data_work_i[95 -: 8];
        fifo_3_byte_6_out = fifo_3_data_work_i[87 -: 8];
        fifo_3_byte_7_out = fifo_3_data_work_i[79 -: 8];
        fifo_3_byte_8_out = fifo_3_data_work_i[71 -: 8];
        fifo_3_byte_9_out = fifo_3_data_work_i[63 -: 8];
        fifo_3_byte_10_out = fifo_3_data_work_i[55 -: 8];
        fifo_3_byte_11_out = fifo_3_data_work_i[47 -: 8];
        fifo_3_byte_12_out = fifo_3_data_work_i[39 -: 8];
        fifo_3_byte_13_out = fifo_3_data_work_i[31 -: 8];
        fifo_3_byte_14_out = fifo_3_data_work_i[23 -: 8];
        fifo_3_byte_15_out = fifo_3_data_work_i[15 -: 8];
        fifo_3_byte_16_out = fifo_3_data_work_i[7 -: 8];
    end
endmodule
