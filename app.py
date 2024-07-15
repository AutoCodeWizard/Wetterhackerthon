import streamlit as st
import requests
import requests_cache
from retry_requests import retry
import pandas as pd

# Funktionen zum Abrufen der Geodaten und Wetterdaten
def get_geocoding(city_name):
    headers = {
        "Content-Type": "application/json"
    }
    geocoding_api_endpoint = f"https://geocoding-api.open-meteo.com/v1/search?name={city_name}&count=5&language=en&format=json"
    response = requests.get(url=geocoding_api_endpoint, headers=headers)

    if response.status_code == 200:
        result = response.json()["results"]
        return sorted(result, key=lambda a: -a["population"] if ("population" in a) else 0)
    else:
        return Exception(response.status_code)

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
    response = retry_session.get(url, params=params)
    if response.status_code == 200:
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
    else:
        return Exception(response.status_code)

# Streamlit App
st.title("Wettervorhersage App")
st.write("Geben Sie eine Stadt ein, um die Wettervorhersage zu erhalten.")

city_name = st.text_input("Stadtname:")
start_date = st.date_input("Startdatum:")
end_date = st.date_input("Enddatum:")

if st.button("Vorhersage anzeigen"):
    if city_name:
        geocoding_results = get_geocoding(city_name)
        if isinstance(geocoding_results, list) and geocoding_results:
            city_info = geocoding_results[0]
            latitude = city_info["latitude"]
            longitude = city_info["longitude"]
            st.write(f"Stadt: {city_info['name']}, Land: {city_info['country']}")
            st.write(f"Koordinaten: {latitude}, {longitude}")
            weather_data = get_weather(latitude, longitude, start_date.strftime("%Y-%m-%d"), end_date.strftime("%Y-%m-%d"))
            if isinstance(weather_data, dict):
                st.write("Wettervorhersage:")
                for date, data in weather_data.items():
                    st.write(f"Datum: {date}")
                    st.write(f"Wettercode: {data['weather_code']}")
                    st.write(f"Maximale Temperatur: {data['temperature_max']}°C")
                    st.write(f"Minimale Temperatur: {data['temperature_min']}°C")
                    st.write(f"Gefühlte maximale Temperatur: {data['apparent_temperature_max']}°C")
                    st.write(f"Gefühlte minimale Temperatur: {data['apparent_temperature_min']}°C")
                    st.write(f"UV-Index: {data['uv_index']}")
                    st.write(f"Niederschlagswahrscheinlichkeit: {data['precipitation_probability']}%")
                    st.write(f"Niederschlagssumme: {data['precipitation_sum']} mm")
                    st.write("---")
            else:
                st.error("Fehler beim Abrufen der Wetterdaten.")
        else:
            st.error("Fehler beim Abrufen der Geodaten.")
    else:
        st.error("Bitte geben Sie einen Stadtnamen ein.")
