#include <stddef.h>
#include <stdio.h>
#include "dsc_types.h"
extern int MapQpToQlevel(dsc_cfg_t * dsc_cfg, dsc_state_t * dsc_state, int qp, int cpnt);
int main(int argc, char **argv) {
    FILE *input = stdin;
    if (argc > 1) {
        input = fopen(argv[1], "rb");
        if (!input) return 2;
    }
    int cpnt, qp, dsc_version_minor, native_420, cpntBitDepth_0, cpntBitDepth_1, qlevel_luma, qlevel_chroma;
    int return_value;
    while (fscanf(input, "%d %d %d %d %d %d %d %d", &cpnt, &qp, &dsc_version_minor, &native_420, &cpntBitDepth_0, &cpntBitDepth_1, &qlevel_luma, &qlevel_chroma) == 8) {
        dsc_cfg_t dsc_cfg = {0};
        dsc_state_t dsc_state = {0};
        int quantTableLuma_oracle_storage[32] = {0};
        int quantTableChroma_oracle_storage[32] = {0};
        dsc_cfg.dsc_version_minor = dsc_version_minor;
dsc_cfg.native_420 = native_420;
dsc_state.cpntBitDepth[0] = cpntBitDepth_0;
dsc_state.cpntBitDepth[1] = cpntBitDepth_1;
quantTableLuma_oracle_storage[qp] = qlevel_luma;
dsc_state.quantTableLuma = quantTableLuma_oracle_storage;
quantTableChroma_oracle_storage[qp] = qlevel_chroma;
dsc_state.quantTableChroma = quantTableChroma_oracle_storage;
        return_value = MapQpToQlevel(&dsc_cfg, &dsc_state, qp, cpnt);
        printf("%d\n", return_value);
    }
    if (input != stdin) fclose(input);
    return 0;
}
