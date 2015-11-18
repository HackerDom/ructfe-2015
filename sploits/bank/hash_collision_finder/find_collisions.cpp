#include <stdlib.h>
#include <stdio.h>
#include <string.h>

#include <boost/thread/thread.hpp>

#include "sha256.h"
#include "sparsehash/sparse_hash_set"

using google::sparse_hash_set;

const long MAX_ELEMENTS = 1600 * 1000 * 1000; // can be slightly bigger, than that num
const long BATCH_SIZE = 100;

sparse_hash_set<long> Set(MAX_ELEMENTS);
boost::mutex g_Mutex;
long glob_iter = 0;

void find_collisions(unsigned char c0)
{
	unsigned char b[256 / 8];
	unsigned char c[13];
	c[0] = c0;
	c[12] = 0;

	long iter = 0;

	long batch[BATCH_SIZE];

	for (c[1] = 'a'; c[1] < 'z'; c[1]++) 
	for (c[2] = 'a'; c[2] < 'z'; c[2]++) 
	for (c[3] = 'a'; c[3] < 'z'; c[3]++) 
	for (c[4] = 'a'; c[4] < 'z'; c[4]++) 
	for (c[5] = 'a'; c[5] < 'z'; c[5]++) 
	for (c[6] = 'a'; c[6] < 'z'; c[6]++) 
	for (c[7] = 'a'; c[7] < 'z'; c[7]++) 
	for (c[8] = 'a'; c[8] < 'z'; c[8]++) 
	for (c[9] = 'a'; c[9] < 'z'; c[9]++) 
	for (c[10] = 'a'; c[10] < 'z'; c[10]++) 
	for (c[11] = 'a'; c[11] < 'z'; c[11]++) 
	{
		SHA256_Context ctx;
		SHA256_Init(&ctx);
		SHA256_Update(&ctx, c, 12);
		SHA256_Final(&ctx, b);

		unsigned long hash = *((long *) b);

		batch[iter % BATCH_SIZE] = hash;

		if (iter % BATCH_SIZE == (BATCH_SIZE - 1)) {
			bool need_insert = glob_iter < MAX_ELEMENTS;

			if(need_insert) {
				g_Mutex.lock();

				for (int i = 0; i < BATCH_SIZE; i++) {
		            Set.insert(batch[i]);
				}
				glob_iter += BATCH_SIZE;

				g_Mutex.unlock();
			} else {
				for (int i = 0; i < BATCH_SIZE; i++) {
			   	    if (Set.count(batch[i]) == 1) {
				   		printf("found %lu %s\n", batch[i], c);
			    	}
				}
				glob_iter += BATCH_SIZE;
			}

			if (glob_iter % 1000000 == 0) {
				printf("glob_iter: %lu\n", glob_iter);
			}
		}

		//if (glob_iter >= 10000000) {
		// if (iter == 1) {
		//	return;
		//}

		iter += 1;
	}
}

int main() {
    int threads_num = 16;

    boost::thread_group threads;
    for (int i = 0; i < threads_num; i++) {
		threads.create_thread(boost::bind(find_collisions, 'a' + i));
    }
    threads.join_all();

    return 0;

	// for (i = 0; i < 256 / 8; i++) {
	// 	printf("%02x", (int) b[i]);
	// }
	// printf("\n");
}
