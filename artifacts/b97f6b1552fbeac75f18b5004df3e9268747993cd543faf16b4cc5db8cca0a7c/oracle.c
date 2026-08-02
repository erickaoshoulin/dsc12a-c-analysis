#include <stdio.h>
extern int ceil_log2(int val);
int main(int argc, char **argv) {
    FILE *input = stdin;
    if (argc > 1) {
        input = fopen(argv[1], "rb");
        if (!input) return 2;
    }
    int val;
    int return_value;
    while (fscanf(input, "%d", &val) == 1) {
        return_value = ceil_log2(val);
        printf("%d\n", return_value);
    }
    if (input != stdin) fclose(input);
    return 0;
}
