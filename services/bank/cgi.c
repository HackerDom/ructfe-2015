#include "cgi.h"

#include <stdlib.h>
#include <string.h>

int get_param(char* param, char* buf, int maxlen) {
    char* query = getenv("QUERY_STRING");
    if (!query) {
        return -1;
    }

    char query_copy[128] = {0};
    strncpy(query_copy, query, 128);

    char* token;

    int param_len = strlen(param);

    for (token = strtok(query_copy, "&"); token; token = strtok(NULL, "&")) {
        if (token[param_len] != '=') {
            continue;
        }

        if (strncmp(token, param, param_len) != 0) {
            continue;
        }

        strncpy(buf, &token[param_len + 1], maxlen);
        return 0;
    }

    return -1;
}