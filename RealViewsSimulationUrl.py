import asyncio
from threading import Thread,Event
from GhostViewCore import BoostViews
from CustomFunctions import getChannelAndId,getUniquePostIds
from GhostViewCore import BoostViews
import time
from GlobalVariables import Gvar
import sys


async def getAllPosts():
    posts=[]
    print(Gvar.LatestPostLinkUrl)
    print(Gvar.OlderPostLinkUrl)
    Lchannel,Latest_Post_id = getChannelAndId(Gvar.LatestPostLinkUrl)
    Ochannel,older_Post_id = getChannelAndId(Gvar.OlderPostLinkUrl)
    if Lchannel == Ochannel:
        bin=0
        if Latest_Post_id < older_Post_id:
            bin=Gvar.LatestPostLink
            Gvar.LatestPostLink=Gvar.OlderPostLinkUrl
            Gvar.OlderPostLinkUrl=bin
        _,post_id = getChannelAndId(Gvar.LatestPostLinkUrl)
        for lpost_id in await getUniquePostIds(Gvar.LatestPostLink,Gvar.OlderPostLinkUrl):
            posts.append(Gvar.LatestPostLinkUrl.replace(Latest_Post_id,lpost_id))
        return posts
    else:
        raise Exception("Post Links are not from same Channel")


async def main():
    posts= await getAllPosts()
    await BoostViews(posts)

Thread(target=Gvar.show_status).start()
asyncio.run(main())
Gvar.thredEvent.set()
sys.exit()