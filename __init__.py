from flask import Flask, request, session, g, redirect, url_for, abort, render_template, flash
from database import *

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI']='postgresql://postgres:hern3010@localhost/price-tracker'


preview_content = None

active_crawlers = []
inactive_crawlers = []



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
            current_url = request.form["url"]
            return render_template("crawlers.html", categories=categories,
                                   subcategories=subcategories[current_category],
                                   current_category=current_category,
                                   name=current_name, url=current_url)

        elif request.method == "GET":
            # on first loading crawlers.html
            return render_template("crawlers.html", categories=categories, subcategories=subcategories["All"],
                                   current_category="All", name="", url="")
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
        current_name = request.form["name"]
        current_category = request.form["category"]
        current_subcategory = request.form["subcategory"]
        current_url = request.form["url"]
        if current_name == "":
            # name input missing
            flash("Please enter a name")
            return render_template("crawlers.html", categories=categories,
                                   subcategories=subcategories[current_category],
                                   current_category=current_category, current_subcategory=current_subcategory,
                                   name=current_name, url=current_url,
                                   preview_content=preview_content)
        else:
            add_crawler(current_name, current_category, current_subcategory, current_url)
            return redirect(url_for("/add"))


@app.route('/preview', methods=["GET", "POST"])
def preview():
    try:
        if request.method == "POST":
            # add preview content
            global preview_content
            current_category = request.form["category"]
            current_name = request.form["name"]
            current_url = request.form["url"]
            current_subcategory = request.form["subcategory"]
            preview_content = current_subcategory
            return render_template("crawlers.html", categories=categories,
                                   subcategories=subcategories[current_category],
                                   current_category=current_category, current_subcategory=current_subcategory,
                                   name=current_name, url=current_url,
                                   preview_content=preview_content)

        elif request.method == "GET":
            # on first loading crawlers.html
            global preview_content
            preview_content = None
            return render_template("crawlers.html", categories=categories, subcategories=subcategories["All"],
                                   current_category="All", name="", url="")
    except Exception as e:
        return render_template("error.html", error=e)


@app.route('/delete_crawler', methods=["GET", "POST"])
def delete_crawler():
    if request.method == "GET":
        return redirect(url_for("/"))
    elif request.method == "POST":
        return redirect(url_for("database"))


@app.route('/rename_crawler', methods=["GET", "POST"])
def rename_crawler():
    if request.method == "GET":
        return redirect(url_for("/"))
    elif request.method == "POST":
        return redirect(url_for("database"))


@app.route('/info_crawler', methods=["GET", "POST"])
def info_crawler():
    if request.method == "GET":
        return redirect(url_for("/"))
    elif request.method == "POST":
        return redirect(url_for("database"))


@app.route('/start_crawler', methods=["GET", "POST"])
def start_crawler():
    if request.method == "GET":
        return redirect(url_for("/"))
    elif request.method == "POST":
        return redirect(url_for("database"))


@app.route('/stop_crawler', methods=["GET", "POST"])
def stop_crawler():
    if request.method == "GET":
        return redirect(url_for("/"))
    elif request.method == "POST":
        return redirect(url_for("database"))


if __name__ == "__main__":
    app.debug = True
    app.run()


