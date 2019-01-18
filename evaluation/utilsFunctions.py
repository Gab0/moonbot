#!/bin/python
from colored import fg
import os
import signal
import sys
import datetime

from .constants import *
from interface.interface import printColored
from random import randrange

def getPercent(i,f):
    if i:
        return (f-i) / i * 100
    else:
        return 0

addPercent = lambda val, per: val + (per /100) * val

POSITIVE = lambda z: True if z == abs(z) else False
Filter = lambda z, idx: [ x[idx] for x in z ]

GraphicalFlags = { 'increase': "/\\",
                   "drop": "\/",
                   'HighLowForecast': 'HL',
                   'Bullish': 'BULL'
}

def getCriteriaSet(Criterion):
    AllAttributes = Criterion['buyCriteria'] + Criterion['sellCriteria']
    CriteriaSet = list(set(sum(AllAttributes, [])))
    return CriteriaSet

def trimWindow(DATA, ProximalBreak, WindowSize, TopLimit=None):
    if TopLimit:
        DATA = DATA[TopLimit-WindowSize-ProximalBreak:TopLimit]
    else:
        DATA = DATA[len(DATA)-WindowSize-ProximalBreak:]
    return DATA

def writeLog(message, DATE=True):
    F = open("moneylog", 'a')
    DATE = "%s  |    " % datetime.datetime.now() if DATE else ""
    F.write("%s%s\n" % (DATE, message))
    print(message)

def showRelevantWindow(DATA, ProximalBreak, WindowSize):
    active_colors = ['light_gray', 'yellow', 'green', 'red', 'blue']
    inactive_colors = [ 'light_gray' for k in range(5) ]

    I = 0
    StartingPoint = len(DATA)-WindowSize-ProximalBreak
    for K in range(StartingPoint, len(DATA)):
        COLORS = active_colors if I < WindowSize else inactive_colors
        Line = ""
        for C in range(len(COLORS)):
            Line += "%s %s %s " % (fg(COLORS[C]), DATA[K][C], fg('white'))
        print(Line)
        I+=1

def showCriterion(Criterion, Print, highlight=[], HighLightMap=[], showOnlyHighlight=False):
    Format = "%s%s%s|   %s"
    FullText=[]
    KEYS = Criterion.keys()

    for k in KEYS:
        Prefix=""
        if k in highlight or '!'+k in highlight:
            if '!'+k in highlight:
                Prefix='!'
            if HighLightMap:
                _color = 'green' if HighLightMap[highlight.index(Prefix+k)] else 'red'
            else:
                _color = 'green'
        else:
            if showOnlyHighlight:
                _color = None
            else:
                _color = 'white'


        #_color = HighlightColor if k in highlight else 'white'
        #if type(Criterion[k]) != tuple:
        spacer = " " * (30-len(Prefix+k))
        if _color:
            printColored(Format % (Prefix, k, spacer, str(Criterion[k])), _color)
        if not Print:
            FullText.append(Format % (Prefix, k, spacer, str(Criterion[k])))
    if not Print:
        return '\n'.join(FullText)

"""
DEPRECATED
def saveCriterion(Criterion, FileName="standardCriterion"):
    File = open(FileName, 'w')
    File.write(str(Criterion))
    File.close()


def loadStandardCriterion():
    try:
        File = open("standardCriterion").read()

        C = eval(File)
        assert(C)
    except:
        print("Failure to load standard criterion.")
        C = {
            "BuyThreshold": 1.5,
            "SellThreshold": 1.5,
            "WindowSize": 20,
            "ProximalBreak": 3,
            "DropThreshold": 0.1,
            "IncreaseThreshold": 0.1,
            "ProcessFlags": 1,
            "PeakTolerance": 1
        }
    return C
    
"""


class MarketOrder():
    def __init__(self, DATA):
        self.fromData(DATA)
        
    def fromData(self, DATA):
        self.ID = DATA['order_id']
        self.cotation = DATA['price']
        self.buysell = DATA['type']
        self.total_amount = DATA['amount']
        self.dealt_amount = DATA['deal_amount']
        self.fullfilled = bool(DATA['status'])
        
    def Show(self):
        print("Limit order of id %i. %s order." % (self.ID, self.buysell))
        print("%.4f completed of a total of %.4f. @ %.2f." % (self.dealt_amount,
                                                             self.total_amount,
                                                             self.cotation))
        
    def remove(self):
        pass# send request to remove itself.


def cleanExit(signal, frame):
    sys.exit(0)
    
def OKCoinCandlestickToTalib(npDATA):
    output = {
        'open': npDATA[:,1],
        'high': npDATA[:,2],
        'low': npDATA[:,3],
        'close': npDATA[:,4],
        'volume': npDATA[:,5]
        }
    return output
    
def dum(a):
    pass

