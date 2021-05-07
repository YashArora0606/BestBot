import requests
import json
import boto3
from datetime import datetime
import time
import asyncio
import aiohttp

POSTAL_CODE = 'L4B4P4'

PRODUCT_CODES = [
    "15309513",
    "15309514",
    "15317226",
    "15318940",
    "15373182",
    "15324508",
    "15309503",
    "15309504",
    "15166285",
    "15229237",
    "15178453",
    "14584744"
]

RETRY_SECONDS = 0.1
TIMEOUT_SECONDS = 20

API_URL = 'https://www.bestbuy.ca/ecomm-api/availability/products?accept=application%2Fvnd.bestbuy.standardproduct.v1%2Bjson&accept-language=en-CA&locations=219%7C608%7C235%7C935%7C995%7C247%7C631%7C620&postalCode=' + POSTAL_CODE + '&skus='
SEARCH_URL = 'https://www.bestbuy.ca/en-ca/product/'

# HEADERS = {
#     'authority': 'www.bestbuy.ca',
#     'pragma': 'no-cache',
#     'cache-control': 'no-cache',
#     'user-agent': 'Mozilla/5.0 (Windows NT 11.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/85.0.4159.2 Safari/537.36',
#     'accept': '*/*',
#     'sec-fetch-site': 'same-origin',
#     'sec-fetch-mode': 'cors',
#     'sec-fetch-dest': 'empty',
#     'referer': 'https://www.bestbuy.ca/en-ca/',
#     'accept-language': 'en-US,en;q=0.9'
# }

HEADERS = {
    'user-agent': 'Mozilla/5.0 (Windows NT 11.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/85.0.4159.2 Safari/537.36',
}


FOUND = False


async def findProduct(product_code, session):
    url = API_URL + product_code
    global ATTEMPTS
    global FOUND
    try:
        async with session.get(url=url, headers=HEADERS) as response:
            resp = await response.read()

            response_formatted = json.loads(
                resp.decode('utf-8-sig').encode('utf-8'))
            quantity = response_formatted['availabilities'][0]['shipping']['quantityRemaining']

            if (quantity < 1):

                print(product_code + " out of Stock.\tAttempt: " +
                      str(ATTEMPTS) + "\tTime: " + str(datetime.now()) + "\tURL: " + SEARCH_URL + product_code)
            else:
                FOUND = True
                print("FOUND " + str(quantity) +
                      " AVAILABLE AT " + SEARCH_URL + product_code)

    except Exception as e:
        print("Unable to get url {} due to {}.".format(url, e))


async def main():

    global ATTEMPTS
    global FOUND
    ATTEMPTS = 1
    FOUND = 0

    async with aiohttp.ClientSession() as session:

        while (not FOUND):
            ret = await asyncio.gather(*[findProduct(product_code, session) for product_code in PRODUCT_CODES])
            ATTEMPTS += 1
            time.sleep(RETRY_SECONDS)

asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
asyncio.run(main())
