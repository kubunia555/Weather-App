
import requests  #request biblioteka most miedzy kodem a internetem.

CITIES = {   #klucz wartosc szer geograficzna  cities z duzych nie zmieniaja sie podczas dzialania programu
    "Warsaw":  (52.23, 21.01),
    "Krakow":  (50.06, 19.94),
    "Gdansk":  (54.35, 18.65),
    "Wroclaw": (51.11, 17.04),
    "Poznan":  (52.41, 16.93),
}

def fetch_weather(): #funkcja fetch trzeba ja wywolac sama nie zadziala;
   
   
    results = []  #lista z wynikami, tu trafia wyniki z pobrania danych API

    for city, (lat, lon) in CITIES.items():
        url = "https://api.open-meteo.com/v1/forecast"  #api z ktorego bierzemy dane pogodowe
        params = {  # parametry zapytania co chcemy dostac
            "latitude": lat,   # szerok geog
            "longitude": lon, # dlugosc geog

            "current": "temperature_2m,relative_humidity_2m,wind_speed_10m,weather_code,cloud_cover",  # jakie obecne dane chcemy pobrac, zachmurzenie
            "hourly": "temperature_2m,relative_humidity_2m,wind_speed_10m", # dane godzinowe
            "daily": "sunrise,sunset",  # wschod i zachod slonca 
            "timezone": "Europe/Warsaw"  # strefa czasowa
        }


        response = requests.get(url, params=params) # request do  api -> pobranie api 


        if response.status_code == 200:  #warunek jesli request jest ok to zwoc  http code 200 czyli ok
                     data = response.json()  #zmiana odpowiedzi z formatu json na python
                     data["city_name"] = city #dopisanie nazwy miasta do danych, api nie zwraca a bedzie potrzebna zeby wiedziec
                     results.append(data)  #dodaje dane do miasta z listy "results"

        else:
             print(f"Błąd dla {city}: {response.status_code}")              # tutaj  jesli znajdzie blad to jaki jest http status code zeby wiedziec
               
    return results  #zwraca wyniki potem przekaze

