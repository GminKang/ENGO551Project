
import os


from flask import Flask, session, render_template, request
from flask_session import Session
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
from sqlalchemy.sql import text
import requests


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


@app.route("/", methods=['GET', 'POST'])
def index():

    return render_template("index.html")

@app.route("/login", methods=["POST","GET"])
def login():
    success  = 0
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        session['username'] = username
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
        elif not title:
            if not isbn:
                books = db.execute(text("SELECT * from books where author like :author"), {"author": '%' + author + '%'}).fetchall()
            elif not author:
                books = db.execute(text("SELECT * from books where isbn like :isbn"), {"isbn": '%' + isbn + '%'}).fetchall()
            else:
                books = db.execute(text("SELECT * from books where isbn like :isbn and author like :author"), {"isbn": '%' + isbn + '%',"author": '%' + author + '%'}).fetchall()
        else:
            if not isbn:
                books = db.execute(text("SELECT * from books where title like :title and author like :author"), {"title": '%' + title + '%',"author": '%' + author + '%'}).fetchall()
            elif not author:
                books = db.execute(text("SELECT * from books where isbn like :isbn and title like :title"), {"isbn": '%' + isbn + '%',"title": '%' + title + '%'}).fetchall()
            else:
                books = db.execute(text("SELECT * from books where title like :title"), {"title": '%' + title + '%'}).fetchall()



        db.commit()
        success = 1
        return render_template("search.html", success = success, books=books)
    return render_template("search.html",success = success)

@app.route("/<string:isbn>", methods=['GET', 'POST'])#,methods=["GET","POST"]
#@app.route("/")
def book(isbn):
    values={'isbn': isbn}
    msg=text('SELECT title, author, year FROM books WHERE isbn= :isbn')
    ans=db.execute(msg,values)
    results= ans.first()
    #title = results[0]
    #author = results[1]
    #year = results[2]
    #Below are to find the review content
    review_ex=text('SELECT u.username,r.content,r.ratings FROM reviews AS r LEFT JOIN users as u ON u.userid=r.user_id WHERE r.book_id= :isbn')
    ans2=db.execute(review_ex,values).fetchall()
    db.commit()




    #content="\n ".join(": ".join(str(x) for x in row) for row in ans2)
    try:
        str1="".join(["isbn:", isbn])
        res = requests.get("https://www.googleapis.com/books/v1/volumes", params={"q": str1})
        title=res.json()["items"][0]["volumeInfo"]["title"]
        author=res.json()["items"][0]["volumeInfo"]["authors"]
        year=res.json()["items"][0]["volumeInfo"]["publishedDate"]

        rating=res.json()["items"][0]["volumeInfo"]["averageRating"]
        count=res.json()["items"][0]["volumeInfo"]["ratingsCount"]
        ISBN13=res.json()["items"][0]["volumeInfo"]["industryIdentifiers"][0]["identifier"]

        rating_u=0
        if res.status_code != 200:
            raise Exception ("ERROR: API reqst unsuccessful")


        if request.method=='POST':

            review = request.form.get("review")
            rat=request.form.get("rating_u")
            t_values={'username': session['username']}
            t_msg=text('SELECT userid FROM users WHERE username= :username')
            t_uid=db.execute(t_msg,t_values).fetchall()[0][0]
            db.execute(text("INSERT INTO reviews VALUES (:userid, :book, :content, :ratings)"), {"userid": t_uid, "book": isbn, "content": review, "ratings": rat})
            db.commit()
            success  = 1
            rating_u=rat
    except KeyError:
        return render_template("error.html",message = "404 not found")

    return render_template("book.html", title=title,author=author,year=year,content=ans2, ISBN=isbn, ISBN13=ISBN13,rating=rating,count=count,rating_u=rating_u)
