import os, uuid
from functools import wraps
from flask import Flask, render_template, request, redirect, url_for, flash, session

from models import db, User
from app import app
from image import save_img


def auth_required(func):
    @wraps(func)
    def inner(*args, **kwargs):
        if "user_id" not in session:
            flash("please login to continue", "warning")
            return redirect(url_for("login"))
        return func(*args, **kwargs)

    return inner


@app.route("/")
@auth_required
def index():
    user = User.query.get(session["user_id"])
    print(user.is_admin)
    if user.is_admin:
        return redirect(url_for("admin"))
    return render_template("index.html", user=user)


@app.route("/admin")
@auth_required
def admin():
    user = User.query.get(session["user_id"])
    return render_template("admin.html", user=user)


@app.route("/profile")
@auth_required
def profile():
    return render_template("profile.html", user=User.query.get(session["user_id"]))


@app.route("/profile", methods=["POST"])
@auth_required
def profile_post():
    user = User.query.get(session["user_id"])
    username = request.form.get("username")
    email = request.form.get("email")

    cpassword = request.form.get("cpassword")
    password = request.form.get("password")

    if username == "" or email == "":
        flash("Username or email cannot be empty", "danger")
        return redirect(url_for("profile"))

    if not user.check_password(cpassword) and cpassword != "":
        flash("Incorrect password entered.", "danger")
        return redirect(url_for("profile"))

    pfp_file = request.files["pfp"]
    if pfp_file:
        if user.pfp_url == "static/default_pfp.jpg":
            pfp_url = os.path.join(
                app.config["UPLOAD_FOLDER"],
                "accounts",
                str(uuid.uuid4().hex) + "_pfp.jpg",
            )
            user.pfp_url = pfp_url
        save_img(pfp_file, user.pfp_url)

    user.username = username
    user.email = email
    user.password = password

    db.session.commit()
    flash("Profile updated successfully", "success")
    return redirect(url_for("index"))


@app.route("/login")
def login():
    return render_template("login.html")


@app.route("/login", methods=["POST"])
def login_post():
    username = request.form.get("username")
    password = request.form.get("password")
    user = User.query.filter_by(username=username).first()

    if username == "" and password == "":
        flash("username or password cannot be empty", "danger")
        return redirect(url_for("login"))

    if not user:
        flash("user doesnot exist", "danger")
        return redirect(url_for("login"))

    if not user.check_password(password):
        flash("incorrect password", "danger")
        return redirect(url_for("login"))

    session["user_id"] = user.id
    return redirect(url_for("index"))


@app.route("/register")
def register():
    return render_template("register.html")


@app.route("/register", methods=["post"])
def register_post():
    username = request.form.get("username")
    email = request.form.get("email")
    password = request.form.get("password")

    if username == "" or password == "" or email == "":
        flash("username, email or password cannot be empty", "danger")
        return redirect(url_for("register"))

    if User.query.filter_by(username=username).first():
        flash("username already exists", "danger")
        return redirect(url_for("register"))

    if User.query.filter_by(email=email).first():
        flash("Someone with that email already exists", "danger")
        return redirect(url_for("register"))

    user = User(username=username, email=email, password=password)
    pfp_file = request.files["pfp"]
    if pfp_file:
        pfp_url = os.path.join(
            app.config["UPLOAD_FOLDER"], "accounts", str(uuid.uuid4().hex) + "_pfp.jpg"
        )
        save_img(pfp_file, pfp_url)
        user.pfp_url = pfp_url

    db.session.add(user)
    db.session.commit()

    flash("User successfully registered", "success")
    return redirect(url_for("index"))


@app.route("/logout")
def logout():
    session.pop("user_id", None)
    return redirect(url_for("index"))
