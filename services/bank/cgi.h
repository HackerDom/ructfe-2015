#ifndef CGI_H
#define CGI_H

// Simple cgi handle proc. Not handles percent chars
int get_param(char* param, char* buf, int maxlen);

#endif