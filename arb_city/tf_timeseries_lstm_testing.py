"""
Created on Wed Jan  1 15:03:37 2020

@author: ngancitano
"""

#https://mrjbq7.github.io/ta-lib/index.html

#TODO: use scalar within [samples, timesteps, features] reshape instead of before

# Process Flow:
# 1. Load raw dataset
# 2. Calculate new columns for daily price change percentage
# 3. Calculate indicators using TA-lib
#    3a. All data MUST BE RELATIVE!!! 
#        Ex. price is a hard number that can fluctuate wildly and is not stationary. 
#        On the other hand, price change % will always hover around 0% and is much more stationary
#        Bollilnger bands are useless! But, percent away from bollinger bands are awesome!
# 4. Normalize data! LSTM uses sigmoid functions which favor normalization over standardization
# 5. Split into training/testing sets
# 6. Reshape data into [samples, timesteps, features] format for LSTM
# 7. Build model
# 8. Train model
# 9. Test model
# 10. Deploy model

#%%
import pandas as pd
import numpy as np
from sklearn.preprocessing import MinMaxScaler, Normalizer, RobustScaler
import tensorflow as tf
import talib
import tensorflow

min_max_scaler = MinMaxScaler()
normalizer = Normalizer()
robust_scaler = RobustScaler()

#%%
# Data download
# 1. Load raw dataset
csv_path = "https://raw.githubusercontent.com/curiousily/Deep-Learning-For-Hackers/master/data/3.stock-prediction/BTC-USD.csv"

df = pd.read_csv(csv_path, parse_dates=['Date'])
df = df.sort_values('Date')

#%% 
# 2. Calculate new columns for daily price change percentage

close_price = df.Close.values.reshape(-1, 1)
#volume = df.Volume.values.reshape(-1, 1)
#volume_shifted_1 = np.roll(volume, -1)
#volume_change = (volume_shifted_1 - volume)
#volume_change_percent = abs(np.roll(volume, -1) - volume) / volume
close_change_percent = (np.roll(close_price, -1) - close_price) / close_price
close_change_percent_normalized = normalizer.fit_transform(close_change_percent)
close_change_percent_minmaxscaled = min_max_scaler.fit_transform(close_change_percent)
#change_price = 

#%%
# 3. Calculate indicators using TA-lib

close_macd, close_macdsignal, close_macdhist = talib.MACD(df.Close.values)
open_macd, open_macdsignal, open_macdhist = talib.MACD(df.Open.values)

atr_normalized = talib.NATR(df.High.values, df.Low.values, df.Close.values)
atr = talib.ATR(df.High.values, df.Low.values, df.Close.values)

momentum = talib.MOM(df.Close.values)

relative_strength_index = talib.RSI(df.Close.values)

stoch_slowk, stock_slowd = talib.STOCH(df.High.values, df.Low.values, df.Close.values)

trix = talib.TRIX(df.Close.values)

absolute_price_oscillator = talib.APO(df.Close.values)

aroon_oscillator = talib.AROONOSC(df.High.values, df.Low.values)

ultimate_oscillator = talib.ULTOSC(df.High.values, df.Low.values, df.Close.values)

williams_oscillator = talib.WILLR(df.High.values, df.Low.values, df.Close.values)



#%%

function_list = [talib.NATR, talib.MOM, talib.RSI]

for function in function_list:
    print(function.__name__)

#%%

ta_df = pd.DataFrame(
    {"momentum": momentum,
     "rsi": relative_strength_index,
     "trix": trix}
    )

ta_nparray = np.array(
    [momentum, relative_strength_index, trix]).T

#%% TESTING HERE


#print(close_price)
scaled_close = min_max_scaler.fit_transform(close_price)

scaled_close = scaled_close[~np.isnan(scaled_close)]
scaled_close = scaled_close.reshape(-1, 1)

#TODO: must scale all columns seperately then re-combine
#TODO: convert close pricing to +1/-1 price change
#TODO: reshape data to include all features

#%%

SEQ_LEN = 100

def to_sequences(data, seq_len):
    d = []

    for index in range(len(data) - seq_len):
        d.append(data[index: index + seq_len])

    return np.array(d)

def preprocess(data_raw, seq_len, train_split):

    data = to_sequences(data_raw, seq_len)

    num_train = int(train_split * data.shape[0])

    X_train = data[:num_train, :-1, :]
    y_train = data[:num_train, -1, :]

    X_test = data[num_train:, :-1, :]
    y_test = data[num_train:, -1, :]

    return X_train, y_train, X_test, y_test


X_train, y_train, X_test, y_test = preprocess(scaled_close, SEQ_LEN, train_split = 0.9)

#%%
# playing around here to fully understand reshape 

train_test_split = .9
#num_split = int(train_test_split * df_sequenced.shape[0])

sequencing_output = to_sequences(scaled_close, 100)
closed_reverse_shape = df.Close.values.reshape(1,-1)
closed_list_shape = df.Close.values

df_reshaped = df.values.reshape(3201,7)
df_sequenced = to_sequences(df_reshaped, 100)

# THIS IS NOT RIGHT! ASK MARCO FOR HELP
X_train_full = df_sequenced[:num_split, :-1, :-1]
 

#%%
DROPOUT = 0.2
WINDOW_SIZE = SEQ_LEN - 1

model = tf.keras.Sequential()

model.add(tf.keras.layers.Bidirectional(
  tf.keras.layers.LSTM(WINDOW_SIZE, return_sequences=True),
  input_shape=(WINDOW_SIZE, X_train.shape[-1])
))
model.add(tf.keras.layers.Dropout(rate=DROPOUT))

model.add(tf.keras.layers.Bidirectional(
  tf.keras.layers.LSTM((WINDOW_SIZE * 2), return_sequences=True)
))
model.add(tf.keras.layers.Dropout(rate=DROPOUT))

model.add(tf.keras.layers.Bidirectional(
  tf.keras.layers.LSTM(WINDOW_SIZE, return_sequences=False)
))

model.add(tf.keras.layers.Dense(units=1))

model.add(tf.keras.layers.Activation('linear'))

#%%
print(X_train.shape)
