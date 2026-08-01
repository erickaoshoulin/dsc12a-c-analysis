#include <stdio.h>
extern int QuantizeResidual(int e, int qlevel);
int main(int argc, char **argv) {
    FILE *input = stdin;
    if (argc > 1) {
        input = fopen(argv[1], "rb");
        if (!input) return 2;
    }
    int e, qlevel;
    int return_value;
    while (fscanf(input, "%d %d", &e, &qlevel) == 2) {
        return_value = QuantizeResidual(e, qlevel);
        printf("%d\n", return_value);
    }
    if (input != stdin) fclose(input);
    return 0;
}
