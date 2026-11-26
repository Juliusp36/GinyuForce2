import sqlite3
import pandas as pd
import zipfile
from pathlib import Path


# Get the paths for the database and MovieLens dataset
base_path = Path(__file__).resolve().parent

db_path = base_path / "movielens.db"
zip_path = base_path.parent / "ml-100k.zip"


# Genres are stored in columns 5-23 of the u.item file
genres = [
    'Unknown',
    'Action',
    'Adventure',
    'Animation',
    "Children's",
    'Comedy',
    'Crime',
    'Documentary',
    'Drama',
    'Fantasy',
    'Film-Noir',
    'Horror',
    'Musical',
    'Mystery',
    'Romance',
    'Sci-Fi',
    'Thriller',
    'War',
    'Western'
]


# Open the MovieLens dataset
with zipfile.ZipFile(zip_path) as z:

    # Read the movie IDs and genre columns
    movies = pd.read_csv(
        z.open('ml-100k/u.item'),
        sep='|',
        encoding='latin-1',
        header=None,
        usecols=[0] + list(range(5, 24))
    )

    # Assign names to each column
    movies.columns = ['movie_id'] + genres


# Store the movie IDs and their corresponding genres
movie_genres = []


# Go through each movie in the dataset
for _, movie in movies.iterrows():

    # Check each genre for the current movie
    for genre in genres:

        # A value of 1 means the movie belongs to that genre
        if movie[genre] == 1:

            movie_genres.append((
                int(movie['movie_id']),
                genre
            ))


# Connect to our existing database
with sqlite3.connect(db_path) as conn:

    # Create a separate table for the movie genres
    conn.execute("""
        CREATE TABLE IF NOT EXISTS movie_genres (
            movie_id INTEGER NOT NULL,
            genre TEXT NOT NULL,
            PRIMARY KEY (movie_id, genre)
        ) WITHOUT ROWID
    """)

    # Remove previous genre information if the script is rerun
    conn.execute("DELETE FROM movie_genres")

    # Insert the movie IDs and their genres
    conn.executemany("""
        INSERT INTO movie_genres (movie_id, genre)
        VALUES (?, ?)
    """, movie_genres)

    # Create an index for filtering movies by genre
    conn.execute("""
        CREATE INDEX IF NOT EXISTS idx_movie_genre
        ON movie_genres(genre)
    """)


print(f"Imported {len(movie_genres)} movie-genre associations")