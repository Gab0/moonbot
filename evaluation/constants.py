#/bin/python
DatabaseFolder = "candlestick_database"
CandlePlotFolder = "graphics"
FlagBankFile = "flagbank"
TimeStep = 60
calibrationWindow = 91800

calibrationLog = "calibration_log"

CoinNames={
    'btc': 'BitCoin',
    'ltc': 'LiteCoin',
    'eth': 'Ethereum',
    'etc': 'Ethereum Classic',
    'bch': 'BitCoin Cash'
}

CoinSymbols={
    'btc': 'B$',
    'ltc': 'L$',
    'eth': 'E$',
    'etc': 'Ec$',
    'bch': 'BC$',

}

TakerTax = 0
MakerTax = 0.25
