#!/usr/bin/env python3

from Crypto.Cipher import AES

key = bytes([i for i in range(60, 76)])
iv = b"\x00" * 16
ciphertext = bytes.fromhex("1417c97254a837b486e829faab5628df")

cipher = AES.new(key, AES.MODE_CBC, iv=iv)
flag = cipher.decrypt(ciphertext)

print(f"[!]Youpiii !!\t{str(flag,"utf-8")}")
