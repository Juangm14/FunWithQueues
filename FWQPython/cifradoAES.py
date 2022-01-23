from Crypto.Cipher import AES
from secrets import token_bytes
import binascii

#key = token_bytes(32)
file = open('symmetricKey.txt', 'r')

key = file.read()
print(key)
key = binascii.a2b_hex(key)
print(key)

def encrypt(msg):

    cipher = AES.new(key, AES.MODE_EAX)
    nonce = cipher.nonce
    ciphertext, tag = cipher.encrypt_and_digest(msg.encode('ascii'))
    return nonce, ciphertext, tag

def decrypt(nonce, ciphertext, tag):
    cipher = AES.new(key, AES.MODE_EAX, nonce=nonce)
    plaintext = cipher.decrypt(ciphertext)

    try:
        cipher.verify(tag)
        return plaintext.decode('ascii')
    except Exception:
        return False

nonce, ciphertext, tag = encrypt(input('Enter a message: '))

print(nonce)
print(ciphertext.hex())
print(tag)

plaintext = decrypt(nonce, ciphertext, tag)

print(f'Cipher text: {ciphertext}')
print(f'Plain text: {plaintext}')

