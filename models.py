from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from app import app


db = SQLAlchemy(app)


class User(db.Model):
    __tablename__ = "users"
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    username = db.Column(db.String(30), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    pfp_url = db.Column(db.String(255), default="/static/default.jpg")

    is_admin = db.Column(db.Boolean, nullable=False, default=False)
    passhash = db.Column(db.String(255), nullable=False)

    @property
    def password(self):
        raise AttributeError("password is not a readable attrivute")

    @password.setter
    def password(self, password):
        self.passhash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.passhash, password)


with app.app_context():
    db.create_all()

    admin = User.query.filter_by(is_admin=True).first()
    if not admin:
        admin = User(
            username="admin", password="admin", email="admin@admin", is_admin=True
        )
        db.session.add(admin)
        db.session.commit()
