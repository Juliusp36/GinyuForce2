import sqlite3 
import pandas as pd 
import zipfile
from pathlib import Path

conn = sqlite3.connect('movielens.db')

# Open MovieLens dataset
zip_path = Path(__file__).resolve().parent.parent / "ml-100k.zip"

with zipfile.ZipFile(zip_path) as z:

    # Ratings table
    ratings_url = z.open('ml-100k/u.data')
    ratings = pd.read_csv(
        ratings_url,
        sep='\t',
        names=['user_id', 'movie_id', 'rating', 'timestamp']
    )
    ratings.to_sql('ratings', conn, if_exists='replace', index=False)

    # Movies table
    movies_url = z.open('ml-100k/u.item')
    movies = pd.read_csv(
        movies_url,
        sep='|',
        encoding='latin-1',
        header=None,
        usecols=[0, 1, 2]
    )
    movies.columns = ['movie_id', 'title', 'release_date']
    movies.to_sql('movies', conn, if_exists='replace', index=False)

    # Users table
    users_url = z.open('ml-100k/u.user')
    users = pd.read_csv(
        users_url,
        sep='|',
        names=['user_id', 'age', 'gender', 'occupation', 'zip_code']
    )
    users.to_sql('users', conn, if_exists='replace', index=False)

# Movie poster table - coming from a github repository which has the poster links for each movie in the database
poster_url = "https://raw.githubusercontent.com/babu-thomas/movielens-posters/master/movie_poster.csv"

# Load the posters into a datframe. Contains 'movie_id' and 'poster_url'
posters_df = pd.read_csv(
    poster_url,
    header=None,
    names=['movie_id', 'poster_url']
)

# Save
posters_df.to_sql('movie_posters', conn, if_exists='replace', index=False)
conn.close()


