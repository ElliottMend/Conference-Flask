from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from datetime import datetime
db = SQLAlchemy()


def default_screen_name(context):
    return context.get_current_parameters()['username']


class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(40), unique=True, nullable=False)
    password = db.Column(db.String(60), unique=True, nullable=False)
    email = db.Column(db.String(80), unique=True, nullable=False)
    screen_name = db.Column(db.String(40), nullable=False,
                            default=default_screen_name)


class Room(db.Model):
    id = db.Column(db.String(40), primary_key=True)
    room_name = db.Column(db.String(60), nullable=False)
    room_password = db.Column(db.String(40), nullable=True)


class UserRoom(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    room_id = db.Column(db.String, db.ForeignKey('room.id'))


class Message(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_room_id = db.Column(db.Integer, db.ForeignKey('user_room.id'))
    message = db.Column(db.String(200), nullable=False)
    datetime = db.Column(db.DateTime, default=datetime.utcnow)
