#!/usr/bin/python
#coding: utf-8

"""A simple IMAPS bot to recieve payment notifications from the
Icelandic online banks"""

import sys
import re
import getpass
import imaplib
import email
import sqlite3
import traceback
from datetime import datetime
from base64 import b64decode
from time import sleep
from BeautifulSoup import BeautifulSoup

import model

## Helpers
def log(message):
    s = unicode(datetime.now().replace(microsecond=0)) + "\t" + unicode(message)
    print s

## Parsers
## (I'm sorry)
def isb_parser(mail):
    """Base64 encoded and missing the plaintext part of the message"""
    payload = b64decode(mail)
    p = BeautifulSoup(payload)
    amounttable = p.find('table').fetchNextSiblings()[5].find("tr")
    amount = int(re.sub(r"[^0-9]", "", amounttable.td.text))    
    skyring = amounttable.fetchNextSiblings()[0].td.text.encode("utf-8")
    return {'amount': amount, 'username': skyring}

def landsbanki_parser(mail):
    """Multipart message that is base64 encoded. Select line and hope
    the best"""
    plaintext = b64decode(mail[0].get_payload())
    lines = plaintext.splitlines()
    amount = int(re.sub(r"[^0-9]", "", lines[4].split(" ")[-2]))
    skyring = unicode(lines[16].strip(), 'utf-8')
    return {'username': skyring, 'amount': amount}

def arion_parser(mail):
    """Non-multipart but with the plaintext in HTML comment"""
    s = mail[:mail.index("-->")]
    lines = s.splitlines()
    amount = int(re.sub(r"[^0-9]", "", lines[9]))
    skyring = unicode(lines[11].split(": ")[1].strip(), 'utf-8')
    return {'username': skyring, 'amount': amount}

def spar_parser(mail):
    """Multipart message but the text version has a lot of linebreaks,
    so I didn't split by lines."""
    text = mail[0].get_payload()
    skyring_start = text.index("Sk=FDring:")+10
    skyring_end = text.index("\n", skyring_start)
    amount_start = text.index("kr. ")+4
    amount_end = text.index(",00", amount_start)
    skyring = unicode(text[skyring_start:skyring_end].strip())
    amount = int(re.sub(r"[^0-9]", "",  text[amount_start:amount_end].strip()))
    return {'username': skyring, 'amount': amount}
    
## Main stuff

def check(user, passwd):
    try:
        i = imaplib.IMAP4_SSL("imap.gmail.com")
        i.login(user, passwd)
    except imaplib.IMAP4.error as ex:
        log(ex)
        sys.exit(1)
    i.select()
    status, response = i.search(None, 'ALL')
    mailids = [int(a) for a in response[0].split()]
    my_mailid = model.DB.get().max_mailid()
    new_mailids = [a+1 for a in range(my_mailid, max(mailids))]

    for mailid in new_mailids:
        log("I'm at: " + str(mailid))
        f = i.fetch(mailid, '(RFC822)')
        mail = f[1][0][1]
        info = f[1][0][0]
        process(mail)
        model.DB.get().add_mailid(mailid)

    i.close()
    i.logout()
    
def process(message):
    mail = email.message_from_string(message)
    sender = mail['X-Original-Sender']
    bank = ""

    try:
        if sender == 'noreply@landsbankinn.is':
            bank = "landsbankinn"
            result = landsbanki_parser(mail.get_payload())
        elif sender == 'islandsbanki@islandsbanki.is':
            bank = "isb"
            result = isb_parser(mail.get_payload())
        elif sender == 'netbanki@arionbanki.is':
            bank = "arion"
            result = arion_parser(mail.get_payload())
        elif sender == 'vefstjori@spar.is':
            bank = "spar"
            result = spar_parser(mail.get_payload())
    except Exception as e:
        log("Parser for {0} failed".format(bank))
        log(traceback.print_exc())
            
    if not bank:
        # This isn't a bank statement, probably just some other mail
        return                
    try:
        username, amount = result["username"], result["amount"]
        user = model.User.get(username) # == False if not found
        user.credit_isk += amount  # raises AttributeError
        user.save()
        if username == "":
            log("Username missing")
            return
        log("Username: {0}, Amount: {1} kr.".format(username, amount))
    except sqlite3.ProgrammingError:
        log("Invalid username: " + result['username'])
        return
    except AttributeError:
        log("Invalid username: " + result['username'])
        return
        
if __name__ == '__main__':
    user = raw_input("Username: ")
    passwd = getpass.getpass()
    try:
        while True:
            check(user, passwd)
            sleep(10*60)
   
    except KeyboardInterrupt:
        sys.exit(1)
        
