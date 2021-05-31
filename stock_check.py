import json
import requests
import scrapers
import tweepy
import random
from datetime import datetime, timezone
from bs4 import BeautifulSoup
from time import sleep
from beanstock import Beanbot


DEBUGGING = False

HEADERS = {
    "Connection": "keep-alive",
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_6) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.0.1 Safari/605.1.15",
}

TARGET = "TARGET"
WALMART = "WALMART"
BESTBUY = "BESTBUY"
GAMESTOP = "GAMESTOP"
AMAZON = "AMAZON"
MICROSOFT = "MICROSOFT"

XBOX = "XBOX SERIES X"

XBOX_MESSAGES = [
    f"{XBOX} IS BACK IN STOCK!\nCHECK IT OUT BELOW!\n",
    f"{XBOX} APPEARS TO BE AVAILABLE BELOW\n",
]

CONSOLES = {
    XBOX: {
        BESTBUY: ["https://www.bestbuy.com/site/6428324.p?skuId=6428324"],
        GAMESTOP: ["https://www.gamestop.com/B224745J.html", "https://www.gamestop.com/xbox-series-x/B224744V.html"],
        TARGET: ["https://www.target.com/p/xbox-series-x-console/-/A-80790841"],
        WALMART: ["https://www.walmart.com/ip/Xbox-Series-X/443574645"],
        AMAZON: ["https://www.amazon.com/Xbox-X/dp/B08H75RTZ8"],
        MICROSOFT: ["https://www.xbox.com/en-us/configure/8WJ714N3RBTL"],
    }
}

RETAILERS_LIST = [TARGET, WALMART, BESTBUY, GAMESTOP, AMAZON, MICROSOFT]


# initiliaze stock_info
stock_info = {}
for retailer in RETAILERS_LIST:
    stock_info[retailer] = {
        "available": None,
        "lastUpdated": "{:%D @ %H:%M:%S} UTC".format(datetime.now()),
        "inStockLinks": [],
        "hasTweeted": False,
    }


# Check Xbox inventory
def check_xbox_stock():
    with open("xboxInfo.json", "r") as json_file:
        prev_info = json.load(json_file)
        for retailer, urls in CONSOLES[XBOX].items():
            for url in urls:
                available = scrapers.scrape(retailer, url)

                # if item is in stock add url to collection.
                if available:
                    stock_info[retailer]["inStockLinks"].append(url)

                # if inStockLinks not empty then update availabilty to True
                if stock_info[retailer]["inStockLinks"]:
                    stock_info[retailer]["available"] = True
                else:
                    stock_info[retailer]["available"] = False
                    prev_info[retailer]["hasTweeted"] = False

    should_update = not prev_info[retailer]["hasTweeted"]
    link_string = ""
    for retailer, stock_data in stock_info.items():
        # if should_update is true then we have already updated
        if not should_update:
            should_update = not prev_info[retailer]["hasTweeted"]

        for link in stock_data["inStockLinks"]:
            stock_info[retailer]["hasTweeted"] = True
            link_string += f"{retailer}: {link}\n"

    # update stock_info so we know have tweeted already to prevent spam tweets
    beanbot = Beanbot()
    try:
        if should_update:
            message = XBOX_MESSAGES[0] + link_string
            beanbot.send_tweet(message)
    except tweepy.TweepError:
        message = XBOX_MESSAGES[1] + link_string
        beanbot.send_tweet(message)

    with open("xboxInfo.json", "w") as file:
        json.dump(stock_info, file, indent=2)


# Check PS5 inventory
def check_ps5_stock():
    pass


def is_available(retailers):
    check_xbox_stock()


def main():
    while True:
        is_available([])
        sleep_duration = random.randint(601, 960)
        sleep(sleep_duration)


if __name__ == "__main__":
    if DEBUGGING:
        pass
    else:
        main()
