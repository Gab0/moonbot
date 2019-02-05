A bot to buy and sell cryptocoins on various exchanges in parallel.
It reads candlestick data based on a basic self-learning method and decides the
moment to transact.

The method of evaluating candlestick data, and act accordingly are using a set of parameters.
At first, the bot would generate every possibility of parameter set (AKA 'Criterion') and test
it against a database of real bitcoin candlesticks. As the set got larger, and with more heavy proccessing involved,
a genetic algorithm approach was implemented to seek the most well-rounded Criterion, optimized to get most profit, while
losing the least ammount money possible by mankind.

Use at your own risk.

### Setup
```
$git clone https://github.com/gab0/moonbot.git
```

Create `credentials_EXCHANGENAME.txt`:
```
[okcoin key]
[okcoin password]
```

### Usage
```
$python moonbot.py -e [okcoinusd,binance] # run moonbot on given list of exchanges.
$python moonbot.py --help                 # :)
$python moonbot.py --dry                  # like a backtest, but running live. does not
trade real money, does not need OKcoin API keys. 
```
And run.

Supported exchanges are all those that are supported by ccxt library.

### Phylosophy
Against modern trading bots optimized by machine learning and stuff, this bot relies on the dumbest techniques.
The bet here is to watch multiple assets, and choose the most profitable to invest on short term. 
