# from sqlalchemy import create_engine, db.Column, db.Integer, db.Float, db.String, MetaData, Table
# from sqlalchemy.orm import sessionmaker, mapper
# from sqlalchemy.ext.declarative import declarative_base
from flask_sqlalchemy import SQLAlchemy
from __init__ import db
from scrapper import scrap

# global categories, subcategories
categories = {"Electronics": "https://carousell.com/categories/electronics-7/",
              "Mobiles & Tablets": "https://carousell.com/categories/mobile-phones-215/"}

subcategories = {"Electronics": {"All": "",
                                 "Computers": "computers-tablets-213/",
                                 "TV & Entertainment Systems": "tvs-entertainment-systems-217/",
                                 "Audio": "audio-207/",
                                 "Computer Parts & Accessories": "computer-parts-accessories-214/",
                                 "Others": "electronics-others-218/"},
                 "Mobiles & Tablets": {"All": "",
                                       "iPhones": "iphones-1235/",
                                       "Android": "androidphones-1237/"}}


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
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer)
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
    active = db.Column(db.Boolean)

    def __init__(self, name, category, subcategory, url, active):
        self.name = name
        self.category = category
        self.subcategory = subcategory
        self.url = url
        self.active = active


class CrawlersToData(db.Model):
    __tablename__ = "crawlers_data"
    id = db.Column(db.Integer, primary_key=True)
    crawler_id = db.Column(db.Integer)
    data_id = db.Column(db.Integer)

    def __init__(self, crawler_id, data_id):
        self.crawler_id = crawler_id
        self.data_id = data_id


class Data(db.Model):
    __tablename__ = "data"
    data_id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    price = db.Column(db.Float)
    date = db.Column(db.String)
    link = db.Column(db.String)

    def __init__(self, name, price, date, link):
        self.name = name
        self.price = price
        self.date = date
        self.link = link


def create_user(email, password):
    new_user = User(email=email, password=password)
    if db.session.query(User).filter(User.email == new_user.email).count() == 0:
        db.session.add(new_user)
        db.session.commit()
        return True


def create_crawler(user, name, category, subcategory, url, status):
    if url:
        effective_url = url
    else:
        effective_url = categories[category] + subcategories[category][subcategory] + "?sort_by=time_created%2Cdescending"
    # create and add crawler
    new_crawler = Crawler(name, category, subcategory, effective_url, status)
    if db.session.query(Crawler).filter(Crawler.name == new_crawler.name).count() == 0:
        print("Crawler added")
        db.session.add(new_crawler)
        db.session.commit()

        # create and add relation to user
        userid = db.session.query(User.user_id).filter(User.email == user).first()
        crawlerid = db.session.query(Crawler.crawler_id).filter(Crawler.name == name).first()
        new_relation = UsersToCrawlers(userid, crawlerid)
        if db.session.query(UsersToCrawlers).filter(UsersToCrawlers.crawler_id == crawlerid).count() == 0:
            db.session.add(new_relation)
            db.session.commit()
        return True
    else:
        return False


def create_data(crawler, name, price, date, link):
    new_data = Data(name=name, price=price, date=date, link=link)
    # if listing of same name, price and date not already in database, add data to database
    if db.session.query(Data).filter(Data.name == new_data.name).\
                              filter(Data.date == new_data.date).\
                              filter(Data.price == new_data.price).count() == 0:
        db.session.add(new_data)
        db.session.commit()
        dataid = new_data.data_id
    else:
        # print(new_data.name, new_data.price, new_data.date)
        dataid = db.session.query(Data.data_id).filter(Data.name == new_data.name).\
                                                        filter(Data.date == new_data.date).\
                                                        filter(Data.price == new_data.price).first()
        # print(dataid)

    crawlerid = db.session.query(Crawler.crawler_id).filter(Crawler.name == crawler).first()
    # if crawler-data relation does not yet exist, add relation
    if crawlerid not in db.session.query(CrawlersToData.crawler_id).filter(CrawlersToData.data_id == dataid).all():
        new_relation = CrawlersToData(crawlerid, dataid)
        db.session.add(new_relation)
        db.session.commit()


def delete_crawler(crawler_name):
    print(crawler_name)
    crawlerid = db.session.query(Crawler.crawler_id).filter(Crawler.name == crawler_name).first()
    if crawlerid:  # if crawler exists
        crawler = db.session.query(Crawler).get(crawlerid)
        crawler_relation = db.session.query(UsersToCrawlers).get(crawlerid)
        db.session.delete(crawler)
        db.session.delete(crawler_relation)
        db.session.commit()

    # delete associated data and relation object
    related_data = []
    for relation_object in db.session.query(CrawlersToData).filter(CrawlersToData.crawler_id == crawlerid).all():
        related_data.append(relation_object.data_id)
        db.session.delete(relation_object)
        db.session.commit()
    for data in db.session.query(Data).filter(Data.data_id.in_(related_data)).all():
        db.session.delete(data)
        db.session.commit()


def delete_data(data_id):
    # crawlerid = db.session.query(Crawler.crawler_id).filter(Crawler.name == crawler_name).first()
    # if data_id:  # if crawler exists
    # dataid = db.session.query(Data.data_id).filter(Data.data_id == data_id).first()
    data = db.session.query(Data).get(data_id)
    data_relation = db.session.query(CrawlersToData).filter(CrawlersToData.data_id == data_id).first()
    db.session.delete(data)
    db.session.delete(data_relation)
    db.session.commit()


def delete_all_data():
    for i in db.session.query(Data).all():
        db.session.delete(i)
        db.session.commit()
    for i in db.session.query(CrawlersToData).all():
        db.session.delete(i)
        db.session.commit()


def scrap_into_database():
    print("Scrapping into database")
    crawlers = db.session.query(Crawler).all()
    for c in crawlers:
        data = scrap(c.url)
        for d in data:
            create_data(c.name, d["name"], d["price"], d["date"], d["link"])


db.create_all()
# delete_all_data()


# create_user(email="test1@mail.com", password="pw")
# create_crawler(user="test1@mail.com", name="h2", category="Electronics", subcategory="Audio", url="", status="activated")
# create_data("h2", "test_data", 5.0, "5/5/18")

