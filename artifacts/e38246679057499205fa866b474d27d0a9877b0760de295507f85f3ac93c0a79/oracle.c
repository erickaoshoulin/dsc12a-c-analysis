#include <stdio.h>
extern int FindResidualSize(int eq);
int main(int argc, char **argv) {
    FILE *input = stdin;
    if (argc > 1) {
        input = fopen(argv[1], "rb");
        if (!input) return 2;
    }
    int eq;
    int return_value;
    while (fscanf(input, "%d", &eq) == 1) {
        return_value = FindResidualSize(eq);
        printf("%d\n", return_value);
    }
    if (input != stdin) fclose(input);
    return 0;
}
