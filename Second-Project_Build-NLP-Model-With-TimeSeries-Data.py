# %% [markdown]
# # **SECOND PROJECT : BUILD NLP MODEL WITH TIME SERIES DATA 👨🏽‍💻**

# %% [markdown]
# * Name         : Lintang Nagari
# * Email        : unggullintangg@gmail.com
# * Linkedin     : <a href='https://www.linkedin.com/in/lintangnagari/'>Lintang Nagari</a>
# * Github       : <a href='https://github.com/lnt-ngr'>lnt-ngr</a>

# %% [markdown]
# **Here are the submission criteria you must meet:**
# 
# * Use any dataset, but it must have **at least 1000 samples**.
# * Must use `LSTM` in the model architecture.
# * Validation set **should be 20%** of the total dataset.
# * Model must use a `sequential model`.
# * Must use Learning Rate in the optimizer.
# * MAE should be **less than 10%** of the data scale.
# 
# **Dataset : https://www.kaggle.com/datasets/shubhamcodez/berkeley-earth-daily-average-temperature**
# 
# **About Dataset**
# 
# Temperatures are in Celsius and reported as anomalies relative to the `Jan 1951-Dec 1980` average.
# 
# The current dataset presented here is described as:
# Berkeley Earth daily TAVG full dataset This current analysis product is preliminary and may be subject to significant future revisions.This analysis was run on `06-Sep-2022` 15:50:29
# 
# Results are based on a **50461 monthly time series** with 21047039 observations and 48263 daily time series with 512331899 observations
# Estimated Jan 1951-Dec 1980 land-average temperature (C): `8.59 +/- 0.05`

# %% [markdown]
# ### __IMPORT LIBRARY__

# %%
import numpy as np
import pandas as pd
import tensorflow as tf
import matplotlib.pyplot as plt

from keras.models import Sequential
from keras.layers import Dense, LSTM, GRU
from sklearn.preprocessing import MinMaxScaler
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error

# %% [markdown]
# ### __DATAFRAME__

# %%
df = pd.read_csv('./dataset/Temperatures.csv')
df.head()

# %%
df.info()

# %%
#Menghilangkan data yang tidak dibutuhkan

df.drop(['Day of Year', 'Anomaly'], axis = 1, inplace = True)
df.shape

# %%
Tanggal = df['Date'].values
Temperature  = df['Temperature'].values

# %% [markdown]
# ### __VISUALISASI DATA TIME SERIES__

# %%

plt.figure(figsize=(15,5))
plt.plot(Tanggal, Temperature)
plt.title('Temperature Rata-Rata', fontsize=18)
plt.xlabel('Date')
plt.ylabel('Temperature')
plt.show()

# %% [markdown]
# ### __TRAINING AND TESTING__

# %%
Tanggal_latih, Tanggal_test, Temperature_latih, Temperature_test = train_test_split(Tanggal, Temperature, test_size=0.2, shuffle=False, random_state=123)

print("Total Nilai Training : ", len(Tanggal_latih))
print("Total Nilai Testing : ", len(Tanggal_test))

# %%
def windowed_dataset(series, window_size, batch_size, shuffle_buffer):
    series = tf.expand_dims(series, axis=-1)
    ds = tf.data.Dataset.from_tensor_slices(series)
    ds = ds.window(window_size + 1, shift=1, drop_remainder=True)
    ds = ds.flat_map(lambda w: w.batch(window_size + 1))
    ds = ds.shuffle(shuffle_buffer)
    ds = ds.map(lambda w: (w[:-1], w[-1:]))
    return ds.batch(batch_size).prefetch(1)

# %% [markdown]
# ### __TRAINING MODEL__

# %%
train_set = windowed_dataset(Temperature_latih, window_size=60, batch_size=100, shuffle_buffer=1000)
test_set = windowed_dataset(Temperature_test, window_size=60, batch_size=100, shuffle_buffer=1000)

model = tf.keras.models.Sequential([
  tf.keras.layers.LSTM(30, return_sequences=True,  input_shape=[None, 1]),
  tf.keras.layers.LSTM(30),
  tf.keras.layers.Dense(30, activation="relu"),
  tf.keras.layers.Dropout(0.3),
  tf.keras.layers.Dense(10, activation="relu"),
  tf.keras.layers.Dense(1),
])

# %%
minMae = (df['Temperature'].max() - df['Temperature'].min()) * 10/100
print("Batas maksimal nilai MAE pada model dari skala data sebesar", minMae)

# %%
class myCallback(tf.keras.callbacks.Callback):
  def on_epoch_end(self, epoch, logs={}):
    if (logs.get('mae')<minMae) & (logs.get('val_mae') < minMae):
      print('\nNilai MAE pada model telah mencapai < "10%"  skala data')
      self.model.stop_training = True
callbacks = myCallback()

# %%
optimizer = tf.keras.optimizers.SGD(learning_rate=1.000e-04, momentum=0.9)
model.compile(
    loss=tf.keras.losses.Huber(),
    optimizer=optimizer,
    metrics=['mae']
    )
history = model.fit(
    train_set,
    epochs=100,
    validation_data=test_set,
    verbose=1,
    callbacks=[callbacks],
    )

# %% [markdown]
# ### __PLOTTING__

# %%
#MAE PLOT

plt.figure(figsize=(15, 5))
plt.plot(history.history['mae'])
plt.plot(history.history['val_mae'], linestyle='--')
plt.title('MAE')
plt.ylabel('MAE')
plt.xlabel('Epoch')
plt.legend(['Training Set', 'Validation Set'])
plt.grid(color="b", linestyle='-', linewidth=2, alpha=0.5)

plt.show()

# %%
#LOSS PLOT

plt.figure(figsize=(15, 5))
plt.plot(history.history['loss'])
plt.plot(history.history['val_loss'], linestyle='--')
plt.title('Loss')
plt.ylabel('Loss')
plt.xlabel('Epoch')
plt.legend(['Training Set', 'Validation Set'])
plt.grid(color="b", linestyle='-', linewidth=2, alpha=0.5)

plt.show()


