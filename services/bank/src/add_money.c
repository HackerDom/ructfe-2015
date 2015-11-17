#include <stdlib.h>
#include <stdio.h>
#include <string.h>

#include "dict/dict.h"
#include "common.h"
#include "cgi.h"

int check_args(char* login, char* account, char* amount) {
    if (!login) {
        printf("<p class='error'>Error: No login</p>\n");
        print_bank_redirect();
        return -1;
    }

    if (!account) {
        printf("<p class='error'>Error: No account</p>\n");
        print_accounts_redirect();
        return -1;
    }

    if (!amount) {
        printf("<p class='error'>Error: No amount</p>\n");
        print_accounts_redirect();
        return -1;
    }

    if (!login_good(login)) {
        printf("<p class='error'>Error: Bad login</p>\n");
        print_bank_redirect();
        return -1;
    }

    if (!account_good(account)) {
        printf("<p class='error'>Error: Bad account</p>\n");
        print_accounts_redirect();
        return -1;
    }
}

int gen_page() {
    char* login = cgigetval("login");
    char* account = cgigetval("account");
    char* amount = cgigetval("amount");

    if (check_args(login, account, amount) == -1) {
        return 1;
    }

    unsigned long amount_long;
    amount_long = strtoul(amount, 0, 10);
    if (amount_long == 0) {
        printf("<p class='error'>Error: Bad amount</p>\n");
        print_accounts_redirect();
        return 1;        
    }

    struct dict t;
    if(new_dict(login, &t) == -1) {
        printf("Internal error\n");
        return 1;
    }

    t.set(account, t.get(account) + amount_long);

    printf("<p class='success'>Successful!</p>\n");
    print_accounts_redirect();
}

int main() {
    int ret;
    print_header(1);
    ret = gen_page();
    print_footer();

    return ret;
}
