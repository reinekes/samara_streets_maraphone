"""Geocode verified article addresses for days 31-40 with Nominatim."""

import json
import time
from pathlib import Path
from urllib.parse import urlencode
from urllib.request import Request, urlopen


ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "data" / "decade_four_addresses.geojson"
ADDRESSES = {
    "Демократическая": ["43", "57", "75"],
    "Георгия Димитрова": ["3", "20", "36", "44"],
    "Ташкентская": ["92", "100", "137", "139"],
    "Стара-Загора": ["58", "96а", "143", "202ж"],
    "Советской Армии": ["2", "5", "29", "283", "285"],
    "Гагарина": ["54", "109", "124", "171"],
    "Победы": ["92", "125", "149", "151"],
    "Авроры": ["110", "150", "154", "201", "207"],
    "Осипенко": ["10а", "12", "32", "34"],
    "Пушкина": ["181", "225", "248", "284"],
}


def fetch(street, number):
    params = urlencode({
        "q": f"Самара, улица {street}, {number}",
        "format": "jsonv2",
        "addressdetails": 1,
        "limit": 10,
        "viewbox": "50.0,53.4,50.4,53.1",
        "bounded": 1,
    })
    request = Request(
        f"https://nominatim.openstreetmap.org/search?{params}",
        headers={"User-Agent": "SamaraMarathonMap/1.0 (local cartographic research)"},
    )
    with urlopen(request, timeout=45) as response:
        return json.load(response)


def main():
    features = []
    for street, numbers in ADDRESSES.items():
        expected = street.lower().replace("ё", "е")
        for number in numbers:
            item = next((candidate for candidate in fetch(street, number)
                         if candidate.get("address", {}).get("house_number", "").lower() == number.lower()
                         and expected in candidate.get("display_name", "").lower().replace("ё", "е")
                         and "Самара" in candidate.get("display_name", "")
                         and 53.1 < float(candidate["lat"]) < 53.4
                         and 50.0 < float(candidate["lon"]) < 50.4), None)
            if item:
                features.append({
                    "type": "Feature",
                    "properties": {
                        "street": street,
                        "number": number,
                        "display_name": item["display_name"],
                        "osm_type": item.get("osm_type"),
                        "osm_id": item.get("osm_id"),
                        "source": "OpenStreetMap via Nominatim",
                    },
                    "geometry": {"type": "Point", "coordinates": [float(item["lon"]), float(item["lat"])]},
                })
                print(f"{street}, {number}: {item['lat']}, {item['lon']}", flush=True)
            else:
                print(f"{street}, {number}: no exact address", flush=True)
            time.sleep(1.1)
    OUTPUT.write_text(json.dumps({
        "type": "FeatureCollection", "attribution": "© OpenStreetMap contributors",
        "license": "ODbL 1.0", "features": features,
    }, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"Saved {len(features)} verified address points to {OUTPUT}")


if __name__ == "__main__":
    main()
