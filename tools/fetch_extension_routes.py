"""Fetch named Samara street segments from Nominatim for days 21-30.

Run only when intentionally refreshing the checked-in OSM snapshot. Nominatim
requires a distinct User-Agent and no more than one request per second.
"""

import json
import time
from pathlib import Path
from urllib.parse import urlencode
from urllib.request import Request, urlopen


ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "data" / "extension_routes.geojson"
STREETS = {
    21: "Вилоновская",
    22: "Ульяновская",
    23: "Шостаковича",
    24: "Маяковского",
    25: "Чкалова",
    26: "Полевая",
    27: "Братьев Коростелёвых",
    28: "Арцыбушевская",
    29: "Буянова",
    30: "Ново-Садовая",
}


def fetch(street):
    query = {"q": f"улица {street}, Самара"} if street == "Братьев Коростелёвых" else {
        "street": street,
        "city": "Самара",
    }
    params = urlencode({**query, "format": "jsonv2", "polygon_geojson": 1, "dedupe": 0, "limit": 100})
    request = Request(
        f"https://nominatim.openstreetmap.org/search?{params}",
        headers={"User-Agent": "SamaraMarathonMap/1.0 (local cartographic research)"},
    )
    with urlopen(request, timeout=30) as response:
        return json.load(response)


def main():
    features = []
    for day, street in STREETS.items():
        results = fetch(street)
        accepted = 0
        for item in results:
            geometry = item.get("geojson") or {}
            expected_name = street.lower().replace("ё", "е")
            found_name = (item.get("name") or "").lower().replace("ё", "е")
            if found_name not in (f"улица {expected_name}", f"{expected_name} улица"):
                continue
            if item.get("osm_type") != "way" or geometry.get("type") != "LineString":
                continue
            if item.get("category") != "highway":
                continue
            if "Самара" not in item.get("display_name", ""):
                continue
            coordinates = geometry.get("coordinates") or []
            if len(coordinates) < 2:
                continue
            if not all(50.0 < lon < 50.4 and 53.1 < lat < 53.4 for lon, lat in coordinates):
                continue
            features.append(
                {
                    "type": "Feature",
                    "id": f"way/{item['osm_id']}",
                    "properties": {
                        "day": day,
                        "street": street,
                        "osm_id": item["osm_id"],
                        "name": item["name"],
                        "source": "OpenStreetMap via Nominatim",
                    },
                    "geometry": geometry,
                }
            )
            accepted += 1
        print(f"{day}: {street}: {accepted} road segments")
        if accepted == 0:
            raise RuntimeError(f"No OSM geometry for day {day}: {street}")
        time.sleep(1.1)

    OUTPUT.write_text(
        json.dumps(
            {
                "type": "FeatureCollection",
                "attribution": "© OpenStreetMap contributors",
                "license": "ODbL 1.0",
                "features": features,
            },
            ensure_ascii=False,
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )
    print(f"Saved {len(features)} segments to {OUTPUT}")


if __name__ == "__main__":
    main()
