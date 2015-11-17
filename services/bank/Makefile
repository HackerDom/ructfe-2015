all:
	$(MAKE) -C src
	$(MAKE) -C src/bank_httpd

	mkdir -p dict
	cp src/dict/libdict.so dict/
	cp src/bank_httpd/bank_httpd ./
	cp src/account.cgi ./
	cp src/add_money.cgi ./
	cp src/bank.cgi ./
	cp src/transfer_money.cgi ./

clean:
	$(MAKE) -C src clean
	$(MAKE) -C src/bank_httpd clean

