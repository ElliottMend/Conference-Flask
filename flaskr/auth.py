from models import User, db
from flask_login import login_user, LoginManager, current_user
from flask import (
    Blueprint, flash, g, redirect, render_template, request, session, url_for
)
from werkzeug.security import check_password_hash, generate_password_hash
import json
login_manager = LoginManager()
bp = Blueprint('auth', __name__, url_prefix='/auth')


@login_manager.user_loader
def user_loader(user_id):
    return User.query.get(int(user_id))


@bp.route('/register', methods=['POST'])
def register():
    data = json.loads(request.data)
    username = data['username']
    password = data['password']
    email = data['email']
    if not username:
        return "no username", 400
    if not password:
        return "no password", 400
    if not email:
        return "no email", 400
    user = User.query.filter_by(username=username).first()
    if user is not None:
        return "username is already taken", 401
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
        return "no username", 400
    if not password:
        return "no password", 400
    user = User.query.filter((User.email == username)
                             | (User.username == username)).first_or_404()
    if user is None:
        return 'user not found', 401
    elif not check_password_hash(user.password, password):
        return "incorrect password", 401
    else:
        session['username'] = username
        login_user(user, remember=True)
        return "logged in"


# @bp.before_app_first_request
# def init():
#     db.drop_all()
#     db.create_all()
