#!/bin/python
from telethon import TelegramClient, events, sync

# These example values won't work. You must get your own api_id and
# api_hash from https://my.telegram.org, under API Development.

telegram_credentials_path = "../credentials/telegram.txt"

api_id, api_hash = list(filter(None, open(telegram_credentials_path).read().split("\n")))
api_id = 12345
api_hash = '0123456789abcdef0123456789abcdef'

client = TelegramClient('session_name', api_id, api_hash)
client.start()

messages = client.get_messages('username')
