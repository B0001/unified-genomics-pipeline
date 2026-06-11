import crypt4gh.lib
import crypt4gh.keys

# Generate or load secure Crypt4GH keys
private_key = crypt4gh.keys.get_private_key("node_secret.sec", callback=lambda: 'password')
public_key = crypt4gh.keys.get_public_key("node_public.pub")
keys = [(0, private_key, public_key)]

# Crypt4GH encrypts the raw FASTQ or VCF data before it is ever sent to the TES environment
with open("patient_data.fastq", "rb") as infile, open("patient_data.fastq.c4gh", "wb") as outfile:
    crypt4gh.lib.encrypt(keys, infile, outfile)