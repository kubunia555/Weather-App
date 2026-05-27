# Weather Pipeline Dashboard 🌤️

Aplikacja ETL pobierająca dane pogodowe z API Open-Meteo dla 5 największych miast w Polsce (Warszawa, Kraków, Gdańsk, Wrocław, Poznań) i prezentująca je na interaktywnym dashboardzie webowym.

## Jak działa aplikacja

### Pipeline ETL (`main.py`)

1. **Fetch** — `etl/fetch_weather.py` wysyła zapytania HTTP do API Open-Meteo i pobiera dane bieżące + prognozę godzinową dla 5 miast
2. **Transform** — `etl/transform.py` przetwarza surowy JSON na dwa pandas DataFrame: `weather_current` (aktualna pogoda) i `weather_hourly` (168 godzin prognozy)
3. **Load** — `etl/load.py` zapisuje DataFrame do bazy SQLite (`data/weather.db`)
4. **Aggregate** — `etl/aggregate.py` tworzy tabelę `weather_daily_summary` (agregaty dzienne) oraz widoki SQL: `latest_weather`, `city_comparison`, `weather_alerts`, `cloudiest_cities`

### Scheduler (`scheduler.py`)

Uruchamia pipeline co 15 minut w pętli nieskończonej (biblioteka `schedule`). Dzięki temu baza danych jest na bieżąco aktualizowana.

### Dashboard (`dashboard.py`)

Interaktywna aplikacja webowa zbudowana w **Dash + Plotly**. Po uruchomieniu startuje lokalny serwer HTTP na porcie **8050**.

#### Sekcje dashboardu:

1. **Aktualna pogoda** — karty z bieżącą temperaturą, wilgotnością, wiatrem i zachmurzeniem dla każdego miasta (ikony dobierane wg kodu pogodowego WMO)
2. **Alerty pogodowe** — ostrzeżenia o ekstremalnych warunkach (upał, silny wiatr) z kolorowym oznaczeniem (zielony = OK, czerwony = alert)
3. **Wykresy godzinowe** — interaktywne wykresy liniowe temperatury i wilgotności w czasie dla wybranego miasta (lista rozwijana)
4. **Porównanie miast** — wykresy słupkowe: średnia temperatura, wiatr, wilgotność, zachmurzenie
5. **Podsumowanie dzienne** — tabela z agregatami (min/max/śr. temperatury, wilgotność, wiatr) z sortowaniem i filtrowaniem

Dashboard automatycznie odświeża dane co 5 minut (komponent `dcc.Interval`).

#### Jak działa technicznie:

- `app.layout` — definiuje strukturę strony (HTML + komponenty Dash)
- `@app.callback` — dekoratory łączące zdarzenia (np. wybór miasta, timer) z funkcjami aktualizującymi wykresy/karty
- Dane pobierane z SQLite przy każdym odświeżeniu i przekazywane do wykresów Plotly

## Struktura projektu

```
main.py           – jednorazowe pobranie danych i zapis do bazy
scheduler.py      – cykliczne pobieranie danych co 15 minut
dashboard.py      – interaktywny dashboard webowy
etl/
  fetch_weather.py  – pobieranie danych z API Open-Meteo
  transform.py      – transformacja JSON → DataFrame
  load.py           – zapis do SQLite (data/weather.db)
  aggregate.py      – agregacje i widoki SQL
data/
  weather.db        – baza danych SQLite (generowana automatycznie)
```

## Wymagania

- Python 3.10+
- Pakiety: `pandas`, `requests`, `dash`, `plotly`, `schedule`
- Połączenie z internetem (API Open-Meteo)

## Instalacja i uruchomienie

### Linux (Ubuntu/Debian)

```bash
# 1. Wejście do katalogu projektu
cd project

# 2. Utworzenie środowiska wirtualnego (izolacja pakietów od systemu)
python3 -m venv .venv

# 3. Aktywacja środowiska wirtualnego
source .venv/bin/activate

# 4. Instalacja wymaganych pakietów
pip install pandas requests dash plotly schedule

# 5. Pobranie danych pogodowych i utworzenie bazy danych
python3 main.py

# 6. Uruchomienie dashboardu
python3 dashboard.py
```

> **Uwaga:** Jeśli `python3 -m venv` nie działa, zainstaluj: `sudo apt install python3.12-venv`

Dashboard będzie dostępny pod adresem: **http://127.0.0.1:8050**

Aby dane odświeżały się automatycznie w tle, uruchom scheduler w osobnym terminalu:

```bash
source .venv/bin/activate
python3 scheduler.py
```

### Windows (PowerShell)

```powershell
# 1. Wejście do katalogu projektu
cd project

# 2. Utworzenie środowiska wirtualnego
python -m venv .venv

# 3. Aktywacja środowiska wirtualnego
.venv\Scripts\activate

# 4. Instalacja wymaganych pakietów
pip install pandas requests dash plotly schedule

# 5. Pobranie danych pogodowych i utworzenie bazy danych
python main.py

# 6. Uruchomienie dashboardu
python dashboard.py
```

> **Uwaga:** Jeśli skrypt aktywacji nie działa, uruchom wcześniej:
> `Set-ExecutionPolicy -Scope CurrentUser -ExecutionPolicy RemoteSigned`

Dashboard będzie dostępny pod adresem: **http://127.0.0.1:8050**

Aby dane odświeżały się automatycznie, uruchom w osobnym terminalu:

```powershell
.venv\Scripts\activate
python scheduler.py
```

## Zatrzymywanie

- Dashboard / Scheduler: `Ctrl+C` w terminalu
- Deaktywacja środowiska wirtualnego: `deactivate`

## Źródło danych

[Open-Meteo API](https://open-meteo.com/) — darmowe API pogodowe, nie wymaga klucza API.
