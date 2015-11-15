#include <stdlib.h>
#include <stdio.h>
#include <string.h>

#include "dict/dict.h"
#include "cgi.h"

int login_good(char* login) {
    int i;
    for (i = 0; login[i]; i += 1) {
        if (login[i] == ' ' || login[i] == '_')
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

    char* login_to = cgigetval("login_to");
    char* account_to = cgigetval("account_to");

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

    if (!login_to) {
        printf("%s\n", "Error: No dest login");
        return 1;
    }

    if (!login_good(login_to)) {
        printf("%s\n", "Error: Bad dest login");
        return 1;
    }

    if (!account_to) {
        printf("%s\n", "Error: No dest account");
        return 1;
    }

    if (!login_good(account_to)) {
        printf("%s\n", "Error: Bad dest account");
        return 1;
    }

    amount_long = get_amount(amount);
    if (amount_long == 0) {
        printf("%s\n", "Error: Bad amount");
        return 1;        
    }

    struct dict t_from;
    ret = new_dict(login, &t_from);

    if(ret == -1) {
        printf("Internal error\n");
        return 1;
    }

    long curr_balance = t_from.get(account);
    if(curr_balance < amount_long) {
        printf("%s\n", "Error: No money");
        return 1;
    }

    struct dict t_to;
    ret = new_dict(login_to, &t_to);
    if(ret == -1) {
        printf("Internal error\n");
        return 1;
    }

    t_from.set(account, curr_balance - amount_long);
    t_to.set(account_to, t_to.get(account_to) - amount_long);

    printf("Successful<br>\n");
    printf("<a href='account.cgi?login=%s'>Go Back</a>\n", login);

    return 0;
}
