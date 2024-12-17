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
    username TEXT,
    ticker TEXT NOT NULL,
    name TEXT NOT NULL, 
    last_sale TEXT NOT NULL, 
    net_change TEXT NOT NULL,
    FOREIGN KEY (username) REFERENCES users(username) ON DELETE CASCADE
);
''')

cur.execute("SELECT * from filters")
data = cur.fetchall()
if len(data) == 0:
    cur.execute("INSERT INTO filters (name, filter) VALUES (?, ?)", ("ALL", "all_tickers"))
    cur.execute("INSERT INTO filters (name, filter) VALUES (?, ?)", ("GAIN", "day_gainers"))
    cur.execute("INSERT INTO filters (name, filter) VALUES (?, ?)", ("LOSE", "day_losers"))
    cur.execute("INSERT INTO filters (name, filter) VALUES (?, ?)", ("ACTIVE", "most_actives"))
    cur.execute("INSERT INTO filters (name, filter) VALUES (?, ?)", ("TECH", "growth_technology_stocks"))

con.commit()
con.close()