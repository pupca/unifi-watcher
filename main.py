import requests
import os
import json
import time
import pickledb
import re
from dotenv import load_dotenv
import telepot
from datetime import datetime
import traceback
import sys


import logging

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler("debug.log"),
        logging.StreamHandler()
    ]
)

load_dotenv()

bot = telepot.Bot(os.environ.get("BOT_TOKEN"))
botToken = os.environ.get("BOT_TOKEN")
timeOut = os.getenv("TIMEOUT", "60")
variantId = os.getenv("VARIANT", False)
s = requests.Session()
db = pickledb.load('unifyGuard.db', True)
url = os.environ.get("ITEM_URL")
itemName = os.getenv("ITEM_NAME", "")


logging.info(
    f"App starting to watch item. Name:{itemName} Variant:'{variantId}', timeout:'{timeOut}', url:'{url}'")

while True:
    try:
        logging.info(f"Getting {itemName} store url.")
        response = s.get(url)
        html = response.content.decode("utf-8")
        logging.info(
            f"Got response [{response.status_code}]. Parsing the page.")
        with open("log.html", "w+") as file:
            file.write(html)

        if db.get('health') != datetime.today().strftime('%Y-%m-%d'):
            logging.info(f"Sending health check.")
            db.set('health', datetime.today().strftime('%Y-%m-%d'))
            bot.sendMessage(os.environ.get("BOT_CHAT"),
                            f"Still watching item {itemName}...")

        match = re.findall(r"var json_product = (.*\"});", html)
        logging.info(f"JSON parsed.")

        if match:
            available = False
            json_match = json.loads(match[0])
            with open("log.json", "w+") as file:
                file.write(match[0])

            if variantId:
                variants = json_match.get("variants", [])
                variant = False
                for var in variants:
                    if variantId == var.get('id', ''):
                        variant = var

                if variant:
                    if variant.get('available', False):
                        available = True
                else:
                    if db.get('variant_error') != datetime.today().strftime('%Y-%m-%d'):
                        db.set('variant_error',
                               datetime.today().strftime('%Y-%m-%d'))
                        bot.sendMessage(os.environ.get("BOT_CHAT"),
                                        f"Error watching item {itemName}. Variant {variantId} was not found on the request page.")

            else:
                if json_match.get('available', False):
                    available = True

            if available:
                logging.info("Item is in stock")

                if db.get(url) == datetime.today().strftime('%Y-%m-%d'):
                    logging.info(
                        "Notification was sent already today. Skiping")
                else:
                    logging.info("Sending notification")
                    db.set(url, datetime.today().strftime('%Y-%m-%d'))
                    bot.sendMessage(os.environ.get("BOT_CHAT"),
                                    f"Your Item {itemName} is in stock! {url}")
            else:
                logging.info("Item is sold out")
    except:
        logging.error("Oops!", sys.exc_info()[0], "occurred.")
        traceback.print_exc()
        if db.get('error') != datetime.today().strftime('%Y-%m-%d'):
            db.set('error', datetime.today().strftime('%Y-%m-%d'))
            bot.sendMessage(os.environ.get("BOT_CHAT"),
                            f"Error watching item {itemName}. Error:'{sys.exc_info()[0]}' check the logs.")

    time.sleep(int(timeOut))
