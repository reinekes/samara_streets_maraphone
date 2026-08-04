from pathlib import Path
import ast
import math


ROOT = Path(__file__).resolve().parents[1]
STREET_MD = ROOT / "streets" / "01-kuibysheva.md"
FRUNZE_MD = ROOT / "streets" / "02-frunze.md"
MAP_PY = ROOT / "map.py"
MAP_HTML = ROOT / "samara_marathon_map.html"


def require(condition, message):
    if not condition:
        raise AssertionError(message)


def load_streets():
    tree = ast.parse(MAP_PY.read_text(encoding="utf-8"))
    for node in tree.body:
        if isinstance(node, ast.Assign):
            for target in node.targets:
                if isinstance(target, ast.Name) and target.id == "streets":
                    return ast.literal_eval(node.value)
    raise AssertionError("streets dictionary is missing in map.py")


def meters_between(a, b):
    lat1, lon1 = map(math.radians, a)
    lat2, lon2 = map(math.radians, b)
    dlat = lat2 - lat1
    dlon = lon2 - lon1
    hav = math.sin(dlat / 2) ** 2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon / 2) ** 2
    return 6371000 * 2 * math.atan2(math.sqrt(hav), math.sqrt(1 - hav))


def main():
    require(STREET_MD.exists(), "streets/01-kuibysheva.md is missing")
    text = STREET_MD.read_text(encoding="utf-8")
    char_count = len(text)

    require("date: 04" in text, "dataview date field is missing")
    require("month: 08" in text, "dataview month field is missing")
    require("year: 2026" in text, "dataview year field is missing")
    require(9500 <= char_count <= 15000, f"md length is {char_count}, expected 9500-15000")
    require("1586" in text, "published md should include Samara foundation prehistory")
    require("1782" in text, "published md should include the first regular city plan")
    require("1804" in text, "published md should include the early regular-plan expansion")
    require("1839" in text, "published md should connect early plans to the street grid")
    for required_fact in ("6000", "900", "61,2", "70,4", "246,4", "15 000", "89 999"):
        require(required_fact in text, f"published md should include numeric fact: {required_fact}")
    require("## Точки маршрута" not in text, "published md should not contain route point metadata")
    require("## Источники" in text, "sources section is missing")
    require("lat:" not in text, "published md should not contain latitude metadata")
    require("lon:" not in text, "published md should not contain longitude metadata")
    require("address:" not in text, "published md should not contain address metadata blocks")
    require("description:" not in text, "published md should not contain description metadata blocks")

    map_source = MAP_PY.read_text(encoding="utf-8")
    html_source = MAP_HTML.read_text(encoding="utf-8")
    streets = load_streets()
    kuibysheva_coords = streets["Куйбышева"]["coords"]

    require('"Куйбышева"' in map_source, "Kuybysheva street data is missing in map.py")
    require("#e74c3c" in map_source, "Kuybysheva highlight color is missing")
    require("highlight_weight" in map_source, "street corridor highlight is missing")
    require(len(kuibysheva_coords) >= 50, "Kuybysheva route should use detailed OSM street geometry")
    longest_segment = max(
        meters_between(kuibysheva_coords[i], kuibysheva_coords[i + 1])
        for i in range(len(kuibysheva_coords) - 1)
    )
    require(longest_segment < 260, f"Kuybysheva line has a {longest_segment:.1f}m shortcut segment")
    for expected in ([53.1809887, 50.0846502], [53.1831783, 50.0860755], [53.1861322, 50.0879869]):
        require(expected in kuibysheva_coords, f"OSM street-axis point {expected} is missing")
    require("Бристоль-Жигули" in map_source, "Bristol-Zhiguli marker is missing")
    require("Крестьянский и Дворянский поземельные банки" in map_source, "land banks marker is missing")
    require("Улица Куйбышева" in html_source, "generated map does not contain Kuybysheva tooltip")

    require(FRUNZE_MD.exists(), "streets/02-frunze.md is missing")
    frunze_text = FRUNZE_MD.read_text(encoding="utf-8")
    frunze_count = len(frunze_text)
    require("date: 04" in frunze_text, "Frunze dataview date field is missing")
    require("month: 08" in frunze_text, "Frunze dataview month field is missing")
    require("year: 2026" in frunze_text, "Frunze dataview year field is missing")
    require(9500 <= frunze_count <= 15000, f"Frunze md length is {frunze_count}, expected 9500-15000")
    require("## Источники" in frunze_text, "Frunze sources section is missing")
    require("lat:" not in frunze_text, "Frunze published md should not contain latitude metadata")
    require("lon:" not in frunze_text, "Frunze published md should not contain longitude metadata")
    for required_fact in ("2,4", "16 декабря 1925", "1853", "1915", "1902-1906", "47", "37", "1907", "1100", "1934"):
        require(required_fact in frunze_text, f"Frunze md should include numeric fact: {required_fact}")

    require('"Фрунзе"' in map_source, "Frunze street data is missing in map.py")
    frunze_coords = streets["Фрунзе"]["coords"]
    require(len(frunze_coords) >= 45, "Frunze route should use detailed OSM street geometry")
    frunze_longest_segment = max(
        meters_between(frunze_coords[i], frunze_coords[i + 1])
        for i in range(len(frunze_coords) - 1)
    )
    require(frunze_longest_segment < 260, f"Frunze line has a {frunze_longest_segment:.1f}m shortcut segment")
    for marker_name in ("Музей модерна", "Костел Пресвятого Сердца Иисуса", "Бункер И. В. Сталина", "Дом-музей М. В. Фрунзе"):
        require(marker_name in map_source, f"Frunze marker is missing: {marker_name}")
    require("Улица Фрунзе" in html_source, "generated map does not contain Frunze tooltip")

    print(f"validated {STREET_MD.relative_to(ROOT)} ({char_count} chars)")


if __name__ == "__main__":
    main()
