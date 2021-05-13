# ntds-analyzer

A script to analyze hashes in Ntds.dit files once the NTLM and LM hashes have been cracked. Compared to other similar tools, it offers improvements such as calculating the plaintext password when the LM hash has been cracked but not the NTLM (as I explained [in this blog](https://github.com/ricardojoserf/LM_original_password_cracker)). 

It also offers information such as:

- Top most common NTLM and LM hashes.

- List of compromised accounts using the same username and password.

- List of compromised accounts with the string "admin" in the username or password.

- Save the list of cracked credentials in *user:password* format in text files.

- Save the list of cracked NTLM and/or LM hashes in *hash:password* format in text files.


### Usage

```
python3 analyzer.py -f NTDS.DIT [-n NTLM_CRACKED_HASHES] [-l LM_CRACKED_HASHES] [-m TOP_MOST_COMMON_PASSWORDS] [-d DEBUG]
```

You can use a file with NTLM cracked hashes in *hash:password* (*-n* parameter), a file with LM cracked hashes in *hash:password* (*-l* parameter) or both. You can set how many most common hashes you want to calculate (*-m* parameter) and if you want to print the hashes in the screen (*-d* parameter).

### Example

```
python3 analyzer.py -f test_files/ntds.dit -n test_files/ntlm_cracked.txt -l test_files/lm_cracked.txt -m 5 -d True
```

We start with 4 NTLM and 8 LM cracked hashes and the Ntds.dit file:

![Image0](images/image0.png)

The script shows the number of hashes, the most common ones and which accounts use the same username and password:

![Image1](images/image1.png)

Then it shows the cracked hashes. Before we had 4 NTLM hashes cracked and now we have 10! That is because we calculated the password from the related LM hashes:

![Image2](images/image2.png)

Finally we get the list of users and their passwords in *user:password* format and the result is dumped to the "credentials.txt" file:

![Image3](images/image3.png)
