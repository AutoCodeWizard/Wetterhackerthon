import requests
import json
import os
from pprint import pprint


class GooglePlacesAPI:
    def __init__(self):
        # Parameter (vorläufig) + API Endpunkt werden gesetzt
        self.places_api_endpoint = "https://places.googleapis.com/v1/places:searchNearby"
        self.maxResultCount = 10
        self.radius = 10000
        self.latitude = "50.1109"
        self.longitude = "8.6821"
        # Field Mask sagt aus, welche Informationen von der API benötigt werden
        self.field_mask = ("places.displayName,"
                           "places.formattedAddress,"
                           "places.accessibilityOptions,"
                           "places.businessStatus,"
                           "places.primaryTypeDisplayName,"
                           "places.attributions,"
                           "places.googleMapsUri,"
                           "places.id,"
                           "places.location,"
                           "places.photos,"
                           "places.primaryType")

        # Parameter ob Sachen Outdoor sind oder nicht -> Werden mit Wetter abgeglichen
        self.yes_outdoor = ["amusement_center", "amusement_park", "hiking_area", "historical_landmark", "marina",
                            "national_park", "park", "tourist_attraction", "zoo", "swimming_pool"]
        self.no_outdoor = ["art_gallery", "museum", "performing_arts_theater", "aquarium", "banquet_hall",
                           "bowling_alley", "cultural_center", "movie_theater"]

    def get_places(self, latitude, longitude, outdoor, radius, max_result_count, date):

        if outdoor:
            included_types = self.yes_outdoor
            excluded_types = self.no_outdoor
        else:
            included_types = self.no_outdoor
            excluded_types = self.yes_outdoor

        # Holt GooglePlacesAPIKey als Env Variable
        google_places_api_key = os.environ.get('GooglePlacesAPIKey')
        # print(f"Google Places API Key: {google_places_api_key}")

        # API Header für Authentication und FieldMask
        headers = {
            "Content-Type": "application/json",
            "X-Goog-Api-Key": google_places_api_key,
            "X-Goog-FieldMask": self.field_mask
            # "X-Goog-FieldMask": "places.displayName"
        }
        # Parameter für API Call; u.a. Standort, Radius und welche Attraktionen,
        # wird nach Popularität ausgegeben NICHT nach Distanz
        data = {
            "includedTypes": included_types,
            "excludedTypes": excluded_types,
            "maxResultCount": max_result_count,
            "locationRestriction": {
                "circle": {
                    "center": {
                        "latitude": latitude,
                        "longitude": longitude
                    },
                    "radius": radius
                }
            },
            "rankPreference": "Popularity"
        }

        # API Call
        response = requests.post(url=self.places_api_endpoint, headers=headers, json=data)
        # Gibt API Response Code aus; für debugging
        print(response.status_code)
        # Wenn erfolgreich -> Output wird in JSON File geschrieben und formatiert
        if response.status_code == 200:
            # with open("testoutput.json", "w") as file:
            #     response_json = response.json()
            #     json.dump(response_json, file, indent=2)
            #     print("exported response")
            pprint(response.status_code)
            jsonresponse = response.json()

            for i in jsonresponse:
                output = {date: jsonresponse[i]}

            return output

        else:
            return response.status_code


# Funktion wird zum Testen gecallt
# places = GooglePlacesAPI()
# places.get_places()

# PARAMETER VON LINUS

# Wetter bis 14 Tage im Voraus
# Nötige Informationen für PlacesAPI:

# Standort Koordinaten (str)
# Standort Name ausgeschrieben (str)
# Datum (str)
# Wochentag (str)
# Suchradius (int) in Meter
# Anzahl Aktivitäten
# Anzahl Restaurants

# Wetterinformationen auswerten für die gesamte Zeitspanne
#   z.B. wenn Temperatur >20 °C und trocken -> outdoor = true
#   wenn Regen oder Schnee ist halt immer -> outdoor = false

# weather_data = {
#     "location": {
#         "coordinates": {
#             "latitude": "XXXX",
#             "longitude": "XXXX",
#             },
#         "location_name": "XXXX",
#     },
#     "date": "XXXX",
#     "weekday": "XXXX",
#     "search_radius": 10000,
#     "total_activities": 2,
#     "total_restaurants": 1,
#     "weather": {
#         "XXXX"  # Format kannst du dir hier aussuchen
#     }
#
# }
