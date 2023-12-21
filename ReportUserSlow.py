from telethon import TelegramClient
from telethon import functions, types
import json
from rich import print
import random
import glob
import time
from rich.console import Console
from rich.theme import Theme
from os import system, name
import requests
from threading import Thread
from CustomFunctions import newDatacenteredProxie
import configparser

config = configparser.ConfigParser()
config.read("config.ini")

suspeciousUser = config["ReportUser"]["username"]

system('cls' if name == 'nt' else 'clear')
print("[+] Loading Script .....")

custom_theme = Theme({"error": "bold red"})
console = Console(theme=custom_theme)


system('cls' if name == 'nt' else 'clear')

sessions = glob.glob("sessions/*.session")
with open("config.json", "r", encoding="utf8") as json_file:
    config = json.load(json_file)

reasons = {
    "ChildAbuse": types.InputReportReasonChildAbuse(),
    "Copyright": types.InputReportReasonCopyright(),
    "FakeAccount": types.InputReportReasonFake(),
    "Pornography": types.InputReportReasonPornography(),
    "Violence": types.InputReportReasonViolence(),
    "Spam": types.InputReportReasonSpam(),
    "Other": types.InputReportReasonOther()
}


console.print("[error]\nReport Options :\n")
for i, key in enumerate(reasons):
    print(f"    [+] {i+1} for '{key}'")

print("\n[-] Select Report Options Seperated By Comma : ", end="")
reason_chooses = input("")
reason_chooses = list(map(lambda i: i.strip(), reason_chooses.split(",")))

reports = config["reports"]

console.print(f"\n[error][+] Reporting[/error] '{suspeciousUser}'\n")


def main():
    for i, session in enumerate(sessions):
        rand_id = random.randint(1, 50)
        try:
            goodIp =False
            httpproxie=""
            while not goodIp:
                httpproxie=newDatacenteredProxie(f"reaction_{suspeciousUser}")
                try:
                    requests.get("http://api.ipify.org",proxies={"http":httpproxie},timeout=5)
                    goodIp=True
                except:
                    pass
            httpproxie = httpproxie.strip("http://")
            server, port = httpproxie.split(":")

            cli = TelegramClient(session, 12121212, "hash",proxy=("http", server, int(port)))
            cli.connect()
        except Exception as e:
            print("[Error] : {e}")
            continue

        if cli.is_user_authorized():
            reason_choosen = random.choice(reason_chooses)
            reason_type = reports[reason_choosen]["type"]
            reason = reasons[reason_type]
            message = random.choice(reports[reason_choosen]["messages"])
            result = cli(functions.messages.ReportRequest(
                peer=suspeciousUser, id=[rand_id], reason=reason, message=message))
            if result:
                print(f"    [{i+1}] Reported for '{reason_type}' with message: '{message}' From ip {httpproxie}")


main()
