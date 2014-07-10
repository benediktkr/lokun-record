#! /usr/bin/env python2
# -*- coding: utf-8 -*-
import sys

from record import model

usage = """Deposists ISK to a user. Prints out the users current credit_isk
after deposit. 

Uses the db specified in config.py

Usage:
    ./deposit.py <username> [amount]

Example:
> ./deposit bktestarhttps 2000
4000"""

def main():
    if len(sys.argv) == 2:
        amount = 2000
    elif len(sys.argv) == 3:
        amount = int(sys.argv[2])
    else:
        print usage
        sys.exit(1)

    username = sys.argv[1]
    try:
        user = model.User.get(username)
        user.credit_isk += amount
        user.save()
    except:
        print "Invalid user"
        sys.exit(2)

    print user.credit_isk

if __name__ == '__main__':
    main()
