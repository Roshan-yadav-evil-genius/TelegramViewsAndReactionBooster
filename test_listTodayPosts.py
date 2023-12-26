from telethon import TelegramClient
from telethon.tl.functions.messages import GetHistoryRequest
from telethon.tl.types import InputPeerChannel
from datetime import datetime, timedelta

# Replace these with your own values
api_id = 154361
api_hash = '5545tggfbv5g65g6'
channel_id = "testingBanA2"  # Use the numeric part of the channel ID
# https://t.me/testingBanA2

# Initialize the client
# 20 - s 4154
# 20 - e 4255
# 21 - s 4155
# 21 - e 4434
# https://t.me/testingbana1/4434
client = TelegramClient('anon', api_id, api_hash)
async def main():

    try:
        await client.start()

        today=datetime.now()
        tomorrow = today+ timedelta(days=1)

        # -------------------------------- Today & Tomorrow --------------------------------
        today = datetime(today.year,today.month,today.day)
        tomorrow = datetime(tomorrow.year,tomorrow.month,tomorrow.day)

        request = GetHistoryRequest(peer=channel_id,offset_id=0,offset_date=today,add_offset=0,limit=200, max_id=0,min_id=0,hash=0)

        allmsg = await client(request)
        allmsg=allmsg.messages
        OPostId=int(allmsg[-1].id)+1
        # ----------------------------------- Hlo & hii -------------------------------------
        request = GetHistoryRequest(peer=channel_id,offset_id=0,offset_date=tomorrow,add_offset=0,limit=200,max_id=0,min_id=0,hash=0)

        allmsg = await client(request)
        allmsg=allmsg.messages
        LPostId=int(allmsg[0].id)

        print("New : ",LPostId," Old : ",OPostId," Total : ",LPostId-OPostId)

    except Exception as e:
        print(e)

    finally:
        await client.disconnect()

# Run the main function
client.loop.run_until_complete(main())
