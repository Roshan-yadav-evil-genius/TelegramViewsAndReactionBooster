import configparser
from CustomFunctions import UpdateConfig
from telethon import TelegramClient, events, utils
from rich import print
config=configparser.ConfigParser()
config.read("config.ini")


api_id = config["MonitorNewPost"]["api_id"]
api_hash = config["MonitorNewPost"]["api_hash"]


client = TelegramClient('anon', api_id, api_hash)

async def main():
    async for dialog in client.iter_dialogs():
        if dialog.is_channel:
            print(f"[+] Title : '{dialog.name}' [+] Id : {dialog.id}")


    
with client:
    client.loop.run_until_complete(main())