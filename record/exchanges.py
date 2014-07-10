# -*- coding: utf-8 -*-

"""A home-cooked library for determining prices in BTC, from ISK.
These things tend to be down, so i have three alternatives. I convert
from BTC <-> EUR <-> ISK and I try not to rely on mtgox. 
I use apis.is to get information from Arion Banki on EUR<->ISK rates. 

The website or record shouldn't pull prices directly from here since
it requires waiting for two web APIs. We'll have a daily-updated table
in our sqlite.

Ignores the fact that buy and sell rates are different. :)
"""

import requests
import config
import model

coinbase = "https://coinbase.com/api/v1/currencies/exchange_rates"
bitcoincharts = "http://api.bitcoincharts.com/v1/markets.json" # 26
arion = "http://apis.is/currency/arion" # 3

def get_eur_value():
    # Calls an API
    j = requests.get(arion).json()
    return float(j['results'][3]['value'])
    #return 159.0

def isk_to_eur(isk=1.0):
    eur_value = get_eur_value()
    return isk / eur_value

def eur_to_isk(eur=1.0):
    eur_value = get_eur_value()
    return eur * eur_value

def get_btc_value():
    # Calls an API
    """in EUR"""
    if config.default_exchange == "coinbase":
        j = requests.get(coinbase).json()
        return float(j['btc_to_eur'])

    if config.default_exchange == "bitcoincharts":
        j = requests.get(bitcoincharts).json()
        return float(j[26]['avg'])
    else:
        raise ValueError("No exchange")
    
def eur_to_btc(eur=1.0):
    btc_value = get_btc_value()
    return eur / btc_value

def btc_to_eur(btc=1.0):
    btc_value = get_btc_value()
    return btc * btc_value
    
def isk_to_btc(isk=1):
    return eur_to_btc(isk*isk_to_eur())

def btc_to_isk(btc=1):
    return eur_to_isk(btc*btc_to_eur())

def get_btc_price():
    return get_btc_price_cached()

def get_btc_price_live():
    """Fetches the current exchange rates from API's. (IO Wait, socket)"""
    
    return config.isk_price * isk_to_btc()

def get_btc_price_cached():
    """Fetch the current BTC price for Lokun from the DB."""

    return model.DB.get().get_btc_price()

def btc_price():
    """This is what everything uses"""
    return float("%.2f" % get_btc_price())
