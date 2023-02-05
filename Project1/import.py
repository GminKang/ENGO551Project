import csv
import os
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
from sqlalchemy.sql import text

DBurl= input('What is your local database URL? \n') #postgresql://postgres:991220@localhost/bookreview

engine = create_engine(DBurl)
db=scoped_session(sessionmaker(bind=engine))


def main():
    f =open("books.csv")
    reader = csv.reader(f)

    db.execute(text("CREATE TABLE IF NOT EXISTS books (isbn VARCHAR(15) NOT NULL PRIMARY KEY,title VARCHAR NOT NULL,author VARCHAR (80) NOT NULL,year VARCHAR(4))"))
    db.execute(text("CREATE TABLE IF NOT EXISTS users (userid SERIAL NOT NULL PRIMARY KEY UNIQUE, username VARCHAR NOT NULL, password VARCHAR (13) NOT NULL )"))
    db.execute(text("CREATE TABLE IF NOT EXISTS reviews ( user_id INT REFERENCES users(userid), book_id VARCHAR(15) REFERENCES books(isbn), content VARCHAR NOT NULL )"))



    for isbn, title, author,year in reader:
        db.execute(text("INSERT INTO books (isbn, title, author, year) VALUES (:isbn, :title, :author, :year)"),
            {"isbn":isbn, "title": title, "author": author, "year": year})
        print(f"Added ISBN - {isbn} with Book Title: {title} by {author}, year: {year}")
    db.commit()

if __name__ == "__main__":
    main()
