import sqlite3, os

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
CREATE TABLE IF NOT EXISTS tickers (
    ticker TEXT NOT NULL,
    name TEXT NOT NULL, 
    last_sale TEXT NOT NULL, 
    net_change TEXT NOT NULL
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

cur.execute("SELECT * from filters")
data = cur.fetchall()
if len(data) == 0:
    cur.execute("INSERT INTO filters (name, filter) VALUES (?, ?)", ("ALL", "update_tickers"))
    cur.execute("INSERT INTO filters (name, filter) VALUES (?, ?)", ("TOP25", "top_25"))

con.commit()
con.close()