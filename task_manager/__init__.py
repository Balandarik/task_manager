from flask import Flask, render_template, url_for, request, redirect
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_mail import Mail
import configparser
config = configparser.ConfigParser()
config.read("config.ini")
UPLOAD_FOLDER = './task_manager/media/'
ALLOWED_EXTENSIONS = set(['txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif','doc','docx'])

app=Flask(__name__)

app.secret_key=config["SECRET_KEY"]["key"]
app.config['SQLALCHEMY_DATABASE_URI']=config["SQL_LIGHT"]["name"]
app.config['SQLALCHEMY_TRACK_MODIFICATIONS']=False
app.config['MAIL_SERVER'] = config["MAIL_SERVER"]["server"]
app.config['MAIL_PORT'] = config["MAIL_PORT"]["port"]
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = config["MAIL_USERNAME"]["username"]
app.config['MAIL_DEFAULT_SENDER'] = config["MAIL_DEFAULT_SENDER"]["default_sender"]
app.config['MAIL_PASSWORD'] = config["MAIL_PASSWORD"]["mail_password"]
mail=Mail(app)
db=SQLAlchemy(app)
login_manager=LoginManager(app)
login_manager.login_view='login'
from task_manager import models, routes