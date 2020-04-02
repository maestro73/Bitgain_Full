import ccxt
from pprint import pprint
from datetime import datetime
from time import time, sleep
import pandas as pd

def get_latest_minute_timestamp():
    string_to_minute = datetime.now().strftime("%Y-%m-%d %H:%M")
    strp_time = datetime.strptime(string_to_minute, "%Y-%m-%d %H:%M")
    return(int(strp_time.timestamp()))

def get_full_ohlcv():
    bitmex = ccxt.bitmex()
    result = []
    last_timestep = time()
    timestamp_now = int(last_timestep)
    for timestamp in range(1443182400, timestamp_now, 60*1000):
        print(f"Timestamp: {timestamp}")
        cycle_time = time() - last_timestep
        last_timestep = time()
        result.append(bitmex.fetchOHLCV('BTC/USD', limit=1000, since=timestamp))
        try:
            sleep(1 - cycle_time)
        except:
            print(f"Sleeping full...")
            sleep(1)
    return(result)

def get_100k_min_ohlcv():
    bitmex = ccxt.bitmex()
    results = []
    last_timestep = time()
    timestamp_now = get_latest_minute_timestamp()
    timestamp_start = (timestamp_now - 60*1000*100)
    for timestamp in range(timestamp_start, timestamp_now, 60000):
        results.append(bitmex.fetchOHLCV('BTC/USD', limit=1000, since=timestamp))
        sleep(1.8)
    return(results)

def get_10k_min_ohlcv():
    bitmex = ccxt.binanceus()
    results = []
    timestamp_now = get_latest_minute_timestamp()
    timestamp_start = (timestamp_now - 60*1000*10)
    for timestamp in range(timestamp_start, timestamp_now, 60000):
        temp_results = bitmex.fetchOHLCV('BTC/USD', limit=1000, since=timestamp*1000)
        for result in temp_results:
            results.append(result)
        sleep(1.85)
    results_df = pd.DataFrame(results, columns=["timestamp","open","high","low","last","volume"])
    return(results_df)

def get_ccxt_ohlcv(symbol="BTC/USD", market=ccxt.binanceus, ticks=10000):
    bitmex = market()
    results = []
    timestamp_now = get_latest_minute_timestamp()
    timestamp_start = (timestamp_now - 60*ticks)
    for timestamp in range(timestamp_start, timestamp_now, 60000):
        print(f"Length: {len(results)}")
        temp_results = bitmex.fetchOHLCV(symbol, limit=1000, since=timestamp*1000)
        for result in temp_results:
            results.append(result)
        sleep(1.85)
    return(pd.DataFrame(results, columns=["timestamp","open","high","low","last","volume"]))

ohlcv_10k = get_ccxt_ohlcv()
pprint(ohlcv_10k.head())

'''
bitmex = ccxt.bitmex()

pprint(bitmex.describe())

ohlcv = bitmex.fetchOHLCV('BTC/USD', limit=1000, since=1443182400)

timestamp = ohlcv[0][0]
timestamp_last = ohlcv[-1][0]
print(timestamp/1000, ': ', datetime.fromtimestamp(timestamp/1000))
print(timestamp_last/1000, ': ', datetime.fromtimestamp(timestamp_last/1000))

time_jump = (timestamp_last/1000 - timestamp/1000)
print(time_jump)

print(f"Timestamp_now: {int(get_now_timestamp())}")
'''