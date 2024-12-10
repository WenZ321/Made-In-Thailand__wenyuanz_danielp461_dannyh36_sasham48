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
    password TEXT NOT NULL
);
''')

# MAIN TABLE
cur.execute('''
CREATE TABLE IF NOT EXISTS mainTable (
    tickers TEXT NOT NULL UNIQUE
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

'''
cur.execute("INSERT INTO filters (?, ?)", ("TOP25", "add a sql command here"))
cur.execute("INSERT INTO filters (?, ?)", ("BOT25", "add a sql command here"))
cur.execute("INSERT INTO filters (?, ?)", ("TECH", "add a sql command here"))
'''
con.commit()
con.close()

def get_db_connection():
    return sqlite3.connect(DB_FILE)

def addAccount(username, password):
    try:
        db = get_db_connection()
        c = db.cursor()
        c.execute("INSERT INTO users (username, password) VALUES (?, ?)", (username, password))
        db.commit()
        db.close()
    except sqlite3.Error as e:
        print(f"Database error: {e}")
    finally:
        db.close()
    
    
def get_user(column, value):
    conn = sqlite3.connect(DB_FILE)
    cur = conn.cursor()
    try:
        query = f"SELECT * FROM users WHERE {column} = ?"
        cur.execute(query, (value))
        user = cur.fetchone()
    except sqlite3.Error as e:
        print(f"An error occurred: {e}")
        user = None
    finally:
        cur.close()
        conn.close()
    return user


