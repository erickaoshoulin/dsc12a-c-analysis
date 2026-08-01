#include <string.h>
#include "dsc_codec.h"

extern int FindMidpoint(dsc_state_t *, int, int);

int dsc_contract_oracle(int cpnt, int cpnt_bit_depth, int left_recon, int qlevel)
{
    dsc_state_t state;
    memset(&state, 0, sizeof(state));
    state.cpntBitDepth[cpnt] = cpnt_bit_depth;
    state.leftRecon[cpnt] = left_recon;
    return FindMidpoint(&state, cpnt, qlevel);
}
