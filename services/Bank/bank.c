#include <stdlib.h>
#include <stdio.h>
#include <string.h>

#include <sys/mman.h>

#include "sha256.h"

#define MAX_ITEMS_IN_BUCKET 	(2)
#define BUFLEN			        (1024 * 1024)
#define MAX_KEYS 		        (256)
#define TREE_MAX_NODES 	        (4096)
#define MAX_KEY_LEN		        (64)
#define BUFF_ADDR 		        ((char *) 0x000000dead000000)

long get_hash(unsigned char *buf);
// num requests to win = 16

// usernames(64 chars max) * 256, tree nodes * (2 ** 12), functions(1K)

struct tree_node {
	long hash;
    char* keys[MAX_ITEMS_IN_BUCKET];
    long values[MAX_ITEMS_IN_BUCKET];
};

struct tree {
	void (*set) (unsigned char* key, int value);
	int (*get) (unsigned char* key);
};


void* set(unsigned char* key, int value) 
// __attribute__((optnone)) 
{
  	unsigned char* mem_start;
  	int i;
	
  	// Get tree start address
  	asm volatile("callq 1f;"
  		"1: popq %0;"
  		"andq $0xffffffffff000000, %0;" : "=r" (mem_start) :: "cc"
	);

  	// mem_start = 0xdead000000;

	long hash;


	// Call get_hash by far address 
	asm volatile("mov %1, %%rdi;"
		"leaq get_hash, %%rax;"
		"callq *%%rax;"
		"movq %%rax, %0;"
		:"=m" (hash): "m" (key) : 
		"%rax", "%rbx", "%rcx", "%rdx", "%rsi", "%rdi",
		"%r8", "%r9", "%r10", "%r11", "%r12", "%r13", "%r14", "%r15", 
		"memory", "cc");


	// return hash;
	// get_hash(key);

	const unsigned char* TREE_NODES_ADDR = mem_start + MAX_KEY_LEN * MAX_KEYS;

	struct tree_node* curr_node = (struct tree_node*) TREE_NODES_ADDR;
	long curr_node_offset = 0;
	
	while(curr_node->hash != 0) {
		curr_node_offset = curr_node_offset * 2;
		if(hash < curr_node->hash) {
			curr_node_offset += 1;
		} else if (hash > curr_node->hash) {
			curr_node_offset += 2;
		} else {
			break;
		}
		curr_node = (struct tree_node*) TREE_NODES_ADDR + curr_node_offset;
		// printf("%d %ld %p\n", curr_node_offset, curr_node->hash, curr_node);
	}

	curr_node->hash = hash;

	// asm volatile("int $3;");

	// return bucket_ptr;

	for (i = 0; i < MAX_ITEMS_IN_BUCKET; i+=1) {
		if(!curr_node->keys[i]) {
			break;
		}

		int j;
		for (j = 0; key[j] && curr_node->keys[i][j] && key[j] == curr_node->keys[i][j]; j++) {}
		if(key[j] == curr_node->keys[i][j] == 0) {
			break;  // equals
		}
	}

	curr_node->values[i] = value;

	// place the key
	if(!curr_node->keys[i]) {
		// find a place for the key
		unsigned char *key_offset = 0;
		int j;
		for (j = 0; j < MAX_KEYS * MAX_KEY_LEN; j += MAX_KEY_LEN) {
			key_offset = mem_start + j;
			if(*key_offset == 0) {
				break;
			}
		}
		// copy new key to founded place
		for (j = 0; j < MAX_KEY_LEN - 1 && key[j]; j++) {
			key_offset[j] = key[j];
		}
		key_offset[j] = 0;

		curr_node->keys[i] = key_offset;
	}

	return curr_node;
}

void* get(unsigned char* key) {
  	unsigned char* mem_start;
	int i;
  	

  	// Get tree start address
  	asm volatile("callq 1f;"
  		"1: popq %0;"
  		"andq $0xffffffffff000000, %0;" : "=r" (mem_start) :: "cc"
	);

  	// mem_start = 0xdead000000;

	long hash;

	// Call get_hash by far address 
	asm volatile("mov %1, %%rdi;"
		"leaq get_hash, %%rax;"
		"callq *%%rax;"
		"movq %%rax, %0;"
		:"=m" (hash): "m" (key) : 
		"%rax", "%rbx", "%rcx", "%rdx", "%rsi", "%rdi",
		"%r8", "%r9", "%r10", "%r11", "%r12", "%r13", "%r14", "%r15", 
		"memory", "cc");
	// hash = 0x657d4c8881d0869f;

	const unsigned char* TREE_NODES_ADDR = mem_start + MAX_KEY_LEN * MAX_KEYS;

	struct tree_node* curr_node = (struct tree_node*) TREE_NODES_ADDR;
	long curr_node_offset = 0;

	while(curr_node->hash != 0) {
		curr_node_offset = curr_node_offset * 2;
		if(hash < curr_node->hash) {
			curr_node_offset += 1;
		} else if (hash > curr_node->hash) {
			curr_node_offset += 2;
		} else {
			break;
		}
		curr_node = (struct tree_node*) TREE_NODES_ADDR + curr_node_offset;
		// printf("%d %ld %p\n", curr_node_offset, curr_node->hash, curr_node);
	}

	// return curr_node; // debug

	if(curr_node->hash == 0) {
		return 0;
	}

	for (i = 0; i < MAX_ITEMS_IN_BUCKET; i+=1) {
		if(!curr_node->keys[i]) {
			return 0;
		}

		int j;
		for (j = 0; key[j] && curr_node->keys[i][j] && key[j] == curr_node->keys[i][j]; j++) {}
		if(key[j] == 0 && curr_node->keys[i][j] == 0) {
			return curr_node->values[i];
		}
	}
	return 0;  // Not found
}

void end() {}



void init_structs() {
	// usernames = BUFF_ADDR
	// bucket_arrays = BUFF_ADDR + 32 * 256 + size

	const char* TREE_NODES_ADDR = BUFF_ADDR + MAX_KEY_LEN * MAX_KEYS;
	const char* FUNCTION_SET_ADDR = TREE_NODES_ADDR + TREE_MAX_NODES * sizeof(struct tree_node);
	const char* FUNCTION_GET_ADDR = FUNCTION_SET_ADDR + 0x2000;

	memcpy((void *)FUNCTION_SET_ADDR,  (void*) set, (void *)get - (void *)set);
	memcpy((void *)FUNCTION_GET_ADDR,  (void*) get, (void *)end - (void *)get);


	printf("%p %p %p %p\n", BUFF_ADDR, TREE_NODES_ADDR, FUNCTION_SET_ADDR, FUNCTION_GET_ADDR);
	
	void* a = ((void *(*)(char* key, int value))FUNCTION_SET_ADDR)("test", 1000);
	// void* a = set("test", 1000);
	printf("%p\n", a);

	// void* b = ((void *(*)(char* key))FUNCTION_GET_ADDR)("test");
	// void* b = get("test");
	// printf("%p\n", b);
	// void* b = get("test");

	// printf("%p\n", ((void *(*)(char* key, int value))set)("testt", 2000));
	printf("%p\n", ((void *(*)(char* key, int value))FUNCTION_SET_ADDR)("testt", 2000));
	printf("%p\n", ((void *(*)(char* key))FUNCTION_GET_ADDR)("test"));
	printf("%p\n", ((void *(*)(char* key))FUNCTION_GET_ADDR)("testt"));
	printf("%p\n", ((void *(*)(char* key))FUNCTION_GET_ADDR)("test"));

}


long get_hash(unsigned char *buf)
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

	unsigned char* buf = (unsigned char*) mmap((void *)0x000000dead000000, 1024 * 1024,
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
