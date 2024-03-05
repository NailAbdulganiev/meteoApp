import time
import requests
import pandas as pd
import json

day = 86400
url = 'https://meteoapi.xn--b1ahgiuw.xn--p1ai/parameter/'
stationID = {
    "Сервисный центр": '"00001F76"',
    "Отделение 17": '"00001F77"',
    "Отделение 9": '"00001F78"',
    "Отделение 12": '"00001F7D"',
    "ПУ Север": '"0000235D"',
    "ПУ Кавказ": '"0000235E"'
}
stationParameters = {
    1: '"SOLAR_RADIATION"',  # Солнечная радиация
    2: '"PRECIPITATION"',  # Атмосферные осадки
    3: '"WIND_SPEED"',  # Скорость ветра
    4: '"LEAF_WETNESS"',  # Влажность листа
    5: '"HC_AIR_TEMPERATURE"',  # Температура воздуха
    6: '"HC_RELATIVE_HUMIDITY"',  # Влажность воздуха
    7: '"DEW_POINT"'  # Точка росы
}

# Создаем пустой словарь для хранения данных
data_dict = {}

try:
    for parameter in stationParameters:
        t = int(time.time())
        msg = {
            "meteoId": stationID.get("Сервисный центр").strip('"'),
            "endTime": t - day,
            "parameterName": stationParameters.get(parameter).strip('"'),
            "startTime": t - 3 * day
        }
        response = requests.post(url, json=msg)
        response.raise_for_status()
        print("Запрос успешно отправлен!")

        data = response.json()
        data_dict[stationParameters[parameter]] = data['values']['values']

        # Создаем DataFrame из полученных данных
        df = pd.DataFrame(data_dict)

        print(df)


    # # Делаем словарь, где время в часах это ключ, а значение параметра в то время - это values
    # data = response.json()
    # dates = data['dates']
    # values = data['values']['values']
    #
    # data_dict = dict(zip(dates, values))
    #
    # # Выводим данные
    # print("Ответ сервера:")
    # print("Dates and values:")
    # for date, value in data_dict.items():
    #     print(f"{date}: {value}")

except requests.exceptions.RequestException as e:
    print("Произошла ошибка при отправке запроса:", e)
