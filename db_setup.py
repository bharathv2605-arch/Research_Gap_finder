"""
db_setup.py - Database Setup Module
Creates SQLite database and all required tables.
Run this file once before starting the application.
"""

import sqlite3
import os

# Path to the database file
DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'database.db')


def get_connection():
    """Get a connection to the SQLite database."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row  # Return rows as dictionaries
    return conn


def create_tables():
    """Create all required tables if they don't exist."""
    conn = get_connection()
    cursor = conn.cursor()

    # ---- Users Table ----
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL
        )
    ''')

    # ---- Papers Table ----
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS papers (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            filename TEXT NOT NULL,
            original_name TEXT NOT NULL,
            upload_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            text_content TEXT,
            FOREIGN KEY (user_id) REFERENCES users(id)
        )
    ''')

    # ---- Keywords Table ----
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS keywords (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            paper_id INTEGER NOT NULL,
            keyword TEXT NOT NULL,
            score REAL DEFAULT 0.0,
            FOREIGN KEY (paper_id) REFERENCES papers(id)
        )
    ''')

    # ---- Analysis Results Table ----
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS analysis_results (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            analysis_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            papers_analyzed TEXT,
            common_topics TEXT,
            missing_topics TEXT,
            gaps TEXT,
            suggestions TEXT,
            FOREIGN KEY (user_id) REFERENCES users(id)
        )
    ''')

    # ---- Insert default admin user (password: admin123) ----
    try:
        cursor.execute('''
            INSERT INTO users (username, password) VALUES (?, ?)
        ''', ('admin', 'admin123'))
    except sqlite3.IntegrityError:
        pass  # User already exists

    # ---- Insert a demo user (password: demo123) ----
    try:
        cursor.execute('''
            INSERT INTO users (username, password) VALUES (?, ?)
        ''', ('demo', 'demo123'))
    except sqlite3.IntegrityError:
        pass  # User already exists

    conn.commit()
    conn.close()
    print("[OK] Database tables created successfully!")


if __name__ == '__main__':
    create_tables()
