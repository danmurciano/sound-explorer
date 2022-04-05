from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt

db = SQLAlchemy()
bcrypt = Bcrypt()

def connect_db(app):
    db.app = app
    db.init_app(app)


class User(db.Model):
    __tablename__ = "users"

    spotify_id = db.Column(db.String(30), primary_key=True)
    display_name = db.Column(db.String(30), nullable=False)
    image = db.Column(db.Text, nullable=False)

    @classmethod
    def register(cls, spotify_id, display_name, image):
        user = cls(
            spotify_id=spotify_id,
            display_name=display_name,
            image=image
        )

        return user
