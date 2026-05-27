import sqlite3 #baza danych wbudowana w pythona
import os  # praca z folderami i plikami


DB_PATH = "data/weather.db"  # sciezka do pliku bazy danych

def load(current_df, hourly_df): #  bierze tabele z transform.py
    os.makedirs("data", exist_ok=True)  #tworzy folder data if nie istnieje
    conn = sqlite3.connect(DB_PATH) # laczenie z baza , tworzy plik jesli nie istnieje
    
    # TABELA: CURRENT WEATHER
    current_df.to_sql(
        "weather_current",
        conn,
        if_exists="append",
        index=False
    )

     # TABELA: HOURLY WEATHER
    hourly_df.to_sql(
        "weather_hourly",
        conn,
        if_exists="append",
        index=False
    ) 

    conn.close() # zamkniecie polaczenia
    print(f"Zapisano {len(current_df)} miast i {len(hourly_df)} rekordów hourly.")  # pokazuje ile zapisano

