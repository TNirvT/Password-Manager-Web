from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from .pw_encrypt import db_path, secret_phrase
from os.path import exists

db = SQLAlchemy()

def create_app():
    app = Flask(__name__)
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['SECRET_KEY'] = secret_phrase
    app.config["SQLALCHEMY_DATABASE_URI"] = f"sqlite:///{db_path}"
    db.init_app(app)
    from .models import PassRecord
    if not exists(db_path): db.create_all(app=app)
    from .views import views
    app.register_blueprint(views, url_prefix="/")

    return app