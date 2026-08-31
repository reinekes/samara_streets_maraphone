from pathlib import Path
import ast


ROOT = Path(__file__).resolve().parents[1]
MAP_PY = ROOT / "map.py"

STREETS = {
    "Фрунзе": {
        "color": "blue",
        "markdown": ROOT / "streets" / "День 2 - Улица Фрунзе.md",
        "min_markers": 20,
        "required_markers": [
            "Дом Подбельского",
            "Фрунзе, 112",
            "Дом на Фрунзе, 119",
            "Дом Гиршфельда",
            "Фахверковый дом во дворе Фрунзе, 75",
            "Дом Новокрещеновой",
            "Дом Поплавского",
        ],
    },
    "Ленинградская": {
        "color": "green",
        "markdown": ROOT / "streets" / "День 3 - Улица Ленинградская.md",
        "min_markers": 25,
        "required_markers": [
            "Жилой дом на Ленинградской, 43",
            "Дом Пожидаева",
            "Дом Петша",
        ],
    },
    "Самарская": {
        "color": "orange",
        "markdown": ROOT / "streets" / "День 4 - Улица Самарская.md",
        "min_markers": 27,
        "required_markers": [
            "Жилой дом на Самарской, 100",
            "Дом Нуйчева на Самарской",
        ],
    },
    "Молодогвардейская": {
        "color": "purple",
        "markdown": ROOT / "streets" / "День 5 - Улица Молодогвардейская.md",
        "min_markers": 35,
        "required_markers": [
            "Дом купца Ивана Санина",
            "Новотроицкий торговый корпус / «Юность»",
            "Дом научных работников",
        ],
    },
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


def main():
    places = load_places()
    for street_name, config in STREETS.items():
        street_places = [
            place
            for place in places
            if place.get("street") == street_name or place.get("color") == config["color"]
        ]
        by_name = {place["name"]: place for place in street_places}
        require(
            len(street_places) >= config["min_markers"],
            f"{street_name}: expected at least {config['min_markers']} markers, got {len(street_places)}",
        )
        missing_images = [place["name"] for place in street_places if not place.get("image_url")]
        require(not missing_images, f"{street_name}: markers without images: {missing_images}")
        for marker_name in config["required_markers"]:
            require(marker_name in by_name, f"{street_name}: missing marker {marker_name}")
            require(by_name[marker_name].get("image_caption"), f"{street_name}: {marker_name} lacks caption")

        markdown = config["markdown"].read_text(encoding="utf-8")
        require(
            "Глубокая проверка Commons и фото" in markdown,
            f"{street_name}: missing Commons/photo audit section",
        )

    print("validated next four street enrichment")


if __name__ == "__main__":
    main()
