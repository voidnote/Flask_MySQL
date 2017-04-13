from flask import Flask, request, redirect, render_template, session, flash
from mysqlconnection import MySQLConnector
import re
app = Flask(__name__)
mysql = MySQLConnector(app,"email_registration")
app.secret_key = "ThisIsSecret"
EMAIL_REGEX = re.compile(r'^[a-zA-Z0-9.+_-]+@[a-zA-Z0-9._-]+\.[a-zA-Z]+$')

# renders the main index page
@app.route("/")
def index():
    return render_template("index.html")

# validates the email address that was entered, and sends it to the DB
@app.route("/new", methods=["POST"])
def new():
    session["email"] = request.form["email"]
    myEmail = session["email"]
    if not EMAIL_REGEX.match(request.form['email']):
        flash("Invalid Email Address!")
        return redirect("/")
    else:
        flash("The email address you entered ")
        flash(session["email"])
        flash(" is a VALID email address. Thank you.")
        query = "INSERT INTO emails (email, created_at, updated_at) VALUES (:email, NOW(), NOW())"
        data = {
            'email': session["email"],
           }
        mysql.query_db(query, data)  
    return redirect("/success")

# displays all of the email addresses entered
@app.route("/success")
def success():
    query = "SELECT email, DATE_FORMAT(created_at, '%m/%d/%Y %h:%i%p') as date, id FROM emails"
    emails = mysql.query_db(query)
    return render_template("results.html", emails = emails)

# deletes the chosen email address
@app.route("/delete/<id>", methods=["POST"])
def delete(id):
    query = "DELETE FROM emails WHERE id=:id"
    data = {
            'id': id,
           }
    mysql.query_db(query, data)  
    return redirect("/success")


app.run(debug=True)
