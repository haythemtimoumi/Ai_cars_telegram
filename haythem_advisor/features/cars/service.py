import os
import sys
import traceback
from features.cars.scrapers.autoscout_scraper import scrape_autoscout24
from features.cars.scrapers.gumtree_scraper import GumtreeScraper
from features.cars.models import CarListing
from core.database import SessionLocal
from sqlalchemy.dialects.postgresql import insert as pg_insert

# Optional: suppress print output unless DEBUG=1
if not os.getenv("DEBUG"):
    sys.stdout = open(os.devnull, 'w')

def scrape_all_cars(chrome_binary: str = None, chromedriver_path: str = None, debug: bool = False):
    if debug:
        print("[i] 🚘 Starting car scraping process...")

    chrome_binary = chrome_binary or os.getenv("CHROME_BINARY", "/usr/bin/google-chrome")
    chromedriver_path = chromedriver_path or os.getenv("CHROMEDRIVER_PATH", "/usr/local/bin/chromedriver")

    if debug:
        print(f"[LOG] CHROME_BINARY={chrome_binary} | CHROMEDRIVER_PATH={chromedriver_path} | HEADLESS={os.getenv('HEADLESS')}")

    all_listings = []

    # === Scrape AutoScout24 ===
    try:
        autoscout24_listings = scrape_autoscout24(chrome_binary, chromedriver_path, debug=debug)
        all_listings.extend(autoscout24_listings)
        if debug:
            print(f"[✓] Scraped {len(autoscout24_listings)} listings from AutoScout24.")
    except Exception as e:
        print("[❌] Exception occurred while scraping AutoScout24:", file=sys.stderr)
        traceback.print_exception(type(e), e, e.__traceback__, file=sys.stderr)

    # === Scrape Gumtree ===
    try:
        print("[LOG] Attempting to scrape Gumtree...")
        gumtree_scraper = GumtreeScraper(chrome_binary, chromedriver_path)
        gumtree_listings = gumtree_scraper.scrape()
        all_listings.extend(gumtree_listings)
        if debug:
            print(f"[✓] Scraped {len(gumtree_listings)} listings from Gumtree.")
    except Exception as e:
        print("[❌] Exception occurred while scraping Gumtree:", file=sys.stderr)
        traceback.print_exception(type(e), e, e.__traceback__, file=sys.stderr)

    if debug:
        print(f"[i] Total combined listings: {len(all_listings)}")

    # === Save to database ===
    db = SessionLocal()
    try:
        if all_listings:
            stmt = pg_insert(CarListing).values(all_listings)
            stmt = stmt.on_conflict_do_nothing(index_elements=['listing_id'])
            result = db.execute(stmt)
            db.commit()
            added = result.rowcount
            if debug:
                print(f"[✓] Saved {added} new listings to the database.")
        else:
            if debug:
                print("[i] No listings to save.")
    except Exception as e:
        db.rollback()
        print("[❌] Failed to save listings to the database.", file=sys.stderr)
        traceback.print_exception(type(e), e, e.__traceback__, file=sys.stderr)
    finally:
        db.close()

    return all_listings
