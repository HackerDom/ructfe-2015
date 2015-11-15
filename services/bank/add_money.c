#include <stdlib.h>
#include <stdio.h>
#include <string.h>

#include "dict/dict.h"
#include "common.h"
#include "cgi.h"

int check_args(char* login, char* account, char* amount) {
    if (!login) {
        printf("%s\n", "Error: No login");
        return -1;
    }

    if (!account) {
        printf("%s\n", "Error: No account");
        return -1;
    }

    if (!amount) {
        printf("%s\n", "Error: No amount");
        return -1;
    }

    if (!login_good(login)) {
        printf("%s\n", "Error: Bad login");
        return -1;
    }

    if (!account_good(account)) {
        printf("%s\n", "Error: Bad account");
        return 1;
    }
}


int main() {
    printf("Content-type: text/html\n\n");
    printf("<head><title>add_money</title><head>\n");

    char* login = cgigetval("login");
    char* account = cgigetval("account");
    char* amount = cgigetval("amount");

    if (check_args(login, account, amount) == -1) {
        return 1;
    }

    unsigned long amount_long;
    amount_long = strtoul(amount, 0, 10);
    if (amount_long == 0) {
        printf("%s\n", "Error: Bad amount");
        return 1;        
    }

    struct dict t;
    if(new_dict(login, &t) == -1) {
        printf("Internal error\n");
        return 1;
    }

    t.set(account, t.get(account) + amount_long);

    printf("Successful<br>\n");
    printf("<a href='account.cgi?login=%s'>Go Back</a>\n", login);

    return 0;
}
