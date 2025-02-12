import aiohttp
import asyncio
from bs4 import BeautifulSoup
from typing import Optional, List, Dict
import time
import random
import pandas as pd

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
}

TIMEOUT = 5

# Function to simulate a small delay between requests
async def async_sleep(seconds: float):
    await asyncio.sleep(seconds)

async def fetch_with_backoff(url: str, retries: int = 5) -> Optional[str]:
    """Fetch data with exponential backoff to handle rate-limiting."""
    attempt = 0
    errored = []
    while attempt < retries:
        async with aiohttp.ClientSession() as session:
            try:
                async with session.get(url, headers=HEADERS, timeout=TIMEOUT) as response:
                    print(f"Fetching {url} - Status code: {response.status}")
                    if response.status == 200:
                        return await response.text()  # Return HTML content if successful
                    elif response.status == 429:  # Handle rate-limiting
                        print(f"Rate-limited on {url}, retrying after backoff...")
                        wait_time = random.uniform(1, 3) * (2 ** attempt)  # Exponential backoff
                        print(f"Waiting for {wait_time:.2f} seconds...")
                        await async_sleep(wait_time)  # Wait before retrying
                        attempt += 1
                    else:
                        print(f"Failed to fetch {url}, status: {response.status}")
                        errored.append(url)
                        return None
            except Exception as e:
                print(f"Error fetching {url}: {e}")
                return None
    print(f"Max retries reached for {url}. Skipping.")
    print(errored)
    return None
'''
# Async function to extract the review content
async def extract_review(URL: str) -> Optional[str]:
    """Extract the review content from a given film page URL asynchronously."""
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(URL, headers=HEADERS) as response:
                if response.status == 200:
                    soup = BeautifulSoup(await response.text(), 'html.parser')

                    # Look for a spoiler notice and extract the review text if present
                    spoiler_notice = soup.find("p", string=lambda x: x and "This review may contain spoilers." in x)
                    if spoiler_notice:
                        review_section = spoiler_notice.find_next("div")
                        if review_section:
                            review_paragraphs = review_section.find_all("p")
                            return " ".join(paragraph.text.strip() for paragraph in review_paragraphs)

                    review_section = soup.find("div", class_="review body-text -prose -hero -loose")
                    if review_section:
                        review_paragraphs = review_section.find_all("p")
                        return " ".join(paragraph.text.strip() for paragraph in review_paragraphs)

                elif response.status == 429:
                    print(f"Rate-limited: {URL} - Waiting for 30 seconds")
                    await async_sleep(30)  # Retry after 30 seconds
                    return await extract_review(URL)  # Retry the request

                else:
                    print(f"Failed to fetch review from {URL}, status code: {response.status}")
                    return None

    except Exception as e:
        print(f"Error fetching review from {URL}: {e}")
        return None
  
# Async function to extract the tags from the review page
async def extract_tags(URL: str) -> Optional[List[str]]:
    """Extract the review tags from a given film page URL asynchronously."""
    html = await fetch_with_backoff(URL)
    if not html:
        return []

    soup = BeautifulSoup(html, 'html.parser')

    tags_section = soup.find("ul", class_="tags")
    if tags_section:
        tag_items = tags_section.find_all("li")
        return [item.find("a").text.strip() for item in tag_items]

    return []
'''
# Async function to fetch pages (replacing requests)
async def get_total_pages(user_url: str) -> int:
    """
    Get the total number of pages for a user's film list.
    Args:
        user_url: The base URL of the user's films page.
    Returns:
        Total number of pages in the film list.
    """
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(user_url, headers=HEADERS, timeout=TIMEOUT) as response:
                if response.status == 200:
                    soup = BeautifulSoup(await response.text(), 'html.parser')
                    pagination = soup.find("div", class_="pagination")
                    if pagination:
                        last_page = pagination.find_all("a")[-1]
                        total_pages = int(last_page.text)
                        return total_pages
                    return 1
                else:
                    print(f"Error fetching total pages: {response.status}")
                    return 1
    except Exception as e:
        print(f"Error fetching total pages: {e}")
        return 1
    
# Async function to convert star rating into numeric values
def convert_star_rating(star_string: Optional[str]) -> Optional[float]:
    """
    Convert star rating strings (e.g., '★★★½') into numeric values (e.g., 3.5).
    Args:
        star_string: A string containing stars (★) and optional half-star (½).
    Returns:
        A float representing the numeric value of the rating, or None if input is invalid.
    """
    if not star_string:
        return None
    full_stars = star_string.count('★')
    return full_stars + 0.5 if '½' in star_string else full_stars

# Async function to extract film data
async def extract_film_data(film: BeautifulSoup) -> Dict[str, Optional[str]]:
    """
    Extract title, numeric rating, review URL, and "liked" status for a single film.
    Only return films that are rated or liked.
    
    Args:
        film: A BeautifulSoup object representing a film entry.
        
    Returns:
        A dictionary containing the film's title, numeric rating, review URL, and "liked" status.
    """
    title = film.find("img").get("alt")
    rating = film.find("span", class_="rating")
    rating_text = rating.text.strip() if rating else None
    numeric_rating = convert_star_rating(rating_text)
    review_link = film.find("a", class_="review-micro")
    review_url = f"https://letterboxd.com{review_link.get('href')}" if review_link else None
    liked = film.find("span", class_="like liked-micro has-icon icon-liked icon-16") is not None

    return {
        "Title": title,
        "Rating": numeric_rating,
        "Review URL": review_url,
        "Liked": liked
    }
    
# Async function to scrape a page of films
async def scrape_page(page_num: int, base_url: str) -> List[Dict[str, Optional[str]]]:
    """Scrape a single page of films asynchronously."""
    page_url = f"{base_url}/page/{page_num}/"
    print(f"Scraping page {page_num}...")
    html = await fetch_with_backoff(page_url)
    if not html:
        return []

    soup = BeautifulSoup(html, 'html.parser')
    films = soup.find_all("li", class_="poster-container")

    # Extract basic data for each film
    film_data = [await extract_film_data(film) for film in films]
    return film_data

# Async function to fetch review content and tags for a single film entry asynchronously
'''
async def fetch_review_entry(entry: Dict[str, Optional[str]], review_url: str) -> Dict[str, Optional[str]]:
    """Fetch review content and tags for a single film asynchronously."""
    try:
        entry["Review"] = await extract_review(review_url)
        entry["Tags"] = await extract_tags(review_url)
    except Exception as e:
        print(f"Error fetching review entry for {entry['Title']}: {e}")
        entry["Review"] = None
        entry["Tags"] = None
    return entry

# Function to fetch reviews and tags concurrently for multiple films
async def fetch_reviews_concurrently(film_data: List[Dict[str, Optional[str]]]) -> List[Dict[str, Optional[str]]]:
    tasks = []
    for entry in film_data:
        review_url = entry.get("Review URL")
        if review_url:
            tasks.append(asyncio.ensure_future(fetch_review_entry(entry, review_url)))

    results = await asyncio.gather(*tasks)

    # Update the film data with fetched reviews and tags
    for idx, result in enumerate(results):
        film_data[idx]["Review"] = result.get("Review")
        film_data[idx]["Tags"] = result.get("Tags")

    return film_data
'''
# Main function to extract user films and their details
async def extract_user_films(username: str) -> List[Dict[str, Optional[str]]]:
    """
    Extract all films and their details (title, rating, review URL, and review content) for a given user asynchronously.
    """
    base_url = f"https://letterboxd.com/{username}/films/"
    total_pages = await get_total_pages(base_url)
    all_films = []

    # Scrape pages concurrently
    tasks = [scrape_page(page_num, base_url) for page_num in range(1, total_pages + 1)]
    page_results = await asyncio.gather(*tasks)

    for page_data in page_results:
        all_films.extend(page_data)

    # Fetch reviews and tags for all films concurrently
    ##all_films_with_reviews = await fetch_reviews_concurrently(all_films)

    return all_films##_with_reviews


# Function to save the data to a CSV file for each user
async def save_data_to_csv(user_data, username: str):
    """Save the user's data to a CSV file."""
    df = pd.DataFrame(user_data)
    filename = f"C:/Users/sarah/Documents/GitHub/letterboxd-scraper/data2/{username}_film_data.csv"
    df.to_csv(filename, index=False)
    print(f"Data for {username} saved to {filename}")

# Function to process a single user
async def process_user(username: str):
    print(f"Scraping data for user: {username}")
    
    # Scrape the user's films
    user_data = await extract_user_films(username)

    # Save data to CSV
    await save_data_to_csv(user_data, username)

    # Simulate a delay between requests to prevent rate-limiting
    await async_sleep(random.uniform(3, 5))  # Sleep 3 to 5 seconds between users

# Function to split the user list into chunks of 4 users each
def chunk_users(user_list: List[str], chunk_size: int = 4) -> List[List[str]]:
    """Split the user list into chunks of 4 users each."""
    for i in range(0, len(user_list), chunk_size):
        yield user_list[i:i + chunk_size]

# Function to process a batch of 4 users concurrently
async def process_users_batch(user_batch: List[str]):
    """Process a batch of 4 users concurrently."""
    tasks = [process_user(username) for username in user_batch]
    await asyncio.gather(*tasks)  # Run all tasks concurrently

# Main function to manage concurrent scraping in batches of 4 users
async def scrape_multiple_users_concurrently(usernames: List[str]):
    # Split users into batches of 4 and process them
    for user_batch in chunk_users(usernames, 1):
        print(f"Processing batch of {len(user_batch)} users...")
        
        # Process each batch concurrently
        await process_users_batch(user_batch)

        # Sleep between batches to avoid hitting rate limits
        await async_sleep(3)  # Adjust the sleep time if necessary

# Running the asyncio event loop
async def main():
    # Read the list of usernames from the CSV
    users = pd.read_csv("C:/Users/sarah/Documents/GitHub/letterboxd-scraper/skipped_users.csv")['user'].to_list()

    # Start scraping users concurrently
    await scrape_multiple_users_concurrently(users)

if __name__ == "__main__":
    asyncio.run(main())
