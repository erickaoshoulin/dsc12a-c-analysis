#include <stdio.h>
#include "dsc_cicd_overlay.h"
extern int dsc_cicd_original_findmidpoint(dsc_state_t *state, int cpnt, int qlevel);
static enum dsc_cicd_mode mode_findmidpoint = DSC_C_ONLY;
static unsigned long mismatches_findmidpoint;
void dsc_cicd_set_mode_findmidpoint(enum dsc_cicd_mode mode) { mode_findmidpoint = mode; }
unsigned long dsc_cicd_mismatch_count_findmidpoint(void) { return mismatches_findmidpoint; }
int dsc_cicd_dispatch_findmidpoint(dsc_state_t *state, int cpnt, int qlevel) {
    int c_value = dsc_cicd_original_findmidpoint(state, cpnt, qlevel);
    if (mode_findmidpoint == DSC_C_ONLY) return c_value;
    int rtl_value = dsc_cicd_rtl_findmidpoint(cpnt, qlevel, state->cpntBitDepth[cpnt], state->leftRecon[cpnt]);
    if (c_value != rtl_value) ++mismatches_findmidpoint;
    return mode_findmidpoint == DSC_RTL_RETURN ? rtl_value : c_value;
}
