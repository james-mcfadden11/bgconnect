import os
import sqlite3

DB_PATH = os.path.join(os.path.dirname(__file__), "..", "annotations.db")


def get_connection() -> sqlite3.Connection:
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db() -> None:
    conn = get_connection()
    conn.execute("""
        CREATE TABLE IF NOT EXISTS annotations (
            id          TEXT PRIMARY KEY,
            user_id     TEXT NOT NULL,
            timestamp   TEXT NOT NULL,
            category    TEXT NOT NULL,
            value       TEXT NOT NULL,
            notes       TEXT,
            created_at  TEXT NOT NULL
        )
    """)
    conn.commit()
    conn.close()
