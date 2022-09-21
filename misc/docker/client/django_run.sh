#!/bin/sh

python3 manage.py makemigrations --check --noinput
python3 manage.py migrate --noinput
python3 manage.py createsuperuser --noinput
python3 manage.py runserver localhost:8086