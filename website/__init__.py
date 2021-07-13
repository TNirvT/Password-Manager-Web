from os import path
from sys import platform

from flask import Flask
from flask_sqlalchemy import SQLAlchemy

if platform.startswith("win32"):
    db_path = path.abspath("/.database/pwmngr.db")
else:
    db_path = path.expanduser("~/.database/pwmngr.db")

secret_id = 1000

db = SQLAlchemy()

def create_app():
    app = Flask(__name__)
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['SECRET_KEY'] = "secret" # change this!
    app.config["SQLALCHEMY_DATABASE_URI"] = f"sqlite:///{db_path}"
    db.init_app(app)
    from .models import PassRecord
    if not path.exists(db_path): db.create_all(app=app)
    from .views import views
    app.register_blueprint(views, url_prefix="/")

    return app