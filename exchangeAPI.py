#!/bin/python
import urllib.request
import urllib.parse
import json
import hashlib
from time import sleep
import ccxt


def getCredentials(exchange_name):
    try:
        CREDENTIALS = open("credentials/%s.txt" % exchange_name).read().split('\n')
        CREDENTIALS = [x for x in CREDENTIALS if x]
        assert(len(CREDENTIALS) == 2)
    except Exception:
        print("FAILURE ON LOADING CREDENTIALS.")
        raise
    return CREDENTIALS


def initExchangeAPI(exchange_name):
    try:
        API = getattr(ccxt, exchange_name)
    except AttributeError:
        print("Fatal error - Exchange %s not detected!" % exchange_name)
        exit()

    API = API()
    K, S = getCredentials(exchange_name)
    API.apiKey = K
    API.secret = S

    return API
