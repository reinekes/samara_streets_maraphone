"""Check the rendered continuation, including routes loaded from data files."""

from pathlib import Path
import os
import re
import runpy
import tempfile


ROOT = Path(__file__).resolve().parents[1]
EXPECTED = [
    "Вилоновская", "Ульяновская", "Волжский проспект", "Маяковского",
    "Чкалова", "Полевая", "Братьев Коростелёвых", "Арцыбушевская",
    "Буянова", "Ново-Садовая",
]


def main():
    previous = Path.cwd()
    try:
        with tempfile.TemporaryDirectory() as temporary:
            os.chdir(temporary)
            state = runpy.run_path(str(ROOT / "map.py"))
            generated = Path("samara_marathon_map.html").read_text()
    finally:
        os.chdir(previous)

    missing = set(EXPECTED) - state["street_layers"].keys()
    assert not missing, f"New street layers are missing: {sorted(missing)}"
    assert len(state["street_layers"]) == 30, "Original twenty layers must remain"
    for number, name in enumerate(EXPECTED, 21):
        matches = list((ROOT / "streets").glob(f"День {number} - *.md"))
        assert len(matches) == 1, (number, matches)
        text = matches[0].read_text()
        assert len(re.findall(r"\[!success\]-", text)) == 30, matches[0]
        assert len(re.findall(r"!\[[^\]]+\]\(", text)) >= 4, matches[0]
        for target in re.findall(r"\[\[([^|\]]+)", text):
            assert (ROOT / "streets" / f"{target}.md").exists(), target
        route = state["streets"][name]
        assert route.get("segments"), f"No sourced line geometry for {name}"
        points = [p for p in state["places"] if p.get("street") == name]
        assert points, f"No markers in {name} layer"
        for point in points:
            assert point.get("image_url"), point["name"]
            assert point.get("coordinate_source"), point["name"]
            lat, lon = point["coords"]
            assert 53.15 < lat < 53.35 and 50.03 < lon < 50.35, point
        assert name in generated, f"Layer absent from saved HTML: {name}"
    print("Validated 30 rendered street layers, 10 articles, quizzes, images and marker provenance")


if __name__ == "__main__":
    main()
