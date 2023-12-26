
import requests
from rich import print
from threading import Thread,active_count
import json
import time

PROXIES=dict()

proxiesUrl={
    "http":"https://raw.githubusercontent.com/Hardikagrawal4575/proxy-premium/main/proxyscrape_premium_http_proxies.txt",
    "socks5":"https://raw.githubusercontent.com/Hardikagrawal4575/proxy-premium/main/proxy%202"
}

for type,url in proxiesUrl.items():
    resp = requests.get(url)
    if resp.status_code==200:
        ips = resp.text.split()
        for ip in ips:
            ip,port=ip.split(":")
            if ip not in PROXIES:
                PROXIES[ip]=dict()
            PROXIES[ip][type]=port

proxiemasks=[]
for ip,ports in PROXIES.items():
    proxie = {
        "http":f"http://{ip}:{ports['http']}",
        "https":f"http://{ip}:{ports['http']}",
        "socks5":f"socks5://{ip}:{ports['socks5']}",
    }
    proxiemasks.append(proxie)

successCount=0
FailierCount=0
Errors=set()
def dummyIpTest(proxie):
    global successCount,FailierCount,Errors
    try:
        resp=requests.get("https://api.ipify.org",proxies=proxie,timeout=1500)
        if resp.status_code==200:
            successCount+=1
        else:
            FailierCount+=1
    except Exception as e:
        Errors.add(f"{e}")
        FailierCount+=1

print("[+] Waiting For Responses")
threads=[]
for mask in proxiemasks:
    process=Thread(target=dummyIpTest,args=(mask,))
    process.start()
    threads.append(process)

for process in threads:
    process.join()

print(f"[+] Success : {successCount}, [+] Unsuccessful : {FailierCount}")

with open("TestIpAuthenticity.log","w") as file:
    for e in Errors:
        file.write(f"{e}\n")

