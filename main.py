import time
import requests
import pandas as pd

day = 86400
url = 'https://meteoapi.xn--b1ahgiuw.xn--p1ai/parameter/'
stationID = {
    "Сервисный центр": '"00001F76"',
    "Отделение 17": '"00001F77"',
    "Отделение 9": '"00001F78"',
    "ПУ Север": '"0000235D"',
    "ПУ Кавказ": '"0000235E"',
    "Отделение 12": '"00001F7D"',
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
            "endTime": t,
            "parameterName": stationParameters.get(parameter).strip('"'),
            "startTime": t - 7 * day
        }

        response = requests.post(url, json=msg)
        response.raise_for_status()
        print(f"Request {parameter}/7...")

        data = response.json()
        data_dict[stationParameters[parameter]] = data['values']['values']
    print(f"All requests have been sent successfully!")
    # Создаем DataFrame из полученных данных
    df = pd.DataFrame(data_dict)
    # Добавляем к DataFrame дату погодных данных
    df['Date'] = data['dates']
    # Удаляем кавычки в названии столбцов
    df = df.rename(columns=lambda x: x.strip('"'))
    df.to_csv('week.csv', index=False)
    # print(df)

except requests.exceptions.RequestException as e:
    print("An error occurred while sending the request:", e)
