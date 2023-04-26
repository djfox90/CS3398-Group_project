import flask
from flask import  request
import requests, json, os
from dotenv import load_dotenv, find_dotenv
from random import randrange
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import exists
import spotifyAPI as sp
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

class Artist(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=False, nullable=False)
    artist = db.Column(db.String(300), unique=False, nullable=False)
    song = db.Column(db.String(300), unique=False, nullable=False)

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


@app.route("/main/<user>", methods=['GET'])
@login_required
def send_to_main(user):
   
    a = Artist.query.all()
   
    song_name=request.args.get('song_name')
    
    song_artist=request.args.get('song_artist')
    if(song_name != "None"):
        art=sp.getSongArt(sp.request_auth(),song_name)
        print(art)
    else:
        art=None
    return flask.render_template(
        "main.html",
        user=user,
        song_lists=a,
        song=song_name,
        artist=song_artist,
        art=art

    )

@app.route("/music-selection", methods=["GET", "POST"])
def find_song():
    form_data = flask.request.form
    artist = form_data["artist"]
    artist_list=[artist]
    genres = form_data["genres"]
    genres_list=[genres]
    track = form_data["track"]
    track_list =[track]
    user = form_data["user"]
    
    
    song = sp.get_recommendations(sp.request_auth(), artists=artist_list, genres=genres_list, tracks=track_list)['tracks'][0]
    
    song_name = song['name']
    song_artist=song['artists'][0]['name']
   
    

    return flask.redirect(flask.url_for("send_to_main",user=user,song_name=song_name, song_artist=song_artist))#sent to login to test
@app.route("/music-database", methods=["GET", "POST"])
def music_database():
    form_data = flask.request.form
    song = form_data["song_name"]
    artist = form_data["song_artist"]
    user=form_data["user"]
    artist_found = Artist(username=user, artist = artist, song = song)
    
    db.session.add(artist_found)

    db.session.commit()
    return flask.redirect(flask.url_for("send_to_main",user=user))
    
@app.route("/logout", methods=["GET", "POST"])
@login_required
def logout():
    logout_user()
    flask.flash("Signed out")
    return flask.redirect(flask.url_for("send_to_login"))
app.run()
