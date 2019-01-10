#!/bin/python

def calculateEMA(CloseValues, TimePeriod):
    #SMA = sum(CloseValues[-TimePeriod:]) / TimePeriod
    MUL = 2 / (TimePeriod + 1)
    EMA = [ CloseValues[-TimePeriod] ]
    for k in range(1, TimePeriod):
        EMA.append((CloseValues[-TimePeriod+k] * MUL) + ( EMA[-1]*(1-MUL)))
    return EMA