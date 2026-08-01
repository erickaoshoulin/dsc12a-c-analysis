/* Generated C-only/shadow/RTL-return dispatcher for contract isflatnessinfosent. */
#include <stdint.h>
enum dsc_cicd_mode { DSC_C_ONLY = 0, DSC_SHADOW = 1, DSC_RTL_RETURN = 2 };
static enum dsc_cicd_mode dsc_cicd_mode_isflatnessinfosent = DSC_C_ONLY;
static unsigned long dsc_cicd_mismatches_isflatnessinfosent;
void dsc_cicd_set_mode_isflatnessinfosent(enum dsc_cicd_mode mode) { dsc_cicd_mode_isflatnessinfosent = mode; }
unsigned long dsc_cicd_mismatch_count_isflatnessinfosent(void) { return dsc_cicd_mismatches_isflatnessinfosent; }
int dsc_cicd_dispatch_scalar_isflatnessinfosent(int c_value, int rtl_value) {
    if (dsc_cicd_mode_isflatnessinfosent != DSC_C_ONLY && c_value != rtl_value) ++dsc_cicd_mismatches_isflatnessinfosent;
    return dsc_cicd_mode_isflatnessinfosent == DSC_RTL_RETURN ? rtl_value : c_value;
}
