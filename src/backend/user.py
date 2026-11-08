"""User Model - Data Access Layer."""
from typing import Optional, List, Dict
from db_config import execute_query

class User:
    @staticmethod
    def create(username: str, age: Optional[int] = None, gender: Optional[str] = None,
               occupation: Optional[str] = None, zip_code: Optional[str] = None) -> int:
        if not username.strip():
            raise ValueError('username is required')
        if User.get_by_username(username):
            raise ValueError('username already exists')
        return execute_query('''INSERT INTO users (user_id, username, age, gender, occupation, zip_code)
            VALUES ((SELECT COALESCE(MAX(user_id), 0) + 1 FROM users), ?, ?, ?, ?, ?)''',
            (username, age, gender, occupation, zip_code))

    @staticmethod
    def get_by_id(user_id: int) -> Optional[Dict]:
        results = execute_query('SELECT * FROM users WHERE user_id = ?', (user_id,), fetch=True)
        return results[0] if results else None

    @staticmethod
    def get_by_username(username: str) -> Optional[Dict]:
        results = execute_query('SELECT * FROM users WHERE username = ?', (username,), fetch=True)
        return results[0] if results else None

    @staticmethod
    def get_all(limit: int = 100, offset: int = 0) -> List[Dict]:
        return execute_query('SELECT * FROM users ORDER BY user_id LIMIT ? OFFSET ?',
                             (limit, offset), fetch=True)

    @staticmethod
    def update(user_id: int, username: Optional[str] = None, age: Optional[int] = None,
               gender: Optional[str] = None, occupation: Optional[str] = None,
               zip_code: Optional[str] = None) -> bool:
        fields = {'username': username, 'age': age, 'gender': gender,
                  'occupation': occupation, 'zip_code': zip_code}
        changes = {k: v for k, v in fields.items() if v is not None}
        if not changes:
            return False
        if username is not None:
            if not username.strip():
                raise ValueError('username is required')
            other = User.get_by_username(username)
            if other and other['user_id'] != user_id:
                raise ValueError('username already exists')
        sql = 'UPDATE users SET ' + ', '.join(f'{key} = ?' for key in changes) + ' WHERE user_id = ?'
        return execute_query(sql, (*changes.values(), user_id)) > 0

    @staticmethod
    def delete(user_id: int) -> bool:
        # Existing MovieLens import has no FK constraints: remove ratings explicitly.
        # Atomic transaction prevents orphan ratings.
        import sqlite3
        from db_config import DB_PATH
        with sqlite3.connect(DB_PATH) as conn:
            conn.execute('DELETE FROM ratings WHERE user_id = ?', (user_id,))
            return conn.execute('DELETE FROM users WHERE user_id = ?', (user_id,)).rowcount > 0
