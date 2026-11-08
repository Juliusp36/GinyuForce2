
"""SQLite connection helper. Set MOVIELENS_DB to override database location."""
import os
import sqlite3
from pathlib import Path

DB_PATH = Path(os.getenv(
    'MOVIELENS_DB',
    str(Path(__file__).resolve().parent / 'movielens.db')
))

def execute_query(query, params=(), fetch=False):
    with sqlite3.connect(DB_PATH) as conn:
        conn.row_factory = sqlite3.Row
        conn.execute('PRAGMA foreign_keys = ON')
        cursor = conn.execute(query, params)
        if fetch:
            return [dict(row) for row in cursor.fetchall()]
        return cursor.lastrowid if query.lstrip().upper().startswith('INSERT') else cursor.rowcount
