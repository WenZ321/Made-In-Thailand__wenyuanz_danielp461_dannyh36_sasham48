import sqlite3, os, requests

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

'''
cur.execute("INSERT INTO filters (?, ?)", ("TOP25", "add a sql command here"))
cur.execute("INSERT INTO filters (?, ?)", ("BOT25", "add a sql command here"))
cur.execute("INSERT INTO filters (?, ?)", ("TECH", "add a sql command here"))
'''
con.commit()
con.close()

def get_db_connection():
    return sqlite3.connect(DB_FILE)

def add_account(username, password):
    try:
        db = get_db_connection()
        cur = db.cursor()
        cur.execute("INSERT INTO users (username, password) VALUES (?, ?)", (username, password))
    except sqlite3.Error as e:
        print(f"Database error: {e}")
    finally:
        cur.close()
        db.commit()
        db.close()
    
def get_user(column, value):
    db = get_db_connection()
    cur = db.cursor()
    try:
        query = f'SELECT * FROM users WHERE {column} = ?'
        cur.execute(query, (value,))
        user = cur.fetchone()
    except sqlite3.Error as e:
        print(f"An error occurred: {e}")
        user = None
    finally:
        cur.close()
        db.commit()
        db.close()
    return user



def update_tickers():
    url = "https://yahoo-finance15.p.rapidapi.com/api/v2/markets/tickers"

    querystring = {"page":"50","type":"STOCKS"}

## Todo: create function
    file = open("app/keys/key_YH-Finance.txt", "r")
    key = file.read()

    headers = {
        "x-rapidapi-key": f"{key}",
        "x-rapidapi-host": "yahoo-finance15.p.rapidapi.com"
    }

    file.close()

    response = requests.get(url, headers=headers, params=querystring)
    data = response.json()
    body_section = data["body"]

    db = get_db_connection()
    cur = db.cursor()
    
    for entry in body_section:
        cur.execute("INSERT INTO tickers (ticker, name, last_sale, net_change) VALUES (?, ?, ?, ?)", (entry["symbol"], entry['name'], entry["lastsale"], entry["netchange"]))
        db.commit()

    cur.close()
    db.close()

def get_tickers():
    db = get_db_connection()
    cur = db.cursor()

    cur.execute("SELECT ticker, name, last_sale, net_change FROM tickers")
    data = cur.fetchall()

    dataEntries = {
        ticker: {
            "name": name,
            "last_sale": last_sale,
            "net_change": net_change
        }
        for ticker, name, last_sale, net_change in data
    }
    
    cur.close()
    db.close()
    
    return dataEntries
    
        