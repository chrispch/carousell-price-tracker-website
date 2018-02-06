from flask import Flask, request, session, g, redirect, url_for, abort, render_template, flash
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "postgresql://postgres:hern3010@localhost/price-tracker"
db = SQLAlchemy(app)

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

preview_content = None


class Data(db.Model):
    __tablename__ = "data"
    price = db.Column(db.Float, primary_key = True)
    name = db.Column(db.String)

    def __init__(self):
        self.price = price
        self.name = name


@app.route('/')
def home():
    return redirect(url_for("crawlers"))


@app.route('/crawlers', methods=["GET", "POST"])
def crawlers():
    error = None
    try:
        if request.method == "POST":
            current_category = request.form["category"]
            current_name = request.form["name"]
            current_search = request.form["search"]
            return render_template("crawlers.html", categories=categories,
                                   subcategories=subcategories[current_category],
                                   current_category=current_category,
                                   name=current_name, search=current_search)

        elif request.method == "GET":
            # on first loading crawlers.html
            return render_template("crawlers.html", categories=categories, subcategories=subcategories["All"],
                                   current_category="All", name="", search="")
    except Exception as e:
        return render_template("error.html", error=e)


@app.route('/database')
def database():
    return render_template("database.html")


@app.route('/add', methods=["GET", "POST"])
def add():
    if request.method == "GET":
        return redirect(url_for("/"))
    elif request.method == "POST":
        return redirect(url_for("database"))


@app.route('/preview', methods=["GET", "POST"])
def preview():
    try:
        if request.method == "POST":
            # add preview content
            global preview_content
            current_category = request.form["category"]
            current_name = request.form["name"]
            current_search = request.form["search"]
            current_subcategory = request.form["subcategory"]
            preview_content = current_subcategory
            return render_template("crawlers.html", categories=categories,
                                   subcategories=subcategories[current_category],
                                   current_category=current_category, current_subcategory=current_subcategory,
                                   name=current_name, search=current_search,
                                   preview_content=preview_content)

        elif request.method == "GET":
            # on first loading crawlers.html
            global preview_content
            preview_content = None
            return render_template("crawlers.html", categories=categories, subcategories=subcategories["All"],
                                   current_category="All", name="", search="")
    except Exception as e:
        return render_template("error.html", error=e)


if __name__ == "__main__":
    app.debug = True
    app.run()


