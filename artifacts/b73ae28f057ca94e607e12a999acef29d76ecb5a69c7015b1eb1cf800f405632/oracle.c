#include <stddef.h>
#include <stdio.h>
#include "dsc_types.h"
extern int FindMidpoint(dsc_state_t * dsc_state, int cpnt, int qlevel);
int main(int argc, char **argv) {
    FILE *input = stdin;
    if (argc > 1) {
        input = fopen(argv[1], "rb");
        if (!input) return 2;
    }
    int cpnt, qlevel, cpntBitDepth, leftRecon;
    int return_value;
    while (fscanf(input, "%d %d %d %d", &cpnt, &qlevel, &cpntBitDepth, &leftRecon) == 4) {
        dsc_state_t dsc_state = {0};
        for (size_t i = 0; i < sizeof(dsc_state.cpntBitDepth) / sizeof(dsc_state.cpntBitDepth[0]); ++i) dsc_state.cpntBitDepth[i] = cpntBitDepth;
for (size_t i = 0; i < sizeof(dsc_state.leftRecon) / sizeof(dsc_state.leftRecon[0]); ++i) dsc_state.leftRecon[i] = leftRecon;
        return_value = FindMidpoint(&dsc_state, cpnt, qlevel);
        printf("%d\n", return_value);
    }
    if (input != stdin) fclose(input);
    return 0;
}
