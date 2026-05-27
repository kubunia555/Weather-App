from etl.fetch_weather import fetch_weather
from etl.transform import transform

raw = fetch_weather()

current_df, hourly_df = transform(raw)

print(current_df.head())
print(hourly_df.head())