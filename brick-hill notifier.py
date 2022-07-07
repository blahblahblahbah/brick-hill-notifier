from datetime import datetime
import asyncio
import httpx
import json



Webhooks = json.load( open("webhooks.json") )
Client = httpx.AsyncClient()

async def bh_notifier():
    for respone in [ [await Client.get(Webhooks.get("Webhooks").get(url)),url] for url in Webhooks.get("Webhooks")]:
        print(respone)


    previous = await Client.get("https://api.brick-hill.com/v1/shop/list?limit=25&cursor=&search=&types[]=face&types[]=head&types[]=hat&types[]=tool&verified_designers_only=false&special_only=false&event_only=false&show_unavailable=true&sort=updated") 
    while True:
        shoplist = await Client.get("https://api.brick-hill.com/v1/shop/list?limit=25&cursor=&search=&types[]=face&types[]=head&types[]=hat&types[]=tool&verified_designers_only=false&special_only=false&event_only=false&show_unavailable=true&sort=updated")       

        if shoplist.status_code == 200:
            for item in shoplist.json()["data"]:
                if item["id"] in [itemP["id"] for itemP in previous.json()["data"]]:
                    duration = (datetime.now() - datetime.strptime(item["updated_at"][0:19], "%Y-%m-%dT%H:%M:%S")).total_seconds()
                    newitem = item["created_at"][0:10]==item["updated_at"][0:10]
                    req = await Client.post(newitem and Webhooks.get("Webhooks").get("UploadedItems") or Webhooks.get("Webhooks").get("UpdatedItems"),
                        json={
                            "content": (newitem==True and (f"New Item! 😁 {Webhooks.get('Mention')}" ) or f"Item updated 😒 {Webhooks.get('Mention')}"),
                            "embeds": [
                                { 
                                    "title": ( (item.get('special')==True or item.get('special')==True) and f"✨ {str(item.get('name'))}") or str(item.get('name')),
                                    "description": "**Item Details**:",
                                    "color": 5814783,
                                    "url": f"https://www.brick-hill.com/shop/{ str(item.get('id')) }",
                                    "fields": [
                                        {
                                            "name": "Bucks",
                                            "value": str(item.get("bucks")),
                                            "inline": True
                                        },
                                        {
                                            "name": "Bits",
                                            "value": str(item.get("bits")),
                                            "inline": True
                                        }
                                    ],
                                    "thumbnail": {
                                        "url": item.get("thumbnail")
                                    },
                                    "footer": {
                                        "text": str(divmod(duration, 1)[0]).replace(".0","")+" seconds ago"
                                    }
                                }
                            ]
                        }
                    )     
                    print("webhook response",req)  
        print(shoplist);previous=shoplist
        await asyncio.sleep( Webhooks.get("refreshInterval") )
asyncio.run( bh_notifier() )

