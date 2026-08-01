#include <cstdlib>
#include <cstdio>
#include "dsc_cicd_overlay.h"
extern "C" int dsc_cicd_original_main(int, char**);
int main(int argc, char** argv) {
    const char* value = std::getenv("DSC_CICD_MODE");
    int mode = value ? std::atoi(value) : 0;
    dsc_cicd_set_mode_findmidpoint(static_cast<dsc_cicd_mode>(mode));
    int result = dsc_cicd_original_main(argc, argv);
    unsigned long mismatches = dsc_cicd_mismatch_count_findmidpoint();
    if (mismatches) std::fprintf(stderr, "C/RTL mismatches: %lu\n", mismatches);
    return mismatches ? 86 : result;
}
