# A file used to test and run queries on the database
import sqlite3
import pandas as pd 

conn = sqlite3.connect('movielens.db')

# Test Query
query = """
SELECT 
    users.user_id, 
    users.age, 
    movies.title, 
    ratings.rating 
FROM ratings
JOIN users ON ratings.user_id = users.user_id
JOIN movies ON ratings.movie_id = movies.movie_id
WHERE users.age < 25 AND ratings.rating = 5
LIMIT 10;
"""

# Construct query into dataframe and 
connected_view = pd.read_sql_query(query, conn)
print(connected_view)

conn.close