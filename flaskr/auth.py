from flaskr.models import Users, db
from flask_login import login_user, LoginManager, login_required, current_user, logout_user
from flask import (
    Blueprint, redirect, abort, request, session, Response
)
from werkzeug.security import check_password_hash, generate_password_hash
import json
import functools
login_manager = LoginManager()
bp = Blueprint('auth', __name__, url_prefix='/auth')


@login_manager.user_loader
def user_loader(user_id):
    return Users.query.get(int(user_id))


def login_not_required(f):
    @functools.wraps(f)
    def wrapped(*args, **kwargs):
        if current_user.is_authenticated:
            return "User is already logged in", 401
        return f(*args, **kwargs)
    return wrapped


def handle_data(data):
    data = json.loads(data)
    username = data['username']
    password = data["password"]
    if not username:
        raise ValueError('Username was not submitted')
    if not password:
        raise ValueError('Password was not submitted')
    if 'email' in data:
        email = data['email']
        if not all(string in email for string in [email, '@', '.']):
            raise ValueError('Email is not in correct format')
        return username, password, email
    return username, password


@ bp.route('/register', methods=['POST'])
@ login_not_required
def register():
    username, password, email = handle_data(request.data)
    user = db.session.query(Users.email, Users.username).\
        filter((Users.email == email) | (Users.username == username)).all()
    if len(user) > 0:
        return "Username or Email is already taken", 400
    else:
        save_user = Users(
            username=username, password=generate_password_hash(password), email=email)
        db.session.add(save_user)
        db.session.commit()
        return 'You have successfully registered', 200


@ bp.route('/login', methods=['POST'])
@ login_not_required
def login():
    username, password = handle_data(request.data)
    user = Users.query.filter(
        (Users.email == username) | (Users.username == username)).first()
    if user is None:
        return 'The Username or Email is incorrect', 400
    elif not check_password_hash(user.password, password):
        return "Password is incorrect", 400
    else:
        login_user(user, remember=True)
        return "logged in", 200


@bp.route("/verify", methods=["GET"])
@login_required
def verify():
    return 200


@ bp.route('/logout', methods=["GET"])
@ login_required
def logout():
    session.clear()
    logout_user()
    return "logged out"


@bp.before_app_first_request
def init():
    # db.drop_all()
    db.create_all()
