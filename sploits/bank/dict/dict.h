#ifndef DICT_H
#define DICT_H

struct dict {
    void (*set) (unsigned char* key, unsigned long value);
    unsigned long (*get) (unsigned char* key);
    unsigned char* (*key_at) (int num);
    unsigned long (*size) ();
    unsigned long (*validate) ();
};

int new_dict(char* dict_name, struct dict* t);

#endif