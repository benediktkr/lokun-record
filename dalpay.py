#! /usr/bin/env python2
# coding: utf8

import encryption

# d0aa.. is the dev key. 
dalpay_aeskey = 'd0aa599304ff1cea6b51dadd5dc6211524538c40940235c77f33b29a1cef2794'

class DalPay(object):
    def __init__(self, username, amount, **kwargs):
        self.username = username
        self.amount = int(amount)
        self.desc = kwargs.get('desc', "VPN")
        self.pageid = kwargs.get("pageid", "01")
        self.key = kwargs.get('key', dalpay_aeskey)
        self.mer_id = "131201"
        self.valute_code = "isk"
        self.langcode = "en"
        self.posturl = "https://secure.dalpay.is/cgi-bin/order2/processorder1.pl"

    def __eq__(self, other):
        return self.__dict__ == other.__dict__

    @property
    def message(self):
        plain = "{0},{1}".format(self.username, self.amount)
        return encryption.encrypt_then_mac(self.key, plain)

    @classmethod
    def read(cls, message, **kwargs):
        key = kwargs.get('key', dalpay_aeskey)
        plain = encryption.decrypt_and_mac(key, message)
        username, amount = plain.split(',')
        return cls(username, amount)
