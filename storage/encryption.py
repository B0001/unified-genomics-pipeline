from __future__ import annotations
import crypt4gh.keys
import crypt4gh.lib

def load_keys(private_key_path: str, public_key_path: str, password: str = "") -> list:
    private_key = crypt4gh.keys.get_private_key(private_key_path, callback=lambda: password)
    public_key  = crypt4gh.keys.get_public_key(public_key_path)
    return [(0, private_key, public_key)]

def encrypt_file(keys: list, input_path: str, output_path: str) -> None:
    with open(input_path, "rb") as infile, open(output_path, "wb") as outfile:
        crypt4gh.lib.encrypt(keys, infile, outfile)

def decrypt_file(keys: list, input_path: str, output_path: str) -> None:
    with open(input_path, "rb") as infile, open(output_path, "wb") as outfile:
        crypt4gh.lib.decrypt(keys, infile, outfile)
