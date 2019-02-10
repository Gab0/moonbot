#!/bin/python

import json


class TransactionPlan():
    def __init__(self, Coin=None, Operation=None, Price=None, Amount=None):
        self.Coin = Coin
        self.MarketName = Coin.MarketName + "/BTC"
        self.Operation = Operation
        self.Price = Price
        self.Amount = Amount

    def show(self):
        print(self.Coin)
        print(self.Operation)
        print(self.Price)

    def check(self):
        Required = [
            self.Coin,
            self.Operation,
            self.Price
        ]

        return all(Required)

    def Execute(self, API):
        Amount = self.Amount / self.Price
        print("Creating order: %s %.3f %s for %s." % (self.Operation,
                                                      Amount,
                                                      self.Coin.MarketName,
                                                      self.Price))
        Test = True

        try:
            response = API.create_order(
                self.MarketName,
                'limit',
                self.Operation,
                amount=Amount,
                price=self.Price,
                params={'test': Test}
            )
            self.Coin.OrderCount += 1
            print(json.dumps(response))
            return response

        except Exception as e:
            print(e)

    def getFromToAsset(self):
        a = self.MarketName.split("/")
        if self.Operation == 'buy':
            a = a.revers()
        return a
