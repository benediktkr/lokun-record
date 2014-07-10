# coding: utf8
import os

"""Configuration, should have a seperate config.py in production."""

sha512s_static_salt = 'omgitsatestingsalt'

# db should be the filename of the sqlite db or 'testing' for a new unit test db
#db = 'production.db'
db = '/home/benedikt/projects/lokun/record/development.db'

# Where client's keys and installers are stored. 
#clients_dir = '/srv/clients'
clients_dir = '/home/benedikt/devroot/clients'

# Secret keys 
#keys_dir = '/srv/keys'
keys_dir = '/home/benedikt/devroot/keys'

# The dir where key related scripts like client_keygen.py and mkinstaller.py
# are stored
#keycontrol_dir = '/srv/keycontrol'
#keycontrol_dir = '/home/benedikt/devroot/keycontrol'
keycontrol_dir = '/home/benedikt/projects/lokun/keycontrol'
openssl_file = os.path.join(keycontrol_dir, 'openssl-bk.cnf')

# Installer build dir
#installer_bdir = '/srv/installer-build'
installer_bdir = '/home/benedikt/devroot/installer-build'

# A logfile the process can write to. 
logfile = "debug.log"

# Pricing and bitcoin settings. Use lower-case. 
default_exchange = "coinbase"
isk_price = 2000

# it's now somewhere around 0.15... I wish
#btc_price = 0.15

logfile = "debug.log"

mailchecker_uname = "paymentbot@lokun.is"
mailchecker_passwd = ""

logpath = "/home/benedikt/devroot/log"
logfrom = "lokun@lokun.is"
logto = ["benedikt@inventati.org"]


dalpay_passwd = "dalpaypass"
# d0aa.. is the dev key
dalpay_key = "d0aa599304ff1cea6b51dadd5dc6211524538c40940235c77f33b29a1cef2794"
