#!/usr/bin/python3

import struct

f = open("empty_dict.dat", "rb")

data = f.read()

if len(data) % 8 != 0:
	print("Bad file, not x8")
	exit(1)


for i in range(0, len(data), 8):
	# if(data[i: i+8] != b"\x00" * 8):
		# print(data[i: i+8])
	data_piece = struct.unpack("<Q", data[i: i+8])[0]
	if data_piece == 0:
		continue
	print("nums[%d] = 0x%016x;" % (i // 8, data_piece), end="\n" if i//8 % 3 == 0 else " ")