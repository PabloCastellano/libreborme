FROM python:3-alpine3.6

ENV PYTHONUNBUFFERED=1

RUN apk add --no-cache build-base bash \
    musl-dev libjpeg-turbo-dev libpng libpq \
    postgresql-dev uwsgi uwsgi-python3 git \
    libxml2-dev libxslt-dev zlib-dev libffi-dev \
    libmagic

ADD requirements /requirements
RUN pip install -U -r /requirements/production.txt

# FIXME: Ugly hardcoded user/pass
# RUN pip install git+https://USER:PASS@gitlab.com/libreborme/yabormeparser.git@develop2
# RUN pip install git+https://USER:PASS@gitlab.com/libreborme/bormescraper.git

RUN mkdir -p /opt/libreborme/bormes /opt/libreborme/run/libreborme /opt/libreborme/logs /opt/libreborme/static

COPY docker/libreborme/entrypoint.sh /
RUN chmod +x /entrypoint.sh

# Disabled - Use Kubernetes CronJobs instead
# COPY docker/libreborme/crontab /etc/crontabs/root

WORKDIR /site
COPY ./ /site

CMD ["/entrypoint.sh"]
