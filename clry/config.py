enable_utc = True
# result_backend = 'ampq'

task_routes = {
    'tasks.add': 'email-queue',
}
    
# task_serializer='json',
# result_serializer='json',
