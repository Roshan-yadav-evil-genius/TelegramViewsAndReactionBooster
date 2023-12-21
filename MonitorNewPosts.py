import subprocess
import configparser
from telethon import TelegramClient, events
from telethon.tl.types import User, Channel, Chat, ChatEmpty
from rich import print
import time
from CustomClasses import Post
from threading import Thread, Event
from NewpostThreads import async_startSendingViews
from CustomFunctions import selectionState, sendReactions
from os import system, name
import shutil
import threading
import os
import sys
from GlobalVariables import Gvar
from rich.table import Table
from rich import box
from rich.panel import Panel
from rich.text import Text
import datetime

import time

config = configparser.ConfigParser()
config.read("config.ini")
stop_event = Event()

system('cls' if name == 'nt' else 'clear')
print("""
        Created By : 'Roshan Yadav' https://t.me/roshanyadavse
              
         Powered By 'BridgeSkillz' https://bridgeskillz.com/
              
                      Phone no : 8476868560
        \n\n""")

api_id = config["MonitorNewPost"]["api_id"]
api_hash = config["MonitorNewPost"]["api_hash"]

minimumviews = int(config["Global"]["minimumviews"])

MonitoringList = config["MonitorNewPost"]["monitorchannel"]
MonitoringList = [int(id.strip()) for id in MonitoringList.split(",") if id]

UIPostMonitoringList = ",".join([str(x) for x in MonitoringList])
STartingTime = time.time()
ResetTime = datetime.time(20, 0, 0)  # 20:00 or 8:00 PM

with open("ProcessedPosts.csv", "w") as file:
    file.write("Url,RequiredViews\n")

client = TelegramClient('anon', api_id, api_hash)
groupmsg = []


@client.on(events.NewMessage)
async def my_event_handler(event):
    try:
        chat = await event.get_chat()
        if not isinstance(chat, Channel):
            return

        sender = await event.get_sender()
        chat_id = event.chat_id
        sender_id = event.sender_id
        if chat_id in MonitoringList:
            if event.message.grouped_id is None or event.message.grouped_id not in groupmsg:
                groupmsg.append(event.message.grouped_id)
                print(Gvar.viewsmapping, chat_id,f"{chat_id}" in Gvar.viewsmapping)
                url =f"https://t.me/{chat.username}/{event.message.id}"

                with open("ProcessedPosts.csv","a") as file:
                    if f"{chat_id}" in Gvar.viewsmapping:
                        lminimumviews = int(Gvar.viewsmapping[f"{chat_id}"])
                        print("[+] Have Limit", lminimumviews)
                        file.write(f"{url},{lminimumviews}\n")
                        task1 = async_startSendingViews(url, lminimumviews)
                    else:
                        print("[+] No Limit", minimumviews)
                        file.write(f"{url},{minimumviews}\n")
                        task1 = async_startSendingViews(url, minimumviews)

                await task1

                if selectionState():
                    chanel_id = chat.username
                    post_id = event.message.id
                    Gvar.REACTIONCOUNT[f"{chanel_id}_{post_id}"] = "Started"
                    await sendReactions(chanel_id, post_id)
    except Exception as e:
        print(f"[+] my_event_handler Error : {e}")
        LogError(f"L1 : {e}")


def LogError(e: Exception):
    if f"{e}" in Gvar.ERRORLOG:
        Gvar.ERRORLOG[f"{e}"] += 1
    else:
        Gvar.ERRORLOG[f"{e}"] = 1


def parseTime(initial, final):
    time_spent_seconds = final - initial
    hours = int(time_spent_seconds // 3600)
    remaining_seconds = time_spent_seconds % 3600
    minutes = int(remaining_seconds // 60)
    seconds = int(remaining_seconds % 60)
    return f"{hours}:{minutes}:{seconds}"


def add_colored_row(table, col1_data, col2_data, col3_data, col4_data, light=False):
    # color_format = "bold" if not light else "dim"
    color_format = "bold"
    table.add_row(f"[{color_format} magenta]{col1_data}[/{color_format} magenta]",
                  f"[{color_format} green]{col2_data}[/{color_format} green]",
                  f"[{color_format} red]{col3_data}[/{color_format} red]",
                  f"[{color_format} cyan]{col4_data}[/{color_format} cyan]"
                  )


def create_table():
    table = Table(title="[bold yellow]BridgeSkillz Analytics Dashboard[/bold yellow]",
                  show_header=True, header_style="bold", expand=True,
                  border_style="bold purple", box=box.HEAVY)

    table.add_column("Post", header_style="bold magenta")
    table.add_column("Views", header_style="bold green")
    table.add_column("IpUsage", header_style="bold red")
    table.add_column("Live", header_style="bold cyan")
    for post in Gvar.NewPosts:
        post: Post = post
        try:
            if post.url not in Gvar.LiveView:
                Gvar.LiveView[post.url] = 0
            if post.url not in Gvar.ipUsageTrack:
                Gvar.ipUsageTrack[post.url] = []
            add_colored_row(table, f"{post.url.replace('https://t.me/','')}", f"{post.views} / {post.requiredViews}",
                            f"{len(Gvar.ipUsageTrack[post.url])}", f"{Gvar.LiveView[post.url]}", light=False)
        except:
            pass
    return table


def GetGeneralInfo():
    DateTime = datetime.datetime.now()
    CurrentTime = DateTime.strftime("%I:%M:%S %p %d/%B/%Y")
    RCurrentTime = DateTime.time()
    RemainingTime = get_remaining_time(ResetTime, RCurrentTime)

    table = Table(show_header=True, header_style="bold magenta",
                  border_style="bold purple", box=box.HEAVY)
    table.add_column("Parameters", justify="left")
    table.add_column("Value", justify="left")

    # Add rows
    table.add_row("[bold yellow]Current Time[bold yellow]",
                  f"[bold yellow]{CurrentTime}[/bold yellow]")
    table.add_row("[bold green]Uptime[bold green]",
                  f"[bold green]{parseTime(STartingTime,time.time())}[/bold green]")
    table.add_row("[bold red]Reset In[bold red]",
                  f"[bold red]{RemainingTime}[/bold red]")
    table.add_row("[bold blue]Thread Count[bold blue]",
                  f"[bold blue]{threading.active_count()}[/bold blue]")
    table.add_row("Monitoring", UIPostMonitoringList)

    return table

import pandas as pd

def restart_program():
    processes = []
    start_time = time.time()  # Record the start time
    max_duration = 10*3600
    df = pd.read_csv("ProcessedPosts.csv")
    df['channelName'] =df['Url'].apply(lambda x: x.split('/')[3] if '/' in x else None)
    df['PostId'] =df['Url'].apply(lambda x: int(x.split('/')[4]) if '/' in x else None)
    for channel in df['channelName'].unique():
        subdf = df[df['channelName']==channel].sort_values(by=['channelName','PostId'])
        config["RealViewsSimulationIndex"]["index"]=str(subdf.shape[0])
        config["RealViewsSimulationIndex"]["latestpostlink"]=subdf.iloc[-1].Url

        with open('config.ini', 'w') as configfile:
            config.write(configfile)

        # Check if 2 minutes have passed
        if time.time() - start_time > max_duration:
            break

        process = subprocess.Popen([sys.executable, "RealViewsSimulationIndex.py"])
        processes.append(process)

        # Wait for the process to complete or for the total time to exceed
        while process.poll() is None:
            if time.time() - start_time > max_duration:
                process.terminate()
                break
            time.sleep(1)  # Sleep to prevent busy waiting

    # Clean up any remaining processes
    for process in processes:
        try:
            process.wait(timeout=5)  # Wait for 5 seconds for clean termination
        except subprocess.TimeoutExpired:
            process.kill()  
    # Executing the second file
    print("Executing the Main file...")
    python = sys.executable
    os.execl(python, python, *sys.argv)


def get_remaining_time(target, current):
    """Calculate the remaining time until the target time and return a formatted string."""
    target_datetime = datetime.datetime.combine(datetime.date.today(), target)
    current_datetime = datetime.datetime.combine(
        datetime.date.today(), current)

    # Adjust for the next day if the target time is already passed for today
    if current_datetime > target_datetime:
        target_datetime += datetime.timedelta(days=1)

    remaining_time = target_datetime - current_datetime
    # Extract hours, minutes, and seconds
    hours, remainder = divmod(remaining_time.seconds, 3600)
    minutes, seconds = divmod(remainder, 60)

    return f"{hours}:{minutes}:{seconds}"


def TerminalUI():
    while not stop_event.is_set():
        now = datetime.datetime.now().time()
        if now.hour == ResetTime.hour and now.minute == ResetTime.minute:
            print("Restarting program at 8:00 PM...")
            restart_program()

        # -------------------------------Ui Section------------------------
        if Gvar.ActiveCommand in ['v', 'g', 'r']:
            print(GetGeneralInfo())

        if Gvar.ActiveCommand in ['v', 'b']:
            print(f"[+] BlacklistedPosts : {Gvar.BLACKLIST}\n")

        if Gvar.ActiveCommand in ['v', 'e']:
            print(f"\n[+] Errors : {Gvar.ERRORLOG}\n")

        if Gvar.ActiveCommand in ['v', 'p']:
            print(f"\n[+] ProcessedPost : {Gvar.ProcessedPost}\n")

        if Gvar.ActiveCommand in ['v', 'l', 'r']:
            if Gvar.NewPosts:
                print(create_table())
            else:
                print("\n[+] Waiting For Post")

        time.sleep(2)
        system('cls' if name == 'nt' else 'clear')


def TerminalControl():
    # v = verbose
    # g = generalinfo
    # l = livePostStatistics
    # e = errors
    # b = Blaclisted
    # p = ProcessedPost
    # r = requiredInfo
    while not stop_event.is_set():
        UserInput = input("")

        if UserInput.lower() in ['v', 'g', 'l', 'e', 'b', 'p', 'r']:
            Gvar.ActiveCommand = UserInput.lower()


client.start()

Thread(target=TerminalUI).start()
Thread(target=TerminalControl).start()
client.run_until_disconnected()
stop_event.set()
