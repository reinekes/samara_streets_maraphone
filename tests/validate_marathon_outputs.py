from pathlib import Path
import ast
import math


ROOT = Path(__file__).resolve().parents[1]
STREET_MD = ROOT / "streets" / "01-kuibysheva.md"
FRUNZE_MD = ROOT / "streets" / "02-frunze.md"
LENINGRADSKAYA_MD = ROOT / "streets" / "03-leningradskaya.md"
SAMARSKAYA_MD = ROOT / "streets" / "04-samarskaya.md"
MOLODOGVARDEYSKAYA_MD = ROOT / "streets" / "05-molodogvardeyskaya.md"
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

    require(LENINGRADSKAYA_MD.exists(), "streets/03-leningradskaya.md is missing")
    leningradskaya_text = LENINGRADSKAYA_MD.read_text(encoding="utf-8")
    leningradskaya_count = len(leningradskaya_text)
    require("date: 05" in leningradskaya_text, "Leningradskaya dataview date field should use leading zero")
    require("month: 08" in leningradskaya_text, "Leningradskaya dataview month field is missing")
    require("year: 2026" in leningradskaya_text, "Leningradskaya dataview year field is missing")
    require_name_history_table(
        leningradskaya_text,
        [
            ("1830-е", "Проломная"),
            ("1840-е", "Сенная"),
            ("1850-е", "Москательная"),
            ("1860-е", "Хлебная"),
            ("с 1870-х - 1918", "Панская"),
            ("1918 - 1924", "Петроградская"),
            ("с 1924", "Ленинградская"),
        ],
        "Leningradskaya",
    )
    require(15000 <= leningradskaya_count <= 36000, f"Leningradskaya md length is {leningradskaya_count}, expected 15000-36000")
    require("| с 1926 | Ленинградская |" not in leningradskaya_text, "Leningradskaya md should not keep the incorrect 1926 renaming table row")
    require("затем в **Ленинградскую** (1926)" not in leningradskaya_text, "Leningradskaya md should not keep the incorrect 1926 renaming sentence")
    for required_fact in ("1782", "15 метров", "1860", "1,8 км", "1986", "1949", "1991", "2001", "2002", "2011"):
        require(required_fact in leningradskaya_text, f"Leningradskaya md should include numeric fact: {required_fact}")
    for required_place in ("Дом Челышева", "Главпочтамт", "Дом Нуйчева", "гостиница «Националь»", "Дом обуви", "Новотроицкий торговый корпус", "арт-кластер «Дом 77»"):
        require(required_place in leningradskaya_text, f"Leningradskaya md should include route place: {required_place}")
    require(leningradskaya_text.count("![") >= 10, "Leningradskaya md should include at least ten publication images")
    require(leningradskaya_text.count("Источник изображения:") >= 10, "Leningradskaya images should have visible source captions")
    require("## Источники" in leningradskaya_text, "Leningradskaya sources section is missing")
    require("lat:" not in leningradskaya_text, "Leningradskaya published md should not contain latitude metadata")
    require("lon:" not in leningradskaya_text, "Leningradskaya published md should not contain longitude metadata")

    require('"Ленинградская"' in map_source, "Leningradskaya street data is missing in map.py")
    leningradskaya_coords = streets["Ленинградская"]["coords"]
    require(len(leningradskaya_coords) >= 20, "Leningradskaya route should use detailed street geometry")
    leningradskaya_longest_segment = max(
        meters_between(leningradskaya_coords[i], leningradskaya_coords[i + 1])
        for i in range(len(leningradskaya_coords) - 1)
    )
    require(leningradskaya_longest_segment < 260, f"Leningradskaya line has a {leningradskaya_longest_segment:.1f}m shortcut segment")
    leningradskaya_image_places = [
        place for place in places
        if place.get("color") == "green" and place.get("image_url")
    ]
    require(len(leningradskaya_image_places) >= 10, "Leningradskaya map should include thumbnails for at least ten green markers")
    for marker_name in ("Дом мещан Ильиных", "Особняк рыбопромышленника Сапрыкина", "Главпочтамт", "Дом художника Головкина", "«Националь»", "Дом Нуйчева", "Дом Жукова", "Дядя Степа", "Арт-кластер «Дом 77»"):
        require(marker_name in map_source, f"Leningradskaya marker is missing: {marker_name}")
    require("Улица Ленинградская" in html_source, "generated map does not contain Leningradskaya tooltip")
    require("Особняк Сапрыкина" in html_source, "generated map should include Leningradskaya thumbnail caption")

    require(SAMARSKAYA_MD.exists(), "streets/04-samarskaya.md is missing")
    samarskaya_text = SAMARSKAYA_MD.read_text(encoding="utf-8")
    samarskaya_count = len(samarskaya_text)
    require("date: 06" in samarskaya_text, "Samarskaya dataview date field should use leading zero")
    require("month: 08" in samarskaya_text, "Samarskaya dataview month field is missing")
    require("year: 2026" in samarskaya_text, "Samarskaya dataview year field is missing")
    require_name_history_table(
        samarskaya_text,
        [
            ("1782", "восточная граница регулярной Самары"),
            ("начало XIX века - 1840-е", "Мечетная"),
            ("с середины XIX века", "Самарская"),
        ],
        "Samarskaya",
    )
    require(15000 <= samarskaya_count <= 42000, f"Samarskaya md length is {samarskaya_count}, expected 15000-42000")
    for required_fact in ("1586", "1782", "1804", "634", "2000-2200", "70,4", "467,3", "746", "1851", "89 тысяч", "1897", "1941", "1955", "1958"):
        require(required_fact in samarskaya_text, f"Samarskaya md should include numeric fact: {required_fact}")
    for required_place in ("Мечетной", "татарская слобода", "Троицкий рынок", "Пассаж", "Сад-Аркадия", "Аквариум", "Дом авиаторов", "Дом Маштакова", "Самарская площадь", "Гидропроекта", "Большого театра"):
        require(required_place in samarskaya_text, f"Samarskaya md should include route place: {required_place}")
    require(samarskaya_text.count("![") >= 14, "Samarskaya md should include at least fourteen publication images")
    require(samarskaya_text.count("Источник изображения:") >= 14, "Samarskaya images should have visible source captions")
    require("## Источники" in samarskaya_text, "Samarskaya sources section is missing")
    require("lat:" not in samarskaya_text, "Samarskaya published md should not contain latitude metadata")
    require("lon:" not in samarskaya_text, "Samarskaya published md should not contain longitude metadata")

    require('"Самарская"' in map_source, "Samarskaya street data is missing in map.py")
    samarskaya_coords = streets["Самарская"]["coords"]
    require(len(samarskaya_coords) >= 55, "Samarskaya route should use detailed street geometry")
    samarskaya_longest_segment = max(
        meters_between(samarskaya_coords[i], samarskaya_coords[i + 1])
        for i in range(len(samarskaya_coords) - 1)
    )
    require(samarskaya_longest_segment < 260, f"Samarskaya line has a {samarskaya_longest_segment:.1f}m shortcut segment")
    samarskaya_image_places = [
        place for place in places
        if place.get("color") == "orange" and place.get("image_url")
    ]
    require(len(samarskaya_image_places) >= 14, "Samarskaya map should include thumbnails for at least fourteen orange markers")
    for marker_name in ("Мечетная улица", "«Замок» Волгопромгаза", "Кухмистерская «Сад-Аркадия»", "Пассаж купчихи Марфы Дьяковой", "Ресторан-варьете «Аквариум»", "Доходный дом доктора Гринберга", "Дом авиаторов", "Дом архитектора Александра Зеленко", "Дом «Гидропроекта»", "Дом Маштакова"):
        require(marker_name in map_source, f"Samarskaya marker is missing: {marker_name}")
    require("Улица Самарская" in html_source, "generated map does not contain Samarskaya tooltip")
    require("Бывший «Аквариум»" in html_source, "generated map should include Aquarium thumbnail caption")

    require(MOLODOGVARDEYSKAYA_MD.exists(), "streets/05-molodogvardeyskaya.md is missing")
    molodogvardeyskaya_text = MOLODOGVARDEYSKAYA_MD.read_text(encoding="utf-8")
    molodogvardeyskaya_count = len(molodogvardeyskaya_text)
    require("date: 07" in molodogvardeyskaya_text, "Molodogvardeyskaya dataview date field should use leading zero")
    require("month: 08" in molodogvardeyskaya_text, "Molodogvardeyskaya dataview month field is missing")
    require("year: 2026" in molodogvardeyskaya_text, "Molodogvardeyskaya dataview year field is missing")
    require_name_history_table(
        molodogvardeyskaya_text,
        [
            ("1800-е", "У Самары"),
            ("1820-е", "Узенькая"),
            ("1839 - 1850-е", "Сенная"),
            ("1840-е - 1850-е", "Симбирская / Хлебная"),
            ("с 1852 / 1860-х - 6 июля 1923", "Соборная"),
            ("с 1894", "Ново-Соборная, часть от Вилоновской до Полевой"),
            ("6 июля 1923 - 27 октября 1948", "Кооперативная"),
            ("с 27 октября 1948", "Молодогвардейская"),
        ],
        "Molodogvardeyskaya",
    )
    require(17000 <= molodogvardeyskaya_count <= 44000, f"Molodogvardeyskaya md length is {molodogvardeyskaya_count}, expected 17000-44000")
    for required_fact in ("3822", "4,5-4,6", "18 улиц", "1782", "1851", "6 июля 1923", "27 октября 1948", "1900", "1898", "1881", "1917", "1927", "400 метров", "1912", "1911", "1932", "1941", "2022", "1869", "1894", "1930", "1932", "1872", "1931-1939", "1967", "1977", "2000"):
        require(required_fact in molodogvardeyskaya_text, f"Molodogvardeyskaya md should include numeric fact: {required_fact}")
    for required_place in ("Молодогвардейский спуск", "Рудольф Абель", "Ночлежный дом", "Кондитерская фабрика", "Троицкой площади", "Новотроицкий торговый корпус", "Щетинкина", "Матвеевых", "Дом Основнина", "Дом Плошкина", "Криппса", "музей самарской почты", "Соборная площадь", "Самарская духовная семинария", "Валерий Грушин", "Дом быта \"Горизонт\"", "\"Крепость\"", "СамГТУ"):
        require(required_place in molodogvardeyskaya_text, f"Molodogvardeyskaya md should include route place: {required_place}")
    require(molodogvardeyskaya_text.count("![") >= 16, "Molodogvardeyskaya md should include at least sixteen publication images")
    require(molodogvardeyskaya_text.count("Источник изображения:") >= 16, "Molodogvardeyskaya images should have visible source captions")
    require("## Источники" in molodogvardeyskaya_text, "Molodogvardeyskaya sources section is missing")
    require("lat:" not in molodogvardeyskaya_text, "Molodogvardeyskaya published md should not contain latitude metadata")
    require("lon:" not in molodogvardeyskaya_text, "Molodogvardeyskaya published md should not contain longitude metadata")

    require('"Молодогвардейская"' in map_source, "Molodogvardeyskaya street data is missing in map.py")
    molodogvardeyskaya_coords = streets["Молодогвардейская"]["coords"]
    require(len(molodogvardeyskaya_coords) >= 55, "Molodogvardeyskaya route should use detailed street geometry")
    molodogvardeyskaya_longest_segment = max(
        meters_between(molodogvardeyskaya_coords[i], molodogvardeyskaya_coords[i + 1])
        for i in range(len(molodogvardeyskaya_coords) - 1)
    )
    require(molodogvardeyskaya_longest_segment < 260, f"Molodogvardeyskaya line has a {molodogvardeyskaya_longest_segment:.1f}m shortcut segment")
    molodogvardeyskaya_image_places = [
        place for place in places
        if place.get("color") == "purple" and place.get("image_url")
    ]
    require(len(molodogvardeyskaya_image_places) >= 18, "Molodogvardeyskaya map should include thumbnails for at least eighteen purple markers")
    for marker_name in ("Молодогвардейский спуск", "Рудольфа Абеля", "Ночлежный дом Кириллова", "Новотроицкий торговый корпус", "Торговый дом Павла Щетинкина", "Особняк братьев Матвеевых", "Дом Основнина", "Дом Плошкина", "Музей самарской почты", "Площадь Куйбышева", "Самарская духовная семинария", "Духовное училище / КуАИ", "Самарская губернская дума", "Дом «Крепость»", "Главный корпус СамГТУ"):
        require(marker_name in map_source, f"Molodogvardeyskaya marker is missing: {marker_name}")
    require("Улица Молодогвардейская" in html_source, "generated map does not contain Molodogvardeyskaya tooltip")
    require("Духовное училище" in html_source, "generated map should include spiritual school thumbnail caption")

    print(
        f"validated {STREET_MD.relative_to(ROOT)} ({char_count} chars), "
        f"{FRUNZE_MD.relative_to(ROOT)} ({frunze_count} chars), "
        f"{LENINGRADSKAYA_MD.relative_to(ROOT)} ({leningradskaya_count} chars), "
        f"{SAMARSKAYA_MD.relative_to(ROOT)} ({samarskaya_count} chars), "
        f"{MOLODOGVARDEYSKAYA_MD.relative_to(ROOT)} ({molodogvardeyskaya_count} chars)"
    )


if __name__ == "__main__":
    main()
