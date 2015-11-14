# make is smart, it knows how to make *.o from *.c

CFLAGS+=-O0
CFLAGS+=-g 
# CFLAGS+=--std c11

CC=gcc

bank: bank.o sha256.o
	$(CC) $(CFLAGS) $^ -o bank 
	execstack -s ./bank

clean:
	rm -f bank.o sha256.o
