import os
import sys
import hashlib
import binascii
import argparse
import itertools as it
from collections import Counter 

output_file_creds = "credentials.txt"
output_file_lm = "cracked_lm.txt"
output_file_ntlm = "cracked_ntlm.txt"


def get_args():
	parser = argparse.ArgumentParser()
	parser.add_argument('-f', '--ntds', required=True, action='store', help='Ntds.dit file location')
	parser.add_argument('-l', '--lm', required=False, action='store', help='Cracked LM hashes file')
	parser.add_argument('-n', '--ntlm', required=False, action='store', help='Cracked NTLM hashes file')
	parser.add_argument('-d', '--debug', required=False, type=str2bool, nargs='?', const=True, default=False, help="Debug option. Default: False")
	parser.add_argument('-m', '--top_most_common', default = 10, required=False, action='store', help='Top most common passwords. Default: 10')
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


def most_common_hashes(list_, dict_, keys, maxval, type_ = ""): 
	print("\n[+] Top %s most common %s hashes " % (maxval, type_))
	occurence_count = Counter(list_) 
	for h in occurence_count.most_common(maxval):
		hash_ = h[0]
		times = h[1]
		password = dict_[hash_] if hash_ in keys else "[Password not cracked]"
		print("%s - %s times (Password: %s)"%(hash_, times, password))


def str2bool(v):
    if isinstance(v, bool):
       return v
    if v.lower() in ('yes', 'true', 't', 'y', '1'):
        return True
    elif v.lower() in ('no', 'false', 'f', 'n', '0'):
        return False
    else:
        raise argparse.ArgumentTypeError('Boolean value expected.')


def main():

	args = get_args()
	ntds_lines = open(args.ntds).read().splitlines()
	ntlm_lines = open(args.ntlm).read().splitlines() if args.ntlm is not None else None
	lm_lines = open(args.lm).read().splitlines() if args.lm is not None else None
	top_most_common = int(args.top_most_common)
	debug = str2bool(args.debug)

	all_ntlm = []
	all_lm = []
	all_info = []
	ntlm_dict = {}
	lm_dict = {}


	# Create dictionary with NTLM cracked hashes
	if ntlm_lines is not None:
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


	print("\n[+] Total LM hashes:       %s"%(len(all_lm)))
	print("[+] Different LM hashes:   %s"%(len((set(all_lm)))))

	print("\n[+] Total NTLM hashes:     %s"%(len(all_ntlm)))
	print("[+] Different NTLM hashes: %s"%(len((set(all_ntlm)))))
	
	if ntlm_lines is not None:
		most_common_hashes(all_ntlm, ntlm_dict, ntlm_dict.keys(), top_most_common, "NTLM")
	
	if lm_lines is not None:
		most_common_hashes(all_lm, lm_dict, lm_dict.keys(), top_most_common, "LM")


	print("\n[+] Accounts with the same username and password")
	for a in all_info:
		if len(a.get("username").split('\\'))>=2:
			user = a.get("username").split('\\')[1]
		else:
			user = a.get("username")
		pwd_ = a.get("password")
		if user == pwd_:
			print("%s:%s" %(a.get("username"), pwd_))

	
	if ntlm_lines is not None:
		print("\n[+] Cracked NTLM hashes")
		for h in ntlm_dict:
			if debug: print("%s:%s" % (h, ntlm_dict[h]))
			with open(output_file_ntlm, 'a') as out:
					out.write('%s:%s\n' %(h, ntlm_dict[h]))
		cracked_ntlm = ntlm_dict.keys()
		counter = Counter(all_ntlm)
		occurence_count = 0
		for i in counter:
			if i in cracked_ntlm:
				occurence_count += counter[i]
		if len(ntlm_dict) >= 1:  print("[+] %s out of %s different hashes cracked (%.2f %%)"%(len(ntlm_dict),len((set(all_ntlm))),float(100*(len(ntlm_dict)/len((set(all_ntlm)))))))
		if occurence_count >= 1: print("[+] %s out of %s total hashes cracked (%.2f %%)"%(occurence_count, len((all_ntlm)), float(100*(occurence_count/len((all_ntlm)))) ))
		print("[+] Cracked NTLM hashes appended to %s\n"%(output_file_ntlm))


	if lm_lines is not None:
		print("\n[+] Cracked LM hashes")
		for h in lm_dict:
			if debug: print("%s:%s" % (h, lm_dict[h]))
			with open(output_file_lm, 'a') as out:
				out.write('%s:%s\n' %(h, lm_dict[h]))
		cracked_lm = lm_dict.keys()
		counter = Counter(all_lm)
		occurence_count = 0
		for i in counter:
			if i in cracked_lm:
				occurence_count += counter[i]
		if len(lm_dict) >= 1:    print("[+] %s out of %s different hashes cracked (%.2f %%)"%(len(lm_dict),len((set(all_lm))),float(100*(len(lm_dict)/len((set(all_lm)))))))	
		if occurence_count >= 1: print("[+] %s out of %s total hashes cracked (%.2f %%)"%(occurence_count, len((all_lm)), float(100*(occurence_count/len((all_lm)))) ))
		print("[+] Cracked LM hashes appended to %s\n"%(output_file_lm))


	print("\n[+] Cracked credentials")
	total_pwnd = 0
	for a in all_info:
		if a.get("password") != "":
			total_pwnd += 1
			if debug: print("%s:%s" %(a.get("username"), a.get("password")))
			with open(output_file_creds, 'a') as out:
				out.write('%s:%s\n' %(a.get("username"), a.get("password")))
	if total_pwnd >= 1: print("[+] %s out of %s different hashes (%.2f %%)"%(total_pwnd, len(all_ntlm), float(100*(total_pwnd/len(all_ntlm))) ) )
	print("[+] Cracked credentials appended to %s\n"%(output_file_creds))


if __name__ == "__main__":
	main()