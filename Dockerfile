FROM python:3-alpine3.6

ENV PYTHONUNBUFFERED=1

RUN apk add --no-cache linux-headers bash gcc \
    musl-dev libjpeg-turbo-dev libpng libpq \
    postgresql-dev uwsgi uwsgi-python3 git \
    libxml2-dev libxslt-dev zlib-dev libffi-dev \
    libmagic

ADD requirements /requirements
RUN pip install -U -r /requirements/development.txt

WORKDIR /site
COPY ./ /site
CMD python manage.py migrate && uwsgi --ini=/site/uwsgi.ini
