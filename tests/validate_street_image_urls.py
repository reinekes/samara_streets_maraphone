from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.parse import parse_qs, urlencode, unquote, urlparse
from urllib.request import Request, urlopen
import argparse
import ast
import json
import re


ROOT = Path(__file__).resolve().parents[1]
MAP_PY = ROOT / "map.py"
COMMONS_API = "https://commons.wikimedia.org/w/api.php"


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


def extract_markdown_urls(path):
    text = path.read_text(encoding="utf-8")
    return re.findall(r"!\[[^\]]+\]\((https?://[^\n]+)\)", text)


def extract_commons_file_title(url):
    parsed_url = urlparse(url)
    require(
        parsed_url.netloc == "commons.wikimedia.org",
        f"non-Commons image URL is not supported by this validator: {url}",
    )

    if parsed_url.path == "/w/index.php":
        title = parse_qs(parsed_url.query).get("title", [""])[0]
        prefix = "Special:Redirect/file/"
        if title.startswith(prefix):
            return "File:" + unquote(title[len(prefix) :]).replace("_", " ")

    prefix = "/wiki/Special:FilePath/"
    if parsed_url.path.startswith(prefix):
        return "File:" + unquote(parsed_url.path[len(prefix) :]).replace("_", " ")

    raise AssertionError(f"unsupported Commons image URL format: {url}")


def fetch_file_metadata(titles):
    request = Request(
        COMMONS_API
        + "?"
        + urlencode(
            {
                "action": "query",
                "format": "json",
                "prop": "imageinfo",
                "iiprop": "mime|url",
                "iiurlwidth": "520",
                "titles": "|".join(titles),
            }
        ),
        headers={"User-Agent": "SamaraMapImageValidator/1.0"},
    )
    with urlopen(request, timeout=15) as response:
        return json.loads(response.read().decode("utf-8"))


def validate_file_titles(titles):
    failures = []
    title_to_metadata = {}

    sorted_titles = sorted(set(titles))
    for start in range(0, len(sorted_titles), 50):
        batch = sorted_titles[start : start + 50]
        try:
            payload = fetch_file_metadata(batch)
        except HTTPError as error:
            failures.append(f"Commons API: HTTP {error.code} while checking {len(batch)} files")
            continue
        except URLError as error:
            failures.append(
                f"Commons API: network error {error.reason} while checking {len(batch)} files"
            )
            continue

        for page in payload.get("query", {}).get("pages", {}).values():
            title = page.get("title", "")
            imageinfo = page.get("imageinfo") or []
            title_to_metadata[title] = imageinfo[0] if imageinfo else None

    for title in sorted_titles:
        metadata = title_to_metadata.get(title)
        if metadata is None:
            failures.append(f"{title}: missing Commons image metadata")
            continue

        mime = metadata.get("mime", "")
        image_url = metadata.get("thumburl") or metadata.get("url", "")
        if not mime.startswith("image/") or not image_url:
            failures.append(f"{title}: invalid image metadata {mime} {image_url}")

    return failures


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--street", required=True)
    parser.add_argument("--markdown", required=True)
    parser.add_argument("--color")
    args = parser.parse_args()

    markdown_path = ROOT / args.markdown
    require(markdown_path.exists(), f"{args.markdown} is missing")

    places = load_places()
    street_places = [
        place
        for place in places
        if place.get("street") == args.street
        or place.get("color") == args.color
    ]

    markdown_urls = extract_markdown_urls(markdown_path)
    url_to_title = {}
    failures = []

    for place in street_places:
        url = place.get("image_url")
        if not url:
            failures.append(f"{place['name']}: missing image_url")
            continue

        try:
            url_to_title[url] = extract_commons_file_title(url)
        except AssertionError as error:
            failures.append(f"{place['name']}: {error}")

    for url in markdown_urls:
        try:
            url_to_title[url] = extract_commons_file_title(url)
        except AssertionError as error:
            failures.append(f"markdown image: {error}")

    failures.extend(validate_file_titles(url_to_title.values()))

    require(
        not failures,
        f"broken {args.street} image URLs:\n" + "\n".join(failures),
    )

    print(
        f"validated {args.street} image URLs: "
        f"{len(street_places)} map markers, {len(markdown_urls)} markdown images"
    )


if __name__ == "__main__":
    main()
