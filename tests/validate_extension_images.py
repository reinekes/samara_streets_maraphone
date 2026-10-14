"""Live-check embedded images in marathon articles 21-30."""

import re
import os
import runpy
import tempfile
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen


ROOT = Path(__file__).resolve().parents[1]


def check(url):
    request = Request(url, headers={"User-Agent": "SamaraMarathonMap/1.0 (image audit)"})
    try:
        with urlopen(request, timeout=20) as response:
            kind = response.headers.get("Content-Type", "")
            if response.status == 200 and kind.startswith("image/"):
                return None
            return f"HTTP {response.status}, {kind}: {url}"
    except (HTTPError, URLError, TimeoutError) as error:
        return f"{error}: {url}"


def main():
    urls = {}
    for day in range(21, 31):
        article = next((ROOT / "streets").glob(f"День {day} - *.md"))
        for url in re.findall(r"!\[[^\]]*\]\((https?://[^)]+)\)", article.read_text()):
            urls.setdefault(url, []).append(day)

    previous = Path.cwd()
    try:
        with tempfile.TemporaryDirectory() as temporary:
            os.chdir(temporary)
            state = runpy.run_path(str(ROOT / "map.py"))
    finally:
        os.chdir(previous)
    for place in state["places"]:
        if place.get("street") in state["extension_days"] and place.get("image_url"):
            urls.setdefault(place["image_url"], []).append(place["street"])

    failures = []
    with ThreadPoolExecutor(max_workers=4) as executor:
        tasks = {executor.submit(check, url): url for url in urls}
        for task in as_completed(tasks):
            failure = task.result()
            if failure:
                failures.append(failure)

    print(f"Checked {len(urls)} distinct image URLs in articles and map stops, days 21-30")
    if failures:
        print("\n".join(failures))
        raise SystemExit(f"{len(failures)} image URLs failed")
    print("All returned HTTP 200 and an image content type")


if __name__ == "__main__":
    main()
