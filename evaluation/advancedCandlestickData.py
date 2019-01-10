#!/bin/python

import numpy as np
import random
from candlestickDatabase import *
from .evaluateCandlestick import *
from .evaluateCandlestick import _criteriaList
from .flagBankOperators import *
from .calibration import SimulateCriterion
from .constants import *
from copy import deepcopy
from plotData import *

def printmaxMinData(MaxMin):
    for k in MaxMin.keys():
        m= "%s%s" % (k, (20-len(k)) * ' ')
        for t in ['max','min','med']:
            V = "%.4f" % MaxMin[k][t]
            m += "%s%s" % (V, (20-len(V)) * ' ')
        print(m)
    print()

def candlestickRunStatistics(multipleCandlesticks, Verbose=False): #TODO: GENERATE CANDLESTICK BANK AS SEPARATE FUNCTION;
    #print(H)
    #print("Transaction Count: %i" % len(H))
    #print('\n'.join([str(x)for x in F]))
    #print("Final NetWorth: %.3f" % H[-1][2])

    criteriaNameList = [ x[0] for x in _criteriaList if x ]
    initMaxMin = lambda: { x: {'max': 0, 'min': 0, 'med': 0} for x in criteriaNameList if x }
    initCriteriaCounter = lambda: { x: {'buy': 0, 'sell': 0} for x in criteriaNameList if x }

    buyMaxMin, sellMaxMin = initMaxMin(), initMaxMin()
    criteriaSetList = {'buy':{}, 'sell':{}}
    criteriaFailSetList = deepcopy(criteriaSetList)
    criteriaCounter = initCriteriaCounter()
    flagBank = {'buy': {'success': [], 'fail': []}, 'sell': {'success': [], 'fail': []}}
    AllMedian = True
    FullHistory = True

    MedWeight = 0
    DataCount = 0
    for DATA in multipleCandlesticks:
        DataCount += 1
        print("%i/%i ... bs %i   ss %i   bf %i  sf %i" % (DataCount, len(multipleCandlesticks),
                                                        len(flagBank['buy']['success']),
                                                        len(flagBank['sell']['success']),
                                                        len(flagBank['buy']['fail']),
                                                        len(flagBank['sell']['fail'])))
        H, F=createPerfectCandlestickRun(DATA, getNullCriterion(WS=32),FullHistory=FullHistory)
        for hh in range(len(H)):
            Action = H[hh][1]
            #print(H[hh])
            #print(F[hh])
            #print("")
            criteriaSet = [ criteriaNameList.index(x) for x in F[hh] if F[hh][x] > 0 ]
            if H[hh][5]:
                appendToSerialFlagList(flagBank[Action]['success'], F[hh])
                try:
                    criteriaSetList[Action][str(criteriaSet)] += 1
                except:
                    criteriaSetList[Action][str(criteriaSet)] = 1
                for FLAG in F[hh]:
                    if F[hh][FLAG] > 0:
                        criteriaCounter[FLAG][Action] += 1
                    if F[hh][FLAG] > 0 or AllMedian:
                        if H[hh][1] == 'buy':
                            buyMaxMin[FLAG]['med'] = (buyMaxMin[FLAG]['med'] * MedWeight + F[hh][FLAG])/ (MedWeight+1) 
                            buyMaxMin[FLAG]['max'] = max(F[hh][FLAG], buyMaxMin[FLAG]['max'])
                            buyMaxMin[FLAG]['min'] = min(F[hh][FLAG], buyMaxMin[FLAG]['min'])

                        else:
                            sellMaxMin[FLAG]['med'] = (sellMaxMin[FLAG]['med'] * MedWeight + F[hh][FLAG])/ (MedWeight+1)  
                            sellMaxMin[FLAG]['max'] = max(F[hh][FLAG], sellMaxMin[FLAG]['max'])
                            sellMaxMin[FLAG]['min'] = min(F[hh][FLAG], sellMaxMin[FLAG]['min'])

                MedWeight += 1
            else:
                appendToSerialFlagList(flagBank[Action]['fail'], F[hh])
                try:
                    criteriaFailSetList[Action][str(criteriaSet)] += 1
                except:
                    criteriaFailSetList[Action][str(criteriaSet)] = 1

    if Verbose:
        print("BUY medians:")
        printmaxMinData(buyMaxMin)
        print("SELL medians:")
        printmaxMinData(sellMaxMin)
        print(criteriaCounter)

        for SetList in [criteriaSetList, criteriaFailSetList]:
            for x in SetList.keys():
                for z in SetList[x].keys():
                    print("%s: %i" % (z, SetList[x][z]) )
                print("")
            print('\n')

    return flagBank

def TEST(DATA, BANK):
    _DATA = np.array(DATA)
    result=SimulateCriterion(_DATA, getNullCriterion(WS=22), FlagBank=BANK)
    print(result)

if __name__ == '__main__':
    DATA = loadCandlestickFromDatabase(MaximumEntries=100)
    print(len(DATA))
    random.shuffle(DATA)
    cut = len(DATA)//2
    bankDATA = DATA[:cut]
    testDATA = DATA[cut:]
    BANK=candlestickRunStatistics(bankDATA)

    for Y in range(len(testDATA)):
        print("Test data of lenght %i" % len(testDATA))
        D = testDATA[Y]
        TEST(D, BANK)
