# make is smart, it knows how to make *.o from *.c

CFLAGS+=-Os
CFLAGS+=-g
CFLAGS+=-fPIC
# CFLAGS+=--std c11

CC=gcc

gen_empty_dict: gen_empty_dict.o
	$(CC) $(CFLAGS) $^ -o gen_empty_dict

clean:
	rm -f gen_empty_dict.o sha256.o
