CFLAGS+=-Os
CFLAGS+=-g
CFLAGS+=-fPIC
CFLAGS+=-Ldict
CFLAGS+=-ldict
# CFLAGS+=--std c11

CC=gcc

bank: bank.o libdict.so
	$(CC) $(CFLAGS) bank.o -o bank 

libdict.so:
	$(MAKE) -C dict

clean:
	$(MAKE) -C dict clean	
	rm -f libdict.so bank bank/bank.o sha256.o
