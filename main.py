import requests
import os
import json
import time
import pickledb
import re
from lxml import etree
from io import StringIO
from lxml.cssselect import CSSSelector
from dotenv import load_dotenv
import telepot
from datetime import datetime

load_dotenv()

bot = telepot.Bot(os.environ.get("BOT_TOKEN"))

botToken = os.environ.get("BOT_TOKEN")
s = requests.Session()
parser = etree.HTMLParser()
selector = CSSSelector('.bundleLogic__wizard .comProduct__badge')
db = pickledb.load('unifyGuard.db', True)
# url = "https://eu.store.ui.com/collections/early-access/products/g4-doorbell-pro-ea"
url = os.environ.get("ITEM_URL")
itemName = os.environ.get("ITEM_NAME")

while True:
    response = s.get(url)
    html = response.content.decode("utf-8")

    with open("log.html", "w+") as file:
        file.write(html)

    if db.get('health') != datetime.today().strftime('%Y-%m-%d'):
        db.set('health', datetime.today().strftime('%Y-%m-%d'))
        bot.sendMessage(os.environ.get("BOT_CHAT"),
                        f"Still watching item: {itemName}...")

    match = re.findall(r"var json_product = (.*\"});", html)
    if match:
        json = json.loads(match[0])
        if json.get('available', ''):
            print("Item is in stock")

            if db.get(url) == datetime.today().strftime('%Y-%m-%d'):
                print("Notification was sent already today. Skiping")
            else:
                print("Sending notification")
                db.set(url, datetime.today().strftime('%Y-%m-%d'))
                bot.sendMessage(os.environ.get("BOT_CHAT"),
                                f"Your Item: {itemName} is in stock! {url}")
        else:
            print("Item is sold out")

    time.sleep(60)
