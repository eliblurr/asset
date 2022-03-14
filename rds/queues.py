from redis import from_url
from config import settings
from rq import Queue

REDIS_QUEUES = ["default","file","email","sms","notification","broadcaster"]

redis = from_url(settings.REDIS_URL)

queues = {
    q:Queue(
        q,
        connection=redis
    )
    for q in REDIS_QUEUES
}

get_queue = lambda queue: queues.get(queue, None)