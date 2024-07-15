import requests
import openmeteo_requests
import requests_cache
from retry_requests import retry
from pprint import pprint
import pandas as pd

"""
requires: city_name: Den Namen der Stadt für welchen die Geodaten benötigt werden.

returns: Eine sortierte (nach Einwohner Anzahl) Liste mit 5 Ergebnissen (dictionaries) zum city_namen.
NOTE: Sollen wir hier schon vorfiltern, also nur notwendige Sachen weitergeben?
"""


def get_geocoding(city_name):
    headers = {
        "Content-Type": "application/json"
    }
    geocoding_api_endpoint = f"https://geocoding-api.open-meteo.com/v1/search?name={city_name}&count=5&language=en&format=json"
    response = requests.get(url=geocoding_api_endpoint, headers=headers)

    if response.status_code == 200:
        result = response.json()["results"]
        # die Liste wird noch anhand der Einwohneranzahl sortiert
        return sorted(result, key=lambda a: -a["population"] if ("population" in a) else 0)
    else:
        return Exception(response.status_code)


"""
requires:   latitude: vom Ort
            longitude: vom Ort
            start_date: Datum format %Y-%m-%d
            end_date: Datum format %Y-%m-%d

returns: Ein dictionary -> {
                            "DATUM1": {
                                        "weather_code":0-80,
                                        "temperature_max": Float Grad Celcius,
                                        "temperature_min": Float Grad Celcius,
                                        "apparent_temperature_max":Float Grad Celcius,
                                        "apparent_temperature_min":Float Grad Celcius,
                                        "uv_index" : Float,
                                        "precipitation_probability": Float für % Zahl (13.0%),
                                        "precipitation_sum": Float
                                    }
                            "DATUM2":...
}
"""


def get_weather(latitude, longitude, start_date, end_date):
    # Setup the Open-Meteo API client with cache and retry on error
    cache_session = requests_cache.CachedSession('.cache', expire_after=3600)
    retry_session = retry(cache_session, retries=5, backoff_factor=0.2)
    openmeteo = openmeteo_requests.Client(session=retry_session)

    url = "https://api.open-meteo.com/v1/forecast"
    params = {
        "latitude": latitude,
        "longitude": longitude,
        "daily": ["weather_code", "temperature_2m_max", "temperature_2m_min", "apparent_temperature_max",
                  "apparent_temperature_min", "sunrise", "sunset", "daylight_duration", "sunshine_duration",
                  "uv_index_max", "uv_index_clear_sky_max", "precipitation_sum", "rain_sum", "showers_sum",
                  "snowfall_sum", "precipitation_hours", "precipitation_probability_max", "wind_speed_10m_max",
                  "wind_gusts_10m_max", "wind_direction_10m_dominant", "shortwave_radiation_sum",
                  "et0_fao_evapotranspiration"],

        "start_date": start_date,
        "end_date": end_date
    }
    responses = openmeteo.weather_api(url, params=params)

    # Process first location. Add a for-loop for multiple locations or weather models
    # completly copied from the API Documentation
    response = responses[0]

    daily = response.Daily()
    daily_weather_code = daily.Variables(0).ValuesAsNumpy()
    daily_temperature_2m_max = daily.Variables(1).ValuesAsNumpy()
    daily_temperature_2m_min = daily.Variables(2).ValuesAsNumpy()
    daily_apparent_temperature_max = daily.Variables(3).ValuesAsNumpy()
    daily_apparent_temperature_min = daily.Variables(4).ValuesAsNumpy()
    daily_sunrise = daily.Variables(5).ValuesAsNumpy()
    daily_sunset = daily.Variables(6).ValuesAsNumpy()
    daily_daylight_duration = daily.Variables(7).ValuesAsNumpy()
    daily_sunshine_duration = daily.Variables(8).ValuesAsNumpy()
    daily_uv_index_max = daily.Variables(9).ValuesAsNumpy()
    daily_uv_index_clear_sky_max = daily.Variables(10).ValuesAsNumpy()
    daily_precipitation_sum = daily.Variables(11).ValuesAsNumpy()
    daily_rain_sum = daily.Variables(12).ValuesAsNumpy()
    daily_showers_sum = daily.Variables(13).ValuesAsNumpy()
    daily_snowfall_sum = daily.Variables(14).ValuesAsNumpy()
    daily_precipitation_hours = daily.Variables(15).ValuesAsNumpy()
    daily_precipitation_probability_max = daily.Variables(16).ValuesAsNumpy()
    daily_wind_speed_10m_max = daily.Variables(17).ValuesAsNumpy()
    daily_wind_gusts_10m_max = daily.Variables(18).ValuesAsNumpy()
    daily_wind_direction_10m_dominant = daily.Variables(19).ValuesAsNumpy()
    daily_shortwave_radiation_sum = daily.Variables(20).ValuesAsNumpy()
    daily_et0_fao_evapotranspiration = daily.Variables(21).ValuesAsNumpy()

    daily_data = {"date": pd.date_range(
        start=pd.to_datetime(daily.Time(), unit="s", utc=True),
        end=pd.to_datetime(daily.TimeEnd(), unit="s", utc=True),
        freq=pd.Timedelta(seconds=daily.Interval()),
        inclusive="left",
        unit="s"
    )}
    daily_data["weather_code"] = daily_weather_code
    daily_data["temperature_2m_max"] = daily_temperature_2m_max
    daily_data["temperature_2m_min"] = daily_temperature_2m_min
    daily_data["apparent_temperature_max"] = daily_apparent_temperature_max
    daily_data["apparent_temperature_min"] = daily_apparent_temperature_min
    daily_data["sunrise"] = daily_sunrise
    daily_data["sunset"] = daily_sunset
    daily_data["daylight_duration"] = daily_daylight_duration
    daily_data["sunshine_duration"] = daily_sunshine_duration
    daily_data["uv_index_max"] = daily_uv_index_max
    daily_data["uv_index_clear_sky_max"] = daily_uv_index_clear_sky_max
    daily_data["precipitation_sum"] = daily_precipitation_sum
    daily_data["rain_sum"] = daily_rain_sum
    daily_data["showers_sum"] = daily_showers_sum
    daily_data["snowfall_sum"] = daily_snowfall_sum
    daily_data["precipitation_hours"] = daily_precipitation_hours
    daily_data["precipitation_probability_max"] = daily_precipitation_probability_max
    daily_data["wind_speed_10m_max"] = daily_wind_speed_10m_max
    daily_data["wind_gusts_10m_max"] = daily_wind_gusts_10m_max
    daily_data["wind_direction_10m_dominant"] = daily_wind_direction_10m_dominant
    daily_data["shortwave_radiation_sum"] = daily_shortwave_radiation_sum
    daily_data["et0_fao_evapotranspiration"] = daily_et0_fao_evapotranspiration

    daily_dataframe = pd.DataFrame(data=daily_data)
    #until here copied

    #erstellen des return Dictionarys
    result_dict = {}
    #loop über alle Zeilen/Tage
    for index, row in daily_dataframe.iterrows():
        #Daten für jeden Tag in einem dictionary
        daily_json = {
            "weather_code": row["weather_code"],
            "temperature_max": row["temperature_2m_max"],
            "temperature_min": row["temperature_2m_min"],
            "apparent_temperature_max": row["apparent_temperature_max"],
            "apparent_temperature_min": row["apparent_temperature_min"],
            "uv_index": row["uv_index_max"],
            "precipitation_probability": row["precipitation_probability_max"],
            "precipitation_sum": row["precipitation_sum"]
        }
        #welches mit dem Datum als key dem return Dictionary hinzugefügt wird.
        result_dict[row["date"].strftime("%Y-%m-%d")] = daily_json

    return result_dict

#Zur veranschaulichung
#print(get_geocoding("Frankfurt"))
#print(get_weather(52.5244,13.4105,"2024-07-14","2024-07-15"))


###### TESTING #########
# pprint(get_geocoding("Frankfurt am Main"))
# city_geocoding = get_geocoding("Frankfurt am Main")
# latitude = city_geocoding[0]["latitude"]
# longitude = city_geocoding[0]["longitude"]
# start_date = "2024-07-16"
# end_date = "2024-07-16"
# weather_data = get_weather(latitude=latitude, longitude=longitude, start_date=start_date, end_date=end_date)
# pprint(weather_data)