#include <stdlib.h>
#include <stdio.h>
#include <string.h>

#include <sys/mman.h>

#include "sha256.h"

#define MAX_ITEMS_IN_BUCKET 	(2)
#define BUFLEN			        (512 * 1024)
#define MAX_KEYS 		        (64)
#define TREE_MAX_NODES 	        (16384)
#define MAX_KEY_LEN		        (64)
#define BUFF_ADDR 		        ((char *) 0x000000dead000000)

// long get_hash(unsigned char *buf);
long get_hash(unsigned char *buf);

// num requests to win = 16

// usernames(64 chars max) * 256, tree nodes * (2 ** 12), functions(1K)

struct tree_node {
	unsigned long hash;
    unsigned short key_offsets[MAX_ITEMS_IN_BUCKET];
    unsigned long values[MAX_ITEMS_IN_BUCKET];
} __attribute__((packed));

struct tree {
	void (*set) (unsigned char* key, int value);
	int (*get) (unsigned char* key);
};


void set(unsigned char* key, int value) 
// __attribute__((optnone)) 
{
  	unsigned char* mem_start;
    long hash;
    int i;

    long (*volatile get_hash_ptr)(unsigned char * key) = get_hash;
    hash = get_hash_ptr(key);

    // Get tree start address
    asm volatile("callq 1f;"
        "1: popq %0;"
        "andq $0xffffffffff000000, %0;" : "=r" (mem_start) :: "cc"
    );

  	// mem_start = 0xdead000000;

    const unsigned char* TREE_NODES_ADDR = mem_start + MAX_KEY_LEN * MAX_KEYS;

	struct tree_node* curr_node = (struct tree_node*) TREE_NODES_ADDR;
	long curr_node_offset = 0;
	
    while(curr_node->hash != 0 && curr_node->hash != hash) {
        if(hash < curr_node->hash) {
            curr_node_offset = curr_node_offset * 2 + 1;
        } else if (hash > curr_node->hash) {
            curr_node_offset = curr_node_offset * 2 + 2;
        }
        curr_node = (struct tree_node*) TREE_NODES_ADDR + curr_node_offset;
    }

	for (i = 0; i < MAX_ITEMS_IN_BUCKET; i+=1) {
        unsigned char* key_ptr = mem_start + curr_node->key_offsets[i];

		if(!curr_node->key_offsets[i]) {
			break;
		}

		int j;
		for (j = 0; key[j] && key_ptr[j] && key[j] == key_ptr[j]; j++) {}
		if(key[j] == 0 && key_ptr[j] == 0) {
			break;  // equals
		}
	}

	// place the key
	if(!curr_node->key_offsets[i]) {
        unsigned long* keys_cnt = (unsigned long*) mem_start;
		unsigned char *key_offset = (*keys_cnt + 1) * MAX_KEY_LEN + mem_start;

        if(*keys_cnt >= MAX_KEYS - 1) {
            return;  // too much items
        }

        // copy new key to free place
		int j;
		for (j = 0; j < MAX_KEY_LEN - 1 && key[j]; j++) {
			key_offset[j] = key[j];
		}

		curr_node->key_offsets[i] = key_offset - mem_start;
        *keys_cnt += 1;
	}

    curr_node->hash = hash;
    curr_node->values[i] = value;
}

long get(unsigned char* key) {
  	unsigned char* mem_start;
	long hash;
    int i;

    // Call get_hash by far address 
    long (*volatile get_hash_ptr)(unsigned char * key) = get_hash;
    hash = get_hash_ptr(key);

    // Get tree start address
    asm volatile("callq 1f;"
        "1: popq %0;"
        "andq $0xffffffffff000000, %0;" : "=r" (mem_start) :: "cc"
    );

    // mem_start = 0xdead000000;

	const unsigned char* TREE_NODES_ADDR = mem_start + MAX_KEY_LEN * MAX_KEYS;

	struct tree_node* curr_node = (struct tree_node*) TREE_NODES_ADDR;
	long curr_node_offset = 0;

    while(curr_node->hash != 0 && curr_node->hash != hash) {
        if(hash < curr_node->hash) {
            curr_node_offset = curr_node_offset * 2 + 1;
        } else if (hash > curr_node->hash) {
            curr_node_offset = curr_node_offset * 2 + 2;
        }
        curr_node = (struct tree_node*) TREE_NODES_ADDR + curr_node_offset;
    }

	if(curr_node->hash == 0) {
		return 0;
	}

	for (i = 0; i < MAX_ITEMS_IN_BUCKET; i += 1) {
        unsigned char* key_ptr = mem_start + curr_node->key_offsets[i];
		if(!curr_node->key_offsets[i]) {
			return 0;
		}

		int j;
		for (j = 0; key[j] && key_ptr[j] && key[j] == key_ptr[j]; j++) {}
		if(key[j] == 0 && key_ptr[j] == 0) {
			return curr_node->values[i];
		}
	}
	return 0;  // Not found
}

unsigned char* key_at(int num) {
    unsigned char* mem_start;

    // Get tree start address
    asm volatile("callq 1f;"
        "1: popq %0;"
        "andq $0xffffffffff000000, %0;" : "=r" (mem_start) :: "cc"
    );

    unsigned long* keys_cnt = (unsigned long*) mem_start;
    unsigned char* key_ptr = mem_start + (num + 1) * MAX_KEY_LEN;
    if(num >= *keys_cnt || key_ptr[0] == 0) {
        return 0;
    }
    return key_ptr;
}

long size() {
    unsigned char* mem_start;

    // Get tree start address
    asm volatile("callq 1f;"
        "1: popq %0;"
        "andq $0xffffffffff000000, %0;" : "=r" (mem_start) :: "cc"
    );

    unsigned long* keys_cnt = (unsigned long*) mem_start;
    return *keys_cnt;
}


void end() {}



void init_structs() {
	// usernames = BUFF_ADDR
	// bucket_arrays = BUFF_ADDR + 32 * 256 + size

	const char* TREE_NODES_ADDR = BUFF_ADDR + MAX_KEY_LEN * MAX_KEYS;
    const char* FUNCTION_SET_ADDR = TREE_NODES_ADDR + TREE_MAX_NODES * sizeof(struct tree_node);
    int FUNCTION_SET_SIZE = (void *)get - (void *)set;
    const char* FUNCTION_GET_ADDR = FUNCTION_SET_ADDR + FUNCTION_SET_SIZE;
    int FUNCTION_GET_SIZE = (void *)key_at - (void *)get;
    const char* FUNCTION_KEY_AT_ADDR = FUNCTION_GET_ADDR + FUNCTION_GET_SIZE;
    int FUNCTION_KEY_AT_SIZE = (void *)size - (void *)key_at;
    const char* FUNCTION_SIZE_ADDR = FUNCTION_KEY_AT_ADDR + FUNCTION_KEY_AT_SIZE;
	int FUNCTION_SIZE_SIZE = (void *)end - (void *)size;

	memcpy((void *)FUNCTION_SET_ADDR,  (void*) set, FUNCTION_SET_SIZE);
    memcpy((void *)FUNCTION_GET_ADDR,  (void*) get, FUNCTION_GET_SIZE);
    memcpy((void *)FUNCTION_KEY_AT_ADDR,  (void*) key_at, FUNCTION_KEY_AT_SIZE);
	memcpy((void *)FUNCTION_SIZE_ADDR,  (void*) size, FUNCTION_SIZE_SIZE);


    printf("%p %p %p %p\n", BUFF_ADDR, TREE_NODES_ADDR, FUNCTION_SET_ADDR, FUNCTION_GET_ADDR);
	printf("set = %d get = %d key_at = %d size = %d \n", FUNCTION_SET_SIZE, FUNCTION_GET_SIZE, FUNCTION_KEY_AT_SIZE, FUNCTION_SIZE_SIZE);
	
	// void* a = ((void *(*)(char* key, int value))FUNCTION_SET_ADDR)("test", 1000);
	// void* a = set("test", 1000);
	// printf("%p\n", a);

	// void* b = ((void *(*)(char* key))FUNCTION_GET_ADDR)("test");
	// void* b = get("test");
	// printf("%p\n", b);
	// void* b = get("test");

	// printf("%p\n", ((void *(*)(char* key, int value))set)("testt", 2000));
	// printf("%p\n", ((void *(*)(char* key, int value))FUNCTION_SET_ADDR)("testt", 2000));
	// printf("%p\n", ((void *(*)(char* key))FUNCTION_GET_ADDR)("test"));
	// printf("%p\n", ((void *(*)(char* key))FUNCTION_GET_ADDR)("testt"));
 //    printf("%p\n", ((void *(*)(char* key))FUNCTION_GET_ADDR)("test"));
 //    printf("%p\n", ((void *(*)(char* key))FUNCTION_GET_ADDR)("test"));
	// printf("%p\n", ((void *(*)(char* key))FUNCTION_GET_ADDR)("testt"));

 //    ((void *(*)(char* key, int value))FUNCTION_SET_ADDR)("test", 2000);
 //    printf("%p\n", ((void *(*)(char* key))FUNCTION_GET_ADDR)("test"));

    unsigned char buf[128] = {0};

    void* max_addr = 0;

    long prevhash = 0;

    int i;
    for (i = 0; i < 15000; i += 1) {
        // int j;
        // for (j = 0;; j += 1) {
            // sprintf(buf, "testttq16%d_%d", i, j);
            sprintf(buf, "testttq16%d", i);
            // if(get_hash(buf) > prevhash) {
                // prevhash = get_hash(buf);
                void* a = ((void *(*)(char* key, int value))FUNCTION_SET_ADDR)(buf, i * 2 + 1);
                // printf("%p\n", a);
                // fflush(stdout);
                if (a > max_addr) {
                    max_addr = a;
                }
                // break;
            // }
        // }
    }

    for (i = 0; i < 32000; i += 1) {
        sprintf(buf, "testttq16%d", i);
        long a = ((long (*)(char* key))FUNCTION_GET_ADDR)(buf);
        if(a || i == 0) {
            printf("%lu ", a);
        }
        // fflush(stdout);
    }

    printf("%d, %d\n", (max_addr - (void*) TREE_NODES_ADDR) / sizeof(struct tree_node), sizeof(struct tree_node));
    // void* a = ((void *(*)(char* key, int value))FUNCTION_SET_ADDR)("test", 1000);

    printf("%lu\n", ((long (*)()) FUNCTION_SIZE_ADDR)());

    for (i = 0; i < ((long (*)()) FUNCTION_SIZE_ADDR)() + 1; i ++) {
        unsigned char *c = ((unsigned char *(*)(int i))FUNCTION_KEY_AT_ADDR)(i);
        if(c) {
            printf("i = %d key = %s\n", i, c);
        } else {
            printf("i = %d key = <nil>\n", i);
        }

    }


}


long __attribute__ ((noinline)) get_hash(unsigned char *buf)
// __attribute__((optnone)) 
{
	int len = strlen((char *) buf);
	// return 123;

	BYTE b[SHA256_BLOCK_SIZE];

	SHA256_CTX ctx;
	sha256_init(&ctx);
	sha256_update(&ctx, buf, len);
	sha256_final(&ctx, b);

	long hash = *((long *) b);
	return hash;
}

int main() {
	int ret;

	unsigned char* buf = (unsigned char*) mmap((void *)0x000000dead000000, BUFLEN,
		PROT_EXEC | PROT_READ | PROT_WRITE, MAP_SHARED | MAP_ANONYMOUS | MAP_FIXED,
		0, 0);

	if(buf == (void *)-1) {
		return 1;
	}

	// Check for heap executableness
	buf[0] = '\xc3';
	((void(*)(void))buf)();
	buf[0] = 0;

	init_structs();

	printf("Bank service is started. Ready for clients\n");	

	// BYTE b[SHA256_BLOCK_SIZE];

	printf("hash: %lu\n", get_hash((unsigned char *)"test"));
	// int i;

	// for (i = 0; i < 256 / 8; i++) {
	// 	printf("%02x", (int) b[i]);
	// }
	// printf("\n");

	return 0;
}
