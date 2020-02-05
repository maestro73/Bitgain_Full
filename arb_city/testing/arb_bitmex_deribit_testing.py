import asyncio
import websockets
import json
#from pprint import pprint
import time
import requests
from bitmex_api_scripts import bitmex
from pprint import pprint

bitmex_public = 'x48r7VjMUus3QyYZjPMEKF-V'
bitmex_secret = 'WYnTxTvSIKNou8FBXK-9cJtjFlQhWiaFdmJJN-se4UaCnYQW'

deribit_public = 'vwfyxeIV'
deribit_secret = 'RhGoowkhuL5Y-HqEqyzIU0Ss1UmKTg4v5DghS6Ld8iE'

def bitmex_test_market(symbol='XBTUSD',qty=1000):
    bitmex_client = bitmex(test=True, api_key=bitmex_public, api_secret=bitmex_secret)
    bitmex_client.Order.Order_new(side='Buy', symbol=symbol, orderQty=qty, ordType='Market').result()

async def call_deribit_market(key, secret):

    auth_msg = {
        "jsonrpc" : "2.0",
        "id" : 9929,
        "method" : "public/auth",
        "params" : {
            "grant_type" : "client_credentials",
            "client_id" : key,
            "client_secret" : secret
        }
    }

    buy_msg = \
        {   
        "jsonrpc" : "2.0",
        "id" : 5275,
        "method" : "private/buy",
        "params" : {
        "instrument_name" : "BTC-PERPETUAL",
        "amount" : 9000,
        "type" : "market",
        "label" : "market0000234"
        }
    }

    async with websockets.connect('wss://test.deribit.com/ws/api/v2') as websocket:
        await websocket.send(json.dumps(auth_msg))
        response1 = await websocket.recv()
        
        await websocket.send(json.dumps(buy_msg))
        #while websocket.open:
        response2 = await websocket.recv()
        # do something with the response...
        pprint(json.loads(response1))
        pprint(json.loads(response2))


async def call_deribit_auth(key, secret):

    auth_msg = {
        "jsonrpc" : "2.0",
        "id" : 9929,
        "method" : "public/auth",
        "params" : {
            "grant_type" : "client_credentials",
            "client_id" : key,
            "client_secret" : secret
        }
    }

    async with websockets.connect('wss://test.deribit.com/ws/api/v2') as websocket:
        await websocket.send(json.dumps(auth_msg))
        #while websocket.open:
        response = await websocket.recv()
        # do something with the response...
        pprint(json.loads(response))

async def call_deribit_btc_futures():

    msg = {
        "jsonrpc" : "2.0",
        "id" : 9344,
        "method" : "public/get_book_summary_by_currency",
            "params" : {
            "currency" : "BTC",
            "kind" : "future"
        }
    }

    async with websockets.connect('wss://test.deribit.com/ws/api/v2') as websocket:
        await websocket.send(msg)
        response = await websocket.recv()
        #while websocket.open:
            #response = await websocket.recv()
            # do something with the response...
        #pprint(response)
        return(response)

def call_bitmex_btc_futures():
    xbt_sep = requests.get("https://www.bitmex.com/api/v1/instrument?symbol=XBTU19")
    xbt_dec = requests.get("https://www.bitmex.com/api/v1/instrument?symbol=XBTZ19")
    xbt_perp = requests.get("https://www.bitmex.com/api/v1/instrument?symbol=XBTUSD")
    return((xbt_sep.json()[0],xbt_dec.json()[0], xbt_perp.json()[0]))

def spread_writer(dates=['sep27','dec27','swaps']): # dates[] will have to change with new futures dates symbols
    ttime = 0
    date_count = 0

    dbit_start = time.time()
    deribit = asyncio.run(call_deribit_btc_futures(json.dumps(msg)))
    deribit = json.loads(deribit)
    print("Deribit Done")
    print(f"Deribit Time: {(time.time()-dbit_start)}")


    for date in dates:
        start = time.time()

        if date == 'swaps': # i don't like this, hacky
            bitmex = requests.get("https://www.bitmex.com/api/v1/instrument?symbol=XBTUSD").json()[0]
        elif date == 'sep27': 
            bitmex = requests.get("https://www.bitmex.com/api/v1/instrument?symbol=XBTU19").json()[0]
        elif date == 'dec27':
            bitmex = requests.get("https://www.bitmex.com/api/v1/instrument?symbol=XBTZ19").json()[0]
        print(f"\n{date} start: ")
        print("Bitmex Done")
        


        with open(f"arb_city_{date}_func.csv", "a") as file:


            file.write(str(deribit['result'][date_count]['ask_price']))
            file.write(", ")
            file.write(str(deribit['result'][date_count]['bid_price']))
            file.write(", ")
            file.write(str(bitmex['askPrice']))
            file.write(", ")
            file.write(str(bitmex['bidPrice']))
            file.write(", ")

            if (bitmex['bidPrice'] > deribit['result'][date_count]['ask_price']):
                spread = (bitmex['bidPrice'] - deribit['result'][date_count]['ask_price'])
                spread_percent = round(spread/deribit['result'][date_count]['ask_price']*100, 4)
                print("Buy Deribit, Sell Bitmex")
                print("Spread: ", spread)
                print("Spread Percent: ", spread_percent)
                file.write(str(spread))
                file.write(", ")
                file.write(str(spread_percent))
                file.write(", Deribit, Bitmex\n")

            elif (deribit['result'][date_count]['bid_price'] > bitmex['askPrice']):
                spread = (deribit['result'][date_count]['bid_price'] - bitmex['askPrice'])
                spread_percent = round(spread/bitmex['askPrice']*100, 4)
                print("Buy Bitmex, Sell Deribit")
                print("Spread: ", spread)
                print("Spread Percent: ", spread_percent)
                file.write(str(spread))
                file.write(", ")
                file.write(str(spread_percent))
                file.write(", Bitmex, Deribit\n")

            else:
                print("\n Prices Equal")
                spread = 0
                spread_percent = 0
                print("Buy Bitmex, Sell Deribit")
                print("Spread: ", spread)
                print("Spread Percent: ", spread_percent)
                file.write(str(spread))
                file.write(", ")
                file.write(str(spread_percent))
                file.write(", None, None\n")

        date_count += 1
        ttime += (time.time() - start)
        print("Runtime: ", time.time()-start)

    runtime = (time.time() - start)
    print("\nRuntime: ", runtime)
    print("ttime: ", ttime)
    #print("Sleeping ", (60 - runtime), "seconds")
    #time.sleep((60 - runtime))



if __name__ == "__main__":
    '''
    counter = 0
    while counter < 1:
        spread_writer()

        counter += 1
    '''

    if (requests.get('http://ipinfo.io').json()['country'] != 'US'):
        print("Not in US")

        #bitmex_test_market() #bitmex buy func
        asyncio.run(call_deribit_market(deribit_public, deribit_secret)) #deribit buy func
        

    else:
        print("In US")
        print("Try Again")