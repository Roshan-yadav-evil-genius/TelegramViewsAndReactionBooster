import aiohttp, asyncio
from CustomFunctions import newProxie,newDatacenteredProxie,getChannelAndId,async_CheckViewOnPost,calc_viewsOfPreviousPost,selectionState,newDatacenteredProxie
from NewpostThreads import sendReactionThreadWrapper
from CustomClasses import TokenException,Target,Post
from aiohttp_socks import ProxyConnector
from rich import print
from scrapy.selector import Selector
from time import sleep
from threading import Thread
from GlobalVariables import Gvar


async def sendViewsOn(post:Post):
    channel,post_id=getChannelAndId(post.url)
    subUrl =f'https://t.me/{channel}/{post_id}?embed=1&mode=tme'
    target =Target(maxRetry=Gvar.maxretry)
    change=True
    while not target.Achieved and target.Attempt < target.maxRetry:
        target.Attempt+=1
        # print(f"[+] Attempt : {target.Attempt}, Url : {post.url} ")
        try:
            if Gvar.proxytype == 'r':
                connector = ProxyConnector.from_url(newProxie())
            else:
                if change:
                    ip=newDatacenteredProxie(post.url)
                connector = ProxyConnector.from_url(ip)
            
            timeout = aiohttp.ClientTimeout(total=Gvar.requesttimeout)
            cookiejar = aiohttp.CookieJar(unsafe=True)
            async with aiohttp.ClientSession(connector=connector,cookie_jar=cookiejar,timeout=timeout) as session:
                Gvar.REQUESTSCOUNT+=1
                async with session.get(url=subUrl,headers={'referer': post.url,'user-agent': Gvar.USER_AGENT}) as resp:
                    Gvar.REQUESTCOMPLETION+=1
                    html = Selector(text=await resp.text())

                    stel_ssid = cookiejar.filter_cookies(resp.url).get("stel_ssid")
                    views_token = html.xpath('//*[@data-view]/@data-view').get()

                    if stel_ssid and views_token : # stel_ssid in  cookie
                        resp = await session.post(
                            url=f'https://t.me/v/?views={views_token}', 
                            headers={
                                'referer': subUrl,
                                'user-agent': Gvar.USER_AGENT,
                                'x-requested-with': 'XMLHttpRequest'},
                            timeout=timeout)
                        Gvar.REQUESTCOMPLETION+=1
                        if resp.status == 200 and await resp.text() == "true":
                            # print(f"[+] Sent Views on {post.url}")
                            post.views+=1
                            target.Achieved = True                
                    else:
                        raise TokenException(f"Token Not Found on 'https://t.me/{channel}/{post_id}?embed=1&mode=tme'")
                        
        except Exception as e:
            if "[The semaphore timeout period has expired]" not in f"{e}":
                if f"{e}" not in Gvar.LOGS:
                    Gvar.LOGS[f"{e}"]=0
                Gvar.LOGS[f"{e}"]+=1
                change=True
            else:
                change=False

async def CheckAndIncreaseView(post:Post):
    channel,post_id=getChannelAndId(post.url)
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(f'https://t.me/{channel}/{post_id}',params={'embed': '1', 'mode': 'tme'},
            headers={'referer': f'https://t.me/{channel}/{post_id}','user-agent': Gvar.USER_AGENT}) as resp:
                html = Selector(text= await resp.text())
                views = html.xpath('//span[@class="tgme_widget_message_views"]').xpath('string()').get()

                if not views: return 0 # post is not available
                views=views.lower()
                if 'k' in views:
                    view_count = int(float(views.replace('k', '').strip()) * 1000)
                else:
                    view_count = int(views.strip())

                # update post status 
                post.status=True
                post.views=view_count
                Gvar.POSTS.append(post)
        
        # start increasing views
        if post.views<post.requiredViews:
            subtask=[]
            for _ in range(post.requiredViews-post.views):
                subtask.append(asyncio.create_task(sendViewsOn(post)))
            await asyncio.gather(*subtask)
    except Exception as e:
        if f"{e}" not in Gvar.LOGS:
            Gvar.LOGS[f"{e}"]=0
        Gvar.LOGS[f"{e}"]+=1

async def calculateViews(PostUrlList: list[str]):
    try:
        PostUrlList.sort(reverse=True)
        calculatedViews = []
        LatestPost = await async_CheckViewOnPost(PostUrlList[0])
        if LatestPost.views<=Gvar.MINVIEWS:
            calculatedViews=calc_viewsOfPreviousPost(Gvar.MINVIEWS,len(PostUrlList))
        else:
            calculatedViews=calc_viewsOfPreviousPost(LatestPost.views,len(PostUrlList))
        # calculatedViews.sort(reverse=True)
        return  [Post(url=url,requiredViews=views) for url,views in zip(PostUrlList,calculatedViews) ]
    except Exception as e:
        if f"{e}" not in Gvar.LOGS:
            Gvar.LOGS[f"{e}"]=0
        Gvar.LOGS[f"{e}"]+=1



async def BoostViews(posts):
    try:
        posts = await calculateViews(list(set(posts)))
        for i,post in enumerate(posts):
            chat_id,post_id = post.url.replace("https://t.me/", "").split("/")
            if selectionState():
                print(f"[{i}] Creating Thread For Reaction on {post.url}")
                Thread(target=sendReactionThreadWrapper,args=(chat_id,post_id)).start()
            print(f"[{i}] Creating task For Views on {post.url}")
            tasks=asyncio.create_task(CheckAndIncreaseView(post))
            await tasks
        #     Gvar.ASYNCTASKS.append(tasks)
        # await asyncio.gather(*Gvar.ASYNCTASKS)
    except Exception as e:
        if f"{e}" not in Gvar.LOGS:
            Gvar.LOGS[f"{e}"]=0
        Gvar.LOGS[f"{e}"]+=1
        