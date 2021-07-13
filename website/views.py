from os import remove
from shutil import copy

from flask import Blueprint, render_template, request, redirect, url_for, flash, make_response
import tldextract

from .master_key import MasterKey
from .pw_gen import pwgen
from .models import PassRecord
from . import db, db_path, secret_id

views = Blueprint("views", __name__)

def validateSession():
    cookieKey = request.cookies.get("pwmngrMaster")
    if cookieKey:
        master_key = MasterKey(bytes(cookieKey, "utf-8"))
        secret_entry = PassRecord.query.get(secret_id)
        if master_key.unlock(None, secret_entry.password):
            return master_key
    return None

@views.route("/", methods=["GET","POST"])
def index():
    master_key = validateSession()
    secret_entry = PassRecord.query.get(secret_id)
    if secret_entry and not master_key:
        view_flag = "locked"
        if request.method == "POST":
            pw = request.form.get("master_pw")
            input_master_key = MasterKey(None)
            if input_master_key.unlock(pw, secret_entry.password):
                view_flag = "unlocked"
                flash("Master password correct", category="good")
                resp = make_response( redirect(url_for("views.content")) )
                resp.set_cookie("pwmngrMaster", input_master_key.key)
                return resp
            else:
                flash("Incorrect password!", category="warn")
    elif not master_key:
        view_flag = "create"
        if request.method == "POST":
            pw = request.form.get("master_pw")
            new_master_key = MasterKey(None)
            new_secret = PassRecord(id=secret_id, url="$dum.my/url$", password=new_master_key.set_pw(pw))
            db.session.add(new_secret)
            db.session.commit()
            flash("Master password created", category="good")
            resp = make_response( redirect(url_for("views.content")) )
            resp.set_cookie("pwmngrMaster", new_master_key.key)
            return resp
    else:
        view_flag = "unlocked"
        if request.method == "POST":
            copy(db_path, db_path+".old")
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

            remove(db_path+".old")
            flash("Master password changed successfully", category="good")
            resp = make_response( redirect(url_for("views.content")) )
            resp.set_cookie("pwmngrMaster", master_key.key)
            return resp
    return render_template("index.html", view_flag=view_flag)

@views.route("/lock")
def master_change():
    if not validateSession(): return redirect(url_for("views.index"))
    flash("Password vault locked", category="warn")
    resp = make_response( redirect(url_for("views.index")) )
    resp.delete_cookie("pwmngrMaster")
    return resp

@views.route("/content", methods=["GET","POST"])
def content():
    master_key = validateSession()
    if not master_key: return redirect(url_for("views.index"))
    if request.method == "POST":
        if "url_read" in request.form:
            url_read = request.form.get("url_read")
            domain = tldextract.extract(url_read).registered_domain
            if domain == "" or "." not in domain:
                flash(f"Invalid URL detected: {domain}", category="warn")
                return redirect(url_for("views.content"))
            result = PassRecord.query.filter_by(url=domain).first()
            if not result:
                return redirect(url_for("views.new_entry", url=domain))
            else:
                result.password = master_key.decrypt(result.password)
                return render_template("content.html", result=result)
        elif "generate_new" in request.form:
            entryId_for_update = request.form.get("generate_new")
            entry_for_update = PassRecord.query.get(entryId_for_update)
            new_pw = pwgen("")
            entry_for_update.password = master_key.encrypt(new_pw)
            db.session.commit()
            flash(f"Record (id={entryId_for_update}) updated successfully", category="good")
            result = PassRecord.query.get_or_404(entryId_for_update)
            result.password = new_pw
            return render_template("content.html", result=result)
    
    entryId = request.cookies.get("entryId")
    if entryId and entryId != str(secret_id):
        result = PassRecord.query.get(int(entryId))
        result.password = master_key.decrypt(result.password)
        resp = make_response( render_template("content.html", result=result) )
        resp.delete_cookie("entryId")
        return resp
    return render_template("content.html", result=None)

@views.route("/add/<string:url>", methods=["GET", "POST"])
def new_entry(url):
    master_key = validateSession()
    if not master_key: return redirect(url_for("views.index"))

    domain = tldextract.extract(url).registered_domain
    if domain == "" or "." not in url:
        flash(f"Invalid URL detected: {domain}", category="warn")
        return redirect(url_for("views.content"))
    if request.method=="POST":
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
            resp = make_response( redirect(url_for("views.content")) )
            resp.set_cookie("entryId", str(PassRecord.query.filter_by(url=domain).first().id))
            return resp
    return render_template("update.html", view_flag="insert", url=domain)

@views.route("/update/<int:id>", methods=["GET", "POST"])
def update(id):
    master_key = validateSession()
    if not master_key: return redirect(url_for("views.masterpw"))
    if id == secret_id: return redirect(url_for("views.content"))
    entry_for_update = PassRecord.query.get_or_404(id)
    if request.method=="POST":
        entry_for_update.login = request.form.get("login")
        entry_for_update.remark = request.form.get("remark")
        new_pw = request.form.get("password").replace(" ","")
        if new_pw != "":
            entry_for_update.password = master_key.encrypt(pwgen(new_pw))
        db.session.commit()
        flash(f"Record (id={id}) updated successfully", category="good")
        resp = make_response( redirect(url_for("views.content")) )
        resp.set_cookie("entryId", str(id))
        return resp
    return render_template("update.html", view_flag="update", entry_for_update=entry_for_update)

@views.route("/delete/<int:id>", methods=["GET"])
def delete(id):
    if not validateSession(): return redirect(url_for("views.index"))
    if id == secret_id: return redirect(url_for("views.content"))
    entry_for_del = PassRecord.query.get_or_404(id) # get / get_or_404 parameter must be primary key
    db.session.delete(entry_for_del)
    db.session.commit()
    flash(f"Record (id={id}) deleted!!", category="warn")
    return redirect(url_for("views.content"))