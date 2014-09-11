# coding: utf8
import sqlite3
import os
import re
import random
from datetime import date, timedelta, datetime
from subprocess import Popen, call
from time import time

from netaddr import IPAddress
from netaddr.core import AddrFormatError

import config
import hashing
import exchanges
import sec

#SUB_DL_BYTES = 1099511627776               
SUB_DL_BYTES = 1000000000000
SUB_LENGTH_DAYS = 30
# TODO: This variable now also exists in config
SUB_PRICE_ISK = config.isk_price

class NotEnoughFundsError(Exception):
    pass

class NodeList(list):
    @classmethod
    def get(cls):
        return cls([Node.get(a['name']) for a in DB.get().lb_get_all()])

    @classmethod
    def best(cls, n=3):
        all_nodes = cls.get()
        candidates =  [a for a in all_nodes if a.alive and a.enabled]
        by_score = sorted(candidates, key=lambda a: a.score)[:n]
        random.shuffle(by_score)
        return cls(by_score)

    @classmethod
    def alive(cls):
        all_nodes = cls.get()
        return cls([a for a in all_nodes if a.alive])

    @classmethod
    def down(cls):
        all_nodes = cls.get()
        return cls([a for a in all_nodes if a.down])

    @classmethod
    def disabled(cls):
        all_nodes = cls.get()
        return cls([a for a in all_nodes if not a.enabled]) 
    

class Node(object):
    def __init__(self, name, ip, **kwargs):
        self.name = str(name)
        self.ip = str(ip)
        self.throughput = kwargs.get('throughput', 0)
        self.total_throughput = kwargs.get('total_throughput', 0)
        self._uptime = kwargs.get('uptime', '0d 0h')
        self.cpu = kwargs.get('cpu', 0.0)
        self._usercount = kwargs.get('usercount', 0)
        # sqlite doesn't have bools
        selfcheck = kwargs.get('selfcheck', False)
        self.selfcheck = bool(selfcheck)
        # Enforce int for hearbeat (time.time() returns a float)
        heartbeat = kwargs.get('heartbeat', 0)
        self.heartbeat = int(heartbeat)
        enabled = kwargs.get('enabled', False)
        self.enabled = bool(enabled)
        is_exit = kwargs.get('is_exit', False)
        self.is_exit = bool(is_exit)
        
    @classmethod
    def get(cls, name):
        l = DB.get().lb_get(name)
        if not l:
            return False
        return cls(name, l['ip'], usercount=l['usercount'],
                   selfcheck=l['selfcheck'], throughput=l['throughput'],
                   cpu=l['cpu'], heartbeat=l['heartbeat'],
                   score=l['score'], uptime=l['uptime'],
                   total_throughput=l['total_throughput'],
                   enabled=l['enabled'], is_exit=l['is_exit'])

    @classmethod
    def auth(cls, name, key):
        apikey = APIKey.auth(key, name=name)
        node = cls.get(name)
        if not node:
            raise ValueError("Not a VPN server")
        return node

    
    @classmethod
    def new(cls, name, ip, is_exit=False):
        lb = cls.get(name)
        if lb:
            raise ValueError("Loadbalancer already exists")
        try:
            IPAddress(ip)
        except AddrFormatError:
            raise ValueError("ip")
        newnode = cls(name, ip, is_exit=is_exit)
        newnode.save()
        return newnode

    @classmethod
    def exists(cls, name):
        return True if cls.get(name) else False

    @classmethod
    def getall(cls):
        return [cls.get(a['name']) for a in DB.get().lb_get_all()]

    @property
    def uptime(self):
        return self._uptime

    @uptime.setter
    def uptime(self, value):
        fsm = re.compile(r"[0-9]+d [0-9][0-9]?h$")
        if not fsm.match(value.strip()):
            raise ValueError("uptime")
        self._uptime = value

    @property
    def usercount(self):
        return self._usercount

    @usercount.setter
    def usercount(self, value):
        if value < 0:
            raise ValueError("Usercount must be >= 0")
        self._usercount = value
    
    @property
    def score(self):
        s = self.usercount + int(self.cpu//10) if self.cpu < 75.0 else 100
        return s

    @property
    def alive(self):
        if not self.selfcheck:
            return False
        elif int(self.heartbeat_age) > 12*60:
            return False
        else:
            return True

    @property
    def down(self):
        # A disabled node isn't down (doesnt affect status)
        return self.enabled and not self.alive
        

    @property
    def heartbeat_age(self):
        return int(time())-self.heartbeat

    def update(self, usercount=0, selfcheck=False, throughput=0, total_throughput=0, uptime='0d 0h', cpu=0.0):
        self.usercount = int(usercount)
        self.heartbeat = int(time())
        self.selfcheck = bool(selfcheck)
        self.throughput = int(throughput)
        self.total_throughput = int(total_throughput)
        self.uptime = str(uptime)
        self.cpu = float(cpu)
        self.save()
    
    def save(self):
        DB.get().lb_save(self.name, self.ip, self.usercount,
                         self.heartbeat, self.score, self.selfcheck,
                         self.throughput, self.cpu, self.uptime,
                         self.total_throughput, self.enabled, self.is_exit)

    def deposit(self, amount, method):
        pass
        
    # :D
    def __iter__(self):
        attrs = []
        attrs.append(('name', self.name))
        attrs.append(('ip', self.ip))
        attrs.append(('score', self.score))
        attrs.append(('usercount', self._usercount))
        attrs.append(('heartbeat', self.heartbeat))
        attrs.append(('selfcheck', self.selfcheck))
        attrs.append(('heartbeat_age', self.heartbeat_age))
        attrs.append(('alive', self.alive))
        attrs.append(('throughput', self.throughput))
        attrs.append(('total_throughput', self.total_throughput))
        attrs.append(('uptime', self.uptime))
        attrs.append(('cpu', self.cpu))
        attrs.append(('enabled', self.enabled))
        attrs.append(('is_exit', self.is_exit))
        return iter(attrs)

    def __str__(self):
        return repr(dict(self))

    def __repr__(self):
        return repr(dict(self))

    def __getitem__(self, key):
        return dict(self)[key]

class Exit(object):
    def __init__(self, name, ip, comments=""):
        self.name = str(name)
        try:
            IPAddress(ip)
        except AddrFormatError:
            raise ValueError("ip")
        self.ip = str(ip)
        self.comments = str(comments)

    @classmethod
    def new(cls, name, ip, comments=""):
        """Saves a new exit_supplement"""
        if cls.get(name):
            raise ValueError("Already exists as exit")
        newexit = cls(name, ip, comments=comments)
        newexit.save()
        return newexit

    @classmethod
    def get(cls, name):
        # This object wraps the Node object, so first we check if the exit
        # exists as a Node. 
        node = Node.get(name)
        if node and node.is_exit:
            return cls(node.name, node.ip)
        
        row = DB.get().get_exit_supplement(name)
        if row:
            return cls(row[0], row[1], comments=row[2])
        else:
            return False

    @classmethod
    def getall(cls):
        # First, collect all the Nodes what are exits
        nodes = [cls(n.name, n.ip) for n in NodeList.get() if n.is_exit]

        # Then, get all exit supplements
        transform = lambda x: cls(x[0], x[1], comments=x[2]) 
        exits = [transform(a) for a in DB.get().get_all_exit_supplements()]

        return nodes + exits

    def save(self):
        # Sqlite cannot accept an IPAddress object without a binding (see #17)
        # so we cast to str. Perhaps use @property and cast implicitly?
        ip = str(self.ip)
        DB.get().save_exit_supplement(self.name, ip, self.comments)

    def __iter__(self):
        attrs = []
        attrs.append(('name', self.name))
        attrs.append(('ip', str(self.ip)))
        return iter(attrs)

    def __dict__(self):
        return  {'ip': self.ip, 'name': self.name}
    
class User(object):
    def __init__(self, username, hashed_passwd, db, **kwargs):
        """Do not construct User directly. Use User.(new|get|auth)"""
        self.username = username
        self.hashed_passwd = hashed_passwd
        self.email = kwargs.get('email', '')
        self.dl_left = kwargs.get('dl_left', 0)
        self.credit_isk = kwargs.get('credit_isk', 0)
        self.credit_btc = kwargs.get('credit_btc', 0)
        self.sub_end = kwargs.get('sub_end', "1971-04-20")
        self.db = db

    @property
    def can_buy(self):
        can_buy_isk = self.credit_isk >= SUB_PRICE_ISK
        can_buy_btc = self.credit_btc >= exchanges.btc_price()
        return can_buy_isk or can_buy_btc

    @property
    def gb_left(self):
        gb = self.dl_left/1000/1000/1000.0
        return round(gb, 2)
        
    @property
    def userdir(self):
        return os.path.join(config.clients_dir, self.username)

    @property
    def sub_active(self):
        if self.sub_end == None:
            return False
        try:
            sub_end_date = date(*map(int, self.sub_end.split('-')))
        except Exception:
            return False
        today = date.today()
        if today < sub_end_date and self.dl_left > 0:
            return True
        return False

    def save(self):
        self.db.save_user(self.username, self.hashed_passwd, self.email,
                          self.dl_left, self.credit_isk, self.credit_btc, self.sub_end)

    def buy_sub(self):
        """Attempts to buy the user some subscription. First tries to use
        credit_btc, then credit_isk. Raises NotEnoughFundsException"""

        b = self.buy_sub_btc() or self.buy_sub_isk()
        if not b:
            raise NotEnoughFundsError
        
        sub_end_date = date.today() + timedelta(SUB_LENGTH_DAYS)
        self.sub_end = sub_end_date.isoformat()
        if self.dl_left < 0:
            self.dl_left = self.dl_left + SUB_DL_BYTES
        else:
            self.dl_left = SUB_DL_BYTES


    def buy_sub_isk(self):
        if self.credit_isk < SUB_PRICE_ISK:
            return False
        self.credit_isk = self.credit_isk - SUB_PRICE_ISK
        return True

    def buy_sub_btc(self):
        price = exchanges.btc_price()
        if self.credit_btc < price:
            return False
        self.credit_btc = self.credit_btc - price
        return True

    def set_passwd(self, passwd):
        """Sets a new password from plain text."""
        if not good_password(passwd):
            raise ValueError("Bad new password")
        self.hashed_passwd = hashed(passwd)

    def mkinstaller(self):
        """Creates a /srv/clients/<name>/Lokun-install.exe for this user.

        /srv/clients/<name>/config.zip must exist.
        This method returning without exceptions does not mean the installer was
        created. Since creating an installer takes around 10 seconds, another
        process is started for it. The only thing this method does is starting
        that process and then returning without blocking.
        """
        Popen([os.path.join(config.keycontrol_dir, 'mkinstaller.py'),
               config.installer_bdir,
               os.path.join(self.userdir, 'config.zip'),
               os.path.join(self.userdir, 'Lokun-install.exe')])
        

    def mkkeys(self):
        """Creates the user's /srv/clients/<name>/config.zip"""
        exit_status = call([os.path.join(config.keycontrol_dir, 'client_keygen.py'),
                            self.username,
                            config.clients_dir,
                            config.keys_dir])
        if exit_status != 0:
            raise Exception('Could not create keys')

    @property
    def btc_addr(self):
        return BTCAddr.assign(self.username).addr
        
    @classmethod
    def auth(cls, username, passwd):
        """Like User.get except it will not let you create the user if he does
        not exist or the password is incorrect."""
        user = cls.get(username)
        if user and compare_passwd(passwd, user.hashed_passwd):
            return user
        raise ValueError("Wrong username/password combination")

    @classmethod
    def new(cls, username, passwd, invkey=None, email='', mkinstaller=True):
        """Create a brand new user.

        Saves the new user to the database, creates a config.zip for him and
        an installer."""
        if DB.get().select_user(username):
            raise ValueError("Username already taken")
        if not good_username(username):
            raise ValueError("Bad username")
        if not good_password(passwd):
            raise ValueError("Bad new password. Must be 8 characters or more.")
        hashed_passwd = hashed(passwd)
        newuser = cls(username, hashed_passwd, DB.get(), email=email)

        if invkey:
            invkey = InviteKey(invkey)
            if invkey.promo_key:
                newuser.dl_left = SUB_DL_BYTES
                newuser.sub_end = "2013-09-14"
            else:
                invkey.use()
        newuser.mkkeys()
        newuser.save()

        if mkinstaller:
            newuser.mkinstaller()
        return newuser

    @classmethod
    def exists(cls, username):
        return True if cls.get(username) else False

    @classmethod
    def get(cls, username):
        """Gets an existing user from the database or returns False if he does
        not exist."""
        db = DB.get()
        row = db.select_user(username)
        return cls(row[0], row[1], db, email=row[2], dl_left=row[3],
                   credit_isk=row[4], credit_btc=row[5], sub_end=row[6]) if row else False

    def __iter__(self):
        attrs = []
        attrs.append(('username', self.username))
        if self.email:
            attrs.append(('email', self.email))
        attrs.append(('dl_left', self.dl_left))
        attrs.append(('credit_isk', self.credit_isk))
        attrs.append(('credit_btc', self.credit_btc))
        attrs.append(('sub_active', self.sub_active))
        attrs.append(('sub_end', self.sub_end))
        attrs.append(('btc_addr', self.btc_addr))
        attrs.append(('gb_left', self.gb_left))
        attrs.append(('can_buy', self.can_buy))
        return iter(attrs)
    
class InviteKey(object):
    def __init__(self, key):
        self.key = key

    @property
    def valid(self):
        if self.promo_key:
            return True
        return DB.get().check_invite_key(self.key)

    @classmethod
    def new(cls):
        """Use to create NEW invite keys."""
        key = hashing.gen_salt(32)
        DB.get().add_invite_key(key)
        return cls(key)

    def use(self):
        DB.get().use_invite_key(self.key)

    @property
    def promo_key(self):
        return self.key in ["FBLOKUN", "VAKTINLOKUN", "RICELAND"]

class BTCPrices(object):
    def __init__(self, price):
        self.price = price

    @classmethod
    def update(cls):
        """Use to insert a new btc->isk entry."""
        # TODO: This will make the exchanges module
        # request the same info twice. This can be
        # mitigated by rewriting the exchanges module
        # to use classes, if one is so inclined.
        btc_price = exchanges.get_btc_price_live()
        btc_isk = exchanges.btc_to_isk()
        DB.get().new_btc_isk(btc_isk, btc_price)
        return cls(btc_price)
                
class BTCAddr(object):
    """A btcaddr-user combination"""
    def __init__(self, addr, usertag):
        self.addr = addr
        self.usertag = usertag

    @classmethod
    def save(cls):
        DB.get().save_btcaddrs(self.addr, self.usertag)

    @classmethod
    def new(cls, username):
        if DB.get().get_btc_addr(username):
            raise ValueError("There is already an address tagged for this user")
        addr = DB.get().tag_new_btc_addr(username)
        return cls(addr, username)
    
    @classmethod
    def assign(cls, username):
        addr = DB.get().get_btc_addr(username)
        if addr:
            return cls(addr, username)
        else:
            return cls.new(username)
        
    @classmethod
    def get(cls, addr):
        """Get an existing Addr/Usertag pairing or False """
        usertag = DB.get().get_btc_addr_tag(addr)
        return cls(addr, usertag) if usertag else False

    def rm(self):
        DB.get().rm_btc_addr(self.addr)

class APIKey(object):
    """Randomly generated keys to access in restapi.py"""
    def __init__(self, key, name, status):
        self.key = key
        self.name = name
        self.status = status

    def __attrs__(self):
        attrs = []
        attrs.append(("key", self.key))
        attrs.append(("name", self.name))
        attrs.append(("status", self.status))
        return attrs

    def save(self):
        DB.get().save_api_key(self.key, self.name, self.status)

    @property
    def good(self):
        return self.status == "good"

    @classmethod
    def new(cls, name, status="good"):
        """Create new api keys."""
        key = hashing.gen_randhex_sha256()
        newkey = cls(key, name, status)
        newkey.save()
        return newkey

    @classmethod
    def get(cls, key):
        row = DB.get().get_api_key(key)
        if not row:
            return cls(key, None, "error")
        key, name, status = row
        return cls(key, name, status)

    @classmethod
    def get_by_name(cls, name):
        rows = DB.get().get_api_key_by_name(name)
        return [cls(k[0], k[1], k[2]) for k in rows]
    
    @classmethod
    def auth(cls, key, name=""):
        """Authorize this key."""
        apikey = cls.get(key)
        if apikey.good and (name == apikey.name or not name):
            return apikey
        else:
            raise ValueError("APIKey not accepted")

# --- Password and security ---------------------------------------------------

def good_username(name):
    """Return True if name is good enough to be allowed in our system."""
    if type(name) != str and type(name) != unicode:
        return False
    if len(name) <= 1: # Just confusing
        return False
    if " " in name:
        return False    # Problems with OpenVPN scripts
    if name.lower() in ('server', 'ca', 'lokun'): # Probably some more bad words
        return False
    # Directory traversal attack and unicode. This is going to be difficult to
    # make bulletproof.
    for s in ('/', '\\', '.'):
        if s in name:
            return False
    # This should do it. BK.
    if not name.isalnum():
        return False
    return True


def good_password(passwd):
    """Return True if password is good enough to be allowed in our system."""
    # TODO: check for the world's most frequently used passwords
    if type(passwd) != str:
        return False
    if len(passwd) < 8:
        return False
    return True
        

def hashed(plain_passwd, method='sha512s', salt=None):
    """Takes in a plaintext password and returns a hash.

    The hash is a string in the format "<method>$<salt>$<hash>" where method is
    the hashing algorithm and salt is the salt for this particular password.

    Method and salt can be specified if needed. Do not specify those without a
    good reason.
    """
    try:
        hashing_func = getattr(hashing, 'hash_'+method)
    except AttributeError:
        raise ValueError('No such hash method: '+method)
    return hashing_func(plain_passwd, salt=salt)

def compare_passwd(plain_passwd, hashed_passwd):
    """Return True if hashed_passwd is plain_passwd hashed, False othervise."""
    (method, salt, _) = hashed_passwd.split('$')

    if sec.compare(hashed(plain_passwd, method=method, salt=salt), hashed_passwd):
        return True
    else:
        return False

# -- Helpers -------------------------------------------------------------------
def dict_from_row(row):
    return dict(zip(row.keys(), row))

# -- DB ------------------------------------------------------------------------

class DB(object):
    """A database ready for use (tables set up etc)."""

    def __init__(self, conn):
        """Initialize with a connection to a set-up database.

        Use DB.get() to get a DB connected to the current database in use.
        """
        self.conn = conn

    @classmethod
    def get(cls):
        conn = sqlite3.connect(config.db, timeout=20)
        return cls(conn)

    def commit(self):
        self.conn.commit()

    def save_user(self, username, hashed_passwd, email, dl_left, credit_isk, credit_btc, sub_end):
        self.conn.execute("insert or replace into user values (?, ?, ?, ?, ?, ?, ?)",
                         (username, hashed_passwd, email or '', dl_left, credit_isk, credit_btc, sub_end))
        self.commit()

    def select_user(self, username):
        c = self.conn.execute("""select username, hashed_passwd, email, dl_left, credit_isk, credit_btc, sub_end
                                 from user where username=?""", (username,))
        return c.fetchone()

    def get_api_key(self, key):
        sql = "select key, name, status from apikeys where key = ?"
        c = self.conn.execute(sql, (key, ))
        result = c.fetchone()
        return result

    def get_api_key_by_name(self, name):
        sql = "select key, name, status from apikeys where name = ?"
        c = self.conn.execute(sql, (name, ))
        return c.fetchall()
        
    def save_api_key(self, key, name, status):
        sql = "insert or replace into apikeys(key, name, status) values(?, ?, ?)"
        self.conn.execute(sql, (key, name, status))
        self.commit()

    def add_invite_key(self, key):
        self.conn.execute("insert into invitekey values (?)", (key,))
        self.commit()

    def check_invite_key(self, key):
        c = self.conn.execute("select key from invitekey where key = ?", (key,))
        return True if c.fetchone() else False

    def use_invite_key(self, key):
        if self.check_invite_key(key):
            self.conn.execute("delete from invitekey where key = ?", (key,))
            self.commit()
        else:
            raise ValueError("Invalid invite key")

    def new_btc_isk(self, btc_isk, btc_price):
        sql = "insert into btcprices(btc_isk, btc_price, timestamp) values(?, ?, ?)"
        now = datetime.now()
        self.conn.execute(sql, (btc_isk, btc_price, now))
        self.conn.commit()
    
    def save_btcaddrs(self, addr, usertag):
        sql = "update btcaddrs set and usertag=? where addr=?"
        self.conn.execute(sql, (usertag, addr))
        self.conn.commit()

    def add_btc_addr(self, addr, usertag=""):
        sql = "insert into btcaddrs(addr, usertag) values(?, ?)"
        self.conn.execute(sql, (addr, usertag))
        self.conn.commit()

    def tag_new_btc_addr(self, tag):
        sql = 'select addr, min(id) from btcaddrs where usertag=""'
        a = self.conn.execute(sql)
        addr = a.fetchone()[0]
        sql = "update btcaddrs set usertag=? where addr=?"
        self.conn.execute(sql, (tag, addr))
        self.conn.commit()
        return addr

    def get_btc_addr(self, tag):
        sql = "select addr from btcaddrs where usertag=?"
        a = self.conn.execute(sql, (tag,))
        addr = a.fetchone()
        return addr[0] if addr else "" # fuck null and None

    def get_btc_addr_tag(self, addr):
        sql = "select addr, usertag from btcaddrs where addr=?"
        a = self.conn.execute(sql, (addr,))
        usertag = a.fetchone()
        return usertag[1] if usertag else ""
    
    def rm_btc_addr(self, addr):
        self.conn.execute("delete from btcaddrs where addr=?", (addr,))
        self.conn.commit()

    def get_btc_price(self):
        sql = "select btc_price from btcprices order by id desc limit 1"
        r = self.conn.execute(sql).fetchone()
        if not r:
            raise Exception("Table btcprices empty")
        return float(r[0])

    def lb_save(self, name, ip, userc, heartb, score, selfc, throughp, cpu, uptime, total, enabled, is_exit):
        sql = """insert or replace
                 into loadbalancing(name, ip, usercount, heartbeat,
                       score, selfcheck, throughput, cpu, uptime,
                       total_throughput, enabled, is_exit)  
                 values(?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)"""
        self.conn.execute(sql, (name, ip, userc, heartb, score, selfc, throughp, cpu, uptime, total, enabled, is_exit))
        self.conn.commit()

    def lb_get(self, name):
        sql = """select name, ip, score, usercount, selfcheck, 
                        throughput, cpu, heartbeat, uptime,
                        total_throughput, enabled, is_exit
                 from loadbalancing where name=?"""
        result = self.conn.execute(sql, (name,)).fetchone()
        if result == None:
            return None
        fields = ["name", "ip", "score", "usercount", "selfcheck",
                  "throughput", "cpu", "heartbeat", "uptime",
                  "total_throughput", "enabled", "is_exit"]
        d = dict(zip(fields, result))
        return d

    def lb_get_all(self):
        cursor = self.conn.cursor()
        sql = """select name from loadbalancing"""
        result = cursor.execute(sql).fetchall() # returns list of tuples
        fields = [a[0] for a in cursor.description]
        result = [dict(zip(fields, server)) for server in result]
        cursor.close()
        return result


    def max_mailid(self):
        sql = "select max(mailid) from paymentbot"
        res = self.conn.execute(sql).fetchone()
        try:
            return int(res[0])
        except TypeError:
            return 0

    def add_mailid(self, mailid):
        sql = "insert into paymentbot(mailid) values(?)"
        self.conn.execute(sql, (mailid, ))
        self.conn.commit()


    def save_exit_supplement(self, name, ip, comments):
        sql = "insert or replace into exit_supplement(name, ip, comments) values(?, ?, ?)"
        self.conn.execute(sql, (name, ip, comments))
        self.conn.commit()

    def get_exit_supplement(self, name):
        sql = "select name, ip, comments from exit_supplement where name=?"
        c = self.conn.execute(sql, (name, ))
        return c.fetchone()

    def get_all_exit_supplements(self):
        sql = "select name, ip, comments from exit_supplement"
        c = self.conn.execute(sql)
        return c.fetchall()

def new_db(name):
    if os.path.exists(name):
        os.remove(name)
    conn = sqlite3.connect(name)
    mktables(conn)
    conn.close()


def mktables(conn):
    """Populates the db conn points at with tables."""
    c = conn.cursor()
    # Represent no email with empty string instead of null. Fuck null.
    c.execute("""create table user (
                     username text primary key,
                     hashed_passwd text not null,
                     email text not null,
                     dl_left integer not null,
                     credit_isk integer not null,
                     credit_btc real not null,
                     sub_end text not null)""")
    c.execute("""create table invitekey (key text primary key)""")
    # will be moved to lokun-billing
    c.execute("""create table apikeys (    
                     key text primary key,
                     status text not null,
                     name text)""") 
    # will probably be moved to lokun-billing
    c.execute("""create table btcprices (
                     id integer primary key autoincrement,
                     btc_isk real not null,
                     btc_price real not null,
                     timestamp datetime not null)""")
    # will probably be moved to lokun-billing
    c.execute("""create table btcaddrs (
                     id integer primary key autoincrement,
                     addr text unique,
                     usertag text not null)""")
    c.execute("""create table loadbalancing(
                     name text primary key,
                     ip text not null default "",
                     score integer not null default 0,
                     usercount integer not null default 0,
                     heartbeat integer not null default 0,
                     selfcheck integer not null default 0,
                     throughput integer not null default 0,
                     cpu real not null default 0.0,
                     uptime text not null default '0d 0h',
                     total_throughput integer not null default 0,
                     enabled integer not null default 0,
                     is_exit integer not null default 0)""")
    # will be moved to lokun-billing
    c.execute("""create table paymentbot (
                     mailid int primary key)""")
    c.execute("""create table exit_supplement(
                     name text not null default "",
                     ip text not null default "",
                     comments text not null default "")""")
    c.execute("""create table deposits (
                     date text not null default "",
                     username text not null default "",
                     amount integer not null default 0,
                     method text not null default "",
                     vsk float not null default 0.0,
                     fees integer not null default 0,
                     invoice text not null default "")""")
