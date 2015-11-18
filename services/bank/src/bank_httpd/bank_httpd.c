#include "mongoose.h"

int main(void) {
  struct mg_server *server = mg_create_server(NULL, NULL);
  mg_set_option(server, "listening_port", "127.0.0.1:3255");
  mg_set_option(server, "document_root", ".");
  mg_set_option(server, "index_files", "bank.cgi");

  printf("Starting on port %s\n", mg_get_option(server, "listening_port"));
  for (;;) mg_poll_server(server, 1000);
  mg_destroy_server(&server);

  return 0;
}
