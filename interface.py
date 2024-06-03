import os
import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
import time
import requests
import pandas as pd
import subprocess
from one_day.temperature import generate_forecast
from three_day.temperature import generate_forecast_3_day
from one_week.temperature import generate_forecast_1_week

stationID = {
    "Сервисный центр": "00001F76",
    "Отделение 17": "00001F77",
    "Отделение 9": "00001F78",
    "Отделение 12": "00001F7D",
}
stationParameters = {
    "Солнечная радиация": "SOLAR_RADIATION",
    "Осадки": "PRECIPITATION",
    "Скорость ветра": "WIND_SPEED",
    "Влажность листа": "LEAF_WETNESS",
    "Температура воздуха": "HC_AIR_TEMPERATURE",
    "Относительная влажность": "HC_RELATIVE_HUMIDITY",
    "Точка росы": "DEW_POINT"
}
forecastIntervals = {
    1: "1 час",
    3: "3 часа",
    24: "1 день",
    72: "3 дня",
    168: "1 неделя"
}
url = 'https://meteoapi.xn--b1ahgiuw.xn--p1ai/parameter/'
day = 86400


class Data():
    def __init__(self):
        self.end_time = None
        self.start_time = None
        self.station = None
        self.interval = None
        self.parameter = None

    def get_station(self):
        self.station = station_combobox.get()
        return self.station

    def get_parameter(self):
        self.parameter = stationParameters.get(parameter_combobox.get(), "Key not found")  # Получение значения по ключу
        return self.parameter

    def get_start_time(self):
        self.start_time = start_time_entry.get()
        return self.start_time

    def get_end_time(self):
        self.end_time = end_time_entry.get()
        return self.end_time

    def get_interval(self):
        self.interval = interval_combobox.get()
        return self.interval

def get_data():
    user_data = Data()
    station = user_data.get_station()
    start_time = user_data.get_start_time()
    end_time = user_data.get_end_time()
    parameter = user_data.get_parameter()

    if not station or not parameter or not start_time or not end_time:
        messagebox.showerror("Ошибка", "Заполните все поля.")
        return

    if not start_time.isdigit() and not end_time.isdigit():
        messagebox.showerror("Ошибка", "Поля StartTime и EndTime должны быть заполнены целыми числами.")
        return

    try:
        data_dict = {}
        i = 1
        for parameter in stationParameters:
            t = int(time.time()) + 10800
            msg = {
                "meteoId": stationID[station],
                "endTime": t - int(end_time) * day,
                "parameterName": stationParameters.get(parameter).strip('"'),
                "startTime": t - int(start_time) * day
            }
            response = requests.post(url, json=msg)
            response.raise_for_status()
            print(f"Request {i}/7...")
            i += 1
            data = response.json()
            data_dict[stationParameters[parameter]] = data['values']['values']
        data_dict["DATE"] = data['dates']

        df = pd.DataFrame(data_dict)
        df = df.rename(columns=lambda x: x.strip('"'))
        df.to_csv('meteo_data.csv', index=False)

        messagebox.showinfo("Успех", "Данные успешно получены и сохранены в csv-файл.")
    except requests.exceptions.RequestException as e:
        messagebox.showerror("Ошибка", f"Произошла ошибка при отправке запроса: {e}")


def open_csv():
    try:
        if not os.path.exists('meteo_data.csv'):
            raise FileNotFoundError("Файл 'meteo_data.csv' не найден. Получите данные с метеостанции.")

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
    user_data = Data()
    parameter = user_data.get_parameter()
    interval = user_data.get_interval()
    if not os.path.exists('meteo_data.csv'):
        raise messagebox.showerror("Ошибка", "Файл 'meteo_data.csv' не найден. Получите данные с метеостанции.")
    if not parameter or not interval:
        raise messagebox.showerror("Ошибка", "Заполните поля 'Параметр' и 'Интервал'.")

    keyInterval = next(key for key, value in forecastIntervals.items() if value == interval)
    if parameter and interval:
        try:
            if interval == "1 час" or interval == "3 часа" or interval == "1 день":
                forecast = generate_forecast(parameter, keyInterval)
            elif interval == "3 дня":
                forecast = generate_forecast_3_day(parameter)
            elif interval == "1 неделя":
                forecast = generate_forecast_1_week(parameter)
            messagebox.showinfo("Прогноз", forecast)  # Отображаем прогноз в messagebox
        except Exception as e:
            messagebox.showerror("Ошибка", f"Произошла ошибка при получении прогноза: {e}")

root = tk.Tk()
root.title("Погода")
root.geometry("600x450")
data = Data()
station_label = tk.Label(root, text="Выберите станцию:", width=22)
station_label.pack(pady=5)
station_combobox = ttk.Combobox(root, values=list(stationID.keys()), width=22)
station_combobox.pack(pady=5)

start_time_label = tk.Label(root, text="Введите StartTime (в днях):", width=22)
start_time_label.pack(pady=5)
start_time_entry = tk.Entry(root, width=25)
start_time_entry.pack(pady=5)
start_time_entry.insert(0, "1460")

end_time_label = tk.Label(root, text="Введите EndTime (в днях):", width=22)
end_time_label.pack(pady=5)
end_time_entry = tk.Entry(root, width=25)
end_time_entry.pack(pady=5)
end_time_entry.insert(0, "0")

parameter_label = tk.Label(root, text="Выберите параметр погоды:", width=22)
parameter_label.pack(pady=5)
parameter_combobox = ttk.Combobox(root, values=list(stationParameters.keys()), width=22)
parameter_combobox.pack(pady=5)

interval_label = tk.Label(root, text="Длительность прогноза:", width=22)
interval_label.pack(pady=5)
interval_combobox = ttk.Combobox(root, values=list(forecastIntervals.values()), width=22)
interval_combobox.pack(pady=5)

data_button = tk.Button(root, text="Получить данные", command=get_data, width=22)
data_button.pack(pady=10)

open_button = tk.Button(root, text="Посмотреть данные", command=open_csv, width=22)
open_button.pack(pady=5)

# Кнопка для получения прогноза
predict_button = tk.Button(root, text="Получить прогноз", command=get_forecast, width=22)
predict_button.pack(pady=10)

root.mainloop()

def create_interface():
    return None