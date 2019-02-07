import optparse

parser = optparse.OptionParser()
parser.add_option('--watch', action='store_true', dest='Watch', default=False)
parser.add_option('--nonoptimal', action='store_true',
                  dest='NonOptimal', default=False)
# DEBUG MODES;
parser.add_option('--blankrun', action='store_true',
                  dest='BlankRun', default=False,
                  help="Moneybot exits before real time evaluations/transactions.")
parser.add_option('--debug', action='store_true',
                  dest='MajorDebug', default=False)
parser.add_option('--noasync', action='store_false',
                  dest='AsyncPool', default=True,
                  help='Run brute force calibration on a single process'+\
                          ' (debug purpose).')

parser.add_option('--nocalibrate', action='store_true',
                  dest='NoCalibrate', default=False)
parser.add_option('--view', action='store_true',
                  dest='ShowStartupCandlestick', default=False,
                  help='Show recent cotation data on start up.')
parser.add_option('--strict', action='store_true',
                  dest='StrictMode', default=False)
parser.add_option('--triple', action='store_true',
                  dest='TripleSimultaneous', default=False)

# CALIBRATION MODES;
parser.add_option('-p', '--calibrate_population', action='store',
                  type='int', dest='GeneticCalibration', default=None,
                  help='Calibrate criterion using genetic algorithm.')
parser.add_option('--calibrate_bruteforce', action='store_true',
                  dest='BruteForceCalibration', default=False,
                  help='Calibrate criterion using brute force (testing all possibilities).')
parser.add_option('--save', action='store_true',
                  dest='SaveCriterion', default=False,
                  help="Save the criterion to calibrated on session")
parser.add_option('--database', action='store_true',
                  dest='CalibrateFromDatabase', default=False)

parser.add_option('--flagbank', action='store_true',
                  dest='FlagBankMode', default=False,
                  help='Think on brain memory mode -- experimental')
parser.add_option('--makeflagbank', action='store_true',
                  dest='MakeFlagBank', default=False,
                  help='Make or renew the flag bank. Flag bank mode depends on that.')

parser.add_option('--sell', action='store_true',

                  dest='ImmediateSell', default=False)

parser.add_option('-c', '--currency', dest='MainCurrency', default="USDT")

# NOTIFICATOIN MODES;
parser.add_option('-m', '--mail', action='store_true',
                  dest='mail', default=False,
                  help="Receive mail notifications on transactions. Need to setup credentials, read README")
parser.add_option('-e', '--exchange', dest='exchanges', default='')
(options, args) = parser.parse_args()
