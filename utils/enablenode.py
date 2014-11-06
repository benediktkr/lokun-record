#! /usr/bin/env python2
# -*- coding: utf-8 -*-
import sys
sys.path.append("..")

from record import model

usage = """Enable or disable a VPN node. 

Usage:
    ./enablenode.py <node> [-d] 

Example:
> ./enablenode.py vpn31
vpn31 has been enabled
> ./enablenode.py vpn31 -d
vpn31 has been disabled
"""

def main():
    if len(sys.argv) == 2:
        enabled = True
    elif len(sys.argv) == 3:
        enabled = sys.argv[2] == "-d"
    else:
        print usage
        sys.exit(1)

    name = sys.argv[1]
    try:
        node = model.Node.get(name)
        node.enabled = enabled
        node.save()
        if node.enabled:
            print name, "has been enabled"
        else:
            print name, "has been disabled"
    except Exception as e:
        print str(e.message)
        sys.exit(2)


if __name__ == '__main__':
    main()
