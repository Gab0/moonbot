#!/bin/python
from evaluation.wallet import Wallet
import datetime
import copy
import exchangeAPI
import re

from evaluation import constants
from evaluation import localStrategies, globalStrategies

import interface

class Coin():
    def __init__(self, MarketName):
        self.MarketName = MarketName
        self.Name = self.marketNameToCoinName(MarketName)

        self.visualSymbol = self.fetchFromCoinSymbols(self.Name)
        self.fullName = self.fetchFromCoinNames(self.Name)

        self.Balance = 0
        self.frozenBalance = 0
        self.Trend = {
            'age': 9999,
            'strenght': 0
            }

        self.InaptStreak = 0

        self.Candlesticks = []

        self.TransactionScore = 0
        self.Active = False

    def feedCandle(self, Candle):
        self.Candlesticks.append(Candle)
        if len(self.Candlesticks) > 100:
            self.Candlesticks = self.Candlesticks[1:]

    def marketNameToCoinName(self, CoinName):
        return CoinName.lower().split('/')[0]

    def fetchFromCoinNames(self, CoinName):
        if CoinName in constants.CoinNames.keys():
            return constants.CoinNames[CoinName]
        else:
            print("WARNING: no coin name found for %s." % CoinName)
            return CoinName.upper()

    def fetchFromCoinSymbols(self, CoinName):
        if CoinName in constants.CoinSymbols.keys():
            return constants.CoinSymbols[CoinName]
        else:
            print("WARNING: no coin symbol found for %s." % CoinName)
            return "$%s" % CoinName.upper()


class ExchangeWatcher():
    def __init__(self, exchange_name):
        self.ExchangeName = exchange_name

        self.API = exchangeAPI.initExchangeAPI(exchange_name)

        self.API.load_markets()

        print("%s| Markets loaded." % exchange_name)

        # -- LOAD AVAILABLE COINS;
        Coins = list(self.API.markets.keys())

        Coins = [Coin(C) for C in Coins if self.filterUsableCoin(C)]

        # -- LOAD STRATEGIES;
        self.LocalStrategy = localStrategies.RSI_BULL_BEAR.Strategy()
        self.GlobalStrategy = globalStrategies.PARSIMONY.GlobalStrategy()

        self.Wallet = Wallet(self.API, Coins)

        print("%s| %i coins loaded." % (exchange_name, len(self.Wallet.Coins)))

        self.Wallet.update()

        self.TransactionCount = {
            'Created': 0,
            'Cancelled': 0
        }

        print("%s| Wallet loaded." % exchange_name)

        if self.API:
            self.updateMarketValues()

        print("%s| Market Values updated." % exchange_name)

        self.zerotime = datetime.datetime.now()
        self.zerocotations = {}

        transactionTypes = ['confirmed', 'tried', 'failed']
        self.TransactionCount = {
            T: 0
            for T in transactionTypes
        }

        self.CurrentRoundtrip = None

        self.timezeroNetWorth = self.Wallet.netWorth()

        print("%s| Net Worth weighted." % exchange_name)

        self.timezeroMarketValues = self.freezeCotations()
        self.enterzeroMarketValues = self.timezeroMarketValues

    def filterUsableCoin(self, CoinMarketName):
        if re.findall("/USD[T]$", CoinMarketName):
            return True

        return False

    def sendNotificationMail(self):
        pass

    def freezeCotations(self):
        return {
            Coin.MarketName: Coin.Candlesticks[-1][3]
            for Coin in self.Wallet.Coins
        }

    def updateMarketValues(self):
        self.Wallet.update()

        for Coin in self.Wallet.Coins:
            Candles = self.API.fetch_ohlcv(Coin.MarketName, '1m')

            for I in range(len(Candles)):
                for J in range(len(Candles[I])):
                    V = Candles[I][J]
                    if V == '.':
                        V = 0
                    else:
                        V = float(V)
                    Candles[I][J] = V

            Coin.Candlesticks = Candles

        self.netWorth = self.Wallet.netWorth()

    def panicExit(self):
        print("Financial Panic; Losing money & aborting.")
        if self.wallet.getPossibleTransactionAction(Coin) == 'sell':
            REQUEST = self.API.create_order(
                self.wallet.Coin,
                'sell', 1, price=self.LastCloseValue)

            message = "Panic sell request created."
            self.writeLog(message)
            self.sendNotificationMail(message)
            exit()

    def writeLog(self, message, DATE=False):
        pass

    def updateMulticoinPriceReference(self):
        pass

    def showAllMarketOrders(self):
        for ORDER in self.Wallet.buyOrder + self.Wallet.sellOrder:
            print("")
            interface.showMarketOrder(ORDER)

    def getBuyOrders(self):
        return self.Wallet.buyOrder + self.Wallet.sellOrder

    def clearMarketOrders(self):
        for ORDER in self.Wallet.getAllMarketOrders():
            orderID = ORDER['order_id']
            # --CANCEL STUCK ORDER;
            if ORDER['status'] != 1:
                self.writeLog("Cancelling %s" % orderID)
                print(self.API.cancel_order(orderID, symbol=ORDER['symbol']).uppder()+'/USD')
                self.TransactionCount['failed'] += 1
                if self.CurrentRoundtrip:
                    if self.CurrentRoundtrip['just'] == 'enter':
                        CurrentRoundtrip = None
                        self.enterzeroMarketValues = self.freezeCotations()
                    elif CurrentRoundtrip['just'] == 'exit':
                        CurrentRoundtrip['just'] = 'enter'
            else:
                self.writeLog("Partially Fulfilled order. Leaving it alone.")

    def clearRoundtrip(self):
        if self.CurrentRoundtrip:
            if self.CurrentRoundtrip['asset'] in self.Wallet.Coins:
                if self.CurrentRoundtrip['just'] == 'exit':
                    print('Finished roundtrip')
                    profit = getPercent(CurrentRoundtrip['exitprice'], self.CurrentRoundtrip['enterprice'])
                    deltatime = datetime.datetime.now() - self.CurrentRoundtrip['initdate']
                    deltatime = deltatime.seconds
                    if self.mailClient:
                        self.mailClient.sendMail("roundtrip on %s completed. profit: %.3f%%\n time spent: %i seconds." % (self.CurrentRoundtrip['asset'], profit, deltatime),
                                            "MOONBOT REPORT: ROUNDTRIP ENDS.")
                    CurrentRoundtrip = None
                    self.TransactionCount['confirmed']+=1
            else:
                print("Uknown roundtrip ends.")
                self.CurrentRoundtrip = None


    def selectAction(self):
        pass
