#include <stddef.h>
#include <stdio.h>
#include "dsc_types.h"
extern int IsFlatnessInfoSent(dsc_cfg_t * dsc_cfg, int qp);
int main(int argc, char **argv) {
    FILE *input = stdin;
    if (argc > 1) {
        input = fopen(argv[1], "rb");
        if (!input) return 2;
    }
    int qp, flatness_min_qp, flatness_max_qp;
    int return_value;
    while (fscanf(input, "%d %d %d", &qp, &flatness_min_qp, &flatness_max_qp) == 3) {
        dsc_cfg_t dsc_cfg = {0};
        dsc_cfg.flatness_min_qp = flatness_min_qp;
dsc_cfg.flatness_max_qp = flatness_max_qp;
        return_value = IsFlatnessInfoSent(&dsc_cfg, qp);
        printf("%d\n", return_value);
    }
    if (input != stdin) fclose(input);
    return 0;
}
