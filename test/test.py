from encryption import *

import os
from base64 import b64encode, b64decode

key = os.urandom(32).encode("hex")

for i in xrange(20000):
    rndplain = os.urandom(128).encode("hex") + "$" + os.urandom(10).encode("hex")    
    #plain = "benediktkr$2000"
    message = encrypt_then_mac(key, b64encode(rndplain))
    plain2 = b64decode(decrypt_and_mac(key, message))
    if rndplain != plain2:
        print "oops"

