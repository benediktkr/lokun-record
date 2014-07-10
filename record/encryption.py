# coding: utf-8
from Crypto.Cipher import AES
import os
import base64
import hashlib
import hmac
import sec

def kdf(key):
    return hashlib.sha512(key.decode("hex")).hexdigest()

def gen_nonce(bits = 32):
    return int(os.urandom(bits/8).encode("hex"), 16)

def int2hex(integer):
    hexstr = hex(integer).lstrip("0x")
    if len(hexstr) % 2 == 0:
        return hexstr
    else:
        return "0" + hexstr

def aes_encrypt(key, plain):
    """AES encrypts plain with hex-encoded key as input and returns
    a string [ciphertext]$[nonce]$[IV] """
    
    iv = os.urandom(16)
    aes = AES.new(key.decode("hex"), AES.MODE_CBC, IV=iv)
    nonce = gen_nonce(32)
    plain = plain + '$' + str(nonce) + '$'
    pad_len = 16 - len(plain) % 16
    # encrypt(plain $ nonce $ padding)
    ciphertext = aes.encrypt(plain + os.urandom(pad_len)).encode("hex")
    return ciphertext + "$" + int2hex(nonce) + "$" + iv.encode("hex")

def aes_decrypt(key, ciphertext, plain_nonce, iv):
    """AES decrypts ciphertext created with aes_encrypt and verifies nonce"""

    aes = AES.new(key.decode("hex"), AES.MODE_CBC, IV=iv.decode("hex"))
    padded = aes.decrypt(ciphertext.decode("hex"))
    plain, decrypted_nonce = padded.split('$')[:2]
    
    if int(plain_nonce, 16) != int(decrypted_nonce):
        raise ValueError("Invalid nonce")
    
    return plain

def hmac_sha512(key, message):
    # Sha512, so key is 64 bit
    h = hmac.new(key.decode("hex"), message, hashlib.sha512)
    return h.hexdigest()

def encrypt_then_mac(key, plain):
    encrypted = aes_encrypt(key, plain)
    hmac = hmac_sha512(key, encrypted)
    return encrypted + "$" + hmac

def decrypt_and_mac(key, message):
    # This works because hmac is hex-encoded, thus the '$' preceeding it is always
    # the last '$' in message
    encrypted, hmac = message.rsplit("$", 1)
    if not sec.compare(hmac, hmac_sha512(key, encrypted)):
        # Usually this means the key is wrong
        raise ValueError("Invalid HMAC")
    ciphertext, nonce, iv = message.split("$")[:3]
    plain = aes_decrypt(key, ciphertext, nonce, iv)
    return plain
