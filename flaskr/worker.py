import redis
from rq import Worker, Queue, Connection
connect = redis.Redis(host='localhost', port=6379, db=0)

if __name__ == "__main__":
    with Connection(connect):
        worker = Worker(list(map(Queue, ['listen'])))
        worker.work()
