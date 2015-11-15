#include "cgi.h"

#include <stdlib.h>
#include <string.h>

// Code is from https://www.eskimo.com/~scs/cclass/handouts/cgi.html

static int xctod(int);

char *unescstring(char *src, int srclen, char *dest, int destsize)
{
    char *endp = src + srclen;
    char *srcp;
    char *destp = dest;
    int nwrote = 0;

    for(srcp = src; srcp < endp; srcp++) {
        if(nwrote > destsize)
            return NULL;
        if(*srcp == '+')
            *destp++ = ' ';
        else if(*srcp == '%')
            {
            *destp++ = 16 * xctod(*(srcp+1)) + xctod(*(srcp+2));
            srcp += 2;
            }
        else    *destp++ = *srcp;
        nwrote++;
    }

    *destp = '\0';

    return dest;
}

static int xctod(int c) {
    if(isdigit(c))
        return c - '0';
    else if(isupper(c))
        return c - 'A' + 10;
    else if(islower(c))
        return c - 'a' + 10;
    else    return 0;
}

char* cgigetval(char *fieldname) {
    int fnamelen;
    char *p, *p2, *p3;
    int len1, len2;
    static char *querystring = NULL;
    if(querystring == NULL) {
        querystring = getenv("QUERY_STRING");
        if(querystring == NULL)
            return NULL;
    }
    
    if(fieldname == NULL)
        return NULL;
    
    fnamelen = strlen(fieldname);
    
    for(p = querystring; *p != '\0';) {
        p2 = strchr(p, '=');
        p3 = strchr(p, '&');
        if(p3 != NULL)
            len2 = p3 - p;
        else    len2 = strlen(p);
    
        if(p2 == NULL || p3 != NULL && p2 > p3) {
            /* no = present in this field */
            p3 += len2;
            continue;
        }
        len1 = p2 - p;
    
        if(len1 == fnamelen && strncmp(fieldname, p, len1) == 0) {
            /* found it */
            int retlen = len2 - len1 - 1;
            char *retbuf = malloc(retlen + 1);
            if(retbuf == NULL)
                return NULL;
            unescstring(p2 + 1, retlen, retbuf, retlen+1);
            return retbuf;
        }
    
        p += len2;
        if(*p == '&')
            p++;
     }
    
    /* never found it */
    return NULL;
}
