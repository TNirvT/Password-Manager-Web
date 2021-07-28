from os import path
from sys import platform

from flask import Flask
from flask_sqlalchemy import SQLAlchemy

from .pw_gen import phrase_gen

if platform.startswith("win32"):
    db_path = path.abspath("/.database/pwmngr.db")
else:
    db_path = path.expanduser("~/.database/pwmngr.db")

salt_path = db_path.replace(".db", ".salt")
secret_path = db_path.replace(".db", ".secr")
if not path.exists(secret_path):
    with open(secret_path, "w") as f:
        f.write(phrase_gen(18,22))
with open(secret_path) as f:
    secret_phrase = f.read()

flask_secret_path = db_path.replace(".db", "_flask.secr")
if not path.exists(flask_secret_path):
    with open(flask_secret_path, "w") as f:
        f.write(phrase_gen(18,22))
with open(flask_secret_path) as f:
    flask_secret_phrase = f.read()

secret_id = 1000

db = SQLAlchemy()

def create_app(test_config=None):
    app = Flask(__name__)
    app.config.from_mapping({
        "SQLALCHEMY_TRACK_MODIFICATIONS": False,
        "SECRET_KEY": flask_secret_phrase,
        "SQLALCHEMY_DATABASE_URI": f"sqlite:///{db_path}"
    })
    if test_config:
        app.config.from_mapping(test_config)
    db.init_app(app)
    from .models import PassRecord
    if not path.exists(db_path):
        db.create_all(app=app)
    from .views import views
    app.register_blueprint(views, url_prefix="/")

    return app