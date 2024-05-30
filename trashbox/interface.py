import tkinter as tk
from tkinter import ttk
from tkinter import messagebox

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

# Функция для получения прогноза
def get_forecast():
    station = station_combobox.get()
    parameter = parameter_combobox.get()
    if not station or not parameter:
        messagebox.showerror("Ошибка", "Выберите станцию и параметр.")
        return
    station_value = stationID[station]

    # Найти ключ по значению
    parameter_key = None
    for key, value in stationParameters.items():
        if value == parameter:
            parameter_key = key
            break

    parameter_value = stationParameters[parameter_key]
    messagebox.showinfo("Прогноз", f"Станция: {station}\nПараметр: {parameter}")

# Создаем главное окно
root = tk.Tk()
root.title("Прогноз погоды")

# Устанавливаем размеры окна
root.geometry("400x200")

# Метка и выпадающий список для станций
station_label = tk.Label(root, text="Выберите станцию:")
station_label.pack(pady=5)
station_combobox = ttk.Combobox(root, values=list(stationID.keys()))
station_combobox.pack(pady=5)

# Метка и выпадающий список для параметров
parameter_label = tk.Label(root, text="Выберите параметр погоды:")
parameter_label.pack(pady=5)
parameter_combobox = ttk.Combobox(root, values=list(stationParameters.values()))
parameter_combobox.pack(pady=5)

# Кнопка для получения прогноза
forecast_button = tk.Button(root, text="Получить прогноз", command=get_forecast)
forecast_button.pack(pady=20)

# Запускаем главный цикл обработки событий
root.mainloop()
