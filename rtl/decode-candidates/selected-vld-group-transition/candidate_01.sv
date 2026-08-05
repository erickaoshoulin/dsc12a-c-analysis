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

module getqpadjpredsize (
    input logic [1:0] unit,
    input logic [1:0] dsc_version_minor,
    input logic native_420,
    input logic [1:0] unit_c_type_selected,
    input logic [4:0] predicted_size_selected,
    input logic [4:0] primary_qp,
    input logic [4:0] prev_primary_qp,
    input logic [4:0] cpntBitDepth_0,
    input logic [4:0] cpntBitDepth_1,
    input logic [4:0] cpntBitDepth_2,
    input logic [4:0] cpntBitDepth_3,
    input logic [4:0] qlevel_luma_new,
    input logic [4:0] qlevel_chroma_new,
    input logic [4:0] qlevel_luma_old,
    input logic [4:0] qlevel_chroma_old,
    output logic signed [4:0] return_value
);
    integer signed cpnt_i;
    integer signed bit_depth_i;
    integer signed qlevel_new_i;
    integer signed qlevel_old_i;
    integer signed pred_size_i;
    integer signed max_size_i;
    always_comb begin
        cpnt_i = unit_c_type_selected;
        case (cpnt_i)
            0: bit_depth_i = cpntBitDepth_0;
            1: bit_depth_i = cpntBitDepth_1;
            2: bit_depth_i = cpntBitDepth_2;
            3: bit_depth_i = cpntBitDepth_3;
            default: bit_depth_i = cpntBitDepth_0;
        endcase
        if ((cpnt_i % 3) == 0) begin
            qlevel_new_i = qlevel_luma_new;
        end else if ((native_420 != 0) && (cpnt_i == 1)) begin
            qlevel_new_i = qlevel_luma_new;
        end else begin
            qlevel_new_i = qlevel_chroma_new;
            if ((dsc_version_minor == 2) && (cpntBitDepth_0 == cpntBitDepth_1) && (qlevel_new_i > 0)) begin
                qlevel_new_i = qlevel_new_i - 1;
            end
        end
        if ((cpnt_i % 3) == 0) begin
            qlevel_old_i = qlevel_luma_old;
        end else if ((native_420 != 0) && (cpnt_i == 1)) begin
            qlevel_old_i = qlevel_luma_old;
        end else begin
            qlevel_old_i = qlevel_chroma_old;
            if ((dsc_version_minor == 2) && (cpntBitDepth_0 == cpntBitDepth_1) && (qlevel_old_i > 0)) begin
                qlevel_old_i = qlevel_old_i - 1;
            end
        end
        pred_size_i = predicted_size_selected + qlevel_old_i - qlevel_new_i;
        max_size_i = bit_depth_i - qlevel_new_i;
        if (pred_size_i < 0) pred_size_i = 0;
        else if (pred_size_i > (max_size_i - 1)) pred_size_i = max_size_i - 1;
        return_value = pred_size_i;
    end
endmodule

module escapecodesize (
    input logic [4:0] qp,
    input logic [1:0] dsc_version_minor,
    input logic native_420,
    input logic [4:0] cpntBitDepth_0,
    input logic [4:0] qlevel_luma,
    output logic signed [5:0] return_value
);
    assign return_value = (cpntBitDepth_0 + 1 - qlevel_luma);
endmodule

module isflatnessinfosent (
    input logic [4:0] qp,
    input logic [4:0] flatness_min_qp,
    input logic [4:0] flatness_max_qp,
    output logic return_value
);
    assign return_value = ((qp >= flatness_min_qp) && (qp <= flatness_max_qp));
endmodule

module maxresidualsize (
    input logic [1:0] cpnt,
    input logic [4:0] qp,
    input logic [1:0] dsc_version_minor,
    input logic native_420,
    input logic [4:0] cpntBitDepth_0,
    input logic [4:0] cpntBitDepth_1,
    input logic [4:0] cpntBitDepth_selected,
    input logic [4:0] qlevel_luma,
    input logic [4:0] qlevel_chroma,
    output logic signed [5:0] return_value
);
    integer signed qlevel_i;
    integer signed chroma_i;
    integer signed max_size_i;
    always_comb begin
        max_size_i = cpntBitDepth_selected;
        if ((cpnt % 3) == 0) begin
            qlevel_i = qlevel_luma;
        end else if ((native_420 != 0) && (cpnt == 1)) begin
            qlevel_i = qlevel_luma;
        end else begin
            chroma_i = qlevel_chroma;
            if ((dsc_version_minor == 2) && (cpntBitDepth_0 == ((cpnt == 1) ? cpntBitDepth_selected : cpntBitDepth_1))) begin
                chroma_i = chroma_i - 1;
            end
            qlevel_i = chroma_i < 0 ? 0 : chroma_i;
        end
        max_size_i = max_size_i - qlevel_i;
        return_value = max_size_i;
    end
endmodule

module predictsize (
    input logic [4:0] req_size_0,
    input logic [4:0] req_size_1,
    input logic [4:0] req_size_2,
    output logic [4:0] return_value
);
    assign return_value = ((req_size_0 + req_size_1 + (2 * req_size_2) + 2) >> 2);
endmodule

module mapqptoqlevel (
    input logic [1:0] cpnt,
    input logic [4:0] qp,
    input logic [1:0] dsc_version_minor,
    input logic native_420,
    input logic [4:0] cpntBitDepth_0,
    input logic [4:0] cpntBitDepth_1,
    input logic [4:0] qlevel_luma,
    input logic [4:0] qlevel_chroma,
    output logic [4:0] return_value
);
    integer signed qlevel_i;
    always_comb begin
        if ((cpnt % 3) == 0) begin
            qlevel_i = qlevel_luma;
        end else if ((native_420 != 0) && (cpnt == 1)) begin
            qlevel_i = qlevel_luma;
        end else begin
            qlevel_i = qlevel_chroma;
            if ((dsc_version_minor == 2) && (cpntBitDepth_0 == cpntBitDepth_1) && (qlevel_i > 0)) begin
                qlevel_i = qlevel_i - 1;
            end
        end
        return_value = qlevel_i;
    end
endmodule

module findresidualsize (
    input logic signed [16:0] eq,
    output logic [4:0] return_value
);
    integer signed eq_i;
    always_comb begin
        eq_i = $signed({{15{eq[16]}}, eq});
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

module vldunit_decode_transition(
    input logic signed [31:0] unit,
    input logic signed [31:0] cfg_bits_per_component,
    input logic signed [31:0] cfg_somewhat_flat_qp_thresh,
    input logic signed [31:0] cfg_dsc_version_minor,
    input logic signed [31:0] cfg_native_420,
    input logic signed [31:0] cfg_flatness_min_qp,
    input logic signed [31:0] cfg_flatness_max_qp,
    input logic signed [31:0] state_firstflat,
    input logic signed [31:0] state_flatnesstype,
    input logic signed [31:0] state_groupcount,
    input logic signed [31:0] state_ichindicesingroup,
    input logic signed [31:0] state_ichselected,
    input logic signed [31:0] state_prevfirstflat,
    input logic signed [31:0] state_previchselected,
    input logic signed [31:0] state_primaryqp,
    input logic signed [31:0] state_prevprimaryqp,
    input logic signed [31:0] state_unitspergroup,
    input logic signed [31:0] state_numbits,
    input logic signed [31:0] state_cpntbitdepth_0,
    input logic signed [31:0] state_cpntbitdepth_1,
    input logic signed [31:0] state_cpntbitdepth_2,
    input logic signed [31:0] state_cpntbitdepth_3,
    input logic signed [31:0] state_unitctype_0,
    input logic signed [31:0] state_unitctype_1,
    input logic signed [31:0] state_unitctype_2,
    input logic signed [31:0] state_unitctype_3,
    input logic signed [31:0] state_unitsspmap_0,
    input logic signed [31:0] state_unitsspmap_1,
    input logic signed [31:0] state_unitsspmap_2,
    input logic signed [31:0] state_unitsspmap_3,
    input logic signed [31:0] state_ichindexunitmap_0,
    input logic signed [31:0] state_ichindexunitmap_1,
    input logic signed [31:0] state_ichindexunitmap_2,
    input logic signed [31:0] state_ichindexunitmap_3,
    input logic signed [31:0] state_ichindexunitmap_4,
    input logic signed [31:0] state_ichindexunitmap_5,
    input logic signed [31:0] state_ichlookup_0,
    input logic signed [31:0] state_ichlookup_1,
    input logic signed [31:0] state_ichlookup_2,
    input logic signed [31:0] state_ichlookup_3,
    input logic signed [31:0] state_ichlookup_4,
    input logic signed [31:0] state_ichlookup_5,
    input logic signed [31:0] state_predictedsize_0,
    input logic signed [31:0] state_predictedsize_1,
    input logic signed [31:0] state_predictedsize_2,
    input logic signed [31:0] state_predictedsize_3,
    input logic signed [31:0] state_rcsizeunit_0,
    input logic signed [31:0] state_rcsizeunit_1,
    input logic signed [31:0] state_rcsizeunit_2,
    input logic signed [31:0] state_rcsizeunit_3,
    input logic signed [31:0] state_usemidpoint_0,
    input logic signed [31:0] state_usemidpoint_1,
    input logic signed [31:0] state_usemidpoint_2,
    input logic signed [31:0] state_usemidpoint_3,
    input logic signed [31:0] qlevel_luma_primary,
    input logic signed [31:0] qlevel_chroma_primary,
    input logic signed [31:0] qlevel_luma_previous,
    input logic signed [31:0] qlevel_chroma_previous,
    input logic signed [31:0] quantized_residual_0,
    input logic signed [31:0] quantized_residual_1,
    input logic signed [31:0] quantized_residual_2,
    input logic signed [31:0] fifo_size,
    input logic signed [31:0] fifo_fullness,
    input logic signed [31:0] fifo_read_ptr,
    input logic [7:0] fifo_byte_0,
    input logic [7:0] fifo_byte_1,
    input logic [7:0] fifo_byte_2,
    input logic [7:0] fifo_byte_3,
    input logic [7:0] fifo_byte_4,
    input logic [7:0] fifo_byte_5,
    input logic [7:0] fifo_byte_6,
    input logic [7:0] fifo_byte_7,
    input logic [7:0] fifo_byte_8,
    input logic [7:0] fifo_byte_9,
    input logic [7:0] fifo_byte_10,
    input logic [7:0] fifo_byte_11,
    input logic [7:0] fifo_byte_12,
    input logic [7:0] fifo_byte_13,
    input logic [7:0] fifo_byte_14,
    input logic [7:0] fifo_byte_15,
    input logic [7:0] fifo_byte_16,
    output logic domain_valid,
    output logic signed [31:0] state_firstflat_out,
    output logic signed [31:0] state_flatnesstype_out,
    output logic signed [31:0] state_ichselected_out,
    output logic signed [31:0] state_prevfirstflat_out,
    output logic signed [31:0] state_previchselected_out,
    output logic signed [31:0] state_numbits_out,
    output logic signed [31:0] state_ichlookup_0_out,
    output logic signed [31:0] state_ichlookup_1_out,
    output logic signed [31:0] state_ichlookup_2_out,
    output logic signed [31:0] state_ichlookup_3_out,
    output logic signed [31:0] state_ichlookup_4_out,
    output logic signed [31:0] state_ichlookup_5_out,
    output logic signed [31:0] state_predictedsize_0_out,
    output logic signed [31:0] state_predictedsize_1_out,
    output logic signed [31:0] state_predictedsize_2_out,
    output logic signed [31:0] state_predictedsize_3_out,
    output logic signed [31:0] state_rcsizeunit_0_out,
    output logic signed [31:0] state_rcsizeunit_1_out,
    output logic signed [31:0] state_rcsizeunit_2_out,
    output logic signed [31:0] state_rcsizeunit_3_out,
    output logic signed [31:0] state_usemidpoint_0_out,
    output logic signed [31:0] state_usemidpoint_1_out,
    output logic signed [31:0] state_usemidpoint_2_out,
    output logic signed [31:0] state_usemidpoint_3_out,
    output logic signed [31:0] quantized_residual_0_out,
    output logic signed [31:0] quantized_residual_1_out,
    output logic signed [31:0] quantized_residual_2_out,
    output logic signed [31:0] fifo_lane_out,
    output logic signed [31:0] fifo_fullness_out,
    output logic signed [31:0] fifo_read_ptr_out
);
    logic signed [31:0] cpnt_i;
    logic signed [31:0] ssp_i;
    logic signed [31:0] predicted_selected_i;
    logic signed [31:0] depth_selected_i;
    logic signed [31:0] qlevel_i;
    logic signed [31:0] adj_predicted_i;
    logic signed [31:0] max_prefix_i;
    logic signed [31:0] prefix_limit_i;
    logic signed [31:0] old_max_prefix_i;
    logic signed [31:0] prefix_value_i;
    logic signed [31:0] size_i;
    logic signed [31:0] max_size_i;
    logic signed [31:0] read_value_i;
    logic signed [31:0] req_0_i;
    logic signed [31:0] req_1_i;
    logic signed [31:0] req_2_i;
    logic done_i;
    logic prefix_stop_i;
    logic special_cap_i;
    logic ich_disallow_i;
    logic use_ich_i;
    logic midpoint_i;
    logic [32:0] read_sum_i;
    logic [135:0] fifo_data_i;
    logic [4:0] qlevel_leaf_i;
    logic signed [4:0] adjusted_leaf_i;
    logic signed [5:0] max_residual_leaf_i;
    logic signed [5:0] escape_leaf_i;
    logic flatness_sent_i;
    logic [4:0] required_0_leaf_i;
    logic [4:0] required_1_leaf_i;
    logic [4:0] required_2_leaf_i;
    logic [4:0] predicted_leaf_i;

    assign cpnt_i = ((unit == 32'sd0) ? state_unitctype_0 : ((unit == 32'sd1) ? state_unitctype_1 : ((unit == 32'sd2) ? state_unitctype_2 : state_unitctype_3)));
    assign ssp_i = ((unit == 32'sd0) ? state_unitsspmap_0 : ((unit == 32'sd1) ? state_unitsspmap_1 : ((unit == 32'sd2) ? state_unitsspmap_2 : state_unitsspmap_3)));
    assign predicted_selected_i = ((unit == 32'sd0) ? state_predictedsize_0 : ((unit == 32'sd1) ? state_predictedsize_1 : ((unit == 32'sd2) ? state_predictedsize_2 : state_predictedsize_3)));
    assign depth_selected_i = ((cpnt_i == 32'sd0) ? state_cpntbitdepth_0 : ((cpnt_i == 32'sd1) ? state_cpntbitdepth_1 : ((cpnt_i == 32'sd2) ? state_cpntbitdepth_2 : state_cpntbitdepth_3)));
    assign fifo_data_i = {fifo_byte_0, fifo_byte_1, fifo_byte_2, fifo_byte_3, fifo_byte_4, fifo_byte_5, fifo_byte_6, fifo_byte_7, fifo_byte_8, fifo_byte_9, fifo_byte_10, fifo_byte_11, fifo_byte_12, fifo_byte_13, fifo_byte_14, fifo_byte_15, fifo_byte_16};

    mapqptoqlevel u_qp_mapping(
        .cpnt(cpnt_i[1:0]), .qp(state_primaryqp[4:0]),
        .dsc_version_minor(cfg_dsc_version_minor[1:0]),
        .native_420(cfg_native_420[0]),
        .cpntBitDepth_0(state_cpntbitdepth_0[4:0]),
        .cpntBitDepth_1(state_cpntbitdepth_1[4:0]),
        .qlevel_luma(qlevel_luma_primary[4:0]),
        .qlevel_chroma(qlevel_chroma_primary[4:0]),
        .return_value(qlevel_leaf_i));

    getqpadjpredsize u_adjusted_prediction(
        .unit(unit[1:0]), .dsc_version_minor(cfg_dsc_version_minor[1:0]),
        .native_420(cfg_native_420[0]),
        .unit_c_type_selected(cpnt_i[1:0]),
        .predicted_size_selected(predicted_selected_i[4:0]),
        .primary_qp(state_primaryqp[4:0]),
        .prev_primary_qp(state_prevprimaryqp[4:0]),
        .cpntBitDepth_0(state_cpntbitdepth_0[4:0]),
        .cpntBitDepth_1(state_cpntbitdepth_1[4:0]),
        .cpntBitDepth_2(state_cpntbitdepth_2[4:0]),
        .cpntBitDepth_3(state_cpntbitdepth_3[4:0]),
        .qlevel_luma_new(qlevel_luma_primary[4:0]),
        .qlevel_chroma_new(qlevel_chroma_primary[4:0]),
        .qlevel_luma_old(qlevel_luma_previous[4:0]),
        .qlevel_chroma_old(qlevel_chroma_previous[4:0]),
        .return_value(adjusted_leaf_i));

    maxresidualsize u_max_residual(
        .cpnt(cpnt_i[1:0]), .qp(state_primaryqp[4:0]),
        .dsc_version_minor(cfg_dsc_version_minor[1:0]),
        .native_420(cfg_native_420[0]),
        .cpntBitDepth_0(state_cpntbitdepth_0[4:0]),
        .cpntBitDepth_1(state_cpntbitdepth_1[4:0]),
        .cpntBitDepth_selected(depth_selected_i[4:0]),
        .qlevel_luma(qlevel_luma_primary[4:0]),
        .qlevel_chroma(qlevel_chroma_primary[4:0]),
        .return_value(max_residual_leaf_i));

    escapecodesize u_escape_size(
        .qp(state_primaryqp[4:0]),
        .dsc_version_minor(cfg_dsc_version_minor[1:0]),
        .native_420(cfg_native_420[0]),
        .cpntBitDepth_0(state_cpntbitdepth_0[4:0]),
        .qlevel_luma(qlevel_luma_primary[4:0]),
        .return_value(escape_leaf_i));

    isflatnessinfosent u_flatness_sent(
        .qp(state_primaryqp[4:0]),
        .flatness_min_qp(cfg_flatness_min_qp[4:0]),
        .flatness_max_qp(cfg_flatness_max_qp[4:0]),
        .return_value(flatness_sent_i));

    findresidualsize u_residual_size_0(
        .eq(quantized_residual_0_out[16:0]),
        .return_value(required_0_leaf_i));

    findresidualsize u_residual_size_1(
        .eq(quantized_residual_1_out[16:0]),
        .return_value(required_1_leaf_i));

    findresidualsize u_residual_size_2(
        .eq(quantized_residual_2_out[16:0]),
        .return_value(required_2_leaf_i));

    predictsize u_predict_size(
        .req_size_0(req_0_i[4:0]), .req_size_1(req_1_i[4:0]),
        .req_size_2(req_2_i[4:0]), .return_value(predicted_leaf_i));

    function automatic signed [31:0] dsc_cicd_read_bits(
        input logic [135:0] data_i,
        input logic signed [31:0] size_i,
        input logic signed [31:0] pointer_i,
        input logic signed [31:0] count_i,
        input logic sign_i);
        integer bit_i;
        integer position_i;
        logic signed [31:0] value_i;
        begin
            value_i = 32'sd0;
            for (bit_i = 0; bit_i < 32; bit_i = bit_i + 1) begin
                if (bit_i < count_i) begin
                    position_i = pointer_i + bit_i;
                    if (position_i >= size_i) position_i = position_i - size_i;
                    if ((position_i >= 0) && (position_i < 136))
                        value_i = (value_i <<< 1) | data_i[135 - position_i];
                end
            end
            if (sign_i && (count_i > 0) && value_i[count_i-1])
                value_i = value_i | (32'hffffffff << count_i);
            dsc_cicd_read_bits = value_i;
        end
    endfunction

    always_comb begin
        state_firstflat_out = state_firstflat;
        state_flatnesstype_out = state_flatnesstype;
        state_ichselected_out = state_ichselected;
        state_prevfirstflat_out = state_prevfirstflat;
        state_previchselected_out = state_previchselected;
        state_numbits_out = state_numbits;
        state_ichlookup_0_out = state_ichlookup_0;
        state_ichlookup_1_out = state_ichlookup_1;
        state_ichlookup_2_out = state_ichlookup_2;
        state_ichlookup_3_out = state_ichlookup_3;
        state_ichlookup_4_out = state_ichlookup_4;
        state_ichlookup_5_out = state_ichlookup_5;
        state_predictedsize_0_out = state_predictedsize_0;
        state_predictedsize_1_out = state_predictedsize_1;
        state_predictedsize_2_out = state_predictedsize_2;
        state_predictedsize_3_out = state_predictedsize_3;
        state_rcsizeunit_0_out = state_rcsizeunit_0;
        state_rcsizeunit_1_out = state_rcsizeunit_1;
        state_rcsizeunit_2_out = state_rcsizeunit_2;
        state_rcsizeunit_3_out = state_rcsizeunit_3;
        state_usemidpoint_0_out = state_usemidpoint_0;
        state_usemidpoint_1_out = state_usemidpoint_1;
        state_usemidpoint_2_out = state_usemidpoint_2;
        state_usemidpoint_3_out = state_usemidpoint_3;
        quantized_residual_0_out = quantized_residual_0;
        quantized_residual_1_out = quantized_residual_1;
        quantized_residual_2_out = quantized_residual_2;
        fifo_lane_out = ssp_i;
        fifo_fullness_out = fifo_fullness;
        fifo_read_ptr_out = fifo_read_ptr;
        domain_valid = 1'b1;
        done_i = 1'b0;
        prefix_stop_i = 1'b0;
        special_cap_i = 1'b0;
        prefix_value_i = 32'sd0;
        prefix_limit_i = 32'sd0;
        old_max_prefix_i = 32'sd0;
        size_i = 32'sd0;
        max_size_i = 32'sd0;
        read_value_i = 32'sd0;
        read_sum_i = 33'd0;
        max_prefix_i = 32'sd0;
        req_0_i = 32'sd0; req_1_i = 32'sd0; req_2_i = 32'sd0;
        use_ich_i = 1'b0; midpoint_i = 1'b0;
        qlevel_i = $signed({27'd0, qlevel_leaf_i});
        adj_predicted_i = $signed(adjusted_leaf_i);
        ich_disallow_i = (cfg_bits_per_component == 32'sd16) && (unit == 0) && ((32'sd3 * qlevel_i) <= (32'sd3 - adj_predicted_i));
        if ((unit < 0) || (unit >= 32'sd4) || (cpnt_i < 0) || (cpnt_i >= 32'sd4) || (ssp_i < 0) || (ssp_i >= 32'sd4) || (state_unitspergroup < 0) || (state_unitspergroup > 32'sd4) || (state_ichindicesingroup < 0) || (state_ichindicesingroup > 32'sd6) || (fifo_size <= 0) || (fifo_size > 32'sd136) || ((fifo_size & 32'sd7) != 0)) domain_valid = 1'b0;
        if (unit == 0) begin
            state_previchselected_out = state_ichselected;
            state_ichselected_out = 32'sd0;
        end
        if ((unit == 0) && (state_groupcount[1:0] == 2'd3)) begin
            if (flatness_sent_i) begin
                if ((32'sd1 < 0) || (32'sd1 > 32) || (fifo_fullness_out < 32'sd1)) domain_valid = 1'b0;
                read_value_i = dsc_cicd_read_bits(fifo_data_i, fifo_size, fifo_read_ptr_out, 32'sd1, 1'b0);
                state_numbits_out = state_numbits_out + 32'sd1;
                fifo_fullness_out = fifo_fullness_out - 32'sd1;
                read_sum_i = {1'b0, fifo_read_ptr_out} + 32'sd1;
                if (read_sum_i >= {1'b0, fifo_size})
                    fifo_read_ptr_out = read_sum_i[31:0] - fifo_size;
                else fifo_read_ptr_out = read_sum_i[31:0];
                state_prevfirstflat_out = (read_value_i != 0) ? 32'sd0 : -32'sd1;
            end else state_prevfirstflat_out = -32'sd1;
        end
        if ((unit == 0) && (state_groupcount[1:0] == 2'd0)) begin
            if (state_prevfirstflat_out >= 0) begin
                state_flatnesstype_out = 32'sd0;
                if (state_primaryqp >= cfg_somewhat_flat_qp_thresh) begin
                    if ((32'sd1 < 0) || (32'sd1 > 32) || (fifo_fullness_out < 32'sd1)) domain_valid = 1'b0;
                    read_value_i = dsc_cicd_read_bits(fifo_data_i, fifo_size, fifo_read_ptr_out, 32'sd1, 1'b0);
                    state_numbits_out = state_numbits_out + 32'sd1;
                    fifo_fullness_out = fifo_fullness_out - 32'sd1;
                    read_sum_i = {1'b0, fifo_read_ptr_out} + 32'sd1;
                    if (read_sum_i >= {1'b0, fifo_size})
                        fifo_read_ptr_out = read_sum_i[31:0] - fifo_size;
                    else fifo_read_ptr_out = read_sum_i[31:0];
                    state_flatnesstype_out = read_value_i;
                end
                if ((32'sd2 < 0) || (32'sd2 > 32) || (fifo_fullness_out < 32'sd2)) domain_valid = 1'b0;
                read_value_i = dsc_cicd_read_bits(fifo_data_i, fifo_size, fifo_read_ptr_out, 32'sd2, 1'b0);
                state_numbits_out = state_numbits_out + 32'sd2;
                fifo_fullness_out = fifo_fullness_out - 32'sd2;
                read_sum_i = {1'b0, fifo_read_ptr_out} + 32'sd2;
                if (read_sum_i >= {1'b0, fifo_size})
                    fifo_read_ptr_out = read_sum_i[31:0] - fifo_size;
                else fifo_read_ptr_out = read_sum_i[31:0];
                state_firstflat_out = read_value_i;
            end else state_firstflat_out = -32'sd1;
        end
        if (state_ichselected_out != 0) begin
            if ((32'sd0 < state_ichindicesingroup) && (state_ichindexunitmap_0 == unit)) begin
                if ((32'sd1 * 32'sd5 < 0) || (32'sd1 * 32'sd5 > 32) || (fifo_fullness_out < 32'sd1 * 32'sd5)) domain_valid = 1'b0;
                read_value_i = dsc_cicd_read_bits(fifo_data_i, fifo_size, fifo_read_ptr_out, 32'sd1 * 32'sd5, 1'b0);
                state_numbits_out = state_numbits_out + 32'sd1 * 32'sd5;
                fifo_fullness_out = fifo_fullness_out - 32'sd1 * 32'sd5;
                read_sum_i = {1'b0, fifo_read_ptr_out} + 32'sd1 * 32'sd5;
                if (read_sum_i >= {1'b0, fifo_size})
                    fifo_read_ptr_out = read_sum_i[31:0] - fifo_size;
                else fifo_read_ptr_out = read_sum_i[31:0];
                state_ichlookup_0_out = read_value_i;
            end
            if ((32'sd1 < state_ichindicesingroup) && (state_ichindexunitmap_1 == unit)) begin
                if ((32'sd1 * 32'sd5 < 0) || (32'sd1 * 32'sd5 > 32) || (fifo_fullness_out < 32'sd1 * 32'sd5)) domain_valid = 1'b0;
                read_value_i = dsc_cicd_read_bits(fifo_data_i, fifo_size, fifo_read_ptr_out, 32'sd1 * 32'sd5, 1'b0);
                state_numbits_out = state_numbits_out + 32'sd1 * 32'sd5;
                fifo_fullness_out = fifo_fullness_out - 32'sd1 * 32'sd5;
                read_sum_i = {1'b0, fifo_read_ptr_out} + 32'sd1 * 32'sd5;
                if (read_sum_i >= {1'b0, fifo_size})
                    fifo_read_ptr_out = read_sum_i[31:0] - fifo_size;
                else fifo_read_ptr_out = read_sum_i[31:0];
                state_ichlookup_1_out = read_value_i;
            end
            if ((32'sd2 < state_ichindicesingroup) && (state_ichindexunitmap_2 == unit)) begin
                if ((32'sd1 * 32'sd5 < 0) || (32'sd1 * 32'sd5 > 32) || (fifo_fullness_out < 32'sd1 * 32'sd5)) domain_valid = 1'b0;
                read_value_i = dsc_cicd_read_bits(fifo_data_i, fifo_size, fifo_read_ptr_out, 32'sd1 * 32'sd5, 1'b0);
                state_numbits_out = state_numbits_out + 32'sd1 * 32'sd5;
                fifo_fullness_out = fifo_fullness_out - 32'sd1 * 32'sd5;
                read_sum_i = {1'b0, fifo_read_ptr_out} + 32'sd1 * 32'sd5;
                if (read_sum_i >= {1'b0, fifo_size})
                    fifo_read_ptr_out = read_sum_i[31:0] - fifo_size;
                else fifo_read_ptr_out = read_sum_i[31:0];
                state_ichlookup_2_out = read_value_i;
            end
            if ((32'sd3 < state_ichindicesingroup) && (state_ichindexunitmap_3 == unit)) begin
                if ((32'sd1 * 32'sd5 < 0) || (32'sd1 * 32'sd5 > 32) || (fifo_fullness_out < 32'sd1 * 32'sd5)) domain_valid = 1'b0;
                read_value_i = dsc_cicd_read_bits(fifo_data_i, fifo_size, fifo_read_ptr_out, 32'sd1 * 32'sd5, 1'b0);
                state_numbits_out = state_numbits_out + 32'sd1 * 32'sd5;
                fifo_fullness_out = fifo_fullness_out - 32'sd1 * 32'sd5;
                read_sum_i = {1'b0, fifo_read_ptr_out} + 32'sd1 * 32'sd5;
                if (read_sum_i >= {1'b0, fifo_size})
                    fifo_read_ptr_out = read_sum_i[31:0] - fifo_size;
                else fifo_read_ptr_out = read_sum_i[31:0];
                state_ichlookup_3_out = read_value_i;
            end
            if ((32'sd4 < state_ichindicesingroup) && (state_ichindexunitmap_4 == unit)) begin
                if ((32'sd1 * 32'sd5 < 0) || (32'sd1 * 32'sd5 > 32) || (fifo_fullness_out < 32'sd1 * 32'sd5)) domain_valid = 1'b0;
                read_value_i = dsc_cicd_read_bits(fifo_data_i, fifo_size, fifo_read_ptr_out, 32'sd1 * 32'sd5, 1'b0);
                state_numbits_out = state_numbits_out + 32'sd1 * 32'sd5;
                fifo_fullness_out = fifo_fullness_out - 32'sd1 * 32'sd5;
                read_sum_i = {1'b0, fifo_read_ptr_out} + 32'sd1 * 32'sd5;
                if (read_sum_i >= {1'b0, fifo_size})
                    fifo_read_ptr_out = read_sum_i[31:0] - fifo_size;
                else fifo_read_ptr_out = read_sum_i[31:0];
                state_ichlookup_4_out = read_value_i;
            end
            if ((32'sd5 < state_ichindicesingroup) && (state_ichindexunitmap_5 == unit)) begin
                if ((32'sd1 * 32'sd5 < 0) || (32'sd1 * 32'sd5 > 32) || (fifo_fullness_out < 32'sd1 * 32'sd5)) domain_valid = 1'b0;
                read_value_i = dsc_cicd_read_bits(fifo_data_i, fifo_size, fifo_read_ptr_out, 32'sd1 * 32'sd5, 1'b0);
                state_numbits_out = state_numbits_out + 32'sd1 * 32'sd5;
                fifo_fullness_out = fifo_fullness_out - 32'sd1 * 32'sd5;
                read_sum_i = {1'b0, fifo_read_ptr_out} + 32'sd1 * 32'sd5;
                if (read_sum_i >= {1'b0, fifo_size})
                    fifo_read_ptr_out = read_sum_i[31:0] - fifo_size;
                else fifo_read_ptr_out = read_sum_i[31:0];
                state_ichlookup_5_out = read_value_i;
            end
            done_i = 1'b1;
        end
        if (!done_i) begin
            max_prefix_i = $signed(max_residual_leaf_i) + (((unit == 0) && !ich_disallow_i) ? 32'sd1 : 32'sd0) - adj_predicted_i;
            old_max_prefix_i = max_prefix_i;
            prefix_limit_i = max_prefix_i;
            if ((cfg_bits_per_component == 32'sd16) && (unit == 0) && (qlevel_i == 0) && ich_disallow_i && ((max_prefix_i + 32'sd48) > 32'sd61)) begin
                prefix_limit_i = 32'sd13;
                special_cap_i = 1'b1;
            end
            if (!prefix_stop_i && (prefix_value_i < prefix_limit_i)) begin
                if ((32'sd1 < 0) || (32'sd1 > 32) || (fifo_fullness_out < 32'sd1)) domain_valid = 1'b0;
                read_value_i = dsc_cicd_read_bits(fifo_data_i, fifo_size, fifo_read_ptr_out, 32'sd1, 1'b0);
                state_numbits_out = state_numbits_out + 32'sd1;
                fifo_fullness_out = fifo_fullness_out - 32'sd1;
                read_sum_i = {1'b0, fifo_read_ptr_out} + 32'sd1;
                if (read_sum_i >= {1'b0, fifo_size})
                    fifo_read_ptr_out = read_sum_i[31:0] - fifo_size;
                else fifo_read_ptr_out = read_sum_i[31:0];
                if (read_value_i == 0) prefix_value_i = prefix_value_i + 1;
                else prefix_stop_i = 1'b1;
            end
            if (!prefix_stop_i && (prefix_value_i < prefix_limit_i)) begin
                if ((32'sd1 < 0) || (32'sd1 > 32) || (fifo_fullness_out < 32'sd1)) domain_valid = 1'b0;
                read_value_i = dsc_cicd_read_bits(fifo_data_i, fifo_size, fifo_read_ptr_out, 32'sd1, 1'b0);
                state_numbits_out = state_numbits_out + 32'sd1;
                fifo_fullness_out = fifo_fullness_out - 32'sd1;
                read_sum_i = {1'b0, fifo_read_ptr_out} + 32'sd1;
                if (read_sum_i >= {1'b0, fifo_size})
                    fifo_read_ptr_out = read_sum_i[31:0] - fifo_size;
                else fifo_read_ptr_out = read_sum_i[31:0];
                if (read_value_i == 0) prefix_value_i = prefix_value_i + 1;
                else prefix_stop_i = 1'b1;
            end
            if (!prefix_stop_i && (prefix_value_i < prefix_limit_i)) begin
                if ((32'sd1 < 0) || (32'sd1 > 32) || (fifo_fullness_out < 32'sd1)) domain_valid = 1'b0;
                read_value_i = dsc_cicd_read_bits(fifo_data_i, fifo_size, fifo_read_ptr_out, 32'sd1, 1'b0);
                state_numbits_out = state_numbits_out + 32'sd1;
                fifo_fullness_out = fifo_fullness_out - 32'sd1;
                read_sum_i = {1'b0, fifo_read_ptr_out} + 32'sd1;
                if (read_sum_i >= {1'b0, fifo_size})
                    fifo_read_ptr_out = read_sum_i[31:0] - fifo_size;
                else fifo_read_ptr_out = read_sum_i[31:0];
                if (read_value_i == 0) prefix_value_i = prefix_value_i + 1;
                else prefix_stop_i = 1'b1;
            end
            if (!prefix_stop_i && (prefix_value_i < prefix_limit_i)) begin
                if ((32'sd1 < 0) || (32'sd1 > 32) || (fifo_fullness_out < 32'sd1)) domain_valid = 1'b0;
                read_value_i = dsc_cicd_read_bits(fifo_data_i, fifo_size, fifo_read_ptr_out, 32'sd1, 1'b0);
                state_numbits_out = state_numbits_out + 32'sd1;
                fifo_fullness_out = fifo_fullness_out - 32'sd1;
                read_sum_i = {1'b0, fifo_read_ptr_out} + 32'sd1;
                if (read_sum_i >= {1'b0, fifo_size})
                    fifo_read_ptr_out = read_sum_i[31:0] - fifo_size;
                else fifo_read_ptr_out = read_sum_i[31:0];
                if (read_value_i == 0) prefix_value_i = prefix_value_i + 1;
                else prefix_stop_i = 1'b1;
            end
            if (!prefix_stop_i && (prefix_value_i < prefix_limit_i)) begin
                if ((32'sd1 < 0) || (32'sd1 > 32) || (fifo_fullness_out < 32'sd1)) domain_valid = 1'b0;
                read_value_i = dsc_cicd_read_bits(fifo_data_i, fifo_size, fifo_read_ptr_out, 32'sd1, 1'b0);
                state_numbits_out = state_numbits_out + 32'sd1;
                fifo_fullness_out = fifo_fullness_out - 32'sd1;
                read_sum_i = {1'b0, fifo_read_ptr_out} + 32'sd1;
                if (read_sum_i >= {1'b0, fifo_size})
                    fifo_read_ptr_out = read_sum_i[31:0] - fifo_size;
                else fifo_read_ptr_out = read_sum_i[31:0];
                if (read_value_i == 0) prefix_value_i = prefix_value_i + 1;
                else prefix_stop_i = 1'b1;
            end
            if (!prefix_stop_i && (prefix_value_i < prefix_limit_i)) begin
                if ((32'sd1 < 0) || (32'sd1 > 32) || (fifo_fullness_out < 32'sd1)) domain_valid = 1'b0;
                read_value_i = dsc_cicd_read_bits(fifo_data_i, fifo_size, fifo_read_ptr_out, 32'sd1, 1'b0);
                state_numbits_out = state_numbits_out + 32'sd1;
                fifo_fullness_out = fifo_fullness_out - 32'sd1;
                read_sum_i = {1'b0, fifo_read_ptr_out} + 32'sd1;
                if (read_sum_i >= {1'b0, fifo_size})
                    fifo_read_ptr_out = read_sum_i[31:0] - fifo_size;
                else fifo_read_ptr_out = read_sum_i[31:0];
                if (read_value_i == 0) prefix_value_i = prefix_value_i + 1;
                else prefix_stop_i = 1'b1;
            end
            if (!prefix_stop_i && (prefix_value_i < prefix_limit_i)) begin
                if ((32'sd1 < 0) || (32'sd1 > 32) || (fifo_fullness_out < 32'sd1)) domain_valid = 1'b0;
                read_value_i = dsc_cicd_read_bits(fifo_data_i, fifo_size, fifo_read_ptr_out, 32'sd1, 1'b0);
                state_numbits_out = state_numbits_out + 32'sd1;
                fifo_fullness_out = fifo_fullness_out - 32'sd1;
                read_sum_i = {1'b0, fifo_read_ptr_out} + 32'sd1;
                if (read_sum_i >= {1'b0, fifo_size})
                    fifo_read_ptr_out = read_sum_i[31:0] - fifo_size;
                else fifo_read_ptr_out = read_sum_i[31:0];
                if (read_value_i == 0) prefix_value_i = prefix_value_i + 1;
                else prefix_stop_i = 1'b1;
            end
            if (!prefix_stop_i && (prefix_value_i < prefix_limit_i)) begin
                if ((32'sd1 < 0) || (32'sd1 > 32) || (fifo_fullness_out < 32'sd1)) domain_valid = 1'b0;
                read_value_i = dsc_cicd_read_bits(fifo_data_i, fifo_size, fifo_read_ptr_out, 32'sd1, 1'b0);
                state_numbits_out = state_numbits_out + 32'sd1;
                fifo_fullness_out = fifo_fullness_out - 32'sd1;
                read_sum_i = {1'b0, fifo_read_ptr_out} + 32'sd1;
                if (read_sum_i >= {1'b0, fifo_size})
                    fifo_read_ptr_out = read_sum_i[31:0] - fifo_size;
                else fifo_read_ptr_out = read_sum_i[31:0];
                if (read_value_i == 0) prefix_value_i = prefix_value_i + 1;
                else prefix_stop_i = 1'b1;
            end
            if (!prefix_stop_i && (prefix_value_i < prefix_limit_i)) begin
                if ((32'sd1 < 0) || (32'sd1 > 32) || (fifo_fullness_out < 32'sd1)) domain_valid = 1'b0;
                read_value_i = dsc_cicd_read_bits(fifo_data_i, fifo_size, fifo_read_ptr_out, 32'sd1, 1'b0);
                state_numbits_out = state_numbits_out + 32'sd1;
                fifo_fullness_out = fifo_fullness_out - 32'sd1;
                read_sum_i = {1'b0, fifo_read_ptr_out} + 32'sd1;
                if (read_sum_i >= {1'b0, fifo_size})
                    fifo_read_ptr_out = read_sum_i[31:0] - fifo_size;
                else fifo_read_ptr_out = read_sum_i[31:0];
                if (read_value_i == 0) prefix_value_i = prefix_value_i + 1;
                else prefix_stop_i = 1'b1;
            end
            if (!prefix_stop_i && (prefix_value_i < prefix_limit_i)) begin
                if ((32'sd1 < 0) || (32'sd1 > 32) || (fifo_fullness_out < 32'sd1)) domain_valid = 1'b0;
                read_value_i = dsc_cicd_read_bits(fifo_data_i, fifo_size, fifo_read_ptr_out, 32'sd1, 1'b0);
                state_numbits_out = state_numbits_out + 32'sd1;
                fifo_fullness_out = fifo_fullness_out - 32'sd1;
                read_sum_i = {1'b0, fifo_read_ptr_out} + 32'sd1;
                if (read_sum_i >= {1'b0, fifo_size})
                    fifo_read_ptr_out = read_sum_i[31:0] - fifo_size;
                else fifo_read_ptr_out = read_sum_i[31:0];
                if (read_value_i == 0) prefix_value_i = prefix_value_i + 1;
                else prefix_stop_i = 1'b1;
            end
            if (!prefix_stop_i && (prefix_value_i < prefix_limit_i)) begin
                if ((32'sd1 < 0) || (32'sd1 > 32) || (fifo_fullness_out < 32'sd1)) domain_valid = 1'b0;
                read_value_i = dsc_cicd_read_bits(fifo_data_i, fifo_size, fifo_read_ptr_out, 32'sd1, 1'b0);
                state_numbits_out = state_numbits_out + 32'sd1;
                fifo_fullness_out = fifo_fullness_out - 32'sd1;
                read_sum_i = {1'b0, fifo_read_ptr_out} + 32'sd1;
                if (read_sum_i >= {1'b0, fifo_size})
                    fifo_read_ptr_out = read_sum_i[31:0] - fifo_size;
                else fifo_read_ptr_out = read_sum_i[31:0];
                if (read_value_i == 0) prefix_value_i = prefix_value_i + 1;
                else prefix_stop_i = 1'b1;
            end
            if (!prefix_stop_i && (prefix_value_i < prefix_limit_i)) begin
                if ((32'sd1 < 0) || (32'sd1 > 32) || (fifo_fullness_out < 32'sd1)) domain_valid = 1'b0;
                read_value_i = dsc_cicd_read_bits(fifo_data_i, fifo_size, fifo_read_ptr_out, 32'sd1, 1'b0);
                state_numbits_out = state_numbits_out + 32'sd1;
                fifo_fullness_out = fifo_fullness_out - 32'sd1;
                read_sum_i = {1'b0, fifo_read_ptr_out} + 32'sd1;
                if (read_sum_i >= {1'b0, fifo_size})
                    fifo_read_ptr_out = read_sum_i[31:0] - fifo_size;
                else fifo_read_ptr_out = read_sum_i[31:0];
                if (read_value_i == 0) prefix_value_i = prefix_value_i + 1;
                else prefix_stop_i = 1'b1;
            end
            if (!prefix_stop_i && (prefix_value_i < prefix_limit_i)) begin
                if ((32'sd1 < 0) || (32'sd1 > 32) || (fifo_fullness_out < 32'sd1)) domain_valid = 1'b0;
                read_value_i = dsc_cicd_read_bits(fifo_data_i, fifo_size, fifo_read_ptr_out, 32'sd1, 1'b0);
                state_numbits_out = state_numbits_out + 32'sd1;
                fifo_fullness_out = fifo_fullness_out - 32'sd1;
                read_sum_i = {1'b0, fifo_read_ptr_out} + 32'sd1;
                if (read_sum_i >= {1'b0, fifo_size})
                    fifo_read_ptr_out = read_sum_i[31:0] - fifo_size;
                else fifo_read_ptr_out = read_sum_i[31:0];
                if (read_value_i == 0) prefix_value_i = prefix_value_i + 1;
                else prefix_stop_i = 1'b1;
            end
            if (!prefix_stop_i && (prefix_value_i < prefix_limit_i)) begin
                if ((32'sd1 < 0) || (32'sd1 > 32) || (fifo_fullness_out < 32'sd1)) domain_valid = 1'b0;
                read_value_i = dsc_cicd_read_bits(fifo_data_i, fifo_size, fifo_read_ptr_out, 32'sd1, 1'b0);
                state_numbits_out = state_numbits_out + 32'sd1;
                fifo_fullness_out = fifo_fullness_out - 32'sd1;
                read_sum_i = {1'b0, fifo_read_ptr_out} + 32'sd1;
                if (read_sum_i >= {1'b0, fifo_size})
                    fifo_read_ptr_out = read_sum_i[31:0] - fifo_size;
                else fifo_read_ptr_out = read_sum_i[31:0];
                if (read_value_i == 0) prefix_value_i = prefix_value_i + 1;
                else prefix_stop_i = 1'b1;
            end
            if (!prefix_stop_i && (prefix_value_i < prefix_limit_i)) begin
                if ((32'sd1 < 0) || (32'sd1 > 32) || (fifo_fullness_out < 32'sd1)) domain_valid = 1'b0;
                read_value_i = dsc_cicd_read_bits(fifo_data_i, fifo_size, fifo_read_ptr_out, 32'sd1, 1'b0);
                state_numbits_out = state_numbits_out + 32'sd1;
                fifo_fullness_out = fifo_fullness_out - 32'sd1;
                read_sum_i = {1'b0, fifo_read_ptr_out} + 32'sd1;
                if (read_sum_i >= {1'b0, fifo_size})
                    fifo_read_ptr_out = read_sum_i[31:0] - fifo_size;
                else fifo_read_ptr_out = read_sum_i[31:0];
                if (read_value_i == 0) prefix_value_i = prefix_value_i + 1;
                else prefix_stop_i = 1'b1;
            end
            if (!prefix_stop_i && (prefix_value_i < prefix_limit_i)) begin
                if ((32'sd1 < 0) || (32'sd1 > 32) || (fifo_fullness_out < 32'sd1)) domain_valid = 1'b0;
                read_value_i = dsc_cicd_read_bits(fifo_data_i, fifo_size, fifo_read_ptr_out, 32'sd1, 1'b0);
                state_numbits_out = state_numbits_out + 32'sd1;
                fifo_fullness_out = fifo_fullness_out - 32'sd1;
                read_sum_i = {1'b0, fifo_read_ptr_out} + 32'sd1;
                if (read_sum_i >= {1'b0, fifo_size})
                    fifo_read_ptr_out = read_sum_i[31:0] - fifo_size;
                else fifo_read_ptr_out = read_sum_i[31:0];
                if (read_value_i == 0) prefix_value_i = prefix_value_i + 1;
                else prefix_stop_i = 1'b1;
            end
            if (!prefix_stop_i && (prefix_value_i < prefix_limit_i)) begin
                if ((32'sd1 < 0) || (32'sd1 > 32) || (fifo_fullness_out < 32'sd1)) domain_valid = 1'b0;
                read_value_i = dsc_cicd_read_bits(fifo_data_i, fifo_size, fifo_read_ptr_out, 32'sd1, 1'b0);
                state_numbits_out = state_numbits_out + 32'sd1;
                fifo_fullness_out = fifo_fullness_out - 32'sd1;
                read_sum_i = {1'b0, fifo_read_ptr_out} + 32'sd1;
                if (read_sum_i >= {1'b0, fifo_size})
                    fifo_read_ptr_out = read_sum_i[31:0] - fifo_size;
                else fifo_read_ptr_out = read_sum_i[31:0];
                if (read_value_i == 0) prefix_value_i = prefix_value_i + 1;
                else prefix_stop_i = 1'b1;
            end
            if (special_cap_i && (prefix_value_i == prefix_limit_i))
                prefix_value_i = old_max_prefix_i;
            if ((unit == 0) && (state_previchselected_out != 0) && !ich_disallow_i)
                size_i = adj_predicted_i + prefix_value_i - 1;
            else size_i = adj_predicted_i + prefix_value_i;
            if (state_previchselected_out != 0)
                use_ich_i = !ich_disallow_i && (prefix_value_i == 0);
            else use_ich_i = !ich_disallow_i && (size_i >= $signed(escape_leaf_i));
            if ((unit == 0) && use_ich_i) begin
                state_ichselected_out = 32'sd1;
                state_rcsizeunit_0_out = 32'sd1 + (32'sd5 * state_ichindicesingroup);
                if (state_unitspergroup > 32'sd1)
                    state_rcsizeunit_1_out = 32'sd0;
                if (state_unitspergroup > 32'sd2)
                    state_rcsizeunit_2_out = 32'sd0;
                if (state_unitspergroup > 32'sd3)
                    state_rcsizeunit_3_out = 32'sd0;
                if ((32'sd0 < state_ichindicesingroup) && (state_ichindexunitmap_0 == unit)) begin
                    if ((32'sd5 < 0) || (32'sd5 > 32) || (fifo_fullness_out < 32'sd5)) domain_valid = 1'b0;
                    read_value_i = dsc_cicd_read_bits(fifo_data_i, fifo_size, fifo_read_ptr_out, 32'sd5, 1'b0);
                    state_numbits_out = state_numbits_out + 32'sd5;
                    fifo_fullness_out = fifo_fullness_out - 32'sd5;
                    read_sum_i = {1'b0, fifo_read_ptr_out} + 32'sd5;
                    if (read_sum_i >= {1'b0, fifo_size})
                        fifo_read_ptr_out = read_sum_i[31:0] - fifo_size;
                    else fifo_read_ptr_out = read_sum_i[31:0];
                    state_ichlookup_0_out = read_value_i;
                end
                if ((32'sd1 < state_ichindicesingroup) && (state_ichindexunitmap_1 == unit)) begin
                    if ((32'sd5 < 0) || (32'sd5 > 32) || (fifo_fullness_out < 32'sd5)) domain_valid = 1'b0;
                    read_value_i = dsc_cicd_read_bits(fifo_data_i, fifo_size, fifo_read_ptr_out, 32'sd5, 1'b0);
                    state_numbits_out = state_numbits_out + 32'sd5;
                    fifo_fullness_out = fifo_fullness_out - 32'sd5;
                    read_sum_i = {1'b0, fifo_read_ptr_out} + 32'sd5;
                    if (read_sum_i >= {1'b0, fifo_size})
                        fifo_read_ptr_out = read_sum_i[31:0] - fifo_size;
                    else fifo_read_ptr_out = read_sum_i[31:0];
                    state_ichlookup_1_out = read_value_i;
                end
                if ((32'sd2 < state_ichindicesingroup) && (state_ichindexunitmap_2 == unit)) begin
                    if ((32'sd5 < 0) || (32'sd5 > 32) || (fifo_fullness_out < 32'sd5)) domain_valid = 1'b0;
                    read_value_i = dsc_cicd_read_bits(fifo_data_i, fifo_size, fifo_read_ptr_out, 32'sd5, 1'b0);
                    state_numbits_out = state_numbits_out + 32'sd5;
                    fifo_fullness_out = fifo_fullness_out - 32'sd5;
                    read_sum_i = {1'b0, fifo_read_ptr_out} + 32'sd5;
                    if (read_sum_i >= {1'b0, fifo_size})
                        fifo_read_ptr_out = read_sum_i[31:0] - fifo_size;
                    else fifo_read_ptr_out = read_sum_i[31:0];
                    state_ichlookup_2_out = read_value_i;
                end
                if ((32'sd3 < state_ichindicesingroup) && (state_ichindexunitmap_3 == unit)) begin
                    if ((32'sd5 < 0) || (32'sd5 > 32) || (fifo_fullness_out < 32'sd5)) domain_valid = 1'b0;
                    read_value_i = dsc_cicd_read_bits(fifo_data_i, fifo_size, fifo_read_ptr_out, 32'sd5, 1'b0);
                    state_numbits_out = state_numbits_out + 32'sd5;
                    fifo_fullness_out = fifo_fullness_out - 32'sd5;
                    read_sum_i = {1'b0, fifo_read_ptr_out} + 32'sd5;
                    if (read_sum_i >= {1'b0, fifo_size})
                        fifo_read_ptr_out = read_sum_i[31:0] - fifo_size;
                    else fifo_read_ptr_out = read_sum_i[31:0];
                    state_ichlookup_3_out = read_value_i;
                end
                if ((32'sd4 < state_ichindicesingroup) && (state_ichindexunitmap_4 == unit)) begin
                    if ((32'sd5 < 0) || (32'sd5 > 32) || (fifo_fullness_out < 32'sd5)) domain_valid = 1'b0;
                    read_value_i = dsc_cicd_read_bits(fifo_data_i, fifo_size, fifo_read_ptr_out, 32'sd5, 1'b0);
                    state_numbits_out = state_numbits_out + 32'sd5;
                    fifo_fullness_out = fifo_fullness_out - 32'sd5;
                    read_sum_i = {1'b0, fifo_read_ptr_out} + 32'sd5;
                    if (read_sum_i >= {1'b0, fifo_size})
                        fifo_read_ptr_out = read_sum_i[31:0] - fifo_size;
                    else fifo_read_ptr_out = read_sum_i[31:0];
                    state_ichlookup_4_out = read_value_i;
                end
                if ((32'sd5 < state_ichindicesingroup) && (state_ichindexunitmap_5 == unit)) begin
                    if ((32'sd5 < 0) || (32'sd5 > 32) || (fifo_fullness_out < 32'sd5)) domain_valid = 1'b0;
                    read_value_i = dsc_cicd_read_bits(fifo_data_i, fifo_size, fifo_read_ptr_out, 32'sd5, 1'b0);
                    state_numbits_out = state_numbits_out + 32'sd5;
                    fifo_fullness_out = fifo_fullness_out - 32'sd5;
                    read_sum_i = {1'b0, fifo_read_ptr_out} + 32'sd5;
                    if (read_sum_i >= {1'b0, fifo_size})
                        fifo_read_ptr_out = read_sum_i[31:0] - fifo_size;
                    else fifo_read_ptr_out = read_sum_i[31:0];
                    state_ichlookup_5_out = read_value_i;
                end
                done_i = 1'b1;
            end
        end
        if (!done_i) begin
            midpoint_i = (size_i == ((((cpnt_i == 32'sd0) ? state_cpntbitdepth_0 : ((cpnt_i == 32'sd1) ? state_cpntbitdepth_1 : ((cpnt_i == 32'sd2) ? state_cpntbitdepth_2 : state_cpntbitdepth_3)))) - qlevel_i));
            if (unit == 32'sd0)
                state_usemidpoint_0_out = midpoint_i;
            if (unit == 32'sd1)
                state_usemidpoint_1_out = midpoint_i;
            if (unit == 32'sd2)
                state_usemidpoint_2_out = midpoint_i;
            if (unit == 32'sd3)
                state_usemidpoint_3_out = midpoint_i;
            if ((size_i < 0) || (size_i > 32) || (fifo_fullness_out < size_i)) domain_valid = 1'b0;
            quantized_residual_0_out = dsc_cicd_read_bits(fifo_data_i, fifo_size, fifo_read_ptr_out, size_i, 1'b1);
            state_numbits_out = state_numbits_out + size_i;
            fifo_fullness_out = fifo_fullness_out - size_i;
            read_sum_i = {1'b0, fifo_read_ptr_out} + size_i;
            if (read_sum_i >= {1'b0, fifo_size})
                fifo_read_ptr_out = read_sum_i[31:0] - fifo_size;
            else fifo_read_ptr_out = read_sum_i[31:0];
            if ((size_i < 0) || (size_i > 32) || (fifo_fullness_out < size_i)) domain_valid = 1'b0;
            quantized_residual_1_out = dsc_cicd_read_bits(fifo_data_i, fifo_size, fifo_read_ptr_out, size_i, 1'b1);
            state_numbits_out = state_numbits_out + size_i;
            fifo_fullness_out = fifo_fullness_out - size_i;
            read_sum_i = {1'b0, fifo_read_ptr_out} + size_i;
            if (read_sum_i >= {1'b0, fifo_size})
                fifo_read_ptr_out = read_sum_i[31:0] - fifo_size;
            else fifo_read_ptr_out = read_sum_i[31:0];
            if ((size_i < 0) || (size_i > 32) || (fifo_fullness_out < size_i)) domain_valid = 1'b0;
            quantized_residual_2_out = dsc_cicd_read_bits(fifo_data_i, fifo_size, fifo_read_ptr_out, size_i, 1'b1);
            state_numbits_out = state_numbits_out + size_i;
            fifo_fullness_out = fifo_fullness_out - size_i;
            read_sum_i = {1'b0, fifo_read_ptr_out} + size_i;
            if (read_sum_i >= {1'b0, fifo_size})
                fifo_read_ptr_out = read_sum_i[31:0] - fifo_size;
            else fifo_read_ptr_out = read_sum_i[31:0];
            req_0_i = $signed({27'd0, required_0_leaf_i});
            req_1_i = $signed({27'd0, required_1_leaf_i});
            req_2_i = $signed({27'd0, required_2_leaf_i});
            max_size_i = req_0_i;
            if (req_1_i > max_size_i) max_size_i = req_1_i;
            if (req_2_i > max_size_i) max_size_i = req_2_i;
            if (midpoint_i) begin
                max_size_i = size_i;
                req_0_i = size_i; req_1_i = size_i; req_2_i = size_i;
            end
            if (unit == 32'sd0) begin
                state_rcsizeunit_0_out = (max_size_i * 32'sd3) + 1;
                state_predictedsize_0_out = $signed({27'd0, predicted_leaf_i});
            end
            if (unit == 32'sd1) begin
                state_rcsizeunit_1_out = (max_size_i * 32'sd3) + 1;
                state_predictedsize_1_out = $signed({27'd0, predicted_leaf_i});
            end
            if (unit == 32'sd2) begin
                state_rcsizeunit_2_out = (max_size_i * 32'sd3) + 1;
                state_predictedsize_2_out = $signed({27'd0, predicted_leaf_i});
            end
            if (unit == 32'sd3) begin
                state_rcsizeunit_3_out = (max_size_i * 32'sd3) + 1;
                state_predictedsize_3_out = $signed({27'd0, predicted_leaf_i});
            end
        end
    end
endmodule

module vldgroup_decode_transition(
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
    input logic signed [31:0] cfg_bits_per_component,
    input logic signed [31:0] cfg_somewhat_flat_qp_thresh,
    input logic signed [31:0] cfg_dsc_version_minor,
    input logic signed [31:0] cfg_native_420,
    input logic signed [31:0] cfg_flatness_min_qp,
    input logic signed [31:0] cfg_flatness_max_qp,
    input logic signed [31:0] state_firstflat,
    input logic signed [31:0] state_flatnesstype,
    input logic signed [31:0] state_groupcount,
    input logic signed [31:0] state_ichindicesingroup,
    input logic signed [31:0] state_ichselected,
    input logic signed [31:0] state_prevfirstflat,
    input logic signed [31:0] state_previchselected,
    input logic signed [31:0] state_primaryqp,
    input logic signed [31:0] state_prevprimaryqp,
    input logic signed [31:0] state_unitspergroup,
    input logic signed [31:0] state_numbits,
    input logic signed [31:0] state_cpntbitdepth_0,
    input logic signed [31:0] state_cpntbitdepth_1,
    input logic signed [31:0] state_cpntbitdepth_2,
    input logic signed [31:0] state_cpntbitdepth_3,
    input logic signed [31:0] state_unitctype_0,
    input logic signed [31:0] state_unitctype_1,
    input logic signed [31:0] state_unitctype_2,
    input logic signed [31:0] state_unitctype_3,
    input logic signed [31:0] state_unitsspmap_0,
    input logic signed [31:0] state_unitsspmap_1,
    input logic signed [31:0] state_unitsspmap_2,
    input logic signed [31:0] state_unitsspmap_3,
    input logic signed [31:0] state_ichindexunitmap_0,
    input logic signed [31:0] state_ichindexunitmap_1,
    input logic signed [31:0] state_ichindexunitmap_2,
    input logic signed [31:0] state_ichindexunitmap_3,
    input logic signed [31:0] state_ichindexunitmap_4,
    input logic signed [31:0] state_ichindexunitmap_5,
    input logic signed [31:0] state_ichlookup_0,
    input logic signed [31:0] state_ichlookup_1,
    input logic signed [31:0] state_ichlookup_2,
    input logic signed [31:0] state_ichlookup_3,
    input logic signed [31:0] state_ichlookup_4,
    input logic signed [31:0] state_ichlookup_5,
    input logic signed [31:0] state_predictedsize_0,
    input logic signed [31:0] state_predictedsize_1,
    input logic signed [31:0] state_predictedsize_2,
    input logic signed [31:0] state_predictedsize_3,
    input logic signed [31:0] state_rcsizeunit_0,
    input logic signed [31:0] state_rcsizeunit_1,
    input logic signed [31:0] state_rcsizeunit_2,
    input logic signed [31:0] state_rcsizeunit_3,
    input logic signed [31:0] state_usemidpoint_0,
    input logic signed [31:0] state_usemidpoint_1,
    input logic signed [31:0] state_usemidpoint_2,
    input logic signed [31:0] state_usemidpoint_3,
    input logic signed [31:0] qlevel_luma_primary,
    input logic signed [31:0] qlevel_chroma_primary,
    input logic signed [31:0] qlevel_luma_previous,
    input logic signed [31:0] qlevel_chroma_previous,
    input logic signed [31:0] state_quantizedresidual_0_0,
    input logic signed [31:0] state_quantizedresidual_0_1,
    input logic signed [31:0] state_quantizedresidual_0_2,
    input logic signed [31:0] state_quantizedresidual_1_0,
    input logic signed [31:0] state_quantizedresidual_1_1,
    input logic signed [31:0] state_quantizedresidual_1_2,
    input logic signed [31:0] state_quantizedresidual_2_0,
    input logic signed [31:0] state_quantizedresidual_2_1,
    input logic signed [31:0] state_quantizedresidual_2_2,
    input logic signed [31:0] state_quantizedresidual_3_0,
    input logic signed [31:0] state_quantizedresidual_3_1,
    input logic signed [31:0] state_quantizedresidual_3_2,
    input logic signed [31:0] cfg_rcb_bits,
    input logic signed [31:0] state_bufferfullness,
    input logic signed [31:0] state_erroroccurred,
    input logic signed [31:0] state_groupcountline,
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
    output logic [31:0] fifo_3_byte_ctr_out,
    output logic signed [31:0] state_firstflat_out,
    output logic signed [31:0] state_flatnesstype_out,
    output logic signed [31:0] state_ichselected_out,
    output logic signed [31:0] state_prevfirstflat_out,
    output logic signed [31:0] state_previchselected_out,
    output logic signed [31:0] state_numbits_out,
    output logic signed [31:0] state_ichlookup_0_out,
    output logic signed [31:0] state_ichlookup_1_out,
    output logic signed [31:0] state_ichlookup_2_out,
    output logic signed [31:0] state_ichlookup_3_out,
    output logic signed [31:0] state_ichlookup_4_out,
    output logic signed [31:0] state_ichlookup_5_out,
    output logic signed [31:0] state_predictedsize_0_out,
    output logic signed [31:0] state_predictedsize_1_out,
    output logic signed [31:0] state_predictedsize_2_out,
    output logic signed [31:0] state_predictedsize_3_out,
    output logic signed [31:0] state_rcsizeunit_0_out,
    output logic signed [31:0] state_rcsizeunit_1_out,
    output logic signed [31:0] state_rcsizeunit_2_out,
    output logic signed [31:0] state_rcsizeunit_3_out,
    output logic signed [31:0] state_usemidpoint_0_out,
    output logic signed [31:0] state_usemidpoint_1_out,
    output logic signed [31:0] state_usemidpoint_2_out,
    output logic signed [31:0] state_usemidpoint_3_out,
    output logic signed [31:0] state_quantizedresidual_0_0_out,
    output logic signed [31:0] state_quantizedresidual_0_1_out,
    output logic signed [31:0] state_quantizedresidual_0_2_out,
    output logic signed [31:0] state_quantizedresidual_1_0_out,
    output logic signed [31:0] state_quantizedresidual_1_1_out,
    output logic signed [31:0] state_quantizedresidual_1_2_out,
    output logic signed [31:0] state_quantizedresidual_2_0_out,
    output logic signed [31:0] state_quantizedresidual_2_1_out,
    output logic signed [31:0] state_quantizedresidual_2_2_out,
    output logic signed [31:0] state_quantizedresidual_3_0_out,
    output logic signed [31:0] state_quantizedresidual_3_1_out,
    output logic signed [31:0] state_quantizedresidual_3_2_out,
    output logic signed [31:0] state_prevprimaryqp_out,
    output logic signed [31:0] state_codedgroupsize_out,
    output logic signed [31:0] state_bufferfullness_out,
    output logic signed [31:0] state_erroroccurred_out,
    output logic signed [31:0] state_origisflat_out,
    output logic signed [31:0] state_groupcountline_out
);
    logic mux_domain_valid_i;
    logic [31:0] mux_post_mux_num_bits_out_i;
    logic [7:0] mux_fifo_0_byte_0_out_i;
    logic [7:0] mux_fifo_0_byte_1_out_i;
    logic [7:0] mux_fifo_0_byte_2_out_i;
    logic [7:0] mux_fifo_0_byte_3_out_i;
    logic [7:0] mux_fifo_0_byte_4_out_i;
    logic [7:0] mux_fifo_0_byte_5_out_i;
    logic [7:0] mux_fifo_0_byte_6_out_i;
    logic [7:0] mux_fifo_0_byte_7_out_i;
    logic [7:0] mux_fifo_0_byte_8_out_i;
    logic [7:0] mux_fifo_0_byte_9_out_i;
    logic [7:0] mux_fifo_0_byte_10_out_i;
    logic [7:0] mux_fifo_0_byte_11_out_i;
    logic [7:0] mux_fifo_0_byte_12_out_i;
    logic [7:0] mux_fifo_0_byte_13_out_i;
    logic [7:0] mux_fifo_0_byte_14_out_i;
    logic [7:0] mux_fifo_0_byte_15_out_i;
    logic [7:0] mux_fifo_0_byte_16_out_i;
    logic [7:0] mux_fifo_1_byte_0_out_i;
    logic [7:0] mux_fifo_1_byte_1_out_i;
    logic [7:0] mux_fifo_1_byte_2_out_i;
    logic [7:0] mux_fifo_1_byte_3_out_i;
    logic [7:0] mux_fifo_1_byte_4_out_i;
    logic [7:0] mux_fifo_1_byte_5_out_i;
    logic [7:0] mux_fifo_1_byte_6_out_i;
    logic [7:0] mux_fifo_1_byte_7_out_i;
    logic [7:0] mux_fifo_1_byte_8_out_i;
    logic [7:0] mux_fifo_1_byte_9_out_i;
    logic [7:0] mux_fifo_1_byte_10_out_i;
    logic [7:0] mux_fifo_1_byte_11_out_i;
    logic [7:0] mux_fifo_1_byte_12_out_i;
    logic [7:0] mux_fifo_1_byte_13_out_i;
    logic [7:0] mux_fifo_1_byte_14_out_i;
    logic [7:0] mux_fifo_1_byte_15_out_i;
    logic [7:0] mux_fifo_1_byte_16_out_i;
    logic [7:0] mux_fifo_2_byte_0_out_i;
    logic [7:0] mux_fifo_2_byte_1_out_i;
    logic [7:0] mux_fifo_2_byte_2_out_i;
    logic [7:0] mux_fifo_2_byte_3_out_i;
    logic [7:0] mux_fifo_2_byte_4_out_i;
    logic [7:0] mux_fifo_2_byte_5_out_i;
    logic [7:0] mux_fifo_2_byte_6_out_i;
    logic [7:0] mux_fifo_2_byte_7_out_i;
    logic [7:0] mux_fifo_2_byte_8_out_i;
    logic [7:0] mux_fifo_2_byte_9_out_i;
    logic [7:0] mux_fifo_2_byte_10_out_i;
    logic [7:0] mux_fifo_2_byte_11_out_i;
    logic [7:0] mux_fifo_2_byte_12_out_i;
    logic [7:0] mux_fifo_2_byte_13_out_i;
    logic [7:0] mux_fifo_2_byte_14_out_i;
    logic [7:0] mux_fifo_2_byte_15_out_i;
    logic [7:0] mux_fifo_2_byte_16_out_i;
    logic [7:0] mux_fifo_3_byte_0_out_i;
    logic [7:0] mux_fifo_3_byte_1_out_i;
    logic [7:0] mux_fifo_3_byte_2_out_i;
    logic [7:0] mux_fifo_3_byte_3_out_i;
    logic [7:0] mux_fifo_3_byte_4_out_i;
    logic [7:0] mux_fifo_3_byte_5_out_i;
    logic [7:0] mux_fifo_3_byte_6_out_i;
    logic [7:0] mux_fifo_3_byte_7_out_i;
    logic [7:0] mux_fifo_3_byte_8_out_i;
    logic [7:0] mux_fifo_3_byte_9_out_i;
    logic [7:0] mux_fifo_3_byte_10_out_i;
    logic [7:0] mux_fifo_3_byte_11_out_i;
    logic [7:0] mux_fifo_3_byte_12_out_i;
    logic [7:0] mux_fifo_3_byte_13_out_i;
    logic [7:0] mux_fifo_3_byte_14_out_i;
    logic [7:0] mux_fifo_3_byte_15_out_i;
    logic [7:0] mux_fifo_3_byte_16_out_i;
    logic [31:0] mux_fifo_0_size_out_i;
    logic [31:0] mux_fifo_0_fullness_out_i;
    logic [31:0] mux_fifo_0_read_ptr_out_i;
    logic [31:0] mux_fifo_0_write_ptr_out_i;
    logic [31:0] mux_fifo_0_max_fullness_out_i;
    logic [31:0] mux_fifo_0_byte_ctr_out_i;
    logic [31:0] mux_fifo_1_size_out_i;
    logic [31:0] mux_fifo_1_fullness_out_i;
    logic [31:0] mux_fifo_1_read_ptr_out_i;
    logic [31:0] mux_fifo_1_write_ptr_out_i;
    logic [31:0] mux_fifo_1_max_fullness_out_i;
    logic [31:0] mux_fifo_1_byte_ctr_out_i;
    logic [31:0] mux_fifo_2_size_out_i;
    logic [31:0] mux_fifo_2_fullness_out_i;
    logic [31:0] mux_fifo_2_read_ptr_out_i;
    logic [31:0] mux_fifo_2_write_ptr_out_i;
    logic [31:0] mux_fifo_2_max_fullness_out_i;
    logic [31:0] mux_fifo_2_byte_ctr_out_i;
    logic [31:0] mux_fifo_3_size_out_i;
    logic [31:0] mux_fifo_3_fullness_out_i;
    logic [31:0] mux_fifo_3_read_ptr_out_i;
    logic [31:0] mux_fifo_3_write_ptr_out_i;
    logic [31:0] mux_fifo_3_max_fullness_out_i;
    logic [31:0] mux_fifo_3_byte_ctr_out_i;
    logic signed [31:0] vld_state_firstflat_s0_i;
    logic signed [31:0] vld_state_flatnesstype_s0_i;
    logic signed [31:0] vld_state_ichselected_s0_i;
    logic signed [31:0] vld_state_numbits_s0_i;
    logic signed [31:0] vld_state_prevfirstflat_s0_i;
    logic signed [31:0] vld_state_previchselected_s0_i;
    logic signed [31:0] vld_state_ichlookup_0_s0_i;
    logic signed [31:0] vld_state_ichlookup_1_s0_i;
    logic signed [31:0] vld_state_ichlookup_2_s0_i;
    logic signed [31:0] vld_state_ichlookup_3_s0_i;
    logic signed [31:0] vld_state_ichlookup_4_s0_i;
    logic signed [31:0] vld_state_ichlookup_5_s0_i;
    logic signed [31:0] vld_state_predictedsize_0_s0_i;
    logic signed [31:0] vld_state_predictedsize_1_s0_i;
    logic signed [31:0] vld_state_predictedsize_2_s0_i;
    logic signed [31:0] vld_state_predictedsize_3_s0_i;
    logic signed [31:0] vld_state_rcsizeunit_0_s0_i;
    logic signed [31:0] vld_state_rcsizeunit_1_s0_i;
    logic signed [31:0] vld_state_rcsizeunit_2_s0_i;
    logic signed [31:0] vld_state_rcsizeunit_3_s0_i;
    logic signed [31:0] vld_state_usemidpoint_0_s0_i;
    logic signed [31:0] vld_state_usemidpoint_1_s0_i;
    logic signed [31:0] vld_state_usemidpoint_2_s0_i;
    logic signed [31:0] vld_state_usemidpoint_3_s0_i;
    logic signed [31:0] fifo_0_fullness_s0_i;
    logic signed [31:0] fifo_0_read_ptr_s0_i;
    logic signed [31:0] fifo_1_fullness_s0_i;
    logic signed [31:0] fifo_1_read_ptr_s0_i;
    logic signed [31:0] fifo_2_fullness_s0_i;
    logic signed [31:0] fifo_2_read_ptr_s0_i;
    logic signed [31:0] fifo_3_fullness_s0_i;
    logic signed [31:0] fifo_3_read_ptr_s0_i;
    logic signed [31:0] vld_state_firstflat_s1_i;
    logic signed [31:0] vld_state_flatnesstype_s1_i;
    logic signed [31:0] vld_state_ichselected_s1_i;
    logic signed [31:0] vld_state_numbits_s1_i;
    logic signed [31:0] vld_state_prevfirstflat_s1_i;
    logic signed [31:0] vld_state_previchselected_s1_i;
    logic signed [31:0] vld_state_ichlookup_0_s1_i;
    logic signed [31:0] vld_state_ichlookup_1_s1_i;
    logic signed [31:0] vld_state_ichlookup_2_s1_i;
    logic signed [31:0] vld_state_ichlookup_3_s1_i;
    logic signed [31:0] vld_state_ichlookup_4_s1_i;
    logic signed [31:0] vld_state_ichlookup_5_s1_i;
    logic signed [31:0] vld_state_predictedsize_0_s1_i;
    logic signed [31:0] vld_state_predictedsize_1_s1_i;
    logic signed [31:0] vld_state_predictedsize_2_s1_i;
    logic signed [31:0] vld_state_predictedsize_3_s1_i;
    logic signed [31:0] vld_state_rcsizeunit_0_s1_i;
    logic signed [31:0] vld_state_rcsizeunit_1_s1_i;
    logic signed [31:0] vld_state_rcsizeunit_2_s1_i;
    logic signed [31:0] vld_state_rcsizeunit_3_s1_i;
    logic signed [31:0] vld_state_usemidpoint_0_s1_i;
    logic signed [31:0] vld_state_usemidpoint_1_s1_i;
    logic signed [31:0] vld_state_usemidpoint_2_s1_i;
    logic signed [31:0] vld_state_usemidpoint_3_s1_i;
    logic signed [31:0] fifo_0_fullness_s1_i;
    logic signed [31:0] fifo_0_read_ptr_s1_i;
    logic signed [31:0] fifo_1_fullness_s1_i;
    logic signed [31:0] fifo_1_read_ptr_s1_i;
    logic signed [31:0] fifo_2_fullness_s1_i;
    logic signed [31:0] fifo_2_read_ptr_s1_i;
    logic signed [31:0] fifo_3_fullness_s1_i;
    logic signed [31:0] fifo_3_read_ptr_s1_i;
    logic signed [31:0] vld_state_firstflat_s2_i;
    logic signed [31:0] vld_state_flatnesstype_s2_i;
    logic signed [31:0] vld_state_ichselected_s2_i;
    logic signed [31:0] vld_state_numbits_s2_i;
    logic signed [31:0] vld_state_prevfirstflat_s2_i;
    logic signed [31:0] vld_state_previchselected_s2_i;
    logic signed [31:0] vld_state_ichlookup_0_s2_i;
    logic signed [31:0] vld_state_ichlookup_1_s2_i;
    logic signed [31:0] vld_state_ichlookup_2_s2_i;
    logic signed [31:0] vld_state_ichlookup_3_s2_i;
    logic signed [31:0] vld_state_ichlookup_4_s2_i;
    logic signed [31:0] vld_state_ichlookup_5_s2_i;
    logic signed [31:0] vld_state_predictedsize_0_s2_i;
    logic signed [31:0] vld_state_predictedsize_1_s2_i;
    logic signed [31:0] vld_state_predictedsize_2_s2_i;
    logic signed [31:0] vld_state_predictedsize_3_s2_i;
    logic signed [31:0] vld_state_rcsizeunit_0_s2_i;
    logic signed [31:0] vld_state_rcsizeunit_1_s2_i;
    logic signed [31:0] vld_state_rcsizeunit_2_s2_i;
    logic signed [31:0] vld_state_rcsizeunit_3_s2_i;
    logic signed [31:0] vld_state_usemidpoint_0_s2_i;
    logic signed [31:0] vld_state_usemidpoint_1_s2_i;
    logic signed [31:0] vld_state_usemidpoint_2_s2_i;
    logic signed [31:0] vld_state_usemidpoint_3_s2_i;
    logic signed [31:0] fifo_0_fullness_s2_i;
    logic signed [31:0] fifo_0_read_ptr_s2_i;
    logic signed [31:0] fifo_1_fullness_s2_i;
    logic signed [31:0] fifo_1_read_ptr_s2_i;
    logic signed [31:0] fifo_2_fullness_s2_i;
    logic signed [31:0] fifo_2_read_ptr_s2_i;
    logic signed [31:0] fifo_3_fullness_s2_i;
    logic signed [31:0] fifo_3_read_ptr_s2_i;
    logic signed [31:0] vld_state_firstflat_s3_i;
    logic signed [31:0] vld_state_flatnesstype_s3_i;
    logic signed [31:0] vld_state_ichselected_s3_i;
    logic signed [31:0] vld_state_numbits_s3_i;
    logic signed [31:0] vld_state_prevfirstflat_s3_i;
    logic signed [31:0] vld_state_previchselected_s3_i;
    logic signed [31:0] vld_state_ichlookup_0_s3_i;
    logic signed [31:0] vld_state_ichlookup_1_s3_i;
    logic signed [31:0] vld_state_ichlookup_2_s3_i;
    logic signed [31:0] vld_state_ichlookup_3_s3_i;
    logic signed [31:0] vld_state_ichlookup_4_s3_i;
    logic signed [31:0] vld_state_ichlookup_5_s3_i;
    logic signed [31:0] vld_state_predictedsize_0_s3_i;
    logic signed [31:0] vld_state_predictedsize_1_s3_i;
    logic signed [31:0] vld_state_predictedsize_2_s3_i;
    logic signed [31:0] vld_state_predictedsize_3_s3_i;
    logic signed [31:0] vld_state_rcsizeunit_0_s3_i;
    logic signed [31:0] vld_state_rcsizeunit_1_s3_i;
    logic signed [31:0] vld_state_rcsizeunit_2_s3_i;
    logic signed [31:0] vld_state_rcsizeunit_3_s3_i;
    logic signed [31:0] vld_state_usemidpoint_0_s3_i;
    logic signed [31:0] vld_state_usemidpoint_1_s3_i;
    logic signed [31:0] vld_state_usemidpoint_2_s3_i;
    logic signed [31:0] vld_state_usemidpoint_3_s3_i;
    logic signed [31:0] fifo_0_fullness_s3_i;
    logic signed [31:0] fifo_0_read_ptr_s3_i;
    logic signed [31:0] fifo_1_fullness_s3_i;
    logic signed [31:0] fifo_1_read_ptr_s3_i;
    logic signed [31:0] fifo_2_fullness_s3_i;
    logic signed [31:0] fifo_2_read_ptr_s3_i;
    logic signed [31:0] fifo_3_fullness_s3_i;
    logic signed [31:0] fifo_3_read_ptr_s3_i;
    logic signed [31:0] vld_state_firstflat_s4_i;
    logic signed [31:0] vld_state_flatnesstype_s4_i;
    logic signed [31:0] vld_state_ichselected_s4_i;
    logic signed [31:0] vld_state_numbits_s4_i;
    logic signed [31:0] vld_state_prevfirstflat_s4_i;
    logic signed [31:0] vld_state_previchselected_s4_i;
    logic signed [31:0] vld_state_ichlookup_0_s4_i;
    logic signed [31:0] vld_state_ichlookup_1_s4_i;
    logic signed [31:0] vld_state_ichlookup_2_s4_i;
    logic signed [31:0] vld_state_ichlookup_3_s4_i;
    logic signed [31:0] vld_state_ichlookup_4_s4_i;
    logic signed [31:0] vld_state_ichlookup_5_s4_i;
    logic signed [31:0] vld_state_predictedsize_0_s4_i;
    logic signed [31:0] vld_state_predictedsize_1_s4_i;
    logic signed [31:0] vld_state_predictedsize_2_s4_i;
    logic signed [31:0] vld_state_predictedsize_3_s4_i;
    logic signed [31:0] vld_state_rcsizeunit_0_s4_i;
    logic signed [31:0] vld_state_rcsizeunit_1_s4_i;
    logic signed [31:0] vld_state_rcsizeunit_2_s4_i;
    logic signed [31:0] vld_state_rcsizeunit_3_s4_i;
    logic signed [31:0] vld_state_usemidpoint_0_s4_i;
    logic signed [31:0] vld_state_usemidpoint_1_s4_i;
    logic signed [31:0] vld_state_usemidpoint_2_s4_i;
    logic signed [31:0] vld_state_usemidpoint_3_s4_i;
    logic signed [31:0] fifo_0_fullness_s4_i;
    logic signed [31:0] fifo_0_read_ptr_s4_i;
    logic signed [31:0] fifo_1_fullness_s4_i;
    logic signed [31:0] fifo_1_read_ptr_s4_i;
    logic signed [31:0] fifo_2_fullness_s4_i;
    logic signed [31:0] fifo_2_read_ptr_s4_i;
    logic signed [31:0] fifo_3_fullness_s4_i;
    logic signed [31:0] fifo_3_read_ptr_s4_i;
    logic vld_domain_s0_i;
    logic signed [31:0] vld_fifo_lane_s0_i;
    logic signed [31:0] vld_fifo_fullness_s0_i;
    logic signed [31:0] vld_fifo_read_ptr_s0_i;
    logic signed [31:0] vld_firstflat_s0_raw_i;
    logic signed [31:0] vld_flatnesstype_s0_raw_i;
    logic signed [31:0] vld_ichselected_s0_raw_i;
    logic signed [31:0] vld_numbits_s0_raw_i;
    logic signed [31:0] vld_prevfirstflat_s0_raw_i;
    logic signed [31:0] vld_previchselected_s0_raw_i;
    logic signed [31:0] vld_ichlookup_0_s0_raw_i;
    logic signed [31:0] vld_ichlookup_1_s0_raw_i;
    logic signed [31:0] vld_ichlookup_2_s0_raw_i;
    logic signed [31:0] vld_ichlookup_3_s0_raw_i;
    logic signed [31:0] vld_ichlookup_4_s0_raw_i;
    logic signed [31:0] vld_ichlookup_5_s0_raw_i;
    logic signed [31:0] vld_predictedsize_0_s0_raw_i;
    logic signed [31:0] vld_predictedsize_1_s0_raw_i;
    logic signed [31:0] vld_predictedsize_2_s0_raw_i;
    logic signed [31:0] vld_predictedsize_3_s0_raw_i;
    logic signed [31:0] vld_rcsizeunit_0_s0_raw_i;
    logic signed [31:0] vld_rcsizeunit_1_s0_raw_i;
    logic signed [31:0] vld_rcsizeunit_2_s0_raw_i;
    logic signed [31:0] vld_rcsizeunit_3_s0_raw_i;
    logic signed [31:0] vld_usemidpoint_0_s0_raw_i;
    logic signed [31:0] vld_usemidpoint_1_s0_raw_i;
    logic signed [31:0] vld_usemidpoint_2_s0_raw_i;
    logic signed [31:0] vld_usemidpoint_3_s0_raw_i;
    logic signed [31:0] vld_residual_0_0_raw_i;
    logic signed [31:0] vld_residual_0_1_raw_i;
    logic signed [31:0] vld_residual_0_2_raw_i;
    logic vld_domain_s1_i;
    logic signed [31:0] vld_fifo_lane_s1_i;
    logic signed [31:0] vld_fifo_fullness_s1_i;
    logic signed [31:0] vld_fifo_read_ptr_s1_i;
    logic signed [31:0] vld_firstflat_s1_raw_i;
    logic signed [31:0] vld_flatnesstype_s1_raw_i;
    logic signed [31:0] vld_ichselected_s1_raw_i;
    logic signed [31:0] vld_numbits_s1_raw_i;
    logic signed [31:0] vld_prevfirstflat_s1_raw_i;
    logic signed [31:0] vld_previchselected_s1_raw_i;
    logic signed [31:0] vld_ichlookup_0_s1_raw_i;
    logic signed [31:0] vld_ichlookup_1_s1_raw_i;
    logic signed [31:0] vld_ichlookup_2_s1_raw_i;
    logic signed [31:0] vld_ichlookup_3_s1_raw_i;
    logic signed [31:0] vld_ichlookup_4_s1_raw_i;
    logic signed [31:0] vld_ichlookup_5_s1_raw_i;
    logic signed [31:0] vld_predictedsize_0_s1_raw_i;
    logic signed [31:0] vld_predictedsize_1_s1_raw_i;
    logic signed [31:0] vld_predictedsize_2_s1_raw_i;
    logic signed [31:0] vld_predictedsize_3_s1_raw_i;
    logic signed [31:0] vld_rcsizeunit_0_s1_raw_i;
    logic signed [31:0] vld_rcsizeunit_1_s1_raw_i;
    logic signed [31:0] vld_rcsizeunit_2_s1_raw_i;
    logic signed [31:0] vld_rcsizeunit_3_s1_raw_i;
    logic signed [31:0] vld_usemidpoint_0_s1_raw_i;
    logic signed [31:0] vld_usemidpoint_1_s1_raw_i;
    logic signed [31:0] vld_usemidpoint_2_s1_raw_i;
    logic signed [31:0] vld_usemidpoint_3_s1_raw_i;
    logic signed [31:0] vld_residual_1_0_raw_i;
    logic signed [31:0] vld_residual_1_1_raw_i;
    logic signed [31:0] vld_residual_1_2_raw_i;
    logic vld_domain_s2_i;
    logic signed [31:0] vld_fifo_lane_s2_i;
    logic signed [31:0] vld_fifo_fullness_s2_i;
    logic signed [31:0] vld_fifo_read_ptr_s2_i;
    logic signed [31:0] vld_firstflat_s2_raw_i;
    logic signed [31:0] vld_flatnesstype_s2_raw_i;
    logic signed [31:0] vld_ichselected_s2_raw_i;
    logic signed [31:0] vld_numbits_s2_raw_i;
    logic signed [31:0] vld_prevfirstflat_s2_raw_i;
    logic signed [31:0] vld_previchselected_s2_raw_i;
    logic signed [31:0] vld_ichlookup_0_s2_raw_i;
    logic signed [31:0] vld_ichlookup_1_s2_raw_i;
    logic signed [31:0] vld_ichlookup_2_s2_raw_i;
    logic signed [31:0] vld_ichlookup_3_s2_raw_i;
    logic signed [31:0] vld_ichlookup_4_s2_raw_i;
    logic signed [31:0] vld_ichlookup_5_s2_raw_i;
    logic signed [31:0] vld_predictedsize_0_s2_raw_i;
    logic signed [31:0] vld_predictedsize_1_s2_raw_i;
    logic signed [31:0] vld_predictedsize_2_s2_raw_i;
    logic signed [31:0] vld_predictedsize_3_s2_raw_i;
    logic signed [31:0] vld_rcsizeunit_0_s2_raw_i;
    logic signed [31:0] vld_rcsizeunit_1_s2_raw_i;
    logic signed [31:0] vld_rcsizeunit_2_s2_raw_i;
    logic signed [31:0] vld_rcsizeunit_3_s2_raw_i;
    logic signed [31:0] vld_usemidpoint_0_s2_raw_i;
    logic signed [31:0] vld_usemidpoint_1_s2_raw_i;
    logic signed [31:0] vld_usemidpoint_2_s2_raw_i;
    logic signed [31:0] vld_usemidpoint_3_s2_raw_i;
    logic signed [31:0] vld_residual_2_0_raw_i;
    logic signed [31:0] vld_residual_2_1_raw_i;
    logic signed [31:0] vld_residual_2_2_raw_i;
    logic vld_domain_s3_i;
    logic signed [31:0] vld_fifo_lane_s3_i;
    logic signed [31:0] vld_fifo_fullness_s3_i;
    logic signed [31:0] vld_fifo_read_ptr_s3_i;
    logic signed [31:0] vld_firstflat_s3_raw_i;
    logic signed [31:0] vld_flatnesstype_s3_raw_i;
    logic signed [31:0] vld_ichselected_s3_raw_i;
    logic signed [31:0] vld_numbits_s3_raw_i;
    logic signed [31:0] vld_prevfirstflat_s3_raw_i;
    logic signed [31:0] vld_previchselected_s3_raw_i;
    logic signed [31:0] vld_ichlookup_0_s3_raw_i;
    logic signed [31:0] vld_ichlookup_1_s3_raw_i;
    logic signed [31:0] vld_ichlookup_2_s3_raw_i;
    logic signed [31:0] vld_ichlookup_3_s3_raw_i;
    logic signed [31:0] vld_ichlookup_4_s3_raw_i;
    logic signed [31:0] vld_ichlookup_5_s3_raw_i;
    logic signed [31:0] vld_predictedsize_0_s3_raw_i;
    logic signed [31:0] vld_predictedsize_1_s3_raw_i;
    logic signed [31:0] vld_predictedsize_2_s3_raw_i;
    logic signed [31:0] vld_predictedsize_3_s3_raw_i;
    logic signed [31:0] vld_rcsizeunit_0_s3_raw_i;
    logic signed [31:0] vld_rcsizeunit_1_s3_raw_i;
    logic signed [31:0] vld_rcsizeunit_2_s3_raw_i;
    logic signed [31:0] vld_rcsizeunit_3_s3_raw_i;
    logic signed [31:0] vld_usemidpoint_0_s3_raw_i;
    logic signed [31:0] vld_usemidpoint_1_s3_raw_i;
    logic signed [31:0] vld_usemidpoint_2_s3_raw_i;
    logic signed [31:0] vld_usemidpoint_3_s3_raw_i;
    logic signed [31:0] vld_residual_3_0_raw_i;
    logic signed [31:0] vld_residual_3_1_raw_i;
    logic signed [31:0] vld_residual_3_2_raw_i;

    processgroupdec_decode_transition u_mux_refill(
        .mux_word_size(mux_word_size),
        .num_ssps(num_ssps),
        .post_mux_num_bits(post_mux_num_bits),
        .max_se_size_0(max_se_size_0),
        .max_se_size_1(max_se_size_1),
        .max_se_size_2(max_se_size_2),
        .max_se_size_3(max_se_size_3),
        .stream_byte_0(stream_byte_0),
        .stream_byte_1(stream_byte_1),
        .stream_byte_2(stream_byte_2),
        .stream_byte_3(stream_byte_3),
        .stream_byte_4(stream_byte_4),
        .stream_byte_5(stream_byte_5),
        .stream_byte_6(stream_byte_6),
        .stream_byte_7(stream_byte_7),
        .stream_byte_8(stream_byte_8),
        .stream_byte_9(stream_byte_9),
        .stream_byte_10(stream_byte_10),
        .stream_byte_11(stream_byte_11),
        .stream_byte_12(stream_byte_12),
        .stream_byte_13(stream_byte_13),
        .stream_byte_14(stream_byte_14),
        .stream_byte_15(stream_byte_15),
        .stream_byte_16(stream_byte_16),
        .stream_byte_17(stream_byte_17),
        .stream_byte_18(stream_byte_18),
        .stream_byte_19(stream_byte_19),
        .stream_byte_20(stream_byte_20),
        .stream_byte_21(stream_byte_21),
        .stream_byte_22(stream_byte_22),
        .stream_byte_23(stream_byte_23),
        .stream_byte_24(stream_byte_24),
        .stream_byte_25(stream_byte_25),
        .stream_byte_26(stream_byte_26),
        .stream_byte_27(stream_byte_27),
        .stream_byte_28(stream_byte_28),
        .stream_byte_29(stream_byte_29),
        .stream_byte_30(stream_byte_30),
        .stream_byte_31(stream_byte_31),
        .stream_byte_32(stream_byte_32),
        .fifo_0_size(fifo_0_size),
        .fifo_0_fullness(fifo_0_fullness),
        .fifo_0_read_ptr(fifo_0_read_ptr),
        .fifo_0_write_ptr(fifo_0_write_ptr),
        .fifo_0_max_fullness(fifo_0_max_fullness),
        .fifo_0_byte_ctr(fifo_0_byte_ctr),
        .fifo_1_size(fifo_1_size),
        .fifo_1_fullness(fifo_1_fullness),
        .fifo_1_read_ptr(fifo_1_read_ptr),
        .fifo_1_write_ptr(fifo_1_write_ptr),
        .fifo_1_max_fullness(fifo_1_max_fullness),
        .fifo_1_byte_ctr(fifo_1_byte_ctr),
        .fifo_2_size(fifo_2_size),
        .fifo_2_fullness(fifo_2_fullness),
        .fifo_2_read_ptr(fifo_2_read_ptr),
        .fifo_2_write_ptr(fifo_2_write_ptr),
        .fifo_2_max_fullness(fifo_2_max_fullness),
        .fifo_2_byte_ctr(fifo_2_byte_ctr),
        .fifo_3_size(fifo_3_size),
        .fifo_3_fullness(fifo_3_fullness),
        .fifo_3_read_ptr(fifo_3_read_ptr),
        .fifo_3_write_ptr(fifo_3_write_ptr),
        .fifo_3_max_fullness(fifo_3_max_fullness),
        .fifo_3_byte_ctr(fifo_3_byte_ctr),
        .fifo_0_byte_0(fifo_0_byte_0),
        .fifo_0_byte_1(fifo_0_byte_1),
        .fifo_0_byte_2(fifo_0_byte_2),
        .fifo_0_byte_3(fifo_0_byte_3),
        .fifo_0_byte_4(fifo_0_byte_4),
        .fifo_0_byte_5(fifo_0_byte_5),
        .fifo_0_byte_6(fifo_0_byte_6),
        .fifo_0_byte_7(fifo_0_byte_7),
        .fifo_0_byte_8(fifo_0_byte_8),
        .fifo_0_byte_9(fifo_0_byte_9),
        .fifo_0_byte_10(fifo_0_byte_10),
        .fifo_0_byte_11(fifo_0_byte_11),
        .fifo_0_byte_12(fifo_0_byte_12),
        .fifo_0_byte_13(fifo_0_byte_13),
        .fifo_0_byte_14(fifo_0_byte_14),
        .fifo_0_byte_15(fifo_0_byte_15),
        .fifo_0_byte_16(fifo_0_byte_16),
        .fifo_1_byte_0(fifo_1_byte_0),
        .fifo_1_byte_1(fifo_1_byte_1),
        .fifo_1_byte_2(fifo_1_byte_2),
        .fifo_1_byte_3(fifo_1_byte_3),
        .fifo_1_byte_4(fifo_1_byte_4),
        .fifo_1_byte_5(fifo_1_byte_5),
        .fifo_1_byte_6(fifo_1_byte_6),
        .fifo_1_byte_7(fifo_1_byte_7),
        .fifo_1_byte_8(fifo_1_byte_8),
        .fifo_1_byte_9(fifo_1_byte_9),
        .fifo_1_byte_10(fifo_1_byte_10),
        .fifo_1_byte_11(fifo_1_byte_11),
        .fifo_1_byte_12(fifo_1_byte_12),
        .fifo_1_byte_13(fifo_1_byte_13),
        .fifo_1_byte_14(fifo_1_byte_14),
        .fifo_1_byte_15(fifo_1_byte_15),
        .fifo_1_byte_16(fifo_1_byte_16),
        .fifo_2_byte_0(fifo_2_byte_0),
        .fifo_2_byte_1(fifo_2_byte_1),
        .fifo_2_byte_2(fifo_2_byte_2),
        .fifo_2_byte_3(fifo_2_byte_3),
        .fifo_2_byte_4(fifo_2_byte_4),
        .fifo_2_byte_5(fifo_2_byte_5),
        .fifo_2_byte_6(fifo_2_byte_6),
        .fifo_2_byte_7(fifo_2_byte_7),
        .fifo_2_byte_8(fifo_2_byte_8),
        .fifo_2_byte_9(fifo_2_byte_9),
        .fifo_2_byte_10(fifo_2_byte_10),
        .fifo_2_byte_11(fifo_2_byte_11),
        .fifo_2_byte_12(fifo_2_byte_12),
        .fifo_2_byte_13(fifo_2_byte_13),
        .fifo_2_byte_14(fifo_2_byte_14),
        .fifo_2_byte_15(fifo_2_byte_15),
        .fifo_2_byte_16(fifo_2_byte_16),
        .fifo_3_byte_0(fifo_3_byte_0),
        .fifo_3_byte_1(fifo_3_byte_1),
        .fifo_3_byte_2(fifo_3_byte_2),
        .fifo_3_byte_3(fifo_3_byte_3),
        .fifo_3_byte_4(fifo_3_byte_4),
        .fifo_3_byte_5(fifo_3_byte_5),
        .fifo_3_byte_6(fifo_3_byte_6),
        .fifo_3_byte_7(fifo_3_byte_7),
        .fifo_3_byte_8(fifo_3_byte_8),
        .fifo_3_byte_9(fifo_3_byte_9),
        .fifo_3_byte_10(fifo_3_byte_10),
        .fifo_3_byte_11(fifo_3_byte_11),
        .fifo_3_byte_12(fifo_3_byte_12),
        .fifo_3_byte_13(fifo_3_byte_13),
        .fifo_3_byte_14(fifo_3_byte_14),
        .fifo_3_byte_15(fifo_3_byte_15),
        .fifo_3_byte_16(fifo_3_byte_16),
        .domain_valid(mux_domain_valid_i),
        .post_mux_num_bits_out(mux_post_mux_num_bits_out_i),
        .fifo_0_byte_0_out(mux_fifo_0_byte_0_out_i),
        .fifo_0_byte_1_out(mux_fifo_0_byte_1_out_i),
        .fifo_0_byte_2_out(mux_fifo_0_byte_2_out_i),
        .fifo_0_byte_3_out(mux_fifo_0_byte_3_out_i),
        .fifo_0_byte_4_out(mux_fifo_0_byte_4_out_i),
        .fifo_0_byte_5_out(mux_fifo_0_byte_5_out_i),
        .fifo_0_byte_6_out(mux_fifo_0_byte_6_out_i),
        .fifo_0_byte_7_out(mux_fifo_0_byte_7_out_i),
        .fifo_0_byte_8_out(mux_fifo_0_byte_8_out_i),
        .fifo_0_byte_9_out(mux_fifo_0_byte_9_out_i),
        .fifo_0_byte_10_out(mux_fifo_0_byte_10_out_i),
        .fifo_0_byte_11_out(mux_fifo_0_byte_11_out_i),
        .fifo_0_byte_12_out(mux_fifo_0_byte_12_out_i),
        .fifo_0_byte_13_out(mux_fifo_0_byte_13_out_i),
        .fifo_0_byte_14_out(mux_fifo_0_byte_14_out_i),
        .fifo_0_byte_15_out(mux_fifo_0_byte_15_out_i),
        .fifo_0_byte_16_out(mux_fifo_0_byte_16_out_i),
        .fifo_1_byte_0_out(mux_fifo_1_byte_0_out_i),
        .fifo_1_byte_1_out(mux_fifo_1_byte_1_out_i),
        .fifo_1_byte_2_out(mux_fifo_1_byte_2_out_i),
        .fifo_1_byte_3_out(mux_fifo_1_byte_3_out_i),
        .fifo_1_byte_4_out(mux_fifo_1_byte_4_out_i),
        .fifo_1_byte_5_out(mux_fifo_1_byte_5_out_i),
        .fifo_1_byte_6_out(mux_fifo_1_byte_6_out_i),
        .fifo_1_byte_7_out(mux_fifo_1_byte_7_out_i),
        .fifo_1_byte_8_out(mux_fifo_1_byte_8_out_i),
        .fifo_1_byte_9_out(mux_fifo_1_byte_9_out_i),
        .fifo_1_byte_10_out(mux_fifo_1_byte_10_out_i),
        .fifo_1_byte_11_out(mux_fifo_1_byte_11_out_i),
        .fifo_1_byte_12_out(mux_fifo_1_byte_12_out_i),
        .fifo_1_byte_13_out(mux_fifo_1_byte_13_out_i),
        .fifo_1_byte_14_out(mux_fifo_1_byte_14_out_i),
        .fifo_1_byte_15_out(mux_fifo_1_byte_15_out_i),
        .fifo_1_byte_16_out(mux_fifo_1_byte_16_out_i),
        .fifo_2_byte_0_out(mux_fifo_2_byte_0_out_i),
        .fifo_2_byte_1_out(mux_fifo_2_byte_1_out_i),
        .fifo_2_byte_2_out(mux_fifo_2_byte_2_out_i),
        .fifo_2_byte_3_out(mux_fifo_2_byte_3_out_i),
        .fifo_2_byte_4_out(mux_fifo_2_byte_4_out_i),
        .fifo_2_byte_5_out(mux_fifo_2_byte_5_out_i),
        .fifo_2_byte_6_out(mux_fifo_2_byte_6_out_i),
        .fifo_2_byte_7_out(mux_fifo_2_byte_7_out_i),
        .fifo_2_byte_8_out(mux_fifo_2_byte_8_out_i),
        .fifo_2_byte_9_out(mux_fifo_2_byte_9_out_i),
        .fifo_2_byte_10_out(mux_fifo_2_byte_10_out_i),
        .fifo_2_byte_11_out(mux_fifo_2_byte_11_out_i),
        .fifo_2_byte_12_out(mux_fifo_2_byte_12_out_i),
        .fifo_2_byte_13_out(mux_fifo_2_byte_13_out_i),
        .fifo_2_byte_14_out(mux_fifo_2_byte_14_out_i),
        .fifo_2_byte_15_out(mux_fifo_2_byte_15_out_i),
        .fifo_2_byte_16_out(mux_fifo_2_byte_16_out_i),
        .fifo_3_byte_0_out(mux_fifo_3_byte_0_out_i),
        .fifo_3_byte_1_out(mux_fifo_3_byte_1_out_i),
        .fifo_3_byte_2_out(mux_fifo_3_byte_2_out_i),
        .fifo_3_byte_3_out(mux_fifo_3_byte_3_out_i),
        .fifo_3_byte_4_out(mux_fifo_3_byte_4_out_i),
        .fifo_3_byte_5_out(mux_fifo_3_byte_5_out_i),
        .fifo_3_byte_6_out(mux_fifo_3_byte_6_out_i),
        .fifo_3_byte_7_out(mux_fifo_3_byte_7_out_i),
        .fifo_3_byte_8_out(mux_fifo_3_byte_8_out_i),
        .fifo_3_byte_9_out(mux_fifo_3_byte_9_out_i),
        .fifo_3_byte_10_out(mux_fifo_3_byte_10_out_i),
        .fifo_3_byte_11_out(mux_fifo_3_byte_11_out_i),
        .fifo_3_byte_12_out(mux_fifo_3_byte_12_out_i),
        .fifo_3_byte_13_out(mux_fifo_3_byte_13_out_i),
        .fifo_3_byte_14_out(mux_fifo_3_byte_14_out_i),
        .fifo_3_byte_15_out(mux_fifo_3_byte_15_out_i),
        .fifo_3_byte_16_out(mux_fifo_3_byte_16_out_i),
        .fifo_0_size_out(mux_fifo_0_size_out_i),
        .fifo_0_fullness_out(mux_fifo_0_fullness_out_i),
        .fifo_0_read_ptr_out(mux_fifo_0_read_ptr_out_i),
        .fifo_0_write_ptr_out(mux_fifo_0_write_ptr_out_i),
        .fifo_0_max_fullness_out(mux_fifo_0_max_fullness_out_i),
        .fifo_0_byte_ctr_out(mux_fifo_0_byte_ctr_out_i),
        .fifo_1_size_out(mux_fifo_1_size_out_i),
        .fifo_1_fullness_out(mux_fifo_1_fullness_out_i),
        .fifo_1_read_ptr_out(mux_fifo_1_read_ptr_out_i),
        .fifo_1_write_ptr_out(mux_fifo_1_write_ptr_out_i),
        .fifo_1_max_fullness_out(mux_fifo_1_max_fullness_out_i),
        .fifo_1_byte_ctr_out(mux_fifo_1_byte_ctr_out_i),
        .fifo_2_size_out(mux_fifo_2_size_out_i),
        .fifo_2_fullness_out(mux_fifo_2_fullness_out_i),
        .fifo_2_read_ptr_out(mux_fifo_2_read_ptr_out_i),
        .fifo_2_write_ptr_out(mux_fifo_2_write_ptr_out_i),
        .fifo_2_max_fullness_out(mux_fifo_2_max_fullness_out_i),
        .fifo_2_byte_ctr_out(mux_fifo_2_byte_ctr_out_i),
        .fifo_3_size_out(mux_fifo_3_size_out_i),
        .fifo_3_fullness_out(mux_fifo_3_fullness_out_i),
        .fifo_3_read_ptr_out(mux_fifo_3_read_ptr_out_i),
        .fifo_3_write_ptr_out(mux_fifo_3_write_ptr_out_i),
        .fifo_3_max_fullness_out(mux_fifo_3_max_fullness_out_i),
        .fifo_3_byte_ctr_out(mux_fifo_3_byte_ctr_out_i)
    );

    vldunit_decode_transition u_vld_unit_0(
        .unit(32'sd0),
        .cfg_bits_per_component(cfg_bits_per_component),
        .cfg_somewhat_flat_qp_thresh(cfg_somewhat_flat_qp_thresh),
        .cfg_dsc_version_minor(cfg_dsc_version_minor),
        .cfg_native_420(cfg_native_420),
        .cfg_flatness_min_qp(cfg_flatness_min_qp),
        .cfg_flatness_max_qp(cfg_flatness_max_qp),
        .state_firstflat(vld_state_firstflat_s0_i),
        .state_flatnesstype(vld_state_flatnesstype_s0_i),
        .state_groupcount(state_groupcount),
        .state_ichindicesingroup(state_ichindicesingroup),
        .state_ichselected(vld_state_ichselected_s0_i),
        .state_prevfirstflat(vld_state_prevfirstflat_s0_i),
        .state_previchselected(vld_state_previchselected_s0_i),
        .state_primaryqp(state_primaryqp),
        .state_prevprimaryqp(state_prevprimaryqp),
        .state_unitspergroup(state_unitspergroup),
        .state_numbits(vld_state_numbits_s0_i),
        .state_cpntbitdepth_0(state_cpntbitdepth_0),
        .state_cpntbitdepth_1(state_cpntbitdepth_1),
        .state_cpntbitdepth_2(state_cpntbitdepth_2),
        .state_cpntbitdepth_3(state_cpntbitdepth_3),
        .state_unitctype_0(state_unitctype_0),
        .state_unitctype_1(state_unitctype_1),
        .state_unitctype_2(state_unitctype_2),
        .state_unitctype_3(state_unitctype_3),
        .state_unitsspmap_0(state_unitsspmap_0),
        .state_unitsspmap_1(state_unitsspmap_1),
        .state_unitsspmap_2(state_unitsspmap_2),
        .state_unitsspmap_3(state_unitsspmap_3),
        .state_ichindexunitmap_0(state_ichindexunitmap_0),
        .state_ichindexunitmap_1(state_ichindexunitmap_1),
        .state_ichindexunitmap_2(state_ichindexunitmap_2),
        .state_ichindexunitmap_3(state_ichindexunitmap_3),
        .state_ichindexunitmap_4(state_ichindexunitmap_4),
        .state_ichindexunitmap_5(state_ichindexunitmap_5),
        .state_ichlookup_0(vld_state_ichlookup_0_s0_i),
        .state_ichlookup_1(vld_state_ichlookup_1_s0_i),
        .state_ichlookup_2(vld_state_ichlookup_2_s0_i),
        .state_ichlookup_3(vld_state_ichlookup_3_s0_i),
        .state_ichlookup_4(vld_state_ichlookup_4_s0_i),
        .state_ichlookup_5(vld_state_ichlookup_5_s0_i),
        .state_predictedsize_0(vld_state_predictedsize_0_s0_i),
        .state_predictedsize_1(vld_state_predictedsize_1_s0_i),
        .state_predictedsize_2(vld_state_predictedsize_2_s0_i),
        .state_predictedsize_3(vld_state_predictedsize_3_s0_i),
        .state_rcsizeunit_0(vld_state_rcsizeunit_0_s0_i),
        .state_rcsizeunit_1(vld_state_rcsizeunit_1_s0_i),
        .state_rcsizeunit_2(vld_state_rcsizeunit_2_s0_i),
        .state_rcsizeunit_3(vld_state_rcsizeunit_3_s0_i),
        .state_usemidpoint_0(vld_state_usemidpoint_0_s0_i),
        .state_usemidpoint_1(vld_state_usemidpoint_1_s0_i),
        .state_usemidpoint_2(vld_state_usemidpoint_2_s0_i),
        .state_usemidpoint_3(vld_state_usemidpoint_3_s0_i),
        .qlevel_luma_primary(qlevel_luma_primary),
        .qlevel_chroma_primary(qlevel_chroma_primary),
        .qlevel_luma_previous(qlevel_luma_previous),
        .qlevel_chroma_previous(qlevel_chroma_previous),
        .quantized_residual_0(state_quantizedresidual_0_0),
        .quantized_residual_1(state_quantizedresidual_0_1),
        .quantized_residual_2(state_quantizedresidual_0_2),
        .fifo_size(((state_unitsspmap_0 == 32'sd0) ? mux_fifo_0_size_out_i : ((state_unitsspmap_0 == 32'sd1) ? mux_fifo_1_size_out_i : ((state_unitsspmap_0 == 32'sd2) ? mux_fifo_2_size_out_i : mux_fifo_3_size_out_i)))),
        .fifo_fullness(((state_unitsspmap_0 == 32'sd0) ? fifo_0_fullness_s0_i : ((state_unitsspmap_0 == 32'sd1) ? fifo_1_fullness_s0_i : ((state_unitsspmap_0 == 32'sd2) ? fifo_2_fullness_s0_i : fifo_3_fullness_s0_i)))),
        .fifo_read_ptr(((state_unitsspmap_0 == 32'sd0) ? fifo_0_read_ptr_s0_i : ((state_unitsspmap_0 == 32'sd1) ? fifo_1_read_ptr_s0_i : ((state_unitsspmap_0 == 32'sd2) ? fifo_2_read_ptr_s0_i : fifo_3_read_ptr_s0_i)))),
        .fifo_byte_0(((state_unitsspmap_0 == 32'sd0) ? mux_fifo_0_byte_0_out_i : ((state_unitsspmap_0 == 32'sd1) ? mux_fifo_1_byte_0_out_i : ((state_unitsspmap_0 == 32'sd2) ? mux_fifo_2_byte_0_out_i : mux_fifo_3_byte_0_out_i)))),
        .fifo_byte_1(((state_unitsspmap_0 == 32'sd0) ? mux_fifo_0_byte_1_out_i : ((state_unitsspmap_0 == 32'sd1) ? mux_fifo_1_byte_1_out_i : ((state_unitsspmap_0 == 32'sd2) ? mux_fifo_2_byte_1_out_i : mux_fifo_3_byte_1_out_i)))),
        .fifo_byte_2(((state_unitsspmap_0 == 32'sd0) ? mux_fifo_0_byte_2_out_i : ((state_unitsspmap_0 == 32'sd1) ? mux_fifo_1_byte_2_out_i : ((state_unitsspmap_0 == 32'sd2) ? mux_fifo_2_byte_2_out_i : mux_fifo_3_byte_2_out_i)))),
        .fifo_byte_3(((state_unitsspmap_0 == 32'sd0) ? mux_fifo_0_byte_3_out_i : ((state_unitsspmap_0 == 32'sd1) ? mux_fifo_1_byte_3_out_i : ((state_unitsspmap_0 == 32'sd2) ? mux_fifo_2_byte_3_out_i : mux_fifo_3_byte_3_out_i)))),
        .fifo_byte_4(((state_unitsspmap_0 == 32'sd0) ? mux_fifo_0_byte_4_out_i : ((state_unitsspmap_0 == 32'sd1) ? mux_fifo_1_byte_4_out_i : ((state_unitsspmap_0 == 32'sd2) ? mux_fifo_2_byte_4_out_i : mux_fifo_3_byte_4_out_i)))),
        .fifo_byte_5(((state_unitsspmap_0 == 32'sd0) ? mux_fifo_0_byte_5_out_i : ((state_unitsspmap_0 == 32'sd1) ? mux_fifo_1_byte_5_out_i : ((state_unitsspmap_0 == 32'sd2) ? mux_fifo_2_byte_5_out_i : mux_fifo_3_byte_5_out_i)))),
        .fifo_byte_6(((state_unitsspmap_0 == 32'sd0) ? mux_fifo_0_byte_6_out_i : ((state_unitsspmap_0 == 32'sd1) ? mux_fifo_1_byte_6_out_i : ((state_unitsspmap_0 == 32'sd2) ? mux_fifo_2_byte_6_out_i : mux_fifo_3_byte_6_out_i)))),
        .fifo_byte_7(((state_unitsspmap_0 == 32'sd0) ? mux_fifo_0_byte_7_out_i : ((state_unitsspmap_0 == 32'sd1) ? mux_fifo_1_byte_7_out_i : ((state_unitsspmap_0 == 32'sd2) ? mux_fifo_2_byte_7_out_i : mux_fifo_3_byte_7_out_i)))),
        .fifo_byte_8(((state_unitsspmap_0 == 32'sd0) ? mux_fifo_0_byte_8_out_i : ((state_unitsspmap_0 == 32'sd1) ? mux_fifo_1_byte_8_out_i : ((state_unitsspmap_0 == 32'sd2) ? mux_fifo_2_byte_8_out_i : mux_fifo_3_byte_8_out_i)))),
        .fifo_byte_9(((state_unitsspmap_0 == 32'sd0) ? mux_fifo_0_byte_9_out_i : ((state_unitsspmap_0 == 32'sd1) ? mux_fifo_1_byte_9_out_i : ((state_unitsspmap_0 == 32'sd2) ? mux_fifo_2_byte_9_out_i : mux_fifo_3_byte_9_out_i)))),
        .fifo_byte_10(((state_unitsspmap_0 == 32'sd0) ? mux_fifo_0_byte_10_out_i : ((state_unitsspmap_0 == 32'sd1) ? mux_fifo_1_byte_10_out_i : ((state_unitsspmap_0 == 32'sd2) ? mux_fifo_2_byte_10_out_i : mux_fifo_3_byte_10_out_i)))),
        .fifo_byte_11(((state_unitsspmap_0 == 32'sd0) ? mux_fifo_0_byte_11_out_i : ((state_unitsspmap_0 == 32'sd1) ? mux_fifo_1_byte_11_out_i : ((state_unitsspmap_0 == 32'sd2) ? mux_fifo_2_byte_11_out_i : mux_fifo_3_byte_11_out_i)))),
        .fifo_byte_12(((state_unitsspmap_0 == 32'sd0) ? mux_fifo_0_byte_12_out_i : ((state_unitsspmap_0 == 32'sd1) ? mux_fifo_1_byte_12_out_i : ((state_unitsspmap_0 == 32'sd2) ? mux_fifo_2_byte_12_out_i : mux_fifo_3_byte_12_out_i)))),
        .fifo_byte_13(((state_unitsspmap_0 == 32'sd0) ? mux_fifo_0_byte_13_out_i : ((state_unitsspmap_0 == 32'sd1) ? mux_fifo_1_byte_13_out_i : ((state_unitsspmap_0 == 32'sd2) ? mux_fifo_2_byte_13_out_i : mux_fifo_3_byte_13_out_i)))),
        .fifo_byte_14(((state_unitsspmap_0 == 32'sd0) ? mux_fifo_0_byte_14_out_i : ((state_unitsspmap_0 == 32'sd1) ? mux_fifo_1_byte_14_out_i : ((state_unitsspmap_0 == 32'sd2) ? mux_fifo_2_byte_14_out_i : mux_fifo_3_byte_14_out_i)))),
        .fifo_byte_15(((state_unitsspmap_0 == 32'sd0) ? mux_fifo_0_byte_15_out_i : ((state_unitsspmap_0 == 32'sd1) ? mux_fifo_1_byte_15_out_i : ((state_unitsspmap_0 == 32'sd2) ? mux_fifo_2_byte_15_out_i : mux_fifo_3_byte_15_out_i)))),
        .fifo_byte_16(((state_unitsspmap_0 == 32'sd0) ? mux_fifo_0_byte_16_out_i : ((state_unitsspmap_0 == 32'sd1) ? mux_fifo_1_byte_16_out_i : ((state_unitsspmap_0 == 32'sd2) ? mux_fifo_2_byte_16_out_i : mux_fifo_3_byte_16_out_i)))),
        .domain_valid(vld_domain_s0_i),
        .state_firstflat_out(vld_firstflat_s0_raw_i),
        .state_flatnesstype_out(vld_flatnesstype_s0_raw_i),
        .state_ichselected_out(vld_ichselected_s0_raw_i),
        .state_prevfirstflat_out(vld_prevfirstflat_s0_raw_i),
        .state_previchselected_out(vld_previchselected_s0_raw_i),
        .state_numbits_out(vld_numbits_s0_raw_i),
        .state_ichlookup_0_out(vld_ichlookup_0_s0_raw_i),
        .state_ichlookup_1_out(vld_ichlookup_1_s0_raw_i),
        .state_ichlookup_2_out(vld_ichlookup_2_s0_raw_i),
        .state_ichlookup_3_out(vld_ichlookup_3_s0_raw_i),
        .state_ichlookup_4_out(vld_ichlookup_4_s0_raw_i),
        .state_ichlookup_5_out(vld_ichlookup_5_s0_raw_i),
        .state_predictedsize_0_out(vld_predictedsize_0_s0_raw_i),
        .state_predictedsize_1_out(vld_predictedsize_1_s0_raw_i),
        .state_predictedsize_2_out(vld_predictedsize_2_s0_raw_i),
        .state_predictedsize_3_out(vld_predictedsize_3_s0_raw_i),
        .state_rcsizeunit_0_out(vld_rcsizeunit_0_s0_raw_i),
        .state_rcsizeunit_1_out(vld_rcsizeunit_1_s0_raw_i),
        .state_rcsizeunit_2_out(vld_rcsizeunit_2_s0_raw_i),
        .state_rcsizeunit_3_out(vld_rcsizeunit_3_s0_raw_i),
        .state_usemidpoint_0_out(vld_usemidpoint_0_s0_raw_i),
        .state_usemidpoint_1_out(vld_usemidpoint_1_s0_raw_i),
        .state_usemidpoint_2_out(vld_usemidpoint_2_s0_raw_i),
        .state_usemidpoint_3_out(vld_usemidpoint_3_s0_raw_i),
        .quantized_residual_0_out(vld_residual_0_0_raw_i),
        .quantized_residual_1_out(vld_residual_0_1_raw_i),
        .quantized_residual_2_out(vld_residual_0_2_raw_i),
        .fifo_lane_out(vld_fifo_lane_s0_i),
        .fifo_fullness_out(vld_fifo_fullness_s0_i),
        .fifo_read_ptr_out(vld_fifo_read_ptr_s0_i)
    );

    vldunit_decode_transition u_vld_unit_1(
        .unit(32'sd1),
        .cfg_bits_per_component(cfg_bits_per_component),
        .cfg_somewhat_flat_qp_thresh(cfg_somewhat_flat_qp_thresh),
        .cfg_dsc_version_minor(cfg_dsc_version_minor),
        .cfg_native_420(cfg_native_420),
        .cfg_flatness_min_qp(cfg_flatness_min_qp),
        .cfg_flatness_max_qp(cfg_flatness_max_qp),
        .state_firstflat(vld_state_firstflat_s1_i),
        .state_flatnesstype(vld_state_flatnesstype_s1_i),
        .state_groupcount(state_groupcount),
        .state_ichindicesingroup(state_ichindicesingroup),
        .state_ichselected(vld_state_ichselected_s1_i),
        .state_prevfirstflat(vld_state_prevfirstflat_s1_i),
        .state_previchselected(vld_state_previchselected_s1_i),
        .state_primaryqp(state_primaryqp),
        .state_prevprimaryqp(state_prevprimaryqp),
        .state_unitspergroup(state_unitspergroup),
        .state_numbits(vld_state_numbits_s1_i),
        .state_cpntbitdepth_0(state_cpntbitdepth_0),
        .state_cpntbitdepth_1(state_cpntbitdepth_1),
        .state_cpntbitdepth_2(state_cpntbitdepth_2),
        .state_cpntbitdepth_3(state_cpntbitdepth_3),
        .state_unitctype_0(state_unitctype_0),
        .state_unitctype_1(state_unitctype_1),
        .state_unitctype_2(state_unitctype_2),
        .state_unitctype_3(state_unitctype_3),
        .state_unitsspmap_0(state_unitsspmap_0),
        .state_unitsspmap_1(state_unitsspmap_1),
        .state_unitsspmap_2(state_unitsspmap_2),
        .state_unitsspmap_3(state_unitsspmap_3),
        .state_ichindexunitmap_0(state_ichindexunitmap_0),
        .state_ichindexunitmap_1(state_ichindexunitmap_1),
        .state_ichindexunitmap_2(state_ichindexunitmap_2),
        .state_ichindexunitmap_3(state_ichindexunitmap_3),
        .state_ichindexunitmap_4(state_ichindexunitmap_4),
        .state_ichindexunitmap_5(state_ichindexunitmap_5),
        .state_ichlookup_0(vld_state_ichlookup_0_s1_i),
        .state_ichlookup_1(vld_state_ichlookup_1_s1_i),
        .state_ichlookup_2(vld_state_ichlookup_2_s1_i),
        .state_ichlookup_3(vld_state_ichlookup_3_s1_i),
        .state_ichlookup_4(vld_state_ichlookup_4_s1_i),
        .state_ichlookup_5(vld_state_ichlookup_5_s1_i),
        .state_predictedsize_0(vld_state_predictedsize_0_s1_i),
        .state_predictedsize_1(vld_state_predictedsize_1_s1_i),
        .state_predictedsize_2(vld_state_predictedsize_2_s1_i),
        .state_predictedsize_3(vld_state_predictedsize_3_s1_i),
        .state_rcsizeunit_0(vld_state_rcsizeunit_0_s1_i),
        .state_rcsizeunit_1(vld_state_rcsizeunit_1_s1_i),
        .state_rcsizeunit_2(vld_state_rcsizeunit_2_s1_i),
        .state_rcsizeunit_3(vld_state_rcsizeunit_3_s1_i),
        .state_usemidpoint_0(vld_state_usemidpoint_0_s1_i),
        .state_usemidpoint_1(vld_state_usemidpoint_1_s1_i),
        .state_usemidpoint_2(vld_state_usemidpoint_2_s1_i),
        .state_usemidpoint_3(vld_state_usemidpoint_3_s1_i),
        .qlevel_luma_primary(qlevel_luma_primary),
        .qlevel_chroma_primary(qlevel_chroma_primary),
        .qlevel_luma_previous(qlevel_luma_previous),
        .qlevel_chroma_previous(qlevel_chroma_previous),
        .quantized_residual_0(state_quantizedresidual_1_0),
        .quantized_residual_1(state_quantizedresidual_1_1),
        .quantized_residual_2(state_quantizedresidual_1_2),
        .fifo_size(((state_unitsspmap_1 == 32'sd0) ? mux_fifo_0_size_out_i : ((state_unitsspmap_1 == 32'sd1) ? mux_fifo_1_size_out_i : ((state_unitsspmap_1 == 32'sd2) ? mux_fifo_2_size_out_i : mux_fifo_3_size_out_i)))),
        .fifo_fullness(((state_unitsspmap_1 == 32'sd0) ? fifo_0_fullness_s1_i : ((state_unitsspmap_1 == 32'sd1) ? fifo_1_fullness_s1_i : ((state_unitsspmap_1 == 32'sd2) ? fifo_2_fullness_s1_i : fifo_3_fullness_s1_i)))),
        .fifo_read_ptr(((state_unitsspmap_1 == 32'sd0) ? fifo_0_read_ptr_s1_i : ((state_unitsspmap_1 == 32'sd1) ? fifo_1_read_ptr_s1_i : ((state_unitsspmap_1 == 32'sd2) ? fifo_2_read_ptr_s1_i : fifo_3_read_ptr_s1_i)))),
        .fifo_byte_0(((state_unitsspmap_1 == 32'sd0) ? mux_fifo_0_byte_0_out_i : ((state_unitsspmap_1 == 32'sd1) ? mux_fifo_1_byte_0_out_i : ((state_unitsspmap_1 == 32'sd2) ? mux_fifo_2_byte_0_out_i : mux_fifo_3_byte_0_out_i)))),
        .fifo_byte_1(((state_unitsspmap_1 == 32'sd0) ? mux_fifo_0_byte_1_out_i : ((state_unitsspmap_1 == 32'sd1) ? mux_fifo_1_byte_1_out_i : ((state_unitsspmap_1 == 32'sd2) ? mux_fifo_2_byte_1_out_i : mux_fifo_3_byte_1_out_i)))),
        .fifo_byte_2(((state_unitsspmap_1 == 32'sd0) ? mux_fifo_0_byte_2_out_i : ((state_unitsspmap_1 == 32'sd1) ? mux_fifo_1_byte_2_out_i : ((state_unitsspmap_1 == 32'sd2) ? mux_fifo_2_byte_2_out_i : mux_fifo_3_byte_2_out_i)))),
        .fifo_byte_3(((state_unitsspmap_1 == 32'sd0) ? mux_fifo_0_byte_3_out_i : ((state_unitsspmap_1 == 32'sd1) ? mux_fifo_1_byte_3_out_i : ((state_unitsspmap_1 == 32'sd2) ? mux_fifo_2_byte_3_out_i : mux_fifo_3_byte_3_out_i)))),
        .fifo_byte_4(((state_unitsspmap_1 == 32'sd0) ? mux_fifo_0_byte_4_out_i : ((state_unitsspmap_1 == 32'sd1) ? mux_fifo_1_byte_4_out_i : ((state_unitsspmap_1 == 32'sd2) ? mux_fifo_2_byte_4_out_i : mux_fifo_3_byte_4_out_i)))),
        .fifo_byte_5(((state_unitsspmap_1 == 32'sd0) ? mux_fifo_0_byte_5_out_i : ((state_unitsspmap_1 == 32'sd1) ? mux_fifo_1_byte_5_out_i : ((state_unitsspmap_1 == 32'sd2) ? mux_fifo_2_byte_5_out_i : mux_fifo_3_byte_5_out_i)))),
        .fifo_byte_6(((state_unitsspmap_1 == 32'sd0) ? mux_fifo_0_byte_6_out_i : ((state_unitsspmap_1 == 32'sd1) ? mux_fifo_1_byte_6_out_i : ((state_unitsspmap_1 == 32'sd2) ? mux_fifo_2_byte_6_out_i : mux_fifo_3_byte_6_out_i)))),
        .fifo_byte_7(((state_unitsspmap_1 == 32'sd0) ? mux_fifo_0_byte_7_out_i : ((state_unitsspmap_1 == 32'sd1) ? mux_fifo_1_byte_7_out_i : ((state_unitsspmap_1 == 32'sd2) ? mux_fifo_2_byte_7_out_i : mux_fifo_3_byte_7_out_i)))),
        .fifo_byte_8(((state_unitsspmap_1 == 32'sd0) ? mux_fifo_0_byte_8_out_i : ((state_unitsspmap_1 == 32'sd1) ? mux_fifo_1_byte_8_out_i : ((state_unitsspmap_1 == 32'sd2) ? mux_fifo_2_byte_8_out_i : mux_fifo_3_byte_8_out_i)))),
        .fifo_byte_9(((state_unitsspmap_1 == 32'sd0) ? mux_fifo_0_byte_9_out_i : ((state_unitsspmap_1 == 32'sd1) ? mux_fifo_1_byte_9_out_i : ((state_unitsspmap_1 == 32'sd2) ? mux_fifo_2_byte_9_out_i : mux_fifo_3_byte_9_out_i)))),
        .fifo_byte_10(((state_unitsspmap_1 == 32'sd0) ? mux_fifo_0_byte_10_out_i : ((state_unitsspmap_1 == 32'sd1) ? mux_fifo_1_byte_10_out_i : ((state_unitsspmap_1 == 32'sd2) ? mux_fifo_2_byte_10_out_i : mux_fifo_3_byte_10_out_i)))),
        .fifo_byte_11(((state_unitsspmap_1 == 32'sd0) ? mux_fifo_0_byte_11_out_i : ((state_unitsspmap_1 == 32'sd1) ? mux_fifo_1_byte_11_out_i : ((state_unitsspmap_1 == 32'sd2) ? mux_fifo_2_byte_11_out_i : mux_fifo_3_byte_11_out_i)))),
        .fifo_byte_12(((state_unitsspmap_1 == 32'sd0) ? mux_fifo_0_byte_12_out_i : ((state_unitsspmap_1 == 32'sd1) ? mux_fifo_1_byte_12_out_i : ((state_unitsspmap_1 == 32'sd2) ? mux_fifo_2_byte_12_out_i : mux_fifo_3_byte_12_out_i)))),
        .fifo_byte_13(((state_unitsspmap_1 == 32'sd0) ? mux_fifo_0_byte_13_out_i : ((state_unitsspmap_1 == 32'sd1) ? mux_fifo_1_byte_13_out_i : ((state_unitsspmap_1 == 32'sd2) ? mux_fifo_2_byte_13_out_i : mux_fifo_3_byte_13_out_i)))),
        .fifo_byte_14(((state_unitsspmap_1 == 32'sd0) ? mux_fifo_0_byte_14_out_i : ((state_unitsspmap_1 == 32'sd1) ? mux_fifo_1_byte_14_out_i : ((state_unitsspmap_1 == 32'sd2) ? mux_fifo_2_byte_14_out_i : mux_fifo_3_byte_14_out_i)))),
        .fifo_byte_15(((state_unitsspmap_1 == 32'sd0) ? mux_fifo_0_byte_15_out_i : ((state_unitsspmap_1 == 32'sd1) ? mux_fifo_1_byte_15_out_i : ((state_unitsspmap_1 == 32'sd2) ? mux_fifo_2_byte_15_out_i : mux_fifo_3_byte_15_out_i)))),
        .fifo_byte_16(((state_unitsspmap_1 == 32'sd0) ? mux_fifo_0_byte_16_out_i : ((state_unitsspmap_1 == 32'sd1) ? mux_fifo_1_byte_16_out_i : ((state_unitsspmap_1 == 32'sd2) ? mux_fifo_2_byte_16_out_i : mux_fifo_3_byte_16_out_i)))),
        .domain_valid(vld_domain_s1_i),
        .state_firstflat_out(vld_firstflat_s1_raw_i),
        .state_flatnesstype_out(vld_flatnesstype_s1_raw_i),
        .state_ichselected_out(vld_ichselected_s1_raw_i),
        .state_prevfirstflat_out(vld_prevfirstflat_s1_raw_i),
        .state_previchselected_out(vld_previchselected_s1_raw_i),
        .state_numbits_out(vld_numbits_s1_raw_i),
        .state_ichlookup_0_out(vld_ichlookup_0_s1_raw_i),
        .state_ichlookup_1_out(vld_ichlookup_1_s1_raw_i),
        .state_ichlookup_2_out(vld_ichlookup_2_s1_raw_i),
        .state_ichlookup_3_out(vld_ichlookup_3_s1_raw_i),
        .state_ichlookup_4_out(vld_ichlookup_4_s1_raw_i),
        .state_ichlookup_5_out(vld_ichlookup_5_s1_raw_i),
        .state_predictedsize_0_out(vld_predictedsize_0_s1_raw_i),
        .state_predictedsize_1_out(vld_predictedsize_1_s1_raw_i),
        .state_predictedsize_2_out(vld_predictedsize_2_s1_raw_i),
        .state_predictedsize_3_out(vld_predictedsize_3_s1_raw_i),
        .state_rcsizeunit_0_out(vld_rcsizeunit_0_s1_raw_i),
        .state_rcsizeunit_1_out(vld_rcsizeunit_1_s1_raw_i),
        .state_rcsizeunit_2_out(vld_rcsizeunit_2_s1_raw_i),
        .state_rcsizeunit_3_out(vld_rcsizeunit_3_s1_raw_i),
        .state_usemidpoint_0_out(vld_usemidpoint_0_s1_raw_i),
        .state_usemidpoint_1_out(vld_usemidpoint_1_s1_raw_i),
        .state_usemidpoint_2_out(vld_usemidpoint_2_s1_raw_i),
        .state_usemidpoint_3_out(vld_usemidpoint_3_s1_raw_i),
        .quantized_residual_0_out(vld_residual_1_0_raw_i),
        .quantized_residual_1_out(vld_residual_1_1_raw_i),
        .quantized_residual_2_out(vld_residual_1_2_raw_i),
        .fifo_lane_out(vld_fifo_lane_s1_i),
        .fifo_fullness_out(vld_fifo_fullness_s1_i),
        .fifo_read_ptr_out(vld_fifo_read_ptr_s1_i)
    );

    vldunit_decode_transition u_vld_unit_2(
        .unit(32'sd2),
        .cfg_bits_per_component(cfg_bits_per_component),
        .cfg_somewhat_flat_qp_thresh(cfg_somewhat_flat_qp_thresh),
        .cfg_dsc_version_minor(cfg_dsc_version_minor),
        .cfg_native_420(cfg_native_420),
        .cfg_flatness_min_qp(cfg_flatness_min_qp),
        .cfg_flatness_max_qp(cfg_flatness_max_qp),
        .state_firstflat(vld_state_firstflat_s2_i),
        .state_flatnesstype(vld_state_flatnesstype_s2_i),
        .state_groupcount(state_groupcount),
        .state_ichindicesingroup(state_ichindicesingroup),
        .state_ichselected(vld_state_ichselected_s2_i),
        .state_prevfirstflat(vld_state_prevfirstflat_s2_i),
        .state_previchselected(vld_state_previchselected_s2_i),
        .state_primaryqp(state_primaryqp),
        .state_prevprimaryqp(state_prevprimaryqp),
        .state_unitspergroup(state_unitspergroup),
        .state_numbits(vld_state_numbits_s2_i),
        .state_cpntbitdepth_0(state_cpntbitdepth_0),
        .state_cpntbitdepth_1(state_cpntbitdepth_1),
        .state_cpntbitdepth_2(state_cpntbitdepth_2),
        .state_cpntbitdepth_3(state_cpntbitdepth_3),
        .state_unitctype_0(state_unitctype_0),
        .state_unitctype_1(state_unitctype_1),
        .state_unitctype_2(state_unitctype_2),
        .state_unitctype_3(state_unitctype_3),
        .state_unitsspmap_0(state_unitsspmap_0),
        .state_unitsspmap_1(state_unitsspmap_1),
        .state_unitsspmap_2(state_unitsspmap_2),
        .state_unitsspmap_3(state_unitsspmap_3),
        .state_ichindexunitmap_0(state_ichindexunitmap_0),
        .state_ichindexunitmap_1(state_ichindexunitmap_1),
        .state_ichindexunitmap_2(state_ichindexunitmap_2),
        .state_ichindexunitmap_3(state_ichindexunitmap_3),
        .state_ichindexunitmap_4(state_ichindexunitmap_4),
        .state_ichindexunitmap_5(state_ichindexunitmap_5),
        .state_ichlookup_0(vld_state_ichlookup_0_s2_i),
        .state_ichlookup_1(vld_state_ichlookup_1_s2_i),
        .state_ichlookup_2(vld_state_ichlookup_2_s2_i),
        .state_ichlookup_3(vld_state_ichlookup_3_s2_i),
        .state_ichlookup_4(vld_state_ichlookup_4_s2_i),
        .state_ichlookup_5(vld_state_ichlookup_5_s2_i),
        .state_predictedsize_0(vld_state_predictedsize_0_s2_i),
        .state_predictedsize_1(vld_state_predictedsize_1_s2_i),
        .state_predictedsize_2(vld_state_predictedsize_2_s2_i),
        .state_predictedsize_3(vld_state_predictedsize_3_s2_i),
        .state_rcsizeunit_0(vld_state_rcsizeunit_0_s2_i),
        .state_rcsizeunit_1(vld_state_rcsizeunit_1_s2_i),
        .state_rcsizeunit_2(vld_state_rcsizeunit_2_s2_i),
        .state_rcsizeunit_3(vld_state_rcsizeunit_3_s2_i),
        .state_usemidpoint_0(vld_state_usemidpoint_0_s2_i),
        .state_usemidpoint_1(vld_state_usemidpoint_1_s2_i),
        .state_usemidpoint_2(vld_state_usemidpoint_2_s2_i),
        .state_usemidpoint_3(vld_state_usemidpoint_3_s2_i),
        .qlevel_luma_primary(qlevel_luma_primary),
        .qlevel_chroma_primary(qlevel_chroma_primary),
        .qlevel_luma_previous(qlevel_luma_previous),
        .qlevel_chroma_previous(qlevel_chroma_previous),
        .quantized_residual_0(state_quantizedresidual_2_0),
        .quantized_residual_1(state_quantizedresidual_2_1),
        .quantized_residual_2(state_quantizedresidual_2_2),
        .fifo_size(((state_unitsspmap_2 == 32'sd0) ? mux_fifo_0_size_out_i : ((state_unitsspmap_2 == 32'sd1) ? mux_fifo_1_size_out_i : ((state_unitsspmap_2 == 32'sd2) ? mux_fifo_2_size_out_i : mux_fifo_3_size_out_i)))),
        .fifo_fullness(((state_unitsspmap_2 == 32'sd0) ? fifo_0_fullness_s2_i : ((state_unitsspmap_2 == 32'sd1) ? fifo_1_fullness_s2_i : ((state_unitsspmap_2 == 32'sd2) ? fifo_2_fullness_s2_i : fifo_3_fullness_s2_i)))),
        .fifo_read_ptr(((state_unitsspmap_2 == 32'sd0) ? fifo_0_read_ptr_s2_i : ((state_unitsspmap_2 == 32'sd1) ? fifo_1_read_ptr_s2_i : ((state_unitsspmap_2 == 32'sd2) ? fifo_2_read_ptr_s2_i : fifo_3_read_ptr_s2_i)))),
        .fifo_byte_0(((state_unitsspmap_2 == 32'sd0) ? mux_fifo_0_byte_0_out_i : ((state_unitsspmap_2 == 32'sd1) ? mux_fifo_1_byte_0_out_i : ((state_unitsspmap_2 == 32'sd2) ? mux_fifo_2_byte_0_out_i : mux_fifo_3_byte_0_out_i)))),
        .fifo_byte_1(((state_unitsspmap_2 == 32'sd0) ? mux_fifo_0_byte_1_out_i : ((state_unitsspmap_2 == 32'sd1) ? mux_fifo_1_byte_1_out_i : ((state_unitsspmap_2 == 32'sd2) ? mux_fifo_2_byte_1_out_i : mux_fifo_3_byte_1_out_i)))),
        .fifo_byte_2(((state_unitsspmap_2 == 32'sd0) ? mux_fifo_0_byte_2_out_i : ((state_unitsspmap_2 == 32'sd1) ? mux_fifo_1_byte_2_out_i : ((state_unitsspmap_2 == 32'sd2) ? mux_fifo_2_byte_2_out_i : mux_fifo_3_byte_2_out_i)))),
        .fifo_byte_3(((state_unitsspmap_2 == 32'sd0) ? mux_fifo_0_byte_3_out_i : ((state_unitsspmap_2 == 32'sd1) ? mux_fifo_1_byte_3_out_i : ((state_unitsspmap_2 == 32'sd2) ? mux_fifo_2_byte_3_out_i : mux_fifo_3_byte_3_out_i)))),
        .fifo_byte_4(((state_unitsspmap_2 == 32'sd0) ? mux_fifo_0_byte_4_out_i : ((state_unitsspmap_2 == 32'sd1) ? mux_fifo_1_byte_4_out_i : ((state_unitsspmap_2 == 32'sd2) ? mux_fifo_2_byte_4_out_i : mux_fifo_3_byte_4_out_i)))),
        .fifo_byte_5(((state_unitsspmap_2 == 32'sd0) ? mux_fifo_0_byte_5_out_i : ((state_unitsspmap_2 == 32'sd1) ? mux_fifo_1_byte_5_out_i : ((state_unitsspmap_2 == 32'sd2) ? mux_fifo_2_byte_5_out_i : mux_fifo_3_byte_5_out_i)))),
        .fifo_byte_6(((state_unitsspmap_2 == 32'sd0) ? mux_fifo_0_byte_6_out_i : ((state_unitsspmap_2 == 32'sd1) ? mux_fifo_1_byte_6_out_i : ((state_unitsspmap_2 == 32'sd2) ? mux_fifo_2_byte_6_out_i : mux_fifo_3_byte_6_out_i)))),
        .fifo_byte_7(((state_unitsspmap_2 == 32'sd0) ? mux_fifo_0_byte_7_out_i : ((state_unitsspmap_2 == 32'sd1) ? mux_fifo_1_byte_7_out_i : ((state_unitsspmap_2 == 32'sd2) ? mux_fifo_2_byte_7_out_i : mux_fifo_3_byte_7_out_i)))),
        .fifo_byte_8(((state_unitsspmap_2 == 32'sd0) ? mux_fifo_0_byte_8_out_i : ((state_unitsspmap_2 == 32'sd1) ? mux_fifo_1_byte_8_out_i : ((state_unitsspmap_2 == 32'sd2) ? mux_fifo_2_byte_8_out_i : mux_fifo_3_byte_8_out_i)))),
        .fifo_byte_9(((state_unitsspmap_2 == 32'sd0) ? mux_fifo_0_byte_9_out_i : ((state_unitsspmap_2 == 32'sd1) ? mux_fifo_1_byte_9_out_i : ((state_unitsspmap_2 == 32'sd2) ? mux_fifo_2_byte_9_out_i : mux_fifo_3_byte_9_out_i)))),
        .fifo_byte_10(((state_unitsspmap_2 == 32'sd0) ? mux_fifo_0_byte_10_out_i : ((state_unitsspmap_2 == 32'sd1) ? mux_fifo_1_byte_10_out_i : ((state_unitsspmap_2 == 32'sd2) ? mux_fifo_2_byte_10_out_i : mux_fifo_3_byte_10_out_i)))),
        .fifo_byte_11(((state_unitsspmap_2 == 32'sd0) ? mux_fifo_0_byte_11_out_i : ((state_unitsspmap_2 == 32'sd1) ? mux_fifo_1_byte_11_out_i : ((state_unitsspmap_2 == 32'sd2) ? mux_fifo_2_byte_11_out_i : mux_fifo_3_byte_11_out_i)))),
        .fifo_byte_12(((state_unitsspmap_2 == 32'sd0) ? mux_fifo_0_byte_12_out_i : ((state_unitsspmap_2 == 32'sd1) ? mux_fifo_1_byte_12_out_i : ((state_unitsspmap_2 == 32'sd2) ? mux_fifo_2_byte_12_out_i : mux_fifo_3_byte_12_out_i)))),
        .fifo_byte_13(((state_unitsspmap_2 == 32'sd0) ? mux_fifo_0_byte_13_out_i : ((state_unitsspmap_2 == 32'sd1) ? mux_fifo_1_byte_13_out_i : ((state_unitsspmap_2 == 32'sd2) ? mux_fifo_2_byte_13_out_i : mux_fifo_3_byte_13_out_i)))),
        .fifo_byte_14(((state_unitsspmap_2 == 32'sd0) ? mux_fifo_0_byte_14_out_i : ((state_unitsspmap_2 == 32'sd1) ? mux_fifo_1_byte_14_out_i : ((state_unitsspmap_2 == 32'sd2) ? mux_fifo_2_byte_14_out_i : mux_fifo_3_byte_14_out_i)))),
        .fifo_byte_15(((state_unitsspmap_2 == 32'sd0) ? mux_fifo_0_byte_15_out_i : ((state_unitsspmap_2 == 32'sd1) ? mux_fifo_1_byte_15_out_i : ((state_unitsspmap_2 == 32'sd2) ? mux_fifo_2_byte_15_out_i : mux_fifo_3_byte_15_out_i)))),
        .fifo_byte_16(((state_unitsspmap_2 == 32'sd0) ? mux_fifo_0_byte_16_out_i : ((state_unitsspmap_2 == 32'sd1) ? mux_fifo_1_byte_16_out_i : ((state_unitsspmap_2 == 32'sd2) ? mux_fifo_2_byte_16_out_i : mux_fifo_3_byte_16_out_i)))),
        .domain_valid(vld_domain_s2_i),
        .state_firstflat_out(vld_firstflat_s2_raw_i),
        .state_flatnesstype_out(vld_flatnesstype_s2_raw_i),
        .state_ichselected_out(vld_ichselected_s2_raw_i),
        .state_prevfirstflat_out(vld_prevfirstflat_s2_raw_i),
        .state_previchselected_out(vld_previchselected_s2_raw_i),
        .state_numbits_out(vld_numbits_s2_raw_i),
        .state_ichlookup_0_out(vld_ichlookup_0_s2_raw_i),
        .state_ichlookup_1_out(vld_ichlookup_1_s2_raw_i),
        .state_ichlookup_2_out(vld_ichlookup_2_s2_raw_i),
        .state_ichlookup_3_out(vld_ichlookup_3_s2_raw_i),
        .state_ichlookup_4_out(vld_ichlookup_4_s2_raw_i),
        .state_ichlookup_5_out(vld_ichlookup_5_s2_raw_i),
        .state_predictedsize_0_out(vld_predictedsize_0_s2_raw_i),
        .state_predictedsize_1_out(vld_predictedsize_1_s2_raw_i),
        .state_predictedsize_2_out(vld_predictedsize_2_s2_raw_i),
        .state_predictedsize_3_out(vld_predictedsize_3_s2_raw_i),
        .state_rcsizeunit_0_out(vld_rcsizeunit_0_s2_raw_i),
        .state_rcsizeunit_1_out(vld_rcsizeunit_1_s2_raw_i),
        .state_rcsizeunit_2_out(vld_rcsizeunit_2_s2_raw_i),
        .state_rcsizeunit_3_out(vld_rcsizeunit_3_s2_raw_i),
        .state_usemidpoint_0_out(vld_usemidpoint_0_s2_raw_i),
        .state_usemidpoint_1_out(vld_usemidpoint_1_s2_raw_i),
        .state_usemidpoint_2_out(vld_usemidpoint_2_s2_raw_i),
        .state_usemidpoint_3_out(vld_usemidpoint_3_s2_raw_i),
        .quantized_residual_0_out(vld_residual_2_0_raw_i),
        .quantized_residual_1_out(vld_residual_2_1_raw_i),
        .quantized_residual_2_out(vld_residual_2_2_raw_i),
        .fifo_lane_out(vld_fifo_lane_s2_i),
        .fifo_fullness_out(vld_fifo_fullness_s2_i),
        .fifo_read_ptr_out(vld_fifo_read_ptr_s2_i)
    );

    vldunit_decode_transition u_vld_unit_3(
        .unit(32'sd3),
        .cfg_bits_per_component(cfg_bits_per_component),
        .cfg_somewhat_flat_qp_thresh(cfg_somewhat_flat_qp_thresh),
        .cfg_dsc_version_minor(cfg_dsc_version_minor),
        .cfg_native_420(cfg_native_420),
        .cfg_flatness_min_qp(cfg_flatness_min_qp),
        .cfg_flatness_max_qp(cfg_flatness_max_qp),
        .state_firstflat(vld_state_firstflat_s3_i),
        .state_flatnesstype(vld_state_flatnesstype_s3_i),
        .state_groupcount(state_groupcount),
        .state_ichindicesingroup(state_ichindicesingroup),
        .state_ichselected(vld_state_ichselected_s3_i),
        .state_prevfirstflat(vld_state_prevfirstflat_s3_i),
        .state_previchselected(vld_state_previchselected_s3_i),
        .state_primaryqp(state_primaryqp),
        .state_prevprimaryqp(state_prevprimaryqp),
        .state_unitspergroup(state_unitspergroup),
        .state_numbits(vld_state_numbits_s3_i),
        .state_cpntbitdepth_0(state_cpntbitdepth_0),
        .state_cpntbitdepth_1(state_cpntbitdepth_1),
        .state_cpntbitdepth_2(state_cpntbitdepth_2),
        .state_cpntbitdepth_3(state_cpntbitdepth_3),
        .state_unitctype_0(state_unitctype_0),
        .state_unitctype_1(state_unitctype_1),
        .state_unitctype_2(state_unitctype_2),
        .state_unitctype_3(state_unitctype_3),
        .state_unitsspmap_0(state_unitsspmap_0),
        .state_unitsspmap_1(state_unitsspmap_1),
        .state_unitsspmap_2(state_unitsspmap_2),
        .state_unitsspmap_3(state_unitsspmap_3),
        .state_ichindexunitmap_0(state_ichindexunitmap_0),
        .state_ichindexunitmap_1(state_ichindexunitmap_1),
        .state_ichindexunitmap_2(state_ichindexunitmap_2),
        .state_ichindexunitmap_3(state_ichindexunitmap_3),
        .state_ichindexunitmap_4(state_ichindexunitmap_4),
        .state_ichindexunitmap_5(state_ichindexunitmap_5),
        .state_ichlookup_0(vld_state_ichlookup_0_s3_i),
        .state_ichlookup_1(vld_state_ichlookup_1_s3_i),
        .state_ichlookup_2(vld_state_ichlookup_2_s3_i),
        .state_ichlookup_3(vld_state_ichlookup_3_s3_i),
        .state_ichlookup_4(vld_state_ichlookup_4_s3_i),
        .state_ichlookup_5(vld_state_ichlookup_5_s3_i),
        .state_predictedsize_0(vld_state_predictedsize_0_s3_i),
        .state_predictedsize_1(vld_state_predictedsize_1_s3_i),
        .state_predictedsize_2(vld_state_predictedsize_2_s3_i),
        .state_predictedsize_3(vld_state_predictedsize_3_s3_i),
        .state_rcsizeunit_0(vld_state_rcsizeunit_0_s3_i),
        .state_rcsizeunit_1(vld_state_rcsizeunit_1_s3_i),
        .state_rcsizeunit_2(vld_state_rcsizeunit_2_s3_i),
        .state_rcsizeunit_3(vld_state_rcsizeunit_3_s3_i),
        .state_usemidpoint_0(vld_state_usemidpoint_0_s3_i),
        .state_usemidpoint_1(vld_state_usemidpoint_1_s3_i),
        .state_usemidpoint_2(vld_state_usemidpoint_2_s3_i),
        .state_usemidpoint_3(vld_state_usemidpoint_3_s3_i),
        .qlevel_luma_primary(qlevel_luma_primary),
        .qlevel_chroma_primary(qlevel_chroma_primary),
        .qlevel_luma_previous(qlevel_luma_previous),
        .qlevel_chroma_previous(qlevel_chroma_previous),
        .quantized_residual_0(state_quantizedresidual_3_0),
        .quantized_residual_1(state_quantizedresidual_3_1),
        .quantized_residual_2(state_quantizedresidual_3_2),
        .fifo_size(((state_unitsspmap_3 == 32'sd0) ? mux_fifo_0_size_out_i : ((state_unitsspmap_3 == 32'sd1) ? mux_fifo_1_size_out_i : ((state_unitsspmap_3 == 32'sd2) ? mux_fifo_2_size_out_i : mux_fifo_3_size_out_i)))),
        .fifo_fullness(((state_unitsspmap_3 == 32'sd0) ? fifo_0_fullness_s3_i : ((state_unitsspmap_3 == 32'sd1) ? fifo_1_fullness_s3_i : ((state_unitsspmap_3 == 32'sd2) ? fifo_2_fullness_s3_i : fifo_3_fullness_s3_i)))),
        .fifo_read_ptr(((state_unitsspmap_3 == 32'sd0) ? fifo_0_read_ptr_s3_i : ((state_unitsspmap_3 == 32'sd1) ? fifo_1_read_ptr_s3_i : ((state_unitsspmap_3 == 32'sd2) ? fifo_2_read_ptr_s3_i : fifo_3_read_ptr_s3_i)))),
        .fifo_byte_0(((state_unitsspmap_3 == 32'sd0) ? mux_fifo_0_byte_0_out_i : ((state_unitsspmap_3 == 32'sd1) ? mux_fifo_1_byte_0_out_i : ((state_unitsspmap_3 == 32'sd2) ? mux_fifo_2_byte_0_out_i : mux_fifo_3_byte_0_out_i)))),
        .fifo_byte_1(((state_unitsspmap_3 == 32'sd0) ? mux_fifo_0_byte_1_out_i : ((state_unitsspmap_3 == 32'sd1) ? mux_fifo_1_byte_1_out_i : ((state_unitsspmap_3 == 32'sd2) ? mux_fifo_2_byte_1_out_i : mux_fifo_3_byte_1_out_i)))),
        .fifo_byte_2(((state_unitsspmap_3 == 32'sd0) ? mux_fifo_0_byte_2_out_i : ((state_unitsspmap_3 == 32'sd1) ? mux_fifo_1_byte_2_out_i : ((state_unitsspmap_3 == 32'sd2) ? mux_fifo_2_byte_2_out_i : mux_fifo_3_byte_2_out_i)))),
        .fifo_byte_3(((state_unitsspmap_3 == 32'sd0) ? mux_fifo_0_byte_3_out_i : ((state_unitsspmap_3 == 32'sd1) ? mux_fifo_1_byte_3_out_i : ((state_unitsspmap_3 == 32'sd2) ? mux_fifo_2_byte_3_out_i : mux_fifo_3_byte_3_out_i)))),
        .fifo_byte_4(((state_unitsspmap_3 == 32'sd0) ? mux_fifo_0_byte_4_out_i : ((state_unitsspmap_3 == 32'sd1) ? mux_fifo_1_byte_4_out_i : ((state_unitsspmap_3 == 32'sd2) ? mux_fifo_2_byte_4_out_i : mux_fifo_3_byte_4_out_i)))),
        .fifo_byte_5(((state_unitsspmap_3 == 32'sd0) ? mux_fifo_0_byte_5_out_i : ((state_unitsspmap_3 == 32'sd1) ? mux_fifo_1_byte_5_out_i : ((state_unitsspmap_3 == 32'sd2) ? mux_fifo_2_byte_5_out_i : mux_fifo_3_byte_5_out_i)))),
        .fifo_byte_6(((state_unitsspmap_3 == 32'sd0) ? mux_fifo_0_byte_6_out_i : ((state_unitsspmap_3 == 32'sd1) ? mux_fifo_1_byte_6_out_i : ((state_unitsspmap_3 == 32'sd2) ? mux_fifo_2_byte_6_out_i : mux_fifo_3_byte_6_out_i)))),
        .fifo_byte_7(((state_unitsspmap_3 == 32'sd0) ? mux_fifo_0_byte_7_out_i : ((state_unitsspmap_3 == 32'sd1) ? mux_fifo_1_byte_7_out_i : ((state_unitsspmap_3 == 32'sd2) ? mux_fifo_2_byte_7_out_i : mux_fifo_3_byte_7_out_i)))),
        .fifo_byte_8(((state_unitsspmap_3 == 32'sd0) ? mux_fifo_0_byte_8_out_i : ((state_unitsspmap_3 == 32'sd1) ? mux_fifo_1_byte_8_out_i : ((state_unitsspmap_3 == 32'sd2) ? mux_fifo_2_byte_8_out_i : mux_fifo_3_byte_8_out_i)))),
        .fifo_byte_9(((state_unitsspmap_3 == 32'sd0) ? mux_fifo_0_byte_9_out_i : ((state_unitsspmap_3 == 32'sd1) ? mux_fifo_1_byte_9_out_i : ((state_unitsspmap_3 == 32'sd2) ? mux_fifo_2_byte_9_out_i : mux_fifo_3_byte_9_out_i)))),
        .fifo_byte_10(((state_unitsspmap_3 == 32'sd0) ? mux_fifo_0_byte_10_out_i : ((state_unitsspmap_3 == 32'sd1) ? mux_fifo_1_byte_10_out_i : ((state_unitsspmap_3 == 32'sd2) ? mux_fifo_2_byte_10_out_i : mux_fifo_3_byte_10_out_i)))),
        .fifo_byte_11(((state_unitsspmap_3 == 32'sd0) ? mux_fifo_0_byte_11_out_i : ((state_unitsspmap_3 == 32'sd1) ? mux_fifo_1_byte_11_out_i : ((state_unitsspmap_3 == 32'sd2) ? mux_fifo_2_byte_11_out_i : mux_fifo_3_byte_11_out_i)))),
        .fifo_byte_12(((state_unitsspmap_3 == 32'sd0) ? mux_fifo_0_byte_12_out_i : ((state_unitsspmap_3 == 32'sd1) ? mux_fifo_1_byte_12_out_i : ((state_unitsspmap_3 == 32'sd2) ? mux_fifo_2_byte_12_out_i : mux_fifo_3_byte_12_out_i)))),
        .fifo_byte_13(((state_unitsspmap_3 == 32'sd0) ? mux_fifo_0_byte_13_out_i : ((state_unitsspmap_3 == 32'sd1) ? mux_fifo_1_byte_13_out_i : ((state_unitsspmap_3 == 32'sd2) ? mux_fifo_2_byte_13_out_i : mux_fifo_3_byte_13_out_i)))),
        .fifo_byte_14(((state_unitsspmap_3 == 32'sd0) ? mux_fifo_0_byte_14_out_i : ((state_unitsspmap_3 == 32'sd1) ? mux_fifo_1_byte_14_out_i : ((state_unitsspmap_3 == 32'sd2) ? mux_fifo_2_byte_14_out_i : mux_fifo_3_byte_14_out_i)))),
        .fifo_byte_15(((state_unitsspmap_3 == 32'sd0) ? mux_fifo_0_byte_15_out_i : ((state_unitsspmap_3 == 32'sd1) ? mux_fifo_1_byte_15_out_i : ((state_unitsspmap_3 == 32'sd2) ? mux_fifo_2_byte_15_out_i : mux_fifo_3_byte_15_out_i)))),
        .fifo_byte_16(((state_unitsspmap_3 == 32'sd0) ? mux_fifo_0_byte_16_out_i : ((state_unitsspmap_3 == 32'sd1) ? mux_fifo_1_byte_16_out_i : ((state_unitsspmap_3 == 32'sd2) ? mux_fifo_2_byte_16_out_i : mux_fifo_3_byte_16_out_i)))),
        .domain_valid(vld_domain_s3_i),
        .state_firstflat_out(vld_firstflat_s3_raw_i),
        .state_flatnesstype_out(vld_flatnesstype_s3_raw_i),
        .state_ichselected_out(vld_ichselected_s3_raw_i),
        .state_prevfirstflat_out(vld_prevfirstflat_s3_raw_i),
        .state_previchselected_out(vld_previchselected_s3_raw_i),
        .state_numbits_out(vld_numbits_s3_raw_i),
        .state_ichlookup_0_out(vld_ichlookup_0_s3_raw_i),
        .state_ichlookup_1_out(vld_ichlookup_1_s3_raw_i),
        .state_ichlookup_2_out(vld_ichlookup_2_s3_raw_i),
        .state_ichlookup_3_out(vld_ichlookup_3_s3_raw_i),
        .state_ichlookup_4_out(vld_ichlookup_4_s3_raw_i),
        .state_ichlookup_5_out(vld_ichlookup_5_s3_raw_i),
        .state_predictedsize_0_out(vld_predictedsize_0_s3_raw_i),
        .state_predictedsize_1_out(vld_predictedsize_1_s3_raw_i),
        .state_predictedsize_2_out(vld_predictedsize_2_s3_raw_i),
        .state_predictedsize_3_out(vld_predictedsize_3_s3_raw_i),
        .state_rcsizeunit_0_out(vld_rcsizeunit_0_s3_raw_i),
        .state_rcsizeunit_1_out(vld_rcsizeunit_1_s3_raw_i),
        .state_rcsizeunit_2_out(vld_rcsizeunit_2_s3_raw_i),
        .state_rcsizeunit_3_out(vld_rcsizeunit_3_s3_raw_i),
        .state_usemidpoint_0_out(vld_usemidpoint_0_s3_raw_i),
        .state_usemidpoint_1_out(vld_usemidpoint_1_s3_raw_i),
        .state_usemidpoint_2_out(vld_usemidpoint_2_s3_raw_i),
        .state_usemidpoint_3_out(vld_usemidpoint_3_s3_raw_i),
        .quantized_residual_0_out(vld_residual_3_0_raw_i),
        .quantized_residual_1_out(vld_residual_3_1_raw_i),
        .quantized_residual_2_out(vld_residual_3_2_raw_i),
        .fifo_lane_out(vld_fifo_lane_s3_i),
        .fifo_fullness_out(vld_fifo_fullness_s3_i),
        .fifo_read_ptr_out(vld_fifo_read_ptr_s3_i)
    );

    assign vld_state_firstflat_s0_i = state_firstflat;
    assign vld_state_flatnesstype_s0_i = state_flatnesstype;
    assign vld_state_ichselected_s0_i = state_ichselected;
    assign vld_state_numbits_s0_i = state_numbits;
    assign vld_state_prevfirstflat_s0_i = state_prevfirstflat;
    assign vld_state_previchselected_s0_i = state_previchselected;
    assign vld_state_ichlookup_0_s0_i = state_ichlookup_0;
    assign vld_state_ichlookup_1_s0_i = state_ichlookup_1;
    assign vld_state_ichlookup_2_s0_i = state_ichlookup_2;
    assign vld_state_ichlookup_3_s0_i = state_ichlookup_3;
    assign vld_state_ichlookup_4_s0_i = state_ichlookup_4;
    assign vld_state_ichlookup_5_s0_i = state_ichlookup_5;
    assign vld_state_predictedsize_0_s0_i = state_predictedsize_0;
    assign vld_state_predictedsize_1_s0_i = state_predictedsize_1;
    assign vld_state_predictedsize_2_s0_i = state_predictedsize_2;
    assign vld_state_predictedsize_3_s0_i = state_predictedsize_3;
    assign vld_state_rcsizeunit_0_s0_i = state_rcsizeunit_0;
    assign vld_state_rcsizeunit_1_s0_i = state_rcsizeunit_1;
    assign vld_state_rcsizeunit_2_s0_i = state_rcsizeunit_2;
    assign vld_state_rcsizeunit_3_s0_i = state_rcsizeunit_3;
    assign vld_state_usemidpoint_0_s0_i = state_usemidpoint_0;
    assign vld_state_usemidpoint_1_s0_i = state_usemidpoint_1;
    assign vld_state_usemidpoint_2_s0_i = state_usemidpoint_2;
    assign vld_state_usemidpoint_3_s0_i = state_usemidpoint_3;
    assign fifo_0_fullness_s0_i = $signed(mux_fifo_0_fullness_out_i);
    assign fifo_0_read_ptr_s0_i = $signed(mux_fifo_0_read_ptr_out_i);
    assign fifo_1_fullness_s0_i = $signed(mux_fifo_1_fullness_out_i);
    assign fifo_1_read_ptr_s0_i = $signed(mux_fifo_1_read_ptr_out_i);
    assign fifo_2_fullness_s0_i = $signed(mux_fifo_2_fullness_out_i);
    assign fifo_2_read_ptr_s0_i = $signed(mux_fifo_2_read_ptr_out_i);
    assign fifo_3_fullness_s0_i = $signed(mux_fifo_3_fullness_out_i);
    assign fifo_3_read_ptr_s0_i = $signed(mux_fifo_3_read_ptr_out_i);
    assign vld_state_firstflat_s1_i = ($signed(state_unitspergroup) > 32'sd0) ? vld_firstflat_s0_raw_i : vld_state_firstflat_s0_i;
    assign vld_state_flatnesstype_s1_i = ($signed(state_unitspergroup) > 32'sd0) ? vld_flatnesstype_s0_raw_i : vld_state_flatnesstype_s0_i;
    assign vld_state_ichselected_s1_i = ($signed(state_unitspergroup) > 32'sd0) ? vld_ichselected_s0_raw_i : vld_state_ichselected_s0_i;
    assign vld_state_numbits_s1_i = ($signed(state_unitspergroup) > 32'sd0) ? vld_numbits_s0_raw_i : vld_state_numbits_s0_i;
    assign vld_state_prevfirstflat_s1_i = ($signed(state_unitspergroup) > 32'sd0) ? vld_prevfirstflat_s0_raw_i : vld_state_prevfirstflat_s0_i;
    assign vld_state_previchselected_s1_i = ($signed(state_unitspergroup) > 32'sd0) ? vld_previchselected_s0_raw_i : vld_state_previchselected_s0_i;
    assign vld_state_ichlookup_0_s1_i = ($signed(state_unitspergroup) > 32'sd0) ? vld_ichlookup_0_s0_raw_i : vld_state_ichlookup_0_s0_i;
    assign vld_state_ichlookup_1_s1_i = ($signed(state_unitspergroup) > 32'sd0) ? vld_ichlookup_1_s0_raw_i : vld_state_ichlookup_1_s0_i;
    assign vld_state_ichlookup_2_s1_i = ($signed(state_unitspergroup) > 32'sd0) ? vld_ichlookup_2_s0_raw_i : vld_state_ichlookup_2_s0_i;
    assign vld_state_ichlookup_3_s1_i = ($signed(state_unitspergroup) > 32'sd0) ? vld_ichlookup_3_s0_raw_i : vld_state_ichlookup_3_s0_i;
    assign vld_state_ichlookup_4_s1_i = ($signed(state_unitspergroup) > 32'sd0) ? vld_ichlookup_4_s0_raw_i : vld_state_ichlookup_4_s0_i;
    assign vld_state_ichlookup_5_s1_i = ($signed(state_unitspergroup) > 32'sd0) ? vld_ichlookup_5_s0_raw_i : vld_state_ichlookup_5_s0_i;
    assign vld_state_predictedsize_0_s1_i = ($signed(state_unitspergroup) > 32'sd0) ? vld_predictedsize_0_s0_raw_i : vld_state_predictedsize_0_s0_i;
    assign vld_state_predictedsize_1_s1_i = ($signed(state_unitspergroup) > 32'sd0) ? vld_predictedsize_1_s0_raw_i : vld_state_predictedsize_1_s0_i;
    assign vld_state_predictedsize_2_s1_i = ($signed(state_unitspergroup) > 32'sd0) ? vld_predictedsize_2_s0_raw_i : vld_state_predictedsize_2_s0_i;
    assign vld_state_predictedsize_3_s1_i = ($signed(state_unitspergroup) > 32'sd0) ? vld_predictedsize_3_s0_raw_i : vld_state_predictedsize_3_s0_i;
    assign vld_state_rcsizeunit_0_s1_i = ($signed(state_unitspergroup) > 32'sd0) ? vld_rcsizeunit_0_s0_raw_i : vld_state_rcsizeunit_0_s0_i;
    assign vld_state_rcsizeunit_1_s1_i = ($signed(state_unitspergroup) > 32'sd0) ? vld_rcsizeunit_1_s0_raw_i : vld_state_rcsizeunit_1_s0_i;
    assign vld_state_rcsizeunit_2_s1_i = ($signed(state_unitspergroup) > 32'sd0) ? vld_rcsizeunit_2_s0_raw_i : vld_state_rcsizeunit_2_s0_i;
    assign vld_state_rcsizeunit_3_s1_i = ($signed(state_unitspergroup) > 32'sd0) ? vld_rcsizeunit_3_s0_raw_i : vld_state_rcsizeunit_3_s0_i;
    assign vld_state_usemidpoint_0_s1_i = ($signed(state_unitspergroup) > 32'sd0) ? vld_usemidpoint_0_s0_raw_i : vld_state_usemidpoint_0_s0_i;
    assign vld_state_usemidpoint_1_s1_i = ($signed(state_unitspergroup) > 32'sd0) ? vld_usemidpoint_1_s0_raw_i : vld_state_usemidpoint_1_s0_i;
    assign vld_state_usemidpoint_2_s1_i = ($signed(state_unitspergroup) > 32'sd0) ? vld_usemidpoint_2_s0_raw_i : vld_state_usemidpoint_2_s0_i;
    assign vld_state_usemidpoint_3_s1_i = ($signed(state_unitspergroup) > 32'sd0) ? vld_usemidpoint_3_s0_raw_i : vld_state_usemidpoint_3_s0_i;
    assign fifo_0_fullness_s1_i = (($signed(state_unitspergroup) > 32'sd0) && (vld_fifo_lane_s0_i == 32'sd0)) ? vld_fifo_fullness_s0_i : fifo_0_fullness_s0_i;
    assign fifo_0_read_ptr_s1_i = (($signed(state_unitspergroup) > 32'sd0) && (vld_fifo_lane_s0_i == 32'sd0)) ? vld_fifo_read_ptr_s0_i : fifo_0_read_ptr_s0_i;
    assign fifo_1_fullness_s1_i = (($signed(state_unitspergroup) > 32'sd0) && (vld_fifo_lane_s0_i == 32'sd1)) ? vld_fifo_fullness_s0_i : fifo_1_fullness_s0_i;
    assign fifo_1_read_ptr_s1_i = (($signed(state_unitspergroup) > 32'sd0) && (vld_fifo_lane_s0_i == 32'sd1)) ? vld_fifo_read_ptr_s0_i : fifo_1_read_ptr_s0_i;
    assign fifo_2_fullness_s1_i = (($signed(state_unitspergroup) > 32'sd0) && (vld_fifo_lane_s0_i == 32'sd2)) ? vld_fifo_fullness_s0_i : fifo_2_fullness_s0_i;
    assign fifo_2_read_ptr_s1_i = (($signed(state_unitspergroup) > 32'sd0) && (vld_fifo_lane_s0_i == 32'sd2)) ? vld_fifo_read_ptr_s0_i : fifo_2_read_ptr_s0_i;
    assign fifo_3_fullness_s1_i = (($signed(state_unitspergroup) > 32'sd0) && (vld_fifo_lane_s0_i == 32'sd3)) ? vld_fifo_fullness_s0_i : fifo_3_fullness_s0_i;
    assign fifo_3_read_ptr_s1_i = (($signed(state_unitspergroup) > 32'sd0) && (vld_fifo_lane_s0_i == 32'sd3)) ? vld_fifo_read_ptr_s0_i : fifo_3_read_ptr_s0_i;
    assign vld_state_firstflat_s2_i = ($signed(state_unitspergroup) > 32'sd1) ? vld_firstflat_s1_raw_i : vld_state_firstflat_s1_i;
    assign vld_state_flatnesstype_s2_i = ($signed(state_unitspergroup) > 32'sd1) ? vld_flatnesstype_s1_raw_i : vld_state_flatnesstype_s1_i;
    assign vld_state_ichselected_s2_i = ($signed(state_unitspergroup) > 32'sd1) ? vld_ichselected_s1_raw_i : vld_state_ichselected_s1_i;
    assign vld_state_numbits_s2_i = ($signed(state_unitspergroup) > 32'sd1) ? vld_numbits_s1_raw_i : vld_state_numbits_s1_i;
    assign vld_state_prevfirstflat_s2_i = ($signed(state_unitspergroup) > 32'sd1) ? vld_prevfirstflat_s1_raw_i : vld_state_prevfirstflat_s1_i;
    assign vld_state_previchselected_s2_i = ($signed(state_unitspergroup) > 32'sd1) ? vld_previchselected_s1_raw_i : vld_state_previchselected_s1_i;
    assign vld_state_ichlookup_0_s2_i = ($signed(state_unitspergroup) > 32'sd1) ? vld_ichlookup_0_s1_raw_i : vld_state_ichlookup_0_s1_i;
    assign vld_state_ichlookup_1_s2_i = ($signed(state_unitspergroup) > 32'sd1) ? vld_ichlookup_1_s1_raw_i : vld_state_ichlookup_1_s1_i;
    assign vld_state_ichlookup_2_s2_i = ($signed(state_unitspergroup) > 32'sd1) ? vld_ichlookup_2_s1_raw_i : vld_state_ichlookup_2_s1_i;
    assign vld_state_ichlookup_3_s2_i = ($signed(state_unitspergroup) > 32'sd1) ? vld_ichlookup_3_s1_raw_i : vld_state_ichlookup_3_s1_i;
    assign vld_state_ichlookup_4_s2_i = ($signed(state_unitspergroup) > 32'sd1) ? vld_ichlookup_4_s1_raw_i : vld_state_ichlookup_4_s1_i;
    assign vld_state_ichlookup_5_s2_i = ($signed(state_unitspergroup) > 32'sd1) ? vld_ichlookup_5_s1_raw_i : vld_state_ichlookup_5_s1_i;
    assign vld_state_predictedsize_0_s2_i = ($signed(state_unitspergroup) > 32'sd1) ? vld_predictedsize_0_s1_raw_i : vld_state_predictedsize_0_s1_i;
    assign vld_state_predictedsize_1_s2_i = ($signed(state_unitspergroup) > 32'sd1) ? vld_predictedsize_1_s1_raw_i : vld_state_predictedsize_1_s1_i;
    assign vld_state_predictedsize_2_s2_i = ($signed(state_unitspergroup) > 32'sd1) ? vld_predictedsize_2_s1_raw_i : vld_state_predictedsize_2_s1_i;
    assign vld_state_predictedsize_3_s2_i = ($signed(state_unitspergroup) > 32'sd1) ? vld_predictedsize_3_s1_raw_i : vld_state_predictedsize_3_s1_i;
    assign vld_state_rcsizeunit_0_s2_i = ($signed(state_unitspergroup) > 32'sd1) ? vld_rcsizeunit_0_s1_raw_i : vld_state_rcsizeunit_0_s1_i;
    assign vld_state_rcsizeunit_1_s2_i = ($signed(state_unitspergroup) > 32'sd1) ? vld_rcsizeunit_1_s1_raw_i : vld_state_rcsizeunit_1_s1_i;
    assign vld_state_rcsizeunit_2_s2_i = ($signed(state_unitspergroup) > 32'sd1) ? vld_rcsizeunit_2_s1_raw_i : vld_state_rcsizeunit_2_s1_i;
    assign vld_state_rcsizeunit_3_s2_i = ($signed(state_unitspergroup) > 32'sd1) ? vld_rcsizeunit_3_s1_raw_i : vld_state_rcsizeunit_3_s1_i;
    assign vld_state_usemidpoint_0_s2_i = ($signed(state_unitspergroup) > 32'sd1) ? vld_usemidpoint_0_s1_raw_i : vld_state_usemidpoint_0_s1_i;
    assign vld_state_usemidpoint_1_s2_i = ($signed(state_unitspergroup) > 32'sd1) ? vld_usemidpoint_1_s1_raw_i : vld_state_usemidpoint_1_s1_i;
    assign vld_state_usemidpoint_2_s2_i = ($signed(state_unitspergroup) > 32'sd1) ? vld_usemidpoint_2_s1_raw_i : vld_state_usemidpoint_2_s1_i;
    assign vld_state_usemidpoint_3_s2_i = ($signed(state_unitspergroup) > 32'sd1) ? vld_usemidpoint_3_s1_raw_i : vld_state_usemidpoint_3_s1_i;
    assign fifo_0_fullness_s2_i = (($signed(state_unitspergroup) > 32'sd1) && (vld_fifo_lane_s1_i == 32'sd0)) ? vld_fifo_fullness_s1_i : fifo_0_fullness_s1_i;
    assign fifo_0_read_ptr_s2_i = (($signed(state_unitspergroup) > 32'sd1) && (vld_fifo_lane_s1_i == 32'sd0)) ? vld_fifo_read_ptr_s1_i : fifo_0_read_ptr_s1_i;
    assign fifo_1_fullness_s2_i = (($signed(state_unitspergroup) > 32'sd1) && (vld_fifo_lane_s1_i == 32'sd1)) ? vld_fifo_fullness_s1_i : fifo_1_fullness_s1_i;
    assign fifo_1_read_ptr_s2_i = (($signed(state_unitspergroup) > 32'sd1) && (vld_fifo_lane_s1_i == 32'sd1)) ? vld_fifo_read_ptr_s1_i : fifo_1_read_ptr_s1_i;
    assign fifo_2_fullness_s2_i = (($signed(state_unitspergroup) > 32'sd1) && (vld_fifo_lane_s1_i == 32'sd2)) ? vld_fifo_fullness_s1_i : fifo_2_fullness_s1_i;
    assign fifo_2_read_ptr_s2_i = (($signed(state_unitspergroup) > 32'sd1) && (vld_fifo_lane_s1_i == 32'sd2)) ? vld_fifo_read_ptr_s1_i : fifo_2_read_ptr_s1_i;
    assign fifo_3_fullness_s2_i = (($signed(state_unitspergroup) > 32'sd1) && (vld_fifo_lane_s1_i == 32'sd3)) ? vld_fifo_fullness_s1_i : fifo_3_fullness_s1_i;
    assign fifo_3_read_ptr_s2_i = (($signed(state_unitspergroup) > 32'sd1) && (vld_fifo_lane_s1_i == 32'sd3)) ? vld_fifo_read_ptr_s1_i : fifo_3_read_ptr_s1_i;
    assign vld_state_firstflat_s3_i = ($signed(state_unitspergroup) > 32'sd2) ? vld_firstflat_s2_raw_i : vld_state_firstflat_s2_i;
    assign vld_state_flatnesstype_s3_i = ($signed(state_unitspergroup) > 32'sd2) ? vld_flatnesstype_s2_raw_i : vld_state_flatnesstype_s2_i;
    assign vld_state_ichselected_s3_i = ($signed(state_unitspergroup) > 32'sd2) ? vld_ichselected_s2_raw_i : vld_state_ichselected_s2_i;
    assign vld_state_numbits_s3_i = ($signed(state_unitspergroup) > 32'sd2) ? vld_numbits_s2_raw_i : vld_state_numbits_s2_i;
    assign vld_state_prevfirstflat_s3_i = ($signed(state_unitspergroup) > 32'sd2) ? vld_prevfirstflat_s2_raw_i : vld_state_prevfirstflat_s2_i;
    assign vld_state_previchselected_s3_i = ($signed(state_unitspergroup) > 32'sd2) ? vld_previchselected_s2_raw_i : vld_state_previchselected_s2_i;
    assign vld_state_ichlookup_0_s3_i = ($signed(state_unitspergroup) > 32'sd2) ? vld_ichlookup_0_s2_raw_i : vld_state_ichlookup_0_s2_i;
    assign vld_state_ichlookup_1_s3_i = ($signed(state_unitspergroup) > 32'sd2) ? vld_ichlookup_1_s2_raw_i : vld_state_ichlookup_1_s2_i;
    assign vld_state_ichlookup_2_s3_i = ($signed(state_unitspergroup) > 32'sd2) ? vld_ichlookup_2_s2_raw_i : vld_state_ichlookup_2_s2_i;
    assign vld_state_ichlookup_3_s3_i = ($signed(state_unitspergroup) > 32'sd2) ? vld_ichlookup_3_s2_raw_i : vld_state_ichlookup_3_s2_i;
    assign vld_state_ichlookup_4_s3_i = ($signed(state_unitspergroup) > 32'sd2) ? vld_ichlookup_4_s2_raw_i : vld_state_ichlookup_4_s2_i;
    assign vld_state_ichlookup_5_s3_i = ($signed(state_unitspergroup) > 32'sd2) ? vld_ichlookup_5_s2_raw_i : vld_state_ichlookup_5_s2_i;
    assign vld_state_predictedsize_0_s3_i = ($signed(state_unitspergroup) > 32'sd2) ? vld_predictedsize_0_s2_raw_i : vld_state_predictedsize_0_s2_i;
    assign vld_state_predictedsize_1_s3_i = ($signed(state_unitspergroup) > 32'sd2) ? vld_predictedsize_1_s2_raw_i : vld_state_predictedsize_1_s2_i;
    assign vld_state_predictedsize_2_s3_i = ($signed(state_unitspergroup) > 32'sd2) ? vld_predictedsize_2_s2_raw_i : vld_state_predictedsize_2_s2_i;
    assign vld_state_predictedsize_3_s3_i = ($signed(state_unitspergroup) > 32'sd2) ? vld_predictedsize_3_s2_raw_i : vld_state_predictedsize_3_s2_i;
    assign vld_state_rcsizeunit_0_s3_i = ($signed(state_unitspergroup) > 32'sd2) ? vld_rcsizeunit_0_s2_raw_i : vld_state_rcsizeunit_0_s2_i;
    assign vld_state_rcsizeunit_1_s3_i = ($signed(state_unitspergroup) > 32'sd2) ? vld_rcsizeunit_1_s2_raw_i : vld_state_rcsizeunit_1_s2_i;
    assign vld_state_rcsizeunit_2_s3_i = ($signed(state_unitspergroup) > 32'sd2) ? vld_rcsizeunit_2_s2_raw_i : vld_state_rcsizeunit_2_s2_i;
    assign vld_state_rcsizeunit_3_s3_i = ($signed(state_unitspergroup) > 32'sd2) ? vld_rcsizeunit_3_s2_raw_i : vld_state_rcsizeunit_3_s2_i;
    assign vld_state_usemidpoint_0_s3_i = ($signed(state_unitspergroup) > 32'sd2) ? vld_usemidpoint_0_s2_raw_i : vld_state_usemidpoint_0_s2_i;
    assign vld_state_usemidpoint_1_s3_i = ($signed(state_unitspergroup) > 32'sd2) ? vld_usemidpoint_1_s2_raw_i : vld_state_usemidpoint_1_s2_i;
    assign vld_state_usemidpoint_2_s3_i = ($signed(state_unitspergroup) > 32'sd2) ? vld_usemidpoint_2_s2_raw_i : vld_state_usemidpoint_2_s2_i;
    assign vld_state_usemidpoint_3_s3_i = ($signed(state_unitspergroup) > 32'sd2) ? vld_usemidpoint_3_s2_raw_i : vld_state_usemidpoint_3_s2_i;
    assign fifo_0_fullness_s3_i = (($signed(state_unitspergroup) > 32'sd2) && (vld_fifo_lane_s2_i == 32'sd0)) ? vld_fifo_fullness_s2_i : fifo_0_fullness_s2_i;
    assign fifo_0_read_ptr_s3_i = (($signed(state_unitspergroup) > 32'sd2) && (vld_fifo_lane_s2_i == 32'sd0)) ? vld_fifo_read_ptr_s2_i : fifo_0_read_ptr_s2_i;
    assign fifo_1_fullness_s3_i = (($signed(state_unitspergroup) > 32'sd2) && (vld_fifo_lane_s2_i == 32'sd1)) ? vld_fifo_fullness_s2_i : fifo_1_fullness_s2_i;
    assign fifo_1_read_ptr_s3_i = (($signed(state_unitspergroup) > 32'sd2) && (vld_fifo_lane_s2_i == 32'sd1)) ? vld_fifo_read_ptr_s2_i : fifo_1_read_ptr_s2_i;
    assign fifo_2_fullness_s3_i = (($signed(state_unitspergroup) > 32'sd2) && (vld_fifo_lane_s2_i == 32'sd2)) ? vld_fifo_fullness_s2_i : fifo_2_fullness_s2_i;
    assign fifo_2_read_ptr_s3_i = (($signed(state_unitspergroup) > 32'sd2) && (vld_fifo_lane_s2_i == 32'sd2)) ? vld_fifo_read_ptr_s2_i : fifo_2_read_ptr_s2_i;
    assign fifo_3_fullness_s3_i = (($signed(state_unitspergroup) > 32'sd2) && (vld_fifo_lane_s2_i == 32'sd3)) ? vld_fifo_fullness_s2_i : fifo_3_fullness_s2_i;
    assign fifo_3_read_ptr_s3_i = (($signed(state_unitspergroup) > 32'sd2) && (vld_fifo_lane_s2_i == 32'sd3)) ? vld_fifo_read_ptr_s2_i : fifo_3_read_ptr_s2_i;
    assign vld_state_firstflat_s4_i = ($signed(state_unitspergroup) > 32'sd3) ? vld_firstflat_s3_raw_i : vld_state_firstflat_s3_i;
    assign vld_state_flatnesstype_s4_i = ($signed(state_unitspergroup) > 32'sd3) ? vld_flatnesstype_s3_raw_i : vld_state_flatnesstype_s3_i;
    assign vld_state_ichselected_s4_i = ($signed(state_unitspergroup) > 32'sd3) ? vld_ichselected_s3_raw_i : vld_state_ichselected_s3_i;
    assign vld_state_numbits_s4_i = ($signed(state_unitspergroup) > 32'sd3) ? vld_numbits_s3_raw_i : vld_state_numbits_s3_i;
    assign vld_state_prevfirstflat_s4_i = ($signed(state_unitspergroup) > 32'sd3) ? vld_prevfirstflat_s3_raw_i : vld_state_prevfirstflat_s3_i;
    assign vld_state_previchselected_s4_i = ($signed(state_unitspergroup) > 32'sd3) ? vld_previchselected_s3_raw_i : vld_state_previchselected_s3_i;
    assign vld_state_ichlookup_0_s4_i = ($signed(state_unitspergroup) > 32'sd3) ? vld_ichlookup_0_s3_raw_i : vld_state_ichlookup_0_s3_i;
    assign vld_state_ichlookup_1_s4_i = ($signed(state_unitspergroup) > 32'sd3) ? vld_ichlookup_1_s3_raw_i : vld_state_ichlookup_1_s3_i;
    assign vld_state_ichlookup_2_s4_i = ($signed(state_unitspergroup) > 32'sd3) ? vld_ichlookup_2_s3_raw_i : vld_state_ichlookup_2_s3_i;
    assign vld_state_ichlookup_3_s4_i = ($signed(state_unitspergroup) > 32'sd3) ? vld_ichlookup_3_s3_raw_i : vld_state_ichlookup_3_s3_i;
    assign vld_state_ichlookup_4_s4_i = ($signed(state_unitspergroup) > 32'sd3) ? vld_ichlookup_4_s3_raw_i : vld_state_ichlookup_4_s3_i;
    assign vld_state_ichlookup_5_s4_i = ($signed(state_unitspergroup) > 32'sd3) ? vld_ichlookup_5_s3_raw_i : vld_state_ichlookup_5_s3_i;
    assign vld_state_predictedsize_0_s4_i = ($signed(state_unitspergroup) > 32'sd3) ? vld_predictedsize_0_s3_raw_i : vld_state_predictedsize_0_s3_i;
    assign vld_state_predictedsize_1_s4_i = ($signed(state_unitspergroup) > 32'sd3) ? vld_predictedsize_1_s3_raw_i : vld_state_predictedsize_1_s3_i;
    assign vld_state_predictedsize_2_s4_i = ($signed(state_unitspergroup) > 32'sd3) ? vld_predictedsize_2_s3_raw_i : vld_state_predictedsize_2_s3_i;
    assign vld_state_predictedsize_3_s4_i = ($signed(state_unitspergroup) > 32'sd3) ? vld_predictedsize_3_s3_raw_i : vld_state_predictedsize_3_s3_i;
    assign vld_state_rcsizeunit_0_s4_i = ($signed(state_unitspergroup) > 32'sd3) ? vld_rcsizeunit_0_s3_raw_i : vld_state_rcsizeunit_0_s3_i;
    assign vld_state_rcsizeunit_1_s4_i = ($signed(state_unitspergroup) > 32'sd3) ? vld_rcsizeunit_1_s3_raw_i : vld_state_rcsizeunit_1_s3_i;
    assign vld_state_rcsizeunit_2_s4_i = ($signed(state_unitspergroup) > 32'sd3) ? vld_rcsizeunit_2_s3_raw_i : vld_state_rcsizeunit_2_s3_i;
    assign vld_state_rcsizeunit_3_s4_i = ($signed(state_unitspergroup) > 32'sd3) ? vld_rcsizeunit_3_s3_raw_i : vld_state_rcsizeunit_3_s3_i;
    assign vld_state_usemidpoint_0_s4_i = ($signed(state_unitspergroup) > 32'sd3) ? vld_usemidpoint_0_s3_raw_i : vld_state_usemidpoint_0_s3_i;
    assign vld_state_usemidpoint_1_s4_i = ($signed(state_unitspergroup) > 32'sd3) ? vld_usemidpoint_1_s3_raw_i : vld_state_usemidpoint_1_s3_i;
    assign vld_state_usemidpoint_2_s4_i = ($signed(state_unitspergroup) > 32'sd3) ? vld_usemidpoint_2_s3_raw_i : vld_state_usemidpoint_2_s3_i;
    assign vld_state_usemidpoint_3_s4_i = ($signed(state_unitspergroup) > 32'sd3) ? vld_usemidpoint_3_s3_raw_i : vld_state_usemidpoint_3_s3_i;
    assign fifo_0_fullness_s4_i = (($signed(state_unitspergroup) > 32'sd3) && (vld_fifo_lane_s3_i == 32'sd0)) ? vld_fifo_fullness_s3_i : fifo_0_fullness_s3_i;
    assign fifo_0_read_ptr_s4_i = (($signed(state_unitspergroup) > 32'sd3) && (vld_fifo_lane_s3_i == 32'sd0)) ? vld_fifo_read_ptr_s3_i : fifo_0_read_ptr_s3_i;
    assign fifo_1_fullness_s4_i = (($signed(state_unitspergroup) > 32'sd3) && (vld_fifo_lane_s3_i == 32'sd1)) ? vld_fifo_fullness_s3_i : fifo_1_fullness_s3_i;
    assign fifo_1_read_ptr_s4_i = (($signed(state_unitspergroup) > 32'sd3) && (vld_fifo_lane_s3_i == 32'sd1)) ? vld_fifo_read_ptr_s3_i : fifo_1_read_ptr_s3_i;
    assign fifo_2_fullness_s4_i = (($signed(state_unitspergroup) > 32'sd3) && (vld_fifo_lane_s3_i == 32'sd2)) ? vld_fifo_fullness_s3_i : fifo_2_fullness_s3_i;
    assign fifo_2_read_ptr_s4_i = (($signed(state_unitspergroup) > 32'sd3) && (vld_fifo_lane_s3_i == 32'sd2)) ? vld_fifo_read_ptr_s3_i : fifo_2_read_ptr_s3_i;
    assign fifo_3_fullness_s4_i = (($signed(state_unitspergroup) > 32'sd3) && (vld_fifo_lane_s3_i == 32'sd3)) ? vld_fifo_fullness_s3_i : fifo_3_fullness_s3_i;
    assign fifo_3_read_ptr_s4_i = (($signed(state_unitspergroup) > 32'sd3) && (vld_fifo_lane_s3_i == 32'sd3)) ? vld_fifo_read_ptr_s3_i : fifo_3_read_ptr_s3_i;
    assign post_mux_num_bits_out = mux_post_mux_num_bits_out_i;
    assign fifo_0_size_out = mux_fifo_0_size_out_i;
    assign fifo_0_write_ptr_out = mux_fifo_0_write_ptr_out_i;
    assign fifo_0_max_fullness_out = mux_fifo_0_max_fullness_out_i;
    assign fifo_0_byte_ctr_out = mux_fifo_0_byte_ctr_out_i;
    assign fifo_0_fullness_out = fifo_0_fullness_s4_i;
    assign fifo_0_read_ptr_out = fifo_0_read_ptr_s4_i;
    assign fifo_0_byte_0_out = mux_fifo_0_byte_0_out_i;
    assign fifo_0_byte_1_out = mux_fifo_0_byte_1_out_i;
    assign fifo_0_byte_2_out = mux_fifo_0_byte_2_out_i;
    assign fifo_0_byte_3_out = mux_fifo_0_byte_3_out_i;
    assign fifo_0_byte_4_out = mux_fifo_0_byte_4_out_i;
    assign fifo_0_byte_5_out = mux_fifo_0_byte_5_out_i;
    assign fifo_0_byte_6_out = mux_fifo_0_byte_6_out_i;
    assign fifo_0_byte_7_out = mux_fifo_0_byte_7_out_i;
    assign fifo_0_byte_8_out = mux_fifo_0_byte_8_out_i;
    assign fifo_0_byte_9_out = mux_fifo_0_byte_9_out_i;
    assign fifo_0_byte_10_out = mux_fifo_0_byte_10_out_i;
    assign fifo_0_byte_11_out = mux_fifo_0_byte_11_out_i;
    assign fifo_0_byte_12_out = mux_fifo_0_byte_12_out_i;
    assign fifo_0_byte_13_out = mux_fifo_0_byte_13_out_i;
    assign fifo_0_byte_14_out = mux_fifo_0_byte_14_out_i;
    assign fifo_0_byte_15_out = mux_fifo_0_byte_15_out_i;
    assign fifo_0_byte_16_out = mux_fifo_0_byte_16_out_i;
    assign fifo_1_size_out = mux_fifo_1_size_out_i;
    assign fifo_1_write_ptr_out = mux_fifo_1_write_ptr_out_i;
    assign fifo_1_max_fullness_out = mux_fifo_1_max_fullness_out_i;
    assign fifo_1_byte_ctr_out = mux_fifo_1_byte_ctr_out_i;
    assign fifo_1_fullness_out = fifo_1_fullness_s4_i;
    assign fifo_1_read_ptr_out = fifo_1_read_ptr_s4_i;
    assign fifo_1_byte_0_out = mux_fifo_1_byte_0_out_i;
    assign fifo_1_byte_1_out = mux_fifo_1_byte_1_out_i;
    assign fifo_1_byte_2_out = mux_fifo_1_byte_2_out_i;
    assign fifo_1_byte_3_out = mux_fifo_1_byte_3_out_i;
    assign fifo_1_byte_4_out = mux_fifo_1_byte_4_out_i;
    assign fifo_1_byte_5_out = mux_fifo_1_byte_5_out_i;
    assign fifo_1_byte_6_out = mux_fifo_1_byte_6_out_i;
    assign fifo_1_byte_7_out = mux_fifo_1_byte_7_out_i;
    assign fifo_1_byte_8_out = mux_fifo_1_byte_8_out_i;
    assign fifo_1_byte_9_out = mux_fifo_1_byte_9_out_i;
    assign fifo_1_byte_10_out = mux_fifo_1_byte_10_out_i;
    assign fifo_1_byte_11_out = mux_fifo_1_byte_11_out_i;
    assign fifo_1_byte_12_out = mux_fifo_1_byte_12_out_i;
    assign fifo_1_byte_13_out = mux_fifo_1_byte_13_out_i;
    assign fifo_1_byte_14_out = mux_fifo_1_byte_14_out_i;
    assign fifo_1_byte_15_out = mux_fifo_1_byte_15_out_i;
    assign fifo_1_byte_16_out = mux_fifo_1_byte_16_out_i;
    assign fifo_2_size_out = mux_fifo_2_size_out_i;
    assign fifo_2_write_ptr_out = mux_fifo_2_write_ptr_out_i;
    assign fifo_2_max_fullness_out = mux_fifo_2_max_fullness_out_i;
    assign fifo_2_byte_ctr_out = mux_fifo_2_byte_ctr_out_i;
    assign fifo_2_fullness_out = fifo_2_fullness_s4_i;
    assign fifo_2_read_ptr_out = fifo_2_read_ptr_s4_i;
    assign fifo_2_byte_0_out = mux_fifo_2_byte_0_out_i;
    assign fifo_2_byte_1_out = mux_fifo_2_byte_1_out_i;
    assign fifo_2_byte_2_out = mux_fifo_2_byte_2_out_i;
    assign fifo_2_byte_3_out = mux_fifo_2_byte_3_out_i;
    assign fifo_2_byte_4_out = mux_fifo_2_byte_4_out_i;
    assign fifo_2_byte_5_out = mux_fifo_2_byte_5_out_i;
    assign fifo_2_byte_6_out = mux_fifo_2_byte_6_out_i;
    assign fifo_2_byte_7_out = mux_fifo_2_byte_7_out_i;
    assign fifo_2_byte_8_out = mux_fifo_2_byte_8_out_i;
    assign fifo_2_byte_9_out = mux_fifo_2_byte_9_out_i;
    assign fifo_2_byte_10_out = mux_fifo_2_byte_10_out_i;
    assign fifo_2_byte_11_out = mux_fifo_2_byte_11_out_i;
    assign fifo_2_byte_12_out = mux_fifo_2_byte_12_out_i;
    assign fifo_2_byte_13_out = mux_fifo_2_byte_13_out_i;
    assign fifo_2_byte_14_out = mux_fifo_2_byte_14_out_i;
    assign fifo_2_byte_15_out = mux_fifo_2_byte_15_out_i;
    assign fifo_2_byte_16_out = mux_fifo_2_byte_16_out_i;
    assign fifo_3_size_out = mux_fifo_3_size_out_i;
    assign fifo_3_write_ptr_out = mux_fifo_3_write_ptr_out_i;
    assign fifo_3_max_fullness_out = mux_fifo_3_max_fullness_out_i;
    assign fifo_3_byte_ctr_out = mux_fifo_3_byte_ctr_out_i;
    assign fifo_3_fullness_out = fifo_3_fullness_s4_i;
    assign fifo_3_read_ptr_out = fifo_3_read_ptr_s4_i;
    assign fifo_3_byte_0_out = mux_fifo_3_byte_0_out_i;
    assign fifo_3_byte_1_out = mux_fifo_3_byte_1_out_i;
    assign fifo_3_byte_2_out = mux_fifo_3_byte_2_out_i;
    assign fifo_3_byte_3_out = mux_fifo_3_byte_3_out_i;
    assign fifo_3_byte_4_out = mux_fifo_3_byte_4_out_i;
    assign fifo_3_byte_5_out = mux_fifo_3_byte_5_out_i;
    assign fifo_3_byte_6_out = mux_fifo_3_byte_6_out_i;
    assign fifo_3_byte_7_out = mux_fifo_3_byte_7_out_i;
    assign fifo_3_byte_8_out = mux_fifo_3_byte_8_out_i;
    assign fifo_3_byte_9_out = mux_fifo_3_byte_9_out_i;
    assign fifo_3_byte_10_out = mux_fifo_3_byte_10_out_i;
    assign fifo_3_byte_11_out = mux_fifo_3_byte_11_out_i;
    assign fifo_3_byte_12_out = mux_fifo_3_byte_12_out_i;
    assign fifo_3_byte_13_out = mux_fifo_3_byte_13_out_i;
    assign fifo_3_byte_14_out = mux_fifo_3_byte_14_out_i;
    assign fifo_3_byte_15_out = mux_fifo_3_byte_15_out_i;
    assign fifo_3_byte_16_out = mux_fifo_3_byte_16_out_i;
    assign state_firstflat_out = vld_state_firstflat_s4_i;
    assign state_flatnesstype_out = vld_state_flatnesstype_s4_i;
    assign state_ichselected_out = vld_state_ichselected_s4_i;
    assign state_numbits_out = vld_state_numbits_s4_i;
    assign state_prevfirstflat_out = vld_state_prevfirstflat_s4_i;
    assign state_previchselected_out = vld_state_previchselected_s4_i;
    assign state_ichlookup_0_out = vld_state_ichlookup_0_s4_i;
    assign state_ichlookup_1_out = vld_state_ichlookup_1_s4_i;
    assign state_ichlookup_2_out = vld_state_ichlookup_2_s4_i;
    assign state_ichlookup_3_out = vld_state_ichlookup_3_s4_i;
    assign state_ichlookup_4_out = vld_state_ichlookup_4_s4_i;
    assign state_ichlookup_5_out = vld_state_ichlookup_5_s4_i;
    assign state_predictedsize_0_out = vld_state_predictedsize_0_s4_i;
    assign state_predictedsize_1_out = vld_state_predictedsize_1_s4_i;
    assign state_predictedsize_2_out = vld_state_predictedsize_2_s4_i;
    assign state_predictedsize_3_out = vld_state_predictedsize_3_s4_i;
    assign state_rcsizeunit_0_out = vld_state_rcsizeunit_0_s4_i;
    assign state_rcsizeunit_1_out = vld_state_rcsizeunit_1_s4_i;
    assign state_rcsizeunit_2_out = vld_state_rcsizeunit_2_s4_i;
    assign state_rcsizeunit_3_out = vld_state_rcsizeunit_3_s4_i;
    assign state_usemidpoint_0_out = vld_state_usemidpoint_0_s4_i;
    assign state_usemidpoint_1_out = vld_state_usemidpoint_1_s4_i;
    assign state_usemidpoint_2_out = vld_state_usemidpoint_2_s4_i;
    assign state_usemidpoint_3_out = vld_state_usemidpoint_3_s4_i;
    assign state_quantizedresidual_0_0_out = ($signed(state_unitspergroup) > 32'sd0) ? vld_residual_0_0_raw_i : state_quantizedresidual_0_0;
    assign state_quantizedresidual_0_1_out = ($signed(state_unitspergroup) > 32'sd0) ? vld_residual_0_1_raw_i : state_quantizedresidual_0_1;
    assign state_quantizedresidual_0_2_out = ($signed(state_unitspergroup) > 32'sd0) ? vld_residual_0_2_raw_i : state_quantizedresidual_0_2;
    assign state_quantizedresidual_1_0_out = ($signed(state_unitspergroup) > 32'sd1) ? vld_residual_1_0_raw_i : state_quantizedresidual_1_0;
    assign state_quantizedresidual_1_1_out = ($signed(state_unitspergroup) > 32'sd1) ? vld_residual_1_1_raw_i : state_quantizedresidual_1_1;
    assign state_quantizedresidual_1_2_out = ($signed(state_unitspergroup) > 32'sd1) ? vld_residual_1_2_raw_i : state_quantizedresidual_1_2;
    assign state_quantizedresidual_2_0_out = ($signed(state_unitspergroup) > 32'sd2) ? vld_residual_2_0_raw_i : state_quantizedresidual_2_0;
    assign state_quantizedresidual_2_1_out = ($signed(state_unitspergroup) > 32'sd2) ? vld_residual_2_1_raw_i : state_quantizedresidual_2_1;
    assign state_quantizedresidual_2_2_out = ($signed(state_unitspergroup) > 32'sd2) ? vld_residual_2_2_raw_i : state_quantizedresidual_2_2;
    assign state_quantizedresidual_3_0_out = ($signed(state_unitspergroup) > 32'sd3) ? vld_residual_3_0_raw_i : state_quantizedresidual_3_0;
    assign state_quantizedresidual_3_1_out = ($signed(state_unitspergroup) > 32'sd3) ? vld_residual_3_1_raw_i : state_quantizedresidual_3_1;
    assign state_quantizedresidual_3_2_out = ($signed(state_unitspergroup) > 32'sd3) ? vld_residual_3_2_raw_i : state_quantizedresidual_3_2;
    assign state_prevprimaryqp_out = state_primaryqp;
    assign state_codedgroupsize_out = vld_state_numbits_s4_i - state_numbits;
    assign state_bufferfullness_out = state_bufferfullness + state_codedgroupsize_out;
    assign state_erroroccurred_out = ($signed(state_bufferfullness_out) > $signed(cfg_rcb_bits)) ? 32'sd1 : state_erroroccurred;
    assign state_origisflat_out = (($signed(state_groupcount) % 32'sd4) == $signed(vld_state_firstflat_s4_i)) ? 32'sd1 : 32'sd0;
    assign state_groupcountline_out = state_groupcountline + 32'sd1;
    assign domain_valid = mux_domain_valid_i && ($signed(state_unitspergroup) >= 32'sd3) && ($signed(state_unitspergroup) <= 32'sd4) && (!($signed(state_unitspergroup) > 32'sd0) || vld_domain_s0_i) && (!($signed(state_unitspergroup) > 32'sd1) || vld_domain_s1_i) && (!($signed(state_unitspergroup) > 32'sd2) || vld_domain_s2_i) && (!($signed(state_unitspergroup) > 32'sd3) || vld_domain_s3_i);
endmodule
