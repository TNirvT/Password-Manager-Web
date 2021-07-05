from flask import Blueprint, render_template, request, redirect, url_for, flash
from shutil import copy2
from .pw_encrypt import *
from .models import PassRecord
from . import db
import tldextract

views = Blueprint("views", __name__)
flag_ = "verify"
print("<<Top of views.py>>")

@views.route("/", methods=["GET","POST"])
def masterpw():
    global flag_
    if not path.exists(key_path):
        flag_ = "new"
        if request.method == "POST":
            master_new = request.form.get("master_pw")
            salt_gen()
            master_pw(master_new, "new")
            flag_ = "logged_in"
            flash("New Master password created", category="good")
            return redirect(url_for("views.content"))
    elif flag_ == "verify":
        if request.method == "POST":
            master_in = request.form.get("master_pw")
            if master_pw(master_in, "login"):
                flag_ = "logged_in"
                flash("Master password correct", category="good")
                return redirect(url_for("views.content"))
            else:
                flash("Incorrect password!", category="warn")
    elif flag_ == "logged_in":
        if request.method == "POST":
            copy2(db_path, db_path+".old")
            old_records = PassRecord.query.all()
            old_pass_decoded = []
            for i in old_records:  # decrypt using existing key
                old_pass_decoded += [( i.id, str_encrypt(i.password, key_read(), "de") )]
            master_pw(request.form.get("master_pw"), "change") # generate a new key using new master p/w
            for i in old_pass_decoded:  # re-encrypt the p/w column using new m_pw
                old_pass_en = str_encrypt(i[1], key_read(), "en")
                updating_record = PassRecord.query.filter_by(id=i[0]).first()
                updating_record.password = old_pass_en
                db.session.commit()
            flash("Master password changed successfully", category="good")
            return redirect(url_for("views.content"))
    return render_template("index.html", flag_=flag_)

@views.route("/lock")
def master_change():
    global flag_
    if flag_ != "logged_in": return redirect(url_for("views.masterpw"))
    flag_= "verify"
    flash("Password vault locked", category="warn")
    return redirect(url_for("views.masterpw"))

@views.route("/content", defaults={"id": None}, methods=["GET","POST"])
@views.route("/content/<int:id>", methods=["GET","POST"])
def content(id):
    if flag_ != "logged_in": return redirect(url_for("views.masterpw"))
    if request.method == "POST":
        url_read = request.form.get("url_read")
        url = tldextract.extract(url_read).registered_domain
        passrecord = PassRecord.query.filter_by(url=url).first()
        if not passrecord:
            return redirect(url_for("views.insert", url=url))
        passrecord.password = str_encrypt(passrecord.password, key_read(), "de")
        return render_template("content.html", s_result=passrecord)
    if id:
        s_result=PassRecord.query.filter_by(id=id).first()
        s_result.password = str_encrypt(s_result.password, key_read(), "de")
        return render_template("content.html", id=None, s_result=s_result)
    return render_template("content.html", s_result=None)

@views.route("/update/<string:url>", methods=["GET", "POST"])
def insert(url):
    if flag_ != "logged_in": return redirect(url_for("views.masterpw"))
    if request.method=="POST":
        login = request.form.get("login")
        remark = request.form.get("remark")
        password_gen = pwgen(request.form.get("password"))
        password = str_encrypt(password_gen, key_read(), "en")
        if PassRecord.query.filter_by(url=url).first():
            return "Error! Record already exists."
        else:
            new_passrecord = PassRecord(url=url,login=login,remark=remark,password=password)
            db.session.add(new_passrecord)
            db.session.commit()
            return redirect(url_for("views.content", id=new_passrecord.id))
    return render_template("update.html", action="insert", url=url)

@views.route("/update/<int:id>", methods=["GET", "POST"])
def update(id):
    if flag_!="logged_in": return redirect(url_for("views.masterpw"))
    passrecord = PassRecord.query.filter_by(id=id).first()
    if request.method=="POST":
        passrecord.login = request.form.get("login")
        passrecord.remark = request.form.get("remark")
        db.session.commit()
        flash(f"Record (id={id}) updated successfully", category="good")
        return redirect(url_for("views.content"))
    return render_template("update.html", action="update", url=passrecord.url, login=passrecord.login, remark=passrecord.remark)

@views.route("/delete/<int:id>", methods=["GET"])
def delete(id):
    if flag_!="logged_in": return redirect(url_for("views.masterpw"))
    passrecord_del = PassRecord.query.get_or_404(id)
    db.session.delete(passrecord_del)
    db.session.commit()
    flash(f"Record (id={id}) deleted!!", category="warn")
    return redirect(url_for("views.content"))