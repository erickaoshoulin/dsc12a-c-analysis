module getqpadjpredsize_candidate_01 (
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
