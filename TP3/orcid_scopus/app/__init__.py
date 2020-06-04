from flask import Flask
from flask_pymongo import PyMongo
from flask_apscheduler import APScheduler

app = Flask(__name__)

app.config["MONGO_URI"] = "mongodb://localhost:27017/is_tp3"
mongo = PyMongo(app)

scheduler = APScheduler()
scheduler.init_app(app)
scheduler.start()

from app import routes