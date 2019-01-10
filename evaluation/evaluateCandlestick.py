#!/bin/python
import datetime
import sys
import itertools
import functools

import numpy as np

#defining NPY_NO_DEPRECATED_API NPY_1_7_API_VERSION
from .utilsFunctions import *
from .constants import *
from .wallet import Wallet
from copy import deepcopy
from time import sleep
from math import log
import random

try:
    import talib
except ImportError:
    print("Failed to import ta-lib. Some criterias are crippled.")

_addPercent = lambda value, percent: value + (percent/100) * value
_getPercent = lambda x, y: (x-y)/y * 100

#from .indicators import *
#from indicators.MACDH import calculateMACDH

StandardTopLimit = 24

StandardBottomLimit = -12
_criteriaParameterRatio = 32
_criteriaList = [
    (None, [0], "0"),
    ('Bullish', range(StandardBottomLimit, StandardTopLimit, 1),
     " getPercent(CloseValues[-1], CandlestickData[-1][1]) - Criterion['Bullish']"),
    ('Bearish', range(StandardBottomLimit, StandardTopLimit, 1),
     "getPercent(CandlestickData[-1][1], CloseValues[-1]) - Criterion['Bearish']"),
    ('Increase', range(StandardBottomLimit, StandardTopLimit, 1),
     "getPercent(Cotation, CloseValues[ELCV]) - Criterion['Increase']"),
    ('Drop', range(StandardBottomLimit, StandardTopLimit, 1),
     "getPercent(CloseValues[ELCV], Cotation) - Criterion['Drop']"),
    ('BuyThreshold', range(StandardBottomLimit, StandardTopLimit, 1),
     "addPercent(CotationMedian, -Criterion['BuyThreshold'])"),
    ('SellThreshold', range(StandardBottomLimit, StandardTopLimit, 1),
     "addPercent(CotationMedian, Criterion['SellThreshold'])"),
    ('HighPeak', range(StandardBottomLimit, StandardTopLimit, 1),
     "Cotation - addPercent(HighestClose, -Criterion['HighPeak'])"),
    ('LowPeak', range(StandardBottomLimit, StandardTopLimit, 1),
     "addPercent(LowestClose, Criterion['LowPeak']) - Cotation"),
    ("PositivePriceSlope", range(StandardBottomLimit, StandardTopLimit), ""),
    ("NegativePriceSlope", range(StandardBottomLimit, StandardTopLimit), ""),
    #('LowTrendPatterns', range(StandardBottomLimit, 4,1), ""),
    #('HighTrendPatterns', range(StandardBottomLimit, 4,1), ""),
    ('Volatility', range(StandardBottomLimit, StandardTopLimit, 1), ""),
    ('MACD Histogram', range(StandardBottomLimit, StandardTopLimit, 1), ""),
    #('Stability', range(StandardBottomLimit, StandardTopLimit, 1), "")
    ('TrendStrength', range(StandardBottomLimit, StandardTopLimit, 1), ""),
    ('DEMA', range(StandardBottomLimit, StandardTopLimit, 1), "")
]
_criteriaGrid = {'buyCriteria': [12,13,14],
                 'sellCriteria': [12,13,14]}


def Think(CandlestickData, Cotation, Criterion, Coin,
 wallet, Logger=True, getFlags=False, FlagBank={}):

    workingCotation = {}
    if Cotation:
        workingCotation['buy'], workingCotation['sell'] = Cotation 
    else:
        workingCotation['buy'] =  workingCotation['sell'] = CandlestickData[-1][4]

    #Flag = NEWreadFlags(CandlestickData, BUY, Criterion)

    BuyCheat = 0
    SellCheat = 0

    PossibleAction = wallet.getPossibleTransactionAction(Coin, workingCotation['buy'])
    if not PossibleAction:
        return 'inapt'

    #Flag = NEWreadFlags(PossibleAction, CandlestickData, BUY, Criterion)
    Flag = {}

    pB = Criterion['ProximalBreak']
    wS = Criterion['WindowSize']

    RelevantCandlestickWindow = trimWindow(CandlestickData, pB, wS)

    # Using numpy or not?

    SetOfFlags = Criterion['buyCriteria'] if PossibleAction == 'buy' else Criterion['sellCriteria']

    #assert(type(RelevantCandlestickWindow) == list)
    #OpenValues = Filter(RelevantCandlestickWindow, 1)
    #HighValues = Filter(RelevantCandlestickWindow, 2)
    #LowValues = Filter(RelevantCandlestickWindow, 3)
    #CloseValues = Filter(RelevantCandlestickWindow, 4)
    #LowestClose = min(CloseValues[:-1])
    #HighestClose = max(CloseValues[:-1])


    #'''
    #assert(type(RelevantCandlestickWindow) == np.ndarray)
    OpenValues = RelevantCandlestickWindow[:,1]
    HighValues = RelevantCandlestickWindow[:,2]
    LowValues = RelevantCandlestickWindow[:,3]
    CloseValues = RelevantCandlestickWindow[:,4]
    AllCloseValues = CandlestickData[:,4]
    LowestClose = np.amin(CloseValues[:-1])
    HighestClose = np.amax(CloseValues[:-1])
    #'''

    try:
        WindowEndPoint = len(CloseValues) - pB -1
        WindowCloseValues = CloseValues[:WindowEndPoint]
        PostWindowCloseValues = CloseValues[WindowEndPoint:]
        CotationMedian = sum(WindowCloseValues) / WindowEndPoint
    except:
        print(len(CandlestickData))
        print(CloseValues)
        print(Criterion['ProximalBreak'])
        raise

    '''
    criteriaList = _criteriaList
    G = {
        'getPercent': getPercent,
         'addPercent': addPercent
    }
    L = {
        'CloseValues': CloseValues,
         'Cotation': Cotation,
         'Criterion': Criterion,
         'WindowEndPoint': WindowEndPoint,
         'CotationMedian': CotationMedian
         }


    for K in SetOfFlags:
        if K:
            Flag[criteriaList[K][0]] = eval(criteriaList[K][2], G, L)
    '''
    TrendPatterns = {
        'HighTrendPatterns': ['CDL3LINESTRIKE', 'CDLABANDONEDBABY'],
        'LowTrendPatterns': ['CDLEVENINGSTAR', 'CDL3BLACKCROWS']
    }
    EvaluationScore = []
    for subset in SetOfFlags:
        EvaluationScore.append([])
        for K in subset:
            NotMode = False
            if K != abs(K):
                K = abs(K)
                NotMode = True
            NAME=_criteriaList[K][0]

            if K == 0:
                x=1
            elif K == 1: # BULLISH;
                x=Flag[NAME] = _getPercent(CloseValues[-1], OpenValues[-2]) - Criterion[NAME]
            elif K == 2: # BEARISH;
                x=Flag[NAME] = _getPercent(OpenValues[-2], CloseValues[-1]) - Criterion[NAME]
            elif K == 3: # INCREASE;
                x=Flag[NAME] = _getPercent(workingCotation[PossibleAction],
                                          CloseValues[-2]) - Criterion[NAME]
            elif K == 4: # DROP;
                x=Flag[NAME] = _getPercent(CloseValues[-2],
                                          workingCotation[PossibleAction]) - Criterion[NAME]
            elif K == 5: # BUY THRESHOLD;
                x=Flag[NAME] = _getPercent(CotationMedian,
                                          workingCotation[PossibleAction]) - Criterion[NAME]
            elif K == 6: # SELL THRESHOLD;
                x=Flag[NAME] = _getPercent(workingCotation[PossibleAction],
                                          CotationMedian) - Criterion[NAME]
            elif K == 7: # HIGH PEAK;
                x=Flag[NAME] = _getPercent(workingCotation[PossibleAction],
                                          HighestClose) + Criterion[NAME]
            elif K == 8: # LOW PEAK;
                x=Flag[NAME] = _getPercent(LowestClose,
                                          workingCotation[PossibleAction]) + Criterion[NAME]
            elif K in [9, 10]: # POSITIVE/NEGATIVE PRICE SLOPE;
                price_slope = functools.reduce(lambda x, y: y-x, CloseValues)
                print(CloseValues)
                price_slope -= CloseValues[0]
                price_slope /= CloseValues[-1]


                if K == 9: # POSITIVE PRICE SLOPE;
                    x=Flag[NAME] = price_slope -\
                    Criterion[NAME]
                else: # NEGATIVE PRICE SLOPE;
                    x=Flag[NAME] = -price_slope -\
                    Criterion[NAME]

            #elif K in [11, 12]: # VOLATILITY/STABILITY;
            elif K == 11: # VOLATILITY;
                WorkingRange = range(WindowEndPoint, len(CloseValues))
                WorkingRangeSize = len(WorkingRange)

                WickSizes=[ max(0.01,
                                HighValues[x]- max(OpenValues[x], CloseValues[x]) +\
                                     min(OpenValues[x], CloseValues[x]) - LowValues[x]) \
                            for x in WorkingRange ]
                CandleSizes=[ max(0.01,
                                  max(OpenValues[x], CloseValues[x]) - min(OpenValues[x], CloseValues[x])) \
                              for x in WorkingRange ]

                #print(WorkingRange)
                #print(WorkingRangeSize)
                #print(OpenValues)
                #print(CloseValues)
                # IF CANDLE SIZES ARE NULL, RESORT TO STANDARD VALUES; DIVISION WOULD FAIL.
                IndexRange = range(len(CandleSizes))

                #if K ==11: #VOLATILITY;
                vsSET = [ log(WickSizes[x]/CandleSizes[x])for x in IndexRange ]
                #else: #STABILITY;
                #    vsSET = [ log(CandleSizes[x]/WickSizes[x]) for x in IndexRange ]

                V = sum(vsSET) / len(vsSET) /100 if len(vsSET) and sum(vsSET) else 0
                x=Flag[NAME]= V - Criterion[NAME]
                if np.isinf(x):
                    print('--')
                    print('ws %s' % WickSizes)
                    print('cs %s' % CandleSizes)
                    print('vsset %s' % vsSET)

            elif K == 12: # MACDH;
                x=Flag[NAME]=calculateMACDH(AllCloseValues) - Criterion[NAME]

            elif K == 13: # TrendStrength;
                x=Flag[NAME]=calculateTrendStrenght(AllCloseValues) - Criterion[NAME]

            elif K == 14:
                shortEMA = calculateEMA(AllCloseValues, 9)[-1]
                longEMA = calculateEMA(AllCloseValues, 21)[-1]

                x=Flag[NAME]= 100 * (shortEMA - longEMA) / ((shortEMA + longEMA) / 2)
            else: # ABNORMAL INDEX;
                x=1
            '''
            elif K in [9, 10]:
                WorkingHighLow = _criteriaList[K][0]
                if WorkingHighLow in Flag.keys(): # Avoid checking twice for same candlestick patterns;
                    x=Flag[WorkingHighLow]
                else:
                    AR = OKCoinCandlestickToTalib(CandlestickData[-4:])
                    x=0
                    for FUNC in TrendPatterns[WorkingHighLow]:
                        x += sum(talib.abstract.Function(FUNC)(AR))
                    Flag[WorkingHighLow]=x
            elif K == 11:
            '''


            '''
            elif K == 9:
                RecentHighMedian = sum(HighValues[WindowEndPoint:]) / (pB+1)
                RecentLowMedian = sum(LowValues[WindowEndPoint:]) / (pB+1)
                x=Flag['HighLowForecast'] = RecentHighMedian - RecentLowMedian
            '''    
            '''
            '''
            x = -x if NotMode else x
            EvaluationScore[-1].append(x)

    # EMA CROSSOVER; TREND DETECTOR;
    TrendValidation=False
    if TrendValidation:
        if wallet.Trend[Coin.Name]['age'] > 0:
            TrendStrengthMOD = calculateTrendStrenght(AllCloseValues)

            #EMAs = [ x[-1] for x in EMAStrip ]
            #StripValues = functools.reduce(lambda x, y: y-x, EMAs) / len(EMAStrip) * TrendStrengthMOD
            wallet.Trend[Coin.Name]['strenght'] = TrendStrengthMOD
            wallet.Trend[Coin.Name]['age'] = 0
        else:
            wallet.Trend[Coin.Name]['age'] += 1

    Trend = random.random() < wallet.Trend[Coin.Name]['strenght'] if TrendValidation else True



    FlagSet = list(Flag.keys())
    EvaluationBinaries = [ [ True if x > 0 else False for x in SubsetScore ]\
                           for SubsetScore in EvaluationScore ]

    EvaluationResult = any([all(SubsetBinaries) for SubsetBinaries in EvaluationBinaries])
    SemiEvaluationResult = any([ sum(SubsetBinaries)/len(SubsetBinaries) >= 1/2 for SubsetBinaries in EvaluationBinaries])

    if Logger:
        FlagShow = [ [_criteriaList[abs(x)][0] for x in Subset ] for Subset in SetOfFlags ]
        for x in range(len(SetOfFlags)):
            for y in range(len(SetOfFlags[x])):
                if SetOfFlags[x][y] < 0:
                    FlagShow[x][y] = '!'+FlagShow[x][y]

    #print(StripValues)
    if EvaluationResult and Trend:
        Action = PossibleAction
        if Logger:
            print("Transaction granted. [%s]" % PossibleAction)
    elif SemiEvaluationResult:
        Action = '!'+PossibleAction
        if Logger:
            print("Try Transaction granted. [%s]" % Action)
    else:
        Action = None
        if Logger:
            print(EvaluationBinaries)
            print("Transaction denied. [%s]" % PossibleAction)
    if Logger:
        for k in range(len(FlagShow)):
            showCriterion(Flag, True,
                          highlight=FlagShow[k],
                          HighLightMap=EvaluationBinaries[k],
                          showOnlyHighlight=True)#True
            print("")

    if FlagBank:
        S, F=resolveActionOnSerialFlagBank(FlagBank[PossibleAction], Flag)
        if S < F:
            Action = PossibleAction
            if Logger:
                print("Flag Bank Granted.")
        else:
            Action = None
            if Logger:
                print("Flag Bank Denied.")
        if Logger: 
            print("SUCC: %.4f    FAIL: %.4f" % (S,F))

    if getFlags:
        return Action, Flag
    return Action

def evaluateCriterionPrecision(HistoryOfTransactions):
    NegativeTransactionCycleCount = 0
    TotalLossOnNegativeTransaction = 0
    for N in range(len(HistoryOfTransactions) -1):
        if HistoryOfTransactions[N][1] == 'buy':
            TransactionCycleBalance =\
                HistoryOfTransactions[N][2] - HistoryOfTransactions[N+1][2]
            if TransactionCycleBalance < 0:
                NegativeTransactionCycleCount += 1
                TotalLossOnNegativeTransaction -= TransactionCycleBalance

    return NegativeTransactionCycleCount, TotalLossOnNegativeTransaction

def getNullCriterion(PB=3, WS=8):
    AllCriteria = list(range(1, len(_criteriaList)))
    NullCriterion = { x: 0 for x in [z[0] for z in _criteriaList if z[0]]}
    NullCriterion.update( { 'buyCriteria': [AllCriteria],
                            'sellCriteria': [AllCriteria],
                            'ProximalBreak': PB, 'WindowSize': WS,
                            'TransactionProbability':0})
    return NullCriterion

def createPerfectCandlestickRun(DATA, FlagGenCriterion, FullHistory=False):
    PRE = FlagGenCriterion['ProximalBreak'] + FlagGenCriterion['WindowSize'] + 12
    D = np.array(DATA)
    CloseValues = D[:,4]

    HistoryOfTransactions=[]
    HistoryOfFlags=[]
    wallet=Wallet()

    for S in range(PRE, len(CloseValues)):
        lowBound = max(S-10,0)
        highBound = min(S+10, len(CloseValues))
        Window = CloseValues[lowBound:highBound]
        LastCotation = CloseValues[S]
        DATE = datetime.datetime.fromtimestamp(DATA[S][0]/1e3)
        Action = wallet.getPossibleTransactionAction('btc', LastCotation)
        Transaction=None
        if Action == 'buy':
            if CloseValues[S] == min(Window):
                Transaction=True
                wallet.COIN['btc'] = wallet.USD/LastCotation
                wallet.USD = 0
                wallet.stashcotation = LastCotation

        if Action == 'sell':
            if CloseValues[S] == max(Window):
                Transaction=True
                wallet.USD = wallet.COIN['btc'] * LastCotation
                wallet.COIN['btc'] = 0
                wallet.stashcotation = 0
                
        if Transaction or FullHistory:
            HistoryOfTransactions.append([str(DATE),
                                          Action,
                                          wallet.netWorth({'btc': LastCotation}),
                                          LastCotation, S, Transaction]
            )
            '''
            ThinkingWindow = trimWindow(D[:S],
                                        FlagGenCriterion['ProximalBreak'],
                                        FlagGenCriterion['WindowSize'])
            '''
            w, Flags = Think(D[:S], [], 
                             FlagGenCriterion, 'btc', wallet, Logger=False, getFlags=True)
            #print(Flags)
            HistoryOfFlags.append(deepcopy(Flags))

    return HistoryOfTransactions, HistoryOfFlags


def calculateTrendStrenght(AllCloseValues):
    TrendStripMaxPastCandlesticks = min(len(AllCloseValues), 50)
    TrendStripTimerangesList = list(range(5, TrendStripMaxPastCandlesticks, 9))

    EMAStrip = [calculateEMA(AllCloseValues, TR) for TR in TrendStripTimerangesList]
    StripSenses = [x[-1]-x[-2] for x in EMAStrip]
    StripSensesPositive = [x==abs(x) for x in StripSenses]

    # y=2abs(0.5-x) ALTERNATIVA;
    StripSameSense = sum(StripSensesPositive)/len(StripSensesPositive)
    TrendStrength = 0.5 + abs(0.5 - StripSameSense)

    return TrendStrength
