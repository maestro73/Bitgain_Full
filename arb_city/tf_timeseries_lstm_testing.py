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
#from keras.optimizers import SGD

min_max_scaler = MinMaxScaler()
normalizer = Normalizer()
robust_scaler = RobustScaler()

def binary_accuracy_(y_test, y_hat_scaled):
    count = 0
    if len(y_test) == len(y_hat_scaled):
        for i in range(0, y_test.shape[0]):
            if y_test[i] == 1 and y_hat_scaled[i] >= 0.5:
                count += 1
            elif y_test[i] == -1 and y_hat_scaled[i] < 0.5:
                count += 1
                
        print(f"Percent Correct: {count/len(y_test)}")
                
    else:
        print("Error: please pass 2 arrays of equal length.")

#%%
# Data download
# 1. Load raw dataset
csv_path = "https://raw.githubusercontent.com/curiousily/Deep-Learning-For-Hackers/master/data/3.stock-prediction/BTC-USD.csv"

df = pd.read_csv(csv_path, parse_dates=['Date'])
df = df.sort_values('Date')

#%% 
# 2. Calculate new columns for daily price change percentage


#volume = df.Volume.values.reshape(-1, 1)
#volume_shifted_1 = np.roll(volume, -1)
#volume_change = (volume_shifted_1 - volume)
#volume_change_percent = abs(np.roll(volume, -1) - volume) / volume
close_price = df.Close.values.reshape(-1, 1)
close_change_percent = (np.roll(close_price, -1) - close_price) / close_price
close_change_percent_normalized = normalizer.fit_transform(close_change_percent)
close_change_percent_minmaxscaled = min_max_scaler.fit_transform(close_change_percent)
#change_price = 

close_change_clean = np.where(close_change_percent_normalized==0,1,close_change_percent_normalized)
#close_change_clean = close_change_clean[close_change_clean.shape[0] - len(d_list):]

close_change_clean_list = []
for x in close_change_clean:
    close_change_clean_list.append(int(x[0]))
    
close_change_clean_list = np.array(close_change_clean_list)

#array1 = np.array([2, 2, 2, 0, 2, 0, 2])
#print np.where(array1==0, 1, array1)

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
'''
function_list = [talib.NATR, talib.MOM, talib.RSI]

for function in function_list:
    print(function.__name__)
'''

#%%

ta_df = pd.DataFrame(
    {"momentum": momentum,
     "rsi": relative_strength_index,
     "trix": trix,
     "natr": atr_normalized,
     "apo": absolute_price_oscillator,
     "aroon": aroon_oscillator,
     "ultimate": ultimate_oscillator,
     "williams": williams_oscillator,
     "close_change": close_change_clean_list}
    )

ta_nparray = np.array(
    [momentum, relative_strength_index, trix,atr_normalized, absolute_price_oscillator, aroon_oscillator, ultimate_oscillator, williams_oscillator, close_change_clean_list]).T

#%% TESTING HERE

'''
#print(close_price)
scaled_close = min_max_scaler.fit_transform(close_price)

scaled_close = scaled_close[~np.isnan(scaled_close)]
scaled_close = scaled_close.reshape(-1, 1)
'''
#TODO: must scale all columns seperately then re-combine
#TODO: convert close pricing to +1/-1 price change
#TODO: reshape data to include all features

#%%

#d-sequence testing

seq_len = 100

ta_nparray_clean = ta_nparray[~np.isnan(ta_nparray).any(axis=1)]
x_data = ta_nparray_clean[:, :-1]
y_data = ta_nparray_clean[:, -1]

d_list = []
for idx in range(len(x_data) - seq_len):
    d_list.append(x_data[idx: idx + seq_len])
    
#this is equal to "data" below in next cell def_preprocess
d_list_np_array = np.array(d_list)

train_split = 0.8
num_train_split = int(train_split * d_list_np_array.shape[0])

x_train = d_list_np_array[:num_train_split, :, :-1]
y_train = y_data[:num_train_split]

x_test = d_list_np_array[num_train_split:, :, :-1]
y_test = y_data[num_train_split:-seq_len]

#%%
y_train_list = y_train[0]

#%%
# data according to https://machinelearningmastery.com/multivariate-time-series-forecasting-lstms-keras/




#%%
'''
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
'''
#%%
# playing around here to fully understand reshape 
'''
train_test_split = .9
#num_split = int(train_test_split * df_sequenced.shape[0])

sequencing_output = to_sequences(scaled_close, 100)
closed_reverse_shape = df.Close.values.reshape(1,-1)
closed_list_shape = df.Close.values

df_reshaped = df.values.reshape(3201,7)
df_sequenced = to_sequences(df_reshaped, 100)

# THIS IS NOT RIGHT! ASK MARCO FOR HELP
X_train_full = df_sequenced[:num_split, :-1, :-1]
'''

#%%

'''
DROPOUT = 0.2
WINDOW_SIZE = seq_len

model = tf.keras.Sequential()

model.add(tf.keras.layers.Bidirectional(
  tf.keras.layers.LSTM(WINDOW_SIZE, return_sequences=True),
  input_shape=(WINDOW_SIZE, x_train.shape[-1])
))
model.add(tf.keras.layers.Dropout(rate=DROPOUT))

model.add(tf.keras.layers.Bidirectional(
  tf.keras.layers.LSTM((WINDOW_SIZE), return_sequences=True)
))
model.add(tf.keras.layers.Dropout(rate=DROPOUT))

model.add(tf.keras.layers.Bidirectional(
  tf.keras.layers.LSTM(WINDOW_SIZE, return_sequences=False)
))

#model.add(tf.keras.layers.Dense())

model.add(tf.keras.layers.Activation('linear'))

'''

#%%

WINDOW_SIZE = seq_len
BATCH_SIZE = 10

opt = tf.keras.optimizers.SGD(lr=0.01, momentum=0.9)

model = tf.keras.Sequential()
#model.add(tf.keras.layers.Dense(12, input_shape=(x_train.shape[1],x_train.shape[2])))
#model.add(tf.keras.layers.Dropout(0.2))
model.add(tf.keras.layers.LSTM(12, return_sequences=True, input_shape=(x_train.shape[1],x_train.shape[2])))
model.add(tf.keras.layers.LSTM(12, return_sequences=True))
model.add(tf.keras.layers.LSTM(12, return_sequences=True))
model.add(tf.keras.layers.LSTM(12, return_sequences=True))
#model.add(tf.keras.layers.Dropout(0.1))
model.add(tf.keras.layers.LSTM(12, return_sequences=False))
#model.add(tf.keras.layers.Dropout(0.1))
#model.add(tf.keras.layers.Dense(12))
#model.add(tf.keras.layers.Dropout(0.1))
model.add(tf.keras.layers.Dense(1))

model.compile(
    loss='binary_crossentropy',
    optimizer='adam',
    metrics=['binary_accuracy']
)
#%%

history = model.fit(
    x_train,
    y_train,
    verbose=1,
    epochs=12,
    batch_size=32,
    shuffle=False,
    #validation_split=0.15
)

yhat = model.predict(x_test)
scaled_yhat = min_max_scaler.fit_transform(yhat)
binary_accuracy_(y_test, scaled_yhat)

#print(scaled_yhat)

#%%
print(y_test[0])