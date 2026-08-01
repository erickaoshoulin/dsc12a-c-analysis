#include <cstdint>
#include <iostream>
#include <limits>
#include "Vfindmidpoint_candidate_01.h"

extern "C" int dsc_contract_oracle(int cpnt, int cpnt_bit_depth, int left_recon, int qlevel);

static int qlevel_max(int cpnt_bit_depth) {
    switch (cpnt_bit_depth) {
    case 8: case 9: return 8;
    case 10: case 11: return 10;
    case 12: case 13: return 12;
    case 14: case 15: return 14;
    default: return 16;
    }
}

int main(int argc, char** argv) {
    VerilatedContext* context = new VerilatedContext;
    context->commandArgs(argc, argv);
    Vfindmidpoint_candidate_01* dut = new Vfindmidpoint_candidate_01{context};
    std::uint64_t vectors = 0;
    for (int cpnt_bit_depth = 8; cpnt_bit_depth <= 16; ++cpnt_bit_depth) {
        const int max_sample = 1 << cpnt_bit_depth;
        for (int cpnt = 0; cpnt < 4; ++cpnt) {
            for (int qlevel = 0; qlevel <= qlevel_max(cpnt_bit_depth); ++qlevel) {
                for (int left_recon = 0; left_recon < max_sample; ++left_recon) {
                    dut->cpnt = static_cast<std::uint8_t>(cpnt);
                    dut->cpnt_bit_depth = static_cast<std::uint8_t>(cpnt_bit_depth);
                    dut->left_recon = static_cast<std::uint16_t>(left_recon);
                    dut->qlevel = static_cast<std::uint8_t>(qlevel);
                    dut->eval();
                    const int expected = dsc_contract_oracle(cpnt, cpnt_bit_depth, left_recon, qlevel);
                    const int actual = static_cast<int>(dut->return_value);
                    ++vectors;
                    if (actual != expected) {
                        std::cout << "RESULT status=COUNTEREXAMPLE vectors=" << vectors
                                  << " mismatches=1 cpnt=" << cpnt
                                  << " cpnt_bit_depth=" << cpnt_bit_depth
                                  << " left_recon=" << left_recon
                                  << " qlevel=" << qlevel
                                  << " expected=" << expected
                                  << " actual=" << actual << "\n";
                        delete dut;
                        delete context;
                        return 1;
                    }
                }
            }
        }
    }
    std::cout << "RESULT status=EXHAUSTIVE_EQUIVALENT vectors=" << vectors
              << " mismatches=0\n";
    delete dut;
    delete context;
    return 0;
}
