from celery import Celery
from clry import config

app = Celery('eAsset')
app.config_from_object(config)

from .events import EventHandler
event = EventHandler(app)