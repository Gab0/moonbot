#!/bin/python

from time import sleep
import datetime
import os
import sys
import numpy as np
import signal
import random

os.chdir(os.path.dirname(os.path.realpath(__file__)))

import exchangeAPI
from evaluation.utilsFunctions import *
from evaluation import decision

from interface.cmdparser import options, args
from interface.niceASCII import sumHorizonASCII, LOGO
from interface.interface import showSleepBar, showRunningTime,\
    printColored, showCoinHeader, showSessionProfit

from interface import interface

from watcher import ExchangeWatcher

signal.signal(signal.SIGINT, cleanExit)


def showHistory(Watcher, coin, window=1000):
    #CNY = compareToDollar("CNY")
    H = Watcher.API.fetch_ohlcv(coin, timeframe='1m')

    H = H[-window:]

    print(" -- DATE ---- TIME ---- OPEN ---- " +\
          "HIGH ---- LOW ---- CLOSE --- %%% -- OHLC")

    lastday = 123
    for d in H:
        DATE = datetime.datetime.fromtimestamp(d[0] / 1e3)
        if DATE.day != lastday:
            print("")
        VALUE = tuple([float(k) for k in d[1:5]])
        DIFFERENCE = getPercent(VALUE[1], VALUE[2])
        OHLCMEAN = sum(VALUE) / 4
        S = "%s" + " -- %.2f" * 6
        print(S % ((DATE,) + VALUE + (DIFFERENCE, OHLCMEAN)))
        lastday = DATE.day


def assertFloat(CandlestickData):
    for w in range(len(CandlestickData)):
        for t in range(len(CandlestickData[w])):
            CandlestickData[w][t] = float(CandlestickData[w][t])


def getCotations(COINS):
    Cotations = {}
    for COIN in COINS:
        Cotations = {}


def periodicCalibration(coinAPI, COINS, HistoryData):

    if options.GeneticCalibration:
        Criterion, Y = simulate(maxEPOCH=options.GeneticCalibration)
        Criterion = serializedSimulation()
        saveCriterion(Criterion, 'standardCriterion')
    elif options.BruteForceCalibration:
        if options.CalibrateFromDatabase:
            HistoryData = loadCandlestickFromDatabase(Verbose=True)

            print("Calibrating from database. %i entries loaded." %
                  len(HistoryData))
            #print([len(x) for x in HistoryData])
            w = np.array(HistoryData)
            # print(w.shape)
            del w

        #HistoryData = np.array(HistoryData)
        CriteriaSimultaneous = 3 if options.TripleSimultaneous else 2
        Criterion = CalibrateCriterionBruteForce(HistoryData,
                                                 options.BlankRun,
                                                 MultiCandlestick=options.CalibrateFromDatabase,
                                                 CriteriaSimultaneousValidation=CriteriaSimultaneous,
                                                 AsyncPool=options.AsyncPool)

    else:
        Criterion = loadStandardCriterion()

    if options.FlagBankMode or options.MakeFlagBank:
        if options.MakeFlagBank or not os.path.isfile(FlagBankFile):
            FlagBank = candlestickRunStatistics(loadCandlestickFromDatabase())
            bankfile = open(FlagBankFile, 'w')
            bankfile.write(str(FlagBank))
            bankfile.close()
        else:
            FlagBank = eval(open(FlagBankFile).read())
        Criterion = getNullCriterion(WS=32)
    else:
        FlagBank = {}

    if options.CalibrateFromDatabase or options.SaveCriterion:
        saveCriterion(Criterion)
    #if Criterion['ProfitValue'] < 101:
    #    sleep(TimeStep * 100)

    LOG = open(calibrationLog, 'a+')
    LOG.write("%s\n\n\n" % Criterion)

    writeLog("Criterion: %s" % Criterion)
    print("")

    SET = getCriteriaSet(Criterion)
    for q in range(len(SET)):
        name = _criteriaList[SET[q]][0]
        if SET[q] < 0:
            name = '!'+ name
        SET[q] = name

    showCriterion(Criterion, True, highlight=SET)
    if options.BlankRun:
        exit()
    return Criterion, FlagBank


def runMoonbot():

    ExchangeList = options.exchanges.split(',')

    print("Initializing Watchers...")

    print()

    AllWatcher = [ExchangeWatcher(E) for E in ExchangeList]
    ## --TEST AREA;




    # -- SHOW ASCII LOGO;
    LOGO_COLOR = ['dark_orange_3a', 'purple_1b', 'gold_3a']
    Logo = sumHorizonASCII(LOGO, [7, 0, 6])
    printColored(Logo, random.choice(LOGO_COLOR))

    # -- INIT EMAIL NOTIFICATION CLIENT;
    '''
    if options.mail:
        try:
            Watcher.mailClient = emailClient()
        except:
            print("EMAIL SETUP FATAL ERROR!" + str(sys.exc_info()))
            Watcher.mailClient = None
    else:
        Watcher.mailClient = None
    '''

    if options.ShowStartupCandlestick:
        for COIN in COINS:
            showHistory(Watcher, COIN)
            print("")

    exchangePortal = "OKCoin International"
    writeLog("\nSession at %s\n" % exchangePortal)

    #D = importCandlestickData(coinAPI, 'USDT_BTC',
    #                          datetime.datetime.timestamp(datetime.datetime.now()))

    print("Online.")
    # -- APP MAIN [INFINITE] LOOP;
    downloadHistory = False
    autoCalibrationOn = False
    HistoryData = []
    for T in range(int(1e15)):
        for Watcher in AllWatcher:
            # -- DOWNLOAD HISTORY DATA;
            if downloadHistory and not T % 2700:
                for COIN in Watcher.Coins:
                    print("%s candlestick data to database." % COIN)
                    HistoryData = Watcher.API.fetch_ohlcv(COIN, timeframe='1m')
                    assertFloat(HistoryData)
                    saveCandlestickToDatabase(HistoryData, datetime.datetime.now())
                print("")

            # -- AUTOMATIC CALIBRATION;
            if autoCalibrationOn and not T % calibrationWindow: # Launch calibration routines;
                Watcher.Criterion, Watcher.FlagBank = periodicCalibration(Watcher.API, Watcher.Coins, HistoryData)

            # -- Begin of round evaluation routines;
            print("round nb %i\n" % (T + 1))

            # -- GET INDIVIDUAL CANDLESTICKS;
            Watcher.updateMarketValues()

            if not T:
                Watcher.enterzeroMarketValues = Watcher.freezeCotations()


            # -- CALCULATE AND SHOW SESSION PROFIT;
            sessionProfitPercent = getPercent(Watcher.netWorth, Watcher.timezeroNetWorth)
            showSessionProfit(sessionProfitPercent)

            # Losing money? Safety measure;
            if sessionProfitPercent < -2:
                Watcher.panicExit()

            # Show market limit orders;
            Watcher.showAllMarketOrders()

            print("")

            # print BRL info;
            #if not T % 30:
            #    BRL_cotation=coinAPI.compareToDollar("BRL")
            #BRL_value = Watcher.netWorth * BRL_cotation
            #print("Got R$%.3f @ R$%.3f/USD" % (BRL_value, BRL_cotation))

            # print running time info;
            showRunningTime(Watcher.zerotime, datetime.datetime.now())

            print("")
            print("")

            if Watcher.Wallet.stashcotation:
                PROFIT = Watcher.Wallet.COIN * SELL
                PROFIT -= Watcher.Wallet.COIN * Watcher.Wallet.stashcotation
                print("if sold now, the stash bought @" +
                                 "%.2f would profit %.2f" % (Watcher.Wallet.stashcotation,
                                                             PROFIT))

            if Watcher.Wallet.getAllMarketOrders():
                if MarketOrderWaitRounds:
                    print("Waiting order to fulfill;")
                    MarketOrderWaitRounds -= 1
                    showSleepBar(TimeStep)
            MarketOrderWaitRounds = 0

            if options.Watch:
                continue

            # --EVALUATE MARKET & THEIR ENTRY/EXIT POINTS;
            Watcher.clearMarketOrders()

            # --CLEAR ROUNDTRIP;
            Watcher.clearRoundtrip()

            # -- EVALUATE TRADING COURSE;
            decision.weightCoinScores(Watcher, options)

            forceSell = False
            if options.ImmediateSell and not T:
                forceSell = True

            decision.transactionDecision(Watcher, options, forceSell)

            interface.showTransactionRecord(Watcher.TransactionCount)
            print("")
            showSleepBar(TimeStep)


if __name__ == "__main__":
    # --CREATE REQUIRED FOLDERS;
    for folder in [DatabaseFolder, CandlePlotFolder]:
        if not os.path.isdir(folder):
            os.mkdir(folder)

    # --LAUNCH BOT;
    runMoonbot()

    # TODO:
    # MAGIC WITH API.fetch_order_book()
