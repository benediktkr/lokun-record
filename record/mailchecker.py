#coding: utf-8

from model import Deposit, DB
from Bankmail import *
import sys
import sqlite3
import imaplib
import traceback
from datetime import datetime
from time import sleep

from common.logger import Logger
import config

logger = Logger()
def log(msg):
    return logger.log(msg)
    

def check(user, passwd):
    try:
        i = imaplib.IMAP4_SSL("imap.gmail.com")
        i.login(user, passwd)
    except imaplib.IMAP4.error as ex: ## kannski grípa utar
        log(str(ex))
        sys.exit(1)

    i.select()
    status, response = i.search(None, 'ALL')
    mailids = [int(a) for a in response[0].split()]
    my_mailid = DB.get().max_mailid()
    new_mailids = [a+1 for a in range(my_mailid, max(mailids))]

    for mailid in new_mailids:
        DB.get().add_mailid(mailid)
        f = i.fetch(mailid, '(RFC822)')
        mail = f[1][0][1]
        info = f[1][0][0]
        try:
            b = Bankmail(mail)
            # .new() calls .save() :(
            Deposit.new(b.username, b.amount, "Wire", deposit=True)
            logger.email("Username: {username}\nAmount: {amount}".format(**b.__dict__))
        except NotBankmail as notb:
            log("Skipping {0}: {1}".format(mailid, str(notb)))
            pass
        except ValueError as ve:
            logger.email("Skipping {0}: {1}".format(mailid, ve))
        except AttributeError:
            logger.email("User {username} not found. Amount: {amount}. Parser: {bank}".format(**b.__dict__))
        except Exception as e:
            logger.email("Uncaught exception: " + str(e))
            sys.exit(1)

    i.close()
    i.logout()
    
                   
if __name__ == "__main__":
    try:
        check(config.mailchecker_uname, config.mailchecker_passwd)
    except KeyboardInterrupt:
        sys.exit(2)
    
    
