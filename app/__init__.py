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
import csv
import os
from flask import Flask, render_template, request, session, redirect
from db_scripts import db_commands

DB_FILE = os.path.join(os.path.dirname(__file__), "xaea69.db")

keys = ["key_Calendarific.txt", "key_MarketStack.txt", "key_YH-Finance.txt"]
for i in range(len(keys)):
    file = open("app/keys/" + keys[i], "r")
    content = file.read()
    if content: ##if file isnt empty
        keys[i] = content
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

@app.route("/main", methods=['GET', 'POST'])
def main():
    if not signed_in():
        print("1234")
        return redirect('/landing')
    key_check()
    
    filter = "ALL"
    if request.method == "POST":
        filter = request.form["filter"]
    
    db_commands.filter(filter, keys[2])
    table = db_commands.get_tickers()

    filter_names = db_commands.get_filters("name")
    for i in range(len(filter_names)):
        filter_names[i] = filter_names[i][0]

    return render_template("main.html", filters = filter_names, table = table)

@app.route("/watchlist", methods = ['GET', 'POST'])
def watchlist():
    if not signed_in():
        return redirect('/landing')
    
    
    
    return render_template("watchlist.html")
    

@app.route("/logout", methods = ['GET', 'POST'])
def logout():
    session.pop('username', None)
    session.clear()
    return render_template("landing.html", message="You have successfully logged out!")

def error(error_message):
    return render_template("error.html", error_message = error_message)

if __name__ == "__main__":
    app.debug = True
    app.run()