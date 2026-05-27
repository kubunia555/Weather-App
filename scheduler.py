import schedule # biblioteka do generowania co jakis czas taskow
import time # biblioteka do pracy z "czasem"

from etl.fetch_weather import fetch_weather # import danych z fetch_weat
from etl.transform import transform # import transform
from etl.load import load  # import pliku load

from etl.aggregate import (
    create_daily_summary,
    create_views
)

def run_pipeline():  # funkcja odpala pipeline

    print("Pobieram dane pogodowe...")

    raw = fetch_weather()  # get api dane z fetcha
    current_df, hourly_df = transform(raw)  # transofrmuje w tabele dane
    load(current_df, hourly_df)  #  zapisuje do bazy

    create_daily_summary()
    create_views()


    print("Gotowe!")



run_pipeline()  # uruchom od razu przy starcie

schedule.every(15).minutes.do(run_pipeline)  #co godzine  uruchamia
print("Scheduler działa...")


while True:  # petla nieskonczona - program dziala caly czas
    schedule.run_pending()  # sprawdza czy czas uruchomic pipeline
    time.sleep(60)  # czeka 60 sekund przed kolejnym sprawdzeniem