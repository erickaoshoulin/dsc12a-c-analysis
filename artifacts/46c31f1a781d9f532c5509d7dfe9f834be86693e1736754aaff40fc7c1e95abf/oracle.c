#include <stddef.h>
#include <stdio.h>
#include "dsc_types.h"
extern int UsingMidpoint(dsc_cfg_t * dsc_cfg, dsc_state_t * dsc_state, int unit, int cpnt);
int main(int argc, char **argv) {
    FILE *input = stdin;
    if (argc > 1) {
        input = fopen(argv[1], "rb");
        if (!input) return 2;
    }
    int unit, cpnt, dsc_version_minor, native_420, primary_qp, cpntBitDepth_0, cpntBitDepth_1, cpntBitDepth_2, cpntBitDepth_3, cpntBitDepth_selected, qlevel_luma, qlevel_chroma, quantized_residual_0, quantized_residual_1, quantized_residual_2;
    int return_value;
    while (fscanf(input, "%d %d %d %d %d %d %d %d %d %d %d %d %d %d %d", &unit, &cpnt, &dsc_version_minor, &native_420, &primary_qp, &cpntBitDepth_0, &cpntBitDepth_1, &cpntBitDepth_2, &cpntBitDepth_3, &cpntBitDepth_selected, &qlevel_luma, &qlevel_chroma, &quantized_residual_0, &quantized_residual_1, &quantized_residual_2) == 15) {
        dsc_cfg_t dsc_cfg = {0};
        dsc_state_t dsc_state = {0};
        int quantTableLuma_oracle_storage[32] = {0};
        int quantTableChroma_oracle_storage[32] = {0};
        dsc_cfg.dsc_version_minor = dsc_version_minor;
dsc_cfg.native_420 = native_420;
dsc_state.primaryQp = primary_qp;
dsc_state.cpntBitDepth[0] = cpntBitDepth_0;
dsc_state.cpntBitDepth[1] = cpntBitDepth_1;
dsc_state.cpntBitDepth[2] = cpntBitDepth_2;
dsc_state.cpntBitDepth[3] = cpntBitDepth_3;
dsc_state.cpntBitDepth[cpnt] = cpntBitDepth_selected;
quantTableLuma_oracle_storage[primary_qp] = qlevel_luma;
dsc_state.quantTableLuma = quantTableLuma_oracle_storage;
quantTableChroma_oracle_storage[primary_qp] = qlevel_chroma;
dsc_state.quantTableChroma = quantTableChroma_oracle_storage;
dsc_state.quantizedResidual[unit][0] = quantized_residual_0;
dsc_state.quantizedResidual[unit][1] = quantized_residual_1;
dsc_state.quantizedResidual[unit][2] = quantized_residual_2;
        return_value = UsingMidpoint(&dsc_cfg, &dsc_state, unit, cpnt);
        printf("%d\n", return_value);
    }
    if (input != stdin) fclose(input);
    return 0;
}
