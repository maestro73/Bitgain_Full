import ccxt
from pprint import pprint
ROUNDING = 4

fees = {
	'bitmex': {
		'maker': -0.00025,
		'taker': 0.00075
	},
	'bitmex_swaps': {
		'maker': -0.00025,
		'taker': 0.00075
	},
	'bitmex_futures': {
		'maker': -0.00025,
		'taker': 0.00075
	},
	'deribit_swaps': {
		'maker': -0.00025,
		'taker': 0.00075
	},
	'deribit_futures': {
		'maker': -0.0002,
		'taker': 0.0005
	},
	'okex_swaps': {
		'maker': 0.0002,
		'taker': 0.00075
	},
	'okex_futures': {
		'maker': 0.0002,
		'taker': 0.0005
	}
}
#print(ccxt.exchanges)

#TODO: incorporate FEES & calculate max potential percentage with 10x leverage
#TODO: incorporate slippage! how though????


'''
bitmex = ccxt.bitmex()
bitmex_markets = bitmex.load_markets()
bitmex_sep = bitmex_markets['XBTU19']
bitmex_dec = bitmex_markets['XBTZ19']
bitmex_perp = bitmex_markets['BTC/USD']
#pprint(bitmex_markets)

deribit = ccxt.deribit()
deribit_markets = deribit.load_markets()
deribit_sep = deribit_markets['BTC-27SEP19']
deribit_dec = deribit_markets['BTC-27DEC19']
deribit_perp = deribit_markets['BTC-PERPETUAL']

okex = ccxt.okex()
okex_markets = okex.load_markets()
okex_sep = okex_markets['BTC-USD-190927']
#okex_dec = okex_markets['BTC-27DEC19']
#okex_perp = okex_markets['BTC-PERPETUAL']
'''

bitmex = ccxt.bitmex()
deribit = ccxt.deribit()
okex = ccxt.okex3()

deribit_markets = deribit.load_markets()['BTC-27SEP19']
#pprint(deribit_markets)

#pprint(okex.load_markets())
#bitmex.urls['api'] = bitmex.urls['test']
#print(bitmex.load_markets())
bitmex_sep_book = bitmex.fetchOrderBook('XBTU19', limit=10000)
bitmex_dec_book = bitmex.fetchOrderBook('XBTZ19', limit=10000)
bitmex_perp_book = bitmex.fetchOrderBook('BTC/USD', limit=10000)

deribit_sep_book = deribit.fetchOrderBook('BTC-27SEP19', limit=10000)
deribit_dec_book = deribit.fetchOrderBook('BTC-27DEC19', limit=10000)
deribit_perp_book = deribit.fetchOrderBook('BTC-PERPETUAL', limit=10000)

okex_sep_book = okex.fetchOrderBook('BTC-USD-190927', limit=10000)
#okex_dec_book = okex.fetchOrderBook('XBTZ19', limit=10000)
#okex_perp_book = okex.fetchOrderBook('BTC-USD-SWAP', limit=10000)


print("Bitmex Sep Bid: ", bitmex_sep_book['bids'][0])
print("Deribit Sep Bid: ", deribit_sep_book['bids'][0])
print("Okex Sep Bid: ", okex_sep_book['bids'][0])
print("Bitmex Sep Ask: ", bitmex_sep_book['asks'][0])
print("Deribit Sep Ask: ", deribit_sep_book['asks'][0])
print("Okex Sep Ask: ", okex_sep_book['asks'][0])
max_sep_bid = max([bitmex_sep_book['bids'][0], deribit_sep_book['bids'][0], okex_sep_book['bids'][0]])
min_sep_ask = min([bitmex_sep_book['asks'][0], deribit_sep_book['asks'][0], okex_sep_book['asks'][0]])
print("Max Sep Bid: ", max_sep_bid)
print("Min Sep Ask: ", min_sep_ask)
print("Sep Spread: ", round(max_sep_bid[0]-min_sep_ask[0], ROUNDING))


print("\nBitmex Dec Bid: ", deribit_dec_book['bids'][0])
print("Deribit Dec Bid: ", deribit_dec_book['bids'][0])
#print("Okex Dec Bid: ", okex_dec_book['bids'][0])
print("Bitmex Dec Ask: ", bitmex_dec_book['asks'][0])
print("Deribit Dec Ask: ", deribit_dec_book['asks'][0])
#print("Okex Dec Ask: ", okex_dec_book['asks'][0])
max_dec_bid = max([bitmex_dec_book['bids'][0], deribit_dec_book['bids'][0]])
min_dec_ask = min([bitmex_dec_book['asks'][0], deribit_dec_book['asks'][0]])
print("Max Dec Bid: ", max_dec_bid)
print("Min Dec Ask: ", min_dec_ask)
print("Dec Spread: ", round(max_dec_bid[0]-min_dec_ask[0], ROUNDING))


print("\nBitmex Perp Bid: ", bitmex_perp_book['bids'][0])
print("Deribit Perp Bid: ", deribit_perp_book['bids'][0])
#print("Okex Perp Bid: ", okex_perp_book['bids'][0])
print("Bitmex Perp Ask: ", bitmex_perp_book['asks'][0])
print("Deribit Perp Ask: ", deribit_perp_book['asks'][0])
#print("Okex Perp Ask: ", okex_perp_book['asks'][0])
max_perp_bid = max([bitmex_perp_book['bids'][0], deribit_perp_book['bids'][0]])#, okex_perp_book['bids'][0]])
min_perp_ask = min([bitmex_perp_book['asks'][0], deribit_perp_book['asks'][0]])#, okex_perp_book['asks'][0]])
print("Max Perp Bid: ", max_perp_bid)
print("Min Perp Ask: ", min_perp_ask)
print("Perp Spread: ", round(max_perp_bid[0]-min_perp_ask[0], ROUNDING))

#pprint(bitmex_sep_book)
#print(bitmex.urls)

