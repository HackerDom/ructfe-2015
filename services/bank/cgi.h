#ifndef CGI_H
#define CGI_H

// Code is from https://www.eskimo.com/~scs/cclass/handouts/cgi.html

// Simple cgi handle proc. Not handles percent chars
char* cgigetval(char* fieldname);
// int get_param(char* param, char* buf, int maxlen);

#endif