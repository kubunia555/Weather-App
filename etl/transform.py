import pandas as pd # biblioteka do pracy z danymi np excel
from datetime import datetime  # biblioteka do pracy z datami i czasem


def transform(raw_data): #funkcja przyjmuje liste danych z fetch_weather
    

    current_rows = [] # pusta lista na wiersze
    hourly_rows = [] # pusta lista na wiersze (godzinowo)

    for item in raw_data:  #petla 

        city = item["city_name"] 
        current = item["current"] #wyciaganie sekcji 'current' z api

        # Current Weather

        current_rows.append({  # dodajemy wiersz do listy
            "city":         city,   # nazwa miasta
            "lat":          item["latitude"],    # szerokosc geog
            "lon":          item["longitude"],   # dlugosc geog
            "temperature":  current["temperature_2m"],        # temperatura C
            "humidity":     current["relative_humidity_2m"],  # wilgotnosc w %
            "wind_speed":   current["wind_speed_10m"],        # predkosc wiatru km/h
            "weather_code": current["weather_code"],          # kod pogody np 0=slonecznie
            "cloud_cover":  current["cloud_cover"],           # zachmurzenie w %
            "sunrise":      item["daily"]["sunrise"][0],      # wschod slonca
            "sunset":       item["daily"]["sunset"][0],       # zachod slonca
            "timestamp":    datetime.now().isoformat()        # kiedy pobrano dane

        })

        # Hourly Weather

        hourly = item["hourly"]

        # zip scala listy razem
        for time, temp, hum, wind in zip(
            hourly["time"],
            hourly["temperature_2m"],
            hourly["relative_humidity_2m"],
            hourly["wind_speed_10m"]
        ):

            hourly_rows.append({
                "city": city,
                "time": time,
                "temperature": temp,
                "humidity": hum,
                "wind_speed": wind
            })

    # zwracamy DWIE tabele
    return (
        pd.DataFrame(current_rows),
        pd.DataFrame(hourly_rows)
    )