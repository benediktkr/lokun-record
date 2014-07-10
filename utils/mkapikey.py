# -*- coding: utf-8 -*-
import sys

usage = """Creates a new API key, registers it to db as \"good\" aand prints it to stdout.
Uses the db specified in config.py. 

Usage:
    ./mkinvkey.py name

Example:
    $ python mkapikey.py vpn3.beta
    55f9e6065a35cebbe9d7ffb5f8b8aa610588d5b4736c79204fb12f57f85a371d
    $
"""


def main():
        if len(sys.argv) =! 2:
                print usage()
                sys.exit(1)

        name = sys.argv[1]
	from record import model
	apik = model.APIKey.new(name, "good")
	print apik.key
	exit(0)


if __name__ == '__main__':
	main()
