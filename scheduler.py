from apscheduler.executors.pool import ThreadPoolExecutor, ProcessPoolExecutor
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.jobstores.sqlalchemy import SQLAlchemyJobStore
from database import DATABASE_URL
from config import settings
import pytz

jobstores = {'default': SQLAlchemyJobStore(url=DATABASE_URL)}
executors = {
    'default': ThreadPoolExecutor(settings.APS_THREAD_POOL_MAX_WORKERS),
    'processpool': ProcessPoolExecutor(settings.APS_PROCESS_POOL_MAX_WORKERS)
}
job_defaults = {'coalesce': False, 'max_instances': 3}

scheduler = BackgroundScheduler(
    timezone=pytz.utc, 
    jobstores=jobstores, 
    executors=executors, 
    job_defaults=job_defaults, 
    misfire_grace_time=settings.APS_MISFIRE_GRACE_TIME
)
