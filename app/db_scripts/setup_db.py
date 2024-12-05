import sqlite3
import os

DB_FILE = os.path.join(os.path.dirname(__file__), "../xaea69.db")

con = sqlite3.connect(DB_FILE)
cur = con.cursor()

# USER TABLE
cur.execute('''
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT NOT NULL UNIQUE,
    password TEXT NOT NULL,
    email TEXT NOT NULL UNIQUE
);
''')

#FILTERS TABLE
cur.execute('''
CREATE TABLE IF NOT EXISTS filters (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL UNIQUE,
    filter TEXT NOT NULL UNIQUE
);
''')

# WATCHLISTS TABLE
cur.execute('''
CREATE TABLE IF NOT EXISTS watchlists (
    user_id INTEGER,
    tickers TEXT NOT NULL UNIQUE,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);
''')

con.commit()
con.close()