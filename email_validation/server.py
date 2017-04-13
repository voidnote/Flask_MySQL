from flask import Flask, request, redirect, render_template, session, flash
from mysqlconnection import MySQLConnector
import re
app = Flask(__name__)
mysql = MySQLConnector(app,"email_registration")
app.secret_key = "ThisIsSecret"
EMAIL_REGEX = re.compile(r'^[a-zA-Z0-9.+_-]+@[a-zA-Z0-9._-]+\.[a-zA-Z]+$')


@app.route("/")
def index():
    return render_template("index.html")

# def index():
#     query = "SELECT name, age, DATE_FORMAT(created_at, '%M %D') as date, DATE_FORMAT(created_at, '%Y') as year FROM friends"
#     friends = mysql.query_db(query)
#     return render_template("index.html", all_friends = friends)

@app.route("/new", methods=["POST"])
def new():
    if not EMAIL_REGEX.match(request.form['email']):
        flash("Invalid Email Address!")
        return redirect("/")
    else:
        flash("Thank you for registering")
        query = "INSERT INTO emails (email, created_at, updated_at) VALUES (:email, NOW(), NOW())"
        session["email"] = request.form["email"]
        data = {
            'email': request.form['email'],
           }
        mysql.query_db(query, data)  
    return redirect("/success")

@app.route("/success")
def success():
    query = "SELECT email, DATE_FORMAT(created_at, '%m/%d/%Y %h:%i%p') as date, id FROM emails"
    emails = mysql.query_db(query)
    return render_template("results.html", emails = emails)

@app.route("/delete/<id>", methods=["POST"])
def delete(id):
    query = "DELETE FROM emails WHERE id=:id"
    data = {
            'id': id,
           }
    mysql.query_db(query, data)  
    return redirect("/success")


app.run(debug=True)
