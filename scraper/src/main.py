from pathlib import Path

import requests


BASE_URL = "https://books.toscrape.com/"
CACHE_DIR = Path(__file__).resolve().parent.parent / "cache"
CACHE_FILE = CACHE_DIR / "catalogue-page-1.html"

USER_AGENT = "FlyRankInternship-A9/1.0 (+https://github.com/Simi268/task-api)"
TIMEOUT = 10


def fetch_catalogue_page():
    CACHE_DIR.mkdir(parents=True, exist_ok=True)

    if CACHE_FILE.exists():
        content = CACHE_FILE.read_bytes()
        print(f"CACHE HIT | size={len(content)} bytes")
        return content

    headers = {
        "User-Agent": USER_AGENT
    }

    response = requests.get(
        BASE_URL,
        headers=headers,
        timeout=TIMEOUT,
    )

    if response.status_code != 200:
        raise RuntimeError(
            f"FETCH FAILED | status={response.status_code}"
        )

    content = response.content
    CACHE_FILE.write_bytes(content)

    print(f"FETCH | status={response.status_code} | size={len(content)} bytes")

    return content


if __name__ == "__main__":
    fetch_catalogue_page()