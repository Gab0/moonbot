#!/bin/python

from indicators.EMA import calculateEMA

def calculateMACDH(CloseValues, bigEMA=26, smallEMA=12, signal=9):
    MACDLine = []
    for W in range(signal, 0, -1):
        sEMA = calculateEMA(CloseValues[:-W], smallEMA)
        bEMA = calculateEMA(CloseValues[:-W], bigEMA)
        MACD = sEMA[-1] - bEMA[-1]
        MACDLine.append(MACD)

    MACDsignalLine = calculateEMA(MACDLine, signal)
    MACDH = MACD - MACDsignalLine[-1]
    return MACDH