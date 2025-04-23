import os
import re
import random
import time
from datetime import datetime, timezone
from typing import List, Dict
from bs4 import BeautifulSoup
import undetected_chromedriver as uc

class GumtreeScraper:
    def __init__(self, chrome_binary: str = None, chromedriver_path: str = None):
        self.chrome_binary = chrome_binary or "/usr/bin/google-chrome"
        self.chromedriver_path = chromedriver_path or "/usr/local/bin/chromedriver"
        self.base_url = "https://www.gumtree.com/search?search_category=cars&search_location=uk&page={}"
        self.source = "gumtree"
        self.user_agents = [
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
            "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"
        ]

    def _setup_driver(self):
        options = uc.ChromeOptions()
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--disable-gpu")
        options.add_argument("--window-size=1920,1080")
        options.add_argument(f"--user-agent={random.choice(self.user_agents)}")
        options.add_argument("--disable-blink-features=AutomationControlled")

        if os.getenv("HEADLESS", "false").lower() == "true":
            options.add_argument("--headless=new")

        driver = uc.Chrome(
            options=options,
            browser_executable_path=self.chrome_binary,
            driver_executable_path=self.chromedriver_path,
            headless=False,
            version_main=122
        )
        
        # Execute stealth scripts
        driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
        return driver

    def _random_delay(self, min_sec=2, max_sec=5):
        """Random delay between actions to mimic human behavior"""
        time.sleep(random.uniform(min_sec, max_sec))

    def _extract_listing_id(self, href: str):
        match = re.search(r'/([0-9]+)$', href)
        return match.group(1) if match else None

    def _parse_price(self, price_text: str):
        return int(re.sub(r"[^\d]", "", price_text))

    def _parse_mileage(self, mileage_text: str):
        return int(re.sub(r"[^\d]", "", mileage_text))

    def _extract_brand_model(self, title: str):
        parts = title.strip().split()
        if parts and re.match(r"^\d{4}$", parts[0]):
            brand = parts[1] if len(parts) > 1 else ""
            model = " ".join(parts[2:4]) if len(parts) > 3 else parts[2] if len(parts) > 2 else ""
        else:
            brand = parts[0] if parts else ""
            model = " ".join(parts[1:3]) if len(parts) > 2 else parts[1] if len(parts) > 1 else ""
        return brand, model

    def _check_for_blocking(self, driver):
        """Check if we're being blocked by Gumtree"""
        try:
            if "sorry" in driver.title.lower():
                return True
            if "blocked" in driver.page_source.lower():
                return True
            return False
        except:
            return False

    def scrape(self) -> List[Dict]:
        print("\U0001F680 Starting Gumtree scrape...")
        driver = self._setup_driver()
        listings = []
        page = 1

        try:
            while True:
                url = self.base_url.format(page)
                print(f"\n\U0001F50E Scraping page {page}: {url}")
                
                driver.get(url)
                self._random_delay(3, 7)  # Longer random delay
                
                # Check if we're blocked
                if self._check_for_blocking(driver):
                    print("\u26A0\ufe0f Blocking detected! Trying to recover...")
                    driver.delete_all_cookies()
                    time.sleep(random.uniform(10, 15))  # Longer wait when blocked
                    driver.refresh()
                    continue
                
                if "cars-vans-motorbikes/cars" in driver.current_url:
                    print("\u26A0\ufe0f Reached non-paginated landing page — ending scrape.")
                    break

                soup = BeautifulSoup(driver.page_source, "html.parser")
                articles = soup.select("article[data-q='search-result']")

                if not articles:
                    print("\u26A0\ufe0f No listings found — maybe blocked or real end.")
                    break

                print(f"\u2705 Found {len(articles)} listings on page {page}.")

                for article in articles:
                    try:
                        title_elem = article.select_one("a[data-q='search-result-anchor']")
                        title_text_elem = article.select_one("div[data-q='tile-title']")
                        if not title_elem or not title_text_elem:
                            print("\u26A0\ufe0f Skipping: title or anchor missing.")
                            continue

                        title_text = title_text_elem.get_text(strip=True)
                        listing_id = self._extract_listing_id(title_elem['href'])
                        brand, model = self._extract_brand_model(title_text)

                        year = article.select_one("span[data-q='motors-year']")
                        mileage = article.select_one("span[data-q='motors-mileage']")
                        fuel = article.select_one("span[data-q='motors-fuel-type']")
                        price = article.select_one("div[data-testid='price']")
                        location = article.select_one("div[data-q='tile-location']")

                        if not (year and mileage and fuel and price and location):
                            continue

                        listings.append({
                            "listing_id": listing_id,
                            "brand": brand,
                            "model": model,
                            "year": int(year.text.strip()),
                            "mileage": self._parse_mileage(mileage.text),
                            "fuel_type": fuel.text.strip(),
                            "gearbox": "Automatic" if "Automatic" in title_text else "Manual",
                            "power_kw": None,
                            "price": self._parse_price(price.text),
                            "currency": "GBP",
                            "location": {"raw": location.text.strip()},
                            "source": self.source,
                            "scraped_at": datetime.now(timezone.utc),
                            "url": "https://www.gumtree.com" + title_elem['href']
                        })

                    except Exception as e:
                        print(f"\u274C Error parsing listing: {e}")

                page += 1
                self._random_delay(5, 10)  # Longer random delay between pages

        finally:
            driver.quit()
            print(f"\n\u2705 Scraped {len(listings)} total listings.")
            return listings