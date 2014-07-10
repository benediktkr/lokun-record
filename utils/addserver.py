# -*- coding: utf-8 -*-
import sys
sys.path.append("..")

usage = """Adds a new server to the load balancer and creates an
API key for that server.
Uses the db specified in config.py. 

Usage:
    ./addserver.py server ip

Example:
    $ python addserver "vpn03.beta" 46.149.22.231
    55f9e6065a35cebbe9d7ffb5f8b8aa610588d5b4736c79204fb12f57f85a371d
    $
"""


def main():
    if len(sys.argv) != 3:
        print usage
        sys.exit(1)
        
    from record import model
    # No input checking
    name = sys.argv[1]
    ip = sys.argv[2]
    apik = model.APIKey.new(name)
    model.DB.get().lb_add(name, ip)
    print apik.key
    exit(0)

if __name__ == '__main__':
    main()
