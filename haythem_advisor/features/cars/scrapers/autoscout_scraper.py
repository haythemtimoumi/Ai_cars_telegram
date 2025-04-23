import re
import time
from datetime import datetime
from typing import List, Dict
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options

from .car_base_scraper import BaseScraper

class AutoScout24Scraper(BaseScraper):
    def __init__(self, chrome_binary: str, chromedriver_path: str):
        super().__init__(source="autoscout24")
        self.chrome_binary = chrome_binary
        self.chromedriver_path = chromedriver_path

    def scrape(self) -> List[Dict]:
        listings = []
        seen_ids = set()
        page = 1

        base_url = (
            "https://www.autoscout24.com/lst?atype=C&cid=2972657"
            "&cy=D%2CA%2CB%2CE%2CF%2CI%2CL%2CNL&damaged_listing=exclude"
            "&desc=0&page={}&powertype=kw&search_id=2cv7ptp0zzl&sort=standard"
            "&source=listpage_pagination&ustate=N%2CU"
        )

        options = Options()
        options.binary_location = self.chrome_binary
        options.add_argument("--headless")
        options.add_argument("--disable-gpu")
        options.add_argument("--window-size=1920,1080")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36")

        service = Service(executable_path=self.chromedriver_path)
        # 🧠 Force ChromeDriver to use version_main=135 (for Docker compatibility)
        driver = webdriver.Chrome(service=service, options=options)

        while True:
            print(f"[i] Scraping page {page}...")
            driver.get(base_url.format(page))
            time.sleep(4)

            cards = driver.find_elements(By.CSS_SELECTOR, 'article[data-testid="list-item"]')
            print(f"[i] Found {len(cards)} cards on page {page}")
            if not cards:
                break

            for idx, card in enumerate(cards):
                try:
                    url = card.find_element(By.CSS_SELECTOR, 'a').get_attribute('href').strip()
                    listing_id = url.split("-")[-1]
                    if listing_id in seen_ids:
                        continue
                    seen_ids.add(listing_id)

                    title = card.find_element(By.CSS_SELECTOR, 'h2').text.strip()
                    brand, model = self._extract_brand_model(title)

                    price_text = card.find_element(By.CSS_SELECTOR, 'p[class*="PriceAndSeals_current_price"]').text
                    price = int(re.sub(r"[^\d]", "", price_text))

                    mileage_text = card.find_element(By.CSS_SELECTOR, 'span[data-testid*="mileage_road"]').text
                    mileage = int(re.sub(r"[^\d]", "", mileage_text))

                    gearbox = card.find_element(By.CSS_SELECTOR, 'span[data-testid*="transmission"]').text.strip().lower()

                    first_reg = card.find_element(By.CSS_SELECTOR, 'span[data-testid*="calendar"]').text.strip()
                    year = int(first_reg.split("/")[-1]) if "/" in first_reg and first_reg.split("/")[-1].isdigit() else None

                    fuel_type = card.find_element(By.CSS_SELECTOR, 'span[data-testid*="gas_pump"]').text.strip().lower()

                    power_kw = self._extract_kw(card)

                    location_text = card.find_element(By.CSS_SELECTOR, 'span[data-testid="sellerinfo-address"]').text
                    city = location_text.split()[-1]

                    listings.append({
                        "listing_id": listing_id,
                        "brand": brand,
                        "model": model,
                        "year": year,
                        "mileage": mileage,
                        "fuel_type": fuel_type,
                        "gearbox": gearbox,
                        "power_kw": power_kw,
                        "price": price,
                        "currency": "EUR",
                        "location": {
                            "country": "Germany",
                            "city": city
                        },
                        "source": self.source,
                        "scraped_at": datetime.utcnow().isoformat(),
                        "url": url
                    })

                except Exception as e:
                    print(f"[!] Card #{idx + 1} - Error parsing card: {e}")
                    continue

            page += 1

        driver.quit()
        return listings

    def _extract_brand_model(self, title: str):
        parts = title.split()
        brand = parts[0] if parts else "unknown"
        model = parts[1] if len(parts) > 1 else "unknown"
        return brand.lower(), model.lower()

    def _extract_kw(self, card) -> int:
        try:
            power = card.find_element(By.CSS_SELECTOR, 'span[data-testid*="speedometer"]').text
            kw_match = re.search(r"(\d+)\s?kW", power)
            return int(kw_match.group(1)) if kw_match else None
        except:
            return None


def scrape_autoscout24(chrome_binary=None, chromedriver_path=None, debug=False):
    import shutil
    chrome_binary = chrome_binary or shutil.which("google-chrome")
    chromedriver_path = chromedriver_path or shutil.which("chromedriver")

    if not chrome_binary:
        raise EnvironmentError("Chrome binary not found.")
    if not chromedriver_path:
        raise EnvironmentError("ChromeDriver not found.")

    if debug:
        print(f"[DEBUG] chrome_binary: {chrome_binary}")
        print(f"[DEBUG] chromedriver_path: {chromedriver_path}")

    scraper = AutoScout24Scraper(chrome_binary=chrome_binary, chromedriver_path=chromedriver_path)
    return scraper.scrape()
