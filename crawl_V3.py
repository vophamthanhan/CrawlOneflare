"""Crawl OneFlare category pages and export business details."""

import argparse
import logging
import re
import time
from dataclasses import dataclass, asdict
from typing import Dict, Iterable, List

import pandas as pd
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException, TimeoutException, WebDriverException
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait


@dataclass
class CrawlerSettings:
    """Configuration for crawling a OneFlare category page."""

    category_url: str
    preload_delay: float = 60.0
    business_page_delay: float = 3.0
    output_file: str = "business_data.xlsx"
    wait_timeout: float = 15.0
    business_links_xpath: str = "//section[4]//li/h3/a"
    name_xpath: str = "//h1"
    jobs_xpath: str = "//main/div/section[1]/section/section[1]/p"
    phone_xpath: str = "//a[@data-tooltip-content='Click to show number']"
    detail_css_selector: str = ".sc-906e671e-5.bQwqNJ"

    def __post_init__(self) -> None:
        if not self.category_url:
            raise ValueError("category_url must not be empty.")


@dataclass
class BusinessRecord:
    """Structured representation of a business profile."""

    business_name: str
    jobs_completed: str
    phone_number: str
    website_url: str
    address: str
    url: str

    def to_dict(self) -> Dict[str, str]:
        """Convert the record to a plain dictionary for serialization."""
        return asdict(self)


class OneFlareCrawler:
    """Class-based crawler responsible for harvesting business data from OneFlare."""

    def __init__(self, driver: WebDriver, settings: CrawlerSettings) -> None:
        self.driver = driver
        self.settings = settings
        self.wait = WebDriverWait(driver, settings.wait_timeout)

    def run(self) -> List[BusinessRecord]:
        """Execute the crawl and return a collection of business records."""
        self._load_category_page()
        links = self._collect_business_links()
        logging.info("Found %d business links.", len(links))
        records: List[BusinessRecord] = []
        for url in links:
            try:
                record = self._extract_business_data(url)
                records.append(record)
            except Exception as exc:
                logging.exception("Failed to process %s: %s", url, exc)
        return records

    def _load_category_page(self) -> None:
        logging.info("Loading category page %s", self.settings.category_url)
        self.driver.get(self.settings.category_url)
        if self.settings.preload_delay > 0:
            logging.debug("Waiting %.1f seconds for category page assets.", self.settings.preload_delay)
            time.sleep(self.settings.preload_delay)

    def _collect_business_links(self) -> List[str]:
        try:
            self.wait.until(EC.presence_of_all_elements_located((By.XPATH, self.settings.business_links_xpath)))
        except TimeoutException:
            logging.warning("Timeout while waiting for business links.")
        links = self.driver.find_elements(By.XPATH, self.settings.business_links_xpath)
        hrefs: List[str] = []
        for link in links:
            href = link.get_attribute("href")
            if href:
                hrefs.append(href)
        return hrefs

    def _extract_business_data(self, url: str) -> BusinessRecord:
        logging.info("Scraping business details from %s", url)
        self.driver.get(url)
        try:
            self.wait.until(EC.presence_of_element_located((By.XPATH, self.settings.name_xpath)))
        except TimeoutException:
            logging.warning("Business name field did not load for %s.", url)
        if self.settings.business_page_delay > 0:
            logging.debug("Waiting %.1f seconds for business page details.", self.settings.business_page_delay)
            time.sleep(self.settings.business_page_delay)
        name = self._safe_get_text(By.XPATH, self.settings.name_xpath)
        jobs = self._extract_jobs_completed()
        phone = self._extract_phone_number()
        website = self._extract_detail_by_label("Website:")
        address = self._extract_detail_by_label("Address:")
        return BusinessRecord(
            business_name=name,
            jobs_completed=jobs,
            phone_number=phone,
            website_url=website,
            address=address,
            url=url,
        )

    def _safe_get_text(self, by: str, locator: str, default: str = "N/A") -> str:
        try:
            element = self.driver.find_element(by, locator)
            text = element.text.strip()
            return text if text else default
        except NoSuchElementException:
            return default

    def _extract_jobs_completed(self) -> str:
        text = self._safe_get_text(By.XPATH, self.settings.jobs_xpath)
        if text == "N/A":
            return text
        match = re.search(r"\d+", text.replace(",", ""))
        return match.group() if match else "N/A"

    def _extract_phone_number(self) -> str:
        try:
            phone_element = self.driver.find_element(By.XPATH, self.settings.phone_xpath)
            try:
                phone_element.click()
                time.sleep(0.5)
            except Exception:
                logging.debug("Phone element click failed; returning visible text.")
            text = phone_element.text.strip()
            return text if text else "N/A"
        except NoSuchElementException:
            return "N/A"

    def _extract_detail_by_label(self, label: str) -> str:
        elements = self.driver.find_elements(By.CSS_SELECTOR, self.settings.detail_css_selector)
        for element in elements:
            raw_text = element.text.strip()
            if label in raw_text:
                value = raw_text.split(label, 1)[1].strip()
                return value if value else "N/A"
        return "N/A"


class ExcelExporter:
    """Responsible for serializing business records to Excel."""

    @staticmethod
    def export(records: Iterable[BusinessRecord], output_file: str) -> None:
        rows = [record.to_dict() for record in records]
        columns = list(BusinessRecord.__dataclass_fields__.keys())
        df = pd.DataFrame(rows, columns=columns)
        df.to_excel(output_file, index=False)
        logging.info("Saved %d records to %s", len(rows), output_file)


def create_chrome_driver(headless: bool = False) -> WebDriver:
    """Build a Chrome WebDriver with optional headless mode."""
    options = webdriver.ChromeOptions()
    if headless:
        options.add_argument("--headless=new")
    options.add_argument("--start-maximized")
    driver = webdriver.Chrome(options=options)
    try:
        driver.maximize_window()
    except WebDriverException:
        logging.debug("Unable to maximize window; continuing with default size.")
    return driver


def configure_logging(verbose: bool) -> None:
    """Configure global logging behavior."""
    level = logging.DEBUG if verbose else logging.INFO
    logging.basicConfig(level=level, format="%(asctime)s | %(levelname)s | %(message)s")


def parse_args() -> argparse.Namespace:
    """Parse command-line arguments for the crawler."""
    parser = argparse.ArgumentParser(description="Crawl OneFlare business listings.")
    parser.add_argument("--category-url", default="https://www.oneflare.com.au/air-conditioning", help="OneFlare category URL to crawl.")
    parser.add_argument("--output", default="business_data.xlsx", help="Destination Excel file.")
    parser.add_argument("--preload-delay", type=float, default=60.0, help="Seconds to wait after loading the category page.")
    parser.add_argument("--business-page-delay", type=float, default=3.0, help="Seconds to wait after loading each business page.")
    parser.add_argument("--wait-timeout", type=float, default=15.0, help="Maximum seconds to wait for key elements.")
    parser.add_argument("--headless", action="store_true", help="Run Chrome in headless mode.")
    parser.add_argument("--verbose", action="store_true", help="Enable debug logging.")
    return parser.parse_args()


def main() -> None:
    """Entry point for running the crawler from the command line."""
    args = parse_args()
    configure_logging(args.verbose)
    settings = CrawlerSettings(
        category_url=args.category_url,
        preload_delay=args.preload_delay,
        business_page_delay=args.business_page_delay,
        output_file=args.output,
        wait_timeout=args.wait_timeout,
    )

    try:
        driver = create_chrome_driver(headless=args.headless)
    except WebDriverException as exc:
        logging.exception("Could not initialize the Chrome WebDriver: %s", exc)
        raise

    crawler = OneFlareCrawler(driver, settings)
    try:
        records = crawler.run()
    finally:
        driver.quit()

    ExcelExporter.export(records, settings.output_file)
    if not records:
        logging.warning("No business records collected. Inspect selectors or delays for adjustments.")


if __name__ == "__main__":
    main()
