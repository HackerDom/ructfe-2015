CFLAGS+=-O3
CFLAGS+=-g
CFLAGS+=-fPIC
CFLAGS+=-shared

CC=gcc

libdict.so: dict.c sha1.o
	$(CC) $(CFLAGS) dict.c sha1.o -o libdict.so
	
clean:
	rm -f libdict.so sha1.o
