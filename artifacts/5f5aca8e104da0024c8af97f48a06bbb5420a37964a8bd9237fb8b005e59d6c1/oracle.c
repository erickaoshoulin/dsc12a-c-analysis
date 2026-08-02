#include <stddef.h>
#include <stdio.h>
#include "dsc_types.h"
extern int GetQpAdjPredSize(dsc_cfg_t * dsc_cfg, dsc_state_t * dsc_state, int unit);
int main(int argc, char **argv) {
    FILE *input = stdin;
    if (argc > 1) {
        input = fopen(argv[1], "rb");
        if (!input) return 2;
    }
    int unit, dsc_version_minor, native_420, unit_c_type_selected, predicted_size_selected, primary_qp, prev_primary_qp, cpntBitDepth_0, cpntBitDepth_1, cpntBitDepth_2, cpntBitDepth_3, qlevel_luma_new, qlevel_chroma_new, qlevel_luma_old, qlevel_chroma_old;
    int return_value;
    while (fscanf(input, "%d %d %d %d %d %d %d %d %d %d %d %d %d %d %d", &unit, &dsc_version_minor, &native_420, &unit_c_type_selected, &predicted_size_selected, &primary_qp, &prev_primary_qp, &cpntBitDepth_0, &cpntBitDepth_1, &cpntBitDepth_2, &cpntBitDepth_3, &qlevel_luma_new, &qlevel_chroma_new, &qlevel_luma_old, &qlevel_chroma_old) == 15) {
        dsc_cfg_t dsc_cfg = {0};
        dsc_state_t dsc_state = {0};
        int quantTableLuma_oracle_storage[32] = {0};
        int quantTableChroma_oracle_storage[32] = {0};
        dsc_cfg.dsc_version_minor = dsc_version_minor;
dsc_cfg.native_420 = native_420;
dsc_state.unitCType[unit] = unit_c_type_selected;
dsc_state.predictedSize[unit] = predicted_size_selected;
dsc_state.primaryQp = primary_qp;
dsc_state.prevPrimaryQp = prev_primary_qp;
dsc_state.cpntBitDepth[0] = cpntBitDepth_0;
dsc_state.cpntBitDepth[1] = cpntBitDepth_1;
dsc_state.cpntBitDepth[2] = cpntBitDepth_2;
dsc_state.cpntBitDepth[3] = cpntBitDepth_3;
quantTableLuma_oracle_storage[primary_qp] = qlevel_luma_new;
dsc_state.quantTableLuma = quantTableLuma_oracle_storage;
quantTableChroma_oracle_storage[primary_qp] = qlevel_chroma_new;
dsc_state.quantTableChroma = quantTableChroma_oracle_storage;
quantTableLuma_oracle_storage[prev_primary_qp] = qlevel_luma_old;
dsc_state.quantTableLuma = quantTableLuma_oracle_storage;
quantTableChroma_oracle_storage[prev_primary_qp] = qlevel_chroma_old;
dsc_state.quantTableChroma = quantTableChroma_oracle_storage;
        return_value = GetQpAdjPredSize(&dsc_cfg, &dsc_state, unit);
        printf("%d\n", return_value);
    }
    if (input != stdin) fclose(input);
    return 0;
}
