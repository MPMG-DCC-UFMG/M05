#!/bin/sh

python3 manage.py makemigrations --check --noinput
python3 manage.py migrate --noinput
export DJANGO_SUPERUSER_PASSWORD=$DJANGO_GSI_SUPERUSER_PASSWORD;
if [ "$DJANGO_GSI_SUPERUSER_USERNAME" ]
then
    python manage.py createsuperuser \
        --noinput \
        --username $DJANGO_GSI_SUPERUSER_USERNAME \
        --api_client_name $DJANGO_GSI_SUPERUSER_CLIENT
fi
export DJANGO_SUPERUSER_PASSWORD=$DJANGO_PROCON_SUPERUSER_PASSWORD;
if [ "$DJANGO_PROCON_SUPERUSER_USERNAME" ]
then
    python manage.py createsuperuser \
        --noinput \
        --username $DJANGO_PROCON_SUPERUSER_USERNAME \
        --api_client_name $DJANGO_PROCON_SUPERUSER_CLIENT
fi
python3 manage.py runserver 0.0.0.0:8087