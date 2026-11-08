"""Rating Model - Data Access Layer. MovieLens 100k ratings have no rating_id."""
from typing import Optional, List, Dict
from datetime import datetime, timezone
from db_config import execute_query
from user import User
from movie import Movie

class Rating:
    @staticmethod
    def create(user_id: int, movie_id: int, rating: int) -> bool:
        if not 1 <= rating <= 5:
            raise ValueError('rating must be an integer from 1 to 5')
        if not User.get_by_id(user_id) or not Movie.get_by_id(movie_id):
            raise ValueError('user or movie not found')
        if Rating.get_by_user_and_movie(user_id, movie_id):
            raise ValueError('user already rated this movie; use update')
        timestamp = int(datetime.now(timezone.utc).timestamp())
        return execute_query('INSERT INTO ratings (user_id, movie_id, rating, timestamp) VALUES (?, ?, ?, ?)',
                             (user_id, movie_id, rating, timestamp)) > 0

    @staticmethod
    def get_by_user_and_movie(user_id: int, movie_id: int) -> Optional[Dict]:
        rows = execute_query('SELECT * FROM ratings WHERE user_id = ? AND movie_id = ?',
                             (user_id, movie_id), fetch=True)
        return rows[0] if rows else None

    @staticmethod
    def get_by_user(user_id: int, limit: int = 100, offset: int = 0) -> List[Dict]:
        return execute_query('''SELECT r.*, m.title FROM ratings r JOIN movies m ON r.movie_id = m.movie_id
            WHERE r.user_id = ? ORDER BY r.timestamp DESC LIMIT ? OFFSET ?''',
            (user_id, limit, offset), fetch=True)

    @staticmethod
    def get_by_movie(movie_id: int, limit: int = 100, offset: int = 0) -> List[Dict]:
        return execute_query('SELECT * FROM ratings WHERE movie_id = ? ORDER BY timestamp DESC LIMIT ? OFFSET ?',
                             (movie_id, limit, offset), fetch=True)

    @staticmethod
    def get_all(limit: int = 100, offset: int = 0) -> List[Dict]:
        return execute_query('SELECT * FROM ratings ORDER BY timestamp DESC LIMIT ? OFFSET ?',
                             (limit, offset), fetch=True)

    @staticmethod
    def update(user_id: int, movie_id: int, rating: int) -> bool:
        if not isinstance(rating, int) or not 1 <= rating <= 5:
            raise ValueError('rating must be an integer from 1 to 5')
        return execute_query('''UPDATE ratings SET rating = ?, timestamp = ?
            WHERE user_id = ? AND movie_id = ?''',
            (rating, int(datetime.now(timezone.utc).timestamp()), user_id, movie_id)) > 0

    @staticmethod
    def delete(user_id: int, movie_id: int) -> bool:
        return execute_query('DELETE FROM ratings WHERE user_id = ? AND movie_id = ?',
                             (user_id, movie_id)) > 0
