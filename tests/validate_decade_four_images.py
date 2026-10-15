"""Live-check embedded photos in days 31-40 and their map popups."""

import os
import re
import runpy
import tempfile
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

from validate_extension_images import check


ROOT = Path(__file__).resolve().parents[1]


def main():
    urls = {}
    for day in range(31, 41):
        article = next((ROOT / "streets").glob(f"День {day} - *.md"))
        for url in re.findall(r"!\[[^\]]*\]\((https?://[^)]+)\)", article.read_text(encoding="utf-8")):
            urls.setdefault(url, []).append(day)

    previous = Path.cwd()
    try:
        with tempfile.TemporaryDirectory() as directory:
            os.chdir(directory)
            state = runpy.run_path(str(ROOT / "map.py"))
    finally:
        os.chdir(previous)
    for place in state["places"]:
        if state["extension_days"].get(place.get("street"), 0) >= 31 and place.get("image_url"):
            urls.setdefault(place["image_url"], []).append(place["street"])

    failures = []
    with ThreadPoolExecutor(max_workers=4) as executor:
        tasks = {executor.submit(check, url): url for url in urls}
        for task in as_completed(tasks):
            failure = task.result()
            if failure:
                failures.append(failure)
    print(f"Checked {len(urls)} distinct image URLs, days 31-40")
    if failures:
        print("\n".join(failures))
        raise SystemExit(f"{len(failures)} image URLs failed")
    print("All returned HTTP 200 and an image content type")


if __name__ == "__main__":
    main()
