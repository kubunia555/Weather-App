from etl.fetch_weather import fetch_weather
from etl.transform import transform
from etl.load import load

from etl.aggregate import (
    create_daily_summary, 
    create_views
)

# pobieranie danych pogodowych z API
raw = fetch_weather()

# utworzenie 2 data frame
current_df, hourly_df = transform(raw)

# zapis danych do SQLite
load(current_df, hourly_df)

# tworzenie tabeli agregacyjnej
create_daily_summary()

# tworzenie SQL VIEW
create_views()