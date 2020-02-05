'''import bitmex

public = '7qiRqic8L8DYMNmArH-8jBHV'
secret = 'zpW3GF2Dhztv7k1mrmwpMxbUAsYYsLgQkEE14--77Y5LrC45'
client = bitmex.bitmex(api_key=public, api_secret=secret)

result = client.Quote.Quote_get(symbol="XBTUSD", reverse=True, count=1).result()
print(result[0][0]['bidPrice'])
'''


import requests, json, pprint
import pandas as pd

def call_bitmex_btc_futures():
	xbt_sep = requests.get("https://www.bitmex.com/api/v1/instrument?symbol=XBTU19")
	xbt_dec = requests.get("https://www.bitmex.com/api/v1/instrument?symbol=XBTZ19")
	xbt_perp = requests.get("https://www.bitmex.com/api/v1/instrument?symbol=XBTUSD")
	return((xbt_sep.json()[0],xbt_dec.json()[0], xbt_perp.json()[0]))

bitmex_xbt_sep, bitmex_xbt_dec, bitmex_xbt_perp = call_bitmex_btc_futures()

pprint.pprint(bitmex_xbt_sep)
pprint.pprint(bitmex_xbt_dec)
pprint.pprint(bitmex_xbt_perp)



'''
print("sep requested")
xbt_sep = requests.get("https://www.bitmex.com/api/v1/instrument?symbol=XBTU19")
print("sep done")
print("dec requested")
xbt_dec = requests.get("https://www.bitmex.com/api/v1/instrument?symbol=XBTZ19")
pprint.pprint(xbt_sep.json()[0]) #index 0 because list of 1 object
#print(type(r.json()[0]))
pprint.pprint(xbt_dec.json()[0])
'''


#response = requests.get("https://www.bitmex.com/api/v1/instrument?filter=%7B%22state%22%3A%20%22Open%22%7D")
#pprint.pprint(response.text)

'''
response = requests.get("https://www.bitmex.com/api/v1/orderBook/L2?symbol=xbt&depth=5").json()
ether_ask_price = response[0]['price']
ether_bid_price = response[1]['price']
print(ether_ask_price)
print(ether_bid_price)

pprint.pprint(response)
print(len(response))
'''

#quote = pd.read_csv('C:/Users/ngancitano/Downloads/20190724/quote_20190724.csv')
#print(quote.head())
#print(quote.shape)

#trade = pd.read_csv('C:/Users/ngancitano/Downloads/20190724_trade/trade_20190724.csv')
#print(trade.head())
#print(trade.shape)