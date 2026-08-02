#include <stdio.h>
#include "dsc_types.h"
extern int SamplePredict(dsc_state_t * dsc_state, int * prevLine, int * currLine, int hPos, PRED_TYPE predType, int qLevel, int unit);
int main(int argc, char **argv) {
    FILE *input = stdin;
    if (argc > 1) {
        input = fopen(argv[1], "rb");
        if (!input) return 2;
    }
    int hPos, predType, qLevel, unit, cpnt_bit_depth, unit_c_type, quantized_residual_0, quantized_residual_1, prev_3, prev_4, prev_5, prev_6, prev_7, prev_8, prev_9, prev_10, prev_11, prev_12, prev_13, prev_14, prev_15, prev_16, prev_17, curr_0, curr_1, curr_2, curr_3, curr_4, curr_5, curr_6, curr_7, curr_8, curr_9, curr_10, curr_11, curr_12, curr_13, curr_14, curr_15;
    static int prevLine[65541] = {0};
    static int currLine[65541] = {0};
    while (fscanf(input, "%d %d %d %d %d %d %d %d %d %d %d %d %d %d %d %d %d %d %d %d %d %d %d %d %d %d %d %d %d %d %d %d %d %d %d %d %d %d %d", &hPos, &predType, &qLevel, &unit, &cpnt_bit_depth, &unit_c_type, &quantized_residual_0, &quantized_residual_1, &prev_3, &prev_4, &prev_5, &prev_6, &prev_7, &prev_8, &prev_9, &prev_10, &prev_11, &prev_12, &prev_13, &prev_14, &prev_15, &prev_16, &prev_17, &curr_0, &curr_1, &curr_2, &curr_3, &curr_4, &curr_5, &curr_6, &curr_7, &curr_8, &curr_9, &curr_10, &curr_11, &curr_12, &curr_13, &curr_14, &curr_15) == 39) {
        dsc_state_t dsc_state = {0};
        dsc_state.cpntBitDepth[unit_c_type] = cpnt_bit_depth;
            dsc_state.unitCType[unit] = unit_c_type;
            dsc_state.quantizedResidual[unit][0] = quantized_residual_0;
            dsc_state.quantizedResidual[unit][1] = quantized_residual_1;
            prevLine[((hPos / 3) * 3 + 5 + -2) + 0] = prev_3;
            prevLine[((hPos / 3) * 3 + 5 + -2) + 1] = prev_4;
            prevLine[((hPos / 3) * 3 + 5 + -2) + 2] = prev_5;
            prevLine[((hPos / 3) * 3 + 5 + -2) + 3] = prev_6;
            prevLine[((hPos / 3) * 3 + 5 + -2) + 4] = prev_7;
            prevLine[((hPos / 3) * 3 + 5 + -2) + 5] = prev_8;
            currLine[((hPos > 8) ? (hPos - 8) : 0) + 0] = curr_0;
            currLine[((hPos > 8) ? (hPos - 8) : 0) + 1] = curr_1;
            currLine[((hPos > 8) ? (hPos - 8) : 0) + 2] = curr_2;
            currLine[((hPos > 8) ? (hPos - 8) : 0) + 3] = curr_3;
            currLine[((hPos > 8) ? (hPos - 8) : 0) + 4] = curr_4;
            currLine[((hPos > 8) ? (hPos - 8) : 0) + 5] = curr_5;
            currLine[((hPos > 8) ? (hPos - 8) : 0) + 6] = curr_6;
            currLine[((hPos > 8) ? (hPos - 8) : 0) + 7] = curr_7;
            currLine[((hPos > 8) ? (hPos - 8) : 0) + 8] = curr_8;
            currLine[((hPos > 8) ? (hPos - 8) : 0) + 9] = curr_9;
            currLine[((hPos > 8) ? (hPos - 8) : 0) + 10] = curr_10;
            currLine[((hPos > 8) ? (hPos - 8) : 0) + 11] = curr_11;
            currLine[((hPos > 8) ? (hPos - 8) : 0) + 12] = curr_12;
        int return_value = SamplePredict(&dsc_state, prevLine, currLine, hPos, predType, qLevel, unit);
        printf("%d\n", return_value);
    }
    if (input != stdin) fclose(input);
    return 0;
}
