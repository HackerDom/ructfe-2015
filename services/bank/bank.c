#include <stdlib.h>
#include <stdio.h>
#include <string.h>

#include "common.h"

int main() {
    print_header();

    char *body = "              <h1>The Bank</h1>\n"
                 "              <div class='well'>\n"
                 "                   We love opensource and safety. We do not take any responsibility if you login is stolen, please keep it safe.\n"
                 "               </div>\n"
                 "               <div class='extra-space-l'></div>\n"
                 "               <form class='sparser-form' action='account.cgi'>"
                 "               <div class='input-group input-group-lg'>\n"
                 "                  <input class='form-control' id='name' value='' name='login' placeholder='Name'>\n"
                 "                  <span class='input-group-btn'>\n"
                 "                  <input class='btn btn-default btn-lg' value='Login!' role='button' type='submit'>\n"
                 "                  </span>\n"
                 "               </div>\n"
                 "               </form>\n";

    printf("%s", body);

    print_footer();

    return 0;
}
