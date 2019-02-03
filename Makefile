settings := libreborme.settings_dev

index:
		./manage.py search_index --models borme.Company --populate
		./manage.py search_index --models borme.Person --populate

reindex:
		./manage.py search_index --delete
		# the index must be created outside Django
		./manage.py search_index --models borme.Company --populate
		./manage.py search_index --models borme.Person --populate

robotstxt:
		./manage.py regenerate_robotstxt

backups:
		s3cmd ls s3://libreborme-prod/backups/database/

recreate_db:
		./manage.py reset_db --noinput
		./manage.py migrate
		./manage.py loaddata ./libreborme/fixtures/config.json
		./manage.py loaddata ./alertas/fixtures/alertasconfig.json
		# ./manage.py createsuperuser --username admin --email pablo@anche.no
		./manage.py shell -c "from django.contrib.auth import get_user_model; get_user_model().objects.create_superuser('pablo@anche.no', '000000')"

recreate_db2:
		# pg_dump -c -C -h localhost -U libreborme > clean_dump.sql
		# no va
		psql -h localhost -U libreborme < clean_dump.sql

sync_stripe:
		# Note: this creates Customers from existing Users in database
		./manage.py djstripe_sync_customers
		./manage.py djstripe_sync_plans_from_stripe
		# from djstripe.models import Product; for product in Product.api_list(): Product.sync_from_stripe_data(product)

run:
		docker-compose up -d
		./manage.py migrate --settings $(settings)
		@echo "\n\n\n#################################################################"
		@echo "NOTES:\n"
		@echo "Mailhog is running at http://localhost:8025"
		@echo "SMTP development server listens at localhost:1025"
		@echo "#######################################################################\n\n\n"
		./manage.py runserver --settings $(settings)
		# ./manage.py runserver_plus

shell:
		./manage.py shell_plus --settings $(settings)

import:
		./manage.py importborme -f 2018-03-13 -t 2018-03-13 --local-only --settings $(settings)

import1:
		./manage.py importbormejson /home/pablo2/.bormes/json/2018/03/13/BORME-A-2018-51-41.json --settings $(settings)

import2:
		./manage.py importbormejson /home/pablo2/bormes_spider/json/2018/03/13/BORME-A-2018-51-41.json --settings $(settings)

emailserver:
		./manage.py mail_debug

graph_model:
		# ./manage.py graph_models -a -g -o graph_model.png
		./manage.py graph_models borme libreborme alertas -g -o graph_model.png
		@echo "Generated graph_model.png"

test:
		DJANGO_SETTINGS_MODULE=libreborme.settings_ci DB_HOST=localhost ./manage.py test --noinput -v 3

test1:
		DJANGO_SETTINGS_MODULE=libreborme.settings_ci DB_HOST=localhost ./manage.py test --noinput -v 3 borme.tests.test_import.TestImport2.test_nombramientos_ceses

test2:
		./setup.py test

test3:
		./runtests.py

test_ci:
		./scripts/wait-for-it.sh elasticsearch:9200 --timeout=30
		coverage run --source='.' manage.py test --noinput -v 3
		coverage report

test_k8s_ci:
		./scripts/wait-for-it.sh elasticsearch.libreborme-6554539.svc.cluster.local:9200 --timeout=30
		DJANGO_SETTINGS_MODULE=libreborme.settings_ci coverage run --source='.' manage.py test --noinput -v 3
		coverage report

test_docker:
		echo `git rev-parse HEAD`
		docker build -t libreborme:ci .
		CONTAINER_IMAGE=libreborme CI_BUILD_REF_NAME=ci docker-compose -f docker-compose.ci.yml -p ci up --abort-on-container-exit

staging:
		./manage.py check --settings $(settings)
		./manage.py check --deploy --settings $(settings)
		./manage.py collectstatic --noinput --settings $(settings)
		./manage.py migrate --settings $(settings)
		./manage.py loaddata ./libreborme/fixtures/config.json --settings $(settings)
		./manage.py loaddata ./alertas/fixtures/alertasconfig.json --settings $(settings)
		uwsgi --ini=/site/uwsgi.ini

update_staging_images:
		# docker login -u gitlab-ci-token -p $CI_JOB_TOKEN registry.gitlab.com
		docker build -t registry.gitlab.com/libreborme/libreborme:staging .
		docker push registry.gitlab.com/libreborme/libreborme:staging
		cd docker/nginx && docker build -t registry.gitlab.com/libreborme/libreborme/nginx:staging .
		docker push registry.gitlab.com/libreborme/libreborme/nginx:staging
