#include <stdio.h>
#include "dsc_types.h"
extern int IsOrigFlatHIndex(dsc_cfg_t * dsc_cfg, dsc_state_t * dsc_state, int hPos);
static int flat_luma_8[32] = {0, 0, 0, 1, 1, 2, 2, 3, 3, 4, 4, 5, 5, 5, 6, 7, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0}; static int flat_chroma_8[32] = {0, 1, 2, 2, 3, 3, 4, 4, 5, 5, 6, 6, 7, 8, 8, 8, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0}; static int flat_luma_10[32] = {0, 0, 0, 1, 1, 2, 2, 3, 3, 4, 4, 5, 5, 6, 6, 7, 7, 7, 8, 9, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0}; static int flat_chroma_10[32] = {0, 1, 2, 2, 3, 3, 4, 4, 5, 5, 6, 6, 7, 7, 8, 8, 9, 10, 10, 10, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0}; static int flat_luma_12[32] = {0, 0, 0, 1, 1, 2, 2, 3, 3, 4, 4, 5, 5, 6, 6, 7, 7, 8, 8, 9, 9, 9, 10, 11, 0, 0, 0, 0, 0, 0, 0, 0}; static int flat_chroma_12[32] = {0, 1, 2, 2, 3, 3, 4, 4, 5, 5, 6, 6, 7, 7, 8, 8, 9, 9, 10, 10, 11, 12, 12, 12, 0, 0, 0, 0, 0, 0, 0, 0}; static int flat_luma_14[32] = {0, 0, 0, 1, 1, 2, 2, 3, 3, 4, 4, 5, 5, 6, 6, 7, 7, 8, 8, 9, 9, 10, 10, 11, 11, 11, 12, 13, 0, 0, 0, 0}; static int flat_chroma_14[32] = {0, 1, 2, 2, 3, 3, 4, 4, 5, 5, 6, 6, 7, 7, 8, 8, 9, 9, 10, 10, 11, 11, 12, 12, 13, 14, 14, 14, 0, 0, 0, 0}; static int flat_luma_16[32] = {0, 0, 0, 1, 1, 2, 2, 3, 3, 4, 4, 5, 5, 6, 6, 7, 7, 8, 8, 9, 9, 10, 10, 11, 11, 12, 12, 13, 13, 13, 14, 15}; static int flat_chroma_16[32] = {0, 1, 2, 2, 3, 3, 4, 4, 5, 5, 6, 6, 7, 7, 8, 8, 9, 9, 10, 10, 11, 11, 12, 12, 13, 13, 14, 14, 15, 16, 16, 16};
int main(int argc, char **argv) {
    FILE *input = stdin;
    if (argc > 1) {
        input = fopen(argv[1], "rb");
        if (!input) return 2;
    }
    int hPos, bits_per_component, primary_qp, num_components, slice_width, flatness_det_thresh, somewhat_flat_qp_delta, native_420, dsc_version_minor, cpnt_bit_depth_0, cpnt_bit_depth_1, orig_0_0, orig_0_1, orig_0_2, orig_0_3, orig_0_4, orig_0_5, orig_0_6, orig_1_0, orig_1_1, orig_1_2, orig_1_3, orig_1_4, orig_1_5, orig_1_6, orig_2_0, orig_2_1, orig_2_2, orig_2_3, orig_2_4, orig_2_5, orig_2_6, orig_3_0, orig_3_1, orig_3_2, orig_3_3, orig_3_4, orig_3_5, orig_3_6;
    static int orig_line_0[65547] = {0};
    static int orig_line_1[65547] = {0};
    static int orig_line_2[65547] = {0};
    static int orig_line_3[65547] = {0};
    while (fscanf(input, "%d %d %d %d %d %d %d %d %d %d %d %d %d %d %d %d %d %d %d %d %d %d %d %d %d %d %d %d %d %d %d %d %d %d %d %d %d %d %d", &hPos, &bits_per_component, &primary_qp, &num_components, &slice_width, &flatness_det_thresh, &somewhat_flat_qp_delta, &native_420, &dsc_version_minor, &cpnt_bit_depth_0, &cpnt_bit_depth_1, &orig_0_0, &orig_0_1, &orig_0_2, &orig_0_3, &orig_0_4, &orig_0_5, &orig_0_6, &orig_1_0, &orig_1_1, &orig_1_2, &orig_1_3, &orig_1_4, &orig_1_5, &orig_1_6, &orig_2_0, &orig_2_1, &orig_2_2, &orig_2_3, &orig_2_4, &orig_2_5, &orig_2_6, &orig_3_0, &orig_3_1, &orig_3_2, &orig_3_3, &orig_3_4, &orig_3_5, &orig_3_6) == 39) {
        dsc_cfg_t dsc_cfg = {0};
        dsc_state_t dsc_state = {0};
        dsc_cfg.bits_per_component = bits_per_component;
            dsc_cfg.flatness_det_thresh = flatness_det_thresh;
            dsc_cfg.somewhat_flat_qp_delta = somewhat_flat_qp_delta;
            dsc_cfg.native_420 = native_420;
            dsc_cfg.dsc_version_minor = dsc_version_minor;
            dsc_state.numComponents = num_components;
            dsc_state.sliceWidth = slice_width;
            dsc_state.primaryQp = primary_qp;
            dsc_state.cpntBitDepth[0] = cpnt_bit_depth_0;
            dsc_state.cpntBitDepth[1] = cpnt_bit_depth_1;
            dsc_state.origLine[0] = orig_line_0;
            dsc_state.origLine[1] = orig_line_1;
            dsc_state.origLine[2] = orig_line_2;
            dsc_state.origLine[3] = orig_line_3;
            switch (bits_per_component) {
            case 8: dsc_state.quantTableLuma = flat_luma_8; dsc_state.quantTableChroma = flat_chroma_8; break;
            case 10: dsc_state.quantTableLuma = flat_luma_10; dsc_state.quantTableChroma = flat_chroma_10; break;
            case 12: dsc_state.quantTableLuma = flat_luma_12; dsc_state.quantTableChroma = flat_chroma_12; break;
            case 14: dsc_state.quantTableLuma = flat_luma_14; dsc_state.quantTableChroma = flat_chroma_14; break;
            case 16: dsc_state.quantTableLuma = flat_luma_16; dsc_state.quantTableChroma = flat_chroma_16; break;
            default: dsc_state.quantTableLuma = flat_luma_8; dsc_state.quantTableChroma = flat_chroma_8; break;
            }
            orig_line_0[PADDING_LEFT + hPos + 0] = orig_0_0;
            orig_line_0[PADDING_LEFT + hPos + 1] = orig_0_1;
            orig_line_0[PADDING_LEFT + hPos + 2] = orig_0_2;
            orig_line_0[PADDING_LEFT + hPos + 3] = orig_0_3;
            orig_line_0[PADDING_LEFT + hPos + 4] = orig_0_4;
            orig_line_0[PADDING_LEFT + hPos + 5] = orig_0_5;
            orig_line_0[PADDING_LEFT + hPos + 6] = orig_0_6;
            orig_line_1[PADDING_LEFT + hPos + 0] = orig_1_0;
            orig_line_1[PADDING_LEFT + hPos + 1] = orig_1_1;
            orig_line_1[PADDING_LEFT + hPos + 2] = orig_1_2;
            orig_line_1[PADDING_LEFT + hPos + 3] = orig_1_3;
            orig_line_1[PADDING_LEFT + hPos + 4] = orig_1_4;
            orig_line_1[PADDING_LEFT + hPos + 5] = orig_1_5;
            orig_line_1[PADDING_LEFT + hPos + 6] = orig_1_6;
            orig_line_2[PADDING_LEFT + hPos + 0] = orig_2_0;
            orig_line_2[PADDING_LEFT + hPos + 1] = orig_2_1;
            orig_line_2[PADDING_LEFT + hPos + 2] = orig_2_2;
            orig_line_2[PADDING_LEFT + hPos + 3] = orig_2_3;
            orig_line_2[PADDING_LEFT + hPos + 4] = orig_2_4;
            orig_line_2[PADDING_LEFT + hPos + 5] = orig_2_5;
            orig_line_2[PADDING_LEFT + hPos + 6] = orig_2_6;
            orig_line_3[PADDING_LEFT + hPos + 0] = orig_3_0;
            orig_line_3[PADDING_LEFT + hPos + 1] = orig_3_1;
            orig_line_3[PADDING_LEFT + hPos + 2] = orig_3_2;
            orig_line_3[PADDING_LEFT + hPos + 3] = orig_3_3;
            orig_line_3[PADDING_LEFT + hPos + 4] = orig_3_4;
            orig_line_3[PADDING_LEFT + hPos + 5] = orig_3_5;
            orig_line_3[PADDING_LEFT + hPos + 6] = orig_3_6;
        int return_value = IsOrigFlatHIndex(&dsc_cfg, &dsc_state, hPos);
        printf("%d\n", return_value);
    }
    if (input != stdin) fclose(input);
    return 0;
}
