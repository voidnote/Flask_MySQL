from flask import Flask, request, redirect, render_template, session, flash
from mysqlconnection import MySQLConnector
import md5 # do this at the top of your file where you import modules
import os, binascii # include this at the top of your file
app = Flask(__name__)
mysql = MySQLConnector(app,"friendsdb")

@app.route("/")
def index():
    query = "SELECT * FROM friends"
    friends = mysql.query_db(query)
    return render_template("index.html", all_friends = friends)

# When you add your users to the database upon registration, you should save their passwords as an hashed md5 string. 
@app.route('/users/create', methods=['POST'])
def create_user():
    username = request.form['username']
    email = request.form['email']
    password = md5.new(request.form['password']).hexdigest();
    query = "INSERT INTO users (username, email, password, created_at, updated_at) VALUES (:username, :email, :password, NOW(), NOW())"
    data = { 'username': username, 'email': email, 'password': password }
    mysql.query_db(query, data)
    return redirect("/")

# when they log in, you should hash the input password to make sure it matches with the one saved in the database. 
@app.route("/friends", methods=["POST"])
def create():
    password = md5.new(request.form['password']).hexdigest()
    email = request.form['email']
    query = "SELECT * FROM users where users.email = :email AND users.password = :password"
    data = { 'email': email, 'password': password}
    user = mysql.query_db(query, data)
    # do the necessary logic to login if the user exists, otherwise redirect to login page with error message<br>
    return redirect("/")

# ---- WITH SALT VERSION ADDED ----

# When you add your users to the database upon registration, you should save their passwords as an hashed md5 string. 
@app.route('/users/create', methods=['POST'])
def create_user_v2():
    username = request.form['username']
    email = request.form['email']
    password = request.form['password']
    salt =  binascii.b2a_hex(os.urandom(15))
    encrypted_pw = md5.new(password + salt).hexdigest()
    query = "INSERT INTO users (username, email, password, salt, created_at, updated_at) VALUES (:username, :email, :encrypted_pw, :salt, NOW(), NOW())"
    data = { 'username': username, 'email': email, 'encrypted_pw': encrypted_pw, 'salt': salt}
    mysql.query_db(query, data)
    return redirect("/")

# when they log in, you should hash the input password to make sure it matches with the one saved in the database. 
@app.route("/friends", methods=["POST"])
def create_v2():
    email = request.form['email']
    password = request.form['password']
    user_query = "SELECT * FROM users WHERE users.email = :email LIMIT 1"
    query_data = {'email': email}
    user = mysql.query_db(user_query, query_data)
    if user[0]:
        encrypted_password = md5.new(password + user[0]['salt']).hexdigest();
        if user[0]['password'] == encrypted_password:
            # this means we have a successful login!
            pass
        else: 
            # invalid password!
            pass
    else: 
        # invalid email!
        pass
    return redirect("/")