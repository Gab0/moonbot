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
        if Coin.Candlesticks:
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
        if Watcher.timezeroMarketValues:
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

    Watcher.Wallet.update()


def transactionDecision(Watcher, options, forceSell=False):

    # print(Watcher.enterzeroMarketValues)

    action = Watcher.GlobalStrategy(Watcher)

    if action is None:
        return

    print("Making decision...")
    # PROBLEMATIC!!!
    if forceSell:
        ActiveCoins = [Coin for Coin in Watcher.Wallet.Coins if Coin.Active]
        if ActiveCoins:
            action.Operation = 'sell'
            Coin = ActiveCoins[0]

    """
    if action:
        PRICE = action.Coin.Candlesticks[-1][3]
        RelevantCandlestickData = np.array(action.Coin.Candlesticks)
        workingCotation = [] if options.StrictMode else [PRICE, PRICE]

    if action.Operation == 'inapt':
        Coin.InaptStreak += 1
        interface.printColored("Insufficient funds to enter %s.    ...%i" %
                     (Coin.fullName, Coin.InaptStreak), 'red')
    elif action:
        Watcher.writeLog("", DATE=False)
        # set price from candlestick data to on-fly latest
        # cotation;
        TransactionValue = PRICE
        refreshMessage = "Refresh cotation on transaction below; from %.3f to %.3f"

        '''
        UncertainTransaction = False


        if '!' in action:
            action = action[1:]
            UncertainTransaction = True
        '''

        if action.Operation == 'buy' and PRICE < TransactionValue:
            '''
            if UncertainTransaction:
                TransactionValue = addPercent(TransactionValue, -1)
            '''

            Watcher.writeLog(refreshMessage % (TransactionValue, PRICE))
            TransactionValue = PRICE

            CurrentRoundtrip = {
                'asset': Coin.Name,
                'enterprice': PRICE,
                'just': 'entered',
                'initdate': datetime.datetime.now()
                }

        if action.Operation == 'sell' and PRICE > TransactionValue:
            '''
            if UncertainTransaction:
                TransactionValue = addPercent(TransactionValue, 1)
            '''
            Watcher.writeLog(refreshMessage % (TransactionValue, PRICE))
            if CurrentRoundtrip:
                CurrentRoundtrip['just'] = 'exit'
                CurrentRoundtrip['exitprice'] = PRICE
            else:
                CurrentRoundtrip = {'asset': 'uknown', 'just': 'exit'}
            TransactionValue = PRICE

        if Watcher.markzeroCoinPrice:
            Ammount = {
                'buy': Watcher.Wallet.USD,
                'sell': action.Coin.Balance
            }
        else:
            Ammount = {
                'buy': 0,
                'sell': 0, 
            }
    """

    if action:
        InvolvedCoins = action.getFromToAsset()
        print(InvolvedCoins)
        #wn = Watcher.Wallet.netWorth(specificCoin=InvolvedCoins[0])
        Watcher.Wallet.updateBalance()

        action.Amount = action.Coin.Balance
        print(action.Amount)
        REQUEST = action.Execute(Watcher.API)

        Watcher.writeLog("Net Worth @ creation US$ %.4f" % Watcher.Wallet.netWorth(), DATE=True)
        Watcher.writeLog(REQUEST)
        MarketOrderWaitRounds = 3

    else:
        pass
        # Coin.InaptStreak = 0
    print("")
