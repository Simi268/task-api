# Books to Scrape — Data Scraper

A polite, cached web scraper built as part of the Backend AI Engineering assignment.

The scraper collects book data from the public **Books to Scrape** catalogue, follows catalogue pagination, caches downloaded pages, extracts book details, normalizes and validates the records, handles failures, and produces JSON output files.

---

## Features

- Catalogue pagination discovery
- Book URL discovery without hardcoding individual book URLs
- Local HTML caching
- Polite request delay of 0.5 seconds between real requests
- Custom User-Agent
- Request timeout handling
- Retry for timeouts and HTTP 5xx responses
- No retry for HTTP 403/404 responses
- Book detail extraction
- Price normalization
- Pydantic validation
- Duplicate URL protection
- Failure isolation
- Run statistics and reporting
- Idempotent output generation

---

## Target

**Website:** Books to Scrape

The scraper processes the first three catalogue pages.


## Robots Check

Requested:

`https://books.toscrape.com/robots.txt`

Result: HTTP `404 (Not Found)`.

No `robots.txt` file was found at the requested location.

## Run

From the repository root:

```bash
pip install requests beautifulsoup4 pydantic
python scraper/src/main.py




