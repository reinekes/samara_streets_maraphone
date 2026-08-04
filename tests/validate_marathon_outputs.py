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


def load_literal_assignment(name):
    tree = ast.parse(MAP_PY.read_text(encoding="utf-8"))
    for node in tree.body:
        if isinstance(node, ast.Assign):
            for target in node.targets:
                if isinstance(target, ast.Name) and target.id == name:
                    return ast.literal_eval(node.value)
    raise AssertionError(f"{name} assignment is missing in map.py")


def load_streets():
    return load_literal_assignment("streets")


def load_places():
    return load_literal_assignment("places")


def body_after_frontmatter(text):
    parts = text.split("---", 2)
    require(len(parts) == 3, "markdown frontmatter block is missing")
    return parts[2].lstrip()


def require_name_history_table(text, rows, street_label):
    body = body_after_frontmatter(text)
    require(body.startswith("| Период | Название |"), f"{street_label} name-history table should follow dataview block")
    require("|---|---|" in body[:120], f"{street_label} name-history table separator is missing")
    for period, name in rows:
        row = f"| {period} | {name} |"
        require(row in body, f"{street_label} name-history row is missing: {row}")


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
    require_name_history_table(
        text,
        [
            ("1810-е", "Казачья"),
            ("1840-е - 1860-е", "Хлебная"),
            ("1860-е - 1917", "Дворянская"),
            ("1917", "Керенского"),
            ("1918 - 28 февраля 1935", "Советская"),
            ("с 28 февраля 1935", "Куйбышева"),
        ],
        "Kuybysheva",
    )
    require(9500 <= char_count <= 34000, f"md length is {char_count}, expected 9500-34000")
    require("1586" in text, "published md should include Samara foundation prehistory")
    require("1782" in text, "published md should include the first regular city plan")
    require("1804" in text, "published md should include the early regular-plan expansion")
    require("1839" in text, "published md should connect early plans to the street grid")
    for required_fact in ("6000", "900", "61,2", "70,4", "246,4", "15 000", "89 999"):
        require(required_fact in text, f"published md should include numeric fact: {required_fact}")
    for new_fact in ("Музей истории войск", "15 апреля 1975", "1913", "Д. А. Вернера", "площадь Революции", "Алексеевская", "1889", "7 ноября 1927"):
        require(new_fact in text, f"Kuybysheva md should include added museum/square fact: {new_fact}")
    require("## Точки маршрута" not in text, "published md should not contain route point metadata")
    require("## Источники" in text, "sources section is missing")
    require("lat:" not in text, "published md should not contain latitude metadata")
    require("lon:" not in text, "published md should not contain longitude metadata")
    require("address:" not in text, "published md should not contain address metadata blocks")
    require("description:" not in text, "published md should not contain description metadata blocks")
    require(text.count("![") >= 14, "Kuybysheva md should include at least fourteen publication images")
    require(text.count("commons.wikimedia.org/wiki/Special:FilePath/") >= 14, "Kuybysheva images should use Wikimedia Commons file paths")
    require(text.count("Источник изображения:") >= 14, "Kuybysheva images should have visible source captions")
    for image_label in (
        "План Самары 1782",
        "План Самары 1839",
        "План Самары 1903",
        "Дворянская улица",
        "Алексеевская площадь",
        "Конка на Панской",
        "Русский торгово-промышленный банк",
        "Самарский областной художественный музей",
        "Кирха Святого Георга",
        "Бристоль-Жигули",
        "площадь Революции",
        "Особняк Клодта",
        "Особняк Наумова",
        "Крестьянский и Дворянский поземельные банки",
    ):
        require(image_label in text, f"Kuybysheva md should include image/caption for: {image_label}")

    map_source = MAP_PY.read_text(encoding="utf-8")
    html_source = MAP_HTML.read_text(encoding="utf-8")
    streets = load_streets()
    places = load_places()
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
    for marker_name in ("Музей истории войск ПриВО", "Площадь Революции"):
        require(marker_name in map_source, f"Kuybysheva marker is missing: {marker_name}")
    require("Улица Куйбышева" in html_source, "generated map does not contain Kuybysheva tooltip")
    require("<b>Адрес:</b>" in html_source, "generated map popups should show address on a separate line")
    require("<b>Стиль:</b>" in html_source, "generated map popups should show style on a separate line")
    require("<b>Даты:</b>" in html_source, "generated map popups should show dates on a separate line")
    require("<b>Факты:</b>" in html_source, "generated map popups should show facts on a separate line")
    require("line-height: 1.35" in html_source, "generated map popups should use readable multi-line formatting")
    kuibysheva_image_places = [
        place for place in places
        if place.get("color") == "red" and place.get("image_url")
    ]
    require(len(kuibysheva_image_places) >= 7, "Kuybysheva map should include thumbnails for at least seven red markers")
    for thumbnail_caption in ("Бристоль-Жигули", "Кирха Святого Георга", "Самарский художественный музей", "Особняк Клодта", "Особняк Наумова", "Поземельные банки", "Площадь Революции"):
        require(thumbnail_caption in html_source, f"Kuybysheva generated map should include thumbnail caption: {thumbnail_caption}")

    require(FRUNZE_MD.exists(), "streets/02-frunze.md is missing")
    frunze_text = FRUNZE_MD.read_text(encoding="utf-8")
    frunze_count = len(frunze_text)
    require("date: 04" in frunze_text, "Frunze dataview date field is missing")
    require("month: 08" in frunze_text, "Frunze dataview month field is missing")
    require("year: 2026" in frunze_text, "Frunze dataview year field is missing")
    require_name_history_table(
        frunze_text,
        [
            ("XVIII век", "Николаевская / Симбирская"),
            ("1853 - 1915", "Саратовская"),
            ("1915 - 16 декабря 1925", "Челышева"),
            ("с 16 декабря 1925", "Фрунзе"),
        ],
        "Frunze",
    )
    require(9500 <= frunze_count <= 36000, f"Frunze md length is {frunze_count}, expected 9500-36000")
    require("## Источники" in frunze_text, "Frunze sources section is missing")
    require("lat:" not in frunze_text, "Frunze published md should not contain latitude metadata")
    require("lon:" not in frunze_text, "Frunze published md should not contain longitude metadata")
    for required_fact in ("2,4", "16 декабря 1925", "1853", "1915", "1902-1906", "47", "37", "1907", "1100", "1934"):
        require(required_fact in frunze_text, f"Frunze md should include numeric fact: {required_fact}")
    for new_fact in ("12 февраля 1915", "Алексеевской площади", "пять вагонов", "22 километров в час", "115 тыс.", "3 копейки", "Драматический театр", "1888", "Михаила Чичагова"):
        require(new_fact in frunze_text, f"Frunze md should include added tram/theatre fact: {new_fact}")
    require(frunze_text.count("![") >= 12, "Frunze md should include at least twelve publication images")
    require(frunze_text.count("commons.wikimedia.org/wiki/Special:FilePath/") >= 12, "Frunze images should use Wikimedia Commons file paths")
    require(frunze_text.count("Источник изображения:") >= 12, "Frunze images should have visible source captions")
    for image_label in (
        "Дом Челышева",
        "Дом-музей М. В. Фрунзе",
        "Губернская земская управа",
        "Самарская филармония",
        "Дом Шостаковича",
        "Музей-усадьба А. Н. Толстого",
        "Костел Пресвятого Сердца Иисуса",
        "Особняк Курлиной",
        "Памятник Чапаеву",
        "Самарский драматический театр",
        "Бункер Сталина",
        "трамвай на улице Фрунзе",
    ):
        require(image_label in frunze_text, f"Frunze md should include image/caption for: {image_label}")

    require('"Фрунзе"' in map_source, "Frunze street data is missing in map.py")
    frunze_coords = streets["Фрунзе"]["coords"]
    require(len(frunze_coords) >= 45, "Frunze route should use detailed OSM street geometry")
    frunze_longest_segment = max(
        meters_between(frunze_coords[i], frunze_coords[i + 1])
        for i in range(len(frunze_coords) - 1)
    )
    require(frunze_longest_segment < 260, f"Frunze line has a {frunze_longest_segment:.1f}m shortcut segment")
    for marker_name in ("Музей модерна", "Костел Пресвятого Сердца Иисуса", "Бункер И. В. Сталина", "Дом-музей М. В. Фрунзе", "Трамвай на Саратовской / Фрунзе", "Самарский драматический театр"):
        require(marker_name in map_source, f"Frunze marker is missing: {marker_name}")
    require("Улица Фрунзе" in html_source, "generated map does not contain Frunze tooltip")
    frunze_image_places = [
        place for place in places
        if place.get("color") == "blue" and place.get("image_url")
    ]
    require(len(frunze_image_places) >= 12, "Frunze map should include thumbnails for at least twelve blue markers")
    require("popup-thumb" in html_source, "generated map popups should render image thumbnails")
    require("Самарский драматический театр" in html_source, "generated map should include drama theater popup")
    require("Самарская филармония" in html_source, "generated map should include Philharmonia thumbnail caption")

    print(f"validated {STREET_MD.relative_to(ROOT)} ({char_count} chars), {FRUNZE_MD.relative_to(ROOT)} ({frunze_count} chars)")


if __name__ == "__main__":
    main()
