#include <stdlib.h>
#include <stdio.h>
#include <string.h>

#include <sys/mman.h>

#include "dict/dict.h"

int main() {
    int ret;

    struct dict t;
    ret = new_dict("mydict", &t);
    if(ret == -1) {
        return 1;
    }

    printf("set = %p\n", t.set);

    unsigned char buf[128] = {0};

    void* max_addr = 0;

    int i;
    for (i = 0; i < 32000; i += 1) {
        sprintf(buf, "testttq16%d", i);
        // t.set(buf, i * 2 + 1);
    }

    printf("SUCESSFULL\n");

    for (i = 0; i < 32000; i += 1) {
        sprintf(buf, "testttq16%d", i);
        long a = t.get(buf);
        if(a || i == 0) {
            printf("%lu ", a);
            fflush(stdout);
        }
    }

    printf("\n%lu\n", t.size());

    for (i = 0; i < (t.size() + 1); i ++) {
        unsigned char *c = t.key_at(i);
        if(c) {
            printf("i = %d key = %s\n", i, c);
        } else {
            printf("i = %d key = <nil>\n", i);
        }
    }
    printf("%lu\n", t.validate());

    printf("Bank service is started. Ready for clients\n"); 

    return 0;
}
