from app import app
from models import db
import auth
from flask_login import current_user, login_required
from flask_socketio import SocketIO
import chat
from flask_cors import CORS

db.init_app(app)
app.register_blueprint(auth.bp)

chat.socketio.init_app(app, manage_session=False,
                       async_mode='eventlet', cors_allowed_origins="http://localhost:3000")
auth.login_manager.init_app(app)
CORS(app, supports_credentials=True)


@app.route('/')
@login_required
def index():
    print(current_user)
    return "sada"


if __name__ == "__main__":
    chat.socketio.run(app)
