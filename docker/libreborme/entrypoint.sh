#!/bin/sh

set -e

crond

cd /site
./scripts/wait-for-it.sh elasticsearch:9200 --timeout=30
./scripts/wait-for-it.sh postgres:5432 --timeout=30
./manage.py migrate
uwsgi --ini=/site/uwsgi.ini
