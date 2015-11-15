#include <stdlib.h>
#include <stdio.h>
#include <string.h>

#include "dict/dict.h"
#include "common.h"
#include "cgi.h"

int check_args(char* login) {
    if (!login) {
        printf("<p class='error'>Error: No login</p>\n");
        print_bank_redirect();
        return -1;
    }

    if (!login_good(login)) {
        printf("<p class='error'>Error: Bad login</p>\n");
        print_bank_redirect();
        return -1;
    }
}

int gen_page() {
    char* login = cgigetval("login");
    if(check_args(login) == -1) {
        return 1;
    }

    printf("              <h1>Your bank accounts (%s)</h1>\n", login);
    printf("              <div class='extra-space-m'></div>\n");

    struct dict t;
    if(new_dict(login, &t) == -1) {
        printf("Internal error\n");
        return 1;
    }

    long accounts_num = t.size();
    if (accounts_num == 0) {
        printf("<h6>You don't have any accounts yet</h6>\n");
        printf("<br>\n");
    } else {
        printf("  <table class='table table-striped'>\n");

        printf("  <thead>\n");
        printf("      <tr>\n");
        printf("          <th>Account</th>\n");
        printf("          <th>Balance</th>\n");
        printf("          <th class='col-md-1 text-right'></th>\n");
        printf("      </tr>\n");
        printf("  </thead>\n");
        printf("  <tbody>\n");


        int i;
        for (i = 0; i < accounts_num; i += 1) {
            unsigned char* key = t.key_at(i);
            if (!key) {
                continue;
            }

            unsigned long value = t.get(key);

            printf("      <tr>\n");
            printf("          <td>%s</td>\n", key);
            printf("          <td>%lu₽</td>\n", value);
            printf("          <td class='col-md-1 text-right'><span data-toggle='modal' data-target='#Modal%d' class='glyphicon glyphicon-transfer pointer-cursor' aria-hidden='true'></span></td>\n", i);
            printf("<div id='Modal%d' class='modal fade' tabindex='-1' role='dialog' aria-labelledby='myModalLabel' aria-hidden='true'>\n", i);
            printf(" <div class='modal-dialog'>\n");
            printf("    <div class='modal-content'>\n");
            printf("      <div class='modal-header'>\n");
            printf("        <button type='button' class='close' data-dismiss='modal' aria-hidden='true'>&times;  </button>\n");
            printf("        <h4 class='modal-title' id='myModalLabel'>Transfer money</h4>\n");
            printf("      </div>\n");
            printf("      <form action='transfer_money.cgi'>\n");
            printf("      <div class='modal-body'>\n");
            printf("        <div class='form-group'>\n");
            printf("          <label for='fromAccount'>From</label>\n");
            printf("          <input value='%s' name='account' class='form-control' id='fromAccount' placeholder='Account' readonly>\n", key);
            printf("        </div>\n");
            printf("        <div class='form-group'>\n");
            printf("          <label for='toLogin'>To</label>\n");
            printf("          <input value='' name='login_to' class='form-control' id='toLogin' placeholder='Login'>\n");
            printf("          <input value='' name='account_to' class='form-control' id='toLogin' placeholder='Account'>\n");
            printf("        </div>\n");
            printf("        <div class='form-group'>\n");
            printf("          <label for='toAmount'>Amount</label>\n");
            printf("          <input type='number' value='' min='0' name='amount' class='form-control' id='toAmount' placeholder='Up to %lu₽'>\n", value);
            printf("        </div>\n");
            printf("        <input type='hidden' value='%s' name='login'><br>\n", login);
            printf("      </div>\n");
            printf("      <div class='modal-footer'>\n");
            printf("        <button type='button' class='btn btn-default' data-dismiss='modal'>Close</button>\n");
            printf("        <input type='submit' class='btn btn-primary' value='Execute'>\n");
            printf("      </div>\n");
            printf("      </form>\n");
            printf("    </div>\n");
            printf("  </div>\n");
            printf("</div>\n");
            printf("      </tr>\n");
        }

        printf("  </tbody>\n");
        printf("  </table>\n");

    }
    printf("         <div class='extra-space-l'></div>\n");
    printf("         <form class='sparser-form form-inline' action='add_money.cgi'>\n");
    printf("         <input type='hidden' value='%s' name='login'><br>\n", login);
    printf("         <legend><h5>Add money to the account (this is free and always will be):</h5></legend>\n");
    printf("         <div class='form-group'>\n");
    printf("         <label for='account'>Account:</label>\n");
    printf("         <input class='form-control' id='account' value='' name='account' placeholder='Enter account'>\n");
    printf("         </div>\n");
    printf("         <div class='form-group'>\n");
    printf("         <label for='amount'>Amount:</label>\n");
    printf("         <input type='number' min='0' class='form-control' id='amount' value='' name='amount' placeholder='Enter amount'>\n");
    printf("         </div>\n");
    printf("         <button type='submit' class='btn btn-success'>Add</button>\n");
    printf("         </form>\n");
    printf("         <div class='extra-space-l'></div>\n");
}

int main() {
    int ret;
    print_header(1);
    ret = gen_page();
    print_footer();

    return ret;
}
