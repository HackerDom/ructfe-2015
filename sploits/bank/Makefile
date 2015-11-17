CFLAGS+=-O3
CFLAGS+=-g
CFLAGS+=-Ldict
CFLAGS+=-ldict

CC=gcc

all: spl seq

spl: libdict.so spl.o sha256.o
	$(CC) $(CFLAGS) spl.o sha256.o -o spl

seq: libdict.so seq.o sha256.o
	$(CC) $(CFLAGS) seq.o sha256.o -o seq

libdict.so:
	$(MAKE) -C dict

clean:
	$(MAKE) -C dict clean	
	rm -f libdict.so spl.o 10/9f4b3c50d7b0df729d299bc6f8e9ef9066971f

#a9/4a8fe5ccb19ba61c4c0873d391e987982fbbd3
