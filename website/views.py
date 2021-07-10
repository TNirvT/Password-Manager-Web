from flask import Blueprint, render_template, request, redirect, url_for, flash, make_response
from shutil import copy
from .pw_encrypt import *
from .models import PassRecord
from . import db
import tldextract

views = Blueprint("views", __name__)

def validateSess():
    cookieKey = request.cookies.get("pwmngrKey")
    if not cookieKey: return False
    try:
        decrypt_trial = str_encrypt(PassRecord.query.filter_by(id=100).first().password, cookieKey, "de")
        if decrypt_trial == secret_phrase:
            return True
    except Exception as err:
        print(f"<<Error! {err}>> (masterpw, verify)")
        flash("Incorrect password!", category="warn")
        return False
    return False

@views.route("/", methods=["GET","POST"])
def masterpw():
    if not PassRecord.query.filter_by(id=100).first():
        flag_ = "new"
        if request.method == "POST":
            master_new = request.form.get("master_pw")
            salt_gen()
            flag_ = "logged_in"
            flash("New Master password created", category="good")
            new_verifyrecord = PassRecord(id=100, url=".dum.my/Url", password=str_encrypt(secret_phrase, key_pw(master_new), "en"))
            db.session.add(new_verifyrecord)
            db.session.commit()
            resp = make_response( redirect(url_for("views.content")) )
            resp.set_cookie("pwmngrKey", key_pw(master_new))
            return resp
    elif not validateSess():
        flag_ = "verify"
        if request.method == "POST":
            master_in = request.form.get("master_pw")
            old_verifyrecord = PassRecord.query.filter_by(id=100).first()
            try:
                decrypt_trial = str_encrypt(old_verifyrecord.password, key_pw(master_in), "de")
                if decrypt_trial == secret_phrase:
                    flag_ = "logged_in"
                    flash("Master password correct", category="good")
                    resp = make_response( redirect(url_for("views.content")) )
                    resp.set_cookie("pwmngrKey", key_pw(master_in))
                    return resp
            except Exception as err:
                print(f"<<Error! {err}>> (masterpw, verify)")
                flash("Incorrect password!", category="warn")
                return render_template("index.html", flag_=flag_)
    elif validateSess():
        flag_ = "logged_in"
        if request.method == "POST":
            copy(db_path, db_path+".old")
            old_records = PassRecord.query.all()
            pass_decoded = []
            old_key = request.cookies.get("pwmngrKey")
            for i in old_records:  # decrypt using existing key
                pass_decoded += [( i.id, str_encrypt(i.password, old_key, "de") )]
            new_key = key_pw(request.form.get("master_pw")) # generate a new key using new master p/w
            for i in pass_decoded:  # re-encrypt the p/w column using new m_pw
                pass_re_en = str_encrypt(i[1], new_key, "en")
                updating_record = PassRecord.query.filter_by(id=i[0]).first()
                updating_record.password = pass_re_en
            db.session.commit()
            flash("Master password changed successfully", category="good")
            resp = make_response( redirect(url_for("views.content")) )
            resp.set_cookie("pwmngrKey", new_key)
            return resp
    return render_template("index.html", flag_=flag_)

@views.route("/lock")
def master_change():
    if not validateSess(): return redirect(url_for("views.masterpw"))
    flash("Password vault locked", category="warn")
    resp = make_response( redirect(url_for("views.masterpw")) )
    resp.delete_cookie("pwmngrKey")
    return resp

# @views.route("/content", defaults={"id": None}, methods=["GET","POST"])
# @views.route("/content/<int:id>", methods=["GET","POST"])
# def content(id):
@views.route("/content", methods=["GET","POST"])
def content():
    if not validateSess(): return redirect(url_for("views.masterpw"))
    if request.method == "POST":
        if "url_read" in request.form:
            url_read = request.form.get("url_read")
            url = tldextract.extract(url_read).registered_domain
            passrecord = PassRecord.query.filter_by(url=url).first()
            if not passrecord:
                return redirect(url_for("views.insert", url=url))
            passrecord.password = str_encrypt(passrecord.password, request.cookies.get("pwmngrKey"), "de")
            return render_template("content.html", s_result=passrecord)
        elif "id_for_pw" in request.form:
            id_for_pw = request.form.get("id_for_pw")
            passrecord = PassRecord.get_or_404(id_for_pw)
            new_pw = pwgen("")
            passrecord.password = str_encrypt(new_pw, request.cookies.get("pwmngrKey"), "en")
            db.session.commit()
            flash(f"Record (id={id_for_pw}) updated successfully", category="good")
            s_result = passrecord
            s_result.password = new_pw
            return render_template("content.html", s_result=s_result)
    # if id and id!=100:
    try:
        cookie_recid = int(request.cookies.get("recId")) # try to use cookie/session_storage instead of url/route parameter
        if cookie_recid and cookie_recid != 100:
            s_result=PassRecord.query.filter_by(id=cookie_recid).first()
            s_result.password = str_encrypt(s_result.password, request.cookies.get("pwmngrKey"), "de")
            resp = make_response( render_template("content.html", s_result=s_result) )
            resp.delete_cookie("recId")
            return resp
    except TypeError:
        print("Skipped cookie read")
        pass
    return render_template("content.html", s_result=None)

@views.route("/update/<string:url>", methods=["GET", "POST"])
def insert(url):
    if not validateSess(): return redirect(url_for("views.masterpw"))
    domain = tldextract.extract(url).registered_domain
    if domain == "" or "." not in url: return "Error! Invalid url."
    if request.method=="POST":
        login = request.form.get("login")
        remark = request.form.get("remark")
        password_gen = pwgen(request.form.get("password"))
        password = str_encrypt(password_gen, request.cookies.get("pwmngrKey"), "en")
        if PassRecord.query.filter_by(url=domain).first():
            return "Error! Record already exists."
        else:
            new_passrecord = PassRecord(url=domain,login=login,remark=remark,password=password)
            db.session.add(new_passrecord)
            db.session.commit()
            resp = make_response( redirect(url_for("views.content")) )
            resp.set_cookie("recId", str(PassRecord.query.filter_by(url=domain).first().id))
            return resp
    return render_template("update.html", action="insert", url=domain)

@views.route("/update/<int:id>", methods=["GET", "POST"])
def update(id):
    if not validateSess(): return redirect(url_for("views.masterpw"))
    if id == 100: return redirect(url_for("views.content"))
    passrecord = PassRecord.query.filter_by(id=id).first()
    if request.method=="POST":
        newpw_input = request.form.get("password").replace(" ","")
        passrecord.login = request.form.get("login")
        passrecord.remark = request.form.get("remark")
        if newpw_input=="":
            pass
        else:
            passrecord.password = str_encrypt(pwgen(newpw_input), request.cookies.get("pwmngrKey"), "en")
        db.session.commit()
        flash(f"Record (id={id}) updated successfully", category="good")
        resp = make_response( redirect(url_for("views.content")) )
        resp.set_cookie("recId", str(id))
        return resp
    return render_template("update.html", action="update", url=passrecord.url, login=passrecord.login, remark=passrecord.remark)

@views.route("/delete/<int:id>", methods=["GET"])
def delete(id):
    if not validateSess(): return redirect(url_for("views.masterpw"))
    if id == 100: return redirect(url_for("views.content"))
    passrecord_del = PassRecord.query.get_or_404(id) # get / get_or_404 parameter must be primary key
    db.session.delete(passrecord_del)
    db.session.commit()
    flash(f"Record (id={id}) deleted!!", category="warn")
    return redirect(url_for("views.content"))