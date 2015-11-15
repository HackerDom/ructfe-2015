#include <stdlib.h>
#include <stdio.h>
#include <string.h>

int main() {
    int ret;

    char *body = "<form action=account.cgi>"
    "Username: <input value='name' name='login'>"
    "<input type='submit'>"
    "</form>";

    printf("Content-type: text/html\n\n");
    printf("<head><title>Bank</title><head>\n");
    printf("<body>%s</body>", body);

    return 0;
}
