/*********************************************************************
* Filename:   sha256.c
* Author:     Brad Conte (brad AT bradconte.com)
* Copyright:
* Disclaimer: This code is presented "as is" without any guarantees.
* Details:    Implementation of the SHA-256 hashing algorithm.
              SHA-256 is one of the three algorithms in the SHA2
              specification. The others, SHA-384 and SHA-512, are not
              offered in this implementation.
              Algorithm specification can be found here:
               * http://csrc.nist.gov/publications/fips/fips180-2/fips180-2withchangenotice.pdf
              This implementation uses little endian byte order.
*********************************************************************/

/*************************** HEADER FILES ***************************/
#include <stdlib.h>
#include <memory.h>
#include "sha256.h"

/****************************** MACROS ******************************/
#define ROTLEFT(a,b) (((a) << (b)) | ((a) >> (32-(b))))
#define ROTRIGHT(a,b) (((a) >> (b)) | ((a) << (32-(b))))

#define CH(x,y,z) (((x) & (y)) ^ (~(x) & (z)))
#define MAJ(x,y,z) (((x) & (y)) ^ ((x) & (z)) ^ ((y) & (z)))
#define EP0(x) (ROTRIGHT(x,2) ^ ROTRIGHT(x,13) ^ ROTRIGHT(x,22))
#define EP1(x) (ROTRIGHT(x,6) ^ ROTRIGHT(x,11) ^ ROTRIGHT(x,25))
#define SIG0(x) (ROTRIGHT(x,7) ^ ROTRIGHT(x,18) ^ ((x) >> 3))
#define SIG1(x) (ROTRIGHT(x,17) ^ ROTRIGHT(x,19) ^ ((x) >> 10))

/**************************** VARIABLES *****************************/

/*********************** FUNCTION DEFINITIONS ***********************/
// hot attribute is a hack to enforce function order
void __attribute__ ((hot)) sha256_transform(SHA256_CTX *ctx, const BYTE data[])
{
	WORD a, b, c, d, e, f, g, h, i, j, t1, t2, m[64];

	WORD k[64];
	*((unsigned long*) &k[0]) = 0x71374491428a2f98;
	*((unsigned long*) &k[2]) = 0xe9b5dba5b5c0fbcf;
	*((unsigned long*) &k[4]) = 0x59f111f13956c25b;
	*((unsigned long*) &k[6]) = 0xab1c5ed5923f82a4;
	*((unsigned long*) &k[8]) = 0x12835b01d807aa98;
	*((unsigned long*) &k[10]) = 0x550c7dc3243185be;
	*((unsigned long*) &k[12]) = 0x80deb1fe72be5d74;
	*((unsigned long*) &k[14]) = 0xc19bf1749bdc06a7;
	*((unsigned long*) &k[16]) = 0xefbe4786e49b69c1;
	*((unsigned long*) &k[18]) = 0x240ca1cc0fc19dc6;
	*((unsigned long*) &k[20]) = 0x4a7484aa2de92c6f;
	*((unsigned long*) &k[22]) = 0x76f988da5cb0a9dc;
	*((unsigned long*) &k[24]) = 0xa831c66d983e5152;
	*((unsigned long*) &k[26]) = 0xbf597fc7b00327c8;
	*((unsigned long*) &k[28]) = 0xd5a79147c6e00bf3;
	*((unsigned long*) &k[30]) = 0x1429296706ca6351;
	*((unsigned long*) &k[32]) = 0x2e1b213827b70a85;
	*((unsigned long*) &k[34]) = 0x53380d134d2c6dfc;
	*((unsigned long*) &k[36]) = 0x766a0abb650a7354;
	*((unsigned long*) &k[38]) = 0x92722c8581c2c92e;
	*((unsigned long*) &k[40]) = 0xa81a664ba2bfe8a1;
	*((unsigned long*) &k[42]) = 0xc76c51a3c24b8b70;
	*((unsigned long*) &k[44]) = 0xd6990624d192e819;
	*((unsigned long*) &k[46]) = 0x106aa070f40e3585;
	*((unsigned long*) &k[48]) = 0x1e376c0819a4c116;
	*((unsigned long*) &k[50]) = 0x34b0bcb52748774c;
	*((unsigned long*) &k[52]) = 0x4ed8aa4a391c0cb3;
	*((unsigned long*) &k[54]) = 0x682e6ff35b9cca4f;
	*((unsigned long*) &k[56]) = 0x78a5636f748f82ee;
	*((unsigned long*) &k[58]) = 0x8cc7020884c87814;
	*((unsigned long*) &k[60]) = 0xa4506ceb90befffa;
	*((unsigned long*) &k[62]) = 0xc67178f2bef9a3f7;

	//4f5

	for (i = 0, j = 0; i < 16; ++i, j += 4)
		m[i] = (data[j] << 24) | (data[j + 1] << 16) | (data[j + 2] << 8) | (data[j + 3]);
	for ( ; i < 64; ++i)
		m[i] = SIG1(m[i - 2]) + m[i - 7] + SIG0(m[i - 15]) + m[i - 16];

	a = ctx->state[0];
	b = ctx->state[1];
	c = ctx->state[2];
	d = ctx->state[3];
	e = ctx->state[4];
	f = ctx->state[5];
	g = ctx->state[6];
	h = ctx->state[7];

	for (i = 0; i < 64; ++i) {
		t1 = h + EP1(e) + CH(e,f,g) + k[i] + m[i];
		t2 = EP0(a) + MAJ(a,b,c);
		h = g;
		g = f;
		f = e;
		e = d + t1;
		d = c;
		c = b;
		b = a;
		a = t1 + t2;
	}

	ctx->state[0] += a;
	ctx->state[1] += b;
	ctx->state[2] += c;
	ctx->state[3] += d;
	ctx->state[4] += e;
	ctx->state[5] += f;
	ctx->state[6] += g;
	ctx->state[7] += h;
}

void __attribute__ ((hot)) sha256_init(SHA256_CTX *ctx)
{
	ctx->datalen = 0;
	ctx->bitlen = 0;
	ctx->state[0] = 0x6a09e667;
	ctx->state[1] = 0xbb67ae85;
	ctx->state[2] = 0x3c6ef372;
	ctx->state[3] = 0xa54ff53a;
	ctx->state[4] = 0x510e527f;
	ctx->state[5] = 0x9b05688c;
	ctx->state[6] = 0x1f83d9ab;
	ctx->state[7] = 0x5be0cd19;
}

void __attribute__ ((hot)) sha256_update(SHA256_CTX *ctx, const BYTE data[], size_t len)
{
	WORD i;

	for (i = 0; i < len; ++i) {
		ctx->data[ctx->datalen] = data[i];
		ctx->datalen++;
		if (ctx->datalen == 64) {
			sha256_transform(ctx, ctx->data);
			ctx->bitlen += 512;
			ctx->datalen = 0;
		}
	}
}

void __attribute__ ((hot)) sha256_final(SHA256_CTX *ctx, BYTE hash[])
{
	WORD i;

	i = ctx->datalen;

	// Pad whatever data is left in the buffer.
	if (ctx->datalen < 56) {
		ctx->data[i++] = 0x80;
		while (i < 56)
			ctx->data[i++] = 0x00;
	}
	else {
		ctx->data[i++] = 0x80;
		while (i < 64)
			ctx->data[i++] = 0x00;
		sha256_transform(ctx, ctx->data);
		memset(ctx->data, 0, 56);
	}

	// Append to the padding the total message's length in bits and transform.
	ctx->bitlen += ctx->datalen * 8;
	ctx->data[63] = ctx->bitlen;
	ctx->data[62] = ctx->bitlen >> 8;
	ctx->data[61] = ctx->bitlen >> 16;
	ctx->data[60] = ctx->bitlen >> 24;
	ctx->data[59] = ctx->bitlen >> 32;
	ctx->data[58] = ctx->bitlen >> 40;
	ctx->data[57] = ctx->bitlen >> 48;
	ctx->data[56] = ctx->bitlen >> 56;
	sha256_transform(ctx, ctx->data);

	// Since this implementation uses little endian byte ordering and SHA uses big endian,
	// reverse all the bytes when copying the final state to the output hash.
	for (i = 0; i < 4; ++i) {
		hash[i]      = (ctx->state[0] >> (24 - i * 8)) & 0x000000ff;
		hash[i + 4]  = (ctx->state[1] >> (24 - i * 8)) & 0x000000ff;
		hash[i + 8]  = (ctx->state[2] >> (24 - i * 8)) & 0x000000ff;
		hash[i + 12] = (ctx->state[3] >> (24 - i * 8)) & 0x000000ff;
		hash[i + 16] = (ctx->state[4] >> (24 - i * 8)) & 0x000000ff;
		hash[i + 20] = (ctx->state[5] >> (24 - i * 8)) & 0x000000ff;
		hash[i + 24] = (ctx->state[6] >> (24 - i * 8)) & 0x000000ff;
		hash[i + 28] = (ctx->state[7] >> (24 - i * 8)) & 0x000000ff;
	}
}

long __attribute__ ((hot)) __attribute__ ((noinline)) get_hash(unsigned char *buf)
{
	int len = strlen((char *) buf);

	BYTE b[SHA256_BLOCK_SIZE];

	SHA256_CTX ctx;
	sha256_init(&ctx);
	sha256_update(&ctx, buf, len);
	sha256_final(&ctx, b);

	long hash = *((long *) b);
	return hash;
}

long __attribute__ ((hot)) __attribute__ ((noinline)) get_hash2(unsigned char *buf, int len)
{
	BYTE b[SHA256_BLOCK_SIZE];

	SHA256_CTX ctx;
	sha256_init(&ctx);
	sha256_update(&ctx, buf, len);
	sha256_final(&ctx, b);

	long hash = *((long *) b);
	return hash;
}

long __attribute__ ((hot)) __attribute__ ((noinline)) get_hash3(unsigned char *buf)
{
	int len = strlen((char *) buf);

	BYTE b[SHA256_BLOCK_SIZE];

	SHA256_CTX ctx;
	sha256_init(&ctx);
	sha256_update(&ctx, buf, len);
	sha256_final(&ctx, b);

	long hash = *((long *) b);
	return hash;
}

void hash_end() {}