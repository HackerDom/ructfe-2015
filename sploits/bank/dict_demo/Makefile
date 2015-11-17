CFLAGS+=-Os
CFLAGS+=-g
CFLAGS+=-Ldict
CFLAGS+=-ldict

CC=gcc

all: dict_demo

dict_demo: libdict.so
	$(CC) $(CFLAGS) dict_demo.c -o dict_demo

libdict.so:
	$(MAKE) -C dict

clean:
	$(MAKE) -C dict clean	
	rm -f libdict.so dict_demo dict_demo.o