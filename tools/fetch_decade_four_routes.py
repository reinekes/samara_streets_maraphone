"""Refresh OSM street geometry for marathon days 31-40.

Run intentionally, not on every map build. Nominatim permits at most one
request per second; the resulting GeoJSON is the reproducible map snapshot.
"""

import json
import time
from pathlib import Path
from urllib.parse import urlencode
from urllib.request import Request, urlopen


ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "data" / "decade_four_routes.geojson"
STREETS = {
    31: "Демократическая",
    32: "Георгия Димитрова",
    33: "Ташкентская",
    34: "Стара-Загора",
    35: "Советской Армии",
    36: "Гагарина",
    37: "Победы",
    38: "Авроры",
    39: "Осипенко",
    40: "Пушкина",
}


def fetch(street):
    params = urlencode({
        "street": street,
        "city": "Самара",
        "format": "jsonv2",
        "polygon_geojson": 1,
        "dedupe": 0,
        "limit": 100,
    })
    request = Request(
        f"https://nominatim.openstreetmap.org/search?{params}",
        headers={"User-Agent": "SamaraMarathonMap/1.0 (local cartographic research)"},
    )
    with urlopen(request, timeout=45) as response:
        return json.load(response)


def main():
    features = []
    for day, street in STREETS.items():
        accepted = 0
        expected = street.lower().replace("ё", "е")
        for item in fetch(street):
            geometry = item.get("geojson") or {}
            found = (item.get("name") or "").lower().replace("ё", "е")
            if found not in (f"улица {expected}", f"{expected} улица"):
                continue
            if item.get("osm_type") != "way" or item.get("category") != "highway":
                continue
            if geometry.get("type") != "LineString":
                continue
            if "Самара" not in item.get("display_name", ""):
                continue
            coords = geometry.get("coordinates") or []
            if len(coords) < 2 or not all(
                50.0 < lon < 50.4 and 53.1 < lat < 53.4 for lon, lat in coords
            ):
                continue
            features.append({
                "type": "Feature",
                "id": f"way/{item['osm_id']}",
                "properties": {
                    "day": day,
                    "street": street,
                    "osm_id": item["osm_id"],
                    "source": "OpenStreetMap via Nominatim",
                },
                "geometry": geometry,
            })
            accepted += 1
        print(f"{day}: {street}: {accepted} OSM segments", flush=True)
        if not accepted:
            raise RuntimeError(f"No matching OSM line for {street}")
        time.sleep(1.1)

    OUTPUT.write_text(json.dumps({
        "type": "FeatureCollection",
        "attribution": "© OpenStreetMap contributors",
        "license": "ODbL 1.0",
        "features": features,
    }, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"Saved {len(features)} OSM segments to {OUTPUT}")


if __name__ == "__main__":
    main()
