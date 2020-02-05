import asyncio, websockets, json, time, requests
from pprint import pprint
from bitmex_api_scripts import bitmex

bitmex_public = 'x48r7VjMUus3QyYZjPMEKF-V'
bitmex_secret = 'WYnTxTvSIKNou8FBXK-9cJtjFlQhWiaFdmJJN-se4UaCnYQW'

def get_bitmex_btc_futures(test = True):
	www = 'testnet'
	if not test:
		www = 'www'
	xbt_sep = requests.get(f"https://{www}.bitmex.com/api/v1/instrument?symbol=XBTU19")
	xbt_dec = requests.get(f"https://{www}.bitmex.com/api/v1/instrument?symbol=XBTZ19")
	xbt_perp = requests.get(f"https://{www}.bitmex.com/api/v1/instrument?symbol=XBTUSD")
	return((xbt_sep.json()[0],xbt_dec.json()[0], xbt_perp.json()[0]))

def place_bitmex_market(side='Buy', symbol='XBTZ19',qty=1000, test=True, bitmex_public = 'x48r7VjMUus3QyYZjPMEKF-V', bitmex_secret = 'WYnTxTvSIKNou8FBXK-9cJtjFlQhWiaFdmJJN-se4UaCnYQW'):
	bitmex_client = bitmex(test=test, api_key=bitmex_public, api_secret=bitmex_secret)
	return(bitmex_client.Order.Order_new(side=side, symbol=symbol, orderQty=qty, ordType='Market').result())
'''
def place_bitmex_limit(price, side='Buy', symbol='XBTZ19', qty=1000):
	bitmex_client = bitmex(test=True, api_key=bitmex_public, api_secret=bitmex_secret)
	bitmex_client.Order.Order_new(side=side, symbol=symbol, orderQty=qty, ordType='Limit', price=price, clOrdID='abc123xyz').result()
'''
def place_bitmex_limit(price, side='Buy', symbol='XBTZ19', qty=1000, test=True, bitmex_public = 'x48r7VjMUus3QyYZjPMEKF-V', bitmex_secret = 'WYnTxTvSIKNou8FBXK-9cJtjFlQhWiaFdmJJN-se4UaCnYQW'):
	bitmex_client = bitmex(test=test, api_key=bitmex_public, api_secret=bitmex_secret)
	return(bitmex_client.Order.Order_new(side=side, symbol=symbol, orderQty=qty, ordType='Limit', price=price).result())

def place_bitmex_limit_and_wait(price, side='Buy', symbol='XBTZ19', qty=1000, test=True, bitmex_public = 'x48r7VjMUus3QyYZjPMEKF-V', bitmex_secret = 'WYnTxTvSIKNou8FBXK-9cJtjFlQhWiaFdmJJN-se4UaCnYQW'):
	bitmex_client = bitmex(test=test, api_key=bitmex_public, api_secret=bitmex_secret)
	bitmex_limit = bitmex_client.Order.Order_new(side=side, symbol=symbol, orderQty=qty, ordType='Limit', price=price).result() # , clOrdID='abc123' parameter optional
	return()

def get_bitmex_opens(test=True, bitmex_public = 'x48r7VjMUus3QyYZjPMEKF-V', bitmex_secret = 'WYnTxTvSIKNou8FBXK-9cJtjFlQhWiaFdmJJN-se4UaCnYQW'):
	bitmex_client = bitmex(test=test, api_key=bitmex_public, api_secret=bitmex_secret)
	return(bitmex_client.Order.Order_getOrders(filter='{\"open\": true}').result())

def bitmex_cancel_all(test=True, bitmex_public = 'x48r7VjMUus3QyYZjPMEKF-V', bitmex_secret = 'WYnTxTvSIKNou8FBXK-9cJtjFlQhWiaFdmJJN-se4UaCnYQW'):
	bitmex_client = bitmex(test=test, api_key=bitmex_public, api_secret=bitmex_secret)
	return(bitmex_client.Order.Order_cancelAll().result())

def bitmex_cancel(test=True, bitmex_public = 'x48r7VjMUus3QyYZjPMEKF-V', bitmex_secret = 'WYnTxTvSIKNou8FBXK-9cJtjFlQhWiaFdmJJN-se4UaCnYQW'):
	bitmex_client = bitmex(test=test, api_key=bitmex_public, api_secret=bitmex_secret)
	return(bitmex_client.Order.Order_cancel().result())

def get_bitmex_positions(test=True, bitmex_public = 'x48r7VjMUus3QyYZjPMEKF-V', bitmex_secret = 'WYnTxTvSIKNou8FBXK-9cJtjFlQhWiaFdmJJN-se4UaCnYQW'):
	bitmex_client = bitmex(test=test, api_key=bitmex_public, api_secret=bitmex_secret)
	return(bitmex_client.Position.Position_get().result())

def close_bitmex_positions(test=True, bitmex_public = 'x48r7VjMUus3QyYZjPMEKF-V', bitmex_secret = 'WYnTxTvSIKNou8FBXK-9cJtjFlQhWiaFdmJJN-se4UaCnYQW'):
	bitmex_client = bitmex(test=test, api_key=bitmex_public, api_secret=bitmex_secret)
	return(bitmex_client.Order.Order_closePosition(symbol="XBTZ19").result())