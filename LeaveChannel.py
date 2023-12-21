from telethon import functions, types
from telethon.sync import TelegramClient
from telethon.errors.rpcerrorlist import UserNotParticipantError,AuthKeyDuplicatedError
from telethon.tl.functions.channels import LeaveChannelRequest
from CustomFunctions import getChannelAndId,getBlackListedSessions
from rich import print
import glob
import configparser 
import os

config = configparser.ConfigParser()
config.read("config.ini")

channelUrlToLeft=config["SessionOperations"]["channelUrlToLeft"]

channel=channelUrlToLeft.replace("https://t.me/","")


for session in glob.glob("./sessions/*.session"):
    sessionname = os.path.basename(session).strip(".session")
    if sessionname in getBlackListedSessions():
        continue
    print(f"[+] Session : {sessionname}")
    try:
        client = TelegramClient(session, 12121212, "hash")
        client.connect()
    except AuthKeyDuplicatedError:
        print("[+] Session Not Avilable")
        continue
    try:
        client.start()
        client(LeaveChannelRequest(channel))
        print(f"[+] Leaving Channel from {sessionname} session")
    except ValueError:
        print(f"[+] Skipping {sessionname} session")
    except UserNotParticipantError:
        print(f"[+] Skipping {sessionname} session")
    except Exception as e:
        print(f"[+] Error : {e}")
    finally:
        client.disconnect()