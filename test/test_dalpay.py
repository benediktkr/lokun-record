#! /usr/bin/env python2
# coding: utf8
import sys
sys.path.append("..")
import unittest
import os

from record import dalpay

class TestDalPay(unittest.TestCase):
    def setUp(self):
        self.key = os.urandom(32).encode("hex")
        dalpay.dalpay_aeskey = self.key 

    def test_reproducible(self):
        key2 = os.urandom(32).encode("hex")
        d1 = dalpay.DalPay("user", 2000)
        d2 = dalpay.DalPay.read(d1.message)
        assert type(d2.amount) == int
        assert d1 == d2
    
        

if __name__ == '__main__':
    unittest.main()
