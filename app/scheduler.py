from apscheduler.executors.pool import ThreadPoolExecutor, ProcessPoolExecutor
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.jobstores.sqlalchemy import SQLAlchemyJobStore
from utils import db_url
from pytz import utc
import config

jobstores = {'default': SQLAlchemyJobStore(url=db_url())}
job_defaults = {'coalesce': config.settings.APS_COALESCE, 'max_instances': config.settings.APS_MAX_INSTANCES}

executors = {
    'default': ThreadPoolExecutor(config.settings.APS_THREAD_POOL_MAX_WORKERS), 
    'processpool': ProcessPoolExecutor(config.settings.APS_PROCESS_POOL_MAX_WORKERS)
}
scheduler = BackgroundScheduler(
    jobstores=jobstores, 
    executors=executors, 
    job_defaults=job_defaults, 
    timezone=utc, 
    misfire_grace_time=config.settings.APS_MISFIRE_GRACE_TIME
)