#!/bin/python

from interface import interface
from .utilsFunctions import addPercent, getPercent

import datetime

import numpy as np


def getCandlestick(coinAPI, CoinName):
    DATA = coinAPI.fetch_ticker(CoinName)
    if not DATA:
        return None

    DATA = DATA['info']

    candleProps = ["openPrice", "lowPrice", "highPrice", "askPrice", "volume"]

    Candle = [float(DATA[cP]) for cP in candleProps]

    return Candle


def weightCoinScores(Watcher, options):
    for c, Coin in enumerate(Watcher.Wallet.Coins):
        # Candle = getCandlestick(Watcher.API, Coin.MarketName)
        # Coin.feedCandle(Candle)

        if not Coin.Candlesticks:
            print("No Candlestick data for %s" % Coin.MarketName)
            continue

        # NO VOLUME? EXCLUDE COIN!
        if not Coin.Candlesticks[-1][-1]:
            # Watcher.Wallet.Coins[c] = None
            print("Removing %s due to zero volume!" % Coin.MarketName)
            continue

        coinNetWorth = Watcher.Wallet.netWorth(specificCoin=Coin)

        Coin.Active = False
        if coinNetWorth > Watcher.netWorth / 2:
            Coin.Active = True

        PRICE = Coin.Candlesticks[-1][3]
        Coin.TransactionScore = Watcher.LocalStrategy(Coin)

        SessionCoinPrice = getPercent(PRICE,
                                      Watcher.timezeroMarketValues[Coin.MarketName])

        EntryCoinPriceVariation = getPercent(PRICE,
                                             Watcher.enterzeroMarketValues[Coin.MarketName])
        interface.showCoinHeader(Coin,
                                 SessionCoinPrice,
                                 EntryCoinPriceVariation,
                                 Coin.Candlesticks,
                                 )

        interface.showCotations(PRICE, PRICE)
        print()

    Watcher.Wallet.Coins = [c for c in Watcher.Wallet.Coins if c is not None]


def transactionDecision(Watcher, options, forceSell=False):

    # print(Watcher.enterzeroMarketValues)

    action, Coin = Watcher.GlobalStrategy(Watcher.Wallet.Coins)

    if forceSell:
        ActiveCoins = [Coin for Coin in Watcher.Wallet.Coins if Coin.Active]
        if ActiveCoins:
            action = 'sell'
            Coin = ActiveCoins[0]

    if action:
        PRICE = Coin.Candlesticks[-1][3]
        RelevantCandlestickData = np.array(Coin.Candlesticks)
        workingCotation = [] if options.StrictMode else [PRICE, PRICE]

    if action == 'inapt':
        Coin.InaptStreak += 1
        interface.printColored("Insufficient funds to enter %s.    ...%i" %
                     (Coin.fullName, Coin.InaptStreak), 'red')
    elif action:
        Watcher.writeLog("", DATE=False)
        # set price from candlestick data to on-fly latest
        # cotation;
        TransactionValue = PRICE
        refreshMessage = "Refresh cotation on transaction below; from %.3f to %.3f"
        UncertainTransaction = False

        if '!' in action:
            action = action[1:]
            UncertainTransaction = True

        if action == 'buy' and PRICE < TransactionValue:
            if UncertainTransaction:
                TransactionValue = addPercent(TransactionValue, -1)
            Watcher.writeLog(refreshMessage % (TransactionValue, PRICE))
            TransactionValue = PRICE

            CurrentRoundtrip = {
                'asset': Coin.Name,
                'enterprice': PRICE,
                'just': 'entered',
                'initdate': datetime.datetime.now()
                }

        if action == 'sell' and PRICE > TransactionValue:
            if UncertainTransaction:
                TransactionValue = addPercent(TransactionValue, 1)
            Watcher.writeLog(refreshMessage % (TransactionValue, PRICE))
            if CurrentRoundtrip:
                CurrentRoundtrip['just'] = 'exit'
                CurrentRoundtrip['exitprice'] = PRICE
            else:
                CurrentRoundtrip = {'asset': 'uknown', 'just': 'exit'}
            TransactionValue = PRICE

        Ammount = {
            'buy': Watcher.Wallet.USD,
            'sell': Coin.Balance
        }

        if action:
            print("Creating order: %s %.3f %s for %s." % (action, Ammount[action], Coin.MarketName, TransactionValue))
            REQUEST = Watcher.API.create_order(Coin.MarketName,
                                               'limit',
                                               action,
                                               amount=Ammount[action],
                                               price=TransactionValue)

        Watcher.writeLog("Net Worth @ creation US$ %.4f" % Watcher.netWorth, DATE=True)
        Watcher.writeLog(REQUEST)
        MarketOrderWaitRounds = 3

    else:
        pass
        # Coin.InaptStreak = 0
    print("")
