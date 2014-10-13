#! /usr/bin/env python2
# -*- coding: utf-8 -*-
import sys
sys.path.append("..")

from record import model

usage = """Deposists ISK to a user. Prints out the users current credit_isk
after deposit. 

Uses the db specified in config.py. Always creates an invoice. If you want to 
add credit to a user, just use the python shell. Like so;

  >>> import model
  >>> user = model.User.get("username")
  >>> user.credit_isk += 100000
  >>> user.save()
  >>> 

Usage:
    ./deposit.py <username> [amount [method]] 

Example:
> ./deposit.py bktestarhttps 2000
2000
> ./deposit.py bktestarhttps 2000 "Wire"
4000
"""

def main():
    if len(sys.argv) == 2:
        amount = 2000
        method = "Wire"
    elif len(sys.argv) == 3:
        amount = int(sys.argv[2])
        method = "Wire"
    elif len(sys.argv) == 4:
        amount = int(sys.argv[2])
        method = str(sys.argv[3])
    else:
        print usage
        sys.exit(1)

    username = sys.argv[1]
    try:
        deposit = model.Deposit.new(username, amount, method)
        user = model.User.get(username)
        print user.credit_isk
        print deposit.invoice
    except Exception as e:
        print str(e.message)
        sys.exit(2)



if __name__ == '__main__':
    main()
