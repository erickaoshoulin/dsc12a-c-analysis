#ifndef DSC_CICD_OVERLAY_H
#define DSC_CICD_OVERLAY_H
#include "dsc_codec.h"
#ifdef __cplusplus
extern "C" {
#endif
enum dsc_cicd_mode { DSC_C_ONLY = 0, DSC_SHADOW = 1, DSC_RTL_RETURN = 2 };
void dsc_cicd_set_mode_findmidpoint(enum dsc_cicd_mode mode);
unsigned long dsc_cicd_mismatch_count_findmidpoint(void);
int dsc_cicd_dispatch_findmidpoint(dsc_state_t *state, int cpnt, int qlevel);
int dsc_cicd_rtl_findmidpoint(int cpnt, int qlevel, int cpntBitDepth, int leftRecon);
#ifdef __cplusplus
}
#endif
#endif
