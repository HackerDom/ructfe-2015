#include <stdlib.h>
#include <stdio.h>
#include <string.h>

#include "dict/dict.h"

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

int main() {
    int ret;

    printf("Content-type: text/html;charset=UTF-8\n\n");
    printf("<head><title>Account</title><head>\n");

    char *body = ""
    "</form>";

    printf("<body>%s</body>", body);

    char login[256];
    ret = get_param("login", login, 256);
    if (ret == -1) {
        printf("%s\n", "Error: No login");
        return 1;
    }

    if (!login_good(login)) {
        printf("%s\n", "Error: Bad login");
        return 1;
    }

    printf("Logged in as %s (<a href='.'>Log out</a>)<br>\n", login);

    struct dict t;
    ret = new_dict(login, &t);

    if(ret == -1) {
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

            long value = t.get(key);

            printf("%s: %ld.%ld₽ ", key, value / 100, value % 100);
            printf("Transfer to: <form action='transfer.cgi'>\n");
            printf("</form>\n");
        }
    }

    printf("Add money on account (account will be created):<br>\n");

    printf("<form action='add_money.cgi'>\n");
    printf("Account: <input value='123' name='account'><br>\n");
    printf("Amount: <input value='123.45' name='amount'><br>\n");
    printf("<input type='hidden' value='%s' name='login'><br>\n", login);
    printf("<input type='submit'>\n");
    printf("</form>\n");

    return 0;
}
