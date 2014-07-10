# -*- coding: utf-8 -*-
import sys

usage = """Updates the prices in BTC and prints the new one out to stdout
Uses the db specified in config.py. Will probably end up as a cron job

Usage:
    ./update_btcprices.py
"""


def main():
	if len(sys.argv) != 1:
		print usage
		exit(1)
                
	import model
	bp = model.BTCPrices.update()
	print "%.2f BTC" % bp.price
	exit(0)


if __name__ == '__main__':
	main()
