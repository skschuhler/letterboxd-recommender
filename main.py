from scraper.utils import *
import pandas as pd
import asyncio

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
}

TIMEOUT = 5

# Running the asyncio event loop
async def main():
    # Read the list of usernames from the CSV
    users = pd.read_csv("C:/Users/sarah/Documents/GitHub/letterboxd-scraper/skipped_users.csv")['user'].to_list()

    # Start scraping users concurrently
    await scrape_multiple_users_concurrently(users)

if __name__ == "__main__":
    asyncio.run(main())