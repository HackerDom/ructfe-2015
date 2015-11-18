CFLAGS+=-Os
CFLAGS+=-g
CFLAGS+=-Ldict
CFLAGS+=-ldict

CC=gcc

all: validator

validator: libdict.so
	$(CC) validator.c -o validator $(CFLAGS)

libdict.so:
	$(MAKE) -C dict

clean:
	$(MAKE) -C dict clean	
	rm -f libdict.so validator validator.o