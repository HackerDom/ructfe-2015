#include <stdlib.h>
#include <stdio.h>
#include <string.h>

#include "dict/dict.h"
#include "common.h"
#include "cgi.h"

int check_args(char* login) {
    if (!login) {
        printf("%s\n", "Error: No login");
        return 1;
    }

    if (!login_good(login)) {
        printf("%s\n", "Error: Bad login");
        return 1;
    }
}

int main() {
    printf("Content-type: text/html;charset=UTF-8\n\n");
    printf("<head><title>Account</title><head>\n");

    char* login = cgigetval("login");
    if(check_args(login) == -1) {
        return 1;
    }

    printf("Logged in as %s (<a href='.'>Log out</a>)<br>\n", login);

    struct dict t;
    if(new_dict(login, &t) == -1) {
        printf("Internal error\n");
        return 1;
    }

    long accounts_num = t.size();
    if (accounts_num == 0) {
        printf("You have no accounts yet<br>\n");
        printf("<br>\n");
    } else {
        printf("Accounts available:<br>\n");

        int i;
        for (i = 0; i < accounts_num; i += 1) {
            unsigned char* key = t.key_at(i);
            if (!key) {
                continue;
            }

            unsigned long value = t.get(key);

            printf("%s: %lu₽ ", key, value);
            printf("Transfer to: <form action='transfer_money.cgi'>\n");
            printf("login: <input value='' name='login_to'>\n");
            printf("account: <input value='' name='account_to'>\n");
            printf("amount: <input value='' name='amount'>\n");
            printf("<input type='hidden' value='%s' name='login'><br>\n", login);
            printf("<input type='hidden' value='%s' name='account'><br>\n", key);
            printf("<input type='submit'>\n");
            printf("</form>\n");
        }
    }

    printf("Add money on account (account will be created):<br>\n");

    printf("<form action='add_money.cgi'>\n");
    printf("Account: <input value='' name='account'><br>\n");
    printf("Amount: <input value='' name='amount'><br>\n");
    printf("<input type='hidden' value='%s' name='login'><br>\n", login);
    printf("<input type='submit'>\n");
    printf("</form>\n");

    return 0;
}
