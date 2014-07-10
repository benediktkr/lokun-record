#!/usr/bin/python
#coding: utf-8

"""Part of Lokun. Parsing of confirmation emails from the icelandic
banks. 
"""
import re
import email
from base64 import b64decode
from BeautifulSoup import BeautifulSoup
import quopri

import model

class Bankmail(object):
    def __init__(self, message):
        self.mail = email.message_from_string(message)
        data = self.parse()
        self.username, self.amount, self.bank = data

    def __attrs__(self):
        attrs = []
        attrs.append(('amount', self.amount))
        attrs.append(('username', self.username))
        attrs.append(('bank', self.bank))
        return attrs

    def parse(self):
        payload = self.mail.get_payload()
        frm = self.mail["From"]
        sender = self.mail['X-Original-Sender'] or getsender(frm)

        if sender == 'noreply@landsbankinn.is':
            r = self.landsbanki_parse(payload)
        elif sender == 'islandsbanki@islandsbanki.is':
            r = self.isb_parse(payload)
        elif sender == 'netbanki@arionbanki.is':
            r = self.arion_parse(payload)
        elif sender == 'vefstjori@spar.is':
            r = self.spar_parse(payload)
        else:
            raise NotBankmail("No parser for {0}".format(sender))
        
        username, amount, bank = r
        if username == "" or not model.good_username(username):
            raise ValueError("Invalid username: \"{0}\"".format(username))
        if amount < 0:
            raise ValueError("amount")
        return r

    def isb_parse(self, payload):
        """Base64 encoded and missing the plaintext part of the message"""
        p = BeautifulSoup(b64decode(payload))
        amounttable = p.find('table').fetchNextSiblings()[5].find("tr")
        amount = int(re.sub(r"[^0-9]", "", amounttable.td.text))    
        skyring = amounttable.fetchNextSiblings()[0].td.text.encode("utf-8")
        return skyring, amount, "isb"

    def landsbanki_parse(self, payload):
        """Multipart message that is base64 encoded. Select line and hope
        the best"""
        plaintext = b64decode(payload[0].get_payload()) # ?
        lines = plaintext.splitlines()
        amount = int(re.sub(r"[^0-9]", "", lines[4].split(" ")[-2]))
        skyring = unicode(lines[16].strip(), 'utf-8')
        return skyring, amount, "lb"

    def arion_parse(self, payload):
        """Non-multipart but with the plaintext in HTML comment"""
        s = payload[:payload.index("-->")]
        lines = s.splitlines()
        # Fault tolerance, it changes around a bit
        try:
            amount = int(re.sub(r"[^0-9]", "", lines[9].split(": ")[1]))
            raw = quopri.decodestring(lines[11]).split(": ")[1]
        except IndexError:
            raise ValueError("2 Arion Bankmail without plaintext encoutered")
        # Not sure if nessesary or formed user input from user "Numi"
        skyring = raw.strip().decode("tis-620")
        return skyring, amount, "arion"
    
    def spar_parser(self, payload):
        """Multipart message but the text version has a lot of linebreaks,
        so I didn't split by lines."""
        text = payload[0].get_payload() # ?
        skyring_start = text.index("Sk=FDring:")+10
        skyring_end = text.index("\n", skyring_start)
        amount_start = text.index("kr. ")+4
        amount_end = text.index(",00", amount_start)
        skyring = unicode(text[skyring_start:skyring_end].strip())
        amount = int(re.sub(r"[^0-9]", "",  text[amount_start:amount_end].strip()))
        return skyring, amount, "spar"
    
def getsender(frm):
    if "<" not in frm:
        return unicode(frm)
    start = frm.index("<")
    end = frm.index(">")
    return unicode(frm[start+1:end])

class NotBankmail(Exception):
    pass
