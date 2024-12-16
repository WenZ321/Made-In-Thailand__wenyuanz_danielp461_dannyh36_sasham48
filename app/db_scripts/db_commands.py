import sqlite3, requests
from db_scripts import setup_db

def get_db_connection():
    return sqlite3.connect(setup_db.DB_FILE)

def clear_table():
    db = get_db_connection()
    cur = db.cursor()
    try:
        cur.execute(f'DELETE FROM tickers;')
        cur.execute(f'DELETE FROM sqlite_sequence WHERE name="tickers";') 
        db.commit()
        print("All data cleared successfully.")
    except sqlite3.Error as e:
        print(f"ERROR: {e}")
    finally:
        cur.close()
        db.close()

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
    

def all_tickers(key):
    url = "https://yahoo-finance15.p.rapidapi.com/api/v2/markets/tickers"

    querystring = {"page":"50","type":"STOCKS"}

    headers = {
        "x-rapidapi-key": f"{key}",
        "x-rapidapi-host": "yahoo-finance15.p.rapidapi.com"
    }

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


def filter_tickers(filter, key):
    if filter == "all_tickers":
        all_tickers(key)
        return

    url = "https://yahoo-finance15.p.rapidapi.com/api/v1/markets/screener"

    querystring = {"list": f"{filter}"}

    headers = {
        "x-rapidapi-key": f"{key}",
        "x-rapidapi-host": "yahoo-finance15.p.rapidapi.com"
    }

    response = requests.get(url, headers=headers, params=querystring)
    data = response.json()

    body_section = data["body"]

    db = get_db_connection()
    cur = db.cursor()
    
    for entry in body_section:
        cur.execute("INSERT INTO tickers (ticker, name, last_sale, net_change) VALUES (?, ?, ?, ?)", (entry["symbol"], entry['fullExchangeName'], entry["regularMarketPrice"], entry["regularMarketChange"]))
        db.commit()

    cur.close()
    db.close()


def get_tickers():
    db = get_db_connection()
    cur = db.cursor()

    cur.execute("SELECT ticker, name, last_sale, net_change FROM tickers")
    data = cur.fetchall()

    data_entries = {
        ticker: {
            "name": name,
            "last_sale": last_sale,
            "net_change": net_change
        }
        for ticker, name, last_sale, net_change in data
    }
    
    cur.close()
    db.close()
    
    return data_entries

def get_filters(column):
    db = get_db_connection()
    cur = db.cursor()

    cur.execute(f"SELECT {column} FROM filters")
    data = cur.fetchall()

    cur.close()
    db.close()
    
    return data

def filter(filter_name, key):
    filters = get_filters("*")
    func = "all_tickers"
    for filter in filters:
        if filter_name in filter:
            func = filter[2]
    clear_table()
    filter_tickers(func, key)
