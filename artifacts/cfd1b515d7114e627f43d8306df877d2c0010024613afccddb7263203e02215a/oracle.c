#include <stddef.h>
#include <stdio.h>
#include "dsc_types.h"
extern int SampToLineBuf(dsc_cfg_t * dsc_cfg, dsc_state_t * dsc_state, int x, int cpnt);
int main(int argc, char **argv) {
    FILE *input = stdin;
    if (argc > 1) {
        input = fopen(argv[1], "rb");
        if (!input) return 2;
    }
    int x, cpnt, cpntBitDepth, linebuf_depth;
    int return_value;
    while (fscanf(input, "%d %d %d %d", &x, &cpnt, &cpntBitDepth, &linebuf_depth) == 4) {
        dsc_cfg_t dsc_cfg = {0};
        dsc_state_t dsc_state = {0};
        for (size_t i = 0; i < sizeof(dsc_state.cpntBitDepth) / sizeof(dsc_state.cpntBitDepth[0]); ++i) dsc_state.cpntBitDepth[i] = cpntBitDepth;
dsc_cfg.linebuf_depth = linebuf_depth;
        return_value = SampToLineBuf(&dsc_cfg, &dsc_state, x, cpnt);
        printf("%d\n", return_value);
    }
    if (input != stdin) fclose(input);
    return 0;
}
