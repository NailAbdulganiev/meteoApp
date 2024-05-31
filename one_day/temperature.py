import numpy as np
import pandas as pd
import os
from keras.src.saving import load_model
# import matplotlib.pyplot as plt
# import tensorflow as tf
# from tensorflow import keras
# from keras import Sequential
# from keras.src.callbacks import ModelCheckpoint
# from keras.src.layers import InputLayer, LSTM, Dropout, Dense
# from keras.src.losses import MeanSquaredError
# from keras.src.metrics import RootMeanSquaredError
# from keras.src.optimizers import Adam
# from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score


def generate_forecast_1_day(parameter):
    # Определяем путь к файлу относительно местоположения скрипта
    base_dir = os.path.dirname(os.path.abspath(__file__))
    data_file = os.path.join(base_dir, "../meteo_data.csv")

    df = pd.read_csv(data_file)
    df.index = pd.to_datetime(df.DATE)
    del df['DATE']

    required_cols = [parameter]
    df = df[required_cols]
    #print(df)

    temp = df[parameter]

    def df_to_X_y(df, window_size=24):
        df_as_np = df.to_numpy()
        X = []
        y = []
        for i in range(len(df_as_np) - window_size):
            row = [[a] for a in df_as_np[i:i + window_size]]
            X.append(row)
            label = df_as_np[i + window_size]
            y.append(label)
        return np.array(X), np.array(y)

    WINDOW_SIZE = 24
    X1, y1 = df_to_X_y(temp, WINDOW_SIZE)

    X_train1, y_train1 = X1[:20000], y1[:20000]
    X_val1, y_val1 = X1[20000:23000], y1[20000:23000]
    X_test1, y_test1 = X1[23000:], y1[23000:]
    #print(X_train1.shape, y_train1.shape, X_val1.shape, y_val1.shape, X_test1.shape, y_test1.shape)

    model2 = load_model(os.path.join(base_dir, 'model2/model2-temperature.keras'))

    def predict_future(model, last_known_data, last_known_dates, steps=3, window_size=24):
        predictions = []
        future_dates = pd.date_range(start=last_known_dates[-1], periods=steps + 1, freq='h')[1:]

        current_data = last_known_data.tolist()

        for _ in range(steps):
            input_data = np.array(current_data[-window_size:]).reshape(1, window_size, 1)
            prediction = model.predict(input_data)
            predictions.append(prediction[0, 0])
            current_data.append(prediction[0, 0])

        return future_dates, predictions

    last_known_data = temp.values[-WINDOW_SIZE:]
    last_known_dates = temp.index[-WINDOW_SIZE:]

    future_steps = 24
    future_dates, predictions = predict_future(model2, last_known_data, last_known_dates, future_steps, WINDOW_SIZE)

    forecast_result = "\n".join([f"{date}: {pred:.2f}" for date, pred in zip(future_dates, predictions)])
    return forecast_result
