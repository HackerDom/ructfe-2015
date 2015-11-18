#include <sys/types.h>
#include <sys/stat.h>
#include <fcntl.h>

#include <stdlib.h>
#include <stdio.h>
#include <string.h>

#include <sys/mman.h>

#include "sha256.c"

#define MAX_ITEMS_IN_BUCKET 	(2)
#define BUFLEN			        (512 * 1024)
#define MAX_KEYS 		        (64)
#define TREE_MAX_NODES 	        (16384)
#define MAX_KEY_LEN		        (64)
#define BUFF_ADDR               ((char *) 0x000000dead000000)
#define SECRET_OFFSET           ((int) 0x71835)
#define SECRET_OFFSET2	        ((int) 0x718b4)

// long get_hash(unsigned char *buf);
long get_hash(unsigned char *buf);

// num requests to win = 16

// usernames(64 chars max) * 256, tree nodes * (2 ** 12), functions(1K)

struct tree_node {
	unsigned long hash;
    unsigned short key_offsets[MAX_ITEMS_IN_BUCKET];
    unsigned long values[MAX_ITEMS_IN_BUCKET];
} __attribute__((packed));


void set(unsigned char* key, unsigned long value) 
// __attribute__((optnone)) 
{
  	unsigned char* mem_start;
    long hash;
    int i;

    // Get tree start address
    asm volatile("leaq (%%rip), %0;"
        "andq $0xfffffffffff00000, %0;" : "=r" (mem_start) :: "cc"
    );

    long (*volatile get_hash_ptr)(unsigned char * key) = mem_start + SECRET_OFFSET;
    hash = get_hash_ptr(key);


  	// mem_start = 0xdead000000;

    const unsigned char* TREE_NODES_ADDR = mem_start + MAX_KEY_LEN * MAX_KEYS;

	struct tree_node* curr_node = (struct tree_node*) TREE_NODES_ADDR;
	long curr_node_offset = 0;
	
    while(curr_node->key_offsets[0] > 0 && curr_node->key_offsets[0] < MAX_KEYS * MAX_KEY_LEN && curr_node->hash != hash) {
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

unsigned long get(unsigned char* key) {
  	unsigned char* mem_start;
	long hash;
    int i;

    // Get tree start address
    asm volatile("leaq (%%rip), %0;"
        "andq $0xfffffffffff00000, %0;" : "=r" (mem_start) :: "cc"
    );

    // Call get_hash by far address 
    long (*volatile get_hash_ptr)(unsigned char * key) = mem_start + SECRET_OFFSET;
    hash = get_hash_ptr(key);

    // mem_start = 0xdead000000;

	const unsigned char* TREE_NODES_ADDR = mem_start + MAX_KEY_LEN * MAX_KEYS;

	struct tree_node* curr_node = (struct tree_node*) TREE_NODES_ADDR;
	long curr_node_offset = 0;

    while(curr_node->key_offsets[0] > 0 && curr_node->key_offsets[0] < MAX_KEYS * MAX_KEY_LEN && curr_node->hash != hash) {
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
    asm volatile("leaq (%%rip), %0;"
        "andq $0xfffffffffff00000, %0;" : "=r" (mem_start) :: "cc"
    );

    unsigned long* keys_cnt = (unsigned long*) mem_start;
    unsigned char* key_ptr = mem_start + (num + 1) * MAX_KEY_LEN;
    if(num >= *keys_cnt || key_ptr[0] == 0) {
        return 0;
    }
    return key_ptr;
}

unsigned long size() {
    unsigned char* mem_start;

    // Get tree start address
    asm volatile("leaq (%%rip), %0;"
        "andq $0xfffffffffff00000, %0;" : "=r" (mem_start) :: "cc"
    );

    unsigned long* keys_cnt = (unsigned long*) mem_start;
    return *keys_cnt;
}

unsigned long validate() {
    unsigned char* mem_start;
    long hash;

    // Get tree start address
    asm volatile("leaq (%%rip), %0;"
        "andq $0xfffffffffff00000, %0;" : "=r" (mem_start) :: "cc"
    );

    // Call get_hash by far address 
    long (*volatile get_hash_ptr)(unsigned char * key, int len) = mem_start + SECRET_OFFSET2;
    hash = get_hash_ptr(mem_start, MAX_KEYS * MAX_KEY_LEN + TREE_MAX_NODES * sizeof(struct tree_node));

    return hash;
}


void end() {}



void init_dict() {
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
    int FUNCTION_SIZE_SIZE = (void *)validate - (void *)size;
    const char* FUNCTION_VALIDATE_ADDR = FUNCTION_SIZE_ADDR + FUNCTION_SIZE_SIZE;
    int FUNCTION_VALIDATE_SIZE = (void *)end - (void *)validate;
    const char* FUNCTION_HASH_ADDR = FUNCTION_VALIDATE_ADDR + FUNCTION_VALIDATE_SIZE;
    int FUNCTION_HASH_SIZE = (void *)get_hash3 - (void *)sha256_transform;

	memcpy((void *)FUNCTION_SET_ADDR,  (void*) set, FUNCTION_SET_SIZE);
    memcpy((void *)FUNCTION_GET_ADDR,  (void*) get, FUNCTION_GET_SIZE);
    memcpy((void *)FUNCTION_KEY_AT_ADDR,  (void*) key_at, FUNCTION_KEY_AT_SIZE);
    memcpy((void *)FUNCTION_SIZE_ADDR,  (void*) size, FUNCTION_SIZE_SIZE);
    memcpy((void *)FUNCTION_VALIDATE_ADDR,  (void*) validate, FUNCTION_VALIDATE_SIZE);
	memcpy((void *)FUNCTION_HASH_ADDR,  (void*) sha256_transform, FUNCTION_HASH_SIZE);

    printf("%p\n", (char*) FUNCTION_HASH_ADDR + (int)(((void *)get_hash) - (void*) sha256_transform));
    printf("%p\n", (char*) FUNCTION_HASH_ADDR + (int)(((void *)get_hash2) - (void*) sha256_transform));
    printf("set = %p get = %p key_at = %p size = %p validate = %p\n", 
        FUNCTION_SET_ADDR - BUFF_ADDR, 
        FUNCTION_GET_ADDR - BUFF_ADDR, 
        FUNCTION_KEY_AT_ADDR - BUFF_ADDR, 
        FUNCTION_SIZE_ADDR - BUFF_ADDR, 
        FUNCTION_VALIDATE_ADDR - BUFF_ADDR);
    printf("set = %d get = %d key_at = %d size = %d validate = %d hash=%d\n", FUNCTION_SET_SIZE, FUNCTION_GET_SIZE, FUNCTION_KEY_AT_SIZE, FUNCTION_SIZE_SIZE, FUNCTION_VALIDATE_SIZE, FUNCTION_HASH_SIZE);
	
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

    struct timeval time; 
    gettimeofday(&time,NULL);

    srand((time.tv_sec * 1000) + (time.tv_usec / 1000));
    int r = rand();

    // for (i = 0; i < 32000; i += 1) {
    //     sprintf(buf, "testttq16%d%d", r, i);
    //     void* a = ((void *(*)(char* key, unsigned long value))FUNCTION_SET_ADDR)(buf, i * 2 + 1);
    //     if (a > max_addr) {
    //         max_addr = a;
    //     }
    // }

    printf("SUCESSFULL\n");

    for (i = 0; i < 32000; i += 1) {
        sprintf(buf, "testttq16%d%d", r, i);
        long a = ((unsigned long (*)(char* key))FUNCTION_GET_ADDR)(buf);
        if(a || i == 0) {
            printf("%lu\n", a);
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

    printf("validate %lu %p %p\n", ((long (*)()) FUNCTION_VALIDATE_ADDR)(), FUNCTION_VALIDATE_ADDR, FUNCTION_SIZE_ADDR);
}


int main() {
	int ret;

    int fd = open("empty_dict.dat", O_RDWR | O_CREAT | O_TRUNC, 0660);
    if (fd == -1) {
        printf("bad out file\n");
        return 1;
    }
    ftruncate(fd, BUFLEN);

	unsigned char* buf = (unsigned char*) mmap((void *)BUFF_ADDR, BUFLEN,
		PROT_EXEC | PROT_READ | PROT_WRITE, MAP_SHARED | MAP_FIXED,
		fd, 0);

	if(buf == (void *)-1) {
		return 1;
	}

	// Check for heap executableness
	buf[0] = '\xc3';
	((void(*)(void))buf)();
	buf[0] = 0;

	init_dict();

	printf("Bank service is started. Ready for clients\n");	

	// BYTE b[SHA256_BLOCK_SIZE];
    unsigned long (*get_hash_my)(unsigned char*) = (void *)BUFF_ADDR + SECRET_OFFSET;

    printf("hash: %lx\n", get_hash_my((unsigned char *)"a"));
	printf("hash: %lx\n", get_hash((unsigned char *)"a"));
	// int i;

	// for (i = 0; i < 256 / 8; i++) {
	// 	printf("%02x", (int) b[i]);
	// }
	// printf("\n");

	return 0;
}
