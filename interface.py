import os
import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
import time
import requests
import pandas as pd
import subprocess
from one_hour.temperature import generate_forecast
from three_hour.temperature import generate_forecast

stationID = {
    "Сервисный центр": "00001F76",
    "Отделение 17": "00001F77",
    "Отделение 9": "00001F78",
    "Отделение 12": "00001F7D",
}
stationParameters = {
    1: "SOLAR_RADIATION",
    2: "PRECIPITATION",
    3: "WIND_SPEED",
    4: "LEAF_WETNESS",
    5: "HC_AIR_TEMPERATURE",
    6: "HC_RELATIVE_HUMIDITY",
    7: "DEW_POINT"
}
forecastIntervals = {
    1: "1 час",
    2: "3 часа",
    3: "1 день",
    4: "3 дня",
    5: "1 неделя"
}
url = 'https://meteoapi.xn--b1ahgiuw.xn--p1ai/parameter/'
day = 86400


def get_data():
    station = station_combobox.get()
    parameter = parameter_combobox.get()
    start_time = start_time_entry.get()
    end_time = end_time_entry.get()
    interval = interval_combobox.get()

    if not station or not parameter or not start_time or not end_time or not interval:
        messagebox.showerror("Ошибка", "Заполните все поля.")
        return
    # получение ключей
    station_value = stationID[station]
    keyIntervals = next(key for key, value in forecastIntervals.items() if value == interval)
    keyParameter = next(key for key, value in stationParameters.items() if value == parameter)

    try:
        data_dict = {}
        for parameter in stationParameters:
            t = int(time.time()) + 10800
            msg = {
                "meteoId": station_value,
                "endTime": t - int(end_time) * day,
                "parameterName": stationParameters.get(parameter).strip('"'),
                "startTime": t - int(start_time) * day
            }
            response = requests.post(url, json=msg)
            response.raise_for_status()
            print(f"Request {parameter}/7...")

            data = response.json()
            data_dict[stationParameters[parameter]] = data['values']['values']
        data_dict["DATE"] = data['dates']

        df = pd.DataFrame(data_dict)
        df = df.rename(columns=lambda x: x.strip('"'))
        df.to_csv('meteo_data_1_week.csv', index=False)

        messagebox.showinfo("Успех", "Данные успешно получены и сохранены в csv-файл.")
    except requests.exceptions.RequestException as e:
        messagebox.showerror("Ошибка", f"Произошла ошибка при отправке запроса: {e}")


def open_csv():
    try:
        if not os.path.exists('meteo_data.csv'):
            raise FileNotFoundError("Файл 'meteo_data.csv' не найден.")

        df = pd.read_csv('meteo_data.csv')

        window = tk.Toplevel(root)

        tree = ttk.Treeview(window)
        tree["columns"] = list(df.columns)
        tree["show"] = "headings"
        for column in df.columns:
            tree.heading(column, text=column)

        for index, row in df.iterrows():
            tree.insert("", "end", values=list(row))

        vsb = ttk.Scrollbar(window, orient="vertical", command=tree.yview)
        vsb.pack(side='right', fill='y')
        tree.configure(yscrollcommand=vsb.set)
        tree.pack(fill="both", expand=True)

        close_button = ttk.Button(window, text="Закрыть", command=window.destroy)
        close_button.pack(pady=10)

    except FileNotFoundError as e:
        messagebox.showerror("Ошибка", str(e))
    except Exception as e:
        messagebox.showerror("Ошибка", f"Произошла ошибка: {e}")

def get_forecast():
    try:
        forecast = generate_forecast()  # Вызываем функцию для получения прогноза
        messagebox.showinfo("Прогноз", forecast)  # Отображаем прогноз в messagebox
    except Exception as e:
        messagebox.showerror("Ошибка", f"Произошла ошибка при получении прогноза: {e}")

root = tk.Tk()
root.title("Погода")
root.geometry("600x450")

station_label = tk.Label(root, text="Выберите станцию:")
station_label.pack(pady=5)
station_combobox = ttk.Combobox(root, values=list(stationID.keys()))
station_combobox.pack(pady=5)

start_time_label = tk.Label(root, text="Введите StartTime (в днях):")
start_time_label.pack(pady=5)
start_time_entry = tk.Entry(root)
start_time_entry.pack(pady=5)
start_time_entry.insert(0, "730")

end_time_label = tk.Label(root, text="Введите EndTime (в днях):")
end_time_label.pack(pady=5)
end_time_entry = tk.Entry(root)
end_time_entry.pack(pady=5)
end_time_entry.insert(0, "0")

parameter_label = tk.Label(root, text="Выберите параметр погоды:")
parameter_label.pack(pady=5)
parameter_combobox = ttk.Combobox(root, values=list(stationParameters.values()))
parameter_combobox.pack(pady=5)

interval_label = tk.Label(root, text="Интервал прогноза:")
interval_label.pack(pady=5)
interval_combobox = ttk.Combobox(root, values=list(forecastIntervals.values()))
interval_combobox.pack(pady=5)

forecast_button = tk.Button(root, text="Получить данные", command=get_data)
forecast_button.pack(pady=10)

open_button = tk.Button(root, text="Посмотреть данные", command=open_csv)
open_button.pack(pady=5)

# Кнопка для получения прогноза
predict_button = tk.Button(root, text="Получить прогноз", command=get_forecast)
predict_button.pack(pady=10)

root.mainloop()


def create_interface():
    return None