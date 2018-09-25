FROM nginx

RUN apt -y update && \
    apt -y install curl

COPY nginx.conf /etc/nginx/nginx.conf
COPY uwsgi_params /etc/nginx/uwsgi_params
