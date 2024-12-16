import sqlite3, os
DB_FILE = os.path.join(os.path.dirname(__file__), "../allTickers.db")

con = sqlite3.connect(DB_FILE)
cur = con.cursor()

cur.execute('''
CREATE TABLE IF NOT EXISTS allTickers (
    ticker TEXT NOT NULL UNIQUE,
    id TEXT NOT NULL UNIQUE
);
''')


con.commit()
con.close()