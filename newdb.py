#! /usr/bin/env python2
# coding: utf8
import sys

usage = """Creates a new empty db with all tables set up and ready.

Usage:
    ./newdb.py <dbname>

Example:
> ./newdb.py production.db"""


def main():
	if len(sys.argv) != 2:
		print usage
		exit(1)

	import model
	import sqlite3
	conn = sqlite3.connect(sys.argv[1])
	model.mktables(conn)
	conn.close()
	exit(0)


if __name__ == '__main__':
	main()
