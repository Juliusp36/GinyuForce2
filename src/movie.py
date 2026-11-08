"""Movie Model - Read-only Data Access Layer."""
from typing import Optional, List, Dict
from db_config import execute_query

class Movie:
    @staticmethod
    def get_by_id(movie_id: int) -> Optional[Dict]:
        rows = execute_query('''SELECT m.*, p.poster_url,
            ROUND(AVG(r.rating), 2) AS average_rating, COUNT(r.rating) AS rating_count
            FROM movies m LEFT JOIN movie_posters p ON m.movie_id = p.movie_id
            LEFT JOIN ratings r ON m.movie_id = r.movie_id
            WHERE m.movie_id = ? GROUP BY m.movie_id''', (movie_id,), fetch=True)
        return rows[0] if rows else None

    @staticmethod
    def get_all(limit: int = 100, offset: int = 0) -> List[Dict]:
        return execute_query('''SELECT m.*, p.poster_url FROM movies m
            LEFT JOIN movie_posters p ON m.movie_id = p.movie_id
            ORDER BY m.movie_id LIMIT ? OFFSET ?''', (limit, offset), fetch=True)

    @staticmethod
    def search(title: str, limit: int = 100) -> List[Dict]:
        return execute_query('''SELECT m.*, p.poster_url FROM movies m
            LEFT JOIN movie_posters p ON m.movie_id = p.movie_id
            WHERE m.title LIKE ? ORDER BY m.title LIMIT ?''', (f'%{title}%', limit), fetch=True)
