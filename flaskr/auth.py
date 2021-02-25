from models import User, db
from flask_login import login_user, LoginManager, current_user
from flask import (
    Blueprint, flash, g, redirect, render_template, request, session, url_for
)
from werkzeug.security import check_password_hash, generate_password_hash
import json
login_manager = LoginManager()
bp = Blueprint('auth', __name__, url_prefix='/auth')


@bp.route('/register', methods=['POST'])
def register():
    data = json.loads(request.data)
    username = data['username']
    password = data['password']
    email = data['password']
    if not username:
        return "no username"
    if not password:
        return "no password"
    if not email:
        return "no email"
    user = User.query.filter_by(username=username).first()
    if user is not None:
        return "username is already taken"
    else:
        save_user = User(
            username=username, password=generate_password_hash(password), email=email)
        db.session.add(save_user)
        db.session.commit()
        return('registered')


@bp.route('/login', methods=['POST'])
def login():
    data = json.loads(request.data)
    username = data['username']
    password = data['password']
    if not username:
        return "no username"
    if not password:
        return "no password"
    user = User.query.filter((User.email == username)
                             | (User.username == username)).first()
    if user is None:
        return 'user not found'
    elif not check_password_hash(user.password, password):
        return "incorrect password"
    else:
        session.clear()
        session['username'] = user.username
        login_user(user)
        return "logged in"


@login_manager.user_loader
def load_user(user_id):
    print(user_id)
    return User.query.filter_by(username=user_id).first()


@bp.before_app_first_request
def init():
    db.create_all()
