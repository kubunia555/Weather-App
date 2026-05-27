import dash                          # framework do dashboardów webowych
from dash import dcc, html, dash_table  # komponenty: wykresy, HTML, tabele
from dash.dependencies import Input, Output  # powiązanie zdarzeń z funkcjami
import plotly.express as px          # tworzenie wykresów
import plotly.graph_objects as go    # puste wykresy (gdy brak danych)
import pandas as pd                  # operacje na danych (DataFrame)
import sqlite3                       # połączenie z bazą SQLite
import os

# ścieżka do bazy danych
DB_PATH = "data/weather.db"


def get_connection():
    """Otwiera połączenie z bazą SQLite."""
    return sqlite3.connect(DB_PATH)


def load_table(table_name):
    """Wczytuje tabelę/widok z bazy jako DataFrame."""
    conn = get_connection()
    df = pd.read_sql(f"SELECT * FROM {table_name}", conn)
    conn.close()

    return df


# sprawdzenie czy baza istnieje
if not os.path.exists(DB_PATH):
    print("UWAGA: Brak bazy danych! Uruchom najpierw: python main.py")

# tworzenie aplikacji Dash
app = dash.Dash(__name__)
app.title = "Dashboard Pogodowy"

# --- LAYOUT (struktura strony) ---
app.layout = html.Div(
    style={"fontFamily": "Arial, sans-serif", "padding": "20px", "backgroundColor": "#f5f5f5"},
    children=[
        # nagłówek
        html.H1("Dashboard Pogodowy - Polska", style={"textAlign": "center"}),
        html.P("Dane pogodowe dla 5 największych miast", style={"textAlign": "center", "color": "gray"}),

        # odświeżanie co 5 minut (Interval wyzwala callbacki automatycznie)
        dcc.Interval(id="interval-refresh", interval=5 * 60 * 1000, n_intervals=0),

        # --- AKTUALNA POGODA ---
        html.H2("Aktualna pogoda"),
        html.Div(id="current-weather-cards", style={"display": "flex", "flexWrap": "wrap", "gap": "15px", "marginBottom": "30px"}),

        # --- ALERTY ---
        html.H2("Alerty pogodowe"),
        html.Div(id="alerts-section", style={"marginBottom": "30px"}),

        # --- WYKRESY GODZINOWE ---
        html.H2("Wykresy godzinowe"),
        html.Label("Wybierz miasto:", style={"fontWeight": "bold"}),
        dcc.Dropdown(
            id="city-dropdown",
            options=[
                {"label": "Warszawa", "value": "Warsaw"},
                {"label": "Kraków", "value": "Krakow"},
                {"label": "Gdańsk", "value": "Gdansk"},
                {"label": "Wrocław", "value": "Wroclaw"},
                {"label": "Poznań", "value": "Poznan"},
            ],
            value="Warsaw",
            style={"width": "250px", "marginBottom": "20px"},
        ),
        dcc.Graph(id="hourly-temp-chart"),
        dcc.Graph(id="hourly-humidity-chart"),

        # --- PORÓWNANIE MIAST ---
        html.H2("Porównanie miast"),
        dcc.Graph(id="comparison-temp-chart"),
        dcc.Graph(id="comparison-wind-chart"),

        # --- RANKINGI MIAST ---
        html.H2("Rankingi miast"),
        html.Div(id="rankings-section", style={"display": "flex", "flexWrap": "wrap", "gap": "15px", "marginBottom": "30px"}),

        # --- PODSUMOWANIE DZIENNE ---
        html.H2("Podsumowanie dzienne"),
        html.Div(id="daily-summary-table", style={"marginBottom": "30px"}),

        # stopka
        html.P("Dane z API: Open-Meteo | Dashboard © 2026", style={"textAlign": "center", "color": "gray", "marginTop": "40px"}),
    ],
)


# --- CALLBACK 1: aktualna pogoda, alerty, porównanie miast, tabela ---
# Dekorator @app.callback łączy Input (co wyzwala) z Output (co aktualizować)
@app.callback(
    [
        Output("current-weather-cards", "children"),
        Output("alerts-section", "children"),
        Output("comparison-temp-chart", "figure"),
        Output("comparison-wind-chart", "figure"),
        Output("rankings-section", "children"),
        Output("daily-summary-table", "children"),
    ],
    Input("interval-refresh", "n_intervals"),  # wyzwalane przez timer co 5 min
)

def update_dashboard(_):
    """Odświeża główne elementy dashboardu."""

    if not os.path.exists(DB_PATH):
        empty_fig = go.Figure()
        empty_fig.update_layout(title="Brak danych - uruchom main.py")
        no_data = html.P("Brak danych. Uruchom: python main.py", style={"color": "red"})

        return no_data, no_data, empty_fig, empty_fig, no_data, no_data

    # --- AKTUALNA POGODA (karty) ---
    try:
        latest_df = load_table("latest_weather")
    except Exception:
        latest_df = load_table("weather_current")

    # sortujemy po timestamp malejąco i bierzemy pierwszy (najnowszy) wiersz per miasto
    if not latest_df.empty:
        latest_df = latest_df.sort_values("timestamp", ascending=False).groupby("city").first().reset_index()

    # opisy pogody wg kodów WMO
    weather_desc = {
        0: "Bezchmurnie", 1: "Prawie bezchmurnie", 2: "Częściowe zachmurzenie", 3: "Pochmurno",
        45: "Mgła", 48: "Mgła",
        51: "Mżawka", 53: "Mżawka", 55: "Mżawka",
        61: "Deszcz", 63: "Deszcz", 65: "Silny deszcz",
        71: "Śnieg", 73: "Śnieg", 75: "Silny śnieg",
        80: "Przelotny deszcz", 81: "Przelotny deszcz", 82: "Przelotny deszcz",
        95: "Burza", 96: "Burza z gradem", 99: "Burza z gradem",
    }

    cards = []
    for _, row in latest_df.iterrows():
        code = row.get("weather_code", 0)
        desc = weather_desc.get(int(code) if pd.notna(code) else 0, "Brak danych")
        card = html.Div(
            style={"backgroundColor": "white", "borderRadius": "10px", "padding": "15px",
                   "boxShadow": "0 2px 5px rgba(0,0,0,0.1)", "minWidth": "180px", "flex": "1"},
            children=[
                html.H3(row['city']),
                html.P(f"Pogoda: {desc}"),
                html.P(f"Temperatura: {round(row['temperature'], 2)}°C", style={"fontSize": "20px", "fontWeight": "bold"}),
                html.P(f"Wilgotność: {round(row['humidity'], 2)}%"),
                html.P(f"Wiatr: {round(row['wind_speed'], 2)} km/h"),
            ],
        )
        cards.append(card)

    # --- ALERTY ---
    try:
        alerts_df = load_table("weather_alerts")
        alert_items = []
        for _, row in alerts_df.iterrows():
            color = "green" if "NORMALNE" in row["alert_status"] else "red"
            alert_items.append(html.P(
                f"{row['city']}: {row['alert_status']} (temp: {row['temperature']}°C, wiatr: {row['wind_speed']} km/h)",
                style={"color": color}
            ))
        alerts_section = html.Div(alert_items) if alert_items else html.P("Brak alertów.", style={"color": "green"})
    except Exception:
        alerts_section = html.P("Brak danych o alertach.", style={"color": "gray"})

    # --- PORÓWNANIE MIAST (wykresy słupkowe) ---
    try:
        comparison_df = load_table("city_comparison")
    except Exception:
        comparison_df = pd.DataFrame()

    if not comparison_df.empty:
        fig_temp = px.bar(comparison_df, x="city", y="avg_temp", title="Średnia temperatura (°C)", color="avg_temp", color_continuous_scale="RdYlBu_r")
        fig_wind = px.bar(comparison_df, x="city", y="avg_wind", title="Średnia prędkość wiatru (km/h)", color="avg_wind", color_continuous_scale="Blues")
    else:
        fig_temp = fig_wind = go.Figure()

    # --- RANKINGI MIAST (bloczki z widoków) ---
    rankings_config = [
        ("hottest_cities", "Najcieplejsze", "avg_temp", "°C"),
        ("coldest_cities", "Najchłodniejsze", "avg_temp", "°C"),
        ("most_humid_cities", "Najbardziej wilgotne", "avg_humidity", "%"),
        ("least_humid_cities", "Najmniej wilgotne", "avg_humidity", "%"),
        ("windy_cities", "Najwiętrzniejsze", "avg_wind", "km/h"),
        ("cloudiest_cities", "Najbardziej pochmurne", "avg_clouds", "%"),
        ("clearest_cities", "Najjaśniejsze", "avg_clouds", "%"),
    ]

    ranking_blocks = []
    for view_name, title, col, unit in rankings_config:
        try:
            df = load_table(view_name)
            items = [html.Li(f"{row['city']}: {round(row[col], 2)} {unit}") for _, row in df.iterrows()]
            block = html.Div(
                style={"backgroundColor": "white", "borderRadius": "10px", "padding": "15px",
                       "boxShadow": "0 2px 5px rgba(0,0,0,0.1)", "minWidth": "200px", "flex": "1"},
                children=[html.H4(title), html.Ul(items)],
            )
            ranking_blocks.append(block)
        except Exception:
            pass

    rankings_section = ranking_blocks if ranking_blocks else html.P("Brak danych.", style={"color": "gray"})

    # --- TABELA PODSUMOWANIA DZIENNEGO ---
    try:
        daily_df = load_table("weather_daily_summary")
        daily_table = dash_table.DataTable(
            data=daily_df.to_dict("records"),
            columns=[
                {"name": "Miasto", "id": "city"},
                {"name": "Data", "id": "date"},
                {"name": "Śr. temp (°C)", "id": "avg_temp"},
                {"name": "Min temp (°C)", "id": "min_temp"},
                {"name": "Max temp (°C)", "id": "max_temp"},
                {"name": "Śr. wilgotność (%)", "id": "avg_humidity"},
                {"name": "Śr. wiatr (km/h)", "id": "avg_wind"},
            ],
            style_header={"backgroundColor": "#3498db", "color": "white", "fontWeight": "bold"},
            style_cell={"padding": "8px", "textAlign": "center"},
            sort_action="native",
            page_size=10,
        )
    except Exception:
        daily_table = html.P("Brak danych dziennych.", style={"color": "gray"})

    return cards, alerts_section, fig_temp, fig_wind, rankings_section, daily_table


# --- CALLBACK 2: wykresy godzinowe (reaguje na zmianę miasta w dropdown) ---
@app.callback(
    [Output("hourly-temp-chart", "figure"), Output("hourly-humidity-chart", "figure")],
    [Input("city-dropdown", "value"), Input("interval-refresh", "n_intervals")],
)

def update_hourly_charts(city, _):
    """Aktualizuje wykresy godzinowe dla wybranego miasta."""

    if not os.path.exists(DB_PATH):
        empty_fig = go.Figure()
        return empty_fig, empty_fig

    conn = get_connection()
    query = "SELECT * FROM weather_hourly WHERE city = ? ORDER BY time"
    hourly_df = pd.read_sql(query, conn, params=[city])
    conn.close()

    if hourly_df.empty:
        empty_fig = go.Figure()
        empty_fig.update_layout(title=f"Brak danych dla {city}")

        return empty_fig, empty_fig

    # wykres temperatury
    fig_temp = px.line(hourly_df, x="time", y="temperature", title=f"Temperatura godzinowa - {city}")
    fig_temp.update_traces(line_color="red")

    # wykres wilgotności
    fig_hum = px.line(hourly_df, x="time", y="humidity", title=f"Wilgotność godzinowa - {city}")
    fig_hum.update_traces(line_color="blue")

    return fig_temp, fig_hum


# --- URUCHOMIENIE ---
if __name__ == "__main__":
    print("Dashboard dostępny pod adresem: http://127.0.0.1:8050")
    app.run(debug=True)
