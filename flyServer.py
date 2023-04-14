import flask
import requests, json, os
from dotenv import load_dotenv, find_dotenv
from random import randrange
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import exists
from flask_login import (
    UserMixin,
    login_user,
    LoginManager,
    login_required,
    logout_user,
)

app = flask.Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv("DATABASE_URL")
app.secret_key = os.getenv("SECRET_KEY")
db = SQLAlchemy(app)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login"

class Person(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    
with app.app_context():
    db.create_all()

@login_manager.user_loader
def load_user(user_id):
    return Person.query.get(int(user_id))

@app.route("/")
def send_to_signup():
    return flask.render_template("sign_up.html")

@app.route("/create", methods=["GET", "POST"])
def create_user():
    form_data = flask.request.form
    username = form_data["username"]
    person = Person(username=username)

    exist = db.session.query(
        exists().where(Person.username == person.username)
    ).scalar()

    if exist:

        flask.flash("This username is already take please select a new one")
        return flask.redirect(flask.url_for("send_to_signup"))
    else:
        db.session.add(person)
        db.session.commit()
        flask.flash("Account created")
        return flask.redirect(flask.url_for("send_to_login"))


@app.route("/login")
def send_to_login():

    return flask.render_template("login.html")

@app.route("/check", methods=["GET", "POST"])
def check_user():
    form_data = flask.request.form
    username = form_data["username"]
    person = Person(username=username)

    user = Person.query.filter_by(username=username).first()

    exist = db.session.query(
        exists().where(Person.username == person.username)
    ).scalar()

    if exist:
        user.authenticated = True
        login_user(user)
        return flask.redirect(flask.url_for("send_to_main", user=str(person.username)))
    else:

        flask.flash("This username is incorrect please try again or create an account")
        return flask.redirect(flask.url_for("send_to_login"))

@app.route("/main/<user>")
@login_required
def send_to_main(user):

    return flask.render_template(
        "main.html",
    )



app.run()