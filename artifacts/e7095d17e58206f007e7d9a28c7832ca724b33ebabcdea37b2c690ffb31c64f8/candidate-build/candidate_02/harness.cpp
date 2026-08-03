#include <cstdio>
        #include <cstdint>
        #include <iostream>
        #include "verilated.h"
        #include "Vsamplepredict_candidate_02.h"

        static long long sign_extend(long long value, int width) {
            if (width >= 63) return value;
            const long long bit = 1LL << (width - 1);
            const long long mask = (1LL << width) - 1;
            value &= mask;
            return (value & bit) ? value - (1LL << width) : value;
        }

        int main(int argc, char **argv) {
            Verilated::commandArgs(argc, argv);
            FILE *input = stdin;
            if (argc > 1) {
                input = std::fopen(argv[1], "rb");
                if (!input) return 2;
            }
            long long hPos;
long long predType;
long long qLevel;
long long unit;
long long cpnt_bit_depth;
long long unit_c_type;
long long quantized_residual_0;
long long quantized_residual_1;
long long prev_3;
long long prev_4;
long long prev_5;
long long prev_6;
long long prev_7;
long long prev_8;
long long prev_9;
long long prev_10;
long long prev_11;
long long prev_12;
long long prev_13;
long long prev_14;
long long prev_15;
long long prev_16;
long long prev_17;
long long curr_0;
long long curr_1;
long long curr_2;
long long curr_3;
long long curr_4;
long long curr_5;
long long curr_6;
long long curr_7;
long long curr_8;
long long curr_9;
long long curr_10;
long long curr_11;
long long curr_12;
long long curr_13;
long long curr_14;
long long curr_15;
                while (std::fscanf(input, "%lld %lld %lld %lld %lld %lld %lld %lld %lld %lld %lld %lld %lld %lld %lld %lld %lld %lld %lld %lld %lld %lld %lld %lld %lld %lld %lld %lld %lld %lld %lld %lld %lld %lld %lld %lld %lld %lld %lld", &hPos, &predType, &qLevel, &unit, &cpnt_bit_depth, &unit_c_type, &quantized_residual_0, &quantized_residual_1, &prev_3, &prev_4, &prev_5, &prev_6, &prev_7, &prev_8, &prev_9, &prev_10, &prev_11, &prev_12, &prev_13, &prev_14, &prev_15, &prev_16, &prev_17, &curr_0, &curr_1, &curr_2, &curr_3, &curr_4, &curr_5, &curr_6, &curr_7, &curr_8, &curr_9, &curr_10, &curr_11, &curr_12, &curr_13, &curr_14, &curr_15) == 39) {
                Vsamplepredict_candidate_02 dut;
                dut.hPos = static_cast<long long>(hPos);
    dut.predType = static_cast<long long>(predType);
    dut.qLevel = static_cast<long long>(qLevel);
    dut.unit = static_cast<long long>(unit);
    dut.cpnt_bit_depth = static_cast<long long>(cpnt_bit_depth);
    dut.unit_c_type = static_cast<long long>(unit_c_type);
    dut.quantized_residual_0 = static_cast<long long>(quantized_residual_0);
    dut.quantized_residual_1 = static_cast<long long>(quantized_residual_1);
    dut.prev_3 = static_cast<long long>(prev_3);
    dut.prev_4 = static_cast<long long>(prev_4);
    dut.prev_5 = static_cast<long long>(prev_5);
    dut.prev_6 = static_cast<long long>(prev_6);
    dut.prev_7 = static_cast<long long>(prev_7);
    dut.prev_8 = static_cast<long long>(prev_8);
    dut.prev_9 = static_cast<long long>(prev_9);
    dut.prev_10 = static_cast<long long>(prev_10);
    dut.prev_11 = static_cast<long long>(prev_11);
    dut.prev_12 = static_cast<long long>(prev_12);
    dut.prev_13 = static_cast<long long>(prev_13);
    dut.prev_14 = static_cast<long long>(prev_14);
    dut.prev_15 = static_cast<long long>(prev_15);
    dut.prev_16 = static_cast<long long>(prev_16);
    dut.prev_17 = static_cast<long long>(prev_17);
    dut.curr_0 = static_cast<long long>(curr_0);
    dut.curr_1 = static_cast<long long>(curr_1);
    dut.curr_2 = static_cast<long long>(curr_2);
    dut.curr_3 = static_cast<long long>(curr_3);
    dut.curr_4 = static_cast<long long>(curr_4);
    dut.curr_5 = static_cast<long long>(curr_5);
    dut.curr_6 = static_cast<long long>(curr_6);
    dut.curr_7 = static_cast<long long>(curr_7);
    dut.curr_8 = static_cast<long long>(curr_8);
    dut.curr_9 = static_cast<long long>(curr_9);
    dut.curr_10 = static_cast<long long>(curr_10);
    dut.curr_11 = static_cast<long long>(curr_11);
    dut.curr_12 = static_cast<long long>(curr_12);
    dut.curr_13 = static_cast<long long>(curr_13);
    dut.curr_14 = static_cast<long long>(curr_14);
    dut.curr_15 = static_cast<long long>(curr_15);
                dut.eval();
                std::cout << static_cast<unsigned long long>(dut.return_value) << "\n";
            }
            if (input != stdin) std::fclose(input);
            return 0;
        }
