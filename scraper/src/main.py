from pathlib import Path
from time import sleep

import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin


BASE_URL = "https://books.toscrape.com/"
CACHE_DIR = Path(__file__).resolve().parent.parent / "cache"

USER_AGENT = "FlyRankInternship-A9/1.0 (+https://github.com/Simi268/task-api)"
TIMEOUT = 10
REQUEST_DELAY = 0.5


def fetch_page(url: str, cache_file: Path | None = None) -> bytes:
    """
    Fetch a page from the website or return its cached copy.
    """

    if cache_file and cache_file.exists():
        content = cache_file.read_bytes()
        print(f"CACHE HIT | {url} | size={len(content)} bytes")
        return content

    headers = {
        "User-Agent": USER_AGENT
    }

    response = requests.get(
        url,
        headers=headers,
        timeout=TIMEOUT,
    )

    if response.status_code != 200:
        raise RuntimeError(
            f"FETCH FAILED | status={response.status_code} | url={url}"
        )

    content = response.content

    if cache_file:
        cache_file.parent.mkdir(parents=True, exist_ok=True)
        cache_file.write_bytes(content)

    print(
        f"FETCH | status={response.status_code} | "
        f"size={len(content)} bytes | url={url}"
    )

    return content


def extract_book_links(html: bytes, page_url: str) -> list[str]:
    """
    Extract all book URLs from a catalogue page.
    """

    soup = BeautifulSoup(html, "html.parser")

    book_links = []

    for article in soup.select("article.product_pod"):
        link = article.select_one("h3 a")

        if link and link.get("href"):
            absolute_url = urljoin(page_url, link["href"])
            book_links.append(absolute_url)

    return book_links


def find_next_page(html: bytes, page_url: str) -> str | None:
    """
    Find the catalogue's next-page URL.
    """

    soup = BeautifulSoup(html, "html.parser")

    next_link = soup.select_one("li.next a")

    if next_link and next_link.get("href"):
        return urljoin(page_url, next_link["href"])

    return None


def discover_books() -> list[str]:
    """
    Discover book URLs from the first three catalogue pages.
    """

    current_url = BASE_URL
    all_book_urls = []
    catalogue_pages = 0

    while current_url and catalogue_pages < 3:
        catalogue_pages += 1

        print(f"\nCATALOGUE PAGE {catalogue_pages}: {current_url}")

        if catalogue_pages == 1:
            cache_file = CACHE_DIR / "catalogue-page-1.html"
        else:
            cache_file = CACHE_DIR / f"catalogue-page-{catalogue_pages}.html"

        html = fetch_page(current_url, cache_file)

        page_books = extract_book_links(
            html,
            current_url
        )

        all_book_urls.extend(page_books)

        print(f"BOOK LINKS FOUND: {len(page_books)}")

        next_url = find_next_page(
            html,
            current_url
        )

        if next_url and catalogue_pages < 3:
            sleep(REQUEST_DELAY)

        current_url = next_url

    unique_urls = list(dict.fromkeys(all_book_urls))

    print("\n--- DISCOVERY SUMMARY ---")
    print(f"catalogue_pages={catalogue_pages}")
    print(f"discovered={len(all_book_urls)}")
    print(f"unique_urls={len(unique_urls)}")

    return unique_urls


if __name__ == "__main__":
    discover_books()