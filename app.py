import streamlit as st
from weather import get_geocoding, get_weather
from googleplaces import GooglePlacesAPI
from pprint import pprint
import json

is_running = True
places = GooglePlacesAPI()

while is_running:
    city_name = str(input("Wohin soll es gehen?: "))
    city_geocoding = get_geocoding(city_name=city_name)
    latitude = city_geocoding[0]["latitude"]
    longitude = city_geocoding[0]["longitude"]
    start_date = str(input("Wann soll die Reise starten? Format YYYY-MM-DD: "))
    end_date = str(input("Wann soll die Reise enden? Format YYYY-MM-DD: "))
    weather_data = get_weather(latitude=latitude,
                               longitude=longitude,
                               start_date=start_date,
                               end_date=end_date)

    activities = []
    activity_names = []
    skipped = 0

    for date, day_data in weather_data.items():

        if day_data["weather_code"] <= 3:
            outdoor = True

        else:
            outdoor = False

        daily_activities = places.get_places(latitude=latitude,
                                             longitude=longitude,
                                             outdoor=outdoor,
                                             radius=10000,
                                             max_result_count=10,
                                             date=date)

        activities.append(daily_activities)

    with open("test.json", "w") as file:
        json.dump(activities, file, indent=2)

    is_running = False

############ TRASH CODE ################


# for activity in daily_activities[date]:
#     print(activity["displayName"]["text"])
#     if activity["displayName"]["text"] in activity_names:
#         skipped += 1
#
#     activities.append(daily_activities)
#     activity_names += activity["displayName"]["text"]


# with open("weatherdata.json", "w") as file:
#     json.dump(weather_data, file, indent=2)
#     print("exported weatherdata into file")

# for date, day_data in weather_data.items():
#     if day_data["weather_code"] <= 3:
#         outdoor = True
#     else:
#         outdoor = False

# for date, day_data in weather_data.items():
#     if day_data["weather_code"] <= 3:
#         outdoor = True
#         daily_activities = places.get_places(latitude=latitude,
#                           longitude=longitude,
#                           outdoor=outdoor,
#                           radius=10000,
#                           max_result_count=10)
#
#         with open(f"activities_{date}.json", "w") as file:
#             json.dump(daily_activities, file, indent=2)
#             print(f"exported daily activities for {date}")
#
#     else:
#         outdoor = False
#         daily_activities = places.get_places(latitude=latitude,
#                           longitude=longitude,
#                           outdoor=outdoor,
#                           radius=10000,
#                           max_result_count=10)
#
#         with open(f"activities_{date}.json", "w") as file:
#             json.dump(daily_activities, file, indent=2)
#             print(f"exported daily activities for {date}")


#     for i in range(len(daily_activities["places"])):
#
#         name = daily_activities["places"][i]["displayName"]["text"]
#         formatted_address = daily_activities["places"][i]["formattedAddress"]
#         primary_type = daily_activities["places"][i]["primaryType"]
#         photos = daily_activities["places"][i]["photos"]
#         accessibility_options = daily_activities["places"][i]["accessibilityOptions"]
#
#         activity = {
#             name: {
#                 "formattedAddress": formatted_address,
#                 "primaryType": primary_type,
#                 "photos": photos,
#                 "accessibilityOptions": accessibility_options
#             }
#         }
#
#         for activity in activities:
#             if activity[name] in activities:
#                 skipped += 1
#
#         else:
#             activities.append(activity)
#
# with open("all_activities.json", "w") as file:
#     json.dump(activities, file, indent=2)
#     print("DONE!")
#     print(f"SKIPPED ACTIVITIES: {skipped}")
