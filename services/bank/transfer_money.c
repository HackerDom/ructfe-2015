#include <stdlib.h>
#include <stdio.h>
#include <string.h>

#include "dict/dict.h"
#include "common.h"
#include "cgi.h"

int check_args(char* login, char* account, char* amount, char* login_to, char* account_to) {
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

    if (!login_to) {
        printf("<p class='error'>Error: No dest login</p>\n");
        print_accounts_redirect();
        return -1;
    }

    if (!account_to) {
        printf("<p class='error'>Error: No dest account</p>\n");
        print_accounts_redirect();
        return -1;
    }

    if (!login_good(login)) {
        printf("<p class='error'>Error: Bad login</p>\n");
        print_bank_redirect();
        return -1;
    }

    if (!login_good(login_to)) {
        printf("<p class='error'>Error: Bad dest login</p>\n");
        print_accounts_redirect();
        return -1;
    }

    if (!account_good(account)) {
        printf("<p class='error'>Error: Bad account</p>\n");
        print_accounts_redirect();
        return -1;
    }
    if (!account_good(account_to)) {
        printf("<p class='error'>Error: Bad dest account</p>\n");
        print_accounts_redirect();
        return -1;
    }
}

int gen_page() {
    char* login = cgigetval("login");
    char* account = cgigetval("account");
    char* amount = cgigetval("amount");
    unsigned long amount_long;

    char* login_to = cgigetval("login_to");
    char* account_to = cgigetval("account_to");

    if (check_args(login, account, amount, login_to, account_to) == -1) {
        return 1;
    }

    amount_long = strtoul(amount, 0, 10);
    if (amount_long == 0) {
        printf("<p class='error'>Error: Bad amount</p>\n");
        print_accounts_redirect();
        return 1;        
    }

    struct dict t_from, to;

    if(new_dict(login, &t_from) == -1) {
        printf("Internal error\n");
        return 1;
    }

    unsigned long curr_balance = t_from.get(account);
    if(curr_balance < amount_long) {
        printf("<p class='error'>Error: No money</p>\n");
        print_accounts_redirect();
        return 1;
    }

    struct dict t_to;
    if(new_dict(login_to, &t_to) == -1) {
        printf("Internal error\n");
        return 1;
    }

    t_from.set(account, curr_balance - amount_long);
    t_to.set(account_to, t_to.get(account_to) + amount_long);

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
