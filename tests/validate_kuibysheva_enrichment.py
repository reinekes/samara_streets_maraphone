from pathlib import Path
import ast
import math
from urllib.parse import unquote


ROOT = Path(__file__).resolve().parents[1]
MAP_PY = ROOT / "map.py"
MAP_HTML = ROOT / "samara_marathon_map.html"
KUIBYSHEVA_MD = ROOT / "streets" / "День 1 - Улица Куйбышева.md"


EXPECTED_COORDS = {
    "Гранд-Отель / Бристоль-Жигули": [53.1893001, 50.0905795],
    "Лютеранская кирха Святого Георга": [53.1898213, 50.0907831],
    "Волжско-Камский коммерческий банк": [53.1894953, 50.0896750],
    "Кинотеатр «Художественный»": [53.1885845, 50.0905115],
    "Особняк Клодта": [53.1934027, 50.0933006],
    "Особняк Наумова / посольство Великобритании": [53.1957377, 50.0948086],
    "Отделение Государственного банка": [53.1921655, 50.0911980],
    "Благородное собрание": [53.1916840, 50.0923185],
    "Дом купца Аржанова": [53.1873578, 50.0891550],
    "Крестьянский и Дворянский поземельные банки": [53.1960675, 50.0952524],
    "Дом промышленности": [53.1943197, 50.0940957],
    "Самарская публичная библиотека": [53.1874889, 50.0892379],
    "Дом купца Белоусова": [53.1870493, 50.0878292],
    "Музей истории войск ПриВО": [53.1967499, 50.0955090],
    "Городская управа": [53.1839787, 50.0862511],
    "Дом братьев Кирилловых": [53.1840935, 50.0872569],
    "Главпочтамт и почтово-телеграфная контора": [53.1883042, 50.0885477],
    "Дом Жоголева / посольство Австралии": [53.1918921, 50.0907185],
    "Дом Елизаровых": [53.1793546, 50.0839564],
    "Дом Синицына": [53.1813413, 50.0851272],
    "Жилой дом на Куйбышева, 31": [53.1814602, 50.0852869],
    "Дом Линева-Разина": [53.1835416, 50.0856932],
    "Дом Первовского": [53.1837099, 50.0860442],
    "Русский торгово-промышленный банк": [53.1830480, 50.0857880],
    "Окружной суд": [53.1852128, 50.0861531],
    "Дом Калачева": [53.1866266, 50.0885394],
    "Промбанк на углу Ленинградской": [53.1876703, 50.0892060],
    "Особняк Покидышева": [53.1880632, 50.0897591],
    "Дом Юдина": [53.1884257, 50.0898641],
    "Дом Ясенкова": [53.1895455, 50.0906915],
    "Дом Малышева": [53.1905325, 50.0912429],
    "Дом Васильева": [53.1906850, 50.0916032],
    "Школа имени Н. А. Хардиной": [53.1909191, 50.0915355],
    "Особняк Дунаева": [53.1927907, 50.0930366],
}


EXPECTED_IMAGE_FRAGMENTS = {
    "Дом купца Аржанова": "93_Kuybisheva_st_Samara.JPG",
    "Музей истории войск ПриВО": "Museum_of_war_history",
    "Дом Елизаровых": "Куйб7-2-012.JPG",
    "Дом Синицына": "Samara_Kuybysheva_29.jpg",
    "Жилой дом на Куйбышева, 31": "Samara_Kuybysheva_31.jpg",
    "Дом Линева-Разина": "Samara._Former_mansion_of_Linev-Razin",
    "Дом Первовского": "Samara_Kuybysheva_46.jpg",
    "Русский торгово-промышленный банк": "Samara._Kuybysheva_Street_P6190086_2350.jpg",
    "Окружной суд": "60_Kuybisheva_st_Samara.JPG",
    "Дом Калачева": "Дом_Калачева",
    "Промбанк на углу Ленинградской": "Самара,_улица_Куйбышева,_97.jpg",
    "Особняк Покидышева": "Особняк_Л.Н._Покидышева.jpg",
    "Дом Юдина": "103_Kuybisheva_st_Samara.JPG",
    "Дом Ясенкова": "Куйбышева_113.jpg",
    "Дом Малышева": "Куйбышева_121.jpg",
    "Дом Васильева": "Дом_Васильева",
    "Школа имени Н. А. Хардиной": "Samara_Kuybysheva_125.jpg",
    "Особняк Дунаева": "Samara_Kuybysheva_135.jpg",
}


def require(condition, message):
    if not condition:
        raise AssertionError(message)


def load_places():
    tree = ast.parse(MAP_PY.read_text(encoding="utf-8"))
    for node in tree.body:
        if isinstance(node, ast.Assign):
            for target in node.targets:
                if isinstance(target, ast.Name) and target.id == "places":
                    return ast.literal_eval(node.value)
    raise AssertionError("places assignment is missing in map.py")


def meters_between(a, b):
    lat1, lon1 = map(math.radians, a)
    lat2, lon2 = map(math.radians, b)
    dlat = lat2 - lat1
    dlon = lon2 - lon1
    hav = math.sin(dlat / 2) ** 2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon / 2) ** 2
    return 6371000 * 2 * math.atan2(math.sqrt(hav), math.sqrt(1 - hav))


def main():
    text = KUIBYSHEVA_MD.read_text(encoding="utf-8")
    html = MAP_HTML.read_text(encoding="utf-8")
    places = load_places()
    red_places = {place["name"]: place for place in places if place.get("color") == "red"}

    required_facts = [
        "Дом потомственной дворянки Любови Боянус",
        "Учительско-педагогическому институту",
        "дом был перестроен в 1900 году Александром Зеленко",
        "цены были написаны прямо на товарах",
        "анархистского мятежа мая 1918 года",
        "кинотреугольник",
        "Oldsmobil",
        "посольство Австралии",
        "Императорского русского музыкального общества",
        "пять газетных киосков",
        "30 рублей в год",
        "клуб ворошиловских стрелков",
        "конка, грузовой трамвай, троллейбус и автобус",
        "Museum of war history, Samara",
        "Дом Ясенкова",
        "Дом Юдина",
        "Особняк Дунаева",
        "Дом Елизаровых",
        "Дом Синицына",
        "Дом Линева-Разина",
        "Русский торгово-промышленный банк",
        "Промбанк на углу Ленинградской",
        "Дом Малышева",
    ]
    for fact in required_facts:
        require(fact in text, f"missing Kuybysheva fact: {fact}")

    for marker_name, expected_coord in EXPECTED_COORDS.items():
        require(marker_name in red_places, f"missing Kuybysheva marker: {marker_name}")
        place = red_places[marker_name]
        require(place.get("image_url"), f"{marker_name} should have image_url")
        require(place.get("image_caption"), f"{marker_name} should have image_caption")
        distance = meters_between(place["coords"], expected_coord)
        require(distance <= 45, f"{marker_name} is {distance:.1f}m from checked address coordinate")
        require(marker_name in html, f"generated map should include marker: {marker_name}")

        expected_image_fragment = EXPECTED_IMAGE_FRAGMENTS.get(marker_name)
        if expected_image_fragment:
            image_url = unquote(place["image_url"])
            require(
                expected_image_fragment in image_url,
                f"{marker_name} should use image from its specific Commons category",
            )

    require(text.count("![") >= 32, "Kuybysheva article should have at least 32 images")
    require(len(red_places) >= 34, "Kuybysheva map should include at least 34 red markers")
    require(
        all(place.get("image_url") for place in red_places.values()),
        "all red Kuybysheva markers should have image_url",
    )

    print(f"validated Kuybysheva enrichment: {len(red_places)} red markers")


if __name__ == "__main__":
    main()
