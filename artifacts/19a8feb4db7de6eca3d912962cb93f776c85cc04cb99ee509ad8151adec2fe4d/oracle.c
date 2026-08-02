#include <stdio.h>
            #include "dsc_types.h"
extern int PredictSize(dsc_cfg_t * dsc_cfg, int * req_size);
            int main(int argc, char **argv) {
                FILE *input = stdin;
                if (argc > 1) {
                    input = fopen(argv[1], "rb");
                    if (!input) return 2;
                }
                int req_size_0, req_size_1, req_size_2;
                int return_value;
                while (fscanf(input, "%d %d %d", &req_size_0, &req_size_1, &req_size_2) == 3) {
                    dsc_cfg_t dsc_cfg = {0};
                        int req_size[3] = {0};
                    req_size[0] = req_size_0;
                        req_size[1] = req_size_1;
                        req_size[2] = req_size_2;
                    return_value = PredictSize(&dsc_cfg, req_size);
                    printf("%d\n", return_value);
                }
                if (input != stdin) fclose(input);
                return 0;
            }
