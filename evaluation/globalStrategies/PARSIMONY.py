#!/bin/python

from . TransactionPlan import TransactionPlan

class GlobalStrategy():
    def __init__(self):

        self.switch_threshold = 30
        self.enter_threshold = 30
        self.exit_threshold = 40

    def __call__(self, Coins):
        coinScores = [Coin.TransactionScore for Coin in Coins]
        activeCoins = sorted([Coin for Coin in Coins if Coin.Active])

        TP = TransactionPlan()
        # Are we long in any coin?
        if activeCoins:
            activeCoin = activeCoins[0]
            # LocalStrategy suggests exiting the active coin?
            if activeCoin.TransactionScore < 0:
                if -activeCoin.TransactionScore + max(coinScores) > self.switch_threshold:
                    TP.Operation = 'sell'
                    TP.Coin = activeCoin
                    return TP
                elif -activeCoin.TransactionScore > self.exit_threshold:
                    TP.Operation = 'sell'
                    TP.Coin = activeCoin
                    return TP

        else:
            if max(coinScores) > self.enter_threshold:
                TP.Operation = 'buy'
                TP.Coin = Coins[coinScores.index(max(coinScores))]
                return TP

        return None
