from flaskr.models import User, db
from flask_login import login_user, LoginManager, login_required, current_user, logout_user
from flask import (
    Blueprint, redirect, abort, request, session, Response
)
from werkzeug.security import check_password_hash, generate_password_hash
import json
login_manager = LoginManager()
bp = Blueprint('auth', __name__, url_prefix='/auth')


@login_manager.user_loader
def user_loader(user_id):
    return User.query.get(int(user_id))


def handle_data(data):
    data = json.loads(request.data)
    username = data["username"]
    password = data["password"]
    if not username:
        return abort(400, Response("Username was not submitted"))
    if not password:
        return abort(400, Response("Password was not submitted"))
    if 'email' in data:
        email = data['email']
        if 'email' not in data:
            return abort(400, Response("Email was not submitted"))
        if not all(string in email for string in [email, '@', '.']):
            return abort(400, Response("The Email is an incorrect format"))
        return username, password, email
    return username, password


@bp.route('/register', methods=['POST'])
def register():
    if not current_user.is_authenticated:
        username, password, email = handle_data(request.data)
        user = db.session.query(User.email, User.username).\
            filter((User.email == email) | (User.username == username)).all()
        if len(user) > 0:
            return "Username or Email is already taken", 400
        else:
            save_user = User(
                username=username, password=generate_password_hash(password), email=email)
            db.session.add(save_user)
            db.session.commit()
            return 'registered', 200
    else:
        return "already logged in", 403


@bp.route('/login', methods=['POST'])
def login():
    if not current_user.is_authenticated:
        username, password = handle_data(request.data)
        a = User.query.first()
        print(a.username)
        print(username, password)
        user = User.query.filter(
            (User.email == username) | (User.username == username)).first_or_404()
        if user is None:
            return 'The Username or Email is incorrect', 401
        elif not check_password_hash(user.password, password):
            print('password')
            return "Password is incorrect", 401
        else:
            session['username'] = username
            login_user(user, remember=True)
            return "logged in", 200
    else:
        return "already logged in", 403


@bp.route('/logout')
@login_required
def logout():
    session.clear()
    logout_user()
    return "logged out"

# @bp.before_app_first_request
# def init():
#     db.drop_all()
#     db.create_all()
