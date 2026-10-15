"""Check days 31-40, map locations, photos and the cross-street index."""

import json
import math
import os
import re
import runpy
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
STREETS = [
    "Демократическая", "Георгия Димитрова", "Ташкентская",
    "Стара-Загора", "Советской Армии", "Гагарина", "Победы",
    "Авроры", "Осипенко", "Пушкина",
]


def distance_to_route(point, segments):
    latitude, longitude = point
    scale_x = 111_320 * math.cos(math.radians(latitude))
    scale_y = 111_320
    best = float("inf")
    for segment in segments:
        for a, b in zip(segment, segment[1:]):
            x1, y1 = (a[1] - longitude) * scale_x, (a[0] - latitude) * scale_y
            x2, y2 = (b[1] - longitude) * scale_x, (b[0] - latitude) * scale_y
            dx, dy = x2 - x1, y2 - y1
            portion = max(0, min(1, -(x1 * dx + y1 * dy) / (dx * dx + dy * dy))) if dx or dy else 0
            best = min(best, math.hypot(x1 + portion * dx, y1 + portion * dy))
    return best


def main():
    previous = Path.cwd()
    try:
        with tempfile.TemporaryDirectory() as directory:
            os.chdir(directory)
            state = runpy.run_path(str(ROOT / "map.py"))
            rendered = Path("samara_marathon_map.html").read_text(encoding="utf-8")
    finally:
        os.chdir(previous)

    assert len(state["street_layers"]) == 40
    assert len(list((ROOT / "streets").glob("День * - *.md"))) == 40
    assert len(state["places"]) > 0
    assert "overlayadd" in rendered and "fitBounds" in rendered
    for day, street in enumerate(STREETS, 31):
        path = ROOT / "streets" / f"День {day} - Улица {street}.md"
        article = path.read_text(encoding="utf-8")
        assert f"day: {day}" in article.split("---", 2)[1]
        assert f"street: {street}" in article.split("---", 2)[1]
        assert article.count("![") >= 3, path
        assert article.count("## ") >= 7, path
        assert "## Проверка памяти" in article, path
        for target in re.findall(r"\[\[([^|\]]+)", article):
            assert (ROOT / "streets" / f"{target}.md").exists(), (path, target)
        stops = [item for item in state["places"] if item.get("street") == street]
        assert len(stops) >= 2, (street, len(stops))
        for stop in stops:
            assert stop.get("coordinate_source"), (street, stop["name"])
            lat, lon = stop["coords"]
            assert 53.1 < lat < 53.4 and 50.0 < lon < 50.4, stop
        route = state["streets"][street]
        assert route["segments"] and route["highlight_weight"] <= 3, street
        for stop in stops:
            separation = distance_to_route(stop["coords"], route["segments"])
            assert separation < 750, (street, stop["name"], round(separation), "metres from route")

    graph = (ROOT / "История - все 40 улиц - Как город вырос и вернулся.md").read_text(encoding="utf-8")
    for day in range(1, 41):
        assert f"[[День {day} - Улица " in graph, day
    for target in re.findall(r"\[\[([^|\]]+)", graph):
        assert (ROOT / "streets" / f"{target}.md").exists(), target

    addresses = json.loads((ROOT / "data" / "decade_four_addresses.geojson").read_text(encoding="utf-8"))
    assert len(addresses["features"]) == 39
    routes = json.loads((ROOT / "data" / "decade_four_routes.geojson").read_text(encoding="utf-8"))
    assert len(routes["features"]) >= 100
    print("Validated 40 street layers, days 31-40, 39 OSM addresses and cross-street links")


if __name__ == "__main__":
    main()
