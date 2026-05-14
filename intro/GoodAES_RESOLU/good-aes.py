from Crypto.Cipher import AES
from secret import FLAG

key = bytes([i for i in range(60, 76)])
cipher = AES.new(key, AES.MODE_CBC, iv = b"\x00" * 16)
ciphertext = cipher.encrypt(FLAG)

print(ciphertext.hex())
# 1417c97254a837b486e829faab5628df
