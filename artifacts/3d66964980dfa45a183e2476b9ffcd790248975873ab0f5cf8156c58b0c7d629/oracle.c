#include <stddef.h>
#include <stdio.h>
#include "dsc_types.h"
extern int EstimateBitsForGroup(dsc_cfg_t * dsc_cfg, dsc_state_t * dsc_state);
int main(int argc, char **argv) {
    FILE *input = stdin;
    if (argc > 1) {
        input = fopen(argv[1], "rb");
        if (!input) return 2;
    }
    int dsc_version_minor, native_420, units_per_group, pixels_in_group, hPos, slice_width, prev_ich_selected, primary_qp, prev_primary_qp, cpntBitDepth_0, cpntBitDepth_1, cpntBitDepth_2, cpntBitDepth_3, unit_c_type_0, unit_c_type_1, unit_c_type_2, unit_c_type_3, unit_start_h_pos_0, unit_start_h_pos_1, unit_start_h_pos_2, unit_start_h_pos_3, predicted_size_0, predicted_size_1, predicted_size_2, predicted_size_3, quantized_residual_0_0, quantized_residual_0_1, quantized_residual_0_2, quantized_residual_1_0, quantized_residual_1_1, quantized_residual_1_2, quantized_residual_2_0, quantized_residual_2_1, quantized_residual_2_2, quantized_residual_3_0, quantized_residual_3_1, quantized_residual_3_2, qlevel_luma_new, qlevel_luma_old, qlevel_chroma_new, qlevel_chroma_old;
    int return_value;
    while (fscanf(input, "%d %d %d %d %d %d %d %d %d %d %d %d %d %d %d %d %d %d %d %d %d %d %d %d %d %d %d %d %d %d %d %d %d %d %d %d %d %d %d %d %d", &dsc_version_minor, &native_420, &units_per_group, &pixels_in_group, &hPos, &slice_width, &prev_ich_selected, &primary_qp, &prev_primary_qp, &cpntBitDepth_0, &cpntBitDepth_1, &cpntBitDepth_2, &cpntBitDepth_3, &unit_c_type_0, &unit_c_type_1, &unit_c_type_2, &unit_c_type_3, &unit_start_h_pos_0, &unit_start_h_pos_1, &unit_start_h_pos_2, &unit_start_h_pos_3, &predicted_size_0, &predicted_size_1, &predicted_size_2, &predicted_size_3, &quantized_residual_0_0, &quantized_residual_0_1, &quantized_residual_0_2, &quantized_residual_1_0, &quantized_residual_1_1, &quantized_residual_1_2, &quantized_residual_2_0, &quantized_residual_2_1, &quantized_residual_2_2, &quantized_residual_3_0, &quantized_residual_3_1, &quantized_residual_3_2, &qlevel_luma_new, &qlevel_luma_old, &qlevel_chroma_new, &qlevel_chroma_old) == 41) {
        dsc_cfg_t dsc_cfg = {0};
        dsc_state_t dsc_state = {0};
        int quantTableLuma_oracle_storage[32] = {0};
        int quantTableChroma_oracle_storage[32] = {0};
        dsc_cfg.dsc_version_minor = dsc_version_minor;
dsc_cfg.native_420 = native_420;
dsc_state.unitsPerGroup = units_per_group;
dsc_state.pixelsInGroup = pixels_in_group;
dsc_state.hPos = hPos;
dsc_state.sliceWidth = slice_width;
dsc_state.prevIchSelected = prev_ich_selected;
dsc_state.primaryQp = primary_qp;
dsc_state.prevPrimaryQp = prev_primary_qp;
dsc_state.cpntBitDepth[0] = cpntBitDepth_0;
dsc_state.cpntBitDepth[1] = cpntBitDepth_1;
dsc_state.cpntBitDepth[2] = cpntBitDepth_2;
dsc_state.cpntBitDepth[3] = cpntBitDepth_3;
dsc_state.unitCType[0] = unit_c_type_0;
dsc_state.unitCType[1] = unit_c_type_1;
dsc_state.unitCType[2] = unit_c_type_2;
dsc_state.unitCType[3] = unit_c_type_3;
dsc_state.unitStartHPos[0] = unit_start_h_pos_0;
dsc_state.unitStartHPos[1] = unit_start_h_pos_1;
dsc_state.unitStartHPos[2] = unit_start_h_pos_2;
dsc_state.unitStartHPos[3] = unit_start_h_pos_3;
dsc_state.predictedSize[0] = predicted_size_0;
dsc_state.predictedSize[1] = predicted_size_1;
dsc_state.predictedSize[2] = predicted_size_2;
dsc_state.predictedSize[3] = predicted_size_3;
dsc_state.quantizedResidual[0][0] = quantized_residual_0_0;
dsc_state.quantizedResidual[0][1] = quantized_residual_0_1;
dsc_state.quantizedResidual[0][2] = quantized_residual_0_2;
dsc_state.quantizedResidual[1][0] = quantized_residual_1_0;
dsc_state.quantizedResidual[1][1] = quantized_residual_1_1;
dsc_state.quantizedResidual[1][2] = quantized_residual_1_2;
dsc_state.quantizedResidual[2][0] = quantized_residual_2_0;
dsc_state.quantizedResidual[2][1] = quantized_residual_2_1;
dsc_state.quantizedResidual[2][2] = quantized_residual_2_2;
dsc_state.quantizedResidual[3][0] = quantized_residual_3_0;
dsc_state.quantizedResidual[3][1] = quantized_residual_3_1;
dsc_state.quantizedResidual[3][2] = quantized_residual_3_2;
quantTableLuma_oracle_storage[primary_qp] = qlevel_luma_new;
dsc_state.quantTableLuma = quantTableLuma_oracle_storage;
quantTableLuma_oracle_storage[prev_primary_qp] = qlevel_luma_old;
dsc_state.quantTableLuma = quantTableLuma_oracle_storage;
quantTableChroma_oracle_storage[primary_qp] = qlevel_chroma_new;
dsc_state.quantTableChroma = quantTableChroma_oracle_storage;
quantTableChroma_oracle_storage[prev_primary_qp] = qlevel_chroma_old;
dsc_state.quantTableChroma = quantTableChroma_oracle_storage;
        return_value = EstimateBitsForGroup(&dsc_cfg, &dsc_state);
        printf("%d\n", return_value);
    }
    if (input != stdin) fclose(input);
    return 0;
}
