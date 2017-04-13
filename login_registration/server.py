from flask import Flask, render_template, request, redirect, session, flash
from mysqlconnection import MySQLConnector
from datetime import datetime
import os, binascii, md5, re

app = Flask(__name__)
app.secret_key = "ThisIsSecret"
EMAIL_REGEX = re.compile(r'^[a-zA-Z0-9.+_-]+@[a-zA-Z0-9._-]+\.[a-zA-Z]+$')
mysql = MySQLConnector(app,"login_registration")

@app.route("/")
def index():
  return render_template("index.html")

# route that handles the main registration process
@app.route("/register", methods=["POST"])
def process():
  errors = 0
  if len(request.form["first_name"]) < 1 or len(request.form["last_name"]) < 1 or len(request.form["email"]) < 1 or len(request.form["password"]) < 1 or len(request.form["pw_confirm"]) < 1:
    flash("Fields cannot be empty!")
    errors += 1
  if not request.form["first_name"].isalpha() or not request.form["last_name"].isalpha():
    flash("Only letters allowed for first and last name")
    errors += 1
  if not EMAIL_REGEX.match(request.form['email']):
    flash("Invalid Email Address!")
    errors += 1
  if len(request.form["password"]) < 8:
    flash("Password must be at least 8 characters")
    errors += 1
  if request.form["password"] != request.form["pw_confirm"]:
    flash("Password didn't match confirmation. Please try again.")
    errors += 1

  # check if the email already exists in the database
  query = "SELECT * FROM users WHERE users.email = :email LIMIT 1"
  data = {'email': request.form['email']}
  user = mysql.query_db(query, data)
  if request.form["email"] == user[0]["email"]:
    flash("This email is already registered. Please login instead.")
    errors += 1
  
  if errors > 0:
    return redirect("/")

  # create hashing
  password = request.form['password']
  salt = binascii.b2a_hex(os.urandom(15))
  encrypted_pw = md5.new(password + salt).hexdigest()

  # submit data to the DB
  query = "INSERT INTO users (first_name, last_name, email, password, salt, created_at, updated_at) VALUES (:first_name, :last_name, :email, :password, :salt, NOW(), NOW())"
  data = {
        "first_name": request.form["first_name"],
        "last_name": request.form["last_name"], 
        "email": request.form["email"],
        "salt":  salt,
        "password": encrypted_pw
          }
  mysql.query_db(query, data)

  # flash the thank you message on the show page
  session["first_name"] = request.form["first_name"]
  flash("Thank you ")
  flash(session["first_name"])
  flash(" for registering!")
  return redirect("/show")

# route for checking the login information that is submitted
@app.route("/login", methods=["POST"])
def login():
  errors = 0
  if len(request.form["email"]) < 1 or len(request.form["password"]) < 1:
    flash("Fields cannot be empty!")
    errors += 1
  if not EMAIL_REGEX.match(request.form['email']):
    flash("Invalid Email Address!")
    errors += 1
  if len(request.form["password"]) < 8:
    flash("Password must be at least 8 characters")
    errors += 1
  if errors > 0:
    return redirect("/")

  # we look up the user's email address and check the password match
  email = request.form['email']
  password = request.form['password']
  query = "SELECT * FROM users WHERE users.email = :email LIMIT 1"
  data = {'email': email}
  user = mysql.query_db(query, data)
  
  if user[0]:
    encrypted_password = md5.new(password + user[0]['salt']).hexdigest()
    if user[0]['password'] == encrypted_password:
      session["first_name"] = user[0]["first_name"]
      flash("Thank you ")
      flash(session["first_name"])
      flash(" for signing in!")
      return redirect("/show")
    else:
      flash("Password is incorrect. Please try again.")
      return redirect("/")
  else:
    flash("Email not found. Please try again.")
    return redirect("/")

@app.route("/show")
def show():
  return render_template("show.html")

app.run(debug=True)