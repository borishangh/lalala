import os
import uuid
from functools import wraps
from flask import Flask, render_template, request, redirect, url_for, flash, session

from models import db, User, Song, Album, Rating
from app import app
from image import save_img
from routes import auth_required


@app.route("/creator")
@auth_required
def creator():
    user = user = User.query.get(session["user_id"])
    most_played = (
        Song.query.filter_by(creator_id=user.id)
        .order_by(Song.plays.desc())
        .limit(5)
        .all()
    )
    return render_template("creator.html", user=user, most_played=most_played)


@app.route("/creator", methods=["POST"])
@auth_required
def creator_post():
    user = User.query.get(session["user_id"])

    if "song" in request.form:
        songname = request.form.get("songname")
        lyrics = request.form.get("lyrics")
        songfile = request.files["songfile"]

        if not songname:
            flash("Song name cannot be empty.", "danger")
            return redirect(url_for("creator"))

        if not songfile:
            flash("Song file cannot be empty.", "danger")
            return redirect(url_for("creator"))

        song_url = os.path.join(
            app.config["UPLOAD_FOLDER"],
            "tracks",
            str(uuid.uuid4().hex) + "_track.mp3",
        )
        songfile.save(song_url)

        song = Song(
            song_name=songname, song_url=song_url, creator_id=user.id, lyrics=lyrics
        )

        db.session.add(song)
        db.session.commit()

        print(songname, lyrics, songfile)
        flash("Track added successfully", "success")

    if "album" in request.form:
        album_name = request.form.get("albumname")
        cover_file = request.files["cover"]

        album = Album(album_name=album_name, creator_id=user.id)

        if cover_file:
            album_cover_url = os.path.join(
                app.config["UPLOAD_FOLDER"],
                "albums",
                str(uuid.uuid4().hex) + "_album.jpg",
            )
            save_img(cover_file, album_cover_url)
            album.album_cover_url = album_cover_url

        db.session.add(album)

        for item in request.form:
            if item.split("-")[0] == "song":
                song_id = int(item.split("-")[1])
                song = Song.query.get(song_id)
                song.album_id = album.id

        db.session.commit()
        flash("Album created sucessfully", "success")

    return redirect(url_for("creator"))
