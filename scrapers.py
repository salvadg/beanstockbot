# Helper functions for scraping data from each site
import requests

from selenium import webdriver
from urllib.request import urlopen
from bs4 import BeautifulSoup
import time

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


DISPATCHER = {
    BESTBUY: lambda soup: _bestbuy(soup),
    GAMESTOP: lambda soup: _gamestop(soup),
    TARGET: lambda soup: _target(soup),
    WALMART: lambda soup: _walmart(soup),
    AMAZON: lambda soup: _amazon(soup),
    MICROSOFT: lambda soup: _microsoft(soup),
}


def _bestbuy(soup):
    # Scraping Bestbuy.
    data = soup.find("button", {"class": "add-to-cart-button"})

    if data.has_attr("disabled"):
        return False
    if data.text == "Add to Cart":
        return True

    return None


def _walmart(soup):
    seller = soup.select_one("#add-on-atc-container > section > div > div > a")

    button = soup.find(
        "button",
        {"class": "button prod-ProductCTA--primary prod-ProductCTA--server display-inline-block button--primary"},
    )

    error_page = soup.find(
        "div",
        {"class": "error-message-margin error-page-message"},
    )

    if button and seller:
        # Only considered available if sold by walmart. No Resellers.
        if button.text.lower() == "add to cart" and seller.text.lower() == "walmart":
            return True
        else:
            return False
    elif "item is unavailable" in error_page.text.lower() or "backorder" in error_page.text.lower():
        return False
    else:  # default to false
        return False


def _target(soup):

    soldout_block = soup.find(
        "div",
        {"data-test": "soldOutBlock"},
    )

    out_of_stock_block = soup.find(
        "div",
        {"data-test": "storeBlockNonBuyableMessages"},
    )

    order_pickup_button = soup.find(
        "button",
        {"data-test": "orderPickupButton"},
    )

    ship_to_store = soup.find(
        "button",
        {"data-test": "shipToStoreButton"},
    )

    ship_it_button = soup.find(
        "button",
        {"data-test": "shipItButton"},
    )

    if order_pickup_button or ship_it_button or ship_to_store:
        return True
    if soldout_block or out_of_stock_block:
        return False

    return None


def _microsoft(soup):
    soldout_button = soup.select_one(
        "#BodyContent > section > div > div > div > div > div > div.pb-4.col-md-3 > button"
    )
    if soldout_button and ("out of stock" in soldout_button.text.strip().lower()):
        return False
    else:
        return True


def _gamestop(soup):
    cart_button = soup.find("button", {"class": "add-to-cart btn btn-primary"})

    if cart_button:
        cart_button_text = cart_button.text.strip().lower()

        if (cart_button_text == "add to cart") or (cart_button_text not in ["not available", "unavailable"]):
            return True
        else:
            return False

    return None


def _amazon(soup):
    SOLD_BY_AMAZON = "ships from and sold by amazon.com."
    soldout_box = soup.find("div", {"id": "outOfStock"})
    buy_box = soup.find("div", {"id": "buyBoxAccording"})
    unqualified_box = soup.find("div", {"id": "unqualifiedBuyBox"})
    add_to_cart = soup.find("input", {"id": "add-to-cart-button"})

    merchant_info = soup.find("div", {"id": "merchant-info"})
    if merchant_info:
        merchant_info = merchant_info.text.lstrip().rstrip().lower()

    if soldout_box or unqualified_box:
        return False
    elif (buy_box or add_to_cart) and merchant_info == SOLD_BY_AMAZON:
        return True
    return None


def _sony(soup):
    print("sony")


def supported():
    return DISPATCHER.keys()


def _dynamic_soup(domain, URL):
    options = webdriver.ChromeOptions()
    options.add_argument("headless")
    driver_path = "./webdrivers/chromedriver"
    driver = webdriver.Chrome(executable_path=driver_path, options=options)
    driver.get(URL)
    response = driver.page_source
    driver.close()
    return response


def scrape(domain, URL):
    if domain not in DISPATCHER.keys():
        return (
            f"'{domain}' is not a supported retailer. Try running supported() for list of our supported retailers",
        )
    else:
        if domain in [TARGET, AMAZON]:
            response = _dynamic_soup(domain, URL)
        else:
            response = requests.get(
                URL,
                headers=HEADERS,
                timeout=5,
            ).content
        soup = BeautifulSoup(response, "lxml")

        return DISPATCHER[domain](soup)
