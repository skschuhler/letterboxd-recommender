# letterboxd-recommender

## scraping
### **Overview**  
This project is an asynchronous web scraper designed to extract user film data from [Letterboxd](https://letterboxd.com/). The scraper retrieves movie ratings, review URLs, and metadata for a given set of users, handling rate-limiting and large datasets efficiently using `aiohttp` and `BeautifulSoup`.  

### **Features**  
- **Asynchronous scraping:** Uses `asyncio` and `aiohttp` to fetch multiple pages concurrently, improving efficiency.  
- **Exponential backoff for rate-limiting:** Implements retry logic to handle `429 Too Many Requests` errors.  
- **Film data extraction:** Retrieves movie titles, numeric ratings, review URLs, and "liked" statuses for each film.  
- **Pagination handling:** Automatically determines the number of pages to scrape for each user.  
- **Batch processing:** Processes multiple users concurrently while preventing excessive requests.  
- **CSV output:** Saves the extracted data in a structured format for further analysis.  

### **How It Works**  
1. **User list input:** Reads a CSV file containing the usernames to scrape.  
2. **Fetching total pages:** Determines how many pages of films each user has.  
3. **Extracting film data w/ pagination:** Scrapes each user's film list, capturing movie titles, ratings, and review URLs.  
4. **Saving results:** Writes the extracted data to CSV files, storing them in the `data2/` directory.  
5. **Handling rate limits:** Uses exponential backoff to wait when rate-limited by Letterboxd.  

Movie data scraped using the Open movie Database at https://www.omdbapi.com/

## **Exploratory Data Analysis (EDA.ipynb) for Letterboxd Ratings**  

### **Overview**  
This script performs exploratory data analysis (EDA) on Letterboxd movie ratings to clean the data, analyze rating trends, and visualize key insights. The goal is to better understand user preferences and the characteristics of highly rated vs. poorly rated movies.  

### **Steps in the Analysis**  

#### **1. Data Cleaning & Filtering**  
- Loads movie ratings and removes duplicate entries.  
- Filters out movies with too few ratings to ensure meaningful insights.  

#### **2. Processing Movie Metadata**  
- Extracts relevant details like genre, director, and actors from metadata.  
- Cleans and structures the data for analysis.  

#### **3. Standardizing User Ratings**  
- Adjusts ratings using z-scores to account for individual rating biases.  
- Computes weighted averages to rank movies fairly.  

#### **4. Identifying Top & Bottom Movies**  
- Determines the highest- and lowest-rated movies based on standardized scores.  
- Analyzes trends in these movies to find common patterns.  

#### **5. Visualizing Trends**  
- Generates bar charts showing which actors and genres appear most often in top- and bottom-rated movies.  

## **Content-Based Movie Recommendation System (content-based.ipynb)**

### **Overview**
This script implements a **content-based filtering** approach to recommend movies to users based on their past preferences. By leveraging **SBERT (Sentence-BERT) embeddings**, the system captures the semantic meaning of movie metadata (e.g., genres, directors, actors, plot) and computes personalized recommendations.

### **How It Works**

#### **1. Data Preparation**
- Loads user ratings, movie metadata, and a list of popular users.
- Filters data to include only **the first 1000 most active users** and their ratings.
- Cleans and processes movie metadata, transforming text fields (e.g., genre, director) into structured lists.

#### **2. Feature Representation Using SBERT**
- Combines key textual attributes (genres, actors, plot, etc.) into a **single descriptive text** per movie.
- Uses **SBERT (all-MiniLM-L6-v2)** to generate **dense vector embeddings** for each movie, capturing their semantic meaning.
- Stores the embeddings for efficient similarity calculations.

#### **3. Building User Profiles**
- Computes a **personalized user profile** by taking a **weighted average** of the SBERT embeddings of movies they’ve rated.
- Normalizes ratings using **min-max scaling** to ensure fair weighting.

#### **4. Generating Movie Recommendations**
- Uses **cosine similarity** to compare a user’s profile against all movies in the dataset.
- Recommends the top **30 most similar movies** that the user hasn’t rated yet.

#### **5. Finding Similar Movies**
- Computes the **most similar movies** to a given title based on SBERT embeddings.
- Returns the **top 10 recommendations** ranked by similarity.

## **Collaborative Filtering for Movie Recommendations (collab-filtering.ipynb)**

### **Overview**
This script implements a **collaborative filtering** approach for movie recommendations using two techniques:
1. **Singular Value Decomposition (SVD)** – A matrix factorization-based approach optimized using hyperparameter tuning.
2. **Neural Collaborative Filtering (NCF)** – A deep learning-based recommendation model.

Both methods predict movie ratings based on user-item interactions and help generate personalized recommendations.

### **How It Works**

#### **1. Data Preparation**
- Loads user ratings and movie IDs.
- Splits data into **training, validation, and test sets** (70%-15%-15% split).
- Maps users and movies to unique numerical indices for model training.

#### **2. SVD Model (Matrix Factorization)**
- Performs **grid search** to fine-tune hyperparameters (number of latent factors, learning rate, regularization).
- Trains the **optimized SVD model** using the best parameters.
- Evaluates performance using **Root Mean Squared Error (RMSE)**.

#### **3. Neural Collaborative Filtering (NCF)**
- Uses **embeddings** to represent users and movies in a latent space.
- Combines user and movie representations via a **deep neural network**.
- Predicts ratings with a **fully connected architecture** using **ReLU activations**.
- Trains the model using **Mean Squared Error (MSE) loss** and **Adam optimizer**.
- Evaluates model performance on the validation set using **MAE and RMSE**.

