import flask
import requests, json, os
from dotenv import load_dotenv, find_dotenv
from random import randrange
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import exists

app = flask.Flask(__name__)

@app.route("/")
def send_to_signup():
    return flask.render_template("sign_up.html")


@app.route("/login")
def send_to_login():

    return flask.render_template("login.html")

app.run()