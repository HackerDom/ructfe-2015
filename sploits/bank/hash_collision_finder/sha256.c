/*-
 * Copyright (c) 2001-2003 Allan Saddi <allan@saddi.com>
 * Copyright (c) 2012 Moinak Ghosh moinakg <at1> gm0il <dot> com
 * All rights reserved.
 *
 * Redistribution and use in source and binary forms, with or without
 * modification, are permitted provided that the following conditions
 * are met:
 * 1. Redistributions of source code must retain the above copyright
 *    notice, this list of conditions and the following disclaimer.
 * 2. Redistributions in binary form must reproduce the above copyright
 *    notice, this list of conditions and the following disclaimer in the
 *    documentation and/or other materials provided with the distribution.
 *
 * THIS SOFTWARE IS PROVIDED BY THE AUTHOR AND CONTRIBUTORS ``AS IS'' AND
 * ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
 * IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE
 * ARE DISCLAIMED.  IN NO EVENT SHALL THE AUTHOR OR CONTRIBUTORS BE LIABLE
 * FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL
 * DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS
 * OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION)
 * HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT
 * LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY
 * OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF
 * SUCH DAMAGE.
 */

/*
 * Define WORDS_BIGENDIAN if compiling on a big-endian architecture.
 */

#ifdef HAVE_CONFIG_H
#include <config.h>
#endif /* HAVE_CONFIG_H */

#include <inttypes.h>
#include <stdint.h>

#include <pthread.h>
#include <string.h>
#include <sha256.h>

#define htonll(x) ((((uint64_t)htonl(x)) << 32) + htonl((x) >> 32))

#define BYTESWAP(x) htonl(x)
#define BYTESWAP64(x) htonll(x)

typedef void (*update_func_ptr)(void *input_data, uint32_t digest[8], uint64_t num_blks);

static uint8_t padding[64] = {
  0x80, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
  0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
  0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
  0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
  0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
  0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
  0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
  0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00
};

static const uint32_t iv256[SHA256_HASH_WORDS] = {
  0x6a09e667L, 0xbb67ae85L, 0x3c6ef372L, 0xa54ff53aL,
  0x510e527fL, 0x9b05688cL, 0x1f83d9abL, 0x5be0cd19L
};

void SHA256_Init (SHA256_Context *sc)
{
	sc->hash[0] = iv256[0];
	sc->hash[1] = iv256[1];
	sc->hash[2] = iv256[2];
	sc->hash[3] = iv256[3];
	sc->hash[4] = iv256[4];
	sc->hash[5] = iv256[5];
	sc->hash[6] = iv256[6];
	sc->hash[7] = iv256[7];

	sc->totalLength = 0LL;
	sc->bufferLength = 0L;
}

void SHA256_Update (SHA256_Context *sc, void *vdata, size_t len)
{
	const uint8_t *data = vdata;
	uint32_t bufferBytesLeft;
	size_t bytesToCopy;
	int rem;
	
	if (sc->bufferLength) {
		do {
			bufferBytesLeft = 64L - sc->bufferLength;
			bytesToCopy = bufferBytesLeft;
			if (bytesToCopy > len)
				bytesToCopy = len;
			
			memcpy (&sc->buffer.bytes[sc->bufferLength], data, bytesToCopy);
			sc->totalLength += bytesToCopy * 8L;
			sc->bufferLength += bytesToCopy;
			data += bytesToCopy;
			len -= bytesToCopy;
			
			if (sc->bufferLength == 64L) {
				sc->blocks = 1;
				sha256_avx(sc->buffer.words, sc->hash, sc->blocks);
				sc->bufferLength = 0L;
			} else {
				return;
			}
		} while (len > 0 && len <= 64L);
		if (!len) return;
	}
	
	sc->blocks = len >> 6;
	rem = len - (sc->blocks << 6);
	len = sc->blocks << 6;
	sc->totalLength += rem * 8L;
	
	if (len) {
		sc->totalLength += len * 8L;
		sha256_avx((uint32_t *)data, sc->hash, sc->blocks);
	}
	if (rem) {
		memcpy (&sc->buffer.bytes[0], data + len, rem);
		sc->bufferLength = rem;
	}
}

void SHA256_Final (SHA256_Context *sc, uint8_t hash[SHA256_HASH_SIZE])
{
	uint32_t bytesToPad;
	uint64_t lengthPad;
	int i;
	
	bytesToPad = 120L - sc->bufferLength;
	if (bytesToPad > 64L)
		bytesToPad -= 64L;
	
	lengthPad = BYTESWAP64(sc->totalLength);
	
	SHA256_Update (sc, padding, bytesToPad);
	SHA256_Update (sc, &lengthPad, 8L);
	
	if (hash) {
		for (i = 0; i < SHA256_HASH_WORDS; i++) {
			hash[0] = (uint8_t) (sc->hash[i] >> 24);
			hash[1] = (uint8_t) (sc->hash[i] >> 16);
			hash[2] = (uint8_t) (sc->hash[i] >> 8);
			hash[3] = (uint8_t) sc->hash[i];
			hash += 4;
		}
	}
}
