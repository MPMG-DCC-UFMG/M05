#!/bin/sh

python3 manage.py makemigrations --check --noinput
python3 manage.py migrate --noinput
python manage.py createsuperuser --noinput
python manage.py runserver localhost:8000