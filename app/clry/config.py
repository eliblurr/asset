from config import settings

enable_utc = True
# List of modules to import when the Celery worker starts.
imports = ('clry.tasks',)
## Broker settings.
broker_url = 'amqp://e-asset-user:password@localhost:5672/e-asset-host'
## Using the database to store task state and results.
result_backend = 'rpc://e-asset-user:password@localhost:5672/e-asset-host'

task_routes = {
    'eAsset.email': 'email-queue',
}

# broker = f'amqp://{settings.RABBITMQ_USER}:{settings.RABBITMQ_PASSWORD}@{settings.RABBITMQ_BASE_URL}:{settings.RABBITMQ_PORT}/{settings.RABBITMQ_VIRTUAL_HOST}'
# backend = f'rpc://{settings.RABBITMQ_USER}:{settings.RABBITMQ_PASSWORD}@{settings.RABBITMQ_BASE_URL}:{settings.RABBITMQ_PORT}/{settings.RABBITMQ_VIRTUAL_HOST}'
# broker = "amqp://e-asset-user:password@localhost:5672/e-asset-host"
# task_serializer='json',
# result_serializer='json',
# broker_url = settings.RABBITMQ_BROKER
# worker_send_task_event = False
# task_ignore_result = True
# task_time_limit = 60
# task_soft_time_limit = 50
# task_acks_late = True
# worker_prefetch_multiplier = 10
# worker_cancel_long_running_tasks_on_connection_loss = True