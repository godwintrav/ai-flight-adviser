
set_user_preferences_function = {
    "name": "set_user_preferences",
    "description": """
Create or update traveler preferences gathered during the conversation.

This tool should be called whenever enough information has been collected about the user's travel plans.

Only 'origin' and 'destination' are required.

All other fields are optional because travelers often provide information gradually throughout the conversation.

Do not invent values for optional fields.
If the user has not specified them, omit them.

The returned preferences object will be used later by you when evaluating flight options, calling get_flight_prices function and making recommendations.
""",
    "parameters": {
        "type": "object",
        "properties": {
            "origin": {
                "type": "string",
                "description": "The city, airport name, or IATA airport code where the traveler is departing from. Example: 'Lagos', 'LOS', 'London Heathrow'."
            },
            "destination": {
                "type": "string",
                "description": "The city, airport name, or IATA airport code where the traveler wants to travel."
            },
            "departure_date": {
                "type": "string",
                "description": "Departure date in YYYY-MM-DD format. Optional because the user may not have chosen a date yet."
            },
            "return_date": {
                "type": "string",
                "description": "Return date in YYYY-MM-DD format. Only needed for round-trip journeys."
            },
            "trip_type": {
                "type": "string",
                "enum": ["one_way", "round_trip"],
                "description": "Type of trip. Optional because it can often be inferred from whether a return date exists."
            },
            "cabin": {
                "type": "string",
                "enum": ["economy", "premium_economy", "business", "first"],
                "description": "Preferred cabin class."
            },
            "priority": {
                "type": "string",
                "enum": [
                    "cheapest",
                    "fastest",
                    "best_value",
                    "flexible",
                    "eco_friendly"
                ],
                "description": "Traveler's primary goal when choosing flights."
            },
            "budget": {
                "type": "number",
                "description": "Maximum budget for the flight in the user's preferred currency."
            },
            "max_stops": {
                "type": "integer",
                "description": "Maximum acceptable number of stops or layovers."
            },
            "checked_bag_required": {
                "type": "boolean",
                "description": "Whether the traveler requires checked baggage."
            },
            "flexible_dates": {
                "type": "boolean",
                "description": "Whether nearby travel dates may be searched to find cheaper fares."
            },
            "preferred_airlines": {
                "type": "array",
                "items": {
                    "type": "string"
                },
                "description": "List of airlines the traveler prefers."
            },
            "avoided_airlines": {
                "type": "array",
                "items": {
                    "type": "string"
                },
                "description": "List of airlines the traveler wishes to avoid."
            },
            "preferred_departure_time": {
                "type": "string",
                "enum": [
                    "morning",
                    "afternoon",
                    "evening",
                    "night"
                ],
                "description": "Preferred departure time window."
            },
            "preferred_arrival_time": {
                "type": "string",
                "enum": [
                    "morning",
                    "afternoon",
                    "evening",
                    "night"
                ],
                "description": "Preferred arrival time window."
            }
        },
        "required": ["origin", "destination"],
        "additionalProperties": False
    }
}


search_airports_function = {
    "name": "search_airports",
    "description": """
Find airports serving a city.

Use this tool whenever the traveler mentions a city instead of an airport code.

The tool returns airport information including IATA codes.

Examples:

- 'Lagos' -> LOS
- 'Abuja' -> ABV
- 'London' -> LHR, LGW, LCY, STN, LTN

Call this tool before searching for flights if airport codes are unknown.
""",
    "parameters": {
        "type": "object",
        "properties": {
            "city": {
                "type": "string",
                "description": "City name supplied by the traveler."
            }
        },
        "required": ["city"],
        "additionalProperties": False
    }
}



get_flight_prices_function = {
    "name": "get_flight_prices",
    "description": """
Search for flight fares between two airports and return flight recommendations.

Before calling this tool:

1. Determine the departure airport.
2. Determine the destination airport.
3. Determine the departure date.
4. Collect any traveler preferences mentioned during the conversation.

IMPORTANT:

Always populate the user_preferences object using information already provided by the traveler.

If a preference has not been mentioned, omit it from the object rather than inventing a value.

The user_preferences object is used later to evaluate flight options and generate personalized recommendations.

Use airport IATA codes rather than city names.

Examples:

Correct:
origin_iata_code = "LOS"
destination_iata_code = "LHR"

Incorrect:
origin_iata_code = "Lagos"
destination_iata_code = "London"

Use search_airports first if airport codes are unknown.

For round trips:
- Set one_way to false
- Provide return_date

For one-way trips:
- Set one_way to true
- Omit return_date

This tool returns flight data that will be analyzed based on the supplied user preferences.
""",
    "parameters": {
        "type": "object",
        "properties": {
            "origin_iata_code": {
                "type": "string",
                "description": "Three-letter IATA airport code for the departure airport. Example: LOS, LHR, JFK."
            },
            "destination_iata_code": {
                "type": "string",
                "description": "Three-letter IATA airport code for the destination airport."
            },
            "departure_date": {
                "type": "string",
                "description": "Departure date in YYYY-MM-DD format."
            },
            "return_date": {
                "type": "string",
                "description": "Return date in YYYY-MM-DD format. Only required for round-trip searches."
            },
            "one_way": {
                "type": "boolean",
                "description": "Whether this is a one-way journey. Set to false when a return date exists."
            },
            "user_preferences": {
                "type": "object",
                "description": """
Traveler preferences extracted from the conversation and also was returned from the set_user_preferences tool specifically.

Populate this object using all known information gathered so far.

Do not invent values.

Only include fields that the traveler has explicitly provided or strongly implied.

This object will later be used to rank and recommend flights.
""",
                "properties": {
                    "origin": {
                        "type": "string",
                        "description": "Original city, airport, or location mentioned by the traveler."
                    },
                    "destination": {
                        "type": "string",
                        "description": "Original destination city, airport, or location mentioned by the traveler."
                    },
                    "departure_date": {
                        "type": "string"
                    },
                    "return_date": {
                        "type": "string"
                    },
                    "trip_type": {
                        "type": "string",
                        "enum": ["one_way", "round_trip"]
                    },
                    "cabin": {
                        "type": "string",
                        "enum": [
                            "economy",
                            "premium_economy",
                            "business",
                            "first"
                        ]
                    },
                    "priority": {
                        "type": "string",
                        "enum": [
                            "cheapest",
                            "fastest",
                            "best_value",
                            "flexible",
                            "eco_friendly"
                        ]
                    },
                    "budget": {
                        "type": "number"
                    },
                    "max_stops": {
                        "type": "integer"
                    },
                    "checked_bag_required": {
                        "type": "boolean"
                    },
                    "flexible_dates": {
                        "type": "boolean"
                    },
                    "preferred_airlines": {
                        "type": "array",
                        "items": {
                            "type": "string"
                        }
                    },
                    "avoided_airlines": {
                        "type": "array",
                        "items": {
                            "type": "string"
                        }
                    },
                    "preferred_departure_time": {
                        "type": "string",
                        "enum": [
                            "morning",
                            "afternoon",
                            "evening",
                            "night"
                        ]
                    },
                    "preferred_arrival_time": {
                        "type": "string",
                        "enum": [
                            "morning",
                            "afternoon",
                            "evening",
                            "night"
                        ]
                    }
                },
                "additionalProperties": False
            }
        },
        "required": [
            "origin_iata_code",
            "destination_iata_code",
            "departure_date",
            "user_preferences"
        ],
        "additionalProperties": False
    }
}

tools = [{"type": "function", "function": set_user_preferences_function}, 
         {"type": "function", "function": search_airports_function},
         {"type": "function", "function": get_flight_prices_function}
        ]