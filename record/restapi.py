#! /usr/bin/env python2
# coding: utf8
import os
import json
import time 
from math import ceil

import bottle
from bottle import route, request, response, put, post, get, HTTPError, hook
from bottle import run, app, static_file, redirect
from random import shuffle, sample
from datetime import datetime
import hashlib

import config
import model
import exchanges
import requests
import hashing
import encryption
import sec
from common.logger import Logger
from dalpay import DalPay
from status import StatusState
from model import NotEnoughFundsError

logger = Logger("record")
def log(msg):
    return logger.log(msg)

@hook('after_request')
def nocache():
    response.set_header('Cache-Control', 'no-cache')

def errstatus(e, alternative=400):
    errstatuses = {
        "Wrong username/password combination": 401,
        "Invalid key/name combination": 401,
        "Invite key not valid": 403,
        "Not a VPN server": 403,
        "Username already taken": 403,
        "Bad new password": 400,
    }
    if str(e) in errstatuses:
        response.status = errstatuses[str(e)]
        return errstatuses[str(e)]
    return alternative


def abort(status, text):
    """Like bottle.abort but json."""
    r = bottle.HTTPResponse(json.dumps({'error': text, 'status': status}))
    r.content_type = 'application/json'
    r.status = status
    raise r

def key_auth(name=""):
    """Authenticates a API key."""
    if not 'secret' in request.forms:
        abort(401, "Must include a secret")
    try:
        return model.APIKey.auth(request.forms['secret'], name=name)
    except ValueError as e:
        abort(403, "Secret not accepted")    

# ------------
# /users/
# ------------

def auth(name):
    if not 'password' in request.forms:
        abort(400, "Must include a password")
    try:
        return model.User.auth(name, request.forms['password'])
    except ValueError as e:
        abort(errstatus(e), e.message)


@put('/users/<name>')
def putuser(name):
    if not 'password' in request.forms:
        abort(400, "Must include a password")
    if model.User.exists(name):
        try:
            user = auth(name)
            if request.forms.newpassword:
                user.set_passwd(request.forms['newpassword'])
            if request.forms.email:
                user.email = request.forms.email
        except ValueError as e:
            errstatus(e)
            log(str(e))
            return {'error': e.message}
    else:
        try:
            user = model.User.new(name, request.forms['password'],
                                  request.forms.invite_key,
                                  email=request.forms.email)
            log("Created a new user")
        except ValueError as e:
            errstatus(e)
            log(str(e))
            return {'error': e.message}
    return dict(user)


@post('/users/<name>')
def getuser(name):
    """This is POST only because GET shows passwords in url."""
    user = auth(name)
    return dict(user)


@post('/users/<name>/config.zip')
def getconfig(name):
    user = auth(name)
    log("Served config for a user")
    return static_file('config.zip',
                       root=user.userdir,
                       mimetype='application/zip',
                       download='config.zip')

@post('/users/<name>/btcaddr')
def getbtcaddr(name):
    user = auth(name)
    log("Assiging a btc addr to a user")
    return {'btc_addr': user.btc_addr}
    
@post('/users/<name>/Lokun-install.exe')
def getexe(name):
    user = auth(name)
    log("Served exe for a user")
    return static_file('Lokun-install.exe',
                       root=user.userdir,
                       mimetype='application/octet-stream',
                       download='Lokun-install.exe')

@post('/users')
def postusers():
    if not 'username' in request.forms:
        abort(400, "Must include a username")
    name = request.forms.username
    return putuser(name)


# -------------
# /vpn/
# -------------

@post('/vpn/<name>/sub')
def vpn_sub(name):
    """Check if sub is active, try to buy if not. 

    The "extra" form parameter is for checking on users that have live
    connections and have used bandwidth that will not be reported
    until they disconnect.
    """
    keyinfo = key_auth()
    user = model.User.get(name)
    if not user:
        # Since the API requires keys, this is okay.
        abort(404, "User not found")

    if 'extra' in request.forms:
        extra = int(request.forms['extra'])
    else:
        extra = 0

    if user.sub_active and user.dl_left > extra:
        log("VPN access granted for a user on ({0})".format(keyinfo.name))
        return {'sub_status': 'True',
                'updated': 'False'}
    try:
        user.buy_sub()
        user.save()
        log("VPN access granted and charged for a user ({0})".format(keyinfo.name))
        return {'sub_status': 'True',
                'updated': 'True'}
    except NotEnoughFundsError as ex:
        log("VPN access denied for a user on {0}".format(keyinfo.name, str(ex)))
        return {'sub_status': 'False'}

@post('/vpn/<name>/report')
def vpn_report(name):
    keyinfo= key_auth()
    user = model.User.get(name)
    if not 'dl' in request.forms:
        abort(400, "Must include dl")
    dl = int(request.forms['dl'])
    if dl < 0:
        abort(400, "dl must be >= 0")
    user.dl_left = user.dl_left - dl
    user.save()
    log("Report for a user recieved (user disconnected from {0})".format(keinfo.name))
    return {}

#----------
# /nodes/
#----------
def node_auth(name):
    """Authorizes and _Authenticates_ a VPN node.

    Used when a node reports its health Used for correctness,
    a VPN node can only report its own health.""" 
    if not 'secret' in request.forms:
        abort(400, "Must include a secret")
    try:
        return model.Node.auth(name, request.forms['secret'])
    except ValueError as e:
        abort(errstatus(e), e.message)

@post('/nodes')
def getallnodes():
    key_auth()
    nodes = lambda nl: [dict(node) for node in nl]

    if not request.params.filter or request.params.filter == "all":
        return {'data': nodes(model.NodeList.get()) }    
    elif request.params.filter == "best":
        return {'data': nodes(model.NodeList.best()) }
    elif request.params.filter == "alive":
        return {'data': nodes(model.NodeList.best()) }
    elif request.params.filter == "down":
        return {'data': nodes(model.NodeList.down()) }
    elif request.params.fitler == "disabled":
        return {'data': nodes(model.NodeList.disabled()) }
    else:
        abort(400, "Invalid filter")

@post('/nodes/<name>')
def postnode(name):
    node = node_auth(name)
    heartbeat = int(time.time())
    old_usercount = int(node.usercount)
    try:
        # coercing the types since sqlite doesn't give a shit
        # about types
        usercount = int(request.forms['usercount'])
        node.cpu = float(request.forms['cpu'])
        node.usercount = int(request.forms['usercount'])
        node.heartbeat = heartbeat
        node.selfcheck = request.forms['selfcheck'].lower() == "true" 
        node.throughput = int(request.forms['throughput'])
        node.total_throughput = int(request.forms.total_throughput)
        node.uptime = request.forms.uptime
        node.save()
    except (ValueError, KeyError) as error:
        abort(400, str(error))

    return {'status': 'ok',
            'userdiff': node.usercount - old_usercount,
            'score': node.score,
            'heartbeat': heartbeat}


@put('/nodes/<name>')
def putnode(name):
    if 'ip' not in request.forms:
        abort(400, "Must include IP address")
    if model.Node.exists(name):
        try:
            log("Changed IP for a node")
            node = node_auth(name)
            node.ip = request.forms["ip"]
            node.save()
            return dict(node)
        except ValueError as e:
            errstatus(e)
            return {'error': e.message}
    else:
        try:
            node = model.Node.new(name, request.forms["ip"])
            apikey = model.APIKey.new(name, status="new")
            log("Created a new node. API key status set to 'new'")
            return dict({'secret': apikey.key}, **dict(node))
        except ValueError as e:
            errstatus(e)
            return {'error': e.message}
    return {}

# ---------------
# /lokun/
# ---------------
@get('/lokun/loadbalancer')
def loadbalancer():
    try:
        count = int(request.params.count or 1)
        rurals = model.NodeList.best(n=count)
        simplelist = [{"ip": a['ip'], "name": a['name']} for a in rurals]
        return {'data': simplelist}
    except ValueError:
        return {'data': []}

@get('/lokun/exits')
def exits():
    response.content_type="application/json"
    ips = ['46.149.23.163',   # gq account: lokun0
           '46.149.20.225',   # gq account: lokun
           '79.134.255.166',  # datacell vps vpn30
           '37.235.49.17']    # edis vps vpn20
    return {'data': ips}

@get('/lokun/connected')
def connected():
    response.set_header('Cache-Control', 'no-cache')
    lokun_exit_ips = exits()['data']
    ip = request['REMOTE_ADDR']
    connected = ip in lokun_exit_ips
    return {'connected': connected, 'myip': ip}

@route('/lokun/price')
def price():
    log("/lokun/price called")
    return {'btc_price': exchanges.btc_price(),
            'isk_price': config.isk_price}

@route('/lokun/status')
def status():
    state = StatusState.check()
    return {'status': state.status,
            'systems': state.systems}
# -----------------
# /callbacks
# -----------------
@post('/callbacks/dalpay')
def dalpay():
    try:
        passwd = request.forms["SilentPostPassword"]
        if not sec.compare(passwd, config.dalpay_passwd):
            log("DalPay: Invalid SilentPostPassword")
            abort(401, "Unauthorized")
        message = request.forms["user1"]
        dalpay = DalPay.read(message, key=config.dalpay_key)
        user = model.User.get(dalpay.username)
        if not user:
            logger.email("DalPay: Invalid username in ciphertext: " + username)
            abort(404, "User not found")
        user.credit_isk += dalpay.amount
        user.save()
        logger.email("DalPay: {0},{1}".format(dalpay.username, dalpay.amount))

        return config.dalpay_return
    except ValueError as ve:
        log(str(ve))
        # Do i need to log something more? BK 22.03.2014
        abort(500, str(ve))

@get('/callbacks/dalpay')
def getcallbacksdalpay():
    redirect("https://www.lokun.is/home")

@post('/callbacks/bitcoinmonitor')
def bitcoinmonitor():
    log("bitcoinmonitor callback called..")
    # There has to be a better way to get s_data..
    s_data = dict(request.forms).keys()[0]
    f = json.loads(s_data)
    d = f['signed_data']
    log("addr: " + f['signed_data']['address'])

    concat = ""
    for s in ['address',
              'agent',
              'amount',
              'amount_btc',
              'confirmations',
              'created',
              'userdata',
              'txhash']:
        concat += str(f['signed_data'][s])
    concat += config.bitcoinmonitor_key
    
    # why on earth whould you use md5 in a new project in 2013?
    signature = hashlib.md5(concat).hexdigest()
    if signature != f['signature']:
        log("signatures do not match")
        abort(403, "Unahtorized")

    db = model.DB.get()
    b = model.BTCAddr.get(f['signed_data']['address'])
    if not b:
        abort(400, "Invalid") 

    user = model.User.get(b.usertag)
    amount = float(f['signed_data']['amount_btc'])
    log("amount: " + str(amount))
    log("user: " + user.username)
    logger.email("Bitcoinmonitor: {0},{1}".format(user.username, amount))
    user.credit_btc += amount
    user.save()
    b.rm()
    return {}
    

# -----------------
# /bitcoinmonitor
# -----------------

@post('/bitcoinmonitor/callback')
def bitcoinmonitorcallback():
    return bitcoinmonitor()

application = bottle.app()

if __name__ == '__main__':
    run(host='0.0.0.0',
        port=8080,
        debug=True,
        reloader=True)
