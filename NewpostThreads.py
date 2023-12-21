import requests
from rich import print
from scrapy.selector import Selector
import time
from CustomFunctions import getChannelAndId,sync_CheckViewOnPost, newProxie as newResidentialProxie, newDatacenteredProxie, sendReactions
from CustomClasses import Post
from threading import Thread
from rich import print
from aiohttp_socks import ProxyConnector
import aiohttp
import asyncio
from GlobalVariables import Gvar
from rich import print


def parseView(strview):
    try:
        views = strview.lower()
        if 'k' in views:
            view_count = int(float(views.replace('k', '').strip()) * 1000)
        else:
            view_count = int(views.strip())
        return view_count
    except:
        return 0



async def sendViewsOn(post: Post, proxie, attempt=1):
    # Gvar.VIEWSCOUNT[f"{channel}--{post_id}"] = post

    channel, post_id = post.url.replace("https://t.me/", "").split("/")

    if f"{channel}--{post_id}" in Gvar.BLACKLIST or post.views > Gvar.MINVIEWS:
        return

    Gvar.SUBTHREADCOUNT += 1
    subUrl = f'https://t.me/{channel}/{post_id}?embed=1&mode=tme'
    try:
        connector = ProxyConnector.from_url(proxie)
        timeout = aiohttp.ClientTimeout(total=Gvar.requesttimeout)
        cookiejar = aiohttp.CookieJar(unsafe=True)
        async with aiohttp.ClientSession(connector=connector, cookie_jar=cookiejar, timeout=timeout) as session:
            async with session.get(
                url=subUrl,
                headers={
                    'referer': post.url,
                    'user-agent': "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/112.0.0.0 Safari/537.36"}) as resp:
                html = Selector(text=await resp.text())

                stel_ssid = cookiejar.filter_cookies(resp.url).get("stel_ssid")
                views_token = html.xpath('//*[@data-view]/@data-view').get()

                if stel_ssid and views_token:  # stel_ssid in  cookie
                    Gvar.LiveView[post.url] = parseView(html.xpath('//span[@class="tgme_widget_message_views"]/text()').extract_first())
                    resp = await session.post(
                        url=f'https://t.me/v/?views={views_token}',
                        headers={
                            'referer': subUrl,
                            'user-agent': "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/112.0.0.0 Safari/537.36",
                            'x-requested-with': 'XMLHttpRequest'},
                        timeout=timeout)
                    if resp.status == 200 and await resp.text() == "true":
                        post.views+=1

                        Gvar.SUBTHREADCOUNT -= 1
                        return 1
                else:
                    raise ValueError("Token Not Available")
    except Exception as e:
        e = f"{e}"
        if e not in Gvar.ERRORLOG:
            Gvar.ERRORLOG[e] = 1
        else:
            Gvar.ERRORLOG[e] += 1

        if e == "Token Not Available":
            Gvar.BLACKLIST.add(f"{channel}--{post_id}")
            attempt = 100
            return

        if attempt < Gvar.maxretry:
            attempt += 1
            if Gvar.proxytype == "r":
                proxy = newResidentialProxie()
            elif Gvar.proxytype == "d":
                proxy = newDatacenteredProxie(post.url)
            # print(f"[+] Attempt {attempt}: {post_url} [+] Proxy : {proxy}")
            if proxy is None:
                Gvar.SUBTHREADCOUNT -= 1
                # print(f"[+] All available ips are used on : {post_url}")
                return
            await sendViewsOn(post, proxy, attempt)
        else:
            Gvar.SUBTHREADCOUNT -= 1
        return


def run_async_function(url, proxie, proxy_type):
    try:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        loop.run_until_complete(sendViewsOn(url, proxie, proxy_type))
    finally:
        loop.close()


def startSendingViews(url, requiredViews, proxy_type):
    post = sync_CheckViewOnPost(url)
    channel, post_id = url.replace("https://t.me/", "").split("/")

    Gvar.VIEWSCOUNT[f"{channel}--{post_id}"] = post.views
    if requiredViews > post.views:
        post.requiredViews = requiredViews-post.views
        for _ in range(requiredViews-post.views):
            if proxy_type == "r":
                proxy = newResidentialProxie()
            elif proxy_type == "d":
                proxy = newDatacenteredProxie(url)
            if proxy:
                Thread(target=run_async_function, args=(
                    url, proxy, proxy_type,)).start()
                time.sleep(Gvar.THREADINTERVAL)


def sendReactionThreadWrapper(chanel_id, post_id):
    Gvar.REACTIONCOUNT[f"{chanel_id}_{post_id}"] = "Started"
    try:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        loop.run_until_complete(sendReactions(chanel_id, post_id))
    finally:
        loop.close()
    Gvar.REACTIONCOUNT[f"{chanel_id}_{post_id}"] = "Done"


async def async_startSendingViews(url, requiredViews):
    post = sync_CheckViewOnPost(url)
    post.requiredViews = requiredViews
    Gvar.NewPosts.append(post)
    if requiredViews > post.views:
        await waitforview(post)

def getActiveProxy(url:str):
    if Gvar.proxytype == "r":
        proxy = newResidentialProxie()
    elif Gvar.proxytype == "d":
        proxy = newDatacenteredProxie(url)
    if proxy:return proxy

    return None

async def waitforview(post: Post):
    proxy=getActiveProxy(post.url)
    chunkSize=10
    tasks=[]
    if post.url not in Gvar.LiveView:
        Gvar.LiveView[post.url]=0
    while  (post.views < post.requiredViews or Gvar.LiveView[post.url]<post.requiredViews) and proxy:
        # print(f"Boosting : {post.url}")
        try:
            if( post.requiredViews-Gvar.LiveView[post.url])>chunkSize:
                try:
                    for _ in range(chunkSize):
                        task1=asyncio.create_task(sendViewsOn(post,proxy))
                        proxy=getActiveProxy(post.url)
                        tasks.append(task1)
                    await asyncio.gather(*tasks)
                except Exception as e:
                    LogError(f"L3 : {e}")
            else:
                try:
                    await sendViewsOn(post,proxy)
                    proxy=getActiveProxy(post.url)
                except Exception as e:
                    LogError(f"L4 : {e}")
        except Exception as e:
            LogError(f"L2 : {e}")
            # await asyncio.sleep(Gvar.THREADINTERVAL)

    Gvar.NewPosts=[ppost for ppost in Gvar.NewPosts if ppost!=post]
    _,id=getChannelAndId(post.url)
    Gvar.ipUsageTrack.pop(post.url)
    Gvar.ProcessedPost.append(id)
def LogError(e:Exception):
    if f"{e}" in Gvar.ERRORLOG:
        Gvar.ERRORLOG[f"{e}"]+=1
    else:
        Gvar.ERRORLOG[f"{e}"]=1