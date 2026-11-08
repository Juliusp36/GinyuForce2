"""Movie Poster Model - Read-only Data Access Layer."""
from typing import Optional, List, Dict
from db_config import execute_query

class MoviePoster:
    @staticmethod
    def get_by_movie(movie_id: int) -> Optional[Dict]:
        rows = execute_query('SELECT * FROM movie_posters WHERE movie_id = ?', (movie_id,), fetch=True)
        return rows[0] if rows else None

    @staticmethod
    def get_all(limit: int = 100, offset: int = 0) -> List[Dict]:
        return execute_query('SELECT * FROM movie_posters ORDER BY movie_id LIMIT ? OFFSET ?',
                             (limit, offset), fetch=True)
