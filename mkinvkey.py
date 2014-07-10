#! /usr/bin/env python2
# -*- coding: utf-8 -*-
import sys

usage = """Creates a new invite key, registers it to db and prints it to stdout.
Uses the db specified in config.py

Usage:
    ./mkinvkey.py

Example:
> ./mkinvkey.py production.db
iWPI1HworTArFbWg0JZNbGYJQMqlHSgKsy5vOlYAcT0="""


def main():
	if len(sys.argv) != 1:
		print usage
		exit(1)

	import model
	ik = model.InviteKey.new()
	print ik.key
	exit(0)


if __name__ == '__main__':
	main()
