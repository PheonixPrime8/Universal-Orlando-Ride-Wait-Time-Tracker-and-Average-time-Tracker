import sqlite3
from config import DB_NAME


def get_connection():
    conn = sqlite3.connect(DB_NAME)
    # SQLite does not enforce foreign keys unless explicitly enabled per connection.
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def create_database():
    with get_connection() as conn:
        cursor = conn.cursor()

        cursor.execute("""
        CREATE TABLE IF NOT EXISTS rides (
            ride_id INTEGER PRIMARY KEY,
            ride_name TEXT NOT NULL,
            park_name TEXT NOT NULL,
            land_name TEXT
        )
        """)

        cursor.execute("""
        CREATE TABLE IF NOT EXISTS wait_times (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            ride_id INTEGER NOT NULL,
            wait_time INTEGER NOT NULL,
            is_open INTEGER NOT NULL,
            recorded_at TEXT NOT NULL,
            FOREIGN KEY (ride_id) REFERENCES rides(ride_id)
        )
        """)
