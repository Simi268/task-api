from pathlib import Path
from time import sleep
from datetime import datetime, timezone
from urllib.parse import urljoin, urlparse

import requests
from bs4 import BeautifulSoup


BASE_URL = "https://books.toscrape.com/"
CACHE_DIR = Path(__file__).resolve().parent.parent / "cache"

USER_AGENT = "FlyRankInternship-A9/1.0 (+https://github.com/Simi268/task-api)"
TIMEOUT = 10
REQUEST_DELAY = 0.5


def fetch_page(url: str, cache_file: Path | None = None) -> bytes:
    """Fetch a page or return its cached copy."""

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
    """Extract all book URLs from a catalogue page."""

    soup = BeautifulSoup(html, "html.parser")

    book_links = []

    for article in soup.select("article.product_pod"):
        link = article.select_one("h3 a")

        if link and link.get("href"):
            absolute_url = urljoin(page_url, link["href"])
            book_links.append(absolute_url)

    return book_links


def find_next_page(html: bytes, page_url: str) -> str | None:
    """Find the catalogue's next-page URL."""

    soup = BeautifulSoup(html, "html.parser")

    next_link = soup.select_one("li.next a")

    if next_link and next_link.get("href"):
        return urljoin(page_url, next_link["href"])

    return None


def discover_books() -> list[tuple[str, str]]:
    """
    Discover book URLs from the first three catalogue pages.

    Returns:
        A list of (book_url, source_page) tuples.
    """

    current_url = BASE_URL
    all_books = []
    catalogue_pages = 0

    while current_url and catalogue_pages < 3:
        catalogue_pages += 1

        print(f"\nCATALOGUE PAGE {catalogue_pages}: {current_url}")

        cache_file = CACHE_DIR / f"catalogue-page-{catalogue_pages}.html"

        html = fetch_page(current_url, cache_file)

        page_books = extract_book_links(
            html,
            current_url
        )

        for book_url in page_books:
            all_books.append((book_url, current_url))

        print(f"BOOK LINKS FOUND: {len(page_books)}")

        next_url = find_next_page(
            html,
            current_url
        )

        if next_url and catalogue_pages < 3:
            sleep(REQUEST_DELAY)

        current_url = next_url

    # Remove duplicate URLs while preserving source page.
    unique_books = {}

    for book_url, source_page in all_books:
        if book_url not in unique_books:
            unique_books[book_url] = source_page

    print("\n--- DISCOVERY SUMMARY ---")
    print(f"catalogue_pages={catalogue_pages}")
    print(f"discovered={len(all_books)}")
    print(f"unique_urls={len(unique_books)}")

    return list(unique_books.items())


def extract_rating(soup: BeautifulSoup) -> str | None:
    """Extract the rating word from the star-rating class."""

    rating_element = soup.select_one("p.star-rating")

    if not rating_element:
        return None

    classes = rating_element.get("class", [])

    rating_words = {
        "One",
        "Two",
        "Three",
        "Four",
        "Five",
    }

    for class_name in classes:
        if class_name in rating_words:
            return class_name

    return None


def extract_book_record(
    html: bytes,
    product_url: str,
    source_page: str,
    fetched_at: str,
) -> dict:
    """Extract the required raw fields from a book page."""

    soup = BeautifulSoup(html, "html.parser")

    title_element = soup.select_one("div.product_main h1")
    price_element = soup.select_one("div.product_main .price_color")
    availability_element = soup.select_one(
        "div.product_main .availability"
    )

    description_element = soup.select_one(
        "#product_description + p"
    )

    title = (
        title_element.get_text(strip=True)
        if title_element
        else None
    )

    price_text = (
        price_element.get_text(strip=True)
        if price_element
        else None
    )

    availability_text = (
        availability_element.get_text(" ", strip=True)
        if availability_element
        else None
    )

    rating_text = extract_rating(soup)

    description = (
        description_element.get_text(" ", strip=True)
        if description_element
        else None
    )

    return {
        "title": title,
        "product_url": product_url,
        "price_text": price_text,
        "availability_text": availability_text,
        "rating_text": rating_text,
        "description": description,
        "source_page": source_page,
        "fetched_at": fetched_at,
    }


def fetch_book_details(
    book_url: str,
    source_page: str,
    index: int,
) -> dict:

    # Create a safe cache filename from the book URL.
    parsed = urlparse(book_url)
    filename = Path(parsed.path).parent.name + ".html"

    cache_file = CACHE_DIR / "books" / filename

    from_cache = cache_file.exists()

    html = fetch_page(
        book_url,
        cache_file,
    )

    # Only delay when an actual network request happened.
    if not from_cache:
        sleep(REQUEST_DELAY)

    fetched_at = datetime.now(timezone.utc).isoformat()

    return extract_book_record(
        html=html,
        product_url=book_url,
        source_page=source_page,
        fetched_at=fetched_at,
    )


def main():
    books = discover_books()

    records = []

    print("\n--- EXTRACTING BOOK DETAILS ---")

    for index, (book_url, source_page) in enumerate(books, start=1):

        print(
            f"\nBOOK {index}/{len(books)}: {book_url}"
        )

        record = fetch_book_details(
            book_url,
            source_page,
            index,
        )

        records.append(record)

    print("\n--- EXTRACTION SUMMARY ---")
    print(f"detail_pages={len(records)}")

    if records:
        print("\n--- SAMPLE RAW RECORD ---")

        import json

        print(
            json.dumps(
                records[0],
                indent=2,
                ensure_ascii=False,
            )
        )


if __name__ == "__main__":
    main()