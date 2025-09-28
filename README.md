# Crawl Oneflare

This project provides a Python script that uses Selenium WebDriver to scrape business listings from Oneflare's air-conditioning category and store the results in an Excel workbook.

## Features
- Launches a Chrome session and loads the chosen Oneflare category page.
- Collects every business profile link discovered on the listing page.
- Visits each profile to capture the business name, jobs completed, phone number, website URL, address, and profile URL.
- Exports the gathered records to `business_data.xlsx` for further analysis.

## Requirements
- Python 3.9 or newer.
- Google Chrome installed on the machine running the scraper.
- A ChromeDriver binary that matches your Chrome version and is available on your system `PATH`.
- Python packages: `selenium`, `pandas`, and `openpyxl` (used by `pandas` to write Excel files).

## Setup
1. Clone this repository or download the project files.
2. (Optional) Create and activate a virtual environment for the project.
3. Install the Python dependencies:
   ```bash
   pip install selenium pandas openpyxl
   ```
4. Ensure the ChromeDriver executable is accessible (either in the project folder or on the `PATH`).

## Usage
1. Review the `category_url` value near the top of `crawl_V2.py` and change it if you want to target a different Oneflare category.
2. Run the scraper from the project directory:
   ```bash
   python crawl_V2.py
   ```
3. The script waits up to 60 seconds for the initial category page to load, gathers profile links, crawls each business page, and writes the output to `business_data.xlsx`.
4. When the run is complete, the Excel file will be available in the project folder and the browser session will close automatically.

## Customisation
- Adjust the `time.sleep` values if your network is slow or if Oneflare changes how the content loads.
- Update the XPath or class-based selectors in `crawl_V2.py` if Oneflare modifies its page structure.
- Extend the `extract_data` function to scrape additional fields as required.

## Troubleshooting
- **WebDriver errors**: Confirm that ChromeDriver matches your Chrome version and that both are accessible to the script.
- **Missing fields (`"N/A"`)**: Some profiles hide data behind interactions or do not include it; you may need to update selectors or add extra waits for dynamic content.
- **Rate limiting or blocking**: Respect Oneflare's terms of use; consider adding longer delays or rotating IPs if you plan to run large crawls.
