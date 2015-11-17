#include <stdlib.h>
#include <stdio.h>
#include <string.h>

#include "dict/dict.h"

int main() {
    struct dict t;
    if(new_dict("dictname", &t) == -1) {
        printf("Internal error\n");
        return 1;
    }

    t.set("key", 123);
    t.set("key2", 1234);

    printf("value for key: %lu\n", t.get("key"));
    printf("validator: %lu\n", t.validate());

}
