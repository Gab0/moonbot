#!/bin/python

import json


def methodOKCOIN(BaseInfo, CoinNames):
    Info = BaseInfo['info']['info']
    USD = float(Info['funds']['free']['usd'])

    fCoins = {}
    uCoins = {}
    for CNAME in CoinNames:
        fCoins[CNAME] = float(Info['funds']['free'][CNAME])
        uCoins[CNAME] = float(Info['funds']['freezed'][CNAME])

    return USD, fCoins, uCoins


def methodBINANCE(BaseInfo, CoinNames):
    Info = BaseInfo['info']
    fCoins = {}
    uCoins = {}

    WantedAsset = CoinNames[0].split("/")[-1].upper()

    for asset in Info['balances']:
        assetName = asset['asset']
        if assetName == WantedAsset:
            USD = float(asset['free'])

        assetName += '/%s' % WantedAsset
        if assetName in CoinNames:
            fCoins[assetName] = float(asset['free'])
            uCoins[assetName] = float(asset['locked'])

    return USD, fCoins, uCoins


def parseFundsInfo(BaseInfo, Coins):
    METHODS = [methodBINANCE, methodOKCOIN]

    for METHOD in METHODS:
        try:
            Data = METHOD(BaseInfo, Coins)
            # print(json.dumps(Data, indent=2))
            return Data
        except Exception:

            continue

    print("""Failed to parse info! update evaluation/ccxtExchangeFundsParser.py
    to fit current exchange.""")
    exit()
