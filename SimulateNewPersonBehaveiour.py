from telethon import functions, types
from telethon.sync import TelegramClient
from telethon.tl.functions.messages import SendReactionRequest,GetHistoryRequest
from telethon.tl.functions.channels import LeaveChannelRequest,JoinChannelRequest,EditBannedRequest
from rich import print
from CustomFunctions import getBlackListedSessions,getActiveproxies
import random
import time
import glob

reactionslist = ['👍', '👌', '❤️', '😍', '🔥', '👏', '😁'
                , '🤯', '😱', '🎉', '🤩', '🙏', '🕊', '💯', '⚡', '🏆', '😇','🤗']

url=input("[+] Channel Link to Simulate : ")
channel=url.replace("https://t.me/","")
noofReactions = input("[+] Enter No of Reaction sended By Single session : ")
maxtimetowaitForNextReaction=input("[+] Max time to wait for next Reaction Greater Than 60 : ")
maxtimetowaitForNextSession=input("[+] Max time to wait for next session Greater Than 60 : ")

Allmsgs=[]
sessionsdir = glob.glob("./sessions/*.session")
for index,sessionfile in enumerate(sessionsdir):
    sessionname=sessionfile.split("/")[-1].strip(".session")
    print(f"[{len(sessionsdir)-index}] Using Session : {sessionfile}")
    if sessionname in getBlackListedSessions():
        continue
    server,port=random.choice(getActiveproxies()).split(":")
    client = TelegramClient(sessionfile, 12121212, "hash",proxy=("http", server,int(port)))
    try:
        client.start()
        if not Allmsgs:
            client(JoinChannelRequest(channel))

            history = client(GetHistoryRequest(peer=channel,offset_id=0,offset_date=None,
                        add_offset=0,limit=200,max_id=0,min_id=0,hash=0))
            msgs={}
            selectone={}
            allmsg=  history.messages
            for message in allmsg:
                if message.grouped_id==None:
                    msgs[f"{message.id}"]=message.grouped_id
                else:
                    selectone[f"{message.grouped_id}"]=f"{message.id}"
            for key in selectone:
                value=selectone[key]
                msgs[value]=key
            Allmsgs=[int(x) for x in msgs]
        selectedmsgs=random.sample(Allmsgs,int(noofReactions))
        reaction=random.sample(reactionslist,int(noofReactions))
        for post_id,selectedReaction in zip(selectedmsgs,reaction):
            print(f"[+] Post Id : {post_id}")
            reaction_obj = types.ReactionEmoji(emoticon=selectedReaction)
            client(SendReactionRequest( peer=channel, msg_id=post_id,big=True, reaction=[reaction_obj]))
            # time.sleep(random.randint(60,int(maxtimetowaitForNextReaction)))
        # time.sleep(random.randint(60,int(maxtimetowaitForNextSession)))

    except Exception as e:
        print(f"[+] Error : {e}")
    finally:
        client.disconnect()

