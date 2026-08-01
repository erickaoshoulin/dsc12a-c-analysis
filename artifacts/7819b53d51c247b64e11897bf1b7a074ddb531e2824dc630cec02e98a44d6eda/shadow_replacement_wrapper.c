/* Generated C-only/shadow/RTL-return dispatcher for contract findmidpoint. */
#include <stdint.h>
enum dsc_cicd_mode { DSC_C_ONLY = 0, DSC_SHADOW = 1, DSC_RTL_RETURN = 2 };
static enum dsc_cicd_mode dsc_cicd_mode_findmidpoint = DSC_C_ONLY;
static unsigned long dsc_cicd_mismatches_findmidpoint;
void dsc_cicd_set_mode_findmidpoint(enum dsc_cicd_mode mode) { dsc_cicd_mode_findmidpoint = mode; }
unsigned long dsc_cicd_mismatch_count_findmidpoint(void) { return dsc_cicd_mismatches_findmidpoint; }
int dsc_cicd_dispatch_scalar_findmidpoint(int c_value, int rtl_value) {
    if (dsc_cicd_mode_findmidpoint != DSC_C_ONLY && c_value != rtl_value) ++dsc_cicd_mismatches_findmidpoint;
    return dsc_cicd_mode_findmidpoint == DSC_RTL_RETURN ? rtl_value : c_value;
}
