#!/bin/sh

python3 manage.py makemigrations --check --noinput
python3 manage.py migrate --noinput
if [ "$DJANGO_SUPERUSER_USERNAME" ]
then
    python manage.py createsuperuser \
        --noinput \
        --username $DJANGO_SUPERUSER_USERNAME \
        --api_client_name $DJANGO_SUPERUSER_CLIENT
fi
python3 manage.py runserver 0.0.0.0:8087