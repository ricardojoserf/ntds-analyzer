# ntds-analyzer

A tool to analyze hashes in Ntds.dit files once the NTLM and LM hashes have been cracked.


- Information about occurrence of the hashes

- Most common NTLM and LM hashes

- It calculates the password when the LM hash has been cracked but the NTLM not (explained [here](https://github.com/ricardojoserf/LM_original_password_cracker))

- List of credentials in *user:password* format

### Example

```
python3 analyzer.py -f test_files/ntds.dit -n test_files/ntlm_cracked.txt -l test_files/lm_cracked.txt
```

We have cracked 6 NTLM hashes and 7 LM hashes:

![Image0](images/image0.png)

We run the script and see we have the value of 12 NTLM hashes now (we got the correct value from the LM hash and testing all the possibilities):

![Image1](images/image1.png)

We also get the list of users and their passwords:

![Image2](images/image2.png)