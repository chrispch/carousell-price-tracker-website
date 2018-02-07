from sqlalchemy import create_engine, Column, Integer, Float, String, MetaData, Table
from sqlalchemy.orm import sessionmaker, mapper
from sqlalchemy.ext.declarative import declarative_base

engine = create_engine('postgresql://postgres:hern3010@localhost/price-tracker', echo=True)
Base = declarative_base()
metadata = MetaData()

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


class Db(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True)
    email = Column(String, unique=True)
    password = Column(String)


class User(object):  # object inheritance is for Python 2 backwards compatibility
    def __init__(self, email, password):
        self.email = email
        self.password = password


class Crawler(object):
    def __init__(self, name, category, subcategory, url, status):
        self.name = name
        self.category = category
        self.subcategory = subcategory
        self.url = url
        self.status = status


class Data(object):
    def __init__(self, name, price, date):
        self.name = name
        self.price = price
        self.data = data


def create_user(email, password):
    new_user = Db(email=email, password=password)
    create_user_table(email)
    return new_user


def add_user(user):
    Session = sessionmaker(bind=engine)
    session = Session()
    if session.query(Db).filter(Db.email == user.email).count() == 0:
        session.add(user)
        session.commit()
        session.close()


def create_user_table(email):
    # Creates a table belonging to user:email which contains user's crawlers
    user_table = Table(email, metadata,
                        Column("id", Integer, primary_key=True),
                        Column("name", String, unique=True),
                        Column("category", String),
                        Column("subcategory", String),
                        Column("url", String),
                        Column("status", String)
                       )
    metadata.create_all(engine)
    mapper(Crawler, user_table)


def create_crawler(name, category, subcategory, url, status):
    if url != "":
        effective_url = categories[category] + subcategories[category][subcategory]
    else:
        effective_url = url
    new_crawler = Crawler(name, category, subcategory, effective_url, status)
    return new_crawler


def add_crawler(crawler):
    Session = sessionmaker(bind=engine)
    session = Session()
    if session.query(Crawler).filter(Crawler.name == crawler.name).count() == 0:
        session.add(crawler)
        session.commit()
        session.close()




# def delete_crawler(crawler):

Base.metadata.create_all(engine)


# Session = sessionmaker(bind=engine)
# session = Session()
#
new_user = create_user("test2@mail.com", "password")
add_user(new_user)
new_crawler = create_crawler("hi", "electronics", "audio", "", "active")
add_crawler(new_crawler)
#
# session.add(Crawler(name="h", category="e", subcategory="y", url="!", status="active"))
#
# session.commit()
# session.close()
# c1 = create_crawler("hi", "electronics", "audio", "")
# add_crawler(c1)
