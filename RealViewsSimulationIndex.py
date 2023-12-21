import configparser
from CustomFunctions import getChannelAndId,getUniquePostIds
from GhostViewCore import BoostViews
from threading import Thread,Event
import asyncio
import sys
from GlobalVariables import Gvar


async def getAllPosts():
    posts=[]
    _,post_id = getChannelAndId(Gvar.LatestPostLink)
    for lpost_id in await getUniquePostIds(Gvar.LatestPostLink,index=Gvar.NoOfPost):
        posts.append(Gvar.LatestPostLink.replace(post_id,lpost_id))
    return posts


async def main():
    posts= await getAllPosts()
    await BoostViews(posts)

# Thread(target=Gvar.show_status).start()
asyncio.run(main())
Gvar.thredEvent.set()
sys.exit()