#! /usr/bin/env python2
# coding: utf8
import unittest
import os
import random
import encryption


def verify_format(testcase, encrypted_msg):
    testcase.assertEqual(len(encrypted_msg.split('$')), 4)
    for part in encrypted_msg.split('$'):
        testcase.assertIsInstance(part, str)
        testcase.assertTrue(len(part) > 0)
        try:
            part.decode("hex") # see if this rasies TypeError
        except TypeError:
            print part
            print encrypted_msg
            raise TypeError
    _ = int(encrypted_msg.split("$")[1], 16) # See if this rasies an error
    #method = hashed_msg.split('$')[0]
    #_ = getattr(hashing, 'hash_'+method) # See if this raises AttributeError


def verify_reproducible(testcase, plaintext_msg, encrypted_msg, key):
    testcase.assertEquals(encryption.decrypt_and_mac(key, encrypted_msg), plaintext_msg)
    

class TestAES(unittest.TestCase):
    def setUp(self):
        self.key = os.urandom(32).encode("hex")
        # There are a bunch of randomly generated things here, 
        # iterating a bunch of times is helpful
        self.iterations = 2000

    def test_well_formed(self):
        for _ in xrange(self.iterations):
            verify_format(self, encryption.encrypt_then_mac(self.key, "State secret"))

    def test_reproducible(self):
        for _ in xrange(self.iterations):
            encrypted_message = encryption.encrypt_then_mac(self.key, 'user,2000')
            verify_reproducible(self, 'user,2000', encrypted_message, self.key)

    def test_failedmac(self):
        for _ in xrange(self.iterations):
            encrypted_message = encryption.encrypt_then_mac(self.key, 'user,2000')
            mac = encrypted_message.rsplit("$", 1)[-1]
            without_mac = encrypted_message.split("$")[:3]
            r = random.randint(0, len(mac)-1)
            mac_modified = mac[:r] + chr(ord(mac[r])+1) + mac[r+1:]
            msg_modified = "$".join(without_mac + [mac_modified])
            try:
                encryption.decrypt_and_mac(self.key, msg_modified)
                # Should not reach this
                assert False
            except ValueError:
                pass

if __name__ == '__main__':
    unittest.main()
