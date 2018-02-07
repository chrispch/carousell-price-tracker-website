# from sqlalchemy import create_engine, db.Column, db.Integer, db.Float, db.String, MetaData, Table
# from sqlalchemy.orm import sessionmaker, mapper
# from sqlalchemy.ext.declarative import declarative_base
from flask_sqlalchemy import SQLAlchemy
from __init__ import app

categories = {"All": "https://carousell.com/",
              "Electronics": "https://carousell.com/categories/electronics-7/",
              "Mobiles & Tablets": "https://carousell.com/categories/mobile-phones-215/"}

subcategories = {"All": {"All": ""},
                 "Electronics": {"Computers": "computers-tablets-213/",
                                 "TV & Entertainment Systems": "tvs-entertainment-systems-217/",
                                 "Audio": "audio-207/",
                                 "Computer Parts & Accessories": "computer-parts-accessories-214/",
                                 "Others": "electronics-others-218/"},
                 "Mobiles & Tablets": {"iPhones": "iphones-1235/",
                                       "Android": "androidphones-1237/"}}

db = SQLAlchemy(app)

class User(db.Model):
    __tablename__ = "users"
    user_id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String, unique=True)
    password = db.Column(db.String)

    def __init__(self, email, password):
        self.email = email
        self.password = password


class UsersToCrawlers(db.Model):
    __tablename__ = "users_crawlers"
    user_id = db.Column(db.Integer, primary_key=True)
    crawler_id = db.Column(db.Integer)

    def __init__(self, user_id, crawler_id):
        self.user_id = user_id
        self.crawler_id = crawler_id


class Crawler(db.Model):
    __tablename__ = "crawlers"
    crawler_id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, unique=True)
    category = db.Column(db.String)
    subcategory = db.Column(db.String)
    url = db.Column(db.String)
    status = db.Column(db.String)

    def __init__(self, name, category, subcategory, url, status):
        self.name = name
        self.category = category
        self.subcategory = subcategory
        self.url = url
        self.status = status


class Data(db.Model):
    __tablename__ = "data"
    data_id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    price = db.Column(db.Float)
    date = db.Column(db.String)

    def __init__(self, data_id, name, price, date):
        self.data_id = data_id
        self.name = name
        self.price = price
        self.date = date


def create_user(email, password):
    new_user = User(email=email, password=password)
    if db.session.query(User).filter(User.email == new_user.email).count() == 0:
        db.session.add(new_user)
        db.session.commit()


def create_crawler(user, name, category, subcategory, url, status):
    if url:
        effective_url = url
    else:
        effective_url = categories[category] + subcategories[category][subcategory]
    # create and add crawler
    new_crawler = Crawler(name, category, subcategory, effective_url, status)
    if db.session.query(Crawler).filter(Crawler.name == new_crawler.name).count() == 0:
        print("Crawler added")
        db.session.add(new_crawler)
        db.session.commit()

    # create and add relation to user
    userid = db.session.query(User.user_id).filter(User.email == user).first()
    crawlerid = db.session.query(Crawler.crawler_id).filter(Crawler.name == name).first()
    relation = UsersToCrawlers(userid, crawlerid)
    if db.session.query(UsersToCrawlers).filter(UsersToCrawlers.crawler_id == crawlerid).count() == 0:
        db.session.add(relation)
        db.session.commit()

def delete_crawler(crawler_name):
    crawlerid = db.session.query(Crawler.crawler_id).filter(Crawler.name == crawler_name).first()
    if crawlerid:  # if crawler exists
        crawler = db.session.query(Crawler).get(crawlerid)
        crawler_relation = db.session.query(UsersToCrawlers).get(crawlerid)
        db.session.delete(crawler)
        db.session.delete(crawler_relation)
        db.session.commit()

# db.create_all()


create_user(email="test1@mail.com", password="pw")
create_crawler(user="test1@mail.com", name="h2", category="Electronics", subcategory="Audio", url="", status="activated")
# delete_crawler("h")