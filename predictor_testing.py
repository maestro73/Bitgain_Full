# pylint: disable=no-member, anomalous-backslash-in-string
import re, tweepy, talib, datetime, requests 
from tweepy import OAuthHandler 
from textblob import TextBlob 
#from objbrowser import browse
from pprint import pprint
import pandas as pd
import numpy as np
from sklearn.preprocessing import Normalizer
import tensorflow as tf
import time
import ccxt
from statistics import mean

rounding = 4

class BitgainPredictor(object):

    def __init__(self, retrain=False):
        # keys and tokens from the Twitter Dev Console 
        consumer_key = 'Ih2mlq5lsnqc9GEmgrkcoz8wj'
        consumer_secret = 'gr7tMB0QHlwqrL5f28YfzT5IDKsbRc9jyyqTIg0eRCrl29AzCJ'
        access_token = '827931206037622784-0AqKtYFM5DHvUySgxkJC3sGzwkSnWDs'
        access_token_secret = 'Ci8DJpBoRpuiggy2y7gamvctR1IjMGAOcgq5nfoB4FoRi'
  
        # attempt authentication 
        try: 
            # create OAuthHandler object 
            self.auth = OAuthHandler(consumer_key, consumer_secret) 
            # set access token and secret 
            self.auth.set_access_token(access_token, access_token_secret) 
            # create tweepy API object to fetch tweets 
            self.api = tweepy.API(self.auth) 
        except: 
            print("Error: Authentication Failed") 

        self.normalizer = Normalizer() # scikit-learn normalizer

        self.retrain = retrain

    def yhat_averager(self, y_hat):
        sum_counter = 0
        for entry in y_hat:
            sum_counter = sum_counter + entry[0]
        self.yhat_average = sum_counter / len(y_hat)

    def binary_accuracy_(self, y_test, y_hat):
        count = 0
        self.yhat_averager(y_hat)
        if len(y_test) == len(y_hat):
            for i in range(0, y_test.shape[0]):
                if y_test[i] == 1 and y_hat[i] >= self.yhat_average:
                    count += 1
                elif y_test[i] == -1 and y_hat[i] < self.yhat_average:
                    count += 1
            print(f"Percent Correct: {count/len(y_test)}")
            return (count/len(y_test))
                    
        else:
            raise ValueError("Error: please pass 2 arrays of equal length.")

    def get_latest_minute_timestamp(self):
        string_to_minute = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
        strp_time = datetime.datetime.strptime(string_to_minute, "%Y-%m-%d %H:%M")
        return(int(strp_time.timestamp()))

    def get_tweets(self, query, count = 1000):
        tweets = []
        try: 
            fetched_tweets = self.api.search(q = query, count = count)
            for tweet in fetched_tweets:
                parsed_tweet = {}
                parsed_tweet['text'] = tweet.text
                parsed_tweet['sentiment'], parsed_tweet['sentiment_score'] = self.get_tweet_sentiment(tweet.text)
                parsed_tweet['datetime'] = tweet.created_at
                parsed_tweet['retweets_count'] = tweet.retweet_count
                parsed_tweet['id'] = tweet.id
                #parsed_tweet['retweets'] = tweet.retweets
                if tweet.retweet_count > 0:
                    if parsed_tweet not in tweets:
                        tweets.append(parsed_tweet)
                else:
                    tweets.append(parsed_tweet)
            return tweets

        except tweepy.TweepError as e:
            print(f"TweepyError: {str(e)}")

    def get_tweet_sentiment(self, tweet):
        clean_tweet = ' '.join(re.sub("(@[A-Za-z0-9]+)|([^0-9A-Za-z \t])|(\w+:\/\/\S+)", " ", tweet).split())
        analysis = TextBlob(clean_tweet)

        if analysis.sentiment.polarity > 0: 
            return 'positive', analysis.sentiment.polarity
        elif analysis.sentiment.polarity < 0: 
            return 'negative', analysis.sentiment.polarity
        else: 
            return 'neutral', analysis.sentiment.polarity

    def get_ccxt_ohlcv_price_data(self, symbol="BTC/USD", market=ccxt.binanceus, ticks=10000, timestamp_now=None):
        bitmex = market()
        results = []
        if timestamp_now == None:
            timestamp_now = self.get_latest_minute_timestamp()
        timestamp_start = (timestamp_now - 60*ticks)
        print("Getting OHLCV...")
        for timestamp in range(timestamp_start, timestamp_now, 60000):
            print(f"Length: {len(results)}")
            temp_results = bitmex.fetchOHLCV('BTC/USD', limit=1000, since=timestamp*1000)
            for result in temp_results:
                results.append(result)
            time.sleep(1.85)
        self.price_data = pd.DataFrame(results, columns=["timestamp","open","high","low","last","volume"])

    def get_bitstamp_usd_minutely_price_data(self, data_path = "bitcoin_ticker.csv"):
        # "https://raw.githubusercontent.com/curiousily/Deep-Learning-For-Hackers/master/data/3.stock-prediction/BTC-USD.csv"
        try:
            df_minutely = pd.read_csv(data_path, parse_dates=['datetime_id']) # loads locally saved data_path (original copy found at github link above)
        except:
            print("Local data load failed... trying github download")
            df_minutely = pd.read_csv("https://raw.githubusercontent.com/curiousily/Deep-Learning-For-Hackers/master/data/3.stock-prediction/BTC-USD.csv", parse_dates=['datetime_id']) # loads locally saved data_path (original copy found at github link above)

        df_bitstamp_usd = df_minutely.loc[df_minutely['market'] == 'bitstamp'] # filters for only bitstamp market
        df_bitstamp_usd = df_bitstamp_usd.loc[df_bitstamp_usd['rpt_key'] == 'btc_usd'] # filters for only btc/usd pair
        df_bitstamp_usd = df_bitstamp_usd.drop(['updated_at', 'date_id', 'created_at', 'market', 'rpt_key'], axis=1) # drop misc columns
        self.price_data = df_bitstamp_usd.sort_values("datetime_id").reset_index(drop=True)#.drop('index', axis=1) # resets index numbering

    def get_indicators_from_price_data(self):

        data = self.price_data

        close_price = data['last'].values.reshape(-1,1) # extract closing price from dataset in the proper form for scikit normalizer
        close_change_percent = (np.roll(close_price, -1) - close_price) / close_price # calculate price percent change between each timestep
        close_change_percent_normalized = self.normalizer.fit_transform(close_change_percent) # converts all values to 1/-1 via rounding + / - 0
        close_change_clean = np.where(close_change_percent_normalized==0,1,close_change_percent_normalized) # replaces 0's with 1's (if no change, buy)

        close_change_clean_list = []
        for x in close_change_clean:
            close_change_clean_list.append(int(x[0]))
        close_change_clean = np.array(close_change_clean_list)

        #close_macd, close_macdsignal, close_macdhist = talib.MACD(data['last'].values)
        #open_macd, open_macdsignal, open_macdhist = talib.MACD(df.Open.values)
        atr_normalized = talib.NATR(data['high'].values, data['low'].values, data['last'].values)
        #atr = talib.ATR(data['high'].values, data['low'].values, data['last'].values)
        momentum = talib.MOM(data['last'].values)
        relative_strength_index = talib.RSI(data['last'].values)
        #stoch_slowk, stock_slowd = talib.STOCH(data['high'].values, data['low'].values, data['last'].values)
        trix = talib.TRIX(data['last'].values)
        absolute_price_oscillator = talib.APO(data['last'].values)
        aroon_oscillator = talib.AROONOSC(data['high'].values, data['low'].values)
        ultimate_oscillator = talib.ULTOSC(data['high'].values, data['low'].values, data['last'].values)
        williams_oscillator = talib.WILLR(data['high'].values, data['low'].values, data['last'].values)

        self.ta_data = np.array(
            [momentum, relative_strength_index, trix, atr_normalized, absolute_price_oscillator, aroon_oscillator, ultimate_oscillator, williams_oscillator, close_change_clean]).T
        self.close_price = close_price
        self.close_change_percent = close_change_percent

        #return ta_nparray

    def transform_indicators_to_lstm_format(self, seq_len = 100, train_split=0.9):

        # TODO: BUG! right now the math is done so that "seq_len" data is cut off from the MOST RECENT DATA
                    # needs to be the opposite! cut off oldest data, not most recent!

        data = self.ta_data

        data = data[~np.isnan(data).any(axis=1)]
        x_data = data[:, :-1]
        y_data = data[:, -1]

        temp_data_list = []
        for idx in range(len(x_data) - seq_len):
            temp_data_list.append(x_data[idx: idx + seq_len])
            
        #this is equal to "data" below in next cell def_preprocess
        temp_data_np_array = np.array(temp_data_list)

        num_train_split = int(train_split * temp_data_np_array.shape[0])

        self.x_train = temp_data_np_array[:num_train_split, :, :-1]
        self.y_train = y_data[:num_train_split]

        self.x_test = temp_data_np_array[num_train_split:, :, :-1]
        self.y_test = y_data[num_train_split:-seq_len]

        self.close_change_percent_test = self.close_change_percent[num_train_split:-seq_len]
        self.close_price_test = self.close_price[num_train_split:-seq_len]

    def build_model(self, activation='relu'):
        #opt = tf.keras.optimizers.SGD(lr=0.01, momentum=0.9)

        self.model = tf.keras.Sequential()
        #self.model.add(tf.keras.layers.Dense(12, input_shape=(x_train.shape[1],x_train.shape[2])))
        #self.model.add(tf.keras.layers.Dropout(0.2))
        self.model.add(tf.keras.layers.LSTM(50, activation='relu', return_sequences=False, input_shape=(self.x_train.shape[1],self.x_train.shape[2])))
        #self.model.add(tf.keras.layers.LSTM(12, return_sequences=True))
        #self.model.add(tf.keras.layers.LSTM(12, return_sequences=False))
        self.model.add(tf.keras.layers.Dropout(0.2))
        #self.model.add(tf.keras.layers.Activation(activation))
        self.model.add(tf.keras.layers.Dense(1))

        self.model.compile(
            loss='binary_crossentropy',
            optimizer='adam',
            metrics=['binary_accuracy']
        )

    def train_model(self, epochs=12, batch_size=12, verbose=1):
        self.history = self.model.fit(
            self.x_train,
            self.y_train,
            verbose=verbose,
            epochs=epochs,
            batch_size=batch_size,
            shuffle=False,
            #validation_split=0.15
        )

    def score_model(self):
        self.yhat_raw = self.model.predict(self.x_test)
        self.yhat = self.normalizer.fit_transform(self.yhat_raw)
        binary_accuracy_percent = self.binary_accuracy_(self.y_test, self.yhat_raw)
        return binary_accuracy_percent

    def save_model(self):
        self.model.save('testing.h5')

    def filter_tweets_by_time(self, tweets, minutes = 1):
        while True:
            if datetime.datetime.utcnow().strftime(f"%S")[0:2] == '00':
                filtered_tweets = [tweet for tweet in tweets if tweet['datetime'] > (datetime.datetime.utcnow() - datetime.timedelta(minutes=minutes))]
                return filtered_tweets
            else:
                print(f"Sleeping 1 sec: {datetime.datetime.utcnow().strftime(f'%S')[0:2]}")
                time.sleep(1)

    def save_tweet_sentiment(self, tweets):

        positive_tweets = [tweet for tweet in tweets if tweet['sentiment'] == 'positive']
        negative_tweets = [tweet for tweet in tweets if tweet['sentiment'] == 'negative']

        positive_tweet_percentage = round(100*len(positive_tweets)/len(tweets), rounding)
        negative_tweet_percentage = round(100*len(negative_tweets)/len(tweets), rounding)

        positive_average_score = sum([tweet['sentiment_score'] for tweet in positive_tweets])
        negative_average_score = sum([tweet['sentiment_score'] for tweet in negative_tweets])

        with open("btc_sentiment.csv", "a+") as _file:
            _file.write(f"{datetime.datetime.utcnow().strftime(f'%Y-%m-%d %H:%M:%S')}, {positive_tweet_percentage},{positive_average_score},{negative_tweet_percentage},{negative_average_score}\n")

        print(f"Positive Tweet Percentage: {positive_tweet_percentage} %")
        print(f"Negative Tweet Percentage: {negative_tweet_percentage} %")

        print(f"Positive Tweet Average Score: {positive_average_score}")
        print(f"Negative Tweet Average Score: {negative_average_score}")

    def sleep_til_next_minute(self):
        seconds = datetime.datetime.utcnow().strftime("%S")[0:2]
        if seconds != "00":
            time.sleep(60 - int(seconds))

    def get_tweets_last_minute(self, query, count = 1000):
        
        tweets = []

        self.sleep_til_next_minute()

        try: 
            fetched_tweets = self.api.search(q = query, count = count)

            for tweet in fetched_tweets:
                parsed_tweet = {}

                parsed_tweet['text'] = tweet.text
                parsed_tweet['sentiment'], parsed_tweet['sentiment_score'] = self.get_tweet_sentiment(tweet.text)
                parsed_tweet['datetime'] = tweet.created_at
                parsed_tweet['retweets_count'] = tweet.retweet_count
                parsed_tweet['id'] = tweet.id
                #parsed_tweet['retweets'] = tweet.retweets

                if tweet.retweet_count > 0:
                    if parsed_tweet not in tweets:
                        tweets.append(parsed_tweet)
                else:
                    tweets.append(parsed_tweet)

            return tweets

        except tweepy.TweepError as e:
            print(f"TweepyError: {str(e)}")

    def was_trade_made_check(self, buy_or_sell, holding):
        if buy_or_sell == 'buy' and holding == False:
            self.trade_count += 1
        elif buy_or_sell == 'sell' and holding == True:
            self.trade_count += 1

    def backtest_model(self, shorts=False):
        capital = 1000
        reverse_capital = 1000
        hodl = 1000
        self.trade_count = 0
        holding = False
        yhat = self.yhat_raw
        y_test = self.y_test
        if len(y_test) == len(yhat):
            for i in range(len(y_test)):
                if yhat[i] >= self.yhat_average:
                    capital = capital * (1 + self.close_change_percent_test[i])
                    self.was_trade_made_check(buy_or_sell='buy', holding=holding)
                    holding = True
                else:
                    reverse_capital = reverse_capital * (1 + self.close_change_percent_test[i])                    
                    self.was_trade_made_check(buy_or_sell='sell', holding=holding)
                    holding = False
                hodl = hodl * (1 + self.close_change_percent_test[i])
        else:
            raise ValueError("length of self.yhat does not match length of self.ytest")

        self.capital = capital
        self.hodl = hodl
        print(f"Backtest capital (starting w/ $1000): {capital} on {self.trade_count} trades")
        print(f"Reverse backtest capital (starting w/ $1000): {reverse_capital}")
        print(f"HODL capital (starting w/ $1000): {hodl}")
        print(f"Starting close: {self.close_price_test[0]} /// Ending close: {self.close_price_test[-1]}")

def run_main():
    
    client = BitgainPredictor()
    client.get_ccxt_ohlcv_price_data()
    client.get_indicators_from_price_data()
    client.transform_indicators_to_lstm_format(seq_len=90, train_split=0.98)
    client.build_model()
    client.train_model()
    client.score_model()
    #client.save_model()
    client.backtest_model()

    #tweets = client.get_tweets(query = "Bitcoin", count = 1000)
    #tweets = client.filter_tweets_by_time(tweets)
    #client.save_tweet_sentiment(tweets)

    '''
    print(f"First tweet: ", tweets[0])
    print(f"Last tweet: ", tweets[-1])
    print(f"Datetime now: {datetime.datetime.utcnow()}")
    print(f"Len(tweets): {len(tweets)}")
    '''

    '''
    filtered_tweets = [tweet for tweet in tweets if (tweet['datetime'] > (datetime.datetime.utcnow() - datetime.timedelta(minutes=2)) and tweet['datetime'] < (datetime.datetime.utcnow() - datetime.timedelta(minutes=1)))]
    print(f"Len(filtered_tweets): {len(filtered_tweets)}")
    print(f"First filtered tweet: ", filtered_tweets[0])
    print(f"Last filtered tweet: ", filtered_tweets[-1])

    '''

    '''
    positive_tweets = [tweet for tweet in tweets if tweet['sentiment'] == 'positive']
    negative_tweets = [tweet for tweet in tweets if tweet['sentiment'] == 'negative']

    print(f"Positive Tweet Percentage: {round(100*len(positive_tweets)/len(tweets), rounding)} %")
    print(f"Negative Tweet Percentage: {round(100*len(negative_tweets)/len(tweets), rounding)} %")
    print(f"Neutral tweets percentage: {round(100*(len(tweets) - len(negative_tweets) - len(positive_tweets))/len(tweets), rounding)} %")
    '''

if __name__ == "__main__":
    run_main()
