/* Generated C-only/shadow/RTL-return dispatcher for contract mapqptoqlevel. */
#include <stdint.h>
enum dsc_cicd_mode { DSC_C_ONLY = 0, DSC_SHADOW = 1, DSC_RTL_RETURN = 2 };
static enum dsc_cicd_mode dsc_cicd_mode_mapqptoqlevel = DSC_C_ONLY;
static unsigned long dsc_cicd_mismatches_mapqptoqlevel;
void dsc_cicd_set_mode_mapqptoqlevel(enum dsc_cicd_mode mode) { dsc_cicd_mode_mapqptoqlevel = mode; }
unsigned long dsc_cicd_mismatch_count_mapqptoqlevel(void) { return dsc_cicd_mismatches_mapqptoqlevel; }
int dsc_cicd_dispatch_scalar_mapqptoqlevel(int c_value, int rtl_value) {
    if (dsc_cicd_mode_mapqptoqlevel != DSC_C_ONLY && c_value != rtl_value) ++dsc_cicd_mismatches_mapqptoqlevel;
    return dsc_cicd_mode_mapqptoqlevel == DSC_RTL_RETURN ? rtl_value : c_value;
}
