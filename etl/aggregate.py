import sqlite3  # biblioteka do obsługi SQLite

# ścieżka do bazy danych
DB_PATH = "data/weather.db"


def create_daily_summary():

    # połączenie z bazą danych
    conn = sqlite3.connect(DB_PATH)

    # cursor pozwala wykonywać zapytania SQL
    cursor = conn.cursor()

    # jeśli tabela już istnieje -> usuń ją
    cursor.execute("""
    DROP TABLE IF EXISTS weather_daily_summary
    """)

    # CREATE TABLE AS SELECT:
    # tworzy nową tabelę na podstawie wyniku zapytania SQL
    cursor.execute("""

    CREATE TABLE weather_daily_summary AS

    SELECT

        -- nazwa miasta
        city,

        -- pobieramy samą datę z timestampu
        DATE(time) as date,

        -- średnia temperatura
        ROUND(AVG(temperature), 2) as avg_temp,

        -- minimalna temperatura
        ROUND(MIN(temperature), 2) as min_temp,

        -- maksymalna temperatura
        ROUND(MAX(temperature), 2) as max_temp,

        -- średnia wilgotność
        ROUND(AVG(humidity), 2) as avg_humidity,

        -- średnia prędkość wiatru
        ROUND(AVG(wind_speed), 2) as avg_wind,

        -- liczba pomiarów
        COUNT(*) as measurements

    FROM weather_hourly

    -- grupowanie:
    -- osobno dla każdego miasta i dnia
    GROUP BY city, DATE(time)

    """)

    # zapisanie zmian do bazy
    conn.commit()

    # zamknięcie połączenia
    conn.close()

    print("Utworzono weather_daily_summary")


# TWORZENIE VIEWS SQL

def create_views():

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # VIEW - NAJCIEPLEJSZE MIASTA

    cursor.execute("""

    CREATE VIEW IF NOT EXISTS hottest_cities AS

    SELECT

        city,

        -- średnia temperatura dla miasta
        AVG(temperature) as avg_temp

    FROM weather_hourly
    -- grupowanie po mieście
    GROUP BY city
    -- sortowanie malejąco
    ORDER BY avg_temp DESC

    """)

    # VIEW - NAJBARDZIEJ WIETRZNE MIASTA

    cursor.execute("""

    CREATE VIEW IF NOT EXISTS windy_cities AS

    SELECT

        city,

        -- średnia prędkość wiatru
        AVG(wind_speed) as avg_wind

    FROM weather_hourly
    GROUP BY city
    -- od największego wiatru
    ORDER BY avg_wind DESC

    """)

    # VIEW - OSTATNIE DANE POGODOWE

    cursor.execute("""

    CREATE VIEW IF NOT EXISTS latest_weather AS

    SELECT

        city,
        temperature,
        humidity,
        wind_speed,
        cloud_cover,
        weather_code,
        timestamp

    FROM weather_current
    ORDER BY timestamp DESC

    """)

    # VIEW - NAJZIMNIEJSZE MIASTA

    cursor.execute("""

    CREATE VIEW IF NOT EXISTS coldest_cities AS

    SELECT

        city,
        AVG(temperature) as avg_temp

    FROM weather_hourly
    GROUP BY city
    ORDER BY avg_temp ASC

    """)

    # VIEW - NAJBARDZIEJ WILGOTNE

    cursor.execute("""

    CREATE VIEW IF NOT EXISTS most_humid_cities AS

    SELECT

        city,
        AVG(humidity) as avg_humidity

    FROM weather_hourly
    GROUP BY city
    ORDER BY avg_humidity DESC

    """)

    # VIEW - NAJMNIEJ WILGOTNE

    cursor.execute("""

    CREATE VIEW IF NOT EXISTS least_humid_cities AS

    SELECT

        city,
        AVG(humidity) as avg_humidity

    FROM weather_hourly
    GROUP BY city
    ORDER BY avg_humidity ASC

    """)

    # VIEW - NAJBARDZIEJ ZACHMURZONE

    cursor.execute("""

    CREATE VIEW IF NOT EXISTS cloudiest_cities AS

    SELECT

        city,
        AVG(cloud_cover) as avg_clouds

    FROM weather_current
    GROUP BY city
    ORDER BY avg_clouds DESC

    """)

    # VIEW - NAJBARDZIEJ SŁONECZNE

    cursor.execute("""

    CREATE VIEW IF NOT EXISTS clearest_cities AS

    SELECT

        city,
        AVG(cloud_cover) as avg_clouds

    FROM weather_current
    GROUP BY city
    ORDER BY avg_clouds ASC

    """)
            
    # VIEW - ALERTY POGODOWE

    cursor.execute("""

    CREATE VIEW IF NOT EXISTS weather_alerts AS

    SELECT

        city,
        temperature,
        wind_speed,
        humidity,

        CASE

            WHEN temperature < 0
                THEN 'UWAGA, TEMPERATURA PONIŻEJ 0!'

            WHEN temperature > 30
                THEN 'UWAGA, GORĄCO!'

            WHEN wind_speed > 40
                THEN 'UWAGA, SILNE WIATRY!'

            ELSE 'NORMALNE WARUNKI POGODOWE'

        END as alert_status

    FROM weather_current

    """)


    # VIEW - KATEGORIE TEMPERATURY

    cursor.execute("""

    CREATE VIEW IF NOT EXISTS weather_category AS

    SELECT

        city,
        temperature,

        CASE

            WHEN temperature < 0
                THEN 'Lodowato'

            WHEN temperature < 10
                THEN 'Zimno'

            WHEN temperature < 20
                THEN 'Chłodno'

            WHEN temperature < 30
                THEN 'Ciepło'

            ELSE 'Gorąco'

        END as temperature_category

    FROM weather_current

    """)


    # VIEW - PORÓWNANIE MIAST

    cursor.execute("""

    CREATE VIEW IF NOT EXISTS city_comparison AS

    SELECT

        city,
        ROUND(AVG(temperature), 2) as avg_temp,
        ROUND(AVG(humidity), 2) as avg_humidity,
        ROUND(AVG(wind_speed), 2) as avg_wind,
        ROUND(MIN(temperature), 2) as min_temp,
        ROUND(MAX(temperature), 2) as max_temp

    FROM weather_hourly
    GROUP BY city

    """)

    conn.commit()
    conn.close()

    print("Views utworzone")