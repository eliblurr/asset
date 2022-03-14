from rq import  Worker, Connection
from .queues import redis, queues

if __name__ == '__main__':
    with Connection(redis):
        worker = Worker( queues, connection=redis )
        worker.work()