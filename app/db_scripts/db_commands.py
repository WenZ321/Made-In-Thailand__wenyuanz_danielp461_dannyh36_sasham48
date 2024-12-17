import sqlite3, requests
from db_scripts import setup_db
from datetime import datetime

def get_db_connection():
    return sqlite3.connect(setup_db.DB_FILE)

def clear_table():
    db = get_db_connection()
    cur = db.cursor()
    try:
        cur.execute(f'DELETE FROM tickers;')
        cur.execute(f'DELETE FROM sqlite_sequence WHERE name="tickers";') 
        db.commit()
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
    
def main_tickers(key):
    clear_table()
    url = "https://yahoo-finance15.p.rapidapi.com/api/v2/markets/tickers"

    querystring = {"page":"1","type":"STOCKS"}

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
        main_tickers(key)
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

def add_watchlist(username, ticker_name):
    db = get_db_connection()
    cur = db.cursor()

    cur.execute("SELECT ticker, name, last_sale, net_change FROM tickers WHERE ticker = ?", (ticker_name,))
    data = cur.fetchall()
    data_entries = []

    for ticker, name, last_sale, net_change in data:
        data_entries = [ticker, name, last_sale, net_change]

    cur.execute("SELECT ticker FROM watchlists WHERE username = ?", (username,))
    data = cur.fetchall()

    if(len(data) == 0):
        cur.execute("INSERT INTO watchlists (username, ticker, name, last_sale, net_change) VALUES (?, ?, ?, ?, ?)", 
                        (username, data_entries[0], data_entries[1], data_entries[2], data_entries[3]))
        db.commit()

    for ticker_tup in data:
        if data_entries[0] not in ticker_tup:
            cur.execute("INSERT INTO watchlists (username, ticker, name, last_sale, net_change) VALUES (?, ?, ?, ?, ?)", 
                        (username, data_entries[0], data_entries[1], data_entries[2], data_entries[3]))
            db.commit()

    cur.close()
    db.close()

def get_watchlist(username):
    db = get_db_connection()
    cur = db.cursor()

    cur.execute("SELECT ticker, name, last_sale, net_change FROM watchlists WHERE username = ?", (username,))
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

def remove_watchlist(username, ticker):
    db = get_db_connection()
    cur = db.cursor()

    cur.execute("DELETE FROM watchlists WHERE username = ? AND ticker = ?", (username, ticker))
    
    db.commit()
    cur.close()
    db.close()

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


def holidays(key):
    db = get_db_connection()
    cur = db.cursor()
    
    url = "https://calendarific.com/api/v2/holidays"
    
    params = {
    "api_key": key,  
    "country": "US",     
    "year": 2024,        
    "type": "national"   
    }
    
    response = requests.get(url, params = params)

    if response.status_code == 200:
        data = response.json()
        holidays = data["response"]["holidays"]
        for holiday in holidays:
            cur.execute("INSERT INTO holidays (name, date) VALUES (?, ?)", (holiday["name"], holiday["date"]["iso"]))
            db.commit()
    
    cur.close()
    db.close()
    
def get_holidays(key):
    
    holidays(key)
    
    db = get_db_connection()
    cur = db.cursor()

    cur.execute("SELECT name, date FROM holidays")
    data = cur.fetchall()

    data_entries = [
        {"name": name, "date": datetime.strptime(date, "%Y-%m-%d").date()}
        for name, date in data
    ]
    
    cur.close()
    db.close()
    
    return data_entries

def get_advice():
    url = "https://api.adviceslip.com/advice"
    
    response = requests.get(url)
    
    if response.status_code == 200:
        data = response.json()
        bad_list = [33,46,80,114,181,203]
        if (data["slip"]["id"] in bad_list):
            advice = "Accept advice"
        else:
            advice = data["slip"]["advice"]
        return advice
    else:
        print(f"Error {response.status_code}: Unable to fetch advice.")
