#!/bin/sh

# Create Rabbitmq user
( 
    rabbitmqctl wait --timeout 60 $RABBITMQ_PID_FILE ; \
    rabbitmqctl add_user $RABBITMQ_USER $RABBITMQ_PASSWORD 2>/dev/null ; \
    rabbitmqctl add_vhost $RABBITMQ_VIRTUAL_HOST ; \
    rabbitmqctl set_user_tags $RABBITMQ_USER administrator ; \
    rabbitmqctl set_permissions -p $RABBITMQ_VIRTUAL_HOST $RABBITMQ_USER  ".*" ".*" ".*" ; \
    echo "*** User '$RABBITMQ_USER' with password '$RABBITMQ_PASSWORD' completed with permissions '.*' '.*' '.*' running on virtualhost '$RABBITMQ_VIRTUAL_HOST' ***" ; \
    echo "*** Log in the WebUI at port '$RABBITMQ_WEB_PORT' (example: http:/localhost:15672) ***"
) &

rabbitmq-server $@

# ref: https://stackoverflow.com/questions/30747469/how-to-add-initial-users-when-starting-a-rabbitmq-docker-container