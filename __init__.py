from flask import Flask, request, session, redirect, url_for, render_template, flash
from database import *
from passlib.hash import sha256_crypt

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI']='postgresql://postgres:hern3010@localhost/price-tracker'
app.secret_key = b'_5#y2L"F4Q8z\n\xec]/'
db = SQLAlchemy(app)

preview_content = None


@app.route('/')
def home():
    return render_template("home.html", database_nav="nav-link",
                                   crawlers_nav="nav-link")


@app.route('/login', methods=["GET", "POST"])
def login():
    if request.method == "GET":
        return redirect(url_for("home"))
    elif request.method == "POST":
        email = request.form["email"]
        password = request.form["password"]
        if db.session.query(User).filter(User.email == email).count() == 0:
            flash("Email is not registered. Please register before logging in.")
            return redirect(url_for("home"))
        else:
            encrypted_password = db.session.query(User.password).filter(User.email == email).first()[0]
            if sha256_crypt.verify(password, encrypted_password):
                session["logged_in"] = True
                session["user_email"] = email
                return redirect(url_for("home"))
            else:
                flash("Password is incorrect. Please try again.")
                return redirect(url_for("home"))


@app.route('/register', methods=["GET", "POST"])
def register():
    if request.method == "GET":
        return redirect(url_for("home"))
    elif request.method == "POST":
        email = request.form["email"]
        password = sha256_crypt.encrypt(request.form["password"])
        if create_user(email, password):
            session['logged_in'] = True
            session["user_email"] = email
            return redirect(url_for("home"))
        else:
            flash("Email is already in use, please try again.")
            return redirect(url_for("home"))


@app.route('/logout', methods=["GET", "POST"])
def logout():
    session['logged_in'] = False
    return redirect(url_for("home"))


@app.route('/crawlers', methods=["GET", "POST"])
def crawlers():
    try:
        # get user's crawlers
        active_crawlers = []
        inactive_crawlers = []
        user_id = db.session.query(User.user_id).filter(User.email == session["user_email"]).first()
        crawler_ids = db.session.query(UsersToCrawlers.crawler_id).filter(UsersToCrawlers.user_id == user_id).all()
        for crawler_id in crawler_ids:
            crawler = db.session.query(Crawler).filter(Crawler.crawler_id == crawler_id).first()
            crawler_info = {}
            crawler_info["name"] = crawler.name
            crawler_info["category"] = crawler.category
            crawler_info["subcategory"] = crawler.subcategory
            crawler_info["url"] = crawler.url
            crawler_info["active"] = crawler.active
            # active crawlers
            if crawler_info["active"]:
                active_crawlers.append(crawler_info)
            else:
                inactive_crawlers.append(crawler_info)

        if request.method == "POST":
            current_category = request.form["category"]
            current_name = request.form["name"]
            current_url = request.form["url"]
            return render_template("crawlers.html", categories=categories,
                                   subcategories=subcategories[current_category],
                                   current_category=current_category,
                                   name=current_name, url=current_url, database_nav="nav-link",
                                   crawlers_nav="nav-link active", active_crawlers=active_crawlers,
                                   inactive_crawlers=inactive_crawlers)

        elif request.method == "GET":
            if session["logged_in"]:
                # on first loading crawlers.html
                return render_template("crawlers.html", categories=categories, subcategories=subcategories["All"],
                                       current_category="All", name="", url="", database_nav="nav-link",
                                       crawlers_nav="nav-link active", active_crawlers=active_crawlers,
                                   inactive_crawlers=inactive_crawlers)
            else:
                return redirect(url_for("home"))
    except Exception as e:
        return render_template("error.html", error=e)


@app.route('/database', methods=["GET", "POST"])
def database():
    if request.method == "POST":
        pass
    elif request.method == "GET":
        if session["logged_in"]:
            return render_template("database.html", database_nav="nav-link active", crawlers_nav="nav-link")
        else:
            return redirect(url_for("home"))


@app.route('/add', methods=["GET", "POST"])
def add():
    if request.method == "GET":
        return redirect(url_for("home"))
    elif request.method == "POST":
        current_name = request.form["name"]
        current_category = request.form["category"]
        current_subcategory = request.form["subcategory"]
        current_url = request.form["url"]
        current_user = session["user_email"]
        create_crawler(current_user, current_name, current_category, current_subcategory, current_url, True)
        flash("Crawler '{}' added successfully!".format(current_name))
        return redirect(url_for("crawlers"))


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
        return redirect(url_for("home"))
    elif request.method == "POST":
        return redirect(url_for("database"))


@app.route('/rename_crawler', methods=["GET", "POST"])
def rename_crawler():
    if request.method == "GET":
        return redirect(url_for("home"))
    elif request.method == "POST":
        return redirect(url_for("database"))


@app.route('/info_crawler', methods=["GET", "POST"])
def info_crawler():
    if request.method == "GET":
        return redirect(url_for("home"))
    elif request.method == "POST":
        return redirect(url_for("database"))


@app.route('/start_crawler', methods=["GET", "POST"])
def start_crawler():
    if request.method == "GET":
        return redirect(url_for("home"))
    elif request.method == "POST":
        return redirect(url_for("database"))


@app.route('/stop_crawler', methods=["GET", "POST"])
def stop_crawler():
    if request.method == "GET":
        return redirect(url_for("home"))
    elif request.method == "POST":
        return redirect(url_for("database"))


if __name__ == "__main__":
    app.debug = True
    app.run()


