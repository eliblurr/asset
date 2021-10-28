from config import settings
from celery import Celery
from clry import config

# broker = f'amqp://{settings.RABBITMQ_USER}:{settings.RABBITMQ_PASSWORD}@{settings.RABBITMQ_BASE_URL}:{settings.RABBITMQ_PORT}/{settings.RABBITMQ_VIRTUAL_HOST}'
# broker = "amqp://e-asset-user:password@localhost:5672/e-asset-host"
# celery = Celery('eAsset', backend='amqp', broker="amqp://e-asset-user:password@localhost:5672/e-asset-host", include=['celery.tasks'])
# backend='amqp',

app = Celery('eAsset', broker="amqp://e-asset-user:password@localhost:5672/e-asset-host", include=['clry.tasks'])
app.config_from_object(config)


if __name__ == '__main__':
    app.start()