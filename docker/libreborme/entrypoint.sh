#!/bin/sh

set -xe

# Disabled - Use Kubernetes CronJobs instead
# crond

if [ -n "$ELASTICSEARCH_URI" ]; then
	ES_HOST=$(echo "$ELASTICSEARCH_URI" | sed 's/.*@\(.*\).*/\1/')
else
	ES_HOST=elasticsearch:9200
fi

if [ -n "$DB_HOST" -a -n "$DB_PORT" ]; then
	PG_HOST="$DB_HOST:$DB_PORT"
else
	PG_HOST=postgres:5432
fi

cd /site
./scripts/wait-for-it.sh $ES_HOST --timeout=30
./scripts/wait-for-it.sh $PG_HOST --timeout=30
make staging settings=libreborme.settings_staging
uwsgi --ini=/site/uwsgi.ini
