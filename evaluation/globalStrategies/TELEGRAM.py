#!/bin/python

from telethon import TelegramClient, events, sync
import time

# These example values won't work. You must get your own api_id and
# api_hash from https://my.telegram.org, under API Development.

from . TransactionPlan import TransactionPlan


class GlobalStrategy():
    def __init__(self):

        self.Real = True

        telegram_credentials_path = ["credentials/telegram.txt",
                                     '../credentials/telegram.txt']

        for path in telegram_credentials_path:
            try:
                credentials = open(path).read().split("\n")
                break
            except Exception as e:
                print(e)
                pass

        api_id, api_hash = list(filter(None, credentials))

        if self.Real:
            self.client = TelegramClient('session_name', api_id, api_hash)
            self.client.start()

        # self.client.get_dialogs()
        self.previousMessage = None

    def parseMessage(self, allCoins, message):
        s = message.split("\n")[0]
        s = s.split(" ")[-1]

        SymbolName = s.replace("-", "/")
        asset = SymbolName.split("/")[0]

        Coin = None
        for coin in allCoins:
            if asset.upper() in coin.Name:
                Coin = coin
                break
        if not Coin:
            print("Coin not found!")
            return None
        Operation = "buy"
        if "BUY PRICE" in message:
            Operation = "buy"
        elif "SELL PRICE" in message:
            Operation = "sell"
        elif "STOP-LOSS" in message:
            Operation = "sell"
        else:
            return None

        Price = message.split(" ")[-1].strip("'")
        Price = float(Price)
        a = TransactionPlan(Coin, Operation, Price)

        a.show()

        return a

    def __call__(self, Watcher):
        print("Fetching telegram messages...")
        if self.Real:
            Groups = ["FreeCryptoRobot Signals"]
            while True:
                try:
                    lastMessage = self.client.get_messages(Groups[0])[0].text
                    break
                except Exception as e:
                    time.sleep(3)
                    print(e)
        else:
            lastMessage ="🔔 GRS-BTC\n📕 SELL PRICE: 0.00009273'"

        if lastMessage != self.previousMessage:

            Watcher.clearMarketOrders()

            print("Parsing Telegram Message:")
            print(lastMessage)

            result = self.parseMessage(Watcher.Wallet.Coins, lastMessage)
            self.previousMessage = lastMessage
            return result
