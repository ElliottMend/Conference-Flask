from app import create_app
from flaskr.chat import socketio
app = create_app()

if __name__ == "__main__":
    socketio.run(app)
