import configparser
from CustomFunctions import UpdateConfig
from telethon import TelegramClient
from rich import print
import pandas as pd

config=configparser.ConfigParser()
config.read("config.ini")


api_id = config["ScrapePremiumUser"]["api_id"]
api_hash = config["ScrapePremiumUser"]["api_hash"]
phone_no = config["ScrapePremiumUser"]["phone_no"]

columns = ["sr.No",'UserId','Username','FullName',"GroupName"]
df = pd.DataFrame(columns=columns)
count=0

with open("data.bl","r") as file:
    alreadyscrapedlist=file.read().split()

try:
    client = TelegramClient(f"sessions/{phone_no}.session", api_id, api_hash)
    client.start()

    for dialog in client.iter_dialogs():
        if not dialog.is_group or f"{dialog.id}" in alreadyscrapedlist:
            continue
        print(f"[Group] Extracting Members From '{dialog.name}' [+] Id : {dialog.id}")
        participants = client.get_participants(dialog.id)
        for participant in participants:
            if participant.premium:
                count+=1
                new_data = {"sr.No":count,'UserId':participant.id,'Username':participant.username,"FullName":f"{participant.first_name} {participant.last_name}","GroupName":dialog.name}
                df = pd.concat([df, pd.DataFrame([new_data])], ignore_index=True)
        with open("data.bl","a") as file:
            file.write(f"{dialog.id}\n")
            
except Exception as e:
    print(f"[+] Error : {e}")
finally:    
    client.disconnect()

df.to_csv("data.csv", index=False)