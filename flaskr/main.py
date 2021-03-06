from app import create_app
from flaskr.chat import socketio
from flaskr.worker import connect
from rq import Queue
from rq.job import Job
app = create_app()
q = Queue(connection=connect)

if __name__ == "__main__":
    socketio.run(app)
