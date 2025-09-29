# OneFlare Business Crawler

Object-oriented Selenium crawler for harvesting OneFlare business listings and exporting structured records to Excel.

## Overview
- Automates Chrome to load a OneFlare category page, capture every business profile link, and extract key fields.
- Uses dataclasses (`CrawlerSettings`, `BusinessRecord`) and a dedicated `OneFlareCrawler` class for maintainable logic.
- Provides configuration flags for wait timings, headless mode, logging verbosity, and output destination.
- Persists results through an `ExcelExporter`, producing recruiter-friendly, analysis-ready spreadsheets.

## Installation
1. Ensure **Python 3.9+**, **Google Chrome**, and a matching **chromedriver** binary are installed and accessible on your `PATH`.
2. (Optional) create a virtual environment.
3. Install project requirements:
   ```bash
   pip install selenium pandas openpyxl
   ```

## Usage
```bash
python crawl_V3.py \
    --category-url https://www.oneflare.com.au/air-conditioning \
    --output business_data.xlsx \
    --preload-delay 60 \
    --business-page-delay 3 \
    --wait-timeout 15 \
    --headless \
    --verbose
```
- Omit `--headless` to view the browser window.
- Drop `--verbose` for leaner INFO-level logs.
- Generated Excel files overwrite existing files with the same name.

## Configuration
`crawl_V3.py` consolidates selectors and delays in `CrawlerSettings`. Tweak these if OneFlare updates its layout:
- `business_links_xpath`: locator for profile links on the category page.
- `detail_css_selector`: shared selector used to find labelled rows (Website, Address, etc.).
- `preload_delay` / `business_page_delay`: coarse waits for asynchronous content.

## Data Schema
Each row in the exported workbook maps to a `BusinessRecord` with the following columns:
- `business_name`
- `jobs_completed`
- `phone_number`
- `website_url`
- `address`
- `url`

## Extending the Project
- Add new properties to `BusinessRecord` and update `_extract_detail_by_label` or dedicated helper methods to scrape them.
- Swap `ExcelExporter.export` with a CSV writer, database client, or API integration for alternative storage.
- Wrap `OneFlareCrawler` in scheduled jobs or integrate with messaging/monitoring pipelines for production use.

## Troubleshooting
- **Driver launch failure**: check that your chromedriver version matches the installed Chrome release.
- **Missing data (`N/A`)**: adjust wait times, refine selectors, or add explicit scroll/interactions for dynamic content.
- **Site blocking / rate limits**: respect OneFlare's terms; apply throttling, randomised delays, or proxy rotation for larger crawls.

## Contributing
Feel free to fork and iterate on the crawler—pull requests that improve resilience, add tests, or expand data coverage are welcome.
