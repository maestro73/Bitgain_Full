import requests
from pprint import pprint

#r = requests.get("http://localhost:4444")#/instrument?symbol=XBTUSD")
r = requests.get("http://localhost:4444/orderBookL2?symbol=XBTUSD")
#try:
	#pprint(r.json())
#except:
	#print(r.text)

print(type(r.json()))

#for x in r.json():
	#print(x)

sells = sorted([x for x in r.json() if x['side']=='Sell'], key = lambda i: i['price'])
buys = sorted([x for x in r.json() if x['side']=='Buy'], key = lambda i: i['price'],reverse=True)
print("Sell orders: ", len(sells))
print("Buy orders: ", len(buys))

print("Asking: ", sells[0]['price'])
print("Bidding: ", buys[0]['price'])
print("Trading: ", (sells[0]['price']+buys[0]['price'])/2)

top_size = 100
top_size_small = int(top_size/10)
top_size_large = int(top_size*10)

top_sells_medium = sum([x['price']*x['size'] for x in sells[:top_size]])
top_sells_small = sum([x['price']*x['size'] for x in sells[:top_size_small]])
top_sells_large = sum([x['price']*x['size'] for x in sells[:top_size_large]])

top_buys_medium = sum([x['price']*x['size'] for x in buys[:top_size]])
top_buys_small = sum([x['price']*x['size'] for x in buys[:top_size_small]])
top_buys_large = sum([x['price']*x['size'] for x in buys[:top_size_large]])

print("Top sells small: ", top_sells_small)
print("Top buys small:  ", top_buys_small)
print("Top sells medium: ", top_sells_medium)
print("Top buys medium:  ", top_buys_medium)
print("Top sells large: ", top_sells_large)
print("Top buys large:  ", top_buys_large)

if (top_sells_small > top_buys_small):
	print("Small SELLS")
else:
	print("Small BUYS")

if (top_sells_medium > top_buys_medium):
	print("Medium SELLS")
else:
	print("Medium BUYS")

if (top_sells_large > top_buys_large):
	print("Large SELLS")
else:
	print("Large BUYS")

print("10th sell price: ", sells[10]['price'], "   Pct: ", (sells[10]['price']-sells[0]['price'])/sells[0]['price']*100)
print("100th sell price: ", sells[100]['price'], "   Pct: ", (sells[100]['price']-sells[0]['price'])/sells[0]['price']*100)
print("500th sell price: ", sells[500]['price'], "   Pct: ", (sells[500]['price']-sells[0]['price'])/sells[0]['price']*100)
print("Max sell price: ", sells[len(sells)-1]['price'], "   Pct: ", (sells[len(sells)-1]['price']-sells[0]['price'])/sells[0]['price']*100)

print("10th buy price: ", buys[10]['price'], "   Pct: ", (buys[10]['price']-buys[0]['price'])/buys[0]['price']*100)
print("100th buy price: ", buys[100]['price'], "   Pct: ", (buys[100]['price']-buys[0]['price'])/buys[0]['price']*100)
print("500th buy price: ", buys[500]['price'], "   Pct: ", (buys[500]['price']-buys[0]['price'])/buys[0]['price']*100)
print("Max buy price: ", buys[len(buys)-1]['price'], "   Pct: ", (buys[len(buys)-1]['price']-buys[0]['price'])/buys[0]['price']*100)


#s = requests.get("https://testnet.bitmex.com/api/explorer/swagger.json")
#pprint(s.json())

#TODO: derive ML input values based on above order book
###Ex1: sum of top 10/100/1000 buys/sells

#print((110-100)/100*100)