# -*- coding: utf-8 -*-
import sys

usage = """Checks an API key, reports the status to stdout

Uses the db specified in config.py. 

Usage:
    ./mkinvkey.py key

Example:
    $ python mkapikey.py 55f9e6065a35cebbe9d7ffb5f8b8aa610588d5b4736c79204fb12f57f85a371
    good
    $
"""


def main():
	if len(sys.argv) != 2:
		print usage
		exit(1)

        key = sys.argv[1]
                
	import model
	apik = model.APIKey.auth(key)
	print apik
	exit(0)


if __name__ == '__main__':
	main()
