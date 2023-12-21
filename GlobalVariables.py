import configparser
import time
from threading import Event
from os import name,system
from rich import print
import requests

config=configparser.ConfigParser()
config.read("config.ini")

class GlobalVariables:
    _instance = None
    CreationTime = time.time()
    ActiveCommand ="r"
    thredEvent = Event()
    ASYNCTASKS=list()
    POSTS = list()
    REQUESTSCOUNT=0
    REQUESTCOMPLETION=0
    LOGS=dict()
    VIEWSCOUNT = dict()
    REACTIONCOUNT=dict()
    ERRORLOG = dict()
    SUBTHREADCOUNT = 0
    BLACKLIST=set()
    postSelectionState = list()
    ActiveSessionIds = list()
    NewPosts=list()
    ProcessedPost=list()
    LiveView=dict()
    Blacklistedsessions=list()
    Activeproxies=set()
    DatacenteredIps = set()
    ipUsageTrack = {}
    proxytype = config["Global"]["proxytype"]
    proxyLinks = [
        "https://raw.githubusercontent.com/Hardikagrawal4575/proxy-premium/main/proxyscrape_premium_http_proxies.txt",
        # "https://raw.githubusercontent.com/Hardikagrawal4575/proxy-premium/main/proxy%202"
    ]

    USER_AGENT = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/106.0.0.0 Safari/537.36'

    MINVIEWS=int(config["Global"]["MinimumViews"])
    THREADINTERVAL = float(config["MonitorNewPost"]["threadcreationinterval"])

    RPusername = config["RPCredentials"]["username"]
    RPpassword = config["RPCredentials"]["password"]
    RPserver = config["RPCredentials"]["server"]
    RPport = config["RPCredentials"]["port"]

    viewsmapping={key:int(value) for key,value in config['MonitorNewPostViewsMapping'].items()}

    requesttimeout = int(config["Global"]["requesttimeout"])

    maxretry = int(config["Global"]["maxretry"])
    
    NoOfMsgForChunk = int(config["Reactions"]["NoOfMsgForChunk"])
    SelectionPercent = int(config["Reactions"]["SelectionPercent"])

    MinNoOfReactionType = int(config["Reactions"]["MinNoOfReactionType"])
    MaxNoOfReactionType = int(config["Reactions"]["MaxNoOfReactionType"])

    MinNoOfReaction = int(config["Reactions"]["MinNoOfReaction"])
    MaxNoOfReaction = int(config["Reactions"]["MaxNoOfReaction"])

    increasepercent = float(config["Global"]["increaseby"])
    
    reactionInterval = int(config["Reactions"]["reactionInterval"])

    LatestPostLink = config["RealViewsSimulationIndex"]["LatestPostLink"]
    NoOfPost = int(config["RealViewsSimulationIndex"]["Index"])

    LatestPostLinkUrl = config["RealViewsSimulationUrl"]["latestpostlink"]
    OlderPostLinkUrl = config["RealViewsSimulationUrl"]["OlderPostLink"]

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super().__new__(cls, *args, **kwargs)
        return cls._instance    
    @classmethod
    def show_status(cls):
        myip=requests.get("https://api.ipify.org")
        while not cls.thredEvent.is_set():
            end_time = time.time()
            cls.POSTS.sort()
            time_spent_seconds = end_time - cls.CreationTime
            hours = int(time_spent_seconds // 3600)
            remaining_seconds = time_spent_seconds % 3600
            minutes = int(remaining_seconds // 60)
            seconds = int(remaining_seconds % 60)
            strtime=f"{hours}:{minutes}:{seconds}"
            print(f"[+] Duration : {hours}:{minutes}:{seconds}",end=" ",flush=True)
            print(f"MyIp : {myip.text}")
            print(f"[+] PostCount : {len(cls.POSTS)}",end=" ",flush=True)
            print(f"[+] Requests : {cls.REQUESTSCOUNT}",end=" ",flush=True)
            print(f"[+] CompletedRequest : {cls.REQUESTCOMPLETION}",flush=True,end="\n\n")
            print("[+] Error : ",flush=True)
            print(cls.LOGS,flush=True)
            print(f"[+] ReactionStatus : ",flush=True)
            print(cls.REACTIONCOUNT,flush=True)
            print(f"[+] ViewsStatus : ",flush=True)
            print(cls.POSTS,flush=True)
            time.sleep(1)
            system('cls' if name=='nt' else 'clear')

Gvar = GlobalVariables()
