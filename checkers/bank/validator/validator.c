#include <stdlib.h>
#include <stdio.h>

#include "dict/dict.h"

int main(int argc, char** argv) {
    if (argc < 3) {
        printf("Bad args\n");
        return 1;
    }

    char* str = argv[1];
    unsigned long value = strtoul(argv[2], 0, 10);

    struct dict t;
    if(new_dict("dictname", &t) == -1) {
        printf("Internal error\n");
        return 1;
    }

    t.set(str, value);
    printf("%lu\n", t.validate());

    return 0;
}
