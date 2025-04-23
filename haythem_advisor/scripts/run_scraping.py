import os
import sys
import traceback

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from features.cars.service import scrape_all_cars
from features.cars.models import Base
from core.database import engine

def log_info(msg):
    print(f"[INFO] {msg}")

def log_error(msg, err=None):
    print(f"[ERROR] {msg}")
    if err:
        traceback.print_exception(type(err), err, err.__traceback__)

if __name__ == "__main__":
    log_info("🚀 Starting full scraping process...")

    # ✅ Ensure the car_listings table exists
    log_info("🔨 Ensuring car_listings table exists...")
    Base.metadata.create_all(bind=engine)

    # Get Chrome paths
    chrome_binary = os.getenv("CHROME_BINARY", "/usr/bin/google-chrome")
    chromedriver_path = os.getenv("CHROMEDRIVER_PATH", "/usr/local/bin/chromedriver")

    try:
        log_info("🔧 Launching scrape_all_cars with debug mode OFF")
        listings = scrape_all_cars(chrome_binary, chromedriver_path, debug=False)

        if listings:
            log_info(f"✅ Scraped {len(listings)} listings successfully!")
        else:
            log_info("⚠️ Scraping completed but returned 0 listings.")

    except Exception as e:
        log_error("❌ An error occurred during the scraping process", e)

    log_info("🏁 Scraping process completed.")
