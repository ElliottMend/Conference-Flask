from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from datetime import datetime
db = SQLAlchemy()


class Users(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(40), unique=True, nullable=False)
    password = db.Column(db.String(100), unique=True, nullable=False)
    email = db.Column(db.String(80), unique=True, nullable=False)


class Servers(db.Model):
    id = db.Column(db.String(80), primary_key=True)
    server_name = db.Column(db.String(60), nullable=False)
    server_password = db.Column(db.String(100), nullable=True)


class UserServers(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    server_id = db.Column(db.String, db.ForeignKey('servers.id'))
    private = db.Column(db.Boolean, default=False)


class Messages(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_server_id = db.Column(db.Integer, db.ForeignKey('user_servers.id'))
    message = db.Column(db.String(200), nullable=False)
    datetime = db.Column(db.DateTime, default=datetime.utcnow)


class Notes(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    server_id = db.Column(db.String, db.ForeignKey('servers.id'))
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    message = db.Column(db.String())


class Inboxs(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    received_user = db.Column(db.Integer, db.ForeignKey('users.id'))
    server_id = db.Column(db.String, db.ForeignKey('servers.id'))
    show = db.Column(db.Boolean, default=True)
    sent_user = db.Column(db.Integer, db.ForeignKey('users.id'))
