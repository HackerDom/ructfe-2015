#ifndef DICT_H
#define DICT_H

struct dict {
    void (*set) (unsigned char* key, int value);
    long (*get) (unsigned char* key);
    unsigned char* (*key_at) (int num);
    long (*size) ();
    long (*validate) ();
};

int new_dict(char* dict_name, struct dict* t);

#endif