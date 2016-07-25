# coding: utf8
import os
import base64
import hashlib
import hmac

import config

"""Hashing methods.

All code that performs actual hashing should be a hashing method. A hashing
method is a function named "hash_<name-of-method>" and accepts the parameters:
passwd -> the string to hash
salt=None -> OPTIONAL salt to use. If not given, the hashing method must create a
             sufficiently good one.
"""


def hash_sha512s(passwd, salt=None):
    """A sha512 hash that includes an additional static salt stored outside
    of the database."""
    salt = salt or gen_salt()
    passwd = passwd.encode('utf-8')
    hash_ = hashlib.sha512(config.sha512s_static_salt + salt + passwd).digest()
    hash_ = base64.b64encode(hash_)
    return 'sha512s$'+salt+'$'+hash_

def gen_salt(length=16):
    """Generates a base64 encoded pseudo-random string, secure enough for
       crypto use. Length is in bytes. Intended for generating salts, hence
       the name."""
    return base64.b64encode(os.urandom(length))

def gen_randhex_sha256():
    """Generates a printable pseudo-random string, secure enough for
       crypto use."""
    return hashlib.sha256(os.urandom(256/8)).hexdigest()

