#include <stdlib.h>
#include <stdio.h>
#include <string.h>

#include "dict/dict.h"
#include "common.h"
#include "cgi.h"


int main() {
    int ret;

    printf("Content-type: text/html\n\n");
    printf("<head><title>add_money</title><head>\n");

    char *body = "";

    printf("<body>%s</body>", body);

    char* login = cgigetval("login");
    char* account = cgigetval("account");
    char* amount = cgigetval("amount");
    long amount_long;

    if (!login) {
        printf("%s\n", "Error: No login");
        return 1;
    }

    if (!login_good(login)) {
        printf("%s\n", "Error: Bad login");
        return 1;
    }

    if (!account) {
        printf("%s\n", "Error: No account");
        return 1;
    }

    if (!account_good(account)) {
        printf("%s\n", "Error: Bad account");
        return 1;
    }

    if (!amount) {
        printf("%s\n", "Error: No amount");
        return 1;
    }

    amount_long = get_amount(amount);
    if (amount_long == 0) {
        printf("%s\n", "Error: Bad amount");
        return 1;        
    }

    struct dict t;
    ret = new_dict(login, &t);

    if(ret == -1) {
        printf("Internal error\n");
        return 1;
    }

    long curr_balance = t.get(account);
    t.set(account, curr_balance + amount_long);

    printf("Successful<br>\n");
    printf("<a href='account.cgi?login=%s'>Go Back</a>\n", login);

    return 0;
}
