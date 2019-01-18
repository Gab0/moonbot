#!/bin/python
import sys
from time import sleep
from colored import fg


def showSleepBar(Time):
    Length = 82
    Interval = Time / 82

    Fill = '.'
    Void = ' '
    Init = '|'
    End = '|'

    for k in range(Length):
        v = Length-k
        print('\r'+Init + k*Fill + v*Void + End, end="")
        sys.stdout.flush()
        sleep(Interval)
    print("")


def showRunningTime(starttime, now):
    RunningTime = now - starttime
    RTs = RunningTime.seconds
    RTd = RunningTime.days
    message = "running for %i days, " % RTd
    message += "%i hours, " % (RTs % 86400 // 3600)
    message += "%i minutes " % (RTs % 86400 % 3600 // 60)
    message += "& %i seconds." % (RTs % 86400 % 3600 % 60)

    print(message)


def showTransactionCountStatistics(TransactionCount):
    print("Limit Market Orders: ( total: %i  |  cancelled %i)" % (
        TransactionCount['Created'], TransactionCount['Cancelled']))


def showCoinHeader(Coin, varSessionCoinPrice, varEnterCoinPrice, CandlestickData):

    # First line.
    _color = 'purple_1b' if Coin.Active else 'blue'
    mainHeader = "\t\tAnalyzing %s candlesticks; vol %.2f; t %.2f"
    printColored(mainHeader % (Coin.MarketName,
                               CandlestickData[-1][5], 0),
                 _color, end='')

    scoreColor = 'green' if Coin.TransactionScore >= 0 else "dark_violet_1b"
    printColored("|> %.3f" % Coin.TransactionScore, scoreColor)

    # Second line.
    print('\t', end='')
    for P in [varSessionCoinPrice, varEnterCoinPrice]:
        _color = 'red' if P < 0 else 'green'
        printColored("%.3f%%\t" %
                     P, _color, end='')

def showTransactionRecord(TransactionRecord):
    print("Transaction Record:")
    print()

    printColored("Confirmed -> %i" % TransactionRecord['confirmed'], 'green')
    printColored("Tried -> %i" % TransactionRecord['tried'], 'yellow')
    printColored("Failed -> %i" % TransactionRecord['failed'], 'red')


def printColored(Text, Color, end='\n'):
    try:
        print("%s %s %s" % ( fg(Color), Text, fg('white') ), end=end)
    except Exception as e:
        # in some systems it crashes.
        print("%s %s %s" % ( fg(Color), Text.encode('utf-8'), fg('white') ), end=end)


def showSessionProfit(sessionProfitPercent):
    _color = 'red' if sessionProfitPercent < 0 else 'green'
    printColored("Session Profit: %.3f%%" %
                 (sessionProfitPercent), _color)


def showCotations(buy_value, sell_value, Labels=['BUY', 'SELL']):
    if buy_value:
        DIFFERENCE = abs((sell_value - buy_value)/ buy_value*100)
    else:
        DIFFERENCE = 0
    print("%s: %.4f  %s: %.4f    DIFF: %.6f%%" % (Labels[0],
                                                  buy_value,
                                                  Labels[1],
                                                  sell_value,
                                                  DIFFERENCE))


def showMarketOrder(MarketOrder):
    print("Market Order id %s" % MarketOrder['order_id'])
    print("\t %.3f of %.3f    %s" % (MarketOrder['deal_amount'],
                                     MarketOrder['amount'],
                                     MarketOrder['symbol'].split("_")[0]))

    print("\t%s @ %.3f" % (MarketOrder['type'],MarketOrder['price']))

