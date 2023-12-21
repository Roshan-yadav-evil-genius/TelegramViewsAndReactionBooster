import glob
import random
import aiohttp
import time
import requests
from threading import Thread
import configparser
from CustomClasses import Post
from scrapy.selector import Selector
from telethon import functions, types
from telethon.sync import TelegramClient
from telethon.tl.functions.messages import SendReactionRequest,GetHistoryRequest
from GlobalVariables import Gvar







def getBlackListedSessions():
    if not Gvar.Blacklistedsessions:
        with open("Blacklistedsessions.txt", "r") as file:
            sessions=file.read().split()
            Blacklistedsessions = [name for name in sessions if name]

    return Blacklistedsessions

def test_ip(ip, protocol="http"):
    try:
        requests.get("http://api.ipify.org",
                     proxies={protocol: f"{protocol}://{ip}"}, timeout=5)
        Gvar.Activeproxies.add(ip)
    except:
        pass

def getActiveproxies():
    if Gvar.Activeproxies: return list(Gvar.Activeproxies)
    ths = []
    for url in Gvar.proxyLinks:
        data = requests.get(url)
        for ip in data.text.split():
            th = Thread(target=test_ip, args=(ip,))
            th.start()
            ths.append(th)
    for x in ths:
        x.join()
    
    return list(Gvar.Activeproxies)



def PostSelectionState():
    Gvar.postSelectionState.clear()
    truePercent = int((Gvar.SelectionPercent/100) * Gvar.NoOfMsgForChunk)
    Gvar.postSelectionState = [False]*Gvar.NoOfMsgForChunk
    Modified = []
    for _ in range(truePercent):
        done = False
        while not done:
            index = random.randint(0, Gvar.NoOfMsgForChunk-1)
            if index not in Modified:
                Gvar.postSelectionState[index] = True
                Modified.append(index)
                done = True
    random.shuffle(Gvar.postSelectionState)

    def getPostSelectionState():
        while True:
            for state in Gvar.postSelectionState:
                yield state
            PostSelectionState()

    return getPostSelectionState()


# -----no need to controll Manually selected----
selected = PostSelectionState()


def selectionState():
    return next(selected)
# ----------------------------------------------


def NoOfReactionTypes():
    return random.randint(Gvar.MinNoOfReactionType, Gvar.MaxNoOfReactionType)


def NoOfReactions():
    return random.randint(Gvar.MinNoOfReaction, Gvar.MaxNoOfReaction)


def selectedReactions():
    reactions = ['👍', '👌', '❤️', '😍', '🔥', '👏', '😁'
                , '🤯', '😱', '🎉', '🤩', '🙏', '🕊', '💯', '⚡', '🏆', '😇','🤗']
    reactions = random.sample(reactions, NoOfReactionTypes())
    finalrecations = []
    for _ in range(NoOfReactions()):
        finalrecations.append(random.choice(reactions))
    return finalrecations


def newProxie():
    username = Gvar.RPusername
    password = Gvar.RPpassword
    server = Gvar.RPserver
    port = Gvar.RPport
    return f'http://{username}:{password}@{server}:{port}'


def newDatacenteredProxie(url):
    if not len(Gvar.DatacenteredIps):
        for link in Gvar.proxyLinks:
            resp = requests.get(link)
            ips = set(resp.text.split())
            Gvar.DatacenteredIps = Gvar.DatacenteredIps.union(ips)
    if url not in Gvar.ipUsageTrack:
        ip = random.choice(list(Gvar.DatacenteredIps))
        Gvar.ipUsageTrack[url] = [ip]
        return f'http://{ip}'

    unusedlist = Gvar.DatacenteredIps-set(Gvar.ipUsageTrack[url])
    if len(unusedlist):
        ip = random.choice(list(unusedlist))
        Gvar.ipUsageTrack[url].append(ip)
        return f'http://{ip}'
    else:
        return None


def getChannelAndId(url):
    channel, id = url.replace("https://t.me/", "").split("/")
    return channel, id


def UpdateConfig(config: configparser.ConfigParser):
    with open("config.ini", "w") as file:
        config.write(file)

async def getUniquePostIds(latest,oldest=None,index=None):
    channel,lurl = getChannelAndId(latest)
    if oldest:
        channel,ourl = getChannelAndId(oldest)
        limit=int(lurl)-int(ourl)+1
    elif index:
        limit = index

    client = TelegramClient("anon", 12121212, "hash")
    try:
        await client.start()
        history = await  client(GetHistoryRequest(
                peer=channel,
                offset_id=int(lurl)+1,
                offset_date=None,
                add_offset=0,
                limit=limit,
                max_id=0,
                min_id=0,
                hash=0
            ))
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
        return [x for x in msgs]
    except ValueError:
        print("[+] Skipping Session")
    finally:
        # Stop and disconnect the client
        client.disconnect()

def calc_viewsOfPreviousPost(viewsOfCurrentPost, noOfPosts):
    previospost = viewsOfCurrentPost
    views = [viewsOfCurrentPost]
    for _ in range(noOfPosts-1):
        previospost = previospost + (Gvar.increasepercent/100) * previospost
        views.append(int(previospost))
    return views


async def async_CheckViewOnPost(posturl):
    post = Post(url=posturl, status=False, views=0)
    channel, post_id = getChannelAndId(posturl)
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(f'https://t.me/{channel}/{post_id}', params={'embed': '1', 'mode': 'tme'},
                                   headers={'referer': f'https://t.me/{channel}/{post_id}', 'user-agent': Gvar.USER_AGENT}) as resp:
                html = Selector(text=await resp.text())
                views = html.xpath(
                    '//span[@class="tgme_widget_message_views"]').xpath('string()').get()

                if not views:
                    return post
                if 'k' in views:
                    view_count = int(
                        float(views.replace('k', '').strip()) * 1000)
                else:
                    view_count = int(views.strip())

                # update post status
                post.status = True
                post.views = view_count
    except:
        pass
    return post


def sync_CheckViewOnPost(posturl)->Post:
    post = Post(url=posturl)
    channel, post_id = getChannelAndId(posturl)
    telegram_request = requests.get(
        f'https://t.me/{channel}/{post_id}',
        params={'embed': '1', 'mode': 'tme'},
        headers={'referer': f'https://t.me/{channel}/{post_id}',
                 'user-agent': Gvar.USER_AGENT})
    html = Selector(text=telegram_request.text)
    views = html.xpath(
        '//span[@class="tgme_widget_message_views"]').xpath('string()').get()

    if views:
        if 'k' in views:
            view_count = int(float(views.replace('k', '').strip()) * 1000)
        else:
            view_count = int(views.strip())
        post.status = True
        post.views = view_count
    return post


def createChunks(contentlist, listsize):
    threads = 0
    if len(contentlist) <= listsize:
        threads = len(contentlist)
    else:
        threads = listsize

    urlDistribution = {}

    for index, url in enumerate(contentlist):
        sublist_index = index % threads
        key = f"_{sublist_index}"
        if key not in urlDistribution:
            urlDistribution[f"_{sublist_index}"] = []
        urlDistribution[f"_{sublist_index}"].append(url)

    return [urlDistribution[key] for key in urlDistribution]

    # reactions = client(GetReactionsRequest(chanel_id, int(post_id), 0, 0, 100, types.InputPeerSelf()))

    # # Print the number of existing reactions
    # print(f"[+] Existing Reactions: {len(reactions)}")
async def sendReactions(chanel_id, post_id,attempt=0):
    try: 
        if attempt<=100:
            reactions = selectedReactions()
            sessions = glob.glob("sessions/*.session")
            for reaction in reactions:
                # time.sleep(random.randint(0,10))
                selectedSession = random.choice(sessions)
                sessionname = selectedSession.split("/")[-1].strip(".session")
                if sessionname not in getBlackListedSessions():
                    server,port=random.choice(getActiveproxies()).split(":")
                    async with TelegramClient(selectedSession, 12121212, "hash", proxy=("http", server,int(port))) as client:
                        try:
                            reaction_obj = types.ReactionEmoji(emoticon=reaction)
                            await client(SendReactionRequest(
                                peer=chanel_id, msg_id=int(post_id),
                                big=True, reaction=[reaction_obj]
                            ))
                            print(f"[+] Reaction Sent On : {post_id}")
                            time.sleep(Gvar.reactionInterval)
                        except Exception as e:
                            print(f"[+] Error: {e}")
    except Exception as e:
       time.sleep(5)
       await sendReactions(chanel_id,post_id,attempt=attempt+1)