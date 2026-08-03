#include <stdio.h>
            #include "dsc_types.h"
extern int SamplePredict(dsc_state_t * dsc_state, int * prevLine, int * currLine, int hPos, PRED_TYPE predType, int qLevel, int unit);
            int main(int argc, char **argv) {
                FILE *input = stdin;
                if (argc > 1) {
                    input = fopen(argv[1], "rb");
                    if (!input) return 2;
                }
                int hPos, predType, qLevel, unit, cpnt_bit_depth, unit_c_type, quantized_residual_0, quantized_residual_1, prev_3, prev_4, prev_5, prev_6, prev_7, prev_8, curr_0, curr_1, curr_2, curr_3, curr_4, curr_5, curr_6;
                int return_value;
                while (fscanf(input, "%d %d %d %d %d %d %d %d %d %d %d %d %d %d %d %d %d %d %d %d %d", &hPos, &predType, &qLevel, &unit, &cpnt_bit_depth, &unit_c_type, &quantized_residual_0, &quantized_residual_1, &prev_3, &prev_4, &prev_5, &prev_6, &prev_7, &prev_8, &curr_0, &curr_1, &curr_2, &curr_3, &curr_4, &curr_5, &curr_6) == 21) {
                    dsc_state_t dsc_state = {0};
                        int prevLine[9] = {0};
                        int currLine[7] = {0};
                    prevLine[3] = prev_3;
                        prevLine[4] = prev_4;
                        prevLine[5] = prev_5;
                        prevLine[6] = prev_6;
                        prevLine[7] = prev_7;
                        prevLine[8] = prev_8;
                        currLine[0] = curr_0;
                        currLine[1] = curr_1;
                        currLine[2] = curr_2;
                        currLine[3] = curr_3;
                        currLine[4] = curr_4;
                        currLine[5] = curr_5;
                        currLine[6] = curr_6;
                        dsc_state.cpntBitDepth[unit_c_type] = cpnt_bit_depth;
                        dsc_state.unitCType[unit] = unit_c_type;
                        dsc_state.quantizedResidual[unit][0] = quantized_residual_0;
                        dsc_state.quantizedResidual[unit][1] = quantized_residual_1;
                    return_value = SamplePredict(&dsc_state, prevLine, currLine, hPos, predType, qLevel, unit);
                    printf("%d\n", return_value);
                }
                if (input != stdin) fclose(input);
                return 0;
            }
