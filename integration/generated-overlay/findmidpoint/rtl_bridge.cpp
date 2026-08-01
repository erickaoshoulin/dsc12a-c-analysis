        #include <cstdint>
        #include <verilated.h>
        #include "Vfindmidpoint_candidate_01.h"
        extern "C" int dsc_cicd_rtl_findmidpoint(int cpnt, int qlevel, int cpntBitDepth, int leftRecon) {
            static VerilatedContext context;
            static Vfindmidpoint_candidate_01 dut{&context};
            dut.cpnt = static_cast<std::uint64_t>(cpnt);
dut.qlevel = static_cast<std::uint64_t>(qlevel);
dut.cpnt_bit_depth = static_cast<std::uint64_t>(cpntBitDepth);
dut.left_recon = static_cast<std::uint64_t>(leftRecon);
dut.eval();
            return static_cast<int>(dut.return_value);
        }
