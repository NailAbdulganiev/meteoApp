import os
import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
import time
import requests
import pandas as pd

# Словари данных
stationID = {
    "Сервисный центр": "00001F76",
    "Отделение 17": "00001F77",
    "Отделение 9": "00001F78",
    "ПУ Север": "0000235D",
    "ПУ Кавказ": "0000235E",
    "Отделение 12": "00001F7D",
}

stationParameters = {
    1: "SOLAR_RADIATION",  # Солнечная радиация
    2: "PRECIPITATION",  # Атмосферные осадки
    3: "WIND_SPEED",  # Скорость ветра
    4: "LEAF_WETNESS",  # Влажность листа
    5: "HC_AIR_TEMPERATURE",  # Температура воздуха
    6: "HC_RELATIVE_HUMIDITY",  # Влажность воздуха
    7: "DEW_POINT"  # Точка росы
}

url = 'https://meteoapi.xn--b1ahgiuw.xn--p1ai/parameter/'
day = 86400


# Функция для получения прогноза
def get_forecast():
    global data
    station = station_combobox.get()
    parameter = parameter_combobox.get()
    start_time = start_time_entry.get()
    end_time = end_time_entry.get()

    if not station or not parameter or not start_time or not end_time:
        messagebox.showerror("Ошибка", "Заполните все поля.")
        return

    station_value = stationID[station]

    # Найти ключ по значению
    parameter_key = None
    for key, value in stationParameters.items():
        if value == parameter:
            parameter_key = key
            break

    parameter_value = stationParameters[parameter_key]
    #print(station_value)
    #print(start_time)
    #print(end_time)
    #print(parameter_value)

    try:
        data_dict = {}
        for parameter in stationParameters:
            t = int(time.time())
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

        # Создаем DataFrame из полученных данных
        df = pd.DataFrame(data_dict)
        df = df.rename(columns=lambda x: x.strip('"'))
        df.to_csv('meteo_data.csv', index=False)

        messagebox.showinfo("Успех", f"Данные успешно получены и сохранены в csv-файл.")
    except requests.exceptions.RequestException as e:
        messagebox.showerror("Ошибка", f"Произошла ошибка при отправке запроса: {e}")


# Функция для открытия CSV-файла и отображения данных в новом окне
def open_csv():
    try:
        # Проверяем существование файла
        if not os.path.exists('meteo_data.csv'):
            raise FileNotFoundError("Файл 'meteo_data.csv' не найден.")

        # Читаем CSV файл в DataFrame
        df = pd.read_csv('meteo_data.csv')

        # Создаем новое окно
        window = tk.Toplevel(root)

        # Создаем и настраиваем Treeview для отображения данных
        tree = ttk.Treeview(window)
        tree["columns"] = list(df.columns)
        tree["show"] = "headings"
        for column in df.columns:
            tree.heading(column, text=column)

        # Вставляем данные в Treeview
        for index, row in df.iterrows():
            tree.insert("", "end", values=list(row))

        # Размещаем Treeview на окне
        tree.pack(fill="both", expand=True)

        # Закрываем окно по кнопке
        close_button = ttk.Button(window, text="Закрыть", command=window.destroy)
        close_button.pack(pady=10)

    except FileNotFoundError as e:
        messagebox.showerror("Ошибка", str(e))
    except Exception as e:
        messagebox.showerror("Ошибка", f"Произошла ошибка: {e}")


# Создаем главное окно
root = tk.Tk()
root.title("Погода")

# Устанавливаем размеры окна
root.geometry("600x400")

# Метка и выпадающий список для станций
station_label = tk.Label(root, text="Выберите станцию:")
station_label.pack(pady=5)
station_combobox = ttk.Combobox(root, values=list(stationID.keys()))
station_combobox.pack(pady=5)

# Метка и текстовое поле для StartTime
start_time_label = tk.Label(root, text="Введите StartTime (в днях):")
start_time_label.pack(pady=5)
start_time_entry = tk.Entry(root)
start_time_entry.pack(pady=5)

# Метка и текстовое поле для EndTime
end_time_label = tk.Label(root, text="Введите EndTime (в днях):")
end_time_label.pack(pady=5)
end_time_entry = tk.Entry(root)
end_time_entry.pack(pady=5)

# Метка и выпадающий список для параметров
parameter_label = tk.Label(root, text="Выберите параметр погоды:")
parameter_label.pack(pady=5)
parameter_combobox = ttk.Combobox(root, values=list(stationParameters.values()))
parameter_combobox.pack(pady=5)

# Кнопка для получения прогноза
forecast_button = tk.Button(root, text="Получить данные", command=get_forecast)
forecast_button.pack(pady=10)

# Кнопка для открытия CSV файла и отображения данных
open_button = tk.Button(root, text="Посмотреть данные", command=open_csv)
open_button.pack(pady=5)

# Запускаем главный цикл обработки событий
root.mainloop()
