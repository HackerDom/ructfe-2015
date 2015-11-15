CFLAGS+=-Os
CFLAGS+=-g
# CFLAGS+=-fPIC
CFLAGS+=-Ldict
CFLAGS+=-ldict

CC=gcc

all: bank.cgi account.cgi add_money.cgi transfer_money.cgi

bank.cgi: bank.o libdict.so cgi.o common.o
	$(CC) $(CFLAGS) bank.o cgi.o common.o -o bank.cgi

account.cgi: account.o libdict.so cgi.o common.o
	$(CC) $(CFLAGS) account.o cgi.o common.o -o account.cgi

add_money.cgi: add_money.o libdict.so cgi.o common.o
	$(CC) $(CFLAGS) add_money.o cgi.o common.o -o add_money.cgi

transfer_money.cgi: transfer_money.o libdict.so cgi.o common.o
	$(CC) $(CFLAGS) transfer_money.o cgi.o common.o -o transfer_money.cgi

libdict.so:
	$(MAKE) -C dict

clean:
	$(MAKE) -C dict clean	
	rm -f libdict.so bank.cgi account.cgi bank.o account.o cgi.o common.o
