from config import REDIS_URL
from redis import from_url
from rq import Queue

REDIS_QUEUES = ["default","file","email","sms","notification","broadcaster"]

redis = from_url(REDIS_URL)

queues = {
    q:Queue(
        q,
        connection=redis
    )
    for q in REDIS_QUEUES
}

get_queue = lambda queue: queues.get(queue, None)