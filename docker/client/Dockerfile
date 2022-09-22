# HTTP server + Django application
FROM python:3.7

# Install Python and Package Libraries
RUN apt-get update && apt-get upgrade -y && \
    apt-get autoremove && \
    apt-get autoclean && \
    apt-get install -f

RUN apt-get update && apt-get install -y default-jre postgresql-client gcc musl-dev

# Don't create bytecode files
ENV PYTHONDONTWRITEBYTECODE 1
# Don't buffer output
ENV PYTHONUNBUFFERED 1

# Create the django user
ENV HOME=/home/django
RUN useradd --create-home --home-dir $HOME django
RUN chown -R django:django $HOME

# Create the appropriate directories
ENV APP_HOME=/home/django
RUN mkdir $APP_HOME/staticfiles
WORKDIR $APP_HOME

COPY requirements.txt .
COPY search_engine .

COPY ./docker/client/django_run.sh ./django_run.sh
RUN chmod +x django_run.sh

RUN chown -R django:django $APP_HOME
USER django
RUN pip install -r requirements.txt