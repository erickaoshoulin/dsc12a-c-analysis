#include <stddef.h>
#include <stdio.h>
#include "dsc_types.h"
extern int Qp2Qlevel(dsc_cfg_t * dsc_cfg, int qp, int cpnt);
int main(int argc, char **argv) {
    FILE *input = stdin;
    if (argc > 1) {
        input = fopen(argv[1], "rb");
        if (!input) return 2;
    }
    int cpnt, qp, bits_per_component, convert_rgb, dsc_version_minor, native_420;
    int return_value;
    while (fscanf(input, "%d %d %d %d %d %d", &cpnt, &qp, &bits_per_component, &convert_rgb, &dsc_version_minor, &native_420) == 6) {
        dsc_cfg_t dsc_cfg = {0};
        dsc_cfg.bits_per_component = bits_per_component;
dsc_cfg.convert_rgb = convert_rgb;
dsc_cfg.dsc_version_minor = dsc_version_minor;
dsc_cfg.native_420 = native_420;
        return_value = Qp2Qlevel(&dsc_cfg, qp, cpnt);
        printf("%d\n", return_value);
    }
    if (input != stdin) fclose(input);
    return 0;
}
