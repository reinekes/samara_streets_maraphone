from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
MAP_PY = ROOT / "map.py"
MAP_HTML = ROOT / "samara_marathon_map.html"


def require(condition, message):
    if not condition:
        raise AssertionError(message)


def main():
    map_source = MAP_PY.read_text(encoding="utf-8")
    html_source = MAP_HTML.read_text(encoding="utf-8")

    require(
        "Объекты культурного наследия" in map_source,
        "heritage layer control label is missing in map.py",
    )
    require(
        "heritage-marker" in html_source,
        "heritage markers should use a distinct popup class",
    )
    require(
        html_source.count("heritage-marker") >= 760,
        "generated map should include all GeoJSON heritage objects",
    )
    require(
        html_source.count('"icon": "ok-sign"') >= 760,
        "heritage markers should use checkmark icons",
    )

    for required_object in (
        "Здание женской гимназии (дом Поплавского)",
        "Особняк Клодта",
        "Польский костел",
        "Дом Маштакова",
    ):
        require(
            required_object in html_source,
            f"heritage popup is missing object: {required_object}",
        )

    for required_field in (
        "<b>Адрес:</b>",
        "<b>Категория:</b>",
        "<b>Вид объекта:</b>",
        "<b>Регистрационный номер:</b>",
    ):
        require(
            required_field in html_source,
            f"heritage popup is missing field label: {required_field}",
        )

    print("validated heritage layer in samara_marathon_map.html")


if __name__ == "__main__":
    main()
