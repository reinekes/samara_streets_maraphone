"""List article text and image URLs while researching new street days.

The source material is printed for editorial review, not copied into the repo.
"""

import argparse
import html
import re
from html.parser import HTMLParser
from urllib.request import Request, urlopen


SOURCES = {
    "31": "https://drugoigorod.ru/democratic_street/",
    "32": "https://drugoigorod.ru/georgiy_dimitrova_street/",
    "33": "https://drugoigorod.ru/tashkentskaya_street/",
    "34": "https://drugoigorod.ru/starazagora_street-2/",
    "35": "https://drugoigorod.ru/soviet_army_streets/",
    "36": "https://drugoigorod.ru/gagarin_street/",
    "37": "https://drugoigorod.ru/victory_streets/",
    "38": "https://drugoigorod.ru/aurora_street/",
    "39": "https://drugoigorod.ru/osipenko_street/",
    "40": "https://drugoigorod.ru/pushkin_street/",
}


class ArticleParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.depth = 0
        self.images = []
        self.paragraphs = []
        self.current = []

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if tag == "article":
            self.depth += 1
        elif self.depth and tag == "img":
            src = attrs.get("data-src") or attrs.get("src") or ""
            if "wp-content/uploads" in src:
                self.images.append((html.unescape(attrs.get("alt", "")), html.unescape(src)))
        elif self.depth and tag in ("p", "h2", "h3"):
            self.current = []

    def handle_endtag(self, tag):
        if self.depth and tag in ("p", "h2", "h3") and self.current:
            text = re.sub(r"\s+", " ", "".join(self.current)).strip()
            if text:
                self.paragraphs.append(text)
            self.current = []
        if tag == "article" and self.depth:
            self.depth -= 1

    def handle_data(self, data):
        if self.depth:
            self.current.append(data)


def main():
    args = argparse.ArgumentParser()
    args.add_argument("day", choices=SOURCES)
    args.add_argument("--images-only", action="store_true")
    selected = args.parse_args()
    request = Request(SOURCES[selected.day], headers={"User-Agent": "SamaraMarathonMap/1.0 (editorial research)"})
    with urlopen(request, timeout=45) as response:
        page = response.read().decode("utf-8")
    parser = ArticleParser()
    parser.feed(page)
    if not selected.images_only:
        print("\n".join(parser.paragraphs[:70]))
    print("\nIMAGES")
    for alt, src in parser.images:
        print(f"{alt}\t{src}")


if __name__ == "__main__":
    main()
