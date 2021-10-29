enable_utc = True
# result_backend = 'ampq'
# task_serializer='json',
# result_serializer='json',

task_routes = {
    'eAsset.email': 'email-queue',
}
