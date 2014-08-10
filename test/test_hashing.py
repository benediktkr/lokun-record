#! /usr/bin/env python2
# coding: utf8
import sys
sys.path.append("..")
import unittest

import hashing


def verify_format(testcase, hashed_passwd):
    testcase.assertEqual(len(hashed_passwd.split('$')), 3)
    for part in hashed_passwd.split('$'):
        testcase.assertIsInstance(part, str)
        testcase.assertTrue(len(part) > 0)
    method = hashed_passwd.split('$')[0]
    _ = getattr(hashing, 'hash_'+method) # See if this raises AttributeError


def verify_reproducible(testcase, plaintext_passwd, hashed_passwd):
    (method, salt, hash_) = hashed_passwd.split('$')
    hash_func = getattr(hashing, 'hash_'+method)
    testcase.assertEquals(hash_func(plaintext_passwd, salt=salt), hashed_passwd)
    

class TestSha512s(unittest.TestCase):
    def setUp(self):
        hashing.sha512s_static_salt = 'asdfadsfadasdfafaadssa'

    def test_well_formed(self):
        verify_format(self, hashing.hash_sha512s('hunter2'))

    def test_reproducible(self):
        hashed_passwd = hashing.hash_sha512s('Password1')
        verify_reproducible(self, 'Password1', hashed_passwd)

        

if __name__ == '__main__':
    unittest.main()
