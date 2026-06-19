from datetime import date
import json
import requests
from dotenv import load_dotenv
import os
from prompts import generate_analysis_prompt

# Initialization

load_dotenv(override=True)

ignav_api_key = os.getenv('IGNAV_API_KEY')

print(ignav_api_key)

with open("airports.json", "r", encoding="utf-8") as f:
    AIRPORTS = json.load(f)

print(AIRPORTS['london'])



def set_user_preferences(
    origin,
    destination,
    departure_date=None,
    return_date=None,
    trip_type=None,
    cabin=None,
    priority=None,
    budget=None,
    max_stops=None,
    checked_bag_required=None,
    flexible_dates=None,
    preferred_airlines=None,
    avoided_airlines=None,
    preferred_departure_time=None,
    preferred_arrival_time=None,
):
    print("INSIDE SET USER PREFERENCES")
    if departure_date is None:
        departure_date = date.today().isoformat()

    user_preferences = {
        "origin": origin,
        "destination": destination,
        "departure_date": departure_date,
    }

    optional_fields = {
        "return_date": return_date,
        "trip_type": trip_type,
        "cabin": cabin,
        "priority": priority,
        "budget": budget,
        "max_stops": max_stops,
        "checked_bag_required": checked_bag_required,
        "flexible_dates": flexible_dates,
        "preferred_airlines": preferred_airlines,
        "avoided_airlines": avoided_airlines,
        "preferred_departure_time": preferred_departure_time,
        "preferred_arrival_time": preferred_arrival_time,
    }

    for key, value in optional_fields.items():
        if value is not None:
            user_preferences[key] = value

    return user_preferences

# Search Airports
def search_airports(city: str):
    print("INSIDE SEARCH AIRPORTS")
    lower_city = city.lower()
    if lower_city == "saint petersburg":
        lower_city = "st. petersburg"
    return AIRPORTS[lower_city]

# Call API and return prompt with data (pass user preferences and path of parameters from LLM since they have access to it)
def get_flight_prices(origin_iata_code, destination_iata_code, departure_date: str, user_preferences, return_date=None, one_way=True):
    print("INSIDE GET FLIGHT PRICES")
    path = '/api/fares/round-trip'

    if one_way is True:
        path = '/api/fares/one-way'
    
    real_departure_date = departure_date.replace("2024", "2026")

    payload = {
        "origin": origin_iata_code,
        "destination": destination_iata_code,
        "departure_date": real_departure_date
    }

    headers = {
    "X-Api-Key": ignav_api_key,
    "Content-Type": "application/json"
    }

    if one_way is not True and return_date is not None:
        real_return_date = return_date.replace("2024", "2026")
        payload["return_date"] = real_return_date
    
    response = requests.post(
        f"https://ignav.com{path}",
        json=payload,
        headers=headers
    )
    
    if response.status_code is not 200:
        print(response.json())
        return "Unexpected Error Occured please wait a minute"
    
    flight_results = response.json()
    return generate_analysis_prompt(user_preferences, flight_results)