import asyncio, logging, celery as C
from services.email import email
from clry import app

logger = logging.getLogger("eAsset.main")

class TaskManager(C.Task):
    def on_failure(self, exc, task_id, args, kwargs, einfo):
        logger.info('{0!r} celery: {1!r}'.format(task_id, exc), exc_info=True)
        logger.critical('{0!r} celery: {1!r}'.format(task_id, exc), exc_info=True)

@app.task(name='add', base=TaskManager, bind=True, acks_late=True, task_time_limit=120, task_soft_time_limit=120, default_retry_delay=10 * 60)
def add(self):
    print(self.request.id)

@app.task(name='email', base=TaskManager, bind=True, acks_late=True, task_time_limit=120, task_soft_time_limit=120, default_retry_delay=10 * 60, retry_backoff=True, retry_kwargs={'max_retries': 2, 'countdown': 2}) 
def send_email(self, *args, **kwargs):
    asyncio.run(email(*args, **kwargs))
