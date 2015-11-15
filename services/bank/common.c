#include "common.h"

#include <string.h>

int login_good(char* login) {
    int i;
    for (i = 0; login[i]; i += 1) {
        if (login[i] == ' ' || login[i] == '_' || login[i] == '=')
            continue;

        if (login[i] >= '0' && login[i] <= '9') {
            continue;
        }

        if (login[i] >= 'a' && login[i] <= 'z') {
            continue;
        }

        if (login[i] >= 'A' && login[i] <= 'Z') {
            continue;
        } 
        return 0;
    }

    return 1;
}

int account_good(char* account) {
    return login_good(account);
}

unsigned long get_amount(char* amount) {
    char* dot_pos = strchr(amount, '.');

    unsigned long ret = strtoul(amount, 0, 10) * 100;
    unsigned long cents = 0;
    if(dot_pos) {
        int len = strlen(dot_pos + 1);

        if (len == 0 || len > 2) {
            return 0;
        }

        cents = strtoul(dot_pos + 1, 0, 10);
        if (len == 1) {
            cents *= 10;
        }
    }
    return ret + cents;
}
