'''
Wen Zhang, Daniel Park, Danny Huang, Sasha(Alex) Murokh
Made-in-Thailand
SoftDev
P01 - ArRESTed Development - Stock Visualizer Platform - XÆA-69
Time Spent:
Target Ship Date: 2024-12-13
'''

# Import necessary libraries
import sqlite3
import os
from flask import Flask, render_template, request, session, redirect
from datetime import datetime
from db_scripts import db_commands



keys = ["key_Calendarific.txt", "key_YH-Finance.txt"]
for i in range(len(keys)):
    file = open("app/keys/" + keys[i], "r")
    content = file.read()
    if content: ##if file isnt empty
        keys[i] = content.replace("\n", "")
    file.close()

def key_check():
    for i in range(len(keys)):
        if ".txt" in keys[i]:
            return error(f"api key is missing in {keys[i]}")
        ##check invalid keys

def signed_in():
    return 'username' in session.keys() and session['username'] is not None

def check_user(username):
    user = db_commands.get_user("username", username)
    if user is None:
        return False
    return user[1] == username

def check_password(username, password):
    user = db_commands.get_user("username", username)
    if user is None:
        return False
    return user[2] == password

# Initialize Flask app
app = Flask(__name__)
app.secret_key = os.urandom(32)

@app.route("/", methods=['GET', 'POST'])
def landing():
    if signed_in():
        return redirect('/main')
    return render_template("landing.html")

@app.route("/login", methods=['GET', 'POST'])
def login():
    if signed_in():
        return redirect('/main')
    elif request.method == "POST":
        username = request.form.get('username')
        password = request.form.get('pw')
        if not check_user(username):
            return render_template("login.html", message="No such username exists")
        if not check_password(username, password):
            return render_template("login.html", message="Incorrect password")
        session['username'] = username
        return redirect('/main')
    return render_template("login.html")

@app.route("/signup", methods=['GET', 'POST'])
def sign_up():
    if signed_in():
        return redirect('/main')
    elif request.method == "POST":
        username = request.form['username']
        password = request.form['pw']
        user = db_commands.get_user("username", username)
        if user is None:
            db_commands.add_account(username, password)
            return redirect('/login')
        else:
            return render_template('signup.html', message="Username already exists")
    return render_template('signup.html')

filter = "ALL"

@app.route("/main", methods=['GET', 'POST'])
def main():
    
    global filter
    
    if not signed_in():
        return redirect('/landing')
    key_check()

    db_commands.get_holidays(keys[0])

    filter_change = False

    if request.method == "POST":
        if 'filter' in request.form:
            filter = request.form["filter"]
            filter_change = True
        if 'watchlist' in request.form:
            ticker = request.form["watchlist"]
            db_commands.add_watchlist(session['username'], ticker)
           
    if filter_change:
        db_commands.filter(filter, keys[1])
    table = db_commands.get_tickers()

    filter_names = db_commands.get_filters("name")
    for i in range(len(filter_names)):
        filter_names[i] = filter_names[i][0]
    
    now = datetime.now()
    today_date = now.date()
    
    holidays = db_commands.get_holidays(keys[0])
    
    future_holidays = [h for h in holidays if h["date"] >= today_date]

    if future_holidays:
        next_holiday = future_holidays[0]  # First holiday in the future
        holiday_name = next_holiday["name"]
        holiday_date = next_holiday["date"]
    else:
        holiday_name = "No upcoming holidays"
        holiday_date = ""
    
    
    advice = db_commands.get_advice()
    
    return render_template("main.html", user=session['username'], filters = filter_names, table = table, today_date = today_date, holiday_name = holiday_name, holiday_date = holiday_date, advice = advice)

@app.route("/watchlist", methods=['GET', 'POST'])
def watchlist():
    if not signed_in():
        return redirect('/landing')
    key_check()
    if request.method == "POST":
        if "remove" in request.form:
            ticker = request.form["remove"]
            db_commands.remove_watchlist(session['username'], ticker)
    
    table = db_commands.get_watchlist(session['username'])
    return render_template("watchlist.html", user=session['username'], table = table)
    
@app.route("/logout", methods = ['GET', 'POST'])
def logout():
    session.pop('username', None)
    session.clear()
    return render_template("landing.html", message="You have successfully logged out!")

def error(error_message):
    return render_template("error.html", error_message = error_message)

if __name__ == "__main__":
    app.debug = True

    db_commands.main_tickers(keys[1])
    db_commands.holidays(keys[0])

    app.run()
