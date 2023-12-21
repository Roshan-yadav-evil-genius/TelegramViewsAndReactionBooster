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
from CustomFunctions import proxyLinks
import configparser

config = configparser.ConfigParser()
config.read("config.ini")

suspeciousUser = config["ReportUser"]["username"]

system('cls' if name == 'nt' else 'clear')
print("[+] Loading Script .....")

custom_theme = Theme({"error": "bold red"})
console = Console(theme=custom_theme)

Activeproxies = []


def test_ip(ip, protocol="http"):
    try:
        requests.get("http://api.ipify.org",
                     proxies={protocol: f"{protocol}://{ip}"}, timeout=5)
        Activeproxies.add(ip)
    except requests.RequestException as e:
        pass

ths = []
for url in proxyLinks:
    data = requests.get(url)
    for ip in data.text.split():
        th = Thread(target=test_ip, args=(ip,))
        th.start()
        ths.append(th)
for x in ths:
    x.join()



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
            httpproxie = random.choice(Activeproxies)
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
