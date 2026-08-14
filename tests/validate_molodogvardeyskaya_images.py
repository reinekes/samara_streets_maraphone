from pathlib import Path
import ast


ROOT = Path(__file__).resolve().parents[1]
MAP_PY = ROOT / "map.py"
MAP_HTML = ROOT / "samara_marathon_map.html"


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
    molodogvardeyskaya_places = [
        place
        for place in places
        if (
            place.get("street") == "Молодогвардейская"
            or place.get("color") == "purple"
        )
    ]
    image_places = [
        place
        for place in molodogvardeyskaya_places
        if place.get("image_url") and place.get("image_caption")
    ]

    require(
        len(molodogvardeyskaya_places) == 35,
        f"expected 35 Molodogvardeyskaya markers, got {len(molodogvardeyskaya_places)}",
    )
    require(
        len(image_places) >= 30,
        f"expected at least 30 Molodogvardeyskaya marker images, got {len(image_places)}",
    )

    html_source = MAP_HTML.read_text(encoding="utf-8")
    for caption in (
        "Молодогвардейский спуск",
        "Дом Фишера / Абеля",
        "Дом быта «Горизонт»",
        "Дом «Крепость»",
        "Дворец бракосочетаний «Теремок»",
    ):
        require(
            caption in html_source,
            f"generated map should include image caption: {caption}",
        )

    print(
        "validated Molodogvardeyskaya marker images: "
        f"{len(image_places)}/{len(molodogvardeyskaya_places)}"
    )


if __name__ == "__main__":
    main()
