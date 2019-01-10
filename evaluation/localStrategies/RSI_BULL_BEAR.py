#!/bin/python

import tulipy as ti
import numpy as np


class Strategy():
    def __init__(self):
        self.slow_sma_period = 50
        self.fast_sma_period = 20

        self.bear_rsi_period = 15
        self.bull_rsi_period = 10

        self.bear_score_adjust = 40

        self.bull_score_adjust = 70

    def __call__(self, Coin):
        CloseValues = np.array([c[3] for c in Coin.Candlesticks[-(self.slow_sma_period + 20):]])

        if CloseValues.shape[0] < self.slow_sma_period:
            return 0

        slow_SMA = ti.sma(CloseValues, period=self.slow_sma_period)[-1]
        fast_SMA = ti.sma(CloseValues, period=self.fast_sma_period)[-1]

        # BEAR TREND;
        if slow_SMA > fast_SMA:
            RSI_period = self.bear_rsi_period
            score_adjust = self.bear_score_adjust
        else:
            RSI_period = self.bull_rsi_period
            score_adjust = self.bull_score_adjust

        Period = max(1, min(RSI_period, CloseValues.shape[0] - 1))

        RSI = ti.rsi(CloseValues, period=Period)

        return max(min(100, RSI[-1] - score_adjust), -100)
