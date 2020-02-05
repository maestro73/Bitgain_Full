import requests, asyncio#, websocket
from pprint import pprint
from arb_city import get_all_open_positions, get_open_sizes, liquidate_all
from deribit_funcs import close_deribit_d27, call_deribit_btc_futures, call_deribit_market, call_deribit_limit, get_open_by_instrument
from bitmex_funcs import place_bitmex_market, place_bitmex_limit, get_bitmex_opens, get_bitmex_positions, close_bitmex_positions
from time import time
from datetime import datetime
import pandas as pd
#from twilio.rest import Client

'''
bitmex_response, deribit_response = liquidate_all()
print("Bitmex...")
pprint(bitmex_response)

print("Deribit...")
pprint(deribit_response)
'''


#from bitmex_websocket import BitMEXWebsocket
#ws = BitMEXWebsocket(endpoint='https://testnet.bitmex.com/api/v1', symbol='XBTUSD', api_key='x48r7VjMUus3QyYZjPMEKF-V', api_secret='WYnTxTvSIKNou8FBXK-9cJtjFlQhWiaFdmJJN-se4UaCnYQW')
'''
bitmex = requests.get("https://testnet.bitmex.com/api/v1/instrument?symbol=XBTZ19").json()[0]
bm_ask_d27 = bitmex['askPrice']
bm_bid_d27 = bitmex['bidPrice']
limit_bid = bm_ask_d27 + 1

place_bitmex_limit(price=limit_bid)
'''
#liquidate_all()

'''
path = 'arb_city_dec27.csv'
csv_ = pd.read_csv(path, index_col='Epoch', engine='python', skipinitialspace=True, error_bad_lines=False, warn_bad_lines=False).iloc[-20160:]
print(csv_.shape)
'''


#r = place_bitmex_market(side='Sell', qty=300)
#order_id = r['result']['order']
#pprint(r)
#print("Order ID: ", order_id)

#p = close_bitmex_positions()
#pprint(p)
'''
#start = time()
ts = datetime.fromtimestamp(time()).strftime('%c')#('%Y-%m-%d %I:%M:%S %p %Z')
print(type(ts))
print(ts)

start_time = time()
with open("time_testing.txt", 'a') as file:
	print(f"Opening time {time()-start_time}")
	file.write("One line")
	print(f"Write time {time()-start_time}")
print(f"Runtime {time()-start_time}")
'''
#liquidate_all()

#pprint(r)

#pprint(asyncio.run(get_open_by_instrument('BTC-27DEC19')))