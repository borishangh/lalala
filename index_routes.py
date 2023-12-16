import os
import uuid
from functools import wraps
from flask import Flask, render_template, request, redirect, url_for, flash, session

from models import db, User, Song, Album, Rating
from app import app
from image import save_img
from routes import auth_required


@app.route("/", methods=["POST"])
@auth_required
def index_post():
    if "play-song" in request.form:
        user = User.query.get(session["user_id"])
        song_id = request.form.get("play-song")
        song = Song.query.get(song_id)
        featured = Song.query.order_by(Song.plays.desc()).limit(12).all()
        return render_template(
            "index.html", user=user, now_playing=song, featured=featured
        )

    return redirect(url_for("index"))
