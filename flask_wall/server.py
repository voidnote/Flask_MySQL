from flask import Flask, render_template, request, redirect, session, flash
from mysqlconnection import MySQLConnector
from datetime import datetime
import os, binascii, md5, re

app = Flask(__name__)
app.secret_key = "ThisIsSecret"
EMAIL_REGEX = re.compile(r'^[a-zA-Z0-9.+_-]+@[a-zA-Z0-9._-]+\.[a-zA-Z]+$')
mysql = MySQLConnector(app,"flask_wall")

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
  if user:
    flash("This email is already registered. Please login instead.")
    errors += 1

  if errors > 0:
    return redirect("/")

  # create hashing
  password = request.form['password']
  salt = binascii.b2a_hex(os.urandom(15))
  encrypted_pw = md5.new(password + salt).hexdigest()

  # submit data to the DB
  query = "INSERT INTO users (first_name, last_name, email, password, created_at, updated_at, salt) VALUES (:first_name, :last_name, :email, :password, NOW(), NOW(), :salt)"
  data = {
        "first_name": request.form["first_name"],
        "last_name": request.form["last_name"], 
        "email": request.form["email"],
        "password": encrypted_pw,
        "salt":  salt
          }
  mysql.query_db(query, data)

  # flash the thank you message on the show page
  session["first_name"] = request.form["first_name"]

  query = "SELECT * FROM users WHERE users.email = :email LIMIT 1"
  data = {'email': request.form["email"]}
  user = mysql.query_db(query, data)
  session["user_id"] = user[0]["id"]

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
      
      query = "SELECT * FROM users WHERE users.email = :email LIMIT 1"
      data = {'email': request.form["email"]}
      user = mysql.query_db(query, data)
      session["user_id"] = user[0]["id"]
      
      return redirect("/show")
    else:
      flash("Password is incorrect. Please try again.")
      return redirect("/")
  else:
    flash("Email not found. Please try again.")
    return redirect("/")

@app.route("/show")
def show():
  if "user_id" in session:
    
    query1 = "SELECT messages.id, CONCAT(first_name , ' ', last_name) as name, message, DATE_FORMAT(messages.created_at, '%M %D %Y') as date FROM messages JOIN users ON messages.user_id = users.id"
    messages = mysql.query_db(query1)

    query2 = "SELECT comments.id, comments.message_id, CONCAT(first_name , ' ', last_name) as name, comments, DATE_FORMAT(comments.created_at, '%M %D %Y') as date FROM comments JOIN users ON comments.user_id = users.id JOIN messages ON messages.id = comments.message_id"
    comments = mysql.query_db(query2)

    return render_template("show.html", all_messages = messages, all_comments = comments)

  else:
    return redirect("/")

@app.route("/logout", methods=["POST"])
def logout():
  session.clear()
  return redirect("/")

@app.route("/postpost", methods=["POST"])
def postpost():
  query = "INSERT INTO messages (message, created_at, updated_at, user_id) VALUES (:message, NOW(), NOW(), :user_id)"
  data = {
      "message": request.form["postpost"],
      "user_id": session["user_id"]
        }
  mysql.query_db(query, data)
  return redirect("/show")

@app.route("/commoncomment", methods=["POST"])
def commoncomment():
  query = "INSERT INTO comments (comments, created_at, updated_at, user_id, message_id) VALUES (:comment, NOW(), NOW(), :user_id, :message_id)"
  data = {
      "comment": request.form["commoncomment"],
      "user_id": session["user_id"],
      "message_id": request.form["message_id"]
        }
  mysql.query_db(query, data)
  return redirect("/show")

app.run(debug=True)