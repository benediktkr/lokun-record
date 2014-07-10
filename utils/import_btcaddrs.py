import model
import sys

usage = """Imports a list of bitcoin addresses from a file.

Example:
 $ python import_btcaddrs.py file.txt

"""

if len(sys.argv) != 1:
    print usage
    sys.exit(1)

l = open(sys.argv[1], "r").readlines()
l = [a[:-1] for a in l]
for a in l:
    model.DB.get().add_btc_addr(a)
