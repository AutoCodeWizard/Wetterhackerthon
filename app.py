import streamlit as st
from weather import get_geocoding, get_weather
from googleplaces import GooglePlacesAPI
from pprint import pprint
import json

is_running = True
places = GooglePlacesAPI()

while is_running:

    # INPUT Funktion für Städtename
    city_name = str(input("Wohin soll es gehen?: "))

    # GEOLOCATION wird mithilfe von Städtename geholt
    city_geocoding = get_geocoding(city_name=city_name)

    # Koordinaten werden ausgelesen und Start- und Enddatum durch Input geholt
    latitude = city_geocoding[0]["latitude"]
    longitude = city_geocoding[0]["longitude"]
    start_date = str(input("Wann soll die Reise starten? Format YYYY-MM-DD: "))
    end_date = str(input("Wann soll die Reise enden? Format YYYY-MM-DD: "))

    # Wetter Daten werden geholt mit Koordinaten sowie Datum
    weather_data = get_weather(latitude=latitude,
                               longitude=longitude,
                               start_date=start_date,
                               end_date=end_date)

    # Leere Liste für Aktivitäten wird erstellt
    activities = []

    # Loop durch Tage in Wetterdaten
    for date, day_data in weather_data.items():

        # Wenn schönes Wetter ist, ist outdoor = True (beeinflusst Art von Aktivitäten, die ausgegeben werden)
        if day_data["weather_code"] <= 3:
            outdoor = True

        # Wenn schlechtes Wetter ist, ist outdoor = False
        else:
            outdoor = False

        # Aktivitäten für die jeweiligen Tage werden eingeholt und in die Liste 'activities' gepackt
        daily_activities = places.get_places(latitude=latitude,
                                             longitude=longitude,
                                             outdoor=outdoor,
                                             radius=10000,
                                             max_result_count=10,
                                             date=date)

        activities.append(daily_activities)

    # Aktivitäten kommen in eine JSON Datei
    with open("test.json", "w") as file:
        json.dump(activities, file, indent=2)

    # Ende des Programms
    is_running = False