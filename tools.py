from datetime import date
import difflib
import json
import re
import requests
import unicodedata
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


# City-name normalization
#
# The airports.json keys come from the (very inconsistent) `municipality` column,
# so the same place shows up as "saint louis", "st louis", "st. lewis",
# "st ives, cambridgeshire", etc. We normalize both the stored keys and incoming
# queries to a shared canonical form so the variants collapse together.

# Whole-word abbreviation expansions, applied with word boundaries so we don't
# mangle substrings (e.g. "stockholm" must not become "saintockholm").
_ABBREVIATIONS = {
    r"\bste\.?\b": "sainte",
    r"\bst\.?\b": "saint",
    r"\bmt\.?\b": "mount",
    r"\bft\.?\b": "fort",
}


def normalize_city(name: str) -> str:
    if not name:
        return ""
    # lowercase + strip accents (e.g. "saint-léonard" -> "saint-leonard")
    text = unicodedata.normalize("NFKD", name).encode("ascii", "ignore").decode("ascii")
    text = text.lower().strip()
    # drop any trailing comma qualifier: "st ives, cambridgeshire" -> "st ives"
    text = text.split(",", 1)[0]
    # punctuation -> spaces so abbreviation boundaries are clean
    text = re.sub(r"[^a-z0-9]+", " ", text).strip()
    for pattern, replacement in _ABBREVIATIONS.items():
        text = re.sub(pattern, replacement, text)
    # collapse repeated whitespace introduced by the steps above
    text = re.sub(r"\s+", " ", text).strip()
    return text


# Normalized form -> list of original airports.json keys (a list because
# distinct originals can normalize to the same value, e.g. "st marys" and
# "st. mary's"; on a hit we merge their airport lists so no data is lost).
AIRPORTS_INDEX: dict[str, list[str]] = {}
for _original_key in AIRPORTS:
    AIRPORTS_INDEX.setdefault(normalize_city(_original_key), []).append(_original_key)

NORMALIZED_KEYS = list(AIRPORTS_INDEX)



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
def _merge_airports(original_keys):
    """Combine the airport lists of one or more original JSON keys into the
    standard {"airports": [...]} shape the rest of the app expects."""
    airports = []
    for key in original_keys:
        airports.extend(AIRPORTS[key]["airports"])
    return {"airports": airports}


def search_airports(city: str):
    print("INSIDE SEARCH AIRPORTS")
    norm = normalize_city(city)

    # 1. exact match on the normalized form
    if norm in AIRPORTS_INDEX:
        return _merge_airports(AIRPORTS_INDEX[norm])

    # 2. confident fuzzy match (typos, slight spelling differences)
    confident = difflib.get_close_matches(norm, NORMALIZED_KEYS, n=1, cutoff=0.8)
    if confident:
        return _merge_airports(AIRPORTS_INDEX[confident[0]])

    # 3. no confident match: return close suggestions instead of crashing so
    #    the model can ask the user to clarify which city they meant.
    near = difflib.get_close_matches(norm, NORMALIZED_KEYS, n=3, cutoff=0.6)
    suggestions = [AIRPORTS_INDEX[match][0] for match in near]
    return {"found": False, "query": city, "suggestions": suggestions}

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