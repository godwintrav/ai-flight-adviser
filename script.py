import json
import math

import pandas as pd

df = pd.read_csv("airports.csv")

# Only keep airports with an IATA code and a municipality
df = df[
    df["iata_code"].notna()
    & df["municipality"].notna()
]


def clean_nans(obj):
    """Recursively replace NaN with None."""
    if isinstance(obj, dict):
        return {
            key: clean_nans(value)
            for key, value in obj.items()
        }

    if isinstance(obj, list):
        return [clean_nans(item) for item in obj]

    if isinstance(obj, float) and math.isnan(obj):
        return None

    return obj


cities = {}

for airport in df.to_dict(orient="records"):
    airport = clean_nans(airport)

    city = airport["municipality"].strip().lower()

    if city not in cities:
        cities[city] = {
            "airports": []
        }

    cities[city]["airports"].append(airport)

with open("airports.json", "w", encoding="utf-8") as f:
    json.dump(
        cities,
        f,
        indent=2,
        ensure_ascii=False,
        allow_nan=False
    )