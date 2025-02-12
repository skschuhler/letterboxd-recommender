import aiohttp
import asyncio
from tqdm.asyncio import tqdm_asyncio
import pandas as pd

df = pd.read_csv('data/ratings.csv')
df.drop_duplicates(subset=['user', 'Title'], keep='first')
counts = df['Title'].value_counts()

multiple_titles = counts[counts > (0.01*2500)].index
df = df[df['Title'].isin(multiple_titles)]

movie_titles = list(df['Title'].unique())

# API key and base URL for OMDB API
API_KEY = 'd0a004d1'
BASE_URL = "http://www.omdbapi.com/"

# List of movies
movies = movie_titles

# Asynchronous function to fetch movie metadata
async def fetch_movie(session, movie):
    params = {
        "apikey": API_KEY,
        "t": movie  # Search by title
    }
    async with session.get(BASE_URL, params=params) as response:
        if response.status == 200:
            data = await response.json()
            if data.get("Response") == "True":
                return {"movie": movie, "metadata": data}  # Return metadata if found
            else:
                return {"movie": movie, "metadata": None}  # Not found
        else:
            return {"movie": movie, "metadata": None}  # Error case

# Main asynchronous function
async def fetch_all_movies(movie_list):
    found_metadata = []
    not_found_movies = []

    # Create a session and fetch all metadata
    async with aiohttp.ClientSession() as session:
        tasks = [fetch_movie(session, movie) for movie in movie_list]
        
        # Run tasks with a progress bar
        for result in tqdm_asyncio.as_completed(tasks, desc="Fetching movie metadata"):
            res = await result
            if res["metadata"]:
                found_metadata.append(res["metadata"])
            else:
                not_found_movies.append(res["movie"])

    return found_metadata, not_found_movies

# Run the async function
if __name__ == "__main__":
    metadata, not_found = asyncio.run(fetch_all_movies(movies))

    # Display results
    print("\nFound Metadata:")
    for movie in metadata:
        print(movie)

    print("\nMovies Not Found or Error Occurred:")
    for movie in not_found:
        print(movie)


pd.DataFrame(metadata).to_csv("found_metadata.csv")
pd.DataFrame(not_found).to_csv("not_found.csv")