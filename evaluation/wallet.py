#!/bin/python

from . import constants
import time
from .ccxtExchangeFundsParser import parseFundsInfo


class Wallet():
    def __init__(self, API=None, coins=[]):
        self.API = API
        self.USD = 100

        self.Coins = coins

        self.Trend = {}

        self.CoinNames = [Coin.Name for Coin in self.Coins]

        self.stashcotation = 0
        self.buyOrder = []
        self.sellOrder = []

    def updateBalance(self):
        BaseInfo = self.API.fetch_balance()
        # print(BaseInfo)
        coinNameList = [Coin.MarketName for Coin in self.Coins]

        self.USD, Balance, frozenBalance = parseFundsInfo(BaseInfo, coinNameList)

        self.buyOrder = []
        self.sellOrder = []

        sTime = time.time()
        for c, Coin in enumerate(self.Coins):
            if Coin.MarketName in Balance.keys():
                print(Coin.MarketName)
                Coin.Balance = Balance[Coin.MarketName]
                Coin.frozenBalance = frozenBalance[Coin.MarketName]
            else:
                print("WARNING! %s not found on balance data... removing." % Coin.MarketName)
                self.Coins[c] = None

        Elapsed = time.time() - sTime
        print("Elapsed %.2f seconds to fetch balance." % Elapsed)

        self.Coins = [c for c in self.Coins if c is not None]

    def updateMarketOrders(self):
        sTime = time.time()
        ORD = self.API.fetch_open_orders(symbol=None, params={})
        if ORD:
            for ORDER in ORD:
                #O = MarketOrder(ORDER)
                O = ORDER
                if O['type'] == 'buy':
                    self.buyOrder.append(O)
                else:
                    self.sellOrder.append(O)

        Elapsed = time.time() - sTime
        print("Elapsed %.2f seconds to fetch open orders." % Elapsed)

    def show(self, Cotations, Print=True):
        message = "wallet: US$ %.4f;" % self.USD

        print([Coin.MarketName for Coin in self.Coins])
        for Coin in self.Coins:
            Balance = Coin.Balance
            if Balance:
                message += "\t%s%.6f;" % (Coin.visualSymbol, Balance)
            else:
                print("Warning! %s not found on balance data." % Coin.MarketName)

        message += "\tNetWorth US$ %.4f;" % self.netWorth(Cotations)

        print(message)

    def netWorth(self, specificCoin=None):
        if specificCoin:
            coinNetWorth = 0
            if specificCoin.Candlesticks:
                coinNetWorth = specificCoin.Candlesticks[-1][3] * (specificCoin.Balance + specificCoin.frozenBalance)
            return coinNetWorth

        NetWorth = self.USD

        for Coin in self.Coins:
            if Coin.Candlesticks:
                coinValue = Coin.Balance + Coin.frozenBalance
                coinValue *= Coin.Candlesticks[-1][3]
                NetWorth += coinValue

        return NetWorth

    def getPossibleTransactionAction(self, Coin):
        if Coin.Candlesticks:
            MoneyBuyPower = self.USD / Coin.Candlesticks[-1][3]

            # going for buy movement;
            if MoneyBuyPower > 0.01 and MoneyBuyPower > Coin.Balance:
                return 'buy'
            # going for sell movement;

            elif Coin.Balance > 0.01:
                return 'sell'
            else:
                return None

    def hasActiveOrders(self):
        R = True if (self.buyOrder + self.sellOrder) else False
        return R

    def getAllMarketOrders(self):
        return self.buyOrder + self.sellOrder

