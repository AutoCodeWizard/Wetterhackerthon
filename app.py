import streamlit as st
import requests
import requests_cache
from retry_requests import retry
from datetime import datetime
import plotly.express as px
import plotly.graph_objects as go
import folium
from streamlit_folium import folium_static
import numpy as np

# Funktionen zum Abrufen der Geodaten und Wetterdaten
def get_geocoding(city_name):
    headers = {
        "Content-Type": "application/json"
    }
    geocoding_api_endpoint = f"https://geocoding-api.open-meteo.com/v1/search?name={city_name}&count=5&language=en&format=json"
    try:
        response = requests.get(url=geocoding_api_endpoint, headers=headers)
        response.raise_for_status()
        result = response.json()["results"]
        return sorted(result, key=lambda a: -a["population"] if ("population" in a) else 0)
    except requests.RequestException as e:
        return str(e)

def get_weather(latitude, longitude, start_date, end_date):
    cache_session = requests_cache.CachedSession('.cache', expire_after=3600)
    retry_session = retry(cache_session, retries=5, backoff_factor=0.2)
    url = "https://api.open-meteo.com/v1/forecast"
    params = {
        "latitude": latitude,
        "longitude": longitude,
        "daily": ["weather_code", "temperature_2m_max", "temperature_2m_min", "apparent_temperature_max",
                  "apparent_temperature_min", "uv_index_max", "precipitation_sum", "precipitation_probability_max"],
        "start_date": start_date,
        "end_date": end_date
    }
    try:
        response = retry_session.get(url, params=params)
        response.raise_for_status()
        daily = response.json()["daily"]
        dates = daily["time"]
        weather_data = {
            date: {
                "weather_code": daily["weather_code"][i],
                "temperature_max": daily["temperature_2m_max"][i],
                "temperature_min": daily["temperature_2m_min"][i],
                "apparent_temperature_max": daily["apparent_temperature_max"][i],
                "apparent_temperature_min": daily["apparent_temperature_min"][i],
                "uv_index": daily["uv_index_max"][i],
                "precipitation_probability": daily["precipitation_probability_max"][i],
                "precipitation_sum": daily["precipitation_sum"][i]
            }
            for i, date in enumerate(dates)
        }
        return weather_data
    except requests.RequestException as e:
        return str(e)

def activity_recommendation(weather_code, temperature_max):
    if temperature_max > 25:
        if weather_code in [0, 1, 2]:  # Sonniges Wetter
            return "Ideal für einen Tag am Strand oder eine Wanderung in der Natur!"
        else:
            return "Ein guter Tag für Indoor-Aktivitäten mit Klimaanlage."
    elif 15 < temperature_max <= 25:
        if weather_code in [0, 1, 2]:  # Leicht bewölkt bis sonnig
            return "Perfekt für einen Stadtrundgang oder eine Fahrradtour."
        elif weather_code in [3, 45]:  # Bewölkt oder Nebel
            return "Gut für den Besuch eines Museums oder eines Indoor-Sportzentrums."
        else:
            return "Wie wäre es mit einem entspannenden Tag in einer Bibliothek oder einem Café?"
    elif 5 < temperature_max <= 15:
        if weather_code in [71, 73, 75]:  # Schneefall
            return "Zeit für Winteraktivitäten wie Schlittschuhlaufen oder Skifahren!"
        else:
            return "Ein guter Tag für Indoor-Aktivitäten oder ein warmes Thermalbad."
    else:
        return "Bleiben Sie warm und genießen Sie gemütliche Indoor-Aktivitäten wie Kochen oder Filmabende."

def plot_temperature(weather_data):
    dates = list(weather_data.keys())
    max_temps = [data['temperature_max'] for data in weather_data.values()]
    min_temps = [data['temperature_min'] for data in weather_data.values()]

    fig = go.Figure()
    fig.add_trace(go.Scatter(x=dates, y=max_temps, mode='lines+markers', name='Max Temp', line=dict(color='red')))
    fig.add_trace(go.Scatter(x=dates, y=min_temps, mode='lines+markers', name='Min Temp', line=dict(color='blue')))
    fig.update_layout(title='Temperaturverlauf', xaxis_title='Datum', yaxis_title='Temperatur (°C)')
    return fig

def add_activity_markers(map_object, latitude, longitude):
    activities = [
        {"name": "Museum", "lat": latitude + 0.01, "lon": longitude, "type": "Indoor"},
        {"name": "Park", "lat": latitude - 0.01, "lon": longitude, "type": "Outdoor"},
        {"name": "Cafe", "lat": latitude, "lon": longitude + 0.01, "type": "Indoor"},
        {"name": "Shopping Center", "lat": latitude, "lon": longitude - 0.01, "type": "Indoor"},
    ]

    for activity in activities:
        folium.Marker(
            location=[activity["lat"], activity["lon"]],
            popup=f'{activity["name"]} ({activity["type"]})',
            icon=folium.Icon(color='blue' if activity["type"] == "Indoor" else 'green')
        ).add_to(map_object)

# Streamlit App
st.set_page_config(page_title="Wettervorhersage", layout="wide")

st.title("Wettervorhersage")
st.sidebar.write("Geben Sie eine Stadt ein, um die Wettervorhersage und Aktivitätenvorschläge zu erhalten.")

city_name = st.sidebar.text_input("Stadtname:", "")
start_date = st.sidebar.date_input("Startdatum:", datetime.now())
end_date = st.sidebar.date_input("Enddatum:", datetime.now())

if st.sidebar.button("Vorhersage anzeigen") and city_name:
    with st.spinner('Abrufen der Geodaten...'):
        geocoding_results = get_geocoding(city_name)
        if isinstance(geocoding_results, list) and geocoding_results:
            city_info = geocoding_results[0]
            latitude = city_info["latitude"]
            longitude = city_info["longitude"]
            st.write(f"Stadt: {city_info['name']}, Land: {city_info['country']}")
            st.write(f"Koordinaten: {latitude}, {longitude}")

            with st.spinner('Wetterdaten werden geladen...'):
                weather_data = get_weather(latitude, longitude, start_date.strftime("%Y-%m-%d"), end_date.strftime("%Y-%m-%d"))
                if isinstance(weather_data, dict):
                    st.write("Wettervorhersage:")
                    fig = plot_temperature(weather_data)
                    st.plotly_chart(fig)
                    for date, data in weather_data.items():
                        st.write(f"**Datum:** {date}")
                        st.write(f"**Maximale Temperatur:** {data['temperature_max']}°C, **Minimale Temperatur:** {data['temperature_min']}°C")
                        st.write(f"**Gefühlte maximale Temperatur:** {data['apparent_temperature_max']}°C, **Gefühlte minimale Temperatur:** {data['apparent_temperature_min']}°C")
                        st.write(f"**UV-Index:** {data['uv_index']}, **Niederschlagswahrscheinlichkeit:** {data['precipitation_probability']}%")
                        st.write(f"**Niederschlagssumme:** {data['precipitation_sum']} mm")
                        activity = activity_recommendation(data['weather_code'], data['temperature_max'])
                        st.write(f"**Empfohlene Aktivität:** {activity}")
                        st.write("---")

                    # Karte anzeigen
                    m = folium.Map(location=[latitude, longitude], zoom_start=12, tiles='cartodbpositron')
                    add_activity_markers(m, latitude, longitude)
                    folium.Marker([latitude, longitude], tooltip=city_info['name']).add_to(m)
                    folium.TileLayer(
                        tiles='https://mt1.google.com/vt/lyrs=s&x={x}&y={y}&z={z}',
                        attr='Google',
                        name='Google Satellite',
                        overlay=True,
                        control=True
                    ).add_to(m)
                    folium.LayerControl().add_to(m)
                    folium_static(m)
                else:
                    st.error(f"Fehler beim Abrufen der Wetterdaten: {weather_data}")
        else:
            st.error(f"Fehler beim Abrufen der Geodaten: {geocoding_results}")
else:
    st.info("Bitte geben Sie einen Stadtnamen ein und klicken Sie auf 'Vorhersage anzeigen'.")
