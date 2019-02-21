FROM python:3.6-stretch
# While python:3.6-slim is lighter, it doesn't include tools such as git or gcc
# which makes build be slower

ENV PYTHONUNBUFFERED=1

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
