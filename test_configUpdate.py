import pandas as pd
import time
import configparser

config = configparser.ConfigParser()
config.read("config.ini")



df = pd.read_csv("ProcessedPosts.csv")
df['channelName'] =df['Url'].apply(lambda x: x.split('/')[3] if '/' in x else None)
df['PostId'] =df['Url'].apply(lambda x: int(x.split('/')[4]) if '/' in x else None)
for channel in df['channelName'].unique():
    subdf = df[df['channelName']==channel].sort_values(by=['channelName','PostId'])
    firstRow = subdf.iloc[0].Url
    lastRow = subdf.iloc[-1].Url
    config["RealViewsSimulationIndex"]["index"]=str(subdf.count())
    config["RealViewsSimulationIndex"]["latestpostlink"]=lastRow

    with open('config.ini', 'w') as configfile:
        config.write(configfile)
    print(firstRow,lastRow)
    time.sleep(60)