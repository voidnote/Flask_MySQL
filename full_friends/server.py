from flask import Flask, request, redirect, render_template, session, flash
from mysqlconnection import MySQLConnector
app = Flask(__name__)
mysql = MySQLConnector(app,"full_friendship")

@app.route("/")
def index():
    query = "SELECT name, age, DATE_FORMAT(created_at, '%M %D') as date, DATE_FORMAT(created_at, '%Y') as year FROM friends"
    friends = mysql.query_db(query)
    return render_template("index.html", all_friends = friends)

@app.route("/new", methods=["POST"])
def new():
    # session["date_format"] = "%Y-%m-%d"
    # Write query as a string. Notice how we have multiple values
    # we want to insert into our query.
    query = "INSERT INTO friends (name, age, created_at, updated_at) VALUES (:name, :age, NOW(), NOW())"
    # We'll then create a dictionary of data from the POST data received.
    data = {
            'name': request.form['name'],
            'age':  request.form['age'],
           }
    # Run query, with dictionary values injected into the query.
    mysql.query_db(query, data)  
    return redirect("/")


app.run(debug=True)
