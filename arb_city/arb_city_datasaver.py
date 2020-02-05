import asyncio
import websockets
import json
#from pprint import pprint
import time
import requests
import datetime
from twilio.rest import Client

msg = \
{
    "jsonrpc" : "2.0",
    "id" : 9344,
    "method" : "public/get_book_summary_by_currency",
    "params" : {
    "currency" : "BTC",
    "kind" : "future"
    }
}

sleep_time = 60
first_fail = True

async def call_deribit_btc_futures(msg):
    async with websockets.connect('wss://test.deribit.com/ws/api/v2') as websocket:
        await websocket.send(msg)
        response = await websocket.recv()
        #while websocket.open:
            #response = await websocket.recv()
            # do something with the response...
        #pprint(response)
        return(response)

def call_bitmex_btc_futures():
    xbt_sep = requests.get("https://testnet.bitmex.com/api/v1/instrument?symbol=XBTU19")
    xbt_dec = requests.get("https://testnet.bitmex.com/api/v1/instrument?symbol=XBTZ19")
    xbt_perp = requests.get("https://testnet.bitmex.com/api/v1/instrument?symbol=XBTUSD")
    return((xbt_sep.json()[0],xbt_dec.json()[0], xbt_perp.json()[0]))



counter = 0

while True:

    start = time.time()

    counter += 1

    try:
        print("\n\n\n**********Loop Starting: ", datetime.datetime.now(), " UTC")
        #Gets deribit sep27 [0], dec27 [1], and swap [2] prices
        btc_deribit = asyncio.run(call_deribit_btc_futures(json.dumps(msg)))
        btc_deribit = json.loads(btc_deribit)
        print("\nDeribit Done")

        #Gets bitmex perp swap, sep27, and dec27 prices
        bitmex_xbt_sep, bitmex_xbt_dec, bitmex_xbt_perp = call_bitmex_btc_futures()
        print("Bitmex Done")
        '''
        print("\n")
        print("Deribit Sep19 Ask: ", btc_deribit['result'][0]['ask_price'])
        print("Deribit Sep19 Bid: ", btc_deribit['result'][0]['bid_price'])
        print("Bitmex Sep19 Ask: ", btc_bitmex['askPrice'])
        print("Bitmex Sep19 Bid: ", btc_bitmex['bidPrice'])
        '''

        #Saves sep27 futures prices

        with open("/home/ngancitano/bitgain/testnet_data/arb_city_sep27.csv", "a") as file:
            print("\nSep27 start: ")

            file.write(str(time.time()))
            file.write(", ")
            file.write(str(btc_deribit['result'][0]['ask_price']))
            file.write(", ")
            file.write(str(btc_deribit['result'][0]['bid_price']))
            file.write(", ")
            file.write(str(bitmex_xbt_sep['askPrice']))
            file.write(", ")
            file.write(str(bitmex_xbt_sep['bidPrice']))
            file.write(", ")

            if (bitmex_xbt_sep['bidPrice'] > btc_deribit['result'][0]['ask_price']):
                spread = (bitmex_xbt_sep['bidPrice'] - btc_deribit['result'][0]['ask_price'])
                spread_percent = round(spread/btc_deribit['result'][0]['ask_price']*100, 4)
                print("Buy Deribit, Sell Bitmex")
                print("Deribit Ask: ", btc_deribit['result'][0]['ask_price'])
                print("BitMex Bid: ", bitmex_xbt_sep['bidPrice'])
                print("Spread: ", spread)
                print("Spread Percent: ", spread_percent)
                file.write(str(spread))
                file.write(", ")
                file.write(str(spread_percent))
                file.write(", Deribit, Bitmex\n")

            elif (btc_deribit['result'][0]['bid_price'] > bitmex_xbt_sep['askPrice']):
                spread = (btc_deribit['result'][0]['bid_price'] - bitmex_xbt_sep['askPrice'])
                spread_percent = round(spread/bitmex_xbt_sep['askPrice']*100, 4)
                print("\nBuy Bitmex, Sell Deribit")
                print("Bitmex Ask: ", bitmex_xbt_sep['askPrice'])
                print("Deribit Bid: ", btc_deribit['result'][0]['bid_price'])
                print("Spread: ", spread)
                print("Spread Percent: ", spread_percent)
                file.write(str(spread))
                file.write(", ")
                file.write(str(spread_percent))
                file.write(", Bitmex, Deribit\n")

        #Saves dec27 futures prices

        with open("/home/ngancitano/bitgain/testnet_data/arb_city_dec27.csv", "a") as file:
            print("\nDec27 start: ")

            file.write(str(time.time()))
            file.write(", ")
            file.write(str(btc_deribit['result'][1]['ask_price']))
            file.write(", ")
            file.write(str(btc_deribit['result'][1]['bid_price']))
            file.write(", ")
            file.write(str(bitmex_xbt_dec['askPrice']))
            file.write(", ")
            file.write(str(bitmex_xbt_dec['bidPrice']))
            file.write(", ")

            if (bitmex_xbt_dec['bidPrice'] > btc_deribit['result'][1]['ask_price']):
                spread = (bitmex_xbt_dec['bidPrice'] - btc_deribit['result'][1]['ask_price'])
                spread_percent = round(spread/btc_deribit['result'][1]['ask_price']*100, 4)
                print("Buy Deribit, Sell Bitmex")
                print("Deribit Ask: ", btc_deribit['result'][1]['ask_price'])
                print("BitMex Bid: ", bitmex_xbt_dec['bidPrice'])
                print("Spread: ", spread)
                print("Spread Percent: ", spread_percent)
                file.write(str(spread))
                file.write(", ")
                file.write(str(spread_percent))
                file.write(", Deribit, Bitmex\n")

            elif (btc_deribit['result'][1]['bid_price'] > bitmex_xbt_dec['askPrice']):
                spread = (btc_deribit['result'][1]['bid_price'] - bitmex_xbt_dec['askPrice'])
                spread_percent = round(spread/bitmex_xbt_dec['askPrice']*100, 4)
                print("\nBuy Bitmex, Sell Deribit")
                print("Bitmex Ask: ", bitmex_xbt_dec['askPrice'])
                print("Deribit Bid: ", btc_deribit['result'][1]['bid_price'])
                print("Spread: ", spread)
                print("Spread Percent: ", spread_percent)
                file.write(str(spread))
                file.write(", ")
                file.write(str(spread_percent))
                file.write(", Bitmex, Deribit\n")

        #Saves swaps prices

        with open("/home/ngancitano/bitgain/testnet_data/arb_city_swaps.csv", "a") as file:
            print("\nPerp start: ")

            file.write(str(time.time()))
            file.write(", ")
            file.write(str(btc_deribit['result'][2]['ask_price']))
            file.write(", ")
            file.write(str(btc_deribit['result'][2]['bid_price']))
            file.write(", ")
            file.write(str(bitmex_xbt_perp['askPrice']))
            file.write(", ")
            file.write(str(bitmex_xbt_perp['bidPrice']))
            file.write(", ")

            if (bitmex_xbt_perp['bidPrice'] > btc_deribit['result'][2]['ask_price']):
                spread = (bitmex_xbt_perp['bidPrice'] - btc_deribit['result'][2]['ask_price'])
                spread_percent = round(spread/btc_deribit['result'][2]['ask_price']*100, 4)
                print("Buy Deribit, Sell Bitmex")
                print("Deribit Ask: ", btc_deribit['result'][2]['ask_price'])
                print("BitMex Bid: ", bitmex_xbt_perp['bidPrice'])
                print("Spread: ", spread)
                print("Spread Percent: ", spread_percent)
                file.write(str(spread))
                file.write(", ")
                file.write(str(spread_percent))
                file.write(", Deribit, Bitmex\n")

            elif (btc_deribit['result'][2]['bid_price'] > bitmex_xbt_perp['askPrice']):
                spread = (btc_deribit['result'][2]['bid_price'] - bitmex_xbt_perp['askPrice'])
                spread_percent = round(spread/bitmex_xbt_perp['askPrice']*100, 4)
                print("\nBuy Bitmex, Sell Deribit")
                print("Bitmex Ask: ", bitmex_xbt_perp['askPrice'])
                print("Deribit Bid: ", btc_deribit['result'][2]['bid_price'])
                print("Spread: ", spread)
                print("Spread Percent: ", spread_percent)
                file.write(str(spread))
                file.write(", ")
                file.write(str(spread_percent))
                file.write(", Bitmex, Deribit\n")

            else:
                print("Swap prices equal")
                spread = 0
                spread_percent = 0
                print("Spread: ", spread)
                print("Spread Percent: ", spread_percent)
                file.write(str(spread))
                file.write(", ")
                file.write(str(spread_percent))
                file.write(", None, None\n")

        runtime = (time.time() - start)
        print("\nRuntime: ", runtime)
        print("Sleeping ", (sleep_time - runtime), "seconds")
        try:
            time.sleep((sleep_time - runtime))
        except:
            time.sleep(sleep_time)
    except Exception as e:
        print(f"\n\n\n**********Loop Failed: {datetime.datetime.now()} UTC")
        print(f"Error: {e}")

        if first_fail == True and counter > 180: # hasn't failed in over 3 hours to reduce spamming notifications
            twil = Client('ACaca0530e4b2efeb483ab6d2519c827b8', '828fc311030c32fbf960b69d9d8f1e0b')

            message = twil.messages.create(
                        body=f"Arb City Test Failed",
                        from_='+12054420287',
                        to='+19733930439')

            print(message.sid)
            first_fail = False

        counter = 0 # resets counter since last fail

        runtime = (time.time() - start)
        print(f"\nRuntime: {runtime}")
        print(f"Sleeping {(sleep_time - runtime)} seconds")
        try:
            time.sleep((sleep_time - runtime))
        except:
            time.sleep(sleep_time)