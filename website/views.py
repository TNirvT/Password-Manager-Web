from os import remove
from shutil import copy
from datetime import datetime

from flask import Blueprint, render_template, request, redirect, url_for, flash, make_response, session
import tldextract

from .master_key import MasterKey
from .pw_gen import pwgen
from .models import PassRecord
from . import db, secret_id, db_path

views = Blueprint("views", __name__)

#############################

def add_session(key):
    session["key"] = key

def remove_session():
    session.pop("key")

def validate_session():
    key = session.get("key", None)
    if not key:
        return None
    master_key = MasterKey(key)
    secret_entry = PassRecord.query.get(secret_id)
    if master_key.unlock(None, secret_entry.password):
        return master_key
    return None

#############################

@views.route("/", methods=["GET"])
def index():
    master_key = validate_session()
    secret_entry = PassRecord.query.get(secret_id)
    if secret_entry and not master_key:
        # Database exists, not logged in yet
        return render_template("index.html", db_exist=True)
    elif not master_key:
        # Database doesn't exist, not logged in yet
        return render_template("index.html", db_exist=False)
    else:
        # Logged in, redirect to content
        return redirect(url_for("views.content_react"))

@views.route("/login", methods=["POST"])
def login():
    pw = request.form.get("master_pw")
    master_key = MasterKey(None)
    secret_entry = PassRecord.query.get(secret_id)
    if secret_entry:
        # Database already exists
        if master_key.unlock(pw, secret_entry.password):
            flash("Master password correct", category="good")
            add_session(master_key.key)
            return redirect(url_for("views.content_react"))
        else:
            flash("Incorrect password!", category="warn")
            return redirect(url_for("views.index"))
    else:
        # Need to create database
        new_secret = PassRecord(id=secret_id, url="$dum.my/url$", password=master_key.set_pw(pw))
        db.session.add(new_secret)
        db.session.commit()
        flash("Master password created", category="good")
        add_session(master_key.key)
        return redirect(url_for("views.content_react"))

@views.route("/change_pw", methods=["POST"])
def master_change():
    master_key = validate_session()

    # copy(db_path, db_path+".old")
    all_rows = PassRecord.query.all()

    all_dec = []
    for row in all_rows:
        data_dec = master_key.decrypt(row.password)
        all_dec.append((row.id, data_dec))

    pw = request.form.get("master_pw")
    PassRecord.query.get(secret_id).password = master_key.set_pw(pw)

    for row in all_dec:
        if row[0] == secret_id:
            continue
        data_enc = master_key.encrypt(row[1])
        PassRecord.query.get(row[0]).password = data_enc
    db.session.commit()

    # remove(db_path+".old")
    flash("Master password changed successfully", category="good")
    resp = make_response( redirect(url_for("views.content")) )
    add_session(master_key.key)
    return resp

# TODO: see if we can redirect to index automatically if not logged in
@views.route("/lock")
def master_lock():
    if not validate_session(): return redirect(url_for("views.index"))
    flash("Password vault locked", category="warn")
    resp = make_response( redirect(url_for("views.index")) )
    remove_session()
    return resp

@views.route("/settings")
def settings():
    if not validate_session(): return redirect(url_for("views.index"))
    return render_template("settings.html")

@views.route("/content", methods=["GET"])
@views.route("/content/<int:entry_id>", methods=["GET"])
def content(entry_id=None):
    master_key = validate_session()
    if not master_key: return redirect(url_for("views.index"))
    
    if entry_id and entry_id != str(secret_id):
        result = PassRecord.query.get(int(entry_id))
        result.password = master_key.decrypt(result.password)
        return render_template("content.html", result=result)

    return render_template("content.html", result=None)

@views.route("/content_react", methods=["GET"])
def content_react():
    master_key = validate_session()
    if not master_key: return redirect(url_for("views.index"))
    return render_template("content_react.html", result=None)

@views.route("/search", methods=["POST"])
def search_db():
    url_read = request.form.get("url_read")
    domain = tldextract.extract(url_read).registered_domain
    if domain == "" or "." not in domain:
        flash(f"Invalid URL detected: {domain}", category="warn")
        return redirect(url_for("views.content"))
    result = PassRecord.query.filter_by(url=domain).first()
    if not result:
        return redirect(url_for("views.new_entry", url=domain))
    else:
        # TODO: can we return result and update url in same request
        return redirect(url_for("views.content", entry_id=result.id))

@views.route("/generate_new", methods=["POST"])
def generate_new_pw():
    master_key = validate_session()
    entryId_for_update = request.form.get("generate_new")
    if entryId_for_update == secret_id:
        return "Invalid ID"
    entry_for_update = PassRecord.query.get(entryId_for_update)
    new_pw = pwgen("")
    entry_for_update.password = master_key.encrypt(new_pw)
    db.session.commit()
    flash(f"Record (id={entryId_for_update}) updated successfully", category="good")
    result = PassRecord.query.get_or_404(entryId_for_update)
    result.password = new_pw
    return render_template("content.html", result=result)

@views.route("/add/<string:url>", methods=["GET"])
def new_entry(url):
    master_key = validate_session()
    if not master_key: return redirect(url_for("views.index"))

    domain = tldextract.extract(url).registered_domain
    if domain == "" or "." not in domain:
        flash(f"Invalid URL detected: {domain}", category="warn")
        return redirect(url_for("views.content"))
    
    return render_template("update.html", view_flag="insert", domain=domain)

@views.route("/insert_db/<string:domain>", methods=["POST"])
def insert_db(domain):
    master_key = validate_session()

    new_login = request.form.get("login")
    new_remark = request.form.get("remark")
    new_pw = pwgen(request.form.get("password"))
    new_pw_enc = master_key.encrypt(new_pw)
    if PassRecord.query.filter_by(url=domain).first():
        return "Error! Record already exists."
    else:
        new_passrecord = PassRecord(url=domain,login=new_login,remark=new_remark,password=new_pw_enc)
        db.session.add(new_passrecord)
        db.session.commit()
        flash("New entry created", category="good")
        entry_id = PassRecord.query.filter_by(url=domain).first().id
        return redirect(url_for("views.content", entry_id=entry_id))

@views.route("/update/<int:id>", methods=["GET"])
def update(id):
    master_key = validate_session()
    if not master_key: return redirect(url_for("views.index"))
    if id == secret_id: return redirect(url_for("views.content"))
    entry_for_update = PassRecord.query.get_or_404(id)
    return render_template("update.html",
        view_flag="update",
        entry_for_update=entry_for_update,
        domain=entry_for_update.url)

@views.route("/update_db/<int:id>", methods=["POST"])
def update_db(id):
    master_key = validate_session()
    if id == secret_id: return "Error! Invalid ID"
    entry_for_update = PassRecord.query.get_or_404(id)
    entry_for_update.login = request.form.get("login")
    entry_for_update.remark = request.form.get("remark")
    new_pw = request.form.get("password").replace(" ","")
    if new_pw != "":
        entry_for_update.password = master_key.encrypt(pwgen(new_pw))
    db.session.commit()
    flash(f"Record (id={id}) updated successfully", category="good")
    return redirect(url_for("views.content", entry_id=id))

@views.route("/delete/<int:id>", methods=["POST"])
def delete(id):
    if not validate_session(): return redirect(url_for("views.index"))
    if id == secret_id: return redirect(url_for("views.content"))
    entry_for_del = PassRecord.query.get_or_404(id)
    db.session.delete(entry_for_del)
    db.session.commit()
    flash(f"Record (id={id}) deleted!!", category="warn")
    return redirect(url_for("views.content"))