"""Check that days 21-30 exist as articles and rendered map layers."""

import os
import re
import runpy
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
EXPECTED = [
    "Вилоновская", "Ульяновская", "Шостаковича", "Маяковского",
    "Чкалова", "Полевая", "Братьев Коростелёвых", "Арцыбушевская",
    "Буянова", "Ново-Садовая",
]


def main():
    previous = Path.cwd()
    try:
        with tempfile.TemporaryDirectory() as temporary:
            os.chdir(temporary)
            state = runpy.run_path(str(ROOT / "map.py"))
            generated = Path("samara_marathon_map.html").read_text(encoding="utf-8")
    finally:
        os.chdir(previous)

    assert len(state["street_layers"]) == 30, "Expected original 20 plus 10 new layers"
    assert state["heritage_layer"] is not None
    assert generated.count("feature_group_") > 30

    for day, street in enumerate(EXPECTED, 21):
        assert street in state["street_layers"], f"No map layer for {street}"
        matches = list((ROOT / "streets").glob(f"День {day} - *.md"))
        assert len(matches) == 1, (day, matches)
        article = matches[0].read_text(encoding="utf-8")
        frontmatter = article.split("---", 2)[1]
        assert f"day: {day}" in frontmatter, matches[0]
        assert f"street: {street}" in frontmatter, matches[0]
        assert article.count("![") >= 4, f"Too few illustrated stops: {matches[0]}"
        answer_count = max(article.count("[!success]"), article.count("**Ответ:**"))
        assert answer_count == 30, (matches[0], answer_count)
        for target in re.findall(r"\[\[([^|\]]+)", article):
            assert (ROOT / "streets" / f"{target}.md").exists(), target

        segments = state["streets"][street].get("segments") or []
        assert segments, f"No sourced line geometry for {street}"
        assert all(len(segment) >= 2 for segment in segments), street
        for segment in segments:
            for lat, lon in segment:
                assert 53.15 < lat < 53.28 and 50.03 < lon < 50.25, (street, lat, lon)

        stops = [place for place in state["places"] if place.get("street") == street]
        assert len(stops) >= 5, f"Too few map stops for {street}"
        assert sum(bool(stop.get("image_url")) for stop in stops) >= 3, (
            f"Too few illustrated map stops for {street}"
        )
        for stop in stops:
            assert stop.get("coordinate_source") or any(
                "Для карты" in detail for detail in stop["info"]
            ), f"No coordinate provenance for {stop['name']}"

    novo_sadovaya = state["streets"]["Ново-Садовая"]
    assert len(novo_sadovaya["segments"]) == 1
    assert len(novo_sadovaya["segments"][0]) <= 15
    assert novo_sadovaya["highlight_weight"] <= 5

    print("Validated 30 street layers, articles 21-30, OSM segments and map stops")


if __name__ == "__main__":
    main()
