import os

from flask import Flask, session, render_template, request
from flask_session import Session
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
from sqlalchemy.sql import text


app = Flask(__name__)
# Check for environment variable
if not os.getenv("DATABASE_URL"):
    raise RuntimeError("DATABASE_URL is not set")

# Configure session to use filesystem
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)


# Set up database
engine = create_engine(os.getenv("DATABASE_URL"))
db = scoped_session(sessionmaker(bind=engine))


@app.route("/")
def index():

    return render_template("index.html")

@app.route("/login", methods=["POST","GET"])
def login():
    success  = 0
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        if not username or not password:
            return render_template("error.html",message = "Please fill out the form.")
        users = db.execute(text("SELECT * from users where username= :username"), {"username": username}).fetchall()
        db.commit()
        success = 1
        return render_template("login.html",success = success, users = users)
    return render_template("login.html",success = success)

@app.route("/register",methods=["GET","POST"])
def register():
    success  = 0
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        if not username or not password:
            return render_template("error.html",message = "Please fill out the form.")
        db.execute(text("INSERT INTO users (username, password) VALUES (:username, :password)"), {"username": username, "password": password})
        db.commit()
        success  = 1
    return render_template("register.html",success = success)

@app.route("/search",methods=["POST","GET"])
def search():
    success  = 0
    if request.method == "POST":
        title = request.form.get("title")
        isbn = request.form.get("isbn")
        author = request.form.get("author")
        if not title and not isbn and not author:
            return render_template("error.html",message = "Please fill at least one filed.")
        books = db.execute(text("SELECT * from books where isbn = :isbn or title = :title or author = :author"), {"isbn": isbn, "title": title, "author": author}).fetchall()
        db.commit()
        success = 1
        return render_template("search.html", success = success, books=books)
    return render_template("search.html",success = success)
@app.route("/<string:isbn>")#,methods=["GET","POST"]
#@app.route("/")
def book(isbn):
    values={'isbn': isbn}
    msg=text('SELECT title, author, year FROM books WHERE isbn= :isbn')
    ans=db.execute(msg,values)
    results= ans.first()
    title = results[0]
    author = results[1]
    year = results[2]
    return render_template("book.html", title=title,author=author,year=year)
