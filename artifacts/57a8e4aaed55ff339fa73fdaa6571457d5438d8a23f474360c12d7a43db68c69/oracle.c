#include <stddef.h>
#include <stdio.h>
#include "dsc_types.h"
extern int EscapeCodeSize(dsc_cfg_t * dsc_cfg, dsc_state_t * dsc_state, int qp);
int main(int argc, char **argv) {
    FILE *input = stdin;
    if (argc > 1) {
        input = fopen(argv[1], "rb");
        if (!input) return 2;
    }
    int qp, dsc_version_minor, native_420, cpntBitDepth_0, qlevel_luma;
    int return_value;
    while (fscanf(input, "%d %d %d %d %d", &qp, &dsc_version_minor, &native_420, &cpntBitDepth_0, &qlevel_luma) == 5) {
        dsc_cfg_t dsc_cfg = {0};
        dsc_state_t dsc_state = {0};
        int quantTableLuma_oracle_storage[32] = {0};
        dsc_cfg.dsc_version_minor = dsc_version_minor;
dsc_cfg.native_420 = native_420;
dsc_state.cpntBitDepth[0] = cpntBitDepth_0;
quantTableLuma_oracle_storage[qp] = qlevel_luma;
dsc_state.quantTableLuma = quantTableLuma_oracle_storage;
        return_value = EscapeCodeSize(&dsc_cfg, &dsc_state, qp);
        printf("%d\n", return_value);
    }
    if (input != stdin) fclose(input);
    return 0;
}
