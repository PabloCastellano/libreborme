FROM python:3.6-slim

ENV PYTHONUNBUFFERED=1

RUN apt-get update && apt-get install -y \
    git \
    gcc \
&& rm -rf /var/lib/apt/lists/*
# RUN apt-get update && apt-get install -f python3-software-properties software-properties-common \
#     python3-dev python3-venv python3-wheel \
#     python3-setuptools libxml2-dev libxslt1-dev libgmp-dev zlib1g-dev \
#     wget git libpq-dev python-psycopg2 \
#     openssl checkinstall

ADD requirements /requirements
RUN pip install -U -r /requirements/production.txt \
    && rm -fr /root/.cache/pip

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
