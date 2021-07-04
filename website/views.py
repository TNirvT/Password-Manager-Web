from flask import Blueprint, render_template, request, redirect, url_for
from .pw_encrypt import *
from .models import PassRecord
from . import db
import tldextract

views = Blueprint("views", __name__)
flag_ = "verify"

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
            return redirect(url_for("views.content"))
    else:
        flag_ = "verify"
        if request.method == "POST":
            master_in = request.form.get("master_pw")
            if master_pw(master_in, "login"):
                flag_ = "logged_in"
                return redirect(url_for("views.content"))
    return render_template("index.html", flag_=flag_)

@views.route("/master-change")
def master_change():
    if flag_ != "logged_in": return redirect(url_for("views.masterpw"))
    # add code here
    return render_template("index.html")

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
        return redirect(url_for("views.content"))
    return render_template("update.html", action="update", url=passrecord.url, login=passrecord.login, remark=passrecord.remark)

@views.route("/delete/<int:id>", methods=["GET"])
def delete(id):
    if flag_!="logged_in": return redirect(url_for("views.masterpw"))
    passrecord_del = PassRecord.query.get_or_404(id)
    db.session.delete(passrecord_del)
    db.session.commit()
    return redirect(url_for("views.content"))