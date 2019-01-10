#!/bin/python
from multiprocessing import Pool, Manager

from .evaluateCandlestick import _criteriaGrid, Think
from .utilsFunctions import *
from .constants import *
import numpy as np
import datetime

def CalibrateCriterionBruteForce(HistoryData, Verbose, AllVerbose=0,
              MultiCandlestick=0, CriteriaSimultaneousValidation=2,
                                 AsyncPool=1): # METHOD PRETTY MUCH USELESS;
    startingTime = datetime.datetime.now()
    bestValue = 0
    Text = ""
    bestCriterion = {}
    bestHistoryOfTransactions = []

    #assert(type(HistoryData) == np.ndarray)
    if not MultiCandlestick:
        HistoryData = [ HistoryData ]

    # Compatible with numpy?
    #HistoryData = np.array(HistoryData)
    
    # Restrain the data;
    #HistoryData = HistoryData[1800:]
    bestCriterion = { 'ProfitValue': 100 }
    #print(HistoryData)
    HistoryData = np.array(HistoryData)

    IterationRanges = [
                       list(itertools.combinations(_criteriaGrid['buyCriteria'],
                                                   r=CriteriaSimultaneousValidation)),
                       list(itertools.combinations(_criteriaGrid['sellCriteria'],
                                                   r=CriteriaSimultaneousValidation))
                       ]
    PrimaryIterator = list(itertools.product(*IterationRanges))
    criteriaList = _criteriaList

    print("Calibrating...")
    PrimaryIteratorLenght = len(PrimaryIterator)
    PrimaryIteratorIndex = 0

    for Combo in PrimaryIterator:
        p = Pool()
        m = Manager()
        q = m.Queue()
        PrimaryIteratorLenght +=1
        IteratorCount = 0
        CreateProcess = p.apply_async if AsyncPool else p.apply       
        PrimaryComboSimulationResults = []
        
        BaseTestCriterion = {
            "WindowSize": 8,
            "ProximalBreak": 6,
            "buyCriteria": [list(Combo[0])],
            "sellCriteria": [list(Combo[1])]
            }

        CriteriaSet = getCriteriaSet(BaseTestCriterion)
        secondaryValuesRanges = [ [ x/_criteriaParameterRatio for x in criteriaList[x][1] ] for x in CriteriaSet ]

        SecondaryIterator = itertools.product(*secondaryValuesRanges)
        for SecondaryCombo in SecondaryIterator:
            TestCriterion = deepcopy(BaseTestCriterion)
            for INDEX in range(len(SecondaryCombo)):
                AttributeName = criteriaList[CriteriaSet[INDEX]][0]
                if AttributeName:
                    TestCriterion[AttributeName] = SecondaryCombo[INDEX]

            R = []
            for C in range(len(HistoryData)):
                assert(type(HistoryData[C]) == np.ndarray)
                R.append(CreateProcess(SimulateCriterion,
                                       (HistoryData[C], deepcopy(TestCriterion)),
                                       { 'QueueData':(q, IteratorCount),
                                         'Verbose': AllVerbose,
                                         'LogTransactions': not MultiCandlestick } ))
                IteratorCount += 1
            PrimaryComboSimulationResults.append(R)
            
        print("Multiprocessing pool %i of %i. Running %i simulations.\n" % (PrimaryIteratorIndex, PrimaryIteratorLenght, IteratorCount) )

        doneCount = 0
        checkTime = log(IteratorCount)
        while not doneCount >= IteratorCount:
            sleep(checkTime)
            doneCount = q.qsize()
            print("%.2f%%" % (doneCount/IteratorCount*100))

        p.close()
        p.join()
        print("")

        for RESULT in PrimaryComboSimulationResults:
            for R in range(len(RESULT)):
                if not type(RESULT[R]) == list:
                    RESULT[R] = RESULT[R].get()
            #if Verbose and RESULT[0][1]:
            #    print(RESULT)
            EvaluatedScore = sum([x[0] for x in RESULT]) / len(RESULT)
            #EvaluatedScore = RESULT[0][0]
            if EvaluatedScore > bestCriterion['ProfitValue']:
                Denied = False
                for R in RESULT:
                    if R[0] < 100:
                        Denied = True
                if Denied:
                     print("Denied by bad result.")
                     continue

                if RESULT[0][4]:
                    NT, TL = evaluateCriterionPrecision(RESULT[0][4])
                    if TL/2 > (EvaluatedScore - 100):
                        continue
                    if NT * 2 > RESULT[0][1]/1.3:
                        continue

                bestCriterion = RESULT[0][3]
                bestCriterion['ProfitValue'] = EvaluatedScore
                bestCountTotalWindows = RESULT[0][2]
                bestCountTransactions = sum([x[1] for x in RESULT])
                bestCriterion['TransactionProbability'] =\
                        bestCountTransactions/len(HistoryData)/bestCountTotalWindows
                bestCountAverageTransactions =\
                        bestCountTotalWindows * bestCriterion['TransactionProbability']
                bestHistoryOfTransactions = RESULT[0][4]

    if bestHistoryOfTransactions:
        for Transaction in bestHistoryOfTransactions:
            _color = 'red' if 'buy' in Transaction else 'green'
            Transaction = "%s    %s %.3f   %.1f  %i" % (tuple(Transaction))
            printColored(Transaction, _color)
            print("")
        Count, Loss = evaluateCriterionPrecision(bestHistoryOfTransactions)
        print("Unprofitable %i, TotalLoss = %i" % (Count, Loss))

    elapsedTime = datetime.datetime.now() - startingTime
    calibrationTotalWindow = bestCountTotalWindows / 60 / 24
    writeLog("Calibrated @ %i      %i seconds (%.3fs per unit). " %\
             (bestCriterion['ProfitValue'],
              elapsedTime.seconds,
              elapsedTime.seconds/IteratorCount) +\
             "Transacted %i of %i searches." %\

             (bestCountAverageTransactions,
              bestCountTotalWindows) )
    
    print("Simulated timeframe corresponds to %.2f days" % calibrationTotalWindow)
    writeLog(showCriterion(bestCriterion, False))

    bestCriterion['info'] = {'TotalWindowCount': bestCountTotalWindows,
                             'SimultaneousValidation': CriteriaSimultaneousValidation,
                             }
    return bestCriterion


def SimulateCriterion(DATA, Criterion,
                      QueueData=None, TimeStep=1, Verbose=0, LogTransactions=0, FlagBank={}):
    ProximalBreak = Criterion['ProximalBreak']
    WindowSize = Criterion['WindowSize']

    wallet = Wallet()
    wallet.COIN = {'btc':0}
    wallet.USD = 100

    HistoryOfTransactions = []
    ProcCount = 0
    EffectiveCount = 0
    assert(type(DATA) == np.ndarray)

    SimulationStartingPoint = max(ProximalBreak+WindowSize, 40) # GAP TO ACCOMODATE EMA CALCULATIONS;
    for k in range(SimulationStartingPoint, len(DATA), TimeStep):

        #SemiRecentValues = Filter(window, 4)
        LastCotation = DATA[k][4]
        result = Think(DATA[:k], [], Criterion, 'btc', wallet, Logger=Verbose, FlagBank=FlagBank)

        DATE = datetime.datetime.fromtimestamp(DATA[k][0]/1e3)
        ProcCount += 1
        if result:
            EffectiveCount += 1
            if result == 'buy':
                wallet.COIN['btc'] = addPercent((wallet.USD/LastCotation), -TakerTax)
                wallet.USD = 0
                wallet.stashcotation = LastCotation

            #elif LAST > SELLthreshold and BTC:# and Flag['sell'] > 0:
            elif result == 'sell':
                wallet.USD = addPercent((wallet.COIN['btc'] * LastCotation), -TakerTax)
                wallet.COIN['btc'] = 0
                wallet.stashcotation = 0
                # to clarify the history;
            #wallet.show()
            if LogTransactions:
                HistoryOfTransactions.append([str(DATE), result, wallet.netWorth({'btc':LastCotation}), LastCotation, k] )
            
    NetWorth = wallet.netWorth( {'btc': DATA[-1][4]} )
    if Verbose:
        print("End of simulation."+\
              " Got $%.3f and B$%.3f    ($%.3f)       bb %.1f       sb %.1f" %\
              (wallet.USD,
               wallet.COIN['btc'],
               NetWorth,
               Criterion['BuyThreshold'],
               Criterion['SellThreshold']))
    if QueueData:
        q, c = QueueData
        q.put(c)
        
    return [NetWorth, EffectiveCount, ProcCount, Criterion, HistoryOfTransactions]
