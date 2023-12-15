import os
from functools import wraps
from flask import Flask, render_template, request, redirect, url_for, flash, session

from models import db, User
from app import app
from image import save_img
from routes import auth_required


@app.route("/creator")
@auth_required
def creator():
    return render_template("creator.html", user=User.query.get(session["user_id"]))


@app.route("/creator", methods=["POST"])
@auth_required
def creator_post():
    user=User.query.get(session["user_id"])

    if "song" in request.form:
        songname = request.form.get('songname')
        lyrics = request.form.get('lyrics')
        songfile = request.files['songfile']

        if not songname:
            flash('Song name cannot be empty.')
            return redirect(url_for("creator"))

        if not songfile:
            flash('Song file cannot be empty.')
            return redirect(url_for("creator"))

        print(songname, lyrics, songfile)
        flash("Track added successfully")
    return redirect(url_for("creator"))
