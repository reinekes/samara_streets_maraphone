"""Resolve selected day 21-30 article addresses against OSM Nominatim.

Only exact Samara street/house matches enter the checked-in snapshot. Keep at
least one second between requests as required by Nominatim's usage policy.
"""

import json
import time
from pathlib import Path
from urllib.parse import urlencode
from urllib.request import Request, urlopen


ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "data" / "extension_addresses.geojson"
ADDRESSES = {
    "Вилоновская": ["2а", "19", "106"],
    "Ульяновская": ["2", "1", "18"],
    "Маяковского": ["2", "15", "19", "32", "37", "42"],
    "Чкалова": ["84", "91", "98"],
    "Полевая": ["43", "50"],
    "Братьев Коростелёвых": ["17", "47", "104", "146"],
    "Ново-Садовая": ["3", "8", "22", "30", "42", "106г"],
}


def fetch(street, number):
    params = urlencode({
        "q": f"Самара, улица {street}, {number}",
        "format": "jsonv2",
        "addressdetails": 1,
        "limit": 10,
        "viewbox": "50.03,53.28,50.25,53.15",
        "bounded": 1,
    })
    request = Request(
        f"https://nominatim.openstreetmap.org/search?{params}",
        headers={"User-Agent": "SamaraMarathonMap/1.0 (local cartographic research)"},
    )
    with urlopen(request, timeout=30) as response:
        return json.load(response)


def main():
    features = []
    for street, numbers in ADDRESSES.items():
        for number in numbers:
            result = next((item for item in fetch(street, number)
                           if item.get("address", {}).get("house_number", "").lower() == number.lower()
                           and street.lower().replace("ё", "е") in item.get("display_name", "").lower().replace("ё", "е")
                           and "Самара" in item.get("display_name", "")
                           and 53.15 < float(item["lat"]) < 53.28
                           and 50.03 < float(item["lon"]) < 50.25), None)
            if result:
                features.append({
                    "type": "Feature",
                    "properties": {
                        "street": street,
                        "number": number,
                        "display_name": result["display_name"],
                        "osm_type": result.get("osm_type"),
                        "osm_id": result.get("osm_id"),
                        "source": "OpenStreetMap via Nominatim",
                    },
                    "geometry": {"type": "Point", "coordinates": [float(result["lon"]), float(result["lat"])]},
                })
                print(f"{street}, {number}: {result['lat']}, {result['lon']}")
            else:
                print(f"{street}, {number}: no exact OSM address")
            time.sleep(1.1)

    OUTPUT.write_text(json.dumps({"type": "FeatureCollection", "features": features},
                                 ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"Saved {len(features)} verified addresses to {OUTPUT}")


if __name__ == "__main__":
    main()
