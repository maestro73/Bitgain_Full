import asyncio, websockets, json, time, requests
from pprint import pprint
from bitmex_api_scripts import bitmex
from bitmex_funcs import place_bitmex_market, get_bitmex_opens, place_bitmex_limit, close_bitmex_positions
from deribit_funcs import call_deribit_market, call_deribit_btc_futures, close_deribit_d27
import pandas
from twilio.rest import Client

#import this_fails_on_purpose
TEST = True
PURCHASE_AMOUNT = 1000
SLEEP_TIME = 60

#TODO 00: for each trade: compare bd_bid/ask_d27 with actual returned fill price
#   This will help determine slippage!
#TODO 05: incorporate 'old' arb_city/arb_city_test data-scrapers into this script
#   This will allow 1 script to do it all!
#TODO DONE??? 10: get avg close prices, include in twilio sms (currently only included for open prices)
#TODO 20: move send_twilio_sms() & log_city() into important functions, instead of in script
#TODO 30: incorporate sleep(60-runtime())
#TODO 40: implement limit & wait order functions (first order only to start) to save on maker/taker fee
    #this will greatly narrow the spread margin for a profitable trade (~0.4% --> ~0.1%)
#TODO 50: if spread continues to seperate, then open more
    #ex: buy at 0.5%, 1%, 1.5% then on the way back down sell at 1.1%, 0.6%, 0.1%
    # these percentages should be replaces with quartiles of normal distribution
    # see https://medium.com/okex-blog/calendar-spread-arbitrage-strategy-report-9128a5232aa5
#TODO 60: phase out emergency liquidation in favor of qty_balancing()
#TODO 70: write qty_balancing()
def liquidate_all(test=True):
    pprint(get_open_sizes(test=test))
    bitmex_respone = close_bitmex_positions(test=test)
    deribit_response = asyncio.run(close_deribit_d27(test=test))
    pprint(get_open_sizes(test=test))
    return(bitmex_respone, deribit_response)

def print_spread_simple(bm_bid, bm_ask, db_bid, db_ask):
	if bm_bid > db_ask:
		print(f"*Sell Bitmex, Buy Deribit: Spread = {bm_bid-db_ask}")
	elif db_bid > bm_ask:
		print(f"*Sell Deribit, Buy Bitmex: Spread = {db_bid-bm_ask}")
	else:
		print("No spread right now. Try again later.")

# don't think this is used
# use spread_finder() instead
def print_spread_analysis(test=True):
    fees = {
        'bitmex': {'maker': -0.00025, 'taker': 0.00075},
        'bitmex_swaps': {'maker': -0.00025, 'taker': 0.00075},
        'bitmex_futures': {'maker': -0.00025, 'taker': 0.00075},
        'deribit_swaps': {'maker': -0.00025, 'taker': 0.00075},
        'deribit_futures': {'maker': -0.0002, 'taker': 0.0005},
        'okex_swaps': {'maker': 0.0002, 'taker': 0.00075},
        'okex_futures': {'maker': 0.0002, 'taker': 0.0005}
    }

    network = 'test'
    if not test:
        network = 'live'

    for contract_date in ['swaps','sep27','dec27']:
        start = time.time()
        path = f'/home/ngancitano/bitgain/{network}net_data/arb_city_{contract_date}.csv'
        print("\n*****", contract_date, "spread summary *****")

        csv_ = pandas.read_csv(path, index_col='Epoch', engine='python', skipinitialspace=True, error_bad_lines=False, warn_bad_lines=False)

        spread_describe = csv_[['Spread','SpreadPercent']].describe(percentiles=[.0001,.001,.005,.01,.02,.05,.1,.25,.5,.75,.95,.98,.99,.995,.999,.9999])
        #print(csv_.describe(percentiles=[.01,.99]))

        #TODO: the below is written horribly, so not DRY, refactor at some point
        first_percentile = spread_describe.loc[['1%'],['Spread','SpreadPercent']].values
        second_percentile = spread_describe.loc[['2%'],['Spread','SpreadPercent']].values
        fifth_percentile = spread_describe.loc[['5%'],['Spread','SpreadPercent']].values
        _95th_percentile = spread_describe.loc[['95%'],['Spread','SpreadPercent']].values
        _98th_percentile = spread_describe.loc[['98%'],['Spread','SpreadPercent']].values
        _99th_percentile = spread_describe.loc[['99%'],['Spread','SpreadPercent']].values

        first_percentile_percentage = round(first_percentile[0][1],6)
        first_percentile = round(first_percentile[0][0], 4)
        second_percentile_percentage = round(second_percentile[0][1],6)
        second_percentile = round(second_percentile[0][0], 4)
        fifth_percentile_percentage = round(fifth_percentile[0][1],6)
        fifth_percentile = round(fifth_percentile[0][0], 4)
        _95th_percentile_percentage = round(_95th_percentile[0][1],6)
        _95th_percentile = round(_95th_percentile[0][0], 4)
        _98th_percentile_percentage = round(_98th_percentile[0][1],6)
        _98th_percentile = round(_98th_percentile[0][0], 4)
        _99th_percentile_percentage = round(_99th_percentile[0][1],6)
        _99th_percentile = round(_99th_percentile[0][0], 4)

        print(f"1st Percentile: {first_percentile}, {first_percentile_percentage}%")
        print(f"2nd Percentile: {second_percentile}, {second_percentile_percentage}%")
        print(f"5th Percentile: {fifth_percentile}, {fifth_percentile_percentage}%")
        print(f"95th Percentile: {_95th_percentile}, {_95th_percentile_percentage}%")
        print(f"98th Percentile: {_98th_percentile}, {_98th_percentile_percentage}%")
        print(f"99th Percentile: {_99th_percentile}, {_99th_percentile_percentage}%")
        print(f"99th-to-1st Spread: {round(_99th_percentile-first_percentile, 4)}, {round(_99th_percentile_percentage-first_percentile_percentage, 4)}%")
        print(f"98th-to-2nd Spread: {round(_98th_percentile-second_percentile, 4)}, {round(_98th_percentile_percentage-second_percentile_percentage, 4)}%")
        print(f"95th-to-5th Spread: {round(_95th_percentile-fifth_percentile, 4)}, {round(_95th_percentile_percentage-fifth_percentile_percentage, 4)}%")


        print(f"Runtime: {round((time.time()-start),4)} seconds")

# finds nearest percentiles that allow for profitable trades
# ex. if 80th - 20th percentile spread > fees then use those
### if not try 90-10, then 95-5, until profitability is found
def spread_finder(contract_date = 'dec27', test = True):

    network = 'test'
    if not test:
        network = 'live'

    start = time.time()
    #uncomment for pythonanywhere
    path = f'/home/ngancitano/bitgain/{network}net_data/arb_city_dec27.csv'
    #path = f'C:/Users/ngancitano/Documents/PythonProjects/bitmex/Py/arb_city_dec27_{network}.csv'
    #print("\n\n***** dec27 spread summary *****")

    csv_ = pandas.read_csv(path, index_col='Epoch', engine='python', skipinitialspace=True, error_bad_lines=False, warn_bad_lines=False).iloc[-20160:]

    spread_describe = csv_[['Spread','SpreadPercent']].describe(percentiles=[.0001,.001,.005,.01,.02,.05,.1,.15,.2,.25,.5,.75,.8,.85,.9,.95,.98,.99,.995,.999,.9999])
    #print(csv_.describe(percentiles=[.01,.99]))

    #TODO: the below is written horribly, so not DRY, refactor at some point
    first_percentile = spread_describe.loc[['1%'],['Spread','SpreadPercent']].values
    second_percentile = spread_describe.loc[['2%'],['Spread','SpreadPercent']].values
    fifth_percentile = spread_describe.loc[['5%'],['Spread','SpreadPercent']].values
    tenth_percentile = spread_describe.loc[['10%'],['Spread','SpreadPercent']].values
    _20th_percentile = spread_describe.loc[['20%'],['Spread','SpreadPercent']].values
    _80th_percentile = spread_describe.loc[['80%'],['Spread','SpreadPercent']].values
    _90th_percentile = spread_describe.loc[['90%'],['Spread','SpreadPercent']].values
    _95th_percentile = spread_describe.loc[['95%'],['Spread','SpreadPercent']].values
    _98th_percentile = spread_describe.loc[['98%'],['Spread','SpreadPercent']].values
    _99th_percentile = spread_describe.loc[['99%'],['Spread','SpreadPercent']].values

    first_percentile_percentage = round(first_percentile[0][1],6)
    first_percentile = round(first_percentile[0][0], 4)
    second_percentile_percentage = round(second_percentile[0][1],6)
    second_percentile = round(second_percentile[0][0], 4)
    fifth_percentile_percentage = round(fifth_percentile[0][1],6)
    fifth_percentile = round(fifth_percentile[0][0], 4)
    tenth_percentile_percentage = round(tenth_percentile[0][1],6)
    tenth_percentile = round(tenth_percentile[0][0],4)
    _20th_percentile_percentage = round(_20th_percentile[0][1],6)
    _20th_percentile = round(_20th_percentile[0][0], 4)
    _80th_percentile_percentage = round(_80th_percentile[0][1],6)
    _80th_percentile = round(_80th_percentile[0][0], 4)
    _90th_percentile_percentage = round(_90th_percentile[0][1],6)
    _90th_percentile = round(_90th_percentile[0][0], 4)
    _95th_percentile_percentage = round(_95th_percentile[0][1],6)
    _95th_percentile = round(_95th_percentile[0][0], 4)
    _98th_percentile_percentage = round(_98th_percentile[0][1],6)
    _98th_percentile = round(_98th_percentile[0][0], 4)
    _99th_percentile_percentage = round(_99th_percentile[0][1],6)
    _99th_percentile = round(_99th_percentile[0][0], 4)

    '''
    print(f"1st Percentile: {first_percentile}, {first_percentile_percentage}%")
    print(f"2nd Percentile: {second_percentile}, {second_percentile_percentage}%")
    print(f"5th Percentile: {fifth_percentile}, {fifth_percentile_percentage}%")
    print(f"10th Percentile: {tenth_percentile}, {tenth_percentile_percentage}%")
    print(f"20th Percentile: {_20th_percentile}, {_20th_percentile_percentage}%")
    print(f"80th Percentile: {_80th_percentile}, {_80th_percentile_percentage}%")
    print(f"90th Percentile: {_90th_percentile}, {_90th_percentile_percentage}%")
    print(f"95th Percentile: {_95th_percentile}, {_95th_percentile_percentage}%")
    print(f"98th Percentile: {_98th_percentile}, {_98th_percentile_percentage}%")
    print(f"99th Percentile: {_99th_percentile}, {_99th_percentile_percentage}%")
    print(f"99th-to-1st Spread: {round(_99th_percentile-first_percentile, 4)}, {round(_99th_percentile_percentage-first_percentile_percentage, 4)}%")
    print(f"98th-to-2nd Spread: {round(_98th_percentile-second_percentile, 4)}, {round(_98th_percentile_percentage-second_percentile_percentage, 4)}%")
    print(f"95th-to-5th Spread: {round(_95th_percentile-fifth_percentile, 4)}, {round(_95th_percentile_percentage-fifth_percentile_percentage, 4)}%")
    print(f"90th-to-10th Spread: {round(_90th_percentile-tenth_percentile, 4)}, {round(_90th_percentile_percentage-tenth_percentile_percentage, 4)}%")
    print(f"80th-to-20th Spread: {round(_80th_percentile-_20th_percentile, 4)}, {round(_80th_percentile_percentage-_20th_percentile_percentage, 4)}%")
    '''
    #print(f"Spread-finder Runtime: {round((time.time()-start),4)} seconds")

    if((_80th_percentile_percentage-_20th_percentile_percentage)>0.6):
        open_spread, close_spread = _80th_percentile, _20th_percentile
        spread_str = '80-20 Percentiles'
    elif ((_90th_percentile_percentage-tenth_percentile_percentage)>0.6):
        open_spread, close_spread = _90th_percentile, tenth_percentile
        spread_str = '90-10 Percentiles'
    elif ((_95th_percentile_percentage-fifth_percentile_percentage)>0.6):
        open_spread, close_spread = _95th_percentile, fifth_percentile
        spread_str = '95-05 Percentiles'
    elif ((_98th_percentile_percentage-second_percentile_percentage)>0.6):
        open_spread, close_spread = _98th_percentile, second_percentile
        spread_str = '98-02 Percentiles'
    else:
        open_spread, close_spread = _99th_percentile, first_percentile
        spread_str = '99-01 Percentiles'

    #dec27_tradeable = csv_.loc[(csv_['SpreadPercent'] <= first_percentile_percentage) | (csv_['SpreadPercent'] >= _99th_percentile_percentage)]
    #dec27_tradeable.to_csv("dec27_tradable.csv")
    print(f'\n\n*****New Spreads {spread_str}. Open: {open_spread}, Close: {close_spread}*****\n\n')
    return(open_spread, close_spread)

# gets dict of open positions (returns full json response)
async def get_all_open_positions(test = True):
    bitmex_client = bitmex(test=test, api_key='x48r7VjMUus3QyYZjPMEKF-V', api_secret='WYnTxTvSIKNou8FBXK-9cJtjFlQhWiaFdmJJN-se4UaCnYQW')
    bitmex_opens = bitmex_client.Position.Position_get().result()

    msg = {
        "jsonrpc" : "2.0",
        "id" : 404,
        "method" : "private/get_position",
        "params" : {
        "instrument_name" : "BTC-27DEC19"
        }
    }

    auth_msg = {
        "jsonrpc" : "2.0",
        "id" : 9929,
        "method" : "public/auth",
        "params" : {
            "grant_type" : "client_credentials",
            "client_id" : 'vwfyxeIV',
            "client_secret" : 'RhGoowkhuL5Y-HqEqyzIU0Ss1UmKTg4v5DghS6Ld8iE'
        }
    }

    api_url = 'wss://test.deribit.com/ws/api/v2'
    if test == False:
        api_url = 'wss://www.deribit.com/ws/api/v2'

    async with websockets.connect(api_url) as websocket:
        await websocket.send(json.dumps(auth_msg))
        response1 = await websocket.recv()
        await websocket.send(json.dumps(msg))
        response = await websocket.recv()
        # do something with the response...
        deribit_opens = (json.loads(response))

    return({'bitmex_opens': bitmex_opens,
        'deribit_opens': deribit_opens})

# gets dict of open positions (just order qty returned)
def get_open_sizes(test=True):
    r = asyncio.run(get_all_open_positions(test=test))
    try:
        db_d27_qty = r['deribit_opens']['result']['size']
    except:
        db_d27_qty = 'error'

    try:
        for _dict in r['bitmex_opens'][0]:
            if(_dict['symbol'] == 'XBTZ19'):
                bm_d27_qty = _dict['currentQty']
    except:
        bm_d27_qty = 'error'

    return({'bm_d27_qty': float(bm_d27_qty),
        'db_d27_qty': float(db_d27_qty)})

# gets current bitmex and deribit prices for dec27 future
def get_d27_prices(test=True):

    start_time = time.time()
    bitmex_url = "https://testnet.bitmex.com/api/v1/instrument?symbol=XBTZ19"
    if not test:
        bitmex_url = "https://www.bitmex.com/api/v1/instrument?symbol=XBTZ19"
    bitmex = requests.get(bitmex_url).json()[0]
    print(f'Bitmex Time: {(time.time()-start_time)}')
    bm_ask_d27 = bitmex['askPrice']
    bm_bid_d27 = bitmex['bidPrice']

    start_time = time.time()

    deribit = asyncio.run(call_deribit_btc_futures(test=test))
    print(f'Deribit Time: {(time.time()-start_time)}')
    db_ask_d27 = deribit['result'][0]['ask_price']
    db_bid_d27 = deribit['result'][0]['bid_price']

    print(f"Deribit Ask: {db_ask_d27}, Bid: {db_bid_d27}")
    print(f"Bitmex Ask: {bm_ask_d27}, Bid: {bm_bid_d27}")
    #print(spread_finder(bm_bid_d27, db_ask_d27))

    print_spread_simple(bm_bid_d27, bm_ask_d27, db_bid_d27, db_ask_d27)

    return(bm_ask_d27, bm_bid_d27, db_ask_d27, db_bid_d27)

# rudimentary logger
def log_city(message, filepath = f'/home/ngancitano/bitgain/arb_city/trading_logs', test=True):
    _tester = 'test'
    if not test:
        _tester = 'live'
    filepath = filepath + f'/arb_city_trader_log_{_tester}.txt'
    with open(filepath, 'a') as file:
        file.write(message)

# sends sms message when trades are executed
def send_twilio_message(_message, _from = '+12054420287', _to = '+19733930439'):
    twil = Client('ACaca0530e4b2efeb483ab6d2519c827b8', '828fc311030c32fbf960b69d9d8f1e0b')
    message = twil.messages.create(body=_message, from_=_from, to=_to)
    #return(message.sid)
    
    

if __name__ == "__main__":
    
    print(f'\nTrader Started: {time.time()}')

    #initialize twilio Client object for sending sms
    twil = Client('ACaca0530e4b2efeb483ab6d2519c827b8', '828fc311030c32fbf960b69d9d8f1e0b')
    
    # finds minimal acceptable spread percentile for trading thresholds
    (open_spread, close_spread) = spread_finder(test=TEST)
    
    # counter since percentile thresholds were updated
    loop_counter = 0

    #if(requests.get('http://ipinfo.io').json()['country'] != 'US'):
    #try:
    while True:

        print(f'\n\n\nLoop Started: {time.time()}')
        
        # updates spread percentiles thresholds once per day
        if loop_counter > 1440:
            (open_spread, close_spread) = spread_finder(test=TEST)

        # gets and prints current open sizes on both markets
        open_sizes_dict = get_open_sizes(test=TEST)
        bitmex_open = open_sizes_dict['bm_d27_qty']
        deribit_open = open_sizes_dict['db_d27_qty']
        print(f"Bitmex Open Qty: {bitmex_open}, Deribit Open Qty: {deribit_open}")

        # this may need to be moved up 1 level to outside 'while True' loop
        bitmex_client = bitmex(test=TEST, api_key='x48r7VjMUus3QyYZjPMEKF-V', api_secret='WYnTxTvSIKNou8FBXK-9cJtjFlQhWiaFdmJJN-se4UaCnYQW')
        while((deribit_open == 0) and (bitmex_open == 0)):

            print("\nBitmex & Deribit @ 0. Monitoring for OPENING oppurtunity")

            (bm_ask_d27, bm_bid_d27, db_ask_d27, db_bid_d27) = get_d27_prices(test=TEST)

            if((bm_bid_d27-db_ask_d27) > open_spread): #bitmex bid (sell) atleast 0.5% greater than deribit ask (buy)

                #TODO: implement limit_wait_til_filled() trades
                bitmex_response = place_bitmex_market(side='Sell', qty=PURCHASE_AMOUNT, test=TEST) # open bitmex short
                deribit_response = asyncio.run(call_deribit_market(size=PURCHASE_AMOUNT, test=TEST)) # open deribit long

                if(deribit_response['result']['order']['order_state'] == 'filled' and bitmex_response[0]['ordStatus'] == 'Filled'):

                    deribit_buy = deribit_response['result']['order']['average_price']
                    bitmex_sell = bitmex_response[0]['price']

                    order_message = f"Opening order submitted & filled. Deribit Buy: {deribit_buy}. Bitmex Sell: {bitmex_sell}."
                    send_twilio_message(_message=order_message)

                    print("***Spread Opened***")
                    print(f"Deribit Buy: {deribit_buy}")
                    print(f"Bitmex Sell: {bitmex_sell}")
                    #csv format: epoch, message, open/close, buy_side, sell_side, buy_price, sell_price
                    log_city(message=f'\n{time.time()}, Trade Opened, Open, Deribit, Bitmex, {db_ask_d27}, {bm_bid_d27}')
                    
                    open_sizes_dict = get_open_sizes(test=TEST)
                    bitmex_open = open_sizes_dict['bm_d27_qty']
                    deribit_open = open_sizes_dict['db_d27_qty']

                else:
                    print("***** UH OH! ONE OF THE ORDERS DID NOT FILL! LIQUIDATING AND RESTARTING SCRIPT!")
                    (bitmex_response, deribit_response) = liquidate_all(test=TEST)

                    #TODO: get avg close prices, include in twilio sms
                    send_twilio_message(_message="Order open failed. Emergency Liquidation.")
                    log_city(message=f'\n{time.time()}, Emergency Liquidation')
                    
                    open_sizes_dict = get_open_sizes(test=TEST)
                    bitmex_open = open_sizes_dict['bm_d27_qty']
                    deribit_open = open_sizes_dict['db_d27_qty']

            elif((db_bid_d27-bm_ask_d27) > open_spread): #deribit bid (sell) atleast 0.5% greater than bitmex ask (buy)

                bitmex_response = place_bitmex_market(qty=PURCHASE_AMOUNT, test=TEST) #open bitmex long
                deribit_response = asyncio.run(call_deribit_market(side='sell', size=PURCHASE_AMOUNT, test=TEST)) # open deribit short

                if(deribit_response['result']['order']['order_state'] == 'filled' and bitmex_response[0]['ordStatus'] == 'Filled'):

                    deribit_sell = deribit_response['result']['order']['average_price']
                    bitmex_buy = bitmex_response[0]['price']

                    order_message = f"Opening order submitted & filled. Bitmex Buy: {bitmex_buy}. Deribit Sell: {deribit_sell}."
                    send_twilio_message(_message=order_message)

                    print("***Spread Opened***")
                    print(f"Bitmex Buy: {bitmex_buy}")
                    print(f"Deribit Sell: {deribit_sell}")
                    log_city(message=f'\n{time.time()}, Trade Opened, Open, Bitmex, Deribit, {bm_ask_d27}, {db_bid_d27}')
                    
                    open_sizes_dict = get_open_sizes(test=TEST)
                    bitmex_open = open_sizes_dict['bm_d27_qty']
                    deribit_open = open_sizes_dict['db_d27_qty']

                else:
                    print("***** UH OH! ONE OF THE ORDERS DID NOT FILL! LIQUIDATING AND RESTARTING SCRIPT!")
                    liquidate_all(test=TEST)
                    send_twilio_message(_message="Order open failed. Emergency Liquidation.")
                    log_city(message=f'\n{time.time()}, Emergency Liquidation')
                    
                    open_sizes_dict = get_open_sizes(test=TEST)
                    bitmex_open = open_sizes_dict['bm_d27_qty']
                    deribit_open = open_sizes_dict['db_d27_qty']

            print(f"Sleeping {SLEEP_TIME} seconds")
            time.sleep(SLEEP_TIME)

        while((abs(bitmex_open) == deribit_open) and (bitmex_open < 0)):

            print(f"\nTrade currently OPEN. Bitmex Short: {bitmex_open}, Deribit Long: {deribit_open} ")

            (bm_ask_d27, bm_bid_d27, db_ask_d27, db_bid_d27) = get_d27_prices(test=TEST)

            if((bm_bid_d27-db_ask_d27) <= close_spread):
                bitmex_response, deribit_response = liquidate_all(test=TEST)
                deribit_close = deribit_response['result']['order']['average_price']
                bitmex_close = bitmex_response[0]['price']
                _message = f"Trade Closed. Bitmex Bought: {bitmex_close}. Deribit Sold: {deribit_close}."
                send_twilio_message(_message=_message)
                log_city(message=f'\n{time.time()}, Trade Closed, Close, Bitmex, Deribit, {bm_ask_d27}, {db_bid_d27}')
                
                open_sizes_dict = get_open_sizes(test=TEST)
                bitmex_open = open_sizes_dict['bm_d27_qty']
                deribit_open = open_sizes_dict['db_d27_qty']
                
            else:
                print(f"Sleeping {SLEEP_TIME} seconds")
                time.sleep(SLEEP_TIME)

        while((bitmex_open == abs(deribit_open)) and (bitmex_open > 0)):

            print(f"\nTrade currently OPEN. Bitmex Long: {bitmex_open}, Deribit Short: {deribit_open} ")

            (bm_ask_d27, bm_bid_d27, db_ask_d27, db_bid_d27) = get_d27_prices(test=TEST)

            if((db_bid_d27-bm_ask_d27) <= close_spread):
                bitmex_response, deribit_response = liquidate_all(test=TEST)
                deribit_close = deribit_response['result']['order']['average_price']
                bitmex_close = bitmex_response[0]['price']
                _message = f"Trade Closed. Bitmex Sold: {bitmex_close}. Deribit Bought: {deribit_close}."
                send_twilio_message(_message=_message)
                log_city(message=f'\n{time.time()}, Trade Closed, Close, Deribit, Bitmex, {db_ask_d27}, {bm_bid_d27}')
                
                open_sizes_dict = get_open_sizes(test=TEST)
                bitmex_open = open_sizes_dict['bm_d27_qty']
                deribit_open = open_sizes_dict['db_d27_qty']

            else:
                print(f"Sleeping {SLEEP_TIME} seconds")
                time.sleep(SLEEP_TIME)

        loop_counter += 1
        print(f"Sleeping {SLEEP_TIME} seconds")
        time.sleep(SLEEP_TIME)
    '''
    except Exception as e: # loops fails for any reason

        print(f"Error: {e}")

        send_twilio_message(_message="Trading Loop Failed.")
        print(f"Trading Loop Failed. Sleeping {SLEEP_TIME} seconds.")
        time.sleep(SLEEP_TIME)
    '''