import hashlib
import hmac
from Crypto.Cipher import AES  # pip install pycrypto
import base64

string = "79233adec2fbae0e4602ed5bfa7296ddas34erq3"
s = AES.new(string[:32])
print(s.block_size)

bstr = bytes(string, "utf-8")  # convert string to bytes


encoded = base64.b64encode(bstr)  # convert bytes of string to coding

decoded = base64.b64decode(encoded).decode("utf-8")  # convert coding to previous string

# hash = hmac.new(encoded, b'', hashlib.sha256).hexdigest()   # convert bytes of string to hexdigest

# # Output
# print('\n','Bytes:', bstr,'\n \n',
#             'Encoded: ', encoded ,'\n \n',
#             'Hashing:', hash , '\n \n',
#             'Decoding:', decoded)


text = string + (AES.block_size - len(string) % AES.block_size) * "0"

# example 1
enc_str = AES.new(string[:16])

encrypt = base64.b64encode(enc_str.encrypt(text)).decode("utf-8")

h_mac = hmac.new(bstr, b"Hello, World!", hashlib.sha256).hexdigest()

print(encrypt, "\n \n", h_mac)
print(len(encrypt), len(h_mac))
