from pathlib import Path
from time import sleep
from datetime import datetime, timezone
from urllib.parse import urljoin, urlparse

import json
import re

import requests
from bs4 import BeautifulSoup
from pydantic import BaseModel, HttpUrl, ValidationError


# ============================================================
# Configuration
# ============================================================

BASE_URL = "https://books.toscrape.com/"

SCRAPER_DIR = Path(__file__).resolve().parent.parent
CACHE_DIR = SCRAPER_DIR / "cache"
OUTPUT_DIR = SCRAPER_DIR / "output"

BOOKS_FILE = OUTPUT_DIR / "books.json"
ERRORS_FILE = OUTPUT_DIR / "errors.json"

USER_AGENT = (
    "FlyRankInternship-A9/1.0 "
    "(+https://github.com/Simi268/task-api)"
)

TIMEOUT = 10
REQUEST_DELAY = 0.5


# ============================================================
# Pydantic Schema
# ============================================================

class BookRecord(BaseModel):
    title: str
    product_url: HttpUrl
    price_text: str
    price_gbp: float
    availability_text: str
    rating_text: str | None
    description: str | None
    source_page: HttpUrl
    fetched_at: str


# ============================================================
# Fetching and Caching
# ============================================================

def fetch_page(
    url: str,
    cache_file: Path | None = None
) -> bytes:
    """
    Fetch a page from the website or return its cached copy.
    """

    if cache_file and cache_file.exists():
        content = cache_file.read_bytes()

        print(
            f"CACHE HIT | {url} | "
            f"size={len(content)} bytes"
        )

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
            f"FETCH FAILED | "
            f"status={response.status_code} | "
            f"url={url}"
        )

    content = response.content

    if cache_file:
        cache_file.parent.mkdir(
            parents=True,
            exist_ok=True
        )

        cache_file.write_bytes(content)

    print(
        f"FETCH | "
        f"status={response.status_code} | "
        f"size={len(content)} bytes | "
        f"url={url}"
    )

    return content


# ============================================================
# Catalogue Discovery
# ============================================================

def extract_book_links(
    html: bytes,
    page_url: str
) -> list[str]:
    """
    Extract all book URLs from a catalogue page.
    """

    soup = BeautifulSoup(
        html,
        "html.parser"
    )

    book_links = []

    for article in soup.select(
        "article.product_pod"
    ):
        link = article.select_one(
            "h3 a"
        )

        if link and link.get("href"):
            absolute_url = urljoin(
                page_url,
                link["href"]
            )

            book_links.append(
                absolute_url
            )

    return book_links


def find_next_page(
    html: bytes,
    page_url: str
) -> str | None:
    """
    Find the catalogue's next-page URL.
    """

    soup = BeautifulSoup(
        html,
        "html.parser"
    )

    next_link = soup.select_one(
        "li.next a"
    )

    if next_link and next_link.get("href"):
        return urljoin(
            page_url,
            next_link["href"]
        )

    return None


def discover_books() -> list[tuple[str, str]]:
    """
    Discover book URLs from the first three
    catalogue pages.

    Returns:
        A list of (book_url, source_page) tuples.
    """

    current_url = BASE_URL

    all_books = []

    catalogue_pages = 0

    while (
        current_url
        and catalogue_pages < 3
    ):
        catalogue_pages += 1

        print(
            f"\nCATALOGUE PAGE "
            f"{catalogue_pages}: "
            f"{current_url}"
        )

        cache_file = (
            CACHE_DIR
            / f"catalogue-page-{catalogue_pages}.html"
        )

        html = fetch_page(
            current_url,
            cache_file
        )

        page_books = extract_book_links(
            html,
            current_url
        )

        for book_url in page_books:
            all_books.append(
                (
                    book_url,
                    current_url
                )
            )

        print(
            f"BOOK LINKS FOUND: "
            f"{len(page_books)}"
        )

        next_url = find_next_page(
            html,
            current_url
        )

        if (
            next_url
            and catalogue_pages < 3
        ):
            sleep(REQUEST_DELAY)

        current_url = next_url

    # Remove duplicate URLs while preserving
    # the first source page.
    unique_books = {}

    for book_url, source_page in all_books:
        if book_url not in unique_books:
            unique_books[book_url] = source_page

    print(
        "\n--- DISCOVERY SUMMARY ---"
    )

    print(
        f"catalogue_pages="
        f"{catalogue_pages}"
    )

    print(
        f"discovered="
        f"{len(all_books)}"
    )

    print(
        f"unique_urls="
        f"{len(unique_books)}"
    )

    return list(
        unique_books.items()
    )


# ============================================================
# Book Field Extraction
# ============================================================

def extract_rating(
    soup: BeautifulSoup
) -> str | None:
    """
    Extract the rating word from the
    star-rating class.
    """

    rating_element = soup.select_one(
        "p.star-rating"
    )

    if not rating_element:
        return None

    classes = rating_element.get(
        "class",
        []
    )

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
    """
    Extract the required raw fields
    from a book page.
    """

    soup = BeautifulSoup(
        html,
        "html.parser"
    )

    title_element = soup.select_one(
        "div.product_main h1"
    )

    price_element = soup.select_one(
        "div.product_main .price_color"
    )

    availability_element = soup.select_one(
        "div.product_main .availability"
    )

    description_element = soup.select_one(
        "#product_description + p"
    )

    title = (
        title_element.get_text(
            strip=True
        )
        if title_element
        else None
    )

    price_text = (
        price_element.get_text(
            strip=True
        )
        if price_element
        else None
    )

    availability_text = (
        availability_element.get_text(
            " ",
            strip=True
        )
        if availability_element
        else None
    )

    rating_text = extract_rating(
        soup
    )

    description = (
        description_element.get_text(
            " ",
            strip=True
        )
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


# ============================================================
# Fetch Individual Book Details
# ============================================================

def fetch_book_details(
    book_url: str,
    source_page: str,
) -> dict:
    """
    Fetch and extract one book's details.
    """

    parsed = urlparse(
        book_url
    )

    # Example:
    # /catalogue/a-light-in-the-attic_1000/index.html
    #
    # Parent directory:
    # a-light-in-the-attic_1000
    book_name = (
        Path(parsed.path)
        .parent
        .name
    )

    cache_file = (
        CACHE_DIR
        / "books"
        / f"{book_name}.html"
    )

    from_cache = cache_file.exists()

    html = fetch_page(
        book_url,
        cache_file
    )

    # Delay only after an actual
    # network request.
    if not from_cache:
        sleep(REQUEST_DELAY)

    fetched_at = (
        datetime.now(
            timezone.utc
        ).isoformat()
    )

    return extract_book_record(
        html=html,
        product_url=book_url,
        source_page=source_page,
        fetched_at=fetched_at,
    )


# ============================================================
# Stage 4 — Price Normalization
# ============================================================

def normalize_price(
    price_text: str
) -> float:
    """
    Convert a price such as '£51.77'
    into the numeric value 51.77.
    """

    match = re.search(
        r"[\d.]+",
        price_text
    )

    if not match:
        raise ValueError(
            f"Could not normalize price: "
            f"{price_text}"
        )

    return float(
        match.group()
    )


def normalize_record(
    record: dict
) -> dict:
    """
    Convert a raw scraped record into
    the normalized schema.
    """

    normalized = record.copy()

    normalized["price_gbp"] = (
        normalize_price(
            record["price_text"]
        )
    )

    return normalized


# ============================================================
# Stage 4 — Validation and Storage
# ============================================================

def validate_and_store(
    records: list[dict]
):
    """
    Validate normalized records and store
    valid and invalid results.
    """

    OUTPUT_DIR.mkdir(
        parents=True,
        exist_ok=True
    )

    valid_records = []
    invalid_records = []

    seen_urls = set()

    for record in records:

        try:
            # Normalize raw record.
            normalized = normalize_record(
                record
            )

            # Validate using Pydantic.
            validated = (
                BookRecord.model_validate(
                    normalized
                )
            )

            product_url = str(
                validated.product_url
            )

            # Prevent duplicate records.
            if product_url in seen_urls:
                continue

            seen_urls.add(
                product_url
            )

            valid_records.append(
                validated.model_dump(
                    mode="json"
                )
            )

        except (
            ValidationError,
            ValueError
        ) as exc:

            invalid_records.append(
                {
                    "record": record,
                    "reason": str(exc),
                }
            )

    # Store valid records.
    BOOKS_FILE.write_text(
        json.dumps(
            valid_records,
            indent=2,
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )

    # Store invalid records.
    ERRORS_FILE.write_text(
        json.dumps(
            invalid_records,
            indent=2,
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )

    print(
        "\n--- VALIDATION SUMMARY ---"
    )

    print(
        f"valid_records="
        f"{len(valid_records)}"
    )

    print(
        f"invalid_records="
        f"{len(invalid_records)}"
    )


# ============================================================
# Main Pipeline
# ============================================================

def main():

    # --------------------------------------------------------
    # Stage 2
    # Discover the first three catalogue pages.
    # --------------------------------------------------------

    books = discover_books()

    records = []

    # --------------------------------------------------------
    # Stage 3
    # Fetch and extract all book details.
    # --------------------------------------------------------

    print(
        "\n--- EXTRACTING BOOK DETAILS ---"
    )

    for index, (
        book_url,
        source_page
    ) in enumerate(
        books,
        start=1
    ):

        print(
            f"\nBOOK "
            f"{index}/{len(books)}: "
            f"{book_url}"
        )

        record = fetch_book_details(
            book_url,
            source_page,
        )

        records.append(
            record
        )

    # --------------------------------------------------------
    # Stage 3 Checkpoint
    # --------------------------------------------------------

    print(
        "\n--- EXTRACTION SUMMARY ---"
    )

    print(
        f"detail_pages="
        f"{len(records)}"
    )

    if records:

        print(
            "\n--- SAMPLE RAW RECORD ---"
        )

        print(
            json.dumps(
                records[0],
                indent=2,
                ensure_ascii=False,
            )
        )

    # --------------------------------------------------------
    # Stage 4
    # Normalize, validate, and store.
    # --------------------------------------------------------

    validate_and_store(
        records
    )


# ============================================================
# Entry Point
# ============================================================

if __name__ == "__main__":
    main()