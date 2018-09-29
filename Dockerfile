FROM python:3-alpine3.6

ENV PYTHONUNBUFFERED=1

RUN apk add --no-cache linux-headers bash gcc \
    musl-dev libjpeg-turbo-dev libpng libpq \
    postgresql-dev uwsgi uwsgi-python3 git \
    libxml2-dev libxslt-dev zlib-dev libffi-dev \
    libmagic make

ADD requirements /requirements
RUN pip install -U -r /requirements/production.txt

COPY docker/libreborme/entrypoint.sh /
RUN chmod +x /entrypoint.sh

RUN echo '0 8 * * 1-5 ./manage.py importbormetoday' > /etc/crontabs/root

WORKDIR /site
COPY ./ /site

CMD ["/entrypoint.sh"]
