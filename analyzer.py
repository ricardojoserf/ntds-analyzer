import os
import sys
import hashlib
import binascii
import argparse
import itertools as it
from collections import Counter 

top_most_common_hashes = 5
output_file = "credentials.txt"

def get_args():
	parser = argparse.ArgumentParser()
	parser.add_argument('-f', '--ntds', required=True, action='store', help='Username')
	parser.add_argument('-l', '--lm', required=False, action='store', help='Password')
	parser.add_argument('-n', '--ntlm', required=True, action='store', help='Option')
	my_args = parser.parse_args()
	return my_args


def get_permutations(passwd):
	lu_sequence = ((c.lower(), c.upper()) if c.isalpha() else c for c in passwd)
	return [''.join(x) for x in it.product(*lu_sequence)]


def get_passwd(uppercase_passwd, ntlm_hash):
	for p in get_permutations(uppercase_passwd):
		ntlm = binascii.hexlify(hashlib.new('md4', p.encode('utf-16le')).digest()).decode("utf-8")
		if ntlm == ntlm_hash:
			return ntlm,p
	return ntlm,""


def get_passwd_from_lm(uppercase_passwd, ntlm_hash):
	ntlm,cleartext_passwd = get_passwd(uppercase_passwd, ntlm_hash)
	return cleartext_passwd


def most_common_hashes(list_, dict_, keys, type_ = "", maxval = top_most_common_hashes): 
	print("\n[+] Top %s most common %s hashes " % (maxval, type_))
	occurence_count = Counter(list_) 
	for h in occurence_count.most_common(maxval):
		hash_ = h[0]
		times = h[1]
		password = dict_[hash_] if hash_ in keys else "[Password not cracked]"
		print("%s - %s times (Password: %s)"%(hash_, times, password))



def main():

	args = get_args()
	ntds_lines = open(args.ntds).read().splitlines()
	ntlm_lines = open(args.ntlm).read().splitlines()
	lm_lines = open(args.lm).read().splitlines() if args.lm is not None else None

	all_ntlm = []
	all_lm = []
	all_info = []
	ntlm_dict = {}
	lm_dict = {}


	# Create dictionary with NTLM cracked hashes
	for n in ntlm_lines:
		hash_ = n.split(":")[0]
		pass_ = n.split(":")[1]
		if hash_ != "31d6cfe0d16ae931b73c59d7e0c089c0":
			ntlm_dict[hash_] = pass_


	# Create dictionary with LM cracked hashes
	if lm_lines is not None:
		for l in lm_lines:
			hash_ = l.split(":")[0]
			pass_ = l.split(":")[1]
			if hash_ != "aad3b435b51404eeaad3b435b51404ee":
				lm_dict[hash_] = pass_

	# Create list with users info
	for l in ntds_lines:
		username = l.split(":")[0]
		lm_hash = l.split(":")[2]
		ntlm_hash = l.split(":")[3]
		if ntlm_hash != "31d6cfe0d16ae931b73c59d7e0c089c0":
			all_ntlm.append(ntlm_hash)
		if lm_hash != "aad3b435b51404eeaad3b435b51404ee":
			all_lm.append(lm_hash)
		password = ""
		if ntlm_hash in ntlm_dict.keys():
			password = ntlm_dict[ntlm_hash]
		elif lm_hash in lm_dict.keys():
			password = get_passwd_from_lm(lm_dict[lm_hash], ntlm_hash)
			ntlm_dict[ntlm_hash] = password
		else:
			password = ""
		all_info.append({"username":username, "ntlm_hash": ntlm_hash, "lm_hash": lm_hash, "password": password})

	print("\nTotal NTLM hashes:     %s"%(len(all_ntlm)))
	print("Different NTLM hashes: %s"%(len((set(all_ntlm)))))
	print("\nTotal LM hashes:       %s"%(len(all_lm)))
	print("Different LM hashes:   %s"%(len((set(all_lm)))))

	most_common_hashes(all_ntlm, ntlm_dict, ntlm_dict.keys(), "NTLM")
	if lm_lines is not None:
		most_common_hashes(all_lm, lm_dict, lm_dict.keys(), "LM")

	print("\n[+] Accounts with the same username and password")
	for a in all_info:
		if len(a.get("username").split('\\'))>=2:
			user = a.get("username").split('\\')[1]
		else:
			user = a.get("username")
		pwd_ = a.get("password")
		if user == pwd_:
			print("%s:%s" %(a.get("username"), pwd_))

	print("\n[+] Cracked NTLM hashes")
	for h in ntlm_dict:
		print("%s:%s" % (h, ntlm_dict[h]))

	if lm_lines is not None:
		print("\n[+] Cracked LM hashes")
		for h in lm_dict:
			print("%s:%s" % (h, lm_dict[h]))

	print("\n[+] Cracked credentials")
	for a in all_info:
		if a.get("password") != "":
			print("%s:%s" %(a.get("username"), a.get("password")))
			with open(output_file, 'a') as out:
				out.write('%s:%s\n' %(a.get("username"), a.get("password")))

	print("\n[+] Cracked credentials stored in %s\n"%(output_file))


if __name__ == "__main__":
	main()